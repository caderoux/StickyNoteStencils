// Sticky-note stencils: planners, a week, and grids -- for 3 x 3 inch (76 mm) notes. The
// tab sits on the edge toward you when the stencil lies on the pad; give each stencil in a
// set a different tab position (1 to 5) so all the tabs show when they are stacked.

/* [Stencil] */
// A ready-made stencil, or Custom grid to set the grid below
preset = "planner_quadrants"; // [planner_quadrants:Planner quadrants, planner_focus:Planner focus, planner_pros_cons:Planner pros and cons, planner_two_columns:Planner two columns, planner_two_rows:Planner two rows, week_labelled:Week with day letters, week_grid:Week grid only, grid_dots:Grid dots, grid_graph:Grid graph dots and axes, custom_grid:Custom grid]

/* [Tab] */
// Width across the top of the tab (11.5 lets five positions show; 15 suits three)
tab_width = 11.5; // [8:0.5:30]
// Where along the edge: 1 to 5 (for three tabs use 1, 3 and 5; for one, 3)
tab_position = 3; // [1:1:5]

/* [Print] */
// Stencil thickness (1.6 is 8 layers of 0.2)
thickness = 1.6; // [0.8:0.2:3]
// Width of the pen slots
slot_width = 1.6; // [1:0.1:2.5]

/* [Custom grid] */
// Spacing of the dots
grid_pitch = 5; // [3:0.5:10]
// Dot size
grid_dot = 1.6; // [1:0.1:3]
// Axes through the middle
grid_axes = false;

/* [Hidden] */
// --- stencil-common.scad, inlined by build.py ---
// Sticky-note stencil standard, shared by every generator -- OpenSCAD port of the Python
// prototype (../conform.py: sheet, tab; ../stencilgen.py: slot, box, rows). Keep the two in
// step: build.py renders every preset here and compares it with the prototype's outline.
//
// The standard (owner): a 76 mm square sheet, corners 3; one tab on its bottom edge --
// jorm's angled tab (MakerWorld 1409445, measured from its blank STEPs): 7 deep, sides 50
// degrees off the edge, every corner 3 round -- of a chosen top width at position 1 to 5.
// Bottom, because lying on the pad the tab sticks out toward the user: every pattern is
// drawn upright with its foot toward the tab. The pattern keeps MARGIN inside the edges;
// pen slots are SLOT wide with round ends. Nothing may cut off an island (a closed loop of
// slot, a letter with a counter): it would drop out.
//
// A generator includes this file while being developed; build.py inlines it for upload
// (MakerWorld takes one .scad file).

SQUARE = 76;             // a 3 x 3 inch note
CORNER_R = 3;
TAB_D = 7;               // [jorm]
TAB_ANGLE = 50;          // [jorm] the tab's sides, degrees off the sheet's edge
TAB_R = 3;               // [jorm]
POSITIONS = 5;
MARGIN = 7;
H = SQUARE / 2 - MARGIN; // the pattern's half extent
BOX = 5;                 // a checkbox; LARGE_BOX for the large ones
LARGE_BOX = 8;
GAP = 2;                 // between a box and its line
TITLE_GAP = 5;           // between the title bar and the first row (was 3)
TITLE = 9;               // a title bar's height: room to write in (owner: larger; was 5)

$fn = 48;

// the tab's width where it meets the sheet
function tab_base(w) = w + 2 * TAB_D / tan(TAB_ANGLE);

// position 1 to POSITIONS, evenly spaced for a tab of top width w, the base of 1 and of
// the last just clear of the sheet's corner rounding
function tab_centre(position, w) =
    let(span = SQUARE - 2 * CORNER_R - tab_base(w))
    -span / 2 + span * (position - 1) / (POSITIONS - 1);

// the sheet and its tab, 2D, centred on the origin, the tab on the bottom edge
module sheet(tab_width, tab_position) {
    x = tab_centre(tab_position, tab_width);
    e = -SQUARE / 2;
    b = tab_base(tab_width) / 2;
    t = tab_width / 2;
    // round the concave corners (the tab's foot), after the convex ones
    offset(r = -TAB_R) offset(delta = TAB_R)
    offset(r = CORNER_R) offset(delta = -CORNER_R)
    union() {
        square(SQUARE, center = true);
        polygon([[x - b, e + 1], [x + b, e + 1], [x + b, e], [x + t, e - TAB_D],
                 [x - t, e - TAB_D], [x - b, e]]);
    }
}

// a pen slot from p0 to p1, w wide, round ended
module slot(p0, p1, w) {
    hull() {
        translate(p0) circle(d = w);
        translate(p1) circle(d = w);
    }
}

// a checkbox centred at c: square (corners 0.5), circle, triangle (pointing down) or heart
module box(c, size, shape) {
    translate(c)
    if (shape == "square")
        offset(r = 0.5) square(size - 1, center = true);
    else if (shape == "circle")
        circle(d = size);
    else if (shape == "triangle")
        let(r = size / 2) polygon([[-r, 0.8 * r], [r, 0.8 * r], [0, -r]]);
    else if (shape == "heart")
        let(k = size / 32)
        polygon([for (i = [0 : 63]) let(a = 360 * i / 63)
            [16 * pow(sin(a), 3) * k,
             (13 * cos(a) - 5 * cos(2 * a) - 2 * cos(3 * a) - cos(4 * a)) * k + size * 0.05]]);
}

// n rows' centres, evenly from top to bottom
function rows_y(n, top, bottom) =
    n == 1 ? [(top + bottom) / 2] : [for (k = [0 : n - 1]) top - (top - bottom) * k / (n - 1)];

// a title bar across the top of the pattern
module title_bar() {
    offset(r = 0.8) offset(delta = -0.8) translate([-H, H - TITLE]) square([2 * H, TITLE]);
}

flat = false;            // true: the stencil's outline in 2D (build.py's check), not a part

// the finished stencil: the sheet, the pattern cut out, extruded
module stencil(tab_width, tab_position, thickness) {
    if (flat)
        difference() { sheet(tab_width, tab_position); children(); }
    else
        linear_extrude(thickness) difference() {
            sheet(tab_width, tab_position);
            children();
        }
}


// presets: [name, kind, layout or labels, grid pitch, dot, axes]
PRESETS = [
    ["planner_quadrants", "planner", "quadrants"],
    ["planner_focus", "planner", "focus"],
    ["planner_pros_cons", "planner", "pros-cons"],
    ["planner_two_columns", "planner", "two-columns"],
    ["planner_two_rows", "planner", "two-rows"],
    ["week_labelled", "week", true],
    ["week_grid", "week", false],
    ["grid_dots", "grid", 5, 1.6, false],
    ["grid_graph", "grid", 5, 1.6, true],
];

P = preset == "custom_grid"
    ? ["custom_grid", "grid", grid_pitch, grid_dot, grid_axes]
    : PRESETS[search([preset], PRESETS)[0]];

module v(x, y0 = -H, y1 = H) slot([x, y0], [x, y1], slot_width);
module h(y, x0 = -H, x1 = H) slot([x0, y], [x1, y], slot_width);

module planner_pattern(layout) {
    if (layout == "quadrants") { v(0); h(0); }
    else if (layout == "focus") { v(0, -H, -H / 3); h(-H / 3); }
    else if (layout == "pros-cons") { v(0, -H, H - 8); h(H - 8); }
    else if (layout == "two-columns") v(0);
    else if (layout == "two-rows") h(0);
}

// a 7-day week: two columns of four, the last cell for notes; day letters (none with a
// counter, so nothing drops out)
module week_pattern(labels) {
    v(0);
    for (y = [H / 2, 0, -H / 2]) h(y);
    if (labels) {
        days = ["M", "T", "W", "TH", "F", "S", "SU"];
        cells = [[-H, H], [0, H], [-H, H / 2], [0, H / 2], [-H, 0], [0, 0], [-H, -H / 2]];
        for (i = [0 : 6])
            translate([cells[i][0] + 2.5, cells[i][1] - 7.5])
                text(days[i], size = 3.65, font = "Liberation Sans:style=Bold");
    }
}

// dots on a pitch; with axes, a slot each way through the middle
module grid_pattern(pitch, dot, axes) {
    n = floor(2 * H / pitch);
    off = -(n * pitch) / 2;
    for (i = [0 : n], j = [0 : n]) {
        x = off + i * pitch;
        y = off + j * pitch;
        if (!(axes && (abs(x) < 0.01 || abs(y) < 0.01)))
            translate([x, y]) circle(d = dot);
    }
    if (axes) { h(0); v(0); }
}

stencil(tab_width, tab_position, thickness)
    if (P[1] == "planner") planner_pattern(P[2]);
    else if (P[1] == "week") week_pattern(P[2]);
    else grid_pattern(P[2], P[3], P[4]);

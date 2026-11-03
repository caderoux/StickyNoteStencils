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

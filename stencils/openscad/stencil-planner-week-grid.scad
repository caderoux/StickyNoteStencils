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
include <stencil-common.scad>

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

// day letters, drawn as pen strokes slot_width wide, as the lines are (owner, 2026-11-03:
// cut from a bold font at 3.65 their strokes were about 0.6, too narrow for a pen). Each
// glyph is polylines, the strokes' centre lines, on a LETTER_H box of its own width; none
// closes a loop, so nothing drops out. LETTER_GAP of sheet between strokes not joined,
// between letters, and between a letter and a slot.
// The S's ends stop short of its middle (35 and -145 degrees): at 20 and -160 they
// closed its counters at the widest slot (2.5), and those dropped out.
LETTER_H = 6;
LETTER_GAP = 1.2;
function glyph_w(ch) = ch == "M" ? 5.5 : ch == "W" ? 6.5 : ch == "F" ? 3.8 : ch == "S" ? 4.2 : 4.5;
function arc(cx, cy, rx, ry, a0, a1, n = 12) =
    [for (k = [0 : n]) let(a = a0 + (a1 - a0) * k / n) [cx + rx * cos(a), cy + ry * sin(a)]];
function glyph(ch) = let(w = glyph_w(ch), h = LETTER_H)
    ch == "M" ? [[[0, 0], [0, h], [w / 2, h * 0.4], [w, h], [w, 0]]]
  : ch == "T" ? [[[0, h], [w, h]], [[w / 2, h], [w / 2, 0]]]
  : ch == "W" ? [[[0, h], [w / 4, 0], [w / 2, h * 0.6], [3 * w / 4, 0], [w, h]]]
  : ch == "H" ? [[[0, 0], [0, h]], [[w, 0], [w, h]], [[0, h / 2], [w, h / 2]]]
  : ch == "F" ? [[[w, h], [0, h], [0, 0]], [[0, h / 2], [w * 0.8, h / 2]]]
  : ch == "S" ? [concat(arc(w / 2, h * 3 / 4, w / 2, h / 4, 35, 270),
                        [for (q = [1 : 12]) arc(w / 2, h / 4, w / 2, h / 4, 90, -145)[q]])]
  :             [concat([[0, h]], arc(w / 2, w / 2, w / 2, w / 2, 180, 360), [[w, h]])];   // U

// the text's strokes, their top left at (x, y_top)
module lettering(text, x, y_top, i = 0) {
    if (i < len(text)) {
        for (line = glyph(text[i]), k = [0 : len(line) - 2])
            slot([x + line[k][0], y_top - LETTER_H + line[k][1]],
                 [x + line[k + 1][0], y_top - LETTER_H + line[k + 1][1]], slot_width);
        lettering(text, x + glyph_w(text[i]) + slot_width + LETTER_GAP, y_top, i + 1);
    }
}

// a 7-day week: two columns of four, the last cell for notes; day letters in each cell's
// top left, slot_width + LETTER_GAP in from its slots (the sheet's margin for the top and
// left ones)
module week_pattern(labels) {
    v(0);
    for (y = [H / 2, 0, -H / 2]) h(y);
    if (labels) {
        days = ["M", "T", "W", "TH", "F", "S", "SU"];
        cells = [[-H, H], [0, H], [-H, H / 2], [0, H / 2], [-H, 0], [0, 0], [-H, -H / 2]];
        inset = slot_width + LETTER_GAP;
        for (i = [0 : 6]) lettering(days[i], cells[i][0] + inset, cells[i][1] - inset);
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

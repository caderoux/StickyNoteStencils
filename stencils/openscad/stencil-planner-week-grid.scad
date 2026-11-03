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

// Sticky-note stencils: lines and checklists -- for 3 x 3 inch (76 mm) notes. A line per
// row, with a box at its left end, its right end, both or neither: pick a shape for each
// end, or None and the line runs on to the edge; None at both ends gives ruled lines. Flip
// the stencil over for the mirror image. The tab sits on the edge toward you when the
// stencil lies on the pad; give each stencil in a set a different tab position (1 to 5) so
// all the tabs show when they are stacked or stand in a holder.

/* [Stencil] */
// Number of rows (as many as fit with stencil between them: about 10 with boxes, 7 with a
// title)
rows = 8; // [1:1:14]
// Box at the left end of each line (None at both ends for ruled lines)
left_box = "square"; // [none:None, square:Square, circle:Circle, heart:Heart, triangle:Triangle]
// Box at the right end of each line
right_box = "none"; // [none:None, square:Square, circle:Circle, heart:Heart, triangle:Triangle]
// Columns
columns = 1; // [1:1:2]
// Large boxes
large_boxes = false;
// A title bar across the top
title = false;
// Rows bunched in threes, as manuscript paper
grouped = false;

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

/* [Hidden] */
include <stencil-common.scad>

// build.py's checks: settings that reproduce the prototype's named examples
// [prototype preset, rows, left_box, right_box, columns, large_boxes, title, grouped]
CHECKS = [
    ["lines-ruled-6", 6, "none", "none", 1, false, false, false],
    ["lines-ruled-8", 8, "none", "none", 1, false, false, false],
    ["lines-ruled-10", 10, "none", "none", 1, false, false, false],
    ["lines-manuscript", 9, "none", "none", 1, false, false, true],
    ["lines-ruled-with-title", 7, "none", "none", 1, false, true, false],
    ["checklist-squares-5", 5, "square", "none", 1, false, false, false],
    ["checklist-squares-8", 8, "square", "none", 1, false, false, false],
    ["checklist-squares-10", 10, "square", "none", 1, false, false, false],
    ["checklist-circles-5", 5, "circle", "none", 1, false, false, false],
    ["checklist-circles-8", 8, "circle", "none", 1, false, false, false],
    ["checklist-circles-10", 10, "circle", "none", 1, false, false, false],
    ["checklist-large-squares-4", 4, "square", "none", 1, true, false, false],
    ["checklist-two-columns-squares", 8, "square", "none", 2, false, false, false],
    ["checklist-two-columns-circles", 8, "circle", "none", 2, false, false, false],
    ["checklist-circles-and-squares", 8, "circle", "square", 1, false, false, false],
    ["checklist-hearts", 8, "heart", "none", 1, false, false, false],
    ["checklist-triangles", 8, "triangle", "none", 1, false, false, false],
    ["checklist-with-title", 7, "square", "none", 1, false, true, false],
];

ROW_BAR = 1.5;  // the narrowest stencil between rows: squares 10 has 1.51

// pitches from the first row to the last: grouped in threes, one more between groups
function row_steps(n) = n - 1 + (grouped ? floor((n - 1) / 3) : 0);

// a line per row with a box at either end, both or neither; the line is the row's
// baseline: its bottom edge level with the boxes' bottoms. Everything stays inside the
// pattern area, line ends included
module rows_pattern() {
    size = large_boxes ? LARGE_BOX : BOX;
    boxed = left_box != "none" || right_box != "none";
    top = H - (title ? TITLE + TITLE_GAP : 0);
    if (title) title_bar();
    height = boxed ? size : slot_width;          // a row's tallest cut
    y0 = top - height + slot_width / 2;          // the first and last baselines
    y1 = -H + slot_width / 2;
    // no more rows than leave ROW_BAR of stencil between one row and the next
    n = max([for (k = [1 : rows])
                 if (row_steps(k) == 0 || (y0 - y1) / row_steps(k) >= height + ROW_BAR - 1e-6)
                     k]);
    if (n < rows) echo(str("Only ", n, " rows fit; making ", n));
    pitch = n > 1 ? (y0 - y1) / row_steps(n) : 0;
    bases = grouped ? [for (k = [0 : n - 1]) y0 - pitch * (k + floor(k / 3))]
                    : rows_y(n, y0, y1);
    col_gap = 4;
    width = (2 * H - col_gap * (columns - 1)) / columns;
    for (c = [0 : columns - 1], base = bases) {
        x0 = -H + c * (width + col_gap);
        x1 = x0 + width;
        cy = base - slot_width / 2 + size / 2;   // a box's centre: standing on the line
        a = left_box != "none" ? x0 + size + GAP : x0;
        b = right_box != "none" ? x1 - size - GAP : x1;
        if (left_box != "none") box([x0 + size / 2, cy], size, left_box);
        if (right_box != "none") box([x1 - size / 2, cy], size, right_box);
        slot([a + slot_width / 2, base], [b - slot_width / 2, base], slot_width);
    }
}

stencil(tab_width, tab_position, thickness) rows_pattern();

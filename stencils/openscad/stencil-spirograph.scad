// Sticky-note stencil: spirograph -- for 3 x 3 inch (76 mm) notes. The stencil is a ring
// with teeth round its inside; a toothed wheel, printed with it, rolls round inside the ring
// with a pen in one of its holes. Each hole draws a different curve, and each wheel size a
// different figure (with the 64-tooth ring: 20 teeth 16 lobes, 24 teeth 8, 30 teeth 32,
// 36 teeth 16). Smooth teeth, as toy spirographs have, 0.15 clearance each side. Not yet
// test-printed: how well they roll is for a print to say.

/* [Stencil] */
// What to make: the ring stencil, a wheel, or both laid side by side
part = "both"; // [ring:Ring stencil, wheel:Wheel, both:Ring and wheel]
// Teeth on the wheel
wheel_teeth = 20; // [20:20 (16 lobes), 24:24 (8 lobes), 30:30 (32 lobes), 36:36 (16 lobes)]

/* [Tab] */
// Width across the top of the tab (11.5 lets five positions show; 15 suits three)
tab_width = 11.5; // [8:0.5:30]
// Where along the edge: 1 to 5 (for three tabs use 1, 3 and 5; for one, 3)
tab_position = 3; // [1:1:5]

/* [Print] */
// Stencil and wheel thickness
thickness = 1.6; // [0.8:0.2:3]

/* [Hidden] */
include <stencil-common.scad>
preset = "spirograph-ring-64";   // build.py's check: the ring stencil
RING = 64;                        // teeth inside the ring
SPIRO_M = 1;                      // module: tooth pitch / pi
SPIRO_DEPTH = 0.75;               // tooth half-height, in modules
SPIRO_CLEAR = 0.15;               // each side
SPIRO_HOLE = 2.5;                 // pen holes, as the library's original's

// a smooth-toothed gear's outline about its pitch circle; internal: the ring's (cut)
// outline, eased out by the clearance; else the wheel's, eased in
module gear(teeth, internal) {
    rp = teeth * SPIRO_M / 2 + (internal ? SPIRO_CLEAR : -SPIRO_CLEAR);
    n = teeth * 24;
    polygon([for (i = [0 : n - 1]) let(t = 360 * i / n, r = rp + SPIRO_DEPTH * SPIRO_M *
             cos(teeth * t)) [r * cos(t), r * sin(t)]]);
}

// the wheel: pen holes on a spiral from near its centre to near its teeth
module wheel2d(teeth) {
    rp = teeth * SPIRO_M / 2;
    inner = SPIRO_HOLE;
    outer = rp - SPIRO_DEPTH * SPIRO_M - SPIRO_HOLE;
    n = max(3, floor((outer - inner) / 1.2));
    difference() {
        gear(teeth, false);
        for (k = [0 : n - 1])
            let(r = inner + (outer - inner) * k / max(1, n - 1), a = k * 2.4 * 180 / PI)
                translate([r * cos(a), r * sin(a)]) circle(d = SPIRO_HOLE);
    }
}

module ring_stencil() stencil(tab_width, tab_position, thickness) gear(RING, true);

module wheel_part() {
    if (flat) wheel2d(wheel_teeth);
    else linear_extrude(thickness) wheel2d(wheel_teeth);
}

if (part == "ring") ring_stencil();
else if (part == "wheel") wheel_part();
else {
    ring_stencil();
    translate([SQUARE / 2 + 5 + wheel_teeth * SPIRO_M / 2 + 1, 0]) wheel_part();
}

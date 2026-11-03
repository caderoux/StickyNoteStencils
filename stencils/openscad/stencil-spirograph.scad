// Sticky-note stencil: spirograph -- for 3 x 3 inch (76 mm) notes. The stencil is a ring
// with teeth round its inside; a toothed wheel rolls round inside the ring with a pen in one
// of its holes. Each hole draws a different curve, and each wheel size a different figure
// (with the 64-tooth ring: 20 teeth 16 lobes, 24 teeth 8, 30 teeth 32, 36 teeth 16).
// Smooth teeth, as toy spirographs have, 0.15 clearance each side.
//
// A lip holds the wheel down (owner, 2026-11-03): the ring is two layers, its teeth on the
// paper and over them a LIP_T lip whose opening is LIP_OVER inside the teeth's tips, so the
// wheel's teeth run under it. The wheel is `thickness` (the ring's tooth layer Z_CLEAR more)
// with a raised ring on it, level with the ring's top, for a fingertip to push (owner: a
// raised ring between the teeth and the pen holes, not a raised middle -- the pen holes
// stay `thickness` deep). That raised ring clears the lip's edge by RIDGE_CLEAR where the
// wheel meets the ring, so it sits 1.9 inside the wheel's pitch circle, and the pen holes
// inside it: the outermost hole is 1.3 further in than before the lip. The ring prints
// lip down (its sheet mirrored, so the tab is where chosen once it is turned over), the
// wheel teeth down: neither overhangs. Not yet test-printed: how well they roll, and
// whether the lip holds, is for a print to say.

/* [Stencil] */
// What to make: the ring stencil and all four wheels on one plate, the ring alone, or one
// wheel
part = "all"; // [all:Ring and all wheels, ring:Ring stencil, wheel:One wheel]
// Teeth on the wheel, for One wheel
wheel_teeth = 20; // [20:20 (16 lobes), 24:24 (8 lobes), 30:30 (32 lobes), 36:36 (16 lobes)]

/* [Tab] */
// Width across the top of the tab (11.5 lets five positions show; 15 suits three)
tab_width = 11.5; // [8:0.5:30]
// Where along the edge: 1 to 5 (for three tabs use 1, 3 and 5; for one, 3)
tab_position = 3; // [1:1:5]

/* [Print] */
// The wheels' thickness; the ring's teeth are 0.2 more, under a 0.8 lip
thickness = 1.6; // [1.2:0.2:2.4]

/* [Hidden] */
include <stencil-common.scad>
preset = "spirograph-ring-64";   // build.py's check: the ring stencil
RING = 64;                        // teeth inside the ring
WHEELS = [20, 24, 30, 36];
SPIRO_M = 1;                      // module: tooth pitch / pi
SPIRO_DEPTH = 0.75;               // tooth half-height, in modules
SPIRO_CLEAR = 0.15;               // each side
SPIRO_HOLE = 2.5;                 // pen holes, as the library's original's
LIP_T = 0.8;                      // the lip: four layers of 0.2
LIP_OVER = 1.0;                   // the lip's opening inside the ring's tooth tips
Z_CLEAR = 0.2;                    // under the lip, over the wheel's teeth
RIDGE_W = 0.8;                    // the wheel's raised ring: two perimeters
RIDGE_CLEAR = 0.3;                // from the lip's edge, where the wheel meets the ring
HOLE_GAP = 0.6;                   // from the raised ring to a pen hole's edge
PLATE_GAP = 3;                    // between parts on the plate

TEETH_T = thickness + Z_CLEAR;    // the ring's tooth layer
RING_T = TEETH_T + LIP_T;         // the ring, and the wheel's raised ring's top
LIP_R = RING * SPIRO_M / 2 + SPIRO_CLEAR - SPIRO_DEPTH * SPIRO_M - LIP_OVER;

// a gear's pitch radius, and its tips' (a wheel's: eased in by the clearance)
function pitch_r(teeth) = teeth * SPIRO_M / 2;
function tip_r(teeth) = pitch_r(teeth) - SPIRO_CLEAR + SPIRO_DEPTH * SPIRO_M;
// the wheel's raised ring's outside: RIDGE_CLEAR inside the lip's edge with the wheel's
// pitch circle on the ring's
function ridge_r(teeth) = LIP_R - (pitch_r(RING) - pitch_r(teeth)) - RIDGE_CLEAR;

// a smooth-toothed gear's outline about its pitch circle; internal: the ring's (cut)
// outline, eased out by the clearance; else the wheel's, eased in
module gear(teeth, internal) {
    rp = teeth * SPIRO_M / 2 + (internal ? SPIRO_CLEAR : -SPIRO_CLEAR);
    n = teeth * 24;
    polygon([for (i = [0 : n - 1]) let(t = 360 * i / n, r = rp + SPIRO_DEPTH * SPIRO_M *
             cos(teeth * t)) [r * cos(t), r * sin(t)]]);
}

// the wheel: pen holes on a spiral from near its centre to HOLE_GAP inside its raised ring
module wheel2d(teeth) {
    inner = SPIRO_HOLE;
    outer = ridge_r(teeth) - RIDGE_W - HOLE_GAP - SPIRO_HOLE / 2;
    n = max(3, floor((outer - inner) / 1.2));
    difference() {
        gear(teeth, false);
        for (k = [0 : n - 1])
            let(r = inner + (outer - inner) * k / max(1, n - 1), a = k * 2.4 * 180 / PI)
                translate([r * cos(a), r * sin(a)]) circle(d = SPIRO_HOLE);
    }
}

// the ring as printed: the lip on the bed, the teeth over it; flat, its outline as used
module ring_stencil() {
    if (flat) stencil(tab_width, tab_position, thickness) gear(RING, true);
    else mirror([1, 0, 0]) {
        linear_extrude(LIP_T) difference() {
            sheet(tab_width, tab_position);
            circle(r = LIP_R, $fn = 4 * RING);
        }
        translate([0, 0, LIP_T - 0.01]) linear_extrude(TEETH_T + 0.01) difference() {
            sheet(tab_width, tab_position);
            gear(RING, true);
        }
    }
}

// a wheel as printed: the teeth on the bed, its raised ring on top
module wheel_part(teeth) {
    if (flat) wheel2d(teeth);
    else {
        linear_extrude(thickness) wheel2d(teeth);
        translate([0, 0, thickness - 0.01]) linear_extrude(RING_T - thickness + 0.01)
            difference() {
                circle(r = ridge_r(teeth), $fn = 96);
                circle(r = ridge_r(teeth) - RIDGE_W, $fn = 96);
            }
    }
}

// the plate: the ring, and beside it the wheels in two columns, the larger two nearer it
module plate() {
    ring_stencil();
    x1 = SQUARE / 2 + PLATE_GAP + tip_r(WHEELS[3]);
    x2 = x1 + tip_r(WHEELS[3]) + PLATE_GAP + tip_r(WHEELS[1]);
    for (p = [[WHEELS[3], x1, 1], [WHEELS[2], x1, -1], [WHEELS[1], x2, 1], [WHEELS[0], x2, -1]])
        translate([p[1], p[2] * (tip_r(p[0]) + PLATE_GAP / 2)]) wheel_part(p[0]);
}

if (part == "ring") ring_stencil();
else if (part == "wheel") wheel_part(wheel_teeth);
else plate();

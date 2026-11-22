"""Post-it, stencil and pen set for a 2 x 4 Gridfinity space: three separate bins
(owner) -- parametric CadQuery (B-rep CSG) source.

  postit-tray-2x2      a 76 mm (3 x 3 inch) sticky-note pad in a low tray, open at the
                       front across the pad's width but for a low lip, so a stencil can
                       lie on the pad with its tab out over the front, wherever the tab is
  stencil-holder-1x2   ten 76 mm square, 1.6 mm stencils standing on edge in comb slots,
                       lifted out by their tabs (owner: the stencils' tabs are staggered;
                       each stencil's whole top edge stands clear above the rim, wherever
                       its tab is)
  pen-holder-1x2       four marker holes and six pen holes (owner: a mix)
  spirograph-holder-1x2  the spirograph's ring and its four wheels on one side, seven
                       stencils beside them (owner, 2026-11-03: the ring with its lip is
                       2.6 thick, too thick for the stencil holder's slots; a 2 x 1 of its
                       own, the wheels in slots sized for each. 2026-11-05: the spirograph
                       on one side, standard stencil slots filling the other). Built as the
                       stencil holder, in the set's place for it or beside

2 x 2 + 1 x 2 + 1 x 2 fills the 2 x 4 space; the 1 x 2 bins go either way round. Each is
a standard Gridfinity bin (a foot per cell, 0.5 under the grid) with the stacking lip
(owner: stackable when empty, and the trays with pads in, for colours), and Gridfinity
Refined feet (owner): each cell's foot is taken from 1x1-block-refined.step (not in this
repository: download it from [ref] into this folder), so each has
four side-loading slots for 6 x 2 mm magnets, pushed in from the foot's sides before the
bin goes on the baseplate. Their roofs bridge (6 wide, at 2.4). Heights (owner): the
tray low, the other two 6 units. Each exports a STEP and an STL, in print orientation:
feet on the bed, no supports. Not yet test-printed.

Every dimension is derived from a source, noted inline:
  [gf]   = Gridfinity spec, checked against a rebuilt standard bin in the owner's archive
           (gridfinity/gf-rebuilt-bin-2x1x4-s1x1-standard-2136f)
           (sectioned: feet 35.6 at the bed, 37.2 from 0.8 to 2.6, 41.5 at 4.75)
  [ref]  = 1x1-block-refined.step, a Gridfinity Refined 1 x 1 block from
           https://www.printables.com/model/971527-gridfinity-refined-base-stpstep-files
           (a clean-sheet STEP remake, magnet slots sized for 0.2 layers and a 0.4 nozzle,
           no screw) of grizzie17's Gridfinity Refined, defined at
           https://www.printables.com/model/413761-gridfinity-refined . Its foot is the
           [gf] foot exactly (no material outside it) less four magnet slots.
  [note] = 3 x 3 inch sticky notes: 76 mm square
  [sten] = owner's stencils: 76 mm square before the tab, 1.6 mm thick (owner: 8 layers
           of 0.2; their printed ones measured 1.66)
  [own]  = the owner's earlier post-it holders with stencil slots, which their stencils
           fit, in the owner's archive: gridfinity/post-it-holder-gridfinity/post-it-holder-
           gridfinity-v2.stl and mounts-organizers/post-it-holder/post-it-holder-v4.stl
           (sectioned: six
           slots each, 2.0 x 77, at 3.0 and 3.2 pitch)
"""
import math
import os

import cadquery as cq

REFINED_STEP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1x1-block-refined.step")
_refined_foot = None


def refined_foot() -> cq.Solid:
    """[ref] The Refined block's foot, centred on the origin, its bottom on z = 0, cut
    0.5 into the plate above it so it fuses with the bin's body (the plate is the body's
    41.5 square there)."""
    global _refined_foot
    if _refined_foot is None:
        block = cq.importers.importStep(REFINED_STEP).val()   # x, y 0..41.5, foot z -4.75..0
        block = block.moved(cq.Location(cq.Vector(-41.5 / 2, -41.5 / 2, 4.75)))
        _refined_foot = block.intersect(cq.Solid.makeBox(60, 60, 4.75 + 0.5,
                                                        cq.Vector(-30, -30, 0)))
    return _refined_foot

# --- Gridfinity ----------------------------------------------------------------------------
GF = 42.0                # [gf] pitch
GAP = 0.5                # [gf] a bin is this much under the grid
U = 7.0                  # [gf] height unit; a bin's body is U * units tall, feet included
CORNER_R = 3.75          # [gf] the bin's outer corner radius
FOOT = (0.8, 1.8, 2.15)  # [gf] a foot's profile from the bed up: 45 degrees, straight, 45
FOOT_H = sum(FOOT)       # 4.75
# [gf] the stacking lip (owner: stackable; trays of different colours on each other), on
# the body's top: its inner face from there up, as (height, inset from the outer wall)
LIP = [(0.0, 2.6), (0.7, 1.9), (2.5, 1.9), (4.4, 0.0)]
LIP_TOP = 3.55           # [gf] the lip cut off flat here, 0.85 wide (as the reference bin)
STACK_DROP = 0.5         # a stacked bin's feet go 0.35 below the rim (its 45 degree faces
                         # seat on the lip's); room for them, where the top is solid
FLOOR_Z = U              # the floor inside, one unit up
WALL = 1.2               # three perimeters (0.4 nozzle)
TOP_R = 0.5              # the lip's outer top edge rounded (its top is only 0.85 wide)

# --- Post-it tray --------------------------------------------------------------------------
NOTE = 76.0              # [note]
TRAY_UNITS = 3           # owner: low; 14 deep over the floor, up to where a stacked tray's
                         # feet come
# The pocket is the lip's foot (LIP[0]) carried down to the floor: a stacked bin's feet
# drop 0.35 below the rim, wider than a pocket inset 3 (it was), which they hit. That
# leaves 1.15 round the pad.
# A stencil lies on the pad in use (owner), its tab out over the front, anywhere along
# that edge (the tabs are staggered): the front wall is open across the pocket's whole
# width down to FRONT_LIP over the floor, a lip that keeps the pad in. A stencil on the
# pad clears it until the pad is that thin. (It was a 50 wide notch for tearing sheets.)
FRONT_LIP = 2.0
# The lip notches' tips cut back from the pad's edge (76 across, untrimmed), so a stencil
# lifted straight out passes them with play (owner); their sides, on the stacked tray's
# foot corners, still hold it
NOTCH_TRIM = 0.6

# --- Stencil holder ------------------------------------------------------------------------
STENCIL = 76.0           # [sten] square, before the tab
STENCIL_T = 1.6          # [sten] (was 1.66)
STENCILS = 10            # owner: 8-10; 10 is enough
TALL_UNITS = 6           # owner: the stencil and pen holders
SLOT_W = 2.0             # [own] a slot's width (was 1.66 + 0.44, 2.1: an allowance for
                         # printed slots coming out narrow, not from a print)
END_CLEAR = 0.5          # [own] past each end of a stencil, to the bottom of its slot: 77
                         # long (was 0.3)
LEAD = 1.0               # the ribs' tops chamfered this much, to guide a stencil in
RIB_DEPTH = 6.0          # how far a stencil's end sits in its slot (owner's first print: the
                         # ribs ended at the stencils' ends, 0.3 clear, so the stencils stood
                         # free of them and fell over; [own] holders hold them full length)

# --- Spirograph holder --------------------------------------------------------------------
# [spiro] = ../stencils/openscad/stencil-spirograph.scad: the ring 2.6 thick (lip and all),
# the wheels 2.6 at their raised rings; tips SPIRO_M * teeth + 2 * (0.75 - 0.15) across.
SPIRO_T = 2.6            # [spiro]
SPIRO_SLOT = SPIRO_T + 0.4   # as the stencil slots, SLOT_W for 1.6
WHEEL_TIPS = {t: t + 1.2 for t in (20, 24, 30, 36)}   # [spiro] tip diameters
WHEEL_CLEAR = 0.5        # a wheel's cradle, round it (END_CLEAR)
WHEEL_SHOW = 1 / 3       # of a wheel's diameter, above the lip's top: to take hold of
SPIRO_RIB = 1.2          # each side of a slot: three perimeters
SPIRO_STENCILS = 7       # standard stencil slots beside them: as many as fit, ribs >= SPIRO_RIB
WHEEL_GAP = 2.0          # between two cradles in a row

# --- Pen holder ----------------------------------------------------------------------------
# All within the lip's opening (36.3 across): two pens side by side fit, three do not.
MARKER_D = 17.0          # markers and highlighters: two side by side at each end
PEN_D = 12.0             # pens: three rows of two between them (owner: a mix)
MARKER_X = 9.1           # the markers 1.2 apart, 0.55 inside the lip
PEN_X = 7.5              # the pens 3 apart
PEN_PITCH = 13.2         # the pens' rows, 1.2 apart


def rrect(w: float, l: float, r: float, x: float, y: float, z: float) -> cq.Wire:
    """A w by l rectangle with corners r, centred at (x, y), level at z."""
    face = cq.Sketch().rect(w, l).vertices().fillet(r)._faces.Faces()[0]
    return face.outerWire().moved(cq.Location(cq.Vector(x, y, z)))


def bin_body(nx: int, ny: int, units: int, keep: cq.Workplane = None) -> cq.Workplane:
    """A solid Gridfinity bin, nx by ny cells: a [ref] Refined foot under each cell, the
    body above them units tall, and the stacking lip on it (its inside cut, the bin
    otherwise solid). The lip's inside is a ruled loft through its [gf] sections, so its
    faces are the profile's 45 degree and straight faces exactly, corners concentric. (The
    feet were first the same kind of loft through FOOT, plain; the Refined foot is that
    exactly, less its magnet slots.) keep: solid left uncut (lip_notches)."""
    w, l = GF * nx - GAP, GF * ny - GAP
    cell = GF - GAP
    top = units * U
    solid = (cq.Workplane("XY", origin=(0, 0, FOOT_H)).sketch().rect(w, l)
             .vertices().fillet(CORNER_R).finalize().extrude(top + LIP_TOP - FOOT_H))
    for i in range(nx):
        for j in range(ny):
            x = -w / 2 + cell / 2 + i * GF
            y = -l / 2 + cell / 2 + j * GF
            foot = refined_foot().moved(cq.Location(cq.Vector(x, y, 0)))
            solid = solid.union(cq.Workplane("XY").add(foot))
    # the lip's inside, from the body's top, on up 1 past the lip's flat top on its 45
    h2, d2 = LIP[-2]
    d_end = d2 - (LIP_TOP + 1.0 - h2)
    levels = [(h, d) for h, d in LIP[:-1]] + [(LIP_TOP + 1.0, d_end)]
    wires = [rrect(w - 2 * d, l - 2 * d, CORNER_R - d, 0, 0, top + h) for h, d in levels]
    inside = cq.Workplane("XY").add(cq.Solid.makeLoft(wires, True))
    if keep is not None:
        inside = inside.cut(keep)
    return solid.cut(inside)


def lip_notches(nx: int, ny: int, units: int, walls=("left", "right", "back", "front"),
                trim: float = 0.0) -> cq.Workplane:
    """Lip notches (owner, after Gridfinity Extended's: stacked trays slid forward with the
    tray's front open): the lip shaped as one socket per cell, not one round the bin, so
    where two cells meet on a wall it keeps the ridge between their sockets' rounded
    corners. That ridge sits in the gap between the feet of the bin stacked above, and
    holds it along that wall. Each is the region on its wall between two cells, from the
    corners' centres (CORNER_R in) out into the wall, less the two cells' sockets (the lip's
    LIP sections, per cell); under the lip it is carried down at 45 degrees into the wall
    (a flat underside would overhang the pocket) to reach below the body's top. Returned as
    solid to keep: bin_body's keep, and cut from a pocket. trim: each cut back this far
    from its tip, toward its wall."""
    w, l = GF * nx - GAP, GF * ny - GAP
    cell = GF - GAP
    top = units * U
    d0 = LIP[0][1]
    drop = CORNER_R - d0 - trim                    # under the lip: down to where 45 meets
    h2, d2 = LIP[-2]
    levels = ([(-drop - 0.2, d0)] + [(h, d) for h, d in LIP[:-1]]
              + [(LIP_TOP + 1.0, d2 - (LIP_TOP + 1.0 - h2))])
    sockets = None
    for i in range(nx):
        for j in range(ny):
            x = -w / 2 + cell / 2 + i * GF
            y = -l / 2 + cell / 2 + j * GF
            loft = cq.Solid.makeLoft([rrect(cell - 2 * d, cell - 2 * d, CORNER_R - d, x, y,
                                            top + h) for h, d in levels], True)
            sockets = loft if sockets is None else sockets.fuse(loft)
    z0, z1 = top - drop - 0.2, top + LIP_TOP + 1.0
    half_y = GAP / 2 + CORNER_R                    # the corners' centres either side of the line
    out = None
    for wall in walls:
        # built on the right (+x) wall at the line y = 0, then turned and moved
        n_lines = (ny if wall in ("left", "right") else nx) - 1
        span = l if wall in ("left", "right") else w
        x_in = (w if wall in ("left", "right") else l) / 2 - CORNER_R + trim   # the tip
        for k in range(1, n_lines + 1):
            g = -span / 2 + k * GF - GAP / 2       # the line between cells k - 1 and k
            band = cq.Solid.makeBox(CORNER_R - 0.75 - trim, 2 * half_y, z1 - z0,
                                    cq.Vector(x_in, -half_y, z0))
            # under the lip: the band's inner face carried out at 45 degrees as it goes down
            wedge = (cq.Workplane("XZ").polyline([(x_in - 1, top), (x_in, top),
                                                  (x_in + drop + 1, top - drop - 1),
                                                  (x_in - 1, top - drop - 1)]).close()
                     .extrude(half_y + 1, both=True).val())
            band = band.cut(wedge)
            angle = {"right": 0, "back": 90, "left": 180, "front": 270}[wall]
            band = band.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), angle)
            shift = (0, g) if wall in ("left", "right") else (g, 0)
            band = band.translate(cq.Vector(*shift, 0))
            out = band if out is None else out.fuse(band)
    return cq.Workplane("XY").add(out.cut(sockets))


def round_top(part: cq.Workplane, z_top: float, pick) -> cq.Workplane:
    """Rounds the edges on the top's plane that pick(edge) selects, in one call (see
    CLAUDE.md: one edge at a time misses edges)."""
    solid = part.val()
    edges = [e for e in solid.Edges()
             if abs(e.BoundingBox().zmin - z_top) < 0.01 and abs(e.BoundingBox().zmax - z_top) < 0.01
             and pick(e)]
    return cq.Workplane("XY").add(solid.fillet(TOP_R, edges))


def on_outline(w: float, l: float):
    """Selects an edge on the bin's outer outline (w by l, corners CORNER_R)."""
    def pick(e):
        p = e.positionAt(0.5)
        dx, dy = abs(p.x) - (w / 2 - CORNER_R), abs(p.y) - (l / 2 - CORNER_R)
        if dx > 0 and dy > 0:
            return abs(math.hypot(dx, dy) - CORNER_R) < 0.05
        return abs(abs(p.x) - w / 2) < 0.05 or abs(abs(p.y) - l / 2) < 0.05
    return pick


def lip_shelf(iw: float, il: float, ir: float, w: float, l: float, top: float) -> cq.Workplane:
    """The pocket's top, iw by il (corners ir), closing in at 45 degrees to the lip's foot
    (LIP[0]) at the body's top: cut from a pocket whose wall is thinner than the lip, it
    leaves a shelf under the lip instead of a flat overhang."""
    d_lip = LIP[0][1]
    lw, ll = w - 2 * d_lip, l - 2 * d_lip
    rise = max((iw - lw) / 2, (il - ll) / 2)
    return cq.Workplane("XY").add(cq.Solid.makeLoft(
        [rrect(iw, il, ir, 0, 0, top - rise), rrect(lw, ll, CORNER_R - d_lip, 0, 0, top)], True))


def postit_tray() -> cq.Workplane:
    """2 x 2, TRAY_UNITS: a square pocket for the pad, the front (-y) wall open across it
    down to FRONT_LIP (through the stacking lip too), the front corners with it, so the side
    walls end square. The pocket is the lip's foot carried down, so the lip stands on its
    walls. A tray stacked on it sits on the back and side lips, and lip notches on those
    (the front has none) hold it: without them it slid forward (owner)."""
    top = TRAY_UNITS * U
    w = l = 2 * GF - GAP
    notches = lip_notches(2, 2, TRAY_UNITS, walls=("left", "right", "back"), trim=NOTCH_TRIM)
    body = bin_body(2, 2, TRAY_UNITS, keep=notches)
    d = LIP[0][1]
    hole = cq.Workplane("XY").add(cq.Solid.extrudeLinear(
        cq.Face.makeFromWires(rrect(w - 2 * d, l - 2 * d, CORNER_R - d, 0, 0, FLOOR_Z)),
        cq.Vector(0, 0, top - FLOOR_Z + 0.01))).cut(notches)
    # the opening: the whole width, from FRONT_LIP up, back to where the corners' rounding
    # starts, so the side walls end square in their full profile, lip and all (owner: cut to
    # the pocket's width all the way up, slivers of the corners and a notch in the lip were
    # left at both ends; cut to the pocket's width and then the lip's, the corners kept a
    # nub of lip standing 0.8 proud of its sloping face and a wall end thinning to 0.2)
    back = -l / 2 + CORNER_R + 0.01                # past the corners' rounding
    opening = (cq.Workplane("XY").box(w + 2, back + l / 2 + 1, top + LIP_TOP + 1 - FLOOR_Z
                                      - FRONT_LIP, centered=False)
               .translate((-w / 2 - 1, -l / 2 - 1, FLOOR_Z + FRONT_LIP)))
    body = body.cut(hole).cut(opening)
    return round_top(body, top + LIP_TOP, on_outline(w, l))


def end_block(x0: float, x1: float, y_in: float, sgn: int, il: float, top: float) -> cq.Workplane:
    """From the end wall (sgn) in to y_in, x0 to x1, floor to top, its top chamfered LEAD."""
    y_wall = sgn * il / 2
    prof = [(y_wall + sgn * 0.01, FLOOR_Z - 0.01), (sgn * y_in, FLOOR_Z - 0.01),
            (sgn * y_in, top - LEAD), (sgn * (y_in + LEAD), top), (y_wall + sgn * 0.01, top)]
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(prof).close().extrude(x1 - x0)


def stencil_holder() -> cq.Workplane:
    """1 x 2, TALL_UNITS: a pocket the length of the bin; on each end wall a backing out to
    the slots' bottoms, END_CLEAR past a stencil's end, and from it a comb of ribs, full
    height, RIB_DEPTH in, leaving STENCILS slots SLOT_W wide. The stencils stand on the
    floor across the bin (thickness along x, their 76 along y), each end RIB_DEPTH into its
    slot, all within the lip's opening so they lift out past it. The backing's and ribs'
    tops are chamfered LEAD at 45 degrees. The walls are thinner than the lip's foot, so the
    pocket closes in under it at 45 degrees."""
    top = TALL_UNITS * U
    w, l = GF - GAP, 2 * GF - GAP
    body = bin_body(1, 2, TALL_UNITS)
    iw, il = w - 2 * WALL, l - 2 * WALL
    ir = CORNER_R - WALL
    shelf = lip_shelf(iw, il, ir, w, l, top)
    z_shelf = shelf.val().BoundingBox().zmin
    hole = (cq.Workplane("XY", origin=(0, 0, FLOOR_Z)).sketch().rect(iw, il)
            .vertices().fillet(ir).finalize().extrude(z_shelf - FLOOR_Z))   # meets the shelf exactly
    body = body.cut(hole).cut(shelf)
    y_bottom = STENCIL / 2 + END_CLEAR             # the slots' bottoms
    y_tip = y_bottom - RIB_DEPTH                   # the ribs' tips
    span = w - 2 * LIP[0][1]                       # the lip's opening, across
    pitch = span / STENCILS
    xs = [-span / 2 + pitch * (k + 0.5) for k in range(STENCILS)]   # the slots' centres
    ribs = None
    for sgn in (-1, 1):
        backing = end_block(-iw / 2, iw / 2, y_bottom, sgn, il, top)
        ribs = backing if ribs is None else ribs.union(backing)
        for k in range(STENCILS + 1):              # between and outside the slots
            x0 = -iw / 2 if k == 0 else xs[k - 1] + SLOT_W / 2
            x1 = iw / 2 if k == STENCILS else xs[k] - SLOT_W / 2
            ribs = ribs.union(end_block(x0, x1, y_tip, sgn, il, top))
    return round_top(body.union(ribs), top + LIP_TOP, on_outline(w, l))


def pen_holder() -> cq.Workplane:
    """1 x 2, TALL_UNITS: holes down to the floor, all within the lip's opening. Two
    markers side by side at each end, three rows of two pens between them."""
    top = TALL_UNITS * U
    w, l = GF - GAP, 2 * GF - GAP
    body = bin_body(1, 2, TALL_UNITS)
    open_l = l / 2 - LIP[0][1]                     # the lip's opening, half its length
    marker_y = open_l - MARKER_D / 2 - 0.3
    holes = [(x, y, MARKER_D) for y in (-marker_y, marker_y) for x in (-MARKER_X, MARKER_X)]
    holes += [(x, y, PEN_D) for y in (-PEN_PITCH, 0.0, PEN_PITCH) for x in (-PEN_X, PEN_X)]
    for x, y, d in holes:
        body = body.cut(cq.Workplane("XY", origin=(x, y, FLOOR_Z)).circle(d / 2)
                        .extrude(top - FLOOR_Z + 0.01))
    # the top is solid: a recess the lip's foot across, STACK_DROP deep, for the feet of a
    # bin stacked on it
    d = LIP[0][1]
    body = body.cut(cq.Workplane("XY").add(cq.Solid.extrudeLinear(
        cq.Face.makeFromWires(rrect(w - 2 * d, l - 2 * d, CORNER_R - d, 0, 0, top - STACK_DROP)),
        cq.Vector(0, 0, STACK_DROP + 0.01))))
    return round_top(body, top + LIP_TOP, on_outline(w, l))


def spirograph_holder() -> cq.Workplane:
    """1 x 2, TALL_UNITS: the stencil holder's pocket, its slots across the lip's opening.
    On one side (owner, 2026-11-05: the spirograph on one side, standard stencil slots
    filling the other) a block along the bin, end wall to end wall, floor to the body's
    top, with three SPIRO_SLOT slots and SPIRO_RIB between and after them: two rows of
    wheels (the two larger, then the two smaller), then the ring standing on the floor, as
    the stencils stand. Each wheel sits in a cradle: a round-bottomed slot WHEEL_CLEAR round
    it, deep enough that WHEEL_SHOW of the wheel stands above the lip's top. Across the
    rest, the stencil holder's backings and end ribs, SPIRO_STENCILS slots SLOT_W wide,
    the ribs between them dividing what is left. The slots' sides are vertical and their
    bottoms face up: nothing overhangs. All within the lip's opening, so everything lifts
    out past it."""
    top = TALL_UNITS * U
    w, l = GF - GAP, 2 * GF - GAP
    body = bin_body(1, 2, TALL_UNITS)
    iw, il = w - 2 * WALL, l - 2 * WALL
    ir = CORNER_R - WALL
    shelf = lip_shelf(iw, il, ir, w, l, top)
    z_shelf = shelf.val().BoundingBox().zmin
    hole = (cq.Workplane("XY", origin=(0, 0, FLOOR_Z)).sketch().rect(iw, il)
            .vertices().fillet(ir).finalize().extrude(z_shelf - FLOOR_Z))   # meets the shelf exactly
    body = body.cut(hole).cut(shelf)
    span = w - 2 * LIP[0][1]                       # the lip's opening, across
    open_l = l - 2 * LIP[0][1]                     # and along
    rows = [(36, 30), (24, 20), None]              # None: the ring
    spiro_w = len(rows) * (SPIRO_SLOT + SPIRO_RIB)
    rib = (span - spiro_w - SPIRO_STENCILS * SLOT_W) / (SPIRO_STENCILS - 1)
    assert rib >= SPIRO_RIB, "stencil slots: too many for the opening"
    x_block = -span / 2 + spiro_w                  # the block's face: the first stencil slot's side
    block = cq.Solid.makeBox(x_block + iw / 2 + 0.01, il + 0.02, top - FLOOR_Z + 0.01,
                             cq.Vector(-iw / 2 - 0.01, -il / 2 - 0.01, FLOOR_Z - 0.01))
    for k, wheels in enumerate(rows):
        x0 = -span / 2 + k * (SPIRO_SLOT + SPIRO_RIB)   # the slot's side
        if wheels is None:                         # the ring, on the floor
            block = block.cut(cq.Solid.makeBox(SPIRO_SLOT, STENCIL + 2 * END_CLEAR,
                                               top - FLOOR_Z + 1,
                                               cq.Vector(x0, -STENCIL / 2 - END_CLEAR, FLOOR_Z)))
            continue
        radii = [WHEEL_TIPS[t] / 2 + WHEEL_CLEAR for t in wheels]
        assert sum(2 * r for r in radii) + WHEEL_GAP <= open_l, "wheels: longer than the opening"
        y = -(sum(2 * r for r in radii) + WHEEL_GAP) / 2
        for t, r in zip(wheels, radii):
            yc = y + r
            y += 2 * r + WHEEL_GAP
            d = WHEEL_TIPS[t]
            zc = top + LIP_TOP + WHEEL_SHOW * d - d / 2     # the wheel's centre
            cradle = cq.Solid.makeCylinder(r, SPIRO_SLOT, cq.Vector(x0, yc, zc), cq.Vector(1, 0, 0))
            if zc < top:                           # straight sides up from its middle
                cradle = cradle.fuse(cq.Solid.makeBox(SPIRO_SLOT, 2 * r, top + 1 - zc,
                                                      cq.Vector(x0, yc - r, zc)))
            block = block.cut(cradle)
    ribs = cq.Workplane("XY").add(block)
    y_bottom = STENCIL / 2 + END_CLEAR             # the slots' bottoms, as the stencil holder's
    y_tip = y_bottom - RIB_DEPTH
    xs = [x_block + k * (SLOT_W + rib) for k in range(SPIRO_STENCILS)]   # the slots' sides
    for sgn in (-1, 1):
        ribs = ribs.union(end_block(x_block - 0.01, iw / 2, y_bottom, sgn, il, top))
        for k in range(SPIRO_STENCILS):            # after each slot
            x0 = xs[k] + SLOT_W
            x1 = iw / 2 if k == SPIRO_STENCILS - 1 else xs[k + 1]
            ribs = ribs.union(end_block(x0, x1, y_tip, sgn, il, top))
    return round_top(body.union(ribs), top + LIP_TOP, on_outline(w, l))

PARTS = {"postit-tray-2x2": postit_tray, "stencil-holder-1x2": stencil_holder,
         "pen-holder-1x2": pen_holder, "spirograph-holder-1x2": spirograph_holder}

if __name__ == "__main__":
    import sys
    for name in (sys.argv[1:] or PARTS):
        part = PARTS[name]()
        cq.exporters.export(part, name + ".step")
        cq.exporters.export(part, name + ".stl", tolerance=0.01, angularTolerance=0.1)
        bb = part.val().BoundingBox()
        print(name, "bbox", [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax,
                                                    bb.zmax)],
              "volume", round(part.val().Volume(), 1), "valid", part.val().isValid(),
              "solids", len(part.solids().vals()))

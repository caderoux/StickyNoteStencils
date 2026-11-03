"""Sticky-note stencil generator, prototype (owner: one conformed stencil per kind, with
options, covering many originals each -- not a copy of every original; toward a parametric
generator on MakerWorld: category, then name, the tab's width and position (1 to 5), and the
thickness).

The library's originals (sources/, measured in catalog.csv) reduce to a few types, each
drawn from a handful of settings; PRESETS names the useful settings of each, and
library.csv maps every original pattern to the preset closest to it. The shapes (a heart,
a lightbulb...) are drawn here from scratch (owner: redrawn, not taken from others'
designs, several of which do not allow redistribution). This is the reference the
OpenSCAD generator is to match: same types, settings and presets.

The standard: a SQUARE sheet (corners CORNER_R), a tab on its bottom edge of a chosen width
at position 1 to 5 (conform.tab_centre), the pattern kept MARGIN inside the edges. Bottom:
lying on the pad the tab sticks out toward the user, so every pattern is drawn upright with
its foot toward the tab (owner) -- titles and headings at the far edge, the first row the
furthest from the tab, a heart's point and a lightbulb's base toward it.
Pen slots are SLOT wide with round ends. Nothing may cut off an island: a closed loop of
slot, or a letter with a counter (O, A, D...), would drop out -- generate() checks the
sheet stays one piece.

Modes:
  python stencilgen.py           every preset's thumbnail (thumbnails/<category>/<name>.svg)
                                 and gallery.png, a contact sheet of them all
"""
import math
import os

import numpy as np
import shapely.affinity as sa
import shapely.geometry as sg
import shapely.ops as so

import conform

HERE = os.path.dirname(os.path.abspath(__file__))
SQUARE = conform.SQUARE
MARGIN = 7.0             # the pattern's edge to the sheet's
SLOT = 1.6               # a pen slot's width (the originals' run 1.2 to 2.0)
BOX = 5.0                # a checkbox; LARGE_BOX for the large ones
LARGE_BOX = 8.0
GAP = 2.0                # between a box and its line
ROW_BAR = 1.5            # the narrowest stencil between rows: squares 10 has 1.51 (at 14
                         # rows the boxes ran into each other)
TITLE_GAP = 5.0          # between the title bar and the first row (was 3)
TITLE = 9.0              # a title bar's height: room to write a word or two (owner: larger;
                         # was 5)
H = SQUARE / 2 - MARGIN  # the pattern's half extent


def slot(x0, y0, x1, y1, w=SLOT):
    """A pen slot from (x0, y0) to (x1, y1), w wide, round ended."""
    return sg.LineString([(x0, y0), (x1, y1)]).buffer(w / 2, cap_style="round")


def box(cx, cy, size, shape):
    if shape == "square":
        return sg.box(cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2).buffer(
            -0.5).buffer(0.5)
    if shape == "circle":
        return sg.Point(cx, cy).buffer(size / 2)
    if shape == "triangle":                       # pointing down, as a bullet
        r = size / 2
        return sg.Polygon([(cx - r, cy + r * 0.8), (cx + r, cy + r * 0.8), (cx, cy - r)])
    if shape == "heart":
        t = np.linspace(0, 2 * math.pi, 64)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        k = size / 32
        return sg.Polygon(list(zip(cx + x * k, cy + y * k + size * 0.05)))
    raise ValueError(shape)


def rows_y(n, top=H, bottom=-H):
    """n rows' centres, evenly from top to bottom."""
    if n == 1:
        return [(top + bottom) / 2]
    return [top - (top - bottom) * k / (n - 1) for k in range(n)]


# --- the types -------------------------------------------------------------------------------
def ruled(rows=8, left="square", right=None, columns=1, size=BOX, title=False,
          grouped=False):
    """A line per row, with a box at its left end, its right end, both or neither: left and
    right each a shape or None (owner: a shape for each end covers squares, circles,
    hearts, triangles and mixed ends; with no box at an end the line runs on to the edge;
    with none at either it is ruled lines, so lines and checklists are one type). One or
    two columns; grouped bunches the rows in threes, a row's gap between groups, as
    manuscript paper. The line is the row's baseline: its bottom edge level with the
    boxes' bottoms, the boxes standing on it (owner: not centred on the box). Everything
    stays inside the pattern area, line ends included (the ruled lines' round ends went
    0.8 past it, before the types merged). No more rows than leave ROW_BAR of stencil
    between one row and the next."""
    top = H - (TITLE + TITLE_GAP if title else 0)
    cuts = []
    if title:
        cuts.append(sg.box(-H, H - TITLE, H, H).buffer(-0.8).buffer(0.8))
    height = size if (left or right) else SLOT        # a row's tallest cut
    y0 = top - height + SLOT / 2                      # the first and last baselines
    y1 = -H + SLOT / 2
    n = max(k for k in range(1, rows + 1)
            if row_steps(k, grouped) == 0 or (y0 - y1) / row_steps(k, grouped) >= height + ROW_BAR - 1e-6)
    pitch = (y0 - y1) / row_steps(n, grouped) if n > 1 else 0
    bases = ([y0 - pitch * (k + k // 3) for k in range(n)] if grouped
             else rows_y(n, y0, y1))
    col_gap = 4.0
    width = (2 * H - col_gap * (columns - 1)) / columns
    for c in range(columns):
        x0 = -H + c * (width + col_gap)
        x1 = x0 + width
        for base in bases:
            a, b = x0, x1
            cy = base - SLOT / 2 + size / 2               # a box's centre: standing on the line
            if left:
                cuts.append(box(x0 + size / 2, cy, size, left))
                a = x0 + size + GAP
            if right:
                cuts.append(box(x1 - size / 2, cy, size, right))
                b = x1 - size - GAP
            cuts.append(slot(a + SLOT / 2, base, b - SLOT / 2, base))
    return cuts


def row_steps(n, grouped):
    """Pitches from the first row to the last: grouped in threes, one more between
    groups."""
    return n - 1 + ((n - 1) // 3 if grouped else 0)


def planner(layout="quadrants"):
    """Dividers: quadrants, focus (one big area over a strip), pros & cons (two columns
    under a heading line), two columns, two rows."""
    v = lambda x, y0=-H, y1=H: slot(x, y0, x, y1)
    h = lambda y, x0=-H, x1=H: slot(x0, y, x1, y)
    return {"quadrants": [v(0), h(0)],
            "focus": [v(0, -H, -H / 3), h(-H / 3)],
            "pros-cons": [v(0, -H, H - 8), h(H - 8)],
            "two-columns": [v(0)],
            "two-rows": [h(0)]}[layout]


def week(labels=True):
    """A 7-day week: two columns of four, the last cell for notes; day letters (none with
    a counter, so nothing drops out)."""
    cuts = [slot(0, -H, 0, H)] + [slot(-H, y, H, y) for y in (H / 2, 0, -H / 2)]
    if labels:
        from matplotlib.font_manager import FontProperties
        from matplotlib.textpath import TextPath
        days = ["M", "T", "W", "TH", "F", "S", "SU"]
        cells = [(-H, H), (0, H), (-H, H / 2), (0, H / 2), (-H, 0), (0, 0), (-H, -H / 2)]
        for d, (x, y) in zip(days, cells):
            tp = TextPath((0, 0), d, size=5, prop=FontProperties(family="DejaVu Sans",
                                                                 weight="bold"))
            polys = [sg.Polygon(p) for p in tp.to_polygons() if len(p) > 2]
            g = so.unary_union(polys)
            cuts.append(sa.translate(g, x + 2.5, y - 7.5))
    return cuts


def grid(kind="dots", pitch=5.0, dot=1.6, axes=False):
    """Dots on a pitch; with axes, a slot each way through the middle."""
    n = int(2 * H // pitch)
    off = -(n * pitch) / 2
    cuts = [sg.Point(off + i * pitch, off + j * pitch).buffer(dot / 2)
            for i in range(n + 1) for j in range(n + 1)
            if not (axes and (abs(off + i * pitch) < 0.01 or abs(off + j * pitch) < 0.01))]
    if axes:
        cuts += [slot(-H, 0, H, 0), slot(0, -H, 0, H)]
    return cuts


SHAPE_MARGIN = 4.0       # a shape (one big cut-out) may come nearer the edge than lines:
                         # a 4 frame keeps the sheet stiff (owner: fill more of the note;
                         # was 0.8 of the pattern area, 49.6)
SHAPE = SQUARE - 2 * SHAPE_MARGIN   # a shape's size, at 100%: its larger extent (68)


def fit(g):
    """A drawn shape centred and scaled so its larger extent is SHAPE."""
    x0, y0, x1, y1 = g.bounds
    g = sa.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
    k = SHAPE / max(x1 - x0, y1 - y0)
    return sa.scale(g, k, k, origin=(0, 0))


def curve(fx, fy, n=180):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return sg.Polygon(list(zip(fx(t), fy(t))))


def shape(name):
    """A fixed outline, drawn here, upright: its foot toward the tab (-y)."""
    if name == "circle":
        g = sg.Point(0, 0).buffer(1, 64)
    elif name == "ellipse":
        g = sa.scale(sg.Point(0, 0).buffer(1, 64), 0.75, 1)
    elif name == "rounded-square":
        g = sg.box(-1, -1, 1, 1).buffer(-0.25).buffer(0.25)
    elif name == "star":                          # five points, one up
        pts = [((1 if k % 2 == 0 else 0.42) * math.sin(k * math.pi / 5),
                (1 if k % 2 == 0 else 0.42) * math.cos(k * math.pi / 5)) for k in range(10)]
        g = sg.Polygon(pts)
    elif name == "heart":                         # point down
        g = curve(lambda t: 16 * np.sin(t) ** 3,
                  lambda t: 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t)
                  - np.cos(4 * t))
    elif name == "arrow":                         # pointing right
        g = sg.Polygon([(-1, -0.22), (0.25, -0.22), (0.25, -0.55), (1, 0), (0.25, 0.55),
                        (0.25, 0.22), (-1, 0.22)])
    elif name == "cloud":                         # bumps over a flat foot
        bumps = [(-0.62, -0.05, 0.36), (-0.22, 0.28, 0.46), (0.28, 0.22, 0.42),
                 (0.66, -0.06, 0.32), (0.0, -0.1, 0.45)]
        g = so.unary_union([sg.Point(x, y).buffer(r, 48) for x, y, r in bumps])
        g = g.union(sg.box(-0.62, -0.38, 0.66, -0.05).buffer(0.1)).intersection(
            sg.box(-2, -0.42, 2, 2))
    elif name == "speech-bubble":                 # its tail down, toward the tab
        body = sa.scale(sg.Point(0, 0.12).buffer(1, 64), 1, 0.72)
        tail = sg.Polygon([(-0.45, -0.35), (-0.1, -0.45), (-0.7, -0.95)])
        g = body.union(tail)
    elif name == "lightbulb":                     # its base down; the screw thread as
        bulb = sg.Point(0, 0.35).buffer(0.62, 64)  # separate bars, so none drops out
        neck = sg.Polygon([(-0.42, 0.0), (0.42, 0.0), (0.26, -0.42), (-0.26, -0.42)])
        g = bulb.union(neck)
        bars = [sg.box(-0.27, y - 0.035, 0.27, y + 0.035).buffer(0.02)   # 0.06 apart: ~1.5
                for y in (-0.55, -0.71, -0.87)]
        tip = sg.box(-0.12, -1.02, 0.12, -0.96).buffer(0.04)
        return [fit(so.unary_union([g] + bars + [tip]))]
    else:
        raise ValueError(name)
    return [fit(g)]


def blank():
    return []


# --- spirograph (owner: the "starburst" is a spirograph's ring, which needs a gear) -------
# The library's one (sources/makerworld-sticky-note-stencil/spirograph.stl): a ring of 65
# teeth inside (30.2 to 32.5 from its centre) and a 21 wheel of 20 teeth with five 2.5 pen
# holes, both module about 0.95. Here: module SPIRO_M, smooth (sinusoidal) teeth, as toy
# spirographs have; the wheel SPIRO_CLEAR smaller all round so the two roll. Not yet
# printed: how well they roll is a test print's to say.
SPIRO_M = 1.0
SPIRO_DEPTH = 0.75       # tooth half-height, in modules
SPIRO_CLEAR = 0.15       # each side
SPIRO_HOLE = 2.5         # pen holes, as the original's
# The lip (owner, 2026-11-03; the generator, openscad/stencil-spirograph.scad, builds it in
# 3D): a lip over the ring's teeth, its opening LIP_OVER inside their tips, holds the wheel
# down; the wheel's raised ring stays RIDGE_CLEAR inside the lip's edge, and its pen holes
# HOLE_GAP inside that.
LIP_OVER = 1.0
RIDGE_W = 0.8
RIDGE_CLEAR = 0.3
HOLE_GAP = 0.6


def gear_outline(teeth, internal=False, m=SPIRO_M):
    """A smooth-toothed gear's outline: radius about the pitch circle (teeth * m / 2),
    SPIRO_DEPTH modules either way. internal: the ring's (cut) outline, eased out by the
    clearance; else the wheel's, eased in."""
    rp = teeth * m / 2 + (SPIRO_CLEAR if internal else -SPIRO_CLEAR)
    t = np.linspace(0, 2 * math.pi, teeth * 24, endpoint=False)
    r = rp + SPIRO_DEPTH * m * np.cos(teeth * t)
    return sg.Polygon(list(zip(r * np.cos(t), r * np.sin(t))))


def spirograph(ring=64):
    """The stencil: an internally toothed ring cut from the sheet, centred."""
    return [gear_outline(ring, internal=True)]


def ridge_r(teeth, ring=64):
    """The wheel's raised ring's outside: RIDGE_CLEAR inside the lip's edge with the
    wheel's pitch circle on the ring's."""
    lip_r = ring * SPIRO_M / 2 + SPIRO_CLEAR - SPIRO_DEPTH * SPIRO_M - LIP_OVER
    return lip_r - (ring - teeth) * SPIRO_M / 2 - RIDGE_CLEAR


def wheel(teeth=20, holes=None):
    """The wheel that rolls in the ring: a gear with pen holes on a spiral from near its
    centre to HOLE_GAP inside its raised ring, each a different curve. (Before the lip they
    ran out to SPIRO_HOLE inside the teeth's roots, 1.3 further.)"""
    g = gear_outline(teeth)
    inner = SPIRO_HOLE
    outer = ridge_r(teeth) - RIDGE_W - HOLE_GAP - SPIRO_HOLE / 2
    n = holes or max(3, int((outer - inner) / 1.2))
    cuts = []
    for k in range(n):
        r = inner + (outer - inner) * k / max(1, n - 1)
        a = k * 2.4                                   # the golden angle, about: spread out
        cuts.append(sg.Point(r * math.cos(a), r * math.sin(a)).buffer(SPIRO_HOLE / 2))
    body = g.difference(so.unary_union(cuts))
    if body.geom_type != "Polygon":
        raise ValueError("wheel: pen holes break it")
    return body


PRESETS = {   # category -> name -> (type, settings)
    "lines": {
        "ruled-6": (ruled, dict(rows=6, left=None)),
        "ruled-8": (ruled, dict(rows=8, left=None)),
        "ruled-10": (ruled, dict(rows=10, left=None)),
        "manuscript": (ruled, dict(rows=9, left=None, grouped=True)),
        "ruled-with-title": (ruled, dict(rows=7, left=None, title=True)),
    },
    "checklist": {
        "squares-5": (ruled, dict(rows=5)),
        "squares-8": (ruled, dict(rows=8)),
        "squares-10": (ruled, dict(rows=10)),
        "circles-5": (ruled, dict(rows=5, left="circle")),
        "circles-8": (ruled, dict(rows=8, left="circle")),
        "circles-10": (ruled, dict(rows=10, left="circle")),
        "large-squares-4": (ruled, dict(rows=4, size=LARGE_BOX)),
        "two-columns-squares": (ruled, dict(rows=8, columns=2)),
        "two-columns-circles": (ruled, dict(rows=8, columns=2, left="circle")),
        "circles-and-squares": (ruled, dict(rows=8, left="circle", right="square")),
        "hearts": (ruled, dict(rows=8, left="heart")),
        "triangles": (ruled, dict(rows=8, left="triangle")),
        "with-title": (ruled, dict(rows=7, title=True)),
    },
    "planner": {
        "quadrants": (planner, dict(layout="quadrants")),
        "focus": (planner, dict(layout="focus")),
        "pros-cons": (planner, dict(layout="pros-cons")),
        "two-columns": (planner, dict(layout="two-columns")),
        "two-rows": (planner, dict(layout="two-rows")),
    },
    "week": {
        "week-labelled": (week, dict(labels=True)),
        "week-grid": (week, dict(labels=False)),
    },
    "grid": {
        "dots": (grid, dict()),
        "graph": (grid, dict(axes=True)),
    },
    "shapes": {
        "arrow": (shape, dict(name="arrow")),
        "circle": (shape, dict(name="circle")),
        "cloud": (shape, dict(name="cloud")),
        "ellipse": (shape, dict(name="ellipse")),
        "heart": (shape, dict(name="heart")),
        "lightbulb": (shape, dict(name="lightbulb")),
        "rounded-square": (shape, dict(name="rounded-square")),
        "speech-bubble": (shape, dict(name="speech-bubble")),
        "star": (shape, dict(name="star")),
    },
    "spirograph": {   # the stencil is the ring; WHEELS are the gears printed with it
        "ring-64": (spirograph, dict(ring=64)),
    },
    "blank": {
        "blank": (blank, dict()),
    },
}


WHEELS = [20, 24, 30, 36]   # with the 64 ring: 16, 8, 32, 16 lobes


def generate(category, name, tab_width=conform.TAB_W, position=3):
    """The stencil as a polygon: the sheet with its tab, the pattern cut out. Raises if
    the pattern would cut off an island."""
    fn, kw = PRESETS[category][name]
    cuts = so.unary_union(fn(**kw)) if fn is not blank else sg.Polygon()
    body = conform.sheet(tab_width, position).difference(cuts)
    if body.geom_type != "Polygon":
        raise ValueError(f"{category}/{name}: the pattern cuts off {len(body.geoms) - 1} "
                         "island(s)")
    return body


def svg(body, path, title=""):
    pad = 2.0
    x0, y0, x1, y1 = body.bounds
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad

    def ring(coords):
        return "M" + " L".join(f"{x - x0 + pad:.2f},{y1 - y + pad:.2f}" for x, y in coords) + " Z"

    d = ring(body.exterior.coords) + " " + " ".join(ring(i.coords) for i in body.interiors)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
                 f'width="{w * 3:.0f}" height="{h * 3:.0f}"><title>{title}</title>'
                 f'<path d="{d}" fill="#2b2b2b" fill-rule="evenodd"/></svg>\n')


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    items = [(c, n) for c in PRESETS for n in PRESETS[c]]
    cols = 6
    fig, axs = plt.subplots(math.ceil(len(items) / cols), cols,
                            figsize=(cols * 3.2, math.ceil(len(items) / cols) * 3.6))
    for ax in axs.ravel():
        ax.axis("off")
    bad = []
    for ax, (c, n) in zip(axs.ravel(), items):
        try:
            body = generate(c, n)
        except ValueError as e:
            bad.append(str(e))
            continue
        svg(body, os.path.join(HERE, "thumbnails", c, n + ".svg"), f"{c} / {n}")
        xs, ys = body.exterior.xy
        ax.fill(xs, ys, color="0.2")
        for i in body.interiors:
            xs, ys = i.xy
            ax.fill(xs, ys, color="white")
        if c == "spirograph":                     # a wheel in the ring, as used
            ring = PRESETS[c][n][1]["ring"]
            w = sa.translate(wheel(WHEELS[0]), (ring - WHEELS[0]) * SPIRO_M / 2, 0)
            xs, ys = w.exterior.xy
            ax.fill(xs, ys, color="tab:orange")
            for i in w.interiors:
                xs, ys = i.xy
                ax.fill(xs, ys, color="white")
        ax.set_xlim(-42, 42)
        ax.set_ylim(-50, 42)
        ax.set_aspect("equal")
        ax.set_title(f"{c} / {n}", fontsize=9)
    for t in WHEELS:
        svg(wheel(t), os.path.join(HERE, "thumbnails", "spirograph", f"wheel-{t}.svg"),
            f"spirograph / wheel {t}")
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "gallery.png"), dpi=60)
    print(len(items), "presets;", "islands:" if bad else "no islands", *bad, sep="\n")


if __name__ == "__main__":
    main()

"""The stencil standard, and originals brought to it (owner: one conformed stencil per kind,
with options, covering many originals -- toward a parametric generator on MakerWorld).

  sheet()        the standard sheet: a SQUARE with CORNER_R corners and a tab on its
                 bottom edge (-y), its width and its position (1 to 5) the two options
                 (TAB_D, TAB_R). Bottom, because lying on the pad the tab sticks out toward
                 the user: every pattern is drawn upright with its foot toward the tab
                 (owner); standing in the holder the tab is up and the pattern upside down
  conformed()    an original's openings brought to the standard: turned so its tab is at
                 the bottom, seen from its smooth face (the bed face, as printed flat;
                 flip/turn for the ones meant to be read from the other side or with no
                 tab), scaled by SQUARE / its own square about its square's centre, and
                 simplified to SIMPLIFY. stencilgen.py takes its fixed shapes this way.
  sheets mode    python conform.py sheets: numbered contact sheets of every distinct
                 pattern in the catalog, conformed, for assessing (sheets/, with
                 index.csv: the numbering library.csv was made against)

The standard (owner): a 76 mm square, a tab on one edge whose width and position (1 to 5)
are the options: five staggered is narrow tabs at 1-5, three is wider ones at 1, 3, 5, one
is position 3 (owner: those are the same thing at different widths, not separate
layouts); the thickness a choice, 1.6 by default (owner: 8 layers of 0.2; their printed
stencils measured 1.66).
"""
import csv
import math
import os
import sys

import numpy as np
import shapely.affinity as sa
import shapely.geometry as sg

import catalog

HERE = os.path.dirname(os.path.abspath(__file__))
SQUARE = 76.0            # the standard sheet: a 3 x 3 inch note
CORNER_R = 3.0           # its corners
# The tab: jorm's (owner: the best looking; [jorm] = sources/makerworld-1409445, measured
# from its blank STEPs): a trapezoid TAB_D deep, its sides TAB_ANGLE off the sheet's edge,
# every corner TAB_R round, convex at the top and concave where it meets the sheet. jorm's
# is 15 across the top (26.75 at the base) at three positions 14.9 apart, the tops just
# meeting. Width here is the top's, the part one grabs; the base follows at TAB_ANGLE.
TAB_W = 11.5             # default: the widest at which five staggered tops stay apart
                         # (11.65); three (1, 3, 5) stay apart to about 19; [jorm] 15.
                         # owner (2026-10-11): fine, seen as a stack of five on the pad and
                         # standing in the holder, the tops meeting edge to edge
POSITIONS = 5
TAB_D = 7.0              # [jorm]
TAB_ANGLE = 50.0         # [jorm] the sides, degrees off the sheet's edge
TAB_R = 3.0              # [jorm] all its corners
SIMPLIFY = 0.05


def tab_base(width: float = TAB_W) -> float:
    """The tab's width where it meets the sheet (its sides run out at TAB_ANGLE)."""
    return width + 2 * TAB_D / math.tan(math.radians(TAB_ANGLE))


def tab_centre(position: int, width: float = TAB_W) -> float:
    """Position 1 to POSITIONS along the tab edge, evenly spaced for a tab of this top
    width, the base of 1 and of the last just clear of the sheet's corner rounding. At
    11.5 wide: about -14.5 apart; at 15, 1, 3 and 5 are -21.6, 0, 21.6."""
    if not 1 <= position <= POSITIONS:
        raise ValueError(f"tab position {position}: 1 to {POSITIONS}")
    span = SQUARE - 2 * CORNER_R - tab_base(width)
    if span < 0:
        raise ValueError(f"tab width {width}: wider than the edge")
    return -span / 2 + span * (position - 1) / (POSITIONS - 1)


def sheet(width: float = TAB_W, position: int = 3):
    """The standard sheet with its tab, as a polygon centred on the origin, the tab on
    the bottom edge."""
    sq = sg.box(-SQUARE / 2, -SQUARE / 2, SQUARE / 2, SQUARE / 2)
    x = tab_centre(position, width)
    edge = -SQUARE / 2
    base, top = tab_base(width) / 2, width / 2
    tab = sg.Polygon([(x - base, edge + 1), (x + base, edge + 1), (x + base, edge),
                      (x + top, edge - TAB_D), (x - top, edge - TAB_D), (x - base, edge)])
    g = sq.union(tab)
    # round every convex corner (the sheet's, the tab's top) then every concave one (the
    # tab's foot)
    g = g.buffer(-CORNER_R, join_style="round").buffer(CORNER_R, join_style="round")
    return g.buffer(TAB_R, join_style="round").buffer(-TAB_R, join_style="round")


def conformed(rel: str, flip: bool = False, turn: int = 0):
    """A library stencil's openings, conformed: a list of polygons in mm on the standard
    square (centre at the origin, tab edge at -y: the bottom, as the user sees it lying on
    the pad with the tab toward them), and the scale applied."""
    mesh = catalog.load_mesh(os.path.join(HERE, rel))
    poly, _, _ = catalog.outline(mesh)
    poly = sa.scale(poly, xfact=-1, yfact=1, origin=(0, 0))      # seen from the smooth face
    side, tab = catalog.square_and_tab(poly)
    x0, y0, x1, y1 = poly.bounds
    edge = tab[0] if tab else None
    # the square's centre: the bounds less the tab
    cx = (x0 + x1) / 2 + {"+x": -1, "-x": 1}.get(edge, 0) * (x1 - x0 - side) / 2
    cy = (y0 + y1) / 2 + {"+y": -1, "-y": 1}.get(edge, 0) * (y1 - y0 - side) / 2
    holes = [sg.Polygon(r) for r in poly.interiors]
    holes = [sa.translate(h, -cx, -cy) for h in holes]
    rot = {"+y": 180, "-y": 0, "+x": -90, "-x": 90, None: 0}[edge] + 90 * turn
    holes = [sa.rotate(h, rot, origin=(0, 0)) for h in holes]
    if flip:
        holes = [sa.scale(h, xfact=-1, yfact=1, origin=(0, 0)) for h in holes]
    k = SQUARE / side
    holes = [sa.scale(h, xfact=k, yfact=k, origin=(0, 0)).simplify(SIMPLIFY) for h in holes]
    return holes, k


def sheets():
    """Numbered contact sheets of every distinct pattern, conform frame, for assessing."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "catalog.csv"), encoding="utf-8"))
            if r["kind"] == "stencil"]
    first = {}
    for r in rows:
        first.setdefault(r["pattern"], r)
    pats = list(first.values())
    out = os.path.join(HERE, "sheets")
    os.makedirs(out, exist_ok=True)
    per = 20
    index = []
    for s0 in range(0, len(pats), per):
        fig, axs = plt.subplots(4, 5, figsize=(20, 17))
        for ax in axs.ravel():
            ax.axis("off")
        for ax, (n, r) in zip(axs.ravel(), enumerate(pats[s0:s0 + per], s0)):
            holes, k = conformed(r["file"])
            body = sheet()
            for g in [body] + holes:
                xs, ys = g.exterior.xy
                ax.fill(xs, ys, color="0.85" if g is body else "0.15")
            ax.set_xlim(-42, 42)
            ax.set_ylim(-50, 42)
            ax.set_aspect("equal")
            same = sum(1 for q in rows if q["pattern"] == r["pattern"])
            ax.set_title(f"#{n}  {r['file'].split('/')[1][11:40]}\n{os.path.basename(r['file'])}"
                         f"  x{same}  s{k:.2f}", fontsize=8)
            index.append((n, r["pattern"], r["file"], same))
        plt.tight_layout()
        plt.savefig(os.path.join(out, f"sheet-{s0 // per + 1}.png"), dpi=45)
        plt.close(fig)
    with open(os.path.join(out, "index.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["n", "pattern", "file", "copies"])
        w.writerows(index)
    print(len(pats), "patterns on", math.ceil(len(pats) / per), "sheets")


if __name__ == "__main__":
    if sys.argv[1:] == ["sheets"]:
        sheets()

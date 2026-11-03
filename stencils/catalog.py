"""Sticky-note stencil library: measures every STL under sources/ and writes catalog.csv,
one row per file, so the collection can be compared, de-duplicated and conformed (owner:
start a library, record where each came from, then analyse, de-dupe and conform size and
tabs).

sources/<origin>/ holds stencils exactly as downloaded (renamed to kebab-case only). They
are other designers' files, most under licences that do not allow redistribution, so they
are not in this repository: sources.csv names each origin folder -- its URL, title,
designer, licence and the download -- for anyone fetching their own copies. catalog.csv
and library.csv were measured from the owner's copies (kept in their private archive,
where each file's full provenance is its row in that archive's MANIFEST.csv).

Measured per file (trimesh, shapely):
  size_x, size_y   the square, without its tab
  thickness        the sheet's: the slices through it at least half as full as the
                   fullest (the outline is taken at the fullest)
  raised           how far anything stands above the sheet (a grip bar), else 0
  tab              which edge it is on (+x, -x, +y, -y, or none, in the file's own
                   axes), its offset: the tab's centre from that edge's middle, seen
                   with the tab at the top from the - side of the plate's thin axis,
                   for a stencil printed flat its smooth bed face (negative is left, as
                   jorm's left-tab blank; turned over, a stencil's sign flips), its width at
                   its base (0.5 out from the square) and how far it sticks out
  openings         the number of cut-outs
  sha256           of the file: identical files
  pattern          a hash of the cut-outs' centres, areas and perimeters relative to the
                   square, rounded to 0.5 mm, 5 mm2 and 0.5 mm (the perimeter tells a round
                   checkbox from a square one of the same area, which centres and areas
                   alone did not), with the tab turned to +x: the same pattern
                   regardless of thickness, export or tab edge
STL and STEP files are measured; a file that is not a flat plate (a source's holder) is
listed with kind = other, a 3mf (a slicer project, its stencils extracted beside it) with
kind = project, and a file holding several stencils with kind = plate (or assembly, if
it holds a holder too; openings then counts its stencils), each extracted beside it.

The owner's target, for conforming: 76 mm square, 1.6 mm thick (owner: 8 layers of 0.2;
their printed stencils measured 1.66),
tabs staggered along the edge so each shows when they stand in the stencil holder
(../bins/postit-stencil-pen-2x4.py).

Run: python catalog.py   (from this folder)
"""
import csv
import glob
import hashlib
import os

import numpy as np
import shapely.geometry as sg
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

def sources() -> dict:
    """sources.csv: one row per origin folder -- its URL, title, designer, licence, what it
    was downloaded as and the download's own record."""
    with open(os.path.join(HERE, "sources.csv"), encoding="utf-8") as fh:
        return {r["folder"]: r for r in csv.DictReader(fh)}


PLATE_MAX_T = 6.0        # thicker than this overall is not a stencil (a sheet with a raised
                         # grip, as Akihiko's, is 4)
LEVELS = 40              # slices through the thickness, to find the sheet


# The plate seen from the + side of its thin axis, as right-handed (u, v): trimesh's own
# to_2D may mirror a part, which flipped tab offsets' signs between files.
VIEW = {2: (0, 1), 1: (2, 0), 0: (1, 2)}


def section_at(mesh, ax, level):
    """The plate's section at level along its thin axis, as a polygon with its cut-outs as
    holes, in (u, v): the plate seen from the + side of that axis."""
    n = np.zeros(3)
    n[ax] = 1
    o = mesh.bounds.mean(axis=0)
    o[ax] = level
    sec = mesh.section(plane_origin=o, plane_normal=n)
    if sec is None:
        return None
    iu, iv = VIEW[ax]
    loops = [sg.Polygon(e[:, [iu, iv]]).buffer(0) for e in sec.discrete if len(e) > 3]
    loops = [lp for lp in loops if lp.area > 0]
    if not loops:
        return None
    loops.sort(key=lambda p: p.area, reverse=True)
    outer = loops[0]
    holes = [p.exterior.coords for p in loops[1:] if outer.contains(p.representative_point())]
    return sg.Polygon(outer.exterior.coords, holes)


def outline(mesh: trimesh.Trimesh):
    """The stencil's sheet: its outline where it has the most material, slicing LEVELS
    times through the thickness (a sheet with a raised grip, cut at mid-height, gave only
    the grip). Returns that outline, the sheet's thickness (the levels at least half as
    full) and how far anything stands above it."""
    ax = int(np.argmin(mesh.extents))
    lo, hi = mesh.bounds[0][ax], mesh.bounds[1][ax]
    step = (hi - lo) / LEVELS
    secs = [section_at(mesh, ax, lo + step * (k + 0.5)) for k in range(LEVELS)]
    areas = [p.area if p is not None else 0.0 for p in secs]
    best = int(np.argmax(areas))
    sheet = sum(1 for a in areas if a >= 0.5 * areas[best]) * step
    return secs[best], sheet, (hi - lo) - sheet


def square_and_tab(poly):
    """Splits the outline into the square and a tab on one edge: the edge whose extent
    across, a little in from it, is much shorter than the plate's is the tab's."""
    x0, y0, x1, y1 = poly.bounds
    w, h = x1 - x0, y1 - y0
    side = min(w, h)
    depth = max(w, h) - side
    best = None
    for edge, (a, b, along) in {"+x": (x1, -1, "y"), "-x": (x0, 1, "y"),
                                "+y": (y1, -1, "x"), "-y": (y0, 1, "x")}.items():
        span = w if along == "x" else h
        if abs((w if along == "y" else h) - side) < 0.5:
            continue                               # this direction has no tab
        probe = a + b * (depth - 0.5)              # just out from the square: the tab's base
        if along == "y":
            line = trimesh.load_path(np.array([[probe, y0 - 1], [probe, y1 + 1]]))
        else:
            line = trimesh.load_path(np.array([[x0 - 1, probe], [x1 + 1, probe]]))
        cut = poly.intersection(sg.LineString(line.vertices))
        if cut.is_empty:
            continue
        lo, hi = (cut.bounds[1], cut.bounds[3]) if along == "y" else (cut.bounds[0], cut.bounds[2])
        if hi - lo < 0.8 * span:
            mid = (y0 + y1) / 2 if along == "y" else (x0 + x1) / 2
            t = (lo + hi) / 2 - mid
            # seen with the tab at the top: turn the plate so its tab's edge is +y; and
            # from the - side of the thin axis (a stencil printed flat: its bed face, the
            # smooth front), which mirrors u
            off = -{"+y": t, "-y": -t, "+x": -t, "-x": t}[edge]
            best = (edge, off + 0.0, hi - lo, depth)
    return side, best


def pattern(poly, tab_edge):
    """A fingerprint of the cut-outs: centres relative to the square's centre and areas,
    rounded, with the tab's edge turned to +x."""
    x0, y0, x1, y1 = poly.bounds
    w, h = x1 - x0, y1 - y0
    cx = x0 + min(w, h) / 2 if tab_edge == "+x" else x1 - min(w, h) / 2 if tab_edge == "-x" \
        else (x0 + x1) / 2
    cy = y0 + min(w, h) / 2 if tab_edge == "+y" else y1 - min(w, h) / 2 if tab_edge == "-y" \
        else (y0 + y1) / 2
    turn = {"+x": 0, None: 0, "+y": -90, "-x": 180, "-y": 90}[tab_edge]
    c, s = np.cos(np.radians(turn)), np.sin(np.radians(turn))
    keys = []
    for ring in poly.interiors:
        hole = sg.Polygon(ring)
        px, py = hole.centroid.x - cx, hole.centroid.y - cy
        rx, ry = c * px - s * py, s * px + c * py
        keys.append((round(rx * 2) / 2, round(ry * 2) / 2, round(hole.area / 5) * 5,
                     round(hole.length * 2) / 2))
    keys.sort()
    return hashlib.sha256(repr(keys).encode()).hexdigest()[:12]


def load_mesh(f: str) -> trimesh.Trimesh:
    """An STL, or a STEP tessellated finely (CadQuery)."""
    if not f.endswith(".step"):
        return trimesh.load(f)
    import tempfile
    import cadquery as cq
    shape = cq.importers.importStep(f)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "t.stl")
        cq.exporters.export(shape, out, tolerance=0.01, angularTolerance=0.1)
        return trimesh.load(out)


def main():
    global SOURCES
    SOURCES = sources()
    rows = []
    files = sorted(f for ext in ("stl", "step", "3mf")
                   for f in glob.glob(os.path.join(HERE, "sources", "*", "*." + ext)))
    for f in files:
        rel = os.path.relpath(f, HERE).replace(os.sep, "/")
        origin = rel.split("/")[1]
        sha = hashlib.sha256(open(f, "rb").read()).hexdigest()
        src = SOURCES.get(origin, {})
        row = {"file": rel, "origin": src.get("url") or src.get("title") or origin,
               "sha256": sha}
        if f.endswith(".3mf"):
            row.update(kind="project")
            rows.append(row)
            continue
        mesh = load_mesh(f)
        big = [p for p in mesh.split(only_watertight=False) if sorted(p.extents)[1] >= 60]
        flat = [p for p in big if p.extents.min() <= PLATE_MAX_T]
        if len(flat) > 1 or (flat and len(big) > len(flat)):
            # several stencils on one plate, or stencils in an assembly: each is extracted
            # beside it (-stencil-N) and measured there
            row.update(kind="plate" if len(big) == len(flat) else "assembly",
                       openings=len(flat))
            rows.append(row)
            continue
        if mesh.extents.min() > PLATE_MAX_T:
            row.update(kind="other")
            rows.append(row)
            continue
        poly, t, raised = outline(mesh)
        side, tab = square_and_tab(poly)
        edge = tab[0] if tab else None
        row.update(kind="stencil", size=round(side, 2), thickness=round(t, 2),
                   raised=round(raised, 1) if raised > 0.2 else 0,
                   tab_edge=edge or "none",
                   tab_offset=round(tab[1], 1) + 0.0 if tab else "", tab_width=round(tab[2], 1) if tab else "",
                   tab_depth=round(tab[3], 1) if tab else "",
                   openings=len(poly.interiors), pattern=pattern(poly, edge))
        rows.append(row)
    # duplicates: same file, or the same pattern
    for r in rows:
        same = [o["file"] for o in rows if o is not r and r["kind"] == "stencil" and
                (o["sha256"] == r["sha256"] or o.get("pattern") == r.get("pattern"))]
        r["duplicates"] = " ".join(same)
    cols = ["file", "kind", "size", "thickness", "raised", "tab_edge", "tab_offset", "tab_width",
            "tab_depth", "openings", "pattern", "duplicates", "sha256", "origin"]
    with open(os.path.join(HERE, "catalog.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})
    for r in rows:
        print({k: r.get(k, "") for k in cols if k not in ("sha256", "origin")})


if __name__ == "__main__":
    main()

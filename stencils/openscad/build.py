"""Builds and checks the OpenSCAD stencil generators.

  dist/<generator>.scad   each generator with stencil-common.scad inlined: one file each,
                          as MakerWorld's Parametric Model Maker takes (upload these)
  shapes                  stencil-shapes.scad's SHAPES, written from the prototype's
                          shapes (stencilgen.shape: drawn there from scratch) at full size
  check                   every preset (or a settings generator's CHECKS) rendered flat by OpenSCAD and compared with the
                          Python prototype's outline (../stencilgen.py): the area that
                          differs, as a share of the stencil's (TOLERANCE; the week's day
                          letters LETTERS_TOLERANCE: OpenSCAD's Liberation Sans is not the
                          prototype's DejaVu Sans); the spirograph's ring and every wheel;
                          and the default rendered as a part, checked to be watertight

OpenSCAD: the nightly (installed 2026-10-11 to C:/Program Files/OpenSCAD (Nightly)), with
the Manifold backend, as MakerWorld runs a recent build.

Run: python build.py
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

import shapely.affinity as sa
import shapely.geometry as sg
import shapely.ops as so
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stencilgen  # noqa: E402

OPENSCAD = r"C:\Program Files\OpenSCAD (Nightly)\openscad.com"
TOLERANCE = 0.002        # a share of the stencil's area that may differ (facets, $fn)
LETTERS_TOLERANCE = 0.02 # with lettering in another font


def inline(path):
    s = open(path, encoding="utf-8").read()
    common = open(os.path.join(HERE, "stencil-common.scad"), encoding="utf-8").read()
    return s.replace("include <stencil-common.scad>",
                     "// --- stencil-common.scad, inlined by build.py ---\n" + common)


def run(scad, out, defines):
    args = [OPENSCAD, "--backend=manifold", "-o", out]
    for k, v in defines.items():
        args += ["-D", f"{k}={v}"]
    r = subprocess.run(args + [scad], capture_output=True, text=True)
    if r.returncode or not os.path.exists(out):
        raise RuntimeError(r.stderr[-2000:])


def svg_polygon(path):
    """OpenSCAD's 2D SVG back to a polygon: its paths' rings, even-odd (y flipped back)."""
    d = " ".join(re.findall(r' d="([^"]+)"', open(path, encoding="utf-8").read()))
    rings = []
    for sub in re.split(r"[Mm]", d):
        pts = [tuple(map(float, p)) for p in re.findall(r"(-?[\d.]+)[ ,](-?[\d.]+)", sub)]
        if len(pts) > 2:
            rings.append(sg.Polygon([(x, -y) for x, y in pts]).buffer(0))
    rings.sort(key=lambda p: p.area, reverse=True)
    g = rings[0]
    for r in rings[1:]:
        g = g.symmetric_difference(r)
    return g


CHECK_FIELDS = ["rows", "left_box", "right_box", "columns", "large_boxes",
                "title", "grouped"]


def settings_checks(path):
    """A settings-based generator's CHECKS: rows of [prototype cat-name, then its settings
    in CHECK_FIELDS order], as -D defines (strings stay quoted)."""
    s = open(path, encoding="utf-8").read()
    if "CHECKS = [" not in s:
        return None
    block = s[s.index("CHECKS = ["):]
    block = block[:block.index("];")]
    out = []
    for row in re.findall(r'^\s*\[(".*)\],\s*$', block, re.M):
        vals = [v.strip() for v in row.split(",")]
        out.append((vals[0].strip('"'), dict(zip(CHECK_FIELDS, vals[1:]))))
    return out


def presets(path):
    """The generator's presets: the ids its PRESETS / SHAPES list, or its check preset."""
    s = open(path, encoding="utf-8").read()
    ids = re.findall(r'^\s*\["([a-z0-9_-]+)", ', s, re.M)
    return ids or re.findall(r'^preset = "([a-z0-9_-]+)";', s, re.M)


def reference(pid):
    """The prototype preset a generator's id stands for: cat_name, or a name that already
    starts with its category (week_labelled). The generators' ids use underscores:
    MakerWorld's customiser failed files whose dropdown values had hyphens."""
    pid = pid.replace("_", "-")
    for cat, names in stencilgen.PRESETS.items():
        for name in names:
            if pid in (f"{cat}-{name}", name) and pid.startswith(cat):
                return cat, name
    raise KeyError(pid)


def write_shapes():
    """stencil-shapes.scad's SHAPES from the prototype's shapes, between its markers."""
    path = os.path.join(HERE, "stencil-shapes.scad")
    s = open(path, encoding="utf-8").read()
    rows = []
    for name in stencilgen.PRESETS["shapes"]:
        polys = []
        for g in stencilgen.shape(name):
            for q in (g.geoms if hasattr(g, "geoms") else [g]):
                assert not q.interiors, name
                polys.append("[" + ", ".join(f"[{x:.3f}, {y:.3f}]"
                                             for x, y in list(q.exterior.coords)[:-1]) + "]")
        rows.append(f'    ["shapes_{name.replace("-", "_")}", [{", ".join(polys)}]],')
    a = s.index("// --- shapes: build.py writes between these lines ---")
    b = s.index("// --- end of shapes ---")
    s = (s[:a] + "// --- shapes: build.py writes between these lines ---\nSHAPES = [\n"
         + "\n".join(rows) + "\n];\n" + s[b:])
    open(path, "w", encoding="utf-8", newline="\n").write(s)


def main():
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    write_shapes()
    bad = 0
    for gen in sorted(glob.glob(os.path.join(HERE, "stencil-*.scad"))):
        name = os.path.basename(gen)
        if name == "stencil-common.scad":
            continue
        dist = os.path.join(HERE, "dist", name)
        open(dist, "w", encoding="utf-8", newline="\n").write(inline(gen))
        print("==", name, "->", os.path.relpath(dist, HERE))
        with tempfile.TemporaryDirectory() as tmp:
            settings = settings_checks(gen)
            if settings is not None:
                checks = [(p, d, stencilgen.generate(*reference(p))) for p, d in settings]
            else:
                checks = [(p, {"preset": f'"{p}"', "part": '"ring"'},
                           stencilgen.generate(*reference(p))) for p in presets(gen)]
            if name == "stencil-spirograph.scad":
                checks += [(f"wheel-{t}", {"part": '"wheel"', "wheel_teeth": t},
                            stencilgen.wheel(t)) for t in stencilgen.WHEELS]
            for label, defines, ref in checks:
                out = os.path.join(tmp, label + ".svg")
                run(dist, out, dict(defines, flat="true"))
                mine = svg_polygon(out)
                diff = mine.symmetric_difference(ref).area / ref.area
                tol = LETTERS_TOLERANCE if label == "week_labelled" else TOLERANCE
                ok = diff <= tol
                bad += not ok
                print(f"   {'ok ' if ok else 'BAD'} {label:34s} differs {diff:.4%}"
                      f"{' (letters: other font)' if tol != TOLERANCE else ''}"
                      f"{'' if mine.geom_type == 'Polygon' else '  (not one piece!)'}")
            stl = os.path.join(tmp, "default.stl")
            run(dist, stl, {})
            m = trimesh.load(stl)
            print(f"   part: watertight {m.is_watertight}, bodies {len(m.split())}, "
                  f"extents {[round(v, 2) for v in m.extents]}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

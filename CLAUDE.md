# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

StickyNoteStencils: printable stencils for 3 x 3 inch sticky notes, written as OpenSCAD
customizers for MakerWorld, and CadQuery Gridfinity bins to hold the pad, stencils and
pens. **This repository is public.** Each part's design record is the comment block at the
top of its source, which says why every dimension is what it is. Owner feedback and test
prints are tagged `owner:`, with the value they replaced, so a value is not "fixed" back.

Developed in TrianonPlaza/Printing as `gridfinity/postit-stencil-pen-2x4` and moved here
2026-11-03 to be published. That repo's CLAUDE.md has the wider lessons on authored
models; the ones that bear on these parts are repeated below.

## Third-party files stay out

`stencils/sources/` (other designers' MakerWorld stencils, measured by `catalog.py`) and
`bins/1x1-block-refined.step` (the Gridfinity Refined foot the bins import) are
gitignored. Most of the stencils are under MakerWorld's Standard Digital File License,
which does not allow redistribution, and the rest have no known licence. The owner's copies
live in TrianonPlaza/Printing under `gridfinity/sticky-note-stencil-references/`. Never
commit them here, or anything extracted from them (meshes, renders). Measurements
(`catalog.csv`, `library.csv`) and links (`sources.csv`) are fine.

## Toolchain

- **OpenSCAD nightly**, Manifold backend:
  `C:\Program Files\OpenSCAD (Nightly)\openscad.com`, `-D name=value` to override.
  winget's nightly entry pointed at a removed build; take the newest installer from
  files.openscad.org/snapshots and check its published sha256.
- **`python stencils/openscad/build.py`** writes `dist/` (each generator with
  `stencil-common.scad` inlined) and compares every preset's outline with the Python
  prototype (`stencils/stencilgen.py`). Keep the two in step: change both. Upload `dist/`.
- **CadQuery 2.8** for `bins/`, from a throwaway venv (`pip install cadquery`, and
  `trimesh`, `shapely`, `matplotlib` for checks and thumbnails).
- `.gitattributes` stores `.py` and `.scad` as LF; write them with LF.

## MakerWorld's Parametric Model Maker

- One `.scad` per generator; shared code is inlined by `build.py`.
- Its upload check validates the customizer parameters, not the model: a file whose
  `include` was missing still passed.
- It failed every file whose dropdown *values* had hyphens, and passed them with
  underscores. Keep labels to plain words, no `-`, `,` or `:` (2026-10-11).
- No dependent dropdowns: split a family of options into several generators.
- Its dropdown shows about five entries with no visible scrollbar (owner, 2026-11-03): the
  week presets, sixth and seventh in their list, looked missing. Put the options people
  look for first, or say in the parameter's description that the list scrolls.

## Gridfinity

Working numbers, checked by sectioning a rebuilt standard bin: 42 pitch, bins 0.5 under
it, height in 7 mm units with the feet included, corners 3.75. A foot from the bed: 0.8
at 45 degrees, 1.8 straight, 2.15 at 45 (4.75). The stacking lip from the body's top: in
0.7 at 45, 1.8 straight, out 1.9 at 45, cut flat 3.55 up. A stacked bin's feet go 0.35
below the rim, so a pocket must be at least the lip's foot (inset 2.6) across near the
top. The lip's opening in a one-cell-wide bin is 36.3. Magnets: Gridfinity Refined
side-loading slots, from the STEP remake (see `bins/postit-stencil-pen-2x4.py`); each slot
counts as a through-hole in `euler_number`.

## Owner's preferences and checks

- Export STLs in print orientation; no supports; downward faces at 45 degrees or less.
- Holes print small on the owner's printer (A1 mini).
- Settle a part's shape with the owner, with a preview, before adding decoration; never
  silently swap a feature the owner described.
- Make features meet exactly; offset only when a check fails, and say why.
- Before handing over: one watertight body per part, `euler_number` as expected, no
  floating regions (slice every layer; do not skip tiny starts), slivers found by opening
  each section by the nozzle width (`buffer(-0.2).buffer(0.2)`).
- A clearance check on a mechanism (a wheel in a ring, a stencil in a slot) needs a
  positive control: push it past its fit and see the overlap before trusting a zero.

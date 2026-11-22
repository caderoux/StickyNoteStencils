# StickyNoteStencils

3D-printable stencils for 3 x 3 inch (76 mm) sticky notes, and a set of Gridfinity bins to
keep the pad, the stencils and your pens on the desk.

> **Status:** prototypes, being test-printed. Expect changes.

## Stencils

Lay a stencil on the pad and draw through it: checklists, ruled lines, planners, a week,
dot grids, shapes to trace round, and a spirograph. Every stencil is a 76 mm square, 1.6
mm thick, with a tab on the edge toward you. Give each stencil in a set a different tab
position (1 to 5), and all the tabs stay visible when they are stacked or stand in the
holder.

The generators are OpenSCAD customizers, written for MakerWorld's Parametric Model Maker:

| Generator | Makes |
|---|---|
| `stencils/openscad/stencil-lines-checklists.scad` | Ruled lines, and checklists with a square, circle, triangle or heart box at either end, with an optional title bar |
| `stencils/openscad/stencil-planner-week-grid.scad` | Planners (quadrants, focus, pros and cons, two columns, two rows), a seven-day week with a notes cell, and dot grids |
| `stencils/openscad/stencil-shapes.scad` | Shapes to trace: arrow, circle, cloud, ellipse, heart, lightbulb, rounded square, speech bubble, star |
| `stencils/openscad/stencil-spirograph.scad` | A ring stencil with teeth inside and toothed wheels that roll round in it, a pen in one of their holes |

MakerWorld takes one file per generator, so upload the copies in `stencils/openscad/dist/`,
which have the shared `stencil-common.scad` inlined. To change a generator, edit the file
in `stencils/openscad/` and run `python stencils/openscad/build.py`. It rebuilds `dist/`,
renders every preset and compares it with the Python prototype (`stencils/stencilgen.py`),
which also draws the thumbnails in `stencils/thumbnails/` and `stencils/gallery.png`.

Build with the OpenSCAD nightly (the Manifold backend). The 2021.01 release is too old.

## Gridfinity bins

`bins/postit-stencil-pen-2x4.py` (CadQuery) makes four bins. The first three fill a 2 x 4
Gridfinity space; the fourth takes the stencil holder's place in it, or stands beside the set:

- **postit-tray-2x2**: holds the pad, open at the front so a stencil lying on it can hang
  its tab out over the edge.
- **stencil-holder-1x2**: ten stencils standing on edge in slots, lifted out by their tabs.
- **pen-holder-1x2**: four marker holes and six pen holes.
- **spirograph-holder-1x2**: the spirograph's ring and four wheels on one side, seven
  stencils in slots on the other. Not yet test-printed.

Each has the stacking lip and Gridfinity Refined feet, with side-loading slots for 6 x 2
mm magnets. The STLs are in print orientation and need no supports.

To rebuild them you need `1x1-block-refined.step` in `bins/`, from
[Gridfinity Refined Base STP/STEP files](https://www.printables.com/model/971527-gridfinity-refined-base-stpstep-files)
by Kytor, a remake of grizzie17's
[Gridfinity Refined](https://www.printables.com/model/413761-gridfinity-refined). That file
is not included here, but the bins' feet are cut from it, so the bins share its CC BY-SA 4.0
licence.

## Where the patterns came from

The stencils began as a survey of the sticky-note stencils on MakerWorld:
`stencils/catalog.py` measured them all, and `stencils/library.csv` maps each one to the
preset here that comes closest to it. The patterns here were drawn from scratch. The tab
follows jorm's angled tab ([MakerWorld 1409445](https://makerworld.com/en/models/1409445-sticky-note-holder-with-stencils)),
measured, not copied.

The originals belong to their designers and are not in this repository.
`stencils/sources.csv` lists each one with its link, designer and licence. To run the
catalog yourself, download them into `stencils/sources/<folder>/`.

## Licence

- **Code** (`.py`, `.scad`): MIT.
- **Gridfinity bins** (the STL, STEP and 3MF files in `bins/`):
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), adapted from Kytor's
  Gridfinity Refined base. If you share them or a remix of them, credit both and keep that
  licence.
- **Everything else made here** (the stencils and images):
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

`LICENSE` has the details and the credits.

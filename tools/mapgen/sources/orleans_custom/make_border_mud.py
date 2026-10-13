"""Swamp canopy onto MUD (ekat:mud_C, the Orleans mud ground of Isle Marais and the levee flats), 2026-10-13. For review, not integrated.

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/make_border_mud.py

The S/N/E/W faces (both parities), the four inner corners and the four outer corners of the swamp canopy wall over mud_C, drawn by
make_borders.edge_cell / outer_cell exactly like the marsh and water sets (mud shading added to make_borders.shade_map: the
canopy's cast shadow on mud steps 160,128,120 -> 144,104,96 -> 112,80,80 -> 96,64,64, all Ekat mud colours).

writes  tools/mapgen/tilesets/borders/bk_swamp_<face><parity>_<sha1('ekat:mud_C')[:8]>.png, i.e. the names borders.bake() gives a
        swamp edge cell baked over ekat:mud_C (faces S0 S1 N0 N1 E0 E1 W0 W1, in_NW in_NE in_SW in_SE, out_NW out_NE out_SW out_SE),
        and mud.json indexing them. NB feather.canon('swamp', 'L') turns mud under an edge cell into grass today; the rollout keeps
        'L' (and 'S', the churchyard mud) as mud to use these.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_borders as mb  # noqa: E402

UNDER = "ekat:mud_C"
H8 = hashlib.sha1(UNDER.encode()).hexdigest()[:8]
OUT_DIR = os.path.join(mb.MAPGEN, "tilesets", "borders")
FACES = mb.FACE_ORDER + [(c, None) for c in mb.OUTER_ORDER]


def file_id(face, par):
    return f"bk_swamp_{face}{'' if par is None else par}_{H8}"


def build(g=None):
    g = g or mb.ground_cells()
    out = {}
    for face, par in FACES:
        if face in mb.OUTER:
            out[(face, par)] = mb.outer_cell("swamp", face, g["mud_C"], g)[0]
        else:
            out[(face, par)] = mb.edge_cell("swamp", face, par, g["mud_C"], g)[0]
    return out, g


def main(argv):
    cells, g = build()
    index = {}
    for (face, par), img in cells.items():
        fid = file_id(face, par)
        img.save(os.path.join(OUT_DIR, fid + ".png"))
        index[fid] = {"style": "swamp", "face": face, "parity": par, "under": UNDER}
    json.dump({"_comment": "Swamp canopy faces / inner / outer corners baked over ekat:mud_C (make_border_mud.py); names as "
                           "borders.bake() gives them.", "cells": index},
              open(os.path.join(OUT_DIR, "mud.json"), "w"), indent=1)
    print(f"wrote {len(index)} mud cells to {os.path.relpath(OUT_DIR, mb.ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])

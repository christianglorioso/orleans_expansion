"""OUTER (convex) corner cells for the border walls of the feather pass (feather.py), 2026-10-13.

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/make_border_corners.py [--sheet]

The art is make_borders.outer_cell (its OUTER docstring): the cell diagonal to a wall's convex corner, showing the overhang that
crosses in from the two face cells beside it plus one corner clump of the corner tree, so the canopy rounds off instead of
leaving a square notch. Drawn with the very renderer, layouts and palettes of the S/N/E/W edge cells (make_borders.py).

writes  tools/mapgen/tilesets/borders/<prefix>_<style>_out_<C>_<sha1(under)[:8]>.png   one 16x16 cell per corner and ground,
        named exactly as borders.bake() names a baked edge cell (face "out_NW" ..., no parity), so once the feather pass hands
        its missing corners to borders.bake (face = the corner name) it finds these files and uses them as the cell's pixels:
            swamp on marsh   bk_swamp_out_*_f819ccaa   (under ekat:marsh_C)
            swamp on water   bk_swamp_out_*_5181453c   (under ekat:water_C)
            swamp on grass   bdg_swamp_out_*_542aa1ca  (under ekat:grass; bdg_ = the primary's, like the bdg_ face cells)
            dry on sand      bk_dry_out_*_2cfd7b76     (under dry:0_0, the pale dry ground 'd')
            dry on red earth bk_dry_out_*_<h(dry:0_14)> (under dry:0_14, 'e')
        any other ground (a bank, a blend) is baked by make_borders.bake_edge(style, "out_NW", None, base16) like a face cell.
        corners.json beside them indexes the files.
--sheet also writes the review sheet (tile_review/art_edge_corners.png) via border_corners_review.py.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_borders as mb  # noqa: E402

MAPGEN = mb.MAPGEN
OUT_DIR = os.path.join(MAPGEN, "tilesets", "borders")

# (style, ground label, ground cell key in make_borders.ground_cells / extra, the metatile name borders.edge_base reports, prefix)
GROUNDS = [
    ("swamp", "marsh", "marsh_C", "ekat:marsh_C", "bk"),
    ("swamp", "water", "water_C", "ekat:water_C", "bk"),
    ("swamp", "town grass", "grass", "ekat:grass", "bdg"),
    ("dry", "sand (dry ground d)", "dry", "dry:0_0", "bk"),
    ("dry", "red earth (e)", "red_earth", "dry:0_14", "bk"),
]


def grounds():
    g = mb.ground_cells()
    from PIL import Image
    dj = json.load(open(os.path.join(HERE, "dry_country.json")))
    dry = Image.open(os.path.join(HERE, "dry_country.png")).convert("RGB")
    x, y = dj["terrain"]["red_earth"][0]
    g["red_earth"] = dry.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16))
    return g


def file_id(style, corner, under, prefix):
    return f"{prefix}_{style}_{corner}_" + hashlib.sha1(under.encode()).hexdigest()[:8]


def build(g=None):
    """{(style, ground label): {corner: PIL image}}, and the file index"""
    g = g or grounds()
    cells, index = {}, {}
    for style, label, key, under, prefix in GROUNDS:
        row = {}
        for corner in mb.OUTER_ORDER:
            img, info = mb.outer_cell(style, corner, g[key], g)
            row[corner] = img
            index[file_id(style, corner, under, prefix)] = {"style": style, "corner": corner, "ground": label, "under": under}
        cells[(style, label)] = row
    return cells, index, g


def main(argv):
    cells, index, g = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    by_id = {}
    for style, label, key, under, prefix in GROUNDS:
        for corner, img in cells[(style, label)].items():
            fid = file_id(style, corner, under, prefix)
            img.save(os.path.join(OUT_DIR, fid + ".png"))
            by_id[fid] = index[fid]
    with open(os.path.join(OUT_DIR, "corners.json"), "w", encoding="utf-8") as f:
        json.dump({"_comment": "Outer (convex) corner cells of the border walls (make_border_corners.py). File = <id>.png, named "
                               "as borders.bake() names a baked edge cell with face = the corner (out_NW: the wall is NW "
                               "of the cell, the cell sits at parity (0, 0); out_NE (1, 0); out_SW (0, 1); out_SE (1, 1)).",
                   "cells": by_id}, f, indent=1)
    print(f"wrote {len(by_id)} corner cells to {os.path.relpath(OUT_DIR, mb.ROOT)}")
    if "--sheet" in argv:
        import border_corners_review
        border_corners_review.main([])


if __name__ == "__main__":
    main(sys.argv[1:])

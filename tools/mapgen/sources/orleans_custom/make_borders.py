"""Map BORDER art: the 2x2 border blocks the engine repeats past every unconnected map edge, plus the wall-transition
cells that let an inward wall of the same canopy meet the map's own terrain. Drawn here in Python (no source tiles).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_borders.py
writes
    sources/orleans_custom/borders.png    16 px cells, all opaque; magenta = unused (borders.json names every cell)
    sources/orleans_custom/borders.json   {"png", "palettes", "blocks", "cells": {name: [x, y]}, "edges", "rules"}
    maps/00_borders_art.png               the review sheet: blocks tiled 6x4, mock map edges at 3x, the swamp and
                                          dry borders side by side, tile and colour counts

The two border blocks (2x2 cells each; the engine draws border[(x & 1) + (y & 1) * 2] at map cell (x, y)):
    swamp_canopy   dense bald-cypress / tupelo / water-oak canopy seen from above. Only colours of the core green
                   palette (Ekat grass + marsh + water + cypress greens: orleans_route_b/10 = orleans_village/07 =
                   orleans_pointe/06), so it shares that palette (in the primary once tier 1 moves there) for free.
    dry_scrub      live oaks and scrub thickets, crowns overlapping, small gaps of dry[0] earth and straw tufts.
                   No rocks in the block (a stone would repeat every 32 px): the edge cells and inner corners carry
                   a few stones (DRY_EDGE_ROCKS). Only make_dry_country.py's colours (earth, straw, leaf greens
                   L0-L4, rock greys K0-K2, outline B0): its own 15-colour palette.
Both are drawn the same way, so they read as one world: crowns of leaf clumps lit from the top-left, taller crowns
over lower ones (each tree has a height) casting a hard shadow to the bottom-right onto the crowns and ground below,
a dark outline round every crown, a dark seam on each clump's lower rim. The cypress is one dome of drooping 2 px
sprays like Ekat's crown, the hardwoods and oaks are scalloped clumps like make_dry_country's trees. Everything is
laid out on a 32 px torus (clumps wrap), so the block has no seam or line on its 32 px grid.

Inward wall: the wall IS the block, placed by map parity like the border (wall cell (x, y) = block[y & 1][x & 1]),
so it runs into the border with no seam. The wall-transition cells sit in the first terrain cell beside the wall:
the wall's own trees hanging out over that terrain (each tree touching the wall keeps its clumps, up to 10 px out;
other trees are gone), with their outline and a deep contact shade + cast shadow on the ground. They join the wall
pixel-exactly. The block is 32 px, so every face has an edge cell for both parities along the edge (_0 / _1 =
x & 1 for faces S/N, y & 1 for E/W), and the wall's inner face sits on a fixed parity. With d = the wall's depth in
cells (0 = no inward wall, the border itself is the wall):
    face S  wall on the map's NORTH edge, terrain south of it: edge cell row y = d, d EVEN (0, 2, 4)
    face E  wall on the WEST edge, terrain east of it:         edge cell column x = d, d EVEN (0, 2, 4)
    face N  wall on the SOUTH edge, terrain north of it:       the wall's first row h - d EVEN (edge row h - d - 1)
    face W  wall on the EAST edge, terrain west of it:         the wall's first column w - d EVEN (edge col w - d - 1)
    in_NW in_NE in_SW in_SE   the inner corner where two walls meet (canopy on the two named sides); its cell's
                              parity (x & 1, y & 1) is then NW (0,0), NE (1,0), SW (0,1), SE (1,1)
Terrains baked here: swamp on Ekat marsh_C and water_C, dry on dry[0]. bake_edge(style, face, parity, base16)
bakes any edge cell on another 16x16 ground cell (e.g. a marsh-water bank cell where a wall crosses a shore).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
P = 32  # the block's period

# ---------------------------------------------------------------- colours
# SWAMP: the core green palette (orleans_route_b/10 = orleans_village/07 = orleans_pointe/06), slot 0 transparent.
CORE_PAL = [(120, 160, 104), (120, 160, 104), (96, 136, 136), (120, 168, 128), (136, 176, 128), (96, 128, 88),
            (144, 184, 152), (40, 56, 40), (64, 96, 64), (72, 96, 64), (80, 112, 96), (80, 80, 80),
            (104, 152, 120), (72, 112, 112), (104, 144, 96)]
S_OUT = (40, 56, 40)                                      # Ekat cypress outline / the canopy's deep shade
C_DK, C_MID, C_HL = (64, 96, 64), (80, 112, 96), (104, 152, 120)   # Ekat cypress crown (blue-green)
O_DK, O_MID, O_HL = (72, 96, 64), (96, 128, 88), (104, 144, 96)    # tupelo / water oak (olive), marsh rims
O_TIP = (120, 160, 104)                                   # sunlit crest (the grass colour)
C_TIP = (144, 184, 152)                                   # cypress sunlit crest (marsh light)
# DRY: make_dry_country.py's colours (all already in OrleansRouteDry / OrleansRouteFarm palettes)
DH, D1, D2, D3 = (240, 224, 184), (224, 200, 144), (200, 168, 112), (160, 128, 88)
ST, ST_D = (216, 184, 88), (176, 144, 64)
L0, L1, L2, L3, L4 = (24, 48, 32), (40, 80, 48), (64, 112, 56), (96, 144, 64), (152, 184, 88)
K0, K1, K2 = (104, 96, 80), (152, 144, 120), (200, 192, 168)
B0 = (64, 40, 32)
DRY_PAL = [(120, 160, 104), DH, D1, D2, D3, ST, ST_D, L0, L1, L2, L3, L4, K0, K1, K2, B0]   # slot 0 transparent

KEY = (255, 0, 255)


def _hash(x, y, k=0):
    """Repeatable noise in [0, 1)."""
    n = (x * 374761393 + y * 668265263 + k * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


# ---------------------------------------------------------------- the clump layouts (hand placed, 32 px torus)
# A layout is a list of trees: (species, bias, [(cx, cy, rx, ry, clump bias), ...]). A tree is shaded as one dome
# (lit top-left) and each clump on it as a small dome; bias brightens (+) or sinks (-) a whole tree or one clump.
# Every clump keeps rx <= 7 and ry <= 6 so a wall's overhang always fits in the one edge cell.
SWAMP = [
    ("c", 0.0, [(6, 1.5, 5, 3.5, 0), (13.5, 1.5, 5, 3.5, 0), (2, 5.5, 4.5, 4, 0), (9.5, 5, 6, 4.5, 0),
                (17, 5.5, 4.5, 4, 0), (1.5, 10, 3.5, 4, 0), (6.5, 10, 6, 5, 0), (13.5, 10, 6, 5, 0), (19, 10, 3.5, 4, 0),
                (3, 14.5, 5, 4, 0), (10, 15, 6, 4.5, 0), (16.5, 14.5, 4.5, 4, 0), (9.5, 18.5, 5, 3, 0)]),  # bald cypress
    ("c", 0.1, [(24, -1, 4.5, 3.5, 0), (30, -1, 4.5, 3.5, 0), (22, 3.5, 4.5, 4, 0), (27.5, 3.5, 6, 4.5, 0),
                (33, 4, 4, 4, 0), (24, 8.5, 5, 4, 0), (30.5, 8.5, 5, 4, 0), (27, 12, 5, 3, 0)]),       # a younger cypress
    ("o", 0.0, [(23, 15.5, 5, 3.5, 0.05), (29, 15.5, 5, 3.5, 0), (19.5, 19.5, 5, 4, 0), (26, 19, 6, 4.5, 0.05),
                (32.5, 19.5, 4.5, 4, 0), (18.5, 24.5, 4.5, 4, -0.05), (25, 24, 6.5, 4.5, 0), (32, 24.5, 5, 4.5, 0),
                (21.5, 29, 5, 4, -0.05), (28.5, 29, 5.5, 4, 0)]),                              # a tupelo
    ("o", 0.1, [(4, 21.5, 5, 3.5, 0.05), (10.5, 21.5, 5, 3.5, 0), (1, 25.5, 4.5, 4, 0), (7.5, 25.5, 6, 4.5, 0.05),
                (14, 26, 4, 3.5, 0), (4, 30, 5, 3.5, -0.05), (11, 30, 5, 3.5, 0)]),                # a water oak
    ("o", -0.35, [(17.5, 18.5, 3, 2.5, 0)]),                                                    # under-storey
]

DRY = [
    ("l", 0.05, [(6, 2.5, 4.5, 3, 0.05), (12, 2.5, 4.5, 3, 0), (3, 6.5, 4, 3.5, 0), (9, 6, 5.5, 4, 0.05),
                 (15, 6.5, 4, 3.5, 0), (5, 11, 5, 3.5, 0), (12.5, 11, 5, 3.5, 0), (9, 14, 4.5, 2.5, -0.05), (2.5, 14.5, 3.5, 2.5, -0.05),
                 (15.5, 15, 3.5, 2.5, -0.05)]),                                                         # live oak
    ("l", 0.0, [(22, 16.5, 4.5, 3, 0.05), (28, 16.5, 4.5, 3, 0), (19, 20.5, 4, 3.5, 0), (25, 20, 5.5, 4, 0.05),
                (31, 20.5, 4, 3.5, 0), (21, 25, 5, 3.5, 0), (28.5, 25, 5, 3.5, 0), (25, 28, 4.5, 2.5, -0.05), (19.5, 29, 3.5, 2.5, -0.05),
                (30.5, 29, 3.5, 2.5, -0.05)]),                                                          # live oak
    ("s", 0.05, [(24, 3.5, 4.5, 3.5, 0.05), (29.5, 2.5, 4, 3, 0), (20, 7, 3.5, 3, 0), (27, 8, 5, 3.5, 0),
                 (22.5, 11, 4, 3, -0.05), (31.5, 10, 3.5, 3, 0), (28, 13, 3.5, 2.5, -0.05)]),                # scrub thicket
    ("s", 0.0, [(4, 19.5, 4.5, 3.5, 0.05), (9.5, 20.5, 4, 3, 0), (1.5, 24.5, 4, 3.5, 0), (7.5, 25, 5, 3.5, 0),
                (12.5, 26.5, 4, 3, -0.05), (4.5, 29.5, 4.5, 2.5, 0), (10.5, 30.5, 3.5, 2.5, -0.05)]),         # scrub thicket
    ("s", 0.1, [(16.5, 12, 3.5, 3, 0.05), (19.5, 14.5, 3, 2.5, 0)]),                                         # scrub
    ("s", -0.05, [(15.5, 21.5, 3, 2.5, 0), (16.5, 29, 3.5, 2.5, 0), (0.5, 15.5, 3, 2.5, 0)]),                # low scrub
]
# Rocks only where a wall meets the open ground: these stones are drawn in edge cells and inner corners only (never
# in the block, where a stone would repeat every 32 px), when they lie wholly in the edge cell's band.
DRY_EDGE_ROCKS = [
    ("r", 0.05, [(7, 10, 5.5, 4, 0.1), (11, 12, 3.5, 2.5, -0.05), (3.5, 12, 3, 2, -0.1)]),    # outcrop: S_0, E_0, in_NW
    ("r", 0.0, [(23.5, 21.5, 5, 4, 0.1), (20.5, 24, 3, 2.5, -0.05), (27, 24.5, 3, 2, -0.1)]),  # outcrop: N_1, W_1, in_SE
]
SWAMP_HEIGHTS = [4, 1, 3, 2, 0]   # per tree: which crowns stand above which
DRY_HEIGHTS = [6, 5, 3, 2, 4, 1]
# straw tufts on the open earth (x, y): small hand-placed clusters
DRY_TUFTS = [(19, 31), (15, 17), (31, 14), (1, 16)]

STYLES = {
    "swamp": {"trees": SWAMP, "heights": SWAMP_HEIGHTS, "shadow": [(1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4)]},
    "dry": {"trees": DRY, "heights": DRY_HEIGHTS, "extras": DRY_EDGE_ROCKS, "shadow": [(1, 1), (1, 2), (2, 2), (2, 3)]},
}
SPECIES = {   # crest, light, mid, dark, deep, outline
    "c": (C_TIP, C_HL, C_MID, C_DK, S_OUT, S_OUT),        # bald cypress: Ekat's crown colours
    "o": (O_TIP, O_HL, O_MID, O_DK, S_OUT, S_OUT),        # tupelo / water oak: the grass and marsh-rim olives
    "l": (L4, L3, L2, L1, L0, L0),                        # live oak: make_dry_country's tree greens
    "s": (ST, L3, L2, L1, L0, L0),                        # scrub: the same greens, sun-dried straw tips
    "r": (K2, K2, K1, K0, K0, B0),                        # rock: make_dry_country's stone greys
}


# ---------------------------------------------------------------- ground cells
EKAT_CELLS = ("grass", "marsh_C", "water_C", "mud_C", "marsh_N", "marsh_S", "marsh_W", "marsh_E", "marsh_inNW", "marsh_inNE",
              "marsh_inSW", "marsh_inSE", "marshwater_N", "marshwater_S", "marshwater_W", "marshwater_E")


def ground_cells():
    """Ekat's swamp cells straight from the source sheet at the cells the orleans_bayou recipe names (colours
    snapped to GBA steps as the tileset build does: they come out exactly the built colours); dry[0] etc. from
    dry_country.png."""
    g = {}
    recipe = json.load(open(os.path.join(MAPGEN, "tilesets", "recipes", "orleans_bayou.json")))
    src = next(s for s in recipe["sources"] if s["name"] == "ekat")
    ek = Image.open(os.path.join(ROOT, src["image"])).convert("RGB")
    for m in src["metatiles"]:
        if "bottom" in m and m["id"] in EKAT_CELLS:
            x, y = m["bottom"]
            im = ek.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16))
            g[m["id"]] = Image.eval(im, lambda v: (v >> 3) << 3)
    # Ekat's cypress (3x3: crown rows over transparency, then the roots on grass) for scale in the mock
    eka = Image.open(os.path.join(ROOT, src["image"])).convert("RGBA").crop((5 * 16, 2 * 16, 8 * 16, 5 * 16))
    cy = Image.eval(eka.convert("RGB"), lambda v: (v >> 3) << 3)
    px, al = cy.load(), eka.load()
    for yy in range(48):
        for xx in range(48):
            if al[xx, yy][3] < 128 or px[xx, yy] in ((248, 248, 248), (248, 0, 0)) or (yy >= 32 and px[xx, yy] in
                                                                ((120, 160, 104), (104, 144, 96), (136, 176, 128))):
                px[xx, yy] = KEY
    g["cypress"] = cy
    dry = Image.open(os.path.join(HERE, "dry_country.png")).convert("RGB")
    dj = json.load(open(os.path.join(HERE, "dry_country.json")))
    cell = lambda xy: dry.crop((xy[0] * 16, xy[1] * 16, xy[0] * 16 + 16, xy[1] * 16 + 16))
    g["dry"] = cell(dj["terrain"]["dry"][0])
    for k in ("dry_grass", "road_C", "cane"):
        v = dj["terrain"][k]
        g[k] = cell(v[0] if isinstance(v[0], list) else v)
    for k in ("field_tree_l", "rock_l"):
        p = dj["pieces"][k]
        g[k] = dry.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
    return g


def shade_map(style):
    """Ground colour -> its cast-shadow colour (palette colours only)."""
    if style == "swamp":
        return {(144, 184, 152): (104, 152, 120), (136, 176, 128): (96, 128, 88), (120, 168, 128): (96, 128, 88),
                (120, 160, 104): (96, 128, 88), (104, 144, 96): (72, 96, 64), (96, 128, 88): (72, 96, 64),
                (104, 152, 120): (80, 112, 96), (80, 112, 96): (64, 96, 64), (72, 96, 64): (64, 96, 64),
                (64, 96, 64): S_OUT, (96, 136, 136): (72, 112, 112), (72, 112, 112): (80, 80, 80),
                (72, 112, 104): (80, 80, 80), (80, 80, 80): S_OUT, S_OUT: S_OUT,
                # Ekat mud (mud_C and its rims; 2026-10-13, canopy on mud): light -> mid -> dark -> the rim's darkest
                (160, 128, 120): (144, 104, 96), (144, 104, 96): (112, 80, 80), (112, 80, 80): (96, 64, 64),
                (96, 64, 64): (88, 72, 64), (88, 72, 64): (88, 72, 64)}
    return {DH: D1, D1: D2, D2: D3, D3: K0, ST: ST_D, ST_D: D3, (240, 216, 120): ST, K0: K0}


# ---------------------------------------------------------------- the renderer
def clumps_of(style, reps=2, extras=False):
    """Every clump on the torus, copied over (2*reps+1)^2 periods:
    (cx, cy, rx, ry, cbias, species, tree bias, tree key, clump index, tree box (x0, y0, x1, y1), height).
    extras: also the style's edge-only trees (drawn under every crown, tree index after the block's trees)."""
    out = []
    k = 0
    trees = list(STYLES[style]["trees"])
    heights = list(STYLES[style]["heights"])
    if extras:
        trees += STYLES[style].get("extras", [])
        heights += [-1] * len(STYLES[style].get("extras", []))   # under the hanging crowns
    for ti, (sp, tb, cl) in enumerate(trees):
        box = (min(c[0] - c[2] for c in cl), min(c[1] - c[3] for c in cl),
               max(c[0] + c[2] for c in cl), max(c[1] + c[3] for c in cl))
        for c in cl:
            for ox in range(-reps, reps + 1):
                for oy in range(-reps, reps + 1):
                    dx, dy = ox * P, oy * P
                    out.append((c[0] + dx, c[1] + dy, c[2], c[3], c[4], sp, tb, (ti, ox, oy), k,
                                (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy), heights[ti]))
            k += 1
    return out


_FP = {}


def footprint(c):
    """The pixels of a clump: its ellipse, plus a cypress's drooping strands below its rim."""
    key = c[:4] + (c[5], c[8])
    if key in _FP:
        return _FP[key]
    cx, cy, rx, ry, sp, k = c[0], c[1], c[2], c[3], c[5], c[8]
    px = set()
    for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 1):
        for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 1):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                px.add((x, y))
    if sp == "c":   # drooping strands: 1-2 px hanging from some bottom-rim columns
        cols = {}
        for x, y in px:
            cols[x] = max(cols.get(x, -99), y)
        for x, yb in cols.items():
            j = (x - math.floor(cx) + k) % 5
            n = 2 if j == 1 else 1 if j == 3 else 0
            if abs(x + 0.5 - cx) > rx * 0.7:
                n = 0
            for j in range(1, n + 1):
                px.add((x, yb + j))
    _FP[key] = px
    return px


def order_key(c):
    # seen from above: a taller tree's crown covers the lower crowns round it; within a tree the clumps further
    # south overlap those to the north
    return (c[10], c[1], c[0])


def clump_colour(c, x, y):
    cx, cy, rx, ry, cb, sp, tb, tree, k, box, ht = c
    crest, hl, mid, dk, deep, out = SPECIES[sp]
    dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
    q = dx * dx + dy * dy
    if q > 1.0:   # a drooping strand
        return deep
    tx = (x + 0.5 - (box[0] + box[2]) / 2) / ((box[2] - box[0]) / 2)
    ty = (y + 0.5 - (box[1] + box[3]) / 2) / ((box[3] - box[1]) / 2)
    vt = -0.45 * tx - 0.8 * ty                      # the tree's dome
    vc = -0.25 * dx - 0.9 * dy                      # the clump's dome
    if sp == "r":
        v = -0.65 * dx - 0.75 * dy + 0.2 * vt + cb + tb
        col = hl if v > 0.2 else mid if v > -0.45 else dk
        if q > 0.75 and dy > 0.2:
            col = dk
        return col
    ladder = [deep, dk, mid, hl, crest]
    if sp == "c":   # bald cypress: one dome of drooping 2 px strands (Ekat's crown), lit top-left
        v = -0.5 * tx - 0.85 * ty + tb + 0.5 * cb
        i = 4 if v > 1.05 else 3 if v > 0.3 else 2 if v > -0.3 else 1 if v > -0.9 else 0
        sx, sy = x - math.floor(box[0]), y - math.floor(box[1])
        strand = sx // 2
        sgn = 1 if tx > 0 else -1                      # the sprays droop outwards from the crown's middle
        p = (sy - sgn * (sx // 2) + int(_hash(strand, tree[0], 3) * 7)) % 7
        if p == 0:
            i -= 1                                   # the gap between two leaf sprays
        elif p == 1 and i < 4:
            i = min(i + 1, 3 if v < 0.7 else 4)       # the lit top of the next spray
        if strand % 2 and p >= 4:
            i -= 1                                   # every second strand hangs in shade
        return ladder[max(i, 0)]
    v = 0.75 * vc + 0.4 * vt + cb + tb
    i = 4 if v > 1.0 else 3 if v > 0.35 else 2 if v > -0.25 else 1 if v > -0.8 else 0
    if q > 0.7 and dy > 0.2:                        # the dark seam on each clump's lower rim
        i = 0 if (q > 0.86 and dy > 0.4) else min(i, 1)
    elif q > 0.5 and dy < -0.4:                     # each clump's lit cap
        i = min(i + 1, 4 if v > 0.6 else 3)
    if sp == "c" and i in (2, 3) and q < 0.85:      # cypress: fronds radiating from the crown's top
        tx0, ty0 = (box[0] + box[2]) / 2, box[1] - 2
        ang = math.atan2(x + 0.5 - tx0, y + 0.5 - ty0)
        f = (ang / 0.2 + 0.37 * k) % 3
        if f < 1:
            i -= 1
        elif f >= 2.2 and i == 2 and v > -0.05:
            i = 3
    elif sp in ("o", "l", "s") and i in (2, 3) and q < 0.6:   # a few lit / dark leaves
        h = _hash(x % P, y % P, 7 + k)
        if h < 0.09:
            i += 1
        elif h > 0.94:
            i -= 1
    return ladder[i]


def render(style, x0, y0, w, h, ground, keep=None, extras=False):
    """Render [x0, x0+w) x [y0, y0+h) of a canopy. ground(x, y) -> colour of the uncovered ground (None = the
    swamp canopy's deep shade); keep(clump) -> bool restricts the clumps (a wall's own, for edge cells)."""
    st = STYLES[style]
    clumps = sorted((c for c in clumps_of(style, extras=extras) if (x0 - 12 < c[0] < x0 + w + 12 and y0 - 12 < c[1] < y0 + h + 12)
                     and (keep is None or keep(c))), key=order_key)
    owner = {}
    for c in clumps:
        for p in footprint(c):
            owner[p] = c
    sh = shade_map(style)
    torder = {c[7]: c[10] for c in clumps}
    img = Image.new("RGB", (w, h))
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c = owner.get((x, y))
            nb = [owner.get((x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if c is not None:
                col = clump_colour(c, x, y)
                # the tree's outline against the ground and against trees behind it
                if any(n is None or (n[7] != c[7] and torder[n[7]] < torder[c[7]]) for n in nb):
                    col = SPECIES[c[5]][5]
                else:   # a taller crown's shadow on this one
                    for dx, dy in st["shadow"]:
                        o = owner.get((x - dx, y - dy))
                        if o is not None and o[7] != c[7] and o[10] > c[10]:
                            lad = SPECIES[c[5]][:5][::-1]   # deep .. crest
                            col = lad[max(0, lad.index(col) - 1)] if col in lad else col
                            break
            else:
                g = ground(x, y) if ground else None
                if g is None:   # the swamp canopy's deep shade between crowns
                    col = S_OUT
                else:
                    col = g
                    if any((x - dx, y - dy) in owner for dx, dy in st["shadow"]):
                        col = sh.get(g, g)
                        if any((x - dx, y - dy) in owner for dx, dy in ((0, 1), (1, 1), (0, 2), (1, 2))):
                            col = sh.get(col, col)   # the deep shade right under a crown
            img.putpixel((x - x0, y - y0), col)
    return img, owner


def block_ground(style, extra=None):
    """The ground inside the block: deep shade (swamp) or the dry[0] earth with straw tufts (dry)."""
    if style == "swamp":
        return None
    t = extra["dry"].load()
    tufts = set()
    for tx, ty in DRY_TUFTS:
        for dx, dy, c in ((0, 0, ST_D), (1, -1, ST), (-1, -1, ST), (0, -1, ST_D), (1, -2, ST), (-1, -2, ST_D),
                          (2, -2, ST), (0, -2, ST)):
            tufts.add((((tx + dx) % P, (ty + dy) % P), c))
    tmap = dict(tufts)

    def f(x, y):
        return tmap.get((x % P, y % P), t[x % 16, y % 16])
    return f


def block(style, g):
    img, _ = render(style, 0, 0, P, P, block_ground(style, g))
    return img


# ---------------------------------------------------------------- wall-transition (edge) cells
# face: which side of the edge cell the terrain is on ("S" = the canopy is north, the cell lies south of the wall).
# For each face: the wall predicate (block coordinates, wall phase fixed), the edge cell origins per parity.
WALLS = {   # the wall half-plane of each face (block coordinates; the wall's phase is fixed, see the docstring)
    "S": lambda x, y: y < P, "N": lambda x, y: y >= P, "E": lambda x, y: x < P, "W": lambda x, y: x >= P}
FACES = {   # face: (the walls it borders, the edge cell's origin per parity)
    "S": (("S",), {0: (0, P), 1: (16, P)}),
    "N": (("N",), {0: (0, P - 16), 1: (16, P - 16)}),
    "E": (("E",), {0: (P, 0), 1: (P, 16)}),
    "W": (("W",), {0: (P - 16, 0), 1: (P - 16, 16)}),
    "in_NW": (("S", "E"), {None: (P, P)}),
    "in_NE": (("S", "W"), {None: (P - 16, P)}),
    "in_SW": (("N", "E"), {None: (P, P - 16)}),
    "in_SE": (("N", "W"), {None: (P - 16, P - 16)}),
}
NEAR = {"S": (0, -16), "N": (0, 16), "E": (-16, 0), "W": (16, 0)}
REACH = 10   # how far (px) a wall's trees may hang out over the terrain (clumps touching the wall: up to 13)


def wall_keep(style, wname):
    """The clumps a wall shows over the terrain beside it: every tree with a clump touching the wall (grown by
    1 px) keeps its clumps, except those not touching the wall that reach more than REACH px out from it; trees
    that do not touch the wall are gone. A clump is at most 12 px tall (+2 px strands), so all stay in one cell."""
    wall, (nx, ny) = WALLS[wname], NEAR[wname]
    nx, ny = nx * REACH // 16, ny * REACH // 16
    cl = [c for c in clumps_of(style) if -40 < c[0] < 2 * P + 40 and -40 < c[1] < 2 * P + 40]

    def touches(c):
        return any(wall(x + dx, y + dy) for x, y in footprint(c) for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))
    touch = {c[7] for c in cl if touches(c)}
    fx, fy = NEAR[wname]
    whole = set()   # small trees (rocks, scrub) that fit in the edge cell hang out whole, never in pieces
    for t in touch:
        tcl = [c for c in cl if c[7] == t]
        if tcl[0][5] in ("r", "s") and all(wall(x, y) or wall(x + fx * 15 // 16, y + fy * 15 // 16)
                                           for c in tcl for x, y in footprint(c)):
            whole.add(t)
    return {(c[7], c[8]) for c in cl
            if c[7] in touch and (c[7] in whole or touches(c)
                                  or all(wall(x, y) or wall(x + nx, y + ny) for x, y in footprint(c)))}


_KEEP = {}


def edge_cell(style, face, parity, base, g):
    """The 16x16 edge cell: the wall's own trees hanging over the 16x16 ground cell `base` (wall_keep), with
    their outline and cast shadow. An inner corner shows both walls' trees."""
    walls, origins = FACES[face]
    ex, ey = origins[parity]
    bp = base.load()
    bg = block_ground(style, g)
    keepset = set()
    for w in walls:
        if (style, w) not in _KEEP:
            _KEEP[(style, w)] = wall_keep(style, w)
        keepset |= _KEEP[(style, w)]

    def wall(x, y):
        return any(WALLS[w](x, y) for w in walls)

    def ground(x, y):
        if wall(x, y):
            return bg(x, y) if bg else None
        return bp[x % 16, y % 16]
    ntrees = len(STYLES[style]["trees"])
    allx = [t for t in clumps_of(style, extras=True) if t[7][0] >= ntrees]

    def keep(c):
        if c[7][0] < ntrees:
            return (c[7], c[8]) in keepset
        # an edge-only stone: every clump of its tree off the wall and within one cell of it
        return all(not wall(x, y) and any(WALLS[w](x + NEAR[w][0] * 15 // 16, y + NEAR[w][1] * 15 // 16)
                                          for w in walls)
                   for t in allx if t[7] == c[7] for x, y in footprint(t))
    img, owner = render(style, ex, ey, 16, 16, ground, keep, extras=True)
    # nothing of a kept clump may fall more than one cell out from its wall
    stray = [(x, y) for (x, y) in owner if not wall(x, y)
             and not any(WALLS[w](x + NEAR[w][0], y + NEAR[w][1]) for w in walls)]
    return img, stray


# ---------------------------------------------------------------- OUTER (convex) corner cells (2026-10-13)
# The terrain cell diagonal to a wall's convex corner: the wall is a quadrant (union of 2x2 blocks on the even grid, so the
# corner's wall cell always has parity (1, 1) for out_NW, (0, 1) out_NE, (1, 0) out_SW, (0, 0) out_SE and the corner cell
# the opposite one: out_NW (0, 0), out_NE (1, 0), out_SW (0, 1), out_SE (1, 1)). Its two 4-neighbours on the wall side are
# the faces' edge cells (out_NW: S_1 to its west, E_1 to its north). The cell shows exactly the overhanging clumps that cross
# into it from those two edge cells (so it joins them pixel-exactly, as the next face cell along a straight wall would),
# plus one corner clump of the tree standing in the wall's corner, which rounds the canopy off diagonally; its right /
# bottom (outer) sides are plain ground. Grounds: any 16x16 cell (bake_edge(style, "out_NW", None, base16)).
OUTER = {   # corner: (horizontal face's wall, vertical face's wall, cell origin in block coordinates, unit vector out of the corner)
    "out_NW": ("S", "E", (P, P), (1, 1)),
    "out_NE": ("S", "W", (P - 16, P), (-1, 1)),
    "out_SW": ("N", "E", (P, P - 16), (1, -1)),
    "out_SE": ("N", "W", (P - 16, P - 16), (-1, -1)),
}
OUTER_ORDER = ("out_NW", "out_NE", "out_SW", "out_SE")
# the corner clump: centre CORNER_D px out from the wall corner along the diagonal, radii (rx, ry); per style
CORNER_CLUMP = {"swamp": (3.0, 5.0, 4.0), "dry": (3.0, 4.5, 3.5)}


def _quad(corner):
    hw, vw = OUTER[corner][:2]
    return lambda x, y: WALLS[hw](x, y) and WALLS[vw](x, y)


def corner_tree(style, corner):
    """the tree standing in the wall's corner pixel (its clumps cover the pixel just inside the corner), as (species,
    tree bias, tree key, box, height) from the block's clumps; None if the corner pixel is open ground"""
    hw, vw, (ex, ey), (ux, uy) = OUTER[corner]
    px, py = P - (1 if ux > 0 else 0), P - (1 if uy > 0 else 0)     # the wall pixel at the corner
    best = None
    for c in sorted(clumps_of(style), key=order_key):
        if (px, py) in footprint(c):
            best = c
    return best


def outer_cell(style, corner, base, g, corner_clump=True):
    """The 16x16 outer-corner cell over the 16x16 ground cell `base` (see OUTER). Returns (img, info)."""
    hw, vw, (ex, ey), (ux, uy) = OUTER[corner]
    quad = _quad(corner)
    bp = base.load()
    bg = block_ground(style, g)
    for w in (hw, vw):
        if (style, w) not in _KEEP:
            _KEEP[(style, w)] = wall_keep(style, w)
    kh, kv = _KEEP[(style, hw)], _KEEP[(style, vw)]

    def ground(x, y):
        if quad(x, y):
            return bg(x, y) if bg else None
        return bp[x % 16, y % 16]
    ntrees = len(STYLES[style]["trees"])
    allc = clumps_of(style, extras=True)
    fp = {(c[7], c[8]): footprint(c) for c in allc if ex - 20 < c[0] < ex + 36 and ey - 20 < c[1] < ey + 36}

    def keep(c):
        k = (c[7], c[8])
        if k not in fp:
            return False
        pts = fp[k]
        if c[7][0] < ntrees:
            # a face's overhanging clump crosses in only if it reaches the wall's other side (it lies in that face's edge cell
            # or in the wall itself)
            return ((k in kh and any(WALLS[vw](x, y) for x, y in pts))
                    or (k in kv and any(WALLS[hw](x, y) for x, y in pts)))
        return False   # no edge-only stones in an outer corner: the faces and inner corners already carry them every 32 px
    extra = []
    if corner_clump:
        t = corner_tree(style, corner)
        if t is not None:
            d, rx, ry = CORNER_CLUMP[style]
            cx, cy = P + ux * d, P + uy * d
            # one more clump of the corner tree, the last of its clumps (index past the layout's), drawn over its neighbours
            extra.append((cx, cy, rx, ry, 0.0, t[5], t[6], t[7], 900 + OUTER_ORDER.index(corner), t[9], t[10]))
    img, owner = render_extra(style, ex, ey, 16, 16, ground, keep, extra)
    return img, {"corner_tree": None if not extra else extra[0][5]}


def render_extra(style, x0, y0, w, h, ground, keep, extra):
    """render() with extra clumps added to the layout (the outer corner's corner clump)"""
    global clumps_of
    base_fn = clumps_of

    def patched(st, reps=2, extras=False):
        return base_fn(st, reps, extras) + (list(extra) if st == style else [])
    clumps_of = patched
    try:
        return render(style, x0, y0, w, h, ground, lambda c: keep(c) or c in extra, extras=True)
    finally:
        clumps_of = base_fn


def bake_edge(style, face, parity, base16):
    """Public: an edge cell baked on any 16x16 ground cell (PIL RGB). face may also be an outer corner (out_NW ...)."""
    if face in OUTER:
        return outer_cell(style, face, base16, ground_cells())[0]
    return edge_cell(style, face, parity, base16, ground_cells())[0]


# ---------------------------------------------------------------- build the sheet
TERRAINS = {"swamp": ["marsh", "water"], "dry": ["dry"]}
BASES = {"marsh": "marsh_C", "water": "water_C", "dry": "dry"}
FACE_ORDER = [("S", 0), ("S", 1), ("N", 0), ("N", 1), ("E", 0), ("E", 1), ("W", 0), ("W", 1),
              ("in_NW", None), ("in_NE", None), ("in_SW", None), ("in_SE", None)]


def edge_name(style, face, parity, terr):
    return f"{style}_{face}_{terr}" + ("" if parity is None else f"_{parity}")


def build():
    g = ground_cells()
    cols = 12
    cells, imgs, strays = {}, {}, []
    blocks = {}
    for style, bname in (("swamp", "swamp_canopy"), ("dry", "dry_scrub")):
        b = block(style, g)
        names = [[None, None], [None, None]]
        for by in range(2):
            for bx in range(2):
                n = f"{bname}_{bx}{by}"
                imgs[n] = b.crop((bx * 16, by * 16, bx * 16 + 16, by * 16 + 16))
                cells[n] = [bx + (2 if style == "dry" else 0), by]
                names[by][bx] = n
        blocks[bname] = names
    row = 2
    for style in ("swamp", "dry"):
        for terr in TERRAINS[style]:
            for k, (face, par) in enumerate(FACE_ORDER):
                n = edge_name(style, face, par, terr)
                img, stray = edge_cell(style, face, par, g[BASES[terr]], g)
                if stray:
                    strays.append((n, len(stray)))
                imgs[n] = img
                cells[n] = [k, row]
            row += 1
    sheet = Image.new("RGB", (cols * 16, row * 16), KEY)
    for n, (x, y) in cells.items():
        sheet.paste(imgs[n], (x * 16, y * 16))
    return sheet, cells, blocks, g, strays


# ---------------------------------------------------------------- counting
def canon(t):
    return min(x.tobytes() for x in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))


def tiles_of(img):
    a = np.array(img)
    return [a[y:y + 8, x:x + 8] for y in range(0, a.shape[0], 8) for x in range(0, a.shape[1], 8)]


def census(imgs_by_group, known_imgs):
    known = {canon(t) for im in known_imgs for t in tiles_of(im)}
    seen = set(known)
    out = []
    for gname, ims in imgs_by_group:
        n, cols = 0, set()
        for im in ims:
            cols |= set(map(tuple, np.array(im).reshape(-1, 3)))
            for t in tiles_of(im):
                k = canon(t)
                if k not in seen:
                    seen.add(k)
                    n += 1
        out.append((gname, len(ims), n, cols))
    return out


# ---------------------------------------------------------------- mock maps
def parity_cell(names, x, y):
    return names[y & 1][x & 1]


def paste_key(img, piece, x, y):
    px = piece.load()
    for yy in range(piece.height):
        for xx in range(piece.width):
            if px[xx, yy] != KEY:
                img.putpixel((x + xx, y + yy), px[xx, yy])


def mock_map(style, cell, g, blocks, W, H, grid, walls, edge, M=5):
    names = blocks["swamp_canopy" if style == "swamp" else "dry_scrub"]
    img = Image.new("RGB", ((W + 2 * M) * 16, (H + 2 * M) * 16))
    for y in range(-M, H + M):
        for x in range(-M, W + M):
            if not (0 <= x < W and 0 <= y < H) or (x, y) in walls:
                im = cell[parity_cell(names, x, y)]
            elif (x, y) in edge:
                face, par = edge[(x, y)]
                im = edge_cell(style, face, par, g[grid[(x, y)]], g)[0]
            else:
                im = g[grid[(x, y)]]
            img.paste(im, ((x + M) * 16, (y + M) * 16))
    return img, (M * 16, M * 16, W * 16, H * 16)


def frame_edges(W, H, n, w, e, s_open=True):
    """Walls n deep on the north, w on the west, e on the east (the south runs into the border); the edge cells
    (faces and inner corners) round the open area."""
    walls = {(x, y) for y in range(H) for x in range(W) if y < n or x < w or x >= W - e}
    edge = {}
    for x in range(w + 1, W - e - 1):
        edge[(x, n)] = ("S", x & 1)
        edge[(x, H - 1)] = ("N", x & 1)
    for y in range(n + 1, H - 1):
        edge[(w, y)] = ("E", y & 1)
        edge[(W - e - 1, y)] = ("W", y & 1)
    edge[(w, n)] = ("in_NW", None)
    edge[(W - e - 1, n)] = ("in_NE", None)
    edge[(w, H - 1)] = ("in_SW", None)
    edge[(W - e - 1, H - 1)] = ("in_SE", None)
    for (x, y), (f, p) in edge.items():   # the parity rules
        assert p is None or p == ((x if f in "SN" else y) & 1)
        assert {"S": y % 2 == 0, "N": (y + 1) % 2 == 0, "E": x % 2 == 0, "W": (x + 1) % 2 == 0,
                "in_NW": (x % 2, y % 2) == (0, 0), "in_NE": (x % 2, y % 2) == (1, 0),
                "in_SW": (x % 2, y % 2) == (0, 1), "in_SE": (x % 2, y % 2) == (1, 1)}[f], (f, x, y)
    return walls, edge


def mock_swamp(cell, g, blocks):
    """A 22x14 swamp map: canopy walls N 2, W 2, E 2 over marsh; a grass meadow in the marsh, an Ekat cypress
    for scale; a lake in the south that runs off the map's south edge into the canopy border (the border is the
    wall there: the map's last row holds the N-face cells, so H is even)."""
    W, H = 22, 14
    grid = {}
    for y in range(H):
        for x in range(W):
            grid[(x, y)] = "water_C" if y >= 9 else "marshwater_N" if y == 8 else "marsh_C"
    gx0, gx1, gy0, gy1 = 10, 16, 3, 5
    for y in range(gy0, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            grid[(x, y)] = "grass"
    for x in range(gx0, gx1 + 1):
        grid[(x, gy0 - 1)] = "marsh_S"
        grid[(x, gy1 + 1)] = "marsh_N"
    for y in range(gy0, gy1 + 1):
        grid[(gx0 - 1, y)] = "marsh_E"
        grid[(gx1 + 1, y)] = "marsh_W"
    grid[(gx0 - 1, gy0 - 1)] = "marsh_inSE"
    grid[(gx1 + 1, gy0 - 1)] = "marsh_inSW"
    grid[(gx0 - 1, gy1 + 1)] = "marsh_inNE"
    grid[(gx1 + 1, gy1 + 1)] = "marsh_inNW"
    walls, edge = frame_edges(W, H, 2, 2, 2)
    img, r = mock_map("swamp", cell, g, blocks, W, H, grid, walls, edge)
    paste_key(img, g["cypress"], r[0] + 4 * 16, r[1] + 3 * 16)
    return img, r


def mock_dry(cell, g, blocks):
    """A 22x14 dry map: scrub walls N 2, W 4, E 2 over earth; a road, a cane field and tall dry grass, the dry
    set's live oak and boulder for scale; the south earth runs into the border."""
    W, H = 22, 14
    grid = {(x, y): "dry" for y in range(H) for x in range(W)}
    for x in range(W):
        grid[(x, 8)] = "road_C"
    for y in range(4, 7):
        for x in range(6, 10):
            grid[(x, y)] = "cane"
    for y in range(10, 13):
        for x in range(12, 17):
            grid[(x, y)] = "dry_grass"
    walls, edge = frame_edges(W, H, 2, 4, 2)
    img, r = mock_map("dry", cell, g, blocks, W, H, grid, walls, edge)
    paste_key(img, g["field_tree_l"], r[0] + 13 * 16, r[1] + 3 * 16)
    paste_key(img, g["rock_l"], r[0] + 7 * 16, r[1] + 10 * 16)
    return img, r


def tiled(cell, names, nx, ny, ox=0, oy=0):
    img = Image.new("RGB", (nx * 16, ny * 16))
    for y in range(ny):
        for x in range(nx):
            img.paste(cell[parity_cell(names, x + ox, y + oy)], (x * 16, y * 16))
    return img


def neighbours(cell, g, blocks):
    """Sugar country: a swamp map (marsh, Route 14) beside a dry map (earth, Route 15), each under a north wall of
    its own border block with the S-face edge cells, as two neighbouring maps sit in the stitched world."""
    W, H = 16, 10
    img = Image.new("RGB", (2 * W * 16, H * 16))
    for side, (style, bname, base, terr) in enumerate((("swamp", "swamp_canopy", "marsh_C", "marsh"),
                                                        ("dry", "dry_scrub", "dry", "dry"))):
        for y in range(H):
            for x in range(W):
                if y < 4:
                    im = cell[parity_cell(blocks[bname], x, y)]
                elif y == 4:
                    im = cell[edge_name(style, "S", x & 1, terr)]
                else:
                    im = g[base]
                img.paste(im, ((side * W + x) * 16, y * 16))
    return img


def corner_ticks(im, r, c=(240, 208, 72)):
    """Mark the map's corners with small L ticks just outside the map (the edge itself stays unobstructed)."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    x, y, w, h = r
    for cx, cy, sx, sy in ((x - 1, y - 1, -1, -1), (x + w, y - 1, 1, -1), (x - 1, y + h, -1, 1), (x + w, y + h, 1, 1)):
        d.line((cx, cy, cx, cy + sy * 8), fill=c)
        d.line((cx, cy, cx + sx * 8, cy), fill=c)
    return im


def wrap(text, n):
    out, line = [], ""
    for w in text.split(" "):
        if line and len(line) + 1 + len(w) > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


def font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size)
    except TypeError:   # Pillow < 10.1
        return ImageFont.load_default()


def review(sheet, cells, blocks, g, lines, path):
    cell = {n: sheet.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)) for n, (x, y) in cells.items()}
    up = lambda im, k: im.resize((im.width * k, im.height * k), Image.NEAREST)
    F, FS = font(16), font(12)
    BG, FG, DIM = (24, 28, 36), (240, 240, 240), (170, 176, 188)
    pad = 16
    parts = []
    # 1. each block tiled 6 x 4 blocks (12 x 8 cells) at 2x
    parts.append(("1. The border blocks tiled 6 x 4 (12 x 8 cells) at 2x: swamp_canopy | dry_scrub",
                  [up(tiled(cell, blocks["swamp_canopy"], 12, 8), 2), up(tiled(cell, blocks["dry_scrub"], 12, 8), 2)]))
    # 2. every cell at 4x, labelled
    LM = 110
    lab = Image.new("RGB", (LM + 12 * 68 + 8, 2 * 66 + 24 + 3 * 86), BG)
    d = ImageDraw.Draw(lab)
    for i, bname in enumerate(("swamp_canopy", "dry_scrub")):
        for by in range(2):
            for bx in range(2):
                lab.paste(up(cell[blocks[bname][by][bx]], 4), (LM + (i * 3 + bx) * 68 + 4, by * 66 + 4))
        d.text((LM + i * 3 * 68 + 4, 2 * 66 + 4), bname, fill=DIM, font=FS)
    d.text((4, 50), "blocks", fill=FG, font=F)
    y0 = 2 * 66 + 24
    for r, (style, terr) in enumerate((("swamp", "marsh"), ("swamp", "water"), ("dry", "dry"))):
        d.text((4, y0 + r * 86 + 14), style + " on", fill=FG, font=F)
        d.text((4, y0 + r * 86 + 36), "earth" if terr == "dry" else terr, fill=FG, font=F)
        for k, (face, par) in enumerate(FACE_ORDER):
            lab.paste(up(cell[edge_name(style, face, par, terr)], 4), (LM + k * 68 + 4, y0 + r * 86))
            d.text((LM + k * 68 + 6, y0 + r * 86 + 66), face + ("" if par is None else f"_{par}"), fill=DIM, font=FS)
    parts.append(("2. borders.png at 4x: the two blocks; then the edge cells (face_parity) of the swamp on marsh, "
                  "on water, and of the dry block on earth", [lab]))
    ms, rs = mock_swamp(cell, g, blocks)
    md, rd = mock_dry(cell, g, blocks)
    parts.append(("3a. Mock swamp map edge at 3x: a 22 x 14 map (yellow ticks = its corners), canopy wall 2 deep "
                  "N, W, E over marsh; the lake runs off the south edge into the canopy border (no inward wall "
                  "there); Ekat's cypress for scale", [up(corner_ticks(ms, rs), 3)]))
    parts.append(("3b. Mock dry map edge at 3x: a 22 x 14 map, scrub wall N 2, W 4, E 2 over earth; road, cane, "
                  "tall dry grass; the earth runs off the south edge into the border; the dry set's live oak and "
                  "boulder for scale", [up(corner_ticks(md, rd), 3)]))
    parts.append(("4. Sugar country at 2x: a swamp map (marsh) beside a dry map (earth), each under its own border "
                  "wall, as two neighbouring maps meet in the world", [up(neighbours(cell, g, blocks), 2)]))
    width = max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in parts)
    height = sum(max(i.height for i in ims) + 24 * len(wrap(t, 160)) + pad for t, ims in parts) + 80 + 22 * len(lines)
    out = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(out)
    y = pad
    for title, ims in parts:
        for line in wrap(title, 160):
            d.text((pad, y), line, fill=FG, font=F)
            y += 22
        y += 2
        x = pad
        for im in ims:
            out.paste(im, (x, y))
            x += im.width + pad
        y += max(i.height for i in ims) + pad
    d.text((pad, y), "5. Counts (8x8 tiles after flip dedupe; tiles equal to plain marsh_C / water_C / dry[0] / grass "
                     "are not new; each group counts only tiles not already in the groups above it)", fill=FG, font=F)
    y += 26
    for line in lines:
        d.text((pad, y), line, fill=DIM, font=F)
        y += 22
    out.crop((0, 0, width, y + pad)).save(path)


def main():
    sheet, cells, blocks, g, strays = build()
    sheet.save(os.path.join(HERE, "borders.png"))
    cell = {n: sheet.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)) for n, (x, y) in cells.items()}

    def pick(name, terr=None):
        if terr is None:
            return [cell[n] for row in blocks[name] for n in row]
        return [cell[edge_name(name, f, p, terr)] for f, p in FACE_ORDER]
    groups = [("swamp_canopy block", pick("swamp_canopy")),
              ("swamp edges on marsh", pick("swamp", "marsh")),
              ("swamp edges on water", pick("swamp", "water")),
              ("dry_scrub block", pick("dry_scrub")),
              ("dry edges on earth", pick("dry", "dry"))]
    rep = census(groups, [g[k] for k in ("marsh_C", "water_C", "dry", "grass")])
    lines = [f"{gname:24s} {ncell:3d} cells {n:4d} new 8x8 tiles   {len(cols):2d} colours"
             for gname, ncell, n, cols in rep]
    swc = set().union(*(r[3] for r in rep[:3]))
    drc = set().union(*(r[3] for r in rep[3:]))
    lines.append(f"swamp art: {len(swc)} colours, outside the core green palette: "
                 f"{sorted(swc - set(CORE_PAL[1:])) or 'none'} (the palette's slot 15 stays free)")
    lines.append(f"dry art: {len(drc)} colours, outside DRY_PAL (make_dry_country colours): "
                 f"{sorted(drc - set(DRY_PAL[1:])) or 'none'}")
    lines.append(f"edge-cell check (no kept clump reaches past its cell): {'ok' if not strays else strays}")
    for line in lines:
        print("  " + line)
    review(sheet, cells, blocks, g, lines, os.path.join(MAPGEN, "maps", "00_borders_art.png"))
    index = {
        "_comment": "Map border art (make_borders.py; its docstring has the details). Cells are [x, y] in 16 px "
                    "units of borders.png, all opaque. blocks: the 2x2 border blocks as [[cell at (x&1, y&1) = "
                    "(0,0), (1,0)], [(0,1), (1,1)]]; the same cells are the inward wall, placed by map parity. edges: "
                    "per border, per terrain, the wall-transition cell of every face (+ _parity).",
        "png": "borders.png",
        "palettes": {"swamp": {"colours": [list(c) for c in CORE_PAL],
                               "note": "slot 0 transparent; exactly the core green palette of the Ekat terrain "
                                       "(orleans_route_b/10, orleans_village/07, orleans_pointe/06; slot 15 free). "
                                       "The swamp cells use only these colours."},
                     "dry": {"colours": [list(c) for c in DRY_PAL],
                             "note": "slot 0 transparent; 15 colours, all from make_dry_country.py (earth DH D1 D2 "
                                     "D3, straw ST ST_D, leaves L0-L4, rock K0-K2, outline B0). Its own palette."}},
        "blocks": blocks,
        "cells": cells,
        "edges": {style: {terr: {(f + ("" if p is None else f"_{p}")): edge_name(style, f, p, terr)
                                 for f, p in FACE_ORDER} for terr in TERRAINS[style]} for style in ("swamp", "dry")},
        "rules": {
            "border": "layout border (4 metatiles) = blocks[name] in the order 00, 10, 01, 11 (engine: "
                      "border[(x & 1) + (y & 1) * 2])",
            "wall": "an inward wall cell (x, y) = blocks[name][y & 1][x & 1], the border's own cell at that parity",
            "depth": "d = wall depth in cells, 0 = no inward wall (the border itself is the wall)",
            "S": "wall on the map's north edge: edge row y = d, d even (0, 2, 4); cell edges[..]['S_<x & 1>']",
            "E": "wall on the west edge: edge column x = d, d even (0, 2, 4); cell edges[..]['E_<y & 1>']",
            "N": "wall on the south edge: first wall row h - d even, edge row h - d - 1; cell edges[..]['N_<x & 1>']",
            "W": "wall on the east edge: first wall column w - d even, edge col w - d - 1; cell edges[..]['W_<y & 1>']",
            "corners": "where two walls meet, the open corner cell: in_NW (canopy N and W) sits at a cell with "
                       "(x & 1, y & 1) = (0, 0), in_NE at (1, 0), in_SW at (0, 1), in_SE at (1, 1)",
            "other_ground": "make_borders.bake_edge(style, face, parity, base16) bakes an edge cell on any 16x16 "
                            "ground cell (e.g. where a wall crosses a marsh-water bank)",
            "passability": "border, wall and edge cells are all impassable (canopy / scrub over the terrain)",
        },
    }
    with open(os.path.join(HERE, "borders.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)


if __name__ == "__main__":
    main()

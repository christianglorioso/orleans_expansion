"""Natural Surf-barrier props: the pieces an irregular line of blocking water cells needs that the sets do not have yet (2026-10-13).
Art for review, not integrated (no recipe, no prefab yet).

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/make_water_barriers.py

A barrier stops a surfer 1-3 cells short of a map edge in open water. Movement is 4-way, so a line of blocking cells may step
diagonally; what it needs is a good stock of single-cell blockers that read as natural (so the line can wander) plus a few larger
accents. What the sets already have (all on ekat:water_C, the one water every Orleans tileset uses):
    bayou    ekat water_weeds1 (leafy plant), water_weeds2 (reed tuft), water_lily (sprouts), waterstump (1x1); knees (3x1, + a
             second row), waterlog (2x1), snag_water (1x2), cypress_small_water (2x3), cypress_water (3x3)
    coast    sunken_piling (1x2, lmk), pile (1x1, harbor), mooring_post (1x1, camp), buoy (1x1, camp), channel_buoy (1x2, lmk),
             shipwreck (4x3); boulder is on grass only
What is missing, drawn here:
    bayou    knees_1a, knees_1b   single-cell cypress-knee clusters (the 3x1 knees force straight runs of three)
             cattails             a 1x2 cattail clump (the top cell is overhead, passable; the bottom blocks): height in a reed line
    coast    rock_1a, rock_1b     single-cell rocks awash (one boulder; two stones), foam at the waterline
             rock_ledge_0/1       a 2x1 low ledge of tumbled stones
Colours: bayou pieces use only the Ekat water / knee / reed colours (the core green palette and the knee browns); the rocks use
only the levee riprap palette (levee.py STONE_L STONE STONE_D OUTLINE FOAM WATER_C WATER_D), so a coastal map that has the
levee or the riprap already holds them.

writes  tools/mapgen/tilesets/water_props/wp_<name>.png   16x16 cells, opaque on water_C (a 1x2 piece's top cell is RGBA: clear
        where the ground shows), plus water_props.json (cells, sizes, passable cells, colours)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, MAPGEN)
import levee  # noqa: E402

OUT_DIR = os.path.join(MAPGEN, "tilesets", "water_props")
WATER, WATER_D, WATER_DK = (96, 136, 136), (72, 112, 112), (80, 80, 80)
# Ekat knee wood (sampled from swamp_tiles.png knees on water) and reed greens (water_weeds2 / reeds)
K_OUT, K_D, K_M, K_L = (48, 48, 40), (104, 96, 88), (136, 120, 104), (160, 144, 120)
R_DK, R_D, R_M, R_L = (40, 56, 40), (64, 96, 64), (80, 112, 96), (104, 152, 120)
# levee riprap
S_L, S_M, S_D, S_O, FOAM = levee.STONE_L, levee.STONE, levee.STONE_D, levee.OUTLINE, levee.FOAM


def _hash(x, y, k=0):
    n = (x * 374761393 + y * 668265263 + k * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def water_cell():
    sys.path.insert(0, HERE)
    import make_borders as mb
    return mb.ground_cells()["water_C"].convert("RGB")


def canvas(w, h, base):
    a = np.zeros((h * 16, w * 16, 3), dtype=np.uint8)
    b = np.array(base)
    for y in range(h):
        for x in range(w):
            a[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = b
    return a


# ---------------------------------------------------------------- bayou: cypress knees
def knees(a, spots, seed):
    """cypress knees: knobbly cones rising from the water, lit from the top-left, a dark waterline and a ripple ring; drawn back
    to front (by waterline), each with its own outline"""
    H, W = a.shape[:2]
    for cx, by, hw, ht in sorted(spots, key=lambda s_: s_[1]):   # base centre x, waterline y, half width at the waterline, height
        for y in range(int(by) - 1, int(by) + 4):                 # the waterline ring and ripple
            for x in range(int(cx - hw - 4), int(cx + hw + 5)):
                if 0 <= x < W and 0 <= y < H:
                    q = ((x + 0.5 - cx) / (hw + 3.0)) ** 2 + ((y + 0.5 - by - 0.8) / 2.2) ** 2
                    if q <= 1.0 and y >= by:
                        a[y, x] = WATER_DK if (q < 0.5 and y <= by + 1) else WATER_D
        mask = np.zeros((H, W), dtype=bool)
        for y in range(int(by - ht), int(by) + 1):
            t = min(1.0, max(0.0, (by - y) / ht))
            half = hw * (1 - t) ** 0.8 + 0.5
            for x in range(int(cx - half) - 1, int(cx + half) + 2):
                if 0 <= x < W and 0 <= y < H and abs(x + 0.5 - cx) <= half:
                    mask[y, x] = True
        for y in range(H):
            for x in range(W):
                if not mask[y, x]:
                    continue
                edge = any(not (0 <= x + i < W and 0 <= y + j < H) or not mask[y + j, x + i] for i, j in ((1, 0), (-1, 0), (0, -1)))
                if edge:
                    a[y, x] = K_OUT
                    continue
                dx = (x + 0.5 - cx) / max(1.0, hw)
                v = -1.2 * dx + (_hash(x, y, seed) - 0.5) * 0.4
                a[y, x] = K_L if v > 0.45 else K_M if v > -0.25 else K_D
                if y >= by - 1:
                    a[y, x] = K_D if v > -0.25 else K_OUT        # wet and dark at the waterline
    return a


# ---------------------------------------------------------------- bayou: cattails (1x2)
def cattails(a, cx, by, seed):
    """a cattail clump: blades from a dark waterline clump, three brown heads on stalks; a is 2 cells tall (top cell overhead)"""
    H, W = a.shape[:2]
    rng = [(_hash(i, 1, seed), _hash(i, 2, seed), _hash(i, 3, seed)) for i in range(14)]
    # the waterline: dark ring + ripples
    for y in range(by - 2, by + 4):
        for x in range(cx - 8, cx + 9):
            if 0 <= x < W and 0 <= y < H:
                q = ((x + 0.5 - cx) / 7.5) ** 2 + ((y + 0.5 - by) / 2.8) ** 2
                if q <= 1.0 and y >= by - 1:
                    a[y, x] = WATER_DK if q < 0.45 else WATER_D
    blades = []
    for i, (h1, h2, h3) in enumerate(rng):
        x0 = cx - 6 + i * 12 / 13.0                 # base spread across 12 px
        lean = (x0 - cx) * 0.3 + (h1 - 0.5) * 0.8
        ln = 8 + int(h2 * 10) + (5 if abs(x0 - cx) < 3 else 0)
        blades.append((x0, lean, ln, h3))
    for x0, lean, ln, h3 in sorted(blades, key=lambda b: b[3]):
        for k in range(ln):
            y = by - k
            x = int(round(x0 + lean * k / 6.0))
            if 0 <= x < W and 0 <= y < H:
                t = k / ln
                a[y, x] = R_DK if k < 2 else (R_L if (t > 0.6 and h3 > 0.45) else R_M if t > 0.25 + 0.3 * h3 else R_D)
                if k > 1 and x + 1 < W and t < 0.35:
                    a[y, x + 1] = R_DK                     # each blade's shaded side at its foot
    for j, (dx, top) in enumerate(((-2, 21), (1, 25), (4, 19))):   # the heads: brown cigars on stalks
        hx = cx + dx
        for k in range(by - top + 8, by - 6):              # stalk
            if 0 <= k < H:
                a[k, hx] = R_D
        for k in range(by - top, by - top + 7):
            for x in (hx - 1, hx, hx + 1):
                if 0 <= k < H and 0 <= x < W:
                    edge = x != hx or k in (by - top, by - top + 6)
                    a[k, x] = K_OUT if (x == hx + 1 or k == by - top + 6) and edge else K_L if (x == hx - 1 and k < by - top + 4) else K_M if x == hx - 1 else K_D
        if 0 <= by - top - 1 < H:
            a[by - top - 1, hx] = R_DK                         # the spike above the head
    return a


# ---------------------------------------------------------------- coast: rocks awash
def rocks(a, stones, seed):
    """rocks in the sea: rounded stones (riprap colours), lit top-left, a darker face at the bottom, outline, a foam ring at the
    waterline and the stone's shadow in the water to the bottom-right"""
    H, W = a.shape[:2]
    owner = -np.ones((H, W), dtype=int)
    for n, (cx, cy, rx, ry) in enumerate(stones):
        for y in range(H):
            for x in range(W):
                q = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if q <= 1.0:
                    owner[y, x] = n
    # water: shadow to the bottom-right, foam round the waterline (the lower half of each stone's rim)
    for y in range(H):
        for x in range(W):
            if owner[y, x] >= 0:
                continue
            near = [owner[y + j, x + i] for i, j in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1))
                    if 0 <= x + i < W and 0 <= y + j < H and owner[y + j, x + i] >= 0]
            sh = any(0 <= x - i < W and 0 <= y - j < H and owner[y - j, x - i] >= 0 for i, j in ((1, 1), (2, 1), (1, 2), (2, 2)))
            if near:
                st = stones[near[0]]
                low = y + 0.5 > st[1] - st[3] * 0.3
                a[y, x] = FOAM if (low and _hash(x // 2, y, seed) < 0.6) else (WATER_D if sh else a[y, x])
            elif sh:
                a[y, x] = WATER_D
            elif any(0 <= x + i < W and 0 <= y + j < H and owner[y + j, x + i] >= 0 for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)) \
                    and _hash(x, y, seed + 9) < 0.03:
                a[y, x] = FOAM                                        # a fleck of spray
    for y in range(H):
        for x in range(W):
            n = owner[y, x]
            if n < 0:
                continue
            cx, cy, rx, ry = stones[n]
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            rim = any(not (0 <= x + i < W and 0 <= y + j < H) or owner[y + j, x + i] != n and (owner[y + j, x + i] < 0 or owner[y + j, x + i] < n)
                      for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if rim:
                a[y, x] = S_O
                continue
            v = -0.65 * dx - 0.8 * dy + (_hash(x, y, seed + n) - 0.5) * 0.35
            face = dy > 0.35                                          # the wet lower face
            a[y, x] = S_D if face and v < 0.2 else S_L if v > 0.75 else S_M if v > -0.35 else S_D
            if face and dy > 0.7 and _hash(x, y, seed + 5) < 0.35:
                a[y, x] = S_O                                         # a wet crack at the foot
    return a


PIECES = {
    # name: (w, h, style, painter, passable cells)
    "knees_1a": (1, 1, "bayou", lambda a: knees(a, [(9.0, 9, 1.6, 5), (5.0, 12, 2.6, 9), (11.5, 13, 2.2, 6)], 1), []),
    "knees_1b": (1, 1, "bayou", lambda a: knees(a, [(4.0, 10, 1.6, 4), (9.5, 12, 2.8, 10), (4.5, 13.5, 1.9, 5)], 2), []),
    "cattails": (1, 2, "bayou", lambda a: cattails(a, 8, 28, 4), [[0, 0]]),
    "rock_1a": (1, 1, "coast", lambda a: rocks(a, [(7.5, 8.5, 5.6, 4.6), (11.8, 11.2, 2.6, 2.0)], 3), []),
    "rock_1b": (1, 1, "coast", lambda a: rocks(a, [(5.0, 7.0, 3.6, 3.0), (10.0, 10.0, 4.2, 3.4), (4.2, 12.4, 2.2, 1.7)], 7), []),
    "rock_ledge": (2, 1, "coast", lambda a: rocks(a, [(6.0, 9.0, 4.6, 3.6), (13.5, 7.5, 5.4, 4.2), (20.5, 9.5, 4.8, 3.8),
                                                   (26.5, 11.0, 3.0, 2.4), (10.5, 12.8, 2.6, 1.8)], 11), []),
}


def build(base=None):
    base = base or water_cell()
    out = {}
    for name, (w, h, style, paint, passable) in PIECES.items():
        a = paint(canvas(w, h, base))
        out[name] = Image.fromarray(a)
    return out, base


def cells_of(name, img):
    w, h = PIECES[name][0], PIECES[name][1]
    return {f"wp_{name}" + ("" if w * h == 1 else f"_{x}{y}"): img.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16))
            for y in range(h) for x in range(w)}


def main(argv):
    pieces, base = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    index = {}
    bpx = np.array(base)
    for name, img in pieces.items():
        w, h, style, _, passable = PIECES[name]
        names = []
        for cn, c in cells_of(name, img).items():
            a = np.array(c)
            same = np.all(a == bpx, axis=-1)
            if [int(cn[-2]), int(cn[-1])] in passable if cn[-2:].isdigit() and w * h > 1 else False:
                # an overhead cell: RGBA, clear where the water shows (drawn over whatever cell is above)
                rgba = np.dstack([a, np.where(same, 0, 255).astype(np.uint8)])
                Image.fromarray(rgba, "RGBA").save(os.path.join(OUT_DIR, cn + ".png"))
            else:
                c.save(os.path.join(OUT_DIR, cn + ".png"))
            names.append(cn)
        cols = sorted({tuple(int(v) for v in p) for p in np.array(img).reshape(-1, 3)})
        index[name] = {"size": [w, h], "style": style, "cells": names, "passable": passable, "base": "ekat:water_C",
                       "colours": [list(c) for c in cols]}
    json.dump({"_comment": "Natural Surf-barrier props (make_water_barriers.py): cells wp_<name>[_<x><y>].png, on ekat:water_C; "
                           "passable = overhead cells (RGBA). Not in any recipe yet.", "pieces": index},
              open(os.path.join(OUT_DIR, "water_props.json"), "w"), indent=1)
    print(f"wrote {len(index)} pieces to {os.path.relpath(OUT_DIR, ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])

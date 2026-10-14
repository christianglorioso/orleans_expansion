"""Own art for the lake trio's spirit pools (legendary lairs batch 2): Uxie's Knowing Pool (reached from the Old Water by
the Canoe Docks' boatman), Mesprit's Heart Pool (off Route 1) and Azelf's Unfailing Spring (off Route 23). One secondary,
gTileset_OrleansLairTrio on gTileset_OrleansGeneral (prefix lt).

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_trio.py
writes tools/mapgen/tilesets/lairs/lair_trio.png + lair_trio.json and recipes_b2/orleans_lair_trio.json (source "lt").

Why not the Rootkin secondary (lk, Celebi's): its seven families already fill its seven palette slots, so the pools' water, the
irises and the three spirit colours would squeeze it. The trio's set keeps the Rootkin look (the same cut stone, cedar and
thatch colours, the shrine's spiral) and is drawn to SEVEN families on purpose (FAMILIES below, one per palette slot).

The three pools are one family of places: a spring in a ring of Rootkin cut stone, the spirit's standing stone at its head with
a spiral inlaid in the spirit's colour (Uxie yellow, Mesprit pink, Azelf blue), each in its own country.
    shared   spring_<key>   a spring pool in a kerb of cut stone on grass (deep, clear, the kerb's shadow on the water)
             spirit_uxie / spirit_mesprit / spirit_azelf 1x2   the spirit's standing stone, its spiral inlaid and glowing
             step_pool      stepping stones across the pool (walkable)
             fog_pool0/1    mist lying on the pool
             lotus_y / lotus_p / lotus_pads   American lotus (yellow, Mesprit's pink) and bare pads on the pool
    uxie     walk_pool / walk_grass / walk_water / walk_end   a Rootkin rope-and-plank walk: across the pool, over the grass, over the
             canoe channel, its end posts at the moored pirogue (all walkable); pirogue 2x1 (moored, blocking)
             story_post 1x2 (a cedar post carved in rings of glyphs, knotted memory cords hanging from it), cords 1x1 (memory cords
             strung between posts), telling_stone 2x2 (the broad stone the tellers sit before, Uxie's spiral), reading_stone 2x1
    mesprit  iris_violet / iris_red / iris_yellow 1x1   Louisiana irises (walkable), garland_post 1x2 (a cedar post wound with
             iris garlands and ribbons)
    azelf    (revision 2: Azelf's lair is dry country, so its pieces are placed in the Route 23 set, make_lair_field.py, which draws
             them with this module's spring_style, spirit_stone, boil, cairn and split_rock)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import (GRASS, WATER, Canvas, Pieces, dual_set, ellipse_body, fill_body, gba, hashn, ink_outline,  # noqa: E402
                         over, write_b2)

# ---------------------------------------------------------------- colours (the primary's grass and water first)
G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
WA = (96, 136, 136)                                                  # the primary's open water (the canoe channel)
PW0, PW1, PW2, PW3 = (40, 72, 80), (56, 96, 104), (80, 128, 128), (152, 200, 192)   # the spring: deep, clear
ST2, ST3, ST4, INK, MO = (128, 128, 112), (168, 168, 144), (208, 208, 184), (40, 40, 48), (80, 112, 64)
FOG1, FOG2 = (176, 192, 184), (216, 224, 216)
STEM, LF2, LF3 = (64, 112, 56), (72, 112, 56), (104, 144, 72)
FY, FW1, FP, FPD = (232, 200, 96), (248, 248, 232), (232, 160, 176), (184, 104, 128)
LOTP = (248, 232, 160)                                               # the yellow lotus' pale petals
IV1, IV2, IR1, IR2 = (152, 120, 216), (104, 72, 168), (216, 88, 56), (152, 48, 40)  # Louisiana irises: violet, copper-red
UX1, UX2, MS1, MS2, AZ1, AZ2 = (248, 224, 96), (200, 160, 40), (248, 168, 200), (208, 96, 144), (128, 184, 248), (64, 104, 208)
WD1, WD2, WD3 = (72, 56, 40), (112, 88, 56), (152, 120, 80)          # weathered planks, the pirogue
TH, TH_D = (184, 152, 88), (144, 120, 64)                            # rope (the Rootkin thatch colours)
CE1, CE2, CE3, CE4 = (96, 56, 40), (136, 80, 56), (176, 112, 72), (216, 168, 72)   # cedar (the Oldest Shrine's posts)
TEAL, ORNG = (64, 152, 152), (224, 120, 48)                          # the Rootkin bands
DH, D1, D2, D3, CRK = (240, 224, 184), (224, 200, 144), (200, 168, 112), (160, 128, 88), (120, 88, 56)

FAMILIES = {   # one per palette slot (7)
    "POOL": [G, GD, GL, SH, PW0, PW1, PW2, PW3, ST2, ST3, ST4, INK, MO, FOG1, FOG2],
    "FLOWERS": [G, GD, GL, SH, STEM, LF2, LF3, IV1, IV2, IR1, IR2, FY, FW1, FP, FPD],
    "LOTUS": [PW0, PW1, PW2, PW3, STEM, LF2, LF3, FY, LOTP, FP, FPD, FW1, INK, ST3, ST4],
    "SPIRIT": [ST2, ST3, ST4, INK, G, GD, SH, FW1, UX1, UX2, MS1, MS2, AZ1, AZ2, GL],
    "WOOD": [WD1, WD2, WD3, TH, INK, G, GD, GL, SH, PW0, PW1, PW2, WA, ST2, ST3],
    "CEDAR": [CE1, CE2, CE3, CE4, G, GD, GL, SH, INK, TEAL, ORNG, FP, FW1, FY, IV1],
    "DRY": [G, GD, GL, SH, DH, D1, D2, D3, CRK, ST2, ST3, ST4, INK, STEM, LF3],
}


def grass_cv(w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, GRASS(i, j))
    return cv


def pool_tex(i, j):
    """Open spring water (away from the kerb): clear, a few slow ripples and glints."""
    if (i * 3 + j * 5) % 23 == 0 or ((i + 2 * j) % 17 == 0 and j % 4 == 1):
        return PW2
    if hashn(i, j, 401) < 0.012:
        return PW3
    return PW1


def pool_cv():
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, pool_tex(i, j))
    return cv


# ---------------------------------------------------------------- the spring pool set
def spring_style(i, j, inside, d):
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1:
            return SH if (d["ds"] == 1 or d["de"] == 1) else GD          # the kerb's foot in the grass
        return GRASS(i, j)
    if near == 1:
        return INK
    if near <= 4:
        # the kerb's top: dressed blocks, lit from the north-west, a joint every 7 px along the run
        along = j if (d["dw"] == near or d["de"] == near) else i
        if along % 7 == 0 and near in (2, 3):
            return ST2
        lit_side = d["dn"] == near or d["dw"] == near
        if near == 2:
            return ST4 if lit_side else ST3
        return ST3 if lit_side else ST2
    if near == 5:
        return ST2 if (i * 3 + j) % 11 else MO                          # its inner face, a little moss
    if near == 6:
        return INK                                                      # the waterline
    if (d["dn"] is not None and d["dn"] <= 8) or (d["dw"] is not None and d["dw"] <= 7):
        return PW0 if (i + j) % 3 else PW1                              # the kerb's shadow on the water
    return pool_tex(i, j)


# ---------------------------------------------------------------- shared props
def spirit_stone(which):
    """1x2 the spirit's standing stone: a tall rough menhir of pale stone (the Oldest Shrine's kind), leaning a little, a large
    spiral cut into its face and inlaid in the spirit's colour, glowing; a ring of the colour in the grass at its foot (Uxie
    yellow, Mesprit pink, Azelf blue)."""
    c1, c2 = {"uxie": (UX1, UX2), "mesprit": (MS1, MS2), "azelf": (AZ1, AZ2)}[which]
    cv = grass_cv(1, 2)
    body = set()
    for j in range(1, 29):
        t = (j - 1) / 27.0
        hw = 2.2 + 3.6 * min(1.0, t * 2.2) - 0.6 * t + 0.6 * math.sin(j * 0.9 + len(which))
        cx = 8.3 - 1.4 * (1 - t)                                         # leaning west at the top
        for i in range(16):
            if abs(i + 0.5 - cx) <= hw:
                body.add((i, j))
    for (x, y) in body:
        left = (x - 1, y) not in body or (x - 2, y) not in body
        right = (x + 1, y) not in body or (x + 2, y) not in body
        c = ST4 if left else (ST2 if right else ST3)
        if (x * 5 + y * 3) % 17 == 0:
            c = ST2
        cv.put(x, y, c)
    ink_outline(cv, body, INK, only_clear=False)
    sp = [(8, 13), (9, 13), (9, 14), (8, 15), (7, 15), (6, 14), (6, 13), (6, 12), (7, 11), (8, 11), (9, 11), (10, 12),
          (10, 13), (10, 14), (10, 15), (10, 16), (9, 17), (8, 17), (7, 17), (6, 17), (5, 16), (5, 15), (5, 14), (5, 13),
          (5, 12), (5, 11), (6, 10), (7, 9)]
    for k, (x, y) in enumerate(sp):
        cv.put(x, y + 1, c2 if k > 15 else c1)
    cv.put(8, 15, FW1)
    cv.put(7, 4, c1)
    cv.put(7, 3, FW1)
    # the glow ring in the grass at its foot
    for i in range(1, 15):
        if cv.get(i, 29) != INK:
            cv.put(i, 29, SH)
        if i % 2 and cv.get(i, 30) != INK:
            cv.put(i, 30, c1 if i in (3, 7, 11) else GL)
    return cv


def step_pool(ground=None):
    """1x1 three flat stepping stones across the pool (walkable); over a kerb cell when `ground` is that cell's canvas."""
    cv = pool_cv() if ground is None else ground.copy()
    for (x, y, rx, ry) in [(4.5, 4.5, 3.6, 2.6), (11.5, 8.5, 3.6, 2.6), (5.5, 13.0, 3.4, 2.3)]:
        b = ellipse_body(x, y, rx, ry)
        fill_body(cv, {(i, j) for (i, j) in b if 0 <= i < 16 and 0 <= j < 16},
                  lambda i, j, x=x, y=y: ST4 if j < y - 0.5 else (ST3 if j < y + 1 else ST2))
        for i in range(16):
            for j in range(16):
                if (i, j - 1) in b and (i, j) not in b:
                    cv.put(i, j, PW0)                                    # each stone's shadow on the water
    return cv


def fog_pool(variant):
    """1x1 wisps of mist lying on the pool: long soft streaks, dense in the middle, dithered at their ends."""
    cv = pool_cv()
    wisps = [(8 + variant * 3, 5 - variant, 9.0, 1.8), (4 - variant * 2, 11 + variant, 7.0, 1.4), (15 - variant * 6, 14, 6.0, 1.1)]
    for (cx, cy, rx, ry) in wisps:
        for j in range(16):
            for i in range(-8, 24):
                v = ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2
                ii = i % 16
                if v < 0.35:
                    cv.put(ii, j, FOG2)
                elif v < 0.75 and (i + j) % 2 == 0:
                    cv.put(ii, j, FOG2 if v < 0.5 else FOG1)
                elif v < 1.0 and (i + 2 * j) % 4 == 0:
                    cv.put(ii, j, FOG1)
    return cv


def lotus(kind):
    """1x1 American lotus on the pool: broad round pads standing just off the water, (a bloom: yellow / pink)."""
    cv = pool_cv()
    for (x, y, r) in [(4.5, 10.5, 3.6), (11.5, 12.5, 3.0), (11.0, 4.5, 3.3)]:
        b = ellipse_body(x, y, r, r * 0.72)
        for (i, j) in b:
            if 0 <= i < 16 and 0 <= j < 16:
                c = LF3 if (i - x) + (j - y) < -1 else LF2
                if abs(i + 0.5 - x) < 0.6 or abs(j + 0.5 - y) < 0.5 and i > x:
                    c = STEM                                             # the veins
                cv.put(i, j, c)
        for i in range(16):
            for j in range(16):
                if (i, j - 1) in b and (i, j) not in b and 0 <= i < 16 and 0 <= j < 16:
                    cv.put(i, j, PW0)
    if kind in ("y", "p"):
        a, b2 = (LOTP, FY) if kind == "y" else (FP, FPD)
        cx, cy = 6, 4
        for (dx, dy, c) in [(-2, 0, a), (2, 0, a), (-1, -2, a), (1, -2, a), (0, -3, a), (-1, -1, a), (1, -1, a), (0, -1, FW1),
                            (-2, 1, b2), (2, 1, b2), (-1, 1, b2), (1, 1, b2), (0, 1, b2), (0, 0, FY if kind == "y" else FW1)]:
            cv.put(cx + dx, cy + dy, c)
        cv.put(cx - 3, cy + 1, INK)
        cv.put(cx + 3, cy + 1, INK)
        cv.hline(cx - 2, cx + 2, cy + 2, INK)
        cv.vline(cx, cy + 3, cy + 5, STEM)
    return cv


# ---------------------------------------------------------------- the rope-and-plank walk (Uxie)
def walk(ground):
    """1x1 a Rootkin rope-and-plank walk running north-south, three planks wide, its boards lashed with rope, over the
    ground: 'pool' (spring water), 'grass', 'water' (the canoe channel), 'end' (over the channel, two mooring posts)."""
    if isinstance(ground, Canvas):
        cv, ground = ground.copy(), "pool"
    elif ground == "pool":
        cv = pool_cv()
    elif ground == "grass":
        cv = grass_cv()
    else:
        cv = Canvas(1, 1)
        for j in range(16):
            for i in range(16):
                cv.put(i, j, WA)
    for j in range(16):
        for i in range(2, 14):
            c = WD3 if j % 4 == 0 else (WD1 if j % 4 == 3 else WD2)
            if i in (2, 13):
                c = WD1
            if (i * 7 + (j // 4) * 5) % 13 == 0 and j % 4 in (1, 2):
                c = WD1                                                  # knots and gaps
            cv.put(i, j, c)
        cv.put(1, j, INK)
        cv.put(14, j, INK)
    for j in (1, 9):
        for i in (3, 12):
            cv.put(i, j, TH)                                             # the rope lashings
            cv.put(i, j + 1, WD1)
    if ground != "grass":
        for j in range(16):
            cv.put(15, j, PW0 if ground == "pool" else WA)
            if j % 3 == 0:
                cv.put(15, j, PW0 if ground == "pool" else PW2)          # the walk's shadow / a ripple on the water
    if ground == "end":
        for x in (0, 13):
            cv.rect(x, 2, 3, 13, WD2)
            cv.vline(x, 2, 14, WD3)
            cv.vline(x + 2, 2, 14, WD1)
            cv.hline(x, x + 2, 1, INK)
            cv.hline(x, x + 2, 15, INK)
            cv.put(x + 1, 6, TH)
            cv.put(x + 1, 7, WD1)
    return cv


def pirogue():
    """2x1 a Rootkin pirogue moored across the end of the walk: a long, low dugout of dark cypress, a pole laid in it."""
    cv = Canvas(2, 1)
    for j in range(16):
        for i in range(32):
            cv.put(i, j, WA)
    body = set()
    for i in range(1, 31):
        t = (i - 15.5) / 15.0
        hw = 4.6 * (1 - t ** 4)
        for j in range(16):
            if abs(j + 0.5 - 8) <= hw:
                body.add((i, j))
    for (i, j) in body:
        c = WD2 if j < 8 else WD1
        if j <= 8 - 3 or j >= 8 + 3:
            c = WD3 if j < 8 else WD1
        cv.put(i, j, c)
    for i in range(4, 28):
        for j in range(6, 10):
            if (i, j) in body:
                cv.put(i, j, WD1 if (i + j) % 5 else INK)                 # the hollow
    cv.line(3, 7, 29, 9, TH)                                             # the pole
    ink_outline(cv, body, INK, only_clear=False)
    for i in range(2, 30):
        if (i, 15) not in body:
            cv.put(i, 14 if (i, 14) not in body else 15, PW1)            # its shadow on the water
    return cv


# ---------------------------------------------------------------- Uxie's props
def story_post():
    """1x2 a memory post: a cedar post carved in rings of glyphs (each ring a remembered telling), its cap carved as a closed
    eye (Uxie's), knotted memory cords hanging from a peg."""
    cv = grass_cv(1, 2)
    body = {(i, j) for j in range(4, 30) for i in range(5, 11)}
    for (i, j) in body:
        c = CE3
        if i == 5:
            c = CE4
        elif i >= 9:
            c = CE2
        if j % 5 == 0:
            c = CE1                                                      # the ring grooves
        elif j % 5 == 2 and (i + j) % 3 == 0:
            c = CE1                                                      # glyphs
        cv.put(i, j, c)
    for (i, j) in [(i, j) for j in range(1, 5) for i in range(4, 12) if abs(i + 0.5 - 8) <= 4 - (4 - j) * 0.7]:
        cv.put(i, j, CE4 if j < 3 else CE3)
        body.add((i, j))
    cv.hline(6, 9, 3, CE1)                                               # the closed eye on the cap
    cv.put(7, 4, CE1)
    cv.put(8, 4, CE1)
    ink_outline(cv, body, INK, only_clear=False)
    # the memory cords from a peg on its east side
    cv.hline(11, 13, 9, CE1)
    for (x, n, col) in [(12, 9, FY), (13, 7, TEAL), (14, 10, ORNG)]:
        for k in range(n):
            cv.put(x, 10 + k, col if k % 3 else CE4)                     # knots
    for i in range(4, 13):
        cv.put(i, 30, SH)
    return cv


def cords():
    """1x1 memory cords strung between two posts: a line sagging east-west, knotted cords hanging in the spirit's yellow,
    the Rootkin teal and orange."""
    cv = grass_cv()
    for i in range(16):
        y = 3 + round(2.2 * math.sin(math.pi * i / 15))
        cv.put(i, y, CE4)
        cv.put(i, y + 1, CE1 if i % 2 else CE2)
        if i % 3 == 1:
            col = [FY, TEAL, ORNG, FW1][(i // 3) % 4]
            n = 5 + (i * 7) % 4
            for k in range(n):
                cv.put(i, y + 2 + k, col if k % 3 != 2 else CE4)
            cv.put(i, y + 2 + n, SH)
    return cv


def telling_stone():
    """2x2 the telling stone: a broad, low boulder dressed flat on top, Uxie's spiral cut into its face and inlaid in yellow,
    worn smooth where generations sat before it."""
    cv = grass_cv(2, 2)
    body = set()
    for j in range(4, 28):
        for i in range(2, 30):
            v = ((i + 0.5 - 16) / 14.0) ** 2 + ((j + 0.5 - 16) / 12.5) ** 4
            if v <= 1.0:
                body.add((i, j))
    for (i, j) in body:
        top = j < 12
        c = ST4 if top and i < 20 else (ST3 if top else ST2)
        if not top and i < 8:
            c = ST3
        if top and (i + j) % 9 == 0:
            c = ST3
        cv.put(i, j, c)
    cv.hline(4, 27, 12, ST3)
    sp = [(16, 18), (17, 18), (17, 19), (16, 20), (15, 20), (14, 19), (14, 18), (14, 17), (15, 16), (16, 16), (17, 16),
          (18, 17), (18, 18), (18, 19), (18, 20), (17, 21), (16, 22), (15, 22), (14, 22), (13, 21), (12, 20), (12, 19)]
    for k, (x, y) in enumerate(sp):
        cv.put(x, y, UX2 if k > 14 else UX1)
    cv.put(16, 19, FW1)
    ink_outline(cv, body, INK, only_clear=False)
    for i in range(4, 29):
        if cv.get(i, 28) != INK:
            cv.put(i, 28, SH)
        cv.put(i, 29, SH if 6 < i < 26 else GD)
    return cv


def reading_stone():
    """2x1 a long low stone where the listeners sit, its top worn smooth."""
    cv = grass_cv(2, 1)
    body = {(i, j) for j in range(5, 13) for i in range(3, 29) if not ((i in (3, 28)) and j in (5, 12))}
    for (i, j) in body:
        cv.put(i, j, ST4 if j < 8 else (ST3 if j < 11 else ST2))
    ink_outline(cv, body, INK, only_clear=False)
    for i in range(4, 29):
        cv.put(i, 14, SH)
    return cv


# ---------------------------------------------------------------- Mesprit's props
def iris(kind):
    """1x1 a clump of Louisiana irises: sword leaves, two or three flowers (violet, copper-red, yellow), walkable."""
    hi, lo = {"violet": (IV1, IV2), "red": (IR1, IR2), "yellow": (FY, IR2)}[kind]
    cv = grass_cv()
    for (x0, lean, h) in [(4, -1, 11), (6, 0, 13), (8, 1, 12), (10, 2, 10), (12, 1, 9)]:
        for k in range(h):
            x = x0 + round(lean * k / h * 2)
            cv.put(x, 15 - k, STEM if k < h - 3 else LF3)
            if k < h // 2:
                cv.put(x + 1, 15 - k, LF2)
    for (x, y) in [(5, 4), (10, 6), (7, 8)]:
        for (dx, dy, c) in [(0, 0, FW1 if kind != "yellow" else FY), (-1, 0, hi), (1, 0, hi), (0, -1, hi), (-2, 1, lo), (2, 1, lo),
                            (-1, 1, lo), (1, 1, lo), (0, 1, FY)]:
            cv.put(x + dx, y + dy, c)
    return cv


def garland_post():
    """1x2 a cedar post wound with a garland of irises and spider lilies, ribbons in the Rootkin teal and orange tied below, a
    pink heart-shaped token hung at the top (Mesprit's)."""
    cv = grass_cv(1, 2)
    body = {(i, j) for j in range(3, 30) for i in range(6, 10)}
    for (i, j) in body:
        cv.put(i, j, CE4 if i == 6 else (CE2 if i == 9 else CE3))
    ink_outline(cv, body, INK, only_clear=False)
    for k in range(22):                                                  # the garland spiralling down
        y = 5 + k
        x = 6 + round(2.6 * math.sin(k * 0.75))
        cv.put(x, y, SH if k % 3 else FP)
        if k % 3 == 0:
            cv.put(x + (1 if x < 8 else -1), y, [IV1, FP, FW1, FY][(k // 3) % 4])
    for (x, n, col) in [(4, 7, TEAL), (11, 8, ORNG), (5, 5, ORNG), (10, 6, TEAL)]:
        for k in range(n):
            cv.put(x + (k % 4 == 3), 18 + k, col)                        # ribbons fluttering
    for (dx, dy) in [(-1, 0), (1, 0), (-2, -1), (-1, -1), (1, -1), (2, -1), (0, 1), (-1, 0), (0, 0)]:
        cv.put(8 + dx, 2 + dy, FP)                                       # the heart token
    cv.put(8, 1, FW1)
    for i in range(5, 11):
        cv.put(i, 30, SH)
    return cv


# ---------------------------------------------------------------- Azelf's props
def _crack(i, j):
    """A crazed crack network: jittered seed points every 6 px, a crack where the two nearest seeds are nearly equidistant."""
    best = []
    for gy in range(j // 6 - 1, j // 6 + 2):
        for gx in range(i // 6 - 1, i // 6 + 2):
            px = gx * 6 + 0.5 + 5 * hashn(gx, gy, 441)
            py = gy * 6 + 0.5 + 5 * hashn(gx, gy, 442)
            best.append((px - i - 0.5) ** 2 + (py - j - 0.5) ** 2)
    best.sort()
    return best[1] ** 0.5 - best[0] ** 0.5


def dry_style(i, j, inside, d):
    """Cracked dry earth pressing in on the grass (inside = dry): the drought outside the grove."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1 and (i + j) % 2 == 0:
            return SH
        if near == 2 and (i * 3 + j) % 5 == 0:
            return D2                                                    # dust blown onto the grass
        return GRASS(i, j)
    if near == 1:
        return D3 if (i + j) % 2 else D2
    k = _crack(i + 32, j + 32)
    if k < 0.32:
        return CRK if hashn(i, j, 433) < 0.5 else D3
    if k < 0.75:
        return D3 if (i + j) % 2 else D2
    if k > 3.2 and hashn(i, j, 431) < 0.25:
        return DH                                                        # the plates' sun-bleached middles
    return D1


def boil():
    """1x1 the spring's eye: water welling up through white sand, rings spreading on the pool, a few bubbles (blocking)."""
    cv = pool_cv()
    for (r, c) in [(7.2, PW2), (5.4, PW1), (4.0, PW3), (2.6, FOG2), (1.4, FOG1)]:
        for j in range(16):
            for i in range(16):
                v = ((i + 0.5 - 8) / r) ** 2 + ((j + 0.5 - 8) / (r * 0.75)) ** 2
                if v <= 1.0 and (c != PW2 or v > 0.82):
                    cv.put(i, j, c)
    for (x, y) in [(6, 7), (9, 8), (8, 6), (10, 7)]:
        cv.put(x, y, PW3)
    cv.put(7, 8, ST4)
    return cv


def cairn(on_dry):
    """1x1 a cairn: flat stones stacked by those who came for the will to go on."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, (D1 if hashn(i, j, 433) > 0.15 else D2) if on_dry else GRASS(i, j))
    body = set()
    for (cx, cy, rx, ry) in [(8, 13, 5.5, 2.4), (8, 10, 4.6, 2.0), (7.5, 7, 3.6, 1.8), (8.5, 4.3, 2.6, 1.6), (8, 2, 1.6, 1.1)]:
        b = ellipse_body(cx, cy, rx, ry)
        for (i, j) in b:
            cv.put(i, j, ST4 if j < cy - 0.4 else (ST3 if j < cy + 0.8 else ST2))
        body |= b
    ink_outline(cv, body, INK, only_clear=False)
    for i in range(3, 14):
        if cv.get(i, 15) != INK:
            cv.put(i, 15, D3 if on_dry else SH)
    return cv


def split_rock():
    """2x2 a boulder split clean in two by a sapling that grew through it: the stubbornest thing in the grove."""
    cv = grass_cv(2, 2)
    body = set()
    for j in range(6, 28):
        for i in range(2, 30):
            v = ((i + 0.5 - 16) / 13.5) ** 2 + ((j + 0.5 - 18) / 10.0) ** 2
            if v <= 1.0 and not (15 <= i <= 16 and j >= 9):
                body.add((i, j))
    for (i, j) in body:
        c = ST3
        if j < 13:
            c = ST4
        if i > 22 or j > 22:
            c = ST2
        cv.put(i, j, c)
    ink_outline(cv, body, INK, only_clear=False)
    for j in range(9, 28):
        cv.put(15, j, INK)
        cv.put(16, j, INK if j % 3 else CRK)                             # the split
    # the sapling rising out of the split
    cv.vline(16, 1, 14, CRK)
    cv.vline(15, 4, 14, D3)
    for (x, y, r) in [(16, 3, 3.2), (12, 5, 2.4), (20, 5, 2.6), (14, 1.5, 1.8), (19, 2, 1.8)]:
        for (i, j) in ellipse_body(x, y, r, r * 0.8):
            if 0 <= j < 32:
                cv.put(i, j, LF3 if (i + j) % 3 else STEM)
    for i in range(4, 29):
        if cv.get(i, 28) != INK:
            cv.put(i, 28, SH)
    return cv


def fern():
    """1x1 a clump of ferns: arching fronds with paired leaflets (walkable)."""
    cv = grass_cv()
    for (ang, ln) in [(-2.3, 7), (-1.9, 8), (-1.3, 8), (-0.8, 7), (-2.7, 6), (-0.4, 6)]:
        x, y = 8.0, 13.0
        for k in range(ln):
            x += math.cos(ang)
            y += math.sin(ang) + k * 0.08
            xi, yi = int(round(x)), int(round(y))
            cv.put(xi, yi, STEM if k < 2 else (LF2 if k < ln - 2 else LF3))
            if k % 2 == 0:
                cv.put(xi, yi - 1, LF3 if k < ln - 2 else GL)
                cv.put(xi + (1 if math.cos(ang) > 0 else -1), yi + 1, STEM)
    cv.put(8, 13, STEM)
    cv.put(7, 13, STEM)
    return cv


def tuft(on_dry):
    """1x1 tufts of wiry grass holding on (walkable): on the cracked earth, or pebbles in the grass."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, (D1 if hashn(i, j, 451) > 0.1 else D2) if on_dry else GRASS(i, j))
    if on_dry:
        for (x0, y0) in [(4, 12), (11, 9), (8, 4)]:
            for (dx, h) in [(-2, 3), (-1, 4), (0, 5), (1, 4), (2, 3)]:
                for k in range(h):
                    cv.put(x0 + dx + (k > 2) * (1 if dx > 0 else -1 if dx < 0 else 0), y0 - k, LF3 if k > 1 else STEM)
            cv.hline(x0 - 3, x0 + 3, y0 + 1, D3)
    else:
        for (x, y) in [(3, 4), (11, 3), (6, 11), (13, 12), (9, 7)]:
            cv.put(x, y, ST4)
            cv.put(x + 1, y, ST3)
            cv.put(x, y + 1, ST2)
            cv.put(x + 1, y + 1, SH)
    return cv


# ---------------------------------------------------------------- the sheet
def build():
    P = Pieces("lt")
    P.add_set("spring", dual_set(spring_style, ro=7, ri=5, wob=0), walk=False,
              comment="a spring pool in a kerb of Rootkin cut stone (blocking)", lair="uxie mesprit azelf")
    P.add("spring_C2", pool_cv(), comment="open spring water (variant)", lair="uxie mesprit azelf")
    for w in ("uxie", "mesprit"):
        P.add(f"spirit_{w}", spirit_stone(w), comment=f"1x2 {w}'s standing stone, its spiral glowing, blocking", lair=w)
    P.add("step_pool", step_pool(), walk=True, comment="1x1 stepping stones across the pool (walkable)", lair="mesprit")
    sp = dual_set(spring_style, ro=7, ri=5, wob=0)
    P.add("step_spring_S", step_pool(sp["S"]), walk=True, comment="1x1 the stepping stones' first stone on the kerb (south)",
          lair="mesprit")
    P.add("fog_pool0", fog_pool(0), comment="1x1 mist on the pool", lair="uxie")
    P.add("fog_pool1", fog_pool(1), comment="1x1 mist on the pool", lair="uxie")
    P.add("lotus_y", lotus("y"), comment="1x1 yellow American lotus on the pool, blocking", lair="uxie mesprit")
    P.add("lotus_p", lotus("p"), comment="1x1 a pink lotus (Mesprit's), blocking", lair="mesprit")
    P.add("lotus_pads", lotus(""), comment="1x1 lotus pads, blocking", lair="uxie mesprit")
    # Uxie
    for g in ("grass", "water", "end"):
        P.add(f"walk_{g}", walk(g), walk=True, comment=f"1x1 the rope-and-plank walk over {g}", lair="uxie")
    spring = dual_set(spring_style, ro=7, ri=5, wob=0)
    for k in ("C", "N", "S"):
        P.add(f"walk_spring_{k}", walk(spring[k]), walk=True, comment=f"1x1 the walk across the pool (over spring_{k})", lair="uxie")
    P.add("pirogue", pirogue(), comment="2x1 a pirogue moored at the walk's end, blocking", lair="uxie")
    P.add("story_post", story_post(), comment="1x2 a memory post (carved glyph rings, knotted cords), blocking", lair="uxie")
    P.add("cords", cords(), comment="1x1 memory cords strung between posts, blocking", lair="uxie")
    P.add("telling_stone", telling_stone(), comment="2x2 the telling stone, Uxie's spiral, blocking", lair="uxie")
    P.add("reading_stone", reading_stone(), comment="2x1 a long stone seat, blocking", lair="uxie")
    # Mesprit
    for k in ("violet", "red", "yellow"):
        P.add(f"iris_{k}", iris(k), walk=True, comment=f"1x1 Louisiana irises ({k}), walkable", lair="mesprit")
    P.add("garland_post", garland_post(), comment="1x2 a cedar post wound with garlands and ribbons, blocking", lair="mesprit")
    # (Azelf's pieces moved to the Route 23 set, make_lair_field.py, in revision 2: they are drawn here, placed there)
    P.add("fern", fern(), walk=True, comment="1x1 ferns (walkable)", lair="uxie mesprit")
    P.add("pebbles", tuft(False), walk=True, comment="1x1 pebbles in the grass (walkable)", lair="uxie")
    return P


def main():
    P = build()
    bad = write_b2(P, "lair_trio.png", "orleans_lair_trio", "gTileset_OrleansLairTrio", "orleans_general.mapping.json",
                   FAMILIES, "The lake trio's spirit pools (Uxie, Mesprit, Azelf)", "make_lair_trio.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_trio: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

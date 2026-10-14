"""Own art for three green lairs (legendary lairs batch 2), one secondary: gTileset_OrleansLairWoods on gTileset_OrleansGeneral (prefix lj).
    Zarude    the Deep Wood off Route 13: old-growth cypress and tupelo, black water, lianas
    Ogerpon   the Courir glade off Route 13: where the Courir de Mardi Gras riders leave their masks
    Tornadus  the Wind's Eye off Route 3: a chenier (a shell ridge of live oaks) where every tree leans one way

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_woods.py
writes tools/mapgen/tilesets/lairs/lair_woods.png + lair_woods.json and recipes_b2/orleans_lair_woods.json (source "lj").

A new secondary: the batch-1 green sets are full (the wet set has no palette room, the Rootkin set's seven families fill its slots).
Grass, marsh, mud, water, cypress and the swamp canopy wall come from the primary; seven families below, one per palette slot.
    zarude    great_cypress 4x4 (a giant buttressed cypress, its hollow a bower of woven vines), lianas 1x2, palmetto 1x1,
              log_bridge_N / _C / _S (a fallen trunk across the slough, walkable), mossy_log 2x1, larder 1x1 (wild fruit on leaves)
    ogerpon   dance_<key> (the trampled dance ring), mask_teal 1x2 (the Teal Mask on its stake: a painted wire-screen face, a yarn
              beard, a tall capuchon), stake_blue / stake_red / stake_grey 1x2 (empty stakes, ribbons in the colours of the Wellspring,
              Hearthflame and Cornerstone masks, waiting for them), workbench 2x1, costumes 2x1 (fringed Courir costumes drying on
              a line), gumbo_pot 1x1
    tornadus  wind_oak 3x3 (a live oak shorn and swept east by the wind), shell_<key> (the chenier's crushed-shell ridge on grass),
              comb_h / comb_v / comb_a / comb_b (grass combed flat by the wind, four ways round the eye; walkable), weathervane 1x2,
              chimes 1x2 (shell chimes streaming from a driftwood post), sea_oats 1x1 (walkable)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import (GRASS, WATER, Canvas, Pieces, dual_set, ellipse_body, hashn, ink_outline, pcell, tex_from,  # noqa: E402
                         write_b2)

MARSH = tex_from(pcell("ekat:marsh_C"))
TALL = tex_from(pcell("ekat:tallgrass"))                          # the deep wood's floor (Zarude's lair is tall grass)
G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
MG, MGL = (120, 168, 128), (144, 184, 152)                       # the primary's marsh greens
WA = (96, 136, 136)
INK = (40, 40, 48)
# the swamp canopy's colours, the cypress bark
S_OUT, C_DK, C_MID, C_HL = (40, 56, 40), (64, 96, 64), (80, 112, 104), (104, 152, 120)
BK0, BK1, BK2, BK3 = (56, 40, 32), (96, 72, 56), (136, 104, 80), (176, 144, 112)
MOSSG = (152, 168, 144)                                          # Spanish moss
FRU1, FRU2 = (96, 48, 112), (168, 72, 104)                       # muscadines, mayhaws
# the masks and the Courir
TL1, TL2, TL3 = (88, 200, 184), (48, 152, 144), (24, 96, 96)     # the Teal Mask
YN1, YN2 = (232, 216, 96), (168, 160, 56)                        # its yarn beard and the capuchon's trim
BL1, BL2, RD1, RD2, GY1, GY2 = (88, 136, 232), (48, 80, 176), (232, 88, 56), (168, 40, 40), (176, 168, 152), (112, 104, 96)
PU1 = (136, 72, 168)
WD1, WD2, WD3 = (88, 64, 48), (136, 104, 72), (184, 152, 104)    # stakes, the bench
# the chenier
OK = [(88, 128, 80), (72, 104, 64), (56, 80, 56), (168, 200, 136), (112, 152, 80)]   # live oak leaves (the Oldest Shrine's)
OB = [(160, 120, 80), (120, 88, 64), (80, 64, 48)]               # live oak bark
SHL1, SHL2, SHL3 = (240, 232, 216), (216, 208, 184), (176, 168, 144)   # crushed shell
OAT1, OAT2 = (216, 192, 120), (176, 152, 88)                     # sea oats
FE1, FE2 = (112, 120, 128), (64, 72, 80)                         # iron (the vane, the pot)

FAMILIES = {
    "FOREST": [G, GD, GL, SH, MG, MGL, S_OUT, C_DK, C_MID, C_HL, BK0, BK1, BK2, MOSSG, INK],
    "SLOUGH": [WA, G, GD, GL, SH, MG, BK0, BK1, BK2, BK3, MOSSG, C_DK, FRU1, FRU2, INK],
    "MASK": [G, GD, GL, SH, TL1, TL2, TL3, YN1, YN2, WD1, WD2, WD3, INK, (248, 248, 232), C_DK],
    "RIBBON": [G, GD, GL, SH, BL1, BL2, RD1, RD2, GY1, GY2, PU1, YN1, WD1, WD2, INK],
    "OAK": [G, GD, GL, SH] + OK + OB + [(48, 40, 32), MOSSG],
    "SHELL": [G, GD, GL, SH, SHL1, SHL2, SHL3, OAT1, OAT2, FE1, FE2, INK, WD1, WD2, (248, 248, 232)],
    "BENCH": [G, GD, GL, SH, WD1, WD2, WD3, TL1, TL2, RD1, BL1, FE1, FE2, INK, YN1],
}


def ground(fn, w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, fn(i, j))
    return cv


# ---------------------------------------------------------------- Zarude
def litter_tex(i, j):
    """The deep wood's floor: leaf litter in the canopy's shade, a few sun-flecks."""
    n = hashn(i, j, 631)
    m = hashn(i // 3, j // 2, 632)
    if n < 0.05:
        return BK1
    if m < 0.3:
        return C_DK
    if m > 0.86 and n > 0.5:
        return G
    return SH if n > 0.35 else GD


def litter_style(i, j, inside, d):
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        return SH if near == 1 and (i + j) % 2 == 0 else GRASS(i, j)
    if near == 1 and (i + j) % 2:
        return GD
    return litter_tex(i, j)

def on_tall(cv):
    """The same piece over the deep wood's tall grass instead of the plain grass (every plain-grass pixel replaced)."""
    out = cv.copy()
    g = {G, GD, GL}
    for j in range(out.h):
        for i in range(out.w):
            c = out.get(i, j)
            if c in g and GRASS(i, j) == c:
                out.put(i, j, TALL(i, j))
    return out


def great_cypress():
    """4x4 a giant old-growth cypress: the trunk rising out of the top into the canopy, Spanish moss and lianas hanging from it, its
    base flaring into great buttresses; in the hollow between them a bower of woven vines and leaves (Zarude's)."""
    cv = ground(GRASS, 4, 4)
    body = set()
    cx = 32
    for j in range(64):
        t = j / 63.0
        hw = 12 + 4 * t + (19 * ((t - 0.5) / 0.5) ** 2.0 if t > 0.5 else 0)
        wob = 1.2 * math.sin(j * 0.19)
        for i in range(64):
            dx = i + 0.5 - cx - wob
            if abs(dx) <= hw:
                if t > 0.7 and abs(dx) > 10 and math.sin(dx * 0.38) > 0.6 and abs(dx) < hw - 2 and j > 54:
                    continue                                             # the gaps between the buttresses
                body.add((i, j))
    for (i, j) in body:
        dx = i + 0.5 - cx
        c = BK2 if dx < -5 else (BK1 if dx < 7 else BK0)
        if (i * 2 + (j // 4)) % 7 == 0:
            c = BK0 if c != BK0 else S_OUT                               # the stringy, furrowed bark
        elif (i * 2 + (j // 4)) % 7 == 1 and c == BK1:
            c = BK2
        cv.put(i, j, c)
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, 1)):
            if (x + dx, y + dy) not in body and 0 <= x + dx < 64 and y + dy < 64:
                cv.put(x + dx, y + dy, INK)
    hol = ellipse_body(cx, 53, 7.0, 9.0)
    for (i, j) in hol:
        if j < 62:
            cv.put(i, j, S_OUT)
    for (i, j) in hol:
        if 53 < j < 62:
            cv.put(i, j, C_DK if (i + j) % 3 else C_MID)                   # the bower of woven vines
            if (i * 3 + j) % 7 == 0:
                cv.put(i, j, BK2)
    for (i, j) in hol:
        if (i, j - 1) not in hol and j < 62:
            cv.put(i, j, INK)
    for (x, y, n) in [(19, 2, 13), (23, 0, 10), (44, 3, 15), (41, 20, 9), (20, 24, 10), (47, 28, 8), (16, 33, 6), (35, 9, 7)]:
        for k in range(n):
            cv.put(x + (k % 3 == 2), y + k, MOSSG)
            if k < n - 2:
                cv.put(x + 1, y + k, C_DK if (x + k) % 2 else MOSSG)
    for (x0, sway) in [(27, 3), (38, -2), (31, 2)]:
        for k in range(44):
            cv.put(x0 + round(sway * math.sin(k * 0.15)), k, C_MID if k % 5 else C_HL)
    for (a, b) in [((12, 61), (1, 63)), ((52, 61), (63, 63)), ((20, 62), (14, 63)), ((45, 62), (50, 63))]:
        cv.line(*a, *b, BK1)
    return cv


def lianas():
    """1x2 lianas and muscadine vine hanging from the canopy in a curtain (blocking)."""
    cv = ground(GRASS, 1, 2)
    for (x, sway, ph) in [(2, 2, 0), (5, 1, 1), (8, 2, 2), (11, 1, 0.5), (14, 2, 1.7)]:
        for k in range(30):
            xx = x + round(sway * math.sin(k * 0.2 + ph))
            cv.put(xx, k, C_DK if k % 3 else C_MID)
            if k % 6 == 3:
                cv.put(xx + 1, k, C_HL)
                cv.put(xx - 1, k + 1, C_MID)
    for i in range(16):
        if i % 3:
            cv.put(i, 31, SH)
    return cv


def palmetto():
    """1x1 a dwarf palmetto: stiff fans of blades on short stems, filling the cell."""
    cv = ground(GRASS)
    for (cx, cy, r, a0, n) in [(4, 11, 7, -2.9, 8), (12, 11, 7, -1.5, 8), (8, 8, 7, -2.4, 9)]:
        for k in range(n):
            a = a0 + k * 0.22
            for t in range(1, r):
                x, y = cx + t * math.cos(a), cy + t * math.sin(a)
                c = C_DK if t < 2 else (C_MID if (k + t) % 3 else C_HL)
                if t == r - 1:
                    c = C_HL if k % 2 else C_MID
                cv.put(round(x), round(y), c)
                cv.put(round(x), round(y) + 1, C_DK if t > 2 else S_OUT)
        cv.line(cx, cy, 8, 15, BK1)
    return cv


def log_bridge(base):
    """1x1 a fallen cypress trunk lying north-south across the slough (walkable): over water ('C') or its banks ('N' / 'S')."""
    cv = Canvas(1, 1)
    src = pcell({"C": "ekat:water_C", "N": "ekat:water_N", "S": "ekat:water_S"}[base])
    for j in range(16):
        for i in range(16):
            c = src.getpixel((i, j))[:3]
            cv.put(i, j, c if c in FAMILIES["SLOUGH"] else (WA if base == "C" else GD))
    for j in range(16):
        for i in range(3, 13):
            c = BK2 if i < 6 else (BK1 if i < 10 else BK0)
            if (j + i) % 7 == 0:
                c = BK1
            if i in (5, 6) and j % 5 == 0:
                c = MOSSG
            cv.put(i, j, c)
        cv.put(2, j, INK)
        cv.put(13, j, INK)
        if base == "C":
            cv.put(14, j, (64, 96, 64) if j % 2 else WA)
    return cv


def mossy_log():
    """2x1 a fallen log rotting into the grass, moss along its back, a fern of mushrooms."""
    cv = ground(GRASS, 2, 1)
    body = {(i, j) for i in range(2, 30) for j in range(5, 13) if not (i in (2, 29) and j in (5, 12))}
    for (i, j) in body:
        c = BK2 if j < 8 else (BK1 if j < 11 else BK0)
        if j == 5 or (j == 6 and i % 3):
            c = C_MID if i % 4 else C_HL
        cv.put(i, j, c)
    ink_outline(cv, body, INK, only_clear=False)
    for (i, j) in ellipse_body(29, 8.5, 2.2, 3.0):
        cv.put(i, j, BK2 if (i + j) % 2 else BK1)
    for i in range(3, 30):
        cv.put(i, 14, SH)
    return cv


def larder():
    """1x1 wild fruit heaped on broad leaves: muscadines, mayhaws (the troop's larder)."""
    cv = ground(GRASS)
    for (i, j) in ellipse_body(8, 10, 7, 4):
        cv.put(i, j, C_DK if (i + j) % 4 else MG)
    for (x, y, c) in [(5, 9, FRU1), (7, 8, FRU2), (9, 9, FRU1), (11, 10, FRU2), (6, 11, FRU2), (8, 11, FRU1), (10, 8, FRU1),
                      (8, 6, FRU2)]:
        cv.put(x, y, c)
        cv.put(x + 1, y, c)
        cv.put(x, y + 1, INK)
        cv.put(x + 1, y + 1, c)
    return cv


def fern_w():
    """1x1 ferns of the deep wood's floor (walkable), in the canopy's greens."""
    cv = ground(GRASS)
    for (ang, ln) in [(-2.3, 7), (-1.9, 8), (-1.3, 8), (-0.8, 7), (-2.7, 6), (-0.4, 6)]:
        x, y = 8.0, 13.0
        for k in range(ln):
            x += math.cos(ang)
            y += math.sin(ang) + k * 0.08
            xi, yi = int(round(x)), int(round(y))
            cv.put(xi, yi, C_DK if k < 2 else (C_MID if k < ln - 2 else C_HL))
            if k % 2 == 0:
                cv.put(xi, yi - 1, C_HL if k < ln - 2 else GL)
                cv.put(xi + (1 if math.cos(ang) > 0 else -1), yi + 1, C_DK)
    return cv


def roots_w(kind):
    """1x1 cypress roots crawling over the ground (walkable): 'a' and 'b' runs, knotted, mossy."""
    cv = ground(GRASS)
    runs = [((0, 4), (15, 10)), ((3, 15), (11, 2))] if kind == "a" else [((0, 11), (15, 6)), ((7, 0), (5, 15))]
    for (a, b) in runs:
        n = 30
        for k in range(n + 1):
            t = k / n
            x = a[0] + (b[0] - a[0]) * t + 1.2 * math.sin(t * 6 + len(kind))
            y = a[1] + (b[1] - a[1]) * t
            cv.put(round(x), round(y), BK1)
            cv.put(round(x), round(y) + 1, BK0)
            cv.put(round(x), round(y) - 1, BK2 if k % 4 else MOSSG)
    return cv


def undergrowth():
    """1x1 a tangle of undergrowth: ferns, palmetto fans and vines over dark ground (blocking)."""
    cv = ground(lambda i, j: C_DK if (i + j) % 3 else SH)
    for (x, y) in [(3, 4), (10, 3), (6, 10), (13, 11)]:
        for (dx, dy) in [(0, 0), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (2, -1), (-2, -1)]:
            cv.put(x + dx, y + dy, C_HL if dy < 0 else C_MID)
    for k in range(16):
        cv.put(k, round(7 + 2 * math.sin(k * 0.6)), C_MID)
    return cv


# ---------------------------------------------------------------- Ogerpon
def dance_style(i, j, inside, d):
    """The dance ring: the grass danced down to bare packed earth, scuffed in arcs, tufts left at its rim."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1 and (i + j) % 2 == 0:
            return WD2
        return GRASS(i, j)
    if near == 1:
        return GD if (i + j) % 2 else WD2
    if near == 2 and hashn(i, j, 602) < 0.35:
        return G
    k = (i * 3 - j * 2) % 13
    if k in (0, 1):
        return WD2
    return WD3 if hashn(i, j, 601) > 0.1 else WD2


def mask_stake(kind):
    """1x2 a stake at the dance ring. 'teal': the Teal Mask on it, a painted wire-screen face with a yarn beard under a tall
    capuchon; 'blue' / 'red' / 'grey': an empty stake, ribbons in its mask's colour tied on, waiting."""
    cv = ground(GRASS, 1, 2)
    for j in range(8, 31):
        cv.put(7, j, WD2)
        cv.put(8, j, WD1)
        cv.put(6, j, INK)
        cv.put(9, j, INK)
    cv.hline(5, 10, 31, SH)
    if kind == "teal":
        # the capuchon: a tall teal cone with a yellow trim and tassel
        for j in range(0, 9):
            hw = 0.5 + j * 0.55
            for i in range(16):
                if abs(i + 0.5 - 8) <= hw:
                    cv.put(i, j, TL1 if i < 8 else TL2)
        cv.hline(3, 12, 9, YN1)
        cv.put(8, 0, YN1)
        # the mask: a wire-screen face (mesh dots), painted eyes, a smile
        for j in range(10, 20):
            for i in range(3, 13):
                c = TL1 if (i + j) % 2 else TL2
                if (i, j) in ((5, 13), (6, 13), (9, 13), (10, 13)):
                    c = INK
                if j == 17 and 5 <= i <= 10:
                    c = TL3
                cv.put(i, j, c)
        cv.vline(2, 10, 19, INK)
        cv.vline(13, 10, 19, INK)
        cv.hline(3, 12, 20, INK)
        for i in range(3, 13):                                            # the yarn beard
            for k in range(3 + (i % 3)):
                cv.put(i, 21 + k, YN1 if (i + k) % 2 else YN2)
    else:
        a, b = {"blue": (BL1, BL2), "red": (RD1, RD2), "grey": (GY1, GY2)}[kind]
        cv.hline(5, 10, 7, INK)
        cv.hline(6, 9, 6, WD2)                                           # the empty hook
        cv.put(8, 9, INK)
        cv.put(8, 10, INK)
        for (x, n, ph) in [(10, 12, 0), (11, 9, 1), (5, 10, 2), (4, 7, 0.5)]:
            for k in range(n):
                cv.put(x + round(1.2 * math.sin(k * 0.6 + ph)), 11 + k, a if k % 3 else b)
        cv.hline(6, 9, 11, b)
    return cv


def workbench():
    """2x1 the mask-maker's bench on a stump: pots of teal, red and blue paint, a roll of wire screen, a half-painted mask."""
    cv = ground(GRASS, 2, 1)
    cv.rect(2, 3, 28, 7, WD2)
    cv.hline(2, 29, 3, WD3)
    cv.hline(2, 29, 9, WD1)
    for x in (4, 26):
        cv.rect(x, 10, 3, 5, WD1)
    cv.hline(1, 30, 2, INK)
    cv.hline(1, 30, 10, INK)
    cv.vline(1, 2, 10, INK)
    cv.vline(30, 2, 10, INK)
    for (x, c) in [(4, TL2), (8, RD1), (12, BL1)]:
        cv.rect(x, 1, 3, 4, c)
        cv.hline(x, x + 2, 1, c)
        cv.hline(x - 1, x + 3, 5, INK)
    for i in range(17, 22):
        for j in range(2, 8):
            cv.put(i, j, FE1 if (i + j) % 2 else FE2)                     # the wire screen roll
    for i in range(23, 29):
        for j in range(2, 8):
            cv.put(i, j, TL1 if i < 26 and (i + j) % 2 else FE1)          # a mask half painted
    cv.put(24, 4, INK)
    cv.put(27, 4, INK)
    for i in range(3, 30):
        cv.put(i, 15, SH)
    return cv


def costumes():
    """2x1 Courir costumes drying on a line between two stakes: fringed shirts in patchwork colours."""
    cv = ground(GRASS, 2, 1)
    for x in (1, 30):
        cv.vline(x, 0, 14, WD1)
        cv.vline(x + 1 if x == 1 else x - 1, 0, 14, INK)
    for i in range(1, 31):
        cv.put(i, 2 + round(1.5 * math.sin(math.pi * i / 30)), WD2)
    for (x0, c1, c2) in [(4, PU1, YN1), (12, BL1, RD1), (20, RD1, YN1), (26, GY1, BL1)]:
        for j in range(4, 12):
            for i in range(x0, x0 + 5):
                cv.put(i, j, c1 if (i + j) % 3 else c2)
        for i in range(x0, x0 + 5):                                      # the fringe
            if i % 2 == 0:
                cv.put(i, 12, c2)
                cv.put(i, 13, c1)
        cv.hline(x0, x0 + 4, 3, INK)
    return cv


def courir_flag():
    """1x2 the Courir's flag on a tall pole: a pennant in the riders' patchwork colours, ribbons at the pole's head."""
    cv = ground(GRASS, 1, 2)
    cv.vline(3, 1, 30, WD2)
    cv.vline(4, 1, 30, WD1)
    cv.vline(2, 1, 30, INK)
    cv.vline(5, 1, 30, INK)
    cv.hline(1, 6, 0, INK)
    for j in range(2, 14):
        w = int((13 - j) * 0.9) + 2 if j > 7 else j + 2
        for i in range(6, min(16, 6 + w + 4)):
            band = (i - 6) // 3
            cv.put(i, j + round(0.8 * math.sin(i * 0.6)), [PU1, YN1, BL1, RD1][band % 4])
    for (x, n, c) in [(1, 6, YN1), (2, 8, RD1)]:
        for k in range(n):
            cv.put(x - (k % 3 == 1), 1 + k, c)
    cv.hline(1, 7, 31, SH)
    return cv


def coop():
    """2x1 a chicken coop of weathered slats (the Courir chases chickens for its gumbo), a hen pecking by it."""
    cv = ground(GRASS, 2, 1)
    cv.rect(3, 4, 20, 10, WD2)
    for x in range(3, 23, 3):
        cv.vline(x, 4, 13, WD1)
    cv.hline(2, 23, 3, WD3)
    cv.hline(2, 23, 2, INK)
    cv.hline(2, 23, 14, INK)
    cv.vline(2, 2, 14, INK)
    cv.vline(23, 2, 14, INK)
    cv.rect(10, 8, 5, 6, INK)
    for (i, j) in ellipse_body(27.5, 10, 2.6, 2.0):
        cv.put(i, j, (248, 248, 232))
    cv.put(29, 8, YN2)
    cv.put(30, 9, YN1)
    cv.put(26, 12, YN2)
    return cv


def capuchons():
    """1x1 three capuchons (the Courir's tall cone hats) set out on a bench, fringed in the riders' colours."""
    cv = ground(GRASS)
    cv.rect(1, 11, 14, 3, WD2)
    cv.hline(1, 14, 14, WD1)
    for (x, c1, c2) in [(3, PU1, YN1), (8, BL1, RD1), (12, RD1, YN1)]:
        for j in range(2, 11):
            hw = (j - 2) * 0.28
            for i in range(16):
                if abs(i + 0.5 - x) <= hw + 0.5:
                    cv.put(i, j, c1 if (i + j) % 3 else c2)
        cv.hline(x - 2, x + 2, 11, c2)
    return cv


def gumbo_pot():
    """1x1 a black iron gumbo pot on a tripod over cold ashes (the Courir ends with gumbo)."""
    cv = ground(GRASS)
    for (i, j) in ellipse_body(8, 13, 6, 2.2):
        cv.put(i, j, FE1 if (i + j) % 2 else SHL3)
    for (a, b) in [((2, 15), (8, 1)), ((14, 15), (8, 1)), ((8, 15), (8, 1))]:
        cv.line(*a, *b, WD1)
    body = ellipse_body(8, 8.5, 5, 4)
    for (i, j) in body:
        cv.put(i, j, FE1 if i < 7 and j < 8 else FE2)
    ink_outline(cv, body, INK, only_clear=False)
    cv.hline(4, 12, 5, INK)
    cv.hline(5, 11, 4, FE1)
    return cv


# ---------------------------------------------------------------- Tornadus
def wind_oak():
    """3x3 a chenier live oak shorn by the Gulf wind: its crown cut low and swept east in one long mass, the trunk leaning with it,
    its limbs reaching east."""
    cv = ground(GRASS, 3, 3)
    for j in range(24, 46):
        t = (45 - j) / 21.0
        x = 15 + t * 7
        w = 4 if j > 36 else 3
        for k in range(-w, w + 1):
            cv.put(round(x) + k, j, OB[0] if k < -1 else (OB[1] if k < 2 else OB[2]))
        cv.put(round(x) - w - 1, j, (48, 40, 32))
        cv.put(round(x) + w + 1, j, (48, 40, 32))
    for (a, b) in [((22, 26), (44, 20)), ((21, 27), (6, 22)), ((23, 25), (34, 12))]:
        for o in (0, 1, 2):
            cv.line(a[0], a[1] + o, b[0], b[1] + o, OB[o])
    body = set()
    for j in range(1, 30):
        for i in range(48):
            u = (i + 0.5 - 27) / 21.5
            v = (j + 0.5 - 14) / 11.5
            r = u * u + v * v
            if r <= 1.0 + 0.18 * math.sin(j * 1.1 + i * 0.3) and not (i < 12 and hashn(i // 2, j, 611) < 0.4):
                body.add((i, j))
    for (i, j) in body:
        lump = math.sin(i * 0.45 + j * 0.2) + math.sin(j * 0.7 - i * 0.15)
        c = OK[1]
        if lump > 0.9:
            c = OK[0]
        if lump > 1.5 or (j < 9 and lump > 0.3):
            c = OK[4] if j < 12 else OK[0]
        if j < 5 and i > 16:
            c = OK[3] if (i + j) % 3 else OK[4]
        if lump < -1.1 or j > 23:
            c = OK[2]
        cv.put(i, j, c)
    for (x, y) in list(body):
        if (x, y + 1) not in body:
            cv.put(x, y + 1, (48, 40, 32))
        if (x - 1, y) not in body and x > 0:
            cv.put(x - 1, y, OK[2])
    for (x, y, n) in [(41, 24, 6), (31, 27, 5), (18, 26, 6), (10, 22, 5)]:
        for k in range(n):
            cv.put(x + k // 2, y + k, MOSSG)                             # moss streaming east
    for i in range(8, 40):
        if cv.get(i, 46) not in OB:
            cv.put(i, 46, SH)
            if 12 < i < 36:
                cv.put(i, 47, SH if i % 2 else GD)
    return cv


def shell_style(i, j, inside, d):
    """The chenier's ridge: sand and crushed shell (inside) on the grass, rippled by the wind, white shell fragments in it."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1:
            return OAT2 if (i + j) % 2 else GD
        if near == 2 and (i * 3 + j) % 5 == 0:
            return OAT1                                                  # sand blown onto the grass
        return GRASS(i, j)
    if near == 1:
        return OAT2 if (i + j) % 3 else G
    # wind ripples: long shallow ridges running north-south, lit on their west face
    r = (i * 2 + round(2 * math.sin(j * 0.5))) % 9
    if r == 0:
        return OAT2
    if r == 1:
        return SHL1
    n = hashn(i, j, 621)
    if n < 0.07:
        return SHL1                                                      # shell fragments
    if n < 0.11:
        return SHL3
    if n > 0.93:
        return (248, 248, 232)
    return OAT1 if hashn(i // 3, j // 2, 622) < 0.45 else SHL2


def comb(kind):
    """1x1 grass combed flat by the wind (walkable): long pale streaks of laid-over blades, 'h' east-west, 'v' north-south, 'a' / 'b'
    the two diagonals."""
    cv = ground(GRASS)
    for j in range(16):
        for i in range(16):
            k = {"h": j, "v": i, "a": i + j, "b": i - j}[kind]
            along = {"h": i, "v": j, "a": i - j, "b": i + j}[kind]
            if k % 4 == 0 and (along + k * 3) % 11 < 8:
                cv.put(i, j, GL)
            elif k % 4 == 1 and (along + k * 3) % 11 < 7:
                cv.put(i, j, G)
            elif k % 4 == 2 and (along + k) % 13 < 3:
                cv.put(i, j, SH)
    return cv


def weathervane():
    """1x2 an iron weathervane on a post: the rooster swung hard round to the east."""
    cv = ground(GRASS, 1, 2)
    cv.vline(7, 8, 30, WD2)
    cv.vline(8, 8, 30, WD1)
    cv.vline(6, 8, 30, INK)
    cv.vline(9, 8, 30, INK)
    cv.hline(1, 14, 8, FE2)                                              # the arrow
    cv.line(13, 6, 15, 8, FE2)
    cv.line(13, 10, 15, 8, FE2)
    cv.rect(1, 6, 2, 5, FE1)
    for (x, y) in [(6, 2), (7, 1), (8, 1), (9, 2), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 4), (7, 4), (8, 4), (9, 5),
                   (4, 2), (3, 1)]:
        cv.put(x, y, FE2)                                                # the rooster
    cv.put(9, 1, FE1)
    cv.hline(4, 11, 31, SH)
    for (x, y) in [(1, 13), (3, 12), (12, 14), (14, 12)]:
        cv.put(x, y, SHL3)
    return cv


def chimes():
    """1x2 shell chimes on a driftwood post, the strings streaming east in the wind."""
    cv = ground(GRASS, 1, 2)
    cv.vline(4, 6, 30, SHL3)
    cv.vline(5, 6, 30, WD2)
    cv.vline(3, 6, 30, INK)
    cv.vline(6, 6, 30, INK)
    cv.hline(3, 12, 6, WD2)
    cv.hline(3, 12, 5, INK)
    for (x0, y0) in [(7, 7), (9, 7), (11, 7)]:
        for k in range(10):
            x, y = x0 + k * 0.45, y0 + k
            cv.put(round(x), round(y), WD1 if k % 3 else SHL1)
            if k % 3 == 0:
                cv.put(round(x) + 1, round(y), SHL2)
    cv.hline(2, 8, 31, SH)
    return cv


def sea_oats():
    """1x1 sea oats bent over by the wind (walkable)."""
    cv = ground(GRASS)
    for (x0, h) in [(3, 10), (6, 12), (9, 11), (12, 9)]:
        for k in range(h):
            x = x0 + round((k / h) ** 2 * 5)
            cv.put(x, 15 - k, OAT2 if k < h - 3 else OAT1)
        for k in range(3):
            cv.put(x0 + 5 + k, 15 - h + k, OAT1)
    return cv


# ---------------------------------------------------------------- the sheet
def build():
    P = Pieces("lj")
    P.add("great_cypress", on_tall(great_cypress()), comment="4x4 a giant old cypress, Zarude's bower in its hollow, blocking", lair="zarude")
    P.add("lianas", lianas(), comment="1x2 a curtain of lianas, blocking", lair="zarude")
    P.add("palmetto", palmetto(), comment="1x1 a dwarf palmetto, blocking", lair="zarude")
    for k in ("N", "C", "S"):
        P.add(f"log_bridge_{k}", log_bridge(k), walk=True, comment=f"1x1 a fallen trunk across the slough (over water_{k})",
              lair="zarude")
    P.add("mossy_log", mossy_log(), comment="2x1 a mossy fallen log, blocking", lair="zarude")
    P.add("larder", larder(), comment="1x1 wild fruit heaped on leaves, blocking", lair="zarude")
    P.add_set("dance", dual_set(dance_style, ro=7, ri=5, wob=1), walk=True, comment="the trampled dance ring", lair="ogerpon")
    for k in ("teal", "blue", "red", "grey"):
        P.add(f"mask_{k}" if k == "teal" else f"stake_{k}", mask_stake(k), comment=f"1x2 the {k} mask stake, blocking",
              lair="ogerpon")
    P.add("workbench", workbench(), comment="2x1 the mask-maker's bench, blocking", lair="ogerpon")
    P.add("costumes", costumes(), comment="2x1 Courir costumes drying on a line, blocking", lair="ogerpon")
    P.add("gumbo_pot", gumbo_pot(), comment="1x1 a gumbo pot on a tripod, blocking", lair="ogerpon")
    P.add("courir_flag", courir_flag(), comment="1x2 the Courir's flag on its pole, blocking", lair="ogerpon")
    P.add("coop", coop(), comment="2x1 a chicken coop and a hen, blocking", lair="ogerpon")
    P.add("capuchons", capuchons(), comment="1x1 capuchons set out on a bench, blocking", lair="ogerpon")
    P.add("fern_w", fern_w(), walk=True, comment="1x1 ferns (walkable)", lair="ogerpon")
    # the deep wood's pieces stand in tall grass (Zarude's floor)
    P.add("roots_a", on_tall(roots_w("a")), walk=True, comment="1x1 cypress roots in the tall grass (walkable)", lair="zarude")
    P.add("roots_b", on_tall(roots_w("b")), walk=True, comment="1x1 cypress roots in the tall grass (walkable)", lair="zarude")
    P.add("fern_t", on_tall(fern_w()), walk=True, comment="1x1 ferns in the tall grass (walkable)", lair="zarude")
    P.add("palmetto_t", on_tall(palmetto()), comment="1x1 a dwarf palmetto in the tall grass, blocking", lair="zarude")
    P.add("lianas_t", on_tall(lianas()), comment="1x2 lianas over the tall grass, blocking", lair="zarude")
    P.add("undergrowth", undergrowth(), comment="1x1 a tangle of undergrowth, blocking", lair="zarude")
    P.add("wind_oak", wind_oak(), comment="3x3 a wind-swept chenier live oak, blocking", lair="tornadus")
    P.add_set("shell", dual_set(shell_style, ro=6, ri=5, wob=1), walk=True, comment="the chenier's shell ridge", lair="tornadus")
    for k in ("h", "v", "a", "b"):
        P.add(f"comb_{k}", comb(k), walk=True, comment=f"1x1 grass combed flat by the wind ({k})", lair="tornadus")
    P.add("weathervane", weathervane(), comment="1x2 an iron weathervane, blocking", lair="tornadus")
    P.add("chimes", chimes(), comment="1x2 shell chimes on a driftwood post, blocking", lair="tornadus")
    P.add("sea_oats", sea_oats(), walk=True, comment="1x1 sea oats bent by the wind (walkable)", lair="tornadus")
    return P


def main():
    P = build()
    bad = write_b2(P, "lair_woods.png", "orleans_lair_woods", "gTileset_OrleansLairWoods", "orleans_general.mapping.json",
                   FAMILIES, "The woods lairs (Zarude, Ogerpon, Tornadus)", "make_lair_woods.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_woods: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

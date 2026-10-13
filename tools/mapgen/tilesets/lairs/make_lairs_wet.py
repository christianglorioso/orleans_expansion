"""Own art for two green lairs (one shared secondary, gTileset_OrleansLairsWet on gTileset_OrleansGeneral):
the rougarou's levee hollow (Route 14) and Suicune's hidden island in the big lake (Route 11). (Celebi's Rootkin
shrine moved to make_lair_rootkin.py, the secondary the other Rootkin shrines will share.)

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lairs_wet.py
writes tools/mapgen/tilesets/lairs/lairs_wet.png + lairs_wet.json and recipes/orleans_lairs_wet.json (source "lw").

Every piece is an opaque cell (props are baked over the ground they stand on). Ground, marsh, water, lily pads,
cypress and the swamp canopy wall with its edge cells come from the primary for free.
    rougarou   levee_<key> (the Oldest Shrine's raised bank set, copied), track_<key> (a ring of trampled grass, the
               circling track), dead_cypress 2x3, cross 1x2 (a weathered wayside cross), wisp_lantern 1x2 (a lantern
               on a crooked post with a pale feu-follet flame), driftwood 2x1, clawed_stump 1x1, fog_grass /
               fog_water 1x1 (bands of ground mist)
    (the moss, sundial, lily and mushroom drawing functions are shared with make_lair_rootkin.py)
    suicune    isle_<key> (the island's grass bank on clear shallows), shallows_<key> (clear shallows on deep water),
               pillar 1x3 (a carved standing pillar on the island), causeway_v / causeway_v_sh / causeway_broken /
               causeway_head (a ruined stone causeway over the water), stepping 1x1, ruin / ruin_l (sunken ruins,
               copied from the route landmarks), fog on water
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import (CORNER_KEYS, SRC, Canvas, Pieces, dual_set, hashn, over, pcell, sheet_cell,  # noqa: E402
                      tex_from, MAPGEN)

# ---------------------------------------------------------------- colours
G, GD, GL = (120, 160, 104), (104, 144, 96), (136, 176, 128)
SH = (96, 128, 88)
SL1, SL2, SL3 = (88, 128, 80), (72, 104, 64), (56, 80, 56)
LP, LM = (168, 200, 136), (112, 152, 80)
E1, E2, E3 = (160, 120, 80), (120, 88, 64), (80, 64, 48)
INKW = (48, 40, 32)
MS1, MS2 = (152, 168, 144), (200, 208, 176)
DW1, DW2, DW3, DW4 = (72, 72, 64), (112, 112, 96), (152, 152, 136), (192, 192, 176)   # bleached dead wood
WS1, WS2 = (152, 232, 184), (216, 248, 224)                                          # feu-follet glow
FOG1, FOG2 = (176, 192, 184), (216, 224, 216)
MOSS1, MOSS2, MOSS3 = (48, 88, 48), (72, 112, 56), (104, 144, 72)
FW1, FW2, FY, FP, FPD = (248, 248, 232), (208, 216, 200), (232, 200, 96), (232, 160, 176), (184, 104, 128)
STEM = (64, 112, 56)
ST1, ST2, ST3, ST4 = (88, 88, 80), (128, 128, 112), (168, 168, 144), (208, 208, 184)
MO, INK = (80, 112, 64), (40, 40, 48)
WA, WD, RP = (96, 136, 136), (72, 112, 112), (152, 192, 184)
SH1, SH2, SND1, SND2 = (112, 168, 160), (144, 192, 176), (168, 184, 152), (200, 208, 176)
BANK1, BANK2, FOAM = (96, 128, 88), (72, 96, 64), (216, 232, 224)
MO2 = (128, 152, 80)
CORE = [(120, 160, 104), (96, 136, 136), (120, 168, 128), (136, 176, 128), (96, 128, 88), (144, 184, 152),
        (40, 56, 40), (64, 96, 64), (72, 96, 64), (80, 112, 96), (80, 80, 80), (104, 152, 120), (72, 112, 112),
        (104, 144, 96)]

FAMILIES = {
    "EARTH": [G, GD, GL, SH, SL1, SL2, SL3, LP, LM, E1, E2, E3, INKW, MS1, MS2],
    "DEAD": [G, GD, GL, SH, INKW, DW1, DW2, DW3, DW4, MS1, MS2, WS1, WS2, FOG1, FOG2],
    "STONE": [G, GD, GL, ST1, ST2, ST3, ST4, MO, INK, MOSS1, MOSS2, MOSS3, SH],
    "WETSTONE": [ST1, ST2, ST3, ST4, MO, INK, WA, WD, RP, SH1, SH2, SND1],
    "WATERY": [WA, WD, RP, SH1, SH2, SND1, SND2, G, GD, GL, BANK1, BANK2, FOAM, FOG1, FOG2],
}

GRASS = tex_from(pcell("ekat:grass"))
WATER = tex_from(pcell("ekat:water_C"))


def ground(fn, w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, fn(i, j))
    return cv


# ---------------------------------------------------------------- dual sets
def track_style(i, j, inside, d):
    """The circling track: grass pressed flat by something that circles here every night, in long curved streaks of
    darker and paler grass, the earth worn through in a few places."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1 and (i + j) % 2 == 0:
            return GL                                          # grass pushed up along the track's edge
        return GRASS(i, j)
    if near == 1:
        return GD if (i + j) % 2 else GRASS(i, j)
    k = (i * 2 + j * 3) % 12
    if k in (0, 1):
        return SH
    if k == 6:
        return GL
    if hashn(i // 2, j // 2, 9) < 0.06:
        return E2
    return GD if k in (2, 7) else G

def moss_style(i, j, inside, d):
    """A sunken circle of deep moss: velvety mounds, a shadowed lip on its north side, a few white specks."""
    if not inside:
        if d["ds"] == 1 or d["de"] == 1:
            return SH
        return GRASS(i, j)
    if d["dn"] is not None and d["dn"] <= 2:
        return MOSS1
    if d["dw"] is not None and d["dw"] <= 1:
        return MOSS1
    n = hashn(i, j, 21)
    b = hashn(i // 2, j // 2, 22)
    c = MOSS3 if b > 0.78 else (MOSS1 if b < 0.18 else MOSS2)
    if c == MOSS3 and hashn(i, j, 23) < 0.3:
        c = MOSS2
    if n < 0.025:
        c = FW2
    return c


def shallows_style(i, j, inside, d):
    """Clear shallows over a pale sand bottom (inside) on the deep lagoon water (outside)."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1:
            return WD if (i + j) % 2 else WA
        return WA
    if near == 1:
        return SH1 if (i + j) % 2 else WA
    if ((i + 2 * j) % 9) == 0:
        return SH2
    if hashn(i, j, 33) < 0.06:
        return SND1
    if hashn(i, j, 34) < 0.03:
        return RP
    return SH1


def isle_style(i, j, inside, d):
    """The island's grass with an earth bank and a line of foam on the clear shallows."""
    if inside:
        if d["ds"] is not None and d["ds"] <= 3:
            return BANK2 if d["ds"] == 1 else BANK1                # the bank's face (south side)
        near = min(v for v in (d["dn"], d["dw"], d["de"], 9) if v is not None)
        if near == 1:
            return BANK1
        return GRASS(i, j)
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if near == 1:
        return FOAM if (i + j) % 3 else SH2
    if near == 2:
        return SH2
    return shallows_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None})


# ---------------------------------------------------------------- rougarou props
def dead_cypress():
    """3x4 a dead bald cypress: a pale grey trunk flaring into buttress roots, the crown long gone, gnarled bare
    limbs reaching out, ragged Spanish moss hanging from them (a silhouette against the night)."""
    cv = Canvas(3, 4)
    cx = 24
    body = set()
    for j in range(14, 61):
        t = (j - 14) / 46.0
        hw = 2.6 + 1.4 * t + (8.0 * ((t - 0.72) / 0.28) ** 1.6 if t > 0.72 else 0)
        for i in range(48):
            if abs(i + 0.5 - cx - 1.2 * math.sin(j * 0.13)) <= hw:
                body.add((i, j))
    # limbs: (start, end, thickness), each a little crooked
    limbs = [((23, 26), (8, 14), 2), ((8, 14), (3, 6), 1), ((8, 14), (12, 5), 1), ((25, 22), (40, 12), 2),
             ((40, 12), (45, 6), 1), ((40, 12), (36, 4), 1), ((24, 16), (21, 6), 1), ((24, 34), (12, 30), 1),
             ((25, 38), (37, 33), 1)]
    for (a, b, w) in limbs:
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2
        for k in range(n + 1):
            t = k / n
            x = a[0] + (b[0] - a[0]) * t + 1.2 * math.sin(t * 6)
            y = a[1] + (b[1] - a[1]) * t
            for dw in range(-w + 1, w):
                body.add((round(x), round(y) + dw))
            body.add((round(x), round(y)))
    for (i, j) in body:
        dx = i + 0.5 - cx
        c = DW3 if dx < -1 else DW2
        if j < 40 and dx < -2:
            c = DW4
        if (j * 3 + i) % 13 == 0:
            c = DW1
        cv.put(i, j, c)
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in body and cv.get(x + dx, y + dy) is None:
                cv.put(x + dx, y + dy, INKW)
    for (a, b) in [((17, 59), (9, 62)), ((31, 59), (39, 62)), ((21, 60), (17, 63)), ((27, 60), (31, 63))]:
        cv.line(*a, *b, DW2)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, INKW)
    for (x, y, n) in [(5, 8, 7), (10, 12, 6), (14, 8, 5), (38, 14, 8), (43, 9, 6), (34, 18, 5), (14, 31, 6),
                      (34, 35, 5), (20, 9, 4)]:
        for k in range(n):
            if cv.get(x, y + k) in (None, INKW):
                cv.put(x, y + k, MS1 if k % 3 else MS2)
            if k < n - 2 and cv.get(x + 1, y + k) in (None, INKW):
                cv.put(x + 1, y + k, MS1)
    cv.put(23, 30, INKW)
    cv.put(23, 31, INKW)
    cv.vline(22, 40, 47, DW1)
    return over(cv, GRASS)

def cross():
    """1x2 a weathered wayside cross of grey cypress planks, leaning a little, a faded rag tied at the crossing and a
    ring of stones at its foot."""
    cv = Canvas(1, 2)
    for j in range(5, 29):
        x = 7 + (1 if j < 12 else 0)
        cv.put(x, j, DW3)
        cv.put(x + 1, j, DW2)
        cv.put(x - 1, j, INKW)
        cv.put(x + 2, j, INKW)
    cv.hline(3, 12, 9, DW3)
    cv.hline(3, 12, 10, DW2)
    cv.hline(3, 12, 8, INKW)
    cv.hline(3, 12, 11, INKW)
    cv.put(2, 9, INKW)
    cv.put(2, 10, INKW)
    cv.put(13, 9, INKW)
    cv.put(13, 10, INKW)
    cv.put(8, 4, INKW)
    cv.put(9, 4, INKW)
    for (x, y) in [(9, 12), (10, 13), (10, 14), (11, 15)]:
        cv.put(x, y, MS2)                              # the rag
    for (x, y) in [(4, 29), (6, 30), (10, 30), (12, 29)]:
        cv.put(x, y, DW4)
        cv.put(x, y + 1, DW1)
    cv.hline(6, 10, 29, SH)
    return over(cv, GRASS)


def wisp_lantern():
    """1x2 a crooked post with an iron lantern hung from its arm; inside, a pale green flame (the feu follet), its
    glow spilling on the post."""
    cv = Canvas(1, 2)
    for j in range(4, 30):
        x = 4 + (1 if j > 18 else 0)
        cv.put(x, j, DW2)
        cv.put(x + 1, j, DW1)
        cv.put(x - 1, j, INKW)
        cv.put(x + 2, j, INKW)
    cv.hline(4, 11, 4, DW2)
    cv.hline(4, 11, 3, INKW)
    cv.hline(4, 11, 5, INKW)
    cv.vline(11, 5, 7, DW1)
    cv.rect(9, 8, 5, 7, DW1)
    cv.rect(10, 9, 3, 5, WS1)
    cv.put(11, 10, WS2)
    cv.put(11, 11, WS2)
    cv.hline(9, 13, 15, INKW)
    for (x, y) in [(8, 10), (14, 11), (11, 16), (7, 13), (14, 7)]:
        cv.put(x, y, WS1)
    cv.hline(3, 7, 30, SH)
    return over(cv, GRASS)


def driftwood():
    """2x1 a bleached, twisted piece of driftwood in the grass: a knotted root end, a branch stub, grain lines."""
    cv = Canvas(2, 1)
    body = set()
    for i in range(4, 28):
        t = (i - 4) / 24
        y0 = 8 + 1.5 * math.sin(t * 4)
        hw = 2.2 - 0.8 * t
        for j in range(16):
            if abs(j - y0) <= hw:
                body.add((i, j))
    for (x, y) in [(3, 6), (2, 5), (3, 10), (2, 11), (4, 5), (26, 5), (27, 4), (28, 3)]:
        body.add((x, y))
    for (i, j) in body:
        cv.put(i, j, DW4 if (j < 8 and (i + j) % 5) else (DW3 if (i * 2 + j) % 7 else DW2))
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in body:
                cv.put(x + dx, y + dy, INKW)
    for i in range(5, 27):
        if cv.get(i, 12) is None or cv.get(i, 12) == INKW:
            cv.put(i, 12, SH)
    return over(cv, GRASS)

def clawed_stump():
    """1x1 a round cypress stump raked by three claw marks, its roots spreading into the grass."""
    cv = Canvas(1, 1)
    cv.ellipse(8, 11, 6.5, 3.5, INKW)
    cv.ellipse(8, 10, 5.5, 4.5, DW2)
    cv.ellipse(8, 7, 5.5, 2.6, INKW)
    cv.ellipse(8, 7, 4.6, 2.0, DW4)
    cv.ellipse(8, 7, 2.5, 1.0, DW3)
    cv.put(8, 7, DW2)
    for x in (5, 8, 11):
        cv.line(x, 9, x - 1, 13, INKW)
        cv.put(x + 1, 10, DW3)
    for (a, b) in [((3, 12), (0, 14)), ((13, 12), (15, 15)), ((7, 13), (6, 15))]:
        cv.line(*a, *b, DW2)
    return over(cv, GRASS)

def fog(on_water, variant=0):
    """1x1 a thin band of low mist (dithered, two pale tones) lying across the cell; joins east-west with itself
    and with the other variant (the band's height at the cell edges is the same)."""
    base = WATER if on_water else GRASS
    cv = ground(base)
    for j in range(16):
        for i in range(16):
            mid = 8 + 2.0 * math.sin((i + 4 * variant) * math.pi / 16) ** 2 - 1
            v = 1 - abs(j - mid) / 4.0
            if v > 0.55 and (i + j) % 2 == 0:
                cv.put(i, j, FOG2)
            elif v > 0.2 and (i + 2 * j) % 4 == 0:
                cv.put(i, j, FOG1)
    return cv


# ---------------------------------------------------------------- celebi props
def moss_tex(i, j):
    c = moss_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None})
    return MOSS2 if c == FW2 else c             # no white specks under the stone (they'd need the flower palette)


def sundial():
    """2x2 a sundial of cut stone on the moss: a round dial on a fluted pedestal, carved hour marks and a spiral
    at its heart, the gnomon's blade and its shadow."""
    cv = Canvas(2, 2)
    cx, cy = 16, 11
    # pedestal
    cv.rect(11, 15, 10, 13, ST3)
    cv.vline(11, 15, 27, ST4)
    cv.vline(20, 15, 27, ST2)
    for x in (13, 16, 18):
        cv.vline(x, 16, 26, ST2)
    cv.vline(10, 15, 28, INK)
    cv.vline(21, 15, 28, INK)
    cv.rect(8, 27, 16, 3, ST2)
    cv.hline(8, 23, 27, ST4)
    cv.hline(7, 24, 30, INK)
    cv.vline(7, 27, 29, INK)
    cv.vline(24, 27, 29, INK)
    # dial
    cv.ellipse(cx, cy + 1, 13, 7, INK)
    cv.ellipse(cx, cy + 1, 12, 6, ST2)
    cv.ellipse(cx, cy, 12, 6, ST4)
    cv.ellipse(cx, cy, 10.5, 5, ST3)
    for a in range(12):
        ang = a * math.pi / 6
        cv.put(round(cx + 9.5 * math.cos(ang)), round(cy + 4.5 * math.sin(ang)), ST1)
    for (x, y) in [(cx, cy), (cx + 1, cy), (cx + 1, cy + 1), (cx, cy + 1), (cx - 1, cy + 1), (cx - 1, cy),
                   (cx - 1, cy - 1), (cx, cy - 1), (cx + 1, cy - 1), (cx + 2, cy - 1)]:
        cv.put(x, y, ST2)
    # gnomon and its shadow
    cv.line(cx, cy - 1, cx - 5, cy - 7, ST1)
    cv.line(cx + 1, cy - 1, cx - 4, cy - 7, ST4)
    cv.line(cx, cy + 1, cx + 7, cy + 3, ST1)
    for (x, y) in [(6, 14), (25, 12), (9, 24)]:
        cv.put(x, y, MO)
    return over(cv, moss_tex)


def lily(kind):
    """1x1 spider lilies (white or pink) in the grass, the ring round the glade's moss."""
    cv = ground(GRASS)
    petal, dark = (FW1, FW2) if kind == "white" else (FP, FPD)
    for (fx, fy) in [(4, 6), (11, 4), (9, 11)]:
        cv.vline(fx, fy + 1, fy + 4, STEM)
        for (dx, dy) in [(-2, -1), (2, -1), (-1, -2), (1, -2), (0, -2), (-2, 1), (2, 1), (-3, 0), (3, 0)]:
            cv.put(fx + dx, fy + dy, petal if (dx + dy) % 2 else dark)
        cv.put(fx, fy - 1, FY)
        cv.put(fx, fy, FY)
    cv.put(13, 13, STEM)
    cv.put(3, 13, STEM)
    return cv


def mushrooms():
    cv = ground(GRASS)
    for (x, y, r) in [(5, 10, 2.5), (10, 8, 2), (8, 13, 1.6)]:
        cv.vline(x, y, y + 2, FW2)
        cv.ellipse(x, y - 0.5, r, r * 0.7, FP)
        cv.put(int(x - 1), int(y - 1), FW1)
        cv.hline(int(x - r), int(x + r), y + 1, SH)
    return cv


def vines_on(edge):
    """The canopy's south-face edge cell (primary) with vines and tiny white flowers hanging into the glade."""
    base = pcell(f"patch:bdg_swamp_{edge}_542aa1ca")
    cv = ground(tex_from(base))
    for (x, n) in [(2, 9), (6, 12), (11, 7), (14, 10)]:
        top = 0
        for k in range(n):
            y = top + k
            cv.put(x + (1 if k % 4 == 2 else 0), y, (64, 96, 64) if k % 3 else (104, 152, 120))
        cv.put(x, top + n, (144, 184, 152))
    return cv


# ---------------------------------------------------------------- suicune props
def pillar():
    """1x3 a carved Rootkin pillar standing on the island: a spiral-banded shaft, a broad capital, moss at its
    foot, lit from the north-west."""
    cv = Canvas(1, 3)
    for j in range(6, 44):
        for i in range(3, 13):
            c = ST3
            if i <= 4:
                c = ST4
            elif i >= 11:
                c = ST2
            cv.put(i, j, c)
        cv.put(2, j, INK)
        cv.put(13, j, INK)
    for yb in (14, 24, 34):
        cv.hline(3, 12, yb, ST2)
        cv.hline(3, 12, yb + 1, ST4)
        for (dx, dy) in [(0, 3), (1, 3), (2, 4), (1, 5), (0, 5), (-1, 4)]:
            cv.put(7 + dx, yb + dy, ST1)
    cv.rect(1, 1, 14, 6, ST3)
    cv.hline(1, 14, 1, ST4)
    cv.hline(1, 14, 6, ST1)
    cv.vline(0, 1, 6, INK)
    cv.vline(15, 1, 6, INK)
    cv.hline(1, 14, 0, INK)
    for (x, y) in [(4, 3), (11, 3)]:
        cv.put(x, y, ST1)
    cv.rect(2, 42, 12, 3, ST2)
    cv.hline(1, 14, 45, INK)
    for (x, y) in [(3, 41), (4, 40), (12, 40), (11, 41), (5, 30), (10, 20)]:
        cv.put(x, y, MO)
    return over(cv, GRASS)


def slab_row(cv, y0, x0, x1, broken=False):
    for j in range(y0, y0 + 16):
        for i in range(x0, x1 + 1):
            cv.put(i, j, ST3)
    for j in (y0, y0 + 8):
        cv.hline(x0, x1, j, ST4)
        cv.hline(x0, x1, j + 7, ST2)
    cv.vline(x0, y0, y0 + 15, ST4)
    cv.vline(x1, y0, y0 + 15, ST1)
    cv.vline((x0 + x1) // 2, y0 + 8, y0 + 15, ST2)
    for (x, y) in [(x0 + 2, y0 + 4), (x1 - 3, y0 + 11)]:
        cv.put(x, y, MO)


def causeway(kind, shallow=False):
    """The ruined causeway north-south over the lagoon: worn slabs (v), the same over the shallows (v_sh), a
    broken span with a slab tipped into the water and stepping stones (broken: blocking), the head where it meets
    the landing (head)."""
    base = (lambda i, j: shallows_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None})) if shallow else WATER
    cv = ground(base)
    x0, x1 = 2, 13
    if kind in ("v", "head"):
        slab_row(cv, 0, x0, x1)
        for j in range(16):
            cv.put(x0 - 1, j, WD)
            cv.put(x1 + 1, j, WD)
        if kind == "head":
            cv.hline(x0, x1, 15, ST1)
        for j in (5, 12):
            cv.put(x1 + 2, j, RP)
            cv.put(x0 - 2, j + 1, RP)
    elif kind == "broken":
        cv.rect(x0, 0, x1 - x0 + 1, 4, ST3)
        cv.hline(x0, x1, 3, ST1)
        cv.hline(x0, x1, 4, WD)
        for (x, y, w, h) in [(4, 8, 5, 4), (10, 11, 3, 3)]:
            cv.rect(x, y, w, h, ST2)
            cv.hline(x, x + w - 1, y, ST4)
            cv.hline(x - 1, x + w, y + h, WD)
        for (x, y) in [(3, 6), (12, 7), (8, 14)]:
            cv.put(x, y, RP)
    return cv


def stepping():
    cv = ground(WATER)
    for (x, y, rx) in [(5, 6, 3.5), (11, 11, 3)]:
        cv.ellipse(x, y + 1, rx + 0.5, 2.5, WD)
        cv.ellipse(x, y, rx, 2.2, ST3)
        cv.put(int(x - 1), int(y - 1), ST4)
        cv.put(int(x + 1), int(y + 1), MO)
    return cv


def copy_ruin(name):
    l = json.load(open(os.path.join(SRC, "route_landmarks.json")))["pieces"][name]
    cv = sheet_cell(os.path.join(SRC, "route_landmarks.png"), l["x"], l["y"], l["w"], l["h"])
    cv.recolor({MO2: MO, FOAM: RP})          # the lagoon's palettes: one moss green, ripples for foam
    return over(cv, WATER)


# ---------------------------------------------------------------- build
def build():
    P = Pieces("lw")
    # rougarou
    shrine = json.load(open(os.path.join(MAPGEN, "tilesets", "arenas", "shrine.json")))["pieces"]
    spng = os.path.join(MAPGEN, "tilesets", "arenas", "shrine.png")
    for key in CORNER_KEYS.values():
        p = shrine[f"berm_{key}"]
        P.add(f"levee_{key}", sheet_cell(spng, p["x"], p["y"]), comment=f"levee bank (the shrine's ridge set) {key}",
              lair="rougarou", walk=False)
    P.add_set("track", dual_set(track_style, ro=6, ri=5, wob=1), walk=True,
              comment="the circling track, trampled grass", lair="rougarou")
    P.add("dead_cypress", dead_cypress(), comment="3x4 a dead cypress, bleached and mossy, blocking", lair="rougarou")
    P.add("cross", cross(), comment="1x2 a weathered wayside cross, blocking", lair="rougarou")
    P.add("wisp_lantern", wisp_lantern(), comment="1x2 a lantern on a crooked post, a pale green flame, blocking",
          lair="rougarou")
    P.add("driftwood", driftwood(), comment="2x1 bleached driftwood, blocking", lair="rougarou")
    P.add("clawed_stump", clawed_stump(), comment="1x1 a stump raked by claws, blocking", lair="rougarou")
    for v in (0, 1):
        P.add(f"fog_grass{v}", fog(False, v), walk=True, comment="1x1 a band of ground mist over grass (walkable)",
              lair="rougarou")
        P.add(f"fog_water{v}", fog(True, v), comment="1x1 a band of mist over water (water: blocking)",
              lair="rougarou suicune")
    # suicune
    P.add_set("shallows", dual_set(shallows_style, ro=6, ri=5, wob=1), walk=False,
              comment="clear shallows over sand on the lagoon (blocking water: surf or the causeway)", lair="suicune")
    P.add_set("isle", dual_set(isle_style, ro=7, ri=5, wob=1), walk=True,
              comment="the island's grass bank on the shallows", lair="suicune")
    P.add("pillar", pillar(), comment="1x3 the carved pillar on the island, blocking", lair="suicune")
    P.add("causeway_v", causeway("v"), walk=True, comment="causeway slabs over the lagoon (walkable)", lair="suicune")
    P.add("causeway_v_sh", causeway("v", True), walk=True, comment="causeway slabs over the shallows", lair="suicune")
    P.add("causeway_head", causeway("head"), walk=True, comment="the causeway's south end at the landing",
          lair="suicune")
    P.add("causeway_broken", causeway("broken"), comment="a broken span, slabs tipped into the water (blocking)",
          lair="suicune")
    P.add("stepping", stepping(), comment="1x1 stepping stones in the water (scenery, blocking)", lair="suicune")
    P.add("ruin", copy_ruin("sunken_ruin"), comment="1x2 a sunken carved pillar (route landmark art)", lair="suicune")
    P.add("ruin_l", copy_ruin("sunken_ruin_l"), comment="2x2 a larger sunken ruin (route landmark art)", lair="suicune")
    return P


def main():
    P = build()
    bad = P.write("lairs_wet.png", "orleans_lairs_wet", "gTileset_OrleansLairsWet", "orleans_general.mapping.json",
                  FAMILIES, "The green lairs (rougarou, Suicune)")
    for b in bad:
        print("off-family:", b)
    print(f"lairs_wet: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

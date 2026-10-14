"""Batch 2 of the storm lairs' secondary (gTileset_OrleansLairStorm, prefix ls, on gTileset_OrleansGeneral): Raikou's struck clearing
(batch 1, unchanged and first in the sheet, so every batch-1 metatile keeps its id) plus
    Zapdos   the lamp gallery on top of the Storm's Edge lighthouse (the existing StormsEdge_LighthouseGallery map, redone)
    Thundurus the levee crown above the river in a thunderstorm (off Route 12)

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_storm_b2.py
writes tools/mapgen/tilesets/lairs/lair_storm_b2.png + lair_storm_b2.json and recipes_b2/orleans_lair_storm.json (source "ls"): a
superset of the batch-1 recipe, to replace it when batch 2 is approved.

Zapdos (the lamp gallery, seen from above, the storm all round it):
    sky_XY (2x2 block)  the storm: dark cloud wrack, a far flicker of lightning inside it (the map's fill and its border block)
    deck_<key>          the gallery's iron deck on the sky: riveted plates, its railing round the rim, the deck's lip and shadow
    deck_C2 / deck_C3   plates with rust streaks / a rain puddle (walkable)
    deck_N_spark        the north rail with St Elmo's fire crackling on its posts
    lantern 4x4         the lantern room: red dome cap with its ventilator ball and lightning rod, glazed panes in iron
                        mullions, the great lens inside burning yellow, the white-and-red watch-room wall under it
    lantern_dark 4x4    the same with the lamp out (during the story, until Eclair's grid is restored: FLAG_STORMS_EDGE_GRID_RESTORED)
    hatch 1x1           the stair hatch down into the lighthouse (the way in and out)
    flag_mast 1x3       a signal mast flying the two hurricane-warning flags (red, a black square in each)
    anemometer 1x2      a cup anemometer spinning on a short mast; storm_lamp 1x1 (the keeper's storm lantern, an oil can), rope 1x1
Thundurus (the levee, drawn in the in-game levee's colours: levee.py's slope, earth, riprap and foam):
    riprap0/1           stone riprap at the waterline (the river to the north)
    slope_n0/1          the levee's river face, in shade; crown0/1 the shell-and-gravel crown road (walkable); slope_s0/1 the lit
                        landward slope (walkable); toe0/1 the landward toe meeting the grass (walkable)
    shack 3x3           the levee watchman's shack: tin roof, plank walls, a lit storm lantern at the door
    bell_post 1x2       the crevasse bell on its post (rung when the levee was in danger)
    sandbags 2x1        sandbags stacked along the crown; mile_post 1x1 (a levee mile marker)
    struck_pole 1x3     a line pole on the crown split by lightning, its rod blackened
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import (GRASS, WATER, Canvas, dual_set, ellipse_body, gba, hashn, ink_outline, over, write_b2)  # noqa: E402
import make_lair_storm as RK  # noqa: E402  (batch 1: Raikou)

G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
INK = (40, 40, 48)
S0, S1, S2, S3 = RK.S0, RK.S1, RK.S2, RK.S3                      # (64,72,88) (96,112,128) (136,152,168) (184,200,208)
SP1, SP2, SP3 = RK.SP1, RK.SP2, RK.SP3                           # the sparks: (88,136,232) (160,216,248) (248,248,248)
GLS1, GLS2, GLS3 = RK.GLS1, RK.GLS2, RK.GLS3                     # glass: (64,96,112) (120,168,184) (208,240,248)
RUST1, RUST2, PALE, GREY, GREY_D = (128, 64, 40), (176, 96, 56), (208, 208, 200), (168, 168, 160), (128, 128, 120)
# the lighthouse's own colours (sources/orleans_custom/lighthouse.png)
R1, R2, R3 = (200, 64, 48), (168, 40, 40), (120, 24, 32)
Y1, Y2, Y3 = (248, 248, 208), (248, 232, 144), (224, 200, 88)
WH1, WH2 = (240, 240, 232), (208, 208, 200)
# the in-game levee (levee.py)
SL1, SL2, SL3 = (96, 128, 88), (80, 112, 72), (64, 96, 64)
EARTH, EARTH_D = (120, 96, 72), (88, 72, 56)
STONE_L, STONE, STONE_D, OUTL = (184, 176, 160), (144, 136, 128), (104, 100, 96), (80, 80, 80)
WA, FOAM = (96, 136, 136), (200, 224, 224)
SHELL = (216, 208, 184)
# wood and brass (the batch-1 WIRE family's browns and the lantern glow)
WB0, WB1, WB2, GLOW = (48, 40, 32), (88, 64, 48), (160, 128, 88), (216, 128, 64)
BRASS = (216, 168, 72)

# colour economy (the batch-1 set already fills most of its seven slots): the deck's rivets and sheen reuse the steel greys, the shell
# road the watch-room white, the levee's earth shadow the wood brown, the waterline foam the glass highlight, the lens' prism rings brass
GREY_D, GREY = S0, S3
Y3 = (216, 168, 72)
SHELL = WH2
FOAM = GLS3
EARTH_D = (88, 64, 48)
STONE_L, STONE, STONE_D, OUTL = (208, 208, 200), (168, 168, 160), (128, 128, 120), INK   # the riprap in the steel greys
WH1 = (248, 248, 248)

NEW_FAMILIES = {
    "LAMP": [INK, S0, S1, S2, S3, R1, R2, R3, Y1, Y2, Y3, GLS1, GLS2, WH1, WH2],
    "DECK": [INK, S0, S1, S2, S3, RUST1, RUST2, PALE, SP1, SP2, SP3, GLS2, GLS3],
    "LEVEE": [G, GD, GL, SL1, SL2, SL3, EARTH, EARTH_D, STONE_L, STONE, STONE_D, OUTL, WA, FOAM, SHELL],
    "SHACK": [INK, WB0, WB1, WB2, GLOW, BRASS, S0, S1, S2, S3, G, GD, GL, SH, Y2],   # (also the bell and the struck pole, on grass)
}


# ---------------------------------------------------------------- Zapdos: the sky, the deck
_BLOBS = [(8, 8, 12.0), (26, 6, 9.0), (20, 22, 12.5), (2, 26, 8.5)]


def _cloud(i, j):
    f = 0.0
    for (bx, by, r) in _BLOBS:
        for ox in (-32, 0, 32):
            for oy in (-32, 0, 32):
                d = math.hypot(i + 0.5 - bx - ox, (j + 0.5 - by - oy) * 1.3) / r
                f = max(f, 1.0 - d)
    return f


def sky_tex(i, j):
    """The storm seen from the gallery: great soft heaps of dark cloud, their upper edges catching the lamp, dithered into the black
    rifts between them (periodic over 32 px: the 2x2 block); a far flicker of lightning in one rift."""
    i, j = i % 32, j % 32
    f = _cloud(i, j)
    up = _cloud(i, (j - 3) % 32)
    d = (i + j) % 2
    if f > 0.12 and up < f - 0.1:
        c = S1 if (f > 0.3 or d) else S0                                 # the heaps' upper edges, lit
    elif f > 0.3:
        c = S0
    elif f > 0.18:
        c = S0 if d else INK
    elif f > 0.08:
        c = INK if (i + 2 * j) % 4 else S0
    else:
        c = INK
    if f > 0.6 and (i * 5 + j * 3) % 37 == 0:
        c = S1
    if (i, j) in ((30, 15), (31, 16), (31, 17), (0, 18)):
        c = SP1
    return c


def sky_block():
    out = {}
    for y in (0, 1):
        for x in (0, 1):
            cv = Canvas(1, 1)
            for j in range(16):
                for i in range(16):
                    cv.put(i, j, sky_tex(i + 16 * x, j + 16 * y))
            out[f"{x}{y}"] = cv
    return out


def deck_tex(i, j, rust=False, plain=False):
    """Riveted iron deck plates, wet: 8 px plates, rivets at their corners, a sheen of rain."""
    a, b = i % 16, (j + 8 * ((i // 16) % 2)) % 16
    if a == 0 or b == 0:
        c = S0
    else:
        c = S1 if (a + b * 2) % 7 == 0 else S2
        if (a, b) in ((2, 2), (13, 2), (2, 13), (13, 13)):
            c = S0                                                       # rivets
        if not plain and (i * 3 + j * 7) % 29 == 0:
            c = GREY                                                     # rain sheen
    if rust and not plain and hashn(i // 2, j, 503) < 0.12 and b > 2:
        c = RUST1 if (i + j) % 2 else RUST2
    return c


def deck_style(i, j, inside, d):
    """The deck on the sky: inside the plates; at the rim the railing (posts every 6 px, two rails); outside, below the rim, the
    gallery's lip and the drop into the storm."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if d["dn"] is not None and d["dn"] <= 3:
            return INK if d["dn"] == 1 else (S0 if d["dn"] == 2 else sky_tex(i, j))   # the lip under the south rail
        return sky_tex(i, j)
    if near == 1:
        return INK
    if near == 2:
        return PALE if (d["dn"] == 2 or d["dw"] == 2) else S2           # the top rail
    if near == 3:
        return S0
    if near == 4:
        along = i if (d["dn"] == 4 or d["ds"] == 4) else j
        return S3 if along % 6 == 0 else (S1 if along % 6 == 1 else deck_tex(i, j))   # posts and the bottom rail's shadow
    if near == 5:
        return S2 if (i + j) % 2 else S1
    return deck_tex(i, j)


def deck_cell(rust=False, puddle=False):
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, deck_tex(i, j, rust=rust))
    if puddle:
        for (i, j) in ellipse_body(8, 9, 6.2, 3.2):
            cv.put(i, j, GLS2 if (i + j) % 5 else GLS3)
        for (i, j) in ellipse_body(8, 9, 6.2, 3.2):
            if (i, j - 1) not in ellipse_body(8, 9, 6.2, 3.2):
                cv.put(i, j, S3)
        cv.put(6, 8, SP3)
    return cv


def plain_deck(w, h):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, deck_tex(i, j, plain=True))
    return cv


def lantern(lit):
    """4x4 the lantern room of the Storm's Edge lighthouse, seen from the gallery."""
    cv = plain_deck(4, 4)
    cx = 32
    # watch-room wall (white, a red band), its shadow on the deck
    for j in range(46, 60):
        for i in range(10, 54):
            c = WH1 if i < 26 else (WH2 if i < 46 else S2)
            if 50 <= j <= 54:
                c = R1 if i < 26 else (R2 if i < 46 else R3)
            cv.put(i, j, c)
    cv.hline(10, 53, 60, INK)
    cv.vline(9, 44, 60, INK)
    cv.vline(54, 44, 60, INK)
    for i in range(12, 56):
        cv.put(i, 61, S0)
        cv.put(i + 1, 62, S0 if i % 2 else S1)
    # the gallery cornice under the glass
    cv.rect(8, 42, 48, 4, S1)
    cv.hline(8, 55, 42, S2)
    cv.hline(8, 55, 45, S0)
    cv.hline(7, 56, 41, INK)
    cv.hline(7, 56, 46, INK)
    cv.vline(7, 41, 46, INK)
    cv.vline(56, 41, 46, INK)
    # the glazing: panes between iron mullions, the lens inside
    for j in range(24, 41):
        for i in range(14, 50):
            c = GLS1 if (i + j) % 4 else GLS2
            if (i - j) % 13 in (0, 1):
                c = GLS2                                                 # reflections of the storm
            cv.put(i, j, c)
    lens = ellipse_body(cx, 32.5, 9.5, 8.0)
    for (i, j) in lens:
        r = math.hypot((i + 0.5 - cx) / 9.5, (j + 0.5 - 32.5) / 8.0)
        if lit:
            c = Y1 if r < 0.35 else (Y2 if r < 0.7 else Y3)
            if int(r * 10) % 3 == 0 and r > 0.3:
                c = Y3                                                   # the lens' prism rings
        else:
            c = GLS2 if r < 0.4 else (GLS1 if int(r * 10) % 3 else S1)
        cv.put(i, j, c)
    if lit:
        for j in range(24, 41):
            for i in range(14, 50):
                if cv.get(i, j) in (GLS1, GLS2) and abs(j + 0.5 - 32.5) < 3.5 and (i + j) % 2 == 0:
                    cv.put(i, j, Y2)                                     # the beam spilling through the panes
    for x in (14, 21, 28, 35, 42, 49):
        cv.vline(x, 24, 40, INK if x in (14, 49) else S0)
    cv.hline(14, 49, 24, S0)
    # the red dome cap, its ventilator ball and lightning rod
    for j in range(10, 25):
        t = (24 - j) / 14.0
        hw = 21 * math.sqrt(max(0.0, 1 - t ** 1.6))
        for i in range(64):
            dx = i + 0.5 - cx
            if abs(dx) <= hw:
                c = R2
                if dx < -hw * 0.45:
                    c = R1
                elif dx > hw * 0.55:
                    c = R3
                if j == 24:
                    c = R3
                cv.put(i, j, c)
    for j in range(10, 25):
        t = (24 - j) / 14.0
        hw = 21 * math.sqrt(max(0.0, 1 - t ** 1.6))
        cv.put(int(cx - hw) - 1, j, INK)
        cv.put(int(cx + hw) + 1, j, INK)
    cv.hline(int(cx - 6), int(cx + 6), 9, INK)
    for (i, j) in ellipse_body(cx, 7, 3.2, 3.0):
        cv.put(i, j, S2 if i < cx else S1)
    ink_outline(cv, ellipse_body(cx, 7, 3.2, 3.0), INK, only_clear=False)
    cv.vline(31, 0, 4, INK)
    cv.vline(32, 0, 4, S3 if lit else S2)
    if lit:
        cv.put(32, 0, SP3)
        cv.put(31, 1, SP2)
    return cv


def hatch():
    """1x1 the stair hatch down into the lighthouse: the lid thrown back, iron steps going down into the dark."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, deck_tex(i, j, plain=True))
    cv.rect(2, 4, 12, 11, INK)
    for k, y in enumerate((6, 9, 12)):
        cv.hline(3 + k, 12 - k, y, S1)
        cv.hline(3 + k, 12 - k, y + 1, S0)
    cv.rect(2, 0, 12, 4, S2)                                             # the lid, thrown back
    cv.hline(2, 13, 0, PALE)
    cv.hline(2, 13, 3, S0)
    cv.put(4, 1, GREY_D)
    cv.put(11, 1, GREY_D)
    cv.vline(1, 0, 15, INK)
    cv.vline(14, 0, 15, INK)
    cv.hline(1, 14, 15, INK)
    return cv


def flag_mast():
    """1x3 a signal mast flying the two hurricane-warning flags: square red flags, a black square at the heart of each."""
    cv = plain_deck(1, 3)
    cv.rect(6, 2, 2, 44, S2)
    cv.vline(5, 2, 45, INK)
    cv.vline(8, 2, 45, INK)
    cv.vline(7, 2, 45, S0)
    cv.hline(5, 8, 1, INK)
    cv.hline(4, 9, 45, INK)
    cv.hline(3, 10, 46, S0)
    for y0 in (4, 17):
        for j in range(10):
            for i in range(9, 16):
                wave = round(math.sin((i - 9) * 0.7 + y0) * 1.0)
                yy = y0 + j + wave
                c = R1 if j < 3 else (R2 if j < 8 else R3)
                if 11 <= i <= 13 and 3 <= j <= 6:
                    c = INK
                cv.put(i, yy, c)
        cv.hline(8, 9, y0, INK)
        cv.hline(8, 9, y0 + 9, INK)
    return cv


def anemometer():
    """1x2 a cup anemometer whirling on a short mast."""
    cv = plain_deck(1, 2)
    cv.vline(7, 8, 29, S2)
    cv.vline(8, 8, 29, S0)
    cv.vline(6, 8, 29, INK)
    cv.vline(9, 8, 29, INK)
    cv.hline(5, 10, 30, INK)
    for (a, r) in [(0.3, 6), (2.4, 6), (4.5, 6)]:
        x, y = 7.5 + r * math.cos(a), 7 + r * 0.55 * math.sin(a)
        cv.line(8, 7, round(x), round(y), S1)
        for (i, j) in ellipse_body(x, y, 1.8, 1.4):
            cv.put(i, j, PALE if i < x else S2)
    cv.put(7, 7, INK)
    for (x, y) in [(1, 3), (14, 9), (2, 11)]:
        cv.put(x, y, SP2)
    return cv


def storm_lamp():
    """1x1 the keeper's storm lantern and an oil can left by the rail."""
    cv = plain_deck(1, 1)
    cv.rect(3, 5, 5, 8, Y2)
    cv.rect(4, 6, 3, 5, Y1)
    cv.hline(2, 8, 4, INK)
    cv.hline(2, 8, 13, INK)
    cv.vline(2, 4, 13, INK)
    cv.vline(8, 4, 13, INK)
    cv.hline(3, 7, 2, S0)
    cv.put(5, 1, INK)
    cv.rect(10, 8, 4, 6, R2)
    cv.hline(10, 13, 8, R1)
    cv.vline(14, 8, 13, INK)
    cv.vline(9, 8, 13, INK)
    cv.hline(9, 14, 14, INK)
    cv.line(13, 7, 15, 5, S2)
    return cv


def rope():
    """1x1 a coil of wet rope on the deck."""
    cv = plain_deck(1, 1)
    for r in (6.0, 4.6, 3.2):
        for (i, j) in ellipse_body(8, 8.5, r, r * 0.7):
            pass
        for k in range(48):
            a = k * math.pi / 24
            x, y = 8 + r * math.cos(a), 8.5 + r * 0.7 * math.sin(a)
            cv.put(round(x), round(y), GREY if math.sin(a) < 0 else GREY_D)
    cv.put(8, 9, INK)
    return cv


# ---------------------------------------------------------------- Thundurus: the levee
def lev(name, variant):
    """1x1 cells of the levee band (they tile east-west; two variants each)."""
    cv = Canvas(1, 1)
    v = variant
    for j in range(16):
        for i in range(16):
            x = i + 16 * v
            if name == "riprap":
                # the river above, foam at the waterline, stones piled up to the face
                top = 5 + round(1.5 * math.sin(x * 0.5))
                if j < top - 1:
                    c = WA
                elif j < top:
                    c = FOAM if x % 3 else WA
                else:
                    sx, sy = (x + (j // 4) * 3) % 6, j % 4
                    c = STONE if sx not in (0, 5) else STONE_D
                    if sy == 0:
                        c = STONE_L if sx not in (0, 5) else STONE
                    if sy == 3 or sx == 0:
                        c = OUTL
                    if j > 13:
                        c = SL3 if (x + j) % 3 else OUTL
            elif name == "slope_n":
                # the river face, in shade, grass striped by the slope
                c = SL3 if j < 4 else (SL2 if j < 10 else SL1)
                if (x * 2 + j) % 9 == 0:
                    c = SL2 if c == SL3 else SL3
                if j == 15:
                    c = EARTH_D if x % 4 == 0 else SL1
            elif name == "crown":
                # the crown road: packed shell and gravel, two wheel ruts, grass at its shoulders
                if j < 2 or j > 13:
                    c = GD if (x + j) % 2 else G
                else:
                    c = SHELL if hashn(x, j, 511) > 0.3 else STONE_L
                    if j in (5, 10):
                        c = EARTH if x % 3 else EARTH_D
                    if hashn(x, j, 512) < 0.05:
                        c = STONE
                    if j in (2, 13):
                        c = EARTH_D if x % 2 else STONE
            elif name == "slope_s":
                # the landward slope, lit
                c = GL if j < 5 else (G if j < 11 else GD)
                if (x * 3 + j * 2) % 11 == 0:
                    c = GL if c != GL else G
            else:   # toe
                c = GD if j < 4 else GRASS(i, j)
                if j < 4 and (x + j) % 3 == 0:
                    c = SL1
                if j == 4 and x % 2:
                    c = GD
            cv.put(i, j, c)
    return cv


def shack():
    """3x3 the levee watchman's shack: a corrugated tin roof, plank walls, a door with a storm lantern lit beside it."""
    cv = Canvas(3, 3)
    for j in range(48):
        for i in range(48):
            cv.put(i, j, GRASS(i, j))
    # roof (a shed roof sloping south)
    for j in range(4, 22):
        for i in range(3, 45):
            c = S2 if (i % 4) < 2 else S1
            if j == 4:
                c = S3
            if (i * 5 + j) % 31 == 0:
                c = WB1                                                  # rust spots
            cv.put(i, j, c)
    cv.hline(2, 45, 3, INK)
    cv.hline(2, 45, 22, INK)
    cv.vline(2, 3, 22, INK)
    cv.vline(45, 3, 22, INK)
    # walls
    for j in range(23, 43):
        for i in range(5, 43):
            c = WB2 if i % 5 else WB1
            if j == 23:
                c = WB0
            cv.put(i, j, c)
    cv.vline(4, 23, 43, INK)
    cv.vline(43, 23, 43, INK)
    cv.hline(4, 43, 43, INK)
    cv.rect(19, 28, 10, 15, WB1)                                         # the door
    cv.vline(19, 28, 42, WB0)
    cv.vline(28, 28, 42, WB0)
    cv.hline(19, 28, 28, WB0)
    cv.put(26, 35, BRASS)
    cv.rect(8, 28, 7, 6, S0)                                             # a window, dark
    cv.rect(9, 29, 2, 2, Y2)
    cv.hline(8, 14, 34, WB0)
    # the storm lantern on its hook, glowing
    cv.rect(33, 29, 4, 6, GLOW)
    cv.rect(34, 30, 2, 4, Y2)
    cv.hline(32, 37, 28, INK)
    cv.hline(32, 37, 35, INK)
    for (x, y) in [(31, 31), (38, 31), (34, 37), (35, 26)]:
        cv.put(x, y, GLOW)
    for i in range(6, 44):
        cv.put(i, 44, SH)
    return cv


def bell_post():
    """1x2 the crevasse bell: a brass bell hung in a little wooden frame on a post, its rope tied off."""
    cv = Canvas(1, 2)
    for j in range(32):
        for i in range(16):
            cv.put(i, j, GRASS(i, j))
    cv.vline(3, 2, 30, WB1)
    cv.vline(12, 2, 30, WB1)
    cv.vline(2, 2, 30, INK)
    cv.vline(13, 2, 30, INK)
    cv.vline(4, 2, 30, WB0)
    cv.vline(11, 2, 30, WB0)
    cv.rect(2, 1, 12, 2, WB2)
    cv.hline(1, 14, 0, INK)
    cv.hline(1, 14, 3, INK)
    for j in range(5, 14):
        hw = 1.5 + (j - 5) * 0.45
        for i in range(16):
            if abs(i + 0.5 - 8) <= hw:
                cv.put(i, j, BRASS if i < 8 else (GLOW if i < 10 else WB1))
    cv.hline(4, 11, 14, INK)
    cv.put(8, 15, WB0)
    cv.line(8, 16, 12, 24, Y2)                                           # the rope, tied off on the post
    cv.hline(1, 14, 31, SH)
    return cv


def sandbags():
    """2x1 sandbags stacked along the crown (burlap, tied ends)."""
    cv = Canvas(2, 1)
    for j in range(16):
        for i in range(32):
            cv.put(i, j, lev("crown", i // 16).get(i % 16, j))
    for (x, y) in [(2, 9), (11, 9), (20, 9), (6, 4), (15, 4), (24, 9)]:
        body = ellipse_body(x + 4, y + 2.5, 4.6, 2.8)
        for (i, j) in body:
            if 0 <= i < 32:
                cv.put(i, j, STONE_L if j < y + 2 else (SHELL if j < y + 4 else STONE))
        ink_outline(cv, body, OUTL, only_clear=False)
        cv.put(x + 1, y + 2, EARTH)
        cv.put(x + 7, y + 2, EARTH)
    return cv


def mile_post():
    """1x1 a white levee mile marker with a black band, on the crown's shoulder."""
    cv = lev("crown", 1)
    cv.rect(6, 2, 4, 11, STONE_L)
    cv.rect(6, 5, 4, 2, OUTL)
    cv.vline(5, 2, 12, OUTL)
    cv.vline(10, 2, 12, OUTL)
    cv.hline(5, 10, 1, OUTL)
    cv.hline(5, 10, 13, EARTH_D)
    return cv


def struck_pole():
    """1x3 a line pole on the crown, split down its length by lightning, its rod and cross-arm blackened."""
    cv = Canvas(1, 3)
    for j in range(48):
        for i in range(16):
            cv.put(i, j, GRASS(i, j))
    for j in range(4, 44):
        cv.put(6, j, WB2 if j > 20 else WB1)
        cv.put(7, j, WB1)
        cv.put(8, j, WB0 if (j // 3) % 2 else INK)                       # the split, charred
        cv.put(9, j, WB1)
        cv.put(5, j, INK)
        cv.put(10, j, INK)
    cv.rect(1, 8, 14, 2, WB0)
    cv.hline(0, 15, 7, INK)
    cv.hline(0, 15, 10, INK)
    for x in (2, 13):
        cv.put(x, 6, S2)
    cv.vline(7, 0, 4, INK)
    cv.vline(8, 0, 3, S0)
    for (x, y) in [(9, 1), (11, 3), (4, 2)]:
        cv.put(x, y, Y2)
    cv.hline(3, 12, 44, SH)
    return cv


# ---------------------------------------------------------------- the sheet
def build():
    P = RK.build()                                                      # batch 1 first: same order, same cells, same ids
    sky = sky_block()
    for k, cv in sky.items():
        P.add(f"sky_{k}", cv, comment="the storm round the lamp gallery (the map's fill and border block)", lair="zapdos")
    deck = dual_set(deck_style, ro=7, ri=5, wob=0)
    P.add_set("deck", deck, walk=True, comment="the gallery's iron deck and railing on the storm", lair="zapdos")
    spark = deck["N"].copy()
    for x in range(0, 16, 6):
        for (dx, dy, c) in [(0, -1, SP2), (0, -2, SP3), (1, -2, SP1), (-1, -3, SP2), (0, -4, SP1)]:
            yy = next((j for j in range(16) if spark.get(x, j) == S3), None)
            if yy is not None:
                spark.put(x + dx, yy + dy, c)
    P.add("deck_N_spark", spark, comment="the north rail, St Elmo's fire on its posts", lair="zapdos")
    P.add("deck_C2", deck_cell(rust=True), walk=True, comment="deck plates with rust streaks", lair="zapdos")
    P.add("deck_C3", deck_cell(puddle=True), walk=True, comment="a rain puddle on the deck", lair="zapdos")
    P.add("lantern", lantern(True), comment="4x4 the lantern room, lamp lit (blocking)", lair="zapdos")
    P.add("lantern_dark", lantern(False), comment="4x4 the lantern room, lamp out (during the story)", lair="zapdos")
    P.add("hatch", hatch(), walk=True, comment="1x1 the stair hatch down into the lighthouse (the warp)", lair="zapdos")
    P.add("flag_mast", flag_mast(), comment="1x3 the hurricane-warning flags on their mast, blocking", lair="zapdos")
    P.add("anemometer", anemometer(), comment="1x2 a cup anemometer, blocking", lair="zapdos")
    P.add("storm_lamp", storm_lamp(), comment="1x1 the keeper's storm lantern and oil can, blocking", lair="zapdos")
    P.add("rope", rope(), comment="1x1 a coil of rope, blocking", lair="zapdos")
    for n in ("riprap", "slope_n", "crown", "slope_s", "toe"):
        for v in (0, 1):
            P.add(f"{n}{v}", lev(n, v), walk=n in ("crown", "slope_s", "toe"), comment=f"the levee band: {n}", lair="thundurus")
    P.add("shack", shack(), comment="3x3 the levee watchman's shack, blocking", lair="thundurus")
    P.add("bell_post", bell_post(), comment="1x2 the crevasse bell, blocking", lair="thundurus")
    P.add("sandbags", sandbags(), comment="2x1 sandbags on the crown, blocking", lair="thundurus")
    P.add("mile_post", mile_post(), comment="1x1 a levee mile marker, blocking", lair="thundurus")
    P.add("struck_pole", struck_pole(), comment="1x3 a line pole split by lightning, blocking", lair="thundurus")
    return P


def families(P):
    fam = dict(RK.families(P))
    fam = {k: v for k, v in fam.items() if len(v) <= 15}
    fam.update(NEW_FAMILIES)
    return fam


def main():
    P = build()
    bad = write_b2(P, "lair_storm_b2.png", "orleans_lair_storm", "gTileset_OrleansLairStorm", "orleans_general.mapping.json",
                   families(P), "The storm lairs (Raikou; batch 2: Zapdos, Thundurus)", "make_lair_storm_b2.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_storm_b2: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

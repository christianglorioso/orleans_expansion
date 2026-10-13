"""Own art for Articuno's room: the frozen hall of the Pointe Rouge ice plant (PointeRouge_IcePlant, 19x14, the
existing room redone). Its own small secondary, gTileset_OrleansIcePlant on the interiors' primary
gTileset_OrleansBuilding.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_iceplant.py
writes tools/mapgen/tilesets/lairs/iceplant.png + iceplant.json and recipes/orleans_iceplant.json (source "ip").

    walls       cap (the steel roof girder), wall (corrugated steel panels furred with rime, icicles), wall_pipe (a
                rimed pipe run with a valve), wall_vent (a frozen fan grille), side_l / side_r, wall_s + corners
    floor       concrete (frosted, seams), ice_<key> (sheet ice on the concrete, a dual set), ice_crack
    hall        dais 3x2 (a raised block of ice the plant froze solid, frost crystals: Articuno's perch),
                light 3x3 (the shaft of cold light from the broken skylight: a pale pool, a drift of snow, glass
                shards), conveyor_l / conveyor / conveyor_r (a frozen belt run), ice_block (a block left on the belt),
                tank 2x2 (a brine tank, rimed), compressor 2x2 (the ammonia compressor, frozen), ice_stack 1x1
    exit        mat (the door mat, frosted; south-arrow warp)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import Canvas, Pieces, dual_set, hashn  # noqa: E402

INK = (24, 32, 48)
C1, C2, C3, C4 = (72, 80, 96), (104, 112, 128), (136, 144, 160), (168, 176, 192)     # concrete, cold
I1, I2, I3, I4, I5 = (120, 160, 192), (152, 192, 216), (184, 216, 232), (216, 236, 248), (248, 252, 255)  # ice
M1, M2, M3, M4 = (48, 56, 72), (80, 96, 112), (120, 136, 152), (168, 184, 200)       # steel
HZ, RS = (216, 176, 64), (152, 96, 72)                                               # hazard yellow, rust
CY = (96, 200, 224)                                                                  # cold light

FAMILIES = {
    "CONCRETE": [INK, C1, C2, C3, C4, I1, I2, I3, I4, I5, CY],
    "STEEL": [INK, M1, M2, M3, M4, I1, I2, I3, I4, I5, HZ, RS, C1, C2, C3],
}


def gp(x, y):
    """Frosted concrete, one slab per 16 px cell: seams, frost spreading from the seams, grit."""
    sx, sy = x % 16, y % 16
    if sx == 15 or sy == 15:
        return C1
    if sx == 14 or sy == 14:
        return I1 if (sx + sy) % 3 == 0 else C2
    n = hashn(sx, sy, 5)
    if n < 0.04:
        return C2
    if n > 0.98:
        return I4
    if (sx + 2 * sy) % 13 == 0:
        return I2
    return C3


def tex(cv, fn, x0=0, y0=0, w=None, h=None):
    w = cv.w if w is None else w
    h = cv.h if h is None else h
    for j in range(y0, y0 + h):
        for i in range(x0, x0 + w):
            cv.put(i, j, fn(i, j))


def ice_style(i, j, inside, d):
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1:
            return I1 if (i + j) % 2 else gp(i, j)
        return gp(i, j)
    if near == 1:
        return I2
    if d["ds"] is not None and d["ds"] <= 2:
        return I1                                   # the sheet's thick edge
    k = (i * 3 + j * 2) % 17
    if k in (0, 1):
        return I4
    if hashn(i, j, 9) < 0.04:
        return I5
    return I3


def ice_tex(i, j):
    return ice_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None})


# ---------------------------------------------------------------- walls
def cap():
    cv = Canvas(1, 1)
    tex(cv, lambda i, j: M1 if (i // 4 + j // 4) % 2 else INK)
    cv.rect(0, 9, 16, 4, M2)
    cv.hline(0, 15, 9, M3)
    for x in (2, 10):
        cv.put(x, 11, M4)                           # rivets
    cv.hline(0, 15, 13, I3)
    cv.hline(0, 15, 14, I4)
    cv.hline(0, 15, 15, M2)
    return cv


def wall(kind=""):
    """Corrugated steel panels, rime thick at the foot, icicles hanging from the top rail."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            c = M3 if i % 4 in (0, 1) else (M2 if i % 4 == 2 else M1)
            cv.put(i, j, c)
    cv.hline(0, 15, 0, M4)
    cv.hline(0, 15, 1, M2)
    for i in range(16):
        h = 3 + int(3 * hashn(i // 2, 0, 3))
        for j in range(16 - h, 16):
            cv.put(i, j, I3 if (i + j) % 3 else I4)
        cv.put(i, 15 - h, I2)
    for (x, n) in [(3, 5), (7, 3), (12, 6)]:
        for k in range(n):
            cv.put(x, 2 + k, I4 if k < n - 1 else I5)
    if kind == "pipe":
        cv.rect(0, 5, 16, 4, M2)
        cv.hline(0, 15, 5, M4)
        cv.hline(0, 15, 8, M1)
        for i in range(0, 16, 3):
            cv.put(i, 4, I4)
            cv.put(i + 1, 9, I5)
        cv.rect(6, 3, 4, 2, RS)
        cv.hline(5, 10, 3, HZ)
    elif kind == "vent":
        cv.rect(3, 3, 10, 9, INK)
        cv.rect(4, 4, 8, 7, M1)
        for k in range(4, 11, 2):
            cv.hline(4, 11, k, M3)
        cv.line(4, 4, 11, 10, I3)
        cv.line(11, 4, 4, 10, I3)
        cv.put(8, 7, I5)
    return cv


def side(right=False):
    cv = Canvas(1, 1)
    tex(cv, lambda i, j: M1 if (i // 4 + j // 4) % 2 else INK)
    for j in range(16):
        cv.put(12, j, M2)
        cv.put(13, j, I3 if j % 5 else I4)
        cv.put(14, j, M3)
        cv.put(15, j, INK)
    if right:
        cv.flip_x()
    return cv


def wall_s(corner=None):
    cv = Canvas(1, 1)
    tex(cv, lambda i, j: M1 if (i // 4 + j // 4) % 2 else INK)
    band = {0: INK, 1: M3, 2: I4, 3: M2}
    for j in range(16):
        for i in range(16):
            d = j if corner is None else max((15 - i) if corner == "sw" else i, j)
            if d in band:
                cv.put(i, j, band[d])
    return cv


# ---------------------------------------------------------------- the hall
def floor_crack():
    cv = Canvas(1, 1)
    tex(cv, ice_tex)
    pts = [(1, 3), (5, 6), (7, 6), (9, 10), (13, 12), (15, 13)]
    for k in range(len(pts) - 1):
        cv.line(*pts[k], *pts[k + 1], I1)
    cv.line(7, 6, 9, 1, I1)
    for (x, y) in pts:
        cv.put(x, y + 1, I5)
    return cv


def dais():
    """3x2 a raised block of ice: the plant's brine froze solid round its mould, now a clear-blue slab with frost
    feathers on its top and a stepped, faceted front (Articuno's perch)."""
    cv = Canvas(3, 2)
    tex(cv, gp)
    cv.rect(3, 4, 42, 14, I3)
    cv.hline(3, 44, 4, I5)
    cv.hline(3, 44, 5, I4)
    cv.rect(3, 18, 42, 9, I2)
    cv.hline(3, 44, 18, I4)
    for x in range(6, 44, 7):
        cv.line(x, 19, x - 2, 26, I1)
    cv.hline(3, 44, 27, I1)
    cv.vline(2, 4, 27, INK)
    cv.vline(45, 4, 27, INK)
    cv.hline(2, 45, 3, INK)
    cv.hline(2, 45, 28, INK)
    # frost feathers on the top
    for (cx, cy) in [(10, 10), (24, 9), (37, 12), (17, 14), (31, 15)]:
        for a in range(6):
            ang = a * math.pi / 3
            cv.line(cx, cy, round(cx + 3 * math.cos(ang)), round(cy + 2 * math.sin(ang)), I5)
    for x in range(2, 46, 5):
        cv.put(x, 29, I1)
        cv.put(x + 1, 30, I2)
    return cv


def light():
    """3x3 the shaft of cold light from the broken skylight: a pale pool on the ice, a drift of snow that fell
    through, glass shards glinting in it."""
    cv = Canvas(3, 3)
    tex(cv, ice_tex)
    for j in range(48):
        for i in range(48):
            v = ((i + 0.5 - 24) / 22) ** 2 + ((j + 0.5 - 24) / 20) ** 2
            if v < 1.0:
                c = cv.get(i, j)
                lit = {I3: I4, I4: I5, I2: I3, I1: I2}.get(c, c)
                if v < 0.55 or (i + j) % 2 == 0:
                    cv.put(i, j, lit)
    # the snow drift
    for j in range(48):
        for i in range(48):
            v = ((i + 0.5 - 20) / 13) ** 2 + ((j + 0.5 - 26) / 8) ** 2
            if v < 1.0:
                cv.put(i, j, I5 if v < 0.7 else I4)
    for (x, y) in [(14, 24), (25, 21), (30, 30), (19, 32), (34, 18)]:
        cv.put(x, y, CY)
        cv.put(x + 1, y, I1)
    return cv


def conveyor(kind):
    """A frozen conveyor run east-west: steel frame, belt slats under rime; ends with the drum."""
    cv = Canvas(1, 1)
    tex(cv, gp)
    cv.rect(0, 3, 16, 9, M1)
    for x in range(0, 16, 3):
        cv.vline(x, 4, 10, M3)
    cv.hline(0, 15, 3, M4)
    cv.hline(0, 15, 11, INK)
    cv.hline(0, 15, 12, M2)
    for i in range(0, 16, 2):
        cv.put(i, 4, I4)
        cv.put(i + 1, 5, I3)
    if kind == "l":
        cv.rect(0, 2, 4, 11, M2)
        cv.vline(0, 2, 12, INK)
        cv.put(2, 7, M4)
    elif kind == "r":
        cv.rect(12, 2, 4, 11, M2)
        cv.vline(15, 2, 12, INK)
        cv.put(13, 7, M4)
    elif kind == "block":
        cv.rect(3, 0, 10, 9, I3)
        cv.hline(3, 12, 0, I5)
        cv.vline(3, 0, 8, I4)
        cv.vline(12, 0, 8, I1)
        cv.hline(3, 12, 8, I1)
        cv.put(6, 3, I5)
    for i in range(16):
        cv.put(i, 13, C2)
    return cv


def tank():
    """2x2 a brine tank: a squat steel drum furred with rime, a gauge, a hazard band, frost spreading round it."""
    cv = Canvas(2, 2)
    tex(cv, gp)
    for j in range(32):
        for i in range(32):
            v = ((i + 0.5 - 16) / 16) ** 2 + ((j + 0.5 - 18) / 14) ** 2
            if v < 1.0 and (i + j) % 2 == 0:
                cv.put(i, j, I2)
    cv.rect(5, 8, 22, 18, M2)
    cv.vline(5, 8, 25, M4)
    cv.vline(6, 8, 25, M3)
    cv.vline(25, 8, 25, M1)
    cv.ellipse(16, 8, 11, 4, M1)
    cv.ellipse(16, 7.5, 10, 3.2, M4)
    cv.ellipse(16, 7.5, 8, 2.2, I4)
    cv.hline(5, 26, 18, HZ)
    cv.hline(5, 26, 19, M1)
    cv.ellipse(20, 13, 2.5, 2.5, INK)
    cv.ellipse(20, 13, 1.6, 1.6, I5)
    cv.line(20, 13, 21, 12, RS)
    for i in range(5, 27):
        cv.put(i, 26, INK)
        if i % 2:
            cv.put(i, 25, I4)
    cv.vline(4, 8, 26, INK)
    cv.vline(27, 8, 26, INK)
    return cv


def compressor():
    """2x2 the compressor that froze the plant: a steel housing, flywheel, gauges, pipes thick with ice."""
    cv = Canvas(2, 2)
    tex(cv, gp)
    cv.rect(3, 6, 26, 20, M2)
    cv.hline(3, 28, 6, M4)
    cv.rect(4, 8, 12, 10, M1)
    cv.ellipse(10, 13, 5, 5, M3)
    cv.ellipse(10, 13, 3, 3, M1)
    cv.put(10, 13, M4)
    for (x, y) in [(20, 10), (25, 10)]:
        cv.ellipse(x, y, 2.2, 2.2, INK)
        cv.ellipse(x, y, 1.4, 1.4, I5)
    cv.rect(18, 15, 9, 3, HZ)
    for x in range(18, 27, 3):
        cv.put(x, 16, INK)
    cv.rect(26, 0, 3, 6, M3)
    cv.vline(26, 0, 6, M4)
    for i in range(3, 29):
        cv.put(i, 26, INK)
    cv.vline(2, 6, 26, INK)
    cv.vline(29, 6, 26, INK)
    for i in range(3, 29, 2):
        cv.put(i, 7, I4)
        cv.put(i + 1, 25, I3)
    for (x, n) in [(5, 4), (14, 3), (22, 5)]:
        for k in range(n):
            cv.put(x, 19 + k, I4)
    return cv


def ice_stack():
    cv = Canvas(1, 1)
    tex(cv, gp)
    for (x, y, w, h) in [(1, 6, 7, 6), (8, 7, 7, 5), (4, 1, 7, 6)]:
        cv.rect(x, y, w, h, I3)
        cv.hline(x, x + w - 1, y, I5)
        cv.vline(x, y, y + h - 1, I4)
        cv.vline(x + w - 1, y, y + h - 1, I1)
        cv.hline(x, x + w - 1, y + h - 1, I1)
        cv.hline(x, x + w - 1, y + h, INK)
    return cv


def mat():
    cv = Canvas(1, 1)
    tex(cv, gp)
    cv.rect(1, 3, 14, 10, M1)
    for x in range(2, 14, 2):
        cv.vline(x, 4, 11, M2)
    cv.hline(1, 14, 3, M3)
    cv.hline(1, 14, 12, INK)
    for (x, y) in [(3, 5), (9, 8), (12, 4)]:
        cv.put(x, y, I4)
    return cv


def void():
    return Canvas(1, 1, fill=INK)


def build():
    P = Pieces("ip")
    P.add("void", void(), comment="outside (black)", lair="articuno")
    P.add("cap", cap(), comment="the back wall's top: the roof girder", lair="articuno")
    P.add("wall", wall(), comment="corrugated steel wall, rimed, icicles", lair="articuno")
    P.add("wall_pipe", wall("pipe"), comment="the wall with a rimed pipe run and a valve", lair="articuno")
    P.add("wall_vent", wall("vent"), comment="the wall with a frozen fan grille", lair="articuno")
    P.add("side_l", side(False), comment="left side wall", lair="articuno")
    P.add("side_r", side(True), comment="right side wall", lair="articuno")
    P.add("wall_s", wall_s(), comment="south wall", lair="articuno")
    P.add("wall_sw", wall_s("sw"), comment="south-west corner", lair="articuno")
    P.add("wall_se", wall_s("se"), comment="south-east corner", lair="articuno")
    P.add("floor", (lambda c: (tex(c, gp), c)[1])(Canvas(1, 1)), walk=True, comment="frosted concrete", lair="articuno")
    P.add_set("ice", dual_set(ice_style, ro=6, ri=5, wob=1), walk=True, comment="sheet ice on the concrete",
              lair="articuno")
    P.add("ice_crack", floor_crack(), walk=True, comment="sheet ice, cracked", lair="articuno")
    P.add("dais", dais(), comment="3x2 the ice dais (Articuno's perch), blocking", lair="articuno")
    P.add("light", light(), walk=True, comment="3x3 the shaft of cold light from the broken skylight, a snow drift "
                                               "(walkable; place it on sheet ice)", lair="articuno")
    for k, n in (("l", "conveyor_l"), ("m", "conveyor"), ("r", "conveyor_r"), ("block", "ice_block")):
        P.add(n, conveyor(k), comment=f"frozen conveyor ({n}), blocking", lair="articuno")
    P.add("tank", tank(), comment="2x2 a rimed brine tank, blocking", lair="articuno")
    P.add("compressor", compressor(), comment="2x2 the frozen compressor, blocking", lair="articuno")
    P.add("ice_stack", ice_stack(), comment="1x1 stacked ice blocks, blocking", lair="articuno")
    P.add("mat", mat(), walk=True, comment="the door mat (south-arrow warp: the exit)", lair="articuno",
          behavior={(0, 0): "MB_SOUTH_ARROW_WARP"})
    return P


def main():
    P = build()
    bad = P.write("iceplant.png", "orleans_iceplant", "gTileset_OrleansIcePlant", "orleans_building.mapping.json",
                  FAMILIES, "The frozen hall of the Pointe Rouge ice plant (Articuno)")
    for b in bad[:20]:
        print("off-family:", b)
    print(f"iceplant: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

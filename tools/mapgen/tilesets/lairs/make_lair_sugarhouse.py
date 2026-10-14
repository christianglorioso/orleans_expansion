"""Own art for Moltres' lair (legendary lairs batch 2): the boiling house of the old sugar mill on Route 17, behind the mill's own plank door.
Its own small secondary, gTileset_OrleansLairSugarhouse on the interiors' primary (gTileset_OrleansBuilding), prefix lm, like the ice plant.

The lore: Louisiana's sugarhouses boiled the cane juice down in a "Jamaica train", a row of great iron kettles set in a brick furnace
bench, the fire under the smallest kettle (the batterie) and its draught pulled along under the others to the chimney. This mill was
shut long ago, but its fire never went out: Moltres keeps it, roosting over the batterie.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_sugarhouse.py
writes tools/mapgen/tilesets/lairs/lair_sugarhouse.png + lair_sugarhouse.json and recipes_b2/orleans_lair_sugarhouse.json (source "lm").

Every cell is own art (no primary piece is used, as in the ice plant), opaque.
    cap, wall, wall_window, wall_tools   the north wall: the brick wall top; the brick face; an arched barred window with daylight in it;
                                         skimmers and ladles hung on pegs
    side_l / side_r, wall_s / wall_sw / wall_se, mat   the side and south walls, the corners, the door mat (south-arrow warp)
    floor, floor_bagasse, floor_glow     the packed-earth floor; strewn with bagasse (crushed cane); lit red by the furnace
    batterie / sirop / flambeau / grande 3x3   the Jamaica train: four iron kettles, smallest to largest, set in the brick bench;
                                         the batterie over the open furnace mouth, burning; syrup boiling in each
    flue 2x3                             the bench's flue rising into the chimney stack in the north-east corner
    cooler 3x1                           a wooden sugar cooler, brown sugar crystallising in it
    hogshead 1x1                         a molasses hogshead; cane 2x2 (cut cane stacked by the carrier); ash 1x1 (raked-out ash, walkable)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import Canvas, Pieces, bricks, ellipse_body, hashn, ink_outline, write_b2  # noqa: E402

INK = (40, 40, 48)
BR1, BR2, BR3, MOR = (200, 128, 88), (144, 88, 80), (128, 80, 72), (88, 72, 80)
SOOT = (64, 56, 56)
SKY1, SKY2 = (232, 224, 176), (176, 200, 200)
E1, E2, E3 = (168, 136, 96), (136, 104, 72), (104, 80, 56)
BAG1, BAG2 = (208, 184, 120), (168, 144, 88)
FE1, FE2, FE3 = (120, 120, 128), (72, 72, 80), (152, 152, 160)
SY1, SY2, SY3 = (232, 176, 72), (200, 128, 48), (152, 80, 32)
EM1, EM2, EM3, EM4 = (152, 40, 24), (216, 88, 32), (248, 160, 48), (248, 232, 136)
WD1, WD2, WD3 = (88, 64, 48), (136, 104, 72), (184, 152, 104)
CN1, CN2, CN3 = (64, 104, 48), (112, 152, 64), (184, 192, 96)

FAMILIES = {
    "WALL": [BR1, BR2, BR3, MOR, INK, SOOT, SKY1, SKY2, FE1, FE2, WD1, WD2, E1, E2, E3],
    "FRONT": [E1, E2, E3, INK, BR1, BR2, BR3, MOR, FE1, FE2, EM1, EM2, EM3, EM4, SOOT],
    "FLOOR": [E1, E2, E3, BAG1, BAG2, INK, BR2, MOR, EM1, EM2, EM3, SOOT, WD1, WD2],
    "KETTLE": [FE1, FE2, FE3, INK, BR1, BR2, BR3, MOR, SY1, SY2, SY3, EM1, EM2, EM3, EM4],
    "WOOD": [WD1, WD2, WD3, INK, E1, E2, E3, SY1, SY2, SY3, FE1, FE2, BAG1, BAG2],
    "CANE": [CN1, CN2, CN3, BAG1, BAG2, E1, E2, E3, INK, WD1, WD2],
}


def floor_tex(i, j):
    n = hashn(i, j, 801)
    if n < 0.06:
        return E3
    if n > 0.9:
        return E1
    return E2 if (i * 3 + j * 5) % 11 else E3


def floor_cv(w=1, h=1, kind="plain"):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            c = floor_tex(i, j)
            if kind == "bagasse":
                # crushed cane fibres: short pale strokes lying every which way
                for (x0, y0, dx, dy) in [(2, 3, 1, 0), (7, 2, 1, 1), (11, 5, 1, -1), (4, 9, 1, 0), (9, 11, 1, 1), (12, 13, 1, 0),
                                         (1, 13, 1, -1), (6, 6, 0, 1)]:
                    for k in range(5):
                        if (i, j) == (x0 + dx * k, y0 + dy * k):
                            c = BAG1 if k % 2 else BAG2
            if kind.startswith("glow"):
                # the furnace's light on the floor: an ordered dither, denser near the fire (north)
                bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]][j % 4][i % 4]
                t = (1.0 - j / 16.0) * 0.8
                if kind == "glow_l":
                    t *= (i + 1) / 16.0
                elif kind == "glow_r":
                    t *= (16 - i) / 16.0
                if bayer < t * 16:
                    c = EM1 if bayer > t * 8 else EM2
            cv.put(i, j, c)
    return cv


# ---------------------------------------------------------------- walls
def cap():
    """1x1 the north wall's top: the brick wall head seen from above, sooted."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, SOOT if j < 12 else (BR3 if j < 15 else INK))
            if j < 12 and (i + j * 3) % 9 == 0:
                cv.put(i, j, MOR)
    return cv


def wall(kind="plain"):
    """1x1 the brick wall face: plain, an arched barred window full of daylight, or skimmers and ladles on pegs."""
    cv = Canvas(1, 1)
    bricks(cv, 0, 0, 16, 16, (BR1, BR2, BR3), MOR, course=4, brick=8, wear=0.02, seed=4)
    for i in range(16):
        cv.put(i, 15, SOOT)
    for j in range(0, 6):
        for i in range(16):
            if hashn(i, j, 804) < 0.25 - j * 0.04:
                cv.put(i, j, SOOT)                                       # soot from the fires, darkest at the top
    if kind == "window":
        for j in range(3, 14):
            for i in range(4, 12):
                dx = i + 0.5 - 8
                if j >= 3 + dx * dx / 6:
                    cv.put(i, j, SKY1 if j < 8 else SKY2)
        for x in (6, 9):
            cv.vline(x, 4, 13, FE2)
        cv.hline(4, 11, 9, FE2)
        cv.hline(3, 12, 14, INK)
    elif kind == "tools":
        cv.hline(2, 13, 4, WD1)
        for (x, ln, head) in [(3, 8, "ladle"), (7, 9, "skim"), (11, 7, "ladle")]:
            cv.vline(x, 4, 4 + ln, WD2)
            if head == "ladle":
                for (i, j) in ellipse_body(x + 0.5, 4 + ln + 1, 2.0, 1.4):
                    cv.put(i, j, FE1 if j < 4 + ln + 1 else FE2)
            else:
                cv.rect(x - 2, 4 + ln, 5, 3, FE1)
                for i in range(x - 2, x + 3):
                    if i % 2:
                        cv.put(i, 4 + ln + 1, INK)
    return cv


def side(right):
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            c = SOOT if (i < 12 if not right else i > 3) else BR3
            if (i == 12 and not right) or (i == 3 and right):
                c = INK
            if c == SOOT and (i + j * 3) % 9 == 0:
                c = MOR
            cv.put(i, j, c)
    return cv


def wall_s(corner=None):
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            c = SOOT if j > 3 else (BR3 if j > 0 else INK)
            if c == SOOT and (i * 3 + j) % 9 == 0:
                c = MOR
            cv.put(i, j, c)
    if corner == "sw":
        for j in range(16):
            for i in range(13):
                cv.put(i, j, SOOT if (i + j * 3) % 9 else MOR)
            cv.put(12, j, INK)
    if corner == "se":
        for j in range(16):
            for i in range(4, 16):
                cv.put(i, j, SOOT if (i + j * 3) % 9 else MOR)
            cv.put(3, j, INK)
    return cv


def mat():
    """1x1 the threshold: worn planks before the door, daylight under it (the south-arrow warp)."""
    cv = floor_cv()
    for j in range(2, 16):
        for i in range(2, 14):
            cv.put(i, j, WD2 if j % 4 else WD1)
    cv.hline(2, 13, 15, E1)
    return cv


# ---------------------------------------------------------------- the Jamaica train
def kettle(size, fire=False):
    """3x3 one station of the Jamaica train: an iron kettle (r = size) set in the brick bench, syrup boiling in it; the bench's front
    face below, its fire door (the batterie: the open furnace mouth, burning)."""
    cv = floor_cv(3, 3)
    # the bench: brick top (rows 0..33), the front face (34..44)
    for j in range(0, 45):
        for i in range(48):
            if j < 34:
                c = BR2 if (i // 8 + j // 4) % 2 else BR3
                if j % 4 == 3 or (i + (4 if (j // 4) % 2 else 0)) % 8 == 0:
                    c = MOR
            else:
                c = BR3 if j < 36 else BR2
                if (j - 34) % 4 == 3 or (i + (4 if ((j - 34) // 4) % 2 else 0)) % 8 == 0:
                    c = MOR
            cv.put(i, j, c)
    cv.hline(0, 47, 34, INK)
    cv.hline(0, 47, 45, INK)
    for i in range(48):
        cv.put(i, 46, E3)
    # the kettle: an iron rim round boiling syrup
    r = size
    rim = ellipse_body(24, 17, r, r * 0.8)
    inner = ellipse_body(24, 17.5, r - 2.5, (r - 2.5) * 0.8)
    for (i, j) in rim:
        cv.put(i, j, FE3 if j < 15 and i < 24 else (FE1 if j < 19 else FE2))
    for (i, j) in inner:
        v = hashn(i, j, 811 + size)
        c = SY2
        if v < 0.15:
            c = SY1
        elif v > 0.88:
            c = SY3
        if (i + j) % 7 == 0 and v > 0.5:
            c = EM4 if fire else SY1                                     # bubbles
        cv.put(i, j, c)
    ink_outline(cv, rim, INK, only_clear=False)
    # steam / heat shimmer over it
    for (x, y) in [(18, 3), (22, 1), (28, 4), (31, 2)]:
        if r > 8:
            cv.put(x, y, FE3)
    # the fire door in the front face
    if fire:
        for j in range(36, 45):
            for i in range(16, 33):
                dx = i + 0.5 - 24
                if j >= 36 + dx * dx / 18:
                    c = EM2
                    if j > 40 and abs(dx) < 5:
                        c = EM4 if j > 42 else EM3
                    elif abs(dx) > 6:
                        c = EM1
                    cv.put(i, j, c)
        for i in range(16, 33):
            cv.put(i, 46, EM1 if i % 2 else E3)                          # glow on the floor before it
    else:
        cv.rect(19, 37, 10, 7, FE2)
        cv.hline(19, 28, 37, FE1)
        cv.rect(22, 40, 4, 2, EM1)                                       # the draught's glow behind the closed door
    return cv


def flue():
    """2x4 the chimney stack in the north-east corner, the bench's flue turning up into it: a square brick stack, sooted near its top,
    an iron damper door and its handle."""
    cv = floor_cv(2, 4)
    for j in range(0, 61):
        for i in range(2, 30):
            c = BR2 if (i // 8 + j // 4) % 2 else BR3
            if j % 4 == 3 or (i + (4 if (j // 4) % 2 else 0)) % 8 == 0:
                c = MOR
            if i < 6:
                c = BR1 if c != MOR else MOR                             # its lit west face
            if j < 14 and hashn(i, j // 2, 821) < 0.55 - j * 0.035:
                c = SOOT
            cv.put(i, j, c)
    cv.vline(1, 0, 61, INK)
    cv.vline(30, 0, 61, INK)
    cv.hline(1, 30, 61, INK)
    cv.rect(10, 40, 12, 9, FE2)
    cv.hline(10, 21, 40, FE1)
    cv.rect(13, 43, 6, 3, EM1)
    cv.hline(19, 23, 44, FE1)
    for i in range(2, 31):
        cv.put(i, 62, E3)
    return cv


def cooler():
    """3x1 a wooden sugar cooler: a shallow trough on legs, brown sugar crystallising in the molasses."""
    cv = floor_cv(3, 1)
    cv.rect(2, 2, 44, 10, WD2)
    cv.hline(2, 45, 2, WD3)
    for j in range(4, 10):
        for i in range(4, 44):
            v = hashn(i, j, 831)
            cv.put(i, j, SY3 if v < 0.4 else (SY2 if v < 0.85 else SY1))
    cv.hline(1, 46, 1, INK)
    cv.hline(1, 46, 12, INK)
    cv.vline(1, 1, 12, INK)
    cv.vline(46, 1, 12, INK)
    for x in (4, 42):
        cv.rect(x, 13, 2, 2, WD1)
    return cv


def hogshead():
    """1x1 a molasses hogshead, its hoops rusted, a dark drip down its side."""
    cv = floor_cv()
    body = ellipse_body(8, 8, 6, 7)
    for (i, j) in body:
        cv.put(i, j, WD3 if i < 6 else (WD2 if i < 11 else WD1))
    for y in (4, 12):
        for i in range(2, 15):
            if (i, y) in body:
                cv.put(i, y, FE2)
    for (i, j) in ellipse_body(8, 2.5, 4.5, 1.5):
        cv.put(i, j, SY3)
    cv.vline(10, 3, 9, SY3)
    ink_outline(cv, body, INK, only_clear=False)
    return cv


def cane():
    """2x2 cut cane stacked by the carrier, bundled, leaves still on some."""
    cv = floor_cv(2, 2)
    for k in range(9):
        y = 6 + k * 2.6
        for i in range(2, 30):
            c = CN2 if (i // 5 + k) % 2 else CN1
            if i % 7 == 0:
                c = BAG2                                                 # the cane's joints
            cv.put(i, round(y), c)
            cv.put(i, round(y) + 1, CN1 if c != BAG2 else BAG2)
    for (x, y) in [(3, 4), (12, 3), (24, 5), (28, 2)]:
        cv.line(x, y, x + 4, y - 3, CN3)
    cv.hline(1, 30, 29, INK)
    cv.vline(9, 6, 28, WD1)
    cv.vline(22, 6, 28, WD1)
    return cv


def ash():
    """1x1 ash raked out of the furnace (walkable)."""
    cv = floor_cv()
    for (i, j) in ellipse_body(8, 9, 7, 4.5):
        v = hashn(i, j, 841)
        cv.put(i, j, SOOT if v < 0.5 else (MOR if v < 0.9 else EM1))
    return cv


def build():
    P = Pieces("lm")
    P.add("cap", cap(), comment="the north wall's top", lair="moltres")
    P.add("wall", wall(), comment="the brick wall", lair="moltres")
    P.add("wall_window", wall("window"), comment="an arched barred window, daylight", lair="moltres")
    P.add("wall_tools", wall("tools"), comment="skimmers and ladles on pegs", lair="moltres")
    P.add("side_l", side(False), comment="left side wall", lair="moltres")
    P.add("side_r", side(True), comment="right side wall", lair="moltres")
    P.add("wall_s", wall_s(), comment="south wall", lair="moltres")
    P.add("wall_sw", wall_s("sw"), comment="south-west corner", lair="moltres")
    P.add("wall_se", wall_s("se"), comment="south-east corner", lair="moltres")
    P.add("floor", floor_cv(), walk=True, comment="packed earth floor", lair="moltres")
    P.add("floor_bagasse", floor_cv(kind="bagasse"), walk=True, comment="floor strewn with bagasse", lair="moltres")
    P.add("floor_glow", floor_cv(kind="glow"), walk=True, comment="floor lit red by the furnace (near)", lair="moltres")
    P.add("floor_glow_l", floor_cv(kind="glow_l"), walk=True, comment="floor lit by the furnace (its west fringe)", lair="moltres")
    P.add("floor_glow_r", floor_cv(kind="glow_r"), walk=True, comment="floor lit by the furnace (its east fringe)", lair="moltres")
    P.add("batterie", kettle(8, fire=True), comment="3x3 the batterie: the smallest kettle over the open fire, blocking", lair="moltres")
    P.add("sirop", kettle(10), comment="3x3 the sirop kettle, blocking", lair="moltres")
    P.add("flambeau", kettle(12), comment="3x3 the flambeau kettle, blocking", lair="moltres")
    P.add("grande", kettle(14), comment="3x3 the grande, the largest kettle, blocking", lair="moltres")
    P.add("flue", flue(), comment="2x4 the chimney stack the flue rises into, blocking", lair="moltres")
    P.add("cooler", cooler(), comment="3x1 a sugar cooler, blocking", lair="moltres")
    P.add("hogshead", hogshead(), comment="1x1 a molasses hogshead, blocking", lair="moltres")
    P.add("cane", cane(), comment="2x2 stacked cut cane, blocking", lair="moltres")
    P.add("ash", ash(), walk=True, comment="1x1 raked-out ash (walkable)", lair="moltres")
    P.add("mat", mat(), walk=True, comment="the threshold (south-arrow warp: the exit)", lair="moltres",
          behavior={(0, 0): "MB_SOUTH_ARROW_WARP"})
    return P


def main():
    P = build()
    bad = write_b2(P, "lair_sugarhouse.png", "orleans_lair_sugarhouse", "gTileset_OrleansLairSugarhouse",
                   "orleans_building.mapping.json", FAMILIES, "The sugarhouse (Moltres)", "make_lair_sugarhouse.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_sugarhouse: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

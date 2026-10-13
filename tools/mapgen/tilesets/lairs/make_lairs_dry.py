"""Own art for the two dry-country lairs (one shared secondary, gTileset_OrleansLairsDry on gTileset_OrleansGeneral):
the Bloodmoon Ursaluna's arroyo den (Route 23) and Entei's burned pepper field (Route 16).

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lairs_dry.py
writes tools/mapgen/tilesets/lairs/lairs_dry.png + lairs_dry.json and recipes/orleans_lairs_dry.json (source "ld").

Every piece is an opaque cell (props baked over their ground). The plain dry ground (dry:0_0) comes from the
primary; the dry-country sets and the dry scrub border are COPIED from their sheets (make_dry_country.py,
make_borders.py) so these maps look like the routes they open off.
    shared     block_XY / S0 S1 N0 N1 E0 E1 W0 W1 / in_* / out_*: the dry scrub wall and its edge cells (border art)
    ursaluna   rock_<key>, rock_C*, rock_face* (the dry country's rock wall set, copied), clay_<key> (red earth on dry
               ground, copied: the red clay of the arroyo bed), den 4x3 (a leaning rock overhang over a bedding hollow
               of leaves, fur and broken branches), rock_face_claw (the face gouged by claws), scarred_stump 1x1,
               bones 1x1, fur 1x1, rock / rock_l (boulders, copied)
    entei      pepper (the dry country's pepper rows, copied), pepper_burnt (the same burned black), ash_<key> (ash
               over dry ground, embers in it), brazier 1x2 (a stone brazier, burning), vent 1x1 (glowing cracks in the ash),
               stubble 1x1 (burned cane stubs)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import (CORNER_KEYS, MAPGEN, SRC, Canvas, Pieces, dual_set, gba, hashn, over, pcell,  # noqa: E402
                      sheet_cell, tex_from)

DRY = tex_from(pcell("dry:0_0"))
DH, D1, D2, D3 = (240, 224, 184), (224, 200, 144), (200, 168, 112), (160, 128, 88)
ST, ST_D = (216, 184, 88), (176, 144, 64)
K0, K1, K2, K3 = (104, 96, 80), (152, 144, 120), (200, 192, 168), (240, 232, 216)
B0, B1, B2 = (64, 40, 32), (104, 72, 48), (144, 104, 64)
L0, L1, L2, L3, L4 = (24, 48, 32), (40, 80, 48), (64, 112, 56), (96, 144, 64), (152, 184, 88)
RE_L, RE, RE_D, RE_DD = (224, 176, 136), (200, 144, 104), (168, 112, 80), (136, 88, 64)
# char, ash, fire
CH0, CH1, CH2, CH3 = (32, 28, 32), (56, 48, 48), (88, 80, 72), (128, 120, 112)
ASH1, ASH2 = (168, 160, 152), (208, 200, 192)
EM1, EM2, EM3, EM4 = (152, 40, 24), (216, 88, 32), (248, 160, 48), (248, 232, 136)
# fur and bedding
FU1, FU2, FU3 = (72, 48, 40), (112, 72, 56), (152, 104, 80)
LV1, LV2 = (136, 112, 56), (176, 144, 72)

# the rock wall's own greys (make_dry_country v3) and the primary's dry ground (dry:0_0 adds DL)
R0, R1, R2, R3, R4, R5, R6 = (40, 40, 40), (64, 64, 64), (96, 92, 96), (128, 124, 128), (160, 156, 152), (200, 196, 184), (240, 232, 216)
DL = (248, 232, 184)
BONE = R6
FAMILIES = {
    "SCRUB": [DH, D1, D2, D3, ST, ST_D, L0, L1, L2, L3, L4, K0, K1, K2, B0],
    "ROCK": [DH, D1, D2, D3, DL, R0, R1, R2, R3, R4, R5, R6, B0, B1],
    "CLAY": [DH, D1, D2, D3, DL, RE_L, RE, RE_D, RE_DD, B0],
    "DEN": [D1, D2, D3, DL, R1, R2, R3, R4, R6, B0, FU1, FU2, FU3, LV1, LV2],
    "FIRE": [DH, D1, D2, D3, DL, CH0, CH1, CH2, CH3, ASH1, EM1, EM2, EM3, EM4, (96, 56, 40)],
}


def ground(fn, w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, fn(i, j))
    return cv


def dc(name):
    """A cell of the dry-country sheet by its terrain name (the first if it is a list)."""
    t = json.load(open(os.path.join(SRC, "dry_country.json")))["terrain"][name]
    xy = t[0] if isinstance(t[0], list) else t
    return sheet_cell(os.path.join(SRC, "dry_country.png"), xy[0], xy[1])


def dc_list(name):
    t = json.load(open(os.path.join(SRC, "dry_country.json")))["terrain"][name]
    return [sheet_cell(os.path.join(SRC, "dry_country.png"), x, y) for x, y in t]


def border(name):
    xy = json.load(open(os.path.join(SRC, "borders.json")))["cells"][name]
    return sheet_cell(os.path.join(SRC, "borders.png"), xy[0], xy[1])


# ---------------------------------------------------------------- the burned cane wall (recoloured copy)
BURN = {(40, 72, 40): CH0, (72, 112, 48): CH1, (112, 152, 56): CH2, (160, 192, 80): CH3, (208, 224, 128): ASH1,
        (200, 192, 104): CH3, (144, 144, 64): CH1}


def burnt(cv):
    cv = cv.copy()
    for j in range(cv.h):
        for i in range(cv.w):
            c = cv.get(i, j)
            if c in BURN:
                c2 = BURN[c]
                if c2 == CH3 and hashn(i, j, 77) < 0.08:
                    c2 = EM2                         # a last ember in the stalks
                cv.put(i, j, c2)
    return cv


PEPPER_BURN = {(40, 72, 40): CH0, (72, 112, 48): CH1, (112, 152, 56): CH2, (160, 192, 80): CH3,
               (248, 120, 88): EM2, (216, 48, 32): CH1, (144, 24, 32): CH0}


def burnt_pepper(cv):
    """The pepper rows burned: the bushes charred to black stalks on the tilled ridges, a few embers."""
    cv = cv.copy()
    for j in range(cv.h):
        for i in range(cv.w):
            c = cv.get(i, j)
            if c is None:
                continue
            c = gba(c)
            if c in PEPPER_BURN:
                c2 = PEPPER_BURN[c]
                if c2 == EM2 and hashn(i, j, 81) < 0.6:
                    c2 = CH2
                cv.put(i, j, c2)
    return cv


# ---------------------------------------------------------------- ash on dry ground
def ash_style(i, j, inside, d):
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near <= 2 and (i + j) % 2 == 0:
            return D3 if near == 1 else D2                     # scorched earth at the ash's edge
        return DRY(i, j)
    if near == 1:
        return CH3 if (i + j) % 2 else D3
    n = hashn(i, j, 51)
    k = (i * 3 + j * 7) % 11
    c = CH3 if k in (0, 5) else ASH1
    if n < 0.10:
        c = CH2
    elif n > 0.95:
        c = CH1
    if hashn(i, j, 53) < 0.004:
        c = EM2
    return c


def ash_tex(i, j):
    return ash_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None})


# ---------------------------------------------------------------- ursaluna props
def den():
    """4x3 the den: a great slab of rock leaning out from the arroyo wall (row 0, claw-scored), the dark hollow under
    it (row 1), a bedding of dry leaves, fur and broken branches spilling out onto the earth (row 2)."""
    cv = Canvas(4, 3)
    rock = dc_list("rock_wall")[0]
    for x0 in range(0, 64, 16):
        cv.paste(rock, x0, 0)
    # the overhang's lip and underside
    for i in range(64):
        y = 13 + int(2 * math.sin(i * 0.2)) + (1 if i % 9 == 0 else 0)
        cv.put(i, y, R6)
        cv.put(i, y + 1, R4)
        for j in range(y + 2, y + 5):
            cv.put(i, j, R3 if j < y + 4 else R2)
        cv.put(i, y + 5, R1)
        for j in range(y + 6, 34):
            cv.put(i, j, R1 if (i + j) % 7 else B0)          # the hollow's darkness
    # claw scores on the slab
    for x in (14, 19, 24, 44, 49):
        cv.line(x, 2, x - 3, 10, R1)
        cv.line(x + 1, 2, x - 2, 10, R6)
    # the dark mouth narrows at the sides: rock buttresses
    for (x0, x1) in ((0, 7), (57, 64)):
        for j in range(16, 36):
            for i in range(x0, x1):
                cv.put(i, j, R4 if (i + j) % 5 else R3)
        cv.vline(x1 - 1 if x0 == 0 else x0, 16, 35, R1)
    # the bedding: a mound of leaves, fur and sticks spilling out
    for j in range(26, 48):
        for i in range(64):
            v = ((i + 0.5 - 32) / 29) ** 2 + ((j + 0.5 - 34) / 11) ** 2
            if v <= 1.0:
                n = hashn(i // 2, j // 2, 61)
                c = LV2 if n < 0.3 else (LV1 if n < 0.55 else (FU2 if n < 0.8 else FU3))
                if hashn(i, j, 62) < 0.08:
                    c = FU1
                cv.put(i, j, c)
            elif j >= 32 and cv.get(i, j) is None:
                cv.put(i, j, DRY(i, j))
    for (a, b) in [((8, 40), (20, 36)), ((40, 44), (55, 39)), ((26, 46), (33, 43))]:
        cv.line(*a, *b, FU3)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, B0)
    for (x, y) in [(30, 31), (31, 31), (12, 33), (50, 34)]:
        cv.put(x, y, BONE)
    for j in range(36, 48):
        for i in range(64):
            if cv.get(i, j) is None:
                cv.put(i, j, DRY(i, j))
    return cv


def face_claw():
    """The rock wall's face extension (rock_wall_face), gouged by three long claw marks."""
    cv = dc("rock_wall_face").copy()
    for x in (4, 8, 12):
        cv.line(x, 1, x - 2, 12, R0)
        cv.line(x + 1, 1, x - 1, 12, R6)
    return over(cv, DRY)


def scarred_stump():
    cv = ground(DRY)
    cv.ellipse(8, 11, 6.5, 3.5, B0)
    cv.ellipse(8, 10, 5.5, 4.5, FU1)
    cv.ellipse(8, 7, 5.5, 2.6, B0)
    cv.ellipse(8, 7, 4.6, 2.0, FU3)
    cv.ellipse(8, 7, 2.2, 0.9, FU2)
    for x in (5, 8, 11):
        cv.line(x, 9, x - 1, 14, B0)
        cv.put(x + 1, 10, R6)
    for (a, b) in [((3, 12), (0, 14)), ((13, 12), (15, 15))]:
        cv.line(*a, *b, FU1)
    return cv


def bones():
    cv = ground(DRY)
    cv.line(3, 9, 11, 6, BONE)
    cv.line(3, 10, 11, 7, R4)
    for (x, y) in [(2, 8), (2, 10), (12, 5), (12, 7)]:
        cv.put(x, y, BONE)
    cv.line(6, 12, 13, 12, BONE)
    cv.put(14, 11, BONE)
    cv.put(14, 13, BONE)
    cv.hline(6, 13, 13, D3)
    return cv


def fur():
    cv = ground(DRY)
    for (x, y) in [(4, 6), (5, 7), (6, 6), (5, 5), (10, 10), (11, 11), (12, 10), (11, 9), (9, 12)]:
        cv.put(x, y, FU2)
        cv.put(x + 1, y + 1, FU1)
    return cv


def boulder(name):
    p = json.load(open(os.path.join(SRC, "dry_country.json")))["pieces"][name]
    return over(sheet_cell(os.path.join(SRC, "dry_country.png"), p["x"], p["y"], p["w"], p["h"]), DRY)


# ---------------------------------------------------------------- entei props
def brazier():
    """1x2 a squat stone brazier on the ash, burning: a bowl of fired stone on a short foot, flames licking up out
    of it, soot on its rim, sparks."""
    cv = Canvas(1, 2)
    cv.rect(4, 22, 8, 7, CH3)
    cv.vline(4, 22, 28, ASH1)
    cv.vline(11, 22, 28, CH2)
    cv.vline(3, 22, 29, CH0)
    cv.vline(12, 22, 29, CH0)
    cv.hline(3, 12, 29, CH0)
    cv.ellipse(8, 20, 7, 3.2, CH0)
    cv.ellipse(8, 19.5, 6, 2.6, ASH1)
    cv.ellipse(8, 19, 5, 1.8, CH1)
    flame = [(8, 4, EM4), (7, 6, EM4), (9, 7, EM3), (8, 8, EM4), (6, 9, EM3), (10, 9, EM3), (7, 10, EM4),
             (9, 11, EM4), (8, 12, EM4), (5, 12, EM2), (11, 12, EM2), (6, 13, EM3), (10, 13, EM3), (7, 14, EM4),
             (9, 14, EM4), (8, 15, EM4), (5, 15, EM2), (11, 15, EM2), (6, 16, EM3), (10, 16, EM3), (4, 17, EM2),
             (12, 17, EM2), (7, 17, EM4), (9, 17, EM4), (8, 17, EM3), (6, 18, EM2), (10, 18, EM2)]
    for (x, y, c) in flame:
        cv.put(x, y, c)
    for (x, y) in [(5, 7), (11, 5), (10, 2)]:
        cv.put(x, y, EM3)
    for (x, y) in [(6, 4), (9, 2)]:
        cv.put(x, y, CH3)                                   # smoke
    return over(cv, ash_tex)


def vent():
    cv = ground(ash_tex)
    pts = [(2, 9), (5, 7), (8, 8), (10, 6), (13, 7)]
    for k in range(len(pts) - 1):
        cv.line(*pts[k], *pts[k + 1], EM2)
    cv.line(8, 8, 9, 12, EM2)
    for (x, y) in pts[1:-1]:
        cv.put(x, y, EM4)
        cv.put(x, y - 1, EM1)
    cv.put(9, 11, EM3)
    return cv


def stubble():
    cv = ground(ash_tex)
    for (x, y, h) in [(3, 10, 4), (6, 12, 3), (9, 9, 5), (12, 11, 3), (5, 6, 3), (11, 5, 2)]:
        cv.vline(x, y - h, y, CH0)
        cv.put(x, y - h, CH3)
    return cv


# ---------------------------------------------------------------- build
def build():
    P = Pieces("ld")
    # the dry scrub wall
    for xy in ("00", "10", "01", "11"):
        P.add(f"block_{xy}", border(f"dry_scrub_{xy}"), comment="the dry scrub wall (border block cell)", lair="both")
    for f in ("S", "N", "E", "W"):
        for k in (0, 1):
            P.add(f"{f}{k}", border(f"dry_{f}_dry_{k}"), walk=True, comment="the scrub wall's edge cell on dry ground",
                  lair="both")
    for c in ("NW", "NE", "SW", "SE"):
        P.add(f"in_{c}", border(f"dry_in_{c}_dry"), walk=True, comment="the scrub wall's inner corner", lair="both")
    from PIL import Image
    for c in ("NW", "NE", "SW", "SE"):
        im = Image.open(os.path.join(MAPGEN, "tilesets", "borders", f"bk_dry_out_{c}_2cfd7b76.png")).convert("RGBA")
        cv = Canvas(1, 1)
        cv.im.paste(im, (0, 0))
        cv.p = cv.im.load()
        P.add(f"out_{c}", cv, walk=True, comment="the scrub wall's outer corner (baked border cell)", lair="both")
    # ursaluna
    keys = [k for k in CORNER_KEYS.values() if k != "C"]
    for k in keys:
        P.add(f"rock_{k}", dc(f"rock_wall_{k}"), comment=f"rock wall (dry-country set) {k}", lair="ursaluna")
    for i, cv in enumerate(dc_list("rock_wall")):
        P.add("rock_C" if i == 0 else f"rock_C{i}", cv, comment="rock wall top", lair="ursaluna")
    for k in ("face", "face_l", "face_r"):
        P.add(f"rock_{k}", dc(f"rock_wall_{k}"), comment=f"rock wall face extension ({k})", lair="ursaluna")
    P.add("rock_face_claw", face_claw(), comment="rock wall face gouged by claws", lair="ursaluna")
    for k in keys:
        P.add(f"clay_{k}", dc(f"red_earth_{k}"), walk=True, comment=f"red clay on dry ground {k}", lair="ursaluna")
    for i, cv in enumerate(dc_list("red_earth")):
        P.add("clay_C" if i == 0 else f"clay_C{i}", cv, walk=True, comment="red clay", lair="ursaluna")
    P.add("den", den(), walk=False, comment="4x3 the den: rock overhang, dark hollow, bedding (all blocking)",
          lair="ursaluna")
    P.add("scarred_stump", scarred_stump(), comment="1x1 a stump scored by claws, blocking", lair="ursaluna")
    P.add("bones", bones(), walk=True, comment="1x1 old bones (walkable)", lair="ursaluna")
    P.add("fur", fur(), walk=True, comment="1x1 tufts of shed fur (walkable)", lair="ursaluna")
    # entei
    P.add("pepper", dc("pepper"), comment="pepper rows (the dry country's field cell, copied), blocking", lair="entei")
    P.add("pepper_burnt", burnt_pepper(dc("pepper")), comment="pepper rows burned black, blocking", lair="entei")
    P.add_set("ash", dual_set(ash_style, ro=6, ri=5, wob=1), walk=True, comment="ash over dry ground", lair="entei")
    P.add("brazier", brazier(), comment="1x2 a burning stone brazier on the ash, blocking", lair="entei")
    P.add("vent", vent(), comment="1x1 glowing cracks in the ash (blocking: hot)", lair="entei")
    P.add("stubble", stubble(), walk=True, comment="1x1 burned cane stubs in the ash (walkable)", lair="entei")
    return P


def main():
    P = build()
    pc = P.items["pepper"]["cv"]
    FAMILIES["CROP"] = sorted({gba(pc.im.getpixel((i, j))[:3]) for j in range(16) for i in range(16)})
    pb = P.items["pepper_burnt"]["cv"]
    FAMILIES["BURNT"] = sorted({gba(pb.im.getpixel((i, j))[:3]) for j in range(16) for i in range(16)})
    print("CROP", len(FAMILIES["CROP"]), "BURNT", len(FAMILIES["BURNT"]))
    bad = P.write("lairs_dry.png", "orleans_lairs_dry", "gTileset_OrleansLairsDry", "orleans_general.mapping.json",
                  FAMILIES, "The dry lairs (Bloodmoon Ursaluna, Entei)")
    for b in bad[:30]:
        print("off-family:", b)
    print(f"lairs_dry: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

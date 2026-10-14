"""Own art for Landorus' lair (legendary lairs batch 2): the Field That Always Bears, off Route 23. Its own secondary,
gTileset_OrleansLairField on gTileset_OrleansGeneral (prefix lh).

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_field.py
writes tools/mapgen/tilesets/lairs/lair_field.png + lair_field.json and recipes_b2/orleans_lair_field.json (source "lh").

Why not the dry lairs' secondary (ld, Ursaluna and Entei): it already merges near-duplicate colours, and Landorus' field squeezed five
of its seven slots (46 cells off their art) when it was tried as a superset. So the field copies what it needs from ld's own sources:
the dry scrub wall and its edge cells (make_borders), the red earth set (make_dry_country, here the tilled clay), the cane and the
dry country's shade tree.

The lore: Landorus is the one who makes the land bear. Off the parched Route 23 road, where nothing grows, there is a hollow in the
scrub where the corn stands ripe, the pumpkins swell and the cane is thick, whatever the season; the people who farm the dry country
leave it the first fruits by the threshing floor.
    block_XY, S0 .. W1, in_*, out_*   the dry scrub wall and its edge cells (as ld's)
    clay_<key>, clay_C*   tilled red earth on dry ground (as ld's)
    corn_a / corn_b       ripe corn standing on the clay ridges (blocking); pumpkins (walkable); cane (blocking)
    thresh_<key>          the threshing floor: flat stones laid in a round on the dry ground (walkable)
    terrace_a / terrace_b a low dry-stone terrace wall running east-west (blocking)
    plough 2x1, scarecrow 1x2, basket 1x1 (the first fruits), jar 1x1, field_tree 2x3 (a pecan at the field's edge)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import Canvas, dual_set, ellipse_body, gba, hashn, ink_outline, over, write_b2  # noqa: E402
import make_lairs_dry as D1  # noqa: E402  (batch 1)

DRY = D1.DRY
DH, DD1, DD2, DD3, DL = D1.DH, D1.D1, D1.D2, D1.D3, D1.DL
ST, ST_D = D1.ST, D1.ST_D
K0, K1, K2 = D1.K0, D1.K1, D1.K2
B0, B1, B2 = D1.B0, D1.B1, D1.B2
L1, L2, L3, L4 = D1.L1, D1.L2, D1.L3, D1.L4
RE_L, RE, RE_D, RE_DD = D1.RE_L, D1.RE, D1.RE_D, D1.RE_DD
R1, R2, R3, R4, R5, R6 = D1.R1, D1.R2, D1.R3, D1.R4, D1.R5, D1.R6
EM2, EM3 = D1.EM2, D1.EM3

NEW_FAMILIES = {
    "FIELD": [RE_L, RE, RE_D, RE_DD, L1, L2, L3, L4, ST, ST_D, B0, EM2, EM3, DD3, DD2],
    "TOOLS": [DH, DD1, DD2, DD3, DL, B0, B1, B2, ST, ST_D, K0, K1, K2, R1, EM2],
}


def clay_tex(i, j):
    """Tilled red clay: furrows running east-west (ridges lit on top)."""
    k = j % 8
    if k in (0, 1):
        return RE_L if (i + j) % 5 else RE
    if k in (5, 6, 7):
        return RE_D if k != 7 else RE_DD
    return RE


def clay_cv(w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, clay_tex(i, j))
    return cv


def corn(v):
    """1x1 ripe corn standing in rows on the clay ridges: stalks, long leaves, ears with gold silk, tassels."""
    cv = clay_cv()
    for (x0, y0) in [(2 + v * 2, 15), (8 + v, 15), (13 - v, 15), (5, 7), (11, 7)]:
        h = 11 if y0 == 15 else 6
        for k in range(h):
            cv.put(x0, y0 - k, L2 if k < h - 2 else ST)
            if k % 3 == 1:
                cv.put(x0 - 1, y0 - k - 1, L3)
                cv.put(x0 - 2, y0 - k, L2)
                cv.put(x0 + 1, y0 - k - 1, L3)
                cv.put(x0 + 2, y0 - k, L1)
            if k == h // 2:
                cv.put(x0 + 1, y0 - k, ST)
                cv.put(x0 + 1, y0 - k + 1, ST_D)
        cv.put(x0, y0 - h, ST)
        cv.put(x0 - 1, y0 - h + 1, ST_D)
        cv.put(x0 + 1, y0 - h + 1, ST_D)
    return cv


def pumpkins():
    """1x1 pumpkins swelling on their vines in the furrows (walkable)."""
    cv = clay_cv()
    for k in range(16):
        y = 9 + round(1.5 * math.sin(k * 0.6))
        cv.put(k, y, L2)
        if k % 4 == 1:
            cv.put(k, y - 1, L3)
            cv.put(k + 1, y - 1, L4)
    for (x, y, r) in [(4, 11, 3.0), (11, 6, 2.6), (12, 13, 2.2)]:
        b = ellipse_body(x, y, r, r * 0.8)
        for (i, j) in b:
            c = EM3 if i < x else EM2
            if int(i - x + 10) % 2 == 0 and abs(i + 0.5 - x) > 0.6:
                c = EM2
            cv.put(i, j, c)
        cv.put(round(x), round(y - r * 0.8) - 1, L1)
        for (i, j) in b:
            if (i, j + 1) not in b:
                cv.put(i, j + 1, RE_DD)
    return cv


def thresh_style(i, j, inside, d):
    """The threshing floor: flat stones laid close in a round, swept clean, on the dry ground."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        return DD3 if near == 1 and (i + j) % 2 else DRY(i, j)
    if near == 1:
        return R2
    if near == 2:
        return R4 if (d["dn"] == 2 or d["dw"] == 2) else R3
    a, b = (i + 2 * (j // 5)) % 7, j % 5
    if a == 0 or b == 0:
        return R2 if (i + j) % 3 else R1
    c = R5 if hashn(i // 7, j // 5, 851) > 0.45 else R4
    if a == 1 and b == 1:
        c = R6
    return c


def terrace(v):
    """1x1 a low dry-stone terrace wall running east-west: rough stones, lit tops, a shadow on the ground below."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, DRY(i, j))
    for j in range(3, 13):
        for i in range(16):
            a, b = (i + 3 * ((j - 3) // 3) + v * 4) % 6, (j - 3) % 3
            c = R4 if b == 0 else (R3 if b == 1 else R2)
            if a == 0:
                c = R1
            cv.put(i, j, c)
    for i in range(16):
        cv.put(i, 2, R5 if i % 3 else R4)
        cv.put(i, 13, R1)
        cv.put(i, 14, DD3 if i % 2 else DD2)
    return cv


def dry_cv(w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, DRY(i, j))
    return cv


def plough():
    """2x1 an old wooden plough left at the field's edge: two handles, the beam, an iron share."""
    cv = dry_cv(2, 1)
    cv.line(2, 3, 14, 9, B1)
    cv.line(2, 4, 14, 10, B0)
    cv.line(4, 1, 13, 8, B2)
    cv.line(4, 2, 13, 9, B0)
    cv.line(12, 9, 28, 8, B1)
    cv.line(12, 10, 28, 9, B0)
    for (i, j) in [(15, 10), (16, 11), (17, 11), (18, 12), (16, 12), (17, 12)]:
        cv.put(i, j, K1)
    cv.hline(15, 18, 13, K0)
    cv.put(28, 7, B2)
    return cv


def scarecrow():
    """1x2 a scarecrow in a farmer's straw hat, its arms on a crossbar, straw poking out."""
    cv = dry_cv(1, 2)
    cv.vline(7, 6, 30, B1)
    cv.vline(8, 6, 30, B0)
    cv.hline(1, 14, 12, B1)
    cv.hline(1, 14, 13, B0)
    for (i, j) in ellipse_body(8, 6.5, 2.6, 2.4):
        cv.put(i, j, ST)
    cv.hline(3, 12, 4, ST_D)
    cv.hline(5, 10, 3, ST)
    cv.hline(6, 9, 2, ST)
    cv.rect(5, 11, 6, 9, K0)
    cv.hline(5, 10, 15, B2)
    for (x, y) in [(1, 14), (14, 14), (6, 20), (9, 21), (2, 13)]:
        cv.put(x, y, ST)
    cv.put(7, 6, B0)
    cv.put(9, 6, B0)
    return cv


def basket():
    """1x1 the first fruits by the threshing floor: a woven basket heaped with corn, a pumpkin and red peppers."""
    cv = dry_cv()
    for (i, j) in ellipse_body(8, 11, 6.5, 3.5):
        cv.put(i, j, ST if (i + j) % 2 else ST_D)
    for (x, y, c) in [(5, 7, ST), (6, 7, ST), (7, 7, ST_D), (9, 6, EM2), (10, 6, DL), (11, 7, EM2), (8, 8, EM2), (4, 8, DL)]:
        cv.put(x, y, c)
        cv.put(x, y + 1, c)
    cv.hline(2, 14, 14, B0)
    return cv


def jar():
    """1x1 a clay water jar in the shade, a gourd dipper on it."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, DRY(i, j))
    b = ellipse_body(8, 9, 5, 5.5)
    for (i, j) in b:
        cv.put(i, j, DL if i < 6 and j < 8 else (DD2 if i < 10 else DD3))
    cv.rect(6, 2, 5, 2, DD3)
    ink_outline(cv, b, B0, only_clear=False)
    cv.put(10, 1, ST_D)
    cv.put(11, 0, ST_D)
    return cv


def build():
    from lair_kit_b2 import CORNER_KEYS, MAPGEN, Pieces
    from PIL import Image
    P = Pieces("lh")
    for xy in ("00", "10", "01", "11"):
        P.add(f"block_{xy}", D1.border(f"dry_scrub_{xy}"), comment="the dry scrub wall (border block cell)", lair="landorus")
    for f in ("S", "N", "E", "W"):
        for k in (0, 1):
            P.add(f"{f}{k}", D1.border(f"dry_{f}_dry_{k}"), walk=True, comment="the scrub wall's edge cell on dry ground", lair="landorus")
    for c in ("NW", "NE", "SW", "SE"):
        P.add(f"in_{c}", D1.border(f"dry_in_{c}_dry"), walk=True, comment="the scrub wall's inner corner", lair="landorus")
    for c in ("NW", "NE", "SW", "SE"):
        im = Image.open(os.path.join(MAPGEN, "tilesets", "borders", f"bk_dry_out_{c}_2cfd7b76.png")).convert("RGBA")
        cv = Canvas(1, 1)
        cv.im.paste(im, (0, 0))
        cv.p = cv.im.load()
        P.add(f"out_{c}", cv, walk=True, comment="the scrub wall's outer corner (baked border cell)", lair="landorus")
    for k in [k for k in CORNER_KEYS.values() if k != "C"]:
        P.add(f"clay_{k}", D1.dc(f"red_earth_{k}"), walk=True, comment=f"tilled red clay on dry ground {k}", lair="landorus")
    for i, cv in enumerate(D1.dc_list("red_earth")):
        P.add("clay_C" if i == 0 else f"clay_C{i}", cv, walk=True, comment="tilled red clay", lair="landorus")
    P.add("corn_a", corn(0), comment="1x1 ripe corn on the clay ridges, blocking", lair="landorus")
    P.add("corn_b", corn(1), comment="1x1 ripe corn (variant), blocking", lair="landorus")
    P.add("pumpkins", pumpkins(), walk=True, comment="1x1 pumpkins on their vines (walkable)", lair="landorus")
    P.add("cane", D1.dc("cane"), comment="1x1 the dry country's sugar cane (copied), blocking", lair="landorus")
    P.add_set("thresh", dual_set(thresh_style, ro=7, ri=5, wob=0), walk=True, comment="the stone threshing floor", lair="landorus")
    P.add("terrace_a", terrace(0), comment="1x1 a dry-stone terrace wall, blocking", lair="landorus")
    P.add("terrace_b", terrace(1), comment="1x1 a dry-stone terrace wall (variant), blocking", lair="landorus")
    P.add("plough", plough(), comment="2x1 an old wooden plough in the furrow, blocking", lair="landorus")
    P.add("scarecrow", scarecrow(), comment="1x2 a scarecrow in a straw hat, blocking", lair="landorus")
    P.add("basket", basket(), comment="1x1 the first fruits on the threshing floor, blocking", lair="landorus")
    P.add("jar", jar(), comment="1x1 a clay water jar, blocking", lair="landorus")
    import json
    p = json.load(open(os.path.join(D1.SRC, "dry_country.json")))["pieces"]["field_tree"]
    from lair_kit_b2 import sheet_cell
    P.add("field_tree", over(sheet_cell(os.path.join(D1.SRC, "dry_country.png"), p["x"], p["y"], p["w"], p["h"]), DRY),
          comment="the dry country's shade tree (copied), blocking", lair="landorus")
    # three near-duplicate pairs (<= 12 apart) in the copied cane and scrub art would be merged by compose's palette v2 (cells off by 11):
    # snap them here instead, so every cell draws exactly
    snap = {(72, 112, 48): (64, 112, 56), (40, 72, 40): (40, 80, 48), (240, 224, 184): (248, 232, 184)}
    for n in P.order:
        P.items[n]["cv"].recolor(snap)
    return P


def families(P):
    snap = {(72, 112, 48): (64, 112, 56), (40, 72, 40): (40, 80, 48), (240, 224, 184): (248, 232, 184)}
    fam = {k: sorted({snap.get(gba(c), gba(c)) for c in D1.FAMILIES[k]}) for k in ("SCRUB", "ROCK", "CLAY")}
    cc = P.items["cane"]["cv"]
    fam["CANE"] = sorted({gba(cc.im.getpixel((i, j))[:3]) for j in range(16) for i in range(16)})
    ft = P.items["field_tree"]["cv"]
    fam["TREE"] = sorted({gba(ft.im.getpixel((i, j))[:3]) for j in range(ft.h) for i in range(ft.w)})
    fam.update({k: sorted({snap.get(gba(c), gba(c)) for c in v}) for k, v in NEW_FAMILIES.items()})
    return {k: v for k, v in fam.items() if len(v) <= 15}


def main():
    P = build()
    fam = families(P)
    bad = write_b2(P, "lair_field.png", "orleans_lair_field", "gTileset_OrleansLairField", "orleans_general.mapping.json",
                   fam, "The Field That Always Bears (Landorus)", "make_lair_field.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_field: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

"""Own art for the Rootkin shrine lairs: Celebi's shrine glade off Route 7 now; Uxie, Mesprit and Azelf (and the
Route 13 meadow shrine) are meant to share this secondary later. gTileset_OrleansLairRootkin on
gTileset_OrleansGeneral.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_rootkin.py
writes tools/mapgen/tilesets/lairs/lair_rootkin.png + lair_rootkin.json and recipes/orleans_lair_rootkin.json
(source "lk").

A Rootkin shrine: the people of the Old Water carve spirals in stone and cedar, thatch with palmetto and paint
their bands teal and orange (make_rootkin_art.py's huts and song house).
    moss_<key>        a sunken circle of deep moss (the shrine's floor)
    sun_stone 2x2     a Rootkin sun stone: a round dial of cut stone on a fluted pedestal, a spiral at its heart,
                      the gnomon's blade and shadow (Celebi's time shrine)
    spirit_house 2x2  a little spirit house: a palmetto-thatch roof on four carved posts over a stone offering
                      slab, a painted band, shells and a bowl of berries left on a woven mat
    cedar_post, cedar_post_bird   carved cedar posts (the Oldest Shrine's, copied: one art family for shrines)
    stone_tall        the spiral-carved standing stone (the Oldest Shrine's, copied)
    lily_white / lily_pink / mushrooms   the ring of spider lilies, a fairy ring
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import MAPGEN, Canvas, Pieces, dual_set, gba, hashn, over, pcell, sheet_cell, tex_from  # noqa: E402
import make_lairs_wet as W  # noqa: E402

GRASS = W.GRASS
G, GD, GL, SH = W.G, W.GD, W.GL, W.SH
TH_L, TH, TH_D, TH_DD = (216, 192, 120), (184, 152, 88), (144, 120, 64), (104, 80, 48)
WD1, WD2, WD3 = (72, 56, 40), (112, 88, 56), (152, 120, 80)
TEAL, ORNG = (64, 152, 152), (224, 120, 48)
ST1, ST2, ST3, ST4, INK = W.ST1, W.ST2, W.ST3, W.ST4, W.INK
BERRY = (160, 48, 96)


def spirit_house():
    """2x2 a Rootkin spirit house: a little palmetto-thatch roof on four carved posts over a stone offering slab,
    a teal-and-orange painted band under the eave, a woven mat, shells and a bowl of berries on it."""
    cv = Canvas(2, 2)
    # the offering slab (stone) with its mat
    cv.rect(4, 20, 24, 8, ST3)
    cv.hline(4, 27, 20, ST4)
    cv.hline(4, 27, 27, ST2)
    cv.vline(3, 20, 28, INK)
    cv.vline(28, 20, 28, INK)
    cv.hline(3, 28, 28, INK)
    for i in range(8, 24):
        for j in range(21, 26):
            cv.put(i, j, TH if (i + j) % 2 else TH_D)
    for (x, y) in [(10, 22), (11, 22), (20, 23)]:
        cv.put(x, y, ST4)                                  # shells
    cv.ellipse(15.5, 23.5, 2.5, 1.5, WD2)
    for (x, y) in [(15, 23), (16, 22), (14, 23)]:
        cv.put(x, y, BERRY)
    # posts
    for x in (5, 25):
        cv.vline(x, 10, 26, WD2)
        cv.vline(x + 1, 10, 26, WD1)
        cv.put(x, 15, ORNG)
        cv.put(x, 17, ORNG)
    # roof: palmetto thatch, a low hip, the painted band under the eave
    for j in range(0, 12):
        xl, xr = 9 - j * 0.8, 22 + j * 0.8
        for i in range(int(xl), int(xr) + 1):
            c = TH if (j % 3) else TH_D
            if j % 3 == 0 and (i + j) % 4 == 0:
                c = TH_L
            cv.put(i, j + 1, c)
        cv.put(int(xl) - 1, j + 1, TH_DD)
        cv.put(int(xr) + 1, j + 1, TH_DD)
    cv.hline(9, 22, 0, TH_DD)
    cv.hline(13, 18, 0, TH_DD)
    for i in range(1, 31):
        if i % 3:
            cv.put(i, 13, TH_DD)                           # ragged fringe
    for i in range(3, 29):
        cv.put(i, 14, TEAL if (i // 2) % 2 else ORNG)      # the painted band
    cv.hline(3, 28, 15, WD1)
    for i in range(2, 30):
        if cv.get(i, 29) is None:
            cv.put(i, 29, SH)
    return over(cv, GRASS)


def sun_stone():
    return W.sundial()


def build():
    P = Pieces("lk")
    P.add_set("moss", dual_set(W.moss_style, ro=6, ri=5, wob=1), walk=True, comment="the sunken moss circle",
              lair="celebi")
    P.add("sun_stone", sun_stone(), comment="2x2 the Rootkin sun stone on the moss, blocking", lair="celebi")
    P.add("spirit_house", spirit_house(), comment="2x2 a Rootkin spirit house with offerings, blocking", lair="celebi")
    shrine = json.load(open(os.path.join(MAPGEN, "tilesets", "arenas", "shrine.json")))["pieces"]
    spng = os.path.join(MAPGEN, "tilesets", "arenas", "shrine.png")
    for n in ("cedar_post", "cedar_post_bird", "stone_tall"):
        p = shrine[n]
        P.add(n, over(sheet_cell(spng, p["x"], p["y"], 1, 2), GRASS), comment=f"1x2 {n} (the Oldest Shrine's art), blocking",
              lair="celebi")
    P.add("lily_white", W.lily("white"), walk=True, comment="1x1 white spider lilies (walkable)", lair="celebi")
    P.add("lily_pink", W.lily("pink"), walk=True, comment="1x1 pink spider lilies (walkable)", lair="celebi")
    P.add("mushrooms", W.mushrooms(), walk=True, comment="1x1 a fairy ring of mushrooms (walkable)", lair="celebi")
    return P


FAMILIES = {
    "FLORA": [G, GD, GL, SH, W.MOSS1, W.MOSS2, W.MOSS3, W.FW1, W.FW2, W.FY, W.FP, W.FPD, W.STEM],
    "STONE": [G, GD, GL, ST1, ST2, ST3, ST4, W.MO, INK, W.MOSS1, W.MOSS2, W.MOSS3, SH],
    "CEDAR": [G, GD, GL, (96, 56, 40), (136, 80, 56), (176, 112, 72), (216, 168, 72), ST4, ST3, ST2, INK],
    "THATCH": [G, GD, GL, SH, TH_L, TH, TH_D, TH_DD, WD1, WD2, TEAL, ORNG, BERRY, ST3, ST4],
    "SLAB": [G, GD, GL, SH, ST2, ST3, ST4, INK, WD1, WD2, TH, TH_D, BERRY, ORNG],
}


def main():
    P = build()
    bad = P.write("lair_rootkin.png", "orleans_lair_rootkin", "gTileset_OrleansLairRootkin",
                  "orleans_general.mapping.json", FAMILIES, "The Rootkin shrine lairs (Celebi)")
    for b in bad[:20]:
        print("off-family:", b)
    print(f"lair_rootkin: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

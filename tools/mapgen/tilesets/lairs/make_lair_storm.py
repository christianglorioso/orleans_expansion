"""Own art for Raikou's lair (Route 2): a lightning-struck clearing in the swamp woods. Its own small secondary,
gTileset_OrleansLairStorm on gTileset_OrleansGeneral (the green lairs' secondary has no palette room left).

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_storm.py
writes tools/mapgen/tilesets/lairs/lair_storm.png + lair_storm.json and recipes/orleans_lair_storm.json (source "ls").

    scorch_<key>    burned ground on the grass: char and ash, the grass singed brown round its edge (the strike
                    ring); scorch_core: the centre fused to glassy black with lightning-fern scars
    glass 1x1       a fulgurite: tubes of fused sand standing out of the char, glinting
    snag 3x3        a lightning-struck cypress (the route landmark's scorched cypress, copied)
    tower 2x4       a power tower (route landmark art, copied) and tower_down 4x2, one knocked over by the strike
    transformer 2x2 a pole transformer torn down, its casing split, sparks; wire 2x1 (the fallen line, copied)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import SRC, Canvas, Pieces, dual_set, gba, hashn, over, pcell, sheet_cell, tex_from  # noqa: E402

GRASS = tex_from(pcell("ekat:grass"))
G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
BR1, BR2 = (136, 120, 72), (104, 88, 56)               # singed grass
CH0, CH1, CH2, CH3 = (32, 28, 32), (56, 48, 48), (88, 80, 72), (128, 120, 112)
ASH = (168, 160, 152)
GLS1, GLS2, GLS3 = (64, 96, 112), (120, 168, 184), (208, 240, 248)
S0, S1, S2, S3 = (64, 72, 88), (96, 112, 128), (136, 152, 168), (184, 200, 208)
SP1, SP2, SP3 = (88, 136, 232), (160, 216, 248), (248, 248, 248)
INK = (40, 40, 48)


def lmk(name):
    p = json.load(open(os.path.join(SRC, "route_landmarks.json")))["pieces"][name]
    return sheet_cell(os.path.join(SRC, "route_landmarks.png"), p["x"], p["y"], p["w"], p["h"])


def colours(cv):
    return {gba(cv.im.getpixel((i, j))[:3]) for j in range(cv.h) for i in range(cv.w) if cv.im.getpixel((i, j))[3]}


def scorch_style(i, j, inside, d):
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if near == 1:
            return BR2 if (i + j) % 2 else BR1
        if near <= 3 and hashn(i, j, 71) < 0.5:
            return BR1 if near == 2 else SH
        return GRASS(i, j)
    if near == 1:
        return CH2 if (i + j) % 2 else BR2
    n = hashn(i // 2, j // 2, 72)
    c = CH1 if n < 0.45 else (CH2 if n < 0.85 else CH3)
    if hashn(i, j, 73) < 0.05:
        c = ASH
    return c


def core():
    """The heart of the strike: char fused glassy black, branching lightning-fern scars burned into it."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, scorch_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None}))
    # Lichtenberg fern: branches from the cell's middle out to its edges (joining the next core cell)
    for (a, b) in [((8, 8), (0, 3)), ((8, 8), (15, 5)), ((8, 8), (3, 15)), ((8, 8), (13, 15)), ((4, 5), (2, 9)),
                   ((12, 6), (11, 2)), ((6, 12), (9, 13))]:
        cv.line(*a, *b, CH0)
    for (x, y) in [(8, 8), (7, 8), (8, 7)]:
        cv.put(x, y, GLS1)
    return cv


def glass():
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, scorch_style(i, j, True, {"dn": None, "ds": None, "dw": None, "de": None}))
    for (x, y, h) in [(5, 10, 5), (8, 11, 7), (11, 10, 4), (7, 7, 3)]:
        cv.vline(x, y - h, y, GLS1)
        cv.vline(x + 1, y - h, y, GLS2)
        cv.put(x + 1, y - h, GLS3)
        cv.put(x, y + 1, CH0)
    cv.put(3, 4, GLS3)
    cv.put(13, 6, GLS3)
    return cv


def transformer():
    """2x2 a pole transformer torn down by the strike: the grey can lying on its side, its lid sprung, porcelain
    bushings snapped, a snaking cable, blue sparks."""
    cv = Canvas(2, 2)
    # the can
    for j in range(8, 24):
        for i in range(6, 24):
            v = (j - 16) / 8.0
            c = S3 if v < -0.55 else (S2 if v < 0.1 else (S1 if v < 0.6 else S0))
            cv.put(i, j, c)
    cv.ellipse(24, 16, 3, 8, S1)
    cv.ellipse(24, 16, 2, 6.5, S0)
    cv.ellipse(6, 16, 3, 8, S2)
    cv.ellipse(6, 16, 2, 6.5, S3)
    for x in (11, 17):
        cv.vline(x, 8, 23, S1)
    for (x, y) in [(5, 7), (6, 6), (7, 7), (3, 12), (2, 13)]:
        cv.put(x, y, S0)
    cv.line(26, 10, 30, 6, S1)                     # sprung lid
    cv.line(27, 11, 31, 7, S3)
    # snapped bushings
    for x in (10, 15, 20):
        cv.rect(x, 4, 2, 4, S3)
        cv.put(x, 3, SP3)
    # cable
    pts = [(24, 22), (27, 25), (24, 28), (18, 29), (12, 27), (6, 29), (2, 27)]
    for k in range(len(pts) - 1):
        cv.line(*pts[k], *pts[k + 1], INK)
    # sparks
    for (x, y, c) in [(31, 5, SP3), (30, 3, SP2), (29, 7, SP1), (2, 26, SP3), (1, 24, SP2), (3, 28, SP1), (11, 2, SP2),
                      (16, 1, SP1)]:
        cv.put(x, y, c)
    body = {(i, j) for j in range(32) for i in range(32) if cv.get(i, j) in (S0, S1, S2, S3)}
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in body and cv.get(x + dx, y + dy) is None:
                cv.put(x + dx, y + dy, INK)
    for i in range(6, 26):
        if cv.get(i, 25) is None:
            cv.put(i, 25, SH)
    return over(cv, GRASS)


def tower_down():
    """4x2 a power tower knocked flat by the strike: the lattice lying west-east, its cross-arms bent, insulators
    scattered (the route's tower art turned on its side and crumpled)."""
    t = lmk("power_tower")
    cv = Canvas(4, 2)
    # rotate the 2x4 tower 90 degrees clockwise onto a 4x2 canvas, then crumple its tip
    for j in range(t.h):
        for i in range(t.w):
            c = t.get(i, j)
            if c is not None:
                cv.put(t.h - 1 - j, i, c)
    for (x, y) in [(2, 10), (3, 11), (1, 20), (4, 21)]:
        cv.put(x, y, None)
    return over(cv, GRASS)


def build():
    P = Pieces("ls")
    P.add_set("scorch", dual_set(scorch_style, ro=7, ri=5, wob=1), walk=True, comment="burned ground on grass",
              lair="raikou")
    P.add("scorch_core", core(), walk=True, comment="the strike's heart, fused char with lightning-fern scars",
          lair="raikou")
    P.add("glass", glass(), comment="1x1 fulgurites standing out of the char, blocking", lair="raikou")
    P.add("snag", over(lmk("scorched_cypress"), GRASS), comment="3x3 the lightning-struck cypress (landmark art)",
          lair="raikou")
    P.add("tower", over(lmk("power_tower"), GRASS), comment="2x4 a power tower (landmark art), blocking", lair="raikou")
    P.add("tower_down", tower_down(), comment="4x2 a power tower knocked flat, blocking", lair="raikou")
    P.add("transformer", transformer(), comment="2x2 a torn-down pole transformer, sparking, blocking", lair="raikou")
    P.add("wire", over(lmk("fallen_line"), GRASS), walk=True, comment="2x1 a fallen live line (landmark art)",
          lair="raikou")
    for n in ("wire_span", "wire_span_l", "wire_span_r"):
        P.add(n, over(lmk(n), GRASS), walk=True, comment=f"1x1 {n}: the line strung between the towers (landmark art)",
              lair="raikou")
    return P


def families(P):
    """The families are taken from the art itself: the scorch set, the copied landmark pieces, the metal."""
    fam = {"SCORCH": [G, GD, GL, SH, BR1, BR2, CH0, CH1, CH2, CH3, ASH, GLS1, GLS2, GLS3],
           "METAL": [G, GD, GL, SH, S0, S1, S2, S3, SP1, SP2, SP3, INK]}
    for n in ("snag", "tower", "wire", "wire_span"):
        cols = sorted(colours(P.items[n]["cv"]))
        fam[n.upper()] = cols
    return fam


def main():
    P = build()
    fam = families(P)
    for k, v in fam.items():
        print(k, len(v))
    bad = P.write("lair_storm.png", "orleans_lair_storm", "gTileset_OrleansLairStorm", "orleans_general.mapping.json",
                  {k: v for k, v in fam.items() if len(v) <= 15}, "Raikou's lightning-struck clearing")
    for b in bad[:20]:
        print("off-family:", b)
    print(f"lair_storm: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

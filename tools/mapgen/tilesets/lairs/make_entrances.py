"""The lairs' entrance art on their routes: OVERLAYS (magenta = clear) drawn over whatever the route has there (canopy,
edge cells, marsh, scrub, dry ground), so build.py's overlay mechanism composes them into the route's own tileset at
the right border parity. Every piece uses the colours of the art it sits on, so the composites stay in one palette.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_entrances.py
writes tools/mapgen/tilesets/lairs/entrances.png + entrances.json (pieces, the overlay source "lent" for the route
recipes, prefabs).

    canopy_gap_w 2x2   a trail into the swamp canopy (the wall to the east, the way in heads east): a dark hollow under
                       the trees, leaves hanging over its mouth, trampled grass leading in (Route 14, the rougarou)
    stone_arch 2x2     a Rootkin stone arch: two spiral-carved posts and a lintel, moss and vines; open (a dark way
                       through: set in a canopy wall, Route 7, Celebi), _mist (a pale mist fills it: free-standing on
                       the lake island, Route 11, Suicune), _vines (sealed: a curtain of vines, both routes during the story)
    scrub_gap 2x2      a cleft into the dry scrub (the wall to the north): a dark gap between the thickets, the earth
                       trodden into it (Routes 23 and 16)
    claw_stump 1x1     a stump raked by claws beside the Route 23 cleft (Ursaluna)
    charred_stake 1x2  a charred field stake, its tip still glowing, beside the Route 16 cleft (Entei)
Route 2 (Raikou) needs no new art: its north canopy wall already has a notch (feather pass) at x 24-25, rows 0-1; the
sealed state fills it with the canopy block (primary pieces), the open state is the map as built.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import Canvas, Pieces, dump, hashn  # noqa: E402

# the swamp canopy's own colours (make_borders CORE_PAL) and the Rootkin stone
S_OUT, C_DK, C_MID, C_HL, C_TIP = (40, 56, 40), (64, 96, 64), (80, 112, 96), (104, 152, 120), (144, 184, 152)
O_DK, O_MID = (72, 96, 64), (96, 128, 88)
GD, SH = (104, 144, 96), (96, 128, 88)
ST1, ST2, ST3, ST4, INK, MO = (88, 88, 80), (128, 128, 112), (168, 168, 144), (208, 208, 184), (40, 40, 48), (80, 112, 64)
FOG1, FOG2 = (176, 192, 184), (216, 224, 216)
# the dry scrub's colours (make_borders DRY_PAL)
D1, D2, D3 = (224, 200, 144), (200, 168, 112), (160, 128, 88)
L0, L1, L2 = (24, 48, 32), (40, 80, 48), (64, 112, 56)
K0, K1, K2 = (104, 96, 80), (152, 144, 120), (200, 192, 168)
B0, B1, B2 = (64, 40, 32), (104, 72, 48), (144, 104, 64)
ST, ST_D = (216, 184, 88), (176, 144, 64)


def canopy_gap_w():
    cv = Canvas(2, 2)
    # the hollow: a dark recess going east under the canopy (right column), rounded mouth
    for j in range(32):
        for i in range(12, 32):
            v = ((i - 12) / 22.0) ** 1.5 + ((j + 0.5 - 16) / 11.0) ** 2
            if v <= 1.0 - 0.08 * math.sin(j * 1.3):
                cv.put(i, j, S_OUT if v > 0.25 or (i + j) % 2 else C_DK)
    # leaves hanging over the mouth: ragged fringe on the hollow's top and bottom
    for i in range(12, 32):
        for (base, sgn) in ((5, 1), (27, -1)):
            n = int(3 * hashn(i, base, 7))
            for k in range(n + 1):
                y = base + sgn * k
                if 0 <= y < 32:
                    cv.put(i, y, C_MID if k < n else C_HL)
    # the trail: trampled grass and mud leading in from the west (left column over the edge cells)
    for j in range(9, 24):
        for i in range(0, 16):
            if ((i * 2 + j * 3) % 9) in (0, 1) or ((i + j) % 5 == 0 and j in range(12, 21)):
                cv.put(i, j, SH)
            elif (i + 2 * j) % 11 == 0:
                cv.put(i, j, GD)
    return cv


def stone_arch(fill):
    """2x2 a Rootkin stone arch. fill: 'open' (a dark way through), 'mist' (pale mist), 'vines' (a vine curtain)."""
    cv = Canvas(2, 2)
    # the passage between the posts
    for j in range(8, 31):
        for i in range(7, 25):
            if fill == "open":
                cv.put(i, j, S_OUT if (i + j) % 5 else C_DK)
            elif fill == "mist":
                v = abs(i - 15.5) / 9 + abs(j - 20) / 14
                if v < 0.6 or (v < 0.95 and (i + j) % 2 == 0):
                    cv.put(i, j, FOG2 if v < 0.35 else FOG1)
            elif fill == "vines":
                if i % 3 != 2 or j < 12 + (i * 7) % 9:
                    cv.put(i, j, C_DK if (i + j) % 4 else C_MID)
                if (i * 5 + j * 3) % 17 == 0:
                    cv.put(i, j, C_HL)
    # posts
    for x0 in (1, 25):
        for j in range(6, 31):
            for i in range(x0, x0 + 6):
                c = ST3
                if i == x0:
                    c = ST4
                elif i == x0 + 5:
                    c = ST2
                cv.put(i, j, c)
            cv.put(x0 - 1, j, INK)
            cv.put(x0 + 6, j, INK)
        for (dx, dy) in [(2, 14), (3, 14), (3, 15), (2, 16), (1, 15)]:
            cv.put(x0 + dx, dy + 4, ST1)
        cv.hline(x0 - 1, x0 + 6, 31, INK)
        cv.put(x0 + 1, 27, MO)
        cv.put(x0 + 4, 24, MO)
    # lintel
    cv.rect(0, 2, 32, 6, ST3)
    cv.hline(0, 31, 2, ST4)
    cv.hline(0, 31, 7, ST1)
    cv.hline(0, 31, 1, INK)
    cv.hline(0, 31, 8, INK)
    cv.vline(0, 1, 8, INK)
    cv.vline(31, 1, 8, INK)
    for cx in (8, 16, 24):
        for (dx, dy) in [(0, 0), (1, 0), (1, 1), (0, 2), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (2, -1)]:
            cv.put(cx + dx, 5 + dy, ST1)
    # moss and vines draped over the lintel
    for i in range(0, 32):
        if hashn(i, 0, 4) < 0.45:
            cv.put(i, 1, MO)
    for (x, n) in [(3, 6), (12, 4), (21, 7), (29, 5)]:
        for k in range(n):
            cv.put(x, 8 + k, C_DK if k % 2 else C_MID)
    return cv


def scrub_gap():
    """2x2 a cleft into the dry scrub (the wall to the north): a dark gap between the thickets, rocks at its lips,
    the earth trodden into it."""
    cv = Canvas(2, 2)
    for j in range(0, 20):
        w = 9 - j * 0.15
        for i in range(32):
            if abs(i + 0.5 - 16) < w + 1.5 * math.sin(j * 0.9):
                cv.put(i, j, L0 if (i + j) % 3 else B0)
    for (x, y) in [(6, 14), (25, 13), (8, 17), (23, 18)]:
        cv.ellipse(x, y, 2.5, 1.8, K0)
        cv.ellipse(x - 0.5, y - 0.5, 1.8, 1.2, K1)
        cv.put(int(x - 1), int(y - 1), K2)
    for j in range(16, 32):
        for i in range(8, 24):
            if (i * 3 + j) % 7 in (0, 1):
                cv.put(i, j, D3)
            elif (i + j) % 5 == 0:
                cv.put(i, j, D2)
    return cv


def claw_stump():
    cv = Canvas(1, 1)
    cv.ellipse(8, 11, 6.5, 3.5, B0)
    cv.ellipse(8, 10, 5.5, 4.5, B1)
    cv.ellipse(8, 7, 5.5, 2.6, B0)
    cv.ellipse(8, 7, 4.6, 2.0, B2)
    cv.ellipse(8, 7, 2.2, 0.9, B1)
    for x in (5, 8, 11):
        cv.line(x, 9, x - 1, 14, B0)
        cv.put(x + 1, 10, K2)
    return cv


def charred_stake():
    cv = Canvas(1, 2)
    for j in range(6, 29):
        cv.put(7, j, B1 if j % 4 else B0)
        cv.put(8, j, B0)
        cv.put(6, j, L0)
        cv.put(9, j, L0)
    cv.put(7, 5, ST)
    cv.put(8, 5, ST_D)
    cv.put(7, 4, ST)
    cv.hline(5, 10, 29, D3)
    cv.put(9, 3, ST)
    return cv


def build():
    P = Pieces("lent")
    P.add("canopy_gap_w", canopy_gap_w(), walk=[[1, 0], [1, 1]], comment="2x2 overlay: a trail into the canopy, "
          "the wall to the east (Route 14)", lair="rougarou")
    for f in ("open", "mist", "vines"):
        P.add(f"stone_arch_{f}" if f != "open" else "stone_arch", stone_arch(f),
              walk=([[0, 1], [1, 1]] if f != "vines" else []),
              comment=f"2x2 overlay: a Rootkin stone arch ({f})", lair="celebi suicune")
    P.add("scrub_gap", scrub_gap(), walk=[[0, 0], [1, 0], [0, 1], [1, 1]],
          comment="2x2 overlay: a cleft into the dry scrub, the wall to the north (Routes 23, 16)", lair="ursaluna entei")
    P.add("claw_stump", claw_stump(), comment="1x1 overlay: a clawed stump (Route 23)", lair="ursaluna")
    P.add("charred_stake", charred_stake(), comment="1x2 overlay: a charred stake, glowing tip (Route 16)", lair="entei")
    return P


def main():
    P = build()
    P.pack()
    P.image.save(os.path.join(HERE, "entrances.png"))
    pieces, mts, prefabs = {}, [], {}
    for n in P.order:
        cv = P.items[n]["cv"]
        px, py = P.pos[n]
        rows = []
        for j in range(cv.ch):
            row = []
            for i in range(cv.cw):
                mid = f"{px + i}_{py + j}"
                mts.append({"id": mid, "bottom": [px + i, py + j]})
                row.append({"overlay": f"lent:{mid}"})
            rows.append(row)
        walk = P.items[n]["walk"] or []
        pieces[n] = {"x": px, "y": py, "w": cv.cw, "h": cv.ch, "walk": walk, "lair": P.items[n]["lair"],
                     "comment": P.items[n]["comment"]}
        prefabs[n] = {"_comment": P.items[n]["comment"], "rows": rows, "door": None, "passable": walk}
    dump(os.path.join(HERE, "entrances.json"), {
        "_comment": "The lairs' route entrances (make_entrances.py): overlay pieces (magenta = clear), the compose "
                    "source 'lent' (overlay_only) to add to each route recipe that places them, and prefabs.",
        "png": "entrances.png", "pieces": pieces,
        "source": {"name": "lent", "type": "image", "image": "tools/mapgen/tilesets/lairs/entrances.png",
                   "transparent": [[255, 0, 255]], "overlay_only": True, "metatiles": mts},
        "prefabs": prefabs,
        "placements": {
            "Route14": {"tileset": "orleans_route_b", "open": [["canopy_gap_w", 25, 30]], "sealed": "the canopy as built",
                        "trigger": [[26, 30], [26, 31]], "opens": "story ch7 (the flood clears); the lair is night-only inside"},
            "Route23": {"tileset": "orleans_route_dry", "open": [["scrub_gap", 22, 1], ["claw_stump", 21, 3]],
                        "sealed": "the feather notch at x 22-23 filled with the dry scrub block", "trigger": [[22, 1], [23, 1]],
                        "opens": "story 45 (post-game); Ursaluna inside at night"},
            "Route7": {"tileset": "orleans_route", "open": [["stone_arch", 34, 1]], "sealed": [["stone_arch_vines", 34, 1]],
                       "trigger": [[34, 2], [35, 2]], "opens": "story 45"},
            "Route11": {"tileset": "orleans_route", "open": [["stone_arch_mist", 28, 20]],
                        "sealed": [["stone_arch_vines", 28, 20]], "trigger": [[28, 21], [29, 21]],
                        "opens": "story 45; the island's cypress goes, the arch stands in its place"},
            "Route2": {"tileset": "orleans_port", "open": "the map as built (the feather notch at x 24-25, rows 0-1)",
                       "sealed": "the notch filled with the swamp canopy block (primary pieces)", "trigger": [[24, 0], [25, 0]],
                       "opens": "story 45"},
            "Route16": {"tileset": "orleans_route_farm", "open": [["scrub_gap", 15, 1], ["charred_stake", 17, 2]],
                        "sealed": "the feather notch at x 14-17 filled with the dry scrub block", "trigger": [[15, 1], [16, 1]],
                        "opens": "story 45"},
        }})
    print(f"entrances: {len(P.order)} pieces, sheet {P.image.size}")
    return P


if __name__ == "__main__":
    main()

"""Own art for the dry routes (tileset orleans_route_dry): the sugar mills of Route 17 ("the sugar mill road") and the
pepper drying sheds of Route 16 ("the pepper fields"). Drawn with make_redfield_art.py's own parts and colours (the
MILL family), on the same 8 px phase, so they are the Redfield sugar mill's cells wherever they show the same thing.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_route_mills_art.py
writes
    sources/orleans_custom/route_mills.png          the piece sheet (16 px cells, magenta = clear)
    sources/orleans_custom/route_mills.json         {"pieces": {name: {x, y, w, h, doors, passable, empty, comment}}}
                                                    (the same format as redfield.json / camp.json)
    sources/orleans_custom/route_mills_preview.png  the sheet on the dry sand, 3x
    maps/00_route_mills_art.png                     the review sheet: both pieces at 3x on the sand, a test patch, the
                                                    unique 8x8 tile counts (flips free)

Pieces:
    route_mill 7x6, door (3,5)   a smaller sibling of Redfield's sugar mill (Cayenne's gym), without its chimney and
                                 sign: the front-gabled boiling house with the louvred monitor on its ridge, the board
                                 gable, barred arched windows, the plank double door on the stone plinth; a tin lean-to
                                 each side, the crushing house's open bay (press wheel and rollers) on the east and a
                                 loading bay stacked with cut cane on the west. It is the Redfield mill shifted up
                                 16 px (the same 8 px phase), with the wall two tile rows shorter.
    drying_shed 4x3 (blocking)   an open-sided timber shed under a tin roof (the lean-tos' cells), strings of red
                                 peppers hanging from the eave, a slatted drying rack laid with peppers between the
                                 posts. Mirror-symmetric.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import make_redfield_art as R  # noqa: E402
from make_redfield_art import (Art, INK, BR, BR_D, BR_L, T_D, T, T_L, T_HI, W_D, W, W_L, GOLD, CN, CN_D,  # noqa: E402
                               PEP, KEY)

PIECES = {}


def add(name, art, comment, doors=(), walk=()):
    empty = [[i, j] for j in range(art.h) for i in range(art.w)
             if all(art.px[i * 16 + x, j * 16 + y] == KEY for y in range(16) for x in range(16))]
    PIECES[name] = (art, {"w": art.w, "h": art.h, "comment": comment, "doors": [list(d) for d in doors],
                          "passable": [list(c) for c in walk], "empty": empty})


def rib(y):
    return (T, T_HI, T_L, T_L)[y % 4]


def route_mill():
    """A Route 17 sugar mill, 7x6, door (3,5): Redfield's mill moved up 16 px (so every shared part is the same
    cells): the boiling house mirrored about x 56, a tin lean-to each side (the west one the east one's mirror), the
    press bay on the east, a loading bay stacked with cane on the west. MILL."""
    a = Art(7, 6)
    CX = 56

    def g(x):
        u = x - 22 if x < CX else 89 - x
        return 44 - u // 2                     # the gable's apex at y 28, the eaves at y 44

    # ---- the boiling house, left half, mirrored
    for x in range(22, CX):
        for y in range(8, g(x)):
            a.put(x, y, rib(y))
    a.hline(22, CX - 1, 7, INK)
    for x in range(44, CX):                    # the monitor along the ridge
        for y in range(2, 30):
            if x in (44, 45):
                c = INK if y % 2 == 0 else T_D
                if y < 6:
                    continue
            else:
                c = rib(y)
            a.put(x, y, c)
    a.hline(46, CX - 1, 1, INK)
    a.vline(46, 1, 5, INK)
    a.vline(43, 5, 29, INK)
    for x in range(44, CX):
        top = 24 - (x - 44) // 3
        for y in range(top, 30):
            a.put(x, y, INK if y in (top, 29) else T_HI if y == top + 1 else (INK if y % 2 else T_D))
    for x in range(22, CX):                    # bargeboards over the board gable
        gy = g(x)
        for y in range(gy + 4, 54):
            if x >= 24:
                k = x % 4
                a.put(x, y, W_D if k == 0 else W_L if k == 1 else W)
        for i, c in enumerate((INK, W_L, W, INK)):
            a.put(x, gy + i, c)
    a.hline(22, CX - 1, 54, INK)               # the wall plate
    a.hline(22, CX - 1, 55, W_L)
    a.hline(22, CX - 1, 56, W)
    a.hline(22, CX - 1, 57, W_D)
    R.brick(a, 24, 58, CX - 1, 87)
    R.arch_window(a, 26, 64)
    R.mill_door_leaf(a, 40, 64)
    for y, c in ((64, INK), (65, BR_L), (66, INK), (67, W_L)):
        a.hline(48, CX - 1, y, c)
    R.boards(a, 48, 68, CX - 1, 95)
    for sy in (76, 92):
        a.hline(48, CX - 1, sy, T_D)
        a.hline(48, CX - 1, sy + 1, INK)
    a.vline(CX - 1, 68, 95, INK)
    R.plinth(a, 24, 39, 88)
    a.mirror_span(22, 89, 0, 95)
    # ---- the east lean-to: tin roof, the press bay mirrored about x 104 (the Redfield mill's bay, 16 px higher)
    R.tin(a, 88, 16, 111, 55, shade=False)
    a.vline(111, 16, 55, INK)
    for y in range(56, 96):
        for x in range(88, 104):
            c = W_D
            if y in (56, 57, 58, 59):
                c = (W_L, W, W_D, INK)[y - 56]
            elif x % 8 in (0, 7):
                c = INK
            a.put(x, y, c)
    import math
    cx, cy = 104.0, 72.0
    for y in range(62, 83):
        for x in range(96, 104):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 6.2 <= d <= 8.2:
                a.put(x, y, INK if d > 7.6 or d < 6.7 else (T_HI if y + 0.5 < cy - 3 else T_L if y + 0.5 < cy else T))
            elif d < 6.2:
                ang = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) % 60
                a.put(x, y, T_L if 24 <= ang <= 36 and d > 1.8 else INK if d > 5.6 else W_D)
    for ang in range(0, 360, 30):
        r = math.radians(ang)
        x, y = int(math.floor(cx + math.cos(r) * 8.8)), int(math.floor(cy + math.sin(r) * 8.8))
        if 96 <= x < 104:
            a.put(x, y, INK)
    a.rect(102, 70, 103, 73, INK)
    a.put(103, 71, T_HI)
    a.rect(96, 83, 103, 95, INK)
    a.rect(97, 84, 103, 94, T_D)
    for rx, ry in ((100.0, 90.5), (104.0, 86.5)):
        a.ellipse(rx, ry, 3.0, 3.0, INK, x0=96, x1=103)
        a.ellipse(rx, ry, 2.1, 2.1, T, x0=96, x1=103)
        a.put(int(rx) - 1, int(ry) - 1, T_HI)
    for y in range(56, 96):
        for x in range(104, 112):
            a.px[x, y] = a.px[207 - x, y]
    # ---- the west lean-to: the east roof's mirror over a loading bay stacked with cut cane on a timber platform
    for y in range(16, 56):
        for x in range(0, 24):
            a.px[x, y] = a.px[111 - x, y]
    for y in range(56, 72):                    # the bay: the beam and the dim back wall (the east bay's cells)
        for x in range(0, 24):
            c = W_D
            if y in (56, 57, 58, 59):
                c = (W_L, W, W_D, INK)[y - 56]
            elif x % 8 in (0, 7):
                c = INK
            a.put(x, y, c)
    R.cane_stalks(a, 0, 23, 73, 87, ends=False)
    a.hline(0, 23, 72, INK)
    a.hline(0, 23, 88, INK)
    a.hline(0, 23, 89, W_L)
    a.hline(0, 23, 90, W)
    a.hline(0, 23, 91, INK)
    for y in range(92, 96):
        for x in range(0, 24):
            a.put(x, y, INK if x % 8 in (0, 7) else W_D)
    a.hline(0, 23, 95, INK)
    return a


def drying_shed():
    """A Route 16 pepper drying shed, 4x3, blocking: a tin roof (the lean-tos' cells) on timber posts, open all round;
    strings of red peppers hanging from the eave every 8 px, a slatted drying rack laid with peppers between the posts.
    Drawn on the left and mirrored. MILL."""
    a = Art(4, 3)
    R.tin(a, 0, 0, 31, 23, shade=False)        # the roof (its east end is the route mill's lean-to edge, mirrored)
    a.vline(0, 0, 23, INK)
    for x in range(1, 32):                     # the strings of peppers hanging from the eave (every 8 px)
        k = x % 8
        if k in (3, 4):
            for y in range(24, 35):
                if k == 3:
                    c = W_L if y < 26 else (PEP if (y - 26) % 3 != 2 else BR_D)
                else:
                    c = W_L if y < 26 else (BR_D if (y - 26) % 3 != 1 else PEP)
                a.put(x, y, c)
            a.put(x, 35, INK if k == 3 else KEY)
        if k == 2 and True:
            for y in (27, 30, 33):
                a.put(x, y, CN_D)
    a.hline(0, 31, 24, INK)                    # the eave's shadow line
    for px in (1,):                            # the corner post
        for y in range(24, 46):
            a.put(px, y, INK)
            a.put(px + 1, y, W_L)
            a.put(px + 2, y, W)
            a.put(px + 3, y, INK)
        a.hline(px, px + 3, 46, INK)
    # the drying rack: slats laid with peppers, on legs
    for y, c in ((36, INK), (37, W_L), (38, W), (39, INK)):
        a.hline(5, 31, y, c)
    for x in range(6, 32):
        if x % 4 in (1, 2):
            a.put(x, 37, PEP if x % 8 < 4 else BR_L)
    for lx in (9, 25):
        for y in range(40, 46):
            a.put(lx, y, INK)
            a.put(lx + 1, y, W_D)
        a.put(lx + 2, 45, INK)
    a.hline(5, 31, 40, INK)
    for x in range(5, 32):
        if x % 8 == 0:
            a.put(x, 41, BR_D)                 # a pepper fallen under the rack
    a.mirror_left()
    return a


# ================================================================ sheet, census, review
def build_pieces():
    PIECES.clear()
    add("route_mill", route_mill(), "Route 17 sugar mill (Redfield's mill without chimney or sign), 7x6.", doors=[(3, 5)])
    add("drying_shed", drying_shed(), "Route 16 pepper drying shed (open timber shed, tin roof, pepper strings), 4x3.")


def pack():
    W = 11
    sheet = Image.new("RGB", (W * 16, 6 * 16), KEY)
    place = {"route_mill": (0, 0), "drying_shed": (7, 0)}
    index = {}
    for n, (cx, cy) in place.items():
        art, meta = PIECES[n]
        sheet.paste(art.im, (cx * 16, cy * 16))
        index[n] = dict(meta, x=cx, y=cy)
    return sheet, index


def census():
    seen, rows = set(), []
    mill_tiles = set(R.tiles_of(R.sugar_mill().im))
    for n, (art, meta) in PIECES.items():
        ts = R.tiles_of(art.im)
        new = 0
        for k in ts:
            if k not in seen:
                seen.add(k)
                new += 1
        rows.append((n, art.w, art.h, len(set(ts)), new, len(set(ts) & mill_tiles)))
    return rows, len(seen)


def patch():
    """Three mills along a dirt road, the cane railway below them, a drying shed beside pepper rows."""
    import make_dry_country as dc
    dry = json.load(open(os.path.join(HERE, "dry_country.json"), encoding="utf-8"))
    dsheet = Image.open(os.path.join(HERE, dry["png"])).convert("RGB")
    rows = ["dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "::::::::::::::::::::::::::::::",
            "::::::::::::::::::::::::::::::",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddddddddddddddddddddddddddddd",
            "dddqqqqqqqqqqdddddddddddddddddd",
            "dddqqqqqqqqqqdddddddddddddddddd",
            "dddqqqqqqqqqqdddddddddddddddddd",
            "dddddddddddddddddddddddddddddd"]
    rows = [r[:30] for r in rows]
    for x in (4, 13, 22):                     # the paths up to the doors
        rows[6] = rows[6][:x - 1] + ":" + rows[6][x:]
    img = dc.render_patch(dsheet, dry, rows)
    R.build_pieces()
    objs = [("route_mill", 1, 1), ("route_mill", 10, 1), ("route_mill", 19, 1)]
    rp = {"route_mill": PIECES["route_mill"][0].im, "drying_shed": PIECES["drying_shed"][0].im}
    for x in range(30):
        n = "rail_h"
        objs.append((n, x, 11))
    objs += [("cane_truck", 3, 10), ("cane_truck", 7, 10), ("drying_shed", 15, 12), ("cane_pile", 26, 4)]
    for n, x, y in objs:
        im = rp[n] if n in rp else R.PIECES[n][0].im
        img.paste(im, (x * 16, y * 16), R.mask(im))
    return img


def review(path, rows, total):
    S = 3
    sand = R.sand_cell()[0]
    out = Image.new("RGB", (1500, 1700), (36, 40, 44))
    d = ImageDraw.Draw(out)
    d.text((10, 8), "Route mills art (make_route_mills_art.py): both pieces at 3x on the dry sand", fill=(255, 240, 160))
    x, y = 10, 28
    info = {r[0]: r for r in rows}
    for n in ("route_mill", "drying_shed"):
        art = PIECES[n][0].im
        pad = Image.new("RGB", (art.width + 16, art.height + 16))
        for yy in range(0, pad.height, 16):
            for xx in range(0, pad.width, 16):
                pad.paste(sand, (xx, yy))
        pad.paste(art, (8, 8), R.mask(art))
        big = pad.resize((pad.width * S, pad.height * S), Image.NEAREST)
        out.paste(big, (x, y))
        _, w, h, tot, new, shared = info[n]
        m = PIECES[n][1]
        door = f" door {tuple(m['doors'][0])}" if m["doors"] else " (blocking)"
        d.text((x, y + big.height + 4), f"{n} {w}x{h}{door}: {tot} tiles ({shared} of them Redfield sugar_mill cells)",
               fill=(225, 225, 210))
        x += big.width + 40
    y += (6 * 16 + 16) * 3 + 30
    d.text((10, y), "Test patch at 3x: three mills along a dirt road, the cane railway below, a drying shed beside "
                    "pepper rows", fill=(255, 240, 160))
    p = patch()
    big = p.resize((p.width * S, p.height * S), Image.NEAREST)
    out.paste(big, (10, y + 18))
    y += 18 + big.height + 12
    d.text((10, y), f"TOTAL: {total} unique 8x8 tiles for the two pieces (flips free, fully clear tiles free)",
           fill=(255, 240, 160))
    out = out.crop((0, 0, max(1500, big.width + 20), y + 24))
    out.save(path)


def main():
    build_pieces()
    sheet, index = pack()
    sheet.save(os.path.join(HERE, "route_mills.png"))
    with open(os.path.join(HERE, "route_mills.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_comment": "Dry-route mills and drying sheds (make_route_mills_art.py): piece -> sheet cell and "
                               "size; magenta = clear. Same format as redfield.json.", "pieces": index}, f, indent=1)
        f.write("\n")
    R.on_ground(sheet, R.sand_cell()[0]).resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(
        os.path.join(HERE, "route_mills_preview.png"))
    rows, total = census()
    review(os.path.join(MAPGEN, "maps", "00_route_mills_art.png"), rows, total)
    for n, w, h, tot, new, shared in rows:
        print(f"  {n:12s} {w}x{h} {tot:3d} tiles ({new} new, {shared} shared with sugar_mill)")
    print(f"  TOTAL unique 8x8 tiles: {total}")
    for n, (art, meta) in PIECES.items():
        cols = {c for c in art.im.getdata() if c != KEY}
        print(f"  {n}: {len(cols)} colours")


if __name__ == "__main__":
    main()

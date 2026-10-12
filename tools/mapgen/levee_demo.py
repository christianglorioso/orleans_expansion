"""Concept mock-ups of a levee (a raised embankment between a road and a river), four ways, for review:
  0. today: flat ground, road, grass verge, water
  1. Johto grass ledge (HnS johto_general 0B0/0B1): grass with a rocky lip, one tile high
  2. Brick City rocky bank (Brick City 2D6/368/365): a rock face dropping straight into the water
  3. own art: a grassy earth embankment with a shaded slope and riprap stones at the waterline
Not in game yet: the pieces are composited here with our grass texture swapped in under the borrowed art.

usage (from the decomp root): python tools/mapgen/levee_demo.py <out.png>
"""
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import Tilesets  # noqa: E402

W, H = 20, 10  # tiles per panel


def ours():
    m = json.load(open(os.path.join(HERE, "tilesets", "orleans_route.mapping.json")))["metatiles"]
    g = json.load(open(os.path.join(HERE, "tilesets", "orleans_general.mapping.json")))["metatiles"]
    ts = Tilesets("data/tilesets/primary/orleans_general", "data/tilesets/secondary/orleans_route")
    t = lambda n: ts.metatile(m[n] if n in m else g[n]).convert("RGB")
    return {k: t(n) for k, n in {"grass": "ekat:grass", "water": "ekat:water_C", "shore": "ekat:water_N",
                                  "tall": "ekat:tallgrass", "pathN": "johto:0D1", "pathC": "johto:0D9",
                                  "pathS": "johto:0E1"}.items()}


def swap_grass(tile, grass):
    """Borrowed art keeps its rock; wherever it shows its own (mint) grass, our grass texture shows instead."""
    a, b = tile.load(), grass.load()
    out = tile.copy()
    o = out.load()
    for y in range(16):
        for x in range(16):
            r, g_, bl = a[x, y]
            if g_ > r + 18 and g_ > bl + 8:  # greenish: grass
                o[x, y] = b[x, y]
    return out


def own_slope(grass, water, row, seed=0):
    """Own art for the embankment's river face, top to bottom: row 0 the crest and upper slope, row 1 the
    lower slope (darker, falling away), row 2 riprap stones at the toe, over the water's edge."""
    rnd = random.Random(seed * 7 + row)
    im = Image.new("RGB", (16, 16))
    if row in (0, 1):
        im.paste(grass, (0, 0))
        px, g = im.load(), grass.load()
        for y in range(16):
            for x in range(16):
                r, gg, b = g[x, y]
                k = 1.0 - 0.12 * row - 0.14 * (y / 15)  # the slope darkens as it falls toward the river
                px[x, y] = (int(r * k), int(gg * k), int(b * k))
        if row == 0:
            for x in range(16):  # the crest: a lit edge along the top of the bank
                px[x, 1] = (150, 182, 112)
                px[x, 2] = (128, 160, 96)
        for _ in range(4):  # tufts on the slope
            x, y = rnd.randrange(1, 15), rnd.randrange(4, 14)
            px[x, y] = (70, 98, 56)
            px[x, y - 1] = (92, 124, 70)
        return im
    im.paste(water, (0, 0))
    px = im.load()
    for cx in range(2, 16, 5):  # riprap: grey stones heaped at the waterline
        cy = 4 + rnd.randrange(0, 3)
        for y in range(0, 16):
            for x in range(cx - 4, cx + 4):
                if 0 <= x < 16 and (x - cx) ** 2 + ((y - cy) * 1.3) ** 2 <= 16:
                    px[x, y] = (156, 150, 138) if y < cy - 1 else (118, 112, 104) if y < cy + 2 else (86, 82, 78)
    for x in range(16):
        for y in range(0, 2):
            if px[x, y] == water.load()[x, y]:
                px[x, y] = (96, 88, 74)  # wet earth at the toe
    return im


def panel(kind, t):
    im = Image.new("RGB", (W * 16, H * 16))
    rnd = random.Random(1)
    for y in range(H):
        for x in range(W):
            im.paste(t["grass"], (x * 16, y * 16))
    for x in range(W):  # some tall grass up top, the levee road below it
        for y in (0, 1):
            if (x // 3) % 2 == 0:
                im.paste(t["tall"], (x * 16, y * 16))
        im.paste(t["pathN"], (x * 16, 3 * 16))
        im.paste(t["pathS"], (x * 16, 4 * 16))
    jt = Tilesets("data/tilesets/primary/johto_general_hns", "data/tilesets/secondary/route_32_hns", "frlg")
    cm = json.load(open(os.path.join(HERE, "tilesets", "orleans_city.mapping.json")))["metatiles"]
    bt = Tilesets("data/tilesets/primary/orleans_general", "data/tilesets/secondary/orleans_city")
    for x in range(W):
        if kind == 0:  # flat: a grass verge, then the shore
            im.paste(t["shore"], (x * 16, 6 * 16))
        elif kind == 1:  # Johto grass ledge, then a grass berm, then the shore
            im.paste(swap_grass(jt.metatile(0x0B0 + x % 2).convert("RGB"), t["grass"]), (x * 16, 5 * 16))
            im.paste(t["shore"], (x * 16, 7 * 16))
        elif kind == 2:  # Brick City rock face straight into the water
            im.paste(swap_grass(bt.metatile(cm["brick:2D6"]).convert("RGB"), t["grass"]), (x * 16, 6 * 16))
        else:  # own art: shaded slope, riprap at the waterline
            lv = Image.open(os.path.join(HERE, "sources", "orleans_custom", "levee.png")).convert("RGB")
            for r in range(3):
                cell = lv.crop(((x % 2) * 16, r * 16, (x % 2) * 16 + 16, r * 16 + 16))
                base = (t["grass"] if r < 2 else t["water"]).copy()
                bp, cp = base.load(), cell.load()
                for yy in range(16):
                    for xx in range(16):
                        if cp[xx, yy] != (255, 0, 255):
                            bp[xx, yy] = cp[xx, yy]
                im.paste(base, (x * 16, (5 + r) * 16))
        first_water = {0: 7, 1: 8, 2: 7, 3: 8}[kind]
        for y in range(first_water, H):
            im.paste(t["water"], (x * 16, y * 16))
    return im.resize((im.width * 3, im.height * 3), Image.NEAREST)


def main(out):
    t = ours()
    titles = ["Today: flat (road, grass verge, river)", "Existing art: Johto grass ledge (HnS)",
              "Existing art: Brick City rock bank", "Own art: grassy embankment with riprap"]
    panels = [panel(k, t) for k in range(4)]
    pw, ph = panels[0].size
    try:
        f = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        f = ImageFont.load_default()
    sheet = Image.new("RGB", (pw * 2 + 60, (ph + 60) * 2 + 20), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    for i, (title, p) in enumerate(zip(titles, panels)):
        x, y = 20 + (i % 2) * (pw + 20), 10 + (i // 2) * (ph + 60)
        d.text((x, y), title, fill=(47, 72, 60), font=f)
        sheet.paste(p, (x, y + 42))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1])

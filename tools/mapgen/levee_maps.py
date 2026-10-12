"""Concept composites: river banks on real maps as they are, as Brick City rock banks, and as our own grassy
levee with riprap. Painted onto the built previews (maps/<key>_preview.png) for review; nothing in the game
changes.

usage (from the decomp root): python tools/mapgen/levee_maps.py <out.png> key[:x0,y0,x1,y1] ...
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from levee_demo import ours, swap_grass  # noqa: E402
from render import Tilesets  # noqa: E402

WATER = set("~wI")
KEY = (255, 0, 255)


def load_art(t):
    cm = json.load(open(os.path.join(HERE, "tilesets", "orleans_city.mapping.json")))["metatiles"]
    bt = Tilesets("data/tilesets/primary/orleans_general", "data/tilesets/secondary/orleans_city")
    brick = {k: swap_grass(bt.metatile(cm[f"brick:{i}"]).convert("RGB"), t["grass"])
             for k, i in (("S", "2D6"), ("E", "214"), ("W", "213"))}
    lv = Image.open(os.path.join(HERE, "sources", "orleans_custom", "levee.png")).convert("RGB")
    own_s = [[lv.crop((v * 16, r * 16, v * 16 + 16, r * 16 + 16)) for r in range(3)] for v in range(2)]
    # the east- and west-facing banks: the south-facing face turned toward the river
    own_e = [[c.rotate(90, expand=True) for c in v] for v in own_s]      # top -> left: crest west, water east
    own_w = [[c.rotate(-90, expand=True) for c in v] for v in own_s]     # top -> right: crest east, water west
    return brick, own_s, own_e, own_w


def over(base, cell):
    """Own art cells keep magenta as transparent: what's underneath shows there."""
    out = base.copy()
    bp, cp = out.load(), cell.load()
    for y in range(16):
        for x in range(16):
            if cp[x, y] != KEY:
                bp[x, y] = cp[x, y]
    return out


def banks(grid, blocked):
    """Bank cells: land with water beside it on one side and land behind it (straight stretches)."""
    h, w = len(grid), len(grid[0])
    wet = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] in WATER
    dry = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] not in WATER and (x, y) not in blocked
    out = []
    for y in range(h):
        for x in range(w):
            if not dry(x, y):
                continue
            if wet(x, y + 1) and dry(x, y - 1) and wet(x - 1, y + 1) and wet(x + 1, y + 1):
                out.append(("S", x, y))
            elif wet(x + 1, y) and dry(x - 1, y) and wet(x + 1, y - 1) and wet(x + 1, y + 1):
                out.append(("E", x, y))
            elif wet(x - 1, y) and dry(x + 1, y) and wet(x - 1, y - 1) and wet(x - 1, y + 1):
                out.append(("W", x, y))
    return out


def variant(key, kind, t, art):
    spec = json.load(open(os.path.join(HERE, "maps", f"{key}.json"), encoding="utf-8"))
    grid = [l.rstrip("\n") for l in open(os.path.join(HERE, "maps", spec["grid"]))]
    im = Image.open(os.path.join(HERE, "maps", f"{key}_preview.png")).convert("RGB")
    if kind == "current":
        return im
    cfg_blocked = set()
    for b in spec["buildings"]:
        rows = b.get("rows")
        if rows is None:
            try:
                rows = json.load(open(os.path.join(HERE, "tilesets", spec["tileset"] + ".json"),
                                      encoding="utf-8"))["prefabs"][b["prefab"]]["rows"]
            except (KeyError, FileNotFoundError):
                continue
        for j, row in enumerate(rows):
            for i in range(len(row)):
                cfg_blocked.add((b["x"] + i, b["y"] + j))
    brick, own_s, own_e, own_w = art
    road = lambda x, y: 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] in ":=#"
    for side, x, y in banks(grid, cfg_blocked):
        v = (x + y) % 2
        cell = lambda cx, cy: im.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
        if kind == "brick":
            im.paste(brick[side], (x * 16, y * 16))
            continue
        if side == "S":  # crest above (unless it's the road), slope here, riprap in the water below
            if not road(x, y - 1) and (x, y - 1) not in cfg_blocked:
                im.paste(over(cell(x, y - 1), own_s[v][0]), (x * 16, (y - 1) * 16))
            im.paste(over(cell(x, y), own_s[v][1]), (x * 16, y * 16))
            im.paste(over(cell(x, y + 1), own_s[v][2]), (x * 16, (y + 1) * 16))
        else:
            parts, dx = (own_e[v], 1) if side == "E" else (own_w[v], -1)
            if not road(x - dx, y) and (x - dx, y) not in cfg_blocked:
                im.paste(over(cell(x - dx, y), parts[0]), ((x - dx) * 16, y * 16))
            im.paste(over(cell(x, y), parts[1]), (x * 16, y * 16))
            im.paste(over(cell(x + dx, y), parts[2]), ((x + dx) * 16, y * 16))
    return im


def main(out, items):
    t = ours()
    art = load_art(t)
    try:
        f = ImageFont.truetype("arialbd.ttf", 30)
        f2 = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        f = f2 = ImageFont.load_default()
    rows = []
    for item in items:
        key, _, box = item.partition(":")
        x0, y0, x1, y1 = map(int, box.split(",")) if box else (0, 0, 999, 999)
        panels = []
        for kind in ("current", "brick", "own"):
            im = variant(key, kind, t, art)
            c = im.crop((x0 * 16, y0 * 16, min(im.width, x1 * 16), min(im.height, y1 * 16)))
            s = max(1, min(3, 760 // c.width))
            panels.append(c.resize((c.width * s, c.height * s), Image.NEAREST))
        rows.append((key, panels))
    W = max(sum(p.width for p in ps) + 80 for _, ps in rows)
    H = sum(max(p.height for p in ps) + 100 for _, ps in rows) + 70
    sheet = Image.new("RGB", (W, H), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 56], fill=(47, 72, 60))
    d.text((20, 10), "River banks on the real maps: current / Brick City rock bank / own-art levee (concept)",
           fill="white", font=f)
    y = 70
    for key, ps in rows:
        d.text((20, y), key.replace("_", " ").title(), fill=(47, 72, 60), font=f)
        x = 20
        for label, p in zip(("Current", "Brick City", "Own art"), ps):
            d.text((x, y + 38), label, fill=(80, 80, 80), font=f2)
            sheet.paste(p, (x, y + 68))
            x += p.width + 20
        y += max(p.height for p in ps) + 100
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

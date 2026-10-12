"""Every route on one sheet: each route's planning mockup (its map panel) beside the map as built, numbered, in a
grid, for reviewing all of them at once.

usage (from the decomp root): python tools/mapgen/routes_sheet.py [out.png] [route keys...]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from town_sheet import built  # noqa: E402

CELL_W = 980  # width of one route's pair


def mock_panel(path):
    """The mockup's map panel (the left part, below the title band): the planning sheets put the map on the left
    and the key/notes on the right."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.crop((0, int(h * 0.0), int(w * 0.62), h))


def main(out=None, keys=None):
    keys = keys or [f"route_{n}" for n in range(2, 26)]
    try:
        f = ImageFont.truetype("arialbd.ttf", 26)
    except OSError:
        f = ImageFont.load_default()
    pairs = []
    for k in keys:
        spec = json.load(open(os.path.join(HERE, "maps", f"{k}.json"), encoding="utf-8"))
        im, b = built(k)
        mock = mock_panel(spec["mockup"])
        half = (CELL_W - 30) // 2
        s1 = half / mock.width
        s2 = half / im.width
        mock = mock.resize((half, int(mock.height * s1)), Image.LANCZOS)
        im = im.resize((half, int(im.height * s2)), Image.LANCZOS if s2 < 1 else Image.NEAREST)
        hh = max(mock.height, im.height)
        cell = Image.new("RGB", (CELL_W, hh + 44), (250, 247, 240))
        d = ImageDraw.Draw(cell)
        d.text((6, 6), k.replace("_", " ").title(), fill=(47, 72, 60), font=f)
        cell.paste(mock, (0, 40))
        cell.paste(im, (half + 30, 40))
        pairs.append(cell)
        print(k, "ok")
    cols = 3
    rows = [pairs[i:i + cols] for i in range(0, len(pairs), cols)]
    W = cols * CELL_W + (cols + 1) * 20
    H = sum(max(c.height for c in r) + 20 for r in rows) + 20
    sheet = Image.new("RGB", (W, H), (230, 226, 216))
    y = 20
    for r in rows:
        x = 20
        for c in r:
            sheet.paste(c, (x, y))
            x += CELL_W + 20
        y += max(c.height for c in r) + 20
    out = out or os.path.join(HERE, "maps", "00_routes_all.png")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2:] or None)

"""maps/00_crescent_nw_grid.png: the north-west corner of Crescent City before | after, 3x, with map column and row numbers.
usage: python tools/mapgen/crescent_nw_grid.py <before.png>   (after = maps/crescent_city_preview.png)"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
X0, Y0, X1, Y1, S = 0, 10, 30, 28, 3  # map cells


def panel(path, title):
    im = Image.open(path).convert("RGB").crop((X0 * 16, Y0 * 16, X1 * 16, Y1 * 16))
    im = im.resize((im.width * S, im.height * S), Image.NEAREST)
    t = 48  # one tile at 3x
    out = Image.new("RGB", (im.width + 40, im.height + 56), (250, 247, 238))
    out.paste(im, (40, 56))
    d = ImageDraw.Draw(out)
    d.text((44, 4), title, fill=(0, 0, 0))
    for x in range(X0, X1):
        px = 40 + (x - X0) * t
        d.line([(px, 56), (px, out.height)], fill=(255, 255, 255) if x % 5 else (255, 200, 0), width=1)
        d.text((px + 14, 36 if x % 2 else 22), str(x), fill=(0, 0, 0))
    for y in range(Y0, Y1):
        py = 56 + (y - Y0) * t
        d.line([(40, py), (out.width, py)], fill=(255, 255, 255) if y % 5 else (255, 200, 0), width=1)
        d.text((8, py + 18), str(y), fill=(0, 0, 0))
    return out


a = panel(sys.argv[1], "BEFORE (map coordinates; gold lines every 5)")
b = panel(os.path.join(HERE, "maps", "crescent_city_preview.png"), "AFTER")
sheet = Image.new("RGB", (a.width + b.width + 20, a.height), (250, 247, 238))
sheet.paste(a, (0, 0))
sheet.paste(b, (a.width + 20, 0))
sheet.save(os.path.join(HERE, "maps", "00_crescent_nw_grid.png"))
print(sheet.size)

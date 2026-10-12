"""Review sheet for the river levees: each levee map drawn from the built tilesets without and with its levee,
plus zoomed crops of the corners and run ends (where seams would show).

usage (from the decomp root): python tools/mapgen/levee_review.py <out.png> [key[:x0,y0,x1,y1][@zoom] ...]
with no keys: every map in levee.MAPS, whole.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402
import levee  # noqa: E402
from render import Tilesets, render  # noqa: E402


def draw(key, with_levee):
    build.MAPPING.clear()  # one map's tileset names at a time (build.py itself runs once per map)
    build.USED.clear()
    build.WANTED.clear()
    b = build.Builder(os.path.join(HERE, "maps", f"{key}.json"))
    if with_levee:
        b.draw()  # the map as built (levee, approaches and all)
    else:
        b.terrain()
        b.buildings()
    root = os.getcwd()
    ts = Tilesets(os.path.join(root, b.ts["primary_dir"]), os.path.join(root, b.ts["secondary_dir"]))
    return render(ts, b.flat(), b.w), b


def main(out, items):
    items = items or sorted(levee.MAPS)
    try:
        f = ImageFont.truetype("arialbd.ttf", 26)
        f2 = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        f = f2 = ImageFont.load_default()
    rows = []
    for item in items:
        item, _, zoom = item.partition("@")
        key, _, box = item.partition(":")
        before, _ = draw(key, False)
        after, b = draw(key, True)
        x0, y0, x1, y1 = map(int, box.split(",")) if box else (0, 0, b.w, b.h)
        crop = lambda im: im.crop((x0 * 16, y0 * 16, min(b.w, x1) * 16, min(b.h, y1) * 16))
        a, c = crop(before), crop(after)
        s = int(zoom) if zoom else max(1, min(3, 900 // a.width))
        rows.append((f"{key} ({x0},{y0})-({x1},{y1})" if box else key,
                     a.resize((a.width * s, a.height * s), Image.NEAREST),
                     c.resize((c.width * s, c.height * s), Image.NEAREST)))
        if b.pending_blends or build.WANTED:
            print(key, "still asks for", len(b.pending_blends) + len(build.WANTED), "pieces (compose, then rebuild)")
    W = max(a.width + c.width for _, a, c in rows) + 60
    H = sum(a.height + 80 for _, a, _ in rows) + 60
    sheet = Image.new("RGB", (W, H), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 48], fill=(47, 72, 60))
    d.text((16, 10), "River levees (own art): before / after, from the built tilesets", fill="white", font=f)
    y = 60
    for label, a, c in rows:
        d.text((16, y), label.replace("_", " "), fill=(47, 72, 60), font=f2)
        sheet.paste(a, (16, y + 30))
        sheet.paste(c, (a.width + 40, y + 30))
        y += a.height + 80
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

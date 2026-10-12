"""Review sheet for the Route 1 slice polish: maps/00_route_1_slice_review.png.

usage (from the decomp root): python -W ignore tools/mapgen/route_1_review.py [--before-dir DIR]

before | after for the whole map (2x), then 3x crops (before | after) of every area the polish changed, then the three
joins (Isle Marais, Grand Oak, the Old Water), each before | after. The "before" images are maps/route_1_before_preview.png
(the approved 2026-10-10 map as it stood when the polish began) and maps/route_1_join_before_<im|go|ow>.png (joined.py
renders of that state); the "after" side is rendered here from the current maps (joined.py for the joins).
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "maps")
ROOT = os.path.dirname(os.path.dirname(HERE))

CROPS = [   # (title, x0, y0, x1, y1) in cells
    ("North-west: water edge, marsh grove, channel, pier and shrine islet", 0, 0, 16, 15),
    ("Road: the meander, its bevels and the verges (north half)", 8, 0, 24, 24),
    ("North-east: the marsh bay and the tall-grass strip", 14, 0, 28, 22),
    ("West: marsh bay, big field, bay and south-west grove", 0, 14, 16, 36),
    ("East: pond and the tall-grass fields", 14, 20, 28, 40),
    ("South end: causeway, islet, pirogue bar, bays and banks", 0, 36, 28, 48),
]


def font(n):
    try:
        return ImageFont.truetype("arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def crop(im, box, k):
    x0, y0, x1, y1 = box
    c = im.crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


def label(im, text, size=22):
    out = Image.new("RGB", (im.width, im.height + size + 14), (250, 247, 240))
    out.paste(im, (0, size + 14))
    ImageDraw.Draw(out).text((8, 6), text, fill=(30, 40, 30), font=font(size))
    return out


def side(a, b, gap=24):
    out = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)), (250, 247, 240))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + gap, 0))
    return out


def stack(parts, gap=28):
    w = max(p.width for p in parts)
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), (250, 247, 240))
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.height + gap
    return out


def join(pair, name):
    out = os.path.join(tempfile.gettempdir(), f"route_1_join_{name}.png")
    subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "joined.py"), out, pair], cwd=ROOT,
                   check=True, capture_output=True)
    return Image.open(out).convert("RGB")


def main():
    before = Image.open(os.path.join(MAPS, "route_1_before_preview.png")).convert("RGB")
    after = Image.open(os.path.join(MAPS, "route_1_preview.png")).convert("RGB")
    sheet = [label(side(label(before.resize((before.width * 2, before.height * 2), Image.NEAREST), "before (approved 2026-10-10)"),
                        label(after.resize((after.width * 2, after.height * 2), Image.NEAREST), "after")),
                   "Route 1 slice polish: whole map (2x)", 30)]
    for title, x0, y0, x1, y1 in CROPS:
        k = 3
        sheet.append(label(side(label(crop(before, (x0, y0, x1, y1), k), "before"), label(crop(after, (x0, y0, x1, y1), k), "after")),
                           title + "  (3x)", 26))
    for name, pair in (("im", "isle_marais:route_1"), ("go", "grand_oak:route_1"), ("ow", "old_water:route_1")):
        bp = os.path.join(MAPS, f"route_1_join_before_{name}.png")
        if os.path.exists(bp):
            sheet.append(label(side(label(Image.open(bp).convert("RGB"), "before"), label(join(pair, name), "after")),
                               f"Join: {pair}", 26))
        else:
            sheet.append(label(join(pair, name), f"Join: {pair}", 26))
    out = stack(sheet)
    dest = os.path.join(MAPS, "00_route_1_slice_review.png")
    out.save(dest)
    print(dest, out.size)


if __name__ == "__main__":
    main()

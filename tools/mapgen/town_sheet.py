"""Town-by-town review sheet: the planning mockup beside the map as built (drawn from the built tilesets, with
doors, people and items marked), at a size that reads.

usage (from the decomp root): python tools/mapgen/town_sheet.py <key> [out.png]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402
from render import Tilesets, render  # noqa: E402


def built(key):
    build.MAPPING.clear()
    b = build.Builder(os.path.join(HERE, "maps", f"{key}.json"))
    b.draw()
    root = os.getcwd()
    ts = Tilesets(os.path.join(root, b.ts["primary_dir"]), os.path.join(root, b.ts["secondary_dir"]))
    im = render(ts, b.flat(), b.w).convert("RGB")
    d = ImageDraw.Draw(im)
    mark = lambda x, y, c: d.rectangle([x * 16 + 1, y * 16 + 1, x * 16 + 14, y * 16 + 14], outline=c, width=2)
    for w in b.warps:
        mark(w["x"], w["y"], (255, 0, 255))
    for o in b.spec.get("objects", []):
        mark(o["x"], o["y"], (0, 160, 255))
    for it in b.spec.get("items", []):
        mark(it["x"], it["y"], (255, 200, 0))
    for s in b.spec.get("signs", []):
        mark(s["x"], s["y"], (255, 120, 0))
    return im, b


def main(key, out=None):
    spec = json.load(open(os.path.join(HERE, "maps", f"{key}.json"), encoding="utf-8"))
    mock = Image.open(spec["mockup"]).convert("RGB")
    im, b = built(key)
    s = 2 if im.width <= 1100 else 1
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    mh = im.height
    mock = mock.resize((round(mock.width * mh / mock.height), mh), Image.LANCZOS)
    try:
        f = ImageFont.truetype("arialbd.ttf", 30)
        f2 = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        f = f2 = ImageFont.load_default()
    W, H = mock.width + im.width + 60, mh + 110
    sheet = Image.new("RGB", (W, H), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 54], fill=(47, 72, 60))
    d.text((20, 10), f"{b.spec['map']}: mockup / as built ({b.w}x{b.h})", fill="white", font=f)
    d.text((20, 64), "Mockup", fill=(80, 80, 80), font=f2)
    d.text((mock.width + 40, 64), "Built  (magenta door, blue person, yellow item, orange sign)", fill=(80, 80, 80),
           font=f2)
    sheet.paste(mock, (20, 96))
    sheet.paste(im, (mock.width + 40, 96))
    out = out or os.path.join(HERE, "maps", f"00_town_{key}.png")
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:])

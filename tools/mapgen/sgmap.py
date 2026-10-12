"""Label a tileset sheet cell by cell, to read building layouts straight off it.

The HnS tilesets in this repo (data/tilesets/secondary/*_hns) are laid out as pictures: a building
appears whole when the metatiles are drawn 16 to a row. This draws a region of that sheet with every
cell's metatile id, so a prefab's rows can be copied exactly.

usage (from the decomp root):
    python tools/mapgen/sgmap.py <secondary> <out.png> [first_id last_id] [--cols 16] [--primary johto_general_hns]
    python tools/mapgen/sgmap.py <secondary> --rows <top_left_id> <w> <h> [--cols 16]
        prints the rectangle's ids as prefab rows (JSON)
"""
import json
import sys

from PIL import Image, ImageDraw

from render import Tilesets

T = "data/tilesets"


def opt(args, name, default):
    return args[args.index(name) + 1] if name in args else default


def main(args):
    sec, cols = args[0], int(opt(args, "--cols", 16))
    if args[1] == "--rows":
        top, w, h = int(args[2], 16), int(args[3]), int(args[4])
        print(json.dumps([[f"{top + j * cols + i:03X}" for i in range(w)] for j in range(h)]))
        return
    prim = opt(args, "--primary", "johto_general_hns")
    ts = Tilesets(f"{T}/primary/{prim}", f"{T}/secondary/{sec}", "frlg")
    pos = [a for a in args[2:] if not a.startswith("--") and a not in (opt(args, "--cols", ""), opt(args, "--primary", ""))]
    lo, hi = (int(pos[0], 16), int(pos[1], 16)) if len(pos) >= 2 else (0x280, 0x280 + ts.count_secondary() - 1 if hasattr(ts, "count_secondary") else 0x4FF)
    n = hi - lo + 1
    rows = (n + cols - 1) // cols
    s = 3
    im = Image.new("RGB", (cols * 16, rows * 16))
    for k in range(n):
        try:
            im.paste(ts.metatile(lo + k), ((k % cols) * 16, (k // cols) * 16))
        except Exception:
            pass
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for k in range(n):
        x, y = (k % cols) * 48, (k // cols) * 48
        d.rectangle([x, y, x + 47, y + 47], outline=(0, 0, 0))
        t = f"{lo + k:03X}"
        d.text((x + 2, y + 2), t, fill=(0, 0, 0))
        d.text((x + 1, y + 1), t, fill=(255, 255, 0))
    im.save(args[1])
    print(args[1], im.size)


if __name__ == "__main__":
    main(sys.argv[1:])

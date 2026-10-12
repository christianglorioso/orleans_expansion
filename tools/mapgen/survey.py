"""Render a secondary tileset's metatiles the way Porymap's selector shows them (8 wide), for browsing.

usage: python survey.py <primary> <secondary> <out.png> [--layout frlg] [--scale 2] [--cols 8]
       python survey.py --pairs <secondary> <out.png> <primary> [<primary> ...] [--layout frlg]
           (renders the first 64 metatiles once per primary, side by side, to spot the right pairing)
"""
import sys
from PIL import Image, ImageDraw

from render import Tilesets

T = "data/tilesets"


def sheet(ts, start, n, cols, scale, label=True):
    rows = (n + cols - 1) // cols
    im = Image.new("RGB", (cols * 16, rows * 16), (0, 0, 0))
    for k in range(n):
        im.paste(ts.metatile(start + k), ((k % cols) * 16, (k // cols) * 16))
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if label:
        d = ImageDraw.Draw(im)
        for r in range(rows):
            d.text((1, r * 16 * scale), f"{start + r * cols:03X}", fill=(255, 255, 0))
    return im


def opt(args, name, default):
    return args[args.index(name) + 1] if name in args else default


if __name__ == "__main__":
    a = sys.argv[1:]
    layout, scale, cols = opt(a, "--layout", "emerald"), int(opt(a, "--scale", 2)), int(opt(a, "--cols", 8))
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--layout", "--scale", "--cols"))]
    if a[0] == "--pairs":
        sec, out, prims = pos[0], pos[1], pos[2:]
        imgs = []
        for p in prims:
            ts = Tilesets(f"{T}/primary/{p}", f"{T}/secondary/{sec}", layout)
            im = sheet(ts, ts.nm, min(96, len(ts.smeta)), 8, scale, label=False)
            ImageDraw.Draw(im).text((2, 2), p, fill=(255, 0, 0))
            imgs.append(im)
        w = sum(i.width + 8 for i in imgs)
        out_im = Image.new("RGB", (w, max(i.height for i in imgs)), (255, 255, 255))
        x = 0
        for i in imgs:
            out_im.paste(i, (x, 0))
            x += i.width + 8
        out_im.save(out)
    else:
        prim, sec, out = pos
        ts = Tilesets(f"{T}/primary/{prim}", f"{T}/secondary/{sec}", layout)
        sheet(ts, ts.nm, len(ts.smeta), cols, scale).save(out)

"""Render a pokeemerald layout (map.bin + tilesets) to PNG, the way Porymap draws it.

usage: python render.py <primary_dir> <secondary_dir> <map.bin> <width> <out.png> [--grid]
       python render.py --sheet <primary_dir> <secondary_dir> <out.png>   (metatile reference sheet)
"""
import struct
import sys
from PIL import Image, ImageDraw

def load_pals(d):
    pals = []
    for i in range(16):
        try:
            lines = open(f"{d}/palettes/{i:02d}.pal").read().split("\n")[3:19]
            pals.append([tuple(int(c) for c in l.split()) for l in lines])
        except FileNotFoundError:
            pals.append([(0, 0, 0)] * 16)
    return pals


def load_tiles(d):
    img = Image.open(f"{d}/tiles.png")
    if img.mode != "P":
        raise SystemExit(f"{d}/tiles.png is not indexed")
    w, h = img.size
    px = img.load()
    tiles = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            tiles.append([px[tx * 8 + x, ty * 8 + y] & 15 for y in range(8) for x in range(8)])
    return tiles


def load_metatiles(d):
    data = open(f"{d}/metatiles.bin", "rb").read()
    v = struct.unpack(f"<{len(data)//2}H", data)
    return [v[i:i + 8] for i in range(0, len(v), 8)]


LAYOUTS = {
    # tiles in primary, metatiles in primary, palettes in primary
    "emerald": (512, 512, 6),
    "frlg": (640, 640, 7),
    "sg": (640, 1024, 7),  # the soulgold project: 11-bit metatile ids, secondary metatiles from 0x400
}


class Tilesets:
    def __init__(self, pdir, sdir, layout="emerald"):
        self.nt, self.nm, self.np = LAYOUTS[layout]
        self.ptiles, self.stiles = load_tiles(pdir), load_tiles(sdir)
        pp, sp = load_pals(pdir), load_pals(sdir)
        self.pals = pp[:self.np] + sp[self.np:]
        self.pmeta, self.smeta = load_metatiles(pdir), load_metatiles(sdir)
        self.cache = {}

    def tile(self, tid):
        if tid < self.nt:
            return self.ptiles[tid] if tid < len(self.ptiles) else None
        tid -= self.nt
        return self.stiles[tid] if tid < len(self.stiles) else None

    def metatile(self, mid):
        if mid in self.cache:
            return self.cache[mid]
        if mid < self.nm:
            m = self.pmeta[mid] if mid < len(self.pmeta) else None
        else:
            j = mid - self.nm
            m = self.smeta[j] if j < len(self.smeta) else None
        im = Image.new("RGB", (16, 16), (255, 0, 255))
        if m:
            px = im.load()
            for layer in range(2):
                for q in range(4):
                    e = m[layer * 4 + q]
                    tid, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
                    t = self.tile(tid)
                    if t is None:
                        continue
                    ox, oy = (q % 2) * 8, (q // 2) * 8
                    for y in range(8):
                        for x in range(8):
                            c = t[(7 - y if vf else y) * 8 + (7 - x if hf else x)]
                            if c == 0 and layer == 1:
                                continue
                            px[ox + x, oy + y] = self.pals[pal][c]
        self.cache[mid] = im
        return im


def render(ts, blocks, width, grid=False):
    height = len(blocks) // width
    out = Image.new("RGB", (width * 16, height * 16))
    for i, b in enumerate(blocks):
        out.paste(ts.metatile(b & 0x3FF), ((i % width) * 16, (i // width) * 16))
    if grid:
        d = ImageDraw.Draw(out)
        for x in range(0, width, 10):
            d.line([(x * 16, 0), (x * 16, height * 16)], fill=(255, 0, 0))
        for y in range(0, height, 10):
            d.line([(0, y * 16), (width * 16, y * 16)], fill=(255, 0, 0))
    return out


def sheet(ts, out, scale=2):
    n_p, n_s = len(ts.pmeta), len(ts.smeta)
    ids = list(range(n_p)) + list(range(ts.nm, ts.nm + n_s))
    cols = 16
    rows = (len(ids) + cols - 1) // cols
    cell = 16 * scale + 22
    im = Image.new("RGB", (cols * cell, rows * cell), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for k, mid in enumerate(ids):
        x, y = (k % cols) * cell, (k // cols) * cell
        im.paste(ts.metatile(mid).resize((16 * scale, 16 * scale), Image.NEAREST), (x + 2, y + 2))
        d.text((x + 2, y + 16 * scale + 4), f"{mid:03X}", fill=(255, 255, 0))
    im.save(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--sheet":
        sheet(Tilesets(a[1], a[2]), a[3])
    else:
        data = open(a[2], "rb").read()
        blocks = struct.unpack(f"<{len(data)//2}H", data)
        render(Tilesets(a[0], a[1]), blocks, int(a[3]), "--grid" in a).save(a[4])

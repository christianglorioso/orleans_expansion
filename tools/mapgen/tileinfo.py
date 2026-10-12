"""Metatile behaviors and coarse visual signatures, used to find edge/transition tiles."""
import re
import struct

from render import Tilesets

ROOT = "."


def behavior_names():
    src = open(f"{ROOT}/include/constants/metatile_behaviors.h").read()
    body = src[src.index("{") + 1:src.index("}")]
    names = [re.sub(r"//.*", "", l).strip().rstrip(",") for l in body.splitlines()]
    names = [n.split("=")[0].strip() for n in names if n.startswith("MB_")]
    return {i: n for i, n in enumerate(names)}


def load_attrs(d):
    b = open(f"{d}/metatile_attributes.bin", "rb").read()
    return struct.unpack(f"<{len(b)//2}H", b)


def classify_px(c):
    r, g, b = c
    if b > r + 25 and b >= g - 5:
        return "W"  # water
    if r > 170 and g > 150 and b < 150 and r - b > 50:
        return "S"  # sand / dirt path
    if g > r and g > b:
        return "G"  # grass / foliage
    return "X"  # anything else (wood, rock, roof, ...)


def signature(img):
    """3x3 grid of majority classes over the 16x16 metatile (5/6/5 px bands)."""
    px = img.load()
    bands = [(0, 5), (5, 11), (11, 16)]
    sig = []
    for y0, y1 in bands:
        for x0, x1 in bands:
            counts = {}
            for y in range(y0, y1):
                for x in range(x0, x1):
                    k = classify_px(px[x, y])
                    counts[k] = counts.get(k, 0) + 1
            sig.append(max(counts, key=counts.get))
    return "".join(sig)


class TileInfo:
    def __init__(self, pdir, sdir):
        self.ts = Tilesets(pdir, sdir)
        self.names = behavior_names()
        pa, sa = load_attrs(pdir), load_attrs(sdir)
        self.attrs = {i: a for i, a in enumerate(pa)}
        self.attrs.update({512 + i: a for i, a in enumerate(sa)})

    def ids(self):
        return sorted(self.attrs)

    def behavior(self, mid):
        return self.names.get(self.attrs[mid] & 0xFF, "?")

    def layer(self, mid):
        return self.attrs[mid] >> 12

    def sig(self, mid):
        return signature(self.ts.metatile(mid))

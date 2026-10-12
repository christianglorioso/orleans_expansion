"""Which pieces of a composed tileset the built maps actually use (to see what a town's tileset can drop).

usage (from the decomp root): python tools/mapgen/usage.py <tileset> [more maps' layout dirs...]
  e.g. python tools/mapgen/usage.py orleans_harbor
Lists, per source, the mapping names no map using the tileset places.
"""
import json
import os
import struct
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def main(name):
    M = json.load(open(os.path.join(HERE, "tilesets", f"{name}.mapping.json")))["metatiles"]
    sym = json.load(open(os.path.join(HERE, "tilesets", f"{name}.json"), encoding="utf-8"))["secondary"]
    L = json.load(open("data/layouts/layouts.json"))
    used = Counter()
    maps = []
    for l in L["layouts"]:
        if l and l.get("secondary_tileset") == sym:
            maps.append(l["name"])
            raw = open(l["blockdata_filepath"], "rb").read()
            for v in struct.unpack(f"<{len(raw) // 2}H", raw):
                used[v & 0x3FF] += 1
    unused = defaultdict(list)
    for n, mid in M.items():
        if mid not in used:
            unused[n.split(":")[0]].append(n.split(":", 1)[1])
    print(name, "maps:", ", ".join(maps))
    for src, ns in sorted(unused.items()):
        print(f"  {src}: {len(ns)} unused: {' '.join(sorted(ns))}")


if __name__ == "__main__":
    main(sys.argv[1])

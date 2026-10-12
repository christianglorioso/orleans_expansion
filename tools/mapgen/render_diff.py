"""Does a tileset change leave every Orleans map looking the same?

usage (from the decomp root):
    python tools/mapgen/render_diff.py <old_primary_dir> <old_secondary_root> [map keys ...]

Renders each outdoor map's CURRENT map.bin with the current tilesets and with the old ones (the old primary directory, and
<old_secondary_root>/<secondary dir>), pixel by pixel, and prints per map the share of cells that differ, the largest colour
step and the largest step on a grass or water cell. Only meaningful when the map.bin files did not change (a tileset recompose
that keeps every metatile id), for example the decision-1 prune.
"""
import glob
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
from render import Tilesets  # noqa: E402


def dirs():
    out = {}
    for p in glob.glob(os.path.join(HERE, "tilesets", "recipes", "*.json")):
        r = json.load(open(p, encoding="utf-8"))
        out[r["symbol"]] = (r["kind"], r["dir"])
    return out


def main(args):
    old_pri, old_sec_root = args[0], args[1]
    keys = [a for a in args[2:] if not a.startswith("--")] or list(world.OUTDOOR)
    D = dirs()
    layouts = {l["id"]: l for l in json.load(open(os.path.join(world.ROOT, "data/layouts/layouts.json")))["layouts"] if l}
    for key in keys:
        spec = json.load(open(os.path.join(HERE, "maps", key + ".json"), encoding="utf-8"))
        l = layouts[spec["layout"]]
        ps, ss = D[l["primary_tileset"]][1], D[l["secondary_tileset"]][1]
        new = Tilesets(os.path.join(world.ROOT, "data/tilesets/primary", ps), os.path.join(world.ROOT, "data/tilesets/secondary", ss))
        old = Tilesets(old_pri, os.path.join(old_sec_root, ss))
        b = open(os.path.join(world.ROOT, l["blockdata_filepath"]), "rb").read()
        blocks = struct.unpack(f"<{len(b) // 2}H", b)
        cells = diff = 0
        worst = 0
        seen = {}
        for v in blocks:
            mid = v & 0x3FF
            if mid not in seen:
                a, c = new.metatile(mid).getdata(), old.metatile(mid).getdata()
                steps = [max(abs(p - q) for p, q in zip(x, y)) for x, y in zip(a, c)]
                seen[mid] = (sum(1 for s in steps if s), max(steps))
            cells += 1
            if seen[mid][0]:
                diff += 1
                worst = max(worst, seen[mid][1])
        print(f"{key:16s} {diff:5d}/{cells:5d} cells differ ({100 * diff / cells:4.1f}%), largest channel step {worst}")


if __name__ == "__main__":
    main(sys.argv[1:])

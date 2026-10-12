"""Seam bands: the cells of a map the engine draws with ANOTHER map's tileset (edges pass, decision 2).

The GBA holds only the current map's primary + secondary tileset.  A connected neighbour's strip of blocks is drawn with them,
so a neighbour block with id >= 512 reads the CURRENT map's secondary: garbage unless both maps share that secondary.
The visible margin is 7 columns W/E and 5 rows N/S (00_edges_measure.md).  The rule enforced here:

    every cell of a map within that margin of a connected edge (along the part of the edge the connection covers) must be a
    PRIMARY metatile (id < 512: grass, marsh, water, banks, cypress canopy, mud, tall grass, the Johto road/paving) when the
    neighbour has a DIFFERENT secondary tileset.  Joins between maps that share a secondary are free.
    So no buildings, magnolias, lamps, signs, props, piers, bridges, boats, blends, levees, approach paving breaks, cane,
    pepper, red earth, gully, salt or rock walls inside a strict band.

usage:
    from bands import strict_cells, check_blocks      # generators and check.py
    python tools/mapgen/bands.py [keys...] [--list]   # measure every built map (violations by piece name)
"""
import json
import os
import struct
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

ROOT = world.ROOT
DEPTH = {"N": 5, "S": 5, "W": 7, "E": 7}
SIDE = {"right": "E", "left": "W", "down": "S", "up": "N"}
OPP = {"E": "W", "W": "E", "N": "S", "S": "N"}
_cache = {}


def info():
    """key -> {w, h, secondary, layout, spec}"""
    if "info" not in _cache:
        layouts = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"] if l}
        out = {}
        for key in world.OUTDOOR:
            spec = json.load(open(os.path.join(world.MAPS, key + ".json"), encoding="utf-8"))
            l = layouts[spec["layout"]]
            out[key] = {"w": l["width"], "h": l["height"], "secondary": l["secondary_tileset"], "layout": l, "spec": spec}
        _cache["info"] = out
    return _cache["info"]


def joins():
    """[(a, side_a, b, side_b, lo_a, hi_a, lo_b, hi_b)]: each connection once; lo/hi = the covered stretch of the edge in
    each map's own coordinates (columns for N/S sides, rows for E/W)."""
    I = info()
    out = []
    for a, d, b, k, _ in world.WORLD:
        A, B = I[a], I[b]
        if d in ("right", "left"):
            lo, hi = max(0, k), min(A["h"], k + B["h"])
            out.append((a, SIDE[d], b, OPP[SIDE[d]], lo, hi, lo - k, hi - k))
        else:
            lo, hi = max(0, k), min(A["w"], k + B["w"])
            out.append((a, SIDE[d], b, OPP[SIDE[d]], lo, hi, lo - k, hi - k))
    return out


def side_cells(key, side, lo, hi):
    w, h = info()[key]["w"], info()[key]["h"]
    d = DEPTH[side]
    cells = set()
    for i in range(lo, hi):
        for k in range(d):
            if side == "N":
                cells.add((i, k))
            elif side == "S":
                cells.add((i, h - 1 - k))
            elif side == "W":
                cells.add((k, i))
            else:
                cells.add((w - 1 - k, i))
    return cells


def bands(key, strict_only=True):
    """{(x, y): neighbour key} for the band cells of `key`; strict_only: only joins whose neighbour has another secondary"""
    I = info()
    out = {}
    for a, sa, b, sb, loa, hia, lob, hib in joins():
        for me, side, lo, hi, other in ((a, sa, loa, hia, b), (b, sb, lob, hib, a)):
            if me != key:
                continue
            if strict_only and I[me]["secondary"] == I[other]["secondary"]:
                continue
            for c in side_cells(me, side, lo, hi):
                out.setdefault(c, other)
    return out


def strict_cells(key):
    """cells of `key` that may hold primary metatiles only"""
    return set(bands(key, True))


def all_band_cells(key):
    return set(bands(key, False))


def read_blocks(key):
    l = info()[key]["layout"]
    b = open(os.path.join(ROOT, l["blockdata_filepath"]), "rb").read()
    return struct.unpack(f"<{len(b) // 2}H", b)


def names_for(key):
    """metatile id -> piece name through the primary's and the map's secondary's mapping"""
    from compose import snake
    inv = {}
    for sym in ("gTileset_OrleansGeneral", info()[key]["secondary"]):
        p = os.path.join(HERE, "tilesets", snake(sym) + ".mapping.json")
        if os.path.exists(p):
            for n, v in json.load(open(p))["metatiles"].items():
                inv.setdefault(v, n)
    return inv


def check_blocks(key, blocks=None):
    """[(x, y, id, name, neighbour)] for strict-band cells that are not primary metatiles"""
    I = info()[key]
    blocks = blocks or read_blocks(key)
    inv = names_for(key)
    bad = []
    for (x, y), other in sorted(bands(key, True).items(), key=lambda kv: (kv[0][1], kv[0][0])):
        v = blocks[y * I["w"] + x] & 0x3FF
        if v >= 512:
            bad.append((x, y, v, inv.get(v, f"{v:03X}"), other))
    return bad


def main(args):
    keys = [a for a in args if not a.startswith("--")] or list(world.OUTDOOR)
    total = 0
    summary = Counter()
    for key in keys:
        bad = check_blocks(key)
        cells = len(strict_cells(key))
        total += len(bad)
        print(f"{key:16s} strict band cells {cells:5d}, not primary {len(bad):5d}")
        by = defaultdict(list)
        for x, y, v, n, o in bad:
            by[n.split("__")[0] if n.startswith("patch:ovl") else n].append((x, y))
            summary[n.split(":")[0] if ":" in n else "raw"] += 1
        if "--list" in args:
            for n, c in sorted(by.items(), key=lambda kv: -len(kv[1]))[:12]:
                print(f"      {len(c):4d} {n} e.g. {c[:3]}")
    print("total violations:", total)
    print("by source:", dict(summary.most_common(12)))


if __name__ == "__main__":
    main(sys.argv[1:])

"""Which tiles of a built map the player can walk on (no collision, not water): used to place story triggers.

usage (from the decomp root): python tools/mapgen/land.py LAYOUT_ID [y ...]   prints a land map, or the land x's on rows y
"""
import json
import re
import struct
import sys

WATER = {"MB_POND_WATER", "MB_INTERIOR_DEEP_WATER", "MB_DEEP_WATER", "MB_WATERFALL", "MB_SOOTOPOLIS_DEEP_WATER",
         "MB_OCEAN_WATER", "MB_NO_SURFACING", "MB_SEAWEED", "MB_SEAWEED_NO_SURFACING", "MB_SHALLOW_WATER_NO_SURF",
         "MB_EASTWARD_CURRENT", "MB_WESTWARD_CURRENT", "MB_NORTHWARD_CURRENT", "MB_SOUTHWARD_CURRENT"}


def behaviors():
    src = open("include/constants/metatile_behaviors.h").read()
    names = re.findall(r"^\s*(MB_\w+)\s*[,=]", src, re.M)
    return {i: n for i, n in enumerate(names)}


def tileset_dir(symbol):
    for line in open("src/data/tilesets/headers.h", encoding="utf-8"):
        pass
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", symbol.replace("gTileset_", "")).lower()
    for kind in ("primary", "secondary"):
        p = f"data/tilesets/{kind}/{snake}"
        try:
            open(f"{p}/metatile_attributes.bin", "rb").close()
            return p
        except FileNotFoundError:
            continue
    raise SystemExit(f"no tileset dir for {symbol}")


def land(layout_id):
    L = {l["id"]: l for l in json.load(open("data/layouts/layouts.json"))["layouts"] if l.get("id")}[layout_id]
    raw = open(L["blockdata_filepath"], "rb").read()
    blocks = struct.unpack(f"<{len(raw) // 2}H", raw)
    W = L["width"]
    attrs = []
    for sym in (L["primary_tileset"], L["secondary_tileset"]):
        a = open(f"{tileset_dir(sym)}/metatile_attributes.bin", "rb").read()
        part = list(struct.unpack(f"<{len(a) // 2}H", a))
        attrs += (part + [0] * 512)[:512]
    names = behaviors()
    rows = []
    for y in range(len(blocks) // W):
        row = []
        for x in range(W):
            b = blocks[y * W + x]
            beh = names.get(attrs[b & 0x3FF] & 0xFF, "")
            row.append(not (b >> 10) & 3 and beh not in WATER)
        rows.append(row)
    return rows


if __name__ == "__main__":
    g = land(sys.argv[1])
    if len(sys.argv) > 2:
        for y in map(int, sys.argv[2:]):
            print(y, [x for x, ok in enumerate(g[y]) if ok])
    else:
        for y, row in enumerate(g):
            print(f"{y:2d} " + "".join("." if ok else "#" for ok in row))

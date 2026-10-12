"""Which HnS Johto metatiles does gTileset_OrleansGeneral keep? (edges pass, decision 1: prune the primary)

usage (from the decomp root):  python tools/mapgen/primary_keep.py [--write]

keep = the primary ids (< 512) any layout using gTileset_OrleansGeneral places (read from the map.bin files, so the list is
what the maps ARE, not what a generator might do) + every 3-digit hex piece id the tileset configs and generators name
(tilesets/*.json, tools/mapgen/*.py: path/paving/fence autotile pieces, signposts, shrubs ... so a rebuild never asks for
a piece that was pruned) + EXTRA (pieces the engine code needs, see ENGINE below).

--write stores tilesets/primary_keep.json, which tilesets/recipes/orleans_general.json ("keep_file") reads.
build.py refuses (warns, draws nothing) when a spec names a primary hex id outside this list, so a missing piece is found
at build time, not in the game.
"""
import glob
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JOHTO_END = 0x1DF
# engine code that names primary ids through include/constants/metatile_labels.h gets its own pieces from
# gen_metatile_labels.py (shared terrain pieces, not Johto ones), so nothing Johto is needed for it
EXTRA = []
# three-digit strings that are NOT ids of this primary: the Emerald general mart/lamp pieces make_town_tilesets cuts out of
# "vgen" and the building primary's floor pieces interior_rooms_world uses (jb:)
NOT_OURS = {0x028, 0x029, 0x02B, 0x030, 0x031, 0x032, 0x033, 0x038, 0x039, 0x03B, 0x040, 0x041, 0x042, 0x043, 0x061,
            0x0C3, 0x0C4, 0x0C5, 0x0C8, 0x0C9, 0x0CB, 0x0CC, 0x0CD}

HEX = re.compile(r"""["']([0-9A-F]{3})["']""")
# files whose three-digit strings are not primary ids
SKIP_JSON = ("general_fortree.json",)


def placed():
    """{id: [layouts]} of primary ids < 512 placed in the maps"""
    out = {}
    for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"]:
        if not l or l.get("primary_tileset") != "gTileset_OrleansGeneral":
            continue
        p = os.path.join(ROOT, l["blockdata_filepath"])
        if not os.path.exists(p):
            continue
        b = open(p, "rb").read()
        if l["width"] * l["height"] < 4:   # 1x1 stub layouts (stripped Hoenn rooms): always metatile 0
            continue
        for v in struct.unpack(f"<{len(b) // 2}H", b):
            if (v & 0x3FF) < 512:
                out.setdefault(v & 0x3FF, set()).add(l["id"])
    return out


def named():
    out = {}
    files = [p for p in glob.glob(os.path.join(HERE, "tilesets", "*.json"))
             if not p.endswith(("mapping.json", "blends.json")) and os.path.basename(p) not in SKIP_JSON]
    files += glob.glob(os.path.join(HERE, "*.py"))
    for p in files:
        if os.path.basename(p) in ("primary_keep.py", "edges_measure.py", "gba_view.py"):
            continue
        for m in HEX.finditer(open(p, encoding="utf-8", errors="replace").read()):
            v = int(m.group(1), 16)
            if v <= JOHTO_END and v not in NOT_OURS:
                out.setdefault(v, set()).add(os.path.basename(p))
    return out


def main(args):
    pl, nm = placed(), named()
    keep = sorted(set(pl) | set(nm) | set(EXTRA))
    print(f"placed in maps: {len(pl)} ids; named in configs/generators: {len(nm)}; union {len(keep)} of {JOHTO_END + 1}")
    only_named = sorted(set(nm) - set(pl))
    print("named but not placed:", " ".join(f"{v:03X}" for v in only_named))
    if "--write" in args:
        data = {"_comment": "Johto metatile ids gTileset_OrleansGeneral keeps (primary_keep.py).",
                "johto": [f"{v:03X}" for v in keep]}
        with open(os.path.join(HERE, "tilesets", "primary_keep.json"), "w") as f:
            json.dump(data, f, indent=0)
        print("wrote tilesets/primary_keep.json")


if __name__ == "__main__":
    main(sys.argv[1:])

"""The Surf-barrier water props (art: sources/orleans_custom/make_water_barriers.py -> tilesets/water_props/, commit 577fe08f4f) as an overlay
source `wpr` plus a prefab per piece on the tilesets of the water maps.

usage (from the decomp root):
    python tools/mapgen/water_props_tileset.py            writes sources/orleans_custom/water_props_sheet.png and patches every water
                                                          tileset's recipe + config in place (idempotent)
Also called as apply(r, c) from landmarks_tileset.apply (the route family) and make_town_tilesets.make (the town variants), so a
regenerated tileset keeps the pieces.  Demand-driven tilesets pay tiles only on a map that places a piece.

Prefabs (all blocking except the cattails' overhead top cell; every cell an overlay on open water, drawn over the ground it stands on):
    wp_knees_a, wp_knees_b   1x1 cypress-knee clusters (bayou style)
    wp_cattails              1x2 cattail clump (bayou style; the top cell is overhead and passable)
    wp_rock_a, wp_rock_b     1x1 rocks awash (coast style)
    wp_rock_ledge            2x1 low ledge of stones (coast style)
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PROPS = os.path.join(HERE, "tilesets", "water_props")
SHEET = os.path.join(HERE, "sources", "orleans_custom", "water_props_sheet.png")
KEY = (255, 0, 255)
# sheet column -> cell file stem
CELLS = ["wp_knees_1a", "wp_knees_1b", "wp_cattails_00", "wp_cattails_01", "wp_rock_1a", "wp_rock_1b", "wp_rock_ledge_00", "wp_rock_ledge_10"]
PREFABS = {
    "wp_knees_a": ([[0]], []),
    "wp_knees_b": ([[1]], []),
    "wp_cattails": ([[2], [3]], [[0, 0]]),
    "wp_rock_a": ([[4]], []),
    "wp_rock_b": ([[5]], []),
    "wp_rock_ledge": ([[6, 7]], []),
}
# the tilesets of the water-style maps (storms_edge, camp_cocodrie, lands_end, oldest_shrine, routes 8, 10, 11, 18-22): crescent is left out (510/512 tiles)
WATER_TILESETS = ["orleans_port", "orleans_camp", "orleans_harbor", "orleans_route", "orleans_route_b", "orleans_gulf", "orleans_offshore"]
BAYOU_PIECES = ("wp_knees_a", "wp_knees_b", "wp_cattails")
COAST_PIECES = ("wp_rock_a", "wp_rock_b", "wp_rock_ledge")


def make_sheet():
    im = Image.new("RGB", (16 * len(CELLS), 16), KEY)
    for i, stem in enumerate(CELLS):
        c = Image.open(os.path.join(PROPS, stem + ".png")).convert("RGBA")
        bg = Image.new("RGBA", c.size, KEY + (255,))
        bg.alpha_composite(c)
        im.paste(bg.convert("RGB"), (i * 16, 0))
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    im.save(SHEET)
    return SHEET


def source():
    return {"name": "wpr", "type": "image", "image": "tools/mapgen/sources/orleans_custom/water_props_sheet.png",
            "transparent": [list(KEY)], "overlay_only": True,
            "_comment": "Surf-barrier water props (own art, make_water_barriers.py), overlays on open water.",
            "metatiles": [{"id": f"{i}_0", "bottom": [i, 0]} for i in range(len(CELLS))]}


def prefabs():
    out = {}
    for name, (rows, passable) in PREFABS.items():
        out[name] = {"_comment": "Surf-barrier prop (water_props_tileset.py).", "door": None, "passable": passable,
                     "rows": [[{"overlay": f"wpr:{i}_0"} for i in row] for row in rows], "_wpr": True}
    return out


def apply(r, c):
    """add the source to recipe r and the prefabs to config c (idempotent); True when it did"""
    if not os.path.exists(SHEET):
        make_sheet()
    r["sources"] = [s for s in r["sources"] if s["name"] != "wpr"]
    r["sources"].append(source())
    c["prefabs"] = {k: v for k, v in c["prefabs"].items() if not v.get("_wpr")}
    c["prefabs"].update(prefabs())
    return True


def patch_all():
    make_sheet()
    for name in WATER_TILESETS:
        cp, rp = os.path.join(HERE, "tilesets", name + ".json"), os.path.join(HERE, "tilesets", "recipes", name + ".json")
        if not (os.path.exists(cp) and os.path.exists(rp)):
            continue
        c, r = json.load(open(cp, encoding="utf-8")), json.load(open(rp, encoding="utf-8"))
        apply(r, c)
        for path, obj in ((cp, c), (rp, r)):
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
                f.write("\n")
        print("water props on", name)


if __name__ == "__main__":
    patch_all()

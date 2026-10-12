"""Lutin's Hollow's own pieces on top of the orleans_hollow tileset variant (make_town_tilesets.py calls apply() for
VARIANTS["orleans_hollow"]["addon"]). The variant stays demand-driven (compose keeps only what hollow.py places) with
the v2 palette packer (never v2_backdrop). Same hook as camp_tileset.py.

    own art     everything in sources/orleans_custom/hollow.png (drawn by make_hollow_art.py, indexed by hollow.json):
                every piece in hollow.json becomes a prefab of the same name; its cells are overlays (drawn over the
                grass beneath), its door cell gets a door behaviour, its `passable` cells are walkable (ferns,
                flowers, mushrooms, the middle of a fairy ring); everything else in a piece blocks.
    stand-ins   every piece in WANTED that the art does NOT define yet gets a stand-in prefab of the same footprint
                (a Shady cabin or the Pokemon Center / barn shifted so the door lands where the real one will, a
                magnolia, a round shrub, roses ...), so hollow.py's layout never changes when the art lands.

WANTED is the single list of pieces (hollow.py reads it too): name -> (w, h, door cell or None, walkable cells, kind).
The art request (tools/mapgen/art_requests/lutins_hollow.md) repeats it with the drawing notes.
"""
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART_DIR = "tools/mapgen/sources/orleans_custom/"
DOOR = "MB_NON_ANIMATED_DOOR"
KEY = (255, 0, 255)


def _all(w, h):
    return [(i, j) for j in range(h) for i in range(w)]


# name -> (w, h, door, walkable cells, kind). Doors are on the bottom row; the cell below is plain ground.
WANTED = {
    # buildings
    "gym_arbour": (7, 5, (3, 4), [], "gym"),
    "hollow_tree": (7, 6, (3, 5), [], "center"),
    "cottage_a": (5, 4, (2, 3), [], "cottage"),
    "cottage_b": (5, 4, (2, 3), [], "cottage"),
    "herbalist": (6, 4, (2, 3), [], "cottage"),
    # moss-draped ring trees (all blocking)
    "tree_a": (3, 3, None, [], "tree"),
    "tree_b": (3, 3, None, [], "tree"),
    "tree_c": (3, 3, None, [], "tree"),
    "tree_s": (2, 2, None, [], "tree_s"),
    "thicket_a": (1, 1, None, [], "shrub"),
    "thicket_b": (1, 1, None, [], "shrub"),
    # understory: blocking
    "bush_a": (1, 1, None, [], "shrub"),
    "bush_b": (1, 1, None, [], "shrub"),
    "mossy_log": (2, 1, None, [], "log"),
    # understory: walkable ground cover
    "fern_a": (1, 1, None, [(0, 0)], "cover"),
    "fern_b": (1, 1, None, [(0, 0)], "cover"),
    "fern_c": (1, 1, None, [(0, 0)], "cover"),
    "moss_mound": (1, 1, None, [(0, 0)], "cover"),
    "bloom_pink": (1, 1, None, [(0, 0)], "cover"),
    "bloom_violet": (1, 1, None, [(0, 0)], "cover"),
    "bloom_white": (1, 1, None, [(0, 0)], "cover"),
    "bloom_gold": (1, 1, None, [(0, 0)], "cover"),
    "glowbell": (1, 1, None, [(0, 0)], "cover"),
    "toadstool_red": (1, 1, None, [(0, 0)], "cover"),
    "toadstool_pale": (1, 1, None, [(0, 0)], "cover"),
    # fairy details
    "fairy_ring": (3, 3, None, _all(3, 3), "ring"),
    "pool": (2, 2, None, [], "pool"),
    "pepper_bed": (3, 2, None, [], "pepper"),
    "riddle_stone": (1, 2, None, [], "stone"),
}

# the stand-ins' tiles (primary ids): a round shrub, roses
SHRUB, ROSES, SIGNPOST = "00E", "005", "003"


def art_index():
    p = os.path.join(HERE, "sources", "orleans_custom", "hollow.json")
    return json.load(open(p, encoding="utf-8"))["pieces"] if os.path.exists(p) else {}


def piece_rows(m, sheet):
    """Prefab rows for one art piece: overlay cells (fully transparent cells are None), the door cell gets the door
    behaviour, passable cells are 'walk' overlays (the art decides the behaviour)."""
    doors = {tuple(d) for d in m["doors"]}
    walk = {tuple(w) for w in m["passable"]}
    rows = []
    for j in range(m["h"]):
        row = []
        for i in range(m["w"]):
            cx, cy = m["x"] + i, m["y"] + j
            cell = sheet.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
            if all(p[:3] == KEY for p in cell.getdata()):
                row.append(None)
                continue
            o = {"overlay": f"hollow:{cx}_{cy}"}
            if (i, j) in doors:
                o["behavior"] = DOOR
            if (i, j) in walk or (i, j) in doors:
                o["walk"] = True
            row.append(o)
        rows.append(row)
    return rows


def _shifted(rows, w, h, dx, bottom_align=True):
    """`rows` placed in a w x h footprint, dx columns right, bottom-aligned (rows that don't fit are cropped)."""
    sh, sw = len(rows), len(rows[0])
    dy = h - sh
    out = []
    for j in range(h):
        row = []
        for i in range(w):
            sj, si = j - dy, i - dx
            row.append(rows[sj][si] if 0 <= sj < sh and 0 <= si < sw else None)
        out.append(row)
    return out


def stand_in(name, spec, P):
    """A same-footprint stand-in prefab for a piece the art agent hasn't delivered."""
    w, h, door, walk, kind = spec
    passable = [list(c) for c in walk]
    rows = None
    if kind == "gym":      # the Moomoo barn (6x5, door col 1) stretched to 7 wide so the door is in column 3
        barn = P["barn"]["rows"]
        cols = [0, 2, 3, 1, 2, 4, 5]
        rows = [[barn[j][c] for c in cols] for j in range(5)]
    elif kind == "center":  # the Pokemon Center (4x4, door col 1), door column 3, bottom aligned
        rows = _shifted(P["pokecenter"]["rows"], w, h, door[0] - 1)
    elif kind == "cottage":  # the Shady cabin (3x4, door col 1)
        rows = _shifted(P["cabin"]["rows"], w, h, door[0] - 1)
    elif kind == "tree" and "magnolia" in P:
        rows = _shifted(P["magnolia"]["rows"], w, h, 0)
    elif kind == "tree_s" and "magnolia" in P:
        rows = _shifted(P["magnolia"]["rows"][1:], w, h, 0)
    elif kind == "shrub":
        rows = [[SHRUB]]
    elif kind == "cover":
        rows = [[SHRUB if name.startswith(("fern", "moss")) else ROSES]]
    elif kind == "log":
        rows = [[SHRUB, SHRUB]]
    elif kind == "ring":
        rows = [[ROSES if (i, j) != (1, 1) else None for i in range(3)] for j in range(3)]
    elif kind == "pool":
        rows = [[SHRUB, SHRUB], [SHRUB, SHRUB]]
    elif kind == "pepper":
        rows = [[SHRUB] * 3, [SHRUB] * 3]
    elif kind == "stone":
        rows = [[None], [SIGNPOST]]
    if rows is None:
        return None
    return {"_comment": f"STAND-IN for the {name} art ({w}x{h}).", "rows": rows,
            "door": list(door) if door else None, "passable": passable, "stand_in": True}


def apply(r, c):
    idx = art_index()
    P = c["prefabs"]
    if idx:
        sheet = Image.open(os.path.join(HERE, "sources", "orleans_custom", "hollow.png")).convert("RGB")
        cells = sorted({(m["x"] + i, m["y"] + j) for m in idx.values() for j in range(m["h"]) for i in range(m["w"])},
                       key=lambda t: (t[1], t[0]))
        r["sources"].append({"name": "hollow", "type": "image", "image": ART_DIR + "hollow.png",
                             "transparent": [list(KEY)], "overlay_only": True,
                             "_comment": "Lutin's Hollow's own art (make_hollow_art.py): overlays.",
                             "metatiles": [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]})
        for name, m in idx.items():
            d = [list(x) for x in m["doors"]]
            P[name] = {"_comment": m.get("comment", "Lutin's Hollow own art."), "rows": piece_rows(m, sheet),
                       "door": d[0] if len(d) == 1 else (d or None),
                       "passable": [list(x) for x in m["passable"]]}
    P["sign"] = {"_comment": "Wooden signpost (primary 003).", "rows": [["003"]]}
    for name, spec in WANTED.items():
        if name in idx:
            continue
        s = stand_in(name, spec, P)
        if s:
            P[name] = s

"""Camp Cocodrie's own pieces on top of the orleans_camp tileset variant (make_town_tilesets.py calls apply() for
VARIANTS["orleans_camp"]["addon"]). The variant stays demand-driven (compose keeps only what camp.py places) with the
v2 palette packer (never v2_backdrop).

Adds:
    own art   everything in sources/orleans_custom/camp.png (drawn by make_camp_art.py, indexed by camp.json): the
              boardwalk cells (bw_<h|v>_<NSWE>), the stilt cabins, and whatever buildings and props the art
              agent has delivered (nurse, bait, smokehouse, porch, chimney, pot, pen fences, gators, okra, fish
              racks, skiffs, trap line ...). Every piece in camp.json becomes a prefab of the same name: its cells
              are overlays (drawn over whatever terrain lies beneath), its door cell gets a door behaviour, its
              walk cells are walkable ground even over water ("walk": the art decides the behaviour).
    cookhouse the Moomoo barn lengthened (middle bays and a second pair of roof rows repeated): the gym, 10x7
    sign      the primary's wooden signpost
    stand-ins every piece the art agent has NOT delivered yet has a stand-in prefab of the same footprint (a cabin
              shifted so its door lines up, crates, the primary's fence, a shrub, a waterlog), so camp.py's layout
              never changes when the art lands: once make_camp_art.py defines the name, camp.json carries it and the
              real prefab replaces the stand-in on the next run. Pieces with no sensible stand-in (chimney, lantern,
              knees, trap line, gator eyes ...) simply don't exist yet: camp.py asks `have(name)` before placing.
"""
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART_DIR = "tools/mapgen/sources/orleans_custom/"
DOOR = "MB_NON_ANIMATED_DOOR"
KEY = (255, 0, 255)

# pieces camp.py wants, with the footprint the art request promised: name -> (w, h, door cell or None, walk cells)
WANTED = {
    "nurse": (5, 5, (2, 3), [(2, 4)]), "bait": (5, 5, (1, 3), [(1, 4)]),
    "smokehouse": (4, 5, (1, 3), [(1, 4)]), "porch": (7, 5, (3, 3), [(3, 4)]),
}
# stand-in art for the buildings: the cabin whose door column is 1, shifted so the door lands where the real one will
STAND_IN = {"nurse": "cabin_a", "bait": "cabin_a", "smokehouse": "cabin_b", "porch": "cabin_a"}
FENCE_STAND_IN = {"pen_h": "0ED", "pen_v": "0F4", "pen_nw": "0EC", "pen_ne": "0EE", "pen_sw": "0FC", "pen_se": "136",
                  "pen_gate": "0FD"}


def art_index():
    p = os.path.join(HERE, "sources", "orleans_custom", "camp.json")
    return json.load(open(p, encoding="utf-8"))["pieces"] if os.path.exists(p) else {}


def piece_rows(name, m, sheet):
    """Prefab rows for one art piece: overlay cells (fully transparent cells are None), the door cell gets the door
    behaviour, walk cells are 'walk' overlays."""
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
            o = {"overlay": f"camp:{cx}_{cy}"}
            if (i, j) in doors:
                o["behavior"] = DOOR
            if (i, j) in walk or (i, j) in doors:
                o["walk"] = True
            row.append(o)
        rows.append(row)
    return rows


def apply(r, c):
    idx = art_index()
    P = c["prefabs"]
    if idx:
        sheet = Image.open(os.path.join(HERE, "sources", "orleans_custom", "camp.png")).convert("RGB")
        cells = sorted({(m["x"] + i, m["y"] + j) for m in idx.values() for j in range(m["h"]) for i in range(m["w"])},
                       key=lambda t: (t[1], t[0]))
        r["sources"].append({"name": "camp", "type": "image", "image": ART_DIR + "camp.png",
                             "transparent": [list(KEY)], "overlay_only": True,
                             "_comment": "Camp Cocodrie's own art (make_camp_art.py): overlays.",
                             "metatiles": [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]})
        for name, m in idx.items():
            rows = piece_rows(name, m, sheet)
            d = [list(x) for x in m["doors"]]
            P[name] = {"_comment": m.get("comment", "Camp Cocodrie own art."), "rows": rows,
                       "door": d[0] if len(d) == 1 else (d or None),
                       "passable": [list(x) for x in m["passable"]]}
            if name.startswith(("gator", "trapline", "buoy", "knees", "skiff", "pirogue", "mooring")):
                P[name]["elev"] = 3
    # ---- the cookhouse: the Moomoo barn lengthened (cols 2-3 repeated twice) and its roof deepened (rows 1-2 twice)
    barn = P["barn"]["rows"]
    cols = [0, 1, 2, 3, 2, 3, 2, 3, 4, 5]
    rws = [0, 1, 2, 1, 2, 3, 4]
    P["cookhouse"] = {"_comment": "The Brothers' cookhouse (gym): the Moomoo barn lengthened to 10x7.",
                      "rows": [[barn[j][i] for i in cols] for j in rws], "door": [1, 6]}
    P["sign"] = {"_comment": "Wooden signpost (primary 003).", "rows": [["003"]]}
    # ---- stand-ins for what the art agent hasn't delivered yet
    for name, (w, h, door, walk) in WANTED.items():
        if name in idx:
            continue
        src = idx.get(STAND_IN[name])
        if not src:
            continue
        sheet = Image.open(os.path.join(HERE, "sources", "orleans_custom", "camp.png")).convert("RGB")
        base = piece_rows(STAND_IN[name], src, sheet)
        dx = door[0] - src["doors"][0][0]
        rows = [[(base[j][i - dx] if 0 <= i - dx < len(base[0]) and j < len(base) else None) for i in range(w)]
                for j in range(h)]
        P[name] = {"_comment": f"STAND-IN for the {name} art ({w}x{h}): {STAND_IN[name]} shifted to the door column.",
                   "rows": rows, "door": list(door), "passable": [list(x) for x in walk], "stand_in": True}
    crates = {"overlay": "props:crates"}
    for name, (w, h) in {"fishrack": (2, 2), "netrack": (2, 2), "pot": (2, 2), "woodpile": (2, 1)}.items():
        if name not in idx:
            P[name] = {"_comment": f"STAND-IN for the {name} art ({w}x{h}): crates.", "stand_in": True,
                       "rows": [[dict(crates) for _ in range(w)] for _ in range(h)]}
    for name, tile in FENCE_STAND_IN.items():
        if name not in idx:
            P[name] = {"_comment": f"STAND-IN for the {name} art: the primary's fence.", "rows": [[tile]],
                       "stand_in": True}
    if "okra" not in idx:
        P["okra"] = {"_comment": "STAND-IN for the okra art: a round shrub (primary 00E).", "rows": [["00E"]],
                     "stand_in": True}
    if "okra_b" not in idx:
        P["okra_b"] = {"_comment": "STAND-IN for the okra_b art: roses (primary 005).", "rows": [["005"]], "stand_in": True}
    wl = P.get("waterlog")
    for name, w in (("skiff", 3), ("pirogue", 2)):
        if name not in idx and wl:
            P[name] = {"_comment": f"STAND-IN for the {name} art: a waterlog.", "stand_in": True,
                       "rows": [list(wl["rows"][0]) + [None] * (w - 2)], "on_patch": wl.get("on_patch"), "elev": 1}
    for name in ("gator", "gator_b"):
        if name not in idx and "log" in P:
            P[name] = {"_comment": f"STAND-IN for the {name} art: a log.", "rows": [list(P["log"]["rows"][0])],
                       "stand_in": True}

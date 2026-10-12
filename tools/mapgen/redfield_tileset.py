"""Redfield's own pieces on top of the orleans_capital tileset variant (make_town_tilesets.py calls apply() for
VARIANTS["orleans_capital"]["addon"]; despite the name the set is Redfield's alone). The variant stays demand-driven
(compose keeps only what redfield.py places) with the v2 palette packer (never v2_backdrop).

Terrain characters redfield.py draws with (added to the variant's config):
    d   dry ground: the town's ground. Stand-in: Ekat's grass (until the dry set is delivered). With the dry set: its
        plain dry cells, and a dual-grid transition set against grass ('.' and the levee ground 'B'), like the marsh set.
    G   the sugarcane field (encounter grass). Stand-in: Ekat's tall grass. With the dry set: its cane rows tile
        (behaviour tall grass).
    q   pepper rows (plain, no encounters). Stand-in: the Grand Oak pepper bed (red-flower placeholder over grass).
    :=  road / plaza paving (the Johto dirt path autotile). With the dry set: its road set replaces the path tiles.

Art, in two index files next to the sheets in sources/orleans_custom (see art_requests/redfield.md):
    redfield.json    (make_redfield_art.py -> redfield.png) every Redfield piece: {"pieces": {name: {x, y, w, h, doors,
                     passable, empty, comment}}}, x/y the piece's top-left cell in the sheet.
    dry_country.json (the shared dry-country set -> its png) {"png": "dry_country.png", "terrain": {...cell names...},
                     "pieces": {...as above...}}; terrain keys: dry (a list of plain variation cells, the first the
                     plain one), dry_grass, cane, pepper, N S W E inNW inNE inSW inSE landSE landSW landNE landNW
                     sTLBR sTRBL (the dry-on-grass dual-grid set: "N" = patch edge on the north side ... exactly
                     Ekat's marsh set), road_C road_N road_S road_W road_E road_NW road_NE road_SW road_SE road_iNW
                     road_iNE road_iSW road_iSE (the cell-based path set on dry ground). Terrain cells are opaque,
                     pieces are overlays (magenta (255,0,255) = clear). Cells are [x, y] in 16 px units.
Every piece in an index becomes a prefab of the same name: its cells are overlays (drawn over whatever terrain lies
beneath), its door cell gets a door behaviour, its walk cells are walkable ("walk": the art decides the behaviour).

Stand-ins: every piece redfield.py asks for that the art agent has NOT delivered yet has a prefab of the same name
and footprint (WANTED below: the contract with the art request), built from what the tileset already has, so the
layout never changes when the art lands: once an index defines the name, its real prefab replaces the stand-in on the
next run.
"""
import copy
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART_DIR = os.environ.get("REDFIELD_ART_DIR", os.path.join(HERE, "sources", "orleans_custom"))
ART_REL = "tools/mapgen/sources/orleans_custom/"
DOOR = "MB_NON_ANIMATED_DOOR"
KEY = (255, 0, 255)

# every piece redfield.py places that the art request promised: name -> (w, h, door cell or None, walkable cells)
SUNDIAL_WALK = [(i, j) for j in range(6) for i in range(8) if not (3 <= i <= 4 and 0 <= j <= 3)]
WANTED = {
    "sugar_mill": (7, 8, (3, 7), []),
    "ritas_office": (5, 4, (1, 3), []),
    "shotgun_a": (3, 6, (1, 5), []), "shotgun_b": (3, 6, (1, 5), []),
    "shotgun_c": (3, 6, (1, 5), []), "shotgun_d": (3, 6, (1, 5), []),
    "bottling_works": (9, 6, (2, 5), []),
    "great_sundial": (8, 6, None, SUNDIAL_WALK),
    "rail_h": (1, 1, None, [(0, 0)]), "rail_cross": (1, 1, None, [(0, 0)]), "rail_end": (1, 1, None, []),
    "cane_truck": (3, 2, None, []),
    "yard_h": (1, 1, None, []), "yard_v": (1, 1, None, []), "yard_nw": (1, 1, None, []), "yard_ne": (1, 1, None, []),
    "yard_sw": (1, 1, None, []), "yard_se": (1, 1, None, []), "yard_gate_l": (1, 1, None, []),
    "yard_gate_r": (1, 1, None, []),
    "sundial": (2, 2, None, []),
    "mirror_ne": (1, 2, None, []), "mirror_nw": (1, 2, None, []), "mirror_se": (1, 2, None, []),
    "mirror_sw": (1, 2, None, []),
    "cane_pile": (2, 2, None, []), "cane_pile_b": (2, 1, None, []),
    "sauce_vat": (2, 2, None, []), "bottle_crates": (2, 1, None, []),
    "ferry": (3, 2, None, []),
    "field_tree": (2, 3, None, []), "field_tree_l": (3, 3, None, []),
}
# stand-in art: the primary's fence tiles for the mill-yard fence (the pen fence of Camp Cocodrie)
FENCE_STAND_IN = {"yard_h": "0ED", "yard_v": "0F4", "yard_nw": "0EC", "yard_ne": "0EE", "yard_sw": "0FC",
                  "yard_se": "136", "yard_gate_l": "0F4", "yard_gate_r": "0F4"}
PEPPER_COLORS = [[120, 160, 104], [104, 144, 96], [110, 146, 100], [136, 176, 128], [140, 178, 131], [122, 172, 130],
                 [149, 190, 157], [96, 128, 88]]
# the dry set's autotile keys (Ekat's corner-set names)
CORNER_KEYS = ["N", "S", "W", "E", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW", "landNE", "landNW", "sTLBR",
               "sTRBL"]
ROAD_KEYS = {"C": "C", "N": "N", "S": "S", "W": "W", "E": "E", "NW": "NW", "NE": "NE", "SW": "SW", "SE": "SE",
             "iNW": "iNW", "iNE": "iNE", "iSW": "iSW", "iSE": "iSE"}


def load(name):
    p = os.path.join(ART_DIR, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def piece_rows(src, m, sheet):
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
            o = {"overlay": f"{src}:{cx}_{cy}"}
            if (i, j) in doors:
                o["behavior"] = DOOR
            if (i, j) in walk or (i, j) in doors:
                o["walk"] = True
            row.append(o)
        rows.append(row)
    return rows


def image_source(name, png, cells, overlay=True, comment="", behaviors=None):
    behaviors = behaviors or {}
    mts = []
    for x, y in cells:
        m = {"id": f"{x}_{y}", "bottom": [x, y]}
        if (x, y) in behaviors:
            m["behavior"] = behaviors[(x, y)]
        mts.append(m)
    s = {"name": name, "type": "image", "image": ART_REL + png, "transparent": [list(KEY)], "metatiles": mts,
         "_comment": comment}
    if overlay:
        s["overlay_only"] = True
    return s


def add_pieces(r, c, src, png, idx, comment):
    """Own-art overlay pieces of one index: a source for their cells and a prefab per piece."""
    pieces = idx.get("pieces", {})
    if not pieces:
        return
    sheet = Image.open(os.path.join(ART_DIR, png)).convert("RGB")
    cells = sorted({(m["x"] + i, m["y"] + j) for m in pieces.values() for j in range(m["h"]) for i in range(m["w"])},
                   key=lambda t: (t[1], t[0]))
    r["sources"].append(image_source(src, png, cells, True, comment))
    for name, m in pieces.items():
        d = [list(x) for x in m["doors"]]
        c["prefabs"][name] = {"_comment": m.get("comment", comment), "rows": piece_rows(src, m, sheet),
                              "door": d[0] if len(d) == 1 else (d or None),
                              "passable": [list(x) for x in m["passable"]]}


def dry_terrain(r, c, dry):
    """The shared dry-country set's terrain: dry ground (with its transition set against grass), dry grass, cane rows,
    pepper rows and the dirt road set, all opaque metatiles of one source."""
    t = dry["terrain"]
    png = dry.get("png", "dry_country.png")
    names, cells, behaviors = {}, [], {}

    def reg(key, cell, behavior=None):
        cell = tuple(cell)
        names[key] = f"dry:{cell[0]}_{cell[1]}"
        if cell not in cells:
            cells.append(cell)
        if behavior:
            behaviors[cell] = behavior
    plain = t["dry"] if isinstance(t["dry"][0], list) else [t["dry"]]
    for k, cell in enumerate(plain):
        reg(f"dry{k}", cell)
    for key in ("dry_grass", "pepper"):
        if key in t:
            reg(key, t[key])
    if "cane" in t:
        reg("cane", t["cane"], "MB_TALL_GRASS")
    for key in CORNER_KEYS:
        if key in t:
            reg(key, t[key])
    for key in ROAD_KEYS:
        if "road_" + key in t:
            reg("road_" + key, t["road_" + key])
    r["sources"].append(image_source("dry", png, cells, overlay=False, comment="The shared dry-country terrain.",
                                     behaviors=behaviors))
    T = c["terrain"]
    T["d"]["tile"] = names["dry0"]
    if "dry_grass" in names:
        T["g"] = {"name": "dry grass", "tile": names["dry_grass"], "elev": 3}
    if "cane" in names:
        T["G"] = {"name": "sugarcane field (wild encounters)", "tile": names["cane"], "elev": 3}
    if "pepper" in names:
        T["q"]["tile"] = names["pepper"]
    if all(k in names for k in CORNER_KEYS):  # the dry-on-grass dual-grid set: a corner autotile like the marsh
        # "connects" is everything that is dry underfoot: dry ground, dry grass, road, plaza paving, cane and pepper rows
        # (the road, cane and pepper tiles are drawn on dry ground, so a dry piece beside them must not show grass)
        a = {"kind": "corners", "connects": "dg:=Gq", "apply_on": ".d", "elev": 3,
             "C": [names[f"dry{k}"] for k in range(len(plain))]}
        a.update({k: names[k] for k in CORNER_KEYS})
        c["autotile"]["dry"] = a
    if "road_C" in names:  # the road set on dry ground replaces the Johto path pieces
        for key in ROAD_KEYS:
            if "road_" + key in names:
                c["autotile"]["path"][key] = names["road_" + key]


def apply(r, c):
    # ---- terrain: dry ground and pepper rows (stand-ins until the dry set is delivered)
    T = c["terrain"]
    T["d"] = {"name": "dry ground (stand-in: grass)", "tile": "ekat:grass", "elev": 3}
    T["q"] = {"name": "pepper rows (stand-in: the Grand Oak bed)", "tile": "patch:peppers", "elev": 3}
    r["patches"].append({"id": "peppers", "reseat": "johto:004", "base": "ekat:grass", "colors": PEPPER_COLORS,
                         "behavior": "MB_NORMAL"})
    for a in c["autotile"].values():  # the water's bank pieces and the like also go on dry ground
        if "apply_on" in a and "." in a["apply_on"] and "d" not in a["apply_on"]:
            a["apply_on"] += "d"
    dry = load("dry_country.json")
    if dry and "terrain" in dry:
        dry_terrain(r, c, dry)
    # the primary's fence tiles (stand-in yard fence and rails) come with their own grass: reseat them on dry ground
    ground = "dry:0_0" if dry and "terrain" in dry else "ekat:grass"
    # every building source (Pokemon Center and Mart, Shady cabin, brick, barn) is redrawn over our ground under its
    # walls: that ground is the dry set's plain sand here, not swamp grass, so no building sits on a green square
    for src in r["sources"]:
        if src.get("rebase_ground"):
            src["rebase_ground"]["base"] = ground
            if src["name"] == "vgen":  # the vanilla PC / Mart tiles' grass arrives as the recoloured swamp greens
                src["rebase_ground"]["colors"] = src["rebase_ground"]["colors"] + [
                    c for c in PEPPER_COLORS if c not in src["rebase_ground"]["colors"]]
    r["patches"].append({"id": "sign_dry", "reseat": "johto:003", "base": ground, "colors": PEPPER_COLORS,
                         "behavior": "MB_NORMAL"})
    have = set((load("redfield.json") or {}).get("pieces", {}))   # real art replaces its stand-in by name
    fence_users = {n: t for n, t in FENCE_STAND_IN.items() if n not in have}
    fence_users.update({n: "0ED" for n in ("rail_h", "rail_cross") if n not in have})
    for t in sorted(set(fence_users.values())):
        r["patches"].append({"id": "fence_" + t, "reseat": "johto:" + t, "base": ground, "colors": PEPPER_COLORS,
                             "behavior": "MB_NORMAL"})
    # ---- own art
    idx = load("redfield.json") or {}
    pieces = dict(idx.get("pieces", {}))
    if dry:
        pieces.update({k: v for k, v in dry.get("pieces", {}).items() if k not in pieces})
    add_pieces(r, c, "rf", "redfield.png", idx, "Redfield's own art (make_redfield_art.py): overlays.")
    if dry and dry.get("pieces"):
        add_pieces(r, c, "dry_o", dry.get("png", "dry_country.png"), {"pieces": dry["pieces"]}, "Dry-country objects.")
    P = c["prefabs"]
    P["sign"] = {"_comment": "Wooden signpost (primary 003) reseated on dry ground.", "rows": [["patch:sign_dry"]]}
    # ---- stand-ins for what the art agent hasn't delivered yet
    crates = {"overlay": "props:crates"}
    barrel = {"overlay": "props:barrel"}
    brick, barn = P.get("brick_shop"), P.get("barn")

    def stand(name, rows, w, h, door, walk, note):
        P[name] = {"_comment": f"STAND-IN for the {name} art ({w}x{h}): {note}.", "rows": rows, "stand_in": True}
        if door:
            P[name]["door"] = list(door)
        if walk:
            P[name]["passable"] = [list(x) for x in walk]

    for name, (w, h, door, walk) in WANTED.items():
        if name in pieces:
            continue
        if name == "sugar_mill" and barn:  # the barn stretched to 7x8, its door on column 3
            br = barn["rows"]
            cols = [0, 2, 3, 1, 2, 3, 5]
            rws = [0, 1, 2, 1, 2, 3, 3, 4]
            stand(name, [[br[j][i] for i in cols] for j in rws], w, h, door, walk, "the Moomoo barn stretched")
        elif name == "ritas_office" and brick:  # the brick shop cut to 5x4
            br = brick["rows"]
            cols = [0, 1, 2, 3, 5]
            stand(name, [[br[j][i] for i in cols] for j in (0, 2, 3, 4)], w, h, door, walk, "the brick shop cut down")
        elif name.startswith("shotgun_") and "cabin" in P:  # the Shady cabin under two empty roof rows
            rows = [[None] * 3, [None] * 3] + [list(rw) for rw in P["cabin"]["rows"]]
            stand(name, rows, w, h, door, walk, "the Shady cabin")
        elif name == "bottling_works" and "brick_row" in P:
            stand(name, copy.deepcopy(P["brick_row"]["rows"]), w, h, door, walk, "the brick row building")
        elif name == "great_sundial":  # the dial's footprint as crates; the plaza paving is the terrain beneath
            rows = [[None] * 8 for _ in range(6)]
            for j in (2, 3):
                for i in (3, 4):
                    rows[j][i] = dict(crates)
            stand(name, rows, w, h, door, walk, "a crate block on the plaza's dirt")
        elif name in ("rail_h", "rail_cross"):
            stand(name, [["patch:fence_0ED"]], w, h, door, walk, "the primary's fence on dry ground, walkable")
        elif name in FENCE_STAND_IN:
            stand(name, [["patch:fence_" + FENCE_STAND_IN[name]]], w, h, door, walk, "the primary's fence on dry ground")
        elif name.startswith("mirror_") and "lamp" in P:
            stand(name, copy.deepcopy(P["lamp"]["rows"]), w, h, door, walk, "a gas lamp")
        elif name in ("sauce_vat",):
            stand(name, [[dict(barrel) for _ in range(w)] for _ in range(h)], w, h, door, walk, "barrels")
        elif name == "ferry" and "airboat" in P:
            stand(name, copy.deepcopy(P["airboat"]["rows"]), w, h, door, walk, "the airboat")
        elif name == "field_tree" and "magnolia" in P:
            stand(name, copy.deepcopy(P["magnolia"]["rows"]), w, h, door, walk, "a magnolia")
        elif name == "field_tree_l" and "magnolia" in P:
            stand(name, [[None] + list(rw) for rw in P["magnolia"]["rows"]], w, h, door, walk, "a magnolia")
        elif name in ("rail_end", "cane_truck", "sundial", "cane_pile", "cane_pile_b",
                      "bottle_crates"):
            stand(name, [[dict(crates) for _ in range(w)] for _ in range(h)], w, h, door, walk, "crates")

"""Rest spots: where each healer room lets the player skip the in-game clock ("Rest until MORNING / DAY / EVENING / NIGHT").

A rest spot is a sign-type bg event running Common_EventScript_RestSpot (data/scripts/orleans_rest.inc) on a bed / cot / bench metatile that
already stands in the room, so it costs no art and no object slot (a map has 16 objects at most; bg events are separate). The cells below
are chosen to be far from the nurse's counter, so the nurse's bow / heal-machine path is never touched, and every cell is checked here:
a rest cell needs a walkable neighbour (the cell the player faces it from) that is not an object, a warp or the exit.

build_interior.py calls `rest_events` for every room that has an entry and `apply_vanilla` for the vanilla rooms it does not generate
(the Battle Frontier Pokemon Center), so a rerun of the generator reproduces the spots instead of wiping them.
"""
import json

SCRIPT = "Common_EventScript_RestSpot"

# the 15x10 Pokemon Center the Crescent / Lands End / Pointe Rouge / Redfield / Storm's Edge rooms share: the hedge-backed white bed (12-13, 2)
# with its cushion row (12-13, 3) in the north-east corner, opposite the nurse's counter
_CENTER_15 = [(12, 3), (13, 3)]

REST = {
    "CrescentCity_PokecenterQuarter": _CENTER_15,
    "CrescentCity_PokecenterWaterfront": _CENTER_15,
    "LandsEnd_Pokecenter": _CENTER_15,
    "PointeRouge_Pokecenter": _CENTER_15,
    "Redfield_Pokecenter": _CENTER_15,
    "StormsEdge_Pokecenter": [(12, 3)],                       # (13, 3) is walled in by the generator machine at (13, 4)
    "LutinsHollow_Pokecenter": [(9, 5), (10, 5)],            # the hedge-backed white bed
    "GrandOak_PokemonCenter": [(11, 5), (12, 5)],            # the window-table cushions
    "CampCocodrie_NurseCabin": [(8, 2), (9, 2)],             # the hedge-backed white bed
    "OldWater_Healer": [(7, 5), (8, 5)],                     # the south bedroll
    "OldWater_RestHouse": [(6, 5), (7, 5)],                  # the south-east bedroll
    "IsleMarais_Shelter": [(3, 10), (3, 11), (5, 10), (5, 11)],  # the two cots by the south door
}

# vanilla rooms (not generated): map folder -> cells, and the layout they are in (checked against its map.bin)
VANILLA = {
    "BattleFrontier_PokemonCenter_1F": [(10, 6), (10, 7)],   # the east-wall cushions
}


def event(x, y):
    return {"type": "sign", "x": x, "y": y, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": SCRIPT}


def without_rest(events):
    return [e for e in events if e.get("script") != SCRIPT]


def check_cells(name, cells, walkable, blocked):
    """walkable(x, y) -> bool for the layout; blocked = cells taken by objects / warps. Raises SystemExit if a cell cannot be used."""
    for x, y in cells:
        if (x, y) in blocked:
            raise SystemExit(f"{name}: rest cell {(x, y)} is taken by an object or warp")
        if not any(walkable(x + dx, y + dy) and (x + dx, y + dy) not in blocked for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))):
            raise SystemExit(f"{name}: rest cell {(x, y)} has no free neighbour to stand on")


def rest_events(name, walkable, blocked):
    cells = REST.get(name)
    if not cells:
        return []
    check_cells(name, cells, walkable, blocked)
    return [event(x, y) for x, y in cells]


def apply_vanilla(root="."):
    """Add the rest spots to the vanilla rooms (idempotent). Returns the maps changed."""
    import struct
    changed = []
    L = {l["id"]: l for l in json.load(open(f"{root}/data/layouts/layouts.json"))["layouts"]}
    for name, cells in VANILLA.items():
        p = f"{root}/data/maps/{name}/map.json"
        m = json.load(open(p, encoding="utf-8"))
        lay = L[m["layout"]]
        raw = open(f"{root}/{lay['blockdata_filepath']}", "rb").read()
        words = struct.unpack(f"<{len(raw) // 2}H", raw)
        w, h = lay["width"], lay["height"]
        blocked = {(o["x"], o["y"]) for o in m["object_events"]} | {(o["x"], o["y"]) for o in m["warp_events"]}
        check_cells(name, cells, lambda x, y: 0 <= x < w and 0 <= y < h and not (words[y * w + x] >> 10) & 3, blocked)
        want = without_rest(m.get("bg_events", [])) + [event(x, y) for x, y in cells]
        if want != m.get("bg_events", []):
            m["bg_events"] = want
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                json.dump(m, f, indent=2, ensure_ascii=False)
                f.write("\n")
            changed.append(name)
    return changed

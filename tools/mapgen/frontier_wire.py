"""Battle Frontier wiring (Chapter 10): every way out of a facility leads back to the Crescent City plaza, in front of that facility's door.

The plaza side is generated (crescent.py: each facility prefab has a door cell and `interior` = its vanilla lobby, so Crescent's map.json carries one
warp per facility). The vanilla Frontier maps are kept as they are, except that every warp that used to leave for MAP_BATTLE_FRONTIER_OUTSIDE_EAST / _WEST
(the lobby mats, and the stray exit warps in the Dome's corridor and pre-battle room) is retargeted here to Crescent City, `dest_warp_id` = that
facility's door warp. Scripts of the facilities only ever warp to their own maps (lobby, corridor, battle room, Pyramid floors, Pike rooms), so a win, a loss
or a retire ends in the lobby, and the lobby's mat leaves by one of these warps.

usage (from the decomp root):
  python tools/mapgen/frontier_wire.py           retarget (after build.py has written data/maps/CrescentCity/map.json); safe to re-run
  python tools/mapgen/frontier_wire.py --check   exit 1 if anything still leaves for a Hoenn map (story_gates_check.frontier_wire runs the same test)
"""
import glob
import json
import os
import sys

# facility -> (lobby map constant, the map directories that belong to it)
FACILITIES = {
    "Tower": ("MAP_BATTLE_FRONTIER_BATTLE_TOWER_LOBBY", "BattleFrontier_BattleTower"),
    "Dome": ("MAP_BATTLE_FRONTIER_BATTLE_DOME_LOBBY", "BattleFrontier_BattleDome"),
    "Palace": ("MAP_BATTLE_FRONTIER_BATTLE_PALACE_LOBBY", "BattleFrontier_BattlePalace"),
    "Arena": ("MAP_BATTLE_FRONTIER_BATTLE_ARENA_LOBBY", "BattleFrontier_BattleArena"),
    "Factory": ("MAP_BATTLE_FRONTIER_BATTLE_FACTORY_LOBBY", "BattleFrontier_BattleFactory"),
    "Pike": ("MAP_BATTLE_FRONTIER_BATTLE_PIKE_LOBBY", "BattleFrontier_BattlePike"),
    "Pyramid": ("MAP_BATTLE_FRONTIER_BATTLE_PYRAMID_LOBBY", "BattleFrontier_BattlePyramid"),
}
OUTSIDE = ("MAP_BATTLE_FRONTIER_OUTSIDE_EAST", "MAP_BATTLE_FRONTIER_OUTSIDE_WEST")
HOENN_LEFTOVERS = OUTSIDE + ("MAP_BATTLE_FRONTIER_RECEPTION_GATE", "MAP_BATTLE_FRONTIER_POKEMON_CENTER_1F", "MAP_BATTLE_FRONTIER_EXCHANGE_SERVICE_CORNER",
                             "MAP_BATTLE_FRONTIER_MART", "MAP_BATTLE_FRONTIER_RANKING_HALL", "MAP_BATTLE_FRONTIER_SCOTTS_HOUSE")
CRESCENT = "data/maps/CrescentCity/map.json"


def load(path):
    return json.load(open(path, encoding="utf-8"))


def save(path, d):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(d, indent=2) + "\n")


def door_warps():
    """facility -> index of the plaza warp that enters its lobby (and the cell it is on)"""
    cc = load(CRESCENT)
    out = {}
    for name, (lobby, _) in FACILITIES.items():
        hits = [(i, w) for i, w in enumerate(cc["warp_events"]) if w["dest_map"] == lobby]
        if len(hits) != 1:
            sys.exit(f"Crescent City has {len(hits)} warps into {lobby} (want exactly one): build crescent_city.json first")
        out[name] = (hits[0][0], (hits[0][1]["x"], hits[0][1]["y"]))
    return out


def facility_maps(prefix):
    # BattleFrontier_BattleTower* also covers the Multi rooms; BattleFrontier_BattlePyramid* the floor and the top
    return sorted(os.path.basename(os.path.dirname(f)) for f in glob.glob(f"data/maps/{prefix}*/map.json"))


def retarget(write):
    doors = door_warps()
    changed, left = [], []
    for name, (lobby, prefix) in FACILITIES.items():
        idx, cell = doors[name]
        for m in facility_maps(prefix):
            path = f"data/maps/{m}/map.json"
            d = load(path)
            dirty = False
            for w in d.get("warp_events", []):
                if w["dest_map"] in HOENN_LEFTOVERS:
                    if w["dest_map"] != "MAP_CRESCENT_CITY" or w["dest_warp_id"] != str(idx):
                        changed.append(f"{m} ({w['x']},{w['y']}) {w['dest_map']} -> MAP_CRESCENT_CITY #{idx} {cell}")
                    w["dest_map"], w["dest_warp_id"] = "MAP_CRESCENT_CITY", str(idx)
                    dirty = True
                if w["dest_map"] == "MAP_CRESCENT_CITY" and w["dest_warp_id"] != str(idx):
                    left.append(f"{m} ({w['x']},{w['y']}) leaves for the wrong Crescent door #{w['dest_warp_id']} (want {idx})")
            # the old Arena workaround: a coord event on the lobby mat that pre-empted the warp. The warp does it now.
            cs = [c for c in d.get("coord_events", []) if not str(c.get("script", "")).endswith("_EventScript_ExitToCrescent")]
            if len(cs) != len(d.get("coord_events", [])):
                d["coord_events"] = cs
                dirty = True
                changed.append(f"{m}: coord event ExitToCrescent removed")
            if dirty and write:
                save(path, d)
    return changed, left


def stray():
    """every warp in a facility map that leaves for a Hoenn leftover, or for a Crescent door that is not its own"""
    doors = door_warps()
    bad = []
    for name, (lobby, prefix) in FACILITIES.items():
        for m in facility_maps(prefix):
            for w in load(f"data/maps/{m}/map.json").get("warp_events", []):
                if w["dest_map"] in HOENN_LEFTOVERS:
                    bad.append(f"{m} ({w['x']},{w['y']}) -> {w['dest_map']}")
                elif w["dest_map"] == "MAP_CRESCENT_CITY" and w["dest_warp_id"] != str(doors[name][0]):
                    bad.append(f"{m} ({w['x']},{w['y']}) -> Crescent door #{w['dest_warp_id']}, not {name}'s #{doors[name][0]}")
    return bad


def main(argv):
    if "--check" in argv:
        bad = stray()
        print("\n".join(bad) or "frontier_wire: every facility exit leads to its Crescent plaza door")
        return 1 if bad else 0
    changed, left = retarget(True)
    print("\n".join(changed) or "frontier_wire: nothing to change")
    print("\n".join(left))
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

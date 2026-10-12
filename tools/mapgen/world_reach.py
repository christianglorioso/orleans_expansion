"""World-wide reachability over every Orleans map joined by its connections (walking AND Surf), for the story gates.

A cell is passable when its collision bits are 0 (any elevation: a deliberate superset, so a "nothing beyond is reachable" proof
can only be too cautious, never wrong). Movement is 4-connected inside a map; leaving a map edge lands in the connected map
(offset convention of the decomp: map A's connection (direction d, offset o) to B puts B's cell at along-axis p - o).

A gate state is a set of story flags that are SET. In a state:
  * an object whose `flag` is set is hidden; every other object whose local id says it is an obstacle (DEBRIS, JAM, SPAN, HEDGE, NET)
    is solid; ordinary NPCs are ignored (they are not gates; ignoring them can only widen the reachable set);
  * a coord-event trigger whose var is a FLAG id with var_value 0 is a wall while that flag is clear (it turns the player back).

usage as a module: reach(starts, flags=set()) -> {map: set(cells)}; python tools/mapgen/world_reach.py shows the baseline.
"""
import glob
import json
import os
import struct
import sys
from collections import deque

OBSTACLE_WORDS = ("DEBRIS", "_JAM", "SPAN", "HEDGE", "_NET", "SHUTTER")
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

_CACHE = {}


def orleans_maps():
    names = []
    for f in sorted(glob.glob("tools/mapgen/maps/*.json")):
        b = os.path.basename(f)
        if f.endswith((".detected.json", ".base.json")) or b.startswith("_"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(d, dict) and "map" in d and "objects" in d:
            names.append(d["map"])
    return sorted(set(names))


def load(name):
    if name in _CACHE:
        return _CACHE[name]
    m = json.load(open(f"data/maps/{name}/map.json", encoding="utf-8"))
    lay = next(l for l in json.load(open("data/layouts/layouts.json"))["layouts"] if l["id"] == m["layout"])
    raw = open(lay["blockdata_filepath"], "rb").read()
    w, h = lay["width"], lay["height"]
    mb = struct.unpack(f"<{w * h}H", raw)
    coll = [[(mb[y * w + x] >> 10) & 3 for x in range(w)] for y in range(h)]
    elev = [[mb[y * w + x] >> 12 for x in range(w)] for y in range(h)]
    conns = []
    for c in m.get("connections", []):
        tgt = c["map"]
        conns.append((c["direction"], tgt, c["offset"]))
    d = {"w": w, "h": h, "coll": coll, "elev": elev, "m": m, "conns": conns}
    _CACHE[name] = d
    return d


def const_to_dir(const):
    """MAP_ORLEANS_ROUTE6 -> Route6 (found by scanning data/maps/*/map.json ids once)"""
    if "_IDS" not in _CACHE:
        ids = {}
        for f in glob.glob("data/maps/*/map.json"):
            try:
                mid = json.load(open(f, encoding="utf-8")).get("id")
            except ValueError:
                continue
            ids[mid] = os.path.basename(os.path.dirname(f))
        _CACHE["_IDS"] = ids
    return _CACHE["_IDS"].get(const)


def blockers(name, flags):
    """cells that are walls in this gate state: obstacle objects (flag clear) and flag-keyed triggers (flag clear)"""
    d = load(name)
    out = set()
    for o in d["m"].get("object_events", []):
        lid = o.get("local_id") or ""
        fl = str(o.get("flag", "0"))
        if fl not in ("0", "") and fl in flags:
            continue
        if any(wd in lid for wd in OBSTACLE_WORDS):
            out.add((o["x"], o["y"]))
    for c in d["m"].get("coord_events", []):
        if c.get("type") != "trigger":
            continue
        var = str(c.get("var", ""))
        if var.startswith("FLAG_") and str(c.get("var_value", "0")) == "0" and var not in flags:
            out.add((c["x"], c["y"]))
    return out


def passable(name, flags=frozenset()):
    d = load(name)
    key = ("pass", name, frozenset(flags))
    if key not in _CACHE:
        wall = blockers(name, flags)
        _CACHE[key] = {(x, y) for y in range(d["h"]) for x in range(d["w"]) if not d["coll"][y][x] and (x, y) not in wall}
    return _CACHE[key]


def neighbours(name, cell, flags):
    """cells next to `cell` (same map or the connected one)"""
    d = load(name)
    x, y = cell
    for dx, dy in DIRS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < d["w"] and 0 <= ny < d["h"]:
            yield name, (nx, ny)
            continue
        direction = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}[(dx, dy)]
        for cd, tgt, off in d["conns"]:
            if cd != direction:
                continue
            t = const_to_dir(tgt)
            if t is None:
                continue
            td = load(t)
            if direction in ("right", "left"):
                p = y - off
                c2 = (0 if direction == "right" else td["w"] - 1, p)
            else:
                p = x - off
                c2 = (p, 0 if direction == "down" else td["h"] - 1)
            if 0 <= c2[0] < td["w"] and 0 <= c2[1] < td["h"]:
                yield t, c2


def reach(starts, flags=frozenset()):
    """starts: [(map, (x, y))]. Returns {map: set(cells)} reachable by walking or Surf (superset) in the gate state `flags`."""
    flags = frozenset(flags)
    seen = {}
    q = deque()
    for name, c in starts:
        if c in passable(name, flags):
            seen.setdefault(name, set()).add(c)
            q.append((name, c))
    while q:
        name, c = q.popleft()
        for n2, c2 in neighbours(name, c, flags):
            if c2 in passable(n2, flags) and c2 not in seen.get(n2, ()):
                seen.setdefault(n2, set()).add(c2)
                q.append((n2, c2))
    return seen


# where the player can stand at the stages the gates are tested for (all on land the player legally reaches by story order)
STARTS = {
    "west": [("CrescentCity", (3, 43)), ("Route3", (10, 11)), ("StormsEdge", (5, 20)), ("GrandOak", (10, 10)), ("IsleMarais", (10, 10)),
             ("Route1", (12, 20)), ("OldWater", (24, 30)), ("Route2", (10, 10))],
    "pointe": [("Route4", (19, 43)), ("PointeRouge", (22, 44)), ("Route5", (30, 24))],
}


def main():
    flags = set(a for a in sys.argv[1:] if a.startswith("FLAG_"))
    r = reach(STARTS["west"] + STARTS["pointe"], flags)
    print("flags set:", sorted(flags) or "none")
    for n in sorted(r):
        print(f"  {n:14s} {len(r[n]):5d} cells")


if __name__ == "__main__":
    main()

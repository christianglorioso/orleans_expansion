"""Flood-fill proof that the story gates of Chapter 2 cannot be walked around (run from the decomp root, after a build):

    python tools/mapgen/story_gates_check.py

Walks the BUILT maps (data/layouts/*/map.bin + data/maps/*/map.json), on foot only (Surf comes after gym 4, so water is a valid
barrier). NPCs and item balls are solid. Cells are walkable like check.py: collision 0 and elevation 0/3/4/15, with the engine's
rule that a walker can't step between two different fixed elevations.
Checks:
  1. Storm's Edge with the drawbridge raised (barriers + both leaves + the open gap): from the Route 2 side nothing on the east
     bank (Mart door, lighthouse door, house E door, the Route 3 exit) is reachable, while the gym door, the Center door and the
     west houses are; with the bridge lowered the east bank is reachable.
  2. Grand Oak + Route 2 joined across their connection (offset 5): from the Route 1 end of town, with the three storm-hedge
     objects in place, no Route 2 cell is reachable; with the hedges gone it is.
  3. Route 3 (from the Storm's Edge side): with the Jayden trigger cells blocked no cell of the east edge is reachable, and every
     trigger row has a free cell for Jayden at x + 1.
  4. Crescent City: with the Route 14 floodwater triggers blocked nothing of the bottom row inside the Route 14 connection is
     reachable from the Route 3 arrival point.
  5. Crescent City west edge into Route 6 (Routes 6-8 open with the fourth verse): with the two storm-debris objects at Route 6's
     (29, 22) and (29, 23) in place nothing west of x 29 is reachable from Crescent; without them it is.
  6. EVERY coord event of every Orleans map (outdoor specs and their interiors): its var is a VAR_* or FLAG_* id (never "0" =
     TRIGGER_RUN_IMMEDIATELY, which freezes on a msgbox), and its elevation matches the cell: the cell's own elevation, 0 (any),
     or 4 on a bridge deck cell (15; a walker keeps the bridgehead's 4). The engine only fires an event at the player's elevation.
Exit code 1 if any check fails.
"""
import json
import os
import struct
import sys
from collections import deque

ROOT = os.getcwd()


def layout(name):
    m = json.load(open(f"data/maps/{name}/map.json"))
    lay = next(l for l in json.load(open("data/layouts/layouts.json"))["layouts"] if l["id"] == m["layout"])
    raw = open(lay["blockdata_filepath"], "rb").read()
    return m, struct.unpack(f"<{len(raw) // 2}H", raw), lay["width"], lay["height"]


class Grid:
    def __init__(self, name, extra_block=(), remove_objects=(), raised=None):
        self.m, self.mb, self.w, self.h = layout(name)
        self.blocked = set(extra_block)
        for o in self.m["object_events"]:
            if o.get("local_id") in remove_objects or o.get("flag", "0") != "0" and o.get("local_id") in remove_objects:
                continue
            self.blocked.add((o["x"], o["y"]))
        self.raised = raised or {}

    def cell(self, x, y):
        if (x, y) in self.raised:
            return self.raised[(x, y)]
        v = self.mb[y * self.w + x]
        return (v >> 10) & 3, v >> 12

    def walk(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h) or (x, y) in self.blocked:
            return False
        c, e = self.cell(x, y)
        return c == 0 and e in (0, 3, 4, 15)

    def fill(self, sources, stop=()):
        """All cells reachable on foot from the sources (cells in `stop` are not entered)."""
        stop = set(stop)
        states = set()
        q = deque()
        for s in sources:
            if self.walk(*s) and s not in stop:
                states.add((s, self.cell(*s)[1]))
                q.append((s, self.cell(*s)[1]))
        while q:
            (x, y), e = q.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) in stop or not self.walk(nx, ny):
                    continue
                me = self.cell(nx, ny)[1]
                if e != 0 and me not in (0, 15) and me != e:
                    continue
                st = ((nx, ny), e if me == 15 else me)
                if st not in states:
                    states.add(st)
                    q.append(st)
        return {c for c, _ in states}


results = []


def check(ok, text):
    results.append(ok)
    print(("ok    " if ok else "FAIL  ") + text)


def storms_edge():
    spec = json.load(open("tools/mapgen/maps/storms_edge.json", encoding="utf-8"))
    raised = {}
    for st in spec["states"]["BridgeRaised"]:  # barriers and leaves block; the gap is plain water
        raised[(st["x"], st["y"])] = (1, 1) if st.get("tile") == "terrain" else (1, 3)
    west_src = [(0, y) for y in range(38)]
    g_up = Grid("StormsEdge", raised=raised)
    g_dn = Grid("StormsEdge")
    doors = {w["dest_map"]: (w["x"], w["y"] + 1) for w in g_up.m["warp_events"]}
    east_targets = {"Mart door": doors["MAP_STORMS_EDGE_MART"], "lighthouse door": doors["MAP_STORMS_EDGE_LIGHTHOUSE"],
                    "east house door": doors["MAP_STORMS_EDGE_HOUSE_E"], "Route 3 exit (49,12)": (49, 12),
                    "Route 3 exit (49,13)": (49, 13)}
    west_targets = {"gym door": doors["MAP_STORMS_EDGE_GYM"], "Center door": doors["MAP_STORMS_EDGE_POKECENTER"],
                    "west house door": doors["MAP_STORMS_EDGE_HOUSE_W"], "centre house door": doors["MAP_STORMS_EDGE_HOUSE_C"],
                    "seafood market door": doors["MAP_STORMS_EDGE_SEAFOOD_MARKET"]}
    up = g_up.fill(west_src)
    for name, c in west_targets.items():
        check(c in up, f"Storm's Edge, bridge raised: {name} {c} is reachable from Route 2")
    for name, c in east_targets.items():
        check(c not in up, f"Storm's Edge, bridge raised: {name} {c} is NOT reachable from Route 2")
    east_cells = [(x, y) for (x, y) in up if x >= 29]
    check(not east_cells, f"Storm's Edge, bridge raised: no walkable cell at x >= 29 is reachable ({len(east_cells)} found)")
    dn = g_dn.fill(west_src)
    for name, c in east_targets.items():
        check(c in dn, f"Storm's Edge, bridge lowered: {name} {c} is reachable")


def grand_oak_route2():
    go_hedges = [(39, 13), (39, 14), (39, 15)]
    ids = {o["local_id"] for o in json.load(open("data/maps/GrandOak/map.json"))["object_events"]
           if o.get("local_id", "").startswith("LOCALID_GRAND_OAK_STORM_HEDGE")}
    check(len(ids) == 3, f"Grand Oak: {len(ids)} storm hedge objects (3 expected, the road is 3 wide)")
    for label, gone in (("hedges in place", ()), ("hedges cut", ids)):
        go = Grid("GrandOak", remove_objects=gone)
        r2 = Grid("Route2")
        # Route 2 y = Grand Oak y - 5 (connection offset 5); both are fills in one space: Route 2 shifted by (40, 5)
        seen_go = go.fill([(19, 33), (20, 33)])
        reach = set()
        frontier = [(0, y - 5) for (x, y) in seen_go if x == 39 and 0 <= y - 5 < r2.h and r2.walk(0, y - 5)]
        if frontier:
            reach = r2.fill(frontier)
        # Grand Oak rows 5-30 are the Route 2 connection (offset 5); rows 0-4 and 31-33 at x 39 are the map's edge with no neighbour
        east_edge = [(x, y) for (x, y) in seen_go if x == 39 and 5 <= y <= 30]
        if gone:
            check(bool(reach), f"Grand Oak + Route 2, {label}: Route 2 is reachable (x=39 cells reached: {sorted(y for _, y in east_edge)})")
        else:
            check(not reach and not east_edge, f"Grand Oak + Route 2, {label}: no cell of the east edge and nothing of Route 2 is reachable "
                  f"(edge cells found: {sorted(y for _, y in east_edge)})")


def route_3():
    trig = [(c["x"], c["y"]) for c in json.load(open("data/maps/Route3/map.json"))["coord_events"]
            if "BridgeStandoff" in c["script"]]
    g = Grid("Route3", remove_objects={"LOCALID_ROUTE3_JAYDEN"})  # he is hidden until his scene
    check(bool(trig), f"Route 3: {len(trig)} Jayden trigger cells {trig}")
    srcs = [(0, y) for y in range(g.h)]
    reach = g.fill(srcs, stop=trig)
    east = sorted(y for (x, y) in reach if x >= 43)
    check(not east, f"Route 3: with the trigger cells blocked nothing at x >= 43 is reachable from the west edge (found rows {east})")
    check(all(g.walk(x + 1, y) for x, y in trig), "Route 3: Jayden has a free walkable cell at (x+1, row) for every trigger row")
    open_ = g.fill(srcs)
    check(any(x >= 43 for x, _ in open_), "Route 3: without the triggers the east side IS reachable (sanity)")


def crescent():
    trig = [(c["x"], c["y"]) for c in json.load(open("data/maps/CrescentCity/map.json"))["coord_events"]
            if "FloodedRoad" in c["script"]]
    g = Grid("CrescentCity")
    check(bool(trig), f"Crescent City: {len(trig)} floodwater trigger cells in the bottom row")
    reach = g.fill([(3, 43), (3, 44)], stop=trig)
    south = sorted(x for (x, y) in reach if y == g.h - 1 and 39 <= x <= 66)
    check(not south, f"Crescent City: with the triggers blocked no bottom-row cell inside the Route 14 connection is reachable (found {south})")
    free = g.fill([(3, 43), (3, 44)])
    cover = {x for (x, y) in free if y == g.h - 1 and 39 <= x <= 66}
    check(cover <= {x for x, _ in trig}, f"Crescent City: every walkable bottom-row cell in x 39-66 is a trigger (uncovered: {sorted(cover - {x for x, _ in trig})})")


def crescent_route6():
    r6 = Grid("Route6")
    deb = [o for o in r6.m["object_events"] if "DEBRIS" in o.get("local_id", "")]
    check(len(deb) == 2 and all(o["flag"] == "FLAG_BADGE04_GET" for o in deb),
          f"Route 6: {len(deb)} storm-debris objects hidden by FLAG_BADGE04_GET at {[(o['x'], o['y']) for o in deb]}")
    trig = [(c["x"], c["y"]) for c in json.load(open("data/maps/CrescentCity/map.json"))["coord_events"]
            if "FloodedRoad" in c["script"]]
    cr = Grid("CrescentCity")
    free = cr.fill([(3, 43), (3, 44)], stop=trig)  # the city, as a player with the arrival done sees it (Route 14 gated)
    # Crescent y -> Route 6 y + 12 (connection offset -12); only the west edge column connects
    src = [(49, y + 12) for (x, y) in free if x == 0 and 0 <= y + 12 < r6.h]
    check(bool(src), f"Crescent City -> Route 6: {len(src)} walkable west-edge cells connect to Route 6's east edge")
    for label, removed in (("debris in place", ()), ("debris cleared", {o["local_id"] for o in deb})):
        g = Grid("Route6", remove_objects=removed)
        reach = g.fill(src)
        west = sorted(c for c in reach if c[0] < 29)
        if removed:
            check(bool(west), f"Route 6, {label}: the west of the route IS reachable (sanity, {len(west)} cells)")
        else:
            check(not west, f"Route 6, {label}: nothing west of x 29 is reachable from Crescent (found {len(west)})")


def all_triggers():
    names = {json.load(open(os.path.join("tools/mapgen/maps", f), encoding="utf-8"))["map"]
             for f in os.listdir("tools/mapgen/maps")
             if f.endswith(".json") and not f.endswith((".detected.json", ".base.json")) and not f.startswith("_")
             and isinstance(json.load(open(os.path.join("tools/mapgen/maps", f), encoding="utf-8")), dict)
             and "map" in json.load(open(os.path.join("tools/mapgen/maps", f), encoding="utf-8"))}
    n = bad = 0
    for d in sorted(os.listdir("data/maps")):
        if "Frlg" in d or not any(d == m or d.startswith(m + "_") for m in names):  # (Route23_Frlg etc. are vanilla FRLG maps)
            continue
        m, mb, w, h = layout(d)
        for c in m.get("coord_events", []):
            if c.get("type") != "trigger":
                continue
            n += 1
            var = str(c["var"])
            ok_var = var.startswith(("VAR_", "FLAG_"))
            cell = mb[c["y"] * w + c["x"]] >> 12
            ok_el = c["elevation"] == cell or c["elevation"] == 0 or (cell == 15 and c["elevation"] == 4)
            if not (ok_var and ok_el):
                bad += 1
                print(f"      {d} ({c['x']},{c['y']}) var {var!r} elevation {c['elevation']} cell elevation {cell} -> {c['script']}")
    check(bad == 0, f"{n} Orleans coord events: every var is a VAR_/FLAG_ id and every elevation matches its cell ({bad} bad)")


if __name__ == "__main__":
    storms_edge()
    grand_oak_route2()
    route_3()
    crescent()
    crescent_route6()
    all_triggers()
    print(f"{results.count(False)} failed of {len(results)}")
    sys.exit(1 if False in results else 0)

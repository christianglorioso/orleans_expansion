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


def layout_objects(name):
    return [o for o in json.load(open(f"data/maps/{name}/map.json"))["object_events"] if "local_id" in o]


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
    g_up = Grid("StormsEdge", raised=raised)
    g_dn = Grid("StormsEdge")
    west_src = [(0, y) for y in range(g_up.h)]
    exits = [tuple(c) for e in spec["exits"] for c in e["cells"] if c[0] == 49]      # the Route 3 causeway cells (x 49), wherever the road runs
    doors = {w["dest_map"]: (w["x"], w["y"] + 1) for w in g_up.m["warp_events"]}
    east_targets = {"Mart door": doors["MAP_STORMS_EDGE_MART"], "lighthouse door": doors["MAP_STORMS_EDGE_LIGHTHOUSE"],
                    "east house door": doors["MAP_STORMS_EDGE_HOUSE_E"], **{f"Route 3 exit {c}": c for c in exits}}
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
    go_hedges = [(43, 13), (43, 14), (43, 15)]
    ids = {o["local_id"] for o in json.load(open("data/maps/GrandOak/map.json"))["object_events"]
           if o.get("local_id", "").startswith("LOCALID_GRAND_OAK_STORM_HEDGE")}
    check(len(ids) == 3, f"Grand Oak: {len(ids)} storm hedge objects (3 expected, the road is 3 wide)")
    for label, gone in (("hedges in place", ()), ("hedges cut", ids)):
        go = Grid("GrandOak", remove_objects=gone)
        r2 = Grid("Route2")
        # Route 2 y = Grand Oak y - 5 (connection offset 5); both are fills in one space: Route 2 shifted by (40, 5)
        seen_go = go.fill([(19, 33), (20, 33)])
        reach = set()
        frontier = [(0, y - 5) for (x, y) in seen_go if x == 43 and 0 <= y - 5 < r2.h and r2.walk(0, y - 5)]
        if frontier:
            reach = r2.fill(frontier)
        # Grand Oak rows 5-30 are the Route 2 connection (offset 5); rows 0-4 and 31-33 at x 39 are the map's edge with no neighbour
        east_edge = [(x, y) for (x, y) in seen_go if x == 43 and 5 <= y <= 30]
        if gone:
            check(bool(reach), f"Grand Oak + Route 2, {label}: Route 2 is reachable (x=43 cells reached: {sorted(y for _, y in east_edge)})")
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
    m = json.load(open("data/maps/CrescentCity/map.json"))
    ev = [(c["x"], c["y"], c["elevation"]) for c in m["coord_events"] if "FloodedRoad" in c["script"]]
    trig = [(x, y) for x, y, _ in ev]
    import crescent_flood   # the floodwater state (fix B): rows 64-65 of the connection are water (collision) until badge 6, the trigger row is 63
    flood = {(c["x"], c["y"]): (1, 3) for c in crescent_flood.cells() if c["collision"]}
    g = Grid("CrescentCity", raised=flood)
    check(bool(trig) and all(y == 63 for _, y in trig), f"Crescent City: {len(ev)} floodwater trigger events on the bank row 63")
    reach = g.fill([(3, 43), (3, 44)], stop=trig)
    south = sorted((x, y) for (x, y) in reach if y >= 63 and 39 <= x <= 66)
    check(not south, f"Crescent City: with the triggers blocked and the water in, no cell of rows 63-65 inside the Route 14 connection is reachable (found {south})")
    # every standable cell of the bank row (a surfer is at the water's elevation) has a trigger at its own elevation
    stand = [(x, g.cell(x, 63)[1]) for x in range(39, 67) if g.cell(x, 63)[0] == 0]
    unc = [(x, e) for x, e in stand if not any(tx == x and ty == 63 and te in (e, 0) for tx, ty, te in ev)]
    check(not unc, f"Crescent City: every standable bank-row cell in x 39-66 is a trigger at its elevation (uncovered: {unc})")
    open_ = Grid("CrescentCity").fill([(3, 43), (3, 44)])
    check(any(y == 65 and 39 <= x <= 66 for x, y in open_), "Crescent City: without the water and triggers the road IS open (sanity)")


def crescent_doors():
    """The Drowned Ward door and the gym door each have one approach cell, held by an object until its flag (people are solid)."""
    g = Grid("CrescentCity")
    objs = {o.get("local_id"): o for o in g.m["object_events"]}
    reach = g.fill([(3, 43), (3, 44)])
    for door, guard, flag in (((62, 26), "LOCALID_CRESCENT_CITY_WARD_GUARD", "FLAG_BADGE03_GET"),
                              ((22, 18), "LOCALID_CRESCENT_CITY_GYM_USHER", "FLAG_HIDE_CRESCENT_GYM_USHER")):
        o = objs.get(guard)
        nbrs = [(door[0] + dx, door[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if g.walk(door[0] + dx, door[1] + dy) or (door[0] + dx, door[1] + dy) == (o["x"], o["y"])]
        check(o is not None and o["flag"] == flag and nbrs == [(o["x"], o["y"])],
              f"Crescent City: door {door} has exactly one approach cell {nbrs}, held by {guard} (hidden by {flag})")
        check(door not in reach, f"Crescent City: with {guard} in place the door {door} cannot be reached on foot")


def crescent_route6():
    r6 = Grid("Route6")
    deb = [o for o in r6.m["object_events"] if "DEBRIS" in o.get("local_id", "")]
    check(len(deb) >= 2 and {(29, 22), (29, 23)} <= {(o["x"], o["y"]) for o in deb} and all(o["flag"] == "FLAG_ROUTE6_DEBRIS_CLEARED" for o in deb),
          f"Route 6: {len(deb)} storm-debris objects hidden by FLAG_ROUTE6_DEBRIS_CLEARED at {[(o['x'], o['y']) for o in deb]}")
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


def crescent_gym():
    g = Grid("CrescentCity_Gym")
    lights = [c for c in g.m["coord_events"] if c.get("type") == "trigger" and "Light" in c["script"]]
    orange = {(c["x"], c["y"]) for c in lights if "Orange" in c["script"]}
    blue = {(c["x"], c["y"]) for c in lights if "Blue" in c["script"]}
    leader = next(o for o in g.m["object_events"] if o["local_id"].endswith("FIFOLET0"))
    check(len(orange) == 3 and len(blue) == 2, f"Crescent gym: {len(orange)} orange (send-back) and {len(blue)} blue lights")
    reach = g.fill([(10, 15)], stop=orange)
    check((leader["x"], leader["y"] + 1) in reach, "Crescent gym: Fifolet's tile is reachable with every orange light blocked")
    # the maze (rows 5-15, people solid): simple paths from the entrance hall's door to the leader's door
    cells = {(x, y) for x in range(g.w) for y in range(5, 16) if g.walk(x, y)}

    def paths(blocked):
        out, path, seen = [], [(10, 15)], {(10, 15)}

        def dfs(c):
            if c == (10, 5):
                out.append(tuple(path))
                return
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if n in cells and n not in blocked and n not in seen:
                    seen.add(n)
                    path.append(n)
                    dfs(n)
                    path.pop()
                    seen.discard(n)
        dfs((10, 15))
        return out
    free, lit = paths(set()), paths(orange)
    check(len(free) > 1 and len(lit) == 1, f"Crescent gym: the maze has {len(free)} routes; with the orange lights lit exactly {len(lit)} remains (it must be 1)")
    check(bool(lit) and blue <= set(lit[0]) and not (orange & set(lit[0])),
          "Crescent gym: both blue lights are on the true way and no orange light is")
    check(all(c["var"] == "FLAG_BADGE03_GET" for c in lights), "Crescent gym: every light is dead once the badge is earned")


def pointe_rouge_east():
    """The dust-storm gate: every cell of Pointe Rouge's last column that the player can stand on is a flag trigger."""
    m, mb, w, h = layout("PointeRouge")
    free = lambda x, y: 0 <= x < w and 0 <= y < h and not (mb[y * w + x] >> 10) & 3  # any elevation, water too (surf, bridges)
    trig = {(c["x"], c["y"]) for c in m["coord_events"]
            if c.get("script") == "PointeRouge_EventScript_DustStorm" and c["var"] == "FLAG_DUST_STORMS_LIFTED" and str(c["var_value"]) == "0"}
    last = {(w - 1, y) for y in range(h) if free(w - 1, y)}
    check(bool(trig) and last <= trig, f"Pointe Rouge: every standable cell of the east edge column is a dust-storm trigger (uncovered: {sorted(last - trig)})")
    check(all(mb[y * w + x] >> 12 == next(c for c in m["coord_events"] if (c["x"], c["y"]) == (x, y))["elevation"] for x, y in trig if free(x, y)),
          "Pointe Rouge: every dust-storm trigger's elevation matches its cell")
    # flood fill (any elevation) from the Route 5 edge and the Route 4 edge with the triggers blocked: nothing at x >= w-1 is reached
    src = [(0, y) for y in range(h) if free(0, y)] + [(x, h - 1) for x in range(w) if free(x, h - 1)]
    seen, q = set(), deque()
    for sx in src:
        if sx not in trig:
            seen.add(sx)
            q.append(sx)
    while q:
        x, y = q.popleft()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n not in seen and n not in trig and free(*n):
                seen.add(n)
                q.append(n)
    check(not any(x >= w - 1 for x, _ in seen), f"Pointe Rouge, triggers blocked: nothing in the east column is reachable ({len(seen)} cells reached)")
    check(not (seen & {(w - 1, y) for y in range(h)}) and any(x >= 60 for x, _ in seen), "Pointe Rouge: the east half IS reachable up to the gate (sanity)")
    check(m["connections"] and any(c["map"] == "MAP_ORLEANS_ROUTE23" and c["direction"] == "right" for c in m["connections"]),
          "Pointe Rouge: the only way east is the Route 23 connection on the last column")


def pointe_gym():
    """Kingfisher's rafters sit behind two nets in the net-rack wall (gaps (6, 7) and (14, 7)); the three fans are reachable first."""
    nets = [o["local_id"] for o in layout_objects("PointeRouge_Gym") if "_NET" in o["local_id"]]
    check(len(nets) == 2, f"Pointe Rouge gym: {len(nets)} net objects")
    g = Grid("PointeRouge_Gym")
    door = [(10, 14)]
    reach = g.fill(door)
    check(not any(y < 7 for _, y in reach), f"Pointe Rouge gym, nets in place: nothing north of the net-rack wall is reachable ({sorted(c for c in reach if c[1] < 7)[:3]})")
    check({(6, 10), (14, 10), (10, 8)} <= reach, "Pointe Rouge gym: the three fans' standing cells (6, 10), (14, 10), (10, 8) are reachable with the nets in place")
    king = next(o for o in g.m["object_events"] if o["local_id"].endswith("KINGFISHER0"))
    g2 = Grid("PointeRouge_Gym", remove_objects=nets)
    reach2 = g2.fill(door)
    check((king["x"], king["y"] + 1) in reach2, "Pointe Rouge gym, nets blown away: Kingfisher's tile is reachable")
    flags = {o["flag"] for o in g.m["object_events"] if o["local_id"] in nets}
    check(flags == {"FLAG_POINTE_GYM_TAILWIND"}, "Pointe Rouge gym: both nets are hidden by FLAG_POINTE_GYM_TAILWIND")
    pr = Grid("PointeRouge")
    guard = next((o for o in pr.m["object_events"] if o.get("local_id") == "LOCALID_POINTE_ROUGE_ICE_PLANT_GUARD"), None)
    door2 = (39, 25)
    nb = [(door2[0] + dx, door2[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if pr.walk(door2[0] + dx, door2[1] + dy) or guard and (door2[0] + dx, door2[1] + dy) == (guard["x"], guard["y"])]
    check(guard is not None and nb == [(guard["x"], guard["y"])], f"Pointe Rouge: the ice plant door's only approach cell {nb} is held by the guard")
    check(guard is not None and guard.get("flag") == "FLAG_HIDE_POINTE_ICE_GUARD", "Pointe Rouge: the ice plant guard is hidden by FLAG_HIDE_POINTE_ICE_GUARD (set by PGSetup from story 45)")
    pr2 = Grid("PointeRouge", remove_objects=["LOCALID_POINTE_ROUGE_ICE_PLANT_GUARD"])
    reach_door = pr2.fill([(39, 27)])
    check((39, 26) in reach_door and (39, 25) in reach_door, "Pointe Rouge, guard gone (story 45+): the ice plant door (39, 25) is reachable from the street")
    ps = open(os.path.join(ROOT, "data", "maps", "PointeRouge", "scripts.inc"), encoding="utf-8").read()
    check("call_if_ge VAR_ORLEANS_STORY, 45, PointeRouge_EventScript_IceGuardGone" in ps and "setflag FLAG_HIDE_POINTE_ICE_GUARD" in ps,
          "Pointe Rouge: PGSetup hides the ice plant guard state-based at story >= 45 (cleared saves are fixed too)")


def world_gates():
    """Every verse / story gate, proved over ALL Orleans maps joined by their connections, walking and Surf together
    (world_reach.py: any collision-0 cell is passable at any elevation, so the closed proofs are conservative)."""
    import world_reach as W
    gates = [  # (name, key flag, maps wholly beyond the gate, {map: predicate on a cell for the part of a map that is beyond})
        ("Route 6 water gate (verse 4, Old Water)", "FLAG_ROUTE6_DEBRIS_CLEARED", ["Route7", "Route8", "Route9", "CampCocodrie", "Route25", "OldestShrine"], {"Route6": lambda c: c[0] < 29}),
        ("Route 10 water gate (verse 5)", "FLAG_BADGE05_GET", ["Route11", "Route12", "Route13", "LutinsHollow"], {"Route10": lambda c: c[0] > 11}),
        ("Crescent floodwater (verse 6)", "FLAG_BADGE06_GET", ["Route14", "Route15", "Route16", "Route17", "Redfield", "Route18", "Route19", "Route20", "LandsEnd", "Route21", "Route22"], {}),
        ("Route 18 water gate (verse 7)", "FLAG_BADGE07_GET", ["Route19", "Route20", "LandsEnd", "Route21", "Route22"], {"Route18": lambda c: c[0] > 38}),
        ("Route 21 water gate (verse 8)", "FLAG_BADGE08_GET", ["Route22"], {"Route21": lambda c: c[1] > 8}),
        ("Route 25 storm wall at the Route 8 seam (both raids): no Route 25 cell at all", "FLAG_ROUTE25_OPEN", ["Route25", "OldestShrine"], {}),
        ("Pointe Rouge dust storm", "FLAG_DUST_STORMS_LIFTED", ["Route23", "Route24"], {}),
    ]
    starts = W.STARTS["west"] + W.STARTS["pointe"]
    all_flags = {g[1] for g in gates}

    def beyond(r, maps, parts):
        out = sorted(m for m in maps if r.get(m))
        for m, pred in parts.items():
            if any(pred(c) for c in r.get(m, ())):
                out.append(m + " (far side)")
        return out
    for name, flag, maps, parts in gates:
        closed = W.reach(starts, all_flags - {flag})
        got = beyond(closed, maps, parts)
        check(not got, f"{name}: with {flag} clear (every other gate open) nothing beyond is reachable by foot or Surf (leaks: {got})")
        opened = W.reach(starts, all_flags)
        got2 = beyond(opened, maps, parts)
        check(bool(got2), f"{name}: with {flag} set the far side IS reachable (sanity: {got2[:3]})")
    # a badge-4 surfer's world, stage by stage (only the gates' own flags matter). Route 10 and Route 25 are partly reachable on their near
    # side (up to their cuts), which is intended: they join Crescent / Route 8.
    west = {"CrescentCity", "Route3", "StormsEdge", "Route2", "GrandOak", "Route1", "IsleMarais", "OldWater", "Route4", "Route5", "PointeRouge"}
    base = west | {"Route6", "Route10"}
    s21 = set(W.reach(starts, set()))
    check(s21 == base, f"story 21 (Kingfisher beaten, verse not yet sung): a surfer reaches the west, Pointe, Route 6 and Route 10's near sides only (extra {sorted(s21 - base)}, missing {sorted(base - s21)})")
    s22 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED"}))
    intended = base | {"Route7", "Route8", "Route9", "CampCocodrie"}
    check(s22 == intended, f"story 22 (verse 4 sung, badge 4 + Surf): Routes 6-9 and Camp Cocodrie open, no Route 25 cell, nothing else (extra {sorted(s22 - intended)}, missing {sorted(intended - s22)})")
    s26 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET"}))
    want26 = intended | {"Route11", "Route12", "Route13", "LutinsHollow"}
    check(s26 == want26, f"story 26 (verse 5): Routes 10-13 and Lutin's Hollow open, nothing more (extra {sorted(s26 - want26)}, missing {sorted(want26 - s26)})")
    s29 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET"}))
    want29 = want26 | {"Route14", "Route15", "Route16", "Route17", "Redfield", "Route18"}  # Route 18 only up to its fallen span
    check(s29 == want29, f"story 29 (verse 6, the floodwater has receded): Routes 14-17 and Redfield open, Routes 18+ still shut (extra {sorted(s29 - want29)}, missing {sorted(want29 - s29)})")
    s33 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET"}))
    want33 = want29 | {"Route19", "Route20", "LandsEnd", "Route21"}  # Route 21 only up to its row-8 cut
    check(s33 == want33, f"story 33 (verse 7, the fallen span is gone): Routes 18-20, Land's End and Route 21's near side open, no Route 22 cell (extra {sorted(s33 - want33)}, missing {sorted(want33 - s33)})")
    s36 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET"}))
    want36 = want33 | {"Route22"}
    check(s36 == want36, f"story 36 (verse 8, the barge and the rain are gone): Route 21 and Route 22 open, nothing east of the dust storms (extra {sorted(s36 - want36)}, missing {sorted(want36 - s36)})")
    s38 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET", "FLAG_DUST_STORMS_LIFTED"}))
    want38 = want36 | {"Route23", "Route24"}
    check(s38 == want38, f"story 38 (Rayquaza wakes, the dust storms lift): Routes 23-24 open, still no Route 25 or shrine cell (extra {sorted(s38 - want38)}, missing {sorted(want38 - s38)})")
    s40 = set(W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET", "FLAG_DUST_STORMS_LIFTED", "FLAG_ROUTE25_OPEN"}))
    want40 = want38 | {"Route25", "OldestShrine"}
    check(s40 == want40, f"story 40 (both raids done, FLAG_ROUTE25_OPEN): Route 25 and the Oldest Shrine open, and only then (extra {sorted(s40 - want40)}, missing {sorted(want40 - s40)})")
    r40 = W.reach(starts, {"FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET", "FLAG_DUST_STORMS_LIFTED"})
    check((5, 24) in r40.get("Route22", ()) and (39, 7) in r40.get("Route24", ()),
          "the dive spot's standing cell Route 22 (5, 24) and the shaft's Route 24 (39, 7) are reachable by story 38 (before the raids)")


def camp_cocodrie():
    """Chapter 5: the nurse cabin's door is held by Isaac until his battle; every cook-off ingredient and the judging table are reachable."""
    cc = Grid("CampCocodrie")
    isaac = next((o for o in cc.m["object_events"] if o.get("local_id") == "LOCALID_CAMP_COCODRIE_ISAAC"), None)
    door = (7, 21)
    nb = [(door[0] + dx, door[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
          if cc.walk(door[0] + dx, door[1] + dy) or (isaac and (door[0] + dx, door[1] + dy) == (isaac["x"], isaac["y"]))]
    check(isaac is not None and isaac["flag"] == "FLAG_HIDE_CAMP_ISAAC" and nb == [(isaac["x"], isaac["y"])],
          f"Camp Cocodrie: the nurse cabin door's only approach cell {nb} is held by Isaac (hidden by FLAG_HIDE_CAMP_ISAAC)")
    # outdoor ingredient spots: standing cells next to the okra patches, the fisherman and the doors are reachable from the landing side (east edge)
    reach = cc.fill([(48, 13), (48, 14)])
    for label, cell in (("okra patch 1", (45, 7)), ("okra patch 2", (46, 5)), ("the dock fisherman", (24, 24)), ("the smokehouse door", (31, 22)),
                        ("cabin 1 door", (4, 12)), ("cabin 4 door", (47, 12)), ("the gym door", (17, 12))):
        check(cell in reach, f"Camp Cocodrie: {label} (standing cell {cell}) is reachable from the landing")
    for room, cells in (("CampCocodrie_Gym", [(9, 4), (5, 4), (13, 4)]), ("CampCocodrie_Smokehouse", [(5, 6)]), ("CampCocodrie_Cabin1", [(3, 3)])):
        g = Grid(room)
        ex = g.m["warp_events"][0]
        r = g.fill([(ex["x"], ex["y"] - 1)])
        check(all(c in r for c in cells), f"{room}: the judging table / fire door / old neighbour's standing cells {cells} are reachable from the door")


def lutins_hollow():
    """Chapter 6: the gym door's only approach cell is held by Lutin's pupil until story 28; the trial's pools and every Lutin are reachable."""
    hh = Grid("LutinsHollow")
    usher = next((o for o in hh.m["object_events"] if o.get("local_id") == "LOCALID_LUTINS_HOLLOW_GYM_USHER"), None)
    door = next((w for w in hh.m["warp_events"] if w["dest_map"] == "MAP_LUTINS_HOLLOW_GYM"), None)
    door = (door["x"], door["y"])
    nb = [(door[0] + dx, door[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
          if hh.walk(door[0] + dx, door[1] + dy) or (usher and (door[0] + dx, door[1] + dy) == (usher["x"], usher["y"]))]
    check(usher is not None and usher["flag"] == "FLAG_HIDE_HOLLOW_GYM_USHER" and nb == [(usher["x"], usher["y"])],
          f"Lutin's Hollow: the gym door's only approach cell {nb} is held by the pupil (hidden by FLAG_HIDE_HOLLOW_GYM_USHER)")
    g = Grid("LutinsHollow_Gym")
    ex = g.m["warp_events"][0]
    r = g.fill([(ex["x"], ex["y"] - 1)])
    need = [(5, 8), (10, 8), (15, 8), (15, 5), (5, 5), (10, 5), (19, 7), (3, 11), (17, 11)]
    check(all(c in r for c in need), f"Lutin's gym: the three pools' standing cells, every Lutin's standing cell and both trainers' are reachable ({[c for c in need if c not in r]} missing)")
    # the arrival lane: the hollow's only way in is the Route 13 lane; the singers by the south pools are on it (story 27)
    check(any(o.get("local_id", "").endswith("_JAYDEN") for o in hh.m["object_events"]), "Lutin's Hollow: Jayden and Wren stand by the south pools")


def redfield_mill():
    """Chapter 7: Rita holds the yard gate (story 31), the shutter holds the gym door's only approach cell until the three sundials are lit,
    every mirror and the two sundials the corridor reaches have a reachable standing cell, and Route 14's rougarou stands on land."""
    src = [(0, 17), (0, 18)]
    rf = Grid("Redfield")
    objs = {o["local_id"]: o for o in rf.m["object_events"] if "local_id" in o}
    shut = objs.get("LOCALID_REDFIELD_SHUTTER_1")
    door = next(w for w in rf.m["warp_events"] if w["dest_map"] == "MAP_REDFIELD_GYM")
    door = (door["x"], door["y"])
    nb = [(door[0] + dx, door[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
          if rf.walk(door[0] + dx, door[1] + dy) or (shut and (door[0] + dx, door[1] + dy) == (shut["x"], shut["y"]))]
    check(shut is not None and shut["flag"] == "FLAG_REDFIELD_MILL_OPEN" and nb == [(shut["x"], shut["y"])],
          f"Redfield: the mill door's only approach cell {nb} is held by the shutter (hidden by FLAG_REDFIELD_MILL_OPEN)")
    trig = {(c["x"], c["y"]) for c in rf.m.get("coord_events", []) if c.get("script") == "Redfield_EventScript_RitaGate"}
    closed = rf.fill(src, stop=trig)
    yard = {(x, y) for x in range(26, 43) for y in range(4, 15)}
    check(len(trig) == 2 and not (closed & yard),
          f"Redfield: with Rita's two gate triggers {sorted(trig)} blocked nothing inside the mill yard is reachable ({sorted(closed & yard)[:3]})")
    og = Grid("Redfield", remove_objects=("LOCALID_REDFIELD_SHUTTER_1",))
    r = og.fill(src)
    check(shut is not None and (shut["x"], shut["y"]) in r, "Redfield: with the shutter gone the gym door's approach cell is reachable from the west road")
    need = {}
    for b in rf.m["bg_events"]:
        sc = b.get("script", "")
        if "_EventScript_Mirror" in sc or "_EventScript_Dial" in sc:
            need[sc.split("_EventScript_")[1]] = (b["x"], b["y"])
    bad = []
    for k, (x, y) in need.items():
        if og.walk(x, y):
            bad.append(f"{k} {x},{y} is walkable (a mirror or dial must be a prop)")
        elif not any((x + dx, y + dy) in r for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            bad.append(f"{k} {x},{y} has no reachable neighbour")
    check(len(need) == 16 and not bad, f"Redfield: all {len(need)} mirror/dial sign cells are props with a reachable neighbour ({bad})")
    # the second sundial pair is two cells (x 32), the corridor x 31 is clear
    check(all((31, y) in r for y in range(4, 12)), "Redfield: the corridor x 31 (y 4-11) is reachable from the road")
    ow = Grid("OldWater")
    cells = [(22, 32), (24, 29), (22, 29), (26, 29), (21, 32)]
    rr = ow.fill([(22, 32)], stop=())
    check(all(c in rr or c in ow.blocked for c in cells) and all(not (c in ow.blocked and c != (22, 32)) or c in cells for c in cells),
          "Old Water: the raid's arrival cell (22, 32) and the actors' cells are on reachable land")


def state_cells(map_name, state):
    """{(x, y): (collision, elevation)} the generated <Map>_EventScript_State<state> sets (its setmetatile lines), over the map's own elevations"""
    import re
    m, mb, w, h = layout(map_name)
    src = open(f"data/maps/{map_name}/scripts.inc", encoding="utf-8").read()
    body = src.split(f"{map_name}_EventScript_State{state}::")[1].split("	return")[0]
    out = {}
    for x, y, coll in re.findall(r"setmetatile (\d+), (\d+), 0x[0-9A-Fa-f]+, (TRUE|FALSE)", body):
        x, y = int(x), int(y)
        out[(x, y)] = (1 if coll == "TRUE" else 0, mb[y * w + x] >> 12)
    return out


def lair_entrances():
    """The legendary lairs (story_data_lairs.py): every route entrance is SEALED in map.bin (no walker reaches its trigger cells from the cell the lair's exit
    returns to), the generated state opens it (all trigger cells reachable and the return cell too), the trigger cells carry the armed-flag trigger, the
    lair's own exit triggers sit on walkable cells of the lair and its encounter has a reachable neighbour (lairs.py --check)."""
    import lairs
    import story_data_lairs as D
    old_states = {"rougarou": "RougarouOpen", "ursaluna": "UrsalunaOpen", "celebi": "CelebiOpen", "suicune": "SuicuneOpen", "raikou": "RaikouOpen", "entei": "EnteiOpen"}
    for key, lair in D.LAIRS.items():
        route = lair["route"]
        if not lair.get("enter") and key not in old_states:
            continue                       # Uxie (the boatman's script warp) and Zapdos (the lighthouse stair) have no route entrance trigger
        state = lair.get("state") or old_states[key]
        script = f"{route}_EventScript_LairEnter{lair.get('enter') or ''}"
        land = (lair["back"][0], lair["back"][1])
        trigs = [c for c in layout(route)[0]["coord_events"] if c.get("script") == script]
        trig = [(c["x"], c["y"]) for c in trigs]
        want = 1 if key == "moltres" else 2
        check(len(trig) == want and all(c.get("var") == D.TRIG and str(c.get("var_value")) == "1" for c in trigs),
              f"{route}: the {key} entrance has {want} trigger(s) {trig} armed by {D.TRIG} (a sealed way never has a live one)")
        opened = state_cells(route, state)
        g_shut, g_open = Grid(route), Grid(route, raised=opened)
        src = [lair["approach"]]
        if key == "galar_articuno":        # the pier stub stands in the lake: reached by Surf, so the check is on the four plank cells themselves
            cells = [(30, 12), (31, 12), (30, 13), (31, 13)]
            check(all(g_shut.cell(*c)[0] == 1 for c in cells), f"{route}: SEALED, the pier's four cells are pilings (collision 1)")
            check(all(opened.get(c, (1, 0))[0] == 0 for c in cells) and land in cells and all(c in opened for c in trig),
                  f"{route}: OPEN (the state's {len(opened)} cells), the four plank cells are walkable ground and hold the triggers {trig} and the return cell {land}")
            continue
        r_shut, r_open = g_shut.fill(src), g_open.fill(src)
        check(all(c not in r_shut for c in trig), f"{route}: SEALED, no walker reaches the {key} trigger cells {trig} from {src[0]} (map.bin holds the closed look)")
        check(all(c in r_open for c in trig) and land in r_open, f"{route}: OPEN (the state's {len(opened)} cells), the {key} trigger cells {trig} and the return cell {land} are reachable from {src[0]}")
    bad = lairs.check()
    check(bad == 0, f"the {len(D.LAIRS)} lair maps match their generator, arrival and exits walk, every encounter has a reachable neighbour ({bad} problems)")


def lands_end():
    """Chapter 8: the Rain Pavilion's seven panels are props with a reachable neighbour, Andrew and Jayden's cells in front of the gym door are
    free and leave its approach cell open, and the verse order is a permutation of 1-7."""
    import story_data_ch8 as c8
    g = Grid("LandsEnd_Gym")
    ex = g.m["warp_events"][0]
    r = g.fill([(ex["x"], ex["y"] - 1)])
    bad = []
    for k, (cells, v) in c8.PANELS.items():
        for (x, y) in cells:
            if g.walk(x, y):
                bad.append(f"panel {k} {x},{y} is walkable")
            elif not any((x + dx, y + dy) in r for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                bad.append(f"panel {k} {x},{y} has no reachable neighbour")
    check(not bad and sorted(v for _c, v in c8.PANELS.values()) == list(range(1, 8)),
          f"Land's End gym: the seven verse panels are props with reachable neighbours and carry verses 1-7 once each ({bad})")
    le = Grid("LandsEnd", remove_objects=("LOCALID_LANDS_END_ANDREW", "LOCALID_LANDS_END_JAYDEN"))
    door = next(w for w in le.m["warp_events"] if w["dest_map"] == "MAP_LANDS_END_GYM")
    door = (door["x"], door["y"])
    objs = {o["local_id"]: o for o in le.m["object_events"] if "local_id" in o}
    a, j = objs["LOCALID_LANDS_END_ANDREW"], objs["LOCALID_LANDS_END_JAYDEN"]
    ok = le.walk(a["x"], a["y"]) and le.walk(j["x"], j["y"]) and (door[0], door[1] + 1) not in ((a["x"], a["y"]), (j["x"], j["y"]))
    check(ok and a["flag"] == "FLAG_HIDE_LANDS_END_ANDREW" and j["flag"] == "FLAG_HIDE_LANDS_END_JAYDEN",
          f"Land's End: Andrew {(a['x'], a['y'])} and Jayden {(j['x'], j['y'])} stand beside the gym door's approach cell {(door[0], door[1] + 1)}, hidden by their flags")


def verse_panels():
    """Chapter 8 S2: every carved panel quotes the verse its Singer sang, verbatim from the leader's own text (sentence by sentence)."""
    import re
    import story_data_ch8 as c8
    BS = chr(92)

    def norm(t):
        return re.sub(r"\s+", " ", t.replace(BS + "n", " ").replace(BS + "p", " ").replace("$", "").replace("BOTH: ", "").replace("THIBODEAUX: ", "")).strip()

    def block(path, label):
        src = open(path, encoding="utf-8").read()
        i = src.index(label + ":")
        j = src.index('$"', i)
        return norm("".join(re.findall(r'\.string "(.*?)"', src[i:j + 2])))
    srcs = {1: ("GrandOak_Gym", "FirstVerse"), 2: ("StormsEdge_Gym", "SecondVerse"), 3: ("CrescentCity_Gym", "ThirdVerse"),
            4: ("PointeRouge_Gym", "FourthVerse"), 5: ("CampCocodrie_Gym", "FifthVerse"), 6: ("LutinsHollow_Gym", "SixthVerse"), 7: ("Redfield_Gym", "SeventhVerse")}
    bad = []
    for v, (f, l) in srcs.items():
        gym = block(f"tools/mapgen/story/{f}.inc", f"{f}_Text_{l}")
        panel = block("tools/mapgen/story/LandsEnd_Gym.inc", f"LandsEnd_Gym_Text_Verse{v}").replace("Carved on the panel: ", "")
        for sent in re.split(r"(?<=[.!?])\s+", panel):
            if sent and sent not in gym:
                bad.append(f"verse {v}: {sent!r}")
    check(not bad, f"Land's End panels: all seven carved verses are verbatim from the Singers' own texts ({bad})")


def finale_rooms():
    """Chapter 9: in the Tide Hall the sealed door is the corridor's only way to Kyogre, Kyogre and Groudon have a standing cell to face them, the
    exits are on the entry side, and the Oldest Shrine's scene cells are free."""
    import arena_rooms
    t = Grid("LandsEnd_DrownedTemple")
    ex = t.m["warp_events"][0]
    sign = next(b for b in t.m["bg_events"] if str(b.get("script", "")).endswith("_TheSealed0"))
    ky = next(o for o in t.m["object_events"] if o.get("local_id", "").endswith("_KYOGRE_RAID0"))
    # the sealed door is a map state (arena_rooms.states): closed in map.bin, its middle column walkable once StateDoorOpen has run
    opened = {(x, y): (0 if walk else 1, 3) for x, y, _n, walk in arena_rooms.states("temple")["DoorOpen"]}
    r_shut = t.fill([(ex["x"], ex["y"] - 1)])
    r_open = Grid("LandsEnd_DrownedTemple", raised=opened).fill([(ex["x"], ex["y"] - 1)])
    sing = (sign["x"], sign["y"] + 1)
    inc = open("tools/mapgen/story/LandsEnd_DrownedTemple.inc", encoding="utf-8").read()
    check(ky["flag"] == "FLAG_HIDE_KYOGRE_RAID" and (ky["x"], ky["y"] + 1) not in r_shut and (ky["x"], ky["y"] + 1) in r_open
          and sing in r_shut and not t.walk(sign["x"], sign["y"]) and (sign["x"], sign["y"]) in r_open
          and "call_if_set FLAG_TEMPLE_DOOR_OPEN, LandsEnd_DrownedTemple_EventScript_StateDoorOpen" in inc and "StateDoorOpen::" in open("data/maps/LandsEnd_DrownedTemple/scripts.inc", encoding="utf-8").read(),
          "Drowned Temple: Kyogre's standing cell is reachable only once the sealed door is open (map state StateDoorOpen, set on load from FLAG_TEMPLE_DOOR_OPEN); the singing cell in front of it is reachable")
    g = Grid("LandsEnd_SaltCathedral")
    ex = g.m["warp_events"][0]
    gr = next(o for o in g.m["object_events"] if o.get("local_id", "").endswith("_GROUDON_RAID0"))
    check((gr["x"], gr["y"] + 1) in g.fill([(ex["x"], ex["y"] - 1)]), "Salt Cathedral: Groudon's standing cell is reachable from the exit")
    _pg = tuple(o["local_id"] for o in Grid("OldestShrine").m["object_events"] if str(o.get("flag", "")).startswith("FLAG_PG_"))
    sh = Grid("OldestShrine", remove_objects=("LOCALID_OLDEST_SHRINE_CAMILLE", "LOCALID_OLDEST_SHRINE_ANDREW", "LOCALID_OLDEST_SHRINE_RAYQUAZA", "LOCALID_OLDEST_SHRINE_JAYDEN") + _pg)
    objs = {o["local_id"]: o for o in sh.m["object_events"] if "local_id" in o}
    cells = [(objs[k]["x"], objs[k]["y"]) for k in ("LOCALID_OLDEST_SHRINE_CAMILLE", "LOCALID_OLDEST_SHRINE_ANDREW", "LOCALID_OLDEST_SHRINE_RAYQUAZA", "LOCALID_OLDEST_SHRINE_JAYDEN")]
    up = next(c for c in sh.m["connections"] if c["direction"] == "down")
    rr = sh.fill([(x, 22) for x in range(sh.w)])
    check(all(sh.walk(*c) for c in cells) and sum(1 for c in cells if c in rr) >= 3 and all(objs[k]["flag"].startswith("FLAG_HIDE_SHRINE") for k in objs if k.startswith("LOCALID_OLDEST_SHRINE_") and "_PG_" not in k and k.split("_")[-1] in ("CAMILLE", "ANDREW", "RAYQUAZA", "JAYDEN")),
          f"Oldest Shrine: the scene cells {cells} are walkable (and reachable from the landing) and hidden by their flags")


def frontier_gate():
    """Chapter 10: the Battle Frontier plaza (Crescent City, south of Canal Avenue) is sealed by its fence and the guard in the one-tile gate; the seven halls'
    doors (real warps into the vanilla lobbies) and the cell in front of each are inside, and every facility exit leads back to its own door (frontier_wire.py);
    every post-game object stands on a walkable cell hidden by its own flag."""
    import frontier_wire as fw
    cc = Grid("CrescentCity")
    guard = next(o for o in cc.m["object_events"] if o.get("local_id") == "LOCALID_CRESCENT_CITY_FRONTIER_GUARD")
    src = [(48, 21)]
    r_closed = cc.fill(src)
    cc2 = Grid("CrescentCity", remove_objects=("LOCALID_CRESCENT_CITY_FRONTIER_GUARD",))
    r_open = cc2.fill(src)
    fronts = {}
    for n, (lobby, _) in fw.FACILITIES.items():
        ws = [w for w in cc.m["warp_events"] if w["dest_map"] == lobby]
        if len(ws) == 1:
            fronts[n] = (ws[0]["x"], ws[0]["y"] + 1)
    check(guard["flag"] == "FLAG_UNUSED_0x2D9" and len(fronts) == 7 and not any(c in r_closed for c in fronts.values()) and all(c in r_open for c in fronts.values()),
          f"Crescent City: the Frontier plaza (the seven halls' doors, standing cells {sorted(fronts.values())}) is reachable only once the guard is gone (FLAG_UNUSED_0x2D9)")
    bad = fw.stray()
    check(not bad and all(cc.walk(*c) for c in fronts.values()),
          f"Battle Frontier: every exit of the seven facilities (lobby mats, stray warps) returns to its own Crescent plaza door; none leaves for a Hoenn map ({bad})")
    import story_data_ch10 as c10
    bad = []
    for (m, key, kind, flag, gfx, (x, y), s) in c10.all_objects():
        g = Grid(m)
        # an arena's legend stands on its dais (a blocking cell in the art): the player faces it from the cell below
        # (Articuno's ice dais blocks too; so do Mesprit's pool, which it hovers over, and Uxie's rock, from the stepping stone / the walk below: batch 2's mocks)
        fy = y + 1 if key in ("KYOGRE_RE", "GROUDON_RE", "ARTICUNO", "MESPRIT", "UXIE") else y
        if not (g.w > x and g.h > fy) or (g.cell(x, fy)[0] != 0):
            bad.append(f"{m} {key} {x},{fy} is not a walkable cell")
        o = [e for e in g.m["object_events"] if e.get("flag") == flag]
        if not o:
            bad.append(f"{m} {key}: no object with {flag}")
    check(not bad, f"post-game objects: all {len(c10.all_objects())} stand on collision-free cells, each hidden by its own flag ({bad})")


def trainers_vs_triggers():
    """A trainer who spots the player on a flag-trigger cell takes over (the approach/battle runs instead of the coord event), and the player
    then stands ON the cell and walks on: a gate leak. So no trainer's line of sight may cover a cell that carries a flag trigger."""
    names = [d for d in sorted(os.listdir("data/maps")) if "Frlg" not in d]
    bad = []
    n = 0
    for d in names:
        try:
            m, mb, w, h = layout(d)
        except (OSError, StopIteration, ValueError, KeyError):
            continue
        cells = {(c["x"], c["y"]) for c in m.get("coord_events", [])
                 if c.get("type") == "trigger" and str(c.get("var", "")).startswith("FLAG_")}
        if not cells:
            continue
        for o in m.get("object_events", []):
            if o.get("trainer_type") != "TRAINER_TYPE_NORMAL":
                continue
            n += 1
            dx, dy = {"MOVEMENT_TYPE_FACE_UP": (0, -1), "MOVEMENT_TYPE_FACE_DOWN": (0, 1), "MOVEMENT_TYPE_FACE_LEFT": (-1, 0),
                      "MOVEMENT_TYPE_FACE_RIGHT": (1, 0)}.get(o.get("movement_type"), (0, 0))
            sight = int(o.get("trainer_sight_or_berry_tree_id", 0))
            for k in range(1, sight + 1):
                if (o["x"] + dx * k, o["y"] + dy * k) in cells:
                    bad.append(f"{d} trainer ({o['x']},{o['y']}) facing {o.get('movement_type')[-4:]} sees the trigger cell {(o['x'] + dx * k, o['y'] + dy * k)}")
                    break
            if dx == dy == 0 and o.get("movement_type", "").startswith("MOVEMENT_TYPE_WANDER"):
                bad.append(f"{d} a wandering trainer ({o['x']},{o['y']}) on a map with flag triggers")
    check(not bad, f"no trainer's line of sight covers a flag-trigger cell ({n} trainers on maps with flag triggers; leaks: {bad})")


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
            walkable = not (mb[c["y"] * w + c["x"]] >> 10) & 3
            sibling = any(o is not c and (o["x"], o["y"]) == (c["x"], c["y"]) and o.get("type") == "trigger"
                          and (o["elevation"] == cell or o["elevation"] == 0 or (cell == 15 and o["elevation"] == 4))
                          for o in m.get("coord_events", []))
            if not (ok_el or not walkable or sibling):  # (a blocked cell never fires; a sibling at the cell's elevation covers it)
                ok_el = False
            else:
                ok_el = True
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
    crescent_doors()
    crescent_gym()
    pointe_gym()
    camp_cocodrie()
    lutins_hollow()
    redfield_mill()
    lair_entrances()
    lands_end()
    verse_panels()
    finale_rooms()
    frontier_gate()
    trainers_vs_triggers()
    world_gates()
    pointe_rouge_east()
    all_triggers()
    print(f"{results.count(False)} failed of {len(results)}")
    sys.exit(1 if False in results else 0)

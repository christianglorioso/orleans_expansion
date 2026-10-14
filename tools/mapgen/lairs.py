"""The legendary lairs, batch 1, in the game: six outdoor lair maps built cell for cell from the approved mocks (tilesets/lairs/lair_mocks.py),
plus the redone ice plant (Articuno, through build_interior.py and the "iceplant" arena kind of arena_rooms.py).

usage (from the decomp root): python tools/mapgen/lairs.py [--check] [KEY ...]      KEY: rougarou ursaluna celebi suicune raikou entei
    (no flag) writes, for each lair: data/layouts/<Map>/{map.bin,border.bin}, the layouts.json entry, data/maps/<Map>/{map.json,scripts.inc}, the map
              group (gMapGroup_Routes, appended) and the event_scripts.s include; the story file tools/mapgen/story/<Map>.inc is spliced into scripts.inc
    --check   regenerates in memory and compares with what is committed (map.bin, border.bin, map.json, layouts entry) plus the lair's own gameplay
              checks: the arrival cell and the exit trigger cells walk, the encounter has a reachable neighbour, every name is in a mapping, the
              cell the exit returns to is walkable on its route once the entrance is open (repro_check.py and check_interior.py call this)

What a lair is (story_data_lairs.py): 20 x 16, unconnected, on gTileset_OrleansGeneral + its own secondary; the walls are the 2 x 2 block the mock
draws (the same block is the layout's border); the way in is the gap in the south wall at x 10-11: the player arrives on (10, 13) and walks south
onto (10..11, 14), a coord trigger (armed by the lair's OnTransition) that warps back to the route's entrance cell. The cells are opaque pieces of
the art; a cell the mock does not walk blocks (collision 1, elevation 3: the water of a lair is not Surf water). The encounter object stands on the
mock's encounter cell; its scripts, flags and the night logic are hand-written (tools/mapgen/story/<Map>.inc).
Nothing here imports build.py's Builder (it only borrows script_suffix and the event_scripts hook).
"""
import json
import os
import re
import struct
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAIRS_ART = os.path.join(HERE, "tilesets", "lairs")
for p in (HERE, LAIRS_ART):
    if p not in sys.path:
        sys.path.insert(0, p)

import story_data_ch10 as C10  # noqa: E402
import story_data_lairs as D  # noqa: E402
import weather_plan  # noqa: E402

GROUP = "gMapGroup_Routes"
# cells that walk although the mock does not: Suicune stands on the island two cells from the causeway head (10, 9) with a gap of broken blocks and
# shallows (10, 8) between (the mock's player cell is 2 away: a talk reaches one cell). The ford (10, 8) is shallow water the player wades onto to face it
WALK_FIX = {"suicune": {(10, 8): True}}
ELEV = 3
BEGIN, END = "@ --- mapgen: generated NPC scripts (begin) ---", "@ --- mapgen: generated NPC scripts (end) ---"
SECONDARY = {"orleans_lairs_wet": "gTileset_OrleansLairsWet", "orleans_lair_rootkin": "gTileset_OrleansLairRootkin",
             "orleans_lairs_dry": "gTileset_OrleansLairsDry", "orleans_lair_storm": "gTileset_OrleansLairStorm",
             # batch 2
             "orleans_lair_trio": "gTileset_OrleansLairTrio", "orleans_lair_woods": "gTileset_OrleansLairWoods", "orleans_lair_fort": "gTileset_OrleansLairFort",
             "orleans_lair_sugarhouse": "gTileset_OrleansLairSugarhouse", "orleans_lair_field": "gTileset_OrleansLairField"}
BATCH2_DIR = os.path.join(ROOT, "..", "tile_review", "set_pieces", "lairs", "batch2")


class JsonMock:
    """a batch-2 mock read from its json (lair_mocks_b2.py writes <lair>_mock.json): the same surface as the batch-1 mock builders"""

    def __init__(self, key):
        d = json.load(open(os.path.join(BATCH2_DIR, f"{D.LAIRS[key]['json']}_mock.json"), encoding="utf-8"))
        self.d = d
        self.names = [r.split() for r in d["metatiles"]]
        self.walk = [[c == "." for c in r] for r in d["walk"]]
        self.H, self.W = len(self.names), len(self.names[0])
        self.objs = [(o["sprite"], o["x"], o["y"]) for o in d["objects"]]
        self.problems = d.get("autotile_conflicts", [])
        self.border = [self.names[0][0], self.names[0][1], self.names[1][0], self.names[1][1]]

    def resolve(self):
        pass

    def wall_cell(self, x, y):
        return self.border[(x & 1) + (y & 1) * 2]


def const_of(name):
    """Route14_RougarouHollow -> MAP_ROUTE14_ROUGAROU_HOLLOW"""
    return "MAP_" + C10.map_snake(name)


def layout_of(name):
    return "LAYOUT_" + C10.map_snake(name)


def block(mid, coll, elev=ELEV):
    return mid | (coll << 10) | (elev << 12)


def mappings(lair):
    gen = json.load(open(os.path.join(HERE, "tilesets", lair.get("primary", "orleans_general") + ".mapping.json"), encoding="utf-8"))["metatiles"]
    sec = json.load(open(os.path.join(HERE, "tilesets", lair["tileset"] + ".mapping.json"), encoding="utf-8"))["metatiles"]
    return gen, sec


def art():
    """{prefix: pieces module} (the art scripts' builders, as lair_mocks.main() makes them)"""
    import importlib
    import lair_mocks
    mods = {}
    for (script, mod, rdir, png, prefix, prim, lairs) in lair_mocks.TILESETS:
        P = importlib.import_module(mod).build()
        P.pack()
        mods[prefix] = P
    return lair_mocks, mods


def mock_map(key, cache={}):
    """the mock of a lair (any of lair_mocks.LAIRS, Articuno's too), resolved: .names, .walk, .objs, .W, .H"""
    if key in D.LAIRS2:
        return JsonMock(key)
    if "art" not in cache:
        cache["art"] = art()
    lair_mocks, mods = cache["art"]
    k, title, fn, prefix = [r for r in lair_mocks.LAIRS if r[0] == key][0]
    m = getattr(lair_mocks, fn)(mods[prefix])
    m.resolve()
    return m


def iceplant_mock():
    """Articuno's room for arena_rooms.py / build_interior.py: .grid (the metatile name of each cell), .walk, .w, .h"""
    from types import SimpleNamespace
    m = mock_map("articuno")
    return SimpleNamespace(grid=m.names, walk=m.walk, w=m.W, h=m.H)


def objects(key):
    """the lair's people: [{"id", "gfx", "x", "y", "flag", "script"}]; the encounter stands on the mock's encounter cell (the static's own cell
    in story_data_ch10.py is the mock's, kept in step by lair_cells())"""
    lair = D.LAIRS[key]
    name, const = lair["map"], const_of(lair["map"])
    m = mock_map(key)
    ex, ey = [(o[1], o[2]) for o in m.objs if o[0] not in ("player", "boatman")][0]
    if key == "rougarou":
        o = dict(D.ROUGAROU, x=ex, y=ey, script=f"{name}_EventScript_Rougarou")
        return [o]
    import build
    out = []
    for o in C10.overlay_for(name):
        out.append(dict(o, script=f"{name}_EventScript_{build.script_suffix(o['id'], const)}"))
    return out


def layout(key):
    """(words[y][x], border words): the map.bin cells and the border block of the lair"""
    lair = D.LAIRS[key]
    m = mock_map(key)
    gen, sec = mappings(lair)

    def mid(n):
        if n.startswith("P:"):
            return gen[n[2:]]
        pre = n.split(":", 1)[0]
        if pre != lair["prefix"]:
            raise SystemExit(f"{key}: cell {n} is not a primary piece nor one of {lair['prefix']}:")
        return sec[n]
    if key == "zapdos":   # map.bin holds the lamp OUT (the story until FLAG_STORMS_EDGE_GRID_RESTORED); the generated StateLanternLit lights it
        m.names = [[n.replace("ls:lantern_", "ls:lantern_dark_") if re.match(r"ls:lantern_[0-9]", n) else n for n in row] for row in m.names]
    fix = WALK_FIX.get(key, {})
    words = [[block(mid(m.names[y][x]), 0 if fix.get((x, y), m.walk[y][x]) else 1) for x in range(m.W)] for y in range(m.H)]
    border = [block(mid(m.wall_cell(x, y)), 0, 0) for (x, y) in ((0, 0), (1, 0), (0, 1), (1, 1))]   # border[(x & 1) + (y & 1) * 2]
    if lair.get("kind") == "interior":       # an interior's camera margin is black, as every interior's (the building primary's solid piece)
        border = [block(mid("P:jb:008"), 1, 0)] * 4
    return words, border, m


def map_json(key):
    lair = D.LAIRS[key]
    name = lair["map"]
    const = const_of(name)
    objs = []
    for o in objects(key):
        objs.append({"local_id": o["id"], "graphics_id": o["gfx"], "x": o["x"], "y": o["y"], "elevation": ELEV, "movement_type": o["move"],
                     "movement_range_x": 0, "movement_range_y": 0, "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0",
                     "script": o["script"], "flag": o["flag"]})
    coords = [{"type": "trigger", "x": x, "y": y, "elevation": ELEV, "var": D.TRIG, "var_value": "1", "script": f"{name}_EventScript_Exit"}
              for (x, y) in D.exits(key)]
    warps = []
    if lair.get("kind") == "gallery":        # Zapdos' lamp gallery: the stair hatch is the warp, back to the keeper's stair (StormsEdge_Lighthouse warp 1)
        ax, ay = D.arrive(key)
        warps = [{"x": ax, "y": ay, "elevation": ELEV, "dest_map": "MAP_STORMS_EDGE_LIGHTHOUSE", "dest_warp_id": "1"}]
    return {"id": const, "name": name, "layout": layout_of(name), "music": lair["music"], "region_map_section": lair["mapsec"],
            "requires_flash": False, "weather": weather_plan.header(name) or "WEATHER_NONE", "map_type": "MAP_TYPE_INDOOR" if lair.get("kind") == "interior" else "MAP_TYPE_ROUTE", "allow_cycling": False, "allow_escaping": False,
            "allow_running": True, "show_map_name": False, "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None,
            "object_events": objs, "warp_events": warps, "coord_events": coords, "bg_events": []}


def layout_entry(key):
    lair = D.LAIRS[key]
    name = lair["map"]
    m = mock_map(key)
    d = f"data/layouts/{name}"
    return {"id": layout_of(name), "name": f"{name}_Layout", "width": m.W, "height": m.H, "primary_tileset": "gTileset_OrleansBuilding" if lair.get("primary") == "orleans_building" else "gTileset_OrleansGeneral",
            "secondary_tileset": SECONDARY[lair["tileset"]], "border_filepath": f"{d}/border.bin", "blockdata_filepath": f"{d}/map.bin"}


def state_scripts(key):
    """the generated map-state scripts of a lair: Zapdos' gallery lantern (lit once the grid is restored); [] for the others"""
    if key != "zapdos":
        return []
    lair = D.LAIRS[key]
    m = mock_map(key)
    gen, sec = mappings(lair)
    lines = [f"{lair['map']}_EventScript_StateLanternLit::"]
    for y in range(m.H):
        for x in range(m.W):
            n = m.names[y][x]
            if re.match(r"ls:lantern_[0-9]", n):
                lines.append(f"\tsetmetatile {x}, {y}, 0x{sec[n]:03X}, TRUE")
    return lines + ["\treturn", ""]


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write(key):
    lair = D.LAIRS[key]
    name = lair["map"]
    words, border, m = layout(key)
    d = os.path.join(ROOT, "data", "layouts", name)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "map.bin"), "wb").write(struct.pack(f"<{m.W * m.H}H", *[v for row in words for v in row]))
    open(os.path.join(d, "border.bin"), "wb").write(struct.pack("<4H", *border))
    lp = os.path.join(ROOT, "data", "layouts", "layouts.json")
    L = json.load(open(lp, encoding="utf-8"))
    entry = layout_entry(key)
    at = [i for i, l in enumerate(L["layouts"]) if l.get("id") == entry["id"]]
    if at:
        L["layouts"][at[0]] = entry          # a layout's position is its numeric id (saves store it): a rerun never moves it
    else:
        L["layouts"].append(entry)
    with open(lp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(L, f, indent=2)
        f.write("\n")
    gp = os.path.join(ROOT, "data", "maps", "map_groups.json")
    G = json.load(open(gp, encoding="utf-8"))
    if not any(name in v for k, v in G.items() if isinstance(v, list) and k != "group_order"):
        G[GROUP].append(name)                # appended: the other maps' numbers do not move
        dump(gp, G)
    md = os.path.join(ROOT, "data", "maps", name)
    os.makedirs(md, exist_ok=True)
    dump(os.path.join(md, "map.json"), map_json(key))
    sp = os.path.join(md, "scripts.inc")
    if not os.path.exists(sp) or BEGIN not in open(sp, encoding="utf-8").read():
        with open(sp, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{name}_MapScripts::\n\t.byte 0\n\n{BEGIN}\n\n{END}\n")
    st = state_scripts(key)
    if st:
        src = open(sp, encoding="utf-8").read()
        src = src[:src.index(BEGIN)] + BEGIN + "\n\n" + "\n".join(st) + "\n" + src[src.index(END):]
        open(sp, "w", encoding="utf-8", newline="\n").write(src)
    from event_scripts import include_map_scripts
    include_map_scripts(ROOT, name)
    import story
    story.splice(name)
    return m


# ---------------------------------------------------------------------------------------------- checks
def walk_from(words, W, H, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and not (words[ny][nx] >> 10) & 3:
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


def check(keys=None):
    """regenerate in memory, compare with the committed files, run the lair's gameplay checks; returns the number of problems"""
    bad = 0
    for key in keys or D.LAIRS:
        lair = D.LAIRS[key]
        name = lair["map"]

        def fail(msg):
            nonlocal bad
            bad += 1
            print(f"  {name}: {msg}")
        try:
            words, border, m = layout(key)
        except SystemExit as e:
            fail(str(e))
            continue
        d = os.path.join(ROOT, "data", "layouts", name)
        try:
            raw = open(os.path.join(d, "map.bin"), "rb").read()
            have = struct.unpack(f"<{len(raw) // 2}H", raw)
            flat = [v for row in words for v in row]
            diff = [i for i in range(min(len(have), len(flat))) if have[i] != flat[i]]
            if len(have) != len(flat) or diff:
                fail(f"map.bin drifts from the generator ({len(have)} vs {len(flat)} words, {len(diff)} cells differ, first {[(i % m.W, i // m.W) for i in diff[:4]]})")
            if open(os.path.join(d, "border.bin"), "rb").read() != struct.pack("<4H", *border):
                fail("border.bin drifts from the generator")
        except OSError as e:
            fail(f"not generated yet: {e}")
        mp = os.path.join(ROOT, "data", "maps", name, "map.json")
        if os.path.exists(mp):
            got = json.load(open(mp, encoding="utf-8"))
            want = map_json(key)
            for k in want:
                if got.get(k) != want[k]:
                    fail(f"map.json {k} drifts from the generator")
        else:
            fail("map.json missing")
        L = {l.get("id"): l for l in json.load(open(os.path.join(ROOT, "data", "layouts", "layouts.json"), encoding="utf-8"))["layouts"]}
        if L.get(layout_of(name)) != layout_entry(key):
            fail("layouts.json entry drifts from the generator")
        G = json.load(open(os.path.join(ROOT, "data", "maps", "map_groups.json"), encoding="utf-8"))
        if not any(name in v for k, v in G.items() if isinstance(v, list) and k != "group_order"):
            fail(f"not in any map group")
        # gameplay: arrival, exits, the encounter's neighbour, the player cell of the mock
        arr = D.arrive(key)
        reach = walk_from(words, m.W, m.H, arr)
        if arr not in reach or (words[arr[1]][arr[0]] >> 10) & 3:
            fail(f"the arrival cell {arr} does not walk")
        for e in D.exits(key):
            if e not in reach:
                fail(f"the exit cell {e} is not reachable from the arrival cell")
        for o in objects(key):
            nb = [(o["x"] + dx, o["y"] + dy) for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1))]
            if not any(c in reach for c in nb):
                fail(f"{o['id']} at ({o['x']}, {o['y']}) has no reachable neighbour")
            sc, face = D.STAND[key]
            dx, dy = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}[face]
            if sc not in reach or (sc[0] + dx, sc[1] + dy) != (o["x"], o["y"]):       # the cell the player talks to it from: the bot tests stand there
                fail(f"{o['id']}: the stand cell {sc} facing {face} is not a reachable neighbour of ({o['x']}, {o['y']})")
        mp_ = (os.path.join(BATCH2_DIR, f"{lair['json']}_mock.json") if key in D.LAIRS2
               else os.path.join(ROOT, "..", "tile_review", "set_pieces", "lairs", f"{lair['mock']}_mock.json"))
        pc = json.load(open(mp_, encoding="utf-8")) if os.path.exists(mp_) else None
        if pc and (pc["encounter_cell"] != [objects(key)[0]["x"], objects(key)[0]["y"]]):
            fail(f"the committed mock's encounter cell {pc['encounter_cell']} differs from the object's")
        if m.problems:
            fail(f"autotile conflicts left in the mock: {m.problems}")
    # the route side: the cell each lair's exit returns to must exist and (once the entrance is open) walk
    return bad


def main(argv):
    keys = [a for a in argv if not a.startswith("--")] or list(D.LAIRS)
    if "--check" in argv:
        bad = check(keys)
        print(f"{len(keys)} lairs, {bad} problems")
        return 1 if bad else 0
    for k in keys:
        m = write(k)
        print(f"{D.LAIRS[k]['map']}: {m.W}x{m.H}, {len(objects(k))} object(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

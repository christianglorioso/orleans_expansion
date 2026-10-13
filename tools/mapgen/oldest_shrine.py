"""The Oldest Shrine (Rayquaza's arena), handmade: the island, ridges, mound, shell road and landing of the approved arena art
(tilesets/arenas/arena_mocks.py shrine_design(), art in shrine.png/shrine.json, wired into orleans_route_b by shrine_tileset.py) laid on the
36 x 32 map that joins Route 25 at its south edge.

usage (from the decomp root): python tools/mapgen/oldest_shrine.py [--no-build] [--fresh]
    writes maps/oldest_shrine.json + oldest_shrine.grid.txt, then build -> compose -> build until the tileset has every piece (like lands_end.py)

What is drawn (cells; the earthwork is symmetric, terrain cell x mirrors to 34 - x, props to 33 - x):
    island        x 5-29, rows 4-23 (land stays >= 4 cells from the north, west and east edges); `.` grass, `"` marsh groves, R ridges, U the mound
    mound         cells 13-21 x 7-10 (U), south face row 11 (build.py "face" rule), mound_steps (2x2) at (16-17, 10-11), singing stone at (16-17, 6-7)
    ridges        two C-shaped banks (R, 2 cells thick) round the plaza, open to the north; the aisle x 15-19 (y > 15) stays clear
    shell road    x 16-17, rows 12-20 (walkable); landing 4x4 at (15-18, 21-24) in place of the old placeholder pier (the art's mock has it one row lower,
                  but its bottom row would sit in Route 25's seam band)
    props         live oaks (7,4) (23,4), small cypress in the marsh groves (8,8) (24,8), cedar posts, standing stones, shells
    islets        Route 25's marsh banks in the bottom corners (rows 26-31 = the seam band: primary pieces only above all, scenery only)
Stand cells: Rayquaza (16,9); the player (16,10) and Jayden (17,10) on the top step; the keeper (15,14), NPC_1 (18,14); Camille (16,23), Andrew (17,20),
the Dragoninite ball (17,24).  Weather and the story scripts are not touched here (weather_plan.py, story/OldestShrine.inc).
Nothing is written to data/ except through build.py.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tilesets", "arenas"))

KEY, NAME, CONST, CFG = "oldest_shrine", "OldestShrine", "MAP_OLDEST_SHRINE", "orleans_route_b"
SPEC = os.path.join(HERE, "maps", KEY + ".json")
W, H = 36, 32

# Route 25's marsh banks in the bottom corners (rectangles of marsh, x y w h): the old map's, kept as they were
ISLETS = [(5, 26, 2, 1), (30, 26, 3, 1), (3, 27, 5, 1), (29, 27, 4, 1), (3, 28, 6, 4), (28, 28, 5, 1), (27, 29, 6, 3)]

# the placeholder NPCs the story script's talkers (story_data_ch9 OLDEST_SHRINE patches them): the keeper and a local, beside the shell road
OBJECTS = [
    {"id": "LOCALID_OLDEST_SHRINE_NPC_0", "gfx": "OBJ_EVENT_GFX_MAN_1", "x": 15, "y": 14, "move": "MOVEMENT_TYPE_FACE_DOWN", "text": "(First-pass placeholder.)"},
    {"id": "LOCALID_OLDEST_SHRINE_NPC_1", "gfx": "OBJ_EVENT_GFX_MAN_1", "x": 18, "y": 14, "move": "MOVEMENT_TYPE_FACE_DOWN", "text": "(First-pass placeholder.)"},
]

# the old map's water props (trees, logs, snags standing in open water): kept where they still stand in open water (cells all water), as the mock does
OLD_WATER_PROPS = [("cypress_water", 32, 10), ("cypress_small_water", 2, 18), ("waterlog", 24, 30), ("waterlog", 8, 1), ("waterlog", 1, 8),
                   ("snag_water", 32, 4)]


def design():
    import arena_mocks
    g = arena_mocks.shrine_design()
    for (x0, y0, w, h) in ISLETS:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                g[y][x] = '"'
    return [row[:] for row in g]


def uses_char(ch):
    return {"M": "U"}.get(ch, ch)      # build.py clears M to grass (mockup building marks): the mound is U


def build_spec():
    cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
    g = design()
    P = cfg["prefabs"]

    def size(name):
        rows = P[name]["rows"]
        return len(rows[0]), len(rows)

    def all_water(x, y):
        return all(0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] == "~" for dx in (0, 1) for dy in (0, 1))

    b = []
    taken = set()

    def put(name, x, y, label, **kw):
        w, h = size(name) if "rows" not in kw else (len(kw["rows"][0]), len(kw["rows"]))
        b.append(dict({"prefab": name, "x": x, "y": y, "label": label}, **kw))
        taken.update((x + i, y + j) for i in range(w) for j in range(h))

    # the old map's water props that still stand in open water
    for name, x, y in OLD_WATER_PROPS:
        w, h = size(name)
        if all(all_water(x + i, y + j) for i in range(w) for j in range(h)):
            put(name, x, y, "Tree" if "cypress" in name else "Water prop")
    # the earthwork's furniture
    put("cypress_small_marsh", 8, 8, "Tree")
    put("cypress_small_marsh", 24, 8, "Tree")
    for x in (7, 23):
        put("live_oak", x, 4, "Tree")
    put("singing_stone", 16, 6, "Singing stone")
    put("mound_steps", 16, 10, "Mound steps")
    # the landing sits one row higher than the art's mock (15, 22): its bottom row is secondary art, and rows 25-31 are Route 25's seam band
    # (primary pieces only, bands.py), so the landing is (15-18, 21-24) with its slab on row 24 and the shell road runs rows 12-20
    rows = [["osh:shell_W", "osh:shell_E"] for _ in range(9)]
    put("shell_road_w", 16, 12, "Shell road", rows=rows, passable=[[i, j] for j in range(9) for i in range(2)])
    put("landing", 15, 21, "Landing")
    for name, x, y in (("cedar_post_bird", 14, 12), ("cedar_post", 12, 13), ("stone_tall", 6, 13), ("stone_tall", 14, 18),
                       ("stone_small", 12, 7), ("stone_small", 13, 22)):
        put(name, x, y, "Prop")
        put(name, 33 - x, y, "Prop")
    # shells on shore grass where the ground is plain grass under all four corners of the cell
    for (x, y) in ((12, 23), (21, 23), (10, 22)):
        if all(g[y + dy][x + dx] == "." for dx in (0, 1) for dy in (0, 1)) and (x, y) not in taken:
            put("shell_scatter", x, y, "Prop")
    # the islets: scenery only (rows 27-31 are Route 25's seam band: primary pieces only; the rest above it)
    for x in (4, 28):
        put("cypress_small_marsh", x, 28, "Tree")
    def plain_marsh(x, y):   # the cell's four corners are all marsh (a plain marsh centre tile, so a plant replaces no edge piece)
        return all(g[min(H - 1, y + dy)][min(W - 1, x + dx)] == '"' for dx in (0, 1) for dy in (0, 1))
    for (x, y, k) in ((3, 30, "a"), (6, 31, "b"), (7, 29, "a"), (31, 30, "b"), (27, 31, "a"), (32, 29, "b")):
        if plain_marsh(x, y):
            put("marsh_plants_" + k, x, y, "Prop")

    def free_water(x, y):
        return g[y][x] == "~" and all_water(x, y) and (x, y) not in taken
    # dressing between the islets and the channel to the landing (x 12-22). The art's mock put these on rows 24-26, but Route 25's seam band is 7
    # rows deep (bands.py DEPTH: rows 25-31 here, strict: primary pieces only), so the secondary props sit on rows <= 24 instead
    for (x, y) in ((8, 23), (25, 23)):                         # cattails (1x2)
        if free_water(x, y) and free_water(x, y + 1):
            put("wp_cattails", x, y, "Water prop")
    for (x, y, k) in ((6, 24, "a"), (11, 24, "b"), (22, 24, "a"), (27, 24, "b")):   # cypress knees
        if free_water(x, y):
            put("wp_knees_" + k, x, y, "Water prop")
    if free_water(9, 24) and free_water(10, 24):               # a drifted log against the west shore
        put("waterlog", 9, 24, "Water prop")
    for (x, y) in ((27, 22), (6, 22)):                         # an egret on an old post (the first that fits)
        if free_water(x, y) and free_water(x, y + 1):
            put("egret_post", x, y, "Water prop")
            break
    grid = ["".join(uses_char(c) for c in row) for row in g]
    return grid, b


def main(args):
    grid, buildings = build_spec()
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write("\n".join(grid) + "\n")
    old = json.load(open(SPEC, encoding="utf-8")) if os.path.exists(SPEC) else {}
    spec = {"_comment": "The Oldest Shrine, handmade: generated by oldest_shrine.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": "LAYOUT_OLDEST_SHRINE", "layout_dir": "data/layouts/OldestShrine", "tileset": CFG,
            "mockup": "../orleans_maps/13_oldest_shrine.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": buildings, "objects": OBJECTS, "surf_only": [], "items": [], "hidden_items": [], "signs": [], "exits": []}
    with open(SPEC, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)
        f.write("\n")
    if "--no-build" in args:
        return
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    run = lambda a: subprocess.run([sys.executable, "-W", "ignore"] + a, text=True, capture_output=True, cwd=os.path.normpath(os.path.join(HERE, "..", "..")))
    for i in range(6):   # build (writes the uses file and asks for overlays), compose, build again
        r = run([os.path.join(HERE, "build.py"), SPEC])
        print(r.stdout.strip()[-1500:], r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = run([os.path.join(HERE, "compose.py"), recipe])
        print(c.stdout.strip()[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return


if __name__ == "__main__":
    main(sys.argv[1:])

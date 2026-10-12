"""Redfield (gym 7, Sun: sugarcane and pepper country), built by hand from its mockup (08_redfield.png): 52 x 38 on the
orleans_capital tileset (make_town_tilesets.py + redfield_tileset.py; the set is Redfield's alone, the name is historic).

usage (from the decomp root; takes the build lock first, see buildlock.py):
    python -W ignore tools/mapgen/redfield.py [--review] [--no-build] [--fresh] [--dry-run]
writes maps/redfield.json + .grid.txt, regenerates the art when make_redfield_art.py can (sources/orleans_custom) and the
tileset recipe (make_town_tilesets.py orleans_capital), composes and builds (again while the build asks for new overlay
tiles), runs check.py; --review writes maps/00_redfield_review.png and maps/redfield_crops/*.png (mockup | built and 3x
crops). Then build_interior.py relinks the door warps to their rooms (labels from town_plans.PLANS["redfield"]).
Edit this file, never maps/redfield.json. Pieces without art yet use stand-ins of the same footprint
(redfield_tileset.py WANTED): the layout doesn't change when the art lands.

Terrain characters: d dry ground (stand-in: grass), G sugarcane field (encounter grass), q pepper rows, : road,
= plaza paving, ~ river, B levee ground (marked by levee.py, kept clear).

Layout (x right, y down; the mockup at 1.25x):
    west       the sugarcane field (x 0-12, y 0-11, encounter grass); the four shotgun houses (x 14-20: two rows of two,
               doors facing south, a lane between the rows joining the street, a stub from each lower door to the road);
               the pepper rows (x 0-12, y 25-37)
    spine      the Route 17 mill road, 2 wide (y 17-18) from the west edge (the exit, cells (0,17) and (0,18)) to the
               river; the main street (x 22-23) from the north end to the bottling works; the cane railway (y 21),
               level with the ground, with a level crossing at the street, cane trucks on it at the west and a
               buffer stop at the east end
    mill yard  a fenced yard (x 25-43, y 3-15), its gate on the road side (x 29-30): the sugar mill (the gym), Rita's
               office, three sundials and six mirrors, cane piles, the Hearthflame Mask in the corner
    south      the great sundial plaza (x 14-21, y 24-29, west of the street), the Pokemon Center and Mart (doors on
               the south road, y 28-29, which runs east to the river dock), the pepper-sauce bottling works (y 30-35)
    river      x 46-51 (a straight bank, so the levee's corners are all the same); the levee ground is the two cells
               x 44-45, kept clear of props and paths; the dock (x 44-49, y 28-30) is the Route 18 landing, and the
               levee tapers into it
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from firstpass import dock_h, dump, item_flag, shell  # noqa: E402
from town_plans import door_label  # noqa: E402
import interiors as mock  # noqa: E402
import levee  # noqa: E402

KEY, NAME, CONST = "redfield", "Redfield", "MAP_REDFIELD"
CFG = "orleans_capital"
W, H = 52, 38
SPEC = os.path.join(HERE, "maps", KEY + ".json")
ART_SCRIPT = os.path.join(HERE, "sources", "orleans_custom", "make_redfield_art.py")

RIVER_X = 46                     # the first water column (x 46-51): a straight bank
ROAD_Y = (17, 18)                # the Route 17 mill road's rows (the west exit is cells (0, 17) and (0, 18))
ROAD_X1 = 43                     # the rail's east end (the buffer stop)
MILL_X1 = 42                     # the mill road's and the south road's east end: one dry cell (x 43) lies between it and the levee ground
                                 # (grass), because the dry-country road set only has soft edges against dry ground
STREET_X = (22, 23)              # the main street
RAIL_Y = 21
SOUTH_Y = (28, 29)               # the south road to the dock
CANE = (0, 0, 12, 11)            # the sugarcane field (cells x0, y0, x1, y1)
PEPPER = (0, 25, 12, 37)         # the pepper rows
PLAZA = (14, 24, 21, 29)         # the great sundial's plaza (paving beneath the piece)
YARD = (25, 3, 43, 15)           # the mill yard's fence (x0, y0, x1, y1), the gate in the south wall
GATE = (29, 30)                  # the gate's two cells
DOCK = (44, 28)                  # the dock's top-left (6 wide, 3 deep)

# door-bearing buildings in the first pass's warp order (the rooms' exits use these warp numbers):
# room key -> (prefab, top-left)
BUILDINGS = [
    ("redfield_shotgun_house_1", "shotgun_a", (14, 1)),
    ("redfield_shotgun_house_2", "shotgun_b", (18, 1)),
    ("redfield_gym", "sugar_mill", (34, 5)),
    ("redfield_house_1", "shotgun_c", (14, 9)),
    ("redfield_house_2", "shotgun_d", (18, 9)),
    ("redfield_ritas_office", "ritas_office", (26, 6)),
    ("redfield_pokecenter", "pokecenter", (26, 24)),
    ("redfield_mart", "mart", (33, 24)),
    ("redfield_bottling_works", "bottling_works", (25, 30)),
]


class Town:
    def __init__(self):
        self.g = [["d"] * W for _ in range(H)]
        self.b = []
        self.occ = set()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs, self.items, self.hidden = [], [], [], []
        self.skipped = []
        self.stand_ins = set()
        self.walk = set()       # cells a person can stand on that the terrain doesn't say (dock planks)

    def fill(self, ch, x0, y0, x1, y1):
        for j in range(y0, y1 + 1):
            for i in range(x0, x1 + 1):
                if 0 <= i < W and 0 <= j < H:
                    self.g[j][i] = ch

    def have(self, prefab):
        return prefab in self.cfg["prefabs"]

    def rows(self, prefab, rows=None):
        return rows or self.cfg["prefabs"][prefab]["rows"]

    def cells(self, prefab, x, y, rows=None):
        r = self.rows(prefab, rows)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0])) if r[j][i] is not None]

    def place(self, prefab, x, y, label=None, rows=None, passable=None, force=False, **kw):
        cells = self.cells(prefab, x, y, rows)
        clash = [c for c in cells if c in self.occ]
        if clash and not force:
            raise SystemExit(f"{prefab} at ({x},{y}) overlaps {clash[:4]}")
        for c in cells:
            self.occ.add(c)
        b = {"prefab": prefab, "x": x, "y": y, "label": label or prefab.replace("_", " ").capitalize()}
        if rows:
            b["rows"] = rows
        if passable is not None:
            b["passable"] = passable
        b.update(kw)
        self.b.append(b)
        if self.cfg["prefabs"][prefab].get("stand_in"):
            self.stand_ins.add(prefab)
        return b

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def corners(self, cells):
        return {(i + dx, j + dy) for i, j in cells for dx in (0, 1) for dy in (0, 1)}

    def inside(self, cells, ch):
        return all(self.at(i, j) == ch for i, j in self.corners(cells))

    def deco(self, prefab, x, y, label=None, on="d", inside=False, ring=0, **kw):
        """A decoration where it fits (its cells free, on terrain `on`; `inside`: wholly inside the patch `on`;
        `ring`: also this many cells of margin free of other objects), else noted and skipped."""
        if not self.have(prefab):
            self.skipped.append((prefab, x, y, "no prefab"))
            return None
        cs = self.cells(prefab, x, y)
        ok = all(0 <= i < W and 0 <= j < H and (i, j) not in self.occ and self.g[j][i] in on for i, j in cs)
        if ok and inside:
            ok = self.inside(cs, on[0])
        if ok and ring:
            ok = not any((i + dx, j + dy) in self.occ for i, j in cs for dx in range(-ring, ring + 1)
                         for dy in range(-ring, ring + 1))
        if not ok:
            self.skipped.append((prefab, x, y))
            return None
        return self.place(prefab, x, y, label, **kw)

    def grid_text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"


# ---------------------------------------------------------------- land, fields, roads
def terrain(t):
    t.fill("~", RIVER_X, 0, W - 1, H - 1)                                      # the river
    t.fill("G", *CANE)                                                         # the sugarcane field
    t.fill("q", *PEPPER)                                                       # the pepper rows
    t.fill("=", *PLAZA)                                                        # the great sundial's plaza
    road = lambda x0, y0, x1, y1: t.fill(":", x0, y0, x1, y1)
    road(0, ROAD_Y[0], MILL_X1, ROAD_Y[1])                                     # the mill road (Route 17, west edge)
    road(STREET_X[0], 3, STREET_X[1], H - 1)                                   # the main street
    road(14, 7, 21, 8)                                                         # the lane between the shotgun rows
    for key, prefab, (x, y) in BUILDINGS[3:5]:                                 # the lower houses' stubs down to the road
        d = t.cfg["prefabs"][prefab]["door"]
        road(x + d[0], y + d[1] + 1, x + d[0] + 1, ROAD_Y[0] - 1)
    road(SOUTH_Y[0] - 4, SOUTH_Y[0], MILL_X1, SOUTH_Y[1])                      # the south road to the dock (y 28-29)
    road(24, 36, 28, 37)                                                       # the works' door lane
    # the mill yard's paths: the gate stub to the road, the front lane, and the office's lane
    road(GATE[0], YARD[3] + 0, GATE[1], ROAD_Y[0] - 1)
    road(GATE[0], 13, 40, 14)
    road(27, 10, 28, 14)


def buildings(t):
    links = {}
    if os.path.exists(SPEC):
        old = json.load(open(SPEC, encoding="utf-8"))
        links = {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}
    for key, prefab, (x, y) in BUILDINGS:
        label = door_label(key, mock.INTERIORS[key]["title"])
        b = t.place(prefab, x, y, label)
        if label in links:
            b["interior"] = links[label]


# ---------------------------------------------------------------- the mill yard
def yard(t):
    """The fenced yard: fence round (x 25-43, y 3-15), the gate's two cells open with a post either side; sundials and
    mirrors (the trial), cane piles by the mill."""
    x0, y0, x1, y1 = YARD
    gx0, gx1 = GATE
    P = t.place
    for x in range(x0, x1 + 1):
        for y, south in ((y0, False), (y1, True)):
            if x in (gx0, gx1):
                continue
            piece = "yard_h"
            if x == x0:
                piece = "yard_sw" if south else "yard_nw"
            elif x == x1:
                piece = "yard_se" if south else "yard_ne"
            elif south and x == gx0 - 1:
                piece = "yard_gate_l"
            elif south and x == gx1 + 1:
                piece = "yard_gate_r"
            P(piece, x, y, "Yard fence")
    for y in range(y0 + 1, y1):
        for x in (x0, x1):
            P("yard_v", x, y, "Yard fence")
    # the trial: three sundials, six mirrors (they turn: the story pass chooses the facings)
    for x, y in ((28, 4), (32, 6), (32, 10)):
        t.deco("sundial", x, y, "Sundial", ring=0)
    for prefab, x, y in (("mirror_se", 26, 4), ("mirror_sw", 31, 4), ("mirror_ne", 31, 8), ("mirror_nw", 33, 8),
                         ("mirror_ne", 30, 10), ("mirror_se", 33, 4)):
        t.deco(prefab, x, y, "Mirror")
    for prefab, x, y in (("cane_pile", 41, 4), ("cane_pile_b", 34, 4), ("cane_pile_b", 37, 4)):
        t.deco(prefab, x, y, "Cane pile", on="d:")
    for x, y in ((42, 9), (42, 10)):
        t.deco("barrel", x, y, "Barrel")


# ---------------------------------------------------------------- the cane railway
def railway(t):
    """The cane railway across town (y 21): the track is level with the ground (walkable), a level crossing at the
    street, the cane trucks standing on it at the west end (their art includes the rail under them), a buffer stop
    at the east end."""
    trucks = [("cane_truck", 3), ("cane_truck", 6), ("cane_truck", 9)]
    for prefab, x in trucks:
        t.place(prefab, x, RAIL_Y - 1, "Cane truck")
    for x in range(0, ROAD_X1):
        if (x, RAIL_Y) in t.occ:
            continue
        t.place("rail_cross" if x in STREET_X else "rail_h", x, RAIL_Y, "Rail", passable=[[0, 0]])
    t.place("rail_end", ROAD_X1, RAIL_Y, "Buffer stop")


# ---------------------------------------------------------------- landmarks and props
def landmarks(t):
    gx, gy = PLAZA[0], PLAZA[1]
    t.place("great_sundial", gx, gy, "Great sundial", passable=[list(c) for c in
            t.cfg["prefabs"]["great_sundial"].get("passable", [])])
    # the river dock: the Route 18 boat landing; the levee tapers into it
    rows, pas = dock_h(6, True)
    rows[2][0] = rows[2][1] = None   # no posts row where the dock meets the bank: the levee ground runs right up to the
                                     # planks on both sides, so the north and south ends are mirror images
    t.place("pier", DOCK[0], DOCK[1], "Dock", rows=rows, passable=pas, dir="h", levee_blocks=pas)  # the levee ends at the planks
    for i, j in pas:
        t.walk.add((DOCK[0] + i, DOCK[1] + j))
    t.deco("ferry", 47, 31, "River boat", on="~", inside=True)
    # the bottling works' yard
    t.deco("sauce_vat", 35, 31, "Sauce vat")
    t.deco("bottle_crates", 34, 34, "Bottle crates")
    t.deco("barrel", 34, 30, "Barrel")


def dress(t):
    D = t.deco
    for prefab, x, y in (("bench", 11, 16), ("bench", 32, 16), ("bench", 30, 26), ("bench", 38, 27),
                         ("lamp", 24, 15), ("lamp", 21, 15), ("lamp", 21, 19), ("lamp", 24, 19), ("lamp", 4, 15),
                         ("lamp", 24, 26), ("lamp", 37, 26),
                         ("lamp", 21, 22), ("lamp", 24, 22), ("barrel", 34, 30), ("crates", 36, 30)):
        D(prefab, x, y)
    # dry-farmland trees: field-edge oaks and pecans (stand-ins: magnolias) round the town
    for prefab, x, y in (("field_tree", 0, 13), ("field_tree", 7, 13), ("field_tree", 9, 13), ("field_tree", 12, 13),
                         ("field_tree", 24, 0), ("field_tree", 30, 0), ("field_tree", 37, 0), ("field_tree", 41, 0),
                         ("field_tree", 12, 22), ("field_tree", 2, 22), ("field_tree", 6, 22),
                         ("field_tree", 38, 22), ("field_tree", 41, 22), ("field_tree_l", 37, 32),
                         ("field_tree_l", 40, 35), ("field_tree", 41, 30), ("field_tree", 20, 31), ("field_tree", 15, 33)):
        D(prefab, x, y, "Tree")
    # a few stones, sparingly: at the field corners and the east edge of town
    for prefab, x, y in (("rock", 3, 14), ("rock", 9, 23), ("rock", 16, 22), ("rock", 40, 19), ("rock_l", 37, 36),
                         ("rock_l", 15, 36)):
        D(prefab, x, y, "Rock")


def signs(t):
    for sid, x, y, text in (
            ("SignTown", 3, 16, "REDFIELD\nSugarcane and pepper country. Mill road west to Route 17."),
            ("SignMill", 28, 16, "REDFIELD SUGAR MILL\nCayenne's mill yard. Mind the mirrors: it only\nworks by day."),
            ("SignSundial", 13, 28, "THE GREAT SUNDIAL\nRedfield keeps its time by the sun."),
            ("SignWorks", 24, 33, "PEPPER-SAUCE BOTTLING WORKS\nBottled hot. Tour the line any day."),
            ("SignLanding", 43, 27, "ROUTE 18 RIVER LANDING\nBoats cross to the east bank.")):
        if (x, y) in t.occ or t.g[y][x] != "d":
            t.skipped.append(("sign", x, y))
            continue
        t.place("sign", x, y, "Sign")
        t.signs.append({"id": sid, "x": x, "y": y, "text": text})


# ---------------------------------------------------------------- people and items
def people(t):
    folk = [
        ("CAYENNE", "OBJ_EVENT_GFX_WOMAN_2", 36, 13, "MOVEMENT_TYPE_FACE_DOWN",
         "CAYENNE: Welcome to my mill. The sun's\nup: bring a mirror to the sundials.\\n(Story pass: gym introduction.)"),
        ("RITA", "OBJ_EVENT_GFX_WOMAN_2", 31, 12, "MOVEMENT_TYPE_FACE_DOWN",
         "RITA: My Chandelure and I keep the\nmill's books. (Story pass: Mega\\nChandelure battle.)"),
        ("FARMHAND", "OBJ_EVENT_GFX_MAN_1", 13, 5, "MOVEMENT_TYPE_FACE_LEFT",
         "Cane's ready to cut. Don't wander in\nunless you want the whole field\\nto come out at you."),
        ("PICKER", "OBJ_EVENT_GFX_WOMAN_2", 13, 30, "MOVEMENT_TYPE_FACE_LEFT",
         "Peppers by the bushel. Dry, dry\nweather: the best kind for heat."),
        ("KEEPER", "OBJ_EVENT_GFX_OLD_MAN", 13, 27, "MOVEMENT_TYPE_FACE_RIGHT",
         "The great sundial's older than the\nmill. It's never once been wrong."),
        ("FOREMAN", "OBJ_EVENT_GFX_MAN_4", 24, 34, "MOVEMENT_TYPE_FACE_UP",
         "Bottling line's running hot today.\nWatch your eyes."),
        ("KID", "OBJ_EVENT_GFX_LITTLE_BOY", 18, 19, "MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT",
         "The cane trucks go all the way to\nthe mill. I rode one once!"),
        ("BOATMAN", "OBJ_EVENT_GFX_FISHERMAN", 48, 28, "MOVEMENT_TYPE_FACE_LEFT",
         "Boats to Route 18 run on the river.\n(Story pass: the boat crossing.)"),
    ]
    for name, gfx, x, y, move, text in folk:
        ok = (x, y) in t.walk or ((x, y) not in t.occ and t.g[y][x] in "d:=")
        if not ok:
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_REDFIELD_{name}", "gfx": gfx, "x": x, "y": y, "move": move, "text": text})
        t.occ.add((x, y))
    # the Mega Stones and the Mask (mockup 3, 4, 5): ordinary balls with stable flags; the story pass gates them
    for x, y, item, key, what in (
            (42, 7, "ITEM_HEARTHFLAME_MASK", "0", "Hearthflame Mask (mockup 5, post-game): the yard's east corridor"),
            (26, 12, "ITEM_CHANDELURITE", "chandelurite", "Chandelurite (mockup 3, post-game): beside Rita's office"),
            (34, 32, "ITEM_SCOVILLAINITE", "scovillainite", "Scovillainite (mockup 4): by the bottling works")):
        if (x, y) in t.occ or t.g[y][x] not in "d:":
            t.skipped.append(("item " + item, x, y))
            continue
        t.items.append({"x": x, "y": y, "item": item, "flag": item_flag(CONST, key), "_comment": what})
        t.occ.add((x, y))


# ---------------------------------------------------------------- the levee ground
def finish(t):
    """Mark the river bank 'B' (levee ground, drawn by build.py): the two cells beside the water (x 44-45), except
    where the dock and anything else stands; paths and props keep out of them."""
    blocked = set(t.occ) | {(x, y) for y in range(H) for x in range(W) if t.g[y][x] not in "d~"}
    grid = ["".join(r) for r in t.g]
    bank = levee.bank_cells(grid, blocked, ground="d")
    for x, y in bank:
        t.g[y][x] = "B"
    return bank


def levee_corners_match(spec_path=SPEC, limit=0.05, picture=True):
    """Regression guard for the user's note that the levee's two corners (where it meets the dock, north and south of
    it) had inconsistent art styles. The south end must be the north end mirrored about the dock's planks (rows
    DOCK[1] and DOCK[1] + 1; the posts row hangs below them in the water only). Three tests, each of which fails on
    the earlier layout (a posts row on the bank, so a flat grass shelf hung below the planks):
      1. the terrain: the same characters at the mirrored cells beside the dock (levee ground, dry ground, water);
      2. what levee.render draws there: the south cells are the north ones flipped (slope, earth and riprap);
      3. the finished picture: grass / water / stone classes of the levee-ground columns, mirrored.
    Returns (ok, worst share of mismatch); the terrain must match exactly."""
    import numpy as np
    from PIL import Image
    spec = json.load(open(spec_path, encoding="utf-8"))
    grid = [ln.strip() for ln in open(os.path.join(HERE, "maps", spec["grid"]), encoding="utf-8") if ln.strip()]
    top, bot = DOCK[1] - 1, DOCK[1] + 2
    cols = range(DOCK[0] - 2, RIVER_X + 2)
    # 1. terrain
    bad = sum(grid[top - k][x] != grid[bot + k][x] for k in range(6) for x in cols)
    t1 = bad / (6 * len(cols))
    # 2. the levee's own drawing
    bank = {(x, y) for y, row in enumerate(grid) for x, ch in enumerate(row) if ch == "B"}
    blocked = {(bd["x"] + i, bd["y"] + j) for bd in spec["buildings"] if bd.get("label") == "Dock"
               for i, j in bd["levee_blocks"]}
    cells = levee.render(grid, bank, lambda x, y: Image.new("RGB", (16, 16), (200, 180, 120)), blocked)
    empty = np.zeros((16, 16), bool)
    drawn = diff = 0
    for k in range(3):
        for x in range(DOCK[0], RIVER_X + 2):
            a = cells.get((x, top - k))
            b = cells.get((x, bot + k))
            a = np.array(a)[..., 3] > 0 if a is not None else empty
            b = np.array(b)[::-1][..., 3] > 0 if b is not None else empty
            drawn += int(a.sum() + b.sum())
            diff += int((a != b).sum()) * 2
    t2 = diff / max(drawn, 1)
    if not picture:
        return t1 == 0 and t2 <= limit, max(t1, t2)
    # 3. the picture (build.py and render are only imported here, so this module stays importable from build.py)
    import build
    from render import Tilesets, render
    bld = build.Builder(spec_path)
    bld.draw()
    ts = Tilesets(bld.ts["primary_dir"], bld.ts["secondary_dir"])
    im = np.array(render(ts, bld.flat(), bld.w).convert("RGB")).astype(int)

    def klass(a):
        r, g, bl = a[..., 0], a[..., 1], a[..., 2]
        out = np.full(r.shape, 2)                 # stone, earth, planks
        out[(g > r + 16) & (g > bl + 14)] = 0     # grass and slope
        out[(g > r + 18) & (bl >= g - 10)] = 1    # water
        return out
    x0, x1 = DOCK[0] * 16, (DOCK[0] + 2) * 16     # the two levee-ground columns
    north = im[(top - 2) * 16:(top + 1) * 16, x0:x1]
    south = im[bot * 16:(bot + 3) * 16, x0:x1][::-1]
    t3 = float((klass(north) != klass(south)).mean())
    worst = max(t1, t2, t3 / 2)                   # (texture noise leaves ~4% of the picture's classes apart)
    return t1 == 0 and worst <= limit, worst


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [  # (file stem, title, x0, y0, x1, y1) in tiles
    ("mill_yard", "The mill yard: mill, Rita's office, mirrors and sundials", 24, 2, 46, 17),
    ("cane_field", "The sugarcane field (encounter grass)", 0, 0, 14, 13),
    ("pepper_field", "The pepper rows", 0, 23, 14, 38),
    ("rail", "The cane railway, trucks and the level crossing", 0, 16, 46, 24),
    ("houses", "The four shotgun houses", 12, 0, 24, 18),
    ("sundial", "The great sundial plaza", 12, 22, 24, 32),
    ("works", "Pokemon Center, Mart and the bottling works", 24, 22, 46, 38),
    ("dock", "The river dock and the levee taper", 38, 24, 52, 34),
    ("levee_top", "Levee corner, north", 40, 0, 52, 8),
    ("levee_south", "Levee corner, south", 40, 30, 52, 38),
]


def review(out):
    from PIL import Image, ImageDraw, ImageFont
    import build
    from render import Tilesets, render
    build.MAPPING.clear()
    b = build.Builder(SPEC)
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    clean = render(ts, b.flat(), b.w).convert("RGB")
    subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "town_sheet.py"), KEY,
                    os.path.join(HERE, "maps", "00_town_redfield.png")], check=True)
    top = Image.open(os.path.join(HERE, "maps", "00_town_redfield.png")).convert("RGB")
    cdir = os.path.join(HERE, "maps", "redfield_crops")
    os.makedirs(cdir, exist_ok=True)
    crops = []
    for stem, title, x0, y0, x1, y1 in REVIEW_AREAS:
        c = clean.crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
        c = c.resize((c.width * 3, c.height * 3), Image.NEAREST)
        c.save(os.path.join(cdir, stem + ".png"))
        crops.append((title, c))
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    pad, head = 24, 48
    width = max(top.width, 2600)
    rows, row, rw = [], [], pad
    for title, c in crops:
        if row and rw + c.width + pad > width:
            rows.append(row)
            row, rw = [], pad
        row.append((title, c))
        rw += c.width + pad
    rows.append(row)
    height = top.height + pad + sum(max(c.height for _, c in r_) + head for r_ in rows) + pad
    sheet = Image.new("RGB", (width, height), (250, 248, 242))
    sheet.paste(top, (0, 0))
    d = ImageDraw.Draw(sheet)
    y = top.height + pad
    for r_ in rows:
        x = pad
        for title, c in r_:
            d.text((x, y + 8), title, fill=(0, 0, 0), font=font)
            sheet.paste(c, (x, y + head))
            x += c.width + pad
        y += max(c.height for _, c in r_) + head
    sheet.save(out)
    print("review sheet:", out, sheet.size)


# ---------------------------------------------------------------- main
def run(args, **kw):
    return subprocess.run([sys.executable, "-W", "ignore"] + args, text=True, capture_output=True, **kw)


def art():
    """Redraw the sheets when make_redfield_art.py can (it needs a main; a half-written script is left alone)."""
    if os.path.exists(ART_SCRIPT) and "__main__" in open(ART_SCRIPT, encoding="utf-8").read():
        r = run([ART_SCRIPT])
        print(r.stdout.strip(), r.stderr.strip()[-1500:])


def main(args):
    art()
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-200:])  # stand-ins and art first
    t = Town()
    terrain(t)
    buildings(t)
    yard(t)
    railway(t)
    landmarks(t)
    dress(t)
    signs(t)
    people(t)
    bank = finish(t)
    if t.skipped:
        print("left out (no room or no art yet):", t.skipped)
    if t.stand_ins:
        print("stand-ins in use (art not delivered yet):", sorted(t.stand_ins))
    print("levee ground:", len(bank), "cells")
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write(t.grid_text())
    lid, ldir = shell(NAME, CONST, "town", "MAPSEC_REDFIELD", "MUS_RG_PEWTER", W, H, t.cfg)
    spec = {"_comment": "Redfield, handmade: generated by redfield.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/08_redfield.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": t.items, "hidden_items": t.hidden,
            "signs": t.signs,
            "exits": [{"name": "W exit at 16", "cells": [[0, ROAD_Y[0]], [0, ROAD_Y[1]]]}]}
    dump(SPEC, spec)
    if "--no-build" in args:
        return
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    if "--fresh" in args:  # start the overlay requests over, so pieces no longer used don't take tiles
        bf = os.path.join(HERE, "tilesets", CFG + ".blends.json")
        with open(bf, "w") as f:
            json.dump([], f)
    flags = [a for a in args if a == "--dry-run"]
    for i in range(6):  # build (writes the uses file and asks for overlays), compose, build again
        r = run([os.path.join(HERE, "build.py"), SPEC] + flags)
        print(r.stdout.strip(), r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = run([os.path.join(HERE, "compose.py"), recipe])
        print(c.stdout.strip()[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return
    c = run([os.path.join(HERE, "check.py"), SPEC])
    print(c.stdout.strip()[-3000:], c.stderr.strip()[-2000:])
    ok, worst = levee_corners_match()
    print(f"levee corners (north and south of the dock) match: {ok} (worst mismatch {worst:.1%})")
    if "--review" in args:
        review(os.path.join(HERE, "maps", "00_redfield_review.png"))
    if not ok:
        sys.exit("the levee's two corners no longer match (levee.py changed?): fix levee.py, not this check")


if __name__ == "__main__":
    main(sys.argv[1:])

"""Pointe Rouge, the state capital, built by hand from its mockup (05_pointe_rouge.png) at 1.5x: 66 x 48.

usage (from the decomp root):
    python tools/mapgen/pointe_tileset.py                      (tileset recipe + builder config)
    python tools/mapgen/pointe.py [--fresh] [--review] [--no-build]   (spec + grid, compose, build, check;
                                                                      --review writes maps/00_pointe_review.png)
    then python -W ignore tools/mapgen/build_interior.py       (relinks the door warps to their rooms)
When the build asks for new overlay tiles, pointe.py composes the tileset and builds again; --fresh starts the
blends file over first, so overlays no longer used don't take tiles. Register a new tileset with
    python -W ignore tools/mapgen/compose.py tools/mapgen/tilesets/recipes/orleans_pointe.json --register

Layout (x right, y down), following the mockup (review round 2, 2026-10-12: less paving, more green):
    north-west    a 2x2 grid of brick houses mirrored about x = 11 (equal 4-tile gaps), a lane between the rows, a central
                  walk on the mirror line, magnolia pairs on the flanks; a pocket park at the head of Capitol Avenue
    Capitol Ave   the 4-wide paved boulevard (x 22-25), magnolia pairs both sides, to the Route 4 exit (south)
    Capitol       the art-deco tower, its grand staircase down to a garden plaza on Government Street
    Government St the 3-wide cross street (y 17-19): Route 5 exit in the west, the river in the east
    PC, Mart      between the Capitol and the river; Riverfront Drive (x 45-47, widening to bays) joins both bridges
    works         ONE closed fence (x 1-19, y 21-47) round the refinery (crude tanks, columns, flare stack, process house,
                  planted islands in its floor) and the rail yard (three sidings of boxcars); one gate, Refinery Road
                  (east); the three sidings run on west through gaps in the west fence to the map's edge
    south         tackle shop and old ice plant on lawns off Laurel Street; a house with a path to the levee road;
                  Kingfisher's boathouse gym standing on the quay (x 40-46) with its dock; lawns, benches facing flower
                  beds; the dock walk (x 37-38)
    quay          four jib cranes along the city quay (x 46-47) with crate clusters beside them; Crescent's
                  riverboat moored at the gym's dock (the lower pier, below the south bridge), lying across its tip like
                  the bar of a T (x 51-53, rows 36-42), a sailor on the pier end; surf lane x 54-56
    river         the Emerald River (x 48-59), a stone quay along the city bank; two stone arch bridges carry
                  the roads to Route 23 (rows 5-6 and 26-27; the south one is Tornadus's span)
    east bank     the riverside walk, magnolia pairs, and organic patches of tall grass south of the lower bridge
"""
import heapq
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from firstpass import dump, join_network, shell, tidy_paths  # noqa: E402
from pointe_tileset import bridge_rows  # noqa: E402
from town_plans import PLANS, door_label  # noqa: E402
import interiors as mock  # noqa: E402

KEY, NAME, CONST = "pointe_rouge", "PointeRouge", "MAP_POINTE_ROUGE"
CFG = "orleans_pointe"
W, H = 66, 48
SPEC = os.path.join(HERE, "maps", KEY + ".json")
RIVER_EAST = 57  # first land column east of the river
FERRY = "--no-ferry" not in sys.argv  # the ferry pier and Crescent's riverboat (pointe_tileset.py adds its art; --no-ferry leaves it out)


def river_west(y):
    """First water column of the Emerald River at row y: the city bank is a straight stone quay (x 47)."""
    return 48


QUAY_X = 47                    # the quay's edge column on the city bank (walkable; the drop to the water drawn on it)
BRIDGE_ROWS = {"stone_north": 4, "stone_south": 25}  # each bridge's top row: rail, deck, deck, rail, face


class Town:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]
        self.b = []          # spec buildings
        self.occ = set()     # cells taken by a prefab
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs = [], []
        self.deck = set()    # walkable bridge deck cells (water underneath in the grid)
        self.skipped = []

    def fill(self, ch, x, y, w, h):
        for j in range(y, y + h):
            for i in range(x, x + w):
                if 0 <= i < W and 0 <= j < H:
                    self.g[j][i] = ch

    def rows(self, prefab, rows=None):
        return rows or self.cfg["prefabs"][prefab]["rows"]

    def cells(self, prefab, x, y, rows=None):
        r = self.rows(prefab, rows)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0])) if r[j][i] is not None]

    def place(self, prefab, x, y, label=None, rows=None, passable=None, ground=".", force=False, **kw):
        """A prefab at (x, y); its footprint becomes plain ground (or `ground`) and is marked taken."""
        cells = self.cells(prefab, x, y, rows)
        clash = [c for c in cells if c in self.occ]
        if clash and not force:
            raise SystemExit(f"{prefab} at ({x},{y}) overlaps {clash[:4]}")
        for i, j in cells:
            if ground is not None:
                self.g[j][i] = ground
            self.occ.add((i, j))
        b = {"prefab": prefab, "x": x, "y": y, "label": label or prefab.replace("_", " ").capitalize()}
        if rows:
            b["rows"] = rows
        if passable is not None:
            b["passable"] = passable
        b.update(kw)
        self.b.append(b)
        return b

    def ok(self, prefab, x, y, on=".", margin=0):
        """Every cell of the prefab (and `margin` cells round it) is open `on` ground, inside the map, untaken."""
        cs = self.cells(prefab, x, y)
        ring = {(i + dx, j + dy) for i, j in cs for dx in range(-margin, margin + 1) for dy in range(-margin, margin + 1)}
        # an opaque primary piece (lamp, sign, fence) would cut a river bank tile off straight: the bank is
        # drawn in the cell west of / above the water (dual grid), so those cells need dry corners too
        plain = not self.cfg["prefabs"][prefab].get("on_patch") and all(
            isinstance(c, str) for row in self.rows(prefab) for c in row if c is not None)
        wet = plain and any(self.g[j2][i2] in "~w" for i, j in cs for i2, j2 in ((i + 1, j), (i, j + 1), (i + 1, j + 1))
                            if 0 <= i2 < W and 0 <= j2 < H)
        return not wet and all(0 <= i < W and 0 <= j < H for i, j in cs) and all(
            self.g[j][i] in on and (i, j) not in self.occ for i, j in ring if 0 <= i < W and 0 <= j < H)

    def deco(self, prefab, x, y, label=None, margin=0, on="."):
        """A decoration (tree, lamp, bench, bed): placed only where it fits, else noted."""
        if self.ok(prefab, x, y, on, margin):
            ground = None if self.cfg["prefabs"][prefab].get("on_patch") or on != "." else "."
            return self.place(prefab, x, y, label, ground=ground)
        self.skipped.append((prefab, x, y))
        return None

    def grid_text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"


# ---------------------------------------------------------------- streets
def terrain(t):
    for y in range(H):
        t.fill("~", river_west(y), y, RIVER_EAST - river_west(y), 1)
    S = lambda x, y, w, h: t.fill("=", x, y, w, h)
    L = lambda x, y, w, h: t.fill(".", x, y, w, h)
    S(22, 9, 4, 39)         # Capitol Avenue (4 wide; it starts level with the lane), to the Route 4 levee-road exit
    S(3, 9, 19, 2)          # the north-west lane (2 wide) between the two rows of houses
    S(10, 11, 2, 6)         # the block's central walk, on the mirror line (x 10-11), down to Government Street
    S(0, 17, 48, 3)         # Government Street (3 wide): Route 5 exit (west) to the riverfront
    S(45, 5, 3, 23)         # Riverfront Drive: two paved columns and the quay's edge
    S(43, 5, 2, 2)          # ... widening to meet the north bridge
    S(44, 8, 1, 6)          # loading bays beside the cranes (the drive is 4 wide there)
    S(44, 20, 1, 6)
    S(26, 26, 22, 2)        # Laurel Street, on to the south bridge (its deck rows are 26-27)
    S(41, 28, 7, 6)         # the north apron of the working quay
    S(40, 34, 7, 1)         # (the boathouse's roof row stands on paving, not lawn)
    S(37, 28, 2, 16)        # the dock walk: 2 wide, from Laurel Street to the levee road
    S(39, 40, 9, 4)         # the gym's forecourt on the quay
    S(26, 44, 22, 2)        # the levee road along the south, out to the quay
    S(QUAY_X, 9, 1, 39)     # the quay's edge from the north bridge down off the map
    S(57, 5, 9, 2)          # Route 23, east of the north bridge (north-east exit, rows 5-6)
    S(57, 26, 9, 2)         # Route 23's second road, east of the south bridge (east exit, rows 26-27)
    S(61, 7, 2, 19)         # the east-bank riverside walk between the bridges
    S(31, 15, 4, 2)         # Capitol plaza at the foot of the staircase
    S(26, 37, 6, 2)         # the south house's lane off the avenue ...
    S(30, 37, 2, 7)         # ... and its path straight down to the levee road
    # the works: paved floor, Refinery Road out through the east gate, the yard lane down to the sidings
    S(2, 22, 17, 11)
    S(2, 33, 20, 2)
    S(17, 35, 2, 11)
    L(9, 28, 2, 4)          # planted islands in the works' floor
    L(15, 28, 1, 4)
    L(43, 31, 2, 2)         # ... on the working quay's apron
    L(40, 42, 2, 2)         # ... and on the gym's forecourt
    for y in RAIL_ROWS:     # each siding: a 2-high strip (the car's top row and the track), grass between
        S(2, y - 1, 17, 2)


RAIL_ROWS = (38, 41, 44)    # the sidings' track rows


# ---------------------------------------------------------------- buildings
def label_of(key):
    return door_label(key, mock.INTERIORS[key]["title"])


def interiors_before():
    """Door links build_interior.py wrote into the last spec (kept so a rerun doesn't drop them)."""
    if not os.path.exists(SPEC):
        return {}
    old = json.load(open(SPEC, encoding="utf-8"))
    return {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}


BUILDINGS = {  # room key -> top-left cell (prefabs come from town_plans.PLANS)
    "pointe_rouge_house_nw": (4, 2), "pointe_rouge_house_ne": (13, 2),
    "pointe_rouge_capitol_lobby": (28, 1),
    "pointe_rouge_pokecenter": (39, 3), "pointe_rouge_mart": (39, 11),
    "pointe_rouge_refinery": (7, 26),
    "pointe_rouge_tackle_shop": (28, 21), "pointe_rouge_ice_plant": (35, 20),
    "pointe_rouge_house_s": (28, 32), "pointe_rouge_gym": (40, 34),
}
PAVED_YARD = {"pointe_rouge_refinery": None, "pointe_rouge_gym": "=", "pointe_rouge_tackle_shop": ".",
              "pointe_rouge_ice_plant": "."}  # buildings standing on paving
HOUSES_S = ((4, 12), (13, 12))  # the block's lower row (doors shut): a 2x2 grid with the two above, mirrored about x = 11
BLOCK_AXIS = 11


def buildings(t):
    links = interiors_before()
    plan = {k: p for k, _, p, _ in PLANS[KEY]}
    for key, (x, y) in BUILDINGS.items():
        b = t.place(plan[key], x, y, label_of(key), ground=PAVED_YARD.get(key, "."))
        if label_of(key) in links:
            b["interior"] = links[label_of(key)]
    for x, y in HOUSES_S:
        t.place("brick_house", x, y, "House", closed=True)
    # Kingfisher's boat slip: the boathouse stands on the quay, its dock reaching into the river beside it (stepped
    # onto from the quay's edge column)
    gx, gy = BUILDINGS["pointe_rouge_gym"]
    t.place("dock", gx + 8, gy + 5, "Dock", ground=None)
    if FERRY:
        ferry_pier(t, gx + 8, gy + 5)


BOAT_DX = 3             # the riverboat's west column is the column after the dock's last one (dock x .. x+2): a T


def ferry_pier(t, dock_x, dock_y):
    """The ferry berth: Crescent City's riverboat moored north-south across the tip of the gym's dock (the lower pier,
    below the southern bridge), a T: the boat runs between the two cities. The old upper ferry pier is gone (user,
    2026-10-13); the open water east of the boat (x 54-56) keeps a Surf lane."""
    # the boat's middle row (row 3 of its 7) is the dock's first row
    t.place("steamboat_ns_s", dock_x + BOAT_DX, dock_y - 3, "Riverboat", ground=None)


def refinery_works(t):
    """The fenced works: a row of crude tanks behind the north fence, the process house (the refinery's door),
    two distillation columns and the flare stack; Refinery Road leaves through the east gate."""
    P = lambda *a: t.place(*a, ground=None)  # everything stands on the paved yard
    for x in (2, 6, 10, 14):
        P("tank", x, 22, "Crude tank")
    P("column", 14, 26, "Distillation column")
    P("column", 16, 26, "Distillation column")
    P("flare", 18, 26, "Flare stack")
    for x in range(2, 16):  # the pipe rack from the tank farm past the process house to the columns
        P("pipes", x, 25, "Pipe rack")
    P("pipes_end", 16, 25, "Pipe rack")


# one closed fence round the whole works and the rail yard below it: x 1..19, y 21..47. The one gate (an opening with a
# post either side) is Refinery Road in the east side; the three sidings pass through 1-cell gaps in the west fence.
FENCE = (1, 21, 19, 47)


def fence(t, x0, y0, x1, y1, gates=()):
    """The primary's grey post-and-rail fence round a yard (x0..x1, y0..y1): a closed line, corners meeting,
    with openings at `gates` (cells); the posts either side of an opening are end-cap pieces."""
    piece = {}
    for x in range(x0, x1 + 1):
        piece[(x, y0)] = "0ED"
        piece[(x, y1)] = "0FD"
    for y in range(y0 + 1, y1):
        piece[(x0, y)] = "0F4"
        piece[(x1, y)] = "0F5"
    # right corners reuse the runs' own pieces: top-right 0ED (a post pair, the stub under its right post where the east
    # rail comes down), bottom-right 0FD (the stub above its right post). 0EE / 136 left a half cell of rail missing
    piece[(x0, y0)], piece[(x1, y0)], piece[(x0, y1)], piece[(x1, y1)] = "0EC", "0ED", "0FC", "0FD"
    caps_left = {"down": "0EF", "up": "0F7"}     # end posts on the west side: the rail runs below / above them
    caps_right = {"down": "0EE", "up": "0F6"}
    for (x, y) in gates:
        piece.pop((x, y), None)
    for (x, y) in gates:
        if x in (x0, x1):
            caps = caps_left if x == x0 else caps_right
            if (x, y - 1) in piece and (x, y - 1) not in gates and (x, y - 1) not in ((x0, y0), (x1, y0)):
                piece[(x, y - 1)] = caps["up"]
            if (x, y + 1) in piece and (x, y + 1) not in gates and (x, y + 1) not in ((x0, y1), (x1, y1)):
                piece[(x, y + 1)] = caps["down"]
    for (x, y), mid in piece.items():
        if (x, y) in t.occ or t.g[y][x] != ".":
            continue
        t.place("fence", x, y, "Fence", rows=[[mid]])


def compound_fence(t):
    x0, y0, x1, y1 = FENCE
    gates = {(x1, 33), (x1, 34)} | {(x0, y) for y in RAIL_ROWS}   # Refinery Road (east), and a gap where each siding runs out west
    fence(t, x0, y0, x1, y1, gates)


def rail_yard(t):
    """Three sidings from the map's west edge (x 0, out through a gap in the fence) to the yard lane, each with a boxcar or two
    standing on it (the boxcar's bottom row is the track). The track and cars are primary art (gTileset_OrleansGeneral), so they
    may stand in the seam bands of the south and south-west."""
    for y, cars in ((RAIL_ROWS[0], (3, 11)), (RAIL_ROWS[1], (7,)), (RAIL_ROWS[2], (3, 11))):
        for car in cars:
            t.place("rail_car", car, y - 1, "Rail car", ground=None)
        for x in range(0, 17):
            if (x, y) not in t.occ:
                t.place("rail_h", x, y, "Track", ground=None)


def bridges(t):
    """Two balustraded stone arch bridges carry the roads to Route 23: the north one (rows 4-8, deck rows 5-6)
    and the south one, Laurel Street (rows 25-29, deck rows 26-27, Tornadus's span). Each runs from the last land column west of the river to the first one east of it; its deck rows are
    street on land so the paving joins the deck without a kerb.

    A surfer passes under both (build.py's "Bridge" handling): the deck and railings over the water are drawn on
    the top layer; deck cells over water are elevation 15 (bridge-over-pond), railings over water elevation 1,
    the deck on the banks elevation 4, stepping down to the street through one elevation-0 cell. The face under
    the deck is a "Bridge" too (surfers pass under its arches or truss bays) except the two solid abutment
    cells at each end, which block."""
    for y0 in BRIDGE_ROWS.values():
        kind = "stone"  # both crossings are the balustraded stone arch bridge (the owner's pick)
        x0 = min(river_west(y) for y in range(y0, y0 + 5)) - 2   # one column further west: the stone bridge needs an even span and the east end
        # (RIVER_EAST 57) must stay west of the seam band (x >= 58)
        L = RIVER_EAST - x0 + 1
        rows = bridge_rows(kind, L)
        rows = [[("johto:1C1" if c == "1C1" else c) for c in row] for row in rows]  # the deck: paving as top-layer art
        for x in (x0, RIVER_EAST):
            t.g[y0][x] = t.g[y0 + 3][x] = t.g[y0 + 4][x] = "."
            t.g[y0 + 1][x] = t.g[y0 + 2][x] = "="
        for j in (y0, y0 + 3, y0 + 4):  # the west end piers stand on the quayside paving where it runs alongside
            if t.g[j][x0 - 1] == "=":
                t.g[j][x0] = "="
        for j in (y0 - 1, y0 + 5):  # no lily pads beside the bridge (under it the water stays "~": surfable)
            for i in range(x0, RIVER_EAST):
                if t.g[j][i] == "~":
                    t.g[j][i] = "w"
        passable = [[i, j] for j in (1, 2) for i in range(L)]
        t.place("bridge", x0, y0, "Bridge", rows=rows[:4], passable=passable, ground=None, force=True, kind=kind)
        face = rows[4]
        t.place("bridge", x0 + 2, y0 + 4, "Bridge", rows=[face[2:L - 2]], passable=[], ground=None, force=True)
        for fx, part in ((x0, face[:2]), (x0 + L - 2, face[L - 2:])):
            t.place("bridge", fx, y0 + 4, "Bridge abutment", rows=[part], ground=None, force=True)
        t.deck |= {(x0 + i, y0 + j) for i, j in passable}


# ---------------------------------------------------------------- door paths
def door_paths(t):
    """A 2-wide paved path from every door to the nearest street (cheapest way round buildings and
    decorations), then any stretch of street left on its own is joined to the main network."""
    blocked = set(t.occ) - t.deck

    def route(sources, is_goal):
        best, prev = {c: 0 for c in sources}, {}
        heap = [(0, x, y) for x, y in sources]
        heapq.heapify(heap)
        while heap:
            d, x, y = heapq.heappop(heap)
            if d > best.get((x, y), 1e9):
                continue
            if is_goal(x, y):
                line, cell = [(x, y)], (x, y)
                while cell in prev:
                    cell = prev[cell]
                    line.append(cell)
                return line[1:]
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked and t.g[ny][nx] not in "~w":
                    nd = d + 1
                    if nd < best.get((nx, ny), 1e9):
                        best[(nx, ny)], prev[(nx, ny)] = nd, (x, y)
                        heapq.heappush(heap, (nd, nx, ny))
        return []

    def paint(line):
        for x, y in line:  # a 2x2 brush: two wide whichever way the path runs
            for i, j in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                if 0 <= i < W and 0 <= j < H and (i, j) not in blocked and t.g[j][i] == ".":
                    t.g[j][i] = "="

    starts = []
    for b in t.b:
        d = t.cfg["prefabs"][b["prefab"]].get("door")
        if not d:
            continue
        for dx, dy in (d if isinstance(d[0], list) else [d]):
            sx, sy = b["x"] + dx, b["y"] + dy + 1
            starts.append((sx, sy))
            own = {(sx, sy), (sx + 1, sy)}
            paint([(sx, sy)] + route([(sx, sy)], lambda x, y: (t.g[y][x] == "=" or (x, y) in t.deck) and (x, y) not in own))
    join_network(t.g, route, paint, t.deck, starts)
    for x, y in starts:  # the paving runs in under each door and its apron, so no kerb crosses the doorway
        t.g[y - 1][x] = t.g[y - 1][x + 1] = "="
    t.g = [list(r) for r in tidy_paths(["".join(r) for r in t.g], blocked=set(t.occ) - t.deck)]


# ---------------------------------------------------------------- greenery and street furniture
def mirrored(t, prefab, x, y, axis, **kw):
    """A decoration and its mirror image about the vertical line at `axis` (between columns axis-1 and axis)."""
    w = len(t.rows(prefab)[0])
    t.deco(prefab, x, y, **kw)
    mx = int(round(2 * axis - x - w))
    if mx != x:
        t.deco(prefab, mx, y, **kw)


def nw_paths(t):
    """The north-west block: each top house's door gets a 3-wide path (centred on the door) down to the lane, so the
    two paths are mirror images about the block's centre line."""
    for key in ("pointe_rouge_house_nw", "pointe_rouge_house_ne"):
        x, y = BUILDINGS[key]
        d = x + 2
        for i in (d - 1, d, d + 1):
            if t.g[y + 6][i] == ".":
                t.g[y + 6][i] = "="


TALL = {  # the east bank's tall grass: organic patches (x ranges per row), rounded outlines
    30: [(62, 63)], 31: [(61, 64)], 32: [(61, 65)], 33: [(62, 65)], 34: [(63, 64)],
    37: [(62, 63)], 38: [(61, 64)], 39: [(61, 65)], 40: [(61, 64)], 41: [(62, 64)], 42: [(63, 64)],
    44: [(62, 63)], 45: [(61, 64)], 46: [(62, 64)],
}


def tall_grass(t):
    for y, spans in TALL.items():
        for x0, x1 in spans:
            for x in range(x0, x1 + 1):
                if t.g[y][x] == ".":
                    t.g[y][x] = "G"


def dress(t):
    """Magnolias in pairs and groups with their planters, lamps, benches facing something, flower beds: placed by
    hand, mirrored where the town is (no trees in the river)."""
    D, M = t.deco, lambda p, x, y, axis, **kw: mirrored(t, p, x, y, axis, **kw)
    # --- the Capitol's garden: the town's flower beds, a deliberate pair flanking the plaza, lamps at its corners
    cap = BUILDINGS["pointe_rouge_capitol_lobby"][0] + 5
    for y in (15, 16):                   # rose-bush planters (3 wide) flanking the plaza
        for dx in range(3):
            M("roses", cap - 5 + dx, y, cap)
    M("lamp", cap - 6, 15, cap)
    D("magnolia", cap - 7, 10)           # a magnolia with a planter of roses at its foot
    D("roses", cap - 7, 13)
    D("roses", cap - 6, 13)
    # --- pocket park at the head of Capitol Avenue (axis 24: the avenue's centre)
    D("magnolia", 26, 1)                 # (20, 1) is the north-west block's mirror of (0, 1)
    M("lamp", 21, 7, 24)
    D("bench", 23, 7)                    # facing the avenue's head
    # --- north-west block: a 2x2 grid of houses mirrored about x = 11. Staggered magnolia pairs on each flank, a
    # magnolia with roses between the top houses, lamps along the central walk
    M("magnolia", 0, 1, BLOCK_AXIS)
    M("magnolia", 1, 4, BLOCK_AXIS)
    M("magnolia", 1, 12, BLOCK_AXIS)
    D("magnolia", 10, 3)
    for x in (10, 11):
        D("roses", x, 6)
    M("lamp", 9, 13, BLOCK_AXIS)
    # --- Capitol Avenue: magnolia pairs with flower beds, one group each side of each block
    for x, y in ((20, 20), (20, 23), (26, 20), (26, 23), (20, 38), (20, 41)):
        D("magnolia", x, y)
    D("magnolia", 26, 28)
    D("magnolia", 26, 31)
    M("lamp", 21, 46, 24)  # the avenue's south end, at the Route 4 exit
    # --- the Center's back garden
    D("magnolia", 38, 0)
    D("magnolia", 40, 0)
    # --- lamps at the bridgeheads (on the lawns: never on an elevation-4 bridgehead cell)
    for x, y in ((43, 9), (60, 9), (60, 23)):
        D("lamp", x, y)
    # --- east bank north: the riverside walk, trees in pairs, benches facing flower beds
    D("magnolia", 63, 8)
    D("magnolia", 64, 11)
    D("bench", 63, 15)
    for x in (63, 64):
        D("roses", x, 16)
    D("magnolia", 63, 18)
    D("magnolia", 64, 21)
    # --- planters: the islands in the works' floor and on the quay
    for x, y in ((9, 29), (10, 29), (9, 30), (10, 30), (15, 29), (15, 30), (43, 31), (44, 31), (43, 32), (44, 32),
                 (40, 42), (41, 42), (40, 43), (41, 43)):
        D("roses", x, y)
    # --- the lawn south of Laurel Street: a pair of magnolias and a bench facing a flower bed; shrubs by the dock walk
    D("magnolia", 33, 29)
    D("magnolia", 35, 29)
    D("bench", 33, 34)
    for dx in range(3):
        D("roses", 33 + dx, 35)
    # --- the riverside bench on the city bank, facing the street
    D("bench", 43, 15)
    # --- south-west lawn: trees, a bench facing a flower bed
    D("magnolia", 26, 39)
    D("magnolia", 28, 39)
    D("bench", 33, 40)
    for dx in range(3):
        D("roses", 33 + dx, 41)
    # --- south-east bank: tall grass with a pair of magnolias on its rim
    D("magnolia", 60, 34)
    D("magnolia", 64, 35)


def quay(t):
    """The working quay along the city bank: its edge column (walkable, the drop to the river drawn on it) with
    iron bollards here and there, four cranes at the loading bays with their crate clusters beside them."""
    bollards = {12, 17, 23, 31, 42}
    # cranes first: each stands on the paving at the quay's edge (the jib over the water); its east column takes the
    # place of the edge column
    for cy in CRANES:
        t.deco("crane", CRANE_X, cy, "Crane", on="=")
    for y in range(H):
        if t.g[y][QUAY_X] == "=" and (QUAY_X, y) not in t.occ:
            t.place("quay_bollard" if y in bollards else "quay", QUAY_X, y, "Quay", ground=None)
        # the wall's face down to the water, in the river's first column, wherever the quayside runs
        if t.g[y][QUAY_X] == "=" and t.g[y][QUAY_X + 1] in "~w" and (QUAY_X + 1, y) not in t.occ:
            t.place("quay_wall", QUAY_X + 1, y, "Quay wall", ground=None)
    for p, x, y in CRATES:
        t.deco(p, x, y, on="=")


CRANE_X = 46                   # the cranes' west column (x 46-47: the jib overhangs the quay's edge)
CRANES = (9, 21, 30, 41)       # top rows of the four cranes (x 46-47)
CRATES = (                     # crate and barrel clusters beside the cranes (x 44-46: the quay's edge column stays clear)
    ("crates", 46, 12), ("barrels", 46, 13), ("crates", 45, 13),                                  # crane 1
    ("crates", 46, 24), ("barrels", 46, 25), ("crates", 45, 25),                                  # crane 2
    ("barrels", 46, 33), ("crates", 46, 34), ("crates", 45, 33),                                 # crane 3
    ("crates", 45, 30), ("barrels", 45, 31),                                                      # crane 3's other side
    ("crates", 45, 41), ("barrels", 45, 42), ("crates", 44, 43),                                  # crane 4, by the gym's dock
)


def signs(t):
    """Town signs at the three ways in, and the Capitol's plaque."""
    for sid, x, y, text in (
            ("SignWest", 3, 20, "POINTE ROUGE\nCapital on the Emerald River."),
            ("SignEast", 64, 7, "POINTE ROUGE\nThe Capitol is across the river."),
            ("SignSouth", 27, 46, "POINTE ROUGE\nNorth: the Capitol. South: Route 4."),
            ("SignCapitol", 30, 14, "STATE CAPITOL\nObservation deck open to all.")):
        if t.ok("sign", x, y):
            t.place("sign", x, y, "Sign")
            t.signs.append({"id": sid, "x": x, "y": y, "text": text})
        else:
            t.skipped.append(("sign", x, y))


# ---------------------------------------------------------------- people
def people(t):
    """Kingfisher by the river at the boathouse (mockup marker 1) and a few townsfolk; story events (Camille's
    sabotage, the Mega Stones, Articuno and Tornadus) are left to the story pass."""
    folk = [
        ("KINGFISHER", "OBJ_EVENT_GFX_MAN_1", 49, 40, "MOVEMENT_TYPE_FACE_LEFT",
         "KINGFISHER: A badge? Prove you\ncan fish first. Try Route 5's lake!"),
        ("CLERK", "OBJ_EVENT_GFX_GENTLEMAN", 30, 17, "MOVEMENT_TYPE_WANDER_AROUND",
         "The legislature's in session.\nThirty-four floors of arguing!"),
        ("WORKER", "OBJ_EVENT_GFX_WORKER_M", 20, 34, "MOVEMENT_TYPE_FACE_LEFT",
         "Shift change at the refinery.\nSmell that? That's overtime."),
        ("ANGLER", "OBJ_EVENT_GFX_FISHERMAN", 47, 18, "MOVEMENT_TYPE_FACE_RIGHT",
         "The Emerald runs deep here. The\nbig ones hide under the bridge."),
        ("KID", "OBJ_EVENT_GFX_LITTLE_GIRL", 23, 4, "MOVEMENT_TYPE_WANDER_AROUND",
         "The magnolias smell like lemons!"),
        ("RETIREE", "OBJ_EVENT_GFX_OLD_MAN", 63, 13, "MOVEMENT_TYPE_FACE_LEFT",
         "Fifty years I've watched barges\npass this bench. Never the same\\lriver twice."),
        ("CHEMIST", "OBJ_EVENT_GFX_SCIENTIST_1", 6, 32, "MOVEMENT_TYPE_FACE_DOWN",
         "Pressure's steady on column two.\nNobody touch the red valves!"),
        ("YARDMAN", "OBJ_EVENT_GFX_MAN_3", 10, 40, "MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT",
         "Tank cars in, tank cars out.\nThe yard never sleeps."),
        ("LASS", "OBJ_EVENT_GFX_LASS", 9, 15, "MOVEMENT_TYPE_FACE_RIGHT",
         "Our street has the best gardens\nin the whole capital."),
        ("TWIN", "OBJ_EVENT_GFX_TWIN", 37, 42, "MOVEMENT_TYPE_WANDER_AROUND",
         "Kingfisher's POKéMON fly so fast\nthey ripple the river!"),
        ("POKEFAN", "OBJ_EVENT_GFX_POKEFAN_M", 64, 29, "MOVEMENT_TYPE_FACE_LEFT",
         "On windy days something huge\ncircles the truss bridge..."),
        ("SHOPPER", "OBJ_EVENT_GFX_WOMAN_2", 43, 16, "MOVEMENT_TYPE_FACE_LEFT",
         "The Mart's stocked for the session.\nEvery lawmaker wants Potions."),
    ]
    if FERRY:  # Crescent's riverboat has only a sailor on its quay saying where it sails: the same here, at the tip of the lower pier
        folk.append(("SAILOR", "OBJ_EVENT_GFX_SAILOR", BUILDINGS["pointe_rouge_gym"][0] + 10, BUILDINGS["pointe_rouge_gym"][1] + 5, "MOVEMENT_TYPE_FACE_RIGHT",
                     "SAILOR: The riverboat sails for\nCrescent City from this pier."))
    for name, gfx, x, y, move, text in folk:
        on_dock = any(b["prefab"] in ("dock", "quay") and 0 <= x - b["x"] < (3 if b["prefab"] == "dock" else 1)
                      and 0 <= y - b["y"] < (2 if b["prefab"] == "dock" else 1) for b in t.b)
        if not on_dock and ((x, y) in t.occ or t.g[y][x] in "~w"):
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_POINTE_ROUGE_{name}", "gfx": gfx, "x": x, "y": y, "move": move, "text": text})
        t.occ.add((x, y))


REVIEW_AREAS = [  # (title, x0, y0, x1, y1) in tiles: the zoomed crops of the review sheet
    ("11. North-west: 2x2 houses, mirrored", 0, 0, 24, 20),
    ("Capitol, garden plaza, pocket park", 18, 0, 40, 20),
    ("8. Cranes: Center, Mart, bridge (quay)", 36, 0, 66, 14),
    ("9. Fence: works, gates, rail yard", 0, 19, 24, 48),
    ("1/4. Tackle shop, ice plant, Laurel St", 24, 18, 48, 32),
    ("5/7. South: house path, gym on the quay, cranes", 24, 30, 50, 48),
    ("10. East bank: tall grass", 50, 24, 66, 48),
    ("East bank north: benches, tree pairs", 56, 4, 66, 28),
    ("12. Lower pier and Crescent's riverboat", 38, 30, 62, 46),
    ("Rose planters (were flower beds): Capitol, south lawn", 25, 12, 41, 19),
    ("Rail yard: tracks end at the yard lane (no buffer stops)", 12, 36, 22, 47),
]


def review(out):
    """The review sheet: the mockup beside the build, then zoomed crops of every area (no event markers)."""
    from PIL import Image, ImageDraw, ImageFont
    from build import Builder
    from render import Tilesets, render
    b = Builder(SPEC)
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    clean = render(ts, b.flat(), b.w)
    before = Image.open(os.path.join(HERE, "maps", "00_pointe_before_review2.png")).convert("RGB")
    mock = before
    S = 2
    top_h = H * 16 * S
    mock = mock.resize((round(mock.width * top_h / mock.height), top_h))
    full = clean.resize((W * 16 * S, H * 16 * S), Image.NEAREST)
    crops = []
    for title, x0, y0, x1, y1 in REVIEW_AREAS:
        c = clean.crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
        crops.append((title, c.resize((c.width * 3, c.height * 3), Image.NEAREST)))
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    pad, head = 24, 48
    width = mock.width + full.width + 3 * pad
    rows, row, rw = [], [], pad
    for title, c in crops:  # as many crops per row as fit
        if row and rw + c.width + pad > width:
            rows.append(row)
            row, rw = [], pad
        row.append((title, c))
        rw += c.width + pad
    rows.append(row)
    height = head + top_h + pad + sum(max(c.height for _, c in rw_) + head for rw_ in rows) + pad
    sheet = Image.new("RGB", (width, height), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), "BEFORE (round 1)", fill=(0, 0, 0), font=font)
    d.text((mock.width + 2 * pad, 8), f"AFTER (round 2), {W}x{H}", fill=(0, 0, 0), font=font)
    sheet.paste(mock, (pad, head))
    sheet.paste(full, (mock.width + 2 * pad, head))
    y = head + top_h + pad
    for rw_ in rows:
        x = pad
        for title, c in rw_:
            d.text((x, y + 8), title, fill=(0, 0, 0), font=font)
            sheet.paste(c, (x, y + head))
            x += c.width + pad
        y += max(c.height for _, c in rw_) + head
    sheet.save(out)
    print("review sheet:", out, sheet.size)


def main(args):
    t = Town()
    terrain(t)
    buildings(t)
    refinery_works(t)
    compound_fence(t)
    rail_yard(t)
    bridges(t)
    nw_paths(t)
    tall_grass(t)
    dress(t)
    quay(t)
    signs(t)
    door_paths(t)
    people(t)
    if t.skipped:
        print("decorations that didn't fit:", t.skipped)
    dev = "--dev" in args  # a scratch spec (maps/_pt_dev.json): layout work without touching the real map
    gridname = ("_pt_dev" if dev else KEY) + ".grid.txt"
    open(os.path.join(HERE, "maps", gridname), "w").write(t.grid_text())
    if dev:
        old = json.load(open(SPEC, encoding="utf-8"))
        lid, ldir = old["layout"], old["layout_dir"]
    else:
        lid, ldir = shell(NAME, CONST, "city", "MAPSEC_POINTE_ROUGE", "MUS_RG_SILPH", W, H, t.cfg)
    spec = {"_comment": "Pointe Rouge, handmade: generated by pointe.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/05_pointe_rouge.png", "grid": gridname, "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": [], "hidden_items": [],
            "signs": t.signs,
            # the grey post-and-rail fence is an object, not terrain: its post tips against the ground beside it
            # aren't seams (check.py skips these tiles)
            "seam_objects": ["johto:" + k for k in ("0E7", "0EC", "0ED", "0EE", "0EF", "0F4", "0F5", "0F6", "0F7", "0FC", "0FD", "135", "136")],
            "exits": [{"name": "Route 5 (west)", "cells": [[0, 17], [0, 18], [0, 19]]},
                      {"name": "Route 23 (north-east)", "cells": [[65, 5], [65, 6]]},
                      {"name": "Route 23 (east, lower)", "cells": [[65, 26], [65, 27]]},
                      {"name": "Route 4 levee road (south)", "cells": [[x, 47] for x in range(22, 26)]}]}
    if dev:
        dump(os.path.join(HERE, "maps", "_pt_dev.json"), spec)
        return
    dump(SPEC, spec)
    if "--no-build" in args:
        return
    flags = [a for a in args if a in ("--no-blends", "--dry-run")]
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    if "--fresh" in args:  # drop overlay tiles no longer used: start the blends file again
        bf = os.path.join(HERE, "tilesets", CFG + ".blends.json")
        if os.path.exists(bf):
            os.remove(bf)
    if "--no-compose" not in args:  # the art may have changed: compose first, always
        subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "compose.py"), recipe], check=True,
                       capture_output=True)
    for _ in range(4):  # build; when it asks for new overlay tiles, compose them and build again
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), SPEC] + flags, text=True,
                           capture_output=True)
        print(r.stdout.strip(), r.stderr.strip()[-2000:])
        if "transition tiles needed" not in r.stdout or "--no-compose" in args:
            break
        c = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "compose.py"), recipe], text=True,
                           capture_output=True)
        print(c.stdout.strip(), c.stderr.strip()[-1000:])
        if c.returncode:
            return
    c = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "check.py"), SPEC], text=True, capture_output=True)
    print(c.stdout.strip(), c.stderr.strip()[-2000:])
    if "--review" in args:  # the review sheet: mockup, build and zoomed crops
        review(os.path.join(HERE, "maps", "00_pointe_review.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

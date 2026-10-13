"""Storm's Edge (gym 2, the battered port at the river mouth), built by hand from its mockup (03_storms_edge.png):
50 x 38, the mockup at 1.25x, on the orleans_port tileset (make_town_tilesets.py + storms_tileset.py).

usage (from the decomp root):
    python -W ignore tools/mapgen/storms_edge.py [--review] [--no-build] [--fresh] [--dry-run]
writes maps/storms_edge.json + .grid.txt, splices tools/mapgen/story/StormsEdge.inc into the map's scripts.inc,
regenerates the art (make_storms_art.py) and the tileset recipe (make_town_tilesets.py orleans_port), composes,
builds (again while the build asks for new overlay tiles), runs check.py and bridge_check.py; --review writes
maps/00_storms_edge_review.png (mockup | built, zoomed crops). Door warps keep the order of the first pass
(Center, Mart, gym, west/centre stilt houses, market, east stilt house, lighthouse), so the rooms' exits stay
right; build_interior.py relinks them by label all the same.

Layout (x right, y down):
    north-west   the substation (gym): a fenced, paved yard 13 wide (x 0-12) with the Brick City hall, gantries, switch cabinets
                 and the Raichunite X, its gate onto the main road; then the Pokemon Center (running on a generator) with its
                 forecourt, x 14-18. The gym is on the WEST bank (user decision 9, 2026-10-12): the raised drawbridge is the
                 only way to the east bank. The Mart is on the east bank's north lot (38,5)
    downed line  a broken row of utility poles between the Mart and the river: one leaning, one snapped with
                 its top in the grass, wires down
    river        5 wide (x 24-28) between levees down to the drawbridge (rows 11-14), then flaring out to the
                 harbour (rows 16-20)
    drawbridge   map.bin holds it lowered (surf under it); the map script raises it (setmetatile, spec "states")
                 until FLAG_STORMS_EDGE_GRID_RESTORED is set: the leaves stand up, the middle opens, barriers
                 close the deck. Walkers can't cross; surfers pass through the gap.
    substation   (see north-west) the Brick City hall made symmetric, lattice gantries bringing the line in over the fence,
                 switch cabinets either side, Eclair at the gate; the gate opens onto the main road
    waterfront   a dark plank quay along the whole south shore on both sides of the mouth; the three stilt
                 houses stand in the water on piles, steps down from their doors to the quay; the seafood market
                 on the west quay; one long pier from the west quay (the fisherman at its end, a hidden item)
    lighthouse   on a spit reaching south into the harbour from the east shore, a path down its west side
    exits        Route 2 (west) and the Route 3 causeway (east) on the main road, rows 12-13
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from firstpass import bridge_h, dump, item_flag, shell, tidy_paths  # noqa: E402
from town_plans import door_label  # noqa: E402
import interiors as mock  # noqa: E402
import levee  # noqa: E402

KEY, NAME, CONST = "storms_edge", "StormsEdge", "MAP_STORMS_EDGE"
CFG = "orleans_port"
W, H = 50, 38
LEVEE_CAPS = True                # the rounded nose where a levee run ends in the lake (levee_caps)
LEVEE_JET = False                # JET 1: the levee heads reach one cell into the lake (needs levee_caps; costs ~65 port tiles)
LEVEE_X = (22, 23, 29, 30)       # the levee ground columns beside the canal (levee.py marks them); the lake reaches the levees' heads
LEVEE_SHORE_PINS = (21, 31)      # the meadow's shore stays at the levees' row + 1 right beside them (JET 1), then recedes away from them (feather.shore_pins)
TOP, BOT = 4, 2                 # rows of lake added above and of harbour below (user decision 2026-10-13: the north coast recedes into a lake shoreline; the lighthouse spit gets a water margin)
H_FINAL = H + TOP + BOT
SPEC = os.path.join(HERE, "maps", KEY + ".json")
STORY = os.path.join(HERE, "story", NAME + ".inc")
GRID_FLAG = "FLAG_STORMS_EDGE_GRID_RESTORED"

ROAD = (12, 13)                 # the main road's rows (both exits)
RIVER = (24, 28)                # the river's water columns above the mouth
BRIDGE = (22, 11, 8)            # x, y (north rail row), length: deck from bank to bank
# the river flaring into the harbour: first and last water column per row (rows above 16: RIVER)
FLARE = {16: (24, 28), 17: (24, 29), 18: (23, 29), 19: (22, 30), 20: (21, 31)}
SHORE = 21                      # the first row of open water along the south shore (the quays stand on it)
EAST_LAND = {21: (40, 49), 22: (40, 49), 23: (40, 48), 24: (40, 47), 36: (38, 45)}  # the east shore and the spit
EAST_LAND.update({y: (37, 46) for y in range(25, 36)})
YARD = (0, 0, 12, 11)           # the substation's fence: x0, y0, x1, y1 (paving inside); WEST bank (user decision 9, 2026-10-12)
GATE = (5, 7)                   # the yard's gate columns (the hall's porch above it)


class Town:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]
        self.b = []
        self.occ = set()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs, self.items, self.hidden = [], [], [], []
        self.walk = set()       # walkable plank cells (quay, pier, stilt steps) and the bridge deck
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

    def place(self, prefab, x, y, label=None, rows=None, passable=None, ground=None, force=False, **kw):
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

    def free(self, cells, on="."):
        return all(0 <= i < W and 0 <= j < H and (i, j) not in self.occ and self.g[j][i] in on for i, j in cells)

    def deco(self, prefab, x, y, label=None, on="."):
        if self.free(self.cells(prefab, x, y), on):
            return self.place(prefab, x, y, label)
        self.skipped.append((prefab, x, y))
        return None

    def grid_text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"


# ---------------------------------------------------------------- land and water
def terrain(t):
    for y in range(H):
        if y < SHORE:
            wl, wr = FLARE.get(y, RIVER)
            t.fill("~", wl, y, wr - wl + 1, 1)
        else:  # the harbour: open water (no lily pads) save the east shore and the spit
            t.fill("~" if y == SHORE else "w", 0, y, W, 1)
            if y in EAST_LAND:
                x0, x1 = EAST_LAND[y]
                t.fill(".", x0, y, x1 - x0 + 1, 1)
    R = lambda x, y, w, h: t.fill(":", x, y, w, h)
    R(0, ROAD[0], BRIDGE[0], 2)                                  # the main road, west of the bridge
    R(BRIDGE[0] + BRIDGE[2], ROAD[0], W - BRIDGE[0] - BRIDGE[2], 2)  # and east of it, to the causeway
    R(14, 9, 5, 3)            # the Center's forecourt (west bank; x13 stays grass for the welcome sign)
    R(36, 9, 8, 3)            # the Mart's forecourt (east bank: the Mart moved over when the gym took the west lot)
    R(3, 14, 18, 3)           # worn ground along the waterfront behind the houses and the market (a port, not a lawn)
    R(32, 14, 13, 3)          # and on the east side of the lane
    # The lanes cross the strip of open water (row SHORE) and end under the quay's plank row (SHORE+1, drawn over
    # them), so the dirt runs straight into the planks. Dual-grid banks: the tile left of a lane takes its bank from the
    # lane's own cells (rows SHORE, SHORE+1: a straight bank, matching the path's grass verge), but the bank right of a
    # lane would be drawn inside the path tile, so a grass cell stands there (rows SHORE, SHORE+1) as the corridor.
    LB = SHORE + 2 - 14           # lane length from row 14 through the quay's plank row
    R(10, 14, 3, LB)              # the pier lane
    R(15, 20, 2, SHORE + 2 - 20)  # the market's apron, onto the quay
    R(32, 14, 2, LB)              # the east lane down to the east quay
    for x0, x1 in ((13, 14), (17, 17), (34, 34)):  # shore ground beside the lanes (13-14 close the one-cell inlet)
        t.fill(".", x0, SHORE, x1 - x0 + 1, 2)
    # the lighthouse path: off the east quay's end, down the spit's west side, round to the door
    R(40, 21, 2, 5)
    R(37, 26, 2, 10)
    R(37, 25, 5, 2)           # a two-row shoulder where the lane steps west (no hard jog)
    R(37, 34, 5, 2)
    # the substation yard: paving inside the fence, out through the gate to a kerbed end on the road (a one-row
    # break-up ('&') read as rubble at the gate, not as paving wearing out)
    x0, y0, x1, y1 = YARD
    t.fill("%", x0 + 1, y0 + 1, x1 - x0 - 1, y1 - y0 - 1)
    t.fill("%", GATE[0], y1, GATE[1] - GATE[0] + 1, 1)


# ---------------------------------------------------------------- buildings
def label_of(key):
    return door_label(key, mock.INTERIORS[key]["title"])


def interiors_before():
    if not os.path.exists(SPEC):
        return {}
    old = json.load(open(SPEC, encoding="utf-8"))
    return {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}


# room key -> (prefab, top-left); in the first pass's door order (the rooms' exits use these warp numbers)
BUILDINGS = [
    ("storms_edge_pokecenter", "pokecenter", (14, 5)),
    ("storms_edge_mart", "mart", (38, 5)),
    ("storms_edge_gym", "substation", (2, 1)),
    ("storms_edge_house_w", "stilt_house", (1, 17)),
    ("storms_edge_house_c", "stilt_house", (6, 17)),
    ("storms_edge_seafood_market", "brick_shop", (14, 15)),
    ("storms_edge_house_e", "stilt_house", (35, 17)),
    ("storms_edge_lighthouse", "lighthouse", (39, 28)),
]
ON_PAVING = {"storms_edge_gym"}


def buildings(t):
    links = interiors_before()
    for key, prefab, (x, y) in BUILDINGS:
        b = t.place(prefab, x, y, label_of(key), ground=None if key in ON_PAVING or prefab == "stilt_house" else ".")
        if label_of(key) in links:
            b["interior"] = links[label_of(key)]
        if prefab == "stilt_house":
            t.walk.add((x + 1, y + 4))
    t.place("emblem", 6, 5, "Gym emblem", force=True)  # drawn over the hall's brick, above the porch


# ---------------------------------------------------------------- the drawbridge
def bridge(t):
    """The road bridge (bridge.png), surf-under by build.py's Bridge rules, and its raised state for the map
    script: the leaves (columns 24 and 27) stand up, the gap between them (25-26) is open water, a barrier closes
    each stub of deck (23 and 28). Symmetric about the river's middle (x 26.0 on screen: the river's five
    water columns are drawn from 23.5 to 28.5)."""
    x0, y0, L = BRIDGE
    rows, passable = bridge_h(L)
    t.place("pier", x0, y0, "Bridge", rows=rows, passable=passable, force=True, dir="bh")
    t.walk |= {(x0 + i, y0 + j) for i, j in passable}
    raised = []
    for x, col in ((24, 0), (27, 1)):  # the leaves
        raised += [{"x": x, "y": y0 + j, "overlay": f"sbr:{col}_{j}", "collision": 1} for j in range(4)]
    for x in (25, 26):  # the open gap: plain water (surfers keep going; walkers can't reach it)
        raised += [{"x": x, "y": y0 + j, "tile": "terrain", "collision": 0} for j in range(4)]
    for x, col in ((23, 2), (28, 3)):  # the barriers on the deck stubs
        raised += [{"x": x, "y": y0 + 1 + j, "overlay": f"sbr:{col}_{j}", "layer": "normal", "collision": 1}
                   for j in range(2)]
    return {"BridgeRaised": raised}


# ---------------------------------------------------------------- quays and the pier
Q = lambda x, y: {"overlay": f"seq:{x}_{y}", "walk": True}
QP = lambda x, y: {"overlay": f"seq:{x}_{y}"}  # posts: not walkable


def quay(t, x0, x1, pier=None):
    """A plank quay over the water along the south shore: rows SHORE+1 (its landward beam) and SHORE+2 (its fascia),
    posts in the water under it; a strip of open water (row SHORE) runs between it and the bank, under the stilt
    houses; the lanes come down to it as dirt. `pier`: the columns where the long pier leaves it."""
    n = x1 - x0 + 1
    rows, passable = [], []
    for j in range(3):
        row = []
        for i in range(n):
            x = x0 + i
            col = 0 if i == 0 else 2 if i == n - 1 else 1
            on_pier = pier and pier[0] <= x <= pier[1]
            if j == 2 and on_pier:
                row.append(None)
                continue
            if j == 1 and on_pier:
                row.append(Q(1, 1))
            elif j == 2:
                row.append(QP(col, 3))
            else:
                row.append(Q(col, 0 if j == 0 else 2))
            if j < 2:
                passable.append([i, j])
        rows.append(row)
    t.place("quay", x0, SHORE + 1, "Quay", rows=rows, passable=passable, force=True)
    t.walk |= {(x0 + i, SHORE + 1 + j) for i, j in passable}


def pier(t, x0, y0, length):
    """The long pier: 3 wide, boards across, an end with its fascia, posts in the water under the end."""
    rows = [[Q(3, 0), Q(4, 0), Q(5, 0)] for _ in range(length - 1)] + [[Q(3, 1), Q(4, 1), Q(5, 1)]]
    rows.append([QP(3, 2), QP(4, 2), QP(5, 2)])
    passable = [[i, j] for j in range(length) for i in range(3)]
    t.place("quay", x0, y0, "Pier", rows=rows, passable=passable, force=True)
    t.walk |= {(x0 + i, y0 + j) for i, j in passable}


def waterfront(t):
    quay(t, 2, 19, pier=(10, 12))      # starts at x 2 so the planks do not run flush into the Route 2 seam (water meets water there)
    quay(t, 32, 39)
    pier(t, 10, SHORE + 3, 9)


# ---------------------------------------------------------------- the substation yard
def fence(t, x0, y0, x1, y1, gates=()):
    piece = {}
    for x in range(x0, x1 + 1):
        piece[(x, y0)] = "0ED"
        piece[(x, y1)] = "0FD"
    for y in range(y0 + 1, y1):
        piece[(x0, y)] = "0F4"
        piece[(x1, y)] = "0F5"
    piece[(x0, y0)], piece[(x1, y0)], piece[(x0, y1)], piece[(x1, y1)] = "0EC", "0EE", "0FC", "136"
    for (x, y), mid in sorted(piece.items()):
        if (x, y) in gates or (x, y) in t.occ:
            continue
        t.place("fence", x, y, "Fence", rows=[[mid]])


def substation(t):
    """Symmetric about the hall's middle (x 6): gantries by the side fences bring the line in over the top fence,
    a switch cabinet below each, danger signs on the fence either side of the gate. (The yard is 13 wide on the west
    bank, so the east design's transformer pairs beside the hall had no room.)"""
    x0, y0, x1, y1 = YARD
    fence(t, x0, y0, x1, y1, gates={(x, y1) for x in range(GATE[0], GATE[1] + 1)})
    for side, gx in (("l", x0 + 1), ("r", x1 - 1)):
        t.place(f"gantry_{side}", gx, 1, "Gantry")
        t.place(f"fence_wires_{side}", gx, 0, "Line over the fence", force=True)
        t.place(f"cabinet_{side}", gx, 5, "Switch cabinet")
    for x in (GATE[0] - 2, GATE[1] + 2):
        t.place("fence_sign", x, y1, "Danger sign", force=True)


# ---------------------------------------------------------------- the downed line
def downed_line(t):
    """The art's 3x12 scene at x 19-21, rows 0-11; empty cells are left out, the poles and the fallen top block."""
    from PIL import Image
    im = Image.open(os.path.join(HERE, "sources", "orleans_custom", "storms_poles.png")).convert("RGB")
    rows, passable = [], []
    for j in range(12):
        row = []
        for i in range(3):
            cell = im.crop((i * 16, j * 16, i * 16 + 16, j * 16 + 16))
            px = [p for p in cell.getdata() if p != (255, 0, 255)]
            if not px:
                row.append(None)
                continue
            row.append({"overlay": f"spl:{i}_{j}"})
            # walk past the loose wires; the poles and the fallen top (wood colours) block
            wood = sum(1 for p in px if p in ((78, 56, 40), (98, 70, 48), (52, 40, 34), (156, 118, 80)))
            if wood < 6:
                passable.append([i, j])
        rows.append(row)
    t.place("downed_line", 19, 0, "Downed line", rows=rows, passable=passable)


# ---------------------------------------------------------------- dressing
def dress(t):
    D = t.deco
    D("generator", 14, 4)                              # the Center runs on it (behind the Center, its cable to the wall)
    D("lamp", 13, 9)                                   # lamps at the forecourts' ends
    D("lamp", 35, 9)
    D("lamp", 44, 9)
    D("bench", 36, 8)                                  # beside the Mart
    D("barrel", 45, 10)                                # a few crates by the Mart, where the delivery trucks stop
    D("crates", 45, 9)
    # by the market and at the lanes down to the quays: crates, barrels, crab traps (on land beside the planks)
    for prefab, x, y in (("crates", 13, 19), ("barrel", 13, 18), ("crates", 20, 19),
                         ("crates", 31, 19), ("barrel", 34, 19)):      # (the crab traps went: 4 port tiles, the lake-end levee heads need them)
        D(prefab, x, y)
    # benches looking out over the harbour (the spit, the east shore)
    D("bench", 44, 35)
    D("bench", 43, 22)
    # storm debris in the harbour
    for prefab, x, y in (("cypress_small_water", 4, 29), ("cypress_small_water", 30, 31), ("cypress_small_water", 23, 27),
                         ("cypress_small_water", 16, 33), ("cypress_small_water", 36, 35)):      # (logs and snags cost port tiles; the cypress is the primary's)
        D(prefab, x, y, "Water prop", on="w")


def signs(t):
    for sid, x, y, text in (
            ("SignWest", 13, 11, "STORM'S EDGE\nThe port at the river's mouth."),
            ("SignEast", 46, 14, "STORM'S EDGE\nWest: the drawbridge. East: Route 3."),
            ("SignLighthouse", 42, 25, "STORM'S EDGE LIGHT\nKeep off the rocks below."),
            ("SignSubstation", GATE[0] - 2, YARD[3], "STORM'S EDGE SUBSTATION\nDANGER: HIGH VOLTAGE. GYM INSIDE.")):
        if (x, y) not in t.occ:
            if not t.free([(x, y)]):
                t.skipped.append(("sign", x, y))
                continue
            t.place("sign", x, y, "Sign")
        t.signs.append({"id": sid, "x": x, "y": y, "text": text})


# ---------------------------------------------------------------- people and items
def people(t):
    folk = [
        ("ECLAIR", "OBJ_EVENT_GFX_WORKER_F", 8, 10, "MOVEMENT_TYPE_FACE_DOWN",
         "ECLAIR: The whole grid tripped when\nthe storm hit. Help me bring it back\\pand we'll talk about a badge."),
        ("BRIDGE_TENDER", "OBJ_EVENT_GFX_WORKER_M", 21, 14, "MOVEMENT_TYPE_FACE_UP",
         "The surge fried the bridge motor.\nShe stays up till the power's back."),
        ("FISHERMAN", "OBJ_EVENT_GFX_FISHERMAN", 11, SHORE + 11, "MOVEMENT_TYPE_FACE_DOWN",
         "After a blow the fish crowd the\nriver mouth. Got a rod, kid?"),
        ("LINEMAN", "OBJ_EVENT_GFX_MAN_2", 17, 3, "MOVEMENT_TYPE_FACE_RIGHT",
         "Three poles down in one night.\nStay clear of those wires!"),
        ("KID", "OBJ_EVENT_GFX_LITTLE_BOY", 16, 10, "MOVEMENT_TYPE_WANDER_AROUND",
         "The Pokémon Center runs on a\ngenerator now. Chug chug chug!"),
        ("FISHMONGER", "OBJ_EVENT_GFX_WOMAN_2", 13, 17, "MOVEMENT_TYPE_FACE_RIGHT",
         "Shrimp's cheap today. Half the\nboats are still tied up."),
        ("SAILOR", "OBJ_EVENT_GFX_SAILOR", 42, 21, "MOVEMENT_TYPE_FACE_LEFT",
         "The surge came right up to the\nstilts. That's what they're for!"),
        ("GRANNY", "OBJ_EVENT_GFX_OLD_WOMAN", 4, 15, "MOVEMENT_TYPE_FACE_DOWN",
         "We raised our houses after the last\nbig storm. Saved us again."),
        ("KEEPER", "OBJ_EVENT_GFX_OLD_MAN", 44, 30, "MOVEMENT_TYPE_FACE_LEFT",
         "My lamp's been dark since the storm.\nShips can't find the mouth at night."),
        ("DECKHAND", "OBJ_EVENT_GFX_SAILOR", 30, 14, "MOVEMENT_TYPE_FACE_LEFT",
         "The bridge motor's fried. Nothing\ncrosses till the grid is back."),
        ("BOY", "OBJ_EVENT_GFX_BOY_1", 42, 17, "MOVEMENT_TYPE_WANDER_AROUND",
         "Eclair's crew hasn't left the\nsubstation in days. It hums!"),
    ]
    for name, gfx, x, y, move, text in folk:
        ok = (x, y) in t.walk or ((x, y) not in t.occ and t.g[y][x] in ".:%")
        if not ok:
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_STORMS_EDGE_{name}", "gfx": gfx, "x": x, "y": y, "move": move,
                          "text": text})
        t.occ.add((x, y))
    # the Raichunite X in the substation yard (mockup marker 3), and the pier's hidden item (marker 5)
    t.items.append({"x": 11, "y": 8, "item": "ITEM_RAICHUNITE_X", "flag": item_flag(CONST, "raichunite_x"),
                    "_comment": "Mega Stone (mockup 3): meant to be found after the grid is restored (story pass)"})
    t.occ.add((11, 8))
    t.hidden.append({"x": 10, "y": SHORE + 6, "item": "ITEM_PEARL", "flag": "FLAG_HIDDEN_ITEM_STORMS_EDGE_PIER"})


# ---------------------------------------------------------------- levees, tidy
def finish(t):
    """Paths the autotile can draw, then the levee ground along the river above the bridge (levee.py)."""
    blocked = {c for c in t.occ if c not in t.walk} | t.walk
    blocked |= {(x, y) for y in range(H) for x in range(W) if t.g[y][x] in "%&"}  # the yard keeps its shape
    breakup = [(x, y) for y in range(H) for x in range(W) if t.g[y][x] == "&"]
    t.g = [list(r) for r in tidy_paths(["".join(r) for r in t.g], blocked=blocked)]
    for x, y in breakup:  # tidy_paths only knows ':' and '=' as road
        t.g[y][x] = "&"
    grow(t)                      # the lake above and the harbour below go in BEFORE the levee is marked: the canal then opens into the lake and the levee fades out there
    x0, y0, L = BRIDGE
    y0 += TOP
    near = {(x, y) for x in range(x0 - 1, x0 + L + 1) for y in range(y0 - 1, y0 + 5)}
    grid = levee.mark(["".join(r) for r in t.g], t.occ | near, KEY)
    t.g = [list(r) for r in grid]
    for x in (LEVEE_X if LEVEE_JET else ()):            # JET 1: each levee reaches one cell past the meadow's shore, into the lake (art: make_levee_caps)
        t.g[TOP - 1][x] = "B"


def grow(t):
    """Everything moves down TOP rows (the road, the bridge and every exit keep their relation to each other); TOP rows of lake go in above
    (the canal opens into it: the water columns just continue) and BOT rows of harbour below. The map's connections move with it (world.WORLD)."""
    t.g = [["~"] * W for _ in range(TOP)] + t.g + [["w"] * W for _ in range(BOT)]
    for b in t.b:
        b["y"] += TOP
    for coll in (t.objects, t.signs, t.items, t.hidden):
        for o in coll:
            o["y"] += TOP
    t.walk = {(x, y + TOP) for x, y in t.walk}
    t.occ = {(x, y + TOP) for x, y in t.occ}


def story_scripts():
    """The map scripts (outside build.py's generated block): the drawbridge stays raised until the grid is
    restored. Written to tools/mapgen/story/StormsEdge.inc (story.py's convention) and spliced in here."""
    text = f"""{NAME}_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, {NAME}_OnLoad
	.byte 0

@ The drawbridge: map.bin has it lowered (surfers pass under it). Until the power grid is restored
@ ({GRID_FLAG}, set by the gym trial in the story pass) the raised state is swapped in: both leaves up, the
@ middle open (surfable), barriers across the deck stubs. {NAME}_EventScript_StateBridgeRaised is written by
@ build.py from the spec's "states" (storms_edge.py), so its metatile ids always match the composed tileset.
{NAME}_OnLoad:
	call_if_unset {GRID_FLAG}, {NAME}_EventScript_StateBridgeRaised
	end
"""
    os.makedirs(os.path.dirname(STORY), exist_ok=True)
    with open(STORY, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    target = os.path.join("data", "maps", NAME, "scripts.inc")
    begin = "@ --- mapgen: generated NPC scripts (begin) ---"
    cur = open(target, encoding="utf-8").read() if os.path.exists(target) else ""
    generated = cur[cur.index(begin):] if begin in cur else ""
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.rstrip("\n") + "\n\n" + generated)


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [  # (title, x0, y0, x1, y1, raised?)
    ("Substation yard (gym), Center, downed line", 0, 0, 24, 15, False),
    ("Drawbridge lowered", 17, 7, 34, 18, False),
    ("Drawbridge raised (until the grid is restored)", 17, 7, 34, 18, True),
    ("River mouth and the lighthouse spit", 18, 14, 50, 38, False),
    ("The long pier", 4, 19, 20, 35, False),
    ("Stilt houses and the west quay", 0, 14, 22, 26, False),
    ("East quay and stilt house", 28, 14, 44, 26, False),
    ("East bank: the Mart", 30, 0, 50, 15, False),
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
    raised = [list(r) for r in b.blocks]
    for x, y, mid, coll in b.state_cells.get("BridgeRaised", []):
        raised[y][x] = (raised[y][x] & ~0x7FF) | mid
    up = render(ts, [v for r in raised for v in r], b.w).convert("RGB")
    subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "town_sheet.py"), KEY,
                    os.path.join(HERE, "maps", "00_town_storms_edge.png")], check=True)
    top = Image.open(os.path.join(HERE, "maps", "00_town_storms_edge.png")).convert("RGB")
    crops = []
    for title, x0, y0, x1, y1, r in REVIEW_AREAS:
        c = (up if r else clean).crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
        crops.append((title, c.resize((c.width * 3, c.height * 3), Image.NEAREST)))
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    pad, head = 24, 48
    width = max(top.width, 2400)
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
    r = subprocess.run([sys.executable, "-W", "ignore"] + args, text=True, capture_output=True, **kw)
    return r


def main(args):
    # the art and the tileset config first: the layout below reads the prefabs from the config
    print(run([os.path.join(HERE, "sources", "orleans_custom", "make_storms_art.py")]).stdout.strip())
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-300:])
    t = Town()
    terrain(t)
    buildings(t)
    states = bridge(t)
    waterfront(t)
    substation(t)
    downed_line(t)
    dress(t)
    signs(t)
    people(t)
    finish(t)
    states = {k: [dict(c, y=c["y"] + TOP) for c in v] for k, v in states.items()}
    if t.skipped:
        print("left out (no room):", t.skipped)
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write(t.grid_text())
    lid, ldir = shell(NAME, CONST, "town", "MAPSEC_STORMS_EDGE", "MUS_RG_VERMILLION", W, H_FINAL, t.cfg)
    spec = {"_comment": "Storm's Edge, handmade: generated by storms_edge.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/03_storms_edge.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": t.items, "hidden_items": t.hidden,
            "signs": t.signs, "states": states, "levee_caps": LEVEE_CAPS,
            "feather": {"shore_pins": {"N": {str(x): 4 for x in LEVEE_SHORE_PINS}}},
            "exits": [{"name": "Route 2 (west)", "cells": [[0, ROAD[0] + TOP], [0, ROAD[1] + TOP]]},
                      {"name": "Route 3 causeway (east)", "cells": [[W - 1, ROAD[0] + TOP], [W - 1, ROAD[1] + TOP]]}]}
    dump(SPEC, spec)
    if "--no-build" in args:
        return
    if "--dry-run" not in args and not os.path.exists(STORY):  # the story pass owns the file once it exists
        story_scripts()
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    if "--fresh" in args:  # start the overlay requests over, so pieces no longer used don't take tiles
        bf = os.path.join(HERE, "tilesets", CFG + ".blends.json")
        if os.path.exists(bf):
            with open(bf, "w") as f:
                json.dump([], f)
    flags = [a for a in args if a == "--dry-run"]
    composed = None
    for i in range(5):  # build (writes the uses file and asks for overlays), compose, build again
        r = run([os.path.join(HERE, "build.py"), SPEC] + flags)
        print(r.stdout.strip(), r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = run([os.path.join(HERE, "compose.py"), recipe])
        composed = c.stdout.strip()
        print(composed[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return
    c = run([os.path.join(HERE, "check.py"), SPEC])
    print(c.stdout.strip()[-3000:], c.stderr.strip()[-2000:])
    c = run([os.path.join(HERE, "bridge_check.py"), SPEC])
    print(c.stdout.strip()[-1500:], c.stderr.strip()[-1000:])
    if "--review" in args:
        review(os.path.join(HERE, "maps", "00_storms_edge_review.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

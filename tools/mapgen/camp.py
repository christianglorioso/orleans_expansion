"""Camp Cocodrie (gym 5, the swamp fishing camp), built by hand from its mockup (06_camp_cocodrie.png): 50 x 35 on the
orleans_camp tileset (make_town_tilesets.py + camp_tileset.py).

usage (from the decomp root; takes the build lock first, see buildlock.py):
    python -W ignore tools/mapgen/camp.py [--review] [--no-build] [--fresh] [--dry-run]
writes maps/camp_cocodrie.json + .grid.txt, regenerates the art (sources/orleans_custom/make_camp_art.py) and the
tileset recipe (make_town_tilesets.py orleans_camp), composes and builds (again while the build asks for new overlay
tiles), runs check.py; --review writes maps/00_camp_cocodrie_review.png and maps/camp_crops/*.png (mockup | built and 3x
crops). Then build_interior.py relinks the door warps to their rooms (labels from town_plans.PLANS["camp_cocodrie"]).
Edit this file, never maps/camp_cocodrie.json. Pieces without art yet use stand-ins of the same footprint
(camp_tileset.py): the layout doesn't change when the art lands.

Layout (x right, y down):
    spine      ONE boardwalk, 2 wide (y 15-16) from the west end (x 2) to the Route 9 landing on the east edge (x 49,
               rows 14-17, 4 wide there). Every door is reached by a 1-wide boardwalk branch: the north cabins and
               the cookhouse by a stub straight down, the south buildings (doors face south) by an L: down the
               building's west side and along a front deck under the doors. No dirt anywhere in the camp.
    north      west marsh with two stilt cabins, fish racks, cypress, the old neighbour's file; the Brothers'
               cookhouse (the Moomoo barn lengthened, chimney, gumbo pot, wood) on the grass yard; the gator pen
               (a mud flat in a rail fence); the pond; a stilt cabin on its west bank in its own marsh; the okra
               garden; the east marsh with the fourth cabin.
    south      a marsh shore (y 17-24) with the Nurse Cabin, Bait Shack, Smokehouse and Dance Porch on stilts, their
               front decks along y 23; the south pier (2 wide, x 24-25) to the airboat dock
    lake       open water (y 25-34): two moored skiffs, a pirogue, a trap line, cypress and logs
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from firstpass import dump, item_flag, shell  # noqa: E402
from town_plans import door_label  # noqa: E402
import interiors as mock  # noqa: E402

KEY, NAME, CONST = "camp_cocodrie", "CampCocodrie", "MAP_CAMP_COCODRIE"
CFG = "orleans_camp"
W, H = 50, 35
SPEC = os.path.join(HERE, "maps", KEY + ".json")

SPINE_Y = (15, 16)              # the spine's rows
LANDING_ROWS = (14, 17)         # the east landing's extra rows (the plaza; the Route 9 exit is rows 15-16 at x 49)
LANDING_X = 43                  # where the spine widens into the landing
LANDING_END = 46                # ... and where the 4-wide plaza ends: the last cells to the edge are the spine's 2 (Route 9's gangway is 2 wide)
SPINE_X = (2, 49)
SHORE_Y = (17, 24)              # the marsh shore band (first, last row); open water from row 25
DECK_Y = 23                     # the south buildings' front deck
PIER_X = (24, 25)               # the south pier: 2 wide, from the spine to the airboat dock
PIER_Y = (17, 26)
MARSH_W = (0, 0, 14, 13)        # west marsh: x0, y0, x1, y1 (cells)
MARSH_E = (45, 0, 49, 13)       # east marsh
MARSH_C3 = (30, 8, 35, 13)      # cabin 3's own marsh pocket (west of the pond)
MUD = (29, 1, 36, 6)            # the gator pen's mud flat (cells); its fence runs round the border tiles
POND = (38, 7, 44, 12)          # water cells
OKRA = (38, 1, 43, 4)           # the okra garden (cells)

# door-bearing buildings, in the first pass's warp order (the rooms' exits use these warp numbers):
# room key -> (prefab, top-left)
BUILDINGS = [
    ("camp_cocodrie_gym", "cookhouse", (16, 5)),
    ("camp_cocodrie_cabin_1", "cabin_a", (3, 8)),
    ("camp_cocodrie_cabin_2", "cabin_a_m", (8, 8)),
    ("camp_cocodrie_cabin_3", "cabin_a", (32, 8)),
    ("camp_cocodrie_cabin_4", "cabin_a_m", (45, 8)),
    ("camp_cocodrie_nurse_cabin", "nurse", (5, 18)),
    ("camp_cocodrie_bait_shack", "bait", (16, 18)),
    ("camp_cocodrie_smokehouse", "smokehouse", (30, 18)),
    ("camp_cocodrie_dance_porch", "porch", (37, 18)),
]
# front-deck extents (x0, x1) for the south buildings, and the x of their hook (the boardwalk down their west side)
DECKS = {"camp_cocodrie_nurse_cabin": (4, 10), "camp_cocodrie_bait_shack": (15, 20),
         "camp_cocodrie_smokehouse": (29, 34), "camp_cocodrie_dance_porch": (36, 44)}


class Town:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]
        self.b = []
        self.occ = set()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs, self.items, self.hidden = [], [], [], []
        self.walk = set()       # walkable plank cells (spine, branches, decks, pier)
        self.skipped = []
        self.stand_ins = set()

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
        """The dual-grid corner cells of every tile in `cells` (x..x+1, y..y+1)."""
        return {(i + dx, j + dy) for i, j in cells for dx in (0, 1) for dy in (0, 1)}

    def inside(self, cells, ch):
        """Every tile's four corner cells are terrain `ch`: the object stands wholly inside the patch."""
        return all(self.at(i, j) == ch for i, j in self.corners(cells))

    def deco(self, prefab, x, y, label=None, on=".", inside=False, ring=0, **kw):
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


# ---------------------------------------------------------------- land and water
def terrain(t):
    t.fill("~", 0, SHORE_Y[1] + 1, W - 1, H - 1)                       # the lake
    t.fill('"', 0, SHORE_Y[0], W - 1, SHORE_Y[1])                      # the marsh shore
    for x0, y0, x1, y1 in (MARSH_W, MARSH_E, MARSH_C3):
        t.fill('"', x0, y0, x1, y1)
    t.fill("L", *MUD)                                                  # the gator pen's mud flat
    t.fill("~", *POND)


# ---------------------------------------------------------------- buildings
def label_of(key):
    return door_label(key, mock.INTERIORS[key]["title"])


def interiors_before():
    if not os.path.exists(SPEC):
        return {}
    old = json.load(open(SPEC, encoding="utf-8"))
    return {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}


def buildings(t):
    links = interiors_before()
    for key, prefab, (x, y) in BUILDINGS:
        b = t.place(prefab, x, y, label_of(key))
        if label_of(key) in links:
            b["interior"] = links[label_of(key)]
    # the cookhouse's dressing: a stovepipe over the roof (drawn over the barn's roof cells), the gumbo pot by the
    # door side, the wood store
    gx, gy = BUILDINGS[0][2][0], BUILDINGS[0][2][1]
    if t.have("chimney"):
        t.place("chimney", gx + 6, gy - 1, "Chimney", force=True)
    t.deco("pot", gx + 10, gy + 4, "Gumbo pot", on=".")
    t.deco("woodpile", gx + 10, gy + 6, "Wood", on=".")


# ---------------------------------------------------------------- the boardwalk
def boardwalk(t):
    """Collect every boardwalk cell with its orientation, then give each cell the piece its neighbours ask for:
    a side is open ('o') toward a neighbour of the same orientation, a seam ('s') toward the other orientation,
    closed ('c': rim, stringer or fascia) toward anything else. Door and steps cells count as walks continuing
    north-south, so the stub's end opens toward them."""
    bw = {}
    for y in SPINE_Y:
        for x in range(SPINE_X[0], SPINE_X[1] + 1):
            bw[(x, y)] = "h"
    for x in range(LANDING_X, LANDING_END + 1):
        for y in LANDING_ROWS:
            bw[(x, y)] = "h"                    # the landing: four rows wide at the Route 9 edge
    # stubs to the north doors (the cell below each steps cell, down to the spine)
    steps = {}
    for key, prefab, (x, y) in BUILDINGS:
        info = t.cfg["prefabs"][prefab]
        door = info["door"]
        dx, dy = (door[0], door[1]) if not isinstance(door[0], list) else door[0]
        steps[(x + dx, y + dy)] = "door"
        low = max([y + dy] + [y + cy for cx, cy in info.get("passable", []) if cx == dx])  # below the steps cell
        for j in range(low + 1, SPINE_Y[0]):
            bw[(x + dx, j)] = "v"
    # the south buildings: an L round the west side and under the doors
    for key, prefab, (x, y) in BUILDINGS[5:]:
        x0, x1 = DECKS[key]
        for j in range(SPINE_Y[-1] + 1, DECK_Y):
            bw[(x0, j)] = "v"
        for i in range(x0, x1 + 1):
            bw[(i, DECK_Y)] = "h"
    # the south pier
    for x in range(PIER_X[0], PIER_X[1] + 1):
        for y in range(PIER_Y[0], PIER_Y[1] + 1):
            bw[(x, y)] = "v"
    # the steps cells (walk cells of the buildings) continue the walks
    virtual = {}
    for key, prefab, (x, y) in BUILDINGS:
        info = t.cfg["prefabs"][prefab]
        for cx, cy in info.get("passable", []):
            virtual[(x + cx, y + cy)] = "v"
        d = info["door"]
        dd = [d] if not isinstance(d[0], list) else d
        for cx, cy in dd:
            virtual[(x + cx, y + cy)] = "v"
    for (x, y), o in sorted(bw.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        def side(nx, ny):
            n = bw.get((nx, ny)) or virtual.get((nx, ny))
            if n is None:
                return "c"
            return "o" if n == o else "s"
        sides = side(x, y - 1) + side(x, y + 1) + side(x - 1, y) + side(x + 1, y)
        name = f"bw_{o}_{sides}"
        plain = (o == "h" and sides[2:] == "oo") or (o == "v" and sides[:2] == "oo")
        if plain and (x + y) % 2 and t.have(name + "_1"):
            name += "_1"
        if not t.have(name):
            raise SystemExit(f"boardwalk piece {name} missing at ({x},{y})")
        t.place(name, x, y, "Boardwalk", passable=[[0, 0]])
        t.walk.add((x, y))
    for c in virtual:
        t.walk.add(c)


# ---------------------------------------------------------------- the gator pens and the okra garden
def pen(t):
    """The pen's fence runs round the mud flat's border tiles (the ring one tile wider than the mud cells on the
    left/top and standing on the last mud column/row on the right/bottom: dual grid), a gate in the middle of the
    south side; gators lie in the mud."""
    x0, y0, x1, y1 = MUD
    fx0, fy0, fx1, fy1 = x0 - 1, y0 - 1, x1, y1
    gate = (fx0 + fx1) // 2
    for x in range(fx0, fx1 + 1):
        for y, kind in ((fy0, "n"), (fy1, "s")):
            piece = {"n": "pen_h", "s": "pen_h"}[kind]
            if x in (fx0, fx1):
                piece = "pen_" + kind + ("w" if x == fx0 else "e")
            elif kind == "s" and x == gate:
                piece = "pen_gate"
            if t.have(piece):
                t.place(piece, x, y, "Pen fence")
    for y in range(fy0 + 1, fy1):
        for x in (fx0, fx1):
            if t.have("pen_v"):
                t.place("pen_v", x, y, "Pen fence")
    # gators in the mud (interior tiles x 29-35, y 1-5)
    for prefab, x, y in (("gator", 30, 2), ("gator_b", 33, 3), ("gator", 30, 4), ("gator_eyes", 35, 2),
                         ("gator_eyes", 34, 5)):
        t.deco(prefab, x, y, "Gator", on="L")


def garden(t):
    """Tidy okra rows: vertical stripes, two crop variations alternating by column."""
    x0, y0, x1, y1 = OKRA
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            t.deco("okra" if (x - x0) % 2 == 0 else "okra_b", x, y, "Okra")


# ---------------------------------------------------------------- dressing
def dress(t):
    D = t.deco
    # fish racks by the west cabins, net racks and the wood store by the south buildings
    for prefab, x, y in (("fishrack", 12, 10), ("fishrack", 0, 10), ("netrack", 22, 19), ("netrack", 27, 19),
                         ("woodpile", 34, 21)):
        D(prefab, x, y, on='."')
    # lanterns along the spine's south side
    for x in (8, 12, 20, 28, 34, 42):
        D("lantern", x, SPINE_Y[-1] + 1, on='"')
    # cypresses and reeds in the marshes (wholly inside the marsh)
    for prefab, x, y in (("cypress_small_marsh", 1, 0), ("cypress_small_marsh", 8, 1), ("cypress_small_marsh", 5, 2),
                         ("cypress_small_marsh", 12, 3), ("cypress_small_marsh", 0, 4), ("cypress_small_marsh", 46, 0),
                         ("cypress_small_marsh", 47, 3), ("reeds_marsh", 4, 5), ("reeds_marsh", 9, 5),
                         ("reeds_marsh", 13, 7), ("reeds_marsh", 46, 6), ("reeds_marsh", 2, 19),
                         ("reeds_marsh", 12, 21), ("reeds_marsh", 21, 22), ("reeds_marsh", 27, 21),
                         ("reeds_marsh", 46, 21), ("cypress_small_marsh", 46, 19), ("cypress_small_marsh", 1, 19)):
        D(prefab, x, y, on='"', inside=True)
    # magnolias on the yard
    for x, y in ((16, 1), (24, 1)):
        D("magnolia", x, y)
    # the lake: moored skiffs and a pirogue, a trap line, cypress and logs
    water = "~"
    for prefab, x, y in (("skiff", 12, 26), ("mooring_post", 11, 26), ("skiff", 33, 26), ("mooring_post", 32, 26),
                         ("pirogue", 20, 27), ("pirogue", 40, 27), ("bollard", 23, 26)):
        D(prefab, x, y, "Water prop", on=water, inside=True)
    for prefab, x, y in (("buoy", 9, 30), ("buoy", 29, 29), ("buoy", 16, 32)):
        D(prefab, x, y, "Water prop", on=water, inside=True)
    for x in range(14, 23):                                            # the trap line
        D("trapline_h", x, 29, "Trap line", on=water, inside=True)
    D("trapline_end", 23, 29, "Trap line", on=water, inside=True)
    for x in range(38, 45):
        D("trapline_h", x, 28, "Trap line", on=water, inside=True)
    D("trapline_end", 45, 28, "Trap line", on=water, inside=True)
    for prefab, x, y in (("cypress_small_water", 31, 30), ("cypress_small_water", 42, 31),
                         ("cypress_small_water", 19, 31), ("waterlog", 2, 31), ("waterlog", 11, 30),
                         ("snag_water", 37, 31), ("snag_water", 1, 28)):
        D(prefab, x, y, "Water prop", on=water, inside=True)
    # the airboat, moored at the pier's end
    t.place("airboat", 26, 25, "Airboat")


def signs(t):
    for sid, x, y, text in (
            ("SignLanding", 43, 13, "CAMP COCODRIE\nBoudreaux & Thibodeaux's cookhouse. Gator pens: look, don't touch."),
            ("SignCookhouse", 15, 12, "THE BROTHERS' COOKHOUSE\nGumbo cook-off. Bring your own fixings!")):
        if (x, y) in t.occ or t.g[y][x] != ".":
            t.skipped.append(("sign", x, y))
            continue
        t.place("sign", x, y, "Sign")
        t.signs.append({"id": sid, "x": x, "y": y, "text": text})


# ---------------------------------------------------------------- people and items
def people(t):
    folk = [
        ("BOUDREAUX", "OBJ_EVENT_GFX_MAN_3", 21, 12, "MOVEMENT_TYPE_FACE_DOWN",
         "BOUDREAUX: Gumbo don't make itself,\ncher. Gather the fixings, then judge\\pour pots. (Story pass: gym.)"),
        ("THIBODEAUX", "OBJ_EVENT_GFX_MAN_1", 22, 12, "MOVEMENT_TYPE_FACE_DOWN",
         "THIBODEAUX: Mine's got more okra.\nHis is wrong. (Story pass: gym.)"),
        ("OLD_NEIGHBOUR", "OBJ_EVENT_GFX_OLD_WOMAN", 6, 6, "MOVEMENT_TYPE_FACE_LEFT",
         "Filé? Sassafras, cher, ground fine.\nI left a bundle under the cypress."),
        ("FISHERMAN", "OBJ_EVENT_GFX_FISHERMAN", 24, 25, "MOVEMENT_TYPE_FACE_LEFT",
         "Drop a line off the dock, cher.\nBig ones come up under the pier."),
        ("ISAAC", "OBJ_EVENT_GFX_BOY_1", 10, DECK_Y, "MOVEMENT_TYPE_FACE_LEFT",
         "ISAAC: ...Oh. It's you.\nI'm not in the mood. (Story pass: Isaac's battle.)"),
        ("ZYDECO_ACCORDION", "OBJ_EVENT_GFX_MAN_2", 43, DECK_Y, "MOVEMENT_TYPE_FACE_LEFT",
         "(Zydeco band: plays at night. TODO story pass: night only.)"),
        ("ZYDECO_RUBBOARD", "OBJ_EVENT_GFX_WOMAN_2", 44, DECK_Y, "MOVEMENT_TYPE_FACE_LEFT",
         "(Zydeco band: plays at night. TODO story pass: night only.)"),
        ("WRANGLER", "OBJ_EVENT_GFX_MAN_4", 32, 7, "MOVEMENT_TYPE_FACE_UP",
         "The brothers raised those gators\nfrom eggs. They only bite strangers."),
        ("KID", "OBJ_EVENT_GFX_LITTLE_BOY", 20, 15, "MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT",
         "Don't tell the nurse I fed the gators\nmy sandwich."),
        ("SMOKER", "OBJ_EVENT_GFX_FAT_MAN", 28, 22, "MOVEMENT_TYPE_FACE_UP",
         "Nothing like pecan smoke on a\nSaturday. Keep the andouille away\\pfrom the gators."),
    ]
    for name, gfx, x, y, move, text in folk:
        ok = (x, y) in t.walk or ((x, y) not in t.occ and t.g[y][x] in '."')
        if not ok:
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_CAMP_COCODRIE_{name}", "gfx": gfx, "x": x, "y": y, "move": move, "text": text})
        t.occ.add((x, y))
    # the gumbo ingredients (mockup 2-5): placeholders until the story pass defines the items; flags are stable
    # (item_flags.json): the old first-pass slots 0 (file), 1 (okra) and 4 (andouille) are kept, the shrimp is new
    for x, y, n, what in ((34, DECK_Y, "4", "andouille (mockup 2): the smokehouse's front deck"),
                          (25, PIER_Y[1], "3", "shrimp (mockup 3): the end of the south pier"),
                          (41, 5, "1", "okra (mockup 4): below the garden"),
                          (5, 6, "0", "file (mockup 5): from the old neighbour")):
        t.items.append({"x": x, "y": y, "item": "ITEM_POTION", "flag": item_flag(CONST, n),
                        "_comment": f"gumbo ingredient placeholder: {what}"})
        t.occ.add((x, y))


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [  # (file stem, title, x0, y0, x1, y1) in tiles
    ("cabins_west", "West: stilt cabins A and B, fish racks, the file", 0, 0, 16, 16),
    ("cookhouse", "The Brothers' cookhouse (gym)", 12, 0, 30, 15),
    ("gators_okra", "Gator pens and okra garden", 27, 0, 50, 8),
    ("pond_cabins", "Pond, stilt cabins 3 and 4", 28, 5, 50, 18),
    ("spine", "The boardwalk spine and the Route 9 landing", 0, 12, 50, 19),
    ("nurse", "Nurse Cabin", 1, 16, 13, 26),
    ("bait", "Bait Shack", 12, 16, 24, 26),
    ("pier", "South pier, airboat and dock fishing", 18, 15, 34, 30),
    ("smokehouse", "Smokehouse", 26, 16, 38, 26),
    ("porch", "Dance Porch", 34, 16, 50, 26),
    ("lake", "South lake: skiffs, trap line", 0, 24, 50, 35),
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
                    os.path.join(HERE, "maps", "00_town_camp_cocodrie.png")], check=True)
    top = Image.open(os.path.join(HERE, "maps", "00_town_camp_cocodrie.png")).convert("RGB")
    cdir = os.path.join(HERE, "maps", "camp_crops")
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


def main(args):
    t = Town()
    terrain(t)
    buildings(t)
    boardwalk(t)
    pen(t)
    garden(t)
    dress(t)
    signs(t)
    people(t)
    if t.skipped:
        print("left out (no room or no art yet):", t.skipped)
    if t.stand_ins:
        print("stand-ins in use (art not delivered yet):", sorted(t.stand_ins))
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write(t.grid_text())
    lid, ldir = shell(NAME, CONST, "town", "MAPSEC_CAMP_COCODRIE", "MUS_RG_FUCHSIA", W, H, t.cfg)
    spec = {"_comment": "Camp Cocodrie, handmade: generated by camp.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/06_camp_cocodrie.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": t.items, "hidden_items": t.hidden,
            "signs": t.signs,
            "exits": [{"name": "Route 9 boardwalk landing (east)", "cells": [[W - 1, y] for y in SPINE_Y]}]}
    dump(SPEC, spec)
    if "--no-build" in args:
        return
    print(run([os.path.join(HERE, "sources", "orleans_custom", "make_camp_art.py")]).stdout.strip())
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-300:])
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
    if "--review" in args:
        review(os.path.join(HERE, "maps", "00_camp_cocodrie_review.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

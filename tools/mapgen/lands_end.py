"""Land's End (gym 8, Rain: the stilt town where the delta meets the Gulf), built by hand from its mockup
(09_lands_end.png): 50 x 38 (the mockup at 1.25x) on the orleans_harbor tileset (make_town_tilesets.py +
lands_end_tileset.py, demand-driven, palette v2).

usage (from the decomp root; takes no lock itself: wrap it in `buildlock.py acquire/release lands_end`):
    python -W ignore tools/mapgen/lands_end.py [--review] [--no-build] [--fresh] [--dry-run] [--ascii]
writes maps/lands_end.json + .grid.txt, regenerates the art (sources/orleans_custom/make_lands_end_art.py) and the
tileset recipe (make_town_tilesets.py orleans_harbor), composes and builds (again while the build asks for new overlay
tiles), runs check.py; --review writes maps/00_lands_end_review.png and maps/lands_end_crops/*.png (mockup | built and 3x
crops). Then build_interior.py relinks the door warps to their rooms (labels from town_plans.PLANS["lands_end"]).
Edit this file, never maps/lands_end.json. Pieces without art yet (the two new shrimp trawlers) use same-footprint
stand-ins (lands_end_tileset.py): the layout doesn't change when the art lands.

The town is water, marsh and mud and nothing else: no grass, so no grass/water/marsh/mud triple joins. The dual-grid
shore sets draw every edge (marsh and mud never share a tile: a two-row water channel separates them).

Layout (x right, y down), everything stands on the water on pilings or planks:
    marsh      the north: rows 0..M(x)-1, a gentle two-step shore, cypress and reeds wholly inside it
    mudflat    the west: a smooth blob rows 11..22 that the main boardwalk crosses to the Route 20 boat exit (x = 0)
    boardwalks narrow dark planks: the main east-west walk (2 wide, rows 15-16, x 0..45); the west and centre
               branches south (2 wide) and the east branch to the tide station; the south loop (1 wide) from the west
               branch past the Marine Supply, open at its east end by a 3-cell channel so the water behind the Centre and
               the shop stays surf-connected; the pavilion's wrap-around deck; the Route 21 landing pier (x 41-42)
    houses     five houses on pilings (varied roofs), steps down to the boardwalk; the Lookout (NE), the Pokemon Center,
               Marine Supply, the Tide Gauge & Weather Station, and the Rain Pavilion (gym) on its own deck
    boats      two shrimp trawlers moored along the west branch
    surf       every dock is solid (elevation 3): a surfer goes round them; none of the water is sealed off
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

KEY, NAME, CONST = "lands_end", "LandsEnd", "MAP_LANDS_END"
CFG = "orleans_harbor"
W, H = 50, 39   # (a 39th row of open water south of the pilings: the pier runs on to the Route 21 seam, the pilings don't sit on the border)
SPEC = os.path.join(HERE, "maps", KEY + ".json")

# ---- terrain: the marsh's first water row per column (rows 0..M-1 are marsh), and the mudflat's rows
MARSH_M = [8] * 10 + [7] * 9 + [8] * 18 + [7] * 13            # x 0-9: 8, 10-18: 7, 19-36: 8, 37-49: 7
MUD = {11: 5, 12: 7, 13: 8, 14: 9, 15: 10, 16: 10, 17: 8, 18: 6, 19: 5, 20: 3, 21: 2, 22: 1}   # row -> last mud column

# door-bearing buildings, in the first pass's warp order (the rooms' exits use these warp numbers):
# room key -> (prefab, top-left)
BUILDINGS = [
    ("lands_end_house_1", "house_plum3_mud", (3, 10)),
    ("lands_end_lookout", "lookout", (42, 8)),
    ("lands_end_house_2", "house_slate4", (17, 10)),
    ("lands_end_house_3", "house_rust3", (31, 10)),
    ("lands_end_house_4", "house_moss3", (8, 18)),
    ("lands_end_pokecenter", "pokecenter", (16, 19)),
    ("lands_end_house_5", "house_teal4", (41, 18)),
    ("lands_end_marine_supply", "shop", (15, 25)),
    ("lands_end_weather_station", "station", (39, 26)),
    ("lands_end_gym", "pavilion", (23, 30)),
]

# boardwalk rectangles (x0, y0, x1, y1, orientation): earlier ones win where they overlap
BOARDWALK = [
    (2, 15, 45, 16, "h"),      # the main east-west walk, out to the Route 20 boat exit at x = 0: it ends on the west mudflat, 2 cells short of the edge (Route 20's flats run on)
    (12, 17, 13, 30, "v"),     # the west branch (to the south loop and the fishing end)
    (27, 17, 28, 28, "v"),     # the centre branch (to the pavilion)
    (37, 17, 38, 30, "v"),     # the east branch (to the tide station)
    (14, 29, 18, 29, "h"),     # the south loop, past the Marine Supply (open at its east end)
    (9, 23, 11, 23, "h"),      # house 4's stub
    (14, 23, 18, 23, "h"),     # the Center's stub
    (39, 23, 42, 23, "h"),     # house 5's stub
    (37, 30, 44, 30, "h"),     # the station's deck
    (41, 31, 42, 36, "v"),     # the Route 21 landing pier (its head stands two rows short of the seam: the pier no longer runs into the border; the boatman and the pearl stay on it)
    (35, 12, 36, 14, "v"),     # the pad north of the main walk, by the north houses (Andrew and Jayden)
    (22, 29, 32, 29, "h"),     # the pavilion's rear deck (1 wide)
    (22, 30, 22, 34, "v"),     # ... its west side
    (32, 30, 32, 34, "v"),     # ... its east side
    (22, 35, 32, 36, "h"),     # ... and its front deck, under the door
]
EXITS = {"W": [(0, 15), (0, 16)], "S": [(41, 38), (42, 38)]}


class Town:
    def __init__(self):
        self.g = [["~"] * W for _ in range(H)]
        self.b = []
        self.occ = set()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs, self.items, self.hidden = [], [], [], []
        self.walk = set()
        self.skipped, self.stand_ins = [], set()

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def have(self, prefab):
        return prefab in self.cfg["prefabs"]

    def rows(self, prefab):
        return self.cfg["prefabs"][prefab]["rows"]

    def cells(self, prefab, x, y):
        r = self.rows(prefab)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0])) if r[j][i] is not None]

    def box(self, prefab, x, y):
        r = self.rows(prefab)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0]))]

    def place(self, prefab, x, y, label=None, force=False, **kw):
        cells = self.cells(prefab, x, y)
        clash = [c for c in cells if c in self.occ]
        if clash and not force:
            raise SystemExit(f"{prefab} at ({x},{y}) overlaps {clash[:4]}")
        for c in cells:
            self.occ.add(c)
        b = {"prefab": prefab, "x": x, "y": y, "label": label or prefab.replace("_", " ").capitalize()}
        b.update(kw)
        self.b.append(b)
        if self.cfg["prefabs"][prefab].get("stand_in"):
            self.stand_ins.add(prefab)
        return b

    def corners(self, cells):
        return {(i + dx, j + dy) for i, j in cells for dx in (0, 1) for dy in (0, 1)}

    def deco(self, prefab, x, y, label=None, on="~", inside=True, ring=0, **kw):
        """A decoration where it fits: its cells inside the map and free, on terrain `on`, and (`inside`) wholly inside
        that patch (every dual-grid corner), `ring` cells of margin clear of other objects; else skipped."""
        if not self.have(prefab):
            self.skipped.append((prefab, x, y, "no prefab"))
            return None
        cs = self.box(prefab, x, y)
        ok = all(0 <= i < W and 0 <= j < H and (i, j) not in self.occ and self.g[j][i] in on for i, j in cs)
        if ok and inside:
            ok = all(0 <= i < W and 0 <= j < H and self.g[j][i] in on for i, j in self.corners(cs))
        if ok and ring:
            ok = not any((i + dx, j + dy) in self.occ for i, j in cs for dx in range(-ring, ring + 1)
                         for dy in range(-ring, ring + 1))
        if not ok:
            self.skipped.append((prefab, x, y))
            return None
        return self.place(prefab, x, y, label, **kw)

    def grid_text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"


def label_of(key):
    return door_label(key, mock.INTERIORS[key]["title"])


def interiors_before():
    if not os.path.exists(SPEC):
        return {}
    old = json.load(open(SPEC, encoding="utf-8"))
    return {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}


# ---------------------------------------------------------------- terrain
def terrain(t):
    for x in range(W):
        for y in range(MARSH_M[x]):
            t.g[y][x] = '"'
    for y, x1 in MUD.items():
        for x in range(0, x1 + 1):
            t.g[y][x] = "L"


# ---------------------------------------------------------------- boardwalk
def door_below(t):
    """The plank cells directly below a door's steps: their north side stays open, the steps run into them."""
    out = set()
    for key, prefab, (x, y) in BUILDINGS:
        info = t.cfg["prefabs"][prefab]
        d = info["door"]
        dx, dy = (d[0], d[1]) if not isinstance(d[0], list) else d[0]
        low = max([dy] + [cy for cx, cy in info.get("passable", []) if cx == dx])
        out.add((x + dx, y + low + 1))
    return out


def plank_cells():
    cells = {}
    for x0, y0, x1, y1, o in BOARDWALK:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cells.setdefault((x, y), o)
    return cells


def boardwalk(t):
    """Every plank cell gets the piece its neighbours ask for: an edge is drawn on a side that has no plank (a lip on
    the north, the deck's timber face on the south, rims west and east), except above a door's steps."""
    cells = plank_cells()
    below = door_below(t)
    for (x, y), o in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        edges = ""
        if (x, y - 1) not in cells and (x, y) not in below:
            edges += "n"
        if (x, y + 1) not in cells:
            edges += "s"
        if (x - 1, y) not in cells:
            edges += "w"
        if (x + 1, y) not in cells:
            edges += "e"
        name = f"plank_{o}{edges}"
        if not t.have(name):
            raise SystemExit(f"plank piece {name} missing at ({x},{y})")
        t.place(name, x, y, "Boardwalk")
        t.walk.add((x, y))


def skirts(t):
    """The pilings under every south face."""
    cells = plank_cells()
    for (x, y), o in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if (x, y + 1) in cells or (x, y + 1) in t.occ or y + 1 >= H:
            continue
        mud = t.at(x, y + 1) == "L"
        pat = x % 3
        if pat == 2:  # between the posts the plain lip carries the shadow line (over mud too)
            piece = "skirt_plain"
            if t.have(piece):
                t.place(piece, x, y + 1, "Pilings")
            continue
        piece = ("m" if mud else "") + ("skirt_e" if pat == 0 else "skirt")
        if t.have(piece):
            t.place(piece, x, y + 1, "Pilings")


def dressing(t):
    """Lanterns on the main walk's north rim at the branch junctions, bollards on the west branch's rim beside the
    trawlers' mooring lines. Overlays on the plank pieces (they block): only on rim cells, so the walking lane stays
    open (the main walk keeps its south row, the branch its east column)."""
    for prefab, cells in (("lantern", ((11, 15), (14, 15), (26, 15), (29, 15), (34, 15), (37, 15))),
                          ("bollard", ((12, 27), (12, 29)))):
        for x, y in cells:
            if (x, y) in t.walk and not any(o["x"] == x and o["y"] == y for o in t.objects) and t.have(prefab):
                t.place(prefab, x, y, prefab.capitalize(), force=True)
            else:
                t.skipped.append((prefab, x, y))


def pc_footing(t):
    """The Center's south-east corner (x 19) overhangs open water past the stub's end: pilings under it."""
    x, y = 16 + 3, 19 + 4
    if t.have("pc_skirt_r") and t.at(x, y) == "~" and (x, y) not in t.occ:
        t.place("pc_skirt_r", x, y, "Pilings")


# ---------------------------------------------------------------- buildings
def buildings(t):
    links = interiors_before()
    for key, prefab, (x, y) in BUILDINGS:
        if not t.have(prefab):
            raise SystemExit(f"{prefab} missing from the tileset config")
        b = t.place(prefab, x, y, label_of(key))
        if label_of(key) in links:
            b["interior"] = links[label_of(key)]


# ---------------------------------------------------------------- boats and water props
BOATS = [("trawler_a", 5, 25), ("trawler_b", 5, 29)]


def waterfront(t):
    D = t.deco
    for prefab, x, y in BOATS:
        D(prefab, x, y, "Boat", on="~", inside=False)
    # mooring piles along the west branch beside the boats, and along the other branches' outer edges
    for x, y in ((11, 25), (11, 27), (11, 29), (11, 31),
                 (26, 19), (26, 23), (29, 20), (29, 24), (36, 19), (36, 24), (39, 19), (36, 28), (39, 28),
                 (46, 15), (46, 16), (0, 18)):
        D("pile", x, y, "Mooring pile", on="~L", inside=False)
    # egrets on old pilings, out in the open water
    for x, y in ((47, 24), (20, 33), (4, 33), (33, 24)):
        D("heron_pile", x, y, "Heron perch", on="~", inside=True, ring=1)


def marsh(t):
    """The marsh is reeds (the mockup draws no trees; the tile budget has no room for cypress: ~30 tiles a kind)."""
    D = t.deco
    for prefab, x, y in (("reeds_marsh", 7, 3), ("reeds_marsh", 13, 2), ("reeds_marsh", 18, 3), ("reeds_marsh", 23, 3),
                         ("reeds_marsh", 29, 3), ("reeds_marsh", 36, 3), ("reeds_marsh", 40, 4), ("reeds_marsh", 47, 3),
                         ("reeds_marsh", 2, 5), ("reeds_marsh", 12, 4), ("reeds_marsh", 20, 5), ("reeds_marsh", 25, 1),
                         ("reeds_marsh", 9, 1), ("reeds_marsh", 16, 1), ("reeds_marsh", 38, 5)):
        D(prefab, x, y, "Tree" if prefab.startswith("cypress") else "Reeds", on='"', inside=True)


def signs(t):
    for sid, x, y, text in (
            ("SignWest", 2, 14, "LAND'S END\nWest: the Route 20 boat to the heron rookery."),
            ("SignPavilion", 24, 35, "THE RAIN PAVILION\nSeven carved verses. Mind the rain.")):
        if not t.have("sign") or (x, y) in t.occ and (x, y) not in t.walk:
            t.skipped.append(("sign", x, y))
            continue
        t.place("sign", x, y, "Sign", force=True)
        t.signs.append({"id": sid, "x": x, "y": y, "text": text})


# ---------------------------------------------------------------- people and items
def people(t):
    folk = [
        ("ANDREW", "OBJ_EVENT_GFX_MAN_2", 35, 12, "MOVEMENT_TYPE_FACE_DOWN",
         "ANDREW: ...The telling doesn't end here.\n(Story pass: Andrew appears.)"),
        ("JAYDEN", "OBJ_EVENT_GFX_BOY_2", 36, 12, "MOVEMENT_TYPE_FACE_LEFT",
         "JAYDEN: Battle me when you've earned it.\n(Story pass: Jayden battle 5.)"),
        ("HERON", "OBJ_EVENT_GFX_OLD_WOMAN", 30, 35, "MOVEMENT_TYPE_FACE_LEFT",
         "HERON: The rain keeps the true telling.\nWin, and the Gulf is yours. (Story pass: gym, Diving Gear.)"),
        ("FISHERMAN", "OBJ_EVENT_GFX_FISHERMAN", 12, 30, "MOVEMENT_TYPE_FACE_LEFT",
         "Drop a line off the boards, cher.\nThe big ones come up under the boats."),
        ("BOATMAN_W", "OBJ_EVENT_GFX_SAILOR", 2, 16, "MOVEMENT_TYPE_FACE_LEFT",
         "The heron rookery boat leaves from\nthe end of the boards. (Route 20.)"),
        ("BOATMAN_S", "OBJ_EVENT_GFX_SAILOR", 42, 35, "MOVEMENT_TYPE_FACE_DOWN",
         "Open Gulf past the landing. Come back\nwhen the pavilion's rain has cleared.\n(Route 21.)"),
        ("KID", "OBJ_EVENT_GFX_LITTLE_BOY", 21, 15, "MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT",
         "We learn to walk on boards before\nwe learn to walk on land!"),
        ("SHRIMPER", "OBJ_EVENT_GFX_FAT_MAN", 27, 23, "MOVEMENT_TYPE_FACE_UP",
         "The nets are folded up till the rain\nlifts. Good shrimp, but only after."),
    ]
    for name, gfx, x, y, move, text in folk:
        if (x, y) not in t.walk or any(o["x"] == x and o["y"] == y for o in t.objects):
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_LANDS_END_{name}", "gfx": gfx, "x": x, "y": y, "move": move, "text": text})
    for x, y, n, item, what in ((45, 16, "ether", "ITEM_ETHER", "the end of the main boardwalk"),
                                (13, 30, "revive", "ITEM_REVIVE", "the west branch's fishing end"),
                                (42, 36, "pearl", "ITEM_PEARL", "the Route 21 landing pier")):
        if (x, y) in t.walk and not any(o["x"] == x and o["y"] == y for o in t.objects):
            t.items.append({"x": x, "y": y, "item": item, "flag": item_flag(CONST, n),
                            "_comment": f"placeholder item: {what}"})
        else:
            t.skipped.append(("item " + n, x, y))


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [  # (file stem, title, x0, y0, x1, y1) in tiles
    ("houses_west", "Stilt houses, west: the mud house, Center and house 4", 0, 7, 26, 27),
    ("houses_east", "Stilt houses, east: houses 3 and 5, the Lookout", 26, 6, 50, 26),
    ("boardwalks", "Boardwalks: the main walk and its branches", 0, 12, 50, 20),
    ("pavilion", "The Rain Pavilion (gym) and its deck", 16, 26, 38, 38),
    ("lookout", "The Lookout tower", 34, 5, 50, 18),
    ("station", "Tide gauge and weather station, the landing pier", 32, 21, 50, 38),
    ("boats", "Shrimp trawlers on the west branch", 0, 20, 18, 34),
    ("shoreline", "Marsh shore and the mudflat", 0, 0, 50, 15),
    ("shop", "Marine Supply and the south loop", 8, 18, 30, 32),
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
    sheet_png = os.path.join(HERE, "maps", "00_town_lands_end.png")
    subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "town_sheet.py"), KEY, sheet_png], check=True)
    top = Image.open(sheet_png).convert("RGB")
    cdir = os.path.join(HERE, "maps", "lands_end_crops")
    os.makedirs(cdir, exist_ok=True)
    crops = []
    for stem, title, x0, y0, x1, y1 in REVIEW_AREAS:
        c = clean.crop((x0 * 16, y0 * 16, min(x1, W) * 16, min(y1, H) * 16))
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


def build_town():
    t = Town()
    terrain(t)
    boardwalk(t)
    dressing(t)
    buildings(t)
    skirts(t)
    pc_footing(t)
    waterfront(t)
    marsh(t)
    signs(t)
    people(t)
    return t


def main(args):
    art = os.path.join(HERE, "sources", "orleans_custom", "make_lands_end_art.py")
    print(run([art]).stdout.strip())
    # the tileset config first: the pieces' footprints come from it
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-200:])
    t = build_town()
    if "--ascii" in args:
        occ_name = {}
        for b in t.b:
            for c in t.box(b["prefab"], b["x"], b["y"]):
                occ_name[c] = b["prefab"]
        for y in range(H):
            line = ""
            for x in range(W):
                n = occ_name.get((x, y))
                line += t.g[y][x] if n is None else "=" if n.startswith("plank") else "S" if "skirt" in n else "o"
            print(f"{y:2d} {line}")
    if t.skipped:
        print("left out (no room or no art yet):", len(t.skipped), t.skipped[:30])
    if t.stand_ins:
        print("stand-ins in use (art not delivered yet):", sorted(t.stand_ins))
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write(t.grid_text())
    lid, ldir = shell(NAME, CONST, "town", "MAPSEC_LANDS_END", "MUS_RG_CINNABAR", W, H, t.cfg)
    spec = {"_comment": "Land's End, handmade: generated by lands_end.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/09_lands_end.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": t.items, "hidden_items": t.hidden,
            "signs": t.signs,
            "exits": [{"name": "Route 20 boat exit, boardwalk end (west)", "cells": [list(c) for c in EXITS["W"]]},
                      {"name": "Route 21: open water south of the landing pier (by Surf)", "by_boat": True, "cells": [list(c) for c in EXITS["S"]]}]}
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
        print(r.stdout.strip()[-1500:], r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = run([os.path.join(HERE, "compose.py"), recipe])
        print(c.stdout.strip()[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return
    c = run([os.path.join(HERE, "check.py"), SPEC])
    print(c.stdout.strip()[-3000:], c.stderr.strip()[-2000:])
    if "--review" in args:
        review(os.path.join(HERE, "maps", "00_lands_end_review.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

"""Mock layouts of the three legendary arenas, rendered the way the GBA draws them, plus the art review sheet.

usage (from the decomp root): python tools/mapgen/tilesets/arenas/arena_mocks.py [--no-art] [--no-compose]
    1. runs the art scripts (make_temple.py, make_cathedral.py, make_shrine.py) unless --no-art
    2. composes the two interior tilesets (recipes/orleans_temple.json, recipes/orleans_saltdome.json) into
       data/tilesets/secondary/<dir> + tilesets/arenas/<dir>.mapping.json unless --no-compose (nothing is registered)
    3. builds each mock from its layout table below, renders it through the composed tileset (interiors) or the
       built Oldest Shrine map with the new pieces drawn in (the shrine), pastes the object sprites at their stand
       cells, and writes at 3x:  ../tile_review/arenas/<arena>_mock.png (+ <arena>_mock.json: the metatile name grid,
       walkable mask and stand cells, ready for the layout agent)
    4. writes the review sheet ../tile_review/arenas/art_arenas.png (every piece at 4x, counts and budgets)

The mocks are proposals for the layout agent: sizes, positions and stand cells are suggestions; nothing in data/maps or
data/layouts is touched.
"""
import json
import math
import os
import struct
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, MAPGEN)
import render  # noqa: E402
from arena_art import dump, scale  # noqa: E402

REVIEW = os.path.normpath(os.path.join(ROOT, "..", "tile_review", "arenas"))
SPRITES = {
    "kyogre": ("graphics/object_events/pics/pokemon_old/kyogre.png", 32, 32),
    "groudon": ("graphics/object_events/pics/pokemon_old/groudon.png", 32, 32),
    "rayquaza": ("graphics/pokemon/rayquaza/overworld.png", 64, 64),
    "player": ("graphics/object_events/pics/people/brendan/walking.png", 16, 32),
    "jayden": ("graphics/object_events/pics/people/boy_2.png", 16, 32),
    "camille": ("graphics/object_events/pics/people/team_aqua/aqua_member_f.png", 16, 32),
    "andrew": ("graphics/object_events/pics/people/man_2.png", 16, 32),
    "keeper": ("graphics/object_events/pics/people/old_woman.png", 16, 32),
    "local": ("graphics/object_events/pics/people/man_1.png", 16, 32),
    "item": ("graphics/object_events/pics/misc/ball_poke.png", 16, 32),
}


def font(n=12):
    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, n)
    return ImageFont.load_default()


def sprite(key, frame=0, face_up=False):
    path, w, h = SPRITES[key]
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None
    im = Image.open(p)
    if face_up and key in ("player", "jayden", "camille", "andrew", "keeper", "local"):
        frame = 1
    sub = im.crop((frame * w, 0, frame * w + w, h))
    if sub.mode == "P":
        rgba = Image.new("RGBA", sub.size, (0, 0, 0, 0))
        pal = sub.getpalette()
        px, out = sub.load(), rgba.load()
        for y in range(h):
            for x in range(w):
                i = px[x, y]
                if i:
                    out[x, y] = (pal[3 * i], pal[3 * i + 1], pal[3 * i + 2], 255)
        return rgba
    return sub.convert("RGBA")


def paste_sprite(img, key, cx, cy, face_up=False):
    """Object at cell (cx, cy): bottom-aligned to the cell, centred on it (how the engine places object sprites)."""
    s = sprite(key, face_up=face_up)
    if s is None:
        return
    x = cx * 16 + 8 - s.width // 2
    y = cy * 16 + 16 - s.height
    img.alpha_composite(s, (x, y))


# ------------------------------------------------------------------ composing and rendering an interior
def compose(recipe):
    subprocess.run([sys.executable, os.path.join(MAPGEN, "compose.py"), recipe], cwd=ROOT, check=True)


class Interior:
    def __init__(self, prefix, dirname, w, h, fill):
        self.prefix, self.dirname, self.w, self.h = prefix, dirname, w, h
        self.grid = [[None] * w for _ in range(h)]
        self.walk = [[False] * w for _ in range(h)]
        art = json.load(open(os.path.join(HERE, {"dt": "temple.json", "sc": "cathedral.json"}[prefix])))
        self.pieces = art["pieces"]
        self.objects = []
        self.notes = []
        self.fill(fill, 0, 0, w, h)

    def put(self, name, x, y):
        p = self.pieces[name]
        walk = set(map(tuple, p["walk"]))
        for j, row in enumerate(p["rows"]):
            for i, mid in enumerate(row):
                if 0 <= x + i < self.w and 0 <= y + j < self.h:
                    self.grid[y + j][x + i] = mid
                    self.walk[y + j][x + i] = (i, j) in walk

    def fill(self, name, x, y, w, h):
        for j in range(h):
            for i in range(w):
                self.put(name, x + i, y + j)

    def obj(self, key, x, y, label, face_up=False):
        self.objects.append({"sprite": key, "x": x, "y": y, "label": label, "face_up": face_up})

    def render(self):
        mp = json.load(open(os.path.join(HERE, f"{self.dirname}.mapping.json")))["metatiles"]
        ts = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_building"),
                             os.path.join(ROOT, f"data/tilesets/secondary/{self.dirname}"))
        img = Image.new("RGBA", (self.w * 16, self.h * 16))
        for y in range(self.h):
            for x in range(self.w):
                img.paste(ts.metatile(mp[self.grid[y][x]]), (x * 16, y * 16))
        for o in sorted(self.objects, key=lambda o: o["y"]):
            paste_sprite(img, o["sprite"], o["x"], o["y"], o["face_up"])
        return img

    def export(self, path, extra=None):
        dump(path, dict({"size": [self.w, self.h], "tileset": self.dirname, "primary": "orleans_building",
                         "grid": [" ".join(r) for r in self.grid],
                         "walk": ["".join("." if w else "#" for w in r) for r in self.walk],
                         "objects": self.objects, "notes": self.notes}, **(extra or {})))


def verify(prefix, dirname, sheet_png):
    """Every composed metatile must draw exactly the art it was cut from (no palette squeeze)."""
    mp = json.load(open(os.path.join(HERE, f"{dirname}.mapping.json")))["metatiles"]
    rec = json.load(open(os.path.join(HERE, "recipes", f"{dirname}.json")))
    ts = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_building"),
                         os.path.join(ROOT, f"data/tilesets/secondary/{dirname}"))
    sheet = Image.open(os.path.join(HERE, sheet_png)).convert("RGB")
    bad = 0
    for m in rec["sources"][0]["metatiles"]:
        bx, by = m["bottom"]
        ref = sheet.crop((bx * 16, by * 16, bx * 16 + 16, by * 16 + 16))
        if "top" in m:
            tx, ty = m["top"]
            top = sheet.crop((tx * 16, ty * 16, tx * 16 + 16, ty * 16 + 16))
            rp, tp = ref.load(), top.load()
            for y in range(16):
                for x in range(16):
                    if tp[x, y] != (255, 0, 255):
                        rp[x, y] = tp[x, y]
        got = ts.metatile(mp[f"{prefix}:{m['id']}"])
        if ref.convert("RGB").tobytes() != got.convert("RGB").tobytes():
            bad += 1
    return bad


# ------------------------------------------------------------------ the Drowned Temple
def plat_name(cells, x, y):
    """The platform piece for cell (x, y) of a platform cell set standing in water (cell-based 9-slice)."""
    n, s, w, e = ((x, y - 1) not in cells, (x, y + 1) not in cells, (x - 1, y) not in cells, (x + 1, y) not in cells)
    key = ("N" if n else "") + ("S" if s else "") + ("W" if w else "") + ("E" if e else "")
    if key in ("N", "S", "W", "E", "NW", "NE", "SW", "SE"):
        return "plat_" + key
    if key == "":
        for c, (dx, dy) in (("iNW", (-1, -1)), ("iNE", (1, -1)), ("iSW", (-1, 1)), ("iSE", (1, 1))):
            if (x + dx, y + dy) not in cells:
                return "plat_" + c
        return "plat_C"
    raise ValueError(f"no platform piece for edges {key} at {x},{y}")


def temple_mock(state="closed"):
    W, H = 19, 21
    m = Interior("dt", "orleans_temple", W, H, "floor")
    from arena_art import hashn
    for y in range(H):
        for x in range(W):
            m.put(["floor", "floor_b", "floor_c", "floor_d"][int(hashn(x, y, 77) * 4)], x, y)
    # floor variety (deterministic scatter)
    var = {(3, 12): "floor_crack", (12, 16): "floor_shells", (5, 17): "floor_sand", (14, 17): "floor_sand",
           (13, 11): "floor_kelp", (4, 11): "floor_bubbles", 
           (15, 14): "floor_crack", (16, 11): "floor_shells", (7, 17): "floor_kelp",
           (1, 17): "floor_sand"}
    for (x, y), n in var.items():
        m.put(n, x, y)
    m.put("light_pool", 8, 13)        # sunlight through cracks in the vault
    m.put("light_pool", 15, 16) if False else None
    # walls
    for y in range(H):
        m.put("side_l", 0, y)
        m.put("side_r", W - 1, y)
    for x in range(1, W - 1):
        m.put("cap_b" if x % 5 == 2 else "cap", x, 0)
        m.put(["frieze_spiral", "frieze_wave"][x % 2], x, 1)
        m.put(["base_plain", "base_coral", "base_plain", "base_kelp"][x % 4], x, 2)
    m.put("frieze_crack", 3, 1)
    m.put("medallion", 8, 0)
    # the sanctum: the moat with the altar island and causeway
    island = {(x, y) for x in range(6, 13) for y in range(4, 8)} | {(x, 8) for x in range(8, 11)}
    island -= {(6, 4), (12, 4)}
    for y in range(3, 9):
        for x in range(1, W - 1):
            if (x, y) in island:
                m.put(plat_name(island | {(x, 9) for x in range(8, 11)}, x, y), x, y)
            else:
                m.put("water_shadow" if y == 3 or (x, y - 1) in island else "water", x, y)
    for (x, y) in [(2, 5), (15, 7), (4, 7), (16, 4), (13, 5)]:
        if (x, y) not in island and m.grid[y][x] == "dt:water":
            m.put("water_glint", x, y)
    m.put("water_kelp", 2, 7)
    m.put("water_kelp", 16, 6)
    m.put("dais", 8, 4)
    m.put("tide_bowl", 7, 4)
    m.put("tide_bowl", 11, 4)
    # the dividing wall and the sealed door
    for x in range(1, W - 1):
        m.put("div_cap_b" if x % 6 == 4 else "div_cap", x, 9)
        m.put(["div_face", "div_face_coral", "div_face", "div_face_kelp"][x % 4], x, 10)
    m.put("door_closed" if state == "closed" else "door_open", 8, 9)
    # the outer hall
    for x, kind in ((3, "column"), (15, "column")):
        m.put(kind, x, 11)
    m.put("column_broken", 3, 15)
    m.put("column_stump", 15, 16)
    m.put("column_fallen", 11, 15)
    m.put("capital_fallen", 14, 15)
    m.put("tide_pool", 1, 13)
    m.put("tide_pool_w", 5, 15)
    m.put("bell", 13, 12)
    m.put("kelp_tall", 6, 11)
    m.put("kelp_tall", 12, 11)
    m.put("coral", 1, 11)
    m.put("coral", 17, 13)
    m.put("rubble", 17, 17)
    m.put("rubble", 9, 16)
    m.put("kelp_tall", 1, 16)
    m.put("coral", 12, 17)
    m.put("light_pool", 15, 14)        # a shaft of light falling beside the bell
    # the entry: the dive pool, and the room's south edge
    for x in range(1, W - 1):
        m.put("wall_s", x, H - 1)          # the room's outer wall closes the south side
    m.put("wall_sw", 0, H - 1)
    m.put("wall_se", W - 1, H - 1)
    m.put("dive_pool", 8, H - 3)
    m.obj("kyogre", 9, 5, "Kyogre (raid object, KYOGRE_FRONT) on the dais")
    m.obj("player", 9, 6, "player's stand cell to face Kyogre", face_up=True)
    m.obj("player", 9, 11, "sing Heron's verse here, facing the sealed door (9,10)", face_up=True) if state == "closed" else None
    m.obj("player", 9, H - 3, "arrival: the dive pool's top step (exit = the cell below)", face_up=True)
    m.notes = [
        "19x21. Sanctum rows 3-8: the moat (deep water, blocking) rings the altar island; the causeway (8-10, 8) meets the door.",
        "Sealed door: door_closed 3x2 at (8,9); its middle column (9,9)-(9,10) opens (map state -> door_open; the lintel is a top layer).",
        "Kyogre stands at (9,5) on the dais; the player faces it from (9,6).",
        "Entry: the dive pool (8-10, 18-19): arrive on (9,18), exit by walking south into (9,19).",
        "Suggested map weather: WEATHER_UNDERWATER_BUBBLES (rising bubbles) for the underwater feel.",
        "Row 20 is the room's south wall (wall_s, corners wall_sw / wall_se), not a void; the map's border block should be void.",
    ]
    return m



# ------------------------------------------------------------------ the Salt Cathedral
def cathedral_mock():
    from arena_art import hashn
    W, H = 23, 22
    m = Interior("sc", "orleans_saltdome", W, H, "floor")
    for y in range(H):
        for x in range(W):
            if hashn(x, y, 5) < 0.3:
                m.put("floor_b", x, y)
    for (x, y, n) in [(9, 9, "floor_crack"), (14, 13, "floor_crack"), (8, 15, "floor_dust"), (14, 8, "floor_dust"),
                      (13, 16, "floor_crystals"), (2, 6, "floor_dust"), (20, 12, "floor_crack"), (8, 11, "floor_crystals")]:
        m.put(n, x, y)
    for y in range(H):
        m.put("side_l", 0, y)
        m.put("side_r", W - 1, y)
    for x in range(1, W - 1):
        m.put("cap_b" if x % 4 == 1 else "cap", x, 0)
        m.put(["face_hi", "face_hi_vein", "face_hi", "face_hi_drill"][x % 4], x, 1)
        m.put(["face_lo", "face_lo_crystal", "face_lo_vein", "face_lo"][x % 4], x, 2)
    m.put("heart", 8, 0)
    m.put("timber_set", 2, 1)
    m.put("timber_set", 18, 1)
    # the heat zone in front of the heart, fading out west, east and south
    for y in range(3, 6):
        for x in range(8, 15):
            m.put("warm", x, y)
        m.put("warm_fade_w", 7, y)
        m.put("warm_fade_e", 15, y)
    for x in range(8, 15):
        m.put("warm_fade_s", x, 6)
    m.put("warm_fade_sw", 7, 6)
    m.put("warm_fade_se", 15, 6)
    for (x, y, n) in [(9, 3, "warm_core"), (13, 3, "warm_core"), (8, 4, "warm_seam"), (14, 4, "warm_glaze"),
                      (9, 5, "warm_seam_v"), (13, 5, "warm_seam"), (11, 5, "warm_core"), (10, 5, "warm_glaze")]:
        m.put(n, x, y)
    # the processional aisle from the track to the heat, two crystal chandeliers over it
    for y in range(7, 18):
        m.put("aisle_w", 10, y)
        m.put("aisle_c", 11, y)
        m.put("aisle_e", 12, y)
    m.put("chandelier", 10, 8)
    m.put("chandelier", 10, 13)
    m.put("dais", 10, 3)
    # the nave: three pairs of pillars, the middle pair timbered
    for y, kind in ((7, "pillar"), (11, "pillar_timber"), (15, "pillar")):
        m.put(kind, 5, y)
        m.put(kind, 16, y)
    # the south rim and the adit
    for x in range(1, W - 1):
        m.put("rim_s", x, H - 2)
        m.put("void", x, H - 1)
    m.put("adit", 10, H - 2)
    # the track: out of the adit, a turn west, along row 18, a turn north, up the west aisle to the cart and the stop
    m.put("rail_sw", 10, 18)
    for x in range(4, 10):
        m.put("rail_h", x, 18)
    m.put("rail_ne", 2, 17)
    for y in range(10, 17):
        m.put("rail_v", 2, y)
    m.put("cart", 2, 8)
    m.put("rail_end", 2, 7)
    # the aisles
    m.put("cribbing", 19, 7)
    m.put("cribbing", 19, 14)
    m.put("lantern_post", 20, 11)
    m.put("lantern_post", 1, 11)
    m.put("crystal_big", 3, 13)
    m.put("crystal", 1, 4)
    m.put("crystal", 21, 5)
    m.put("crystal_big", 2, 3)          # the top corners of the nave, dressed alike
    m.put("crystal_big", 19, 3)
    m.put("lantern_fallen", 5, 4)
    m.put("lantern_fallen", 17, 5)
    m.put("crystal", 18, 10)
    m.put("salt_blocks", 19, 17)
    m.put("spall", 1, 19)
    m.put("spall", 21, 13)
    m.put("spall", 4, 5)
    m.obj("groudon", 11, 4, "Groudon (raid object, GROUDON_FRONT) on the dais")
    m.obj("player", 11, 5, "player's stand cell to face Groudon", face_up=True)
    m.obj("player", 11, H - 2, "arrival: the adit's mouth (exit = the cell below)", face_up=True)
    m.notes = [
        "23x22. The heart (7x3) fills the middle of the back wall; Groudon at (11,4) on the dais (10-12, 3-4); the player faces it from (11,5).",
        "The warm floor (warm*, rows 3-6) carries the heart's palette: keep mine furniture (lanterns, rails) off it.",
        "Entry: the adit (10-12, 20-21): arrive on (11,20), exit by walking south into (11,21). The track runs out of it to the cart.",
        "Nave: three pairs of 2x3 pillars (x 5-6 and 16-17); the side aisles hold the track, cribbing, crystals and lanterns.",
    ]
    return m


# ------------------------------------------------------------------ the Oldest Shrine (outdoor, on orleans_route_b)
CORNER_KEYS = {"1111": "C", "0011": "N", "1100": "S", "0101": "W", "1010": "E", "0111": "inNW", "1011": "inNE",
               "1101": "inSW", "1110": "inSE", "0001": "landSE", "0010": "landSW", "0100": "landNE", "1000": "landNW",
               "0110": "sTLBR", "1001": "sTRBL"}


def shrine_design():
    """The island as a terrain grid (36 x 32): '~' water, '.' grass, '"' marsh, 'R' ridge, 'M' platform mound.
    Everything more than 2 cells from the island keeps the built map (the feathered water, the Surf barrier).
    The earthwork is symmetric: terrain cell x mirrors to 34 - x, so the dual-grid art is symmetric about the line
    between tiles 16 and 17 (pixel 272), where the steps, the singing stone and the landing are centred."""
    W, H = 36, 32
    g = [["~"] * W for _ in range(H)]
    cx, cy, rx, ry, n = 17.5, 14.0, 12.6, 10.1, 3.4
    for y in range(H):
        for x in range(18):
            a = math.atan2(y + 0.5 - cy, abs(x + 0.5 - cx))
            wob = 0.05 * math.sin(3 * a + 0.7) + 0.04 * math.sin(5 * a + 2.0)
            if abs((x + 0.5 - cx) / rx) ** n + abs((y + 0.5 - cy) / ry) ** n <= 1.0 + wob:
                g[y][x] = g[y][34 - x] = "."
    for y in range(21, 24):                 # land under the landing's head
        for x in range(14, 21):
            g[y][x] = "."
    for y in range(7, 11):                  # the platform mound: cells 13-21 x 7-10
        for x in range(13, 22):
            g[y][x] = "M"

    def arc(rxx, ryy, a0, a1, ccx=17.5, ccy=12.5):
        cells = []
        for k in range(400):
            a = math.radians(a0 + (a1 - a0) * k / 399)
            x = int(math.floor(ccx + rxx * math.cos(a)))
            y = int(math.floor(ccy + ryy * math.sin(a)))
            if not cells or cells[-1] != (x, y):
                if cells and abs(cells[-1][0] - x) == 1 and abs(cells[-1][1] - y) == 1:
                    cells.append((x, cells[-1][1]))
                cells.append((x, y))
        return cells

    for (r0, r1, amax) in SHRINE_RIDGES:      # bands of an ellipse round the plaza (x-units; y stretched by ASPECT)
        for y in range(H):
            for x in range(18):
                dx, dy = x + 0.5 - 17.5, (y + 0.5 - 12.5) * SHRINE_ASPECT
                rho, ang = math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))
                if r0 <= rho < r1 and 90 <= ang <= amax and not (15 <= x <= 19 and y > 15):
                    g[y][x] = g[y][34 - x] = "R"
    # tidy the west half (then mirror): join diagonal-only steps (they draw as beads), drop one-cell spurs (knobs)
    R = {(x, y) for y in range(H) for x in range(18) if g[y][x] == "R"}
    for (x, y) in sorted(R):
        for dx in (-1, 1):
            if (x + dx, y + 1) in R and (x + dx, y) not in R and (x, y + 1) not in R:
                R.add((x, y + 1))
    R = {(x, y) for (x, y) in R if sum((x + dx, y + dy) in R for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2}
    for y in range(H):
        for x in range(18):
            if g[y][x] == "R":
                g[y][x] = g[y][34 - x] = "."
    for (x, y) in R:
        if not (15 <= x <= 19 and y > 15):
            g[y][x] = g[y][34 - x] = "R"
    for (x0, y0, w, h) in SHRINE_MARSH:     # small marsh groves (cypress) between the mound and the shore
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if g[y][x] == "." and not ((x in (x0, x0 + w - 1)) and (y in (y0, y0 + h - 1))):
                    g[y][x] = g[y][34 - x] = '"'
    return g


SHRINE_RIDGES = [(5.6, 7.5, 172), (9.7, 11.4, 177)]   # (inner, outer radius, how far round) about (17.5, 12.5)
SHRINE_ASPECT = 1.35
SHRINE_MARSH = [(7, 8, 5, 4)]                                   # west groves; mirrored east


def shrine_mock():
    W, H = 36, 32
    mp = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]
    mpb = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_route_b.mapping.json")))["metatiles"]
    inv = {v: k for k, v in mp.items()}
    inv.update({v: k for k, v in mpb.items()})
    ts = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_general"),
                         os.path.join(ROOT, "data/tilesets/secondary/orleans_route_b"))
    raw = open(os.path.join(ROOT, "data/layouts/OldestShrine/map.bin"), "rb").read()
    blocks = struct.unpack(f"<{len(raw) // 2}H", raw)
    cur = [[inv.get(blocks[y * W + x] & 0x3FF, "?") for x in range(W)] for y in range(H)]
    g = shrine_design()
    land = {(x, y) for y in range(H) for x in range(W) if g[y][x] != "~"}
    near = {(x + dx, y + dy) for (x, y) in land for dx in range(-2, 3) for dy in range(-2, 3)}
    sheet = Image.open(os.path.join(HERE, "shrine.png")).convert("RGBA")
    art = json.load(open(os.path.join(HERE, "shrine.json")))["pieces"]
    names = [[None] * W for _ in range(H)]

    def ch(x, y):
        return g[max(0, min(H - 1, y))][max(0, min(W - 1, x))]

    def all_water(x, y):
        return all(ch(x + dx, y + dy) == "~" for dx in (0, 1) for dy in (0, 1))

    # water props (cypress, logs, snags, Surf-barrier props) of the built map: whole groups, kept or dropped together
    keep = set()
    seen = set()
    import re
    for y in range(H):
        for x in range(W):
            nm = cur[y][x]
            mm = re.match(r"patch:(cypress(?:_small)?)_(\d)(\d)_water", nm)
            if mm and (x, y) not in seen:
                ox, oy = x - int(mm.group(2)), y - int(mm.group(3))
                w_ = 2 if "small" in mm.group(1) else 3
                cells = [(ox + i, oy + j) for j in range(3) for i in range(w_)]
                seen.update(cells)
                if all(all_water(cx_, cy_) for (cx_, cy_) in cells if 0 <= cx_ < W and 0 <= cy_ < H):
                    keep.update(cells)
            elif any(nm.startswith(p_) for p_ in ("ekat:water_lily", "ekat:water_weeds", "ekat:waterlog", "ekat:snag",
                                                   "ekat:waterstump", "patch:ovl_wpr")) and all_water(x, y):
                keep.add((x, y))

    img = Image.new("RGBA", (W * 16, H * 16))
    problems = []
    for y in range(H):
        for x in range(W):
            cs = [ch(x, y), ch(x + 1, y), ch(x, y + 1), ch(x + 1, y + 1)]
            if (x, y) in near and (x, y) in keep and all_water(x, y):
                img.paste(ts.metatile(blocks[y * W + x] & 0x3FF), (x * 16, y * 16))
                names[y][x] = cur[y][x]
                continue
            if (x, y) not in near and (x, y) not in seen or (x, y) in keep:
                if cur[y][x].startswith("patch:pier"):      # the placeholder dock goes (the landing replaces it)
                    img.paste(ts.metatile(mp["ekat:water_C"]), (x * 16, y * 16))
                    names[y][x] = "ekat:water_C"
                    continue
                img.paste(ts.metatile(blocks[y * W + x] & 0x3FF), (x * 16, y * 16))
                names[y][x] = cur[y][x]
                continue

            def bits(f):
                return "".join("1" if f(c) else "0" for c in cs)

            if "~" in cs:
                lands = {c for c in cs if c != "~"}
                key = CORNER_KEYS[bits(lambda c: c == "~")]
                if key == "C":
                    n = "ekat:water_C"
                elif lands <= {'"'}:
                    n = f"ekat:marshwater_{key}"
                elif lands <= {"."}:
                    n = f"ekat:water_{key}"
                else:
                    n = None
                    problems.append((x, y, "".join(cs)))
            elif '"' in cs:
                key = CORNER_KEYS[bits(lambda c: c == '"')]
                n = f"ekat:marsh_{key}"
                if not set(cs) <= {'"', "."}:
                    problems.append((x, y, "".join(cs)))
            elif "M" in cs:
                key = CORNER_KEYS[bits(lambda c: c == "M")]
                n = "ekat:grass" if key == "C" else f"osh:mound_{key}"
                if "R" in cs:
                    problems.append((x, y, "".join(cs)))
            elif "R" in cs:
                key = CORNER_KEYS[bits(lambda c: c == "R")]
                n = f"osh:berm_{key}"
            else:
                n = "ekat:grass"
            if n == "ekat:grass" and "M" not in cs:      # the mound's face extension (build.py's 'face' rule)
                nn, ne = ch(x, y - 1) == "M", ch(x + 1, y - 1) == "M"
                if nn and ne:
                    n = "osh:mound_face"
                elif nn:
                    n = "osh:mound_face_r"
                elif ne:
                    n = "osh:mound_face_l"
            names[y][x] = n
            if n is None:
                img.paste((255, 0, 255, 255), (x * 16, y * 16, x * 16 + 16, y * 16 + 16))
            elif n.startswith("osh:"):
                p = art[n[4:]]
                img.paste(sheet.crop((p["x"] * 16, p["y"] * 16, p["x"] * 16 + 16, p["y"] * 16 + 16)), (x * 16, y * 16))
            else:
                img.paste(ts.metatile(mp[n]), (x * 16, y * 16))

    def put_piece(name, x, y):
        p = art[name]
        crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        px = crop.load()
        for j in range(crop.height):
            for i in range(crop.width):
                if px[i, j][:3] == (255, 0, 255):
                    px[i, j] = (0, 0, 0, 0)
        img.alpha_composite(crop, (x * 16, y * 16))
        for j in range(p["h"]):
            for i in range(p["w"]):
                names[y + j][x + i] = f"{name}[{i},{j}]"

    def put_cypress(x, y, small=False):
        k = "cypress_small" if small else "cypress"
        for j in range(3):
            for i in range(2 if small else 3):
                img.paste(ts.metatile(mp[f"patch:{k}_{i}{j}_marsh"]), ((x + i) * 16, (y + j) * 16))
                names[y + j][x + i] = f"patch:{k}_{i}{j}_marsh"

    put_cypress(8, 8, small=True)
    put_cypress(24, 8, small=True)
    for (x, y) in ((7, 4),):
        put_piece("live_oak", x, y)
        put_piece("live_oak", 30 - x, y)
    put_piece("mound_steps", 16, 10)
    put_piece("singing_stone", 16, 6)
    put_piece("landing", 15, 22)
    # the ceremonial shell road: from the landing's head up the aisle and across the plaza to the steps
    for y in range(12, 22):
        put_piece("shell_W", 16, y)
        put_piece("shell_E", 17, y)
    for (nm, x, y) in [("cedar_post_bird", 14, 12), ("cedar_post", 12, 13), ("stone_tall", 6, 13),
                       ("stone_tall", 14, 18), ("stone_small", 12, 7), ("stone_small", 13, 22)]:
        put_piece(nm, x, y)
        put_piece(nm, 33 - x, y)
    for (x, y) in ((12, 23), (21, 23), (10, 22)):
        if g[y][x] == "." and names[y][x] == "ekat:grass":
            put_piece("shell_scatter", x, y)

    # the two islets in the bottom corners (Route 25's marsh banks): scenery only. Rows 27-31 are the seam band
    # (primary pieces only): a small cypress clump and marsh plants there; reeds, cattails, knees, a log and the
    # egret post (secondary) only on rows <= 26, all off the channel to the landing (x 12-22).
    def water_free(x, y):
        return 0 <= x < W and 0 <= y < H and names[y][x] == "ekat:water_C" and g[y][x] == "~"

    for (x, y) in ((4, 28), (28, 28)):
        put_cypress(x, y, small=True)
    for (x, y, k) in ((3, 30, 1), (6, 31, 3), (7, 29, 1), (31, 30, 3), (27, 31, 1), (32, 29, 3)):
        if names[y][x] in ("ekat:marsh_C", "ekat:marsh_plants1", "ekat:marsh_plants3"):
            img.paste(ts.metatile(mp[f"ekat:marsh_plants{k}"]), (x * 16, y * 16))
            names[y][x] = f"ekat:marsh_plants{k}"

    def put_meta(name, x, y):
        img.paste(ts.metatile(mpb[name]), (x * 16, y * 16))
        names[y][x] = name

    for (x, y) in ((9, 24), (26, 24)):                  # cattails (1x2)
        if water_free(x, y) and water_free(x, y + 1):
            put_meta("patch:ovl_wpr_2_0__ekat_water_C", x, y)
            put_meta("patch:ovl_wpr_3_0__ekat_water_C", x, y + 1)
    for (x, y, k) in ((7, 25, 0), (11, 26, 1), (24, 26, 0), (28, 25, 1)):   # cypress knees
        if water_free(x, y):
            put_meta(f"patch:ovl_wpr_{k}_0__ekat_water_C", x, y)
    if water_free(9, 26) and water_free(10, 26):        # a drifted log against the west islet
        put_meta("ekat:waterlog_0", 9, 26)
        put_meta("ekat:waterlog_1", 10, 26)
    for (x, y) in ((23, 24), (11, 24)):                 # egrets on old posts
        if water_free(x, y) and water_free(x, y + 1):
            p_ = art["egret_post"]
            crop = sheet.crop((p_["x"] * 16, p_["y"] * 16, (p_["x"] + 1) * 16, (p_["y"] + 2) * 16))
            px_ = crop.load()
            for j in range(crop.height):
                for i in range(crop.width):
                    if px_[i, j][:3] == (255, 0, 255):
                        px_[i, j] = (0, 0, 0, 0)
            img.alpha_composite(crop, (x * 16, y * 16))
            names[y][x], names[y + 1][x] = "egret_post[0,0]", "egret_post[0,1]"
            break
    objs = [("rayquaza", 16, 9, "Rayquaza (raid object) on the mound, before the singing stone", False),
            ("player", 16, 10, "the player on the top step, facing Rayquaza (the raid)", True),
            ("jayden", 17, 10, "Jayden beside the player (2 v 1)", True),
            ("keeper", 15, 14, "the shrine keeper (NPC_0), beside the shell road", False),
            ("local", 18, 14, "NPC_1, beside the shell road", False),
            ("camille", 16, 23, "Camille holds the landing steps", False),
            ("andrew", 17, 20, "Andrew at the head of the steps, on the shell road in the aisle", False),
            ("item", 17, 24, "Dragoninite on the landing (post-game)", False)]
    for o in sorted(objs, key=lambda o: o[2]):
        paste_sprite(img, o[0], o[1], o[2], o[4])
    return img, names, g, objs, problems


# ------------------------------------------------------------------ outputs: the mocks at 3x and the review sheet
BG, FG, HEAD, DIM = (34, 36, 42), (230, 230, 225), (250, 220, 120), (160, 165, 170)


def caption(img, title, lines, scale_=3):
    """The mock at `scale_` with a caption band underneath (title + notes)."""
    big = scale(img.convert("RGB"), scale_)
    f, fb = font(15), font(20)
    h = 40 + 21 * len(lines) + 12
    meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = max([meas.textlength(l, font=f) for l in lines] + [meas.textlength(title, font=fb)]) + 24
    out = Image.new("RGB", (int(max(big.width, tw)), big.height + h), BG)
    out.paste(big, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((10, big.height + 8), title, fill=HEAD, font=fb)
    for k, l in enumerate(lines):
        d.text((10, big.height + 40 + 21 * k), l, fill=FG, font=f)
    return out


def compose_stats(recipe):
    r = subprocess.run([sys.executable, os.path.join(MAPGEN, "compose.py"), recipe], cwd=ROOT, check=True,
                       capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if "metatiles" in l and "tiles" in l][0]
    return line.strip()


def piece_images(json_name, sheet_png, over=None):
    """[(name, RGBA image of the piece as it will show, w, h)]: overlays drawn over `over` (16x16 ground)."""
    doc = json.load(open(os.path.join(HERE, json_name)))
    sheet = Image.open(os.path.join(HERE, sheet_png)).convert("RGBA")
    out = []
    for name, p in doc["pieces"].items():
        crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        if p.get("kind") == "overlay" and over is not None:
            px = crop.load()
            for j in range(crop.height):
                for i in range(crop.width):
                    if px[i, j][:3] == (255, 0, 255):
                        px[i, j] = (0, 0, 0, 0)
            bg = Image.new("RGBA", crop.size)
            for y in range(0, crop.height, 16):
                for x in range(0, crop.width, 16):
                    bg.paste(over, (x, y))
            bg.alpha_composite(crop)
            crop = bg
        if "top" in doc["pieces"][name] or os.path.exists(os.path.join(HERE, "recipes")):
            pass
        out.append((name, crop, p))
    return out, doc


def with_top(json_name, sheet_png, name):
    """An interior piece with its top layer drawn over it (as the GBA shows it)."""
    doc = json.load(open(os.path.join(HERE, json_name)))
    sheet = Image.open(os.path.join(HERE, sheet_png)).convert("RGBA")
    rec = None
    for r in os.listdir(os.path.join(HERE, "recipes")):
        d = json.load(open(os.path.join(HERE, "recipes", r)))
        if d["sources"][0]["image"].endswith(sheet_png):
            rec = d
    p = doc["pieces"][name]
    img = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
    for m in rec["sources"][0]["metatiles"]:
        if "top" in m and (m["id"] == name or m["id"].startswith(name + "_")):
            bx, by = m["bottom"]
            tx, ty = m["top"]
            top = sheet.crop((tx * 16, ty * 16, tx * 16 + 16, ty * 16 + 16))
            tp = top.load()
            for j in range(16):
                for i in range(16):
                    if tp[i, j][:3] == (255, 0, 255):
                        tp[i, j] = (0, 0, 0, 0)
            img.alpha_composite(top, ((bx - p["x"]) * 16, (by - p["y"]) * 16))
    return img


def section(items, title, sub, k=4, width=2000):
    """A sheet section: every piece at k x with its label; wraps at `width`."""
    from arena_art import tiles_of, tile_key
    f, fb, fs = font(13), font(22), font(15)
    pad, x, y, rowh = 14, 14, 70, 0
    placed = []
    for name, im, p, label in items:
        w, h = im.width * k, im.height * k
        lw = max(w, int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(label, font=f)) + 6)
        if x + lw > width - pad:
            x, y, rowh = 14, y + rowh + 44, 0
        placed.append((name, im, label, x, y))
        x += lw + pad
        rowh = max(rowh, h)
    H = y + rowh + 50
    out = Image.new("RGB", (width, H), BG)
    d = ImageDraw.Draw(out)
    d.text((14, 12), title, fill=HEAD, font=fb)
    d.text((14, 42), sub, fill=DIM, font=fs)
    for name, im, label, x, y in placed:
        out.paste(scale(im.convert("RGB"), k), (x, y))
        d.text((x, y + im.height * k + 4), label, fill=FG, font=f)
    return out


def distinct_tiles(im):
    from arena_art import tiles_of, tile_key
    return len({tile_key(t) for t in tiles_of(im.convert("RGBA"))})


def main():
    args = sys.argv[1:]
    if "--no-art" not in args:
        for s in ("make_temple.py", "make_cathedral.py", "make_shrine.py"):
            subprocess.run([sys.executable, os.path.join(HERE, s)], cwd=ROOT, check=True)
    stats = {}
    for d in ("orleans_temple", "orleans_saltdome"):
        stats[d] = compose_stats(os.path.join("tools/mapgen/tilesets/arenas/recipes", d + ".json"))
        print(stats[d])
    bad = {"orleans_temple": verify("dt", "orleans_temple", "temple.png"),
           "orleans_saltdome": verify("sc", "orleans_saltdome", "cathedral.png")}
    print("metatiles not drawing their art exactly:", bad)
    os.makedirs(REVIEW, exist_ok=True)

    # ---- the Drowned Temple
    t = temple_mock()
    timg = t.render()
    topen = temple_mock("open").render()
    cap = caption(timg, "Drowned Temple (Kyogre) - mock layout, 19 x 21, own secondary gTileset_OrleansTemple, 3x",
                  t.notes + [f"Tileset: {stats['orleans_temple']}; per-tile palette check 0 off-family; "
                             f"{bad['orleans_temple']} metatiles off their art."])
    inset = scale(topen.convert("RGB").crop((96, 96, 208, 192)), 3)
    cap.paste(inset, (cap.width - inset.width - 10 if cap.width > timg.width * 3 + inset.width else 0, 0)) if False else None
    cap.save(os.path.join(REVIEW, "drowned_temple_mock.png"))
    scale(topen.convert("RGB").crop((80, 48, 224, 208)), 3).save(os.path.join(REVIEW, "drowned_temple_door_open.png"))
    t.export(os.path.join(REVIEW, "drowned_temple_mock.json"))

    # ---- the Salt Cathedral
    c = cathedral_mock()
    cimg = c.render()
    caption(cimg, "Salt Cathedral (Groudon) - mock layout, 23 x 22, own secondary gTileset_OrleansSaltdome, 3x",
            c.notes + [f"Tileset: {stats['orleans_saltdome']}; per-tile palette check 0 off-family; "
                       f"{bad['orleans_saltdome']} metatiles off their art."]).save(
        os.path.join(REVIEW, "salt_cathedral_mock.png"))
    c.export(os.path.join(REVIEW, "salt_cathedral_mock.json"))

    # ---- the Oldest Shrine
    simg, names, g, objs, problems = shrine_mock()
    est = shrine_budget()
    notes = [
        "36 x 32 (the map's size), on orleans_route_b. Only the island and 2 cells round it are redrawn: the feathered water,",
        "the Surf-barrier cypress and Route 25's banks (rows 27-31, the seam band: primary only) are the built map's.",
        "Symmetric earthwork: terrain cell x mirrors to 34 - x; steps, singing stone and landing centre on the line between tiles 16|17.",
        "Platform mound (grid 'M', cells 13-21 x 7-10), steps (16-17, 10-11); two raised C-shaped banks (grid 'R', two cells thick)",
        "opening north, aisle x 15-19; the shell road (shell_W/E, x 16-17, rows 12-21) runs from the landing's head to the steps.",
        "Bottom islets: cypress clump + marsh plants in the seam band (primary), cattails/knees/log/egret post above it (rows <= 26).",
        "Rayquaza (16,9) before the singing stone; player (16,10) + Jayden (17,10) on the top step; keeper (15,14), NPC_1 (18,14);",
        "Camille (16,23) on the landing, Andrew (17,20) at its head in the aisle; Dragoninite (17,24); landing 4x4 at (15-18, 22-25).",
        f"New art on orleans_route_b: ~{est['tiles']} new 8x8 tiles (route_b holds 96/512 today), {est['palettes']} palettes "
        f"(its slots 8 and 11 are empty); autotile conflicts in this mock: {len(problems)}.",
    ]
    caption(simg, "The Oldest Shrine (Rayquaza) - mock layout over the built map, 3x", notes).save(
        os.path.join(REVIEW, "oldest_shrine_mock.png"))
    dump(os.path.join(REVIEW, "oldest_shrine_mock.json"), {
        "size": [36, 32], "tileset": "orleans_route_b",
        "terrain": ["".join(r) for r in g],
        "metatiles": [" ".join(n or "?" for n in r) for r in names],
        "objects": [{"sprite": o[0], "x": o[1], "y": o[2], "label": o[3]} for o in objs],
        "placements": "see arena_mocks.shrine_mock(): live_oak (7,4)+(23,4), cypress_small_marsh (8,8)+(24,8), "
                      "mound_steps (16,10), singing_stone (16,6), landing (15,22), shell road x 16-17 rows 12-21, "
                      "posts/stones mirrored x -> 33 - x, islet dressing as listed in the notes",
        "notes": notes, "autotile_conflicts": problems})

    review_sheet(stats, bad, est)


def shrine_budget():
    """Estimated cost on orleans_route_b: distinct new 8x8 tiles (flips free) of every shrine piece as it will be
    drawn (overlays over Ekat grass), minus tiles the primary already has (grass, water); palettes = families."""
    import make_shrine as S
    from arena_art import tiles_of, tile_key
    grass = S.ground("ekat:grass").convert("RGBA")
    water = S.ground("ekat:water_C").convert("RGBA")
    known = {tile_key(t) for t in tiles_of(grass)} | {tile_key(t) for t in tiles_of(water)}
    items, doc = piece_images("shrine.json", "shrine.png", over=grass)
    new = set()
    per = {}
    for name, im, p in items:
        ks = {tile_key(t) for t in tiles_of(im.convert("RGBA"))} - known
        per[name] = len(ks)
        new |= ks
    return {"tiles": len(new), "palettes": len(doc["families"]), "per": per}


def review_sheet(stats, bad, est):
    import make_shrine as S
    grass = S.ground("ekat:grass").convert("RGBA")
    secs = []
    # temple
    items, doc = piece_images("temple.json", "temple.png")
    its = []
    for name, im, p in items:
        if name.endswith("__top"):
            continue
        if name == "door_open":
            im = with_top("temple.json", "temple.png", name)
        its.append((name, im, p, f"{name} {p['w']}x{p['h']}: {distinct_tiles(im)} t"))
    secs.append(section(its, "Drowned Temple (Kyogre): gTileset_OrleansTemple, own secondary on orleans_building",
                        f"{stats['orleans_temple']}  |  budget 512 tiles / 512 metatiles / 7 palettes  |  families "
                        f"STONE, WATER, BELL (<= 15 each, every 8x8 tile checked)  |  {bad['orleans_temple']} metatiles off art  "
                        f"|  pieces at 4x, 't' = distinct 8x8 tiles in the piece"))
    # cathedral
    items, doc = piece_images("cathedral.json", "cathedral.png")
    its = []
    for name, im, p in items:
        if name.endswith("__top"):
            continue
        if name == "chandelier":
            im = with_top("cathedral.json", "cathedral.png", name)
        its.append((name, im, p, f"{name} {p['w']}x{p['h']}: {distinct_tiles(im)} t"))
    secs.append(section(its, "Salt Cathedral (Groudon): gTileset_OrleansSaltdome, own secondary on orleans_building",
                        f"{stats['orleans_saltdome']}  |  budget 512 tiles / 512 metatiles / 7 palettes  |  families "
                        f"SALT, MINE, HEAT  |  {bad['orleans_saltdome']} metatiles off art  |  pieces at 4x"))
    # shrine
    items, doc = piece_images("shrine.json", "shrine.png", over=grass)
    its = [(name, im, p, f"{name} {p['w']}x{p['h']} {p['kind']}: {est['per'][name]} new t") for name, im, p in items]
    secs.append(section(its, "The Oldest Shrine (Rayquaza): new pieces for orleans_route_b (overlays shown over Ekat grass)",
                        f"~{est['tiles']} new 8x8 tiles in all (route_b today: 96/512 tiles, 35 metatiles; Route 14 shares it)  "
                        f"|  {est['palettes']} palettes (families EARTH, STONE; route_b's slots 8 and 11 are empty)  |  pieces at 4x"))
    # the berm set laid out as a test patch, at 4x
    patch = berm_patch(grass)
    secs.append(section([("patch", patch, None, "ridges (R) and the mound (M) autotiled from a small grid, 4x")],
                        "Shrine earthworks test patch", "build.py corners() keys; the mound's face extension and steps below its south edge"))
    W = max(s.width for s in secs)
    H = sum(s.height for s in secs)
    out = Image.new("RGB", (W, H), BG)
    y = 0
    for s in secs:
        out.paste(s, (0, y))
        y += s.height
    out.save(os.path.join(REVIEW, "art_arenas.png"))
    print("wrote", os.path.join(REVIEW, "art_arenas.png"), out.size)


def berm_patch(grass):
    rows = ["..............",
            "..RRR.........",
            "..R.RR...MMMM.",
            "..R..R...MMMM.",
            "..RRRR...MMMM.",
            "..............",
            ".R.R..........",
            "..R...........",
            ".............."]
    g = [list(r) for r in rows]
    H, W = len(g), len(g[0])
    sheet = Image.open(os.path.join(HERE, "shrine.png")).convert("RGBA")
    art = json.load(open(os.path.join(HERE, "shrine.json")))["pieces"]
    img = Image.new("RGBA", (W * 16, H * 16))

    def ch(x, y):
        return g[max(0, min(H - 1, y))][max(0, min(W - 1, x))]

    for y in range(H):
        for x in range(W):
            cs = [ch(x, y), ch(x + 1, y), ch(x, y + 1), ch(x + 1, y + 1)]
            n = None
            for c in ("M", "R"):
                if c in cs:
                    key = CORNER_KEYS["".join("1" if q == c else "0" for q in cs)]
                    if c == "R":
                        n = f"berm_{key}"
                    elif key != "C":
                        n = f"mound_{key}"
            if n is None and "M" not in cs:
                nn, ne = ch(x, y - 1) == "M", ch(x + 1, y - 1) == "M"
                n = "mound_face" if nn and ne else ("mound_face_r" if nn else ("mound_face_l" if ne else None))
            if n:
                p = art[n]
                img.paste(sheet.crop((p["x"] * 16, p["y"] * 16, p["x"] * 16 + 16, p["y"] * 16 + 16)), (x * 16, y * 16))
            else:
                img.paste(grass, (x * 16, y * 16))
    p = art["mound_steps"]
    img.paste(sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + 2) * 16, (p["y"] + 2) * 16)), (10 * 16, 4 * 16))
    return img


if __name__ == "__main__":
    main()

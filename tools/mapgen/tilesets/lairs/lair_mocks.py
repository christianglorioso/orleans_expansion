"""Mock layouts of the batch-1 legendary lairs and their route entrances, rendered at 3x, plus the review sheet.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/lair_mocks.py [--no-art] [--no-compose]
    1. runs the art scripts (make_lairs_wet.py, make_lairs_dry.py, make_iceplant.py, make_entrances.py)
    2. composes the three lair secondaries into data/tilesets/secondary/<dir> (nothing registered) for the budgets
    3. builds each lair from its table below and writes ../tile_review/set_pieces/lairs/<lair>_mock.png (3x, with a
       caption) + <lair>_mock.json (terrain, metatile names, walkable mask, stand cells, entry/exit, notes); the
       rougarou also as it looks at night
    4. renders every route entrance (open and sealed) over the built route: <lair>_entrance.png
    5. writes the review sheet ../tile_review/set_pieces/lairs/art_lairs.png
The mocks are proposals: positions and stand cells are suggestions for the layout agent; data/ is not touched.
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import LairMap, MAPGEN, ROOT, dump, night, scale  # noqa: E402

REVIEW = os.path.normpath(os.path.join(ROOT, "..", "tile_review", "set_pieces", "lairs"))
BG, FG, HEAD, DIM = (34, 36, 42), (230, 230, 225), (250, 220, 120), (160, 165, 170)


def font(n=12):
    for f in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, n)
    return ImageFont.load_default()


def caption(img, title, lines, k=3):
    big = scale(img.convert("RGB"), k)
    f, fb = font(15), font(20)
    meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = max([meas.textlength(l, font=f) for l in lines] + [meas.textlength(title, font=fb)]) + 24
    out = Image.new("RGB", (int(max(big.width, tw)), big.height + 52 + 21 * len(lines)), BG)
    out.paste(big, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((10, big.height + 8), title, fill=HEAD, font=fb)
    for i, l in enumerate(lines):
        d.text((10, big.height + 40 + 21 * i), l, fill=FG, font=f)
    return out


# ---------------------------------------------------------------- terrain resolvers
def water_res(key, others):
    if key == "C":
        return "P:ekat:water_C"
    if others <= {"."} or others <= {"t", "."}:
        return f"P:ekat:water_{key}"
    if others <= {'"'}:
        return f"P:ekat:marshwater_{key}"
    return None


def marsh_res(key, others):
    return "P:ekat:marsh_C" if key == "C" else (f"P:ekat:marsh_{key}" if others <= {"."} else None)


def lw(name):
    return lambda key, others: f"lw:{name}_{key}"


WET_BASE = {".": ("P:ekat:grass", True), "~": ("P:ekat:water_C", False), '"': ("P:ekat:marsh_C", True),
            "R": ("P:ekat:grass", False), "t": ("lw:track_C", True), "m": ("lw:moss_C", True),
            "i": ("lw:isle_C", True), "s": ("lw:shallows_C", False)}


def wet_map(P, W=20, H=16, fill="."):
    sets = [("R", lw("levee"), False), ("i", lambda k, o: f"lw:isle_{k}" if o <= {"s"} else None, True),
            ("s", lambda k, o: f"lw:shallows_{k}" if o <= {"~"} else None, False), ("~", water_res, False),
            ('"', marsh_res, True), ("t", lw("track"), True), ("m", lw("moss"), True)]
    return LairMap(W, H, WET_BASE, sets, {"lw": P}, wall_style="swamp", fill=fill)


def wobble(seq):
    return lambda k: seq[k % len(seq)]


def corners_deep(n, extra=()):
    """1 block deep along a side, 2 at both ends (and at the block indices in `extra`)."""
    return lambda k: 2 if k in (0, n - 1) or k in extra else 1


def frame_std(m, extra_n=(), extra_s=(), extra_w=(), extra_e=()):
    BW, BH = (m.W + 1) // 2, (m.H + 1) // 2
    m.frame(corners_deep(BW, extra_n), corners_deep(BW, extra_s), corners_deep(BH, extra_w),
            corners_deep(BH, extra_e), gap={5})


# ---------------------------------------------------------------- 1. the rougarou's levee hollow (Route 14, night)
def rougarou(P):
    m = wet_map(P)
    frame_std(m)
    m.disc("~", 13.6, 5.0, 3.0, 1.5)                   # the black pond in the north-east, mist on it
    cy = 8.6
    for j in range(m.H):                               # the circling track round the hollow's heart
        for i in range(m.W):
            rho = math.hypot((i + 0.5 - 9.0) / 3.0, (j + 0.5 - cy) / 2.3)
            if 0.70 <= rho < 1.12 and m.g[j][i] == ".":
                m.g[j][i] = "t"
    for j in range(m.H):                               # the levee bank wraps it from the west round to the north
        for i in range(m.W):
            rho = math.hypot((i + 0.5 - 9.3) / 5.0, (j + 0.5 - cy) / 4.2)
            a = math.degrees(math.atan2(j + 0.5 - cy, i + 0.5 - 9.3))
            if 0.90 <= rho < 1.14 and (a < -80 or a > 140) and m.g[j][i] == "." and (i, j) not in m.wall                     and 4 <= j <= 9 and i >= 4:
                m.g[j][i] = "R"
    m.prop("lw", "dead_cypress", 14, 7)
    m.prop("lw", "dead_snag", 3, 9)
    m.prop("lw", "hunting_stand", 12, 10)
    m.prop("lw", "cross", 3, 3)
    m.prop("lw", "wisp_lantern", 16, 11)
    m.prop("lw", "fence_a", 8, 12)
    m.prop("lw", "fence_b", 7, 12)
    m.prop("lw", "fence_a", 14, 12)
    m.prop("lw", "driftwood", 5, 12)
    m.prop("lw", "clawed_stump", 11, 7)
    m.prop("lw", "clawed_stump", 6, 3)
    m.prop("lw", "bones", 3, 12)
    m.prop("lw", "bones", 13, 9)
    m.prop("lw", "trap", 9, 12)
    for (x, y) in [(10, 3), (12, 7), (16, 6), (17, 3)]:
        if m.g[y][x] == "." and not m.edge_cell(x, y):
            m.prop("lw", "cattails", x, y)
    for (x, y) in [(12, 5), (13, 5), (14, 5), (15, 5)]:
        if all(m.ch(x + dx, y + dy) == "~" for dx in (0, 1) for dy in (0, 1)):
            m.prop("lw", f"fog_water{x % 2}", x, y)
    for (x, y) in [(7, 3), (8, 3), (9, 3), (3, 6), (3, 7), (13, 4), (16, 9), (16, 10), (3, 11), (15, 12), (16, 12)]:
        if m.g[y][x] == "." and not m.edge_cell(x, y) and not any(px <= x < px + P.items[n]["cv"].cw and
                                                                    py <= y < py + P.items[n]["cv"].ch
                                                                    for (_, n, px, py) in m.props if _ == "lw"):
            m.prop("lw", f"fog_grass{x % 2}", x, y)
    m.obj("lycanroc", 9, 8, "the rougarou (Lycanroc Midnight, night only) in the middle of its track")
    m.obj("player", 10, 12, "the player, facing north")
    m.notes = [
        "20x16, unconnected, swamp canopy wall (primary art), the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "A hollow ringed by the levee bank (the shrine's ridge set), the circling track of trampled grass round the stand cell (9,8);",
        "a black pond with cattails in the north-east, two dead trees, an old hunting stand and broken fences by the way in, a",
        "wayside cross, a feu-follet lantern, driftwood, clawed stumps, bones and a sprung trap, mist along the edges.",
        "Night only: the hollow is the same by day (the rougarou object is hidden then); the lantern's flame reads best at night.",
    ]
    return m


# ---------------------------------------------------------------- 4. Celebi's time-shrine glade (Route 7)
def celebi(P):
    sets = [("~", water_res, False), ("m", lambda key, others: f"lk:moss_{key}" if others <= {"."} else None, True)]
    base = {".": ("P:ekat:grass", True), "~": ("P:ekat:water_C", False), "m": ("lk:moss_C", True)}
    m = LairMap(20, 16, base, sets, {"lk": P}, wall_style="swamp")
    frame_std(m)
    m.disc("m", 10.0, 9.0, 3.3, 2.5)                   # the sunken moss circle
    m.disc("~", 15.5, 11.7, 1.7, 1.2)                  # a spring pool in the south-east
    m.prop("lk", "live_oak", 3, 3)                     # two great oaks framing the north
    m.prop("lk", "live_oak", 13, 3)
    m.prop("lk", "spirit_house", 9, 4)                 # the spirit house on the axis, behind the sun stone
    m.prop("lk", "sun_stone", 9, 8)
    m.prop("lk", "cedar_post_bird", 7, 5)
    m.prop("lk", "cedar_post_bird", 12, 5)
    m.prop("lk", "stone_tall", 4, 8)
    m.prop("lk", "stone_tall", 15, 7)
    occupied = set()
    for (_, n, px, py) in m.props:
        cv = P.items[n]["cv"]
        occupied |= {(px + i, py + j) for i in range(cv.cw) for j in range(cv.ch)}

    def free(x, y):
        return (3 <= x <= 16 and 3 <= y <= 12 and m.g[y][x] == "." and (x, y) not in occupied
                and not m.edge_cell(x, y) and not (9 <= x <= 11 and y >= 11) and m.ch(x + 1, y) == "." and m.ch(x, y + 1) == "."
                and m.ch(x + 1, y + 1) == "." and m.ch(x - 1, y) != "~" and m.ch(x, y - 1) != "~")
    ring = []
    for k in range(48):                                # a full ring of lilies and ferns round the moss
        a = 2 * math.pi * k / 48
        x, y = int(round(9.6 + 5.0 * math.cos(a))), int(round(8.6 + 3.6 * math.sin(a)))
        if free(x, y) and (x, y) not in ring:
            ring.append((x, y))
    for k, (x, y) in enumerate(ring):
        m.prop("lk", ["lily_white", "fern", "lily_white", "lily_pink", "fern"][k % 5], x, y)
        occupied.add((x, y))
    for (x, y, n) in [(5, 11, "fern"), (6, 12, "mushrooms"), (13, 12, "fern"), (3, 7, "fern"), (16, 10, "fern"),
                      (4, 12, "mossy_stones"), (16, 5, "mossy_stones"), (7, 3, "mushrooms"), (12, 3, "fern"),
                      (8, 11, "dapple"), (12, 7, "dapple"), (6, 6, "dapple"), (14, 9, "dapple")]:
        if free(x, y):
            m.prop("lk", n, x, y)
            occupied.add((x, y))
    for (x, y) in [(8, 9), (11, 10), (12, 9)]:
        if all(m.ch(x + dx, y + dy) == "m" for dx in (0, 1) for dy in (0, 1)) and (x, y) not in occupied:
            m.prop("lk", "dapple_moss", x, y)
    lily_pads(m, [(15, 11), (16, 11)])
    m.obj("celebi", 10, 10, "Celebi (post-game) hovering before the sun stone")
    m.obj("player", 10, 12, "the player, facing north")
    m.notes = [
        "20x16, unconnected, swamp canopy wall, the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "A Rootkin shrine: two great live oaks frame the north, the palmetto-thatched spirit house stands on the axis behind",
        "the Rootkin sun stone at the heart of a sunken moss circle; carved cedar posts with egrets, spiral standing stones,",
        "a full ring of spider lilies and ferns, mossy stones, mushrooms, a spring pool and light dappling through the trees.",
        "Celebi at (10,10), the player at (10,12). Uxie, Mesprit and Azelf's shrines can share the set.",
    ]
    return m


# ---------------------------------------------------------------- 5. Suicune's hidden lagoon (Route 11)
def suicune(P):
    m = wet_map(P, fill="~")
    frame_std(m)
    m.rect(".", 0, 12, 20, 4)                           # the landing shore in the south
    m.disc("s", 10.5, 7.0, 4.6, 3.0, only="~")
    m.disc("i", 10.5, 6.8, 2.3, 1.6)
    m.prop("lw", "pillar", 10, 3)
    m.prop("lw", "causeway_v_sh", 10, 9)
    m.prop("lw", "causeway_v", 10, 10)
    m.prop("lw", "causeway_head", 10, 11)
    m.prop("lw", "causeway_broken", 5, 9)
    m.prop("lw", "stepping", 6, 10)
    m.prop("lw", "ruin", 4, 4)
    m.prop("lw", "ruin_l", 15, 8)
    def inner(ch, x, y, w=1, h=1):
        return all(m.ch(i, j) == ch for i in range(x, x + w + 1) for j in range(y, y + h + 1))
    for (x, y) in [(13, 3), (12, 3), (14, 3), (3, 9), (12, 10)]:
        if inner("~", x, y, 3, 1):
            m.prop("lw", "pillar_fallen", x, y)          # a second pillar, fallen into the lagoon
            break
    for (x, y) in [(6, 7), (7, 7), (6, 6), (13, 6), (12, 6), (13, 7)]:
        if inner("s", x, y, 3, 1):
            m.prop("lw", "pillar_fallen_sh", x, y)       # and a drum of it lying in the shallows
            break
    else:
        for (x, y) in [(13, 10), (3, 9), (4, 10), (14, 10)]:
            if inner("~", x, y, 3, 1) and not any(abs(px - x) < 4 and abs(py - y) < 2
                                                  for (_, n, px, py) in m.props if _ == "lw"):
                m.prop("lw", "pillar_fallen", x, y)      # (the shallows are too narrow: a second drum in the lagoon)
                break
    placed = 0
    for (x, y) in [(9, 8), (11, 8), (8, 8), (12, 8), (7, 7), (13, 7), (8, 4), (13, 5)]:
        if inner("s", x, y) and placed < 3 and not any(px <= x < px + P.items[n]["cv"].cw and py <= y < py + P.items[n]["cv"].ch
                                                       for (_, n, px, py) in m.props if _ == "lw"):
            m.prop("lw", "blocks_sh", x, y)              # broken causeway blocks tipped into the shallows
            placed += 1
    for x in (3, 5, 9, 15, 16):
        if m.g[3][x] == "~" and m.g[4][x] == "~" and not any(
                px <= x < px + P.items[n]["cv"].cw and py <= 3 < py + P.items[n]["cv"].ch
                for (_, n, px, py) in m.props if _ == "lw"):
            m.prop("lw", "reflection", x, 3)            # the trees' reflection under the north wall
    m.fixed = {(2, 11): "lw:shore_w", (17, 11): "lw:shore_e"}
    lily_pads(m, [(4, 7), (15, 4), (16, 6), (14, 10), (6, 4)])
    for (x, y) in [(3, 6), (16, 11), (4, 11)]:
        if all(m.ch(x + dx, y + dy) == "~" for dx in (0, 1) for dy in (0, 1)):
            m.prop("lw", f"fog_water{x % 2}", x, y)
    m.obj("suicune", 10, 7, "Suicune (post-game) on the island before the pillar")
    m.obj("player", 10, 9, "the player on the causeway at the island's foot, facing north")
    m.notes = [
        "20x16, unconnected, swamp canopy wall over the water; the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "A still lagoon; an island ringed by clear shallows, a carved pillar, a ruined causeway (walkable, x 10, rows 9-11) from",
        "the shore, its broken blocks tipped into the shallows, a broken spur with stepping stones, a second pillar fallen in the",
        "lagoon and a drum of it in the shallows, sunken ruins, the trees' reflection, lily pads and mist. Suicune at (10,7).",
        "The two cells where the bank meets the side walls are hand-made (shore_w / shore_e: the canopy over the bank).",
    ]
    return m


def lily_pads(m, cells):
    for (x, y) in cells:
        if all(m.ch(x + dx, y + dy) == "~" for dx in (-1, 0, 1, 2) for dy in (-1, 0, 1, 2)):
            m.props.append(("P", "ekat:water_lily", x, y))


# ---------------------------------------------------------------- the dry lairs
def ld(name, ground=("d",)):
    return lambda key, others: f"ld:{name}_{key}" if others <= set(ground) else None


DRY_BASE = {"d": ("P:dry:0_0", True), "r": ("ld:rock_C", False), "c": ("ld:clay_C", True), "a": ("ld:ash_C", True),
            "q": ("ld:pepper", False), "p": ("ld:pepper_burnt", False)}


def dry_map(P, W=20, H=16):
    sets = [("r", ld("rock", ("d",)), False), ("c", ld("clay"), True), ("a", ld("ash"), True)]
    m = LairMap(W, H, DRY_BASE, sets, {"ld": P}, wall_style="ld", fill="d")
    m.faces = {"r": {"face": "ld:rock_face", "face_l": "ld:rock_face_l", "face_r": "ld:rock_face_r"}}
    return m


# ---------------------------------------------------------------- 2. the Bloodmoon Ursaluna's arroyo den (Route 23)
def ursaluna(P):
    m = dry_map(P)
    frame_std(m)
    m.rect("r", 4, 4, 12, 2)                           # the arroyo's head wall in the north
    m.rect("r", 4, 6, 4, 6)                            # the west wall (cells 4-7)
    m.rect("r", 12, 6, 4, 6)                           # the east wall (cells 12-15)
    pass                                               # (red clay streaks the walls; the floor stays dry)
    m.prop("ld", "den", 8, 5)
    # the channel (floor tiles 8-10): the side walls drawn as cliffs, the west wall's shadow on the floor
    for y in range(8, 12):
        m.prop("ld", "cliff_w", 7, y)
        m.prop("ld", "floor_shadow", 8, y)
        m.prop("ld", "cliff_e", 11, y)
    m.prop("ld", "scarred_stump", 5, 12)
    m.prop("ld", "scarred_stump", 13, 12)
    m.prop("ld", "bones", 10, 10)
    m.prop("ld", "bones", 3, 12)
    m.prop("ld", "fur", 9, 9)
    m.prop("ld", "fur", 15, 12)
    for x in (4, 14):
        m.prop("ld", "rock_face_claw", x, 12)
    from lair_kit import hashn
    m.fixed = {}
    for y in range(m.H):                               # the rock tops: the set's weathered variants, cracks and slabs
        for x in range(m.W):
            if all(m.ch(x + dx, y + dy) == "r" for dx in (0, 1) for dy in (0, 1)):
                h = hashn(x, y, 99)
                if h < 0.55:
                    m.fixed[(x, y)] = ["ld:rock_C1", "ld:rock_C2", "ld:rock_C3"][int(h * 100) % 3]
    m.obj("ursaluna", 10, 8, "the Bloodmoon Ursaluna (post-game, night only) at its den")
    m.obj("player", 9, 11, "the player in the arroyo, facing north")
    m.notes = [
        "20x16, unconnected, dry scrub wall (the Route 23 border art), the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "A narrow, deep arroyo: two rock walls close in from both sides (lit rims, the west face in shade, the east face lit,",
        "red clay bleeding down both, the west wall's shadow across the floor), a channel three cells wide to the den: a slab",
        "of rock leaning over a bedding of leaves, fur and branches. Claw-scored faces and stumps, bones and shed fur.",
        "Ursaluna at (10,8) before the bedding, the player at (9,11).",
    ]
    return m


# ---------------------------------------------------------------- 7. Entei's burned cane field (Route 16)
def entei(P):
    m = dry_map(P)
    frame_std(m)
    m.rect("q", 3, 3, 14, 3)                           # the pepper field, north
    m.rect("p", 7, 4, 6, 2)                            # ... burned where it faced the fire
    m.rect("q", 3, 7, 2, 6)                            # and its rows down both sides
    m.rect("q", 15, 7, 2, 6)
    m.rect("p", 3, 7, 2, 2)
    m.rect("p", 15, 7, 2, 2)
    m.rect("a", 6, 7, 8, 5)                            # the ash ground round the braziers (rounded by the set)
    m.rect("a", 8, 12, 4, 1)
    for (x, y) in [(6, 7), (12, 7), (6, 9), (12, 9)]:
        m.prop("ld", "brazier", x, y)
    for (x, y) in [(8, 8), (11, 8), (9, 11)]:
        m.prop("ld", "vent", x, y)
    for (x, y) in [(10, 7), (8, 10), (11, 11), (7, 11)]:
        if m.g[y][x] == "a":
            m.prop("ld", "stubble", x, y)
    m.obj("entei", 9, 10, "Entei (post-game) in the ring of braziers")
    m.obj("player", 10, 13, "the player, facing north")
    m.notes = [
        "20x16, unconnected, dry scrub wall (the Route 16 border art), the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "Deep in the Route 16 pepper fields: pepper rows (the route's own field art) wrap a burned-out clearing, the rows nearest",
        "the fire burned black; ash ground, four stone braziers burning round it, glowing vents and burned stubble. Entei at (9,10).",
    ]
    return m


# ---------------------------------------------------------------- 6. Raikou's lightning-struck clearing (Route 2)
STORM_BASE = {".": ("P:ekat:grass", True), "s": ("ls:scorch_C", True)}


def raikou(Pst):
    sets = [("s", lambda key, others: f"ls:scorch_{key}" if others <= {"."} else None, True)]
    m = LairMap(20, 16, STORM_BASE, sets, {"ls": Pst}, wall_style="swamp")
    frame_std(m)
    m.disc("s", 10.0, 9.4, 4.4, 2.9)
    for (x, y) in [(9, 9), (10, 9), (9, 10), (10, 10)]:
        m.prop("ls", "scorch_core", x, y)
    m.prop("ls", "glass", 8, 8)
    m.prop("ls", "glass", 12, 9)
    m.prop("ls", "snag", 9, 3)
    m.prop("ls", "tower", 3, 3)                        # the transmission towers: two standing, the line snapped
    m.prop("ls", "tower", 15, 3)                       # where the strike came down, one tower knocked flat
    for x in range(5, 8):
        m.prop("ls", "wire_span", x, 3)
    m.prop("ls", "wire_span_r", 8, 3)
    m.prop("ls", "wire_span_l", 12, 3)
    for x in range(13, 15):
        m.prop("ls", "wire_span", x, 3)
    m.prop("ls", "tower_down", 13, 11)
    m.prop("ls", "transformer", 3, 9)
    m.prop("ls", "wire", 5, 12)
    m.obj("raikou", 10, 10, "Raikou (post-game) on the strike's heart")
    m.obj("player", 10, 13, "the player, facing north")
    m.notes = [
        "20x16, unconnected, swamp canopy wall (primary art), the way in from the south (x 10-11, rows 14-15: exit trigger).",
        "A clearing where lightning struck: a ring of char and singed grass, its heart fused with fern-like scars and",
        "fulgurites, a struck cypress, the Route 2 transmission line: two towers standing, the line snapped between them, one tower",
        "knocked flat, a torn-down transformer sparking, a fallen live line.",
        "Raikou at (10,10), the player at (10,13).",
    ]
    return m


# ---------------------------------------------------------------- 3. Articuno: the frozen hall of the ice plant
def articuno(Pi):
    base = {"f": ("ip:floor", True), "i": ("ip:ice_C", True)}
    sets = [("i", lambda key, others: f"ip:ice_{key}" if others <= {"f"} else None, True)]
    m = LairMap(19, 14, base, sets, {"ip": Pi}, wall_style="none", fill="f")
    m.disc("i", 9.5, 6.6, 5.6, 3.9)
    for x in range(1, 18):
        m.prop("ip", "cap", x, 0)
        m.prop("ip", {3: "wall_vent", 15: "wall_vent", 6: "wall_pipe", 7: "wall_pipe", 11: "wall_pipe",
                      12: "wall_pipe"}.get(x, "wall"), x, 1)
        m.prop("ip", "wall_s", x, 13)
    for y in range(0, 13):
        m.prop("ip", "side_l", 0, y)
        m.prop("ip", "side_r", 18, y)
    m.prop("ip", "wall_sw", 0, 13)
    m.prop("ip", "wall_se", 18, 13)
    m.prop("ip", "mat", 9, 13)
    m.prop("ip", "dais", 8, 4)
    m.prop("ip", "light", 8, 6)
    m.prop("ip", "ice_crack", 6, 5)
    m.prop("ip", "ice_crack", 12, 8)
    m.prop("ip", "tank", 1, 3)
    m.prop("ip", "tank", 16, 3)
    m.prop("ip", "compressor", 16, 7)
    m.prop("ip", "compressor", 1, 7)
    for (x, n) in [(1, "conveyor_l"), (2, "conveyor"), (3, "ice_block"), (4, "conveyor"), (5, "conveyor_r")]:
        m.prop("ip", n, x, 11)
    for (x, n) in [(13, "conveyor_l"), (14, "ice_block"), (15, "conveyor"), (16, "ice_block"), (17, "conveyor_r")]:
        m.prop("ip", n, x, 11)
    for (x, y) in [(1, 6), (17, 6), (3, 3), (15, 3)]:
        m.prop("ip", "ice_stack", x, y)
    m.obj("articuno", 9, 5, "Articuno (post-game) on the ice dais under the broken skylight")
    m.obj("player", 9, 6, "the player in the shaft of light, facing north")
    m.notes = [
        "19x14, the existing PointeRouge_IcePlant redone on its own secondary (gTileset_OrleansIcePlant on orleans_building).",
        "The exit stays where it is: the mat at (9,13) (warp to Pointe Rouge warp 8). Articuno keeps its cell (9,5), the dais's front middle; the player faces it from (9,6).",
        "A frozen plant hall: sheet ice spreading from the dais, a shaft of cold light and a drift of snow under the broken",
        "skylight, rimed brine tanks and compressors, two frozen conveyor runs with ice blocks left on them, icicles on the walls.",
    ]
    return m


# ---------------------------------------------------------------- the route entrances, sealed and open
ENTRANCES = {
    # lair: (route map, crop (x, y, w, h), sealed actions, open actions)
    "rougarou": ("Route14", (14, 24, 14, 11), [], [("ovl", "canopy_gap_w", 25, 30)]),
    "ursaluna": ("Route23", (14, 0, 18, 10), [("fill", "dry", 22, 0, 2, 2)],
                 [("ovl", "scrub_gap", 22, 1), ("ovl", "claw_stump", 21, 2)]),
    "celebi": ("Route7", (26, 0, 18, 10), [("ovl", "stone_arch_vines", 34, 1)], [("ovl", "stone_arch", 34, 1)]),
    "suicune": ("Route11", (21, 15, 16, 10), [("decypress",), ("ovl", "stone_arch_vines", 28, 20)],
                [("decypress",), ("ovl", "stone_arch_mist", 28, 20)]),
    "raikou": ("Route2", (17, 0, 16, 10), [("fill", "swamp", 24, 0, 2, 2)], []),
    "entei": ("Route16", (8, 0, 18, 10), [("fill", "dry", 14, 0, 4, 2)],
              [("ovl", "scrub_gap", 15, 1), ("ovl", "charred_stake", 17, 2)]),
}


def route_render(route):
    import re
    import struct
    import render
    L = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"] if "id" in l}
    d = json.load(open(os.path.join(ROOT, f"data/maps/{route}/map.json")))
    lay = L[d["layout"]]

    def snake(sym):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", sym.replace("gTileset_", "")).lower()
    sec = snake(lay["secondary_tileset"])
    ts = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_general"),
                         os.path.join(ROOT, f"data/tilesets/secondary/{sec}"))
    names = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]
    names.update(json.load(open(os.path.join(MAPGEN, "tilesets", f"{sec}.mapping.json")))["metatiles"])
    raw = open(os.path.join(ROOT, lay["blockdata_filepath"]), "rb").read()
    blocks = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    return ts, names, blocks, lay["width"], lay["height"], sec


def entrance_panel(lair, which):
    route, (cx, cy, cw, ch), sealed, opened = ENTRANCES[lair]
    ts, names, blocks, W, H, sec = route_render(route)
    inv = {v: k for k, v in names.items()}
    acts = sealed if which == "sealed" else opened
    grid = [[blocks[y * W + x] & 0x3FF for x in range(W)] for y in range(H)]
    ovl = []
    for a in acts:
        if a[0] == "fill":                          # close a feather notch with the wall block, faces below it
            _, style, x0, y0, w, h = a
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    n = f"bd:swamp_canopy_{x & 1}{y & 1}" if style == "swamp" else f"bd:dry_scrub_{x & 1}{y & 1}"
                    grid[y][x] = names[n]
            for x in range(x0, x0 + w):
                n = f"patch:bdg_swamp_S{x & 1}_542aa1ca" if style == "swamp" else f"bd:dry_S_dry_{x & 1}"
                if n in names:
                    grid[y0 + h][x] = names[n]
        elif a[0] == "decypress":                   # the island's cypress makes way for the arch
            for y in range(H):
                for x in range(W):
                    n = inv.get(grid[y][x], "")
                    if n.startswith("patch:cypress") and n.endswith("_marsh"):
                        grid[y][x] = names["ekat:marsh_C"]
                    elif n.startswith("patch:cypress") and n.endswith("_water"):
                        grid[y][x] = names["ekat:water_C"]
        else:
            ovl.append(a)
    img = Image.new("RGBA", (cw * 16, ch * 16))
    for y in range(cy, cy + ch):
        for x in range(cx, cx + cw):
            img.paste(ts.metatile(grid[y][x]), ((x - cx) * 16, (y - cy) * 16))
    sheet = Image.open(os.path.join(HERE, "entrances.png")).convert("RGBA")
    art = json.load(open(os.path.join(HERE, "entrances.json")))["pieces"]
    for (_, name, x, y) in ovl:
        p = art[name]
        crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        px = crop.load()
        for j in range(crop.height):
            for i in range(crop.width):
                if px[i, j][:3] == (255, 0, 255):
                    px[i, j] = (0, 0, 0, 0)
        img.alpha_composite(crop, ((x - cx) * 16, (y - cy) * 16))
    return img, route, sec


def entrance_mock(lair, notes):
    a, route, sec = entrance_panel(lair, "sealed")
    b, _, _ = entrance_panel(lair, "open")
    A, B = scale(a.convert("RGB"), 3), scale(b.convert("RGB"), 3)
    f, fb = font(15), font(20)
    out = Image.new("RGB", (A.width + B.width + 24, A.height + 40 + 52 + 21 * len(notes)), BG)
    d = ImageDraw.Draw(out)
    d.text((8, 8), "sealed (during the story)", fill=HEAD, font=fb)
    d.text((A.width + 24, 8), "open", fill=HEAD, font=fb)
    out.paste(A, (0, 40))
    out.paste(B, (A.width + 24, 40))
    y = A.height + 48
    d.text((8, y), f"{route} entrance to the {lair} lair (route tileset {sec}), 3x", fill=HEAD, font=fb)
    for i, l in enumerate(notes):
        d.text((8, y + 30 + 21 * i), l, fill=FG, font=f)
    return out


ENTRANCE_NOTES = {
    "rougarou": ["Route 14, the east canopy wall beside the pond (cells 26, 30-31): a trail opens into the trees.",
                 "Sealed: the canopy as built. Open from story ch7 (the flood clears), any hour; the rougarou inside is night-only.",
                 "Walking east into (26,30) or (26,31) warps to the hollow (coord trigger); art: canopy_gap_w (overlay, canopy colours)."],
    "ursaluna": ["Route 23, a feather notch in the north scrub (cells 22-23, rows 0-1) becomes a cleft, a clawed stump beside it.",
                 "Sealed: the notch filled with the scrub block. Open from story 45 (post-game); Ursaluna is inside at night.",
                 "Walking north into (22,1) or (23,1) warps to the arroyo; art: scrub_gap + claw_stump (overlays, scrub colours)."],
    "celebi": ["Route 7, a feather notch in the north canopy (cells 34-35, rows 1-2): a Rootkin stone arch stands in it.",
               "Sealed: a curtain of vines fills the arch. Open from story 45: the way through the arch.",
               "Walking north into (34,2) or (35,2) warps to the shrine glade; art: stone_arch / stone_arch_vines (overlays)."],
    "suicune": ["Route 11, the hexagon island in the big lake: its cypress makes way for a Rootkin arch (28-29, 20-21).",
                "Sealed: a curtain of vines. Open from story 45: mist shimmers in the arch (the hidden island beyond).",
                "Surf to the island, walk north into (28,21) or (29,21): warp to the lagoon; art: stone_arch_mist / _vines."],
    "raikou": ["Route 2, the feather notch in the north canopy right above the old encounter cell (24-25, rows 0-1).",
               "No new art (the Port tileset is full): sealed = the notch filled with the canopy block (primary pieces);",
               "open from story 45 = the map as built. Walking north into (24,0) or (25,0) warps to the struck clearing."],
    "entei": ["Route 16, the feather notch in the north scrub above the pepper fields (14-17, rows 0-1): a cleft, a charred stake.",
              "Sealed: the notch filled with the scrub block. Open from story 45.",
              "Walking north into (15,1) or (16,1) warps to the burned field; art: scrub_gap + charred_stake (overlays)."],
}


# ---------------------------------------------------------------- the pipeline
TILESETS = [  # (art script, module, recipe dir, sheet, prefix, primary dir, lairs)
    ("make_lairs_wet.py", "make_lairs_wet", "orleans_lairs_wet", "lairs_wet.png", "lw", "orleans_general", "rougarou, Suicune"),
    ("make_lair_rootkin.py", "make_lair_rootkin", "orleans_lair_rootkin", "lair_rootkin.png", "lk", "orleans_general",
     "Celebi (room for Uxie, Mesprit, Azelf later)"),
    ("make_lairs_dry.py", "make_lairs_dry", "orleans_lairs_dry", "lairs_dry.png", "ld", "orleans_general", "Bloodmoon Ursaluna, Entei"),
    ("make_lair_storm.py", "make_lair_storm", "orleans_lair_storm", "lair_storm.png", "ls", "orleans_general", "Raikou"),
    ("make_iceplant.py", "make_iceplant", "orleans_iceplant", "iceplant.png", "ip", "orleans_building", "Articuno"),
]

LAIRS = [  # (key, title, builder, prefix of its pieces)
    ("rougarou", "The rougarou's levee hollow (Lycanroc Midnight), off Route 14", "rougarou", "lw"),
    ("ursaluna", "The Bloodmoon Ursaluna's arroyo den, off Route 23", "ursaluna", "ld"),
    ("articuno", "Articuno: the frozen hall of the Pointe Rouge ice plant", "articuno", "ip"),
    ("celebi", "Celebi's Rootkin shrine glade, off Route 7", "celebi", "lk"),
    ("suicune", "Suicune's hidden island in the big lake, off Route 11", "suicune", "lw"),
    ("raikou", "Raikou at the Route 2 transmission towers: the struck clearing", "raikou", "ls"),
    ("entei", "Entei in the Route 16 pepper fields: the burned field", "entei", "ld"),
]

BEFORE = {
    "rougarou": "Before ch7 the Route 14 entrance is the canopy as built (no way in); from ch7 the trail is open at any hour, but the "
                "rougarou only stands in its track at night (its object is hidden by day): by day an empty, misty hollow.",
    "ursaluna": "Before story 45 the Route 23 cleft is closed by the scrub; afterwards the arroyo is open, the den empty by day "
                "(Ursaluna only at night, FLAG_PG_URSALUNA_BM).",
    "articuno": "The room is the existing ice plant interior (Pointe Rouge, warp 8), reachable in the story: the same frozen hall, "
                "the dais empty (Articuno hidden until story 45, FLAG_PG_ARTICUNO).",
    "celebi": "Before story 45 the Route 7 arch is filled with a curtain of vines; afterwards the way through is open.",
    "suicune": "Before story 45 the island's arch (in place of its cypress) is filled with vines; afterwards mist shimmers in it.",
    "raikou": "Before story 45 the feather notch in Route 2's north canopy is filled with the canopy block (no new art); "
              "afterwards it is open as built.",
    "entei": "Before story 45 the Route 16 cleft is closed by the scrub; afterwards it is open, a charred stake beside it.",
}


def verify(recipe_dir, sheet_png, prefix, primary_dir):
    """Every composed metatile must draw its art; returns (metatiles off, worst colour shift)."""
    import render
    mp = json.load(open(os.path.join(HERE, f"{recipe_dir}.mapping.json")))["metatiles"]
    rec = json.load(open(os.path.join(HERE, "recipes", f"{recipe_dir}.json")))
    ts = render.Tilesets(os.path.join(ROOT, f"data/tilesets/primary/{primary_dir}"),
                         os.path.join(ROOT, f"data/tilesets/secondary/{recipe_dir}"))
    sheet = Image.open(os.path.join(HERE, sheet_png)).convert("RGB")
    off, worst = 0, 0.0
    for m in rec["sources"][0]["metatiles"]:
        bx, by = m["bottom"]
        ref = sheet.crop((bx * 16, by * 16, bx * 16 + 16, by * 16 + 16)).load()
        got = ts.metatile(mp[f"{prefix}:{m['id']}"]).convert("RGB").load()
        bad = False
        for y in range(16):
            for x in range(16):
                a, b = ref[x, y], got[x, y]
                a = tuple((v >> 3) << 3 for v in a)
                if a != b:
                    bad = True
                    worst = max(worst, sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5)
        off += bad
    return off, worst


def main():
    import importlib
    args = sys.argv[1:]
    os.makedirs(REVIEW, exist_ok=True)
    mods, stats = {}, {}
    for (script, mod, rdir, png, prefix, prim, lairs) in TILESETS:
        if "--no-art" not in args:
            subprocess.run([sys.executable, os.path.join(HERE, script)], cwd=ROOT, check=True, capture_output=True)
        M = importlib.import_module(mod)
        P = M.build()
        P.pack()
        mods[prefix] = P
        if "--no-compose" not in args:
            r = subprocess.run([sys.executable, os.path.join(MAPGEN, "compose.py"),
                                f"tools/mapgen/tilesets/lairs/recipes/{rdir}.json"], cwd=ROOT, check=True,
                               capture_output=True, text=True)
            line = [l for l in r.stdout.splitlines() if "metatiles" in l and "tiles" in l][0].strip()
            squeeze = [l.strip() for l in r.stdout.splitlines() if "colours in 15" in l or "reduced to 15" in l]
            off, worst = verify(rdir, png, prefix, prim)
            stats[rdir] = (line, squeeze, off, worst, lairs)
            print(line, squeeze, f"off {off} worst {worst:.1f}")
    subprocess.run([sys.executable, os.path.join(HERE, "make_entrances.py")], cwd=ROOT, check=True, capture_output=True)
    lair_imgs = {}
    for (key, title, fn, prefix) in LAIRS:
        m = globals()[fn](mods[prefix])
        img = m.render()
        lair_imgs[key] = img
        rec = [r for r in TILESETS if r[4] == prefix][0]
        st = stats.get(rec[2])
        lines = m.notes + ["Before it opens: " + BEFORE[key]]
        if st:
            lines.append(f"Tileset {rec[2]} ({rec[6]}): {st[0]}")
        if m.problems:
            lines.append(f"autotile conflicts left in the mock: {m.problems}")
        caption(img, title + " - mock, 3x", lines).save(os.path.join(REVIEW, f"{key}_mock.png"))
        if key == "rougarou":
            caption(night(img), title + " - at night (the day/night tint, approximated), 3x", lines).save(
                os.path.join(REVIEW, "rougarou_mock_night.png"))
        stand = [o for o in m.objs if o[0] != "player"]
        player = [o for o in m.objs if o[0] == "player"]
        m.export(os.path.join(REVIEW, f"{key}_mock.json"), {
            "tileset": rec[2], "primary": rec[5],
            "encounter_cell": [stand[0][1], stand[0][2]] if stand else None,
            "player_cell": [player[0][1], player[0][2]] if player else None,
            "entry": ENTRY.get(key), "before": BEFORE[key]})
    for key in ENTRANCES:
        entrance_mock(key, ENTRANCE_NOTES[key]).save(os.path.join(REVIEW, f"{key}_entrance.png"))
    review_sheet(mods, stats, lair_imgs)


ENTRY = {
    "rougarou": {"arrive": [10, 13], "exit": [[10, 14], [11, 14], [10, 15], [11, 15]], "to": "Route14 (25,30), facing west"},
    "ursaluna": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route23 (22,2), facing south"},
    "articuno": {"arrive": [9, 12], "exit": [[9, 13]], "to": "PointeRouge warp 8 (the existing door)"},
    "celebi": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route7 (34,3), facing south"},
    "suicune": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route11 (28,22), facing south"},
    "raikou": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route2 (24,1), facing south"},
    "entei": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route16 (15,2), facing south"},
}


def section(items, title, sub, k=4, width=2000):
    f, fb, fs = font(13), font(22), font(15)
    meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pad, x, y, rowh = 14, 14, 70, 0
    placed = []
    for (im, label) in items:
        w, h = im.width * k, im.height * k
        lw = max(w, int(meas.textlength(label, font=f)) + 6)
        if x + lw > width - pad:
            x, y, rowh = 14, y + rowh + 44, 0
        placed.append((im, label, x, y))
        x += lw + pad
        rowh = max(rowh, h)
    out = Image.new("RGB", (width, y + rowh + 50), BG)
    d = ImageDraw.Draw(out)
    d.text((14, 12), title, fill=HEAD, font=fb)
    d.text((14, 42), sub, fill=DIM, font=fs)
    for im, label, x, y in placed:
        out.paste(scale(im.convert("RGB"), k), (x, y))
        d.text((x, y + im.height * k + 4), label, fill=FG, font=f)
    return out


def review_sheet(mods, stats, lair_imgs):
    from lair_kit import tiles_of_count
    secs = []
    for (script, mod, rdir, png, prefix, prim, lairs) in TILESETS:
        P = mods[prefix]
        items = []
        for n in P.order:
            if "_" in n and n.rsplit("_", 1)[1] in ("N", "S", "W", "E", "inNW", "inNE", "inSW", "inSE", "landSE",
                                                    "landSW", "landNE", "landNW", "sTLBR", "sTRBL") and not n.startswith("rock_face"):
                continue                                      # the corner sets are shown as test patches in the mocks
            cv = P.items[n]["cv"]
            items.append((cv.im, f"{n} {cv.cw}x{cv.ch}: {tiles_of_count(cv.im)} t"))
        st = stats.get(rdir)
        sub = (f"{st[0]}  |  budget 512 tiles / 512 metatiles / 7 palettes  |  squeeze: {st[1] or 'none'}  |  metatiles "
               f"off their art: {st[2]} (worst shift {st[3]:.0f})" if st else "")
        secs.append(section(items, f"{rdir} (prefix {prefix}, on {prim}): {lairs}", sub + "  |  corner sets: C only (all "
                            "15 keys in the sheet); 4x, t = distinct 8x8 tiles", k=4))
    ent = json.load(open(os.path.join(HERE, "entrances.json")))
    sheet = Image.open(os.path.join(HERE, "entrances.png")).convert("RGBA")
    items = []
    for n, p in ent["pieces"].items():
        crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        items.append((crop, f"{n} {p['w']}x{p['h']} overlay"))
    secs.append(section(items, "Route entrances (overlays; magenta = clear; composed into each route's own tileset)",
                        "canopy_gap_w (Route 14), stone_arch / _mist / _vines (Routes 7, 11), scrub_gap (Routes 23, 16), "
                        "claw_stump (23), charred_stake (16); Route 2: no new art", k=4))
    W = max(s.width for s in secs)
    out = Image.new("RGB", (W, sum(s.height for s in secs)), BG)
    y = 0
    for s in secs:
        out.paste(s, (0, y))
        y += s.height
    out.save(os.path.join(REVIEW, "art_lairs.png"))
    print("wrote", os.path.join(REVIEW, "art_lairs.png"), out.size)


if __name__ == "__main__":
    main()

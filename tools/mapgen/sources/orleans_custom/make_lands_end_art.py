"""Own art for Land's End, the stilt town where the delta meets the Gulf (gym 8, Heron).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_lands_end_art.py
writes (16x16 cells, magenta = transparent):
    lands_end_planks.png   the boardwalk planks, opaque (placed as plain metatiles, walkable)
    lands_end_art.png      everything drawn over water, mud or planks (overlays)
    lands_end.json         piece -> sheet, cell rectangle, doors, walkable cells (read by tools/mapgen/lands_end_tileset.py)
    lands_end_preview.png  every piece at 3x over water
    ../../maps/00_lands_end_art.png   the review sheet: every piece at 3x over Ekat water or the boardwalk, a test patch
                           of the town at 3x, and the tile census (marginal 8x8 tiles per piece group against the
                           budget in art_requests/lands_end.md)

Pieces
    h<edges>, v<edges>    narrow wooden boardwalk planks: h = an east-west run (boards laid north-south), v = a
                          north-south run (boards laid east-west); <edges> lists the open sides (n, s, w, e): the
                          north edge is a thin lit lip, the south edge shows the deck's timber face
    skirt, skirt_e        the pilings under a deck's south face (shadow lip, posts, ripples); _e adds the end post
    skirt_plain           the shadow lip and a few ripples with no post (the cells between the pilings)
    mskirt, mskirt_e      the same standing in the mudflat (no ripples)
    pc_skirt              4x1, the pilings row under the Pokemon Center's south wall (the skirt's own tiles; the door
                          column is left empty for the boardwalk)
    house_<roof><w>[_mud] a house on pilings: the Shady Forest cabin's front wall (tools/mapgen/sources/shady_forest, the
                          art the bayou towns use) under a shingle roof redrawn on an 8 px repeat in the house's own
                          colour, a floor beam on braced posts and a flight of steps down from the door
    pavilion              the Rain Pavilion (gym): an open timber pavilion under a hipped standing-seam tin roof, a heron
                          weathervane, rain chains into rain barrels at the corners, and seven carved heron verse panels
                          (three each side of the doorway, a spread-wing heron over it), 9x5, door (4,4)
    lookout               the Lookout: a timber watchtower on X-braced legs, glazed lookout cabin under a pyramid roof,
                          catwalk, pennant, the base room with its door, 3x7, door (1,6)
    station               the Tide Gauge & Weather Station: a white clapboard hut under a tin roof, the instrument mast
                          (anemometer cups, wind vane), a Stevenson screen, the red-and-white tide staff on its pile and
                          the stilling well with its recorder box, 5x4, door (1,3)
    shop                  Marine Supply (the Mart): a board-and-batten chandlery under a blue tin roof, the MARINE SUPPLY
                          signboard, a life ring over the glazed door (an anchor on its glass), buoys, display windows
                          with nets hung in them, a rope coil by the door, 5x4, door (2,3)
    trawler_a, trawler_b  Gulf shrimp trawlers, 6x3 overlays on open water: a white planked hull with a pointed, flared
                          bow, the sheer line (rub rail) sweeping up to the stem, a red boot stripe and the waterline
                          shadow; the pilothouse forward with a lit window; the mast behind it with both outrigger booms
                          raised in a tall V, the nets bunched up along them and the trawl doors hanging at the tips;
                          the work deck aft (hatch, winch, shrimp baskets); a mooring line to the east edge. A: bow
                          east, red trim. B: A mirrored (bow west, so every hull, deck and rigging tile is shared) with a
                          blue-trimmed pilothouse and its line from the stern.
    heron_pile            a white egret standing on an old piling in the water, 1x2 (the piling is `pile`)
    pile                  a lone mooring piling with a rope collar, 1x1
    sign                  a small wooden sign on the boardwalk, 1x1
    lantern, bollard      deck dressing, 1x1 overlays on the planks: a lantern post, a bollard with a rope

Colours: every 8x8 tile is an exact subset of one palette the built orleans_harbor tileset already has (the palettes
are at their limit, so no new hue is introduced): the houses' roofs and walls are the Shady cabin's own (palettes 6
and 10); everything else is drawn in two families, WATER (the tin greens, the wood, the rope, cream and the ripple:
palette 11) and HULL (whites, the glass, red, blue, the lit window and the wood: palette 12). Tiles that touch the
water's ripples are WATER tiles; tiles with white, glass, red or blue are HULL tiles. check() lists any tile that
fits no palette.

Tile economy (orleans_harbor holds 512 tiles; Land's End is its only map): every texture (shingles, tin seams,
clapboard, board-and-batten, planks, hull side, the X bracing) repeats every 8 px on the piece's origin, so a run of
wall or roof costs one tile; symmetric pieces are drawn on the left and mirrored about a tile line (flipped tiles are
free); the five houses share every wall, beam, post and step tile and differ only in their roof colour (four tile
rows of three tiles each, repeated down the slope); trawler B is trawler A mirrored.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MAPGEN = os.path.join(ROOT, "tools", "mapgen")
KEY = (255, 0, 255)

# ---- colours. The house roofs and walls keep the Shady Forest cabin's own colours (palettes 6 and 10).
OUT = (32, 40, 64)
NAVY = (48, 56, 88)
SHD = (64, 48, 56)
# the planks (unchanged from the first drawing: their tiles are the boardwalk the layout is built on)
WH, W1, W2 = (168, 136, 104), (144, 112, 88), (128, 96, 80)   # boards: lit edge, board, alternate board
WG, WF, WD = (88, 64, 56), (104, 80, 64), (72, 56, 56)       # gaps, the deck's timber face, its dark underside
PL = (120, 96, 80)
WATER = (96, 136, 136)                                       # Ekat water (the flat stand-in)
# WATER family (palette 11): ink, wood, tin greens, rope, cream, stone, the ripple
INK = (40, 40, 56)
WK = (96, 72, 56)
GREY = (144, 144, 152)
CREAM, STONE, ROPE = (232, 224, 200), (192, 184, 168), (208, 184, 128)
TIN_D, TIN, TIN_L, TIN_H = (56, 80, 80), (80, 112, 104), (104, 136, 120), (136, 168, 144)
RIP = (136, 176, 176)
# HULL family (palette 12): ink, wood, whites, glass, red, blue, the lit window
DK = (80, 56, 56)
WHITE, WHITE_D = (232, 232, 224), (192, 192, 184)
GLASS, GLASS_D = (160, 208, 216), (104, 152, 176)
RED = (192, 72, 56)
BLUE_D, BLUE = (56, 72, 120), (72, 104, 160)
YELLOW = (248, 232, 128)

# the cabin's roof colours and the recolours that give each house its own roof (dark, mid, light)
CABIN_ROOF = [(64, 48, 56), (104, 72, 80), (128, 88, 104), (88, 72, 80)]
ROOFS = {
    "plum": CABIN_ROOF,
    "slate": [(48, 56, 72), (80, 96, 112), (104, 120, 136), (72, 80, 96)],
    "rust": [(88, 48, 40), (136, 72, 56), (168, 104, 80), (112, 64, 56)],
    "moss": [(48, 64, 48), (80, 104, 72), (104, 128, 88), (64, 88, 64)],
    "teal": [(40, 72, 80), (64, 104, 112), (88, 136, 136), (56, 88, 96)],
}

# the built orleans_harbor palettes this art is drawn to (secondary palettes 6 and 8-12, snapshot 2026-10-12; 7 is the
# old trawler's and goes when the new trawlers land). check() tests every tile against them.
PALETTES = {
    6: [(112, 80, 80), (248, 232, 128), (88, 72, 80), (248, 248, 216), (232, 176, 112), (48, 56, 80), (96, 64, 64),
        (208, 184, 144), (32, 40, 64), (80, 96, 112), (128, 104, 104), (112, 120, 128), (160, 136, 112),
        (144, 104, 96), (128, 128, 136)],
    8: [(200, 64, 80), (232, 144, 112), (96, 96, 120), (248, 184, 128), (184, 200, 224), (64, 72, 104),
        (248, 248, 248), (152, 176, 216), (216, 104, 96), (216, 224, 232), (96, 168, 232), (128, 128, 136),
        (232, 232, 224), (32, 40, 64), (232, 136, 64)],
    9: [(104, 152, 120), (136, 176, 128), (96, 64, 64), (120, 168, 128), (64, 96, 64), (96, 136, 136), (40, 56, 40),
        (96, 128, 88), (72, 112, 104), (112, 80, 80), (144, 184, 152), (120, 160, 104), (80, 80, 80),
        (104, 144, 96), (152, 112, 104)],
    10: [(48, 56, 88), (128, 88, 104), (64, 48, 56), (64, 104, 112), (136, 72, 56), (168, 104, 80), (88, 136, 136),
         (104, 128, 88), (88, 48, 40), (104, 72, 80), (96, 72, 64), (40, 72, 80), (80, 104, 72), (32, 40, 64),
         (48, 64, 48)],
    11: [(128, 96, 80), (136, 168, 144), (72, 56, 56), (208, 184, 128), (144, 144, 152), (80, 112, 104),
         (40, 40, 56), (96, 72, 56), (232, 224, 200), (56, 80, 80), (136, 176, 176), (144, 112, 88), (168, 136, 104),
         (104, 136, 120), (192, 184, 168)],
    12: [(144, 112, 88), (160, 208, 216), (56, 72, 120), (80, 56, 56), (104, 152, 176), (232, 232, 224),
         (192, 72, 56), (72, 104, 160), (192, 192, 184), (128, 96, 80), (40, 40, 56), (144, 144, 152),
         (248, 232, 128), (104, 80, 64), (168, 136, 104)],
}


class Cell:
    """A transparent RGBA canvas w x h cells with pixel helpers."""

    def __init__(self, w, h):
        self.w, self.h = w * 16, h * 16
        self.im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.px[x, y] = c + (255,) if len(c) == 3 else c

    def get(self, x, y):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return None
        p = self.px[x, y]
        return p[:3] if p[3] else None

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.put(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def clear(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.px[x, y] = (0, 0, 0, 0)

    def paste(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                c = other.get(x, y)
                if c:
                    self.put(ox + x, oy + y, c)

    def sprite(self, x0, y0, rows, pal):
        """Hand-placed pixels: one string per row; '.' and ' ' leave the pixel alone, other chars via pal."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in ". ":
                    self.put(x0 + i, y0 + j, pal[ch])

    def mirror_x(self, y0=0, y1=None, xc=None):
        """Rows y0..y1: the right half becomes the mirror of the left half (about the piece's centre, a tile line, so
        the right half's tiles are flipped copies and cost nothing)."""
        y1 = self.h - 1 if y1 is None else y1
        W = self.w if xc is None else xc
        for y in range(y0, y1 + 1):
            for x in range(W // 2):
                self.px[W - 1 - x, y] = self.px[x, y]

    def flipped(self):
        out = Cell(self.w // 16, self.h // 16)
        out.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        out.px = out.im.load()
        return out

    def outline(self, c, region=None, skip=()):
        """A 1 px outline on clear pixels touching art (4-neighbours); `skip`: colours that don't get one."""
        x0, y0, x1, y1 = region or (0, 0, self.w - 1, self.h - 1)
        add = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.get(x, y) is not None:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = self.get(x + dx, y + dy)
                    if n is not None and n not in skip and n != c and x0 <= x + dx <= x1 and y0 <= y + dy <= y1:
                        add.append((x, y))
                        break
        for x, y in add:
            self.put(x, y, c)


# ---------------------------------------------------------------- boardwalk planks (opaque, unchanged)
def plank(orient, edges):
    """One plank cell. Boards are 4 px (3 board + 1 gap), so every 8x8 tile repeats along a run."""
    c = Cell(1, 1)
    n, s, w, e = ("n" in edges), ("s" in edges), ("w" in edges), ("e" in edges)
    for y in range(16):
        for x in range(16):
            if orient == "h":   # boards run north-south: vertical stripes
                k, i = x // 4, x % 4
                col = WG if i == 3 else (WH if i == 0 and k % 2 == 0 else W1 if k % 2 == 0 else W2)
                if i != 3 and (y in (7,) and k % 2 == 1 or y == 11 and k % 2 == 0 and x // 8 == 0):
                    col = WG    # a few butt joints
            else:               # boards run east-west: horizontal stripes
                k, i = y // 4, y % 4
                col = WG if i == 3 else (WH if i == 0 and k % 2 == 0 else W1 if k % 2 == 0 else W2)
                if i != 3 and (x == 5 and k % 2 == 1 or x == 12 and k % 2 == 0):
                    col = WG
            c.put(x, y, col)
    # nails where the boards cross the stringers under them
    if orient == "h":
        for x in range(1, 16, 4):
            for y in (3, 12):
                if c.get(x, y) != WG:
                    c.put(x, y, WG)
    else:
        for y in range(1, 16, 4):
            for x in (3, 12):
                c.put(x, y, WG)
    if n:
        c.hline(0, 15, 0, OUT)
        c.hline(0, 15, 1, WH)
    if s:   # the deck's edge timber, seen from the south
        c.hline(0, 15, 11, WG)
        c.hline(0, 15, 12, WF)
        c.hline(0, 15, 13, WF)
        c.hline(0, 15, 14, WD)
        c.hline(0, 15, 15, OUT)
        for x in range(2, 16, 8):
            c.put(x, 12, PL)   # bolt heads on the timber
    if w:
        c.vline(0, 0, 15, OUT)
        c.vline(1, 1 if n else 0, 10 if s else 15, WH)
        if s:
            c.vline(1, 11, 14, WF)
    if e:
        c.vline(15, 0, 15, OUT)
        c.vline(14, 1 if n else 0, 10 if s else 15, WG)
        if s:
            c.vline(14, 11, 14, WD)
    return c


# ---------------------------------------------------------------- pilings: the shared post, the skirts
def post(c, x, y0, y1, mud=False, water=True):
    """A 4 px timber pile (x..x+3, y0..y1), round and lit down its middle (the same both ways, so a mirrored post is
    the same tile), its foot in ripples (water) or a shadow (mud)."""
    c.vline(x, y0, y1, INK)
    c.vline(x + 1, y0, y1, W2)
    c.vline(x + 2, y0, y1, W2)
    c.vline(x + 3, y0, y1, INK)
    c.put(x + 1, y0, WK)
    c.put(x + 2, y0, WK)
    if mud:
        c.hline(x, x + 3, y1 + 1, WD)
    elif water:
        c.put(x - 1, y1 + 1, RIP)
        c.put(x + 4, y1 + 1, RIP)
        c.hline(x + 1, x + 2, y1 + 2, RIP)


def lip(c, y=0, x0=0, x1=15):
    """The shadow under a deck's south face: the timber's dark underside and its shadow on the water."""
    c.hline(x0, x1, y, INK)
    c.hline(x0, x1, y + 1, TIN_D)


def skirt(end=False, mud=False, left=True, plain=False):
    """The pilings under a deck's south face: the shadow lip, posts (one in each 8 px half that has one: the right
    post is the left one mirrored), ripples at the waterline. plain: the lip and a few ripples only."""
    c = Cell(1, 1)
    lip(c)
    if plain:
        for x, y in ((2, 5), (3, 5), (9, 9), (10, 9), (11, 9)):
            c.put(x, y, RIP)
        c.put(13, 4, RIP)
        return c
    posts = ([2] if left else []) + ([10] if end else [])
    for x in posts:
        post(c, x, 2, 9, mud=mud)
    return c


def pc_skirt():
    """4x1: the Pokemon Center standing on the water: the skirt's lip and a post pair in each cell (the skirt_e tiles),
    the door column (1) left empty for the boardwalk under the door."""
    c = Cell(4, 1)
    for i in (0, 2, 3):
        c.paste(skirt(end=True), i * 16, 0)
    return c


# ---------------------------------------------------------------- houses on pilings
def cabin_pixels():
    """The Shady Forest cabin (source metatiles 24B-24D, 253-255, 25B-25D, 263-265) as a 48x64 RGBA image, with
    the source's own grass cut away (the same pieces and grass colours the harbour recipe rebases)."""
    sys.path.insert(0, MAPGEN)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        from compose import TilesetSource, Recolor, rgb, flip
        spec = {"name": "shady", "primary": "general", "secondary": "tools/mapgen/sources/shady_forest", "layers": 3}
        rc = Recolor([])
        src = TilesetSource(spec, rc)
        ids = [["24B", "24C", "24D"], ["253", "254", "255"], ["25B", "25C", "25D"], ["263", "264", "265"]]
        c = Cell(3, 4)
        for j, row in enumerate(ids):
            for i, mid in enumerate(row):
                es, _ = src.metatile(int(mid, 16))
                for layer in range(len(es) // 4):
                    for q in range(4):
                        t, p, hf, vf = es[layer * 4 + q]
                        for k, col in enumerate(flip(rgb(t, p, rc), hf, vf)):
                            if col is not None:
                                c.put(i * 16 + (q % 2) * 8 + k % 8, j * 16 + (q // 2) * 8 + k // 8, col)
        # the source grass (teal) is the cabin's ground: cut it away (the near-grass greens of the Shady set)
        for y in range(c.h):
            for x in range(c.w):
                col = c.get(x, y)
                if col and col[1] > col[0] + 30 and col[1] > col[2] - 10 and col not in (NAVY, OUT):
                    c.px[x, y] = (0, 0, 0, 0)
        return c
    finally:
        os.chdir(cwd)


def shingle(x, k, dk, mid, lt):
    """The cabin's shingle courses on an 8 px repeat: a course line (mid, dark joints) and three rows of shingle
    face (light, mid joints); the joints step by two pixels from one course to the next."""
    ph = 1 if k < 4 else 3
    joint = x % 4 == ph
    if k % 4 == 0:
        return dk if joint else mid
    return mid if joint else lt


def roof(c, W, ramp):
    """A house roof W px wide, 48 px tall, in four distinct tile rows (back slope, ridge cap, the front slope repeated
    three times, the eave): the cabin's shingles and outline, every row on the 8 px repeat."""
    dk, mid, lt = ramp[0], ramp[1], ramp[2]
    for x in range(W):
        # back slope (y 1..8): dark courses, the far side in shade
        for y in range(1, 9):
            k = (y - 1) % 4
            c.put(x, y, dk if k in (0, 2) else (dk if x % 4 == (1 if (y - 1) % 8 < 4 else 3) else mid))
        c.put(x, 0, OUT)
        # the ridge line and the cap course (y 9..14), its shadow (y 15)
        c.put(x, 9, OUT if x % 4 != 3 else dk)
        c.put(x, 10, mid if x % 4 != 3 else OUT)
        for y in (11, 12, 13):
            c.put(x, y, dk if x % 4 == 3 else mid)
        c.put(x, 14, mid if x % 4 != 3 else dk)
        c.put(x, 15, NAVY)
        # the front slope (y 16..44), course lines every 4 px
        for y in range(16, 45):
            c.put(x, y, shingle(x, (y - 16) % 8, dk, mid, lt))
        # the eave: shadow line, eave board, outline
        c.put(x, 45, NAVY)
        c.put(x, 46, dk if x % 4 == 1 else mid)
        c.put(x, 47, NAVY)
    for x in (0, W - 1):
        c.vline(x, 0, 15, OUT)
        c.vline(x, 16, 47, NAVY)


def under_house(c, W, mud=False, steps_x=16):
    """Row 4 of a house (y 64..79): the floor beam on two braced posts per cell, the steps cell under the door.
    Every post cell is the same pixels (and its right half the left half mirrored), so they cost three tiles."""
    y0 = 64
    for cx in range(0, W, 16):
        if cx == steps_x:
            continue
        c.hline(cx, cx + 15, y0, WK)
        c.hline(cx, cx + 15, y0 + 1, WD)
        c.hline(cx, cx + 15, y0 + 2, INK)
        for px in (cx + 1, cx + 11):
            post(c, px, y0 + 3, y0 + 11, mud=mud)
        # cross-bracing between the pair (45 degrees, symmetric)
        for t in range(6):
            c.put(cx + 5 + t, y0 + 4 + t, WK)
            c.put(cx + 10 - t, y0 + 4 + t, WK)
    # the steps: stringers and treads going down to the boardwalk (the same tile top and bottom, and mirrored)
    sx = steps_x
    for y in range(y0, y0 + 16):
        k = (y - y0) % 4
        c.hline(sx + 2, sx + 13, y, WH if k == 0 else W1 if k in (1, 2) else WD)
        c.put(sx, y, INK)
        c.put(sx + 1, y, W2)
        c.put(sx + 14, y, W2)
        c.put(sx + 15, y, INK)


def house(roof_name, width, mud=False, cab=None):
    """A house on pilings: roof (rows 0-2) in the house's colour, the cabin's front wall (row 3, widened by a
    window bay where width = 4), the floor beam, posts and steps (row 4)."""
    cab = cab or cabin_pixels()
    c = Cell(width, 5)
    W = width * 16
    roof(c, W, ROOFS[roof_name])
    # the front wall: column 0 = cabin column 0, column 1 = the door column, the last = cabin column 2, a middle
    # window bay (the cabin's own) in a 4-wide house
    for y in range(48, 64):
        for x in range(W):
            if x < 16:
                sx = x
            elif x >= W - 16:
                sx = x - (W - 16) + 32
            elif x < 32:
                sx = x
            else:
                sx = 32 + (x % 16)
                if x % 16 >= 14:
                    sx = 2 + (x % 16) - 14 + 2
            c.put(x, y, cab.get(sx, y))
    if width == 4:
        for y in range(48, 64):
            for x in (46, 47):
                c.put(x, y, cab.get(x - 30, y))
    under_house(c, W, mud)
    return c


# ---------------------------------------------------------------- the Rain Pavilion (gym)
def heron_relief(c, x, y, facing=1, col=CREAM, shade=STONE):
    """A carved standing heron, 7x11, cream on the panel."""
    pts = [(0, 0), (1, 0), (2, 1), (3, 1), (2, 2), (2, 3), (1, 4), (1, 5), (2, 5), (2, 6), (3, 6), (3, 7), (4, 7),
           (2, 7), (1, 6), (4, 6), (5, 7), (3, 8), (2, 8), (4, 8), (3, 9), (3, 10), (4, 10), (2, 10)]
    beak = [(-1, 0), (-2, 0)]
    fx = (lambda d: x + d) if facing > 0 else (lambda d: x + 6 - d)
    for dx, dy in pts:
        c.put(fx(dx), y + dy, col)
    for dx, dy in beak:
        c.put(fx(dx), y + dy, shade)
    c.put(fx(1), y, INK)
    for dx, dy in ((3, 9), (4, 9), (5, 7)):
        c.put(fx(dx), y + dy, shade)


TIN_FRONT = [TIN_H, TIN, TIN_L, TIN_L, TIN_L, TIN_L, TIN, TIN_H]      # standing seams on the 8 px repeat (symmetric)
TIN_SHADE = [TIN_L, TIN_D, TIN, TIN, TIN, TIN, TIN_D, TIN_L]
TIN_BACK = [TIN, TIN_D, TIN_D, TIN_D, TIN_D, TIN_D, TIN_D, TIN]


def pavilion():
    """9x5, drawn on the left and mirrored about the door column's centre line. The hips run at 45 degrees through
    the tile corners (x + y = 39), so every hip tile is the same tile."""
    W, H = 9, 5
    c = Cell(W, H)
    K = 39
    # ---- roof
    for y in range(3, 40):
        xb = max(0, K - y)
        for x in range(xb, 72):
            p = x % 8
            if y == 3:
                col = INK
            elif y < 8:
                col = TIN_BACK[p]
            elif y == 8:
                col = INK
            elif y == 9:
                col = TIN_H
            elif y == 10:
                col = TIN_D if p in (0, 7) else TIN
            elif y < 32:
                col = TIN_FRONT[p]
            else:
                col = TIN_SHADE[p]
            c.put(x, y, col)
        c.put(xb, y, INK)
        if 9 <= y:
            c.put(xb + 1, y, TIN_H)
    # eave: fascia board, then the rafter tails in the shade under it
    for x in range(72):
        p = x % 8
        c.put(x, 40, INK)
        c.put(x, 41, W1)
        c.put(x, 42, W2)
        c.put(x, 43, WD)
        c.put(x, 44, INK)
        for y in range(45, 60):
            c.put(x, y, INK)
        c.put(x, 45, WK if p in (3, 4) else INK)
    c.vline(0, 40, 44, INK)
    # the back rail seen through the posts, the floor in the light toward the front
    for x in range(72):
        c.put(x, 51, WD)
        c.put(x, 52, WK)
        c.put(x, 53, WD)
        c.put(x, 59, WD)
        for y in range(60, 80):
            k = x % 4
            c.put(x, y, WD if k == 3 else WH if (k == 0 and y == 60) else W1 if k in (0, 1) else W2)
    # front posts straddling each cell line (16 k - 2 .. 16 k + 1), the corner post at 0..3; knee braces under the eave
    posts = [0, 14, 30, 46, 62]
    for px in posts:
        c.vline(px, 45, 79, INK)
        c.vline(px + 1, 45, 79, W1)
        c.vline(px + 2, 45, 79, W2)
        c.vline(px + 3, 45, 79, INK)
        for d in (1, 2):
            if px - d >= 0:
                c.put(px - d, 44 + d, W2)
            c.put(px + 3 + d, 44 + d, W2)
    # three carved verse panels between the posts (cells 1-3), the heron facing the doorway
    for k in (1, 2, 3):
        x0, x1 = 16 * k + 2, 16 * k + 13
        c.rect(x0, 58, x1, 79, INK)
        c.rect(x0 + 1, 59, x1 - 1, 79, W2)
        c.hline(x0 + 1, x1 - 1, 59, WH)
        c.vline(x0 + 1, 60, 79, W1)
        heron_relief(c, x0 + 3, 63, -1)
        c.hline(x0 + 1, x1 - 1, 76, WK)       # the plinth under the carving
        c.hline(x0 + 1, x1 - 1, 77, WD)
    # the corner bay: a low balustrade, a rain chain from the eave into a rain barrel
    for x in range(4, 14):
        c.put(x, 64, INK)
        c.put(x, 65, WH)
        c.put(x, 66, WK)
        if x % 4 == 1:
            c.vline(x, 67, 79, INK)
    for y in range(45, 70):
        c.put(8, y, GREY if y % 3 else STONE)
        c.put(9, y, STONE if y % 3 == 1 else GREY if y % 3 == 2 else INK)
    c.sprite(5, 69, ["..INNNNI..",
                     ".INWWWWNI.",
                     ".IKKKKKKI.",
                     ".IWWWWWWI.",
                     ".IKKKKKKI.",
                     ".IWWWWWWI.",
                     ".IKKKKKKI.",
                     ".IWWWWWWI.",
                     ".IKKKKKKI.",
                     "..IIIIII.."], {"I": INK, "N": TIN_D, "W": W1, "K": WK})
    # the doorway (cell 4): the lintel panel with the spread-wing heron over the opening (symmetric), the floor
    c.rect(66, 46, 71, 58, INK)
    c.rect(67, 47, 71, 57, W2)
    c.hline(67, 71, 47, WH)
    c.vline(67, 48, 57, W1)
    c.sprite(67, 48, ["....C",       # the spread-wing heron (its left half; the mirror completes it)
                      "C...C",
                      "CC..S",
                      ".CCCC",
                      "..CCC",
                      "...CC",
                      "....C",
                      "...S.",
                      "..S.."], {"C": CREAM, "S": STONE})
    for y in range(59, 80):
        for x in range(66, 72):
            k = x % 4
            c.put(x, y, WD if k == 3 else W1 if k in (0, 1) else W2)
    c.hline(66, 71, 59, WD)
    c.mirror_x(0, 79)
    # the heron weathervane on the ridge (the one asymmetric part): a heron in profile on an arrow
    c.sprite(66, 0, ["II......", ".I.IIII.", "..IIIII.", "...I.I.."], {"I": INK})
    c.vline(71, 3, 3, INK)
    c.vline(72, 3, 3, INK)
    return c, [4, 4]


# ---------------------------------------------------------------- the Lookout
def lookout():
    """3x7, drawn on the left and mirrored (the pennant, the door knob and the life ring are the only asymmetric
    parts). The X bracing runs at 45 degrees through the tile corners: every brace tile is one tile."""
    c = Cell(3, 7)
    # pyramid roof (tin), 2 px out per row
    for y in range(8, 23):
        d = y - 8
        x0 = max(1, 22 - 2 * d)
        for x in range(x0, 24):
            p = x % 8
            col = TIN_FRONT[p] if y < 19 else TIN_SHADE[p]
            if x < x0 + 2:
                col = TIN_H
            c.put(x, y, col)
        c.put(x0, y, INK)
        if x0 > 1:
            c.put(x0 - 1, y, INK)
    c.hline(22, 23, 7, INK)
    c.hline(1, 23, 23, INK)
    c.hline(1, 23, 24, DK)
    c.vline(1, 22, 24, INK)
    # the lookout cabin: white frame, glazed all round
    c.rect(4, 25, 23, 40, INK)
    c.rect(5, 25, 23, 39, WHITE)
    c.hline(5, 23, 25, WHITE_D)
    for x0 in (7, 16):
        c.rect(x0, 27, x0 + 6, 35, GLASS_D)
        c.hline(x0, x0 + 6, 27, GLASS)
        c.put(x0, 28, GLASS)
        c.put(x0 + 1, 28, GLASS)
        c.put(x0, 29, GLASS)
    for x in (6, 14, 15, 23):
        c.vline(x, 26, 36, WHITE_D)
    c.hline(5, 23, 37, WHITE_D)
    c.hline(5, 23, 38, GREY)
    # the catwalk round the cabin, its railing (2 px posts on the 8 px repeat)
    c.rect(0, 40, 23, 44, INK)                    # the floor: lit edge, fascia
    c.hline(1, 23, 41, WH)
    c.hline(1, 23, 42, W1)
    c.hline(1, 23, 43, W2)
    c.hline(0, 23, 34, INK)                       # the railing: top rail, dark posts against the white cabin
    c.hline(1, 23, 35, WH)
    c.hline(1, 23, 36, INK)
    c.vline(0, 34, 40, INK)
    for x in range(1, 24):
        if x % 8 in (3, 4):
            c.vline(x, 37, 39, INK if x % 8 == 3 else W2)
    for t in range(4):                            # knee braces from the legs up under the catwalk
        c.put(8 + t, 48 - t - 3, WK)
        c.put(8 + t, 48 - t - 2, INK)
    # the legs (posts at 4..7), the X bracing (45 degrees, x + y and x - y on the tile corners)
    for y in range(47, 96):
        c.put(4, y, INK)
        c.put(5, y, W1)
        c.put(6, y, W2)
        c.put(7, y, INK)
    for t in range(32):
        c.put(8 + t, 48 + t, WK)
        c.put(8 + t, 49 + t, INK) if 8 + t < 24 else None
    for t in range(16):
        c.put(23 - t, 64 + t, WK)
        c.put(23 - t, 65 + t, INK)
    # the girt below the bracing
    c.hline(8, 23, 80, INK)
    c.hline(8, 23, 81, W1)
    c.hline(8, 23, 82, WK)
    c.hline(8, 23, 83, INK)
    # the base room: tin roof (y 88..95), board-and-batten walls (y 96..111), a window
    c.hline(0, 23, 88, INK)
    for x in range(1, 24):
        c.put(x, 89, TIN_H)
        for y in range(90, 94):
            c.put(x, y, TIN_FRONT[x % 8])
        c.put(x, 94, TIN_D)
        c.put(x, 95, INK)
    c.vline(0, 88, 95, INK)
    for y in range(96, 112):
        for x in range(1, 24):
            p = x % 8
            c.put(x, y, WF if p in (0, 7) else WH if p == 1 else W1 if p in (2, 3, 4, 5) else W2)
    c.vline(0, 96, 111, INK)
    c.hline(0, 23, 111, INK)
    c.hline(1, 23, 96, DK)
    c.rect(6, 99, 13, 105, INK)
    c.rect(7, 100, 12, 104, GLASS_D)
    c.hline(7, 12, 100, GLASS)
    c.put(7, 101, GLASS)
    c.hline(6, 13, 106, WH)
    # the door (cell 1, row 6): x 18..29, symmetric
    c.rect(18, 98, 23, 111, INK)
    c.rect(19, 99, 23, 111, DK)
    c.rect(20, 100, 23, 104, W2)
    c.rect(20, 106, 23, 110, W2)
    c.mirror_x(0, 111)
    # pennant on its pole above the roof (asymmetric)
    c.vline(23, 0, 7, INK)
    c.vline(24, 0, 7, GREY)
    c.sprite(25, 0, ["IIIIII.", "RRRRWWI", "RRRWWI.", "IIII..."], {"I": INK, "R": RED, "W": WHITE})
    c.put(26, 106, YELLOW)                 # the door knob
    # the life ring by the door
    c.sprite(30, 106, [".RW.", "W..R", "R..W", ".WR."], {"R": RED, "W": WHITE})
    return c, [1, 6]


# ---------------------------------------------------------------- the Tide Gauge & Weather Station
def station():
    c = Cell(5, 4)
    # ---- the instrument mast on the roof (cell 0-1 column 1): anemometer cups and a wind vane
    c.vline(11, 1, 15, INK)
    c.vline(12, 1, 15, GREY)
    c.hline(9, 14, 2, INK)
    c.sprite(8, 1, ["WW", "IW"], {"W": WHITE, "I": INK})
    c.sprite(14, 1, ["WW", "WI"], {"W": WHITE, "I": INK})
    c.hline(8, 15, 8, INK)
    c.sprite(13, 6, ["RR.", "RRR", "RR."], {"R": RED})
    c.put(8, 7, INK)
    c.put(8, 9, INK)
    # ---- the hut's roof: a tin band (y 16..31)
    for x in range(48):
        p = x % 8
        c.put(x, 16, INK)
        c.put(x, 17, TIN_H)
        for y in range(18, 26):
            c.put(x, y, TIN_FRONT[p])
        for y in range(26, 29):
            c.put(x, y, TIN_SHADE[p])
        c.put(x, 29, TIN_D)
        c.put(x, 30, INK)
        c.put(x, 31, GREY)
    for x in (0, 47):
        c.vline(x, 16, 31, INK)
    # ---- white clapboard walls (y 32..63)
    for y in range(32, 63):
        for x in range(1, 47):
            c.put(x, y, WHITE if (y - 32) % 4 != 3 else WHITE_D)
    c.vline(0, 31, 63, INK)
    c.vline(47, 31, 63, INK)
    c.hline(0, 47, 63, INK)
    # the windows (cells 0 and 2, mirror images), the door (cell 1, row 3): blue, a porthole, symmetric but the knob
    for x0 in (3, 34):
        c.rect(x0, 35, x0 + 10, 44, INK)
        c.rect(x0 + 1, 36, x0 + 9, 43, GLASS_D)
        c.hline(x0 + 1, x0 + 9, 36, GLASS)
        c.vline(x0 + 5, 37, 43, INK)
        c.hline(x0, x0 + 10, 45, WHITE_D)
    for x in (4, 35):
        c.put(x, 37, GLASS)
    c.rect(19, 42, 28, 63, INK)
    c.rect(20, 43, 27, 62, BLUE)
    c.hline(20, 27, 43, BLUE_D)
    c.rect(22, 46, 25, 49, INK)
    c.rect(23, 47, 24, 48, GLASS)
    c.hline(21, 26, 53, BLUE_D)
    c.put(26, 56, YELLOW)
    # the Stevenson screen beside the door: a louvred white box on legs (cell 2, row 3)
    c.rect(33, 48, 43, 57, INK)
    c.rect(34, 49, 42, 56, WHITE)
    for y in (51, 53, 55):
        c.hline(34, 42, y, WHITE_D)
    c.hline(34, 42, 49, WHITE)
    c.vline(35, 58, 62, INK)
    c.vline(41, 58, 62, INK)
    # ---- the tide staff (cell 3, x 56..63): red-and-white bands on the 8 px repeat, the pile at its foot
    c.rect(56, 3, 63, 55, INK)
    for y in range(4, 55):
        band = (y // 4) % 2
        c.hline(57, 62, y, RED if band else WHITE)
        if y % 4 == 0:
            c.hline(57, 59, y, INK)
    c.hline(57, 62, 4, WHITE_D)
    post(c, 58, 56, 59)
    c.vline(56, 55, 55, INK)
    # ---- the stilling well (cell 4, x 72..79): the recorder box on its pipe
    c.rect(72, 18, 79, 26, INK)
    c.rect(73, 19, 78, 25, WHITE_D)
    c.hline(73, 78, 19, WHITE)
    c.put(74, 21, RED)
    c.hline(74, 77, 23, GREY)
    for y in range(27, 59):
        c.put(74, y, INK)
        c.put(75, y, GREY)
        c.put(76, y, GREY)
        c.put(77, y, INK)
    c.put(73, 59, RIP)
    c.put(78, 59, RIP)
    c.hline(75, 76, 60, RIP)
    return c, [1, 3]


# ---------------------------------------------------------------- Marine Supply (the Mart)
FONT = {  # 3x5 capitals
    "M": ["101", "111", "111", "101", "101"], "A": ["010", "101", "111", "101", "101"],
    "R": ["110", "101", "110", "101", "101"], "I": ["111", "010", "010", "010", "111"],
    "N": ["1001", "1101", "1011", "1001", "1001"], "E": ["111", "100", "110", "100", "111"],
    "S": ["011", "100", "010", "001", "110"], "U": ["101", "101", "101", "101", "111"],
    "P": ["110", "101", "110", "100", "100"], "L": ["100", "100", "100", "100", "111"],
    "Y": ["101", "101", "010", "010", "010"], " ": ["000", "000", "000", "000", "000"],
}


def text(c, s, x, y, col, gap=1):
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == "1":
                    c.put(x + i, y + j, col)
        x += len(FONT[ch][0]) + gap


BLUE_TIN = [GLASS_D, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, GLASS_D]
BLUE_SHADE = [BLUE, BLUE_D, BLUE_D, BLUE_D, BLUE_D, BLUE_D, BLUE_D, BLUE]
BATTEN = [DK, W2, W1, W1, W1, W1, W2, DK]


def shop():
    """5x4, drawn on the left and mirrored about the door's centre line; the sign's letters and the rope
    coil go on afterwards."""
    c = Cell(5, 4)
    # ---- the blue tin roof: a band with its gable ends raked out at 45 degrees (y 4..23)
    for y in range(4, 24):
        xb = max(0, 23 - y)
        for x in range(xb, 40):
            p = x % 8
            if y == 4:
                col = INK
            elif y == 5:
                col = GLASS
            elif y < 18:
                col = BLUE_TIN[p]
            else:
                col = BLUE_SHADE[p]
            c.put(x, y, col)
        c.put(xb, y, INK)
        if y > 5:
            c.put(xb + 1, y, GLASS)
    c.hline(0, 39, 22, BLUE_D)
    c.hline(0, 39, 23, INK)
    # ---- walls: board-and-batten (y 24..63)
    for y in range(24, 63):
        for x in range(1, 40):
            c.put(x, y, BATTEN[x % 8])
    c.hline(1, 39, 24, DK)
    c.vline(0, 24, 63, INK)
    c.hline(0, 39, 63, INK)
    # ---- the signboard (y 29..39): its letters sit in one tile row (y 32..39)
    c.rect(8, 29, 39, 39, INK)
    c.hline(9, 39, 30, WH)
    c.rect(9, 31, 39, 38, WF)
    c.hline(9, 39, 38, DK)
    # ---- display window (cells 0-1): glass, a net draped inside
    c.rect(3, 42, 23, 56, INK)
    c.rect(4, 43, 22, 55, GLASS_D)
    c.hline(4, 22, 43, GLASS)
    c.put(4, 44, GLASS)
    for y in range(49, 56):                     # a net hung in the window: a diamond mesh, a float line along its top
        for x in range(4, 23):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                c.put(x, y, DK)
    for x in range(5, 22, 4):
        c.put(x, 48, RED)
    c.hline(3, 23, 57, WH)
    c.hline(3, 23, 58, DK)
    # ---- a buoy hanging beside the door (symmetric pair)
    c.sprite(27, 45, ["..I..", ".IRI.", "IRRRI", "IWWWI", "IRRRI", ".III."], {"I": INK, "R": RED, "W": WHITE})
    # ---- the door (cell 2): glazed, an anchor on the glass
    c.rect(34, 47, 39, 63, INK)
    c.rect(35, 48, 39, 62, WF)
    c.rect(36, 49, 39, 56, GLASS_D)
    c.hline(36, 39, 49, GLASS)
    c.vline(39, 50, 55, INK)
    c.hline(37, 39, 51, INK)
    c.put(37, 54, INK)
    c.put(38, 55, INK)
    c.rect(36, 58, 39, 61, W2)
    c.hline(36, 39, 58, WH)
    # ---- the life ring over the door: red sides, white top and bottom (the same flipped)
    c.sprite(36, 40, ["..II", ".IWW", "IRI.", "IRI.", "IRI.", ".IWW", "..II"], {"I": INK, "R": RED, "W": WHITE})
    c.mirror_x(0, 63)
    # the lettering (one 8 px tile row) and a rope coil by the door
    text(c, "MARINE SUPPLY", 14, 33, WHITE)  # 52 px: x 14..65
    c.sprite(12, 57, [".IIIIII.", "IWHHHHWI", "IHIIIIHI", "IHI..IHI", "IWHHHHWI", ".IIIIII."],
             {"I": INK, "W": W1, "H": WH})
    return c, [2, 3]


# ---------------------------------------------------------------- the shrimp trawlers
HOUSE_X = (56, 71)      # the pilothouse (bow-east coordinates): tile columns 7-8, over the plain midships deck
MAST_X = 39             # the mast (39 ink, 40 grey): the booms are mirror images about x = 39.5, a tile line


def trawler_hull():
    """The trawler, bow east (96x48), without its mooring line or the pilothouse trim. The hull is drawn column by
    column from a profile (north rail, deck, south rail, rub rail, side, boot stripe, waterline): the midships columns
    are the same pixels on an 8 px repeat, the sheer rises and the deck narrows to the stem head over the last 19 px.
    The whole boat is HULL-family (palette 12) except the shadow and ripples on the water (their own tile row)."""
    c = Cell(6, 3)
    X0, XM, XS = 4, 72, 91         # the stern, where the bow begins, the stem head
    cols = {}
    for x in range(X0, XS + 1):
        u = max(0.0, (x - XM) / (XS - XM))
        top = round(18 - 3 * u ** 1.5)             # the north rail: the sheer lifts it a little toward the stem
        rail = round(29 - 14 * u ** 1.8)           # the south rail sweeps up to meet it at the stem head
        if x < X0 + 2:   # the stern quarters, rounded
            top, rail = (20, 27) if x == X0 else (19, 28)
        bot = 39 if x <= 80 else 39 - round((x - 80) * 24 / (XS - 80))
        if x == X0:
            bot = 37
        elif x == X0 + 1:
            bot = 38
        cols[x] = (top, rail, max(bot, rail))
    for x, (top, rail, bot) in cols.items():
        c.put(x, top, INK)
        if rail - top >= 5:
            c.put(x, top + 1, WHITE)               # the north bulwark's cap
            c.put(x, top + 2, WHITE_D)             # and its inner face
            for y in range(top + 3, rail - 1):     # deck planks fore and aft (seams only: the deck is the same flipped)
                k = (y - top - 3) % 3
                c.put(x, y, W2 if k == 2 else W1)
            c.put(x, rail - 1, INK)
        else:
            for y in range(top + 1, rail):
                c.put(x, y, WHITE if y < rail - 1 or rail - top < 3 else WHITE_D)
        c.put(x, rail, WHITE)                      # the south bulwark's cap
        if bot > rail:
            c.put(x, rail + 1, WF)                 # the rub rail: the sheer line
        for y in range(rail + 2, bot):
            c.put(x, y, WHITE)
        if bot - rail >= 7:
            c.put(x, bot - 4, WHITE_D)
            c.put(x, bot - 3, RED)
            c.put(x, bot - 2, RED)
            c.put(x, bot - 1, DK)
        elif bot - rail >= 4:
            c.put(x, bot - 2, RED)
            c.put(x, bot - 1, DK)
        if bot > rail:
            c.put(x, bot, INK)
    c.outline(INK, region=(0, 0, 95, 39))
    hx = 85
    c.put(hx, cols[hx][1] + 3, INK)                # the hawse pipe
    # the shadow on the water under the hull and the ripples (their own tile row, y 40..47: WATER tiles)
    for x in range(X0 + 1, 83):
        c.put(x, 40, TIN_D)
        if 1 <= x % 8 <= 6 and x < 80:
            c.put(x, 41, TIN_D)
        if x % 8 == 3 and x < 80:
            c.hline(x, x + 1, 43, RIP)
    c.hline(84, 85, 41, RIP)
    # ---- the mast, the outrigger booms raised in a tall V (2 up for 1 out, mirror images about the mast's centre
    # line), the nets bunched up and hanging along their upper halves with a float line, the trawl doors at the tips
    m = MAST_X
    r = Cell(6, 3)                                # the rigging, drawn west of the mast's centre line and mirrored
    r.vline(m - 1, 0, 26, INK)
    r.vline(m, 1, 26, GREY)
    r.put(m, 0, INK)
    for y in range(1, 26):                        # the aft boom, 2 up for 1 out
        x = m - 2 - (25 - y) // 2
        r.put(x, y, GREY)
        if y > 11:
            r.put(x + 1, y, INK)
        if y <= 15:                               # the net bundled under it, a float line along its foot
            w = 2 if y < 4 else 3
            for k in range(1, w + 1):
                r.put(x - k, y + 1, WF if (k + y) % 2 else W2)
            if y % 3 == 1 and y > 3:
                r.put(x - w - 1, y + 1, WHITE)
    r.outline(INK, region=(0, 0, m, 17))
    dx = m - 17                                   # the trawl door hanging at the tip
    r.rect(dx, 2, dx + 5, 9, INK)
    r.rect(dx + 1, 3, dx + 4, 8, WF)
    r.vline(dx + 1, 3, 8, W1)
    r.vline(dx + 4, 3, 8, W1)
    r.hline(dx + 1, dx + 4, 5, DK)
    r.hline(dx + 1, dx + 4, 8, GREY)
    for y in range(27):
        for x in range(m + 1):
            r.px[2 * m + 1 - x, y] = r.px[x, y]
    r.put(m, 0, YELLOW)                           # the masthead light
    r.put(m + 1, 0, YELLOW)
    c.paste(r, 0, 0)
    # ---- the pilothouse forward (tile columns 7-8): roof seen from above, the south wall, three windows, one lit
    hx0, hx1 = HOUSE_X
    c.rect(hx0, 9, hx1, 27, INK)
    c.rect(hx0 + 1, 10, hx1 - 1, 13, WHITE_D)
    c.hline(hx0 + 1, hx1 - 1, 10, WHITE)
    c.hline(hx0, hx1, 14, INK)
    c.rect(hx0 + 1, 15, hx1 - 1, 26, WHITE)
    c.hline(hx0 + 1, hx1 - 1, 26, WHITE_D)
    for wx, lit in ((hx0 + 2, False), (hx0 + 6, True), (hx0 + 10, False)):
        c.rect(wx, 16, wx + 4, 22, INK)
        if lit:
            c.rect(wx + 1, 17, wx + 3, 21, YELLOW)
            c.put(wx + 1, 17, WHITE)
        else:
            c.rect(wx + 1, 17, wx + 3, 21, GLASS_D)
            c.hline(wx + 1, wx + 3, 17, GLASS)
            c.put(wx + 1, 18, GLASS)
    c.vline(hx0 + 11, 5, 9, INK)                  # the radar on its post (over the house's east tile)
    c.hline(hx0 + 8, hx0 + 14, 5, INK)
    c.hline(hx0 + 9, hx0 + 13, 6, GREY)
    # ---- deck gear: a shrimp basket at the stern, the hatch (symmetric across a tile line), the winch drum
    c.sprite(9, 17, ["IIIIII",
                     "IHHHHI",
                     "IWKKWI",
                     "IWWWWI",
                     "IIIIII"], {"I": INK, "H": WH, "W": W1, "K": DK})
    c.sprite(18, 17, ["IIIIIIIIIIII",
                      "IHHHHHHHHHHI",
                      "IHWWWWWWWWHI",
                      "IHWKWWWWKWHI",
                      "IHWWWWWWWWHI",
                      "IIIIIIIIIIII"], {"I": INK, "H": WH, "W": W2, "K": DK})
    c.sprite(m - 5, 20, ["IIIIIIIIIIII", "IGWWWWWWWWGI", "IGGGGGGGGGGI", "IGWWWWWWWWGI", "IIIIIIIIIIII"],
             {"I": INK, "G": GREY, "W": WHITE_D})
    return c


def trawler(kind):
    """trawler_a: bow east, red trim on the pilothouse. trawler_b: the same boat mirrored (bow west, so every hull,
    deck, rigging and gear tile is A's flipped), blue trim, its line from the stern quarter. Each line reaches the piece's
    east edge at y 34 (row 2), the height of a piling's rope collar in the next cell east."""
    c = trawler_hull()
    if kind == "b":
        c = c.flipped()
    trim = RED if kind == "a" else BLUE
    hx0, hx1 = HOUSE_X if kind == "a" else (95 - HOUSE_X[1], 95 - HOUSE_X[0])
    c.hline(hx0 + 1, hx1 - 1, 13, trim)
    c.hline(hx0 + 1, hx1 - 1, 15, trim)
    if kind == "a":     # the bow line: from the stem head's cleat, slack, down to the edge
        pts = [(89, 16), (90, 18), (91, 20), (92, 22), (92, 23), (92, 24), (93, 25), (93, 26), (93, 27), (94, 28),
               (94, 29), (94, 30), (95, 31), (95, 32), (95, 33), (95, 34)]
    else:               # the stern line: from the quarter chock, short, to the edge
        pts = [(92, 30), (93, 31), (93, 32), (94, 33), (95, 34)]
    for x, y in pts:
        c.put(x, y, WH)
        if c.get(x - 1, y) is None:
            c.put(x - 1, y, INK)
    return c


# ---------------------------------------------------------------- small pieces
def heron_pile():
    """An egret on an old piling: the top cell is the bird, the bottom cell is `pile` (the same tiles)."""
    c = Cell(1, 2)
    c.paste(pile(), 0, 16)
    body = [(6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10),
            (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (12, 12), (11, 12)]
    neck = [(6, 8), (5, 7), (5, 6), (6, 5), (6, 4), (5, 3), (5, 2), (6, 2)]
    for x, y in body + neck:
        c.put(x, y, WHITE)
    for x, y in [(10, 10), (11, 11), (9, 11), (12, 12)]:
        c.put(x, y, WHITE_D)
    c.hline(2, 4, 3, YELLOW)
    c.vline(8, 12, 15, INK)
    c.vline(9, 12, 15, INK)
    for x, y in body + neck:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if c.get(x + dx, y + dy) is None:
                c.put(x + dx, y + dy, INK)
    c.put(4, 2, INK)
    return c


def pile():
    """A mooring piling with a rope collar, cap at the top of the cell, symmetric (its right half is the left
    mirrored)."""
    c = Cell(1, 1)
    c.rect(5, 0, 10, 11, INK)
    c.rect(6, 1, 9, 10, W1)
    c.vline(6, 1, 10, W2)
    c.vline(9, 1, 10, W2)
    c.hline(6, 9, 1, WH)
    c.hline(5, 10, 4, ROPE)
    c.hline(5, 10, 5, WK)
    c.put(4, 12, RIP)
    c.put(11, 12, RIP)
    c.hline(6, 9, 13, RIP)
    return c


def sign():
    c = Cell(1, 1)
    c.rect(1, 2, 14, 10, INK)
    c.rect(2, 3, 13, 9, W1)
    c.hline(2, 13, 3, WH)
    c.hline(4, 11, 5, WK)
    c.hline(5, 10, 7, WK)
    c.vline(7, 11, 14, INK)
    c.vline(8, 11, 14, INK)
    c.hline(6, 9, 15, WD)
    return c


def lantern():
    c = Cell(1, 1)
    c.sprite(5, 0, ["..II..", ".IGGI.", "IYYYYI", "IYWYYI", "IYYYYI", ".IIII.", "..IG..", "..IG..", "..IG..",
                    "..IG..", "..IG..", "..IG..", ".IIII.", "IGGGGI", ".IIII."], {"I": INK, "G": GREY, "Y": YELLOW,
                                                                                    "W": WHITE})
    return c


def bollard():
    c = Cell(1, 1)
    c.sprite(3, 3, ["..IIIIII..", ".IGHHHHGI.", ".IGGGGGGI.", "IRRRRRRRRI", "IRKRRRKRRI", ".IGGGGGGI.",
                    ".IGGGGGGI.", "..IIIIII.."], {"I": INK, "G": GREY, "H": STONE, "R": ROPE, "K": WK})
    c.sprite(12, 7, ["RR.", ".RR", "..R", "..R"], {"R": ROPE})
    return c


# ---------------------------------------------------------------- the sheets
HOUSES = [("plum", 3, False), ("plum", 3, True), ("slate", 4, False), ("rust", 3, False), ("moss", 3, False),
          ("teal", 4, False)]
PLACED_HOUSES = ["house_plum3_mud", "house_slate4", "house_rust3", "house_moss3", "house_teal4"]


def pieces():
    """name -> (Cell, sheet, info). Planks are opaque (sheet "planks"), the rest are overlays ("art")."""
    out = {}
    for o in "hv":
        for mask in range(16):
            edges = "".join(e for k, e in enumerate("nswe") if mask >> k & 1)
            out[f"{o}{edges}"] = (plank(o, edges), "planks", {"walk": True})
    out["skirt"] = (skirt(), "art", {})
    out["skirt_e"] = (skirt(end=True), "art", {})
    out["skirt_plain"] = (skirt(plain=True), "art", {"comment": "The deck's shadow lip and ripples, no post."})
    out["mskirt"] = (skirt(mud=True), "art", {})
    out["mskirt_e"] = (skirt(end=True, mud=True), "art", {})
    out["pc_skirt"] = (pc_skirt(), "art", {"comment": "Pilings under the Pokemon Center's south wall, 4x1 (column 1 "
                                                      "empty: the boardwalk under the door)."})
    cab = cabin_pixels()
    for roof_name, width, mud in HOUSES:
        out[f"house_{roof_name}{width}" + ("_mud" if mud else "")] = (
            house(roof_name, width, mud, cab), "art",
            {"doors": [[1, 3]], "passable": [[1, 4]], "walk": [[1, 4]],
             "comment": f"House on pilings: Shady cabin, {roof_name} roof, {width} wide, on posts, steps from the door."})
    pv, door = pavilion()
    out["pavilion"] = (pv, "art", {"doors": [door], "comment": "The Rain Pavilion (gym), 9x5, door (4,4)."})
    lk, door = lookout()
    out["lookout"] = (lk, "art", {"doors": [door], "comment": "The Lookout tower, 3x7, door (1,6)."})
    st, door = station()
    out["station"] = (st, "art", {"doors": [door], "comment": "Tide Gauge & Weather Station, 5x4, door (1,3)."})
    sh, door = shop()
    out["shop"] = (sh, "art", {"doors": [door], "comment": "Marine Supply (the Mart), 5x4, door (2,3)."})
    out["trawler_a"] = (trawler("a"), "art", {"comment": "Gulf shrimp trawler, bow east, red trim, 6x3 (blocking)."})
    out["trawler_b"] = (trawler("b"), "art", {"comment": "Gulf shrimp trawler, bow west, blue trim, 6x3 (blocking)."})
    out["heron_pile"] = (heron_pile(), "art", {"comment": "An egret on an old piling in the water, 1x2."})
    out["pile"] = (pile(), "art", {"comment": "A mooring piling, 1x1."})
    out["sign"] = (sign(), "art", {"comment": "A wooden sign, 1x1."})
    out["lantern"] = (lantern(), "art", {"comment": "A lantern post on the boardwalk, 1x1."})
    out["bollard"] = (bollard(), "art", {"comment": "A bollard with a rope, on the boardwalk, 1x1."})
    return out


def pack(items, width_cells):
    """Shelf-pack pieces into a sheet width_cells wide: name -> (x, y) in cells."""
    pos, x, y, row_h = {}, 0, 0, 0
    for name, (c, _, _) in items:
        w, h = c.w // 16, c.h // 16
        if x + w > width_cells:
            x, y, row_h = 0, y + row_h, 0
        pos[name] = (x, y)
        x += w
        row_h = max(row_h, h)
    return pos, y + row_h


# ---------------------------------------------------------------- the tile census and the checks
# piece groups and their budgets (marginal 8x8 tiles; art_requests/lands_end.md)
GROUPS = [
    ("houses (the five placed)", PLACED_HOUSES, 85),
    ("pavilion", ["pavilion"], 50),
    ("lookout", ["lookout"], 40),
    ("station", ["station"], 32),
    ("shop", ["shop"], 36),
    ("trawlers", ["trawler_a", "trawler_b"], 40),
    ("small pieces", ["skirt", "skirt_e", "skirt_plain", "mskirt", "mskirt_e", "heron_pile", "pile", "sign"], 15),
    ("optional: pc_skirt", ["pc_skirt"], None),
    ("optional: deck dressing", ["lantern", "bollard"], None),
]
# the tileset as built before this art: 489 tiles, of which the first drawing's placed pieces were 333 and the old
# trawler stand-in 30 (the rest, 126, is the terrain, planks, Pokemon Center and reeds)
BUILT, OLD_ART, OLD_TRAWLER = 489, 333, 30


def rgb_array(c):
    a = np.zeros((c.h, c.w, 3), np.uint8)
    a[...] = KEY
    for y in range(c.h):
        for x in range(c.w):
            v = c.get(x, y)
            if v:
                a[y, x] = v
    return a


def canon(t):
    return min(v.tobytes() for v in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))


def tiles_of(c):
    a = rgb_array(c)
    out = []
    for ty in range(0, a.shape[0], 8):
        for tx in range(0, a.shape[1], 8):
            t = a[ty:ty + 8, tx:tx + 8]
            if ((t[..., 0] == 255) & (t[..., 1] == 0) & (t[..., 2] == 255)).all():
                continue
            out.append((canon(t), t))
    return out


def census(ps):
    """Unique 8x8 tiles (flips free, clear tiles free) group by group in GROUPS order: a group's own count and its
    marginal count (tiles no earlier group already has)."""
    seen = set()
    rows = []
    for title, names, target in GROUPS:
        own = set()
        for n in names:
            own |= {k for k, _ in tiles_of(ps[n][0])}
        new = own - seen
        seen |= own
        rows.append((title, names, target, len(own), len(new)))
    return rows, len(seen)


def check(ps):
    """Every overlay tile must be an exact subset of one of the tileset's palettes; doors must not be empty cells."""
    pals = [set(p) for p in PALETTES.values()]
    problems = []
    for n, (c, sheet, info) in ps.items():
        if sheet != "art":
            continue
        if n.startswith("house_"):
            # the roofs and the front wall are the cabin's own colours as the first drawing had them (already packed,
            # some with the packer's shifts): only the beam/post/steps row is new
            low = Cell(c.w // 16, c.h // 16)
            low.paste(c, 0, 0)
            low.clear(0, 0, c.w - 1, 63)
            c = low
        bad = 0
        for k, t in tiles_of(c):
            cols = {tuple(int(v) for v in p) for p in t.reshape(-1, 3)} - {KEY}
            if not any(cols <= p for p in pals):
                bad += 1
                if bad == 1:
                    problems.append(f"{n}: tile fits no palette: {sorted(cols)}")
        if bad > 1:
            problems.append(f"{n}: {bad} tiles fit no palette")
    return problems


# ---------------------------------------------------------------- review sheet
def ground_cells():
    """Ekat water, a mud cell and the plank cells from the built tileset (render.py), or flat stand-ins."""
    try:
        sys.path.insert(0, MAPGEN)
        from render import Tilesets
        m = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_harbor.mapping.json")))["metatiles"]
        ts = Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_general"),
                      os.path.join(ROOT, "data/tilesets/secondary/orleans_harbor"))
        g = {"~": ts.metatile(m["ekat:water_C"]).copy(), "L": ts.metatile(m["ekat:mud_C"]).copy()}
        for k, v in m.items():
            if k.startswith("lep:"):
                g[k[4:]] = ts.metatile(v).copy()
        return g, "Ekat water and planks from the built orleans_harbor tileset"
    except Exception as e:  # noqa: BLE001 (the review must not stop the art)
        print("  review: flat stand-ins for the ground:", e)
        return {"~": Image.new("RGB", (16, 16), WATER), "L": Image.new("RGB", (16, 16), (144, 104, 96))}, "flat stand-ins"


def on_ground(c, cell, pad=0):
    w, h = c.w + 2 * pad, c.h + 2 * pad
    bg = Image.new("RGB", (w, h))
    for y in range(0, h, 16):
        for x in range(0, w, 16):
            bg.paste(cell, (x, y))
    bg.paste(c.im, (pad, pad), c.im)
    return bg


def plank_name(cells, x, y, o):
    edges = ""
    for e, (dx, dy) in zip("nswe", ((0, -1), (0, 1), (-1, 0), (1, 0))):
        if (x + dx, y + dy) not in cells:
            edges += e
    return o + edges


def town_patch(ps, g):
    """A stretch of the town drawn the way lands_end.py builds it: a main walk (2 wide) with a west branch running
    south, two houses on the walk's north side, the shop on a stub, the trawlers moored along the branch, skirts and
    pilings under every south face (skirt_e / skirt / skirt_plain on the x % 3 rhythm), a lantern and a bollard."""
    PW, PH = 26, 17
    cells = {}
    for x in range(0, 26):
        for y in (6, 7):
            cells[(x, y)] = "h"
    for y in range(8, 17):
        for x in (12, 13):
            cells[(x, y)] = "v"
    for x in range(14, 21):
        cells[(x, 14)] = "h"
    img = Image.new("RGB", (PW * 16, PH * 16))
    for y in range(PH):
        for x in range(PW):
            img.paste(g["~"], (x * 16, y * 16))
    for (x, y), o in cells.items():
        n = plank_name(cells, x, y, o)
        img.paste(g.get(n) or ps[n][0].im.convert("RGB"), (x * 16, y * 16))
    objs = []
    for (x, y), o in sorted(cells.items()):
        if (x, y + 1) in cells or y + 1 >= PH:
            continue
        pat = x % 3
        objs.append(("skirt_e" if pat == 0 else "skirt" if pat == 1 else "skirt_plain", x, y + 1))
    objs += [("house_rust3", 2, 1), ("house_teal4", 17, 1), ("shop", 15, 10), ("trawler_a", 5, 9),
             ("trawler_b", 4, 13), ("pile", 11, 9), ("pile", 11, 11), ("pile", 11, 13), ("pile", 10, 15),
             ("heron_pile", 23, 10), ("lantern", 9, 6), ("bollard", 13, 9), ("sign", 7, 7)]
    occupied = set()
    for n, x, y in objs:
        c = ps[n][0]
        if n.startswith("house") or n == "shop":
            for j in range(c.h // 16):
                for i in range(c.w // 16):
                    occupied.add((x + i, y + j))
    for n, x, y in objs:
        if "skirt" in n and (x, y) in occupied:
            continue
        c = ps[n][0]
        img.paste(c.im, (x * 16, y * 16), c.im)
    return img


def review(ps, index, rows, total, problems, path):
    S = 3
    g, src = ground_cells()
    BG, FG, HI, OK, BAD = (36, 40, 44), (225, 225, 210), (255, 240, 160), (150, 220, 150), (255, 120, 120)
    groups = [
        ("Houses on pilings (the five placed, then house_plum3 unplaced)", PLACED_HOUSES + ["house_plum3"], "~"),
        ("The Rain Pavilion (gym), the Lookout", ["pavilion", "lookout"], "~"),
        ("Tide gauge and weather station, Marine Supply (leaves HOLD)", ["station", "shop"], "~"),
        ("Shrimp trawlers (A bow east, B mirrored)", ["trawler_a", "trawler_b"], "~"),
        ("Skirts, piles, egret, sign (over water / mud)",
         ["skirt", "skirt_e", "skirt_plain", "mskirt", "mskirt_e", "pc_skirt", "pile", "heron_pile", "sign"], "~"),
        ("Deck dressing (over the planks)", ["lantern", "bollard"], "h"),
    ]
    own = {}
    for n, (c, sheet, info) in ps.items():
        if sheet == "art":
            own[n] = len({k for k, _ in tiles_of(c)})
    Wd = 2100
    lay, y = [], 10
    lay.append(("t", "Land's End own art (make_lands_end_art.py): every piece at 3x over " + src, 10, y, HI))
    y += 26
    for title, names, gr in groups:
        lay.append(("t", title, 10, y, HI))
        y += 20
        x, rowh = 10, 0
        for n in names:
            c = ps[n][0]
            cell = g[gr] if not n.startswith("m") else g["L"]
            if n == "house_plum3_mud":
                cell = g["L"]
            im = on_ground(c, cell, pad=8).resize(((c.w + 16) * S, (c.h + 16) * S), Image.NEAREST)
            if x + im.width > Wd - 10:
                x, y, rowh = 10, y + rowh + 26, 0
            lay.append(("i", (n, im), x, y, None))
            x += max(im.width + 16, 200)
            rowh = max(rowh, im.height)
        y += rowh + 32
    patch = town_patch(ps, g).resize((26 * 16 * S, 17 * 16 * S), Image.NEAREST)
    lay.append(("t", "Test patch at 3x: the main walk and the west branch, two houses, Marine Supply on its stub, the "
                     "trawlers moored along the branch, skirts (post / post / plain on the x%3 rhythm) and pilings "
                     "under the south faces, a lantern, a bollard, a sign, an egret", 10, y, HI))
    y += 20
    lay.append(("p", patch, 10, y, None))
    y += patch.height + 20
    ty = y
    y += 20 * (len(rows) + 6) + 16 * len(problems)
    out = Image.new("RGB", (max(Wd, patch.width + 20), y + 20), BG)
    d = ImageDraw.Draw(out)
    for kind, v, x, yy, col in lay:
        if kind == "t":
            d.text((x, yy), v, fill=col)
        elif kind == "i":
            n, im = v
            out.paste(im, (x, yy))
            m = index[n]
            extra = f", door {m['doors'][0]}" if m.get("doors") else ""
            d.text((x, yy + im.height + 3), f"{n} {m['w']}x{m['h']}{extra}: {own[n]} tiles", fill=FG)
        else:
            out.paste(v, (x, yy))
    d.text((10, ty), "Tile census: unique 8x8 tiles (flipped copies and clear tiles are free), group by group; "
                     "'marginal' = tiles no group above already has", fill=HI)
    ty += 22
    tot_target = 0
    for title, names, target, n_own, n_new in rows:
        ok = target is None or n_new <= target
        tt = f"<= {target}" if target is not None else "(optional)"
        if target:
            tot_target += target
        d.text((10, ty), f"{title:28s} marginal {n_new:4d}   target {tt:10s}  (alone {n_own})   "
                         f"{'OK' if ok else 'OVER'}", fill=OK if ok else BAD)
        ty += 20
    est = BUILT - OLD_ART - OLD_TRAWLER + total
    d.text((10, ty), f"TOTAL new art: {total} tiles (targets add up to {tot_target} plus the optional pieces). "
                     f"orleans_harbor estimate: {BUILT} built - {OLD_ART} old art - {OLD_TRAWLER} old trawler + "
                     f"{total} = {est} of 512 (shop included, out of HOLD)", fill=HI)
    ty += 20
    for p in problems:
        d.text((10, ty), "PROBLEM: " + p, fill=BAD)
        ty += 16
    out.save(path)
    return est


def main():
    ps = pieces()
    index = {"_comment": "Land's End own art (make_lands_end_art.py): piece -> sheet and cell rectangle.", "pieces": {}}
    for sheet, width in (("planks", 8), ("art", 16)):
        items = [(n, v) for n, v in ps.items() if v[1] == sheet]
        pos, hc = pack(items, width)
        im = Image.new("RGB", (width * 16, hc * 16), KEY)
        for name, (c, _, info) in items:
            x, y = pos[name]
            im.paste(c.im, (x * 16, y * 16), c.im)
            empty = [[i, j] for j in range(c.h // 16) for i in range(c.w // 16)
                     if all(c.get(i * 16 + a, j * 16 + b) is None for a in range(16) for b in range(16))]
            index["pieces"][name] = dict({"sheet": sheet, "x": x, "y": y, "w": c.w // 16, "h": c.h // 16,
                                          "empty": empty}, **info)
        im.save(os.path.join(HERE, f"lands_end_{sheet}.png"))
    with open(os.path.join(HERE, "lands_end.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, indent=1)
        f.write("\n")
    # preview: every overlay piece over Ekat water, planks as they are, at 3x
    art = Image.open(os.path.join(HERE, "lands_end_art.png")).convert("RGB")
    planks = Image.open(os.path.join(HERE, "lands_end_planks.png")).convert("RGB")
    prev = Image.new("RGB", (art.width, art.height + planks.height + 16), WATER)
    for im, oy in ((art, 0), (planks, art.height + 16)):
        a = np.array(im)
        m = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
        prev.paste(im, (0, oy), Image.fromarray((m * 255).astype(np.uint8)))
    prev.resize((prev.width * 3, prev.height * 3), Image.NEAREST).save(os.path.join(HERE, "lands_end_preview.png"))
    problems = check(ps)
    for n, p in index["pieces"].items():
        for dcell in p.get("doors", []):
            if dcell in p["empty"]:
                problems.append(f"{n}: door cell {dcell} is empty")
    rows, total = census(ps)
    est = review(ps, index["pieces"], rows, total, problems, os.path.join(MAPGEN, "maps", "00_lands_end_art.png"))
    print("lands_end art:", len(ps), "pieces")
    for title, names, target, n_own, n_new in rows:
        print(f"  {title:28s} {n_new:4d} marginal (alone {n_own}), target {target}")
    print(f"  TOTAL new art {total}; orleans_harbor estimate {est} of 512")
    for p in problems:
        print("  PROBLEM:", p)


if __name__ == "__main__":
    main()

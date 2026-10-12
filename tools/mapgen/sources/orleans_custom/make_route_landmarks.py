"""Own art: the route landmarks of Routes 2-25 (art_requests/route_landmarks.md), drawn in Python, no source tiles.

Every piece is an overlay (magenta (255, 0, 255) = clear) that sits on whatever ground the generator puts under it
(grass, mud, marsh, dry ground, water), like make_props.py / make_bridge.py output. Pieces that stand in water carry
no water of their own: only ripple and splash accents at their base, drawn over Ekat's pond teal. Lit from the
top-left; 1 px dark outlines; <= 15 GBA-exact colours per piece; symmetric pieces are mirrored (their right halves
are flipped tiles); repeat elements (rail ties, brick courses, deck planks, steps) repeat every 8 px so they share
tiles.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_route_landmarks.py
writes
    sources/orleans_custom/route_landmarks.png          the sheet (16 px cells, magenta = clear)
    sources/orleans_custom/route_landmarks.json         the index (the camp / dry-country / hollow format, read by
                                                        redfield_tileset.add_pieces): {"png", "pieces": {name: {x, y,
                                                        w, h, doors, passable, empty, comment, tilesets, over}}} and,
                                                        ready to paste, "source" (the recipe image source "lmk") and
                                                        "prefabs" ({name: {"rows": [[{"overlay": "lmk:x_y"}...]]}})
    sources/orleans_custom/route_landmarks_preview.png  the sheet at 3x on Ekat grass
    maps/00_route_landmarks_art.png                     the review sheet: every piece at 3x on its ground, test
                                                        patches, unique 8x8 tile counts

Index extras (hints for the routes agent): "tilesets" = the route tilesets the piece's routes use; "over" = cells
that read best drawn over the player (the wires the player walks under, tall tops).
"""
import json
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
KEY = (255, 0, 255)

# ---------------------------------------------------------------- colours (multiples of 8: GBA-exact)
INK = (40, 40, 48)                                                     # cool ink: steel, stone
INKW = (48, 40, 32)                                                    # warm ink: wood, bark
S0, S1, S2, S3 = (64, 72, 88), (96, 112, 128), (136, 152, 168), (184, 200, 208)   # steel, grey-blue
RU1, RU2, RU3 = (128, 64, 40), (176, 96, 56), (216, 144, 88)          # rust
C1, C2, C3 = (128, 128, 120), (168, 168, 160), (208, 208, 200)        # concrete
W1, W2, W3, W4 = (96, 64, 48), (136, 96, 64), (176, 136, 88), (216, 184, 128)     # timber
GW1, GW2, GW3, GW4 = (80, 72, 64), (112, 104, 88), (152, 144, 120), (192, 184, 160)  # sea-grey timber
ST1, ST2, ST3, ST4 = (88, 88, 80), (128, 128, 112), (168, 168, 144), (208, 208, 184)  # Rootkin stone
MO1, MO2 = (80, 112, 64), (128, 152, 80)                               # moss on stone
WD, WA, WL, WF = (72, 112, 112), (96, 136, 136), (152, 192, 184), (216, 232, 224)   # Ekat pond teal: shade, water, ripple, foam
Y1, Y2, WHT = (232, 176, 72), (248, 232, 152), (248, 248, 240)        # glow
R1, R2, R3 = (144, 40, 40), (200, 64, 56), (240, 120, 104)             # signal red
L0, L1, L2, L3, L4 = (40, 56, 40), (56, 88, 56), (80, 120, 64), (112, 152, 80), (160, 184, 104)  # leaves
MS1, MS2, MS3 = (112, 128, 112), (152, 168, 144), (200, 208, 176)     # Spanish moss
B0, B1, B2, B3 = (48, 40, 32), (88, 64, 48), (128, 96, 72), (168, 136, 104)       # bark
BR_L, BR, BR_D = (200, 112, 80), (168, 80, 56), (120, 56, 48)         # brick
SP1, SP2, SP3 = (88, 136, 232), (160, 216, 248), (248, 248, 248)      # electric spark
DSH = (160, 128, 88)                                                   # shade on dry ground (dry_country D3)


def _hh(x, y, k=0):
    """Repeatable noise in [0, 1)."""
    n = (x * 374761393 + y * 668265263 + k * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def ell(cx, cy, rx, ry):
    """Pixels whose centres lie in the ellipse."""
    for y in range(int(math.floor(cy - ry)) - 1, int(math.ceil(cy + ry)) + 1):
        for x in range(int(math.floor(cx - rx)) - 1, int(math.ceil(cx + rx)) + 1):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                yield x, y


def seg(x0, y0, x1, y1):
    """Bresenham line pixels."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


class Art:
    """One piece: w x h cells of 16 px, magenta = clear."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.W, self.H = w * 16, h * 16
        self.px = [[KEY] * self.W for _ in range(self.H)]

    def put(self, x, y, c):
        x, y = int(x), int(y)
        if c is not None and 0 <= x < self.W and 0 <= y < self.H:
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.W and 0 <= y < self.H else KEY

    def clear_at(self, x, y):
        return self.get(x, y) == KEY

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(min(x0, x1), y, max(x0, x1), y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, min(y0, y1), x, max(y0, y1), c)

    def line(self, x0, y0, x1, y1, c, behind=False):
        for x, y in seg(x0, y0, x1, y1):
            if not behind or self.clear_at(x, y):
                self.put(x, y, c)

    def fill(self, pts, c, behind=False):
        for x, y in pts:
            if not behind or self.clear_at(x, y):
                self.put(x, y, c)

    def sprite(self, x0, y0, rows, pal, flip=False, behind=False):
        """Hand-placed pixels: one string per row, '.' or ' ' clear; flip = mirrored; behind = only on clear pixels."""
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch in ". ":
                    continue
                if behind and not self.clear_at(x0 + i, y0 + j):
                    continue
                self.put(x0 + i, y0 + j, pal[ch])

    def mirror(self, y0=0, y1=None):
        """Rows y0..y1: the right half becomes the mirror of the left half."""
        y1 = self.H - 1 if y1 is None else y1
        for y in range(y0, y1 + 1):
            for x in range(self.W // 2):
                self.px[y][self.W - 1 - x] = self.px[y][x]

    def outline(self, c, skip=(), region=None):
        """Outer outline: clear pixels touching a drawn one (4-neighbours) become `c`."""
        x0, y0, x1, y1 = region or (0, 0, self.W - 1, self.H - 1)
        hits = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
                if self.px[y][x] == KEY and any(self.get(x + dx, y + dy) not in (KEY, c) + tuple(skip)
                                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in hits:
            self.px[y][x] = c

    def remap(self, table):
        for row in self.px:
            for i, c in enumerate(row):
                if c in table:
                    row[i] = table[c]

    def paste(self, other, ox, oy):
        for y in range(other.H):
            for x in range(other.W):
                c = other.px[y][x]
                if c != KEY:
                    self.put(ox + x, oy + y, c)

    def flipped(self):
        out = Art(self.w, self.h)
        out.px = [row[::-1] for row in self.px]
        return out

    def crop_cells(self, cx, cy, w, h):
        out = Art(w, h)
        out.px = [row[cx * 16:(cx + w) * 16] for row in self.px[cy * 16:(cy + h) * 16]]
        return out

    def colours(self):
        return {c for row in self.px for c in row if c != KEY}

    def image(self):
        im = Image.new("RGB", (self.W, self.H))
        im.putdata([c for row in self.px for c in row])
        return im


def ripple(a, x0, x1, y, dark=True, foam=False):
    """Water-line accents at the foot of something standing in water: a light ripple arc either side, a dark lap
    line along the base (where the object meets the water)."""
    for x in range(x0, x1 + 1):
        if a.clear_at(x, y) and dark:
            a.put(x, y, WD)
    a.hline(x0 - 3, x0 - 1, y, WL)
    a.hline(x1 + 1, x1 + 3, y, WL)
    a.put(x0 - 4, y + 1, WL)
    a.put(x1 + 4, y + 1, WL)
    if foam:
        a.put(x0 - 1, y, WF)
        a.put(x1 + 1, y, WF)


# ---------------------------------------------------------------- grounds (for the previews and the review sheet)
GROUND_CELLS = {"grass": ("ekat_swamp/swamp_tiles.png", 0, 0), "marsh": ("ekat_swamp/swamp_tiles.png", 2, 0),
                "water": ("ekat_swamp/swamp_tiles.png", 2, 15), "mud": ("ekat_swamp/swamp_tiles.png", 2, 10),
                "dry": ("orleans_custom/dry_country.png", 0, 0)}
_GROUND = {}


def ground_cell(kind):
    """One 16 px cell of a real ground tile from the source sheets the route tilesets are built from (snapped to
    GBA colours as the build does): Ekat's grass, marsh, pond water and mud, the dry country's plain earth."""
    if kind not in _GROUND:
        f, x, y = GROUND_CELLS[kind]
        im = Image.open(os.path.join(HERE, "..", f)).convert("RGB").crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16))
        _GROUND[kind] = im.point(lambda v: (v >> 3) << 3)
    return _GROUND[kind]


def _pixels(im):
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())


def ground(kind, w, h):
    """A w x h cell field of one ground (kind may also be a callable (cx, cy) -> kind)."""
    bg = Image.new("RGB", (w * 16, h * 16))
    for cy in range(h):
        for cx in range(w):
            k = kind(cx, cy) if callable(kind) else kind
            bg.paste(ground_cell(k), (cx * 16, cy * 16))
    return bg


def over(bg, im, x, y):
    """Paste an RGB image with magenta clear onto bg at pixel (x, y)."""
    m = Image.new("L", im.size, 0)
    m.putdata([0 if p == KEY else 255 for p in _pixels(im.convert("RGB"))])
    bg.paste(im, (x, y), m)
    return bg


def on_ground(im, kind, margin=0):
    bg = ground(kind, im.width // 16 + 2 * margin, im.height // 16 + 2 * margin)
    return over(bg, im, margin * 16, margin * 16)


# ================================================================ the pieces
# ---------------------------------------------------------------- rails (Route 4, Route 17)
def rail_v():
    """A piece of track running north-south: two steel rails over timber ties every 8 px (no ballast bed, so it
    lies on any ground); seamless along a run."""
    a = Art(1, 1)
    for t in (1, 9):
        a.rect(1, t, 14, t + 2, W2)
        a.hline(1, 14, t, W3)
        a.hline(1, 14, t + 2, W1)
        a.vline(1, t, t + 2, W1)
        a.vline(14, t, t + 2, W1)
        a.hline(2, 13, t + 3, INKW)               # the tie's shadow on the ground
        for x in (2, 5, 10, 13):                   # spike heads on the tie plates
            a.put(x, t + 1, S0)
    for x in (3, 11):
        a.vline(x, 0, 15, S3)
        a.vline(x + 1, 0, 15, S1)
        for y in range(16):
            if a.clear_at(x + 2, y):
                a.put(x + 2, y, INK)
    return a


def rail_h():
    """A piece of track running east-west (rail_v turned): rails at 3-4 and 11-12 px, ties every 8 px."""
    a = Art(1, 1)
    for t in (1, 9):
        a.rect(t, 1, t + 2, 14, W2)
        a.vline(t, 1, 14, W3)
        a.vline(t + 2, 1, 14, W1)
        a.hline(t, t + 2, 1, W3)
        a.hline(t, t + 2, 14, W1)
        a.vline(t + 3, 2, 14, INKW)
        for y in (2, 5, 10, 13):
            a.put(t + 1, y, S0)
    for y in (3, 11):
        a.hline(0, 15, y, S3)
        a.hline(0, 15, y + 1, S1)
        for x in range(16):
            if a.clear_at(x, y + 2):
                a.put(x, y + 2, INK)
    return a


# ---------------------------------------------------------------- the power line (Route 2)
WIRE_A, WIRE_B = 8, 12          # where the two wires leave the tower's top cell (px from its top), at its sides
SAG = 2                         # the wires hang this many px lower mid-span


def power_tower():
    """Steel lattice transmission pylon, 2x4: two crossarms with strings of glass insulators, an X-braced body
    that flares to concrete footings, rust at the joints. Mirror-symmetric (left half drawn)."""
    a = Art(2, 4)
    leg = lambda y: 12 - (y - 10) * 9 / 48          # the left leg's x from y=10 (x 12) to y=58 (x 3)
    # the peak (earth-wire point) and the cage under it
    a.vline(15, 0, 9, S1)
    a.put(14, 1, S0)
    a.vline(14, 2, 9, S0)
    a.vline(13, 3, 9, S2)
    a.put(15, 0, S3)
    # upper crossarm: full width, a strut under it back to the cage
    a.hline(0, 15, 2, S2)
    a.hline(0, 15, 3, S0)
    a.line(3, 4, 12, 6, S1)
    a.put(0, 2, S3)
    # lower crossarm
    a.hline(3, 15, 7, S2)
    a.hline(3, 15, 8, S0)
    a.line(6, 9, 12, 10, S1)
    # insulator strings: glass discs hanging under the arm ends, the wires leave from their feet
    for x, y0, y1 in ((0, 4, WIRE_A - 1), (4, 9, WIRE_B - 1)):
        for y in range(y0, y1 + 1):
            k = (y - y0) % 2
            a.put(x, y, S3 if k == 0 else S1)
            if x > 0:
                a.put(x + 1, y, S2 if k == 0 else KEY)
                a.put(x - 1, y, INK if k == 0 else KEY)
            else:
                a.put(x + 1, y, S2 if k == 0 else KEY)
    a.hline(0, 3, WIRE_B, INK)                 # the lower wire runs out past the upper insulators
    # the body: legs (ink outside, lit face, shade), horizontal struts, X-bracing in each panel
    panels = [10, 18, 27, 37, 48, 58]
    for y in range(10, 60):
        x = int(round(leg(min(y, 58))))
        a.put(x - 1, y, INK)
        a.put(x, y, S2)
        a.put(x + 1, y, S1)
    for k, y in enumerate(panels[:-1]):
        y2 = panels[k + 1]
        xl, xl2 = int(round(leg(y))), int(round(leg(y2)))
        a.line(xl + 2, y + 1, 15, y2 - 1, S1, behind=True)
        a.line(15, y + 1, xl2 + 2, y2 - 1, S1, behind=True)
        a.hline(xl + 2, 15, y, S0)
        a.put(xl, y, RU2)                         # rust at the joint, a streak under it
        a.put(xl + 1, y + 1, RU1)
    # concrete footing under the leg foot: a small plinth
    a.sprite(0, 58, ["..kkkkk.",
                     ".k33333k",
                     "k2222221k",
                     "k2222211k",
                     ".kkkkkkk."], {"k": INK, "3": C3, "2": C2, "1": C1})
    a.put(2, 59, S0)
    a.put(3, 59, S0)
    a.put(4, 59, S2)
    a.put(3, 58, INK)
    a.put(4, 58, S2)
    a.put(5, 58, S1)
    a.mirror()
    return a


def wire(shape):
    """One 1x1 cell of the two overhead wires between towers (walkable, drawn over the player): 'l' leaves the tower
    on its west and sags SAG px across the cell, 'm' hangs level at the bottom of the sag, 'r' rises to the tower
    on its east (= 'l' mirrored: flipped tiles)."""
    a = Art(1, 1)
    for y0 in (WIRE_A, WIRE_B):
        for x in range(16):
            if shape == "m":
                dy = SAG
            else:
                t = x if shape == "l" else 15 - x
                dy = 0 if t < 4 else 1 if t < 11 else 2
            a.put(x, y0 + dy, INK)
    return a


def fallen_line(variant):
    """A snapped power cable lying on dry ground, 2x1: a fat black cable in loose curves, a scorch on the earth,
    the bare copper end sparking blue-white. Variant 'a' ends east, 'b' (a coil, a broken insulator) ends west."""
    a = Art(2, 1)
    if variant == "a":
        pts = [(0, 6), (5, 5), (10, 8), (14, 11), (19, 11), (23, 8), (26, 7)]
        end = (26, 7)
    else:
        pts = [(29, 7), (27, 12), (21, 12), (17, 9), (18, 5), (22, 4), (25, 7), (22, 10), (15, 11), (10, 9),
               (7, 7)]
        end = (7, 7)
    ex, ey = end
    d = 1 if variant == "a" else -1
    cx, cy = ex + d * 4, ey + 3                      # scorch on the earth under the spark: a burnt star
    for x, y in ell(cx, cy, 3.2, 1.6):
        a.put(x, y, B0)
    for k in range(10):
        ang = k * math.pi / 5 + 0.3
        n = 3 + int(_hh(k, 1, 5) * 3)
        for r in range(2, n + 2):
            a.put(cx + round(math.cos(ang) * r * 1.4), cy + round(math.sin(ang) * r * 0.6), B1)
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        path += list(seg(x0, y0, x1, y1))
    for x, y in path:                                  # the cable: 2 px, lit on top, its shadow under
        a.put(x, y + 2, DSH)
    for x, y in path:
        a.put(x, y + 1, INK)
    for x, y in path:
        a.put(x, y, S1)
    if variant == "b":                                 # a broken glass insulator still on the cable's far end
        a.sprite(27, 5, ["s3s", "S3S", "s3s", "S3S"], {"S": S2, "s": S1, "3": S3})
    cu = (216, 128, 64)                                # the bare end: copper strands fanned out, the spark
    for dx, dy in ((1, -1), (2, 0), (1, 1), (2, -2)):
        a.put(ex + d * dx, ey + dy, cu)
    sx, sy = ex + d * 4, ey - 2
    for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3), (2, -2), (-2, 2), (2, 2), (-2, -2), (4, -2), (-1, -4),
                   (-4, 1)):
        a.put(sx + dx, sy + dy, SP1)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2), (1, -1), (-1, 1)):
        a.put(sx + dx, sy + dy, SP2)
    a.put(sx, sy, SP3)
    a.put(sx + 1, sy - 1, SP3)
    a.put(sx + d * 6, sy - 3, SP2)
    a.put(sx - d * 3, sy + 4, SP1)
    return a


# ---------------------------------------------------------------- the shore lookout (Route 2)
BRASS, BRASS_D = (216, 168, 64), (152, 104, 48)
GLASS, GLASS_L = (56, 72, 96), (152, 176, 200)


def lookout():
    """A small wooden shore lookout, 3x4: a board-and-batten hut on short stilts, a railed deck on its flat roof
    with a brass spyglass on a tripod aimed out to sea, a ladder up its east side, a life ring hung on the rail.
    The door (shut) is in the bottom-centre cell with two steps up to it. The hut is mirror-symmetric; the
    spyglass, ladder, ring and latch are its only one-off tiles."""
    a = Art(3, 4)
    # ---- roof deck: planks seen from above, a railing along its front
    a.rect(2, 9, 23, 13, W3)
    for x in range(2, 24):
        if x % 8 == 5:
            a.vline(x, 9, 13, W2)
    a.rect(1, 14, 23, 16, W1)                                      # the roof's front edge (fascia)
    a.hline(1, 23, 14, W2)
    a.hline(1, 23, 17, INKW)
    a.vline(0, 9, 16, INKW)
    a.hline(1, 23, 8, INKW)
    for x in (2, 12):                                              # railing posts, top rail
        a.rect(x, 4, x + 1, 13, W2)
        a.put(x, 4, W4)
        a.vline(x + 2, 5, 13, INKW)
    a.hline(2, 23, 4, W4)
    a.hline(2, 23, 5, W2)
    a.hline(2, 23, 3, INKW)
    a.hline(2, 23, 9, W2)
    # ---- the hut walls: board and batten (8 px)
    a.rect(4, 18, 23, 55, W2)
    for x in range(4, 24):
        if x % 8 in (3, 7):
            a.vline(x, 18, 55, W1)
        elif x % 8 == 4:
            a.vline(x, 18, 55, W3)
    a.hline(4, 23, 18, W1)                                         # the eave's shadow
    a.vline(3, 17, 56, INKW)
    # window, shuttered
    a.rect(6, 23, 13, 33, W4)
    a.rect(7, 24, 12, 32, GLASS)
    a.line(8, 31, 11, 25, GLASS_L)
    a.vline(9, 24, 32, W4)
    a.hline(7, 12, 28, W4)
    a.rect(6, 34, 13, 35, W3)
    a.hline(6, 13, 36, INKW)
    a.vline(5, 23, 35, INKW)
    a.vline(14, 23, 35, INKW)
    a.hline(5, 14, 22, INKW)
    # the door: planks, two braces; shut
    a.rect(18, 29, 23, 55, W4)
    a.rect(19, 30, 23, 55, W1)
    for x in range(19, 24):
        if x % 3 == 0:
            a.vline(x, 30, 55, W2)
    a.hline(19, 23, 33, W3)
    a.hline(19, 23, 52, W3)
    a.hline(17, 23, 28, INKW)
    a.vline(17, 28, 55, INKW)
    # ---- the floor beam, stilts, steps
    a.rect(1, 56, 23, 57, W1)
    a.hline(1, 23, 56, W3)
    a.hline(1, 23, 58, INKW)
    a.rect(4, 59, 6, 63, W2)
    a.vline(4, 59, 63, W3)
    a.vline(7, 59, 63, INKW)
    a.vline(3, 59, 63, INKW)
    a.line(8, 60, 12, 63, W1)
    for k, y in enumerate((58, 61)):                               # steps up to the door
        a.rect(17 - k, y, 23, y + 1, W3)
        a.hline(17 - k, 23, y, W4)
        a.hline(17 - k, 23, y + 2, INKW)
    a.mirror()
    a.rect(26, 42, 27, 43, BRASS)                                  # the latch
    # ---- the spyglass on its tripod, on the roof deck behind the rail, aimed out to sea (east)
    a.line(32, 3, 32, 12, BRASS_D)
    a.line(31, 4, 28, 12, BRASS_D)
    a.line(33, 4, 36, 12, BRASS_D)
    a.line(25, 4, 37, 0, BRASS)
    a.line(25, 5, 37, 1, BRASS_D)
    a.line(26, 5, 38, 1, BRASS_D)
    a.put(30, 2, (248, 216, 128))
    a.put(33, 1, (248, 216, 128))
    a.fill(((38, 0), (39, 0), (39, 1), (38, 2)), INKW)
    a.fill(((24, 5), (24, 6), (25, 6)), INKW)
    a.put(39, 0, GLASS_L)
    for x in range(24, 40):                                        # the front rail in front of the tripod
        a.put(x, 4, W4)
        a.put(x, 5, W2)
    # ---- a life ring hung on the rail (west)
    for x, y in ell(8.5, 9, 4.4, 4.2):
        q = (x + 0.5 - 8.5) ** 2 + (y + 0.5 - 9) ** 2
        if 4.5 < q:
            ang = math.atan2(y + 0.5 - 9, x + 0.5 - 8.5)
            a.put(x, y, R2 if int((ang + math.pi) / (math.pi / 2) + 0.5) % 2 else WHT)
    # ---- the ladder up the east side to the roof deck
    for y in range(3, 64):
        a.put(42, y, INKW)
        a.put(43, y, W3)
        a.put(46, y, W2)
        a.put(47, y, INKW)
    for y in range(6, 64, 4):
        a.hline(44, 45, y, W3)
        a.hline(44, 45, y + 1, W1)
    return a


# ---------------------------------------------------------------- the freight car (Route 17)
CAR1, CAR2, CAR3 = (104, 40, 32), (144, 64, 48), (184, 96, 64)


def rail_car():
    """A boxcar standing on the east-west track, 3x2 (blocks): the track (rail_h's art) runs through its bottom row
    under the wheels; a sun-faded red body with ribs, a sliding door, a stencilled mark, two trucks of wheels."""
    a = Art(3, 2)
    r = rail_h()
    for i in range(3):
        a.paste(r, i * 16, 16)
    # body: roof walkway, side, sill
    a.rect(2, 2, 45, 3, C3)
    a.hline(2, 45, 1, INK)
    a.rect(2, 4, 45, 19, CAR2)
    a.hline(2, 45, 4, CAR3)
    a.hline(2, 45, 19, CAR1)
    for x in range(5, 45, 5):                                    # side ribs
        a.vline(x, 5, 18, CAR1)
        a.vline(x - 1, 5, 18, CAR3)
    a.vline(1, 2, 20, INK)
    a.vline(46, 2, 20, INK)
    a.put(1, 1, KEY)
    a.put(46, 1, KEY)
    # the sliding door
    a.rect(18, 5, 29, 19, CAR1)
    for x in range(19, 29, 3):
        a.vline(x, 6, 19, CAR2)
    a.hline(17, 30, 5, C2)                                        # door track
    a.vline(17, 5, 19, INK)
    a.vline(30, 5, 19, INK)
    a.rect(27, 11, 28, 13, C3)                                    # latch
    # stencil marks: a white herald and a line of lettering
    a.rect(6, 8, 12, 12, CAR1)
    a.rect(7, 9, 11, 11, C3)
    a.put(9, 10, CAR2)
    a.hline(34, 42, 9, C3)
    a.hline(34, 39, 11, C3)
    # rust streak and grab irons
    a.vline(43, 6, 12, CAR1)
    a.vline(3, 14, 17, C2)
    a.vline(44, 14, 17, C2)
    # underframe and trucks
    a.rect(2, 20, 45, 21, INK)
    for tx in (6, 30):
        a.rect(tx, 22, tx + 11, 24, S0)
        a.hline(tx, tx + 11, 22, S1)
        for wx in (tx + 2, tx + 9):                                # wheels on the near rail (y 27)
            for x, y in ell(wx + 0.5, 25, 3, 2.6):
                a.put(x, y, S0)
            a.put(wx, 24, S2)
            a.put(wx - 1, 25, S1)
            a.put(wx, 25, INK)
            a.hline(wx - 2, wx + 2, 27, INK)
        a.rect(tx + 4, 24, tx + 7, 25, S1)                         # the spring box
        a.hline(tx + 4, tx + 7, 24, S2)
    return a


# ---------------------------------------------------------------- the mill chimney (Route 17)
SOOT1, SOOT2 = (64, 56, 56), (96, 72, 64)


def chimney():
    """A tall brick sugar-mill chimney, 1x5: a corbelled crown with a soot stain running down from its mouth, iron
    bands every cell, a stone plinth. The shaft repeats every 16 px, so its middle cells are one cell's tiles."""
    a = Art(1, 5)

    def brick(x, y):
        if (y % 4) == 3:
            return BR_D                                            # mortar course (dark joint)
        if (x + (4 if (y // 4) % 2 else 0)) % 8 == 0:
            return BR_D
        return BR_L if x <= 4 else BR if x <= 10 else BR_D

    for y in range(6, 72):
        for x in range(3, 13):
            a.put(x, y, brick(x, y))
        a.put(2, y, INK)
        a.put(13, y, INK)
    for y in range(6, 72):
        if y % 16 == 10:                                           # iron bands
            a.hline(2, 13, y, S0)
            a.hline(3, 6, y, S1)
            a.hline(2, 13, y + 1, INK)
            a.put(12, y + 1, RU1)
            a.put(12, y + 2, RU1)
    # the crown: corbel courses and the mouth
    a.rect(1, 3, 14, 7, BR)
    a.hline(1, 14, 3, BR_L)
    a.hline(1, 14, 5, BR_D)
    a.hline(1, 14, 7, BR_D)
    a.vline(0, 3, 7, INK)
    a.vline(15, 3, 7, INK)
    a.hline(1, 14, 8, INK)
    a.rect(2, 1, 13, 2, INK)
    a.rect(4, 1, 11, 2, SOOT1)
    a.hline(1, 14, 0, INK)
    a.put(1, 1, INK)
    a.put(14, 1, INK)
    # the soot stain: the crown's top course blackened, a streak running down from the mouth, ragged at its foot
    for x in range(1, 15):
        for y in range(3, 5):
            if a.get(x, y) in (BR_L, BR, BR_D):
                a.put(x, y, SOOT2 if y == 3 else SOOT1)
    for x in range(4, 13):
        depth = 12 + int(_hh(x, 0, 9) * 6) + (8 if 6 <= x <= 10 else 0)
        for y in range(5, depth):
            c = a.get(x, y)
            if c in (BR_L, BR, BR_D):
                a.put(x, y, SOOT1 if (c == BR_D or y < depth - 5) else SOOT2)
    # the plinth
    a.rect(1, 72, 14, 78, C2)
    a.hline(1, 14, 72, C3)
    a.vline(12, 73, 78, C1)
    a.vline(13, 73, 78, C1)
    a.vline(14, 73, 78, C1)
    a.hline(1, 14, 75, C1)
    a.vline(0, 72, 78, INK)
    a.vline(15, 72, 78, INK)
    a.hline(0, 15, 79, INK)
    a.hline(1, 14, 71, INK)
    return a


# ---------------------------------------------------------------- the levee gate (Route 14)
def levee_gate():
    """Two heavy concrete gate posts either side of the 2-wide road, 4x2 (the middle two columns are open and
    walkable): each post carries a red-and-white swing bar folded back along the road edge (pointing away, north)
    on an iron hinge. Mirror-symmetric."""
    a = Art(4, 2)
    # the swing bar, folded back: rises from the hinge on the post away up the road edge
    for y in range(1, 18):
        c = R2 if (y // 4) % 2 == 0 else WHT
        a.put(10, y, c)
        a.put(11, y, c)
        a.put(12, y, R1 if c == R2 else C2)
        a.put(9, y, INK)
        a.put(13, y, INK)
    a.hline(10, 12, 0, INK)
    a.rect(9, 1, 13, 2, INK)                                        # the end cap and its reflector
    a.rect(10, 1, 12, 1, Y1)
    # the post: concrete, its top face, a hinge collar
    a.rect(7, 16, 14, 18, C3)
    a.rect(7, 19, 14, 29, C2)
    a.vline(13, 19, 29, C1)
    a.vline(14, 19, 29, C1)
    a.hline(7, 14, 24, C1)
    a.rect(7, 20, 14, 21, S0)                                       # the hinge band
    a.hline(7, 14, 20, S1)
    a.rect(10, 15, 12, 17, S0)
    a.put(10, 15, S2)
    a.vline(6, 16, 29, INK)
    a.vline(15, 16, 29, INK)
    a.hline(7, 14, 15, INK)
    a.put(9, 15, INK)
    a.hline(6, 15, 30, INK)
    # hazard chevrons on the post's road face
    for y in range(25, 30):
        for x in range(7, 15):
            if (x + y) % 4 == 0:
                a.put(x, y, Y1)
    # a counterweight block on the outer side of the post
    a.rect(2, 22, 6, 29, C1)
    a.hline(2, 6, 22, C2)
    a.vline(1, 22, 29, INK)
    a.hline(1, 6, 21, INK)
    a.hline(1, 6, 30, INK)
    a.mirror()
    return a


def poly(pts):
    """Pixels whose centres lie inside the polygon."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    out = []
    for y in range(int(min(ys)), int(max(ys)) + 1):
        cy = y + 0.5
        cross = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 <= cy < y1) or (y1 <= cy < y0):
                cross.append(x0 + (cy - y0) * (x1 - x0) / (y1 - y0))
        cross.sort()
        for xa, xb in zip(cross[::2], cross[1::2]):
            for x in range(int(math.ceil(xa - 0.5)), int(math.floor(xb - 0.5)) + 1):
                out.append((x, y))
    return out


# ---------------------------------------------------------------- in the water: buoy, beacon, ruins, piling
def channel_buoy():
    """A red-and-white channel buoy, 1x2 on water: a striped float riding low, a little red tower with a white
    band, a lit lamp under a hood; a dark lap line and ripple rings where it bobs (no water of its own)."""
    a = Art(1, 2)
    # lamp and hood
    a.hline(6, 9, 0, INK)
    a.rect(5, 1, 10, 1, INK)
    a.rect(6, 2, 9, 5, Y1)
    a.rect(6, 2, 7, 3, Y2)
    a.put(6, 2, WHT)
    a.vline(5, 2, 5, INK)
    a.vline(10, 2, 5, INK)
    a.rect(5, 6, 10, 6, INK)
    # the tower: two red legs, a red day-mark with a white band
    a.rect(5, 7, 10, 15, R2)
    a.vline(5, 7, 15, R3)
    a.vline(9, 7, 15, R1)
    a.vline(10, 7, 15, R1)
    a.rect(5, 10, 10, 11, WHT)
    a.put(10, 10, S3)
    a.put(10, 11, S3)
    a.vline(4, 7, 15, INK)
    a.vline(11, 7, 15, INK)
    # the float: a drum seen from a little above, red and white vertical stripes
    for x, y in ell(8, 17, 6.5, 2.2):
        a.put(x, y, R3)
    for x, y in ell(8, 17, 5, 1.2):
        a.put(x, y, R2)
    for y in range(18, 24):
        for x in range(2, 14):
            band = ((x - 2) // 3) % 2
            c = R2 if band == 0 else WHT
            if x >= 11:
                c = R1 if band == 0 else S3
            if x == 2:
                c = R3 if band == 0 else WHT
            a.put(x, y, c)
    a.hline(2, 13, 23, R1)
    a.vline(1, 17, 23, INK)
    a.vline(14, 17, 23, INK)
    a.hline(3, 12, 14, INK)
    a.fill(((2, 15), (1, 16), (13, 15), (14, 16)), INK)
    # where it meets the water
    a.hline(2, 13, 24, WD)
    a.hline(3, 12, 25, WD)
    ripple(a, 1, 14, 24, dark=False, foam=True)
    a.hline(4, 11, 27, WL)
    a.put(3, 26, WL)
    a.put(12, 26, WL)
    return a


GL1, GL2 = (56, 168, 104), (184, 248, 200)                           # the beacon's green light


def nav_beacon():
    """A navigation beacon on stilts, 2x3 on water: four creosoted piles braced in an X, a plank platform, a short
    post tower carrying a green lantern under a hood and a red day-mark triangle; a ladder down one pile."""
    a = Art(2, 3)
    # piles (front pair; the back pair peeks between them) and their X bracing
    for x in (5, 12):
        a.rect(x, 26, x + 2, 42, W1)
        a.vline(x, 26, 42, W2)
        a.vline(x - 1, 26, 42, INKW)
    a.line(8, 28, 14, 38, W2)
    a.line(8, 38, 14, 28, W2)
    a.rect(13, 26, 14, 38, W1)
    # platform
    a.rect(2, 21, 15, 23, W3)
    a.hline(2, 15, 21, W4)
    a.rect(2, 24, 15, 25, W1)
    a.hline(2, 15, 26, INKW)
    a.vline(1, 21, 25, INKW)
    a.hline(2, 15, 20, INKW)
    for x in range(2, 16):
        if x % 4 == 1:
            a.put(x, 22, W2)
    # rail: posts at the corners, a top rail
    a.rect(3, 16, 3, 20, W2)
    a.hline(3, 15, 16, W3)
    a.hline(3, 15, 17, INKW)
    a.vline(2, 16, 20, INKW)
    a.hline(2, 15, 15, INKW)
    # the tower post
    a.rect(14, 6, 15, 20, S1)
    a.vline(14, 6, 20, S2)
    a.vline(13, 6, 20, INK)
    # the red day-mark triangle on the post
    tri = poly([(10.5, 14.5), (16, 7.5), (21.5, 14.5)])
    a.fill(tri, R2)
    a.fill([(x, y) for x, y in tri if x < 14 and y > 11], R3)
    a.line(10, 15, 15, 8, INK)
    a.hline(10, 15, 15, INK)
    a.hline(13, 15, 12, WHT)
    # the lantern
    a.rect(11, 1, 15, 5, GL1)
    a.rect(12, 2, 13, 3, GL2)
    a.put(12, 2, WHT)
    a.vline(10, 1, 5, INK)
    a.hline(11, 15, 0, INK)
    a.hline(11, 15, 6, INK)
    a.put(10, 0, KEY)
    a.mirror()
    # water: the piles' lap lines and ripples
    for x in (5, 12, 17, 24):
        a.hline(x - 1, x + 3, 43, WD)
    for x0 in (2, 22):
        a.hline(x0, x0 + 7, 44, WL)
    a.hline(9, 22, 46, WL)
    a.put(1, 45, WL)
    a.put(30, 45, WL)
    # a ladder down the east pile
    for y in range(26, 43):
        a.put(28, y, W2)
    for y in range(27, 43, 3):
        a.hline(26, 28, y, W3)
    return a


def spiral(a, x0, y0, deep=ST1, lit=ST4):
    """A Rootkin spiral carved into stone: a dark groove with a lit lower edge, 7x7."""
    rows = ["..ddd..",
            ".d...d.",
            "d..dd.d",
            "d.d..dd",
            "d.d.d.d",
            ".d..d..",
            "..dd..."]
    a.sprite(x0, y0, rows, {"d": deep})
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "d" and j + 1 < len(rows) and rows[j + 1][i] == "." and a.get(x0 + i, y0 + j + 1) not in (KEY,):
                a.put(x0 + i, y0 + j + 1, lit)


def stone_column(a, x0, x1, top, base, seed=0):
    """A round stone column (lit from the left) from `top` to the waterline `base`, its top broken off ragged."""
    w = x1 - x0
    for x in range(x0, x1 + 1):
        t = (x - x0) / w
        c = ST4 if t < 0.15 else ST3 if t < 0.45 else ST2 if t < 0.8 else ST1
        jag = top + int(_hh(x, seed, 21) * 4) + (2 if (x - x0) % 5 == 2 else 0)
        for y in range(jag, base + 1):
            a.put(x, y, c)
        a.put(x, jag, ST4 if t < 0.6 else ST3)            # the fresh break catches the light
    a.outline(INK, region=(x0 - 1, 0, x1 + 1, base))
    # drum joints
    for y in range(top + 9, base, 9):
        for x in range(x0, x1 + 1):
            if a.get(x, y) != KEY:
                a.put(x, y, ST1)


def moss(a, x0, x1, y0, y1, seed=0):
    """Moss streaks on stone: thick at the waterline, thinning upwards."""
    for x in range(x0, x1 + 1):
        h = int(_hh(x, seed, 31) * (y1 - y0))
        for y in range(y1 - h, y1 + 1):
            c = a.get(x, y)
            if c in (ST1, ST2, ST3, ST4):
                a.put(x, y, MO1 if c in (ST1, ST2) else MO2)


def sunken_ruin():
    """A broken carved Rootkin pillar standing in water, 1x2: its top snapped off ragged, spiral carvings, moss
    climbing from the waterline; a lap line and ripples at its foot."""
    a = Art(1, 2)
    stone_column(a, 4, 11, 3, 26, seed=1)
    spiral(a, 5, 9)
    spiral(a, 5, 18)
    moss(a, 4, 11, 20, 26, seed=1)
    a.put(9, 5, MO2)
    a.put(10, 6, MO1)
    a.hline(3, 12, 27, WD)
    ripple(a, 3, 12, 27, dark=False, foam=True)
    a.hline(5, 10, 29, WL)
    return a


def sunken_ruin_l():
    """The larger ruin, 2x2 in water: a thick pillar stump beside a carved capital block that has toppled and lies
    half-sunk at a tilt, moss on both; ripples along the waterline."""
    a = Art(2, 2)
    stone_column(a, 3, 13, 5, 26, seed=4)
    spiral(a, 5, 12)
    moss(a, 3, 13, 19, 26, seed=4)
    # the toppled capital: a tilted block with a carved face
    blk = poly([(13, 18), (27, 14), (30, 26), (16, 27)])
    a.fill(blk, ST2)
    top = poly([(13, 18), (27, 14), (26, 12), (12, 16)])
    a.fill(top, ST4)
    a.fill([(x, y) for x, y in blk if x >= 27], ST1)
    a.line(13, 18, 27, 14, ST3)
    spiral(a, 18, 17)
    a.outline(INK, region=(11, 10, 31, 27))
    moss(a, 15, 29, 22, 26, seed=5)
    a.hline(2, 30, 27, WD)
    ripple(a, 2, 30, 27, dark=False, foam=True)
    a.hline(6, 12, 29, WL)
    a.hline(18, 26, 29, WL)
    return a


BARN1, BARN2 = (232, 224, 208), (176, 168, 152)
ROPE = W3                                                             # (keeps the piling in 15 colours)


def sunken_piling():
    """A barnacled piling in water, 1x2: an old round timber pile, its cut top showing the end grain, a frayed rope
    round it, a crust of barnacles and weed above the waterline; ripples at its foot."""
    a = Art(1, 2)
    for x in range(4, 12):
        t = (x - 4) / 7
        c = GW4 if t < 0.15 else GW3 if t < 0.45 else GW2 if t < 0.8 else GW1
        for y in range(4, 27):
            a.put(x, y, c)
    for y in range(6, 26, 5):                                          # grain checks
        a.vline(7 + (y % 3), y, y + 2, GW1)
    for x, y in ell(8, 3.5, 4, 2):                                     # the cut top
        a.put(x, y, W3)
    for x, y in ell(8, 3.5, 2, 1):
        a.put(x, y, W2)
    a.put(8, 3, W1)
    a.outline(INK)
    # the rope
    for x in range(4, 12):
        a.put(x, 11 + (x % 2), ROPE)
        a.put(x, 12 + (x % 2), W2 if x % 2 else ROPE)
    a.vline(12, 12, 15, ROPE)
    a.put(13, 16, ROPE)
    # barnacles above the waterline, weed at it
    for k, (x, y) in enumerate(((5, 18), (9, 17), (6, 21), (9, 22), (4, 24))):
        a.put(x, y, BARN1)
        a.put(x + 1, y, BARN2)
        a.put(x, y + 1, BARN2)
        a.put(x + 1, y + 1, INK if k % 2 else GW1)
    for x in range(4, 12):
        h = 1 + int(_hh(x, 2, 41) * 3)
        a.vline(x, 26 - h, 26, MO1 if x > 6 else MO2)
    a.hline(3, 12, 27, WD)
    ripple(a, 3, 12, 27, dark=False, foam=True)
    a.hline(5, 10, 29, WL)
    return a


# ---------------------------------------------------------------- the wreck (Routes 18, 22)
def shipwreck():
    """A half-sunk wooden hull, 4x3 on water, listing: the bow reared up out of the water on the west, the stern
    gone under on the east, the after planking stove in so the ribs show against the water, a broken mast leaning
    from the deck; weed on the hull, foam and ripples along the waterline."""
    a = Art(4, 3)
    WL_Y = 38                                                          # the waterline
    gun = lambda x: 9 + (x - 6) * 0.42                                 # the gunwale, high at the bow
    # the hull side: bow stem curving down to the water, strakes following the sheer
    hull = poly([(4, 8), (7, 7.5), (60, 9 + 54 * 0.42), (60, WL_Y + 1), (13, WL_Y + 1), (8, 30), (4, 17)])
    for x, y in hull:
        if y > WL_Y:
            continue
        d = y - gun(x)
        c = GW3 if d < 12 else GW2                                    # the hull turns under: darker low down
        if x < 8 + d * 0.25:
            c = GW4 if d < 12 else GW3                                 # the bow's flare catches the light
        if int(d) % 4 == 3:
            c = GW2 if c in (GW3, GW4) else GW1                        # plank seams follow the sheer
        a.put(x, y, c)
    # the gunwale cap and a sliver of deck seen from above
    for x in range(5, 61):
        g = int(round(gun(x)))
        a.put(x, g - 1, GW4)
        a.put(x, g - 2, W2)
        a.put(x, g - 3, INKW)
        a.put(x, g, GW1)
    # the after part stove in: ribs against the water
    for x in range(38, 61):
        g = int(round(gun(x)))
        for y in range(g + 1, WL_Y + 1):
            rib = (x - 38) % 6 in (0, 1)
            torn = y > g + 2 + int(_hh(x, 3, 51) * 6) or x > 50
            if torn and not rib:
                a.put(x, y, KEY)
            elif rib:
                a.put(x, y, GW2 if (x - 38) % 6 == 0 else INKW)
    for x in range(52, 61):                                            # the stern rail sags, broken
        g = int(round(gun(x)))
        if (x - 52) % 4 == 3:
            for y in range(g - 3, g + 1):
                a.put(x, y, KEY)
    # the bow stem post and a rusted anchor ring
    a.line(4, 8, 4, 17, GW4)
    a.line(5, 17, 9, 31, GW1)
    a.fill(((9, 14), (10, 14), (11, 15), (10, 16), (9, 16), (8, 15)), RU1)
    a.put(9, 15, KEY)
    a.put(10, 15, KEY)
    # weed and wet wood along the waterline
    for x in range(10, 50):
        h = 1 + int(_hh(x, 4, 61) * 4)
        for y in range(WL_Y - h, WL_Y + 1):
            if a.get(x, y) in (GW1, GW2, GW3):
                a.put(x, y, MO1 if y > WL_Y - 2 else MO2)
    # the broken mast leaning aft, a torn yard
    for t in range(0, 19):                                             # y 18 (the deck) up to 0
        y, x = 18 - t, int(round(26 + t * 0.34))
        a.put(x - 1, y, INKW)
        a.put(x, y, W3)
        a.put(x + 1, y, W2)
        a.put(x + 2, y, INKW)
    for x, y in ((31, 0), (33, 0), (32, 1)):                           # splintered top
        a.put(x, y, KEY)
    a.put(32, 0, W3)
    a.line(27, 8, 41, 13, W2)                                          # a fallen yard
    a.line(27, 9, 41, 14, INKW)
    a.line(33, 2, 47, 18, INKW)                                        # a slack stay to the hull
    a.outline(INKW, region=(0, 0, 63, WL_Y))
    for x in range(64):                                                # the outline must not sit on the water
        if a.get(x, WL_Y + 1) == INKW:
            a.put(x, WL_Y + 1, KEY)
    # the waterline: lap shadow, foam where the hull meets it, ripples
    for x in range(8, 62):
        if a.get(x, WL_Y) != KEY:
            a.put(x, WL_Y + 1, WD)
    for x in range(8, 62, 1):
        if a.get(x, WL_Y + 1) == WD and _hh(x, 6, 71) < 0.3:
            a.put(x, WL_Y + 1, WF)
    a.hline(2, 8, WL_Y + 1, WL)
    a.put(1, WL_Y + 2, WL)
    a.hline(16, 28, WL_Y + 4, WL)
    a.hline(36, 50, WL_Y + 3, WL)
    a.hline(54, 60, WL_Y + 6, WL)
    a.put(62, WL_Y + 1, WF)
    a.put(63, WL_Y + 2, WL)
    return a


# ---------------------------------------------------------------- the oyster bed (Route 19)
SH0, SH1, SH2, SH3 = (72, 64, 64), (120, 112, 104), (168, 160, 144), (216, 208, 192)
NACRE = (208, 192, 224)


def oyster_bed():
    """A heap of oyster shells and stones on an islet, 3x2: grey shells piled in a low mound (back rows higher),
    a few turned up showing their pearly insides, wet and darker at the foot, two stones."""
    a = Art(3, 2)
    mound = set(ell(24, 21, 21, 9)) | set(ell(17, 18, 11, 9)) | set(ell(31, 19, 11, 8))
    for x, y in mound:
        a.put(x, y, SH1)
    shells = []
    for row, y in enumerate((12, 16, 20, 24, 27)):
        for k in range(8):
            x = 5 + k * 5.6 + (2.8 if row % 2 else 0) + (_hh(k, row, 83) - 0.5) * 2
            if (int(x), int(y)) in mound:
                shells.append((y + (_hh(k, row, 84) - 0.5) * 1.5, x, row * 8 + k))
    for y, x, k in sorted(shells):
        wet = y > 25
        rx, ry = 3.3, 2.1
        pts = [p for p in ell(x, y, rx, ry) if p in mound]
        for px, py in pts:
            dx, dy = (px + 0.5 - x) / rx, (py + 0.5 - y) / ry
            c = SH3 if dx + dy < -0.9 else SH2 if dx + dy < 0.5 else SH1
            if k % 5 == 2 and not wet and dx * dx + dy * dy < 0.4:
                c = NACRE                                              # an open shell: nacre inside
            if wet:
                c = {SH3: SH2, SH2: SH1, SH1: SH1, NACRE: SH2}[c]
            a.put(px, py, c)
        for px, py in pts:                                             # each shell's dark lip on its shadow side
            dx, dy = (px + 0.5 - x) / rx, (py + 0.5 - y) / ry
            if dx * dx + dy * dy > 0.55 and dx + dy > 0.4:
                a.put(px, py, SH0)
        if k % 5 == 2 and not wet:
            a.put(int(x) - 1, int(y) - 1, WHT)
    for cx, cy, r in ((9, 25, 3.4),):                                 # a stone (mirrored: two)
        for px, py in ell(cx, cy, r, r * 0.7):
            dx, dy = px + 0.5 - cx, py + 0.5 - cy
            a.put(px, py, ST3 if dx + dy < -1 else ST2 if dx + dy < 1.2 else ST1)
    a.outline(INK)
    a.mirror()
    for x, y in ((30, 13), (34, 18)):                                   # a couple of glints off the mirror
        a.put(x, y, WHT)
    return a


# ---------------------------------------------------------------- the heron roost (Route 20)
DROP, DROP_D = (248, 248, 240), (200, 200, 184)


def bird_platform():
    """A heron roost, 6x3 on water: a weathered plank platform on pilings, dead-branch perches standing up from it,
    a stick nest, white droppings splashed over the deck and down the edge; ripples at the pilings. The platform is
    mirror-symmetric (its cells repeat); perches, nest and droppings are the only one-off tiles."""
    a = Art(6, 3)
    for x in (5, 37):                                                  # pilings with their lap lines
        a.rect(x, 26, x + 3, 41, GW2)
        a.vline(x, 26, 41, GW3)
        a.vline(x + 3, 26, 41, GW1)
        a.vline(x - 1, 26, 41, INKW)
        a.vline(x + 4, 26, 41, INKW)
        a.hline(x - 1, x + 4, 42, WD)
        a.hline(x - 4, x - 2, 42, WL)
        a.hline(x + 5, x + 7, 42, WL)
        a.hline(x - 1, x + 4, 44, WL)
    a.rect(1, 12, 47, 24, GW3)                                         # deck planks, seams every 8 px
    for x in range(1, 48):
        if x % 8 == 0:
            a.vline(x, 12, 24, GW2)
        if x % 8 == 1:
            a.vline(x, 12, 24, GW4)
    a.hline(1, 47, 12, GW4)
    a.rect(1, 25, 47, 28, GW2)                                         # the front beam, bolts every 8 px
    a.hline(1, 47, 25, GW1)
    a.hline(1, 47, 28, GW1)
    for x in range(4, 48, 8):
        a.put(x, 26, INKW)
    a.hline(1, 47, 11, INKW)
    a.hline(1, 47, 29, INKW)
    a.vline(0, 12, 28, INKW)
    # perches: dead branches standing up from the deck (one each side, mirrored)
    bx, top = 20, 1
    for y in range(top + 3, 21):
        a.put(bx, y, B1)
        a.put(bx + 1, y, B0)
        a.put(bx - 1, y, INKW)
    a.put(bx, top + 3, B2)
    for dx, dy in ((-4, -3), (3, -4)):
        a.line(bx, top + 6, bx + dx, top + 6 + dy, B1)
        a.put(bx + dx, top + 6 + dy - 1, B2)
    a.hline(bx - 2, bx + 3, 21, B0)
    for x, y in ((17, 22), (23, 18), (11, 15)):                       # droppings under the perch, a run
        a.put(x, y, DROP)
        a.put(x + 1, y, DROP_D)
        a.put(x, y + 1, DROP_D)
    a.vline(21, 25, 28, DROP)
    # a stick nest across the middle (its left half; mirrored)
    nx, ny = 38, 15
    for k in range(8):
        x0 = nx + int(_hh(k, nx, 91) * 6)
        a.line(x0, ny + 1 + k % 3, min(47, x0 + 4), ny + (k + 1) % 3, B2 if k % 2 else B1)
    a.hline(nx + 1, 47, ny + 4, B0)
    a.put(46, ny, DROP)
    a.put(47, ny, DROP_D)
    a.mirror()
    return a


# ---------------------------------------------------------------- the abandoned offshore platform (Route 21)
DARK = (24, 24, 32)


def offshore_platform():
    """A rusted, abandoned offshore platform, 6x6 on water (the reserved 6x3 + 6x3, as one picture): a steel deck
    on four great legs braced in an X, barnacled and rust-banded at the waterline; a railing round it; the lattice
    stub of the derrick in the middle, snapped off and bent; oil drums on either side, rust bleeding over the
    plates; one stretch of the front rail bent down. Mirror-symmetric (left half drawn) apart from the damage, and
    deck, girder and legs repeat every 8-16 px, so it costs few tiles for its size."""
    a = Art(6, 6)
    WLY = 88
    # ---- legs: a front leg, a back leg in shadow, X bracing between
    x0 = 10
    a.rect(x0, 60, x0 + 11, WLY, S1)
    a.vline(x0, 60, WLY, S2)
    a.vline(x0 + 1, 60, WLY, S3)
    a.rect(x0 + 8, 60, x0 + 11, WLY, S0)
    for y in range(64, WLY, 8):
        a.hline(x0, x0 + 11, y, S0)
    a.vline(x0 - 1, 60, WLY, INK)
    a.vline(x0 + 12, 60, WLY, INK)
    a.rect(x0, WLY - 5, x0 + 11, WLY, RU1)
    a.hline(x0, x0 + 11, WLY - 6, RU2)
    for k in range(4):
        a.put(x0 + 1 + k * 3, WLY - 3 + k % 2, C3)
    a.rect(36, 60, 43, WLY, S0)
    a.vline(37, 60, WLY, S1)
    a.vline(35, 60, WLY, INK)
    a.vline(44, 60, WLY, INK)
    a.rect(36, WLY - 4, 43, WLY, RU1)
    a.line(23, 64, 34, 84, S0)
    a.line(23, 84, 34, 64, S0)
    a.hline(x0 - 1, x0 + 12, WLY + 1, WD)                             # water at the feet
    a.hline(x0 - 4, x0 - 2, WLY + 1, WL)
    a.hline(x0, x0 + 9, WLY + 3, WL)
    a.hline(35, 44, WLY + 1, WD)
    a.hline(25, 31, WLY + 2, WL)
    a.put(x0 + 12, WLY + 1, WF)
    # ---- the front girder, its bolts bleeding rust, the hazard stripe
    a.rect(1, 54, 47, 59, S1)
    a.hline(1, 47, 54, S2)
    a.hline(1, 47, 59, S0)
    for x in range(4, 48, 8):
        a.put(x, 57, S0)
        a.vline(x, 58, 59, RU1)
    a.hline(1, 47, 60, INK)
    a.vline(0, 14, 59, INK)
    for x in range(1, 48, 4):
        a.hline(x, x + 1, 53, Y1)
    # ---- the deck plates, seams every 16 px
    for y in range(14, 53):
        for x in range(1, 48):
            a.put(x, y, C1 if x % 16 == 0 or y % 16 == 0 else C3 if x % 16 == 1 or y % 16 == 1 else C2)
    # ---- the railing: back rail and front rail, posts every 8 px
    for x in range(4, 48, 8):
        a.vline(x, 8, 14, S2)
        a.vline(x + 1, 8, 14, S0)
        a.vline(x, 47, 53, S2)
        a.vline(x + 1, 47, 53, S0)
    for y in (8, 47):
        a.hline(1, 47, y, S3)
        a.hline(1, 47, y + 1, S0)
    # ---- oil drums by the west rail
    for dx in (6, 13):
        a.rect(dx, 31, dx + 5, 39, RU2)
        a.vline(dx, 31, 39, RU3)
        a.vline(dx + 5, 31, 39, RU1)
        a.hline(dx, dx + 5, 34, RU1)
        a.hline(dx, dx + 5, 31, RU3)
        a.hline(dx - 1, dx + 6, 30, INK)
        a.vline(dx - 1, 30, 40, INK)
        a.vline(dx + 6, 30, 40, INK)
        a.hline(dx - 1, dx + 6, 40, INK)
    # ---- the derrick stub in the middle: a rusty lattice snapped off above the deck (left half)
    base_l, top_l = 30, 38
    fx = lambda t: round(top_l + (base_l - top_l) * t)
    for y in range(0, 43):
        xl = fx(y / 42)
        a.put(xl - 1, y, INK)
        a.put(xl, y, RU3)
        a.put(xl + 1, y, RU1)
    for y0, y1 in ((4, 16), (16, 29), (29, 42)):
        l0, l1 = fx(y0 / 42), fx(y1 / 42)
        a.line(l0 + 2, y0, 47, y1, RU1)
        a.line(47, y0, l1 + 2, y1, RU1)
        a.hline(l1 + 1, 47, y1, RU2)
    a.rect(base_l - 2, 42, 47, 44, S0)                                  # its foot plate
    a.hline(base_l - 2, 47, 45, INK)
    a.vline(base_l - 3, 42, 45, INK)
    a.mirror()
    a.vline(95, 14, 59, INK)
    # ---- the damage (not mirrored): the snapped top bent over, a bent stretch of rail, a rust stain
    for x, y in ((37, 0), (38, 0), (58, 0), (59, 1), (47, 0), (48, 0)):
        a.put(x, y, KEY)
    a.line(57, 2, 63, 6, RU2)
    a.line(57, 3, 63, 7, INK)
    a.put(38, 1, RU2)
    for x in range(28, 45):
        for y in (47, 48):
            a.put(x, y, C1 if y % 16 == 0 else C3 if y % 16 == 1 else C2)
    for x in (28, 36, 44):
        a.vline(x, 47, 53, C2)
        a.vline(x + 1, 47, 53, C2)
    a.line(27, 47, 36, 52, S3)
    a.line(27, 48, 36, 53, S0)
    a.line(45, 47, 39, 51, S3)
    for x, y in ell(74, 24, 6, 3):
        if a.get(x, y) in (C1, C2, C3):
            a.put(x, y, RU2 if ((x - 74) / 6) ** 2 + ((y - 24) / 3) ** 2 < 0.45 else RU3)
    return a


# ---------------------------------------------------------------- the Oldest Shrine's steps (Route 25)
def shrine_steps():
    """Worn stone steps rising out of the water to the shrine island, 6x3: five steps between two carved cheek
    walls (blocking), the flight walkable (the middle four columns); a few chipped nosings, moss in the joints by
    the walls and along the waterline; the lowest step meets the water with a lap line and ripples. Mirror-
    symmetric, every course 8 px, so the flight repeats."""
    a = Art(6, 3)
    WLY = 40
    for k in range(5):
        y = k * 8
        a.rect(16, y, 47, y + 4, ST3)
        a.hline(16, 47, y, ST4)
        a.rect(16, y + 5, 47, y + 7, ST2)
        a.hline(16, 47, y + 7, ST1)
        for x in range(16, 48):
            if (x + k * 8) % 16 == 0:
                a.vline(x, y + 1, y + 4, ST2)
    x0 = 4                                                              # the cheek wall
    a.rect(x0, 0, x0 + 11, WLY - 1, ST2)
    a.vline(x0, 0, WLY - 1, ST4)
    a.vline(x0 + 1, 0, WLY - 1, ST3)
    a.vline(x0 + 10, 0, WLY - 1, ST1)
    a.vline(x0 + 11, 0, WLY - 1, ST1)
    for y in (13, 27):
        a.hline(x0, x0 + 11, y, ST1)
        a.hline(x0, x0 + 11, y + 1, ST3)
    a.vline(x0 - 1, 0, WLY - 1, INK)
    a.vline(x0 + 12, 0, WLY - 1, INK)
    spiral(a, x0 + 3, 3)
    for x in range(16, 20):                                            # moss in the joints by the wall
        for y in range(0, WLY):
            if y % 8 in (5, 6, 7) and (x - 16) < 3 - (y // 8) % 2:
                a.put(x, y, MO1)
    for x in range(4, 48):                                             # moss along the waterline (16 px period)
        h = (1, 3, 2, 4, 1, 2, 3, 1)[(x % 16) // 2]
        for y in range(WLY - 1 - h, WLY):
            if a.get(x, y) in (ST1, ST2, ST3, ST4):
                a.put(x, y, MO1 if y > WLY - 3 else MO2)
    a.hline(3, 47, WLY, WD)
    a.hline(0, 2, WLY, WL)
    a.hline(12, 30, WLY + 2, WL)
    a.mirror()
    for x, y in ((22, 5), (23, 5), (23, 6), (66, 21), (67, 21), (67, 22)):   # two chipped nosings
        a.put(x, y, ST1)
    a.put(40, WLY, WF)
    a.put(41, WLY, WF)
    return a


# ---------------------------------------------------------------- the drowned temple gate (Route 22)
SEAL1, SEAL2 = (72, 160, 160), (152, 224, 216)


def temple_gate():
    """A half-flooded Rootkin temple doorway, 5x4: a stepped crest over a carved lintel of spirals, a stone facade
    on its platform, pillars carved with spirals, a corbelled doorway sealed by a stone slab with a faintly glowing
    spiral seal (the dive entrance: the door cell is the bottom centre), steps going down into the water. Mirror-
    symmetric (moss and vines too); blocks and spirals sit on a 16 px rhythm, so the facade repeats."""
    a = Art(5, 4)
    WLY = 56
    a.rect(2, 16, 39, WLY - 1, ST2)                                   # the facade blocks
    for y in range(16, WLY):
        for x in range(2, 40):
            if y % 8 == 7:
                a.put(x, y, ST1)
            elif y % 8 == 0:
                a.put(x, y, ST3)
            elif (x + (8 if (y // 8) % 2 else 0)) % 16 == 0:
                a.put(x, y, ST1)
    a.vline(2, 16, WLY - 1, ST3)
    a.vline(1, 16, WLY - 1, INK)
    a.rect(0, 7, 39, 16, ST3)                                         # the lintel: a band of spirals
    a.hline(0, 39, 7, ST4)
    a.hline(0, 39, 15, ST2)
    a.hline(0, 39, 16, ST1)
    a.hline(0, 39, 17, INK)
    a.hline(0, 39, 6, INK)
    for x in (4, 20):
        spiral(a, x, 8)
    a.vline(0, 6, 17, INK)
    for k, (x0, y0) in enumerate(((10, 3), (20, 0))):                 # the stepped crest
        a.rect(x0, y0 + 1, 39, 6, ST3 if k else ST2)
        a.hline(x0, 39, y0 + 1, ST4)
        a.hline(x0, 39, y0, INK)
        a.vline(x0 - 1, y0, 6, INK)
    a.rect(36, 1, 39, 4, ST1)                                         # a carved eye at the top
    a.rect(37, 2, 39, 3, SEAL1)
    a.rect(22, 18, 29, WLY - 1, ST3)                                  # the pillars by the door
    a.vline(22, 18, WLY - 1, ST4)
    a.vline(28, 18, WLY - 1, ST2)
    a.vline(29, 18, WLY - 1, ST1)
    a.vline(21, 18, WLY - 1, INK)
    a.vline(30, 18, WLY - 1, INK)
    spiral(a, 22, 24)
    spiral(a, 22, 40)
    for y in range(18, WLY):                                          # the corbelled doorway and its slab
        half = 8 if y >= 26 else 8 - (26 - y) // 2
        a.hline(40 - half - 1, 39, y, INK)
        if y >= 20:
            a.hline(40 - half, 39, y, ST2 if y < 46 else ST1)
    for y in range(20, 46, 6):
        a.hline(32, 39, y, ST1)
    a.vline(32, 26, 45, ST3)
    for k, y in enumerate((46, 49, 52)):                              # steps going down into the water
        x0 = 30 - k * 3
        a.rect(x0, y, 39, y + 1, ST4 if k == 0 else ST3)
        a.hline(x0, 39, y + 2, ST1)
        a.vline(x0 - 1, y, y + 2, INK)
    for vx, n in ((6, 14), (18, 8)):                                  # vines from the lintel
        for y in range(18, 18 + n):
            a.put(vx + (1 if (y // 3) % 2 else 0), y, MO1 if y % 4 else MO2)
        a.put(vx + 1, 18 + n, MO2)
    for x in range(0, 40):                                            # moss on the lintel and at the waterline
        if x % 16 in (3, 4, 11):
            a.put(x, 7, MO2)
            a.put(x, 6, MO1)
        h = (1, 3, 2, 4, 1, 2, 3, 1)[(x % 16) // 2]
        for y in range(WLY - 1 - h, WLY):
            if a.get(x, y) in (ST1, ST2, ST3, ST4):
                a.put(x, y, MO1 if y > WLY - 3 else MO2)
    for x in range(1, 40):                                            # the water at the foot
        if a.get(x, WLY - 1) != KEY:
            a.put(x, WLY, WD)
    a.hline(30, 39, WLY + 1, WD)
    a.hline(20, 26, WLY + 2, WL)
    a.hline(34, 39, WLY + 4, WL)
    a.hline(4, 12, WLY + 2, WL)
    for x in (24, 31):
        a.put(x, WLY, WF)
    a.mirror()
    for x, y in ell(40, 33, 6.2, 6.2):                                # the seal: a ring round a spiral, faintly lit
        q = ((x + 0.5 - 40) ** 2 + (y + 0.5 - 33) ** 2) ** 0.5
        if 5.0 < q:
            a.put(x, y, SEAL1)
    spiral(a, 37, 30, deep=SEAL1, lit=SEAL2)
    a.put(36, 28, SEAL2)
    return a


# ---------------------------------------------------------------- the mine tunnel (Route 24)
K0, K1, K2, K3 = (104, 96, 80), (152, 144, 120), (200, 192, 168), (240, 232, 216)   # the dry set's rock greys


def mine_mouth():
    """A timbered mine tunnel mouth in a rock face, 3x3, the door at the bottom centre: rock heaped round a timber
    set (two posts, a cap beam), a second set deeper in the dark, rusty rails running out of the tunnel, a lit
    lantern hanging from the cap."""
    a = Art(3, 3)
    blobs = [(10, 18, 11, 12), (24, 11, 13, 10), (38, 18, 11, 12), (8, 36, 9, 12), (40, 36, 9, 12),
             (24, 24, 20, 14), (15, 6, 6, 5), (33, 7, 8, 6)]
    for y in range(48):
        for x in range(48):
            best = None
            for cx, cy, rx, ry in blobs:
                q = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if q <= 1 and (best is None or cy > best[0][1]):
                    best = ((cx, cy, rx, ry), q)
            if best is None:
                continue
            (cx, cy, rx, ry), q = best
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            v = -0.65 * dx - 0.75 * dy
            c = K3 if v > 0.8 else K2 if v > 0.1 else K1 if v > -0.5 else K0
            if q > 0.82 and dy > 0.2:
                c = K0
            a.put(x, y, c)
    a.outline(B0)
    for x in range(48):                                                 # the rock sits on the ground: flat foot
        a.put(x, 47, a.get(x, 47) if a.get(x, 46) == KEY else B0)
    # cracks
    for pts in (((6, 14), (8, 16), (8, 18)), ((40, 12), (41, 14), (43, 15)), ((28, 4), (29, 6))):
        for x, y in pts:
            a.put(x, y, K0)
    # the tunnel: darkness, the inner set, the rails
    a.rect(15, 17, 32, 47, DARK)
    a.rect(19, 22, 20, 40, W1)
    a.rect(27, 22, 28, 40, W1)
    a.rect(18, 21, 29, 22, W1)
    for y, x0, x1 in ((38, 19, 28), (42, 18, 29), (46, 17, 30)):        # ties
        a.hline(x0, x1, y, W1)
        a.hline(x0, x1, y + 1, INKW)
    a.line(20, 34, 18, 47, RU2)                                         # rusty rails running out of the dark
    a.line(21, 34, 19, 47, RU1)
    a.line(27, 34, 29, 47, RU2)
    a.line(28, 34, 30, 47, RU1)
    # the timber set at the mouth
    for x0 in (12, 33):
        a.rect(x0, 16, x0 + 2, 47, W2)
        a.vline(x0, 16, 47, W3)
        a.vline(x0 + 2, 16, 47, W1)
        a.vline(x0 - 1, 16, 47, INKW)
        a.vline(x0 + 3, 16, 47, INKW)
    a.rect(10, 12, 37, 15, W2)
    a.hline(10, 37, 12, W3)
    a.hline(10, 37, 15, W1)
    a.hline(10, 37, 11, INKW)
    a.hline(10, 37, 16, INKW)
    a.vline(9, 11, 16, INKW)
    a.vline(38, 11, 16, INKW)
    a.rect(10, 13, 11, 14, W4)                                          # sawn ends
    a.rect(36, 13, 37, 14, W4)
    # the lantern on a hook from the cap beam
    a.vline(17, 17, 19, INK)
    a.rect(16, 20, 18, 20, INK)
    a.rect(15, 21, 19, 25, INK)
    a.rect(16, 22, 18, 24, Y1)
    a.put(16, 22, Y2)
    a.hline(16, 18, 26, INK)
    for x, y in ((14, 23), (20, 23), (17, 28), (14, 26), (20, 27)):      # its glow on the timbers
        if a.get(x, y) == DARK:
            a.put(x, y, W1)
    return a


# ---------------------------------------------------------------- trees and logs
CH1, CH2, ASH = (56, 48, 48), (88, 80, 72), (136, 128, 120)          # char
HEART, HEART_D = (216, 192, 144), (160, 128, 96)                     # split heartwood
GSH = (96, 128, 88)                                                  # shade on Ekat grass (its turf line)


def clumps(a, lobes, ramp, x_max=None, seed=0, shift=0.0):
    """Leaf clumps lit from the top-left (the dry-country crowns' way): each lobe (cx, cy, rx, ry) lit on top,
    darker below, a dark seam along its lower rim where it overlaps what was drawn before; lobes further down
    are nearer and drawn last. ramp = darkest..lightest (5)."""
    k0, k1, k2, k3, k4 = ramp
    x_max = a.W if x_max is None else x_max
    for cx, cy, rx, ry in sorted(lobes, key=lambda l: l[1]):
        for x, y in ell(cx, cy, rx, ry):
            if not (0 <= x < x_max):
                continue
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            v = -dy * 0.85 - dx * 0.3 + 0.25 * (_hh(x // 2, y // 2, 11 + seed) - 0.5) + shift
            c = k4 if v > 0.85 else k3 if v > 0.2 else k2 if v > -0.45 else k1
            rim = dx * dx + dy * dy
            if rim > 0.72 and dy > 0.35:
                c = k0 if rim > 0.88 else k1
            a.put(x, y, c)
    for y in range(a.H):                                              # sparse leaf flecks
        for x in range(x_max):
            c = a.px[y][x]
            if c == k2 and _hh(x, y, 12 + seed) < 0.1:
                a.px[y][x] = k3
            elif c == k3 and _hh(x, y, 13 + seed) < 0.08:
                a.px[y][x] = k2


def tube(a, pts, r, lit, mid, dark, ink=None):
    """A thick rounded limb or root along a polyline: lit on its upper side, dark under."""
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(n) + 1):
            path.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    if ink:
        for x, y in path:
            for px, py in ell(x, y, r + 1, r + 1):
                if a.clear_at(px, py):
                    a.put(px, py, ink)
    for x, y in path:
        for px, py in ell(x, y, r, r):
            dy = py + 0.5 - y
            a.put(px, py, lit if dy < -r * 0.35 else dark if dy > r * 0.35 else mid)


def scorched_cypress():
    """A lightning-split bald cypress on marsh, 3x3: the trunk riven down the middle into two charred halves leaning
    apart, the pale heartwood showing along the split, bare black snags, a few live branches still in leaf, cypress
    knees and flared roots at the foot."""
    a = Art(3, 3)
    # live foliage first (behind the trunk): one tuft high on the east, one lower on the west
    clumps(a, [(39, 8, 6, 4), (44, 11, 4, 3.5), (35, 12, 5, 3.5)], (L0, L1, L2, L3, L4), seed=1)
    clumps(a, [(7, 19, 5, 3.5), (11, 22, 4.5, 3)], (L0, L1, L2, L3, L4), seed=2)
    # the two halves of the trunk, leaning apart from the fork at y 28
    halves = [[(23, 40), (22, 28), (18, 16), (13, 3)], [(26, 40), (27, 28), (31, 16), (36, 4)]]
    for side, pts in enumerate(halves):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for t in range(0, 101):
                x = x0 + (x1 - x0) * t / 100
                y = y0 + (y1 - y0) * t / 100
                w = 3.5 - (40 - y) / 16                                 # thinner towards the top
                for px in range(int(round(x - w)), int(round(x + w)) + 1):
                    inner = (px >= x + w - 1.5) if side == 0 else (px <= x - w + 1.5)
                    outer_lit = side == 0 and px <= x - w + 1
                    a.put(px, round(y), HEART if inner and y < 30 else ASH if outer_lit else CH1)
    # the base: one solid flared trunk
    for y in range(28, 44):
        w = 6 + max(0, y - 34) * 0.9
        for x in range(int(24.5 - w), int(24.5 + w) + 1):
            t = (x - (24.5 - w)) / (2 * w)
            a.put(x, y, ASH if t < 0.18 else CH2 if t < 0.45 else CH1)
    for y in range(29, 44, 3):                                          # bark furrows
        for x in (21, 25, 28):
            if a.get(x, y) in (CH1, CH2):
                a.vline(x, y, y + 1, (40, 40, 48))
    a.line(24, 28, 25, 33, HEART_D)                                     # the split runs on into the base
    a.line(25, 33, 24, 36, (40, 40, 48))
    # snags: bare black branches
    for pts in (((15, 10), (8, 6), (5, 7)), ((18, 18), (12, 17)), ((32, 14), (37, 11)), ((34, 8), (40, 5)),
                ((29, 22), (34, 21), (37, 22))):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            a.line(x0, y0, x1, y1, CH1)
    # roots splaying into the marsh, and two knees
    for pts in (((18, 42), (12, 45), (6, 46)), ((21, 43), (18, 46), (16, 47)), ((31, 42), (37, 45), (43, 46)),
                ((28, 43), (31, 46), (33, 47))):
        tube(a, pts, 1.2, CH2, CH1, CH1)
    for kx in (7, 41):
        a.sprite(kx - 2, 41, ["..a..", ".ab..", ".abc.", "abbcc"], {"a": ASH, "b": CH2, "c": CH1})
    a.outline((40, 40, 48))
    return a


def great_oak():
    """The great live oak on marsh, 4x4: a vast spreading crown, a great limb sweeping out low on each side down to
    the ground (the live oak's way), beards of Spanish moss, a short massive trunk, roots coiling out over the
    ground like serpents. Mirror-symmetric (left half drawn), so its right half is flipped tiles."""
    a = Art(4, 4)
    half = 32
    # the crown: a broad dome of clumps, its lower edge scalloped
    lobes = [(30, 7, 9, 6.5), (18, 8, 8, 6), (8, 14, 7, 5.5), (25, 15, 9, 6.5), (5, 22, 4.5, 5), (14, 21, 8, 6),
             (30, 24, 8, 5.5), (7, 29, 6.5, 4.5), (21, 30, 7, 4.5)]
    clumps(a, lobes, (L0, L1, L2, L3, L4), x_max=half, seed=3)
    a.outline(L0, region=(0, 0, half - 1, 40))
    # the trunk
    for y in range(32, 55):
        w = 6 + max(0, y - 47) * 0.9
        for x in range(int(32 - w), half):
            t = (x - (32 - w)) / w
            c = B3 if t < 0.25 else B2 if t < 0.7 else B1
            if (x * 3 + y // 3) % 7 == 0 and t > 0.25:
                c = B1 if c == B2 else B0
            if y < 36:
                c = B1 if t < 0.6 else B0                             # in the crown's shade
            a.put(x, y, c)
        a.put(int(32 - w) - 1, y, B0)
    # the great limb sweeping out low and down to rest on the ground
    tube(a, [(28, 40), (20, 37), (11, 38), (5, 42), (3, 48)], 2.0, B3, B2, B1, ink=B0)
    tube(a, [(27, 36), (21, 32)], 1.6, B3, B2, B1)
    # roots like coiled serpents: thick roots snaking out, one coiling round on itself
    tube(a, [(27, 53), (19, 55), (12, 54), (8, 57), (10, 61), (16, 60)], 1.8, B3, B2, B1, ink=B0)
    tube(a, [(29, 55), (25, 59), (21, 62)], 1.4, B3, B2, B1, ink=B0)
    # Spanish moss: tapered beards from the crown's edge and the limb
    for x0, y0, n in ((5, 33, 7), (10, 33, 9), (16, 34, 6), (24, 34, 8), (8, 40, 6), (14, 39, 8), (19, 39, 5),
                      (2, 26, 6)):
        for k in range(n):
            x = x0 + (1 if k in (3, 4) else 0)
            a.put(x, y0 + k, MS3 if k < n // 2 else MS2 if k < n - 1 else MS1)
            if k < n - 3:
                a.put(x + 1, y0 + k, MS2 if k < n // 2 else MS1)
    a.mirror()
    return a


def felled_log():
    """A felled trunk lying on grass, 3x1: furrowed bark, a branch stub, a clean saw cut showing the rings (east),
    a broken end (west), a patch of moss; its shadow on the grass."""
    a = Art(3, 1)
    for x in range(3, 42):
        a.put(x, 14, GSH)
        a.put(x, 15, GSH if 5 < x < 40 else KEY)
    for y in range(3, 14):
        t = (y - 3) / 10
        for x in range(3, 42):
            c = B3 if t < 0.2 else B2 if t < 0.6 else B1
            if (x + (y // 3) * 3) % 7 == 0 and 0.2 <= t:
                c = B1 if c == B2 else B0
            a.put(x, y, c)
    for y in range(3, 14):                                              # the broken west end: splinters
        d = int(_hh(0, y, 131) * 3)
        for x in range(3, 3 + d):
            a.put(x, y, KEY)
        a.put(3 + d, y, HEART_D)
    for x, y in ell(42, 8.5, 4, 5.5):                                   # the saw cut: rings
        q = ((x + 0.5 - 42) / 4) ** 2 + ((y + 0.5 - 8.5) / 5.5) ** 2
        a.put(x, y, W2 if q > 0.75 else W4 if q > 0.45 else W3 if q > 0.15 else W2)
    a.put(42, 8, W1)
    a.rect(16, 0, 17, 3, B2)                                            # branch stub
    a.vline(16, 0, 3, B3)
    a.hline(16, 17, 0, HEART_D)
    for x in range(22, 31):                                             # moss on the top
        a.vline(x, 3, 3 + int(_hh(x, 1, 133) * 2), MO2 if x % 3 else MO1)
    a.outline(B0, skip=(GSH,))
    return a


def cut_stump():
    """A cut stump on grass, 1x1 (the Kleavorite spot): a clean axe-cut top showing its rings, a notch, furrowed
    bark, flaring roots; its shadow on the grass."""
    a = Art(1, 1)
    for x in range(2, 14):
        a.put(x, 15, GSH)
    for y in range(6, 14):
        w = 5 + (1 if y > 10 else 0) + (1 if y > 12 else 0)
        for x in range(8 - w, 8 + w):
            t = (x - (8 - w)) / (2 * w)
            c = B3 if t < 0.2 else B2 if t < 0.65 else B1
            if x % 3 == 1 and t > 0.2:
                c = B1
            a.put(x, y, c)
    for x, y in ell(8, 6, 5, 2.6):                                      # the cut top: rings
        q = ((x + 0.5 - 8) / 5) ** 2 + ((y + 0.5 - 6) / 2.6) ** 2
        a.put(x, y, W3 if q > 0.6 else W4 if q > 0.25 else W3)
    a.put(7, 6, W2)
    a.put(8, 6, W2)
    a.fill(((11, 4), (12, 5), (12, 6)), W2)                             # the axe notch
    a.outline(B0, skip=(GSH,))
    for x, y in ((2, 14), (13, 14), (1, 15), (14, 15)):                 # root flares
        a.put(x, y, B1)
    return a


# ================================================================ registration
SRC = "lmk"                                     # the recipe source name the prefab rows below refer to
DOOR = "MB_NON_ANIMATED_DOOR"
R, RV, RB, RD = "orleans_route", "orleans_river", "orleans_route_b", "orleans_route_dry"
PIECES = {}                                     # name -> (Art, meta)
ALIASES = {}                                    # name -> (piece, cell x0, cell y0, w, h, comment): a part of a piece


def add(name, art, comment, ground, tilesets, doors=(), walk=(), over=()):
    """Register a piece (the camp / dry-country / hollow index format, plus hints). `empty`: cells with nothing
    drawn (no tile needed)."""
    empty = [[i, j] for j in range(art.h) for i in range(art.w)
             if all(art.px[j * 16 + y][i * 16 + x] == KEY for y in range(16) for x in range(16))]
    PIECES[name] = (art, {"w": art.w, "h": art.h, "comment": comment, "doors": [list(d) for d in doors],
                          "passable": [list(c) for c in walk], "empty": empty, "tilesets": list(tilesets),
                          "over": [list(c) for c in over], "ground": ground})


ALL = lambda w, h: [(i, j) for j in range(h) for i in range(w)]

SECTIONS = [
    ("Route 2: the power line and the shore (orleans_route)",
     ["power_tower", "wire_span_l", "wire_span", "wire_span_r", "fallen_line", "fallen_line_b", "lookout"]),
    ("Rails and the mill (Route 4 orleans_river; Route 17 orleans_route_dry)", ["rail_v", "rail_h", "rail_car",
                                                                                 "chimney"]),
    ("Levee, channel and marsh (Routes 5-14)", ["levee_gate", "channel_buoy", "nav_beacon", "sunken_ruin",
                                               "scorched_cypress", "great_oak", "felled_log", "cut_stump"]),
    ("The Gulf and the drowned ruins (Routes 18-25, orleans_route_b; Route 24 orleans_route_dry)",
     ["sunken_ruin_l", "sunken_piling", "shipwreck", "oyster_bed", "bird_platform", "offshore_platform",
      "shrine_steps", "temple_gate", "mine_mouth"]),
]


def build_pieces():
    PIECES.clear()
    ALIASES.clear()
    add("power_tower", power_tower(), "Steel lattice transmission pylon, two crossarms with glass insulator strings, "
        "concrete footings, rust at the joints (2x4, blocking). The wires leave its top cell's sides 8 and 12 px down "
        "(wire_span_l / wire_span_r meet them).", "grass", [R])
    add("wire_span_l", wire("l"), "Overhead wires, the cell east of a tower: leaving the crossarms and sagging 2 px "
        "(1x1, walkable; drawn over the player).", "grass", [R], walk=[(0, 0)], over=[(0, 0)])
    add("wire_span", wire("m"), "Overhead wires mid-span, hanging level (1x1, walkable, over the player); repeat it "
        "between wire_span_l and wire_span_r.", "grass", [R], walk=[(0, 0)], over=[(0, 0)])
    add("wire_span_r", wire("r"), "Overhead wires, the cell west of a tower: rising to the crossarms (1x1, walkable, "
        "over the player; wire_span_l mirrored).", "grass", [R], walk=[(0, 0)], over=[(0, 0)])
    add("fallen_line", fallen_line("a"), "A snapped power cable lying on dry ground, its bare end sparking blue-white "
        "over a scorch (2x1, blocking).", "dry", [R])
    add("fallen_line_b", fallen_line("b"), "Fallen cable, second variant: a loose coil, a broken insulator, the "
        "sparking end west (2x1, blocking).", "dry", [R])
    add("lookout", lookout(), "Shore lookout: a board-and-batten hut on short stilts, a railed roof deck with a brass "
        "spyglass on a tripod, a ladder up the east side, a life ring; the door (shut) at the bottom centre with "
        "steps up to it (3x4, door (1,3)).", "grass", [R], doors=[(1, 3)])
    add("rail_v", rail_v(), "Railway track running north-south: two rails on timber ties every 8 px, no ballast "
        "(1x1, walkable, seamless along a run, any ground).", "grass", [RV], walk=[(0, 0)])
    add("rail_h", rail_h(), "Railway track running east-west (1x1, walkable, seamless, any ground).", "dry",
        [RD], walk=[(0, 0)])
    add("rail_car", rail_car(), "A sun-faded red boxcar standing on the east-west track; its bottom row carries the "
        "track (rail_h) under the wheels, so it drops into a rail_h run (3x2, blocking; the track row is y of the "
        "rail).", "dry", [RD])
    add("chimney", chimney(), "Tall brick sugar-mill chimney: corbelled crown, soot stain from the mouth, iron bands, "
        "stone plinth (1x5, blocking).", "dry", [RD])
    add("levee_gate", levee_gate(), "Levee gate: two heavy concrete posts, each with a red-and-white swing bar folded "
        "back (pointing north along the road), hinge, counterweight, hazard chevrons; the middle two columns are "
        "open road (4x2, columns 1-2 walkable and empty).", "grass", [RB], walk=[(1, 0), (2, 0), (1, 1), (2, 1)])
    add("channel_buoy", channel_buoy(), "Red-and-white channel buoy on water: striped float, little red tower, a lit "
        "lamp; lap line and ripples (1x2, blocking). Also the tournament float.", "water", [R, RB])
    add("nav_beacon", nav_beacon(), "Navigation beacon on stilts on water: braced timber piles, a railed platform, a "
        "post with a green lantern and a red day-mark, a ladder (2x3, blocking).", "water", [R])
    add("sunken_ruin", sunken_ruin(), "A broken carved Rootkin pillar standing in water: ragged break, spiral "
        "carvings, moss from the waterline (1x2, blocking).", "water", [R, RB])
    add("sunken_ruin_l", sunken_ruin_l(), "Larger ruin in water: a pillar stump and a toppled carved capital half-sunk "
        "at a tilt (2x2, blocking).", "water", [RB])
    add("sunken_piling", sunken_piling(), "Barnacled piling in water: an old round timber pile, cut top, a frayed "
        "rope, a crust of barnacles and weed (1x2, blocking). Route 20's pilings (placed as sunken_ruin today).",
        "water", [RB])
    add("shipwreck", shipwreck(), "Half-sunk wooden hull on water, listing: bow reared up west, stern under east, ribs "
        "showing through the stove-in planking, a broken leaning mast and yard, weed and foam at the waterline (4x3, "
        "blocking).", "water", [RB])
    add("oyster_bed", oyster_bed(), "A heap of oyster shells and stones: grey shells piled low, a few open showing "
        "nacre, wet at the foot (3x2, blocking). For the islets: on mud or sand.", "mud", [RB])
    add("scorched_cypress", scorched_cypress(), "Lightning-split bald cypress on marsh: two charred halves leaning "
        "apart, pale heartwood along the split, black snags, two live tufts, knees and roots (3x3, blocking).",
        "marsh", [R])
    add("great_oak", great_oak(), "The great live oak on marsh: a vast crown, a limb sweeping low to the ground each "
        "side, Spanish moss, a massive trunk, roots coiling like serpents (4x4, blocking).", "marsh", [R])
    add("felled_log", felled_log(), "Felled trunk on grass: furrowed bark, a sawn end with rings, a broken end, a "
        "branch stub, moss (3x1, blocking).", "grass", [R])
    add("cut_stump", cut_stump(), "A cut stump on grass, rings on its axe-cut top, a notch (1x1, blocking; the "
        "Kleavorite spot).", "grass", [R])
    add("bird_platform", bird_platform(), "Heron roost on water: a weathered plank platform on pilings, forked "
        "dead-branch perches, two stick nests, droppings (6x3, blocking).", "water", [RB])
    add("offshore_platform", offshore_platform(), "Abandoned offshore platform on water, 6x6 (the two stacked 6x3 "
        "rects the generator reserves, as one picture; or place offshore_platform_n over offshore_platform_s): a "
        "rusted steel deck with a railing (one stretch bent down), the snapped stub of the derrick in the middle, oil "
        "drums, rust stains; four great legs braced in an X (blocking).", "water", [RB])
    add("shrine_steps", shrine_steps(), "Worn stone steps rising out of the water to the shrine island between two "
        "carved cheek walls (6x3; the flight, columns 1-4, walkable; the walls block).", "water", [RB],
        walk=[(i, j) for j in range(3) for i in range(1, 5)])
    add("temple_gate", temple_gate(), "Half-flooded Rootkin temple doorway: stepped crest, a lintel of spirals, carved "
        "pillars, a corbelled doorway sealed by a slab with a faintly glowing spiral seal, steps down into the water "
        "(5x4, door (2,3) = the dive entrance).", "water", [RB], doors=[(2, 3)])
    add("mine_mouth", mine_mouth(), "Timbered mine tunnel mouth in a rock face: timber set, a second set deep in the "
        "dark, rusty rails running out, a lit lantern on a hook (3x3, door (1,2)).", "dry", [RD], doors=[(1, 2)])
    ALIASES["offshore_platform_n"] = ("offshore_platform", 0, 0, 6, 3,
                                      "Offshore platform, north half (6x3): place over offshore_platform_s.")
    ALIASES["offshore_platform_s"] = ("offshore_platform", 0, 3, 6, 3,
                                      "Offshore platform, south half (6x3): the legs in the water.")


# ================================================================ checks
def check_pieces():
    """Footprints against the spec; doors on the bottom row; GBA-exact colours; <= 15 per piece."""
    want = {"power_tower": (2, 4), "fallen_line": (2, 1), "fallen_line_b": (2, 1), "lookout": (3, 4),
            "rail_h": (1, 1), "rail_v": (1, 1), "rail_car": (3, 2), "chimney": (1, 5), "levee_gate": (4, 2),
            "channel_buoy": (1, 2), "nav_beacon": (2, 3), "sunken_ruin": (1, 2), "sunken_ruin_l": (2, 2),
            "shipwreck": (4, 3), "bird_platform": (6, 3), "offshore_platform": (6, 6), "shrine_steps": (6, 3),
            "temple_gate": (5, 4), "mine_mouth": (3, 3), "oyster_bed": (3, 2), "scorched_cypress": (3, 3),
            "great_oak": (4, 4), "felled_log": (3, 1), "cut_stump": (1, 1), "wire_span": (1, 1)}
    problems = []
    for name, (w, h) in want.items():
        m = PIECES[name][1]
        if (m["w"], m["h"]) != (w, h):
            problems.append(f"{name}: {m['w']}x{m['h']}, wanted {w}x{h}")
    for name, (art, m) in PIECES.items():
        cols = art.colours()
        if len(cols) > 15:
            problems.append(f"{name}: {len(cols)} colours")
        bad = [c for c in cols if any(v % 8 for v in c)]
        if bad:
            problems.append(f"{name}: colours not GBA-exact {bad[:3]}")
        for d in m["doors"]:
            if d[1] != m["h"] - 1:
                problems.append(f"{name}: door {d} not on the bottom row")
    # the rails must tile: their edges match the opposite edges
    for name, axis in (("rail_v", "v"), ("rail_h", "h")):
        px = PIECES[name][0].px
        ok = px[0] == px[15] if axis == "v" else all(row[0] == row[15] for row in px)
        if not ok:
            problems.append(f"{name}: does not tile along its run")
    return problems


# ================================================================ tiles
def tile_keys(art):
    """The piece's non-clear 8x8 tiles, each keyed by the least of its flips (h/v/hv flips are one tile)."""
    keys = set()
    for ty in range(0, art.H, 8):
        for tx in range(0, art.W, 8):
            t = tuple(tuple(art.px[ty + y][tx:tx + 8]) for y in range(8))
            if all(c == KEY for row in t for c in row):
                continue
            keys.add(min((t, tuple(r[::-1] for r in t), t[::-1], tuple(r[::-1] for r in t[::-1]))))
    return keys


def tile_census(order):
    """Per piece: (its unique tiles, how many are new in `order`); the total; per route tileset, the union."""
    seen, out, per_ts = set(), {}, {}
    for name in order:
        art, meta = PIECES[name]
        mine = tile_keys(art)
        out[name] = (len(mine), len(mine - seen))
        seen |= mine
        for ts in meta["tilesets"]:
            per_ts.setdefault(ts, set()).update(mine)
    return out, len(seen), {k: len(v) for k, v in per_ts.items()}


# ================================================================ the sheet and the index
def pack(width=16):
    order = sorted(PIECES, key=lambda n: (-PIECES[n][0].h, -PIECES[n][0].w, n))
    # shelf packing: each piece goes at the first place it fits
    used = set()
    place = {}
    for n in order:
        art = PIECES[n][0]
        y = 0
        while n not in place:
            for x in range(0, width - art.w + 1):
                cells = {(x + i, y + j) for j in range(art.h) for i in range(art.w)}
                if not cells & used:
                    place[n] = (x, y)
                    used |= cells
                    break
            y += 1
    rows = max(y for _, y in used) + 1
    sheet = Image.new("RGB", (width * 16, rows * 16), KEY)
    index = {}
    for n, (cx, cy) in place.items():
        art, meta = PIECES[n]
        sheet.paste(art.image(), (cx * 16, cy * 16))
        index[n] = dict({k: v for k, v in meta.items() if k != "ground"}, x=cx, y=cy)
    for n, (p, x0, y0, w, h, comment) in ALIASES.items():
        m = index[p]
        index[n] = {"w": w, "h": h, "comment": comment, "doors": [], "passable": [],
                    "empty": [[i, j] for i, j in ([e[0], e[1] - y0] for e in m["empty"]) if 0 <= j < h],
                    "tilesets": m["tilesets"], "over": [], "x": m["x"] + x0, "y": m["y"] + y0}
    return sheet, index


def prefab_rows(m, sheet):
    """The prefab rows for one indexed piece, exactly as redfield_tileset.piece_rows builds them for source SRC."""
    doors = {tuple(d) for d in m["doors"]}
    walk = {tuple(w) for w in m["passable"]}
    rows = []
    for j in range(m["h"]):
        row = []
        for i in range(m["w"]):
            cx, cy = m["x"] + i, m["y"] + j
            cell = sheet.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
            if all(p == KEY for p in _pixels(cell)):
                row.append(None)
                continue
            o = {"overlay": f"{SRC}:{cx}_{cy}"}
            if (i, j) in doors:
                o["behavior"] = DOOR
            if (i, j) in walk or (i, j) in doors:
                o["walk"] = True
            row.append(o)
        rows.append(row)
    return rows


def write_index(sheet, index, path):
    cells = sorted({(m["x"] + i, m["y"] + j) for m in index.values() for j in range(m["h"]) for i in range(m["w"])
                    if [i, j] not in m["empty"]}, key=lambda t: (t[1], t[0]))
    source = {"name": SRC, "type": "image", "image": "tools/mapgen/sources/orleans_custom/route_landmarks.png",
              "transparent": [list(KEY)], "overlay_only": True,
              "_comment": "Route landmarks (own art, make_route_landmarks.py), overlays on any ground.",
              "metatiles": [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]}
    prefabs = {}
    for n, m in index.items():
        d = m["doors"]
        prefabs[n] = {"_comment": m["comment"], "rows": prefab_rows(m, sheet),
                      "door": d[0] if len(d) == 1 else (d or None), "passable": m["passable"]}
    doc = {"_comment": "Route landmarks own art (make_route_landmarks.py, art_requests/route_landmarks.md): piece -> "
                       "sheet cell [x, y] and size w x h in 16 px cells; overlays, magenta = clear; doors and "
                       "passable are cells within the piece; empty = cells with nothing drawn; tilesets = the route "
                       "tilesets its routes use; over = cells best drawn over the player. 'source' + 'prefabs' are "
                       "the same pieces ready for a route recipe/config (source name 'lmk'), or feed 'pieces' to "
                       "redfield_tileset.add_pieces(r, c, 'lmk', 'route_landmarks.png', doc, ...).",
           "png": "route_landmarks.png", "pieces": index, "source": source, "prefabs": prefabs}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


# ================================================================ the review sheet
def place(field, name, cx, cy):
    over(field, PIECES[name][0].image(), cx * 16, cy * 16)


def patch_rail():
    """Route 17: a rail line on dry ground, two boxcars on it, the mill chimney beside it; Route 4: two tracks
    running north-south across grass."""
    f = ground("dry", 18, 7)
    for x in range(18):
        place(f, "rail_h", x, 5)
    place(f, "rail_car", 2, 4)
    place(f, "rail_car", 9, 4)
    place(f, "chimney", 15, 0)
    place(f, "mine_mouth", 0, 0)
    g = ground("grass", 6, 7)
    for y in range(7):
        place(g, "rail_v", 1, y)
        place(g, "rail_v", 3, y)
    out = Image.new("RGB", (f.width + g.width + 16, f.height), (34, 38, 42))
    out.paste(f, (0, 0))
    out.paste(g, (f.width + 16, 0))
    return out


def patch_power():
    """Route 2: three towers along a power line on grass, the wires between them, the dry patch below with the
    fallen lines, the lookout."""
    f = ground(lambda x, y: "dry" if y >= 6 and 4 <= x <= 16 else "grass", 34, 9)
    towers = (1, 13, 25)
    for t in towers:
        place(f, "power_tower", t, 1)
    for a, b in zip(towers, towers[1:]):
        xs = list(range(a + 2, b))
        for k, x in enumerate(xs):
            place(f, "wire_span_l" if k == 0 else "wire_span_r" if k == len(xs) - 1 else "wire_span", x, 1)
    place(f, "fallen_line", 5, 6)
    place(f, "fallen_line_b", 10, 7)
    place(f, "fallen_line", 13, 6)
    place(f, "lookout", 29, 5)
    return f


def patch_water():
    """The Gulf: the shipwreck, buoys, the beacon, the ruins and pilings on Ekat's water."""
    f = ground("water", 28, 9)
    place(f, "shipwreck", 1, 3)
    for x, y in ((7, 1), (11, 6), (20, 2), (25, 6)):
        place(f, "channel_buoy", x, y)
    place(f, "nav_beacon", 14, 1)
    place(f, "sunken_ruin", 18, 5)
    place(f, "sunken_ruin_l", 21, 4)
    for x in (7, 9):
        place(f, "sunken_piling", x, 4)
    return f


def review(path, census, total, per_ts, problems):
    S = 3
    W = 2200
    pos, y = [], 40
    for title, names in SECTIONS:
        pos.append(("title", title, 10, y))
        y += 22
        x, rowh = 10, 0
        for n in names:
            art, meta = PIECES[n]
            im = on_ground(art.image(), meta["ground"], 1)
            im = im.resize((im.width * S, im.height * S), Image.NEAREST)
            t, new = census[n]
            lab = f"{n} {art.w}x{art.h} on {meta['ground']}: {t} tiles ({new} new), {len(art.colours())} col"
            if meta["doors"]:
                lab += f", door {tuple(meta['doors'][0])}"
            wlab = max(im.width, 6 * len(lab))
            if x + wlab > W - 10:
                x, y, rowh = 10, y + rowh + 26, 0
            pos.append(("img", (lab, im), x, y))
            x += wlab + 24
            rowh = max(rowh, im.height)
        y += rowh + 36
    for title, im in (("Test patch: Route 17's rail line on dry ground, two boxcars, the mill chimney, the mine mouth; "
                       "Route 4's two tracks on grass", patch_rail()),
                      ("Test patch: Route 2's power line on grass (towers, wire_span_l / wire_span / wire_span_r), "
                       "fallen lines on a dry patch", patch_power()),
                      ("Test patch: the Gulf - shipwreck, channel buoys, the beacon, ruins and barnacled pilings on "
                       "Ekat's water", patch_water())):
        im = im.resize((im.width * S, im.height * S), Image.NEAREST)
        pos.append(("title", title, 10, y))
        y += 22
        pos.append(("img", ("", im), 10, y))
        y += im.height + 30
    lines = [f"Unique 8x8 tiles over all pieces (h/v flips free, clear tiles free): {total}"]
    for title, names in SECTIONS:
        lines.append(f"    {title}: {sum(census[n][1] for n in names)} new tiles")
    lines.append("Per route tileset (the pieces its routes use): " +
                 ", ".join(f"{k} {v}" for k, v in sorted(per_ts.items())))
    lines.append("Colours per piece <= 15, all GBA-exact (multiples of 8); ground under the pieces = real cells of "
                 "Ekat's swamp sheet (grass, marsh, water, mud) and the dry-country sheet (dry)." if not problems else
                 "PROBLEMS: " + "; ".join(problems))
    H = y + 18 * len(lines) + 20
    out = Image.new("RGB", (W, H), (34, 38, 42))
    d = ImageDraw.Draw(out)
    d.text((10, 10), "Route landmarks own art (make_route_landmarks.py): every piece at 3x on its intended ground "
                     "(one cell of ground round each)", fill=(240, 240, 240))
    for kind, v, x, yy in pos:
        if kind == "title":
            d.text((x, yy), v, fill=(250, 230, 160))
        else:
            lab, im = v
            out.paste(im, (x, yy))
            if lab:
                d.text((x, yy + im.height + 4), lab, fill=(220, 220, 210))
    for i, line in enumerate(lines):
        d.text((10, y + 18 * i), line, fill=(255, 255, 170) if i == 0 else (220, 220, 220))
    out.save(path)


def main():
    build_pieces()
    problems = check_pieces()
    order = [n for _, names in SECTIONS for n in names]
    missing = [n for n in PIECES if n not in order]
    order += missing
    census, total, per_ts = tile_census(order)
    sheet, index = pack()
    sheet.save(os.path.join(HERE, "route_landmarks.png"))
    write_index(sheet, index, os.path.join(HERE, "route_landmarks.json"))
    on_ground(sheet, "grass").resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(
        os.path.join(HERE, "route_landmarks_preview.png"))
    review(os.path.join(MAPGEN, "maps", "00_route_landmarks_art.png"), census, total, per_ts, problems)
    for n in order:
        art = PIECES[n][0]
        print(f"  {n:18s} {art.w}x{art.h}  {census[n][0]:3d} tiles {census[n][1]:3d} new  {len(art.colours()):2d} colours")
    print(f"route_landmarks.png {sheet.size}, {len(index)} pieces; {total} unique 8x8 tiles (flips free)")
    print("per tileset:", per_ts)
    for p in problems:
        print("  PROBLEM:", p)


if __name__ == "__main__":
    main()

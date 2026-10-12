"""Own art for Camp Cocodrie (gym 5, the swamp fishing camp): its boardwalk, its distinct buildings and the
props that make it a working camp. Everything is drawn here in Python (no source tiles), as overlays: magenta
is transparent, so each piece sits over whatever terrain the builder finds underneath (marsh, water, banks).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_camp_art.py
writes camp.png (16x16 cells), camp_preview.png (4x, on a swamp backdrop) and camp.json (the piece index that
tools/mapgen/camp_tileset.py turns into prefabs: name -> sheet cell, size, doors, walkable cells).

Colour families: every piece is drawn in one family of <= 15 colours that the tileset already has, so the
palette packer (compose.py "palette v2") doesn't have to squeeze anything:
    P4    the primary's packed-mud path colours (planks, posts, fence, fish, skiffs, lanterns)
    P1    the primary's red/white/grey set (the Nurse Cabin, trap-line floats)
    P3    the primary's blues (the Bait Shack: the Mart's blue tin roof)
    BARN  the Moomoo barn's set (rust tin, olive greys, reds, cream: cabin A, smokehouse, dance porch, pots,
          gators, the cookhouse chimney)
    SHADY the Shady Forest houses' set (mauve shakes, lit windows: cabin B)
    LEAF  swamp greens
    GARDEN the primary's flower-bed palette 0 (okra: its greens, grey-brown soil, yellow/wine flower)
Tiles in one piece may come from two families when they sit in different 8x8 rows (the buildings' stilts row
is cabin A's BARN tiles under a P1/P3 front): every 8x8 tile is still an exact subset of one palette.

Pieces (cells w x h; door = walk-in cell, walk = cells you can stand on):
    bw_<o>_<NSWE>[_v]  one boardwalk cell: o = h (boards run north-south, an east-west walk) or v; each side
                       o(pen) / c(losed: rim, side stringer or the front fascia on posts) / s(eam: the boards
                       change direction there); _1 = the second grain variation of a plain run cell
    cabin_a, cabin_b   stilt cabins 4x5 (rust tin + grey clapboard / cedar shakes + stained boards) on pilings,
                       steps down from the door; _m = mirrored (door on the right)
    nurse              the Nurse Cabin 5x5 (the camp's Pokemon Center): white boards, red tin, red-cross sign
    bait               the Bait Shack 5x5 (the camp's Mart): blue tin roof, BAIT signboard, cooler and rods
    smokehouse         4x5: cabin A's tin, tarred boards, louvred vent, stovepipe and smoke
    porch              the Dance Porch 7x5: cabin A's tin over an open porch on red posts, paper lanterns, steps
    chimney            1x2 stovepipe and smoke for the cookhouse roof
    pot                2x2 cast-iron gumbo pot over a fire
    woodpile 2x1, pen_h/_v/_nw/_ne/_sw/_se/_gate 1x1 (dual-grid: post mid-cell), gator/gator_b (mirror) 2x1, gator_eyes,
    okra/okra_b (opaque, tile both ways), fishrack/netrack 2x2, lantern, bollard, mooring_post (= bollard art), skiff 3x1,
    pirogue 2x1, trapline_h (tiles east-west), trapline_end, buoy
Tile economy (orleans_camp is demand-driven, 512 tiles): roofs repeat every 8 px down the slope (roof8), symmetric
fronts are drawn on the left and mirrored (flipped tiles are free), the stilts rows and the porch/smokehouse roofs
are cabin A's own tiles (cabin_stilts, pasted on the same 8 px phase).
"""
import json
import os
import random

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)

# ---------------------------------------------------------------- colour families
# P4: the primary's path set
NAVY, SLATE, GREY, PALE, WHITE4 = (64, 72, 104), (88, 88, 112), (120, 120, 128), (168, 184, 200), (216, 224, 232)
W_DD, W_D, W_M, W_L, W_HI = (104, 80, 64), (128, 104, 80), (152, 128, 96), (176, 152, 120), (216, 192, 136)
GOLD, GOLD_D, MINT = (232, 224, 136), (208, 184, 104), (184, 224, 160)
# P1: reds and whites
R_D, R_M, R_L, R_HI = (168, 32, 40), (200, 80, 72), (216, 104, 96), (232, 144, 112)
WH, WH_D, WH_DD, WH_S = (240, 240, 248), (200, 216, 232), (168, 184, 200), (144, 160, 176)
P1_WOOD, P1_WOOD_L, P1_GLOW, P1_GREEN = (152, 120, 96), (192, 168, 136), (248, 200, 136), (120, 160, 104)
# P3: blues
B_HI, B_L, B_M, B_D, B_PALE, B_SKY = (112, 184, 240), (96, 160, 216), (72, 128, 192), (48, 96, 160), (152, 208, 248), (200, 216, 232)
OCHRE = (200, 176, 104)
# BARN
OL_DD, OL_D, OL_M, OL_L = (72, 72, 56), (88, 96, 72), (128, 128, 104), (160, 160, 144)
TAR = (72, 64, 56)
RU_L, RU, RU_D, RU_HI = (232, 152, 88), (184, 104, 56), (152, 80, 32), (208, 144, 112)
BR, BR_D, CREAM = (184, 80, 80), (128, 56, 64), (240, 216, 152)
STEEL, STEEL_D = (128, 128, 136), (120, 120, 128)
# SHADY
SH_L, SH_M, SH_D, SH_DD = (128, 88, 104), (104, 72, 80), (88, 72, 80), (64, 48, 56)
SH_OUT, SH_OUT2 = (32, 40, 64), (48, 56, 88)
SH_TRIM, SH_WOOD, SH_WOOD_D = (208, 184, 144), (160, 136, 112), (128, 104, 104)
SH_GLOW, SH_GLOW_D, SH_GLOW_L = (248, 232, 128), (232, 176, 112), (248, 248, 216)
SH_GREY = (112, 112, 120)
# LEAF: swamp greens (the terrain's own), a pale okra flower with a wine centre
LF_DD, LF_D, LF_M, LF_L, LF_HI = (40, 56, 40), (64, 96, 64), (96, 128, 88), (104, 152, 120), (136, 176, 128)
POD, FLOWER, WINE = (120, 160, 104), (232, 224, 136), (128, 56, 64)
# MUD: the mud bank's own palette (secondary palette 11: the mud browns plus the swamp greens), for the okra beds:
# tilled soil in the same browns as the gator pen's mud flat, okra in the swamp greens, the palest tan for the flower
MU_HI, MU_L, MU_M, MU_D, MU_DD = (160, 144, 120), (160, 128, 120), (144, 104, 96), (112, 80, 80), (96, 64, 64)
MU_T, MU_G, MU_K = (136, 120, 104), (104, 96, 88), (48, 48, 40)
MG_DD, MG_D, MG_O, MG_M, MG_T, MG_L, MG_HI = (40, 56, 40), (64, 96, 64), (72, 96, 64), (96, 128, 88), (80, 112, 96), \
    (104, 152, 120), (120, 160, 104)
# GARDEN: the primary's flower-bed palette (primary palette 0): its greens, a grey-brown tilled soil, and the okra
# flower in its own colours (pale yellow petals, a wine-red eye)
GD_DD, GD_M, GD_G, GD_L = (40, 56, 40), (104, 144, 96), (120, 160, 104), (136, 176, 128)
GD_SOIL, GD_SOIL_D, GD_YEL, GD_WH, GD_RED = (112, 96, 96), (88, 80, 64), (248, 192, 112), (232, 240, 240), (192, 48, 64)


class Art:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w * 16, h * 16), KEY)
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < self.w * 16 and 0 <= y < self.h * 16 and c is not None:
            self.px[x, y] = c

    def get(self, x, y):
        return self.px[x, y]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def frame(self, x0, y0, x1, y1, c):
        self.hline(x0, x1, y0, c)
        self.hline(x0, x1, y1, c)
        self.vline(x0, y0, y1, c)
        self.vline(x1, y0, y1, c)

    def clear(self, x0, y0, x1, y1):
        self.rect(x0, y0, x1, y1, KEY)

    def mirrored(self):
        out = Art(self.w, self.h)
        out.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        out.px = out.im.load()
        return out

    def sprite(self, x0, y0, rows, pal):
        """Hand-placed pixels: one string per row, '.' or ' ' transparent (left alone), other chars via pal."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in ". ":
                    self.put(x0 + i, y0 + j, pal[ch])

    def ellipse(self, cx, cy, rx, ry, c, x0=None, x1=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0 and (x0 is None or x0 <= x <= x1):
                    self.put(x, y, c)

    def opaque(self, x, y):
        return 0 <= x < self.w * 16 and 0 <= y < self.h * 16 and self.px[x, y] != KEY

    def outline(self, c, region=None, skip=()):
        """A 1 px outline round everything drawn (4-neighbours), only on transparent pixels; `skip`: colours that
        don't get outlined (smoke, ripples)."""
        x0, y0, x1, y1 = region or (0, 0, self.w * 16 - 1, self.h * 16 - 1)
        add = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.px[x, y] != KEY:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.opaque(x + dx, y + dy) and self.px[x + dx, y + dy] not in skip and \
                            x0 <= x + dx <= x1 and y0 <= y + dy <= y1:
                        add.append((x, y))
                        break
        for x, y in add:
            self.px[x, y] = c

    def mirror_left(self, y0=0, y1=None):
        """Make rows y0..y1 left-right symmetric: the right half becomes the mirror of the left half (the width is
        a whole number of 8 px tiles each side, so the right half's tiles are flipped copies and cost nothing)."""
        W = self.w * 16
        y1 = self.h * 16 - 1 if y1 is None else y1
        for y in range(y0, y1 + 1):
            for x in range(W // 2):
                self.px[W - 1 - x, y] = self.px[x, y]


PIECES = {}  # name -> (Art, meta)


def add(name, art, comment, doors=(), walk=(), empty=()):
    PIECES[name] = (art, {"w": art.w, "h": art.h, "comment": comment, "doors": [list(d) for d in doors],
                          "passable": [list(c) for c in walk], "empty": [list(c) for c in empty]})


# ================================================================ the boardwalk
def board_cell(orient, sides, var=0):
    """One 16x16 boardwalk cell. Boards are 8 px wide (two per cell); `var` swaps the grain flecks so long runs
    don't repeat every cell. The front (south) side is a fascia beam on posts, so the deck reads as raised over
    the swamp; the far (north) side a dark rim; the sides a stringer; a seam is where the boards turn."""
    a = Art(1, 1)
    rng = random.Random(f"{orient}{var}")
    N, S, Wd, E = sides
    deck_bottom = 11 if S == "c" else 15
    for y in range(16):
        for x in range(16):
            if y > deck_bottom:
                continue
            u = x if orient == "h" else y     # across the boards
            k = u % 8
            c = W_DD if k == 0 else W_L if k == 1 else W_M if k < 6 else W_D
            a.put(x, y, c)
    # grain flecks along each board, and nails over the joists
    for b in range(2):
        for _ in range(2):
            along = rng.randrange(1, 13)
            across = b * 8 + rng.choice((3, 4))
            ln = rng.choice((2, 3))
            for t in range(ln):
                x, y = (across, along + t) if orient == "h" else (along + t, across)
                if y <= deck_bottom and a.get(x, y) == W_M:
                    a.put(x, y, W_D)
        for along in (3, 12):
            for across in (b * 8 + 2, b * 8 + 5):
                x, y = (across, along) if orient == "h" else (along, across)
                if y <= deck_bottom:
                    a.put(x, y, W_DD)
    # light catching the tops of a few boards
    for b in range(2):
        along = rng.randrange(0, 10)
        for t in range(3):
            x, y = (b * 8 + 2, along + t) if orient == "h" else (along + t, b * 8 + 2)
            if y <= deck_bottom and a.get(x, y) == W_M:
                a.put(x, y, W_HI)
    if N == "c":
        a.hline(0, 15, 0, NAVY)
        a.hline(0, 15, 1, W_DD)
    elif N == "s":
        a.hline(0, 15, 0, W_DD)
    if Wd == "c":
        a.vline(0, 0, deck_bottom, NAVY)
        a.vline(1, 1 if N == "c" else 0, deck_bottom, W_HI)
    elif Wd == "s":
        a.vline(0, 0, deck_bottom, W_DD)
    if E == "c":
        a.vline(15, 0, deck_bottom, NAVY)
        a.vline(14, 1 if N == "c" else 0, deck_bottom, W_DD)
    elif E == "s":
        a.vline(15, 0, deck_bottom, W_DD)
    if S == "c":  # the front fascia beam, posts standing in the water/marsh below it
        a.hline(0, 15, 11, W_DD)
        a.hline(0, 15, 12, W_M)
        a.hline(0, 15, 13, W_D)
        a.hline(0, 15, 14, NAVY)
        x0 = 1 if Wd == "c" else 0
        x1 = 14 if E == "c" else 15
        for x in range(16):
            if not x0 <= x <= x1:
                a.put(x, 11, NAVY if x in (0, 15) else None)
        posts = [p for p in (3, 11) if x0 <= p <= x1 - 1]
        if Wd == "c":
            posts = [1] + [p for p in posts if p > 4]
        if E == "c":
            posts = [p for p in posts if p < 11] + [13]
        for p in posts:
            a.rect(p, 14, p + 1, 15, W_D)
            a.put(p + 1, 15, W_DD)
            a.put(p, 14, W_M)
        if Wd == "c":
            a.vline(0, 11, 14, NAVY)
        if E == "c":
            a.vline(15, 11, 14, NAVY)
    if S == "s":
        a.hline(0, 15, 15, W_DD)
    return a


def boardwalk():
    combos = []
    for orient in "hv":
        for N in "ocs":
            for S in "ocs":
                for Wd in "ocs":
                    for E in "ocs":
                        combos.append((orient, N + S + Wd + E))
    for orient, sides in combos:
        add(f"bw_{orient}_{sides}", board_cell(orient, sides), "Camp boardwalk cell (walkable).", walk=[(0, 0)])
        if (orient == "h" and sides[2:] == "oo") or (orient == "v" and sides[:2] == "oo"):
            add(f"bw_{orient}_{sides}_1", board_cell(orient, sides, 1), "Camp boardwalk cell, second grain.",
                walk=[(0, 0)])


# ================================================================ shared building parts
def tin_roof(a, x0, y0, x1, y1, dark, mid, light, hi, cap, cap_d, out, rust=None, rust_d=None, seed=0, pitch=4,
             blobs=3):
    """A corrugated tin roof seen from above the eave: vertical ribs, nail lines, a capped ridge, a dark eave
    line; `rust` patches with drips (galvanised tin gone to rust round the nails)."""
    rng = random.Random(seed)
    for y in range(y0, y1 + 1):
        low = y > y0 + (y1 - y0) * 0.7
        for x in range(x0, x1 + 1):
            k = (x - x0) % pitch
            c = dark if k == 0 else light if k == 1 else mid
            if low and k == 1 and y % 2:
                c = mid  # the roof turns away from the light toward the eave
            a.put(x, y, c)
    for y in range(y0 + 3, y0 + 6):  # sunlit band under the ridge
        for x in range(x0, x1 + 1):
            if (x - x0) % pitch == 1:
                a.put(x, y, hi)
    for ny in range(y0 + 9, y1 - 3, 12):  # nail lines
        for x in range(x0 + 2, x1, 8):
            a.put(x, ny, dark)
    if rust:
        # rust: streaks running down from the nail lines, wider at the top, and a ragged band along the eave
        for _ in range(blobs):
            cx = rng.randrange(x0 + 4, x1 - 6)
            cy = rng.randrange(y0 + 8, y1 - 16)
            ln = rng.randrange(7, 14)
            w = rng.choice((3, 4, 5))
            for t in range(ln):
                half = max(0, round((w / 2) * (1 - t / ln) + rng.uniform(-0.6, 0.6)))
                for x in range(cx - half, cx + half + 1):
                    k = (x - x0) % pitch
                    a.put(x, cy + t, rust_d if k == 0 and rust_d else rust)
        for x in range(x0 + 1, x1):
            h = 1 + (rng.random() < 0.5) + (rng.random() < 0.25) + ((x * 7) % 11 == 0) * 2
            for t in range(h):
                k = (x - x0) % pitch
                a.put(x, y1 - 2 - t, rust_d if k == 0 and rust_d else rust)
    a.hline(x0, x1, y0, out)
    a.hline(x0 + 1, x1 - 1, y0 + 1, cap)
    a.hline(x0 + 1, x1 - 1, y0 + 2, cap_d)
    a.hline(x0, x1, y1, out)
    a.hline(x0 + 1, x1 - 1, y1 - 1, dark)
    a.vline(x0, y0, y1, out)
    a.vline(x1, y0, y1, out)


def clapboard(a, x0, y0, x1, y1, light, mid, lap, out=None, lap_h=4):
    for y in range(y0, y1 + 1):
        k = (y - y0) % lap_h
        for x in range(x0, x1 + 1):
            a.put(x, y, lap if k == 0 else light if k == 1 else mid)


def window(a, x0, y0, w, h, frame_c, glass, glow, glow_l, out, sill=None):
    """A window with a cross mullion and warm light inside."""
    a.rect(x0, y0, x0 + w - 1, y0 + h - 1, out)
    a.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2, frame_c)
    a.rect(x0 + 2, y0 + 2, x0 + w - 3, y0 + h - 3, glow)
    mx, my = x0 + w // 2, y0 + h // 2
    a.vline(mx, y0 + 2, y0 + h - 3, frame_c)
    a.hline(x0 + 2, x0 + w - 3, my, frame_c)
    a.put(x0 + 2, y0 + 2, glow_l)
    a.put(x0 + 3, y0 + 2, glow_l)
    a.put(mx + 1, y0 + 2, glow_l)
    a.rect(x0 + 2, my + 1, mx - 1, y0 + h - 3, glass)
    a.rect(mx + 1, my + 1, x0 + w - 3, y0 + h - 3, glass)
    if sill:
        a.hline(x0, x0 + w - 1, y0 + h, sill)


def stilts(a, y0, x0, x1, door_x, piles, pile, pile_l, pile_d, beam, beam_l, under, out, tread, tread_d, riser):
    """The floor beam, the dark crawl space and pilings standing in the water or marsh, cross-braced; steps down
    from the door (cell column starting at door_x). Between the pilings the terrain shows through (transparent),
    so the cabin stands over whatever is beneath."""
    a.hline(x0, x1, y0, out)
    a.hline(x0 + 1, x1 - 1, y0 + 1, beam_l)
    a.hline(x0 + 1, x1 - 1, y0 + 2, beam)
    a.hline(x0, x1, y0 + 3, out)
    a.rect(x0 + 1, y0 + 4, x1 - 1, y0 + 6, under)
    for x in range(x0 + 1, x1, 2):
        a.put(x + (1 if x % 4 == 1 else 0), y0 + 7, under)
    sx0, sx1 = door_x + 2, door_x + 13
    for i, p in enumerate(piles):
        a.rect(p, y0 + 4, p + 2, y0 + 15, pile)
        a.vline(p, y0 + 4, y0 + 14, pile_l)
        a.vline(p + 2, y0 + 4, y0 + 15, pile_d)
        a.vline(p - 1, y0 + 4, y0 + 15, out)
        a.vline(p + 3, y0 + 4, y0 + 15, out)
        a.hline(p, p + 2, y0 + 15, pile_d)
    ps = sorted(piles)
    for pa, pb in zip(ps, ps[1:]):  # an X brace between neighbouring pilings, unless the steps are between them
        if pa < sx0 < pb or pa < sx1 < pb:
            continue
        span = pb - pa - 4
        for t in range(span + 1):
            x = pa + 4 + t
            ya = y0 + 6 + round(t * 6 / max(1, span))
            yb = y0 + 12 - round(t * 6 / max(1, span))
            a.put(x, ya, pile_d)
            a.put(x, yb, pile_d)
    # steps down from the door, between two stringers
    a.vline(sx0 - 1, y0, y0 + 15, out)
    a.vline(sx1 + 1, y0, y0 + 15, out)
    a.vline(sx0, y0 + 1, y0 + 15, riser)
    a.vline(sx1, y0 + 1, y0 + 15, riser)
    for i, y in enumerate(range(y0 + 1, y0 + 16, 5)):
        a.hline(sx0 + 1, sx1 - 1, y, tread_d)
        a.rect(sx0 + 1, y + 1, sx1 - 1, y + 2, tread)
        a.rect(sx0 + 1, y + 3, sx1 - 1, min(y + 4, y0 + 15), riser)


# ================================================================ stilt cabins
def cabin_a():
    """Stilt cabin A: rust-streaked corrugated tin roof, weathered grey-green clapboard, olive shutters, lit window,
    plank door; on pilings with steps down. BARN family."""
    a = Art(4, 5)
    tin_roof(a, 0, 1, 63, 45, STEEL_D, STEEL, OL_L, CREAM, OL_L, OL_M, NAVY, rust=RU, rust_d=RU_D, seed=11)
    a.hline(1, 62, 46, TAR)            # shadow under the eave
    a.hline(2, 61, 47, OL_D)
    clapboard(a, 2, 48, 61, 63, OL_L, OL_M, OL_D)
    a.vline(1, 46, 63, NAVY)
    a.vline(62, 46, 63, NAVY)
    a.vline(2, 48, 63, CREAM)          # corner boards
    a.vline(61, 48, 63, OL_D)
    # door (cell column 1)
    a.rect(18, 48, 29, 63, NAVY)
    a.rect(19, 49, 28, 63, RU_D)
    for x in (21, 24, 27):
        a.vline(x, 50, 63, BR_D)
    a.rect(19, 49, 28, 49, CREAM)
    a.put(26, 56, CREAM)
    a.put(26, 57, OL_L)
    # window and shutters (columns 2-3)
    window(a, 37, 50, 16, 11, CREAM, RU_L, CREAM, CREAM, NAVY, sill=OL_D)
    for sx in (33, 54):
        a.rect(sx, 50, sx + 2, 60, OL_D)
        a.vline(sx + 1, 51, 59, OL_DD)
        a.frame(sx - 1, 49, sx + 3, 61, NAVY)
    # a lantern hook by the door, a horseshoe over it
    a.put(32, 52, OL_DD)
    a.rect(31, 53, 33, 55, RU_L)
    a.put(32, 54, CREAM)
    a.hline(22, 25, 47, OL_M)
    stilts(a, 64, 1, 62, 16, (4, 38, 57), OL_M, OL_L, OL_D, TAR, OL_D, OL_DD, NAVY, OL_L, CREAM, OL_D)
    return a


def cabin_b():
    """Stilt cabin B: cedar-shake roof with a stovepipe, stained board walls, two lit windows. SHADY family."""
    a = Art(4, 5)
    # shakes: staggered rows of 4 px shingles, darker toward the eave
    for y in range(1, 46):
        row = (y - 1) // 5
        for x in range(0, 64):
            k = (x + (row % 2) * 3) % 6
            c = SH_L if y < 14 else SH_M
            if k == 0:
                c = SH_DD
            elif (y - 1) % 5 == 4:
                c = SH_D
            elif k == 1 and y < 30:
                c = SH_L
            a.put(x, y, c)
    a.hline(0, 63, 0, SH_OUT)
    a.hline(0, 63, 1, SH_WOOD)          # ridge board
    a.hline(0, 63, 2, SH_WOOD_D)
    a.hline(0, 63, 45, SH_OUT)
    a.vline(0, 0, 45, SH_OUT)
    a.vline(63, 0, 45, SH_OUT)
    # stovepipe with a cap (right of centre)
    a.rect(44, 0, 48, 12, SH_OUT)
    a.rect(45, 2, 47, 12, SH_GREY)
    a.vline(45, 2, 12, (128, 128, 136))
    a.rect(43, 0, 49, 1, SH_OUT)
    a.hline(44, 48, 1, (128, 128, 136))
    a.hline(44, 48, 13, SH_DD)
    a.hline(1, 62, 46, SH_DD)
    a.hline(2, 61, 47, SH_OUT2)
    clapboard(a, 2, 48, 61, 63, SH_WOOD, SH_WOOD_D, SH_D)
    a.vline(1, 46, 63, SH_OUT)
    a.vline(62, 46, 63, SH_OUT)
    a.vline(2, 48, 63, SH_TRIM)
    a.vline(61, 48, 63, SH_D)
    # door column 1, windows in columns 0 and 2-3
    a.rect(18, 48, 29, 63, SH_OUT)
    a.rect(19, 49, 28, 63, SH_M)
    a.rect(20, 50, 27, 55, SH_GLOW_D)
    a.vline(23, 50, 55, SH_M)
    a.hline(20, 27, 52, SH_M)
    a.rect(19, 49, 28, 49, SH_TRIM)
    a.put(26, 58, SH_GLOW)
    window(a, 5, 50, 10, 10, SH_TRIM, SH_GLOW_D, SH_GLOW, SH_GLOW_L, SH_OUT, sill=SH_D)
    window(a, 38, 50, 16, 10, SH_TRIM, SH_GLOW_D, SH_GLOW, SH_GLOW_L, SH_OUT, sill=SH_D)
    # a flower box under the big window
    a.rect(38, 61, 53, 63, SH_D)
    for x in range(39, 53, 3):
        a.put(x, 60, SH_GLOW)
    stilts(a, 64, 1, 62, 16, (4, 38, 57), SH_D, SH_WOOD_D, SH_DD, SH_DD, SH_D, SH_OUT2, SH_OUT, SH_WOOD, SH_TRIM, SH_D)
    return a


# ================================================================ the camp's own buildings
# Cheap in tiles by construction: the roofs repeat every 8 px down the slope (roof8) and are mirrored about the
# middle (flipped tiles are free), the stilts row is cabin A's (same pilings, braces and steps on the same 8 px
# phase, so the tiles are cabin A's own), symmetric fronts are drawn on the left and mirrored.
def roof8(a, x0, y0, x1, y1, dark, mid, light, hi, cap, cap_d, out, pitch=4):
    """A corrugated tin roof like tin_roof, but its body repeats every 8 px down the slope (one nail line per 8 px
    row) so a roof costs four rows of tiles whatever its depth: ridge, body, the shaded lower slope, the eave."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = (x - x0) % pitch
            c = dark if k == 0 else light if k == 1 else mid
            if y >= y1 - 12 and k == 1 and y % 2:
                c = mid
            a.put(x, y, c)
    for y in range(y0 + 3, y0 + 6):
        for x in range(x0, x1 + 1):
            if (x - x0) % pitch == 1:
                a.put(x, y, hi)
    for y in range(y0 + 10, y1 - 12, 8):
        for x in range(x0 + 2, x1, 8):
            a.put(x, y, dark)
    a.hline(x0, x1, y0, out)
    a.hline(x0 + 1, x1 - 1, y0 + 1, cap)
    a.hline(x0 + 1, x1 - 1, y0 + 2, cap_d)
    a.hline(x0, x1, y1, out)
    a.hline(x0 + 1, x1 - 1, y1 - 1, dark)
    a.vline(x0, y0, y1, out)
    a.vline(x1, y0, y1, out)


_CABIN_A = []


def cabin_stilts(a, cols, y0=64):
    """Cabin A's stilts row copied 8 px column by 8 px column (cols: which of its eight columns, 0 = the west end
    and piling, 1 = plain beam, 2/3 = the steps, 4/5 = the middle piling and the brace's start, 6 = brace, 7 = the
    last piling and the east end): every tile is one of cabin A's, so the row costs nothing."""
    if not _CABIN_A:
        _CABIN_A.append(cabin_a())
    src = _CABIN_A[0].im
    for i, c in enumerate(cols):
        a.im.paste(src.crop((c * 8, 64, c * 8 + 8, 80)), (i * 8, y0))


def mirror_span(a, x0, x1, y0, y1):
    """Mirror the left half of the span x0..x1 onto its right half (a door drawn once, symmetric)."""
    for y in range(y0, y1 + 1):
        for i in range((x1 - x0 + 1) // 2):
            a.px[x1 - i, y] = a.px[x0 + i, y]


def nurse():
    """The Nurse Cabin (the camp's Pokemon Center), 5x5: red tin roof with a big red-cross sign over the door,
    white clapboard, glass double door, lit windows with flower boxes, a lantern each side of the door; on cabin
    A's stilts with steps down the middle. P1 (the stilts row: BARN, cabin A's tiles). Symmetric."""
    a = Art(5, 5)
    roof8(a, 0, 1, 79, 45, R_D, R_M, R_L, R_HI, R_HI, R_L, NAVY)
    # the sign: a white board on the roof over the door, red cross
    a.rect(30, 24, 39, 38, NAVY)
    a.rect(31, 25, 39, 37, WH)
    a.hline(31, 39, 36, WH_D)
    a.hline(31, 39, 37, WH_DD)
    a.vline(31, 25, 35, WH)
    a.rect(38, 27, 39, 35, R_M)          # the cross (mirrored: 4 wide, 12 across)
    a.rect(33, 29, 39, 32, R_M)
    a.hline(33, 37, 29, R_HI)
    a.put(38, 27, R_HI)
    a.put(39, 27, R_HI)
    a.hline(33, 37, 32, R_D)
    a.hline(38, 39, 35, R_D)
    a.vline(33, 29, 32, R_L)
    a.hline(31, 39, 39, R_D)             # its shadow on the tin
    # walls
    a.hline(1, 78, 46, SLATE)
    a.hline(2, 77, 47, WH_S)
    clapboard(a, 2, 48, 77, 63, WH, WH_D, WH_DD)
    a.vline(1, 46, 63, NAVY)
    a.vline(2, 48, 63, WH)
    # glass double door (the two leaves meet on the mirror line)
    a.rect(32, 48, 39, 63, NAVY)
    a.rect(33, 49, 39, 63, R_M)
    a.vline(33, 49, 63, R_L)
    a.hline(33, 39, 49, R_HI)
    a.rect(35, 50, 38, 62, P1_GLOW)
    a.rect(35, 59, 38, 62, R_HI)
    a.put(35, 50, WH)
    a.put(36, 50, WH)
    a.put(35, 51, WH)
    a.vline(39, 49, 63, NAVY)
    a.hline(34, 39, 63, WH_S)
    # a lit window with a flower box
    window(a, 9, 50, 14, 9, WH, R_HI, P1_GLOW, WH, NAVY)
    a.rect(9, 59, 22, 61, NAVY)
    a.rect(10, 60, 21, 61, P1_WOOD)
    a.hline(10, 21, 60, P1_WOOD_L)
    for x in range(10, 22, 2):
        a.put(x, 59, P1_GREEN)
    for x in (11, 15, 19):
        a.put(x, 58, R_M)
        a.put(x + 1, 59, R_L)
    # a lantern by the door
    a.sprite(26, 48, ["..N.", ".NN.", "NGGN", "NWGN", "NGGN", ".NN."],
             {"N": NAVY, "G": P1_GLOW, "W": WH})
    cabin_stilts(a, (0, 1, 4, 5, 2))
    a.mirror_left()
    return a


LETTERS = {"B": ["XX.", "X.X", "XX.", "X.X", "XX."], "A": [".X.", "X.X", "XXX", "X.X", "X.X"],
           "I": ["XXX", ".X.", ".X.", ".X.", "XXX"], "T": ["XXX", ".X.", ".X.", ".X.", ".X."]}


def bait():
    """The Bait Shack (the camp's Mart), 5x5: blue tin roof with a hand-lettered BAIT board, weathered grey
    boards, a blue screen door, a counter window under a striped awning (jars on the shelf), a cooler out front,
    rods leaning by the window and a landing net on the wall; cabin A's stilts. P3."""
    a = Art(5, 5)
    roof8(a, 0, 1, 79, 45, B_D, B_M, B_L, B_HI, B_PALE, B_L, NAVY)
    a.mirror_left(0, 45)
    # the BAIT board over the counter
    a.rect(40, 32, 63, 39, NAVY)
    a.rect(41, 33, 62, 38, OCHRE)
    a.hline(41, 62, 33, WH_D)
    x = 44
    for ch in "BAIT":
        a.sprite(x, 34, LETTERS[ch], {"X": B_D})
        x += 5
    a.put(46, 34, B_D)                   # hand-lettered: a little wobble
    # walls
    a.hline(1, 78, 46, SLATE)
    a.hline(2, 77, 47, GREY)
    clapboard(a, 2, 48, 77, 63, WH_DD, WH_S, GREY)
    a.vline(1, 46, 63, NAVY)
    a.vline(78, 46, 63, NAVY)
    a.vline(2, 48, 63, WH_D)
    a.vline(77, 48, 63, SLATE)
    # screen door (column 1)
    a.rect(18, 48, 29, 63, NAVY)
    a.rect(19, 49, 28, 63, B_L)
    a.vline(19, 49, 63, B_HI)
    a.rect(21, 50, 26, 55, SLATE)
    a.rect(21, 58, 26, 62, SLATE)
    for y in range(50, 63):
        for xx in range(21, 27):
            if a.get(xx, y) == SLATE and (xx + y) % 2 == 0:
                a.put(xx, y, NAVY)
    mirror_span(a, 18, 29, 48, 63)
    a.put(27, 57, WH)
    # the counter window (columns 2.5-4.5), striped awning over it
    a.rect(40, 51, 71, 62, NAVY)
    for y in range(48, 51):
        for xx in range(40, 72):
            a.put(xx, y, B_M if (xx // 4) % 2 == 0 else WH)
    for xx in range(40, 72):
        a.put(xx, 48, B_D if (xx // 4) % 2 == 0 else WH_D)
        if xx % 4 in (1, 2):
            a.put(xx, 51, B_M if (xx // 4) % 2 == 0 else WH)
    a.vline(40, 48, 51, NAVY)
    a.vline(71, 48, 51, NAVY)
    a.rect(41, 52, 70, 58, NAVY)
    a.hline(41, 70, 56, SLATE)          # a shelf of bait jars
    for xx in range(42, 70, 4):
        a.sprite(xx, 53, ["P.", "HB", "BB"], {"P": B_PALE, "H": B_HI, "B": B_L})
    a.rect(41, 57, 70, 58, SLATE)
    a.hline(40, 71, 59, OCHRE)          # the counter
    a.hline(40, 71, 60, WH_S)
    a.hline(40, 71, 61, GREY)
    a.hline(40, 71, 62, NAVY)
    # a landing net on the wall by the door
    a.sprite(32, 48, [".NNN.", "NGSGN", "NSGSN", "NGSGN", ".NNN.", "..O..", "..O..", "..O..", "..O.."],
             {"N": NAVY, "G": GREY, "S": SLATE, "O": OCHRE})
    # rods leaning by the window
    for i, top in enumerate((48, 50)):
        x0 = 72 + i * 2
        for y in range(top, 63):
            a.put(x0 + (y - top) // 6, y, OCHRE)
        a.put(x0, top, NAVY)
        a.put(x0 + (60 - top) // 6, 58, B_D)  # reel
    # the cooler out front
    a.sprite(3, 54, [".NNNNNNNNN.", "NBHHHHHHHBN", "NBBBNNNBBBN", "NNNNNNNNNNN", "NWWWWWWWWDN", "NWWWWWWWWDN",
                     "NWDDDDDDDDN", "NNNNNNNNNNN"], {"N": NAVY, "B": B_L, "H": B_HI, "W": WH, "D": WH_D})
    cabin_stilts(a, (0, 1, 2, 3, 1, 1, 4, 5, 6, 7))
    return a


def smokehouse():
    """The smokehouse, 4x5: cabin A's rusty tin roof (mirrored, so its tiles are free) with a stovepipe and smoke
    rising off it, tarred board-and-batten walls, a wide strapped plank door, a louvred vent; cabin A's stilts.
    BARN."""
    a = Art(4, 5)
    a.im.paste(cabin_a().mirrored().im.crop((0, 0, 64, 48)), (0, 0))
    # stovepipe mid-roof, smoke rising off it and drifting east
    a.sprite(40, 16, ["NNNNNNNN", "NLLSSSDN", "NNNNNNNN", ".NLSSDN.", ".NLSSDN.", ".NLSSDN.", ".NLSSDN.",
                      ".NLSSDN.", "NNNNNNNN", "NDDDDDDN", "NNNNNNNN"],
             {"N": NAVY, "L": OL_L, "S": STEEL, "D": STEEL_D})
    a.sprite(40, 0, ["......MMMM......", "....MMCCCCMM....", "...MCCCCCCCLM...", "...MCCCCCCLLM...",
                     "....MLCCLLMM....", ".....MMMMM......", "...MMCCM........", "..MCCCCLM.......",
                     "..MCCCLLM.......", "...MLLMM........", "...MCLM.........", "..MCLM..........",
                     "..MLM...........", "...M............"], {"L": OL_L, "C": CREAM, "M": OL_M})
    # tarred board-and-batten walls (under cabin A's eave line, rows 46-47 kept)
    for y in range(48, 64):
        for x in range(2, 62):
            k = x % 8
            c = OL_DD if k == 0 else OL_D if k == 1 else TAR
            if k == 5 and y % 8 == 3:
                c = OL_DD
            a.put(x, y, c)
    a.vline(2, 48, 63, OL_M)
    a.vline(61, 48, 63, OL_DD)
    # a wide strapped plank door (column 1, symmetric)
    a.rect(16, 48, 31, 63, NAVY)
    a.rect(17, 49, 30, 63, OL_M)
    for x in (20, 23):
        a.vline(x, 48, 63, OL_D)
    a.vline(17, 48, 63, OL_L)
    for y in (51, 59):
        a.hline(17, 23, y, STEEL)
        a.hline(17, 23, y + 1, NAVY)
        a.put(19, y, OL_L)
    mirror_span(a, 16, 31, 48, 63)
    a.vline(23, 48, 63, NAVY)
    a.vline(24, 48, 63, NAVY)
    # louvred vent
    a.rect(40, 50, 55, 59, NAVY)
    for y in range(51, 59):
        k = (y - 51) % 3
        a.hline(41, 54, y, OL_L if k == 0 else OL_M if k == 1 else TAR)
    a.hline(41, 54, 49, OL_DD)          # soot over the vent
    cabin_stilts(a, range(8))
    return a


def porch():
    """The Dance Porch, 7x5: cabin A's tin roof (mirrored) over an open porch on red posts, a red fascia with
    paper lanterns, the hall dark behind a cream railing, the doorway in the middle; cabin A's stilts with steps
    down the middle. BARN. Symmetric."""
    a = Art(7, 5)
    ca = cabin_a()
    a.im.paste(ca.im.crop((0, 0, 56, 40)), (0, 0))
    # the fascia beam under the eave
    a.hline(0, 55, 40, NAVY)
    a.hline(1, 55, 41, RU_HI)
    a.hline(1, 55, 42, BR)
    a.hline(1, 55, 43, BR_D)
    a.hline(1, 55, 44, NAVY)
    a.vline(0, 40, 44, NAVY)
    # the hall's front wall in the shade of the porch, dark
    for y in range(45, 54):
        for x in range(1, 56):
            a.put(x, y, TAR if y == 45 or x % 8 == 4 else BR_D)
    a.rect(1, 54, 55, 62, TAR)
    a.hline(1, 55, 57, OL_DD)
    a.hline(1, 55, 60, OL_DD)
    # the railing
    a.hline(1, 47, 55, CREAM)
    a.hline(1, 47, 56, OL_M)
    for x in range(1, 48):
        if x % 4 == 1:
            a.vline(x, 57, 61, OL_L)
    a.hline(1, 47, 62, OL_L)
    a.hline(0, 55, 63, NAVY)
    # the doorway (the door cell is the middle column)
    a.rect(50, 46, 55, 53, NAVY)
    a.hline(48, 55, 62, OL_D)
    a.vline(0, 40, 63, NAVY)
    # posts: the corner, one mid, one each side of the door
    for p in (1, 24, 43):
        a.vline(p, 44, 63, NAVY)
        a.vline(p + 1, 45, 63, RU_HI)
        a.vline(p + 2, 45, 63, BR)
        a.vline(p + 3, 45, 63, BR_D)
        a.vline(p + 4, 44, 63, NAVY)
    # paper lanterns along the eave (same 8 px phase, so they share tiles)
    lantern = [".NN.", "RLLR", "LCCL", "RLLR", ".RR."]
    for x in (12, 36):
        a.sprite(x, 45, lantern, {"N": NAVY, "R": RU, "L": RU_L, "C": CREAM})
    a.sprite(54, 45, [".N", "RL", "LC", "RL", ".R"], {"N": NAVY, "R": RU, "L": RU_L, "C": CREAM})
    cabin_stilts(a, (0, 1, 1, 1, 4, 5, 2))
    a.mirror_left()
    # the east half of the roof from cabin A's rust-free columns (unflipped), so the rust isn't mirrored
    for i, c in enumerate((1, 2, 6, 1, 2, 6, 7)):
        a.im.paste(ca.im.crop((c * 8, 0, c * 8 + 8, 40)), (56 + i * 8, 0))
    return a


# ================================================================ cookhouse dressing
def chimney():
    """1x2 stovepipe through the cookhouse roof, a rain hat, smoke rising. BARN. Symmetric."""
    a = Art(1, 2)
    a.sprite(3, 10, ["..NNNNNN..", ".NLLLLLLN.", "NNNNNNNNNN"], {"N": NAVY, "L": OL_L})
    for y in range(13, 27):
        a.sprite(5, y, ["NSLLSN" if y % 8 != 3 else "NDSSDN"], {"N": NAVY, "L": OL_L, "S": STEEL, "D": STEEL_D})
    a.sprite(3, 27, ["NNNNNNNNNN", "NRUUUUUURN", "NDDDDDDDDN", "NNNNNNNNNN"], {"N": NAVY, "R": RU_L, "U": RU, "D": RU_D})
    a.sprite(4, 0, ["..LLL", ".LCCL", "LCCCL", ".LLCL", "..LL.", "...LL", "..LCL", "...L."],
             {"L": OL_L, "C": CREAM})
    a.mirror_left()
    return a


def pot():
    """2x2 cast-iron gumbo pot on a fire in a ring of stones, steam rising. BARN. Drawn symmetric (flipped
    halves are free) and a glint added on the lit side."""
    a = Art(2, 2)
    for cx in (5, 10, 16):
        a.ellipse(cx, 26.5, 2.6, 2.0, OL_M)
        a.ellipse(cx - 0.7, 25.8, 1.3, 1.0, OL_L)
    for cx, h in ((7, 6), (12, 8)):
        for t in range(h):
            w = max(0, round(1.6 * (1 - t / h)))
            for x in range(cx - w, cx + w + 1):
                a.put(x, 27 - t, RU if abs(x - cx) == w else RU_L)
        a.put(cx, 26, CREAM)
        a.put(cx, 25, CREAM)
    a.ellipse(15.5, 17, 11.5, 8, TAR)
    a.ellipse(15.5, 19, 9, 5, OL_DD, x0=0, x1=15)
    a.ellipse(15.5, 10, 11.5, 3.5, OL_DD)
    a.ellipse(15.5, 10, 10, 2.6, STEEL_D)
    a.ellipse(15.5, 10.5, 8.5, 2.2, RU_D)
    a.ellipse(15.5, 10.5, 5, 1.2, RU)
    a.put(11, 10, RU_L)
    a.put(14, 11, CREAM)
    a.rect(3, 12, 4, 14, TAR)
    a.outline(NAVY, (0, 7, 15, 31))
    for cx, cy, r in ((12, 4, 2.0), (14.5, 2.2, 1.8)):
        a.ellipse(cx, cy, r, r * 0.8, OL_L)
        a.ellipse(cx - 0.5, cy - 0.5, r * 0.6, r * 0.5, CREAM)
    a.mirror_left()
    a.rect(8, 14, 9, 15, STEEL_D)               # glint on the lit side
    a.put(8, 14, OL_L)
    return a


def woodpile():
    """2x1 split wood stacked in three courses, log ends to the front. P4. Symmetric."""
    a = Art(2, 1)
    end = [".DDDD.", "DHLLHD", "DLMMLD", "DLMMLD", ".DDDD."]
    pal = {"D": W_DD, "H": W_HI, "L": W_L, "M": W_M}
    a.rect(3, 8, 28, 14, W_D)
    a.rect(7, 4, 24, 8, W_D)
    for x in (1, 9, 17, 25):
        a.sprite(x, 10, end, pal)
    for x in (5, 13, 21):
        a.sprite(x, 6, end, pal)
    for x in (9, 17):
        a.sprite(x, 2, end, pal)
    a.outline(NAVY)
    a.mirror_left()
    return a


# ================================================================ gator pens and okra
POST = ["..NNNN..", ".NHHHHN.", ".NLHHLN.", ".NDLLDN.", ".NDLLDN.", ".NDLLDN.", ".NDLLDN.", ".NDLLDN.",
        ".NDLLDN.", ".NDLLDN.", ".NDLLDN.", ".NNNNNN."]           # x 4..11, y 2..13
P4P = {"N": NAVY, "H": W_HI, "L": W_L, "M": W_M, "D": W_D, "K": W_DD, "G": GREY, "S": SLATE, "P": PALE,
       "W": WHITE4, "Y": GOLD, "O": GOLD_D}


def rails(a, x0, x1):
    for y0 in (4, 9):
        a.hline(x0, x1, y0, NAVY)
        a.hline(x0, x1, y0 + 1, W_L)
        a.hline(x0, x1, y0 + 2, W_M)
        a.hline(x0, x1, y0 + 3, NAVY)
    for x in (2, 13):
        if x0 <= x <= x1:
            a.put(x, 6, W_D)
            a.put(x, 11, W_D)


def vrail(a, y0, y1):
    a.vline(6, y0, y1, NAVY)
    a.vline(7, y0, y1, W_L)
    a.vline(8, y0, y1, W_L)
    a.vline(9, y0, y1, NAVY)


def pen_piece(kind):
    """The pen fence (P4 weathered wood), dual-grid: every piece has its post in the middle of the cell and rails
    out to the sides it joins. Symmetric posts, so ne/se are the flips of nw/sw."""
    a = Art(1, 1)
    west, east, north, south = {"h": (1, 1, 0, 0), "v": (0, 0, 1, 1), "nw": (0, 1, 0, 1), "ne": (1, 0, 0, 1),
                                "sw": (0, 1, 1, 0), "se": (1, 0, 1, 0)}[kind]
    if west:
        rails(a, 0, 5)
    if east:
        rails(a, 10, 15)
    if north:
        vrail(a, 0, 2)
    if south:
        vrail(a, 13, 15)
    a.sprite(4, 2, POST, P4P)
    return a


def pen_gate():
    """The pen's gate: rails right across with a cross brace and a stile at each end (no post)."""
    a = Art(1, 1)
    rails(a, 0, 15)
    for t in range(10):
        for x in (3 + t, 12 - t):
            a.put(x, 4 + t, W_HI if t < 2 else W_M)
    a.sprite(0, 3, ["N", "H", "M", "M", "M", "M", "M", "M", "M", "M", "N"], P4P)
    a.sprite(1, 3, ["N", "L", "D", "D", "D", "D", "D", "D", "D", "D", "N"], P4P)
    a.mirror_left()
    return a


def gator(open_jaw=True):
    """2x1 gator half sunk in the mud, head east. BARN: olive greys, cream teeth, red mouth, orange eye; the
    mud lapping round the body in tar."""
    a = Art(2, 1)
    # tail (tapering west), body, head
    for x in range(1, 12):
        hw = 0.7 + (x - 1) * 0.22
        for y in range(16):
            if abs(y - 9.5) <= hw:
                a.put(x, y, OL_D)
    a.ellipse(15.5, 9, 7.5, 4.2, OL_D)
    if open_jaw:
        head = ["..NN........",
                ".NMMNNNNN...",
                "dddETddMdNN.",
                "ddddddddddN.",
                "dddddddMdddN",
                "dddNCNCNCNCN",
                "ddNRRRRRRRRN",
                "ddNrRRRRRRN.",
                "dddNCNCNCN..",
                "ddddddddN...",
                "NKKKKKNN...."]
    else:
        head = ["..NN........",
                ".NMMNNNN....",
                "dddETddMNN..",
                "ddddddddddN.",
                "dddddddMdddN",
                "ddddddddddN.",
                "dddCdCdCdCN.",
                "dddNNNNNNN..",
                "ddKKKK......"]
    a.sprite(20, 3, head, {"N": NAVY, "M": OL_M, "d": OL_D, "C": CREAM, "R": BR, "r": BR_D, "E": RU_L, "T": TAR,
                           "K": OL_DD})
    # scutes along the back and the tail's crest
    for x in range(9, 22, 2):
        a.put(x, 7, OL_M)
        a.put(x + 1, 7, OL_L if x < 15 else OL_M)
        a.put(x, 10, OL_M)
        a.put(x + 1, 10, OL_DD)
    for x in range(2, 10, 2):
        a.put(x, 9, OL_M)
        a.put(x + 1, 9, OL_L if x > 5 else OL_M)
    for x in range(10, 22, 3):
        a.put(x, 12, OL_DD)
    a.outline(NAVY, skip=(TAR,))
    # wet mud lapping the waterline (the south edge of the body) and a few ripples
    for x in range(0, 32):
        for y in range(15, 6, -1):
            if a.get(x, y) == NAVY and (y == 15 or a.get(x, y + 1) == KEY):
                a.put(x, y, TAR)
                break
    for x, y in ((3, 13), (4, 13), (13, 15), (14, 15), (15, 15), (20, 15), (21, 15)):
        if a.get(x, y) == KEY:
            a.put(x, y, TAR)
    return a


def gator_eyes():
    """1x1 a gator lying under the mud: two eye bumps and the nostrils above it, mud rippled round. BARN.
    Symmetric."""
    a = Art(1, 1)
    a.sprite(0, 3, ["..TT....", ".T......", "........", ".T......", "..T.....", "...TT...", "........",
                    "........", "........", "....TT..", "........"], {"T": TAR})
    a.sprite(0, 4, ["........", "....NNN.", "...NMMMN", "...NdELN", "....NNN.", "........", "......NN",
                    ".....NdT", "......NN"],
             {"N": NAVY, "M": OL_M, "d": OL_D, "E": RU_L, "L": TAR, "T": TAR})
    a.mirror_left()
    return a


def okra():
    """1x1 okra bed, opaque: a tilled ridge running north-south between furrows, an okra plant on it (palmate
    leaves, upright pods, a flower). Tiles seamlessly both ways (the furrows are symmetric, the plant stays inside
    the cell). GARDEN family (primary palette 0)."""
    a = Art(1, 1)
    for y in range(16):
        for x in range(16):
            c = GD_SOIL
            if x in (0, 15):
                c = GD_SOIL_D
            elif x in (1, 14) and y % 2:
                c = GD_SOIL_D
            a.put(x, y, c)
    for x, y in ((4, 1), (10, 3), (6, 6), (11, 9), (3, 11), (8, 13), (11, 15), (4, 15)):
        a.hline(x, x + 1, y, GD_SOIL_D)
    a.sprite(0, 0, ["................",
                    "........D.......",
                    ".......DLD......",
                    ".......DLD..YY..",
                    "...D...DGD.YWYY.",
                    "..DLD...M..YRYY.",
                    "..DLD..DMD..YY..",
                    "..DGD.DLLMD.D...",
                    "...MDDLLMLLDMD..",
                    "..DLLDLMLLMLLLD.",
                    ".DLLMLLMLMLLLMD.",
                    ".DLMLLMMLLMLLD..",
                    "..DDLMDMDMLDD...",
                    "....DD.M.DD.....",
                    ".......MS.......",
                    "........S......."],
             {"D": GD_DD, "L": GD_L, "M": GD_M, "G": GD_G, "Y": GD_YEL, "W": GD_WH, "R": GD_RED, "S": GD_SOIL_D})
    return a


def okra_b():
    """The second okra cell: the first one mirrored (free) with a pair of pods where the flower was."""
    a = okra().mirrored()
    a.rect(1, 3, 5, 6, GD_SOIL)
    a.sprite(2, 2, ["..D.", ".DLD", ".DLD", ".DGD", "..M."], {"D": GD_DD, "L": GD_L, "G": GD_G, "M": GD_M})
    return a


# ================================================================ racks, lights, posts
def rack(kind):
    """2x2 drying rack: two poles and a crossbar (P4) with split fish or a net hung on it. The poles mirror,
    the middle repeats, so fish rack and net rack share their pole tiles."""
    a = Art(2, 2)
    # left pole and bar (mirrored afterwards)
    a.hline(1, 15, 4, NAVY)
    a.hline(1, 15, 5, W_L)
    a.hline(1, 15, 6, W_D)
    a.hline(1, 15, 7, NAVY)
    a.sprite(2, 2, [".NN.", "NHHN"], P4P)
    for y in range(4, 29):
        a.sprite(2, y, ["NLDN"], P4P)
    a.sprite(1, 28, ["NNNNNN"], P4P)
    a.put(4, 6, W_DD)
    if kind == "fish":
        fish = ["N.N", "NSN", ".N.", "NPN", "NWN", "PHP", "PHP", "PHP", "PHP", "NHN", "NGN", "NGN", ".N."]
        small = ["N.N", ".N.", "NPN", "PHP", "PHP", "PHP", "NHN", "NGN", ".N."]
        for x in (8,):
            a.sprite(x + 1, 7, fish, P4P)
            a.sprite(x + 5, 7, small, P4P)
        a.put(9, 7, NAVY)
    else:
        for y in range(8, 25):
            for x in range(7, 16):
                sag = 22 + (x - 7) * 2 // 8
                if y > sag:
                    continue
                if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                    a.put(x, y, GREY if y < 15 else SLATE)
        for x in range(7, 16):
            sag = 22 + (x - 7) * 2 // 8
            a.put(x, sag + 1, NAVY if x % 3 else GOLD_D)
        for x in range(8, 16, 3):
            a.put(x, 8, PALE)
    a.mirror_left()
    return a


def lantern():
    """1x1 lantern on a post by the boardwalk. P4. Symmetric."""
    a = Art(1, 1)
    a.sprite(4, 0, ["..NNNN..", ".NNNNNN.", ".NYYYYN.", ".NYWWYN.", ".NYWWYN.", ".NOYYON.", ".NNNNNN.",
                    "...NN...", "..NLLN..", "..NMMN..", "..NMMN..", "..NMMN..", "..NMMN..", "..NDDN..",
                    ".NNNNNN."], P4P)
    a.mirror_left()
    return a


RIPPLE = {"P": PALE, "W": WHITE4}


def bollard():
    """1x1 a squat mooring piling in the water, rope wrapped round it. P4."""
    a = Art(1, 1)
    a.sprite(3, 1, ["..NNNNNN..", ".NHHHHHHN.", "NHLLMMLHHN", "NHHLLLLHHN", "NLHHHHHHDN", "NLMMMMMMDN",
                    "NYOYOYOYON", "NOYOYOYODN", "NLMMMMMMDN", "NLMMMMMDDN", "NLMMMMMDDN", ".NNNNNNNN."], P4P)
    a.sprite(12, 7, ["Y.", "OY", ".O", ".Y", "O."], P4P)
    a.sprite(1, 13, [".PP.......WP.", "...WPPPPPP..."], RIPPLE)
    return a


def skiff():
    """3x1 jonboat: aluminium hull, two bench seats, an outboard at the stern, a rope off the bow (west) to
    its mooring post. P4."""
    a = Art(3, 1)
    for x in range(4, 42):
        top = 2 if x > 6 else 2 + (7 - x) // 1 // 2
        bot = 13 if x > 6 else 13 - (7 - x) // 2
        for y in range(top, bot + 1):
            a.put(x, y, GREY)
        a.put(x, top, WHITE4)
        a.put(x, top + 1, PALE)
        a.put(x, bot - 2, PALE)
        a.put(x, bot - 1, SLATE)
        a.put(x, bot, SLATE)
    for x in range(8, 41, 8):                     # ribs
        a.vline(x, 4, 10, SLATE)
    for x in (16, 32):                            # bench seats
        a.rect(x, 3, x + 3, 10, W_M)
        a.vline(x, 3, 10, W_L)
        a.vline(x + 3, 3, 10, W_D)
        a.hline(x, x + 3, 3, W_HI)
    a.rect(41, 2, 41, 13, SLATE)                  # transom
    a.sprite(41, 4, ["NNNNNNN", "NSGGGSN", "NSGWGSN", "NSGGGSN", "NSSSSSN", ".NNNNN.", "..NSN..", "..NNN.."], P4P)
    a.outline(NAVY)
    for x in range(0, 4):                         # the bow rope
        a.put(x, 7 + (x < 2), GOLD_D if x % 2 else GOLD)
    a.sprite(43, 13, ["W.P", ".PW"], RIPPLE)
    a.sprite(6, 15, ["P....PP"], RIPPLE)
    return a


def pirogue():
    """2x1 narrow dugout, pointed at both ends, a thwart amidships. P4. Symmetric."""
    a = Art(2, 1)
    for x in range(1, 16):
        hw = min(3.2, 0.6 + (x - 1) * 0.42)
        for y in range(16):
            d = y - 8.5
            if abs(d) <= hw:
                a.put(x, y, W_M)
        # rim and hollow
    for y in range(16):
        for x in range(1, 16):
            if a.get(x, y) == W_M:
                up = a.get(x, y - 1) == KEY
                dn = a.get(x, y + 1) == KEY
                if up:
                    a.put(x, y, W_HI)
                elif dn:
                    a.put(x, y, W_D)
    for x in range(5, 16):
        a.put(x, 8, W_DD)
        a.put(x, 9, W_D)
        if x > 7:
            a.put(x, 7, W_D)
            a.put(x, 10, W_L)
    a.rect(14, 6, 15, 11, W_L)
    a.vline(14, 6, 11, W_HI)
    a.outline(NAVY)
    a.sprite(5, 13, ["P.....WP"], RIPPLE)
    a.mirror_left()
    return a


# ================================================================ the trap line and buoys (P1)
P1P = {"N": NAVY, "R": R_M, "D": R_D, "H": R_HI, "L": R_L, "W": WH, "w": WH_D, "S": WH_S, "s": WH_DD,
       "G": GREY, "g": SLATE, "O": P1_WOOD, "o": P1_WOOD_L}


def trapline_h():
    """1x1 float line: a rope with a red float every 8 px, tiles east-west (both halves identical). P1."""
    a = Art(1, 1)
    for x in range(16):
        a.put(x, 8, P1_WOOD_L if x % 4 else P1_WOOD)
    for x0 in (2, 10):
        a.sprite(x0, 6, [".NN.", "NHRN", "RRRD", ".DD."], P1P)
        a.sprite(x0, 10, ["s..s"], P1P)
    return a


def trapline_end():
    """1x1 the end of a trap line: the rope from the west to an end buoy, and a wire crab trap half sunk. P1."""
    a = Art(1, 1)
    for x in range(0, 4):
        a.put(x, 8, P1_WOOD_L if x % 4 else P1_WOOD)
    a.sprite(3, 3, ["..NN..", ".NHRN.", "NHRRDN", "NWWWwN", "NRRRDN", ".NDDN.", "..ss.."], P1P)
    a.sprite(9, 6, ["NNNNNN", "NgSgSN", "NSgSgN", "NgSgSN", "NNNNNN", ".s..s."], P1P)
    return a


def buoy():
    """1x1 a red and white float on its own, ripple ring. P1. Symmetric."""
    a = Art(1, 1)
    a.sprite(0, 3, ["........", "......NN", ".....NHH", "....NHRR", "....NWWW", "....NRRR", ".....NDD",
                    "......NN", "....s...", "......ss"], P1P)
    a.mirror_left()
    return a


def extra_pieces():
    add("nurse", nurse(), "The Nurse Cabin (camp Pokemon Center) on stilts, 5x5.", doors=[(2, 3)], walk=[(2, 4)])
    add("bait", bait(), "The Bait Shack (camp Mart) on stilts, 5x5.", doors=[(1, 3)], walk=[(1, 4)])
    add("smokehouse", smokehouse(), "The smokehouse on stilts, 4x5.", doors=[(1, 3)], walk=[(1, 4)])
    add("porch", porch(), "The Dance Porch (red hall, open porch, lanterns) on stilts, 7x5.", doors=[(3, 3)],
        walk=[(3, 4)])
    add("chimney", chimney(), "Stovepipe and smoke for the cookhouse roof, 1x2.")
    add("pot", pot(), "Cast-iron gumbo pot on a fire, 2x2.")
    add("woodpile", woodpile(), "Stacked split wood, 2x1.")
    for k in ("h", "v", "nw", "ne", "sw", "se"):
        add("pen_" + k, pen_piece(k), f"Gator pen fence ({k}), weathered wood.")
    add("pen_gate", pen_gate(), "Gator pen gate.")
    add("gator", gator(True), "Gator half sunk in the mud, jaw open, 2x1.")
    add("gator_b", gator(True).mirrored(), "Gator half sunk in the mud, facing west (gator mirrored), 2x1.")
    add("gator_eyes", gator_eyes(), "A gator's eyes and nostrils above the mud, 1x1.")
    add("okra", okra(), "Okra bed (tiles both ways), with a flower.")
    add("okra_b", okra_b(), "Okra bed (tiles both ways), pods.")
    add("fishrack", rack("fish"), "Fish drying rack, 2x2.")
    add("netrack", rack("net"), "Net drying rack, 2x2.")
    add("lantern", lantern(), "Lantern on a post, 1x1.")
    add("bollard", bollard(), "Mooring bollard with rope, in the water, 1x1.")
    add("mooring_post", bollard(), "Mooring post in the water (the bollard's art), 1x1.")
    add("skiff", skiff(), "Jonboat with outboard, rope off the bow (west), 3x1.")
    add("pirogue", pirogue(), "Pirogue (dugout), 2x1.")
    add("trapline_h", trapline_h(), "Trap line: rope with floats, tiles east-west, 1x1.")
    add("trapline_end", trapline_end(), "Trap line end: end buoy and a crab trap, 1x1.")
    add("buoy", buoy(), "A lone float buoy, 1x1.")


# ================================================================ main
def pack():
    """All pieces onto one sheet, 16 cells wide, rows packed left to right."""
    order = sorted(PIECES, key=lambda n: (not n.startswith("bw_"), -PIECES[n][0].h, n))
    W = 20
    x = y = rowh = 0
    place = {}
    for n in order:
        art, meta = PIECES[n]
        if x + art.w > W:
            x, y, rowh = 0, y + rowh, 0
        place[n] = (x, y)
        x += art.w
        rowh = max(rowh, art.h)
    H = y + rowh
    sheet = Image.new("RGB", (W * 16, H * 16), KEY)
    index = {}
    for n, (cx, cy) in place.items():
        art, meta = PIECES[n]
        sheet.paste(art.im, (cx * 16, cy * 16))
        index[n] = dict(meta, x=cx, y=cy)
    return sheet, index


def preview(sheet):
    """The sheet over a swamp backdrop (grass, water stripes), 4x."""
    bg = Image.new("RGB", sheet.size, (120, 160, 104))
    px = bg.load()
    for y in range(sheet.height):
        for x in range(sheet.width):
            if (y // 16) % 3 == 2:
                px[x, y] = (96, 136, 136)
    mask = Image.new("L", sheet.size, 0)
    mp, sp = mask.load(), sheet.load()
    for y in range(sheet.height):
        for x in range(sheet.width):
            mp[x, y] = 0 if sp[x, y] == KEY else 255
    bg.paste(sheet, (0, 0), mask)
    return bg.resize((bg.width * 4, bg.height * 4), Image.NEAREST)


def main():
    boardwalk()
    add("cabin_a", cabin_a(), "Stilt cabin A (rust tin, grey clapboard) on pilings, 4x5.", doors=[(1, 3)], walk=[(1, 4)])
    add("cabin_a_m", cabin_a().mirrored(), "Stilt cabin A mirrored, 4x5.", doors=[(2, 3)], walk=[(2, 4)])
    add("cabin_b", cabin_b(), "Stilt cabin B (cedar shakes, stained boards) on pilings, 4x5.", doors=[(1, 3)], walk=[(1, 4)])
    add("cabin_b_m", cabin_b().mirrored(), "Stilt cabin B mirrored, 4x5.", doors=[(2, 3)], walk=[(2, 4)])
    for extra in EXTRA:
        extra()
    sheet, index = pack()
    sheet.save(os.path.join(HERE, "camp.png"))
    preview(sheet).save(os.path.join(HERE, "camp_preview.png"))
    with open(os.path.join(HERE, "camp.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_comment": "Camp Cocodrie own art index (make_camp_art.py): piece -> sheet cell and size.",
                   "pieces": index}, f, indent=1)
        f.write("\n")
    print("camp.png", sheet.size, len(index), "pieces")


EXTRA = [extra_pieces]

if __name__ == "__main__":
    main()

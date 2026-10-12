"""Own art for Lutin's Hollow (gym 6, Fairy): a hidden hollow ringed by moss-draped live oaks.

Everything here is drawn in Python (no source art), on one small swamp palette (the Ekat grass, the bayou's leaf
greens and bark browns, Spanish-moss greys, timber and a few fairy accents), and returned as RGBA sprites with an
anchor. hollow.py composites the sprites into one scene the size of the map, so canopies, moss curtains,
undergrowth and buildings overlap naturally, then cuts the scene into 16x16 cells (each distinct cell is one
metatile). Textures repeat every 8 or 16 px where they can, so repeated cells share tiles.

    moss_tree()     a live oak: lumpy canopy, Spanish moss beards (a layer of their own), trunk and roots
    great_tree()    the Pokemon Center: a vast hollow oak, its door an arched hollow in the trunk, Poke Ball plaque
    arbour()        the gym: a glade pavilion behind hanging curtains of Spanish moss, parted at the door
    cottage()       the moss houses and the Herbalist: thick moss roofs, timber walls, round doors, herb bundles
    props           ferns, bushes, flowers, glow-bells, toadstools, fairy rings, pepper rows, still pools,
                    the riddle stone, a mossy log

usage: python tools/mapgen/sources/orleans_custom/make_hollow_art.py
writes hollow.png + hollow.json (the pieces hollow_tileset.py turns into prefabs), hollow_preview.png and the review sheet
maps/00_hollow_art.png. The pieces are drawn by THE PIECE LAYER further down (2026-10-12); the sketches just below are
the first pass, kept for reference (sketch_preview() still draws them) but no longer registered.
"""
import math
import os
import random

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette (GBA colours: multiples of 8)
G, G_L, G_D = (120, 160, 104), (136, 176, 128), (104, 144, 96)   # the Ekat swamp grass and its specks
SH, SH_D = (96, 128, 80), (80, 112, 72)                         # shade on the grass under canopies
L0, L1, L2, L3, L4 = (40, 56, 40), (56, 80, 56), (72, 104, 64), (96, 128, 80), (128, 160, 96)  # leaves
M0, M1, M2, M3 = (96, 112, 96), (128, 144, 120), (160, 176, 144), (200, 208, 176)             # Spanish moss
B0, B1, B2, B3 = (56, 48, 40), (88, 64, 56), (120, 88, 72), (152, 112, 88)                    # bark
W1, W2, W3, W4 = (104, 72, 56), (136, 96, 72), (168, 128, 96), (200, 168, 128)                # timber
PL, PL_D = (224, 208, 168), (192, 176, 136)                                                   # plaster
S1, S2, S3 = (96, 96, 88), (136, 136, 120), (176, 176, 160)                                   # stone
P1, P2, P3 = (192, 88, 144), (232, 144, 192), (248, 200, 224)                                 # fairy pink
V1, V2 = (120, 88, 168), (168, 136, 216)                                                      # violet
Y1, Y2 = (232, 192, 88), (248, 240, 168)                                                      # warm glow
C1, C2 = (104, 200, 200), (184, 240, 232)                                                     # cold glow
R1, R2, R3 = (168, 48, 48), (216, 80, 72), (248, 152, 136)                                    # Center red
U1, U2 = (56, 88, 152), (96, 136, 200)                                                        # Mart blue
WH = (248, 248, 240)
WA, WA_D, WA_L, WA_G = (96, 136, 136), (72, 112, 112), (136, 176, 176), (192, 224, 216)       # water
LEAVES = [L0, L1, L2, L3, L4]


class Sprite:
    """An RGBA pixel canvas with an anchor: (ax, ay) is the pixel that sits on the anchor point in the scene."""

    def __init__(self, w, h, ax=0, ay=0):
        self.a = np.zeros((h, w, 4), np.uint8)
        self.w, self.h, self.ax, self.ay = w, h, ax, ay

    def put(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = c
            self.a[y, x, 3] = 255

    def get(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3]:
            return tuple(int(v) for v in self.a[y, x, :3])
        return None

    def on(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[int(y), int(x), 3] > 0

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def outline(self, c):
        """Every opaque pixel that touches a clear one (4-neighbours) becomes `c`."""
        m = self.a[:, :, 3] > 0
        p = np.pad(m, 1)
        inner = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        self.a[m & ~inner, :3] = c

    def paste(self, other, x, y, where=None):
        """Draw `other` with its anchor at (x, y). `where(dest_rgba) -> bool mask`: only where it allows."""
        x0, y0 = int(x) - other.ax, int(y) - other.ay
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = min(other.w, self.w - x0), min(other.h, self.h - y0)
        if sx1 <= sx0 or sy1 <= sy0:
            return
        src = other.a[sy0:sy1, sx0:sx1]
        dst = self.a[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
        m = src[:, :, 3] > 0
        if where is not None:
            m &= where(dst)
        dst[m] = src[m]

    def flipped(self):
        s = Sprite(self.w, self.h, self.w - 1 - self.ax, self.ay)
        s.a = self.a[:, ::-1].copy()
        return s

    def image(self):
        return Image.fromarray(self.a, "RGBA")


def disc(cx, cy, rx, ry=None):
    ry = ry or rx
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                yield x, y


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def shade_clump(s, cx, cy, r, ramp, rng, ry=None, light=(-0.55, -0.83), fleck=0.18, rim=1):
    """A round clump of leaves lit from the upper left: banded shading with an ordered dither between bands,
    leaf flecks, and a darker rim on its shadow side (where it sits over whatever was drawn before)."""
    ry = ry or r * 0.86
    for x, y in disc(cx, cy, r, ry):
        nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - cy) / ry
        rr = nx * nx + ny * ny
        nz = math.sqrt(max(0.0, 1 - rr))
        lum = -(nx * light[0] + ny * light[1]) * 0.75 + nz * 0.55
        t = (lum + 0.35) / 1.45 * (len(ramp) - 1)
        t += (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.9
        k = max(0, min(len(ramp) - 1, int(round(t))))
        if rng.random() < fleck and 0 < k < len(ramp) - 1:  # leaf flecks: a lighter or darker leaf here and there
            k += 1 if rng.random() < 0.5 else -1
        if rr > 0.78 and (nx * light[0] + ny * light[1]) < -0.1:
            k = min(k, rim)
        s.put(x, y, ramp[k])


def moss_strand(short, long_, x, y, n, rng, top=4):
    """One beard of Spanish moss hanging from (x, y), n pixels long, wavering a little, pale near the top.
    Its first `top` pixels go on `short`, the rest on `long_` (scenes let long moss hang only in front of
    trunks and over open ground, not across the canopy below)."""
    for k in range(n):
        if k and k % 3 == 0 and rng.random() < 0.45:
            x += rng.choice((-1, 1))
        c = M3 if k == 0 else M2 if (k + x) % 3 else M1
        if k >= n - 2:
            c = M1 if k == n - 2 else M0
        layer = short if k < top else long_
        layer.put(x, y + k, c)
        if k < n - 3 and rng.random() < 0.3:
            layer.put(x + 1, y + k, M0)


def hang(short, long_, mask, rng, every=(1, 3), length=(7, 16), top=4):
    """Spanish moss along the underside of a canopy mask: beards wherever its lower edge is, longest in the
    middle of the tree and short at its sides."""
    h, w = mask.shape
    xs = [x for x in range(w) if mask[:, x].any()]
    if not xs:
        return
    x0, x1 = xs[0], xs[-1]
    x = x0 + rng.randint(2, 3)
    while x < x1 - 1:
        y = int(np.nonzero(mask[:, x])[0].max())
        mid = 1 - abs((x - x0) / max(1, x1 - x0) * 2 - 1)
        n = int(length[0] * 0.5 + (length[1] - length[0] * 0.5) * mid * rng.uniform(0.55, 1.0))
        moss_strand(short, long_, x, y - 2, max(3, n), rng, top)
        if rng.random() < 0.55:
            moss_strand(short, long_, x + 1, y - 1, max(3, n - rng.randint(2, 6)), rng, top)
        x += rng.randint(*every) + 1


# ---------------------------------------------------------------- the moss-draped live oak
def moss_tree(seed=1, w=48, canopy_h=30, trunk_h=12, roots=True):
    """A live oak hung with Spanish moss. Anchor: the middle of the trunk's foot. Returns (body, moss, long_moss)."""
    rng = random.Random(seed)
    H = canopy_h + trunk_h + 6
    s = Sprite(w + 4, H, (w + 4) // 2, canopy_h + trunk_h)
    cx = (w + 4) / 2
    base = canopy_h + trunk_h
    for x, y in disc(cx, base, 17, 3.4):  # shade on the grass
        s.put(x, y, SH)
    tw = 5
    for y in range(canopy_h - 6, base + 1):
        flare = max(0, y - (base - 5)) * 1.5
        x0, x1 = int(cx - tw - flare), int(cx + tw - 1 + flare)
        for x in range(x0, x1 + 1):
            f = (x - x0) / max(1, x1 - x0)
            c = B3 if f < 0.25 else B2 if f < 0.62 else B1
            if (x * 3 + y) % 7 == 0 and 0.1 < f < 0.9:
                c = B1  # bark furrows
            s.put(x, y, c)
        s.put(x0 - 1, y, B0)
        s.put(x1 + 1, y, B0)
    if roots:
        for dx, ln in ((-11, 6), (10, 6), (-6, 3), (5, 3)):
            for k in range(ln):
                x = cx + dx * (k + 1) / ln
                yy = base - 1 + (k > ln // 2)
                s.put(x, yy, B2)
                s.put(x, yy + 1, B0)
    s.hline(cx - 6, cx + 5, base + 1, B0)
    clumps = [(0, -8, 11), (-13, -3, 9), (13, -3, 9), (-7, 4, 10), (7, 4, 10), (0, 1, 11)]
    top = canopy_h / 2 + 1
    canopy = Sprite(s.w, s.h)
    for dx, dy, r in clumps:
        shade_clump(canopy, cx + dx + rng.uniform(-1, 1), top + dy + rng.uniform(-1, 1), r, LEAVES, rng)
    m = canopy.a[:, :, 3] > 0
    canopy.outline(L0)
    s.paste(canopy, 0, 0)
    short, long_ = Sprite(s.w, s.h, s.ax, s.ay), Sprite(s.w, s.h, s.ax, s.ay)
    hang(short, long_, m, rng)
    return s, short, long_


# ---------------------------------------------------------------- shared building bits
_MOSS_TEX = None


def moss_texture():
    """A 16x16 wrapping texture of moss cushions (so roof cells repeat and share tiles): lumpy clumps lit from
    the upper left, a few pale tufts."""
    global _MOSS_TEX
    if _MOSS_TEX is None:
        rng = random.Random(77)
        t = Sprite(48, 48)
        t.rect(0, 0, 47, 47, L1)
        for cx, cy, r in ((4, 4, 5.5), (12, 5, 5), (8, 11, 5.5), (0, 12, 5), (16, 12, 5), (4, 20, 5.5), (12, 21, 5),
                          (8, 27, 5.5), (0, 28, 5), (16, 28, 5)):
            for ox in (0, 16, 32):
                for oy in (0, 16, 32):
                    shade_clump(t, cx + ox, cy + oy - 4, r, [L1, L2, L3, L4], random.Random(int(cx * 7 + cy)),
                                fleck=0.12)
        tex = t.a[16:32, 16:32].copy()
        for x, y in ((3, 1), (11, 2), (7, 8), (15, 9), (3, 14)):  # pale tufts
            tex[y, x, :3] = M3
            tex[y, (x + 1) % 16, :3] = M2
        _MOSS_TEX = tex
    return _MOSS_TEX


def moss_roof(s, x0, y0, x1, y1, rng, eave_beards=True, round_top=10, sag=3):
    """A thick, rounded roof of moss over x0..x1, y0..y1: a loaf-shaped silhouette (ends rounded off, the eave
    sagging a little at each end), filled with the wrapping moss texture, outlined, with beards of Spanish moss
    along the eave."""
    tex = moss_texture()
    w = x1 - x0 + 1
    cols = []
    for x in range(x0, x1 + 1):
        u = (x + 0.5 - x0) / w * 2 - 1  # -1 .. 1
        top = y0 + round_top * (1 - math.sqrt(max(0.0, 1 - u ** 4)))
        bot = y1 - sag * (1 - abs(u) ** 6) + sag  # the middle of the eave sits sag px higher than its ends
        cols.append((x, int(round(top)), int(round(bot))))
    for x, top, bot in cols:
        for y in range(top, bot + 1):
            c = tex[y % 16, x % 16, :3]
            s.put(x, y, tuple(int(v) for v in c))
        s.put(x, top, L0)
        s.put(x, bot, L0)
        s.put(x, bot - 1, L1)
    for (xa, ta, ba), (xb, tb, bb) in zip(cols, cols[1:]):  # close the outline between steps
        for y in range(min(ta, tb), max(ta, tb) + 1):
            s.put(xa if ta > tb else xb, y, L0)
        for y in range(min(ba, bb), max(ba, bb) + 1):
            s.put(xa if ba < bb else xb, y, L0)
    s.vline(x0, cols[0][1], cols[0][2], L0)
    s.vline(x1, cols[-1][1], cols[-1][2], L0)
    if eave_beards:
        for x, top, bot in cols[2:-2:3]:
            n = 3 + (x * 7 + bot) % 4
            for k in range(n):
                s.put(x, bot + 1 + k, M2 if k < n - 1 else M1)
    return cols


def round_door(s, cx, y_bottom, w=10, h=14, wood=(W1, W2, W3), glow=False):
    """An arched plank door (round top), iron ring; `glow`: open, warm light inside."""
    x0, x1 = cx - w // 2, cx + w // 2 - 1
    ytop = y_bottom - h + 1
    r = w / 2
    for y in range(ytop, y_bottom + 1):
        for x in range(x0, x1 + 1):
            dy = y - (ytop + r)
            if dy < 0 and ((x + 0.5 - cx) / r) ** 2 + (dy / r) ** 2 > 1:
                continue
            if glow:
                c = Y1 if y > ytop + 3 else W1
                if y >= y_bottom - 2:
                    c = Y2
            else:
                c = wood[1] if (x - x0) % 3 else wood[0]
                if (x - x0) % 3 == 1:
                    c = wood[2]
            s.put(x, y, c)
    # frame
    for y in range(ytop, y_bottom + 1):
        for x in range(x0 - 1, x1 + 2):
            if s.get(x, y) is not None and not (x0 <= x <= x1):
                pass
    for x in range(x0 - 1, x1 + 2):
        for y in range(ytop - 1, y_bottom + 1):
            inside = x0 <= x <= x1 and ytop <= y and (y - (ytop + r) >= 0 or ((x + 0.5 - cx) / r) ** 2 + ((y - ytop - r) / r) ** 2 <= 1)
            if inside:
                continue
            near = any(x0 <= x + dx <= x1 and ytop <= y + dy <= y_bottom and (
                y + dy - (ytop + r) >= 0 or ((x + dx + 0.5 - cx) / r) ** 2 + ((y + dy - ytop - r) / r) ** 2 <= 1)
                for dx, dy in ((1, 0), (-1, 0), (0, 1)))
            if near:
                s.put(x, y, B0)
    if not glow:
        s.put(x1 - 2, y_bottom - 6, S1)
        s.put(x1 - 2, y_bottom - 5, S3)


def round_window(s, cx, cy, r=3.5, lit=True):
    for x, y in disc(cx, cy, r + 1):
        s.put(x, y, B0)
    for x, y in disc(cx, cy, r):
        s.put(x, y, Y1 if lit else S1)
    for x, y in disc(cx - 0.7, cy - 0.7, r * 0.55):
        s.put(x, y, Y2 if lit else S2)
    s.hline(cx - r + 1, cx + r - 1, cy, W1)  # glazing bars
    s.vline(cx, cy - r + 1, cy + r - 1, W1)


def herb_bundle(s, x, y, kind=0):
    """A bundle of drying herbs hung upside down from a string."""
    leaf, bloom = ((L3, L4), (V1, V2), (L2, M2))[kind % 3]
    s.vline(x, y, y + 1, W1)
    s.put(x, y + 2, B0)
    for k, ww in enumerate((1, 2, 2, 2, 1)):
        for dx in range(-ww + 1, ww):
            s.put(x + dx, y + 3 + k, leaf[(dx + k) % 2] if k < 3 else bloom[(dx + k) % 2])


def flower_dots(s, x0, y0, x1, y1, rng, cols, n):
    for _ in range(n):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1)
        c = rng.choice(cols)
        s.put(x, y, c)


def stone_step(s, x0, x1, y):
    s.hline(x0, x1, y, S3)
    s.hline(x0, x1, y + 1, S2)
    s.hline(x0, x1, y + 2, S1)
    s.put(x0 - 1, y + 1, B0)
    s.put(x1 + 1, y + 1, B0)


# ---------------------------------------------------------------- the moss houses and the Herbalist
def cottage(w_cells=5, h_cells=4, door_col=2, herbalist=False, seed=5):
    """A fairy-tale cottage: a deep moss roof drooping over low half-timbered walls on a stone footing, a round
    plank door, round windows lit warm. The Herbalist adds herb bundles under the eave, a blue sign board with
    a white leaf (the Mart's colours), and pots of herbs by the door. Anchor: top-left of its cell box."""
    rng = random.Random(seed)
    W, H = w_cells * 16, h_cells * 16
    s = Sprite(W, H)
    eave = H - 28  # the roof's lower edge
    # walls
    wall_top, foot = eave - 2, H - 4
    s.rect(2, wall_top, W - 3, foot, PL)
    for x in range(2, W - 2):  # timber frame: posts every 16 px, a rail, braces
        if (x - 2) % 16 in (0, 15):
            s.vline(x, wall_top, foot, W2)
    s.hline(2, W - 3, wall_top + 2, W2)
    s.hline(2, W - 3, foot - 6, W2)
    for x in range(2, W - 3, 16):
        for k in range(1, 6):  # little braces
            s.put(x + k, foot - 6 - k, W1)
            s.put(x + 15 - k, foot - 6 - k, W1)
    for y in range(wall_top, foot + 1):  # plaster shading under the eave
        if y < wall_top + 4:
            for x in range(3, W - 3):
                if s.get(x, y) == PL:
                    s.put(x, y, PL_D)
    s.rect(1, foot - 1, W - 2, H - 2, S2)  # stone footing
    for x in range(1, W - 1, 6):
        s.vline(x + (3 if (x // 6) % 2 else 0), foot - 1, H - 2, S1)
    s.hline(1, W - 2, foot - 1, S3)
    s.hline(1, W - 2, H - 1, B0)
    s.vline(1, wall_top, H - 2, B0)
    s.vline(W - 2, wall_top, H - 2, B0)
    # roof (over the wall top)
    moss_roof(s, 0, 1, W - 1, eave - 2, rng)
    # chimney poking through the roof
    cxh = W - 20 if not herbalist else 12
    s.rect(cxh, 0, cxh + 5, 7, S2)
    s.vline(cxh, 0, 7, B0)
    s.vline(cxh + 5, 0, 7, B0)
    s.hline(cxh, 0, cxh + 5, B0)
    s.hline(cxh + 1, cxh + 4, 1, S3)
    # door and windows
    dcx = door_col * 16 + 8
    round_door(s, dcx, H - 3, 10, 15)
    stone_step(s, dcx - 6, dcx + 5, H - 3)
    for c in range(w_cells):
        if c == door_col:
            continue
        if herbalist and c == door_col + 1:
            continue
        if abs(c - door_col) == 1 or (w_cells > 5 and c in (0, w_cells - 1)):
            round_window(s, c * 16 + 8, foot - 12, 3.5)
    # flower boxes under the windows / tufts at the footing
    for x in range(4, W - 4, 5):
        if abs(x - dcx) > 8:
            s.put(x, H - 4, (P2, Y1, V2, WH)[(x // 5) % 4])
            s.put(x + 1, H - 4, L3)
    if herbalist:
        for i, x in enumerate(range(8, W - 6, 7)):  # herb bundles along the eave
            if abs(x - dcx) > 6:
                herb_bundle(s, x, eave + 1, i)
        # the sign: a blue board with a white leaf, hung from a bracket right of the door
        sx = dcx + 10
        s.hline(sx, sx + 11, eave + 2, B0)
        s.vline(sx + 2, eave + 2, eave + 4, B0)
        s.vline(sx + 9, eave + 2, eave + 4, B0)
        s.rect(sx, eave + 5, sx + 11, eave + 13, U1)
        s.rect(sx + 1, eave + 6, sx + 10, eave + 12, U2)
        for x, y in disc(sx + 6, eave + 9, 3.2, 2.2):
            s.put(x, y, WH)
        s.put(sx + 3, eave + 11, WH)
        s.put(sx + 4, eave + 10, WH)
        s.hline(sx, sx + 11, eave + 14, B0)
        s.vline(sx - 1, eave + 5, eave + 13, B0)
        s.vline(sx + 12, eave + 5, eave + 13, B0)
    return s


# ---------------------------------------------------------------- the gym: the Moss Curtains
def arbour(w_cells=7, h_cells=5, seed=11):
    """Lutin's gym: a glade pavilion of bent boughs, roofed with moss and flowering vine, its front hung with
    curtains of Spanish moss between rustic posts. The middle curtain is tied back on the door, where a soft
    pink light shows; fairy lights along the beam, a carved fairy-wing plaque above the door. Anchor: top-left."""
    rng = random.Random(seed)
    W, H = w_cells * 16, h_cells * 16
    s = Sprite(W, H)
    dcx = W // 2
    beam = 30
    # the inner shade (behind the curtains): dark green, with a pink glow in the middle bay
    s.rect(4, beam - 2, W - 5, H - 4, L1)
    for x, y in disc(dcx, H - 14, 14, 18):
        if beam <= y <= H - 4:
            d = ((x - dcx) / 14) ** 2 + ((y - (H - 14)) / 18) ** 2
            s.put(x, y, P3 if d < 0.25 else P2 if d < 0.55 else P1 if d < 0.8 else V1)
    # roof: a long arched dome of moss over woven boughs, flowering vine across it
    tex = moss_texture()
    for y in range(0, beam + 1):
        for x in range(0, W):
            t = (x + 0.5 - W / 2) / (W / 2)
            top = 6 + 10 * t * t  # arched: lower at the ends
            if y >= top:
                s.put(x, y, tuple(int(v) for v in tex[y % 16, x % 16, :3]))
    for x in range(W):  # outline of the dome
        t = (x + 0.5 - W / 2) / (W / 2)
        top = int(math.ceil(6 + 10 * t * t))
        s.put(x, top, L0)
        t2 = (x + 1.5 - W / 2) / (W / 2)
        for y in range(top, int(math.ceil(6 + 10 * t2 * t2)) + 1):
            if x + 1 < W:
                s.put(x if t2 * t2 > t * t else x + 1, y, L0)
    s.vline(0, 16, beam, L0)
    s.vline(W - 1, 16, beam, L0)
    # the woven ridge: a bough arching along the top, and the front beam
    for x in range(4, W - 4):
        t = (x + 0.5 - W / 2) / (W / 2)
        y = int(8 + 10 * t * t)
        s.put(x, y, B2 if x % 4 else B3)
        s.put(x, y + 1, B1)
    s.hline(1, W - 2, beam - 1, B3)
    s.hline(1, W - 2, beam, B2)
    s.hline(1, W - 2, beam + 1, B0)
    # flowering vine on the roof: blossoms in clusters
    for _ in range(46):
        x = rng.randint(4, W - 5)
        t = (x + 0.5 - W / 2) / (W / 2)
        y = rng.randint(int(9 + 10 * t * t), beam - 4)
        c = rng.choice((P2, P3, V2, P2, WH))
        s.put(x, y, c)
        if rng.random() < 0.5:
            s.put(x + 1, y, P1 if c != WH else Y2)
    # posts: rustic bough posts at each end and either side of the door bay
    posts = [3, dcx - 14, dcx + 12, W - 6]
    for px in posts:
        s.rect(px, beam - 1, px + 2, H - 4, B2)
        s.vline(px, beam - 1, H - 4, B3)
        s.vline(px - 1, beam, H - 4, B0)
        s.vline(px + 3, beam, H - 4, B0)
        for k in range(3):  # a little flare at the foot
            s.put(px - 1 - k // 2, H - 4 + k // 2, B1)
            s.put(px + 3 + k // 2, H - 4 + k // 2, B1)
    # the curtains of moss: dense strands from the beam, longest mid-bay, swaying
    bays = [(5, dcx - 15), (dcx + 15, W - 7)]
    for a, b in bays:
        for x in range(a, b + 1):
            mid = 1 - abs((x - a) / max(1, b - a) * 2 - 1)
            n = int(34 + 14 * mid + rng.randint(-4, 3))
            xx = x
            for k in range(n):
                if k and k % 5 == 0 and rng.random() < 0.35:
                    xx += rng.choice((-1, 1))
                if not (a - 1 <= xx <= b + 1):
                    continue
                c = (M3, M2, M2, M1, M2, M1)[(k + x * 2) % 6] if (x % 3) else (M1, M0, M1)[k % 3]
                if k >= n - 2:
                    c = M0
                s.put(xx, beam + 2 + k, c)
    # the door bay: the curtain tied back to both sides, the doorway between
    for side in (-1, 1):
        x_tie = dcx + side * 11
        for k in range(36):
            spread = int(6 * math.sin(min(1.0, k / 22) * math.pi / 2))
            for j in range(4):
                x = x_tie - side * (3 - j) + side * (-spread if k > 18 else 0) // 2
                c = (M2, M3, M2, M1)[(j + k) % 4]
                s.put(x + side * (spread // 3), beam + 2 + k, c)
        y_tie = beam + 22
        s.hline(x_tie - 2, x_tie + 2, y_tie, P1)  # a pink ribbon ties each curtain back
        s.put(x_tie, y_tie - 1, P2)
    # the doorway: a soft glowing arch with sparkles
    for x, y in [(dcx - 5, beam + 10), (dcx + 4, beam + 16), (dcx - 2, beam + 24), (dcx + 6, beam + 30),
                 (dcx - 6, beam + 34)]:
        s.put(x, y, WH)
        s.put(x + 1, y, P3)
        s.put(x, y + 1, P3)
    # fairy lights along the beam
    for x in range(6, W - 6, 6):
        s.put(x, beam + 2 + (x // 6) % 2, Y2)
        s.put(x, beam + 3 + (x // 6) % 2, Y1)
    # a carved plaque with fairy wings above the door
    px0, py0 = dcx - 8, beam - 9
    s.rect(px0, py0, px0 + 15, py0 + 7, W3)
    s.hline(px0, px0 + 15, py0, B0)
    s.hline(px0, px0 + 15, py0 + 7, B0)
    s.vline(px0, py0, py0 + 7, B0)
    s.vline(px0 + 15, py0, py0 + 7, B0)
    for x, y in ((dcx - 1, py0 + 3), (dcx, py0 + 3), (dcx - 1, py0 + 4), (dcx, py0 + 4)):
        s.put(x, y, P1)
    for side in (-1, 1):  # wings
        base = dcx if side > 0 else dcx - 1
        for x, y in ((base + side * 2, py0 + 2), (base + side * 3, py0 + 2), (base + side * 4, py0 + 3),
                     (base + side * 2, py0 + 3), (base + side * 3, py0 + 3), (base + side * 2, py0 + 5),
                     (base + side * 3, py0 + 5)):
            s.put(x, y, P2 if y < py0 + 4 else P3)
    # mossy stone threshold, and blossoms at the posts' feet
    stone_step(s, dcx - 8, dcx + 7, H - 4)
    for px in posts:
        for dx in (-3, -1, 4, 6):
            s.put(px + dx, H - 3, rng.choice((P2, V2, WH, Y2)))
            s.put(px + dx, H - 2, L2)
    return s


# ---------------------------------------------------------------- the Pokemon Center: a great hollow oak
def great_tree(seed=21):
    """The Pokemon Center: the trunk of a vast live oak, 6 cells across at its root flare, its door an arched
    hollow. Its crown is part of the canopy above (the scene draws it as a crown of big clumps). A red and white
    Poke Ball plaque hangs over the arch, two red lanterns either side, lit round windows up the trunk.
    Returns (trunk sprite anchored at its foot centre, crown sprite anchored at the same point)."""
    rng = random.Random(seed)
    W, H = 104, 72
    s = Sprite(W, H, W // 2, H - 4)
    cx = W / 2
    foot = H - 4
    for x, y in disc(cx, foot, 50, 5):  # shade on the grass
        s.put(x, y, SH)
    # trunk: wide, slightly narrowing upward, flaring into buttress roots
    for y in range(0, foot + 1):
        k = y / foot
        half = 24 + 3 * k + (max(0, y - (foot - 14)) ** 1.7) * 0.55
        x0, x1 = int(cx - half), int(cx + half - 1)
        for x in range(x0, x1 + 1):
            f = (x - x0) / max(1, x1 - x0)
            c = B3 if f < 0.2 else B2 if f < 0.55 else B1
            # deep vertical furrows every 6 px, wavering
            if (x + int(2 * math.sin(y / 5.0))) % 6 == 0 and 0.06 < f < 0.94:
                c = B0 if f > 0.55 else B1
            elif (x + int(2 * math.sin(y / 5.0))) % 6 == 1 and f < 0.55:
                c = B3
            s.put(x, y, c)
        s.put(x0 - 1, y, B0)
        s.put(x1 + 1, y, B0)
    # roots: three buttresses each side, sloping onto the grass
    for side in (-1, 1):
        for k, (dx, ln) in enumerate(((28, 12), (36, 10), (44, 7))):
            for i in range(ln):
                x = cx + side * (dx - 6 + i)
                y0 = foot - ln + i
                for y in range(int(y0), foot + 1):
                    s.put(x, y, B2 if y < foot - 1 else B1)
                s.put(x, y0 - 1, B0)
        s.hline(cx - 50, cx + 49, foot + 1, B0)
    # moss on the bark: a few green and grey patches
    for _ in range(18):
        x, y = rng.randint(int(cx - 22), int(cx + 20)), rng.randint(2, foot - 24)
        for dx in range(rng.randint(2, 4)):
            s.put(x + dx, y, rng.choice((L3, L2, M2)))
    # the hollow door: a tall arch of warm light, a step of root
    dx0 = int(cx) - 8
    arch_top = foot - 30
    for y in range(arch_top, foot + 1):
        for x in range(dx0 - 2, dx0 + 18):
            r = 10
            dy = y - (arch_top + r)
            if dy < 0 and ((x + 0.5 - cx) / r) ** 2 + (dy / r) ** 2 > 1:
                continue
            s.put(x, y, B0)
    for y in range(arch_top + 2, foot + 1):
        for x in range(dx0, dx0 + 16):
            r = 8
            dy = y - (arch_top + 2 + r)
            if dy < 0 and ((x + 0.5 - cx) / r) ** 2 + (dy / r) ** 2 > 1:
                continue
            c = W1 if y < arch_top + 10 else Y1 if y < foot - 5 else Y2
            if y >= arch_top + 10 and (x - dx0) in (0, 15):
                c = W2
            s.put(x, y, c)
    s.hline(dx0 - 1, dx0 + 16, foot, B2)  # the root sill
    s.hline(dx0 - 1, dx0 + 16, foot + 1, B0)
    # the Poke Ball plaque over the arch
    pcx, pcy = cx, arch_top - 7
    for x, y in disc(pcx, pcy, 6.5):
        s.put(x, y, B0)
    for x, y in disc(pcx, pcy, 5.5):
        s.put(x, y, R2 if y < pcy - 0.5 else WH)
    for x, y in disc(pcx - 1.8, pcy - 2.5, 1.6):
        s.put(x, y, R3)
    s.hline(pcx - 5, pcx + 4, int(pcy), B0)
    for x, y in disc(pcx, pcy, 2.2):
        s.put(x, y, B0)
    for x, y in disc(pcx, pcy, 1.2):
        s.put(x, y, WH)
    # red lanterns hanging either side of the door
    for side in (-1, 1):
        lx = int(cx + side * 16) - (1 if side < 0 else 0)
        s.vline(lx + 1, arch_top - 2, arch_top + 3, B0)
        s.rect(lx - 1, arch_top + 4, lx + 3, arch_top + 10, R2)
        s.rect(lx, arch_top + 5, lx + 2, arch_top + 9, Y2)
        s.vline(lx + 1, arch_top + 5, arch_top + 9, Y1)
        s.hline(lx - 1, lx + 3, arch_top + 4, R1)
        s.hline(lx - 1, lx + 3, arch_top + 10, R1)
        s.put(lx + 1, arch_top + 11, R1)
    # round windows up the trunk (rooms inside)
    round_window(s, cx - 15, 14, 3.5)
    round_window(s, cx + 14, 20, 3.5)
    # crown: big clumps of leaf over the trunk's top, moss hanging over the arch line
    crown = Sprite(160, 112, 80, 112 - 4 + 0)
    ccx = 80
    cy0 = 112 - 4 - foot  # the trunk's top in crown coordinates
    clumps = [(-46, cy0 - 6, 16), (46, cy0 - 6, 16), (-30, cy0 - 24, 18), (30, cy0 - 24, 18), (0, cy0 - 30, 20),
              (-20, cy0 - 4, 17), (20, cy0 - 4, 17), (0, cy0 - 10, 18)]
    for dx, dy, r in clumps:
        shade_clump(crown, ccx + dx, dy, r, LEAVES, rng, fleck=0.15)
    m = crown.a[:, :, 3] > 0
    crown.outline(L0)
    short, long_ = Sprite(crown.w, crown.h, crown.ax, crown.ay), Sprite(crown.w, crown.h, crown.ax, crown.ay)
    hang(short, long_, m, rng, every=(1, 2), length=(8, 18))
    return s, crown, short, long_


# ---------------------------------------------------------------- props
def fern(seed=1):
    """A clump of ferns, 16x16 (anchor: bottom centre)."""
    rng = random.Random(seed)
    s = Sprite(18, 16, 9, 15)
    for x, y in disc(9, 14, 7, 2):
        s.put(x, y, SH)
    for ang in (-150, -125, -100, -80, -55, -30):
        a = math.radians(ang + rng.uniform(-6, 6))
        ln = rng.uniform(8, 11)
        for i in range(int(ln)):
            t = i / ln
            x = 9 + math.cos(a) * i
            y = 14 + math.sin(a) * i + t * t * 4  # fronds droop at the tips
            s.put(x, y, L3 if i < ln * 0.6 else L4)
            if i % 2 == 0 and 1 < i < ln - 1:  # leaflets
                s.put(x + math.cos(a + 1.57), y + math.sin(a + 1.57), L2)
                s.put(x - math.cos(a + 1.57), y - math.sin(a + 1.57), L3)
    s.outline(L1)
    return s


def bush(seed=2, w=18, h=14, berries=None):
    """A round undergrowth shrub (anchor: bottom centre), optional berries / blossoms."""
    rng = random.Random(seed)
    s = Sprite(w + 2, h + 2, (w + 2) // 2, h)
    for x, y in disc((w + 2) / 2, h, w / 2, 2):
        s.put(x, y, SH)
    sub = Sprite(w + 2, h + 2)
    for dx, dy, r in ((-3, -1, 5.5), (3, -1, 5.5), (0, -4, 6)):
        shade_clump(sub, (w + 2) / 2 + dx, h - 6 + dy, r, LEAVES[1:], rng, fleck=0.2)
    sub.outline(L0)
    s.paste(sub, 0, 0)
    if berries:
        for _ in range(5):
            x, y = rng.randint(4, w - 3), rng.randint(3, h - 4)
            if s.get(x, y) not in (None, L0, SH):
                s.put(x, y, rng.choice(berries))
    return s


def flowers(seed=3, cols=(P2, V2, WH, Y2), n=7):
    """A loose patch of small wildflowers on the grass (walkable), 16x16 (anchor: centre)."""
    rng = random.Random(seed)
    s = Sprite(16, 16, 8, 8)
    for _ in range(n):
        x, y = rng.randint(2, 13), rng.randint(3, 13)
        c = rng.choice(cols)
        s.put(x, y + 1, L2)
        s.put(x, y, c)
        if rng.random() < 0.6:
            s.put(x + 1, y, c)
            s.put(x, y - 1, c)
            s.put(x + 1, y - 1, WH if c != WH else Y2)
    return s


def glow_bells(seed=4):
    """Glow-bells: pale cyan bell flowers on arching stems, lit from within (walkable), 16x16."""
    rng = random.Random(seed)
    s = Sprite(16, 16, 8, 8)
    for x, y in ((4, 11), (8, 13), (11, 10)):
        for k in range(5):
            s.put(x + (k > 2), y - k, L2)
    for x, y in ((3, 6), (7, 8), (10, 5), (12, 9), (5, 9)):
        s.put(x, y, C2)
        s.put(x + 1, y, C1)
        s.put(x, y + 1, C1)
        s.put(x + 1, y + 1, WH if rng.random() < 0.4 else C1)
    return s


def toadstools(seed=6, n=3, cap=(R1, R2), pale=False):
    """A little cluster of toadstools (walkable), 16x16 (anchor: centre)."""
    rng = random.Random(seed)
    s = Sprite(16, 16, 8, 8)
    spots = [(5, 11), (10, 9), (8, 13), (12, 13)][:n]
    for x, y in spots:
        big = rng.random() < 0.5
        s.vline(x, y - 1, y + 1, S3)
        s.put(x, y + 2, B0)
        c0, c1 = ((S2, WH) if pale else cap)
        w = 2 if big else 1
        s.hline(x - w, x + w, y - 2, c1)
        s.hline(x - w + 1, x + w - 1, y - 3, c1)
        s.put(x - w, y - 2, c0)
        s.put(x + w, y - 2, c0)
        if not pale:
            s.put(x, y - 3, WH)
        s.hline(x - w, x + w, y - 1, B0 if not pale else S1)
    return s


def fairy_ring(r=19, seed=8):
    """A fairy ring: a circle of pale, faintly glowing toadstools in a ring of darker grass. 48x48, anchor
    centre (one cell's middle), walkable."""
    rng = random.Random(seed)
    s = Sprite(48, 48, 24, 24)
    cx = cy = 24
    for x in range(48):
        for y in range(48):
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.15)
            if abs(d - r) < 2.5:
                s.put(x, y, SH if abs(d - r) < 1.5 else SH_D if (x + y) % 2 else SH)
    n = 13
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.12, 0.12)
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r / 1.15
        big = i % 2 == 0
        s.vline(x, y - 1, y, S3)
        s.hline(x - 1, x + 1, y + 1, SH_D)
        if big:
            s.hline(x - 2, x + 2, y - 2, S2)
            s.hline(x - 1, x + 1, y - 3, WH)
            s.hline(x - 1, x + 1, y - 2, C2)
            s.put(x, y - 4, WH)
        else:
            s.hline(x - 1, x + 1, y - 2, WH)
            s.put(x, y - 3, C2)
    for _ in range(5):  # a few motes of light inside
        a, d = rng.uniform(0, 6.28), rng.uniform(3, r - 6)
        s.put(cx + math.cos(a) * d, cy + math.sin(a) * d * 0.85, Y2)
    return s


def pepper_bed(w_cells=3, h_cells=2, seed=9):
    """A raised bed of pepper plants in tilled rows: dark soil, bushy plants hung with red and green peppers,
    a plank edging. Anchor: top-left of its cell box."""
    rng = random.Random(seed)
    W, H = w_cells * 16, h_cells * 16
    s = Sprite(W, H)
    s.rect(1, 2, W - 2, H - 3, B1)
    for y in range(2, H - 2, 4):  # furrows
        s.hline(2, W - 3, y + 2, B0)
        s.hline(2, W - 3, y, B2)
    s.rect(0, H - 3, W - 1, H - 2, W2)  # plank edging
    s.hline(0, W - 1, H - 2, W1)
    s.hline(0, W - 1, H - 1, B0)
    s.vline(0, 2, H - 2, W1)
    s.vline(W - 1, 2, H - 2, W1)
    s.hline(0, W - 1, 1, W3)
    for row in range(2):
        for i in range(w_cells * 2):
            x = 4 + i * 8 + (4 if row else 0) % 8
            y = 9 + row * 12
            if x > W - 4:
                continue
            for dx, dy in ((0, -5), (-3, -3), (3, -3), (-2, -1), (2, -1), (0, -2)):
                for xx, yy in disc(x + dx, y + dy, 2.2):
                    s.put(xx, yy, L3 if dy < -2 else L2)
            s.put(x - 3, y - 6, L4)
            s.put(x + 1, y - 7, L4)
            for _ in range(3):  # peppers hanging
                px, py = x + rng.randint(-3, 3), y + rng.randint(-4, 0)
                c = rng.choice((R2, R2, R1, L4))
                s.put(px, py, c)
                s.put(px, py + 1, R1 if c != L4 else L3)
    return s


def still_pool(seed=10):
    """A small still pool with a ring of mossy stones: the water is a mirror (pale sky, a moon's reflection,
    sparkles). 32x32, anchor top-left."""
    rng = random.Random(seed)
    s = Sprite(32, 32)
    cx, cy = 16, 16
    for x, y in disc(cx, cy, 14.5, 12.5):
        s.put(x, y, S1)
    for x, y in disc(cx, cy, 12, 10):
        d = math.hypot((x + 0.5 - cx) / 12, (y + 0.5 - cy) / 10)
        s.put(x, y, WA_D if d > 0.82 else WA if d > 0.45 else WA_L)
    for x, y in disc(cx + 3, cy - 2, 2.6):  # the moon's reflection
        s.put(x, y, WA_G)
    s.put(cx + 2, cy - 3, WH)
    for x, y in ((cx - 6, cy + 2), (cx - 3, cy - 5), (cx + 6, cy + 4)):
        s.put(x, y, WH)
    # rim stones: lumps round the edge, lit top-left, moss on some
    for i in range(14):
        a = 2 * math.pi * i / 14
        x, y = cx + math.cos(a) * 13, cy + math.sin(a) * 11
        for xx, yy in disc(x, y, 2.6, 2.2):
            s.put(xx, yy, S2)
        s.put(x - 1, y - 1, S3)
        if i % 3 == 0:
            s.put(x, y - 1, L3)
            s.put(x + 1, y - 1, L4)
    s.outline(B0)
    return s


def riddle_stone():
    """A standing stone, mossy, carved with a fox's flame-tail that glows faintly: the Delphoxite riddle.
    16x24, anchor bottom centre (it rises into the cell above)."""
    s = Sprite(16, 24, 8, 23)
    for x, y in disc(8, 22, 7, 2):
        s.put(x, y, SH)
    for y in range(3, 22):
        half = 5 if y > 6 else 5 - (6 - y) // 1.5
        for x in range(int(8 - half), int(8 + half)):
            f = (x - (8 - half)) / (2 * half)
            s.put(x, y, S3 if f < 0.3 else S2 if f < 0.7 else S1)
    s.outline(B0)
    for x, y in ((5, 5), (6, 4), (7, 4), (6, 6), (10, 7), (9, 8), (10, 9)):
        s.put(x, y, L3)
    for x, y in ((5, 6), (6, 5), (9, 7), (4, 18), (5, 19), (11, 17), (10, 19)):
        s.put(x, y, L4)
    # the carved flame-tail: an S-curve that ends in a flame, glowing warm
    for x, y in ((7, 16), (8, 15), (9, 14), (9, 13), (8, 12), (7, 11), (7, 10), (8, 9), (9, 9)):
        s.put(x, y, Y1)
    for x, y in ((9, 8), (10, 8), (10, 10)):
        s.put(x, y, R2)
    s.put(8, 8, Y2)
    return s


def mossy_log(seed=12):
    """A fallen log furred with moss, toadstools at one end, 32x16 (anchor top-left)."""
    rng = random.Random(seed)
    s = Sprite(32, 16)
    for x, y in disc(16, 13, 15, 2):
        s.put(x, y, SH)
    s.rect(3, 5, 27, 12, B2)
    s.hline(3, 27, 5, B3)
    s.hline(3, 27, 6, B3)
    s.hline(3, 27, 11, B1)
    s.hline(3, 27, 12, B0)
    for x in range(4, 27, 5):
        s.put(x, 8 + (x // 5) % 2, B1)
    for x, y in disc(28, 8.5, 3.5, 4):  # cut end, rings
        s.put(x, y, W4)
    for x, y in disc(28, 8.5, 1.5, 2):
        s.put(x, y, W3)
    s.outline(B0)
    for x in range(4, 26):  # moss on top
        if rng.random() < 0.7:
            s.put(x, 5, rng.choice((L3, L4, M2)))
        if rng.random() < 0.35:
            s.put(x, 4, rng.choice((L3, M2)))
    for x in (6, 9):
        s.put(x, 4, R2)
        s.put(x, 3, R2)
        s.put(x + 1, 4, WH)
    return s


def moss_mound(seed=13):
    """A low cushion of moss and creeping fern on the grass (walkable ground cover), 16x16."""
    rng = random.Random(seed)
    s = Sprite(16, 16, 8, 8)
    for x, y in disc(8, 9, 6.5, 4.5):
        if rng.random() < 0.85:
            s.put(x, y, rng.choice((L3, L3, L4, M2)) if y < 9 else rng.choice((L2, L3)))
    return s


# ---------------------------------------------------------------- preview
def preview(out):
    sheet = Image.new("RGBA", (420, 220), G + (255,))

    def put(sp, x, y):
        sheet.alpha_composite(sp.image(), (x - sp.ax, y - sp.ay))

    for i, seed in enumerate((3, 7)):
        b, m, l = moss_tree(seed)
        for sp in (b, m, l):
            put(sp, 30 + 56 * i, 48)
    trunk, crown, cm, cl = great_tree()
    put(crown, 200, 120)
    put(trunk, 200, 120)
    put(cm, 200, 120)
    put(cl, 200, 120)
    a = arbour()
    put(a, 270, 4)
    put(cottage(), 4, 130)
    put(cottage(6, 4, 2, herbalist=True), 90, 130)
    x = 280
    for sp in (fern(1), bush(2, berries=(P2, WH)), flowers(3), glow_bells(4), toadstools(6), moss_mound()):
        put(sp, x, 112)
        x += 20
    put(fairy_ring(), 300, 160)
    put(pepper_bed(), 340, 140)
    put(still_pool(), 340, 180)
    put(riddle_stone(), 390, 210)
    put(mossy_log(), 380, 110)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)


sketch_preview = preview   # the first sketches' sheet (not written any more; main() below writes hollow_preview.png)



# ======================================================================================================================
# THE PIECE LAYER (2026-10-12): the pieces hollow.py places, each drawn on its own canvas of 16 px cells in the
# footprint of art_requests/lutins_hollow.md (hollow_tileset.WANTED), registered with add() and packed by main() into
#     hollow.png              16 px cells, magenta (255, 0, 255) = clear: every piece is an OVERLAY on plain swamp grass
#     hollow.json             {"png", "pieces": {name: {x, y, w, h, doors, passable, empty, comment}}}
#     hollow_preview.png      the sheet on Ekat's grass, 3x
#     maps/00_hollow_art.png  the review sheet: every piece at 3x, a test glade at 3x, unique 8x8 tile counts
# The first sketches above (Sprite, moss_tree(), great_tree() ...) are kept for reference; nothing below calls them.
#
# Colour families (GBA-exact, <= 15 colours in every piece, checked by main()):
#     LEAF    LINK + LF1..LF5 leaf ramp, MS1..MS3 Spanish moss, BK1..BK3 bark, GSH shade on grass  (trees, understory)
#     TIMBER  INK, LF1..LF4 roof moss, MS1/MS2 mossy stone, BK1..BK3 timber, PLS/PLD plaster, GL1/GL2 warm window
#             (+ one accent: PK2, or BL1 for the Herbalist's sign)                             (cottages, Herbalist)
#     FAIRY   pinks PK1..PK3, violets VI1/VI2, WHT, gold GL1/GL2, teal TL1/TL2, mushroom red RD1/RD2, stems LF2..LF4
#     the gym and the hollow tree mix LEAF with FAIRY/TIMBER colours, still <= 15 each.
# Tile discipline: everything sits on the 8 px grid. Roofs, plaster, bark, moss curtains and footings are 8 px periodic
# textures fixed to the piece's own origin (every piece starts at x = 0), so their insides are the same tiles wherever
# they appear (the Herbalist's roof and walls are the cottages' tiles); the ring trees are mirror symmetric above the
# trunk and share their whole lower half (canopy base, moss beards, trunk, roots, undergrowth); the fairy ring, the
# pool and the gym are drawn on their left halves and mirrored; ground cover leaves most of its 8x8 quarters empty
# (free).
# ======================================================================================================================
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

KEY = (255, 0, 255)
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))

# ---------------------------------------------------------------- colours (multiples of 8: GBA-exact)
LINK = (40, 56, 40)                                   # leaf ink (Ekat's darkest cypress green)
LF1, LF2, LF3, LF4, LF5 = (48, 72, 56), (64, 96, 64), (80, 120, 72), (112, 152, 88), (160, 184, 104)
MS1, MS2, MS3 = (112, 128, 112), (152, 168, 144), (200, 208, 176)    # Spanish moss / mossy stone
INK = (48, 48, 40)                                    # bark and timber ink (Ekat's root ink)
BK1, BK2, BK3 = (88, 72, 64), (128, 104, 80), (168, 144, 112)
GSH = (96, 128, 88)                                   # shade on the grass (Ekat's turf line)
PLS, PLD = (232, 216, 176), (192, 176, 144)           # plaster
GL1, GL2 = (232, 168, 72), (248, 224, 136)            # warm light / gold
PK1, PK2, PK3 = (184, 72, 120), (232, 128, 168), (248, 200, 216)
VI1, VI2 = (112, 80, 160), (168, 136, 216)
WHT = (248, 248, 232)
TL1, TL2 = (72, 160, 168), (168, 232, 224)
RD1, RD2 = (168, 40, 48), (224, 80, 64)
BL1 = (56, 96, 168)
WA1, WA2, WA3 = (72, 112, 112), (96, 136, 136), (152, 192, 184)    # Ekat's pond teal, and its sky reflection


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
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def sprite(self, x0, y0, rows, pal, flip=False, behind=False):
        """Hand-placed pixels: one string per row, '.' clear; flip = mirrored; behind = only on clear pixels."""
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

    def edge(self, c, pixels, border=True):
        """Inner outline: every pixel of the set `pixels` with a 4-neighbour outside the set (or off the canvas when
        `border`) becomes `c`."""
        hits = []
        for x, y in pixels:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                off = not (0 <= nx < self.W and 0 <= ny < self.H)
                if (off and border) or (not off and (nx, ny) not in pixels):
                    hits.append((x, y))
                    break
        for x, y in hits:
            self.put(x, y, c)

    def outline(self, c, skip=()):
        """Outer outline: clear pixels touching a drawn one (4-neighbours) become `c`."""
        hits = [(x, y) for y in range(self.H) for x in range(self.W)
                if self.px[y][x] == KEY and any(self.get(x + dx, y + dy) not in (KEY, c) + tuple(skip)
                                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in hits:
            self.px[y][x] = c

    def remap(self, table):
        """Swap colours (to keep a piece inside its 15)."""
        for row in self.px:
            for i, c in enumerate(row):
                if c in table:
                    row[i] = table[c]

    def copy_rows(self, other, y0, y1):
        for y in range(y0, y1 + 1):
            self.px[y] = list(other.px[y])

    def flipped(self):
        out = Art(self.w, self.h)
        out.px = [row[::-1] for row in self.px]
        return out

    def colours(self):
        return {c for row in self.px for c in row if c != KEY}

    def image(self):
        im = Image.new("RGB", (self.W, self.H))
        im.putdata([c for row in self.px for c in row])
        return im


PIECES = {}   # name -> (Art, meta)


def add(name, art, comment, doors=(), walk=()):
    """Register a piece (the camp/dry-country index format). `empty`: cells with nothing drawn (no tile needed)."""
    empty = [[i, j] for j in range(art.h) for i in range(art.w)
             if all(art.px[j * 16 + y][i * 16 + x] == KEY for y in range(16) for x in range(16))]
    PIECES[name] = (art, {"w": art.w, "h": art.h, "comment": comment, "doors": [list(d) for d in doors],
                          "passable": [list(c) for c in walk], "empty": empty})


# ---------------------------------------------------------------- foliage: lobed crowns (the dry-country trees' way)
def leafy(a, lobes, tones, ink, light=(-0.5, -0.86), border=True, seed=0, gy=None, cell=(7, 6), bias=0.0,
          crease=True):
    """A crown of leaf lobes (cx, cy, rx, ry) listed back to front (later lobes are nearer and overlap). Two scales of
    light, both from `light` (top-left): each lobe is lit on its upper-left and shaded below (a dark rim where it sits
    over the lobe behind), and its leaves are small clusters on a staggered lattice (`cell` px), each a little brighter
    on its upper-left rim and darker on its lower-right, so the crown reads as leaf clumps, not smooth pillows. `gy`:
    the crown's base, toward which it darkens. An ink outline round the union (`border`: the canvas edge counts as
    outside). tones = (deep, shade, mid, light, high). Returns the pixel set."""
    owner = {}
    for i, (cx, cy, rx, ry) in enumerate(lobes):
        for x, y in ell(cx, cy, rx, ry):
            if 0 <= x < a.W and 0 <= y < a.H:
                owner[(x, y)] = i
    top = min(y for _, y in owner) if owner else 0
    base = gy if gy is not None else (max(y for _, y in owner) if owner else 1)
    sx, sy = cell
    for (x, y), i in owner.items():
        cx, cy, rx, ry = lobes[i]
        nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        r2 = nx * nx + ny * ny
        lum = nx * light[0] + ny * light[1]
        v = 1.75 + 1.45 * lum - 1.5 * max(0.0, (y - top) / max(1, base - top) - 0.45) + bias
        # the leaf cluster this pixel belongs to (nearest lattice point)
        row = round((y + 0.5) / sy)
        best = None
        for j in (row - 1, row, row + 1):
            off = (sx / 2) * (j % 2)
            col = round((x + 0.5 - off) / sx)
            for k in (col - 1, col, col + 1):
                px_, py_ = k * sx + off, j * sy
                d = (x + 0.5 - px_) ** 2 + ((y + 0.5 - py_) * 1.15) ** 2
                if best is None or d < best[0]:
                    best = (d, px_, py_)
        _, px_, py_ = best
        jx, jy = _hh(int(px_ * 2), int(py_ * 2), 7 + seed) - 0.5, _hh(int(px_ * 2), int(py_ * 2), 9 + seed) - 0.5
        ux, uy = (x + 0.5 - px_ - jx) / (sx * 0.55), (y + 0.5 - py_ - jy) / (sy * 0.55)
        loc = ux * light[0] + uy * light[1]
        if loc > 0.6:
            v += 0.75
        elif loc < -0.65:
            v -= 0.75
        if r2 > 0.8 and lum < -0.1:
            v = min(v, 0.6)
        if crease and owner.get((x, y + 1), -1) > i:
            v = min(v - 1.0, 1.0)
        k = max(0, min(4, int(math.floor(v + 0.5))))
        a.put(x, y, tones[k])
    a.edge(ink, set(owner), border=border)
    return set(owner)


# ---------------------------------------------------------------- Spanish moss
BEARDS = {   # hand-placed beards of Spanish moss: 3 = MS3 (lit), 2 = MS2, 1 = MS1 (shade)
    "long": [".332..",
             "23332.",
             "233221",
             "12322.",
             ".2321.",
             ".1222.",
             "..221.",
             ".122..",
             "..21..",
             "..2...",
             ".12...",
             "..2...",
             "..1..."],
    "mid": [".32..",
            "2332.",
            "2322.",
            "1232.",
            ".221.",
            ".12..",
            "..2..",
            ".21..",
            "..1.."],
    "short": [".32.",
              "2332",
              "1221",
              ".22.",
              ".21.",
              "..1."],
    "wisp": ["32",
             "22",
             "21",
             ".1"],
}
MOSS_PAL = {"3": MS3, "2": MS2, "1": MS1}


MOSS_DARK = {"3": MS2, "2": MS1, "1": LF2}       # moss in the crown's shade (the ring trees)


def beard(a, x, y, kind, flip=False, pal=None):
    a.sprite(x, y, BEARDS[kind], pal or MOSS_PAL, flip=flip)


# ---------------------------------------------------------------- the ring trees
TREE_TONES = (LF1, LF2, LF3, LF4, LF5)
# the lower crown, the same in all three trees (so rows 24..47 are shared tiles), back to front
TREE_LOWER = [(16, 20, 8, 6), (6.5, 23, 6.5, 6.5), (25, 22, 8, 6.5), (13, 27, 8, 6), (5.5, 30.5, 5.5, 4.5),
              (22, 31, 7.5, 5)]
TREE_UPPER = {   # the crown above it (left half; mirrored): the trees' silhouettes
    "tree_a": [(24, 8.5, 10, 7.5), (13, 11, 8, 6.5), (6.5, 16, 6.5, 5.5), (20, 14, 7, 5.5)],        # a round dome
    "tree_b": [(15, 8, 9, 7), (6.5, 14, 6.5, 6), (24, 12, 7, 6), (16, 15, 9, 6)],                # broad, two-humped
    "tree_c": [(24, 7.5, 7, 7), (17, 10, 7, 6), (9, 14, 7, 6), (6.5, 17, 6.5, 5), (20, 15, 8, 6)],  # tall, in bloom
}


def ground_shade(a, cx, cy, rx, ry):
    for x, y in ell(cx, cy, rx, ry):
        if a.clear_at(x, y):
            a.put(x, y, GSH)


def understory(a, x0, y0, flip=False):
    """A low leafy shrub at a tree's foot (fills the bottom corners of the trunk row so the ring reads dense)."""
    a.sprite(x0, y0, ["....kkkk......",
                      "..kklhlmk.....",
                      ".klhlmmmmkkk..",
                      "kllmmmdmklhmk.",
                      "klmmdmddkmmmdk",
                      "kmmddmdkdmmddk",
                      ".kdddkkkddddk.",
                      "..kkk...kkkk.."],
             {"k": LINK, "h": LF5, "l": LF4, "m": LF3, "d": LF2}, flip=flip)


def trunk_row(a, cx=24, top=26, foot=44):
    """The trunk (lit from the left, not mirrored): a column of furrowed bark, a short root flare with root fingers
    reaching onto the grass. Drawn behind what is already there (crown, moss, undergrowth)."""
    pal = {"k": LINK, "1": BK1, "2": BK2, "3": BK3}
    rows = []
    for y in range(top, foot + 1):
        flare = max(0, y - (foot - 4))
        x0, x1 = cx - 5 - flare, cx + 4 + flare
        line = ""
        for x in range(x0, x1 + 1):
            k, w = x - x0, x1 - x0
            c = "3" if k <= 1 else "2" if k < w * 0.6 else "1"
            if (x - cx) % 4 == 1 and 1 < k < w - 1 and (y * 3 + x) % 8 != 0:
                c = "1" if k < w * 0.6 else "k"
            if x in (x0, x1):
                c = "k"
            line += c
        rows.append((x0, y, line))
    for x0, y, line in rows:
        for i, ch in enumerate(line):
            if a.clear_at(x0 + i, y) or a.get(x0 + i, y) == GSH:
                a.put(x0 + i, y, pal[ch])
    # root fingers onto the grass
    a.sprite(cx - 14, foot - 3, ["......kk",
                                 "....kk32",
                                 "..kk322k",
                                 "kk3222k.",
                                 ".kkkkk.."], pal, behind=True)
    a.sprite(cx + 7, foot - 3, ["kk......",
                                "21kk....",
                                "k211kk..",
                                ".k1111kk",
                                "..kkkkk."], pal, behind=True)
    a.hline(cx - 9, cx + 8, foot + 1, LINK)


def ring_tree(name):
    a = Art(3, 3)
    ground_shade(a, 24, 44.5, 18, 3.4)
    understory(a, 0, 38)
    leafy(a, TREE_UPPER[name] + TREE_LOWER, TREE_TONES, LINK)
    a.mirror()
    trunk_row(a)
    # Spanish moss hanging from the crown's underside, over the trunk and the undergrowth
    # (few and uneven, in the darker moss, so a row of trees doesn't hang an even comb of pale strands)
    for x, y, kind, flip in ((6, 33, "long", False), (11, 34, "wisp", False), (27, 35, "short", True),
                             (38, 33, "mid", True)):
        beard(a, x, y, kind, flip, MOSS_DARK)
    return a


def ring_trees():
    a = ring_tree("tree_a")
    b, c = ring_tree("tree_b"), ring_tree("tree_c")
    for t in (b, c):
        t.copy_rows(a, 24, 47)
    # tree_c: a flowering vine through its crown
    for x, y in ((14, 7), (30, 6), (9, 13), (37, 14), (22, 3), (24, 12), (17, 17), (32, 19)):
        c.sprite(x, y, [".p.", "pPp", ".q."], {"p": PK3, "P": PK2, "q": LF2})
    return a, b, c


def small_tree():
    """tree_s, 2x2: a young live oak, the same leaves and moss as the ring trees."""
    a = Art(2, 2)
    ground_shade(a, 16, 29, 11, 2.6)
    leafy(a, [(16, 7.5, 9, 7), (8, 11, 7, 6), (11, 17, 8, 5.5), (16, 19, 7, 4.5)], TREE_TONES, LINK)
    a.mirror()
    pal = {"k": LINK, "1": BK1, "2": BK2, "3": BK3}
    a.sprite(11, 21, ["..k3221k..",
                      "..k3221k..",
                      "..k3121k..",
                      "..k3221k..",
                      ".k32221k..",
                      "k3k2221k1k",
                      "kk.kkkkkkk"], pal, behind=True)
    for x, y, kind, flip in ((6, 20, "short", False), (11, 22, "wisp", False), (21, 21, "mid", True)):
        beard(a, x, y, kind, flip)
    return a


def thicket(variant):
    """thicket_a/_b, 1x1: dense dark leaves filling the cracks between the ring's trunks."""
    a = Art(1, 1)
    ground_shade(a, 8, 14.5, 7.5, 1.6)
    if variant == "a":
        leafy(a, [(8, 6, 6.5, 5.5), (4, 10, 4, 4.5), (8, 11, 5, 4)], TREE_TONES, LINK, cell=(5, 5), bias=-0.2)
        a.mirror()
    else:
        leafy(a, [(6, 6, 5.5, 5), (11, 7, 5, 5), (4, 11, 4, 4), (10, 11.5, 5.5, 4)], TREE_TONES, LINK,
              cell=(5, 5), bias=-0.2, seed=3)
        beard(a, 9, 12, "wisp")
    return a


def shrub_piece(variant):
    """bush_a/_b, 1x1 understory shrubs, lighter than the thickets: bush_a in white blossom, bush_b a yaupon with red
    berries."""
    a = Art(1, 1)
    ground_shade(a, 8, 14, 6.5, 1.6)
    if variant == "a":
        leafy(a, [(8, 8, 5.5, 4.5), (5, 11, 4, 3.5), (11, 11, 4, 3.5)], TREE_TONES, LINK, cell=(4, 4), bias=0.35)
        a.mirror()
        for x, y in ((5, 6), (10, 5), (3, 10), (8, 9), (12, 10)):
            a.sprite(x, y, [".w.", "wqw"], {"w": WHT, "q": MS3})
    else:
        leafy(a, [(7, 8, 5, 4.5), (11, 9, 4, 4), (5, 11.5, 4, 3.5), (10, 12, 4.5, 3)], TREE_TONES, LINK,
              cell=(4, 4), bias=0.3, seed=5)
        for x, y in ((5, 7), (9, 6), (12, 9), (7, 11), (11, 12), (4, 10)):
            a.sprite(x, y, ["r", "d"], {"r": RD2, "d": RD1})
    return a


def frond(a, bx, by, ang, n, curl, w0=1.5):
    """One fern frond from (bx, by), laid over the fronds before it (Ekat's leafy plants' way: no hard outline): a
    tapered leaf along a curving midrib (`ang` degrees, 0 = east, -90 = up, bending `curl` degrees a pixel), widest a
    third of the way out; mid green with a lit midrib and a pale tip, its upper edge light, its lower edge notched
    dark (the leaflets), and a dark line where it lies over the frond behind or over the grass below it."""
    x, y, t = float(bx) + 0.5, float(by) + 0.5, math.radians(ang)
    cells = {}
    steps = n * 3
    for i in range(steps):
        f = i / (steps - 1)
        half = w0 * (f / 0.3 if f < 0.3 else max(0.0, (1 - f) / 0.7) ** 0.8) + 0.25
        nx, ny = -math.sin(t), math.cos(t)
        if ny < 0:
            nx, ny = -nx, -ny
        for k in range(-int(half * 3), int(half * 3) + 1):
            d = k / 3
            p = (int(math.floor(x + nx * d)), int(math.floor(y + ny * d)))
            old = cells.get(p)
            if old is None or abs(d) < abs(old[0]):
                cells[p] = (d, f, half)
        x += math.cos(t) / 3
        y += math.sin(t) / 3
        t += math.radians(curl) / 3
    for (px, py), (d, f, half) in cells.items():
        if abs(d) < 0.34:
            c = LF5 if f > 0.82 else LF4 if f > 0.3 else LF3
        elif d < 0:
            c = LF3 if d < -half + 0.6 and f > 0.2 else LF2
        else:
            c = (LINK if (px + py) % 2 else LF1) if d > half - 0.6 else LF2
        a.put(px, py, c)
    for (px, py), (d, f, half) in cells.items():   # a dark line below the frond where it lies over something
        q = (px, py + 1)
        if q not in cells and d >= 0 and f > 0.15 and f < 0.92:
            a.put(*q, LINK if not a.clear_at(*q) and a.get(*q) != GSH else LF1)


FERNS = {   # (base x, base y, [(angle, length, curl)]) back to front: three different clumps, off the cell's centre.
    # Angles in screen degrees (-90 = up); a frond on the left arches over and droops with a negative curl.
    "fern_a": (7, 13, [(-150, 8, -9), (-30, 8, 9), (-118, 9, -6), (-62, 9, 6), (-90, 9, 1)]),
    "fern_b": (9, 12, [(-155, 7, -10), (-25, 7, 10), (-108, 9, -5), (-70, 8, 6)]),
    "fern_c": (6, 13, [(-150, 7, -10), (-35, 8, 9), (-112, 9, -5), (-75, 9, 4)]),
}


def fern_piece(name):
    a = Art(1, 1)
    bx, by, fronds = FERNS[name]
    for x, y in ell(bx + 0.5, by + 1.3, 5, 1.5):
        a.put(x, y, GSH)
    for ang, n, curl in fronds:
        frond(a, bx, by, ang, n, curl)
    a.put(bx, by, LF1)
    return a


GROUND = {"k": LF1, "d": LF2, "m": LF3, "l": LF4, "h": LF5, "2": MS2, "3": MS3, "s": GSH}


def moss_mound_piece():
    """A low cushion of moss on the grass, pale grey-green tufts on its lit side, and a sprig of new fern (walkable)."""
    a = Art(1, 1)
    a.sprite(1, 7, ["......ss......",
                    "....dmmmd.....",
                    "..dl32lmmd.dd.",
                    ".dl332lmmmdlmd",
                    "dl3llmmmmdmmmd",
                    "dmlmmmdmmddmdk",
                    "skdddkdddkddks",
                    ".sskkkskkksss."], GROUND)
    a.sprite(9, 3, [".l.l", "lm.m", ".dm.", "..d."], GROUND)
    return a


FLOWER = [".a.",
          "acb",
          ".b."]
BLOOMS = {   # name: (light petal, dark petal, eye, [(x, y) flowers], [(x, y) leaf pairs])
    "bloom_pink": (PK3, PK2, GL2, [(2, 2), (7, 4), (11, 1), (4, 9), (10, 9), (13, 6), (7, 12)],
                   [(3, 5), (8, 7), (12, 4), (5, 12), (11, 12)]),
    "bloom_violet": (VI2, VI1, GL2, [(1, 6), (5, 2), (9, 6), (12, 2), (4, 11), (11, 11)],
                     [(2, 9), (6, 5), (10, 9), (13, 5), (5, 14)]),
    "bloom_white": (WHT, MS3, GL1, [(3, 3), (8, 1), (12, 5), (6, 7), (2, 11), (9, 11), (13, 12)],
                    [(4, 6), (7, 10), (13, 8), (3, 14), (10, 14)]),
    "bloom_gold": (GL2, GL1, BK2, [(2, 4), (6, 1), (10, 3), (13, 8), (5, 9), (9, 12), (1, 12)],
                   [(3, 7), (7, 4), (11, 6), (6, 12), (2, 15)]),
}


def bloom(name):
    """A drift of small wildflowers in the grass (walkable): four-petalled, lit upper-left, a bright eye, leaves."""
    a = Art(1, 1)
    hi, lo, eye, flowers, leaves = BLOOMS[name]
    for x, y in leaves:
        a.sprite(x - 1, y, ["m.d", ".d."], GROUND)
    for x, y in flowers:
        a.sprite(x - 1, y - 1, FLOWER, {"a": hi, "b": lo, "c": eye})
        if a.clear_at(x, y + 2):
            a.put(x, y + 2, LF2)
    return a


def glowbell():
    """Glow-bells: three arching stems from one root, each hung with a pale cyan bell lit from inside, motes of light
    (walkable)."""
    a = Art(1, 1)
    for x, y in ell(7.5, 13.6, 3.5, 1.2):
        a.put(x, y, GSH)
    stems = [[(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8), (7, 7), (8, 6), (8, 5), (9, 4), (10, 4), (11, 5)],
             [(6, 12), (5, 11), (4, 10), (4, 9), (3, 8), (3, 7), (2, 6)],
             [(8, 12), (9, 11), (10, 10), (11, 10), (12, 10), (13, 11)]]
    for pts in stems:
        for i, (x, y) in enumerate(pts):
            a.put(x, y, LF2 if i < 3 else LF3)
    bell = ["ttt", "twT", "T.T"]
    pal = {"t": TL2, "T": TL1, "w": WHT}
    for x, y in ((10, 6), (1, 7), (12, 12)):
        a.sprite(x, y, bell, pal)
    a.sprite(5, 12, ["d.", ".k"], {"d": LF3, "k": LF1})
    a.sprite(8, 12, [".m", "k."], {"m": LF3, "k": LF1})
    for x, y in ((5, 3), (13, 2), (2, 12)):
        a.put(x, y, GL2)
    return a


TOAD_PAL = {"k": LINK, "R": RD2, "r": RD1, "w": WHT, "S": MS3, "s": GSH}


def toadstool(kind):
    """A little cluster of toadstools (walkable): red with white spots, or pale ones glowing faintly."""
    a = Art(1, 1)
    big = ["..kkkk..",
           ".kwRRRk.",
           "kRRRwRrk",
           "krRrrrrk",
           ".kkkkkk.",
           "...wS...",
           "...wS...",
           "..ssss.."]
    small = [".kkk.",
             "kRwRk",
             "krrrk",
             ".kkk.",
             "..w..",
             ".sss."]
    tiny = [".kk.", "kRRk", ".wS.", ".ss."]
    if kind == "pale":
        pal = dict(TOAD_PAL, R=WHT, r=VI2, w=PK3, S=MS3)
        pal["k"] = VI1
    else:
        pal = TOAD_PAL
    a.sprite(1, 5, big, pal)
    a.sprite(9, 1, small, pal)
    a.sprite(10, 10, tiny, pal)
    if kind == "pale":
        for x, y in ((8, 4), (13, 8), (2, 3)):
            a.put(x, y, TL2)
        for (x, y) in ((4, 10), (5, 10), (12, 13), (11, 4)):   # the faint glow under the caps
            a.put(x, y, TL2)
    return a


# ---------------------------------------------------------------- fairy details
def fairy_ring_piece():
    """A fairy ring, 3x3, all walkable: a ring of lusher, darker grass with small pale toadstools standing on it, a few
    motes of light inside. Drawn on the left half and mirrored."""
    a = Art(3, 3)
    cx, cy, rx, ry = 24.0, 24.5, 18.0, 15.5
    for y in range(48):
        for x in range(24):
            d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry)
            if abs(d - 1) * min(rx, ry) < 1.0:
                a.put(x, y, GSH)
            elif abs(d - 1) * min(rx, ry) < 1.9 and (x + 2 * y) % 5 == 0:
                a.put(x, y, GSH)       # tufts of the lusher grass either side of the ring
    big = [".kkk.", "kwWpk", "kppvk", ".kSk.", "..s.."]
    small = [".kk.", "kwpk", ".Sk.", "..s."]
    pal = {"k": VI1, "w": WHT, "W": WHT, "p": PK3, "v": VI2, "S": WHT, "s": TL2}
    for i, deg in enumerate((270, 240, 212, 182, 152, 122, 90)):
        t = math.radians(deg)
        x, y = cx + rx * math.cos(t), cy + ry * math.sin(t)
        st = big if i % 2 == 0 else small
        w = len(st[0])
        x0 = int(round(x - w / 2))
        if deg in (270, 90):
            x0 = 24 - w + 2 if w == 5 else 22   # straddles the mirror line: drawn so the mirror completes it
        a.sprite(x0, int(round(y)) - len(st) + 2, st, pal)
    for x, y in ((14, 19), (19, 28), (11, 26)):
        a.put(x, y, GL2)
    a.put(20, 15, TL2)
    a.mirror()
    return a


def pool():
    """A small still pool in a ring of mossy stones (2x2, blocking): its water a mirror, the pale sky and the moon
    reflected in it."""
    a = Art(2, 2)
    cx, cy = 16.0, 16.5
    for x, y in ell(cx, cy + 1.5, 15.5, 12.5):
        a.put(x, y, GSH)
    for x, y in ell(cx, cy, 12, 9.5):
        d = math.hypot((x + 0.5 - cx) / 12, (y + 0.5 - cy) / 9.5)
        c = WA2
        if y + 0.5 < cy - 9.5 * 0.35 and d > 0.62:
            c = WA1                      # the far rim's shadow on the water
        elif ((x + 0.5 - cx) / 8.5) ** 2 + ((y + 0.5 - cy - 1) / 3.2) ** 2 <= 1:
            c = WA3                      # the pale sky
        a.put(x, y, c)
    stones = []
    for i in range(16):
        t = 2 * math.pi * (i + 0.5) / 16
        stones.append((cx + 13.3 * math.cos(t), cy + 10.8 * math.sin(t), 3.3 if i % 3 else 2.8, 2.6 if i % 2 else 2.3))
    stones.sort(key=lambda s_: s_[1])
    for sx, sy, rx, ry in stones:
        for x, y in ell(sx, sy, rx, ry):
            if x >= 16:
                continue
            nx, ny = (x + 0.5 - sx) / rx, (y + 0.5 - sy) / ry
            lum = -0.6 * nx - 0.8 * ny
            a.put(x, y, MS3 if lum > 0.55 else MS2 if lum > -0.25 else MS1)
        if sy < cy:
            a.put(int(sx) - 1, int(sy - ry) + 1, LF4)
            a.put(int(sx), int(sy - ry) + 1, LF3)
    a.mirror()
    stone_px = {(x, y) for y in range(a.H) for x in range(a.W) if a.get(x, y) in (MS1, MS2, MS3, LF3, LF4)}
    a.edge(INK, stone_px, border=False)
    # the reflection: a moon, a glint, ripples (not mirrored: lit from the upper left)
    a.sprite(9, 12, [".ww.", "w..w", "w...", ".ww."], {"w": WHT})
    for x, y in ((19, 17), (20, 17), (22, 20), (13, 21), (14, 21)):
        a.put(x, y, WHT if (x + y) % 2 else WA3)
    return a


PEPPER = ["...klk.....",
          "..klmmk.k..",
          ".kllmrmklk.",
          "kllmmRmmmmk",
          "kmmrmmmrmdk",
          "kmmRmdmRddk",
          "kdmmdrdddk.",
          ".kddkRddk..",
          "..kk.k.k..."]


def pepper_bed_piece():
    """A raised bed of pepper plants, 3x2 (blocking), that tiles east-west: plank sides, tilled rows, bushy plants
    hung with red peppers. Each end is half of a post, so two beds side by side share one whole post."""
    a = Art(3, 2)
    W = a.W
    a.hline(1, W - 2, 30, GSH)
    a.rect(0, 5, W - 1, 7, BK2)          # the back board
    a.hline(0, W - 1, 4, INK)
    a.hline(0, W - 1, 5, BK3)
    for y in range(8, 26):               # tilled soil, furrows every 4 px
        for x in range(W):
            a.put(x, y, INK if y % 4 == 3 else BK1)
    for x in range(1, W, 6):
        a.put(x, 9 + (x // 6) % 3 * 4, BK2)
    a.hline(0, W - 1, 26, BK3)           # the front board
    a.rect(0, 27, W - 1, 28, BK2)
    a.hline(0, W - 1, 29, INK)
    for x in range(4, W, 8):
        a.put(x, 28, BK1)                # nail heads
    pal = {"k": LINK, "l": LF4, "m": LF3, "d": LF2, "r": RD2, "R": RD1}
    for x0, y0 in [(8 + 16 * k - 5, 4) for k in range(3)] + [(16 * k - 5, 14) for k in range(4)]:
        a.sprite(x0, y0, PEPPER, pal)
    # the end posts: half each (a whole post where two beds meet)
    for y in range(3, 30):
        a.put(0, y, BK2)
        a.put(1, y, INK)
        a.put(W - 2, y, INK)
        a.put(W - 1, y, BK3)
    a.hline(0, 1, 2, INK)
    a.hline(W - 2, W - 1, 2, INK)
    a.put(W - 1, 3, BK3)
    return a


def riddle_stone_piece():
    """The riddle stone, 1x2 (blocking): a mossy standing stone carved with a fox's curling flame-tail that glows."""
    a = Art(1, 2)
    for x, y in ell(8, 29.5, 7, 1.8):
        a.put(x, y, GSH)
    for y in range(5, 30):
        half = 5.0 if y > 10 else 5.0 - (10 - y) ** 1.6 * 0.18
        x0, x1 = int(round(8 - half)), int(round(8 + half)) - 1
        for x in range(x0, x1 + 1):
            f = (x - x0) / max(1, x1 - x0)
            a.put(x, y, MS3 if f < 0.25 else MS2 if f < 0.72 else MS1)
    px = {(x, y) for y in range(a.H) for x in range(a.W) if a.get(x, y) in (MS1, MS2, MS3)}
    a.edge(INK, px, border=False)
    a.sprite(4, 4, ["..kk..",
                    ".klmk.",
                    "kllmmk",
                    "km..mk",
                    "m....d",
                    ".....d"], {"k": LF2, "l": LF4, "m": LF3, "d": LF2}, behind=False)
    a.put(4, 7, MS3)
    for x, y in ((3, 25), (4, 26), (11, 24), (10, 26), (4, 13)):
        a.put(x, y, LF3)
    a.sprite(5, 11, ["..gG.",
                     ".g..g",
                     ".G...",
                     "..gg.",
                     "....g",
                     "...gG",
                     ".gg..",
                     "g....",
                     ".G..."], {"g": GL2, "G": GL1})
    a.put(8, 10, RD2)
    a.put(9, 10, GL2)
    return a


def mossy_log_piece():
    """A fallen log furred with moss, 2x1 (blocking): a cut end with rings, a bracket fungus, two toadstools."""
    a = Art(2, 1)
    for x, y in ell(16, 13.5, 14.5, 2):
        a.put(x, y, GSH)
    for y in range(5, 13):
        for x in range(2, 28):
            c = BK3 if y <= 6 else BK2 if y <= 9 else BK1
            if (x * 3 + y * 5) % 11 == 0 and 6 < y < 12:
                c = BK1 if c != BK1 else INK
            a.put(x, y, c)
    for x, y in ell(27.5, 8.5, 2.6, 4.2):
        a.put(x, y, BK3)
    for x, y in ell(27.5, 8.5, 1.4, 2.4):
        a.put(x, y, PLD)
    a.put(27, 8, BK2)
    px = {(x, y) for y in range(16) for x in range(32) if a.get(x, y) not in (KEY, GSH)}
    a.edge(LINK, px, border=False)
    for x in range(3, 25):                # moss along the top
        a.put(x, 5, LF4 if x % 3 else MS3)
        a.put(x, 4, LF3 if x % 4 else KEY)
        if x % 5 in (1, 2):
            a.put(x, 6, LF3)
    a.sprite(17, 9, ["ppp", ".pP"], {"p": PLD, "P": BK2})   # bracket fungus
    a.sprite(5, 1, [".kk.", "kRRk", ".ww."], {"k": LINK, "R": RD2, "w": WHT})
    a.sprite(9, 2, ["kk", "RR", "w."], {"k": LINK, "R": RD2, "w": WHT})
    return a


# ---------------------------------------------------------------- buildings: shared parts
def _cushions():
    """An 8x8 wrapping texture of moss cushions (tone indices 0 crease .. 4 tuft): rounded clumps on a staggered
    lattice (8 px across, 4 down, every other row offset 4), each lit on its upper left, a dark crease where the clump
    in front overlaps it. Every roof cell that is all cushion is the same tile."""
    centres = [(8 * i + 4 * (j % 2) + 4, 4 * j + 2) for j in range(-3, 14) for i in range(-2, 7)]
    owner = {}
    for n, (cx, cy) in enumerate(sorted(centres, key=lambda c: (c[1], c[0]))):
        for x, y in ell(cx, cy, 4.3, 3.9):
            owner[(x, y)] = (n, cx, cy)
    tex = []
    for y in range(16, 24):
        row = []
        for x in range(16, 24):
            n, cx, cy = owner[(x, y)]
            nx, ny = (x + 0.5 - cx) / 4.3, (y + 0.5 - cy) / 3.9
            lum = -0.5 * nx - 0.86 * ny
            t = 4 if lum > 0.62 and nx * nx + ny * ny > 0.3 else 3 if lum > 0.15 else 2 if lum > -0.45 else 1
            if owner.get((x, y + 1), (n,))[0] > n:
                t = 0
            row.append(t)
        tex.append(row)
    return tex


CUSHION = _cushions()
ROOF_BANDS = [   # tone 0..4 -> colour, by 8 px band from the roof's top down: lit near the crown, darker to the eave
    (LF2, LF3, LF4, LF4, MS2),
    (LF1, LF2, LF3, LF4, LF4),
    (LF1, LF2, LF3, LF3, LF4),
    (LF1, LF1, LF2, LF3, LF3),
]


def roof_colour(x, y, band):
    return ROOF_BANDS[min(band, len(ROOF_BANDS) - 1)][CUSHION[y % 8][x % 8]]


def drip(x):
    """The eave's scallops: one rounded drip every 8 px (so eave cells repeat)."""
    return (0, 1, 1, 2, 2, 1, 1, 0)[x % 8]


def cushion_roof(a, x0, x1, top, eave, corner=11):
    """A thick, rounded moss roof over x0..x1: the cushion texture in bands, the top corners rounded, the eave a rolled
    lip that sags in drips every 8 px, an ink outline. Returns the eave's bottom row per x."""
    bottoms = {}
    for x in range(x0, x1 + 1):
        u = min(x - x0, x1 - x)
        t = top + (corner - math.sqrt(max(0.0, corner ** 2 - (corner - u) ** 2)) if u < corner else 0)
        t = int(round(t))
        b = eave + drip(x) + (2 if u < 3 else 1 if u < 8 else 0)
        bottoms[x] = b
        for y in range(t, b + 1):
            band = (y - top) // 8
            c = roof_colour(x, y, band)
            if y >= b - 4:   # the rolled lip of the eave
                c = (LF4, LF3, LF2, LF2, LF1)[min(4, y - (b - 4))]
                if y == b - 4 and x % 8 in (0, 7):
                    c = LF3
            a.put(x, y, c)
    px = {(x, y) for x in range(x0, x1 + 1) for y in range(a.H) if a.get(x, y) in (LF1, LF2, LF3, LF4, MS2)}
    a.edge(INK, px)
    return bottoms


def plaster_wall(a, x0, x1, y0, y1, posts):
    """Plaster between dark timbers: posts (2 px) at `posts`, a top plate, a mid rail, the eave's shade at the top."""
    a.rect(x0, y0, x1, y1, PLS)
    a.hline(x0, x1, y0, INK)
    for px in posts:
        a.vline(px, y0, y1, BK2)
        a.vline(px + 1, y0, y1, BK1)
    a.hline(x0, x1, y1 - 7, BK2)
    a.hline(x0, x1, y1 - 6, BK1)


def footing(a, x0, x1, y0):
    """A low footing of mossy stones (4 rows), 8 px periodic, an ink line under it."""
    for y in range(y0, y0 + 4):
        for x in range(x0, x1 + 1):
            k = (x + (4 if (y - y0) >= 2 else 0)) % 8
            c = MS2 if (y - y0) % 2 == 0 else MS1
            if k == 0:
                c = INK
            elif k == 1 and (y - y0) % 2 == 0:
                c = PLS if x % 16 < 8 else MS2
            a.put(x, y, c)
    a.hline(x0, x1, y0, INK)
    for x in range(x0, x1 + 1, 8):
        a.put(x + 3, y0, LF3)
        a.put(x + 4, y0, LF4)
    a.hline(x0, x1, y0 + 4, INK)


def lit_round_window(a, cx, cy, flower=PK2):
    """A round window (11 px) in a timber ring, warm light, a cross of glazing bars; a flower box under it."""
    a.sprite(cx - 6, cy - 6, ["...iiiii...",
                              ".ii22222ii.",
                              ".i2yyyyy2i.",
                              "i2yYYbyyy2i",
                              "i2yYybyyy2i",
                              "i2bbbbbbb2i",
                              "i2yyybyyy2i",
                              "i2yyybyyy2i",
                              ".i2yybyy2i.",
                              ".ii22222ii.",
                              "...iiiii..."], {"i": INK, "2": BK2, "y": GL1, "Y": GL2, "b": BK1})
    a.sprite(cx - 6, cy + 5, ["ifLfLfLfLi.",
                              "i3333333331",
                              "i2222222221",
                              ".iiiiiiiii."], {"i": INK, "3": BK3, "2": BK2, "1": BK1, "f": flower, "L": LF3})


def arched_door(a, cx, bottom, wood=(BK1, BK2, BK3), ring=MS1):
    """A round-topped plank door (12 px wide) in an arch of mossy stones, an iron ring; a stone step below."""
    w1, w2, w3 = wood
    rows = ["....ssssss....",
            "..ssiiiiiiss..",
            ".ssi323232iss.",
            ".si33232321is.",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si33232323r1is",
            "si3323232rR1is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "si3323232321is",
            "iiiiiiiiiiiiii"]
    pal = {"s": MS2, "i": INK, "3": w3, "2": w2, "1": w1, "r": ring, "R": INK}
    a.sprite(cx - 7, bottom - len(rows) + 1, rows, pal)


def herbs(a, x, y, flower=PK2):
    """A bundle of herbs hung upside down from the eave."""
    a.sprite(x - 2, y, ["..i..",
                        "..i..",
                        ".i2i.",
                        "imLmi",
                        "iLmLi",
                        ".mLm.",
                        ".fmf.",
                        "..f.."], {"i": INK, "2": BK2, "m": LF3, "L": LF4, "f": flower})


def chimney(a, x, top=0):
    """A stout chimney of mossy stones poking up through the roof, moss round its foot."""
    a.sprite(x, top, ["iiiiiiii",
                      "i222222i",
                      "i111111i",
                      "iiiiiiii",
                      ".i2221i.",
                      ".i22i1i.",
                      ".i2211i.",
                      ".iii21i.",
                      ".i2221i.",
                      "LmLLmLLm"], {"i": INK, "2": MS2, "1": MS1, "L": LF4, "m": LF3})


def cottage_piece(w=5, door_col=2, kind="a"):
    """A moss-roofed fairy-tale cottage (5x4; the Herbalist 6x4): a deep cushioned moss roof sagging in drips at the
    eave, plaster between dark timbers on a footing of mossy stones, a round plank door in a stone arch, round lit
    windows with flower boxes, herbs drying under the eave. Built from 8 px periodic parts fixed to the piece's
    origin, so the cottages and the Herbalist share their roof, wall and footing tiles."""
    a = Art(w, 4)
    W = a.W
    dcx = door_col * 16 + 8
    posts = [3] + [16 * k for k in range(1, w) if k not in (door_col, door_col + 1)] + [door_col * 16 + 1, door_col * 16 + 14] + [W - 5]
    plaster_wall(a, 3, W - 4, 30, 56, posts)
    a.vline(2, 30, 56, INK)
    a.vline(W - 3, 30, 56, INK)
    cushion_roof(a, 0, W - 1, 1, 31)
    footing(a, 2, W - 3, 57)
    a.hline(3, W - 4, 62, GSH)
    a.hline(5, W - 6, 63, GSH)
    flower = BL1 if kind == "herbalist" else PK2
    wood = (LF1, LF2, LF3) if kind == "b" else (BK1, BK2, BK3)
    arched_door(a, dcx, 60, wood=wood)
    a.sprite(dcx - 7, 61, [".pppppppppppp.", "iqqqqqqqqqqqqi", ".ssssssssssss."],
             {"p": MS2, "q": MS1, "i": INK, "s": GSH})
    wins = [1, 3] if w == 5 else [1, 4]
    for c in wins:
        lit_round_window(a, c * 16 + 8, 42, PK2 if kind != "herbalist" else GL2)
    if kind == "a":
        chimney(a, 58)
        herbs(a, 9, 34)
        herbs(a, 70, 34, GL2)
    elif kind == "b":
        chimney(a, 14)
        herbs(a, 70, 34)
        # a climbing rose up the west corner, toadstools in the roof moss
        a.sprite(4, 34, [".fL", "Lm.", ".Lf", "mL.", ".fm", "Lm.", ".mL", "fL.", ".m.", "Lmf", ".L.", "mf.",
                         ".L.", "Lm.", ".mf", "L..", "m..", ".m."], {"f": PK2, "L": LF4, "m": LF3})
        for x, y in ((50, 9), (60, 13), (27, 18)):
            a.sprite(x, y, [".iiii.", "ipfppi", "ipppfi", ".i22i.", "..mm.."],
                     {"i": INK, "f": PLS, "p": PK2, "2": PLS, "m": LF2})
    else:   # the Herbalist: the blue sign on a bracket, herbs all along the eave, a crate of cuttings
        for x, fl in ((9, GL2), (30, GL2), (63, GL2), (86, GL2)):
            herbs(a, x, 34, fl)
        a.sprite(42 + 6, 33, ["iiiiiiiiiiii",
                              ".i......i...",
                              ".i......i...",
                              "iiiiiiiiiiii",
                              "iBBBBBBBBBBi",
                              "iBBBBpBBBBBi",
                              "iBBBpppBBBBi",
                              "iBBppLppBBBi",
                              "iBBBpLpBBBBi",
                              "iBBBBLBBBBBi",
                              "iBBBLBBBBBBi",
                              "iiiiiiiiiiii"], {"i": INK, "B": BL1, "p": PLS, "L": LF3})
        a.sprite(80, 49, ["..L.m.L..mL..",
                          ".mLmLLmLmLLm.",
                          "iiiiiiiiiiiii",
                          "i33333333333i",
                          "i2i2222i2222i",
                          "i22i222i2222i",
                          "i222i22i2222i",
                          "i2222i2i2222i",
                          "i22222ii2222i",
                          "i11111i11111i",
                          "iiiiiiiiiiiii",
                          ".sssssssssss."],
                 {"i": INK, "3": BK3, "2": BK2, "1": BK1, "L": LF4, "m": LF3, "s": GSH})
    return a


# ---------------------------------------------------------------- the gym: the Moss Curtains
STRAND = [MS3, MS2, MS1, None, MS2, MS3, MS1, MS2]        # the curtain's strands across 8 px (None: a gap)
STRAND_LEN = [3, 1, 4, 0, 2, 5, 1, 3, 2, 4, 0, 3, 5, 1, 2, 4]   # how far each strand hangs past the hem (16 px period)


def gym_arbour():
    """Lutin's gym, 7x5: a glade pavilion under a domed roof of moss with a flowering vine, its front hung with
    curtains of Spanish moss between rustic bough posts; the middle bay's curtains are tied back with pink ribbons on a
    doorway glowing pink. A carved plaque with fairy wings crowns the dome. Drawn on the left half and mirrored; the
    roof is the cottages' moss, the curtains an 8 px periodic weave."""
    a = Art(7, 5)
    W, H = a.W, a.H
    beam = 28
    # the shade inside the pavilion (shows between the strands)
    a.rect(4, beam + 4, W // 2, H - 5, LF1)
    a.rect(4, beam + 4, W // 2, beam + 6, INK)
    # the dome
    for x in range(W // 2):
        u = (x + 0.5 - W / 2) / (W / 2)
        t = int(round(3 + 12 * u * u))
        for y in range(t, beam):
            a.put(x, y, roof_colour(x, y, y // 8))
    px = {(x, y) for x in range(W // 2) for y in range(beam) if not a.clear_at(x, y)}
    for x, y in px:
        if (x, y - 1) not in px or (x - 1, y) not in px and x == 0:
            a.put(x, y, INK)
    for x, y in px:
        if x == 0:
            a.put(x, y, INK)
    # the flowering vine across the dome (16 px period)
    for x0 in range(0, W // 2, 16):
        a.sprite(x0, 17, ["....L...........",
                          "LmL.pP..L.mL....",
                          "..mLPpmLmL..mLpP",
                          "...........L.mPp"], {"L": LF4, "m": LF3, "p": PK3, "P": PK2})
    # the plaque: a carved oval with fairy wings, on the crown of the dome
    a.sprite(44, 3, ["......iiiiii",
                     "....ii333333",
                     "...i3322222.",
                     "..i3pp222222",
                     "..i3Ppp22222",
                     "..i32Pp2pp22",
                     "..i322P2Pp22",
                     "...i32222222",
                     "....ii111111",
                     "......iiiiii"], {"i": INK, "3": BK3, "2": BK2, "1": BK1, "p": PK3, "P": PK2})
    # the beam: a peeled bough, fairy lights hung under it
    a.hline(0, W // 2, beam, INK)
    a.hline(0, W // 2, beam + 1, BK3)
    a.hline(0, W // 2, beam + 2, BK2)
    a.hline(0, W // 2, beam + 3, INK)
    for x in range(4, W // 2, 8):
        a.put(x, beam + 2, BK1)
        a.put(x + 1, beam + 4, GL2)
        a.put(x + 1, beam + 5, PK3)
    # curtains of moss in the side bay
    for x in range(7, 38):
        c0 = STRAND[x % 8]
        if c0 is None:
            continue
        hem = H - 12 + STRAND_LEN[x % 16] - 3
        for y in range(beam + 4, hem + 1):
            c = c0
            if (y + x * 3) % 9 == 0:
                c = MS1 if c0 != MS1 else MS2          # kinks in the strands
            if y >= hem - 1:
                c = MS1
            a.put(x, y, c)
    # posts: rustic boughs
    for p in (2, 38):
        for y in range(beam - 1, H - 3):
            a.put(p, y, INK)
            a.put(p + 1, y, BK3)
            a.put(p + 2, y, BK2)
            a.put(p + 3, y, BK1)
            a.put(p + 4, y, INK)
        for y in range(beam + 7, H - 4, 9):
            a.put(p + 2, y, BK1)                      # knots
        a.sprite(p - 2, H - 4, ["i1222i11i", ".iiiiiiii"], {"i": INK, "2": BK2, "1": BK1})
    # the door bay: the glow, and the curtains drawn back to the posts with pink ribbons
    for y in range(beam + 4, H - 4):
        for x in range(43, W // 2):
            dy = (y - (beam + 4)) / (H - 8 - beam)
            d = (W // 2 - x) / 13 + (0.6 - dy) * 0.25
            c = PK3 if d < 0.45 else PK2 if d < 0.75 else PK1 if d < 1.0 else LF1
            a.put(x, y, c)
    for y in range(beam + 4, H - 4):
        k = y - (beam + 4)
        reach = int(2 + 6 * math.sin(min(1.0, k / 24) * math.pi / 2)) if k < 26 else int(8 - (k - 26) * 0.35)
        reach = max(3, reach)
        for i in range(reach):
            x = 43 + i
            c = (MS2, MS3, MS2, MS1, MS2, MS3, MS2, MS1, MS2)[(i + k // 4) % 9]
            if i == reach - 1:
                c = MS1
            a.put(x, y, c)
    a.sprite(42, 57, ["Ppp.", "PpPp", ".P.."], {"p": PK2, "P": PK1})     # the ribbon
    for x, y in ((50, 40), (53, 47), (48, 55), (54, 62), (51, 68)):
        a.put(x, y, GL2)
    # the threshold and the blossoms at the posts' feet
    a.rect(43, H - 4, W // 2, H - 2, MS2)
    a.hline(43, W // 2, H - 4, MS3)
    a.hline(43, W // 2, H - 1, INK)
    a.put(43, H - 3, INK)
    a.put(43, H - 2, INK)
    for x in (0, 9, 30, 35):
        a.sprite(x, H - 4, [".p.", "pPp", ".L."], {"p": PK3, "P": PK2, "L": LF3})
    a.hline(7, 37, H - 5, LF2)
    a.mirror()
    for x, y in ((60, 44), (63, 58), (58, 66)):           # sparkles in the doorway (not mirrored)
        a.put(x, y, GL2)
    return a


# ---------------------------------------------------------------- the Pokemon Center: a great hollow oak
def bark(x, y, zone):
    """Live-oak bark, 8 px across and 16 down (periodic): two uneven plates between deep furrows, each plate lit on its
    west edge, cracked across at staggered heights, a knot now and then. zone: 0 lit, 1 mid, 2 shade."""
    k, j = x % 8, y % 16
    if k in (0, 5):                                         # furrows
        return INK if zone == 2 or (zone == 1 and j % 8 < 5) else BK1
    plate_a = k < 5
    crack = (plate_a and j in (5, 6) and k in (2, 3, 4)[: 3 - (j - 5)]) or (not plate_a and j == 12)
    if crack:
        return BK1 if zone < 2 else INK
    edge = k in (1, 6)
    if zone == 0:
        return BK3 if edge or (plate_a and k == 2 and j % 8 < 3) else BK2
    if zone == 1:
        return BK3 if edge and j % 3 else BK2
    return BK2 if edge else BK1


ROOTS = [   # (x at the trunk, x at the tip, rows above the foot where it leaves the trunk, half-width at the trunk)
    (-24, -50, 26, 8.0), (-24, -41, 14, 6.0)]


def hollow_tree():
    """The Pokemon Center, 7x6: the trunk of a vast live oak under a crown of leaves hung with moss, its door an
    arched hollow glowing warm under a red and white hood, a Poke Ball plaque above, red lanterns either side, round
    lit windows. The trunk is 8 px periodic bark (lit west, shaded east)."""
    a = Art(7, 6)
    W, H = a.W, a.H
    # the trunk: a vast column, a little narrower under the crown, flaring into buttress roots
    foot = H - 6
    dcx = W // 2
    body = set()
    for y in range(18, foot + 1):
        hw = 30 + max(0.0, y - (foot - 14)) ** 1.5 * 0.22 + (1 if (y // 8) % 2 else 0)
        for x in range(int(round(dcx - hw)), int(round(dcx + hw))):
            body.add((x, y))
    for x, y in body:
        zone = 0 if x < 40 else 1 if x < 76 else 2
        a.put(x, y, bark(x, y, zone))
    a.edge(INK, body, border=True)
    roots = set()
    for side in (-1, 1):
        for xt, xe, up, w0 in ROOTS:          # outer roots first; each its own ridge with its own outline
            y0 = foot - up
            mine = {}
            for y in range(y0, foot + 1):
                t = (y - y0) / max(1, foot - y0)
                xc = dcx + side * (abs(xt) + (abs(xe) - abs(xt)) * t ** 1.4) - (0.5 if side > 0 else 0)
                w = w0 * (1 - 0.55 * t) + (1.5 if t > 0.8 else 0)
                for x in range(int(math.floor(xc - w)), int(math.ceil(xc + w)) + 1):
                    if 0 <= x < W and (x, y) not in body:
                        mine[(x, y)] = (x - xc) * side / max(w, 1)      # > 0: the root's outer, lower side
            for (x, y), d in mine.items():
                top = (x, y - 1) not in mine and (x, y - 1) not in body
                if side < 0:
                    c = BK3 if top or d < -0.35 else BK2 if d < 0.4 else BK1
                else:
                    c = BK2 if top or d < -0.35 else BK1
                a.put(x, y, c)
            a.edge(INK, set(mine), border=True)
            for (x, y) in mine:
                if (x, y - 1) in body and a.get(x, y - 1) == INK:
                    a.put(x, y - 1, BK1 if side > 0 else BK2)          # the root grows out of the trunk: no seam
            roots |= set(mine)
    for x in range(W):
        if (x, foot) in body | roots and a.clear_at(x, foot + 1):
            a.put(x, foot + 1, GSH)
    # the hood over the door: red and white
    a.sprite(dcx - 14, 55, ["....iiiiiiiiiiiiiiiiiiii....",
                            "..iiRRwRRwRRwRRwRRwRRwRRii..",
                            ".iRRRrwRRrwRRrwRRrwRRrwRRRi.",
                            "iRrrRrwrRrwrRrwrRrwrRrwrRrri",
                            "iiiiiiiiiiiiiiiiiiiiiiiiiiii"], {"i": INK, "R": RD2, "r": RD1, "w": WHT})
    # the hollow: an arch of dark bark lip, warm light inside, a root sill
    for y in range(60, foot + 1):
        for x in range(dcx - 11, dcx + 11):
            r = 11
            dy = y - (60 + r)
            if dy < 0 and ((x + 0.5 - dcx) / r) ** 2 + (dy / r) ** 2 > 1:
                continue
            a.put(x, y, INK)
    for y in range(62, foot + 1):
        for x in range(dcx - 9, dcx + 9):
            r = 9
            dy = y - (62 + r)
            if dy < 0 and ((x + 0.5 - dcx) / r) ** 2 + (dy / r) ** 2 > 1:
                continue
            c = GL1 if y < foot - 6 else GL2
            if x in (dcx - 9, dcx + 8) and y > 66:
                c = BK2
            a.put(x, y, c)
    a.rect(dcx - 4, 66, dcx + 3, foot - 7, GL2)      # light through the inner door
    a.hline(dcx - 10, dcx + 9, foot, BK3)
    a.hline(dcx - 10, dcx + 9, foot + 1, INK)
    # the Poke Ball plaque
    pcx, pcy = dcx, 44
    for x, y in ell(pcx, pcy, 8, 8):
        a.put(x, y, INK)
    for x, y in ell(pcx, pcy, 6.8, 6.8):
        a.put(x, y, RD2 if y < pcy else WHT)
    for x, y in ell(pcx + 2.2, pcy - 2.4, 4.5, 4.5):
        if a.get(x, y) == RD2 and (x - pcx) + (y - pcy) > 3:
            a.put(x, y, RD1)
    a.put(pcx - 4, pcy - 4, WHT)
    a.put(pcx - 3, pcy - 5, WHT)
    a.hline(pcx - 7, pcx + 6, pcy, INK)
    for x, y in ell(pcx, pcy + 0.5, 2.6, 2.6):
        a.put(x, y, INK)
    for x, y in ell(pcx, pcy + 0.5, 1.5, 1.5):
        a.put(x, y, WHT)
    for x in range(pcx - 5, pcx + 5):
        if a.get(x, pcy + 4) == WHT:
            a.put(x, pcy + 4, MS3)
    # round windows up the trunk, lanterns by the door
    lit_round_window(a, 30, 48, RD2)
    lit_round_window(a, W - 30, 48, RD2)
    for lx in (dcx - 18, dcx + 15):
        a.sprite(lx, 60, [".i.", ".i.", "iii", "RYR", "RYR", "rYr", "iii", ".r."],
                 {"i": INK, "R": RD2, "r": RD1, "Y": GL2})
    # the crown
    lobes = [(56, 9, 16, 9), (36, 11, 14, 8.5), (16, 15, 13, 8), (6.5, 22, 6.5, 6.5), (44, 18, 14, 7.5),
             (24, 23, 13, 7), (10, 28, 9, 5.5), (40, 26, 12, 5.5), (56, 26, 10, 5)]
    crown = Art(7, 6)
    leafy(crown, lobes, (LF1, LF2, LF3, LF4, LF4), INK, gy=32, cell=(8, 6))
    crown.mirror(0, 40)
    for y in range(40):
        for x in range(W):
            if not crown.clear_at(x, y):
                a.put(x, y, crown.get(x, y))
    for x, y, kind in ((4, 30, "mid"), (13, 31, "long"), (24, 29, "short"), (34, 30, "mid"), (47, 30, "wisp")):
        beard(a, x, y, kind)
        beard(a, W - x - len(BEARDS[kind][0]), y, kind, flip=True)     # the same moss, mirrored (free tiles)
    a.remap({MS1: LF2, GSH: KEY})       # 15 colours: the moss's shade is the leaves', no shade on the grass
    return a


# ---------------------------------------------------------------- registration
SECTIONS = [
    ("Buildings", ["gym_arbour", "hollow_tree", "cottage_a", "cottage_b", "herbalist"]),
    ("Ring trees (blocking)", ["tree_a", "tree_b", "tree_c", "tree_s", "thicket_a", "thicket_b"]),
    ("Understory (blocking)", ["bush_a", "bush_b", "mossy_log"]),
    ("Ground cover (walkable)", ["fern_a", "fern_b", "fern_c", "moss_mound", "bloom_pink", "bloom_violet",
                                 "bloom_white", "bloom_gold", "glowbell", "toadstool_red", "toadstool_pale"]),
    ("Fairy", ["fairy_ring", "pool", "pepper_bed", "riddle_stone"]),
]


def build_pieces():
    PIECES.clear()
    add("gym_arbour", gym_arbour(), "Lutin's gym: a glade pavilion behind curtains of Spanish moss, parted at the "
        "glowing door (7x5).", doors=[(3, 4)])
    add("hollow_tree", hollow_tree(), "The Pokemon Center: a vast hollow live oak, arched lit door under a red hood, "
        "Poke Ball plaque (7x6).", doors=[(3, 5)])
    add("cottage_a", cottage_piece(5, 2, "a"), "Moss cottage A: cushioned moss roof, round plank door, round lit windows, "
        "herbs under the eave, chimney east (5x4).", doors=[(2, 3)])
    add("cottage_b", cottage_piece(5, 2, "b"), "Moss cottage B: green round door, chimney west, a climbing rose, toadstools "
        "in the roof moss (5x4).", doors=[(2, 3)])
    add("herbalist", cottage_piece(6, 2, "herbalist"), "The Herbalist (shop): the cottages' roof and walls, a blue sign, "
        "herbs drying all along the eave, a crate of cuttings (6x4).", doors=[(2, 3)])
    a, b, c = ring_trees()
    add("tree_a", a, "Ring tree A: a moss-hung live oak, round crown (3x3, blocking; opaque crown).")
    add("tree_b", b, "Ring tree B: broad two-humped crown (3x3, blocking; lower half = tree_a's tiles).")
    add("tree_c", c, "Ring tree C: tall crown in pink bloom (3x3, blocking; lower half = tree_a's tiles).")
    add("tree_s", small_tree(), "Small ring tree: a young moss-hung oak (2x2, blocking).")
    add("thicket_a", thicket("a"), "Thicket: dense dark leaves for the cracks between trunks (1x1, blocking).")
    add("thicket_b", thicket("b"), "Thicket, second shape (1x1, blocking).")
    add("bush_a", shrub_piece("a"), "Understory shrub in white blossom (1x1, blocking).")
    add("bush_b", shrub_piece("b"), "Yaupon shrub with red berries (1x1, blocking).")
    add("mossy_log", mossy_log_piece(), "Fallen log furred with moss, toadstools, bracket fungus (2x1, blocking).")
    for n in ("fern_a", "fern_b", "fern_c"):
        add(n, fern_piece(n), "A clump of arching ferns (1x1, walkable).", walk=[(0, 0)])
    add("moss_mound", moss_mound_piece(), "A low cushion of moss and a fern sprig (1x1, walkable).", walk=[(0, 0)])
    for n in ("bloom_pink", "bloom_violet", "bloom_white", "bloom_gold"):
        add(n, bloom(n), f"A drift of {n[6:]} wildflowers (1x1, walkable).", walk=[(0, 0)])
    add("glowbell", glowbell(), "Glow-bells: pale cyan bells lit from within (1x1, walkable).", walk=[(0, 0)])
    add("toadstool_red", toadstool("red"), "Red toadstools with white spots (1x1, walkable).", walk=[(0, 0)])
    add("toadstool_pale", toadstool("pale"), "Pale toadstools glowing faintly (1x1, walkable).", walk=[(0, 0)])
    add("fairy_ring", fairy_ring_piece(), "A fairy ring of pale toadstools on darker grass (3x3, all walkable).",
        walk=[(i, j) for j in range(3) for i in range(3)])
    add("pool", pool(), "A still reflecting pool in a ring of mossy stones (2x2, blocking).")
    add("pepper_bed", pepper_bed_piece(), "A raised bed of red peppers (3x2, blocking); tiles east-west (half posts at "
        "the ends).")
    add("riddle_stone", riddle_stone_piece(), "The riddle stone: a mossy standing stone, a glowing carved flame-tail "
        "(1x2, blocking).")


# ---------------------------------------------------------------- checks
def check_pieces():
    """Footprints, doors and walkable cells against hollow_tileset.WANTED; GBA-exact colours; <= 15 per piece."""
    problems = []
    try:
        import sys
        sys.path.insert(0, MAPGEN)
        from hollow_tileset import WANTED
    except Exception as e:  # noqa: BLE001
        WANTED = None
        problems.append(f"could not read hollow_tileset.WANTED ({e})")
    if WANTED:
        for name, (w, h, door, walk, _kind) in WANTED.items():
            if name not in PIECES:
                problems.append(f"{name}: missing")
                continue
            m = PIECES[name][1]
            if (m["w"], m["h"]) != (w, h):
                problems.append(f"{name}: {m['w']}x{m['h']}, wanted {w}x{h}")
            if ([list(door)] if door else []) != m["doors"]:
                problems.append(f"{name}: doors {m['doors']}, wanted {door}")
            if sorted(map(tuple, m["passable"])) != sorted(map(tuple, walk)):
                problems.append(f"{name}: walkable {m['passable']}, wanted {walk}")
        for name in PIECES:
            if name not in WANTED:
                problems.append(f"{name}: not in WANTED")
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
    return problems


# ---------------------------------------------------------------- tiles
def tile_census(order):
    """Unique 8x8 tiles (a tile and its h/v/hv flips are one tile; fully clear tiles are free), counted in `order`:
    per piece its tile count and how many are new. Returns ({name: (tiles, new)}, total)."""
    seen, out = set(), {}
    for name in order:
        art = PIECES[name][0]
        mine = set()
        new = 0
        for ty in range(0, art.H, 8):
            for tx in range(0, art.W, 8):
                t = tuple(tuple(art.px[ty + y][tx:tx + 8]) for y in range(8))
                if all(c == KEY for row in t for c in row):
                    continue
                flips = (t, tuple(r[::-1] for r in t), t[::-1], tuple(r[::-1] for r in t[::-1]))
                k = min(flips)
                mine.add(k)
                if k not in seen:
                    seen.add(k)
                    new += 1
        out[name] = (len(mine), new)
    return out, len(seen)


# ---------------------------------------------------------------- the sheet
def pack(width=24):
    order = sorted(PIECES, key=lambda n: (-PIECES[n][0].h, -PIECES[n][0].w, n))
    x = y = rowh = 0
    place = {}
    for n in order:
        art = PIECES[n][0]
        if x + art.w > width:
            x, y, rowh = 0, y + rowh, 0
        place[n] = (x, y)
        x += art.w
        rowh = max(rowh, art.h)
    sheet = Image.new("RGB", (width * 16, (y + rowh) * 16), KEY)
    index = {}
    for n, (cx, cy) in place.items():
        art, meta = PIECES[n]
        sheet.paste(art.image(), (cx * 16, cy * 16))
        index[n] = dict(meta, x=cx, y=cy)
    return sheet, index


def _pixels(im):
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())


def grass_cell():
    im = Image.open(os.path.join(HERE, "..", "ekat_swamp", "swamp_tiles.png")).convert("RGB").crop((0, 0, 16, 16))
    return im.point(lambda v: (v >> 3) << 3)


def on_grass(im, margin=0):
    """An RGB image with magenta clear, laid over Ekat's grass (with `margin` cells of grass round it)."""
    g = grass_cell()
    W, H = im.width + margin * 32, im.height + margin * 32
    bg = Image.new("RGB", (W, H))
    for y in range(0, H, 16):
        for x in range(0, W, 16):
            bg.paste(g, (x, y))
    m = Image.new("L", im.size, 0)
    m.putdata([0 if p == KEY else 255 for p in _pixels(im.convert("RGB"))])
    bg.paste(im, (margin * 16, margin * 16), m)
    return bg


def write_preview(sheet, path):
    on_grass(sheet).resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(path)


# ---------------------------------------------------------------- the test glade
GLADE = [   # 30 x 22: '.' grass, ':' path; the pieces are placed by GLADE_PIECES
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............::..............",
    "..............::..............",
    "..............::..............",
    "......::......::..............",
    "......::......::..............",
    "......::......::..............",
    "......::......::..............",
    ".....::::::::::::::::::::.....",
    ".....::::::::::::::::::::.....",
    ".............::...............",
    ".............::...............",
    ".............::...............",
    ".............::...............",
    ".............::...............",
]
GLADE_PIECES = [
    # the ring: a row of trees along the top, columns down the sides, the bottom row with the lane's gap
    ("tree_a", 0, 0), ("tree_b", 3, 0), ("tree_c", 6, 0), ("tree_a", 9, 0), ("tree_b", 12, 0), ("tree_a", 15, 0),
    ("tree_c", 18, 0), ("tree_b", 21, 0), ("tree_a", 24, 0), ("tree_c", 27, 0),
    ("tree_c", 0, 3), ("tree_a", 0, 6), ("tree_b", 0, 9), ("tree_a", 0, 12), ("tree_c", 0, 15),
    ("tree_b", 27, 3), ("tree_a", 27, 6), ("tree_c", 27, 9), ("tree_b", 27, 12), ("tree_a", 27, 15),
    ("tree_b", 0, 18), ("tree_a", 3, 19), ("tree_c", 6, 19), ("tree_s", 9, 20), ("thicket_a", 11, 21),
    ("thicket_b", 15, 21), ("tree_s", 16, 20), ("tree_b", 18, 19), ("tree_a", 21, 19), ("tree_c", 24, 19),
    ("tree_b", 27, 18),
    ("tree_s", 3, 3), ("thicket_a", 5, 3), ("thicket_b", 24, 3), ("tree_s", 25, 3), ("thicket_a", 26, 5),
    ("thicket_b", 3, 18), ("bush_b", 26, 17),
    # the buildings
    ("gym_arbour", 11, 3), ("hollow_tree", 3, 5), ("cottage_a", 19, 11),
    # fairy details
    ("fairy_ring", 20, 6), ("pool", 23, 9), ("pepper_bed", 8, 12), ("riddle_stone", 18, 4), ("mossy_log", 9, 18),
]


def path_key(grid, x, y):
    """build.py's path autotile: which edge or corner of the path patch this ':' cell is."""
    h, w = len(grid), len(grid[0])
    same = lambda i, j: not (0 <= i < w and 0 <= j < h) or grid[j][i] == ":"   # noqa: E731
    n, s, ww, e = same(x, y - 1), same(x, y + 1), same(x - 1, y), same(x + 1, y)
    key = ("N" if not n else "S" if not s else "") + ("W" if not ww else "E" if not e else "")
    if not key:
        for dx, dy, k in ((-1, -1, "iNW"), (1, -1, "iNE"), (-1, 1, "iSW"), (1, 1, "iSE")):
            if not same(x + dx, y + dy):
                return k
    return key or "C"


def path_cells():
    """The town's own path metatiles (the Johto dirt path in orleans_general), read from the built tilesets; the inner
    corners composed the way the recipe composes them (C, with the corner quarter where both edges are grass)."""
    try:
        import sys
        sys.path.insert(0, MAPGEN)
        import render
        root = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
        ts = render.Tilesets(os.path.join(root, "data/tilesets/primary/orleans_general"),
                             os.path.join(root, "data/tilesets/secondary/orleans_hollow"))
        ids = {"NW": 0xD0, "N": 0xD1, "NE": 0xD2, "W": 0xD8, "C": 0xD9, "E": 0xDA, "SW": 0xE0, "S": 0xE1, "SE": 0xE2}
        cells = {k: ts.metatile(v).convert("RGB") for k, v in ids.items()}
    except Exception:  # noqa: BLE001  (no built tileset: a flat stand-in path)
        c = Image.new("RGB", (16, 16), (152, 128, 96))
        cells = {k: c for k in ("NW", "N", "NE", "W", "C", "E", "SW", "S", "SE")}
    pathset = set(_pixels(cells["C"]))
    for k, (ea, eb, qx, qy) in {"iNW": ("N", "W", 0, 0), "iNE": ("N", "E", 8, 0), "iSW": ("S", "W", 0, 8),
                                "iSE": ("S", "E", 8, 8)}.items():
        im = cells["C"].copy()
        A, B = cells[ea], cells[eb]
        for y in range(qy, qy + 8):
            for x in range(qx, qx + 8):
                pa, pb = A.getpixel((x, y)), B.getpixel((x, y))
                if pa not in pathset and pb not in pathset:
                    im.putpixel((x, y), pa)
        cells[k] = im
    return cells


def glade():
    """The test glade: Ekat's grass, the path patch, the ring, the three buildings, the fairy details, then ground
    cover and understory scattered over the free grass the way hollow.py does it (denser toward the ring)."""
    h, w = len(GLADE), len(GLADE[0])
    out = Image.new("RGB", (w * 16, h * 16))
    g = grass_cell()
    pc = path_cells()
    for y in range(h):
        for x in range(w):
            out.paste(pc[path_key(GLADE, x, y)] if GLADE[y][x] == ":" else g, (x * 16, y * 16))
    occ = set()
    for name, x0, y0 in GLADE_PIECES:
        art = PIECES[name][0]
        for j in range(art.h):
            for i in range(art.w):
                occ.add((x0 + i, y0 + j))
    for y in range(h):
        for x in range(w):
            if GLADE[y][x] == ":":
                occ.add((x, y))
    for d in ((14, 8), (6, 11), (21, 15)):      # keep the ground in front of each door clear
        occ.add(d)
    extra = []
    ring = {(x, y) for n, x0, y0 in GLADE_PIECES if n.startswith(("tree", "thicket"))
            for x in range(x0, x0 + PIECES[n][0].w) for y in range(y0, y0 + PIECES[n][0].h)}
    cover = ["fern_a", "fern_b", "fern_c", "moss_mound", "bloom_pink", "bloom_violet", "bloom_white", "bloom_gold",
             "glowbell", "toadstool_red", "toadstool_pale"]
    for y in range(h):
        for x in range(w):
            if (x, y) in occ:
                continue
            near = min((max(abs(x - i), abs(y - j)) for i, j in ring), default=9)
            r = _hh(x, y, 77)
            if near == 1 and r < 0.75:
                extra.append((("bush_a", "bush_b", "fern_a", "fern_b", "fern_c", "fern_a")[int(_hh(x, y, 5) * 6)], x, y))
            elif near == 2 and r < 0.6:
                extra.append((cover[int(_hh(x, y, 6) * len(cover))], x, y))
            elif r < 0.3:
                extra.append((cover[int(_hh(x, y, 8) * len(cover))], x, y))
    for name, x0, y0 in GLADE_PIECES + extra:
        art = PIECES[name][0]
        im = art.image()
        m = Image.new("L", im.size, 0)
        m.putdata([0 if c == KEY else 255 for row in art.px for c in row])
        out.paste(im, (x0 * 16, y0 * 16), m)
    return out


# ---------------------------------------------------------------- the review sheet
def review(path, census, total, problems):
    S = 3
    W = 1800
    blocks = []
    for title, names in SECTIONS:
        items = []
        for n in names:
            art = PIECES[n][0]
            im = on_grass(art.image(), 1 if art.w * art.h > 1 else 0)
            if art.w * art.h == 1:
                im = on_grass(art.image(), 0)
                big = Image.new("RGB", (48, 48))
                g = grass_cell()
                for yy in range(0, 48, 16):
                    for xx in range(0, 48, 16):
                        big.paste(g, (xx, yy))
                big.paste(im, (16, 16))
                im = big
            t, new = census[n]
            lab = f"{n} {art.w}x{art.h}: {t} tiles ({new} new), {len(art.colours())} col"
            if PIECES[n][1]["doors"]:
                lab += f", door {tuple(PIECES[n][1]['doors'][0])}"
            items.append((lab, im.resize((im.width * S, im.height * S), Image.NEAREST)))
        blocks.append((title, items))
    gl = glade()
    gl = gl.resize((gl.width * S, gl.height * S), Image.NEAREST)
    # layout
    y = 40
    pos = []
    for title, items in blocks:
        pos.append(("title", title, 10, y))
        y += 22
        x, rowh = 10, 0
        for lab, im in items:
            wlab = max(im.width, 7 * len(lab))
            if x + wlab > W - 10:
                x, y, rowh = 10, y + rowh + 26, 0
            pos.append(("img", (lab, im), x, y))
            x += wlab + 24
            rowh = max(rowh, im.height)
        y += rowh + 36
    pos.append(("title", "Test glade (3x): ring of trees, understory and ground cover, the hollow-tree Pokemon Center "
                         "(west), the gym arbour (north), a cottage with the path at its door, fairy ring, pool, "
                         "pepper beds, riddle stone, log; paths are the town's own path tiles", 10, y))
    y += 22
    pos.append(("glade", gl, 10, y))
    y += gl.height + 20
    lines = [f"Unique 8x8 tiles over all pieces (flips free, clear tiles free): {total}"]
    for title, names in SECTIONS:
        lines.append(f"    {title}: {sum(census[n][1] for n in names)} new tiles")
    lines.append("Colours per piece <= 15, all GBA-exact (multiples of 8)." if not problems else
                 "PROBLEMS: " + "; ".join(problems))
    H = y + 18 * len(lines) + 20
    out = Image.new("RGB", (W, H), (34, 38, 42))
    d = ImageDraw.Draw(out)
    d.text((10, 10), "Lutin's Hollow own art (make_hollow_art.py): every piece at 3x on the swamp grass "
                     "(1 cell of grass round the bigger pieces)", fill=(240, 240, 240))
    for kind, v, x, yy in pos:
        if kind == "title":
            d.text((x, yy), v, fill=(250, 230, 160))
        elif kind == "img":
            lab, im = v
            out.paste(im, (x, yy))
            d.text((x, yy + im.height + 4), lab, fill=(220, 220, 210))
        else:
            out.paste(v, (x, yy))
    for i, line in enumerate(lines):
        d.text((10, y + 18 * i), line, fill=(255, 255, 170) if i == 0 else (220, 220, 220))
    out.save(path)


def main():
    build_pieces()
    problems = check_pieces()
    order = [n for _, names in SECTIONS for n in names]
    census, total = tile_census(order)
    sheet, index = pack()
    sheet.save(os.path.join(HERE, "hollow.png"))
    with open(os.path.join(HERE, "hollow.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_comment": "Lutin's Hollow own art (make_hollow_art.py): piece -> sheet cell [x, y] and size "
                               "w x h in 16 px cells; overlays, magenta = clear; doors and passable are cells "
                               "within the piece; empty = cells with nothing drawn.",
                   "png": "hollow.png", "pieces": index}, f, indent=1)
        f.write("\n")
    write_preview(sheet, os.path.join(HERE, "hollow_preview.png"))
    review(os.path.join(MAPGEN, "maps", "00_hollow_art.png"), census, total, problems)
    for n in order:
        art = PIECES[n][0]
        print(f"  {n:15s} {art.w}x{art.h}  {census[n][0]:3d} tiles {census[n][1]:3d} new  {len(art.colours()):2d} colours")
    print(f"hollow.png {sheet.size}, {len(index)} pieces; {total} unique 8x8 tiles (flips free)")
    for p in problems:
        print("  PROBLEM:", p)


if __name__ == "__main__":
    main()

"""The Oldest Shrine (Rayquaza's arena, outdoor map OldestShrine): own art for the route tileset it stands on.

usage (from the decomp root): python tools/mapgen/tilesets/arenas/make_shrine.py
writes tools/mapgen/tilesets/arenas/shrine.png (16 px cells, magenta = clear) and shrine.json: the pieces, the two
compose sources (opaque metatiles "osh", overlays "osho"), the corner-set autotiles for the ridges and the mound, and
the overlay prefabs, ready for the layout agent to add to orleans_route_b (the map's tileset; Route 14 shares it).

An ancient earthwork in the manner of Poverty Point: concentric earthen ridges round a plaza and a flat-topped
platform mound, a ring of live oaks and cypress, carved cedar posts and standing stones, open sky over the mound.
    berm_<key>     the low ridge: a grassy earthen berm as a dual-grid corner set on Ekat grass (build.py corners(): the
                   keys of CORNER_KEYS; C is plain ekat:grass). Lit lip on the north, a 6 px grassy slope with earth
                   showing on the south, side slopes, a shadow on the grass beyond.
    mound_S, mound_landNE, mound_landNW
                   the platform mound's south edge and its two south corners: the slope runs to the cell's foot ...
    mound_face, mound_face_l, mound_face_r
                   ... and on down through the cell below (the face extension, rock_wall's rule in build.py: face under
                   an S edge, face_l under landNE, face_r under landNW). Every other mound piece is the berm's.
    mound_steps    2x2: steps cut into the mound's south face (cedar log risers, packed earth treads): row 0 replaces
                   two mound_S cells, row 1 the two mound_face cells below; walkable.
    live_oak       4x3 a live oak with Spanish moss (overlay on grass)
    cedar_post, cedar_post_bird
                   1x2 carved red-cedar posts: ochre and clay bands, a spiral; the second topped by a carved bird
    stone_tall, stone_small
                   standing stones (1x2, 1x1) in the Rootkin stone of Route 25's shrine steps, spiral-carved, lichen
    singing_stone  2x2 the singing stone on the mound: a great upright stone bored through (the wind sings in it)
    landing        4x4 the landing steps (replaces the yellow placeholder dock), opaque: a stone landing slab at the
                   water, steps up the bank between two cheek walls with cedar mooring posts; columns 1-2 walkable.
Colour families: EARTH (ridge, mound, steps, oak) and STONE (posts, stones, landing); every 8x8 tile fits one (checked).
"""
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arena_art import MAPGEN, ROOT, Canvas, Sheet, check_families, dump, hashn  # noqa: E402

sys.path.insert(0, MAPGEN)
import render  # noqa: E402

# ---------------------------------------------------------------- colours
G, GD, GL = (120, 160, 104), (104, 144, 96), (136, 176, 128)        # Ekat grass and its flecks (exact)
SH = (96, 128, 88)                                                  # shadow on grass (Ekat's turf-line colour)
SL1, SL2, SL3 = (88, 128, 80), (72, 104, 64), (56, 80, 56)          # grassy slope, lit to dark
LP = (168, 200, 136)                                                # the lit lip of a ridge top
LM = (112, 152, 80)                                                 # leaf mid
E1, E2, E3 = (160, 120, 80), (120, 88, 64), (80, 64, 48)            # earth / cedar log
INKW = (48, 40, 32)                                                 # warm ink
MS1, MS2 = (152, 168, 144), (200, 208, 176)                         # Spanish moss
ST1, ST2, ST3, ST4 = (88, 88, 80), (128, 128, 112), (168, 168, 144), (208, 208, 184)   # Rootkin stone (Route 25)
MO = (80, 112, 64)                                                  # moss on stone
CD1, CD2, CD3 = (96, 56, 40), (136, 80, 56), (176, 112, 72)         # weathered red cedar: dark, mid, lit
OC = (216, 168, 72)                                                 # ochre paint
INK = (40, 40, 48)
WA, RP = (96, 136, 136), (152, 192, 184)                            # Ekat water, ripple

FAMILIES = {
    "EARTH": [G, GD, GL, SH, SL1, SL2, SL3, LP, LM, E1, E2, E3, INKW, MS1, MS2],
    "STONE": [G, GD, GL, ST1, ST2, ST3, ST4, MO, CD1, CD2, CD3, OC, INK, WA, RP],
}
CORNER_KEYS = {"1111": "C", "0011": "N", "1100": "S", "0101": "W", "1010": "E", "0111": "inNW", "1011": "inNE",
               "1101": "inSW", "1110": "inSE", "0001": "landSE", "0010": "landSW", "0100": "landNE", "1000": "landNW",
               "0110": "sTLBR", "1001": "sTRBL"}


# ---------------------------------------------------------------- ground from the built primary
_TS = None


def ground(name):
    """A primary metatile (e.g. 'ekat:grass') as a 16x16 RGB image, drawn from the built gTileset_OrleansGeneral."""
    global _TS
    if _TS is None:
        _TS = (render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_general"),
                               os.path.join(ROOT, "data/tilesets/secondary/orleans_route_b")),
               json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"])
    ts, mp = _TS
    return ts.metatile(mp[name]).convert("RGB")


def grass_px(x, y):
    return ground("ekat:grass").getpixel((x % 16, y % 16))


# ---------------------------------------------------------------- the berm (dual-grid corner set)
def disk(r):
    return [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= r * r + r * 0.5]


def morph(m, offs, op):
    out = set()
    if op == "dilate":
        for (x, y) in m:
            for dx, dy in offs:
                out.add((x + dx, y + dy))
        return out
    cand = m
    for (x, y) in cand:
        if all((x + dx, y + dy) in m for dx, dy in offs):
            out.add((x, y))
    return out


def corner_region(bits, w=1, h=1, extra_rows=0, ro=7, ri=5):
    """The ridge top as a pixel set on a canvas with a 16 px margin, for a tile whose corners TL TR BL BR are `bits`
    (each corner cell owns its quadrant and carries on past the tile's edge): convex corners rounded (radius ro),
    concave ones (radius ri). Coordinates: tile pixel (0, 0) = (16, 16)."""
    m = set()
    q = {0: (range(-16, 8), range(-16, 8)), 1: (range(8, 32), range(-16, 8)),
         2: (range(-16, 8), range(8, 32 + extra_rows)), 3: (range(8, 32), range(8, 32 + extra_rows))}
    for k, b in enumerate(bits):
        if b == "1":
            xs, ys = q[k]
            for y in ys:
                for x in xs:
                    m.add((x + 16, y + 16))
    m = morph(morph(m, disk(ro), "erode"), disk(ro), "dilate")        # opening: round convex corners
    m = morph(morph(m, disk(ri), "dilate"), disk(ri), "erode")        # closing: round concave corners
    return m


def ridge_inside(m, x, y, i, j):
    """Colour of a pixel on a ridge (inside the bank's region): the lit lip on the north, a lit west slope, a
    shaded east slope, a two-tone south slope eight pixels deep, the sunlit crest between."""
    def dist(dx, dy, lim):
        return next((d for d in range(1, lim + 1) if (x + dx * d, y + dy * d) not in m), None)
    dn, ds = dist(0, -1, 3), dist(0, 1, 8)
    dw, de = dist(-1, 0, 5), dist(1, 0, 5)
    if dn == 1:
        return LP
    if ds is not None:                       # the near (south) slope: lighter high up, darker low down
        if ds <= 2:
            return SL2 if (i + j) % 3 else SL3
        if ds <= 5:
            return SL2 if (i + j) % 2 else SL1
        return SL1 if (i + 2 * j) % 3 else GD
    if dn == 2:
        return GL
    if dw is not None:                       # west slope, in the light
        return GL if dw <= 2 or (i + j) % 2 == 0 else grass_px(i, j)
    if de is not None:                       # east slope, in shade
        return SL1 if de <= 2 else (GD if (i + j) % 2 == 0 else SL1)
    if dn == 3:
        return GL if (i + j) % 2 == 0 else grass_px(i, j)
    return GL if (i + j) % 2 == 0 and (i + 3 * j) % 4 != 0 else grass_px(i, j)     # the sunlit crest


def berm_tile(bits, face_h=6, rows=1, style="mound"):
    """Draw a corner-set piece: style 'mound' (flat walkable top, rows=2 with face_h ~22 for the tall south face) or
    'ridge' (a raised bank: crest, lip, slopes inside, a two-tone face below)."""
    m = corner_region(bits, extra_rows=16 * (rows - 1))
    cv = Canvas(1, rows)
    if style == "ridge":
        face_h = 7
    for j in range(16 * rows):
        for i in range(16):
            p = (i + 16, j + 16)
            x, y = p
            c = grass_px(i, j)
            if p in m and style == "ridge":
                c = ridge_inside(m, x, y, i, j)
            elif p in m:
                near = min([d for d in range(1, 6) if any(q not in m for q in ((x, y - d), (x - d, y), (x + d, y),
                                                                               (x, y + d)))] or [9])
                if (x, y - 1) not in m:
                    c = LP
                elif (x - 1, y) not in m:
                    c = GL
                elif (x + 1, y) not in m:
                    c = GD
                elif near <= 3 and (i + j) % 2 == 0:
                    c = GL                              # the sunlit crown of the bank
                elif near <= 5 and (i + 2 * j) % 4 == 0:
                    c = GL
            else:
                k = next((k for k in range(1, face_h + 1) if (x, y - k) in m), None)
                if k is not None and style == "ridge":
                    n = hashn(i, j, 14)
                    c = SL3 if k <= 4 else (SL3 if n < 0.6 else E3)        # the bank's foot, in shadow
                    if k == 1:
                        c = SL2
                elif k is not None:
                    t = k / face_h
                    n = hashn(i, j, 12 if rows == 1 else 13)
                    if t <= 0.2:
                        c = SL1
                    elif t <= 0.5:
                        c = SL1 if n < 0.55 else SL2
                    elif t <= 0.8:
                        c = SL2 if n < (0.75 if rows == 1 else 0.9) else E2
                    else:
                        c = SL3 if n < (0.7 if rows == 1 else 0.85) else E3
                    # tufts of grass hanging over the slope's top, earth showing low down
                    if k == 1 and n < 0.3:
                        c = GD
                    if rows > 1 and 0.3 < t < 0.8 and (j % 6 == 3) and n < 0.45:
                        c = SL2 if c == SL1 else SL3      # faint contour terraces down the tall mound
                    if (x - 1, y) in m or (x + 1, y) in m:
                        pass
                elif (x, y - face_h - 1) in m:
                    c = SH
                elif (x + 1, y) in m or (x + 2, y) in m:
                    c = SL1 if (x + 1, y) in m else GD          # west slope (lit side)
                elif (x - 1, y) in m or (x - 2, y) in m:
                    c = SL2 if (x - 1, y) in m else SH          # east slope (shaded side)
                elif (x, y + 1) in m:
                    c = SH                                      # the back slope's edge (seen past the lip)
                elif (x, y + 2) in m and (i % 2 == 0):
                    c = GD
            cv.put(i, j, c)
    return cv


def mound_steps():
    """2x2 steps cut into the mound's south face (row 0 = where two mound_S cells go, row 1 = the two mound_face
    cells under them): five cedar-log risers with packed-earth treads between earth cheeks, the grass lip above."""
    full = Canvas(2, 2)
    s_top = berm_tile("1100", face_h=22, rows=2)
    full.paste(s_top, 0, 0)
    full.paste(s_top, 16, 0)
    top, bot = 9, 30                      # the flight runs from the lip (y 8) to the face's foot
    x0, x1 = 5, 26
    for j in range(top, bot + 1):
        for i in range(x0 - 2, x1 + 3):
            if i < x0 or i > x1:
                full.put(i, j, E2 if (i + j) % 3 else E3)      # earth cheeks
            else:
                full.put(i, j, E1)
    n = 5
    for k in range(n):
        y = top + 1 + k * (bot - top) // n
        full.hline(x0, x1, y, E3)
        full.hline(x0, x1, y + 1, E2)
        full.hline(x0, x1, y + 2, E2)
        full.hline(x0, x1, y + 3, E3)
        full.put(x0, y + 1, E1)
        full.put(x1, y + 2, E3)
        for x in range(x0 + 3, x1, 7):
            full.put(x, y + 2, E3)                              # log end grain
    full.hline(x0 - 2, x1 + 2, top - 1, LP)
    full.hline(x0 - 2, x1 + 2, bot + 1, SH)
    for j in (top + 2, top + 9, top + 15):
        full.put(x0 - 2, j, GD)
        full.put(x1 + 2, j + 2, GD)
    return full


# ---------------------------------------------------------------- the trees and carvings (overlays)
def live_oak():
    """4x3 a live oak: a vast crown far wider than tall, built of overlapping leaf masses (dark under, lit on top);
    a short massive trunk that splits into great limbs reaching out sideways, visible under the crown's edges;
    Spanish moss hanging in clumps; root flare at the foot."""
    cv = Canvas(4, 3)
    cx = 32

    def limb(a, b, w0, w1, sag):
        for t in range(0, 61):
            u = t / 60
            x = a[0] + (b[0] - a[0]) * u
            y = a[1] + (b[1] - a[1]) * u + sag * math.sin(math.pi * u)
            ww = w0 + (w1 - w0) * u
            for k in range(-int(ww), int(ww) + 1):
                c = E1 if k < 0 else (E2 if k < ww - 1 else E3)
                cv.put(round(x), round(y + k), c)
            cv.put(round(x), round(y - ww - 1), INKW)
            cv.put(round(x), round(y + ww + 1), INKW)

    limb((cx - 3, 32), (cx - 27, 26), 3.0, 1.2, 2.5)
    limb((cx + 3, 32), (cx + 27, 27), 3.0, 1.2, 2.5)
    limb((cx - 1, 30), (cx - 12, 19), 2.5, 1.5, 0)
    limb((cx + 1, 30), (cx + 13, 19), 2.5, 1.5, 0)
    for j in range(28, 46):
        w = 5.5 if j < 39 else 5.5 + (j - 39) * 1.1
        for i in range(int(cx - w), int(math.ceil(cx + w))):
            d = (i + 0.5 - cx) / w
            c = E1 if d < -0.3 else (E2 if d < 0.35 else E3)
            if (i * 3 + j * 2) % 13 == 0:
                c = E3
            cv.put(i, j, c)
        cv.put(int(cx - w) - 1, j, INKW)
        cv.put(int(math.ceil(cx + w)), j, INKW)
    cv.hline(cx - 12, cx + 12, 46, INKW)
    # crown masses (x, y, rx, ry): the side masses sit high so the limbs show beneath them
    masses = [(32, 10, 15, 8), (17, 13, 12, 7), (47, 13, 12, 7), (6, 15, 6, 5), (58, 15, 6, 5), (32, 19, 10, 6),
              (24, 6, 8, 5), (41, 6, 8, 5)]
    for (x, y, rx, ry) in masses:
        cv.ellipse(x, y + 1, rx + 1, ry + 1, INKW)
    for (x, y, rx, ry) in masses:
        cv.ellipse(x, y, rx, ry, SL3)
    for (x, y, rx, ry) in masses:
        cv.ellipse(x - 1, y - 1.5, rx - 1.5, ry - 1.8, SL2)
    for (x, y, rx, ry) in masses:
        cv.ellipse(x - 2, y - 2.5, rx - 4, ry - 3.2, LM)
    for (x, y, rx, ry) in masses:
        if rx >= 8:
            cv.ellipse(x - 3.5, y - 3.5, rx - 7.5, ry - 5, LP)
    for j in range(0, 30):
        for i in range(64):
            c = cv.get(i, j)
            n = hashn(i, j, 4)
            if c == LM and n < 0.14:
                cv.put(i, j, SL2)
            elif c == SL2 and n < 0.10:
                cv.put(i, j, SL3)
            elif c == LP and n < 0.2:
                cv.put(i, j, LM)
    # Spanish moss: a few clumps from the crown's underside and from the limbs, irregular lengths
    for (x, ln) in [(3, 6), (9, 4), (14, 8), (21, 5), (42, 6), (49, 8), (55, 4), (60, 6), (26, 4), (38, 5)]:
        y = None
        for j in range(30, 0, -1):
            if cv.get(x, j) in (SL3, INKW, E3, E2, E1):
                y = j
                break
        if y is None:
            continue
        for k in range(1, ln + 1):
            c = MS2 if k % 3 == 1 else MS1
            if cv.get(x, y + k) is None or cv.get(x, y + k) in (INKW,):
                cv.put(x, y + k, c)
            if k < ln - 2 and cv.get(x + 1, y + k) is None:
                cv.put(x + 1, y + k, MS1)
    return cv

def cedar_post(bird=False):
    """1x2 a carved post of weathered red cedar: a squared post with grain lines, notched bands painted ochre and
    clay-white in a zigzag, a carved spiral; a pointed top, or a carved egret standing on it."""
    cv = Canvas(1, 2)
    x0, x1 = 5, 10
    top = 6 if not bird else 10
    for j in range(top, 30):
        for i in range(x0, x1 + 1):
            c = CD2
            if i == x0:
                c = CD3
            elif i >= x1 - 1:
                c = CD1
            elif (i == x0 + 2 and j % 5 != 0) or (i == x0 + 3 and j % 7 == 3):
                c = CD1                                     # grain
            cv.put(i, j, c)
        cv.put(x0 - 1, j, INK)
        cv.put(x1 + 1, j, INK)
    # notched bands with painted zigzags
    for yb in (13, 22):
        cv.hline(x0 - 1, x1 + 1, yb - 1, INK)
        cv.hline(x0, x1, yb, CD1)
        for i in range(x0, x1 + 1):
            cv.put(i, yb + 1, OC if (i % 2 == 0) else CD2)
            cv.put(i, yb + 2, OC if (i % 2 == 1) else ST4)
        cv.hline(x0, x1, yb + 3, CD1)
    # the carved spiral between them
    for (x, y) in [(7, 17), (8, 17), (8, 18), (7, 19), (6, 19), (6, 18), (6, 17), (7, 16), (8, 16), (9, 16)]:
        cv.put(x, y, CD1)
    cv.put(7, 18, CD3)
    cv.ellipse(8, 30, 5, 1.6, INK)
    cv.hline(x0, x1, 29, CD1)
    if not bird:
        cv.hline(x0, x1, top - 1, CD2)
        cv.hline(x0 + 1, x1 - 1, top - 2, CD2)
        cv.put(x0 + 1, top - 2, CD3)
        cv.hline(x0 + 2, x1 - 2, top - 3, CD3)
        for (x, y) in [(x0 - 1, top - 1), (x0, top - 2), (x0 + 1, top - 3), (x1 + 1, top - 1), (x1, top - 2),
                       (x1 - 1, top - 3), (x0 + 2, top - 4), (x0 + 3, top - 4)]:
            cv.put(x, y, INK)
    else:
        # a carved egret standing on the post's flat top, beak to the west, painted clay-white
        cv.hline(x0 - 1, x1 + 1, top - 1, INK)
        body = [(6, 7), (7, 7), (8, 7), (9, 7), (10, 8), (6, 8), (7, 8), (8, 8), (9, 8), (7, 9), (8, 9)]
        for (x, y) in body:
            cv.put(x, y, ST4)
        cv.put(9, 8, ST3)
        cv.put(8, 8, ST3)
        for (x, y) in [(6, 6), (6, 5), (6, 4), (5, 3), (6, 3)]:
            cv.put(x, y, ST4)
        cv.put(3, 3, OC)
        cv.put(4, 3, OC)
        for (x, y) in [(2, 3), (3, 2), (4, 2), (5, 2), (6, 2), (7, 3), (7, 4), (7, 5), (7, 6), (8, 6), (9, 6), (10, 7),
                       (11, 8), (10, 9), (9, 9), (6, 9), (5, 8), (5, 7), (5, 6), (5, 5), (5, 4), (4, 4), (3, 4)]:
            if cv.get(x, y) is None:
                cv.put(x, y, INK)
        cv.put(7, 9, CD1)
        cv.put(8, 9, CD1)
    return cv

def standing_stone(tall=True):
    """A standing stone in the Rootkin stone of Route 25's steps: tall 1x2 (a weathered upright slab, rounded top) or
    small 1x1 (a squat boulder-stone), a carved spiral, lichen, its shadow."""
    cv = Canvas(1, 2 if tall else 1)
    H = 32 if tall else 16
    top = 3 if tall else 6
    bot = H - 3
    body = set()
    for j in range(top, bot):
        t = (j - top) / max(1, bot - top)
        hw = (4.0 + 1.0 * t) if tall else (4.5 + 1.5 * math.sin(math.pi * min(1, t * 1.4)) * 0.6)
        if j < top + 2:
            hw -= 1.6 - 0.8 * (j - top)
        for i in range(16):
            if abs(i + 0.5 - 8) <= hw:
                body.add((i, j))
    for (i, j) in body:
        u = (i + 0.5 - 8)
        c = ST4 if u < -2.0 else (ST3 if u < 2.2 else ST2)
        cv.put(i, j, c)
    for (i, j) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            if (i + dx, j + dy) not in body:
                cv.put(i + dx, j + dy, INK)
    sy = 12 if tall else 10
    for (x, y) in [(7, sy), (8, sy), (9, sy + 1), (8, sy + 2), (7, sy + 2), (6, sy + 1), (6, sy), (7, sy - 1),
                   (8, sy - 1)]:
        cv.put(x, y, ST2)
    cv.put(8, sy + 1, ST4)
    for (x, y) in ([(6, 20), (7, 21), (9, 6), (6, 25), (7, 26)] if tall else [(6, 12), (9, 8)]):
        if (x, y) in body:
            cv.put(x, y, MO)
    cv.ellipse(8, bot + 0.5, 6, 1.6, INK)
    cv.hline(4, 12, bot - 1, ST2)
    return cv

def singing_stone():
    """2x2 the singing stone: a tall monolith leaning a little west, weathered, bored through by one great hole high
    on its shoulder and two small ones (the wind sings in them), a spiral carved low on its face, lichen, shells and
    an ochre-smeared offering stone at its foot."""
    cv = Canvas(2, 2)
    top, bot = 1, 28
    body = {}
    for j in range(top, bot):
        t = (j - top) / (bot - top)
        hw = 6.5 + 3.5 * t
        if j < top + 4:
            hw -= (4 - (j - top)) * 1.3
        cxj = 16 - 2.5 * (1 - t)                       # the lean
        for i in range(32):
            if abs(i + 0.5 - cxj) <= hw:
                body[(i, j)] = (i + 0.5 - (cxj - hw)) / (2 * hw)
    for (i, j), u in body.items():
        c = ST4 if u < 0.22 else (ST3 if u < 0.72 else ST2)
        if hashn(i, j, 3) < 0.05:
            c = ST2
        cv.put(i, j, c)
    for (i, j) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            if (i + dx, j + dy) not in body:
                cv.put(i + dx, j + dy, INK)
    # the holes
    for (x, y, r) in [(17, 7, 2.6), (12, 15, 1.3), (19, 18, 1.1)]:
        cv.ellipse(x, y, r + 1, r + 1, ST2)
        cv.ellipse(x, y, r, r, INK)
        cv.put(int(x - 1), int(y + r + 0.6), ST4)
    # the spiral low on the face, left of centre
    pts = [(12, 22), (13, 22), (13, 23), (12, 24), (11, 24), (10, 23), (10, 22), (11, 21), (12, 20), (13, 20),
           (14, 21), (14, 22), (14, 23), (14, 24)]
    for (x, y) in pts:
        cv.put(x, y, ST1)
    for (x, y) in [(9, 11), (10, 12), (21, 13), (22, 24), (21, 25), (13, 4)]:
        if (x, y) in body:
            cv.put(x, y, MO)
    cv.ellipse(16, 28.5, 12, 2.4, INK)
    cv.hline(6, 26, 27, ST2)
    # offerings at its foot: shells and an ochre-smeared pebble
    for (x, y, c) in [(23, 28, OC), (24, 28, OC), (24, 29, ST2), (27, 28, ST4), (28, 28, ST4), (27, 29, ST2),
                      (6, 29, ST4), (7, 29, ST4), (6, 30, ST2), (10, 30, ST4)]:
        cv.put(x, y, c)
    return cv

def landing():
    """4x4 the landing steps, opaque. Row 0: the head of the flight on the plaza's grass; rows 1-2: six steps down
    the bank between two carved cheek walls, cedar mooring posts on their tops; row 3: the landing slab at the
    water, the water lapping round its front and sides. Columns 1-2 are walkable (all four rows); the cheeks
    block; a surfer steps onto the slab from the south."""
    cv = Canvas(4, 4)
    for j in range(64):
        for i in range(64):
            cv.put(i, j, grass_px(i, j) if j < 30 else WA)
    # the flight (columns 1-2, x 16..47)
    for j in range(2, 48):
        for i in range(15, 49):
            cv.put(i, j, ST3)
    for k in range(7):
        y = 4 + k * 6
        cv.hline(15, 48, y, ST4)
        cv.hline(15, 48, y + 4, ST2)
        cv.hline(15, 48, y + 5, ST1)
        for x in (21, 33, 42):
            cv.put(x + (k % 2) * 4, y + 2, ST2)
    # the slab at the water (row 3): big flags, lit lip, its face into the water, water round its sides
    cv.rect(10, 46, 44, 12, ST3)
    for x in (10, 25, 39):
        cv.vline(x, 47, 56, ST2)
    cv.hline(10, 53, 46, ST4)
    cv.hline(10, 53, 52, ST2)
    cv.rect(10, 57, 44, 3, ST2)
    cv.hline(10, 53, 60, ST1)
    cv.vline(9, 46, 60, INK)
    cv.vline(54, 46, 60, INK)
    cv.hline(9, 54, 61, INK)
    for x in range(8, 56, 3):
        cv.put(x, 62, RP)
    for j in range(48, 61, 4):
        cv.put(7, j, RP)
        cv.put(56, j + 2, RP)
    for (x, y) in [(20, 59), (31, 58), (44, 59), (13, 55), (49, 50)]:
        cv.put(x, y, MO)
    # cheek walls (columns 0 and 3) down the bank, ending in rounded caps at the slab
    for x0 in (3, 49):
        for j in range(1, 46):
            for i in range(x0, x0 + 12):
                c = ST3
                if i == x0:
                    c = ST4
                elif i == x0 + 11:
                    c = ST2
                cv.put(i, j, c)
            cv.put(x0 - 1, j, INK)
            cv.put(x0 + 12, j, INK)
        cv.hline(x0 - 1, x0 + 12, 0, INK)
        cv.hline(x0, x0 + 11, 1, ST4)
        for j in (18, 32):
            cv.hline(x0, x0 + 11, j, ST2)
        cv.ellipse(x0 + 6, 45, 6.5, 3, ST2)
        cv.hline(x0, x0 + 11, 46, ST1)
        cv.hline(x0 - 1, x0 + 12, 47, INK) if False else None
        cx = x0 + 6
        for (x, y) in [(cx - 1, 25), (cx, 25), (cx + 1, 26), (cx, 27), (cx - 1, 27), (cx - 2, 26), (cx - 2, 25),
                       (cx - 1, 24), (cx + 1, 24)]:
            cv.put(x, y, ST1)
        for (x, y) in [(x0 + 2, 38), (x0 + 3, 39), (x0 + 9, 42), (x0 + 1, 12)]:
            cv.put(x, y, MO)
        px = x0 + 4
        cv.rect(px, 3, 4, 11, CD2)
        cv.vline(px, 3, 13, CD3)
        cv.vline(px + 3, 3, 13, CD1)
        cv.vline(px - 1, 2, 14, INK)
        cv.vline(px + 4, 2, 14, INK)
        cv.hline(px, px + 3, 2, INK)
        cv.hline(px, px + 3, 6, OC)
        cv.hline(px, px + 3, 10, OC)
        cv.hline(px - 1, px + 4, 14, ST2)
    # water and grass outside the cheeks: the bank line (grass above y 30) meets the cheeks' outer faces
    for j in range(28, 32):
        for x in (0, 1, 61, 62, 63):
            cv.put(x, j, GD if j < 30 else WA)
    return cv


def shell_px(x, y):
    """Crushed-shell road: pale shell grit with chips of grey, a few ochre and dark fragments; 16 px period."""
    n = hashn(x % 16, y % 16, 41)
    if n < 0.10:
        return ST3
    if n < 0.14:
        return ST2
    if n < 0.16:
        return OC
    if n > 0.97:
        return GL
    return ST4


def shell_path(key):
    """A cell of the shell road (cell-based 3x3 like the Johto path; key = which sides are the road's edge): the grit
    runs to the cell's edge on the road's inner sides; on an edge side it stops 3-4 px in, with a darker trodden rim
    and grass tufts creeping over."""
    cv = Canvas(1, 1)
    edges = {"N": "n", "S": "s", "W": "w", "E": "e", "NW": "nw", "NE": "ne", "SW": "sw", "SE": "se", "C": ""}[key]
    wob = [3, 4, 4, 3, 3, 4, 3, 3, 4, 4, 3, 4, 3, 3, 4, 3]
    for j in range(16):
        for i in range(16):
            inset = []
            if "n" in edges:
                inset.append(j - wob[i])
            if "s" in edges:
                inset.append(15 - j - wob[(i + 5) % 16])
            if "w" in edges:
                inset.append(i - wob[j])
            if "e" in edges:
                inset.append(15 - i - wob[(j + 7) % 16])
            d = min(inset) if inset else 99
            if d < 0:
                c = grass_px(i, j)
                if d == -1 and hashn(i, j, 5) < 0.4:
                    c = GD
            elif d == 0:
                c = ST2 if hashn(i, j, 3) < 0.6 else ST3
            elif d == 1:
                c = ST3
            else:
                c = shell_px(i, j)
            cv.put(i, j, c)
    return cv


def shell_scatter():
    """1x1 shells on the grass: two oyster shells (grey, ruffled), a white clam, a few chips."""
    cv = Canvas(1, 1)
    for (x, y) in [(3, 9), (4, 9), (5, 9), (4, 10), (5, 10), (3, 10)]:
        cv.put(x, y, ST3)
    cv.put(3, 9, ST2)
    cv.put(5, 11, ST1)
    cv.put(4, 11, ST1)
    for (x, y) in [(10, 5), (11, 5), (10, 6), (11, 6), (12, 6)]:
        cv.put(x, y, ST4)
    cv.put(12, 7, ST2)
    cv.put(11, 7, ST2)
    for (x, y) in [(8, 12), (12, 11), (7, 4), (13, 13)]:
        cv.put(x, y, ST4)
    cv.put(9, 12, OC)
    return cv


def egret_post():
    """1x2 an egret on a weathered cedar post standing in the water: the post's waterline ripples, a white egret
    with its S-curved neck and yellow-ochre bill."""
    cv = Canvas(1, 2)
    for j in range(13, 30):
        cv.put(6, j, CD3)
        cv.put(7, j, CD2)
        cv.put(8, j, CD2)
        cv.put(9, j, CD1)
        cv.put(5, j, INK)
        cv.put(10, j, INK)
    cv.hline(6, 9, 12, CD3)
    cv.hline(5, 10, 11, INK)
    for x in (6, 8):
        cv.put(x, 18, CD1)
    for x in range(3, 13):
        cv.put(x, 30, RP if x % 2 else WA)
    cv.hline(4, 11, 29, RP)
    cv.put(6, 29, CD1)
    cv.put(9, 29, CD1)
    # the egret: body on the post, tail to the east, neck curving up, bill pointing west
    body = [(6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (7, 8), (8, 8), (9, 8), (10, 8), (11, 9), (8, 10), (9, 10)]
    neck = [(6, 7), (5, 6), (5, 5), (6, 4), (6, 3), (5, 2), (4, 2)]
    for (x, y) in body + neck:
        cv.put(x, y, ST4)
    for (x, y) in [(9, 9), (10, 9), (9, 10)]:
        cv.put(x, y, ST3)
    cv.put(2, 2, OC)
    cv.put(3, 2, OC)
    cv.put(8, 11, INK)                      # legs
    cv.put(8, 12, INK) if False else None
    for (x, y) in [(5, 9), (5, 8), (6, 8), (6, 10), (7, 10), (10, 10), (11, 10), (12, 9), (11, 8), (10, 7), (9, 7),
                   (8, 7), (7, 7), (7, 6), (6, 5), (7, 5), (7, 4), (7, 3), (6, 1), (5, 1), (4, 1), (3, 1), (1, 2),
                   (2, 3), (3, 3), (4, 3), (4, 4), (4, 5), (4, 6), (5, 7)]:
        if cv.get(x, y) is None:
            cv.put(x, y, INK)
    return cv


# ---------------------------------------------------------------- the sheet, json
def build():
    sh = Sheet(16)
    meta = {}

    def add(name, cv, kind, walk=False, comment=""):
        sh.add(name, cv)
        meta[name] = {"kind": kind, "walk": walk, "comment": comment}

    for bits, key in CORNER_KEYS.items():
        add("berm_" + key, berm_tile(bits, style="ridge"), "opaque",
            comment=f"ridge bank, corner key {key} ({bits}), on grass" + (" (the crest fill)" if key == "C" else ""))
    for bits, key in CORNER_KEYS.items():
        if key in ("C", "S", "landNE", "landNW"):
            continue
        add("mound_" + key, berm_tile(bits), "opaque",
            comment=f"platform mound, corner key {key} ({bits}): flat walkable top (its C is ekat:grass)")
    for bits, key in (("1100", "S"), ("0100", "landNE"), ("1000", "landNW")):
        tall = berm_tile(bits, face_h=22, rows=2)
        add("mound_" + key, tall.crop(0, 0, 1, 1), "opaque",
            comment=f"platform mound {key}: the slope runs to the cell's foot (the face goes on in the cell below)")
    ext = {"face": "1100", "face_l": "0100", "face_r": "1000"}
    for k, bits in ext.items():
        add("mound_" + k, berm_tile(bits, face_h=22, rows=2).crop(0, 1, 1, 1), "opaque",
            comment=f"platform mound face extension '{k}' (build.py corners() 'face' rule: under S / landNE / landNW)")
    add("mound_steps", mound_steps(), "opaque", walk=True,
        comment="2x2 steps up the mound's south face: row 0 in place of two mound_S, row 1 of two mound_face; walkable")
    for key in ("C", "N", "S", "W", "E", "NW", "NE", "SW", "SE"):
        add("shell_" + key, shell_path(key), "opaque", walk=True,
            comment=f"ceremonial shell road (crushed shell on grass), cell-based like the Johto path: {key}")
    add("egret_post", egret_post(), "overlay", comment="1x2 an egret standing on an old cedar post in the water "
                                                         "(overlay on Ekat water), blocking")
    add("shell_scatter", shell_scatter(), "overlay", walk=True, comment="1x1 oyster and clam shells scattered on the grass by "
                                                             "the shore (overlay on grass), walkable")
    add("live_oak", live_oak(), "overlay", comment="4x3 a live oak with Spanish moss (overlay on grass): blocking; the top "
                                                   "row is canopy (could be drawn over the player)")
    add("cedar_post", cedar_post(False), "overlay", comment="1x2 a carved red-cedar post (overlay on grass), blocking")
    add("cedar_post_bird", cedar_post(True), "overlay", comment="1x2 a cedar post topped by a carved egret, blocking")
    add("stone_tall", standing_stone(True), "overlay", comment="1x2 a standing stone, spiral-carved, blocking")
    add("stone_small", standing_stone(False), "overlay", comment="1x1 a small standing stone, blocking")
    add("singing_stone", singing_stone(), "overlay",
        comment="2x2 the singing stone (bored through, spiral-carved, offerings at its foot), blocking")
    add("landing", landing(), "opaque", walk=[[1, 0], [2, 0], [1, 1], [2, 1], [1, 2], [2, 2], [1, 3], [2, 3]],
        comment="4x4 the landing steps (opaque; row 0 on the plaza's grass, row 3 over the water): columns 1-2 walkable, "
                "the cheek walls block; replaces the placeholder dock")
    sh.pack()
    return sh, meta


def write(sh, meta):
    sh.image.save(os.path.join(HERE, "shrine.png"))
    pieces, opaque_mts, overlay_mts, prefabs = {}, [], [], {}
    for name, p in sh.pieces.items():
        m = meta[name]
        walk = m["walk"]
        walk = [[i, j] for j in range(p["h"]) for i in range(p["w"])] if walk is True else (walk or [])
        rows = []
        for j in range(p["h"]):
            row = []
            for i in range(p["w"]):
                cx, cy = p["x"] + i, p["y"] + j
                if m["kind"] == "opaque":
                    mid = name if p["w"] == p["h"] == 1 else f"{name}_{i}_{j}"
                    opaque_mts.append({"id": mid, "bottom": [cx, cy]})
                    row.append(f"osh:{mid}")
                else:
                    mid = f"{cx}_{cy}"
                    overlay_mts.append({"id": mid, "bottom": [cx, cy]})
                    row.append({"overlay": f"osho:{mid}"})
            rows.append(row)
        pieces[name] = {"x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"], "kind": m["kind"], "walk": walk,
                        "comment": m["comment"]}
        if m["kind"] == "overlay" or name in ("landing", "mound_steps"):
            prefabs[name] = {"_comment": m["comment"], "rows": rows, "door": None, "passable": walk}
    keys = [k for k in CORNER_KEYS.values() if k != "C"]
    berm = {"kind": "corners", "connects": "R", "apply_on": "R.", "elev": 3, "collision": 1, "C": "osh:berm_C",
            "_comment": "the low ridges (grid char R, on grass '.'): blocking berms; keep R two cells from marsh / water "
                        "/ paths (no transition art for those)"}
    berm.update({k: f"osh:berm_{k}" for k in keys})
    mound = dict(berm, connects="M", apply_on="M.", _comment="the platform mound (grid char M): the berm's pieces with "
                 "the tall south face; its top (C) is plain walkable grass: give the edge tiles collision (the corner "
                 "set's 'collision' blocks C too, so set the top back to 0 or use a terrain char for it)")
    mound.update({k: f"osh:mound_{k}" for k in keys})
    mound["C"] = "ekat:grass"
    mound.update({"S": "osh:mound_S", "landNE": "osh:mound_landNE", "landNW": "osh:mound_landNW",
                  "face": {"face": "osh:mound_face", "face_l": "osh:mound_face_l", "face_r": "osh:mound_face_r"}})
    doc = {
        "_comment": "The Oldest Shrine's own art (make_shrine.py): piece -> sheet cells (16 px), kind (opaque metatile or "
                    "overlay drawn over the ground), walkable cells. 'sources' are compose sources for the "
                    "orleans_route_b recipe (opaque 'osh', overlay-only 'osho'), 'autotile' the corner sets for its "
                    "tileset config, 'prefabs' the overlay pieces + the landing and steps as prefabs.",
        "png": "shrine.png",
        "families": {k: [list(c) for c in v] for k, v in FAMILIES.items()},
        "pieces": pieces,
        "sources": [
            {"name": "osh", "type": "image", "image": "tools/mapgen/tilesets/arenas/shrine.png",
             "transparent": [[255, 0, 255]], "metatiles": opaque_mts,
             "_comment": "opaque pieces: the ridge berm and mound sets, the mound steps, the landing"},
            {"name": "osho", "type": "image", "image": "tools/mapgen/tilesets/arenas/shrine.png",
             "transparent": [[255, 0, 255]], "overlay_only": True, "metatiles": overlay_mts,
             "_comment": "overlays (live oak, cedar posts, standing stones, singing stone), drawn over whatever ground"},
        ],
        "autotile": {"berm": berm, "mound": mound},
        "prefabs": prefabs,
    }
    dump(os.path.join(HERE, "shrine.json"), doc)
    return doc


def main():
    sh, meta = build()
    imgs = []
    g = ground("ekat:grass")
    for n, p in sh.pieces.items():
        crop = sh.image.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16)).convert("RGBA")
        if meta[n]["kind"] == "overlay":                    # check overlays as the GBA will show them: over grass
            bg = Image.new("RGBA", crop.size)
            for y in range(0, crop.height, 16):
                for x in range(0, crop.width, 16):
                    bg.paste(g, (x, y))
            px = crop.load()
            for y in range(crop.height):
                for x in range(crop.width):
                    if px[x, y][:3] == (255, 0, 255):
                        px[x, y] = (0, 0, 0, 0)
            bg.alpha_composite(crop)
            crop = bg
        imgs.append((n, crop))
    bad = check_families(imgs, FAMILIES, "shrine")
    for b in bad:
        print("off-family tile:", b)
    write(sh, meta)
    print(f"shrine: {len(sh.pieces)} pieces, sheet {sh.image.size}, {len(bad)} off-family tiles")


if __name__ == "__main__":
    main()

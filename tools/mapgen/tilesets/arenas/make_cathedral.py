"""The Salt Cathedral (Groudon's raid arena, LandsEnd_SaltCathedral): own art for its own secondary tileset.

usage (from the decomp root): python tools/mapgen/tilesets/arenas/make_cathedral.py
writes tools/mapgen/tilesets/arenas/cathedral.png + cathedral.json and recipes/orleans_saltdome.json (source "sc").

The old salt mine under Route 24, a salt dome like Avery Island's: room-and-pillar workings carved into a nave.
    walls       the cut salt face in three rows (the dark overhang, the upper face with its grey strata and cutter
                grooves, the lower face with crystal veins and spall at its foot), side walls, timber sets braced
                against the face, the south rim
    heart       the hot glowing heart in the back wall (7x3): a rift where the salt has cracked open over molten
                light, the salt around it glazed and warm, molten drips
    dais        Groudon's dais (3x2), a block of salt left standing, scorched and glowing at its seams
    floor       the salt floor (tool marks, cracks, crystals, salt dust) and the warm floor near the heart (the glow
                on the salt, glowing seams)
    pillars     carved salt pillars (2x3: capital, banded shaft with a crystal vein, base), one with a timber collar
                and a hung lantern
    mine        rails (straight, curves, the end stop), a salt cart on the rails, timber cribbing, a lantern post,
                crystal clusters, salt blocks and spall
    entry       the timbered adit the shaft comes in by (3x2): rails run out of it; its bottom-middle cell is the exit
Colour families (palettes): SALT, MINE, HEAT; every 8x8 tile fits one (checked).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arena_art import Canvas, Sheet, check_families, hashn, texture, write  # noqa: E402

INK = (32, 32, 40)
SA0, SA1, SA2, SA3, SA4, SA5 = (72, 72, 88), (112, 112, 128), (152, 152, 160), (192, 192, 192), (224, 224, 216), (248, 248, 240)
BA, BD = (184, 168, 168), (128, 120, 128)          # strata: a pinkish-grey band, a dark band
CR1, CR2, CR3 = (176, 208, 232), (232, 240, 248), (224, 184, 200)   # crystal: pale blue, white, pink
TB0, TB1, TB2, TB3 = (64, 40, 32), (104, 72, 48), (144, 104, 64), (184, 144, 96)   # timber
IR1, RU = (64, 64, 72), (152, 88, 56)              # iron, rust
LY1, LY2 = (248, 192, 80), (248, 240, 176)         # lantern light
H0, H1, H2, H3, H4, H5 = (88, 24, 32), (160, 40, 32), (216, 88, 40), (248, 152, 56), (248, 216, 104), (248, 248, 200)
WS1, WS2, WS3 = (200, 152, 136), (232, 200, 168), (160, 112, 112)  # salt lit by the heart

FAMILIES = {
    "SALT": [INK, SA0, SA1, SA2, SA3, SA4, SA5, BA, BD, CR1, CR2, CR3],
    "MINE": [INK, TB0, TB1, TB2, TB3, IR1, RU, LY1, LY2, SA0, SA1, SA2, SA3, SA4, SA5],
    "HEAT": [INK, H0, H1, H2, H3, H4, H5, WS1, WS2, WS3, SA0, SA1, SA2, SA3, SA4],
}


def put_tex(cv, fn, x=0, y=0, w=None, h=None):
    w = cv.w if w is None else w
    h = cv.h if h is None else h
    texture(cv, x, y, w, h, fn)


# ---------------------------------------------------------------- textures
def floor_px(x, y, seed=0):
    """The salt floor, 16 px period: pale salt with the long curved scores the cutting machines left (arcs running
    across the cell edge to edge so neighbouring cells join), a faint grain."""
    sx, sy = x % 16, y % 16
    # two cutter arcs per cell, entering and leaving at the same heights so cells chain east-west
    for base in (4, 12):
        yy = base + round(1.6 * math.sin((sx + (0 if base == 4 else 8)) * math.pi / 8))
        if sy == yy:
            return SA3 if (sx + base) % 5 else SA2
        if sy == yy - 1 and (sx + base) % 3 == 0:
            return SA5
    n = hashn(sx, sy, 17 + seed)
    if n < 0.05:
        return SA3
    if n > 0.96:
        return SA5
    return SA4


def face_px(x, y):
    """The cut salt face: vertical strata (a grey band, a pink band) and horizontal cutter grooves every 8 px."""
    sx, sy = x % 16, y % 16
    band = (sx * 3 + (sy // 5)) % 16
    c = SA3
    if band in (0, 1, 2):
        c = BD if band == 1 else SA2
    elif band in (8, 9, 10):
        c = BA
    elif band == 13:
        c = SA4
    if sy % 8 == 7:
        c = SA1 if c != BD else SA0
    elif sy % 8 == 0:
        c = SA4 if c != BD else SA2
    return c


# ---------------------------------------------------------------- walls
def cap(variant=0):
    """The dark overhang of the face (the wall's top as the GBA shows it): rough salt in shadow, a lit lip."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            n = hashn(i // 2, j // 2, 31 + variant)
            cv.put(i, j, SA0 if n < 0.55 else (SA1 if n < 0.9 else INK))
    for i in range(16):
        cv.put(i, 12, SA1)
        cv.put(i, 13, SA3 if (i + variant) % 6 else SA4)
        cv.put(i, 14, SA4)
        cv.put(i, 15, SA2)
    if variant:
        for (x, y) in [(4, 6), (5, 5), (5, 6), (11, 8)]:
            cv.put(x, y, CR1)
    return cv


def face_hi(kind="plain"):
    cv = Canvas(1, 1)
    put_tex(cv, face_px)
    if kind == "vein":
        pts = [(1, 14), (3, 12), (4, 11), (6, 9), (7, 9), (9, 7), (10, 5), (12, 4), (14, 2)]
        for k in range(len(pts) - 1):
            cv.line(*pts[k], *pts[k + 1], CR1)
        for (x, y) in pts[::2]:
            cv.put(x, y - 1, CR2)
            cv.put(x + 1, y + 1, SA1)
    elif kind == "drill":
        for x in (4, 11):
            cv.vline(x, 2, 12, SA1)
            cv.put(x, 1, INK)
            cv.put(x + 1, 4, SA5)
    return cv


def face_lo(kind="plain", seed=0):
    """Lower face: strata, a crystal vein or a cluster, spall heaped at the foot, a shadow line on the floor."""
    cv = Canvas(1, 1)
    put_tex(cv, lambda i, j: face_px(i, j + 8))
    for i in range(16):
        h = 2 + int(3 * hashn(i // 2, 0, seed))
        for j in range(15 - h, 15):
            cv.put(i, j, SA4 if hashn(i, j, seed + 3) < 0.6 else SA3)
        cv.put(i, 15 - h - 1, SA2) if hashn(i, 9, seed) < 0.5 else None
        cv.put(i, 15, SA1)
    if kind == "crystal":
        for (x, y) in [(5, 9), (6, 8), (6, 7), (7, 9), (4, 10), (8, 10), (10, 9), (11, 8), (11, 10)]:
            cv.put(x, y, CR1)
        for (x, y) in [(6, 6), (11, 7)]:
            cv.put(x, y, CR2)
        cv.put(7, 8, CR3)
    elif kind == "vein":
        cv.line(2, 2, 7, 6, CR1)
        cv.line(7, 6, 13, 4, CR1)
        cv.put(7, 5, CR2)
    return cv


def side(right=False):
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            n = hashn(i // 2, j // 2, 44)
            cv.put(i, j, SA0 if n < 0.6 else SA1)
    for j in range(16):
        cv.put(11, j, SA1)
        cv.put(12, j, SA2)
        cv.put(13, j, SA4 if j % 7 else SA3)
        cv.put(14, j, SA3)
        cv.put(15, j, SA1)
    if right:
        cv.flip_x()
    return cv


def rim_s(kind="plain"):
    """The room's south edge seen from above: the floor ends at a lit lip and drops into darkness."""
    cv = Canvas(1, 1)
    put_tex(cv, floor_px, 0, 0, 16, 4)
    for i in range(16):
        cv.put(i, 4, SA5)
        cv.put(i, 5, SA3)
        cv.put(i, 6, SA2)
        for j in range(7, 16):
            n = hashn(i // 2, j // 2, 51)
            cv.put(i, j, SA0 if j < 10 and n < 0.6 else (SA1 if j < 9 else INK))
    return cv


def timber_set():
    """3x2 a timber set braced against the face (rows: upper face, lower face): two posts, the header beam, wedges,
    a lantern hung on the left post."""
    cv = Canvas(3, 2)
    for k in range(3):
        cv.paste(face_hi(), 16 * k, 0)
        cv.paste(face_lo("plain", 5 + k), 16 * k, 16)
    cv.recolor({BA: SA3, BD: SA2})        # the face behind the timbers carries the mine palette (no strata colours)
    for x0 in (5, 37):
        cv.rect(x0, 4, 6, 26, TB2)
        cv.vline(x0, 4, 29, TB3)
        cv.vline(x0 + 5, 4, 29, TB1)
        cv.vline(x0 - 1, 4, 30, TB0)
        cv.vline(x0 + 6, 4, 30, TB0)
        for y in (10, 18, 25):
            cv.hline(x0 + 1, x0 + 4, y, TB1)
        cv.rect(x0 - 1, 29, 8, 2, TB1)
        cv.hline(x0 - 2, x0 + 7, 31, INK)
    cv.rect(2, 1, 44, 6, TB2)
    cv.hline(2, 45, 1, TB3)
    cv.hline(2, 45, 6, TB1)
    cv.hline(2, 45, 7, TB0)
    cv.hline(2, 45, 0, TB0)
    cv.vline(1, 0, 7, TB0)
    cv.vline(46, 0, 7, TB0)
    for x in (12, 24, 33):
        cv.put(x, 3, TB1)
        cv.put(x + 1, 4, TB1)
    for x in (4, 36):
        cv.rect(x, 8, 8, 2, TB3)
        cv.hline(x, x + 7, 10, TB0)
    # lantern on the left post
    cv.vline(13, 8, 11, IR1)
    cv.rect(12, 12, 4, 5, IR1)
    cv.rect(13, 13, 2, 3, LY2)
    cv.put(12, 17, IR1)
    cv.put(15, 17, IR1)
    for (x, y) in [(11, 14), (16, 14), (14, 18), (13, 11)]:
        cv.put(x, y, LY1)
    return cv


# ---------------------------------------------------------------- the heart
def heart():
    """7x3 the hot glowing heart in the back wall (rows: overhang, upper face, lower face): a tall rift where the salt
    has split open over molten light: the white-yellow core deep inside, orange and red toward its jagged lips, dark
    shards of salt across it, the salt around it glazed warm, molten salt running down to the floor, embers."""
    cv = Canvas(7, 3)
    for k in range(7):
        cv.paste(cap(k % 2), 16 * k, 0)
        cv.paste(face_hi(), 16 * k, 16)
        cv.paste(face_lo("plain", 11 + k), 16 * k, 32)
    W = 112
    cx = W / 2
    # warm light on the salt, decided per 8x8 tile (a tile is all salt-family or all heat-family); inside a warm tile
    # the share of warm pixels falls off with distance, so the tile edges don't read
    warm = {SA5: WS2, SA4: WS2, SA3: WS1, BA: WS1, SA2: WS3, BD: WS3, CR1: H4, CR2: H5, CR3: H3}
    cool = {SA5: SA4, BA: SA3, BD: SA2, CR1: SA4, CR2: SA4, CR3: SA3}
    for ty in range(0, 48, 8):
        for tx in range(0, W, 8):
            dt = math.hypot((tx + 4 - cx) / 46.0, (ty + 4 - 30) / 24.0)
            if dt >= 1.0:
                continue
            for j in range(ty, ty + 8):
                for i in range(tx, tx + 8):
                    c = cv.get(i, j)
                    d = math.hypot((i + 0.5 - cx) / 46.0, (j + 0.5 - 30) / 24.0)
                    p = max(0.0, min(1.0, (1.0 - d) / 0.45))
                    cv.put(i, j, warm.get(c, c) if hashn(i, j, 71) < p else cool.get(c, c))

    def lip(j):                      # half-width of the rift at row j: a tall jagged slot, widest low in the face
        if j < 3 or j > 45:
            return 0.0
        t = (j - 3) / 42.0
        base = 5 + 13 * math.sin(math.pi * min(1.0, t * 1.1)) ** 1.3
        return base + 2.5 * math.sin(j * 1.9) + 1.5 * math.sin(j * 0.7 + 1)

    for j in range(48):
        hw = lip(j)
        if hw <= 0:
            continue
        off = 3 * math.sin(j * 0.21)
        for i in range(W):
            d = abs(i + 0.5 - cx - off) / hw
            depth = (j - 3) / 42.0
            if d <= 1.0:
                core = d * (1.15 - 0.45 * depth)
                c = H5 if core < 0.22 else (H4 if core < 0.42 else (H3 if core < 0.62 else (H2 if core < 0.8 else H1)))
                cv.put(i, j, c)
            elif d <= 1.18:
                cv.put(i, j, H0)
            elif d <= 1.3 and (i + j) % 2 == 0:
                cv.put(i, j, WS3)
    for (x0, y0, x1, y1) in [(cx - 12, 15, cx - 2, 19), (cx + 2, 26, cx + 13, 23), (cx - 9, 35, cx + 1, 38)]:
        cv.line(x0, y0, x1, y1, H0)
        cv.line(x0, y0 + 1, x1, y1 + 1, H1)
    for (x, y0, n) in [(cx - 17, 36, 10), (cx + 16, 35, 11), (cx - 6, 43, 4), (cx + 7, 42, 5)]:
        for k in range(n):
            y = y0 + k
            if y < 48:
                cv.put(x, y, H3 if k < n - 2 else H4)
                cv.put(x + 1, y, H2 if k % 3 else H3)
    for (x, y) in [(cx - 26, 12), (cx + 22, 12), (cx - 22, 28), (cx + 26, 22), (cx - 30, 20)]:
        cv.put(x, y, H4)
    # any tile the glow reached carries the heat palette: its leftover strata / crystal colours go to plain salt
    hot = {H0, H1, H2, H3, H4, H5, WS1, WS2, WS3}
    for ty in range(0, 48, 8):
        for tx in range(0, W, 8):
            px = [(i, j) for j in range(ty, ty + 8) for i in range(tx, tx + 8)]
            if any(cv.get(i, j) in hot for i, j in px):
                for i, j in px:
                    c = cv.get(i, j)
                    cv.put(i, j, cool.get(c, c))
    return cv

def dais():
    """3x2 Groudon's dais: a block of salt left standing in front of the heart, its top cracked with glowing seams,
    its front face glazed by the heat, salt spall at its foot."""
    cv = Canvas(3, 2)
    put_tex(cv, lambda i, j: warm_px(i, j, 0))
    # block: a roughly hewn slab of salt, rounded corners and a ragged rim; top (y 3..17), front face (18..27)
    body = set()
    for j in range(2, 28):
        for i in range(1, 47):
            cxd = max(0, abs(i + 0.5 - 24) - 18)
            cyd = max(0, abs(j + 0.5 - 15) - 8)
            r = 4.5 + 1.5 * hashn(i // 3, j // 3, 2)
            if cxd * cxd + cyd * cyd <= r * r:
                body.add((i, j))
    for (i, j) in body:
        top_face = j < 18 + (1 if (i // 5) % 2 else 0)
        c = (SA4 if hashn(i // 2, j // 2, 8) < 0.8 else WS2) if top_face else (WS1 if (i // 9) % 2 else WS3)
        cv.put(i, j, c)
    for (i, j) in body:
        if (i, j - 1) not in body:
            cv.put(i, j, WS2)
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (i + dx, j + dy) not in body:
                cv.put(i + dx, j + dy, INK)
    for x in range(4, 45):
        y = 18 + (1 if (x // 5) % 2 else 0)
        if (x, y) in body:
            cv.put(x, y, WS2)
    # glowing seams across the top
    seam = [(6, 9), (10, 10), (14, 8), (19, 11), (24, 10), (28, 12), (33, 9), (38, 11), (42, 10)]
    for k in range(len(seam) - 1):
        cv.line(*seam[k], *seam[k + 1], H2)
    for (x, y) in seam[1::2]:
        cv.put(x, y, H4)
    cv.line(24, 10, 22, 16, H2)
    cv.line(33, 9, 35, 4, H2)
    # spall at the foot
    for x in range(1, 47, 3):
        if hashn(x, 0, 9) < 0.6:
            cv.put(x, 29, WS2)
            cv.put(x + 1, 29, WS1)
            cv.put(x, 30, WS3)
    return cv


def warm_px(x, y, seed=0):
    """The salt floor lit by the heart: the same scores as floor_px, in warm tones."""
    c = floor_px(x, y, seed)
    return {SA5: WS2, SA4: WS2, SA3: WS1, SA2: WS3}.get(c, c)


def floor(kind="plain", seed=0):
    cv = Canvas(1, 1)
    put_tex(cv, lambda i, j: floor_px(i, j, seed))
    if kind == "crack":
        pts = [(1, 12), (4, 10), (6, 10), (9, 7), (12, 6), (15, 3)]
        for k in range(len(pts) - 1):
            cv.line(*pts[k], *pts[k + 1], SA1)
        for (x, y) in pts:
            cv.put(x, y + 1, SA5)
    elif kind == "crystals":
        for (x, y) in [(4, 10), (5, 9), (5, 8), (6, 10), (11, 6), (12, 5), (12, 7), (10, 7)]:
            cv.put(x, y, CR1)
        cv.put(5, 7, CR2)
        cv.put(12, 4, CR2)
        cv.put(6, 9, CR3)
        cv.hline(3, 7, 11, SA2)
        cv.hline(10, 13, 8, SA2)
    elif kind == "dust":
        for j in range(16):
            for i in range(16):
                v = ((i - 8) / 7.5) ** 2 + ((j - 9) / 5.0) ** 2
                if v < 1.0 - 0.3 * hashn(i // 2, j // 2, seed + 4):
                    cv.put(i, j, SA5 if v < 0.5 else (SA4 if (i + j) % 2 else SA5))
        cv.hline(4, 12, 14, SA3)
    return cv


def warm_floor(kind="plain", seed=0):
    """The floor in the heart's light. 'core' is the hottest (orange flecks); fade_<side> loses the glow toward that
    side (s, w, e, sw, se), a dithered falloff so the warm zone has no hard edge."""
    cv = Canvas(1, 1)
    put_tex(cv, lambda i, j: warm_px(i, j, seed))
    if kind == "seam":
        pts = [(0, 9), (3, 8), (6, 10), (9, 9), (12, 11), (15, 10)]
        for k in range(len(pts) - 1):
            cv.line(*pts[k], *pts[k + 1], H2)
        for (x, y) in pts[1:-1]:
            cv.put(x, y, H4)
            cv.put(x, y - 1, H1)
    elif kind == "seam_v":
        pts = [(8, 0), (7, 4), (9, 8), (8, 12), (9, 15)]
        for k in range(len(pts) - 1):
            cv.line(*pts[k], *pts[k + 1], H2)
        cv.put(7, 4, H4)
        cv.put(8, 12, H4)
    elif kind == "glaze":
        for j in range(16):
            for i in range(16):
                if ((i - 8) / 7.0) ** 2 + ((j - 8) / 5.0) ** 2 < 1.0 and (i * 3 + j) % 4 != 0:
                    cv.put(i, j, WS1 if (i + j) % 3 else H3)
        cv.put(6, 6, H4)
        cv.put(10, 9, H4)
    elif kind == "core":
        for j in range(16):
            for i in range(16):
                if hashn(i, j, 23) < 0.12:
                    cv.put(i, j, H3 if hashn(i, j, 5) < 0.5 else WS1)
    elif kind.startswith("fade_"):
        side = kind[5:]

        def t(i, j):                 # 0 = fully warm, 1 = fully plain, along the faded side(s)
            v = 0.0
            if "s" in side:
                v = max(v, (j + 0.5) / 16)
            if "w" in side:
                v = max(v, 1 - (i + 0.5) / 16)
            if "e" in side:
                v = max(v, (i + 0.5) / 16)
            return v

        def px(i, j):
            if hashn(i, j, 61) < 1.0 - t(i, j) * 1.15:
                return warm_px(i, j, seed)
            c = floor_px(i, j, seed)
            return {SA5: SA4}.get(c, c)
        put_tex(cv, px)
    return cv


# ---------------------------------------------------------------- pillars and mine furniture
def pillar(kind="plain"):
    """2x3 a carved salt pillar: a stepped capital with a carved cross of strata, a banded shaft with a crystal vein,
    a broad base with spall. 'timber': a timber collar round the shaft and a lantern hung on it."""
    cv = Canvas(2, 3)
    put_tex(cv, floor_px)
    # shaft
    for j in range(8, 42):
        for i in range(5, 27):
            c = face_px(i, j)
            if i == 5:
                c = SA5
            elif i == 6:
                c = SA4 if c != BD else SA3
            elif i >= 24:
                c = SA1 if i == 26 else SA2
            cv.put(i, j, c)
        cv.put(4, j, INK)
        cv.put(27, j, INK)
    # vein
    pts = [(10, 40), (12, 33), (11, 28), (15, 22), (14, 16), (17, 11)]
    for k in range(len(pts) - 1):
        cv.line(*pts[k], *pts[k + 1], CR1)
    for (x, y) in pts[1::2]:
        cv.put(x + 1, y, CR2)
    # capital: two stepped courses
    cv.rect(1, 0, 30, 5, SA4)
    cv.hline(1, 30, 0, SA5)
    cv.hline(1, 30, 4, SA2)
    cv.rect(3, 5, 26, 3, SA3)
    cv.hline(3, 28, 7, SA1)
    cv.vline(0, 0, 4, INK)
    cv.vline(31, 0, 4, INK)
    cv.vline(2, 5, 7, INK)
    cv.vline(29, 5, 7, INK)
    for x in range(6, 27, 5):
        cv.put(x, 2, SA2)
    # base
    cv.rect(2, 41, 28, 4, SA3)
    cv.hline(2, 29, 41, SA5)
    cv.hline(2, 29, 44, SA1)
    cv.rect(1, 45, 30, 2, SA2)
    cv.hline(0, 31, 47, INK)
    cv.vline(1, 41, 46, INK)
    cv.vline(30, 41, 46, INK)
    for x in range(0, 32, 4):
        if hashn(x, 2, 6) < 0.6:
            cv.put(x, 46, SA4)
    if kind == "timber":
        # the collar's tiles carry the mine palette: no strata or vein colours in tile rows 2-4 of the shaft
        for j in range(16, 40):
            for i in range(32):
                c = cv.get(i, j)
                cv.put(i, j, {BA: SA3, BD: SA2, CR1: SA4, CR2: SA5, CR3: SA3}.get(c, c)) if c else None
        cv.rect(4, 22, 24, 6, TB2)
        cv.hline(4, 27, 22, TB3)
        cv.hline(4, 27, 27, TB0)
        cv.vline(3, 22, 27, TB0)
        cv.vline(28, 22, 27, TB0)
        for x in (9, 16, 22):
            cv.vline(x, 23, 26, TB1)
        # lantern hung on the collar's front
        cv.vline(16, 28, 29, IR1)
        cv.rect(14, 30, 5, 6, IR1)
        cv.rect(15, 31, 3, 4, LY2)
        cv.put(16, 33, LY1)
        for (x, y) in [(12, 32), (20, 32), (16, 37)]:
            cv.put(x, y, LY1)
    return cv


RAIL_GAUGE = (4, 11)   # rail columns of a north-south track in a 16 px cell


def rails(kind):
    """Rails on the salt floor, 1x1: v, h, end (a stop block, the track running south)."""
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    if kind == "v":
        for y in (2, 10):
            cv.hline(2, 13, y, TB1)
            cv.hline(2, 13, y + 1, TB0)
        for x in RAIL_GAUGE:
            cv.vline(x, 0, 15, IR1)
            cv.vline(x + 1, 0, 15, SA2)
    elif kind == "h":
        for x in (2, 10):
            cv.vline(x, 2, 13, TB1)
            cv.vline(x + 1, 2, 13, TB0)
        for y in RAIL_GAUGE:
            cv.hline(0, 15, y, IR1)
            cv.hline(0, 15, y + 1, SA2)
    elif kind == "end":
        for y in (6, 12):
            cv.hline(2, 13, y, TB1)
            cv.hline(2, 13, y + 1, TB0)
        for x in RAIL_GAUGE:
            cv.vline(x, 5, 15, IR1)
            cv.vline(x + 1, 5, 15, SA2)
        cv.rect(2, 1, 12, 5, TB2)
        cv.hline(2, 13, 1, TB3)
        cv.hline(2, 13, 5, TB0)
        cv.vline(1, 1, 5, TB0)
        cv.vline(14, 1, 5, TB0)
        cv.put(4, 3, RU)
        cv.put(11, 3, RU)
    return cv


def rail_curve(kind):
    """2x2 a quarter turn of track (ne joins north and east: in at the top-left cell's north side, out at the
    bottom-right cell's east side; nw, se, sw likewise). The rails run at the gauge radii about the block's corner
    between its two open sides, the ties lie radially; the fourth cell (the inside of the turn) is plain floor."""
    cv = Canvas(2, 2)
    put_tex(cv, floor_px)
    ox = 32 if "e" in kind else 0
    oy = 0 if "n" in kind else 32
    sx = -1 if ox else 1
    sy = 1 if oy == 0 else -1
    r_in, r_out = 32 - RAIL_GAUGE[1] - 0.5, 32 - RAIL_GAUGE[0] - 0.5   # the gauge, measured from the corner
    for k in range(7):
        ang = math.radians(6 + k * 13)
        for t in range(0, 2):
            pts = []
            for r in (r_in - 2.5, r_out + 2.5):
                pts.append((ox + sx * r * math.cos(ang), oy + sy * r * math.sin(ang)))
            (x0, y0), (x1, y1) = pts
            cv.line(int(math.floor(x0 + 0.0 * t)), int(math.floor(y0)) + t, int(math.floor(x1)), int(math.floor(y1)) + t,
                    TB1 if t == 0 else TB0)
    for r in (r_in, r_out):
        for k in range(240):
            ang = math.radians(90 * k / 239)
            x = ox + sx * r * math.cos(ang)
            y = oy + sy * r * math.sin(ang)
            cv.put(int(math.floor(x)), int(math.floor(y)), IR1)
            if cv.get(int(math.floor(x)), int(math.floor(y)) + 1) != IR1:
                cv.put(int(math.floor(x)), int(math.floor(y)) + 1, SA2)
    for r in (r_in, r_out):
        for k in range(240):
            ang = math.radians(90 * k / 239)
            cv.put(int(math.floor(ox + sx * r * math.cos(ang))), int(math.floor(oy + sy * r * math.sin(ang))), IR1)
    return cv

def cart():
    """1x2 a salt cart standing on the north-south rails, heaped with salt lumps, rust on its iron sides."""
    cv = Canvas(1, 2)
    put_tex(cv, floor_px)
    for y in (6, 14, 22, 28):
        cv.hline(2, 13, y, TB1)
        cv.hline(2, 13, y + 1, TB0)
    for x in RAIL_GAUGE:
        cv.vline(x, 0, 31, IR1)
        cv.vline(x + 1, 0, 31, SA2)
    # body
    cv.rect(1, 5, 14, 22, IR1)
    cv.rect(2, 6, 12, 20, SA1)
    cv.rect(2, 16, 12, 10, IR1)
    cv.hline(2, 13, 16, SA2)
    for (x, y) in [(3, 18), (9, 20), (12, 23), (5, 24)]:
        cv.put(x, y, RU)
    cv.vline(1, 5, 26, INK)
    cv.vline(14, 5, 26, INK)
    cv.hline(1, 14, 27, INK)
    # salt heaped above the rim
    for j in range(2, 16):
        for i in range(2, 14):
            v = ((i + 0.5 - 8) / 6.5) ** 2 + ((j + 0.5 - 10) / 7.0) ** 2
            if v < 1.0:
                n = hashn(i // 2, j // 2, 12)
                cv.put(i, j, SA5 if n < 0.45 else (SA4 if n < 0.8 else SA3))
    for (x, y) in [(5, 6), (9, 4), (11, 9), (6, 11)]:
        cv.put(x, y, SA2)
    # wheels peeking out
    for (x, y) in [(0, 9), (15, 9), (0, 21), (15, 21)]:
        cv.rect(x, y, 1, 3, INK)
    return cv


def cribbing():
    """2x2 mine cribbing: a square crib of round logs notched together in alternating courses, the way roof supports
    are built in old mines. Each east-west log runs past the corners and shows its pale cut end; between them the
    north-south logs show only their cut ends at the corners, with the next log back in the shadow between. The top
    course is seen from above: two side logs lying over the back log, the dark hollow of the crib between."""
    cv = Canvas(2, 2)
    put_tex(cv, floor_px)

    def log_ew(y, x0, x1, dark=False):
        rows = [TB3, TB2, TB2, TB1, TB0] if not dark else [TB1, TB1, TB0, TB0, INK]
        for k, c in enumerate(rows):
            cv.hline(x0, x1, y + k, c)
        if not dark:
            for x in range(x0 + 3, x1 - 1, 5):
                cv.put(x, y + 2, TB1)              # bark checks
                cv.put(x + 1, y + 1, TB3)
        cv.hline(x0, x1, y - 1, INK) if not dark else None
        cv.hline(x0, x1, y + 5, INK) if not dark else None

    def end(x, y):
        """A cut log end, 4 x 5: dark ring, pale face, the heart."""
        cv.rect(x, y, 4, 5, TB1)
        cv.rect(x + 1, y + 1, 2, 3, TB3)
        cv.put(x + 1, y + 1, LY2)
        cv.put(x + 2, y + 2, TB2)
        for (px, py) in [(x, y), (x + 3, y), (x, y + 4), (x + 3, y + 4)]:
            cv.put(px, py, INK)
        cv.vline(x - 1, y + 1, y + 3, INK)
        cv.vline(x + 4, y + 1, y + 3, INK)
        cv.hline(x + 1, x + 2, y - 1, INK)
        cv.hline(x + 1, x + 2, y + 5, INK)

    # soft shadow at the foot
    for x in range(1, 31):
        cv.put(x, 30, SA1 if 2 < x < 29 else SA2)
    # front courses, bottom up: east-west logs (with their cut ends past the corners) alternating with gaps where
    # the north-south logs show their ends and the back log sits in shadow
    for y, kind in ((25, "log"), (20, "gap"), (15, "log"), (10, "gap")):
        if kind == "log":
            log_ew(y, 4, 27)
            end(0, y)
            end(28, y)
        else:
            cv.rect(6, y, 20, 5, SA0)
            log_ew(y, 6, 25, dark=True)
            end(3, y)
            end(25, y)
    # the top course from above: the back log, the two side logs over it, the hollow between
    cv.rect(8, 4, 16, 6, SA0)
    log_ew(1, 4, 27)
    end(0, 1)
    end(28, 1)
    for x0 in (3, 25):
        cv.rect(x0, 2, 4, 9, TB2)
        cv.vline(x0, 2, 10, TB3)
        cv.vline(x0 + 3, 2, 10, TB1)
        cv.vline(x0 - 1, 2, 10, INK)
        cv.vline(x0 + 4, 2, 10, INK)
        cv.put(x0 + 1, 5, TB1)
        cv.put(x0 + 2, 8, TB1)
    return cv

def lantern_post():
    """1x2 a timber post with a lit lantern on a hook."""
    cv = Canvas(1, 2)
    put_tex(cv, floor_px)
    cv.rect(6, 2, 4, 26, TB2)
    cv.vline(6, 2, 27, TB3)
    cv.vline(9, 2, 27, TB1)
    cv.vline(5, 2, 28, TB0)
    cv.vline(10, 2, 28, TB0)
    cv.hline(5, 10, 1, TB0)
    cv.rect(4, 27, 8, 2, TB1)
    cv.hline(3, 12, 29, INK)
    cv.hline(10, 13, 6, IR1)
    cv.vline(13, 6, 8, IR1)
    cv.rect(11, 9, 5, 6, IR1)
    cv.rect(12, 10, 3, 4, LY2)
    cv.put(13, 12, LY1)
    for (x, y) in [(10, 11), (15, 16), (12, 16)]:
        cv.put(x, y, LY1)
    return cv


def crystal(big=False):
    """A cluster of salt crystals (halite cubes) growing from the floor: 1x1, or 2x2."""
    n = 2 if big else 1
    cv = Canvas(n, n)
    put_tex(cv, floor_px)
    cubes = ([(5, 9, 5), (10, 11, 4), (8, 5, 3)] if not big else
             [(10, 22, 9), (20, 24, 7), (15, 13, 7), (6, 14, 5), (24, 15, 5), (17, 4, 4)])
    for (x, y, s) in cubes:
        # a cube: lit top, pale left face, blue right face, outline
        cv.rect(x - s // 2, y - s // 2, s, s, CR1)
        cv.rect(x - s // 2, y - s // 2, s // 2, s, CR2)
        cv.hline(x - s // 2, x + s // 2 - 1, y - s // 2, CR2)
        cv.put(x - s // 2 + 1, y - s // 2 + 1, SA5)
        cv.hline(x - s // 2, x + s // 2 - 1, y + s // 2, SA1)
        if s >= 5:
            cv.put(x, y, CR3)
        for i in range(x - s // 2 - 1, x + s // 2 + 1):
            if cv.get(i, y - s // 2 - 1) in (SA3, SA4, SA5, SA2):
                cv.put(i, y - s // 2 - 1, SA1)
        cv.vline(x - s // 2 - 1, y - s // 2, y + s // 2, SA1)
        cv.vline(x + s // 2, y - s // 2, y + s // 2, SA1)
    return cv


def salt_blocks():
    """2x1 cut salt blocks stacked beside the track."""
    cv = Canvas(2, 1)
    put_tex(cv, floor_px)
    for (x, y, w, h) in [(2, 7, 12, 7), (14, 8, 13, 6), (7, 2, 12, 6)]:
        cv.rect(x, y, w, h, SA4)
        cv.hline(x, x + w - 1, y, SA5)
        cv.hline(x, x + w - 1, y + h - 1, SA2)
        cv.vline(x + w - 1, y, y + h - 1, SA2)
        cv.vline(x - 1, y, y + h - 1, SA1)
        cv.vline(x + w, y, y + h - 1, SA1)
        cv.hline(x, x + w - 1, y + h, SA1)
        cv.put(x + 2, y + 2, SA3)
    return cv


def spall():
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    for (x, y, r) in [(5, 10, 3.5), (11, 11, 3), (8, 6, 2.5)]:
        cv.ellipse(x, y + 1, r, r * 0.8, SA1)
        cv.ellipse(x, y, r, r * 0.75, SA4)
        cv.put(int(x - 1), int(y - 1), SA5)
    return cv


def adit():
    """3x2 the timbered adit the shaft comes down to, in the south rim: a timber set over the dark gallery, rails
    running in, a lantern on the right post. Row 1 middle is the exit (walk south into the dark)."""
    cv = Canvas(3, 2)
    cv.paste(rim_s(), 0, 0)
    cv.paste(rim_s(), 32, 0)
    cv.paste(rim_s(), 0, 16)
    cv.paste(rim_s(), 32, 16)
    for k in (0, 2):
        for j in range(16, 32):
            for i in range(16):
                n = hashn(i // 2, j // 2, 52)
                cv.put(16 * k + i, j, SA0 if n < 0.5 else INK)
    put_tex(cv, floor_px, 16, 0, 16, 8)
    # the dark gallery
    cv.rect(10, 6, 28, 26, INK)
    for j in range(6, 32):
        for i in range(12, 36):
            if j < 12 or hashn(i, j, 3) < 0.05:
                cv.put(i, j, SA0 if j < 9 else INK)
    # rails running in (fading into the dark)
    for x in (16 + RAIL_GAUGE[0], 16 + RAIL_GAUGE[1]):
        cv.vline(x, 0, 22, IR1)
        cv.vline(x + 1, 0, 14, SA2)
    for y in (2, 10, 18):
        cv.hline(18, 29, y, TB1 if y < 14 else TB0)
    # the timber set: two posts and the cap
    for x0 in (7, 35):
        cv.rect(x0, 4, 6, 28, TB2)
        cv.vline(x0, 4, 31, TB3)
        cv.vline(x0 + 5, 4, 31, TB1)
        cv.vline(x0 - 1, 4, 31, TB0)
        cv.vline(x0 + 6, 4, 31, TB0)
    cv.rect(4, 0, 40, 6, TB2)
    cv.hline(4, 43, 0, TB3)
    cv.hline(4, 43, 5, TB0)
    cv.vline(3, 0, 5, TB0)
    cv.vline(44, 0, 5, TB0)
    for x in (12, 23, 34):
        cv.put(x, 2, TB1)
        cv.put(x + 1, 3, TB1)
    # lantern
    cv.rect(41, 9, 5, 6, IR1)
    cv.rect(42, 10, 3, 4, LY2)
    cv.put(43, 12, LY1)
    for (x, y) in [(40, 11), (46, 12), (43, 16)]:
        cv.put(x, y, LY1)
    return cv


def aisle(side):
    """The nave's processional aisle, polished salt slabs laid down the middle (3 wide: w, c, e), a carved border on
    its outer sides; the slabs repeat every cell so the runner is any length."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            c = SA5 if (i + j * 3) % 11 else SA4
            if j == 15:
                c = SA3
            if j == 0:
                c = SA5
            cv.put(i, j, c)
    for j in range(16):
        if side == "w":
            cv.put(0, j, SA2)
            cv.put(1, j, SA3)
            cv.put(3, j, SA3 if j % 4 else CR1)
        elif side == "e":
            cv.put(15, j, SA2)
            cv.put(14, j, SA3)
            cv.put(12, j, SA3 if j % 4 else CR1)
    if side == "c":
        for (x, y) in [(7, 7), (8, 7), (7, 8), (8, 8)]:
            cv.put(x, y, CR1)
        cv.put(7, 7, CR2)
        for (x, y) in [(5, 7), (10, 8), (7, 5), (8, 10)]:
            cv.put(x, y, SA3)
    return cv


def chandelier():
    """3x2 a chandelier of salt crystals hanging over the aisle (the salt mines' chapels have them): a ring of crystal
    drops on chains with a lantern at its heart. Returns (bottom, top): the aisle beneath with the light it throws
    (walkable; columns = aisle w, c, e), and the chandelier itself drawn over the player (top layer)."""
    bot = Canvas(3, 2)
    for j in (0, 16):
        for k, sd in enumerate("wce"):
            bot.paste(aisle(sd), 16 * k, j)
    cx, cy = 24, 12
    # its shadow on the aisle below (it hangs high: a soft dithered ring)
    for j in range(32):
        for i in range(48):
            v = ((i + 0.5 - cx) / 12) ** 2 + ((j + 0.5 - 24) / 4.5) ** 2
            if 0.45 < v < 1.0 and (i + j) % 2 == 0:
                bot.put(i, j, SA3)
    top = Canvas(3, 2)
    for x in (cx - 10, cx + 10, cx):
        for y in range(0, 6 if x != cx else 4):
            top.put(x, y, SA0 if y % 2 else SA1)
    ring = set()
    for k in range(96):
        a = 2 * math.pi * k / 96
        for dr in (0, 1):
            ring.add((round(cx + (11 + dr) * math.cos(a)), round(cy + (4.5 + dr * 0.5) * math.sin(a))))
    for (x, y) in ring:
        top.put(x, y, SA1)
    for (x, y) in ring:
        if (x, y - 1) not in ring:
            top.put(x, y - 1, SA0)
        if (x, y + 1) not in ring:
            top.put(x, y + 1, SA0)
    for k in range(14):
        a = 2 * math.pi * k / 14 + 0.2
        x, y = round(cx + 11.5 * math.cos(a)), round(cy + 5 * math.sin(a))
        n = 4 if math.sin(a) > 0 else 3
        for d in range(2, n + 2):
            top.put(x, y + d, CR1 if d < n + 1 else CR2)
            top.put(x + 1, y + d, SA1 if d < n + 1 else None)
        top.put(x, y + n + 2, SA0)
    for (x, y, c) in [(cx - 1, cy - 3, CR1), (cx, cy - 3, CR1), (cx - 2, cy - 2, CR1), (cx - 1, cy - 2, SA5),
                      (cx, cy - 2, CR2), (cx + 1, cy - 2, CR1), (cx - 2, cy - 1, CR1), (cx - 1, cy - 1, CR2),
                      (cx, cy - 1, SA5), (cx + 1, cy - 1, CR1), (cx - 1, cy, CR1), (cx, cy, CR1), (cx - 1, cy + 1, SA1),
                      (cx - 2, cy, SA0), (cx + 1, cy, SA0), (cx - 3, cy - 1, SA0), (cx + 2, cy - 1, SA0),
                      (cx - 1, cy - 4, SA0), (cx, cy - 4, SA0)]:
        top.put(x, y, c)
    return bot, top


def aisle_px(i, j):
    """aisle('c') texture by absolute pixel (the chandelier's floor is the middle of the runner)."""
    c = SA5 if ((i % 16) + (j % 16) * 3) % 11 else SA4
    if j % 16 == 15:
        c = SA3
    return c


def lantern_fallen():
    """1x1 a mine lantern knocked over on the salt floor: the cage on its side, the glass cracked, a little pool of
    light spilled from it."""
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    for j in range(16):
        for i in range(16):
            if ((i - 9) / 6.5) ** 2 + ((j - 10) / 4.0) ** 2 < 1.0 and (i + j) % 2 == 0:
                cv.put(i, j, SA5)
    cv.rect(4, 7, 7, 5, IR1)                        # the cage lying east-west
    cv.rect(5, 8, 4, 3, LY2)
    cv.put(6, 9, LY1)
    cv.put(8, 8, SA4)                               # the crack
    cv.vline(11, 6, 12, IR1)                        # the base, tipped
    cv.vline(3, 8, 10, IR1)                         # the top cap
    cv.put(2, 9, IR1)
    cv.put(1, 8, IR1)                               # the bail handle
    cv.put(1, 7, IR1)
    cv.hline(4, 11, 12, SA1)
    for (x, y) in [(12, 9), (13, 11), (12, 12), (7, 13)]:
        cv.put(x, y, LY1)
    cv.put(13, 6, SA4)
    cv.put(14, 7, SA5)
    return cv


def void():
    return Canvas(1, 1, fill=INK)


def build():
    sh = Sheet(16)
    meta = {}

    def add(name, cv, walk=False, comment="", exit_cell=None, top=None):
        sh.add(name, cv)
        meta[name] = {"walk": walk, "comment": comment}
        if exit_cell:
            meta[name]["exit"] = exit_cell
        if top is not None:
            sh.add(name + "__top", top)
            meta[name]["top"] = name + "__top"

    add("void", void(), comment="outside the mine (black)")
    add("cap", cap(0), comment="back wall, row 0: the dark overhang of the face")
    add("cap_b", cap(1), comment="back wall, row 0: with a glint of crystal")
    add("face_hi", face_hi(), comment="back wall, row 1: the cut face, strata and cutter grooves")
    add("face_hi_vein", face_hi("vein"), comment="back wall, row 1: a crystal vein")
    add("face_hi_drill", face_hi("drill"), comment="back wall, row 1: drill holes")
    add("face_lo", face_lo("plain", 1), comment="back wall, row 2: spall at the foot")
    add("face_lo_crystal", face_lo("crystal", 2), comment="back wall, row 2: a crystal cluster")
    add("face_lo_vein", face_lo("vein", 3), comment="back wall, row 2: a crystal vein")
    add("side_l", side(False), comment="left side wall")
    add("side_r", side(True), comment="right side wall")
    add("rim_s", rim_s(), comment="the room's south edge (floor drops into darkness), blocking")
    add("timber_set", timber_set(), comment="3x2 a timber set braced against the face (rows 1-2 of the back wall), lantern")
    add("heart", heart(), comment="7x3 the hot glowing heart in the back wall (rows 0-2), blocking")
    add("dais", dais(), comment="3x2 Groudon's dais of standing salt (blocking); Groudon stands on its middle bottom cell")
    for k in ("plain", "crack", "crystals", "dust"):
        add("floor" if k == "plain" else "floor_" + k, floor(k, 0), walk=True,
            comment="salt floor" + ("" if k == "plain" else ": " + k))
    add("floor_b", floor("plain", 1), walk=True, comment="salt floor, second grain")
    for k in ("plain", "core", "seam", "seam_v", "glaze", "fade_s", "fade_w", "fade_e", "fade_sw", "fade_se"):
        add("warm" if k == "plain" else "warm_" + k, warm_floor(k, 0), walk=True,
            comment={"plain": "salt floor lit by the heart", "core": "the hottest floor (orange flecks)",
                     "seam": "warm floor, a glowing seam east-west",
                     "seam_v": "warm floor, a glowing seam north-south", "glaze": "warm floor, salt glazed by heat"}.get(
                k, "the glow's edge: warm fading out toward " + k[5:].upper()))
    for k in ("w", "c", "e"):
        add("aisle_" + k, aisle(k), walk=True, comment=f"the polished processional aisle, {k} column (3 wide)")
    add("pillar", pillar(), comment="2x3 a carved salt pillar, blocking")
    add("pillar_timber", pillar("timber"), comment="2x3 a salt pillar with a timber collar and a hung lantern, blocking")
    for k in ("v", "h", "end"):
        add("rail_" + k, rails(k), walk=True, comment={"v": "rails north-south", "h": "rails east-west",
            "end": "the end of the track: a timber stop block (track runs south)"}[k])
    for k in ("ne", "nw", "se", "sw"):
        add("rail_" + k, rail_curve(k), walk=True,
            comment=f"2x2 a quarter turn of track joining {dict(n='north', s='south')[k[0]]} and "
                    f"{dict(e='east', w='west')[k[1]]} (the cell inside the turn is plain floor)")
    add("cart", cart(), comment="1x2 a salt cart on north-south rails, blocking")
    cb, ct = chandelier()
    add("chandelier", cb, walk=True, top=ct, comment="3x2 a salt-crystal chandelier over the aisle: the aisle and its "
        "light are the bottom layer (walkable), the chandelier the top layer (drawn over the player); place it across "
        "the aisle's three columns")
    add("cribbing", cribbing(), comment="2x2 mine cribbing: a square crib of round logs in alternating courses, "
                                        "cut ends lighter, blocking")
    add("lantern_post", lantern_post(), comment="1x2 a timber post with a lantern, blocking")
    add("crystal", crystal(False), comment="1x1 a cluster of salt crystals, blocking")
    add("lantern_fallen", lantern_fallen(), comment="1x1 a mine lantern knocked over on the floor, blocking")
    add("crystal_big", crystal(True), comment="2x2 a big cluster of salt crystals, blocking")
    add("salt_blocks", salt_blocks(), comment="2x1 cut salt blocks, blocking")
    add("spall", spall(), comment="1x1 salt spall, blocking")
    add("adit", adit(), walk=[[1, 0], [1, 1]], exit_cell=[1, 1],
        comment="3x2 the timbered adit the shaft comes down to, set in the south rim: row 0 middle = the arrival cell, "
                "row 1 middle = the exit (walk south into the dark: exit coord event / arrow warp); the rest blocks")
    sh.pack()
    return sh, meta


def main():
    sh, meta = build()
    bad = check_families([(n, sh.image.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16)))
                          for n, p in sh.pieces.items()], FAMILIES, "cathedral")
    for b in bad:
        print("off-family tile:", b)
    write(sh, meta, "sc", "orleans_saltdome", "gTileset_OrleansSaltdome", "cathedral.png", FAMILIES,
          "The Salt Cathedral (Groudon's arena)")
    print(f"cathedral: {len([n for n in sh.pieces if not n.endswith('__top')])} pieces, sheet {sh.image.size}, {len(bad)} off-family tiles")


if __name__ == "__main__":
    main()

"""The Drowned Temple (Kyogre's raid arena, LandsEnd_DrownedTemple): own art for its own secondary tileset.

usage (from the decomp root): python tools/mapgen/tilesets/arenas/make_temple.py
writes tools/mapgen/tilesets/arenas/temple.png (16 px cells, magenta = clear) and temple.json (piece -> cells + notes),
and the compose recipe tools/mapgen/tilesets/arenas/recipes/orleans_temple.json (source name "dt").

A flooded Rootkin stone temple under the Gulf, drawn in the same pale spiral-carved stone as the Route 22 temple gate
(route_landmarks.png) but sunk into a blue-green underwater light:
    walls        back wall in three rows (cap, carved frieze of spirals and waves, a base crusted with algae, barnacles
                 and coral), side walls, the central medallion over the altar, the dividing wall with its sealed door
    door         the sealed door, closed (a slab with the glowing spiral seal, the one that opens to Heron's verse) and
                 open (the slab sunk, the passage lit; the lintel is drawn over the player)
    water        Kyogre's moat: deep water with slow swells, glints, the shadow under walls and platform faces
    platform     the altar island and causeway standing in the moat: flagstone top, lit lip, a south face into the water
    altar        Kyogre's dais (3x2, a glowing spiral ring) and two tide bowls of glowing water
    hall         flagstones and their variants (cracks, shells, sand drift, caustic light, kelp, bubbles), broken columns
                 (full, broken, stump, a fallen drum, a fallen capital), tide pools, kelp, coral, rubble, the sunken bell
    entry        the dive pool the player surfaces through (3x2; its bottom-middle cell is the exit)
Colour families (palettes): STONE, WATER, BELL; every 8x8 tile fits one (checked).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arena_art import Canvas, Sheet, check_families, hashn, texture, write  # noqa: E402

# ---------------------------------------------------------------- colours
INK = (24, 32, 48)
T1, T2, T3, T4, T5 = (56, 72, 80), (88, 104, 112), (120, 144, 144), (160, 184, 176), (200, 216, 208)   # sea stone
A1, A2 = (48, 96, 80), (88, 136, 104)                    # algae / kelp
C1, C2 = (192, 88, 88), (232, 144, 120)                  # coral
BC = (224, 216, 184)                                     # barnacles, shells, sand glints
G1, G2, G3 = (64, 168, 176), (136, 224, 216), (216, 248, 240)   # the glow (seal, altar, tide bowls)
LT = (176, 216, 200)                                     # caustic light on stone
W0, W1, W2 = (16, 40, 64), (32, 64, 96), (48, 96, 120)   # deep water
S1, S2 = (64, 128, 144), (104, 168, 168)                 # shallow water
RP, FM = (152, 208, 200), (216, 240, 232)                # ripple, foam
Z1, Z2, Z3 = (80, 64, 48), (136, 104, 64), (192, 160, 88)   # bronze
V1, V2 = (64, 144, 128), (120, 192, 160)                 # verdigris

FAMILIES = {
    "STONE": [INK, T1, T2, T3, T4, T5, A1, A2, C1, C2, BC, G1, G2, G3, LT],
    "WATER": [INK, W0, W1, W2, S1, S2, RP, FM, T1, T2, T3, T4, A1, A2, G2],
    "BELL": [INK, Z1, Z2, Z3, V1, V2, T1, T2, T3, T4, T5, A1, A2, C1, BC],
}


# ---------------------------------------------------------------- textures
def floor_px(x, y, seed=0):
    """Worn paving, one slab per 16 px cell (every floor-based piece lines up with every other): soft joints on the
    right and bottom, a lit top-left lip, a few small worn spots and chips (the seed picks which)."""
    sx, sy = x % 16, y % 16
    if sy == 15 or sx == 15:
        return T2
    if (sy == 0 and 1 < sx < 13) or (sx == 0 and 1 < sy < 11):
        return T4
    marks = {0: [(4, 5, T4), (5, 5, T4), (4, 6, T4), (11, 10, T2), (12, 10, T2), (9, 3, T2)],
             1: [(10, 4, T4), (11, 4, T4), (10, 5, T4), (4, 11, T2), (5, 11, T2), (12, 12, T4)],
             2: [(7, 8, T4), (8, 8, T4), (8, 9, T4), (3, 3, T2), (12, 5, T2), (13, 5, T2)],
             3: [(3, 9, T2), (4, 9, T2), (11, 6, T4), (12, 6, T4), (11, 7, T4), (7, 12, T2)]}[seed % 4]
    for (mx, my, c) in marks:
        if (sx, sy) == (mx, my):
            return c
    return T3


def wall_px(x, y):
    """Wall blocks 16 x 8 in running bond, lit top row, shaded bottom row."""
    by = y % 8
    bx = (x + (8 if (y // 8) % 2 else 0)) % 16
    n = hashn(x % 16, y % 16, 7)
    if by == 7 or bx == 15:
        return T1
    if by == 0:
        return T4
    if by == 6:
        return T2
    if n < 0.08:
        return T2
    return T3


def water_px(x, y, seed=0):
    """Deep water: W1 with long low swells of W2 and a few W0 troughs, period 16 x 16."""
    xx, yy = x % 16, y % 16
    # two swell lines per tile, gently curved
    for base, off in ((3, 0), (11, 8)):
        cy = base + (1 if ((xx + off) % 16) in range(4, 10) else 0)
        if yy == cy and ((xx + off) % 16) in range(2, 12):
            return W2
        if yy == cy + 1 and ((xx + off) % 16) in range(4, 10):
            return W0
    return W1


def put_tex(cv, fn, x=0, y=0, w=None, h=None, ox=0, oy=0):
    w = cv.w if w is None else w
    h = cv.h if h is None else h
    texture(cv, x, y, w, h, lambda i, j: fn(i + ox, j + oy))


# ---------------------------------------------------------------- small motifs
def spiral(cv, cx, cy, c, r=4):
    """A square Rootkin spiral (the carving on the temple gate), about 2r+1 px across."""
    pts = []
    x, y = cx, cy
    step = 1
    d = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    k = 0
    pts.append((x, y))
    while step <= 2 * r:
        for _ in range(2):
            dx, dy = d[k % 4]
            for _ in range(step):
                x += dx
                y += dy
                if abs(x - cx) <= r and abs(y - cy) <= r:
                    pts.append((x, y))
            k += 1
        step += 2
    for p in pts:
        cv.put(p[0], p[1], c)


def barnacles(cv, x0, y0, w, h, seed, rate=0.08):
    for j in range(y0, y0 + h):
        for i in range(x0, x0 + w):
            if hashn(i, j, seed) < rate and cv.get(i, j) not in (None,):
                cv.put(i, j, BC)
                if cv.get(i + 1, j) is not None:
                    cv.put(i + 1, j, T2)


def coral_nub(cv, x, y, big=False):
    """A small branching coral, base at (x, y)."""
    cv.put(x, y, C1)
    cv.put(x, y - 1, C1)
    cv.put(x - 1, y - 2, C2)
    cv.put(x + 1, y - 2, C2)
    cv.put(x, y - 2, C1)
    if big:
        cv.put(x - 2, y - 3, C2)
        cv.put(x + 2, y - 3, C2)
        cv.put(x - 1, y - 3, C1)
        cv.put(x + 1, y - 3, C1)
        cv.put(x, y - 4, C2)
    cv.put(x - 1, y + 1, INK)
    cv.put(x + 1, y + 1, INK)


def kelp(cv, x, y, h, seed, lean=1):
    """A kelp frond rising from (x, y) for h px, swaying."""
    for k in range(h):
        sx = x + int(round(1.5 * __import__("math").sin((k + seed) / 3.0))) * lean
        cv.put(sx, y - k, A1 if k % 3 else A2)
        if k % 4 == 1:
            cv.put(sx + 1, y - k, A2)
        if k % 4 == 3:
            cv.put(sx - 1, y - k, A2)


# ---------------------------------------------------------------- walls
def wall_cap(edge_n=False, variant=0):
    """The wall's top seen from above: a dark course of rubble with a lit lip on its south side (and north)."""
    cv = Canvas(1, 1)
    # rough capstones: irregular blocks of T2 on dark T1 joints, a few lit edges, algae in the joints
    stones = [(0, 2, 7, 5), (8, 1, 7, 6), (1, 8, 5, 4), (7, 8, 8, 4)]
    cv.rect(0, 0, 16, 16, T1)
    for (x, y, w, h) in stones:
        cv.rect(x, y, w, h, T2)
        cv.hline(x, x + w - 2, y, T3)
        cv.put(x + w - 1, y + h - 1, INK)
    for (x, y) in [(3, 4), (11, 3), (12, 9), (2, 10)]:
        cv.put(x, y, T1)
    for (x, y) in [(7, 5), (6, 6), (15, 7), (6, 12)]:
        cv.put(x, y, A1)
    for i in range(16):
        cv.put(i, 13, T3)
        cv.put(i, 14, T4 if i % 7 else T5)
        cv.put(i, 15, T2)
        if edge_n:
            cv.put(i, 0, T2)
            cv.put(i, 1, T4 if i % 5 else T3)
    if variant:
        cv.put(10, 4, C1)
        cv.put(11, 4, C2)
        cv.put(10, 5, INK)
        cv.put(3, 9, BC)
    return cv


def wall_frieze(kind):
    """The carved frieze row: moldings top and bottom, a spiral or a wave carved between."""
    cv = Canvas(1, 1)
    put_tex(cv, wall_px)
    cv.rect(0, 0, 16, 3, T3)
    cv.hline(0, 15, 0, T5)
    cv.hline(0, 15, 1, T4)
    cv.hline(0, 15, 3, T1)
    cv.rect(0, 4, 16, 9, T3)
    cv.hline(0, 15, 12, T2)
    cv.hline(0, 15, 13, T4)
    cv.hline(0, 15, 14, T3)
    cv.hline(0, 15, 15, T1)
    if kind == "spiral":
        cv.rect(3, 4, 10, 8, T2)
        cv.rect(4, 5, 8, 6, T3)
        spiral(cv, 8, 8, T1, 3)
        cv.vline(1, 4, 11, T2)
        cv.vline(14, 4, 11, T2)
    elif kind == "wave":
        for i in range(16):
            yy = 8 + [0, -1, -2, -2, -1, 0, 1, 1][i % 8]
            cv.put(i, yy, T1)
            cv.put(i, yy + 1, T4)
            cv.put(i, yy - 3, T2 if i % 8 < 4 else T3)
    elif kind == "crack":
        cv.rect(3, 4, 10, 8, T2)
        cv.rect(4, 5, 8, 6, T3)
        spiral(cv, 8, 8, T1, 3)
        for k, (i, j) in enumerate([(11, 0), (10, 1), (10, 2), (9, 3), (9, 4), (10, 5), (11, 6), (11, 7), (12, 8)]):
            cv.put(i, j, INK)
            cv.put(i + 1, j, T5 if k % 2 else T4)
    # algae streaks dripping from the molding
    for i in (2, 13):
        cv.vline(i, 3, 5 + (i % 3), A1)
    return cv


def wall_base(kind, seed):
    """The base course: big blocks, algae climbing from the waterline, barnacles, coral nubs."""
    cv = Canvas(1, 1)
    put_tex(cv, wall_px, oy=8)
    for i in range(16):
        h = 3 + int(3 * hashn(i, 0, seed))
        for j in range(16 - h, 16):
            cv.put(i, j, A1 if (i + j) % 3 else A2)
    barnacles(cv, 0, 6, 16, 8, seed, 0.05)
    if kind == "coral":
        coral_nub(cv, 4, 12, True)
        coral_nub(cv, 11, 13)
    elif kind == "kelp":
        kelp(cv, 3, 15, 12, seed)
        kelp(cv, 12, 15, 9, seed + 2, -1)
    cv.hline(0, 15, 15, INK)
    return cv


def side_wall(right=False):
    """A side wall seen from above: a dark strip with its lit inner edge (toward the room)."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            n = hashn(i, j, 11)
            c = T1 if ((i // 4 + j // 4) % 2 or n < 0.4) else T2
            cv.put(i, j, c)
    for j in range(16):
        cv.put(12, j, T2)
        cv.put(13, j, T4 if j % 6 else T3)
        cv.put(14, j, T3)
        cv.put(15, j, T1)
    if (hashn(0, 0, 5) > 0.5):
        cv.put(8, 7, C1)
    if right:
        cv.flip_x()
    return cv


def medallion():
    """3x3 centre of the back wall over the altar (rows cap, frieze, base): a great carved disc of waves around the
    spiral, rising over the cap, faintly lit by the seal's glow, coral at its foot."""
    import math
    cv = Canvas(3, 3)
    for k in range(3):
        cv.paste(wall_cap(), 16 * k, 0)
        cv.paste(wall_frieze("wave"), 16 * k, 16)
        cv.paste(wall_base("plain", 41 + k), 16 * k, 32)
    cx, cy = 24, 24
    cv.ellipse(cx, cy + 1, 21, 19, INK)
    cv.ellipse(cx, cy, 20, 18, T2)
    cv.ellipse(cx - 0.5, cy - 0.5, 19, 17, T4)
    cv.ellipse(cx, cy, 18, 16, T3)
    for a in range(12):
        ang = a * math.pi / 6 + math.pi / 12
        x, y = cx + 14.5 * math.cos(ang), cy + 13 * math.sin(ang)
        spiral(cv, round(x), round(y), T2, 1)
        cv.put(round(x) - 1, round(y) - 1, T5)
    cv.ellipse(cx, cy, 11, 10, T1)
    cv.ellipse(cx, cy, 10, 9, T2)
    cv.ellipse(cx - 0.5, cy - 0.5, 9, 8, T3)
    spiral(cv, cx, cy, G1, 6)
    for (x, y) in [(cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1)]:
        cv.put(x, y, G3)
    for (x, y) in [(cx - 4, cy - 3), (cx + 5, cy + 2), (cx - 2, cy + 5), (cx + 3, cy - 5)]:
        cv.put(x, y, G2)
    for i in (cx - 1, cx + 2):
        cv.vline(i, cy + 18, cy + 21, G1)
    cv.put(cx - 1, cy + 22, G2)
    coral_nub(cv, 6, 45, True)
    coral_nub(cv, 41, 45, True)
    coral_nub(cv, 30, 46)
    return cv


# ---------------------------------------------------------------- the dividing wall and the sealed door
def divider_cap(variant=0):
    return wall_cap(edge_n=True, variant=variant)


def divider_face(kind, seed):
    cv = wall_base(kind, seed)
    # the face's top: a lit course under the cap
    cv.hline(0, 15, 0, T4)
    return cv


def door(state):
    """3x2: row 0 = cap level (the jambs' tops and the lintel), row 1 = the face (jambs and the slab / the opening).
    Returns (bottom, top): `top` is only the open door's lintel over the passage (drawn over the player)."""
    cv = Canvas(3, 2)
    top = Canvas(3, 2)
    # jambs: carved pillars left and right
    for x0 in (0, 32):
        cv.rect(x0, 0, 16, 32, T3)
        put_tex(cv, wall_px, x0, 16, 16, 16)
        cv.rect(x0 + 2, 0, 12, 32, T3)
        cv.vline(x0 + 2, 0, 31, T4)
        cv.vline(x0 + 13, 0, 31, T2)
        cv.vline(x0 + 1, 0, 31, T1)
        cv.vline(x0 + 14, 0, 31, T1)
        spiral(cv, x0 + 8, 7, T1, 3)
        spiral(cv, x0 + 8, 21, T1, 3)
        cv.rect(x0, 28, 16, 4, A1)
        cv.hline(x0, x0 + 15, 31, INK)
        cv.vline(x0 + (13 if x0 == 0 else 2), 25, 30, A2)
    # the outer edges blend into the dividing wall's cap and face
    for x0, xs in ((0, range(0, 2)), (32, range(46, 48))):
        for i in xs:
            for j in range(16):
                cv.put(i, j, wall_cap(True).get(i % 16, j))
    if state == "closed":
        # lintel across the top (row 0 middle), the slab below it (row 1 middle)
        cv.rect(16, 0, 16, 16, T3)
        cv.hline(16, 31, 0, T2)
        cv.hline(16, 31, 1, T4)
        cv.rect(16, 3, 16, 9, T3)
        cv.hline(16, 31, 12, T2)
        cv.hline(16, 31, 13, T4)
        cv.hline(16, 31, 14, T2)
        cv.hline(16, 31, 15, T1)
        for i in range(17, 31, 4):
            cv.put(i, 6, T1)
            cv.put(i + 1, 7, T1)
            cv.put(i + 2, 6, T1)
        # the slab
        cv.rect(16, 16, 16, 16, T2)
        cv.rect(17, 16, 14, 15, T3)
        cv.hline(17, 30, 16, T4)
        cv.vline(17, 16, 30, T4)
        cv.vline(30, 16, 30, T2)
        cv.ellipse(24, 23.5, 6, 6, T2)
        spiral(cv, 24, 23, G1, 4)
        for (x, y) in [(24, 23), (25, 23), (24, 24)]:
            cv.put(x, y, G3)
        for (x, y) in [(20, 20), (28, 27), (21, 27), (27, 19)]:
            cv.put(x, y, G2)
        cv.hline(16, 31, 31, INK)
        cv.rect(16, 29, 16, 2, A1)
        cv.put(19, 28, A2)
        cv.put(28, 28, A2)
    else:
        # passage floor (row 0 middle) under the lintel (top layer), the opening (row 1 middle) with the slab sunk
        put_tex(cv, floor_px, 16, 0, 16, 32)
        for j in range(32):
            for i in range(16, 32):
                c = cv.get(i, j)
                shade = {T3: T2, T4: T3, T2: T1}.get(c, c)
                cv.put(i, j, shade if j < 20 else c)
        cv.vline(16, 0, 31, INK)
        cv.vline(31, 0, 31, INK)
        cv.rect(17, 28, 14, 3, T2)          # the sunk slab's top edge in the floor
        cv.hline(17, 30, 28, T4)
        spiral(cv, 24, 29, G1, 1)
        for (x, y) in [(20, 22), (27, 18), (23, 12), (25, 6)]:
            cv.put(x, y, G2)               # glints of the sanctum's light down the passage
        # lintel: drawn over the player, upper 6 px of the passage cell
        top.rect(16, 0, 16, 6, T3)
        top.hline(16, 31, 0, T2)
        top.hline(16, 31, 1, T4)
        top.hline(16, 31, 4, T2)
        top.hline(16, 31, 5, T1)
        for i in range(17, 31, 4):
            top.put(i, 3, T1)
            top.put(i + 2, 3, T1)
    return cv, top


# ---------------------------------------------------------------- water and the platform
def water(kind="plain", seed=0):
    cv = Canvas(1, 1)
    put_tex(cv, water_px)
    if kind == "glint":
        for (x, y) in [(5, 6), (6, 6), (12, 13)]:
            cv.put(x, y, G2)
        cv.put(13, 13, RP)
    elif kind == "shadow":         # under a wall's base or a platform's face
        for i in range(16):
            for j in range(0, 4 + (1 if i % 5 == 2 else 0)):
                cv.put(i, j, W0)
            cv.put(i, 4 + (1 if i % 5 == 2 else 0), W1)
        cv.put(4, 7, W2)
        cv.put(11, 9, W2)
    elif kind == "kelp":
        kelp(cv, 6, 15, 11, seed)
        kelp(cv, 11, 15, 7, seed + 3, -1)
    return cv


def platform(n, s, w, e, inner=()):
    """A cell of the altar island / causeway: flagstone top; edges toward water get a lit lip (n, w, e) or a stone
    face with the waterline (s). `inner` lists concave corners (nw, ne, sw, se) where only the diagonal is water."""
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    if n:
        cv.hline(0, 15, 0, T1)
        cv.hline(0, 15, 1, T5)
        cv.hline(0, 15, 2, T4)
    if w:
        cv.vline(0, 0, 15, T1)
        cv.vline(1, 0, 15, T4)
    if e:
        cv.vline(15, 0, 15, T1)
        cv.vline(14, 0, 15, T2)
    if s:
        # the face: two courses of blocks into the water, algae at the waterline
        for i in range(16):
            cv.put(i, 10, T4)
            cv.put(i, 11, T2 if i % 8 != 7 else T1)
            cv.put(i, 12, T2 if (i + 4) % 8 != 7 else T1)
            cv.put(i, 13, A1 if (i * 7) % 5 else A2)
            cv.put(i, 14, S1 if i % 4 else RP)
            cv.put(i, 15, W1 if i % 6 else RP)
        if w:
            for j in range(10, 16):
                cv.put(0, j, T1 if j < 14 else W1)
        if e:
            for j in range(10, 16):
                cv.put(15, j, T1 if j < 14 else W1)
    if n and w:
        cv.put(1, 1, T5)
        cv.put(0, 0, INK)
    if n and e:
        cv.put(15, 0, INK)
    for c in inner:
        x = 0 if "w" in c else 15
        y = 0 if "n" in c else 15
        if "n" in c:
            cv.put(x, 0, T1)
            cv.put(x, 1, T5 if x == 0 else T1)
            cv.put(1 if x == 0 else 14, 0, T1)
        else:
            cv.put(x, 15, S1)
            cv.put(x, 14, T1)
            cv.put(1 if x == 0 else 14, 15, T1)
    return cv


# ---------------------------------------------------------------- the altar
def dais():
    """Kyogre's dais, 3x2: a round stepped platform, a ring of glowing spiral inlay, coral at its foot."""
    cv = Canvas(3, 2)
    put_tex(cv, floor_px)
    cx, cy = 24, 15
    cv.ellipse(cx, cy + 3, 22, 13, T1)       # the step's shadow
    cv.ellipse(cx, cy + 2, 21, 12, T2)       # lower step face
    cv.ellipse(cx, cy, 21, 12, T4)
    cv.ellipse(cx, cy, 20, 11, T3)
    cv.ellipse(cx, cy - 1, 16, 8.5, T1)
    cv.ellipse(cx, cy - 1, 15.5, 8, T4)
    cv.ellipse(cx, cy - 2, 15, 7.5, T3)
    # the glowing ring
    import math
    for a in range(48):
        ang = a * math.pi / 24
        x = cx + 12 * math.cos(ang)
        y = cy - 2 + 5.5 * math.sin(ang)
        cv.put(round(x), round(y), G1 if a % 4 else G2)
    for a in range(8):
        ang = a * math.pi / 4 + 0.3
        x = cx + 12 * math.cos(ang)
        y = cy - 2 + 5.5 * math.sin(ang)
        cv.put(round(x), round(y), G3)
    spiral(cv, cx, cy - 2, G1, 3)
    cv.put(cx, cy - 2, G3)
    # carved steps on the front (south) face
    for i in range(cx - 6, cx + 7):
        cv.put(i, cy + 11, T4)
        cv.put(i, cy + 12, T2)
    coral_nub(cv, 6, 27, True)
    coral_nub(cv, 42, 26)
    cv.put(9, 24, BC)
    cv.put(38, 25, BC)
    return cv


def tide_bowl():
    """A stone bowl on a short pillar, brimming with glowing water, 1x2."""
    cv = Canvas(1, 2)
    put_tex(cv, floor_px)
    # pillar
    cv.rect(5, 12, 6, 16, T3)
    cv.vline(5, 12, 27, T4)
    cv.vline(10, 12, 27, T2)
    cv.vline(4, 12, 28, T1)
    cv.vline(11, 12, 28, T1)
    spiral(cv, 8, 19, T2, 2)
    cv.rect(3, 27, 10, 3, T2)
    cv.hline(3, 12, 27, T4)
    cv.hline(2, 13, 30, T1)
    cv.vline(2, 27, 29, T1)
    cv.vline(13, 27, 29, T1)
    # bowl
    cv.ellipse(8, 9, 7, 4, T1)
    cv.ellipse(8, 8.5, 6, 3.2, T4)
    cv.ellipse(8, 8, 5, 2.2, G1)
    cv.ellipse(8, 7.6, 3, 1.2, G2)
    cv.put(7, 7, G3)
    cv.rect(3, 9, 10, 3, T3)
    cv.hline(3, 12, 11, T2)
    cv.hline(3, 12, 12, T1)
    for (x, y) in [(6, 3), (9, 1), (8, 4)]:
        cv.put(x, y, G2)                # motes of light rising
    return cv


# ---------------------------------------------------------------- the hall
def floor(kind="plain", seed=0):
    cv = Canvas(1, 1)
    put_tex(cv, lambda i, j: floor_px(i, j, seed))
    if kind == "crack":
        pts = [(2, 3), (3, 4), (4, 4), (5, 5), (6, 6), (6, 7), (7, 8), (8, 8), (9, 9), (10, 10), (10, 11), (12, 12)]
        for x, y in pts:
            cv.put(x, y, T1)
            cv.put(x, y + 1, T4)
    elif kind == "shells":
        for x, y in [(4, 5), (11, 10)]:
            cv.put(x, y, BC)
            cv.put(x + 1, y, BC)
            cv.put(x, y + 1, T2)
        for x, y in [(9, 3), (8, 4), (9, 4), (10, 4), (9, 5), (8, 6), (10, 6), (7, 4), (11, 4)]:
            cv.put(x, y, C2)
        cv.put(9, 4, C1)
    elif kind == "sand":
        for j in range(16):
            for i in range(16):
                v = ((i - 8) / 9.0) ** 2 + ((j - 8) / 6.5) ** 2
                if v < 1.0 - 0.25 * hashn(i // 2, j // 2, 5):
                    cv.put(i, j, T4 if (i + 3 * j) % 9 else T3)
        cv.put(5, 9, BC)
        cv.put(12, 6, BC)
    elif kind == "kelp":
        kelp(cv, 5, 13, 9, seed)
        kelp(cv, 10, 14, 7, seed + 2, -1)
        cv.put(5, 14, T1)
        cv.put(10, 15, T1)
    elif kind == "bubbles":
        for x, y in [(6, 12), (8, 9), (7, 6), (9, 3), (10, 11), (4, 2)]:
            cv.put(x, y, BC)
            cv.put(x + 1, y, G2)
            cv.put(x, y - 1, LT)
    return cv


def light_pool():
    """2x2: a pool of rippling light on the paving where the sun reaches down through a crack in the vault (the
    caustic net of light the sea throws), bright in the middle and breaking up toward its edge."""
    import math
    cv = Canvas(2, 2)
    put_tex(cv, floor_px)
    for j in range(32):
        for i in range(32):
            v = ((i + 0.5 - 16) / 15) ** 2 + ((j + 0.5 - 16) / 13) ** 2
            if v > 1.0:
                continue
            u = abs(math.sin(i * 0.42 + 1.3 * math.sin(j * 0.31)))
            w = abs(math.sin(j * 0.47 + 1.2 * math.sin(i * 0.27)))
            net = min(u, w)                         # a wavy net: bright where either wave crosses zero
            c = cv.get(i, j)
            lit = {T3: LT, T4: T5, T2: T3}.get(c, c)
            if v < 0.6:
                if net < 0.16:
                    cv.put(i, j, T5)
                elif net < 0.34:
                    cv.put(i, j, lit)
                elif c == T2:
                    cv.put(i, j, T3)
            elif net < 0.22 and (i + j) % 2 == 0:
                cv.put(i, j, lit)
    return cv

def column(kind):
    """Broken columns of the hall. full 1x3 (capital, fluted shaft, base), broken 1x2 (ragged top), stump 1x1."""
    h = {"full": 3, "broken": 2, "stump": 1}[kind]
    cv = Canvas(1, h)
    put_tex(cv, floor_px)
    H = 16 * h
    top = {"full": 2, "broken": 6, "stump": 3}[kind]
    # shaft
    for j in range(top, H - 3):
        for i in range(3, 13):
            c = T3
            if i in (5, 8, 11):
                c = T2
            if i == 3:
                c = T4
            if i == 12:
                c = T2
            cv.put(i, j, c)
        cv.put(2, j, T1)
        cv.put(13, j, T1)
    # base
    cv.rect(1, H - 5, 14, 4, T3)
    cv.hline(1, 14, H - 5, T4)
    cv.hline(1, 14, H - 2, T2)
    cv.hline(0, 15, H - 1, T1)
    cv.vline(0, H - 5, H - 2, T1)
    cv.vline(15, H - 5, H - 2, T1)
    cv.rect(1, H - 3, 14, 1, A1)
    cv.put(3, H - 4, A2)
    cv.put(12, H - 4, A2)
    if kind == "full":
        cv.rect(0, 0, 16, 7, T3)
        cv.hline(0, 15, 0, T1)
        cv.hline(1, 14, 1, T5)
        cv.hline(1, 14, 2, T4)
        cv.hline(0, 15, 6, T2)
        cv.hline(1, 14, 7, T1)
        cv.vline(0, 0, 6, T1)
        cv.vline(15, 0, 6, T1)
        spiral(cv, 4, 4, T2, 1)
        spiral(cv, 11, 4, T2, 1)
        coral_nub(cv, 12, 30, True)
        barnacles(cv, 3, 10, 10, 20, 31, 0.04)
        kelp(cv, 4, H - 4, 10, 2)
    else:
        # ragged break: a jagged lit top with the broken core
        prof = [0, 2, 1, 3, 0, 1, 2, 4, 3, 1, 0, 2]
        for k, i in enumerate(range(2, 14)):
            t = top - 2 + prof[k]
            for j in range(0, t):
                cv.put(i, j, floor_px(i, j))
            cv.put(i, t, T1)
            cv.put(i, t + 1, T5 if prof[k] < 2 else T4)
            cv.put(i, t + 2, T4 if i < 9 else T3)
        if kind == "broken":
            coral_nub(cv, 5, 22)
            barnacles(cv, 3, 10, 10, 14, 17, 0.05)
    return cv


def fallen_column():
    """A column drum lying on the floor, 3x1, its broken capital beside it (fallen_capital, 1x1)."""
    cv = Canvas(3, 1)
    put_tex(cv, floor_px)
    cv.rect(2, 4, 42, 10, T3)
    for i in range(2, 44):
        cv.put(i, 3, T1)
        cv.put(i, 4, T5 if i % 9 else T4)
        cv.put(i, 6, T2 if i % 3 == 0 else T3)
        cv.put(i, 9, T2)
        cv.put(i, 12, T2)
        cv.put(i, 13, A1)
        cv.put(i, 14, T1)
    # broken end (left) and the round end (right, the drum face)
    for j in range(3, 15):
        cv.put(1, j, T1)
    cv.ellipse(44, 8.5, 3.5, 6, T1)
    cv.ellipse(44, 8.5, 2.5, 5, T4)
    cv.put(44, 8, T2)
    for x in (12, 13, 26, 27):
        cv.vline(x, 4, 13, T2)
    barnacles(cv, 2, 5, 40, 6, 23, 0.05)
    coral_nub(cv, 20, 13)
    return cv


def fallen_capital():
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    cv.rect(1, 5, 14, 8, T3)
    cv.hline(1, 14, 5, T5)
    cv.hline(1, 14, 6, T4)
    cv.hline(1, 14, 12, T2)
    cv.hline(0, 15, 13, T1)
    cv.vline(0, 5, 13, T1)
    cv.vline(15, 5, 13, T1)
    cv.hline(1, 14, 4, T1)
    spiral(cv, 5, 9, T2, 1)
    spiral(cv, 11, 9, T2, 1)
    coral_nub(cv, 8, 12)
    return cv


def tide_pool(w):
    """A tide pool sunk in the floor, w x 2: a ragged rim of rocks with algae, shallow water over a stony bottom,
    deeper under the north rim, an anemone and a starfish."""
    import math
    cv = Canvas(w, 2)
    put_tex(cv, floor_px)
    W, H = 16 * w, 32
    cx, cy = W / 2, 16.5
    rx, ry = W / 2 - 2.5, 11.5

    def d(i, j):
        a = math.atan2(j + 0.5 - cy, i + 0.5 - cx)
        wob = 0.10 * math.sin(3 * a + w) + 0.06 * math.sin(7 * a)
        return ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2 - wob

    for j in range(H):
        for i in range(W):
            v = d(i, j)
            if v <= 0.62:
                cv.put(i, j, S1 if hashn(i, j, 4) < 0.07 else S2)
            elif v <= 1.0:
                cv.put(i, j, W2 if j < cy else S1)
            elif v <= 1.22:
                cv.put(i, j, T1)
            elif v <= 1.55:
                n = hashn(i // 2, j // 2, 5)
                cv.put(i, j, T4 if n < 0.35 else (T2 if n < 0.7 else (A1 if n < 0.85 else T3)))
    for k in range(3, W - 5, 6):
        y = int(cy + 2 + 3 * math.sin(k))
        cv.put(k, y, RP)
        cv.put(k + 1, y, RP)
    cv.put(int(cx) + 4, 10, FM)
    cv.put(int(cx) + 5, 10, RP)
    for x, y in [(int(cx) - 6, 20), (int(cx) - 7, 21), (int(cx) - 6, 21), (int(cx) - 5, 21), (int(cx) - 6, 22)]:
        cv.put(x, y, RP)
    for x, y in [(4, 26), (5, 25), (6, 26), (5, 27), (3, 25), (7, 25)]:
        cv.put(x, y, A2)
    return cv

def coral_cluster():
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    cv.ellipse(8, 12, 6, 3, T2)
    coral_nub(cv, 5, 11, True)
    coral_nub(cv, 10, 12, True)
    coral_nub(cv, 8, 9)
    cv.put(3, 13, BC)
    cv.put(12, 14, BC)
    return cv


def kelp_tall():
    """Tall kelp growing out of a crack between fallen stones, 1x2 (blocking)."""
    cv = Canvas(1, 2)
    put_tex(cv, floor_px)
    for (x, y, r) in [(4, 28, 3.5), (11, 28.5, 4), (8, 30, 2.5)]:
        cv.ellipse(x, y + 1, r, r * 0.7, T1)
        cv.ellipse(x, y, r, r * 0.65, T2)
        cv.put(int(x - 1), int(y - 2), T4)
    kelp(cv, 5, 26, 22, 1)
    kelp(cv, 9, 27, 26, 4, -1)
    kelp(cv, 12, 26, 15, 7)
    return cv

def rubble():
    cv = Canvas(1, 1)
    put_tex(cv, floor_px)
    for (x, y, r) in [(5, 10, 3.5), (11, 11, 3), (8, 6, 2.5)]:
        cv.ellipse(x, y + 1, r, r * 0.8, T1)
        cv.ellipse(x, y, r, r * 0.75, T3)
        cv.put(int(x - 1), int(y - 1), T5)
    cv.put(4, 13, A1)
    cv.put(12, 13, A2)
    return cv


def bell():
    """The sunken bell, 2x2: a great bronze temple bell standing in the silt, its crown loop on top, two raised bands,
    a thick lip, verdigris running down from the bands, barnacles, a coral on its shoulder, silt drifted against it."""
    cv = Canvas(2, 2)
    put_tex(cv, floor_px)
    cx = 16
    top, lip = 7, 26
    prof = {}
    for y in range(top, lip + 2):
        t = (y - top) / (lip - top)
        hw = 5.5 + 1.0 * t + 6.5 * t ** 3.2
        if y == top:
            hw = 3.5
        elif y == top + 1:
            hw = 5.0
        prof[y] = hw
    body = {}
    for y, hw in prof.items():
        for x in range(0, 32):
            d = (x + 0.5 - cx) / hw
            if abs(d) <= 1.0:
                body[(x, y)] = d
    for (x, y), d in body.items():
        c = Z3 if -0.75 < d < -0.3 else (Z2 if d < 0.45 else Z1)
        if d <= -0.75:
            c = Z2
        cv.put(x, y, c)
    for yb in (top + 5, top + 13):
        for (x, y), d in body.items():
            if y == yb:
                cv.put(x, y, Z3 if d < 0.2 else Z2)
            if y == yb + 1:
                cv.put(x, y, Z1)
    for (x, y), d in body.items():
        if y >= lip:
            cv.put(x, y, Z3 if d < -0.2 else (Z2 if d < 0.5 else Z1))
        if y == lip - 1:
            cv.put(x, y, Z1)
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in body:
                cv.put(x + dx, y + dy, INK)
    for (x, y) in [(-2, -1), (-2, -2), (-1, -3), (0, -3), (1, -3), (2, -2), (2, -1)]:
        cv.put(cx + x - 1, top + y, Z2 if x < 1 else Z1)
    for (x, y) in [(-3, -1), (-3, -2), (-2, -3), (3, -1), (3, -2), (2, -3), (-1, -4), (0, -4), (1, -4)]:
        cv.put(cx + x - 1, top + y, INK)
    cv.put(cx - 1, top - 1, INK)
    cv.put(cx - 1, top - 2, INK)
    for (x, y0, n) in [(13, top + 7, 6), (19, top + 7, 9), (16, top + 15, 5), (11, top + 15, 4), (22, top + 15, 6)]:
        for k in range(n):
            if (x, y0 + k) in body:
                cv.put(x, y0 + k, V1 if k % 3 else V2)
    for (x, y) in [(12, 18), (20, 12), (23, 21), (9, 23)]:
        if (x, y) in body:
            cv.put(x, y, BC)
    for (x, y) in [(19, 9), (20, 8), (18, 8), (19, 7), (19, 10)]:
        cv.put(x, y, C1)
    # silt drifted against the foot (higher on the right)
    for x in range(0, 32):
        h = 2 + max(0, (x - 14)) * 0.35 + 1.5 * hashn(x, 0, 3)
        for y in range(int(31 - h), 31):
            if y > lip - 3:
                cv.put(x, y, T4 if hashn(x, y, 6) < 0.85 else T5)
        cv.put(x, int(31 - h) - 1, T3) if hashn(x, 2, 3) < 0.5 and int(31 - h) - 1 > lip - 3 else None
    return cv

def dive_pool():
    """The dive pool the player surfaces through, 3x2: a square well of deep water in a stone rim; steps lead down
    into it on the north side (row 0 middle = the top step, where the player arrives); row 1 middle is the exit."""
    cv = Canvas(3, 2)
    put_tex(cv, floor_px)
    # rim
    cv.rect(2, 4, 44, 28, T1)
    cv.rect(3, 5, 42, 26, T4)
    cv.rect(4, 6, 40, 24, T3)
    # the well
    for j in range(9, 32):
        for i in range(7, 41):
            cv.put(i, j, water_px(i, j))
    cv.hline(7, 40, 9, W0)
    cv.hline(7, 40, 10, W0)
    cv.vline(7, 9, 31, W0)
    cv.vline(40, 9, 31, W0)
    # steps down at the north middle
    for k, y in enumerate((8, 11, 14)):
        cv.rect(18, y, 12, 3, [T4, T3, T2][k])
        cv.hline(18, 29, y + 2, T1)
    cv.vline(17, 8, 17, T1)
    cv.vline(30, 8, 17, T1)
    cv.rect(18, 17, 12, 2, S1)
    cv.hline(18, 29, 19, RP)
    # glints, bubbles and the light from below
    for (x, y) in [(12, 22), (13, 22), (34, 26), (24, 25), (25, 24), (10, 28), (36, 14)]:
        cv.put(x, y, G2)
    for (x, y) in [(23, 27), (26, 29), (20, 30)]:
        cv.put(x, y, RP)
    # rim carvings
    for x in (10, 38):
        spiral(cv, x, 6, T2, 1)
    cv.put(5, 30, A1)
    cv.put(42, 30, A1)
    return cv


def void():
    cv = Canvas(1, 1, fill=INK)
    return cv


# ---------------------------------------------------------------- the sheet, json and recipe
def build():
    sh = Sheet(16)
    meta = {}

    def add(name, cv, walk=False, comment="", behavior=None, top=None, exit_cell=None, layer=None):
        sh.add(name, cv)
        meta[name] = {"walk": walk, "comment": comment}
        if behavior:
            meta[name]["behavior"] = behavior
        if exit_cell:
            meta[name]["exit"] = exit_cell
        if top is not None:
            sh.add(name + "__top", top)
            meta[name]["top"] = name + "__top"
        if layer:
            meta[name]["layer"] = layer

    add("void", void(), comment="outside the temple (black)")
    add("cap", wall_cap(), comment="back wall, row 0: the wall's top seen from above")
    add("cap_b", wall_cap(variant=1), comment="back wall, row 0: with a coral and a barnacle")
    add("frieze_spiral", wall_frieze("spiral"), comment="back wall, row 1: carved spiral")
    add("frieze_wave", wall_frieze("wave"), comment="back wall, row 1: carved wave")
    add("frieze_crack", wall_frieze("crack"), comment="back wall, row 1: cracked spiral")
    add("base_plain", wall_base("plain", 1), comment="back wall, row 2: algae and barnacles")
    add("base_coral", wall_base("coral", 2), comment="back wall, row 2: coral crust")
    add("base_kelp", wall_base("kelp", 3), comment="back wall, row 2: kelp against the wall")
    add("side_l", side_wall(False), comment="left side wall (its lit edge faces the room)")
    add("side_r", side_wall(True), comment="right side wall")
    add("medallion", medallion(), comment="3x3 centre of the back wall over the altar (rows cap, frieze, base)")
    add("div_cap", divider_cap(), comment="dividing wall, row 0: its top (lit lips both sides; water north of it)")
    add("div_cap_b", divider_cap(1), comment="dividing wall, row 0: with a coral and a barnacle")
    add("div_face", divider_face("plain", 5), comment="dividing wall, row 1: its south face")
    add("div_face_coral", divider_face("coral", 6), comment="dividing wall, row 1: coral")
    add("div_face_kelp", divider_face("kelp", 7), comment="dividing wall, row 1: kelp")
    dc, _ = door("closed")
    add("door_closed", dc, comment="3x2 sealed door in the dividing wall (rows cap, face): the spiral seal glows; all "
                                   "cells block. Sing Heron's verse at the middle cell of row 1.")
    do, dtop = door("open")
    add("door_open", do, top=dtop, walk=[[1, 0], [1, 1]],
        comment="3x2 the door opened (map state): the slab sunk, the passage (middle column) walkable; the lintel over "
                "the passage is the top layer (drawn over the player)")
    for k in ("plain", "glint", "shadow", "kelp"):
        add("water" if k == "plain" else "water_" + k, water(k, 3),
            comment={"plain": "deep water (blocking: the moat)", "glint": "deep water with a glint of the altar's light",
                     "shadow": "deep water under a wall base or a platform's south face",
                     "kelp": "deep water with kelp"}[k])
    plats = {"C": (0, 0, 0, 0, ()), "N": (1, 0, 0, 0, ()), "S": (0, 1, 0, 0, ()), "W": (0, 0, 1, 0, ()),
             "E": (0, 0, 0, 1, ()), "NW": (1, 0, 1, 0, ()), "NE": (1, 0, 0, 1, ()), "SW": (0, 1, 1, 0, ()),
             "SE": (0, 1, 0, 1, ()), "iNW": (0, 0, 0, 0, ("nw",)), "iNE": (0, 0, 0, 0, ("ne",)),
             "iSW": (0, 0, 0, 0, ("sw",)), "iSE": (0, 0, 0, 0, ("se",))}
    for k, (n, s, w, e, inner) in plats.items():
        add("plat_" + k, platform(n, s, w, e, inner), walk=True,
            comment=f"altar island / causeway cell, edge {k} (flagstone top; N/W/E lit lip, S stone face into the water"
                    + ("" if not inner else "; concave corner") + ")")
    add("dais", dais(), comment="3x2 Kyogre's dais (blocking); Kyogre's object stands on its middle bottom cell")
    add("tide_bowl", tide_bowl(), comment="1x2 a tide bowl of glowing water on a pillar (blocking)")
    for k in ("plain", "crack", "shells", "sand", "kelp", "bubbles"):
        add("floor" if k == "plain" else "floor_" + k, floor(k, 0), walk=True,
            comment="hall flagstones" + ("" if k == "plain" else f": {k}"))
    add("floor_b", floor("plain", 1), walk=True, comment="hall flagstones, second wear pattern")
    add("floor_c", floor("plain", 2), walk=True, comment="hall flagstones, third wear pattern")
    add("floor_d", floor("plain", 3), walk=True, comment="hall flagstones, fourth wear pattern")
    add("light_pool", light_pool(), walk=True, comment="2x2 a pool of caustic light on the paving (walkable)")
    add("column", column("full"), comment="1x3 a standing column (capital, fluted shaft, coral base), blocking")
    add("column_broken", column("broken"), comment="1x2 a broken column, ragged top, blocking")
    add("column_stump", column("stump"), comment="1x1 a column stump, blocking")
    add("column_fallen", fallen_column(), comment="3x1 a column drum lying on the floor, blocking")
    add("capital_fallen", fallen_capital(), comment="1x1 a fallen capital, blocking")
    add("tide_pool", tide_pool(2), comment="2x2 a tide pool sunk in the floor (blocking)")
    add("tide_pool_w", tide_pool(3), comment="3x2 a wider tide pool (blocking)")
    add("coral", coral_cluster(), comment="1x1 a coral cluster on the floor, blocking")
    add("kelp_tall", kelp_tall(), comment="1x2 tall kelp from a rock, blocking")
    add("rubble", rubble(), comment="1x1 fallen stones, blocking")
    add("bell", bell(), comment="2x2 the sunken bell, half buried in the silt, blocking")
    add("dive_pool", dive_pool(), walk=[[1, 0], [1, 1]], exit_cell=[1, 1],
        comment="3x2 the dive pool: row 0 middle = the top step (arrival cell), row 1 middle = the exit (walk south "
                "into the water: the exit coord event / arrow warp); the rest blocks")
    sh.pack()
    return sh, meta


def main():
    sh, meta = build()
    bad = check_families([(n, sh.image.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16)))
                          for n, p in sh.pieces.items()], FAMILIES, "temple")
    for b in bad:
        print("off-family tile:", b)
    write(sh, meta, "dt", "orleans_temple", "gTileset_OrleansTemple", "temple.png", FAMILIES,
          "The Drowned Temple (Kyogre's arena)")
    print(f"temple: {len([n for n in sh.pieces if not n.endswith('__top')])} pieces, sheet {sh.image.size}, "
          f"{len(bad)} off-family tiles")


if __name__ == "__main__":
    main()

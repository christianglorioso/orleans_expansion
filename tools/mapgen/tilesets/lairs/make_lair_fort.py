"""Own art for the Galarian birds' lair (legendary lairs batch 2): Spanish Fort, off Route 14 just south of Crescent City. One secondary,
gTileset_OrleansLairFort on gTileset_OrleansGeneral (prefix lf).

The lore: an old brick fort in the marsh outside the city, abandoned, then (as the real Spanish Fort on Lake Pontchartrain was) turned
into a jazz-age pleasure garden: a bandstand on the parade ground, a dance floor, strings of electric lights, a carousel. That closed
too, and the woods took it. The three Galarian birds keep it now, like a band that never left: Articuno on the bandstand, Zapdos
strutting on the dance floor, Moltres in the dark of a casemate.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_lair_fort.py
writes tools/mapgen/tilesets/lairs/lair_fort.png + lair_fort.json and recipes_b2/orleans_lair_fort.json (source "lf").

Drawn in the brick, mortar, sill and ivy colours of Crescent City's Drowned Ward ruins (sources/orleans_custom/crescent_brick.png).
    rampart / rampart_ivy 1x2   the fort's north rampart: its grassed top with a brick coping, the brick face under it
    casemate 2x2                an arched casemate in the rampart face, dark inside; casemate_glow (Moltres': violet embers in the dark)
    pier 1x2                    a ruined brick pier standing alone; rubble 1x1 (fallen brick in the grass, blocking)
    floor_<key>                 the old dance floor: cracked terrazzo, red and blue chips, grass in the cracks (walkable)
    bandstand 4x3               the bandstand: an octagon of white posts and fretwork under a verdigris dome, steps at its front
    lamp 1x2                    a cast-iron lamp post, its globe broken; festoon 1x1 (a string of dead bulbs sagging, walkable)
    carousel_horse 2x1          a carousel horse fallen in the grass, its paint faded, its brass pole snapped
    cannon 2x1, shot 1x1        an old iron cannon on its carriage, a pyramid of shot
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import GRASS, Canvas, Pieces, bricks, dual_set, ellipse_body, hashn, ink_outline, write_b2  # noqa: E402

G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
BR1, BR2, BR3, MOR = (200, 128, 88), (144, 88, 80), (128, 80, 72), (88, 72, 80)
DK1, DK0, SILL = (48, 56, 80), (32, 32, 48), (152, 152, 120)
IVY1, IVY2, INK = (80, 112, 96), (64, 96, 64), (40, 40, 48)
V1, V2, V3 = (104, 56, 152), (168, 96, 216), (232, 184, 248)
T1, T2, T3, TR, TB = (216, 208, 184), (184, 176, 152), (144, 136, 120), (176, 96, 80), (88, 120, 152)
W1, W2, W3 = (240, 240, 224), (200, 200, 184), (152, 152, 136)
CU1, CU2, CU3 = (120, 176, 152), (80, 136, 120), (48, 88, 80)
WDB, WDD = (136, 104, 72), (88, 64, 48)
FE1, FE2, Y1, Y2, GLS = (112, 120, 128), (64, 72, 80), (248, 224, 128), (200, 160, 64), (176, 200, 200)
CR, CRD, GOLD, GOLDD, BLU = (200, 56, 56), (136, 32, 40), (224, 184, 72), (168, 128, 48), (72, 104, 176)

FAMILIES = {
    "TRACK": [G, GD, GL, SH, W1, W2, W3, INK, (112, 80, 80), (144, 104, 96), (160, 128, 120), WDB, WDD, (176, 144, 104), FE1],
    "PAVILION": [(96, 136, 136), (72, 112, 112), (176, 144, 104), WDB, WDD, W1, W2, W3, INK, FE1, FE2, GLS, Y1, Y2, SILL],
    "STAND": [G, GD, GL, SH, WDB, WDD, (176, 144, 104), FE1, FE2, INK, Y1, Y2, GOLDD, W1, CR],
    "BRICK": [G, GD, GL, SH, BR1, BR2, BR3, MOR, DK1, DK0, SILL, IVY1, IVY2, INK],
    "GLOW": [BR1, BR2, BR3, MOR, DK1, DK0, IVY2, INK, V1, V2, V3, G, GD, SH, SILL],
    "FLOOR": [G, GD, GL, SH, T1, T2, T3, TR, TB, INK, BR2, MOR],
    "BAND": [T1, T2, T3, SH, W1, W2, W3, CU1, CU2, CU3, WDB, WDD, INK, IVY1, GD],
    "BANDD": [(176, 144, 104), WDB, WDD, W1, W2, W3, CU1, CU2, CU3, INK, IVY1, GD, SH],
    "IRON": [G, GD, GL, SH, FE1, FE2, INK, Y1, Y2, GLS, WDB, WDD, SILL, BR2, MOR],
    "CAROUSEL": [G, GD, GL, SH, W1, W2, W3, CR, CRD, GOLD, GOLDD, BLU, INK],
}


def grass_cv(w=1, h=1, bg=None):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, (bg or GRASS)(i, j))
    return cv


def rampart_top(cv, w):
    """Row 0 of a rampart piece: the grassed top of the earthwork, a brick coping along its front edge."""
    for j in range(16):
        for i in range(w):
            c = GD if (i * 3 + j) % 7 else SH
            if hashn(i, j, 701) < 0.08:
                c = G
            cv.put(i, j, c)
    for i in range(w):
        cv.put(i, 12, INK)
        cv.put(i, 13, SILL)
        cv.put(i, 14, BR1 if i % 6 else MOR)
        cv.put(i, 15, BR2 if i % 6 else MOR)


def brick_face(cv, x0, y0, w, h, seed=0, ivy=0.0):
    bricks(cv, x0, y0, w, h, (BR1, BR2, BR3), MOR, course=4, brick=8, wear=0.02, seed=seed)
    for i in range(x0, x0 + w):
        for j in range(y0, y0 + h):
            if hashn(i, j // 3, 711 + seed) < ivy and (i * 5 + j) % 3:
                cv.put(i, j, IVY1 if (i + j) % 2 else IVY2)
    for i in range(x0, x0 + w):
        cv.put(i, y0 + h - 1, DK1)                                       # the face's foot, in shadow


def rampart(ivy=False):
    """1x2 the rampart: grassed top, brick coping, brick face with ivy."""
    cv = Canvas(1, 2)
    rampart_top(cv, 16)
    brick_face(cv, 0, 16, 16, 16, seed=1 if ivy else 0, ivy=0.45 if ivy else 0.08)
    if ivy:
        for (x, n) in [(3, 12), (9, 15), (13, 8)]:
            for k in range(n):
                cv.put(x + (k % 4 == 1), 12 + k, IVY2 if k % 2 else IVY1)
    return cv


def casemate(glow=False):
    """2x2 an arched casemate in the rampart face: the brick vault's mouth, dark inside, its voussoirs picked out, a stone sill;
    glow: violet embers smouldering in the dark (Moltres)."""
    cv = Canvas(2, 2)
    rampart_top(cv, 32)
    brick_face(cv, 0, 16, 32, 16, seed=3, ivy=0.06)
    arch = set()
    for j in range(16, 32):
        for i in range(32):
            dx = i + 0.5 - 16
            top = 21 + (dx * dx) / 14.0
            if abs(dx) <= 10 and j >= top:
                arch.add((i, j))
    for (i, j) in arch:
        cv.put(i, j, DK0 if j > 24 or abs(i + 0.5 - 16) < 7 else DK1)
    for (i, j) in arch:
        for dx, dy in ((0, -1), (-1, 0), (1, 0)):
            q = (i + dx, j + dy)
            if q not in arch and 0 <= q[0] < 32 and q[1] >= 16:
                cv.put(q[0], q[1], SILL if dy == -1 and (q[0] % 3) else MOR)
    cv.hline(5, 26, 31, SILL)
    if glow:
        for (x, y) in [(13, 28), (15, 29), (17, 28), (19, 29), (14, 30), (16, 27), (18, 30), (12, 30)]:
            cv.put(x, y, V2)
        for (x, y) in [(15, 28), (17, 29), (16, 30)]:
            cv.put(x, y, V3)
        for (x, y) in [(11, 26), (20, 25), (14, 24), (18, 26), (13, 26)]:
            cv.put(x, y, V1)
    return cv


def pier():
    """1x2 a ruined brick pier standing alone on the parade ground, its top broken, ivy climbing it."""
    cv = grass_cv(1, 2)
    body = set()
    for j in range(2, 30):
        for i in range(3, 13):
            top = 2 + (4 if i > 8 else 0) + (2 if i in (5, 6) else 0)
            if j >= top:
                body.add((i, j))
    tmp = Canvas(1, 2)
    brick_face(tmp, 0, 0, 16, 32, seed=5, ivy=0.25)
    for (i, j) in body:
        cv.put(i, j, tmp.get(i, j))
    ink_outline(cv, body, INK, only_clear=False)
    for i in range(3, 14):
        cv.put(i, 30, SH)
    return cv


def rubble():
    """1x1 fallen brick in the grass, a broken sill stone among it."""
    cv = grass_cv()
    for (x, y, c) in [(3, 9, BR1), (7, 11, BR2), (11, 8, BR3), (5, 12, BR2), (9, 6, BR1), (12, 12, BR1), (2, 13, BR3)]:
        cv.rect(x, y, 3, 2, c)
        cv.hline(x, x + 2, y + 2, MOR)
    cv.rect(6, 3, 5, 2, SILL)
    cv.hline(6, 10, 5, INK)
    return cv


def floor_style(i, j, inside, d):
    """The dance floor: cracked terrazzo (pale ground, red and blue chips), grass pushing through its cracks; its edge a brick kerb."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        return SH if near == 1 and (i + j) % 2 else GRASS(i, j)
    if near == 1:
        return MOR
    if near == 2:
        return BR2 if (i + j) % 4 else MOR
    if (i * 7 + j * 3) % 41 == 0 or (abs((i - j * 2) % 23) < 1 and j % 5):
        return GD if hashn(i, j, 721) < 0.5 else T3                     # cracks, grass in them
    n = hashn(i, j, 722)
    if n < 0.04:
        return TR
    if n > 0.965:
        return TB
    if (i + j) % 16 == 0:
        return T2                                                        # the floor's squares
    return T1 if hashn(i // 2, j // 2, 723) > 0.25 else T2


def bandstand(bg=None):
    """4x3 the bandstand: an octagon of white posts with fretwork under a verdigris dome, its finial, a raised floor and steps at the
    front; a hole in the dome, ivy up one post. It stands on the dance floor (plain terrazzo under it)."""
    cv = Canvas(4, 3)
    for j in range(48):
        for i in range(64):
            cv.put(i, j, bg(i, j) if bg else (T1 if hashn(i // 2, j // 2, 723) > 0.25 else T2))
    cx = 32
    # the raised floor and its skirt
    for j in range(32, 44):
        for i in range(6, 58):
            c = WDB if j < 34 else (W2 if j < 42 else W3)
            if j >= 34 and (i % 6 == 0):
                c = W3
            cv.put(i, j, c)
    cv.hline(5, 58, 31, INK)
    cv.hline(5, 58, 44, INK)
    cv.vline(5, 31, 44, INK)
    cv.vline(58, 31, 44, INK)
    for k, y in enumerate((44, 46)):                                     # the steps
        cv.rect(24 - 2 * k, y, 16 + 4 * k, 2, W2 if k == 0 else W3)
        cv.hline(24 - 2 * k, 39 + 2 * k, y + 1, INK)
    # posts and fretwork
    for x in (8, 20, 32, 44, 55):
        cv.vline(x - 1, 14, 32, INK)
        cv.vline(x, 14, 32, W1)
        cv.vline(x + 1, 14, 32, W2)
        cv.vline(x + 2, 14, 32, INK)
    for x in range(8, 56):
        if x % 4 in (0, 1):
            cv.put(x, 16, W2)
        cv.put(x, 17, W1 if x % 2 else W3)
    for j in range(18, 31):
        for i in range(10, 55):
            if (j >= 18 and i >= 10 and i < 55 and cv.get(i, j) not in (W1, W2, W3, INK, IVY1, GD)):
                cv.put(i, j, WDD if j > 28 else (WDB if (i + j) % 7 == 0 else WDD))   # the floor seen under the roof
    # the dome
    for j in range(2, 16):
        t = (15 - j) / 13.0
        hw = 28 * math.sqrt(max(0.0, 1 - t ** 1.4))
        for i in range(64):
            dx = i + 0.5 - cx
            if abs(dx) <= hw:
                c = CU2
                if dx < -hw * 0.4:
                    c = CU1
                elif dx > hw * 0.55:
                    c = CU3
                if (i // 4 + j) % 5 == 0 and j < 14:
                    c = CU3 if c != CU3 else CU2                         # the ribs
                cv.put(i, j, c)
        cv.put(int(cx - hw) - 1, j, INK)
        cv.put(int(cx + hw) + 1, j, INK)
    cv.hline(2, 61, 15, INK)
    cv.hline(3, 60, 14, W2)
    for (i, j) in ellipse_body(40, 8, 4, 2.5):
        cv.put(i, j, INK if (i + j) % 3 else WDD)                         # the hole
    cv.vline(32, 0, 2, INK)
    cv.put(31, 1, W2)
    cv.put(33, 1, W2)
    for k in range(16):
        cv.put(56 + (k % 3 == 1), 16 + k, IVY1 if k % 2 else GD)          # ivy up the east post
    return cv


def lamp(bg=None):
    """1x2 a cast-iron lamp post of the pleasure garden, its glass globe broken."""
    cv = grass_cv(1, 2, bg)
    cv.rect(6, 10, 4, 20, FE2)
    cv.vline(6, 10, 29, FE1)
    cv.vline(5, 10, 29, INK)
    cv.vline(10, 10, 29, INK)
    cv.rect(4, 27, 8, 3, FE2)
    cv.hline(3, 12, 30, INK)
    for (i, j) in ellipse_body(8, 6, 4, 4):
        if not (i > 8 and j < 6):
            cv.put(i, j, GLS if (i + j) % 3 else SILL)
    cv.put(9, 3, INK)
    cv.put(10, 5, INK)
    cv.hline(5, 10, 10, INK)
    cv.put(8, 1, FE2)
    cv.hline(4, 12, 31, SH if not bg else PL3)
    return cv


def festoon(bg=None):
    """1x1 a string of dead bulbs sagging across the dance floor's edge (overhead: walkable)."""
    cv = grass_cv(1, 1, bg)
    for i in range(16):
        y = 4 + round(3 * math.sin(math.pi * i / 15))
        cv.put(i, y, INK)
        if i % 4 == 2:
            cv.put(i, y + 1, Y2)
            cv.put(i, y + 2, Y1 if i % 8 == 2 else GLS)
    return cv


def carousel_horse():
    """2x1 a carousel horse fallen in the grass: white body, red saddle, gold trim, the brass pole snapped off."""
    cv = grass_cv(2, 1)
    body = ellipse_body(15, 8, 8, 3.2)
    for (i, j) in body:
        cv.put(i, j, W1 if j < 8 else W2)
    head = ellipse_body(25, 6, 3.4, 2.4)
    for (i, j) in head:
        cv.put(i, j, W1 if j < 6 else W2)
    for (i, j) in ellipse_body(22, 7, 2.5, 2):
        cv.put(i, j, W2)
    ink_outline(cv, body | head, INK)
    for i in range(12, 18):
        cv.put(i, 5, CR)
        cv.put(i, 6, CRD)
    cv.hline(11, 18, 7, GOLD)
    cv.line(4, 9, 9, 13, W3)                                             # legs
    cv.line(5, 7, 9, 11, W2)
    cv.line(20, 10, 23, 13, W3)
    for (x, y) in [(27, 4), (28, 5), (26, 3)]:
        cv.put(x, y, CRD)                                                # the mane
    cv.put(26, 6, INK)
    cv.line(15, 4, 15, 0, GOLD)                                          # the snapped pole
    cv.put(16, 0, GOLDD)
    cv.line(1, 14, 7, 12, GOLDD)
    for (x, y) in [(10, 9), (19, 9)]:
        cv.put(x, y, BLU)
    for i in range(6, 28):
        if cv.get(i, 12) not in (INK, W2, W3):
            cv.put(i, 12, SH)
    return cv


def cannon():
    """2x1 an iron cannon on a rotted wooden carriage, pointing east over the parade ground."""
    cv = grass_cv(2, 1)
    cv.rect(4, 8, 14, 5, WDB)
    cv.hline(4, 17, 12, WDD)
    for (x, y) in [(7, 12), (15, 12)]:
        for (i, j) in ellipse_body(x, y, 3, 3):
            cv.put(i, j, WDD)
        cv.put(x, y, FE2)
    body = set()
    for i in range(6, 29):
        hw = 3.2 - (i - 6) * 0.06
        for j in range(16):
            if abs(j + 0.5 - 7) <= hw:
                body.add((i, j))
    for (i, j) in body:
        cv.put(i, j, FE1 if j < 6 else FE2)
    ink_outline(cv, body, INK, only_clear=False)
    cv.vline(28, 4, 9, INK)
    for i in range(4, 30):
        cv.put(i, 15, SH)
    return cv


def shot():
    """1x1 a pyramid of iron shot."""
    cv = grass_cv()
    for (x, y) in [(4, 11), (8, 11), (12, 11), (6, 8), (10, 8), (8, 5)]:
        for (i, j) in ellipse_body(x, y, 2.2, 2.0):
            cv.put(i, j, FE1 if i < x and j < y else FE2)
        cv.put(x - 1, y - 1, SILL)
    cv.hline(2, 14, 13, SH)
    return cv


# ---------------------------------------------------------------- revision 3: the other two Galarian lairs
# Galarian Zapdos: the Bush Track (off Route 14, east): a Cajun "bush track", a straight dirt strip in the country where match races are
# run between two horses, a plank starting gate at one end, a judge's stand at the finish, benches, hay. The track is the primary's mud.
# Galarian Articuno: the Milneburg pavilion (off Route 10, by Surf): a jazz-age dance pavilion out on the lake on its pilings, where bands
# played on the camps' weekends: a plank deck with a white railing, the bandstand, cafe tables, lamps, dead festoons, a gramophone.
MUD = None
PL1, PL2, PL3 = (176, 144, 104), (136, 104, 72), (88, 64, 48)          # the pavilion's planks (PL2, PL3 = WDB, WDD)
WA, WA_D = (96, 136, 136), (72, 112, 112)
MUD1, MUD2, MUD3 = (112, 80, 80), (144, 104, 96), (160, 128, 120)       # the primary's mud (the track)


def _mud_tex():
    from lair_kit_b2 import pcell, tex_from
    return tex_from(pcell("ekat:mud_C"))


def plank_tex(i, j):
    """The pavilion's deck: boards running east-west, 4 px wide, butt joints staggered, a nail head here and there."""
    row = j // 4
    if j % 4 == 3:
        return PL3
    if (i + row * 6) % 16 == 0:
        return PL3
    c = PL1 if j % 4 == 0 else PL2
    if (i * 3 + row * 5) % 23 == 0:
        c = PL3
    return c


def deck_style(i, j, inside, d):
    """The deck on the lake (inside = planks): a white railing along its rim, posts every 8 px; outside, the water, the deck's shadow
    and the tops of its pilings showing under the south edge."""
    near = min(v for v in (d["dn"], d["ds"], d["dw"], d["de"], 9) if v is not None)
    if not inside:
        if d["dn"] is not None and d["dn"] <= 2:
            return WA_D if d["dn"] == 1 else (PL3 if i % 8 in (3, 4) else WA_D)   # the deck's shadow, a piling's head
        return WA
    if near == 1:
        return INK
    if near == 2:
        return W1 if (d["dn"] == 2 or d["dw"] == 2) else W2                    # the top rail
    if near == 3:
        along = i if (d["dn"] == 3 or d["ds"] == 3) else j
        return W3 if along % 8 == 0 else plank_tex(i, j)                       # the posts
    return plank_tex(i, j)


def table():
    """1x1 a little round cafe table on the deck, two bentwood chairs, an empty glass."""
    cv = grass_cv(1, 1, plank_tex)
    for (i, j) in ellipse_body(8, 7, 4.2, 3.2):
        cv.put(i, j, W1 if j < 7 else W2)
    ink_outline(cv, ellipse_body(8, 7, 4.2, 3.2), INK, only_clear=False)
    cv.vline(8, 10, 13, FE2)
    cv.hline(6, 10, 14, FE2)
    for x in (1, 13):
        cv.rect(x, 6, 2, 6, FE2)
        cv.hline(x - 1, x + 2, 9, FE1)
    cv.put(9, 6, GLS)
    cv.put(9, 5, GLS)
    return cv


def gramophone():
    """1x1 a gramophone left on a crate, its brass horn turned to the empty floor."""
    cv = grass_cv(1, 1, plank_tex)
    cv.rect(3, 8, 10, 6, WDB)
    cv.hline(3, 12, 8, PL1)
    cv.hline(2, 13, 14, INK)
    cv.rect(5, 6, 6, 2, WDD)
    cv.vline(8, 2, 6, FE2)
    for k in range(7):
        r = 1 + k * 0.6
        cv.put(round(8 + k), round(2 - k * 0.3), Y2)
        cv.put(round(8 + k), round(2 + r), Y2)
        cv.vline(round(8 + k), round(2 - k * 0.3), round(2 + r), Y1 if k > 4 else Y2)
    return cv


def piling():
    """1x1 old pilings standing out of the lake where the deck has gone (blocking)."""
    cv = Canvas(1, 1)
    for j in range(16):
        for i in range(16):
            cv.put(i, j, WA if (i * 3 + j * 5) % 29 else WA_D)
    for (x, y) in [(3, 4), (11, 6), (6, 11)]:
        for (i, j) in ellipse_body(x, y, 2.2, 1.8):
            cv.put(i, j, PL1 if i < x else PL2)
        cv.put(x, y, PL3)
        for k in range(3):
            cv.put(x - 1 + k, y + 2, WA_D)
    return cv


def rail(kind):
    """1x1 the track's white rail on the grass: 'h' running east-west (two rails, a post every 8 px), 'end' a corner post."""
    cv = grass_cv()
    if kind == "h":
        cv.hline(0, 15, 6, W1)
        cv.hline(0, 15, 7, W3)
        cv.hline(0, 15, 10, W1)
        cv.hline(0, 15, 11, W3)
        for x in (3, 11):
            cv.rect(x, 4, 2, 10, W1)
            cv.vline(x + 1, 4, 13, W2)
            cv.put(x, 14, SH)
            cv.put(x + 1, 14, SH)
    else:
        cv.hline(0, 7, 6, W1)
        cv.hline(0, 7, 7, W3)
        cv.hline(0, 7, 10, W1)
        cv.hline(0, 7, 11, W3)
        cv.rect(7, 3, 3, 11, W1)
        cv.vline(9, 3, 13, W2)
        cv.hline(6, 10, 2, INK)
    return cv


def start_gate():
    """3x2 the starting gate across the track's west end: a plank frame of two stalls, their gates shut, a rope across the top."""
    mud = _mud_tex()
    cv = grass_cv(3, 2, mud)
    for x in (4, 20, 36):
        cv.rect(x, 2, 4, 28, WDB)
        cv.vline(x, 2, 29, PL1)
        cv.vline(x + 3, 2, 29, WDD)
        cv.hline(x - 1, x + 4, 1, INK)
    for x0 in (8, 24):
        for y in (8, 16, 24):
            cv.hline(x0, x0 + 11, y, PL1)
            cv.hline(x0, x0 + 11, y + 1, WDD)
    cv.line(4, 3, 40, 3, FE1)
    for i in range(2, 44):
        cv.put(i, 30, MUD1)
    return cv


def judge_stand():
    """2x3 the judge's stand at the finish: a little raised box of planks under a tin roof, a ladder, a bell."""
    cv = grass_cv(2, 3)
    cv.rect(4, 2, 24, 8, FE1)
    cv.hline(3, 28, 1, INK)
    cv.hline(3, 28, 10, INK)
    for i in range(4, 28, 3):
        cv.vline(i, 2, 9, FE2)
    cv.rect(6, 11, 20, 12, WDB)
    cv.hline(6, 25, 11, PL1)
    cv.rect(9, 13, 14, 5, INK)
    for x in (6, 25):
        cv.vline(x, 11, 45, WDD)
        cv.vline(x + 1, 23, 45, WDB)
    for y in range(26, 45, 4):
        cv.hline(14, 18, y, PL1)
    cv.vline(14, 23, 45, WDD)
    cv.vline(18, 23, 45, WDD)
    cv.rect(24, 12, 3, 3, Y2)
    cv.hline(5, 27, 46, SH)
    return cv


def finish_post():
    """1x2 the finish post: a white post, a red disc at its head."""
    cv = grass_cv(1, 2)
    cv.rect(7, 10, 3, 20, W1)
    cv.vline(9, 10, 29, W3)
    cv.vline(6, 10, 29, INK)
    cv.vline(10, 10, 29, INK)
    for (i, j) in ellipse_body(8.5, 6, 4.5, 4.5):
        cv.put(i, j, CR if (i - 8) ** 2 + (j - 6) ** 2 > 4 else W1)
    ink_outline(cv, ellipse_body(8.5, 6, 4.5, 4.5), INK, only_clear=False)
    cv.hline(5, 12, 30, SH)
    return cv


def benches():
    """2x1 plank benches for the crowd along the rail."""
    cv = grass_cv(2, 1)
    for y in (3, 9):
        cv.rect(2, y, 28, 3, PL1)
        cv.hline(2, 29, y + 2, WDD)
        for x in (4, 27):
            cv.vline(x, y + 3, y + 5, WDD)
    return cv


def hay():
    """1x1 a hay bale, twine round it."""
    cv = grass_cv()
    cv.rect(2, 4, 12, 9, Y2)
    cv.hline(2, 13, 4, Y1)
    cv.hline(2, 13, 12, GOLDD)
    for x in (5, 10):
        cv.vline(x, 4, 12, GOLDD)
    cv.hline(1, 14, 13, INK)
    cv.hline(2, 13, 14, SH)
    return cv


def build():
    P = Pieces("lf")
    P.add("rampart", rampart(False), comment="1x2 the north rampart (grassed top, brick face), blocking", lair="galar")
    P.add("rampart_ivy", rampart(True), comment="1x2 the rampart under ivy, blocking", lair="galar")
    P.add("casemate", casemate(False), comment="2x2 an arched casemate, dark inside, blocking", lair="galar")
    P.add("casemate_glow", casemate(True), comment="2x2 Moltres' casemate, violet embers in the dark, blocking", lair="galar")
    P.add("pier", pier(), comment="1x2 a ruined brick pier, blocking", lair="galar")
    P.add("rubble", rubble(), comment="1x1 fallen brick, blocking", lair="galar")
    P.add_set("floor", dual_set(floor_style, ro=4, ri=4, wob=0), walk=True, comment="the old terrazzo dance floor", lair="galar")
    P.add("bandstand", bandstand(), comment="4x3 the bandstand, blocking", lair="galar")
    P.add("lamp", lamp(), comment="1x2 a cast-iron lamp post, its globe broken, blocking", lair="galar")
    P.add("festoon", festoon(), walk=True, comment="1x1 a string of dead bulbs overhead (walkable)", lair="galar")
    P.add("carousel_horse", carousel_horse(), comment="2x1 a fallen carousel horse, blocking", lair="galar")
    P.add("cannon", cannon(), comment="2x1 an old iron cannon, blocking", lair="galar")
    P.add("shot", shot(), comment="1x1 a pyramid of shot, blocking", lair="galar")
    # revision 3: Galarian Zapdos' bush track and Galarian Articuno's lakefront pavilion
    for k in ("h", "end"):
        P.add(f"rail_{k}", rail(k), comment=f"1x1 the track's white rail ({k}), blocking", lair="galar_zapdos")
    P.add("start_gate", start_gate(), comment="3x2 the starting gate on the track, blocking", lair="galar_zapdos")
    P.add("judge_stand", judge_stand(), comment="2x3 the judge's stand at the finish, blocking", lair="galar_zapdos")
    P.add("finish_post", finish_post(), comment="1x2 the finish post, blocking", lair="galar_zapdos")
    P.add("benches", benches(), comment="2x1 benches for the crowd, blocking", lair="galar_zapdos")
    P.add("hay", hay(), comment="1x1 a hay bale, blocking", lair="galar_zapdos")
    P.add_set("deck", dual_set(deck_style, ro=4, ri=4, wob=0), walk=True, comment="the pavilion's deck on the lake, railed",
              lair="galar_articuno")
    P.add("bandstand_d", bandstand(plank_tex), comment="4x3 the bandstand on the pavilion's deck, blocking", lair="galar_articuno")
    P.add("lamp_d", lamp(plank_tex), comment="1x2 a lamp post on the deck, blocking", lair="galar_articuno")
    P.add("festoon_d", festoon(plank_tex), walk=True, comment="1x1 dead bulbs over the deck (walkable)", lair="galar_articuno")
    P.add("table", table(), comment="1x1 a cafe table and two chairs on the deck, blocking", lair="galar_articuno")
    P.add("gramophone", gramophone(), comment="1x1 a gramophone on a crate, blocking", lair="galar_articuno")
    P.add("piling", piling(), comment="1x1 old pilings in the lake, blocking", lair="galar_articuno")
    return P


def main():
    P = build()
    bad = write_b2(P, "lair_fort.png", "orleans_lair_fort", "gTileset_OrleansLairFort", "orleans_general.mapping.json",
                   FAMILIES, "Spanish Fort (the Galarian birds)", "make_lair_fort.py")
    for b in bad[:40]:
        print("off-family:", b)
    print(f"lair_fort: {len(P.order)} pieces, sheet {P.image.size}, {len(bad)} off-family tiles")
    return P


if __name__ == "__main__":
    main()

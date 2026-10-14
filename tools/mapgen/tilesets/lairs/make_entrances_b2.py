"""The batch-2 lairs' entrance art on their routes: OVERLAYS (magenta = clear) drawn over whatever the route has at the spot (canopy,
its edge cells, marsh, grass, scrub, dry ground), as batch 1's make_entrances.py; build.py composes them into the route's own tileset.
A second overlay source, "le2" (batch 1's is "lent"), so the batch-1 entrances keep their names.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/make_entrances_b2.py
writes tools/mapgen/tilesets/lairs/entrances_b2.png + entrances_b2.json (pieces, the overlay source, prefabs, per-route placements).

Each piece is drawn in the colours of what it stands on (the swamp canopy, the marsh and grass, the dry scrub) plus a few accents, so
it lands in the route's existing palettes; lair_mocks_b2.py measures that against each route tileset.
    spirit_gate_e / _moss   (Route 1, Mesprit) a trail into the canopy (the wall to the east) between two carved cedar posts, a cord
                            of pink charms across its mouth; sealed: a curtain of Spanish moss hanging over it
    grove_gap               (Route 23, Azelf) a cleft into the north scrub, green showing beyond it (the grove), a cedar post with blue
                            charms at its side; sealed: the notch filled with the scrub block (as the Ursaluna cleft)
    field_gate / _shut      (Route 23, Landorus) a split-rail field gate across the south scrub notch, swung open (a cart track
                            through) / shut and chained
    levee_steps_e / _log    (Route 12, Thundurus) plank steps up a grassy bank into the canopy (east), a storm lantern on a post;
                            sealed: a fallen trunk across the mouth
    liana_gap_e / liana_curtain_e   (Route 13, Zarude) a trail into the canopy (east), lianas pulled aside; sealed: a liana curtain
    courir_gap_w / liana_curtain_w  (Route 13, Ogerpon) a trail into the canopy (west), a Courir ribbon-stake beside it; sealed:
                            a liana curtain
    wind_gap_n              (Route 3, Tornadus) a trail into the canopy (north) at the marsh notch, the trees either side combed
                            east by the wind, a bent windsock pole; sealed: the canopy as built
    sally_port_w / _bricked (Route 14, the Galarian birds) the brick piers of an old fort gate in the canopy (west), the trail
                            through it; sealed: the gate bricked up and grown over
    mill_door_ajar 1x2      (Route 17, Moltres; optional, the Capital tileset is full) the mill's plank door ajar, firelight in it
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import Canvas, Pieces, dump, hashn  # noqa: E402
import make_entrances as E1  # noqa: E402  (batch 1's colours and its canopy_gap_w)

S_OUT, C_DK, C_MID, C_HL, C_TIP = E1.S_OUT, E1.C_DK, E1.C_MID, E1.C_HL, E1.C_TIP
GD, SH = E1.GD, E1.SH
G, GL = (120, 160, 104), (136, 176, 128)
ST1, ST2, ST3, ST4, INK, MO = E1.ST1, E1.ST2, E1.ST3, E1.ST4, E1.INK, E1.MO
D1, D2, D3 = E1.D1, E1.D2, E1.D3
L0, L1, L2 = E1.L0, E1.L1, E1.L2
K0, K1, K2 = E1.K0, E1.K1, E1.K2
B0, B1, B2 = E1.B0, E1.B1, E1.B2
MOSS1, MOSS2 = (152, 168, 144), (200, 208, 176)                  # Spanish moss (the wet lairs' / the oak's)
CE1, CE2, CE3 = (96, 56, 40), (136, 80, 56), (176, 112, 72)      # cedar
PINK, PINK_D, BLUE, BLUE_D = (232, 160, 176), (184, 104, 128), (128, 184, 248), (64, 104, 208)
BR1, BR2, BR3, MOR = (200, 128, 88), (144, 88, 80), (128, 80, 72), (88, 72, 80)    # the Drowned Ward's brick
PU, YE, RD = (136, 72, 168), (232, 216, 96), (232, 88, 56)
GLOW1, GLOW2 = (248, 160, 48), (216, 88, 32)
WD1, WD2, WD3 = (88, 64, 48), (136, 104, 72), (184, 152, 104)


def hollow(cv, d, x0=0, y0=0):
    """A dark way into the canopy in a 2x2 overlay: the recess heading east ('e', in the right column), west ('w', in the left
    column) or north ('n', in the top row); leaves hang over its mouth."""
    for j in range(32):
        for i in range(32):
            if d == "e":
                v = ((i - 12) / 22.0) ** 1.5 if i >= 12 else 9
                v += ((j + 0.5 - 16) / 11.0) ** 2
            elif d == "w":
                v = ((19 - i) / 22.0) ** 1.5 if i <= 19 else 9
                v += ((j + 0.5 - 16) / 11.0) ** 2
            else:
                v = ((19 - j) / 22.0) ** 1.5 if j <= 19 else 9
                v += ((i + 0.5 - 16) / 11.0) ** 2
            if v <= 1.0 - 0.08 * math.sin((j if d != "n" else i) * 1.3):
                cv.put(x0 + i, y0 + j, S_OUT if v > 0.25 or (i + j) % 2 else C_DK)
    # fringe of leaves over the mouth
    if d in ("e", "w"):
        rng = range(12, 32) if d == "e" else range(0, 20)
        for i in rng:
            for (base, sgn) in ((5, 1), (27, -1)):
                n = int(3 * hashn(i, base, 7))
                for k in range(n + 1):
                    cv.put(x0 + i, y0 + base + sgn * k, C_MID if k < n else C_HL)
    else:
        for j in range(0, 20):
            for (base, sgn) in ((5, 1), (26, -1)):
                n = int(3 * hashn(base, j, 7))
                for k in range(n + 1):
                    cv.put(x0 + base + sgn * k, y0 + j, C_MID if k < n else C_HL)


def trail(cv, d):
    """Trampled grass and mud leading into the way (the column / row before the hollow)."""
    for j in range(32):
        for i in range(32):
            inside = {"e": i < 16 and 9 <= j < 24, "w": i >= 16 and 9 <= j < 24, "n": j >= 16 and 9 <= i < 24}[d]
            if inside:
                if ((i * 2 + j * 3) % 9) in (0, 1):
                    cv.put(i, j, SH)
                elif (i + 2 * j) % 11 == 0:
                    cv.put(i, j, GD)


def cedar_post(cv, x, y0, y1, charm=None):
    for j in range(y0, y1 + 1):
        cv.put(x, j, CE3)
        cv.put(x + 1, j, CE2)
        cv.put(x + 2, j, CE1)
        cv.put(x - 1, j, INK)
        cv.put(x + 3, j, INK)
        if (j - y0) % 5 == 2:
            cv.put(x + 1, j, CE1)                                        # the carved rings
    cv.hline(x - 1, x + 3, y0 - 1, INK)
    cv.hline(x, x + 2, y0 - 2, INK)
    cv.put(x + 1, y0 - 2, CE3)
    if charm:
        a, b = charm
        for k in range(4):
            cv.put(x + 3 + (k % 2), y0 + 3 + k, a if k % 2 else b)


def spirit_gate_e(sealed):
    cv = Canvas(2, 2)
    hollow(cv, "e")
    trail(cv, "e")
    cedar_post(cv, 13, 3, 12, (PINK, PINK_D))
    cedar_post(cv, 13, 20, 29, (PINK, PINK_D))
    for k in range(9, 21):                                               # a cord of pink charms across the mouth
        x = 15 + round(1.5 * math.sin((k - 9) * math.pi / 11))
        cv.put(x, k, CE3)
        if k % 3 == 0:
            cv.put(x + 1, k, PINK)
            cv.put(x + 1, k + 1, PINK_D)
    if sealed:
        for i in range(17, 32):
            for j in range(4, 29):
                if (i % 3 != 1 or j < 8 + (i * 5) % 7) and hashn(i, j, 901) < 0.85:
                    cv.put(i, j, MOSS1 if (i + j) % 3 else MOSS2)
    return cv


def grove_gap(sealed=False):
    """2x2 a cleft into the north scrub with the grove's green showing beyond, a cedar post hung with blue charms at its west side."""
    cv = Canvas(2, 2)
    for j in range(0, 24):
        w = 3.5 + j * 0.25
        for i in range(32):
            if abs(i + 0.5 - 17) < w:
                c = L1 if (i + 2 * j) % 5 else L2                       # green beyond: the grove's leaves
                if j > 14:
                    c = L0 if (i + j) % 2 else L1
                cv.put(i, j, c)
    for side in (1, -1):                                                 # the thicket jaws either side
        for j in range(0, 24):
            for k in range(6):
                i = (12 - k) if side == 1 else (22 + k)
                if k <= 3 + 2 * math.sin(j * 0.5 + side):
                    cv.put(i, j, L2 if k == 0 else (L1 if (i + j) % 3 else L0))
    for j in range(22, 32):
        for i in range(6, 28):
            if (i * 3 + j) % 7 in (0, 1):
                cv.put(i, j, D2)
            elif (i + j) % 2 == 0 and j < 25:
                cv.put(i, j, D3)
    cedar_post(cv, 6, 12, 28, (BLUE, BLUE_D))
    return cv


def field_gate(shut):
    """2x2 a split-rail field gate in the south scrub notch: open (swung back against the scrub, a cart track through) or shut and
    chained."""
    cv = Canvas(2, 2)
    for j in range(0, 32):                                               # the cart track
        for i in range(8, 24):
            if i in (10, 11, 20, 21):
                cv.put(i, j, D3 if (j % 3) else D2)
    for x in (3, 28):                                                    # the gate posts
        for j in range(4, 26):
            cv.put(x, j, B1)
            cv.put(x + 1, j, B0)
            cv.put(x - 1, j, B0)
        cv.hline(x - 1, x + 1, 3, B0)
    if shut:
        for y in (8, 14, 20):
            cv.hline(4, 27, y, B2)
            cv.hline(4, 27, y + 1, B1)
            cv.hline(4, 27, y + 2, B0)
        cv.line(5, 8, 26, 22, B2)
        for (x, y) in [(26, 13), (27, 14), (26, 15), (27, 16)]:
            cv.put(x, y, K1)                                             # the chain
    else:
        for k in range(3):                                               # swung back flat against the west scrub
            cv.vline(5 + k * 2, 6, 24, B2 if k % 2 else B1)
        cv.line(5, 6, 9, 24, B0)
    return cv


def levee_steps_e(sealed):
    """2x2 plank steps climbing a grassy bank into the canopy (east), a storm lantern on a post at their foot; sealed: a fallen trunk."""
    cv = Canvas(2, 2)
    hollow(cv, "e")
    for k in range(5):                                                   # the steps, rising east
        x = 6 + k * 4
        for j in range(10, 23):
            cv.put(x, j, WD3 if j % 4 else WD1)
            cv.put(x + 1, j, WD2)
            cv.put(x + 2, j, WD1)
    cv.vline(4, 4, 12, WD1)
    cv.vline(3, 4, 12, INK)
    cv.vline(5, 4, 12, INK)
    cv.rect(2, 1, 5, 4, GLOW1)
    cv.rect(3, 2, 3, 2, YE)
    cv.hline(2, 6, 0, INK)
    cv.hline(2, 6, 5, INK)
    if sealed:
        for j in range(12, 21):
            for i in range(2, 32):
                c = B1 if j < 15 else (B0 if j > 18 else B2)
                if (i + j) % 9 == 0:
                    c = MO
                cv.put(i, j, c)
        cv.hline(2, 31, 11, INK)
        cv.hline(2, 31, 21, INK)
        for (i, j) in [(1, 14), (1, 15), (1, 16), (1, 17)]:
            cv.put(i, j, B2)
    return cv


def liana_gap(d, sealed, courir=False):
    """2x2 a trail into the canopy (wall east 'e' / west 'w'), lianas pulled aside (open) or hanging as a curtain (sealed); courir: a
    ribbon-stake in the Courir's colours beside it (Ogerpon)."""
    cv = Canvas(2, 2)
    hollow(cv, d)
    trail(cv, d)
    xs = range(17, 32) if d == "e" else range(0, 15)
    for x in xs:
        if x % 3 == 0:
            if sealed:
                for k in range(4, 30):
                    cv.put(x + round(math.sin(k * 0.3 + x) * 0.8), k, C_DK if k % 4 else C_MID)
            else:
                edge = (x < 21) if d == "e" else (x > 10)
                if edge or x in (30, 1):
                    for k in range(4, 30):
                        cv.put(x, k, C_DK if k % 4 else C_MID)
    if courir:
        sx = 26 if d == "w" else 4
        for j in range(4, 30):
            cv.put(sx, j, WD2)
            cv.put(sx + 1, j, WD1)
            cv.put(sx - 1, j, INK)
            cv.put(sx + 2, j, INK)
        for (x, n, c) in [(sx + 3, 10, PU), (sx + 4, 8, YE), (sx - 2, 9, RD), (sx + 3, 6, BLUE)]:
            for k in range(n):
                cv.put(x + (k % 3 == 2), 6 + k, c)
    return cv


def wind_gap_n():
    """2x2 a trail into the canopy at the north notch, the trees either side combed east by the wind, a bent windsock on a pole."""
    cv = Canvas(2, 2)
    hollow(cv, "n")
    trail(cv, "n")
    for j in range(0, 16):                                               # the leaves combed east on both sides of the way
        for i in range(0, 32):
            if (i < 8 or i > 24) and (i + j * 2) % 5 == 0:
                cv.put(i, j, C_HL if (i + j) % 2 else C_TIP)
    cv.vline(3, 14, 30, WD1)
    cv.vline(2, 14, 30, INK)
    cv.vline(4, 14, 30, INK)
    for k in range(9):                                                   # the windsock, streaming east
        y = 14 + k // 3
        cv.put(5 + k, y, RD if (k // 2) % 2 else (240, 240, 232))
        cv.put(5 + k, y + 1, RD if (k // 2) % 2 else (200, 200, 184))
    return cv


def sally_port_w(bricked):
    """2x2 the old fort's sally port in the canopy (wall west): two square brick piers at the trail's mouth (north and south of it),
    the arch between them fallen; sealed: the gate bricked up and grown over."""
    cv = Canvas(2, 2)
    hollow(cv, "w")
    trail(cv, "w")
    for y0 in (2, 22):
        for j in range(y0, y0 + 9):
            for i in range(10, 22):
                c = BR2 if ((i // 4) + (j // 3)) % 2 else BR3
                if j % 3 == 2 or (i + (2 if (j // 3) % 2 else 0)) % 4 == 0:
                    c = MOR
                if j == y0:
                    c = BR1
                cv.put(i, j, c)
        cv.hline(9, 22, y0 - 1, INK)
        cv.vline(9, y0 - 1, y0 + 9, INK)
        cv.vline(22, y0 - 1, y0 + 9, INK)
        cv.hline(9, 22, y0 + 9, INK if y0 == 22 else SH)
    for (x, y) in [(14, 12), (17, 13), (12, 19)]:
        cv.rect(x, y, 3, 2, BR2)                                         # fallen brick of the arch
        cv.hline(x, x + 2, y + 2, MOR)
    if bricked:
        for j in range(10, 22):
            for i in range(0, 21):
                c = BR2 if ((i // 4) + (j // 3)) % 2 else BR3
                if j % 3 == 2 or (i + (2 if (j // 3) % 2 else 0)) % 4 == 0:
                    c = MOR
                if hashn(i, j, 911) < 0.3:
                    c = C_DK if (i + j) % 2 else C_MID                   # grown over
                cv.put(i, j, c)
    return cv


def mill_door_ajar():
    """1x2 the mill's plank double door standing ajar, firelight glowing in the gap (Route 17; optional)."""
    cv = Canvas(1, 2)
    for j in range(8, 32):
        for i in range(6, 10):
            c = GLOW1 if j > 14 else GLOW2
            if (i + j) % 5 == 0:
                c = YE
            cv.put(i, j, c)
    cv.vline(5, 8, 31, INK)
    cv.vline(10, 8, 31, INK)
    return cv


PLACEMENTS = {
    # route: tileset, the lair, open overlays, sealed (overlays or a fill description), triggers (walk into), the cell the lair returns to
    "Route1": {"tileset": "orleans_bayou", "lair": "mesprit", "open": [["spirit_gate_e", 26, 27]], "sealed": [["spirit_gate_e_moss", 26, 27]],
               "trigger": [[27, 27], [27, 28]], "heading": "east", "back": [26, 27, "LEFT"], "opens": "story 45"},
    "Route23_N": {"tileset": "orleans_route_dry", "lair": "azelf", "open": [["grove_gap", 33, 1]],
                  "sealed": "the feather notch at x 33-34, rows 0-1, filled with the dry scrub block (as the Ursaluna cleft at 22-23)",
                  "trigger": [[33, 1], [34, 1]], "heading": "north", "back": [33, 2, "DOWN"], "opens": "story 45"},
    "Route23_S": {"tileset": "orleans_route_dry", "lair": "landorus", "open": [["field_gate", 27, 38]], "sealed": [["field_gate_shut", 27, 38]],
                  "trigger": [[27, 39], [28, 39]], "heading": "south", "back": [27, 37, "UP"], "opens": "story 45"},
    "Route12": {"tileset": "orleans_route", "lair": "thundurus", "open": [["levee_steps_e", 25, 22]], "sealed": [["levee_steps_e_log", 25, 22]],
                "trigger": [[26, 22], [26, 23]], "heading": "east", "back": [24, 22, "LEFT"], "opens": "story 45"},
    "Route13_E": {"tileset": "orleans_route", "lair": "zarude", "open": [["liana_gap_e", 26, 25]], "sealed": [["liana_curtain_e", 26, 25]],
                  "trigger": [[27, 25], [27, 26]], "heading": "east", "back": [26, 26, "LEFT"], "opens": "story 45"},
    "Route13_W": {"tileset": "orleans_route", "lair": "ogerpon", "open": [["courir_gap_w", 0, 25]], "sealed": [["liana_curtain_w", 0, 25]],
                  "trigger": [[0, 25], [0, 26]], "heading": "west", "back": [2, 25, "RIGHT"], "opens": "story 45"},
    "Route3": {"tileset": "orleans_crescent", "lair": "tornadus",
               "open": "the marsh notch as built (x 27-28, rows 1-2); optional wind_gap_n at (27,0) only if 16 Crescent tiles are freed",
               "sealed": "the notch filled with the swamp canopy block (rows 0-1, primary pieces), bd:swamp_S_marsh_X on row 2",
               "trigger": [[27, 1], [28, 1]], "heading": "north", "back": [27, 2, "DOWN"], "opens": "story 45",
               "note": "Crescent is full (510/512 tiles): no new art by default, as Raikou's Route 2"},
    "Route14": {"tileset": "orleans_route_b", "lair": "galar", "open": [["sally_port_w", 0, 7]], "sealed": [["sally_port_w_bricked", 0, 7]],
                "trigger": [[0, 7], [0, 8]], "heading": "west", "back": [2, 7, "RIGHT"], "opens": "story 45"},
    "Route17": {"tileset": "orleans_capital", "lair": "moltres", "open": "the mill door as built, its warp live (optionally mill_door_ajar at (33,8), 5 tiles, only if Capital frees them: 508/512)",
                "sealed": "the mill door as built, no warp (a 'barred' message)", "trigger": [[33, 9]], "heading": "north",
                "back": [33, 10, "DOWN"], "opens": "story 45"},
}


def route_palettes(sec):
    """The route's 13 palettes (primary 0-5, secondary 6-12), colours 1-15 each."""
    from lair_kit import ROOT
    pals = []
    for d, rng in (("data/tilesets/primary/orleans_general", range(0, 6)), (f"data/tilesets/secondary/{sec}", range(6, 13))):
        for i in rng:
            p = os.path.join(ROOT, d, "palettes", f"{i:02d}.pal")
            if os.path.exists(p):
                lines = open(p).read().splitlines()[4:19]
                pals.append([tuple(int(v) for v in l.split()) for l in lines if l.strip()])
    return pals


def snap_to_route(cv, route, x0, y0):
    """Snap the overlay so that, composited over the route's ground at (x0, y0), every 8x8 tile is drawn by ONE palette the route
    already has: per tile, the palette that holds all the ground colours left showing and is nearest to the overlay's own colours."""
    import lair_mocks as B1
    ts, names, blocks, W, H, sec = B1.route_render(route)
    pals = route_palettes(sec)
    from PIL import Image
    ground = Image.new("RGB", (cv.w, cv.h))
    for j in range(cv.ch):
        for i in range(cv.cw):
            ground.paste(ts.metatile(blocks[(y0 + j) * W + x0 + i] & 0x3FF).convert("RGB"), (i * 16, j * 16))
    g = ground.load()

    def d2(a, b):
        return sum((p - q) ** 2 for p, q in zip(a, b))
    for ty in range(0, cv.h, 8):
        for tx in range(0, cv.w, 8):
            px = [(i, j) for j in range(ty, ty + 8) for i in range(tx, tx + 8)]
            over_px = [(i, j, cv.get(i, j)) for (i, j) in px if cv.get(i, j) is not None]
            if not over_px:
                continue
            showing = {g[i, j] for (i, j) in px if cv.get(i, j) is None}
            cands = [p for p in pals if showing <= set(p)] or pals
            best = min(cands, key=lambda p: sum(min(d2(c, q) for q in p) for (_, _, c) in over_px))
            for (i, j, c) in over_px:
                if c not in best:
                    cv.put(i, j, min(best, key=lambda q: d2(c, q)))
    return cv


SNAP = {  # piece -> (route, x, y) where it stands (its colours are snapped into that route's palettes)
    "spirit_gate_e": ("Route1", 26, 27), "spirit_gate_e_moss": ("Route1", 26, 27), "grove_gap": ("Route23", 33, 1),
    "field_gate": ("Route23", 27, 38), "field_gate_shut": ("Route23", 27, 38), "levee_steps_e": ("Route12", 25, 22),
    "levee_steps_e_log": ("Route12", 25, 22), "liana_gap_e": ("Route13", 26, 25), "liana_curtain_e": ("Route13", 26, 25),
    "courir_gap_w": ("Route13", 0, 25), "liana_curtain_w": ("Route13", 0, 25), "wind_gap_n": ("Route3", 27, 0),
    "sally_port_w": ("Route14", 0, 7), "sally_port_w_bricked": ("Route14", 0, 7), "mill_door_ajar": ("Route17", 33, 8),
}


def build():
    P = build_raw()
    for n in P.order:
        if n in SNAP:
            snap_to_route(P.items[n]["cv"], *SNAP[n])
    return P


def build_raw():
    P = Pieces("le2")
    P.add("spirit_gate_e", spirit_gate_e(False), walk=[[1, 0], [1, 1]], comment="2x2 overlay: a trail into the canopy (east) between cedar posts, pink charms (Route 1)", lair="mesprit")
    P.add("spirit_gate_e_moss", spirit_gate_e(True), comment="2x2 overlay: the same, a curtain of Spanish moss over it (sealed)", lair="mesprit")
    P.add("grove_gap", grove_gap(), walk=[[0, 0], [1, 0], [0, 1], [1, 1]], comment="2x2 overlay: a cleft into the north scrub, the grove beyond, blue charms (Route 23)", lair="azelf")
    P.add("field_gate", field_gate(False), walk=[[0, 0], [1, 0], [0, 1], [1, 1]], comment="2x2 overlay: the field gate swung open (Route 23 south)", lair="landorus")
    P.add("field_gate_shut", field_gate(True), walk=[[0, 0], [1, 0]], comment="2x2 overlay: the field gate shut and chained (sealed)", lair="landorus")
    P.add("levee_steps_e", levee_steps_e(False), walk=[[0, 0], [1, 0], [0, 1], [1, 1]], comment="2x2 overlay: plank steps up into the canopy (east), a storm lantern (Route 12)", lair="thundurus")
    P.add("levee_steps_e_log", levee_steps_e(True), comment="2x2 overlay: the same, a fallen trunk across it (sealed)", lair="thundurus")
    P.add("liana_gap_e", liana_gap("e", False), walk=[[1, 0], [1, 1]], comment="2x2 overlay: a trail into the canopy (east), lianas pulled aside (Route 13)", lair="zarude")
    P.add("liana_curtain_e", liana_gap("e", True), comment="2x2 overlay: a liana curtain over it (sealed)", lair="zarude")
    P.add("courir_gap_w", liana_gap("w", False, courir=True), walk=[[0, 0], [0, 1]], comment="2x2 overlay: a trail into the canopy (west), a Courir ribbon-stake (Route 13)", lair="ogerpon")
    P.add("liana_curtain_w", liana_gap("w", True), comment="2x2 overlay: a liana curtain over it (sealed)", lair="ogerpon")
    P.add("wind_gap_n", wind_gap_n(), walk=[[0, 0], [1, 0], [0, 1], [1, 1]], comment="2x2 overlay: a trail into the canopy (north), a windsock (Route 3)", lair="tornadus")
    P.add("sally_port_w", sally_port_w(False), walk=[[0, 0], [0, 1], [1, 0], [1, 1]], comment="2x2 overlay: the fort's sally port in the canopy (west) (Route 14)", lair="galar")
    P.add("sally_port_w_bricked", sally_port_w(True), comment="2x2 overlay: the sally port bricked up and grown over (sealed)", lair="galar")
    P.add("mill_door_ajar", mill_door_ajar(), walk=[[0, 1]], comment="1x2 overlay: the mill door ajar, firelight (Route 17, optional)", lair="moltres")
    return P


def main():
    P = build()
    P.pack()
    P.image.save(os.path.join(HERE, "entrances_b2.png"))
    pieces, mts, prefabs = {}, [], {}
    for n in P.order:
        cv = P.items[n]["cv"]
        px, py = P.pos[n]
        rows = []
        for j in range(cv.ch):
            row = []
            for i in range(cv.cw):
                mid = f"{px + i}_{py + j}"
                mts.append({"id": mid, "bottom": [px + i, py + j]})
                row.append({"overlay": f"le2:{mid}"})
            rows.append(row)
        walk = P.items[n]["walk"] or []
        pieces[n] = {"x": px, "y": py, "w": cv.cw, "h": cv.ch, "walk": walk, "lair": P.items[n]["lair"], "comment": P.items[n]["comment"]}
        prefabs[n] = {"_comment": P.items[n]["comment"], "rows": rows, "door": None, "passable": walk}
    dump(os.path.join(HERE, "entrances_b2.json"), {
        "_comment": "The batch-2 lairs' route entrances (make_entrances_b2.py): overlay pieces (magenta = clear), the compose source 'le2' "
                    "(overlay_only) to add to each route recipe that places them, prefabs, and the placements (proposed; the layout agent "
                    "builds them as spec 'gates' states, as batch 1's).",
        "png": "entrances_b2.png", "pieces": pieces,
        "source": {"name": "le2", "type": "image", "image": "tools/mapgen/tilesets/lairs/entrances_b2.png",
                   "transparent": [[255, 0, 255]], "overlay_only": True, "metatiles": mts},
        "prefabs": prefabs, "placements": PLACEMENTS})
    print(f"entrances_b2: {len(P.order)} pieces, sheet {P.image.size}")
    return P


if __name__ == "__main__":
    main()

"""Own art for Storm's Edge (the battered port, gym 2): drawn here in Python, magenta = transparent (overlays).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_storms_art.py
writes storms_*.png and storms_preview.png. Every piece is drawn on the 8 px grid with textures that repeat every
8 px (or mirrored left/right), so compose's tile dedupe (flips included) keeps the cost down; colours come from
the bridge, props and Ekat swamp sets the town already has.

    storms_planks.png   the harbour's dark plank boardwalk (quay, boards running north-south) and the long pier
                        (boards running east-west), with edge beams, a fascia and the posts standing in the water
    storms_stilt.png    the stilt row under a stilt house: platform beam, piles in the water, steps to the door
    storms_sub.png      the substation yard: lattice gantry with insulator strings, transformers with porcelain
                        bushings, a switch cabinet, wires over the fence, a danger sign for the fence (left and
                        mirrored right versions)
    storms_poles.png    the downed line by the Pokemon Center: a standing pole, a leaning pole with slack wires,
                        a snapped pole lying on the grass, wires on the ground, a dangling wire by the road
    storms_bridge.png   the drawbridge raised: a bascule leaf standing up (west, east) and the red-and-white
                        barrier across the deck at each end (drawn over the bridge.png deck)
    storms_misc.png     the Pokemon Center's generator
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)

# wood (the road bridge's own browns, so the boardwalk shares its palette)
B_L, B, B_D = (156, 118, 80), (140, 104, 70), (108, 78, 52)
SEAM, BEAM, POST, OUT = (84, 60, 42), (98, 70, 48), (78, 56, 40), (52, 40, 34)
# water (Ekat's flat water and its dark shade) and a ripple
WATER, WATER_D, RIPPLE = (96, 136, 136), (72, 112, 112), (136, 176, 176)
# steel, porcelain, warning colours
ST_L, ST, ST_D, ST_O = (184, 192, 192), (144, 152, 152), (104, 112, 116), (56, 60, 68)
CONC = (168, 168, 160)
PORC, PORC_L, PORC_D = (176, 96, 64), (208, 136, 96), (120, 64, 48)
YEL, BLK, RED, WHITE = (248, 208, 72), (40, 40, 44), (200, 56, 48), (240, 240, 232)
WIRE = (48, 48, 56)
GRASS_D = (72, 104, 64)  # a shadow on the grass (the Ekat bank's dark green)


class Sheet:
    def __init__(self, cw, ch):
        self.im = Image.new("RGB", (cw * 16, ch * 16), KEY)
        self.px = self.im.load()
        self.w, self.h = cw * 16, ch * 16

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = c

    def get(self, x, y):
        return self.px[x, y]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.put(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def sag(self, x0, y0, x1, y1, depth, c):
        """A wire hanging between two points (a parabola `depth` px below the chord at its middle)."""
        n = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        last = None
        for i in range(n + 1):
            t = i / n
            p = (round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + depth * 4 * t * (1 - t)))
            if p != last:
                self.put(*p, c)
                last = p

    def mirror_into(self, src_x0, src_y0, cw, ch, dst_x0, dst_y0):
        """Copy a block of cells mirrored left-right (the right-hand version of a left-hand piece)."""
        w, h = cw * 16, ch * 16
        block = [[self.px[src_x0 * 16 + i, src_y0 * 16 + j] for i in range(w)] for j in range(h)]
        for j in range(h):
            for i in range(w):
                self.px[dst_x0 * 16 + w - 1 - i, dst_y0 * 16 + j] = block[j][i]

    def save(self, name):
        self.im.save(os.path.join(HERE, name))
        return self.im


# ------------------------------------------------------------------ planks
def quay_board(x, y):
    """The quay's deck: boards running north-south, 4 px wide, light and dark boards alternating, a nail line
    every 8 px (no butt joints: they made a brick pattern); repeats every 8 px."""
    i = x % 8
    if i in (0, 4):
        return SEAM
    if y % 8 == 2 and i in (2, 6):
        return SEAM if i == 6 else B_D  # nails into the joist
    if i < 4:
        return B_L if i == 1 else B
    return B if i == 5 else B_D


def pier_board(x, y):
    """The pier's deck: boards running east-west (across the way you walk), the quay's boards turned."""
    return quay_board(y, x)


def planks():
    """Cells (x, y):
        quay  (0..2, 0..2): 3x3 block NW N NE / W C E / SW S SE; (0..2, 3): posts under SW, S, SE
        pier  (3..5, 0..1): W C E deck / SW S SE end; (3..5, 2): posts under the end
        (6, 0): quay deck meeting the pier (C with the pier's first board line below), (6, 1) posts beside a pier
    """
    s = Sheet(7, 4)
    # --- quay 3x3: every cell starts as deck, then the edges are cut in
    for cx in range(3):
        for cy in range(3):
            for j in range(16):
                for i in range(16):
                    s.put(cx * 16 + i, cy * 16 + j, quay_board(i, j))
    # north edge (row 0): a kerb beam along the deck's landward edge
    for cx in range(3):
        x0 = cx * 16
        s.rect(x0, 0, x0 + 15, 0, OUT)
        s.rect(x0, 1, x0 + 15, 2, BEAM)
        s.rect(x0, 1, x0 + 15, 1, B_L)
        s.rect(x0, 3, x0 + 15, 3, SEAM)
    # south edge (row 2): the deck's fascia, seen from the water side
    for cx in range(3):
        x0, y0 = cx * 16, 32
        s.rect(x0, y0 + 10, x0 + 15, y0 + 10, SEAM)
        s.rect(x0, y0 + 11, x0 + 15, y0 + 13, BEAM)
        s.rect(x0, y0 + 11, x0 + 15, y0 + 11, B_L)
        s.rect(x0, y0 + 14, x0 + 15, y0 + 14, POST)
        s.rect(x0, y0 + 15, x0 + 15, y0 + 15, OUT)
    # west and east ends: a side beam
    for cy in range(3):
        y0 = cy * 16
        top = 0
        bot = 15
        s.rect(0, y0 + top, 0, y0 + bot, OUT)
        s.rect(1, y0 + top + (1 if cy == 0 else 0), 2, y0 + bot, BEAM)
        s.rect(1, y0 + top + (1 if cy == 0 else 0), 1, y0 + bot, B_L)
        s.rect(3, y0 + top + (1 if cy == 0 else 0), 3, y0 + bot, SEAM)
        s.rect(47, y0 + top, 47, y0 + bot, OUT)
        s.rect(45, y0 + top + (1 if cy == 0 else 0), 46, y0 + bot, BEAM)
        s.rect(45, y0 + top + (1 if cy == 0 else 0), 45, y0 + bot, B_L)
        s.rect(44, y0 + top + (1 if cy == 0 else 0), 44, y0 + bot, SEAM)
    for x in (0, 47):  # the fascia wraps the corners
        s.rect(x, 42, x, 47, OUT)
    # posts in the water under the south edge (row 3): a pile every 8 px, a shadow under the deck, ripples
    def posts(x0, y0, first=0):
        for i in range(16):
            s.put(x0 + i, y0, WATER_D)
            if i % 2 == 0:
                s.put(x0 + i, y0 + 1, WATER_D)
        for px in range(x0 + first, x0 + 16, 8):
            s.rect(px + 2, y0, px + 4, y0 + 7, POST)
            s.rect(px + 2, y0, px + 2, y0 + 7, BEAM)
            s.rect(px + 4, y0, px + 4, y0 + 7, OUT)
            s.put(px + 1, y0 + 7, RIPPLE)
            s.put(px + 5, y0 + 7, RIPPLE)
            s.rect(px + 2, y0 + 8, px + 4, y0 + 8, RIPPLE)
            s.rect(px + 2, y0 + 9, px + 4, y0 + 10, WATER_D)
    for cx in range(3):
        posts(cx * 16, 48)
    # --- pier (cells 3..5): W C E deck rows 0, end row 1, posts row 2
    for cx in range(3, 6):
        for cy in range(2):
            for j in range(16):
                for i in range(16):
                    s.put(cx * 16 + i, cy * 16 + j, pier_board(i, j))
    for cy in range(2):  # side stringers
        y0 = cy * 16
        bot = 15 if cy == 0 else 9
        s.rect(48, y0, 48, y0 + bot, OUT)
        s.rect(49, y0, 50, y0 + bot, BEAM)
        s.rect(49, y0, 49, y0 + bot, B_L)
        s.rect(95, y0, 95, y0 + bot, OUT)
        s.rect(93, y0, 94, y0 + bot, BEAM)
        s.rect(93, y0, 93, y0 + bot, B_L)
    for cx in range(3, 6):  # the end's fascia
        x0, y0 = cx * 16, 16
        s.rect(x0, y0 + 10, x0 + 15, y0 + 10, SEAM)
        s.rect(x0, y0 + 11, x0 + 15, y0 + 13, BEAM)
        s.rect(x0, y0 + 11, x0 + 15, y0 + 11, B_L)
        s.rect(x0, y0 + 14, x0 + 15, y0 + 14, POST)
        s.rect(x0, y0 + 15, x0 + 15, y0 + 15, OUT)
    s.rect(48, 26, 48, 31, OUT)
    s.rect(95, 26, 95, 31, OUT)
    for cx in range(3, 6):
        posts(cx * 16, 32)
    # --- (6, 0): quay deck over the pier's head; (6, 1): quay posts beside the pier (shadow only)
    for j in range(16):
        for i in range(16):
            s.put(96 + i, j, quay_board(i, j))
    for i in range(16):
        s.put(96 + i, 16, WATER_D)
    s.save("storms_planks.png")
    return s.im


# ------------------------------------------------------------------ stilt row
def stilt():
    """3x1: the stilt row under a stilt house (Shady cabin art above it): the platform beam, four piles standing
    in the water with cross braces, and steps down from the door (middle cell, walkable) to the quay."""
    s = Sheet(3, 1)
    s.rect(0, 0, 47, 0, OUT)
    s.rect(0, 1, 47, 2, BEAM)
    s.rect(0, 1, 47, 1, B_L)
    s.rect(0, 3, 47, 3, OUT)
    for x in range(48):  # shadow on the water under the house
        s.put(x, 4, WATER_D)
        if x % 2 == 0:
            s.put(x, 5, WATER_D)
    # cross braces between the outer and inner piles of each side cell
    for x0 in (0, 32):
        s.line(x0 + 4, 5, x0 + 11, 11, SEAM)
        s.line(x0 + 11, 5, x0 + 4, 11, SEAM)
    for px in (1, 12, 32, 43):  # piles
        s.rect(px, 4, px + 2, 12, POST)
        s.put(px, 4, BEAM)
        s.rect(px, 5, px, 12, BEAM)
        s.rect(px + 2, 4, px + 2, 12, OUT)
        s.put(px - 1, 12, RIPPLE)
        s.put(px + 3, 12, RIPPLE)
        s.rect(px, 13, px + 2, 13, RIPPLE)
        s.rect(px, 14, px + 2, 15, WATER_D)
    # steps (middle cell, x 16..31): stringers and treads down to the quay
    s.rect(18, 4, 18, 15, OUT)
    s.rect(29, 4, 29, 15, OUT)
    s.rect(19, 4, 28, 15, B_D)
    for y in range(4, 16, 3):
        s.rect(19, y, 28, y, B_L)
        s.rect(19, y + 1, 28, y + 1, B)
    s.save("storms_stilt.png")
    return s.im


# ------------------------------------------------------------------ substation
def gantry(s, x0, y0):
    """1x3 lattice gantry at cell (x0, y0): crossarm with three insulator strings, wires leaving up out of the cell
    above (drawn separately), legs to a concrete footing."""
    X, Y = x0 * 16, y0 * 16
    # legs
    s.rect(X + 3, Y + 6, X + 3, Y + 44, ST_D)
    s.rect(X + 12, Y + 6, X + 12, Y + 44, ST_D)
    s.rect(X + 4, Y + 6, X + 4, Y + 44, ST)
    s.rect(X + 11, Y + 6, X + 11, Y + 44, ST)
    # lattice: zigzag bracing every 8 px
    for yy in range(Y + 8, Y + 44, 8):
        s.line(X + 5, yy, X + 10, yy + 4, ST_D)
        s.line(X + 10, yy + 4, X + 5, yy + 8, ST_D)
        s.rect(X + 5, yy, X + 10, yy, ST)
    # crossarm with a top chord
    s.rect(X + 0, Y + 3, X + 15, Y + 5, ST_O)
    s.rect(X + 1, Y + 3, X + 14, Y + 3, ST_L)
    s.rect(X + 1, Y + 4, X + 14, Y + 4, ST)
    # insulator strings (porcelain discs) hanging from the crossarm
    for ix in (X + 2, X + 7, X + 13):
        for k, yy in enumerate(range(Y + 6, Y + 12)):
            s.put(ix, yy, PORC_L if k % 2 == 0 else PORC_D)
            s.put(ix + 1, yy, PORC if k % 2 == 0 else PORC_D)
        s.put(ix, Y + 12, ST_O)
    # wires up from the crossarm to the cell top (the incoming line)
    for ix in (X + 2, X + 7, X + 13):
        s.rect(ix + 1, Y + 0, ix + 1, Y + 2, WIRE)
    # footing
    s.rect(X + 1, Y + 44, X + 14, Y + 47, CONC)
    s.rect(X + 1, Y + 47, X + 14, Y + 47, ST_D)
    s.rect(X + 1, Y + 44, X + 14, Y + 44, ST_L)


def transformer(s, x0, y0):
    """2x2 transformer at cell (x0, y0): tank with radiator fins, three porcelain bushings on the lid, a small
    conservator, the danger plate, on a concrete plinth."""
    X, Y = x0 * 16, y0 * 16
    # plinth
    s.rect(X + 1, Y + 27, X + 30, Y + 31, CONC)
    s.rect(X + 1, Y + 27, X + 30, Y + 27, ST_L)
    s.rect(X + 1, Y + 31, X + 30, Y + 31, ST_D)
    # radiator fins either side
    for fx in (X + 1, X + 26):
        for k in range(5):
            s.rect(fx + k, Y + 12, fx + k, Y + 26, ST_L if k % 2 == 0 else ST_D)
        s.rect(fx, Y + 11, fx + 4, Y + 11, ST_O)
    # tank
    s.rect(X + 6, Y + 9, X + 25, Y + 26, ST)
    s.rect(X + 6, Y + 9, X + 25, Y + 10, ST_L)
    s.rect(X + 6, Y + 9, X + 6, Y + 26, ST_O)
    s.rect(X + 25, Y + 9, X + 25, Y + 26, ST_O)
    s.rect(X + 7, Y + 25, X + 24, Y + 26, ST_D)
    for k in range(X + 9, X + 24, 4):  # tank ribs
        s.rect(k, Y + 12, k, Y + 24, ST_D)
    # danger plate
    s.rect(X + 13, Y + 15, X + 18, Y + 20, YEL)
    s.rect(X + 13, Y + 15, X + 18, Y + 15, BLK)
    s.line(X + 16, Y + 16, X + 15, Y + 18, BLK)
    s.line(X + 15, Y + 18, X + 17, Y + 18, BLK)
    s.line(X + 17, Y + 18, X + 16, Y + 20, BLK)
    # lid and bushings
    s.rect(X + 5, Y + 7, X + 26, Y + 8, ST_D)
    s.rect(X + 5, Y + 7, X + 26, Y + 7, ST_L)
    for bx in (X + 9, X + 15, X + 21):
        for k, yy in enumerate(range(Y + 0, Y + 7)):
            s.rect(bx, yy, bx + 1, yy, PORC_L if k % 2 == 0 else PORC)
            s.put(bx + 2, yy, PORC_D)
        s.rect(bx, Y + 0, bx + 2, Y + 0, ST_O)
    # conservator (a little drum on a leg)
    s.rect(X + 24, Y + 2, X + 29, Y + 5, ST)
    s.rect(X + 24, Y + 2, X + 29, Y + 2, ST_L)
    s.rect(X + 24, Y + 5, X + 29, Y + 5, ST_O)
    s.rect(X + 26, Y + 6, X + 27, Y + 6, ST_D)


def cabinet(s, x0, y0):
    """1x2 switch cabinet: grey steel box, louvres, the danger sign."""
    X, Y = x0 * 16, y0 * 16
    s.rect(X + 2, Y + 8, X + 13, Y + 29, ST)
    s.rect(X + 2, Y + 8, X + 13, Y + 9, ST_L)
    s.rect(X + 2, Y + 8, X + 2, Y + 29, ST_O)
    s.rect(X + 13, Y + 8, X + 13, Y + 29, ST_O)
    s.rect(X + 2, Y + 29, X + 13, Y + 29, ST_O)
    s.rect(X + 1, Y + 6, X + 14, Y + 7, ST_D)  # roof lip
    s.rect(X + 7, Y + 10, X + 8, Y + 28, ST_D)  # door split
    for yy in range(Y + 11, Y + 16, 2):  # louvres
        s.rect(X + 4, yy, X + 6, yy, ST_D)
        s.rect(X + 9, yy, X + 11, yy, ST_D)
    s.rect(X + 9, Y + 19, X + 12, Y + 23, YEL)  # danger sign
    s.put(X + 11, Y + 20, BLK)
    s.put(X + 10, Y + 21, BLK)
    s.put(X + 11, Y + 22, BLK)
    s.rect(X + 2, Y + 30, X + 13, Y + 31, CONC)


def substation():
    """Left-hand versions at cells 0..3, mirrored right-hand versions at cells 4..7:
        (0, 0..2) gantry 1x3     (1..2, 1..2) transformer 2x2    (3, 0..1) cabinet 1x2
        (0, 3)   wires over the top fence (three wires leaving the gantry north)
        (3, 2)   danger sign on the fence ("johto" fence piece underneath shows through)
    """
    s = Sheet(8, 4)
    gantry(s, 0, 0)
    transformer(s, 1, 1)
    cabinet(s, 3, 0)
    for ix in (2, 7, 13):  # three wires running north over the fence row
        s.rect(ix + 1, 48, ix + 1, 63, WIRE)
    # danger sign for a fence panel: yellow plate with a black bolt
    X, Y = 48, 32
    s.rect(X + 4, Y + 4, X + 11, Y + 11, BLK)
    s.rect(X + 5, Y + 5, X + 10, Y + 10, YEL)
    s.line(X + 8, Y + 5, X + 6, Y + 8, BLK)
    s.line(X + 6, Y + 8, X + 9, Y + 8, BLK)
    s.line(X + 9, Y + 8, X + 7, Y + 10, BLK)
    s.mirror_into(0, 0, 4, 4, 4, 0)
    s.save("storms_sub.png")
    return s.im


# ------------------------------------------------------------------ the downed line
def pole(s, X, Y, lean=0, arm=True):
    """A wooden utility pole whose foot is at (X, Y) (pixel), 40 px tall; lean: px the top leans to the right."""
    top = Y - 40
    for yy in range(top, Y + 1):
        t = (Y - yy) / 40
        x = X + round(lean * t)
        s.rect(x - 1, yy, x + 1, yy, POST)
        s.put(x - 1, yy, BEAM)
        s.put(x + 1, yy, OUT)
    tx = X + lean
    if arm:  # crossarm, tilted with the lean, and two glass insulators
        d = 1 if lean > 3 else 0
        s.line(tx - 7, top + 6 - d * 2, tx + 7, top + 6 + d * 2, OUT)
        s.line(tx - 7, top + 5 - d * 2, tx + 7, top + 5 + d * 2, BEAM)
        for ix, iy in ((tx - 6, top + 3 - d * 2), (tx + 6, top + 3 + d * 2)):
            s.rect(ix - 1, iy, ix, iy + 1, (200, 224, 216))
            s.put(ix, iy + 1, (120, 160, 152))
    s.rect(X - 2, Y + 1, X + 2, Y + 1, GRASS_D)  # where it stands


def downed_line():
    """The broken line by the Pokemon Center, drawn as one 3x12 scene (cells x 0..2 = map x 19..21, y 0..11): a pole
    leaning hard at the top with the line coming in from the north, a pole snapped off in the middle with its top
    lying across the grass and the wires draped down to it, and a standing pole by the road with its wires hanging
    loose. Cells left empty are not placed."""
    s = Sheet(3, 12)
    ins = (200, 224, 216)
    # pole A, foot at y 40, leaning east
    pole(s, 22, 40, lean=6)
    for ix, iy in ((28 - 6, 1), (28 + 6, 3)):        # the line coming in from the north
        s.line(ix + 1, 0, ix, iy, WIRE)
    # pole B, snapped: the stump (foot y 104) and its top lying across the grass to the west
    X, Y = 24, 104
    s.rect(X - 1, Y - 8, X + 1, Y, POST)
    s.rect(X - 1, Y - 8, X - 1, Y, BEAM)
    s.rect(X + 1, Y - 8, X + 1, Y, OUT)
    s.put(X - 1, Y - 9, B_L)
    s.put(X + 1, Y - 10, B_L)
    s.put(X, Y - 11, B_L)
    s.rect(X - 2, Y + 1, X + 2, Y + 1, GRASS_D)
    # the fallen top: from the stump down to the south-west, its crossarm flat on the grass
    for k in range(3):
        s.line(X - 3, Y - 6 + k, X - 20, Y + 3 + k, (BEAM, POST, OUT)[k])
    s.line(X - 4, Y - 2, X - 20, Y + 6, GRASS_D)
    s.line(X - 23, Y - 4, X - 18, Y + 10, OUT)
    s.line(X - 22, Y - 4, X - 17, Y + 10, BEAM)
    s.rect(X - 24, Y - 5, X - 23, Y - 4, ins)
    s.rect(X - 18, Y + 10, X - 17, Y + 11, ins)
    # A's wires, slack: draped all the way down to the ground round the fallen top
    s.sag(28 - 6, 3, X - 22, Y - 4, 0, WIRE)
    s.sag(28 + 6, 5, X + 9, Y - 2, 0, WIRE)
    s.sag(X + 9, Y - 2, X - 17, Y + 11, 6, WIRE)
    # pole C by the road (foot y 184), standing, its wires hanging loose to the grass
    pole(s, 24, 184)
    s.sag(24 - 6, 184 - 40 + 3, 9, 176, 4, WIRE)
    s.sag(24 + 6, 184 - 40 + 3, 39, 178, 4, WIRE)
    s.save("storms_poles.png")
    return s.im


# ------------------------------------------------------------------ drawbridge raised
def bridge_raised():
    """Cells: (0, 0..3) the west bascule leaf standing up over its pit (it replaces the bridge's four rows in the
    leaf's column: rail, deck, deck, rail), (1, 0..3) the east leaf (mirrored); (2, 0..1) the west barrier
    across the deck (the bridge.png deck under it), (3, 0..1) the east barrier."""
    s = Sheet(4, 4)
    bridge = Image.open(os.path.join(HERE, "bridge.png")).convert("RGB")
    # --- west leaf in cell column 0: the deck stood on end over its pit, seen from the river mouth
    X = 0
    s.rect(X + 14, 2, X + 15, 55, WATER_D)          # its shadow on the water, toward the gap
    s.rect(X + 1, 1, X + 13, 57, OUT)
    for yy in range(2, 57):                         # the deck's boards, end on (the bridge's own browns)
        for xx in range(X + 4, X + 12):
            k = (xx - X - 4) % 4
            s.put(xx, yy, SEAM if k == 0 else B_L if k == 1 else B)
        s.put(X + 2, yy, ST_D)                      # steel side girders
        s.put(X + 3, yy, ST)
        s.put(X + 12, yy, ST_D)
    for yy in range(4, 56, 6):                      # rivets on the girder
        s.put(X + 3, yy, ST_L)
    for ry in (5, 47):                              # the handrails, now standing across it
        s.rect(X + 2, ry, X + 13, ry + 1, BEAM)
        s.rect(X + 2, ry, X + 13, ry, B_L)
        s.rect(X + 2, ry + 2, X + 13, ry + 2, OUT)
        for bx in (X + 5, X + 9):
            s.rect(bx, ry + 3, bx, ry + 6, POST)
    s.rect(X + 1, 0, X + 13, 1, ST_O)               # the tip, a red lamp on it
    s.rect(X + 6, 0, X + 8, 0, RED)
    s.rect(X + 0, 56, X + 14, 63, ST_O)             # pivot and counterweight pit
    s.rect(X + 1, 57, X + 13, 62, ST_D)
    s.rect(X + 4, 58, X + 9, 61, ST)
    s.rect(X + 5, 59, X + 8, 60, ST_L)
    s.mirror_into(0, 0, 1, 4, 1, 0)
    # --- barriers over the deck (cells 2 and 3, rows 0..1): the bridge's middle deck cells, then the boom
    for cx in (2, 3):
        for j in range(32):
            for i in range(16):
                s.put(cx * 16 + i, j, bridge.getpixel((16 + i, 16 + j)))
    for cx, bx in ((2, 10), (3, 5)):  # the boom along the deck's width, near the leaf (east of the west barrier)
        X = cx * 16 + bx
        for j in range(0, 32):
            c = RED if (j // 4) % 2 == 0 else WHITE
            s.rect(X - 1, j, X + 1, j, c)
            s.put(X + 2 if cx == 2 else X - 2, j, OUT)  # its shadow on the deck
        # the post at the north end, a red lamp on top
        s.rect(X - 2, 0, X + 2, 4, BLK)
        s.rect(X - 1, 0, X + 1, 1, RED)
    s.save("storms_bridge.png")
    return s.im


# ------------------------------------------------------------------ misc
def misc():
    """(0..1, 0) the Pokemon Center's generator: a diesel set on skids with an exhaust and a cable;
    (2, 0) the gym's emblem for the hall's brick front: a stone roundel with a yellow bolt."""
    s = Sheet(3, 1)
    X = 32  # the emblem: a disc of stone, a dark ring, the bolt
    for j in range(16):
        for i in range(16):
            d = ((i - 7.5) ** 2 + (j - 7.5) ** 2) ** 0.5
            if d <= 7.2:
                s.put(X + i, j, OUT if d > 6.2 else (176, 168, 136) if d > 5.2 else (64, 56, 56))
    for a, b in (((9, 2), (5, 8)), ((5, 8), (10, 8)), ((10, 8), (6, 13))):
        s.line(X + a[0], a[1], X + b[0], b[1], YEL)
        s.line(X + a[0] + 1, a[1], X + b[0] + 1, b[1], YEL)
    s.rect(1, 13, 30, 15, POST)            # skids
    s.rect(1, 13, 30, 13, BEAM)
    s.rect(2, 4, 26, 12, (176, 72, 56))    # housing (generator red)
    s.rect(2, 4, 26, 5, (208, 104, 80))
    s.rect(2, 4, 2, 12, OUT)
    s.rect(26, 4, 26, 12, OUT)
    s.rect(2, 12, 26, 12, OUT)
    for x in range(5, 16, 2):              # louvres
        s.rect(x, 7, x, 10, (120, 48, 40))
    s.rect(18, 7, 23, 10, ST_D)            # panel
    s.put(19, 8, YEL)
    s.put(21, 8, (96, 200, 96))
    s.rect(23, 0, 24, 4, ST_O)             # exhaust
    s.rect(23, 0, 24, 0, ST)
    s.rect(27, 10, 31, 11, WIRE)           # cable to the Center
    s.save("storms_misc.png")
    return s.im


def main():
    ims = [("planks", planks()), ("stilt", stilt()), ("substation", substation()), ("downed line", downed_line()),
           ("bridge raised", bridge_raised()), ("generator", misc())]
    W = sum(im.width for _, im in ims) + 8 * len(ims)
    H = max(im.height for _, im in ims)
    prev = Image.new("RGB", (W, H), (255, 255, 255))
    x = 0
    for _, im in ims:
        prev.paste(im, (x, 0))
        x += im.width + 8
    prev.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(HERE, "storms_preview.png"))
    print("storms art:", ", ".join(f"{n} {im.size}" for n, im in ims))


if __name__ == "__main__":
    main()

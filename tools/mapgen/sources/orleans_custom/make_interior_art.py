"""Own art for interiors: Rootkin hut interiors and Magnolia's glass conservatory (walls and dais; the hedge maze
itself uses the HnS Celadon gym tiles).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_interior_art.py
writes rootkin_interior.png and conservatory.png (8 cells wide, 16x16 cells); magenta = transparent.
Floors and walls are full cells; objects are drawn on transparent cells and placed over a floor cell.
The CELLS tables below name every cell (used by the recipes).
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
CLEAR = (0, 0, 0, 0)
OUTL = (52, 42, 34)
# Rootkin palette (shared with the exteriors)
TH_L, TH, TH_D, TH_DD = (214, 192, 124), (184, 158, 92), (146, 120, 64), (104, 84, 46)
FL_L, FL, FL_D = (196, 166, 124), (172, 142, 104), (130, 104, 76)
WD, WD_D = (124, 104, 82), (92, 76, 60)
MAT_L, MAT, MAT_D = (204, 160, 100), (176, 128, 74), (128, 90, 52)
TEAL, OCHRE, RED = (72, 140, 136), (204, 152, 64), (186, 66, 56)
STONE_L, STONE, STONE_D = (176, 172, 164), (138, 134, 128), (96, 92, 88)
FLAME, FLAME_L, EMBER = (232, 120, 48), (252, 208, 96), (160, 56, 32)
HERB, HERB_D = (110, 150, 80), (76, 110, 58)
BLUE, BLUE_L = (64, 104, 184), (150, 190, 240)


def cell():
    return Image.new("RGBA", (16, 16), CLEAR)


# ------------------------------------------------------------------ Rootkin
def floor(alt=False):
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=FL)
    for i, y in enumerate(range(0, 16, 4)):
        d.line([(0, y + 3), (15, y + 3)], fill=FL_D)
        d.line([(0, y), (15, y)], fill=FL_L)
        seam = (5 + i * 7 + (4 if alt else 0)) % 16
        d.line([(seam, y), (seam, y + 2)], fill=FL_D)
    if alt:
        d.point((11, 6), fill=FL_D)
        d.point((3, 13), fill=FL_D)
    return c


def thatch_top():
    c = cell()
    d = ImageDraw.Draw(c)
    for y in range(16):
        band = y % 5
        d.line([(0, y), (15, y)], fill=TH_L if band == 0 else TH if band < 3 else TH_D)
        for x in range(y % 3, 16, 3):
            if band in (1, 3):
                d.point((x, y), fill=TH_DD if band == 3 else TH_D)
    return c


def thatch_bottom():
    """Woven reed wall panel with a dark skirting."""
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=TH)
    for x in range(0, 16, 2):
        d.line([(x, 0), (x, 12)], fill=TH_D)
    for y in range(1, 12, 3):
        for x in range((y // 3) % 2 * 2, 16, 4):
            d.line([(x, y), (x + 1, y)], fill=TH_L)
    d.rectangle([0, 13, 15, 15], fill=WD_D)
    d.line([(0, 13), (15, 13)], fill=OUTL)
    return c


def side_wall():
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=WD_D)
    for x in (3, 9, 13):
        d.line([(x, 0), (x, 15)], fill=WD)
    return c


def mat(kind):
    """Woven mat: 'single' (complete), or 'L'/'M'/'R' pieces of a long mat."""
    c = cell()
    d = ImageDraw.Draw(c)
    x0 = 1 if kind in ("single", "L") else 0
    x1 = 14 if kind in ("single", "R") else 15
    d.rectangle([x0, 2, x1, 13], fill=MAT)
    for y in range(3, 13):
        for x in range(x0 + ((x0 + y) % 2), x1 + 1, 2):
            d.point((x, y), fill=MAT_L if (x + y) % 4 else MAT_D)
    d.line([(x0, 2), (x1, 2)], fill=MAT_D)
    d.line([(x0, 13), (x1, 13)], fill=MAT_D)
    if kind in ("single", "L"):
        for y in range(3, 13, 2):
            d.point((0, y), fill=MAT_D)
    if kind in ("single", "R"):
        for y in range(3, 13, 2):
            d.point((15, y), fill=MAT_D)
    d.line([(x0 + 2 if kind in ("single", "L") else 0, 7), (x1 - 2 if kind in ("single", "R") else 15, 7)], fill=TEAL)  # a woven stripe
    return c


def hearth(q, kettle=False):
    """2x2 fire pit: ring of stones, embers, a small flame (kettle: a kettle hung over it on a tripod). q = quadrant 0..3."""
    big = Image.new("RGBA", (32, 32), CLEAR)
    d = ImageDraw.Draw(big)
    d.ellipse([2, 4, 29, 29], fill=STONE_D)
    for i in range(14):
        import math
        a = i / 14 * 2 * math.pi
        x, y = 15.5 + 12 * math.cos(a), 16.5 + 11 * math.sin(a)
        d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=STONE if i % 2 else STONE_L, outline=OUTL)
    d.ellipse([8, 10, 23, 23], fill=EMBER)
    d.ellipse([11, 12, 20, 21], fill=FLAME)
    d.polygon([(13, 18), (15, 8), (16, 13), (18, 9), (19, 18)], fill=FLAME_L)
    if kettle:
        for x0, x1 in ((6, 15), (25, 16)):
            d.line([(x0, 26), (x1, 1)], fill=WD_D, width=2)
        d.line([(15, 2), (15, 8)], fill=OUTL)
        d.ellipse([9, 8, 22, 19], fill=(70, 66, 64), outline=OUTL)
        d.line([(11, 10), (14, 9)], fill=STONE)
        d.line([(21, 12), (25, 10)], fill=OUTL, width=2)  # spout
    return big.crop(((q % 2) * 16, (q // 2) * 16, (q % 2) * 16 + 16, (q // 2) * 16 + 16))


def basket():
    c = cell()
    d = ImageDraw.Draw(c)
    d.ellipse([2, 4, 13, 14], fill=MAT, outline=OUTL)
    for y in range(6, 13, 2):
        d.line([(4, y), (11, y)], fill=MAT_D)
    d.ellipse([3, 3, 12, 7], fill=MAT_L, outline=OUTL)
    return c


def jar():
    c = cell()
    d = ImageDraw.Draw(c)
    d.ellipse([3, 4, 12, 15], fill=(150, 92, 60), outline=OUTL)
    d.rectangle([5, 2, 10, 5], fill=(150, 92, 60), outline=OUTL)
    d.line([(4, 9), (11, 9)], fill=OCHRE)
    return c


def herbs(right):
    """Herb bundles hanging on the woven wall (a 2-cell rack), drawn over thatch_bottom."""
    c = thatch_bottom()
    d = ImageDraw.Draw(c)
    d.line([(0, 2), (15, 2)], fill=WD_D)
    for x in ((3, 9) if not right else (2, 8, 13)):
        d.line([(x, 2), (x, 4)], fill=OUTL)
        d.polygon([(x - 2, 4), (x + 2, 4), (x + 1, 11), (x - 1, 11)], fill=HERB if x % 2 else HERB_D)
    return c


def paddles(right):
    c = thatch_bottom()
    d = ImageDraw.Draw(c)
    for x in (4, 12):  # two per cell, evenly spaced along the whole rack
        d.line([(x, 0), (x, 8)], fill=WD_D)
        d.ellipse([x - 2, 7, x + 2, 12], fill=WD, outline=OUTL)
    return c


def verse(n, q):
    """Painted verse, 2x2 over both rows of the reed wall: a tanned hide hung from a lashed rod, each painted
    with its own scene (1 the water, 2 Rayquaza, 3 the storm, 4 the great tree). q = quadrant 0..3."""
    import math
    big = Image.new("RGBA", (32, 32), CLEAR)
    for i in range(2):
        big.paste(thatch_top(), (i * 16, 0))
        big.paste(thatch_bottom(), (i * 16, 16))
    d = ImageDraw.Draw(big)
    d.polygon([(3, 4), (28, 4), (29, 12), (28, 24), (26, 27), (21, 25), (16, 27), (11, 25), (6, 27), (3, 24), (2, 12)],
              fill=MAT_L, outline=OUTL)
    d.line([(1, 3), (30, 3)], fill=WD_D, width=2)  # the rod
    for x in (5, 26):
        d.line([(x, 0), (x, 4)], fill=OUTL)
    if n == 1:  # the water: rolling waves under the sun
        d.ellipse([12, 8, 19, 14], fill=FLAME_L, outline=OUTL)
        for a_ in range(0, 360, 45):
            r = math.radians(a_)
            d.point((15.5 + 6 * math.cos(r), 11 + 5 * math.sin(r)), fill=RED)
        for y, c in ((17, BLUE), (20, TEAL), (23, BLUE)):
            for x in range(6, 25, 4):  # even ripples
                d.line([(x, y), (x + 1, y - 1), (x + 2, y - 1), (x + 3, y)], fill=c)
    elif n == 2:  # Rayquaza: a painted caricature of its head, in profile
        GREEN = (56, 168, 88)
        for fin in ([(5, 7), (13, 9), (10, 13)], [(9, 6), (18, 9), (14, 11)]):  # swept-back head fins
            d.polygon(fin, fill=GREEN, outline=OUTL)
        d.point((6, 7), fill=FLAME_L)
        d.point((10, 6), fill=FLAME_L)
        d.polygon([(8, 13), (12, 9), (19, 10), (25, 14), (25, 17), (20, 19), (14, 22), (9, 21)], fill=GREEN, outline=OUTL)
        d.line([(13, 20), (20, 18), (24, 17)], fill=HERB_D)  # the jaw
        d.line([(18, 16), (24, 16)], fill=RED)  # mouth
        d.line([(11, 11), (19, 11), (24, 14)], fill=FLAME_L)  # the yellow ring markings
        d.ellipse([9, 15, 13, 19], outline=FLAME_L)
        d.rectangle([16, 12, 17, 13], fill=FLAME_L)  # eye
        d.point((17, 12), fill=OUTL)
    elif n == 3:  # the storm: a cloud, rain and a bolt over the water
        d.ellipse([6, 8, 17, 14], fill=STONE, outline=OUTL)
        d.ellipse([12, 7, 25, 14], fill=STONE, outline=OUTL)
        for x in (9, 12, 22, 25):
            d.line([(x, 16), (x - 2, 21)], fill=BLUE)
        d.polygon([(16, 13), (12, 19), (15, 19), (13, 24), (19, 17), (16, 17), (19, 13)], fill=FLAME_L, outline=OUTL)  # the bolt, centred
    else:  # the great tree
        d.rectangle([14, 13, 17, 21], fill=WD_D, outline=OUTL)
        d.ellipse([6, 5, 25, 15], fill=TEAL, outline=OUTL)
        for p_ in ((10, 9), (15, 7), (20, 10), (13, 12), (18, 12)):
            d.point(p_, fill=RED)
        for x0, x1 in ((14, 10), (17, 21), (15, 13), (16, 18)):
            d.line([(x0, 21), (x1, 23)], fill=WD_D)
    return big.crop(((q % 2) * 16, (q // 2) * 16, (q % 2) * 16 + 16, (q // 2) * 16 + 16))


def bedroll(right):
    c = cell()
    d = ImageDraw.Draw(c)
    if not right:
        d.rectangle([1, 3, 15, 13], fill=MAT, outline=OUTL)
        d.rectangle([2, 4, 6, 12], fill=(220, 210, 180), outline=OUTL)  # pillow
    else:
        d.rectangle([0, 3, 14, 13], fill=TEAL, outline=OUTL)              # blanket
        for x in range(2, 14, 3):
            d.line([(x, 4), (x, 12)], fill=(56, 112, 108))
    return c


def bench(right):
    c = cell()
    d = ImageDraw.Draw(c)
    x0, x1 = (1, 15) if not right else (0, 14)
    d.rectangle([x0, 4, x1, 11], fill=WD, outline=OUTL)
    d.line([(x0 + 1, 6), (x1 - 1, 6)], fill=WD_D)
    if not right:
        d.line([(4, 8), (9, 8)], fill=STONE_L)  # a knife
    else:
        d.polygon([(4, 7), (10, 7), (8, 10)], fill=(206, 170, 110))  # a half-carved charm
        for x in (2, 12):
            d.point((x, 13), fill=(214, 190, 140))  # shavings
    return c


def canoe(part):
    c = cell()
    d = ImageDraw.Draw(c)
    if part == 0:
        d.polygon([(8, 1), (13, 10), (13, 15), (3, 15), (3, 10)], fill=WD, outline=OUTL)
        d.polygon([(8, 4), (11, 11), (11, 15), (5, 15), (5, 11)], fill=WD_D)
    elif part == 1:
        d.rectangle([3, 0, 13, 15], fill=WD, outline=None)
        d.line([(3, 0), (3, 15)], fill=OUTL)
        d.line([(13, 0), (13, 15)], fill=OUTL)
        d.rectangle([5, 0, 11, 15], fill=WD_D)
        d.line([(5, 8), (11, 8)], fill=WD)  # thwart
    else:
        d.polygon([(3, 0), (13, 0), (13, 5), (8, 14), (3, 5)], fill=WD, outline=OUTL)
        d.polygon([(5, 0), (11, 0), (11, 4), (8, 11), (5, 4)], fill=WD_D)
    return c


def pedestal(orb, part):
    c = cell()
    d = ImageDraw.Draw(c)
    col, lt = ((BLUE, BLUE_L) if orb == "blue" else (RED, FLAME_L))
    if part == 0:
        d.ellipse([4, 4, 11, 11], fill=col, outline=OUTL)
        d.point((6, 6), fill=lt)
        d.point((7, 6), fill=lt)
        d.rectangle([3, 11, 12, 15], fill=STONE_L, outline=OUTL)
    else:
        d.rectangle([4, 0, 11, 12], fill=STONE, outline=OUTL)
        d.rectangle([2, 12, 13, 15], fill=STONE_D, outline=OUTL)
    return c


def doormat():
    c = floor()
    d = ImageDraw.Draw(c)
    d.rectangle([2, 4, 13, 15], fill=MAT_D)
    for y in range(5, 15, 2):
        d.line([(3, y), (12, y)], fill=MAT)
    return c


def firepit(q):
    """3x3 fire pit for the song house: a wide ring of stones round the embers. q = cell 0..8 (row-major)."""
    import math
    big = Image.new("RGBA", (48, 48), CLEAR)
    d = ImageDraw.Draw(big)
    d.ellipse([3, 5, 44, 45], fill=STONE_D)
    for i in range(20):
        a = i / 20 * 2 * math.pi
        x, y = 23.5 + 18 * math.cos(a), 25 + 17 * math.sin(a)
        d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=STONE if i % 2 else STONE_L, outline=OUTL)
    d.ellipse([11, 13, 36, 37], fill=EMBER)
    for x0, y0, x1, y1 in ((14, 22, 33, 27), (16, 28, 31, 33)):  # logs
        d.rectangle([x0, y0, x1, y1], fill=WD_D, outline=OUTL)
    d.ellipse([15, 14, 32, 30], fill=FLAME)
    d.polygon([(17, 27), (20, 11), (22, 19), (24, 7), (26, 18), (28, 12), (30, 27)], fill=FLAME_L)
    return big.crop(((q % 3) * 16, (q // 3) * 16, (q % 3) * 16 + 16, (q // 3) * 16 + 16))


def chair(part):
    """Tupelo's high-backed carved chair, 1x2 on a transparent cell: part 0 = the backrest and crest,
    1 = the woven seat and legs."""
    big = Image.new("RGBA", (16, 32), CLEAR)
    d = ImageDraw.Draw(big)
    for x in (2, 12):  # posts
        d.rectangle([x, 3, x + 1, 31], fill=WD_D, outline=OUTL)
    d.rectangle([4, 6, 11, 19], fill=MAT)  # woven back panel
    for y in range(7, 19, 2):
        d.line([(4, y), (11, y)], fill=MAT_L)
    d.line([(7, 6), (7, 19)], fill=TEAL)
    d.line([(8, 6), (8, 19)], fill=TEAL)
    d.polygon([(1, 6), (3, 3), (12, 3), (14, 6)], fill=OCHRE, outline=OUTL)  # carved crest
    d.ellipse([4, 0, 11, 7], fill=(56, 168, 88), outline=OUTL)  # the green orb (Rayquaza), between the blue and red ones
    d.point((6, 2), fill=BLUE_L)
    d.point((7, 2), fill=BLUE_L)
    d.rectangle([1, 20, 14, 24], fill=TEAL, outline=OUTL)  # cushion
    d.line([(2, 22), (13, 22)], fill=OCHRE)
    d.rectangle([2, 25, 13, 26], fill=WD, outline=OUTL)  # front rail
    return big.crop((0, part * 16, 16, part * 16 + 16))


def stool():
    """A log-stump stool (transparent cell)."""
    c = cell()
    d = ImageDraw.Draw(c)
    d.ellipse([0, 11, 15, 15], fill=FL_D)  # shadow on the floor
    d.rectangle([1, 6, 14, 13], fill=WD_D, outline=OUTL)
    for x in (4, 7, 10, 13):
        d.line([(x, 8), (x, 13)], fill=WD)
    d.ellipse([1, 10, 14, 14], fill=WD_D)
    d.arc([1, 10, 14, 14], 0, 180, fill=OUTL)
    d.ellipse([1, 2, 14, 10], fill=FL_L, outline=OUTL)
    d.ellipse([4, 4, 11, 8], outline=FL_D)
    d.point((7, 6), fill=FL_D)
    d.point((8, 6), fill=FL_D)
    return c

def wall_basket(right):
    """Woven baskets hung on pegs on the reed wall (drawn over thatch_bottom)."""
    c = thatch_bottom()
    d = ImageDraw.Draw(c)
    x0, x1, y1 = (3, 12, 11) if not right else (4, 11, 10)
    d.point(((x0 + x1) // 2, 1), fill=OUTL)  # the peg
    d.line([((x0 + x1) // 2, 1), (x0 + 1, 4)], fill=WD_D)
    d.line([((x0 + x1) // 2, 1), (x1 - 1, 4)], fill=WD_D)
    d.pieslice([x0, y1 - 14, x1, y1], 0, 180, fill=MAT, outline=OUTL)
    for y in range(y1 - 5, y1, 2):
        d.line([(x0 + 2, y), (x1 - 2, y)], fill=MAT_D)
    d.line([(x0, y1 - 7), (x1, y1 - 7)], fill=MAT_L)
    return c


def trade_counter(part, goods):
    """The trader's counter (transparent cell over the floor): part L/M/R; goods = bare, balls (Net Balls) or potions."""
    c = cell()
    d = ImageDraw.Draw(c)
    x0 = 1 if part == "L" else 0
    x1 = 14 if part == "R" else 15
    d.rectangle([x0, 6, x1, 9], fill=MAT_L)  # the top
    d.line([(x0, 6), (x1, 6)], fill=OUTL)
    d.rectangle([x0, 10, x1, 15], fill=WD)  # the front, planked
    d.line([(x0, 10), (x1, 10)], fill=WD_D)
    d.line([(x0, 13), (x1, 13)], fill=WD_D)
    d.line([(x0, 15), (x1, 15)], fill=OUTL)
    for x in (4, 11):
        d.line([(x, 11), (x, 14)], fill=WD_D)
    for x, on in ((x0, part == "L"), (x1, part == "R")):
        if on:
            d.line([(x, 6), (x, 15)], fill=OUTL)
    if goods == "balls":  # Net Balls
        for cx in (5, 10):
            d.ellipse([cx - 3, 1, cx + 3, 7], fill=STONE_L, outline=OUTL)
            d.pieslice([cx - 3, 1, cx + 3, 7], 180, 360, fill=TEAL, outline=OUTL)
            d.point((cx, 4), fill=OUTL)
    elif goods == "potions":  # remedy jars
        for cx in (5, 10):
            d.rectangle([cx - 2, 1, cx + 2, 7], fill=BLUE, outline=OUTL)
            d.rectangle([cx - 1, 0, cx + 1, 1], fill=WD_D)
    return c

def log_pile(q):
    """2x2 stack of cypress logs, end grain towards us. q = quadrant 0..3."""
    big = Image.new("RGBA", (32, 32), CLEAR)
    d = ImageDraw.Draw(big)
    d.ellipse([1, 26, 30, 31], fill=FL_D)  # shadow
    for cx, cy in ((7, 24), (16, 24), (25, 24), (11, 16), (20, 16), (16, 8)):
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=WD_D, outline=OUTL)
        d.ellipse([cx - 4, cy - 4, cx + 3, cy + 3], fill=FL_L)
        d.ellipse([cx - 2, cy - 2, cx + 1, cy + 1], outline=FL_D)
    return big.crop(((q % 2) * 16, (q // 2) * 16, (q % 2) * 16 + 16, (q // 2) * 16 + 16))


def workbench(part, item):
    """The carver's workbench (transparent cell over the floor): part L/M/R, with tools and work on top."""
    c = cell()
    d = ImageDraw.Draw(c)
    x0 = 1 if part == "L" else 0
    x1 = 14 if part == "R" else 15
    d.rectangle([x0, 5, x1, 10], fill=FL_L)  # thick plank top
    d.line([(x0, 5), (x1, 5)], fill=OUTL)
    d.line([(x0, 8), (x1, 8)], fill=FL)
    d.rectangle([x0, 11, x1, 12], fill=WD_D)  # apron
    d.line([(x0, 13), (x1, 13)], fill=OUTL)
    for x, on in ((x0, part == "L"), (x1, part == "R")):
        if on:
            d.line([(x, 5), (x, 13)], fill=OUTL)
            lx = x + 1 if part == "L" else x - 3
            d.rectangle([lx, 13, lx + 2, 15], fill=WD_D, outline=OUTL)  # leg
    if item == "knife":  # a carving knife and a gouge
        d.line([(3, 7), (8, 7)], fill=STONE_L)
        d.rectangle([9, 6, 12, 8], fill=WD_D, outline=OUTL)
        d.line([(4, 10), (9, 10)], fill=STONE)
    elif item == "charm":  # the half-carved cypress charm
        d.polygon([(4, 0), (11, 0), (8, 8)], fill=MAT_L, outline=OUTL)
        d.line([(6, 2), (9, 2)], fill=TEAL)
        d.point((7, 4), fill=TEAL)
    elif item == "mallet":
        d.rectangle([3, 3, 8, 7], fill=WD, outline=OUTL)
        d.line([(9, 5), (13, 8)], fill=WD_D, width=2)
    return c

def fishing_net(part):
    """A half-mended fishing net hung on the reed wall (3 cells: L, M, R), floats along the top cord and a torn
    patch on the right (drawn over thatch_bottom)."""
    big = Image.new("RGBA", (48, 16), CLEAR)
    for i in range(3):
        big.paste(thatch_bottom(), (i * 16, 0))
    d = ImageDraw.Draw(big)
    d.line([(4, 2), (44, 2)], fill=OUTL)  # the top cord
    for x in range(4, 44, 5):  # diamond mesh
        d.line([(x, 2), (x + 5, 11)], fill=WD_D)
        d.line([(x + 5, 2), (x, 11)], fill=WD_D)
    d.line([(4, 11), (44, 11)], fill=WD_D)
    d.rectangle([35, 5, 40, 10], fill=TH)  # the torn patch, half mended
    d.line([(35, 10), (38, 6)], fill=OUTL)
    d.line([(38, 6), (40, 8)], fill=OUTL)
    for x in (9, 19, 29, 39):  # floats
        d.ellipse([x - 2, 0, x + 2, 4], fill=RED, outline=OUTL)
    for x0, x1 in ((2, 4), (44, 46)):  # pegs
        d.rectangle([x0, 1, x1, 3], fill=OUTL)
    i = "LMR".index(part)
    return big.crop((i * 16, 0, i * 16 + 16, 16))


ROOTKIN = [  # (name, image), 8 per row
    ("floor", floor()), ("floor_b", floor(True)), ("thatch_top", thatch_top()), ("thatch_bot", thatch_bottom()),
    ("side", side_wall()), ("doormat", doormat()), ("mat", mat("single")), ("mat_L", mat("L")),
    ("mat_M", mat("M")), ("mat_R", mat("R")), ("hearth_0", hearth(0)), ("hearth_1", hearth(1)),
    ("hearth_2", hearth(2)), ("hearth_3", hearth(3)), ("basket", basket()), ("jar", jar()),
    ("herbs_L", herbs(False)), ("herbs_R", herbs(True)), ("paddles_L", paddles(False)), ("paddles_R", paddles(True)),
 ("bedroll_L", bedroll(False)), ("bedroll_R", bedroll(True)),
    ("bedrollm_L", bedroll(True).transpose(Image.FLIP_LEFT_RIGHT)), ("bedrollm_R", bedroll(False).transpose(Image.FLIP_LEFT_RIGHT)),
    ("bench_L", bench(False)), ("bench_R", bench(True)), ("canoe_0", canoe(0)), ("canoe_1", canoe(1)),
    ("canoe_2", canoe(2)), ("orb_blue_0", pedestal("blue", 0)), ("orb_blue_1", pedestal("blue", 1)), ("orb_red_0", pedestal("red", 0)),
    ("orb_red_1", pedestal("red", 1)),
] + [(f"kettle_{q}", hearth(q, True)) for q in range(4)] + [(f"firepit_{q}", firepit(q)) for q in range(9)] + [
    ("chair_0", chair(0)), ("chair_1", chair(1)), ("stool", stool())] + [
    (f"verse{n}_{'LR'[q % 2]}{q // 2}", verse(n, q)) for n in range(1, 5) for q in range(4)] + [
    ("wbasket_L", wall_basket(False)), ("wbasket_R", wall_basket(True))] + [
    (f"counter_{p}_{g}", trade_counter(p, g)) for p in "LMR" for g in ("bare", "balls", "potions")] + [
    (f"logs_{q}", log_pile(q)) for q in range(4)] + [(f"net_{p}", fishing_net(p)) for p in "LMR"] + [
    (f"wb_{p}_{i}", workbench(p, i)) for p, i in (("L", "knife"), ("M", "mallet"), ("M", "charm"), ("R", "knife"))]


# ------------------------------------------------------------------ conservatory
PAVE_L, PAVE, PAVE_D = (226, 222, 206), (204, 198, 180), (164, 158, 140)
MOSS = (128, 160, 96)
GLASS, GLASS_L, GLASS_D = (176, 216, 222), (214, 238, 240), (132, 180, 190)
FRAME, FRAME_D = (244, 244, 236), (176, 184, 180)
LEAF, LEAF_D = (96, 150, 96), (64, 112, 72)
WATER, WATER_L, WATER_D = (88, 152, 200), (150, 200, 232), (60, 112, 160)


def pavers():
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=PAVE)
    for x0, y0, x1, y1 in ((0, 0, 7, 7), (8, 0, 15, 7), (0, 8, 7, 15), (8, 8, 15, 15)):
        d.rectangle([x0, y0, x1, y1], outline=PAVE_D)
        d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=PAVE_L)
    for p in ((7, 3), (8, 12), (2, 8), (12, 7)):
        d.point(p, fill=MOSS)
    return c


def glass_wall(row):
    """Back wall: row 0 = upper panes against the sky; row 1 = lower panes with plants and a sill."""
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=GLASS if row == 0 else GLASS_D)
    if row == 1:
        d.ellipse([-3, 4, 9, 16], fill=LEAF_D)
        d.ellipse([7, 6, 19, 18], fill=LEAF)
        d.rectangle([0, 13, 15, 15], fill=FRAME)
        d.line([(0, 13), (15, 13)], fill=FRAME_D)
    d.line([(0, 0), (0, 15)], fill=FRAME)
    d.line([(8, 0), (8, 12 if row else 15)], fill=FRAME)
    if row == 0:
        d.line([(0, 8), (15, 8)], fill=FRAME)
        d.line([(2, 6), (5, 2)], fill=GLASS_L)
    return c


def glass_side():
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=GLASS_D)
    d.rectangle([5, 0, 10, 15], fill=FRAME)
    d.line([(5, 0), (5, 15)], fill=FRAME_D)
    d.ellipse([-6, 2, 4, 14], fill=LEAF_D)
    d.ellipse([11, 4, 21, 16], fill=LEAF)
    return c


def dais(part):
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=STONE_L)
    d.line([(0, 15), (15, 15)], fill=STONE_D)
    d.line([(0, 14), (15, 14)], fill=STONE)
    if part == "L":
        d.line([(0, 0), (0, 15)], fill=STONE_D)
    if part == "R":
        d.line([(15, 0), (15, 15)], fill=STONE_D)
    if part == "M":
        d.ellipse([4, 3, 11, 10], outline=(110, 150, 100))  # leaf emblem
        d.line([(7, 3), (8, 10)], fill=(110, 150, 100))
    return c


CONSERVATORY = [
    ("pavers", pavers()), ("glass_0", glass_wall(0)), ("glass_1", glass_wall(1)), ("glass_side", glass_side()),
    ("dais_L", dais("L")), ("dais_M", dais("M")), ("dais_R", dais("R")),
]


# ------------------------------------------------------------------ shelter (Isle Marais dance hall)
CANVAS, CANVAS_L, CANVAS_D = (120, 132, 84), (150, 162, 108), (88, 98, 62)
METAL, METAL_D = (176, 180, 184), (112, 116, 124)
BLANKET, BLANKET_D = (64, 96, 150), (44, 70, 116)
TABLE, TABLE_D = (200, 196, 186), (150, 146, 136)
BOX, BOX_D = (196, 156, 100), (150, 112, 64)
WATER_B = (140, 196, 232)
RED_X = (210, 50, 50)


def cot(part):
    """Camp cot, 1x2: part 0 = head (pillow), 1 = foot (folded blanket). Transparent around it."""
    c = cell()
    d = ImageDraw.Draw(c)
    y0, y1 = (2, 15) if part == 0 else (0, 13)
    d.rectangle([2, y0, 13, y1], fill=CANVAS, outline=METAL_D)
    d.line([(3, y0 + 1), (3, y1 - 1)], fill=CANVAS_L)
    d.line([(12, y0 + 1), (12, y1 - 1)], fill=CANVAS_D)
    if part == 0:
        d.rectangle([4, 3, 11, 7], fill=(232, 228, 216), outline=OUTL)   # pillow
        d.line([(2, 2), (13, 2)], fill=METAL)
    else:
        d.rectangle([3, 4, 12, 10], fill=BLANKET, outline=OUTL)          # folded blanket
        d.line([(3, 7), (12, 7)], fill=BLANKET_D)
        d.line([(2, 13), (13, 13)], fill=METAL)
        for x in (2, 13):
            d.line([(x, 13), (x, 15)], fill=METAL_D)                      # legs
    return c


def supply(part, row):
    """Folding tables piled with supplies, 3 cells wide x 2 tall: (part 0..2, row 0..1)."""
    big = Image.new("RGBA", (48, 32), CLEAR)
    d = ImageDraw.Draw(big)
    d.rectangle([1, 10, 46, 27], fill=TABLE, outline=OUTL)
    d.line([(2, 26), (45, 26)], fill=TABLE_D)
    for x in (3, 44):
        d.line([(x, 28), (x, 31)], fill=METAL_D)
    for i, x in enumerate((3, 9)):                                        # water bottles
        d.rectangle([x, 4, x + 4, 14], fill=WATER_B, outline=OUTL)
        d.rectangle([x + 1, 2, x + 3, 4], fill=(60, 110, 190))
    d.rectangle([16, 6, 29, 17], fill=BOX, outline=OUTL)                  # crate of cans
    d.line([(16, 11), (29, 11)], fill=BOX_D)
    for x in (18, 22, 26):
        d.ellipse([x, 13, x + 2, 15], fill=METAL)
    d.rectangle([33, 8, 44, 18], fill=(240, 240, 236), outline=OUTL)      # first-aid box
    d.rectangle([37, 10, 40, 16], fill=RED_X)
    d.rectangle([35, 12, 42, 14], fill=RED_X)
    d.rectangle([6, 18, 14, 23], fill=BOX, outline=OUTL)                  # loaves / parcels
    d.rectangle([20, 19, 30, 24], fill=(214, 180, 110), outline=OUTL)
    return big.crop((part * 16, row * 16, part * 16 + 16, row * 16 + 16))


def counter_row(part, items):
    """A one-row folding table (counter you can talk across): part 'L', 'M' or 'R', with items on top."""
    c = cell()
    d = ImageDraw.Draw(c)
    x0, x1 = (1 if part == "L" else 0), (14 if part == "R" else 15)
    d.rectangle([x0, 7, x1, 13], fill=TABLE, outline=None)
    d.line([(x0, 7), (x1, 7)], fill=OUTL)
    d.line([(x0, 13), (x1, 13)], fill=TABLE_D)
    d.line([(x0, 14), (x1, 14)], fill=OUTL)
    if part == "L":
        d.line([(1, 7), (1, 14)], fill=OUTL)
    if part == "R":
        d.line([(14, 7), (14, 14)], fill=OUTL)
    for x in ((3, 12) if part != "M" else (8,)):
        d.line([(x, 14), (x, 15)], fill=METAL_D)
    if items == "water":
        for x in (3, 8):
            d.rectangle([x, 1, x + 3, 10], fill=WATER_B, outline=OUTL)
            d.rectangle([x + 1, 0, x + 2, 1], fill=(60, 110, 190))
    elif items == "cans":
        d.rectangle([2, 3, 13, 10], fill=BOX, outline=OUTL)
        for x in (4, 8, 11):
            d.ellipse([x - 1, 5, x + 1, 7], fill=METAL)
    elif items == "aid":
        d.rectangle([3, 2, 12, 10], fill=(240, 240, 236), outline=OUTL)
        d.rectangle([6, 3, 9, 9], fill=RED_X)
        d.rectangle([4, 5, 11, 7], fill=RED_X)
    elif items == "bread":
        d.rectangle([2, 5, 8, 10], fill=(214, 180, 110), outline=OUTL)
        d.rectangle([9, 4, 13, 10], fill=BOX, outline=OUTL)
    elif items == "papers":
        d.rectangle([2, 4, 9, 10], fill=(244, 240, 226), outline=OUTL)
        d.line([(3, 6), (8, 6)], fill=TABLE_D)
        d.line([(3, 8), (7, 8)], fill=TABLE_D)
        d.rectangle([10, 2, 13, 10], fill=METAL_D, outline=OUTL)      # microscope
        d.point((11, 3), fill=WATER_B)
    elif items == "pot":
        d.ellipse([2, 1, 13, 11], fill=(70, 66, 64), outline=OUTL)   # gumbo pot
        d.ellipse([4, 3, 11, 6], fill=(150, 88, 40))
        d.point((6, 0), fill=(220, 220, 220))
        d.point((9, 0), fill=(220, 220, 220))
    elif items == "bowls":
        for x in (3, 9):
            d.ellipse([x, 6, x + 4, 10], fill=(232, 228, 216), outline=OUTL)
            d.line([(x + 1, 7), (x + 3, 7)], fill=(150, 88, 40))
    return c


def labkit(part):
    """Lafayette's field kit, 2x2: a crate of instruments with a sample case on top."""
    big = Image.new("RGBA", (32, 32), CLEAR)
    d = ImageDraw.Draw(big)
    d.rectangle([2, 10, 29, 30], fill=BOX, outline=OUTL)
    d.line([(2, 20), (29, 20)], fill=BOX_D)
    d.rectangle([6, 2, 25, 11], fill=(90, 120, 150), outline=OUTL)
    for x in (9, 14, 19):
        d.rectangle([x, 4, x + 3, 9], fill=WATER_B, outline=OUTL)
    d.rectangle([12, 23, 19, 27], fill=(240, 240, 236), outline=OUTL)
    return big.crop(((part % 2) * 16, (part // 2) * 16, (part % 2) * 16 + 16, (part // 2) * 16 + 16))


def accordion():
    """A battered accordion hanging on the wall (drawn over the wall tile)."""
    c = cell()
    d = ImageDraw.Draw(c)
    d.line([(8, 0), (8, 3)], fill=OUTL)
    d.rectangle([2, 3, 13, 13], fill=(150, 40, 40), outline=OUTL)
    for x in range(4, 13, 2):
        d.line([(x, 4), (x, 12)], fill=(100, 26, 26))
    d.rectangle([1, 4, 3, 12], fill=(232, 228, 216), outline=OUTL)
    for y in range(5, 12, 2):
        d.point((2, y), fill=OUTL)
    return c


def stage(lip, side=None):
    """Raised stage planks, darker than the hall floor; lip = the front face; side = 'L'/'R' for the
    stage's ends. One continuous outline runs down each end and turns along the front face at the corner."""
    c = cell()
    d = ImageDraw.Draw(c)
    x0, x1 = (2, 15) if side == "L" else (0, 13) if side == "R" else (0, 15)
    top_end = 10 if lip else 15
    d.rectangle([x0, 0, x1, top_end], fill=(150, 104, 62))
    for i, y in enumerate(range(0, top_end + 1, 4)):
        d.line([(x0, y), (x1, y)], fill=(178, 128, 80))
        if y + 3 <= top_end:
            d.line([(x0, y + 3), (x1, y + 3)], fill=(118, 80, 46))
        sx = (5 + i * 7) % 16
        if x0 <= sx <= x1:
            d.line([(sx, y), (sx, min(y + 2, top_end))], fill=(118, 80, 46))
    if lip:  # the front face
        d.rectangle([x0, 11, x1, 14], fill=(96, 64, 38))
        d.line([(x0, 11), (x1, 11)], fill=(196, 150, 96))
        d.line([(x0, 15), (x1, 15)], fill=OUTL)
    if side == "L":
        d.line([(1, 0), (1, 15 if lip else 15)], fill=OUTL)
        d.line([(0, 2), (0, 15)], fill=(150, 130, 90)) if False else None
    if side == "R":
        d.line([(14, 0), (14, 15)], fill=OUTL)
    if lip and side == "L":
        d.point((1, 15), fill=OUTL)
    if lip and side == "R":
        d.point((14, 15), fill=OUTL)
    return c


def floor_hall():
    """The theater's wood floor colours, for the strip beside the stage's ends (approximation, under the art)."""
    return cell()


SHELTER = ([("cot_0", cot(0)), ("cot_1", cot(1)), ("stage", stage(False)), ("stage_lip", stage(True)),
            ("stage_L", stage(False, "L")), ("stage_R", stage(False, "R")), ("stage_lip_L", stage(True, "L")), ("stage_lip_R", stage(True, "R"))]
           + [(f"supply_{p}{r}", supply(p, r)) for r in range(2) for p in range(3)]
           + [(f"ct_{part}_{it}", counter_row(part, it)) for part, it in
              (("L", "water"), ("M", "cans"), ("M", "bread"), ("M", "water"), ("R", "aid"), ("L", "aid"), ("R", "aid"),
               ("L", "papers"), ("M", "papers"), ("R", "papers"), ("L", "pot"), ("R", "bowls"), ("M", "aid"))]
           + [(f"labkit_{i}", labkit(i)) for i in range(4)] + [("accordion", accordion())])


# ------------------------------------------------------------------ church (Isle Marais)
STONE_F, STONE_F_L, STONE_F_D = (196, 188, 172), (216, 210, 196), (156, 148, 134)
WOOD_W, WOOD_W_L, WOOD_W_D = (110, 76, 50), (140, 100, 66), (78, 52, 34)
PLASTER, PLASTER_D = (226, 216, 196), (196, 184, 162)
PEW, PEW_L, PEW_D = (132, 88, 52), (164, 116, 72), (96, 62, 36)
RUNNER, RUNNER_D, GOLD = (170, 44, 48), (130, 30, 36), (222, 186, 90)
GLASS_C = [(70, 110, 190), (200, 60, 60), (230, 190, 70), (80, 160, 100)]


def ch_floor():
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=STONE_F)
    for x0, y0, x1, y1 in ((0, 0, 7, 7), (8, 0, 15, 7), (0, 8, 7, 15), (8, 8, 15, 15)):
        d.rectangle([x0, y0, x1, y1], outline=STONE_F_D)
        d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=STONE_F_L)
    return c


def ch_wall(row, window=None):
    """Back wall: row 0 = dark wood with a cornice, row 1 = plaster over a wainscot. window = 0/1 (part)."""
    c = cell()
    d = ImageDraw.Draw(c)
    if row == 0:
        d.rectangle([0, 0, 15, 15], fill=WOOD_W)
        d.line([(0, 2), (15, 2)], fill=WOOD_W_L)
        d.line([(0, 3), (15, 3)], fill=WOOD_W_D)
        for x in (3, 11):
            d.line([(x, 4), (x, 15)], fill=WOOD_W_D)
    else:
        d.rectangle([0, 0, 15, 15], fill=PLASTER)
        d.rectangle([0, 10, 15, 15], fill=WOOD_W)
        d.line([(0, 10), (15, 10)], fill=WOOD_W_L)
        d.line([(0, 15), (15, 15)], fill=OUTL)
    if window is not None:  # an arched stained-glass window across both rows
        if row == 0:
            d.rectangle([3, 6, 12, 15], fill=(60, 50, 70))
            d.pieslice([3, 1, 12, 11], 180, 360, fill=(60, 50, 70))
            for i, (x, y) in enumerate(((5, 7), (9, 7), (5, 11), (9, 11), (7, 4))):
                d.rectangle([x, y, x + 1, y + 2], fill=GLASS_C[i % 4])
        else:
            d.rectangle([3, 0, 12, 8], fill=(60, 50, 70))
            for i, (x, y) in enumerate(((5, 1), (9, 1), (7, 4), (5, 6), (9, 6))):
                d.rectangle([x, y, x + 1, y + 1], fill=GLASS_C[(i + 1) % 4])
            d.line([(3, 9), (12, 9)], fill=PLASTER_D)
    return c


def ch_side():
    c = cell()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 15, 15], fill=WOOD_W_D)
    d.line([(7, 0), (7, 15)], fill=WOOD_W)
    return c


def pew(part):
    """A pew facing the altar, seen from behind as the game's camera sees it: the seat on top, then the
    back of the tall backrest (panelled), carved end panels with rounded tops, a shadow on the floor.
    part L/M/R."""
    c = ch_floor()
    d = ImageDraw.Draw(c)
    x0, x1 = (3 if part == "L" else 0), (12 if part == "R" else 15)
    d.rectangle([x0, 2, x1, 5], fill=PEW_L)                   # seat
    d.line([(x0, 2), (x1, 2)], fill=(190, 140, 92))
    d.rectangle([x0, 6, x1, 7], fill=(176, 126, 80))          # top rail of the backrest
    d.line([(x0, 6), (x1, 6)], fill=(206, 156, 104))
    d.rectangle([x0, 8, x1, 13], fill=PEW)                    # back of the backrest
    for px in range(x0 + 3 if part == "L" else 1, x1, 5):     # panels
        d.rectangle([px, 9, px + 2, 12], outline=PEW_D)
    d.line([(x0, 13), (x1, 13)], fill=PEW_D)
    d.line([(x0, 14), (x1, 14)], fill=OUTL)
    d.line([(x0, 15), (x1, 15)], fill=STONE_F_D)              # shadow on the floor
    if part in ("L", "R"):                                    # carved end panel, rounded top
        ex = 1 if part == "L" else 12
        d.rectangle([ex, 3, ex + 2, 14], fill=PEW_D)
        d.ellipse([ex - 1, 0, ex + 3, 4], fill=PEW_D)
        d.line([(ex + 1, 1), (ex + 1, 13)], fill=PEW)
        d.line([(ex - 1, 2), (ex - 1, 14)] if part == "L" else [(ex + 3, 2), (ex + 3, 14)], fill=OUTL)
        d.line([(ex, 15), (ex + 2, 15)], fill=STONE_F_D)
    return c


def altar(part, row):
    """Altar on a raised step: row 0 = the table with candles and cloth, row 1 = the step."""
    c = ch_floor()
    d = ImageDraw.Draw(c)
    x0, x1 = (1 if part == "L" else 0), (14 if part == "R" else 15)
    if row == 0:
        d.rectangle([x0, 3, x1, 15], fill=(236, 230, 214))       # cloth
        d.line([(x0, 3), (x1, 3)], fill=OUTL)
        d.rectangle([x0, 9, x1, 11], fill=RUNNER)                # red band
        if part != "M":
            d.rectangle([6, 0, 8, 5], fill=(250, 246, 230), outline=OUTL)   # candle
            d.point((7, 0), fill=FLAME_L)
        else:
            d.rectangle([5, 4, 10, 7], fill=GOLD, outline=OUTL)              # a plain gold plate
    else:
        d.rectangle([x0, 0, x1, 9], fill=STONE_F_L)
        d.line([(x0, 9), (x1, 9)], fill=STONE_F_D)
        d.line([(x0, 10), (x1, 10)], fill=OUTL)
    if part == "L":
        d.line([(x0, 3 if row == 0 else 0), (x0, 15 if row == 0 else 10)], fill=OUTL)
    if part == "R":
        d.line([(x1, 3 if row == 0 else 0), (x1, 15 if row == 0 else 10)], fill=OUTL)
    return c


def runner(part):
    """The red aisle runner (vertical): 'T' top end, 'M' middle; L/C/R columns. A dark outer edge with
    gold trim just inside it runs down both sides and across the top end, turning the corners."""
    c = ch_floor()
    d = ImageDraw.Draw(c)
    side = part[-1]
    top = part.startswith("T")
    x0, x1 = (3, 15) if side == "L" else (0, 12) if side == "R" else (0, 15)
    y0 = 3 if top else 0
    d.rectangle([x0, y0, x1, 15], fill=RUNNER)
    if side == "L":
        d.line([(x0, y0), (x0, 15)], fill=RUNNER_D)
        d.line([(x0 + 1, y0 + (1 if top else 0)), (x0 + 1, 15)], fill=GOLD)
    if side == "R":
        d.line([(x1, y0), (x1, 15)], fill=RUNNER_D)
        d.line([(x1 - 1, y0 + (1 if top else 0)), (x1 - 1, 15)], fill=GOLD)
    if top:
        d.line([(x0, y0), (x1, y0)], fill=RUNNER_D)
        gx0 = x0 + 1 if side == "L" else 0
        gx1 = x1 - 1 if side == "R" else 15
        d.line([(gx0, y0 + 1), (gx1, y0 + 1)], fill=GOLD)
    return c


def candles():
    c = ch_floor()
    d = ImageDraw.Draw(c)
    d.rectangle([2, 8, 13, 13], fill=WOOD_W, outline=OUTL)          # stand
    for x, h in ((4, 4), (7, 6), (10, 3)):
        d.rectangle([x, 8 - h, x + 1, 8], fill=(250, 246, 230))
        d.point((x, 7 - h), fill=FLAME_L)
    return c


def bellrope(part):
    """The bell rope: 0 = hanging from the ceiling, 1 = its tassel above the floor."""
    c = ch_floor()
    d = ImageDraw.Draw(c)
    if part == 0:
        d.line([(7, 0), (7, 15)], fill=(200, 174, 112))
        d.line([(8, 0), (8, 15)], fill=(150, 124, 76))
    else:
        d.line([(7, 0), (7, 7)], fill=(200, 174, 112))
        d.line([(8, 0), (8, 7)], fill=(150, 124, 76))
        d.polygon([(5, 8), (10, 8), (11, 13), (4, 13)], fill=RUNNER, outline=OUTL)
    return c


def ch_mat(side):
    """Door mat, L/C/R pieces: a dark red mat with a gold border around the whole mat."""
    c = ch_floor()
    d = ImageDraw.Draw(c)
    x0, x1 = (2, 15) if side == "L" else (0, 13) if side == "R" else (0, 15)
    d.rectangle([x0, 3, x1, 15], fill=RUNNER_D)
    d.line([(x0 if side == "L" else 0, 4), (x1 if side == "R" else 15, 4)], fill=GOLD)
    d.line([(x0 if side == "L" else 0, 14), (x1 if side == "R" else 15, 14)], fill=GOLD)
    if side == "L":
        d.line([(x0 + 1, 4), (x0 + 1, 14)], fill=GOLD)
    if side == "R":
        d.line([(x1 - 1, 4), (x1 - 1, 14)], fill=GOLD)
    return c


CHURCH = ([("floor", ch_floor()), ("wall_0", ch_wall(0)), ("wall_1", ch_wall(1)), ("win_0", ch_wall(0, 0)), ("win_1", ch_wall(1, 1)),
           ("side", ch_side()), ("candles", candles()), ("rope_0", bellrope(0)), ("rope_1", bellrope(1)),
           ("mat_L", ch_mat("L")), ("mat_C", ch_mat("C")), ("mat_R", ch_mat("R"))]
          + [(f"pew_{p}", pew(p)) for p in "LMR"]
          + [(f"altar_{p}{r}", altar(p, r)) for r in range(2) for p in "LMR"]
          + [(f"run_{p}", runner(p)) for p in ("TL", "TC", "TR", "ML", "MC", "MR")])


def sheet(cells, name):
    rows = (len(cells) + 7) // 8
    im = Image.new("RGB", (128, rows * 16), KEY)
    for i, (_, c) in enumerate(cells):
        im.paste(c, ((i % 8) * 16, (i // 8) * 16), c)
    im.save(os.path.join(HERE, name))
    print(os.path.join(HERE, name))


def cell_index(cells):
    return {n: [i % 8, i // 8] for i, (n, _) in enumerate(cells)}


if __name__ == "__main__":
    sheet(ROOTKIN, "rootkin_interior.png")
    sheet(CONSERVATORY, "conservatory.png")
    sheet(SHELTER, "shelter.png")
    sheet(CHURCH, "church.png")

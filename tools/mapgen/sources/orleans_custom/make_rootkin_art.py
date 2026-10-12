"""Rootkin buildings for the Old Water (own art): stilt hut, round song house, canoe boathouse.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_rootkin_art.py
writes rootkin_hut.png (3x4 cells), rootkin_songhouse.png (5x5), rootkin_boathouse.png (4x3); magenta = transparent.
The Rootkin and their customs are invented; nothing here depicts a real people's sacred architecture.
"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
CLEAR = (0, 0, 0, 0)
OUTL = (52, 42, 34)
TH_L, TH, TH_D, TH_DD = (214, 192, 124), (184, 158, 92), (146, 120, 64), (104, 84, 46)   # palmetto thatch
WD_L, WD, WD_D = (156, 136, 108), (124, 104, 82), (92, 76, 60)                         # weathered cypress
STILT = (84, 68, 52)
MAT_L, MAT_D = (176, 128, 74), (128, 90, 52)                                            # woven door mat
TEAL, OCHRE, RED = (72, 140, 136), (204, 152, 64), (186, 66, 56)
FLAME, FLAME_L = (232, 120, 48), (252, 208, 96)
SHADOW = (60, 50, 40)


def thatch(d, poly_top, y0, y1, xl, xr):
    """Fill rows y0..y1 between xl(y)..xr(y) with layered palmetto thatch."""
    for y in range(y0, y1 + 1):
        a, b = int(xl(y)), int(xr(y))
        band = (y - y0) % 5
        base = TH_L if band == 0 else TH if band < 3 else TH_D
        d.line([(a, y), (b, y)], fill=base)
        for x in range(a + (y % 3), b, 3):  # frond strokes
            if band in (1, 3):
                d.point((x, y), fill=TH_D if band == 1 else TH_DD)
    # outline
    for y in range(y0, y1 + 1):
        d.point((int(xl(y)), y), fill=OUTL)
        d.point((int(xr(y)), y), fill=OUTL)
    d.line([(int(xl(y0)), y0), (int(xr(y0)), y0)], fill=OUTL)


def fringe(d, y, a, b):
    """Ragged thatch ends hanging below the eave."""
    for x in range(a, b + 1):
        ln = 1 + ((x * 7) % 4)
        d.line([(x, y), (x, y + ln)], fill=TH_D if x % 2 else TH)
        d.point((x, y + ln + 1), fill=OUTL)


def planks_v(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=WD, outline=OUTL)
    for x in range(x0 + 4, x1, 4):
        d.line([(x, y0 + 1), (x, y1 - 1)], fill=WD_D)
        d.line([(x + 1, y0 + 1), (x + 1, y0 + 3)], fill=WD_L)


def mat_door(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=MAT_D, outline=OUTL)
    for y in range(y0 + 1, y1, 2):
        for x in range(x0 + 1 + (y // 2) % 2, x1, 2):
            d.point((x, y), fill=MAT_L)
    d.line([(x0, y0 + 1), (x1, y0 + 1)], fill=WD_D)


def charm(d, x, y):
    d.line([(x, y), (x, y + 6)], fill=OUTL)
    for i, c in enumerate((RED, OCHRE, TEAL)):
        d.point((x, y + 2 + i * 2), fill=c)
        d.point((x - 1, y + 2 + i * 2), fill=c)


def hut():
    """Stilt hut, 3x4 cells: palmetto roof, cypress plank walls, porch on stilts, ladder to the door."""
    w, h = 48, 64
    im = Image.new("RGBA", (w, h), CLEAR)
    d = ImageDraw.Draw(im)
    # stilts and ladder (bottom), drawn first
    for x in (5, 41):
        d.rectangle([x, 50, x + 2, 62], fill=STILT, outline=OUTL)
    for x in (18, 29):
        d.line([(x, 50), (x, 63)], fill=OUTL)
    for y in range(52, 63, 3):
        d.line([(19, y), (28, y)], fill=WD_L)
        d.line([(19, y + 1), (28, y + 1)], fill=WD_D)
    for x in range(8, 40):  # shadow under the porch
        if not (17 <= x <= 30):
            d.point((x, 51), fill=SHADOW)
    # porch deck
    d.rectangle([2, 46, 45, 50], fill=WD_L, outline=OUTL)
    for x in range(6, 45, 6):
        d.line([(x, 47), (x, 49)], fill=WD_D)
    # walls
    planks_v(d, 5, 26, 42, 46)
    mat_door(d, 19, 31, 28, 46)
    d.rectangle([8, 31, 15, 37], fill=(70, 60, 50), outline=OUTL)          # window
    d.line([(8, 34), (15, 34)], fill=WD_L)
    d.rectangle([33, 31, 39, 37], fill=(70, 60, 50), outline=OUTL)
    d.line([(36, 31), (36, 37)], fill=WD_L)
    charm(d, 30, 27)
    for x, y in ((10, 40), (12, 41), (35, 41)):  # hanging herbs
        d.line([(x, 38), (x, y)], fill=(96, 132, 72))
    # roof: palmetto thatch gable
    thatch(d, None, 2, 25, lambda y: 12 - y * 0.48, lambda y: 35 + y * 0.48)
    fringe(d, 26, 0, 47)
    d.line([(12, 2), (35, 2)], fill=OUTL)
    d.rectangle([22, 0, 25, 2], fill=WD_D, outline=OUTL)  # ridge pole end
    return im


def songhouse():
    """Round song house, 5x5 cells: conical thatch roof, painted band, carved posts, torches."""
    w, h = 80, 80
    im = Image.new("RGBA", (w, h), CLEAR)
    d = ImageDraw.Draw(im)
    # stilts / low platform
    for x in (6, 22, 56, 72):
        d.rectangle([x, 70, x + 2, 78], fill=STILT, outline=OUTL)
    d.rectangle([2, 64, 77, 70], fill=WD_L, outline=OUTL)
    for x in range(8, 77, 7):
        d.line([(x, 65), (x, 69)], fill=WD_D)
    for y in range(71, 80, 3):  # broad steps to the entrance
        d.rectangle([30, y, 49, y + 1], fill=WD_L if y % 2 else WD, outline=OUTL)
    # round wall
    d.rounded_rectangle([6, 40, 73, 64], radius=8, fill=WD, outline=OUTL)
    for x in range(10, 72, 4):
        d.line([(x, 42), (x, 63)], fill=WD_D)
    # painted band: zigzag
    d.rectangle([7, 52, 72, 56], fill=OCHRE)
    for x in range(7, 72, 4):
        d.line([(x, 56), (x + 2, 52)], fill=TEAL)
        d.line([(x + 2, 52), (x + 4, 56)], fill=TEAL)
    d.line([(7, 51), (72, 51)], fill=OUTL)
    d.line([(7, 57), (72, 57)], fill=OUTL)
    # entrance with carved posts
    mat_door(d, 31, 50, 48, 64)
    d.rectangle([33, 50, 46, 55], fill=(60, 48, 38))
    for x in (28, 49):
        d.rectangle([x, 44, x + 2, 64], fill=WD_D, outline=OUTL)
        d.point((x + 1, 47), fill=RED)
        d.point((x + 1, 53), fill=TEAL)
    # torches
    for x in (16, 62):
        d.line([(x, 52), (x, 64)], fill=STILT)
        d.ellipse([x - 2, 47, x + 2, 52], fill=FLAME)
        d.point((x, 48), fill=FLAME_L)
        d.point((x, 49), fill=FLAME_L)
    # conical thatch roof
    cx = 39.5
    thatch(d, None, 6, 42, lambda y: cx - 4 - (y - 6) * 1.0 - math.sin((y - 6) / 36 * math.pi) * 6,
           lambda y: cx + 4 + (y - 6) * 1.0 + math.sin((y - 6) / 36 * math.pi) * 6)
    fringe(d, 43, 2, 77)
    # finial: carved pole with a feather
    d.rectangle([38, 0, 41, 6], fill=WD_D, outline=OUTL)
    d.line([(42, 1), (45, 0)], fill=RED)
    d.line([(42, 2), (46, 2)], fill=OCHRE)
    return im


def boathouse():
    """Canoe boathouse, 4x3 cells: thatch roof on posts over the water, a canoe in its slip."""
    w, h = 64, 48
    im = Image.new("RGBA", (w, h), CLEAR)
    d = ImageDraw.Draw(im)
    # canoe in the slip (water shows through)
    d.ellipse([12, 34, 52, 42], fill=WD, outline=OUTL)
    d.ellipse([16, 36, 48, 40], fill=WD_D)
    d.line([(20, 38), (44, 38)], fill=(70, 56, 44))
    # posts
    for x in (3, 29, 58):
        d.rectangle([x, 18, x + 2, 46], fill=STILT, outline=OUTL)
    # shade under the roof
    for y in range(19, 24):
        for x in range(4, 60):
            if (x + y) % 2 == 0:
                d.point((x, y), fill=SHADOW)
    # roof
    thatch(d, None, 2, 17, lambda y: 6 - y * 0.35, lambda y: 57 + y * 0.35)
    fringe(d, 18, 0, 63)
    d.line([(6, 2), (57, 2)], fill=OUTL)
    charm(d, 31, 19)
    return im


ROPE, ROPE_D = (200, 174, 112), (150, 124, 76)


def walk_v():
    """Vertical walkway, 3 cells wide, one cell tall (tiles vertically): rough planks between rope rails."""
    im = Image.new("RGBA", (48, 16), CLEAR)
    d = ImageDraw.Draw(im)
    for i, y in enumerate(range(0, 16, 4)):  # planks across the walkway, slightly uneven ends
        a, b = 4 - (i % 2), 43 + ((i * 3) % 3)
        d.rectangle([a, y, b, y + 2], fill=WD_L if i % 2 else WD, outline=None)
        d.line([(a, y + 3), (b, y + 3)], fill=WD_D)
        d.point((a + 6 + i * 5 % 20, y + 1), fill=WD_D)  # knots
        d.point((b - 9 - i * 7 % 15, y + 1), fill=WD_D)
        d.point((a, y), fill=OUTL)
        d.point((b, y + 2), fill=OUTL)
    for x in (2, 45):  # rope rails and a lashed post per cell
        d.line([(x, 0), (x, 15)], fill=ROPE)
        d.line([(x + 1 if x == 2 else x - 1, 0), (x + 1 if x == 2 else x - 1, 15)], fill=ROPE_D)
        d.rectangle([x - 1, 5, x + 1, 9], fill=STILT, outline=OUTL)
        d.line([(x - 1, 7), (x + 1, 7)], fill=ROPE)
    return im


def walk_h():
    """Horizontal walkway, 3x3 cells: left end, middle (repeats), right end; deck rows then pilings."""
    im = Image.new("RGBA", (48, 48), CLEAR)
    d = ImageDraw.Draw(im)
    # deck: boards running across the walkway (vertical boards)
    for i, x in enumerate(range(2, 46, 4)):
        top, bot = 4 - (i % 2), 28 + (i * 3) % 3
        d.rectangle([x, top, x + 2, bot], fill=WD_L if i % 2 else WD)
        d.line([(x + 3, top), (x + 3, bot)], fill=WD_D)
        d.point((x + 1, top + 7 + (i * 5) % 12), fill=WD_D)
        d.point((x, bot), fill=OUTL)
    # rope rails along both sides with lashed posts
    for y in (2, 29):
        d.line([(2, y), (45, y)], fill=ROPE)
        d.line([(2, y + 1), (45, y + 1)], fill=ROPE_D)
    for x in (2, 23, 44):
        for y in (0, 27):
            d.rectangle([x - 1, y, x + 1, y + 4], fill=STILT, outline=OUTL)
            d.line([(x - 1, y + 2), (x + 1, y + 2)], fill=ROPE)
    # shadow under the deck and pilings into the water
    for x in range(2, 46):
        d.point((x, 32), fill=SHADOW)
        if x % 2 == 0:
            d.point((x, 33), fill=SHADOW)
    for x in (4, 22, 42):
        d.rectangle([x, 32, x + 2, 41], fill=STILT, outline=OUTL)
        d.line([(x - 1, 43), (x + 3, 43)], fill=(150, 196, 200))  # ripple
    return im


def save(img, name):
    out = Image.new("RGB", img.size, KEY)
    out.paste(img, (0, 0), img)
    out.save(os.path.join(HERE, name))
    print(os.path.join(HERE, name))


if __name__ == "__main__":
    save(hut(), "rootkin_hut.png")
    save(songhouse(), "rootkin_songhouse.png")
    save(walk_v(), "rootkin_walk_v.png")
    save(walk_h(), "rootkin_walk_h.png")

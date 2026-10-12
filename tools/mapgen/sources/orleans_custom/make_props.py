"""Own art: street furniture and lived-in props for the Orleans towns, drawn to sit on any ground (overlays).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_props.py
writes props.png (cells of 16x16, magenta = transparent) and props_preview.png. Layout (cell x, y):
    bench      (0,0)-(1,0)   wooden slat bench with iron ends, 2x1
    lamp       (2,0)/(2,1)   black iron gas lamp, lantern lit, 1x2 (top, post)
    planter    (3,1)-(4,1)   brick planter of mixed flowers, 2x1
    barrel     (5,1)         oak barrel with iron hoops
    crates     (6,1)         stacked fish crates
    trap       (7,1)         crab trap (wire cage, rope float)
    net_rack   (3,0)-(4,0) over (3,1)? no: (5,0)-(6,0) top, see NET below
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
OUT = (46, 40, 40)
WOOD, WOOD_L, WOOD_D = (150, 108, 70), (184, 140, 94), (104, 72, 46)
IRON, IRON_L = (44, 44, 52), (92, 92, 104)
GLOW, GLOW_L = (250, 214, 110), (255, 246, 196)
BRICK, BRICK_L, BRICK_D = (170, 82, 60), (200, 112, 82), (120, 56, 44)
SOIL = (92, 66, 48)
LEAF, LEAF_D = (88, 138, 76), (60, 102, 60)
FLOWERS = [(226, 72, 72), (246, 206, 70), (240, 240, 236), (168, 104, 196), (240, 140, 170)]
WIRE, WIRE_D = (150, 160, 150), (96, 110, 100)
ROPE = (206, 180, 120)
FLOAT = (226, 92, 56)

CELLS = (8, 2)


def main():
    im = Image.new("RGB", (CELLS[0] * 16, CELLS[1] * 16), KEY)
    px = im.load()

    def put(x, y, c):
        px[x, y] = c

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                put(x, y, c)

    # ---- bench (cells 0,0 and 1,0): seen from the front, seat and back slats, iron ends, standing on its feet
    bx = 0
    rect(bx + 2, 3, bx + 29, 4, OUT)        # back rail top outline
    for y, c in ((4, WOOD_L), (5, WOOD), (7, WOOD_L), (8, WOOD)):  # two back slats
        rect(bx + 3, y, bx + 28, y, c)
    rect(bx + 3, 6, bx + 28, 6, WOOD_D)
    rect(bx + 3, 9, bx + 28, 9, WOOD_D)
    for y, c in ((10, WOOD_L), (11, WOOD), (12, WOOD_D)):  # seat
        rect(bx + 2, y, bx + 29, y, c)
    for x in (bx + 2, bx + 29):  # iron ends and legs
        rect(x - 1, 4, x, 14, IRON)
        put(x, 5, IRON_L)
    rect(bx + 1, 15, bx + 3, 15, IRON)
    rect(bx + 28, 15, bx + 30, 15, IRON)
    for x in (bx + 2, bx + 29):
        put(x - 1, 3, OUT)
    # ---- gas lamp (cell 2,0 top: lantern; 2,1: post)
    lx = 32
    rect(lx + 6, 1, lx + 9, 1, IRON)        # cap
    rect(lx + 5, 2, lx + 10, 3, IRON)
    rect(lx + 5, 4, lx + 10, 10, IRON)      # lantern frame
    rect(lx + 6, 4, lx + 9, 9, GLOW)
    rect(lx + 6, 4, lx + 7, 6, GLOW_L)
    rect(lx + 5, 11, lx + 10, 12, IRON)
    rect(lx + 7, 13, lx + 8, 15, IRON)
    rect(lx + 7, 16, lx + 8, 28, IRON)      # post
    put(lx + 7, 17, IRON_L)
    rect(lx + 6, 26, lx + 9, 27, IRON)      # collar
    rect(lx + 5, 28, lx + 10, 30, IRON)     # base
    rect(lx + 6, 28, lx + 7, 28, IRON_L)
    # ---- planter (cells 3,1 and 4,1): brick box with soil and mixed flowers above the rim
    px0, py0 = 48, 16
    rect(px0 + 1, py0 + 8, px0 + 30, py0 + 15, BRICK)
    for y in (py0 + 10, py0 + 13):
        rect(px0 + 1, y, px0 + 30, y, BRICK_D)
    for x in range(px0 + 1, px0 + 31, 4):
        for y in range(py0 + 8, py0 + 16):
            if (y - py0) in (11, 12) and (x - px0) % 8 == 1 or (y - py0) in (8, 9) and (x - px0) % 8 == 5 or \
                    (y - py0) in (14, 15) and (x - px0) % 8 == 5:
                put(x, y, BRICK_D)
    rect(px0 + 1, py0 + 7, px0 + 30, py0 + 7, BRICK_L)  # rim
    rect(px0 + 2, py0 + 5, px0 + 29, py0 + 6, SOIL)
    import random
    rng = random.Random(7)
    for x in range(px0 + 2, px0 + 30):  # foliage
        for y in range(py0 + 1, py0 + 6):
            if y >= py0 + 3 or rng.random() < 0.5:
                put(x, y, LEAF if rng.random() < 0.6 else LEAF_D)
    for i, x in enumerate(range(px0 + 3, px0 + 29, 4)):  # blooms, every colour
        c = FLOWERS[i % len(FLOWERS)]
        y = py0 + 1 + (i % 2)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)):
            if 0 <= y + dy - py0 < 6:
                put(x + dx, y + dy, c)
        put(x, y, (255, 255, 230))
    # ---- barrel (cell 5,1)
    x0, y0 = 80, 16
    for y in range(y0 + 2, y0 + 16):
        t = abs((y - y0) - 8.5) / 7.5
        half = 6 - int(t * 1.6)
        for x in range(x0 + 8 - half, x0 + 8 + half):
            u = (x - (x0 + 8 - half)) / (2 * half)
            put(x, y, WOOD_L if u < 0.35 else WOOD if u < 0.75 else WOOD_D)
        put(x0 + 8 - half - 1, y, OUT)
        put(x0 + 8 + half, y, OUT)
    for y in (y0 + 5, y0 + 12):
        rect(x0 + 2, y, x0 + 13, y, IRON)
    rect(x0 + 4, y0 + 1, x0 + 11, y0 + 2, WOOD_D)  # lid
    rect(x0 + 5, y0 + 1, x0 + 10, y0 + 1, WOOD_L)
    # ---- crates (cell 6,1): two fish crates stacked
    x0 = 96
    for (cx0, cy0, cx1, cy1) in ((x0 + 1, y0 + 8, x0 + 14, y0 + 15), (x0 + 3, y0 + 1, x0 + 12, y0 + 8)):
        rect(cx0, cy0, cx1, cy1, OUT)
        rect(cx0 + 1, cy0 + 1, cx1 - 1, cy1 - 1, WOOD)
        for y in range(cy0 + 1, cy1):
            if (y - cy0) % 3 == 0:
                rect(cx0 + 1, y, cx1 - 1, y, WOOD_D)
        rect(cx0 + 1, cy0 + 1, cx1 - 1, cy0 + 1, WOOD_L)
    # ---- crab trap (cell 7,1): wire cage with a rope and an orange float
    x0 = 112
    rect(x0 + 1, y0 + 6, x0 + 13, y0 + 15, WIRE_D)
    for y in range(y0 + 7, y0 + 15):
        for x in range(x0 + 2, x0 + 13):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                put(x, y, WIRE)
            else:
                put(x, y, (70, 84, 76))
    rect(x0 + 1, y0 + 6, x0 + 13, y0 + 6, WIRE)
    for y in range(y0 + 2, y0 + 7):
        put(x0 + 12, y, ROPE)
    rect(x0 + 11, y0 + 0, x0 + 14, y0 + 3, FLOAT)
    put(x0 + 12, y0 + 1, (255, 170, 130))
    im.save(os.path.join(HERE, "props.png"))
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(os.path.join(HERE, "props_preview.png"))
    print("props.png", im.size)


if __name__ == "__main__":
    main()

"""Own art: the river face of a grassy levee, drawn in the swamp palette.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_levee.py
writes levee.png (2 variants side by side, each 16 px wide x 48 px tall = 3 cells) and levee_preview.png:
    row 0  the crest: flat grass, a lit rim, a ragged grass overhang, then the slope begins
    row 1  the slope face (vertical grass blades, darkening as it falls) down to a shaded earth band
    row 2  riprap: rounded, outlined stones heaped at the toe, foam where they meet the water (bottom of the
           cell is water, so the next row down is plain water)
Variants A/B tile in any order along a straight bank. Magenta = transparent (the water shows through).
"""
import os
import random

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
GRASS = [(120, 160, 104), (110, 146, 100), (104, 144, 96), (136, 176, 128)]   # the shared swamp grass
RIM, RIM_D = (156, 190, 120), (90, 122, 72)
SLOPE = [(98, 132, 80), (88, 120, 72), (78, 108, 64), (68, 96, 58)]           # lit .. shaded slope greens
BLADE_L, BLADE_D = (124, 158, 94), (60, 86, 52)
EARTH, EARTH_D, EARTH_L = (118, 94, 66), (88, 70, 52), (146, 120, 86)
STONE, STONE_L, STONE_D, STONE_O = (150, 146, 138), (190, 186, 174), (112, 108, 102), (62, 60, 60)
WET = (74, 62, 50)
WATER, FOAM = (93, 136, 140), (196, 222, 222)


def cell_set(seed):
    rnd = random.Random(seed)
    im = Image.new("RGB", (16, 48), KEY)
    px = im.load()
    # ---- row 0: crest
    # y 0-4 stay transparent: the real swamp grass tile shows through above the rim
    for x in range(16):
        px[x, 5] = RIM
        px[x, 6] = RIM if (x + seed) % 3 else SLOPE[0]           # ragged overhang
        px[x, 7] = RIM_D if (x + seed) % 3 == 0 else SLOPE[0]
    # ---- slope face rows 0 (y 8-15) and 1 (y 16-27): darker as it falls, vertical blades
    for y in range(8, 28):
        band = min(3, (y - 8) // 5)
        for x in range(16):
            px[x, y] = SLOPE[band]
    for x in range(16):
        top = 8 + rnd.randrange(0, 4)
        while top < 26:
            length = rnd.randrange(2, 5)
            for y in range(top, min(27, top + length)):
                px[x, y] = BLADE_L if y < 14 and (x + y) % 2 else BLADE_D if y > 18 else SLOPE[0]
            top += length + rnd.randrange(2, 5)
    for _ in range(3):  # a few clover/weed clumps on the face
        cx, cy = rnd.randrange(2, 14), rnd.randrange(10, 22)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            px[cx + dx, cy + dy] = BLADE_L if (dx, dy) == (0, -1) else (70, 104, 60)
    # earth band at the toe (y 28-31), roots and pebbles
    for y in range(28, 32):
        for x in range(16):
            px[x, y] = EARTH_D if y == 28 else EARTH
    for x in range(0, 16, 3):
        px[(x + seed) % 16, 28] = BLADE_D
        px[(x + 1 + seed) % 16, 30] = EARTH_L
    # ---- row 2: riprap (y 32-47) over wet earth, then water at the bottom
    for y in range(32, 48):
        for x in range(16):
            px[x, y] = WET if y < 42 else WATER
    stones = [(2 + seed % 2, 35, 3), (8, 34, 4), (14 - seed % 2, 36, 3), (5, 40, 3), (11, 41, 3)]
    for cx, cy, r in stones:
        for y in range(cy - r - 1, cy + r + 2):
            for x in range(cx - r - 1, cx + r + 2):
                d = ((x - cx) ** 2 + ((y - cy) * 1.25) ** 2) ** 0.5
                xx = x % 16
                if 32 <= y < 48:
                    if d <= r - 0.5:
                        u = (x - cx) + (y - cy)  # light from the top-left
                        px[xx, y] = STONE_L if u < -2 else STONE_D if u > 2 else STONE
                    elif d <= r + 0.6 and px[xx, y] not in (STONE, STONE_L, STONE_D):
                        px[xx, y] = STONE_O
    for x in range(16):  # foam where the stones meet the water
        for y in (42, 43):
            if px[x, y] == WATER:
                px[x, y] = FOAM if (x + y + seed) % 3 else WATER
        if px[x, 44] == WATER and (x + seed) % 4 == 0:
            px[x, 44] = FOAM
    return im


def main():
    out = Image.new("RGB", (32, 48), KEY)
    out.paste(cell_set(0), (0, 0))
    out.paste(cell_set(1), (16, 0))
    out.save(os.path.join(HERE, "levee.png"))
    strip = Image.new("RGB", (16 * 12, 48))
    for i in range(12):
        strip.paste(out.crop(((i % 2) * 16, 0, (i % 2) * 16 + 16, 48)), (i * 16, 0))
    strip.resize((strip.width * 4, strip.height * 4), Image.NEAREST).save(os.path.join(HERE, "levee_preview.png"))
    print("levee.png", out.size)


if __name__ == "__main__":
    main()

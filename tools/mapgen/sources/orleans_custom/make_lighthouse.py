"""Own art for Storm's Edge: a Gulf-coast lighthouse (3x6 cells), white tower with two red bands, a black
lantern room with a gallery rail and a red cap, on a stone plinth with the keeper's door.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_lighthouse.py
writes lighthouse.png next to this script; magenta = transparent. Each cell is overlaid on the terrain
under it (the door cell, (1, 5), gets a door behaviour in the tileset config).
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
OUT = (52, 50, 58)
WHITE, WHITE_M, WHITE_D = (246, 244, 236), (214, 212, 204), (170, 168, 164)
RED, RED_M, RED_D = (204, 64, 52), (170, 44, 40), (122, 30, 32)
IRON, IRON_L = (40, 40, 48), (88, 88, 100)
GLASS, GLASS_L = (248, 232, 150), (255, 250, 214)
STONE, STONE_L, STONE_D = (156, 146, 132), (186, 176, 160), (112, 104, 96)
DOOR, DOOR_D = (110, 72, 48), (74, 46, 32)

W, H = 48, 96


def main():
    im = Image.new("RGB", (W, H), KEY)
    px = im.load()

    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = c

    cx = 23.5
    # ---- tower: tapers from 30 wide at its foot (y 80) to 18 at the gallery (y 30)
    top, foot = 30, 80
    for y in range(top, foot + 1):
        t = (y - top) / (foot - top)
        half = 9 + t * 6
        x0, x1 = int(round(cx - half)), int(round(cx + half))
        band = 44 <= y <= 51 or 62 <= y <= 69
        for x in range(x0, x1 + 1):
            u = (x - x0) / max(1, x1 - x0)  # 0 left .. 1 right: light from the left
            if band:
                c = RED if u < 0.45 else RED_M if u < 0.8 else RED_D
            else:
                c = WHITE if u < 0.45 else WHITE_M if u < 0.8 else WHITE_D
            put(x, y, c)
        put(x0 - 1, y, OUT)
        put(x1 + 1, y, OUT)
    # small windows up the tower
    for wy in (37, 56, 74):
        for y in range(wy, wy + 4):
            for x in (23, 24):
                put(x, y, IRON)
        put(23, wy, IRON_L)
    # ---- gallery deck and rail (y 24-30), wider than the tower
    for y in range(26, 31):
        for x in range(10, 38):
            put(x, y, IRON if y >= 28 else IRON_L)
    for x in range(10, 38, 3):  # rail posts
        for y in range(22, 26):
            put(x, y, IRON)
    for x in range(10, 38):
        put(x, 22, IRON)
    # ---- lantern room: glass panes with mullions (y 12-25)
    for y in range(12, 26):
        for x in range(16, 32):
            c = GLASS_L if x < 20 else GLASS
            if x in (16, 21, 26, 31) or y == 12:
                c = IRON
            put(x, y, c)
    # the lamp
    for y in range(16, 22):
        for x in range(22, 26):
            put(x, y, (255, 255, 236))
    # ---- red cap and vent ball (y 2-12)
    for y in range(5, 13):
        t = (y - 5) / 7
        half = 3 + t * 6.5
        for x in range(int(cx - half), int(cx + half) + 1):
            u = (x - (cx - half)) / (2 * half)
            put(x, y, RED if u < 0.5 else RED_M if u < 0.85 else RED_D)
        put(int(cx - half) - 1, y, OUT)
        put(int(cx + half) + 1, y, OUT)
    for x in range(int(cx - 4), int(cx + 5)):
        put(x, 4, OUT)
    for y in range(0, 4):
        for x in range(22, 26):
            put(x, y, IRON if (x, y) not in ((22, 0), (25, 0)) else KEY)
    put(23, 1, IRON_L)
    # ---- stone plinth (y 80-95) with the keeper's door, centred on cell column 1 (x 16-31)
    for y in range(81, 95):
        for x in range(5, 43):
            course = (y - 81) // 4
            joint = (x + (course % 2) * 4) % 8 == 0 or (y - 81) % 4 == 0
            c = STONE_D if joint else STONE_L if x < 20 else STONE
            put(x, y, c)
    for x in range(5, 43):
        put(x, 80, OUT)
        put(x, 95, OUT)
    for y in range(80, 96):
        put(4, y, OUT)
        put(43, y, OUT)
    # door: arched, dark wood, opening on the bottom edge of the middle cell
    for y in range(82, 96):
        for x in range(19, 29):
            arch = y >= 84 or 21 <= x <= 26
            if arch:
                put(x, y, DOOR if x < 26 else DOOR_D)
        put(18, y, OUT)
        put(29, y, OUT)
    for x in range(19, 29):
        put(x, 82 if 21 <= x <= 26 else 84, OUT)
    put(26, 89, (230, 200, 90))  # handle
    im.save(os.path.join(HERE, "lighthouse.png"))
    big = im.resize((W * 4, H * 4), Image.NEAREST)
    big.save(os.path.join(HERE, "lighthouse_preview.png"))
    print("lighthouse.png", im.size)


if __name__ == "__main__":
    main()

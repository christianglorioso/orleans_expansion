"""Own art: the bayou's working boats, drawn over open water (overlays).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_boats.py
writes boats.png (16x16 cells, magenta = transparent) and boats_preview.png:
    trawler  cells (0-3, 0-1)  a Gulf shrimp trawler: white hull, red boot stripe, wheelhouse aft, mast with
                               outrigger booms and green nets
    airboat  cells (4-6, 0-1)  a swamp airboat: flat aluminium hull, raised seat, caged fan at the stern
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
OUT = (40, 40, 48)
HULL, HULL_D = (240, 238, 228), (190, 188, 180)
STRIPE, STRIPE_D = (196, 60, 48), (140, 40, 36)
DECK, DECK_D = (176, 132, 88), (130, 96, 62)
CABIN, CABIN_D, GLASS = (232, 228, 214), (180, 176, 164), (120, 170, 196)
MAST, NET, NET_D, FLOAT = (96, 80, 66), (92, 140, 96), (60, 100, 70), (232, 120, 60)
ALU, ALU_L, ALU_D = (176, 184, 190), (214, 220, 224), (120, 128, 136)
FAN, CAGE, SEAT = (60, 62, 70), (150, 156, 162), (52, 86, 140)
WAKE = (214, 232, 236)


def main():
    im = Image.new("RGB", (7 * 16, 2 * 16), KEY)
    px = im.load()

    def put(x, y, c):
        if 0 <= x < im.width and 0 <= y < im.height:
            px[x, y] = c

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                put(x, y, c)

    # ---------------- trawler (64 x 32, cells 0-3 x 0-1), bow to the right: compact, so it costs few tiles
    for x in range(4, 61):
        bow = max(0, x - 50)               # the bow rises and narrows
        top, bottom = 16 - bow // 3, 28 - bow // 2
        rect(x, top, x, top + 2, DECK if x % 6 else DECK_D)        # deck
        rect(x, top + 3, x, bottom - 4, HULL if x < 56 else HULL_D)  # topsides
        rect(x, bottom - 3, x, bottom - 2, STRIPE if x % 9 else STRIPE_D)
        rect(x, bottom - 1, x, bottom, OUT)
        put(x, top - 1, OUT)
    rect(3, 15, 3, 28, OUT)
    for x in range(8, 58, 5):  # a little wake along the waterline
        put(x, 30, WAKE)
        put(x + 1, 31, WAKE)
    # wheelhouse aft
    rect(8, 4, 21, 15, OUT)
    rect(9, 5, 20, 14, CABIN)
    rect(9, 12, 20, 14, CABIN_D)
    rect(11, 7, 13, 9, GLASS)
    rect(16, 7, 18, 9, GLASS)
    rect(7, 2, 22, 4, STRIPE)              # roof
    rect(7, 1, 22, 1, OUT)
    # mast amidships with outrigger booms raised in a V, short nets at the tips
    mx = 41
    rect(mx, 1, mx + 1, 15, MAST)
    rect(mx - 1, 0, mx + 2, 0, OUT)
    for i in range(14):
        put(mx - 1 - i, 9 - (i * 2) // 3, MAST)
        put(mx + 2 + i, 9 - (i * 2) // 3, MAST)
    for bx in (mx - 14, mx + 15):
        for y in range(1, 9):
            for x in range(bx - 2, bx + 3):
                if (x + y) % 2 == 0:
                    put(x, y, NET if y < 6 else NET_D)
        put(bx, 9, FLOAT)
    # ---------------- airboat (48 x 32) at x 64
    X = 64
    for x in range(X + 2, X + 46):
        rect(x, 22, x, 23, ALU_L)
        rect(x, 24, x, 27, ALU if x < X + 40 else ALU_D)
        put(x, 28, OUT)
        put(x, 21, OUT)
    rect(X + 1, 21, X + 1, 28, OUT)
    rect(X + 46, 22, X + 46, 27, OUT)
    for x in range(X + 6, X + 42, 4):
        put(x, 29, WAKE)
    # raised seat
    rect(X + 22, 12, X + 29, 20, OUT)
    rect(X + 23, 13, X + 28, 15, SEAT)
    rect(X + 24, 16, X + 27, 20, ALU_D)
    # caged fan at the stern: a round guard with spokes and a dark propeller blur behind it
    cx, cy, r = X + 10, 11, 9
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= (r - 1) ** 2:
                put(x, y, FAN if (x + y) % 3 else ALU_D)
            elif d2 <= (r + 0.6) ** 2:
                put(x, y, CAGE)
    for i in range(-r, r + 1):  # spokes
        put(cx + i, cy, CAGE)
        put(cx, cy + i, CAGE)
    rect(cx - 1, cy - 1, cx + 1, cy + 1, ALU_L)  # hub
    rect(cx + r - 1, 17, cx + r + 1, 21, ALU_D)  # the fan's mount
    im.save(os.path.join(HERE, "boats.png"))
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(os.path.join(HERE, "boats_preview.png"))
    print("boats.png", im.size)


if __name__ == "__main__":
    main()

"""Own art: a railed wooden road bridge for the Orleans towns and routes (not the Olivine pier planks).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_bridge.py
writes bridge.png and bridge_preview.png; magenta = transparent (the water shows through around the rails).

Cells (x, y), 16x16 each:
  east-west bridge, 3 wide x 4 tall:  columns 0 left end / 1 middle (repeats) / 2 right end;
      rows 0 north rail, 1-2 deck (walkable; planks run north-south), 3 south rail
  north-south bridge, 4 wide x 3 tall, at x 3-6: columns 3 west rail, 4-5 deck (planks run east-west),
      6 east rail; rows 0 north end / 1 middle (repeats) / 2 south end
The deck cells are opaque; the rail cells are drawn over whatever is beneath (overlays).
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
PLANK, PLANK_L, PLANK_D = (156, 118, 80), (182, 142, 98), (108, 78, 52)
SEAM = (84, 60, 42)
RAIL, RAIL_L = (98, 70, 48), (140, 104, 70)
POST = (78, 56, 40)
OUT = (52, 40, 34)


def main():
    W, H = 7 * 16, 4 * 16
    im = Image.new("RGB", (W, H), KEY)
    px = im.load()

    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = c

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                put(x, y, c)

    # ================= east-west bridge (cells 0-2 x, 0-3 y): 48 x 64 px
    # deck: rows 1-2 (y 16-47), planks running north-south (vertical boards 4 px wide)
    for x in range(0, 48):
        for y in range(16, 48):
            # boards repeat every 8 px, so the deck reuses the same few 8x8 tiles
            c = PLANK_L if x % 8 < 3 else PLANK if x % 8 < 7 else SEAM
            if x % 8 == 3:
                c = SEAM
            if y % 8 == 2 and x % 4 == 1:
                c = SEAM  # nails over the joists
            put(x, y, c)
    # north rail (row 0): a stringer beam along the deck edge, balusters, the handrail
    rect(0, 12, 47, 15, RAIL)      # stringer
    rect(0, 12, 47, 12, RAIL_L)
    rect(0, 4, 47, 6, RAIL)        # handrail
    rect(0, 4, 47, 4, RAIL_L)
    for x in range(2, 48, 8):      # balusters (every 8 px: repeating tiles)
        rect(x, 7, x + 1, 11, POST)
    # south rail (row 3): the stringer under the deck edge, balusters, handrail, nothing below
    rect(0, 48, 47, 51, RAIL)
    rect(0, 51, 47, 51, OUT)
    for x in range(2, 48, 8):
        rect(x, 52, x + 1, 56, POST)
    rect(0, 57, 47, 59, RAIL)
    rect(0, 57, 47, 57, RAIL_L)
    rect(0, 60, 47, 60, OUT)
    # end posts where the bridge meets the bank (left end: x 0-3, right end: x 44-47), on both rails
    for x0 in (0, 44):
        rect(x0, 2, x0 + 3, 15, POST)
        rect(x0, 2, x0 + 3, 2, RAIL_L)
        rect(x0, 48, x0 + 3, 61, POST)
        rect(x0, 48, x0 + 3, 48, RAIL_L)
        rect(x0, 61, x0 + 3, 61, OUT)
    # ================= north-south bridge (cells 3-6 x, 0-2 y): x 48-111, y 0-47
    X = 48
    for x in range(X + 16, X + 48):
        for y in range(0, 48):
            c = PLANK_L if y % 8 < 3 else PLANK if y % 8 < 7 else SEAM
            if y % 8 == 3:
                c = SEAM
            if x % 8 == 2 and y % 4 == 1:
                c = SEAM
            put(x, y, c)
    # west rail (cell 3): stringer at x 60-63, balusters, handrail at x 52-54
    rect(X + 12, 0, X + 15, 47, RAIL)
    rect(X + 15, 0, X + 15, 47, RAIL_L)
    for y in range(2, 48, 8):
        rect(X + 7, y, X + 11, y + 1, POST)
    rect(X + 4, 0, X + 6, 47, RAIL)
    rect(X + 4, 0, X + 4, 47, RAIL_L)
    rect(X + 3, 0, X + 3, 47, OUT)
    # east rail (cell 6): mirror
    rect(X + 48, 0, X + 51, 47, RAIL)
    rect(X + 48, 0, X + 48, 47, RAIL_L)
    for y in range(2, 48, 8):
        rect(X + 52, y, X + 56, y + 1, POST)
    rect(X + 57, 0, X + 59, 47, RAIL)
    rect(X + 59, 0, X + 59, 47, RAIL_L)
    rect(X + 60, 0, X + 60, 47, OUT)
    # end posts at the north (y 0-3) and south (y 44-47) ends
    for y0 in (0, 44):
        rect(X + 2, y0, X + 15, y0 + 3, POST)
        rect(X + 48, y0, X + 61, y0 + 3, POST)
        rect(X + 2, y0, X + 15, y0, RAIL_L)
        rect(X + 48, y0, X + 61, y0, RAIL_L)
    im.save(os.path.join(HERE, "bridge.png"))
    im.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(HERE, "bridge_preview.png"))
    print("bridge.png", im.size)


if __name__ == "__main__":
    main()

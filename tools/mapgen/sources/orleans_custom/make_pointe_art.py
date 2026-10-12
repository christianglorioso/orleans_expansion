"""Own art for Pointe Rouge, the state capital: the art-deco Capitol, the refinery, the rail yard, the riverfront
boathouse gym and the two river bridges.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_pointe_art.py
writes pointe_*.png next to this script (16x16 cells, magenta = transparent) and pointe_preview.png.

The pieces are drawn to be cheap in a 512-tile secondary: every building is mirror-symmetric about a tile
boundary (the right half is the left half flipped, which the tileset composer stores once) and the repeating
parts (tower floors, tank walls, truss bays, rails) repeat on an 8-pixel grid so identical tiles collapse.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)

# ---------------------------------------------------------------- shared palette
# Two colour families, each exactly one 15-colour palette, so the art packs into the tileset's 7 palettes without
# squeezing anything. Buildings, industry, bridges and benches use family A (Brick City's stone, roofs, windows
# and bricks, plus the Capitol's gold); planting uses family G (Ekat's greens, flower colours from the Pokemon
# Center's palette, a stone kerb and soil). A piece never mixes the two.
hexc = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
K = hexc("303850")          # outline (Brick City's darkest roof blue)
S1 = hexc("d0d0b8")         # limestone, lit (Brick City stone trim)
S2 = hexc("b0b090")         # limestone
S3 = hexc("989878")         # limestone, shade
S4 = hexc("584850")         # deep shade
WHITE = hexc("f8f8f8")
W1 = hexc("404868")         # window
W2 = hexc("a8c0e0")         # window glint
G1 = hexc("e8c058")         # gold
G2 = hexc("c88058")         # bronze (Brick City's warm brick highlight)
GR1 = hexc("d0d8e8")        # greys: tanks, roofs, rails, gravel
GR2 = hexc("808890")
GR3 = hexc("606068")
RED = hexc("905850")        # Pointe Rouge red (Brick City's brick red)
RED_D = hexc("805048")
TIN1 = hexc("808890")       # slate roof, bridge steel
TIN2 = hexc("606068")
TIN3 = hexc("404868")
BROWN = hexc("805048")      # doors, sleepers, bench wood
FAMILY_A = [K, W1, S4, GR3, GR2, S3, S2, S1, GR1, W2, WHITE, BROWN, RED, G2, G1]
LEAF0, LEAF1, LEAF2, LEAF3 = hexc("283828"), hexc("406040"), hexc("608058"), hexc("78a068")  # Ekat's greens
FLOWERS = [hexc("c84050"), G1, WHITE, hexc("60a8e8"), hexc("f8b880"), hexc("d86860"), hexc("e89070")]
FAMILY_G = [LEAF0, LEAF1, LEAF2, LEAF3] + FLOWERS + [S1, S3, BROWN, K]
R1, R2 = GR1, GR2
T1, T2, T3, T4 = WHITE, GR1, GR2, GR3
ST1, ST2, ST3 = TIN1, TIN2, TIN3
CO1, CO2 = S1, S2
WOOD1, WOOD2 = WHITE, S1
GRAVEL1, GRAVEL2 = GR2, GR3
TIE, RAIL, RAIL_D = BROWN, GR1, GR3
FLAME1, FLAME2 = G1, RED


class Canvas:
    def __init__(self, cw, ch):
        self.w, self.h = cw * 16, ch * 16
        self.im = Image.new("RGB", (self.w, self.h), KEY)
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def get(self, x, y):
        return self.px[x, y] if 0 <= x < self.w and 0 <= y < self.h else KEY

    def outline_cells(self, c=K):
        """Outline each 16x16 cell on its own (pieces that repeat or meet other pieces, like bridge parts):
        transparent pixels reachable from the cell's top or bottom edge that touch art in the same cell."""
        for cy in range(0, self.h, 16):
            for cx in range(0, self.w, 16):
                inside = lambda x, y: cx <= x < cx + 16 and cy <= y < cy + 16
                outside, stack = set(), [(x, y) for x in range(cx, cx + 16) for y in (cy, cy + 15)]
                while stack:
                    x, y = stack.pop()
                    if (x, y) in outside or not inside(x, y) or self.get(x, y) != KEY:
                        continue
                    outside.add((x, y))
                    stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                hits = [(x, y) for x, y in outside if any(inside(x + dx, y + dy) and self.get(x + dx, y + dy) not in (KEY, c)
                                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
                for x, y in hits:
                    self.put(x, y, c)

    def outline(self, c=K, region=None, outer_only=False):
        """Draw an outline on transparent pixels touching art (4-neighbourhood). outer_only: only on the
        silhouette (transparent pixels reachable from the canvas edge), so holes in a lattice stay open."""
        x0, y0, x1, y1 = region or (0, 0, self.w - 1, self.h - 1)
        outside = None
        if outer_only:
            outside = set()
            stack = [(x, y) for x in range(self.w) for y in (0, self.h - 1)] + \
                [(x, y) for y in range(self.h) for x in (0, self.w - 1)]
            while stack:
                x, y = stack.pop()
                if (x, y) in outside or not (0 <= x < self.w and 0 <= y < self.h) or self.get(x, y) != KEY:
                    continue
                outside.add((x, y))
                stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        hits = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if outside is not None and (x, y) not in outside:
                    continue
                if self.get(x, y) == KEY and any(self.get(x + dx, y + dy) not in (KEY, c)
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    hits.append((x, y))
        for x, y in hits:
            self.put(x, y, c)

    def mirror(self):
        """Copy the left half onto the right, flipped (the art is drawn left half only)."""
        for y in range(self.h):
            for x in range(self.w // 2):
                self.px[self.w - 1 - x, y] = self.px[x, y]


# ---------------------------------------------------------------- the Capitol (10 x 14 cells)
def capitol():
    """Louisiana's art-deco Capitol: a tall limestone tower with vertical window bands and a gilded lantern,
    flanking chamber wings with flat roofs, a bronze-doored portico and a grand staircase. Drawn left half only
    and mirrored. Door cells: (4, 11) and (5, 11); steps: cells 3-6 of rows 12-13."""
    c = Canvas(10, 14)
    cx = 80  # centre line
    # --- lantern and dome (rows 0-1, x 64-95)
    c.rect(78, 0, 79, 3, G2)                     # finial
    c.put(78, 0, G1)
    for y in range(4, 13):                       # gilded dome
        half = min(8, 2 + (y - 4))
        c.rect(cx - half, y, cx - 1, y, G1 if y < 8 else G2 if y > 10 else G1)
        c.put(cx - half, y, G2)
    c.rect(72, 5, 74, 7, G1)        # glint
    c.rect(70, 13, 79, 14, S3)                   # drum cornice
    c.hline(69, 79, 13, S1)
    for y in range(15, 30):                      # octagonal lantern drum with tall arched openings
        c.rect(70, y, 79, y, S2)
    for x0 in (72, 77):
        c.rect(x0, 17, x0 + 1, 28, W1)
        c.put(x0, 16, S3)
        c.put(x0, 18, W2)
    c.vline(70, 15, 29, S3)
    c.rect(66, 30, 79, 31, S1)                   # lantern base step
    c.hline(66, 79, 31, S3)
    # --- crown: stepped shoulders with sculpted eagles (row 2, y 32-47)
    c.rect(62, 32, 79, 39, S2)
    c.hline(62, 79, 32, S1)
    c.rect(64, 34, 65, 39, S3)
    c.rect(68, 34, 69, 39, W1)
    c.rect(73, 34, 74, 39, W1)
    c.vline(62, 32, 39, S3)
    c.rect(56, 40, 79, 41, S1)                   # setback ledge
    c.hline(56, 79, 41, S3)
    for x0 in (56,):                             # corner eagle sculpture on the shoulder
        c.rect(x0, 36, x0 + 3, 39, S1)
        c.rect(x0 + 1, 34, x0 + 2, 35, S2)
        c.put(x0, 37, S3)
    # --- upper tower (y 42-71, x 56-103): narrower shaft
    def shaft(x0, y0, y1):
        """Window bands on an 8-px grid: pier 2 px, window 4 px, pier 2 px; a spandrel every 8 rows."""
        for y in range(y0, y1 + 1):
            for x in range(x0, cx):
                k, r = (x - x0) % 8, (y - y0) % 8
                if k in (0, 1, 6, 7):
                    col = S1 if k == 1 else S2
                elif r in (6, 7):
                    col = S3          # spandrel
                else:
                    col = W1 if not (k == 2 and r in (1, 2)) else W2
                c.put(x, y, col)
    shaft(56, 42, 71)
    c.vline(56, 42, 71, S3)
    # --- main tower shaft (y 72-151, x 48-111) with the corner piers
    c.rect(48, 70, 79, 71, S1)                   # second setback ledge
    c.hline(48, 79, 71, S3)
    shaft(56, 72, 151)
    c.rect(48, 72, 55, 151, S2)                  # corner pier
    c.rect(49, 72, 51, 151, S1)
    c.vline(55, 72, 151, S3)
    for y in range(76, 152, 16):                 # the pier's carved bands
        c.hline(48, 55, y, S3)
    c.rect(50, 66, 53, 69, S1)                   # pier-top statue
    c.rect(51, 64, 52, 65, S2)
    # --- wings: flat roof seen from above (y 104-127), x 0-47
    c.rect(0, 104, 47, 127, R1)
    c.rect(0, 104, 47, 105, S1)                  # parapet
    c.hline(0, 47, 106, S3)
    for x0 in range(6, 44, 16):                  # skylights over the chambers
        c.rect(x0, 111, x0 + 9, 120, W1)
        c.rect(x0 + 1, 112, x0 + 8, 119, W2)
        c.rect(x0 + 1, 116, x0 + 8, 116, W1)
        c.vline(x0 + 4, 112, 119, W1)
    c.rect(0, 122, 47, 127, R2)
    c.vline(0, 104, 127, S3)
    # --- wing facades (y 128-191): cornice, two storeys of tall windows between pilasters, base course
    c.rect(0, 128, 47, 135, S1)
    c.hline(0, 47, 134, S3)
    for x in range(2, 48, 4):                    # dentils
        c.put(x, 135, S3)
    c.rect(0, 136, 47, 183, S2)
    for x0 in range(0, 48, 16):
        c.rect(x0, 136, x0 + 3, 183, S1)         # pilaster
        c.vline(x0 + 3, 136, 183, S3)
        for wy0, wy1 in ((140, 155), (162, 179)):
            c.rect(x0 + 6, wy0, x0 + 13, wy1, W1)
            c.rect(x0 + 7, wy0 + 1, x0 + 8, wy0 + 3, W2)
            c.hline(x0 + 6, x0 + 13, wy0 + 8, S3)   # transom
            c.rect(x0 + 5, wy1 + 1, x0 + 14, wy1 + 2, S3)  # sill
    c.rect(0, 184, 47, 191, S3)
    c.hline(0, 47, 184, S4)
    for x in range(4, 48, 8):
        c.vline(x, 186, 190, S4)
    c.vline(0, 128, 191, S4)
    # --- central portico under the tower (x 48-111, y 152-191)
    c.rect(48, 152, 79, 159, G2)                 # bronze frieze
    c.hline(48, 79, 152, G1)
    for x in range(50, 80, 4):
        c.put(x, 155, G1)
        c.put(x + 1, 156, G1)
    c.hline(48, 79, 159, K)
    c.rect(48, 160, 79, 191, S4)                 # recessed porch
    for x0 in (50, 62):                          # columns
        c.rect(x0, 160, x0 + 5, 191, S2)
        c.rect(x0 + 1, 160, x0 + 2, 191, S1)
        c.vline(x0 + 5, 160, 191, S3)
        c.rect(x0 - 1, 160, x0 + 6, 161, S1)     # capital
    c.rect(70, 168, 79, 191, G2)                 # the bronze doors (door cells 4/5 of row 11)
    c.rect(71, 170, 79, 191, K)
    c.rect(72, 171, 79, 190, G2)
    c.rect(73, 172, 76, 178, G1)
    c.rect(73, 181, 76, 188, G1)
    c.hline(70, 79, 166, G1)                     # transom grille
    c.hline(70, 79, 167, K)
    # --- terrace before the wings (row 12, y 192-207): balustrade on a plinth
    c.rect(0, 192, 47, 207, S2)
    c.hline(0, 47, 192, S1)
    for x in range(2, 48, 4):
        c.rect(x, 195, x + 1, 201, S1)
        c.vline(x + 1, 196, 201, S3)
    c.hline(0, 47, 194, S3)
    c.rect(0, 202, 47, 207, S3)
    c.hline(0, 47, 202, S1)
    c.hline(0, 47, 207, S4)
    c.vline(0, 192, 207, S4)
    # --- grand staircase (cells 3-6, rows 12-13): treads and risers, cheek walls with urns
    for y in range(192, 224):
        r = (y - 192) % 4
        c.rect(52, y, 79, y, S1 if r == 0 else S2 if r in (1, 2) else S3)
    c.rect(48, 188, 51, 223, S3)                 # cheek wall
    c.vline(48, 188, 223, S4)
    c.rect(49, 186, 51, 188, S1)
    c.mirror()
    c.outline(K)
    return c.im


# ---------------------------------------------------------------- refinery pieces
def tank():
    """A white crude tank (3x3 cells) with a red band; mirrored about its middle."""
    c = Canvas(3, 3)
    cx, w = 24, 22  # half width
    # roof: an ellipse seen from above
    for y in range(3, 17):
        t = (y - 10) / 7.5
        half = int(w * (1 - t * t) ** 0.5) if abs(t) < 1 else 0
        for x in range(cx - half, cx):
            c.put(x, y, T1 if y < 9 else T2)
    for x in range(cx - 4, cx):                   # roof hatch
        c.put(x, 8, T3)
        c.put(x, 9, T4)
    # wall
    for y in range(10, 44):
        top = 10 if True else 0
        for x in range(cx - w, cx):
            u = (x - (cx - w)) / w
            col = T2 if u < 0.15 else T1 if u < 0.7 else T2
            if y >= 17 or ((y - 10) / 7.5) ** 2 + ((x - cx + 0.5) / w) ** 2 > 1:
                c.put(x, y, col)
    for y in range(17, 44):                       # wall seams on the 8-px grid
        for x in range(cx - w + 6, cx, 8):
            c.put(x, y, T3)
    for y in range(28, 33):                       # the red band
        for x in range(cx - w, cx):
            c.put(x, y, RED if y < 32 else RED_D)
    for y in range(40, 44):                       # base shading
        for x in range(cx - w, cx):
            c.put(x, y, T3 if y < 43 else T4)
    for x in range(cx - w, cx):                   # rim where wall meets roof
        y = 17 if x < cx - w + 3 else 17
        c.put(x, 17, T3)
    c.mirror()
    c.outline(K)
    return c.im


def column(cells_high=7):
    """A distillation column (1 cell wide): a steel cylinder with platform rings every 32 px and a cap."""
    c = Canvas(1, cells_high)
    for y in range(6, c.h - 2):
        for x in range(2, 14):
            u = (x - 2) / 12
            c.put(x, y, T1 if u < 0.3 else T2 if u < 0.7 else T3)
    for y in range(3, 7):                          # domed cap
        half = 2 + (y - 3) * 2
        c.rect(8 - half, y, 7 + half, y, T2)
    c.rect(7, 0, 8, 2, T4)                         # vent
    for y in range(20, c.h - 8, 32):               # platform with railing
        c.rect(0, y, 15, y + 1, T4)
        c.hline(0, 15, y - 3, T3)
        c.put(0, y - 2, T3)
        c.put(15, y - 2, T3)
    for y in range(8, c.h - 2):                    # ladder
        if y % 3 == 0:
            c.hline(11, 13, y, T4)
    c.vline(11, 8, c.h - 3, T4)
    c.vline(13, 8, c.h - 3, T4)
    c.rect(1, c.h - 3, 14, c.h - 1, T4)            # base
    c.outline(K)
    return c.im


def flare(cells_high=7):
    """The flare stack: a thin red-and-white stack with a flame at the top (1 cell wide)."""
    c = Canvas(1, cells_high)
    for y in range(10, c.h - 1):
        band = ((y - 10) // 8) % 2
        c.rect(5, y, 10, y, RED if band == 0 else T1)
        c.put(10, y, RED_D if band == 0 else T3)
    c.rect(4, c.h - 3, 11, c.h - 1, T4)
    # flame
    for y, (a, b, col) in enumerate([(7, 8, FLAME1), (6, 9, FLAME1), (6, 9, FLAME2), (5, 10, FLAME2), (5, 10, FLAME1),
                                     (6, 10, FLAME2), (6, 9, FLAME1), (5, 10, FLAME2), (6, 9, FLAME2), (6, 9, RED)]):
        c.rect(a, y, b, y, col)
    c.rect(7, 3, 8, 6, S1)
    c.outline(K)
    return c.im


def refinery():
    """The refinery's process house (6 x 6 cells): a corrugated-steel hall with a flat roof, a strip of windows,
    a roll-up door and the personnel door at (2, 5); mirrored except the roll-up door and the sign."""
    c = Canvas(6, 6)
    W = c.w
    # roof (rows 0-1, y 4-31): flat metal roof with vents
    c.rect(0, 4, W // 2 - 1, 31, R1)
    c.hline(0, W // 2 - 1, 4, T1)
    for x in range(0, W // 2, 8):
        c.vline(x + 4, 6, 29, R2)
    for x0 in (10, 30):                            # roof vents
        c.rect(x0, 10, x0 + 7, 17, T3)
        c.rect(x0 + 1, 11, x0 + 6, 13, T1)
        c.hline(x0, x0 + 7, 17, T4)
    c.rect(0, 28, W // 2 - 1, 31, R2)
    # wall (rows 2-5, y 32-95): corrugated steel, vertical ribs on a 4-px grid
    for y in range(32, 96):
        for x in range(0, W // 2):
            c.put(x, y, T2 if x % 4 in (0, 1) else T1 if x % 4 == 2 else T3)
    c.rect(0, 32, W // 2 - 1, 35, T4)              # eave
    c.hline(0, W // 2 - 1, 32, T3)
    for x0 in range(0, W // 2, 16):                # clerestory windows
        c.rect(x0 + 3, 42, x0 + 12, 49, W1)
        c.rect(x0 + 4, 43, x0 + 6, 44, W2)
        c.hline(x0 + 3, x0 + 12, 50, T4)
    c.rect(0, 58, W // 2 - 1, 61, RED)             # red stripe
    c.hline(0, W // 2 - 1, 61, RED_D)
    c.rect(0, 92, W // 2 - 1, 95, T4)              # plinth
    c.mirror()
    # personnel door at cell (2, 5): x 32-47, y 80-95
    c.rect(35, 70, 44, 95, K)
    c.rect(36, 71, 43, 95, GR3)
    c.rect(37, 73, 42, 79, W2)
    c.put(42, 86, G1)
    c.rect(33, 66, 46, 69, T4)                     # canopy
    c.hline(33, 46, 66, T3)
    # roll-up loading door, right side (cells 4-5)
    c.rect(66, 64, 89, 95, K)
    for y in range(65, 95):
        c.rect(67, y, 88, y, T3 if y % 3 else T4)
    c.rect(66, 62, 89, 63, RED_D)
    c.outline(K)
    return c.im


def pipe_rack():
    """A pipe rack (cells): (0,0) two pipes running east-west on a steel trestle (repeats),
    (1,0) the rack's end, the pipes turning down into the ground."""
    c = Canvas(2, 1)
    for x0 in (0, 16):
        c.rect(x0 + 6, 4, x0 + 7, 15, GR3)          # trestle leg
        c.hline(x0, x0 + 15, 3, GR3)                 # cross beam
    for y0 in (5, 9):                                # the pipes
        c.hline(0, 23, y0, WHITE)
        c.hline(0, 23, y0 + 1, GR1)
        c.hline(0, 23, y0 + 2, GR2)
    for x0 in (20, 24):                              # turning down at the end
        c.rect(x0, 5, x0 + 2, 15, GR1)
        c.vline(x0, 5, 15, WHITE)
        c.vline(x0 + 2, 5, 15, GR2)
    c.hline(4, 4, 5, GR2)
    c.outline(K)
    return c.im


# ---------------------------------------------------------------- rail yard
def rails():
    """Rail pieces (cells): (0,0) track east-west on ballast, (1,0) its west end with a buffer stop,
    (2,0) east end buffer, (3,0)-(5,0) a black tank car standing on the track (3 cells)."""
    c = Canvas(6, 1)

    def track(x0):
        for y in range(2, 14):
            for x in range(x0, x0 + 16):
                c.put(x, y, GRAVEL2 if (x * 3 + y * 5) % 8 < 2 else GRAVEL1)
        for x in range(x0 + 1, x0 + 16, 4):       # ties
            c.rect(x, 3, x + 1, 12, TIE)
        for y in (5, 10):                          # rails
            c.hline(x0, x0 + 15, y, RAIL)
            c.hline(x0, x0 + 15, y + 1, RAIL_D)
    for i in range(6):
        track(i * 16)
    # buffer stops: a red-and-white beam on two posts
    for x0, side in ((16, 1), (32, -1)):
        bx = x0 + (3 if side == 1 else 9)
        c.rect(bx, 2, bx + 3, 14, RED)
        c.rect(bx, 6, bx + 3, 8, T1)
        c.vline(bx + (0 if side == 1 else 3), 2, 14, K)
    # tank car over the track (cells 3-5): black cylinder with a dome and walkway
    x0 = 48
    for y in range(1, 13):
        for x in range(x0 + 2, x0 + 46):
            u = (y - 1) / 11
            c.put(x, y, GR3 if u < 0.3 else K if u < 0.8 else K)
    c.rect(x0 + 20, 0, x0 + 27, 2, GR3)   # dome
    c.rect(x0 + 2, 6, x0 + 45, 6, GR2)   # walkway line
    for xw in (x0 + 6, x0 + 14, x0 + 34, x0 + 42):  # wheels on the rails
        c.rect(xw - 2, 12, xw + 2, 15, K)
        c.put(xw, 13, RAIL)
    c.rect(x0 + 1, 3, x0 + 1, 11, K)
    c.rect(x0 + 46, 3, x0 + 46, 11, K)
    c.rect(x0 + 18, 8, x0 + 29, 10, RED)           # PR stripe
    return c.im


# ---------------------------------------------------------------- the riverfront boathouse gym (7 x 6 cells)
def boathouse():
    """Kingfisher's gym: a big white clapboard boathouse with a slate roof, a cupola with a kingfisher
    weathervane, shuttered windows, two cross-braced boat-bay doors and the door at (3, 5) (no gym sign). Mirrored about the
    middle of cell 3; the facade repeats per 16-px cell so it costs few tiles."""
    c = Canvas(7, 6)
    cx = 56
    # cupola (row 0) with the kingfisher weathervane
    c.rect(55, 0, 55, 3, K)
    c.rect(51, 1, 55, 2, W2)                       # the kingfisher (blue)
    c.put(50, 2, G1)                               # its beak
    c.rect(48, 6, 55, 7, TIN3)                     # cupola cap
    c.rect(50, 4, 55, 5, TIN2)
    c.rect(49, 8, 55, 15, WOOD1)
    c.rect(51, 9, 53, 13, W1)
    c.put(51, 9, W2)
    c.vline(49, 8, 15, WOOD2)
    # roof (y 14-43): hipped slate with standing seams on a 4-px grid
    for y in range(14, 44):
        inset = max(0, 10 - (y - 14))
        for x in range(inset, cx):
            c.put(x, y, TIN1 if x % 4 != 0 else TIN2)
    for y in range(40, 44):
        for x in range(0, cx):
            c.put(x, y, TIN2 if x % 4 else TIN3)
    c.hline(10, cx - 1, 14, GR1)                   # ridge cap
    c.rect(44, 22, 55, 35, WOOD1)                  # dormer
    c.rect(42, 19, 55, 21, TIN3)
    c.rect(47, 25, 55, 33, W1)
    c.rect(48, 26, 50, 28, W2)
    c.rect(0, 44, cx - 1, 47, RED)                 # fascia
    c.hline(0, cx - 1, 47, RED_D)
    # facade (rows 3-5, y 48-95): clapboard, a line every 4 px
    for y in range(48, 96):
        for x in range(0, cx):
            c.put(x, y, WOOD1 if y % 4 != 3 else WOOD2)
    for x0 in (0, 16, 32):                         # upper windows, one per cell, shuttered
        c.rect(x0 + 4, 51, x0 + 11, 60, K)
        c.rect(x0 + 5, 52, x0 + 10, 59, W1)
        c.rect(x0 + 5, 52, x0 + 6, 54, W2)
        c.hline(x0 + 5, x0 + 10, 55, WOOD1)
        c.vline(x0 + 7, 52, 59, WOOD1)
        c.rect(x0 + 2, 51, x0 + 3, 60, W1)          # shutters
        c.rect(x0 + 12, 51, x0 + 13, 60, W1)
        c.hline(x0 + 3, x0 + 12, 61, WOOD2)          # sill
    for x0 in (0, 16):                             # boat-bay doors (cells 0-1, rows 4-5)
        c.rect(x0 + 1, 66, x0 + 15, 95, BROWN)
        c.hline(x0, x0 + 15, 65, K)
        c.vline(x0 + 1, 66, 95, K)
        for i in range(14):
            c.put(x0 + 2 + i, 67 + i * 28 // 14, G2)
            c.put(x0 + 15 - i, 67 + i * 28 // 14, G2)
        for x in range(x0 + 4, x0 + 16, 4):
            c.vline(x, 66, 95, RED_D)
    c.vline(32, 65, 95, K)
    c.vline(0, 48, 95, WOOD2)
    # the door (centre of cell 3) under a small red hood; no gym sign (the owner removed those)
    c.rect(48, 72, cx - 1, 95, K)
    c.rect(50, 74, cx - 1, 95, BROWN)
    c.rect(51, 76, cx - 1, 83, W1)
    c.rect(52, 77, 53, 79, W2)
    c.rect(46, 68, cx - 1, 70, RED)
    c.hline(46, cx - 1, 70, RED_D)
    c.rect(0, 94, cx - 1, 95, S4)                  # sill on the pilings
    c.mirror()
    c.outline(K)
    return c.im


# ---------------------------------------------------------------- the river bridges
def truss_bridge():
    """The steel deck-truss bridge (east-west), cells:
        (0,0) north parapet over the water          (1,0) its concrete abutment pylon with a lantern (west end)
        (0,1) south parapet (deck behind it) and the deck's edge girder   (1,1) its pylon
        (0,2) truss bay under the deck (repeats; water shows through)   (1,2) a concrete pier under the truss
        (2,2) the abutment face; column 3 holds the east-end pieces (mirrored)
    The deck itself is the street paving (primary 1C1)."""
    c = Canvas(3, 3)

    def parapet(x0, y0):
        """Steel railing: top and bottom rails, a post every 8 px and one diagonal per bay."""
        c.hline(x0, x0 + 15, y0, ST1)
        c.hline(x0, x0 + 15, y0 + 1, ST2)
        c.hline(x0, x0 + 15, y0 + 7, ST2)
        c.hline(x0, x0 + 15, y0 + 8, ST3)
        for xb in (x0, x0 + 8):
            c.rect(xb, y0, xb + 1, y0 + 8, ST2)
            c.vline(xb, y0, y0 + 8, ST1)
            for k in range(5):
                c.put(xb + 2 + k, y0 + 2 + k, ST3)
                c.put(xb + 3 + k, y0 + 2 + k, ST3)

    def girder(x0, y0, h):
        c.rect(x0, y0, x0 + 15, y0 + h - 1, ST2)
        c.hline(x0, x0 + 15, y0, ST1)
        c.hline(x0, x0 + 15, y0 + h - 1, ST3)
        for x in range(x0 + 3, x0 + 16, 8):
            c.put(x, y0 + 2, ST3)
            if h > 5:
                c.put(x, y0 + h - 3, ST3)
    # north parapet over the water (row 0), then the girder along the deck's edge
    for x0 in (0, 16):
        parapet(x0, 3)
        girder(x0, 12, 4)
    for y in range(3, 12):  # the railing's panels are shaded solid, so water and bank never show through
        for x in range(0, 32):
            if c.get(x, y) == KEY:
                c.put(x, y, S4)

    # south parapet standing on the deck (row 1): deck colour behind it, then the girder face
    c.rect(0, 16, 31, 25, GR1)
    for x0 in (0, 16):
        parapet(x0, 17)
        girder(x0, 26, 6)

    # abutment pylons (west end, rows 0-1): concrete with a lantern on the north one
    for row_y in (0, 16):
        c.rect(16, row_y, 23, row_y + 15, CO1)
        c.vline(23, row_y, row_y + 15, CO2)
        c.hline(16, 23, row_y + 15, CO2)
        c.hline(16, 23, row_y, WHITE)
    c.rect(17, 1, 22, 4, GR3)
    c.rect(18, 2, 21, 3, G1)
    # truss bay under the deck (row 2): chords and a Warren V per 16 px
    y0 = 32
    for x0 in (0, 16, 32):
        c.rect(x0, y0, x0 + 15, y0 + 2, ST2)
        c.hline(x0, x0 + 15, y0, ST1)
        c.hline(x0, x0 + 15, y0 + 2, ST3)
        c.rect(x0, y0 + 11, x0 + 15, y0 + 13, ST2)
        c.hline(x0, x0 + 15, y0 + 13, ST3)
    for k in range(8):
        y = y0 + 3 + k
        for x in (k, 15 - k):
            c.put(x, y, ST1)
            c.put(x + (1 if x < 8 else -1), y, ST2)
    # the pier: a concrete column in front of the truss, into the water
    c.rect(20, y0 + 3, 27, y0 + 15, CO1)
    c.vline(27, y0 + 3, y0 + 15, CO2)
    c.hline(20, 27, y0 + 3, WHITE)
    c.hline(20, 27, y0 + 15, CO2)
    # abutment face (cell 2,2): solid concrete, laid over the river banks at both ends
    c.rect(32, y0, 47, y0 + 15, CO1)
    c.hline(32, 47, y0, WHITE)
    for y in range(y0 + 5, y0 + 16, 5):
        c.hline(32, 47, y, CO2)
    c.outline_cells(K)
    return with_mirrored_ends(c.im)


def deck_behind(c, x0, x1, y0, y1):
    """Fill what shows between a south parapet's bars with the deck (it stands on the deck, not over water)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if c.get(x, y) == KEY:
                c.put(x, y, GR1)


def with_mirrored_ends(im):
    """Add column 3: the east-end pieces, i.e. column 1 (rows 0-1) and cell (2, 2) mirrored."""
    out = Image.new("RGB", (64, im.height), KEY)
    out.paste(im, (0, 0))
    for (sx, sy) in ((1, 0), (1, 1), (2, 2)):
        cell = im.crop((sx * 16, sy * 16, sx * 16 + 16, sy * 16 + 16)).transpose(Image.FLIP_LEFT_RIGHT)
        out.paste(cell, (48, sy * 16))
    return out


def stone_bridge():
    """The stone arch bridge (east-west), cells:
        (0,0) north balustrade        (1,0) its end pier (west; mirrored for east)
        (0,1) south balustrade + deck edge   (1,1) its end pier
        (0,2),(1,2) the arch face over the water (two cells per arch, repeats)   (2,2) the abutment face
    The deck is the street paving."""
    c = Canvas(3, 3)
    for row_y in (0, 16):
        for x0 in (0, 16):
            top = row_y + (6 if row_y == 0 else 1)
            c.rect(x0, top, x0 + 15, top + 1, S1)      # handrail
            c.hline(x0, x0 + 15, top + 2, S3)
            for x in range(x0, x0 + 16, 4):         # balusters
                c.rect(x, top + 3, x + 1, top + 7, S2)
                c.put(x + 1, top + 4, S3)
            c.rect(x0, top + 8, x0 + 15, top + 9, S2)  # plinth
            c.hline(x0, x0 + 15, top + 9, S3)
        if row_y == 16:
            c.rect(0, 28, 31, 31, S3)                   # the bridge's side face below the south balustrade
            c.hline(0, 31, 31, S4)
    for row_y in (0, 16):                               # end piers with a cap
        c.rect(16, row_y, 23, row_y + 15, S2)
        c.rect(16, row_y, 23, row_y + 2, S1)
        c.vline(23, row_y, row_y + 15, S3)
        c.hline(16, 23, row_y + 3, S3)
    deck_behind(c, 0, 31, 16, 27)
    for y in range(9, 14):  # shadow between the north balusters, so water and bank never show through
        for x in range(0, 32):
            if c.get(x, y) == KEY:
                c.put(x, y, S4)
    # arch face: voussoirs around an opening that shows the water (transparent)
    y0 = 32
    c.rect(0, y0, 31, y0 + 15, S2)
    for x in range(0, 32):
        dx = (x - 15.5) / 13.5
        if abs(dx) < 1:
            ytop = y0 + 4 + int(9 * (1 - (1 - dx * dx) ** 0.5))
            for y in range(ytop, y0 + 16):
                c.put(x, y, KEY)
            c.put(x, ytop - 1, S3)
            c.put(x, ytop - 2, S1)
    for x in range(0, 32, 8):
        c.vline(x, y0, y0 + 2, S3)
    c.hline(0, 31, y0, S1)
    c.rect(32, y0, 47, y0 + 15, S2)                     # abutment face: solid masonry over the banks
    c.hline(32, 47, y0, S1)
    for y in range(y0 + 4, y0 + 16, 4):
        c.hline(32, 47, y, S3)
        for x in range(32 + (y // 4) % 2 * 4, 48, 8):
            c.vline(x, y - 3, y - 1, S3)
    c.outline_cells(K)
    return with_mirrored_ends(c.im)


def boat_dock():
    """The gym's small boat dock (3x2 cells), running east from the bank: planks laid north-south on a frame,
    posts at the corners, a cleat at the far end. Walkable; drawn over the water."""
    c = Canvas(3, 2)
    W_, H_ = c.w, c.h
    for x in range(0, W_):
        for y in range(1, H_ - 2):
            b = x % 4
            c.put(x, y, G2 if b == 0 else BROWN if b in (1, 2) else S4)
    c.hline(0, W_ - 1, 1, S4)                         # frame along the north edge
    c.rect(0, H_ - 3, W_ - 1, H_ - 2, S4)             # and the south edge
    c.rect(W_ - 3, 1, W_ - 1, H_ - 2, S4)             # the far end
    for x0, y0 in ((W_ - 4, 0), (W_ - 4, H_ - 4), (14, H_ - 4), (30, H_ - 4)):  # posts
        c.rect(x0, y0, x0 + 3, y0 + 3, GR3)
        c.put(x0 + 1, y0 + 1, GR2)
    c.rect(W_ - 9, 13, W_ - 6, 15, GR3)               # cleat
    c.outline(K)
    return c.im


# ---------------------------------------------------------------- street furniture and planting
def bench():
    """A slatted park bench (2 cells), seen from the front: wooden slats on black iron ends."""
    c = Canvas(2, 1)
    for y, col in ((3, G2), (4, BROWN), (6, G2), (7, BROWN), (10, G2), (11, RED_D)):
        c.hline(3, 28, y, col)
    for x in (2, 29):
        c.rect(x - 1, 2, x, 14, K)
    c.hline(1, 3, 14, K)
    c.hline(28, 30, 14, K)
    c.rect(4, 12, 27, 12, S4)          # shadow under the seat
    c.outline(K)
    return c.im


def flowerbed():
    """A formal flower bed (3x1 cells): a low stone kerb round soil, two rows of flowers with every flower its own
    colour along the row, clipped shrubs at the ends."""
    c = Canvas(3, 1)
    W_, H_ = c.w, c.h
    c.rect(1, 1, W_ - 2, H_ - 2, S1)                  # kerb
    c.hline(1, W_ - 2, H_ - 2, S3)
    c.rect(3, 3, W_ - 4, H_ - 4, BROWN)               # soil
    c.hline(3, W_ - 4, H_ - 4, LEAF0)
    k = 0
    for y, x_first in ((4, 8), (9, 10)):
        for x in range(x_first, W_ - 8, 5):
            col = FLOWERS[k % len(FLOWERS)]
            k += 1
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (2, 1), (0, -1)):
                c.put(x + dx, y + dy, col)
            c.put(x, y, WHITE if col != WHITE else G1)
            c.put(x + 1, y + 2, LEAF2)
    for x0 in (3, W_ - 7):                            # clipped shrubs at the ends
        c.rect(x0, 3, x0 + 3, H_ - 4, LEAF2)
        c.rect(x0 + 1, 4, x0 + 2, 5, LEAF3)
    c.outline(K)
    return c.im


MAGNOLIA_SNAP = {"103020": "283828", "286038": "406040", "408048": "406040", "587848": "608058", "78b070": "78a068",
                 "f8f8f0": "f8f8f8", "c8c8b8": "d0d0b8", "685858": "805048", "e8c878": "e8c058", "403830": "283828"}


def magnolia():
    """The region's magnolia (magnolia.png, 2x3), its colours snapped to ones the town already has."""
    im = Image.open(os.path.join(HERE, "magnolia.png")).convert("RGB")
    px = im.load()
    snap = {hexc(a): hexc(b) for a, b in MAGNOLIA_SNAP.items()}
    for y in range(im.height):
        for x in range(im.width):
            c = tuple((v >> 3) << 3 for v in px[x, y])
            if px[x, y] != KEY and c in snap:
                px[x, y] = snap[c]
    return im


# ---------------------------------------------------------------- the tackle shop, the old ice plant
def tackle_shop():
    """The bait and tackle shop (6x5 cells): a timber shack with a tin roof and a big painted fish on posts above
    it, a window full of rods, rods leaning by the wall, a net hung to dry, and the door at (1, 4). The walls and
    roof repeat on an 8-pixel grid so the shop costs few tiles."""
    c = Canvas(6, 5)
    # the fish sign on two posts (y 0-15)
    for px_ in (34, 60):
        c.rect(px_, 9, px_ + 1, 17, BROWN)
    for x in range(26, 61):
        t = (x - 26) / 34
        half = int(6 * (1 - (2 * t - 1) ** 2) ** 0.5)
        c.rect(x, 7 - half, x, 7 + half, W2)
        c.put(x, 7 + half, GR2)
    for i in range(7):                                   # the tail
        c.rect(61 + i, 7 - i, 61 + i, 7 + i, W2)
    c.rect(30, 5, 31, 6, K)                              # eye
    c.put(30, 5, WHITE)
    # roof (y 16-35): corrugated tin, ribs every 4 px
    for y in range(16, 36):
        for x in range(0, 96):
            c.put(x, y, GR1 if x % 4 in (0, 1) else GR2 if x % 4 == 2 else GR3)
    c.hline(0, 95, 16, WHITE)
    c.rect(0, 32, 95, 35, RED_D)                         # eave
    # timber walls (y 36-79): boards, a seam every 4 px
    for y in range(36, 80):
        for x in range(0, 96):
            c.put(x, y, G2 if y % 4 != 3 else BROWN)
    # the door (cell 1,4), boxed to the 16-px cell
    c.rect(18, 64, 29, 79, K)
    c.rect(19, 65, 29, 79, BROWN)
    c.rect(20, 66, 27, 71, W1)
    c.put(27, 74, G1)
    # shop window full of rods (cells 2-3 of rows 2-3)
    c.rect(36, 42, 59, 59, K)
    c.rect(37, 43, 58, 58, W1)
    for x in range(39, 58, 4):
        c.vline(x, 44, 57, BROWN)
        c.put(x, 44, G1)
    # rods leaning by the wall (cell 4) and a net hung to dry (cell 5)
    for x0 in (66, 70, 74):
        for k in range(24):
            c.put(x0 + k // 12, 79 - k, BROWN if k < 21 else K)
    for y in range(40, 64):
        for x in range(82, 94):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                c.put(x, y, GR2)
    c.hline(81, 94, 39, BROWN)
    c.outline(K)
    return c.im


def ice_plant():
    """The old ice plant (9x6 cells): a brick cold-storage block with a flat roof and two cooling fans, a row of
    small high windows, faded painted ICE lettering, insulated loading doors either side of the door at (4, 5),
    standing on a concrete loading dock. Mirrored about the middle (except the lettering)."""
    c = Canvas(9, 6)
    W_, cx = c.w, c.w // 2
    # roof (y 8-31): flat, with a cooling fan on each side
    c.rect(0, 8, cx - 1, 31, GR1)
    c.hline(0, cx - 1, 8, WHITE)
    c.rect(0, 28, cx - 1, 31, GR2)
    for y in range(12, 26):
        for x in range(24, 40):
            if (x - 31.5) ** 2 + (y - 18.5) ** 2 <= 42:
                c.put(x, y, GR3 if (x + y) % 3 else K)
    c.rect(31, 18, 32, 19, GR1)
    # brick facade (y 32-95): a brick course every 4 px, joints every 8 px, alternate courses offset by 4
    for y in range(32, 96):
        for x in range(0, cx):
            row = (y - 32) // 4
            mortar = y % 4 == 3 or (x + (4 if row % 2 else 0)) % 8 == 7
            c.put(x, y, BROWN if mortar else RED)
    c.rect(0, 32, cx - 1, 35, S3)                        # stone cornice
    c.hline(0, cx - 1, 32, S1)
    for x0 in range(4, cx, 16):                          # small high windows, one per cell
        c.rect(x0, 39, x0 + 7, 44, K)
        c.rect(x0 + 1, 40, x0 + 6, 43, W1)
        c.put(x0 + 1, 40, W2)
    c.hline(0, cx - 1, 61, GR2)                          # ammonia pipes along the wall
    c.hline(0, cx - 1, 62, GR3)
    c.rect(0, 84, cx - 1, 95, S2)                        # the concrete loading dock
    c.hline(0, cx - 1, 84, S1)
    c.hline(0, cx - 1, 95, S3)
    for x0 in (16, 40):                                  # insulated loading doors, a 16-px pair each side
        c.rect(x0, 64, x0 + 15, 83, RED_D)
        c.rect(x0 + 1, 65, x0 + 15, 83, WHITE)
        for y in range(69, 83, 5):
            c.hline(x0 + 1, x0 + 15, y, GR1)
    c.rect(0, 64, 1, 95, RED_D)
    # the door (cell 4, row 5): steel, up the dock's steps
    c.rect(cx - 6, 68, cx - 1, 95, K)
    c.rect(cx - 5, 69, cx - 1, 95, GR3)
    c.rect(cx - 3, 71, cx - 1, 77, W1)
    c.rect(cx - 8, 64, cx - 1, 66, S3)
    c.mirror()
    c.put(cx + 3, 82, G1)
    # faded painted ICE across the upper wall (centred, not mirrored)
    font = {"I": ["111", "010", "010", "010", "111"], "C": ["0111", "1000", "1000", "1000", "0111"],
            "E": ["1111", "1000", "1110", "1000", "1111"]}
    x = cx - 15
    for ch in "ICE":
        for r, row in enumerate(font[ch]):
            for k, bit in enumerate(row):
                if bit == "1":
                    c.rect(x + k * 2, 48 + r * 2, x + k * 2 + 1, 49 + r * 2, S1)
        x += len(font[ch][0]) * 2 + 3
    c.outline(K)
    return c.im


def quay():
    """The stone quay on the city bank (water to the east), two cells wide:
        (0,0) the quayside's edge, over the paving's east kerb: coping stones (the paving shows to the left)
        (1,0) the same with an iron mooring bollard (blocks)
        (4,0) the quay wall, over the river's bank piece: the wall's wet face dropping to the waterline
              (the water shows to the right)
        (2,0) stacked crates   (3,0) two barrels   (drawn over the paving)"""
    c = Canvas(5, 1)

    def coping(x0):
        for y in range(16):
            c.rect(x0 + 9, y, x0 + 15, y, S1)
            c.put(x0 + 9, y, S3)
            if y % 8 == 7:
                c.hline(x0 + 10, x0 + 15, y, S3)            # a joint every 8 px
    c.rect(26, 4, 30, 12, K)                             # the bollard (on the coping, drawn after the outline)
    c.rect(27, 5, 29, 11, GR3)
    c.rect(25, 4, 31, 5, K)
    c.put(27, 6, GR2)
    for (x0, y0, x1, y1) in ((33, 7, 46, 15), (35, 0, 44, 7)):  # crates
        c.rect(x0, y0, x1, y1, K)
        c.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, G2)
        for y in range(y0 + 1, y1):
            if (y - y0) % 3 == 0:
                c.hline(x0 + 1, x1 - 1, y, BROWN)
        c.hline(x0 + 1, x1 - 1, y0 + 1, S1)
    for bx in (50, 57):                                  # barrels
        for y in range(4, 16):
            half = 3 if y in (4, 15) else 4
            for x in range(bx + 4 - half, bx + 4 + half):
                c.put(x, y, G2 if x < bx + 3 else BROWN)
        for y in (7, 12):
            c.hline(bx, bx + 7, y, GR3)
        c.rect(bx + 1, 3, bx + 6, 4, RED_D)
    c.outline(K)
    bollard = [(x, y, c.get(x, y)) for x in range(25, 32) for y in range(3, 14) if c.get(x, y) != KEY]
    coping(0)                                            # copings and the wall face join their neighbours: no outline
    coping(16)
    for x, y, col in bollard:
        c.put(x, y, col)
    for y in range(16):                                  # (4,0) the wall's face
        c.put(64, y, S3)
        c.rect(65, y, 72, y, GR3 if y % 4 else K)
        c.put(73, y, K)
        c.rect(74, y, 75, y, W1)
    return c.im


def crane():
    """A small dockside jib crane (2x3 cells), painted yellow: a lattice mast on a concrete block, the jib
    reaching east with a hook on its cable, a counterweight at the back."""
    c = Canvas(2, 3)
    c.rect(2, 38, 17, 47, S2)                            # concrete base block
    c.hline(2, 17, 38, S1)
    c.hline(2, 17, 47, S3)
    c.rect(7, 8, 12, 38, G2)                             # the mast, a lattice of yellow steel
    c.vline(7, 8, 38, G1)
    for y in range(10, 38, 6):
        for k in range(5):
            c.put(8 + k, y + k, BROWN)
    c.rect(2, 4, 31, 8, G2)                              # the jib
    c.hline(2, 31, 4, G1)
    for x in range(4, 31, 4):
        c.put(x, 6, BROWN)
        c.put(x + 1, 7, BROWN)
    c.rect(0, 3, 5, 12, GR3)                             # counterweight
    c.rect(9, 0, 10, 4, G2)                              # the jib's tie
    c.vline(26, 9, 25, K)                                # cable and hook, a crate in the sling
    c.hline(23, 29, 25, GR3)
    c.rect(22, 27, 30, 36, G2)
    c.hline(22, 30, 27, G1)
    c.vline(22, 27, 36, G1)
    for x in (22, 26, 30):
        c.vline(x, 27, 36, BROWN)
    c.hline(22, 30, 31, BROWN)
    c.outline(K)
    return c.im


PIECES = {
    "pointe_crane.png": crane,
    "pointe_tackle.png": tackle_shop,
    "pointe_iceplant.png": ice_plant,
    "pointe_quay.png": quay,
    "pointe_capitol.png": capitol,
    "pointe_tank.png": tank,
    "pointe_column.png": column,
    "pointe_flare.png": flare,
    "pointe_refinery.png": refinery,
    "pointe_rails.png": rails,
    "pointe_pipes.png": pipe_rack,
    "pointe_gym.png": boathouse,

    "pointe_stonebridge.png": stone_bridge,
    "pointe_bench.png": bench,
    "pointe_dock.png": boat_dock,
    "pointe_flowerbed.png": flowerbed,
    "pointe_magnolia.png": magnolia,
}


def main():
    ims = {}
    fam = {hexc("%02x%02x%02x" % c) for c in FAMILY_A}, {hexc("%02x%02x%02x" % c) for c in FAMILY_G}
    for name, fn in PIECES.items():
        ims[name] = fn()
        ims[name].save(os.path.join(HERE, name))
        used = {c for c in ims[name].getdata() if c != KEY}
        if not (used <= fam[0] or used <= fam[1]):
            print(f"  {name}: colours outside one family: {sorted('%02x%02x%02x' % c for c in used - fam[0])}")
    # preview on swamp grass, 3x
    pad = 8
    W = sum(i.width for i in ims.values()) + pad * (len(ims) + 1)
    H = max(i.height for i in ims.values()) + 2 * pad
    out = Image.new("RGB", (W, H), (120, 160, 104))
    x = pad
    for im in ims.values():
        m = im.copy()
        mask = Image.eval(m.convert("RGB").point(lambda v: v), lambda v: v)
        px = m.load()
        for yy in range(m.height):
            for xx in range(m.width):
                if px[xx, yy] != KEY:
                    out.putpixel((x + xx, pad + yy), px[xx, yy])
        x += im.width + pad
    out.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(HERE, "pointe_preview.png"))
    print("wrote", ", ".join(ims), "and pointe_preview.png")


if __name__ == "__main__":
    main()

"""Own art for Crescent City (fantasy New Orleans), drawn to sit over any terrain as overlays.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_crescent_art.py
writes crescent_<family>.png (16x16 cells, magenta = transparent; one sheet per colour family, *_raw sheets for
opaque pieces placed as plain metatiles), crescent.json (piece -> sheet, cell rectangle, doors, passable cells;
read by tools/mapgen/crescent_tileset.py, which turns every piece into a prefab) and crescent_preview.png.

The tileset is tight (512 tiles): every piece is drawn on the 8 px tile grid so its tiles repeat (walls, roofs,
rails, decks every 8 px), symmetric pieces are drawn as a left half and mirrored (a flipped tile is a free copy),
and buildings are built from shared kits of tiles (identical tiles are stored once, whichever piece they're in):
the Creole facade kit (only the stucco carries a colour), the civic kit (ashlar, pier, cornice, window, glass
door) shared by the Battle Frontier, the downtown blocks and the metal warehouse; the crypt and the Conservation
Center reuse the gym's own column, door and frieze tiles. Measure a change by counting distinct 8x8 tiles (flips
included) over the placed pieces, or by composing the tileset into a scratch dir.
    tomb, tomb_box       whitewashed family tomb with pediment and cross (2x2); a low box tomb (2x1)
    crypt                the oldest crypt, 3x3: a small portico of the gym's tiles under its own weathered pediment
    vault                a wall of oven vaults, 3x2
    gym                  the Fifolet gym: a white marble temple-mausoleum, blue wisp lanterns, 7x6, door (3,4)
    ruin_a, ruin_b       roofless brick shells of the Drowned Ward (4x3, 3x3), standing in water or marsh
    ruin_door            ruin_a with a barred cellar door: the Blacksnake hideout, door (1,2)
    fence_<NSEW>         wrought-iron fence pieces, one per set of connections (N, S, E, W), from shared quarters
    bal_l/m/r, bal_fern  iron balcony railing over a townhouse's upper floor, one with a hanging fern
    stall                market stall: red-and-white awning (stall_top) over a produce counter (stall_base), 3x2
    fountain             tiered stone fountain in a round basin, 3x3; obelisk 1x3 (neither placed yet)
    hedge_l/m/r          clipped box hedge
    flowerbed            formal bed of mixed flowers, walkable (raw)
    walk_vl/vm/vr, walk_ht/hm/hb   dark boardwalk planks, walkable over water (raw)
    mailbox, bin, sign, generator  street furniture; the old generator at the end of Rotom's pier
    gazebo               the City Park bandstand, 4x4
    fbridge_l/r          a white railed footbridge, 2 wide (raw); rwalk_l/m/r a railed boardwalk, 3 wide (raw)
    easel                a painter's easel
    steamboat            the riverboat broadside, 7x3 (not placed); steamboat_ns the riverboat moored north-south, 3x7
    creole_<shop>        Creole townhouse facades (crescent_tileset.py stacks Brick City's slate roof on them as
                         house_<shop>), each with its trade's board on the gallery over the door
    wh_roof9/6 + wh_wall9/6    warehouse: tin roof over board siding (combos warehouse9/6); wh_wall9b/6b corrugated
                         metal with a sliding door (combos warehouse9b/6b), doors (1,2)
    fac_<facility>       the Battle Frontier: tower 5x5, dome 5x4, palace 5x3, arena 5x4, factory 5x3, pike 5x4,
                         pyramid 5x4 (doors shut until the post-game: no door cells)
    block_dept           the Department Store, 7x5, door (3,4); block_hall the Conservation Center, 9x5, door (4,4)
    trough               a drinking fountain for the Frontier plaza, 2x2; pot_sand a terracotta flower pot
    shrub_pot, flower_cart (2x1), barrel   street props
"""
import json
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
CLEAR = (0, 0, 0, 0)

# ---- colours. Every piece is snapped to one family of <= 15 colours taken from the city tileset's own palettes
# (Pokemon Center whites and blues, Brick City bricks, the dock's woods, the cypress greens), so the art adds
# almost no new colours and nothing gets squeezed.
h = lambda s: tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
FAMILY = {
    "stone": [h(c) for c in "c84050 b8c8e0 606078 404868 f8b880 e89070 98b0d8 60a8e8 d8e0e8 f8f8f8 d86860 808088 303850 608888 487070".split()],
    "brick": [h(c) for c in "505050 606068 303850 808890 484850 404868 805048 905850 d0d8e8 c88058 a8c0e0 989878 584850 406040 507060".split()],
    "wood": [h(c) for c in "d8c880 b8a058 785818 e8e098 404868 787880 908030 f8f0b8 c84050 f09038 689878 9068c8 303850 d86860".split()],
    "leaf": [h(c) for c in "303028 283828 686058 406040 507060 887868 689878 a09078 c84050 f0d048 f8f8f8 9068c8 e078b0 6890e0 f09038".split()],
    # the French Quarter's stucco (four colours and their shades), shutters, glass, white trim, iron
    "creole": [h(c) for c in "e8a8a0 c88078 f0d890 c8b060 a8c8e8 7898c0 b0d0a0 80a878 406040 507060 404868 98b0d8 f8f8f8 b8c8e0 303850".split()],
}
OUT = h("303850")
IRON, IRON_L, IRON_H = h("404868"), h("606078"), h("98b0d8")
W0, W1, W2, W3, W4, W5 = h("f8f8f8"), h("d8e0e8"), h("b8c8e0"), h("98b0d8"), h("808088"), h("606078")
STONE_D = h("404868")
CREAM, CREAM_D, CREAM_DD = h("d0d8e8"), h("989878"), h("808890")
BRICK_D, BRICK, BRICK_L, BRICK_H = h("805048"), h("905850"), h("c88058"), h("c88058")
MORTAR = h("584850")
DARK = h("303850")
RED_D, RED, RED_L = h("c84050"), h("c84050"), h("d86860")
GREEN_D, GREEN, GREEN_L = h("406040"), h("507060"), h("689878")
LEAF_D, LEAF, LEAF_M, LEAF_L = h("283828"), h("406040"), h("507060"), h("689878")
MOSS, MOSS_L = h("507060"), h("689878")
GRASS_D = h("689060")
WATER_D, WATER, WATER_L = h("487070"), h("608888"), h("b8c8e0")
SPRAY, SPRAY_L = h("d8e0e8"), h("f8f8f8")
WISP, WISP_L, WISP_D = h("60a8e8"), h("d8e0e8"), h("98b0d8")
WOOD_D, WOOD, WOOD_L = h("785818"), h("b8a058"), h("d8c880")
TRUNK, TRUNK_D = h("686058"), h("303028")
GOLD, GOLD_L = h("f8b880"), h("e89070")
YELLOW, ORANGE, PURPLE, PINK, BLUEF = h("f0d048"), h("f09038"), h("9068c8"), h("e078b0"), h("6890e0")
SLATE_D, SLATE = h("303850"), h("606078")


def snap(im, family, box=None):
    """Every opaque pixel (inside box) to the nearest colour of the family."""
    pal = FAMILY[family]
    px = im.load()
    W, H = im.size
    x0, y0, x1, y1 = box or (0, 0, W, H)
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = min(pal, key=lambda c: (c[0] - r) ** 2 * 3 + (c[1] - g) ** 2 * 4 + (c[2] - b) ** 2 * 2) + (255,)
    return im


class Sheet:
    def __init__(self, cols=16, rows=24):
        self.im = Image.new("RGBA", (cols * 16, rows * 16), CLEAR)
        self.cols, self.rows = cols, rows
        self.used = set()
        self.pieces = {}

    def place(self, name, art, doors=(), passable=(), comment=""):
        w, h = art.width // 16, art.height // 16
        for y in range(self.rows - h + 1):
            for x in range(self.cols - w + 1):
                cells = {(x + i, y + j) for i in range(w) for j in range(h)}
                if not cells & self.used:
                    self.used |= cells
                    self.im.alpha_composite(art, (x * 16, y * 16))
                    empty = [[i, j] for j in range(h) for i in range(w)
                             if art.crop((i * 16, j * 16, i * 16 + 16, j * 16 + 16)).getextrema()[3][1] == 0]
                    self.pieces[name] = {"x": x, "y": y, "w": w, "h": h, "doors": [list(d) for d in doors],
                                         "passable": [list(p) for p in passable], "empty": empty, "comment": comment}
                    return
        raise SystemExit(f"no room for {name}")


def canvas(w, h):
    im = Image.new("RGBA", (w * 16, h * 16), CLEAR)
    return im, ImageDraw.Draw(im)


def P(d, x, y, c):
    d.point((x, y), fill=c)


def outline(im, color=OUT, sides=(1, 1, 1, 1)):
    """Draw an outline round every opaque region (outside the shape)."""
    px = im.load()
    W, H = im.size
    edge = []
    for y in range(H):
        for x in range(W):
            if px[x, y][3]:
                continue
            for dx, dy, on in ((1, 0, sides[0]), (-1, 0, sides[1]), (0, 1, sides[2]), (0, -1, sides[3])):
                nx, ny = x + dx, y + dy
                if on and 0 <= nx < W and 0 <= ny < H and px[nx, ny][3] and px[nx, ny][:3] != color:
                    edge.append((x, y))
                    break
    for x, y in edge:
        px[x, y] = color + (255,)


# ------------------------------------------------------------------ cemetery
def tomb(body=W0, shade=W2, dark=W4, tablet=W3, roof=W1):
    im, d = canvas(2, 2)
    # cross on the apex
    d.rectangle([15, 0, 16, 6], fill=dark)
    d.rectangle([13, 2, 18, 3], fill=dark)
    # pediment
    d.polygon([(4, 13), (15, 4), (16, 4), (27, 13)], fill=roof)
    d.line([(4, 13), (15, 4)], fill=body)
    d.line([(16, 4), (27, 13)], fill=shade)
    d.polygon([(11, 12), (15, 8), (16, 8), (20, 12)], fill=shade)  # tympanum recess
    # cornice
    d.rectangle([2, 13, 29, 15], fill=body)
    d.line([(2, 15), (29, 15)], fill=shade)
    # body
    d.rectangle([4, 16, 27, 27], fill=body)
    d.rectangle([22, 16, 27, 27], fill=shade)  # side in shade
    d.line([(4, 16), (27, 16)], fill=dark)
    # marble tablet with lettering
    d.rectangle([9, 18, 19, 25], fill=tablet)
    d.rectangle([9, 18, 19, 18], fill=dark)
    for y in (20, 22, 24):
        d.line([(11, y), (17, y)], fill=dark)
    # plinth
    d.rectangle([2, 28, 29, 30], fill=shade)
    d.line([(2, 28), (29, 28)], fill=body)
    outline(im)
    # a soft shadow on the ground under it
    return im


def tomb_box():
    im, d = canvas(2, 1)
    d.rectangle([3, 2, 28, 6], fill=W0)  # lid
    d.line([(3, 6), (28, 6)], fill=W2)
    d.rectangle([4, 7, 27, 12], fill=W2)  # front
    d.rectangle([11, 8, 20, 11], fill=W3)
    d.line([(13, 9), (18, 9)], fill=W4)
    d.rectangle([2, 13, 29, 14], fill=W3)
    outline(im)
    return im


def crypt():
    """The oldest crypt, 3x3: a society tomb built like a small copy of the gym's portico - its corner pier, a column
    each side, the arched iron door and the dentil band are the gym's own tiles - under a weathered pediment of its
    own with a cross, urns on the corners and moss in the joints. Left half drawn; main() mirrors it."""
    g = mirror(gym())
    im, d = canvas(3, 3)
    for x0, y0, gx, gy in ((0, 16, 8, 32), (8, 16, 8, 32), (16, 16, 8, 32),      # dentil band
                           (0, 24, 0, 40), (0, 32, 0, 48), (0, 40, 0, 72),      # corner pier
                           (8, 24, 16, 40), (8, 32, 16, 48), (8, 40, 16, 72),   # the column: capital, shaft, base
                           (16, 24, 48, 40), (16, 32, 48, 48), (16, 40, 48, 72)):  # over the door, its arch, bars
        im.paste(g.crop((gx, gy, gx + 8, gy + 8)), (x0, y0))
    # the pediment: 1 in 2 up to the apex at x 23, a recessed tympanum, a cross on top
    for x in range(0, 24):
        top = 15 - x // 2
        d.line([(x, top), (x, 15)], fill=W1)
        P(d, x, top, W0)
        if top + 4 <= 14:
            d.line([(x, top + 4), (x, 14)], fill=W3)
    d.line([(0, 15), (23, 15)], fill=W2)
    d.rectangle([23, 0, 23, 4], fill=W4)  # cross (2 px wide with the mirror)
    d.line([(21, 1), (23, 1)], fill=W4)
    d.ellipse([18, 9, 29, 14], fill=W2, outline=W4)  # a worn rosette
    d.rectangle([2, 9, 5, 14], fill=W3)  # an urn on the corner
    d.rectangle([3, 7, 4, 8], fill=W4)
    for x, y in ((6, 13), (7, 12), (14, 11), (12, 12), (20, 14)):  # moss and staining
        P(d, x, y, MOSS)
    outline(im)
    return im


def vault():
    """A short wall of oven vaults, three high, whitewashed, with marble slabs."""
    im, d = canvas(3, 2)
    d.rectangle([1, 3, 46, 28], fill=W1)
    d.rectangle([0, 1, 47, 4], fill=W0)  # coping
    d.line([(0, 4), (47, 4)], fill=W3)
    for r, y in enumerate((6, 13, 20)):
        for c, x in enumerate((3, 18, 33)):
            slab = (W3 if (r + c) % 3 else W2)
            d.rectangle([x, y, x + 11, y + 5], fill=slab)
            d.rectangle([x, y, x + 11, y], fill=W4)
            d.line([(x + 3, y + 3), (x + 8, y + 3)], fill=W4)
    d.rectangle([0, 27, 47, 30], fill=W3)
    outline(im)
    return im


def gym():
    """The Fifolet gym: a white marble temple-mausoleum with a blue wisp in its pediment. Drawn on the 8 px tile
    grid (columns, door bars, roof slope 1:2 and friezes repeat tile by tile) and mirrored, so it stays cheap."""
    im, d = canvas(7, 6)
    W, H = im.size
    cx = W // 2  # 56: the mirror axis
    # pediment: slope exactly 1:2 from (8, 28) to the apex (56, 4)
    for x in range(8, cx):
        top = 28 - (x - 8) // 2
        d.line([(x, top), (x, 28)], fill=W1)
        P(d, x, top, W0)
        it = top + 5  # the tympanum, set back from the raking cornice
        if x >= 18 and it < 27:
            d.line([(x, it), (x, 27)], fill=W3)
    # the wisp emblem (left half; mirrored)
    d.ellipse([cx - 8, 12, cx + 7, 25], fill=W2, outline=W4)
    d.polygon([(cx - 4, 23), (cx - 5, 18), (cx - 1, 13), (cx, 16), (cx + 3, 14), (cx + 4, 19), (cx + 3, 23)], fill=WISP)
    d.polygon([(cx - 2, 22), (cx - 2, 19), (cx, 17), (cx + 2, 20), (cx + 1, 22)], fill=WISP_L)
    d.rectangle([cx - 2, 0, cx + 1, 4], fill=W2)  # apex finial
    # acroterion urn on the corner
    d.rectangle([5, 21, 10, 27], fill=W2)
    d.ellipse([4, 16, 11, 22], fill=W2, outline=W4)
    # entablature: plain band, dentils (4 px period), shadow line
    d.rectangle([0, 28, cx, 39], fill=W0)
    d.line([(0, 31), (cx, 31)], fill=W3)
    for x in range(0, cx, 4):
        d.rectangle([x + 1, 33, x + 2, 35], fill=W3)
    d.line([(0, 39), (cx, 39)], fill=W4)
    # wall behind the colonnade, in shade
    d.rectangle([8, 40, cx, 79], fill=W2)
    # columns: each exactly one 8 px tile wide (x 16-23 and 32-39), capital and base inside the same tile
    for x0 in (16, 32):
        d.rectangle([x0, 40, x0 + 7, 41], fill=W0)
        d.line([(x0, 42), (x0 + 7, 42)], fill=W4)
        d.rectangle([x0 + 1, 43, x0 + 6, 77], fill=W0)
        d.line([(x0 + 5, 43), (x0 + 5, 77)], fill=W2)
        d.line([(x0 + 6, 43), (x0 + 6, 77)], fill=W4)
        d.line([(x0 + 3, 43), (x0 + 3, 77)], fill=W1)
        d.rectangle([x0, 78, x0 + 7, 79], fill=W2)
    # the corner pier (x 0-7) closing the facade
    d.rectangle([0, 40, 7, 79], fill=W1)
    d.line([(7, 40), (7, 79)], fill=W4)
    # central doorway x 44-55 (left half): a pilaster frame, then the iron door with 4 px bars
    d.rectangle([44, 40, 47, 79], fill=W1)
    d.line([(47, 40), (47, 79)], fill=W4)
    d.rectangle([48, 48, cx, 79], fill=DARK)
    d.rectangle([48, 44, cx, 47], fill=W2)
    d.pieslice([48, 48, 63, 63], 180, 270, fill=WISP_D)
    for x in (49, 53):
        d.line([(x, 52), (x, 79)], fill=IRON_L)
    d.line([(48, 64), (cx, 64)], fill=IRON_L)
    d.line([(cx - 1, 52), (cx - 1, 79)], fill=OUT)
    P(d, cx - 3, 70, GOLD_L)
    # stylobate and the stair
    d.rectangle([0, 80, cx, 83], fill=W1)
    d.line([(0, 83), (cx, 83)], fill=W3)
    d.rectangle([0, 84, 31, 93], fill=W2)  # the plinth either side of the stair
    d.line([(0, 93), (31, 93)], fill=W4)
    for y in (84, 88, 92):
        d.rectangle([32, y, cx, y + 2], fill=W1)
        d.line([(32, y + 3), (cx, y + 3)], fill=W3)
    # a wisp lantern on the plinth: an iron tripod holding a blue flame
    x = 12
    d.line([(x, 72), (x, 86)], fill=IRON)
    d.line([(x - 3, 89), (x, 82)], fill=IRON)
    d.line([(x + 3, 89), (x, 82)], fill=IRON)
    d.rectangle([x - 3, 70, x + 3, 72], fill=IRON)
    d.polygon([(x - 2, 69), (x - 3, 65), (x, 60), (x + 1, 63), (x + 3, 65), (x + 2, 69)], fill=WISP)
    d.polygon([(x - 1, 68), (x - 1, 65), (x, 63), (x + 1, 66), (x + 1, 68)], fill=WISP_L)
    outline(im)
    return im


# ------------------------------------------------------------------ fences
def _fence_rail(d, x0, x1, y0):
    """Rails and spear-topped pickets of an east-west run between x0 and x1, the tile's rows y0..y0+7 of the cell."""
    for x in range(x0, x1 + 1):
        if x % 4 == 1:
            d.line([(x, max(0, 3 - y0)), (x, min(7, 13 - y0))], fill=IRON)
            if y0 == 0:
                P(d, x, 2, OUT)
    for y, c in ((5, IRON_L), (12, IRON)):
        if y0 <= y < y0 + 8:
            d.line([(x0, y - y0), (x1, y - y0)], fill=OUT)
        if y0 <= y + 1 < y0 + 8:
            d.line([(x0, y + 1 - y0), (x1, y + 1 - y0)], fill=c)


def _fence_post(rail, south=False, top=True):
    """The left half of a post cell (the right half is the mirror image of the same kind of tile): a slim square
    shaft on a wider foot under a ball finial (which hides a fence running north), the rail coming in from the
    west, a fence running south below the post's foot."""
    im, d = tile8()
    y0 = 0 if top else 8
    if rail:
        _fence_rail(d, 0, 5, y0)
    if top:
        d.line([(6, 4), (6, 7)], fill=OUT)
        d.line([(7, 4), (7, 7)], fill=IRON)
        d.ellipse([5, 0, 10, 5], fill=IRON, outline=OUT)  # clipped at x 7: half the ball
        P(d, 6, 1, IRON_H)
        P(d, 7, 1, IRON_L)
        P(d, 6, 2, IRON_L)
    else:
        d.line([(6, 0), (6, 3)], fill=OUT)
        d.line([(7, 0), (7, 3)], fill=IRON)
        d.rectangle([5, 4, 7, 6], fill=OUT)
        P(d, 7, 4, IRON)
        if south:
            P(d, 6, 7, OUT)
            P(d, 7, 7, IRON)
    return im


def fence(n, s, e, w):
    """A wrought-iron fence cell, built from 8 px tiles so every combination shares them. East-west runs show
    spear-topped pickets every 4 px; north-south runs are seen end-on as a bar with finials every 4 px (mirror-
    symmetric); posts (mirror-symmetric) stand wherever the fence turns, ends or branches."""
    straight_h = e and w and not n and not s
    straight_v = n and s and not e and not w
    if straight_h:
        t, dt = tile8()
        b, db = tile8()
        _fence_rail(dt, 0, 7, 0)
        _fence_rail(db, 0, 7, 8)
        return quad_cell(t, t, b, b)
    if straight_v:
        t, dt = tile8()
        dt.line([(6, 0), (6, 7)], fill=OUT)
        dt.line([(7, 0), (7, 7)], fill=IRON)
        for y in (2, 6):
            dt.line([(5, y), (7, y)], fill=OUT)
        return quad_cell(t, hflip(t), t, hflip(t))
    return quad_cell(_fence_post(w), hflip(_fence_post(e)), _fence_post(w, s, top=False),
                     hflip(_fence_post(e, s, top=False)))


# ------------------------------------------------------------------ drowned ward ruins
def brick_wall(d, x0, y0, x1, y1, seed=0):
    """Brick courses (4 px) with staggered joints; the pattern repeats every 8 px on the sheet's own grid, so a
    wall costs one tile however large it is."""
    d.rectangle([x0, y0, x1, y1], fill=BRICK)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            row, col = y % 8, x % 8
            if row in (0, 4):
                P(d, x, y, MORTAR)
            elif col == (0 if row < 4 else 4):
                P(d, x, y, MORTAR)
            elif (row, col) in ((1, 2), (5, 6)):
                P(d, x, y, BRICK_L)
            elif (row, col) in ((3, 6), (7, 2)):
                P(d, x, y, BRICK_D)


def mirror(im):
    """Left half mirrored onto the right: symmetric art costs half the tiles (flipped tiles are shared)."""
    W, H = im.size
    px = im.load()
    for y in range(H):
        for x in range(W // 2):
            px[W - 1 - x, y] = px[x, y]
    return im


def jagged_top(im, x0, x1, base, amp, seed):
    """Cut the top of a wall into a broken, stepped profile."""
    px = im.load()
    for x in range(x0, x1 + 1):
        h = base + int(amp * (0.5 + 0.5 * math.sin(x * 0.45 + seed) * math.cos(x * 0.21 + seed * 2)))
        h += (x * 7 + seed) % 3
        for y in range(0, h):
            px[x, y] = CLEAR


def vines(d, pts):
    for x, y, n in pts:
        for k in range(n):
            P(d, x + (1 if k % 3 == 1 else 0), y + k, LEAF if k % 2 else LEAF_M)
        P(d, x - 1, y + 1, LEAF_D)


def broken_top(im, x0, x1, tops):
    """Cut a wall's top into a broken profile: `tops` gives the top y of each 8 px column, with a ragged step
    inside each column."""
    px = im.load()
    for x in range(x0, x1 + 1):
        k = (x - x0) // 8
        t = tops[min(k, len(tops) - 1)] + (0, 1, 1, 2, 1, 0, 2, 3)[(x - x0) % 8 if k % 2 else 7 - (x - x0) % 8]
        for y in range(0, t):
            px[x, y] = CLEAR


def darken(im, box, dr=34, dg=26, db=22):
    px = im.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (max(0, r - dr), max(0, g - dg), max(0, b - db), 255)


def vine(d, x, y):
    """One ivy strand inside an 8x8 tile at (x, y)."""
    for k, (dx, c) in enumerate(((3, LEAF_M), (4, LEAF), (3, LEAF_M), (2, LEAF), (3, LEAF_D), (4, LEAF_M), (3, LEAF), (3, LEAF_D))):
        P(d, x + dx, y + k, c)
    P(d, x + 5, y + 2, LEAF_M)
    P(d, x + 1, y + 5, LEAF_M)


def ruin_a(door=False):
    """A roofless brick shell: a darker side wall, two empty upper windows, a doorway (or the barred cellar door
    of the Blacksnake hideout), moss along the waterline. Openings sit on the 8 px grid so they repeat."""
    im, d = canvas(4, 3)
    W, H = im.size
    brick_wall(d, 0, 0, W - 1, H - 1)
    darken(im, (0, 0, 7, H - 1))
    broken_top(im, 0, W - 1, [14, 10, 4, 8, 6, 12, 18, 24])
    for x in (16, 40):  # upper windows, one tile each, with a stone sill under
        d.rectangle([x, 16, x + 7, 23], fill=DARK)
        d.rectangle([x, 24, x + 7, 25], fill=CREAM_D)
    if door:
        d.rectangle([24, 30, 39, 31], fill=CREAM_D)
        d.rectangle([24, 32, 39, 47], fill=DARK)
        for x in range(24, 40):
            if x % 4 == 2:
                d.line([(x, 32), (x, 47)], fill=IRON_L)
        d.line([(24, 39), (39, 39)], fill=IRON_L)
    else:
        d.rectangle([24, 32, 39, 47], fill=DARK)
        d.rectangle([24, 44, 39, 47], fill=WATER_D)
        d.line([(24, 44), (39, 44)], fill=WATER)
        d.rectangle([48, 32, 55, 39], fill=DARK)
        d.rectangle([48, 40, 55, 41], fill=CREAM_D)
    for x in range(0, W):  # moss and the waterline along the foot
        if im.getpixel((x, 46))[3]:
            d.point((x, 46), fill=MOSS if x % 4 else LEAF_M)
            d.point((x, 47), fill=LEAF_D)
    vine(d, 8, 16)
    vine(d, 56, 32)
    outline(im)
    return im


def ruin_b():
    """A broken gable end: a chimney stack, a tall arched window, the rest fallen."""
    im, d = canvas(3, 3)
    W, H = im.size
    brick_wall(d, 0, 0, W - 1, H - 1)
    darken(im, (40, 0, 47, H - 1))
    broken_top(im, 0, W - 1, [10, 0, 0, 6, 12, 20])
    d.rectangle([8, 0, 15, 2], fill=CREAM_D)  # the chimney cap (x 8-15 stands to the top)
    d.line([(8, 2), (15, 2)], fill=CREAM_DD)
    px = im.load()
    for y in range(0, 6):  # chimney stack only above the gable line
        for x in list(range(0, 8)) + list(range(16, 24)):
            if y < 5:
                px[x, y] = CLEAR
    d.rectangle([24, 16, 31, 39], fill=DARK)  # arched window, two tiles tall
    d.pieslice([24, 12, 31, 20], 180, 360, fill=DARK)
    d.rectangle([24, 40, 31, 41], fill=CREAM_D)
    d.rectangle([8, 32, 15, 47], fill=DARK)  # a low doorway
    for x in range(0, W):
        if px[x, 46][3]:
            d.point((x, 46), fill=MOSS if x % 4 else LEAF_M)
            d.point((x, 47), fill=LEAF_D)
    vine(d, 0, 16)
    vine(d, 32, 24)
    outline(im)
    return im


# ------------------------------------------------------------------ french quarter balconies
def balcony(kind):
    """The iron railing of a gallery across the lower half of an upper-floor wall cell."""
    im, d = canvas(1, 1)
    x0 = 2 if kind == "l" else 0
    x1 = 13 if kind == "r" else 15
    d.rectangle([x0, 14, x1, 15], fill=OUT)  # the balcony floor slab
    d.line([(x0, 13), (x1, 13)], fill=IRON)
    d.line([(x0, 7), (x1, 7)], fill=OUT)  # handrail
    d.line([(x0, 8), (x1, 8)], fill=IRON_L)
    for x in range(x0, x1 + 1):
        # lacework: pickets with little scrolls between them
        if (x - x0) % 4 == 0:
            d.line([(x, 9), (x, 12)], fill=OUT)
        elif (x - x0) % 4 == 2:
            P(d, x, 10, OUT)
            P(d, x, 11, IRON_L)
        else:
            P(d, x, 10 if (x - x0) % 4 == 1 else 11, IRON)
    if kind in ("l", "r"):
        xp = x0 if kind == "l" else x1
        d.rectangle([xp - (1 if kind == "l" else 0), 6, xp + (0 if kind == "l" else 1), 15], fill=OUT)
    if kind == "fern":
        # a hanging fern basket from the gallery above
        d.line([(7, 0), (7, 2)], fill=OUT)
        d.ellipse([3, 2, 12, 7], fill=LEAF)
        for x, y in ((3, 6), (4, 7), (11, 6), (12, 7), (6, 6), (9, 7)):
            P(d, x, y, LEAF_M)
        P(d, 5, 3, LEAF_L)
        P(d, 9, 3, LEAF_L)
        d.rectangle([5, 6, 9, 7], fill=WOOD_D)
    return im


# ------------------------------------------------------------------ market
def stall(stripe):
    """A market stall: striped awning, poles, a counter of produce crates. Drawn on the 8 px grid and mirror-
    symmetric: the stripes are symmetric inside every tile (red 4 px across each tile join, white 4 px in the
    middle), the crates come in three kinds mirrored about the middle, so the whole stall is eight tiles."""
    im, d = canvas(3, 2)
    W = im.width
    dark = RED_D if stripe == RED else GREEN_D
    for x in range(0, W // 2):
        c = stripe if x % 8 in (6, 7, 0, 1) else W0
        d.line([(x, 2), (x, 11)], fill=c)
        if x % 4 in (1, 2):
            P(d, x, 12, c)
        P(d, x, 6, dark if c == stripe else W2)
    d.line([(0, 1), (W // 2 - 1, 1)], fill=OUT)
    d.line([(1, 12), (1, 26)], fill=WOOD_D)  # pole
    d.rectangle([0, 22, W // 2 - 1, 29], fill=WOOD)  # counter
    d.line([(0, 22), (W // 2 - 1, 22)], fill=WOOD_L)
    for x in (7, 15, 23):
        d.line([(x, 23), (x, 29)], fill=WOOD_D)
    d.line([(0, 28), (W // 2 - 1, 28)], fill=WOOD_D)
    produce = [(RED, RED_L), (YELLOW, h("e8e098")), (GREEN_L, h("e8e098"))]
    for k, (c, cl) in enumerate(produce):
        x = k * 8
        d.rectangle([x + 1, 17, x + 6, 21], fill=WOOD_D)
        for i in range(6):
            P(d, x + 1 + i, 16 + (i % 2), c)
            P(d, x + 1 + i, 18, cl if i % 2 else c)
    d.line([(1, 12), (1, 26)], fill=WOOD_D)
    mirror(im)
    outline(im)
    return im


# ------------------------------------------------------------------ park and plazas
def fountain():
    im, d = canvas(3, 3)
    # basin
    d.ellipse([1, 22, 46, 46], fill=W2)
    d.ellipse([1, 22, 46, 44], fill=W1)
    d.ellipse([5, 25, 42, 41], fill=WATER)
    d.ellipse([5, 25, 42, 33], fill=WATER_D)
    for x, y in ((11, 35), (14, 37), (33, 36), (36, 34), (23, 39), (17, 30), (30, 30)):
        d.line([(x, y), (x + 3, y)], fill=WATER_L)
    # pedestal and the upper bowl
    d.rectangle([21, 16, 26, 34], fill=W1)
    d.line([(26, 16), (26, 34)], fill=W3)
    d.ellipse([18, 32, 29, 37], fill=W2)
    d.ellipse([13, 11, 34, 19], fill=W1)
    d.ellipse([15, 12, 32, 16], fill=WATER)
    d.rectangle([22, 6, 25, 12], fill=W2)
    # spray: a plume from the top falling into both bowls
    d.ellipse([20, 0, 27, 7], fill=SPRAY)
    P(d, 23, 1, SPRAY_L)
    P(d, 22, 2, SPRAY_L)
    for x0, x1 in ((14, 9), (33, 38)):
        d.line([(x0, 17), (x1, 27)], fill=SPRAY)
    for x0, x1 in ((19, 15), (28, 32)):
        d.line([(x0, 6), (x1, 12)], fill=SPRAY)
    outline(im)
    return im


def obelisk():
    im, d = canvas(1, 3)
    d.polygon([(5, 6), (7, 2), (8, 2), (10, 6)], fill=W1)
    d.polygon([(5, 6), (10, 6), (11, 36), (4, 36)], fill=W2)
    d.polygon([(8, 6), (10, 6), (11, 36), (9, 36)], fill=W3)
    d.line([(7, 3), (5, 6)], fill=W0)
    d.rectangle([2, 36, 13, 41], fill=W1)
    d.line([(2, 41), (13, 41)], fill=W3)
    d.rectangle([1, 42, 14, 45], fill=W2)
    d.rectangle([5, 38, 10, 40], fill=W3)
    outline(im)
    return im


def hedge(kind):
    """Clipped box hedge; the middle piece repeats every 8 px."""
    im, d = canvas(1, 1)
    x0 = 2 if kind == "l" else 0
    x1 = 13 if kind == "r" else 15
    d.rectangle([x0, 3, x1, 14], fill=LEAF_D)
    d.rectangle([x0, 3, x1, 10], fill=LEAF)
    for x in range(x0, x1 + 1):
        if x % 4 == 1:
            P(d, x, 5, LEAF_M)
            P(d, x + 1, 8, LEAF_M)
        if x % 8 == 3:
            P(d, x, 4, LEAF_L)
    outline(im, sides=(1 if kind == "r" else 0, 1 if kind == "l" else 0, 1, 1))
    return im


def walk(kind):
    """Boardwalk planks (opaque), drawn to repeat every 8 px. kind: vl/vm/vr for a north-south walk (boards
    across, a beam down the left or right edge), ht/hm/hb for an east-west one (boards along, beams top/bottom)."""
    im, d = canvas(1, 1)
    vertical = kind[0] == "v"
    for y in range(16):
        for x in range(16):
            u, v = (x, y) if vertical else (y, x)  # u along the board, v across the boards
            c = WOOD_D  # weathered dark planks, 8 px boards: a highlight along each, a dark seam between
            if v % 8 == 7:
                c = OUT
            elif v % 8 == 0:
                c = h("908030")
            elif v % 8 == 3 and u % 8 in (2, 5):
                c = WOOD
            P(d, x, y, c)
    edge = {"vl": ("x", 0), "vr": ("x", 15), "ht": ("y", 0), "hb": ("y", 15)}.get(kind)
    if edge:
        axis, at = edge
        inner = 1 if at == 0 else 14
        if axis == "x":
            d.line([(at, 0), (at, 15)], fill=OUT)
            d.line([(inner, 0), (inner, 15)], fill=WOOD_D)
        else:
            d.line([(0, at), (15, at)], fill=OUT)
            d.line([(0, inner), (15, inner)], fill=WOOD_D)
    return im


def flowerbed():
    """A formal bed (walkable): dark foliage with two blooms per 8 px tile, every bloom a different colour."""
    im, d = canvas(1, 1)
    d.rectangle([0, 0, 15, 15], fill=LEAF)
    for y in range(16):
        for x in range(16):
            if (x + 2 * y) % 5 == 0:
                P(d, x, y, LEAF_M)
            elif (x * 3 + y) % 7 == 0:
                P(d, x, y, LEAF_D)
    colours = [(RED, YELLOW), (W0, PURPLE), (PINK, BLUEF), (ORANGE, W0)]
    for k, (tx, ty) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
        for (fx, fy), c in zip(((2, 2), (5, 5)), colours[k]):
            x, y = tx + fx, ty + fy
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                P(d, x + dx, y + dy, c)
            P(d, x, y, YELLOW if c != YELLOW else ORANGE)
    return im


def mailbox():
    im, d = canvas(1, 1)
    d.rectangle([7, 9, 8, 14], fill=IRON)
    d.rounded_rectangle([4, 2, 11, 10], radius=3, fill=(72, 96, 152))
    d.rectangle([4, 7, 11, 10], fill=(56, 76, 128))
    d.line([(5, 5), (10, 5)], fill=W0)
    outline(im)
    return im


def bin_():
    im, d = canvas(1, 1)
    d.rectangle([4, 4, 11, 13], fill=IRON)
    d.rectangle([3, 3, 12, 5], fill=IRON_L)
    for x in (6, 9):
        d.line([(x, 7), (x, 12)], fill=OUT)
    outline(im)
    return im


def sign():
    im, d = canvas(1, 1)
    d.rectangle([3, 9, 4, 14], fill=WOOD_D)
    d.rectangle([11, 9, 12, 14], fill=WOOD_D)
    d.rectangle([1, 2, 14, 9], fill=WOOD)
    d.rectangle([1, 2, 14, 2], fill=WOOD_L)
    for y in (4, 6):
        d.line([(3, y), (12, y)], fill=WOOD_D)
    outline(im)
    return im


def generator():
    """The old waterfront generator at the end of Rotom's pier: a grey cabinet with louvres and a yellow hazard
    plate, mirror-symmetric (two tiles)."""
    im, d = canvas(1, 1)
    d.rectangle([2, 4, 13, 14], fill=W4)        # cabinet
    d.rectangle([2, 2, 13, 4], fill=W2)         # lid
    d.line([(2, 5), (13, 5)], fill=W5)
    for y in (7, 9, 11):                        # louvres either side
        d.line([(3, y), (4, y)], fill=OUT)
        d.line([(11, y), (12, y)], fill=OUT)
    d.rectangle([4, 7, 11, 12], fill=GOLD, outline=OUT)  # hazard plate with its "!"
    d.rectangle([7, 8, 8, 9], fill=OUT)
    d.rectangle([7, 11, 8, 11], fill=OUT)
    d.line([(2, 13), (13, 13)], fill=W5)
    d.rectangle([3, 14, 4, 15], fill=OUT)       # feet
    mirror(im)
    outline(im)
    return im


def gazebo():
    """The park bandstand: a white gazebo under a verdigris pavilion roof, columns, a balustrade, steps at the
    front. Left half drawn on the 8 px grid, then mirrored: the roof falls 1 px in 2 so its edge tiles repeat
    along the slope, the ribs and fascia repeat every 8 px, the columns stand at the same place in their tiles."""
    im, d = canvas(4, 4)
    cx = 32  # the mirror axis
    # finial: a white ball on a spike over the apex
    d.rectangle([cx - 1, 3, cx - 1, 7], fill=W0)
    d.rectangle([cx - 2, 1, cx - 1, 2], fill=W0)
    P(d, cx - 1, 0, W2)
    # the roof: x_edge(y) = 32 - 2 (y - 8) for y 8..23, outlined by the two pixels left of it in each row, so the
    # edge crosses exactly two tiles per tile row and its tiles repeat down the slope; verdigris with ribs every
    # 8 px, seams every 8 rows, a lighter band along the ribs' tops
    for y in range(8, 24):
        xe = cx - 2 * (y - 8)
        for x in range(max(0, xe - 2), cx):
            if x < xe:
                c = OUT
            elif x % 8 == 4 or (y % 8 == 4 and x % 8 in (0, 1, 2)):
                c = WATER_D
            elif x % 8 == 5:
                c = W3
            else:
                c = WATER
            P(d, x, y, c)
    # fascia and valance
    d.rectangle([1, 24, cx - 1, 26], fill=W0)
    d.line([(1, 27), (cx - 1, 27)], fill=W2)
    for x in range(1, cx):
        P(d, x, 28, W0 if x % 4 in (1, 2) else OUT)
    # the shade under the roof (out to the edge, so the outer columns' tiles are the inner ones')
    d.rectangle([0, 29, cx - 1, 33], fill=OUT)
    d.rectangle([0, 34, cx - 1, 47], fill=IRON)
    # columns at x 2..5 and 18..21 (the same place in their tiles)
    for x0 in (2, 18):
        d.rectangle([x0 - 1, 32, x0 + 4, 33], fill=W0)  # capital
        d.rectangle([x0, 34, x0 + 2, 45], fill=W0)
        d.line([(x0 + 3, 34), (x0 + 3, 45)], fill=W2)
        d.rectangle([x0 - 1, 46, x0 + 4, 47], fill=W2)  # base
    # balustrade between the columns, open in the middle (x 24..31): balusters every 4 px (8 px periodic)
    for x in list(range(0, 2)) + list(range(6, 18)) + list(range(22, 24)):
        P(d, x, 40, W1)
        if x % 4 == 0:
            d.line([(x, 41), (x, 46)], fill=W1)
        P(d, x, 47, W2)
    d.rectangle([24, 44, cx - 1, 47], fill=W3)  # the floor seen through the opening
    # floor platform and the steps
    d.rectangle([1, 48, cx - 1, 50], fill=W1)
    d.rectangle([1, 51, cx - 1, 54], fill=W3)
    d.line([(0, 55), (cx - 1, 55)], fill=OUT)
    d.line([(16, 56), (16, 63)], fill=OUT)  # the steps, outlined by hand so nothing spills into the next tile
    for y in range(56, 64):
        d.line([(17, y), (cx - 1, y)], fill=W3 if y % 3 == 2 else W1)
    mirror(im)
    outline(im)
    return im


def steamboat():
    """The riverboat: a white sternwheeler seen broadside, bow to the east, red paddle wheel at the stern.
    Its middle repeats every 8 px (windows, railings, hull stripe), so it costs few tiles."""
    im, d = canvas(7, 3)
    W, H = im.size
    # hull (row 2): white with a red stripe; the waterline at y 43, water below
    d.rectangle([14, 32, W - 12, 42], fill=W0)
    d.polygon([(W - 12, 32), (W - 1, 32), (W - 7, 42), (W - 12, 42)], fill=W0)
    d.rectangle([14, 38, W - 10, 39], fill=RED)
    d.line([(14, 40), (W - 9, 40)], fill=W2)
    d.line([(14, 43), (W - 8, 43)], fill=W3)
    # main deck (row 1): cabin with windows every 8 px under a railing
    d.rectangle([16, 18, W - 16, 31], fill=W1)
    d.line([(14, 17), (W - 13, 17)], fill=W0)
    for x in range(16, W - 16):
        if x % 8 in (3, 4):
            d.line([(x, 22), (x, 27)], fill=SLATE_D)
        if x % 4 == 0:
            P(d, x, 30, W3)
    d.line([(16, 31), (W - 16, 31)], fill=W3)
    # texas deck and the pilot house (row 0), twin stacks with gold crowns
    d.rectangle([32, 8, W - 32, 15], fill=W1)
    d.line([(30, 7), (W - 30, 7)], fill=W0)
    for x in range(32, W - 32):
        if x % 8 in (3, 4):
            P(d, x, 11, SLATE_D)
            P(d, x, 12, SLATE_D)
    d.rectangle([W - 46, 1, W - 36, 7], fill=W0)
    d.rectangle([W - 44, 3, W - 38, 5], fill=SLATE_D)
    d.line([(W - 47, 0), (W - 35, 0)], fill=RED)
    for x in (40, 50):
        d.rectangle([x, 0, x + 3, 15], fill=OUT)
        d.line([(x + 3, 2), (x + 3, 15)], fill=IRON)
        d.rectangle([x - 1, 0, x + 4, 1], fill=GOLD)
    # the stern paddle wheel
    d.rectangle([1, 16, 13, 42], fill=RED)
    for y in range(18, 42, 4):
        d.line([(2, y), (12, y)], fill=W2)
    d.line([(7, 16), (7, 42)], fill=OUT)
    d.rectangle([0, 14, 14, 16], fill=W0)
    # a pennant at the bow
    d.line([(W - 14, 6), (W - 14, 17)], fill=IRON)
    d.polygon([(W - 13, 6), (W - 8, 8), (W - 13, 10)], fill=RED)
    outline(im)
    # ripples along the waterline
    for x in range(16, W - 10):
        if x % 8 in (1, 2, 3):
            P(d, x, 45, WATER_L)
    return im


def tallgrass(dense=True):
    """Soft long grass for wild encounters, drawn over the lawn: fans of leaning blades, dark at the root,
    light at the tips. dense: two fans per 8 px tile, wrapping, so a whole patch is one repeating tile;
    rim: three loose fans per cell for a patch's edge cells, so patches fade out instead of ending in a row."""

    def fan(px, W, H, x, y, wrap, size=3):
        for k in range(-size + 1, size):
            length = size + 2 - abs(k)
            for t in range(length):
                i = x + k + (k > 0 and t >= length - 2) - (k < 0 and t >= length - 2)
                j = y - t
                if wrap:
                    i, j = i % W, j % H
                if 0 <= i < W and 0 <= j < H:
                    c = LEAF_D if t == 0 else LEAF if t < length - 2 else LEAF_M
                    px[i, j] = c + (255,)

    if dense:
        tile = Image.new("RGBA", (8, 8), CLEAR)
        tp = tile.load()
        for x, y in ((1, 7), (5, 6), (3, 3), (7, 2)):
            fan(tp, 8, 8, x, y, True, 2)
        im = Image.new("RGBA", (16, 16), CLEAR)
        for i in (0, 8):
            for j in (0, 8):
                im.paste(tile, (i, j))
        return im
    im = Image.new("RGBA", (16, 16), CLEAR)
    px = im.load()
    for x, y, s in ((4, 7, 2), (11, 13, 2), (12, 4, 2), (4, 14, 2)):
        fan(px, 16, 16, x, y, False, s)
    return im


def footbridge(side):
    """A white railed footbridge, two cells wide (side "l" or "r"), running north-south: deck boards every
    4 px, a white handrail with posts every 8 px along the outer edge, a shadow under the rail. Opaque."""
    im, d = canvas(1, 1)
    for y in range(16):
        d.line([(0, y), (15, y)], fill=W1 if y % 4 else W3)
    outer = 0 if side == "l" else 15
    step = 1 if side == "l" else -1
    rail = [outer + step * k for k in range(4)]  # outline, rail, rail, shadow
    for y in range(16):
        P(d, rail[0], y, OUT)
        P(d, rail[1], y, W0)
        P(d, rail[2], y, W2 if y % 8 not in (0, 1) else W0)
        P(d, rail[3], y, W4)
    for y in range(16):
        if y % 8 in (0, 1):  # posts
            P(d, rail[1], y, W2)
            P(d, rail[2], y, W2)
    return im


def railwalk(kind):
    """A weathered railed boardwalk, three cells wide (kind l/m/r), north-south: dark planks across, a rail of
    posts and a top beam along each outer edge. Opaque."""
    im = walk("vm")
    d = ImageDraw.Draw(im)
    if kind in ("l", "r"):
        outer = 0 if kind == "l" else 15
        step = 1 if kind == "l" else -1
        for y in range(16):
            P(d, outer, y, OUT)
            P(d, outer + step, y, WOOD_L if y % 8 else WOOD_D)
            P(d, outer + 2 * step, y, WOOD if y % 8 in (0, 1) else WOOD_D)
            P(d, outer + 3 * step, y, OUT if y % 8 in (0, 1) else WOOD_D)
    return im


def easel():
    """A painter's easel with a half-finished canvas of the pond (Smeargle's haunt)."""
    im, d = canvas(1, 1)
    d.line([(4, 15), (7, 3)], fill=WOOD_D)
    d.line([(11, 15), (8, 3)], fill=WOOD_D)
    d.line([(8, 6), (9, 15)], fill=WOOD_D)
    d.rectangle([3, 2, 12, 9], fill=h("f8f0b8"))
    d.rectangle([4, 6, 11, 8], fill=h("689878"))
    d.rectangle([5, 4, 7, 5], fill=h("c84050"))
    d.rectangle([9, 3, 10, 5], fill=h("f09038"))
    P(d, 8, 7, h("9068c8"))
    d.line([(3, 10), (12, 10)], fill=WOOD)
    outline(im)
    return im


def steamboat_ns():
    """The riverboat moored north-south along the shore, in the overworld's 3/4 view: a white sternwheeler, bow to
    the north. A pointed foredeck with a capstan; twin black stacks with gold feathered crowns and a brace between
    them; the railed hurricane deck over the main cabin, the texas deck on it with the pilot house forward; the
    cabin's after wall (the one face the camera sees) with its windows; the red paddlewheel across the stern.
    The left half is drawn on the 8 px grid (decks, rails and roofs repeat every 8 px down the long middle) and
    mirrored about x 24, so most of the boat is a handful of repeating tiles."""
    im, d = canvas(3, 7)
    cx = 24
    DECK, PLANK = W2, W3

    def xl(y):  # the hull's edge (left half): a pointed bow, then straight sides
        if y < 2:
            return None
        if y <= 15:
            return 24 - (y - 0) if y >= 2 else None
        return max(3, 9 - (y - 15) // 2)

    # hull and main deck: outline, red trim, white guard rail with posts, deck planks
    for y in range(2, 98):
        x0 = xl(y)
        d.line([(x0, y), (cx - 1, y)], fill=DECK)
        for x in range(x0 + 3, cx):
            if x % 4 == 2:
                P(d, x, y, PLANK)
        P(d, x0, y, OUT)
        if x0 + 1 < cx:
            P(d, x0 + 1, y, RED)
        if x0 + 2 < cx:
            P(d, x0 + 2, y, W0 if y % 4 else W3)
    P(d, 22, 2, OUT)
    P(d, 23, 1, OUT)
    P(d, 23, 2, RED)
    d.line([(23, 0), (23, 1)], fill=IRON)  # jackstaff
    P(d, 23, 0, GOLD)
    # capstan and bitts on the foredeck
    d.rectangle([22, 13, 23, 15], fill=W4)
    d.line([(22, 13), (23, 13)], fill=W1)
    d.line([(21, 13), (21, 15)], fill=OUT)
    d.line([(21, 16), (23, 16)], fill=OUT)
    for y in (22, 26):
        P(d, 13, y, OUT)
        P(d, 13, y + 1, W4)
    # the hurricane deck (roof of the main cabin) x 10..23, y 30..91: rail along its edge, a shadow wall below it
    d.line([(10, 29), (cx - 1, 29)], fill=OUT)
    for y in range(30, 92):
        P(d, 9, y, W4)
        P(d, 10, y, W0 if y % 4 else W3)
        d.line([(11, y), (cx - 1, y)], fill=W1)
        P(d, 11, y, W2)
        if y % 8 == 4:  # seams in the deck's canvas
            d.line([(12, y), (cx - 1, y)], fill=W2)
    d.line([(10, 30), (cx - 1, 30)], fill=W0)
    # the main cabin's after wall (the face we see), y 92..97: a cornice line, windows
    d.line([(9, 92), (cx - 1, 92)], fill=OUT)
    d.rectangle([9, 93, cx - 1, 97], fill=W2)
    for x in range(9, cx):
        if x % 4 in (1, 2):
            d.line([(x, 94), (x, 96)], fill=IRON)
            P(d, x, 94, W3)
    d.line([(9, 97), (cx - 1, 97)], fill=W3)
    # the texas deck: x 16..23, y 48..75, its after wall y 76..81
    d.line([(16, 47), (cx - 1, 47)], fill=OUT)
    for y in range(48, 76):
        P(d, 16, y, OUT)
        d.line([(17, y), (cx - 1, y)], fill=W0)
        P(d, 17, y, W1)
        if y % 8 == 4:
            d.line([(18, y), (cx - 1, y)], fill=W1)
        if y % 8 == 0:  # a row of skylights down the texas roof
            d.line([(20, y), (21, y)], fill=W3)
    d.line([(16, 76), (cx - 1, 76)], fill=OUT)
    for y in range(77, 82):
        P(d, 16, y, OUT)
        d.line([(17, y), (cx - 1, y)], fill=W2)
    for x in range(17, cx):
        if x % 4 in (2, 3):
            d.line([(x, 78), (x, 80)], fill=IRON)
    d.line([(16, 82), (cx - 1, 82)], fill=W3)
    # the pilot house on the texas deck's forward end: a fancy roof, glass all round (its after face shows)
    d.line([(18, 39), (cx - 1, 39)], fill=OUT)
    P(d, 17, 40, OUT)
    d.rectangle([18, 40, cx - 1, 43], fill=W0)
    d.line([(18, 41), (cx - 1, 41)], fill=RED)  # red trim round the roof
    P(d, 17, 41, OUT)
    P(d, 17, 42, OUT)
    P(d, cx - 1, 38, GOLD)  # finial (2 px with the mirror)
    d.line([(17, 44), (cx - 1, 44)], fill=OUT)
    for y in range(45, 48):
        P(d, 17, y, OUT)
        d.line([(18, y), (cx - 1, y)], fill=IRON)
        for x in range(18, cx):
            if x % 3 == 0:
                P(d, x, y, W0)
    P(d, 19, 45, W3)
    # twin stacks (the left one x 17..20; mirrored), bases on the hurricane deck at y 38, crowns at y 8..12
    for y in range(12, 39):
        P(d, 17, y, OUT)
        P(d, 18, y, IRON)
        P(d, 19, y, IRON_L if y % 6 else IRON)
        P(d, 20, y, OUT)
    d.rectangle([16, 36, 21, 38], fill=W4)  # the collar where it leaves the deck
    d.line([(16, 39), (21, 39)], fill=OUT)
    for x, y in ((16, 8), (18, 8), (20, 8), (16, 9), (17, 9), (18, 9), (19, 9), (20, 9), (21, 9)):
        P(d, x, y, GOLD)  # feathered crown
    d.rectangle([16, 10, 21, 11], fill=GOLD_L)
    d.line([(17, 10), (20, 10)], fill=OUT)  # the stack's mouth
    for x in (15, 17, 19, 21):
        P(d, x, 7, OUT)
    P(d, 15, 9, OUT)
    P(d, 15, 10, OUT)
    P(d, 15, 11, OUT)
    P(d, 22, 9, OUT)
    P(d, 22, 10, OUT)
    P(d, 22, 11, OUT)
    # the stern deck and the paddlewheel across the stern
    d.rectangle([5, 98, cx - 1, 99], fill=W0)  # the wheel's frame beam
    d.line([(5, 98), (cx - 1, 98)], fill=OUT)
    for y in range(100, 109):
        c = (RED, RED_L, RED, OUT)[(y - 100) % 4]
        d.line([(6, y), (cx - 1, y)], fill=c)
    for x in range(6, cx):
        if x % 8 == 4:
            d.line([(x, 100), (x, 108)], fill=W0)  # the wheel's rims, seen edge on
    d.line([(5, 100), (5, 108)], fill=OUT)
    d.line([(6, 100), (6, 108)], fill=W2)
    for x in range(5, cx):  # spray churned up under the wheel
        P(d, x, 109, W0 if x % 4 in (0, 1) else W2)
        P(d, x, 110, W2 if x % 4 in (1, 2) else CLEAR)
    mirror(im)
    outline(im)
    return im


# ------------------------------------------------------------------ French Quarter: Creole townhouses
# Stucco in four colours, white quoined pilasters, green shutters, a cast-iron gallery between the storeys. The
# facade is a kit of 8 px tiles: every window, door, shop front, gallery and pilaster tile is drawn without any
# wall colour in it and mirror-symmetric (its right half is its left half flipped, a free copy), so all of them
# are shared by every house whatever its colour; a colour costs two tiles (plain stucco, stucco on the plinth).
# Each shop hangs a 16x8 board on its gallery above the door: a lettered half shared by all, a picture half of
# its own (one tile per trade).
CREOLE = {"pink": (h("e8a8a0"), h("c88078")), "yellow": (h("f0d890"), h("c8b060")),
          "blue": (h("a8c8e8"), h("7898c0")), "green": (h("b0d0a0"), h("80a878"))}
SHUT, SHUT_L = h("406040"), h("507060")
GLASS, GLASS_L = h("404868"), h("98b0d8")


def tile8():
    im = Image.new("RGBA", (8, 8), CLEAR)
    return im, ImageDraw.Draw(im)


def hflip(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def sym_cell(left_top, left_bottom):
    """A 16x16 cell from its left half (two 8x8 tiles); the right half is the mirror image."""
    im = Image.new("RGBA", (16, 16), CLEAR)
    im.paste(left_top, (0, 0))
    im.paste(left_bottom, (0, 8))
    im.paste(hflip(left_top), (8, 0))
    im.paste(hflip(left_bottom), (8, 8))
    return im


def quad_cell(tl, tr, bl, br):
    im = Image.new("RGBA", (16, 16), CLEAR)
    for t, (x, y) in ((tl, (0, 0)), (tr, (8, 0)), (bl, (0, 8)), (br, (8, 8))):
        if t is not None:
            im.paste(t, (x, y))
    return im


def cr_stucco(c, cd, base=False):
    """Plain stucco, 8 px periodic; base: the bottom tile of the ground floor, the wall meeting the plinth."""
    im, d = tile8()
    d.rectangle([0, 0, 7, 7], fill=c)
    for x, y in ((3, 2), (6, 6), (1, 5)):
        P(d, x, y, cd)
    if base:
        d.line([(0, 5), (7, 5)], fill=cd)
        d.line([(0, 6), (7, 6)], fill=W2)
        d.line([(0, 7), (7, 7)], fill=OUT)
    return im


def cr_quoin(base=False):
    """The white rusticated corner pilaster (left side; the right one is its mirror image)."""
    im, d = tile8()
    d.rectangle([1, 0, 5, 7], fill=W0)
    d.line([(6, 0), (6, 7)], fill=W2)
    d.line([(7, 0), (7, 7)], fill=GLASS_L)
    d.line([(1, 3), (5, 3)], fill=W2)
    d.line([(1, 7), (5, 7)], fill=W2)
    P(d, 4, 1, W2)  # the long and short stones of the quoins
    P(d, 2, 5, W2)
    d.line([(0, 0), (0, 7)], fill=OUT)
    if base:
        d.line([(1, 5), (6, 5)], fill=W2)
        d.line([(1, 6), (7, 6)], fill=W2)
        d.line([(0, 7), (7, 7)], fill=OUT)
    return im


def cr_window():
    """A tall French window between louvred shutters (left half): lintel, shutter, frame, pane, the meeting stile."""
    t, dt = tile8()
    b, db = tile8()
    for d, y0 in ((dt, 0), (db, 8)):
        for y in range(8):
            yy = y0 + y
            d.line([(0, y), (2, y)], fill=SHUT_L if yy % 2 else SHUT)
            P(d, 3, y, W0)
            d.line([(4, y), (6, y)], fill=GLASS)
            P(d, 7, y, W2)
    dt.line([(0, 0), (7, 0)], fill=W0)       # lintel
    dt.line([(0, 1), (2, 1)], fill=OUT)      # shadow under it on the shutter
    P(dt, 4, 2, GLASS_L)
    P(dt, 4, 3, GLASS_L)
    P(dt, 5, 2, GLASS_L)
    db.line([(4, 0), (6, 0)], fill=W0)       # glazing bar
    P(db, 4, 2, GLASS_L)
    db.line([(0, 6), (7, 6)], fill=W0)       # sill
    db.line([(0, 7), (7, 7)], fill=OUT)
    return sym_cell(t, b)


def cr_door():
    """Panelled double doors under a fanlight, in a white surround (left half)."""
    t, dt = tile8()
    b, db = tile8()
    dt.rectangle([0, 0, 7, 7], fill=W0)
    dt.rectangle([3, 1, 7, 4], fill=GLASS_L)  # fanlight
    P(dt, 3, 1, W0)
    P(dt, 4, 1, W0)
    P(dt, 3, 2, W0)
    dt.line([(5, 2), (7, 4)], fill=W0)       # its radiating bar
    dt.line([(2, 5), (7, 5)], fill=OUT)
    dt.rectangle([2, 6, 7, 7], fill=SHUT)
    db.rectangle([0, 0, 7, 7], fill=W0)
    db.rectangle([2, 0, 7, 7], fill=SHUT)
    for y in (1, 4):                          # panels
        db.line([(3, y), (5, y)], fill=SHUT_L)
    dt.line([(3, 7), (5, 7)], fill=SHUT_L)
    P(db, 6, 2, W0)                           # knob
    db.line([(7, 0), (7, 7)], fill=OUT)       # the meeting stiles (2 px with the mirror)
    P(dt, 7, 6, OUT)
    P(dt, 7, 7, OUT)
    db.line([(0, 6), (1, 6)], fill=W2)
    db.line([(0, 7), (7, 7)], fill=OUT)
    P(db, 1, 0, W2)
    return sym_cell(t, b)


def cr_shop():
    """A shop window under a striped awning (left half): the stripes meet in a wide band in the middle."""
    t, dt = tile8()
    b, db = tile8()
    for x in range(8):
        c = W0 if 3 <= x <= 5 else SHUT  # five stripes a cell: 3, 3, 4 (across the middle), 3, 3
        dt.line([(x, 1), (x, 3)], fill=c)
        P(dt, x, 4, c if x % 4 in (1, 2) else GLASS)  # the scalloped edge
    dt.line([(0, 0), (7, 0)], fill=OUT)
    dt.line([(0, 5), (7, 5)], fill=GLASS)     # shade under the awning
    dt.rectangle([0, 6, 7, 7], fill=W0)
    dt.rectangle([2, 7, 7, 7], fill=GLASS)
    db.rectangle([0, 0, 7, 7], fill=W0)
    db.rectangle([2, 0, 7, 3], fill=GLASS)
    for x, y in ((4, 2), (5, 1), (6, 0)):     # a glint on the pane
        P(db, x, y, GLASS_L)
    db.line([(0, 5), (7, 5)], fill=W2)        # sill, stall riser
    db.line([(0, 6), (7, 6)], fill=W2)
    db.line([(0, 7), (7, 7)], fill=OUT)
    return sym_cell(t, b)


def cr_lace(post=False):
    """The cast-iron gallery, 8 px periodic: balusters every 4 px with scrolls between them over the whitewashed
    gallery, the handrail, the slab below; post: the iron post at the facade's left end (mirrored for the right)."""
    t, dt = tile8()
    b, db = tile8()
    dt.rectangle([0, 0, 7, 1], fill=OUT)
    dt.rectangle([0, 2, 7, 7], fill=W2)
    dt.line([(0, 3), (7, 3)], fill=OUT)       # handrail
    db.rectangle([0, 0, 7, 7], fill=W2)
    for x in range(8):                        # rows 4..9 of the gallery: 4..7 in the top tile, 8..9 in the bottom
        if x % 4 == 0:
            dt.line([(x, 4), (x, 7)], fill=OUT)
            db.line([(x, 0), (x, 1)], fill=OUT)
        elif x % 4 == 2:
            P(dt, x, 5, OUT)
            P(db, x, 0, OUT)
        else:
            P(dt, x, 6 + (x % 4 == 3), OUT)
    db.line([(0, 2), (7, 2)], fill=OUT)       # bottom rail
    db.rectangle([0, 3, 7, 5], fill=W0)       # the gallery's slab
    db.line([(0, 6), (7, 6)], fill=W2)
    db.line([(0, 7), (7, 7)], fill=OUT)
    if post:
        for d in (dt, db):
            d.line([(0, 0), (0, 7)], fill=OUT)
            d.line([(1, 0), (1, 7)], fill=GLASS)
        P(dt, 1, 4, GLASS_L)
        P(dt, 1, 5, GLASS_L)
    return t, b


SIGNS = ("cafe", "salon", "laundry", "apts", "trades", "coins", "icecream", "egg", "quill", "book")


def cr_board(icon):
    """The shop board's picture half (the right one): its trade as a picture on the white board."""
    im, d = tile8()
    d.rectangle([0, 0, 7, 7], fill=W0)
    d.line([(0, 0), (7, 0)], fill=OUT)
    d.line([(0, 7), (7, 7)], fill=OUT)
    d.line([(7, 0), (7, 7)], fill=OUT)
    px = lambda pts, c: [P(d, x, y, c) for x, y in pts]
    if icon == "cafe":  # a steaming cup on its saucer
        px([(3, 1), (4, 2)], GLASS_L)
        d.rectangle([1, 3, 4, 5], fill=SHUT)
        px([(5, 3), (5, 4)], SHUT)
        d.line([(0, 6), (5, 6)], fill=GLASS)
    elif icon == "salon":  # open scissors
        px([(1, 1), (2, 2), (3, 3), (5, 1), (4, 2)], OUT)
        px([(3, 4), (2, 5), (4, 5), (5, 5)], GLASS)
        px([(1, 5), (1, 6), (2, 6), (5, 6), (6, 6), (6, 5)], OUT)
    elif icon == "laundry":  # a shirt
        d.rectangle([2, 2, 5, 6], fill=GLASS_L)
        px([(1, 2), (1, 3), (6, 2), (6, 3)], GLASS_L)
        px([(3, 1), (4, 1)], OUT)
        px([(3, 2), (4, 2)], W0)
        d.line([(2, 6), (5, 6)], fill=GLASS)
    elif icon == "apts":  # a key
        d.rectangle([1, 2, 3, 4], fill=h("c8b060"))
        P(d, 2, 3, W0)
        d.line([(4, 3), (6, 3)], fill=h("c8b060"))
        px([(5, 4), (6, 5)], h("c8b060"))
    elif icon == "trades":  # two arrows, one each way
        d.line([(1, 2), (5, 2)], fill=OUT)
        px([(5, 1), (6, 2), (5, 3)], OUT)
        d.line([(2, 5), (6, 5)], fill=SHUT)
        px([(2, 4), (1, 5), (2, 6)], SHUT)
    elif icon == "coins":  # a gold coin and a smaller one behind
        d.ellipse([1, 1, 5, 5], fill=h("f0d890"), outline=h("c8b060"))
        P(d, 3, 3, h("c8b060"))
        d.rectangle([4, 5, 6, 6], fill=h("c8b060"))
        P(d, 2, 2, W0)
    elif icon == "icecream":  # a cone with a pink scoop
        d.ellipse([2, 1, 5, 4], fill=h("e8a8a0"))
        P(d, 3, 1, W0)
        px([(2, 5), (3, 5), (4, 5), (5, 5), (3, 6), (4, 6)], h("c8b060"))
        P(d, 4, 4, h("c88078"))
    elif icon == "egg":  # an egg with green spots
        d.ellipse([2, 1, 5, 6], fill=h("f0d890"), outline=h("c8b060"))
        px([(3, 3), (4, 5)], h("80a878"))
        P(d, 3, 2, W0)
    elif icon == "quill":  # a quill pen over a line of writing
        px([(5, 1), (4, 2), (5, 2), (3, 3), (4, 3), (2, 4), (3, 4)], h("7898c0"))
        px([(6, 1), (1, 5)], OUT)
        d.line([(3, 6), (6, 6)], fill=GLASS)
    elif icon == "book":  # an open book
        d.rectangle([1, 2, 6, 5], fill=W2)
        d.line([(1, 6), (6, 6)], fill=h("7898c0"))
        d.line([(1, 1), (6, 1)], fill=W0)
        px([(3, 2), (4, 2), (3, 3), (4, 3), (3, 4), (4, 4), (3, 5), (4, 5)], h("7898c0"))
        P(d, 2, 3, GLASS)
        P(d, 5, 3, GLASS)
    return im


def cr_board_letters():
    """The shop board's lettered half (the left one), the same on every board."""
    im, d = tile8()
    d.rectangle([0, 0, 7, 7], fill=W0)
    d.line([(0, 0), (7, 0)], fill=OUT)
    d.line([(0, 7), (7, 7)], fill=OUT)
    d.line([(0, 0), (0, 7)], fill=OUT)
    for x0, x1, y in ((2, 3, 2), (5, 6, 2), (2, 2, 4), (4, 6, 4)):
        d.line([(x0, y), (x1, y)], fill=GLASS)
    d.line([(2, 5), (6, 5)], fill=GLASS_L)
    return im


def creole(colour, upper, ground, sign=None):
    """A Creole townhouse facade, three cells tall (the roof is Brick City's, stacked on by the prefab):
    upper and ground are strings of cell kinds: E corner, W wall, N window, D door, S shop front. The shop board
    hangs on the gallery over the door."""
    n = len(upper)
    im = Image.new("RGBA", (n * 16, 48), CLEAR)
    c, cd = CREOLE[colour]
    wall, wall_base = cr_stucco(c, cd), cr_stucco(c, cd, base=True)
    quoin, quoin_base = cr_quoin(), cr_quoin(base=True)
    cells = {"N": cr_window(), "D": cr_door(), "S": cr_shop()}
    for row, pattern in ((0, upper), (2, ground)):
        for i, k in enumerate(pattern):
            x0, y0 = i * 16, row * 16
            if k in cells:
                im.paste(cells[k], (x0, y0))
                continue
            low = wall_base if row == 2 else wall
            cell = quad_cell(wall, wall, low, low)
            if k == "E":
                left = i == 0
                q, qb = (quoin, quoin_base if row == 2 else quoin) if left else (hflip(quoin), hflip(quoin_base if row == 2 else quoin))
                cell = quad_cell(q, wall, qb, low) if left else quad_cell(wall, q, low, qb)
            im.paste(cell, (x0, y0))
    lt, lb = cr_lace()
    pt, pb = cr_lace(post=True)
    for i in range(n):
        if i == 0:
            cell = quad_cell(pt, lt, pb, lb)
        elif i == n - 1:
            cell = quad_cell(lt, hflip(pt), lb, hflip(pb))
        else:
            cell = quad_cell(lt, lt, lb, lb)
        im.paste(cell, (i * 16, 16))
    if sign:
        x0 = ground.index("D") * 16
        im.paste(cr_board_letters(), (x0, 16))
        im.paste(cr_board(sign), (x0 + 8, 16))
    return im


# ------------------------------------------------------------------ Waterfront: warehouses
def warehouse_roof(n):
    """A corrugated tin roof, two cells deep (stone colours): ridge cap along the top, gutter along the eave. The
    corrugation (2 px ridges, 2 px grooves) is symmetric inside every 8 px tile, so the right end is the left end
    mirrored and the whole roof is six tiles whatever its length."""
    im, d = canvas(n, 2)
    W = im.width
    for x in range(W):
        d.line([(x, 4), (x, 27)], fill=W1 if x % 4 in (1, 2) else W3)
    d.line([(0, 0), (W - 1, 0)], fill=OUT)
    d.rectangle([0, 1, W - 1, 2], fill=W0)           # ridge cap
    d.line([(0, 3), (W - 1, 3)], fill=W4)
    d.line([(0, 27), (W - 1, 27)], fill=W4)          # shadow under the gutter's lip
    d.rectangle([0, 28, W - 1, 29], fill=W1)         # gutter
    d.line([(0, 30), (W - 1, 30)], fill=W2)
    d.line([(0, 31), (W - 1, 31)], fill=OUT)
    for x in (0, W - 1):
        d.line([(x, 0), (x, 31)], fill=OUT)
    for x in (1, W - 2):
        d.line([(x, 4), (x, 27)], fill=W2)
    return im


def warehouse_wall(kinds, sign=None):
    """Three cells of lapped board siding (wood colours), on the 8 px grid so it repeats: kinds per column, 'C' a
    cargo door (two columns wide, two rows tall), 'D' the way in (a window above it), 'N' a window, 'W' plain
    boards; a painted sign board across the top. Doors, windows and the board's ends are mirror-symmetric."""
    n = len(kinds)
    im, d = canvas(n, 3)
    W, H = im.size
    CREAM = h("f8f0b8")
    for y in range(H):  # lapped boards: a lit edge, the board, the shadow line under the next one
        d.line([(0, y), (W - 1, y)], fill=(h("908030"), WOOD_L, WOOD, WOOD)[y % 4])

    def window(x0, y0):  # 8x6 window centred in a cell
        d.rectangle([x0 + 4, y0, x0 + 11, y0 + 5], fill=OUT)
        d.rectangle([x0 + 5, y0 + 1, x0 + 10, y0 + 4], fill=CREAM)
        d.line([(x0 + 7, y0 + 1), (x0 + 8, y0 + 1)], fill=WOOD_D)
        d.line([(x0 + 7, y0 + 1), (x0 + 7, y0 + 4)], fill=WOOD_D)
        d.line([(x0 + 8, y0 + 1), (x0 + 8, y0 + 4)], fill=WOOD_D)

    i = 0
    while i < n:
        k = kinds[i]
        x0 = i * 16
        if k == "C":  # plank doors, two columns wide, two rows tall: 6 px boards, a brace across, a lintel
            d.rectangle([x0, 16, x0 + 31, 47], fill=WOOD_D)
            for x in range(x0, x0 + 32):
                if x % 8 in (0, 7):
                    d.line([(x, 16), (x, 47)], fill=OUT)
                elif x % 8 == 1:
                    d.line([(x, 17), (x, 47)], fill=WOOD)
            d.line([(x0, 16), (x0 + 31, 16)], fill=OUT)
            d.rectangle([x0, 28, x0 + 31, 30], fill=WOOD_L)
            d.line([(x0, 31), (x0 + 31, 31)], fill=OUT)
            i += 2
            continue
        if k == "D":  # the way in: a plank door with a lit pane
            d.rectangle([x0 + 4, 33, x0 + 11, 47], fill=OUT)
            d.rectangle([x0 + 5, 34, x0 + 10, 47], fill=WOOD_D)
            d.rectangle([x0 + 6, 36, x0 + 9, 38], fill=CREAM)
            d.line([(x0 + 7, 34), (x0 + 8, 34)], fill=WOOD)
            P(d, x0 + 9, 42, CREAM)
            P(d, x0 + 6, 42, CREAM)
        if k in ("N", "D"):
            window(x0, 17)
        i += 1
    if sign:  # a long painted board across the top (a repeating pattern of lettering), its ends mirrored
        x0, x1 = sign[0] * 16, sign[1] * 16 + 15
        d.rectangle([x0, 1, x1, 7], fill=OUT)
        d.rectangle([x0 + 1, 2, x1 - 1, 6], fill=CREAM)
        for x in range(x0 + 8, x1 - 7):
            if x % 8 in (1, 2):
                d.line([(x, 3), (x, 5)], fill=h("c84050"))
            elif x % 8 in (5, 6):
                d.line([(x, 3), (x, 5)], fill=WOOD_D)
    d.line([(0, H - 2), (W - 1, H - 2)], fill=WOOD_D)
    d.line([(0, H - 1), (W - 1, H - 1)], fill=OUT)
    for x, xi in ((0, 1), (W - 1, W - 2)):  # corner boards
        d.line([(x, 0), (x, H - 1)], fill=OUT)
        d.line([(xi, 0), (xi, H - 2)], fill=WOOD_L)
    return im


# ------------------------------------------------------------------ Civic kit: the Battle Frontier and downtown
# White ashlar architecture as a kit of 8 px tiles (stone colours) shared by the seven Frontier facilities and the
# two downtown blocks: ashlar, the corner pier, the cornice, a window, the glass entrance and their plinth course.
# Every piece is mirror-symmetric (its right half is its left half flipped, a free copy), so a building costs its
# left half's distinct tiles; walls, cornices and roofs repeat every 8 px. Each Frontier facility keeps the shared
# hall at its foot and gets its own crown and colour: the Tower's battlements and blue glass, the Dome's glass
# dome, the Palace's orange tiles, the Arena's red-and-white canopy and pennants, the Factory's sawtooth roof and
# chimney, the Pike's steep teal roof of scales, the Pyramid's stepped sandstone.
SAND, SAND_D, SAND_DD = h("f8b880"), h("e89070"), h("d86860")
TEAL, TEAL_D = h("608888"), h("487070")


def k_ashlar(base=False):
    im, d = tile8()
    d.rectangle([0, 0, 7, 7], fill=W1)
    d.line([(0, 3), (7, 3)], fill=W2)
    d.line([(0, 7), (7, 7)], fill=W2)
    d.line([(0, 0), (0, 2)], fill=W2)
    d.line([(4, 4), (4, 6)], fill=W2)
    for x, y in ((1, 0), (2, 0), (5, 4), (6, 4)):  # lit top edges of the blocks
        P(d, x, y, W0)
    if base:  # the plinth course at the foot of the wall
        d.line([(0, 4), (7, 4)], fill=W0)
        d.line([(0, 5), (7, 5)], fill=W2)
        d.line([(0, 6), (7, 6)], fill=W3)
        d.line([(0, 7), (7, 7)], fill=OUT)
    return im


def k_pier(base=False):
    """The corner pier (the left one; the right one is its mirror image)."""
    im, d = tile8()
    d.rectangle([1, 0, 4, 7], fill=W0)
    d.line([(5, 0), (5, 7)], fill=W1)
    d.line([(6, 0), (6, 7)], fill=W2)
    d.line([(7, 0), (7, 7)], fill=W3)
    d.line([(1, 7), (5, 7)], fill=W2)
    d.line([(0, 0), (0, 7)], fill=OUT)
    if base:
        d.line([(1, 4), (7, 4)], fill=W0)
        d.line([(1, 5), (7, 5)], fill=W2)
        d.line([(1, 6), (7, 6)], fill=W3)
        d.line([(0, 7), (7, 7)], fill=OUT)
    return im


def k_cornice(end=False):
    im, d = tile8()
    d.line([(0, 0), (7, 0)], fill=OUT)
    d.rectangle([0, 1, 7, 2], fill=W0)
    d.line([(0, 3), (7, 3)], fill=W2)
    for x in range(8):  # dentils
        P(d, x, 4, W0 if x % 4 in (1, 2) else W3)
    d.line([(0, 5), (7, 5)], fill=W3)
    d.line([(0, 6), (7, 6)], fill=W1)
    d.line([(0, 7), (7, 7)], fill=W2)
    if end:
        d.line([(0, 0), (0, 7)], fill=OUT)
    return im


def k_window():
    """A window in the ashlar: white frame, dark glass with a glint, a sill."""
    im, d = tile8()
    d.rectangle([0, 0, 7, 7], fill=W1)
    d.line([(0, 7), (7, 7)], fill=W2)
    d.rectangle([1, 0, 6, 6], fill=W0)
    d.rectangle([2, 1, 5, 5], fill=IRON)
    d.line([(2, 1), (5, 1)], fill=OUT)
    for x, y in ((2, 2), (3, 2), (2, 3)):
        P(d, x, y, W3)
    d.line([(1, 7), (6, 7)], fill=W3)
    return im


def k_door():
    """The glass entrance (left half of a 16 px door on the axis): a white surround, sliding glass doors."""
    t, dt = tile8()
    b, db = tile8()
    for d in (dt, db):
        d.rectangle([0, 0, 7, 7], fill=W0)
        d.line([(1, 0), (1, 7)], fill=W2)
    dt.line([(0, 0), (7, 0)], fill=W2)
    dt.line([(2, 2), (7, 2)], fill=OUT)
    dt.rectangle([2, 3, 7, 7], fill=IRON)
    db.rectangle([2, 0, 7, 5], fill=IRON)
    for x, y in ((3, 4), (4, 4), (3, 5)):
        P(dt, x, y, W3)
    P(db, 3, 1, W3)
    db.line([(6, 1), (6, 3)], fill=W3)  # handle
    db.line([(7, 0), (7, 5)], fill=OUT)  # the doors meet (2 px with the mirror)
    dt.line([(7, 3), (7, 7)], fill=OUT)
    db.line([(0, 5), (7, 5)], fill=W2)
    db.line([(0, 6), (7, 6)], fill=W3)
    db.line([(0, 7), (7, 7)], fill=OUT)
    P(db, 1, 5, W2)
    return t, b


KIT = {}


def kit():
    if not KIT:
        dt, db = k_door()
        KIT.update(A=k_ashlar(), Ab=k_ashlar(True), P=k_pier(), Pb=k_pier(True), C=k_cornice(), Ce=k_cornice(True),
                   N=k_window(), Dt=dt, Db=db)
    return KIT


def sym_tiles(rows):
    """An image from its left half's grid of 8x8 tiles (None: empty); the right half is the mirror image."""
    n = len(rows[0])
    im = Image.new("RGBA", (n * 16, len(rows) * 8), CLEAR)
    for j, row in enumerate(rows):
        for i, t in enumerate(row):
            if t is not None:
                im.paste(t, (i * 8, j * 8))
                im.paste(hflip(t), ((2 * n - 1 - i) * 8, j * 8))
    return im


def tiles_of(im, x0, y0, cols, rows):
    """Cut an image (drawn as a left half) into a grid of 8x8 tiles."""
    return [[im.crop((x0 + i * 8, y0 + j * 8, x0 + i * 8 + 8, y0 + j * 8 + 8)) for i in range(cols)] for j in range(rows)]


def hall_rows(windows="..N.."):
    """The facility's hall: cornice, a row of wall with its windows ('N' per tile column of the left half: each
    facility its own arrangement, free), the ground floor with the entrance (the left half of a five-cell front)."""
    k = kit()
    return [[k["Ce"], k["C"], k["C"], k["C"], k["C"]],
            [k["P"]] + [k["N"] if c == "N" else k["A"] for c in windows[1:]],
            [k["P"], k["A"], k["A"], k["A"], k["Dt"]],
            [k["Pb"], k["Ab"], k["Ab"], k["Ab"], k["Db"]]]


def crown_canvas(rows):
    """A left-half canvas (40 px wide) for a crown `rows` tiles tall."""
    im = Image.new("RGBA", (40, rows * 8), CLEAR)
    return im, ImageDraw.Draw(im)


def fac_tower():
    """Battle Tower, 5x5: a slim keep (32 px) rising behind the hall, battlements on a cornice, a strip of blue
    glass up its middle; the hall's cornice runs across its foot."""
    im, d = crown_canvas(6)
    x0 = 24  # the keep's left wall
    # battlements: merlons with the roof showing between them, the parapet's face below
    d.rectangle([x0, 0, 39, 7], fill=W1)
    for a, b in ((x0, 30), (36, 39)):
        d.rectangle([a, 0, b, 3], fill=W0)
        d.line([(a, 0), (b, 0)], fill=OUT)
    d.rectangle([31, 1, 35, 3], fill=W3)  # the crenel: the roof behind, in shade
    d.line([(31, 1), (35, 1)], fill=OUT)
    d.line([(x0, 4), (39, 4)], fill=W2)
    d.line([(x0, 7), (39, 7)], fill=W3)
    d.line([(x0, 0), (x0, 7)], fill=OUT)
    # the shaft (rows 2..5): ashlar (8 px periodic), the glass strip on the axis (x 36..43 with the mirror)
    for y in range(16, 48):
        for x in range(x0, 36):
            c = W1
            if y % 8 in (3, 7) or (x % 8 == 0 and y % 8 < 3) or (x % 8 == 4 and 3 < y % 8 < 7):
                c = W2
            P(d, x, y, c)
        d.line([(36, y), (39, y)], fill=WISP if y % 8 not in (0, 7) else W3)
        P(d, 36, y, W0)
        if y % 8 in (2, 3):
            P(d, 38, y, WISP_L)
    d.line([(x0, 16), (x0, 47)], fill=OUT)
    d.line([(x0 + 1, 16), (x0 + 1, 47)], fill=W0)
    k = kit()
    top = tiles_of(im, 0, 0, 5, 6)
    top[1] = [None, None, None, k["Ce"], k["C"]]  # the battlements stand on a cornice
    for row in top:
        for i in range(3):
            row[i] = None
    return sym_tiles(top + hall_rows("..N.."))


def fac_dome():
    """Battle Dome, 5x4: a glass dome (a lattice of panes, 8 px periodic inside) on the hall."""
    im, d = crown_canvas(4)
    cx, base, r = 40, 32, 30
    for y in range(base - r, base):
        w = (r * r - (base - y) ** 2) ** 0.5
        xl = int(round(cx - w))
        for x in range(max(0, xl), cx):
            c = WISP
            if x % 8 == 4 or y % 8 == 4:
                c = W3  # mullions
            P(d, x, y, c)
    # highlights on the upper left, a finial
    for x, y in ((22, 10), (23, 10), (21, 11), (20, 12), (19, 13), (26, 7), (27, 7), (28, 6)):
        P(d, x, y, W1)
    d.rectangle([cx - 1, 0, cx - 1, 2], fill=W0)
    full = Image.new("RGBA", (80, 32), CLEAR)
    full.paste(im, (0, 0))
    full.paste(hflip(im), (40, 0))
    outline(full)
    return sym_tiles(tiles_of(full, 0, 0, 5, 4) + hall_rows(".N.N."))


def fac_palace():
    """Battle Palace, 5x3: a low hip roof of orange clay tiles (hips 1 in 1, so the edge tile repeats) on the
    hall."""
    im, d = crown_canvas(2)
    for y in range(16):
        xe = 15 - y  # the hip edge
        for x in range(max(0, xe), 40):
            if x == xe:
                c = OUT
            elif y % 4 == 0:
                c = SAND_DD
            elif y % 4 == 1 and x % 4 in (0, 1):
                c = SAND
            else:
                c = SAND_D
            P(d, x, y, c)
    d.line([(16, 0), (39, 0)], fill=OUT)  # ridge
    d.line([(16, 1), (39, 1)], fill=SAND)
    d.line([(0, 14), (39, 14)], fill=SAND_DD)  # eave
    d.line([(0, 15), (39, 15)], fill=OUT)
    return sym_tiles(tiles_of(im, 0, 0, 5, 2) + hall_rows("...NN"))


def fac_arena():
    """Battle Arena, 5x4: a red-and-white striped canopy (its edges fall 1 in 2 from the apex, so they repeat down
    the slope) with a scalloped valance, a forked pennant flying from the apex."""
    im, d = crown_canvas(4)
    cx = 40
    stripe = lambda x: RED if x % 8 in (6, 7, 0, 1) else W0
    for y in range(4, 24):
        xe = cx - 2 * (y - 4)
        for x in range(max(0, xe - 2), cx):
            if x < xe:
                c = OUT
            else:
                c = stripe(x)
                if y % 8 == 3:  # a seam every 8 rows
                    c = RED_L if c == RED else W2
            P(d, x, y, c)
    for x in range(cx):  # the valance, and the deep shade under the canopy
        c = stripe(x)
        d.line([(x, 24), (x, 26)], fill=c)
        P(d, x, 27, c if x % 4 in (1, 2) else OUT)
        d.line([(x, 28), (x, 31)], fill=OUT)
    d.line([(0, 24), (0, 27)], fill=OUT)
    # a flagstaff on the apex flying a forked pennant
    d.line([(39, 0), (39, 5)], fill=IRON)
    P(d, 39, 0, GOLD)
    d.polygon([(38, 1), (33, 2), (35, 3), (33, 4), (38, 4)], fill=RED)
    P(d, 37, 2, RED_L)
    return sym_tiles(tiles_of(im, 0, 0, 5, 4) + hall_rows(".N..."))


def fac_factory():
    """Battle Factory, 5x3: a sawtooth roof of north lights (a tooth every 8 px: a slope, then a glazed face) and a
    brick chimney on the axis."""
    im, d = crown_canvas(2)
    for x in range(40):
        t = x % 8
        if t == 7:  # the glazed face of the tooth
            d.line([(x, 1), (x, 12)], fill=W3)
            P(d, x, 0, OUT)
            P(d, x, 2, W0)
            continue
        top = 7 - t
        d.line([(x, top + 1), (x, 12)], fill=W4)
        P(d, x, top, OUT)
        P(d, x, top + 1, W2)  # the lit slope
        if t == 6:
            d.line([(x, 2), (x, 7)], fill=WISP)
    d.line([(0, 8), (39, 8)], fill=W5)  # the gutter between the teeth and the roof's front
    d.line([(0, 12), (39, 12)], fill=W5)
    d.line([(0, 13), (39, 13)], fill=W2)
    d.line([(0, 14), (39, 14)], fill=W1)
    d.line([(0, 15), (39, 15)], fill=OUT)
    d.line([(0, 0), (0, 15)], fill=OUT)
    # the chimney on the axis (x 36..43 with the mirror): brick, a dark cap
    d.rectangle([36, 0, 39, 13], fill=RED)
    for y in range(0, 14):
        if y % 4 == 3:
            d.line([(36, y), (39, y)], fill=RED_L)
        elif (y // 4) % 2 == 0:
            P(d, 38, y, RED_L)
    d.line([(35, 0), (35, 13)], fill=OUT)
    d.rectangle([35, 0, 39, 1], fill=OUT)
    return sym_tiles(tiles_of(im, 0, 0, 5, 2) + hall_rows(".NNN."))


def fac_pike():
    """Battle Pike, 5x4: a steep roof of dark teal scales (edges 1 in 1, so the edge tile repeats down the slope)
    with a pair of yellow snake's eyes, a spire, the entrance at its foot."""
    im, d = crown_canvas(6)
    for y in range(8, 48):
        xe = 47 - y
        for x in range(max(0, xe), 40):
            if x == xe:
                c = OUT
            else:
                c = TEAL_D
                if (y % 4 == 0 and x % 4 in (1, 2)) or (y % 4 == 2 and x % 4 in (3, 0)):
                    c = TEAL  # scales
                elif (y % 4 == 1 and x % 4 == 2) or (y % 4 == 3 and x % 4 == 0):
                    c = W3
            P(d, x, y, c)
    d.line([(0, 46), (39, 46)], fill=TEAL)
    d.line([(0, 47), (39, 47)], fill=OUT)
    # a pair of yellow snake's eyes in the roof, looking out over the plaza (the right one is the mirror image)
    d.polygon([(33, 27), (35, 26), (37, 27), (35, 29)], fill=SAND)
    d.line([(33, 27), (35, 25)], fill=OUT)
    d.line([(35, 25), (37, 27)], fill=OUT)
    P(d, 35, 26, OUT)
    P(d, 35, 27, OUT)  # the slit pupil
    P(d, 34, 27, W0)
    d.line([(33, 28), (35, 30)], fill=OUT)
    d.line([(35, 30), (37, 28)], fill=OUT)
    # spire
    d.rectangle([38, 1, 39, 7], fill=IRON)
    P(d, 39, 0, GOLD)
    P(d, 38, 0, OUT)
    P(d, 37, 4, OUT)
    return sym_tiles(tiles_of(im, 0, 0, 5, 6) + hall_rows()[2:])


def fac_pyramid():
    """Battle Pyramid, 5x4: stepped sandstone, each step 8 px up and 8 px in (one tile repeats for every step's
    end, one for the courses), a dark doorway at its foot."""
    S, F, Sd, Fb, St = (tile8() for _ in range(5))
    s, ds = S
    f, df = F

    def course(dd, x0=0):
        dd.rectangle([x0, 0, 7, 7], fill=SAND)
        dd.line([(x0, 0), (7, 0)], fill=W0 if x0 == 0 else SAND)  # the tread, lit
        dd.line([(x0, 1), (7, 1)], fill=SAND)
        dd.line([(x0, 5), (7, 5)], fill=SAND_D)
        dd.line([(x0, 7), (7, 7)], fill=SAND_DD)
        P(dd, 3, 2, SAND_D)
        P(dd, 7, 3, SAND_D)
    course(df)
    course(ds)
    ds.line([(0, 0), (7, 0)], fill=OUT)  # the step's top edge and end
    ds.line([(0, 1), (7, 1)], fill=W0)
    ds.line([(0, 0), (0, 7)], fill=OUT)
    ds.line([(1, 1), (1, 7)], fill=SAND_D)
    ds.line([(0, 7), (7, 7)], fill=SAND_DD)
    sd, dsd = Sd  # the side below the last step
    course(dsd)
    dsd.line([(0, 0), (0, 7)], fill=OUT)
    dsd.line([(1, 0), (1, 7)], fill=SAND_D)
    fb, dfb = Fb  # the foot: the last course and the ground line
    course(dfb)
    dfb.line([(0, 6), (7, 6)], fill=SAND_DD)
    dfb.line([(0, 7), (7, 7)], fill=OUT)
    sb = sd.copy()
    dsb = ImageDraw.Draw(sb)
    dsb.line([(0, 6), (7, 6)], fill=SAND_DD)
    dsb.line([(0, 7), (7, 7)], fill=OUT)
    # the doorway: a dark trapezoid under a lintel (left half)
    st, dst = St
    course(dst)
    dst.rectangle([1, 2, 7, 3], fill=SAND_DD)  # lintel
    dst.line([(1, 1), (7, 1)], fill=OUT)
    dst.rectangle([4, 4, 7, 7], fill=OUT)
    P(dst, 3, 7, OUT)
    dst.line([(3, 4), (3, 6)], fill=SAND_D)
    db_ = Image.new("RGBA", (8, 8), CLEAR)
    ddb = ImageDraw.Draw(db_)
    course(ddb)
    ddb.rectangle([3, 0, 7, 7], fill=OUT)
    ddb.line([(2, 0), (2, 6)], fill=SAND_D)
    ddb.line([(0, 6), (2, 6)], fill=SAND_DD)
    ddb.line([(0, 7), (7, 7)], fill=OUT)
    rows = [[None] * (4 - r) + [s] + [f] * r for r in range(5)]  # steps: row r ends at column 4 - r
    rows += [[s, f, f, f, f], [s, f, f, f, st], [sb, fb, fb, fb, db_]]
    return sym_tiles(rows)


def block_dept():
    """The Department Store, 7x5, door (3, 4): three storeys of ashlar under a flat roof and the cornice, windows in
    bays, a DEPT STORE band, a red-and-white awning over shop windows and the glass entrance."""
    k = kit()
    roof, droof = tile8()
    droof.rectangle([0, 0, 7, 7], fill=W3)
    droof.line([(0, 0), (7, 0)], fill=OUT)
    droof.line([(0, 1), (7, 1)], fill=W2)
    for x in (2, 6):
        droof.line([(x, 3), (x + 1, 3)], fill=W2)
    droof.line([(0, 6), (7, 6)], fill=W1)  # the parapet's coping
    droof.line([(0, 7), (7, 7)], fill=W0)
    roof_end = roof.copy()
    de = ImageDraw.Draw(roof_end)
    de.line([(0, 0), (0, 7)], fill=OUT)
    de.line([(1, 1), (1, 7)], fill=W1)
    band, dband = tile8()
    dband.rectangle([0, 0, 7, 7], fill=DARK)
    dband.line([(0, 0), (7, 0)], fill=W2)
    dband.line([(0, 7), (7, 7)], fill=W2)
    dband.line([(0, 1), (7, 1)], fill=IRON)
    awn, dawn = tile8()
    for x in range(8):
        c = RED if x % 8 in (6, 7, 0, 1) else W0
        dawn.line([(x, 0), (x, 4)], fill=c)
        P(dawn, x, 5, c if x % 4 in (1, 2) else IRON)
    dawn.line([(0, 2), (7, 2)], fill=W2)
    for x in range(8):
        if x % 8 in (6, 7, 0, 1):
            P(dawn, x, 2, RED_L)
    dawn.line([(0, 6), (7, 6)], fill=IRON)
    dawn.line([(0, 7), (7, 7)], fill=W0)
    gt, dgt = tile8()  # display windows: big panes, a white frame every 8 px
    dgt.rectangle([0, 0, 7, 7], fill=W0)
    dgt.rectangle([1, 1, 7, 7], fill=IRON)
    for x, y in ((2, 3), (3, 2), (4, 1), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2)):
        P(dgt, x, y, W3)
    gb, dgb = tile8()
    dgb.rectangle([0, 0, 7, 7], fill=W0)
    dgb.rectangle([1, 0, 7, 3], fill=IRON)
    P(dgb, 2, 1, W3)
    dgb.line([(0, 4), (7, 4)], fill=W0)
    dgb.line([(0, 5), (7, 5)], fill=W2)
    dgb.line([(0, 6), (7, 6)], fill=W3)
    dgb.line([(0, 7), (7, 7)], fill=OUT)
    A, N, P_ = k["A"], k["N"], k["P"]
    rows = [[roof_end] + [roof] * 6,
            [k["Ce"]] + [k["C"]] * 6,
            [P_, N, A, N, A, N, A],
            [P_, A, A, A, A, A, A],
            [P_, N, A, N, A, N, A],
            [P_, A, A, A, A, A, A],
            [P_, band, band, band, band, band, band],
            [P_, awn, awn, awn, awn, awn, awn],
            [P_, gt, gt, gt, gt, gt, k["Dt"]],
            [k["Pb"], gb, gb, gb, gb, gb, k["Db"]]]
    im = sym_tiles(rows)
    # the lettering, centred on the axis (x 32..79): 4x5 capitals, 1 px apart
    font = {"D": ["111.", "1..1", "1..1", "1..1", "111."], "E": ["1111", "1...", "111.", "1...", "1111"],
            "P": ["111.", "1..1", "111.", "1...", "1..."], "T": ["1111", ".1..", ".1..", ".1..", ".1.."],
            "S": [".111", "1...", ".11.", "...1", "111."], "O": [".11.", "1..1", "1..1", "1..1", ".11."],
            "R": ["111.", "1..1", "111.", "1.1.", "1..1"]}
    d = ImageDraw.Draw(im)
    x = 32 + 1
    for ch in "DEPT STORE":
        if ch == " ":
            x += 3
            continue
        for j, line in enumerate(font[ch]):
            for i, b in enumerate(line):
                if b == "1":
                    P(d, x + i, 48 + 2 + j, W0)
        x += 5
    return im


def gym_tiles():
    """The gym's column, its capital and base, the shaded wall behind the colonnade and the dentil band, cut from
    the gym itself so the Conservation Center's portico shares them."""
    g = mirror(gym())
    cut = lambda x, y: g.crop((x, y, x + 8, y + 8))
    return dict(cap=cut(16, 40), shaft=cut(16, 48), base=cut(16, 72), shade=cut(8, 48), dentil=cut(8, 32))


def block_hall():
    """The Conservation Center, 9x5, door (4, 4): a civic hall with a teal copper roof, a pediment with a gold
    trilobite over a portico of four columns (the gym's), wings of windows, the glass entrance on the axis."""
    k = kit()
    g = gym_tiles()
    A, N, P_ = k["A"], k["N"], k["P"]
    # the roof: teal scales (the Pike's), seen as a band over the wings, its hipped ends 1 in 1
    im = Image.new("RGBA", (72, 24), CLEAR)
    d = ImageDraw.Draw(im)
    for y in range(24):
        xe = 15 - y if y < 16 else 0
        for x in range(max(0, xe), 72):
            if x == xe and y < 16:
                c = OUT
            else:
                c = TEAL_D
                if (y % 4 == 0 and x % 4 in (1, 2)) or (y % 4 == 2 and x % 4 in (3, 0)):
                    c = TEAL
                elif (y % 4 == 1 and x % 4 == 2) or (y % 4 == 3 and x % 4 == 0):
                    c = W3
            P(d, x, y, c)
    d.line([(16, 0), (71, 0)], fill=OUT)
    d.line([(0, 15), (0, 23)], fill=OUT)
    # the pediment over the portico (x 40..71 on the left half), 1 in 2, a gold ammonite in the tympanum
    for x in range(40, 72):
        top = 23 - (x - 40) // 2
        d.line([(x, top), (x, 23)], fill=W1)
        P(d, x, top, OUT)
        P(d, x, top + 1, W0)
        if top + 4 < 22:
            d.line([(x, top + 4), (x, 22)], fill=W3)
    d.line([(40, 23), (71, 23)], fill=W2)
    # a gold trilobite (a fossil that is symmetric anyway): head shield, segmented body, the axial lobe
    d.ellipse([65, 12, 78, 23], fill=GOLD, outline=OUT)  # clipped at the axis: the mirror completes it
    d.line([(66, 15), (71, 15)], fill=GOLD_L)  # the head shield's rim
    for y in (17, 19, 21):  # body segments
        d.line([(67, y), (71, y)], fill=GOLD_L)
    d.line([(70, 13), (70, 22)], fill=GOLD_L)  # the axial lobe (x 70..73 with the mirror)
    P(d, 68, 14, OUT)  # an eye
    top = tiles_of(im, 0, 0, 9, 3)
    col = lambda t: [t, g["shade"], t, g["shade"]]  # columns at tile columns 5 and 7, the shaded wall between
    rows = top + [
        [k["Ce"]] + [k["C"]] * 8,
        [P_, A, N, A, N] + col(g["cap"]),
        [P_, A, A, A, A] + col(g["shaft"]),
        [P_, A, N, A, N] + col(g["shaft"]),
        [P_, A, A, A, A] + col(g["shaft"]),
        [P_, A, A, A, A] + col(g["base"])[:3] + [k["Dt"]],
        [k["Pb"]] + [k["Ab"]] * 7 + [k["Db"]]]
    return sym_tiles(rows)


def warehouse_wall_b(kinds):
    """The other kind of warehouse wall (stone colours): corrugated metal siding, a sectional sliding door on its
    rail ('C', two columns wide, two rows tall), the glass door ('D') and the windows ('N') of the civic kit, so it
    adds only the siding and the sliding door. Same kinds and sizes as warehouse_wall."""
    n = len(kinds)
    W, H = n * 16, 48
    k = kit()
    sid, d1 = tile8()
    for x in range(8):  # dark grey corrugation under the light tin roof
        d1.line([(x, 0), (x, 7)], fill=W4 if x % 4 in (1, 2) else W5)
    sid_b = sid.copy()
    d2 = ImageDraw.Draw(sid_b)
    d2.line([(0, 6), (7, 6)], fill=IRON)
    d2.line([(0, 7), (7, 7)], fill=OUT)
    edge = sid.copy()
    d3 = ImageDraw.Draw(edge)
    d3.line([(0, 0), (0, 7)], fill=OUT)
    d3.line([(1, 0), (1, 7)], fill=W2)
    edge_b = sid_b.copy()
    d4 = ImageDraw.Draw(edge_b)
    d4.line([(0, 0), (0, 7)], fill=OUT)
    d4.line([(1, 0), (1, 5)], fill=W2)
    door = []
    for part in ("top", "mid", "bot"):  # a painted sectional door, ribbed, on its rail
        t, dd = tile8()
        dd.rectangle([0, 0, 7, 7], fill=W3)
        dd.line([(0, 0), (0, 7)], fill=OUT)
        dd.line([(7, 0), (7, 7)], fill=OUT)
        dd.line([(1, 0), (1, 7)], fill=W2)
        dd.line([(1, 3), (6, 3)], fill=W2)  # a rib, lit above, shaded below
        dd.line([(1, 4), (6, 4)], fill=W4)
        if part == "top":
            dd.rectangle([0, 0, 7, 1], fill=IRON)  # the rail and a roller
            dd.line([(0, 0), (7, 0)], fill=OUT)
            P(dd, 4, 1, W3)
        if part == "bot":
            dd.line([(0, 6), (7, 6)], fill=W4)
            dd.line([(0, 7), (7, 7)], fill=OUT)
        door.append(t)
    grid = [[sid] * (2 * n) for _ in range(6)]
    for j in range(6):
        grid[j][0] = edge_b if j == 5 else edge
        grid[j][2 * n - 1] = hflip(edge_b if j == 5 else edge)
        if j == 5:
            for i in range(1, 2 * n - 1):
                grid[j][i] = sid_b
    i = 0
    while i < n:
        kd = kinds[i]
        if kd == "C":
            for c in range(4):
                for j, t in zip(range(2, 6), (door[0], door[1], door[1], door[2])):
                    grid[j][2 * i + c] = t
            i += 2
            continue
        if kd in ("N", "D"):
            grid[2][2 * i] = k["N"]
            grid[2][2 * i + 1] = hflip(k["N"])
        if kd == "D":
            grid[4][2 * i], grid[4][2 * i + 1] = k["Dt"], hflip(k["Dt"])
            grid[5][2 * i], grid[5][2 * i + 1] = k["Db"], hflip(k["Db"])
        i += 1
    im = Image.new("RGBA", (W, H), CLEAR)
    for j, row in enumerate(grid):
        for i2, t in enumerate(row):
            im.paste(t, (i2 * 8, j * 8))
    return im


# ------------------------------------------------------------------ plaza and street props (mirror-symmetric)
TERRA, TERRA_D = h("f09038"), h("c84050")


def trough():
    """A drinking fountain for the Frontier plaza, 2x2: a stone post with a spout running into a low basin.
    Left half drawn, mirrored."""
    im, d = canvas(2, 2)
    cx = 16
    # the post (x 12..19 with the mirror), its cap, the spout and the stream
    d.rectangle([11, 4, cx - 1, 6], fill=W0)
    d.line([(11, 7), (cx - 1, 7)], fill=W2)
    d.rectangle([12, 8, cx - 1, 21], fill=W1)
    d.line([(12, 8), (12, 21)], fill=W2)
    d.line([(14, 4), (cx - 1, 4)], fill=W1)
    P(d, cx - 1, 2, W2)
    P(d, cx - 1, 3, W1)  # a finial knob
    d.rectangle([14, 10, cx - 1, 11], fill=W3)  # the spout's mask
    P(d, cx - 1, 11, OUT)
    for y in range(12, 20):  # the stream
        P(d, cx - 1, y, WISP if y % 3 else W0)
    # the basin (outlined by hand along its top, so nothing spills into the row above): rim, water, front wall
    d.line([(0, 16), (11, 16)], fill=OUT)
    d.rectangle([1, 17, cx - 1, 18], fill=W0)
    d.rectangle([2, 19, cx - 1, 23], fill=WATER)
    d.line([(2, 19), (cx - 1, 19)], fill=WATER_D)
    for x, y in ((4, 21), (5, 21), (8, 22), (9, 22)):
        P(d, x, y, W2)
    d.rectangle([12, 16, 13, 21], fill=W1)  # the post standing in the water
    d.line([(12, 16), (12, 21)], fill=W2)
    P(d, 14, 21, W0)  # splash
    P(d, cx - 1, 21, W0)
    P(d, 14, 22, W2)
    d.rectangle([1, 24, cx - 1, 29], fill=W1)
    d.line([(1, 24), (cx - 1, 24)], fill=W0)
    for x in range(1, cx):
        if x % 8 == 4:
            d.line([(x, 25), (x, 29)], fill=W2)
    d.line([(1, 30), (cx - 1, 30)], fill=W3)
    d.line([(1, 17), (1, 30)], fill=W2)
    d.line([(0, 16), (0, 31)], fill=OUT)
    d.line([(0, 31), (cx - 1, 31)], fill=OUT)
    mirror(im)
    outline(im)
    return im


def pot(top):
    """A terracotta pot (its lower tile shared by every pot), holding flowers or a clipped box ball (the upper
    tile), mirror-symmetric."""
    im, d = canvas(1, 1)
    d.rectangle([4, 8, 11, 9], fill=TERRA)  # rim
    d.line([(5, 10), (10, 10)], fill=TERRA_D)
    d.rectangle([5, 11, 10, 12], fill=TERRA)
    d.rectangle([6, 13, 9, 13], fill=TERRA)
    d.line([(6, 14), (9, 14)], fill=TERRA_D)
    for y in (11, 12):
        P(d, 5, y, TERRA_D)
        P(d, 10, y, TERRA_D)
    P(d, 6, 13, TERRA_D)
    P(d, 9, 13, TERRA_D)
    d.ellipse([3, 0, 12, 7], fill=LEAF)  # the same outline for both, so the pot tile is shared
    if top == "flowers":
        for x, y, c in ((5, 2, RED), (7, 1, YELLOW), (4, 4, PINK), (6, 5, W0), (7, 3, RED), (5, 6, YELLOW)):
            P(d, x, y, c)
        for x, y in ((6, 3), (4, 6), (7, 6)):
            P(d, x, y, LEAF_L)
    else:  # a clipped box ball
        d.ellipse([4, 1, 9, 5], fill=LEAF_M)
        for x, y in ((5, 2), (7, 3), (4, 5), (6, 1)):
            P(d, x, y, LEAF_L)
        for x, y in ((4, 6), (6, 7), (3, 4)):
            P(d, x, y, LEAF_D)
    mirror(im)
    outline(im, color=h("303028"))
    return im


def flower_cart():
    """A flower seller's cart, 2x1: buckets of flowers on a plank cart between two wheels, mirror-symmetric."""
    im, d = canvas(2, 1)
    cx = 16
    d.rectangle([2, 4, cx - 1, 9], fill=GREEN_L)  # foliage
    blooms = (RED, ORANGE, PURPLE, h("f8f0b8"), h("d86860"))
    for i, x in enumerate(range(3, cx, 3)):
        for dy in (0, 3):
            P(d, x, 4 + dy + (i % 2), blooms[(i + dy) % len(blooms)])
            P(d, x + 1, 4 + dy + (i % 2), blooms[(i + dy + 2) % len(blooms)])
    for x in range(2, cx):
        if x % 3 == 0:
            P(d, x, 3, GREEN_L)
    d.rectangle([1, 9, cx - 1, 12], fill=WOOD)  # the cart box
    d.line([(1, 9), (cx - 1, 9)], fill=WOOD_L)
    d.line([(1, 11), (cx - 1, 11)], fill=WOOD_D)
    for x in range(1, cx):
        if x % 4 == 0:
            P(d, x, 10, WOOD_D)
    d.ellipse([1, 10, 7, 15], fill=h("404868"))  # a wheel
    d.ellipse([3, 11, 5, 14], fill=h("787880"))
    P(d, 4, 12, h("404868"))
    mirror(im)
    outline(im)
    return im


def barrel():
    """A cooper's barrel: the lid, staves, two iron hoops, mirror-symmetric."""
    im, d = canvas(1, 1)
    d.rectangle([3, 4, 12, 14], fill=WOOD)
    d.ellipse([3, 1, 12, 6], fill=WOOD_L)
    d.ellipse([5, 2, 10, 5], fill=h("908030"))
    d.ellipse([6, 3, 9, 4], fill=WOOD_L)
    for x in (5, 7):
        d.line([(x, 6), (x, 14)], fill=h("908030"))
        d.line([(15 - x, 6), (15 - x, 14)], fill=h("908030"))
    for y in (7, 12):
        d.line([(3, y), (12, y)], fill=h("404868"))
    d.line([(3, 4), (3, 14)], fill=WOOD_D)
    mirror(im)
    outline(im)
    return im


def main():
    """Each piece goes on the sheet of its colour family (crescent_<family>.png), so compose builds one palette
    group per family that lines up with the tileset's own palettes."""
    sheets = {f: Sheet(rows=48) for f in FAMILY}
    sheets.update({f + "_raw": Sheet(rows=4) for f in ("wood", "leaf", "stone")})

    def place(fam, name, art, raw=False, **kw):
        """raw: an opaque piece placed as its own metatile, not drawn over the terrain (costs no ground copies)."""
        snap(art, fam)
        sheets[fam + ("_raw" if raw else "")].place(name, art, **kw)

    place("stone", "gym", mirror(gym()), doors=[(3, 4)], passable=[(2, 5), (3, 5), (4, 5)],
          comment="Fifolet gym: marble temple-mausoleum (own art), 7x6, door (3,4), steps walkable.")
    place("brick", "ruin_a", ruin_a(), comment="Drowned Ward ruin: roofless brick shell (own art), 4x3.")
    place("brick", "ruin_door", ruin_a(door=True), doors=[(1, 2)],
          comment="Drowned Ward ruin with a barred cellar door (own art), 4x3, door (1,2).")
    place("brick", "ruin_b", ruin_b(), comment="Drowned Ward ruin: broken gable end and chimney (own art), 3x3.")
    place("stone", "crypt", mirror(crypt()), comment="The oldest crypt: society tomb with columns and urns (own art), 3x3.")
    place("stone", "fountain", mirror(fountain()), comment="Tiered stone fountain (own art), 3x3.")
    place("stone", "vault", mirror(vault()), comment="Wall of oven vaults (own art), 3x2.")
    st = stall(RED)
    place("stone", "stall_top", st.crop((0, 0, st.width, 16)), comment="Market stall awning (own art).")
    place("wood", "stall_base", st.crop((0, 16, st.width, 32)), comment="Market stall counter (own art).")
    place("stone", "tomb", mirror(tomb()), comment="Whitewashed family tomb (own art), 2x2.")
    place("stone", "tomb_box", tomb_box(), comment="Low box tomb (own art), 2x1.")
    place("stone", "obelisk", mirror(obelisk()), comment="Stone obelisk (own art), 1x3.")
    for k in ("l", "m", "r", "fern"):
        place("stone", f"bal_{k}", balcony(k), passable=[(0, 0)], comment="Iron balcony railing (own art), over a brick wall.")
    for k in ("l", "m", "r"):
        place("leaf", f"hedge_{k}", hedge(k), comment="Clipped box hedge (own art).")
    place("leaf", "pgrass", tallgrass(True), passable=[(0, 0)], comment="Park tall grass (own art), wild encounters.")
    place("leaf", "pgrass_rim", tallgrass(False), passable=[(0, 0)], comment="Park tall grass, the patch's soft edge.")
    place("leaf", "flowerbed", flowerbed(), raw=True, passable=[(0, 0)], comment="Formal flower bed (own art), walkable.")
    place("stone", "mailbox", mailbox(), comment="Mailbox (own art).")
    place("stone", "bin", bin_(), comment="Litter bin (own art).")
    place("stone", "gazebo", gazebo(), comment="Park bandstand: white gazebo, verdigris roof (own art), 4x4.")
    # French Quarter townhouses (facades; the prefab stacks Brick City's slate roof on top)
    for name, colour, upper, ground, icon in (
            ("creole_cafe", "pink", "ENWWNE", "ESDSNE", "cafe"), ("creole_salon", "blue", "ENWNE", "ENDSE", "salon"),
            ("creole_laundry", "yellow", "ENWWNE", "ESDSSE", "laundry"),
            ("creole_apartment", "green", "ENNE", "EDNE", "apts"),
            ("creole_trades", "pink", "ENWWNE", "ESDSNE", "trades"),
            ("creole_gamecorner", "yellow", "ENWWNE", "ESDSSE", "coins"),
            ("creole_icecream", "green", "ENWWNE", "EDSSSE", "icecream"),
            ("creole_daycare", "blue", "ENWNE", "ENDNE", "egg"),
            ("creole_namerater", "pink", "ENE", "EDE", "quill"), ("creole_tutor", "blue", "ENE", "EDE", "book")):
        place("creole", name, creole(colour, upper, ground, icon), doors=[(ground.index("D"), 2)],
              comment=f"Creole townhouse facade, {colour} stucco, iron gallery, a {icon} board (own art).")
    # waterfront warehouses: tin roofs over board siding with cargo doors (roof and walls on their own sheets)
    for n, kinds, door, board in ((9, "WDNC_NC_W", 1, (1, 7)), (6, "WDNC_W", 1, (1, 4))):
        place("stone", f"wh_roof{n}", warehouse_roof(n), comment="Warehouse tin roof (own art).")
        place("wood", f"wh_wall{n}", warehouse_wall(list(kinds), board), doors=[(door, 2)],
              comment="Warehouse board siding with cargo doors (own art).")
        place("stone", f"wh_wall{n}b", warehouse_wall_b(list(kinds)), doors=[(door, 2)],
              comment="Warehouse of corrugated metal with a sliding door (own art); the tin roof goes on top.")
    # the Battle Frontier's seven facilities (doors shut until the post-game: no door cells) and the downtown blocks
    for kind, fn in (("tower", fac_tower), ("dome", fac_dome), ("palace", fac_palace), ("arena", fac_arena),
                     ("factory", fac_factory), ("pike", fac_pike), ("pyramid", fac_pyramid)):
        place("stone", f"fac_{kind}", fn(), comment=f"Battle {kind.title()} (own art): the Frontier's shared hall, "
              "its own crown.")
    place("stone", "block_dept", block_dept(), doors=[(3, 4)],
          comment="Department Store (own art), 7x5, door (3,4): ashlar, cornice, DEPT STORE band, awning, glass doors.")
    place("stone", "block_hall", block_hall(), doors=[(4, 4)],
          comment="Conservation Center (own art), 9x5, door (4,4): teal roof, pediment with a trilobite, portico.")
    place("stone", "trough", trough(), comment="Drinking fountain: a stone post and basin (own art), 2x2.")
    place("leaf", "pot_sand", pot("flowers"), comment="Terracotta flower pot (own art).")
    place("leaf", "shrub_pot", pot("shrub"), comment="Potted box shrub (own art); shares the pot's tile.")
    place("wood", "flower_cart", flower_cart(), comment="Flower seller's cart (own art), 2x1.")
    place("wood", "barrel", barrel(), comment="Barrel (own art).")
    place("stone", "steamboat_ns", mirror(steamboat_ns()), comment="The riverboat moored north-south (own art), 3x7.")
    place("stone", "steamboat", steamboat(), comment="The riverboat: white sternwheeler (own art), 7x3, moored in water.")
    for k in ("l", "r"):
        place("stone", f"fbridge_{k}", footbridge(k), raw=True, passable=[(0, 0)], comment="White railed footbridge (own art).")
    for k in ("l", "m", "r"):
        place("wood", f"rwalk_{k}", railwalk(k), raw=True, passable=[(0, 0)], comment="Railed boardwalk (own art).")
    place("wood", "easel", easel(), comment="Painter's easel (own art).")
    place("stone", "generator", generator(), comment="Old generator cabinet (own art): Rotom's pier.")
    place("wood", "sign", sign(), comment="Wooden notice board (own art).")
    for k in ("vl", "vm", "vr", "ht", "hm", "hb"):
        place("wood", f"walk_{k}", walk(k), raw=True, passable=[(0, 0)], comment="Boardwalk planks (own art), walkable over water.")
    for n in (0, 1):
        for s in (0, 1):
            for e in (0, 1):
                for w in (0, 1):
                    if n + s + e + w:
                        name = "fence_" + "".join(k for k, on in zip("NSEW", (n, s, e, w)) if on)
                        place("stone", name, fence(n, s, e, w), comment="Wrought-iron fence piece (own art).")
    pieces, previews = {}, []
    for fam, sh in sheets.items():
        if not sh.used:
            continue
        rows = max(y for _, y in sh.used) + 1
        crop = sh.im.crop((0, 0, sh.cols * 16, rows * 16))
        out = Image.new("RGB", crop.size, KEY)
        out.paste(crop, (0, 0), crop)
        out.save(os.path.join(HERE, f"crescent_{fam}.png"))
        prev = Image.new("RGB", crop.size, (120, 160, 104))  # preview on swamp grass
        prev.paste(crop, (0, 0), crop)
        previews.append(prev)
        for name, p in sh.pieces.items():
            pieces[name] = dict(p, sheet=fam)
    with open(os.path.join(HERE, "crescent.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_comment": "written by make_crescent_art.py: piece -> sheet (crescent_<sheet>.png) and cell rectangle",
                   "pieces": pieces, "combos": {"stall": ["stall_top", "stall_base"],
                                                "warehouse9": ["wh_roof9", "wh_wall9"], "warehouse6": ["wh_roof6", "wh_wall6"],
                                                "warehouse9b": ["wh_roof9", "wh_wall9b"],
                                                "warehouse6b": ["wh_roof6", "wh_wall6b"]}},
                  f, indent=1)
        f.write("\n")
    full = Image.new("RGB", (256, sum(p.height + 4 for p in previews)), (40, 40, 40))
    y = 0
    for p in previews:
        full.paste(p, (0, y))
        y += p.height + 4
    full.resize((full.width * 3, full.height * 3), Image.NEAREST).save(os.path.join(HERE, "crescent_preview.png"))
    old = os.path.join(HERE, "crescent.png")
    if os.path.exists(old):
        os.remove(old)
    print("crescent sheets:", {f: sh.im.size for f, sh in sheets.items()}, len(pieces), "pieces")


if __name__ == "__main__":
    main()

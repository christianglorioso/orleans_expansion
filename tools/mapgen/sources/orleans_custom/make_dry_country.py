"""The shared dry-country set: Redfield (sugarcane and pepper country, gym 7) and Routes 15, 16, 17, 23 and 24.
Sun-bleached Louisiana sugar country in late summer, drawn here in Python (no source tiles).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_dry_country.py
writes
    sources/orleans_custom/dry_country.png    16 px cells: opaque terrain cells, then overlay pieces (magenta = clear)
    sources/orleans_custom/dry_country.json   the index (the format agreed in art_requests/dry_country.md, read by
                                              redfield_tileset.py): {"png", "terrain": {name: [x, y] or a list of
                                              [x, y]}, "pieces": {name: {x, y, w, h, doors, passable, empty,
                                              comment}}}
    maps/00_dry_country_art.png               the review sheet: every cell at 3x, test patches at 3x, tile counts

Terrain (all opaque; every texture repeats every 16 px, so pixel (x, y) of every cell is the same spot of the same
ground and pieces drawn from the same texture join without a seam):
    dry          sun-baked sandy earth; a list: plain first, then pebbles, a crack, a straw tuft (rare variations)
    dry_grass    sparse straw-coloured grass on the earth (plain ground)
    cane         sugarcane in north-south rows 8 px apart (tall grass: the encounter field); 8 px periodic across
    pepper       red-pepper bushes on tilled east-west ridges; 8 px periodic across
    salt, salt_dry   Route 24's white salt crust (cracked plates), and dry earth flecked with salt (between them)
    N S W E inNW inNE inSW inSE landSE landSW landNE landNW sTLBR sTRBL
                 dry ground on Ekat's swamp grass, a dual grid exactly like Ekat's marsh set (build.py corners():
                 a tile's four corners TL TR BL BR are the cells (x, y) (x+1, y) (x, y+1) (x+1, y+1); "N" = 0011 is
                 the patch's north edge, inNW = 0111, landSE = 0001, sTLBR = 0110 ...). The patch edge runs 10 px
                 from an in-corner (6 px from an out-corner), round on the outside (radius 10), tight on the inside
                 (radius 6), with the grass's dark turf line, the turf's shadow on the earth (north and west sides)
                 and wisps of straw where the grass gives out. Outside the edge every pixel is Ekat's grass, inside
                 it the dry ground's own texture: only the 8x8 tiles the edge crosses are new.
    road_C road_N road_S road_W road_E road_NW road_NE road_SW road_SE road_iNW road_iNE road_iSW road_iSE
                 packed-earth road on dry ground, cell based like the Johto dirt path (build.py path_tile: road_N =
                 the road's north edge ...): the Johto path's own colours, so it joins the other routes' paths; the
                 edge sits 4 px in and wanders one pixel on an 8 px period, so the road's 8x8 tiles repeat.
v2 (2026-10-12; every v1 cell keeps its [x, y]; dry_grass and salt redrawn in place), rows 10-17 of the sheet:
    dry_grass    now tall dry grass (encounter grass for Routes 23/24), its outer pixel ring exactly dry[0]'s
    salt         the crust re-seeded so it tiles with itself under check.py's measure
    cane_wall + cane_wall_<corner key>    the blocking cane-field backdrop on dry ground (stalk face on its S side)
    salt_<corner key>                      salt crust on dry ground (its C is "salt")
    red_earth (list: plain, pebbles, crack) + red_earth_<corner key>   red earth on dry ground
    gully + gully_<corner key>             an eroded gully cut into dry ground (wall face on its N side, lip on S)
    All four are dual grids with the dry-on-grass set's corner keys and geometry; outside the patch is the road's
    8 px dust (seamless against dry[0]); everything in them repeats every 8 px. maps/00_dry_country_v2.png reviews
    them (test patches, new tile count, check.py-style seam figures).
v3 (2026-10-12), rows 18-21:
    rock_wall + rock_wall_<corner key>     a blocking bedrock wall/cliff on dry ground: rough rock top, a 14 px Gen-3
                                           face on the S side (its outline extruded down: square lip, strata), side
                                           returns, a lit rim on the N side; its own squarish geometry (15 / 1 px)
    rock_wall is a list like dry: the plain fill (flat bedrock, soft tonal swells) at [0, 18], then crack, slab and
                                           weathered variations (row 23), features 1 px clear of the cell sides
    rock_wall_face, _face_l, _face_r (+ _il / _ir / _ilr step variants), row 22: the face's lower half, placed in
                                           the dry cells directly under the wall's south edge (face_cells() is the
                                           rule); the S edge (and landNW / landNE) now run their face to the cell's
                                           foot, so the face stands about two cells tall
    dry_grass (still [4, 0]) is now a continuous tall-grass fill; dry_grass_<corner key> its ragged straw border
    on dry ground. maps/00_dry_country_v3.png reviews them (with the mine and cave mouths set in the face).
Pieces (overlays, blocking):
    field_tree 2x3 (a pecan), field_tree_l 3x3 (a spreading live oak), rock 1x1, rock_l 2x2 (a boulder).
    The trees are mirror-symmetric (lit from above) so their right halves are flipped tiles.

Colour families (all GBA-exact, <= 15 each):
    GROUND  Ekat's grass (snapped) + the turf line, sand earth, straw, road     (terrain)
    CROP    cane greens and stalk gold, pepper reds, tilled soil              (cane, pepper)
    SALT    salt whites + the sand earth                                       (salt cells)
    TREE    leaf greens, bark, rock greys                                      (pieces)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
KEY = (255, 0, 255)


def gba(c):
    return tuple((int(v) >> 3) << 3 for v in c)


# ---------------------------------------------------------------- colours
# GROUND: Ekat's swamp grass (snapped as the tileset build snaps it), its turf line, earth, straw, road
G, GD, GL = (120, 160, 104), (104, 144, 96), (136, 176, 128)
G_RIM = (96, 128, 88)
DH, D1, D2, D3 = (240, 224, 184), (224, 200, 144), (200, 168, 112), (160, 128, 88)
ST_L, ST, ST_D = (240, 216, 120), (216, 184, 88), (176, 144, 64)
R_L, R1, R_D, R_DD = (176, 152, 120), (152, 128, 96), (128, 104, 80), (104, 80, 64)   # the Johto path's colours
# CROP
C0, C1, C2, C3, C4 = (40, 72, 40), (72, 112, 48), (112, 152, 56), (160, 192, 80), (208, 224, 128)
STK, STK_D = (200, 192, 104), (144, 144, 64)
PEP_L, PEP, PEP_D = (248, 120, 88), (216, 48, 32), (144, 24, 32)
SO_L, SO, SO_D = (176, 120, 80), (136, 88, 56), (96, 56, 40)
# SALT
SA_W, SA, SA_D, SA_C = (248, 248, 240), (232, 232, 216), (208, 200, 184), (176, 160, 136)
# TREE (+ rocks)
L0, L1, L2, L3, L4 = (24, 48, 32), (40, 80, 48), (64, 112, 56), (96, 144, 64), (152, 184, 88)
B0, B1, B2 = (64, 40, 32), (104, 72, 48), (144, 104, 64)
K0, K1, K2, K3 = (104, 96, 80), (152, 144, 120), (200, 192, 168), (240, 232, 216)


def _hash(x, y, k=0):
    """Repeatable noise in [0, 1)."""
    n = (x * 374761393 + y * 668265263 + k * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def blank(w=16, h=16, c=KEY):
    return [[c] * w for _ in range(h)]


# ================================================================ ground textures
def ekat_grass():
    im = Image.open(os.path.join(HERE, "..", "ekat_swamp", "swamp_tiles.png")).convert("RGB")
    return [[gba(im.getpixel((x, y))) for x in range(16)] for y in range(16)]


GRASS = ekat_grass()

# the earth's grit: (x, y, kind) on a 16 px period; kind d = a 2 px dash of shade with a lit grain above,
# s = a single dark grain, h = a single light grain
GRIT = [(2, 1, "d"), (9, 2, "s"), (13, 4, "d"), (6, 5, "h"), (0, 7, "s"), (10, 8, "d"), (4, 10, "d"),
        (14, 11, "h"), (12, 13, "s"), (7, 14, "d"), (1, 13, "h"), (15, 0, "h")]


def tuft(t, bx, by, blades, wrap=True):
    """A tuft of thin straw blades rising from (bx, by): blades = (dx, height, lean) with lean -1/0/1 (one pixel
    sideways every second pixel up). Front blades lit (ST_L tips), back blades dark; a shaded foot."""
    W, H = len(t[0]), len(t)
    for k, (dx, hgt, lean) in enumerate(blades):
        back = k % 2 == 1
        for j in range(hgt):
            x, y = bx + dx + lean * ((j + 1) // 2), by - j
            if wrap:
                x, y = x % W, y % H
            elif not (0 <= x < W and 0 <= y < H):
                continue
            c = ST_D if back else (ST_L if j == hgt - 1 else ST)
            if j == 0:
                c = ST_D
            t[y][x] = c
    for dx in range(min(b[0] for b in blades) - 1, max(b[0] for b in blades) + 2):
        x, y = bx + dx, by + 1
        if wrap:
            x, y = x % W, y % H
        if 0 <= x < W and 0 <= y < H and t[y][x] in (D1, DH):
            t[y][x] = D2


def dry_tex(variant=0):
    """Sun-baked sandy earth: flat sand with sparse grit; repeats every 16 px. Variations put one small feature
    in one quarter (or two) of the cell so they cost few tiles: 1 pebbles, 2 a crack, 3 a straw tuft."""
    t = blank(c=D1)
    for x, y, k in GRIT:
        if k == "d":
            t[y][x], t[y][(x + 1) % 16] = D2, D2
            t[(y - 1) % 16][x] = DH
        elif k == "s":
            t[y][x] = D2
        else:
            t[y][x] = DH
    if variant == 1:  # three pebbles in the top-left quarter
        for px, py, big in ((1, 2, True), (5, 4, False), (3, 5, False)):
            for x, y, c in (((px, py, DH), (px + 1, py, D1), (px, py + 1, D2), (px + 1, py + 1, D3))
                            if big else ((px, py, DH), (px + 1, py, D2), (px + 1, py + 1, D3))):
                t[y][x] = c
            if big:
                t[py + 1][px + 2] = D3
                t[py][px + 2] = D2
    elif variant == 2:  # a sun crack: a jagged main split and a short branch, in the bottom-right quarter
        pts = [(8, 9), (9, 10), (9, 11), (10, 12), (11, 12), (12, 13), (13, 13), (14, 14), (11, 13), (11, 14),
               (12, 10), (13, 10), (10, 11)]
        for x, y in pts:
            t[y][x] = D3
        for x, y in pts:
            if y + 1 < 16 and t[y + 1][x] in (D1, D2):
                t[y + 1][x] = DH   # the crack's lit lower lip
    elif variant == 3:  # a tuft of dry grass in the bottom-right quarter
        tuft(t, 11, 13, [(0, 6, 0), (-1, 4, 0), (1, 5, 1), (-2, 4, -1), (2, 3, 1), (-1, 6, -1), (3, 2, 1)],
             wrap=False)
    return t


def dry_grass_tex():
    """The dry-grass field (encounter grass of Routes 23 and 24), v3: tall straw grass edge to edge, joining itself
    both ways; a patch's border on dry ground is the dry_grass_* dual-grid set (dry_grass_field_tex, below)."""
    return dry_grass_field_tex()


def cane_tex():
    """Sugarcane rows (north-south, 8 px apart), seen from above: the jointed green-gold stalk pair of each row,
    long blades arching off the joints (lit at the joint, dark beneath) and reaching across the shaded gap
    between the rows. 8 px period across, 16 down."""
    t = blank(8, 16, C1)
    for y in range(16):
        t[y][7] = C0
        t[y][0] = C0 if y % 4 in (1, 2) else C1
    for y in range(16):      # the stalk pair: lit left, shaded right, a joint every 4 px
        j = y % 4 == 0
        t[y][3] = STK_D if j else STK
        t[y][4] = C0 if j else STK_D
    # blades (x, dir, y, length): long ones every 8 px each side, short ones between
    for x0, d, y0, n in ((2, -1, 0, 4), (5, 1, 4, 4), (2, -1, 8, 4), (5, 1, 12, 4),
                         (2, -1, 4, 2), (5, 1, 0, 2), (2, -1, 12, 2), (5, 1, 8, 2)):
        for k in range(n):
            x, y = (x0 + d * k) % 8, (y0 + k) % 16
            t[y][x] = (C4, C3, C2, C2)[k] if n > 2 else (C3, C2)[k]
            yy = (y + 1) % 16
            if t[yy][x] not in (C4, C3) and k < n - 1:
                t[yy][x] = C0
    return t


def pepper_tex():
    """Pepper rows: bushy plants hung with red peppers on a tilled east-west ridge, the furrow below; 8 px across,
    16 down."""
    t = blank(8, 16, SO)
    for x in range(8):
        t[0][x] = SO_L if x % 3 else SO
        for y in (12, 13):
            t[y][x] = SO_D
        t[14][x] = SO_D if x % 2 else SO
        t[15][x] = SO_L if (x + 1) % 4 else SO
        t[11][x] = SO
    # the bush: a rounded clump 8 wide, y 1..10, lit on top
    shape = ["..####..",
             ".######.",
             "########",
             "########",
             "########",
             "########",
             "########",
             ".######.",
             ".######.",
             "..####.."]
    for j, row in enumerate(shape):
        y = 1 + j
        for x, ch in enumerate(row):
            if ch == "#":
                c = C2
                if j <= 1 or (j == 2 and x in (1, 2, 5)):
                    c = C3
                if j >= 7:
                    c = C1
                if j == 9 or (j == 8 and x in (1, 6)) or x in (0, 7) and j >= 3:
                    c = C0
                t[y][x] = c
    t[2][2] = C4
    t[3][5] = C3
    t[6][3] = C1
    t[7][6] = C1
    # peppers: hanging pods (lit top, deep red, dark tip)
    for px, py in ((1, 4), (5, 5), (3, 7)):
        t[py][px], t[py + 1][px], t[py + 2][px] = PEP_L, PEP, PEP_D
    t[4][2] = PEP
    t[10][1] = C0
    t[10][6] = C0
    return t


def salt_tex():
    """Salt crust: white plates of uneven size split by a net of fine cracks (a periodic Voronoi net, so it
    repeats every 16 px), each plate's edge curled up: lit below/right of a crack, shaded above it."""
    seeds = [(0.3, 0.4), (9.9, 0.9), (8.1, 7.7), (0.2, 5.5), (4.7, 13.1)]   # no crack runs along a side
    t = blank(c=SA)
    crack = [[False] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            ds = sorted(math.hypot(min(abs(x + 0.5 - sx), 16 - abs(x + 0.5 - sx)),
                                   min(abs(y + 0.5 - sy), 16 - abs(y + 0.5 - sy))) for sx, sy in seeds)
            crack[y][x] = ds[1] - ds[0] < 0.75
    for y in range(16):
        for x in range(16):
            if crack[y][x]:
                t[y][x] = SA_D if _hash(x, y, 51) < 0.7 else SA_C
    for y in range(16):
        for x in range(16):
            if crack[y][x]:
                continue
            if crack[(y - 1) % 16][x] or crack[y][(x - 1) % 16]:
                t[y][x] = SA_W
    for x, y in ((4, 5), (12, 7), (8, 12), (1, 9)):
        if t[y][x] == SA:
            t[y][x] = SA_W
    return t


def salt_dry_tex():
    """Dry earth flecked with salt (between the dry ground and the crust)."""
    t = dry_tex()
    for x, y in ((3, 2), (4, 2), (3, 3), (11, 5), (12, 5), (6, 9), (14, 10), (13, 10), (2, 12), (9, 13), (10, 13),
                 (9, 14), (15, 15)):
        t[y][x] = SA_W
    for x, y in ((4, 3), (12, 6), (7, 9), (10, 14), (3, 13)):
        t[y][x] = SA_D
    return t


SALT = salt_tex()


def tile16(t8):
    """An 8 px wide texture (16 rows) repeated to a 16 px cell."""
    return [row + row for row in t8]


# ================================================================ the dual grid: dry ground on grass
T_IN, T_OUT = 10.0, 6.0   # the edge runs 10 px from an in-corner (6 px from an out-corner)
CORNER_KEYS = {  # build.py Builder.CORNER_KEYS: corners TL TR BL BR -> piece
    "1111": "C", "0011": "N", "1100": "S", "0101": "W", "1010": "E",
    "0111": "inNW", "1011": "inNE", "1101": "inSW", "1110": "inSE",
    "0001": "landSE", "0010": "landSW", "0100": "landNE", "1000": "landNW",
    "0110": "sTLBR", "1001": "sTRBL",
}
EDGE_ORDER = ["N", "S", "W", "E", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW", "landNE", "landNW", "sTLBR",
              "sTRBL"]
# the edge wanders a pixel in and out along its length (16 px period, flat at the cell joins)
JAG = [0, 0, 0.6, 0.6, 0, -0.6, -0.6, 0, 0, 0.6, 0, 0, -0.6, 0, 0.6, 0]


def inside(bits, x, y, tin=T_IN, tout=T_OUT, pn=2.0):
    """Is the point (x, y) of a tile (0..16) dry? bits: corners TL TR BL BR ('1' = dry). Every quarter of the
    tile is decided by its own corner c, its horizontal neighbour h, its vertical neighbour w and the diagonal d:
    straight edges T_OUT from the out side, convex corners a circle of T_IN round the lone dry corner, concave
    corners a circle of T_OUT round the lone grass corner, and the diagonal touch (sTLBR, sTRBL) two concave
    corners (as Ekat composes them)."""
    S = {(0, 0): bits[0] == "1", (1, 0): bits[1] == "1", (0, 1): bits[2] == "1", (1, 1): bits[3] == "1"}
    qx, qy = int(x >= 8), int(y >= 8)
    c, h, w, d = S[(qx, qy)], S[(1 - qx, qy)], S[(qx, 1 - qy)], S[(1 - qx, 1 - qy)]
    cx, cy, hx, wy = qx * 16, qy * 16, (1 - qx) * 16, (1 - qy) * 16
    if pn == 2.0:
        r = lambda px, py: math.hypot(x - px, y - py)
    else:   # a squarer corner (the rock wall)
        r = lambda px, py: (abs(x - px) ** pn + abs(y - py) ** pn) ** (1.0 / pn)
    if c:
        if not h and not w and not d:
            return r(cx, cy) <= tin
        return True
    if h and w:
        return r(cx, cy) > tout
    if h:
        return abs(x - cx) > tout if d else r(hx, cy) <= tin
    if w:
        return abs(y - cy) > tout if d else r(cx, wy) <= tin
    return r(hx, wy) <= tin


def sdf(bits, tin=T_IN, tout=T_OUT, pn=2.0):
    """Signed distance (px, + = dry) at the 16x16 pixel centres, and its gradient. Measured on a 4x sample of the
    tile padded by replication: the edge always crosses a tile side square to it, so the padding is exact."""
    ss, pad = 4, 4
    n = 16 * ss
    coords = (np.arange(n) + 0.5) / ss
    m = np.array([[inside(bits, x, y, tin, tout, pn) for x in coords] for y in coords])
    m = np.pad(m, pad * ss, mode="edge")
    ys, xs = np.nonzero(np.ones_like(m))
    pos = np.stack([(xs - pad * ss + 0.5) / ss, (ys - pad * ss + 0.5) / ss], 1)
    flat = m.reshape(-1)
    pin, pout = pos[flat], pos[~flat]
    out = np.zeros((16, 16))
    for y in range(16):
        for x in range(16):
            p = np.array([x + 0.5, y + 0.5])
            me = inside(bits, p[0], p[1], tin, tout, pn)
            other = pout if me else pin
            dist = np.sqrt(((other - p) ** 2).sum(1)).min() if len(other) else 99.0
            out[y, x] = dist if me else -dist
    gy, gx = np.gradient(out)
    return out, gx, gy


def dry_edge(bits, tex=None):
    tex = tex or dry_tex()
    s0, gx, gy = sdf(bits)
    out = blank()
    for y in range(16):
        for x in range(16):
            nx, ny = gx[y, x], gy[y, x]
            ln = math.hypot(nx, ny) or 1.0
            nx, ny = nx / ln, ny / ln            # points into the dry ground
            s = s0[y, x] + abs(ny) * JAG[x] + abs(nx) * JAG[y]
            shade_side = (0.55 * nx + 0.83 * ny) > 0.35   # grass to the north / north-west: its turf shades the earth
            if s >= 0:
                if s < 1.0 and shade_side:
                    c = D2
                elif s < 1.0:
                    c = tex[y][x] if tex[y][x] != D1 else (DH if _hash(x, y, 5) < 0.35 else D1)
                elif s < 1.8 and _hash(x, y, 6) < 0.22:
                    c = ST if _hash(x, y, 7) < 0.6 else ST_D      # wisps of straw where the grass gives out
                elif s < 1.8 and shade_side and _hash(x, y, 8) < 0.5:
                    c = D2
                else:
                    c = tex[y][x]
            else:
                if s > -1.0:
                    c = G_RIM
                elif s > -1.8 and not shade_side and _hash(x, y, 9) < 0.3:
                    c = GD
                else:
                    c = GRASS[y][x]
            out[y][x] = c
    return out


# ================================================================ v2: more dual-grid sets on dry ground
# cane_wall (the blocking cane-field backdrop), salt (crust on dry), red_earth (red earth on dry) and gully (an eroded
# gully cut into dry ground): each a dual grid like the dry-on-grass set (same corner keys, same 10 px / 6 px edge
# geometry), the patch inside, dry[0] outside. A face (the cane's stalks, the gully's north wall) is a band along the
# edges whose normal points the right way, its width scaled by that normal: it shrinks to nothing where the edge
# crosses a tile side square to it, so a tile never needs to know its neighbour and always joins it.
# Economy: everything in these pieces repeats every 8 px both ways (the ground outside is the road's 8 px dust, which
# sits against dry[0] without a seam), so a straight edge's two halves are one tile and the fills cost one tile each.
RE_L, RE, RE_D, RE_DD = (224, 176, 136), (200, 144, 104), (168, 112, 80), (136, 88, 64)   # red earth
GF, GF_D = (184, 152, 104), (152, 120, 80)                                               # gully floor
GW, GW_D = (176, 136, 88), (120, 88, 56)                                                 # gully wall strata
_SDF = {}


def dual_tile(bits, paint, tin=T_IN, tout=T_OUT, pn=2.0):
    """One dual-grid tile: paint(x, y, s, nx, ny) with s the signed distance (+ = inside the patch) and (nx, ny)
    the edge's outward normal (towards the ground outside)."""
    if (bits, tin, tout, pn) not in _SDF:
        _SDF[(bits, tin, tout, pn)] = sdf(bits, tin, tout, pn)
    s0, gx, gy = _SDF[(bits, tin, tout, pn)]
    below = None
    if getattr(paint, "wants_below", False):   # px straight down to the ground outside (99: not in this tile)
        m = [[inside(bits, x + 0.5, y + 0.5, tin, tout, pn) for x in range(16)] for y in range(16)]
        below = [[next((k for k in range(1, 16 - y) if not m[y + k][x]), 99) for x in range(16)] for y in range(16)]
    out = blank()
    for y in range(16):
        for x in range(16):
            ln = math.hypot(gx[y, x], gy[y, x])
            nx, ny = (-gx[y, x] / ln, -gy[y, x] / ln) if ln > 1e-6 else (0.0, 0.0)
            if below is None:
                out[y][x] = paint(x, y, float(s0[y, x]), nx, ny)
            else:
                out[y][x] = paint(x, y, float(s0[y, x]), nx, ny, below[y][x])
    return out


def edge_set(paint, tin=T_IN, tout=T_OUT, pn=2.0):
    return {key: dual_tile(bits, paint, tin, tout, pn) for bits, key in CORNER_KEYS.items() if key != "C"}


JAG8 = [0, 0.6, 0.6, 0, -0.6, 0, 0, 0]


def jagged(x, y, s, nx, ny):
    return s + abs(ny) * JAG8[x % 8] + abs(nx) * JAG8[y % 8]


def tile8(t8):
    """An 8x8 texture repeated to a 16 px cell."""
    return [row + row for row in t8] * 2


EXT = None   # the ground outside the patch: dust_tex() (set after the road's textures are defined)
SHADE = {D1: D2, DH: D2, D2: D3, D3: D3}      # dry ground in a shadow


# ---- cane_wall: a solid stand of tall cane, too thick to walk into
def cane_wall_tex():
    """The stand's top: a dark, tangled mass of long cane blades (no rows, no stalks showing: unlike the walk-in
    cane), lit blades crossing every which way, a few pale tassels (the cane's flowering arrows); 16 px period."""
    t = blank(8, 8, C1)
    for y in range(8):
        for x in range(8):
            if _hash(x, y, 61) < 0.3:
                t[y][x] = C0
    for x, y, d in ((1, 0, 1), (5, 2, -1), (2, 4, 1), (6, 6, -1)):
        path = [(x, y, C3), (x + d, y, C2), (x + 2 * d, y + 1, C2), (x + 3 * d, y + 2, C2), (x + 3 * d, y + 3, C1)]
        for px, py, c in path:
            t[py % 8][px % 8] = c
        for px, py, c in path[1:4]:
            if t[(py + 1) % 8][px % 8] in (C1,):
                t[(py + 1) % 8][px % 8] = C0
    t[3][6], t[4][6] = C4, STK        # a tassel
    t = t[4:] + t[:4]                 # rolled so the texture's wrap rows are no busier than its inside (check.py)
    return tile8(t)


CANE_WALL = cane_wall_tex()
STALKS = [C0, STK, STK_D, C0, STK, STK_D, STK, C0]   # the face's stalks across (8 px period; dark at the cell sides)
CW_FACE, CW_SHADOW = 9.0, 3.0


def paint_cane_wall(x, y, s, nx, ny):
    down = max(0.0, ny)
    if s >= 0:
        if down > 0.05 and s < CW_FACE * down:          # the front face: stalks standing on their row of soil
            t = s / (CW_FACE * down)
            depth = s / down
            if t < 0.12:
                return SO_D
            if t > 0.78:                                 # the canopy's hanging fringe
                return C2 if _hash(x % 8, int(depth), 63) < 0.3 else C0 if _hash(x % 8, int(depth), 64) < 0.5 else C1
            c = STALKS[x % 8]
            if int(depth) % 4 == 2 and c != C0:          # a joint
                c = STK_D if c == STK else C0
            return c
        if s < 1.0:
            return C0
        if s < 2.2 and ny < -0.3 and _hash(x % 8, y % 8, 65) < 0.45:   # lit blade tips along the top
            return C3
        return CANE_WALL[y][x]
    sh = CW_SHADOW * max(0.0, 0.35 * nx + 0.94 * ny)    # its shadow falls down and a little right
    if -s < sh:
        return D3 if -s < 1.0 else SHADE[EXT[y][x]]
    return EXT[y][x]


# ---- salt crust on dry ground
def paint_salt(x, y, s, nx, ny):
    s2 = jagged(x, y, s, nx, ny)
    if s2 >= 0:
        if s2 < 1.0:                                      # the crust's raised edge
            return SA_C if ny > 0.35 else SA_W if ny < -0.35 else SA_D
        if s2 < 2.0 and ny > 0.35:
            return SA_D
        return SALT[y][x]
    if s2 > -1.0 and ny > 0.35:
        return D2                                         # the crust's lip shades the earth
    if s2 > -3.0 and _hash(x % 8, y % 8, 71) < 0.32 * (1 + s2 / 3.0):
        return SA_W if _hash(x % 8, y % 8, 72) < 0.6 else SA     # flakes broken off the crust
    return EXT[y][x]


# ---- red earth
def red_tex(variant=0):
    """Sun-baked red earth (muted ochre-red): flat with grit like the dry ground; 16 px period. Variations: 1 a
    scatter of pebbles (top-left quarter), 2 a sun crack (bottom-right quarter). The plain cell repeats every
    8 px like the edge pieces' red."""
    t8 = blank(8, 8, RE)
    for x, y, c in ((1, 1, RE_D), (2, 1, RE_D), (1, 0, RE_L), (5, 4, RE_D), (6, 2, RE_L), (3, 6, RE_D),
                    (4, 6, RE_D), (3, 5, RE_L), (0, 4, RE_L)):
        t8[y][x] = c
    t = tile8(t8)
    if variant == 1:
        for px, py in ((2, 2), (5, 4), (2, 6)):
            t[py][px], t[py][px + 1], t[py + 1][px], t[py + 1][px + 1] = RE_L, RE, RE_D, RE_DD
    elif variant == 2:
        for x, y in ((8, 9), (9, 10), (10, 10), (11, 11), (11, 12), (12, 13), (13, 13), (10, 12), (9, 13),
                     (14, 14), (12, 10)):
            t[y][x] = RE_DD
            if y + 1 < 16 and t[y + 1][x] == RE:
                t[y + 1][x] = RE_L
    return t


RED = red_tex(0)


def paint_red(x, y, s, nx, ny):
    s2 = jagged(x, y, s, nx, ny)
    if abs(s2) < 1.5:                                     # the soils mingle in a dithered band
        if _hash(x % 8, y % 8, 81) < 0.5 + s2 / 3.0:
            return RE_D if (s2 < 0.5 and _hash(x % 8, y % 8, 82) < 0.3) else RED[y][x]
        return EXT[y][x]
    return RED[y][x] if s2 > 0 else EXT[y][x]


# ---- the gully
def gully_tex():
    """The gully's floor: packed, shaded silt with washed pebbles and a faint wash line; 16 px period."""
    t = blank(8, 8, GF)
    for x, y, c in ((1, 1, GF_D), (2, 1, GF_D), (5, 3, D2), (6, 3, GF), (6, 4, GF_D), (3, 6, GF_D), (0, 5, D2),
                    (6, 7, GF_D)):
        t[y][x] = c
    return tile8(t)


GULLY = gully_tex()
G_FACE, G_SIDE = 8.0, 3.0
STRATA = [GW, D2, GW, GW, D3, GW, D3, GW_D, GW_D]
RUNNEL = [0, 0, 1, 0, 0, 0, 1, 0]   # erosion runnels down the wall (8 px period)


def paint_gully(x, y, s, nx, ny):
    up = max(0.0, -ny)                                    # ground to the north: its wall faces us
    if s >= 0:
        if up > 0.05 and s < G_FACE * up:
            t = s / (G_FACE * up)
            if t < 0.14:
                return DH                                 # the lit lip
            depth = s / up
            if t > 0.86:
                return GW_D                               # the dark foot of the wall
            c = STRATA[min(int(depth), len(STRATA) - 1)]
            if RUNNEL[x % 8] and c in (GW, D2):
                c = D3
            return c
        side = abs(nx)
        if side > 0.3 and s < G_SIDE * side:              # the side walls: west wall in shade, east wall lit
            return (D3 if s < 1.5 else GW) if nx < 0 else (D2 if s < 1.5 else GW)
        if ny > 0.3 and s < 1.0:
            return GF_D                                   # the floor darkens under the south rim
        return GULLY[y][x]
    if ny > 0.3 and s > -1.0:
        return GW_D                                       # the south rim's broken edge
    if ny > 0.3 and s > -2.0:
        return DH                                         # the rim's sunlit lip
    if abs(nx) > 0.5 and s > -1.0:
        return D2
    return EXT[y][x]


# ================================================================ v3: the rock wall and the dry-grass field
# rock_wall: a blocking bedrock wall (Route 24's salt-dome face, Route 23's bluff), a dual grid on dry ground with its
# own, fatter geometry (the edge 15 px from an in-corner, 1 px from an out-corner, squarish corners) so the south
# face can stand 14 px tall inside the edge tile (the plateau outline extruded straight down); the plateau top is rough rock. dry_grass_*: the dry-grass field's ragged straw border
# on dry ground (the field itself is the dry_grass cell, now a continuous tall-grass fill).
RW_K, RW0, RW1, RW2, RW3, RW4 = (40, 40, 40), (64, 64, 64), (96, 92, 96), (128, 124, 128), (160, 156, 152), \
    (200, 196, 184)    # bedrock: darker than the boulders, a neutral grey between their warm stone and Cianwood's
RW_LV = [RW0, RW1, RW2, RW3, RW4]
RW_IN, RW_OUT = 15.0, 1.0     # (they add up to 16: a straight edge sits RW_OUT from the out side)
RW_FACE = RW_IN - 1.0        # the face's height: its lit top lip sits 1 px below the tile above


# the plateau top, in the Gen-3 way: mostly plain bedrock with a few long open cracks (never a closed joint net) that
# wander across the cell sides into the next cell, each a step down to the south-east (its upper lip lit, its foot
# shaded); a shadowed slab under a crack, a lit slab, a few pebbles
CRAG_CRACKS = []                              # the plain fill is flat bedrock: its texture is the variations
CRAG_SHADE = []
CRAG_LIT = []
# the variations (rock_wall list entries 1-3): features only inside the cell (1 px clear of every side), so each
# variation's border is the plain fill's own and it seams with the plain fill, the other variations and every edge
CRAG_VARIANTS = [
    ("rock_wall_crack", {"cracks": [[(2, 6), (5, 5), (8, 7), (11, 6), (13, 8)], [(8, 7), (9, 11), (8, 13)]],
                         "shade": [[(2, 7), (8, 8), (12, 8), (10, 10), (4, 9)]], "lit": [], "pebbles": [(4, 12)],
                         "weather": None}),
    ("rock_wall_slab", {"cracks": [[(9, 10), (11, 12), (13, 12)]],
                        "shade": [], "lit": [[(1.5, 5), (4, 3), (6, 4), (9, 1.5), (14, 3), (12.5, 6), (14.5, 9),
                                              (10, 11), (7, 9.5), (3, 10.5)]],
                        "pebbles": [(4, 11), (6, 12), (12, 12)], "weather": None}),
    ("rock_wall_weathered", {"cracks": [[(12, 3), (11, 6), (12, 9), (11, 12)]], "shade": [], "lit": [],
                             "pebbles": [(5, 11)], "weather": (7.0, 7.5, 5.5, 5.0), "pits": True}),
]


def _in_poly(px, py, poly):
    c = False
    for k in range(len(poly)):
        (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % len(poly)]
        if (y0 > py) != (y1 > py) and px < x0 + (py - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def _in_tri(p, a, b, c):
    sd = lambda p1, p2, p3: (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = sd(p, a, b), sd(p, b, c), sd(p, c, a)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


def strip_seam(t):
    """check.py's measure across a periodic texture's own wrap, on whole and partial strips (an edge tile shows
    only part of the texture), both ways: the worst of them."""
    a_ = np.array(t).astype(int)
    d = lambda p, q: np.abs(p - q).sum(-1)
    vals = []
    for tt in (a_, a_.transpose(1, 0, 2)):
        n = tt.shape[0]
        for sl in (slice(0, n), slice(0, n // 2), slice(n // 2, n), slice(2, n - 2)):
            vals.append(d(tt[sl, -1], tt[sl, 0]).mean() - (d(tt[sl, -2], tt[sl, -1]).mean()
                                                             + d(tt[sl, 0], tt[sl, 1]).mean()) / 2)
    return max(vals)


def roll16(t, dx, dy):
    r = [row[len(row) - dx:] + row[:len(row) - dx] if dx else list(row) for row in t]
    return r[len(r) - dy:] + r[:len(r) - dy] if dy else r


def _crag_cracks(t, lines, clip=None):
    crack = set()
    for line in lines:
        for (x0, y0), (x1, y1) in zip(line, line[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for i in range(n + 1):
                u = i / n
                crack.add((int(math.floor(x0 + (x1 - x0) * u + 0.5)) % 16,
                           int(math.floor(y0 + (y1 - y0) * u + 0.5)) % 16))
    ok = (lambda x, y: True) if clip is None else clip
    for x, y in crack:
        for dx, dy, c in ((-1, -1, RW3), (0, -1, RW3), (1, 1, RW1), (0, 1, RW1)):
            xx, yy = (x + dx) % 16, (y + dy) % 16
            if (xx, yy) not in crack and ok(xx, yy):
                t[yy][xx] = c
    for x, y in crack:
        if ok(x, y):
            t[y][x] = RW0


def rock_top_tex():
    """The plateau top's plain fill: quiet bedrock (mostly flat RW2), two short cracks in different directions, a
    shaded slab, a little mottling, two pebbles; rolled so nothing runs along a cell side. The rock_wall list's
    variations (CRAG_VARIANTS) add the busier features."""
    t = [[RW2] * 16 for _ in range(16)]
    tw = 2 * math.pi / 16
    for y in range(16):
        for x in range(16):
            # broad, soft tonal swells (periodic, crossing the cell sides): the rock's lie, not a pattern of marks
            f = (0.6 * math.sin(tw * (x + 2 * y) + 0.8) + 0.5 * math.sin(tw * (2 * x - y) + 2.1)
                 + 0.3 * math.sin(tw * (3 * x + y) + 4.0))
            if f > 1.05 or (f > 0.85 and _hash(x, y, 127) < 0.5):
                t[y][x] = RW3
            elif f < -1.05 or (f < -0.85 and _hash(x, y, 128) < 0.5):
                t[y][x] = RW1
            if any(_in_poly(x + 0.5, y + 0.5, p) for p in CRAG_SHADE):
                t[y][x] = RW1
            elif _hash(x, y, 121) < 0.02:
                t[y][x] = RW1
            elif _hash(x, y, 123) < 0.012:
                t[y][x] = RW3
    _crag_cracks(t, CRAG_CRACKS)
    t[12][11], t[13][11] = RW3, RW1                   # a pebble
    best = min((strip_seam(roll16(t, dx, dy)), dx, dy) for dy in range(16) for dx in range(16))
    return roll16(t, best[1], best[2])


def rock_top_variant(spec):
    """A variation of the plain fill: its features drawn only 1 px or more inside the cell (its outer ring is the
    plain fill's own, so it seams like the plain fill)."""
    t = [list(r) for r in ROCK_TOP]
    inner = lambda x, y: 1 <= x <= 14 and 1 <= y <= 14
    for y in range(16):
        for x in range(16):
            if not inner(x, y):
                continue
            if any(_in_poly(x + 0.5, y + 0.5, p) for p in spec["shade"]):
                t[y][x] = RW1
                if spec.get("pits") and _hash(x, y, 125) < 0.12:
                    t[y][x] = RW0 if _hash(x, y, 126) < 0.6 else RW2     # weathered pits
            if any(_in_poly(x + 0.5, y + 0.5, p) for p in spec["lit"]):
                t[y][x] = RW3
            if spec["weather"]:
                cx, cy, rx, ry = spec["weather"]
                q = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if q < 1.0 and (q < 0.45 or (x + y) % 2):
                    t[y][x] = RW4 if _hash(x, y, 124) < 0.15 else RW3
                    if spec.get("pits") and _hash(x, y, 125) < 0.1:
                        t[y][x] = RW1                     # weathered pits
    for poly in spec["lit"]:                               # a slab's shaded lower and right edges
        n = len(poly)
        for k in range(n):
            (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % n]
            if (x1 - x0) * 0.78 - (y1 - y0) * 0.62 > 0:    # an edge on the slab's lit side: skip
                continue
            m = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for i in range(m + 1):
                u = i / m
                x, y = int(x0 + (x1 - x0) * u), int(y0 + (y1 - y0) * u)
                if inner(x, y):
                    t[y][x] = RW1
    for poly in spec["lit"]:                               # and its lit upper-left edges
        n = len(poly)
        for k in range(n):
            (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % n]
            if (x1 - x0) * 0.78 - (y1 - y0) * 0.62 <= 0:
                continue
            m = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for i in range(m + 1):
                u = i / m
                x, y = int(x0 + (x1 - x0) * u + 0.5), int(y0 + (y1 - y0) * u + 0.5)
                if inner(x, y) and t[y][x] == RW3:
                    t[y][x] = RW4
    _crag_cracks(t, spec["cracks"], clip=inner)
    for x, y in spec["pebbles"]:
        if inner(x, y) and inner(x, y + 1):
            t[y][x], t[y + 1][x] = RW4, RW0
            if inner(x + 1, y + 1):
                t[y + 1][x + 1] = RW1
    return t


ROCK_TOP = rock_top_tex()
ROCK_TOP_VARIANTS = [(name, rock_top_variant(spec)) for name, spec in CRAG_VARIANTS]


def rock_face_tex():
    """The cliff face below the lip, 24 rows by 16 px (repeats along the face; rows 0-12 in the S edge cell, 13-22
    in the face-extension cell below it): angular blocks of bedrock (a
    Voronoi net stretched across, periodic along the face), each lit on its top-left and shaded on its
    bottom-right, dark joints between them, the whole face in shade and darkest at its foot; tall, narrow facets (a sheer face, not the plateau's lumps)."""
    seeds = [(1.0, 2.0), (4.5, 5.0), (7.5, 1.5), (10.5, 6.5), (13.5, 2.5), (2.5, 10.0), (8.0, 9.5), (14.0, 10.5)]
    seeds = seeds + [(sx + 3.0, sy + 12.0) for sx, sy in seeds]
    t = [[RW1] * 16 for _ in range(24)]
    torx = lambda a, b: min(abs(a - b), 16 - abs(a - b))
    for y in range(24):
        for x in range(16):
            px, py = x + 0.5, y + 0.5
            ds = sorted((math.hypot(torx(px, sx), (py - sy) * 0.5), i) for i, (sx, sy) in enumerate(seeds))   # tall facets
            (d1, i1), (d2, _) = ds[0], ds[1]
            if d2 - d1 < 0.8:
                t[y][x] = RW_K if y > 1 else RW0
                continue
            sx, sy = seeds[i1]
            dx = ((px - sx + 8) % 16) - 8
            v = -dx / 2.2 + 0.25 * (_hash(x, y, 104) - 0.5)          # each facet lit on its left
            base = 2.4 - (y * 2.0) / 22        # the face is in shade, darkest at its foot
            lv = int(round(base + (0.8 if v > 0.4 else 0 if v > -0.4 else -0.9)))
            t[y][x] = RW_LV[max(0, min(3, lv))]
    return t


ROCK_FACE = roll16(rock_face_tex(), min((strip_seam([r[16 - dx:] + r[:16 - dx] if dx else r
                                                      for r in rock_face_tex()][:13]), dx) for dx in range(16))[1], 0)
# (rolled along the face so no joint runs down a cell side)


def paint_rock_wall(x, y, s, nx, ny, vb=99):
    """The south face is the plateau's outline extruded straight down (vb: px down to the ground), so it stands
    as a sheer Gen-3 face with a square top lip and keeps its height round the corners; the side returns win
    where the edge runs north-south (which also covers the two columns where a corner's face would need the
    tile above)."""
    if s >= 0:
        side = abs(nx)
        if side > 0.45 and s < 4.0 * side:                # the side returns: east in shade, west catching light
            if s < 1.0:
                return RW_K if nx > 0 else RW1
            return (RW0 if s < 2.0 else RW1) if nx > 0 else RW3
        if vb <= RW_FACE:                                 # the south face
            if vb == RW_FACE:
                return RW4                                # the lit top lip
            if vb == RW_FACE - 1:
                return RW_K                               # the lip's shadow line
            if vb == 1:
                return RW_K                               # the foot
            return ROCK_FACE[int(RW_FACE - vb - 2)][x]
        if s < 1.0:
            return RW0                                    # the rim's edge
        if s < 2.0 and ny < -0.3:
            return RW4 if _hash(x % 8, y % 8, 103) < 0.6 else RW3   # the rim catching the light
        return ROCK_TOP[y][x]
    if nx > 0.5 and -s < 1.0:
        return D2                                         # (the face's dark foot row is its shadow line)
    return EXT[y][x]


paint_rock_wall.wants_below = True

# The face extension: the S edge (and the two outer corners, landNW / landNE) carry the lip and the upper face down
# to the bottom of their cell, and the cell below takes the lower face, its dark foot and a little scree.
FACE_CONT = {"1100": "rock_wall_face", "1000": "rock_wall_face_r", "0100": "rock_wall_face_l"}


def rock_wall_edges():
    """The rock wall's 14 edge tiles; in the three FACE_CONT tiles every face column runs on to the cell's foot
    (no foot drawn there). Also returns, for each of them, each column's face row at the bottom (None: no face)
    and the bottom row's pixels, for the extension cells."""
    tiles = edge_set(paint_rock_wall, RW_IN, RW_OUT, 4.0)
    bottoms = {}
    for bits, key in CORNER_KEYS.items():
        if bits not in FACE_CONT:
            continue
        t = tiles[key]
        s0, gx, gy = _SDF[(bits, RW_IN, RW_OUT, 4.0)]
        m = [[inside(bits, x + 0.5, y + 0.5, RW_IN, RW_OUT, 4.0) for x in range(16)] for y in range(16)]
        ft = [None] * 16
        for x in range(16):
            yi = max((y for y in range(16) if m[y][x]), default=None)
            if yi is None or yi == 15:
                continue
            ln = math.hypot(gx[yi, x], gy[yi, x]) or 1.0
            nxv = -gx[yi, x] / ln
            if abs(nxv) > 0.45 and s0[yi, x] < 4.0 * abs(nxv):
                continue                                   # a side return, not the face
            f0 = int(RW_FACE - 1 - 2)                      # the face row just above the ground (vb 1)
            for y in range(yi, 16):
                t[y][x] = ROCK_FACE[f0 + y - yi][x]
            ft[x] = f0 + 15 - yi
        bottoms[FACE_CONT[bits]] = (ft, list(t[15]))
    return tiles, bottoms


def face_extension(ft, top, il=False, ir=False):
    """A face-extension cell: the lower face under each face column (ft: the face row reached at the bottom of
    the cell above, None: no face), its dark foot on row 10, a shadow and scree below, dust beyond. il / ir (an
    inner corner: the next cell on that side is another wall's edge tile, a step of the wall) end the face 1 px
    short on that side, so it meets that tile's own ground pixel, not its edge; a face's end column is a dark corner on the right, a lit
    one on the left."""
    out = blank()
    face = [[False] * 16 for _ in range(16)]
    for j in range(10):
        for x in range(16):
            if ft[x] is None:
                continue
            if ir and x > 14 and j >= 1:
                continue                                   # a step on the east: stop 1 px short of its edge tile
            if il and x < 1 and j >= 1:
                continue
            face[j][x] = True
    for y in range(16):
        for x in range(16):
            out[y][x] = EXT[y][x] if y else (top[x] if ft[x] is None else EXT[y][x])
    cols = [x for x in range(16) if ft[x] is not None]
    for j in range(10):
        for x in range(16):
            if face[j][x]:
                c = ROCK_FACE[min(23, ft[x] + 1 + j)][x]
                if x + 1 < 16 and not face[j][x + 1]:
                    c = RW_K                               # the face's corner, in shade
                elif x > 0 and not face[j][x - 1]:
                    c = RW3                                # the face's corner, catching the light
                out[j][x] = c
    for x in range(16):
        if face[9][x]:
            out[10][x] = RW_K                              # the foot
            out[11][x] = D3                                # its shadow on the ground
            out[12][x] = D2 if (x + 12) % 2 else out[12][x]
    # the shadow the face casts to its east, and the scree at its foot
    for j in range(1, 12):
        for x in range(16):
            if face[min(j, 9)][x] and x + 1 < 16 and not face[min(j, 9)][x + 1] and ft[x] is not None:
                for k, c in ((1, D3), (2, D2)):
                    if x + k < 16 and not face[min(j, 9)][x + k] and j >= k:
                        out[j][x + k] = c if (c == D3 or (x + k + j) % 2) else out[j][x + k]
    lo, hi = (min(cols), max(cols)) if cols else (0, -1)
    for x, y, big in ((lo + 2, 11, True), (lo + 6, 12, False), (lo + 9, 11, False), (hi - 3, 12, True),
                      (hi - 7, 13, False), (hi + 2, 10, False), (lo - 2, 11, False)):
        if 0 <= x < 15 and 9 <= y < 14 and not face[min(y, 9)][x]:
            out[y][x] = RW2
            out[y + 1][x] = RW0
            if big:
                out[y][x + 1] = RW1
                out[y + 1][x + 1] = RW_K
    return out


def rock_wall_extensions(bottoms):
    f, l_, r_ = bottoms["rock_wall_face"], bottoms["rock_wall_face_l"], bottoms["rock_wall_face_r"]
    return {"rock_wall_face": face_extension(*f), "rock_wall_face_l": face_extension(*l_),
            "rock_wall_face_r": face_extension(*r_),
            "rock_wall_face_il": face_extension(*f, il=True), "rock_wall_face_ir": face_extension(*f, ir=True),
            "rock_wall_face_ilr": face_extension(*f, il=True, ir=True),
            "rock_wall_face_l_ir": face_extension(*l_, ir=True), "rock_wall_face_r_il": face_extension(*r_, il=True)}


FACE_KEYS = ["rock_wall_face", "rock_wall_face_l", "rock_wall_face_r", "rock_wall_face_il", "rock_wall_face_ir",
             "rock_wall_face_ilr", "rock_wall_face_l_ir", "rock_wall_face_r_il"]


def face_cells(at, w, h, wall="R"):
    """Which cells take a face extension (the layout's rule): a non-wall cell c = (x, y) whose own east, south
    and south-east cells are not wall (so its own dual-grid tile is plain ground), with the wall to its north
    (N = (x, y-1)) or north-east (NE = (x+1, y-1)):
        N and NE: rock_wall_face; N only: rock_wall_face_r; NE only: rock_wall_face_l;
        then add _il if (x-1, y) or (x-1, y+1) is wall (a step of the wall on the west, for _face and _face_r)
        and _ir if (x+2, y) or (x+2, y+1) is wall (a step on the east, for _face and _face_l)."""
    out = {}
    W = lambda x, y: at(x, y) in wall
    for y in range(h):
        for x in range(w):
            if W(x, y) or W(x + 1, y) or W(x, y + 1) or W(x + 1, y + 1):
                continue
            n, ne = W(x, y - 1) and y > 0, W(x + 1, y - 1) and y > 0
            il = W(x - 1, y) or W(x - 1, y + 1)
            ir = W(x + 2, y) or W(x + 2, y + 1)
            if n and ne:
                key = "rock_wall_face" + ("_ilr" if il and ir else "_il" if il else "_ir" if ir else "")
            elif n:
                key = "rock_wall_face_r" + ("_il" if il else "")
            elif ne:
                key = "rock_wall_face_l" + ("_ir" if ir else "")
            else:
                continue
            out[(x, y)] = key
    return out


def dry_grass_field_tex():
    """Tall dry grass, edge to edge (Gen-3 tall grass in straw): staggered fans of pointed blades, lit tips, a
    dark heart under each fan; 8 px period both ways."""
    t = blank(8, 8, ST_D)
    for cx, by in ((2, 3), (6, 7)):
        for dx, dy, c in ((0, -3, ST_L), (-1, -2, ST_L), (1, -2, ST), (-2, -1, ST), (-1, -1, ST), (0, -2, ST),
                          (0, -1, ST_D), (1, -1, ST), (2, -1, ST_D), (-2, 0, ST_D), (-1, 0, D3), (0, 0, D3),
                          (1, 0, D3), (2, 0, ST_D)):
            t[(by + dy) % 8][(cx + dx) % 8] = c
    t = [row[-3:] + row[:-3] for row in t]
    t = t[-2:] + t[:-2]                    # rolled so the fans don't line up along a cell side (check.py)
    return tile8(t)


DRY_GRASS_FILL = dry_grass_field_tex()   # the dry_grass cell
DG_TIP = [0, 2, 1, 0, 3, 1, 0, 2]                     # blade tips standing above the field's north edge (8 px period)


def paint_dry_grass(x, y, s, nx, ny):
    s2 = jagged(x, y, s, nx, ny)
    if s2 >= 0:
        if ny > 0.3 and s2 < 1.2:
            return D3                                     # the grass's shaded foot along its south side
        return DRY_GRASS_FILL[y][x]
    if ny < -0.3 and -s2 < DG_TIP[x % 8]:
        return ST_L if -s2 > DG_TIP[x % 8] - 1 else ST    # tips poking above the north edge
    if abs(nx) > 0.5 and -s2 < 1.0 and _hash(x % 8, y % 8, 91) < 0.5:
        return ST_D                                       # stray blades at the sides
    if ny > 0.3 and -s2 < 1.0:
        return D2
    return EXT[y][x]


# ================================================================ the road (cell based, on dry ground)
R_INSET, R_ROUND = 4, 4
RJAG = [0, 1, 0, 0, -1, 0, 1, 0]   # 8 px period: the road's edge tiles repeat


def road_tex():
    """Packed earth (the Johto path's colours), 8 px period."""
    t = blank(8, 8, R1)
    for x, y in ((1, 2), (2, 2), (5, 5)):
        t[y][x] = R_D
    for x, y in ((1, 1), (5, 4)):
        t[y][x] = R_L
    t[6][1] = R_D
    return [row + row for row in t] * 2


def dust_tex():
    """The dry verge beside the road: sand with a little kicked-up grit; 8 px period."""
    t = blank(8, 8, D1)
    for x, y, c in ((2, 1, D2), (6, 2, DH), (5, 5, D2), (0, 6, DH), (3, 4, DH)):
        t[y][x] = c
    return [row + row for row in t] * 2


EXT = dust_tex()


def road_piece(n, s, w, e, notch=None):
    """One road cell: n/s/w/e = which sides are open (dry ground beyond); notch ('NW', ...) cuts an inner corner.
    The road lies R_INSET px in from an open side; its rim is a worn darker lip (R_D), the verge outside is dust."""
    road, dust = road_tex(), dust_tex()
    out = blank()
    for y in range(16):
        for x in range(16):
            cand = [99.0]
            if n:
                cand.append(y - (R_INSET + RJAG[x % 8]))
            if s:
                cand.append((15 - y) - (R_INSET + RJAG[x % 8]))
            if w:
                cand.append(x - (R_INSET + RJAG[y % 8]))
            if e:
                cand.append((15 - x) - (R_INSET + RJAG[y % 8]))
            dd = min(cand)
            for on, sx, sy in ((n and w, 1, 1), (n and e, -1, 1), (s and w, 1, -1), (s and e, -1, -1)):
                if not on:
                    continue
                lx = x if sx > 0 else 15 - x          # distances from the open corner
                ly = y if sy > 0 else 15 - y
                c0 = R_INSET + R_ROUND
                if lx < c0 and ly < c0:
                    dd = min(dd, R_ROUND - math.hypot(lx - c0, ly - c0))
            if notch:
                nx = x if "W" in notch else 15 - x
                ny = y if "N" in notch else 15 - y
                # the dry corner where the two roads' verges meet: a square with its inner corner rounded
                k = R_INSET - 1
                dn = max(nx - (k + RJAG[y % 8]), ny - (k + RJAG[x % 8]))
                if nx > k - 2 and ny > k - 2:
                    dn = max(dn, math.hypot(nx - (k - 2), ny - (k - 2)) - 2.0)
                dd = min(dd, dn)
            if dd >= 1:
                out[y][x] = road[y][x]
            elif dd >= 0:
                out[y][x] = R_D
            elif dd >= -1 and _hash(x % 8, y % 8, 3) < 0.4:
                out[y][x] = D2
            else:
                out[y][x] = dust[y][x]
    return out


ROAD_SIDES = {"C": (0, 0, 0, 0), "N": (1, 0, 0, 0), "S": (0, 1, 0, 0), "W": (0, 0, 1, 0), "E": (0, 0, 0, 1),
              "NW": (1, 0, 1, 0), "NE": (1, 0, 0, 1), "SW": (0, 1, 1, 0), "SE": (0, 1, 0, 1)}


# ================================================================ pieces
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[KEY] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else KEY

    def mirror(self):
        for y in range(self.h):
            for x in range(self.w // 2):
                self.px[y][self.w - 1 - x] = self.px[y][x]

    def outline(self, c, skip=()):
        hits = [(x, y) for y in range(self.h) for x in range(self.w)
                if self.px[y][x] == KEY and any(self.get(x + dx, y + dy) not in (KEY, c) + tuple(skip)
                                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in hits:
            self.px[y][x] = c


def canopy(cv, lobes, base_y):
    """A tree crown of leaf clumps. lobes: (cx, cy, rx, ry) for the left half (mirrored after); clumps further
    down are nearer the viewer and overlap those above. Each clump is lit on top, darkens below, and has a dark
    seam along its lower rim where it overlaps another clump."""
    half = cv.w // 2
    owner = [[-1] * cv.w for _ in range(cv.h)]
    order = sorted(range(len(lobes)), key=lambda i: lobes[i][1])
    for i in order:
        cx, cy, rx, ry = lobes[i]
        for y in range(cv.h):
            for x in range(half):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    owner[y][x] = i
    for y in range(cv.h):
        for x in range(half):
            i = owner[y][x]
            if i < 0:
                continue
            cx, cy, rx, ry = lobes[i]
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            v = -dy * 0.8 - dx * 0.15 + 0.3 * (_hash(x // 2, y // 2, 11) - 0.5) - 0.7 * (cy / base_y - 0.35)
            rim = dx * dx + dy * dy
            col = L4 if v > 0.85 else L3 if v > 0.3 else L2 if v > -0.35 else L1
            if rim > 0.72 and dy > 0.25:
                col = L0 if rim > 0.88 and dy > 0.45 else L1
            elif rim > 0.55 and dy < -0.45:   # each clump's lit crown
                col = {L1: L2, L2: L3, L3: L4, L4: L4}[col]
            cv.put(x, y, col)
    # leaf texture: sparse light and dark flecks
    for y in range(cv.h):
        for x in range(half):
            c = cv.px[y][x]
            if c in (L2, L3) and _hash(x, y, 12) < 0.12:
                cv.px[y][x] = L3 if c == L2 else L4
            elif c in (L2, L3) and _hash(x, y, 13) < 0.08:
                cv.px[y][x] = L1
    return owner


def trunk(cv, x0, x1, y0, y1, roots=2):
    """A trunk (left half; mirrored after): bark lit on the left, shaded right of centre, roots flaring at the
    foot; the canopy's shadow darkens its top."""
    half = cv.w // 2
    for y in range(y0, y1 + 1):
        flare = max(0, roots - (y1 - y)) if y > y1 - roots else 0
        for x in range(x0 - flare, half):
            if cv.px[y][x] != KEY and y < y0 + 2:
                continue
            k = x - (x0 - flare)
            c = B2 if k < 2 else B1
            if (x + y) % 5 == 0 and k >= 2:
                c = B0
            if y < y0 + 3:
                c = B0 if k >= 1 else B1
            cv.put(x, y, c)


def ground_shadow(cv, cx, cy, rx, ry):
    """A dithered shadow on the ground round the foot of a tree (works on earth and grass alike)."""
    for y in range(cv.h):
        for x in range(cv.w // 2):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0 and cv.px[y][x] == KEY and (x + y) % 2 == 0:
                cv.put(x, y, L0)


def field_tree():
    """A pecan, 2x3: a tall rounded crown of clumps over a short trunk."""
    cv = Canvas(32, 48)
    ground_shadow(cv, 16, 43, 11, 3.5)
    trunk(cv, 13, 0, 31, 44, roots=3)
    lobes = [(16, 6, 8, 6), (9, 9, 6, 5.5), (4, 15, 4.5, 5), (12, 14, 7, 6), (16, 19, 7, 6.5), (6, 22, 6, 5.5),
             (13, 25, 7, 6), (16, 29, 7, 5), (5.5, 28, 4.5, 4)]
    canopy(cv, lobes, 34)
    cv.mirror()
    cv.outline(L0, skip=(L0,))
    return cv


def field_tree_l():
    """A spreading live oak, 3x3: a broad low crown, heavy limbs, a thick short trunk."""
    cv = Canvas(48, 48)
    ground_shadow(cv, 24, 43, 16, 4)
    trunk(cv, 19, 0, 31, 44, roots=4)
    lobes = [(22, 6, 9, 5.5), (12, 8, 8, 5.5), (4.5, 14, 5, 5), (16, 13, 9, 6), (24, 15, 9, 6.5), (8, 20, 7, 6),
             (18, 22, 8, 6), (3.5, 22, 3.5, 4), (24, 26, 7, 5.5), (12, 27, 7, 5)]
    canopy(cv, lobes, 34)
    cv.mirror()
    cv.outline(L0, skip=(L0,))
    return cv


def rock(w, h, blobs, cracks=()):
    """A stone: a union of ellipses lit from the top-left, dark outline, a sliver of shadow at its foot."""
    cv = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            best = None
            for cx, cy, rx, ry in blobs:
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                q = dx * dx + dy * dy
                if q <= 1.0 and (best is None or cy > best[1][1]):
                    best = ((dx, dy, q), (cx, cy))
            if best is None:
                continue
            dx, dy, q = best[0]
            v = -0.65 * dx - 0.75 * dy + 0.15 * (_hash(x // 2, y // 2, 17) - 0.5)
            col = K3 if v > 0.75 else K2 if v > 0.15 else K1 if v > -0.45 else K0
            if q > 0.8 and dy > 0.1:
                col = K0
            cv.put(x, y, col)
    for pts in cracks:
        for x, y in pts:
            cv.put(x, y, K0)
            if cv.get(x + 1, y + 1) in (K1, K2, K3):
                cv.put(x + 1, y + 1, K2 if cv.get(x + 1, y + 1) == K3 else K1)
    cv.outline(B0)
    # contact shadow on the ground under the stone
    for x in range(w):
        for y in range(h - 1, 0, -1):
            if cv.get(x, y - 1) == B0 and cv.get(x, y) == KEY and _hash(x, y, 19) < 0.6:
                cv.put(x, y, L0) if (x + y) % 2 == 0 else None
                break
    return cv


def rock_s():
    return rock(16, 16, [(7.5, 10, 6, 4.5), (10.5, 11.5, 4, 3)], cracks=[((6, 9), (7, 10))])


def rock_l():
    return rock(32, 32, [(13, 15, 11, 10), (20, 19, 10, 9), (9, 23, 7, 5), (24, 25, 6.5, 4.5)],
                cracks=[((12, 9), (13, 10), (13, 11), (14, 12)), ((20, 15), (21, 16), (21, 17)),
                        ((8, 19), (9, 20), (10, 20))])


V2_SETS = [  # (prefix, its plain C cells [(name, texture)], the edge painter); salt's C is the v1 "salt" cell
    ("cane_wall", [("cane_wall", CANE_WALL)], paint_cane_wall),
    ("salt", [], paint_salt),
    ("red_earth", [("red_earth", red_tex(0)), ("red_earth_pebbles", red_tex(1)), ("red_earth_crack", red_tex(2))],
     paint_red),
    ("gully", [("gully", GULLY)], paint_gully),
]


V3_SETS = [  # (prefix, plain C cells, painter, edge from an in-corner, from an out-corner, corner roundness p);
    # dry_grass's C is the v1 cell [4, 0]
    ("rock_wall", [("rock_wall", ROCK_TOP)], paint_rock_wall, RW_IN, RW_OUT, 4.0),
    ("dry_grass", [], paint_dry_grass, T_IN, T_OUT, 2.0),
]


# ================================================================ the sheet
COLS = 9


def build():
    cells, pieces = {}, {}
    cells["dry"] = dry_tex(0)
    cells["dry_pebbles"] = dry_tex(1)
    cells["dry_crack"] = dry_tex(2)
    cells["dry_tuft"] = dry_tex(3)
    cells["dry_grass"] = dry_grass_tex()
    cells["cane"] = tile16(cane_tex())
    cells["pepper"] = tile16(pepper_tex())
    cells["salt"] = salt_tex()
    cells["salt_dry"] = salt_dry_tex()
    for bits, key in CORNER_KEYS.items():
        if key != "C":
            cells[key] = dry_edge(bits)
    for key, sides in ROAD_SIDES.items():
        cells["road_" + key] = road_piece(*sides)
    for k in ("NW", "NE", "SW", "SE"):
        cells["road_i" + k] = road_piece(0, 0, 0, 0, notch=k)
    layout = [["dry", "dry_pebbles", "dry_crack", "dry_tuft", "dry_grass", "cane", "pepper", "salt", "salt_dry"],
              EDGE_ORDER[:7], EDGE_ORDER[7:],
              ["road_" + k for k in ("C", "N", "S", "W", "E", "NW", "NE", "SW", "SE")],
              ["road_i" + k for k in ("NW", "NE", "SW", "SE")]]
    # v2 (2026-10-12): four more dual-grid sets on dry ground, each from a new row below the pieces (rows 10-17);
    # nothing of v1 moves
    v2_rows = []
    for prefix, plain_cells, paint in V2_SETS:
        names = []
        for name, tex in plain_cells:
            cells[name] = tex
            names.append(name)
        for key, tile in edge_set(paint).items():
            cells[f"{prefix}_{key}"] = tile
        names += [f"{prefix}_{k}" for k in EDGE_ORDER]
        while names:
            v2_rows.append(names[:COLS])
            names = names[COLS:]
    # v3: the rock wall and the dry-grass border (rows 18-21)
    for prefix, plain_cells, paint, tin, tout, pn in V3_SETS:
        names = []
        for name, tex in plain_cells:
            cells[name] = tex
            names.append(name)
        if prefix == "rock_wall":
            edges, bottoms = rock_wall_edges()
        else:
            edges = edge_set(paint, tin, tout, pn)
        for key, tile in edges.items():
            cells[f"{prefix}_{key}"] = tile
        names += [f"{prefix}_{k}" for k in EDGE_ORDER]
        while names:
            v2_rows.append(names[:COLS])
            names = names[COLS:]
    # v3b: the rock wall's face-extension cells (row 22)
    cells.update(rock_wall_extensions(bottoms))
    v2_rows.append(list(FACE_KEYS))
    # v3c: the plateau top's variations (row 23)
    for name, tex in ROCK_TOP_VARIANTS:
        cells[name] = tex
    v2_rows.append([n for n, _ in ROCK_TOP_VARIANTS])
    rows = len(layout) + 5 + len(v2_rows)
    sheet = Image.new("RGB", (COLS * 16, rows * 16), KEY)
    pos = {}
    for cy, row in enumerate(layout):
        for cx, name in enumerate(row):
            for y in range(16):
                for x in range(16):
                    sheet.putpixel((cx * 16 + x, cy * 16 + y), cells[name][y][x])
            pos[name] = [cx, cy]
    for cy, row in enumerate(v2_rows, start=len(layout) + 5):
        for cx, name in enumerate(row):
            for y in range(16):
                for x in range(16):
                    sheet.putpixel((cx * 16 + x, cy * 16 + y), cells[name][y][x])
            pos[name] = [cx, cy]
    py = len(layout)
    for name, cv, (cx, cy), comment in (
            ("field_tree", field_tree(), (0, py), "A pecan at a field's edge (2x3, blocking)."),
            ("field_tree_l", field_tree_l(), (2, py), "A spreading live oak (3x3, blocking)."),
            ("rock", rock_s(), (5, py), "A stone (1x1, blocking)."),
            ("rock_l", rock_l(), (6, py), "A boulder (2x2, blocking).")):
        for y in range(cv.h):
            for x in range(cv.w):
                sheet.putpixel((cx * 16 + x, cy * 16 + y), cv.px[y][x])
        w, h = cv.w // 16, cv.h // 16
        empty = [[i, j] for j in range(h) for i in range(w)
                 if all(cv.px[j * 16 + y][i * 16 + x] == KEY for y in range(16) for x in range(16))]
        pieces[name] = {"x": cx, "y": cy, "w": w, "h": h, "doors": [], "passable": [], "empty": empty,
                        "comment": comment}
    terrain = {"dry": [pos["dry"], pos["dry_pebbles"], pos["dry_crack"], pos["dry_tuft"]]}
    for name in ("dry_grass", "cane", "pepper", "salt", "salt_dry"):
        terrain[name] = pos[name]
    for k in EDGE_ORDER:
        terrain[k] = pos[k]
    for k in list(ROAD_SIDES) + ["iNW", "iNE", "iSW", "iSE"]:
        terrain["road_" + k] = pos["road_" + k]
    for prefix, plain_cells, paint in V2_SETS + [t_[:3] for t_ in V3_SETS]:
        if plain_cells:
            v = [pos[n] for n, _ in plain_cells]
            terrain[prefix] = v if len(v) > 1 else v[0]
        for k in EDGE_ORDER:
            terrain[f"{prefix}_{k}"] = pos[f"{prefix}_{k}"]
    for k in FACE_KEYS:
        terrain[k] = pos[k]
    terrain["rock_wall"] = [pos["rock_wall"]] + [pos[n] for n, _ in ROCK_TOP_VARIANTS]
    index = {
        "_comment": "The shared dry-country set (make_dry_country.py). Terrain cells are opaque, pieces are "
                    "overlays (magenta = clear); cells are [x, y] in 16 px units. dry: plain first, then "
                    "variations. N..sTRBL: dry ground on Ekat's grass, the dual grid of Ekat's marsh set. "
                    "road_*: the cell-based road on dry ground (build.py path_tile keys). cane = encounter "
                    "grass. salt / salt_dry: Route 24's salt crust. v2: dry_grass is tall dry grass (encounter "
                    "grass) ringed by dry[0]'s pixels; four dual-grid sets on dry ground (patch inside, dry[0] "
                    "outside), each <prefix> (its C fill: a cell or a list, plain first) + <prefix>_N ... "
                    "<prefix>_sTRBL with Ekat's corner keys: cane_wall (blocking cane-field backdrop, its stalk "
                    "face on the south), salt (C = the salt crust cell), red_earth, gully (an eroded gully, its "
                    "wall face on the north side). v3: rock_wall (+ rock_wall_N ... sTRBL), a blocking bedrock "
                    "wall with a 14 px cliff face on its south side (its own geometry: the edge 15 px from an "
                    "in-corner); dry_grass is now a continuous tall-grass fill and dry_grass_N ... sTRBL its "
                    "ragged border on dry ground. rock_wall_face / _face_l / _face_r / _face_il / _face_ir: the "
                    "face-extension cells under the wall's south edge (make_dry_country.face_cells gives the rule). "
                    "rock_wall is a list like dry: the plain fill, then crack, slab and weathered variations.",
        "png": "dry_country.png", "terrain": terrain, "pieces": pieces}
    return sheet, index


# ================================================================ review: test patches and tile counts
def cell_img(sheet, xy):
    return sheet.crop((xy[0] * 16, xy[1] * 16, xy[0] * 16 + 16, xy[1] * 16 + 16))


def grass_img():
    im = Image.new("RGB", (16, 16))
    for y in range(16):
        for x in range(16):
            im.putpixel((x, y), GRASS[y][x])
    return im


def render_patch(sheet, index, rows, objects=(), images=()):
    """Draw a test map the way build.py would: '.' grass, 'd' dry (dual grid against grass; the road, cane,
    pepper, dry grass and salt count as dry ground for it, as they should in the layout), ':' road (path_tile),
    'G' cane, 'q' pepper, 'g' dry grass, 's' salt, 'z' salt-flecked earth. objects: (piece, x, y) overlays."""
    t = index["terrain"]
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, ".") for r in rows]
    h = len(rows)
    at = lambda x, y: rows[min(max(y, 0), h - 1)][min(max(x, 0), w - 1)]
    con = "d:GqgszTWSruR"
    out = Image.new("RGB", (w * 16, h * 16))
    grass = grass_img()
    plain = {"G": "cane", "q": "pepper", "g": "dry_grass", "s": "salt", "z": "salt_dry", "W": "cane_wall",
             "S": "salt", "r": "red_earth", "u": "gully", "R": "rock_wall"}
    for y in range(h):
        for x in range(w):
            ch = rows[y][x]
            if ch in ".d":
                bits = "".join("1" if at(x + dx, y + dy) in con else "0" for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)))
                key = CORNER_KEYS[bits] if bits != "0000" else None
                if key is None:
                    im = grass
                elif key == "C":
                    v = t["dry"]
                    im = cell_img(sheet, v[0] if (x * 31 + y * 17) % 9 else v[(x * 7 + y * 13) % len(v)])
                else:
                    im = cell_img(sheet, t[key])
            elif ch == ":":
                same = lambda i, j: at(i, j) == ":" or not (0 <= i < w and 0 <= j < h)
                n, s = same(x, y - 1), same(x, y + 1)
                ww, e = same(x - 1, y), same(x + 1, y)
                if not n and not s:
                    n = s = True
                if not ww and not e:
                    ww = e = True
                key = ("N" if not n else "S" if not s else "") + ("W" if not ww else "E" if not e else "")
                if not key:
                    for dx, dy, k in ((-1, -1, "iNW"), (1, -1, "iNE"), (-1, 1, "iSW"), (1, 1, "iSE")):
                        if not same(x + dx, y + dy):
                            key = k
                            break
                im = cell_img(sheet, t["road_" + (key or "C")])
            else:
                v = t[plain[ch]]
                im = cell_img(sheet, v[0] if isinstance(v[0], list) else v)
            out.paste(im, (x * 16, y * 16))
    # the v2 dual-grid sets on dry ground: 'W' cane wall, 'S' salt crust, 'r' red earth (pepper rows count as red
    # earth), 'u' gully; drawn on their own cells and on dry cells next to them
    for ch, prefix, conn in V2_CHARS + V3_CHARS:
        for y in range(h):
            for x in range(w):
                if rows[y][x] not in "d" + ch:
                    continue
                bits = "".join("1" if at(x + dx, y + dy) in conn else "0" for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)))
                if bits == "0000":
                    continue
                key = CORNER_KEYS[bits]
                if key == "C":
                    v = t[prefix]
                    if isinstance(v[0], list) and prefix == "rock_wall":    # scattered about 1 in 4
                        v = v[0] if _hash(x, y, 131) >= 0.25 else v[1 + int(_hash(x, y, 132) * (len(v) - 1))]
                    elif isinstance(v[0], list):
                        v = v[0] if (x * 31 + y * 17) % 9 else v[(x * 7 + y * 13) % len(v)]
                    im = cell_img(sheet, v)
                else:
                    im = cell_img(sheet, t[f"{prefix}_{key}"])
                out.paste(im, (x * 16, y * 16))
    if any("R" in r for r in rows) and "rock_wall_face" in t:
        for (x, y), key in face_cells(at, w, h).items():
            out.paste(cell_img(sheet, t[key]), (x * 16, y * 16))
    for name, ox, oy in objects:
        p = index["pieces"][name]
        art = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        a = np.array(art)
        m = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
        out.paste(art, (ox * 16, oy * 16), Image.fromarray((m * 255).astype(np.uint8)))
    for art, ox, oy in images:
        out.paste(art, (ox * 16, oy * 16), art)
    return out


PATCHES = [
    ("blob, L-shape, 1-wide neck, diagonal touches", [
        "..................",
        "..ddd.......d.....",
        ".ddddd.....ddd....",
        ".dddddd.....d.....",
        "..dddd...........",
        "...dd....ddddddd..",
        ".........d........",
        ".d.d.....d........",
        "..d......d...dd...",
        ".d.d.........dd...",
        "...........dd.....",
        "...........dd.....",
        ".................."]),
    ("road through dry ground and grass, a crossing, a bend", [
        "dddddddd::dddddd",
        "dddddddd::dddddd",
        "::::::::::::::dd",
        "::::::::::::::dd",
        "dddddddd::dd::dd",
        "dddddddd::dd::dd",
        "....ddd.::dd::::",
        "........::dd::::",
        "........::dddddd",
        "........::ddd...",
        "........::......"]),
    ("cane field beside grass and dry ground, pepper rows, dry grass, salt", [
        "GGGGGGGG....dddddddd",
        "GGGGGGGG....dqqqqqqd",
        "GGGGGGGGdd..dqqqqqqd",
        "GGGGGGGGdd..dqqqqqqd",
        "GGGGGGGGdd..dddddddd",
        "GGGGGGGG....ggggdddd",
        "dddddddd....ggggzzss",
        "dddddddd....ggggzsss",
        "............dddzssss"]),
]
TREES = ("trees and rocks on dry ground", [
    "dddddddddddddddd",
    "dddddddddddddddd",
    "dddddddddddddddd",
    "dddddddddddddddd",
    "dddddddddddd....",
    "ddddddddddd.....",
    "dddddddddd......",
    "dddddddddd......"],
    [("field_tree", 1, 1), ("field_tree_l", 4, 1), ("rock", 9, 2), ("rock_l", 10, 1), ("field_tree", 12, 4),
     ("rock", 8, 6), ("field_tree_l", 0, 5)])


def tile_census(sheet, index):
    """Unique 8x8 tiles per group (flips count as the same tile; Ekat's grass quarters already exist)."""
    a = np.array(sheet)
    g = np.array(grass_img())
    known = set()

    def canon(t):
        return min(x.tobytes() for x in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))
    for qy in (0, 8):
        for qx in (0, 8):
            known.add(canon(g[qy:qy + 8, qx:qx + 8]))
    groups = {"dry ground (plain + variations)": ["dry"], "dry grass": ["dry_grass"], "cane": ["cane"],
              "pepper": ["pepper"], "salt (extra)": ["salt", "salt_dry"], "dry-on-grass edge set": EDGE_ORDER,
              "road set": ["road_" + k for k in list(ROAD_SIDES) + ["iNW", "iNE", "iSW", "iSE"]]}
    cells_of = {}
    for gname, keys in groups.items():
        cs = []
        for k in keys:
            v = index["terrain"][k]
            cs += v if isinstance(v[0], list) else [v]
        cells_of[gname] = cs
    for name, p in index["pieces"].items():
        cells_of[f"{name} ({p['w']}x{p['h']})"] = [[p["x"] + i, p["y"] + j] for j in range(p["h"]) for i in range(p["w"])]
    seen = set(known)
    report = []
    total = 0
    for gname, cs in cells_of.items():
        n = 0
        for cx, cy in cs:
            for qy in (0, 8):
                for qx in (0, 8):
                    t = a[cy * 16 + qy:cy * 16 + qy + 8, cx * 16 + qx:cx * 16 + qx + 8]
                    if ((t[..., 0] == 255) & (t[..., 1] == 0) & (t[..., 2] == 255)).all():
                        continue
                    k = canon(t)
                    if k not in seen:
                        seen.add(k)
                        n += 1
        cols = len({tuple(map(tuple, a[cy * 16:cy * 16 + 16, cx * 16:cx * 16 + 16].reshape(-1, 3))) for cx, cy in cs})
        report.append((gname, len(cs), n))
        total += n
    return report, total


def colour_families(sheet, index):
    a = np.array(sheet)
    fam = {}
    groups = {"ground (edge set, dry, road)": EDGE_ORDER + ["dry"] + ["road_" + k for k in list(ROAD_SIDES) +
                                                                     ["iNW", "iNE", "iSW", "iSE"]],
              "dry grass": ["dry_grass"], "crops (cane, pepper)": ["cane", "pepper"], "salt": ["salt", "salt_dry"]}
    for gname, keys in groups.items():
        cols = set()
        for k in keys:
            v = index["terrain"][k]
            for cx, cy in (v if isinstance(v[0], list) else [v]):
                cols |= {tuple(c) for c in a[cy * 16:cy * 16 + 16, cx * 16:cx * 16 + 16].reshape(-1, 3)}
        fam[gname] = len(cols)
    cols = set()
    for p in index["pieces"].values():
        blk = a[p["y"] * 16:(p["y"] + p["h"]) * 16, p["x"] * 16:(p["x"] + p["w"]) * 16].reshape(-1, 3)
        cols |= {tuple(c) for c in blk if tuple(c) != KEY}
    fam["pieces (trees, rocks)"] = len(cols)
    return fam


def review(sheet, index, path):
    S = 3
    blocks = []
    # every cell at 3x with its name
    names = [(k, v) for k, v in index["terrain"].items() if k != "dry" and k not in v2_keys() and k not in v3_keys()] + \
            [(f"dry[{i}]", v) for i, v in enumerate(index["terrain"]["dry"])]
    names.sort(key=lambda kv: (kv[1][1], kv[1][0]))
    lab_w = 16 * S + 12
    per_row = 9
    cells_h = ((len(names) + per_row - 1) // per_row) * (16 * S + 16)
    piece_imgs = []
    for name, p in index["pieces"].items():
        art = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        bg = Image.new("RGB", art.size, (255, 0, 255))
        piece_imgs.append((name, art.resize((art.width * S, art.height * S), Image.NEAREST)))
    patches = [(title, render_patch(sheet, index, rows)) for title, rows in PATCHES]
    patches.append((TREES[0], render_patch(sheet, index, TREES[1], TREES[2])))
    report, total = tile_census(sheet, index)
    fam = colour_families(sheet, index)
    W = 1500
    ph = sum(p.height * S + 24 for _, p in patches)
    H = 40 + cells_h + 16 * 3 * S + 40 + ph + 40 + 20 * (len(report) + len(fam) + 4)
    H += 0
    out = Image.new("RGB", (W, H), (36, 40, 44))
    d = ImageDraw.Draw(out)
    y = 8
    d.text((10, y), "Dry country set (make_dry_country.py): every cell at 3x, test patches at 3x", fill=(240, 240, 240))
    y += 24
    for i, (name, (cx, cy)) in enumerate(names):
        col, row = i % per_row, i // per_row
        x0, y0 = 10 + col * (16 * S + 110), y + row * (16 * S + 16)
        out.paste(cell_img(sheet, [cx, cy]).resize((16 * S, 16 * S), Image.NEAREST), (x0, y0))
        d.text((x0 + 16 * S + 4, y0 + 18), name, fill=(220, 220, 200))
    y += cells_h + 8
    x = 10
    rowh = 0
    for name, im in piece_imgs:
        bg = Image.new("RGB", im.size, (90, 90, 96))
        a = np.array(im)
        m = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
        bg.paste(im, (0, 0), Image.fromarray((m * 255).astype(np.uint8)))
        out.paste(bg, (x, y + 14))
        d.text((x, y), name, fill=(220, 220, 200))
        x += im.width + 30
        rowh = max(rowh, im.height + 20)
    y += rowh + 10
    x = 10
    for title, im in patches:
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        if x + big.width > W - 10:
            x = 10
            y = ybot
        d.text((x, y), title, fill=(240, 240, 240))
        out.paste(big, (x, y + 16))
        ybot = y + 16 + big.height + 12
        x += big.width + 20
    y = ybot + 8
    d.text((10, y), "Unique 8x8 tiles (flips free; Ekat grass quarters already in the tileset):", fill=(240, 240, 200))
    y += 18
    for gname, ncell, n in report:
        d.text((20, y), f"{gname}: {ncell} cells, {n} new tiles", fill=(220, 220, 220))
        y += 16
    d.text((20, y), f"TOTAL: {total} unique 8x8 tiles", fill=(255, 255, 160))
    y += 22
    d.text((10, y), "Colours per family: " + ", ".join(f"{k} {v}" for k, v in fam.items()), fill=(220, 220, 220))
    y += 24
    out = out.crop((0, 0, W, y))
    out.save(path)
    return report, total, fam


V2_CHARS = [("W", "cane_wall", "W"), ("S", "salt", "S"), ("r", "red_earth", "rq"), ("u", "gully", "u")]


def v2_keys():
    keys = set()
    for prefix, plain_cells, _ in V2_SETS:
        keys |= {n for n, _ in plain_cells} | {prefix} | {f"{prefix}_{k}" for k in EDGE_ORDER}
    return keys - {"salt"}


V2_PATCHES = [
    ("cane-field backdrop (blocking) with a 2-wide road, beside a walk-in cane patch (encounters)", [
        "WWWWWWWWW::dWWWWWWWW",
        "WWWWWWWWW::dWWWWWWWW",
        "WWWWWWWWW::dWWWWWWWW",
        "WWWddddWd::dWWWWWWWW",
        "WWWdGGGdd::dWWWWWWWW",
        "WWddGGGGd:::::::::::",
        "WWdGGGGdd:::::::::::",
        "WWddGGddd::ddddddddd",
        "WWWWdddWd::dWWWWWWWW",
        "WWWWWWWWW::dWWWWWWWW",
        "WWWWWWWWW::dWWWWWWWW"]),
    ("salt flat edging into dry ground, dry-grass encounter patches", [
        "SSSSSSSSSSSdddddddd",
        "SSSSSSSSSSSSddggggd",
        "SSSSSSSSSSSdddggggd",
        "SSSSSSSSSddddddgggd",
        "SSSSSSSSdddggdddddd",
        "SSSSSSSSSddggdddddd",
        "SSSSSSSdddddddddddd",
        "SSSSddddSSddddggggd",
        "SSSddddSSSddddggggd",
        "SSdddddddddddddd:::",
        "dddddddddddddddd:::"]),
    ("red earth with pepper rows", [
        "dddddrrrrrrrrrrdddd",
        "ddrrrrrrrrrrrrrrddd",
        "drrqqqqqqqqqqrrrrdd",
        "drrqqqqqqqqqqrrrrdd",
        "drrqqqqqqqqqqrrrddd",
        "drrrrrrrrrrrrrrrddd",
        "ddrrrrrrrrrrrrdrrdd",
        "dddrrrdddrrrrdddddd",
        "ddddddddddddddddddd"]),
    ("a winding gully in dry ground (1 and 2 wide, a bend, a diagonal step, a spur)", [
        "dddddddddddddddddddd",
        "uuuudddddddddddddddd",
        "uuuuuudddddddddddddd",
        "dddduuuudddddddddddd",
        "dddddduuuddddddudddd",
        "ddddddduudddddduuddd",
        "dddddddduuuuuuuuuddd",
        "ddddddddduuuuuuuuudd",
        "dddddddddddddddduuuu",
        "dddddddddddddddddduu",
        "dddddddddddddddddddd"]),
]
V2_CROP = "Gq"   # crop fields: check.py treats their outline as an object edge


def seam_pair(a, b):
    """check.py's measure for a cell a left of cell b (arrays 16x16x3): the colour jump across the shared side
    less the jump just inside each cell."""
    a, b = a.astype(int), b.astype(int)
    d = lambda p, q: np.abs(p - q).sum(-1)
    return d(a[:, 15], b[:, 0]).mean() - (d(a[:, 14], a[:, 15]).sum() + d(b[:, 0], b[:, 1]).sum()) / 32


def patch_seams(img, rows):
    a = np.array(img)
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, ".") for r in rows]
    worst = []
    for y in range(len(rows)):
        for x in range(w):
            c = a[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if x + 1 < w and rows[y][x] not in V2_CROP and rows[y][x + 1] not in V2_CROP:
                worst.append((seam_pair(c, a[y * 16:y * 16 + 16, x * 16 + 16:x * 16 + 32]), x, y, "R"))
            if y + 1 < len(rows) and rows[y][x] not in V2_CROP and rows[y + 1][x] not in V2_CROP:
                n = a[y * 16 + 16:y * 16 + 32, x * 16:x * 16 + 16]
                worst.append((seam_pair(c.transpose(1, 0, 2), n.transpose(1, 0, 2)), x, y, "D"))
    worst.sort(reverse=True)
    return worst


def census_v2(sheet, index):
    """New unique 8x8 tiles of v2 (flips free): against Ekat's grass and every v1 tile that v2 kept."""
    a = np.array(sheet)

    def canon(t):
        return min(x.tobytes() for x in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))

    def quarters(cx, cy):
        for qy in (0, 8):
            for qx in (0, 8):
                t = a[cy * 16 + qy:cy * 16 + qy + 8, cx * 16 + qx:cx * 16 + qx + 8]
                if not ((t[..., 0] == 255) & (t[..., 1] == 0) & (t[..., 2] == 255)).all():
                    yield canon(t)
    g = np.array(grass_img())
    seen = {canon(g[qy:qy + 8, qx:qx + 8]) for qy in (0, 8) for qx in (0, 8)}
    T = index["terrain"]
    redrawn = {"dry_grass", "salt"}
    new = v2_keys() | v3_keys()
    cells = lambda k: T[k] if isinstance(T[k][0], list) else [T[k]]
    for k in T:
        if k not in redrawn and k not in new:
            for cx, cy in cells(k):
                seen |= set(quarters(cx, cy))
    for p in index["pieces"].values():
        for j in range(p["h"]):
            for i in range(p["w"]):
                seen |= set(quarters(p["x"] + i, p["y"] + j))
    groups = [("dry_grass (redrawn: tall dry grass)", ["dry_grass"]), ("salt crust (redrawn: tiles)", ["salt"])]
    for prefix, plain_cells, _ in V2_SETS:
        keys = ([prefix] if plain_cells else []) + [f"{prefix}_{k}" for k in EDGE_ORDER]
        groups.append((f"{prefix} set ({len(plain_cells) + 14} cells)", keys))
    report, total = [], 0
    for gname, keys in groups:
        n = 0
        for k in keys:
            for cx, cy in cells(k):
                for q in quarters(cx, cy):
                    if q not in seen:
                        seen.add(q)
                        n += 1
        report.append((gname, n))
        total += n
    return report, total


def review_v2(sheet, index, path):
    S = 3
    T = index["terrain"]
    names = []
    for k in ["dry_grass", "salt"] + [k for k in T if k in v2_keys()]:
        v = T[k]
        if isinstance(v[0], list):
            names += [(f"{k}[{i}]", c) for i, c in enumerate(v)]
        else:
            names.append((k, v))
    names.sort(key=lambda kv: (kv[1][1], kv[1][0]))
    patches = [(title, rows, render_patch(sheet, index, rows)) for title, rows in V2_PATCHES]
    report, total = census_v2(sheet, index)
    # seams: the plain cells against themselves and their neighbours, and every cell side in the test patches
    a = np.array(sheet)
    cell = lambda xy: a[xy[1] * 16:xy[1] * 16 + 16, xy[0] * 16:xy[0] * 16 + 16]
    dry0 = cell(T["dry"][0])
    plain_seams = []
    plain_list = [("dry_grass", T["dry_grass"]), ("salt", T["salt"]), ("cane_wall", T["cane_wall"]),
                  ("gully", T["gully"])] + [(f"red_earth[{i}]", c) for i, c in enumerate(T["red_earth"])]
    for name, xy in plain_list:
        c = cell(xy)
        sv = max(seam_pair(c, c), seam_pair(c.transpose(1, 0, 2), c.transpose(1, 0, 2)))
        plain_seams.append(f"{name}|itself {sv:.1f}")
    g = cell(T["dry_grass"])
    T_ = lambda c: c.transpose(1, 0, 2)
    for k, (first, second, vertical) in {"dry": ("g", "c", False), "road_N": ("g", "c", True),
                                         "road_S": ("c", "g", True), "road_W": ("g", "c", False),
                                         "road_E": ("c", "g", False)}.items():
        c = cell(T[k][0] if isinstance(T[k][0], list) else T[k])
        pair = [g if w_ == "g" else c for w_ in (first, second)]
        sv = seam_pair(T_(pair[0]), T_(pair[1])) if vertical else seam_pair(pair[0], pair[1])
        if k == "dry":
            sv = max(sv, seam_pair(c, g), seam_pair(T_(g), T_(c)), seam_pair(T_(c), T_(g)))
        plain_seams.append(f"dry_grass|{k} {sv:.1f}")
    W = 1500
    rows_h = ((len(names) + 8) // 9) * (16 * S + 16)
    ph = sum(im.height * S + 40 for _, _, im in patches)
    out = Image.new("RGB", (W, 60 + rows_h + ph + 400), (36, 40, 44))
    d = ImageDraw.Draw(out)
    y = 8
    d.text((10, y), "Dry country v2 (make_dry_country.py): the new and redrawn cells at 3x, test patches at 3x",
           fill=(240, 240, 240))
    y += 24
    for i, (name, (cx, cy)) in enumerate(names):
        col, row = i % 9, i // 9
        x0, y0 = 10 + col * (16 * S + 110), y + row * (16 * S + 16)
        out.paste(cell_img(sheet, [cx, cy]).resize((16 * S, 16 * S), Image.NEAREST), (x0, y0))
        d.text((x0 + 16 * S + 4, y0 + 18), name, fill=(220, 220, 200))
    y += rows_h + 8
    x, ybot = 10, y
    seam_lines = []
    for title, rows, im in patches:
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        if x + big.width > W - 10:
            x, y = 10, ybot
        d.text((x, y), title, fill=(240, 240, 240))
        out.paste(big, (x, y + 16))
        ybot = max(ybot, y + 16 + big.height + 14)
        x += big.width + 20
        ws = patch_seams(im, rows)
        over = [w_ for w_ in ws if w_[0] > 20]
        seam_lines.append(f"{title[:40]}...: worst cell-side seam {ws[0][0]:.1f}, {len(over)} above 20")
    y = ybot + 6
    d.text((10, y), "New unique 8x8 tiles in v2 (flips free; Ekat grass and every kept v1 tile already exist):",
           fill=(240, 240, 200))
    y += 18
    for gname, n in report:
        d.text((20, y), f"{gname}: {n}", fill=(220, 220, 220))
        y += 16
    d.text((20, y), f"TOTAL new: {total}", fill=(255, 255, 160))
    y += 22
    d.text((10, y), "Seams (check.py's measure, target <= 20):", fill=(240, 240, 200))
    y += 18
    for line in seam_lines + ["; ".join(plain_seams[:5]), "; ".join(plain_seams[5:])]:
        d.text((20, y), line, fill=(220, 220, 220))
        y += 16
    out.crop((0, 0, W, y + 10)).save(path)
    return report, total, seam_lines, plain_seams


V3_CHARS = [("R", "rock_wall", "R"), ("g", "dry_grass", "g")]


def v3_keys():
    keys = set()
    for prefix, plain_cells, *_ in V3_SETS:
        keys |= {n for n, _ in plain_cells} | {f"{prefix}_{k}" for k in EDGE_ORDER}
    return keys | set(FACE_KEYS)


def landmark_images():
    """The mouths the rock wall's face must take (for the review only): the route landmarks' mine_mouth (3x3) and
    Cianwood's cave mouth (3x2: boulder 342-344 / 352, 368 (the opening), 354 from the HnS tilesets, its sand
    keyed out as the route recipe's rebase_ground does)."""
    out = {}
    idx = json.load(open(os.path.join(HERE, "route_landmarks.json"), encoding="utf-8"))
    m = idx["pieces"]["mine_mouth"]
    im = Image.open(os.path.join(HERE, "route_landmarks.png")).convert("RGB")
    art = im.crop((m["x"] * 16, m["y"] * 16, (m["x"] + m["w"]) * 16, (m["y"] + m["h"]) * 16))
    a = np.array(art)
    alpha = (~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)) * 255).astype(np.uint8)
    out["mine_mouth"] = Image.merge("RGBA", (*art.split(), Image.fromarray(alpha)))
    root = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
    try:
        sys.path.insert(0, MAPGEN)
        from render import Tilesets
        ts = Tilesets(os.path.join(root, "data/tilesets/primary/johto_general_hns"),
                      os.path.join(root, "data/tilesets/secondary/cianwood_city_hns"), layout="frlg")
        cave = Image.new("RGB", (48, 32))
        for j, row in enumerate(((0x342, 0x343, 0x344), (0x352, 0x368, 0x354))):
            for i, mid in enumerate(row):
                cave.paste(ts.metatile(mid), (i * 16, j * 16))
        sand = {(238, 230, 139), (74, 123, 222), (74, 148, 222), (139, 164, 255), (82, 156, 230), (216, 192, 136),
                (230, 213, 139), (106, 164, 230), (213, 197, 106), (208, 184, 104)}
        a = np.array(cave)
        alpha = np.array([[0 if tuple(c) in sand else 255 for c in row] for row in a], dtype=np.uint8)
        out["cave_mouth"] = Image.merge("RGBA", (*cave.split(), Image.fromarray(alpha)))
    except Exception as e:      # the HnS tilesets are optional for the review
        print("  (no Cianwood cave mouth for the review:", e, ")")
    return out


V3_PATCHES = [
    ("rock wall: a 2-cell face (S edge + extension row) with the mine mouth and Cianwood's cave mouth at its foot, "
     "a road along it, a salt flat", [
        "RRRRRRRRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRdddRRRRRRRRR",
        "dRRRRRRRRRRdddddRRRRRRRR",
        "ddRRRRRRRRddddddRRRRRRRd",
        "dddddddddddddddddddddddd",
        "ddd::::::::::::::::::ddd",
        "ddd::::::::::::::::::ddd",
        "ddddddddddddddddd::ddddd",
        "dddddddSSSSdddddd::ddddd",
        "ddddSSSSSSSSddddd::ddddd",
        "dddSSSSSSSSSSdddd::ddddd"],
     [("mine_mouth", 4, 5), ("cave_mouth", 18, 6)]),
    ("a bluff: outer and inner corners of the face, steps, a 1-wide spur", [
        "RRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRRRR",
        "dRRRRRRRRRRRRRRRRR",
        "ddRRRRRRdddRRRRRRR",
        "ddddRRRRddddRRRRRR",
        "dddddddddddddRRRRR",
        "ddddddddddddddRRdd",
        "ddddddddddddddRRdd",
        "dddddddddddddddddd",
        "dddddddddddddddddd"],
     []),
    ("dry-grass encounter patches on dry ground beside a road", [
        "dddddddddddddddddddddd",
        "ddgggddddddddddddddddd",
        "dgggggdddd::::::::::::",
        "dgggggdddd::::::::::::",
        "ddggddddddd::ddddddddd",
        "ddddddgdddd::ddgggdddd",
        "dddddggggdd::dgggggddd",
        "dddddggggdd::ddgggggdd",
        "ddddddggddd::dddgggddd",
        "::::::::::::::dddddgdd",
        "::::::::::::::dddddddd",
        "ddddddddddddddddgggggd",
        "ddgggggdddggddgggggggd",
        "dggggggggdggdddggggddd",
        "ddddgggddddddddddddddd"],
     []),
]


def census_v3(sheet, index):
    """New unique 8x8 tiles of v3 (flips free) against Ekat's grass and everything v1/v2 kept."""
    a = np.array(sheet)

    def canon(t):
        return min(x.tobytes() for x in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))

    def quarters(cx, cy):
        for qy in (0, 8):
            for qx in (0, 8):
                t = a[cy * 16 + qy:cy * 16 + qy + 8, cx * 16 + qx:cx * 16 + qx + 8]
                if not ((t[..., 0] == 255) & (t[..., 1] == 0) & (t[..., 2] == 255)).all():
                    yield canon(t)
    g = np.array(grass_img())
    seen = {canon(g[qy:qy + 8, qx:qx + 8]) for qy in (0, 8) for qx in (0, 8)}
    T = index["terrain"]
    new = v3_keys() | {"rock_wall", "dry_grass"}
    cells = lambda k: T[k] if isinstance(T[k][0], list) else [T[k]]
    for k in T:
        if k not in new:
            for cx, cy in cells(k):
                seen |= set(quarters(cx, cy))
    for p in index["pieces"].values():
        for j in range(p["h"]):
            for i in range(p["w"]):
                seen |= set(quarters(p["x"] + i, p["y"] + j))
    groups = [("dry_grass fill (redrawn: continuous)", ["dry_grass"]),
              ("dry_grass border set (14 cells)", [f"dry_grass_{k}" for k in EDGE_ORDER]),
              ("rock_wall set (15 cells + 3 variations)", ["rock_wall"] + [f"rock_wall_{k}" for k in EDGE_ORDER]),
              ("rock_wall face extension (8 cells)", list(FACE_KEYS))]
    report, total = [], 0
    for gname, keys in groups:
        n = 0
        for k in keys:
            for cx, cy in cells(k):
                for q in quarters(cx, cy):
                    if q not in seen:
                        seen.add(q)
                        n += 1
        report.append((gname, n))
        total += n
    return report, total


def review_v3(sheet, index, path):
    S = 3
    T = index["terrain"]
    names = [(k, T[k]) for k in ["dry_grass"] + [f"{p}_{k}" for p in ("rock_wall", "dry_grass")
                                                for k in EDGE_ORDER] + FACE_KEYS]
    names += [(f"rock_wall[{i}]", c) for i, c in enumerate(T["rock_wall"])]
    names.sort(key=lambda kv: (kv[1][1], kv[1][0]))
    lm = landmark_images()
    patches = []
    for title, rows, objs in V3_PATCHES:
        imgs = [(lm[n], x, y) for n, x, y in objs if n in lm]
        patches.append((title, rows, render_patch(sheet, index, rows), render_patch(sheet, index, rows, images=imgs)))
    report, total = census_v3(sheet, index)
    a = np.array(sheet)
    cell = lambda xy: a[xy[1] * 16:xy[1] * 16 + 16, xy[0] * 16:xy[0] * 16 + 16]
    seam_lines = []
    for name in ("dry_grass", "rock_wall"):
        c = cell(T[name][0] if isinstance(T[name][0], list) else T[name])
        sv = max(seam_pair(c, c), seam_pair(c.transpose(1, 0, 2), c.transpose(1, 0, 2)))
        seam_lines.append(f"{name}|itself {sv:.1f}")
    W = 1500
    rows_h = ((len(names) + 8) // 9) * (16 * S + 16)
    ph = sum(im.height * S + 40 for *_, im in patches)
    out = Image.new("RGB", (W, 60 + rows_h + ph + 300), (36, 40, 44))
    d = ImageDraw.Draw(out)
    y = 8
    d.text((10, y), "Dry country v3 (make_dry_country.py): rock_wall and the dry-grass field, cells at 3x, test "
                    "patches at 3x (the mine and cave mouths are the existing pieces, laid over the face)",
           fill=(240, 240, 240))
    y += 24
    for i, (name, (cx, cy)) in enumerate(names):
        col, row = i % 9, i // 9
        x0, y0 = 10 + col * (16 * S + 110), y + row * (16 * S + 16)
        out.paste(cell_img(sheet, [cx, cy]).resize((16 * S, 16 * S), Image.NEAREST), (x0, y0))
        d.text((x0 + 16 * S + 4, y0 + 18), name, fill=(220, 220, 200))
    y += rows_h + 8
    x, ybot = 10, y
    for title, rows, bare, im in patches:
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        if x + big.width > W - 10:
            x, y = 10, ybot
        d.text((x, y), title, fill=(240, 240, 240))
        out.paste(big, (x, y + 16))
        ybot = max(ybot, y + 16 + big.height + 14)
        x += big.width + 20
        ws = patch_seams(bare, rows)
        over = [w_ for w_ in ws if w_[0] > 20]
        seam_lines.append(f"{title[:44]}...: worst cell-side seam {ws[0][0]:.1f}, {len(over)} above 20")
    y = ybot + 6
    d.text((10, y), "New unique 8x8 tiles in v3 (flips free; everything v1/v2 kept already exists):",
           fill=(240, 240, 200))
    y += 18
    for gname, n in report:
        d.text((20, y), f"{gname}: {n}", fill=(220, 220, 220))
        y += 16
    d.text((20, y), f"TOTAL new: {total}", fill=(255, 255, 160))
    y += 22
    d.text((10, y), "Seams (check.py's measure, target <= 20; terrain only, before the overlays):",
           fill=(240, 240, 200))
    y += 18
    for line in seam_lines:
        d.text((20, y), line, fill=(220, 220, 220))
        y += 16
    out.crop((0, 0, W, y + 10)).save(path)
    return report, total, seam_lines


def main():
    sheet, index = build()
    png = os.path.join(HERE, "dry_country.png")
    sheet.save(png)
    with open(os.path.join(HERE, "dry_country.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)
    report, total, fam = review(sheet, index, os.path.join(MAPGEN, "maps", "00_dry_country_art.png"))
    for gname, ncell, n in report:
        print(f"  {gname:34s} {ncell:3d} cells {n:4d} tiles")
    print(f"  TOTAL unique 8x8 tiles: {total}")
    print("  colours:", fam)
    report, total, seam_lines, plain_seams = review_v2(sheet, index,
                                                       os.path.join(MAPGEN, "maps", "00_dry_country_v2.png"))
    print("v2:")
    for gname, n in report:
        print(f"  {gname:40s} {n:4d} new tiles")
    print(f"  TOTAL new v2 tiles: {total}")
    for line in seam_lines + plain_seams:
        print("  " + line)
    report, total, seam_lines = review_v3(sheet, index, os.path.join(MAPGEN, "maps", "00_dry_country_v3.png"))
    print("v3:")
    for gname, n in report:
        print(f"  {gname:40s} {n:4d} new tiles")
    print(f"  TOTAL new v3 tiles: {total}")
    for line in seam_lines:
        print("  " + line)


if __name__ == "__main__":
    main()

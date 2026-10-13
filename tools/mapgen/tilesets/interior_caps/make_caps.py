"""Own art: the end pieces of the interior wall frames, now that every interior border is plain black (9eb00d1b8f).

usage (from the decomp root): python tools/mapgen/tilesets/interior_caps/make_caps.py
writes, next to this script:
    caps_<set>.png + caps_<set>.json   one sheet per secondary (16 px cells, every cell opaque, bottom layer only)
    sources/<recipe>.<src>.json        the image source to append to tilesets/recipes/<recipe>.json (src "ec"; the
                                       Shelter's pieces are a second source "es" in orleans_hall, so each sheet's
                                       colour groups stay inside one existing palette)
and the review images under tile_review/interior_caps/ (caps_review.png, caps_rooms_mock.png).

Each piece is drawn over the real composed metatile it replaces (render.Tilesets on the built primary + secondary),
in that metatile's own palette, so it adds no colours. check_fit() proves every 8x8 tile of every piece fits one
palette the target tileset already has.

    style        rooms   replaces                   pieces (L and R)
    generic      74      jb:0A8 / jb:0B0 at the     top_L/R  : the wall's top row ends in a framed pilaster
                         bar's two ends             foot_L/R : the pilaster comes down to a plinth where the wall
                                                               meets the floor
    rootkin      8       rk:side at the 4 corners   top_L/R  : a corner post seen end-on (cut log, lashed), outer
                                                               corner rounded off
                                                    foot_L/R : the same post at the bottom corners
    shelter      1       th:44D top and bottom      top / foot (+R): a cornice and a plinth on the cream pillar
    church       1       cw:side top and bottom     top / foot (L/R): a carved wood capital with a gold stud and a
                                                               moulded plinth
    conservatory 1       cv:glass_0 / cv:glass_1 at top0/top1_L/R : the glass roof stops at a white corner post
                         the bar's ends, the two               that carries on down the glass_side mullion
                         bottom corners             foot     : the post's stone footing (both bottom corners)
"""
import json
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, os.path.join(MAPGEN, "tilesets", "arenas"))
sys.path.insert(0, MAPGEN)
from arena_art import Canvas, dump, gba, scale, KEY  # noqa: E402
import render  # noqa: E402

PRIMARY = os.path.join(ROOT, "data/tilesets/primary/orleans_building")
REVIEW = os.path.join(os.path.dirname(ROOT), "tile_review", "interior_caps")

SETS = {
    # set: (secondary dir, recipe, symbol)
    "interior": ("orleans_interior", "orleans_interior", "gTileset_OrleansInterior"),
    "rootkin": ("orleans_rootkin_in", "orleans_rootkin_in", "gTileset_OrleansRootkinIn"),
    "shelter": ("orleans_hall", "orleans_hall", "gTileset_OrleansHall"),
    "church": ("orleans_hall", "orleans_hall", "gTileset_OrleansHall"),
    "conservatory": ("orleans_conservatory", "orleans_conservatory", "gTileset_OrleansConservatory"),
}
SRC_NAME = {k: "es" if k == "shelter" else "ec" for k in SETS}
_TS, _MAP = {}, {}


def ts(sec):
    if sec not in _TS:
        _TS[sec] = render.Tilesets(PRIMARY, os.path.join(ROOT, "data/tilesets/secondary", sec))
        m = json.load(open(os.path.join(MAPGEN, "tilesets", sec + ".mapping.json")))["metatiles"]
        m.update(json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_building.mapping.json")))["metatiles"])
        _MAP[sec] = m
    return _TS[sec]


def mid(sec, name):
    ts(sec)
    return _MAP[sec][name]


def base(sec, name):
    """The composed metatile as an opaque 1x1 Canvas."""
    im = ts(sec).metatile(mid(sec, name)).convert("RGBA")
    cv = Canvas(1, 1)
    cv.im.paste(im, (0, 0))
    cv.p = cv.im.load()
    return cv


BLACK = (0, 0, 0)


class Side:
    """Draw in 'left' coordinates; on the right side x is mirrored (the base art underneath is NOT flipped)."""

    def __init__(self, cv, side):
        self.cv, self.r = cv, side == "R"

    def X(self, x):
        return 15 - x if self.r else x

    def put(self, x, y, c):
        self.cv.put(self.X(x), y, c)

    def h(self, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            self.put(x, y, c)

    def v(self, x, y0, y1, c):
        for y in range(y0, y1 + 1):
            self.put(x, y, c)

    def rect(self, x, y, w, h, c):
        for j in range(y, y + h):
            self.h(x, x + w - 1, j, c)


# ------------------------------------------------------------------ generic (HnS wall, primary palette 4)
G_OUT, G_DK, G_LT, G_LT2 = (120, 120, 120), (80, 80, 104), (224, 232, 240), (208, 216, 224)
G_BAND, G_SH, G_WALL, G_WHI, G_TEAL = (168, 168, 160), (104, 104, 104), (168, 192, 176), (192, 216, 200), (88, 184, 168)


def generic_top(side):
    cv = base("orleans_interior", "jb:0A8")
    s = Side(cv, side)
    # the pilaster (x0..4) runs down from the top band; the band's lower rows stop against it
    s.v(0, 0, 15, G_DK)
    s.v(1, 1, 15, G_LT)
    s.v(2, 1, 15, G_LT2)
    s.v(3, 5, 15, G_BAND)
    s.v(4, 8, 15, G_OUT)        # its shadow on the wall face
    s.h(1, 15, 0, G_OUT)        # the top outline runs over it
    s.put(0, 0, G_DK)
    s.h(1, 3, 1, G_LT)          # the band's light rows merge into the pilaster: one frame
    s.put(3, 7, G_OUT)
    s.put(4, 7, G_OUT)
    return cv


def generic_foot(side):
    cv = base("orleans_interior", "jb:0B0")
    s = Side(cv, side)
    s.v(0, 0, 15, G_DK)
    s.v(1, 0, 7, G_LT)
    s.v(2, 0, 7, G_LT2)
    s.v(3, 0, 7, G_BAND)
    s.v(4, 0, 7, G_OUT)
    # plinth (one pixel wider than the pilaster) where the wall comes down to the floor
    s.h(1, 5, 8, G_OUT)
    s.rect(1, 9, 4, 4, G_BAND)
    s.v(1, 9, 12, G_LT2)
    s.v(5, 9, 14, G_OUT)
    s.h(1, 4, 13, G_SH)
    s.h(1, 4, 14, G_SH)
    s.h(0, 15, 15, G_OUT)
    s.put(0, 15, G_DK)
    return cv


# ------------------------------------------------------------------ Rootkin (rk:side planks, palette 8)
R_D0, R_P, R_PL = (48, 40, 32), (88, 72, 56), (120, 104, 80)
R_BR, R_T1, R_T2 = (144, 120, 64), (184, 152, 88), (208, 192, 120)
R_C1, R_C2, R_C3 = (192, 160, 120), (200, 168, 104), (208, 184, 136)


def log_end(s, cy):
    """A cut post seen from above: bark ring, light end grain, growth rings, dark outline."""
    cx = 7.5
    for y in range(16):
        for x in range(16):
            d = ((x + 0.5 - (cx + 0.5)) ** 2 + (y + 0.5 - (cy + 0.5)) ** 2) ** 0.5
            if d <= 6.6:
                c = R_D0
                if d <= 5.8:
                    c = R_BR
                if d <= 4.9:
                    c = R_C3 if (x + y) < 2 * cx + 1 else R_C2
                if 2.4 <= d <= 3.2:
                    c = R_C1
                if d <= 1.0:
                    c = R_C1
                s.put(x, y, c)
    # a crack in the grain
    s.put(8, int(cy) - 1, R_BR)
    s.put(9, int(cy) - 2, R_BR)


def rope(s, y):
    """Lashing across the plank run, under or over the post."""
    for x in range(16):
        s.put(x, y, R_T2 if x % 3 == 0 else R_T1)
        s.put(x, y + 1, R_BR if x % 3 == 2 else R_T1)
        s.put(x, y + 2, R_D0)


def rootkin(kind, side):
    cv = base("orleans_rootkin_in", "rk:side")
    s = Side(cv, side)
    if kind == "top":
        rope(s, 13)
        log_end(s, 6.5)
        for (x, y) in ((0, 0), (1, 0), (0, 1)):  # outer corner rounded off into the black
            s.put(x, y, BLACK)
        s.put(2, 0, R_D0)
        s.put(1, 1, R_D0)
        s.put(0, 2, R_D0)
    else:
        rope(s, 0)
        log_end(s, 8.5)
        for (x, y) in ((0, 15), (1, 15), (0, 14)):
            s.put(x, y, BLACK)
        s.put(2, 15, R_D0)
        s.put(1, 14, R_D0)
        s.put(0, 13, R_D0)
    return cv


# ------------------------------------------------------------------ the hall (orleans_hall): Shelter and Church
# orleans_hall is composed with the legacy palette packer, which re-packs the whole tileset if a new colour group
# turns up, and the Church's wood is squeezed (28 colours -> 15). So each hall sheet is drawn in the colours of ONE
# unsqueezed palette cluster the hall already has, and uses enough of them that the greedy merge can only join it
# to that cluster (tested: every existing hall metatile composes identically, caps included):
#   Shelter pieces: all 14 colours of the theater group th:44D comes from (built palette 7): cream and peach,
#                   the ivy greens, the olive of its stone base.
#   Church pieces:  the Shelter-supply wood cluster (built palette 11): a brown ramp, stained-glass blues and reds.
# Shelter pillar (th:44D)
S_OUT, S_PE, S_CR = (120, 120, 120), (232, 160, 136), (240, 232, 200)
S_PE2, S_RD, S_CRM = (208, 128, 104), (176, 88, 64), (216, 208, 136)
S_SL, S_RU, S_OL1, S_OL2 = (80, 80, 104), (152, 72, 40), (176, 168, 96), (152, 144, 80)
S_V1, S_V2, S_V3, S_V4 = (208, 248, 192), (160, 224, 144), (144, 208, 160), (120, 168, 144)

IVY = ["....aa..........",
       "...abba.........",
       "...accd..e......",
       "....dd..abba....",
       ".....e..acc.d...",
       ".....e...dd.....",
       "....aa...e......",
       "...abbd..e......",
       "....cd.........."]


def ivy(s, x0, y0):
    cmap = {"a": S_V3, "b": S_V2, "c": S_V1, "d": S_SL, "e": S_V4}
    for j, row in enumerate(IVY):
        for i, ch in enumerate(row):
            if ch in cmap:
                s.put(x0 + i, y0 + j, cmap[ch])


def shelter(kind, side):
    cv = base("orleans_hall", "th:44D")
    s = Side(cv, side)
    if kind == "top":   # cornice, with ivy trailing off it on the room side
        s.h(0, 15, 0, S_OUT)
        s.h(1, 14, 1, S_CR)
        s.h(1, 14, 2, S_CR)
        s.h(1, 14, 3, S_CRM)
        s.h(1, 14, 4, S_PE)
        s.h(1, 14, 5, S_PE2)
        s.h(0, 15, 6, S_OUT)
        for y in range(1, 6):
            s.put(0, y, S_OUT)
            s.put(15, y, S_OUT)
        for x in (3, 6, 9, 12):  # dentils under the cornice
            s.put(x, 7, S_RD)
        ivy(s, 5, 5)
    else:               # an olive stone plinth
        s.h(2, 13, 9, S_PE)
        s.h(0, 15, 10, S_RU)
        s.h(1, 14, 11, S_CRM)
        s.h(1, 14, 12, S_OL1)
        s.h(1, 14, 13, S_OL1)
        s.h(1, 14, 14, S_OL2)
        s.h(0, 15, 15, S_SL)
        for y in range(11, 15):
            s.put(0, y, S_OUT)
            s.put(15, y, S_OUT)
        s.put(3, 12, S_CRM)
        s.put(9, 13, S_OL2)
        s.put(12, 12, S_CRM)
    return cv


# Church side (cw:side), in the hall's wood cluster (built palette 11)
K0, K1, K2, K3, K4 = (48, 40, 32), (112, 80, 40), (144, 104, 56), (176, 128, 80), (192, 152, 96)
GL_B, GL_LB, GL_R, GL_DR, GL_W = (56, 104, 184), (136, 192, 232), (144, 40, 40), (96, 24, 24), (232, 224, 216)
GL_I = (200, 192, 184)


def church_panel(s, y0, y1):
    """A carved block face: lit left edge, dark right edge, two flutes."""
    for y in range(y0, y1 + 1):
        s.put(0, y, K0)
        s.put(1, y, K3)
        s.h(2, 13, y, K1)
        s.put(14, y, K2)
        s.put(15, y, K0)
        for x in (5, 10):
            s.put(x - 1, y, K2)
            s.put(x, y, K0)


def church(kind, side):
    """Whole-cell carved blocks: the hall's wood cluster has (48,40,32)/(112,80,40) where cw:side has
    (56,40,32)/(96,64,40), so a piece never continues the plain column inside itself; it meets it at a moulding."""
    cv = Canvas(1, 1, K0)
    s = Side(cv, side)
    if kind == "top":   # post head: moulding with a stained-glass boss (the windows' blue and red), carved block
        s.h(0, 15, 0, K2)
        s.h(0, 15, 1, K4)
        s.h(0, 15, 2, K3)
        s.h(0, 15, 3, K2)
        s.h(0, 15, 4, K0)
        s.h(1, 14, 5, K1)
        s.h(0, 15, 6, K0)
        church_panel(s, 7, 12)
        s.h(1, 14, 13, K2)
        s.h(0, 15, 14, K1)
        s.h(0, 15, 15, K0)
        s.put(0, 0, K0)  # outer corner eased
        for (x, y, c) in ((7, 0, GL_B), (8, 0, GL_B), (6, 1, GL_B), (7, 1, GL_W), (8, 1, GL_I), (9, 1, GL_B),
                          (6, 2, GL_B), (7, 2, GL_R), (8, 2, GL_DR), (9, 2, GL_B), (7, 3, GL_B), (8, 3, GL_B),
                          (5, 1, K0), (10, 1, K0), (5, 2, K0), (10, 2, K0), (6, 0, K0), (9, 0, K0),
                          (6, 3, K0), (9, 3, K0), (7, 4, K0), (8, 4, K0)):
            cv.put(x, y, c)
    else:               # base: collar, carved block, stepped plinth
        s.h(0, 15, 0, K0)
        s.h(1, 14, 1, K3)
        s.h(0, 15, 2, K1)
        s.h(0, 15, 3, K0)
        church_panel(s, 4, 8)
        s.h(0, 15, 9, K0)
        s.h(0, 15, 10, K1)
        s.h(0, 15, 11, K2)
        s.h(0, 15, 12, K4)
        s.h(0, 15, 13, K3)
        s.h(0, 15, 14, K2)
        s.h(0, 15, 15, K0)
    return cv


# ------------------------------------------------------------------ Conservatory (cv glass, conservatory palette 6)
C_FR, C_G1 = (240, 240, 232), (176, 184, 176)
C_ST0, C_ST1, C_ST2, C_ST3, C_STD, C_STG = (176, 168, 160), (160, 152, 136), (200, 192, 176), (224, 216, 200), (96, 88, 88), (136, 128, 128)


def splice_cols(a, b, x0, x1):
    """a with columns x0..x1 taken from b."""
    out = a.copy()
    for y in range(16):
        for x in range(x0, x1 + 1):
            out.put(x, y, b.get(x, y))
    return out


def conservatory(kind, side):
    sec = "orleans_conservatory"
    gs = base(sec, "cv:glass_side")
    if kind == "foot":
        cv = gs
        # the corner post's stone footing
        cv.rect(4, 11, 8, 5, C_ST2)
        cv.vline(4, 11, 15, C_STG)
        cv.vline(11, 11, 15, C_STG)
        cv.hline(4, 11, 11, C_ST3)
        cv.hline(5, 10, 12, C_ST3)
        cv.hline(5, 10, 14, C_ST1)
        cv.hline(4, 11, 15, C_STD)
        cv.hline(5, 10, 10, C_G1)
        return cv
    glass = base(sec, "cv:glass_0" if kind == "top0" else "cv:glass_1")
    # outside the post: glass_side's planting; the post itself (x5..10) is glass_side's mullion; inside: the glass
    cv = splice_cols(glass, gs, 0, 10) if side == "L" else splice_cols(glass, gs, 5, 15)
    if kind == "top0":  # the post's cap at the roof line
        cv.hline(4, 11, 0, C_G1)
        cv.hline(4, 11, 1, C_FR)
        cv.hline(4, 11, 2, C_FR)
        cv.hline(4, 11, 3, C_G1)
        cv.put(4, 0, C_ST0)
        cv.put(11, 0, C_ST0)
        # the roof's cross bar (y8) and frame meet the post
        if side == "L":
            cv.hline(11, 15, 8, C_FR)
        else:
            cv.hline(0, 4, 8, C_FR)
    else:               # glass_1: its sill (y13..15) runs into the post
        if side == "L":
            cv.hline(11, 15, 13, glass.get(12, 13))
            cv.hline(11, 15, 14, C_FR)
            cv.hline(11, 15, 15, C_FR)
        else:
            cv.hline(0, 4, 13, glass.get(3, 13))
            cv.hline(0, 4, 14, C_FR)
            cv.hline(0, 4, 15, C_FR)
    return cv


# ------------------------------------------------------------------ the pieces
def flip(cv):
    return cv.copy().flip_x()


def pieces():
    P = {}
    gl, gfl = generic_top("L"), generic_foot("L")
    P["interior"] = [
        ("gen_top_L", gl, "jb:0A8", "wall top row, left end (x=0, y=0)"),
        ("gen_top_R", flip(gl), "jb:0A8", "wall top row, right end (x=W-1, y=0)"),
        ("gen_foot_L", gfl, "jb:0B0", "wall lower row, left end: the pilaster's plinth at the floor (x=0, y=1)"),
        ("gen_foot_R", flip(gfl), "jb:0B0", "wall lower row, right end (x=W-1, y=1)"),
    ]
    P["rootkin"] = [
        ("rk_top_L", rootkin("top", "L"), "rk:side", "frame's top-left corner (x=0, y=0)"),
        ("rk_top_R", rootkin("top", "R"), "rk:side", "frame's top-right corner (x=W-1, y=0)"),
        ("rk_foot_L", rootkin("foot", "L"), "rk:side", "frame's bottom-left corner (x=0, y=H-1)"),
        ("rk_foot_R", rootkin("foot", "R"), "rk:side", "frame's bottom-right corner (x=W-1, y=H-1)"),
    ]
    st, sf = shelter("top", "L"), shelter("foot", "L")
    P["shelter"] = [
        ("sh_top_L", st, "th:44D", "Shelter pillar, top (x=0, y=0)"),
        ("sh_top_R", flip(st), "th:44D", "Shelter pillar, top (x=W-1, y=0)"),
        ("sh_foot_L", sf, "th:44D", "Shelter pillar, last cell above the black bottom row (x=0)"),
        ("sh_foot_R", flip(sf), "th:44D", "Shelter pillar, foot (x=W-1)"),
    ]
    P["church"] = [
        ("ch_top_L", church("top", "L"), "cw:side", "Church side, top (x=0, y=0)"),
        ("ch_top_R", church("top", "R"), "cw:side", "Church side, top (x=W-1, y=0)"),
        ("ch_foot_L", church("foot", "L"), "cw:side", "Church side, last cell above the black bottom row (x=0)"),
        ("ch_foot_R", church("foot", "R"), "cw:side", "Church side, foot (x=W-1)"),
    ]
    P["conservatory"] = [
        ("cv_top0_L", conservatory("top0", "L"), "cv:glass_0", "glass roof row 0, left end (x=0, y=0)"),
        ("cv_top0_R", conservatory("top0", "R"), "cv:glass_0", "glass roof row 0, right end (x=W-1, y=0)"),
        ("cv_top1_L", conservatory("top1", "L"), "cv:glass_1", "glass roof row 1, left end (x=0, y=1)"),
        ("cv_top1_R", conservatory("top1", "R"), "cv:glass_1", "glass roof row 1, right end (x=W-1, y=1)"),
        ("cv_foot", conservatory("foot", "L"), "cv:glass_side", "both bottom corners (x=0 and x=W-1, y=H-1)"),
    ]
    return P


# ------------------------------------------------------------------ palette fit
def tiles8(im):
    px = im.load()
    for ty in range(0, im.height, 8):
        for tx in range(0, im.width, 8):
            yield (tx // 8, ty // 8), {gba(px[tx + i, ty + j][:3]) for j in range(8) for i in range(8)}


def check_fit(sec, items):
    """Each 8x8 tile's colours inside one existing palette (primary 0-5 or the secondary's 6-12; black = index 0)."""
    t = ts(sec)
    pals = [set(gba(c) for c in p[1:]) | {BLACK} for p in t.pals[:13]]
    out = {}
    for name, cv, *_ in items:
        fits = []
        for q, cols in tiles8(cv.im.convert("RGB")):
            ok = [i for i, p in enumerate(pals) if cols <= p]
            if not ok:
                raise SystemExit(f"{name} tile {q}: colours {sorted(cols - set().union(*pals))} fit no palette of {sec}")
            fits.append(ok[0])
        out[name] = fits
    return out


# ------------------------------------------------------------------ writing
def write_set(key, items):
    sec, recipe, symbol = SETS[key]
    sheet = Image.new("RGB", (8 * 16, ((len(items) + 7) // 8) * 16), KEY)
    mts, meta = [], {}
    for i, (name, cv, replaces, where) in enumerate(items):
        x, y = i % 8, i // 8
        sheet.paste(cv.im.convert("RGB"), (x * 16, y * 16))
        mts.append({"id": name, "bottom": [x, y]})
        meta[name] = {"x": x, "y": y, "replaces": replaces, "metatile": f"{SRC_NAME[key]}:{name}", "where": where}
    png = f"caps_{key}.png"
    sheet.save(os.path.join(HERE, png))
    fit = check_fit(sec, items)
    for n in meta:
        meta[n]["palettes"] = fit[n]
    dump(os.path.join(HERE, f"caps_{key}.json"), {
        "_comment": f"Interior wall end pieces for {symbol} (own art, make_caps.py). Each piece is a plain bottom-layer "
                    f"cell (layer type normal, behaviour normal, blocks like the cell it replaces). 'palettes' = the "
                    f"existing palette slot each 8x8 tile fits (no new colours).",
        "png": png, "tileset": symbol, "pieces": meta})
    os.makedirs(os.path.join(HERE, "sources"), exist_ok=True)
    dump(os.path.join(HERE, "sources", f"{recipe}.{SRC_NAME[key]}.json"), {
        "_comment": f"Append this object to the 'sources' list of tools/mapgen/tilesets/recipes/{recipe}.json, then "
                    f"compose that recipe; the pieces land as {SRC_NAME[key]}:<id> in {recipe}.mapping.json.",
        "name": SRC_NAME[key], "type": "image", "image": f"tools/mapgen/tilesets/interior_caps/{png}",
        "transparent": [[255, 0, 255]], "group_rule": "fewest", "metatiles": mts})
    return fit


# ------------------------------------------------------------------ mock: rooms with the caps placed
LAYOUTS = None


def layout(name):
    global LAYOUTS
    if LAYOUTS is None:
        LAYOUTS = {l["name"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"]
                   if "name" in l}
    l = LAYOUTS[name + "_Layout"]
    w, h = l["width"], l["height"]
    d = open(os.path.join(ROOT, l["blockdata_filepath"]), "rb").read()
    g = [[struct.unpack_from("<H", d, 2 * (y * w + x))[0] & 0x3FF for x in range(w)] for y in range(h)]
    return g, l["secondary_tileset"]


SEC_OF = {"gTileset_OrleansInterior": "orleans_interior", "gTileset_OrleansHall": "orleans_hall",
          "gTileset_OrleansRootkinIn": "orleans_rootkin_in", "gTileset_OrleansConservatory": "orleans_conservatory"}


def placements(g, sec):
    """The rule a layout agent would code into build_interior (reference implementation for the mocks)."""
    H, W = len(g), len(g[0])
    out = {}

    black = {mid(sec, "jb:000"), mid(sec, "jb:008")}

    def ends_of_run(y, ident, left, right):
        # an end is a wall cell whose neighbour is off the map or black (not a machine or shelf on the wall)
        for x in range(W):
            if g[y][x] != ident:
                continue
            if x == 0 or g[y][x - 1] in black:
                out[(x, y)] = left
            elif x == W - 1 or g[y][x + 1] in black:
                out[(x, y)] = right

    def column(ident, top, foot, x, side):
        ys = [y for y in range(H) if g[y][x] == ident]
        if ys:
            out[(x, min(ys))] = f"{top}_{side}"
            out[(x, max(ys))] = f"{foot}_{side}"

    if sec == "orleans_interior" and g[0][0] == mid(sec, "jb:0A8"):
        ends_of_run(0, mid(sec, "jb:0A8"), "gen_top_L", "gen_top_R")
        ends_of_run(1, mid(sec, "jb:0B0"), "gen_foot_L", "gen_foot_R")
    elif sec == "orleans_rootkin_in":
        s = mid(sec, "rk:side")
        for x, sd in ((0, "L"), (W - 1, "R")):
            column(s, "rk_top", "rk_foot", x, sd)
    elif sec == "orleans_hall":
        for name, pre in (("th:44D", "sh"), ("cw:side", "ch")):
            s = mid(sec, name)
            if g[0][0] == s:
                for x, sd in ((0, "L"), (W - 1, "R")):
                    column(s, pre + "_top", pre + "_foot", x, sd)
    elif sec == "orleans_conservatory":
        out[(0, 0)], out[(W - 1, 0)] = "cv_top0_L", "cv_top0_R"
        out[(0, 1)], out[(W - 1, 1)] = "cv_top1_L", "cv_top1_R"
        out[(0, H - 1)] = out[(W - 1, H - 1)] = "cv_foot"
    return out


def room_image(name, P, caps=True, k=3):
    g, sym = layout(name)
    sec = SEC_OF[sym]
    t = ts(sec)
    byname = {n: cv for items in P.values() for n, cv, *_ in items}
    put = placements(g, sec) if caps else {}
    im = Image.new("RGB", (len(g[0]) * 16, len(g) * 16))
    for y, row in enumerate(g):
        for x, v in enumerate(row):
            im.paste(byname[put[(x, y)]].im.convert("RGB") if (x, y) in put else t.metatile(v), (x * 16, y * 16))
    # a black margin all round, as the game draws the border
    m = Image.new("RGB", (im.width + 32, im.height + 32), BLACK)
    m.paste(im, (16, 16))
    return scale(m, k), put


def font(sz):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


BG, FG, DIM = (32, 32, 40), (232, 232, 232), (150, 150, 160)


def mock_rooms(P):
    rooms = ["CampCocodrie_Cabin1", "OldWater_Healer", "IsleMarais_Church"]
    rows = []
    for r in rooms:
        a, _ = room_image(r, P, caps=False)
        b, put = room_image(r, P, caps=True)
        rows.append((r, a, b, put))
    W = max(a.width + b.width for _, a, b, _ in rows) + 60
    H = sum(a.height + 40 for _, a, _, _ in rows) + 50
    out = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(out)
    d.text((20, 12), "Interior wall end pieces: before (left) / after (right), 3x, black border as in game",
           fill=FG, font=font(20))
    y = 50
    for r, a, b, put in rows:
        d.text((20, y), f"{r}   ({len(put)} cells capped)", fill=FG, font=font(16))
        out.paste(a, (20, y + 22))
        out.paste(b, (40 + a.width, y + 22))
        y += a.height + 40
    out.save(os.path.join(REVIEW, "caps_rooms_mock.png"))
    return rows


def corner_crops(name, P, k=4, n=3):
    """The room's four corners (n x n cells each, with the black margin), before and after."""
    out = []
    for caps in (False, True):
        im, _ = room_image(name, P, caps=caps, k=1)
        W, H = im.width, im.height
        c = 16 * n + 16
        crops = [im.crop((0, 0, c, c)), im.crop((W - c, 0, W, c)), im.crop((0, H - c, c, H)), im.crop((W - c, H - c, W, H))]
        row = Image.new("RGB", (4 * c + 3 * 4, c), BG)
        for i, cr in enumerate(crops):
            row.paste(cr, (i * (c + 4), 0))
        out.append(scale(row, k))
    return out


def review(P, fits):
    f16, f13 = font(16), font(13)
    blocks = []
    # 1. the pieces, 6x, each next to the cell it replaces
    for key, items in P.items():
        sec = SETS[key][0]
        cells = []
        for name, cv, replaces, where in items:
            b = scale(base(sec, replaces).im.convert("RGB"), 6)
            a = scale(cv.im.convert("RGB"), 6)
            cells.append((name, replaces, b, a, fits[key][name]))
        blocks.append(("pieces", key, cells))
    samples = [("generic (74 rooms)", "CampCocodrie_Cabin1"), ("Rootkin huts (8)", "OldWater_Healer"),
               ("Isle Marais Shelter", "IsleMarais_Shelter"), ("Isle Marais Church", "IsleMarais_Church"),
               ("Grand Oak Conservatory gym", "GrandOak_Gym")]
    crops = [(lab, r, corner_crops(r, P)) for lab, r in samples]
    W = 1600
    H = 60
    for _, key, cells in blocks:
        H += 30 + ((len(cells) + 3) // 4) * 150
    for _, _, (a, b) in crops:
        H += 40 + a.height + b.height + 10
    out = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(out)
    d.text((20, 14), "Interior wall end pieces  -  pieces at 6x (base cell | new piece), then each style's four "
                     "corners at 4x (top: now, bottom: with the pieces)", fill=FG, font=font(18))
    y = 56
    for _, key, cells in blocks:
        sec, recipe, sym = SETS[key]
        d.text((20, y), f"{sym}  ({len(cells)} metatiles, {len(cells) * 4} tiles at most)", fill=FG, font=f16)
        y += 26
        for i, (name, rep, b, a, fit) in enumerate(cells):
            x = 20 + (i % 4) * 390
            yy = y + (i // 4) * 150
            out.paste(b, (x, yy))
            out.paste(a, (x + 100, yy))
            d.text((x + 204, yy + 4), f"{SRC_NAME[key]}:{name}", fill=FG, font=f13)
            d.text((x + 204, yy + 22), f"replaces {rep}", fill=DIM, font=f13)
            d.text((x + 204, yy + 40), f"palette slot {sorted(set(fit))}", fill=DIM, font=f13)
        y += ((len(cells) + 3) // 4) * 150 + 4
    for lab, r, (a, b) in crops:
        d.text((20, y + 8), f"{lab}: {r}  (corners TL, TR, BL, BR)", fill=FG, font=f16)
        y += 36
        out.paste(a, (20, y))
        y += a.height + 6
        out.paste(b, (20, y))
        y += b.height + 14
    out = out.crop((0, 0, W, y + 10))
    out.save(os.path.join(REVIEW, "caps_review.png"))


def main():
    os.makedirs(REVIEW, exist_ok=True)
    P = pieces()
    fits = {key: write_set(key, items) for key, items in P.items()}
    mock_rooms(P)
    review(P, fits)
    for key, items in P.items():
        print(f"{SETS[key][2]}: {len(items)} pieces; palette slots used {sorted({s for v in fits[key].values() for s in v})}")


if __name__ == "__main__":
    main()

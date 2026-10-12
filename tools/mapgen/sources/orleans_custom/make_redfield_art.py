"""Own art for Redfield (gym 7, Cayenne): sugarcane and pepper country by the river levee, a sun-bleached Louisiana
farm town. Everything is drawn here in Python (no source tiles), as overlays: magenta is transparent, so each piece
sits on the dry-country sand (make_dry_country.py) or whatever terrain the builder finds beneath (road, water).

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_redfield_art.py
writes
    sources/orleans_custom/redfield.png           the piece sheet (16 px cells, magenta = clear)
    sources/orleans_custom/redfield.json          {"pieces": {name: {x, y, w, h, doors, passable, empty, comment}}}
                                                  (make_camp_art.py's format; redfield_tileset.py makes the prefabs)
    sources/orleans_custom/redfield_preview.png   the sheet on the dry sand, 3x
    maps/00_redfield_art.png                      the review sheet: every piece at 3x on the sand, a test patch of the
                                                  town at 3x, the unique 8x8 tile count (flips free)

Pieces (names, sizes, doors and walk cells exactly as art_requests/redfield.md asks):
    sugar_mill 7x8          Cayenne's gym: a front-gabled boiling house (tin roof in perspective, a louvred monitor
                            along the ridge letting off steam, the painted sun sign on the board gable, barred arched
                            windows, the big double door on steps), the brick chimney with iron bands against its west
                            corner (the tallest thing in town), the crushing house lean-to on the east (press wheel and
                            rollers in the open bay, cut cane stacked at its foot)
    ritas_office 5x4        whitewashed clapboard office, red tin roof, lit window, a ledger signboard
    shotgun_a/b/c/d 3x6     front-gabled shotgun houses: long tin roof receding north, a gable end over a covered
                            porch, one door and one window, brick piers; blue / mint / ochre / rose clapboard, the
                            same roof, porch, piers and steps (their tiles are shared)
    bottling_works 9x6      red brick, saw-tooth tin roof, the brick stack (the mill's own tiles), a giant pepper-sauce
                            bottle sign on the roof, barred arched windows, a loading dock and a steam pipe
    great_sundial 8x6       an octagonal plaza of small pale pavers in a stone kerb with a sun-ray inlay; a big round
                            stone dial face in a brass ring with hour bars, flat and walkable; a brass gnomon fin in 3/4
                            view (the only blocking part, inside cols 3-4 rows 0-3) and its long shadow on the face
    yard_h/v/nw/ne/sw/se    the mill yard fence (cell based: a post in each cell, rails out to the sides it joins,
                            a steel cane-knife edge along the top rail); yard_gate_l/_r the open gate posts
    sundial 2x2, mirror_ne/nw/se/sw 1x2, cane_pile 2x2, cane_pile_b 2x1
    rail_h, rail_cross, rail_end 1x1; cane_truck 3x2 (bottom row = the track under the wheels)
    sauce_vat 2x2, bottle_crates 2x1, ferry 3x2 (on water, roped to the dock to the north)

Colour families (all GBA-exact, <= 15 each, one per piece):
    MILL   ink, brick reds, tin greys (the lightest doubles as whitewash, smoke and flagstone), weathered wood,
           brass gold, two cane greens, pepper red: everything except the houses' walls
    HOUSE  ink, the tin greys, porch wood, pier brick + one pastel clapboard ramp (two colourways per palette fit)
Tile economy (Redfield's art is about 294 unique 8x8 tiles, flips free): every texture (brick, tin, clapboard, pavers,
rails, cut cane) is one repeating 8 px cell on the piece's own origin (cells are 16 px, so every piece shares the
phase); symmetric parts are drawn on one side and mirrored about a tile line (flipped tiles are free): the mill's
boiling house and bay, the great sundial's four quadrants, the dock, the houses' roofs, posts, piers and fences; the
mill and the bottling works share their stack, arched windows, plinth and door leaf; Rita's office has the houses'
door, eave band and clapboard cell; the four houses share every roof, porch, pier and door tile and differ only in
their clapboard.
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

# ---------------------------------------------------------------- MILL family (15)
INK = (56, 40, 40)
BR_D, BR, BR_L = (128, 48, 40), (176, 80, 56), (216, 128, 88)
T_D, T, T_L, T_HI = (96, 96, 104), (144, 144, 144), (192, 184, 168), (240, 232, 208)
W_D, W, W_L = (112, 72, 48), (160, 112, 64), (208, 168, 104)
GOLD = (240, 200, 88)
CN_D, CN = (72, 104, 40), (128, 160, 56)
PEP = (216, 48, 40)
MILL = [INK, BR_D, BR, BR_L, T_D, T, T_L, T_HI, W_D, W, W_L, GOLD, CN_D, CN, PEP]

# ---------------------------------------------------------------- HOUSE walls: faded pastel clapboard (light, mid, lap)
WALLS = {
    "a": ((168, 200, 224), (128, 168, 200), (88, 120, 160)),     # blue
    "b": ((184, 224, 192), (136, 192, 160), (88, 144, 120)),     # mint
    "c": ((240, 208, 128), (216, 168, 88), (160, 120, 56)),      # ochre
    "d": ((240, 184, 176), (216, 144, 136), (160, 96, 96)),      # rose
}


class Art:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.W, self.H = w * 16, h * 16
        self.im = Image.new("RGB", (self.W, self.H), KEY)
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < self.W and 0 <= y < self.H and c is not None:
            self.px[x, y] = c

    def get(self, x, y):
        return self.px[x, y] if 0 <= x < self.W and 0 <= y < self.H else KEY

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.H, y1 + 1)):
            for x in range(max(0, x0), min(self.W, x1 + 1)):
                self.px[x, y] = c

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def frame(self, x0, y0, x1, y1, c):
        self.hline(x0, x1, y0, c)
        self.hline(x0, x1, y1, c)
        self.vline(x0, y0, y1, c)
        self.vline(x1, y0, y1, c)

    def sprite(self, x0, y0, rows, pal):
        """Hand-placed pixels: one string per row; '.' and ' ' leave the pixel alone, other chars via pal."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in ". ":
                    self.put(x0 + i, y0 + j, pal[ch])

    def ellipse(self, cx, cy, rx, ry, c, x0=None, x1=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0 and \
                        (x0 is None or x0 <= x <= x1):
                    self.put(x, y, c)

    def opaque(self, x, y):
        return 0 <= x < self.W and 0 <= y < self.H and self.px[x, y] != KEY

    def outline(self, c=INK, region=None, skip=()):
        """A 1 px outline on clear pixels touching art (4-neighbours); `skip`: colours that don't get one."""
        x0, y0, x1, y1 = region or (0, 0, self.W - 1, self.H - 1)
        add = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.px[x, y] != KEY:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if x0 <= nx <= x1 and y0 <= ny <= y1 and self.opaque(nx, ny) and self.px[nx, ny] not in skip \
                            and self.px[nx, ny] != c:
                        add.append((x, y))
                        break
        for x, y in add:
            self.px[x, y] = c

    def mirror_span(self, x0, x1, y0=0, y1=None):
        """Rows y0..y1: the right half of x0..x1 becomes the mirror of its left half."""
        y1 = self.H - 1 if y1 is None else y1
        for y in range(y0, y1 + 1):
            for i in range((x1 - x0 + 1) // 2):
                self.px[x1 - i, y] = self.px[x0 + i, y]

    def mirror_left(self, y0=0, y1=None):
        self.mirror_span(0, self.W - 1, y0, y1)

    def mirrored(self):
        out = Art(self.w, self.h)
        out.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        out.px = out.im.load()
        return out

    def paste(self, other, ox, oy):
        for y in range(other.H):
            for x in range(other.W):
                c = other.px[x, y]
                if c != KEY:
                    self.put(ox + x, oy + y, c)

    def recolour(self, mapping, region=None):
        x0, y0, x1, y1 = region or (0, 0, self.W - 1, self.H - 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = self.px[x, y]
                if c in mapping:
                    self.px[x, y] = mapping[c]


PIECES = {}   # name -> (Art, meta)


def add(name, art, comment, doors=(), walk=()):
    empty = [[i, j] for j in range(art.h) for i in range(art.w)
             if all(art.px[i * 16 + x, j * 16 + y] == KEY for y in range(16) for x in range(16))]
    PIECES[name] = (art, {"w": art.w, "h": art.h, "comment": comment, "doors": [list(d) for d in doors],
                          "passable": [list(c) for c in walk], "empty": empty})


# ================================================================ shared textures (phase = the piece's origin)
def brick(a, x0, y0, x1, y1, lit=None, shade=None):
    """Red brick in 3 px courses, staggered by 4: dark joints, a lit pixel at each brick's top-left. 8 px periodic.
    lit / shade: columns drawn as the stack's sunlit and shaded edges."""
    for y in range(y0, y1 + 1):
        r = y % 8
        for x in range(x0, x1 + 1):
            k = (x + (4 if r >= 4 else 0)) % 8
            if r in (0, 4) or k == 0:
                c = BR_D
            elif r in (1, 5) and k == 1:
                c = BR_L
            else:
                c = BR
            a.put(x, y, c)
    if lit:
        for y in range(y0, y1 + 1):
            for x in lit:
                a.put(x, y, BR_D if y % 4 == 0 else BR_L)
    if shade:
        for y in range(y0, y1 + 1):
            for x in shade:
                a.put(x, y, BR_D)


def tin(a, x0, y0, x1, y1, ramp=(T_D, T, T_L, T_HI), cap=True, shade=True):
    """Corrugated tin seen from the eave side: vertical ribs every 4 px (groove, lit rib, face, face), a nail every
    8 px, an ink ridge with a lit cap, a dark eave. The last whole 8 px row of a deep roof turns away from the light
    (shading by whole tile rows, so the roof body repeats one tile). 8 px periodic."""
    dd, d, m, l = ramp
    low0 = (y1 // 8) * 8 if (shade and y1 - y0 >= 12) else y1 + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = x % 4
            c = (dd, m, d, d)[k] if y >= low0 else (d, l, m, m)[k]
            if y % 8 == 4 and x % 8 == 2:
                c = dd
            a.put(x, y, c)
    if cap:
        a.hline(x0, x1, y0, INK)
        a.hline(x0, x1, y0 + 1, l)
        a.hline(x0, x1, y0 + 2, m)
    a.hline(x0, x1, y1 - 1, dd)
    a.hline(x0, x1, y1, INK)


def clapboard(a, x0, y0, x1, y1, light, mid, lap):
    for y in range(y0, y1 + 1):
        k = y % 4
        for x in range(x0, x1 + 1):
            a.put(x, y, lap if k == 0 else light if k == 1 else mid)


def plinth(a, x0, x1, y0):
    """A course of dressed stone one tile row high (y0 % 8 == 0): lit top, a joint every 8 px, an ink foot. The mill and
    the bottling works stand on the same tiles."""
    a.rect(x0, y0, x1, y0 + 6, T_L)
    a.hline(x0, x1, y0, T_HI)
    a.hline(x0, x1, y0 + 6, T)
    for x in range(x0, x1 + 1):
        if x % 8 == 3:
            a.vline(x, y0 + 1, y0 + 5, T)
    a.hline(x0, x1, y0 + 7, INK)


def boards(a, x0, y0, x1, y1, ramp=(W_D, W, W_L)):
    """Vertical weathered boards, 4 px wide: a dark seam, a lit edge, the face, a nail every 8 px."""
    d, m, l = ramp
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = x % 4
            c = d if k == 0 else l if k == 1 else m
            if k == 2 and y % 8 == 5:
                c = d
            a.put(x, y, c)


# ================================================================ the brick stack (mill and bottling works)
SMOKE = [(5, 6, 2.8, 2.2), (10, 4, 3.4, 2.6), (17, 3, 3.2, 2.3), (24, 2, 2.6, 1.8)]


def stack(a, x, bottom, top=8):
    """A brick stack filling two whole tiles (x % 8 == 0, x..x+15), so the mill's and the bottling works' stacks are
    the same tiles and never mix with a roof behind them: a stone cap with soot at the lip (y top..top+6), an iron
    band below it, the sunlit left edge and the shaded right; smoke rising in the 8 px row above, drifting east."""
    brick(a, x + 1, top + 7, x + 14, bottom, lit=(x + 1, x + 2), shade=(x + 13, x + 14))
    a.vline(x, top + 7, bottom, INK)
    a.vline(x + 15, top + 7, bottom, INK)
    a.sprite(x, top, ["IIIIIIIIIIIIIIII",
                      "IHHHHHHHHHHHHHLI",
                      "ILLLLLLLLLLLLLTI",
                      "IIIIIIIIIIIIIIII",
                      "IBIKKKKKKKKKKIDI",
                      "IBDDDDDDDDDDDDDI",
                      "IBBRRRRRRRRRRDDI"],
             {"I": INK, "H": T_HI, "L": T_L, "T": T, "D": BR_D, "K": INK, "B": BR_L, "R": BR})
    for y, c in ((top + 13, INK), (top + 14, T), (top + 15, INK)):
        a.hline(x + 1, x + 14, y, c)
    a.put(x + 1, top + 14, T_L)
    a.put(x + 2, top + 14, T_L)
    for cx, cy, rx, ry in SMOKE:
        a.ellipse(x + cx, cy, rx + 1, ry + 1, T_L)
    for cx, cy, rx, ry in SMOKE:
        a.ellipse(x + cx - 0.6, cy - 0.6, rx, ry, T_HI)


# ================================================================ A. buildings
def arch_window(a, x, y):
    """A tall arched window 13 px wide, 18 tall: a lit brick arch, glazing bars and iron bars, furnace light inside
    (gold above, brick-red below). The mill's and the bottling works' windows (the same tiles)."""
    rows = ["...IIIIIII...",
            ".IIBBBBBBBII.",
            "IBBIIIIIIIBBI",
            "IBIHDgIgDgIBI",
            "IBIgDgIgDgIBI",
            "IBIgDgIgDgIBI",
            "IBIIIIIIIIIBI",
            "IBIgDgIgDgIBI",
            "IBIgDgIgDlIBI",
            "IBIgDgIgDlIBI",
            "IBIIIIIIIIIBI",
            "IBIlDlIlDlIBI",
            "IBIlDlIlDrIBI",
            "IBIlDlIlDrIBI",
            "IBIlDlIrDrIBI",
            "IBIIIIIIIIIBI",
            "ITTTTTTTTTTTI",
            "IIIIIIIIIIIII"]
    a.sprite(x, y, rows, {"I": INK, "B": BR_L, "g": GOLD, "H": T_HI, "l": BR_L, "r": BR, "T": T_L, "D": T_D})


def mill_door_leaf(a, x, y, latch=False):
    """The left leaf of the mill's plank double door, one tile column (x % 8 == 0) from y (the arch row) down four
    tile rows: a brick arch, the frame, planks, iron straps. Its flip is the right leaf, so a 16 px double door (the
    bottling works') costs no more tiles than the mill's own."""
    a.sprite(x, y, ["......II",
                    "...IIIBB",
                    ".IIBBBII",
                    "IBBIIIWW"], {"I": INK, "B": BR_L, "W": W_L})
    for yy in range(y + 2, y + 36):
        a.put(x, yy, INK)
        a.put(x + 1, yy, BR_L)
        a.put(x + 2, yy, INK)
    boards(a, x + 3, y + 4, x + 7, y + 35)
    for sy in (y + 12, y + 28):               # iron straps
        a.hline(x + 3, x + 7, sy, T_D)
        a.hline(x + 3, x + 7, sy + 1, INK)
        a.put(x + 4, sy, T_L)


def sugar_mill():
    """Cayenne's gym, 7x8, the tallest thing in Redfield, filling its footprint. Built from whole repeating tiles:
    - the boiling house, front-gabled and mirrored about the door's middle (x 56): one corrugated-tin cell repeated
      over both roof slopes (only the ridge line and the bargeboards differ), a louvred monitor along the ridge letting
      off steam, timber bargeboards over a board gable with the gym's painted sun sign, a timber wall plate, one brick
      cell, barred arched windows (the bottling works' tiles), the big plank double door under brick arches, steps;
    - the chimney against the west corner: the bottling works' stack (cap, iron bands, shaft: the same tiles) with two
      more bands, on a mirrored plinth with the furnace's fire door glowing;
    - the crushing house, a tin lean-to on the east whose open bay is mirrored about its middle (x 104): the geared
      press wheel over three rollers, cut cane stacked at its foot. MILL."""
    a = Art(7, 8)
    CX = 56

    def g(x):
        """The bargeboard's top (y) at column x: the gable's apex at the ridge (y 44), the eaves at y 60."""
        u = x - 22 if x < CX else 89 - x
        return 60 - u // 2

    # ---- the boiling house, left half (x 22..55), mirrored about x 56
    for x in range(22, CX):                    # the roof: one corrugated cell, ribs running down the slope
        for y in range(24, g(x)):
            a.put(x, y, (T, T_HI, T_L, T_L)[y % 4])
    a.hline(22, CX - 1, 23, INK)
    for x in range(44, CX):                    # the monitor: louvred sides, the same tin on top, a louvred front
        for y in range(18, 46):
            if x in (44, 45):
                c = INK if y % 2 == 0 else T_D
                if y < 22:
                    continue
            else:
                c = (T, T_HI, T_L, T_L)[y % 4]
            a.put(x, y, c)
    a.hline(46, CX - 1, 17, INK)
    a.vline(46, 17, 21, INK)
    a.vline(43, 21, 45, INK)
    for x in range(44, CX):
        top = 40 - (x - 44) // 3
        for y in range(top, 46):
            a.put(x, y, INK if y in (top, 45) else T_HI if y == top + 1 else (INK if y % 2 else T_D))
    for x in range(22, CX):                    # bargeboards over a board gable
        gy = g(x)
        for y in range(gy + 4, 70):
            if x >= 24:
                k = x % 4
                a.put(x, y, W_D if k == 0 else W_L if k == 1 else W)
        for i, c in enumerate((INK, W_L, W, INK)):
            a.put(x, gy + i, c)
    for y in range(52, 68):                    # the painted sun sign (centred on the mirror line)
        for x in range(48, CX):
            d = math.hypot(x + 0.5 - CX, y + 0.5 - 60)
            if d <= 8.0:
                c = INK if d > 7.2 else BR if d > 6.2 else T_HI
                ang = math.degrees(math.atan2(y + 0.5 - 60, x + 0.5 - CX)) % 45
                if d <= 3.2:
                    c = GOLD
                elif d <= 5.6 and (ang < 10 or ang > 35):
                    c = GOLD if d < 4.8 else BR_L
                a.put(x, y, c)
    a.hline(22, CX - 1, 70, INK)               # the timber wall plate
    a.hline(22, CX - 1, 71, W_L)
    a.hline(22, CX - 1, 72, W)
    a.hline(22, CX - 1, 73, W_D)
    brick(a, 24, 74, CX - 1, 111)
    arch_window(a, 26, 80)
    mill_door_leaf(a, 40, 80)                 # the left leaf: the frame column, then planks to the middle
    for y, c in ((80, INK), (81, BR_L), (82, INK), (83, W_L)):
        a.hline(48, CX - 1, y, c)
    boards(a, 48, 84, CX - 1, 115)
    for sy in (92, 108):
        a.hline(48, CX - 1, sy, T_D)
        a.hline(48, CX - 1, sy + 1, INK)
    a.vline(CX - 1, 84, 115, INK)             # where the leaves meet
    plinth(a, 24, 39, 112)
    for y, row in zip(range(116, 124), ["IIIIIIIIIIIIIIII", "IHHHHHHHHHHHHHHH", "ILLLLLLLLLLLLLLL",
                                        "IIIIIIIIIIIIIIII", "IHHHHHHHHHHHHHHH", "ILLLLLLLLLLLLLLL",
                                        "ITTTTTTTTTTTTTTT", "IIIIIIIIIIIIIIII"]):
        a.sprite(40, y, [row], {"I": INK, "H": T_HI, "L": T_L, "T": T})
    a.mirror_span(22, 89, 16, 127)
    # steam off the monitor, drifting east
    for cx, cy, rx, ry in ((58.5, 13.0, 1.6, 1.4), (61.0, 10.8, 2.0, 1.7)):     # steam (inside one tile)
        a.ellipse(cx, cy, rx + 1, ry + 1, T_L)
    for cx, cy, rx, ry in ((58.5, 13.0, 1.6, 1.4), (61.0, 10.8, 2.0, 1.7)):
        a.ellipse(cx - 0.6, cy - 0.6, rx, ry, T_HI)
    # ---- the crushing house (x 88..111): a tin lean-to, the open bay mirrored about x 104
    tin(a, 88, 32, 111, 71, shade=False)
    a.vline(111, 32, 71, INK)
    for y in range(72, 120):
        for x in range(88, 104):
            c = W_D                               # the back wall in the shade of the bay
            if y in (72, 73, 74, 75):
                c = (W_L, W, W_D, INK)[y - 72]     # the beam
            elif x % 8 in (0, 7):
                c = INK                           # board seams
            a.put(x, y, c)
    cx, cy = 104.0, 88.0                       # the press wheel: geared rim lit on top, six spokes, the hub
    for y in range(78, 99):
        for x in range(96, 104):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 6.2 <= d <= 8.2:
                a.put(x, y, INK if d > 7.6 or d < 6.7 else (T_HI if y + 0.5 < cy - 3 else T_L if y + 0.5 < cy else T))
            elif d < 6.2:
                ang = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) % 60
                a.put(x, y, T_L if 24 <= ang <= 36 and d > 1.8 else INK if d > 5.6 else W_D)
    for ang in range(0, 360, 30):
        r = math.radians(ang)
        x, y = int(math.floor(cx + math.cos(r) * 8.8)), int(math.floor(cy + math.sin(r) * 8.8))
        if 96 <= x < 104:
            a.put(x, y, INK)
    a.rect(102, 86, 103, 89, INK)
    a.put(103, 87, T_HI)
    a.rect(96, 99, 103, 111, INK)               # the roller frame, the rollers
    a.rect(97, 100, 103, 110, T_D)
    for rx, ry in ((100.0, 106.5), (104.0, 102.5)):
        a.ellipse(rx, ry, 3.0, 3.0, INK, x0=96, x1=103)
        a.ellipse(rx, ry, 2.1, 2.1, T, x0=96, x1=103)
        a.put(int(rx) - 1, int(ry) - 1, T_HI)
    for y in range(72, 120):                   # mirror the bay about x 104
        for x in range(104, 112):
            a.px[x, y] = a.px[207 - x, y]
    # cut cane stacked at its foot
    cane_stalks(a, 88, 111, 114, 121, ends=False)
    a.hline(88, 111, 113, INK)
    a.hline(88, 111, 122, INK)
    # ---- the chimney against the west corner (the bottling works' stack) with two more iron bands, on a plinth
    stack(a, 8, 103)
    for by in (61, 85):
        for y, c in ((by, INK), (by + 1, T), (by + 2, INK)):
            a.hline(9, 22, y, c)
        a.put(9, by + 1, T_L)
        a.put(10, by + 1, T_L)
    a.rect(0, 104, 31, 119, INK)
    brick(a, 1, 106, 15, 118)
    a.hline(1, 15, 105, T_L)
    a.sprite(10, 107, ["IIIIII",
                       "ITTTTT",
                       "ITIIII",
                       "ITIPGG",
                       "ITIGGH",
                       "ITIGHH",
                       "ITIIII",
                       "ITTTTT",
                       "IIIIII"], {"I": INK, "T": T_D, "P": PEP, "G": GOLD, "H": T_HI})
    a.mirror_span(0, 31, 104, 119)
    return a


def ritas_office():
    """Rita's office in the mill yard, 5x4, door (1,3): a red corrugated tin roof with a stovepipe, whitewashed
    clapboard (the same cell as the shotgun houses' lit roof slope), the shotgun houses' plank door, a lit window, and a
    ledger signboard on a bracket. The roof's corrugation is symmetric within each tile and the corner boards match,
    so the east end is the west end's flip. MILL."""
    a = Art(5, 4)
    for y in range(8, 32):                     # the red tin roof: 2 px ribs, a cap, an eave
        for x in range(80):
            k = x % 4
            c = (BR_D, BR_L, BR_L, BR_D)[k] if y < 24 else (BR_D, BR, BR, BR_D)[k]
            a.put(x, y, c)
    a.hline(0, 79, 8, INK)
    a.hline(0, 79, 9, T_HI)
    a.hline(0, 79, 10, BR_L)
    a.hline(0, 79, 30, BR_D)
    a.hline(0, 79, 31, INK)
    a.vline(0, 8, 31, INK)
    a.vline(79, 8, 31, INK)
    a.sprite(56, 0, [".IIIIII.",          # the stovepipe (inside one tile column)
                     "IITTTTII",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".ILTTDI.",
                     ".IIIIII.",
                     ".IDDDDI.",
                     "..IIII.."], {"I": INK, "T": T, "L": T_L, "D": T_D})
    # the walls: the whitewash clapboard cell, corner boards, a plinth
    for y in range(40, 60):
        for x in range(1, 79):
            a.put(x, y, (T, T_HI, T_L, T_L)[y % 4])
    a.hline(1, 78, 32, T_HI)                  # the fascia board and the shade under the eave (the houses' band)
    a.hline(1, 78, 33, T_L)
    a.hline(0, 79, 34, INK)
    a.rect(2, 35, 77, 39, T_D)
    for x in (1, 78):
        a.vline(x, 34, 63, INK)
    for x in (2, 77):
        a.vline(x, 40, 59, T_HI)
    a.rect(2, 60, 77, 62, T_D)
    a.hline(2, 77, 60, T)
    a.hline(1, 78, 63, INK)
    house_door(a, 16, 40)                       # the shotgun houses' door
    a.sprite(40, 40, ["IIIIIIIIIIIIIIII",     # the lit window (x 40..55, y 40..54)
                      "IHHHHHHHHHHHHHHI",
                      "IHIIIIIIIIIIIIDI",
                      "IHIHGGGIGGGGGIDI",
                      "IHIGHGGIGGGGGIDI",
                      "IHIGGGGIGGGGGIDI",
                      "IHIGGGGIGGGGGIDI",
                      "IHIIIIIIIIIIIIDI",
                      "IHIGGGGIGGGGLIDI",
                      "IHIGGGGIGGGLLIDI",
                      "IHIGGGGIGGLLLIDI",
                      "IHIIIIIIIIIIIIDI",
                      "IHHHHHHHHHHHHHHI",
                      "ITTTTTTTTTTTTTTI",
                      "IIIIIIIIIIIIIIII"],
             {"I": INK, "H": T_HI, "D": T, "G": GOLD, "L": BR_L, "T": T_L})
    a.sprite(64, 33, ["IIIIIIII",          # the ledger signboard on its bracket (x 64..71)
                      "..I..I..",
                      "..I..I..",
                      "IIIIIIII",
                      "IWWWWWWI",
                      "IWIIIIWI",
                      "IWHHIHWI",
                      "IWTHITWI",
                      "IWHHIHWI",
                      "IWTHIPWI",
                      "IWIIIPWI",
                      "IWWWWWWI",
                      "IIIIIIII"], {"I": INK, "W": W_L, "H": T_HI, "T": T, "P": PEP})
    return a


def gable_line(x):
    """The bargeboard's top edge (y) at column x: apex at the ridge (y 28), down 1 px every 2 px to y 39 at the eaves."""
    u = x if x < 24 else 47 - x
    return 39 - u // 2


def house_door(a, x, y):
    """The tall plank door with a glass transom (the transom in the 5 px above y), white trim, 16 px wide: the shotgun
    houses' and Rita's office's (the same tiles when y % 8 == 0)."""
    a.sprite(x, y - 5, ["IHIIIIIIIIIIIIHI",
                        "IHITTTTTTTTTTIHI",
                        "IHITLTTTTTLTTIHI",
                        "IHITTTTTTTTTTIHI",
                        "IHIIIIIIIIIIIIHI"], {"I": INK, "H": T_HI, "T": T_D, "L": T_L})
    for k in range(24):
        row = "IHIWWWWWWWWWWIHI"
        if k in (2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20):
            row = "IHIWLDDDDDDLWIHI" if k not in (2, 13) else "IHIWLLLLLLLLWIHI"
        if k in (9, 20):
            row = "IHIWDDDDDDDDWIHI"
        if k == 11:
            row = "IHIWWWWWWWWWHIHI"
        a.sprite(x, y + k, [row], {"I": INK, "H": T_HI, "W": W, "L": W_L, "D": W_D})


def shotgun(key):
    """A shotgun house, 3x6, door (1,5): the long tin roof on a north-south ridge receding north (one corrugated cell
    mirrored over both slopes, the ridge cap down the middle), the gable end in clapboard with a louvred vent under white bargeboards, a tin
    porch roof right across, the front wall in the porch's shade with one tall door (transom over it) and one window,
    white porch posts, the floor on brick piers and plank steps. Everything is common to the four houses except the
    clapboard of the walls and the gable (their colour): the walls fill whole 8 px tiles, so a colourway costs only the
    tiles its colour touches. HOUSE family."""
    WL, WM, WD = WALLS[key]
    a = Art(3, 6)
    # ---- the roof: ribs down each slope, the ridge cap
    for y in range(0, 40):
        for x in range(48):
            k = y % 4
            a.put(x, y, (T, T_HI, T_L, T_L)[k])
    for y in range(1, 40):
        for x, c in ((22, T), (23, T_HI), (24, T_HI), (25, T)):
            a.put(x, y, c)
    a.hline(0, 47, 0, INK)
    a.vline(0, 0, 39, INK)
    a.vline(47, 0, 39, INK)
    a.vline(1, 1, 39, T_HI)
    a.vline(46, 1, 39, T_HI)
    # ---- the gable: shingles below the bargeboards
    for x in range(48):
        g = gable_line(x)
        for y in range(g, 48):
            if y >= g + 3 and 2 <= x <= 45:
                k = y % 4
                a.put(x, y, WD if k == 0 else WL if k == 1 else WM)
            elif y >= g + 3:
                a.put(x, y, KEY)
        a.put(x, g, INK)
        a.put(x, g + 1, T_HI)
        a.put(x, g + 2, INK)
    a.vline(1, 41, 47, INK)
    a.vline(46, 41, 47, INK)
    a.sprite(16, 28, ["......II",
                      ".....IHH",
                      "....IHHH",
                      "...IHHII",
                      "..IHHIDD",
                      ".IHHIIII",
                      "IHHHIDDD",
                      "IHHHIIII",
                      "IHHHIDDD",
                      "IHHHIIII",
                      "IHHHHHHH",
                      "IIIIIIII"], {"I": INK, "H": T_HI, "D": T_D})
    a.mirror_span(0, 47, 26, 47)
    # ---- the porch roof (y 48..55) and the porch's shade (y 56..63)
    tin(a, 0, 48, 47, 55)
    a.vline(0, 48, 55, INK)
    a.vline(47, 48, 55, INK)
    a.hline(1, 46, 56, T_HI)                  # the fascia board
    a.hline(1, 46, 57, T_L)
    a.hline(0, 47, 58, INK)
    a.rect(2, 59, 45, 63, T_D)                # the wall in shade under the porch roof
    a.vline(0, 56, 58, INK)
    a.vline(47, 56, 58, INK)
    # ---- the front wall (y 64..87): clapboard, the door (x 16..31), the window (x 32..42)
    clapboard(a, 2, 64, 45, 87, WL, WM, WD)
    house_door(a, 16, 64)
    a.sprite(32, 59, ["...........",
                      "...........",
                      "...........",
                      "...........",
                      "...........",
                      "IIIIIIIIIII",
                      "IHHHHHHHHHI",
                      "IHTTTHTTTHI",
                      "IHTLTHTTTHI",
                      "IHLTTHTTTHI",
                      "IHTTTHTTTHI",
                      "IHHHHHHHHHI",
                      "IHTTTHTTTHI",
                      "IHTTTHTTLHI",
                      "IHTTTHTLTHI",
                      "IHTTTHTTTHI",
                      "IHTTTHTTTHI",
                      "IHHHHHHHHHI",
                      "ITTTTTTTTTI",
                      "ILLLLLLLLLI",
                      "IIIIIIIIIII"], {"I": INK, "H": T_HI, "T": T_D, "L": T_L})
    for px in (1, 43):                        # the white porch posts
        a.vline(px, 56, 87, INK)
        a.vline(px + 1, 58, 87, T_HI)
        a.vline(px + 2, 58, 87, T_L)
        a.vline(px + 3, 56, 87, INK)
    # ---- the porch floor on brick piers, plank steps to the door (y 88..95)
    a.hline(0, 47, 88, INK)
    a.hline(1, 46, 89, W_L)
    a.hline(1, 46, 90, W)
    a.hline(0, 47, 91, INK)
    a.rect(2, 92, 45, 95, INK)
    for px in (2, 40):
        a.sprite(px, 92, ["DBBBBD", "DBDDBD", "DBBBBD", "IIIIII"], {"D": BR_D, "B": BR, "I": INK})
    a.sprite(16, 88, ["IIIIIIIIIIIIIIII",
                      "IWLLLLLLLLLLLLWI",
                      "IWWWWWWWWWWWWWWI",
                      "IIIIIIIIIIIIIIII",
                      "IWLLLLLLLLLLLLWI",
                      "IWWWWWWWWWWWWWWI",
                      "IDDDDDDDDDDDDDDI",
                      "IIIIIIIIIIIIIIII"], {"I": INK, "W": W, "L": W_L, "D": W_D})
    return a


def bottling_works():
    """The Pepper-Sauce Bottling Works, 9x6, door (2,5): red brick under a saw-tooth tin roof (three teeth, each a
    strip of north-light glazing and a tin slope, 16 px apart so they repeat), the brick stack (the mill's own tiles),
    a giant red pepper-sauce bottle sign standing on the roof, barred arched windows, a plank double door, a stone
    plinth; on the east the steam pipe up the corner with its valve and a puff of steam, and the loading dock under a
    tin canopy. MILL."""
    a = Art(9, 6)
    R = 111                                   # the east end (behind the stack: no saw-tooth tiles there)
    for y0 in (8, 24, 40):
        tin(a, 0, y0 + 4, R, y0 + 15, cap=False)
        a.hline(0, R, y0, INK)
        a.hline(0, R, y0 + 1, T_D)
        a.hline(0, R, y0 + 2, T_D)
        a.hline(0, R, y0 + 3, INK)
        for x in range(0, R + 1, 8):
            a.put(x + 3, y0 + 1, T_L)         # glints on the glazing
            a.vline(x, y0, y0 + 3, INK)       # glazing bars
        for i in range(16):                   # the saw-tooth profile at the ends
            cut = 3 - (i * 4) // 16
            for x in range(0, cut):
                a.put(x, y0 + i, KEY)
            for x in range(R - cut + 1, R + 1):
                a.put(x, y0 + i, KEY)
            a.put(cut, y0 + i, INK)
            a.put(R - cut, y0 + i, INK)
    a.hline(0, R, 8, INK)
    # ---- the stack (the mill's, same phase: body x 98..109), rising off the roof
    stack(a, 96, 55)
    # ---- the bottle sign on the roof: centred on x 56 (left half drawn, mirrored; the glint and the label added)
    half = ["......II",
            ".....IPP",
            ".....IRR",
            "......II",
            "......IH",
            "......IP",
            "......IP",
            "......IP",
            ".....IIP",
            "....IPPP",
            "...IPPPP",
            "..IPPPPP",
            ".IPPPPPP",
            ".IPPPPPP",
            ".IPPIIII",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIHHHH",
            ".IPIIIII",
            ".IPPPPPP",
            ".IPPPPPP",
            ".IPPPPPP",
            ".IRRRRRR",
            "..IIIIII",
            ".IIIIIII",
            ".IDTDDDD",
            ".IIIIIII",
            "..IDI...",
            "..IDI...",
            "..IDIIII",
            "..IDDDDD"]
    a.sprite(48, 0, half, {"I": INK, "P": PEP, "R": BR_D, "H": T_HI, "D": T_D, "T": T_L})
    a.mirror_span(48, 63, 0, 39)
    for y in range(9, 27):                     # the glint down the lit shoulder
        a.put(51 if y > 11 else 53, y, T_HI if y < 14 or y > 22 else BR_L)
    a.sprite(53, 15, ["...cC.", "..cCc.", "...P..", "..PPP.", "..PPP.", "..PPP.", "...P.."],
             {"c": CN_D, "C": CN, "P": PEP})
    # ---- the brick front (x 0..R), the timber plate, windows, the door, the plinth
    a.hline(0, R, 56, INK)
    a.hline(1, R - 1, 57, W_L)
    a.hline(1, R - 1, 58, W)
    a.hline(1, R - 1, 59, W_D)
    brick(a, 1, 60, R - 1, 87)
    a.vline(0, 56, 95, INK)
    a.vline(R, 56, 95, INK)
    plinth(a, 1, R - 1, 88)
    a.hline(0, R, 95, INK)
    for x in (18, 50, 66, 82):                 # the mill's arched windows (the same tiles: same 8 px phase)
        arch_window(a, x, 64)
    # the double door: the mill's left leaf (the same tiles) and its flip
    mill_door_leaf(a, 32, 64)
    for y in range(64, 96):
        for i in range(8):
            a.px[40 + i, y] = a.px[39 - i, y]
    # ---- the steam pipe (x 112..115) up the corner to an elbow, a valve wheel, a puff of steam
    for y in range(24, 88):
        for x, c in ((112, INK), (113, T_HI), (114, T), (115, INK)):
            a.put(x, y, c)
        if y % 8 == 0:
            a.hline(112, 115, y, INK)
            a.put(113, y + 1, T_L)
    a.sprite(112, 20, ["IIIIIIII", "IHHHHTTI", "ITTTTTDI", "IIIIIIII"], {"I": INK, "H": T_HI, "T": T, "D": T_D})
    a.sprite(113, 42, [".III.", "IGGGI", "IGIGI", "IGGGI", ".III."], {"I": INK, "G": GOLD})
    for cx, cy, rx, ry in ((122.5, 13.0, 1.6, 1.4), (125.0, 10.8, 2.0, 1.7)):   # steam (inside one tile)
        a.ellipse(cx, cy, rx + 1, ry + 1, T_L)
    for cx, cy, rx, ry in ((122.5, 13.0, 1.6, 1.4), (125.0, 10.8, 2.0, 1.7)):
        a.ellipse(cx - 0.6, cy - 0.6, rx, ry, T_HI)
    # ---- the loading dock (x 120..143, drawn on the west half and mirrored): a tin canopy on two posts, the open
    # cargo bay, the plank dock with bumpers
    tin(a, 120, 48, 131, 55)
    a.vline(120, 48, 55, INK)
    a.rect(120, 56, 131, 79, INK)
    for y in range(57, 80):
        for x in range(121, 132):
            a.put(x, y, INK if y % 4 == 1 else W_D)
    for x, c in ((120, INK), (121, T_L), (122, T), (123, INK)):
        a.vline(x, 56, 79, c)
    a.hline(120, 131, 80, INK)
    a.hline(120, 131, 81, W_L)
    a.hline(120, 131, 82, W)
    a.hline(120, 131, 83, INK)
    for y in range(84, 95):
        for x in range(120, 132):
            a.put(x, y, W_D if x % 4 == 3 else W_L if x % 4 == 0 else W)
    a.hline(120, 131, 95, INK)
    a.vline(120, 80, 95, INK)
    a.sprite(124, 86, ["IIII", "IDDI", "IDDI", "IDDI", "IIII"], {"I": INK, "D": T_D})
    for y in range(48, 96):
        for x in range(132, 144):
            a.px[x, y] = a.px[263 - x, y]
    return a


def great_sundial():
    """The great sundial, 8x6: a giant dial inlaid in an octagonal plaza, built from one mirrored quadrant.
    - The plaza: pale pavers (one 8 px cell repeated) inside a stone kerb, eight sun rays of brick inlay running from
      the dial's ring out to brass studs at the kerb.
    - The dial face (flat, walkable): a big round stone face in a brass ring filling the middle, hour bars round the
      rim (the cardinal hours long).
    - The top-left quadrant is drawn and mirrored both ways (flipped tiles are free); only the cells under the gnomon
      and its shadow are unique: the gnomon (the only blocking part, inside cols 3-4 rows 0-3) is a triangular brass
      fin standing on the face in 3/4 view, its sunlit edge and thickness, and its long dark shadow across the face
      toward the west. MILL."""
    a = Art(8, 6)
    C = 24
    DX, DY, RX, RY = 64, 48, 42.0, 28.0      # the dial (centred on the quadrant corner)

    def inn(x, y, i):
        x0, y0, x1, y1 = i, i, 127 - i, 95 - i
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return False
        return min(x - x0, x1 - x) + min(y - y0, y1 - y) >= C - i

    def rad(x, y):
        return math.hypot((x + 0.5 - DX) / RX, (y + 0.5 - DY) / RY)

    for y in range(48):                        # the top-left quadrant
        for x in range(64):
            if not inn(x, y, 0):
                continue
            if not inn(x, y, 1):
                c = INK
            elif not inn(x, y, 3):
                c = T if not inn(x, y, 2) else T_L
            elif not inn(x, y, 4):
                c = T
            else:
                r, k = y % 8, x % 8
                c = T_L if (r in (3, 7) or (k == 7 and r < 3) or (k == 3 and r > 3)) else T_HI
                if (k, r) in ((1, 1), (5, 5)):
                    c = T_L                         # the stone's grain
            r = rad(x, y)
            if r <= 1.0:                            # the dial face in its brass ring
                if r > 0.955:
                    c = INK
                elif r > 0.87:
                    c = T_HI if r > 0.935 else GOLD if r > 0.895 else W_L
                elif r > 0.85:
                    c = INK
                else:
                    c = T_L
            elif inn(x, y, 5) and r > 1.06:        # the rays: W, N and the NW diagonal
                if y == DY - 1 or x == DX - 1:
                    c = BR_L
                elif x - y == DX - DY:
                    c = BR_L
                elif x - y == DX - DY + 1:
                    c = BR
            a.put(x, y, c)
    for h in (6, 7, 8, 9):                      # hour bars in the quadrant (the cardinal hours long)
        th = math.radians(h * 30)
        long_ = h % 3 == 0
        for t in range(0, 9 if long_ else 6):
            rr = 0.82 - t * 0.012
            x = int(math.floor(DX + RX * rr * math.cos(th)))
            y = int(math.floor(DY + RY * rr * math.sin(th)))
            if x < 64 and y < 48:
                a.put(x, y, INK)
    for x, y in ((6, DY - 1), (DX - 1, 6), (21, 5)):                    # brass studs at the rays' ends
        a.sprite(x - 1, y - 1, ["IG", "GG"], {"I": INK, "G": GOLD})
    for y in range(48):                        # mirror the quadrant both ways
        for x in range(64):
            c = a.px[x, y]
            a.px[127 - x, y] = c
            a.px[x, 95 - y] = c
            a.px[127 - x, 95 - y] = c
    # the fin's shadow: a long dark line across the face toward the west, inside one tile row (y 40..47)
    for x in range(32, 63):
        t = (62 - x) / 30
        y = 41 + int(round(t * 5))
        a.put(x, y, T_D)
        if x > 46:
            a.put(x, y - 1, T_D)
    # the fin: a brass right triangle, its upright back edge at x 57 (y 6..30), its foot from (57, 30) to the dial's
    # centre (71, 46), its sloping top edge catching the light
    def hyp(y):
        return 57 + (y - 6) * 14 / 40
    for y in range(6, 47):
        x_end = int(hyp(y))
        x_start = 57 if y <= 30 else 57 + (y - 30) * 14 // 16
        for x in range(x_start, x_end + 1):
            c = W_L
            if x >= x_end - 1:
                c = GOLD if y > 8 else T_HI
            elif x == 57 and y <= 30:
                c = W
            a.put(x, y, c)
        a.put(x_end + 1, y, INK)
        a.put(x_start - 1, y, INK)
    a.hline(56, 58, 5, INK)
    for y in range(30, 48):
        a.put(57 + (y - 30) * 14 // 16, y, INK)
    a.put(int(hyp(14)), 14, T_HI)
    a.put(int(hyp(30)), 30, T_HI)
    return a


# ================================================================ B. the mill yard
def fence_rails(a, x0, x1):
    """The fence's horizontal rails between x0..x1: a top rail with a steel cane-knife edge, a lower rail."""
    for x in range(x0, x1 + 1):
        a.put(x, 3, INK)
        a.put(x, 4, T_HI if x % 8 not in (3, 4) else T)     # the steel edge, notched like a row of blades
        a.put(x, 5, T_D)
        a.put(x, 6, W_L)
        a.put(x, 7, W)
        a.put(x, 8, INK)
        a.put(x, 10, INK)
        a.put(x, 11, W_L)
        a.put(x, 12, W_D)
        a.put(x, 13, INK)
        if x % 8 in (3, 4):
            a.put(x, 2, INK)
            a.put(x, 3, T_L)


def fence_vrail(a, y0, y1):
    """The fence's north-south rail seen from above: weathered plank, the steel cane-knife edge down its middle
    (notched every 8 px); symmetric, so the cell's halves are flips of each other."""
    for y in range(y0, y1 + 1):
        edge = T_HI if y % 8 not in (3, 4) else T
        for x, c in ((5, INK), (6, W_L), (7, edge), (8, edge), (9, W_L), (10, INK)):
            a.put(x, y, c)


FENCE_POST = ["..IIII..",
              ".IHHHHI.",
              ".IWLLWI.",
              ".IWLLWI.",
              ".IWDDWI.",
              ".IWLLWI.",
              ".IDDDDI.",
              ".IWLLWI.",
              ".IWLLWI.",
              ".IWDDWI.",
              ".IWLLWI.",
              ".IIIIII."]
FPAL = {"I": INK, "H": T_L, "L": W_L, "W": W, "D": W_D}


def yard_piece(kind):
    """The mill yard fence, one cell: a weathered post in the middle, rails out to the sides it joins (corners are
    cell-based too: nw joins east and south)."""
    a = Art(1, 1)
    west, east, north, south = {"h": (1, 1, 0, 0), "v": (0, 0, 1, 1), "nw": (0, 1, 0, 1), "ne": (1, 0, 0, 1),
                                "sw": (0, 1, 1, 0), "se": (1, 0, 1, 0)}[kind]
    if west:
        fence_rails(a, 0, 5)
    if east:
        fence_rails(a, 10, 15)
    if north:
        fence_vrail(a, 0, 2)
    if south:
        fence_vrail(a, 12, 15)
    a.sprite(4, 2, FENCE_POST, FPAL)
    return a


def yard_gate_l():
    """The west gate post: a tall iron-banded post at the cell's east side with a cap, the fence's rails coming in from
    the west, and the gate leaf folded back flat against them (planks, a Z brace, iron hinge straps)."""
    a = Art(1, 1)
    fence_rails(a, 0, 9)
    # the folded leaf, in front of the rails
    a.rect(0, 2, 9, 14, INK)
    for x in range(0, 9):
        k = x % 3
        for y in range(3, 14):
            a.put(x, y, (W_L, W, W)[k] if k else W_D)
    for t in range(0, 9):
        a.put(8 - t, 4 + t, W_D)
        a.put(8 - t, 5 + t, W_L)
    for y in (4, 11):
        a.hline(0, 9, y, T_D)
        a.put(9, y, INK)
    a.hline(0, 9, 14, INK)
    a.vline(9, 2, 14, INK)
    # the post
    a.sprite(9, 0, ["IIIIIII",
                    "IHHHHHI",
                    "ITTTTTI",
                    "IIIIIII",
                    "ILWWWDI",
                    "IDDDDDI",
                    "ILWWWDI",
                    "ILWWWDI",
                    "ILWWWDI",
                    "IDDDDDI",
                    "ILWWWDI",
                    "ILWWWDI",
                    "ILWWWDI",
                    "IDDDDDI",
                    "ILWWWDI",
                    "IIIIIII"], {"I": INK, "H": T_L, "T": T, "L": W_L, "W": W, "D": T_D})
    return a


def sundial(lit=False):
    """A yard sundial, 2x2: a stone pedestal (stepped base, a column, a capital) under a round brass dial plate with hour
    ticks and a gnomon. Lit (the solved state): a sunbeam strikes the plate and it blazes white-gold; only the plate's
    tiles change. MILL."""
    a = Art(2, 2)
    a.sprite(0, 14, ["......IIIIIIIIII",
                     ".....IHHHHHHHHHH",
                     ".....ILLLLLLLLLL",
                     "......IIIIIIIIII",
                     "........IHLLLLLL",
                     "........IHLLLLLL",
                     "........IHLTLLLL",
                     "........IHLLLLLL",
                     "........IHLLLLLL",
                     "........IHLLLLLL",
                     "......IIHHHHHHHH",
                     ".....IHLLLLLLLLL",
                     "....IHLLLLLLLLLL",
                     "....ITTTTTTTTTTT",
                     "....IIIIIIIIIIII"],
             {"I": INK, "H": T_HI, "L": T_L, "T": T})
    a.mirror_left()
    # the dial plate
    a.ellipse(16, 10, 12, 4.6, INK)
    a.ellipse(16, 10, 11, 3.6, W_L)
    a.ellipse(16, 9.7, 9.4, 2.7, GOLD)
    for x, y in ((8, 9), (11, 7), (14, 7), (18, 7), (21, 7), (24, 9)):
        a.put(x, y, W)
    a.hline(6, 25, 13, W)                      # the plate's thickness
    a.hline(8, 23, 14, INK)
    if lit:
        a.ellipse(16, 9.7, 7.6, 2.4, T_HI, x0=8, x1=23)     # the plate blazing white-gold
        a.ellipse(16, 9.8, 4.5, 1.3, GOLD, x0=8, x1=23)
        for x, y in ((9, 3), (22, 2), (12, 1), (20, 5)):    # sparkles over it
            a.sprite(x - 1, y - 1, [".G.", "GHG", ".G."], {"G": GOLD, "H": T_HI})
    # the gnomon: a brass triangle standing on the plate, its shadow to the west
    a.sprite(15, 1, ["I.......",
                     "IGI.....",
                     "IGWI....",
                     "IGWWI...",
                     "IGWWWI..",
                     "IGWWWWI.",
                     "IGWWWWWI",
                     "IIIIIIII"], {"I": INK, "G": GOLD, "W": W})
    if True:
        for t in range(6):
            a.put(14 - t, 9 + t // 3, W)
            a.put(13 - t, 9 + t // 3, W)
    return a


def mirror_piece(front):
    """A standing brass mirror, 1x2: the disc in a brass ring on a yoke (cell 0), the post on a stone footing (cell
    1). front=True: its glass faces south-east, catching the light (mirror_se; mirror_sw is its flip); False: its
    brass back is to us, the glass turned north-east (mirror_ne; mirror_nw is the flip). MILL."""
    a = Art(1, 2)
    if front:
        a.sprite(2, 3, ["....IIIII....",
                        "...IGGGGGI...",
                        "..IGHHHHLGI..",
                        ".IGHHHHLLTGI.",
                        ".IGHHHLLTTGI.",
                        "IGHHHLLTTTTGI",
                        "IGHHLLTTTTTGI",
                        "IGHLLTTTTTDGI",
                        "IGLLTTTTTDDGI",
                        ".IGLTTTTDDGI.",
                        ".IGTTTTDDDGI.",
                        "..IGTTDDDGI..",
                        "...IGGGGGI...",
                        "....IIIII...."],
                 {"I": INK, "G": GOLD, "H": T_HI, "L": T_L, "T": T, "D": T_D})
    else:
        a.sprite(2, 3, ["....IIIII....",
                        "...IWWWWWI...",
                        "..IWLLLLWHI..",
                        ".IWLWWWWLWHI.",
                        ".IWLWWWWWLHI.",
                        "IWLWWIIIWWLHI",
                        "IWLWWIGIWWLHI",
                        "IWLWWIIIWWLHI",
                        "IWLWWWWWWWLHI",
                        ".IWLWWWWWLHI.",
                        ".IWWLLLLLWHI.",
                        "..IWWWWWWHI..",
                        "...IDDDDDI...",
                        "....IIIII...."],
                 {"I": INK, "W": W, "L": W_L, "H": T_HI, "G": GOLD, "D": W_D})
    # the yoke and pivots
    a.sprite(0, 8, ["II", "GI", "GI", "II"], {"I": INK, "G": GOLD})
    a.sprite(14, 8, ["II", "IG", "IG", "II"], {"I": INK, "G": GOLD})
    a.sprite(0, 12, ["II..............",
                     "GI..............",
                     "GI..............",
                     "GI..............",
                     "GI..............",
                     "GI..............",
                     "WIIIIIIIIIIIIIIW",
                     "IWWWWWWWWWWWWWWI",
                     "..IIIIIIIIIIII.."], {"I": INK, "G": GOLD, "W": W})
    for y in range(12, 18):
        a.put(14, y, INK)
        a.put(15, y, GOLD)
    a.put(15, 12, INK)
    # the post and footing (cell 1)
    for y in range(21, 27):
        a.sprite(5, y, ["IWLLWI" if y % 4 else "IDDDDI"], {"I": INK, "W": W_L, "L": W, "D": W_D})
    a.sprite(1, 26, ["..IIIIIIIIII..",
                     ".IHHHHHHHHHHI.",
                     "IHLLLLLLLLLLHI",
                     "ITTTTTTTTTTTTI",
                     ".IIIIIIIIIIII."], {"I": INK, "H": T_HI, "L": T_L, "T": T, "D": T_D})
    return a


def cane_stalks(a, x0, x1, y0, y1, ends=True):
    """Cut cane lying east-west: stalks 2 px thick (gold lit top, green underside), a joint ring every 8 px staggered
    by 4 between neighbouring stalks (8 px periodic both ways, so heaps of any size repeat their tiles), the pale cut
    ends at both ends."""
    for y in range(y0, y1 + 1):
        top = y % 2 == 0
        sh = 4 if (y // 2) % 2 else 0
        for x in range(x0, x1 + 1):
            k = (x + sh) % 8
            c = CN_D if k == 0 else (GOLD if top else CN)
            if top and k == 4:
                c = CN
            a.put(x, y, c)
        if ends:
            a.put(x0, y, W_L if top else W)
            a.put(x1, y, W_L if top else W)


def cane_pile(big=True):
    """Cut cane in tied bundles, stacked (2x2) or a lower heap (2x1): stalks lying east-west, rope ties, a few leafy
    tops spilling off the heap; drawn on the left and mirrored. MILL."""
    a = Art(2, 2 if big else 1)
    layers = [(2, 29, 22, 29), (4, 27, 14, 21), (8, 23, 8, 13)] if big else [(2, 29, 6, 13)]
    for x0, x1, y0, y1 in layers:
        cane_stalks(a, x0, x1, y0, y1)
    a.outline(INK)
    for x0, x1, y0, y1 in layers:
        a.vline(x0 + 5, y0, y1, W_D)
        a.vline(x0 + 6, y0, y1, W)
    top = layers[-1][2]
    a.sprite(6, top - 4, ["...c......", "..cC...C..", ".cC.C.cCc.", "......C..."], {"C": CN, "c": CN_D})
    a.outline(INK, skip=(CN, CN_D))
    a.mirror_left()
    return a


# ================================================================ C. the cane railway
RAIL_A, RAIL_B = 5, 11    # the rails' rows in a track cell


def track(a, x0, x1, oy=0, sleepers=True):
    """Narrow-gauge track: a sleeper every 8 px, two rails (lit head, web, ink foot)."""
    if sleepers:
        for x in range(x0, x1 + 1):
            k = x % 8
            if k in (2, 3, 4, 5):
                for y in range(oy + 3, oy + 14):
                    a.put(x, y, W_D if k == 5 or y == oy + 13 else W if k in (3, 4) else W_L)
                a.put(x, oy + 2, INK)
                a.put(x, oy + 14, INK)
            if k in (1, 6):
                for y in range(oy + 3, oy + 14):
                    a.put(x, y, INK)
    for ry in (RAIL_A, RAIL_B):
        for x in range(x0, x1 + 1):
            a.put(x, oy + ry - 1, INK)
            a.put(x, oy + ry, T_HI)
            a.put(x, oy + ry + 1, T)
            a.put(x, oy + ry + 2, INK)
        for x in range(x0, x1 + 1):
            if x % 8 in (3, 4):
                a.put(x, oy + ry + 1, T_D)    # the spikes


def rail_h():
    a = Art(1, 1)
    track(a, 0, 15)
    return a


def rail_cross():
    """The level crossing: road planks laid between and beside the rails, flush with them."""
    a = Art(1, 1)
    for y in range(1, 15):
        for x in range(16):
            k = (y - 1) % 4
            a.put(x, y, INK if k == 3 else W_L if k == 0 else W)
    for x in range(16):
        a.put(x, 0, INK)
        a.put(x, 15, INK)
    for x, y in ((3, 2), (11, 2), (3, 14), (11, 14), (7, 8), (15, 8)):
        a.put(x, y, W_D)
    for ry in (RAIL_A, RAIL_B):
        for x in range(16):
            a.put(x, ry - 1, INK)
            a.put(x, ry, T_HI)
            a.put(x, ry + 1, T)
            a.put(x, ry + 2, INK)
    return a


def rail_end():
    """The buffer stop at the east end: the track's west half (rail_h's tiles) runs into a timber frame with a
    red-and-white buffer beam filling the east half."""
    a = Art(1, 1)
    track(a, 0, 7)
    a.sprite(8, 1, ["IIIIIIII",
                    "IHPHPHPI",
                    "IPHPHPHI",
                    "IIIIIIII",
                    "IWLI.IWI",
                    "IWLI.IWI",
                    "IWLI.IWI",
                    "IWLIIIWI",
                    "IWWWWWWI",
                    "IWDDDDWI",
                    "IWI..IWI",
                    "IDI..IDI",
                    "IIIIIIII"], {"I": INK, "H": T_HI, "P": PEP, "W": W, "L": W_L, "D": W_D})
    return a


def cane_truck(load=True):
    """An open flat cane truck, 3x2 (the bottom row is the track under its wheels): a timber deck on an iron frame,
    stakes up the sides, four spoked wheels on the rail; loaded with cut cane (or empty, a straw lining). Drawn on the
    left and mirrored about its middle; the loaded and empty trucks share their wheel and deck tiles. MILL."""
    a = Art(3, 2)
    track(a, 0, 47, oy=16)
    a.rect(2, 17, 24, 22, INK)                 # the deck and frame
    a.hline(3, 24, 18, W_L)
    a.hline(3, 24, 19, W)
    a.hline(3, 24, 20, W_D)
    a.hline(3, 24, 21, T_D)
    a.sprite(0, 18, ["II", "TI", "II"], {"I": INK, "T": T})
    for wx in (8, 16):
        a.sprite(wx - 4, 21, [".IIIIII.",
                              "IITTTTII",
                              "ITIDDITI",
                              "ITDHTDTI",
                              "ITIDDITI",
                              "IITTTTII",
                              ".IIIIII."], {"I": INK, "T": T, "D": T_D, "H": T_HI})
    a.rect(20, 22, 24, 23, INK)
    a.hline(20, 24, 22, T_D)
    if load:
        for x0, y0, y1 in ((3, 10, 16), (5, 6, 9), (9, 2, 5)):
            cane_stalks(a, x0, 24, y0, y1, ends=False)
            for y in range(y0, y1 + 1):
                a.put(x0, y, W_L if y % 2 == 0 else W)
        a.sprite(13, 0, ["..c..", ".cC.c"], {"C": CN, "c": CN_D})
        a.outline(INK, region=(0, 0, 24, 16), skip=(CN, CN_D))
    else:
        a.rect(3, 13, 24, 16, INK)
        for x in range(4, 25):
            a.put(x, 14, GOLD if x % 3 else W_L)
            a.put(x, 15, W_L if x % 4 else W)
            a.put(x, 16, W)
    for sx in ((3,) if load else (3, 14)):       # the stakes
        top = 6 if load else 9
        a.vline(sx - 1, top, 17, INK)
        a.vline(sx, top + 1, 17, W_L)
        a.vline(sx + 1, top + 1, 17, W_D)
        a.vline(sx + 2, top, 17, INK)
        a.hline(sx - 1, sx + 2, top, INK)
    a.mirror_left()
    if not load:
        cane_stalks(a, 18, 29, 12, 13)          # a few loose stalks left in the bed
    return a


# ================================================================ D. the bottling yard and the river
def sauce_vat():
    """A big wooden fermenting vat of red pepper mash, 2x2: staves bound by iron hoops (lit down the middle, rounding
    away at both sides; mirrored), the open top full of mash with a paddle leaning in it. MILL."""
    a = Art(2, 2)
    for y in range(9, 30):
        for x in range(3, 16):
            k = x % 4
            c = W_D if k == 0 else W_L if k == 1 else W
            if x <= 5:
                c = W_D if k == 0 else W
            a.put(x, y, c)
    for hy in (14, 24):
        a.hline(3, 15, hy, T_D)
        a.hline(3, 15, hy + 1, INK)
        a.hline(8, 15, hy, T)
    a.hline(3, 15, 30, INK)
    a.ellipse(16, 9, 14, 5.5, INK, x0=0, x1=15)
    a.ellipse(16, 9, 13, 4.5, W_L, x0=0, x1=15)
    a.ellipse(16, 9.4, 11.0, 3.4, BR_D, x0=0, x1=15)
    a.ellipse(16, 9.8, 10.0, 2.6, PEP, x0=0, x1=15)
    a.hline(5, 15, 14, W_D)
    a.outline(INK, region=(0, 0, 15, 31))
    a.mirror_left()
    for x, y in ((9, 9), (12, 8), (16, 10), (20, 9), (23, 10), (14, 11)):
        a.put(x, y, BR_L)
    for x, y in ((11, 10), (18, 11), (21, 8)):
        a.put(x, y, BR_D)
    for t in range(10):                       # the paddle
        a.put(17 + t, 9 - t, W_L)
        a.put(18 + t, 9 - t, W_D)
    a.sprite(26, 0, [".II", "IWI", "II."], {"I": INK, "W": W_L})
    return a


def bottle_crates():
    """Two crates of red-capped sauce bottles, 2x1: slatted wooden crates, the bottles' necks and caps in rows. MILL."""
    a = Art(2, 1)
    for ox in (1, 17):
        a.sprite(ox, 1, ["IIIIIIIIIIIIII",
                         "IPIPIPIPIPIPII"[:14],
                         "IHIHIHIHIHIHII"[:14],
                         "IPIPIPIPIPIPII"[:14],
                         "IHIHIHIHIHIHII"[:14],
                         "IIIIIIIIIIIIII",
                         "IWLLLLLLLLLLWI",
                         "IWWWWWWWWWWWWI",
                         "IIIIIIIIIIIIII",
                         "IWLLLLLLLLLLWI",
                         "IWWWWWWWWWWWWI",
                         "IWDDDDDDDDDDWI",
                         "IIIIIIIIIIIIII"],
                 {"I": INK, "P": PEP, "H": T_HI, "W": W, "L": W_L, "D": W_D})
    for ox in (1, 17):
        for i in range(6):
            for j in range(2):
                x, y = ox + 1 + i * 2, 2 + j * 2
                a.put(x, y, PEP)
                a.put(x, y + 1, T_HI if i % 2 == 0 else T_L)
    a.sprite(19, 2, ["G"], {"G": GOLD})
    return a


def ferry():
    """The Route 18 river launch, 3x2, moored on the water below the dock: a flat timber hull with a white strake and
    a rope rubbing strake, a little cabin with a red tin roof and a lit window in each bay, a lantern on a pole at the
    bow, the outboard at the stern, the mooring rope running up to the dock. The hull and cabin repeat every 8 px.
    MILL."""
    a = Art(3, 2)
    # the hull (x 2..45, y 13..24)
    for x in range(2, 46):
        for y, c in ((13, INK), (14, W_L), (15, W), (16, INK), (17, T_HI), (18, T_L), (19, INK), (20, W),
                     (21, W), (22, W_D), (23, INK)):
            if y == 19 and x % 4 in (1, 2):
                c = W_L                         # the rope rubbing strake
            if y in (20, 21) and x % 8 == 3:
                c = W_D                         # plank butts
            a.put(x, y, c)
        if x % 8 in (1, 5):
            a.put(x, 24, T_HI)                  # foam along the waterline
    for i, y in enumerate(range(13, 24)):      # the bow: rounded, raked
        for x in range(2, 2 + max(0, 4 - i // 2 - (1 if i > 6 else 0) * 2)):
            a.put(x, y, KEY)
    for i, y in enumerate(range(16, 24)):
        a.put(max(2, 5 - i // 2) if i < 6 else 2 + (i - 5), y, INK)
    a.vline(45, 13, 23, INK)
    # the cabin (x 23..40): red tin roof, white walls, a lit window per 8 px bay
    for y in range(2, 7):
        for x in range(24, 40):
            a.put(x, y, (BR_D, BR_L, BR, BR)[x % 4] if y < 6 else BR_D)
    a.hline(23, 40, 1, INK)
    a.hline(23, 40, 7, INK)
    for y in range(8, 13):
        for x in range(24, 40):
            k = x % 8
            c = T_HI
            if y in (9, 10, 11) and k in (2, 3, 4, 5):
                c = INK if k in (2, 5) or y == 9 and False else GOLD
                if y == 9 and k in (3, 4):
                    c = GOLD
                if y == 11 and k in (3, 4):
                    c = BR_L
            if y == 12:
                c = T_L
            a.put(x, y, c)
    a.vline(23, 1, 12, INK)
    a.vline(40, 1, 12, INK)
    # the lantern on its pole at the bow (west)
    a.sprite(5, 1, ["..I..",
                    ".III.",
                    "IGGGI",
                    "IGHGI",
                    "IGGGI",
                    ".III.",
                    "..I..",
                    "..W..",
                    "..W..",
                    "..W..",
                    "..W..",
                    ".IWI."], {"I": INK, "G": GOLD, "H": T_HI, "W": W_D})
    # a cleat at the bow and the mooring rope up to the dock
    a.sprite(12, 11, ["IIII", "ITTI"], {"I": INK, "T": T})
    for y in range(0, 12):
        x = 13 + (1 if y < 6 else 0)
        a.put(x, y, W_L)
        a.put(x + 1, y, INK if y % 3 == 0 else W)
    # the outboard at the stern
    a.sprite(42, 12, ["IIII.", "ITTI.", "ITDI.", "IDDI.", ".II..", ".IHI.", "..I.."],
             {"I": INK, "T": T, "D": T_D, "H": T_HI})
    return a


# ================================================================ registry
def build_pieces():
    PIECES.clear()
    add("sugar_mill", sugar_mill(), "Cayenne's gym: the sugar mill (brick stack, tin boiling house, crushing house), 7x8.",
        doors=[(3, 7)])
    add("ritas_office", ritas_office(), "Rita's office in the mill yard (whitewash, red tin, ledger sign), 5x4.",
        doors=[(1, 3)])
    for k, colour in zip("abcd", ("blue", "mint", "ochre", "rose")):
        add("shotgun_" + k, shotgun(k), f"Shotgun house ({colour} clapboard, shared roof and porch), 3x6.",
            doors=[(1, 5)])
    add("bottling_works", bottling_works(), "Pepper-Sauce Bottling Works (brick, saw-tooth roof, bottle sign), 9x6.",
        doors=[(2, 5)])
    walk = [(i, j) for j in range(6) for i in range(8) if not (3 <= i <= 4 and 0 <= j <= 3)]
    add("great_sundial", great_sundial(), "The great sundial on its octagonal flagstone plaza, 8x6.", walk=walk)
    for k in ("h", "v", "nw", "ne", "sw", "se"):
        add("yard_" + k, yard_piece(k), f"Mill yard fence ({k}): plank-and-post, cane-knife top rail.")
    gl = yard_gate_l()
    add("yard_gate_l", gl, "Mill yard gate post, west of the opening (leaf folded back).")
    add("yard_gate_r", gl.mirrored(), "Mill yard gate post, east of the opening (leaf folded back).")
    add("sundial", sundial(False), "Yard sundial: stone pedestal, brass dial, 2x2.")
    se, ne = mirror_piece(True), mirror_piece(False)
    add("mirror_se", se, "Brass mirror on a post, glass facing south-east, 1x2.")
    add("mirror_sw", se.mirrored(), "Brass mirror on a post, glass facing south-west, 1x2.")
    add("mirror_ne", ne, "Brass mirror on a post, glass facing north-east (back to us), 1x2.")
    add("mirror_nw", ne.mirrored(), "Brass mirror on a post, glass facing north-west (back to us), 1x2.")
    add("cane_pile", cane_pile(True), "Stacked bundles of cut cane, tied, 2x2.")
    add("cane_pile_b", cane_pile(False), "A low heap of cut cane, 2x1.")
    add("rail_h", rail_h(), "Cane railway track, east-west (walkable).", walk=[(0, 0)])
    add("rail_cross", rail_cross(), "Cane railway level crossing: planks between the rails (walkable).", walk=[(0, 0)])
    add("rail_end", rail_end(), "Cane railway buffer stop (east end).")
    add("cane_truck", cane_truck(True), "Cane truck loaded with cut cane, on its track, 3x2.")
    add("sauce_vat", sauce_vat(), "Wooden fermenting vat of red pepper mash, 2x2.")
    add("bottle_crates", bottle_crates(), "Crates of red-capped sauce bottles, 2x1.")
    add("ferry", ferry(), "Route 18 river launch moored by the dock (overlay on water), 3x2.")


def pack(width=24):
    names = list(PIECES)
    order = sorted(names, key=lambda n: (-PIECES[n][0].h, -PIECES[n][0].w, names.index(n)))
    x = y = rowh = 0
    place = {}
    for n in order:
        art = PIECES[n][0]
        if x + art.w > width:
            x, y, rowh = 0, y + rowh, 0
        place[n] = (x, y)
        x += art.w
        rowh = max(rowh, art.h)
    sheet = Image.new("RGB", (width * 16, (y + rowh) * 16), KEY)
    index = {}
    for n in names:
        cx, cy = place[n]
        art, meta = PIECES[n]
        sheet.paste(art.im, (cx * 16, cy * 16))
        index[n] = dict(meta, x=cx, y=cy)
    return sheet, index


# ================================================================ checks and the tile census
def canon(t):
    return min(v.tobytes() for v in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))


def tiles_of(im):
    a = np.array(im)
    out = []
    for ty in range(0, a.shape[0], 8):
        for tx in range(0, a.shape[1], 8):
            t = a[ty:ty + 8, tx:tx + 8]
            if ((t[..., 0] == 255) & (t[..., 1] == 0) & (t[..., 2] == 255)).all():
                continue
            out.append(canon(t))
    return out


def census():
    """Unique 8x8 tiles (flips free, fully clear tiles free), piece by piece in registry order: new tiles each adds."""
    seen = set()
    rows = []
    for n, (art, meta) in PIECES.items():
        ts = tiles_of(art.im)
        new = 0
        for k in ts:
            if k not in seen:
                seen.add(k)
                new += 1
        rows.append((n, art.w, art.h, len(set(ts)), new))
    return rows, len(seen)


def check():
    problems = []
    for n, (art, meta) in PIECES.items():
        cols = {c for c in art.im.getdata() if c != KEY}
        fam = set(MILL) | {c for v in WALLS.values() for c in v}
        if len(cols) > 15:
            problems.append(f"{n}: {len(cols)} colours")
        bad = [c for c in cols if any(v % 8 for v in c) or c not in fam]
        if bad:
            problems.append(f"{n}: colours outside the families {bad[:4]}")
        if n.startswith("shotgun"):
            if len(cols) > 15:
                problems.append(f"{n}: house over 15")
        for d in meta["doors"]:
            if list(d) in meta["empty"]:
                problems.append(f"{n}: door cell {d} empty")
    return problems


# ================================================================ preview and review
def sand_cell():
    dry = json.load(open(os.path.join(HERE, "dry_country.json"), encoding="utf-8"))
    sheet = Image.open(os.path.join(HERE, dry["png"])).convert("RGB")
    v = dry["terrain"]["dry"]
    x, y = v[0] if isinstance(v[0], list) else v
    return sheet.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)), sheet, dry


def mask(im):
    a = np.array(im.convert("RGB"))
    m = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
    return Image.fromarray((m * 255).astype(np.uint8))


def on_ground(im, cell):
    bg = Image.new("RGB", im.size)
    for y in range(0, im.height, 16):
        for x in range(0, im.width, 16):
            bg.paste(cell, (x, y))
    bg.paste(im, (0, 0), mask(im))
    return bg


WATER = (96, 136, 136)


def write_preview(sheet, path):
    sand = sand_cell()[0]
    on_ground(sheet, sand).resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(path)


def town_patch():
    """A test patch of the town drawn the way the builder would: dry ground, the dry set's road, Ekat-flat water,
    the pieces on top (the dock is a plain plank stand-in for the Olivine dock)."""
    sys.path.insert(0, HERE)
    import make_dry_country as dc
    sand, dsheet, dry = sand_cell()
    rows = [
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddddddddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "::::::::::::::::::::::::::::::::::~~~~",
        "::::::::::::::::::::::::::::::::::~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::::::::::::::::~~~~",
        "dddddddddddddddddd::::::::::::::::~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
        "dddddddddddddddddd::dddddddddddddd~~~~",
    ]
    PW, PH = len(rows[0]), len(rows)
    terr = [r.replace("~", "d") for r in rows]
    img = dc.render_patch(dsheet, dry, terr)
    px = img.load()
    for y in range(PH):
        for x in range(PW):
            if rows[y][x] == "~":
                for j in range(16):
                    for i in range(16):
                        px[x * 16 + i, y * 16 + j] = WATER
    objs = []
    P = lambda n, x, y: objs.append((n, x, y))
    # ---- the mill yard (x 0..17, y 0..11): fence, gate on the south side, mill, office, sundials, mirrors, piles
    x0, y0, x1, y1 = 0, 0, 17, 11
    gate = (8, 9)
    for x in range(x0, x1 + 1):
        for y, south in ((y0, False), (y1, True)):
            if south and x in gate:
                continue
            n = "yard_h"
            if x == x0:
                n = "yard_sw" if south else "yard_nw"
            elif x == x1:
                n = "yard_se" if south else "yard_ne"
            elif south and x == gate[0] - 1:
                n = "yard_gate_l"
            elif south and x == gate[1] + 1:
                n = "yard_gate_r"
            P(n, x, y)
    for y in range(y0 + 1, y1):
        P("yard_v", x0, y)
        P("yard_v", x1, y)
    P("sugar_mill", 10, 1)
    P("ritas_office", 1, 1)
    P("sundial", 2, 6)
    P("sundial", 6, 7)
    P("mirror_se", 1, 8)
    P("mirror_sw", 5, 5)
    P("mirror_ne", 8, 6)
    P("mirror_nw", 4, 8)
    P("cane_pile", 7, 1)
    P("cane_pile_b", 7, 3)
    P("cane_pile_b", 2, 9)
    # ---- the cane railway along y 13 (the road row 12-13 is crossed at x 18-19... the line runs on row 15)
    # ---- the shotgun street (y 14..19), the four colourways side by side
    for i, k in enumerate("abcd"):
        P("shotgun_" + k, i * 4 + 1, 14)
    # rail line on row 21 with a level crossing at the street (x 18-19) and trucks at the west end
    for x in range(0, 33):
        if x in (18, 19):
            P("rail_cross", x, 21)
        elif not (1 <= x <= 9):
            P("rail_h", x, 21)
    P("rail_end", 33, 21)
    P("cane_truck", 1, 20)
    P("cane_truck", 4, 20)
    P("cane_truck", 7, 20)
    # ---- the great sundial plaza and the bottling works with its yard
    P("great_sundial", 0, 23)
    P("bottling_works", 21, 25)
    P("sauce_vat", 30, 15)
    P("sauce_vat", 32, 15)
    P("bottle_crates", 30, 18)
    P("bottle_crates", 32, 18)
    P("cane_pile_b", 21, 15)
    P("cane_pile", 23, 15)
    # ---- the river, the dock (a plank stand-in for the Olivine dock: rows 26-27, posts in the water), the ferry
    for x in range(31 * 16, 38 * 16):
        for y in range(26 * 16, 28 * 16 + 4):
            yy = y - 26 * 16
            if yy >= 32:
                c = W_D if (x % 32) in (6, 7, 8) else None
            elif yy in (0, 31):
                c = INK
            else:
                c = INK if x % 8 == 7 else W_L if x % 8 == 0 else W
            if c:
                px[x, y] = c
    P("ferry", 34, 28)
    for n, x, y in objs:
        art = PIECES[n][0].im
        img.paste(art, (x * 16, y * 16), mask(art))
    return img


def review(sheet, index, path, census_rows, total, problems):
    S = 3
    sand = sand_cell()[0]
    BG, FG, HI = (36, 40, 44), (225, 225, 210), (255, 240, 160)
    groups = [
        ("Buildings", ["sugar_mill", "ritas_office", "shotgun_a", "shotgun_b", "shotgun_c", "shotgun_d",
                       "bottling_works"]),
        ("Landmark", ["great_sundial"]),
        ("Mill yard", ["yard_nw", "yard_h", "yard_ne", "yard_v", "yard_sw", "yard_se", "yard_gate_l", "yard_gate_r",
                       "sundial", "mirror_se", "mirror_sw", "mirror_ne", "mirror_nw", "cane_pile",
                       "cane_pile_b"]),
        ("Cane railway", ["rail_h", "rail_cross", "rail_end", "cane_truck"]),
        ("Bottling yard and river", ["sauce_vat", "bottle_crates", "ferry"]),
    ]
    info = {n: (tot, new) for n, w, h, tot, new in census_rows}
    Wd = 2000
    blocks = []
    for title, names in groups:
        items = []
        for n in names:
            art = PIECES[n][0].im
            ground = Image.new("RGB", art.size, WATER) if n == "ferry" else on_ground(Image.new("RGB", art.size, KEY), sand)
            ground.paste(art, (0, 0), mask(art))
            pad = Image.new("RGB", (art.width + 16, art.height + 16))
            for y in range(0, pad.height, 16):
                for x in range(0, pad.width, 16):
                    if n == "ferry":
                        pad.paste(Image.new("RGB", (16, 16), WATER), (x, y))
                    else:
                        pad.paste(sand, (x, y))
            pad.paste(ground, (8, 8))
            items.append((n, pad.resize((pad.width * S, pad.height * S), Image.NEAREST)))
        blocks.append((title, items))
    patch = town_patch()
    patch3 = patch.resize((patch.width * S, patch.height * S), Image.NEAREST)
    # layout
    y = 10
    lay = []
    for title, items in blocks:
        lay.append(("t", title, 10, y))
        y += 22
        x, rowh = 10, 0
        for n, im in items:
            if x + max(im.width, 236) > Wd - 10:
                x, y = 10, y + rowh + 28
                rowh = 0
            lay.append(("i", (n, im), x, y))
            x += max(im.width + 14, 250)
            rowh = max(rowh, im.height)
        y += rowh + 34
    lay.append(("t", "Test patch at 3x: the mill yard (fence, south gate, sundials, mirrors, cane piles), the shotgun "
                     "street (blue, mint, ochre, rose), the cane railway with a level crossing and trucks, the great "
                     "sundial, the bottling works with vats and crates, the ferry below the dock", 10, y))
    y += 22
    lay.append(("p", patch3, 10, y))
    y += patch3.height + 16
    out = Image.new("RGB", (max(Wd, patch3.width + 20), y + 40 + 16 * (len(problems) + 3)), BG)
    d = ImageDraw.Draw(out)
    for kind, v, x, yy in lay:
        if kind == "t":
            d.text((x, yy), v, fill=HI)
        elif kind == "i":
            n, im = v
            out.paste(im, (x, yy))
            tot, new = info[n]
            m = index[n]
            extra = f" door {m['doors'][0]}" if m["doors"] else ""
            d.text((x, yy + im.height + 3), f"{n} {m['w']}x{m['h']}{extra}: {tot} tiles ({new} new)", fill=FG)
        else:
            out.paste(v, (x, yy))
    d.text((10, y), f"TOTAL: {total} unique 8x8 tiles for all Redfield pieces (flips free, fully clear tiles free; "
                    f"'new' = tiles not already used by an earlier piece in this list)", fill=HI)
    y += 18
    for p in problems:
        d.text((10, y), "PROBLEM: " + p, fill=(255, 120, 120))
        y += 16
    out.save(path)


def main():
    build_pieces()
    problems = check()
    sheet, index = pack()
    sheet.save(os.path.join(HERE, "redfield.png"))
    with open(os.path.join(HERE, "redfield.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_comment": "Redfield own art index (make_redfield_art.py): piece -> sheet cell and size; "
                               "magenta = clear. See tools/mapgen/art_requests/redfield.md.",
                   "pieces": index}, f, indent=1)
        f.write("\n")
    write_preview(sheet, os.path.join(HERE, "redfield_preview.png"))
    rows, total = census()
    review(sheet, index, os.path.join(MAPGEN, "maps", "00_redfield_art.png"), rows, total, problems)
    for n, w, h, tot, new in rows:
        print(f"  {n:18s} {w}x{h} {tot:4d} tiles {new:4d} new")
    print(f"  TOTAL unique 8x8 tiles: {total}")
    for p in problems:
        print("  PROBLEM:", p)


if __name__ == "__main__":
    main()

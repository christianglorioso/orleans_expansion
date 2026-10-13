"""Optional Game Corner furniture for gTileset_OrleansInterior (riverboat-casino hall, CrescentCity_GameCorner 21x14).

usage (from the decomp root): python tools/game_corner_art/make_furniture.py

Pieces (16 px cells), all drawn on the TOP layer over the hall's plain carpet (bottom = the primary's jb:0CC floor,
copied into each sheet so compose re-uses the primary tile), layer type covered (everything under the sprites,
like the counters already in the room):
    gacha_<tier>_0/1   1x2  capsule machine, globe over body: basic (red), great (blue), ultra (gold), master (purple)
    bj_<i>_<j>         4x2  Blackjack table: half-moon of teal felt in a dark wood rim with brass tacks, dealer's
                            chip tray and shoe on the flat north side, three betting spots by the player's rail
    derby_<i>_<j>      4x2  Derby window: chalk odds board (upper half of row 0, over the clerk's head), counter
                            with a brass ticket grille (row 1)
    counter_L/M/R      1x1  brass-railed counter (coin clerk)
    case_L/M/R         1x1  glass prize case (prize counter)

Palettes: interior's legacy palette packer re-packs the whole tileset if a sheet brings colours no slot has, so each
sheet is drawn in ONE existing palette's colours (the slot is named per sheet below) and is its own compose source;
the only new colours are three purples for the Master machine, added to the slot that has 8 free entries.
Tested by composing: every existing metatile of orleans_interior is unchanged.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MAPGEN = os.path.join(ROOT, "tools", "mapgen")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(MAPGEN, "tilesets", "arenas"))
sys.path.insert(0, MAPGEN)
from arena_art import Canvas, dump  # noqa: E402
from gc_kit import REVIEW, font, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = os.path.join(HERE, "furniture")
FLOOR = (232, 176, 112)       # jb:0CC, the hall carpet (primary palette 4)
KEY = (255, 0, 255)
SLATE = (80, 80, 104)         # the HnS outline colour, in every palette used here

# ---------------------------------------------------------------- capsule machines
TIERS = {
    # name: (sheet / existing palette, colours)
    "basic": ("gc_red", dict(hi=(248, 128, 112), main=(200, 80, 64), dark=SLATE, glass=(216, 224, 224),
                             glass2=(176, 176, 160), glint=(248, 248, 248), metal=(144, 144, 136), metal2=(120, 120, 120),
                             caps=[(248, 128, 112), (240, 232, 144), (104, 192, 104), (80, 144, 192), (248, 248, 248)],
                             crank=(208, 192, 104), crank2=(168, 144, 64))),
    "great": ("gc_blue", dict(hi=(120, 184, 248), main=(48, 112, 192), dark=SLATE, glass=(216, 224, 224),
                              glass2=(176, 176, 160), glint=(232, 248, 248), metal=(144, 144, 136), metal2=(120, 120, 120),
                              caps=[(224, 96, 80), (192, 160, 64), (128, 184, 112), (120, 184, 248), (248, 120, 96)],
                              crank=(208, 176, 104), crank2=(192, 160, 64))),
    "ultra": ("gc_gold", dict(hi=(248, 240, 128), main=(224, 176, 72), dark=(128, 112, 88), glass=(232, 232, 240),
                              glass2=(176, 176, 160), glint=(248, 248, 248), metal=(168, 168, 160), metal2=(120, 120, 120),
                              caps=[(248, 240, 128), (224, 176, 72), (248, 248, 248), (168, 152, 104), (128, 112, 88)],
                              crank=(168, 152, 104), crank2=(128, 112, 88))),
    "master": ("gc_purple", dict(hi=(184, 128, 232), main=(136, 80, 192), dark=(88, 48, 136), glass=(176, 224, 248),
                                 glass2=(192, 184, 208), glint=(248, 248, 248), metal=(192, 184, 208), metal2=(120, 120, 120),
                                 caps=[(184, 128, 232), (168, 208, 120), (248, 248, 248), (176, 224, 248), (128, 160, 104)],
                                 crank=(192, 184, 208), crank2=(120, 120, 120))),
}
SHEET_SLOT = {"gc_red": "interior palette 6", "gc_blue": "primary palette 1", "gc_gold": "interior palette 8",
              "gc_purple": "interior palette 9 + 3 purples", "gc_table": "interior palette 10 (+ white)",
              "gc_derby": "interior palette 11"}


def machine(c):
    """1x2 (16x32): glass globe of capsules on a lidded cap, body with a coin slot, crank and chute, on a base."""
    cv = Canvas(1, 2)
    o = c["dark"] if c["dark"] != SLATE else SLATE
    # globe (centre 8,11, r 6.5)
    cx, cy, r = 7.5, 11.0, 6.5
    for y in range(32):
        for x in range(16):
            d2 = (x + 0.5 - (cx + 0.5)) ** 2 + (y + 0.5 - (cy + 0.5)) ** 2
            if d2 <= r * r:
                cv.put(x, y, c["glass"])
    # capsules: two-tone balls (colour top, pale bottom) heaped in the globe
    caps = [(3, 12), (6, 13), (9, 13), (12, 12), (4, 9), (8, 10), (11, 8), (6, 6)]
    for i, (x, y) in enumerate(caps):
        col = c["caps"][i % len(c["caps"])]
        cv.rect(x, y, 3, 2, col)
        cv.hline(x, x + 2, y + 2, c["glass2"])
        cv.put(x, y, c["glint"])
    # glass: rim shading and glint
    for y in range(32):
        for x in range(16):
            d2 = (x + 0.5 - (cx + 0.5)) ** 2 + (y + 0.5 - (cy + 0.5)) ** 2
            if r * r >= d2 > (r - 1) ** 2 and (x > cx or y > cy):
                cv.put(x, y, c["glass2"])
    for (x, y) in ((4, 7), (4, 8), (5, 6), (3, 9)):
        cv.put(x, y, c["glint"])
    # lid on top of the globe
    cv.rect(5, 3, 6, 2, c["main"])
    cv.hline(5, 10, 3, c["hi"])
    cv.rect(6, 2, 4, 1, c["hi"])
    # collar under the globe, then the body
    cv.rect(2, 17, 12, 2, c["metal"])
    cv.hline(2, 13, 17, c["glass"])
    cv.rect(2, 19, 12, 10, c["main"])
    cv.vline(2, 19, 28, c["hi"])
    cv.hline(2, 13, 19, c["hi"])
    cv.vline(13, 20, 28, o)
    # crank knob (left), coin slot (right), capsule chute (bottom centre)
    cv.ellipse(5.5, 23.0, 2.6, 2.6, c["metal"])
    cv.put(4, 21, c["glint"])
    cv.hline(3, 8, 23, c["crank2"])
    cv.rect(7, 22, 2, 3, c["crank"])
    cv.rect(10, 21, 2, 4, o)
    cv.put(10, 21, c["metal2"])
    cv.rect(5, 26, 6, 2, o)
    cv.hline(5, 10, 26, c["metal2"])
    # base
    cv.rect(1, 29, 14, 2, c["metal2"])
    cv.hline(1, 14, 29, c["metal"])
    cv.outline(SLATE)
    return cv


# ---------------------------------------------------------------- Blackjack table (interior palette 10 + white)
T_FELT, T_FELT2, T_LINE = (40, 152, 152), (48, 184, 168), (64, 224, 184)
T_W0, T_W1, T_W2 = (128, 104, 72), (152, 128, 64), (168, 152, 72)
T_BR1, T_BR2 = (224, 216, 104), (216, 200, 96)
T_WHITE = (248, 248, 248)


def table():
    import math
    cv = Canvas(4, 2)
    cx, top, rx, ry = 31.5, 2, 30.5, 22.0     # half-moon top: flat north edge at y=2, curve down to y=24

    def inside(x, y, shrink=0.0, dy=0.0):
        if y < top + shrink * 0.5:
            return False
        nx, ny = (x + 0.5 - (cx + 0.5)) / (rx - shrink), (y + 0.5 - top - dy) / (ry - shrink)
        return nx * nx + ny * ny <= 1.0
    for y in range(32):
        for x in range(64):
            if inside(x, y, 0, 4) and not inside(x, y):
                cv.put(x, y, T_W0)               # the apron: the rim's front face, seen below the top
            if inside(x, y):
                cv.put(x, y, T_W1)
            if inside(x, y, 1.0):
                cv.put(x, y, T_W2)
            if inside(x, y, 2.6):
                cv.put(x, y, T_FELT)
    for y in range(32):                          # apron shading: darker toward the bottom
        for x in range(64):
            if cv.get(x, y) == T_W0 and inside(x, y - 2, 0, 0):
                cv.put(x, y, T_W1 if (x // 3) % 2 else T_W0)
    # felt: lit band under the dealer's edge, the insurance arc
    for y in range(32):
        for x in range(64):
            if cv.get(x, y) == T_FELT:
                if y <= top + 3:
                    cv.put(x, y, T_FELT2)
                nx, ny = (x + 0.5 - (cx + 0.5)) / 18.0, (y + 0.5 - top) / 12.0
                if abs(math.hypot(nx, ny) - 1.0) < 0.045:
                    cv.put(x, y, T_LINE)
    # brass tacks along the rim
    for k in range(15):
        a = math.pi * (k + 0.5) / 15
        cv.put(int(round(cx - math.cos(a) * (rx - 0.6))), int(round(top + math.sin(a) * (ry - 0.6))), T_BR1)
    # five betting spots around the player's rail
    for k in range(5):
        a = math.pi * (k + 1) / 6
        bx, by = cx - math.cos(a) * 23.0, top + math.sin(a) * 16.0
        cv.ellipse(bx + 0.5, by + 0.5, 2.6, 1.7, T_LINE)
        cv.ellipse(bx + 0.5, by + 0.5, 1.4, 0.8, T_FELT)
    # dealer's chip tray and the card shoe on the flat side; two cards dealt
    cv.rect(23, 3, 18, 4, T_W0)
    for i, col in enumerate((T_BR1, T_WHITE, T_BR2, T_LINE, T_BR1, T_WHITE, T_BR2, T_LINE)):
        cv.vline(24 + i * 2, 4, 5, col)
    cv.rect(46, 3, 6, 4, T_W0)
    cv.rect(47, 4, 4, 2, T_WHITE)
    for (x, y) in ((27, 9), (32, 9)):
        cv.rect(x, y, 4, 5, T_WHITE)
        cv.put(x + 1, y + 1, T_LINE)
        cv.put(x + 2, y + 3, T_W1)
    cv.outline(T_W0)
    return cv


# ---------------------------------------------------------------- Derby window (interior palette 11)
D_BOARD, D_BOARD2, D_CHALK = (80, 112, 80), (72, 152, 88), (232, 232, 168)
D_WOOD, D_RED, D_PEACH, D_TEAL = (152, 128, 80), (192, 112, 120), (248, 160, 120), (64, 136, 136)
D_GREEN = (112, 200, 88)

DIGITS = {"2": ["111", "..1", "111", "1..", "111"], "3": ["111", "..1", ".11", "..1", "111"],
          "4": ["1.1", "1.1", "111", "..1", "..1"], "5": ["111", "1..", "111", "..1", "111"],
          "6": ["111", "1..", "111", "1.1", "111"], "9": ["111", "1.1", "111", "..1", "111"],
          "x": ["...", "1.1", ".1.", "1.1", "..."]}


def chalk(cv, x, y, text, c):
    for ch in text:
        g = DIGITS[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == "1":
                    cv.put(x + i, y + j, c)
        x += len(g[0]) + 1


def derby():
    cv = Canvas(4, 2)
    # odds board across the top row's upper half (the clerk stands in front of it, under its lower edge)
    cv.rect(1, 0, 62, 10, D_WOOD)
    cv.rect(3, 1, 58, 7, D_BOARD)
    # six lanes: the lane colour, then the odds in chalk ("x3", "x5", ...)
    lanes = [D_RED, D_PEACH, D_GREEN, D_TEAL, D_CHALK, D_RED]
    for i, odds in enumerate(["x2", "x3", "x5", "x4", "x6", "x9"]):
        x = 4 + i * 9
        cv.rect(x, 3, 1, 3, lanes[i])
        chalk(cv, x + 2, 2, odds, D_CHALK)
    cv.hline(3, 60, 8, D_WOOD)
    cv.hline(1, 62, 9, D_WOOD)
    for x in (2, 61):          # the board's posts, down behind the counter
        cv.vline(x, 10, 15, D_WOOD)
    # counter (row 1): top, front face with panels, brass-coloured ticket grille in the middle two cells
    cv.rect(0, 16, 64, 4, D_CHALK)
    cv.hline(0, 63, 19, D_PEACH)
    cv.rect(0, 20, 64, 10, D_WOOD)
    for x in range(4, 64, 16):
        cv.rect(x, 22, 8, 6, D_BOARD2 if 16 <= x < 48 else D_WOOD)
    for x in range(4, 64, 16):
        cv.hline(x, x + 7, 22, D_CHALK if 16 <= x < 48 else D_PEACH)
    # grille: an arched window on the counter top, bars
    cv.rect(22, 10, 20, 7, D_WOOD)
    cv.rect(24, 11, 16, 6, D_TEAL)
    for x in range(25, 40, 3):
        cv.vline(x, 11, 16, D_CHALK)
    cv.hline(22, 41, 10, D_CHALK)
    cv.rect(29, 16, 6, 2, SLATE)        # the ticket slot
    cv.outline(SLATE)
    return cv


# ---------------------------------------------------------------- counters (interior palette 8)
C_W1, C_W2, C_BR1, C_BR2 = (128, 112, 88), (168, 152, 104), (248, 240, 128), (224, 176, 72)
C_GL, C_GL2, C_WH, C_G1, C_G2 = (232, 232, 240), (176, 176, 160), (248, 248, 248), (168, 168, 160), (120, 120, 120)


def counter(part, case=False):
    """One cell of a 3-piece counter: top 6 px, front face below. part in L / M / R."""
    cv = Canvas(1, 1)
    x0 = 1 if part == "L" else 0
    x1 = 14 if part == "R" else 15
    if case:   # glass prize case: glass top showing prizes, wood frame and face
        cv.rect(x0, 1, x1 - x0 + 1, 8, C_W2)
        cv.rect(x0 + (1 if part == "L" else 0), 2, x1 - x0 + 1 - (1 if part in "LR" else 0), 6, C_GL)
        prizes = {"L": [(5, 4, C_BR2), (9, 3, C_BR1)], "M": [(3, 3, C_BR1), (8, 5, C_BR2), (12, 3, C_G1)],
                  "R": [(4, 4, C_BR2), (9, 3, C_BR1)]}[part]
        for (x, y, col) in prizes:
            cv.rect(x, y, 3, 2, col)
            cv.put(x, y, C_WH)
        for x in range(x0, x1 + 1, 5):
            cv.put(x + 1, 2, C_WH)
        cv.rect(x0, 9, x1 - x0 + 1, 5, C_W1)
        cv.hline(x0, x1, 9, C_W2)
        cv.hline(x0, x1, 14, C_G2)
    else:      # brass-railed counter: wood top, a brass rail along the front, panelled face
        cv.rect(x0, 2, x1 - x0 + 1, 6, C_W2)
        cv.hline(x0, x1, 2, C_GL)
        cv.hline(x0, x1, 7, C_BR1)
        cv.hline(x0, x1, 8, C_BR2)
        for x in range(x0 + 2, x1, 5):
            cv.vline(x, 7, 9, C_BR2)
        cv.rect(x0, 9, x1 - x0 + 1, 5, C_W1)
        for x in range(x0 + 2, x1 - 1, 6):
            cv.rect(x, 10, 4, 3, C_W2)
        cv.hline(x0, x1, 14, C_G2)
    cv.outline(SLATE)
    return cv


# ---------------------------------------------------------------- sheets, recipe sources, mock
def build():
    sheets = {}

    def add(sheet, name, cv):
        sheets.setdefault(sheet, []).append((name, cv))
    for tier, (sheet, col) in TIERS.items():
        add(sheet, f"gacha_{tier}", machine(col))
    add("gc_table", "bj", table())
    add("gc_derby", "derby", derby())
    for p in "LMR":
        add("gc_gold", f"counter_{p}", counter(p))
        add("gc_gold", f"case_{p}", counter(p, case=True))
    return sheets


def write(sheets):
    """One overlay-only image source per sheet + overlay patches over the carpet (base pc:0CC = johto_building's
    0CC, the same metatile as the primary's jb:0CC, so compose re-uses the primary's carpet tile under the art)."""
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "sources"), exist_ok=True)
    index, all_patches = {}, []
    for sheet, items in sheets.items():
        cols = sum(cv.cw for _, cv in items)
        rows = max(cv.ch for _, cv in items)
        im = Image.new("RGB", (cols * 16, rows * 16), KEY)
        mts, x = [], 0
        for name, cv in items:
            sub = Image.new("RGB", (cv.w, cv.h), KEY)
            sub.paste(cv.im, (0, 0), cv.im)
            im.paste(sub, (x * 16, 0))
            for j in range(cv.ch):
                for i in range(cv.cw):
                    mid = name if cv.cw == cv.ch == 1 else (f"{name}_{j}" if cv.cw == 1 else f"{name}_{i}_{j}")
                    mts.append({"id": mid, "bottom": [x + i, j]})
                    all_patches.append({"id": f"gc_{mid}", "overlay": {"base": "pc:0CC", "art": f"{sheet}:{mid}"}})
                    index.setdefault(name, {"sheet": sheet, "w": cv.cw, "h": cv.ch, "cells": []})["cells"].append(
                        [i, j, f"patch:gc_{mid}", [x + i, j]])
            x += cv.cw
        im.save(os.path.join(OUT, f"{sheet}.png"))
        dump(os.path.join(OUT, "sources", f"orleans_interior.{sheet}.json"), {
            "_comment": f"Append to the 'sources' of tools/mapgen/tilesets/recipes/orleans_interior.json (own art, "
                        f"make_furniture.py; drawn in {SHEET_SLOT[sheet]}). Art only: the metatiles are the overlay "
                        f"patches in orleans_interior.patches.json.",
            "name": sheet, "type": "image", "image": f"tools/game_corner_art/furniture/{sheet}.png",
            "transparent": [[255, 0, 255]], "group_rule": "fewest", "overlay_only": True, "metatiles": mts})
    dump(os.path.join(OUT, "sources", "orleans_interior.patches.json"), all_patches)
    dump(os.path.join(OUT, "furniture.json"), {
        "_comment": "Game Corner furniture: piece -> sheet, size in cells, cells [x, y, metatile name once composed "
                    "into gTileset_OrleansInterior, sheet cell]. Every cell is an overlay patch: the hall carpet "
                    "(jb:0CC) below, the art above, layer covered (under sprites). Suggested places in "
                    "CrescentCity_GameCorner (21x14): gacha machines at x 2/4/6/8, y 2-3 (basic, great, ultra, "
                    "master); Blackjack table x 8-11, y 7-8; Derby window x 12-15, y 2-3 (the attendant at (13,2) "
                    "stands in front of the odds board); prize case x 17-19, y 3; coin counter x 2-4, y 8. All cells "
                    "block; the signs stay where they are.",
        "pieces": index})
    return index


def room_mock(index):
    """The Game Corner as built now, and with the pieces placed (3x)."""
    import struct
    sys.path.insert(0, MAPGEN)
    from render import Tilesets
    t = Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_building"),
                 os.path.join(ROOT, "data/tilesets/secondary/orleans_interior"))
    w, h = 21, 14
    d = open(os.path.join(ROOT, "data/layouts/CrescentCity_GameCorner/map.bin"), "rb").read()
    base = Image.new("RGB", (w * 16, h * 16))
    for y in range(h):
        for x in range(w):
            base.paste(t.metatile(struct.unpack_from("<H", d, 2 * (y * w + x))[0] & 0x3FF), (x * 16, y * 16))
    after = base.copy()
    place = {"gacha_basic": (2, 2), "gacha_great": (4, 2), "gacha_ultra": (6, 2), "gacha_master": (8, 2),
             "bj": (8, 7), "derby": (12, 2), "case_L": (17, 3), "case_M": (18, 3), "case_R": (19, 3),
             "counter_L": (2, 8), "counter_M": (3, 8), "counter_R": (4, 8)}
    imgs = {}
    for sheet in {v["sheet"] for v in index.values()}:
        imgs[sheet] = Image.open(os.path.join(OUT, f"{sheet}.png")).convert("RGB")
    for name, (px, py) in place.items():
        p = index[name]
        sh = imgs[p["sheet"]]
        for (i, j, mt, (cx, cy)) in p["cells"]:
            cell = sh.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16))
            floor = Image.new("RGB", (16, 16), FLOOR)
            mask = Image.eval(cell, lambda v: v).convert("RGB")
            m = Image.new("L", (16, 16), 0)
            cp, mp = cell.load(), m.load()
            for yy in range(16):
                for xx in range(16):
                    mp[xx, yy] = 0 if cp[xx, yy] == KEY else 255
            floor.paste(mask, (0, 0), m)
            after.paste(floor, ((px + i) * 16, (py + j) * 16))
    return base, after


def main():
    os.makedirs(REVIEW, exist_ok=True)
    sheets = build()
    index = write(sheets)
    base, after = room_mock(index)
    k = 3
    out = Image.new("RGB", (base.width * k * 2 + 60, base.height * k + 60), (40, 40, 48))
    dr = ImageDraw.Draw(out)
    dr.text((20, 12), "CrescentCity_GameCorner: now (stand-ins) | with the riverboat-casino furniture (3x)",
            fill=(230, 230, 230), font=font(18))
    out.paste(scale(base, k), (20, 44))
    out.paste(scale(after, k), (40 + base.width * k, 44))
    out.save(os.path.join(REVIEW, "room_mock.png"))
    # the sheets at 6x on the carpet
    rows = []
    for sheet in sheets:
        im = Image.open(os.path.join(OUT, f"{sheet}.png")).convert("RGB")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                if px[x, y] == KEY:
                    px[x, y] = FLOOR
        rows.append((sheet, scale(im, 6)))
    W = max(r.width for _, r in rows) + 40
    H = sum(r.height + 34 for _, r in rows) + 10
    sh = Image.new("RGB", (W, H), (40, 40, 48))
    dr = ImageDraw.Draw(sh)
    y = 6
    for name, r in rows:
        dr.text((20, y), f"{name}.png  ({SHEET_SLOT[name]})", fill=(230, 230, 230),
                font=font(15))
        sh.paste(r, (20, y + 24))
        y += r.height + 34
    sh.save(os.path.join(REVIEW, "furniture_sheets.png"))


if __name__ == "__main__":
    main()

"""Helpers for walking the player across map seams and grading what the screen shows (used by tests/t_transitions.py).

Cell data (behavior, collision, elevation) comes from the game's own MapGrid functions through the harness `mapinfo`
command, so water/land and elevation rules are what the engine sees, not what the layout files say.
Frames are 240x160 RGB numpy arrays; the player stands on screen tile column 7, row 4 (16 px tiles) whenever idle.
"""
import re
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

from bot import ROOT, map_data, wsl_path

DIRV = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
PLAYER_COL, PLAYER_ROW = 7, 4
COLS, ROWS = 15, 10


# ---------------------------------------------------------------- behaviors
def _surfable_behaviors():
    mb = (ROOT / "include/constants/metatile_behaviors.h").read_text()
    body = mb[mb.index("enum {"):mb.index("};")]
    names, val = {}, 0
    for line in body.splitlines()[1:]:
        m = re.match(r"\s*(MB_\w+)\s*(?:=\s*(\w+))?\s*,", line)
        if m:
            if m.group(2):
                val = int(m.group(2), 0)
            names[m.group(1)] = val
            val += 1
    src = (ROOT / "src/metatile_behavior.c").read_text()
    surf = set()
    for m in re.finditer(r"\[(MB_\w+)\]\s*=([^\n]*)", src):
        if "TILE_FLAG_SURFABLE" in m.group(2) and m.group(1) in names:
            surf.add(names[m.group(1)])
    bad = {names[n] for n in names if "WATERFALL" in n or "CURRENT" in n or n in ("MB_FAST_WATER", "MB_CYCLING_ROAD_WATER")}
    return surf - bad, names


SURFABLE, MB = _surfable_behaviors()


class Grid:
    """behavior / collision / elevation for every cell of the map the player is currently on"""

    def __init__(self, b):
        self.name = b.map_name()
        md = map_data(self.name)
        self.W, self.H = md["width"], md["height"]
        addr = lambda n: b.syms.call_addr(n)
        r = b.h.cmd("mapinfo 0 0 %d %d %d %d %d" % (self.W, self.H, addr("MapGridGetMetatileBehaviorAt"),
                                                    addr("MapGridGetCollisionAt"), addr("MapGridGetElevationAt")))
        toks = r.split()
        assert len(toks) == self.W * self.H, (len(toks), self.W * self.H)
        self.cells = {}
        i = 0
        for y in range(self.H):
            for x in range(self.W):
                t = toks[i]
                i += 1
                self.cells[(x, y)] = (int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16))
        self.objects = []
        for o in md["objects"]:
            self.objects.append(((o["x"], o["y"]), o.get("flag", "0")))
        self.warps = {(w["x"], w["y"]) for w in md["warps"]}

    def probe(self, b, x0, y0, w=1, h=1):
        """(behavior, collision, elevation) of cells anywhere on the grid including the margin beyond the map edge"""
        addr = lambda n: b.syms.call_addr(n)
        r = b.h.cmd("mapinfo %d %d %d %d %d %d %d" % (x0, y0, w, h, addr("MapGridGetMetatileBehaviorAt"),
                                                      addr("MapGridGetCollisionAt"), addr("MapGridGetElevationAt")))
        return [(int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16)) for t in r.split()]

    def inb(self, c):
        return 0 <= c[0] < self.W and 0 <= c[1] < self.H

    def surfable(self, c):
        return self.cells[c][0] in SURFABLE

    def walkable(self, c):
        return self.inb(c) and self.cells[c][1] == 0

    def can_step(self, a, bcell):
        if not self.walkable(bcell):
            return False
        return True


def mismatch(cur, tile):
    """IsElevationMismatchAt: 0 (transition) and 15 (multi-level, bridge decks) never block; else the elevations must match"""
    if cur == 0 or tile in (0, 15):
        return False
    return cur != tile


def next_elev(cur, tile):
    """ObjectEventUpdateElevation: the player takes the tile's elevation (0 included) except on multi-level tiles"""
    return cur if tile == 15 else tile


def bfs_elev(grid, start, elev, goal_fn, avoid=(), farthest_key=None):
    """BFS over (cell, player elevation) with the engine's rules: stepping onto a tile of a different non-0/15 elevation
    is blocked; the player's elevation follows the last non-0/15 tile. Returns the path to the first goal cell, or, with
    farthest_key, the path to the reachable cell that maximises farthest_key(cell). None if nothing."""
    st = (start, elev)
    prev = {st: None}
    q = deque([st])
    best = None
    while q:
        cur = q.popleft()
        c, e = cur
        if c != start and goal_fn(c):
            best = cur
            break
        if farthest_key and (best is None or farthest_key(c) > farthest_key(best[0])):
            best = cur
        for dx, dy in DIRV.values():
            n = (c[0] + dx, c[1] + dy)
            if n in avoid or not grid.walkable(n):
                continue
            eb = grid.cells[n][2]
            shore = grid.surfable(c) != grid.surfable(n)      # use Surf / stop surfing: the engine does not apply the elevation rule
            if not shore and mismatch(e, eb):
                continue
            ne = next_elev(e, eb)
            ns = (n, ne)
            if ns in prev:
                continue
            prev[ns] = cur
            q.append(ns)
    if best is None or best[0] == start:
        return None
    path = []
    cur = best
    while prev[cur] is not None:
        path.append(cur[0])
        cur = prev[cur]
    return path[::-1]


def bfs(grid, start, goal_fn, avoid=(), limit=4000):
    prev = {start: None}
    q = deque([start])
    while q:
        c = q.popleft()
        if c != start and goal_fn(c):
            path = []
            while c != start:
                path.append(c)
                c = prev[c]
            return path[::-1]
        for dx, dy in DIRV.values():
            n = (c[0] + dx, c[1] + dy)
            if n in prev or n in avoid or not grid.inb(n) or not grid.can_step(c, n):
                continue
            prev[n] = c
            q.append(n)
            if len(prev) > limit:
                return None
    return None


# ---------------------------------------------------------------- frames
def grab(b):
    p = b.out / "_frame.ppm"
    b.h.cmd("shot " + wsl_path(p))
    return np.array(Image.open(p).convert("RGB"))


def cells_of(frame):
    return frame.reshape(ROWS, 16, COLS, 16, 3).transpose(0, 2, 1, 3, 4)   # (row, col, 16, 16, 3)


def black_cells(frame):
    return int((cells_of(frame).max(axis=(2, 3, 4)) == 0).sum())


def strip_diff(A, B, d, region, T=20):
    """Compare frame A (before a step in direction d) with B (after it): B cell (r,c) shows what A showed at
    (r+dy, c+dx). `region` is 'front' (the cells ahead of the player in A), 'back' (the cells behind), or 'all'.
    Returns (fraction of compared cells whose mean abs difference exceeds T, number compared, list of (r,c) in B)."""
    dx, dy = DIRV[d]
    ca, cb = cells_of(A).astype(np.int16), cells_of(B).astype(np.int16)
    bad, tot, where = 0, 0, []
    for r in range(ROWS):
        for c in range(COLS):
            ar, ac = r + dy, c + dx                                   # where this world cell was in A
            if not (0 <= ar < ROWS and 0 <= ac < COLS):
                continue
            # skip the player sprite (2 tiles tall) in both frames
            if (r in (PLAYER_ROW - 1, PLAYER_ROW) and c == PLAYER_COL) or (ar in (PLAYER_ROW - 1, PLAYER_ROW) and ac == PLAYER_COL):
                continue
            ahead = (ac - PLAYER_COL) * dx + (ar - PLAYER_ROW) * dy       # >0: ahead of the player in A
            if region == "front" and ahead <= 0:
                continue
            if region == "back" and ahead >= 0:
                continue
            tot += 1
            # a cell counts as changed when a quarter of its pixels changed clearly (water ripples and sprites change less)
            if (np.abs(ca[ar, ac] - cb[r, c]).sum(axis=2) > 48).mean() > 0.25:
                bad += 1
                where.append((r, c))
    return (bad / tot if tot else 0.0), tot, where


# ---------------------------------------------------------------- images
def _label(img, text, xy=(2, 1)):
    d = ImageDraw.Draw(img)
    d.rectangle([xy[0] - 1, xy[1] - 1, xy[0] + 6 * len(text) + 1, xy[1] + 9], fill=(0, 0, 0))
    d.text(xy, text, fill=(255, 255, 120))


def filmstrip(frames, labels, path, cols=8, thumb=(120, 80), mark=()):
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb[0], rows * thumb[1]), (20, 20, 20))
    for i, (f, lab) in enumerate(zip(frames, labels)):
        im = Image.fromarray(f).resize(thumb, Image.BILINEAR)
        _label(im, lab)
        if i in mark:
            ImageDraw.Draw(im).rectangle([0, 0, thumb[0] - 1, thumb[1] - 1], outline=(255, 0, 0), width=2)
        sheet.paste(im, ((i % cols) * thumb[0], (i // cols) * thumb[1]))
    sheet.save(path)
    return path


def pair_image(A, B, d, where_front, path, title=""):
    """A (before) | B (after) at 1.5x, flagged front-strip cells outlined red on B"""
    sc = 1.5
    ia = Image.fromarray(A).resize((int(240 * sc), int(160 * sc)), Image.NEAREST)
    ib = Image.fromarray(B).resize((int(240 * sc), int(160 * sc)), Image.NEAREST)
    dr = ImageDraw.Draw(ib)
    for r, c in where_front:
        dr.rectangle([c * 16 * sc, r * 16 * sc, (c + 1) * 16 * sc - 1, (r + 1) * 16 * sc - 1], outline=(255, 0, 0), width=2)
    out = Image.new("RGB", (ia.width * 2 + 4, ia.height + 14), (20, 20, 20))
    out.paste(ia, (0, 14))
    out.paste(ib, (ia.width + 4, 14))
    ImageDraw.Draw(out).text((2, 2), "before | after  " + title, fill=(255, 255, 120))
    out.save(path)
    return path

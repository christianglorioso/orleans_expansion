"""The Old Water (Rootkin village), polished by hand from the approved layout (mockup 10_old_water.png): 50 x 42 on the
orleans_bayou tileset (shared with Isle Marais and Route 1 since the seams review) (demand-driven, palette v2).

usage (from the decomp root):
    python -W ignore tools/mapgen/old_water.py [--ascii] [--dry-run] [--no-build] [--review]
Wrap it in `buildlock.py acquire/release old_water` when it writes data/ (every run without --dry-run does).

What it writes: maps/old_water.grid.txt (terrain: ~ water, " marsh, . lawn, : trodden-earth path) and the spec's
`buildings` list. The huts, song house, shrine stone and rope walkways keep the approved positions (they are read
from the spec and never moved); the vegetation (cypress, reeds, snags, logs) is re-checked against the new terrain
and nudged only where it no longer fits. Events (NPCs, item, sign) stay as they are.

Design (x right, y down):
  islands  every island is a union of rounded rectangles with low-frequency noise on its outline, so shores are
           lobed and scalloped, with a few hand-placed coves and spits; each stands alone in open water.
  lawns    the darker grass cores: each hut's yard, plus a one-cell margin round every path (a path needs grass on
           every side, never marsh or water: the marsh/water bank pieces are drawn in the cell beside them).
  paths    trodden-earth tracks (the packed-mud path set), 2 wide, with chamfered ends and one-cell bulges, from
           every door to the walkway landing(s) of its island.
  marsh    the rest of each island: thick on the sides away from the paths, where the cypress and reeds stand.
Edit this file, never maps/old_water.grid.txt.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "maps", "old_water.json")
GRID = os.path.join(HERE, "maps", "old_water.grid.txt")
W, H = 50, 42
YY, XX = np.mgrid[0:H, 0:W]
CX_, CY_ = XX + 0.5, YY + 0.5

NOBUF = os.environ.get('OW_NOBUF') == '1'
VEG = ("cypress_marsh", "cypress_small_marsh", "cypress_water", "cypress_small_water", "waterlog", "snag_water",
       "reeds_marsh")


# ---------------------------------------------------------------- shapes
def rrect(cx, cy, hx, hy, r):
    qx = np.abs(CX_ - cx) - (hx - r)
    qy = np.abs(CY_ - cy) - (hy - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def noise(seed, amp):
    rng = np.random.RandomState(seed)
    n = np.zeros((H, W))
    for k in range(5):
        wl = rng.uniform(3.2, 9.0)
        a = rng.uniform(0, math.pi)
        ph = rng.uniform(0, 2 * math.pi)
        n += math.sin(0) + np.sin((CX_ * math.cos(a) + CY_ * math.sin(a)) * 2 * math.pi / wl + ph)
    return n / 5 * amp * 1.9


def ell(cx, cy, rx, ry):
    return ((CX_ - cx) / rx) ** 2 + ((CY_ - cy) / ry) ** 2 <= 1.0


def box(x0, y0, x1, y1):
    return (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1)


def island(discs, seed, amp=0.45, force=(), room=None):
    """An island as a union of discs (x, y, r) in cell-edge coordinates: scalloped, lobed shores with natural coves where
    the discs meet, plus a little low-frequency noise. room: (x0, y0, x1, y1) it may not leave, so neighbours never touch."""
    sdf = np.min([np.hypot(CX_ - x, CY_ - y) - r for x, y, r in discs], axis=0) + noise(seed, amp)
    m = sdf < 0
    if room:
        m &= box(*room)
    for f in force:
        m |= box(*f)
    return m


def shore_features(m, protect, others, seed, gap=4, coves=0.45):
    """Hand-made-looking small features on an island's shore: coves (disc bitten out of the shore) and bumps (a disc
    added just outside it), spaced out, never within the protected cells (paths, lawns, landings) and never closer than
    two cells of water to another island (others)."""
    rng = np.random.RandomState(seed)
    m = m.copy()
    edge = m & ~erode(m, 1)
    pts = [(x, y) for y, x in zip(*np.nonzero(edge)) if sum(m[y + dy, x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                                              if 0 <= y + dy < H and 0 <= x + dx < W) < 4]
    rng.shuffle(pts)
    done = []
    for x, y in pts:
        if any(abs(x - a) + abs(y - b) < gap for a, b in done):
            continue
        if rng.rand() < coves:
            r = rng.uniform(1.0, 1.7)
            d = (np.hypot(CX_ - (x + 0.5), CY_ - (y + 0.5)) <= r) & m
            if (d & protect).any() or d.sum() > 9:
                continue
            m &= ~d
        else:
            # a bump pushes outward: centre one cell out along the shore normal (towards the nearest water)
            nx = sum(1 for dx in (-1, 1) if 0 <= x + dx < W and not m[y, x + dx] for _ in [0]) * 0
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < W and 0 <= y + dy < H and not m[y + dy, x + dx]:
                    best = (dx, dy)
                    break
            if not best:
                continue
            r = rng.uniform(1.2, 2.0)
            cx, cy = x + 0.5 + best[0] * 1.0, y + 0.5 + best[1] * 1.0
            d = np.hypot(CX_ - cx, CY_ - cy) <= r
            if (d & dilate(others, 2)).any() or (d & dilate(protect, 0)).any():
                continue
            m |= d
        done.append((x, y))
    return m


def left_edge(rows):
    """A bank along the east edge from the x of its west shore, per row (a few cells deep, the shore stepping in and out)."""
    m = np.zeros((H, W), bool)
    for y, x0 in rows.items():
        m[y, x0:] = True
    return m


def prect(x0, y0, x1, y1, cut=""):
    m = box(x0, y0, x1, y1)
    for c in cut.split():
        cx = x0 if "w" in c else x1
        cy = y0 if "n" in c else y1
        m[cy, cx] = False
    return m


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def dilate_cross(m, r=1):
    """Dilation by a plus-shaped kernel: rounds the corners a square kernel would keep."""
    out = m.copy()
    for k in range(r):
        out = out | np.roll(out, 1, 0) | np.roll(out, -1, 0) | np.roll(out, 1, 1) | np.roll(out, -1, 1)
    return out


def edt(m):
    """Distance from every cell centre to the nearest cell of m (brute force: the masks are small)."""
    ys, xs = np.nonzero(m)
    if not len(xs):
        return np.full((H, W), 99.0)
    d = np.full((H, W), 99.0)
    for x, y in zip(xs, ys):
        d = np.minimum(d, np.hypot(XX - x, YY - y))
    return d


def blur01(seed, wl=(2.5, 5.0)):
    """Smooth noise in 0..1 (a few sines): used to make a margin's width wander."""
    rng = np.random.RandomState(seed)
    n = np.zeros((H, W))
    for k in range(4):
        w = rng.uniform(*wl)
        a = rng.uniform(0, math.pi)
        n += np.sin((CX_ * math.cos(a) + CY_ * math.sin(a)) * 2 * math.pi / w + rng.uniform(0, 2 * math.pi))
    n = n / 4
    return np.clip(n * 1.4 * 0.5 + 0.5, 0, 1)


def erode(m, r=1):
    return ~dilate(~m, r)


def majority(m, rounds=1):
    for _ in range(rounds):
        n = sum(np.roll(np.roll(m, dy, 0), dx, 1).astype(int) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        m = np.where(n >= 6, True, np.where(n <= 3, False, m))
    return m


def components(m):
    seen = np.zeros_like(m)
    out = []
    for y in range(H):
        for x in range(W):
            if m[y, x] and not seen[y, x]:
                st, comp = [(x, y)], []
                seen[y, x] = True
                while st:
                    a, b = st.pop()
                    comp.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        i, j = a + da, b + db
                        if 0 <= i < W and 0 <= j < H and m[j, i] and not seen[j, i]:
                            seen[j, i] = True
                            st.append((i, j))
                out.append(comp)
    return out


# ---------------------------------------------------------------- the spec's fixed pieces
def load_spec():
    spec = json.load(open(SPEC, encoding="utf-8"))
    spec["buildings"] = [b for b in spec["buildings"] if b.get("label") != "Seam reeds"]   # re-laid every run
    return spec


def walk_ends(spec):
    """Deck cells at each end of every walkway (the first and last row/column), as lists of (x, y)."""
    out = []
    for b in spec["buildings"]:
        p = b["prefab"]
        if p.startswith("walk_v"):
            n = int(p[6:])
            out.append(("v", b["label"], [(b["x"] + i, b["y"]) for i in range(3)],
                        [(b["x"] + i, b["y"] + n - 1) for i in range(3)]))
        elif p.startswith("walk_h"):
            n = int(p[6:])
            out.append(("h", b["label"], [(b["x"], b["y"] + j) for j in range(2)],
                        [(b["x"] + n - 1, b["y"] + j) for j in range(2)]))
    return out


HUTS = {  # label -> (x, y, w, h): the yard is the footprint plus one column right and one row below
    "Healer": (15, 4, 3, 4), "Song house": (21, 3, 5, 5), "Trader": (28, 4, 3, 4),
    "Carver's workshop": (6, 16, 3, 4), "Tupelo's house": (37, 15, 3, 4), "Rest house (bed)": (42, 15, 2, 4),
    "Wren's house": (39, 28, 3, 4), "Canoe docks": (23, 31, 3, 4),
}


# ---------------------------------------------------------------- the islands
ROUTE_GRID = os.path.join(HERE, "maps", "route_1.grid.txt")
ROUTE_DY = 15      # our row = Route 1's row + 15 (the connection offset)


def route_edge():
    """Route 1's west column, per row of ours it reaches: [(our row, kind)], kind '.' grass, '"' marsh (tall grass counts
    as marsh: the village set has no tall grass), '~' water. Read from the built grid, so the seam follows Route 1."""
    g = [l.rstrip(chr(10)) for l in open(ROUTE_GRID, encoding="utf-8")]
    out = []
    for ry, row in enumerate(g):
        y = ry + ROUTE_DY
        if y >= H:
            break
        c = row[0]
        out.append((y, "~" if c == "~" else '"' if c in '"G' else "."))
    return out


def edge_runs():
    runs, cur = [], None
    for y, k in route_edge():
        if k == "~":
            cur = None
        elif cur is None:
            cur = [y, y]
            runs.append(cur)
        else:
            cur[1] = y
    return [tuple(r) for r in runs]


BANKS = edge_runs()

# (new char, x0, y0, x1, y1): every marsh cell in the box becomes that character
FIXES = []

BANK_ROOMS = {f"bank{i}": (47 if i == 0 else 46, y0, 49, y1) for i, (y0, y1) in enumerate(BANKS)}
ROOMS = {"north": (4, 1, 40, 11), "west": (1, 14, 14, 23), "east": (31, 14, 45, 22), "sw": (1, 27, 15, 38),
         "south": (18, 28, 31, 39), "se": (34, 26, 43, 37), "shrine": (40, 2, 47, 8)}
ROOMS.update(BANK_ROOMS)


def marsh_mask(ends):
    forced = []
    for kind, label, a, b in ends:
        for cells in (a, b):
            for x, y in cells:
                forced.append((x, y, x, y))
    isl = {}
    isl["north"] = island([(11.3, 8.6, 3.0), (15.8, 5.9, 3.6), (19.6, 8.0, 3.8), (23.5, 6.6, 4.9), (27.6, 5.8, 3.4),
                           (29.5, 8.4, 3.6), (32.6, 6.8, 3.5), (34.6, 9.0, 2.8), (36.2, 5.4, 1.9), (16.5, 10.0, 1.9),
                           (25.8, 10.4, 2.0), (8.0, 6.8, 2.6), (11.5, 4.2, 2.4), (19.8, 3.0, 2.2), (37.2, 6.5, 2.4)], seed=11, room=(6, 1, 39, 11))
    isl["west"] = island([(6.0, 17.5, 3.8), (10.2, 16.8, 3.6), (5.5, 20.8, 3.0), (9.0, 20.6, 3.1), (11.5, 18.5, 2.6),
                          (3.6, 19.0, 2.3), (3.0, 18.3, 3.0)], seed=23, room=(1, 14, 14, 23))
    isl["east"] = island([(36.0, 17.5, 3.3), (40.0, 18.2, 3.8), (42.6, 17.6, 3.2), (38.5, 20.5, 2.6), (42.5, 20.8, 2.5),
                          (35.2, 15.6, 2.0), (43.4, 19.8, 1.9), (43.8, 18.6, 2.0)], seed=37, room=(31, 14, 47, 22))
    isl["sw"] = island([(7.0, 30.0, 3.4), (4.8, 33.0, 3.2), (9.5, 33.2, 3.5), (7.2, 35.2, 2.6), (12.0, 32.4, 2.4),
                        (11.8, 29.6, 2.0), (4.4, 33.5, 3.4), (7.0, 36.2, 2.4)], seed=41, room=(1, 27, 15, 37))
    isl["south"] = island([(22.0, 31.5, 3.2), (25.5, 32.5, 4.0), (28.5, 31.0, 2.6), (21.8, 35.0, 3.3), (25.0, 35.8, 3.5),
                           (28.2, 35.0, 3.0), (24.8, 37.4, 3.2)], seed=53, room=(18, 28, 31, 38))
    isl["se"] = island([(38.2, 29.4, 3.2), (40.8, 29.0, 3.0), (41.0, 31.0, 2.4), (38.0, 33.4, 3.3), (40.8, 33.4, 3.3),
                        (40.4, 34.6, 2.2), (36.8, 31.5, 2.0), (40.8, 31.6, 2.3), (40.0, 36.0, 2.2), (38.5, 27.0, 2.2)], seed=67, room=(34, 26, 47, 36))
    # the Route 1 shore: land along the east edge where Route 1's west column is land (its rows 0-5 and 12-26 = ours 15-20
    # and 27-41), open water for the channel (ours 21-26); lobed banks a few cells deep
    for i, (y0, y1) in enumerate(BANKS):       # a few cells deep, the west shore stepping in and out a cell at a time
        rng = np.random.RandomState(90 + i)
        xmin, d = (47 if i == 0 else 46), 2
        rows = {}
        for y in range(y0, y1 + 1):
            d = int(np.clip(d + rng.choice([-1, 0, 0, 1]), 0, 3))
            rows[y] = max(xmin, 48 - d - (1 if y in (y0, y1) else 0) + (1 if y in (y0, y1) else 0))
        isl[f"bank{i}"] = left_edge(rows)
    isl["shrine"] = island([(43.0, 4.6, 2.1), (44.8, 5.4, 1.4)], seed=71, amp=0.3, room=(40, 2, 47, 8))
    return isl, forced


def stroke(pts, r=1.05):
    """Cells within r of a polyline (cell-edge coordinates): a soft, slightly uneven track, 2-3 cells wide."""
    d = np.full((H, W), 99.0)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        L2 = vx * vx + vy * vy or 1e-9
        t = np.clip(((CX_ - x0) * vx + (CY_ - y0) * vy) / L2, 0, 1)
        d = np.minimum(d, np.hypot(CX_ - (x0 + t * vx), CY_ - (y0 + t * vy)))
    return d <= r


def neat(p, keep):
    """Fill 1-cell notches, drop 1-cell spurs and give every path cell a full 2x2 block (what the path set draws well)."""
    for _ in range(8):
        n = (np.roll(p, 1, 0).astype(int) + np.roll(p, -1, 0) + np.roll(p, 1, 1) + np.roll(p, -1, 1))
        add = ~p & (n >= 3)
        spur = p & (n <= 1) & ~keep
        if not add.any() and not spur.any():
            break
        p = (p | add) & ~spur
    for _ in range(4):
        blk = np.zeros_like(p)
        for dy in (0, 1):
            for dx in (0, 1):
                full = p & np.roll(p, -1, 0) & np.roll(p, -1, 1) & np.roll(np.roll(p, -1, 0), -1, 1)
                blk |= np.roll(np.roll(full, dy, 0), dx, 1)
        bad = p & ~blk
        if not bad.any():
            break
        for y, x in zip(*np.nonzero(bad)):     # grow towards the neighbour with the most path around it
            best, bs = None, -1
            for ox in (-1, 0):
                for oy in (-1, 0):
                    cells = [(x + ox + i, y + oy + j) for i in (0, 1) for j in (0, 1)]
                    if any(not (0 <= a < W and 0 <= b < H) for a, b in cells):
                        continue
                    sc = sum(p[b, a] for a, b in cells)
                    if sc > bs:
                        best, bs = cells, sc
            if best:
                for a, b in best:
                    p[b, a] = True
    return p


def tidy(p, lawn, protect):
    """Hill-climb the track's outline with the path autotile's own scoring (natural.Shape): single-row steps, inner
    corners crowding outer ones and the like draw as hard seams, so toggle cells while the drawing gets better.
    Cells may only be added where all eight neighbours are lawn or path (the grass shoulder stays whole); `protect`
    cells (landings, door fronts) never change."""
    import natural
    rng = np.random.RandomState(3)
    inner = erode(lawn | p, 1)

    def grid_of(m):
        return ["".join(":" if m[y, x] else "." for x in range(W)) for y in range(H)]

    S = natural.Shape(grid_of(p))

    def local(x, y):
        return [(i, j) for i in range(x - 2, x + 3) for j in range(y - 2, y + 3) if 0 <= i < W and 0 <= j < H]

    def two_wide_ok(m, x, y):
        for i, j in [(a, b) for a in range(x - 1, x + 2) for b in range(y - 1, y + 2)]:
            if 0 <= i < W and 0 <= j < H and m[j, i] and not any(
                    all(0 <= i + a + u < W and 0 <= j + b + v < H and m[j + b + v, i + a + u] for u in (0, 1) for v in (0, 1))
                    for a in (-1, 0) for b in (-1, 0)):
                return False
        return True

    for sweep in range(12):
        cells = [(x, y) for y in range(H) for x in range(W)
                 if (p[y, x] or (inner[y, x] and dilate(p, 1)[y, x])) and (x, y) not in protect]
        rng.shuffle(cells)
        changed = 0
        for x, y in cells:
            if p[y, x] and False:
                continue
            area = local(x, y)
            before = S.region_bad(area)
            new = not p[y, x]
            p[y, x] = new
            S.g[y][x] = ":" if new else "."
            if S.region_bad(area) < before and two_wide_ok(p, x, y):
                changed += 1
            else:
                p[y, x] = not new
                S.g[y][x] = ":" if not new else "."
        if not changed:
            break
    return p


def paths():
    return np.zeros((H, W), bool)   # the tracks were dropped (user preferred the look without them)


def paths_old():
    p = np.zeros((H, W), bool)
    keep = np.zeros((H, W), bool)
    # north: the trunk from the north-west landing to the north-east one, a plaza under the song house
    p |= stroke([(10.0, 9.0), (13.0, 8.9), (16.5, 9.1), (19.0, 9.7), (21.5, 9.4), (23.5, 9.2), (27.0, 9.1), (30.0, 8.9),
                 (32.5, 9.4), (36.0, 9.0)])
    p |= prect(10, 8, 12, 9, "nw") | prect(34, 8, 36, 9, "ne")
    p |= ell(23.5, 9.5, 2.5, 1.6)
    # worn bulges on alternating sides of the long run (natural.py's trick): two cells, one cell deep
    p |= prect(14, 10, 15, 10) | prect(18, 7, 19, 7) | prect(28, 10, 29, 10) | prect(31, 7, 32, 7)
    # west (Carver): from the north-west walkway's foot round the east side of the hut to its door and the west walkway
    p |= stroke([(11.0, 17.0), (11.0, 18.0), (10.4, 19.6), (9.2, 20.7), (7.5, 21.0)])
    p |= prect(10, 16, 12, 16, "") | prect(6, 20, 9, 21, "nw")
    # east (Tupelo, Rest house): down from the north-east walkway's foot, then east along both doors
    p |= stroke([(35.0, 16.0), (35.0, 17.0), (35.6, 19.0), (38.0, 20.0), (43.5, 20.0)], 1.1)
    p |= prect(34, 15, 35, 16, "")
    # south-west garden: from the west walkway's foot to the south-west walkway
    p |= stroke([(7.0, 29.0), (7.6, 30.0), (9.0, 31.4), (11.5, 32.6)])
    p |= prect(6, 28, 8, 28, "") | prect(10, 32, 11, 33, "")
    # south (canoe docks): a U round the hut from the south-west landing to the south-east one
    p |= stroke([(21.7, 32.0), (21.7, 34.5), (22.7, 36.0), (25.0, 36.3), (27.3, 36.0), (28.3, 34.5), (28.3, 32.0)])
    p |= prect(21, 32, 22, 33, "") | prect(27, 32, 28, 33, "")
    # south-east (Wren): a short track from the south-east walkway to the door and a small apron
    p |= stroke([(38.0, 33.0), (40.0, 33.0), (42.0, 33.2)], 1.1) | ell(40.5, 33.3, 2.2, 1.5)
    p |= prect(37, 32, 38, 33, "")
    return neat(p, keep)


def lawns(path, ends):
    lw = np.zeros((H, W), bool)
    for label, (x, y, w, h) in HUTS.items():
        lw |= box(x, y, x + w, y + h)
    return lw


def build():
    spec = load_spec()
    ends = walk_ends(spec)
    isl, forced = marsh_mask(ends)
    path = paths()
    lawn = lawns(path, ends)
    fm = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in forced:
        fm[y0, x0] = True
    protect = dilate(lawn | path | fm, 1)
    isl = {k: majority(m) for k, m in isl.items()}
    for i, k in enumerate(isl):
        others = np.zeros((H, W), bool)
        for k2, m2 in isl.items():
            if k2 != k:
                others |= m2
        room = ROOMS[k]
        m = isl[k] if k == "shrine" or k.startswith("bank") else shore_features(isl[k], protect, others, 100 + i)
        isl[k] = m & box(*room) | (isl[k] & ~box(*room))
    marsh = np.zeros((H, W), bool)
    for m in isl.values():
        marsh |= m
    for x0, y0, x1, y1 in forced:
        marsh[y0, x0] = True
    # the yards keep a marsh border (as the original had)
    rim = dilate(lawn, 1)
    inroom = np.zeros((H, W), bool)
    for k, room in ROOMS.items():
        inroom |= box(*room)
    marsh |= rim & inroom
    lawn &= inroom
    # the deck between a walkway's two ends floats over open water: nothing but water under it
    deck = np.zeros((H, W), bool)
    for b in spec["buildings"]:
        n = int(b["prefab"][6:]) if b["prefab"].startswith(("walk_v", "walk_h")) else 0
        if b["prefab"].startswith("walk_v"):
            deck |= box(b["x"], b["y"] + 1, b["x"] + 2, b["y"] + n - 2)
        elif b["prefab"].startswith("walk_h"):
            deck |= box(b["x"] + 1, b["y"], b["x"] + n - 2, b["y"] + 1)
    marsh &= ~deck
    lawn &= ~deck
    path &= ~deck
    cs = components(marsh)
    if len([c for c in cs if len(c) >= 8]) != 7 + len(BANKS):
        print("WARNING: islands merged or split:", [(len(c), min(x for x, y in c), min(y for x, y in c)) for c in cs])
    for comp in components(marsh):
        if len(comp) < 12:
            for x, y in comp:
                marsh[y, x] = False
    fm2 = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in forced:
        fm2[y0, x0] = True
    for _ in range(3):    # one-cell spurs and notches in the shore
        n = (np.roll(marsh, 1, 0).astype(int) + np.roll(marsh, -1, 0) + np.roll(marsh, 1, 1) + np.roll(marsh, -1, 1))
        marsh = (marsh & ~((n <= 1) & ~fm2 & ~lawn)) | (~marsh & (n >= 3) & ~deck)
    grid = np.full((H, W), "~", dtype="<U1")
    grid[marsh] = '"'
    grid[lawn] = "."
    grid[path] = ":"
    # Route 1's column x0 meets our x = 49: grass in its rows 0-5 and 12-21, marsh in 22-26. Banks: marsh ring, grass core
    # in the grass rows (the core runs to the edge so the seam is grass on grass), plain marsh in the marsh rows.
    bank = np.zeros((H, W), bool)
    for k in BANK_ROOMS:
        bank |= marsh & box(*ROOMS[k])
    padded = np.pad(bank, 1, constant_values=False)
    padded[:, -1] = True
    padded[:, -1][0] = False
    core = bank & erode(padded, 1)[1:-1, 1:-1]
    core[:, 49] = bank[:, 49]
    kind = dict(route_edge())
    for y in range(H):
        for x in range(W):
            if bank[y, x]:
                grid[y, x] = "." if (core[y, x] and kind.get(y) == ".") else '"'
    for ch, x0, y0, x1, y1 in FIXES:          # hand fixes for the odd three-terrain corner the autotiles can't blend
        sub = grid[y0:y1 + 1, x0:x1 + 1]
        sub[sub == '"'] = ch
    return spec, grid, ends


def prefab_sizes():
    cfg = json.load(open(os.path.join(HERE, "tilesets", "orleans_bayou.json"), encoding="utf-8"))
    pm = load_spec().get("prefab_map", {})          # the rope walkways keep their own names on the shared bayou tileset
    out = {k: (len(v["rows"][0]), len(v["rows"])) for k, v in cfg["prefabs"].items()}
    out.update({k: out[v] for k, v in pm.items()})
    return out


def reconcile(spec, grid):
    """Keep every cypress/reed/snag/log where it fits the new terrain, move the rest to the nearest spot that does."""
    sizes = prefab_sizes()
    fixed = [b for b in spec["buildings"] if b["prefab"] not in VEG]
    veg = [b for b in spec["buildings"] if b["prefab"] in VEG]
    at = lambda x, y: grid[y][x] if 0 <= x < W and 0 <= y < H else None
    taken = set()          # cells no tree may use
    near = set()           # cells a tree body must keep one cell clear of (buildings, walkways, events, paths)
    for b in fixed:
        w, h = sizes[b["prefab"]]
        cells = {(b["x"] + i, b["y"] + j) for i in range(w) for j in range(h)}
        if b["prefab"].startswith(("hut", "songhouse", "walk")):
            near |= cells
        taken |= cells
    for o in list(spec.get("objects", [])) + list(spec.get("items", [])) + list(spec.get("signs", [])):
        near.add((o["x"], o["y"]))
    for y in range(H):
        for x in range(W):
            if grid[y][x] in ":.":
                near.add((x, y)) if grid[y][x] == ":" else None
    # the hidden channel in from the east edge must stay open
    channel = {(x, y) for x in range(38, W) for y in range(19, 30)}

    def body(kind, x, y):
        w, h = sizes[kind]
        return {(x + i, y + j) for i in range(w) for j in range(h)}

    def ring(cells, r):
        return {(a + i, b + j) for a, b in cells for i in range(-r, r + 1) for j in range(-r, r + 1)}

    def ok(kind, x, y, occ):
        w, h = sizes[kind]
        want = '"' if kind.endswith("_marsh") else "~"
        if x < 0 or y < 0 or x + w >= W + (0 if want == '"' else 1) or y + h > H:
            return False
        if kind.startswith("cypress") and (x < 1 or y < 1 or x + w > W - 1 or y + h > H - 1):
            return False        # a tree never stands against the map edge: a cell of open water beyond it
        for j in range(y, y + h + 1):          # the dual-grid block: one more column and row than the body
            for i in range(x, x + w + 1):
                if at(i, j) != want and not (want == "~" and i >= W):
                    return False
        cells = body(kind, x, y)
        if cells & occ:
            return False
        if want == '"':
            if ring(cells, 1) & near:
                return False
        else:
            if cells & channel or ring(cells, 1) & (near - {c for c in near if at(*c) == ":"}):
                return False
        return True

    rng = np.random.RandomState(4)
    placed, moved, dropped = [], [], []
    occ = set(taken)
    todo = []
    for b in veg:
        if ok(b["prefab"], b["x"], b["y"], occ):
            occ |= body(b["prefab"], b["x"], b["y"])
            placed.append(b)
        else:
            todo.append(b)
    for b in todo:
        best = None
        for spacing in (True, False):
            for r in range(1, 40):
                cands = [(b["x"] + dx, b["y"] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                         if max(abs(dx), abs(dy)) == r]
                cands.sort(key=lambda c: abs(c[0] - b["x"]) + abs(c[1] - b["y"]) + rng.uniform(0, 3.0))
                for x, y in cands:
                    if not ok(b["prefab"], x, y, occ):
                        continue
                    if spacing and b["prefab"] == "reeds_marsh" and any(
                            q["prefab"] == "reeds_marsh" and max(abs(q["x"] - x), abs(q["y"] - y)) < 3
                            for q in placed):
                        continue
                    best = (x, y)
                    break
                if best:
                    break
            if best:
                break
        if best:
            nb = dict(b, x=best[0], y=best[1])
            occ |= body(b["prefab"], *best)
            placed.append(nb)
            moved.append((b["prefab"], (b["x"], b["y"]), best))
        else:
            dropped.append((b["prefab"], (b["x"], b["y"])))
    # rows of trees at one height read as a fence: let the members of a long row drift a cell here and there
    rows = {}
    for i, b in enumerate(placed):
        if b["prefab"] in ("cypress_water", "cypress_small_water"):
            rows.setdefault(b["y"], []).append(i)
    for y, idx in rows.items():
        if len(idx) < 4:
            continue
        for i in idx:
            b = placed[i]
            occ -= body(b["prefab"], b["x"], b["y"])
            opts = [(0, 0)] + [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
            rng.shuffle(opts)
            for dx, dy in [(0, 0)] * (1 if rng.rand() < 0.3 else 0) + opts:
                if ok(b["prefab"], b["x"] + dx, b["y"] + dy, occ):
                    placed[i] = dict(b, x=b["x"] + dx, y=b["y"] + dy)
                    break
            nb = placed[i]
            occ |= body(nb["prefab"], nb["x"], nb["y"])
    return fixed + placed, moved, dropped


def verify(grid, spec, ends):
    """On-foot reachability over grass and marsh: every door front, NPC, item and walkway landing is reachable from the
    first door's front (walkway decks count as walkable between their two ends)."""
    g = grid
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and g[y][x] != "~"
    deck = set()
    for b in spec["buildings"]:
        n = int(b["prefab"][6:]) if b["prefab"].startswith(("walk_v", "walk_h")) else 0
        if b["prefab"].startswith("walk_v"):
            deck |= {(b["x"] + i, b["y"] + j) for i in range(3) for j in range(n)}
        elif b["prefab"].startswith("walk_h"):
            deck |= {(b["x"] + i, b["y"] + j) for i in range(n) for j in range(2)}
    ok = lambda x, y: walk(x, y) or (x, y) in deck
    fronts = {lb: (x + w // 2, y + h) for lb, (x, y, w, h) in HUTS.items()}
    start = fronts["Healer"]
    seen, st = {start}, [start]
    while st:
        a, b = st.pop()
        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (a + da, b + db)
            if c not in seen and ok(*c):
                seen.add(c)
                st.append(c)
    targets = dict(fronts)
    for o in list(spec.get("objects", [])) + list(spec.get("items", [])):
        targets[o.get("id") or o.get("item")] = (o["x"], o["y"])
    miss = [k for k, c in targets.items() if c not in seen]
    print("  on-foot reachability from the Healer's door:", "all doors, NPCs and the item reachable" if not miss else f"UNREACHABLE {miss}")
    return not miss


def lawn_forced(ends):
    m = np.zeros((H, W), bool)
    for kind, label, a, b in ends:
        for cells in (a, b):
            for x, y in cells:
                m[y, x] = True
    return m


def ascii_map(grid, spec):
    g = [list(r) for r in grid]
    for b in spec["buildings"]:
        pass
    return "\n".join("%2d %s" % (y, "".join(r)) for y, r in enumerate(g))


SCRATCH = "C:/Users/chris/AppData/Local/Temp/claude/C--Users-chris-orleans-expansion/9db27ca2-6d98-400d-94d8-6894eb875d80/scratchpad"


def main(args):
    spec, grid, ends = build()
    rows = ["".join(r) for r in grid]
    verify(["".join(r) for r in grid], spec, ends)
    buildings, moved, dropped = reconcile(spec, grid)
    # The banks must not be a way in on foot: a belt of dense reeds along the seam column (x = 49), and every land cell of
    # that column made impassable (spec "block"), so Route 1's land stops at the seam. Only the channel leads in.
    taken = set()
    for b in buildings:
        w, h = prefab_sizes()[b["prefab"]]
        taken |= {(b["x"] + i, b["y"] + j) for i in range(w) for j in range(h)}
    belt, block = [], [[W - 1, y] for y in range(H) if grid[y][W - 1] != "~"]
    for y0, y1 in BANKS:
        y = y0
        while y <= y1:
            yy = min(y, y1 - 1)
            if all(grid[j][i] == '"' for j in (yy, yy + 1, yy + 2) for i in (W - 2, W - 1) if j < H) and not ({(W - 1, yy), (W - 1, yy + 1)} & taken):
                belt.append({"prefab": "reeds_marsh", "x": W - 1, "y": yy, "label": "Seam reeds"})
                taken |= {(W - 1, yy), (W - 1, yy + 1)}
            y += 2
    spec = dict(spec, buildings=buildings + belt, block=block)
    print(f"seam belt: {len(belt)} reed pairs, {len(block)} blocked cells")
    print(f"vegetation: {len(moved)} moved, {len(dropped)} dropped", dropped)
    if "--ascii" in args:
        print("   " + "".join(str(i % 10) for i in range(W)))
        print(ascii_map(grid, spec))
    if "--dev" in args:   # preview without touching maps/: a scratch copy of the spec pointing at a scratch grid
        gp = SCRATCH + "/ow_dev.grid.txt"
        open(gp, "w").write("\n".join(rows) + "\n")
        sp = dict(spec, grid=gp, edits=[])
        json.dump(sp, open(SCRATCH + "/ow_dev.json", "w", encoding="utf-8"))
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), SCRATCH + "/ow_dev.json",
                            "--dry-run", "--preview", SCRATCH + "/ow_dev_preview.png"], capture_output=True, text=True)
        print(r.stdout.strip()[-600:], r.stderr.strip()[-1500:])
        return
    if "--dry-run" in args:
        return
    with open(GRID, "w", newline="\n") as f:
        f.write("\n".join(rows) + "\n")
    out = dict(spec, edits=[], _comment="The Old Water, polished by hand: generated by old_water.py (edit that, not this "
                                        "file or the grid).")
    out["_exits"] = ("Reached by water: the hidden channel enters from the east edge (the rows Route 1 has water in, "
                     "connection offset 15); no exit on foot.")
    out = {k: out[k] for k in ["_comment"] + [k for k in out if k != "_comment"]}
    with open(SPEC, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", GRID, "and", SPEC)


if __name__ == "__main__":
    main(sys.argv[1:])

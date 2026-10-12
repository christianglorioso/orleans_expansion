"""Route 1 polish pass (slice polish, 2026-10-12): rewrites maps/route_1.json + .grid.txt from the approved original
(maps/route_1.base.json + route_1.base.grid.txt, kept untouched) with:

  * the road: still 2 wide, now meandering (x 14-15 at the Grand Oak end, 15-16 along the boat landing, 14-15, 13-14 at
    the Isle Marais end). Every 1-column shift is a two-row bevel (3 wide), so natural.total_bad stays 0 (the path
    autotile draws it all). A one-cell plain-grass verge each side, everywhere;
  * tall grass with organic outlines: the old blocks' coverage, re-cut with a smooth noise field (rounded bays and
    points, loose clumps) instead of stair-stepped rectangles;
  * the west edge is the original's: land, marsh and groves along x 0, and the channel (rows 6-13, the Surf exit to the Old
    Water) open to the edge exactly as before. The south-west pond is its own pond again (the user asked for the channel
    to stay closed everywhere else);
  * the south end: two bays of water narrow towards the causeway over the last rows and the banks close, so the seam
    with Isle Marais's grass top row (and its marsh at x 0) has a shore. The pirogue's mud bar is three rows further
    up to leave room for the bank, and the islet moved one row up with it;
  * the east marsh bay has a wavier west edge; the west groves are the original's (two groves moved to fit).

The pier, the shrine, the islet, the events, items, triggers and both road exits are the original's. Takes no lock itself:
    python tools/mapgen/buildlock.py acquire route_1
    python -W ignore tools/mapgen/route_1.py [--out DIR] [--ascii]
    ... build.py / compose.py / check.py as the README says (the tileset is shared: see "Route tilesets") ...
    python tools/mapgen/buildlock.py release route_1
Edit this file, not maps/route_1.json. --out DIR writes the spec and grid there instead (nothing in data/ is touched).
"""
import copy
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import natural  # noqa: E402

MAPS = os.path.join(HERE, "maps")
W, H = 28, 48
KEY = "route_1"
SEED = 11

# --- the road: the left column of the 2-wide road by row; a shift of one column is two rows of 3-wide road
SHIFTS = [(22, 13)]     # (first row of the 3-wide pair, new left column); it starts at x = 14
ROAD_START = 14

# --- terrain: ~ water, " marsh, L mud, . ground (the road and the tall grass are laid on it); see terrain_rows()


def spans(*segs):
    """A row from (char, count) segments."""
    row = "".join(c * n for c, n in segs)
    assert len(row) == W, (len(row), row)
    return row


def terrain_rows():
    s = spans
    R = []
    R.append(s((".", 28)))                                                                  # 0 lawn, like Grand Oak's last row
    R.append(s(('"', 11), (".", 11), ('"', 6)))                                             # 1
    R.append(s(('"', 11), (".", 11), ('"', 6)))                                             # 2
    R.append(s(('"', 11), (".", 8), ('"', 9)))                                              # 3
    R.append(s(('"', 11), (".", 7), ('"', 10)))                                             # 4
    R.append(s((".", 18), ('"', 10)))                                                       # 5
    R.append(s(("~", 14), (".", 4), ('"', 10)))                                             # 6  channel
    R.append(s(("~", 14), (".", 5), ('"', 9)))                                              # 7
    R.append(s(("~", 2), ('"', 4), ("~", 8), (".", 6), ('"', 8)))                           # 8  islet x2-5
    R.append(s(("~", 2), ('"', 4), ("~", 8), (".", 7), ('"', 7)))                           # 9
    R.append(s(("~", 2), ('"', 4), ("~", 8), (".", 7), ('"', 7)))                           # 10
    R.append(s(("~", 2), ('"', 4), ("~", 8), (".", 7), ('"', 7)))                           # 11
    R.append(s(("~", 14), (".", 7), ('"', 7)))                                              # 12
    R.append(s(("~", 14), (".", 7), ('"', 7)))                                              # 13
    R.append(s((".", 21), ('"', 7)))                                                        # 14
    R.append(s(('"', 7), (".", 14), ('"', 7)))                                              # 15
    R.append(s(('"', 7), (".", 15), ('"', 6)))                                              # 16
    R.append(s(('"', 7), (".", 15), ('"', 6)))                                              # 17
    R.append(s(('"', 7), (".", 1), ('"', 4), (".", 11), ('"', 5)))                          # 18
    R.append(s(('"', 7), (".", 1), ('"', 4), (".", 12), ('"', 4)))                          # 19
    R.append(s(('"', 2), (".", 6), ('"', 4), (".", 16)))                                    # 20
    R.append(s(('"', 2), (".", 6), ('"', 4), (".", 16)))                                    # 21
    R.append(s(('"', 2), (".", 26)))                                                        # 22 (x 0-1 marsh to 25: the Old Water has no tall grass)
    R.append(s(('"', 2), (".", 16), ("~", 4), (".", 6)))                                    # 23 east pond
    R.append(s(('"', 2), (".", 16), ("~", 5), (".", 5)))                                    # 24
    R.append(s(('"', 2), (".", 16), ("~", 7), (".", 3)))                                    # 25
    R.append(s(('"', 1), (".", 17), ("~", 7), (".", 3)))                                    # 26
    R.append(s((".", 2), ("~", 8), (".", 8), ("~", 7), (".", 3)))                           # 27 west pond
    R.append(s((".", 2), ("~", 8), (".", 9), ("~", 3), (".", 6)))                           # 28
    R.append(s((".", 4), ("~", 5), (".", 15), ('"', 4)))                                    # 29
    R.append(s((".", 5), ("~", 2), (".", 16), ('"', 5)))                                    # 30
    R.append(s(('"', 4), (".", 19), ('"', 5)))                                              # 31
    R.append(s(('"', 4), (".", 20), ('"', 4)))                                              # 32
    R.append(s(('"', 4), (".", 21), ('"', 3)))                                              # 33
    R.append(s(('"', 4), (".", 24)))                                                        # 34
    R.append(s((".", 5), ("~", 6), (".", 17)))                                              # 35 south bay
    R.append(s(("~", 12), (".", 14), ("~", 2)))                                             # 36 causeway
    R.append(s(("~", 12), (".", 14), ("~", 2)))                                             # 37
    R.append(s(("~", 12), (".", 13), ("~", 3)))                                             # 38
    R.append(s(("~", 5), (".", 5), ("~", 2), (".", 12), ("~", 4)))                          # 39 islet, peninsula
    R.append(s(("~", 4), (".", 12), ("~", 12)))                                             # 40 islet + neck
    R.append(s(("~", 4), (".", 12), ("~", 1), ("L", 3), ("~", 8)))                          # 41 islet, mud bar
    R.append(s(("~", 5), (".", 5), ("~", 2), (".", 4), ("~", 1), ("L", 6), ("~", 5)))       # 42
    R.append(s(("~", 12), (".", 4), ("~", 1), ("L", 6), ("~", 5)))                          # 43
    R.append(s((".", 2), ("~", 10), (".", 4), ("~", 10), (".", 2)))                         # 44 the bays
    R.append(s(('"', 1), (".", 4), ("~", 7), (".", 4), ("~", 7), (".", 5)))                 # 45
    R.append(s(('"', 1), (".", 8), ("~", 3), (".", 4), ("~", 3), (".", 9)))                 # 46
    R.append(s(('"', 1), (".", 27)))                                                        # 47
    return R


# the old cypress, seated in the new marsh: (prefab, x, y) by the old position
TREES = {(18, 4): (19, 4), (1, 30): (1, 31), (1, 0): (1, 1), (4, 1): (4, 1), (8, 1): (8, 1)}
BAR = {"pirogue": (17, 41)}
# events nudged for the new banks: the old cell is a bank tile (surf water) now
MOVED = {"LOCALID_ROUTE1_LAFAYETTE": (16, 38)}

# --- tall grass: noise amplitude (cells), lattice size
G_AMP, G_SCALE = 2.5, 5.0
ISLET = (4, 39, 8, 4)       # the west islet (x, y, w, h): all tall grass


def load_base():
    spec = json.load(open(os.path.join(MAPS, KEY + ".base.json"), encoding="utf-8"))
    g = [list(l.rstrip("\n")) for l in open(os.path.join(MAPS, KEY + ".base.grid.txt"), encoding="utf-8") if l.strip()]
    for ch, x, y, w, h in spec["edits"]:
        for j in range(y, y + h):
            for i in range(x, x + w):
                g[j][i] = ch
    for row in g:  # the mockup's building footprints are just ground
        for i, c in enumerate(row):
            if c in "HKPM":
                row[i] = "."
    return spec, g


def road_spans():
    """{y: (a, b)} inclusive: 2 wide; a one-column shift is two rows of 3-wide road (what the path autotile draws)."""
    out = {}
    cur = ROAD_START
    shifts = dict(SHIFTS)
    y = 0
    while y < H:
        if y in shifts:
            nx = shifts[y]
            for yy in (y, y + 1):
                out[yy] = (min(cur, nx), max(cur, nx) + 1)
            cur = nx
            y += 2
        else:
            out[y] = (cur, cur + 1)
            y += 1
    return out


class Noise:
    def __init__(self, seed, scale):
        self.rng = random.Random(seed)
        self.scale = scale
        self.lat = {}

    def v(self, i, j):
        if (i, j) not in self.lat:
            self.lat[(i, j)] = self.rng.uniform(-1, 1)
        return self.lat[(i, j)]

    def at(self, x, y):
        fx, fy = x / self.scale, y / self.scale
        i, j = math.floor(fx), math.floor(fy)
        sm = lambda t: t * t * (3 - 2 * t)
        tx, ty = sm(fx - i), sm(fy - j)
        a = self.v(i, j) * (1 - tx) + self.v(i + 1, j) * tx
        b = self.v(i, j + 1) * (1 - tx) + self.v(i + 1, j + 1) * tx
        return a * (1 - ty) + b * ty


class Route:
    def __init__(self):
        self.spec, self.old = load_base()
        self.g = [list(r) for r in terrain_rows()]
        self.old_g = {(x, y) for y in range(H) for x in range(W) if self.old[y][x] == "G"}
        self.buildings = copy.deepcopy(self.spec["buildings"])

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def put(self, ch, x, y):
        if 0 <= x < W and 0 <= y < H:
            self.g[y][x] = ch

    def text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"

    def count(self, ch):
        return sum(r.count(ch) for r in self.g)


def lay_road(t, spans_):
    road = {(x, y) for y in range(H) for x in range(spans_[y][0], spans_[y][1] + 1)}
    for x, y in road:
        t.put(":", x, y)
    verge = natural.ring(road, 1) - road
    for x, y in verge:
        if 0 <= x < W and 0 <= y < H and t.g[y][x] in '"~' and y < 36 and not (6 <= y <= 13 and x == 13):
            t.put(".", x, y)      # (the channel's east end keeps its water: the pier's end is a bank piece, as in the original)
    return road, verge


def chamfer(bound):
    """Euclidean distance (cells) from every cell to the nearest cell of `bound`."""
    pts = list(bound)
    return {(x, y): min((math.hypot(x - a, y - b) for a, b in pts), default=99.0)
            for y in range(H) for x in range(W)}


# tall grass covers the ground (the user: "it's a swamp, it should be covered"): everything that is not the verge, the
# bank rows or a few plain drifts, with ragged margins. The edge beside the verge, the drifts and (less) the banks is cut
# by smooth noise; a 3x3 blur of the field rounds the outline into even treads.
DRIFTS = [(21.5, 21.5, 1.9), (21.5, 33.5, 1.7), (9.5, 17.5, 1.2), (24.5, 10.8, 1.1), (5.5, 22.5, 1.1), (7.5, 29.5, 1.0), (7.8, 32.6, 1.3)]
G_WANT = 372
NO_G_FROM = 44          # rows from here down are the south bank: plain grass
G_AMP = 2.4


def tall_grass(t, road, verge):
    noise = Noise(SEED, 5.0)
    noise2 = Noise(SEED + 7, 2.5)
    ground = {(x, y) for y in range(NO_G_FROM) for x in range(W) if t.g[y][x] == "." and (x, y) not in verge
              and not (x <= 2 and 20 <= y <= 26)}   # the grass cell beside the Old Water's marsh shore stays plain
    drift = {(x, y) for cx, cy, r in DRIFTS for x in range(W) for y in range(H) if math.hypot(x - cx, y - cy) <= r}
    free = ({(x, y) for x, y in verge if 0 <= x < W and 0 <= y < H and t.g[y][x] != ":"} | (drift & ground))
    wall = {(x, y) for y in range(H) for x in range(W) if t.g[y][x] in '"~L'}
    d_free = chamfer(free)
    d_wall = chamfer(wall)
    field0 = {c: min(d_free[c], d_wall[c] + 1.4) - 0.5 + noise.at(*c) * G_AMP + noise2.at(*c) * G_AMP * 0.4 for c in ground}
    field = {}
    for c in ground:    # a 3x3 blur rounds the outlines (even treads instead of single-cell steps)
        tot = wt = 0.0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                q = (c[0] + i, c[1] + j)
                if q in field0:
                    w = (2 - abs(i)) * (2 - abs(j))
                    tot += w * field0[q]
                    wt += w
        field[c] = tot / wt

    def nb(c, s_):
        x, y = c
        return sum(((x + i, y + j) in s_) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0))

    def make(bias):
        sel = {c for c in ground if c not in free and field[c] + bias > 0}
        for _ in range(2):
            new = set(sel)
            for c in ground:
                k = nb(c, sel)
                if c in sel and k <= 2:
                    new.discard(c)
                elif c not in sel and k >= 6 and c not in free:
                    new.add(c)
            sel = new
        seen, keep = set(), set()    # no clumps under 5 cells
        for c in sorted(sel):
            if c in seen:
                continue
            comp, stack = [], [c]
            seen.add(c)
            while stack:
                p = stack.pop()
                comp.append(p)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (p[0] + dx, p[1] + dy)
                    if q in sel and q not in seen:
                        seen.add(q)
                        stack.append(q)
            if len(comp) >= 5:
                keep |= set(comp)
        return keep

    best = None
    for bias in [x / 10 for x in range(-30, 41)]:
        keep = make(bias)
        if best is None or abs(len(keep) - G_WANT) < abs(len(best) - G_WANT):
            best = keep
    for x, y in best:
        t.put("G", x, y)
    return best


def seat_trees(t):
    out = []
    for b in t.buildings:
        key = (b["x"], b["y"])
        if b["prefab"].startswith("cypress") and key in TREES:
            b["x"], b["y"] = TREES[key]
        if b["prefab"] in BAR:
            b["x"], b["y"] = BAR[b["prefab"]]
        out.append(b)
    t.buildings = out


def report(t):
    S = natural.Shape(t.g)
    bad = [(x, y, S.cell_bad(x, y)) for y in range(H) for x in range(W) if S.cell_bad(x, y)]
    print("path badness:", sum(b for _, _, b in bad), bad[:20])
    print("G", t.count("G"), "(old", len(t.old_g), ") marsh", t.count('"'), "water", t.count("~"), "road", t.count(":"))


def ascii_dump(t):
    print("    " + "".join(str(x % 10) for x in range(W)))
    for y in range(H):
        print(f"{y:2d}  " + "".join(t.g[y]))


def build_route():
    t = Route()
    road, verge = lay_road(t, road_spans())
    tall_grass(t, road, verge)
    seat_trees(t)
    return t


def write(t, out):
    spec = copy.deepcopy(t.spec)
    spec["edits"] = []
    spec["_edits"] = "No edits: the grid is final (route_1.py wrote it from the original in route_1.base.*)."
    spec["buildings"] = t.buildings
    for o in spec["objects"]:
        if o["id"] in MOVED:
            o["x"], o["y"] = MOVED[o["id"]]
    spec["_comment"] = "Route 1, polished by route_1.py (edit that, not this file)."
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, KEY + ".grid.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(t.text())
    with open(os.path.join(out, KEY + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main(args):
    out = args[args.index("--out") + 1] if "--out" in args else MAPS
    t = build_route()
    report(t)
    if "--ascii" in args:
        ascii_dump(t)
    write(t, out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])

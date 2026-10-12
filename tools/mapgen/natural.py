"""Natural paths: worn, irregular dirt roads instead of uniform 2-wide strips with hard right-angle elbows.

The reference look is Brick City's sandy aprons (ragged organic edges, worn doorsteps) and Goldenrod's roads
that flare where they meet. The dirt-path autotile (build.py path_tile) can only draw shapes in which every
path cell sits in a full 2x2 block of path and has at most one "inner corner" diagonal, so every change here is
an edit to the character grid that is tried, scored with the autotile's own rules (`badness`), and kept only if
the drawing gets no worse. Edits, in order (all deterministic per map: seeded from the map key):

  * doorstep aprons: a small worn area 3-5 wide and 2 deep under each door (the carved stub is 2 wide and sits
    right of the door), bevelled at the bottom when 5 wide;
  * worn bends: the inside of elbows and T-junction corners gets a 1-3 step staircase fillet (as if cut by foot
    traffic), the outside of an elbow sometimes loses its corner cell;
  * long straight runs get occasional bulges (one or two cells deeper for a few cells, stepped ends) on
    alternating sides, and now and then a 1-cell lateral drift (the road jogs aside and back).

Never touched: a band `margin` cells wide along the map edges (exits stay straight and where the neighbour
expects them), prefab footprints and the ring around them, docks and bridges (and 3 cells round them), water,
marsh, mud, tall grass and anything that isn't plain grass (a new path cell needs plain grass or path in all
eight neighbours), and the mockup's tree cells. Run tidy_paths afterwards (it should find nothing to do).
"""
import random

PATH = ":="
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAG = ((-1, -1), (1, -1), (-1, 1), (1, 1))

STATS = {}  # counts from the last run (for the review tooling)


class Shape:
    def __init__(self, grid):
        self.g = [list(r) for r in grid]
        self.h, self.w = len(self.g), len(self.g[0])

    def inb(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def p(self, x, y):
        """Path, as the autotile sees it: off the map counts as path (build.py `same`)."""
        return not self.inb(x, y) or self.g[y][x] in PATH

    def pin(self, x, y):
        """Path inside the map only."""
        return self.inb(x, y) and self.g[y][x] in PATH

    def cell_bad(self, x, y):
        if not self.inb(x, y):
            return 0
        if self.g[y][x] not in PATH:
            # a 1-wide sliver of grass between two bits of path draws as two facing borders
            return 3 * ((self.pin(x - 1, y) and self.pin(x + 1, y)) + (self.pin(x, y - 1) and self.pin(x, y + 1)))
        p = self.p
        n, s, w, e = p(x, y - 1), p(x, y + 1), p(x - 1, y), p(x + 1, y)
        score = 0
        if not any(all(p(x + i, y + j) for i in (ox, ox + 1) for j in (oy, oy + 1)) for ox in (-1, 0) for oy in (-1, 0)):
            score += 4
        if not n and not s:
            score += 4
        if not w and not e:
            score += 4
        u = sum(1 for dx, dy in DIAG if not p(x + dx, y + dy) and p(x + dx, y) and p(x, y + dy))
        edge = not (n and s and w and e)
        score += 2 * u if edge else 2 * max(0, u - 1)
        return score

    def region_bad(self, cells):
        return sum(self.cell_bad(x, y) for x, y in cells)


def ring(cells, r):
    return {(x + i, y + j) for x, y in cells for i in range(-r, r + 1) for j in range(-r, r + 1)}


IMPORTANT = {"pokecenter", "mart", "gym", "brick_hall", "brick_shop", "capitol"}  # fronts that get a worn plaza


def natural_paths(key, grid, foot=frozenset(), docks=frozenset(), doors=(), trees=frozenset(), margin=4,
                  kind="route", fronts=()):
    """Returns the grid with natural-looking paths (see the module docstring). foot: prefab cells (buildings,
    docks, patches under prefabs); docks: dock/bridge cells (kept well clear); doors: door cells of buildings
    (their aprons go in the rows below); trees: the mockup's tree cells (left for plant_trees); kind: "route" or
    "town" (towns get no bulges); fronts: [{prefab, doors}] per building, so important fronts get a plaza."""
    S = Shape(grid)
    g, w, h = S.g, S.w, S.h
    rng = random.Random(key + "paths")
    stats = {"aprons": 0, "fillets": 0, "rounded": 0, "bulges": 0, "drifts": 0}
    near_foot = ring(foot, 1)
    no_go = set(foot) | ring(docks, 3) | ring(trees, 1)
    protected = set()  # cells that must stay path (door stubs, aprons)
    path_ch = max(PATH, key=lambda c: sum(r.count(c) for r in g))

    def in_core(x, y):
        return margin <= x < w - margin and margin <= y < h - margin

    def can_add(x, y, hug=False):
        # plain grass (or the odd cell of the mockup's tall grass), with only grass, tall grass or path around
        # it: the tall grass beside a new path cell goes back to plain grass (the one-tile verge the user wants)
        if not in_core(x, y) or g[y][x] not in ".G" or (x, y) in no_go or (not hug and (x, y) in near_foot):
            return False
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                c = (x + i, y + j)
                if not S.inb(*c):
                    return False
                if g[c[1]][c[0]] not in ".G:=" and not (hug and c in foot):
                    return False
        return True

    def can_remove(x, y):
        return in_core(x, y) and g[y][x] in PATH and (x, y) not in protected and (x, y) not in near_foot

    def attempt(adds, removes=(), hug=False, slack=0):
        adds, removes = list(dict.fromkeys(adds)), list(dict.fromkeys(removes))
        if not adds and not removes:
            return False
        if not all(can_add(x, y, hug) for x, y in adds) or not all(can_remove(x, y) for x, y in removes):
            return False
        region = ring(adds + removes, 2)
        before = S.region_bad(region)
        old = {(x, y): g[y][x] for x, y in adds + removes}
        verge = {(x + i, y + j) for x, y in adds for i in (-1, 0, 1) for j in (-1, 0, 1)
                 if S.inb(x + i, y + j) and g[y + j][x + i] == "G"} - set(adds)
        old.update({c: "G" for c in verge})
        for x, y in verge:
            g[y][x] = "."
        for x, y in adds:
            g[y][x] = local_char(x, y)
        for x, y in removes:
            g[y][x] = "."
        if S.region_bad(region) > before + slack or (removes and not joined(removes)):
            for (x, y), c in old.items():
                g[y][x] = c
            return False
        return True

    def joined(removes):
        """Whether the path cells round the removed ones still hang together (within a few cells of them)."""
        box = ring(removes, 4)
        nb = [c for c in ring(removes, 1) if S.pin(*c)]
        if not nb:
            return True
        seen, todo = {nb[0]}, [nb[0]]
        while todo:
            x, y = todo.pop()
            for dx, dy in N4:
                c = (x + dx, y + dy)
                if c in box and c not in seen and S.pin(*c):
                    seen.add(c)
                    todo.append(c)
        return all(c in seen for c in nb)

    def local_char(x, y):
        near = [g[y + j][x + i] for i in (-1, 0, 1) for j in (-1, 0, 1) if S.inb(x + i, y + j) and g[y + j][x + i] in PATH]
        return max(PATH, key=near.count) if near else path_ch

    # ---- worn ground in front of buildings. Important fronts (Pokemon Center, Mart, gym, hall, shop) get a plaza:
    # door width + 4 wide, its outer corners bevelled, reaching down to the street when the street is close (fronts
    # side by side share one); houses get a small doorstep where their stub is long
    def door_groups(cells):
        by_row, out = {}, []
        for x, y in cells:
            by_row.setdefault(y, []).append(x)
        for y, xs in by_row.items():
            xs.sort()
            cur = [xs[0]]
            for x in xs[1:]:
                if x - cur[-1] <= 1:
                    cur.append(x)
                else:
                    out.append((cur, y))
                    cur = [x]
            out.append((cur, y))
        return out

    important = {(x, y) for f in fronts if f["prefab"] in IMPORTANT for x, y in f["doors"]}
    plazas, small = [], []
    for xs, dy in sorted(door_groups(doors), key=lambda g_: (g_[1], g_[0][0])):
        if not S.pin(xs[0], dy + 1):
            continue  # no stub under this door (a closed door on the shore): leave it
        protected.update((x, dy + 1) for x in xs)
        (plazas if any((x, dy) in important for x in xs) else small).append((xs[0], xs[-1], dy + 1))
    merged = []  # (a, b, y0, member door spans)
    for a, b, y0 in sorted(plazas, key=lambda p: (p[2], p[0])):
        if merged and merged[-1][2] == y0 and a - 2 - (merged[-1][1] + 3) <= 4:
            # close neighbours (a Center beside a Mart) share one plaza
            merged[-1] = (merged[-1][0], b, y0, merged[-1][3] + [(a, b)])
        else:
            merged.append((a, b, y0, [(a, b)]))

    def street_below(lo, hi, y0, reach=5):
        """Rows from y0 to the first row of path under the plaza that isn't its own stub, if within reach."""
        for t in range(1, reach + 1):
            row = [S.pin(x, y0 + t) for x in range(lo, hi + 1)]
            if sum(row) >= max(3, len(row) * 2 // 3) and not all(S.pin(x, y0 + t - 1) for x in range(lo, hi + 1)):
                return t  # a street: most of the row under the plaza (stubs alone don't count)
        return None

    for a, b, y0, members in merged:
        done_ = False
        for lo, hi in ((a - 2, b + 3), (a - 1, b + 2), (a - 1, b + 1)):
            t = street_below(lo, hi, y0)
            shapes = []
            if t is not None and t >= 2:
                # down to the street: the top row only in front of each door (its corners and the gap between two
                # fronts stay grass), the rest is worn ground
                top = sorted({x for ma, mb in members for x in range(max(lo + 1, ma - 1), min(hi - 1, mb + 2) + 1)})
                rows = [top] + [list(range(lo, hi + 1)) for _ in range(t - 1)]
                shapes.append([(x, y0 + j) for j, xs_ in enumerate(rows) for x in xs_])
                shapes.append([(x, y0 + j) for j in range(t) for x in range(lo, hi + 1)])
            for depth in (3, 2):
                rows = [list(range(lo, hi + 1)) for _ in range(depth - 1)] + [list(range(lo + 1, hi))]
                shapes.append([(x, y0 + j) for j, xs_ in enumerate(rows) for x in xs_])
            for cells in shapes:
                adds = [c for c in cells if not S.pin(*c)]
                if adds and attempt(adds, hug=True):
                    protected.update(cells)
                    stats["plazas"] = stats.get("plazas", 0) + 1
                    done_ = True
                    break
            if done_:
                break

    for a, b, y0 in small:
        hi0 = max(b, a + 1)  # the carved stub is 2 wide, from the door rightwards
        if any(S.pin(x, y0 + j) for x in range(a - 2, hi0 + 3) for j in (2, 3) if not a <= x <= hi0):
            continue  # the street (or another path) is right there: a doorstep would only make a slab
        for lo, hi in rng.sample([(a - 1, hi0 + 1), (a - 1, hi0)], 2):  # 4 or 3 wide, 2 deep
            cells = [(x, y0 + j) for x in range(lo, hi + 1) for j in (0, 1)]
            adds = [c for c in cells if not S.pin(*c)]
            if attempt(adds, hug=True):
                protected.update(cells)
                stats["aprons"] += 1
                break

    # ---- diagonal roads: a 2-3 wide road stepping one cell per row draws as a chain of rounded beads (every cell
    # needs two inner corners, the autotile has one). Four wide, each row overlapping the next by three, it draws
    # as a continuous jagged road: each row of such a run gets a cell more on each side (a 3-wide run one more)
    def segs(y):
        out, x = [], 0
        while x < w:
            if S.pin(x, y):
                a = x
                while x + 1 < w and S.pin(x + 1, y):
                    x += 1
                out.append((a, x))
            x += 1
        return out
    rows_ = {y: segs(y) for y in range(h)}
    chains, used = [], set()
    for y in range(h):
        for s in rows_[y]:
            if (y, s) in used or s[1] - s[0] + 1 not in (2, 3):
                continue
            for d in (1, -1):
                chain, cy, cs = [(y, s)], y, s
                while cy + 1 < h and (cs[0] + d, cs[1] + d) in rows_[cy + 1]:
                    cy, cs = cy + 1, (cs[0] + d, cs[1] + d)
                    chain.append((cy, cs))
                if len(chain) >= 3:
                    chains.append(chain)
                    used.update(chain)
                    break

    def widen(part):
        options = [[c for y, (a, b) in part for c in ((a - 1, y), (b + 1, y))]]
        if all(b - a + 1 == 3 for _, (a, b) in part):
            options = [[(a - 1, y) for y, (a, b) in part], [(b + 1, y) for y, (a, b) in part]] + options
        return any(attempt(o) for o in options)
    for chain in chains:
        i = 0
        while i < len(chain) - 1:
            for n in range(len(chain) - i, 1, -1):
                if widen(chain[i:i + n]):
                    stats["diagonals"] = stats.get("diagonals", 0) + 1
                    i += n
                    break
            else:
                i += 1

    # ...and wherever a road still has cells that need two inner corners (irregular diagonals), fill the grass
    # corners they miss, one cell at a time, while that makes the drawing strictly better
    for _ in range(6):
        changed = False
        for y in range(h):
            for x in range(w):
                if not S.pin(x, y) or not in_core(x, y) or S.cell_bad(x, y) == 0:
                    continue
                for dx, dy in DIAG:
                    c = (x + dx, y + dy)
                    if S.inb(*c) and not S.pin(*c) and S.pin(x + dx, y) and S.pin(x, y + dy) and attempt([c], slack=-1):
                        stats["repairs"] = stats.get("repairs", 0) + 1
                        changed = True
        if not changed:
            break

    # ---- worn bends: fillets in inner corners, sometimes a rounded outer corner
    def arm(x, y, dx, dy, side):
        """Length of the straight path edge starting at (x, y) and running (dx, dy), with grass on `side`."""
        n = 0
        while S.pin(x + dx * n, y + dy * n) and S.inb(x + dx * n + side[0], y + dy * n + side[1]) and \
                not S.pin(x + dx * n + side[0], y + dy * n + side[1]) and n < 12:
            n += 1
        return n

    corners = []
    for y in range(h):
        for x in range(w):
            if S.pin(x, y) or not S.inb(x, y):
                continue
            for sx, sy in DIAG:  # (sx, sy): from this grass cell towards the path's inside corner
                if S.pin(x + sx, y) and S.pin(x, y + sy) and S.pin(x + sx, y + sy):
                    ah = arm(x, y + sy, -sx, 0, (0, -sy))   # the edge running away along the row beside us
                    av = arm(x + sx, y, 0, -sy, (-sx, 0))   # and along the column
                    if max(ah, av) >= 3 and min(ah, av) >= 2 or max(ah, av) >= 4:
                        # an elbow or junction, a stair step (min arm 2), or a tread with a 1-row riser
                        corners.append((x, y, sx, sy, ah, av))
    rng.shuffle(corners)
    done = []
    for x, y, sx, sy, ah, av in corners:
        if g[y][x] in PATH:
            continue
        if min(ah, av) == 1:
            # a staircase (a road drawn on the diagonal): the tread above the riser runs on 1-3 cells, so the
            # steps come in uneven lengths and the band's thickness varies, instead of a regular flight
            if rng.random() < 0.5:
                k = min(rng.choice((1, 1, 2, 2, 3)), max(ah, av) - 2)
                run = [(x - i * sx, y) for i in range(k)] if ah >= av else [(x, y - j * sy) for j in range(k)]
                for n in range(len(run), 0, -1):
                    if attempt(run[:n]):
                        stats["treads"] = stats.get("treads", 0) + 1
                        break
            continue
        f = rng.choices((0, 1, 2), (30, 55, 15))[0]
        if min(ah, av) < 6:
            f = min(f, 1)  # a short arm (a door stub, a stair step) only gets a single bevel
        if any(o == (sx, sy) and (bx == x or by == y) and abs(x - bx) + abs(y - by) <= 10 for bx, by, o in done)                 and rng.random() < 0.7:
            continue  # the same bevel on the same side of the next stub along reads as a pattern
        if any(abs(x - bx) + abs(y - by) <= 4 for bx, by, _ in done):
            # the junction already has a worn corner: most of its others stay sharp, none grow big
            f = 0 if rng.random() < 0.6 else min(f, 1)
        for k in range(f, 0, -1):
            tri = [(x - i * sx, y - j * sy) for i in range(k) for j in range(k - i)]
            if attempt(tri):
                stats["fillets"] += 1
                done.append((x, y, (sx, sy)))
                break

    outer = []
    for y in range(h):
        for x in range(w):
            if not S.pin(x, y):
                continue
            for sx, sy in DIAG:  # (sx, sy): from this path cell towards the grass outside the corner
                if S.inb(x + sx, y + sy) and not S.pin(x + sx, y) and not S.pin(x, y + sy) and not S.pin(x + sx, y + sy):
                    ah = arm(x, y, -sx, 0, (0, sy))
                    av = arm(x, y, 0, -sy, (sx, 0))
                    if min(ah, av) >= 3 and max(ah, av) >= 4:
                        outer.append((x, y, sx, sy, None))
                    elif min(ah, av) == 1 and max(ah, av) >= 5:  # a stair tread's end: cut back 1-2 cells
                        outer.append((x, y, sx, sy, [(x - i * sx, y) for i in range(2)] if ah >= av else
                                      [(x, y - j * sy) for j in range(2)]))
    rng.shuffle(outer)
    for x, y, sx, sy, run in outer:
        if run is None:
            if rng.random() < 0.5 and attempt([], [(x, y)]):
                stats["rounded"] += 1
        elif rng.random() < 0.4 and (attempt([], run) or attempt([], run[:1])):
            stats["treads"] = stats.get("treads", 0) + 1

    # ---- straight runs: now and then a bulge (the road a cell wider for 4-8 cells, stepped ends) on one edge,
    # alternating sides along a road, never both edges at one spot; and on long clean stretches the odd drift (the
    # road jogs a cell aside and back, keeping its width; the jogs overlap by two cells so the stairs draw)
    placed = []  # (axis, road line, start, end)
    axes = {"h": (w, h, lambda a, b: (a, b)), "v": (h, w, lambda a, b: (b, a))}

    def edges():
        """Straight edge runs: road cells with grass on side s and road behind them."""
        out = []
        for axis, (L, M, at) in axes.items():
            for line in range(1, M - 1):
                for s in (-1, 1):
                    ok = lambda a: S.pin(*at(a, line)) and S.pin(*at(a, line - s)) and S.inb(*at(a, line + s))                         and not S.pin(*at(a, line + s))
                    a = 0
                    while a < L:
                        if not ok(a):
                            a += 1
                            continue
                        b = a
                        while b + 1 < L and ok(b + 1):
                            b += 1
                        if b - a + 1 >= 10:
                            out.append((axis, line, s, a, b))
                        a = b + 1
        return out

    def corridors():
        """Stretches of road with a constant 2-3 wide cross-section and grass on both sides."""
        out = []
        for axis, (L, M, at) in axes.items():
            def section(a, line):
                if not S.inb(*at(a, line - 1)) or S.pin(*at(a, line - 1)):
                    return 0
                k = 0
                while S.pin(*at(a, line + k)):
                    k += 1
                return k if 2 <= k <= 3 and S.inb(*at(a, line + k)) else 0
            for line in range(1, M - 1):
                a = 0
                while a < L:
                    k = section(a, line)
                    if not k:
                        a += 1
                        continue
                    b = a
                    while b + 1 < L and section(b + 1, line) == k:
                        b += 1
                    if b - a + 1 >= 16:
                        out.append((axis, line, k, a, b))
                    a = b + 1
        return out

    def clash(axis, line, a, b):
        return any(ax == axis and abs(ln - line) <= 7 and pa - 5 <= b and a <= pb + 5 for ax, ln, pa, pb in placed)

    todo = corridors() if kind == "route" else []
    rng.shuffle(todo)
    for axis, line, k, a, b in todo:
        at = axes[axis][2]
        if rng.random() < 0.5:
            continue
        for _ in range(6):
            n = rng.randrange(7, 12)
            pos = rng.randrange(a + 3, max(a + 4, b - 2 - n))
            end = pos + n - 1
            s = rng.choice((-1, 1))
            if end > b - 3 or clash(axis, line, pos, end):
                continue
            edge, far = (line - 1, line + k - 1) if s < 0 else (line + k, line)
            adds = [at(i, edge) for i in range(pos, end + 1)]
            removes = [at(i, far) for i in range(pos + 2, end - 1)]
            if not any(S.pin(*at(i, edge + s)) for i in range(pos - 1, end + 2)) and attempt(adds, removes):
                placed.append((axis, line, pos, end))
                stats["drifts"] += 1
                break

    todo = edges() if kind == "route" else []  # towns: no bulges (they read as errors on a street)
    rng.shuffle(todo)
    side_of = {}  # last bulge side per road, so they alternate
    for axis, line, s, a, b in todo:
        at = axes[axis][2]
        if rng.random() < 0.45:
            continue
        road = (axis, line if s > 0 else line + s)  # roughly: the same road from either edge
        if side_of.get(road) == s and rng.random() < 0.7:
            continue
        pos = a + 3 + rng.randrange(0, 4)
        while pos < b - 3:
            n = rng.choice((4, 5, 5, 6, 7, 8))  # long enough to read as a widening, not a knob
            end = pos + n - 1
            if end > b - 3:
                break
            beyond = [at(i, line + s * d) for i in range(pos - 1, end + 2) for d in (2, 3)]
            if not clash(axis, line, pos, end) and not any(S.pin(*c) for c in beyond) and                     attempt([at(i, line + s) for i in range(pos, end + 1)]):
                placed.append((axis, line, pos, end))
                side_of[road] = s
                stats["bulges"] += 1
                pos = end + rng.randrange(10, 19)
            else:
                pos += rng.randrange(2, 5)
    STATS.clear()
    STATS.update(stats)
    return ["".join(r) for r in g]


def total_bad(grid):
    S = Shape(grid)
    return S.region_bad((x, y) for y in range(S.h) for x in range(S.w))

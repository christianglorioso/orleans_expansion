"""Isle Marais polish pass (slice polish, 2026-10-12): rewrites maps/isle_marais.json + .grid.txt from the approved
original (maps/isle_marais.base.json + isle_marais.base.grid.txt, kept untouched) with:

  * a flowing path network: bevelled corners, plazas at the hall (church) and barn fronts and at the pier's foot, a
    street whose ends taper instead of stopping square, lanes that bow instead of meeting at right angles;
  * organic mud banks (east flat, west channel bank, south shoal) instead of the trapezoid and the straight strip;
  * more cypress groves, reed clumps and a second lily pond in the marsh (no cypress knees).

Buildings, doors, NPCs, items, signs, triggers and the Route 1 exit are the original's. Takes no lock itself:
    python tools/mapgen/buildlock.py acquire isle_marais
    python -W ignore tools/mapgen/isle_marais_gen.py [--out DIR] [--ascii]
    ... build.py / compose.py / check.py as the README says ...
    python tools/mapgen/buildlock.py release isle_marais
Edit this file, not maps/isle_marais.json (the base files are the untouched original). --out DIR writes the spec and
grid there instead (for previews: render with build.Builder; nothing in data/ is touched either way).
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
W, H = 38, 30
KEY = "isle_marais"


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


class Town:
    def __init__(self):
        self.spec, self.g = load_base()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", "orleans_bayou.json"), encoding="utf-8"))
        self.occ = {}          # cell -> prefab name (every cell of every building's box)
        self.new = []          # buildings added by this script
        for b in self.spec["buildings"]:
            self.mark(b)

    def mark(self, b):
        rows = self.cfg["prefabs"][b["prefab"]]["rows"]
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c is not None:
                    self.occ[(b["x"] + i, b["y"] + j)] = b["prefab"]

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def put(self, ch, x, y):
        if 0 <= x < W and 0 <= y < H:
            self.g[y][x] = ch

    def rows(self, ch, y, *spans):
        for a, b in spans:
            for x in range(a, b + 1):
                self.put(ch, x, y)

    def text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"

    def count(self, ch):
        return sum(r.count(ch) for r in self.g)

    def add(self, prefab, x, y, label):
        b = {"prefab": prefab, "x": x, "y": y, "label": label}
        self.new.append(b)
        self.mark(b)
        return b


# ---------------------------------------------------------------- mud
def mud(t):
    """The east flat, the west channel bank and the south shoal, redrawn with wandering outlines (every row's span is
    its own: runs of 2-3 rows per step, no straight edge longer than five cells, no one-cell notches)."""
    for y in range(H):
        for x in range(W):
            if t.g[y][x] == "L":
                t.g[y][x] = "."
    # east flat (the levee breach): a lobed shape, bay at the pier, a creek-like tail wandering down to the gulf
    flat = {
        16: [(25, 28)],
        17: [(23, 31)],
        18: [(24, 26), (29, 32)],
        19: [(29, 32)],
        20: [(29, 31)],
        21: [(28, 30)],
        22: [(27, 30)],
        23: [(27, 29)],
    }
    for y, spans in flat.items():
        t.rows("L", y, *spans)
    # west channel bank: wider where the shore bulges, narrow where it pinches
    west = {
        17: [(6, 9)],
        18: [(7, 8)],
        19: [(8, 10)],
        20: [(8, 9)],
    }
    for y, spans in west.items():
        t.rows("L", y, *spans)
    # south shoal
    t.rows("L", 22, (12, 14), (17, 19))
    t.rows("L", 23, (13, 14), (18, 19))


# ---------------------------------------------------------------- marsh and vegetation
def marsh(t):
    """The east marsh bulges into the town between the cabins and the shore (room for a real grove), the north patch
    grows a row (so reeds fit under its cypress) and a small reed bed sits in the pocket beside the main road."""
    east_from = {6: 34, 7: 33, 8: 33, 9: 33, 10: 33, 11: 33, 12: 34, 13: 34, 14: 34}
    for y, x0 in east_from.items():
        for x in range(x0, W):
            t.put('"', x, y)
    t.rows('"', 6, (14, 17))                 # the north patch, one row deeper
    t.rows('"', 9, (21, 23))                 # the reed bed beside the road
    t.rows('"', 10, (21, 23))
    t.rows('"', 11, (21, 23))
    for x in (35, 36):                       # a second lily pond, in the east marsh
        for y in (12, 13):
            t.put('~', x, y)


GROVES = [   # (prefab, x, y, label)
    ("cypress_marsh", 33, 8, "Cypress grove (east)"),
    ("reeds_marsh", 36, 8, "Reeds"),
    ("reeds_marsh", 37, 10, "Reeds"),
    ("reeds_marsh", 36, 3, "Reeds"),
    ("reeds_marsh", 14, 4, "Reeds"),
    ("reeds_marsh", 16, 4, "Reeds"),
    ("reeds_marsh", 21, 9, "Reeds"),
    ("reeds_marsh", 22, 9, "Reeds"),
]


def plant(t):
    for prefab, x, y, label in GROVES:
        t.add(prefab, x, y, label)


def fits(t, b):
    """check.py's rule for a prefab drawn on a patch base: every tile's four corner cells are that patch."""
    base = t.cfg["prefabs"][b["prefab"]].get("on_patch")
    rows = t.cfg["prefabs"][b["prefab"]]["rows"]
    bad = []
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c is None:
                continue
            x, y = b["x"] + i, b["y"] + j
            if any(t.at(min(x + dx, W - 1), min(y + dy, H - 1)) not in base for dx in (0, 1) for dy in (0, 1)):
                bad.append((x, y))
    return bad


# ---------------------------------------------------------------- paths
def catmull(pts, n=14):
    out = []
    p = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            s = k / n
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * s + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * s * s
                                    + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * s ** 3) for a in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def wet(t, x, y, r=1):
    """Would a path cell here cover a terrain border? Marsh, mud and churchyard patches (and water) draw their left/top
    borders in the cell to their left/above, and water draws its bank in the land cell beside it, so a path may not sit
    left of or above such a cell (it can sit to its right or below: the patch draws that border itself)."""
    soft = ('~', '"', 'L', 'S', 'I')
    return (any(t.at(x + i, y + j) in soft for i, j in ((1, 0), (0, 1), (1, 1))) or t.at(x, y - 1) in ('~', 'I')
            or (r > 1 and any(t.at(x + i, y + j) in soft for i in range(-r, r + 1) for j in range(-r, r + 1))))


def brush(t, cx, cy, r, ch=":"):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if 0 <= x < W and 0 <= y < H and math.hypot(x - cx, y - cy) <= r and t.g[y][x] == "." \
                    and (x, y) not in t.occ and not wet(t, x, y):
                t.g[y][x] = ch


def stroke(t, pts, radii, n=14):
    """A soft path along a spline through pts; the radius eases through `radii` (one per control point)."""
    line = catmull(pts, n)
    m = len(line) - 1
    for i, (x, y) in enumerate(line):
        s = i / m * (len(radii) - 1)
        k = min(int(s), len(radii) - 2)
        r = radii[k] + (radii[k + 1] - radii[k]) * (s - k)
        brush(t, x, y, r)


PATH = ":"


SPANS = {   # y -> path spans (x0, x1); hand-drawn so every bevel and plaza is where it is wanted
    # the Route 1 road, straight at the exit (x 18-19), then the barn plaza and the east lane to the tarped house
    0: [(18, 19)], 1: [(18, 19)], 2: [(18, 19)], 3: [(18, 19)], 4: [(18, 19)],
    5: [(18, 24)],
    6: [(18, 31)],
    7: [(18, 31)],
    8: [(18, 19)],
    9: [(18, 19)], 10: [(18, 19)], 11: [(18, 19)],
    # the church forecourt and its neck down to the street
    # the street, ending in a worn staircase at each end
    12: [(5, 31)],
    13: [(5, 31)],
    # the lane past the player's house and on to the pier's foot
    16: [(11, 12)], 17: [(11, 12)],
    18: [(11, 12), (20, 22)],
    19: [(11, 22)],
    20: [(11, 22)],
}
CHURCH = {y: [(9, 10)] for y in range(7, 12)}   # straight and even, under the double door
LANE = {14: [(11, 12)], 15: [(11, 12)]}


def paths(t):
    for spans in (SPANS, CHURCH, LANE):
        for y, sp in spans.items():
            t.rows(":", y, *sp)


def smooth(t, protect=frozenset(), passes=1):
    for _ in range(passes):
        new = [r[:] for r in t.g]
        for y in range(H):
            for x in range(W):
                if (x, y) in t.occ or (x, y) in protect or t.g[y][x] not in ".:" or wet(t, x, y):
                    continue
                n = sum(1 for i in (-1, 0, 1) for j in (-1, 0, 1)
                        if not (0 <= x + i < W and 0 <= y + j < H) or t.g[y + j][x + i] == ":")
                new[y][x] = ":" if n >= 5 else "."
        t.g = new


def tidy(t, protect=frozenset()):
    """Hill-climb with the autotile's own scoring (natural.Shape), but only around cells the autotile can't draw: the
    hand-drawn spans stay as drawn wherever they are already clean."""
    S = natural.Shape(t.g)
    cand = lambda x, y: ((x, y) not in t.occ and (x, y) not in protect and S.g[y][x] in ".:" and not wet(t, x, y) and y > 0)
    for _ in range(6):
        bad = {(x, y) for y in range(H) for x in range(W) if S.cell_bad(x, y)}
        if not bad:
            break
        changed = 0
        for x, y in sorted(natural.ring(bad, 1)):
            if not (0 <= x < W and 0 <= y < H) or not cand(x, y):
                continue
            around = [(x + i, y + j) for i in range(-2, 3) for j in range(-2, 3)]
            before = S.region_bad(around)
            old = S.g[y][x]
            S.g[y][x] = ":" if old == "." else "."
            if S.region_bad(around) < before:
                changed += 1
            else:
                S.g[y][x] = old
        if not changed:
            break
    t.g = S.g


def worn(t):
    """natural.py's worn bends (fillets inside elbows and junctions, the odd rounded corner), scored with the autotile's
    own rules; nothing near a building, the pier or the water."""
    foot = set(t.occ)
    docks = {c for c, n in t.occ.items() if n == "pier"}
    t.g = [list(r) for r in natural.natural_paths(KEY, ["".join(r) for r in t.g], foot=foot, docks=docks, margin=1, kind="town")]
    print("natural:", natural.STATS)


def build_town():
    t = Town()
    for y in range(H):
        for x in range(W):
            if t.g[y][x] in ":=":
                t.g[y][x] = "."
    mud(t)
    marsh(t)
    paths(t)
    protect = {(18, 0), (19, 0), (22, 5), (9, 7), (10, 7), (6, 12), (26, 12), (30, 12), (29, 6), (16, 19)}
    for y in range(H):      # a path never covers a terrain border or a building
        for x in range(W):
            if t.g[y][x] == ":" and ((x, y) in t.occ or (wet(t, x, y) and y > 0)):
                print("path cell dropped (covers a border or a building):", (x, y))
                t.g[y][x] = "."
    for p in protect:
        t.g[p[1]][p[0]] = ":"
    tidy(t, protect)
    worn(t)
    plant(t)
    for b in t.spec["buildings"] + t.new:
        bad = fits(t, b) if t.cfg["prefabs"][b["prefab"]].get("on_patch") else []
        if bad:
            print("prefab crosses its patch edge:", b["label"], b["x"], b["y"], bad[:3])
    return t


def report(t):
    S = natural.Shape(t.g)
    bad = [(x, y, S.cell_bad(x, y)) for y in range(H) for x in range(W) if S.cell_bad(x, y)]
    print("path badness:", sum(b for _, _, b in bad), bad[:20])


def write(t, out, proposal=False):
    spec = copy.deepcopy(t.spec)
    if proposal:
        spec["_proposal"] = True
    spec["edits"] = []
    spec["_edits"] = "No edits: the grid is final (isle_marais_gen.py wrote it from the original in isle_marais.base.*)."
    spec["buildings"] = spec["buildings"] + t.new
    spec.pop("_channel", None)
    spec.pop("_east_swamp", None)
    spec["_comment"] = "Isle Marais, polished by isle_marais_gen.py (edit that, not this file)."
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, KEY + ".grid.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(t.text())
    with open(os.path.join(out, KEY + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ascii_dump(t):
    print("    " + "".join(str(x % 10) for x in range(W)))
    for y in range(H):
        line = ""
        for x in range(W):
            if (x, y) in t.occ:
                n = t.occ[(x, y)]
                line += "T" if n.startswith(("cypress", "reeds")) else n[0].upper()
            else:
                line += t.g[y][x]
        print(f"{y:2d}  {line}")


def main(args):
    out = args[args.index("--out") + 1] if "--out" in args else MAPS
    t = build_town()
    report(t)
    if "--ascii" in args:
        ascii_dump(t)
    write(t, out, proposal="--proposal" in args)
    print("wrote", out, "mud", t.count("L"), "path", t.count(":"))


if __name__ == "__main__":
    main(sys.argv[1:])

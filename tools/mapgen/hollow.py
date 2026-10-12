"""Lutin's Hollow (gym 6, Fairy: a hidden hollow of Spanish moss), built by hand from its mockup (07_lutins_hollow.png):
50 x 38 on the orleans_hollow tileset (make_town_tilesets.py + hollow_tileset.py).

usage (from the decomp root; takes no lock itself: wrap it in `buildlock.py acquire/release hollow`):
    python -W ignore tools/mapgen/hollow.py [--review] [--no-build] [--fresh] [--dry-run] [--ascii]
writes maps/lutins_hollow.json + .grid.txt, regenerates the art (sources/orleans_custom/make_hollow_art.py when it
writes hollow.png/hollow.json) and the tileset recipe (make_town_tilesets.py orleans_hollow), composes and builds
(again while the build asks for new overlay tiles), runs check.py; --review writes maps/00_lutins_hollow_review.png and
maps/hollow_crops/*.png (mockup | built and 3x crops). Then build_interior.py relinks the door warps to their rooms
(labels from town_plans.PLANS["lutins_hollow"]). Edit this file, never maps/lutins_hollow.json. Pieces without art yet
use same-footprint stand-ins (hollow_tileset.py): the layout doesn't change when the art lands.

Layout (x right, y down); everything is ground (no marsh, no tall grass):
    ring       a dense ring of moss-draped trees (a superellipse with a ragged inner edge, two cells thick at the map
               edge) with ONE gap, the Route 13 lane in the south-west; thickets fill the cracks between the trunks
    pond       an irregular pond in the middle, with a soft organic loop path round it (width 2-4, no right angles)
    gym        the glade arbour behind its moss curtains, north; the Pokemon Center is a hollow tree in the west; two moss
               cottages (north-east, south-west) and the Herbalist (south-east); a short curving spur to every door
    fairy      three pepper plots in the corner clearings, fairy rings in the east and west glades, a reflecting pool
               beside each of the five false Lutins, the Delphoxite riddle stone by the gym
    ground     dense layered undergrowth: ferns, moss, flower drifts, toadstools, glow-bells, bushes, logs
"""
import json
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from firstpass import dump, item_flag, shell  # noqa: E402
from town_plans import door_label  # noqa: E402
import interiors as mock  # noqa: E402
import natural  # noqa: E402
from hollow_tileset import WANTED  # noqa: E402

KEY, NAME, CONST = "lutins_hollow", "LutinsHollow", "MAP_LUTINS_HOLLOW"
CFG = "orleans_hollow"
W, H = 50, 38
SPEC = os.path.join(HERE, "maps", KEY + ".json")
EXIT_ROWS = (30, 31)    # the Route 13 exit: x = 0, the 2 rows Route 13's lane meets (world seam: Route 13 rows 2-3 + 28)
CX, CY = 25.0, 19.5                 # the pond's centre
RNG_SEED = 1307

# door-bearing buildings, in the first pass's warp order (the rooms' exits use these warp numbers):
# room key -> (prefab, top-left)
BUILDINGS = [
    ("lutins_hollow_gym", "gym_arbour", (22, 2)),
    ("lutins_hollow_moss_house_n", "cottage_a", (34, 6)),
    ("lutins_hollow_pokecenter", "hollow_tree", (5, 10)),
    ("lutins_hollow_herbalist", "herbalist", (39, 23)),
    ("lutins_hollow_moss_house_s", "cottage_b", (8, 22)),
]


def pond_r(th):
    return 5.3 + 0.8 * math.sin(2 * th + 0.7) + 0.6 * math.sin(3 * th + 2.1) + 0.3 * math.sin(5 * th + 1.0)


def loop_c(th):     # the loop's centre line (distance from the pond centre): wanders in and out
    return (pond_r(th) + 5.4 + 0.8 * math.sin(4 * th + 1.3) + 0.6 * math.sin(7 * th + 4.0)
            + 0.3 * math.sin(11 * th + 0.6) + 0.8 * math.sin(2 * th + 2.2))


def loop_w(th):     # its width stays steady (a narrow footpath); the centre line does the wandering
    return 2.5 + 0.12 * math.sin(3 * th + 0.3)


class Town:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]
        self.b = []
        self.occ = set()
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.objects, self.signs, self.items, self.hidden = [], [], [], []
        self.skipped, self.stand_ins = [], set()
        self.counts = {}
        self.rng = random.Random(RNG_SEED)
        self.forest = set()          # cells where the ring's trees may stand
        self.doors, self.fronts = [], []

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def fill(self, ch, x0, y0, x1, y1):
        for j in range(y0, y1 + 1):
            for i in range(x0, x1 + 1):
                if 0 <= i < W and 0 <= j < H:
                    self.g[j][i] = ch

    def have(self, prefab):
        return prefab in self.cfg["prefabs"]

    def rows(self, prefab):
        return self.cfg["prefabs"][prefab]["rows"]

    def cells(self, prefab, x, y):
        r = self.rows(prefab)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0])) if r[j][i] is not None]

    def box(self, prefab, x, y):
        r = self.rows(prefab)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0]))]

    def place(self, prefab, x, y, label=None, **kw):
        cells = self.box(prefab, x, y)
        clash = [c for c in cells if c in self.occ]
        if clash:
            raise SystemExit(f"{prefab} at ({x},{y}) overlaps {clash[:4]}")
        for c in cells:
            self.occ.add(c)
        b = {"prefab": prefab, "x": x, "y": y, "label": label or prefab.replace("_", " ").capitalize()}
        b.update(kw)
        self.b.append(b)
        self.counts[prefab] = self.counts.get(prefab, 0) + 1
        if self.cfg["prefabs"][prefab].get("stand_in"):
            self.stand_ins.add(prefab)
        return b

    def near_water(self, cells, r=0):
        return any(self.at(i + dx, j + dy) == "~" for i, j in cells for dx in range(-r, r + 2)
                   for dy in range(-r, r + 2))

    def deco(self, prefab, x, y, label=None, ring=0, water=False, **kw):
        """A decoration on free plain ground (its cells inside the map, free, not on path, a cell clear of water
        unless `water`); `ring`: also this many cells of margin free of other objects). Else skipped."""
        if not self.have(prefab):
            self.skipped.append((prefab, x, y, "no prefab"))
            return None
        cs = self.box(prefab, x, y)
        ok = all(0 <= i < W and 0 <= j < H and (i, j) not in self.occ and self.g[j][i] == "." for i, j in cs)
        if ok and not water:
            ok = not self.near_water(cs, 1)
        if ok and ring:
            ok = not any((i + dx, j + dy) in self.occ for i, j in cs for dx in range(-ring, ring + 1)
                         for dy in range(-ring, ring + 1))
        if not ok:
            self.skipped.append((prefab, x, y))
            return None
        return self.place(prefab, x, y, label, **kw)

    def grid_text(self):
        return "\n".join("".join(r) for r in self.g) + "\n"


# ---------------------------------------------------------------- water and buildings
def label_of(key):
    return door_label(key, mock.INTERIORS[key]["title"])


def interiors_before():
    if not os.path.exists(SPEC):
        return {}
    old = json.load(open(SPEC, encoding="utf-8"))
    return {b["label"]: b["interior"] for b in old.get("buildings", []) if b.get("interior")}


def pond(t):
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - CX, y - CY)
            if d < pond_r(math.atan2(y - CY, x - CX)):
                t.g[y][x] = "~"


def buildings(t):
    links = interiors_before()
    for key, prefab, (x, y) in BUILDINGS:
        b = t.place(prefab, x, y, label_of(key))
        if label_of(key) in links:
            b["interior"] = links[label_of(key)]
        d = t.cfg["prefabs"][prefab]["door"]
        t.doors.append((x + d[0], y + d[1]))
        t.fronts.append((x + d[0], y + d[1] + 1))


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


def wet(t, x, y, r):
    return any(t.at(x + i, y + j) == "~" for i in range(-r, r + 1) for j in range(-r, r + 1))


def brush(t, cx, cy, r):
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if 0 <= x < W and 0 <= y < H and math.hypot(x - cx, y - cy) <= r and t.g[y][x] == "." \
                    and (x, y) not in t.occ and not wet(t, x, y, 2):
                t.g[y][x] = ":"


def stroke(t, pts, radii):
    """A soft path along a spline through pts; the radius eases through `radii` (one per control point)."""
    line = catmull(pts)
    m = len(line) - 1
    for i, (x, y) in enumerate(line):
        s = i / m * (len(radii) - 1)
        k = min(int(s), len(radii) - 2)
        r = radii[k] + (radii[k + 1] - radii[k]) * (s - k)
        brush(t, x, y, r)


def line2(t, pts, n=24):
    """A 2-wide footpath along a spline through pts: for steep stretches each row gets a 2-cell span, for shallow ones
    each column gets a 2-cell span, so the edges step evenly (a cell sideways every row or two) and the width is steady."""
    line = catmull(pts, n)
    prev = None
    for (x, y), (x2, y2) in zip(line, line[1:] + [line[-1]]):
        steep = abs(y2 - y) >= abs(x2 - x) if (x2, y2) != (x, y) else prev
        prev = steep
        for sub in (0.0, 0.5):     # two samples per step keep diagonals gap-free
            sx, sy = x + (x2 - x) * sub, y + (y2 - y) * sub
            cells = ([(math.floor(sx) + i, round(sy)) for i in (0, 1)] if steep
                     else [(round(sx), math.floor(sy) + j) for j in (0, 1)])
            for i, j in cells:
                if 0 <= i < W and 0 <= j < H and t.g[j][i] == "." and (i, j) not in t.occ and not wet(t, i, j, 2):
                    t.g[j][i] = ":"


def loop_pts(step=6):
    return [(CX + loop_c(math.radians(k)) * math.cos(math.radians(k)),
             CY + loop_c(math.radians(k)) * math.sin(math.radians(k))) for k in range(0, 360, step)]


def spur(t, front, bow=0.8, lift=1.0):
    """A gently bowed 2-wide spur from a doorstep to the nearest point of the loop."""
    fx, fy = front
    def clear(q):    # the straight run from just below the door to q crosses no building
        for k in range(4, 21):
            i, j = round(fx + (q[0] - fx) * k / 20), round(fy + 1 + (q[1] - fy - 1) * k / 20)
            if any((i + a, j + b) in t.occ for a in (-1, 0, 1) for b in (-1, 0, 1)):
                return False
        return True
    tx, ty = min((q for q in loop_pts(3) if clear(q)), key=lambda q: math.hypot(q[0] - fx, q[1] - fy))
    mx, my = (fx + tx) / 2, (fy + 1 + ty) / 2
    d = math.hypot(tx - fx, ty - fy) or 1.0
    nx, ny = -(ty - fy) / d, (tx - fx) / d
    line2(t, [(fx, fy), (fx, fy + lift), (mx + nx * bow, my + ny * bow), (tx, ty)])


def paths(t):
    # the loop round the pond: a wandering centre line, a steady 2-wide footpath
    pts = loop_pts(6)
    line2(t, pts + pts[:3], 16)
    # the Route 13 lane: the five exit rows at the edge, easing into a 2-wide lane that climbs to the loop's SW side
    for x in range(0, 4):
        for y in EXIT_ROWS:
            t.g[y][x] = ":"
    stroke(t, [(3, 31), (5, 30.8), (7, 30.3)], [2.5, 1.7, 1.2])
    tx, ty = min(loop_pts(3), key=lambda q: math.hypot(q[0] - 18, q[1] - 27))
    line2(t, [(7, 30.4), (11, 29.4), (14.5, 28.2), (tx, ty)], 16)
    # spurs: each starts at the doorstep and runs to the loop (or the lane)
    for front, bow in zip(t.fronts, (0.0, 0.8, -0.8, 0.8, -0.6)):
        spur(t, front, bow)


def smooth(t, protect=frozenset(), passes=2):
    """Majority filter on the path (a cell is path when at least 5 of its 3x3 block are): rounds elbows and the
    brush marks into soft, stepped bevels and drops 1-cell bumps."""
    for _ in range(passes):
        new = [row[:] for row in t.g]
        for y in range(H):
            for x in range(W):
                if (x, y) in t.occ or (x, y) in protect or not (3 < x < W - 4 and 3 < y < H - 4) or t.g[y][x] not in ".:"                         or wet(t, x, y, 2):
                    continue
                n = sum(1 for i in (-1, 0, 1) for j in (-1, 0, 1)
                        if not (0 <= x + i < W and 0 <= y + j < H) or t.g[y + j][x + i] == ":")
                new[y][x] = ":" if n >= 5 else "."
        t.g = new


def tidy(t, protect=frozenset()):
    """Hill-climb the path cells with the autotile's own scoring (natural.Shape): flip a cell between path and grass
    whenever that lowers the badness of its neighbourhood (no 1-wide bits, no slivers, no stacked inner corners)."""
    S = natural.Shape(t.g)
    cand = lambda x, y: ((x, y) not in t.occ and (x, y) not in protect and S.g[y][x] in ".:"
                         and not wet(t, x, y, 2) and 3 < x < W - 4 and 3 < y < H - 4)
    for _ in range(8):
        changed = 0
        for y in range(H):
            for x in range(W):
                if not cand(x, y):
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


# ---------------------------------------------------------------- the ring of trees
def forest_cell(x, y):
    if x < 2 or y < 2 or x > W - 3 or y > H - 3:
        return True
    th = math.atan2(y - CY + 0.0, x - CX)
    f = (abs(x - CX) / 20.6) ** 2.7 + (abs(y - 19.2) / 14.2) ** 2.7
    f *= 1 + 0.06 * math.sin(3 * th + 0.4) + 0.045 * math.sin(7 * th + 1.9) + 0.035 * math.sin(11 * th + 0.3)
    return f > 1.0


GLADES = [(8.5, 6.0, 5.0, 3.6), (43.5, 6.5, 5.0, 3.6), (42.5, 33.0, 5.0, 3.6),  # pepper corners
          (41.5, 13.5, 4.5, 4.0), (4.5, 21.5, 4.0, 4.0)]                      # fairy-ring glades (x, y, rx, ry)


def make_forest(t):
    pathcells = {(x, y) for y in range(H) for x in range(W) if t.g[y][x] == ":"}
    near_path = {(x + i, y + j) for x, y in pathcells for i in range(-2, 3) for j in range(-2, 3)}
    keep = set()
    for c in t.occ:
        keep |= {(c[0] + i, c[1] + j) for i in range(-1, 2) for j in range(-1, 2)}
    glade = lambda x, y: any(((x - gx) / rx) ** 2 + ((y - gy) / ry) ** 2 < 1 and 2 <= x <= W - 3 and 2 <= y <= H - 3
                             for gx, gy, rx, ry in GLADES)
    for y in range(H):
        for x in range(W):
            if forest_cell(x, y) and (x, y) not in near_path and (x, y) not in keep and not glade(x, y) \
                    and t.g[y][x] == "." and (x, y) not in t.occ:
                t.forest.add((x, y))


def trees(t):
    """Greedy dense packing: big trees first, then smaller, then thickets in every crack of the ring."""
    rng = t.rng
    kinds = [("tree_a", "tree_b", "tree_c"), ("tree_s",)]
    for group in kinds:
        cells = list(t.forest)
        rng.shuffle(cells)
        for x, y in cells:
            prefab = rng.choice(group)
            if not t.have(prefab):
                continue
            bx = t.box(prefab, x, y)
            if all(c in t.forest and c not in t.occ for c in bx):
                t.place(prefab, x, y, "Ring tree")
    thick = [p for p in ("thicket_a", "thicket_b") if t.have(p)]
    for x, y in sorted(t.forest):
        if (x, y) not in t.occ and thick:
            t.place(rng.choice(thick), x, y, "Thicket")


# ---------------------------------------------------------------- fairy details
PEPPERS = [(5, 4), (41, 4), (40, 32)]     # each plot is two beds side by side (6 x 2)
RINGS = [(40, 12), (2, 21)]               # fairy rings (3x3, top-left)
RIDDLE = (31, 6)                          # the Delphoxite riddle stone (1x2, top-left)


def fairy(t):
    for x, y in PEPPERS:
        for dx in (0, 3):
            t.deco("pepper_bed", x + dx, y, "Pepper row")
    for x, y in RINGS:
        t.deco("fairy_ring", x, y, "Fairy ring")
    t.deco("riddle_stone", RIDDLE[0], RIDDLE[1], "Riddle stone")


# ---------------------------------------------------------------- people, items, signs
def people(t):
    """(id, gfx, x, y, movement, text), then reflecting pools beside the false Lutins."""
    folk = [
        ("LUTIN", "OBJ_EVENT_GFX_ARTIST", 27, 8, "MOVEMENT_TYPE_FACE_LEFT",
         "LUTIN: The real one casts a reflection,\ncher. Look in the pools. (Story pass: gym.)"),
        ("FLOETTE_SEED", "OBJ_EVENT_GFX_WOMAN_4", 43, 28, "MOVEMENT_TYPE_FACE_LEFT",
         "Floette seeds, cher. Come back when the\ntelling is done. (Post-game: story pass.)"),
        ("JAYDEN", "OBJ_EVENT_GFX_BOY_2", 12, 27, "MOVEMENT_TYPE_FACE_RIGHT",
         "JAYDEN: ...Not now. (Story pass: Jayden battle 4.)"),
        ("WREN", "OBJ_EVENT_GFX_GIRL_2", 13, 27, "MOVEMENT_TYPE_FACE_LEFT",
         "WREN: (hums) ...part of the true telling.\n(Story pass.)"),
    ]
    for name, gfx, x, y, move, text in folk:
        if t.at(x, y) not in (".", ":") or (x, y) in t.occ:
            t.skipped.append(("npc " + name, x, y))
            continue
        t.objects.append({"id": f"LOCALID_LUTINS_HOLLOW_{name}", "gfx": gfx, "x": x, "y": y, "move": move, "text": text})
        t.occ.add((x, y))
    # the riddle's reward: the Delphoxite (mockup 2), at the stone; a placeholder ball with a stable flag until the
    # story pass hides it behind the gym
    x, y = RIDDLE[0], RIDDLE[1] + 2
    if t.at(x, y) in (".", ":") and (x, y) not in t.occ:
        t.items.append({"x": x, "y": y, "item": "ITEM_DELPHOXITE", "flag": item_flag(CONST, "delphoxite"),
                        "_comment": "Delphoxite (mockup 2): the riddle's reward at the stone. TODO story pass: after the gym."})
        t.occ.add((x, y))
    else:
        t.skipped.append(("item delphoxite", x, y))


FALSE_LUTIN_ANGLES = (-140, -92, -38, 52, 122)    # where round the pond the false Lutins stand (degrees)


def pools(t):
    """A false Lutin beside a reflecting pool (2x2) on the pond's bank, one at each angle, the NPC on the loop side of
    the pool facing the water."""
    n = 0
    for deg in FALSE_LUTIN_ANGLES:
        th = math.radians(deg)
        R = pond_r(th)
        done = False
        for k in (1.5, 1.9, 1.1, 2.3):
            px = int(round(CX + (R + k) * math.cos(th))) - 1
            py = int(round(CY + (R + k) * math.sin(th))) - 1
            if not t.deco("pool", px, py, "Reflecting pool", water=True):
                continue
            for k2 in (3.2, 3.6, 2.9, 4.0):
                nx = int(round(CX + (R + k2) * math.cos(th)))
                ny = int(round(CY + (R + k2) * math.sin(th)))
                if t.at(nx, ny) in (".", ":") and (nx, ny) not in t.occ:
                    n += 1
                    face = ("MOVEMENT_TYPE_FACE_RIGHT" if math.cos(th) < -0.7 else "MOVEMENT_TYPE_FACE_LEFT" if math.cos(th) > 0.7
                            else "MOVEMENT_TYPE_FACE_DOWN" if math.sin(th) < 0 else "MOVEMENT_TYPE_FACE_UP")
                    t.objects.append({"id": f"LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_{n}", "gfx": "OBJ_EVENT_GFX_ARTIST",
                                      "x": nx, "y": ny, "move": face,
                                      "text": "(False Lutin: there is no reflection in the pool.)"})
                    t.occ.add((nx, ny))
                    done = True
                    break
            if done:
                break
        if not done:
            t.skipped.append(("false Lutin + pool at angle", deg))


def signs(t):
    for sid, x, y, text in (
            ("SignHollow", 5, 28, "LUTIN'S HOLLOW\nHidden among the Spanish moss. Mind the false Lutins."),
            ("SignHerbalist", 38, 27, "HERBALIST\nSimples, tonics and Floette seeds.")):
        spot = None
        for r in range(0, 5):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    c = (x + dx, y + dy)
                    if spot is None and 0 <= c[0] < W and 0 <= c[1] < H and c not in t.occ and t.g[c[1]][c[0]] == "."                             and not t.near_water([c]):
                        spot = c
        if not t.have("sign") or spot is None:
            t.skipped.append(("sign", x, y))
            continue
        x, y = spot
        t.place("sign", x, y, "Sign")
        t.signs.append({"id": sid, "x": x, "y": y, "text": text})


# ---------------------------------------------------------------- undergrowth
def noise_grid(rng, cell=5):
    gw, gh = W // cell + 3, H // cell + 3
    g = [[rng.random() for _ in range(gw)] for _ in range(gh)]

    def f(x, y):
        fx, fy = x / cell, y / cell
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[j][i] * (1 - tx) + g[j][i + 1] * tx
        b = g[j + 1][i] * (1 - tx) + g[j + 1][i + 1] * tx
        return a * (1 - ty) + b * ty
    return f


FERNS = ("fern_a", "fern_b", "fern_c")
TOADS = ("toadstool_red", "toadstool_pale")
BUSHES = ("bush_a", "bush_b")
LOGS = 9
# (kind, how many drifts, min radius, max radius): the tile budget lever is FERNS / the bloom kinds
DRIFTS = [("fern", 24, 2.5, 5.0), ("moss", 13, 2.0, 3.6), ("toad", 11, 1.8, 3.0), ("glow", 10, 1.5, 2.6),
          ("pink", 8, 2.0, 3.4), ("violet", 8, 2.0, 3.4), ("white", 9, 2.0, 3.6), ("gold", 7, 2.0, 3.2)]


def undergrowth(t):
    rng = t.rng
    forest = t.forest
    # cells to keep walkable around paths, doors, people, items
    walk = set()
    for y in range(H):
        for x in range(W):
            if t.g[y][x] == ":":
                walk |= {(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
    for c in t.fronts + t.doors + [(o["x"], o["y"]) for o in t.objects] + [(i["x"], i["y"]) for i in t.items]:
        walk |= {(c[0] + i, c[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
    # Chebyshev distance to the ring's trees and thickets
    dist = {(x, y): 99 for y in range(H) for x in range(W)}
    tree_names = {"Ring tree", "Thicket"}
    tc = set()
    for b in t.b:
        if b["label"] in tree_names:
            tc |= set(t.box(b["prefab"], b["x"], b["y"]))
    cur = list(tc)
    for c in cur:
        dist[c] = 0
    d = 0
    while cur and d < 8:
        d += 1
        nxt = []
        for x, y in cur:
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    n = (x + i, y + j)
                    if n in dist and dist[n] > d:
                        dist[n] = d
                        nxt.append(n)
        cur = nxt
    n_bush = noise_grid(rng, 5)       # where the bushes thicken
    free = lambda x, y: t.g[y][x] == "." and (x, y) not in t.occ

    # -- blocking understory first: bushes thicken near the trees (in clumps), a few mossy logs lie along the ring
    cells = [(x, y) for y in range(H) for x in range(W) if free(x, y) and (x, y) not in walk]
    rng.shuffle(cells)
    for x, y in cells:
        dtree = dist[(x, y)]
        base = 0.30 if dtree <= 1 else 0.20 if dtree == 2 else 0.12 if dtree == 3 else 0.04 if dtree <= 5 else 0.0
        if rng.random() < base * (0.2 + 2.0 * n_bush(x, y) ** 2):
            t.deco(rng.choice(BUSHES), x, y, "Bush")
    logs = 0
    for _ in range(400):
        if logs >= LOGS:
            break
        x, y = rng.randrange(2, W - 3), rng.randrange(2, H - 3)
        if 2 <= dist[(x, y)] <= 5 and not any(c in walk for c in t.box("mossy_log", x, y))                 and t.deco("mossy_log", x, y, "Mossy log"):
            logs += 1

    # -- walkable ground cover in drifts: each drift is an ellipse of one plant (ferns, moss and toadstools in the
    # shade, flowers in the open), thick in the middle and thinning out; a faint scatter of ferns and moss elsewhere
    drifts = []
    for kind, count, rmin, rmax in DRIFTS:
        for _ in range(count):
            for _try in range(40):
                cx, cy = rng.uniform(3, W - 3), rng.uniform(3, H - 3)
                if free(int(cx), int(cy)) and not wet(t, int(cx), int(cy), 1):
                    drifts.append((kind, cx, cy, rng.uniform(rmin, rmax), rng.uniform(rmin, rmax) * 0.8))
                    break
    for k, deg in enumerate(range(10, 360, 36)):    # a few flowers in the strip between the loop and the pond
        th = math.radians(deg)
        r = pond_r(th) + 2.6
        drifts.append((("pink", "violet", "white", "gold", "glow")[k % 5], CX + r * math.cos(th), CY + r * math.sin(th),
                       2.4, 1.8))
    path_near = {c for c in walk if t.at(*c) == "."}
    cells = [(x, y) for y in range(H) for x in range(W) if free(x, y)]
    rng.shuffle(cells)
    for x, y in cells:
        if not free(x, y):
            continue
        best, kind = 0.0, None
        for k, cx, cy, rx, ry in drifts:
            v = 1.0 - (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
            if v > best:
                best, kind = v, k
        if kind is None:
            if rng.random() > (0.14 if dist[(x, y)] <= 3 else 0.08):
                continue
            kind = rng.choice(("fern", "fern", "moss", "white"))
        elif rng.random() > 0.40 + 0.55 * best:
            continue
        elif rng.random() < 0.18:      # a companion plant in the drift
            kind = rng.choice(("fern", "moss"))
        if (x, y) in path_near and rng.random() < 0.5:
            continue
        p = {"fern": lambda: rng.choice(FERNS), "moss": lambda: "moss_mound", "toad": lambda: rng.choice(TOADS),
             "glow": lambda: "glowbell", "pink": lambda: "bloom_pink", "violet": lambda: "bloom_violet",
             "white": lambda: "bloom_white", "gold": lambda: "bloom_gold"}[kind]()
        t.deco(p, x, y, "Undergrowth")


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [  # (file stem, title, x0, y0, x1, y1) in tiles
    ("gym", "The gym: the moss curtains", 16, 0, 36, 13),
    ("center", "Pokemon Center: the hollow tree", 0, 7, 20, 22),
    ("cottage_n", "Moss cottage N, pepper plot and fairy ring", 30, 0, 50, 17),
    ("cottage_s", "Moss cottage S and the lane", 0, 19, 24, 38),
    ("herbalist", "Herbalist and the south-east glade", 28, 19, 50, 38),
    ("ring_entrance", "Tree ring and the Route 13 entrance", 0, 24, 14, 38),
    ("pond", "Pond loop, reflecting pools, false Lutins", 10, 6, 40, 32),
    ("peppers_w", "Pepper plot and fairy ring, west glades", 0, 0, 16, 24),
]


def review(out):
    from PIL import Image, ImageDraw, ImageFont
    import build
    from render import Tilesets, render
    build.MAPPING.clear()
    b = build.Builder(SPEC)
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    clean = render(ts, b.flat(), b.w).convert("RGB")
    sheet_png = os.path.join(HERE, "maps", "00_town_lutins_hollow.png")
    subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "town_sheet.py"), KEY, sheet_png], check=True)
    top = Image.open(sheet_png).convert("RGB")
    cdir = os.path.join(HERE, "maps", "hollow_crops")
    os.makedirs(cdir, exist_ok=True)
    crops = []
    for stem, title, x0, y0, x1, y1 in REVIEW_AREAS:
        c = clean.crop((x0 * 16, y0 * 16, min(x1, W) * 16, min(y1, H) * 16))
        c = c.resize((c.width * 3, c.height * 3), Image.NEAREST)
        c.save(os.path.join(cdir, stem + ".png"))
        crops.append((title, c))
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    pad, head = 24, 48
    width = max(top.width, 2600)
    rows, row, rw = [], [], pad
    for title, c in crops:
        if row and rw + c.width + pad > width:
            rows.append(row)
            row, rw = [], pad
        row.append((title, c))
        rw += c.width + pad
    rows.append(row)
    height = top.height + pad + sum(max(c.height for _, c in r_) + head for r_ in rows) + pad
    sheet = Image.new("RGB", (width, height), (250, 248, 242))
    sheet.paste(top, (0, 0))
    d = ImageDraw.Draw(sheet)
    y = top.height + pad
    for r_ in rows:
        x = pad
        for title, c in r_:
            d.text((x, y + 8), title, fill=(0, 0, 0), font=font)
            sheet.paste(c, (x, y + head))
            x += c.width + pad
        y += max(c.height for _, c in r_) + head
    sheet.save(out)
    print("review sheet:", out, sheet.size)


# ---------------------------------------------------------------- main
def run(args, **kw):
    return subprocess.run([sys.executable, "-W", "ignore"] + args, text=True, capture_output=True, **kw)


def build_town(bare=False):
    t = Town()
    pond(t)
    buildings(t)
    paths(t)
    protect = set(t.fronts) | set(t.doors)
    smooth(t, protect, passes=0)
    tidy(t, protect)
    if bare:      # terrain, buildings and paths only (to read the terrain seams without the stand-ins' noise)
        return t
    make_forest(t)
    fairy(t)
    people(t)
    pools(t)
    signs(t)
    trees(t)
    undergrowth(t)
    return t


def main(args):
    # the tileset config first: the pieces' footprints come from it
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-200:])
    t = build_town("--bare" in args)
    if "--ascii" in args:
        sym = {"~": "~", ":": ":", ".": ".", "#": "#"}
        occ_name = {}
        for b in t.b:
            for c in t.box(b["prefab"], b["x"], b["y"]):
                occ_name[c] = b["prefab"]
        for y in range(H):
            line = ""
            for x in range(W):
                if (x, y) in occ_name:
                    n = occ_name[(x, y)]
                    line += "T" if n.startswith(("tree", "thicket")) else "B" if n in ("gym_arbour", "hollow_tree", "cottage_a", "cottage_b", "herbalist") else "o"
                else:
                    line += t.g[y][x]
            print(f"{y:2d} {line}")
    if t.skipped:
        print("left out (no room or no art yet):", len(t.skipped), t.skipped[:30])
    if t.stand_ins:
        print("stand-ins in use (art not delivered yet):", sorted(t.stand_ins))
    print("placed:", dict(sorted(t.counts.items())))
    open(os.path.join(HERE, "maps", KEY + ".grid.txt"), "w").write(t.grid_text())
    lid, ldir = shell(NAME, CONST, "town", "MAPSEC_LUTINS_HOLLOW", "MUS_RG_LAVENDER", W, H, t.cfg)
    spec = {"_comment": "Lutin's Hollow, handmade: generated by hollow.py (edit that, not this file).",
            "map": NAME, "map_const": CONST, "layout": lid, "layout_dir": ldir, "tileset": CFG,
            "mockup": "../orleans_maps/07_lutins_hollow.png", "grid": KEY + ".grid.txt", "edits": [],
            "buildings": t.b, "objects": t.objects, "surf_only": [], "items": t.items, "hidden_items": t.hidden,
            "signs": t.signs,
            "exits": [{"name": "Route 13 lane (west)", "cells": [[0, y] for y in EXIT_ROWS]}]}
    dump(SPEC, spec)
    if "--no-build" in args:
        return
    art = os.path.join(HERE, "sources", "orleans_custom", "make_hollow_art.py")
    if "hollow.json" in open(art, encoding="utf-8").read():   # the art agent's registration layer has landed
        print(run([art]).stdout.strip()[-300:])
    print(run([os.path.join(HERE, "make_town_tilesets.py"), CFG]).stdout.strip()[-300:])
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    if "--fresh" in args:  # start the overlay requests over, so pieces no longer used don't take tiles
        bf = os.path.join(HERE, "tilesets", CFG + ".blends.json")
        with open(bf, "w") as f:
            json.dump([], f)
    flags = [a for a in args if a == "--dry-run"]
    for i in range(6):  # build (writes the uses file and asks for overlays), compose, build again
        r = run([os.path.join(HERE, "build.py"), SPEC] + flags)
        print(r.stdout.strip()[-1500:], r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = run([os.path.join(HERE, "compose.py"), recipe])
        print(c.stdout.strip()[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return
    c = run([os.path.join(HERE, "check.py"), SPEC])
    print(c.stdout.strip()[-3000:], c.stderr.strip()[-2000:])
    if "--review" in args:
        review(os.path.join(HERE, "maps", "00_lutins_hollow_review.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

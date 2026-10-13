"""Edge transitions ("feather to the border"), user request 2026-10-13.  Brief: edge_feather_plan.md (gitignored).

A map's unconnected edges (and the part of an edge a connection does not cover, and the corners) used to end in a straight line:
a one-cell hedge, a 2-cell canopy wall, terrain cut dead against open water.  This pass shapes an organic transition INSIDE the map
whose outermost cells are the border block itself and whose inner outline wanders.  It runs inside borders.prepare / borders.apply,
i.e. inside build.py's Builder, so every generator and repro_check reproduce it.  It never touches map.bin by hand.

Styles (borders.STYLE):
  swamp / dry   canopy (scrub) wall.  The wall is the border block continued inward (wall cell (x, y) = block[(x & 1) + (y & 1) * 2]),
                so its outer cells are indistinguishable from the border.  The art's edge cells (borders.json) hang the wall's trees
                over the first terrain cell beside it and need the wall face on a fixed parity (see borders.py), so the wall is a union
                of 2x2 blocks aligned to the even grid (an odd last row / column of a map is a half block, always wall).  Depth along an
                edge is a seeded random walk of 0..MAXB blocks (steps of one block, runs of 1-2 blocks = 2-4 cells), i.e. canopy 1..5 cells deep.
                Faces S/N/E/W and the four INNER corners (in_NW ...) exist; the OUTER (convex) corner pieces do not: those cells
                stay plain terrain and are listed in b.feather_missing (see edge_feather_missing.md for the art spec).
  water         land recedes: grid land cells within d (2..5, wandering) of the edge become water, so the engine's own water-bank
                autotile draws a shoreline, and the outer rows are open water like the border.  Land that cannot recede (a building,
                path, door, NPC within a cell of the carved water) is reported in b.feather_report (a map-specific decision).

Gameplay is never changed: events, doors, exits, paths, trainer sight lines, structures and the cells a story state swaps are protected
(a wall, edge cell or new water may not touch them; walls shorten instead).  Seam bands are untouched: wall/edge cells never lie in the
connected overlap, and dry maps (whose scrub art is not primary) never put one in a strict band.

Entry point (called by borders.prepare): prepare(b, key, style, sp, keep_open, strict_all) sets b.wall / b.edge for borders.apply (canopy
styles) or edits b.grid (water style).  FEATHER lists the maps this is switched on for (the prototype: three maps).
"""
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bands  # noqa: E402

FEATHER = {"isle_marais", "storms_edge", "route_16"}
STUB_MAX = 60                 # patches bigger than this are never turned plain (Redfield's cane fields run across its join with Route 17)
MAXB = 2                      # canopy depth in 2x2 blocks (0..MAXB): 1..5 cells including the overhang cell
ROAD = set(":=p%&B")          # grid characters of paths / paving / levee ground: never covered
LAND = set(".\"dGgLSeqQwysrvp:=%&")
WATERCH = set("~Iw")
LANDW = set(".\"GgLd")       # ground a water border recedes (land and marsh); never a road, levee or open water
FACE_DIR = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


SCRIPT_XY = re.compile(r"setobjectxy(?:perm)?\s+\w+\s*,\s*(\d+)\s*,\s*(\d+)")
LINE_TRIGGER = re.compile(r"WaterGate|DustStorm|FloodedRoad|SandstormTrigger|SunTrigger|ViciousSandstorm|LairEnter")   # (LairEnter: the legendary lairs' entrance triggers sit in the wall notch, they do not shape it)
DECOR = re.compile(r"^(cypress|reeds|reed|snag|waterlog|lily|knee|stump|tall|weed|bush|shrub|flower|rock|boulder|log)", re.I)


def landmarks(b):
    """cells of prefabs that are not plain decor (landmarks, wires, rails, benches ...): the pass never covers them"""
    br = __import__("band_rules")
    out = set()
    for bd in b.spec.get("buildings", []):
        if not DECOR.match(bd["prefab"]):
            out |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    return out


def _rng(*parts):
    return random.Random("|".join(str(p) for p in parts))


def protected(b, key, extras=True):
    """cells that must stay exactly as they are: events, doors, exits, structures, paths, trainer sight lines"""
    P = set()
    spec = b.spec
    for coll in ("objects", "items", "signs", "hidden_items", "triggers"):
        P |= {(o["x"], o["y"]) for o in spec.get(coll, []) if not o.get("gate")}
    P |= {tuple(c) for c in spec.get("keep_open", [])}
    for ex in spec.get("exits", []):
        P |= {tuple(c) for c in ex["cells"]}
    for bd in spec.get("buildings", []):
        p = b.ts["prefabs"][bd["prefab"]]
        door = p.get("door")
        for dx, dy in ([] if not door else door if isinstance(door[0], list) else [door]):
            P |= {(bd["x"] + dx, bd["y"] + dy), (bd["x"] + dx, bd["y"] + dy + 1)}
    br = __import__("band_rules")
    for bd in spec.get("buildings", []) if extras else []:
        if br.is_structure(b, bd):
            P |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    for cells in spec.get("states", {}).values() if extras else []:
        P |= {(c["x"], c["y"]) for c in cells}
    # the committed map.json also holds what the story pass added (people, trainers, coord triggers, warps)
    path = os.path.join(bands.ROOT, "data", "maps", spec["map"], "map.json")
    if os.path.exists(path):
        d = json.load(open(path, encoding="utf-8"))
        for o in d.get("object_events", []):
            P.add((o["x"], o["y"]))
            if o.get("trainer_type") not in (None, "TRAINER_TYPE_NONE"):
                try:
                    sight = int(o.get("trainer_sight_or_berry_tree_id", 4))
                except ValueError:
                    sight = 4
                mv = o.get("movement_type", "")
                dirs = [v for k, v in FACE_DIR.items() if mv.endswith("FACE_" + k)] or list(FACE_DIR.values())
                for dx, dy in dirs:
                    for i in range(1, sight + 2):
                        P.add((o["x"] + dx * i, o["y"] + dy * i))
        for k in ("warp_events", "coord_events", "bg_events"):
            for o in d.get(k, []):
                if k == "coord_events" and LINE_TRIGGER.search(o.get("script", "")):
                    continue            # a gate / storm line is written across the whole route and must not shape the terrain
                P.add((o["x"], o["y"]))
    # cells a script stands an object on (setobjectxy / setobjectxyperm: Route 3's Jayden standoff rows ...): they and their neighbours stay open
    for path in (os.path.join(bands.ROOT, "data", "maps", spec["map"], "scripts.inc"), os.path.join(HERE, "story", spec["map"] + ".inc")):
        if os.path.exists(path):
            for m_ in SCRIPT_XY.finditer(open(path, encoding="utf-8", errors="replace").read()):
                x_, y_ = int(m_.group(1)), int(m_.group(2))
                P |= {(x_ + i, y_ + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
    for y in range(b.h) if extras else []:
        for x in range(b.w):
            if b.grid[y][x] in ROAD:
                P.add((x, y))
    return {c for c in P if 0 <= c[0] < b.w and 0 <= c[1] < b.h}


def dilate(cells, r, w, h):
    out = set()
    for x, y in cells:
        for j in range(-r, r + 1):
            for i in range(-r, r + 1):
                if 0 <= x + i < w and 0 <= y + j < h:
                    out.add((x + i, y + j))
    return out


def walk(rng, n, lo, hi, free):
    """a profile of n values in lo..hi: steps of one, runs of 1-2 entries; free[i] False forces lo there"""
    out, v, run = [], rng.randint(lo, hi), 0
    want = rng.choice((1, 2))
    for i in range(n):
        if run >= want:
            opts = [u for u in (v - 1, v + 1) if lo <= u <= hi]
            v = rng.choice(opts) if opts else v
            run, want = 0, rng.choice((1, 2))
        out.append(v)
        run += 1
    return [v if free[i] else lo for i, v in enumerate(out)]


def relax(vals, lo):
    """no step bigger than one between neighbours (lower the higher one) so every step is one block: edge pieces exist for it"""
    vals = list(vals)
    for _ in range(len(vals)):
        ch = False
        for i in range(len(vals)):
            for j in (i - 1, i + 1):
                if 0 <= j < len(vals) and vals[i] > vals[j] + 1:
                    vals[i] = vals[j] + 1
                    ch = True
        if not ch:
            break
    return vals


def side_geom(b, side):
    """(n_blocks along, cell(i, k) -> map cell i along the side, k in from the edge)"""
    w, h = b.w, b.h
    if side in "NS":
        return w, lambda i, k: (i, k) if side == "N" else (i, h - 1 - k)
    return h, lambda i, k: (k, i) if side == "W" else (w - 1 - k, i)


def seam_zone(key, depth=3):
    """map cells within `depth` of the edge column/row along every connected overlap: the neighbour's strip is drawn right beside them,
    so the terrain there is the seam's and this pass leaves it alone"""
    I = bands.info()
    w, h = I[key]["w"], I[key]["h"]
    cells = set()
    for a, sa, b2, sb, loa, hia, lob, hib in bands.joins():
        for me, side, lo, hi in ((a, sa, loa, hia), (b2, sb, lob, hib)):
            if me != key:
                continue
            for i in range(lo, hi):
                for k in range(depth):
                    cells.add({"N": (i, k), "S": (i, h - 1 - k), "W": (k, i), "E": (w - 1 - k, i)}[side])
    return cells


def side_geom(b, side):
    """(length of the side, cell(i, k): the map cell at position i along the side, k cells in from the edge)"""
    w, h = b.w, b.h
    if side in "NS":
        return w, (lambda i, k: (i, k)) if side == "N" else (lambda i, k: (i, h - 1 - k))
    return h, (lambda i, k: (k, i)) if side == "W" else (lambda i, k: (w - 1 - k, i))


def walk(rng, n, lo, hi, runs):
    """n values in lo..hi, steps of one, each value held for a run drawn from `runs`"""
    out, v = [], rng.randint(lo, hi)
    while len(out) < n:
        out += [v] * rng.choice(runs)
        opts = [u for u in (v - 1, v + 1) if lo <= u <= hi]
        v = rng.choice(opts)
    return out[:n]


def relax(vals, cap):
    """cap each value (cap[i]) and keep neighbouring steps at one by lowering the higher side"""
    vals = [min(v, c) for v, c in zip(vals, cap)]
    ch = True
    while ch:
        ch = False
        for i in range(len(vals)):
            for j in (i - 1, i + 1):
                if 0 <= j < len(vals) and vals[i] > vals[j] + 1:
                    vals[i] = vals[j] + 1
                    ch = True
    return vals


def wall_cells(b, prof):
    """the wall: per 2x2 block of each side, 2m cells deep (an odd map's last row / column is always wall: its first wall row must be even)"""
    wall = set()
    for (side, lo, hi), vals in prof.items():
        n, cell = side_geom(b, side)
        dim = b.h if side in "NS" else b.w
        off = (dim % 2) if side in "SE" else 0
        inside = b.feather_inside[(side, lo, hi)]
        for j, m in enumerate(vals):
            cols = [i for i in (2 * j, 2 * j + 1) if i < n and lo <= i < hi]
            if not cols or not inside[j]:
                continue
            for i in cols:
                for k in range(2 * m + off):
                    wall.add(cell(i, k))
    return wall


def classify(b, wall, sp):
    """(edge {cell: face}, wall): every terrain cell 4-adjacent to the wall (the border counts as wall along the unconnected spans);
    a cell squeezed between walls becomes wall"""
    w, h = b.w, b.h
    wall = set(wall)

    def is_wall(x, y):
        if 0 <= x < w and 0 <= y < h:
            return (x, y) in wall
        if x < 0 and 0 <= y < h:
            return any(lo <= y < hi for lo, hi in sp["W"])
        if x >= w and 0 <= y < h:
            return any(lo <= y < hi for lo, hi in sp["E"])
        if y < 0 and 0 <= x < w:
            return any(lo <= x < hi for lo, hi in sp["N"])
        if y >= h and 0 <= x < w:
            return any(lo <= x < hi for lo, hi in sp["S"])
        return True
    while True:
        edge, added = {}, False
        for y in range(h):
            for x in range(w):
                if (x, y) in wall:
                    continue
                n, s, we, e = is_wall(x, y - 1), is_wall(x, y + 1), is_wall(x - 1, y), is_wall(x + 1, y)
                if not (n or s or we or e):
                    continue
                if (n and s) or (we and e) or n + s + we + e >= 3:
                    wall.add((x, y))
                    added = True
                    continue
                face = ("in_NW" if n and we else "in_NE" if n and e else "in_SW" if s and we else "in_SE" if s and e
                        else "S" if n else "N" if s else "E" if we else "W")
                edge[(x, y)] = face
        if not added:
            for y in range(h):          # outer (convex) corners: only a diagonal touches the wall (art: make_borders.outer_cell)
                for x in range(w):
                    if (x, y) in wall or (x, y) in edge:
                        continue
                    for dx, dy, nm in ((-1, -1, "out_NW"), (1, -1, "out_NE"), (-1, 1, "out_SW"), (1, 1, "out_SE")):
                        if (x + dx, y + dy) in wall:
                            edge[(x, y)] = nm
                            break
            return edge, wall


def missing_corners(b, wall, edge):
    """terrain cells whose only wall contact is diagonal (the outside of a convex wall corner): the art has no piece for them yet"""
    out = []
    for y in range(b.h):
        for x in range(b.w):
            if (x, y) in wall or (x, y) in edge:
                continue
            for dx, dy, nm in ((-1, -1, "out_NW"), (1, -1, "out_NE"), (-1, 1, "out_SW"), (1, 1, "out_SE")):
                if (x + dx, y + dy) in wall:
                    out.append((x, y, nm))
    return out


def canon(style, ch):
    """the plain ground an edge cell stands on, or None when it cannot be made plain here"""
    if style == "swamp":
        # mud keeps its own edge cells (commit 577fe08f4f: canopy over ekat:mud_C, bk_swamp_*_834ef142); a churchyard cell is baked over its own tile
        return {'"': '"', ".": ".", "~": "~", "I": "~", "w": "~", "G": ".", "L": "L", "S": "S", "d": ".", "g": "."}.get(ch)
    return {"d": "d", "G": "d", "g": "d", "q": "d", "Q": "d", "e": "d", "y": "d", "s": "d", "r": "d", "v": "d", ".": "d", "L": "d", "w": "d"}.get(ch)


def prepare(b, key, style, sp, keep_open, strict_all):
    b.feather_strict = strict_all
    """canopy styles: choose the wall, set b.wall / b.edge / b.border_depth and bend b.grid under them.  water: recede the land."""
    b.feather_missing, b.feather_report = [], []
    if style == "water":
        return prepare_water(b, key, sp, keep_open)
    return prepare_canopy(b, key, style, sp, keep_open, strict_all)


def groves(b):
    """the marsh groves of the spec (cypress on a marsh patch, with the patch's window): the wall gives way round them rather than eating them"""
    br = __import__("band_rules")
    out = set()
    for bd in b.spec.get("buildings", []):
        if bd["prefab"] in ("cypress_marsh", "cypress_small_marsh"):
            for x, y, _ in br.prefab_cells(b, bd):
                out |= {(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
    return {c for c in out if 0 <= c[0] < b.w and 0 <= c[1] < b.h}


def prepare_canopy(b, key, style, sp, keep_open, strict_all, maxb=MAXB):
    w, h = b.w, b.h
    P = protected(b, key) | keep_open | landmarks(b)
    if style == "swamp" and b.spec.get("feather", {}).get("keep_groves"):      # a town that wants its bayou groves (Isle Marais): the wall retreats round them
        P |= groves(b)
    PD = dilate(P, 1, w, h)
    forbid = seam_zone(key, 3)
    if style == "dry":
        forbid |= strict_all
    prof, caps = {}, {}
    b.feather_inside = {}
    for side in "NSWE":
        n, cell = side_geom(b, side)
        nb = (n + 1) // 2
        for lo, hi in sp[side]:
            vals = walk(_rng(key, side, lo, "canopy"), nb, 0, maxb, (1, 2))
            inside = [lo <= 2 * j and min(2 * j + 1, n - 1) < hi for j in range(nb)]
            b.feather_inside[(side, lo, hi)] = inside
            cap = [maxb if inside[j] else 0 for j in range(nb)]
            for j in range(nb):          # a block beside a connected stretch stays plain: the wall tapers into the border
                for jj in (j - 1, j + 1):
                    if 0 <= jj < nb and not inside[jj]:
                        cap[j] = 0
            prof[(side, lo, hi)] = relax(vals, cap)
            caps[(side, lo, hi)] = cap
    sets = "qQGgwsvr" if style == "dry" else "Gg"
    comps, seen_c = [], set()
    for y0 in range(h):                      # patches of crops / cane / tall grass / mud: a wall that bites a corner off one leaves an orphan stub
        for x0 in range(w):
            if b.grid[y0][x0] in sets and (x0, y0) not in seen_c:
                ch0, comp, todo = b.grid[y0][x0], set(), [(x0, y0)]
                while todo:
                    q = todo.pop()
                    if q in comp or not (0 <= q[0] < w and 0 <= q[1] < h) or b.grid[q[1]][q[0]] != ch0:
                        continue
                    comp.add(q)
                    todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
                seen_c |= comp
                comps.append(comp)

    def cost(prof):
        wall = wall_cells(b, prof)
        edge, wall = classify(b, wall, sp)
        c = 0
        for q in wall:
            if q in PD or q in forbid:
                c += 1000
        for (x, y) in edge:
            if (x, y) in P or (x, y) in forbid:
                c += 2           # left plain (no overhang piece there): a mild blemish, never a conflict
                continue
            if canon(style, b.grid[y][x]) is None:
                c += 8
                continue
            seen = {canon(style, b.grid[cy][cx]) for cx, cy in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
                    if cx < w and cy < h and (cx, cy) not in wall}
            if len(seen) > 1:
                c += 25          # a terrain boundary under the overhang: the edge cell would not be a plain ground cell
        cover = wall | set(edge)
        for comp in comps:
            n_in = len(comp & cover)
            if 0 < n_in < len(comp) and len(comp) <= STUB_MAX:
                c += 30
        for vals in prof.values():
            k = 1
            for a, b_ in zip(vals, vals[1:] + [None]):
                if b_ == a:
                    k += 1
                else:
                    c += max(0, k - 2) * 4       # no straight run longer than 2 blocks (4 cells)
                    k = 1
        return c
    def clear_conflicts():
        """lower every block whose wall touches a forbidden / protected cell (two sides can cover the same corner cells)"""
        for _ in range(20):
            wall = wall_cells(b, prof)
            edge, wall = classify(b, wall, sp)
            badw = {q for q in wall if q in PD or q in forbid}
            if not badw:
                return
            for (side, lo, hi), vals in prof.items():
                n, cell = side_geom(b, side)
                for j, m in enumerate(vals):
                    if any(cell(i, k) in badw for i in (2 * j, 2 * j + 1) if i < n for k in range(2 * m + 1 + (side in "SE" and (b.h if side == "S" else b.w) % 2))):
                        if m:
                            vals[j] = m - 1
                        else:
                            b.feather_inside[(side, lo, hi)][j] = False      # the odd map's forced last row would land on something
                prof[(side, lo, hi)] = relax(vals, caps[(side, lo, hi)])

    clear_conflicts()
    best = cost(prof)
    for _ in range(5):
        moved = False
        for key_, vals in prof.items():
            for j in range(len(vals)):
                for m in range(caps[key_][j] + 1):
                    if m == vals[j]:
                        continue
                    trial = list(vals)
                    trial[j] = m
                    trial = relax(trial, caps[key_])
                    old = prof[key_]
                    prof[key_] = trial
                    c = cost(prof)
                    if c < best:
                        best, vals, moved = c, trial, True
                    else:
                        prof[key_] = old
                prof[key_] = vals
        if not moved:
            break
    clear_conflicts()
    b.feather_cost = best
    wall = wall_cells(b, prof)
    edge, wall = classify(b, wall, sp)
    for c in list(edge):          # depth-0 edge cells (against the border itself) may still sit on something unusable: left plain
        if c in P or c in forbid or canon(style, b.grid[c[1]][c[0]]) is None:
            edge.pop(c)
            b.feather_report.append(f"edge cell {c} left plain (event, seam or ground the art cannot draw)")
    cover = wall | set(edge)
    plain = "d" if style == "dry" else "."
    stubs = 0
    for comp in comps:                       # what is left of a crop / cane / tall-grass patch the wall bit into becomes plain ground
        n_in = len(comp & cover)
        if 0 < n_in < len(comp) and len(comp) <= STUB_MAX:      # only a small patch is left as an orphan stub; a big field just runs on under the wall
            for (x, y) in comp - cover:
                if (x, y) not in P and b.grid[y][x] != "w":
                    b.grid[y][x] = plain
                    stubs += 1
    if stubs:
        b.border_log.append(f"feather: {stubs} cells of patches the wall bit into became plain ground")
    # the ground: every edge cell and the 2x2 corner window its dual-grid tile reads is one plain terrain; the wall takes its neighbour's
    T = {c: canon(style, b.grid[c[1]][c[0]]) for c in edge}
    for (x, y), t in sorted(T.items()):
        b.grid[y][x] = t
    for (x, y), t in sorted(T.items()):
        if t in "LS":              # mud / churchyard: its window is left alone (mud never touches marsh; the overhang is baked over whatever is there)
            continue
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            cx, cy = x + dx, y + dy
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in P and (cx, cy) not in wall and (cx, cy) not in edge:
                if b.grid[cy][cx] in LAND | WATERCH and b.grid[cy][cx] not in ROAD:
                    b.grid[cy][cx] = t
    owner, todo = dict(T), list(T.items())
    while todo:
        nxt = []
        for (x, y), t in todo:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (x + dx, y + dy)
                if c in wall and c not in owner:
                    owner[c] = t
                    nxt.append((c, t))
        todo = nxt
    for (x, y), t in owner.items():
        if (x, y) in wall:
            b.grid[y][x] = t
    for (x, y) in wall:
        if (x, y) not in owner:
            b.grid[y][x] = "." if style == "swamp" else "d"
    # props under the wall / edge cells go (structures never get here: protected)
    zone = wall | set(edge)
    br = __import__("band_rules")
    keep, dropped = [], []
    for bd in b.spec.get("buildings", []):
        cells = {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
        (dropped if (cells & zone) else keep).append(bd)
    if dropped:
        b.spec["buildings"] = keep
        gone = {(x, y) for bd in dropped for x, y, _ in br.prefab_cells(b, bd)}
        b.spec["signs"] = [g for g in b.spec.get("signs", []) if (g["x"], g["y"]) not in gone]
        by = {}
        for bd in dropped:
            by[bd["prefab"]] = by.get(bd["prefab"], 0) + 1
        b.border_log.append("feather: props under the wall taken out: " + ", ".join(f"{k} x{v}" for k, v in sorted(by.items())))
        moved, lost = regrow(b, [d for d in dropped if _regrowable(d)], zone, P, forbid=forbid)
        if moved or lost:
            b.border_log.append(f"feather: {len(moved)} of {len(moved) + len(lost)} dropped decor props regrown nearby" + (f"; lost: {', '.join(sorted({d['prefab'] for d in lost}))}" if lost else ""))
    if style == "swamp":          # the seam bands are primary-only: a baked edge cell (bk_, a secondary patch) may not stand in one
        for c in list(edge):
            if c not in strict_all:
                continue
            x_, y_ = c
            face_ = edge[c]
            ground = {canon(style, b.grid[cy][cx]) for cx, cy in ((x_, y_), (x_ + 1, y_), (x_, y_ + 1), (x_ + 1, y_ + 1))
                      if cx < w and cy < h and (cx, cy) not in wall}
            if len(ground) != 1 or (face_.startswith("out_") and ground != {"."}) or ground - set('".~'):
                edge.pop(c)
                b.feather_report.append(f"edge cell {c} left plain (a baked piece may not stand in a seam band)")
    b.feather_bake = True        # an edge cell on a ground the art has no piece for (a bank, a blend) is baked: the overhang over that cell's pixels
    b.wall, b.edge = wall, edge
    b.border_depth = {s_: max((max(v) * 2 for (sd, lo, hi), v in prof.items() if sd == s_), default=0) for s_ in "NSWE"}
    b.feather_prof = prof
    b.feather_missing = []     # outer corners have art now (bake: bk_/bdg_ <style>_out_<corner>)
    exp = surf_exposure(b, key, sp)
    b.feather_exposed = exp
    if exp:
        b.feather_report.append("surf exposure: " + ", ".join(f"{s_}: {len(v)} positions {_ranges(v)}" for s_, v in exp.items()))
    b.border_log.append(f"feather {style}: {len(wall)} wall cells, {len(edge)} edge cells, {len(b.feather_missing)} outer corners without art")
    return True


def prepare_water(b, key, sp, keep_open):
    """water border: the land recedes so the outermost cells are open water; the shoreline wanders 2..5 cells in (banks come from the
    water autotile). Nothing protected is touched; where land has to stay within 2 cells of the edge it is reported."""
    w, h = b.w, b.h
    P = protected(b, key) | keep_open | landmarks(b)
    br = __import__("band_rules")
    structure = set()
    for bd in b.spec.get("buildings", []):
        if br.is_structure(b, bd):
            structure |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    PD = dilate(P | structure, 2, w, h)     # a shore cell is a bank piece: two cells keep every prop on plain land
    seam = seam_zone(key, 3)
    carved = 0
    carved_cells = set()
    cuts = []
    for side in "NSWE":
        n, cell = side_geom(b, side)
        for lo, hi in sp[side]:
            want = walk(_rng(key, side, lo, "shore"), hi - lo, 4, 6, (2, 3, 4))
            cap = []
            for i in range(lo, hi):
                lim = 7
                for k in range(7):
                    c = cell(i, k)
                    if c in PD or c in seam or b.grid[c[1]][c[0]] in "B#":
                        lim = k
                        break
                cap.append(lim)
            pins = (b.spec.get("feather", {}).get("shore_pins", {}) or {}).get(side, {})
            for pos, dmax in pins.items():          # spec "feather": {"shore_pins": {side: {position: max carve depth}}}: the shore stays this near here
                if lo <= int(pos) < hi:
                    cap[int(pos) - lo] = min(cap[int(pos) - lo], dmax)
            d = relax(want, cap)
            for i in range(lo, hi):
                if cap[i - lo] < 2:
                    if any(b.grid[cell(i, k)[1]][cell(i, k)[0]] not in WATERCH for k in range(2)):
                        cuts.append((side, i))
                for k in range(d[i - lo]):
                    x, y = cell(i, k)
                    if b.grid[y][x] in LANDW:
                        b.grid[y][x] = "~"
                        carved += 1
                        carved_cells.add((x, y))
    water = carved_cells
    keep, dropped = [], []
    for bd in b.spec.get("buildings", []):
        cells = {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
        if (cells & water) and not br.is_structure(b, bd) and not _water_prop(bd):
            dropped.append(bd)
        else:
            keep.append(bd)
    if dropped:
        b.spec["buildings"] = keep
        by = {}
        for bd in dropped:
            by[bd["prefab"]] = by.get(bd["prefab"], 0) + 1
        b.border_log.append("feather: props in the receded water taken out: " + ", ".join(f"{k} x{v}" for k, v in sorted(by.items())))
        moved, lost = regrow(b, [d for d in dropped if _regrowable(d)], carved_cells, P | structure, forbid=seam)
        if moved or lost:
            b.border_log.append(f"feather: {len(moved)} of {len(moved) + len(lost)} dropped decor props regrown nearby" + (f"; lost: {', '.join(sorted({d['prefab'] for d in lost}))}" if lost else ""))
    groups = {}
    for side, i in cuts:
        groups.setdefault(side, []).append(i)
    for side, v in groups.items():
        b.feather_report.append(f"{side} edge: land within 2 cells of the edge at positions {_ranges(v)} cannot recede (building / path / event / seam)")
    b.border_log.append(f"feather water: {carved} land cells became water")
    b.wall, b.edge = set(), {}
    strict_all = getattr(b, "feather_strict", set())
    prepare_barrier(b, key, sp, P | structure, seam, strict_all, events=protected(b, key, extras=False))
    exp = surf_exposure(b, key, sp)
    b.feather_exposed = exp
    if exp:
        b.feather_report.append("surf exposure after the barrier: " + ", ".join(f"{s}: {len(v)} positions" for s, v in exp.items()))
    return True


def _regrowable(bd):
    return bool(DECOR.match(bd["prefab"]))


def _water_prop(bd):
    return bd["prefab"] in ("waterlog", "snag_water", "cypress_water") or str(bd.get("label", "")).startswith("Water")


def _ranges(v):
    v = sorted(set(v))
    out, s = [], v[0]
    for a, c in zip(v, v[1:] + [None]):
        if c != a + 1:
            out.append(f"{s}-{a}" if a != s else str(s))
            s = c
    return ", ".join(out)


# ---------------------------------------------------------------- Surf barriers (user, 2026-10-13)
# "Every Surf-reachable cell is a viewpoint": where open water meets an unconnected edge the player must stop 1-3 cells short of it
# at scenery, never at the map's end.  The sealed zone S (water rows 0..L-1 along the edge, L wandering 1..3) is walled off by a
# chain of blocking props along S's 4-neighbour boundary B (diagonal steps seal for 4-direction movement), so the last water the
# surfer can reach lies behind cypress / logs / snags / pilings.  Props come from a per-tileset palette (swamp or sea).
BARRIER_CLASSES = {
    # class -> ((prefab, weight), ...): "big" pieces make a grove / cluster, "low" pieces close the gaps between clusters, "accent" is rare
    "swamp": {"big": (("cypress_water", 3), ("cypress_small_water", 3)),
              "low": (("wp_knees_a", 3), ("wp_knees_b", 3), ("wp_cattails", 3), ("waterlog", 2), ("snag_water", 2)),
              "accent": (("snag_water", 1),)},
    "sea": {"big": (("wp_rock_ledge", 3), ("wp_rock_a", 2)),
            "low": (("wp_rock_a", 4), ("wp_rock_b", 4), ("snag_water", 1), ("waterlog", 1)),
            "accent": (("sunken_piling", 2), ("channel_buoy", 1), ("cypress_small_water", 1))},
    # the port tileset (Storm's Edge + Route 2) is at its tile limit: only pieces its maps already pay for
    "port": {"big": (("cypress_small_water", 4), ("cypress_water", 3)),
             "low": (("snag_water", 3), ("wp_knees_a", 2), ("wp_cattails", 2)),
             "accent": ()},
}
SEA_TILESETS = ("gulf", "offshore", "harbor", "coast", "crescent")


def barrier_classes(b):
    name = b.spec["tileset"]
    kind = "port" if name.endswith("_port") else "sea" if any(s in name for s in SEA_TILESETS) else "swamp"
    have = b.ts["prefabs"]
    out = {c: [(p, w_) for p, w_ in lst if p in have] for c, lst in BARRIER_CLASSES[kind].items()}
    if not out["big"]:
        out["big"] = [(p, 1) for p in ("cypress_water", "cypress_small_water") if p in have]
    if not out["low"]:
        out["low"] = [(p, 1) for p in ("waterlog", "snag_water") if p in have]
    return kind, out


def prefab_shape(b, name):
    p = b.ts["prefabs"][name]
    rows = p["rows"]
    passable = {tuple(c) for c in p.get("passable", [])}
    cells = {(i, j) for j, row in enumerate(rows) for i, c in enumerate(row) if c is not None}
    return cells, cells - passable


def blocking_cells(b):
    """(blocked, structure cells): cells a surfer / walker cannot enter because of props; cells of structures (decks) kept apart"""
    br = __import__("band_rules")
    blocked, struct = set(), set()
    for bd in b.spec.get("buildings", []):
        cells = {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
        pr = b.ts["prefabs"][bd["prefab"]]
        pas = {(bd["x"] + c[0], bd["y"] + c[1]) for c in (bd.get("passable") or pr.get("passable") or [])}
        if br.is_structure(b, bd):
            struct |= cells
        else:
            blocked |= cells - pas
    return blocked, struct


def prepare_barrier(b, key, sp, P, forbid, strict_all, maxl=4, events=()):
    """Stop the surfer 1-4 cells short of every unconnected edge with scenery that reads as the place, not as a fence:
    segments of the edge alternate between CLUSTERS (groves of big props, a thick sealed zone behind them filled with undergrowth) and GAPS
    (low pieces: knees, cattails, rocks, snags), the line wanders 1-4 cells from the edge, no prop is repeated more than 3 times in a row.
    Movement is 4-way, so a chain of blocking cells that only touches diagonally still seals.  Returns the number of unsealed boundary cells."""
    w, h = b.w, b.h
    br = __import__("band_rules")
    rng = _rng(key, "barrier")
    water = {(x, y) for y in range(h) for x in range(w) if b.grid[y][x] in WATERCH}
    blocked, struct = blocking_cells(b)
    occupied = set(P) | struct
    for bd in b.spec.get("buildings", []):
        occupied |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    kind, cls = barrier_classes(b)
    allp = {p for lst in cls.values() for p, _ in lst}
    if not allp:
        b.feather_report.append("no barrier props in this tileset")
        return 0
    shapes = {p: prefab_shape(b, p) for p in allp}
    S, owner, mode = set(), {}, {}
    for side in "NSWE":
        n, cell = side_geom(b, side)
        for lo, hi in sp[side]:
            r2 = _rng(key, side, lo, "surf2")
            dl = []
            for i in range(lo, hi):
                k = 0
                while k < 9 and cell(i, k) in water:
                    k += 1
                dl.append(k)                 # water rows from the edge (a non-water cell stops the run)
            segs, i, is_cl = [], lo, r2.random() < 0.5
            while i < hi:
                ln = r2.randint(4, 8) if is_cl else r2.randint(2, 5)
                segs.append((i, min(hi, i + ln), is_cl))
                i += ln
                is_cl = not is_cl
            want = []
            for a, e, cl in segs:
                base = r2.choice((3, 4) if cl else (1, 2)) if kind != "sea" else r2.choice((2, 3, 4) if cl else (1, 2))
                for i in range(a, e):
                    mode[(side, i)] = "big" if cl else "low"
                    want.append(max(1, min(maxl, base + (r2.choice((-1, 1)) if r2.random() < 0.3 else 0))))
            cap = [min(maxl, d - 2) if d >= 3 else 0 for d in dl]
            L = relax(want, cap)
            for i in range(lo, hi):
                for k in range(L[i - lo]):
                    S.add(cell(i, k))
                    owner.setdefault(cell(i, k), (side, i))

    S -= dilate(events or P, 2, w, h)        # an event / NPC / item in the water is never sealed in: the barrier keeps two cells away from it

    def nbrs(c):
        x, y = c
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    def usable(c):
        return c in water and c not in occupied and c not in forbid

    s0 = len(S)
    for _ in range(80):                       # S must be sealable: every outside neighbour is blocked already or can take a prop
        bad = set()
        for c in S:
            for nb in nbrs(c):
                if not (0 <= nb[0] < w and 0 <= nb[1] < h) or nb in S or nb in blocked:
                    continue
                if not usable(nb):
                    bad.add(c)
        if not bad:
            break
        S -= bad
    b.border_log.append(f"feather surf zone: {s0} cells wanted, {len(S)} sealable")

    def fits(p, ax, ay, S, newocc, newblocked, inside_only=False):
        """the prop's footprint stands on free water (and on the patch window the prop's rule wants); its passable cells never touch the sealed zone from outside"""
        cells, blk = shapes[p]
        foot = {(ax + i, ay + j) for i, j in cells}
        if any(not usable(f) or f in newocc for f in foot):
            return None
        if inside_only and any(f not in S for f in foot):
            return None
        win = {(f[0] + dx, f[1] + dy) for f in foot for dx in (0, 1) for dy in (0, 1)}
        if any(q not in water and 0 <= q[0] < w and 0 <= q[1] < h for q in win):
            return None
        if any(f in strict_all for f in foot) and not br.prefab_is_primary(b, {"prefab": p, "x": ax, "y": ay}):
            return None
        pas = {(ax + i, ay + j) for i, j in cells - blk}
        if any(q not in S and q not in newblocked and any(nb in S and nb not in foot for nb in nbrs(q)) for q in pas):
            return None
        return foot, {(ax + i, ay + j) for i, j in blk}

    def pick(order, weights_by_class):
        flat = []
        for ci, c in enumerate(order):
            for p, w_ in weights_by_class.get(c, ()):
                flat.append((p, w_, ci))
        return flat

    def solve(S):
        B = {nb for c in S for nb in nbrs(c) if 0 <= nb[0] < w and 0 <= nb[1] < h and nb not in S and nb not in blocked}

        def okey(c):
            ow = next((owner[q] for q in nbrs(c) if q in owner), ("Z", 0))
            return (ow[0], ow[1], c[0] + c[1])
        placed, newblocked, newocc, leaks = [], set(), set(), set()
        recent = {}
        rest = set(B)
        while rest:
            c = min(rest, key=okey)
            ow = next((owner[q] for q in nbrs(c) if q in owner), ("Z", 0))
            want = mode.get(ow, "low")
            order = ("big", "low", "accent") if want == "big" else ("low", "big", "accent")
            last = recent.setdefault(ow[0], [])
            best, bestscore = None, -1e9
            for strictseq in (True, False):                         # the "no more than 3 of one prop in a row" rule gives way only when nothing else fits
              for p, wgt, ci in pick(order, cls):
                if ci == 2 and rng.random() > 0.10:
                    continue                                       # accents are rare
                if strictseq and len(last) >= 3 and last[-1] == last[-2] == last[-3] == p:
                    continue
                cells, blk = shapes[p]
                for (bx, by) in blk:
                    ax, ay = c[0] - bx, c[1] - by
                    r = fits(p, ax, ay, S, newocc, newblocked)
                    if r is None:
                        continue
                    foot, blkc = r
                    cover = blkc & rest
                    score = 1.2 * len(cover) + (3 if ci == 0 else 0) + wgt * 0.3 + rng.random() * 4.0
                    if score > bestscore:
                        best, bestscore = (p, ax, ay, foot, blkc), score
              if best is not None:
                break
            if best is None:
                leaks.add(c)
                rest.discard(c)
                continue
            p, ax, ay, foot, blkc = best
            placed.append({"prefab": p, "x": ax, "y": ay, "label": "Surf barrier"})
            last.append(p)
            newocc |= foot
            newblocked |= blkc
            rest -= blkc
        return placed, leaks, newocc, newblocked

    result = None
    for rnd in range(40):                     # a boundary cell no prop can take: other draws first, then pull the sealed zone back from it
        best = None
        for seed in range(14):
            rng = _rng(key, "barrier", rnd, seed)
            r = solve(S)
            if best is None or len(r[1]) < len(best[1]):
                best = r
            if not r[1]:
                break
        result = best
        if not best[1]:
            break
        rad = 1 + rnd // 3
        S = {c for c in S if not any(abs(c[0] - q[0]) <= rad and abs(c[1] - q[1]) <= rad for q in best[1])}
    placed, leaks, newocc, newblocked = result
    # undergrowth: the sealed zone behind a cluster is not bare water, and a few single low pieces drift in front of the line
    rng = _rng(key, "undergrowth")
    extras = []
    lows = [p for p, _ in cls["low"] if len(shapes[p][0]) == 1] or [p for p, _ in cls["low"]]
    bigs = cls["big"]
    cs = sorted(S)
    rng.shuffle(cs)
    for c in cs:
        ow = owner.get(c)
        if ow is None or c in newocc or c in newblocked:
            continue
        cl = mode.get(ow) == "big"
        r0 = rng.random()
        if cl and bigs and r0 < 0.10:
            p = rng.choices([q for q, _ in bigs], [w_ for _, w_ in bigs])[0]
        elif r0 < ((0.16 if kind == "sea" else 0.34) if cl else 0.06) and lows:
            p = rng.choice(lows)
        else:
            continue
        r = fits(p, c[0], c[1], S, newocc, newblocked, inside_only=True)
        if r is None:
            continue
        foot, blkc = r
        extras.append({"prefab": p, "x": c[0], "y": c[1], "label": "Surf barrier"})
        newocc |= foot
        newblocked |= blkc
    edge_d = lambda q: min(q[0], q[1], w - 1 - q[0], h - 1 - q[1])
    for c in sorted(water):
        if edge_d(c) < 4 or edge_d(c) > 8 or c in S or c in newocc or rng.random() > 0.022:
            continue
        p = rng.choice(lows) if lows else None
        if p is None:
            continue
        # only on open water well clear of the sealed zone and of every placed prop
        if any((c[0] + i, c[1] + j) in S or (c[0] + i, c[1] + j) in newocc for i in range(-2, 3) for j in range(-2, 3)):
            continue
        r = fits(p, c[0], c[1], S, newocc, newblocked)
        if r is None:
            continue
        foot, blkc = r
        extras.append({"prefab": p, "x": c[0], "y": c[1], "label": "Surf barrier"})
        newocc |= foot
        newblocked |= blkc
    placed = placed + extras
    for pl in placed:
        cells, _ = shapes[pl["prefab"]]
        for f in {(pl["x"] + i, pl["y"] + j) for i, j in cells}:       # plain deep water ('w') under a prop becomes the decorated water its patch rule wants
            for dx in (0, 1):
                for dy in (0, 1):
                    q = (f[0] + dx, f[1] + dy)
                    if q[0] < w and q[1] < h and b.grid[q[1]][q[0]] in "wI":
                        b.grid[q[1]][q[0]] = "~"
    b.spec["buildings"] = b.spec.get("buildings", []) + placed
    if placed:
        by = {}
        for bd in placed:
            by[bd["prefab"]] = by.get(bd["prefab"], 0) + 1
        b.border_log.append("feather surf barrier: " + ", ".join(f"{k} x{v}" for k, v in sorted(by.items())))
    if leaks:
        b.feather_report.append(f"surf barrier: {len(leaks)} boundary cells could not take a prop (leaks): {sorted(leaks)[:8]}")
    return len(leaks)


def surf_exposure(b, key, sp):
    """{side: [positions]}: unconnected-edge positions where a surfer can stand with open water between him and the border.
    A cell is surf-open when it is water and no prop / wall / edge cell blocks it; a sealed pocket along the edge does not count."""
    w, h = b.w, b.h
    water = {(x, y) for y in range(h) for x in range(w) if b.grid[y][x] in WATERCH}
    blocked, _ = blocking_cells(b)
    blocked |= set(getattr(b, "wall", ())) | set(getattr(b, "edge", {}))
    free = water - blocked
    seen, comps = set(), []
    for c in sorted(free):
        if c in seen:
            continue
        comp, todo = [], [c]
        seen.add(c)
        while todo:
            q = todo.pop()
            comp.append(q)
            for nb in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)):
                if nb in free and nb not in seen:
                    seen.add(nb)
                    todo.append(nb)
        comps.append(comp)
    seam = seam_zone(key, 1)
    # a component is open water the player can reach when it runs into the map's interior (4+ cells from every edge) or into a
    # connection; a pocket sealed off along the edge does neither
    reach = {c for comp in comps if any(min(x, y, w - 1 - x, h - 1 - y) >= 4 or (x, y) in seam for x, y in comp) for c in comp}
    near_join = dilate(seam_zone(key, 3), 4, w, h)        # a corner beside a connection belongs to the join (the seam bands), not to this pass
    out = {}
    for side in "NSWE":
        n, cell = side_geom(b, side)
        for lo, hi in sp[side]:
            for i in range(lo, hi):
                for k in range(8):
                    c = cell(i, k)
                    if c in blocked or c not in water:
                        break
                    if c in reach:
                        if c not in near_join and cell(i, 0) not in near_join:
                            out.setdefault(side, []).append(i)
                        break
    return out


# ---------------------------------------------------------------- regrowing the decor the wall / the water took
def regrow(b, dropped, zone, P, radius=12, forbid=()):
    """Put every dropped decor prop (cypress groves, reeds, snags, logs) back as near its old place as the new outline allows: the same ground
    under its footprint (marsh window for patch props), clear of the wall by a cell, of events and of other props. Returns (moved, lost)."""
    br = __import__("band_rules")
    w, h = b.w, b.h
    occ = set(P)
    for bd in b.spec.get("buildings", []):
        occ |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    near_zone = dilate(zone, 1, w, h) | set(forbid)
    moved, lost = [], []
    ring = sorted(((dx, dy) for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)),
                  key=lambda d: (d[0] * d[0] + d[1] * d[1], abs(d[0]) + abs(d[1])))
    for bd in sorted(dropped, key=lambda d: (d["y"], d["x"])):
        p = b.ts["prefabs"][bd["prefab"]]
        rows = bd.get("rows") or p["rows"]
        cells = [(i, j) for j, row in enumerate(rows) for i, c in enumerate(row) if c is not None]
        base = p.get("on_patch")
        sig = {(i, j): b.grid[bd["y"] + j][bd["x"] + i] for i, j in cells if 0 <= bd["x"] + i < w and 0 <= bd["y"] + j < h}
        tree = bd["prefab"].startswith("cypress")
        found = None
        for dx, dy in ring:
            x, y = bd["x"] + dx, bd["y"] + dy
            foot = [(x + i, y + j) for i, j in cells]
            if any(not (0 <= f[0] < w and 0 <= f[1] < h) for f in foot):
                continue
            if any(f in near_zone or f in occ for f in foot):
                continue
            if any(b.grid[f[1]][f[0]] in ROAD for f in foot):
                continue
            if base:
                if any(b.grid[min(f[1] + b_, h - 1)][min(f[0] + a_, w - 1)] not in base for f in foot for a_ in (0, 1) for b_ in (0, 1)):
                    continue
            elif any(sig.get((i, j)) != b.grid[y + j][x + i] for i, j in cells):
                continue
            found = (x, y, foot)
            break
        if found is None and base == '"' and tree:
            found = new_grove(b, bd, cells, occ, near_zone, P, ring, zone)
        if found is None:
            lost.append(bd)
            continue
        x, y, foot = found
        moved.append(dict(bd, x=x, y=y))
        occ |= set(foot)
        if tree:                      # trees keep a cell apart
            occ |= dilate(set(foot), 1, w, h)
    if moved:
        b.spec["buildings"] = b.spec.get("buildings", []) + moved
    return moved, lost


def new_grove(b, bd, cells, occ, near_zone, P, ring, zone=()):
    """a lost marsh grove is grown again where there is room: a small round marsh patch on open grass (a grass cell all round it), the tree in
    its middle; returns (x, y, foot) or None"""
    w, h = b.w, b.h
    tw = max(i for i, _ in cells) + 1
    th = max(j for _, j in cells) + 1
    for dx, dy in ring:
        x, y = bd["x"] + dx, bd["y"] + dy
        x0, y0, x1, y1 = x - 1, y - 1, x + tw + 1, y + th + 1          # the patch (tree + a marsh cell all round it: the window rule)
        if x0 - 1 < 0 or y0 - 1 < 0 or x1 + 1 >= w or y1 + 1 >= h:
            continue
        ok = True
        for cy in range(y0 - 1, y1 + 2):                                   # patch + a grass cell all round: nothing but plain grass or marsh
            for cx in range(x0 - 1, x1 + 2):
                c = (cx, cy)
                inner = x0 <= cx <= x1 and y0 <= cy <= y1
                ch = b.grid[cy][cx]
                tree = x <= cx < x + tw and y <= cy < y + th
                if c in occ or c in P or c in zone or (tree and c in near_zone) or ch not in '."':      # grass or marsh only (a new patch may join an old marsh margin and touch the edge cells)
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        for cy in range(y0, y1 + 1):                                       # a rounded patch: the four corner cells stay grass
            for cx in range(x0, x1 + 1):
                if (cx in (x0, x1)) and (cy in (y0, y1)):
                    continue
                b.grid[cy][cx] = '"'
        foot = [(x + i, y + j) for i, j in cells]
        return x, y, foot
    return None

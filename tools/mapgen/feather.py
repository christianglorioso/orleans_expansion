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
MAXB = 2                      # canopy depth in 2x2 blocks (0..MAXB): 1..5 cells including the overhang cell
ROAD = set(":=p%&B")          # grid characters of paths / paving / levee ground: never covered
LAND = set(".\"dGgLSeqQwysrvp:=%&")
WATERCH = set("~Iw")
FACE_DIR = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


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


def protected(b, key):
    """cells that must stay exactly as they are: events, doors, exits, structures, paths, trainer sight lines"""
    P = set()
    spec = b.spec
    for coll in ("objects", "items", "signs", "hidden_items", "triggers"):
        P |= {(o["x"], o["y"]) for o in spec.get(coll, []) if not o.get("gate")}
    for ex in spec.get("exits", []):
        P |= {tuple(c) for c in ex["cells"]}
    for bd in spec.get("buildings", []):
        p = b.ts["prefabs"][bd["prefab"]]
        door = p.get("door")
        for dx, dy in ([] if not door else door if isinstance(door[0], list) else [door]):
            P |= {(bd["x"] + dx, bd["y"] + dy), (bd["x"] + dx, bd["y"] + dy + 1)}
    br = __import__("band_rules")
    for bd in spec.get("buildings", []):
        if br.is_structure(b, bd):
            P |= {(x, y) for x, y, _ in br.prefab_cells(b, bd)}
    for cells in spec.get("states", {}).values():
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
                P.add((o["x"], o["y"]))
    for y in range(b.h):
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
    wall = set()
    for (side, lo, hi), vals in prof.items():
        n, cell = side_geom(b, side)
        for j, m in enumerate(vals):
            for i in (2 * j, 2 * j + 1):
                if i < n and lo <= i < hi:
                    for k in range(2 * m):
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
        return {'"': '"', ".": ".", "~": "~", "I": "~", "w": "~", "G": ".", "L": ".", "d": ".", "g": "."}.get(ch)
    return {"d": "d", "G": "d", "g": "d", "q": "d", "Q": "d", "e": "d", "y": "d", "s": "d", "r": "d", "v": "d", ".": "d", "L": "d", "w": "d"}.get(ch)


def prepare(b, key, style, sp, keep_open, strict_all):
    """canopy styles: choose the wall, set b.wall / b.edge / b.border_depth and bend b.grid under them.  water: recede the land."""
    b.feather_missing, b.feather_report = [], []
    if (b.w % 2) or (b.h % 2):
        b.feather_report.append("odd map size: feather pass skipped")
        return None
    if style == "water":
        return prepare_water(b, key, sp, keep_open)
    return prepare_canopy(b, key, style, sp, keep_open, strict_all)


def prepare_canopy(b, key, style, sp, keep_open, strict_all, maxb=MAXB):
    w, h = b.w, b.h
    P = protected(b, key) | keep_open | landmarks(b)
    PD = dilate(P, 1, w, h)
    forbid = seam_zone(key, 3)
    if style == "dry":
        forbid |= strict_all
    prof, caps = {}, {}
    for side in "NSWE":
        n, cell = side_geom(b, side)
        nb = n // 2
        for lo, hi in sp[side]:
            vals = walk(_rng(key, side, lo, "canopy"), nb, 0, maxb, (1, 2))
            inside = [lo <= 2 * j and 2 * j + 1 < hi for j in range(nb)]
            cap = [maxb if inside[j] else 0 for j in range(nb)]
            for j in range(nb):          # a block beside a connected stretch stays plain: the wall tapers into the border
                for jj in (j - 1, j + 1):
                    if 0 <= jj < nb and not inside[jj]:
                        cap[j] = 0
            prof[(side, lo, hi)] = relax(vals, cap)
            caps[(side, lo, hi)] = cap
    sets = "qQGgwsvr" if style == "dry" else "GgL"
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
                c += 10          # a terrain boundary under the overhang: the edge cell would not be a plain ground cell
        cover = wall | set(edge)
        for comp in comps:
            n_in = len(comp & cover)
            if 0 < n_in < len(comp):
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
                    if m and any(cell(i, k) in badw for i in (2 * j, 2 * j + 1) if i < n for k in range(2 * m + 1)):
                        vals[j] = m - 1
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
        if 0 < n_in < len(comp):
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
    b.feather_bake = True        # an edge cell on a ground the art has no piece for (a bank, a blend) is baked: the overhang over that cell's pixels
    b.wall, b.edge = wall, edge
    b.border_depth = {s_: max((max(v) * 2 for (sd, lo, hi), v in prof.items() if sd == s_), default=0) for s_ in "NSWE"}
    b.feather_prof = prof
    b.feather_missing = missing_corners(b, wall, edge)
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
    cuts = []
    for side in "NSWE":
        n, cell = side_geom(b, side)
        for lo, hi in sp[side]:
            want = walk(_rng(key, side, lo, "shore"), hi - lo, 2, 5, (2, 3, 4))
            cap = []
            for i in range(lo, hi):
                lim = 6
                for k in range(6):
                    c = cell(i, k)
                    if c in PD or c in seam or b.grid[c[1]][c[0]] in "B#":
                        lim = k
                        break
                cap.append(lim)
            d = relax(want, cap)
            for i in range(lo, hi):
                if cap[i - lo] < 2:
                    if any(b.grid[cell(i, k)[1]][cell(i, k)[0]] not in WATERCH for k in range(2)):
                        cuts.append((side, i))
                for k in range(d[i - lo]):
                    x, y = cell(i, k)
                    if b.grid[y][x] in LAND and b.grid[y][x] not in ROAD:
                        b.grid[y][x] = "~"
                        carved += 1
    water = {(x, y) for y in range(h) for x in range(w) if b.grid[y][x] == "~"}
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
    groups = {}
    for side, i in cuts:
        groups.setdefault(side, []).append(i)
    for side, v in groups.items():
        b.feather_report.append(f"{side} edge: land within 2 cells of the edge at positions {_ranges(v)} cannot recede (building / path / event / seam)")
    b.border_log.append(f"feather water: {carved} land cells became water")
    b.wall, b.edge = set(), {}
    return True


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

"""City approaches: where a route leaves Crescent City or Pointe Rouge, the city's road carries on into the route
and turns into the route's dirt road gradually, so leaving a city doesn't feel like stepping off a kerb onto a
cart track.

On the route side, from the edge it shares with the city:
  * the city's flagstone paving ('%', Johto flagstone autotile, primary 1B8-1CA: no secondary tiles) carries on
    for a few cells at the width of the city's exit (the route's road is widened or trimmed at the edge to
    match it; its first exit cell stays where it was, so the maps still line up);
  * then three cells of paving breaking up ('&'): drawn as dirt road, with the paving laid over it as an overlay
    whose slabs drop out the further they are from the paving (draw(), called by build.py, requests each
    distinct cell from compose as a "pixels" patch over the dirt tile, like the levee);
  * then the route's ordinary dirt road. Side roads meeting the paved stretch break up the same way.
  * a pair of lamps at the city limit, a signpost where the paving gives out, a bench, and a pair of magnolias
    (the towns' street tree) close to the city, then a single one, then the route's own wild trees.
Where the stretch runs into a bridge, the paving goes right up to it and the dirt starts on the far side.

lay() runs in firstpass.first_pass() near the end (after the greenery, before prune_thin), so everything else
in the first pass treats the stretch as ordinary road; draw() runs in build.py after the terrain.
"""
import hashlib
import math
import os
import random

# route -> (edge shared with the city, width of the city's road at its exit, city name for the sign)
ROUTES = {
    "route_3": ("E", 2, "CRESCENT CITY"),
    "route_14": ("N", 2, "CRESCENT CITY"),
    "route_5": ("E", 3, "POINTE ROUGE"),
    "route_23": ("W", 2, "POINTE ROUGE"),
    "route_4": ("N", 4, "POINTE ROUGE"),
}
PAVED, BREAK = "%", "&"
ROAD = ":=p"      # p: a road on the dry-country routes' green meadow (firstpass.dry_finish), after lay() has run
OPEN = '.G'         # ground a road, verge or prop may take (tall grass gives way to plain grass)
PAVED_MAX, BREAK_LEN = 3, 3


def lay(key, grid, occ, prefabs, dock=frozenset()):
    """Returns (grid, buildings, signs) for a route that meets a city; the grid unchanged otherwise.
    occ: cells taken by prefabs (updated with the new props); dock: bridge/dock cells (the stretch stops there)."""
    if key not in ROUTES:
        return grid, [], []
    side, width, city = ROUTES[key]
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    n_along = w if side in "NS" else h
    rng = random.Random(key + "approach")

    def xy(a, d):  # along-edge coordinate a, depth d from the city edge
        return {"N": (a, d), "S": (a, h - 1 - d), "W": (d, a), "E": (w - 1 - d, a)}[side]

    def at(a, d):
        x, y = xy(a, d)
        return g[y][x] if 0 <= x < w and 0 <= y < h else None

    def put(a, d, ch):
        x, y = xy(a, d)
        g[y][x] = ch

    runs, a = [], 0
    while a < n_along:
        if at(a, 0) in ROAD:
            b = a
            while b + 1 < n_along and at(b + 1, 0) in ROAD:
                b += 1
            runs.append((a, b))
            a = b + 1
        else:
            a += 1
    if not runs:
        return grid, [], []
    out, signs = [], []

    def one(r0, r1, n):
        """The approach for the road reaching the city edge at along r0..r1 (n: which one, for sign ids)."""

        def cell_ok(a, d):
            c = at(a, d)
            return c is not None and (c in ROAD or c in OPEN) and xy(a, d) not in occ

        def verge_ok(a, d):  # levee ground ('B') is grass to walk on: a fine verge
            c = at(a, d)
            return c is None or ((c in ROAD or c in OPEN or c == "B") and xy(a, d) not in dock)

        def reach(lo, hi):
            """How deep a band [lo, hi] can be paved, and whether a bridge or dock stopped it."""
            for d in range(PAVED_MAX + BREAK_LEN):
                if any(xy(a, d) in dock for a in range(lo, hi + 1)):
                    return d, True
                if not all(cell_ok(a, d) for a in range(lo, hi + 1)) or not verge_ok(lo - 1, d) or not verge_ok(hi + 1, d):
                    return d, False
            return PAVED_MAX + BREAK_LEN, False
        # the band keeps the route's first exit cell where it is if it can (the maps line up on it); a band that can't
        # grow that way grows the other way (then its first cell is the new one, and the city's lines up with that)
        options = [(r0, r0 + width - 1)]
        if r1 - r0 + 1 < width:
            options.append((r1 - width + 1, r1))
        best = max(options, key=lambda o: (reach(*o)[0], o == options[0]))
        lo, hi = best
        depth, bridged = reach(lo, hi)
        if depth < 2:
            return
        paved = depth if bridged else max(1, depth - BREAK_LEN)
        band = {(a, d) for a in range(lo, hi + 1) for d in range(depth)}
        for a, d in band:
            put(a, d, PAVED if d < paved else BREAK)
        # the old road beside the band near the edge goes back to grass (the exit is exactly the city's width);
        # road meeting the stretch from the side breaks up into it
        for a in range(n_along):
            for d in range(depth + 1):
                if (a, d) in band or at(a, d) not in ROAD:
                    continue
                if d < 2 and not lo <= a <= hi and lo - 3 <= a <= hi + 3:
                    put(a, d, ".")
        for _ in range(2):
            for a in range(n_along):
                for d in range(depth + 3):
                    if at(a, d) in ROAD and any(at(a + i, d + j) == PAVED for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        put(a, d, BREAK)
        # a one-tile plain-grass verge beside the stretch
        for a in (lo - 1, hi + 1):
            for d in range(depth + 1):
                if at(a, d) == "G":
                    put(a, d, ".")

        def free(cells):
            return all(at(a, d) is not None and at(a, d) in OPEN and xy(a, d) not in occ for a, d in cells)

        def place(prefab, cells, label):
            """cells: (along, depth) pairs the prefab covers; its top-left in map coordinates is their minimum."""
            pts = [xy(a, d) for a, d in cells]
            for x, y in pts:
                g[y][x] = "."
                occ.add((x, y))
            x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
            out.append({"prefab": prefab, "x": x0, "y": y0, "label": label})
            return x0, y0

        def footprint(prefab, a0, d0, toward):
            """The (along, depth) cells of a prefab whose map-space box starts nearest the band edge at along a0
            (toward = -1: the prefab lies on the low side of the band, its far edge at a0) and depth d0."""
            rows = prefabs[prefab]["rows"]
            pw, ph = len(rows[0]), len(rows)
            span_along, span_depth = (pw, ph) if side in "NS" else (ph, pw)
            alongs = range(a0 - span_along + 1, a0 + 1) if toward < 0 else range(a0, a0 + span_along)
            return [(a, d) for a in alongs for d in range(d0, d0 + span_depth)]

        # lamps at the city limit, one each side of the road
        if "lamp" in prefabs:
            for toward, edge in ((-1, lo - 1), (1, hi + 1)):
                for d0 in (0, 1):
                    cells = footprint("lamp", edge, d0, toward)
                    if free(cells):
                        place("lamp", cells, "Lamp")
                        break
        # magnolias: a pair close to the city (an avenue), then one, then the route's own wild trees
        if "magnolia" in prefabs:
            for d0, sides_ in ((2, (-1, 1)), (paved + BREAK_LEN + 3, (rng.choice((-1, 1)),))):
                for toward in sides_:
                    edge = lo - 2 if toward < 0 else hi + 2
                    for dd in (0, 1, -1):
                        cells = footprint("magnolia", edge, d0 + dd, toward)
                        ring = {(a + i, d + j) for a, d in cells for i in (-1, 0, 1) for j in (-1, 0, 1)} - set(cells)
                        if d0 + dd >= 0 and free(cells) and all(at(a, d) is None or (at(a, d) in OPEN + ROAD + PAVED + BREAK
                                                                                and xy(a, d) not in occ) for a, d in ring):
                            place("magnolia", cells, "Tree")
                            for a, d in ring:  # plain grass round the tree
                                if at(a, d) == "G":
                                    put(a, d, ".")
                            break
        # a signpost where the paving gives out, and a bench across the road from it
        sign_side = rng.choice((-1, 1))
        if "sign" in prefabs:
            for d0 in (depth, depth - 1, depth + 1):
                edge = lo - 1 if sign_side < 0 else hi + 1
                cells = [(edge, d0)]
                if d0 > 0 and free(cells):
                    x, y = place("sign", cells, "Sign")
                    signs.append({"id": "SignCity" + (str(n + 1) if n else ""), "x": x, "y": y, "text": f"{city}\nCity limits: welcome!"})
                    break
        if "bench" in prefabs:
            for d0 in (paved, paved + 1, 1):
                edge = hi + 1 if sign_side < 0 else lo - 1
                toward = 1 if sign_side < 0 else -1
                cells = footprint("bench", edge, d0, toward)
                if free(cells):
                    place("bench", cells, "Bench")
                    break

    for n, (r0, r1) in enumerate(sorted(runs)):  # every road reaching the city edge gets its own approach
        one(r0, r1, n)
    return ["".join(r) for r in g], out, signs


# ---------------------------------------------------------------- drawing the break-up (build.py)
def draw(b):
    """Lays the city paving over the dirt of every break-up cell ('&'), its stones dropping out towards the dirt.
    Each distinct cell is requested from compose as a "pixels" overlay on the dirt tile under it.

    How a cell is drawn, all in map space (so stones that straddle two cells come out the same in both):
      * the paving tile the cell would have if the paving ran on into the dirt (kerbs only along its sides);
      * it breaks up in staggered 8x4 setts, each kept or dropped as a whole: kept while a hash of its position is
        under the coverage there (1 against the paving, 0 against the dirt road beyond), so most hold near the
        paving and a few strays lie further out. A kept sett keeps its face, mid tone and joint lines; a dropped
        one leaves the joint pixels that outline a neighbouring kept stone;
      * kerb pieces are kept only where they touch surviving paving (no kerb fragments alone on the grass), and
        specks under 12 pixels and lone bits of kerb go;
      * each surviving stone gets a 1-pixel dirt shadow below and to the right, where dirt shows there;
      * every colour is one of the dirt tile's own primary palette (face, mid, joint greys and the shadow
        brown), so a broken cell needs no secondary palette slot of its own."""
    cells = [(x, y) for y in range(b.h) for x in range(b.w) if b.grid[y][x] == BREAK]
    if not cells or "paved" not in b.ts["autotile"]:
        return
    import sys
    from PIL import Image
    build = sys.modules[type(b).__module__]  # the builder's own module: run as a script it is __main__, and a
    # fresh `import build` would be a second copy with an empty MAPPING (every cell then had no name underneath)
    from render import Tilesets
    root = os.getcwd()
    ts = Tilesets(os.path.join(root, b.ts["primary_dir"]), os.path.join(root, b.ts["secondary_dir"]))
    inv = {mid: n for n, mid in build.MAPPING.items()}
    A = dict(b.ts["autotile"]["paved"], connects=b.ts["autotile"]["paved"]["connects"] + ROAD)
    paved = [(x, y) for y in range(b.h) for x in range(b.w) if b.grid[y][x] == PAVED]
    paved_set = set(paved)
    dirt = [(x, y) for y in range(b.h) for x in range(b.w) if b.grid[y][x] in ROAD]
    centre = ts.metatile(build.hx(A["C"])).convert("RGB").load()
    pal = [tuple(c) for c in ts.pals[(ts.pmeta[0x0D9][0] >> 12) & 15]]  # the dirt's own primary palette
    greys = sorted({c for c in pal[1:] if max(c) - min(c) <= 48 and c[2] >= c[0] and sum(c) > 0}, key=sum,
                   reverse=True)
    browns = sorted({c for c in pal[1:] if c[0] > c[2] + 24 and c[1] < 160}, key=sum)
    shadow = browns[0] if browns else (104, 80, 64)
    grass = {c for c in pal if c[1] > c[0] + 24 and c[1] > c[2] + 24}
    nb = lambda w_: ((w_[0] + 1, w_[1]), (w_[0] - 1, w_[1]), (w_[0], w_[1] + 1), (w_[0], w_[1] - 1))

    def dist(px, py, rects):
        best = 1e9
        for cx, cy in rects:
            dx = max(cx * 16 - px, 0, px - (cx * 16 + 15))
            dy = max(cy * 16 - py, 0, py - (cy * 16 + 15))
            best = min(best, math.hypot(dx, dy))
        return best
    decided = {}

    def sett_of(wx, wy):  # 8x4 setts, every other row shifted by 4
        return (wx + 4 * ((wy // 4) % 2)) // 8, wy // 4

    def kept_sett(s):
        if s not in decided:
            sx, sy = s
            wx, wy = sx * 8 + 4 - 4 * (sy % 2), sy * 4 + 2
            cx, cy = wx // 16, wy // 16
            np_ = [c for c in paved if abs(c[0] - cx) <= 4 and abs(c[1] - cy) <= 4]
            nd_ = [c for c in dirt if abs(c[0] - cx) <= 4 and abs(c[1] - cy) <= 4]
            dp, dd = dist(wx, wy, np_), dist(wx, wy, nd_)
            c = 1.0 if not nd_ else 0.0 if not np_ else dd / (dp + dd + 1e-6)
            r = int(hashlib.md5(f"{sx}:{sy}".encode()).hexdigest()[:6], 16) / 0xFFFFFF
            decided[s] = r < c * 1.1 - 0.04
        return decided[s]

    # 1. every break-up pixel in map space: its paving colour, whether it is kerb, the dirt colour under it
    px_art, px_base, kerb, unders = {}, {}, set(), {}
    for x, y in cells:
        under = inv.get(b.blocks[y][x] & 0x3FF)
        if not under:
            continue
        unders[(x, y)] = under
        art = ts.metatile(b.path_tile(x, y, A)).convert("RGB").load()
        base = ts.metatile(b.blocks[y][x] & 0x3FF).convert("RGB").load()
        for j in range(16):
            for i in range(16):
                w_ = (x * 16 + i, y * 16 + j)
                px_art[w_], px_base[w_] = art[i, j], base[i, j]
                if art[i, j] != centre[i, j] and art[i, j] not in grass:
                    kerb.add(w_)
    paving_cols = sorted({c for c in px_art.values() if c not in grass}, key=sum, reverse=True)
    # tones: the two lightest paving colours (face, kerb highlight) -> the palette's light grey, then one step
    # down per darker tone (mid -> the joint grey, joint -> the darker grey), so the herringbone keeps 3 tones
    tones = {c: greys[min(max(0, k - 1), len(greys) - 1)] if greys else c for k, c in enumerate(paving_cols)}
    lum_cut = sum(paving_cols[1]) if len(paving_cols) > 1 else 0
    light = lambda w_: w_ in px_art and px_art[w_] not in grass and sum(px_art[w_]) >= lum_cut
    stone_px = lambda w_: w_ in px_art and px_art[w_] not in grass
    in_paved = lambda w_: (w_[0] // 16, w_[1] // 16) in paved_set
    # 2. kept: the pixels of kept setts, and the joint pixels outlining a kept stone next door
    keep = set()
    for w_ in px_art:
        if not stone_px(w_):
            continue
        if kept_sett(sett_of(*w_)):
            keep.add(w_)
        elif not light(w_) and any(light(q) and kept_sett(sett_of(*q)) for q in nb(w_)):
            keep.add(w_)
    # 3. kerb only where it touches surviving paving (through kept kerb), and no specks
    reach = {w_ for w_ in keep if w_ not in kerb}
    todo = [w_ for w_ in keep if w_ in kerb and (any(in_paved(q) for q in nb(w_)) or any(q in reach for q in nb(w_)))]
    reach.update(todo)
    while todo:
        w_ = todo.pop()
        for q in nb(w_):
            if q in keep and q in kerb and q not in reach:
                reach.add(q)
                todo.append(q)
    keep = {w_ for w_ in keep if w_ not in kerb or w_ in reach}
    # a joint or outline pixel only stays beside a stone face that stays (no thin lines left on the grass)
    for _ in range(2):
        keep = {w_ for w_ in keep if light(w_) or any(
            (w_[0] + i, w_[1] + j) in keep and light((w_[0] + i, w_[1] + j)) for i in (-1, 0, 1) for j in (-1, 0, 1))}
    seen = set()
    for w_ in list(keep):
        if w_ in seen:
            continue
        comp, todo, touches = {w_}, [w_], False
        while todo:
            p = todo.pop()
            for q in nb(p):
                if in_paved(q):
                    touches = True
                if q in keep and q not in comp:
                    comp.add(q)
                    todo.append(q)
        seen |= comp
        if not touches and (len(comp) < 12 or comp <= kerb):  # specks, and kerb with no paving left by it
            keep -= comp
    # 4. the overlays
    out_dir = os.path.join(os.path.dirname(os.path.abspath(build.__file__)), "tilesets", "approach")
    os.makedirs(out_dir, exist_ok=True)
    b.approach_art = {}  # (x, y) -> the overlay image (for previews made before compose has the pieces)
    for (x, y), under in unders.items():
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        ip = im.load()
        for j in range(16):
            for i in range(16):
                w_ = (x * 16 + i, y * 16 + j)
                if w_ in keep:
                    ip[i, j] = tones[px_art[w_]] + (255,)
                elif px_base[w_] not in grass and ((w_[0] - 1, w_[1]) in keep or (w_[0], w_[1] - 1) in keep):
                    ip[i, j] = shadow + (255,)  # the stone sits in the ground
        b.approach_art[(x, y)] = im
        lid = "ap_" + hashlib.sha1(im.tobytes() + under.encode()).hexdigest()[:12]
        if f"patch:{lid}" in build.MAPPING:
            b.blocks[y][x] = (b.blocks[y][x] & ~0x3FF) | build.MAPPING[f"patch:{lid}"]
            build.USED.add(f"patch:{lid}")
            continue
        path = os.path.join(out_dir, lid + ".png")
        if not os.path.exists(path):
            im.save(path)
        b.pending_blends[lid] = {"id": lid, "pixels": os.path.relpath(path, root).replace(os.sep, "/"),
                                 "base": under, "attr_of": under}

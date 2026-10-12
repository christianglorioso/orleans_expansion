"""Map borders and inward walls (edges pass, decision 3), applied while a map is built (build.py's Builder).

Past an UNCONNECTED edge the engine draws the layout's 2x2 border block (border.bin), indexed by map coordinates. Every Orleans
map gets one of three borders (STYLE, the user's list in edges_plan.md): the swamp cypress canopy, open water, the dry scrub.
Art: sources/orleans_custom/make_borders.py (approved), cells in borders.png / borders.json (rules there):

    border block    the block's four cells = border.bin ([00, 10, 01, 11]: border[(x & 1) + (y & 1) * 2])
    inward wall     d cells deep along the unconnected stretch of an edge; wall cell (x, y) = the block cell at (x & 1, y & 1)
    edge cells      the first terrain cell beside a wall (or beside the border itself when d = 0): the wall's trees hanging over
                    the terrain, by face (S / N / E / W) and parity (x & 1 for S and N, y & 1 for E and W), and the four inner
                    corners where two walls meet; swamp cells exist on marsh and water, dry cells on dry earth; every other ground
                    is baked with make_borders.bake_edge (swamp on grass: 'bdg_*' patches of the primary, anything else a
                    patch of the map's own tileset)
    parity rule     N / W walls are d cells deep with d even; on the S / E sides the wall's first row (column) h - d (w - d) is
                    even, so d has the parity of h (w). d = 0 is "the border itself is the wall".
    depth           0 where the terrain beside the edge already is what the border is (swamp: marsh or water, dry: dry earth),
                    else 2 (or 3 on an odd S / E side): the terrain is covered by the wall. Water borders: the wall is 2 cells of
                    water laid over the terrain (grid edit), no art.
    passability     walls and edge cells are impassable; an event, a door or an exit on one shortens the wall (never moved).
    seam bands      walls never touch a seam band (the connected stretch of an edge): cells inside one are left alone.

prepare(b) runs before the terrain is drawn (grid edits, props out of the wall, depths); apply(b) after (the blocks).
Everything it did is in b.border_log; b.border_conflicts lists what it could not do.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bands  # noqa: E402

SWAMP = ["isle_marais", "grand_oak", "old_water", "pointe_rouge", "lutins_hollow",
         "route_1", "route_2", "route_3", "route_4", "route_5", "route_6", "route_7", "route_9", "route_12", "route_13",
         "route_14", "route_25"]
WATER = ["storms_edge", "crescent_city", "camp_cocodrie", "lands_end", "oldest_shrine",
         "route_8", "route_10", "route_11", "route_18", "route_19", "route_20", "route_21", "route_22"]
DRY = ["redfield", "route_15", "route_16", "route_17", "route_23", "route_24"]
STYLE = {**{k: "swamp" for k in SWAMP}, **{k: "water" for k in WATER}, **{k: "dry" for k in DRY}}

BLOCK = {"swamp": [f"bd:swamp_canopy_{n}" for n in ("00", "10", "01", "11")],
         "dry": [f"bd:dry_scrub_{n}" for n in ("00", "10", "01", "11")],
         "water": ["ekat:water_C"] * 4}
AGREE = {"swamp": set('"~Iw'), "water": set("~Iw"), "dry": set("d")}
WALKABLE_ON = set(".\"dGgL:=pS")          # grid chars a wall may replace
OPP = {"N": "S", "S": "N", "W": "E", "E": "W"}


def unconnected(key):
    """{side: [(lo, hi)]}: the stretches of each edge no connection covers (positions along the edge)"""
    I = bands.info()
    w, h = I[key]["w"], I[key]["h"]
    length = {"N": w, "S": w, "W": h, "E": h}
    covered = {s: [] for s in "NSWE"}
    for a, sa, b2, sb, loa, hia, lob, hib in bands.joins():
        if a == key:
            covered[sa].append((loa, hia))
        if b2 == key:
            covered[sb].append((lob, hib))
    out = {}
    for s in "NSWE":
        free = [True] * length[s]
        for lo, hi in covered[s]:
            for i in range(lo, hi):
                free[i] = False
        spans, start = [], None
        for i, f in enumerate(free + [False]):
            if f and start is None:
                start = i
            elif not f and start is not None:
                spans.append((start, i))
                start = None
        out[s] = spans
    return out


def cell_at(b, side, i, k):
    """the map cell at position i along `side`, k cells in from the edge"""
    return {"N": (i, k), "S": (i, b.h - 1 - k), "W": (k, i), "E": (b.w - 1 - k, i)}[side]


def min_depth(b, side):
    size = b.h if side in "SN" else b.w
    if side in "NW":
        return 0
    return size % 2           # the S / E wall's first row (column) size - d must be even


def terrain_agrees(b, style, side, spans):
    ok = AGREE[style]
    for lo, hi in spans:
        for i in range(lo, hi):
            for k in range(2):
                x, y = cell_at(b, side, i, k)
                if b.grid[y][x] not in ok:
                    return False
    return True


ENABLED = False   # decision 3 is switched on once the walls leave the maps' seams and gates alone (see edges_progress.log.md)


def prepare(b, key):
    b.border_style = STYLE.get(key) if ENABLED else ("swamp" if b.spec.get("walls") else None)
    b.border_log, b.border_conflicts = [], []
    b.border_names = None
    b.wall, b.edge = set(), {}
    if not b.border_style:
        return
    style = b.border_style
    b.border_names = BLOCK[style] if ENABLED else None
    sp = unconnected(key)
    if not ENABLED:
        sp = {s_: [] for s_ in "NSWE"}
    w, h = b.w, b.h
    strict_all = bands.all_band_cells(key)
    spec = b.spec
    # cells that hold something that must stay open
    keep_open = set()
    for coll in ("objects", "items", "signs", "hidden_items", "triggers"):
        keep_open |= {(o["x"], o["y"]) for o in spec.get(coll, [])}
    for ex in spec.get("exits", []):
        keep_open |= {tuple(c) for c in ex["cells"]}
    for bd in spec.get("buildings", []):
        p = b.ts["prefabs"][bd["prefab"]]
        door = p.get("door")
        for dx, dy in ([] if not door else door if isinstance(door[0], list) else [door]):
            keep_open |= {(bd["x"] + dx, bd["y"] + dy), (bd["x"] + dx, bd["y"] + dy + 1)}

    if style == "water":
        changed = 0
        for side in "NSWE":
            if not sp[side] or terrain_agrees(b, style, side, sp[side]):
                continue
            for lo, hi in sp[side]:
                for i in range(lo, hi):
                    for k in range(2):
                        x, y = cell_at(b, side, i, k)
                        if (x, y) in keep_open or (x, y) in strict_all or b.grid[y][x] in "~Iw#":
                            continue
                        if b.grid[y][x] in WALKABLE_ON | set("BTHKPM"):
                            b.grid[y][x] = "~"
                            changed += 1
        if changed:
            b.border_log.append(f"water wall: {changed} edge cells made water")
        return

    # swamp / dry: depth per side, the walls, the edge cells
    depth = {}
    for side in "NSWE":
        if not sp[side]:
            continue
        d0 = min_depth(b, side)
        depth[side] = d0 if terrain_agrees(b, style, side, sp[side]) else d0 + 2
    wall = set()

    def build_walls(depth):
        out = set()
        for side, d in depth.items():
            for lo, hi in sp[side]:
                for i in range(lo, hi):
                    for k in range(d):
                        out.add(cell_at(b, side, i, k))
        return out
    # an event on a wall shortens that side's wall until nothing stands on it
    while True:
        wall = build_walls(depth)
        hit = [(s, c) for s in depth for c in [c for c in wall if c in keep_open]]
        if not hit:
            break
        side = hit[0][0]
        if depth[side] <= min_depth(b, side):
            break
        depth[side] -= 2
        b.border_log.append(f"{side} wall shortened to {depth[side]}: something stands at {hit[0][1]}")
    wall -= strict_all
    b.border_depth = depth
    # spec "walls": gate walls of canopy inside a seam band (the pieces are primary ones, so they are allowed there): e.g. Grand Oak's
    # tree wall along the Route 2 side, which gates the road. {"side", "depth", "lo", "hi", "gaps": [[lo, hi], ...]}
    gap_cells = set()
    for w_ in spec.get("walls", []):
        side, d = w_["side"], w_["depth"]
        for i in range(w_["lo"], w_["hi"]):
            gap = any(g0 <= i < g1 for g0, g1 in w_.get("gaps", []))
            for k in range(d + 1):
                c = cell_at(b, side, i, k)
                if gap:
                    gap_cells.add(c)
                elif k < d:
                    wall.add(c)
    wall -= gap_cells

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
        return True           # beyond a corner: the border block
    edge = {}
    for y in range(h):
        for x in range(w):
            if (x, y) in wall or (x, y) in gap_cells or ((x, y) in strict_all and not any(
                    (x + dx, y + dy) in wall for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))):
                continue
            n, s, we, e = is_wall(x, y - 1), is_wall(x, y + 1), is_wall(x - 1, y), is_wall(x + 1, y)
            if not (n or s or we or e):
                continue
            if n and we:
                face = "in_NW"
            elif n and e:
                face = "in_NE"
            elif s and we:
                face = "in_SW"
            elif s and e:
                face = "in_SE"
            elif n and not s:
                face = "S"
            elif s and not n:
                face = "N"
            elif we and not e:
                face = "E"
            elif e and not we:
                face = "W"
            else:
                wall.add((x, y))      # squeezed between two walls: wall too
                continue
            edge[(x, y)] = face
    for c in list(edge):
        if c in wall or c in keep_open:
            edge.pop(c)
            b.border_conflicts.append(f"edge cell {c} holds an event/exit: left plain")
    # props under the wall and the edge cells go; structures are a conflict
    zone = wall | set(edge)
    keep, dropped = [], []
    for bd in spec.get("buildings", []):
        cells = {(x, y) for x, y, _ in __import__("band_rules").prefab_cells(b, bd)}
        if not (cells & zone):
            keep.append(bd)
        elif __import__("band_rules").is_structure(b, bd):
            keep.append(bd)
            b.border_conflicts.append(f"{bd.get('label', bd['prefab'])} ({bd['prefab']}) at ({bd['x']},{bd['y']}) stands in the wall")
        else:
            dropped.append(bd)
    if dropped:
        spec["buildings"] = keep
        by = {}
        for bd in dropped:
            by.setdefault(bd["prefab"], 0)
            by[bd["prefab"]] += 1
        b.border_log.append("props under the wall taken out: " + ", ".join(f"{k} x{v}" for k, v in sorted(by.items())))
        gone = {(x, y) for bd in dropped for x, y, _ in __import__("band_rules").prefab_cells(b, bd)}
        spec["signs"] = [g for g in spec.get("signs", []) if (g["x"], g["y"]) not in gone]
    # the ground under the wall and the edge cells becomes the plain terrain of the style (a road or a wall piece there goes)
    for side, d in depth.items():       # the terrain under a wall is the terrain of the cell it hangs over (no autotile edges inside it)
        for lo, hi in sp[side]:
            for i in range(lo, hi):
                x0, y0 = cell_at(b, side, i, d)
                src = b.grid[y0][x0]
                if src in "HKPMBT:=%&p":
                    src = {"swamp": ".", "dry": "d"}[style]
                for k in range(d):
                    x, y = cell_at(b, side, i, k)
                    if (x, y) in wall:
                        b.grid[y][x] = src
    b.wall, b.edge = wall, edge
    b.border_log.append(f"{style} border: depths " + ", ".join(f"{s}={d}" for s, d in sorted(depth.items()))
                        + f"; {len(wall)} wall cells, {len(edge)} edge cells")


def _parity(face, x, y):
    return None if face.startswith("in_") else (x & 1 if face in "SN" else y & 1)


def edge_base(b, x, y, mapping_inv):
    """the canonical ground an edge cell sits on: 'marsh' | 'water' | 'dry' | 'grass' | None (anything else: baked over it)"""
    name = mapping_inv.get(b.blocks[y][x] & 0x3FF, "")
    if name in ("ekat:marsh_C", "ekat:marsh_plants1", "ekat:marsh_plants3"):
        return "marsh", "ekat:marsh_C"
    if name in ("ekat:water_C", "ekat:water_lily", "ekat:water_weeds1"):
        return "water", "ekat:water_C"
    if name.startswith("dry:") and name.split(":")[1] in ("0_0", "1_0", "2_0", "3_0"):
        return "dry", "dry:0_0"
    if name == "ekat:grass":
        return "grass", name
    return None, name


def apply(b):
    """lay the wall and the edge cells over the drawn map (after Builder.draw_once)"""
    if not getattr(b, "border_style", None) or b.border_style == "water":
        return
    import sys as _sys
    build = _sys.modules[type(b).__module__]
    style = b.border_style
    inv = {}
    for n, v in build.MAPPING.items():
        inv.setdefault(v, n)
    names = BLOCK[style]
    for (x, y) in sorted(b.wall):
        b.blocks[y][x] = build.block(build.hx(names[(x & 1) + (y & 1) * 2]), 1, 3)
    for (x, y), face in sorted(b.edge.items()):
        terr, under = edge_base(b, x, y, inv)
        par = _parity(face, x, y)
        suffix = "" if par is None else f"_{par}"
        if terr in ("marsh", "water") and style == "swamp":
            nm = f"bd:swamp_{face}_{terr}{suffix}"
        elif terr == "dry" and style == "dry":
            nm = f"bd:dry_{face}_dry{suffix}"
        else:
            nm = bake(b, build, inv, style, face, par, x, y, terr, under)
            if nm is None:
                continue
        b.blocks[y][x] = build.block(build.hx(nm), 1, 3)


_GROUND = {}


def bake(b, build, inv, style, face, par, x, y, terr, under):
    """an edge cell baked over whatever ground is there: a pixels patch (swamp on grass: the primary's, else the map's tileset)"""
    from PIL import Image
    from render import Tilesets
    sys.path.insert(0, os.path.join(HERE, "sources", "orleans_custom"))
    import make_borders as mb
    root = os.getcwd()
    ts = Tilesets(os.path.join(root, b.ts["primary_dir"]), os.path.join(root, b.ts["secondary_dir"]))
    base = ts.metatile(b.blocks[y][x] & 0x3FF).convert("RGB")
    img = mb.bake_edge(style, face, par, base)
    prefix = "bdg" if (terr == "grass" and style == "swamp") else "bk"
    bid = f"{prefix}_{style}_{face}{'' if par is None else par}_" + hashlib.sha1(under.encode()).hexdigest()[:8]
    if f"patch:{bid}" in build.MAPPING:
        build.USED.add(f"patch:{bid}")
        return f"patch:{bid}"
    out_dir = os.path.join(HERE, "tilesets", "borders")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, bid + ".png")
    if not os.path.exists(path):
        img.save(path)
    if not under or ":" not in under:
        return None
    b.pending_blends[bid] = {"id": bid, "pixels": os.path.relpath(path, root).replace(os.sep, "/"), "attr_of": under}
    return None

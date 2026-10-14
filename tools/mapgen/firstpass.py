"""First-pass builds of every remaining route and town, straight from their mockups.

For each map: extract the mockup (outdoor colours), convert the terrain to what the chosen tileset supports,
place building prefabs by type (stand-ins where the tileset has no Center/Mart/gym), plant trees on wooded
areas, boats on trawler blocks, placeholder NPCs on N/T markers; create the map shell (map.json, layout,
map group, map section, scripts.inc), build with build.py --no-blends and run check.py. A first pass is a
starting point for review, not a finished map: specs go to maps/<key>.json and are meant to be hand-tuned.

usage (from the decomp root): python tools/mapgen/firstpass.py [key ...]     (default: every map below)
"""
import json
import math
import os
import subprocess
import sys
from collections import Counter, deque

import levee
from town_plans import (DOCK_ALL, DRY_FADE, EDGE_CLEAR, ROCK_KEEPOFF, EDGE_PAINT, SEAM_ADOPT, DRY_ROUTES, EXTRA_EXITS, GROW, PLANS, ROUTE_PLANS, SCALE, TERRAIN_FIX,
                        TOWN_CFG, door_label)
import route_features  # landmarks and details for the routes (route_features.py)
for _k, _v in route_features.PLANS.items():  # its buildings join town_plans.ROUTE_PLANS
    ROUTE_PLANS[_k] = ROUTE_PLANS.get(_k, []) + list(_v)

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(HERE, "maps")
MOCKUPS = os.path.join("..", "orleans_maps")

# (key, mockup, map name, constant, kind, tileset config, map section, music)
TOWNS = [
    ("storms_edge", "03_storms_edge", "StormsEdge", "MAP_STORMS_EDGE", "town", "orleans_harbor", "MAPSEC_STORMS_EDGE", "MUS_RG_VERMILLION"),
    ("crescent_city", "04_crescent_city", "CrescentCity", "MAP_CRESCENT_CITY", "city", "orleans_harbor", "MAPSEC_CRESCENT_CITY", "MUS_RG_CELADON"),
    ("pointe_rouge", "05_pointe_rouge", "PointeRouge", "MAP_POINTE_ROUGE", "city", "orleans_harbor", "MAPSEC_POINTE_ROUGE", "MUS_RG_SILPH"),
    ("camp_cocodrie", "06_camp_cocodrie", "CampCocodrie", "MAP_CAMP_COCODRIE", "town", "orleans_harbor", "MAPSEC_CAMP_COCODRIE", "MUS_RG_FUCHSIA"),
    ("lutins_hollow", "07_lutins_hollow", "LutinsHollow", "MAP_LUTINS_HOLLOW", "town", "orleans_harbor", "MAPSEC_LUTINS_HOLLOW", "MUS_RG_LAVENDER"),
    ("redfield", "08_redfield", "Redfield", "MAP_REDFIELD", "town", "orleans_harbor", "MAPSEC_REDFIELD", "MUS_RG_PEWTER"),
    ("lands_end", "09_lands_end", "LandsEnd", "MAP_LANDS_END", "town", "orleans_harbor", "MAPSEC_LANDS_END", "MUS_RG_CINNABAR"),
    ("oldest_shrine", "13_oldest_shrine", "OldestShrine", "MAP_OLDEST_SHRINE", "route", "orleans_route", "MAPSEC_OLDEST_SHRINE", "MUS_RG_SEVII_ROUTE"),
]
SECTION_NAMES = {"MAPSEC_STORMS_EDGE": "STORM'S EDGE", "MAPSEC_CRESCENT_CITY": "CRESCENT CITY",
                 "MAPSEC_POINTE_ROUGE": "POINTE ROUGE", "MAPSEC_CAMP_COCODRIE": "CAMP COCODRIE",
                 "MAPSEC_LUTINS_HOLLOW": "LUTIN'S HOLLOW", "MAPSEC_REDFIELD": "REDFIELD",
                 "MAPSEC_LANDS_END": "LAND'S END", "MAPSEC_OLDEST_SHRINE": "OLDEST SHRINE"}
BOAT_ROUTES = {6, 7, 8, 9, 10, 11, 18, 19, 20, 21, 22, 25}


def routes():
    out = []
    for n in range(2, 26):
        mock = [f for f in os.listdir(MOCKUPS) if f.startswith(f"r{n:02d}_")][0][:-4]
        out.append((f"route_{n}", mock, f"Route{n}", f"MAP_ORLEANS_ROUTE{n}", "route", "orleans_route",
                    f"MAPSEC_ROUTE_{n}", "MUS_SURF" if n in BOAT_ROUTES else "MUS_RG_ROUTE24"))
    return out


ALL = TOWNS + routes()


def load_cfg(name):
    return json.load(open(os.path.join(HERE, "tilesets", name + ".json")))


# ---------------------------------------------------------------- grid conversion
def components(grid, chars):
    h, w = len(grid), len(grid[0])
    seen, out = set(), []
    for y in range(h):
        for x in range(w):
            if grid[y][x] in chars and (x, y) not in seen:
                q, cells = deque([(x, y)]), []
                seen.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    cells.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and grid[ny][nx] in chars:
                            seen.add((nx, ny))
                            q.append((nx, ny))
                out.append(cells)
    return out


def normalise(grid, cfg):
    """Mockup characters -> characters this tileset config supports; returns (grid, tree cells, boat blocks)."""
    allowed = set(cfg["terrain"])
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    # trawlers and other industrial blocks standing in water are boats; on land they are buildings
    boats = []
    for cells in components(g, "I"):
        ring = [(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        ring = [(x, y) for x, y in ring if 0 <= x < w and 0 <= y < h and g[y][x] not in "I#"]  # piers are neutral
        wet = bool(ring) and sum(g[y][x] == "~" for x, y in ring) >= len(ring) / 2
        for x, y in cells:
            g[y][x] = "~" if wet else "H"
        if wet:
            boats.append((min(x for x, _ in cells), min(y for _, y in cells)))
    trees = set()
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c in "TR":
                trees.add((x, y))
                c = "."
            elif c == "S":
                c = "="          # stone paving, not the churchyard set
            elif c == "#":
                pass             # boardwalks: docks() makes them piers over water, path on land
            elif c == "Y":
                c = "H"
            elif c == "G" and "G" not in allowed:
                c = '"'
            if c not in allowed:
                c = "."
            g[y][x] = c
    return ["".join(r) for r in g], trees, boats


# ---------------------------------------------------------------- placement
def fits(occ, x, y, pw, ph, w, h):
    return 0 <= x and 0 <= y and x + pw <= w and y + ph <= h and not any(
        (i, j) in occ for i in range(x, x + pw) for j in range(y, y + ph))


def occupy(occ, x, y, pw, ph):
    for i in range(x, x + pw):
        for j in range(y, y + ph):
            occ.add((i, j))


STAND_IN = {  # mockup building kind -> (bayou prefab, label)
    "P": ("house_b", "Pokémon Center (stand-in)"), "M": ("house_a", "Mart / shop (stand-in)"),
    "Y": ("church", "Gym (stand-in)"), "K": ("barn", "Key building (stand-in)"), "H": ("house_a", "House"),
}


def place_buildings(detected, grid, cfg, occ):
    prefabs = cfg["prefabs"]
    out, skipped = [], []
    h, w = len(grid), len(grid[0])
    flip = 0
    for b in detected:
        if b["w"] * b["h"] < 4:  # marker outlines
            continue
        prefab, label = STAND_IN.get(b["kind"], ("house_a", "Building"))
        if b["kind"] == "H" and (b["w"] < 4 or b["h"] < 4):
            prefab = "cabin"
        if b["kind"] == "H" and prefab == "house_a":
            prefab = ("house_a", "house_b")[flip % 2]
            flip += 1
        if b["kind"] == "K" and b["w"] < 5:
            prefab = "house_b"
        if prefab not in prefabs:
            skipped.append((b, "no prefab in this tileset"))
            continue
        rows = prefabs[prefab]["rows"]
        ph, pw = len(rows), len(rows[0])
        x = max(0, min(w - pw, b["x"] + (b["w"] - pw) // 2))
        y = max(0, min(h - ph - 1, b["y"] + b["h"] - ph))
        placed = None
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0), (0, 1), (1, -1), (-1, -1)):
            if fits(occ, x + dx, y + dy, pw, ph + 1, w, h):  # +1: keep the row under the door free
                placed = (x + dx, y + dy)
                break
        if not placed:
            skipped.append((b, "no room for the prefab"))
            continue
        x, y = placed
        occupy(occ, x, y, pw, ph + 1)
        out.append({"prefab": prefab, "x": x, "y": y, "label": label})
    return out, skipped


def clear_buildings(grid, street, roads_win=False):
    """Building cells of the mockup -> the ground around them (planned towns place their own buildings).
    roads_win: a box standing in a road or yard (a route's gate, a yard's warehouse) becomes road."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    for cells in components(g, "HKPMI"):
        ring = Counter(g[y + dy][x + dx] for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] not in "HKPMI")
        paths = sum(n for c, n in ring.items() if c in ":=")
        ground = next((c for c, _ in ring.most_common() if c in ".\"=:L"), street)
        if roads_win and paths >= 0.3 * sum(ring.values()):
            ground = ":" if ring[":"] >= ring["="] else "="
        for x, y in cells:
            g[y][x] = ground
    return ["".join(r) for r in g]


def scale_grid(grid, s):
    h, w = len(grid), len(grid[0])
    W, H = round(w * s), round(h * s)
    return ["".join(grid[min(h - 1, int(y / s))][min(w - 1, int(x / s))] for x in range(W)) for y in range(H)]


def place_planned(town, grid, cfg, occ, s):
    """The town's planned buildings (town_plans.PLANS; a route's landmarks from ROUTE_PLANS), each centred on
    its scaled mockup rectangle. Buildings without an interior are closed (their doors stay shut)."""
    import interiors as mock
    out, skipped = [], []
    h, w = len(grid), len(grid[0])
    plan = PLANS[town] if town in PLANS else [(None, label, prefab, rect) for label, prefab, rect in ROUTE_PLANS.get(town, [])]
    for key, label, prefab, (bx, by, bw, bh) in plan:
        rows = cfg["prefabs"][prefab]["rows"]
        ph, pw = len(rows), len(rows[0])
        cx, bottom = (bx + bw / 2) * s, (by + bh) * s
        x = max(0, min(w - pw, round(cx - pw / 2)))
        y = max(0, min(h - ph - 1, round(bottom) - ph))
        placed = None
        apart = lambda px_, py_: not any((px_ - 1, py_ + j) in occ or (px_ + pw, py_ + j) in occ for j in range(ph))
        for gap in (True, False):  # a tile apart from the neighbours if there's room, else as close as it fits
            for r in range(0, 5):  # nearest free spot, a ring at a time (the +1 keeps the row under the door free)
                ring = sorted(((dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r),
                              key=lambda d: (abs(d[1]), abs(d[0])))
                placed = next(((x + dx, y + dy) for dx, dy in ring if fits(occ, x + dx, y + dy, pw, ph + 1, w, h)
                               and (not gap or apart(x + dx, y + dy))), None)
                if placed:
                    break
            if placed:
                break
        if not placed:
            skipped.append((key or label, "no room for the prefab"))
            continue
        x, y = placed
        occupy(occ, x, y, pw, ph + 1)
        name = door_label(key, mock.INTERIORS[key]["title"]) if key else label
        out.append({"prefab": prefab, "x": x, "y": y, "label": name, **({} if key else {"closed": True})})
    return out, skipped


def with_placeholders(cfg):
    """Stand-ins for route landmark art that isn't drawn yet (route_features.PLACEHOLDERS): each gets a prefab of
    the same footprint built from existing pieces, flagged "_placeholder" (the spec gets the stand-in's own prefab
    name plus rows, see swap_placeholders). A real prefab of the same name in the tileset config wins."""
    pf = cfg["prefabs"]
    for name, (like, pattern, walk) in route_features.PLACEHOLDERS.items():
        if name in pf or like not in pf:
            continue
        src = pf[like]
        if pattern is None:
            pf[name] = dict(src, _placeholder=like)
            continue
        sh, sw = len(src["rows"]), len(src["rows"][0])
        rows = [[src["rows"][j % sh][i % sw] if c == "#" else None for i, c in enumerate(p)] for j, p in enumerate(pattern)]
        pf[name] = {"rows": rows, "door": None, "_placeholder": like,
                    **({"passable": [[i, j] for j, r in enumerate(rows) for i, c in enumerate(r) if c is not None]} if walk else {})}
    return cfg


def swap_placeholders(buildings, cfg):
    """Spec buildings that use a placeholder name get the stand-in's prefab (the one the tileset config has) and
    its rows, so build.py needs no new prefab; "art" keeps the intended name."""
    out = []
    for b in buildings:
        pf = cfg["prefabs"].get(b["prefab"])
        if pf and "_placeholder" in pf:
            b = dict(b, prefab=pf["_placeholder"], art=b["prefab"], rows=pf["rows"], **(
                {"passable": pf["passable"]} if "passable" in pf else {}))
        out.append(b)
    return out


def mock_cells(mock, det, rgb, box=None, tol=5):
    """Tiles of the mockup whose key colour is rgb (sampled at five points of the tile), within box (x0, y0, x1, y1)."""
    from PIL import Image
    im = Image.open(os.path.join(MOCKUPS, mock + ".png")).convert("RGB")
    fx, fy = det["frame"][0], det["frame"][1]
    pitch, out = det["pitch"], set()
    x0, y0, x1, y1 = box or (0, 0, det["width"], det["height"])
    for ty in range(y0, y1):
        for tx in range(x0, x1):
            hits = 0
            for ox, oy in ((.5, .5), (.3, .3), (.7, .3), (.3, .7), (.7, .7)):
                c = im.getpixel((int(fx + (tx + ox) * pitch), int(fy + (ty + oy) * pitch)))
                hits += all(abs(a - b) <= tol for a, b in zip(c, rgb))
            if hits >= 3:
                out.add((tx, ty))
    return out


def apply_route_terrain(key, grid, mock, det):
    """route_features terrain edits: rectangles and key-colour regions painted over the normalised mockup."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    for e in route_features.FEATURES.get(key, {}).get("terrain", []) + route_features.FEATURES.get(key, {}).get("terrain_edges", []):
        if e[0] == "rect":
            cells = [(x, y) for y in range(e[2], e[2] + e[4]) for x in range(e[1], e[1] + e[3])]
            ch = e[5]
        else:
            cells = mock_cells(mock, det, e[1], e[3] if len(e) > 3 else None)
            ch = e[2]
        for x, y in cells:
            if 0 <= x < w and 0 <= y < h:
                g[y][x] = ch
    return ["".join(r) for r in g]


DRY_PROPS = {"cypress_marsh": "field_tree_l", "cypress_small_marsh": "field_tree", "cypress": "field_tree_l",
             "cypress_small": "field_tree", "boulder": "rock_l"}


def dry_features(feat):
    """A dry route's landmarks: field trees and rocks of the dry-country set instead of cypress in marsh and the
    Cianwood boulder, no marsh patches under anything."""
    def prop(e):
        opt = {k: v for k, v in (e[4] if len(e) > 4 else {}).items() if k not in ("patch", "ring")}
        return (DRY_PROPS.get(e[0], e[0]),) + tuple(e[1:4]) + ((opt,) if opt else ())
    return dict(feat, props=[prop(e) for e in feat.get("props", [])])


def place_features(key, grid, cfg, occ, existing=()):
    """route_features props, lines and signs, each at the free spot nearest the stated cell (stand-ins for undrawn
    art included). A prop drawn on a patch (marsh tree, reeds, a shrine; or standing in water) needs its footprint
    and the cell to its right and below (the dual-grid corners) to be that terrain, so the patch border never runs
    through it; the ground there is painted to marsh. Returns (grid, buildings, signs, cells to keep as painted)."""
    feat = route_features.FEATURES.get(key, {})
    if key in DRY_ROUTES:
        feat = dry_features(feat)
    pf = cfg["prefabs"]
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    out, signs, keep = [], [], set()
    GROUND = '."G'
    # a tree's marsh grove (the cells round its footprint) stays whole: nothing is painted or stood on there
    grove = {(b["x"] + i, b["y"] + j) for b in existing if pf.get(b["prefab"], {}).get("on_patch") == '"'
             for j in range(-1, len(pf[b["prefab"]]["rows"]) + 1) for i in range(-1, len(pf[b["prefab"]]["rows"][0]) + 1)}

    def spot(name, x, y, opt):
        rows = pf[name]["rows"]
        ph, pw = len(rows), len(rows[0])
        cells = [(i, j) for j, r in enumerate(rows) for i, c in enumerate(r) if c is not None]
        patch = opt.get("patch")
        on = opt.get("on", GROUND)
        water = "~" in on
        reach = opt.get("reach", 2)
        cand = sorted(((abs(dx) + abs(dy), dx, dy) for dx in range(-reach, reach + 1) for dy in range(-reach, reach + 1)))
        pad = [(pw, j) for j in range(ph + 1)] + [(i, ph) for i in range(pw)] if (patch or water) else []
        for _, dx, dy in cand:
            px, py = x + dx, y + dy
            good = all(0 <= px + i < w and 0 <= py + j < h and g[py + j][px + i] in on and (px + i, py + j) not in occ
                       and (patch or water or (px + i, py + j) not in grove) for i, j in cells)
            if good and pad:
                extra = on if water else GROUND + patch
                good = all(0 <= px + i < w and 0 <= py + j < h and g[py + j][px + i] in extra + ("I" if water else "")
                           and (px + i, py + j) not in occ for i, j in pad)
            if not good:
                continue
            door = pf[name].get("door")
            if door and not (py + door[1] + 1 < h and g[py + door[1] + 1][px + door[0]] in GROUND + ":="):
                continue
            return px, py, pw, ph
        return None

    def put(name, x, y, label, opt):
        if name not in pf:
            print(f"    feature skipped (no prefab {name})")
            return None
        at = spot(name, x, y, opt)
        if not at:
            print(f"    feature skipped ({name} near {x},{y}: no room)")
            return None
        px, py, pw, ph = at
        patch = opt.get("patch")
        ring = opt.get("ring", 1 if patch else 0)
        for j in range(-ring, ph + ring + (1 if patch else 0)):
            for i in range(-ring, pw + ring + (1 if patch else 0)):
                cx, cy = px + i, py + j
                if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in occ:
                    inside = 0 <= i < pw and 0 <= j < ph
                    if patch and (inside or g[cy][cx] in GROUND):
                        g[cy][cx] = patch
                        keep.add((cx, cy))
                    elif g[cy][cx] in 'G"L' and not patch and "~" not in opt.get("on", ""):
                        g[cy][cx] = "."
        occupy(occ, px, py, pw, ph + (1 if pf[name].get("door") else 0))
        b = {"prefab": name, "x": px, "y": py, "label": label}
        if pf[name].get("door"):
            b["closed"] = True
        out.append(b)
        return b

    for name, x0, y0, x1, y1, label in feat.get("lines", []):  # tracks first: they run the whole way
        n = max(abs(x1 - x0), abs(y1 - y0)) + 1
        for k in range(n):
            x = x0 + (x1 - x0) * k // max(1, n - 1)
            y = y0 + (y1 - y0) * k // max(1, n - 1)
            if 0 <= x < w and 0 <= y < h and g[y][x] in GROUND + "L" and (x, y) not in occ:
                put(name, x, y, label, {"reach": 0})
    for e in feat.get("props", []):
        put(e[0], e[1], e[2], e[3], e[4] if len(e) > 4 else {})
    if feat.get("spans"):  # overhead wires along the top row of a line of towers: _r west of each tower, _l east of it
        tower, wire = feat["spans"]
        towers = sorted((b for b in out if b["prefab"] == tower), key=lambda b: b["x"])
        if towers and wire + "_l" in pf:
            ty = towers[0]["y"]
            tw = len(pf[tower]["rows"][0])
            cells = {}
            for k, t in enumerate(towers):
                cells[t["x"] - 1] = wire + "_r"
                cells[t["x"] + tw] = wire + "_l"
                lo = t["x"] + tw + 1
                hi = (towers[k + 1]["x"] - 2) if k + 1 < len(towers) else w - 1
                for x in range(lo, hi + 1):
                    cells.setdefault(x, wire)
            for x in range(0, towers[0]["x"] - 1):
                cells.setdefault(x, wire)
            for x, nm in sorted(cells.items()):
                if 0 <= x < w and (x, ty) not in occ and g[ty][x] not in "~I#":
                    if g[ty][x] == "G":
                        g[ty][x] = "."  # the span's cells are plain ground: the tall grass under the wire gives way
                    occ.add((x, ty))
                    out.append({"prefab": nm, "x": x, "y": ty, "label": "Wire"})
    for n, (x, y, text) in enumerate(feat.get("signs", [])):
        b = put("sign", x, y, "Sign", {"reach": 3}) if "sign" in pf else None
        if b:
            signs.append({"id": f"RouteSign{n + 1}", "x": b["x"], "y": b["y"], "text": text})
    return ["".join(r) for r in g], out, signs, keep


def hidden_items(key, const, markers, grid, occ):
    """route_features hidden items, at the mockup's hidden-item markers: the nearest cell a player can stand on
    (not a shore tile, which is drawn as water). Water ones (opts water: found while surfing) and ones on a dock
    (opts occ) are allowed where stated. Returns (hidden items, cells reached only by Surf)."""
    h, w = len(grid), len(grid[0])
    marks = [(m["x"], m["y"]) for m in markers if m["kind"] == "hidden_item"]
    out, surf = [], []
    shore = lambda x, y: any(grid[j][i] in "~I" for i in range(max(0, x - 1), min(w, x + 2)) for j in range(max(0, y - 1), min(h, y + 2)))
    for n, e in enumerate(route_features.FEATURES.get(key, {}).get("hidden", [])):
        x, y = (e[2], e[3]) if len(e) > 3 else marks[n] if n < len(marks) else (None, None)
        if x is None:
            continue
        opt = e[4] if len(e) > 4 else {}
        cells = sorted(((abs(dx) + abs(dy), x + dx, y + dy) for dx in range(-4, 5) for dy in range(-4, 5)))
        at = None
        for _, cx, cy in cells:
            if not (0 <= cx < w and 0 <= cy < h) or ((cx, cy) in occ and not opt.get("occ")):
                continue
            if grid[cy][cx] in '.:="LG' and not shore(cx, cy):
                at = (cx, cy)
                break
            if opt.get("water") and grid[cy][cx] in "~I" and (cx, cy) not in occ:
                at = (cx, cy)
                surf.append([cx, cy])
                break
            if opt.get("occ") and (cx, cy) in occ:
                at = (cx, cy)
                break
        if at:
            occ.add(at)
            out.append({"x": at[0], "y": at[1], "item": e[0], "flag": item_flag(const, f"H{n}"), "_note": e[1]})
    return out, surf


def boulders(key, rocks, grid, cfg, occ, prefab="boulder"):
    """Rock in the mockup (a bluff, the salt dome) as a field of boulders on bare ground: staggered rows,
    each boulder standing on grass with a tile between neighbours, where most of its footprint is rock."""
    out = []
    if prefab not in cfg["prefabs"]:
        return out
    rows = cfg["prefabs"][prefab]["rows"]
    ph, pw = len(rows), len(rows[0])
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    import random
    rng = random.Random(key + "rocks")
    for cells in components([["R" if (x, y) in rocks else "." for x in range(w)] for y in range(h)], "R"):
        if len(cells) < 12:
            continue
        cs = set(cells)
        if not any(min(x, y, w - 1 - x, h - 1 - y) == 0 for x, y in cells) and len(cells) < 40:
            continue  # a small stone patch inside the map (oyster beds, a yard) is not a bluff
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        for y in range(min(ys), max(ys) - ph + 2, ph + 1):
            off = (pw + 1) // 2 if ((y - min(ys)) // (ph + 1)) % 2 else 0
            for x0 in range(min(xs) + off, max(xs) - pw + 2, pw + 1):
                if rng.random() < 0.3:
                    continue  # gaps, so the field reads as a natural scatter, not a lattice
                x = x0 + rng.choice((-1, 0, 0, 1))
                foot = [(i, j) for i in range(x, x + pw) for j in range(y, y + ph)]
                ring = [(i, j) for i in range(x - 1, x + pw + 1) for j in range(y - 1, y + ph + 1)
                        if 0 <= i < w and 0 <= j < h]  # a tile clear all round (the map edge is fine)
                if sum(c in cs for c in foot) * 2 < len(foot) or not fits(occ, x, y, pw, ph, w, h) or \
                        any(c in occ for c in ring):
                    continue
                if any(g[j][i] not in '."GL' for i, j in foot):
                    continue
                for i, j in foot:
                    g[j][i] = "."
                occupy(occ, x, y, pw, ph)
                out.append({"prefab": prefab, "x": x, "y": y, "label": "Boulder"})
    grid[:] = ["".join(r) for r in g]
    return out


def carve_paths(buildings, grid, cfg, occ, path_char, dock_walk=frozenset(), exits=None):
    """A path at least 2 wide from every door to the nearest road or street (cheapest over open ground,
    around buildings, through water only when there is no other way); then every door's patch of ground
    is joined to the main one, so no building sits on an island of its own."""
    import heapq
    blocked = {(b["x"] + i, b["y"] + j) for b in buildings
               for j, row in enumerate(b.get("rows") or cfg["prefabs"][b["prefab"]]["rows"]) for i in range(len(row))}
    blocked -= dock_walk
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    cost = {".": 1, "G": 2, '"': 3, "L": 2, "~": 25, "I": 25}

    def route(sources, is_goal):
        best, prev = {c: 0 for c in sources}, {}
        heap = [(0, x, y) for x, y in sources]
        heapq.heapify(heap)
        while heap:
            d, x, y = heapq.heappop(heap)
            if d > best.get((x, y), 1e9):
                continue
            if is_goal(x, y):
                line, cell = [], (x, y)
                while cell in prev:
                    cell = prev[cell]
                    line.append(cell)
                return line
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    nd = d + (1 if (nx, ny) in dock_walk else cost.get(g[ny][nx], 1))
                    if nd < best.get((nx, ny), 1e9):
                        best[(nx, ny)], prev[(nx, ny)] = nd, (x, y)
                        heapq.heappush(heap, (nd, nx, ny))
        return []

    def paint(line):
        # a way across open water longer than a short bridge is no way at all: islands are reached by Surf
        if sum(g[y][x] in "~I" for x, y in line) > 6:
            return False
        on_line = set(line)
        for x, y in line:  # 2x2 brush: two wide on straight runs either way
            for i, j in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
                if 0 <= i < w and 0 <= j < h and (i, j) not in blocked and (i, j) not in dock_walk and g[j][i] not in ":=#":
                    if g[j][i] in "~I":
                        # across water the way is a boardwalk ('#') that docks() makes a railed bridge, never a
                        # dam; but the brush's other half never spills into the water beside a shore path
                        if (i, j) in on_line or any((i + a, j + c) in on_line and g[j + c][i + a] in "~I"
                                                    for a, c in ((-1, 0), (0, -1)) if 0 <= i + a < w and 0 <= j + c < h):
                            g[j][i] = "#"
                        continue
                    g[j][i] = path_char

    starts = []
    for b in buildings:
        for dx, dy in door_cells(cfg, b):
            sx, sy = dx, dy + 1
            if sy >= h:
                continue
            starts.append((sx, sy))
            own = {(i, j) for i in (sx, sx + 1) for j in (sy, sy + 1)}
            paint(route([(sx, sy)], lambda x, y: (g[y][x] in ":=" or (x, y) in dock_walk) and (x, y) not in own))

    to_edges(g, blocked, path_char, exits)
    join_network(g, route, paint, dock_walk, starts)
    return ["".join(r) for r in g]


SIDE = {(0, 1): "S", (0, -1): "N", (1, 0): "E", (-1, 0): "W"}


def near_exit(exits, side, a, slack=4):
    return exits is None or any(e["side"] == side and abs(e["pos"] - a) <= slack for e in exits)


def to_edges(g, blocked, path_char, exits=None, reach=7):
    """Roads heading for the mockup's exits run all the way to the edge (the last tiles are often hidden under
    the exit arrow or label): a straight road ending within `reach` tiles of an edge, running towards it and
    within a few tiles of an exit arrow on that edge, is extended. Roads that reach an edge where the mockup
    shows no exit are cut back from it, so a map never seems to lead somewhere it doesn't."""
    h, w = len(g), len(g[0])
    is_p = lambda x, y: 0 <= x < w and 0 <= y < h and g[y][x] in ":="
    for (dx, dy), side in SIDE.items():
        for a in (range(w) if dy else range(h)):
            at = lambda k: (a, h - 1 - k if dy > 0 else k) if dy else (w - 1 - k if dx > 0 else k, a)
            if not near_exit(exits, side, a):
                # no exit here: a road running straight into this edge stops two tiles short of it
                if exits is not None and is_p(*at(0)) and is_p(*at(2)):
                    for k in (0, 1):
                        x, y = at(k)
                        if (x, y) not in blocked:
                            g[y][x] = "."
                continue
            for k in range(reach + 1):
                x, y = at(k)
                if is_p(x, y):
                    break
            else:
                continue
            if k == 0 or not all(is_p(x - dx * i, y - dy * i) for i in range(1, 5)):
                continue  # already at the edge, or not a straight road running towards it (a diagonal's
                # stair-steps would fill out into a wedge)
            cells = [(x + dx * i, y + dy * i) for i in range(1, k + 1)]
            if any(c in blocked or g[c[1]][c[0]] in "~I" for c in cells):
                continue
            for i, j in cells:
                g[j][i] = path_char


def landings(grid, exits, occ, dock_walk):
    """Boat exits get a landing: where the mockup's exit arrow sits on open water, a short pier runs out from
    the nearest bit of shore toward it, so there is somewhere to board. Returns (pier buildings, walk cells)."""
    h, w = len(grid), len(grid[0])
    water = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] in "~I"
    out, walk = [], set()
    for e in exits:
        side, a = e["side"], e["pos"]
        ex, ey = {"N": (a, 0), "S": (a, h - 1), "W": (0, a), "E": (w - 1, a)}[side]
        if not water(min(max(ex, 0), w - 1), min(max(ey, 0), h - 1)):
            continue
        if any((x, y) in dock_walk for x in range(ex - 6, ex + 7) for y in range(ey - 6, ey + 7)):
            continue  # a dock already serves this exit
        # the nearest shore cell (land with water beside it) to the exit
        shore = [(x, y) for y in range(h) for x in range(w) if not water(x, y) and (x, y) not in occ
                 and any(water(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        if not shore:
            continue
        sx, sy = min(shore, key=lambda c: abs(c[0] - ex) + abs(c[1] - ey))
        vertical = side in "NS" or (side in "WE" and abs(sx - ex) < abs(sy - ey))
        if vertical:
            step = 1 if ey > sy else -1
            n = 4
            ys = [sy + step * (i + 1) for i in range(n)]
            x0 = max(0, min(w - 3, sx - 1))
            if not all(water(x0 + i, y) and (x0 + i, y) not in occ for i in range(3) for y in ys):
                continue
            rows, pas = pier_v(n, land_top=step > 0, land_bottom=step < 0)
            by = sy + 1 if step > 0 else sy - len(rows)
            p = {"prefab": "pier", "x": x0, "y": by, "label": "Dock", "rows": rows, "passable": pas, "dir": "v"}
        else:
            step = 1 if ex > sx else -1
            n = 5
            xs = [sx + step * (i + 1) for i in range(n)]
            y0 = max(0, min(h - 3, sy))
            if not all(water(x, y0 + j) and (x, y0 + j) not in occ for x in xs for j in range(3)):
                continue
            rows, pas = dock_h(n, True)
            p = {"prefab": "pier", "x": min(xs), "y": y0, "label": "Dock", "rows": rows, "passable": pas, "dir": "h"}
        out.append(p)
        for i, j in pas:
            walk.add((p["x"] + i, p["y"] + j))
        for j, row in enumerate(p["rows"]):
            for i in range(len(row)):
                occ.add((p["x"] + i, p["y"] + j))
    return out, walk


def network(g, dock_walk, extra=()):
    """Components of the road network: path and street cells, dock planks (and any extra cells)."""
    h, w = len(g), len(g[0])
    on = lambda x, y: g[y][x] in ":=#" or (x, y) in dock_walk or (x, y) in extra
    comp, seen = {}, set()
    for y in range(h):
        for x in range(w):
            if on(x, y) and (x, y) not in seen:
                q, cells = deque([(x, y)]), set()
                seen.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    cells.add((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and on(nx, ny):
                            seen.add((nx, ny))
                            q.append((nx, ny))
                for c in cells:
                    comp[c] = len(cells), min(cells)
    return comp


def join_network(g, route, paint, dock_walk, starts=()):
    """One road network: every stretch of path, dock or door apron is joined to the largest one by the
    cheapest path (walking across grass alone doesn't count as connected)."""
    dead = set()
    for _ in range(80):
        comp = network(g, dock_walk, set(starts))
        if not comp:
            return
        main = max(comp.values())
        island = next((k for k in sorted(set(comp.values())) if k != main and k[1] not in dead), None)
        if not island:
            return
        cells = [c for c, k in comp.items() if k == island]
        line = route(cells, lambda x, y: comp.get((x, y)) == main)
        if not line or paint(line) is False:
            dead.add(island[1])  # walled in, or only across open water (an island): leave it be


def _var(n):
    return {"var": f"pier_{n:03X}"}


def pier_v(length, land_top, land_bottom):
    """Rows of a 3-wide north-south pier cut from the Olivine dock: capped at a land end, posts at a water end."""
    rows = [[_var(0x3E0), _var(0x3E1), _var(0x3E2)] if land_top else [_var(0x3E8), _var(0x3E9), _var(0x3EA)]]
    rows += [[_var(0x3E8), _var(0x3E9), _var(0x3EA)] for _ in range(length - 2)]
    if land_bottom:
        rows.append([_var(0x3E8), _var(0x3E9), _var(0x3EA)])
        walk = len(rows)
    else:
        rows += [[_var(0x3F0), _var(0x3F1), _var(0x3F2)], [_var(0x3F8), _var(0x3F9), _var(0x3FA)]]
        walk = len(rows) - 1
    return rows, [[i, j] for j in range(walk) for i in range(3)]


def dock_h(length, posts):
    """Rows of a 2-deep east-west dock (top edge, bottom edge) with posts under it when it stands in water."""
    mid = lambda a, b, c: [_var(a)] + [_var(b)] * (length - 2) + [_var(c)]
    rows = [mid(0x3E0, 0x3E1, 0x3E2), mid(0x3F0, 0x3F1, 0x3F2)]
    if posts:
        rows.append(mid(0x3F8, 0x3F9, 0x3F9))
    return rows, [[i, j] for j in range(2) for i in range(length)]


def bridge_h(length):
    """Rows of the railed east-west road bridge (own art, bridge.png): north rail, two deck rows, south rail;
    end posts at both banks. Deck cells are opaque, rail cells are drawn over the water (overlays)."""
    col = lambda i: "0" if i == 0 else "2" if i == length - 1 else "1"
    rail = lambda r: [{"overlay": f"brg:{col(i)}{r}"} for i in range(length)]
    rows = [rail(0), [f"brg:{col(i)}1" for i in range(length)], [f"brg:{col(i)}2" for i in range(length)], rail(3)]
    return rows, [[i, j] for j in (1, 2) for i in range(length)]


def bridge_v(length):
    """Rows of the railed north-south road bridge: west rail, two deck columns, east rail."""
    row = lambda j: "0" if j == 0 else "2" if j == length - 1 else "1"
    rows = [[{"overlay": f"brg:3{row(j)}"}, f"brg:4{row(j)}", f"brg:5{row(j)}", {"overlay": f"brg:6{row(j)}"}]
            for j in range(length)]
    return rows, [[i, j] for j in range(length) for i in (1, 2)]


def spans_water(g, x, y, chars):
    """Whether the strip of `chars` through (x, y) has water on both sides across it (a pier, or a bridge)."""
    h, w = len(g), len(g[0])

    def first(dx, dy):
        i, j = x, y
        while 0 <= i < w and 0 <= j < h and g[j][i] in chars:
            i, j = i + dx, j + dy
        return g[j][i] if 0 <= i < w and 0 <= j < h else None
    return (first(0, -1) == "~" and first(0, 1) == "~") or (first(-1, 0) == "~" and first(1, 0) == "~")


def bridges(grid, longest=12):
    """Roads crossing water (a river, a channel) become boardwalk, so docks() lays a plank bridge and the
    water keeps flowing under it; longer crossings stay causeways."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    cand = {(x, y) for y in range(h) for x in range(w) if g[y][x] in ":=" and spans_water(g, x, y, ":=")}
    for cells in components([["#" if (x, y) in cand else "." for x in range(w)] for y in range(h)], "#"):
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if max(bw, bh) <= longest and min(bw, bh) <= 4:  # straight crossings only, not diagonal causeways
            for x, y in cells:
                g[y][x] = "#"
    return ["".join(r) for r in g]


def plank_walks(cells, g, occ, out, walk):
    """Boardwalks over land (a swamp camp's walkways) as plank decking, 2 wide, from the bridge's deck
    planks (no rails): the longest straight runs first. Leftover scraps become path."""
    h, w = len(g), len(g[0])
    left = set(cells)
    while len(left) >= 3:
        best = (0, "v", 0, 0)
        for x, y in left:
            if (x, y - 1) not in left:
                n = 0
                while (x, y + n) in left:
                    n += 1
                best = max(best, (n, "v", x, y))
            if (x - 1, y) not in left:
                n = 0
                while (x + n, y) in left:
                    n += 1
                best = max(best, (n, "h", x, y))
        n, d, x, y = best
        if n < 8:  # only real boardwalks get decking; a pier's root on the shore stays path
            break
        if d == "h":
            ys = sorted({j for i, j in left if i == x + n // 2 and abs(j - y) <= 2})
            y0 = max(0, min(h - 2, round(sum(ys) / len(ys) - 0.5)))
            bx, by, rows = x, y0, [["brg:11"] * n, ["brg:12"] * n]
        else:
            xs = sorted({i for i, j in left if j == y + n // 2 and abs(i - x) <= 2})
            x0 = max(0, min(w - 2, round(sum(xs) / len(xs) - 0.5)))
            bx, by, rows = x0, y, [["brg:41", "brg:51"] for _ in range(n)]
        cells_ = [(bx + i, by + j) for j in range(len(rows)) for i in range(len(rows[0]))]
        if any(c in occ for c in cells_):
            left -= {c for c in left if (c[1] == y if d == "h" else c[0] == x)}
            continue
        out.append({"prefab": "pier", "x": bx, "y": by, "label": "Boardwalk", "rows": rows,
                    "passable": [[i, j] for j in range(len(rows)) for i in range(len(rows[0]))], "dir": "w" + d})
        for c in cells_:
            occ.add(c)
            walk.add(c)
            g[c[1]][c[0]] = "."
        if d == "v":
            left -= {(i, j) for i, j in left if y <= j < y + n and abs(i - x) <= 2}
        else:
            left -= {(i, j) for i, j in left if x <= i < x + n and abs(j - y) <= 2}
    for x, y in left:
        if g[y][x] == "#":
            g[y][x] = ":"


def docks(grid, occ, all_wet=False, planks=False):
    """Boardwalk cells ('#'): on land they become path; over water they become piers and docks cut from the
    Olivine dock art (the user's pick), split into straight runs where boardwalks branch. Returns the grid,
    the dock buildings and the set of walkable dock cells."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    out, walk = [], set()
    for cells in components(g, "#"):
        ring = [g[y + dy][x + dx] for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] != "#"]
        def watery(x, y):  # mostly water around it (not counting the boardwalk itself)
            around = [g[j][i] for i in range(x - 2, x + 3) for j in range(y - 2, y + 3)
                      if 0 <= i < w and 0 <= j < h and g[j][i] != "#"]
            return bool(around) and sum(c == "~" for c in around) >= 0.6 * len(around)
        wet = {c for c in cells if all_wet or spans_water(g, *c, "#") or watery(*c)}
        xs_, ys_ = [c[0] for c in cells], [c[1] for c in cells]
        if wet and min(max(xs_) - min(xs_), max(ys_) - min(ys_)) < 3:
            wet = set(cells)  # a straight boardwalk reaching the water is a pier from the path to its end
        land_cells = [c for c in cells if c not in wet]
        if planks and len(land_cells) >= 6:
            plank_walks(land_cells, g, occ, out, walk)  # boardwalk on land: plank decking
        else:
            for x, y in land_cells:
                g[y][x] = ":"  # boardwalk on land: path
        if len(wet) < 4:
            for x, y in wet:
                g[y][x] = "~"  # a scrap over water: open water
            continue
        left = set(wet)
        cells = list(wet)
        best = None
        for x, y in cells:
            g[y][x] = "~"
        while len(left) >= 4:
            # the longest straight run left, vertical or horizontal
            best = (0, "v", 0, 0)
            for x, y in left:
                if (x, y - 1) not in left:
                    n = 0
                    while (x, y + n) in left:
                        n += 1
                    best = max(best, (n, "v", x, y))
                if (x - 1, y) not in left:
                    n = 0
                    while (x + n, y) in left:
                        n += 1
                    best = max(best, (n, "h", x, y))
            n, d, x, y = best
            land = lambda i, j: 0 <= i < w and 0 <= j < h and g[j][i] not in "~I"
            ends = (land(x, y - 1), land(x, y + n)) if d == "v" else (land(x - 1, y), land(x + n, y))
            if n < 3 and not (n == 2 and any(ends)):  # scraps stay water; a 2-tile jetty or crossing is kept
                break
            if d == "v" and land(x, y - 1) and land(x, y + n):
                # land at both ends: a road bridge (own art, railed), deck 2 wide with a rail each side
                xs = sorted({i for i, j in left if j == y + n // 2 and abs(i - x) <= 2})
                x0 = max(1, min(w - 3, round(sum(xs) / len(xs) - 0.5)))
                rows, pas = bridge_v(n)
                bx, by, d = x0 - 1, y, "bv"
            elif d == "h" and land(x - 1, y) and land(x + n, y):
                ys = sorted({j for i, j in left if i == x + n // 2 and abs(j - y) <= 2})
                y0 = max(1, min(h - 3, round(sum(ys) / len(ys) - 0.5)))
                rows, pas = bridge_h(n)
                bx, by, d = x, y0 - 1, "bh"
            elif d == "v":
                xs = sorted({i for i, j in left if j == y + n // 2 and abs(i - x) <= 2})
                x0 = max(0, min(w - 3, round(sum(xs) / len(xs) - 1)))
                land_top = y > 0 and g[y - 1][x] not in "~"
                land_bot = y + n >= h or g[y + n][x] not in "~"
                rows, pas = pier_v(n, land_top, land_bot)
                bx, by = x0, y
            else:
                ys = sorted({j for i, j in left if i == x + n // 2 and abs(j - y) <= 2})
                y0 = max(0, min(h - 3, round(sum(ys) / len(ys) - 0.5)))
                posts = y0 + 2 < h and any(g[y0 + 2][x + i] == "~" for i in range(n))
                rows, pas = dock_h(n, posts)
                bx, by = x, y0
                if posts:  # a post only stands in open water: not on a bank, nor right beside one
                    wet3 = lambda i: all(0 <= x + i + d < w and g[y0 + 2][x + i + d] == "~" for d in (-1, 0, 1))
                    rows[2] = [c if wet3(i) else None for i, c in enumerate(rows[2])]
            foot_ = [(bx + i, by + j) for j, row in enumerate(rows) for i in range(len(row)) if row[i] is not None]
            if any(c in occ for c in foot_):
                # something already stands here (a building on the shore): this short crossing stays a path
                run = [(x, y + k) for k in range(n)] if d.endswith("v") else [(x + k, y) for k in range(n)]
                for i, j in run:
                    g[j][i] = ":"
                    left.discard((i, j))
                continue
            out.append({"prefab": "pier", "x": bx, "y": by, "label": "Bridge" if d.startswith("b") else "Dock",
                        "rows": rows, "passable": pas, "dir": d})
            for i, j in pas:
                walk.add((bx + i, by + j))
            for j, row in enumerate(rows):
                for i in range(len(row)):
                    occ.add((bx + i, by + j))
                    left.discard((bx + i, by + j))
            # the boardwalk's other cells along this run belong to it too
            if d.endswith("v"):
                left -= {(i, j) for i, j in left if y <= j < y + n and abs(i - x) <= 2}
            else:
                left -= {(i, j) for i, j in left if x <= i < x + n and abs(j - y) <= 2}
    join_docks(out, walk, occ, h)
    return ["".join(r) for r in g], out, walk


def join_docks(docks_, walk, occ, h):
    """Branch piers meet the docks they hang off: stretch each north-south pier up (and down) to the nearest
    dock plank within 4 rows, dropping that dock's posts where the pier joins."""
    plank = lambda: [_var(0x3E8), _var(0x3E9), _var(0x3EA)]
    for p in docks_:
        if p["dir"] != "v":
            continue
        cols = range(p["x"], p["x"] + 3)
        for gap in range(1, 5):  # up
            y = p["y"] - gap
            if y < 0 or not all((x, y) in walk for x in cols):
                continue
            nwalk = len({j for _, j in p["passable"]}) + gap - 1
            p["rows"] = [plank() for _ in range(gap - 1)] + [plank()] + p["rows"][1:]
            p["y"] = y + 1
            p["passable"] = [[i, j] for j in range(nwalk) for i in range(3)]
            for x in cols:
                for j in range(p["y"], p["y"] + gap):
                    occ.add((x, j))
                    walk.add((x, j))
            for d in docks_:  # the posts of the dock above give way where the pier joins
                if d["dir"] == "h" and len(d["rows"]) == 3 and p["y"] <= d["y"] + 2 < p["y"] + gap:
                    for x in cols:
                        if 0 <= x - d["x"] < len(d["rows"][2]):
                            d["rows"][2][x - d["x"]] = None
            break
        last_walk = p["y"] + len({j for _, j in p["passable"]})
        for gap in range(0, 5):  # down: planks instead of end posts, on to the dock below
            y = last_walk + gap
            if y >= h or not all((x, y) in walk for x in cols):
                continue
            nwalk = y - p["y"]
            p["rows"] = [p["rows"][0]] + [plank() for _ in range(nwalk - 1)]
            p["passable"] = [[i, j] for j in range(nwalk) for i in range(3)]
            for x in cols:
                for j in range(p["y"], y):
                    occ.add((x, j))
                    walk.add((x, j))
            break


def organic_rim(core, ok, seed, reach=2):
    """Cells to add round a grove's core so its marsh has an irregular, natural outline instead of a rounded
    square: within `reach` of the core, a cell joins where smooth noise beats its distance (so the rim bulges
    in some places and hugs the core in others). ok(x, y): whether the cell may become marsh."""
    import random
    rng = random.Random(seed)
    cs = set(core)
    xs, ys = [c[0] for c in core], [c[1] for c in core]
    phase = [rng.random() * 6.283 for _ in range(3)]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    out = []
    for x in range(min(xs) - reach, max(xs) + reach + 1):
        for y in range(min(ys) - reach, max(ys) + reach + 1):
            if (x, y) in cs or not ok(x, y):
                continue
            d = min(max(abs(x - a), abs(y - b)) for a, b in core)
            ang = math.atan2(y - cy, x - cx)
            bulge = 0.5 + 0.5 * math.sin(2 * ang + phase[0]) * math.cos(3 * ang + phase[1])
            if d - 0.3 <= reach * bulge:
                out.append((x, y))
    return out


def greenery(key, grid, cfg, occ, kind, avoid, groves=True):
    """The bayou look on top of the mockup: marsh along land edges of the map, cypress groves (a marsh
    patch with trees inside, never touching its edge) on empty ground, and cypresses standing in open
    water. Returns (grid, tree buildings)."""
    import random
    rng = random.Random(key)
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    pf = cfg["prefabs"]
    # keep clear of paths, doors and everything already placed
    near = set()
    for y in range(h):
        for x in range(w):
            if g[y][x] in ":=" or (x, y) in occ or (x, y) in avoid:
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        near.add((x + dx, y + dy))
            elif g[y][x] == "L":  # marsh never meets mud
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        near.add((x + dx, y + dy))
    out = []
    if kind != "city":  # a continuous marsh fringe along the map's land edges
        for y in range(h):
            for x in range(w):
                if min(x, y, w - 1 - x, h - 1 - y) < 3 and g[y][x] == "." and (x, y) not in near:  # mockup grass stays
                    g[y][x] = '"'
    # groves: marsh patches with one or two cypresses, a tile of marsh all round each tree
    free = lambda x, y: 0 <= x < w and 0 <= y < h and g[y][x] in '."G' and (x, y) not in near
    spots = [(x, y) for y in range(h) for x in range(w)]
    rng.shuffle(spots)
    target = sum(free(x, y) for x, y in spots) // (110 if kind == "city" else 50) if groves else 0
    taken = set()
    for x, y in spots:
        if len([b for b in out if b["prefab"].startswith("cypress") and b["prefab"].endswith("_marsh")]) >= target:
            break
        trees = rng.choice([("cypress_marsh",), ("cypress_marsh", "cypress_small_marsh"), ("cypress_small_marsh",)])
        sizes = [(len(pf[t]["rows"][0]), len(pf[t]["rows"])) for t in trees]
        gw = sum(s[0] for s in sizes) + 2 + (len(trees) - 1)
        gh = max(s[1] for s in sizes) + 2
        rect = [(x + i, y + j) for i in range(gw) for j in range(gh)]
        if not all(free(i, j) and (i, j) not in taken for i, j in rect):
            continue
        for i, j in rect + organic_rim(rect, lambda a, b: free(a, b) and (a, b) not in taken, key + str(x) + str(y)):
            g[j][i] = '"'
        for i in range(-3, gw + 3):  # groves keep apart (their rims may touch: neighbours merge into one marsh)
            for j in range(-3, gh + 3):
                taken.add((x + i, y + j))
        tx = x + 1
        for t, (tw, th) in zip(trees, sizes):
            ty = y + 1 + (gh - 2 - th)
            out.append({"prefab": t, "x": tx, "y": ty, "label": "Tree"})
            occupy(occ, tx, ty, tw, th)
            tx += tw + 1
    # cypresses in open water, well away from shores, docks and boats
    wet = lambda x, y: 0 <= x < w and 0 <= y < h and g[y][x] == "~" and (x, y) not in near and (x, y) not in taken
    water = sum(g[y][x] == "~" for y in range(h) for x in range(w))
    want, have = (0 if key in SALT else water // 160), 0  # bald cypress is a freshwater tree: none in the Gulf
    for x, y in spots:
        if have >= want:
            break
        t = rng.choice(["cypress_water", "cypress_small_water"])
        tw, th = len(pf[t]["rows"][0]), len(pf[t]["rows"])
        if all(wet(x + i, y + j) for i in range(-1, tw + 1) for j in range(-1, th + 1)):
            out.append({"prefab": t, "x": x, "y": y, "label": "Tree"})
            occupy(occ, x, y, tw, th)
            for i in range(-3, tw + 3):
                for j in range(-3, th + 3):
                    taken.add((x + i, y + j))
            have += 1
    # floating logs and snags in open water, tall reeds in the marsh (no cypress knees: the user removed them)
    for t, per in (("waterlog", 220), ("snag_water", 260)):
        tw, th = len(pf[t]["rows"][0]), len(pf[t]["rows"])
        want, have = water // per, 0
        for x, y in spots:
            if have >= want:
                break
            if all(wet(x + i, y + j) for i in range(-1, tw + 1) for j in range(-1, th + 1)):
                out.append({"prefab": t, "x": x, "y": y, "label": "Water prop"})
                occupy(occ, x, y, tw, th)
                for i in range(-3, tw + 3):
                    for j in range(-3, th + 3):
                        taken.add((x + i, y + j))
                have += 1
    if "reeds_marsh" in pf:
        tw, th = len(pf["reeds_marsh"]["rows"][0]), len(pf["reeds_marsh"]["rows"])
        marsh = sum(g[y][x] == '"' for y in range(h) for x in range(w))
        want, have = marsh // 70, 0
        for x, y in spots:
            if have >= want:
                break
            box = [(x + i, y + j) for i in range(-1, tw + 1) for j in range(-1, th + 1)]
            if all(0 <= i < w and 0 <= j < h and g[j][i] == '"' and (i, j) not in occ and (i, j) not in near
                   for i, j in box):
                out.append({"prefab": "reeds_marsh", "x": x, "y": y, "label": "Reeds"})
                occupy(occ, x, y, tw, th)
                have += 1
    # marsh never touches mud (a hard seam): any left beside mud goes back to grass
    for y in range(h):
        for x in range(w):
            if g[y][x] == '"' and (x, y) not in occ and any(
                    0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] == "L"
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                g[y][x] = "."
    return ["".join(r) for r in g], out


def levee_roads(grid):
    """Levee roads (thin mud strips running off a road, or long on their own) are road; wide mudflats stay."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    for cells in components(g, "L"):
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        thin = min(max(xs) - min(xs), max(ys) - min(ys)) + 1 <= 4
        long = max(max(xs) - min(xs), max(ys) - min(ys)) + 1 >= 10
        touches = any(0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] in ":="
                      for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if thin and touches:  # a thin strip of mud running off a road (a levee track); mudflats stay mud
            for x, y in cells:
                g[y][x] = ":"
    return ["".join(r) for r in g]


def fill_holes(grid, biggest=12, keep=frozenset()):
    """Small patches of ground walled in by road (a yard's sundial pads, a plaza's centrepiece) become road,
    so yards don't turn into rings and lattices."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    for cells in components(g, '."GL'):
        if len(cells) > biggest or any(c in keep for c in cells):
            continue
        cs = set(cells)
        ring = {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - cs
        if all(0 <= x < w and 0 <= y < h and g[y][x] in ":=" for x, y in ring):
            ch = Counter(g[y][x] for x, y in ring).most_common(1)[0][0]
            for x, y in cells:
                g[y][x] = ch
    return ["".join(r) for r in g]


def route_grass(key, grid, occ, share=None):
    """Tall grass in big organic patches away from the road (a plain-grass verge stays beside it) and off the
    shores. The mockup's own patches lead: they grow to about half again their size (at least a fifth of the
    land, at most 45%), rather than filling the route (the user found routes reading as a sea of grass)."""
    import random
    rng = random.Random(key + "grass")
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    keep = set()
    for y in range(h):
        for x in range(w):
            if g[y][x] in ":=~I#L" or (x, y) in occ:
                r = 1  # the user's rule: one tile of plain grass beside roads and shores
                for dx in range(-r, r + 1):
                    for dy in range(-r, r + 1):
                        keep.add((x + dx, y + dy))
    cand = [(x, y) for y in range(h) for x in range(w) if g[y][x] in '."' and (x, y) not in keep]
    land = sum(g[y][x] in '."GL:=' for y in range(h) for x in range(w)) or 1
    have = sum(g[y][x] == "G" for y in range(h) for x in range(w))
    if share is None:
        share = min(0.45, max(0.2, 1.5 * have / land))
    need = int(share * land) - have
    if need <= 0 or not cand:
        return ["".join(r) for r in g]
    # smooth value noise on a coarse lattice: patches, not salt and pepper
    step = 6
    lat = {(i, j): rng.random() for i in range(w // step + 2) for j in range(h // step + 2)}

    def noise(x, y):
        i, j, fx, fy = x // step, y // step, (x % step) / step, (y % step) / step
        a = lat[(i, j)] * (1 - fx) + lat[(i + 1, j)] * fx
        b = lat[(i, j + 1)] * (1 - fx) + lat[(i + 1, j + 1)] * fx
        return a * (1 - fy) + b * fy
    cand.sort(key=lambda c: -noise(*c))
    for x, y in cand[:need]:
        g[y][x] = "G"
    return ["".join(r) for r in g]


def prune_thin(grid, keep=frozenset()):
    """Tall grass and marsh only where they are at least 3 wide: a 1-2 tile sliver draws as a hollow pill of
    border tiles with no blades (tall grass) or a pale stripe (marsh), so slivers go back to plain grass."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    for ch in ('G', '"'):
        inside = set()
        for y in range(h - 2):
            for x in range(w - 2):
                if all(g[y + j][x + i] == ch for i in range(3) for j in range(3)):
                    inside.update((x + i, y + j) for i in range(3) for j in range(3))
        for y in range(h):
            for x in range(w):
                if g[y][x] == ch and (x, y) not in inside and (x, y) not in keep:
                    g[y][x] = "."
    return ["".join(r) for r in g]


def yards_to_grass(grid):
    """Big paved yards and plazas in a town or on a route (a fenced substation yard, a mill yard) read as one
    bare slab: they become grass, and the door paths carved later cross them. Roads (up to 4 wide) stay."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    is_p = lambda x, y: 0 <= x < w and 0 <= y < h and g[y][x] in ":="
    core = {(x, y) for y in range(h) for x in range(w)
            if all(is_p(x + dx, y + dy) for dx in range(-2, 3) for dy in range(-2, 3))}
    for x, y in core:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if is_p(x + dx, y + dy):
                    g[y + dy][x + dx] = "."
    return ["".join(r) for r in g]


def furnish(key, grid, cfg, occ, kind, docks_, buildings=()):
    """Street life: benches facing the streets, lamps spaced along the main roads (not overdone), crates,
    barrels and crab traps on the waterfront of fishing towns, magnolias in the yards. Only pieces the
    town's tileset has are used; nothing stands on a road, in water or across a doorway."""
    import random
    rng = random.Random(key + "props")
    pf = cfg["prefabs"]
    h, w = len(grid), len(grid[0])
    road = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] in ":="
    # props stand on plain grass with plain ground (or road) all round: on marsh or a shore they'd each need
    # their own composite tiles, which the tile budget can't spare
    ground = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] == "." and (x, y) not in occ
    plain = lambda x, y: not (0 <= x < w and 0 <= y < h) or grid[y][x] in ".:="
    out = []

    def clear(x, y, pw, ph, ring=1):
        return all(ground(i, j) for i in range(x, x + pw) for j in range(y, y + ph)) and not any(
            (i, j) in occ or not plain(i, j) for i in range(x - ring, x + pw + ring) for j in range(y - ring, y + ph + ring))

    def put(prefab, x, y, label):
        rows = pf[prefab]["rows"]
        occupy(occ, x, y, len(rows[0]), len(rows))
        out.append({"prefab": prefab, "x": x, "y": y, "label": label})

    cells = [(x, y) for y in range(h) for x in range(w)]
    rng.shuffle(cells)
    roads = sum(road(x, y) for x, y in cells)
    city = kind == "city"
    # benches: on the grass just north of a street, facing it, near the doors people come and go from first
    doors = [(dx, dy + 1) for b in buildings if not b.get("closed") for dx, dy in door_cells(cfg, b)]
    near_door = lambda x, y: min((abs(x - a) + abs(y - b) for a, b in doors), default=99)
    if "bench" in pf:
        want = max(3, roads // (45 if city else 70))
        for x, y in sorted(cells, key=lambda c: (not 2 <= near_door(*c) <= 7, near_door(*c))):
            if want <= 0:
                break
            if road(x, y + 1) and road(x + 1, y + 1) and not road(x, y - 1) and clear(x, y, 2, 1) and \
                    not any(b["label"] == "Bench" and abs(b["x"] - x) + abs(b["y"] - y) < 8 for b in out):
                put("bench", x, y, "Bench")
                want -= 1
    # lamps: beside the busiest roads, well spaced
    if "lamp" in pf:
        want = max(1, roads // (70 if city else 150))
        for x, y in cells:
            if want <= 0:
                break
            if road(x, y + 2) and clear(x, y, 1, 2) and \
                    not any(b["label"] == "Lamp" and abs(b["x"] - x) + abs(b["y"] - y) < 10 for b in out):
                put("lamp", x, y, "Lamp")
                want -= 1
    # waterfront clutter by the docks: a little cluster of crates, barrels and traps
    clutter = [p for p in ("crates", "barrel", "trap") if p in pf]
    if clutter and docks_:
        for d in docks_[:6]:
            spots = [(d["x"] + i, d["y"] + j) for i in range(-3, len(d["rows"][0]) + 3)
                     for j in range(-3, len(d["rows"]) + 3)]
            rng.shuffle(spots)
            placed = 0
            for x, y in spots:
                if placed >= 2:
                    break
                if ground(x, y) and not road(x, y) and not any((i, j) in occ for i in (x - 1, x + 1) for j in (y,)) and \
                        all(plain(x + dx, y + dy) or (x + dx, y + dy) in occ for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and \
                        any(road(x + dx, y + dy) or (x + dx, y + dy) in occ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    put(rng.choice(clutter), x, y, "Prop")
                    placed += 1
    # magnolias in yards: by the houses, clear of doors and paths
    if "magnolia" in pf:
        want = 5 if not city else 8
        for x, y in cells:
            if want <= 0:
                break
            if clear(x, y, 2, 3) and any(road(i, y + 3) or road(i, y + 4) for i in range(x - 1, x + 3)):
                put("magnolia", x, y, "Tree")
                want -= 1
    return out


def tidy_paths(grid, blocked=frozenset()):
    """Paths the autotile can draw: diagonal-only steps (mockup roads drawn at an angle) become 4-connected
    stairs, and every path cell gets a full 2x2 block of path around it (no 1-wide runs or notches)."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    is_p = lambda x, y: 0 <= x < w and 0 <= y < h and g[y][x] in ":="
    free = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in blocked and g[y][x] not in "~I#"
    for y in range(h - 1):
        for x in range(w - 1):
            a, b, c, d = is_p(x, y), is_p(x + 1, y), is_p(x, y + 1), is_p(x + 1, y + 1)
            if a and d and not b and not c or b and c and not a and not d:
                ch = g[y][x] if a else g[y][x + 1]
                for i, j in ((x + 1, y), (x, y + 1)) if a else ((x, y), (x + 1, y + 1)):
                    if free(i, j):
                        g[j][i] = ch
                        break
    for _ in range(2):
        for y in range(h):
            for x in range(w):
                if not is_p(x, y):
                    continue
                blocks = [[(x + i, y + j) for i in (ox, ox + 1) for j in (oy, oy + 1)] for ox in (-1, 0) for oy in (-1, 0)]
                if any(all(is_p(i, j) for i, j in bl) for bl in blocks):
                    continue
                ok = [bl for bl in blocks if all(is_p(i, j) or free(i, j) for i, j in bl)]
                if ok:
                    bl = min(ok, key=lambda bl: sum(not is_p(i, j) for i, j in bl))
                    for i, j in bl:
                        g[j][i] = g[y][x] if not is_p(i, j) else g[j][i]
    return ["".join(r) for r in g]


def islets(grid, occ, smallest=6):
    """Specks of land left in open water by the mockup (a trawler's outline, a pier stub) go back to water."""
    g = [list(r) for r in grid]
    for cells in components(g, '."LG'):
        if len(cells) < smallest and not any(c in occ for c in cells):
            for x, y in cells:
                g[y][x] = "~"
    return ["".join(r) for r in g]


def banks(grid, keep=frozenset()):
    """Water, marsh or mud touching a road or street becomes plain grass (the path autotile only has grass
    edges, and the user wants a strip of plain grass beside roads), as does marsh touching mud."""
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])

    def verge(chars, near):
        hits = []
        for y in range(h):
            for x in range(w):
                if g[y][x] in chars:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            i, j = x + dx, y + dy
                            if 0 <= i < w and 0 <= j < h and g[j][i] in near and (i, j) not in keep:
                                hits.append((i, j))
        for i, j in hits:
            g[j][i] = "."
    g = [list(r) for r in levee_roads(["".join(r) for r in g])]
    verge(":=", "~I\"LG")
    verge("L", '"')
    return ["".join(r) for r in g]


def door_cells(cfg, b):
    d = cfg["prefabs"][b["prefab"]].get("door")
    if not d:
        return []
    ds = d if isinstance(d[0], list) else [d]
    return [(b["x"] + dx, b["y"] + dy) for dx, dy in ds]


def plant_trees(trees, grid, cfg, occ, dry=False):
    """Mockup trees are round blobs of any size: one tree per small blob, a staggered grid of trees across
    woods. A tree goes where at least a third of its footprint is tree cells and the ground under it is open."""
    out, grove = [], set()
    h, w = len(grid), len(grid[0])
    tg = [["T" if (x, y) in trees else "." for x in range(w)] for y in range(h)]
    names = ("field_tree_l", "field_tree") if dry else ("cypress", "cypress_small", "cypress_marsh", "cypress_small_marsh")
    sizes = {p: (len(cfg["prefabs"][p]["rows"]), len(cfg["prefabs"][p]["rows"][0]))
             for p in names if p in cfg["prefabs"]}
    for cells in components(tg, "T"):
        cs = set(cells)
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        base = ("field_tree_l" if dry else "cypress") if len(cells) >= 6 else ("field_tree" if dry else "cypress_small")
        if base not in sizes:
            continue
        ph, pw = sizes[base]
        woods = len(cells) >= 20
        spots = [((min(xs) + max(xs) + 1 - pw) // 2, (min(ys) + max(ys) + 1 - ph) // 2)] if not woods else [
            (x + (pw // 2 if (y // ph) % 2 else 0), y) for y in range(min(ys), max(ys) - ph + 2, ph)
            for x in range(min(xs), max(xs) - pw + 2, pw + 1)]
        for x, y in spots:
            foot = [(i, j) for i in range(x, x + pw) for j in range(y, y + ph)]
            if not fits(occ, x, y, pw, ph, w, h):
                continue
            if woods and sum(c in cs for c in foot) * 3 < len(foot):
                continue
            if dry:  # a field tree stands on open dry ground (cane under it goes back to ground), no grove
                ring = [(i, j) for i in range(x - 1, x + pw + 1) for j in range(y - 1, y + ph + 1)
                        if 0 <= i < w and 0 <= j < h and (i, j) not in foot]
                if any(grid[j][i] not in '.G' for i, j in foot) or any(grid[j][i] in ":=%&~I#" for i, j in ring):
                    continue
                for i, j in foot:
                    grid[j][i] = "."
                occupy(occ, x, y, pw, ph)
                out.append({"prefab": base, "x": x, "y": y, "label": "Tree"})
                continue
            # every tree stands in its own grove: marsh under it and a tile of marsh all round (the user's
            # rule; the plain cypress shows a pale square on grass), so the ground must be open land
            ground = {grid[j][i] for i, j in foot if (i, j) not in cs} or {"."}
            prefab = base + "_marsh" if ground <= set('."G') and base + "_marsh" in sizes else None
            ring = [(i, j) for i in range(x - 1, x + pw + 1) for j in range(y - 1, y + ph + 1)
                    if 0 <= i < w and 0 <= j < h and (i, j) not in foot]
            if prefab and any(grid[j][i] not in '."G' or ((i, j) in occ and (i, j) not in grove) for i, j in ring):
                prefab = None  # no water, path or building in the grove
            if prefab and any(grid[j][i] == "L" for i in range(max(0, x - 2), min(w, x + pw + 2))
                              for j in range(max(0, y - 2), min(h, y + ph + 2))):
                prefab = None  # marsh never meets mud
            if prefab:
                occupy(occ, x, y, pw, ph)
                out.append({"prefab": prefab, "x": x, "y": y, "label": "Tree"})
                core = []
                for i in range(x - 1, x + pw + 1):
                    for j in range(y - 1, y + ph + 1):
                        if 0 <= i < w and 0 <= j < h and ((i, j) in foot or grid[j][i] in '."G'):
                            grid[j][i] = '"'
                            grove.add((i, j))
                            core.append((i, j))
                # an irregular rim, so a tree's grove isn't a stamped rounded square (neighbours merge)
                ok = lambda i, j: (0 <= i < w and 0 <= j < h and grid[j][i] in '."G' and (i, j) not in occ
                                   and not any(0 <= i + a < w and 0 <= j + c < h and grid[j + c][i + a] in ":=L~I#"
                                               for a in (-1, 0, 1) for c in (-1, 0, 1)))
                for i, j in organic_rim(core, ok, f"{x},{y}", reach=1):
                    grid[j][i] = '"'
                    grove.add((i, j))
    return out


def place_boats(boats, grid, cfg, occ, kind="trawler"):
    """Working boats moored where the mockup draws them (trawlers; the camp's airboat): own art over water."""
    out = []
    if kind not in cfg["prefabs"]:
        return out
    rows = cfg["prefabs"][kind]["rows"]
    ph, pw = len(rows), len(rows[0])
    h, w = len(grid), len(grid[0])
    for x, y in boats:
        if fits(occ, x, y, pw, ph, w, h) and all(grid[j][i] == "~" for i in range(x, x + pw) for j in range(y, y + ph)):
            occupy(occ, x, y, pw, ph)
            out.append({"prefab": kind, "x": x, "y": y, "label": "Boat"})
    return out


ITEM_FLAGS = os.path.join(HERE, "item_flags.json")


def item_flag(const, n):
    """A stable, unique flag for a first-pass item ball: taken from the unused vanilla flags at 0x270 and up
    (the story's own flags live low, from 0x27) and remembered in item_flags.json so reruns keep them."""
    import re
    reg = json.load(open(ITEM_FLAGS)) if os.path.exists(ITEM_FLAGS) else {}
    key = f"{const}:{n}"
    if key not in reg:
        free = [f for f in re.findall(r"#define (FLAG_UNUSED_0x([0-9A-F]+))\s", open("include/constants/flags.h").read())
                if int(f[1], 16) >= 0x270]
        used = set(reg.values())
        reg[key] = next(f for f, _ in free if f not in used)
        dump(ITEM_FLAGS, reg)
    return reg[key]


def objects(markers, grid, occ, const):
    """Mockup markers -> placeholder people, swimmers and item balls, each nudged to the nearest tile it can
    really stand on. Returns (objects, items, surf-only cells). Mega Stones and hidden items are left to the
    story pass (they need scripts and hidden-item flags)."""
    out, items, surf = [], [], []
    h, w = len(grid), len(grid[0])
    stem = const[len("MAP_"):]

    def shore(x, y):
        return any(grid[j][i] in "~I" for i in range(max(0, x - 1), min(w, x + 2)) for j in range(max(0, y - 1), min(h, y + 2)))

    def land_ok(x, y):  # dry, open and not a shore tile (those are drawn as water)
        return 0 <= x < w and 0 <= y < h and grid[y][x] in '.:="LG' and (x, y) not in occ and not shore(x, y)

    def water_ok(x, y):  # open water, a tile clear of any shore
        return 0 <= x < w and 0 <= y < h and (x, y) not in occ and all(
            0 <= i < w and 0 <= j < h and grid[j][i] == "~" for i in range(x - 1, x + 2) for j in range(y - 1, y + 2))

    def nearest(x, y, ok, reach=3):
        cells = sorted(((abs(dx) + abs(dy), x + dx, y + dy) for dx in range(-reach, reach + 1)
                        for dy in range(-reach, reach + 1)))
        return next(((cx, cy) for _, cx, cy in cells if ok(cx, cy)), None)

    for n, m in enumerate(markers):
        x, y = m["x"], m["y"]
        if m["kind"] in ("npc", "trainer"):
            trainer = m["kind"] == "trainer"
            at = nearest(x, y, land_ok)
            swim = False
            if not at and trainer:
                at, swim = nearest(x, y, water_ok), True
            if not at:
                continue
            o = {"id": f"LOCALID_{stem}_{'TRAINER' if trainer else 'NPC'}_{n}",
                 "gfx": "OBJ_EVENT_GFX_SWIMMER_M" if swim else "OBJ_EVENT_GFX_YOUNGSTER" if trainer else "OBJ_EVENT_GFX_MAN_1",
                 "x": at[0], "y": at[1], "move": "MOVEMENT_TYPE_FACE_DOWN",
                 "text": "(Trainer: first-pass placeholder.)" if trainer else "(First-pass placeholder.)"}
            if swim:
                o["elevation"] = 1
                surf.append(list(at))
            out.append(o)
            occ.add(at)
        elif m["kind"] == "item":
            at = nearest(x, y, land_ok)
            if at:
                items.append({"x": at[0], "y": at[1], "item": "ITEM_POTION", "flag": item_flag(const, n),
                              "_comment": "first-pass placeholder item"})
                occ.add(at)
    return out, items, surf


# ---------------------------------------------------------------- map shell
def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def shell(name, const, kind, mapsec, music, w, h, cfg):
    lid = "LAYOUT_" + const[len("MAP_"):]
    ldir = f"data/layouts/{name}"
    os.makedirs(ldir, exist_ok=True)
    L = json.load(open("data/layouts/layouts.json", encoding="utf-8"))
    if not any(l.get("id") == lid for l in L["layouts"]):
        L["layouts"].append({"id": lid, "name": f"{name}_Layout", "width": w, "height": h,
                             "primary_tileset": cfg["primary"], "secondary_tileset": cfg["secondary"],
                             "border_filepath": f"{ldir}/border.bin", "blockdata_filepath": f"{ldir}/map.bin"})
        dump("data/layouts/layouts.json", L)
    G = json.load(open("data/maps/map_groups.json", encoding="utf-8"))
    grp = "gMapGroup_Routes" if kind == "route" else "gMapGroup_Towns"
    if name not in G[grp]:
        G[grp].append(name)
        dump("data/maps/map_groups.json", G)
    if mapsec in SECTION_NAMES:
        R = json.load(open("src/data/region_map/region_map_sections.json", encoding="utf-8"))
        if not any(s["id"] == mapsec for s in R["map_sections"]):
            R["map_sections"].append({"id": mapsec, "name": SECTION_NAMES[mapsec]})
            dump("src/data/region_map/region_map_sections.json", R)
    md = f"data/maps/{name}"
    os.makedirs(md, exist_ok=True)
    if not os.path.exists(f"{md}/map.json"):
        dump(f"{md}/map.json", {
            "id": const, "name": name, "layout": lid, "music": music, "region_map_section": mapsec,
            "requires_flash": False, "weather": "WEATHER_NONE",
            "map_type": {"route": "MAP_TYPE_ROUTE", "town": "MAP_TYPE_TOWN", "city": "MAP_TYPE_CITY"}[kind],
            "allow_cycling": True, "allow_escaping": False, "allow_running": True, "show_map_name": True,
            "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None,
            "object_events": [], "warp_events": [], "coord_events": [], "bg_events": []})
    if not os.path.exists(f"{md}/scripts.inc"):
        with open(f"{md}/scripts.inc", "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{name}_MapScripts::\n\t.byte 0\n")
    return lid, ldir


# ---------------------------------------------------------------- one map
# ---------------------------------------------------------------- the dry country
GREEN_PROPS = ("lamp", "bench", "magnolia", "sign_g")  # props drawn on grass: they stand in the green meadow


def dry_finish(key, grid, occ, cfg, green, rocks, reserved, buildings, masks):
    """Turns a dry route's first-pass ground ('.', and the mudflat 'L') into the dry-country terrain:
      d  dry ground (the base; dry grass 'g' is left unused: its straw tile seams against dry ground and the road by
         25-26, art_requests/dry_country_salt.md), q pepper rows (route_features "beds"), s / z salt crust and its
         salt-dusted ground (Route 24, the dome's end)
      .  green meadow stays where the mockup draws short grass, and where the route meets a green map: the ground fades
         from meadow to dry over DRY_FADE[key] cells in soft patches (the dry-on-grass autotile draws the edges)
    Rules the dry autotile sets: a road cell on dry ground has only sand edges, so every road cell gets a ring of dry
    ground; the city approach's paving and its break-up ('%', '&') keep their green ring; cane, pepper, salt and dry
    grass tiles carry no border of their own, so they keep a cell of dry ground between them and the meadow.
    Returns (grid, extra buildings: rocks, coal heaps)."""
    import random
    rng = random.Random(key + "dry")
    g = [list(r) for r in grid]
    h, w = len(g), len(g[0])
    pf = cfg["prefabs"]
    out = []
    feat = route_features.FEATURES.get(key, {})

    def vnoise(seed, step):
        r2 = random.Random(key + seed)
        lat = {(i, j): r2.random() for i in range(w // step + 2) for j in range(h // step + 2)}

        def f(x, y):
            i, j, fx, fy = x // step, y // step, (x % step) / step, (y % step) / step
            fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
            a = lat[(i, j)] * (1 - fx) + lat[(i + 1, j)] * fx
            b = lat[(i, j + 1)] * (1 - fx) + lat[(i + 1, j + 1)] * fx
            return a * (1 - fy) + b * fy
        return f
    cheb = lambda x, y, cells, r: any((x + i, y + j) in cells for i in range(-r, r + 1) for j in range(-r, r + 1))
    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    for x0, y0, rw, rh, ch in EDGE_PAINT.get(key, []):   # a road row trimmed or added at the edge (the world seams)
        for y in range(y0, min(h, y0 + rh)):
            for x in range(x0, min(w, x0 + rw)):
                g[y][x] = ch
    road = {(x, y) for y in range(h) for x in range(w) if g[y][x] in ":=&"}
    apr = {(x, y) for y in range(h) for x in range(w) if g[y][x] == "%"}
    # a road cell with all four sides road and two or more open diagonals can draw only one inner corner: the odd
    # diagonal cell is filled in (a one-cell step in the road's edge), which keeps the edge pieces matching
    for _ in range(4):
        grew = False
        for x, y in sorted(road):
            if not all((x + dx, y + dy) in road | apr for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            open_ = [(x + dx, y + dy) for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1))
                     if inside(x + dx, y + dy) and (x + dx, y + dy) not in road | apr]
            if len(open_) >= 2:
                for cx, cy in open_:
                    if g[cy][cx] == "." and (cx, cy) not in occ and 0 < cx < w - 1 and 0 < cy < h - 1:
                        g[cy][cx] = ":"
                        road.add((cx, cy))
                        grew = True
                        break
        if not grew:
            break
    # the approach's side stubs (a road cell or two just beside the paved band, going nowhere) are dropped
    if apr:
        dm = max(x for x, _ in apr)
        for comp in components([["P" if (x, y) in apr else "." for x in range(w)] for y in range(h)], "P"):
            ys = [c[1] for c in comp]
            y0, y1 = min(ys), max(ys)
            for y, away in ((y0 - 1, -1), (y1 + 1, 1)):
                for x in range(0, dm + 2):
                    if inside(x, y) and g[y][x] in ":&" and not (inside(x, y + away) and g[y + away][x] in ":=&%"):
                        g[y][x] = "."
                        road.discard((x, y))
    # the mudflat (route 17's coal heaps): dry ground with a few stones
    for cells in components(g, "L"):
        cs = set(cells)
        for x, y in cells:
            g[y][x] = "."
        for x, y in sorted(cells, key=lambda c: (c[1], c[0])):
            if "rock_l" in pf and all((x + i, y + j) in cs for i in range(-1, 3) for j in range(-1, 3)) and \
                    all((x + i, y + j) not in occ for i in range(2) for j in range(2)) and rng.random() < 0.3:
                occupy(occ, x, y, 2, 2)
                out.append({"prefab": "rock_l", "x": x, "y": y, "label": "Coal heap"})
    # ---- the meadow
    lawn = set(green)
    edge_lawn = set()   # the two columns along a green neighbour's edge: meadow whatever the mockup draws there
    for side, F in DRY_FADE.get(key, {}).items():
        n1, n2 = vnoise("fade", 4), vnoise("fade2", 2)
        zone = set()
        for y in range(h):
            for x in range(w):
                d = {"W": x, "E": w - 1 - x, "N": y, "S": h - 1 - y}[side]
                if d >= F:
                    continue
                zone.add((x, y))
                v = 0.5 + (0.7 * n1(x, y) + 0.3 * n2(x, y) - 0.5) * 2.0
                if d <= 1 or v >= min(1.0, max(0.0, (d - 1) / (F - 2))):   # the two edge columns are always meadow: a green neighbour's lawn runs right up to the border
                    lawn.add((x, y))
        for _ in range(3):  # soft patches, not specks
            nxt = set(lawn)
            for x, y in zone:
                n = sum((x + i, y + j) in lawn for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0))
                if n >= 6:
                    nxt.add((x, y))
                elif n <= 2:
                    nxt.discard((x, y))
            lawn = nxt
        for _ in range(4):  # the dry autotile can't draw a one-cell finger or notch: cells pinched between two opposite neighbours flip
            nxt = set(lawn)
            for x, y in zone:
                v = (x, y) in lawn
                for a, b in (((x - 1, y), (x + 1, y)), ((x, y - 1), (x, y + 1))):
                    if all(0 <= c[0] < w and 0 <= c[1] < h for c in (a, b)) and ((a in lawn) != v) and ((b in lawn) != v):
                        (nxt.discard if v else nxt.add)((x, y))
            lawn = nxt
    for side, F in DRY_FADE.get(key, {}).items():  # (the smoothing must not eat the two edge columns)
        for y in range(h):
            for x in range(w):
                if {"W": x, "E": w - 1 - x, "N": y, "S": h - 1 - y}[side] <= 1:
                    lawn.add((x, y))
                    edge_lawn.add((x, y))
    # a speck of meadow (a stray key-colour match) isn't a meadow
    lawn_cells = [["G" if (x, y) in lawn else "." for x in range(w)] for y in range(h)]
    for cells in components(lawn_cells, "G"):
        if len(cells) < 8:
            lawn -= set(cells)
    # props drawn on grass (the approach's lamps, bench, magnolias, signpost) stand in the meadow, with a ring
    for b in buildings:
        if b["prefab"] == "sign" and not cheb(b["x"], b["y"], lawn | apr, 2):
            continue
        if b["prefab"] in GREEN_PROPS or b["prefab"] == "sign":
            rows = b.get("rows") or pf[b["prefab"]]["rows"]
            if b["prefab"] == "sign" and "sign_g" in pf:
                b["prefab"] = "sign_g"
            for j in range(-1, len(rows) + 1):
                for i in range(-1, len(rows[0]) + 1):
                    lawn.add((b["x"] + i, b["y"] + j))
    # a grove in the meadow (Route 23's hollow): its trees stand on grass too
    for b in buildings:
        if b["prefab"] in ("field_tree", "field_tree_l") and cheb(b["x"], b["y"], green, 2):
            rows = pf[b["prefab"]]["rows"]
            for j in range(-1, len(rows) + 1):
                for i in range(-1, len(rows[0]) + 1):
                    lawn.add((b["x"] + i, b["y"] + j))
    # the approach's paving and dirt keep a green ring (as far out as the dirt is the old Johto path on grass)
    depth_max = max((x for x, _ in apr), default=-1)
    for x, y in apr:
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if inside(x + i, y + j) and x + i <= depth_max:
                    lawn.add((x + i, y + j))
    # roads near the approach lie in the meadow: the old Johto path on grass ('p'), green all round
    meadow_road = set()  # (the approach's dirt, '&', is dry-country road: its ring is dry)
    for x, y in meadow_road:
        g[y][x] = "p"
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if inside(x + i, y + j):
                    lawn.add((x + i, y + j))
    # a road on dry ground wants dry ground all round it
    for x, y in road - meadow_road:
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                lawn.discard((x + i, y + j))
    # encounter patches carry no border: none in or touching the meadow
    ENC = "G"
    for y in range(h):
        for x in range(w):
            if g[y][x] == ENC and cheb(x, y, lawn, 1):
                g[y][x] = "."
                if (x, y) not in edge_lawn:
                    lawn.discard((x, y))
    # what a person can't walk through, and what must stay reachable from the roads
    solid = set()
    for b in buildings:
        rows = b.get("rows") or pf[b["prefab"]]["rows"]
        walk = {tuple(c) for c in (b.get("passable") or pf.get(b["prefab"], {}).get("passable") or [])}
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c is not None and (i, j) not in walk:
                    solid.add((b["x"] + i, b["y"] + j))
    solid |= {c for c in out_cells(out, pf)}
    free = lambda x, y: inside(x, y) and g[y][x] == "." and (x, y) not in lawn
    if feat.get("encounter") == "g":
        # tall dry grass patches come out as lobed, irregular blobs (the art's test patch), not the mockup's rectangles: each
        # keeps its centre and about its area; no cell on a road, a prop or beside either (the dry ground round it is the border)
        import math
        wall_ = {(x, y) for y in range(h) for x in range(w) if g[y][x] == "r"}
        band_ = masks.get("gully") or set()
        okcell = lambda x, y: (inside(x, y) and g[y][x] in ".G" and (x, y) not in lawn and (x, y) not in occ
                               and not cheb(x, y, road | apr, 1) and not cheb(x, y, solid, 1)
                               and not cheb(x, y, wall_, 3) and not cheb(x, y, band_, 2))
        for comp in components([["G" if g[y][x] == ENC else "." for x in range(w)] for y in range(h)], "G"):
            n = len(comp)
            if n < 6:
                continue
            xs, ys = [c[0] for c in comp], [c[1] for c in comp]
            cx, cy = sum(xs) / n, sum(ys) / n
            ax = max(2.0, (max(xs) - min(xs) + 1) / 2)
            ay = max(2.0, (max(ys) - min(ys) + 1) / 2)
            if n > 140:   # a merged field: lobes along its long axis instead of one blob
                pass
            r4 = random.Random(f"{key}{int(cx)}{int(cy)}")
            amp = [(r4.uniform(0.10, 0.22), r4.uniform(0, 6.283)) for _ in range(3)]
            feats = [(r4.uniform(0, 6.283), r4.choice((-0.42, -0.35, 0.3, 0.38)), r4.uniform(0.35, 0.6)) for _ in range(2)]

            def radius(th):
                v = 1 + sum(a * math.sin((k + 1) * th + ph) for k, (a, ph) in enumerate(amp))
                for t0, d, wd in feats:  # a notch (d < 0) or a bulge (d > 0)
                    dd = (th - t0 + math.pi) % (2 * math.pi) - math.pi
                    v += d * math.exp(-(dd / wd) ** 2)
                return max(0.45, v)

            def paint(m):
                out_ = set()
                for y in range(int(cy - ay * m * 1.8) - 2, int(cy + ay * m * 1.8) + 3):
                    for x in range(int(cx - ax * m * 1.8) - 2, int(cx + ax * m * 1.8) + 3):
                        dx, dy = (x + 0.0 - cx) / (ax * m), (y + 0.0 - cy) / (ay * m)
                        if math.hypot(dx, dy) <= radius(math.atan2(dy, dx)) and okcell(x, y):
                            out_.add((x, y))
                for _ in range(2):  # no one-cell tags or necks: the majority of the eight neighbours decides
                    nxt = set(out_)
                    for x, y in list(out_):
                        if sum((x + i, y + j) in out_ for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)) <= 2:
                            nxt.discard((x, y))
                    out_ = nxt
                return out_
            lo, hi, best = 0.5, 2.0, None
            for _ in range(14):  # scale until the blob has about the mockup rectangle's area
                m = (lo + hi) / 2
                blob = paint(m)
                best = blob if best is None or abs(len(blob) - n) < abs(len(best) - n) else best
                if len(blob) < n:
                    lo = m
                else:
                    hi = m
            for x, y in comp:
                g[y][x] = "."
            for x, y in best or ():
                g[y][x] = ENC
            if os.environ.get("DRYDEBUG"):
                print(f"    patch at {int(cx)},{int(cy)}: mockup {n} cells, blob {len(best or ())}")
    enc_cells = {(x, y) for y in range(h) for x in range(w) if g[y][x] == ENC}
    near_occ = lambda x, y, r: cheb(x, y, occ, r)

    def carve(blocking):
        """Opens a 2-wide lane from every target the roads can't reach (an encounter patch, an item, a trainer) to
        the nearest reachable cell, through whatever `blocking` (cells of the cane wall or the pepper beds) is in the way."""
        targets = {tuple(c) for c in reserved}
        for comp in components([["G" if (x, y) in enc_cells else "." for x in range(w)] for y in range(h)], "G"):
            targets.add(comp[0])
        for _ in range(60):
            reach = deque(c for c in road | meadow_road if inside(*c))
            seen = set(reach)
            while reach:
                x, y = reach.popleft()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if inside(nx, ny) and (nx, ny) not in seen and g[ny][nx] not in blocking and (nx, ny) not in solid:
                        seen.add((nx, ny))
                        reach.append((nx, ny))
            lost = [t for t in sorted(targets) if t not in seen]
            if not lost:
                return
            t = lost[0]  # shortest way out through the blocking cells
            prev, q, hit = {t: None}, deque([t]), None
            while q and hit is None:
                x, y = q.popleft()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if inside(nx, ny) and (nx, ny) not in prev and (nx, ny) not in solid:
                        prev[(nx, ny)] = (x, y)
                        if (nx, ny) in seen:
                            hit = (nx, ny)
                            break
                        q.append((nx, ny))
            if hit is None:
                targets.discard(t)
                continue
            c = hit
            while c is not None:
                for i, j in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)):
                    if inside(c[0] + i, c[1] + j) and g[c[1] + j][c[0] + i] in blocking:
                        g[c[1] + j][c[0] + i] = "."
                c = prev[c]
    # ---- the cane wall (Route 15, the cane fields): everything off the roads is blocking cane, with a dry verge
    # along the roads, clearings round the walk-in patches and the people, and open ground where the roads leave
    if feat.get("walls"):
        n1 = vnoise("verge", 3)
        keep = set()
        for x, y in road | meadow_road:
            r = 1 + (1 if n1(x, y) > 0.62 else 0)
            keep |= {(x + i, y + j) for i in range(-r, r + 1) for j in range(-r, r + 1)}
            if min(x, y, w - 1 - x, h - 1 - y) == 0:  # a road leaving the map: open ground out to the edge
                keep |= {(x + i, y + j) for i in range(-3, 4) for j in range(-3, 4)}
        for x, y in enc_cells:
            keep |= {(x + i, y + j) for i in range(-1, 2) for j in range(-1, 2)}
        for x, y in occ | {tuple(c) for c in reserved}:
            keep |= {(x + i, y + j) for i in range(-1, 2) for j in range(-1, 2)}
        wall = {(x, y) for y in range(h) for x in range(w) if free(x, y) and (x, y) not in keep}
        for _ in range(2):  # soft outlines: the majority of the eight neighbours decides (off the map counts as cane)
            nxt = set(wall)
            for y in range(h):
                for x in range(w):
                    if not free(x, y) or (x, y) in keep:
                        continue
                    n = sum(((x + i, y + j) in wall or not inside(x + i, y + j)) for i in (-1, 0, 1) for j in (-1, 0, 1)
                            if (i, j) != (0, 0))
                    if n >= 5:
                        nxt.add((x, y))
                    elif n <= 2:
                        nxt.discard((x, y))
            wall = nxt
        lawn_cells = [["G" if (x, y) in wall else "." for x in range(w)] for y in range(h)]
        for cells in components(lawn_cells, "G"):
            if len(cells) < 9:
                wall -= set(cells)
        for x, y in wall:
            g[y][x] = "w"
        carve("w")
    # ---- gullies (Route 23's dry washes): 2 wide along the mockup's riverbed band, broken where a road crosses
    if masks.get("gully"):
        band = masks["gully"]
        for y in range(h):
            for x in range(w):
                if g[y][x] == ENC and cheb(x, y, band, 2):  # encounter patches keep off the wash
                    g[y][x] = "."
        enc_cells -= {(x, y) for x, y in enc_cells if g[y][x] != ENC}
        cols = {}
        for x, y in band:
            cols.setdefault(x, []).append(y)
        xs = sorted(cols)
        if xs:
            cen = {x: sum(cols[x]) / len(cols[x]) for x in xs}
            for x in range(xs[0], xs[-1] + 1):  # columns the band lacks take their neighbours' line
                if x not in cen:
                    lo = max((a for a in xs if a < x), default=None)
                    hi = min((a for a in xs if a > x), default=None)
                    cen[x] = cen[lo if lo is not None else hi] if lo is None or hi is None else \
                        cen[lo] + (cen[hi] - cen[lo]) * (x - lo) / (hi - lo)
            sm = {x: sum(cen[i] for i in range(x - 3, x + 4) if i in cen) / sum(i in cen for i in range(x - 3, x + 4))
                  for x in cen}
            prev_top = None
            for x in sorted(sm):
                top = int(round(sm[x])) - 1
                rows = {top, top + 1}
                if prev_top is not None:  # no diagonal-only joins: fill the rows between two columns
                    rows |= set(range(min(prev_top, top), max(prev_top, top) + 2))
                prev_top = top
                for y in rows:
                    if free(x, y) and not cheb(x, y, road, 1) and not cheb(x, y, occ, 1):
                        g[y][x] = "v"
    # ---- the salt flat (Route 24): the mockup's salt-white ground, edged by the salt set, dry ground round the patches
    if masks.get("salt"):
        m = masks["salt"]
        for _ in range(2):  # fill the hatch's gaps and trim specks
            m = {(x, y) for y in range(h) for x in range(w)
                 if sum((x + i, y + j) in m for i in (-1, 0, 1) for j in (-1, 0, 1)) >= 5}
        for x, y in m:
            if free(x, y) and not cheb(x, y, enc_cells, 2) and not cheb(x, y, occ, 1) and not cheb(x, y, road, 1):
                g[y][x] = "s"
    # ---- pepper rows as blocking backdrop beds (Route 16): random whole beds, 2-wide lanes between them
    if feat.get("beds"):
        r3 = random.Random(key + "beds")
        want = feat["beds"] * sum(free(x, y) for y in range(h) for x in range(w))
        have = 0
        for _ in range(5000):
            if have >= want:
                break
            bw, bh = r3.randint(5, 16), r3.randint(3, 5)
            bx, by = r3.randint(0, w - bw), r3.randint(0, h - bh)
            cells = [(bx + i, by + j) for i in range(bw) for j in range(bh)]
            ring = [(bx + i, by + j) for i in range(-2, bw + 2) for j in range(-2, bh + 2)]
            if all(free(*c) and c not in occ for c in cells) and not any(
                    inside(*c) and (g[c[1]][c[0]] in ":=%&pGq" or c in occ or c in lawn or c in solid) for c in ring):
                for x, y in cells:
                    g[y][x] = "q"
                have += len(cells)
        carve("q")
    # ---- scattered stones on the dry hills (Route 23's slopes): (prefab, share of the ground)
    for name, per in feat.get("stones", []):
        if name not in pf:
            continue
        rows = pf[name]["rows"]
        ph, pw = len(rows), len(rows[0])
        box = [(i, j) for i in range(-1, pw + 1) for j in range(-1, ph + 1)]
        spots = [(x, y) for y in range(h) for x in range(w)
                 if all(inside(x + i, y + j) and g[y + j][x + i] == "." and (x + i, y + j) not in lawn
                        and (x + i, y + j) not in road and (x + i, y + j) not in occ for i, j in box)]
        rng.shuffle(spots)
        left = int(sum(g[y][x] == "." for y in range(h) for x in range(w)) * per)
        for x, y in spots:
            if left <= 0:
                break
            if any((x + i, y + j) in occ for i, j in box):
                continue
            occupy(occ, x, y, pw, ph)
            out.append({"prefab": name, "x": x, "y": y, "label": "Rock"})
            left -= 1
    # ---- seams with a neighbouring map (town_plans.SEAM_ADOPT): the edge continues the neighbour's terrain
    for spec in SEAM_ADOPT.get(key, []):
        seam_adopt(key, g, spec, occ | solid | {tuple(c) for c in reserved}, road)
    # ---- everything left of the ground is dry (red earth where the mockup is red earth)
    base = feat.get("base", "d")
    for y in range(h):
        for x in range(w):
            if g[y][x] == "." and (x, y) not in lawn:
                g[y][x] = "e" if base == "e" and not cheb(x, y, road | meadow_road, 1) and not cheb(x, y, solid, 1)                     and not cheb(x, y, enc_cells, 1) else "d"
    enc = feat.get("encounter", "G")
    if enc != "G":
        for y in range(h):
            for x in range(w):
                if g[y][x] == "G":
                    g[y][x] = enc
    # the sets (cane wall, red earth, gully, salt) carry their own borders and need dry ground (a 'd' cell) between
    # them and anything else (a road, an encounter patch, the meadow, a prop's tiles): such cells go back to dry ground
    # nothing but dry ground within 3 cells of a rock wall: its south face needs the extension row and a plain row below it
    walls = {(x, y) for y in range(h) for x in range(w) if g[y][x] == "r"}
    if walls:
        for y in range(h):
            for x in range(w):
                if g[y][x] in "gGsvewqQ" and cheb(x, y, walls, 3):
                    g[y][x] = "d"
    allowed = {"w": "wd", "s": "sd", "v": "vd", "g": "gd", "e": "eqQd", "q": "eqQd", "Q": "eqQd", "r": "rd"}
    for _ in range(8):
        bad = []
        for y in range(h):
            for x in range(w):
                c = g[y][x]
                if c not in allowed:
                    continue
                for i in (-1, 0, 1):
                    for j in (-1, 0, 1):
                        if inside(x + i, y + j) and g[y + j][x + i] not in allowed[c]:
                            bad.append((x, y))
                            break
                    else:
                        continue
                    break
        if not bad:
            break
        for x, y in bad:
            g[y][x] = "d"
    for cells in components(g, "q"):  # a stub of pepper bed (a bed the seam strips or rings cut) isn't a bed
        if len(cells) < 8:
            for x, y in cells:
                g[y][x] = "d"
    return ["".join(r) for r in g], out


def seam_adopt(key, g, spec, blocked, road):
    """A dry route's edge continues what its neighbour has at the border (the world seams, phase 2): along the edge, a field
    character of the neighbour's edge row (cane G, pepper q, cane wall w, red earth e) is painted this many cells deep into this
    map (one depth per run of the same character; red earth varies row by row), ground that is plain dry ('d', a gully or salt
    flat's dry fringe) clears the sets from the last few cells, and the painted field gets a ring of dry ground against whatever
    else is next to it.  spec: side (this map's edge), from (neighbour key), dy (neighbour row/column = this map's + dy),
    depth (min, max) of the fields, clear (min, max) of the plain-ground strip, nside (neighbour's edge, default opposite).
    Sets (g) in place."""
    import random
    h, w = len(g), len(g[0])
    side = spec["side"]
    nside = spec.get("nside", {"E": "W", "W": "E", "N": "S", "S": "N"}[side])
    ng = [l.rstrip() for l in open(os.path.join(MAPS_DIR, spec["from"] + ".grid.txt"), encoding="utf-8")]
    nh, nw = len(ng), len(ng[0])
    dy = spec["dy"]
    rng = random.Random(key + side + spec["from"])
    horiz = side in "EW"
    n_t = h if horiz else w
    edge = lambda c: {"W": (lambda t: ng[t][0]), "E": (lambda t: ng[t][nw - 1]), "N": (lambda t: ng[0][t]),
                      "S": (lambda t: ng[nh - 1][t])}[nside](c)
    nlen = nh if nside in "WE" else nw
    cell = lambda t, d: ((w - 1 - d if side == "E" else d), t) if horiz else (t, (h - 1 - d if side == "S" else d))
    prof = {}
    for t in range(n_t):
        u = t + dy
        if 0 <= u < nlen:
            c = edge(u)
            prof[t] = {"Q": "q", "g": "d", "v": "d"}.get(c, c)
    d0, d1 = spec.get("depth", (5, 9))
    c0, c1 = spec.get("clear", (3, 5))
    lat = {i: rng.random() for i in range(n_t // 3 + 2)}
    smooth = lambda t: lat[t // 3] * (1 - (t % 3) / 3) + lat[t // 3 + 1] * ((t % 3) / 3)
    depth, run = {}, None
    for t in range(n_t):
        c = prof.get(t)
        if c in ("G", "q", "w", "s"):
            if run is None or run[0] != c or run[1] != t - 1:
                run = [c, t, rng.randint(d0, d1)]
            run[1] = t
            depth[t] = run[2]
        elif c == "e":
            depth[t] = int(round(c0 + 1 + smooth(t) * (d1 - c0 - 1)))
        elif c == "d":
            depth[t] = int(round(c0 + smooth(t) * (c1 - c0)))
    roadnear = {(x + i, y + j) for y in range(h) for x in range(w) if g[y][x] in ":=%&" for i in (-1, 0, 1) for j in (-1, 0, 1)}
    painted = {}
    for t, c in prof.items():
        if c not in ("G", "q", "w", "e", "d", "s"):
            continue
        for d in range(depth[t]):
            x, y = cell(t, d)
            if (x, y) in blocked or g[y][x] in ":=%&":
                continue
            if c == "d":
                if g[y][x] in ".qwQegsv":
                    if g[y][x] == "q":  # a pepper bed the strip would cut to a stub goes whole
                        comp = {(x, y)}
                        todo = [(x, y)]
                        while todo:
                            cx, cy = todo.pop()
                            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                                if 0 <= nx < w and 0 <= ny < h and g[ny][nx] == "q" and (nx, ny) not in comp:
                                    comp.add((nx, ny))
                                    todo.append((nx, ny))
                        if len(comp) <= 80:
                            for cx, cy in comp:
                                g[cy][cx] = "d"
                    g[y][x] = "d"
            elif g[y][x] in "Gg":  # an encounter patch stays whole
                continue
            elif (x, y) not in roadnear:
                g[y][x] = c
                painted[(x, y)] = c
    ok = {"G": "Gd", "w": "wd", "q": "eqQd", "e": "eqQd", "s": "sd"}
    for _ in range(2):
        for (x, y), c in list(painted.items()):
            if c == "e":
                continue
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    nx, ny = x + i, y + j
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and g[ny][nx] in "GqwQegsvr"                             and g[ny][nx] not in ok[c] and (nx, ny) not in painted:
                        g[ny][nx] = "d"


def edge_clear(key, grid, occ):
    """town_plans.EDGE_CLEAR: marsh and tall grass come off the last cells of a green route's edge where a neighbour has plain
    ground across the border (the world seams, phase 2): [{"side", "span": (a, b) of columns/rows, "depth": (min, max)}]"""
    import random
    h, w = len(grid), len(grid[0])
    g = [list(r) for r in grid]
    for x0, y0, rw, rh, ch in EDGE_PAINT.get(key, []):   # last-word rectangles (a road row trimmed, marsh kept off an edge)
        for y in range(y0, min(h, y0 + rh)):
            for x in range(x0, min(w, x0 + rw)):
                g[y][x] = ch
    specs = EDGE_CLEAR.get(key)
    if not specs:
        return ["".join(r) for r in g]
    rng = random.Random(key + "clear")
    for sp in specs:
        side, (a, b), (d0, d1) = sp["side"], sp["span"], sp["depth"]
        n = w if side in "NS" else h
        lat = {i: rng.random() for i in range(n // 3 + 3)}
        for t in range(max(0, a), min(n, b)):
            f = lat[t // 3] * (1 - (t % 3) / 3) + lat[t // 3 + 1] * ((t % 3) / 3)
            for d in range(int(round(d0 + f * (d1 - d0)))):
                x, y = ((t, d) if side == "N" else (t, h - 1 - d) if side == "S" else (d, t) if side == "W" else (w - 1 - d, t))
                if g[y][x] in '"G' and not any((x + i, y + j) in occ for i in range(-2, 3) for j in range(-2, 3)):
                    g[y][x] = "."
    return ["".join(r) for r in g]


def out_cells(out, pf):
    """Footprint cells of the pieces dry_finish itself placed."""
    for b in out:
        rows = pf[b["prefab"]]["rows"]
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c is not None:
                    yield (b["x"] + i, b["y"] + j)


def face_cells(wallset, w, h):
    """The rock wall's face extension (make_dry_country.face_cells): {cell: key} for the plain cells under every south edge."""
    W = lambda x, y: (max(0, min(x, w - 1)), max(0, min(y, h - 1))) in wallset   # off the map edge the wall carries on
    out = {}
    for y in range(h):
        for x in range(w):
            if (x, y) in wallset or W(x + 1, y) or W(x, y + 1) or W(x + 1, y + 1):
                continue
            n, ne = y > 0 and W(x, y - 1), y > 0 and W(x + 1, y - 1)
            il, ir = W(x - 1, y) or W(x - 1, y + 1), W(x + 2, y) or W(x + 2, y + 1)
            if n and ne:
                out[(x, y)] = "face" + ("_ilr" if il and ir else "_il" if il else "_ir" if ir else "")
            elif n:
                out[(x, y)] = "face_r" + ("_il" if il else "")
            elif ne:
                out[(x, y)] = "face_l" + ("_ir" if ir else "")
    return out


def dry_cliffs(key, rocks, grid, cfg, occ):
    """Rock in a dry route's mockup becomes a rock_wall cliff (the dry set's v3 bedrock wall, character 'r'), laid out for the
    art's rules: the mockup's rock cells (holes filled) quantised to 2x2 blocks so every step is 2 cells or more, no diagonal
    touches along the face, no wall within 2 cells of a road (the south face needs its extension row and one plain row below
    it), none in the meadow where the route fades to green. route_features "rock_wall": {"depth": (2, 4)} caps the wall's depth
    in blocks of 4 columns (Route 23's bluff), {"mouths": [(label, prefab, (x, y))]} sets the tunnel mouths into the face, their
    bottom row on the extension row (the door at the foot), each at the plain stretch nearest (x, y). Returns the buildings: the
    mouths and a few loose rock / rock_l at the foot (scree). Without "rock_wall" a route keeps the old rock scatter."""
    import random
    feat = route_features.FEATURES.get(key, {})
    spec = feat.get("rock_wall")
    pf = cfg["prefabs"]
    rng = random.Random(key + "cliff")
    h, w = len(grid), len(grid[0])
    out = []
    if not spec:
        return out, set()
    mask = {c for c in rocks if grid[c[1]][c[0]] in ".G"}
    # holes: cells shut in by rock (a cave box's floor) are rock too
    out_ = deque(c for c in [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
                 if c not in mask)
    seen = set(out_)
    while out_:
        x, y = out_.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and (nx, ny) not in mask:
                seen.add((nx, ny))
                out_.append((nx, ny))
    holes = {(x, y) for y in range(h) for x in range(w) if (x, y) not in seen and grid[y][x] in ".G=:"}
    mask |= holes
    if holes:  # a cave box's floor (road cells in the grid) is rock now
        g = [list(r) for r in grid]
        for x, y in holes:
            g[y][x] = "."
        grid[:] = ["".join(r) for r in g]
    road = {(x, y) for y in range(h) for x in range(w) if grid[y][x] in ":=%&"}
    if spec.get("depth"):
        d0, d1 = spec["depth"]
        import math
        lat = {i: rng.random() for i in range(w // 4 + 2)}
        mask = {(x, y) for x, y in mask if y < (d1 if lat[x // 4] > 0.5 else d0)}
    for side, F in DRY_FADE.get(key, {}).items():  # none in the meadow
        mask = {(x, y) for x, y in mask if {"W": x, "E": w - 1 - x, "N": y, "S": h - 1 - y}[side] > F}
    for side, F in ROCK_KEEPOFF.get(key, {}).items():  # and none beside a neighbour's edge that has none (the world seams)
        mask = {(x, y) for x, y in mask if {"W": x, "E": w - 1 - x, "N": y, "S": h - 1 - y}[side] > F}
    # 2x2 blocks (3 of 4 cells; an edge block counts its own cells)
    blocks = set()
    for bx in range(0, w, 2):
        for by in range(0, h, 2):
            cells = [(bx + i, by + j) for i in range(2) for j in range(2) if bx + i < w and by + j < h]
            if sum(c in mask for c in cells) * 4 >= len(cells) * 3:
                blocks.add((bx // 2, by // 2))
    cellsof = lambda b: [(b[0] * 2 + i, b[1] * 2 + j) for i in range(2) for j in range(2)]
    near = lambda c, cells, r: any((c[0] + i, c[1] + j) in cells for i in range(-r, r + 1) for j in range(-r, r + 1))
    keep_off = road | occ
    blocks = {b for b in blocks if not any(near(c, road, 2) or near(c, occ, 1) for c in cellsof(b))}
    for _ in range(4):  # no spur one block wide (off the map counts as wall)
        inb = lambda b: (b[0], b[1]) in blocks or not (0 <= b[0] * 2 < w and 0 <= b[1] * 2 < h)
        thin = {b for b in blocks if not (inb((b[0] - 1, b[1])) or inb((b[0] + 1, b[1]))) or
                not (inb((b[0], b[1] - 1)) or inb((b[0], b[1] + 1)))}
        if not thin:
            break
        blocks -= thin
    for _ in range(6):  # no diagonal touches; no wall block that is alone
        bad = set()
        for (i, j) in blocks:
            if (i + 1, j + 1) in blocks and (i + 1, j) not in blocks and (i, j + 1) not in blocks:
                bad.add((i + 1, j + 1))
            if (i - 1, j + 1) in blocks and (i - 1, j) not in blocks and (i, j + 1) not in blocks:
                bad.add((i - 1, j + 1))
        blocks -= bad
        gridb = [["R" if (x, y) in blocks else "." for x in range(w // 2 + 1)] for y in range(h // 2 + 1)]
        for comp in components(gridb, "R"):
            if len(comp) < 3:
                blocks -= set(comp)
        if not bad:
            break
    wall = {c for b in blocks for c in cellsof(b) if c[0] < w and c[1] < h}
    if not wall:
        return out, wall
    g = [list(r) for r in grid]
    for x, y in wall:
        g[y][x] = "r"
    grid[:] = ["".join(r) for r in g]
    for c in list(wall):
        occ.add(c)
    faces = face_cells(wall, w, h)
    for c in faces:
        occ.add(c)
    # the mouths: bottom row on the extension row, three plain face cells wide, wall above, a plain row below
    for label, prefab, (tx, ty) in spec.get("mouths", []):
        rows = pf[prefab]["rows"]
        mh, mw = len(rows), len(rows[0])
        best = None
        for (x, y), k in faces.items():
            if y < mh - 1 or y + 1 >= h or not all(faces.get((x + i, y)) == "face" for i in range(mw)):
                continue
            if not all((x + i, y - j) in wall for i in range(mw) for j in range(1, mh)):
                continue
            if any((x + i, y + 1) in road or (x + i, y + 1) in wall for i in range(mw)):
                continue
            d = abs(x + mw // 2 - tx) + abs(y - ty)
            if best is None or d < best[0]:
                best = (d, x, y)
        if best is None:
            print(f"    cliff: no stretch of plain face for {label} near {tx},{ty}")
            continue
        _, x, y = best
        out.append({"prefab": prefab, "x": x, "y": y - (mh - 1), "label": label, "closed": True})
        for i in range(mw):
            occ.add((x + i, y + 1))
            occ.add((x + i, y + 2))
    # scree at the foot: a few loose stones one or two rows below the extension row, none in front of a door
    stones = [p for p in ("rock", "rock_l") if p in pf]
    cols = sorted({x for (x, y) in faces if faces[(x, y)].startswith("face")})
    for (x, y) in sorted(faces):
        if rng.random() > spec.get("scree", 0.12) or not stones:
            continue
        name = rng.choice(stones)
        rws = pf[name]["rows"]
        pw, ph = len(rws[0]), len(rws)
        sy = y + 2
        if all(0 <= x + i < w and 0 <= sy + j < h and grid[sy + j][x + i] == "." and (x + i, sy + j) not in occ
               and not any((x + i + a, sy + j + b) in road for a in (-2, 3) for b in (-2, 3)) for i in range(pw) for j in range(ph)):
            if not any((x + i + a, sy + j + b) in occ for i in range(pw) for j in range(ph) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                occupy(occ, x, sy, pw, ph)
                out.append({"prefab": name, "x": x, "y": sy, "label": "Rock"})
    return out, wall

def dry_rocks(key, rocks, grid, cfg, occ):
    """Rock and cliff in a dry route's mockup (Route 23's bluff, Route 24's dome face), from the dry set's pieces:
    'mix' scatters rock_l, rock and field trees at random with room round each (no regular rows); 'wall' packs the
    whole region with rock_l and fills what is left with rock (the tileset has no cliff piece: art_requests/
    route_landmarks.md asks for one). Returns the buildings."""
    import random
    style = route_features.FEATURES.get(key, {}).get("rocks", "mix")
    pf = cfg["prefabs"]
    rng = random.Random(key + "rocks")
    h, w = len(grid), len(grid[0])
    out = []
    mine = set()
    ok = lambda x, y: (0 <= x < w and 0 <= y < h and (x, y) in rocks and grid[y][x] == "." and (x, y) not in occ
                       and (x, y) not in mine)

    def put(name, x, y):
        rows = pf[name]["rows"]
        cells = [(x + i, y + j) for j in range(len(rows)) for i in range(len(rows[0]))]
        mine.update(cells)
        occupy(occ, x, y, len(rows[0]), len(rows))
        out.append({"prefab": name, "x": x, "y": y, "label": "Boulder" if name.startswith("rock") else "Tree"})
    if style == "wall":
        for name, pw, ph in (("rock_l", 2, 2), ("rock", 1, 1)):
            for y in range(h):
                for x in range(w):
                    if all(ok(x + i, y + j) for i in range(pw) for j in range(ph)):
                        put(name, x, y)
        return out
    area = {"rock_l": (2, 2), "rock": (1, 1), "field_tree": (2, 3)}
    cells = sorted(c for c in rocks if grid[c[1]][c[0]] == ".")
    for _ in range(len(cells) * 3):
        name = rng.choices(["rock_l", "rock", "field_tree"], [5, 4, 2])[0]
        pw, ph = area[name]
        x, y = rng.choice(cells)
        if not all(ok(x + i, y + j) for i in range(pw) for j in range(ph)):
            continue
        if any((x + i, y + j) in mine for i in range(-2, pw + 2) for j in range(-1, ph + 1)):
            continue
        if sum((x + i, y + j) in mine for i in range(-4, pw + 4) for j in range(-4, ph + 4)) > 14:
            continue  # density: no more than a few pieces within reach
        put(name, x, y)
    return out


def first_pass(entry):
    key, mock, name, const, kind, cfg_name, mapsec, music = entry
    cfg_name = TOWN_CFG.get(key, cfg_name)  # each town has its own tileset
    dry = key in DRY_ROUTES  # the dry country: the dry-country art set instead of the bayou's (dry_route_tileset.py)
    green, masks = set(), {}  # cells that stay green meadow in the dry country (the mockup's short grass); gully, salt cells
    cfg = with_placeholders(load_cfg(cfg_name))
    prefix = os.path.join(MAPS_DIR, key)
    subprocess.run([sys.executable, os.path.join(HERE, "extract.py"), os.path.join(MOCKUPS, mock + ".png"), prefix,
                    "--outdoor"], check=True, capture_output=True)
    det = json.load(open(prefix + ".detected.json"))
    raw = [l.rstrip("\n") for l in open(prefix + ".grid.txt")]
    grid, trees, boats = normalise(raw, cfg)
    markers = det["markers"]
    exits = det.get("exits", [])  # the mockup's exit arrows: {side, pos} along that edge
    rocks = set()
    if kind == "route":  # rock and stone (a bluff, the salt dome) become boulder fields on bare ground, not trees
        rocks = {(x, y) for y, r in enumerate(raw) for x, c in enumerate(r) if c in "RS"}
        trees -= rocks
        grid = ["".join("." if (x, y) in rocks else c for x, c in enumerate(r)) for y, r in enumerate(grid)]
    if key in GROW and GROW[key].get("S"):  # more map to the south than the mockup draws: its last rows mirrored
        n, h0 = GROW[key]["S"], len(grid)
        src = [h0 - 1 - (k % h0) for k in range(n)]  # mirror the bottom rows downwards
        grid = grid + [grid[y] for y in src]
        trees |= {(x, h0 + k) for k, y in enumerate(src) for x in range(len(grid[0])) if (x, y) in trees}
    exits = exits + EXTRA_EXITS.get(key, [])
    if key in PLANS:  # scale the town up so the real prefabs fit where the mockup drew its boxes
        s = SCALE[key]
        sw, sh = len(grid[0]), len(grid)
        for fx, fy, fw, fh, ch in TERRAIN_FIX.get(key, []):
            grid = [r if not fy <= y < fy + fh else r[:fx] + ch * fw + r[fx + fw:] for y, r in enumerate(grid)]
        grid = scale_grid(clear_buildings(grid, "=" if kind == "city" else "."), s)
        trees = {(x, y) for y in range(len(grid)) for x in range(len(grid[0]))
                 if (min(sw - 1, int(x / s)), min(sh - 1, int(y / s))) in trees}
        boats = [(round(x * s), round(y * s)) for x, y in boats]
        markers = [dict(m, x=int(m["x"] * s), y=int(m["y"] * s)) for m in markers]
        exits = [dict(e, pos=int((e["pos"] + 0.5) * s)) for e in exits]
    elif kind == "route":  # a route's boxes (a gate on the road, a warehouse in its yard) give way to ground
        grid = apply_route_terrain(key, clear_buildings(grid, ".", roads_win=True), mock, det)
        if dry:
            # the extractor reads crop rows (sugar cane, pepper dots) as tall grass: only the key's tall-grass green is
            # encounter grass here
            tall = mock_cells(mock, det, (143, 196, 106), tol=6)
            grid = ["".join("G" if (x, y) in tall else "." if c == "G" else c for x, c in enumerate(r))
                    for y, r in enumerate(grid)]
            masks = {}
            f_ = route_features.FEATURES.get(key, {})
            if f_.get("gully"):  # the dry washes: the mockup's riverbed band is gully, not road
                masks["gully"] = mock_cells(mock, det, f_["gully"], tol=2)
                band = masks["gully"]  # (the extractor's road cells there include stray ones the sampling misses)
                grid = ["".join("." if c == ":" and any((x + i, y + j) in band for i in range(-2, 3) for j in range(-2, 3))
                                else c for x, c in enumerate(r)) for y, r in enumerate(grid)]
            if f_.get("salt"):  # the salt flats
                masks["salt"] = mock_cells(mock, det, f_["salt"], tol=6)
            trees |= mock_cells(mock, det, (63, 115, 80), tol=10) - rocks  # the dark blobs are trees (field trees)
            if f_.get("rock_wall") and rocks:  # a cave box's floor shut in by rock is rock, not a street to join to the roads
                gg = [list(r) for r in grid]
                hh, ww = len(gg), len(gg[0])
                dq = deque((x, y) for x in range(ww) for y in range(hh) if (x in (0, ww - 1) or y in (0, hh - 1)) and (x, y) not in rocks)
                sn = set(dq)
                while dq:
                    x, y = dq.popleft()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < ww and 0 <= ny < hh and (nx, ny) not in sn and (nx, ny) not in rocks:
                            sn.add((nx, ny))
                            dq.append((nx, ny))
                for y in range(hh):
                    for x in range(ww):
                        if (x, y) not in sn and (x, y) not in rocks and gg[y][x] in ":=":
                            gg[y][x] = "."
                grid = ["".join(r) for r in gg]
            green = mock_cells(mock, det, (211, 230, 180), tol=6)
            for cells in components([["G" if (x, y) in green else "." for x in range(len(grid[0]))]
                                     for y in range(len(grid))], "G"):  # props drawn over a meadow don't hole it
                green |= {(x, y) for x in range(min(c[0] for c in cells), max(c[0] for c in cells) + 1)
                          for y in range(min(c[1] for c in cells), max(c[1] for c in cells) + 1)}
    open(prefix + ".grid.txt", "w").write("\n".join(grid) + "\n")
    w, h = len(grid[0]), len(grid)
    occ = set()
    path_char = "=" if kind == "city" else ":"
    grid = fill_holes(bridges(tidy_paths(levee_roads(grid))))
    if kind in ("town", "route") and key not in SACRED:
        grid = yards_to_grass(grid)
    grid, dock_list, dock_walk = docks(grid, occ, key in DOCK_ALL, planks=kind in ("town", "route"))
    patch_keep = set()  # patches under prefabs that stand in them: verges mustn't eat them
    if key in PLANS or key in ROUTE_PLANS:
        buildings, skipped = place_planned(key, grid, cfg, occ, SCALE.get(key, 1))
        g = [list(r) for r in grid]
        for b in buildings:  # buildings stand on plain ground: no water, marsh, mud or tall grass under or round them,
            # and no path under them (own-art buildings are drawn over whatever is beneath); a prefab that stands
            # in a patch (the shrine stone in marsh) gets that patch instead
            pf = cfg["prefabs"][b["prefab"]]
            rows, base = pf["rows"], pf.get("on_patch")
            for j in range(-1, len(rows) + 1):
                for i in range(-1, len(rows[0]) + 1):
                    x, y = b["x"] + i, b["y"] + j
                    inside = 0 <= i < len(rows[0]) and 0 <= j < len(rows)
                    if not (0 <= x < w and 0 <= y < h) or (x, y) in dock_walk:
                        continue
                    if base:
                        g[y][x] = base
                        patch_keep.add((x, y))
                    elif g[y][x] in "~I\"LG" or (inside and g[y][x] in ":="):
                        g[y][x] = "."
        grid = ["".join(r) for r in g]
        for b in skipped:
            print("    skipped", b)
    else:
        buildings, skipped = place_buildings(det["buildings"], grid, cfg, occ) if kind != "route" else ([], [])
    # piers out toward boat exits: towns (and the shrine) that the boat lines call at, and the routes whose
    # mockups mark a landing; water routes are crossed by Surf and need none
    more, more_walk = landings(grid, exits if kind != "route" or key in LANDINGS else [], occ, dock_walk)
    dock_list, dock_walk = dock_list + more, dock_walk | more_walk
    grid = carve_paths(buildings + dock_list, grid, cfg, occ, path_char, dock_walk, exits)
    # where the path joiner had to cross water it left boardwalk: lay those as bridges too
    grid, more, more_walk = docks(grid, occ)
    dock_list, dock_walk = dock_list + more, dock_walk | more_walk
    # a river keeps flowing past its bridges: no verge may fill the water just up- and downstream of one
    bridge_water = {(b["x"] + i, b["y"] + j) for b in dock_list if b["label"] == "Bridge"
                    for j in range(-3, len(b["rows"]) + 3) for i in range(-3, len(b["rows"][0]) + 3)
                    if 0 <= b["x"] + i < w and 0 <= b["y"] + j < h and grid[b["y"] + j][b["x"] + i] in "~I"}
    patch_keep |= bridge_water
    foot = {(b["x"] + i, b["y"] + j) for b in buildings + dock_list
            for j, row in enumerate(b.get("rows") or cfg["prefabs"][b["prefab"]]["rows"]) for i in range(len(row))}
    dock_cells = {(b["x"] + i, b["y"] + j) for b in dock_list for j, row in enumerate(b["rows"]) for i in range(len(row))}
    grid = banks(tidy_paths(grid, foot | patch_keep), dock_cells | patch_keep)
    grid = islets(grid, occ)
    buildings = dock_list + buildings
    g = [list(r) for r in grid]
    for b in buildings:  # a walkable street tile under every door
        for x, y in door_cells(cfg, b):
            if y + 1 < h and g[y + 1][x] in "~\"":
                g[y + 1][x] = path_char
    for b in dock_list:  # the road runs right onto each end of a bridge's deck (no grass gap, no rounded end)
        if b["label"] != "Bridge":
            continue
        rows = b["rows"]
        ew = len(rows) == 4 and all(j in (1, 2) for _, j in b["passable"])
        for i, j in b["passable"]:
            if ew and i not in (0, len(rows[0]) - 1) or not ew and j not in (0, len(rows) - 1):
                continue
            dx, dy = ((-1 if i == 0 else 1), 0) if ew else (0, (-1 if j == 0 else 1))
            x, y = b["x"] + i + dx, b["y"] + j + dy
            for _ in range(3):
                if not (0 <= x < w and 0 <= y < h) or g[y][x] in ":=%&" or g[y][x] in "~I" or (x, y) in occ:
                    break
                g[y][x] = path_char
                x, y = x + dx, y + dy
    grid = fill_holes(tidy_paths(["".join(r) for r in g], foot | patch_keep), keep=patch_keep)  # the last word on path shapes: 2 wide
    grid = banks(grid, dock_cells | patch_keep)
    # one road surface per map, so dirt and paving never meet in a hard seam: the cities are paved throughout,
    # towns keep packed-mud roads (their yards included)
    if kind == "city":
        grid = [r.replace(":", "=") for r in grid]
    elif kind == "town":
        grid = [r.replace("=", ":") for r in grid]
    if kind in ("town", "route") and key not in SACRED and key not in route_features.STRAIGHT:  # worn bends, bulges, doorstep aprons (natural.py)
        from natural import natural_paths
        fronts = [{"prefab": b["prefab"], "doors": door_cells(cfg, b)} for b in buildings if door_cells(cfg, b)]
        grid = tidy_paths(natural_paths(key, grid, foot | patch_keep, dock_cells | dock_walk,
                                        [c for b in buildings for c in door_cells(cfg, b)], trees, kind=kind,
                                        fronts=fronts), foot | patch_keep)
    if route_features.FEATURES.get(key, {}).get("trim_shore"):  # thick road touching the water: the shore row goes to grass
        for _ in range(2):
            g = [list(r) for r in grid]
            for y in range(h):
                for x in range(w):
                    if g[y][x] in ":=" and (x, y) not in foot | patch_keep | dock_cells and any(
                            0 <= x + i < w and 0 <= y + j < h and grid[y + j][x + i] in "~I"
                            for i in (-1, 0, 1) for j in (-1, 0, 1)) and sum(
                            0 <= x + i < w and 0 <= y + j < h and grid[y + j][x + i] in ":="
                            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)) >= 3:
                        g[y][x] = "."
            grid = ["".join(r) for r in g]
    if key in levee.MAPS:  # levee ground along river channels ('B'): kept clear, drawn by build.py
        near = {(x + i, y + j) for x, y in dock_cells for i in (-1, 0, 1) for j in (-1, 0, 1)}
        grid = levee.mark(grid, occ | foot | patch_keep | near, key)
    feature_signs, feature_keep = [], set()
    if kind == "route":
        grid, more, feature_signs, feature_keep = place_features(key, grid, cfg, occ, buildings)  # landmarks and details
        if dry:
            cliff, wall = dry_cliffs(key, rocks, grid, cfg, occ)
            mixed = rocks - wall if route_features.FEATURES.get(key, {}).get("rock_wall", {}).get("mix", not wall) else set()
            buildings += more + cliff + dry_rocks(key, mixed, grid, cfg, occ)
        else:
            buildings += more + boulders(key, rocks, grid, cfg, occ)
        if key not in SACRED:
            grid = route_grass(key, grid, occ, route_features.FEATURES.get(key, {}).get("share"))
    trees = {(x, y) for x, y in trees if grid[y][x] not in ":="}  # no trees on the roads
    open(prefix + ".grid.txt", "w").write("\n".join(grid) + "\n")
    buildings += place_boats(boats, grid, cfg, occ, "airboat" if key == "camp_cocodrie" else "trawler")
    if kind != "route":  # street life: benches, lamps, waterfront clutter, yard magnolias
        buildings += furnish(key, grid, cfg, occ, kind, dock_list, buildings)
    g = [list(r) for r in grid]
    for x0, y0, rw, rh, _ch in EDGE_PAINT.get(key, []):  # trees and greenery keep off the rectangles edge_clear paints
        occ |= {(x, y) for y in range(y0, y0 + rh) for x in range(x0, x0 + rw)}
    buildings += plant_trees(trees, g, cfg, occ, dry)  # may turn a marsh tree's footprint back into marsh
    grid = ["".join(r) for r in g]
    if dry:  # no bayou: no marsh fringe, cypress groves or water props
        extra = []
    else:
        grid, extra = greenery(key, grid, cfg, occ, kind, {(m["x"], m["y"]) for m in markers}, groves=key not in SACRED)
    buildings += extra
    grid = edge_clear(key, grid, occ)
    from approach import lay as approach_lay  # routes leaving a city: its paving carried on and broken up (approach.py)
    grid, more, approach_signs = approach_lay(key, grid, occ, cfg["prefabs"], dock_cells)
    buildings += more
    grid = prune_thin(grid, occ | patch_keep | feature_keep)  # no 1-2 tile slivers of tall grass or marsh
    open(prefix + ".grid.txt", "w").write("\n".join(grid) + "\n")
    lid, ldir = shell(name, const, kind, mapsec, music, w, h, cfg)
    spec_path = prefix + ".json"
    objs, items, surf = objects(markers, grid, occ, const)
    hidden, hidden_surf = hidden_items(key, const, markers, grid, occ)
    surf = surf + hidden_surf
    # the mockup's exits that are reached on foot, for check.py to test: road or plank cells on that edge
    walk_all = dock_walk | {(i, j) for b in dock_list for i, j in ((b["x"] + a, b["y"] + c) for a, c in b["passable"])}
    spec_exits = []
    for e in exits:
        cells = [c for c in ([(e["pos"] + d, 0 if e["side"] == "N" else h - 1) for d in range(-4, 5)] if e["side"] in "NS" else
                             [(0 if e["side"] == "W" else w - 1, e["pos"] + d) for d in range(-4, 5)])
                 if 0 <= c[0] < w and 0 <= c[1] < h and (grid[c[1]][c[0]] in ":=%&" or c in walk_all)]
        if cells:
            spec_exits.append({"name": f"{e['side']} exit at {e['pos']}", "cells": [list(c) for c in cells]})
    if dry:  # the ground becomes dry country (and fades to meadow where a green map is next door)
        reserved = {(o["x"], o["y"]) for o in objs + items + hidden} | {tuple(c) for c in surf}
        grid, more = dry_finish(key, grid, occ, cfg, green, rocks, reserved, buildings, masks)
        buildings += more
        open(prefix + ".grid.txt", "w").write("\n".join(grid) + "\n")
    spec = {"_comment": f"FIRST PASS generated by firstpass.py from {mock}.png: hand-tune before release.",
            "map": name, "map_const": const, "layout": lid, "layout_dir": ldir, "tileset": cfg_name,
            "mockup": os.path.join(MOCKUPS, mock + ".png").replace(os.sep, "/"), "grid": key + ".grid.txt",
            "edits": [], "buildings": swap_placeholders(buildings, cfg), "objects": objs, "surf_only": surf,
            "items": items, "hidden_items": hidden, "signs": approach_signs + feature_signs, "exits": spec_exits}
    spec["buildings"] = [b for b in spec["buildings"] if b["prefab"] not in __import__("town_plans").DROP_PREFAB.get(key, ())]
    if key in __import__("town_plans").CHAR_MAP:  # a route on a town's tileset reads its grid characters in the town's alphabet (build.py "char_map")
        spec["char_map"] = __import__("town_plans").CHAR_MAP[key]
        spec["prefab_map"] = __import__("town_plans").PREFAB_MAP[key]
    import wedge  # the world's join edits (world_edges.json): edits and prefab drops/adds per map
    wedge.apply_to_spec(spec, key)
    dump(spec_path, spec)
    b = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), spec_path] + ([] if BLENDS else ["--no-blends"]),
                       capture_output=True, text=True)
    c = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "check.py"), spec_path],
                       capture_output=True, text=True)
    summary = [l for l in (b.stdout + c.stdout + b.stderr[-300:] + c.stderr[-300:]).splitlines()
               if any(k in l for k in ("warps", "problems", "seams", "Error", "error", "left as plain"))]
    return {"key": key, "size": f"{w}x{h}", "buildings": len([x for x in buildings if x["label"] not in ("Tree", "Boat", "Dock", "Bridge", "Boardwalk", "Water prop", "Reeds", "Boulder", "Bench", "Lamp", "Prop")]),
            "trees": len([x for x in buildings if x["label"] == "Tree"]), "skipped": len(skipped),
            "ok": b.returncode == 0, "log": summary}


BLENDS = "--blends" in sys.argv  # request transition and overlay tiles (then compose, then run again)
HANDMADE = {"crescent_city", "pointe_rouge", "storms_edge", "camp_cocodrie", "lutins_hollow", "redfield", "lands_end", "oldest_shrine"}  # own generators (crescent.py, pointe.py, storms_edge.py, camp.py, hollow.py, redfield.py, lands_end.py, oldest_shrine.py)
SACRED = {"oldest_shrine"}  # the shrine island: its courtyard stays a courtyard, its ring of trees the mockup's
LANDINGS = {"oldest_shrine", "route_4", "route_9", "route_12"}  # routes whose mockups mark a boat landing
SALT = {"route_2", "route_21", "route_22", "isle_marais", "storms_edge", "lands_end"}  # on the Gulf: salt water


def main(keys):
    keys = [k for k in keys if not k.startswith("--")]
    todo = [e for e in ALL if (not keys and e[0] not in HANDMADE) or e[0] in keys]
    for e in todo:
        r = first_pass(e)
        print(f"{r['key']:<16} {r['size']:>7}  buildings {r['buildings']:>2}  trees {r['trees']:>3}  skipped {r['skipped']}"
              f"  {'built' if r['ok'] else 'BUILD FAILED'}")
        for line in r["log"]:
            print("    " + line)


if __name__ == "__main__":
    main(sys.argv[1:])

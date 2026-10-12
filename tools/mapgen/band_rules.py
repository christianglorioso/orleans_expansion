"""The seam-band rule applied while a map is built (build.py's Builder.draw calls prepare() and repair()).

See bands.py for the rule itself.  Every generator ends in build.py, so enforcing it here keeps every map's band clean no
matter which generator (firstpass, crescent.py, pointe.py ...) produced the spec:

  prepare(b)  before the terrain is laid:
    * props (trees other than cypress groves, magnolias, lamps, signs, benches, flowers, fences, rails, logs, reeds, boats' props,
      rocks ...) with a cell in a strict band are taken out of b.spec["buildings"] (and a sign event standing on one);
    * terrain characters the autotiles can only draw with secondary pieces (cane, pepper, red earth, gully, salt, rock wall,
      churchyard ...) become the plain character the config names in "band_fallback" (default '.' grass);
    * structures (anything with a door, bridges, piers, docks, planks, quays, boardwalks) are never removed: they are
      reported, and the generator has to move them (b.band_unresolved lists them).
  repair(b)  after the terrain is laid: cells of the band that still hold a secondary piece (dual-grid edges of a set that
    stops inside the band, three-way blends, levee pieces ...) get their 2x2 corner window rewritten to one plain terrain and
    the map is drawn again (up to MAX_ROUNDS times).
Everything it changes is listed in b.band_log (build.py prints it; look_diff-style reports quote it).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bands  # noqa: E402

MAX_ROUNDS = 14
# prefab names / labels that are structures: walkways, buildings with doors, anything a generator has to place by hand
STRUCTURE = re.compile(r"^(pier|bridge|quay|plank|dock|bw_|walk|boardwalk|landing|gate|skirt|mskirt|pile|heron_pile|trapline|"
                       r"pavilion|substation|refinery|stilt|house|hut|cabin|barn|church)", re.I)
STRUCTURE_LABELS = ("Bridge", "Dock", "Boardwalk", "Pier")
# every prefab that is NOT a structure and has a cell in a strict band is a prop and is dropped; groves of cypress are kept
# because their pieces are primary (checked per prefab, below)


def _build(b):
    """the builder's own module (run as a script it is __main__: a fresh `import build` would have an empty MAPPING)"""
    return sys.modules[type(b).__module__]


def _primary_name(b, name):
    """is a piece name / hex id a primary metatile? (a dict cell, an overlay or a variant is not)"""
    build = _build(b)
    try:
        return build.MAPPING[name] < 512 if ":" in name else int(name, 16) < 512
    except (KeyError, ValueError):
        return False


def prefab_cells(b, bd):
    p = b.ts["prefabs"][bd["prefab"]]
    rows = bd.get("rows") or p["rows"]
    return [(bd["x"] + i, bd["y"] + j, c) for j, row in enumerate(rows) for i, c in enumerate(row) if c is not None]


def is_structure(b, bd):
    p = b.ts["prefabs"][bd["prefab"]]
    return bool(p.get("door") or bd.get("door") or bd.get("label") in STRUCTURE_LABELS or STRUCTURE.match(bd["prefab"])
                or STRUCTURE.match(str(bd.get("label", ""))))


def prefab_is_primary(b, bd):
    return all(isinstance(c, str) and _primary_name(b, c) for _, _, c in prefab_cells(b, bd))


def prepare(b, key):
    b.band_log = []
    b.band_unresolved = []
    b.band = set()
    b.band_map = {}
    if key not in bands.world.OUTDOOR:
        return
    strict = bands.strict_cells(key)
    b.band = strict
    b.band_map = bands.bands(key, True)
    if not strict:
        return
    spec = b.spec
    keep, dropped = [], []
    for bd in spec.get("buildings", []):
        cells = prefab_cells(b, bd)
        inside = [(x, y) for x, y, _ in cells if (x, y) in strict]
        if not inside:
            keep.append(bd)
        elif prefab_is_primary(b, bd):
            keep.append(bd)
        elif is_structure(b, bd) and (b.ts["prefabs"][bd["prefab"]].get("door") or bd.get("door")) and nudge(b, bd, strict, keep):
            keep.append(bd)
        elif is_structure(b, bd):
            keep.append(bd)
            b.band_unresolved.append(f"{bd.get('label', bd['prefab'])} ({bd['prefab']}) at ({bd['x']},{bd['y']}): {len(inside)} of "
                                     f"{len(cells)} cells in the band")
        else:
            dropped.append(bd)
    if dropped:
        gone = {(x, y) for bd in dropped for x, y, _ in prefab_cells(b, bd)}
        spec["buildings"] = keep
        # a tree / fence / bed that BLOCKED the way keeps blocking (a gate may rest on it): its cells stay impassable ("block")
        blocking = []
        for bd in dropped:
            if GATE_PROPS.search(bd["prefab"]):
                p = b.ts["prefabs"][bd["prefab"]]
                pas = {tuple(c) for c in bd.get("passable", p.get("passable", []))}
                blocking += [[bd["x"] + i, bd["y"] + j] for j, row in enumerate(bd.get("rows") or p["rows"])
                             for i, c in enumerate(row) if c is not None and (i, j) not in pas]
        if blocking:
            spec["block"] = list(spec.get("block", [])) + blocking
            b.band_log.append(f"{len(blocking)} cells of removed trees/fences stay impassable")
        by = {}
        for bd in dropped:
            by.setdefault(bd["prefab"], []).append((bd["x"], bd["y"]))
        b.band_log.append("props taken out of the band: " + ", ".join(f"{k} x{len(v)}" for k, v in sorted(by.items())))
        signs = spec.get("signs", [])
        lost = [g for g in signs if (g["x"], g["y"]) in gone]
        if lost:
            spec["signs"] = [g for g in signs if (g["x"], g["y"]) not in gone]
            b.band_log.append("sign events removed with their signposts: " + ", ".join(f"({g['x']},{g['y']})" for g in lost))
        for coll in ("objects", "items"):
            hit = [o for o in spec.get(coll, []) if (o["x"], o["y"]) in gone]
            if hit:
                b.band_log.append(f"WARNING {coll} stood on a removed prop: " + ", ".join(f"({o['x']},{o['y']})" for o in hit))
    # terrain characters
    fb = b.ts.get("band_fallback", {})
    changed = 0
    zone = window(b, strict)
    for (x, y) in zone:
        c = b.grid[y][x]
        if c in ":=&" and "p" in b.ts["terrain"] and "d" in b.ts["terrain"]:
            # the dry country's road set (dry:* pieces) is secondary: the Johto dirt path ('p', the approach's road on the
            # green meadow) carries the road through the band
            b.grid[y][x] = "p"
            changed += 1
        elif c == "&":                       # the approach paving's break-up (secondary overlay pieces) is plain dirt road in a band
            b.grid[y][x] = ":"
            changed += 1
        elif c in fb and fb[c] != c:
            b.grid[y][x] = fb[c]
            changed += 1
    if changed:
        b.band_log.append(f"{changed} terrain cells in the band simplified (band_fallback)")


INWARD = {"N": (0, 1), "S": (0, -1), "W": (1, 0), "E": (-1, 0)}


def nudge(b, bd, strict, others):
    """Move a building with a door out of the band, inward (away from the join), by the smallest step that leaves every one of its
    cells on plain ground ('.' in the grid) clear of other buildings, events and the band. Returns True if moved."""
    cells = prefab_cells(b, bd)
    key = b.key
    sides = set()
    for a_, sa, b_, sb, loa, hia, lob, hib in bands.joins():
        for me, side, lo, hi in ((a_, sa, loa, hia), (b_, sb, lob, hib)):
            if me == key:
                sides.add(side)
    busy = {(x, y) for o in others + b.spec.get("buildings", []) if o is not bd for x, y, _ in prefab_cells(b, o)}
    for coll in ("objects", "items", "signs", "hidden_items", "triggers"):
        busy |= {(o["x"], o["y"]) for o in b.spec.get(coll, [])}
    for ex in b.spec.get("exits", []):
        busy |= {tuple(c) for c in ex["cells"]}
    for side in sorted(sides, key=lambda s_: -sum(1 for x, y, _ in cells if (x, y) in strict)):
        dx, dy = INWARD[side]
        for step in range(1, 12):
            moved = [(x + dx * step, y + dy * step) for x, y, _ in cells]
            if any(not (0 <= x < b.w and 0 <= y < b.h) for x, y in moved):
                break
            if any((x, y) in strict or (x, y) in busy or b.grid[y][x] != "." for x, y in moved):
                continue
            bd["x"] += dx * step
            bd["y"] += dy * step
            b.band_log.append(f"{bd.get('label', bd['prefab'])} ({bd['prefab']}) moved {step} cell(s) inward, to ({bd['x']},{bd['y']})")
            return True
    return False


def window(b, cells):
    """the cells + the ones right of / below them (a dual-grid tile reads its cell and those three)"""
    out = set()
    for x, y in cells:
        for dx in (0, 1):
            for dy in (0, 1):
                if x + dx < b.w and y + dy < b.h:
                    out.add((x + dx, y + dy))
    return out


def violations(b):
    """[(x, y, id, name)] strict-band cells that are not primary metatiles"""
    build = _build(b)
    inv = {}
    for n, v in build.MAPPING.items():
        inv.setdefault(v, n)
    return [(x, y, b.blocks[y][x] & 0x3FF, inv.get(b.blocks[y][x] & 0x3FF, "?")) for (x, y) in sorted(b.band, key=lambda c: (c[1], c[0]))
            if (b.blocks[y][x] & 0x3FF) >= 512]


GATE_PROPS = re.compile(r"magnolia|tree|fence|flower|bed|hedge|wall|cypress|boulder|rock", re.I)
DRY_CHARS = set("dGgqQweysrv")
DRY_MAPS = {"redfield", "route_15", "route_16", "route_17", "route_23", "route_24"}


def repair(b):
    """one round of repairs; returns True if the grid changed (the caller draws again)"""
    bad = violations(b)
    changed = False
    # a tree standing on a marsh patch whose edge a repair has moved is taken out (check.py: "crosses its patch edge")
    if b.band:
        keep, gone = [], []
        for bd in b.spec.get("buildings", []):
            base = b.ts["prefabs"].get(bd["prefab"], {}).get("on_patch")
            if base:
                cells = [(bd["x"] + i, bd["y"] + j) for j, row in enumerate(bd.get("rows") or b.ts["prefabs"][bd["prefab"]]["rows"])
                         for i, c in enumerate(row) if c]
                if any(b.grid[min(y + dy, b.h - 1)][min(x + dx, b.w - 1)] not in base for x, y in cells for dx in (0, 1) for dy in (0, 1)):
                    gone.append(bd)
                    continue
            keep.append(bd)
        if gone:
            b.spec["buildings"] = keep
            b.band_log.append("trees off a repaired patch: " + ", ".join(f"{g['prefab']}@({g['x']},{g['y']})" for g in gone))
            changed = True
    for (x, y) in sorted(b.band_blends):          # water + marsh/mud + grass in one tile of the band: take the marsh/mud out
        for i, j in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            if i < b.w and j < b.h and b.grid[j][i] in '"L':
                b.grid[j][i] = "."
                changed = True
    if not bad:
        return changed
    terr = b.ts["terrain"]
    fb = b.ts.get("band_fallback", {})
    for x, y, mid, name in bad:
        win = [(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1) if x + dx < b.w and y + dy < b.h]
        chars = [b.grid[j][i] for i, j in win]
        new = None
        if name.startswith("dry:") or any(c in DRY_CHARS for c in chars):
            # a dry-country piece in the band: one plain terrain over the whole window, the one most of it already is
            dry = sum(1 for c in chars if c in DRY_CHARS)
            other = b.band_map.get((x, y))        # a green neighbour (Route 14, Pointe Rouge, Route 18): the band stays meadow
            green = other is not None and other not in DRY_MAPS
            new = "d" if dry * 2 >= len(chars) and "d" in terr and not green else "."
        elif name.startswith("patch:blend_"):
            for (i, j) in win:                       # water + marsh/mud + grass in one tile: take the marsh/mud out
                if b.grid[j][i] in '"L':
                    b.grid[j][i] = "."
                    changed = True
            continue
        elif name.startswith("patch:lv_"):
            for (i, j) in win:
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if 0 <= i + di < b.w and 0 <= j + dj < b.h and b.grid[j + dj][i + di] == "B":
                            b.grid[j + dj][i + di] = "."
                            changed = True
            continue
        else:
            c = b.grid[y][x]
            if c in fb and fb[c] != c:
                new = fb[c]
        if new:
            for (i, j) in win:
                if b.grid[j][i] != new and b.grid[j][i] not in ':=%&p':   # roads keep their cells
                    b.grid[j][i] = new
                    changed = True
    return changed

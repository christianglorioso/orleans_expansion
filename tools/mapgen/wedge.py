"""Edge edits for the world's joins (phase 2): data in world_edges.json, applied to a route's spec.

firstpass.py regenerates every route's spec with "edits": [], so the edge work that makes the joins line up lives in
world_edges.json and is merged back in by `apply_to_spec` (firstpass calls it just before it writes the spec).  The
handmade towns (camp.py, lands_end.py, crescent.py ...) do their own edge work in their generators.

world_edges.json:  { map_key: { "edits": [[char, x, y, w, h], ...],      painted over the grid, in order
                                "drop":  [[x, y], ...],                    prefabs (by their x, y) taken out
                                "add":   [ {prefab, x, y, label}, ... ] }  prefabs put in }

Authoring (see world_phase2_W.log.md): in a script,
    g = wedge.Grid("route_6")            # the generated grid
    wedge.pour(g, "E", {i: '"' ...}, ...) # or g.set(x, y, ch)
    g.save()                              # diff -> world_edges.json, spec patched
then run build.py and check.py on the spec as usual.  Everything here is pure data + geometry: no build, no lock.
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "maps")
EDGES = os.path.join(HERE, "world_edges.json")


def load():
    if not os.path.exists(EDGES):
        return {}
    return json.load(open(EDGES, encoding="utf-8"))


def store(d):
    import re
    text = json.dumps(d, indent=1, sort_keys=True)
    # one line per rect / cell pair
    text = re.sub(r"\[\s+([^\[\]{}]*?)\s+\]", lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text)
    with open(EDGES, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")


def base_grid(key):
    return [l.rstrip("\n") for l in open(os.path.join(MAPS, key + ".grid.txt"), encoding="utf-8") if l.strip()]


def effective_grid(key):
    """the grid build.py sees: grid.txt plus the world edits"""
    g = [list(r) for r in base_grid(key)]
    for ch, x, y, w, h in load().get(key, {}).get("edits", []):
        for j in range(y, y + h):
            for i in range(x, x + w):
                g[j][i] = ch
    return ["".join(r) for r in g]


def apply_to_spec(spec, key):
    """merge world_edges[key] into a spec dict (idempotent); returns the spec"""
    e = load().get(key)
    if not e:
        return spec
    spec["edits"] = [list(r) for r in e.get("edits", [])]
    if e.get("exits"):  # exits the generator doesn't list (a flat that runs on to a neighbour's walk)
        spec["exits"] = [x for x in spec.get("exits", []) if x["name"] not in {y["name"] for y in e["exits"]}] + e["exits"]
    drop = {(x, y) for x, y in e.get("drop", [])}
    keep = [b for b in spec["buildings"] if (b["x"], b["y"]) not in drop and not b.get("_w")]
    keep += [dict(b, _w=True) for b in e.get("add", [])]
    spec["buildings"] = keep
    return spec


class Grid:
    def __init__(self, key):
        self.key = key
        self.base = base_grid(key)
        self.h, self.w = len(self.base), len(self.base[0])
        self.g = [list(r) for r in self.base]
        self.drop = []
        self.exits = []
        self.dropped = []
        self.add = []
        # the spec as firstpass made it: drops put back, adds taken out (authoring always starts from scratch)
        e = load().get(key, {})
        sp = json.load(open(os.path.join(MAPS, key + ".json"), encoding="utf-8"))
        self.buildings = [b for b in sp["buildings"] if not b.get("_w")] + [dict(b) for b in e.get("dropped", [])]

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def rect(self, x, y, w, h, ch):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.set(i, j, ch)

    def grove(self, x, y, w, h, trees, ch='"'):
        """a marsh patch x..x+w-1 / y..y+h-1 with trees (prefab, x, y) standing in it (their cells must lie inside)"""
        self.rect(x, y, w, h, ch)
        for pf, tx, ty in trees:
            self.add.append({"prefab": pf, "x": tx, "y": ty, "label": "Tree"})

    def move(self, x, y, nx, ny):
        """move the prefab whose top-left is (x, y) to (nx, ny)"""
        b = next(b for b in self.buildings if (b["x"], b["y"]) == (x, y))
        self.drop.append([x, y])
        self.dropped.append(b)
        self.add.append(dict(b, x=nx, y=ny))

    def edge(self, side, i):
        return {"N": (i, 0), "S": (i, self.h - 1), "W": (0, i), "E": (self.w - 1, i)}[side]

    def inward(self, side, i, d):
        """cell d steps in from edge cell i"""
        x, y = self.edge(side, i)
        return {"N": (x, y + d), "S": (x, y - d), "W": (x + d, y), "E": (x - d, y)}[side]

    def length(self, side):
        return self.w if side in "NS" else self.h

    def diff_rects(self):
        out = []
        for y in range(self.h):
            x = 0
            while x < self.w:
                if self.g[y][x] != self.base[y][x]:
                    ch, x0 = self.g[y][x], x
                    while x < self.w and self.g[y][x] == ch and self.g[y][x] != self.base[y][x]:
                        x += 1
                    out.append([ch, x0, y, x - x0, 1])
                else:
                    x += 1
        # merge identical runs on consecutive rows into taller rects
        merged = []
        for r in out:
            for m in merged:
                if m[0] == r[0] and m[1] == r[1] and m[3] == r[3] and m[2] + m[4] == r[2]:
                    m[4] += 1
                    break
            else:
                merged.append(list(r))
        return merged

    def changed(self):
        return {(x, y) for y in range(self.h) for x in range(self.w) if self.g[y][x] != self.base[y][x]}

    def auto_drop(self, spec_path=None, keep_labels=()):
        """drop every non-structural prefab whose footprint sits on an edited cell and no longer on its own patch"""
        spec = json.load(open(spec_path or os.path.join(MAPS, self.key + ".json"), encoding="utf-8"))
        spec["buildings"] = self.buildings
        cfg = json.load(open(os.path.join(HERE, "tilesets", spec["tileset"] + ".json"), encoding="utf-8"))
        ch = self.changed()
        dropped = []
        for b in spec["buildings"]:
            if b.get("_w"):
                continue
            pf = cfg["prefabs"][b["prefab"]]
            rows = b.get("rows") or pf["rows"]
            cells = {(b["x"] + i, b["y"] + j) for j, r in enumerate(rows) for i, c in enumerate(r) if c is not None}
            want = pf.get("on_patch")
            ring = {(x + i, y + j) for x, y in cells for i in (-1, 0, 1) for j in (-1, 0, 1)} if want else cells
            hit = ring & ch
            if not hit:
                continue
            if b["label"] in ("Tree", "Water prop", "Reeds", "Floating debris", "Sunken ruin", "Boulder"):
                if want is None or any(self.g[y][x] != want for x, y in ring if 0 <= x < self.w and 0 <= y < self.h):
                    dropped.append((b["x"], b["y"], b["prefab"], b["label"]))
                    self.drop.append([b["x"], b["y"]])
                    self.dropped.append(b)
            else:
                print("  WARNING: structural prefab", b["label"], b["prefab"], b["x"], b["y"], "overlaps an edit")
        return dropped

    def save(self, spec=True):
        d = load()
        e = {"edits": self.diff_rects(), "drop": sorted(map(list, self.drop)), "dropped": self.dropped, "add": self.add, "exits": self.exits}
        if not e["edits"] and not e["add"]:
            d.pop(self.key, None)
        else:
            d[self.key] = e
        store(d)
        if spec:
            p = os.path.join(MAPS, self.key + ".json")
            s = json.load(open(p, encoding="utf-8"))
            s["buildings"] = self.buildings
            apply_to_spec(s, self.key)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                json.dump(s, f, indent=1)
                f.write("\n") if False else None


def prof_of(key, side, lo=None, hi=None, edge_chars=None):
    """terrain profile of a map's edge: {edge index: class} with class in '~' water, '"' marsh (tall grass and trees count
    as marsh), '.' ground; reads the effective grid (grid.txt + edits).  Trees are prefabs on marsh: the grid already says so."""
    g = effective_grid(key)
    h, w = len(g), len(g[0])
    n = w if side in "NS" else h
    out = {}
    for i in range(n):
        x, y = {"N": (i, 0), "S": (i, h - 1), "W": (0, i), "E": (w - 1, i)}[side]
        c = g[y][x]
        out[i] = {"~": "~", '"': '"', "G": '"', "T": '"', "I": "~", "L": "L"}.get(c, c if c in '.:=' else ".")
    return out


def depths(n, base, spread, seed, minrun=2, maxrun=4):
    """a list of n depths: constant over runs of 2-4 cells, stepping by 1-2 within base +- spread"""
    rng = random.Random(seed)
    out = []
    d = base
    while len(out) < n:
        out += [d] * rng.randint(minrun, maxrun)
        d = max(base - spread, min(base + spread, d + rng.choice((-2, -1, -1, 1, 1, 2))))
    return out[:n]


def pour(g, side, prof, lo, hi, base=5, spread=2, seed=1, offset=0, taper=True, only=None, wet=False):
    """Bring a neighbour's shore into map `g` along its `side`: for each edge index i in [lo, hi) the neighbour's edge cell
    is prof[i - offset] ('~' water, '"' marsh, '.' ground): where it is land, paint that land `d_i` cells deep (d_i varies in
    runs of 2-4 cells between base-spread and base+spread, and shallows next to a water cell so a channel gets a rounded
    mouth); where it is water the cell keeps `g`'s own water.  Ground gets a marsh rim so grass never touches both marsh and
    water at one corner (no blend tiles).  `only`: restrict to cells currently one of these chars."""
    idx = [i for i in range(lo, hi) if prof.get(i - offset) is not None]
    dep = dict(zip(idx, depths(len(idx), base, spread, seed)))
    # channel mouths: shallower beside a water cell
    if taper:
        for i in idx:
            if prof[i - offset] != "~":
                near = min([abs(i - j) for j in idx if prof[j - offset] == "~"] or [9])
                if near == 1:
                    dep[i] = max(2, dep[i] - 2)
                elif near == 2:
                    dep[i] = max(2, dep[i] - 1)
    for i in idx:
        ch = prof[i - offset]
        if ch == "~" and not wet:
            continue
        for d in range(dep[i]):
            x, y = g.inward(side, i, d)
            if 0 <= x < g.w and 0 <= y < g.h and (only is None or g.g[y][x] in only):
                g.g[y][x] = ch
    return dep


def rim(g, region=None):
    """no 2x2 block with water, marsh and ground all in it (that needs a blend tile): the ground cell becomes marsh"""
    cells = region if region is not None else g.changed()
    for _ in range(6):
        fix = set()
        for y in range(g.h - 1):
            for x in range(g.w - 1):
                blk = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
                if not any(c in cells for c in blk):
                    continue
                ch = [g.g[b][a] for a, b in blk]
                if "~" in ch and any(c in '"G' for c in ch) and "." in ch:
                    fix |= {c for c in blk if g.g[c[1]][c[0]] == "."}
        if not fix:
            return
        for x, y in fix:
            g.g[y][x] = '"'


def moat(g, a, b, ch="."):
    """cells of terrain b that touch terrain a (8 neighbours) become `ch` (mud and marsh share no transition set: a ground
    cell must lie between them)"""
    for _ in range(4):
        fix = {(x, y) for y in range(g.h) for x in range(g.w) if g.g[y][x] == b and any(
            g.at(x + i, y + j) == a for i in (-1, 0, 1) for j in (-1, 0, 1))}
        if not fix:
            return
        for x, y in fix:
            g.g[y][x] = ch


def keep_off(g, a, b, r=2, ch="~", region=None):
    """cells of terrain b within r (Chebyshev) of terrain a become `ch`: keeps two terrains that have no clean transition apart
    (the new mud flats off an island's ground)"""
    fix = {(x, y) for y in range(g.h) for x in range(g.w) if g.g[y][x] == b and any(
        g.at(x + i, y + j) == a for i in range(-r, r + 1) for j in range(-r, r + 1))}
    for x, y in fix:
        g.g[y][x] = ch

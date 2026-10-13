"""Shared kit for the legendary lairs (batch 1): ground cells from the built tilesets, a dual-grid set maker, a sheet
of opaque pieces (props are baked over the ground they stand on, so every lair metatile is a plain cell), the
compose recipe writer, and the mock-map builder used by lair_mocks.py.

Outdoor lairs are small unconnected maps on the shared outdoor primary (gTileset_OrleansGeneral), so Ekat grass,
marsh, water, lily pads, cypress and the swamp canopy wall with its edge cells cost nothing; each lair secondary only
holds the lair's own art (and the dry-country / border cells the dry lairs reuse, copied from their sheets).
"""
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, os.path.join(MAPGEN, "tilesets", "arenas"))
sys.path.insert(0, MAPGEN)
from arena_art import Canvas, check_families, dump, gba, hashn, scale, KEY  # noqa: E402,F401
import render  # noqa: E402

CORNER_KEYS = {"1111": "C", "0011": "N", "1100": "S", "0101": "W", "1010": "E", "0111": "inNW", "1011": "inNE",
               "1101": "inSW", "1110": "inSE", "0001": "landSE", "0010": "landSW", "0100": "landNE", "1000": "landNW",
               "0110": "sTLBR", "1001": "sTRBL"}
SRC = os.path.join(MAPGEN, "sources", "orleans_custom")

# ---------------------------------------------------------------- ground from the built tilesets
_P = {}


def primary():
    if "ts" not in _P:
        _P["ts"] = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_general"),
                                   os.path.join(ROOT, "data/tilesets/secondary/orleans_route_b"))
        _P["map"] = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]
        _P["bts"] = render.Tilesets(os.path.join(ROOT, "data/tilesets/primary/orleans_building"),
                                    os.path.join(ROOT, "data/tilesets/secondary/orleans_interior"))
    return _P


def pcell(name):
    """A primary metatile as a 16x16 RGB image."""
    P = primary()
    return P["ts"].metatile(P["map"][name]).convert("RGB")


def as_canvas(im):
    cv = Canvas(im.width // 16, im.height // 16)
    cv.im.paste(im.convert("RGBA"), (0, 0))
    cv.p = cv.im.load()
    return cv


def sheet_cell(png, x, y, w=1, h=1):
    """Cells of an art sheet (magenta = clear) as a Canvas."""
    im = Image.open(png).convert("RGBA").crop((x * 16, y * 16, (x + w) * 16, (y + h) * 16))
    px = im.load()
    for j in range(im.height):
        for i in range(im.width):
            if px[i, j][:3] == KEY:
                px[i, j] = (0, 0, 0, 0)
    return as_canvas(im)


def tex_from(im):
    """A 16x16 RGB image as a texture function (x, y) -> colour."""
    p = im.load()
    return lambda x, y: p[x % 16, y % 16][:3]


def over(cv, ground):
    """A canvas composited over a ground (a texture function or a 16x16 image), as a new opaque canvas."""
    g = ground if callable(ground) else tex_from(ground)
    out = Canvas(cv.cw, cv.ch)
    for j in range(cv.h):
        for i in range(cv.w):
            c = cv.get(i, j)
            out.put(i, j, c if c is not None else g(i, j))
    return out


# ---------------------------------------------------------------- dual-grid sets
def _disk(r):
    return [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dx * dx + dy * dy <= r * r + r * 0.5]


def _morph(m, offs, op):
    if op == "dilate":
        return {(x + dx, y + dy) for (x, y) in m for dx, dy in offs}
    return {(x, y) for (x, y) in m if all((x + dx, y + dy) in m for dx, dy in offs)}


_REG = {}


def corner_region(bits, ro=6, ri=5, wob=0):
    """The patch region (pixel set, tile pixel (0, 0) = (16, 16)) for corner bits TL TR BL BR; convex corners
    rounded by ro, concave by ri; wob > 0 roughens the boundary a little (deterministic, seam-safe: the wobble is
    a function of the absolute position along the edge, so neighbouring tiles agree)."""
    key = (bits, ro, ri, wob)
    if key in _REG:
        return _REG[key]
    m = set()
    q = {0: (range(-16, 8), range(-16, 8)), 1: (range(8, 32), range(-16, 8)),
         2: (range(-16, 8), range(8, 32)), 3: (range(8, 32), range(8, 32))}
    for k, b in enumerate(bits):
        if b == "1":
            xs, ys = q[k]
            m |= {(x + 16, y + 16) for y in ys for x in xs}
    m = _morph(_morph(m, _disk(ro), "erode"), _disk(ro), "dilate")
    m = _morph(_morph(m, _disk(ri), "dilate"), _disk(ri), "erode")
    if wob:
        # push the boundary in or out by one pixel on a 4 px rhythm keyed to x + y (period divides 16)
        edge_in = {(x, y) for (x, y) in m if any((x + dx, y + dy) not in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        edge_out = {(x + dx, y + dy) for (x, y) in edge_in for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - m
        out = set(m)
        for (x, y) in edge_in:
            if (x + 2 * y) % 8 in (0, 1):
                out.discard((x, y))
        for (x, y) in edge_out:
            if (2 * x + y) % 8 in (4,):
                out.add((x, y))
        m = out
    _REG[key] = m
    return m


def dual_set(style, ro=6, ri=5, wob=1):
    """{key: Canvas} for the 15 corner keys; style(i, j, inside, info) -> colour, where info has the distances to the
    other region in the four directions (dn, ds, dw, de; None beyond 8) and the tile pixel (i, j)."""
    out = {}
    for bits, key in CORNER_KEYS.items():
        m = corner_region(bits, ro, ri, wob)
        cv = Canvas(1, 1)
        for j in range(16):
            for i in range(16):
                x, y = i + 16, j + 16
                inside = (x, y) in m

                def dist(dx, dy):
                    return next((d for d in range(1, 9) if (((x + dx * d, y + dy * d) in m) != inside)), None)
                info = {"dn": dist(0, -1), "ds": dist(0, 1), "dw": dist(-1, 0), "de": dist(1, 0)}
                cv.put(i, j, style(i, j, inside, info))
        out[key] = cv
    return out


# ---------------------------------------------------------------- the sheet of pieces
class Pieces:
    """Named opaque pieces (Canvas, w x h cells) with walk flags and notes; packs into a sheet and a recipe."""

    def __init__(self, prefix, cols=16):
        self.prefix, self.cols = prefix, cols
        self.items = {}
        self.order = []

    def add(self, name, cv, walk=False, comment="", lair="", behavior=None):
        assert name not in self.items, name
        self.items[name] = dict(cv=cv, walk=walk, comment=comment, lair=lair, behavior=behavior)
        self.order.append(name)
        return name

    def add_set(self, base, cells, walk=False, comment="", lair=""):
        for key, cv in cells.items():
            self.add(f"{base}_{key}", cv, walk=walk, comment=f"{comment} ({key})", lair=lair)

    def pack(self):
        x = y = shelf = 0
        pos = {}
        for n in self.order:
            cv = self.items[n]["cv"]
            if x + cv.cw > self.cols:
                x, y, shelf = 0, y + shelf, 0
            pos[n] = (x, y)
            x += cv.cw
            shelf = max(shelf, cv.ch)
        im = Image.new("RGB", (self.cols * 16, (y + shelf) * 16), KEY)
        for n in self.order:
            cv = self.items[n]["cv"]
            px, py = pos[n]
            sub = Image.new("RGB", (cv.w, cv.h), KEY)
            sub.paste(cv.im, (0, 0), cv.im)
            im.paste(sub, (px * 16, py * 16))
        self.pos, self.image = pos, im
        return im

    def cell_names(self, n):
        cv = self.items[n]["cv"]
        if cv.cw == cv.ch == 1:
            return [[f"{self.prefix}:{n}"]]
        return [[f"{self.prefix}:{n}_{i}_{j}" for i in range(cv.cw)] for j in range(cv.ch)]

    def write(self, png, dirname, symbol, primary_mapping, families, title, group_rule="fewest"):
        self.pack()
        self.image.save(os.path.join(HERE, png))
        mts, pieces = [], {}
        for n in self.order:
            it = self.items[n]
            cv = it["cv"]
            px, py = self.pos[n]
            names = self.cell_names(n)
            for j in range(cv.ch):
                for i in range(cv.cw):
                    e = {"id": names[j][i].split(":", 1)[1], "bottom": [px + i, py + j]}
                    if it["behavior"] and (i, j) in it["behavior"]:
                        e["behavior"] = it["behavior"][(i, j)]
                    mts.append(e)
            walk = it["walk"]
            walk = [[i, j] for j in range(cv.ch) for i in range(cv.cw)] if walk is True else (walk or [])
            pieces[n] = {"x": px, "y": py, "w": cv.cw, "h": cv.ch, "rows": names, "walk": walk,
                         "lair": it["lair"], "comment": it["comment"]}
        dump(os.path.join(HERE, png.replace(".png", ".json")), {
            "_comment": f"{title}: piece -> sheet cells (16 px, every cell opaque: props are baked over their ground), "
                        f"metatile names ('{self.prefix}:<id>' in {symbol}), walkable cells (the rest block), the lair "
                        f"it belongs to. Made by {os.path.basename(sys.argv[0])}.",
            "png": png, "tileset": symbol, "families": {k: [list(c) for c in v] for k, v in families.items()},
            "pieces": pieces})
        os.makedirs(os.path.join(HERE, "recipes"), exist_ok=True)
        dump(os.path.join(HERE, "recipes", dirname + ".json"), {
            "_comment": f"{title} (own art, tools/mapgen/tilesets/lairs). Compose: python tools/mapgen/compose.py "
                        f"tools/mapgen/tilesets/lairs/recipes/{dirname}.json (mapping lands in tilesets/lairs/). To "
                        f"register: copy into tilesets/recipes/, set primary_mapping to '{primary_mapping}', compose "
                        f"--register.",
            "kind": "secondary", "dir": dirname, "symbol": symbol, "primary_mapping": "../" + primary_mapping,
            "palette": "v2",
            "sources": [{"name": self.prefix, "type": "image", "image": f"tools/mapgen/tilesets/lairs/{png}",
                         "transparent": [[255, 0, 255]], "group_rule": group_rule, "metatiles": mts}]})
        bad = check_families([(n, self.items[n]["cv"].im) for n in self.order], families, self.prefix)
        return bad


# ---------------------------------------------------------------- shared props drawing helpers
def outline_shape(cv, body, c):
    for (x, y) in list(body):
        for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in body:
                cv.put(x + dx, y + dy, c)


def night(im, k=(0.42, 0.48, 0.78), lift=(4, 8, 22)):
    """An approximation of the day/night tint at night (for the review renders only)."""
    im = im.convert("RGB")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            px[x, y] = (min(255, int(r * k[0]) + lift[0]), min(255, int(g * k[1]) + lift[1]), min(255, int(b * k[2]) + lift[2]))
    return im


# ---------------------------------------------------------------- the mock map builder
SPRITES = {
    "player": ("graphics/object_events/pics/people/brendan/walking.png", 16, 32),
    "lycanroc": ("graphics/pokemon/lycanroc/midnight/overworld.png", 32, 32),
    "ursaluna": ("graphics/pokemon/ursaluna/bloodmoon/overworld.png", 32, 32),
    "articuno": ("graphics/pokemon/articuno/overworld.png", 32, 32),
    "celebi": ("graphics/pokemon/celebi/overworld.png", 32, 32),
    "suicune": ("graphics/pokemon/suicune/overworld.png", 32, 32),
    "raikou": ("graphics/pokemon/raikou/overworld.png", 32, 32),
    "entei": ("graphics/pokemon/entei/overworld.png", 32, 32),
}


def sprite(key, frame=0):
    path, w, h = SPRITES[key]
    im = Image.open(os.path.join(ROOT, path))
    sub = im.crop((frame * w, 0, frame * w + w, h))
    rgba = Image.new("RGBA", sub.size, (0, 0, 0, 0))
    if sub.mode == "P":
        pal = sub.getpalette()
        p, o = sub.load(), rgba.load()
        for y in range(h):
            for x in range(w):
                i = p[x, y]
                if i:
                    o[x, y] = (pal[3 * i], pal[3 * i + 1], pal[3 * i + 2], 255)
        return rgba
    return sub.convert("RGBA")


class LairMap:
    """A mock lair: terrain chars, dual-grid sets, a 2x2-block wall with edge cells, props, sprites.

    sets: [(char, resolver(key, others) -> name, walkable)] in priority order; base: {char: (name, walkable)}.
    Names: 'P:<primary metatile>' or '<prefix>:<id>' (a Pieces cell)."""

    def __init__(self, W, H, base, sets, pieces, wall_style="swamp", fill="."):
        self.W, self.H = W, H
        self.g = [[fill] * W for _ in range(H)]
        self.base, self.sets = base, sets
        self.pieces = pieces            # {prefix: Pieces}
        self.wall = set()
        self.wall_style = wall_style
        self.props = []                 # (prefix, name, x, y)
        self.objs = []                  # (sprite, x, y, label, frame)
        self.faces = {}                 # set char -> {"face": name, "face_l": .., "face_r": ..}
        self.notes = []

    def rect(self, ch, x, y, w, h):
        for j in range(y, y + h):
            for i in range(x, x + w):
                if 0 <= i < self.W and 0 <= j < self.H:
                    self.g[j][i] = ch

    def disc(self, ch, cx, cy, rx, ry, only=None):
        for j in range(self.H):
            for i in range(self.W):
                if ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2 <= 1.0:
                    if only is None or self.g[j][i] in only:
                        self.g[j][i] = ch

    def frame(self, depth_n, depth_s, depth_w, depth_e, gap=()):
        """Walls of 2x2 blocks round the map (block coordinates): depth_<side>(k) = blocks deep at block k along
        that side; `gap` = block columns left open in the south wall (the way in)."""
        BW, BH = (self.W + 1) // 2, (self.H + 1) // 2
        b = set()
        for k in range(BW):
            for d in range(depth_n(k)):
                b.add((k, d))
            if k not in gap:
                for d in range(depth_s(k)):
                    b.add((k, BH - 1 - d))
        for k in range(BH):
            for d in range(depth_w(k)):
                b.add((d, k))
            for d in range(depth_e(k)):
                b.add((BW - 1 - d, k))
        for (bx, by) in b:
            for dy in (0, 1):
                for dx in (0, 1):
                    self.wall.add((bx * 2 + dx, by * 2 + dy))

    def prop(self, prefix, name, x, y):
        self.props.append((prefix, name, x, y))

    def obj(self, key, x, y, label, frame=0):
        self.objs.append((key, x, y, label, frame))

    def ch(self, x, y):
        return self.g[max(0, min(self.H - 1, y))][max(0, min(self.W - 1, x))]

    def resolve(self):
        W, H = self.W, self.H
        names = [[None] * W for _ in range(H)]
        walk = [[True] * W for _ in range(H)]
        problems = []
        for y in range(H):
            for x in range(W):
                if (x, y) in self.wall:
                    names[y][x] = self.wall_cell(x, y)
                    walk[y][x] = False
                    continue
                cs = [self.ch(x, y), self.ch(x + 1, y), self.ch(x, y + 1), self.ch(x + 1, y + 1)]
                n = None
                for (c, res, wk) in self.sets:
                    if c in cs:
                        bits = "".join("1" if q == c else "0" for q in cs)
                        key = CORNER_KEYS[bits]
                        others = {q for q in cs if q != c}
                        n = res(key, others)
                        if n is None:
                            problems.append((x, y, "".join(cs)))
                            n = self.base[self.g[y][x]][0]
                        walk[y][x] = wk if bits.count("1") >= 2 else self.base[self.g[y][x]][1]
                        break
                if n is None:
                    n, wk = self.base[self.g[y][x]]
                    walk[y][x] = wk
                    for c, fc in self.faces.items():
                        if c in cs:
                            continue
                        nn, ne = self.ch(x, y - 1) == c, self.ch(x + 1, y - 1) == c
                        k = "face" if nn and ne else ("face_r" if nn else ("face_l" if ne else None))
                        if k:
                            n = fc[k]
                            walk[y][x] = False
                e = self.edge_cell(x, y)
                if e:
                    plain = {v[0] for v in self.base.values()}
                    if n not in plain:
                        problems.append((x, y, "wall edge over " + str(n)))
                    n = e
                names[y][x] = n
        for (prefix, name, x, y) in self.props:
            if prefix == "P":                       # a single primary metatile (e.g. a lily pad)
                names[y][x] = "P:" + name
                walk[y][x] = False
                continue
            P = self.pieces[prefix]
            rows = P.cell_names(name)
            wl = P.items[name]["walk"]
            cv = P.items[name]["cv"]
            wset = {(i, j) for j in range(cv.ch) for i in range(cv.cw)} if wl is True else set(map(tuple, wl or []))
            for j, row in enumerate(rows):
                for i, nm in enumerate(row):
                    if 0 <= x + i < W and 0 <= y + j < H:
                        if self.edge_cell(x + i, y + j) or (x + i, y + j) in self.wall:
                            problems.append((x + i, y + j, f"prop {name} over a wall edge cell"))
                        names[y + j][x + i] = nm
                        walk[y + j][x + i] = (i, j) in wset
        self.names, self.walk, self.problems = names, walk, problems
        return names

    def ground_kind(self, x, y):
        return {"~": "water", '"': "marsh"}.get(self.g[y][x], "grass")

    def edge_cell(self, x, y):
        """The wall's edge cell for an open cell beside it (None when not beside the wall)."""
        if self.wall_style == "none":
            return None
        def Wl(i, j):
            return (i, j) in self.wall
        n, s, w, e = Wl(x, y - 1), Wl(x, y + 1), Wl(x - 1, y), Wl(x + 1, y)
        f = None
        if n and w:
            f = "in_NW"
        elif n and e:
            f = "in_NE"
        elif s and w:
            f = "in_SW"
        elif s and e:
            f = "in_SE"
        elif n:
            f = f"S{x & 1}"
        elif s:
            f = f"N{x & 1}"
        elif w:
            f = f"E{y & 1}"
        elif e:
            f = f"W{y & 1}"
        elif Wl(x - 1, y - 1):
            f = "out_NW"
        elif Wl(x + 1, y - 1):
            f = "out_NE"
        elif Wl(x - 1, y + 1):
            f = "out_SW"
        elif Wl(x + 1, y + 1):
            f = "out_SE"
        if f is None:
            return None
        if self.wall_style == "swamp":
            kind = self.ground_kind(x, y)
            if kind == "grass":
                return f"P:patch:bdg_swamp_{f}_542aa1ca"
            if f.startswith("out"):
                return None
            if f.startswith("in"):
                return f"P:bd:swamp_{f}_{kind}"
            return f"P:bd:swamp_{f[0]}_{kind}_{f[1]}"
        return f"{self.wall_style}:{f}"

    def wall_cell(self, x, y):
        if self.wall_style == "swamp":
            return f"P:bd:swamp_canopy_{x & 1}{y & 1}"
        return f"{self.wall_style}:block_{x & 1}{y & 1}"

    def cell_image(self, n):
        if n.startswith("P:"):
            return pcell(n[2:])
        prefix, mid = n.split(":", 1)
        P = self.pieces[prefix]
        if not hasattr(P, "_cells"):
            P._cells = {}
            for name in P.order:
                cv = P.items[name]["cv"]
                for j, row in enumerate(P.cell_names(name)):
                    for i, nm in enumerate(row):
                        P._cells[nm] = cv.im.crop((i * 16, j * 16, i * 16 + 16, j * 16 + 16)).convert("RGB")
        return P._cells[n]

    def render(self):
        names = self.resolve()
        img = Image.new("RGBA", (self.W * 16, self.H * 16))
        for y in range(self.H):
            for x in range(self.W):
                img.paste(self.cell_image(names[y][x]), (x * 16, y * 16))
        for (key, x, y, label, frame) in sorted(self.objs, key=lambda o: o[2]):
            s = sprite(key, frame)
            img.alpha_composite(s, (x * 16 + 8 - s.width // 2, y * 16 + 16 - s.height))
        return img

    def export(self, path, extra=None):
        dump(path, dict({"size": [self.W, self.H], "terrain": ["".join(r) for r in self.g],
                         "metatiles": [" ".join(n for n in r) for r in self.names],
                         "walk": ["".join("." if w else "#" for w in r) for r in self.walk],
                         "objects": [{"sprite": o[0], "x": o[1], "y": o[2], "label": o[3]} for o in self.objs],
                         "notes": self.notes, "autotile_conflicts": self.problems}, **(extra or {})))


def tiles_of_count(im):
    from arena_art import tiles_of, tile_key
    return len({tile_key(t) for t in tiles_of(im.convert("RGBA"))})

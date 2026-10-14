"""Compose a new Emerald-format tileset from metatiles picked out of other tilesets and image sheets.

usage (from the decomp root):
    python tools/mapgen/compose.py tools/mapgen/tilesets/recipes/<recipe>.json [...] [--register]

A recipe lists sources and what to take from each:

  * "type": "tileset" (default) - an existing tileset pair on disk. Metatile ranges keep their
    8-wide layout. Primaries may be Emerald-layout (512 tiles) or HnS-style 640-tile; "layers": 3
    reads triple-layer metatiles (pokeemerald's triple-layer patch / Great Tileset Exchange
    format) and flattens them to two layers. FRLG's 4-byte attributes are read for their layer only.
  * "type": "image" - an RGB(A) sheet of 16x16 cells (e.g. an RPG Maker / Essentials tileset at
    1x). Each listed metatile names a "bottom" cell and optionally a "top" cell drawn over the
    player; transparent pixels (alpha 0, or any "transparent" colour) show the layer beneath.

The output is a normal primary or secondary tileset (tiles.png, metatiles.bin,
metatile_attributes.bin, palettes/00-15.pal) plus <dir>.mapping.json, which records where every
source metatile ended up so map specs can refer to pieces by name.

Palettes: every source palette used by the picked metatiles becomes a colour group (image sheets
are split into groups of <=15 colours). Groups are merged until they fit the available slots
(6 primary / 7 secondary); slots that end up with more than 15 colours are reduced with weighted
k-means. A recipe's "recolor" table maps source colours to new ones before any of this, which is how
mixed sources are made to share one grass colour. A secondary reuses tiles, palettes and the
recolor table from its primary's mapping.
"""
import glob
import json
import os
import struct
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = "data/tilesets"
LAYOUTS = {"emerald": (512, 512, 6), "frlg": (640, 640, 7), "sg": (640, 1024, 7)}  # sg: the soulgold project (11-bit metatile ids)
MAX_TILES, MAX_METATILES = 512, 512
PRIMARY_SLOTS, SECONDARY_SLOTS = 6, 7
LAYER_NORMAL, LAYER_COVERED = 0, 1


# ---------------------------------------------------------------- loading helpers
_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def load_tiles(d):
    def f():
        im = Image.open(f"{d}/tiles.png")
        if im.mode != "P":
            raise SystemExit(f"{d}/tiles.png must be an indexed PNG")
        w, h = im.size
        px = im.load()
        return [tuple(px[tx * 8 + x, ty * 8 + y] & 15 for y in range(8) for x in range(8))
                for ty in range(h // 8) for tx in range(w // 8)]
    return cached(("tiles", d), f)


def load_pal(d, i):
    def f():
        try:
            lines = open(f"{d}/palettes/{i:02d}.pal").read().split("\n")[3:19]
            return [tuple(int(c) for c in l.split()) for l in lines]
        except FileNotFoundError:
            return [(0, 0, 0)] * 16
    return cached(("pal", d, i), f)


def load_u16(path):
    def f():
        b = open(path, "rb").read()
        return struct.unpack(f"<{len(b)//2}H", b)
    return cached(("u16", path), f)


def load_attrs(path, count):
    """Metatile attributes as Emerald-format u16s. FRLG's 4-byte attributes keep only their layer type
    (bits 29-30); FRLG behaviour ids differ from Emerald's, so behaviour becomes MB_NORMAL (0)."""
    def f():
        b = open(path, "rb").read()
        if count and len(b) == 4 * count:
            return tuple(((v >> 29) & 3) << 12 for v in struct.unpack(f"<{count}I", b))
        return struct.unpack(f"<{len(b)//2}H", b)
    return cached(("attr", path), f)


def gba_color(c):
    """Snap to the 5-bit-per-channel colours the GBA can show."""
    return tuple((v >> 3) << 3 for v in c)


def dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def flip(px, h, v):
    rows = [px[i * 8:i * 8 + 8] for i in range(8)]
    if v:
        rows = rows[::-1]
    if h:
        rows = [r[::-1] for r in rows]
    return tuple(c for r in rows for c in r)


def tuplify(x):
    return tuple(tuplify(i) for i in x) if isinstance(x, list) else x


def behavior_ids():
    src = open("include/constants/metatile_behaviors.h").read()
    body = src[src.index("{") + 1:src.index("}")]
    names = [l.split("//")[0].strip().rstrip(",").split("=")[0].strip() for l in body.splitlines()]
    return {n: i for i, n in enumerate(n for n in names if n.startswith("MB_"))}


# ---------------------------------------------------------------- tile model
# A tile reference is a hashable key: ("dir", tileset_dir, index) for a tile in an indexed tiles.png,
# ("img", path, index) for an 8x8 piece of an image sheet, or ("comp", lower, upper) for two
# (tile, palette, h, v) entries baked into one tile. Palette keys work the same way.
# rgb() turns (tile key, palette key) into 64 RGB values, None for transparent.

class Recolor:
    """Exact colour swaps, plus (optionally) any colour within `tolerance` of a source colour."""

    def __init__(self, table, tolerance=0):
        self.map = {gba_color(tuple(a)): gba_color(tuple(b)) for a, b in table}
        self.tol2 = tolerance * tolerance
        self.near = {}

    def __call__(self, c):
        if c in self.map:
            return self.map[c]
        if not self.tol2:
            return c
        if c not in self.near:
            best = min(self.map, key=lambda k: dist2(k, c), default=None)
            self.near[c] = self.map[best] if best is not None and dist2(best, c) <= self.tol2 else c
        return self.near[c]


LOCAL_RECOLOR = {}  # source name -> Recolor applied only to that source's pixels
SHEET_RECOLOR = {}  # image sheet path -> Recolor used instead of the recipe's (the primary's copy of a secondary's art must
                    # recolour it exactly the way the secondaries do, or the shared pieces would not be identical)


def rgb(tkey, pkey, recolor):
    if pkey[0] == "rc":
        return tuple(None if c is None else LOCAL_RECOLOR[pkey[1]](c) for c in rgb(tkey, pkey[2], recolor))
    kind = tkey[0]
    if kind == "blank":
        return (None,) * 64
    if kind == "dir":
        tiles = load_tiles(tkey[1])
        t = tiles[tkey[2]] if tkey[2] < len(tiles) else (0,) * 64
        pal = load_pal(pkey[1], pkey[2])
        return tuple(None if c == 0 else recolor(gba_color(pal[c])) for c in t)
    if kind == "img":
        rc = SHEET_RECOLOR.get(tkey[1], recolor)
        return tuple(None if c is None else rc(c) for c in ImageSource.sheets[tkey[1]].tiles[tkey[2]])
    if kind == "px":  # finished pixels (a "pixels" patch, e.g. a levee cell drawn by build.py from composed art)
        return tkey[1]
    if kind == "inner":
        # inner corner: start from the centre piece; a pixel takes the edge colour only where BOTH
        # edge pieces differ from the centre there (their fringes overlap only in the corner)
        (ct, cp, ch, cv), (at, ap, ah, av), (bt, bp, bh, bv) = tkey[1], tkey[2], tkey[3]
        grass = set(tkey[4])
        c = flip(rgb(ct, cp, recolor), ch, cv)
        a = flip(rgb(at, ap, recolor), ah, av)
        b2 = flip(rgb(bt, bp, recolor), bh, bv)
        return tuple(ai if (ai in grass and bi in grass) else ci for ci, ai, bi in zip(c, a, b2))
    if kind == "blend":
        # three-terrain transition: pixels come from B where the mask tile shows the B-side land
        # colour (e.g. mud), otherwise from A
        (at, ap, ah, av), (bt, bp, bh, bv), (mt, mp, mh, mv) = tkey[1], tkey[2], tkey[3]
        land, grass = set(tkey[4]), set(tkey[5])
        a = flip(rgb(at, ap, recolor), ah, av)
        b2 = flip(rgb(bt, bp, recolor), bh, bv)
        m = flip(rgb(mt, mp, recolor), mh, mv)
        out = []
        for ai, bi, mi in zip(a, b2, m):
            if mi in land:
                out.append(bi)          # the other land (mud/marsh) side, with its own bank
            elif mi in grass or ai not in grass:
                out.append(ai)          # grass side, or water/bank on the grass side
            else:
                out.append(mi)          # the land patch's own edge outline, drawn over grass
        return tuple(out)
    if kind == "mask":
        drop = set(tkey[2])
        return tuple(None if c in drop else c for c in rgb(tkey[1], pkey[1], recolor))
    if kind == "comp":
        (lt, lp, lh, lv), (ut, up, uh, uv) = tkey[1], tkey[2]
        lo = flip(rgb(lt, lp, recolor), lh, lv)
        hi = flip(rgb(ut, up, recolor), uh, uv)
        return tuple(b if b is not None else a for a, b in zip(lo, hi))
    raise ValueError(tkey)


def is_blank(entry, recolor):
    return all(c is None for c in rgb(entry[0], entry[1], recolor))


# ---------------------------------------------------------------- sources
class TilesetSource:
    """Metatiles from tileset folders on disk. Entries are (tile key, palette key, hflip, vflip)."""

    def __init__(self, spec, recolor):
        self.name = spec["name"]
        root = spec.get("root", T)
        self.pdir = f"{root}/primary/{spec['primary']}" if "/" not in spec["primary"] else spec["primary"]
        sec = spec.get("secondary")
        self.sdir = (sec if sec and "/" in sec else f"{root}/secondary/{sec}") if sec else None
        self.nt, self.nm, self.np = LAYOUTS[spec.get("layout", "emerald")]
        # "layers" describes the secondary; the primary is read as "primary_layers" (default 2)
        self.layers = spec.get("layers", 2)
        self.dir_layers = {self.pdir: spec.get("primary_layers", 2), self.sdir: self.layers}
        self.recolor = recolor
        if spec.get("recolor"):
            LOCAL_RECOLOR[self.name] = Recolor(spec["recolor"])
        for d in (self.pdir, self.sdir):
            if d and os.path.exists(f"{d}/metatile_attributes.bin"):
                n = os.path.getsize(f"{d}/metatiles.bin") / (2 * 4 * self.dir_layers[d])
                size = os.path.getsize(f"{d}/metatile_attributes.bin") / n if n else 2
                if size not in (2, 4):
                    raise SystemExit(f"{d}: unknown metatile attribute format ({size} bytes)")

    def entry(self, e):
        tid, p = e & 0x3FF, e >> 12
        tkey = ("dir", self.pdir, tid) if tid < self.nt else ("dir", self.sdir, tid - self.nt)
        pkey = ("dir", self.pdir, p) if p < self.np else ("dir", self.sdir, p)
        if self.name in LOCAL_RECOLOR:
            pkey = ("rc", self.name, pkey)
        return (tkey, pkey, (e >> 10) & 1, (e >> 11) & 1)

    def picks(self, spec):
        for lo, hi in spec.get("ranges", []):
            lo, hi = int(lo, 16), int(hi, 16)
            for mid in range(lo, hi + 1):
                yield f"{mid:03X}", self.metatile(mid)
            yield None, None  # end of range: pad to the next row of 8
        if spec.get("ids"):
            for mid in spec["ids"]:
                yield mid.upper(), self.metatile(int(mid, 16))
            yield None, None

    def metatile(self, mid):
        """(8 entries, attribute) for an absolute metatile id, or None past the end."""
        d, j = (self.pdir, mid) if mid < self.nm else (self.sdir, mid - self.nm)
        layers = self.dir_layers[d]
        n = 4 * layers
        mts, attrs = load_u16(f"{d}/metatiles.bin"), load_attrs(f"{d}/metatile_attributes.bin", len(load_u16(f"{d}/metatiles.bin")) // n)
        if j * n >= len(mts):
            return None
        es = [self.entry(e) for e in mts[j * n:j * n + n]]
        attr = attrs[j]
        if layers == 2:
            return es, attr
        return self.flatten(es, attr)

    def flatten(self, es, attr):
        """Triple-layer (bottom, middle, top) -> two layers.

        Middle sits below the player and top above it. When no quadrant uses the top layer the
        metatile becomes COVERED (both layers below the player); when the middle is empty it is
        NORMAL; otherwise bottom and middle are baked into new tiles and top stays on top."""
        bot, mid, top = es[0:4], es[4:8], es[8:12]
        blank = lambda layer: all(is_blank(e, self.recolor) for e in layer)
        behavior = attr & 0xFF
        if blank(top):
            return bot + mid, behavior | (LAYER_COVERED << 12)
        if blank(mid):
            return bot + top, behavior | (LAYER_NORMAL << 12)
        lower = []
        for b, m in zip(bot, mid):
            if is_blank(m, self.recolor):
                lower.append(b)
            else:
                lower.append((("comp", b, m), ("comp", b[1], m[1]), 0, 0))
        return lower + top, behavior | (LAYER_NORMAL << 12)


class ImageSource:
    """Metatiles cut from an image sheet of 16x16 cells."""
    sheets = {}

    def __init__(self, spec, recolor):
        self.name = spec["name"]
        self.path = spec["image"]
        self.fewest_groups = spec.get("group_rule") == "fewest"
        self.recolor = recolor
        self.behaviors = behavior_ids()
        if self.path not in ImageSource.sheets:
            ImageSource.sheets[self.path] = self
            im = Image.open(self.path).convert("RGBA")
            keys = {tuple(c) for c in spec.get("transparent", [])}
            w, h = im.size
            px = im.load()
            self.cols = w // 8
            self.tiles = []
            for ty in range(h // 8):
                for tx in range(w // 8):
                    t = []
                    for y in range(8):
                        for x in range(8):
                            r, g, b, a = px[tx * 8 + x, ty * 8 + y]
                            t.append(None if a < 128 or (r, g, b) in keys else gba_color((r, g, b)))
                    self.tiles.append(tuple(t))
        else:
            self.__dict__.update({k: v for k, v in ImageSource.sheets[self.path].__dict__.items()
                                  if k in ("cols", "tiles")})
        self.groups = None

    def cell_entries(self, cell):
        c, r = cell
        base = (r * 2) * self.cols + c * 2
        return [base, base + 1, base + self.cols, base + self.cols + 1]

    def picks(self, spec):
        mts = spec["metatiles"]
        # split the colours of every tile we use into groups of <= 15 so each tile fits one palette
        used = set()
        for m in mts:
            for c, r, q in m.get("quads", []):
                used.add(self.cell_entries([c, r])[q])
            for k in ("bottom", "top"):
                cells = m.get(k)
                if cells:
                    for cell in ([cells] if isinstance(cells[0], int) else cells):
                        used.update(self.cell_entries(cell))
        self.group_of = self.split_groups(sorted(used))
        for m in mts:
            if m.get("quads"):
                es = [self.make(self.cell_entries([c, r])[q]) for c, r, q in m["quads"]]
            else:
                es = self.layer(m["bottom"])
            if m.get("top"):
                es += self.layer(m["top"])
                layer = LAYER_NORMAL if m.get("layer", "normal") == "normal" else LAYER_COVERED
            else:
                es += [self.make(None)] * 4
                layer = LAYER_COVERED
            beh = self.behaviors[m.get("behavior", "MB_NORMAL")]
            yield m["id"], (es, beh | (layer << 12))
        yield None, None

    def make(self, t):
        if t is None:
            return (("blank",), ("blank",), 0, 0)
        return (("img", self.path, t), ("img", self.path, self.group_of[t]), 0, 0)

    def layer(self, cells):
        """A layer from one cell, or several cells stacked (later ones drawn over earlier ones)."""
        if isinstance(cells[0], int):
            cells = [cells]
        layer = [self.make(t) for t in self.cell_entries(cells[0])]
        for cell in cells[1:]:
            over = [self.make(t) for t in self.cell_entries(cell)]
            layer = [(("comp", a, b), ("comp", a[1], b[1]), 0, 0) for a, b in zip(layer, over)]
        return layer

    def split_groups(self, tiles):
        """Tile -> colour group (<= 15 colours each), most colourful tiles first, each joining the group with the
        smallest union. With "group_rule": "fewest" on the source, also try joining the group it adds fewest colours
        to and keep whichever needs fewer groups (helps sheets with many small objects; can hurt others' packing)."""
        cols = {t: {c for c in self.tiles[t] if c is not None} for t in tiles}
        best_out, best_n = None, None
        rules = [lambda g, u: u] + ([lambda g, u: (u - len(g), u)] if self.fewest_groups else [])
        for rule in rules:
            groups, out = [], {}
            for t in sorted(tiles, key=lambda t: -len(cols[t])):
                best = None
                for i, g in enumerate(groups):
                    u = len(g | cols[t])
                    if u <= 15 and (best is None or rule(g, u) < best[0]):
                        best = (rule(g, u), i)
                if best is None:
                    groups.append(set(cols[t]))
                    out[t] = len(groups) - 1
                else:
                    groups[best[1]] |= cols[t]
                    out[t] = best[1]
            if best_n is None or len(groups) < best_n:
                best_out, best_n = out, len(groups)
        return best_out


def make_source(spec, recolor):
    return ImageSource(spec, recolor) if spec.get("type") == "image" else TilesetSource(spec, recolor)


# ---------------------------------------------------------------- palette packing
KEEP_COLORS = set()  # colours palette reduction must keep exactly (e.g. the shared grass)


def kmeans(weights, k):
    pts = list(weights)
    if len(pts) <= k:
        return pts
    fixed = [c for c in pts if c in KEEP_COLORS][:k]
    cent = fixed or [max(pts, key=lambda c: weights[c])]
    while len(cent) < k:
        cent.append(max(pts, key=lambda c: min(dist2(c, q) for q in cent)))
    for _ in range(25):
        groups = [[] for _ in cent]
        for c in pts:
            groups[min(range(len(cent)), key=lambda i: dist2(c, cent[i]))].append(c)
        new = []
        for i, g in enumerate(groups):
            if not g or cent[i] in fixed:
                new.append(cent[i])
                continue
            tw = sum(weights[c] for c in g)
            new.append(gba_color(tuple(round(sum(c[j] * weights[c] for c in g) / tw) for j in range(3))))
        if new == cent:
            break
        cent = new
    return list(dict.fromkeys(cent))


def merge_cost(a, b):
    u = set(a) | set(b)
    if len(u) <= 15:
        return len(u) - 16  # negative: free merge, prefer the most overlap
    w = {c: a.get(c, 0) + b.get(c, 0) for c in u}
    return sum(sorted(w.values())[:len(u) - 15])


def pack_first_fit(groups, slots):
    """First-fit decreasing: the most colourful groups first, each into the slot it adds fewest new colours
    to. Returns clusters like pack_palettes builds, or None if some group fits nowhere."""
    clusters = []
    for k, w in sorted(groups.items(), key=lambda kw: -len(kw[1])):
        fits = [(len(set(w) - set(cw)), -len(set(w) & set(cw)), i) for i, (_, cw) in enumerate(clusters)
                if len(set(w) | set(cw)) <= 15]
        if fits:
            i = min(fits)[2]
            for c, n in w.items():
                clusters[i][1][c] = clusters[i][1].get(c, 0) + n
            clusters[i][0].append(k)
        elif len(clusters) < slots:
            clusters.append(([k], dict(w)))
        else:
            return None
    return clusters


def pack_tiles(groups, slots, tries=60):
    """groups: {colour set key: {color: weight}}, one per distinct set of colours an 8x8 tile uses. Packs the
    sets into palette slots of 15 (first fit, fewest new colours, the most colourful first), trying many
    orders and keeping the one that overflows least; only an overflowing slot is reduced (kmeans), so a
    tileset that can be packed exactly keeps every colour of its art. -> like pack_palettes."""
    import random
    keys = list(groups)
    sets = {k: set(groups[k]) for k in keys}
    rnd = random.Random(7)
    best = None
    for t in range(tries):
        ks = keys[:]
        if t:
            rnd.shuffle(ks)
        ks.sort(key=lambda k: -len(sets[k]))  # stable: equal sizes keep the shuffled order
        clusters = []  # [colour set, [keys]]
        for k in ks:
            s = sets[k]
            fits = [(len(s - cs), -len(s & cs), i) for i, (cs, _) in enumerate(clusters) if len(s | cs) <= 15]
            if fits:
                i = min(fits)[2]
            elif len(clusters) < slots:
                clusters.append([set(), []])
                i = len(clusters) - 1
            else:  # fits nowhere: where it overflows least
                i = min(range(len(clusters)), key=lambda j: len(s | clusters[j][0]))
            clusters[i][0] |= s
            clusters[i][1].append(k)
        score = sum(max(0, len(cs) - 15) for cs, _ in clusters)
        if best is None or score < best[0]:
            best = (score, clusters)
        if score == 0:
            break
    pals, where, report = [], {}, []
    for cs, ks in best[1]:
        w = {}
        for k in ks:
            for c, n in groups[k].items():
                w[c] = w.get(c, 0) + n
        colors = kmeans(w, 15) if len(w) > 15 else sorted(w, key=lambda c: -w[c])
        if len(w) > 15:
            worst = max(min(dist2(c, q) for q in colors) for c in w) ** 0.5
            report.append(f"  slot {len(pals)}: {len(w)} colours reduced to 15 (worst shift {worst:.0f})")
        for k in ks:
            where[k] = len(pals)
        pals.append(colors)
    return pals, where, report


def pack_palettes(groups, slots):
    """groups: {key: {color: weight}} -> (list of slot palettes, {key: slot index}, report lines)."""
    clusters = [([k], dict(w)) for k, w in groups.items()]
    while len(clusters) > slots:
        best = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                c = merge_cost(clusters[i][1], clusters[j][1])
                if best is None or c < best[0]:
                    best = (c, i, j)
        _, i, j = best
        keys = clusters[i][0] + clusters[j][0]
        w = dict(clusters[i][1])
        for c, n in clusters[j][1].items():
            w[c] = w.get(c, 0) + n
        clusters[j:j + 1] = []
        clusters[i] = (keys, w)
    if any(len(w) > 15 for _, w in clusters):  # the greedy merge overflowed: try first-fit, which often packs exactly
        clusters = pack_first_fit(groups, slots) or clusters
    pals, where, report = [], {}, []
    for keys, w in clusters:
        colors = kmeans(w, 15) if len(w) > 15 else sorted(w, key=lambda c: -w[c])
        if len(w) > 15:
            worst = max(min(dist2(c, q) for q in colors) for c in w) ** 0.5
            report.append(f"  slot {len(pals)}: {len(w)} colours reduced to 15 (worst shift {worst:.0f})")
        for k in keys:
            where[k] = len(pals)
        pals.append(colors)
    return pals, where, report


# ---------------------------------------------------------------- palette v2 (recipe "palette": "v2")
# Every 8x8 tile is placed by its own colours, weighted by how many pixels the built maps actually show:
#   1. near-duplicate colours (<= V2_MERGE apart, never in the same tile: the same shade from different sources)
#      are treated as one while packing, so the packer sees which tiles really need separate room;
#   2. the merged colour sets are packed into the slots (simulated annealing on overflow, several seeds);
#   3. alternate: each slot picks its <= 15 colours (k-medoids over its own colours plus midpoints of near pairs,
#      cost = map pixels x shift^2, steep past V2_SOFT), then every tile moves to the slot or primary palette
#      that draws it best;
#   4. local search with the exact cost: move a tile group to another slot (both slots re-pick their colours) or
#      to a primary palette whenever that lowers the total. The seed with the lowest total cost wins.
# Opt-in "v2_backdrop": true makes the backdrop colour free in bottom-layer tiles (index 0 there shows palette 0,
# colour 0, the swamp grass). Off by default: the DNS tint leaves colour 0 untinted, so it would glow at night.
# KEEP_COLORS weigh V2_KEEP_MULT times as much instead of being pinned into every slot they appear in.
V2_MERGE, V2_SOFT, V2_PENALTY, V2_KEEP_MULT = 12, 12.0, 300.0, 10.0
V2_GRASS_MULT = 10   # extra weight on the backdrop grass colour (on top of KEEP_COLORS' multiplier)
V2_FLOOR = 3000      # a colour the maps show on >= 20 pixels weighs at least this much (small details still count)
V2_UNPLACED = 0.05   # weight per pixel of a tile no map places (so it still gets a sensible colour)
V2_NEW = 16          # placements assumed for a piece the previous compose didn't have (maps not built with it yet)


def map_counts(r, recipe_path):
    """{metatile name: placements} over the built maps that use this tileset, read through the previous compose's
    mapping file (the one those maps were built against); every name in that file is listed, 0 if unplaced.
    {} when there are no maps or no mapping yet."""
    mp = os.path.join(os.path.dirname(recipe_path), "..", f"{r['dir']}.mapping.json")
    if not os.path.exists(mp) or not os.path.exists("data/layouts/layouts.json"):
        return {}
    inv = {v: k for k, v in json.load(open(mp))["metatiles"].items()}
    cnt, maps = {n: 0 for n in inv.values()}, 0
    for l in json.load(open("data/layouts/layouts.json"))["layouts"]:
        if not l or l.get("secondary_tileset" if r["kind"] == "secondary" else "primary_tileset") != r["symbol"]:
            continue
        if not os.path.exists(l["blockdata_filepath"]):
            continue
        maps += 1
        b = open(l["blockdata_filepath"], "rb").read()
        for v in struct.unpack(f"<{len(b) // 2}H", b):
            n = inv.get(v & 0x3FF)
            if n:
                cnt[n] += 1
    return cnt if maps else {}


def v2_items(picked, names, counts, reuse, recolor):
    """{(tkey, pkey): ({colour: weight}, bottom_only)} for every tile that needs a palette."""
    name_of = {i: n for n, i in names.items()}
    placed = bool(counts)
    items, mapw = {}, {}
    for i, p in enumerate(picked):
        if not p:
            continue
        n = counts.get(name_of.get(i), V2_NEW) if placed else 10
        for li, (tkey, pkey, _, _) in enumerate(p[0]):
            if (tkey, pkey) in reuse:
                continue
            px = rgb(tkey, pkey, recolor)
            if all(c is None for c in px):
                continue
            k = (tkey, pkey)
            if k not in items:
                items[k] = ({}, True)
                mapw[k] = {}
                for c in px:
                    if c is not None:
                        items[k][0][c] = items[k][0].get(c, 0) + V2_UNPLACED
            if li >= 4:
                items[k] = (items[k][0], False)
            for c in px:
                if c is not None:
                    mapw[k][c] = mapw[k].get(c, 0) + n
    cover = {}
    for mw in mapw.values():
        for c, m in mw.items():
            cover[c] = cover.get(c, 0) + m
    for k, (w, _) in items.items():
        for c, m in mapw[k].items():
            w[c] += m * max(1.0, V2_FLOOR / cover[c]) if cover[c] >= 20 else m
    return items


def _v2_cost(dd):
    import numpy as np
    return dd + V2_PENALTY * np.maximum(0.0, np.sqrt(dd) - V2_SOFT) ** 2


def _v2_merge(sets, forced):
    tot, cooc = {}, {}
    for cols in sets:
        for c, w in cols.items():
            tot[c] = tot.get(c, 0) + w
            cooc.setdefault(c, set()).update(cols)
    rep, members = {}, {}
    for c in sorted(tot, key=lambda c: (c not in forced, -tot[c], c)):
        if c not in forced:
            near = [q for q in members if dist2(c, q) <= V2_MERGE ** 2 and not any(m in cooc[c] for m in members[q])]
            if near:
                q = min(near, key=lambda q: (dist2(c, q), -tot[q], q))
                rep[c] = q
                members[q].append(c)
                continue
        rep[c] = c
        members[c] = [c]
    return rep


def _v2_anneal(sets, slots, seed, iters=300000, cap=15):
    """Slot per colour set, minimising overflow past `cap` (then total colours)."""
    import math
    import random
    rnd = random.Random(seed)
    sets = [sorted(s) for s in sets]
    n = len(sets)
    asg = [rnd.randrange(slots) for _ in range(n)]
    if n == 0 or slots < 2:
        return asg
    cnt = [dict() for _ in range(slots)]
    for i, k in enumerate(asg):
        for c in sets[i]:
            cnt[k][c] = cnt[k].get(c, 0) + 1
    f = lambda sz: max(0, sz - cap) * 10 + sz * 0.1
    total = sum(f(len(c)) for c in cnt)
    best = (total, asg[:])
    t0, t1 = 3.0, 0.05
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / iters)
        i = rnd.randrange(n)
        a = asg[i]
        b = rnd.randrange(slots - 1)
        b += b >= a
        s, ca, cb = sets[i], cnt[a], cnt[b]
        la = len(ca) - sum(1 for c in s if ca[c] == 1)
        lb = len(cb) + sum(1 for c in s if c not in cb)
        delta = f(la) + f(lb) - f(len(ca)) - f(len(cb))
        if delta <= 0 or rnd.random() < math.exp(-delta / temp):
            for c in s:
                if ca[c] == 1:
                    del ca[c]
                else:
                    ca[c] -= 1
                cb[c] = cb.get(c, 0) + 1
            asg[i] = b
            total += delta
            if total < best[0] - 1e-9:
                best = (total, asg[:])
    return best[1]


def _v2_choose(weights, k=15, with_cost=False):
    """<= k colours for one slot: exact when they fit, else k-medoids (greedy + swaps) over the slot's colours and
    the GBA-snapped midpoints of near pairs. with_cost: (colours, cost)."""
    import numpy as np
    cols = sorted(weights, key=lambda c: (-weights[c], c))
    if len(cols) <= k:
        return (cols, 0.0) if with_cost else cols
    Ci = np.array(cols, dtype=int)
    ii, jj = np.nonzero(np.triu(((Ci[:, None, :] - Ci[None, :, :]) ** 2).sum(-1) <= 40 * 40, 1))
    pair = Ci[ii] + Ci[jj]
    mids = np.concatenate([(pair // 16) * 8, ((pair + 8) // 16) * 8])
    cand = list(dict.fromkeys(cols + [tuple(int(v) for v in m) for m in mids]))
    C, K = np.array(cols, dtype=float), np.array(cand, dtype=float)
    W = np.array([weights[c] * (V2_KEEP_MULT if c in KEEP_COLORS else 1) for c in cols])
    D = _v2_cost(((C[:, None, :] - K[None, :, :]) ** 2).sum(-1)) * W[:, None]
    S, cur = [], np.full(len(cols), np.inf)
    while len(S) < k:
        tot = np.minimum(cur[:, None], D).sum(0)
        tot[S] = np.inf
        j = int(tot.argmin())
        S.append(j)
        cur = np.minimum(cur, D[:, j])
    base = cur.sum()
    improved = True
    while improved:
        improved = False
        for si in range(len(S)):
            rest = D[:, [S[x] for x in range(len(S)) if x != si]].min(1)
            tot = np.minimum(rest[:, None], D).sum(0)
            tot[S] = np.inf
            j = int(tot.argmin())
            if tot[j] < base - 1e-6:
                S[si], base, improved = j, tot[j], True
    return ([cand[j] for j in S], float(base)) if with_cost else [cand[j] for j in S]


def _v2_unit_cost(cols, pal, bottom, bd):
    import numpy as np
    if not cols:
        return 0.0
    P = np.array(list(pal) + ([bd] if bottom else []) or [(999, 999, 999)], dtype=float)
    C = np.array(list(cols), dtype=float)
    W = np.array([w * (V2_KEEP_MULT if c in KEEP_COLORS else 1) for c, w in cols.items()])
    return float((_v2_cost(((C[:, None, :] - P[None, :, :]) ** 2).sum(-1).min(1)) * W).sum())


def _v2_refine(units, where, base_pals, slots, bd, rounds=8):
    def slot_weights():
        W = [dict() for _ in range(slots)]
        for u, (kind, k) in zip(units, where):
            if kind == "s":
                for c, w in u["cols"].items():
                    W[k][c] = W[k].get(c, 0) + w
        return W
    for _ in range(rounds):
        pals = [_v2_choose(w) for w in slot_weights()]
        cands = [("p", k, p) for k, p in enumerate(base_pals)] + [("s", k, p) for k, p in enumerate(pals) if p]
        changed = 0
        for ui, u in enumerate(units):
            costs = {(kind, k): _v2_unit_cost(u["cols"], p, u["bottom"], bd) for kind, k, p in cands}
            best = min(costs, key=lambda kk: (costs[kk], kk))
            if costs[best] < costs.get(where[ui], float("inf")) - 1e-6:
                where[ui] = best
                changed += 1
        if not changed:
            break
    pals = [_v2_choose(w) for w in slot_weights()]
    cost = sum(_v2_unit_cost(u["cols"], base_pals[k] if kind == "p" else pals[k], u["bottom"], bd)
               for u, (kind, k) in zip(units, where))
    return pals, where, cost


def _v2_local(units, where, base_pals, slots, bd, passes=6, ndest=3):
    """Exact-cost local search: move one tile group at a time to the primary palette or one of the `ndest` slots
    sharing most of its colours (re-picking both slots' colours) while that lowers the total cost."""
    def shifted(W, cols, sign):
        W = dict(W)
        for c, x in cols.items():
            v = W.get(c, 0) + sign * x
            if sign < 0 and v <= 1e-9:
                W.pop(c, None)
            else:
                W[c] = v
        return W
    W = [dict() for _ in range(slots)]
    for u, (kind, k) in zip(units, where):
        if kind == "s":
            W[k] = shifted(W[k], u["cols"], 1)
    sc = [_v2_choose(w, with_cost=True) for w in W]
    for _ in range(passes):
        moved = 0
        for ui, u in enumerate(units):
            if not u["cols"]:
                continue
            kind, a = where[ui]
            if kind == "s":
                Wa = shifted(W[a], u["cols"], -1)
                pa = _v2_choose(Wa, with_cost=True)
                gain = sc[a][1] - pa[1]
            else:
                gain = _v2_unit_cost(u["cols"], base_pals[a], u["bottom"], bd)
            best = None
            for k, p in enumerate(base_pals):
                if (kind, a) != ("p", k):
                    d = _v2_unit_cost(u["cols"], p, u["bottom"], bd) - gain
                    if best is None or d < best[0]:
                        best = (d, ("p", k), None)
            near = sorted((k for k in range(slots) if (kind, a) != ("s", k)),
                          key=lambda k: (-sum(1 for c in u["cols"] if c in W[k]), k))[:ndest]
            for k in near:
                Wb = shifted(W[k], u["cols"], 1)
                pb = _v2_choose(Wb, with_cost=True)
                d = pb[1] - sc[k][1] - gain
                if best is None or d < best[0]:
                    best = (d, ("s", k), (Wb, pb))
            if best and best[0] < -1e-6 * max(1.0, abs(gain)):
                if kind == "s":
                    W[a], sc[a] = Wa, pa
                if best[1][0] == "s":
                    W[best[1][1]], sc[best[1][1]] = best[2]
                where[ui] = best[1]
                moved += 1
        if not moved:
            break
    pals = [p for p, _ in sc]
    cost = sum(_v2_unit_cost(u["cols"], base_pals[k] if kind == "p" else pals[k], u["bottom"], bd)
               for u, (kind, k) in zip(units, where))
    return pals, where, cost


def pack_v2(items, base_pals, slots, bd, seeds=3):
    """items: {key: ({colour: weight}, bottom_only)} -> (slot palettes, {key: slot}, {key: primary slot}, report)."""
    rep = _v2_merge([w for w, _ in items.values()], set(KEEP_COLORS) | {bd})
    units, order = {}, []
    for key, (cols, bottom) in items.items():
        uk = (frozenset(rep[c] for c in cols if not (bottom and rep[c] == bd)), bottom)
        if uk not in units:
            units[uk] = {"cols": {}, "keys": [], "bottom": bottom}
            order.append(uk)
        u = units[uk]
        u["keys"].append(key)
        for c, w in cols.items():
            if not (bottom and c == bd):
                u["cols"][c] = u["cols"].get(c, 0) + w
    U = [units[uk] for uk in order]
    start = [None] * len(U)
    groups = {}  # merged colour set -> units that need a secondary slot
    for ui, uk in enumerate(order):
        fit = [k for k, p in enumerate(base_pals) if uk[0] <= set(p)] if uk[0] else [0]
        if fit:
            start[ui] = ("p", fit[0])
        else:
            groups.setdefault(uk[0], []).append(ui)
    sets = list(groups)
    maximal = [s for s in sets if not any(s < t for t in sets)]
    best = None
    for seed in range(seeds):
        slot_of = dict(zip(maximal, _v2_anneal(maximal, slots, seed)))
        for s in sets:
            if s not in slot_of:
                slot_of[s] = next(slot_of[t] for t in maximal if s < t)
        where = list(start)
        for s, uis in groups.items():
            for ui in uis:
                where[ui] = ("s", slot_of[s])
        pals, where, cost = _v2_refine(U, where, base_pals, slots, bd)
        pals, where, cost = _v2_local(U, where, base_pals, slots, bd)
        if best is None or cost < best[2]:
            best = (pals, where, cost)
    pals, where, _ = best
    sec, prim = {}, {}
    for u, (kind, k) in zip(U, where):
        for key in u["keys"]:
            (prim if kind == "p" else sec)[key] = k
    # report: what each slot had to give up, by the weight it carries
    report = []
    for k, p in enumerate(pals):
        W = {}
        for u, (kind, kk) in zip(U, where):
            if kind == "s" and kk == k:
                for c, w in u["cols"].items():
                    W[c] = W.get(c, 0) + w
        if len(W) > 15:
            shifts = [(min(dist2(c, q) for q in p) ** 0.5, c) for c in W if W[c] >= V2_FLOOR]
            worst = max(shifts, default=(0, None))[0]
            report.append(f"  slot {k}: {len(W)} colours in 15 (worst shift on a colour the maps show: {worst:.0f})")
    n_in = len({c for cols, _ in items.values() for c in cols})
    report.insert(0, f"  palette v2: {n_in} colours, {len(set(rep.values()))} after near-duplicate merge; "
                     f"{len(prim)} tiles drawn with primary palettes")
    return pals, sec, prim, report


# ---------------------------------------------------------------- tiles
def flips(px):
    return {(h, v): flip(px, h, v) for h in (0, 1) for v in (0, 1)}


class TileBank:
    def __init__(self, reserve_blank):
        self.tiles, self.index = [], {}
        if reserve_blank:
            self.add((0,) * 64)

    def add(self, px):
        """Returns (index, hflip, vflip) for pixel indices, deduplicating flipped copies."""
        for (h, v), f in flips(px).items():
            if f in self.index:
                return self.index[f], h, v
        self.tiles.append(px)
        self.index[px] = len(self.tiles) - 1
        return len(self.tiles) - 1, 0, 0


def demand_only(r, picked, names):
    """A "demand" tileset keeps only the pieces its maps place (build.py writes them to tilesets/uses/<dir>/,
    one file per layout), so a town's set doesn't carry the whole kit. Everything is still cut, so patches can
    be made from pieces that aren't kept. Until every layout using the tileset has been built once, nothing is
    left out (a partial rebuild must not starve the maps it didn't build)."""
    import glob
    ud = os.path.join(HERE, "tilesets", "uses", r["dir"])
    layouts = [l for l in json.load(open("data/layouts/layouts.json"))["layouts"]
               if l and l.get("secondary_tileset") == r["symbol"]
               and l.get("width", 2) * l.get("height", 2) > 1]  # 1x1 stub layouts (stripped Hoenn rooms) place nothing
    have = {os.path.basename(f)[:-5]: f for f in glob.glob(os.path.join(ud, "*.json"))}
    missing = [l["id"] for l in layouts if l["id"] not in have]
    if not layouts or missing:
        print(f"  demand: keeping everything ({len(missing)} of {len(layouts)} layouts not built yet: "
              f"{', '.join(missing[:4])})")
        return picked, names
    used = set()
    for l in layouts:
        used |= set(json.load(open(have[l["id"]])))
    keep = sorted({i for n, i in names.items() if n in used})
    remap = {i: k for k, i in enumerate(keep)}
    before = sum(1 for p in picked if p)
    print(f"  demand: {len(keep)} of {before} pieces placed by its {len(layouts)} maps; the rest left out")
    return [picked[i] for i in keep], {n: remap[i] for n, i in names.items() if i in remap}



# ---------------------------------------------------------------- shared pieces (primary <-> secondaries)
def tile_hash(px):
    import hashlib
    return hashlib.sha1(repr(px).encode()).hexdigest()[:20]


def piece_sig(p, recolor):
    """What a metatile looks like (both layers' pixels after recolouring and flipping, and its attribute): two pieces
    with the same signature are the same piece, wherever each tileset keeps its tiles."""
    import hashlib
    h = hashlib.sha1()
    for tkey, pkey, hf, vf in p[0]:
        px = rgb(tkey, pkey, recolor)
        h.update(repr(None if all(c is None for c in px) else flip(px, hf, vf)).encode())
    h.update(repr(p[1]).encode())
    return h.hexdigest()[:20]


def snake(sym):
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", sym.replace("gTileset_", "")).lower()


def primary_counts(r, recipe_path):
    """{name: placements} for the primary: every layout using it, each metatile id read through the primary's previous
    mapping (ids < 512) or the layout's own secondary mapping (the shared terrain still lives there before the first
    compose that moves it). Names the maps never place get 0; {} when nothing is known."""
    tdir = os.path.join(os.path.dirname(recipe_path), "..")
    if not os.path.exists("data/layouts/layouts.json"):
        return {}
    own = os.path.join(tdir, f"{r['dir']}.mapping.json")
    inv_p = {v: k for k, v in json.load(open(own))["metatiles"].items()} if os.path.exists(own) else {}
    cnt, maps, sec_inv = {}, 0, {}
    for l in json.load(open("data/layouts/layouts.json"))["layouts"]:
        if not l or l.get("primary_tileset") != r["symbol"] or not os.path.exists(l["blockdata_filepath"]):
            continue
        sp = os.path.join(tdir, snake(l["secondary_tileset"]) + ".mapping.json")
        if sp not in sec_inv:
            sec_inv[sp] = ({v: k for k, v in json.load(open(sp))["metatiles"].items()} if os.path.exists(sp) else {})
        inv_s = sec_inv[sp]
        maps += 1
        b = open(l["blockdata_filepath"], "rb").read()
        for v in struct.unpack(f"<{len(b) // 2}H", b):
            mid = v & 0x3FF
            n = inv_p.get(mid) if mid < MAX_METATILES else inv_s.get(mid)
            if n:
                cnt[n] = cnt.get(n, 0) + 1
    if not maps:
        return {}
    for n in list(inv_p.values()) + [n for inv in sec_inv.values() for n in inv.values()]:
        cnt.setdefault(n, 0)
    return cnt


def sparse_primary(r, recipe_path, picked, names):
    """The primary keeps only what the maps use, at the SAME metatile ids as before: the HnS Johto metatiles named in the
    keep file stay where they were (so hex ids in tileset configs, specs and generators keep working), every other Johto
    slot is left empty, and the shared terrain (recipe "shared": name regexes) fills the freed slots first."""
    import re
    keep = json.load(open(os.path.join(os.path.dirname(recipe_path), "..", r["keep_file"])))
    kept = {int(x, 16) for x in keep["johto"]}
    n_slots = max(int(n.split(":")[1], 16) for n in names if n.startswith("johto:")) + 1
    out = [None] * n_slots
    new_names = {}
    for n, i in names.items():
        if n.startswith("johto:"):
            j = int(n.split(":")[1], 16)
            if j in kept and picked[i]:
                out[j] = picked[i]
                new_names[n] = j
    holes = [j for j in range(n_slots) if out[j] is None]
    pats = [re.compile(p) for p in r.get("shared", [])]
    unplaced = set(r.get("drop_names", ()))    # seams review: shared pieces no built map places and no secondary needs a tile of (primary_seam_prune.py lists them)
    dropped = 0
    for n, i in names.items():
        if n.startswith("johto:") or not picked[i] or not any(p.search(n) for p in pats):
            continue
        if n in unplaced and not n.startswith(tuple(r.get("keep_names", ()))):
            dropped += 1
            continue
        if holes:
            j = holes.pop(0)
            out[j] = picked[i]
        else:
            out.append(picked[i])
            j = len(out) - 1
        new_names[n] = j
    missing = [x for x in keep["johto"] if f"johto:{x}" not in new_names]
    if missing:
        raise SystemExit(f"keep file names Johto metatiles that do not exist: {missing[:8]}")
    if dropped:
        print(f"  primary: {dropped} shared pieces no map places were left out")
    print(f"  primary: {sum(1 for x in out if x)} metatiles kept ({len(kept)} Johto at their old ids, "
          f"{len(new_names) - len(kept)} shared pieces), {len(holes)} free slots below id {n_slots}")
    return out, new_names


def drop_shared(picked, names, base, recolor):
    """A secondary does not carry a piece the primary already has, if it is the same piece (same pixels, same attribute):
    the maps reach it through the primary's mapping. A piece with the primary's name but another look stays here
    (and shadows the primary's name for this tileset's maps)."""
    sig, drop, differ = base.get("sig") or {}, set(), []
    for n, i in names.items():
        if n in sig and picked[i]:
            (drop.add(i) if piece_sig(picked[i], recolor) == sig[n] else differ.append(n))
    keep = [i for i in range(len(picked)) if i not in drop]
    remap = {i: k for k, i in enumerate(keep)}
    print(f"  shared with the primary: {len(drop)} pieces dropped" + (f"; {len(differ)} differ and stay: "
          f"{', '.join(sorted(differ)[:5])}{'...' if len(differ) > 5 else ''}" if differ else ""))
    return [picked[i] for i in keep], {n: remap[i] for n, i in names.items() if i in remap}


# ---------------------------------------------------------------- compose
def compose(recipe_path):
    r = json.load(open(recipe_path))
    kind = r["kind"]
    secondary = kind == "secondary"
    out_dir = f"{T}/{kind}/{r['dir']}"
    base = None
    if secondary:
        base = json.load(open(os.path.join(os.path.dirname(recipe_path), "..", r["primary_mapping"])))
    recolor = Recolor((base or {}).get("recolor", []) + r.get("recolor", []), r.get("recolor_tolerance", 0))
    SHEET_RECOLOR.clear()
    for s_ in r["sources"]:
        if s_.get("own_recolor"):
            o = s_["own_recolor"]
            SHEET_RECOLOR[s_["image"]] = Recolor(r.get("recolor", []) + o["table"], o.get("tolerance", 0))
    KEEP_COLORS.clear()
    KEEP_COLORS.update(gba_color(tuple(c)) for c in (base or {}).get("keep_colors", []) + r.get("keep_colors", []))

    # 1. pick metatiles, keeping each source range's 8-wide layout
    picked = []  # (entries, attr) or None for padding
    names, sources = {}, {}
    hidden = {}  # "overlay_only" sources: art only ever drawn over terrain by overlay patches, never placed raw
    for s in r["sources"]:
        src = make_source(s, recolor)
        sources[src.name] = src
        if s.get("pick_only_for_patches"):
            continue
        for name, mt in src.picks(s):
            if s.get("overlay_only"):
                if name is not None:
                    hidden[f"{src.name}:{name}"] = mt
                continue
            if name is None:
                while len(picked) % 8:
                    picked.append(None)
                continue
            names[f"{src.name}:{name}"] = len(picked)
            picked.append(mt)

    # re-seat: building tiles whose ground is the source's own grass get that ground cut away and are
    # redrawn over our base tile, so the grass texture runs continuously up to the walls
    for spec in r["sources"]:
        rb = spec.get("rebase_ground")
        if not rb:
            continue
        drop = tuple(sorted(gba_color(tuple(c)) for c in rb["colors"]))
        base_entries = picked[names[rb["base"]]][0][:4]
        for name, idx in list(names.items()):
            if not name.startswith(spec["name"] + ":") or not picked[idx]:
                continue
            entries, attr = picked[idx]
            merged = [(("comp", entries[q], entries[4 + q]), ("comp", entries[q][1], entries[4 + q][1]), 0, 0) for q in range(4)]
            if not any(c in drop for m in merged for c in rgb(m[0], m[1], recolor)):
                continue
            upper = [(("mask", m[0], drop), ("mask", m[1]), 0, 0) for m in merged]
            picked[idx] = (base_entries + upper, (attr & 0x0FFF) | (LAYER_COVERED << 12))

    # patches: a new metatile from one metatile's lower layer and another's upper layer, e.g. a
    # boat lifted off its original water onto ours, or a door tile given a door behaviour
    behaviors = behavior_ids() if r.get("patches") else {}

    def resolve(ref):
        if ref in names:
            return picked[names[ref]]
        if ref in hidden:
            return hidden[ref]
        src, mid = ref.split(":", 1)
        mt = sources[src].metatile(int(mid, 16))
        if mt is None:
            raise SystemExit(f"patch reference {ref} does not exist")
        return mt

    patches = list(r.get("patches", []))
    if r.get("blends_file"):
        bf = os.path.join(os.path.dirname(recipe_path), "..", r["blends_file"])
        if os.path.exists(bf):
            patches += json.load(open(bf))
    for pt in patches:
        if "pixels" in pt:
            # a whole cell drawn elsewhere (levee.py via build.py): its 16x16 image becomes the lower layer,
            # behaviour and layer type from the metatile it replaces; each 8x8 tile is grouped by its own
            # colours so the palette packer can fit them wherever they suit
            # with "base", the image is an overlay: its clear pixels show that metatile (both layers, as cut
            # from its source, so the colours are the art's own, not a previous compose's)
            im = Image.open(pt["pixels"]).convert("RGBA")
            ip = im.load()
            under = resolve(pt["base"]) if pt.get("base") else None
            entries = []
            for q in range(4):
                ox, oy = (q % 2) * 8, (q // 2) * 8
                if under:
                    mq = (("comp", under[0][q], under[0][4 + q]), ("comp", under[0][q][1], under[0][4 + q][1]))
                    below = rgb(mq[0], mq[1], recolor)
                cols = []
                for j in range(8):
                    for i in range(8):
                        c = ip[ox + i, oy + j]
                        cols.append(gba_color(c[:3]) if c[3] >= 128 or not under else below[j * 8 + i])
                cols = tuple(cols)
                # "group": tiles drawn as one piece of art (the levee) share a palette group, so its colours are
                # packed together and its own colours are kept exactly when a slot has to be reduced
                gk = ("px", pt["group"]) if pt.get("group") else ("px", tuple(sorted({c for c in cols if c is not None})))
                entries.append((("px", cols), gk, 0, 0))
            if pt.get("group") == "levee":
                import levee
                KEEP_COLORS.update(gba_color(c) for c in [levee.STONE_L, levee.STONE, levee.STONE_D, levee.OUTLINE,
                                                          levee.EARTH, levee.EARTH_D, levee.FOAM] + levee.SLOPE)
            entries += [(("blank",), ("blank",), 0, 0)] * 4
            names[f"patch:{pt['id']}"] = len(picked)
            picked.append((entries, resolve(pt["attr_of"])[1]))
            continue
        if "blend" in pt:
            spec = pt["blend"]
            ta, tb, tm = resolve(spec["A"]), resolve(spec["B"]), resolve(spec["M"])
            land = resolve(spec["land"])
            colors = tuple(sorted({px for e in land[0][:4] for px in rgb(e[0], e[1], recolor) if px is not None}))
            gr = resolve(spec.get("grass", "ekat:grass"))
            gcolors = tuple(sorted({px for e in gr[0][:4] for px in rgb(e[0], e[1], recolor) if px is not None}))
            merge = lambda mt, i: (("comp", mt[0][i], mt[0][4 + i]), ("comp", mt[0][i][1], mt[0][4 + i][1]), 0, 0)
            entries = []
            for q in range(4):
                ea, eb, em = merge(ta, q), merge(tb, q), merge(tm, q)
                entries.append((("blend", ea, eb, em, colors, gcolors), ("blend", ea[1], eb[1], em[1]), 0, 0))
            entries += [(("blank",), ("blank",), 0, 0)] * 4
            names[f"patch:{pt['id']}"] = len(picked)
            picked.append((entries, ta[1]))
            continue
        if "overlay" in pt:
            # an object cell drawn over the terrain the builder found underneath it (both of the base's
            # layers merged into the lower layer, the art on the upper layer, drawn under the player)
            spec = pt["overlay"]
            base_mt, art = resolve(spec["base"]), resolve(spec["art"])
            merge = lambda mt, i: (("comp", mt[0][i], mt[0][4 + i]), ("comp", mt[0][i][1], mt[0][4 + i][1]), 0, 0)
            # a base whose upper layer is empty there (paving, plain ground) keeps its own lower tile, so a
            # primary tile under an overlay is reused from the primary instead of copied into the secondary
            base_q = lambda mt, i: mt[0][i] if is_blank(mt[0][4 + i], recolor) else merge(mt, i)
            # "upper": take the art from the source's upper layer (e.g. dock planks drawn over water)
            art_q = list(art[0][4:] if spec.get("upper") else art[0][:4])
            if spec.get("vflip"):
                # the art upside down (a moored boat turned bow-for-stern): swap its top and bottom quadrants and flip
                # every tile vertically; the terrain beneath is left as it is
                art_q = [(t, pal, h, v ^ 1) for t, pal, h, v in [art_q[i] for i in (2, 3, 0, 1)]]
            entries = [base_q(base_mt, i) for i in range(4)] + art_q
            # "walk": the art decides the behaviour (planks over water are walkable ground)
            beh_src = art if spec.get("walk") else base_mt
            # "layer": "normal" puts the art above characters at low elevations (a bridge deck a surfer passes
            # under; walkers on the bridge are at elevation 4 and drawn over it)
            attr = (beh_src[1] & 0x0FFF) | ((LAYER_NORMAL if spec.get("layer") == "normal" else LAYER_COVERED) << 12)
            if spec.get("behavior"):
                attr = (attr & ~0xFF) | behavior_ids()[spec["behavior"]]
            names[f"patch:{pt['id']}"] = len(picked)
            picked.append((entries, attr))
            continue
        if "inner" in pt:
            spec = pt["inner"]
            cen, ea, eb, q = resolve(spec["C"]), resolve(spec["A"]), resolve(spec["B"]), spec["q"]
            g = resolve(spec["grass"])
            grass = tuple(sorted({px for e in g[0][:4] for px in rgb(e[0], e[1], recolor) if px is not None}))
            # work on both layers merged, so pieces that keep grass below and dirt above compare correctly
            merge = lambda mt, i: (("comp", mt[0][i], mt[0][4 + i]), ("comp", mt[0][i][1], mt[0][4 + i][1]), 0, 0)
            entries = [merge(cen, i) for i in range(4)] + [(("blank",), ("blank",), 0, 0)] * 4
            mc, ma, mb = merge(cen, q), merge(ea, q), merge(eb, q)
            entries[q] = (("inner", mc, ma, mb, grass), ("inner", mc[1], ma[1], mb[1]), 0, 0)
            names[f"patch:{pt['id']}"] = len(picked)
            picked.append((entries, cen[1]))
            continue
        if "reseat" in pt:
            # cut the source's ground colours away and draw the rest over another tile
            src_mt, base_mt = resolve(pt["reseat"]), resolve(pt["base"])
            drop = tuple(sorted(gba_color(tuple(c)) for c in pt["colors"]))
            merged = [(("comp", src_mt[0][q], src_mt[0][4 + q]), ("comp", src_mt[0][q][1], src_mt[0][4 + q][1]), 0, 0) for q in range(4)]
            upper = [(("mask", m[0], drop), ("mask", m[1]), 0, 0) for m in merged]
            attr = (src_mt[1] & 0x0FFF) | (LAYER_COVERED << 12)
            # "merge_base": the base's two layers merged into the lower layer, for a base whose art sits on its upper
            # layer (e.g. a flower patch under the fountain's spray, Grand Oak)
            lower = ([(("comp", base_mt[0][q], base_mt[0][4 + q]), ("comp", base_mt[0][q][1], base_mt[0][4 + q][1]), 0, 0)
                      for q in range(4)] if pt.get("merge_base") else base_mt[0][:4])
            names[f"patch:{pt['id']}"] = len(picked)
            picked.append((lower + upper, attr))
            continue
        lower, upper = resolve(pt["lower"]), resolve(pt.get("upper", pt["lower"]))
        attr = upper[1]
        if "behavior" in pt:
            attr = (attr & ~0xFF) | behaviors[pt["behavior"]]
        if "layer" in pt:
            attr = (attr & 0x0FFF) | ({"normal": LAYER_NORMAL, "covered": LAYER_COVERED}[pt["layer"]] << 12)
        entries = lower[0][:4] + upper[0][4:]
        if pt.get("hflip"):
            # mirror: swap left/right quadrants of each layer and flip every tile
            entries = [(t, pal, h ^ 1, v) for t, pal, h, v in
                       [entries[i] for i in (1, 0, 3, 2, 5, 4, 7, 6)]]
        if pt.get("vflip"):
            # upside down: swap top and bottom quadrants of each layer and flip every tile vertically
            entries = [(t, pal, h, v ^ 1) for t, pal, h, v in
                       [entries[i] for i in (2, 3, 0, 1, 6, 7, 4, 5)]]
        names[f"patch:{pt['id']}"] = len(picked)
        picked.append((entries, attr))
    if r.get("keep_file"):
        picked, names = sparse_primary(r, recipe_path, picked, names)
    if r.get("demand"):
        picked, names = demand_only(r, picked, names)
    if base and base.get("sig"):
        picked, names = drop_shared(picked, names, base, recolor)
    if len(picked) > MAX_METATILES:
        raise SystemExit(f"{len(picked)} metatiles picked; the limit is {MAX_METATILES}")

    # 2. which (tile, palette) pairs do we need, and which colours does each palette group use
    reuse, base_slots, base_pals = {}, {}, []
    if base:
        reuse = {tuplify(json.loads(k)): v for k, v in base["tiles"].items()}
        base_pals = [[tuple(c) for c in p] for p in base["palettes"]]
        # the same pixels already in the primary (a shared piece's tiles under a prop, say) are never copied
        content = base.get("content") or {}
        for p in picked:
            for tkey, pkey, _, _ in (p[0] if p else []):
                if (tkey, pkey) in reuse:
                    continue
                px = rgb(tkey, pkey, recolor)
                if all(c is None for c in px):
                    continue
                hit = content.get(tile_hash(px))
                if hit:
                    reuse[(tkey, pkey)] = tuple(hit)
    # "tile_palettes": every 8x8 tile is placed in a palette by its own colours (pack_tiles), rather than by
    # the source palette it came from - far fewer colours lost when a set mixes many sources
    tile_pal = bool(r.get("tile_palettes"))
    v2 = r.get("palette") == "v2"  # see "palette v2" above
    colours_of = {}

    def gkey(tkey, pkey):
        if v2:
            return (tkey, pkey)
        if not tile_pal:
            return pkey
        if (tkey, pkey) not in colours_of:
            colours_of[(tkey, pkey)] = ("set", tuple(sorted({c for c in rgb(tkey, pkey, recolor) if c is not None})))
        return colours_of[(tkey, pkey)]
    groups = {}
    for p in picked:
        if not p:
            continue
        for tkey, pkey, _, _ in p[0]:
            if (tkey, pkey) in reuse:
                continue
            g = groups.setdefault(gkey(tkey, pkey), {})
            for c in rgb(tkey, pkey, recolor):
                if c is not None:
                    g[c] = g.get(c, 0) + 1
    groups = {k: g for k, g in groups.items() if g}
    if base:
        # a group whose colours already sit in one primary palette doesn't need its own slot
        for pkey, g in list(groups.items()):
            for i, pal in enumerate(base_pals):
                if all(c in pal for c in g):
                    base_slots[pkey] = i
                    del groups[pkey]
                    break
    v2_bottom, v2_bd = set(), None
    if v2:
        v2_bd = recolor(gba_color(tuple(r.get("backdrop") or (base or {}).get("backdrop") or (0, 0, 0))))
        counts = primary_counts(r, recipe_path) if not secondary else map_counts(r, recipe_path)
        items = v2_items(picked, names, counts, reuse, recolor)
        if not r.get("v2_backdrop"):
            # off by default: with OW_ENABLE_DNS the day/night tint (TimeMixPalettes) copies colour 0 through
            # untinted, so grass drawn as the backdrop would stay day-bright next to tinted grass after dark
            items = {k: (w, False) for k, (w, _) in items.items()}
        for w, _ in items.values():  # the base grass borders plain grass everywhere: any shift shows as a seam
            if v2_bd in w:
                w[v2_bd] *= V2_GRASS_MULT
        v2_bottom = {k for k, (_, bottom) in items.items() if bottom}
        pals, where, base_slots, report = pack_v2(items, base_pals, SECONDARY_SLOTS if secondary else PRIMARY_SLOTS,
                                                  v2_bd)
    else:
        pals, where, report = (pack_tiles if tile_pal else pack_palettes)(groups, SECONDARY_SLOTS if secondary
                                                                           else PRIMARY_SLOTS)
    slot_offset = PRIMARY_SLOTS if secondary else 0

    # 3. build tiles and metatiles
    bank = TileBank(reserve_blank=not secondary)
    tile_map = {}
    out_mts, out_attrs = [], []
    inv_names = {i: n for n, i in names.items()} if isinstance(names, dict) else {}
    trace = []                                   # COMPOSE_TRACE=1: the tiles each metatile added to the bank (the biggest eaters first)
    for pi, p in enumerate(picked):
        if not p:
            out_mts.append([0] * 8)
            out_attrs.append(0)
            continue
        entries, attr = p
        bank0 = len(bank.tiles)
        new = []
        for tkey, pkey, h, v in entries:
            if (tkey, pkey) in reuse:
                t, th, tv, slot = reuse[(tkey, pkey)]
                new.append(t | ((h ^ th) << 10) | ((v ^ tv) << 11) | (slot << 12))
                continue
            px = rgb(tkey, pkey, recolor)
            if all(c is None for c in px):
                new.append(0)  # fully transparent: tile 0 of the primary is blank
                continue
            gk = gkey(tkey, pkey)
            if gk in v2_bottom and all(c is None or c == v2_bd for c in px):
                new.append(0)  # v2: only backdrop colour on the bottom layer, which tile 0 shows anyway
                continue
            if gk in base_slots:
                slot_pal, slot = base_pals[base_slots[gk]], base_slots[gk]
            else:
                slot_pal, slot = pals[where[gk]], where[gk] + slot_offset
            if (tkey, pkey) not in tile_map:
                full = [None] + slot_pal
                lo = 1
                if gk in v2_bottom:  # v2: a bottom-layer tile draws the backdrop colour with index 0 (transparent)
                    full, lo = [v2_bd] + slot_pal, 0
                idx = tuple(0 if c is None else min(range(lo, len(full)), key=lambda i: dist2(c, full[i])) for c in px)
                tile_map[(tkey, pkey)] = (bank.add(idx), slot)
            (t, th, tv), slot = tile_map[(tkey, pkey)]
            t += MAX_TILES if secondary else 0
            new.append(t | ((h ^ th) << 10) | ((v ^ tv) << 11) | (slot << 12))
        out_mts.append(new)
        out_attrs.append(attr)
        trace.append((len(bank.tiles) - bank0, inv_names.get(pi, "?")))
    if os.environ.get("COMPOSE_TRACE"):
        by = {}
        for n_, nm in trace:
            k = nm.split("__")[0] if nm.startswith("patch:ovl") else nm.split(":")[0] + ":" + nm.split(":")[-1].split("_")[0]
            by[k] = by.get(k, 0) + n_
        print("tile cost by group:", sorted(by.items(), key=lambda kv: -kv[1])[:25])
        top = {}
        for n_, nm in trace:
            k = nm.split(":")[0] + (":" + nm.split(":")[1].split("_")[0] if nm.startswith("patch:") else "")
            top[k] = top.get(k, 0) + n_
        print("tile cost by family:", sorted(top.items(), key=lambda kv: -kv[1])[:30])
        ov = {}
        for n_, nm in trace:
            if nm.startswith("patch:ovl_"):
                k = "ovl_" + nm.split("_")[1]
                ov[k] = ov.get(k, 0) + n_
        print("overlay cost by art:", sorted(ov.items(), key=lambda kv: -kv[1]))
        print("ALL:", [(n_, nm) for n_, nm in trace if n_])
        if os.environ.get("COMPOSE_TRACE") == "2":
            print("pieces:", [(n_, nm) for n_, nm in trace if n_ and (nm.startswith("patch:ovl_wpr") or "cypress_small" in nm or "lmk_15_" in nm or "lmk_6_" in nm or "waterlog" in nm or "snag" in nm or "lv_" in nm and n_ > 3)])
    if len(bank.tiles) > MAX_TILES:
        raise SystemExit(f"{len(bank.tiles)} tiles needed; the limit is {MAX_TILES}")

    # 4. write files
    os.makedirs(f"{out_dir}/palettes", exist_ok=True)
    rows = (len(bank.tiles) + 15) // 16
    im = Image.new("P", (128, rows * 8))
    gray = []
    for i in range(16):
        gray += [i * 17] * 3
    im.putpalette(gray + [0] * (768 - len(gray)))
    px = im.load()
    for n, t in enumerate(bank.tiles):
        ox, oy = (n % 16) * 8, (n // 16) * 8
        for i, c in enumerate(t):
            px[ox + i % 8, oy + i // 8] = c
    im.save(f"{out_dir}/tiles.png")
    with open(f"{out_dir}/metatiles.bin", "wb") as f:
        f.write(struct.pack(f"<{len(out_mts) * 8}H", *[e for m in out_mts for e in m]))
    with open(f"{out_dir}/metatile_attributes.bin", "wb") as f:
        f.write(struct.pack(f"<{len(out_attrs)}H", *out_attrs))
    # Colour 0 is transparent everywhere except as the backdrop (palette 0), which shows through
    # holes in bottom-layer tiles. Using the grass colour hides those holes; set it in every palette
    # so Porymap draws the same thing the game does.
    bd = recolor(gba_color(tuple(r.get("backdrop") or (base or {}).get("backdrop") or (0, 0, 0))))
    all_pals = [[bd] * 16 for _ in range(16)]
    for i, p in enumerate(pals):
        all_pals[slot_offset + i] = [bd] + p + [(0, 0, 0)] * (15 - len(p))
    for i, p in enumerate(base_pals):
        all_pals[i] = [bd] + p + [(0, 0, 0)] * (15 - len(p))
    for i, p in enumerate(all_pals):
        with open(f"{out_dir}/palettes/{i:02d}.pal", "w", newline="\r\n") as f:
            f.write("JASC-PAL\n0100\n16\n" + "".join(f"{c[0]} {c[1]} {c[2]}\n" for c in p))

    sig, content = {}, {}
    if not secondary:
        for n, i in names.items():
            if not n.startswith("johto:") and picked[i]:
                sig[n] = piece_sig(picked[i], recolor)
        for (tkey, pkey), ((t, th, tv), slot) in tile_map.items():
            px = rgb(tkey, pkey, recolor)
            for h in (0, 1):
                for v in (0, 1):
                    content.setdefault(tile_hash(flip(px, h, v)), [t, th ^ h, tv ^ v, slot])
    mapping = {
        "sig": sig or None,
        "content": content or None,
        "tileset": r["symbol"],
        "kind": kind,
        "backdrop": list(bd),
        "recolor": r.get("recolor", []) if not secondary else None,
        "keep_colors": r.get("keep_colors", []) if not secondary else None,
        "metatile_offset": MAX_METATILES if secondary else 0,
        "metatiles": {k: v + (MAX_METATILES if secondary else 0) for k, v in names.items() if picked[v]},
        "palettes": pals if not secondary else None,
        "tiles": {} if secondary else {
            json.dumps([list(k[0]), list(k[1])]): [t, h, v, slot] for k, ((t, h, v), slot) in tile_map.items()
        },
    }
    mp = os.path.join(os.path.dirname(recipe_path), "..", f"{r['dir']}.mapping.json")
    json.dump(mapping, open(mp, "w"), indent=0)
    print(f"{r['symbol']}: {len(picked)} metatiles, {len(bank.tiles)} tiles, {len(pals)} new palette slots"
          + (f" (+{len(set(base_slots.values()))} shared with primary)" if base else ""))
    for line in report:
        print(line)
    return r


# ---------------------------------------------------------------- registration
BEGIN, END = "// --- mapgen: composed tilesets (begin) ---", "// --- mapgen: composed tilesets (end) ---"


def splice(path, anchor, block):
    """Insert/replace our marked block right before `anchor` (first occurrence)."""
    src = open(path).read()
    if BEGIN in src:
        src = src[:src.index(BEGIN)] + src[src.index(END) + len(END) + 1:]
    i = src.index(anchor)
    src = src[:i] + BEGIN + "\n" + block + END + "\n" + src[i:]
    with open(path, "w", newline="\n") as f:
        f.write(src)


def register():
    """Register every recipe's output (not just the ones composed this run)."""
    recipes = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(HERE, "tilesets", "recipes", "*.json")))]
    recipes.sort(key=lambda r: r["kind"] != "primary")
    gfx, mts, hdr = "", "", ""
    for r in recipes:
        kind, d, sym = r["kind"], r["dir"], r["symbol"]
        if not os.path.exists(f"data/tilesets/{kind}/{d}/tiles.png"):
            continue
        n = sym.replace("gTileset_", "")
        path = f"data/tilesets/{kind}/{d}"
        gfx += f'const u32 gTilesetTiles_{n}[] = INCGFX_U32("{path}/tiles.png", ".4bpp.fastSmol");\n\n'
        gfx += f"const u16 gTilesetPalettes_{n}[][16] =\n{{\n"
        gfx += "".join(f'    INCGFX_U16("{path}/palettes/{i:02d}.pal", ".gbapal"),\n' for i in range(16)) + "};\n\n"
        mts += f'const u16 gMetatiles_{n}[] = INCBIN_U16("{path}/metatiles.bin");\n'
        mts += f'const u16 gMetatileAttributes_{n}[] = INCBIN_U16("{path}/metatile_attributes.bin");\n\n'
        hdr += (f"const struct Tileset {sym} =\n{{\n    .isCompressed = TRUE,\n"
                f"    .isSecondary = {'TRUE' if kind == 'secondary' else 'FALSE'},\n"
                f"    .tiles = gTilesetTiles_{n},\n    .palettes = gTilesetPalettes_{n},\n"
                f"    .metatiles = gMetatiles_{n},\n    .metatileAttributes = gMetatileAttributes_{n},\n"
                f"    .callback = NULL,\n}};\n\n")
    splice("src/data/tilesets/graphics.h", "#else", gfx)
    splice("src/data/tilesets/metatiles.h", "#else", mts)
    splice("src/data/tilesets/headers.h", "const struct Tileset gTileset_General =", hdr)
    print("registered:", ", ".join(r["symbol"] for r in recipes))


if __name__ == "__main__":
    args = sys.argv[1:]
    for p in args:
        if p.endswith(".json"):
            compose(p)
    if "--register" in args:
        register()

"""Shared helpers for the legendary arenas' own art (make_temple.py, make_cathedral.py, make_shrine.py).

Every piece is drawn on a Canvas (16 px cells, RGBA, alpha 0 = clear), placed on a Sheet (one PNG per arena,
magenta = clear, the format compose.py's image sources read) and recorded in the arena's json with its cell
rectangle and per-cell gameplay notes (walk / behaviour / layer).

Colours are always GBA-exact (multiples of 8). Each arena declares colour FAMILIES (<= 15 colours each, the palettes
the art is drawn to); check_families() proves every 8x8 tile of every piece fits one family, so compose's palette
packing has nothing to squeeze.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
KEY = (255, 0, 255)


def gba(c):
    return tuple((int(v) >> 3) << 3 for v in c[:3])


def mix(a, b, t):
    return gba(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


class Canvas:
    """A w x h cell RGBA canvas. Colours are RGB tuples; None = clear."""

    def __init__(self, w, h, fill=None):
        self.cw, self.ch = w, h
        self.w, self.h = w * 16, h * 16
        self.im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0) if fill is None else tuple(fill) + (255,))
        self.p = self.im.load()

    # ---- pixels
    def put(self, x, y, c):
        if c is None:
            return
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[x, y] = tuple(c[:3]) + (255,)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            v = self.p[x, y]
            return v[:3] if v[3] else None
        return None

    def clear(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[x, y] = (0, 0, 0, 0)

    def rect(self, x, y, w, h, c):
        for j in range(int(y), int(y + h)):
            for i in range(int(x), int(x + w)):
                self.put(i, j, c)

    def hline(self, x0, x1, y, c):
        for i in range(int(x0), int(x1) + 1):
            self.put(i, y, c)

    def vline(self, x, y0, y1, c):
        for j in range(int(y0), int(y1) + 1):
            self.put(x, j, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, c):
        if rx <= 0 or ry <= 0:
            return
        for j in range(int(cy - ry - 1), int(cy + ry + 2)):
            for i in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.put(i, j, c)

    def poly(self, pts, c):
        m = Image.new("1", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=1)
        mp = m.load()
        for j in range(self.h):
            for i in range(self.w):
                if mp[i, j]:
                    self.put(i, j, c)

    def mask(self, fn=None):
        """Set of drawn pixels (optionally those whose colour satisfies fn)."""
        out = set()
        for j in range(self.h):
            for i in range(self.w):
                v = self.p[i, j]
                if v[3] and (fn is None or fn(v[:3])):
                    out.add((i, j))
        return out

    def outline(self, c, sides="nsew", within=None, diag=False):
        """Ink every clear pixel touching the drawn shape (4-neighbour, optionally 8)."""
        m = self.mask() if within is None else within
        add = set()
        nb = [(0, -1, "s"), (0, 1, "n"), (-1, 0, "e"), (1, 0, "w")]
        for (x, y) in m:
            for dx, dy, s in nb:
                if s in sides and (x + dx, y + dy) not in m and self.get(x + dx, y + dy) is None:
                    add.add((x + dx, y + dy))
            if diag:
                for dx in (-1, 1):
                    for dy in (-1, 1):
                        if (x + dx, y + dy) not in m and self.get(x + dx, y + dy) is None:
                            add.add((x + dx, y + dy))
        for (x, y) in add:
            self.put(x, y, c)

    def recolor(self, table):
        for j in range(self.h):
            for i in range(self.w):
                v = self.p[i, j]
                if v[3] and v[:3] in table:
                    self.p[i, j] = tuple(table[v[:3]]) + (255,)

    def paste(self, other, ox, oy):
        """Draw another canvas over this one (clear pixels of `other` leave this one)."""
        for j in range(other.h):
            for i in range(other.w):
                v = other.p[i, j]
                if v[3]:
                    self.put(ox + i, oy + j, v[:3])

    def mirror_x(self, axis=None):
        """Copy the left half onto the right half, mirrored about `axis` (pixel column count of the left half)."""
        a = self.w // 2 if axis is None else axis
        for j in range(self.h):
            for i in range(a):
                v = self.p[i, j]
                tx = 2 * a - 1 - i
                if 0 <= tx < self.w:
                    self.p[tx, j] = v

    def flip_x(self):
        self.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        self.p = self.im.load()
        return self

    def copy(self):
        c = Canvas(self.cw, self.ch)
        c.im = self.im.copy()
        c.p = c.im.load()
        return c

    def crop(self, cx, cy, cw, ch):
        c = Canvas(cw, ch)
        c.im = self.im.crop((cx * 16, cy * 16, (cx + cw) * 16, (cy + ch) * 16))
        c.p = c.im.load()
        return c

    def over(self, ground):
        """This canvas composited over an opaque ground canvas (or a 16x16 RGB image tiled)."""
        out = Canvas(self.cw, self.ch)
        for j in range(self.h):
            for i in range(self.w):
                if isinstance(ground, Canvas):
                    g = ground.get(i, j)
                else:
                    g = ground.getpixel((i % 16, j % 16))[:3]
                out.put(i, j, g)
        out.paste(self, 0, 0)
        return out


def texture(cv, x, y, w, h, fn):
    """Fill a rect with fn(px, py) -> colour, in absolute canvas coordinates (so textures repeat by position)."""
    for j in range(int(y), int(y + h)):
        for i in range(int(x), int(x + w)):
            cv.put(i, j, fn(i, j))


def hashn(x, y, s=0):
    """Deterministic pixel noise in [0, 1)."""
    h = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


# ------------------------------------------------------------------ the sheet
class Sheet:
    """Pieces packed onto a sheet `cols` cells wide; records {name: {x, y, w, h, ...meta}}."""

    def __init__(self, cols=16):
        self.cols = cols
        self.items = []          # (name, canvas, meta)
        self.pieces = {}

    def add(self, name, cv, **meta):
        assert name not in self.pieces, name
        self.items.append((name, cv, meta))
        self.pieces[name] = None
        return name

    def pack(self):
        """Shelf packing in insertion order (a piece never straddles the sheet width)."""
        x = y = shelf = 0
        placed = {}
        for name, cv, meta in self.items:
            if x + cv.cw > self.cols:
                x, y, shelf = 0, y + shelf, 0
            placed[name] = (x, y)
            x += cv.cw
            shelf = max(shelf, cv.ch)
        rows = y + shelf
        im = Image.new("RGB", (self.cols * 16, rows * 16), KEY)
        for name, cv, meta in self.items:
            px, py = placed[name]
            sub = Image.new("RGB", (cv.w, cv.h), KEY)
            sub.paste(cv.im, (0, 0), cv.im)
            im.paste(sub, (px * 16, py * 16))
            self.pieces[name] = dict(meta, x=px, y=py, w=cv.cw, h=cv.ch)
        self.image = im
        return im


# ------------------------------------------------------------------ checks and counts
def tiles_of(im, x0=0, y0=0, w=None, h=None):
    """8x8 tiles (tuples of RGB or None) of an RGB(A)/canvas region."""
    if isinstance(im, Canvas):
        im = im.im
    im = im.convert("RGBA")
    w = w if w is not None else im.width
    h = h if h is not None else im.height
    p = im.load()
    out = []
    for ty in range(y0, y0 + h, 8):
        for tx in range(x0, x0 + w, 8):
            t = []
            for j in range(8):
                for i in range(8):
                    v = p[tx + i, ty + j]
                    t.append(None if (v[3] == 0 or v[:3] == KEY) else v[:3])
            out.append(tuple(t))
    return out


def tile_key(t):
    """Canonical key under the four flips (GBA tiles flip for free)."""
    rows = [t[i * 8:(i + 1) * 8] for i in range(8)]
    cands = []
    for hf in (False, True):
        for vf in (False, True):
            r = rows[::-1] if vf else rows
            r = [row[::-1] for row in r] if hf else r
            cands.append(tuple(c for row in r for c in row))
    return min(cands, key=lambda k: repr(k))


def count_tiles(images, known=()):
    """Distinct 8x8 tiles (flip-deduplicated) over opaque images, minus tiles in `known`."""
    seen = set(tile_key(t) for t in known)
    new = set()
    for im in images:
        for t in tiles_of(im):
            k = tile_key(t)
            if k not in seen:
                new.add(k)
    return len(new)


def check_families(images, families, label=""):
    """Every 8x8 tile's colours must sit inside one family. Returns a list of problems."""
    fam = {k: set(gba(c) for c in v) for k, v in families.items()}
    for k, v in fam.items():
        assert len(v) <= 15, f"family {k} has {len(v)} colours"
    bad = []
    for name, im in images:
        for i, t in enumerate(tiles_of(im)):
            cols = set(c for c in t if c is not None)
            if not cols:
                continue
            if not any(cols <= f for f in fam.values()):
                w = (im.width if not isinstance(im, Canvas) else im.w) // 8
                best = min(fam, key=lambda k: len(cols - fam[k]))
                bad.append((label, name, (i % w, i // w), best, sorted(cols - fam[best])))
    return bad


def snap_to_families(cv, families):
    """Last resort for anti-aliased edges: per 8x8 tile, map every colour to the nearest colour of the family that
    covers most of the tile's pixels."""
    fam = {k: [gba(c) for c in v] for k, v in families.items()}
    for ty in range(0, cv.h, 8):
        for tx in range(0, cv.w, 8):
            px = [(i, j, cv.get(i, j)) for j in range(ty, ty + 8) for i in range(tx, tx + 8)]
            cols = [c for _, _, c in px if c is not None]
            if not cols:
                continue
            best = max(fam, key=lambda k: sum(1 for c in cols if c in fam[k]))
            for i, j, c in px:
                if c is not None and c not in fam[best]:
                    cv.put(i, j, min(fam[best], key=lambda f: sum((a - b) ** 2 for a, b in zip(f, c))))


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


def scale(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


# ------------------------------------------------------------------ sheet + json + compose recipe
def write(sh, meta, prefix, dirname, symbol, sheet_png, families, title, behaviors=None):
    """Write <prefix>.png, <prefix>.json and recipes/<dirname>.json (compose image source named `prefix`)."""
    behaviors = behaviors or {}
    png = os.path.join(HERE, sheet_png)
    sh.image.save(png)
    pieces = {}
    mts = []
    for name, p in sh.pieces.items():
        if name.endswith("__top"):
            continue
        m = meta[name]
        top = sh.pieces[m["top"]] if m.get("top") else None
        cells = []
        for j in range(p["h"]):
            row = []
            for i in range(p["w"]):
                mid = name if p["w"] == p["h"] == 1 else f"{name}_{i}_{j}"
                e = {"id": mid, "bottom": [p["x"] + i, p["y"] + j]}
                if top is not None:
                    tc = (top["x"] + i, top["y"] + j)
                    if any(px for px in [sh.image.getpixel((tc[0] * 16 + a, tc[1] * 16 + b)) != (255, 0, 255)
                                         for a in range(16) for b in range(16)]):
                        e["top"] = list(tc)
                        e["layer"] = "normal"
                bh = behaviors.get((name, i, j))
                if m.get("exit") == [i, j]:
                    bh = bh or "MB_SOUTH_ARROW_WARP"
                if bh:
                    e["behavior"] = bh
                mts.append(e)
                row.append(f"{prefix}:{mid}")
            cells.append(row)
        walk = m["walk"]
        if walk is True:
            walk = [[i, j] for j in range(p["h"]) for i in range(p["w"])]
        elif walk is False:
            walk = []
        pieces[name] = {"x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"], "rows": cells, "walk": walk,
                        "comment": m["comment"]}
        if m.get("exit"):
            pieces[name]["exit"] = m["exit"]
    dump(os.path.join(HERE, prefix_json(sheet_png)), {
        "_comment": f"{title}: piece -> sheet cell rectangle (16 px cells), the metatile names per cell ('{prefix}:<id>' "
                    f"in the composed tileset {symbol}), walkable cells (everything else should block), notes. "
                    f"Made by {os.path.basename(sys.argv[0])}.",
        "png": sheet_png, "source": prefix, "tileset": symbol, "families": {k: [list(c) for c in v] for k, v in families.items()},
        "pieces": pieces})
    os.makedirs(os.path.join(HERE, "recipes"), exist_ok=True)
    dump(os.path.join(HERE, "recipes", dirname + ".json"), {
        "_comment": f"{title} (own art, tools/mapgen/tilesets/arenas). Composes on top of the interiors' primary "
                    f"(orleans_building). Compose with: python tools/mapgen/compose.py "
                    f"tools/mapgen/tilesets/arenas/recipes/{dirname}.json (mapping lands in tilesets/arenas/); to "
                    f"register it in the ROM, copy this recipe into tilesets/recipes/ with primary_mapping "
                    f"'orleans_building.mapping.json' and run compose.py --register.",
        "kind": "secondary", "dir": dirname, "symbol": symbol,
        "primary_mapping": "../orleans_building.mapping.json",
        "sources": [{"name": prefix, "type": "image", "image": f"tools/mapgen/tilesets/arenas/{sheet_png}",
                     "transparent": [[255, 0, 255]], "group_rule": "fewest", "metatiles": mts}]})
    return pieces


def prefix_json(sheet_png):
    return sheet_png.replace(".png", ".json")



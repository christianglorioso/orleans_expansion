"""Lay the whole Orleans world out from the connection table (world.py) and review every seam.

usage (from the decomp root):  python tools/mapgen/world_stitch.py

Reads world.WORLD (never map.json: the table is the source of truth; run world.py to write the connections), walks
the connections from Isle Marais, places every connected map at its world position and draws each map straight from
its map.bin (render.py, the same way Porymap draws it), so the picture is always the maps as built, never a stale preview.

Writes into tools/mapgen/maps/:
  00_world.png         the whole world downscaled to ~8000 px on the long side, names and thin outlines
  00_world_full.png    the same at 16 px per cell (tiles 00_world_full_<n>.png when a side would pass 16000 px)
  00_world_seams.md    one block per connection: do the exits line up, does the terrain hard-cut at the border
  00_world_seams.png   contact sheet, a 3x crop of every join

Maps the walk from Isle Marais does not reach (Pointe Rouge's group: only the riverboat links it) are laid out
on their own, beside the main world, in a red dashed box.  Overlapping rectangles are listed and outlined red:
the GBA allows them (a connection only needs its own edge), but the graph is not planar there.
"""
import json
import os
import re
import struct
import sys
from collections import deque

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
from render import Tilesets, render  # noqa: E402

ROOT = world.ROOT
MAPS = world.MAPS
OUT = MAPS
CELL = 16
START = "isle_marais"
SIDE = {"right": ("E", "W"), "left": ("W", "E"), "down": ("S", "N"), "up": ("N", "S")}


# ------------------------------------------------------------------ the maps as built
def snake(name):
    name = name.replace("gTileset_", "")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Built:
    """One map: its size, collision words and its render, straight from the layout's map.bin."""

    def __init__(self, stem, maps, cache):
        info = maps.info[stem]
        lay = info["layout"]
        self.stem, self.w, self.h = stem, info["w"], info["h"]
        pd = os.path.join(ROOT, "data/tilesets/primary", snake(lay["primary_tileset"]))
        sd = os.path.join(ROOT, "data/tilesets/secondary", snake(lay["secondary_tileset"]))
        if not os.path.isdir(sd):  # fall back on the builder's tileset config
            cfg = json.load(open(os.path.join(HERE, "tilesets", info["spec"]["tileset"] + ".json"), encoding="utf-8"))
            pd, sd = os.path.join(ROOT, cfg["primary_dir"]), os.path.join(ROOT, cfg["secondary_dir"])
        if (pd, sd) not in cache:
            cache[(pd, sd)] = Tilesets(pd, sd)
        data = open(os.path.join(ROOT, lay["blockdata_filepath"]), "rb").read()
        self.blocks = struct.unpack(f"<{len(data) // 2}H", data)
        assert len(self.blocks) == self.w * self.h, (stem, len(self.blocks), self.w, self.h)
        self.im = render(cache[(pd, sd)], self.blocks, self.w).convert("RGB")
        self.spec = info["spec"]

    def passable(self, x, y):
        return ((self.blocks[y * self.w + x] >> 10) & 3) == 0

    def cls(self, x, y):
        """terrain class of a cell from its colour: W water, T tree/dark, g green ground or marsh, p sand/path/earth, o other"""
        r, g, b = self.im.crop((x * 16 + 4, y * 16 + 4, x * 16 + 12, y * 16 + 12)).resize((1, 1), Image.BOX).getpixel((0, 0))
        if b > r + 25 and b >= g - 4:
            return "W"
        lum = 0.3 * r + 0.59 * g + 0.11 * b
        if g >= r - 3 and g > b + 10:
            return "T" if lum < 115 else "g"
        if r >= g >= b and r - b > 25:
            return "p"
        return "o"

    def edge_cell(self, side, i):
        return {"N": (i, 0), "S": (i, self.h - 1), "W": (0, i), "E": (self.w - 1, i)}[side]

    def length(self, side):
        return self.w if side in "NS" else self.h

    def spec_exits(self, side):
        """[[cells along the edge], ...]: the exits listed in the map's spec (roads, boardwalks, piers)"""
        out = []
        for e in self.spec.get("exits") or []:
            cells = [tuple(c) for c in e["cells"]]
            xs, ys = {x for x, _ in cells}, {y for _, y in cells}
            s = "W" if xs == {0} else "E" if xs == {self.w - 1} else "N" if ys == {0} else "S" if ys == {self.h - 1} else "?"
            if s == side:
                out.append(sorted(y if side in "WE" else x for x, y in cells))
        return out

    def hint_exits(self, side):
        """the table's EXTRA_EXITS: boat channels and mockup arrows the spec has no exit for"""
        return world.EXTRA_EXITS.get((self.stem, side), [])


# ------------------------------------------------------------------ layout
def neighbours():
    adj = {}
    for e in world.WORLD:
        adj.setdefault(e[0], []).append(e)
        adj.setdefault(e[2], []).append(e)
    return adj


def other_pos(known, pos, size, e):
    """the position of the map on the other end of entry e, given the position of the known end"""
    a, d, b, k, _ = e
    (aw, ah), (bw, bh) = size[a], size[b]
    x, y = pos
    if known == a:
        return b, {"right": (x + aw, y + k), "left": (x - bw, y + k), "down": (x + k, y + ah), "up": (x + k, y - bh)}[d]
    return a, {"right": (x - aw, y - k), "left": (x + bw, y - k), "down": (x - k, y - ah), "up": (x - k, y + bh)}[d]


def lay_out(size):
    """-> (components [dict stem->(x, y)], conflicts).  The first component holds START."""
    adj = neighbours()
    seen, comps, conflicts = set(), [], []
    order = [START] + [s for s in world.OUTDOOR if s != START]
    for root in order:
        if root in seen:
            continue
        pos = {root: (0, 0)}
        seen.add(root)
        q = deque([root])
        while q:
            s = q.popleft()
            for e in adj.get(s, []):
                t, p = other_pos(s, pos[s], size, e)
                if t in pos:
                    if pos[t] != p:
                        conflicts.append((e, pos[t], p))
                else:
                    pos[t] = p
                    seen.add(t)
                    q.append(t)
        comps.append(pos)
    return comps, conflicts


def bbox(pos, size, pad=0):
    x0 = min(x for x, y in pos.values()) - pad
    y0 = min(y for x, y in pos.values()) - pad
    x1 = max(pos[s][0] + size[s][0] for s in pos) + pad
    y1 = max(pos[s][1] + size[s][1] for s in pos) + pad
    return x0, y0, x1, y1


def overlap_pairs(pos, size):
    out = []
    names = sorted(pos)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ax, ay = pos[a]
            bx, by = pos[b]
            w = min(ax + size[a][0], bx + size[b][0]) - max(ax, bx)
            h = min(ay + size[a][1], by + size[b][1]) - max(ay, by)
            if w > 0 and h > 0:
                out.append((a, b, w, h))
    return out


def place_apart(main, other, size, target, margin=4):
    """shift component `other` to the free spot nearest `target` (a cell position) that clears every main rectangle"""
    ox0, oy0, ox1, oy1 = bbox(other, size)
    bw, bh = ox1 - ox0, oy1 - oy0
    rects = [(main[s][0], main[s][1], main[s][0] + size[s][0], main[s][1] + size[s][1]) for s in main]
    mx0, my0, mx1, my1 = bbox(main, size)
    best = None
    for y in range(my0 - bh - 20, my1 + 20, 2):
        for x in range(mx0 - 20, mx1 + 20, 2):
            if any(x - margin < r[2] and x + bw + margin > r[0] and y - margin < r[3] and y + bh + margin > r[1] for r in rects):
                continue
            d = (x + bw / 2 - target[0]) ** 2 + (y + bh / 2 - target[1]) ** 2
            if best is None or d < best[0]:
                best = (d, x, y)
    _, x, y = best
    return {s: (p[0] - ox0 + x, p[1] - oy0 + y) for s, p in other.items()}


# ------------------------------------------------------------------ drawing the world
def font(px, bold=True):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        for d in ("C:/Windows/Fonts/", ""):
            try:
                return ImageFont.truetype(d + name, px)
            except OSError:
                pass
    return ImageFont.load_default()


def label(draw, xy, text, fnt, fill=(255, 255, 255), plate=(20, 20, 20, 190), pad=5):
    x, y = xy
    l, t, r, b = draw.textbbox((x, y), text, font=fnt)
    draw.rectangle([l - pad, t - pad, r + pad, b + pad], fill=plate)
    draw.text((x, y), text, font=fnt, fill=fill)


def draw_world(builts, pos_main, pos_apart, size, overlaps, out_dir):
    allpos = dict(pos_main)
    allpos.update(pos_apart)
    x0, y0, x1, y1 = bbox(allpos, size, pad=4)
    W, H = (x1 - x0) * CELL, (y1 - y0) * CELL
    canvas = Image.new("RGB", (W, H), (28, 38, 52))
    for s, (x, y) in allpos.items():
        canvas.paste(builts[s].im, ((x - x0) * CELL, (y - y0) * CELL))
    in_overlap = {s for a, b, _, _ in overlaps for s in (a, b)}
    # seams of the table, as magenta bars on the border
    ov = ImageDraw.Draw(canvas)
    for a, d, b, k, _ in world.WORLD:
        (ax, ay), (bx, by) = allpos[a], allpos[b]
        aw, ah = size[a]
        bw, bh = size[b]
        if d in ("right", "left"):
            xx = (ax + aw if d == "right" else ax) - x0
            lo, hi = max(ay, by), min(ay + ah, by + bh)
            ov.line([(xx * CELL, (lo - y0) * CELL), (xx * CELL, (hi - y0) * CELL)], fill=(255, 0, 255), width=3)
        else:
            yy = (ay + ah if d == "down" else ay) - y0
            lo, hi = max(ax, bx), min(ax + aw, bx + bw)
            ov.line([((lo - x0) * CELL, yy * CELL), ((hi - x0) * CELL, yy * CELL)], fill=(255, 0, 255), width=3)
    return canvas, (x0, y0), allpos, in_overlap


def annotate(img, scale, origin, allpos, size, in_overlap, apart, names, fs):
    """outlines + names on `img`, which is the full canvas scaled by `scale`"""
    d = ImageDraw.Draw(img, "RGBA")
    fnt = font(fs)
    x0, y0 = origin
    for s, (x, y) in allpos.items():
        l, t = (x - x0) * CELL * scale, (y - y0) * CELL * scale
        r, b = l + size[s][0] * CELL * scale, t + size[s][1] * CELL * scale
        col = (255, 60, 60) if s in in_overlap else (255, 255, 255)
        d.rectangle([l, t, r - 1, b - 1], outline=col + (255,), width=1 if scale < 1 else 2)
        label(d, (l + 8, t + 6), names[s], fnt)
    if apart:
        l = min(allpos[s][0] for s in apart); t = min(allpos[s][1] for s in apart)
        r = max(allpos[s][0] + size[s][0] for s in apart); b = max(allpos[s][1] + size[s][1] for s in apart)
        l, t, r, b = ((l - 2 - x0) * CELL * scale, (t - 2 - y0) * CELL * scale, (r + 2 - x0) * CELL * scale, (b + 2 - y0) * CELL * scale)
        step = 24
        for xx in range(int(l), int(r), step * 2):
            d.line([(xx, t), (min(xx + step, r), t)], fill=(255, 80, 80, 255), width=3)
            d.line([(xx, b), (min(xx + step, r), b)], fill=(255, 80, 80, 255), width=3)
        for yy in range(int(t), int(b), step * 2):
            d.line([(l, yy), (l, min(yy + step, b))], fill=(255, 80, 80, 255), width=3)
            d.line([(r, yy), (r, min(yy + step, b))], fill=(255, 80, 80, 255), width=3)
        label(d, (l + 10, b - 4 * fs), "NOT CONNECTED to the rest: reached by the riverboat only", font(int(fs * 1.1)),
              fill=(255, 220, 220), plate=(120, 0, 0, 220))
    return img


# ------------------------------------------------------------------ seams
def cell_pixels(b, side, i, depth):
    """pixels of the edge cell i, line `depth` in from the border, as a list of 16 RGB tuples"""
    x, y = b.edge_cell(side, i)
    im = b.im
    out = []
    for p in range(16):
        if side == "E":
            out.append(im.getpixel((x * 16 + 15 - depth, y * 16 + p)))
        elif side == "W":
            out.append(im.getpixel((x * 16 + depth, y * 16 + p)))
        elif side == "S":
            out.append(im.getpixel((x * 16 + p, y * 16 + 15 - depth)))
        else:
            out.append(im.getpixel((x * 16 + p, y * 16 + depth)))
    return out


def seam_score(A, sa, i, B, sb, j):
    """check.py's terrain-seam score for the border between A's edge cell i and B's edge cell j (colour jump across it
    minus the texture's own jump); above 20 is a hard cut"""
    d = lambda p, q: sum(abs(u - v) for u, v in zip(p, q))
    a0, a1 = cell_pixels(A, sa, i, 0), cell_pixels(A, sa, i, 1)
    b0, b1 = cell_pixels(B, sb, j, 0), cell_pixels(B, sb, j, 1)
    cross = sum(d(p, q) for p, q in zip(a0, b0)) / 16
    inner = (sum(d(p, q) for p, q in zip(a0, a1)) + sum(d(p, q) for p, q in zip(b0, b1))) / 32
    return cross - inner


NAMES = {"W": "water", "T": "tree/dark", "g": "marsh/grass", "p": "sand/path", "o": "other"}


def runs_of(cells):
    """[(first, last)] of consecutive integers"""
    out = []
    for c in sorted(cells):
        if out and c == out[-1][1] + 1:
            out[-1][1] = c
        else:
            out.append([c, c])
    return [tuple(r) for r in out]


def fmt_runs(cells, label):
    return ", ".join(f"{label}{a}" if a == b else f"{label}{a}-{b}" for a, b in runs_of(cells))


def analyse(entry, builts):
    a, d, b, k, note = entry
    sa, sb = SIDE[d]
    A, B = builts[a], builts[b]
    la, lb = A.length(sa), B.length(sb)
    lo, hi = max(0, k), min(la, k + lb)           # A-coordinates where both maps are present
    axis = "row" if sa in "EW" else "col"
    cells = list(range(lo, hi))
    n = max(1, len(cells))
    res = {"entry": entry, "lo": lo, "hi": hi, "axis": axis, "sa": sa, "sb": sb, "n": hi - lo}
    inside = lambda t: lo <= t < hi
    spec_a = {t for sp in A.spec_exits(sa) for t in sp if inside(t)}
    spec_b = {j + k for sp in B.spec_exits(sb) for j in sp if inside(j + k)}
    hint_a = {t for sp in A.hint_exits(sa) for t in sp if inside(t)}
    hint_b = {j + k for sp in B.hint_exits(sb) for j in sp if inside(j + k)}
    res["xa"], res["xb"] = sorted(spec_a | hint_a), sorted(spec_b | hint_b)
    cls_a = {t: A.cls(*A.edge_cell(sa, t)) for t in cells}
    cls_b = {t: B.cls(*B.edge_cell(sb, t - k)) for t in cells}
    pas_a = {t: A.passable(*A.edge_cell(sa, t)) for t in cells}
    pas_b = {t: B.passable(*B.edge_cell(sb, t - k)) for t in cells}
    open_water = [t for t in cells if cls_a[t] == "W" and cls_b[t] == "W" and pas_a[t] and pas_b[t]]
    res["open_water"] = open_water
    sev, reasons = 0, []
    notes = []

    # ---- exits
    land = spec_a | spec_b
    if land:
        res["mode"] = "land"
        both = spec_a & spec_b
        res["unmatched_a"], res["unmatched_b"] = sorted(spec_a - spec_b), sorted(spec_b - spec_a)
        if spec_a and spec_b:
            state = "aligned" if spec_a == spec_b else ("partial" if both else "disjoint")
        else:
            # one side has an exit, the other has none: what does the exit run into?
            mine, other_p, other_c = (spec_a, pas_b, cls_b) if spec_a else (spec_b, pas_a, cls_a)
            if any(other_p[t] for t in mine) and all(other_c[t] == "W" for t in mine if other_p[t]):
                state = "landing"                  # a pier/boardwalk end meeting open water
            elif any(other_p[t] for t in mine):
                state = "one-sided-open"           # the other side has open ground there but no exit drawn
            else:
                state = "one-sided-wall"
        res["state"] = state
        # an unmatched exit cell whose neighbour across the border is blocked runs into a wall
        walls = []
        for t in sorted((spec_a - spec_b) | (spec_b - spec_a)):
            if (t in spec_a and not pas_b[t]) or (t in spec_b and not pas_a[t]):
                walls.append(t)
        usable = [t for t in sorted(spec_a | spec_b) if pas_a[t] and pas_b[t]]
        res["blocked"] = walls if usable else sorted(spec_a | spec_b)
        if state in ("aligned", "partial") and not usable:
            state = res["state"] = "disjoint"
        um = len(res["unmatched_a"]) + len(res["unmatched_b"]) if state in ("aligned", "partial", "disjoint") else 0
        if state == "disjoint":
            sev = 3
            reasons.append("exits do not meet (no usable exit cell)" if not usable else "exits do not meet")
        elif state == "partial":
            sev = max(sev, 2)
            reasons.append(f"{um} exit cell(s) without a partner")
        elif state == "one-sided-open":
            sev = max(sev, 2)
            reasons.append("exit has no exit on the other side (open ground)")
        elif state == "one-sided-wall":
            sev = 3
            reasons.append("exit runs into a wall")
        if walls and usable and state in ("aligned", "partial"):
            sev = 3
            reasons.append(f"exit cell(s) {fmt_runs(walls, axis[0])} run into a wall on the other side")
    else:
        res["mode"] = "water"
        res["state"] = "channel"
        res["blocked"] = []
        res["unmatched_a"] = res["unmatched_b"] = []
        if not open_water:
            sev = 3
            reasons.append("no open water passage across the border")
        elif len(open_water) <= 2:
            sev = max(sev, 2)
            reasons.append(f"open water passage only {len(open_water)} cell(s) wide")
        arrows = sorted(hint_a | hint_b)
        shut = [t for t in arrows if t not in open_water]
        if shut:
            notes.append(f"mockup arrow row(s) {fmt_runs(shut, '')} (in {world.OUTDOOR[a]} {axis}s) are not in the open passage")
            sev = max(sev, 1)
        if arrows and not hint_a and not spec_a:
            notes.append(f"no exit drawn on {world.OUTDOOR[a]}'s {sa} side")
            sev = max(sev, 1)
        if arrows and not hint_b and not spec_b:
            notes.append(f"no exit drawn on {world.OUTDOOR[b]}'s {sb} side")
            sev = max(sev, 1)
        reasons += notes

    # ---- terrain along the whole overlapped border
    water_cut, hard, tone, pairs = [], [], [], {}
    for t in cells:
        i, j = t, t - k
        ca, cb = cls_a[t], cls_b[t]
        if (ca == "W") != (cb == "W"):
            water_cut.append(t)
            pairs.setdefault((ca, cb), []).append(t)
        else:
            sc = seam_score(A, sa, i, B, sb, j)
            if sc > 40:
                hard.append(t)
            elif sc > 20:
                tone.append(t)
    res["water_cut"], res["hard"], res["tone"], res["pairs"] = water_cut, hard, tone, pairs
    if len(water_cut) >= 8:
        sev = max(sev, 3)
    elif len(water_cut) >= 3:
        sev = max(sev, 2)
    elif water_cut:
        sev = max(sev, 1)
    if water_cut:
        reasons.append(f"water cut over {len(water_cut)} cells")
    if n >= 6:
        if len(hard) >= 0.6 * n:
            sev = max(sev, 3)
        elif len(hard) >= 0.3 * n:
            sev = max(sev, 2)
        elif len(hard) >= 0.1 * n:
            sev = max(sev, 1)
        if len(tone) >= 0.5 * n:
            sev = max(sev, 1)
    elif len(hard) >= 3:
        sev = max(sev, 1)
    if hard:
        reasons.append(f"hard colour cut over {len(hard)} cells")
    if n >= 6 and len(tone) >= 0.5 * n:
        reasons.append(f"grass/ground tone differs across the border ({len(tone)} cells)")
    res["sev"] = ("OK", "LOW", "MEDIUM", "HIGH")[sev]
    res["reasons"] = reasons
    return res


def describe(res, builts):
    a, d, b, k, note = res["entry"]
    ax = res["axis"]
    lines = []
    names = world.OUTDOOR
    ca = fmt_runs(res["xa"], "")
    cb = fmt_runs([t - k for t in res["xb"]], "")
    st = res["state"]
    if res["mode"] == "land":
        if st == "aligned":
            lines.append(f"exits line up: {names[a]} {ax}s {ca} meet {names[b]} {ax}s {cb}")
        elif st == "partial":
            lines.append(f"exits partly line up: {names[a]} {ax}s {ca} / {names[b]} {ax}s {cb}; cells without a partner: "
                         f"{names[a]} {fmt_runs(res['unmatched_a'], '') or 'none'}, {names[b]} {fmt_runs([t - k for t in res['unmatched_b']], '') or 'none'}")
        elif st == "disjoint":
            lines.append(f"exits do NOT meet: {names[a]} {ax}s {ca} / {names[b]} {ax}s {cb}")
        elif st == "landing":
            who = names[a] if res["xa"] else names[b]
            lines.append(f"{who}'s exit (pier/boardwalk end) runs out into open water on the other side: fine")
        elif st == "one-sided-open":
            who, other = (names[a], names[b]) if res["xa"] else (names[b], names[a])
            lines.append(f"only {who} has an exit here ({ax}s {ca or cb} of {names[a]}); {other}'s edge there is open ground with no exit built")
        elif st == "one-sided-wall":
            who, other = (names[a], names[b]) if res["xa"] else (names[b], names[a])
            lines.append(f"only {who} has an exit here ({ax}s {ca or cb} of {names[a]}); {other}'s edge there is a wall")
        if res["blocked"]:
            lines.append(f"exit cells blocked by collision on one side: {names[a]} {ax}s {fmt_runs(res['blocked'], '')}")
    else:
        ow = res["open_water"]
        lines.append(f"boat join: open water passage across the border at {names[a]} {ax}s {fmt_runs(ow, '') or 'NONE'} ({len(ow)} cells)")
        arrows = []
        if res["xa"]:
            arrows.append(f"{names[a]} arrow {ax}s {ca}")
        if res["xb"]:
            arrows.append(f"{names[b]} arrow {ax}s {cb} (= {names[a]} {ax}s {fmt_runs(res['xb'], '')})")
        if arrows:
            lines.append("mockup arrows: " + "; ".join(arrows))
    for r in res["reasons"]:
        if r.startswith("no exit drawn") or r.startswith("mockup arrow"):
            lines.append(r)
    for (pa, pb), cells in sorted(res["pairs"].items(), key=lambda kv: -len(kv[1])):
        lines.append(f"hard cut: {NAMES[pa]} ({names[a]}) | {NAMES[pb]} ({names[b]}) over {len(cells)} cells, "
                     f"{names[a]} {ax}s {fmt_runs(cells, '')}")
    if res["hard"]:
        lines.append(f"hard colour cut (seam score over 40) over {len(res['hard'])} of {res['n']} cells, "
                     f"{names[a]} {ax}s {fmt_runs(res['hard'], '')}")
    if res["tone"]:
        lines.append(f"slight tone shift (seam score 20-40) over {len(res['tone'])} of {res['n']} cells, "
                     f"{names[a]} {ax}s {fmt_runs(res['tone'], '')}")
    if not res["pairs"] and not res["hard"] and not res["tone"]:
        lines.append("terrain continues across the border")
    return lines


# ------------------------------------------------------------------ contact sheet
SEV_COL = {"OK": (60, 170, 80), "LOW": (200, 190, 40), "MEDIUM": (240, 140, 30), "HIGH": (230, 50, 50)}


def seam_panel(res, builts, scale=3, depth=8, win=20):
    a, d, b, k, note = res["entry"]
    sa, sb = res["sa"], res["sb"]
    A, B = builts[a], builts[b]
    lo, hi = res["lo"], res["hi"]
    marks = sorted(set(res["xa"]) | set(res["xb"]))
    centre = (sum(marks) / len(marks)) if marks else (lo + hi) / 2
    w0 = int(round(centre - win / 2))
    w0 = max(lo - 3, min(w0, hi + 3 - win))
    cells = range(w0, w0 + win)
    cs = CELL * scale
    horiz = sa in "EW"
    if horiz:
        P = Image.new("RGB", (2 * depth * cs, win * cs), (40, 40, 40))
    else:
        P = Image.new("RGB", (win * cs, 2 * depth * cs), (40, 40, 40))

    def cut(bm, side, i0, i1):
        """the depth cells nearest the border of map bm on `side`, for edge cells i0..i1-1 (out of range: left dark)"""
        lenb = bm.length(side)
        a0, a1 = max(0, i0), min(lenb, i1)
        if a1 <= a0:
            return None, 0
        if side == "E":
            box = ((bm.w - depth) * 16, a0 * 16, bm.w * 16, a1 * 16)
        elif side == "W":
            box = (0, a0 * 16, depth * 16, a1 * 16)
        elif side == "S":
            box = (a0 * 16, (bm.h - depth) * 16, a1 * 16, bm.h * 16)
        else:
            box = (a0 * 16, 0, a1 * 16, depth * 16)
        return bm.im.crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.NEAREST), a0 - i0

    ia, offa = cut(A, sa, w0, w0 + win)
    ib, offb = cut(B, sb, w0 - k, w0 - k + win)
    if horiz:
        # A is on the left when it is the west side of the join (d == 'right'), else on the right
        ax = 0 if sa == "E" else depth * cs
        bx = depth * cs if sa == "E" else 0
        if ia: P.paste(ia, (ax, offa * cs))
        if ib: P.paste(ib, (bx, offb * cs))
        seam = depth * cs
    else:
        ay = 0 if sa == "S" else depth * cs
        by = depth * cs if sa == "S" else 0
        if ia: P.paste(ia, (offa * cs, ay))
        if ib: P.paste(ib, (offb * cs, by))
        seam = depth * cs
    dr = ImageDraw.Draw(P)
    if horiz:
        dr.line([(seam, 0), (seam, P.height)], fill=(255, 0, 255), width=2)
    else:
        dr.line([(0, seam), (P.width, seam)], fill=(255, 0, 255), width=2)
    ok = set(res["xa"]) & set(res["xb"])
    for t in marks:
        if not (w0 <= t < w0 + win):
            continue
        col = (255, 235, 0) if t in ok else (255, 70, 70)
        u = (t - w0) * cs
        if horiz:
            dr.rectangle([seam - 4, u + 3, seam + 4, u + cs - 3], fill=col)
        else:
            dr.rectangle([u + 3, seam - 4, u + cs - 3, seam + 4], fill=col)
    return P


def contact_sheet(results, builts, path, ncols=4):
    scale, depth, win = 3, 8, 20
    pw, ph = win * CELL * scale, win * CELL * scale          # panel content box (a vertical join is 20 wide x 16 high cells)
    head = 74
    cellw, cellh = pw + 16, ph + head + 16
    rows = (len(results) + ncols - 1) // ncols
    sheet = Image.new("RGB", (ncols * cellw, rows * cellh), (24, 24, 28))
    dr = ImageDraw.Draw(sheet)
    f1, f2 = font(26), font(19, bold=False)
    for n, res in enumerate(results):
        a, d, b, k, note = res["entry"]
        x, y = (n % ncols) * cellw + 8, (n // ncols) * cellh + 8
        P = seam_panel(res, builts, scale, depth, win)
        sev = res["sev"]
        dr.rectangle([x, y, x + pw, y + head - 6], fill=(40, 40, 46))
        dr.rectangle([x, y, x + 12, y + head - 6], fill=SEV_COL[sev])
        dr.text((x + 22, y + 4), f"{n + 1:2d}. {world.OUTDOOR[a]} {d} {world.OUTDOOR[b]}  ({k:+d})  {sev}", font=f1, fill=(255, 255, 255))
        sub = "; ".join(res["reasons"]) or "clean seam"
        dr.text((x + 22, y + 38), sub[:110], font=f2, fill=(205, 205, 210))
        sheet.paste(P, (x + (pw - P.width) // 2, y + head + (ph - P.height) // 2))
    sheet.save(path)
    return sheet.size


# ------------------------------------------------------------------ report
def write_report(results, comps, conflicts, overlaps_main, overlaps_apart, apart_names, path, sheet_size):
    counts = {s: 0 for s in ("HIGH", "MEDIUM", "LOW", "OK")}
    for r in results:
        counts[r["sev"]] += 1
    L = []
    L.append("# World seams\n")
    L.append("Generated by `tools/mapgen/world_stitch.py` from the table in `tools/mapgen/world.py`; "
             "images: `00_world.png`, `00_world_full.png`, contact sheet `00_world_seams.png` (3x crop of each join, panel numbers below; "
             "magenta = the border, yellow bar = an exit cell with a partner, red bar = an exit cell without one).\n")
    L.append(f"**{len(results)} connections: " + ", ".join(f"{counts[s]} {s}" for s in ("HIGH", "MEDIUM", "LOW", "OK")) + ".**\n")
    L.append("Severity: HIGH = exits do not meet, an exit runs into a wall or is blocked, no open water across a boat border, "
             "water cut over 8+ cells, 3+ exit cells without a partner, or a hard colour cut over 60% of the border; "
             "MEDIUM = 1-2 exit cells without a partner, an exit with open ground (no exit) on the other side, a 1-2 cell boat passage, "
             "water cut over 3-7 cells, or a hard colour cut over 30%; "
             "LOW = water cut over 1-2 cells, a hard colour cut over 10%, an arrow row outside the open passage, a missing mockup arrow on a boat border, "
             "or a palette tone shift over half the border; OK otherwise. "
             "A 'water cut' is a border cell that is water on one side only (judged from the render's colours, so a dock over water counts as land). "
             "'Colour cut' is check.py's seam score (colour jump across the border minus the texture's own jump): over 40 is a hard cut, "
             "20-40 a tone shift (the route and town tilesets draw their grass slightly differently).\n")
    L.append("## Summary table\n")
    L.append("| # | join (A direction B, offset) | border cells | exits | water cut | colour cuts (cells) | severity |")
    L.append("|---|---|---|---|---|---|---|")
    for n, r in enumerate(results, 1):
        a, d, b, k, _ = r["entry"]
        ex = (f"boat, {len(r['open_water'])} open" if r["mode"] == "water" else
              r["state"] if r["state"] != "partial" else f"partial ({len(r['unmatched_a']) + len(r['unmatched_b'])} unmatched)")
        L.append(f"| {n} | {world.OUTDOOR[a]} {d} {world.OUTDOOR[b]} ({k:+d}) | {r['n']} | {ex} | {len(r['water_cut'])} | {len(r['hard'])} hard, {len(r['tone'])} tone | **{r['sev']}** |")
    L.append("\n## Per join (worst first)\n")
    order = sorted(range(len(results)), key=lambda i: (-("OK LOW MEDIUM HIGH".split().index(results[i]["sev"])), i))
    for i in order:
        r = results[i]
        a, d, b, k, note = r["entry"]
        L.append(f"### {i + 1}. {world.OUTDOOR[a]} {d} {world.OUTDOOR[b]}, offset {k:+d}: {r['sev']}")
        L.append(f"- table note: {note}")
        sa, sb = r["sa"], r["sb"]
        L.append(f"- border: {world.OUTDOOR[a]} {sa} edge against {world.OUTDOOR[b]} {sb} edge; the maps share {r['n']} cells "
                 f"({r['axis']}s {r['lo']}-{r['hi'] - 1} of {world.OUTDOOR[a]})")
        for line in describe(r, BUILTS):
            L.append(f"- {line}")
        L.append("")
    L.append("## Layout\n")
    for pos_name, ov in (("main world", overlaps_main), ("Pointe Rouge group", overlaps_apart)):
        if ov:
            L.append(f"Overlapping rectangles in the {pos_name} (the connection graph is not planar here; GBA allows it):")
            for a, b, w, h in ov:
                L.append(f"- {world.OUTDOOR[a]} and {world.OUTDOOR[b]} overlap by {w} x {h} cells")
        else:
            L.append(f"No two maps overlap in the {pos_name}.")
    if conflicts:
        L.append("\nConnections that disagree about where a map sits (a cycle with inconsistent offsets):")
        for e, p1, p2 in conflicts:
            L.append(f"- {e[0]} {e[1]} {e[2]} ({e[3]:+d}): placed at {p1} and {p2}")
    unreached = [world.OUTDOOR[s] for s in apart_names]
    L.append(f"\nNot reached by walking the connections from Isle Marais: {', '.join(unreached) if unreached else 'none'} "
             "(laid out separately in the picture, in the red dashed box).")
    L.append("\n## Questions\n")
    for q in world.QUESTIONS:
        L.append(f"- {q}")
    L.append("\n## Warps, not connections\n")
    for m, side, what in world.WARPS:
        L.append(f"- {world.OUTDOOR.get(m, m)} {side}: {what}")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    return counts


BUILTS = {}


def main():
    maps = world.Maps()
    cache = {}
    for s in world.OUTDOOR:
        BUILTS[s] = Built(s, maps, cache)
    size = {s: (BUILTS[s].w, BUILTS[s].h) for s in BUILTS}
    comps, conflicts = lay_out(size)
    main_pos = comps[0]
    # every other component goes beside the main world; the first (largest) is placed near Crescent City's north
    apart_pos = {}
    target = (main_pos["crescent_city"][0] + 30, main_pos["crescent_city"][1] - 130) if "crescent_city" in main_pos else (0, 0)
    rest = dict(main_pos)
    for comp in comps[1:]:
        placed = place_apart(rest, comp, size, target)
        apart_pos.update(placed)
        rest.update(placed)
    overlaps_main = overlap_pairs(main_pos, size)
    overlaps_apart = []
    for comp in comps[1:]:
        overlaps_apart += overlap_pairs({s: apart_pos[s] for s in comp}, size)
    print(f"{len(main_pos)} maps reached from {START}; not reached: {sorted(apart_pos)}")
    print("overlaps:", [(world.OUTDOOR[a], world.OUTDOOR[b], w, h) for a, b, w, h in overlaps_main + overlaps_apart] or "none")
    if conflicts:
        print("CONFLICTS:", conflicts)

    names = world.OUTDOOR
    canvas, origin, allpos, in_overlap = draw_world(BUILTS, main_pos, apart_pos, size, overlaps_main + overlaps_apart, OUT)
    W, H = canvas.size
    print(f"world canvas {W} x {H} px at 16 px per cell")
    # full resolution
    full_fs = 30
    if max(W, H) <= 16000:
        full = canvas.copy()
        annotate(full, 1, origin, allpos, size, in_overlap, list(apart_pos), names, full_fs)
        full.save(os.path.join(OUT, "00_world_full.png"))
        print("wrote 00_world_full.png", full.size)
    else:
        n = 0
        tw = 8000
        ann = canvas.copy()
        annotate(ann, 1, origin, allpos, size, in_overlap, list(apart_pos), names, full_fs)
        for y in range(0, H, tw):
            for x in range(0, W, tw):
                ann.crop((x, y, min(W, x + tw), min(H, y + tw))).save(os.path.join(OUT, f"00_world_full_{n}.png"))
                n += 1
        print(f"wrote {n} tiles 00_world_full_<n>.png")
    # downscaled
    scale = 8000 / max(W, H)
    small = canvas.resize((round(W * scale), round(H * scale)), Image.LANCZOS)
    annotate(small, scale, origin, allpos, size, in_overlap, list(apart_pos), names, 34)
    small.save(os.path.join(OUT, "00_world.png"))
    print("wrote 00_world.png", small.size)

    # seams
    results = [analyse(e, BUILTS) for e in world.WORLD]
    sheet = contact_sheet(results, BUILTS, os.path.join(OUT, "00_world_seams.png"))
    print("wrote 00_world_seams.png", sheet)
    counts = write_report(results, comps, conflicts, overlaps_main, overlaps_apart, sorted(apart_pos),
                          os.path.join(OUT, "00_world_seams.md"), sheet)
    print("seams:", counts)
    for n, r in enumerate(results, 1):
        a, d, b, k, _ = r["entry"]
        print(f"{n:2d} {r['sev']:6s} {a} {d} {b} {k:+d}: {'; '.join(r['reasons']) or 'clean'}")


if __name__ == "__main__":
    main()

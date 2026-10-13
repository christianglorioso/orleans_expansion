"""Levee END CAPS where a levee runs out into open water (Storm's Edge's canal mouth), 2026-10-13. Art for review: not integrated.

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/make_levee_caps.py

levee.py draws a levee pixel by pixel from distance fields; where a run ends it tapers into the map's ordinary shore. Where a run
ends in OPEN WATER (the canal opening into a lake) that taper leaves a straight stone shelf and a slope cut flat (see the review
sheet). render_caps() is levee.render with three changes, so every pixel still comes from levee._levee_px (the same riprap, earth,
slope, crest and foam, the same palette, the same 16 px textures, so the cap joins the run's own cells pixel for pixel):
  1. every convex corner of the levee ground that has water on both sides is rounded to RADIUS px (the head becomes a rounded nose);
  2. a meadow shore cell beside the head no longer counts as "the end of the run" for the head itself, so the riprap, the earth band
     and the slope wrap all the way round the nose instead of thinning out there; the run still tapers into the meadow's ordinary
     bank along its outer side (TAPER px from where the meadow shore meets it);
  3. the head's own cells and the water round it are drawn (the region grows by one cell round a head), so nothing is clipped.
Two head shapes, both drawn for the west and east levees: JET = 1 (the levee reaches one cell past the meadow's shore: a jetty head
with water on three sides) and JET = 0 (flush with the shore: the face turns the corner onto the lake and runs out along it).

writes  tools/mapgen/tilesets/levee/caps/cap_<W|E>_j<JET>_<dx>_<dy>.png   RGBA overlays (clear where the ground shows), cell offset
            (dx, dy) from the levee's head cell on the canal side, plus caps.json (cell -> the ground it overlays: ekat:water_C or
            ekat:grass, as build.py's levee() names an overlay's base). The rollout names them lv_<sha1(overlay + under)> as usual.
        the mock images used by levee_barrier_review.py (the review sheet).
"""
import json
import math
import os
import sys
import warnings

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, MAPGEN)
import levee  # noqa: E402
from levee import _blur, _edt, _hash, _levee_px, END, TOE, WIDTH  # noqa: E402

RADIUS = 11      # px: the nose's rounding
CLEAR = 13.0     # px of water beyond the head's waterline painted open (the tileset's bank lip there goes)
TAPER = 14.0     # px over which the outer-side riprap fades into the meadow's ordinary bank
CAP_DIR = os.path.join(MAPGEN, "tilesets", "levee", "caps")


def convex_corners(grid, bank, wet):
    """(cell, corner) of every levee-ground cell corner with water on both edge sides and the diagonal"""
    out = []
    for x, y in bank:
        for cx, cy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            if wet(x + cx, y) and wet(x, y + cy) and wet(x + cx, y + cy):
                out.append(((x, y), (cx, cy)))
    return out


def heads_of(grid, bank, wet):
    """levee cells at the end of a run that ends in water: a bank cell with water beyond it along the run (vertical runs here)"""
    return {(x, y) for x, y in bank if (wet(x, y - 1) and (x, y + 1) in bank) or (wet(x, y + 1) and (x, y - 1) in bank)}


def render_caps(grid, bank, base, blocked=frozenset(), radius=RADIUS):
    """levee.render with rounded noses where a run ends in water (see the module docstring); {(x, y): RGBA 16x16 overlay}"""
    h, w = len(grid), len(grid[0])
    wet_cell = lambda x, y: (not (0 <= x < w and 0 <= y < h)) or grid[y][x] in levee.WATER
    heads = heads_of(grid, bank, wet_cell)
    ring1 = set(bank)
    for x, y in bank:
        ring1 |= {(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if 0 <= x + i < w and 0 <= y + j < h}
    region = set(bank)
    for x, y in bank:
        r = 2 if (x, y) in heads else 1
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if 0 <= x + i < w and 0 <= y + j < h and wet_cell(x + i, y + j):
                    region.add((x + i, y + j))
    x0 = max(0, min(x for x, _ in region) - 4)
    y0 = max(0, min(y for _, y in region) - 4)
    x1 = min(w, max(x for x, _ in region) + 5)
    y1 = min(h, max(y for _, y in region) + 5)
    W, H = (x1 - x0) * 16, (y1 - y0) * 16
    cell_mask = lambda pred: np.kron(np.array([[1.0 if pred(x, y) else 0.0 for x in range(x0, x1)]
                                               for y in range(y0, y1)], dtype=np.float32),
                                     np.ones((16, 16), dtype=np.float32))
    water = _blur(cell_mask(wet_cell), 3) > 0.5
    # 1. the nose: every convex corner of the levee ground with water round it is rounded off
    for (cx, cy), (sx, sy) in convex_corners(grid, bank, wet_cell):
        px0 = (cx - x0) * 16 + (0 if sx < 0 else 16)            # the corner point
        py0 = (cy - y0) * 16 + (0 if sy < 0 else 16)
        ccx, ccy = px0 - sx * radius, py0 - sy * radius          # the rounding circle's centre, inside the cell
        for yy in range(int(min(py0, ccy)), int(max(py0, ccy))):
            for xx in range(int(min(px0, ccx)), int(max(px0, ccx))):
                if 0 <= xx < W and 0 <= yy < H and math.hypot(xx + 0.5 - ccx, yy + 0.5 - ccy) > radius:
                    water[yy, xx] = True
    d_land = _edt(water)
    d_water = _edt(~water)
    d = np.where(water, -d_water, d_land)
    ds = _blur(d, 4)
    gy, gx = np.gradient(ds)
    ny = gy / (np.hypot(gx, gy) + 1e-6)
    vis = np.clip((-ny + 1) / 2, 0, 1)
    width = np.full(d.shape, float(WIDTH), dtype=np.float32)

    def near(x, y, pred):
        return any(0 <= x + i < w and 0 <= y + j < h and pred(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1))

    def shore(x, y):
        return (not wet_cell(x, y) and (x, y) not in bank and near(x, y, wet_cell)
                and near(x, y, lambda i, j: (i, j) in bank))
    # 2. a meadow shore cell beside a head is where the OUTER side of the run meets the meadow's bank, not the end of the run
    junction = {(x, y) for x in range(x0, x1) for y in range(y0, y1) if shore(x, y) and near(x, y, lambda i, j: (i, j) in heads)}
    ends_at = {(x, y) for x in range(x0, x1) for y in range(y0, y1) if (shore(x, y) and (x, y) not in junction) or (x, y) in blocked}
    ends = cell_mask(lambda x, y: (x, y) in ends_at) > 0.5
    back = _blur(cell_mask(lambda x, y: not wet_cell(x, y) and (x, y) not in bank and not near(
        x, y, lambda i, j: (i, j) in ends_at)), 3) > 0.5
    avail = _blur(d + _edt(back), 6)
    width = np.minimum(width, np.maximum(8, avail - 2))
    width = np.round(width / 4) * 4
    e = _edt(ends)
    taper = np.clip((e - 2) / (END - 2), 0, 1)
    width = TOE + (width - TOE) * taper ** 0.8
    # the outer side's riprap fades out where it meets the meadow's ordinary bank: distance from the junction cells' shore line
    jmask = cell_mask(lambda x, y: (x, y) in junction) > 0.5
    ej = _edt(jmask) if jmask.any() else np.full(d.shape, 99.0, dtype=np.float32)
    # toward the junction the face sinks into the meadow too (the run's outer side is crest-level meadow)
    tj = np.clip((ej - 6) / TAPER, 0, 1) ** 1.5
    width = TOE + (width - TOE) * tj
    fy, fx = np.gradient(width - d)
    steep = np.maximum(np.hypot(fx, fy), 0.25)
    inner = _edt(cell_mask(lambda x, y: (x, y) not in region) > 0.5)

    def keep(sx, sy, r):
        X, Y = sx - x0 * 16, sy - y0 * 16
        if not (0 <= X < W and 0 <= Y < H) or inner[Y, X] <= r + 1.5:
            return False
        ev, jv = float(e[Y, X]), float(ej[Y, X])
        if jv < TAPER and not -TOE + r * 0.6 <= float(d[Y, X]) <= TOE:
            return False
        if jv < TAPER and _hash(sx, sy, 17) > (jv - 2) / (TAPER - 2) * 1.2:
            return False              # fewer stones toward the meadow's own bank
        if ev <= END and not -TOE + r * 0.6 <= float(d[Y, X]) <= TOE:
            return False
        if ev > END:
            return True
        t = max(0.0, (ev - 2) / (END - 2))
        return _hash(sx, sy, 13) < t * 1.3 - 0.15

    # 3. the water round a head is open water: the tileset's bank piece there (drawn for the levee ground beside it) goes
    #    (a band beyond the riprap's toe, fading out toward the meadow's own bank so its shore line is never cut square)
    clear = {(x + i, y + j) for x, y in heads for i in (-1, 0, 1) for j in (-1, 0, 1) if wet_cell(x + i, y + j)}
    out = {}
    for cx, cy in sorted(region):
        bp = base(cx, cy).convert("RGB").load()
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        px = im.load()
        changed = False
        for yy in range(16):
            for xx in range(16):
                X, Y = (cx - x0) * 16 + xx, (cy - y0) * 16 + yy
                gxp, gyp = cx * 16 + xx, cy * 16 + yy
                dv, ev = float(d[Y, X]), float(e[Y, X])
                if (dv < -9 and not ((cx, cy) in clear and dv > -CLEAR)) or ev < 0.5:
                    continue
                jv = float(ej[Y, X])
                if jv < 1.0 and dv < 0:
                    continue              # the meadow's own bank cell stays as the tileset draws it
                c = _levee_px(gxp, gyp, dv, float(width[Y, X]), float(vis[Y, X]), ev if jv >= TAPER else min(ev, END * jv / TAPER),
                              keep, float(steep[Y, X]))
                if c in (levee.EARTH, levee.EARTH_D) and jv < TAPER and dv > 0:
                    c = None              # no earth seam running off the head into the meadow's grass
                if c in (levee.WATER_C, levee.WATER_D, levee.FOAM) and (cx, cy) not in ring1 and (cx, cy) not in clear:
                    c = None              # past the levee's own ring only its stones are laid (the meadow's bank stays)
                if c is None and (cx, cy) in clear and -CLEAR < dv < 0 and jv > 10 + (CLEAR + dv) * 0.5:
                    c = levee.WATER_C
                if c is None:
                    continue
                px[xx, yy] = c + (255,)
                changed |= c != bp[xx, yy]
        if changed:
            out[(cx, cy)] = im
    return out


# ---------------------------------------------------------------- the Storm's Edge canal-mouth mock (in memory; nothing written to data/)
def storms_edge_mock(tip=3, jet=1, caps=True):
    """Storm's Edge built in memory with its north edge receded into a lake: the levees (x 22-23, 29-30) end at row `tip`, the
    meadow's shore `jet` rows further south, wandering back from there. Returns (image, levee overlays, grid, under-names)."""
    warnings.filterwarnings("ignore")
    cwd = os.getcwd()
    os.chdir(ROOT)
    import build
    from render import Tilesets
    cap = {}
    orig = levee.render

    def capture(grid, bank, base, blocked=frozenset()):
        cap["args"] = (grid, bank, base, blocked)
        return {}
    levee.render = capture
    try:
        b = build.Builder(os.path.join(MAPGEN, "maps", "storms_edge.json"))
        shore = {}
        for x in range(12, 42):
            if x in (22, 23, 29, 30):
                shore[x] = tip
            else:
                off = min(abs(x - 21.5), abs(x - 30.5))
                shore[x] = tip + jet + (1 if off > 2 else 0) + (1 if off > 5 else 0) + (1 if 8 < off < 11 else 0)
        for x, s_ in shore.items():
            for y in range(s_):
                if b.grid[y][x] in ".B:%":
                    b.grid[y][x] = "~"
        b.draw()
        grid, bank, base, blocked = cap["args"]
        cells = render_caps(grid, bank, base, blocked) if caps else orig(grid, bank, base, blocked)
        ts = Tilesets(os.path.join(ROOT, b.ts["primary_dir"]), os.path.join(ROOT, b.ts["secondary_dir"]))
        inv = {}
        for n, v in build.MAPPING.items():
            inv.setdefault(v, n)
        im = Image.new("RGB", (b.w * 16, b.h * 16))
        for y in range(b.h):
            for x in range(b.w):
                im.paste(ts.metatile(b.blocks[y][x] & 0x3FF).convert("RGB"), (x * 16, y * 16))
        for (x, y), ov in cells.items():
            im.paste(ov, (x * 16, y * 16), ov)
        under = {c: inv.get(b.blocks[c[1]][c[0]] & 0x3FF, "?") for c in cells}
        return im, cells, [list(r) for r in b.grid], under
    finally:
        levee.render = orig
        os.chdir(cwd)


def head_cells(cells, grid, tip):
    """the cap pieces: overlays in the 3 x 4 window round each head (rows tip-1 .. tip+2), keyed by side and offset"""
    out = {}
    for side, hx in (("W", 23), ("E", 29)):      # the head cell on the canal side of each levee
        for (x, y), ov in cells.items():
            dx, dy = x - hx, y - tip
            if -2 <= dx <= 2 and -1 <= dy <= 2 and not (side == "W" and dx > 0) and not (side == "E" and dx < 0):
                out[(side, dx, dy)] = ov
    return out


def main(argv):
    os.makedirs(CAP_DIR, exist_ok=True)
    index = {}
    for jet in (1, 0):
        im, cells, grid, under = storms_edge_mock(3, jet)
        for (side, dx, dy), ov in sorted(head_cells(cells, grid, 3).items()):
            hx = 23 if side == "W" else 29
            nm = f"cap_{side}_j{jet}_{dx:+d}_{dy:+d}".replace("+", "p").replace("-", "m")
            ov.save(os.path.join(CAP_DIR, nm + ".png"))
            index[nm] = {"side": side, "jet": jet, "offset_from_canal_side_head": [dx, dy],
                         "under": under[(hx + dx, 3 + dy)], "storms_edge_cell": [hx + dx, 3 + dy]}
    json.dump({"_comment": "Levee end caps (make_levee_caps.py): RGBA overlays over `under`, offset (dx, dy) from the levee's head cell "
                           "on the canal side (west levee x 23, east levee x 29 on Storm's Edge), head row = dy 0, the lake north. "
                           "jet 1: the levee reaches one cell past the meadow's shore; jet 0: flush with it.", "cells": index},
              open(os.path.join(CAP_DIR, "caps.json"), "w"), indent=1)
    print(f"wrote {len(index)} cap cells to {os.path.relpath(CAP_DIR, ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])

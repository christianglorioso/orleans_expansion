"""Surf viewpoints (edge feather rollout, user rule 2026-10-13: "every Surf-reachable cell counts as a viewpoint").

usage (from the decomp root):  python tools/mapgen/surf_check.py [--views DIR] [map_stem ...]

Reads the built map.bin files (nothing is written except the pictures).  With HM Surf and every story water gate open, a water cell is
Surf-reachable when it lies in a water component (across map connections) that touches walkable land.  For every unconnected-edge position
the check walks inward from the edge: the first cell that is blocked (a prop, the canopy wall, an edge cell) or is land ends the line of
sight harmlessly; a Surf-reachable water cell met first means a surfer can stand there with open water between him and the border.
That is an EXPOSED position (corners beside a connection are left to the join).  With --views DIR a contact sheet per map is written:
the 15 x 10 camera view (7 columns each side, 5 rows above, 4 below the player) from the Surf-reachable cell nearest the edge every 5
positions along each unconnected stretch, exposed views outlined in red, plus a text list of the bad views.
"""
import json
import os
import struct
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import borders  # noqa: E402
import gba_view as gv  # noqa: E402
import world  # noqa: E402

ROOT = world.ROOT
WATER = range(0x10, 0x16)


def attrs(path):
    raw = open(path, "rb").read()
    return struct.unpack(f"<{len(raw) // 2}H", raw)


class Surf:
    def __init__(self, keys=None):
        self.wd = gv.World()
        self.keys = keys or list(borders.STYLE)
        self.grid = {}
        pa = attrs(os.path.join(ROOT, "data/tilesets/primary/orleans_general/metatile_attributes.bin"))
        for stem in self.wd.maps.info:
            lay = self.wd.maps.info[stem]["layout"]
            w, h = self.wd.size(stem)
            sec = attrs(os.path.join(ROOT, "data/tilesets/secondary", gv.snake(lay["secondary_tileset"]), "metatile_attributes.bin"))
            blocks = self.wd.blocks[stem]
            water, blocked = set(), set()
            land = set()
            for y in range(h):
                for x in range(w):
                    v = blocks[y * w + x]
                    mid, coll = v & 0x3FF, (v >> 10) & 3
                    a = pa[mid] if mid < 512 else sec[mid - 512] if mid - 512 < len(sec) else 0
                    beh = a & 0x1FF
                    if coll:
                        blocked.add((x, y))
                    elif beh in WATER:
                        water.add((x, y))
                    else:
                        land.add((x, y))
            self.grid[stem] = {"w": w, "h": h, "water": water, "blocked": blocked, "land": land}
        self.reach = self.flood()

    def neighbours(self, stem, c):
        g = self.grid[stem]
        x, y = c
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < g["w"] and 0 <= ny < g["h"]:
                yield stem, (nx, ny)
                continue
            d = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}[(dx, dy)]
            for cd, tgt, off in self.wd.conns[stem]:
                if cd != d:
                    continue
                tg = self.grid[tgt]
                if d in ("right", "left"):
                    c2 = (0 if d == "right" else tg["w"] - 1, y - off)
                else:
                    c2 = (x - off, 0 if d == "down" else tg["h"] - 1)
                if 0 <= c2[0] < tg["w"] and 0 <= c2[1] < tg["h"]:
                    yield tgt, c2

    def real_land(self):
        """land cells in a walkable component of 6+ cells (across connections): a one-cell stone (a snag's top) inside a sealed pocket is not a shore"""
        seen, keep = set(), set()
        for stem, g in self.grid.items():
            for c in sorted(g["land"]):
                if (stem, c) in seen:
                    continue
                comp, q = [], deque([(stem, c)])
                seen.add((stem, c))
                while q:
                    s, p = q.popleft()
                    comp.append((s, p))
                    for s2, p2 in self.neighbours(s, p):
                        if p2 in self.grid[s2]["land"] and (s2, p2) not in seen:
                            seen.add((s2, p2))
                            q.append((s2, p2))
                if len(comp) >= 6:
                    keep |= set(comp)
        return keep

    def flood(self):
        """Surf-reachable water: components that touch walkable land"""
        shore = self.real_land()
        seen, comps = set(), []
        for stem, g in self.grid.items():
            for c in sorted(g["water"]):
                if (stem, c) in seen:
                    continue
                comp, touches, q = [], False, deque([(stem, c)])
                seen.add((stem, c))
                while q:
                    s, p = q.popleft()
                    comp.append((s, p))
                    for s2, p2 in self.neighbours(s, p):
                        g2 = self.grid[s2]
                        if p2 in g2["land"] and (s2, p2) in shore:
                            touches = True
                        elif p2 in g2["water"] and (s2, p2) not in seen:
                            seen.add((s2, p2))
                            q.append((s2, p2))
                if touches:
                    comps.append(comp)
        return {c for comp in comps for c in comp}

    def exposed(self, stem):
        """[(side, i, k)]: unconnected-edge positions and the depth of the first Surf-reachable cell with a clear line to the border"""
        g = self.grid[stem]
        w, h = g["w"], g["h"]
        sp = borders.unconnected(stem)
        from feather import dilate, seam_zone
        near_join = dilate(seam_zone(stem, 3), 4, w, h)
        out = []
        for side in "NSWE":
            cell = {"N": lambda i, k: (i, k), "S": lambda i, k: (i, h - 1 - k),
                    "W": lambda i, k: (k, i), "E": lambda i, k: (w - 1 - k, i)}[side]
            for lo, hi in sp[side]:
                for i in range(lo, hi):
                    first = None
                    for k in range(8):
                        c = cell(i, k)
                        if c in g["blocked"] or c in g["land"]:
                            break
                        if c in g["water"] and (stem, c) in self.reach:
                            first = (k, c)
                            break
                    near = cell(i, 0) in near_join
                    out.append((side, i, first[0] if first else None, first[1] if first else cell(i, 6), near))
        return out


def view(surf, stem, cell, scale=2, mark=None):
    """the camera's 15 x 10 window around the player at `cell`, as the engine draws it (border blocks, neighbour strips)"""
    wd = surf.wd
    grid, src, W, H = wd.backup(stem)
    ts = wd.ts(stem)
    o = gv.MAP_OFFSET
    px, py = cell[0] + o, cell[1] + o
    x0, y0 = px - 7, py - 5
    im = gv.Image.new("RGB", (15 * 16, 10 * 16))
    for j in range(10):
        for i in range(15):
            bx, by = x0 + i, y0 + j
            if 0 <= bx < W and 0 <= by < H:
                im.paste(gv.cell_img(ts, grid[by * W + bx]), (i * 16, j * 16))
    d = gv.ImageDraw.Draw(im)
    d.rectangle([7 * 16 + 2, 5 * 16 + 2, 7 * 16 + 13, 5 * 16 + 13], outline=(255, 255, 0))      # the player
    if mark:
        d.rectangle([0, 0, im.width - 1, im.height - 1], outline=mark, width=2)
    return im.resize((im.width * scale, im.height * scale), gv.Image.NEAREST)


def sheet(surf, stem, out, stride=5, scale=1, limit=48):
    """contact sheet of views from the nearest reachable cell along every unconnected edge"""
    rows = surf.exposed(stem)
    picks, bad = [], []
    last = {}
    for side, i, k, c, near in rows:
        if k is None:
            continue
        if last.get(side) is None or i - last[side] >= stride:
            picks.append((side, i, k, c, near))
            last[side] = i
        if not near and (side, i) not in {(p[0], p[1]) for p in bad}:
            bad.append((side, i, k, c, near))
    exposed_view = [p for p in bad]
    shown = picks[:limit]
    for e in exposed_view[:12]:
        if e not in shown:
            shown.append(e)
    if not shown:
        return 0, bad
    cols = 4
    cw, ch = 15 * 16 * scale, 10 * 16 * scale
    from PIL import Image, ImageDraw
    n = len(shown)
    rws = (n + cols - 1) // cols
    sh = Image.new("RGB", (cols * (cw + 6), rws * (ch + 18)), (30, 30, 36))
    d = ImageDraw.Draw(sh)
    for n_, (side, i, k, c, near) in enumerate(shown):
        isbad = (side, i, k, c, near) in bad and not near
        v = view(surf, stem, c, scale=scale, mark=(255, 40, 40) if isbad else None)
        x, y = (n_ % cols) * (cw + 6), (n_ // cols) * (ch + 18)
        sh.paste(v, (x, y + 16))
        d.text((x + 2, y + 2), f"{stem} {side}@{i} depth {k}{' EXPOSED' if isbad else ''}", fill=(255, 120, 120) if isbad else (200, 200, 200))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sh.save(out)
    return len(shown), bad


def main(argv):
    views = None
    if "--views" in argv:
        views = argv[argv.index("--views") + 1]
        argv = [a for a in argv if a != views and a != "--views"]
    keys = [a for a in argv if not a.startswith("--")] or list(borders.STYLE)
    surf = Surf(keys)
    total = 0
    for k in keys:
        rows = surf.exposed(k)
        bad = [(s, i, kk) for s, i, kk, c, near in rows if kk is not None and not near]
        by = {}
        for s, i, kk in bad:
            by.setdefault(s, []).append(i)
        total += len(bad)
        txt = ", ".join(f"{s}: {len(v)} ({min(v)}-{max(v)})" for s, v in sorted(by.items()))
        print(f"{k:15s} exposed {len(bad):3d}  {txt}")
        if views:
            n, _ = sheet(surf, k, os.path.join(views, f"surf_views_{k}.png"))
    print("total exposed positions:", total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

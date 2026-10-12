"""Bridges you can surf under: for each bridge in a built map, the elevation/collision of the cells round it and
whether a surfer gets from the water on one side of it to the other (and a walker across it).

usage (from the decomp root): python tools/mapgen/bridge_check.py <spec.json> ...
Reads the layout's map.bin as built. Cells print as elevation (hex), '#' for collision.
"""
import json
import os
import struct
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))


def load(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    L = json.load(open("data/layouts/layouts.json"))
    lay = next(l for l in L["layouts"] if l and l.get("id") == spec["layout"])
    w, h = lay["width"], lay["height"]
    raw = open(lay["blockdata_filepath"], "rb").read()
    blocks = struct.unpack(f"<{w * h}H", raw)
    elev = [[blocks[y * w + x] >> 12 for x in range(w)] for y in range(h)]
    coll = [[(blocks[y * w + x] >> 10) & 3 for x in range(w)] for y in range(h)]
    return spec, w, h, elev, coll


def reach(start, ok, w, h, keep):
    """Cells reachable from start moving 4-ways, an object keeping elevation `keep` (0/15 cells keep it)."""
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + a, y + c)
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and ok(*n):
                seen.add(n)
                q.append(n)
    return seen


def main(paths):
    bad = 0
    for p in paths:
        spec, w, h, elev, coll = load(p)
        grid = [l.rstrip("\n") for l in open(os.path.join(os.path.dirname(p), spec["grid"]), encoding="utf-8")]
        for b in spec.get("buildings", []):
            if b.get("label") != "Bridge":
                continue
            bw, bh = len(b["rows"][0]), len(b["rows"])
            x0, y0 = b["x"], b["y"]
            print(f"{spec['map']} bridge at ({x0},{y0}) {bw}x{bh}")
            for y in range(max(0, y0 - 2), min(h, y0 + bh + 2)):
                print("   ", "".join("#" if coll[y][x] else "%X" % elev[y][x]
                                     for x in range(max(0, x0 - 4), min(w, x0 + bw + 4))))
            surf = lambda x, y: coll[y][x] == 0 and elev[y][x] in (1, 15)
            ew = bh == 4 and all(j in (1, 2) for _, j in b["passable"])
            # surfer: from the water just upstream of the bridge to just downstream
            if ew:
                a = [(x, y0 - 1) for x in range(x0, x0 + bw) if y0 - 1 >= 0 and surf(x, y0 - 1)]
                z = {(x, y0 + bh) for x in range(x0, x0 + bw) if y0 + bh < h and surf(x, y0 + bh)}
            else:
                a = [(x0 - 1, y) for y in range(y0, y0 + bh) if x0 - 1 >= 0 and surf(x0 - 1, y)]
                z = {(x0 + bw, y) for y in range(y0, y0 + bh) if x0 + bw < w and surf(x0 + bw, y)}
            ok = bool(a and z and reach(a[0], surf, w, h, 1) & z)
            print("    surf under:", "yes" if ok else "NO", "" if a and z else "(no water on both sides)")
            bad += not ok and bool(a and z)
            # walker: from the street at one end across the deck to the other (elevation rules)
            ends = []
            for i, j in b["passable"]:
                x, y = x0 + i, y0 + j
                for dx, dy in ((-1, 0), (1, 0)) if ew else ((0, -1), (0, 1)):
                    n = (x + dx, y + dy)
                    if 0 <= n[0] < w and 0 <= n[1] < h and not (x0 <= n[0] < x0 + bw and y0 <= n[1] < y0 + bh):
                        ends.append(n)
            def walk_from(s):
                cur = {s: elev[s[1]][s[0]]}
                q = deque([s])
                while q:
                    x, y = q.popleft()
                    e = cur[(x, y)]
                    for a2, c2 in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (x + a2, y + c2)
                        if not (0 <= n[0] < w and 0 <= n[1] < h) or n in cur or coll[n[1]][n[0]]:
                            continue
                        me = elev[n[1]][n[0]]
                        if e not in (0, 15) and me not in (0, 15) and me != e:
                            continue
                        if me in (1,):  # water: walkers don't go there
                            continue
                        cur[n] = e if me in (0, 15) else me
                        q.append(n)
                return set(cur)
            land_ends = [e for e in ends if elev[e[1]][e[0]] not in (1,)]
            if len(land_ends) >= 2:
                r = walk_from(land_ends[0])
                print("    walk across:", "yes" if land_ends[-1] in r else "NO")
                bad += land_ends[-1] not in r
    print("problems:", bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)

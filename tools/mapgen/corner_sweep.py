"""Corner sweep (seams review, 2026-10-14): where does a connection strip end against the border block?

usage (from the decomp root):  python -W ignore tools/mapgen/corner_sweep.py [--min 22] [map_stem ...]

For every outdoor map the engine's backup layout (gba_view.World.backup: the neighbours' strips, the border blocks) is read; every run of
cells where a strip cell (a neighbour's cell drawn with this map's tilesets) touches a border cell (4-neighbour, within the camera margin
7 W/E, 5 N/S) is a "strip end".  Its step = the mean RGB difference of the two cells of each pair along the run.  A canopy that ends in a
ruler-straight line against open ground (the user's "square step") scores high; a strip that ends in open water against a water border,
or in canopy against canopy, scores low.  Prints  map  strip-of  run (cells)  mean step  position,  worst first.
The map that OWNS the cells of the strip is the neighbour: the fix belongs to the neighbour when it is a route (user rule: routes
accommodate towns); both a town: report."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gba_view as gv  # noqa: E402

MARGIN = {"W": 7, "E": 7, "N": 5, "S": 5}


def mean_rgb(img):
    px = img.convert("RGB").resize((1, 1))
    return px.getpixel((0, 0))


def sweep(wd, stem):
    grid, src, W, H = wd.backup(stem)
    w, h = wd.size(stem)
    ts = wd.ts(stem)
    o = gv.MAP_OFFSET
    cache = {}

    def col(i):
        v = grid[i] & 0x3FF if grid[i] != gv.UNDEF else None
        if v is None:
            return None
        if v not in cache:
            cache[v] = mean_rgb(gv.cell_img(ts, grid[i]))
        return cache[v]

    def visible(x, y):
        mx, my = x - o, y - o
        return -MARGIN["W"] <= mx < w + MARGIN["E"] and -MARGIN["N"] <= my < h + MARGIN["S"]

    out = []
    for orient in ("V", "H"):          # V: boundary between horizontally neighbouring cells, H: between vertical neighbours
        seen = set()
        for y in range(H):
            for x in range(W):
                nx, ny = (x + 1, y) if orient == "V" else (x, y + 1)
                if nx >= W or ny >= H or not (visible(x, y) and visible(nx, ny)):
                    continue
                a, b = y * W + x, ny * W + nx
                sa, sb = src[a], src[b]
                if (sa not in (None, "map") and sb is None) or (sb not in (None, "map") and sa is None):
                    strip, bord = (a, b) if sa not in (None, "map") else (b, a)
                    ca, cb = col(strip), col(bord)
                    if ca is None or cb is None:
                        continue
                    d = sum(abs(p - q) for p, q in zip(ca, cb)) / 3.0
                    out.append((orient, x, y, src[strip], d))
    # runs: consecutive boundary cells with the same orientation and strip owner
    runs = []
    by = {}
    for orient, x, y, owner, d in out:
        by.setdefault((orient, owner), []).append((x, y, d))
    for (orient, owner), cells in by.items():
        cells.sort(key=(lambda c: (c[0], c[1])) if orient == "V" else (lambda c: (c[1], c[0])))
        run = []
        for c in cells:
            if run and ((orient == "V" and c[0] == run[-1][0] and c[1] == run[-1][1] + 1) or
                        (orient == "H" and c[1] == run[-1][1] and c[0] == run[-1][0] + 1)):
                run.append(c)
            else:
                if run:
                    runs.append((orient, owner, run))
                run = [c]
        if run:
            runs.append((orient, owner, run))
    res = []
    for orient, owner, run in runs:
        d = sum(c[2] for c in run) / len(run)
        res.append({"map": stem, "owner": owner, "orient": orient, "len": len(run), "step": round(d, 1),
                    "at": (run[0][0] - o, run[0][1] - o)})
    return res


def main(argv):
    thr = 22.0
    if "--min" in argv:
        thr = float(argv[argv.index("--min") + 1])
        argv = [a for i, a in enumerate(argv) if a != "--min" and (i == 0 or argv[i - 1] != "--min")]
    wd = gv.World()
    keys = [a for a in argv if not a.startswith("--")] or sorted(wd.maps.info)
    rows = []
    for k in keys:
        rows += sweep(wd, k)
    rows = [r for r in rows if r["len"] >= 3 and r["step"] >= thr]
    rows.sort(key=lambda r: -r["step"] * min(r["len"], 12))
    for r in rows:
        print(f"{r['map']:15s} strip of {r['owner']:15s} {r['orient']} run {r['len']:2d}  step {r['step']:5.1f}  at {r['at']}")
    print(f"{len(rows)} strip ends with a step >= {thr}")
    return rows


if __name__ == "__main__":
    main(sys.argv[1:])

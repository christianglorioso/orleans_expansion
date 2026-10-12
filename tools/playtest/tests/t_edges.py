"""Map edges in the real engine: for every Orleans outdoor map, warp next to each connection seam (middle of the
overlap, both ends of the overlap, the cell just outside the overlap) and to the middle of every unconnected edge,
screenshot the view. Look at the contact sheets for garbled neighbour strips and flat border blocks
(see tools/mapgen/edges_plan.md). Checks: the warp arrives, the game does not crash, the screen is not blank."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import map_data, ROOT  # noqa: E402

OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


def outdoor_maps(b):
    g = json.loads((ROOT / "data/maps/map_groups.json").read_text())
    names = list(g["gMapGroup_Towns"]) + list(g["gMapGroup_Routes"])
    return [n for n in names if (ROOT / "data/maps" / n / "map.json").exists()]


def nearest_walkable(md, x, y, along, radius=6):
    """closest cell with no collision to (x,y), searching along the edge first"""
    W, H = md["width"], md["height"]
    best = None
    for r in range(0, radius + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                cx, cy = x + dx, y + dy
                if 0 <= cx < W and 0 <= cy < H and md["coll"][cy][cx] == 0:
                    cand = (r, cx, cy)
                    if best is None or cand < best:
                        best = cand
        if best:
            return best[1], best[2]
    return None


def spots_for(name, ids):
    md = map_data(name)
    W, H = md["width"], md["height"]
    spots = []
    connected = set()
    for c in md["connections"]:
        d, off = c["direction"], int(c["offset"])
        connected.add(d)
        other = ids.get(c["map"])
        if other is None:
            continue
        od = map_data(other)
        if d in ("up", "down"):
            lo, hi = max(0, off), min(W, off + od["width"]) - 1
            y = 1 if d == "up" else H - 2
            pts = [("mid", (lo + hi) // 2, y), ("seam-lo", lo, y), ("seam-hi", hi, y)]
            if lo > 1:
                pts.append(("beyond-lo", lo - 2, y))
            if hi < W - 3:
                pts.append(("beyond-hi", hi + 2, y))
        else:
            lo, hi = max(0, off), min(H, off + od["height"]) - 1
            x = 1 if d == "left" else W - 2
            pts = [("mid", x, (lo + hi) // 2), ("seam-lo", x, lo), ("seam-hi", x, hi)]
            if lo > 1:
                pts.append(("beyond-lo", x, lo - 2))
            if hi < H - 3:
                pts.append(("beyond-hi", x, hi + 2))
        for tag, x, y in pts:
            spots.append((d, "conn %s %s" % (other, tag), x, y))
    for d in ("up", "down", "left", "right"):
        if d not in connected:
            x = W // 2 if d in ("up", "down") else (1 if d == "left" else W - 2)
            y = H // 2 if d in ("left", "right") else (1 if d == "up" else H - 2)
            spots.append((d, "open edge", x, y))
    return md, spots


def run(b, t):
    b.new_game()
    b.shots.clear()                    # keep the boot screens out of the edge sheets
    ids = {}
    names = outdoor_maps(b)
    for n in names:
        mid = map_data(n)["id"]
        if mid:
            ids[mid] = n
    total = arrived = 0
    report = []
    for name in names:
        md, spots = spots_for(name, ids)
        for side, desc, x, y in spots:
            cell = nearest_walkable(md, x, y, side)
            if not cell:
                t.note("%s %s: no walkable cell near (%d,%d)" % (name, side, x, y))
                continue
            total += 1
            ok = b.warp(name, cell[0], cell[1], timeout_s=15)
            b.check_alive("warping to %s" % name)
            label = "%s %s %s @%d,%d" % (name, side, desc, cell[0], cell[1])
            if ok:
                arrived += 1
                b.shot(label)
                blank = b.nonblack() < 300
                report.append({"map": name, "side": side, "spot": desc, "cell": cell, "blank": blank})
                if blank:
                    t.check("not blank: " + label, False)
            else:
                b.shot("NOARRIVE " + label)
                t.check("arrives: " + label, False, b.where())
                report.append({"map": name, "side": side, "spot": desc, "cell": cell, "arrived": False})
    t.check("every edge spot arrived", arrived == total, "%d/%d" % (arrived, total))
    t.note("%d maps, %d edge spots screenshotted" % (len(names), arrived))
    Path(b.out, "edges_report.json").write_text(json.dumps(report, indent=1))

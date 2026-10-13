"""Map transitions in the real engine (SLOW: about 10-15 minutes; run it with `run_all.py --slow` or `run_all.py t_trans`).

Part 1: every connection (data/maps/*/map.json), both directions: warp 10 cells before the seam, WALK across it along the
exit road/channel, keep walking 10 cells into the neighbour, capturing a frame every step. Detects
  * passable:  the walk gets across and 10 cells in (invisible wall, elevation mismatch, missing passage, gate left shut),
  * flip:      the strip of the neighbour that was visible before the crossing looks different right after it
               (compared cell by cell, in world coordinates, with the same strip seen from the other side of the seam),
  * garble:    fully black 16x16 cells on screen,
  * freeze / crash.
Part 2: every outdoor map, along every edge that has no connection (and the stretch of a connected edge outside the
connection): warp at intervals and grade the border view (flat border, hard cut, ok).
Output: out/<run>/t_transitions/{filmstrips,pairs,joins,edges}/, results.json, summary.txt.
"""
import json
import shutil
import sys
import traceback
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import GameCrash, ROOT, map_data  # noqa: E402
from mapwalk import (SURFABLE, DIRV, Grid, bfs, bfs_elev, mismatch, next_elev, black_cells, cells_of, filmstrip, grab, pair_image, strip_diff, COLS, ROWS,  # noqa: E402
                     PLAYER_COL, PLAYER_ROW, _label)

DEPTH = 10
OPP = {"up": "down", "down": "up", "left": "right", "right": "left"}
D_OF = {"up": "U", "down": "D", "left": "L", "right": "R"}
GATE_FLAGS = ["FLAG_BADGE0%d_GET" % i for i in range(1, 9)] + ["FLAG_CUT_STORM_HEDGE", "FLAG_STORMS_EDGE_GRID_RESTORED",
                                                              "FLAG_DUST_STORMS_LIFTED", "FLAG_SYS_POKEDEX_GET", "FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_ROUTE25_OPEN"]
ARRIVAL_VARS = ["VAR_ROUTE4_ARRIVAL", "VAR_CAMP_ARRIVAL", "VAR_HOLLOW_ARRIVAL", "VAR_REDFIELD_ARRIVAL", "VAR_REDFIELD_RAID_CALL", "VAR_LANDS_END_ARRIVAL", "VAR_LANDS_END_SCENE"]  # one-off arrival scenes: already seen
FLIP_MIN = 0.15          # fraction of strip cells that changed
FLIP_EXCESS = 0.10       # ... above the worst ordinary step on the same walk


def outdoor_maps():
    g = json.loads((ROOT / "data/maps/map_groups.json").read_text())
    names = list(g["gMapGroup_Towns"]) + list(g["gMapGroup_Routes"])
    return [n for n in names if (ROOT / "data/maps" / n / "map.json").exists()]


def setup(b):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    b.set_var("VAR_ORLEANS_STORY", 44)
    for v in ARRIVAL_VARS:
        b.set_var(v, 1)
    b.set_var("VAR_OLD_WATER_RAID", 2)
    b.set_var("VAR_OLD_WATER_TELLING", 2)
    missing = []
    for f in GATE_FLAGS:
        try:
            b.set_flag(f)
        except KeyError:
            missing.append(f)
    return missing


def depth_of(cell, d, W, H, inward_from_edge=True):
    """distance from the seam edge of the map for a crossing in direction d (d = side of the map with the seam)"""
    x, y = cell
    return {"up": y, "down": H - 1 - y, "left": x, "right": W - 1 - x}[d]


class Walk:
    """one walk: records frames, handles surf/foot, replans around blocked cells"""

    def __init__(self, b, label):
        self.b, self.label = b, label
        self.frames, self.meta = [], []
        self.problems = []
        self.cross_index = None

    def surfing(self):
        return bool(self.b.r8(self.b.sym("gPlayerAvatar")) & 8)

    def set_surf(self, on):
        if self.surfing() == on:
            return
        self.b.call("SetPlayerAvatarTransitionFlags", 8 if on else 1)
        self.b.frames(10)

    def start_surf(self, tile_elev):
        """a real player gets onto the water by using Surf, which hops onto the tile and takes its elevation"""
        b = self.b
        self.set_surf(True)
        oid = b.r8(b.sym("gPlayerAvatar") + 5)
        ea = b.sym("gObjectEvents") + oid * 0x24 + 0x0B
        if tile_elev != 15:
            b.w8(ea, (b.r8(ea) & 0xF0) | tile_elev)

    def capture(self, note=""):
        self.frames.append(grab(self.b))
        self.meta.append({"map": self.b.map_name(), "pos": self.b.pos(), "note": note})

    def recover_from_battle(self):
        """a wild encounter (water/grass) interrupted the walk: win it, wait for the field, remember it"""
        b = self.b
        if b.in_battle() or not b.in_overworld():
            self.problems.append("wild battle at %s" % (b.pos(),))
            b.advance_text(60)
            b.settle()

    def step_to(self, grid, cell):
        b = self.b
        cur = b.pos()
        d = {(0, -1): "U", (0, 1): "D", (-1, 0): "L", (1, 0): "R"}[(cell[0] - cur[0], cell[1] - cur[1])]
        want_surf = grid.surfable(cell)
        if want_surf and not self.surfing():
            self.start_surf(grid.cells[cell][2])
        ok = b.step(d, tries=2)
        b.check_alive("walking " + self.label)
        self.recover_from_battle()
        if b.script_status() != 2:                        # a trigger fired: note it, dismiss, carry on
            self.problems.append("script at %s" % (b.pos(),))
            b.advance_text(30)
        return ok and b.pos() == cell

    def walk(self, grid, cells, avoid_extra=None):
        """walk the list of cells, capturing each. Returns None or a failure string."""
        for cell in cells:
            ok = self.step_to(grid, cell)
            self.capture()
            if not ok:
                return ("blocked stepping %s -> %s (beh/coll/elev %s)" % (self.meta[-1]["pos"], cell, grid.cells.get(cell)), cell)
        return None


def static_avoid(b, grid):
    av = set(grid.warps)
    for c, fl in grid.objects:
        if str(fl) in ("0", "") or not b.flag(fl):
            av.add(c)
    return av


def lane_candidates(b, X, d, Y, off, grid):
    """lanes whose both edge cells are open, shortest approach first: [(a, edge_cell, start_cell)]"""
    my = map_data(Y)
    W, H = grid.W, grid.H
    if d in ("up", "down"):
        lo, hi = max(0, off), min(W, off + my["width"]) - 1
        edge = lambda a: (a, 0 if d == "up" else H - 1)
        ycell = lambda a: (a - off, my["height"] - 1 if d == "up" else 0)
    else:
        lo, hi = max(0, off), min(H, off + my["height"]) - 1
        edge = lambda a: (0 if d == "left" else W - 1, a)
        ycell = lambda a: (my["width"] - 1 if d == "left" else 0, a - off)
    mid = (lo + hi) // 2
    avoid = static_avoid(b, grid)
    D = min(DEPTH, (H if d in ("up", "down") else W) - 1)
    out = []
    for a in sorted(range(lo, hi + 1), key=lambda a: abs(a - mid)):
        e, yc = edge(a), ycell(a)
        if not grid.walkable(e) or e in avoid or my["coll"][yc[1]][yc[0]] != 0:
            continue
        path = bfs(grid, e, lambda c: depth_of(c, d, W, H) >= D, avoid=avoid)
        if path is None:
            continue
        out.append((len(path), abs(a - mid), a, e, path[-1]))
    out.sort()
    return [(a, e, s) for _, _, a, e, s in out]


def player_elev(b):
    oid = b.r8(b.sym("gPlayerAvatar") + 5)
    return b.r8(b.sym("gObjectEvents") + oid * 0x24 + 0x0B) & 0x0F


def do_crossing(b, base, X, d, Y, off, outdir, ids):
    res = {"from": X, "to": Y, "dir": d, "offset": off, "passable": False, "flip": False, "garble": False,
           "detail": "", "front": None, "back": None, "baseline": None, "black": 0, "frames": 0, "steps_after": 0,
           "script": []}
    label = "%s>%s" % (X, Y)
    mx = map_data(X)
    W, H = mx["width"], mx["height"]
    # 1. load X next to the seam so the engine can tell us what each cell is
    edge_probe = {"up": (W // 2, 0), "down": (W // 2, H - 1), "left": (0, H // 2), "right": (W - 1, H // 2)}[d]
    cand = None
    for r in range(0, 40):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                c = (edge_probe[0] + dx, edge_probe[1] + dy)
                if max(abs(dx), abs(dy)) == r and 0 <= c[0] < W and 0 <= c[1] < H and mx["coll"][c[1]][c[0]] == 0:
                    cand = c
                    break
            if cand:
                break
        if cand:
            break
    b.loadstate(base)
    b.set_var("VAR_REPEL_STEP_COUNT", 250)               # no wild battles while walking (lead is level 100)
    b.frames(5)
    if not b.warp(X, cand[0], cand[1], timeout_s=20):
        res["detail"] = "warp into %s failed (%s)" % (X, b.where())
        return res, None
    b.check_alive("loading " + X)
    grid = Grid(b)
    avoid = static_avoid(b, grid)
    lanes = lane_candidates(b, X, d, Y, off, grid)
    if not lanes:
        res["detail"] = "no lane to the seam in %s: every edge cell is blocked, or the neighbour's matching cell is" % X
        return res, None
    # 2. try lanes until an elevation-correct route from a start cell ~10 cells back to the edge exists AND the first
    #    cell beyond the edge can be entered (collision / elevation as the engine sees it)
    cells = None
    why = []
    dx, dy = DIRV[D_OF[d]]
    for a, e, start in lanes[:12]:
        b.loadstate(base)
        b.set_var("VAR_REPEL_STEP_COUNT", 250)
        b.frames(5)
        if not b.warp(X, start[0], start[1], timeout_s=20):
            continue
        b.check_alive("loading " + X)
        e0 = grid.cells[start][2]
        e0 = player_elev(b) if e0 == 15 else e0
        route = bfs_elev(grid, start, e0, lambda c, e=e: c == e, avoid=avoid)
        if route is None:
            why.append("lane %d: no elevation-legal route from %s (start elev %d)" % (a, start, e0))
            continue
        # elevation the player has on arriving at the edge cell
        ee = e0
        for c in route:
            ee = next_elev(ee, grid.cells[c][2])
        beh, coll, el = grid.probe(b, e[0] + dx, e[1] + dy)[0]
        shore_cross = grid.surfable(e) != (beh in SURFABLE)
        if coll != 0 or (not shore_cross and mismatch(ee, el)):
            why.append("lane %d: cell beyond the edge %s has collision %d elevation %d, player arrives at elevation %d" % (a, (e[0] + dx, e[1] + dy), coll, el, ee))
            continue
        cells, res["lane"] = route, a
        break
    if cells is None:
        res["detail"] = "no way across: %d lanes tried. %s" % (min(12, len(lanes)), "; ".join(why[:3]))
        return res, None
    w = Walk(b, label)
    w.set_surf(grid.surfable(b.pos()))
    b.frames(240)                                      # let the map-name popup go away before the first frame
    w.capture("start")
    fail = w.walk(grid, cells)
    if fail:
        res["detail"] = "in %s before the seam: %s; player elev %d" % (X, fail[0], player_elev(b))
        res["frames"] = len(w.frames)
        return res, w
    # 3. the crossing step
    dx, dy = DIRV[D_OF[d]]
    edge_cell = b.pos()
    ahead = grid.probe(b, edge_cell[0] + dx, edge_cell[1] + dy)[0]
    pe = player_elev(b)
    if ahead[0] in SURFABLE and not w.surfing():
        w.start_surf(ahead[2])
    ok = b.step(D_OF[d], tries=2)
    b.check_alive("crossing " + label)
    if b.script_status() != 2:
        w.problems.append("script at the seam")
        b.advance_text(30)
    w.capture("cross")
    if b.map_name() != Y:
        res["detail"] = ("step across the seam failed on %s at %s facing %s: the cell beyond (engine view) has behavior/collision/elevation %s, "
                         "player elevation %d" % (X, b.pos(), d, ahead, pe))
        res["frames"] = len(w.frames)
        return res, w
    w.cross_index = len(w.frames) - 1
    # 4. keep walking into Y
    g2 = Grid(b)
    Wy, Hy = g2.W, g2.H
    Dy = min(DEPTH, (Hy if d in ("up", "down") else Wy) - 1)
    inward = lambda c: depth_of(c, OPP[d], Wy, Hy)
    avoid2 = static_avoid(b, g2)
    reached = 0
    for attempt in range(6):
        goal = lambda c: inward(c) >= Dy
        path = bfs_elev(g2, b.pos(), player_elev(b), goal, avoid=avoid2)
        if path is None:                                   # dead end: go as deep as the map lets us
            path = bfs_elev(g2, b.pos(), player_elev(b), lambda c: False, avoid=avoid2, farthest_key=inward)
            if path is None:
                break
            res["detail"] = "dead end: deepest reachable cell is %d cells in (wanted %d)" % (inward(path[-1]), Dy)
        fail = w.walk(g2, path)
        reached = max(reached, inward(b.pos()))
        if fail is None:
            break
        avoid2.add(fail[1])
        res["detail"] = "in %s after the seam: %s" % (Y, fail[0])
    reached = max(reached, inward(b.pos()))
    res["steps_after"] = max(0, len(w.frames) - 1 - w.cross_index)
    res["reached_depth"] = reached
    res["passable"] = bool(b.map_name() == Y and reached >= min(Dy, 3))
    if reached >= Dy:
        res["detail"] = ""
    res["short"] = bool(res["passable"] and reached < Dy)
    res["frames"] = len(w.frames)
    res["script"] = w.problems
    # 5. frame analysis
    ci = w.cross_index
    A, B = w.frames[ci - 1], w.frames[ci]
    front, nf, wf = strip_diff(A, B, D_OF[d], "front")
    back, nb, wb = strip_diff(A, B, D_OF[d], "back")
    base_list = []
    for i in range(1, len(w.frames)):
        if i == ci or w.meta[i]["map"] != w.meta[i - 1]["map"]:
            continue
        p0, p1 = w.meta[i - 1]["pos"], w.meta[i]["pos"]
        mv = {(0, -1): "U", (0, 1): "D", (-1, 0): "L", (1, 0): "R"}.get((p1[0] - p0[0], p1[1] - p0[1]))
        if mv:
            base_list.append(strip_diff(w.frames[i - 1], w.frames[i], mv, "front")[0])
    base_front = float(np.median(base_list)) if base_list else 0.0   # median: a walking NPC must not hide a flip
    res.update(front=round(front, 3), back=round(back, 3), baseline=round(base_front, 3), cells_front=nf)
    res["flip"] = bool((front >= FLIP_MIN and front > base_front + FLIP_EXCESS) or (back >= FLIP_MIN + 0.1 and back > base_front + FLIP_EXCESS))
    blacks = [black_cells(f) for f in w.frames]
    res["black"] = max(blacks)
    res["garble"] = bool(res["black"] > 0)
    res["worst_frame"] = int(np.argmax(blacks)) if res["black"] else ci
    # 6. images
    fs = outdir / "filmstrips" / ("%s__%s__%s.png" % (X, d, Y))
    labels = ["%d %s %d,%d" % (i, m["map"][:5], m["pos"][0], m["pos"][1]) for i, m in enumerate(w.meta)]
    fs.parent.mkdir(parents=True, exist_ok=True)
    filmstrip(w.frames, labels, fs, mark=(ci,))
    pp = outdir / "pairs" / ("%s__%s__%s.png" % (X, d, Y))
    pp.parent.mkdir(parents=True, exist_ok=True)
    pair_image(A, B, D_OF[d], wf, pp, "%s>%s front %.0f%% back %.0f%% (ordinary step %.0f%%)" % (X, Y, front * 100, back * 100, base_front * 100))
    res["filmstrip"] = str(fs)
    res["pair"] = str(pp)
    return res, w


# ------------------------------------------------------------------ part 2: unconnected edges
def border_grade(frame, px, py, W, H):
    """grade the border view for a player standing at (px,py) of a WxH map"""
    cells = cells_of(frame)
    outside, inside_edge, outside_edge = [], [], []
    for r in range(ROWS):
        for c in range(COLS):
            x, y = px + (c - PLAYER_COL), py + (r - PLAYER_ROW)
            if x < 0 or y < 0 or x >= W or y >= H:
                outside.append((r, c))
    if not outside:
        return {"grade": "n/a", "outside": 0}
    hashes = {cells[r, c].tobytes() for r, c in outside}
    pix = np.concatenate([cells[r, c].reshape(-1, 3) for r, c in outside])
    colors = len({tuple(p) for p in pix[::7]})
    # contrast between the nearest outside cells and the nearest inside cells (mean colour)
    def near(cond):
        sel = [(r, c) for r in range(ROWS) for c in range(COLS)
               if cond(px + (c - PLAYER_COL), py + (r - PLAYER_ROW)) and (r, c) not in ((PLAYER_ROW, PLAYER_COL), (PLAYER_ROW - 1, PLAYER_COL))]
        return np.mean([cells[r, c].reshape(-1, 3).mean(axis=0) for r, c in sel], axis=0) if sel else None
    inx = near(lambda x, y: 0 <= x < W and 0 <= y < H and (x in (0, W - 1) or y in (0, H - 1)))
    outx = near(lambda x, y: (x in (-1, W) and -1 <= y <= H) or (y in (-1, H) and -1 <= x <= W))
    contrast = float(np.abs(inx - outx).sum()) if inx is not None and outx is not None else 0.0
    nb = sum(1 for r, c in outside if cells[r, c].max() == 0)
    grade = "ok"
    why = []
    mean = pix.mean(axis=0)
    watery = mean[1] >= mean[0] + 15 and mean[2] >= mean[0] + 15            # teal/blue: open water past the edge is natural
    if len(hashes) <= 1 or colors <= 4:
        grade = "FLATWATER" if watery else "FLAT"
        why = ["border is one flat %s block (%d distinct cells, %d colours)" % ("water" if watery else "terrain", len(hashes), colors)]
    elif len(hashes) <= 2:
        grade, why = "PLAIN", ["only %d distinct border cells" % len(hashes)]
    if contrast > 120:
        grade = "HARDCUT" if grade == "ok" else grade + "+HARDCUT"
        why.append("edge contrast %.0f" % contrast)
    if nb:
        grade = "BLACK" if grade == "ok" else grade + "+BLACK"
        why.append("%d black cells" % nb)
    return {"grade": grade, "outside": len(outside), "distinct": len(hashes), "colors": colors, "contrast": round(contrast),
            "black": nb, "why": "; ".join(why)}


GRADE_RANK = {"ok": 0, "n/a": 0, "FLATWATER": 1, "PLAIN": 1, "HARDCUT": 2, "FLAT": 2, "BLACK": 3}


def rank(g):
    return max(GRADE_RANK.get(p, 2) for p in g.split("+"))


def edge_samples(name, ids):
    md = map_data(name)
    W, H = md["width"], md["height"]
    covered = {s: [] for s in ("up", "down", "left", "right")}
    for c in md["connections"]:
        other = ids.get(c["map"])
        if not other:
            continue
        od = map_data(other)
        off = int(c["offset"])
        if c["direction"] in ("up", "down"):
            covered[c["direction"]].append((off, off + od["width"] - 1))
        else:
            covered[c["direction"]].append((off, off + od["height"] - 1))
    out = []
    for side in ("up", "down", "left", "right"):
        n = W if side in ("up", "down") else H
        free = [a for a in range(n) if not any(lo <= a <= hi for lo, hi in covered[side])]
        if not free:
            continue
        picks = sorted({free[int(i * (len(free) - 1) / 4)] for i in range(5)}) if len(free) > 5 else free[::max(1, len(free) // 3)]
        for a in picks:
            out.append((side, a, "unconnected" if not covered[side] else "outside the connection"))
    return md, out


def edge_cell(md, side, a):
    """nearest walkable cell at depth 1..4 inward of the edge, at/near position a along it"""
    W, H = md["width"], md["height"]
    for depth in (1, 2, 3, 4):
        for da in (0, 1, -1, 2, -2, 3, -3, 4, -4):
            aa = a + da
            c = {"up": (aa, depth), "down": (aa, H - 1 - depth), "left": (depth, aa), "right": (W - 1 - depth, aa)}[side]
            if 0 <= c[0] < W and 0 <= c[1] < H and md["coll"][c[1]][c[0]] == 0:
                return c
    return None


def edges_part(b, base, names, ids, outdir, t, results):
    rows = []
    for name in names:
        md, samples = edge_samples(name, ids)
        views, grades = [], []
        for side, a, kind in samples:
            c = edge_cell(md, side, a)
            if c is None:
                continue
            b.loadstate(base)
            b.frames(3)
            try:
                ok = b.warp(name, c[0], c[1], timeout_s=15)
                b.check_alive("edge warp " + name)
            except GameCrash as e:
                t.bug("crash warping to %s %s edge: %s" % (name, side, e))
                continue
            if not ok:
                grades.append({"side": side, "at": c, "grade": "NOARRIVE", "why": b.where()})
                continue
            b.frames(240)                                  # map-name popup gone
            f = grab(b)
            g = border_grade(f, c[0], c[1], md["width"], md["height"])
            g.update(side=side, at=list(c), kind=kind)
            grades.append(g)
            views.append((f, "%s %s@%d,%d %s" % (name[:12], side[0], c[0], c[1], g["grade"]), g))
        if not grades:
            rows.append({"map": name, "worst": "n/a", "views": 0})
            continue
        worst = max(grades, key=lambda g: rank(g["grade"]) if g["grade"] != "NOARRIVE" else 9)
        rows.append({"map": name, "worst": worst["grade"], "worst_side": worst.get("side"), "why": worst.get("why", ""),
                     "views": len(grades), "grades": grades})
        if views:
            p = outdir / "edges" / ("%s.png" % name)
            p.parent.mkdir(parents=True, exist_ok=True)
            order = sorted(range(len(views)), key=lambda i: -rank(views[i][2]["grade"]))
            filmstrip([views[i][0] for i in order], [views[i][1] for i in order], p, cols=5, thumb=(192, 128))
            rows[-1]["sheet"] = str(p)
    return rows


# ------------------------------------------------------------------ main
def run(b, t):
    outdir = b.out
    for sub in ("filmstrips", "pairs", "joins", "edges"):
        (outdir / sub).mkdir(exist_ok=True)
    t.note("ROM sha1 %s" % b.sha)
    missing = setup(b)
    if missing:
        t.note("gate flags not defined in this build (skipped): %s" % missing)
    base = outdir / "base.state"
    b.savestate(base)
    names = outdoor_maps()
    ids = {}
    for n in names:
        i = map_data(n)["id"]
        if i:
            ids[i] = n
    crossings = []
    for n in names:
        for c in map_data(n)["connections"]:
            if c["map"] in ids:
                crossings.append((n, c["direction"], ids[c["map"]], int(c["offset"])))
    t.note("%d connections walked in %d directed crossings" % (len(crossings) // 2, len(crossings)))
    results = []
    for i, (X, d, Y, off) in enumerate(crossings):
        try:
            res, w = do_crossing(b, base, X, d, Y, off, outdir, ids)
        except GameCrash as e:
            res = {"from": X, "to": Y, "dir": d, "offset": off, "passable": False, "flip": False, "garble": False,
                   "detail": "GAME CRASH: %s" % e, "crash": True}
            t.bug("crash walking %s>%s: %s" % (X, Y, e))
        except Exception as e:                                  # keep going: one bad crossing must not end the run
            res = {"from": X, "to": Y, "dir": d, "offset": off, "passable": False, "flip": False, "garble": False,
                   "detail": "bot error: %s" % traceback.format_exc().strip().splitlines()[-1]}
        results.append(res)
        print("  [%d/%d] %s -%s-> %s: %s" % (i + 1, len(crossings), X, d, Y,
              "PASS" if res["passable"] else "BLOCKED", ) + (" FLIP" if res["flip"] else "") + (" BLACK" if res["garble"] else ""), flush=True)
    # key frames of every crossing go to the contact sheet
    for r in results:
        if r.get("pair"):
            b.shots.append(("%s>%s%s" % (r["from"], r["to"], " FLIP" if r["flip"] else ""), Path(r["pair"])))
    # per-join sheets: both directions stacked
    byjoin = {}
    for r in results:
        byjoin.setdefault(frozenset((r["from"], r["to"])), []).append(r)
    for key, rs in byjoin.items():
        imgs = []
        for r in rs:
            for k in ("pair", "filmstrip"):
                if r.get(k) and Path(r[k]).exists():
                    im = Image.open(r[k]).convert("RGB")
                    _label(im, "%s > %s" % (r["from"], r["to"]), xy=(4, im.height - 12))
                    imgs.append(im)
        if imgs:
            wmax = max(i.width for i in imgs)
            sheet = Image.new("RGB", (wmax, sum(i.height for i in imgs) + 4 * len(imgs)), (40, 40, 40))
            y = 0
            for im in imgs:
                sheet.paste(im, (0, y))
                y += im.height + 4
            a, bb = sorted(key)
            sheet.save(outdir / "joins" / ("%s__%s.png" % (a, bb)))
    # ---- part 2
    edge_rows = edges_part(b, base, names, ids, outdir, t, results)
    # ---- tables
    lines = ["JOIN TABLE  (passable / flip / garble / worst frame)", "%-16s %-5s %-16s %-4s %-5s %-6s %s" %
             ("from", "dir", "to", "pass", "flip", "garble", "worst frame / front% back% (ordinary step %)")]
    for r in results:
        lines.append("%-16s %-5s %-16s %-4s %-5s %-6s %s" % (
            r["from"], r["dir"], r["to"], "yes" if r["passable"] else "NO", "YES" if r["flip"] else "no",
            "YES" if r["garble"] else "no",
            ("f%s %s%%/%s%% (%s%%)" % (r.get("worst_frame"), int(100 * (r.get("front") or 0)), int(100 * (r.get("back") or 0)),
                                       int(100 * (r.get("baseline") or 0))) if r.get("front") is not None else r["detail"][:80])))
        if r.get("detail"):
            lines.append("      -> " + r["detail"])
        if r.get("script"):
            lines.append("      (a script ran on the walk: %s)" % "; ".join(r["script"]))
        if r.get("black"):
            lines.append("      (%d fully black cells on screen; worst frame %s: see the filmstrip)" % (r["black"], r.get("worst_frame")))
    lines += ["", "EDGES TABLE (worst view per map)", "%-16s %-9s %-6s %s" % ("map", "worst", "views", "side / note")]
    for e in edge_rows:
        lines.append("%-16s %-9s %-6s %s %s" % (e["map"], e["worst"], e.get("views", 0), e.get("worst_side", ""), e.get("why", "")))
    txt = "\n".join(lines)
    (outdir / "summary.txt").write_text(txt)
    (outdir / "results.json").write_text(json.dumps({"rom_sha1": b.sha, "crossings": results, "edges": edge_rows}, indent=1))
    n = len(results)
    npass = sum(r["passable"] for r in results)
    nflip = sum(r["flip"] for r in results)
    ngarb = sum(r["garble"] for r in results)
    t.note("passable %d/%d, flip %d, garble(black) %d; table in %s" % (npass, n, nflip, ngarb, outdir / "summary.txt"))
    t.check("every crossing is passable", npass == n, "; ".join("%s>%s: %s" % (r["from"], r["to"], r["detail"][:60])
                                                              for r in results if not r["passable"])[:900])
    t.check("no tile/palette flip at any seam", nflip == 0, ", ".join("%s>%s" % (r["from"], r["to"]) for r in results if r["flip"])[:900])
    t.check("no black cells while crossing", ngarb == 0, ", ".join("%s>%s" % (r["from"], r["to"]) for r in results if r["garble"])[:600])
    bad_edges = [e for e in edge_rows if rank(e["worst"]) >= 2]
    t.check("every unconnected edge shows a proper border", not bad_edges, ", ".join("%s:%s" % (e["map"], e["worst"]) for e in bad_edges)[:900])
    print()
    print(txt)

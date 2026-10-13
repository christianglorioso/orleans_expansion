"""On-foot connectivity before/after check for the edge pass: python tools/mapgen/feather_foot.py <Map> [<Map> ...]
Compares data/layouts/<Map>/map.bin in the working tree with git HEAD: every event cell (warp, object, item, sign) that could be
reached on foot from the map's first exit before must still be reachable after.  Water metatile behaviours (0x10-0x15) block."""
import json, os, struct, subprocess, sys
from collections import deque
ROOT = os.getcwd()
lays = {l["id"]: l for l in json.load(open("data/layouts/layouts.json"))["layouts"] if l}


def attrs(d):
    raw = open(os.path.join(d, "metatile_attributes.bin"), "rb").read()
    return struct.unpack(f"<{len(raw) // 2}H", raw)


def snake(n):
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n.replace("gTileset_", "")).lower()


def grid(name, blob, lay, prim, sec):
    w, h = lay["width"], lay["height"]
    mb = struct.unpack(f"<{w * h}H", blob)
    ok = {}
    for y in range(h):
        for x in range(w):
            v = mb[y * w + x]
            mid, coll = v & 0x3FF, (v >> 10) & 3
            beh = (prim[mid] if mid < 512 else sec[mid - 512] if mid - 512 < len(sec) else 0) & 0x1FF
            ok[(x, y)] = coll == 0 and not (0x10 <= beh <= 0x15)
    return ok


def comp(ok, starts):
    seen, q = set(), deque()
    for s in starts:
        if ok.get(s):
            seen.add(s); q.append(s)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (x + dx, y + dy)
            if ok.get(c) and c not in seen:
                seen.add(c); q.append(c)
    return seen


bad = 0
for name in sys.argv[1:]:
    m = json.load(open(f"data/maps/{name}/map.json", encoding="utf-8"))
    lay = lays[m["layout"]]
    path = lay["blockdata_filepath"]
    after = open(path, "rb").read()
    before = subprocess.run(["git", "show", "HEAD:" + path.replace("\\", "/")], capture_output=True).stdout
    prim = attrs("data/tilesets/primary/orleans_general")
    sec = attrs("data/tilesets/secondary/" + snake(lay["secondary_tileset"]))
    # the before state used the HEAD tileset attributes: read them from git too
    def gattr(dirp):
        raw = subprocess.run(["git", "show", f"HEAD:{dirp}/metatile_attributes.bin"], capture_output=True).stdout
        return struct.unpack(f"<{len(raw) // 2}H", raw)
    secb = gattr("data/tilesets/secondary/" + snake(lay["secondary_tileset"]))
    primb = gattr("data/tilesets/primary/orleans_general")
    okb, oka = grid(name, before, lay, primb, secb), grid(name, after, lay, prim, sec)
    pts = [(o["x"], o["y"]) for k in ("warp_events", "object_events", "bg_events", "coord_events") for o in m.get(k, [])]
    starts = [(int(o["x"]), int(o["y"])) for o in m.get("warp_events", [])[:1]] or [(p[0], p[1]) for p in pts[:1]]
    # stand-cells: an event cell itself or any 4-neighbour
    def near(p, comp_):
        return p in comp_ or any((p[0] + dx, p[1] + dy) in comp_ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    # start: the largest component before
    seeds = [c for c, v in okb.items() if v]
    best = set()
    seen_all = set()
    for c in seeds:
        if c in seen_all:
            continue
        cc = comp(okb, [c]); seen_all |= cc
        if len(cc) > len(best):
            best = cc
    cx, cy = lay['width'] // 2, lay['height'] // 2
    seed = next(c for c in sorted(best, key=lambda c: abs(c[0] - cx) + abs(c[1] - cy)) if oka.get(c))
    cb, ca = comp(okb, [seed]), comp(oka, [seed]) if oka.get(seed) else set()
    lost = [p for p in pts if near(p, cb) and not near(p, ca)]
    print(f"{name}: foot-reachable cells before {len(cb)} after {len(ca)}; events lost: {lost or 'none'}")
    bad += bool(lost)
sys.exit(1 if bad else 0)

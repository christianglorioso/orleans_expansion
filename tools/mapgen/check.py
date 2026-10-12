"""Quality checks for a generated map. Run after build.py has written the map.

usage (from the decomp root):
    python tools/mapgen/check.py tools/mapgen/maps/<map>.json [--seams N] [--out DIR]

Reports:
  * terrain seams: tile edges where the colour jump across the edge is much bigger than the texture
    just inside either tile. Building/object outlines are expected hard edges and are listed
    separately; terrain-to-terrain seams above 20 should be fixed.
  * off-palette grass: tiles whose grass-like pixels aren't the shared swamp grass.
  * gameplay: every warp on a door-behaviour tile, every door reachable from the tile below it,
    every NPC/item on walkable ground, and a walk test from the first door that must reach every
    door, event and map exit.
  * writes <out>/<map>_seams.png (worst seams, magenta line) and tools/mapgen/maps/<map>_compare.png
    (mockup next to the result).
"""
import json
import os
import struct
import sys
from collections import Counter, defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402
from build import Builder  # noqa: E402
from compose import behavior_ids  # noqa: E402
from render import Tilesets  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# tile-name prefixes whose edges are object/building outlines rather than terrain
OBJECT_PREFIXES = ("johto:02A", "johto:03A", "johto:003",  # the approach lamp (head, post) and signpost
                   "shady:", "brick:", "barn:", "patch:church", "patch:barn", "patch:shady", "patch:pier",
                   "cian:", "brg:", "patch:brick_", "patch:hall_", "patch:gable_", "patch:cave_door",
                   "patch:boat", "patch:cypress", "patch:grave", "ekat:knees", "ekat:water_weeds",
                   "ekat:waterstump", "ekat:water_lily", "ekat:marsh_plants", "ekat:mud_plants", "ekat:cypress",
                   "patch:reeds", "ekat:waterlog", "ekat:snag", "patch:tallgrass", "ekat:tallgrass",
                   "patch:shrine", "patch:ovl_", "vgen:", "patch:mart", "patch:pc_door",
                   "patch:gym_door", "ekat:log", "ekat:stump", "ekat:cane", "004", "patch:peppers", "patch:cane", "patch:fl_", "patch:fnt_fl", "np:", "patch:gymsign",
                   "ccwr:", "cclr:", "ccsr:", "lep:", "patch:pcw_", "patch:fence_", "patch:sign_dry", "patch:lamp_dry",
                   "patch:se_h", "patch:se_step")  # Crescent City's own opaque pieces (boardwalk planks, flower beds); lep: Land's End's planks


def opt(args, name, default):
    return args[args.index(name) + 1] if name in args else default


def main(args):
    spec_path = args[0]
    out_dir = opt(args, "--out", os.path.join(HERE, "maps"))
    top_n = int(opt(args, "--seams", 40))
    spec = json.load(open(spec_path))
    name = spec["map"]
    stem = os.path.splitext(os.path.basename(spec_path))[0]  # outputs are named after the spec file
    proposal = "_proposal" in spec

    b = Builder(spec_path)
    b.draw()  # terrain, levees, approaches, buildings: the map as built
    ts_cfg = b.ts
    render_path = os.path.join(out_dir, f"_{name}_check.png")
    b.preview(".", render_path, events=False)
    im = Image.open(render_path).convert("RGB")
    px = im.load()
    inv = {}
    for k, v in build.MAPPING.items():
        inv.setdefault(v, k)
    tname = lambda x, y: inv.get(b.blocks[y][x] & 0x3FF, "%03X" % (b.blocks[y][x] & 0x3FF))

    # the dry-country set's crop rows (cane, pepper) are fields with a hard outline like the Ekat cane: object edges
    crops = tuple(ts_cfg["terrain"][c]["tile"] for c in "Gq" if c in ts_cfg["terrain"]
                  and ts_cfg["terrain"][c]["tile"].startswith("dry:"))

    # ---- seams
    d = lambda a, c: sum(abs(p - q) for p, q in zip(a, c))
    seams = []
    for y in range(b.h):
        for x in range(b.w):
            if x + 1 < b.w:
                cross = sum(d(px[x*16+15, y*16+i], px[x*16+16, y*16+i]) for i in range(16)) / 16
                inner = (sum(d(px[x*16+14, y*16+i], px[x*16+15, y*16+i]) for i in range(16)) +
                         sum(d(px[x*16+16, y*16+i], px[x*16+17, y*16+i]) for i in range(16))) / 32
                seams.append((cross - inner, "R", x, y))
            if y + 1 < b.h:
                cross = sum(d(px[x*16+i, y*16+15], px[x*16+i, y*16+16]) for i in range(16)) / 16
                inner = (sum(d(px[x*16+i, y*16+14], px[x*16+i, y*16+15]) for i in range(16)) +
                         sum(d(px[x*16+i, y*16+16], px[x*16+i, y*16+17]) for i in range(16))) / 32
                seams.append((cross - inner, "D", x, y))
    seams.sort(reverse=True)
    # cells within two cells of a dock/bridge/boardwalk footprint or on the map's edge (where levee.py ends a run); lv|lv seams count as
    # real everywhere else
    span = {(bd["x"] + i, bd["y"] + j) for bd in spec.get("buildings", [])
            if bd.get("label") in ("Bridge", "Dock", "Boardwalk", "Pier") and bd.get("rows")
            for j, row in enumerate(bd["rows"]) for i, cell in enumerate(row) if cell is not None}
    near_span = lambda x, y: (any((x + i, y + j) in span for i in range(-2, 3) for j in range(-2, 3))
                              or min(x, y, b.w - 2 - x, b.h - 2 - y) <= 0)  # or the run is cut by the map's edge
    seam_objects = tuple(spec.get("seam_objects", ()))  # a spec may list more object tiles (e.g. its fence pieces)
    terrain = []
    for s, dr, x, y in seams:
        nb = (x + 1, y) if dr == "R" else (x, y + 1)
        a, c = tname(x, y), tname(*nb)
        if a.startswith(OBJECT_PREFIXES + crops + seam_objects) or c.startswith(OBJECT_PREFIXES + crops + seam_objects):
            continue
        if a == c and a.startswith("patch:lv_"):
            continue  # one levee tile repeating down a straight run (its texture repeats by design; the score is palette noise)
        if a.startswith("patch:lv_") and c.startswith("patch:lv_") and near_span(x, y):
            continue  # a levee run's end taper beside a dock or bridge: its whole-stone riprap outline is the art
        if s < 20:
            break
        terrain.append((s, dr, x, y, a, c))
    print(f"terrain seams above 20: {len(terrain)}")
    for s, dr, x, y, a, c in terrain[:30]:
        print(f"  {s:6.1f} {dr} ({x},{y}) {a} | {c}")
    cells = []
    for s, dr, x, y in seams[:top_n]:
        x0, y0 = max(0, x - 1), max(0, y - 1)
        crop = im.crop((x0*16, y0*16, min(b.w, x0+3)*16, min(b.h, y0+3)*16)).resize((144, 144), Image.NEAREST)
        dd = ImageDraw.Draw(crop)
        sx, sy = (x - x0) * 48, (y - y0) * 48
        dd.line([(sx+48, sy), (sx+48, sy+48)] if dr == "R" else [(sx, sy+48), (sx+48, sy+48)], fill=(255, 0, 255))
        dd.text((2, 2), f"{x},{y}{dr}", fill=(255, 255, 0))
        cells.append(crop)
    if cells:
        sheet = Image.new("RGB", (8*148, ((len(cells)+7)//8)*148), (255, 255, 255))
        for k, c in enumerate(cells):
            sheet.paste(c, ((k % 8)*148, (k // 8)*148))
        sheet.save(os.path.join(out_dir, f"{stem}_seams.png"))

    # ---- off-palette grass
    ts = Tilesets(ts_cfg["primary_dir"], ts_cfg["secondary_dir"])
    grass_name = ts_cfg["terrain"]["."]["tile"]
    canon = set(ts.metatile(build.hx(grass_name)).getdata())
    dist2 = lambda a, c: sum((p - q) ** 2 for p, q in zip(a, c))
    grassy = lambda c: c not in canon and min(dist2(c, k) for k in canon) <= 900 and not (c[2] > c[1] - 10)
    bad = defaultdict(list)
    for y in range(b.h):
        for x in range(b.w):
            n = tname(x, y)
            if n.startswith(OBJECT_PREFIXES) or n.startswith(("ekat:", "patch:blend_", "patch:lv_", "patch:ap_", "dry:")):
                continue  # dry:* are the dry set's own edge pieces: they carry their dark grass outline
            off = [c for c in ts.metatile(b.blocks[y][x] & 0x3FF).getdata() if grassy(c)]
            if len(off) >= 4:
                bad[n].append((x, y))
    print(f"tiles with off-palette grass (excluding Ekat terrain and objects): {len(bad)}")
    for n, where in sorted(bad.items(), key=lambda kv: -len(kv[1]))[:15]:
        print(f"  {n} x{len(where)} e.g. {where[:3]}")

    # ---- gameplay (the live map files only; skipped for proposal specs, which aren't written)
    if proposal:
        print("gameplay: skipped (proposal spec, map files not written)")
        problems = []
    inv_b = {v: k for k, v in behavior_ids().items()}
    m = json.load(open(f"data/maps/{name}/map.json")) if not proposal else {"warp_events": [], "object_events": [], "bg_events": []}
    lay = os.path.join(spec["layout_dir"], "map.bin")
    raw = open(lay, "rb").read() if not proposal else struct.pack(f"<{b.w*b.h}H", *b.flat())
    mb = struct.unpack(f"<{len(raw)//2}H", raw)
    W, H = b.w, b.h
    rd = lambda p: struct.unpack('<%dH' % (len(open(p, 'rb').read())//2), open(p, 'rb').read())
    pa = rd(os.path.join(ts_cfg["primary_dir"], "metatile_attributes.bin"))
    sa = rd(os.path.join(ts_cfg["secondary_dir"], "metatile_attributes.bin"))

    def beh(x, y):
        v = mb[y*W+x]
        mid = v & 0x3FF
        a = pa[mid] if mid < 512 else sa[mid-512]
        return inv_b.get(a & 0xFF, "?"), (v >> 10) & 3, v >> 12

    # on foot: ground (elevation 3), bridgeheads (4), the steps between (0) and bridge decks (15); 1 is water
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and not (mb[y*W+x] >> 10) & 3 and (mb[y*W+x] >> 12) in (0, 3, 4, 15)
    problems = []
    for w in m["warp_events"]:
        if "DOOR" not in beh(w["x"], w["y"])[0]:
            problems.append(f"warp ({w['x']},{w['y']}) not on a door tile: {beh(w['x'], w['y'])}")
        if not walk(w["x"], w["y"] + 1):
            problems.append(f"door ({w['x']},{w['y']}) not reachable from below")
    surf_only = {tuple(c) for c in spec.get("surf_only", [])}
    for o in m["object_events"] + m["bg_events"]:
        if o.get("type") == "sign":
            continue  # signs sit on the object they describe; the reachability test covers them
        if not walk(o["x"], o["y"]) and (o["x"], o["y"]) not in surf_only:  # swimmers belong on water
            problems.append(f"event at ({o['x']},{o['y']}) on a blocked or water tile: {beh(o['x'], o['y'])}")
    if m["warp_events"]:
        w0 = m["warp_events"][0]
        start = (w0["x"], w0["y"] + 1)
        # the engine's elevation rule: a walker keeps its elevation on 15 (bridges) and takes 0 (a step) or
        # the cell's own elevation elsewhere; it can't move between two different fixed elevations
        el = lambda x, y: mb[y*W+x] >> 12
        states, q = {(start, 3)}, deque([(start, 3)])
        while q:
            (x, y), e = q.popleft()
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if not walk(nx, ny):
                    continue
                me = el(nx, ny)
                if e != 0 and me not in (0, 15) and me != e:
                    continue
                s = ((nx, ny), e if me == 15 else me)
                if s not in states:
                    states.add(s)
                    q.append(s)
        seen = {c for c, _ in states}
        for w in m["warp_events"]:
            if (w["x"], w["y"] + 1) not in seen:
                problems.append(f"door ({w['x']},{w['y']}) not reachable on foot")
        for o in m["object_events"] + m["bg_events"]:
            if (o["x"], o["y"]) in surf_only:
                continue
            if all((o["x"]+dx, o["y"]+dy) not in seen for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))):
                problems.append(f"event ({o['x']},{o['y']}) not reachable on foot")
        for ex in spec.get("exits", []):
            if ex.get("by_boat"):  # an exit on a bank only a boat reaches (Crescent's far bank): not a walking exit
                continue
            if not any((x, y) in seen for x, y in ex["cells"]):
                problems.append(f"exit {ex['name']} not reachable on foot")
    # prefabs drawn on a patch base (e.g. cypress_marsh) must sit fully inside that patch: every tile's
    # four corner cells must be the patch, or the patch border runs through the object
    for bld in spec.get("buildings", []):
        base = ts_cfg["prefabs"].get(bld["prefab"], {}).get("on_patch")
        if not base:
            continue
        rows = ts_cfg["prefabs"][bld["prefab"]]["rows"]
        edge = [(bld["x"] + i, bld["y"] + j) for j, row in enumerate(rows) for i, cell in enumerate(row)
                if cell and any(b.at(min(bld["x"] + i + dx, W - 1), min(bld["y"] + j + dy, H - 1)) not in base
                                for dx in (0, 1) for dy in (0, 1))]
        if edge:
            problems.append(f"{bld['label']} at ({bld['x']},{bld['y']}) crosses its patch edge at {edge[:4]}")
    print(f"gameplay problems: {len(problems)}")
    for p in problems:
        print("  " + p)

    # ---- comparison with the mockup
    if spec.get("mockup") and os.path.exists(spec["mockup"]):
        det = json.load(open(os.path.join(os.path.dirname(spec_path), spec["grid"].replace(".grid.txt", ".detected.json"))))
        l, t, r, btm = det["frame"]
        mock = Image.open(spec["mockup"]).convert("RGB").crop((l, t, r + 1, btm + 1))
        prev = os.path.join(HERE, "maps", f"{stem}_preview.png")
        b.preview(".", prev)
        new = Image.open(prev)
        new = new.resize((new.width*2, new.height*2), Image.NEAREST)
        mock = mock.resize(new.size)
        out = Image.new("RGB", (new.width*2+30, new.height+40), (255, 255, 255))
        dd = ImageDraw.Draw(out)
        out.paste(mock, (0, 40))
        out.paste(new, (new.width+30, 40))
        dd.text((8, 14), "Mockup", fill=(0, 0, 0))
        dd.text((new.width+38, 14), f"{name} now  (W = door warp, N = NPC, i = item, ? = hidden item)", fill=(0, 0, 0))
        cmp_path = os.path.join(HERE, "maps", f"{stem}_compare.png")
        out.save(cmp_path)
        print("comparison:", cmp_path)
    os.remove(render_path)


if __name__ == "__main__":
    main(sys.argv[1:])

"""Grand Oak (gym 1, Grass): the garden town, laid out by hand from the approved 2026-10-10 build and polished on
2026-10-12 (slice_brief.md). 40 x 34 on the orleans_town tileset (grand_oak_tileset.py: demand-driven, palette v2).

usage (from the decomp root; wrap in `buildlock.py acquire/release grand_oak` when it builds):
    python -W ignore tools/mapgen/grand_oak.py [--review] [--no-build] [--fresh] [--ascii] [--preview out.png]
writes maps/grand_oak.json + maps/grand_oak.grid.txt (events, items, signs and the buildings' interior links are kept
from the spec that is there), applies grand_oak_tileset.py, builds / composes until no overlay is missing, runs check.py;
--review writes maps/00_grand_oak_slice_review.png (before | after and 3x crops). Edit this file, not the spec.

Layout (x right, y down):
    plaza      the Pokemon Center / Mart plaza in the west (rounded ends, 4 rows deep), flowing into the main street
    trunk      the east-west main street (a gentle S), the gate apron in the east where the recruiters stand
    court      the gym's fountain court: a rounded plaza under the glass door, a lawn with the fountain, planters and
               lamps either side
    spine      the north-south main street (it eases a cell west mid-way), bevelled at every junction; it ends in the
               Route 1 road at x 19-20 (kept straight and 2 wide for the last 4 rows, where Route 1 expects it)
    lanes      the nursery's door path and the two south avenues, each rising a row towards its houses; every door has
               a flared apron at least 2 wide
    greenery   magnolias in clumps, avenue lines and a tree-wall edge, varied spacing; mixed-colour flower beds and
               borders along the paths (five colours: the old red flower and the four hollow wildflower drifts); a
               handful of lamps on the main street, the plazas and the court
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import natural  # noqa: E402

KEY, NAME, CONST = "grand_oak", "GrandOak", "MAP_GRAND_OAK"
CFG = "orleans_town"
W, H = 40, 34
SPEC = os.path.join(HERE, "maps", KEY + ".json")
GRID = os.path.join(HERE, "maps", KEY + ".grid.txt")
SEED = 1210

# ---- the fixed design (approved 2026-10-10): prefab, x, y, label. Order matters: it is the warp order
FIXED = [
    ("pokecenter", 5, 8, "Pokemon Center"), ("mart", 11, 8, "Poke Mart"), ("greenhouse", 25, 0, "Gym: glass conservatory"),
    ("fountain", 29, 9, "Fountain"),
    ("planter", 22, 9, "Flower planter"), ("planter", 35, 9, "Flower planter"),
    ("cane", 22, 1, "Sugarcane bed"), ("peppers", 22, 4, "Pepper rows"),
    ("cane", 35, 1, "Sugarcane bed"), ("peppers", 35, 4, "Pepper rows"),    # the gym surround mirrors about x 29.5
    ("house_b", 23, 16, "Garden nursery (Berries)"),
    ("cabin", 3, 24, "House (south-west)"), ("cabin", 9, 24, "House (south-centre)"),
    ("cabin", 32, 24, "House (south-east)"),
    ("planter", 23, 24, "Flower planter"), ("planter", 27, 24, "Flower planter"),
]
# cells that must stay walkable (NPCs, triggers, hidden items, exits)
KEEP_WALK = [(25, 7), (35, 13), (37, 13), (39, 13), (39, 14), (39, 15), (32, 7), (29, 7), (30, 7), (31, 7), (29, 8), (30, 8),
             (31, 8), (11, 21), (26, 27), (19, 33), (20, 33)]
SIGN = (18, 32)


class Town:
    def __init__(self):
        self.cfg = json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))
        self.old = json.load(open(SPEC, encoding="utf-8"))
        self.g = [["."] * W for _ in range(H)]
        self.b = []
        self.occ = {}          # cell -> prefab that stands on it
        self.counts = {}
        self.rng = random.Random(SEED)
        self.doors, self.fronts = [], []
        self.interiors = {b["label"]: b["interior"] for b in self.old["buildings"] if b.get("interior")}

    def rows(self, prefab):
        return self.cfg["prefabs"][prefab]["rows"]

    def box(self, prefab, x, y):
        r = self.rows(prefab)
        return [(x + i, y + j) for j in range(len(r)) for i in range(len(r[0]))]

    def free(self, cells):
        return all(0 <= x < W and 0 <= y < H and (x, y) not in self.occ and self.g[y][x] == "." for x, y in cells)

    def place(self, prefab, x, y, label=None, **kw):
        cells = self.box(prefab, x, y)
        clash = [c for c in cells if c in self.occ]
        if clash:
            raise SystemExit(f"{prefab} at ({x},{y}) overlaps {clash[:4]} ({self.occ[clash[0]]})")
        for c in cells:
            self.occ[c] = prefab
        b = {"prefab": prefab, "x": x, "y": y, "label": label or prefab.replace("_", " ").capitalize()}
        b.update(kw)
        self.b.append(b)
        self.counts[prefab] = self.counts.get(prefab, 0) + 1
        return b


# ---------------------------------------------------------------- the fixed buildings
def buildings(t):
    for prefab, x, y, label in FIXED:
        b = t.place(prefab, x, y, label)
        if label in t.interiors:
            b["interior"] = t.interiors[label]
        d = t.cfg["prefabs"][prefab].get("door")
        if d:
            t.doors.append((x + d[0], y + d[1]))
            t.fronts.append((x + d[0], y + d[1] + 1, prefab))


# ---------------------------------------------------------------- paths
# The path network: straight runs of constant width (streets 3 wide, lanes 2), plazas as regular rounded rectangles /
# octagons, every junction corner bevelled by a 45 degree fillet (a triangle of cells). Route 1's road (x 19-20) arrives
# straight and 2 wide from y 32; the street narrows to it through the bevelled crossing at the avenues.
def block(x0, y0, x1, y1, cut=0):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if min(x - x0, x1 - x) + min(y - y0, y1 - y) >= cut}


def fillet(cx, cy, sx, sy, k):
    """A bevel in the concave corner at (cx, cy): the triangle of k(k+1)/2 cells reaching (-sx, -sy) from the corner."""
    return {(cx - i * sx, cy - j * sy) for i in range(k) for j in range(k - i)}


def design_paths(t):
    P = set()
    P |= block(5, 12, 14, 16, cut=1)                    # the Pokemon Center / Mart plaza (a rounded rectangle)
    P |= block(5, 13, 39, 15)                           # the main street, 3 wide, straight to the gate
    # the gym court: an octagon, the lawn (a smaller octagon, x 28-31, y 9-12) left out, opening into the main street
    P |= {(x, y) for y, (a, b) in {7: (27, 32), 8: (26, 33), 9: (25, 34), 10: (25, 34), 11: (25, 34), 12: (25, 34)}.items()
          for x in range(a, b + 1)} - {(x, y) for y, (a, b) in {9: (29, 30), 10: (28, 31), 11: (28, 31), 12: (29, 30)}.items() for x in range(a, b + 1)}
    P |= {(24, 12), (35, 12)}                          # its bevels where it meets the street
    P |= block(18, 16, 20, 29) | block(19, 30, 20, 33)  # the north-south street, 3 wide, then Route 1's 2
    P |= fillet(17, 16, 1, -1, 1) | fillet(21, 16, -1, -1, 1)     # bevels under the main street
    P |= block(6, 28, 31, 29)                          # the avenues (2-wide lanes), their doors on the top row ...
    P |= block(2, 28, 6, 31, cut=1) | block(31, 28, 35, 31, cut=1)   # ... each ending in a rounded landing at its door
    P |= fillet(17, 27, 1, 1, 1) | fillet(21, 27, -1, 1, 1)       # bevels either side of the crossing
    P |= fillet(18, 30, 1, -1, 1) | fillet(21, 30, -1, -1, 1)     # ... and where the street narrows to the Route 1 road
    # the nursery's forecourt, off the street: a rounded landing under the door (x 26), reached by a 2-wide lane
    P |= block(21, 22, 23, 23) | block(24, 21, 28, 23, cut=0) - {(24, 21), (28, 21)}
    return P


# ---------------------------------------------------------------- lamps, sign, trees, flowers
LAMPS = [(24, 6), (35, 6),             # the gym court's corners
         (3, 9), (16, 10),             # the Pokemon Center / Mart plaza's ends
         (22, 18), (16, 22), (30, 16),  # the main streets, one a side, not mirrored
         (23, 31)]                     # the south entrance


def lamps(t):
    for x, y in LAMPS:
        if not t.free(t.box("lamp", x, y)):
            raise SystemExit(f"lamp at ({x},{y}) is not on free ground")
        t.place("lamp", x, y, "Lamp")


def sign(t):
    t.place("sign", SIGN[0], SIGN[1], "Town sign")


# the magnolias (top-left corners of 2x3 trees), grouped by clump: touching or nearly touching inside a clump, a few
# cells of lawn between clumps, the tree-wall along the west, north and south edges
TREES = [
    # north-west: a deep grove, a glade (x 9-10), a second grove, one tree by the gym
    (0, 0), (2, 1), (0, 3), (4, 0), (5, 3), (7, 1),
    (9, 4), (11, 1), (13, 0), (15, 2), (18, 0), (17, 4), (19, 3),
    (20, 8), (18, 7),
    # the west edge, a grove round the hidden seed (x 11, y 21: a pocket open to the north), the middle west
    (0, 7), (1, 10), (0, 14), (0, 17), (0, 21), (0, 24), (0, 28),
    (3, 16), (5, 18), (2, 19), (7, 18), (9, 19), (7, 21), (12, 18), (14, 18), (13, 21),
    # the south wall (varied gaps) and the south-east corner
    (0, 31), (7, 31), (9, 31), (11, 31), (14, 31),
    (24, 31), (26, 31), (29, 31), (37, 31),
    (36, 28),
    # east of the nursery: an avenue line and a grove
    (28, 18), (31, 19), (34, 17), (36, 20),
    # the east tree-wall (x 38-39): the road to Route 2 (rows 13-15, closed by the storm hedge) is the only gap, so the hedge really
    # gates Route 2 (the connection covers rows 5-30). Rows 4-12 and 16-30, 3 rows a tree.
    (38, 4), (38, 7), (38, 10), (38, 16), (38, 19), (38, 22), (38, 25), (38, 28),
]

def trees(t):
    t.tree_list = []
    for x, y in TREES:
        cells = t.box("magnolia", x, y)
        bad = [c for c in cells if c in t.occ or not (0 <= c[0] < W and 0 <= c[1] < H) or t.g[c[1]][c[0]] != "."]
        if bad:
            print(f"magnolia at ({x},{y}) skipped: {bad[:3]} taken")
            continue
        t.place("magnolia", x, y, "Magnolia")
        t.tree_list.append((x, y))


def col(x, y, n):
    return [(x, y + j) for j in range(n)]


def rect(x, y, w, h):
    return [(x + i, y + j) for j in range(h) for i in range(w)]


# flower beds and borders, each a list of cells; every cell of a bed gets a different colour from its neighbours
BEDS = [   # formal beds and borders: tidy rectangles and lines, every cell a different colour from its neighbours
    [(28, 10), (28, 11), (31, 10), (31, 11), (29, 12), (30, 12)],              # the ring round the fountain lawn
    rect(9, 9, 2, 3), col(4, 9, 3), col(15, 9, 3),                             # the Center / Mart plaza
    [(x, 12) for x in range(17, 24)],                                          # the main street's north border
    col(2, 26, 2), col(6, 26, 2), col(8, 26, 2), col(12, 26, 2), col(31, 26, 2), col(35, 26, 2),   # flanking the doors
    [(23, 27), (24, 27), (25, 27)], [(27, 27), (28, 27), (29, 27)],            # under the south planters
    rect(22, 6, 2, 3), rect(36, 6, 2, 3),                                      # beside the gym front, mirrored
]
BLOOMS = ["flowers", "bloom_pink", "bloom_violet", "bloom_blue", "bloom_white", "bloom_yellow"]


def flowers(t, seed=SEED + 1):
    rng = random.Random(seed)
    used = {k: 0 for k in BLOOMS}
    at = {}
    for bed in BEDS:
        cells = [c for c in bed if t.free([c]) and c not in at]
        rng.shuffle(cells)
        cells.sort(key=lambda c: (c[1], c[0]))
        for c in cells:
            near = {at[(c[0] + i, c[1] + j)] for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2) if (c[0] + i, c[1] + j) in at}
            adj = {at[(c[0] + i, c[1] + j)] for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (c[0] + i, c[1] + j) in at}
            opts = [k for k in BLOOMS if k not in adj]
            best = min(used[k] + (3 if k in near else 0) + rng.random() for k in opts)
            k = next(k for k in opts if used[k] + (3 if k in near else 0) + rng.random() >= best - 1e-9) if False else min(
                opts, key=lambda k: used[k] + (3 if k in near else 0) + rng.random() * 1.5)
            at[c] = k
            used[k] += 1
    for c, k in sorted(at.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        t.place(k, c[0], c[1], "Flowers")
    t.counts["bloom colours"] = used


def ascii_map(t):
    out = []
    for y in range(H):
        line = ""
        for x in range(W):
            if (x, y) in t.occ:
                n = t.occ[(x, y)]
                line += {"magnolia": "T", "lamp": "l", "flowers": "f", "planter": "p"}.get(n, "f" if n.startswith("bloom") else "B")
            else:
                line += t.g[y][x]
        out.append(f"{y:2d} {line}")
    return "\n".join(out)


def build_town():
    t = Town()
    buildings(t)
    P = design_paths(t)
    for x, y in P:
        if 0 <= x < W and 0 <= y < H and (x, y) not in t.occ:
            t.g[y][x] = ":"
    t.pathcells = {(x, y) for y in range(H) for x in range(W) if t.g[y][x] == ":"}
    lamps(t)
    sign(t)
    trees(t)
    flowers(t)
    return t


def render_town(t, out, scale=1):
    """Terrain and buildings as the builder draws them (nothing is written to data/)."""
    import build
    from render import Tilesets, render
    spec = dict(t.old)
    spec["edits"], spec["buildings"], spec["grid"] = [], t.b, KEY + "_tmp.grid.txt"
    tmp_g = os.path.join(HERE, "maps", KEY + "_tmp.grid.txt")
    tmp = os.path.join(HERE, "maps", KEY + "_tmp.json")
    open(tmp_g, "w").write("\n".join("".join(r) for r in t.g) + "\n")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    build.MAPPING.clear()
    b = build.Builder(tmp)
    os.remove(tmp)
    os.remove(tmp_g)
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    im = render(ts, b.flat(), b.w).convert("RGB")
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale))
    im.save(out)
    print("preview", out, im.size)
    return b


# ---------------------------------------------------------------- review sheet
REVIEW_AREAS = [   # (title, x0, y0, x1, y1) in tiles
    ("The gym court and the north-east", 20, 0, 40, 15),
    ("Pokemon Center / Mart plaza and the north-west grove", 0, 4, 22, 18),
    ("The crossing, the nursery path and the hidden-seed grove", 0, 12, 34, 28),
    ("The south: avenues, door tabs, sign, wall, Route 1 road", 0, 24, 40, 34),
    ("The gate and the east grove", 28, 10, 40, 24),
]


def review(t, out):
    from PIL import Image, ImageDraw, ImageFont
    after_path = os.path.join(HERE, "maps", KEY + "_after.png")
    render_town(t, after_path)
    before = Image.open(os.path.join(HERE, "maps", KEY + "_before.png")).convert("RGB")
    after = Image.open(after_path).convert("RGB")
    font = ImageFont.truetype("arial.ttf", 30) if os.path.exists("C:/Windows/Fonts/arial.ttf") else ImageFont.load_default()
    pad, head = 24, 44
    width = 2 * 1280 + 3 * pad
    blocks = [("Before (the approved 2026-10-10 build)", before.resize((1280, 1088), Image.NEAREST)),
              ("After (slice polish 2026-10-12)", after.resize((1280, 1088), Image.NEAREST))]
    blocks_b = []
    for title, x0, y0, x1, y1 in REVIEW_AREAS:
        box = (x0 * 16, y0 * 16, x1 * 16, y1 * 16)
        size = ((x1 - x0) * 48, (y1 - y0) * 48)
        blocks_b.append([(f"Before: {title}", before.crop(box).resize(size, Image.NEAREST)),
                         (f"After: {title}", after.crop(box).resize(size, Image.NEAREST))])
    # lay the blocks out in rows: the two panels of a pair go side by side when they fit, else one under the other
    rows = [blocks] + blocks_b
    height = pad
    for pair in rows:
        side = sum(im.width for _, im in pair) + (len(pair) + 1) * pad <= width
        height += (head + max(im.height for _, im in pair) + pad) if side else sum(head + im.height + pad for _, im in pair)
    sheet = Image.new("RGB", (width, height), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    y = pad
    for pair in rows:
        side = sum(im.width for _, im in pair) + (len(pair) + 1) * pad <= width
        x = pad
        for title, im in pair:
            d.text((x, y), title, fill=(0, 0, 0), font=font)
            sheet.paste(im, (x, y + head))
            if side:
                x += im.width + pad
            else:
                y += head + im.height + pad
        if side:
            y += head + max(im.height for _, im in pair) + pad
    sheet.save(out)
    print("review sheet:", out, sheet.size)


NL = chr(10)


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline=NL) as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write(NL)


def sh(args, **kw):
    return subprocess.run([sys.executable, "-W", "ignore"] + args, text=True, capture_output=True, **kw)


def write_spec(t):
    open(GRID, "w", encoding="utf-8", newline=NL).write(NL.join("".join(r) for r in t.g) + NL)
    spec = dict(t.old)
    spec["_comment"] = "Grand Oak, handmade: generated by grand_oak.py (edit that, not this file)."
    spec["edits"], spec["buildings"] = [], t.b
    spec["grid"] = KEY + ".grid.txt"
    for o in spec["objects"]:       # the gardener's second line was 38 characters (the box holds 36)
        o["text"] = o["text"].replace("Come back when the storms have passed.", "Come back after the storms.")
    spec["signs"] = [dict(sg, x=SIGN[0], y=SIGN[1]) for sg in spec["signs"]]    # the town sign, beside the street
    dump(SPEC, spec)


def main(args):
    print(sh([os.path.join(HERE, "grand_oak_tileset.py")]).stdout.strip()[-200:])
    t = build_town()
    if "--ascii" in args:
        print("   " + "".join(str(i % 10) for i in range(W)))
        print(ascii_map(t))
    print("placed:", dict(sorted(t.counts.items())))
    print("path badness:", natural.total_bad(["".join(r) for r in t.g]))
    if "--preview" in args:
        render_town(t, args[args.index("--preview") + 1])
    if "--review" in args:
        review(t, os.path.join(HERE, "maps", "00_grand_oak_slice_review.png"))
    if "--no-build" in args or "--preview" in args or "--review" in args:
        return
    write_spec(t)
    recipe = os.path.join(HERE, "tilesets", "recipes", CFG + ".json")
    if "--fresh" in args:    # start the overlay requests over, so pieces no longer used don't take tiles
        with open(os.path.join(HERE, "tilesets", CFG + ".blends.json"), "w") as f:
            json.dump([], f)
    for i in range(6):       # build (writes the uses file and asks for overlays), compose, build again
        r = sh([os.path.join(HERE, "build.py"), SPEC])
        print(r.stdout.strip()[-1500:], r.stderr.strip()[-2000:])
        if i and "transition tiles needed" not in r.stdout:
            break
        c = sh([os.path.join(HERE, "compose.py"), recipe])
        print(c.stdout.strip()[-1500:], c.stderr.strip()[-1500:])
        if c.returncode:
            return
    # settle: palette v2 weighs colours by what the built map shows, so compose once more against the finished map
    # (it moves a few shifted greens back), then build again so map.bin matches the final mapping
    c = sh([os.path.join(HERE, "compose.py"), recipe])
    print(c.stdout.strip()[-1100:], c.stderr.strip()[-1500:])
    r = sh([os.path.join(HERE, "build.py"), SPEC])
    print(r.stdout.strip()[-300:], r.stderr.strip()[-1000:])
    c = sh([os.path.join(HERE, "check.py"), SPEC])
    print(c.stdout.strip()[-3000:], c.stderr.strip()[-2000:])


if __name__ == "__main__":
    main(sys.argv[1:])

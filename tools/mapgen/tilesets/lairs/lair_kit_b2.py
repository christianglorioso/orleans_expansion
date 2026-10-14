"""Shared kit for the legendary lairs, BATCH 2 (lair_kit.py's Canvas / Pieces / dual sets / LairMap, plus what batch 2 adds).

What batch 2 adds:
  * write_b2(): Pieces.write() with the outputs kept apart from batch 1: the sheet + json land in tilesets/lairs/ under the
    batch-2 name, the compose recipe in tilesets/lairs/recipes_b2/. A batch-2 recipe for a batch-1 secondary (lk, ls, ld) is
    a SUPERSET of the batch-1 one: the batch-1 pieces come first, in the same order and at the same sheet cells, so every
    batch-1 metatile keeps its id; it replaces the batch-1 recipe only when the user approves batch 2 (LAYOUT_HANDOFF_batch2.md).
  * stage_compose(): composes a recipe in a STAGING copy of the tree (the system temp dir), never in data/: the budget and the
    "every metatile draws its art" check without touching the committed tilesets.
  * drawing helpers the batch-2 art scripts share (shaded bodies, posts, planks, bricks, ropes).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit import (CORNER_KEYS, KEY, MAPGEN, ROOT, SRC, Canvas, LairMap, Pieces, check_families, dual_set, dump,  # noqa: E402,F401
                      gba, hashn, over, pcell, scale, sheet_cell, tex_from)
import render  # noqa: E402

STAGE = os.path.join(tempfile.gettempdir(), "orleans_lairs_b2_stage")
REVIEW = os.path.normpath(os.path.join(ROOT, "..", "tile_review", "set_pieces", "lairs", "batch2"))
RECIPES_B2 = os.path.join(HERE, "recipes_b2")

GRASS = tex_from(pcell("ekat:grass"))
WATER = tex_from(pcell("ekat:water_C"))
MARSH = tex_from(pcell("ekat:marsh_C"))
DRY = tex_from(pcell("dry:0_0"))

# the primary's grass and the swamp canopy's own colours (make_borders CORE_PAL)
G, GD, GL, SH = (120, 160, 104), (104, 144, 96), (136, 176, 128), (96, 128, 88)
S_OUT, C_DK, C_MID, C_HL, C_TIP = (40, 56, 40), (64, 96, 64), (80, 112, 96), (104, 152, 120), (144, 184, 152)


# ---------------------------------------------------------------- writing (batch-2 names, recipes_b2/)
def write_b2(P, png, dirname, symbol, primary_mapping, families, title, script):
    """P.write() for batch 2: sheet + json in tilesets/lairs/<png>, the recipe in recipes_b2/<dirname>.json. Returns the
    off-family tiles."""
    P.pack()
    P.image.save(os.path.join(HERE, png))
    mts, pieces = [], {}
    for n in P.order:
        it = P.items[n]
        cv = it["cv"]
        px, py = P.pos[n]
        names = P.cell_names(n)
        for j in range(cv.ch):
            for i in range(cv.cw):
                e = {"id": names[j][i].split(":", 1)[1], "bottom": [px + i, py + j]}
                if it["behavior"] and (i, j) in it["behavior"]:
                    e["behavior"] = it["behavior"][(i, j)]
                mts.append(e)
        walk = it["walk"]
        walk = [[i, j] for j in range(cv.ch) for i in range(cv.cw)] if walk is True else (walk or [])
        pieces[n] = {"x": px, "y": py, "w": cv.cw, "h": cv.ch, "rows": names, "walk": walk,
                     "lair": it["lair"], "comment": it["comment"]}
    dump(os.path.join(HERE, png.replace(".png", ".json")), {
        "_comment": f"{title}: piece -> sheet cells (16 px, every cell opaque: props are baked over their ground), metatile names "
                    f"('{P.prefix}:<id>' in {symbol}), walkable cells (the rest block), the lair it belongs to. Made by {script} "
                    f"(legendary lairs batch 2).",
        "png": png, "tileset": symbol, "families": {k: [list(c) for c in v] for k, v in families.items()},
        "pieces": pieces})
    os.makedirs(RECIPES_B2, exist_ok=True)
    dump(os.path.join(RECIPES_B2, dirname + ".json"), {
        "_comment": f"{title} (own art, tools/mapgen/tilesets/lairs, batch 2). Budget check without touching data/: "
                    f"lair_mocks_b2.py composes it in a staging tree. To register (after the user approves batch 2): copy into "
                    f"tilesets/recipes/, set primary_mapping to '{primary_mapping}', compose --register.",
        "kind": "secondary", "dir": dirname, "symbol": symbol, "primary_mapping": "../" + primary_mapping,
        "palette": "v2",
        "sources": [{"name": P.prefix, "type": "image", "image": f"tools/mapgen/tilesets/lairs/{png}",
                     "transparent": [[255, 0, 255]], "group_rule": "fewest", "metatiles": mts}]})
    return check_families([(n, P.items[n]["cv"].im) for n in P.order], families, P.prefix)


# ---------------------------------------------------------------- staging compose and the art check
def _stage_tree():
    os.makedirs(os.path.join(STAGE, "tools", "mapgen", "tilesets", "lairs", "recipes_b2"), exist_ok=True)
    os.makedirs(os.path.join(STAGE, "include", "constants"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "include", "constants", "metatile_behaviors.h"),
                os.path.join(STAGE, "include", "constants", "metatile_behaviors.h"))
    for prim in ("orleans_general", "orleans_building"):
        src = os.path.join(MAPGEN, "tilesets", f"{prim}.mapping.json")
        shutil.copy(src, os.path.join(STAGE, "tools", "mapgen", "tilesets", f"{prim}.mapping.json"))
        dst = os.path.join(STAGE, "data", "tilesets", "primary", prim)
        if not os.path.exists(dst):
            shutil.copytree(os.path.join(ROOT, "data", "tilesets", "primary", prim), dst)


def stage_compose(recipe_name, png):
    """Compose recipes_b2/<recipe_name>.json in the staging tree. Returns (summary line, palette report lines, the stdout)."""
    _stage_tree()
    sl = os.path.join(STAGE, "tools", "mapgen", "tilesets", "lairs")
    shutil.copy(os.path.join(HERE, png), os.path.join(sl, png))
    shutil.copy(os.path.join(RECIPES_B2, recipe_name + ".json"), os.path.join(sl, "recipes_b2", recipe_name + ".json"))
    out = os.path.join(STAGE, "data", "tilesets", "secondary", recipe_name)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "palettes"), exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(MAPGEN, "compose.py"),
                        f"tools/mapgen/tilesets/lairs/recipes_b2/{recipe_name}.json"], cwd=STAGE, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"compose {recipe_name} failed:\n{r.stdout}\n{r.stderr}")
    line = [l for l in r.stdout.splitlines() if "metatiles" in l and "tiles" in l][0].strip()
    pal = [l.strip() for l in r.stdout.splitlines() if "colours in 15" in l or "reduced to 15" in l or "palette v2" in l]
    return line, pal, r.stdout


def stage_verify(recipe_name, png, prefix, primary_dir):
    """Every staged metatile must draw its sheet cell exactly (at GBA colour depth): (cells off, worst shift)."""
    sl = os.path.join(STAGE, "tools", "mapgen", "tilesets", "lairs")
    mp = json.load(open(os.path.join(sl, f"{recipe_name}.mapping.json")))["metatiles"]
    rec = json.load(open(os.path.join(RECIPES_B2, recipe_name + ".json")))
    ts = render.Tilesets(os.path.join(STAGE, "data", "tilesets", "primary", primary_dir),
                         os.path.join(STAGE, "data", "tilesets", "secondary", recipe_name))
    from PIL import Image
    sheet = Image.open(os.path.join(HERE, png)).convert("RGB")
    off, worst = 0, 0.0
    for m in rec["sources"][0]["metatiles"]:
        bx, by = m["bottom"]
        ref = sheet.crop((bx * 16, by * 16, bx * 16 + 16, by * 16 + 16)).load()
        got = ts.metatile(mp[f"{prefix}:{m['id']}"]).convert("RGB").load()
        bad = False
        for y in range(16):
            for x in range(16):
                a = tuple((v >> 3) << 3 for v in ref[x, y])
                b = got[x, y]
                if a != b:
                    bad = True
                    worst = max(worst, sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5)
        off += bad
    return off, worst


def staged_tileset(recipe_name, primary_dir):
    return render.Tilesets(os.path.join(STAGE, "data", "tilesets", "primary", primary_dir),
                           os.path.join(STAGE, "data", "tilesets", "secondary", recipe_name))


# ---------------------------------------------------------------- drawing helpers
def ground_cv(fn, w=1, h=1):
    cv = Canvas(w, h)
    for j in range(cv.h):
        for i in range(cv.w):
            cv.put(i, j, fn(i, j))
    return cv


def ink_outline(cv, body, ink, sides=((1, 0), (-1, 0), (0, -1), (0, 1)), only_clear=True):
    for (x, y) in list(body):
        for dx, dy in sides:
            q = (x + dx, y + dy)
            if q not in body and (not only_clear or cv.get(*q) is None):
                cv.put(q[0], q[1], ink)


def fill_body(cv, body, col):
    """col(x, y) -> colour, for every pixel of the body."""
    for (x, y) in body:
        cv.put(x, y, col(x, y))


def ellipse_body(cx, cy, rx, ry):
    out = set()
    for j in range(int(cy - ry - 1), int(cy + ry + 2)):
        for i in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((i + 0.5 - cx) / rx) ** 2 + ((j + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((i, j))
    return out


def lit(body, x, y, ramp, cx=None, cy=None):
    """A light-from-the-upper-left ramp over a body: ramp = [darkest .. lightest]."""
    xs = [p[0] for p in body]
    ys = [p[1] for p in body]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    t = ((x - x0) / max(1, x1 - x0)) * 0.6 + ((y - y0) / max(1, y1 - y0)) * 0.4
    k = len(ramp) - 1 - int(t * (len(ramp) - 0.01))
    return ramp[max(0, min(len(ramp) - 1, k))]


def post(cv, x, y0, y1, light, mid, dark, ink, w=3):
    """A vertical round post (w px wide) from y0 to y1 inclusive, outlined."""
    for j in range(y0, y1 + 1):
        for k in range(w):
            cv.put(x + k, j, light if k == 0 else (dark if k == w - 1 else mid))
        cv.put(x - 1, j, ink)
        cv.put(x + w, j, ink)
    cv.hline(x - 1, x + w, y0 - 1, ink)


def shadow_under(cv, x0, x1, y, col):
    for i in range(x0, x1 + 1):
        if cv.get(i, y) is None:
            cv.put(i, y, col)


def planks_h(cv, x0, y0, w, h, cols, ink, seam_every=8, seed=0):
    """Horizontal boards (rows of 4 px), board ends staggered."""
    l, m, d = cols
    for j in range(h):
        row = j // 4
        for i in range(w):
            c = m
            if j % 4 == 0:
                c = l
            elif j % 4 == 3:
                c = d
            if (i + row * 5 + seed) % seam_every == 0:
                c = ink if j % 4 else d
            cv.put(x0 + i, y0 + j, c)


def planks_v(cv, x0, y0, w, h, cols, ink, seam_every=11, seed=0):
    """Vertical boards (4 px wide), board ends staggered."""
    l, m, d = cols
    for i in range(w):
        col = i // 4
        for j in range(h):
            c = m
            if i % 4 == 0:
                c = l
            elif i % 4 == 3:
                c = d
            if (j + col * 7 + seed) % seam_every == 0:
                c = ink if i % 4 else d
            cv.put(x0 + i, y0 + j, c)


def bricks(cv, x0, y0, w, h, cols, mortar, course=4, brick=8, wear=0.0, seed=0):
    """Running-bond brick: cols = (light, mid, dark) brick colours; `wear` > 0 knocks pale spots out."""
    l, m, d = cols
    for j in range(h):
        row = j // course
        for i in range(w):
            off = (brick // 2) if row % 2 else 0
            if j % course == course - 1 or (i + off) % brick == 0:
                c = mortar
            else:
                c = m
                if j % course == 0:
                    c = l
                elif (i + off) % brick == brick - 1:
                    c = d
                if hashn((i + off) // brick + x0, row + y0, 61 + seed) < 0.25:
                    c = d if c == m else c
            if wear and hashn(x0 + i, y0 + j, 62 + seed) < wear:
                c = mortar
            cv.put(x0 + i, y0 + j, c)


def rope(cv, x0, y0, x1, y1, sag, col, dark=None):
    """A sagging rope between two points."""
    n = max(abs(x1 - x0), 1)
    for k in range(n + 1):
        t = k / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
        cv.put(round(x), round(y), col)
        if dark:
            cv.put(round(x), round(y) + 1, dark)


def sparkle(cv, x, y, c1, c2):
    cv.put(x, y, c1)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if cv.get(x + dx, y + dy) is not None:
            cv.put(x + dx, y + dy, c2)


def mirror_piece(cv):
    return cv.copy().flip_x()


def colours_of(cv):
    out = set()
    for j in range(cv.h):
        for i in range(cv.w):
            c = cv.get(i, j)
            if c is not None:
                out.add(gba(c))
    return out


def snap(cv, palette):
    """Map every colour of the canvas to the nearest colour of `palette` (exact family colours only)."""
    pal = [gba(c) for c in palette]
    for j in range(cv.h):
        for i in range(cv.w):
            c = cv.get(i, j)
            if c is not None and gba(c) not in pal:
                cv.put(i, j, min(pal, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, c))))
    return cv

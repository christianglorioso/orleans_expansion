"""Review sheet + budget numbers for the border OUTER corners and the strict-band-safe (primary) dry set, 2026-10-13.

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/border_corners_review.py

Reads (never writes game data):
  tile_review/proto_isle_marais_after.png, proto_route_16_after.png   the main session's prototype renders (2x, +7/+5 cell margin)
  an in-memory build of isle_marais and route_16 (build.Builder, as feather_dbg.py does) for the missing-corner list and the walls
  data/tilesets/primary/orleans_general                                     the primary's tiles and palettes, for the counts
Writes:
  tools/mapgen/tilesets/borders/primary_dry/pdry_*.png   the primary dry set (make_borders art recoloured into primary palette 2)
  tools/mapgen/tilesets/borders/primary_dry/pdry.json    its index, tiers and counts
  tile_review/art_edge_corners.png                          the review sheet
"""
import hashlib
import json
import os
import struct
import sys
import warnings

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_borders as mb  # noqa: E402
import make_border_corners as mc  # noqa: E402

ROOT, MAPGEN = mb.ROOT, mb.MAPGEN
REVIEW = os.path.normpath(os.path.join(ROOT, "..", "tile_review"))
PDRY_DIR = os.path.join(MAPGEN, "tilesets", "borders", "primary_dry")
PRIM = os.path.join(ROOT, "data", "tilesets", "primary", "orleans_general")
MARGIN = (7, 5)

# ---------------------------------------------------------------- the primary dry set: DRY_PAL -> primary palette 2
# Palette 2 of gTileset_OrleansGeneral already holds the dry ground (dry:0_0 = DH D1 D2) and the core greens; every primary palette
# is full (6 x 15, 82 distinct colours in use), so the dry scrub cannot bring its own 15 colours. Each DRY_PAL colour goes to the
# palette-2 colour of the same role (lightness ladder kept: outline < deep < dark < mid < light).
P2 = {   # DRY_PAL colour -> palette 2 colour
    mb.DH: mb.DH, mb.D1: mb.D1, mb.D2: mb.D2,
    mb.D3: (160, 136, 120),                         # deep shade on the ground
    mb.ST: (200, 168, 112), mb.ST_D: (160, 136, 120),   # straw tufts -> sand shades
    mb.L0: (48, 48, 40), mb.L1: (64, 96, 64), mb.L2: (88, 120, 88), mb.L3: (120, 160, 104), mb.L4: (136, 176, 128),
    mb.K0: (104, 88, 80), mb.K1: (160, 136, 120), mb.K2: (224, 200, 144), mb.B0: (96, 64, 64),
}
PDRY_FACES = [("S", 0), ("S", 1), ("N", 0), ("N", 1), ("E", 0), ("E", 1), ("W", 0), ("W", 1),
              ("in_NW", None), ("in_NE", None), ("in_SW", None), ("in_SE", None),
              ("out_NW", None), ("out_NE", None), ("out_SW", None), ("out_SE", None)]
TIERS = {   # what each tier lets the feather pass draw inside a dry strict band
    "T1": ("S_0", "S_1", "N_0", "N_1", "W_0", "W_1", "in_NE"),
    "T2": ("S_0", "S_1", "N_0", "N_1", "W_0", "W_1", "in_NE", "E_0", "E_1", "in_NW", "in_SW", "out_NW", "out_SW"),
    "T3": tuple(f + ("" if p is None else f"_{p}") for f, p in PDRY_FACES),
}


def recolour(img, table=P2):
    a = np.array(img.convert("RGB"))
    out = a.copy()
    for src, dst in table.items():
        m = np.all(a == src, axis=-1)
        out[m] = dst
    return Image.fromarray(out)


def pdry_cells(g):
    cells = {}
    for face, par in PDRY_FACES:
        nm = face + ("" if par is None else f"_{par}")
        if face in mb.OUTER:
            img = mb.outer_cell("dry", face, g["dry"], g)[0]
        else:
            img = mb.edge_cell("dry", face, par, g["dry"], g)[0]
        cells[nm] = recolour(img)
    return cells


# ---------------------------------------------------------------- counting against the primary
def canon(t):
    return min(x.tobytes() for x in (t, t[:, ::-1], t[::-1], t[::-1, ::-1]))


def tiles_of(img):
    a = np.array(img.convert("RGB"))
    return [a[y:y + 8, x:x + 8] for y in range(0, a.shape[0], 8) for x in range(0, a.shape[1], 8)]


def primary_state():
    """(set of canonical RGB 8x8 tiles the primary already draws, numbers)"""
    im = Image.open(os.path.join(PRIM, "tiles.png"))
    a = np.array(im)
    W = a.shape[1] // 8
    pals = []
    for p in range(16):
        L = open(os.path.join(PRIM, "palettes", f"{p:02d}.pal")).read().split("\n")
        pals.append([tuple(map(int, l.split())) for l in L[3:] if l.strip()])
    mt = open(os.path.join(PRIM, "metatiles.bin"), "rb").read()
    known, tiles_used = set(), set()
    for i in range(len(mt) // 16):
        if not any(mt[i * 16:i * 16 + 16]):
            continue
        for k in range(8):
            v = struct.unpack_from("<H", mt, i * 16 + k * 2)[0]
            t, p = v & 0x3FF, (v >> 12) & 0xF
            if t >= 512:
                continue
            tiles_used.add(t)
            idx = a[(t // W) * 8:(t // W) * 8 + 8, (t % W) * 8:(t % W) * 8 + 8]
            rgb = np.array(pals[p], dtype=np.uint8)[idx]
            if v & 0x400:
                rgb = rgb[:, ::-1]
            if v & 0x800:
                rgb = rgb[::-1]
            known.add(canon(rgb))
    mapping = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]
    pal_full = []
    for p in range(6):
        pal_full.append(len(set(pals[p][1:])))
    return known, {"tiles_used": len(tiles_used), "tiles_free": 512 - len(tiles_used), "metatiles_named": len(set(mapping.values())),
                   "metatiles_free": 512 - len(set(mapping.values())), "palette_colours": pal_full,
                   "pal2": pals[2][1:]}


def new_tiles(imgs, known):
    seen, n, cols = set(known), 0, set()
    for im in imgs:
        cols |= set(map(tuple, np.array(im.convert("RGB")).reshape(-1, 3)))
        for t in tiles_of(im):
            k = canon(t)
            if k not in seen:
                seen.add(k)
                n += 1
    return n, cols


# ---------------------------------------------------------------- the prototype maps
def probe(keys):
    """in-memory builds: missing corners (x, y, corner, ground name), walls, edges, strict band cells"""
    warnings.filterwarnings("ignore")
    cwd = os.getcwd()
    os.chdir(ROOT)
    sys.path.insert(0, MAPGEN)
    import build
    import bands
    out = {}
    try:
        for key in keys:
            b = build.Builder(os.path.join(MAPGEN, "maps", key + ".json"))
            b.draw()
            inv = {}
            for n, v in build.MAPPING.items():
                inv.setdefault(v, n)
            out[key] = {"w": b.w, "h": b.h, "wall": set(b.wall), "edge": dict(b.edge),
                        "missing": [(x, y, nm, inv.get(b.blocks[y][x] & 0x3FF, "?")) for x, y, nm in b.feather_missing],
                        "strict": set(bands.all_band_cells(key)), "grid": [list(r) for r in b.grid]}
    finally:
        os.chdir(cwd)
    return out


def load_render(name):
    im = Image.open(os.path.join(REVIEW, name)).convert("RGB")
    return im.resize((im.width // 2, im.height // 2), Image.NEAREST)


def cell_box(x, y):
    X, Y = (x + MARGIN[0]) * 16, (y + MARGIN[1]) * 16
    return (X, Y, X + 16, Y + 16)


def place_corners(key, style, P, render_1x, g):
    """paste every missing outer corner, baked on the render's own ground pixels; returns (image, placed, skipped)"""
    im = render_1x.copy()
    placed, skipped = [], []
    wall = P["wall"]
    for x, y, corner, under in P["missing"]:
        four = any((x + dx, y + dy) in wall for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if four:
            skipped.append((x, y, corner, "a face cell the pass left plain (strict band / seam), not a corner"))
            continue
        if style == "dry" and (x, y) in P["strict"]:
            skipped.append((x, y, corner, "in a strict band: secondary art not allowed (primary dry set)"))
            continue
        base = render_1x.crop(cell_box(x, y))
        cellim = mb.outer_cell(style, corner, base, g)[0]
        im.paste(cellim, cell_box(x, y)[:2])
        placed.append((x, y, corner, under))
    return im, placed, skipped


def band_mock(P, render_1x, pd, g):
    """Route 16 east: inside the strict band (columns w-8 .. w-1) the faces / corners the primary dry set covers, on plain sand
    only, as the feather pass would place them with the band's wall at depth 0 (the border is the wall); returns (image, uses)"""
    w, h = P["w"], P["h"]
    wall = set(P["wall"])
    sp = {"N": [(0, w)], "S": [(0, w)], "W": [(0, 4)], "E": [(0, 5)]}   # borders.unconnected('route_16')

    def is_wall(x, y):
        if 0 <= x < w and 0 <= y < h:
            return (x, y) in wall
        if x < 0 and 0 <= y < h:
            return any(lo <= y < hi for lo, hi in sp["W"])
        if x >= w and 0 <= y < h:
            return any(lo <= y < hi for lo, hi in sp["E"])
        if y < 0 and 0 <= x < w:
            return any(lo <= x < hi for lo, hi in sp["N"])
        if y >= h and 0 <= x < w:
            return any(lo <= x < hi for lo, hi in sp["S"])
        return True
    seam = {(x, y) for x in range(w - 3, w) for y in range(5, h)}
    im = render_1x.copy()
    uses = {}
    for y in range(h):
        for x in range(w - 8, w):
            if (x, y) in wall or (x, y) in seam or P["grid"][y][x] != "d":
                continue
            n, s, we, e = is_wall(x, y - 1), is_wall(x, y + 1), is_wall(x - 1, y), is_wall(x + 1, y)
            face = None
            if n or s or we or e:
                face = ("in_NW" if n and we else "in_NE" if n and e else "in_SW" if s and we else "in_SE" if s and e
                        else "S" if n else "N" if s else "E" if we else "W")
                if not face.startswith("in_"):
                    face += f"_{(x if face in 'SN' else y) & 1}"
            else:
                for dx, dy, nm in ((-1, -1, "out_NW"), (1, -1, "out_NE"), (-1, 1, "out_SW"), (1, 1, "out_SE")):
                    if is_wall(x + dx, y + dy):
                        face = nm
            if face:
                im.paste(pd[face], cell_box(x, y)[:2])
                uses[face] = uses.get(face, 0) + 1
    return im, uses


# ---------------------------------------------------------------- sheet helpers
def font(size):
    return mb.font(size)


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def boxes(im, cells, k, col=(255, 0, 255)):
    im = im.copy()
    d = ImageDraw.Draw(im)
    for x, y in cells:
        X, Y = (x + MARGIN[0]) * 16 * k, (y + MARGIN[1]) * 16 * k
        d.rectangle((X, Y, X + 16 * k - 1, Y + 16 * k - 1), outline=col, width=2)
    return im


def main(argv):
    g = mc.grounds()
    corners, index, _ = mc.build(g)
    pd = pdry_cells(g)
    os.makedirs(PDRY_DIR, exist_ok=True)
    for nm, im in pd.items():
        im.save(os.path.join(PDRY_DIR, f"pdry_{nm}.png"))
    known, st = primary_state()
    # ---- counts
    lines = [f"primary gTileset_OrleansGeneral today: {st['tiles_used']}/512 tiles ({st['tiles_free']} free), "
             f"{512 - st['metatiles_free']}/512 metatile ids named ({st['metatiles_free']} free), palettes 0-5 colours "
             f"{st['palette_colours']} of 15 (none free)"]
    ground_tiles = [g[k] for k in ("marsh_C", "water_C", "grass", "dry", "red_earth")]
    from_ground = set(known)
    for im in ground_tiles:
        for t in tiles_of(im):
            from_ground.add(canon(t))
    count_rows = []
    for style, label, key, under, prefix in mc.GROUNDS:
        ims = list(corners[(style, label)].values())
        n, cols = new_tiles(ims, from_ground)
        pal = set(map(tuple, mb.CORE_PAL[1:] if style == "swamp" else mb.DRY_PAL[1:]))
        ground_cols = set(map(tuple, np.array(g[key].convert("RGB")).reshape(-1, 3)))
        outside = sorted(cols - pal - ground_cols)
        home = "primary (bdg_, like the face cells)" if prefix == "bdg" else ("map secondary blends (bk_) or primary as bd:" if style == "swamp" else "map secondary blends (bk_)")
        count_rows.append(f"{style} on {label:22s} 4 cells  {n:3d} new 8x8 tiles  {len(cols):2d} colours, outside the "
                          f"{'core green' if style == 'swamp' else 'dry'} palette + ground: {outside or 'none'}  -> {home}")
    pk = {nm: im for nm, im in pd.items()}
    tier_rows = []
    pdry_counts = {}
    for t, names in TIERS.items():
        n, cols = new_tiles([pk[nm] for nm in names], known)
        outside = sorted(cols - set(st["pal2"]))
        pdry_counts[t] = {"metatiles": len(names), "new_tiles": n, "colours": len(cols), "outside_pal2": outside}
        tier_rows.append(f"primary dry {t}: {len(names):2d} metatiles  {n:3d} new 8x8 tiles  {len(cols):2d} colours, all in primary "
                         f"palette 2: {'yes' if not outside else outside}  ({', '.join(names)})")
    json.dump({"_comment": "Primary-safe dry border set (border_corners_review.py): make_borders' dry edge / corner cells on dry:0_0, "
                           "recoloured into gTileset_OrleansGeneral palette 2 (P2 table). Not integrated; tiers = what a dry strict "
                           "band can draw with each subset.",
               "cells": {nm: f"pdry_{nm}.png" for nm in pd}, "recolour": {str(k): list(v) for k, v in P2.items()},
               "tiers": {t: list(v) for t, v in TIERS.items()}, "counts": pdry_counts,
               "primary": {k: v for k, v in st.items() if k != "pal2"}},
              open(os.path.join(PDRY_DIR, "pdry.json"), "w"), indent=1)
    # ---- the prototypes
    P = probe(["isle_marais", "route_16"])
    rim = load_render("proto_isle_marais_after.png")
    r16 = load_render("proto_route_16_after.png")
    im_after, im_pl, im_sk = place_corners("isle_marais", "swamp", P["isle_marais"], rim, g)
    r16_after, r_pl, r_sk = place_corners("route_16", "dry", P["route_16"], r16, g)
    mock, uses = band_mock(P["route_16"], r16_after, pd, g)
    for ln in lines + count_rows + tier_rows:
        print(" ", ln)
    print("  isle_marais: placed", len(im_pl), "skipped", im_sk)
    print("  route_16: placed", len(r_pl), "skipped", r_sk)
    print("  band mock uses", uses)
    # ---- the sheet
    F, FS = font(16), font(12)
    BG, FG, DIM = (24, 28, 36), (240, 240, 240), (170, 176, 188)
    pad = 16
    parts = []
    # 1. each new cell at 4x, with the bare ground for reference and a 3x3 context (the cell in its corner, at 4x)
    LM = 200
    rows = [(f"{s} on {lab}", corners[(s, lab)], g[k]) for s, lab, k, _, _ in mc.GROUNDS]
    RH = 270
    lab = Image.new("RGB", (LM + 5 * 72 + 24 + 2 * 10 * 16 + 8, len(rows) * RH + 8), BG)
    d = ImageDraw.Draw(lab)
    sheet_cells = mb.build()
    bcell = {n: sheet_cells[0].crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)) for n, (x, y) in sheet_cells[1].items()}
    for r, (title, cs, ground) in enumerate(rows):
        y0 = r * RH + 8
        d.text((4, y0 + 24), title, fill=FG, font=F)
        lab.paste(up(ground, 4), (LM, y0))
        d.text((LM, y0 + 68), "ground", fill=DIM, font=FS)
        for i, cn in enumerate(mb.OUTER_ORDER):
            lab.paste(up(cs[cn], 4), (LM + (i + 1) * 72, y0))
            d.text((LM + (i + 1) * 72, y0 + 68), cn, fill=DIM, font=FS)
        # context: a 2x2-block wall tongue with its four convex corners, at 2x
        style = "swamp" if title.startswith("swamp") else "dry"
        ctx = island(style, ground, g, bcell, sheet_cells[2])
        lab.paste(up(ctx, 2), (LM + 5 * 72 + 24, y0))
    parts.append(("1. The new OUTER corner cells at 4x (out_NW = the wall is NW of the cell), per ground; right: a 2x2-block "
                  "wall (a tongue off a north wall + a free 2x2 block) in that ground at 2x with its S/N/E/W faces, inner corners and the four new outer corners", [lab]))
    k4 = 4
    zoom = Image.new("RGB", (4 * (3 * 16 * k4 + 16), 2 * (2 * 3 * 16 * k4 + 40)), BG)
    dz = ImageDraw.Draw(zoom)
    picks = [("isle_marais", rim, im_after, im_pl), ("route_16", r16, r16_after, r_pl)]
    zi = 0
    for key, before, after, pl in picks:
        seen = set()
        for x, y, corner, under in pl:
            if corner in seen:
                continue
            seen.add(corner)
            bx, by = (x - 1 + MARGIN[0]) * 16, (y - 1 + MARGIN[1]) * 16
            col, row = zi % 4, zi // 4
            X, Y = col * (3 * 16 * k4 + 16), row * (2 * 3 * 16 * k4 + 40) + 4
            zoom.paste(up(before.crop((bx, by, bx + 48, by + 48)), k4), (X, Y + 26))
            zoom.paste(up(after.crop((bx, by, bx + 48, by + 48)), k4), (X, Y + 26 + 3 * 16 * k4 + 4))
            dz.text((X, Y - 2), f"{key} ({x},{y}) {corner}", fill=DIM, font=FS)
            dz.text((X, Y + 10), f"on {under[:24]}", fill=DIM, font=FS)
            zi += 1
    parts.append(("2a. One corner of each kind from the prototypes at 4x: the plain render (square notch) above, the new cell "
                  "baked on that cell's own ground below (centre cell of each crop)", [zoom]))
    parts.append(("2b. Isle Marais prototype at 2x with every outer corner placed (magenta boxes = the cells drawn; "
                  f"{len(im_pl)} placed" + (f", skipped: {im_sk}" if im_sk else "") + ")",
                  [boxes(up(im_after, 2), [(x, y) for x, y, _, _ in im_pl], 2)]))
    parts.append(("2c. The same, without the boxes", [up(im_after, 2)]))
    parts.append((f"2d. Route 16 prototype at 2x with every outer corner placed ({len(r_pl)} placed; skipped {len(r_sk)}: "
                  "the column-38 cells the pass lists are face cells it left plain in the 8-column east band, not corners)",
                  [boxes(up(r16_after, 2), [(x, y) for x, y, _, _ in r_pl], 2)]))
    # 3. the primary dry set
    labp = Image.new("RGB", (LM + 16 * 72, 2 * 96 + 8), BG)
    d = ImageDraw.Draw(labp)
    d.text((4, 24), "secondary dry", fill=FG, font=F)
    d.text((4, 44), "(original)", fill=DIM, font=FS)
    d.text((4, 96 + 24), "primary dry", fill=FG, font=F)
    d.text((4, 96 + 44), "(palette 2)", fill=DIM, font=FS)
    for i, (face, par) in enumerate(PDRY_FACES):
        nm = face + ("" if par is None else f"_{par}")
        orig = mb.outer_cell("dry", face, g["dry"], g)[0] if face in mb.OUTER else mb.edge_cell("dry", face, par, g["dry"], g)[0]
        labp.paste(up(orig, 4), (LM + i * 72, 8))
        labp.paste(up(pd[nm], 4), (LM + i * 72, 96 + 8))
        d.text((LM + i * 72, 96 + 74), nm, fill=DIM, font=FS)
    parts.append(("3a. The strict-band-safe dry set: make_borders' dry face / corner cells on sand, recoloured into primary "
                  "palette 2 (no new colour). Top: the secondary original; bottom: the primary version", [labp]))
    w16 = P["route_16"]["w"]
    cx0 = (w16 - 16 + MARGIN[0]) * 16
    crop = (cx0, 0, mock.width, mock.height)
    marks = [(x, y) for y in range(P["route_16"]["h"]) for x in range(w16 - 8, w16)
             if np.any(np.array(mock.crop(cell_box(x, y))) != np.array(r16_after.crop(cell_box(x, y))))]
    mb_ = boxes(up(mock, 2), marks, 2, (0, 220, 255)).crop(tuple(v * 2 for v in crop))
    parts.append(("3b. Route 16 east mock at 2x (the 8-column band to Route 17 = the rightmost 8 map columns). Left: today. "
                  "Right: the band's edge cells drawn with the primary dry set (cyan boxes; the band's wall at depth 0 and Route 16's own wall stepping down at its edge: tier T2 pieces " + ", ".join(
                      f"{k} x{v}" for k, v in sorted(uses.items())) + ")",
                  [up(r16_after, 2).crop(tuple(v * 2 for v in crop)), mb_]))
    z = 4
    zc = (cx0 + 6 * 16, 0, cx0 + 6 * 16 + 12 * 16, 10 * 16)
    parts.append(("3c. Its north-east corner at 4x: today / with the primary set (where the palette-2 scrub meets the "
                  "secondary border block the greens shift: see the notes)", [up(r16_after.crop(zc), z), up(mock.crop(zc), z)]))
    whole = recolour(mock)
    parts.append(("3d. Option B, for comparison: the WHOLE dry family recoloured into palette 2 (secondary block and edges "
                  "too), so band and non-band scrub match exactly; this changes the approved dry look", [up(whole.crop(zc), z)]))
    notes = lines + count_rows + tier_rows + [
        "corner cells: no parity variants (the wall is 2x2-aligned: out_NW sits at parity (0,0), out_NE (1,0), out_SW (0,1), out_SE (1,1)).",
        "where the corners live: named as borders.bake() names them, the swamp marsh / water and all dry corners are bk_ patches, i.e. "
        "per-map secondary blends, demand-driven (only the corner / ground pairs a map uses); swamp-on-grass corners are bdg_ and "
        "build.py routes bdg_ to the PRIMARY blends (each used one ~3 tiles; Isle Marais uses 1). Adding the marsh / water corners to "
        "borders.png as bd:swamp_out_* instead would put all 8 in the primary (the recipe's ^bd:swamp_ rule) for 24 tiles: not advised. "
        "A secondary corner may not stand in a strict band: the pass should leave such a cell plain (a notch) or use the primary dry set.",
        "primary dry set: every primary palette is full (90 slots, 82 distinct colours), so the dry scrub's own 15 colours cannot come "
        "in; the set is the same art recoloured into palette 2 (which already holds the sand). It joins the sand exactly but its greens "
        "are the sage core greens: where it meets the secondary dry_scrub border block / wall there is a visible hue step (3c). "
        "T1 needs the band's wall at depth 0 with Route 16's wall already down to depth 0 before the band; T2 also lets that wall "
        "step down at the band edge (as the prototype's does: the mock uses T2). Option B (3d) = recolour the whole dry family to "
        "palette 2, seamless, but it changes the approved dry look and the secondaries' dry art.",
        "feather.missing_corners also lists cells that are 4-adjacent to the wall but were popped from b.edge (strict band / seam): "
        "Route 16 (38,0) (38,1) (38,26) (38,27) are face / inner-corner cells, not outer corners.",
    ]
    width = max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in parts)
    height = sum(max(i.height for i in ims) + 22 * len(mb.wrap(t, 170)) + 2 * pad for t, ims in parts) + 60 + 22 * sum(
        len(mb.wrap(n, 150)) for n in notes)
    out = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(out)
    y = pad
    for title, ims in parts:
        for line in mb.wrap(title, 170):
            d.text((pad, y), line, fill=FG, font=F)
            y += 22
        y += 4
        x = pad
        for im in ims:
            out.paste(im, (x, y))
            x += im.width + pad
        y += max(i.height for i in ims) + pad
    d.text((pad, y), "4. Counts (8x8 tiles after flip dedupe; tiles the primary already draws, and plain ground tiles, are not new)",
           fill=FG, font=F)
    y += 26
    for n in notes:
        for line in mb.wrap(n, 150):
            d.text((pad, y), line, fill=DIM, font=F)
            y += 22
    path = os.path.join(REVIEW, "art_edge_corners.png")
    out.crop((0, 0, width, y + pad)).save(path)
    print("wrote", path, out.size)


def island(style, base, g, cell, blocks, W=10, H=8):
    """a 2x2-block wall tongue hanging from a north wall plus a free 2x2 block: every face, inner and outer corner"""
    wall = {(x, y) for x in range(W) for y in range(H) if y < 2 or (2 <= x < 4 and y < 4) or (6 <= x < 8 and 4 <= y < 6)}
    bname = "swamp_canopy" if style == "swamp" else "dry_scrub"
    im = Image.new("RGB", (W * 16, H * 16))
    for y in range(H):
        for x in range(W):
            if (x, y) in wall:
                c = cell[blocks[bname][y & 1][x & 1]]
            else:
                n, s, w_, e = (x, y - 1) in wall, (x, y + 1) in wall, (x - 1, y) in wall, (x + 1, y) in wall
                face = ("in_NW" if n and w_ else "in_NE" if n and e else "in_SW" if s and w_ else "in_SE" if s and e
                        else "S" if n else "N" if s else "E" if w_ else "W" if e else None)
                if face:
                    par = None if face.startswith("in_") else (x & 1 if face in "SN" else y & 1)
                    c = mb.edge_cell(style, face, par, base, g)[0]
                else:
                    oc = None
                    for dx, dy, nm in ((-1, -1, "out_NW"), (1, -1, "out_NE"), (-1, 1, "out_SW"), (1, 1, "out_SE")):
                        if (x + dx, y + dy) in wall:
                            oc = nm
                    c = mb.outer_cell(style, oc, base, g)[0] if oc else base
            im.paste(c, (x * 16, y * 16))
    return im


if __name__ == "__main__":
    main(sys.argv[1:])

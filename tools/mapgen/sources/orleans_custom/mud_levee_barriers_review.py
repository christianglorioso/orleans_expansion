"""Review sheet for the canopy-on-mud set, the levee end caps and the Surf-barrier props (2026-10-13).

usage (from the decomp root):  python tools/mapgen/sources/orleans_custom/mud_levee_barriers_review.py
writes tile_review/art_mud_levee_barriers.png (reads the art scripts in this folder, the prototype renders in tile_review/, and an
in-memory build of Storm's Edge; never writes game data).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_borders as mb  # noqa: E402
import make_border_mud as mud  # noqa: E402
import make_levee_caps as mlc  # noqa: E402
import make_water_barriers as wb  # noqa: E402
import border_corners_review as bcr  # noqa: E402

REVIEW = bcr.REVIEW
up = bcr.up
BG, FG, DIM = (24, 28, 36), (240, 240, 240), (170, 176, 188)


def label_row(items, k, F, FS, gap=16):
    """[(img, label)] side by side at k x with labels below"""
    w = sum(i.width * k + gap for i, _ in items) + gap
    h = max(i.height * k for i, _ in items) + 34
    out = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(out)
    x = gap
    for im, lab in items:
        out.paste(up(im, k), (x, 0))
        for i, line in enumerate(mb.wrap(lab, max(6, im.width * k // 7))[:2]):
            d.text((x, im.height * k + 3 + 13 * i), line, fill=DIM, font=FS)
        x += im.width * k + gap
    return out


def grid_lines(im, k, col=(255, 0, 255)):
    im = im.copy()
    d = ImageDraw.Draw(im)
    for x in range(0, im.width, 16 * k):
        d.line((x, 0, x, im.height), fill=col)
    for y in range(0, im.height, 16 * k):
        d.line((0, y, im.width, y), fill=col)
    return im


def tile_colours(imgs):
    worst = 0
    for im in imgs:
        a = np.array(im.convert("RGB"))
        for y in range(0, a.shape[0], 8):
            for x in range(0, a.shape[1], 8):
                worst = max(worst, len({tuple(p) for p in a[y:y + 8, x:x + 8].reshape(-1, 3)}))
    return worst


# ---------------------------------------------------------------- existing water props (from their source art)
def ekat_cell(x, y, w=1, h=1):
    im = Image.open(os.path.join(mb.ROOT, "tools/mapgen/sources/ekat_swamp/swamp_tiles.png")).convert("RGBA")
    c = im.crop((x * 16, y * 16, (x + w) * 16, (y + h) * 16))
    c = Image.eval(c, lambda v: (v >> 3) << 3)
    base = Image.new("RGBA", c.size, (96, 136, 136, 255))
    base.alpha_composite(c)
    return base.convert("RGB")


def overlay_on_water(path, x, y, w=1, h=1, water=None):
    im = Image.open(os.path.join(mb.ROOT, path)).convert("RGB").crop((x * 16, y * 16, (x + w) * 16, (y + h) * 16))
    a = np.array(im)
    key = np.all(a == (255, 0, 255), axis=-1)
    wa = np.array(water)
    out = a.copy()
    for yy in range(h):
        for xx in range(w):
            blk = key[yy * 16:yy * 16 + 16, xx * 16:xx * 16 + 16]
            out[yy * 16:yy * 16 + 16, xx * 16:xx * 16 + 16][blk] = wa[blk]
    return Image.fromarray(out)


def existing_props(water):
    lmk = "tools/mapgen/sources/orleans_custom/route_landmarks.png"
    bayou = [(ekat_cell(1, 14), "weeds1"), (ekat_cell(2, 14), "weeds2"), (ekat_cell(3, 14), "lily"),
             (ekat_cell(7, 14), "stump"), (ekat_cell(5, 14, 2, 1), "waterlog 2x1"), (ekat_cell(5, 12, 3, 1), "knees 3x1")]
    coast = [(overlay_on_water(lmk, 15, 7, 1, 2, water), "sunken piling 1x2"),
             (overlay_on_water("tools/mapgen/sources/orleans_custom/lands_end_art.png", 7, 21, 1, 1, water), "pile"),
             (overlay_on_water("tools/mapgen/sources/orleans_custom/camp.png", 15, 19, 1, 1, water), "mooring post"),
             (overlay_on_water("tools/mapgen/sources/orleans_custom/camp.png", 8, 19, 1, 1, water), "buoy"),
             (overlay_on_water(lmk, 6, 5, 1, 2, water), "channel buoy")]
    return bayou, coast


# ---------------------------------------------------------------- barrier-line mocks
def line_rows(W, seed):
    """a wandering row per column in 1..3 (cells in from the map's north edge), steps of at most one"""
    r, out = 2, []
    for x in range(W):
        h = mb._hash(x, 7, seed)
        if h < 0.28 and r > 1:
            r -= 1
        elif h > 0.72 and r < 3:
            r += 1
        out.append(r)
    return out


def barrier_mock(style, water, new, W=28, H=8, M=3):
    """open water W x H with M rows of the border beyond the north edge (also water); the barrier line 1-3 cells in"""
    img = Image.new("RGB", (W * 16, (H + M) * 16))
    for y in range(H + M):
        for x in range(W):
            img.paste(water, (x * 16, y * 16))
    rows = line_rows(W, 3 if style == "bayou" else 9)
    ek = {"w1": ekat_cell(1, 14), "w2": ekat_cell(2, 14), "lily": ekat_cell(3, 14), "stump": ekat_cell(7, 14)}
    lmk = "tools/mapgen/sources/orleans_custom/route_landmarks.png"
    pil = overlay_on_water(lmk, 15, 7, 1, 2, water)
    pile = overlay_on_water("tools/mapgen/sources/orleans_custom/lands_end_art.png", 7, 21, 1, 1, water)
    cat = Image.open(os.path.join(wb.OUT_DIR, "wp_cattails_00.png")).convert("RGBA")
    blocked = set()
    x = 0
    k = 0
    while x < W:
        r = rows[x] + M
        h = mb._hash(x, 11, 5 if style == "bayou" else 6)
        if style == "bayou":
            if x + 2 < W and rows[x] == rows[x + 1] == rows[x + 2] and h < 0.25:
                img.paste(ekat_cell(5, 12, 3, 1), (x * 16, r * 16))
                blocked |= {(x, r), (x + 1, r), (x + 2, r)}
                x += 3
                continue
            pick = ["knees_1a", "w2", "cattails", "knees_1b", "w1", "lily", "stump", "w2", "knees_1a", "cattails"][k % 10]
            k += 1
            if pick in ("knees_1a", "knees_1b"):
                img.paste(new[pick], (x * 16, r * 16))
            elif pick == "cattails":
                img.paste(new["cattails"].crop((0, 16, 16, 32)), (x * 16, r * 16))
                img.paste(cat, (x * 16, (r - 1) * 16), cat)
            else:
                img.paste(ek[pick], (x * 16, r * 16))
            blocked.add((x, r))
            x += 1
        else:
            if x + 1 < W and rows[x] == rows[x + 1] and h < 0.35:
                img.paste(new["rock_ledge"], (x * 16, r * 16))
                blocked |= {(x, r), (x + 1, r)}
                x += 2
                continue
            pick = ["rock_1a", "rock_1b", "pile", "rock_1b", "piling", "rock_1a"][k % 6]
            k += 1
            if pick == "pile":
                img.paste(pile, (x * 16, r * 16))
            elif pick == "piling":
                img.paste(pil, (x * 16, (r - 1) * 16))
            else:
                img.paste(new[pick], (x * 16, r * 16))
            blocked.add((x, r))
            x += 1
    return img, blocked, M


def edge_marked(img, M, k, blocked=None):
    im = up(img, k)
    d = ImageDraw.Draw(im)
    y = M * 16 * k
    for x in range(0, im.width, 8):
        d.line((x, y, x + 4, y), fill=(240, 208, 72), width=2)
    if blocked:
        for bx, by in blocked:
            d.rectangle((bx * 16 * k, by * 16 * k, (bx + 1) * 16 * k - 1, (by + 1) * 16 * k - 1), outline=(255, 64, 64))
    return im


def main(argv):
    F, FS = mb.font(16), mb.font(12)
    pad = 16
    parts, notes = [], []
    # ---------------- 1. canopy on mud
    cells, g = mud.build()
    sheet = mb.build()
    bcell = {n: sheet[0].crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)) for n, (x, y) in sheet[1].items()}
    items = [(g["mud_C"], "mud_C")] + [(im, f + ("" if p is None else f"_{p}")) for (f, p), im in cells.items()]
    parts.append(("1a. Swamp canopy onto mud (ekat:mud_C, the Isle Marais mud) at 4x: faces S/N/E/W both parities, inner corners, "
                  "outer corners. Files bk_swamp_<face><parity>_834ef142.png (the bake() names)", [label_row(items, 4, F, FS)]))
    isl = bcr.island("swamp", g["mud_C"], g, bcell, sheet[2])
    # a mud flat beside marsh: the wall over both, as a shoreline of mud meets it
    parts.append(("1b. A 2x2-block canopy wall (a tongue off a north wall + a free block) in mud at 3x, every new piece in place",
                  [up(isl, 3)]))
    mud_tiles = bcr.new_tiles(list(cells.values()), {bcr.canon(t) for t in bcr.tiles_of(g["mud_C"])})
    notes.append(f"canopy on mud: 16 cells, {mud_tiles[0]} new 8x8 tiles, {len(mud_tiles[1])} colours (core green + Ekat mud), "
                 f"at most {tile_colours(cells.values())} colours in any 8x8 tile; secondary (bk_) like the other baked edges.")
    notes.append("canopy on mud: feather.canon('swamp', ...) maps 'L' (mud) to '.' today, so the pass paints grass under an edge "
                 "cell on mud; keep 'L' / 'S' as mud there to use this set.")
    # ---------------- 2. levee caps
    proto = Image.open(os.path.join(REVIEW, "proto_storms_edge_after.png")).convert("RGB")
    proto = proto.resize((proto.width // 2, proto.height // 2), Image.NEAREST)
    win = lambda im: im.crop((16 * 16, 0, 38 * 16, 15 * 16))                  # map x 16-37 (+7 margin), rows 0-9 (+5)
    plain_im, *_ = mlc.storms_edge_mock(3, 1, caps=False)
    cap1, cells1, grid1, under1 = mlc.storms_edge_mock(3, 1, caps=True)
    cap0, cells0, *_ = mlc.storms_edge_mock(3, 0, caps=True)
    mw = lambda im: im.crop((13 * 16, 0, 39 * 16, 11 * 16))
    parts.append(("2a. Storm's Edge canal (2x): left, today's prototype (the canal runs into the north border); right, the canal "
                  "opening into a lake (the north edge receded, in-memory build), drawn by today's levee.render: a flat stone shelf "
                  "and a slope cut square at each head", [up(win(proto), 2), up(mw(plain_im), 2)]))
    parts.append(("2b. The same with the end caps (make_levee_caps.render_caps): left, JET 1 (each levee reaches one cell past "
                  "the meadow's shore: a rounded, stone-armoured nose); right, JET 0 (flush with the shore: the face turns the "
                  "corner onto the lake and fades into the meadow's bank)", [up(mw(cap1), 2), up(mw(cap0), 2)]))
    zw = lambda im, x0: im.crop((x0 * 16, 1 * 16, (x0 + 5) * 16, 6 * 16))
    parts.append(("2c. The four heads at 4x with the cell grid (JET 1: west, east; JET 0: west, east)",
                  [grid_lines(up(zw(cap1, 20), 4), 4), grid_lines(up(zw(cap1, 27), 4), 4),
                   grid_lines(up(zw(cap0, 20), 4), 4), grid_lines(up(zw(cap0, 27), 4), 4)]))
    import json
    idx = json.load(open(os.path.join(mlc.CAP_DIR, "caps.json")))["cells"]
    rows = []
    for jet in (1, 0):
        for side in ("W", "E"):
            its = []
            for nm, v in sorted(idx.items(), key=lambda kv: (kv[1]["offset_from_canal_side_head"][1], kv[1]["offset_from_canal_side_head"][0])):
                if v["jet"] == jet and v["side"] == side:
                    ov = Image.open(os.path.join(mlc.CAP_DIR, nm + ".png")).convert("RGBA")
                    cell = Image.new("RGBA", (16, 16), (255, 0, 255, 255))
                    cell.alpha_composite(ov)
                    dx, dy = v["offset_from_canal_side_head"]
                    its.append((cell.convert("RGB"), f"{dx:+d},{dy:+d}"))
            rows.append(label_row(its, 4, F, FS))
    parts.append(("2d. The cap cells as RGBA overlays at 4x (magenta = the ground shows through), offset (dx, dy) from the levee's "
                  "head cell on the canal side; rows: JET 1 west, JET 1 east, JET 0 west, JET 0 east (tilesets/levee/caps/)", rows[:2]))
    parts.append(("", rows[2:]))
    caps_cols = set()
    for nm in idx:
        a = np.array(Image.open(os.path.join(mlc.CAP_DIR, nm + ".png")).convert("RGBA"))
        caps_cols |= {tuple(int(v) for v in p[:3]) for p in a.reshape(-1, 4) if p[3]}
    lev_pal = set(mlc.levee.GRASS + mlc.levee.SLOPE) | {mlc.levee.WATER_C, mlc.levee.WATER_D, mlc.levee.EARTH, mlc.levee.EARTH_D,
                                                        mlc.levee.STONE_L, mlc.levee.STONE, mlc.levee.STONE_D, mlc.levee.OUTLINE,
                                                        mlc.levee.FOAM}
    notes.append(f"levee caps: {len(idx)} cells (JET 1: {sum(v['jet'] == 1 for v in idx.values())}, JET 0: "
                 f"{sum(v['jet'] == 0 for v in idx.values())}); colours {len(caps_cols)}, outside the levee palette: "
                 f"{sorted(caps_cols - lev_pal) or 'none'}. Each is an overlay over the ground named in caps.json, the way build.py's "
                 f"levee() stores its cells (lv_<sha1(overlay + under)>), so the rollout can hand them to compose unchanged or call "
                 f"render_caps in place of levee.render.")
    notes.append("levee caps: JET 1 is the recommended shape. With JET 0 the tileset's bank lip for the meadow (drawn in the water "
                 "cell north of the meadow) stands about half a cell proud of the levee's nose. The cypress / logs / pilings in the "
                 "lake in 2a-2c are placed by the surf-barrier pass now in feather.py (working tree), not by this art.")
    notes.append("levee caps: the lake shore here is a mock (rows 0-2 water, the meadow wandering back 1-3 rows beside the levees); "
                 "today the feather pass cannot recede that shore (the gym, paths and B cells hold it), which is the rollout's call.")
    # ---------------- 3. barrier props
    water = mb.ground_cells()["water_C"].convert("RGB")
    newp, _ = wb.build(water)
    bayou, coast = existing_props(water)
    parts.append(("3a. What exists (from the source art, on water_C, 4x). Bayou: also cypress_water 3x3, cypress_small_water 2x3, "
                  "snag_water 1x2. Coast/port: also shipwreck 4x3; boulder exists on grass only", [label_row(bayou, 4, F, FS),
                                                                                                   label_row(coast, 4, F, FS)]))
    parts.append(("3b. What is new (tilesets/water_props/, 4x): bayou single-cell knee clusters and a 1x2 cattail clump (its top "
                  "cell overhead); coast single-cell rocks awash and a 2x1 low ledge (levee riprap colours)",
                  [label_row([(newp["knees_1a"], "knees_1a"), (newp["knees_1b"], "knees_1b"), (newp["cattails"], "cattails 1x2")], 4, F, FS),
                   label_row([(newp["rock_1a"], "rock_1a"), (newp["rock_1b"], "rock_1b"), (newp["rock_ledge"], "rock_ledge 2x1")], 4, F, FS)]))
    mb_, blk_b, M = barrier_mock("bayou", water, newp)
    mc_, blk_c, _ = barrier_mock("coast", water, newp)
    parts.append(("3c. Barrier lines at 2x: open water, the map's north edge = the yellow dashes (3 border rows beyond), a line "
                  "wandering 1-3 cells in that a surfer cannot cross (4-way movement: diagonal steps still block). Bayou: knees, "
                  "reed tufts, weeds, lilies, a stump, cattails, a 3-knee run. Coast: rocks, ledges, pilings",
                  [edge_marked(mb_, M, 2), edge_marked(mc_, M, 2)]))
    parts.append(("3d. The same with the blocking cells boxed", [edge_marked(mb_, M, 2, blk_b), edge_marked(mc_, M, 2, blk_c)]))
    for name, (w, h, style, _, passable) in wb.PIECES.items():
        pass
    nb = bcr.new_tiles([newp[n] for n in ("knees_1a", "knees_1b", "cattails")], {bcr.canon(t) for t in bcr.tiles_of(water)})
    nc = bcr.new_tiles([newp[n] for n in ("rock_1a", "rock_1b", "rock_ledge")], {bcr.canon(t) for t in bcr.tiles_of(water)})
    notes.append(f"barrier props: bayou new 3 pieces / 4 metatiles, {nb[0]} new tiles, {len(nb[1])} colours (Ekat water, knee "
                 f"browns, reed greens); coast new 3 pieces / 4 metatiles, {nc[0]} new tiles, {len(nc[1])} colours (levee riprap + "
                 f"water); at most {tile_colours(newp.values())} colours in any 8x8 tile. Secondary art (props), not primary.")
    notes.append("barrier props existing: bayou water_weeds1/2, water_lily, waterstump, waterlog, knees, snag_water, "
                 "cypress_small_water, cypress_water; coast sunken_piling, pile (harbor), mooring_post / buoy (camp), channel_buoy, "
                 "shipwreck. Missing were single-cell knees, tall reeds in water, and any rock in water: drawn.")
    # ---------------- layout
    width = max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in parts)
    height = sum(max(i.height for i in ims) + 22 * len(mb.wrap(t, 170)) + 2 * pad for t, ims in parts) + 60 + 22 * sum(
        len(mb.wrap(n, 150)) for n in notes)
    out = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(out)
    y = pad
    for title, ims in parts:
        for line in (mb.wrap(title, 170) if title else []):
            d.text((pad, y), line, fill=FG, font=F)
            y += 22
        y += 4
        x = pad
        for im in ims:
            out.paste(im, (x, y))
            x += im.width + pad
        y += max(i.height for i in ims) + pad
    d.text((pad, y), "4. Counts and notes (8x8 tiles after flip dedupe; plain ground tiles are not new)", fill=FG, font=F)
    y += 26
    for n in notes:
        for line in mb.wrap(n, 150):
            d.text((pad, y), line, fill=DIM, font=F)
            y += 22
    path = os.path.join(REVIEW, "art_mud_levee_barriers.png")
    out.crop((0, 0, width, y + pad)).save(path)
    print("wrote", path, out.size)
    for n in notes:
        print(" ", n)


if __name__ == "__main__":
    main(sys.argv[1:])

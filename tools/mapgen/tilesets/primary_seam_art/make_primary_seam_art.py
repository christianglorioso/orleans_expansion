"""Primary-only seam-band art (seams review 2, specs A, B, D; C = the Battle Tower is on hold): pieces for gTileset_OrleansGeneral
that may stand in a seam band, where the engine draws a neighbour's cells with this map's tilesets (so only primary metatiles survive).

usage (from the decomp root):  python tools/mapgen/tilesets/primary_seam_art/make_primary_seam_art.py
writes, next to this script:
    primary_seam_art.png    16 px cells. Row 0: the two shared bottom layers (ekat:water_C, dry:0_0), copied from the built primary.
                            Row 1: the top layers (magenta = transparent: the bottom shows through). Row 2: pieces with their own bottom.
    primary_seam_art.json   every piece: spec, cells, layer type, behaviour, the primary palette each 8x8 tile fits, new-tile cost,
                            where it goes; the per-spec tile / metatile counts against today's primary
    sources/orleans_general.pss.json   the image source for tools/mapgen/tilesets/recipes/orleans_general.json (add it in
                            make_primary_recipe.py, which writes that recipe); the pieces land as pss:<id>
Nothing in data/ or the recipes is touched.

How the pieces stay cheap (the primary is full: 512 / 512 tiles before the seam agent's pruning):
  * Every piece is a top layer over a ground the primary already has (ekat:water_C, dry:0_0), layer type COVERED (both layers under
    the sprites), so the bottom costs no tile and the top only where the art is. A top layer over another ground (water_E, a bank,
    a lily cell) is a free extra metatile.
  * Colours: only colours the primary palettes already hold; each 8x8 tile inside one existing palette (fit_palette() proves it).
  * B  rocks awash and a cypress knee (art: tilesets/water_props/wp_rock_1a/1b, wp_knees_1a) recoloured into primary palette 2, the
       water palette (its stones are the warm greys of the in-map rocks; the foam becomes the palette's pale sage). The primary has no
       tile animation (gTileset_OrleansGeneral.callback = NULL): water_C is one flat colour, nothing to animate.
  * D  the Johto path (0D0-0E2 + the four inner corners) on dry ground: the Johto edge pieces are single-layer art whose kerb is the
       flat grass colour (palette 5 index 3); that index becomes transparent over dry:0_0, so the eight edges share 4 new tiles by
       flips and the inner corners take one each. Plus the kerb cell where the path (on grass) runs under a dry corner cell
       (dry:1_2 above it, Route 23 x 8): the kerb is grass or sand column by column, as that cell's bottom edge is.
  * A  the dry scrub (make_borders.py's dry_scrub block, its edge cells at both parities, inner and outer corners) as a top layer over
       dry:0_0: leaves, stones and straw in primary palette 4, the cast shadow on the sand dropped (no sand shade fits palette 4).
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, MAPGEN)
sys.path.insert(0, os.path.join(MAPGEN, "sources", "orleans_custom"))
import render  # noqa: E402

PRIM = os.path.join(ROOT, "data", "tilesets", "primary", "orleans_general")
SEC_DRY = os.path.join(ROOT, "data", "tilesets", "secondary", "orleans_route_dry")
PROPS = os.path.join(MAPGEN, "tilesets", "water_props")
KEY = (255, 0, 255)
SRC = "pss"
GRASS = (120, 160, 104)
WATER = (96, 136, 136)
SPEC_ORDER = ("B", "D", "A")   # priority after C (on hold): the cumulative counts follow it

# ---------------------------------------------------------------- the primary as built today
TS = render.Tilesets(PRIM, PRIM)
MT = open(os.path.join(PRIM, "metatiles.bin"), "rb").read()
AT = open(os.path.join(PRIM, "metatile_attributes.bin"), "rb").read()
NAMES = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]
PALS = [TS.pals[p] for p in range(6)]


def behaviour_names():
    src = open(os.path.join(ROOT, "include", "constants", "metatile_behaviors.h")).read()
    body = src[src.index("{") + 1:src.index("}")]
    names = [l.split("//")[0].strip().rstrip(",").split("=")[0].strip() for l in body.splitlines()]
    return {i: n for i, n in enumerate(n for n in names if n.startswith("MB_"))}


BEH = behaviour_names()


def entries(mid):
    return struct.unpack_from("<8H", MT, mid * 16)


def attr(mid):
    return struct.unpack_from("<H", AT, mid * 2)[0]


def quad_rgba(e, top):
    """one 8x8 tile entry of a metatile as an RGBA array (top layer: index 0 transparent)"""
    tid, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
    t = np.array(TS.ptiles[tid], dtype=np.uint8).reshape(8, 8)
    if hf:
        t = t[:, ::-1]
    if vf:
        t = t[::-1]
    rgb = np.array(TS.pals[pal], dtype=np.uint8)[t]
    a = np.full((8, 8, 1), 255, np.uint8)
    if top:
        a[t == 0] = 0
    return np.concatenate([rgb, a], axis=2)


def layer_rgba(name, layer):
    """a primary metatile's layer as a 16x16 RGBA image (bottom: opaque)"""
    e = entries(NAMES[name])
    out = np.zeros((16, 16, 4), np.uint8)
    for q in range(4):
        out[(q // 2) * 8:(q // 2) * 8 + 8, (q % 2) * 8:(q % 2) * 8 + 8] = quad_rgba(e[layer * 4 + q], layer == 1)
    return Image.fromarray(out, "RGBA")


def full_rgb(name):
    return TS.metatile(NAMES[name]).convert("RGB")


def canon(a):
    """an 8x8 RGBA tile, flip-invariant key (transparent pixels all equal)"""
    a = a.copy()
    a[a[..., 3] == 0] = 0
    return min(x.tobytes() for x in (a, a[:, ::-1], a[::-1], a[::-1, ::-1]))


def known_tiles():
    """every 8x8 tile the primary draws today, as (layer-aware) RGBA keys"""
    k = set()
    for mid in range(len(MT) // 16):
        e = entries(mid)
        if not any(e):
            continue
        for i, v in enumerate(e):
            if i >= 4 and v == 0:
                continue
            if (v & 0x3FF) < len(TS.ptiles):
                k.add(canon(quad_rgba(v, i >= 4)))
    return k


def quads(im):
    a = np.array(im.convert("RGBA"))
    return [a[y:y + 8, x:x + 8] for y in (0, 8) for x in (0, 8)]


def fit_palette(q, top, prefer=()):
    """the primary palette (0-5) an 8x8 RGBA tile fits: opaque colours in slots 1-15 (a bottom tile may also use slot 0, the
    backdrop grass); None if it fits none"""
    cols = {tuple(int(v) for v in p[:3]) for p in q.reshape(-1, 4) if p[3]}
    order = list(prefer) + [p for p in range(6) if p not in prefer]
    for p in order:
        have = set(PALS[p][1:]) | (set() if top else {PALS[p][0]})
        if cols <= have:
            return p
    return None


# ---------------------------------------------------------------- colour helpers
def dist(a, b):
    r = (a[0] + b[0]) / 2
    return ((2 + r / 256) * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + (2 + (255 - r) / 256) * (a[2] - b[2]) ** 2) ** .5


def nearest(c, pal):
    return min(pal[1:], key=lambda p: dist(p, c))


def recolour(img, table):
    a = np.array(img.convert("RGBA"))
    out = a.copy()
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x, 3]:
                c = tuple(int(v) for v in a[y, x, :3])
                out[y, x, :3] = table[c]
    return Image.fromarray(out, "RGBA")


def clear(img, colours):
    """pixels of the given colours become transparent"""
    a = np.array(img.convert("RGBA"))
    for c in colours:
        a[np.all(a[..., :3] == c, axis=-1), 3] = 0
    return Image.fromarray(a, "RGBA")


def over(bottom, top):
    b = bottom.convert("RGBA").copy()
    b.alpha_composite(top.convert("RGBA"))
    return b.convert("RGB")


# ---------------------------------------------------------------- B: Surf blockers on water
# wp_rock / wp_knees colours -> primary palette 2 (the water palette: water, the dark-water ring, warm stone greys)
B_TABLE = {
    (144, 136, 128): (160, 136, 120), (104, 100, 96): (104, 88, 80), (104, 96, 96): (104, 88, 80), (80, 80, 80): (88, 72, 72),
    (184, 176, 160): (144, 184, 152), (200, 224, 224): (144, 184, 152), (72, 112, 112): (80, 112, 104), WATER: WATER,
    (48, 48, 40): (40, 56, 40), (104, 96, 88): (104, 88, 80), (136, 120, 104): (136, 112, 96), (160, 144, 120): (160, 136, 120),
}


def spec_b():
    out = []
    for nm, src, use in (("rock_a", "wp_rock_1a", "rock awash (wp_rock_a's art)"),
                         ("rock_b", "wp_rock_1b", "rock awash (wp_rock_b's art)"),
                         ("knee", "wp_knees_1a", "cypress knee cluster (wp_knees_a's art)")):
        im = Image.open(os.path.join(PROPS, src + ".png")).convert("RGBA")
        top = clear(recolour(im, B_TABLE), [WATER])   # open water stays the bottom's water_C
        out.append(dict(id=f"w_{nm}", spec="B", base="ekat:water_C", top=top, layer="covered",
                        behavior=BEH[attr(NAMES["ekat:water_C"]) & 0xFF], prefer=(2,),
                        use=f"{use} on open water; blocking (collision 1 in the map). Same top over any other water cell "
                            "(water_E/W/S, lily, mudwater) is a free extra metatile: base + this top"))
    return out


# ---------------------------------------------------------------- D: the Johto path on dry ground
PATH_EDGES = {"NW": "johto:0D0", "N": "johto:0D1", "NE": "johto:0D2", "W": "johto:0D8", "E": "johto:0DA",
              "SW": "johto:0E0", "S": "johto:0E1", "SE": "johto:0E2"}
PATH_INNER = {"iNW": "patch:path_iNW", "iNE": "patch:path_iNE", "iSW": "patch:path_iSW", "iSE": "patch:path_iSE"}


def dry_cell(name):
    """a dry-country secondary metatile (orleans_route_dry, built) as RGB"""
    ts = render.Tilesets(PRIM, SEC_DRY)
    m = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_route_dry.mapping.json")))["metatiles"]
    return ts.metatile(m[name]).convert("RGB")


def spec_d():
    out = []
    for k, src in PATH_EDGES.items():
        # the edge pieces are one opaque top layer (their bottom is hidden); the kerb is the flat grass (pal 5 index 3)
        top = clear(layer_rgba(src, 1), [GRASS])
        out.append(dict(id=f"pd_{k}", spec="D", base="dry:0_0", top=top, layer="covered", behavior="MB_NORMAL", prefer=(5,),
                        use=f"Johto path {k} edge on dry ground (replaces {src} where the kerb's outside is dry:0_0)"))
    for k, src in PATH_INNER.items():
        top = clear(layer_rgba(src, 0), [GRASS])   # the inner corners are single-layer: the grass bite becomes sand
        out.append(dict(id=f"pd_{k}", spec="D", base="dry:0_0", top=top, layer="covered", behavior="MB_NORMAL", prefer=(5,),
                        use=f"Johto path inner corner {k} with a dry-ground bite (replaces {src})"))
    # the path crossing the meadow / dry bank (Route 23, x 8): the dry patch's corner cell beside the path (dry:1_2 = landSE above the
    # path: sand only in its bottom-right) meets the kerb with half its bottom edge sand. The kerb continues that cell's edge straight
    # through: per column, its outermost row decides grass (kept, with the bank's rim colour) or sand (transparent: dry:0_0 shows).
    pal5 = PALS[5]
    for k, src, nb, row in (("N", "johto:0D1", "dry:1_2", 15),):
        edge = np.array(dry_cell(nb))[row]
        a = np.array(layer_rgba(src, 1))
        for y in range(16):
            for x in range(16):
                if tuple(a[y, x, :3]) != GRASS or a[y, x, 3] == 0:
                    continue
                c = tuple(int(v) for v in edge[x])
                if c in ((224, 200, 144), (200, 168, 112), (248, 232, 184), (240, 224, 184), (216, 184, 88)):
                    a[y, x, 3] = 0              # sand side of the bank
                else:
                    a[y, x, :3] = c if c in pal5 else nearest(c, pal5)   # grass side and the bank's rim
        out.append(dict(id=f"pd_{k}_by_{nb.replace(':', '')}", spec="D", base="dry:0_0", top=Image.fromarray(a, "RGBA"),
                        layer="covered", behavior="MB_NORMAL", prefer=(5,),
                        use=f"Johto path (on grass) {k} edge whose outside neighbour is the dry corner cell {nb}: the kerb is grass "
                            f"where {nb}'s facing edge is grass and dry ground where it is sand (Route 23 x 8, rows 12 and 34)"))
    return out


# ---------------------------------------------------------------- A: the dry scrub over dry ground
# leaves / stones / straw / the cast shade on the sand -> primary palette 4 (the foliage palette), by role and lightness
# (chosen against bd:dry_scrub side by side: the closest values; palette 4's greens are bluer than the dry set's olives)
A_LADDER = {"L0": (16, 48, 32), "L1": (64, 80, 72), "L2": (88, 120, 72), "L3": (64, 128, 72), "L4": (120, 176, 112),
            "ST": (232, 200, 120), "ST_D": (200, 176, 120), "K0": (104, 88, 88), "K1": (144, 160, 144), "K2": (200, 200, 184),
            "B0": (64, 56, 48), "D2": (200, 176, 120), "D3": (200, 176, 120)}


def spec_a(ladder=None):
    import make_borders as mb
    ladder = dict(A_LADDER, **(ladder or {}))
    g = mb.ground_cells()
    sand = g["dry"]   # make_dry_country's dry[0]: the same pixel pattern as the primary's dry:0_0
    table = {getattr(mb, k): v for k, v in ladder.items()}
    table[mb.D1] = ladder["D2"]   # (a shaded highlight)

    def split(img, base):
        """the art over `base` -> a top layer: pixels still equal to the bare ground are transparent (dry:0_0 shows); the
        rest (crowns, stones, straw and the crowns' cast shade on the sand) in palette 4"""
        a = np.array(img.convert("RGB"))
        b = np.array(base.convert("RGB"))
        out = np.zeros((16, 16, 4), np.uint8)
        for y in range(16):
            for x in range(16):
                if (a[y, x] == b[y, x]).all():
                    continue
                c = tuple(int(v) for v in a[y, x])
                out[y, x, :3] = table.get(c, nearest(c, PALS[4]))
                out[y, x, 3] = 255
        return Image.fromarray(out, "RGBA")
    out = []
    # tiers (cost counted in this order): A1 the S / N faces, enough for a band whose wall is the border itself (depth 0) along a
    # north / south edge; A2 + the E / W faces and the inner and outer corners, for the map's own wall stepping down to depth 0 where
    # the band starts (and the band's corner); A3 + the block, so the wall itself may run inward inside a band
    for face, par in mb.FACE_ORDER:
        nm = face + ("" if par is None else f"_{par}")
        img = mb.edge_cell("dry", face, par, sand, g)[0]
        out.append(dict(id=f"sc_{nm}", spec="A", tier="A1" if face in ("S", "N") else "A2", base="dry:0_0", top=split(img, sand),
                        layer="covered", behavior="MB_NORMAL", prefer=(4,),
                        use=f"dry scrub wall edge {nm} on dry ground (= bd:dry_{face}_dry" + ("" if par is None else f"_{par}") + ")"))
    for corner in mb.OUTER_ORDER:
        img = mb.outer_cell("dry", corner, sand, g)[0]
        out.append(dict(id=f"sc_{corner}", spec="A", tier="A2", base="dry:0_0", top=split(img, sand), layer="covered",
                        behavior="MB_NORMAL", prefer=(4,), use=f"dry scrub outer corner {corner} on dry ground"))
    blk = mb.block("dry", g)
    for by in range(2):
        for bx in range(2):
            cell = blk.crop((bx * 16, by * 16, bx * 16 + 16, by * 16 + 16))
            out.append(dict(id=f"sc_block_{bx}{by}", spec="A", tier="A3", base="dry:0_0", top=split(cell, sand), layer="covered",
                            behavior="MB_NORMAL", prefer=(4,),
                            use=f"dry scrub wall / border block cell ({bx},{by}) = bd:dry_scrub_{bx}{by}; blocking"))
    return out


# ---------------------------------------------------------------- assemble
def pieces():
    return spec_b() + spec_d() + spec_a()


def cost(ps, known):
    """new 8x8 tiles per piece (flip dedupe against today's primary and the pieces before it), palette per quadrant"""
    seen = set(known)
    for p in ps:
        n, fits = 0, []
        for q in quads(p["top"]):
            if not q[..., 3].any():
                fits.append(None)       # empty top quadrant: the blank tile
                continue
            pal = fit_palette(q, True, p.get("prefer", ()))
            if pal is None:
                bad = {tuple(int(v) for v in c[:3]) for c in q.reshape(-1, 4) if c[3]}
                raise SystemExit(f"{p['id']}: a top tile fits no primary palette: {sorted(bad)}")
            fits.append(pal)
            k = canon(q)
            if k not in seen:
                seen.add(k)
                n += 1
        p["new_tiles"], p["palettes"] = n, fits
    return ps


def main():
    known = known_tiles()
    ps = cost(pieces(), known)
    bases = ["ekat:water_C", "dry:0_0"]
    for b in bases:
        if b not in NAMES:
            raise SystemExit(f"{b} is not in the primary")
    sheet = Image.new("RGB", (16 * max(len(ps), len(bases)), 32), KEY)
    for i, b in enumerate(bases):
        sheet.paste(full_rgb(b), (i * 16, 0))
    for i, p in enumerate(ps):
        t = Image.new("RGBA", (16, 16), KEY + (255,))
        t.alpha_composite(p["top"])
        sheet.paste(t.convert("RGB"), (i * 16, 16))
        p["cell"] = [i, 1]
    sheet.save(os.path.join(HERE, "primary_seam_art.png"))
    counts = {}
    for s in SPEC_ORDER:
        sp = [p for p in ps if p["spec"] == s]
        counts[s] = {"metatiles": len(sp), "new_tiles": sum(p["new_tiles"] for p in sp)}
    for t in ("A1", "A2", "A3"):
        sp = [p for p in ps if p.get("tier") == t]
        counts[t] = {"metatiles": len(sp), "new_tiles": sum(p["new_tiles"] for p in sp)}
    run = 0
    for s in SPEC_ORDER:
        run += counts[s]["new_tiles"]
        counts[s]["cumulative_tiles"] = run
    meta = {
        "_comment": "Primary-only seam-band pieces (make_primary_seam_art.py; seams2 specs A, B, D). Each piece = the named primary "
                    "ground as the bottom layer + the top cell here (layer type covered, under the sprites). 'palettes' = the "
                    "primary palette each top 8x8 tile fits (null = empty quadrant). new_tiles = 8x8 tiles not already in "
                    "gTileset_OrleansGeneral (flip dedupe, counted in spec order B, D, A). Not integrated.",
        "png": "primary_seam_art.png", "tileset": "gTileset_OrleansGeneral", "source": SRC,
        "bases": {b: [i, 0] for i, b in enumerate(bases)},
        "counts": counts,
        "pieces": {p["id"]: {"spec": p["spec"], "tier": p.get("tier", p["spec"]), "metatile": f"{SRC}:{p['id']}", "bottom": p["base"], "top_cell": p["cell"],
                             "layer": p["layer"], "behavior": p["behavior"], "palettes": p["palettes"],
                             "new_tiles": p["new_tiles"], "use": p["use"]} for p in ps},
    }
    with open(os.path.join(HERE, "primary_seam_art.json"), "w", newline="\n") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    src = {"_comment": "Add to the 'sources' of tools/mapgen/tilesets/recipes/orleans_general.json (through make_primary_recipe.py, "
                       "which writes that recipe), then compose; the pieces land as pss:<id>. Bottom = the primary's own water_C / "
                       "dry:0_0 cell (row 0, identical pixels, so no new tiles); top = row 1, magenta transparent.",
           "name": SRC, "type": "image", "image": "tools/mapgen/tilesets/primary_seam_art/primary_seam_art.png",
           "transparent": [list(KEY)],
           "metatiles": [{"id": p["id"], "bottom": meta["bases"][p["base"]], "top": p["cell"], "layer": p["layer"],
                          "behavior": p["behavior"]} for p in ps]}
    os.makedirs(os.path.join(HERE, "sources"), exist_ok=True)
    with open(os.path.join(HERE, "sources", "orleans_general.pss.json"), "w", newline="\n") as f:
        json.dump(src, f, indent=1)
        f.write("\n")
    used = len({(e & 0x3FF) for mid in range(len(MT) // 16) for e in entries(mid)[:4] if any(entries(mid))}
               | {(e & 0x3FF) for mid in range(len(MT) // 16) for e in entries(mid)[4:] if e})
    print(f"primary today: {len(TS.ptiles)} tiles in tiles.png, {used} referenced; {len(MT) // 16} metatiles")
    for s in SPEC_ORDER:
        c = counts[s]
        print(f"  spec {s}: {c['metatiles']:2d} metatiles, {c['new_tiles']:3d} new tiles (cumulative {c['cumulative_tiles']})")
    for t in ("A1", "A2", "A3"):
        print(f"    tier {t}: {counts[t]['metatiles']:2d} metatiles, {counts[t]['new_tiles']:3d} new tiles")
    for p in ps:
        print(f"    {p['id']:14s} {p['new_tiles']} new  palettes {p['palettes']}")


if __name__ == "__main__":
    main()

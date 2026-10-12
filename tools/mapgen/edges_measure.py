"""Edges pass, step B: measure the primary.  Read-only on game data.

usage (from the decomp root):  python tools/mapgen/edges_measure.py

For every Orleans outdoor map: which metatiles (by source piece name, tilesets/*.mapping.json) sit in the seam bands (the cells
within the camera's reach of every connected edge: N/S 5 rows, W/E 7 columns, on this side of the join; the neighbour's side is its
own map's band) and in the margin of every unconnected edge (what its border block has to continue).  Groups them into a terrain
vocabulary and prices that vocabulary in 8x8 tiles and palette colours against what gTileset_OrleansGeneral (the shared primary)
has room for.  Writes tools/mapgen/maps/00_edges_measure_data.md (all generated numbers; the written analysis in
00_edges_measure.md is authored on top of it).
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
import gba_view as gv  # noqa: E402

ROOT = world.ROOT
OUT = os.path.join(world.MAPS, "00_edges_measure_data.md")


# ---------------------------------------------------------------- names and classes
def load_mapping(tileset_const):
    n = gv.snake(tileset_const)
    p = os.path.join(HERE, "tilesets", n + ".mapping.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    inv = {}
    for k, v in d["metatiles"].items():
        inv.setdefault(v, k)
    return inv


def colour_class(im):
    r, g, b = im.crop((4, 4, 12, 12)).resize((1, 1)).getpixel((0, 0))
    if b > r + 25 and b >= g - 4:
        return "water"
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    if g >= r - 3 and g > b + 10:
        return "tree/dark green" if lum < 115 else "grass"
    if r >= g >= b and r - b > 25:
        return "ground/path"
    return "other"


RULES = [
    (r"^ekat:grass", "grass"),
    (r"^ekat:tallgrass", "tall grass"),
    (r"^ekat:marshwater", "marsh-water bank"),
    (r"^ekat:mudwater", "mud-water bank"),
    (r"^ekat:marsh", "marsh"),
    (r"^ekat:mud", "mud"),
    (r"^ekat:water|^ekat:waterlog|^ekat:waterstump|^ekat:snag", "water"),
    (r"^patch:cypress|^patch:reeds|cypress", "tree (cypress)"),
    (r"^patch:(path|ap_)", "path / paving"),
    (r"pier|ovl_brg|walk_|dock|boat|plank", "pier / bridge / boat"),
    (r"^dry:", "dry country"),
    (r"^patch:blend", "blend (3-way transition)"),
    (r"shady|barn|brick|church|^patch:pc|^patch:mart|vgen|ct_|lv_|labkit|supply|stage|pcw|^patch:fl|shrine|^rk:|^cv:|^cw:|^sp:", "building / town art"),
    (r"ovl_mag|magnolia", "tree (magnolia)"),
    (r"^patch:ovl|^patch:", "prop / overlay"),
]


def classify(name, im):
    if name is None:
        return "primary/unnamed: " + colour_class(im)
    if name.startswith("johto:"):
        return "primary johto: " + colour_class(im)
    for pat, cat in RULES:
        if re.search(pat, name):
            # an overlay on a base terrain: keep the base, mark the prop
            if cat in ("prop / overlay", "tree (cypress)", "pier / bridge / boat") and re.search(r"__ekat_(\w+?)_", name):
                pass
            return cat
    return "other: " + name.split(":")[0]


def base_of(name):
    """terrain under an overlay/patch name, when the name says (patch:ovl_..__ekat_water_C__..., cypress_10_marsh)"""
    if name is None:
        return None
    m = re.search(r"__ekat_(\w+?)_[A-Za-z]+(__|$)", name)
    if m:
        return m.group(1)
    m = re.search(r"_(marsh|water|mud)$", name)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------- tiles
def tile_key(ts, tid, hf, vf, pal):
    """canonical 8x8 tile (resolved colours, minimal over flips) and its colour set"""
    t = ts.tile(tid)
    if t is None:
        return None, frozenset()
    rows = [[None if t[y * 8 + x] == 0 else ts.pals[pal][t[y * 8 + x]] for x in range(8)] for y in range(8)]
    variants = []
    for fh in (0, 1):
        for fv in (0, 1):
            r = rows[::-1] if fv else rows
            r = [row[::-1] for row in r] if fh else r
            variants.append(tuple(tuple(row) for row in r))
    key = min(variants, key=lambda v: repr(v))
    cols = frozenset(c for row in key for c in row if c is not None)
    return key, cols


def metatile_tiles(ts, mid):
    m = ts.pmeta[mid] if mid < 512 else (ts.smeta[mid - 512] if mid - 512 < len(ts.smeta) else None)
    if m is None:
        return []
    out = []
    for e in m:
        tid, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        out.append((tid, hf, vf, pal))
    return out



FAMILIES = [
    # (label, tileset stem to read it from, regex over mapping names)
    ("grass", "route_1", r"^ekat:grass"),
    ("marsh (autotile set + plants)", "route_1", r"^ekat:marsh_"),
    ("water (autotile set, no logs)", "route_1", r"^ekat:water_"),
    ("marsh-water bank set", "route_1", r"^ekat:marshwater_"),
    ("tall grass", "route_1", r"^ekat:tallgrass"),
    ("mud set", "route_1", r"^ekat:mud_"),
    ("mud-water bank set", "route_1", r"^ekat:mudwater_"),
    ("cypress canopy on marsh/water (all pieces)", "route_1", r"^patch:cypress"),
    ("dry country set (dry:*)", "route_16", r"^dry:"),
]


def family_tiles(wd, stem, pattern):
    ts = wd.ts(stem)
    sec = wd.maps.info[stem]["layout"]["secondary_tileset"]
    names = load_mapping(sec)
    mids = [mid for mid, nm in names.items() if re.search(pattern, nm)]
    keys, pals = {}, set()
    for mid in mids:
        for tid, hf, vf, pal in metatile_tiles(ts, mid):
            k, c = tile_key(ts, tid, hf, vf, pal)
            if k is None:
                continue
            keys[k] = c
            if tid >= 512:
                pals.add(pal)
    return mids, keys, pals


def greedy_pack(sets, npal=6, cap=15):
    pals = [set() for _ in range(npal)]
    unfit = []
    for c in sorted(sets, key=lambda c: -len(c)):
        best, bs = None, None
        for i, p in enumerate(pals):
            add = len(c - p)
            if len(p) + add <= cap:
                sc = (len(c & p), -add)
                if bs is None or sc > bs:
                    best, bs = i, sc
        if best is None:
            unfit.append(c)
        else:
            pals[best] |= c
    return pals, unfit


def vocab_section(wd, L, pts, used_pri):
    # what the primary has to keep
    keep_tiles = set()
    for mid in used_pri:
        for tid, hf, vf, pal in metatile_tiles(pts, mid):
            if tid < 512:
                keep_tiles.add(tid)
    sec_refs = set()
    seen = set()
    for stem in world.OUTDOOR:
        sec = wd.maps.info[stem]["layout"]["secondary_tileset"]
        if sec in seen:
            continue
        seen.add(sec)
        ts = wd.ts(stem)
        for j in range(len(ts.smeta)):
            for tid, hf, vf, pal in metatile_tiles(ts, 512 + j):
                if tid < 512:
                    sec_refs.add(tid)
    keep_tiles |= sec_refs
    keep_keys = {}
    for tid in keep_tiles:
        # resolve with the palette(s) the tile is used with (first found)
        pass
    for mid in range(len(pts.pmeta)):
        for tid, hf, vf, pal in metatile_tiles(pts, mid):
            if tid in keep_tiles and tid < 512 and mid in used_pri:
                k, c = tile_key(pts, tid, hf, vf, pal)
                if k is not None:
                    keep_keys[k] = c
    for stem in world.OUTDOOR:           # tiles the secondaries borrow from the primary
        ts = wd.ts(stem)
        for j in range(len(ts.smeta)):
            for tid, hf, vf, pal in metatile_tiles(ts, 512 + j):
                if tid < 512 and pal < 6:
                    k, c = tile_key(ts, tid, hf, vf, pal)
                    if k is not None:
                        keep_keys[k] = c
    L.append("## What the primary must keep, and what a shared vocabulary would cost\n")
    L.append(f"- Outdoor maps use {len(used_pri)} primary metatiles; with the primary tiles the secondaries borrow, the primary has to keep {len(keep_tiles)} of its {len(pts.ptiles)} tiles "
             f"({len({k for k in keep_keys})} unique after flip/colour dedupe). Free now: {512 - len(pts.ptiles)} tiles; free if everything unused is pruned: {512 - len(keep_tiles)}.")
    kp, kunfit = greedy_pack(list(keep_keys.values()))
    L.append(f"- Those kept tiles alone need {sum(len(p) for p in kp)} palette colours of the 6 x 15 = 90 slots (greedy packing; {len(kunfit)} tiles unplaced).")
    L.append("")
    L.append("| vocabulary family | metatiles | unique 8x8 tiles | colours | secondary palettes it uses |")
    L.append("|---|---|---|---|---|")
    fam_data = {}
    for label, stem, pat in FAMILIES:
        mids, keys, pals = family_tiles(wd, stem, pat)
        cols = set().union(*keys.values()) if keys else set()
        fam_data[label] = (keys, cols)
        L.append(f"| {label} | {len(mids)} | {len(keys)} | {len(cols)} | {sorted(pals)} |")
    L.append("")

    def combo(labels):
        keys = {}
        for l in labels:
            keys.update(fam_data[l][0])
        # tiles already in the kept primary set cost nothing
        new = {k: c for k, c in keys.items() if k not in keep_keys}
        cols = set().union(*new.values()) if new else set()
        pals, unfit = greedy_pack(list(keep_keys.values()) + list(new.values()))
        return len(keys), len(new), len(cols), sum(len(p) for p in pals), len(unfit)

    core = ["grass", "marsh (autotile set + plants)", "water (autotile set, no logs)", "marsh-water bank set", "tall grass"]
    L.append("| shared set | unique tiles | new tiles (not already kept) | new colours | colours in 6 palettes after packing | tiles unplaced |")
    L.append("|---|---|---|---|---|---|")
    sets = [("core green: grass + marsh + water + marsh-water bank + tall grass", core),
            ("core + mud + mud-water bank", core + ["mud set", "mud-water bank set"]),
            ("core + cypress canopy", core + ["cypress canopy on marsh/water (all pieces)"]),
            ("core + mud sets + cypress", core + ["mud set", "mud-water bank set", "cypress canopy on marsh/water (all pieces)"]),
            ("dry country alone", ["dry country set (dry:*)"]),
            ("core + dry country", core + ["dry country set (dry:*)"]),
            ("core + cypress + dry country", core + ["cypress canopy on marsh/water (all pieces)", "dry country set (dry:*)"]),
            ("everything above", [l for l, _s, _p in FAMILIES])]
    for name, labels in sets:
        t, n, c, packed, unf = combo(labels)
        L.append(f"| {name} | {t} | {n} | {c} | {packed} | {unf} |")
    L.append("")
    L.append(f"Budget: {512 - len(pts.ptiles)} free tiles now, {512 - len(keep_tiles)} after pruning to the kept set; palette slots 90, the kept set takes {sum(len(p) for p in kp)}.\n")


def mismatch_section(wd, L, klass, tiles_of, mm_cells, pts, used_pri):
    """the joins that really garble: the two maps have different secondary tilesets"""
    rows = []
    for a, d, b, k, note in world.WORLD:
        sa = wd.maps.info[a]["layout"]["secondary_tileset"]
        sb = wd.maps.info[b]["layout"]["secondary_tileset"]
        rows.append((a, d, b, sa, sb, sa != sb))
    nm = sum(1 for r in rows if r[5])
    L.append("## Which joins garble at all\n")
    L.append(f"A join only garbles when the two maps have DIFFERENT secondary tilesets (a neighbour's ids then index the wrong table). "
             f"Of the {len(rows)} joins in world.py, {len(rows) - nm} join maps that share a secondary (nothing to fix) and {nm} do not:\n")
    L.append("| join | secondary A | secondary B |")
    L.append("|---|---|---|")
    for a, d, b, sa, sb, mism in rows:
        if mism:
            L.append(f"| {a} {d} {b} | {sa.replace('gTileset_', '')} | {sb.replace('gTileset_', '')} |")
    L.append("")
    tot = sum(mm_cells.values())
    cc = Counter()
    names = Counter()
    rep = {}
    for (sec, mid), n in mm_cells.items():
        c, nme = klass(sec, mid)
        cc[c] += n
        key = nme or f"{sec}:{mid}"
        if mid >= 512:
            names[key] += n
            rep.setdefault(key, (sec, mid))
    L.append(f"### Vocabulary of the garbling bands only ({tot} cells, own side of each mismatched join)\n")
    L.append("| terrain class | cells | share |")
    L.append("|---|---|---|")
    for c, n in cc.most_common():
        L.append(f"| {c} | {n} | {100 * n / max(tot, 1):.0f}% |")
    prim = sum(n for (s, m), n in mm_cells.items() if m < 512)
    L.append(f"\nPrimary pieces already right: {100 * prim / max(tot, 1):.0f}%. Secondary piece names: {len(names)}.\n")
    L.append("| top N names | cells covered (incl. primary) | unique secondary tiles needed |")
    L.append("|---|---|---|")
    cum, chosen = prim, []
    for i, (nme, n) in enumerate(names.most_common(), 1):
        cum += n
        chosen.append(rep[nme])
        if i in {5, 10, 15, 20, 30, 40, 60, 80, 120, 200}:
            L.append(f"| {i} | {100 * cum / max(tot, 1):.0f}% | {len(tiles_of(chosen))} |")
    L.append("")
    L.append("Top 30 names: " + ", ".join(f"`{n}` {c}" for n, c in names.most_common(30)) + "\n")


def main():
    wd = gv.World()
    prim_dir = None
    # primary: occupancy
    any_stem = "route_1"
    pts = wd.ts(any_stem)
    n_ptiles = len(pts.ptiles)
    n_pmeta = len(pts.pmeta)
    pal_used = [set() for _ in range(6)]
    pri_names = load_mapping("gTileset_OrleansGeneral")
    # used primary metatiles anywhere (outdoor maps only here; interiors reported separately)
    used_pri = Counter()
    for stem in world.OUTDOOR:
        for v in wd.blocks[stem]:
            if (v & 0x3FF) < 512:
                used_pri[v & 0x3FF] += 1
    # primary tiles referenced by primary metatiles in use + by every secondary metatile used (primary tile ids < 512 in secondary pieces)
    used_ptiles = set()
    for mid in range(n_pmeta):
        for tid, hf, vf, pal in metatile_tiles(pts, mid):
            if tid < 512:
                used_ptiles.add(tid)
            if tid < 512 and pal < 6:
                px = pts.tile(tid)
                if px:
                    for c in set(px):
                        if c:
                            pal_used[pal].add(pts.pals[pal][c])
    all_used_ptiles = set()
    for mid in used_pri:
        for tid, hf, vf, pal in metatile_tiles(pts, mid):
            if tid < 512:
                all_used_ptiles.add(tid)

    # ---- seam bands
    band_cells = defaultdict(Counter)          # category -> Counter((tileset, mid))
    per_map = {}
    joins = []
    cat_cells = Counter()
    mm_cells = Counter()
    piece_cells = Counter()                    # (tileset const, mid) -> cells in seam bands + unconnected margins
    kinds_cells = {"seam": Counter(), "margin": Counter()}
    map_piece = {}
    tilekeys = {}
    names_by_ts = {}
    for stem in world.OUTDOOR:
        segs, bk = gv.analyse(wd, stem)
        w, h = wd.size(stem)
        lay = wd.maps.info[stem]["layout"]
        sec = lay["secondary_tileset"]
        ts = wd.ts(stem)
        names = names_by_ts.setdefault(sec, load_mapping(sec))
        rec = {"seam": Counter(), "margin": Counter(), "segs": segs}
        for s in segs:
            side, a, b = s["side"], s["a"], s["b"]
            D = gv.VIS[side]
            kind = "seam" if s["kind"] else "margin"
            for i in range(a, b):
                for d in range(D):
                    x, y = {"N": (i, d), "S": (i, h - 1 - d), "W": (d, i), "E": (w - 1 - d, i)}[side]
                    mid = wd.blocks[stem][y * w + x] & 0x3FF
                    rec[kind][mid] += 1
                    piece_cells[(sec, mid, kind)] += 1
                    if kind == "seam" and wd.maps.info[s["kind"]]["layout"]["secondary_tileset"] != sec:
                        mm_cells[(sec, mid)] += 1
        per_map[stem] = rec

    # classify
    cls_cache = {}

    def klass(sec, mid):
        key = (sec, mid)
        if key not in cls_cache:
            stem = next(s for s in world.OUTDOOR if wd.maps.info[s]["layout"]["secondary_tileset"] == sec)
            ts = wd.ts(stem)
            nm = (names_by_ts.setdefault(sec, load_mapping(sec)).get(mid) if mid >= 512 else pri_names.get(mid))
            cls_cache[key] = (classify(nm, ts.metatile(mid)), nm)
        return cls_cache[key]

    # per category totals
    cat_tot = {"seam": Counter(), "margin": Counter()}
    cat_pieces = defaultdict(lambda: defaultdict(Counter))   # kind -> cat -> {(sec, mid): cells}
    for (sec, mid, kind), n in piece_cells.items():
        c, nm = klass(sec, mid)
        cat_tot[kind][c] += n
        cat_pieces[kind][c][(sec, mid)] += n

    # ---- tile cost of pieces
    def tiles_of(pieces):
        keys, cols = {}, {}
        for (sec, mid) in pieces:
            if mid < 512:
                continue                       # primary already
            stem = next(s for s in world.OUTDOOR if wd.maps.info[s]["layout"]["secondary_tileset"] == sec)
            ts = wd.ts(stem)
            for tid, hf, vf, pal in metatile_tiles(ts, mid):
                if tid < 512:
                    continue                    # a primary tile
                k, c = tile_key(ts, tid, hf, vf, pal)
                if k is not None:
                    keys[k] = c
        return keys

    allp = {(sec, mid) for (sec, mid, _k) in piece_cells}
    secondary_pieces = {p for p in allp if p[1] >= 512}
    all_keys = tiles_of(allp)

    # packing check against the primary palettes
    def pack(keys, existing):
        pals = [set(p) for p in existing]
        caps = 15
        unfit = 0
        extra_cols = 0
        newpals = []
        for k, c in sorted(keys.items(), key=lambda kv: -len(kv[1])):
            best, bestscore = None, -1
            for i, p in enumerate(pals):
                add = len(c - p)
                if len(p) + add <= caps:
                    score = len(c & p) * 100 - add
                    if score > bestscore:
                        best, bestscore = i, score
            if best is None:
                unfit += 1
                newpals.append(c)
            else:
                extra_cols += len(c - pals[best])
                pals[best] |= c
        return unfit, extra_cols, pals

    existing = [pal_used[i] for i in range(6)]

    # ---- write the data file
    L = []
    L.append("# Edges measure: generated data\n")
    L.append("Generated by `tools/mapgen/edges_measure.py` (read-only). Bands: N/S 5 rows, W/E 7 columns of the map's own cells along every connected edge (seam) or unconnected edge (margin).\n")
    L.append("## Primary (gTileset_OrleansGeneral) now\n")
    L.append(f"- tiles.png holds {n_ptiles} tiles of 512 allowed ({512 - n_ptiles} free); metatiles.bin {n_pmeta} of 512 ({512 - n_pmeta} free).")
    L.append(f"- primary metatiles used on the 36 outdoor maps: {len(used_pri)} (of {n_pmeta}); tiles those need: {len(all_used_ptiles)}. Tiles reachable only from primary metatiles no outdoor map uses: {len(used_ptiles - all_used_ptiles)} (reclaimable if nothing else, e.g. interiors, uses them).")
    L.append("- palette colours in use per primary palette (index 0 = backdrop excluded): " + ", ".join(f"pal {i}: {len(pal_used[i])}/15" for i in range(6)))
    L.append("")
    L.append("## Seam-band and margin vocabulary (cells, all 36 maps)\n")
    L.append("| terrain class | seam cells | margin cells | distinct piece names | (tileset, id) pieces |")
    L.append("|---|---|---|---|---|")
    cats = sorted(set(cat_tot["seam"]) | set(cat_tot["margin"]), key=lambda c: -(cat_tot["seam"][c] + cat_tot["margin"][c]))
    for c in cats:
        pcs = set(cat_pieces["seam"][c]) | set(cat_pieces["margin"][c])
        nms = {klass(sec, mid)[1] or f"{sec}:{mid}" for (sec, mid) in pcs}
        L.append(f"| {c} | {cat_tot['seam'][c]} | {cat_tot['margin'][c]} | {len(nms)} | {len(pcs)} |")
    tot_seam = sum(cat_tot["seam"].values())
    tot_margin = sum(cat_tot["margin"].values())
    sec_seam = sum(n for (s, m, k), n in piece_cells.items() if k == "seam" and m >= 512)
    sec_margin = sum(n for (s, m, k), n in piece_cells.items() if k == "margin" and m >= 512)
    L.append(f"\nTotals: seam {tot_seam} cells ({100 * sec_seam / max(tot_seam, 1):.0f}% secondary pieces), margin {tot_margin} cells ({100 * sec_margin / max(tot_margin, 1):.0f}% secondary).\n")
    L.append(f"Everything used in any band/margin needs {len(secondary_pieces)} distinct secondary pieces = {len(all_keys)} unique 8x8 tiles (flip-deduplicated, colours resolved) and "
             f"{len(set().union(*all_keys.values()) if all_keys else set())} distinct colours.\n")

    vocab_section(wd, L, pts, used_pri)
    L.append("## Pieces by class (top pieces, with the tiles each costs)\n")
    for c in cats:
        pcs = Counter()
        for k in ("seam", "margin"):
            pcs.update(cat_pieces[k][c])
        keys = tiles_of(pcs)
        L.append(f"### {c}: {len(pcs)} pieces, {len(keys)} unique secondary tiles")
        for (sec, mid), n in pcs.most_common(8):
            nm = klass(sec, mid)[1]
            L.append(f"- {mid:03X} `{nm}` ({sec.replace('gTileset_', '')}): {n} cells")
        L.append("")

    L.append("## Coverage curve by piece NAME (tileset-independent), seam + margin cells\n")
    namecnt = Counter()
    rep = {}
    for (sec, mid, k), n in piece_cells.items():
        nm = klass(sec, mid)[1] or f"{sec}:{mid}"
        if mid < 512:
            continue                      # primary pieces are already shared
        namecnt[nm] += n
        rep.setdefault(nm, (sec, mid))
    total = sum(n for (s, m, k), n in piece_cells.items())
    prim_cells = sum(n for (s, m, k), n in piece_cells.items() if m < 512)
    L.append(f"Cells already drawn right (primary pieces): {100 * prim_cells / total:.0f}%. The rest by secondary piece name:\n")
    L.append("| top N names | cumulative cells covered (incl. primary) | unique secondary tiles needed |")
    L.append("|---|---|---|")
    cum, chosen = prim_cells, []
    marks = {5, 10, 15, 20, 30, 40, 60, 80, 120, 200, 400}
    for i, (nm, n) in enumerate(namecnt.most_common(), 1):
        cum += n
        chosen.append(rep[nm])
        if i in marks:
            L.append(f"| {i} | {100 * cum / total:.0f}% | {len(tiles_of(chosen))} |")
    L.append(f"\nDistinct secondary piece names in bands/margins: {len(namecnt)}.\n")
    L.append("Top 25 secondary names: " + ", ".join(f"`{nm}` {n}" for nm, n in namecnt.most_common(25)) + "\n")

    mismatch_section(wd, L, klass, tiles_of, mm_cells, pts, used_pri)
    L.append("## Per map (seam bands and margins)\n")
    for stem in world.OUTDOOR:
        rec = per_map[stem]
        sec = wd.maps.info[stem]["layout"]["secondary_tileset"]
        L.append(f"### {world.OUTDOOR[stem]} (`{stem}`, {sec.replace('gTileset_', '')})")
        for kind in ("seam", "margin"):
            cc = Counter()
            for mid, n in rec[kind].items():
                cc[klass(sec, mid)[0]] += n
            tot = sum(cc.values()) or 1
            L.append(f"- {kind} ({tot} cells): " + ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in cc.most_common(7)))
        bids = wd.border[stem]
        L.append(f"- border block now: " + "/".join(f"{b & 0x3FF:03X}" for b in bids) + " = " + ", ".join(sorted({str(klass(sec, b & 0x3FF)[1]) for b in bids})))
        L.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # json for the analysis step
    summary = dict(n_ptiles=n_ptiles, n_pmeta=n_pmeta, used_pri=len(used_pri), seam=tot_seam, margin=tot_margin,
                   unique_tiles=len(all_keys), pieces=len(secondary_pieces))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()

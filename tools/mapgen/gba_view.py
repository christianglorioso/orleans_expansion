"""GBA-accurate edge view: what the player really sees near the edges of every Orleans outdoor map.

usage (from the decomp root):  python tools/mapgen/gba_view.py [map_stem ...]

Read-only on game data.  Writes into tools/mapgen/maps/:
  gba_view/<map>.png          the map plus the engine's whole backup margin, drawn the way the GBA draws it
  00_gba_view.png             contact sheet of every map, downscaled to ~8000 px on the long side
  00_gba_view_report.md       every map and edge segment: connected or not, how wrong, severity

How the engine does it (src/fieldmap.c, include/fieldmap.h, src/field_camera.c; this script ports it literally):
  * gBackupMapLayout is (w + 15) x (h + 14): MAP_OFFSET = 7 cells of margin on every side (east gets 8 columns:
    MAP_OFFSET_W = 15 = 7 + 1 + 7, the extra one is the east side).  It is filled with 0xFFFF (MAPGRID_UNDEFINED),
    then the map is copied to (7, 7), then every connection in map.json order copies a strip of the neighbour's
    raw blocks: 7 rows for north/south, 7 columns for west, 8 for east, clipped to the backup grid.  Later
    connections overwrite earlier ones.
  * Any cell still 0xFFFF (unconnected edge, the part of an edge a connection doesn't reach, and the four
    diagonal corners) is drawn as the border block: border.bin is 2 x 2, border[(x & 1) + (y & 1) * 2] with x, y in
    map coordinates (backup coordinate - 7), tiled forever.  (GetBorderBlockAt; Orleans layouts are not FRLG.)
  * Every cell is drawn with the CURRENT map's primary and secondary tileset (DrawMetatileAt): a neighbour's
    metatile id >= 512 indexes THIS map's secondary, and its tile ids and palettes (primary palettes 0-5, secondary
    6-12) are this map's.  That is the garbled strip.  An id past the end of this secondary reads off the end of
    its table (garbage); drawn magenta here.
  * The camera: DrawWholeMapView draws a 16 x 16 metatile window, the screen shows 240 x 160 px = 15 x 10 metatiles
    (the BG vertical offset is +8, so the window's top row is half hidden), the player stands at metatile column 7,
    row 5 of the window (5 rows above, 4.5 below).  So the player at the map edge sees 7 cells past a west/east edge
    (8 on the east while scrolling) and 5 past a north/south edge (the 5th half hidden on the south, the 5th on the
    north half visible).  The view margins used for the statistics are W 7, E 7, N 5, S 5; the picture shows the whole
    backup margin and dims what the camera can never reach.
  * gBackupMapLayout must be <= MAX_MAP_DATA_SIZE (10240) cells or the map does not load; the report lists the area.
"""
import json
import os
import re
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
from render import Tilesets  # noqa: E402

ROOT = world.ROOT
OUT = os.path.join(world.MAPS)
VIEW_DIR = os.path.join(OUT, "gba_view")

MAP_OFFSET = 7
MAX_MAP_DATA_SIZE = 10240
UNDEF = 0xFFFF
VIS = {"N": 5, "S": 5, "W": 7, "E": 7}           # cells the camera shows past each edge (statistics)
NUM_METATILES_PRIMARY = 512
DIFF_THRESHOLD = 14.0                              # mean abs RGB difference above which a cell "looks different"
CUT_THRESHOLD = 22.0                               # edge cell vs the border block beside it: a hard cutoff
DIRSIDE = {"up": "N", "down": "S", "left": "W", "right": "E"}


def snake(name):
    name = name.replace("gTileset_", "")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def tileset_dirs(layout):
    pd = os.path.join(ROOT, "data/tilesets/primary", snake(layout["primary_tileset"]))
    sd = os.path.join(ROOT, "data/tilesets/secondary", snake(layout["secondary_tileset"]))
    return pd, sd


def read_u16(path):
    data = open(path, "rb").read()
    return list(struct.unpack(f"<{len(data) // 2}H", data))


class World:
    def __init__(self):
        self.maps = world.Maps()
        self.const2stem = {i["const"]: s for s, i in self.maps.info.items()}
        self.ts_cache = {}
        self.blocks = {}
        self.border = {}
        self.conns = {}
        for stem, info in self.maps.info.items():
            lay = info["layout"]
            self.blocks[stem] = read_u16(os.path.join(ROOT, lay["blockdata_filepath"]))
            assert len(self.blocks[stem]) == info["w"] * info["h"], stem
            self.border[stem] = read_u16(os.path.join(ROOT, lay["border_filepath"]))
            mj = json.load(open(info["path"], encoding="utf-8"))
            self.conns[stem] = [(c["direction"], self.const2stem[c["map"]], c["offset"]) for c in (mj.get("connections") or [])]

    def ts(self, stem):
        lay = self.maps.info[stem]["layout"]
        key = tileset_dirs(lay)
        if key not in self.ts_cache:
            self.ts_cache[key] = Tilesets(*key)
        return self.ts_cache[key]

    def size(self, stem):
        i = self.maps.info[stem]
        return i["w"], i["h"]

    def backup(self, stem):
        """gBackupMapLayout as the engine builds it: (grid, src) with src[cell] = None (map), ('conn', stem) or None for border"""
        w, h = self.size(stem)
        W, H = w + 2 * MAP_OFFSET + 1, h + 2 * MAP_OFFSET
        grid = [UNDEF] * (W * H)
        src = [None] * (W * H)             # 'map' | stem of the connection | None (border)
        for y in range(h):
            for x in range(w):
                grid[(y + MAP_OFFSET) * W + x + MAP_OFFSET] = self.blocks[stem][y * w + x]
                src[(y + MAP_OFFSET) * W + x + MAP_OFFSET] = "map"

        def fill(x, y, cstem, x2, y2, fw, fh):
            cw, _ch = self.size(cstem)
            cb = self.blocks[cstem]
            for j in range(fh):
                for i in range(fw):
                    if 0 <= x + i < W and 0 <= y + j < H:
                        grid[(y + j) * W + x + i] = cb[(y2 + j) * cw + x2 + i]
                        src[(y + j) * W + x + i] = cstem

        for d, cstem, off in self.conns[stem]:
            cw, ch = self.size(cstem)
            if d in ("down", "up"):
                x = off + MAP_OFFSET
                if d == "down":
                    y, y2 = h + MAP_OFFSET, 0
                else:
                    y, y2 = 0, ch - MAP_OFFSET
                if x < 0:
                    x2 = -x
                    x += cw
                    width = x if x < W else W
                    x = 0
                else:
                    x2 = 0
                    width = cw if x + cw < W else W - x
                fill(x, y, cstem, x2, y2, width, MAP_OFFSET)
            else:
                y = off + MAP_OFFSET
                if d == "left":
                    x, x2, fw = 0, cw - MAP_OFFSET, MAP_OFFSET
                else:
                    x, x2, fw = w + MAP_OFFSET, 0, MAP_OFFSET + 1
                if y < 0:
                    y2 = -y
                    height = y + ch if y + ch < H else H
                    y = 0
                else:
                    y2 = 0
                    height = ch if y + ch < H else H - y
                fill(x, y, cstem, x2, y2, fw, height)
        b = self.border[stem]
        for by in range(H):
            for bx in range(W):
                if grid[by * W + bx] == UNDEF:
                    mx, my = bx - MAP_OFFSET, by - MAP_OFFSET
                    grid[by * W + bx] = b[(mx & 1) + (my & 1) * 2]      # (x + 1) & 1 on backup coords == mx & 1
        return grid, src, W, H


def cell_img(ts, v):
    return ts.metatile(v & 0x3FF)


def img_diff(a, b):
    """mean abs RGB difference between two 16 x 16 images"""
    pa, pb = a.tobytes(), b.tobytes()
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def secondary_len(ts):
    return len(ts.smeta)


def garbage(ts, v):
    m = v & 0x3FF
    return m >= NUM_METATILES_PRIMARY + len(ts.smeta) if m >= NUM_METATILES_PRIMARY else m >= len(ts.pmeta)


def runs(vals):
    """[(start, end_exclusive, value)] maximal runs of equal values"""
    out, s = [], 0
    for i in range(1, len(vals) + 1):
        if i == len(vals) or vals[i] != vals[s]:
            out.append((s, i, vals[s]))
            s = i
    return out


def analyse(wd, stem):
    """per-edge-segment statistics of one map"""
    w, h = wd.size(stem)
    grid, src, W, H = wd.backup(stem)
    ts = wd.ts(stem)
    segs = []
    for side in "NSWE":
        length = w if side in "NS" else h
        depth = VIS[side]

        def cell(i, k):
            """backup coordinates of the k-th cell outward (k = 1 is adjacent) of edge position i"""
            if side == "N":
                return i + MAP_OFFSET, MAP_OFFSET - k
            if side == "S":
                return i + MAP_OFFSET, h + MAP_OFFSET - 1 + k
            if side == "W":
                return MAP_OFFSET - k, i + MAP_OFFSET
            return w + MAP_OFFSET - 1 + k, i + MAP_OFFSET

        kinds = [src[cell(i, 1)[1] * W + cell(i, 1)[0]] for i in range(length)]
        for a, b, kind in runs(kinds):
            seg = {"side": side, "a": a, "b": b, "len": b - a, "kind": kind, "depth": depth}
            # a connection copies the neighbour's WHOLE strip: its cells up to 7 columns (N/S) / 5 rows (E/W) past the overlap are in the
            # camera too (the corners), drawn with THIS map's tileset: grade them as well (only cells that really hold this neighbour)
            ext = 7 if side in "NS" else 5
            cells = [(cell(i, k), i, k) for i in range(a - (ext if kind is not None else 0), b + (ext if kind is not None else 0))
                     for k in range(1, depth + 1) if kind is None or (0 <= cell(i, k)[0] < W and 0 <= cell(i, k)[1] < H)]
            if kind is not None:                      # connected
                nts = wd.ts(kind)
                sec = wrong = garb = n = 0
                for (bx, by), i, k in cells:
                    v = grid[by * W + bx]
                    if src[by * W + bx] != kind:
                        continue
                    n += 1
                    m = v & 0x3FF
                    if m >= NUM_METATILES_PRIMARY:
                        sec += 1
                    if garbage(ts, v):
                        garb += 1
                        wrong += 1
                        continue
                    if img_diff(cell_img(ts, v), cell_img(nts, v)) > DIFF_THRESHOLD:
                        wrong += 1
                seg.update(n=n, secondary=sec / max(n, 1), wrong=wrong / max(n, 1), garbage=garb / max(n, 1))
                share = seg["wrong"]
                seg["sev"] = "HIGH" if share >= 0.5 else "MED" if share >= 0.2 else "LOW" if share > 0 else "OK"
            else:                                     # border
                ids = set()
                for (bx, by), i, k in cells:
                    ids.add(grid[by * W + bx] & 0x3FF)
                bids = [v & 0x3FF for v in wd.border[stem]]
                flat = len(set(bids)) == 1
                # hard cutoff: how different is the outermost map cell from the border cell right beside it?
                diffs = []
                for i in range(a, b):
                    ex, ey = {"N": (i, 0), "S": (i, h - 1), "W": (0, i), "E": (w - 1, i)}[side]
                    bx, by = cell(i, 1)
                    ev = grid[(ey + MAP_OFFSET) * W + ex + MAP_OFFSET]
                    bv = grid[by * W + bx]
                    diffs.append(img_diff(cell_img(ts, ev), cell_img(ts, bv)))
                hard = sum(1 for d in diffs if d > CUT_THRESHOLD) / max(len(diffs), 1)
                seg.update(border_ids=bids, flat=flat, cutoff=hard, mean_diff=sum(diffs) / max(len(diffs), 1))
                if flat and hard >= 0.4:
                    sev = "HIGH"
                elif hard >= 0.4:
                    sev = "MED"
                elif hard >= 0.15:
                    sev = "MED" if flat else "LOW"
                else:
                    sev = "LOW" if flat else "OK"
                if (b - a) <= 2 and hard < 0.9:           # a stub (exit gaps etc.) is minor
                    sev = "LOW" if sev != "OK" else "OK"
                seg["sev"] = sev
            segs.append(seg)
    return segs, (grid, src, W, H)


SEV_COL = {"HIGH": (230, 40, 40), "MED": (240, 150, 30), "LOW": (230, 220, 60), "OK": (60, 200, 90)}


def draw_map(wd, stem, segs, bk, font):
    grid, src, W, H = bk
    w, h = wd.size(stem)
    ts = wd.ts(stem)
    im = Image.new("RGB", (W * 16, H * 16))
    for i, v in enumerate(grid):
        im.paste(cell_img(ts, v), ((i % W) * 16, (i // W) * 16))
    # dim what the camera never reaches
    shade = Image.new("RGB", im.size, (0, 0, 0))
    mask = Image.new("L", im.size, 110)
    md = ImageDraw.Draw(mask)
    vx0, vx1 = (MAP_OFFSET - VIS["W"]) * 16, (MAP_OFFSET + w + VIS["E"]) * 16
    vy0, vy1 = (MAP_OFFSET - VIS["N"]) * 16, (MAP_OFFSET + h + VIS["S"]) * 16
    md.rectangle([vx0, vy0, vx1 - 1, vy1 - 1], fill=0)
    im = Image.composite(shade, im, mask)
    d = ImageDraw.Draw(im)
    d.rectangle([vx0, vy0, vx1 - 1, vy1 - 1], outline=(0, 220, 255))
    d.rectangle([MAP_OFFSET * 16 - 1, MAP_OFFSET * 16 - 1, (MAP_OFFSET + w) * 16, (MAP_OFFSET + h) * 16], outline=(255, 230, 0))
    # segment severity markers along the map edge
    for s in segs:
        a, b, side = s["a"], s["b"], s["side"]
        col = SEV_COL[s["sev"]]
        if side in "NS":
            x0, x1 = (MAP_OFFSET + a) * 16, (MAP_OFFSET + b) * 16
            y = (MAP_OFFSET - 1) * 16 if side == "N" else (MAP_OFFSET + h) * 16 + 12
            d.rectangle([x0 + 1, y + 2, x1 - 2, y + 3], fill=col)
            tx, ty = x0 + 3, y - 10 if side == "N" else y + 4
        else:
            y0, y1 = (MAP_OFFSET + a) * 16, (MAP_OFFSET + b) * 16
            x = (MAP_OFFSET - 1) * 16 if side == "W" else (MAP_OFFSET + w) * 16 + 12
            d.rectangle([x + 2, y0 + 1, x + 3, y1 - 2], fill=col)
            tx, ty = (x - 52 if side == "W" else x + 6), y0 + 2
        label = (s["kind"] if s["kind"] and s["kind"] != "map" else "border") + " " + s["sev"]
        d.text((tx + 1, ty + 1), label, fill=(0, 0, 0), font=font)
        d.text((tx, ty), label, fill=col, font=font)
    return im


def fmt_ids(ids):
    return "/".join(f"{i:03X}" for i in ids)


def main(argv):
    only = [a for a in argv if not a.startswith("-")]
    wd = World()
    stems = only or list(world.OUTDOOR)
    os.makedirs(VIEW_DIR, exist_ok=True)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    report = []
    images = []
    summary = []
    for stem in stems:
        segs, bk = analyse(wd, stem)
        im = draw_map(wd, stem, segs, bk, font)
        path = os.path.join(VIEW_DIR, stem + ".png")
        im.save(path)
        images.append((stem, im))
        w, h = wd.size(stem)
        lay = wd.maps.info[stem]["layout"]
        area = (w + 15) * (h + 14)
        report.append(f"## {world.OUTDOOR[stem]} (`{stem}`) {w}x{h}, `{lay['secondary_tileset']}`, backup grid {area}/{MAX_MAP_DATA_SIZE} cells\n")
        report.append("| edge | cells | status | detail | severity |")
        report.append("|---|---|---|---|---|")
        for s in segs:
            rng = f"{s['side']} {s['a']}-{s['b'] - 1}"
            if s["kind"] is not None:
                det = (f"neighbour `{s['kind']}`: {s['secondary'] * 100:.0f}% of its {s['n']} visible cells are secondary metatiles (>=512); "
                       f"{s['wrong'] * 100:.0f}% draw visibly wrong" + (f" ({s['garbage'] * 100:.0f}% index past this secondary: garbage)" if s["garbage"] else ""))
                status = "connected"
            else:
                det = (f"border `{fmt_ids(s['border_ids'])}` " + ("FLAT single metatile; " if s["flat"] else "patterned; ")
                       + f"{s['cutoff'] * 100:.0f}% of edge cells hard-cut against it (mean diff {s['mean_diff']:.0f})")
                status = "unconnected"
            report.append(f"| {rng} | {s['len']}x{s['depth']} | {status} | {det} | **{s['sev']}** |")
            summary.append((stem, s))
        report.append("")
        print(f"{stem}: {len(segs)} segments", flush=True)
    # contact sheet (shelf packing)
    if len(images) > 1:
        sheet_w = 7600
        pad = 24
        order = sorted(images, key=lambda t: -t[1].size[1])
        x = y = rowh = 0
        place = []
        for stem, im in order:
            if x + im.size[0] > sheet_w and x:
                x, y, rowh = 0, y + rowh + pad + 14, 0
            place.append((stem, im, x, y + 14))
            x += im.size[0] + pad
            rowh = max(rowh, im.size[1])
        total_h = y + rowh + 14
        sheet = Image.new("RGB", (sheet_w, total_h), (30, 30, 36))
        sd = ImageDraw.Draw(sheet)
        for stem, im, px, py in place:
            sheet.paste(im, (px, py))
            sd.text((px, py - 12), f"{world.OUTDOOR[stem]}", fill=(255, 255, 255), font=font)
        long = max(sheet.size)
        if long > 8000:
            f = 8000 / long
            sheet = sheet.resize((int(sheet.size[0] * f), int(sheet.size[1] * f)), Image.LANCZOS)
        sheet.save(os.path.join(OUT, "00_gba_view.png"))
        print("sheet", sheet.size)
    # report
    if not only:
        head = ["# GBA edge view report", "",
                "Generated by `tools/mapgen/gba_view.py`. Engine rules ported from `src/fieldmap.c` (see the script docstring): "
                "7-cell backup margin, connection strips of the neighbour's raw blocks, 2x2 border block tiled by map coordinates, "
                "everything drawn with the CURRENT map's tilesets. Camera reach used here: W 7, E 7, N 5, S 5 cells.", "",
                "Severity. Connected segment: share of the neighbour's visible cells that draw visibly different from how the neighbour's own "
                "tileset draws them (HIGH >= 50%, MED >= 20%, LOW > 0). Unconnected segment: HIGH = flat single-metatile border and terrain "
                "hard-cuts against it on >= 40% of the segment; MED = patterned border but hard cut, or flat with some cut; LOW = flat but "
                "terrain already matches it, or a short stub.", ""]
        cnt = {}
        for _stem, s in summary:
            k = ("conn" if s["kind"] else "border", s["sev"])
            cnt[k] = cnt.get(k, 0) + 1
        head.append("Totals (segments): " + ", ".join(f"{a} {b}: {n}" for (a, b), n in sorted(cnt.items())))
        head.append("")
        worst = sorted(summary, key=lambda t: (-(t[1]["wrong"] if t[1]["kind"] else t[1]["cutoff"]) , -t[1]["len"]))
        head.append("## Worst connected segments")
        head.append("")
        for stem, s in sorted([t for t in summary if t[1]["kind"]], key=lambda t: (-t[1]["wrong"], -t[1]["len"]))[:14]:
            head.append(f"- `{stem}` {s['side']} {s['a']}-{s['b'] - 1} -> `{s['kind']}`: {s['wrong'] * 100:.0f}% wrong, {s['secondary'] * 100:.0f}% secondary ({s['sev']})")
        head.append("")
        head.append("## Isle Marais (asked for specially)")
        head.append("")
        for stem, s in summary:
            if stem == "isle_marais":
                if s["kind"]:
                    head.append(f"- {s['side']} {s['a']}-{s['b'] - 1} connected to `{s['kind']}`: {s['secondary'] * 100:.0f}% secondary, {s['wrong'] * 100:.0f}% draw wrong ({s['sev']})")
                else:
                    head.append(f"- {s['side']} {s['a']}-{s['b'] - 1} unconnected, border `{fmt_ids(s['border_ids'])}` flat={s['flat']}, hard cut {s['cutoff'] * 100:.0f}% ({s['sev']})")
        head.append("")
        head.append("## Maps")
        head.append("")
        with open(os.path.join(OUT, "00_gba_view_report.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(head + report) + "\n")
        print("report written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

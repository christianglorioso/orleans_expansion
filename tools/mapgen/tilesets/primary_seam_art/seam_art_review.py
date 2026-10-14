"""Review mocks for the primary seam-band art (make_primary_seam_art.py): each piece set placed in its real context, drawn the way the
GBA draws it (gba_view's backup layout: the map, its connections' strips and the border, every cell with the VIEWING map's tilesets),
before and after.

usage (from the decomp root):  python tools/mapgen/tilesets/primary_seam_art/seam_art_review.py
reads the built maps and tilesets (writes nothing in data/), writes into tile_review/seams2/art/:
    pieces.png                     every piece at 4x on its ground, with its tile cost
    B_crescent_bay.png             the Surf-exposed band cells of Crescent City sealed with the primary rocks / knee (Crescent's own view
                                   and Route 14's view across the south join)
    D_route_16_17.png              the Johto path through the Route 16 / Route 17 bands on dry ground (both sides of the join)
    D_route_23.png                 the path crossing Route 23's meadow / dry bank at x 8 (both crossings)
    A_route_16.png                 Route 16's NE and SE corners: the scrub wall carried through the band to the border (both sides)
Each sheet: before | after at 3x, the map edge in magenta, cells changed in the after outlined in cyan on a third copy.
The placements are this script's interpretation of where the integrator would put the pieces (EDITS below); nothing is integrated.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MAPGEN = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(MAPGEN, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, MAPGEN)
import make_primary_seam_art as A  # noqa: E402
import gba_view as gv  # noqa: E402
import json  # noqa: E402

OUT = os.path.join(os.path.dirname(ROOT), "tile_review", "seams2", "art")
MO = gv.MAP_OFFSET
FAKE0 = 0x10000


class Mock:
    def __init__(self):
        self.wd = gv.World()
        self.orig = {k: list(v) for k, v in self.wd.blocks.items()}
        self.pieces = {p["id"]: p for p in A.pieces()}
        self.fake, self.fake_of = {}, {}
        self.names = {}

    def names_of(self, stem):
        if stem not in self.names:
            lay = self.wd.maps.info[stem]["layout"]
            n = {}
            for sym in (lay["primary_tileset"], lay["secondary_tileset"]):
                for f in os.listdir(os.path.join(MAPGEN, "tilesets")):
                    if f.endswith(".mapping.json"):
                        m = json.load(open(os.path.join(MAPGEN, "tilesets", f)))
                        if m["tileset"] == sym:
                            n.update(m["metatiles"])
            self.names[stem] = n
        return self.names[stem]

    def piece(self, pid, base=None):
        """a fake block id for piece pid over `base` (a primary metatile name; default the piece's own ground)"""
        p = self.pieces[pid]
        key = (pid, base or p["base"])
        if key not in self.fake_of:
            v = FAKE0 + len(self.fake_of)
            self.fake_of[key] = v
            self.fake[v] = A.over(A.full_rgb(key[1]), p["top"])
        return self.fake_of[key]

    def set(self, stem, cells, what, base=None):
        w = self.wd.maps.info[stem]["w"]
        for x, y in cells:
            cur = self.wd.blocks[stem][y * w + x]
            if what in self.pieces:
                b = base
                if b == "under":   # the piece over whatever primary ground the cell has now
                    inv = {v: k for k, v in self.names_of(stem).items()}
                    b = inv[cur & 0x3FF]
                v = self.piece(what, b)
            else:
                v = self.names_of(stem)[what]
            self.wd.blocks[stem][y * w + x] = v if v >= FAKE0 else (cur & 0xFC00) | v

    def reset(self):
        self.wd.blocks = {k: list(v) for k, v in self.orig.items()}

    def view(self, stem, x0, y0, x1, y1):
        """map cells [x0, x1) x [y0, y1) (may reach into the margin) as the GBA draws them from `stem`"""
        grid, src, W, H = self.wd.backup(stem)
        ts = self.wd.ts(stem)
        im = Image.new("RGB", ((x1 - x0) * 16, (y1 - y0) * 16), (255, 0, 255))
        for y in range(y0, y1):
            for x in range(x0, x1):
                bx, by = x + MO, y + MO
                if not (0 <= bx < W and 0 <= by < H):
                    continue
                v = grid[by * W + bx]
                if v >= FAKE0:
                    c = self.fake[v]
                elif gv.garbage(ts, v):
                    c = Image.new("RGB", (16, 16), (255, 0, 255))
                else:
                    c = ts.metatile(v & 0x3FF)
                im.paste(c, ((x - x0) * 16, (y - y0) * 16))
        return im


def font(n):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def frame(im, stem, wd, x0, y0, k):
    """3x, map edge in magenta"""
    w, h = wd.size(stem)
    big = im.resize((im.width * k, im.height * k), Image.NEAREST)
    d = ImageDraw.Draw(big)
    X0, Y0, X1, Y1 = (0 - x0) * 16 * k, (0 - y0) * 16 * k, (w - x0) * 16 * k, (h - y0) * 16 * k
    d.rectangle((X0, Y0, X1 - 1, Y1 - 1), outline=(255, 0, 255), width=2)
    return big


def outline(big, cells, x0, y0, k, col=(0, 230, 255)):
    big = big.copy()
    d = ImageDraw.Draw(big)
    for x, y in cells:
        X, Y = (x - x0) * 16 * k, (y - y0) * 16 * k
        d.rectangle((X, Y, X + 16 * k - 1, Y + 16 * k - 1), outline=col, width=2)
    return big


def sheet(path, title, rows, notes=()):
    """rows: [(label, [images])]"""
    F, FS = font(18), font(14)
    pad = 12
    width = max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in rows)
    lines = [title] + list(notes)
    height = 30 * len(lines) + sum(max(i.height for i in ims) + 30 + pad for _, ims in rows) + pad
    out = Image.new("RGB", (width, height), (24, 28, 36))
    d = ImageDraw.Draw(out)
    y = pad
    for i, ln in enumerate(lines):
        d.text((pad, y), ln, fill=(240, 240, 240) if i == 0 else (180, 186, 198), font=F if i == 0 else FS)
        y += 30 if i == 0 else 22
    y += 8
    for label, ims in rows:
        d.text((pad, y), label, fill=(240, 240, 240), font=FS)
        y += 24
        x = pad
        for im in ims:
            out.paste(im, (x, y))
            x += im.width + pad
        y += max(i.height for i in ims) + pad
    out = out.crop((0, 0, width, y))
    out.save(path)
    print("wrote", path, out.size)


def compare(M, stem, box, edits, k=3):
    """(before, after, after with the changed cells outlined) of `stem`'s view of box; edits = [(stem, cells, what, base)]"""
    x0, y0, x1, y1 = box
    M.reset()
    before = frame(M.view(stem, *box), stem, M.wd, x0, y0, k)
    for e in edits:
        M.set(*e)
    after_im = M.view(stem, *box)
    M.reset()
    plain = M.view(stem, *box)
    after = frame(after_im, stem, M.wd, x0, y0, k)
    changed = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
               if after_im.crop(((x - x0) * 16, (y - y0) * 16, (x - x0) * 16 + 16, (y - y0) * 16 + 16)).tobytes()
               != plain.crop(((x - x0) * 16, (y - y0) * 16, (x - x0) * 16 + 16, (y - y0) * 16 + 16)).tobytes()]
    return before, after, outline(after, changed, x0, y0, k)


# ---------------------------------------------------------------- the placements (the integrator decides; these are mocks)
def b_edits(M=None):
    # surf_check's five exposed Crescent cells (2026-10-14): (7,0) (96,0) water_C, (83,0) (0,18) water_E, (73,65) water_W
    e = [("crescent_city", [(7, 0)], "w_rock_a", None), ("crescent_city", [(96, 0)], "w_rock_b", None),
         ("crescent_city", [(83, 0)], "w_knee", "under"), ("crescent_city", [(0, 18)], "w_rock_b", "under"),
         ("crescent_city", [(73, 65)], "w_rock_a", "under")]
    return e


def d_16_17_edits():
    e = [("route_17", [(x, 12) for x in range(0, 9)], "pd_N", None),
         ("route_17", [(x, 13) for x in range(0, 9)], "pd_S", None),
         ("route_16", [(38, 16)], "pd_NE", None), ("route_16", [(38, 17)], "pd_iNE", None),
         ("route_16", [(x, 17) for x in range(39, 46)], "pd_N", None),
         ("route_16", [(x, 18) for x in range(38, 46)], "pd_S", None)]
    return e


def d_23_edits():
    # x 8, rows 12 and 34: the path's N edge under the dry corner cell dry:1_2 (unchanged)
    return [("route_23", [(8, 12), (8, 34)], "pd_N_by_dry1_2", None)]


def a_edits(full):
    """Route 16 north-east / south-east: the band x 38-45 (Route 17's view reaches it). full: the wall (rows 0-1 / 26-27) carried on
    to the border with the block + faces (tier A3); otherwise the border itself is the wall in the band (depth 0) and Route 16's
    wall steps down at x 38 (tiers A1 + A2)."""
    e = []
    if full:
        for x in range(38, 46):
            e += [("route_16", [(x, 0)], f"sc_block_{x & 1}0", None), ("route_16", [(x, 1)], f"sc_block_{x & 1}1", None),
                  ("route_16", [(x, 2)], f"sc_S_{x & 1}", None),
                  ("route_16", [(x, 26)], f"sc_block_{x & 1}0", None), ("route_16", [(x, 27)], f"sc_block_{x & 1}1", None),
                  ("route_16", [(x, 25)], f"sc_N_{x & 1}", None)]
        # rows 0-4 have Route 16's border on the east too (the Route 17 connection starts at row 5): its W face down x 45
        e += [("route_16", [(45, 2)], "sc_in_NE", None), ("route_16", [(45, 3)], "sc_W_1", None), ("route_16", [(45, 4)], "sc_W_0", None)]
    else:
        e += [("route_16", [(38, 0)], "sc_in_NW", None), ("route_16", [(38, 1)], "sc_E_1", None),
              ("route_16", [(38, 2)], "sc_out_NW", None)]
        e += [("route_16", [(x, 0)], f"sc_S_{x & 1}", None) for x in range(39, 45)]
        # rows 0-4 have Route 16's border on the east too (the Route 17 connection starts at row 5): its W face down x 45
        e += [("route_16", [(45, 0)], "sc_in_NE", None)] + [("route_16", [(45, y)], f"sc_W_{y & 1}", None) for y in range(1, 5)]
        e += [("route_16", [(38, 27)], "sc_in_SW", None), ("route_16", [(38, 26)], "sc_E_0", None),
              ("route_16", [(38, 25)], "sc_out_SW", None)]
        e += [("route_16", [(x, 27)], f"sc_N_{x & 1}", None) for x in range(39, 46)]
    return e


def pieces_sheet(path):
    import json as _j
    meta = _j.load(open(os.path.join(HERE, "primary_seam_art.json")))
    F = font(13)
    ps = A.pieces()
    S, cw, ch = 4, 16 * 4 + 44, 16 * 4 + 40
    cols = 9
    out = Image.new("RGB", (cols * cw + 12, ((len(ps) + cols - 1) // cols) * ch + 60), (24, 28, 36))
    d = ImageDraw.Draw(out)
    c = meta["counts"]
    d.text((8, 6), "Primary seam-band pieces (gTileset_OrleansGeneral palettes only), each over its primary ground, 4x", fill=(240, 240, 240), font=font(16))
    d.text((8, 28), "  ".join(f"{s}: {c[s]['metatiles']} metatiles / {c[s]['new_tiles']} new tiles" for s in ("B", "D", "A")) +
           "   (A1 " + str(c["A1"]["new_tiles"]) + ", A2 " + str(c["A2"]["new_tiles"]) + ", A3 " + str(c["A3"]["new_tiles"]) + ")",
           fill=(180, 186, 198), font=F)
    for i, p in enumerate(ps):
        X, Y = 8 + (i % cols) * cw, 56 + (i // cols) * ch
        out.paste(A.over(A.full_rgb(p["base"]), p["top"]).resize((16 * S, 16 * S), Image.NEAREST), (X, Y))
        m = meta["pieces"][p["id"]]
        d.text((X, Y + 16 * S + 2), p["id"], fill=(220, 220, 220), font=F)
        d.text((X, Y + 16 * S + 18), f"+{m['new_tiles']} t  {m.get('tier', '')}", fill=(160, 166, 178), font=F)
    out.save(path)
    print("wrote", path, out.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    pieces_sheet(os.path.join(OUT, "pieces.png"))
    M = Mock()
    # ---- B
    rows = []
    for stem, box, lab in (("crescent_city", (-1, -5, 14, 6), "Crescent City NW lake, (7,0): w_rock_a (Route 6 / Route 3 joins to the west)"),
                           ("crescent_city", (76, -5, 104, 6), "Crescent City NE lake, (83,0) knee over water_E, (96,0) w_rock_b"),
                           ("crescent_city", (-7, 12, 8, 24), "Crescent City W, (0,18) w_rock_b over water_E (the Route 6 join strip on the left)"),
                           ("crescent_city", (64, 56, 82, 71), "Crescent City south bay, (73,65) w_rock_a over water_W, seen from Crescent"),
                           ("route_14", (16, -7, 36, 5), "... and the same bay seen from Route 14 across the south join (Crescent's cells drawn with Route 14's tilesets)")):
        b, a, o = compare(M, stem, box, b_edits(M))
        rows.append((lab + ":  before | after | after, changed cells outlined", [b, a, o]))
    sheet(os.path.join(OUT, "B_crescent_bay.png"), "Spec B: primary Surf blockers in the Crescent seam bands (3x, magenta = the viewing map's edge)", rows,
          ["The five cells surf_check still lists for Crescent City. All three pieces are top layers over the ground the cell already has,",
           "so the same rock / knee stands on water_E / water_W at no tile cost (an extra metatile each). Palette 2 (the water palette).",
           "Not art B: the magenta column in Route 14's view (its x 35 = Crescent x 74, rows 57-65) is Crescent's levee (secondary lv_ pieces and",
           "wpr rocks over it), outside bands.py's south band but inside the 8th east column Route 14's camera reaches while scrolling."])
    # ---- D: Route 16 / 17
    rows = []
    for stem, box, lab in (("route_17", (-7, 7, 14, 18), "Route 17's view: its band x 0-7 + Route 16's last 7 columns on the left"),
                           ("route_16", (30, 12, 53, 23), "Route 16's view: its band x 38-45 + Route 17's first 8 columns on the right")):
        b, a, o = compare(M, stem, box, d_16_17_edits())
        rows.append((lab + ":  before | after | after, changed cells outlined", [b, a, o]))
    sheet(os.path.join(OUT, "D_route_16_17.png"), "Spec D: the Johto path on dry ground through the Route 16 / Route 17 seam bands (3x)", rows,
          ["Before: the band path is plain 0D9 (no kerb against sand: the 192-point seams) and Route 17's x 8 has the green-kerbed 0D1 / 0E1 (the nick).",
           "After: pd_N / pd_S along both bands, pd_NE + pd_iNE where Route 16's dry-road stair meets it; the dry road (secondary) starts where it did."])
    rows = []
    for box, lab in (((2, 8, 14, 18), "Route 23, the north crossing (rows 12-13)"), ((2, 30, 14, 39), "Route 23, the south crossing (rows 34-35)")):
        b, a, o = compare(M, "route_23", box, d_23_edits())
        rows.append((lab + ":  before | after | after, changed cells outlined", [b, a, o]))
    sheet(os.path.join(OUT, "D_route_23.png"), "Spec D: the path crossing Route 23's meadow / dry bank at x 8 (3x)", rows,
          ["x 8, rows 12 / 34: pd_N_by_dry1_2, the path's N edge whose kerb follows the bottom edge of the dry corner cell above it (dry:1_2):",
           "grass on the left, dry ground on the right. Nothing else changes (the S side already meets grass; x 9 on is the dry road)."])
    # ---- A
    rows = []
    for full, tag in ((False, "tiers A1 + A2: the border is the wall in the band, Route 16's wall steps down at x 38"),
                      (True, "tiers A1 + A2 + A3: the wall runs on through the band to the border")):
        for stem, box, lab in (("route_16", (28, -5, 53, 6), "Route 16 NE"), ("route_16", (28, 21, 53, 33), "Route 16 SE"),
                               ("route_17", (-7, -5, 8, 3), "Route 17's NW margin (Route 16 rows 0-7 are above its connection: border)")):
            if stem == "route_17" and not full:
                continue
            b, a, o = compare(M, stem, box, a_edits(full))
            rows.append((f"{lab}, {tag}:  before | after | outlined", [b, a, o]))
    sheet(os.path.join(OUT, "A_route_16.png"), "Spec A: the primary dry scrub in Route 16's east band (3x)", rows,
          ["Wall parity as make_borders.py requires it (x 38 even: E face / in_NW / out_NW; row 0 / row 27 = the border as the wall; x 45 = W face",
           "of the east border, which only reaches row 4 there, so no outer corner at (45,5): the 2x2 wall grid would want it at row 6).",
           "The primary scrub is drawn in palette 4 (the foliage palette): its greens are bluer than the dry set's own (secondary) scrub,",
           "so where the band's primary scrub meets Route 16's secondary wall / border block there is a hue step. Route 17's view of rows 0-4",
           "is its border, so only rows 5+ of the band show from there (the SE rows 22-27 do)."])


if __name__ == "__main__":
    main()

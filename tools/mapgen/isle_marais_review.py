"""Review sheet for the Isle Marais slice polish: maps/00_isle_marais_slice_review.png.

usage (from the decomp root): python -W ignore tools/mapgen/isle_marais_review.py

before (maps/isle_marais_before_preview.png: the approved 2026-10-10 map, rendered with its old tileset) | after,
3x crops (before | after) of every area the polish changed, and mock-ups of the proposals that were NOT implemented
(the two sailboats swapped for local craft; a weathered pier) plus the Route 1 join. Reads data/ and the maps only.
"""
import colorsys
import json
import os
import shutil
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402
from render import Tilesets, render  # noqa: E402

MAPS = os.path.join(HERE, "maps")
SPEC = os.path.join(MAPS, "isle_marais.json")
ART = os.path.join(HERE, "sources", "orleans_custom")

CROPS = [   # (title, x0, y0, x1, y1) in cells
    ("Church forecourt, street's west landing, west mud bank", 3, 5, 14, 23),
    ("Barn plaza, east lane, Route 1 road", 16, 0, 33, 9),
    ("Street's east end, mud flat, pier foot", 17, 12, 33, 25),
    ("South lane and mud shoals", 9, 17, 25, 25),
    ("East marsh: grove, reeds, second lily pond", 30, 0, 38, 16),
    ("North patch and reed bed", 12, 0, 26, 12),
]


def font(n):
    try:
        return ImageFont.truetype("arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def draw_spec(spec_path):
    build.MAPPING.clear()
    build.USED.clear()
    build.WANTED.clear()
    b = build.Builder(spec_path)
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    return render(ts, b.flat(), b.w).convert("RGB")


def crop(im, box, k):
    x0, y0, x1, y1 = box
    c = im.crop((x0 * 16, y0 * 16, x1 * 16, y1 * 16))
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


def keyed(path, box=None):
    im = Image.open(path).convert("RGBA")
    if box:
        im = im.crop(box)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] == (255, 0, 255):
                px[x, y] = (0, 0, 0, 0)
    return im


def paste_art(im, art, cx, cy):
    im.alpha_composite(art, (cx * 16, cy * 16))


def weather(im, box):
    """A weathered-driftwood pier: the bright planks desaturated and darkened (a mock-up of the proposal)."""
    out = im.copy()
    px = out.load()
    x0, y0, x1, y1 = [v * 16 for v in box]
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y][:3]
            if r - b > 40 and r > 140 and g > 110:
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                r2, g2, b2 = colorsys.hsv_to_rgb(h, s * 0.5, v * 0.78)
                px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255))
    return out


def stats(im, box):
    x0, y0, x1, y1 = [v * 16 for v in box]
    c = im.crop((x0, y0, x1, y1))
    px = list(c.getdata())
    h = s = v = 0.0
    n = 0
    for r, g, b in px:
        hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        h += hh
        s += ss
        v += vv
        n += 1
    return s / n, v / n


def main():
    after = draw_spec(SPEC)
    before = Image.open(os.path.join(MAPS, "isle_marais_before_preview.png")).convert("RGB")
    tmp = tempfile.mkdtemp()
    try:
        spec = json.load(open(SPEC, encoding="utf-8"))
        spec["buildings"] = [b for b in spec["buildings"] if b["prefab"] != "boat"]
        shutil.copy(os.path.join(MAPS, spec["grid"]), tmp)
        json.dump(spec, open(os.path.join(tmp, "isle_marais.json"), "w", encoding="utf-8"), ensure_ascii=False)
        bare = draw_spec(os.path.join(tmp, "isle_marais.json"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # proposal 1: local craft instead of the two white sailboats
    prop = bare.convert("RGBA")
    pirogue = keyed(os.path.join(ART, "pirogue.png"))                         # the approved Route 1 pirogue, 4x2
    trawler = keyed(os.path.join(ART, "lands_end_art.png"), (160, 272, 256, 320))   # Land's End trawler_a, 6x3
    paste_art(prop, pirogue, 10, 23)   # by the fisherman's fishing spot, resting on the shoal
    paste_art(prop, trawler, 16, 27)   # far off, in open water
    prop = prop.convert("RGB")

    # proposal 2: the pier, weathered
    pier_box = (23, 19, 26, 30)
    weathered = weather(after, pier_box)
    ps, pv = stats(after, pier_box)
    gs, gv = stats(after, (14, 21, 22, 22))      # grass strip
    ws, wv = stats(after, (28, 26, 37, 29))      # open water

    import joined
    joined.APPROACHES[("isle_marais", "N")] = ("route_1", "S")
    panels = joined.pair_image("isle_marais", "route_1")

    pad, head = 24, 44
    width = 2640
    sheet_parts = []   # (title, image)
    sheet_parts.append(("Before (approved 2026-10-10)", before.resize((before.width * 2, before.height * 2), Image.NEAREST)))
    sheet_parts.append(("After", after.resize((after.width * 2, after.height * 2), Image.NEAREST)))
    pairs = []
    for title, *box in CROPS:
        pairs.append((title, crop(before, box, 3), crop(after, box, 3)))
    props = [
        ("Proposal (not implemented): the sailboats swapped for a pirogue at the fishing spot and a far-off trawler",
         crop(after, (6, 20, 32, 30), 2), crop(prop, (6, 20, 32, 30), 2)),
        (f"Proposal (not implemented): weathered pier. Now mean saturation {ps:.2f} / value {pv:.2f} "
         f"(grass {gs:.2f} / {gv:.2f}, water {ws:.2f} / {wv:.2f})",
         crop(after, (17, 17, 33, 30), 2), crop(weathered, (17, 17, 33, 30), 2)),
    ]
    rows = []
    rows.append([sheet_parts[0], sheet_parts[1]])
    for title, a, b in pairs:
        rows.append([(title + " (before)", a), (title + " (after)", b)])
    for title, a, b in props:
        rows.append([(title + " | now", a), ("proposed", b)])
    if panels:
        j = panels[0][1]
        rows.append([("Route 1 join (Isle Marais north exit / Route 1 south end)", j.resize((j.width * 2, j.height * 2), Image.NEAREST))])
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    colw = lambda t, im: max(im.width, int(d0.textlength(t, font=font(24))))
    groups, cur, cw = [], [], 0          # flow the groups (before | after pairs) into rows no wider than the sheet
    flat = rows
    rows = []
    for g in flat:
        gw = sum(colw(t, im) + pad for t, im in g)
        if cur and cw + gw > width:
            rows.append(cur)
            cur, cw = [], 0
        cur.append(g)
        cw += gw
    rows.append(cur)
    height = pad + sum(max(im.height for g in r for _, im in g) + head + pad for r in rows)
    sheet = Image.new("RGB", (width, height), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    y = pad
    for r in rows:
        x = pad
        for g in r:
            for title, im in g:
                d.text((x, y + 6), title, fill=(0, 0, 0), font=font(24))
                sheet.paste(im, (x, y + head))
                x += colw(title, im) + pad
        y += max(im.height for g in r for _, im in g) + head + pad
    out = os.path.join(MAPS, "00_isle_marais_slice_review.png")
    sheet.save(out)
    print(out, sheet.size, f"pier sat/val {ps:.2f}/{pv:.2f} grass {gs:.2f}/{gv:.2f} water {ws:.2f}/{wv:.2f}")


if __name__ == "__main__":
    main()

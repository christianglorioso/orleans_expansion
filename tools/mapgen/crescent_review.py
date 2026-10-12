"""maps/00_crescent_review.png for the review-2 round: the whole map before | after, then 3x crops of every change
(before beside after). maps/crescent_city_before.png is the 2026-10-12 build before the round (rendered through the
tileset of the day); maps/crescent_city_preview.png is the current one (build.py writes it).

usage (from the decomp root): python tools/mapgen/crescent_review.py
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "maps")
OX = 14
SCALE = 3
CROPS = [  # design coordinates (x0, y0, x1, y1)
    ("1. Cemetery: the south fence run flush on the park walk (the gym and forecourt moved up a row)", (-1, 3, 18, 26)),
    ("2. Bandstand centred on its island (and the pond, island and the two cypresses on the same centre line)", (-7, 24, 15, 40)),
    ("3a. Route 3 exit: street 3 narrows by a bevelled step", (-14, 38, 4, 48)),
    ("3b. Route 14 exit: Canal Avenue narrows 4 -> 3 -> 2 a tile a side", (33, 54, 45, 66)),
    ("4+5+6. Riverboat Terminal flush on the quay, the riverboat at the pier's end, no trees in the river", (38, 43, 70, 58)),
    ("7a. Levee along the basin canal, round the corner onto the east bank", (44, 0, 64, 8)),
    ("7b. Levee: the canal's west end", (-14, 0, 6, 8)),
    ("9. Drowned Ward: no walkway; the Blacksnake cellar door is the ruin at the south basin's foot, on street 2", (38, 2, 60, 30)),
    ("10a. Battle Frontier, west half", (-14, 44, 12, 66)),
    ("10b. Battle Frontier, east half", (10, 44, 37, 66)),
    ("11a. Bevelled junction corners: French Quarter, Canal Avenue", (12, 6, 44, 16)),
    ("11b. Bevelled junction corners: Downtown, street 3", (12, 24, 44, 46)),
]


def make():
    before = Image.open(os.path.join(MAPS, "crescent_city_before.png")).convert("RGB")
    after = Image.open(os.path.join(MAPS, "crescent_city_preview.png")).convert("RGB")
    gap, head = 24, 34
    width = before.width + gap + after.width
    blocks = [("Whole map: before | after", before, after)]
    for title, (x0, y0, x1, y1) in CROPS:
        box = ((x0 + OX) * 16, y0 * 16, (x1 + OX) * 16, y1 * 16)
        pair = [im.crop(box).resize(((x1 - x0) * 16 * SCALE, (y1 - y0) * 16 * SCALE), Image.NEAREST) for im in (before, after)]
        blocks.append((title + "   (3x, before | after)", pair[0], pair[1]))
    height = sum(max(a.height, b.height) + head + gap for _, a, b in blocks)
    sheet = Image.new("RGB", (width, height), (250, 247, 238))
    d = ImageDraw.Draw(sheet)
    y = 0
    for title, a, b in blocks:
        d.text((6, y + 8), title, fill=(30, 30, 30))
        sheet.paste(a, (0, y + head))
        sheet.paste(b, (a.width + gap, y + head) if a.width + gap + b.width <= width else (0, y + head + a.height))
        y += max(a.height, b.height) + head + gap
    out = os.path.join(MAPS, "00_crescent_review.png")
    sheet.save(out)
    print("review sheet:", out, sheet.size)


if __name__ == "__main__":
    make()

"""Review the seam where a route meets a town: both previews placed edge to edge as the game would show them,
the route's exit cells lined up with the town's.

usage (from the decomp root): python tools/mapgen/joined.py <out.png> [pair ...]
a pair is town:route (e.g. crescent_city:route_3); with none, every pair in APPROACHES is drawn.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "maps")

# town exit side -> the route that leaves through it, and the side of the route it enters by
APPROACHES = {
    ("isle_marais", "N"): ("route_1", "S"),
    ("crescent_city", "W"): ("route_3", "E"),
    ("crescent_city", "S"): ("route_14", "N"),
    ("pointe_rouge", "W"): ("route_5", "E"),
    ("pointe_rouge", "N"): ("route_23", "W"),
    ("pointe_rouge", "E"): ("route_23", "W"),
    ("pointe_rouge", "S"): ("route_4", "N"),
    ("grand_oak", "S"): ("route_1", "N"),
}


# joins that are map connections rather than road exits (the water-only Old Water): (town, side) -> (route, side, dy)
# where dy is the route's row for the town's row 0 (map.json's connection offset, negated: route y = town y + dy)
LINKS = {
    ("old_water", "E"): ("route_1", "W", -15),
}


def link_image(town, route, side, rside, dy, span=14):
    """A map connection with a row offset: the town's east edge against the route's west edge, rows lined up by dy."""
    tim = Image.open(os.path.join(MAPS, f"{town}_preview.png")).convert("RGB")
    rim = Image.open(os.path.join(MAPS, f"{route}_preview.png")).convert("RGB")
    tw, th = tim.width // 16, tim.height // 16
    rw, rh = rim.width // 16, rim.height // 16
    assert side == "E" and rside == "W", "only east/west links are drawn"
    canvas = Image.new("RGB", (2 * span * 16, th * 16), (30, 30, 30))
    canvas.paste(tim.crop(((tw - span) * 16, 0, tw * 16, th * 16)), (0, 0))
    r0, r1 = max(0, dy), min(rh, th + dy)         # route rows that exist beside the town's rows
    canvas.paste(rim.crop((0, r0 * 16, span * 16, r1 * 16)), (span * 16, (r0 - dy) * 16))
    d = ImageDraw.Draw(canvas)
    d.line([(span * 16, 0), (span * 16, canvas.height)], fill=(255, 0, 255))
    return [(f"{town} {side}  /  {route} {rside}  (route row = town row {dy:+d})", canvas)]


def exits(key):
    """[(side, [cells])] from the spec's exits (side worked out from where the cells lie)."""
    spec = json.load(open(os.path.join(MAPS, f"{key}.json"), encoding="utf-8"))
    grid = [l.rstrip("\n") for l in open(os.path.join(MAPS, spec["grid"]), encoding="utf-8")]
    h, w = len(grid), len(grid[0])
    out = []
    for e in spec.get("exits") or []:
        cells = [tuple(c) for c in e["cells"]]
        xs, ys = {x for x, _ in cells}, {y for _, y in cells}
        side = ("W" if xs == {0} else "E" if xs == {w - 1} else "N" if ys == {0} else "S" if ys == {h - 1}
                else "?")
        out.append((side, cells))
    return out, (w, h)


def pair_image(town, route, span=14):
    tex, (tw, th) = exits(town)
    rex, (rw, rh) = exits(route)
    tim = Image.open(os.path.join(MAPS, f"{town}_preview.png")).convert("RGB")
    rim = Image.open(os.path.join(MAPS, f"{route}_preview.png")).convert("RGB")
    out = []
    for side, cells in tex:
        want = APPROACHES.get((town, side))
        if not want or want[0] != route:
            continue
        rcells = next((c for s, c in rex if s == want[1]), None)
        if rcells is None:
            continue
        if side in "WE":  # horizontal join: rows line up on the exits' first cell
            ty, ry = min(y for _, y in cells), min(y for _, y in rcells)
            top = max(0, ty - span)
            bot = ty + span
            canvas = Image.new("RGB", (2 * span * 16, (bot - top) * 16), (30, 30, 30))
            if side == "W":   # route on the left, its east edge against the town's west edge
                canvas.paste(rim.crop(((rw - span) * 16, (ry - (ty - top)) * 16, rw * 16,
                                       (ry - (ty - top) + bot - top) * 16)), (0, 0))
                canvas.paste(tim.crop((0, top * 16, span * 16, bot * 16)), (span * 16, 0))
            else:
                canvas.paste(tim.crop(((tw - span) * 16, top * 16, tw * 16, bot * 16)), (0, 0))
                canvas.paste(rim.crop((0, (ry - (ty - top)) * 16, span * 16,
                                       (ry - (ty - top) + bot - top) * 16)), (span * 16, 0))
            d = ImageDraw.Draw(canvas)
            d.line([(span * 16, 0), (span * 16, canvas.height)], fill=(255, 0, 255))
        else:  # vertical join
            tx, rx = min(x for x, _ in cells), min(x for x, _ in rcells)
            left = max(0, tx - span)
            right = tx + span
            canvas = Image.new("RGB", ((right - left) * 16, 2 * span * 16), (30, 30, 30))
            if side == "S":   # route below the town
                canvas.paste(tim.crop((left * 16, (th - span) * 16, right * 16, th * 16)), (0, 0))
                canvas.paste(rim.crop(((rx - (tx - left)) * 16, 0, (rx - (tx - left) + right - left) * 16,
                                       span * 16)), (0, span * 16))
            else:
                canvas.paste(rim.crop(((rx - (tx - left)) * 16, (rh - span) * 16,
                                       (rx - (tx - left) + right - left) * 16, rh * 16)), (0, 0))
                canvas.paste(tim.crop((left * 16, 0, right * 16, span * 16)), (0, span * 16))
            d = ImageDraw.Draw(canvas)
            d.line([(0, span * 16), (canvas.width, span * 16)], fill=(255, 0, 255))
        out.append((f"{town} {side}  /  {route} {want[1]}", canvas))
    return out


def main(dest, pairs):
    if not pairs:
        pairs = sorted({f"{t}:{r}" for (t, _), (r, _) in APPROACHES.items()})
    panels = []
    for p in pairs:
        town, route = p.split(":")
        links = [(k, v) for k, v in LINKS.items() if k[0] == town and v[0] == route]
        for (t, side), (r, rside, dy) in links:
            panels += link_image(t, r, side, rside, dy)
        if not links:
            panels += pair_image(town, route)
    try:
        f = ImageFont.truetype("arialbd.ttf", 22)
    except OSError:
        f = ImageFont.load_default()
    W = max(p.width * 2 for _, p in panels) + 40
    H = sum(p.height * 2 + 50 for _, p in panels) + 20
    sheet = Image.new("RGB", (W, H), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    y = 10
    for label, p in panels:
        d.text((20, y), label, fill=(47, 72, 60), font=f)
        sheet.paste(p.resize((p.width * 2, p.height * 2), Image.NEAREST), (20, y + 34))
        y += p.height * 2 + 50
    sheet.save(dest)
    print(dest, sheet.size, len(panels), "joins")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

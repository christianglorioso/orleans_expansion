"""Read a planning-layout mockup PNG into an ASCII terrain grid plus detected buildings and markers.

usage: python extract.py <mockup.png> <out_prefix>
writes <out_prefix>.grid.txt and <out_prefix>.detected.json

The mockups draw the map in a framed area whose grid lines are every 10 tiles. Each tile is
classified by the dominant key color inside it; markers and labels are ignored for terrain.
"""
import json
import sys
from collections import Counter, deque

from PIL import Image

# key color -> terrain char
TERRAIN = {
    (211, 230, 180): ".",  # open ground
    (166, 207, 234): "~",  # water
    (188, 214, 179): '"',  # marsh
    (210, 203, 187): "=",  # street
    (207, 200, 187): "S",  # stone
    (185, 139, 90): "#",   # boardwalk
    (199, 176, 124): "L",  # levee
    (216, 196, 155): ":",  # road
    (255, 253, 246): "H",  # house / building
    (239, 228, 251): "K",  # key building
    (229, 229, 229): "I",  # industrial
    (255, 225, 214): "P",  # pokemon center
    (219, 233, 251): "M",  # mart
    (143, 196, 106): "G",  # tall grass (wild encounters)
    (94, 154, 76): "T",    # tree
    # interiors (tools/mapgen/interiors.py)
    (112, 92, 74): "W",    # wall
    (226, 205, 166): "f",  # wood floor
    (232, 232, 224): "t",  # tile floor
    (176, 150, 116): "x",  # mud / storm damage
    (171, 121, 82): "C",   # counter / table
    (196, 98, 88): "r",    # rug / mat
    (154, 176, 206): "b",  # bed / cot
    (134, 108, 92): "s",   # shelves / cabinet
    (126, 184, 96): "p",   # planter / bed
    (78, 132, 70): "h",    # hedge
    (198, 228, 238): "g",  # glass wall
    (205, 170, 110): "e",  # stage / platform
    (70, 70, 70): "E",     # door mat (exit)
    (184, 158, 92): "v",   # thatch / woven wall
}
BUILDING = set("HKIPMY")

# Outdoor mode (--outdoor): the outdoor key colours only (the interior ones above sit close to some outdoor
# colours, e.g. pepper rows vs stage), plus the colours the later town and route mockups use.
OUTDOOR_CHARS = set('.~"=S#L:HKIPMGT')
TERRAIN_OUTDOOR = {k: v for k, v in TERRAIN.items() if v in OUTDOOR_CHARS}
TERRAIN_OUTDOOR.update({
    # deep water (the Gulf, Big Lake): shades of its wave pattern
    (126, 179, 220): "~", (121, 174, 216): "~", (116, 170, 213): "~", (124, 177, 219): "~", (117, 171, 214): "~",
    # pale open ground, city ground, dry ground, salt flat, sand
    (228, 223, 211): ".", (227, 207, 156): ".",
    (236, 230, 200): ".", (233, 227, 197): ".", (242, 226, 180): ".", (243, 242, 237): ".",
    # forest floor
    (169, 196, 156): ".", (167, 193, 154): ".", (172, 190, 156): ".",
    # marsh tufts
    (173, 203, 163): '"', (166, 198, 157): '"', (159, 192, 149): '"', (155, 189, 145): '"', (157, 191, 147): '"',
    (143, 180, 132): '"',
    # trees and woods
    (125, 155, 108): "T", (156, 197, 138): "T", (151, 186, 133): "T", (79, 127, 82): "T",
    # causeway road (close to the mudflat below: exact matches win)
    (203, 189, 158): ":",
    # sugarcane and pepper rows: crops with wild encounters
    (187, 211, 128): "G", (200, 221, 143): "G", (184, 208, 126): "G", (197, 218, 141): "G",
    (233, 192, 138): "G", (211, 121, 88): "G", (174, 179, 97): "G", (230, 189, 136): "G",
    # footpaths (close to the dry ground above: exact matches win) and more tall-grass shades
    (227, 211, 166): ":", (132, 186, 96): "G", (122, 177, 87): "G",
    # mudflat
    (205, 184, 148): "L", (202, 181, 146): "L",
    # plaza / yard
    (226, 217, 195): "=", (223, 214, 192): "=", (225, 220, 208): "=",
    # rock and cliff
    (157, 146, 132): "R", (155, 144, 130): "R", (116, 107, 93): "R",
    # gym / trial buildings (pinker than the Pokémon Center)
    (253, 226, 226): "Y",
    # the brown exit roads and bridges the later towns draw: boardwalk (a bridge where it crosses water)
    (169, 138, 102): "#",
    # the levee key colour is a road along the levee top (mudflats, a slightly paler tan, stay mud)
    (199, 176, 124): ":",
})
# the dark name pills over exits: their white lettering would otherwise read as a house
LABEL = [(46, 52, 57), (28, 40, 51)]
FRAME_COLOR = (91, 83, 70)

# marker fill colors (circle icons)
MARKERS = {
    (46, 134, 193): "npc",
    (224, 168, 0): "item",
    (211, 84, 0): "event",
    (154, 123, 46): "hidden_item",
    (31, 111, 163): "fishing",
    (169, 50, 38): "mega_stone",
    (192, 57, 43): "trainer",
    (122, 90, 47): "shrine",
    (214, 96, 120): "heal",
    (70, 110, 190): "shop",
    (120, 90, 60): "push",
    (40, 150, 160): "switch",
}


def near(c, table, tol=10):
    best, bd = None, tol * tol * 3
    for k in table:
        d = sum((a - b) ** 2 for a, b in zip(c, k))
        if d <= bd:
            best, bd = k, d
    return best


def find_frame(im):
    """Locate the map frame: the dark border line around the planning area."""
    px = im.load()
    W, H = im.size
    is_frame = lambda c: near(c, (FRAME_COLOR,), tol=8) is not None
    # walk down an inner column to find the frame's top/bottom, then across the middle row
    ys = [y for y in range(H) if is_frame(px[W // 4, y])]
    top, bottom = ys[0], ys[-1]
    mid = (top + bottom) // 2
    xs = [x for x in range(W) if is_frame(px[x, mid])]
    # group into runs of adjacent pixels: the first two runs are the frame's left and right lines
    runs = [[xs[0], xs[0]]]
    for x in xs[1:]:
        if x - runs[-1][1] <= 2:
            runs[-1][1] = x
        else:
            runs.append([x, x])
    left, right = runs[0][0], runs[1][1]
    # the frame line is ~2px thick; the playable area starts right after it
    return left, top, right, bottom


def grid_pitch(im, frame):
    """Distance between the faint 10-tile grid lines, divided by 10."""
    px = im.load()
    left, top, right, bottom = frame
    y = top + 3
    runs, prev = [], None
    # grid lines are slightly darker than the surrounding fill; find their x positions on many rows
    votes = Counter()
    for y in range(top + 5, bottom - 5, 7):
        for x in range(left + 5, right - 5):
            a, b = px[x - 1, y], px[x, y]
            if sum(b) < sum(a) - 25 and abs(sum(px[x + 2, y]) - sum(a)) < 6:
                votes[x - left] += 1
    lines = sorted(x for x, n in votes.items() if n > (bottom - top) / 7 * 0.3)
    merged = []
    for x in lines:
        if not merged or x - merged[-1] > 4:
            merged.append(x)
    if len(merged) >= 2:
        gaps = [b - a for a, b in zip(merged, merged[1:])]
        return Counter(gaps).most_common(1)[0][0] / 10, merged
    return None, merged


def classify(im, frame, pitch, table=None):
    table = table or TERRAIN
    px = im.load()
    left, top, right, bottom = frame
    ox, oy = left, top
    w = round((right - left) / pitch)
    h = round((bottom - top) / pitch)
    grid = []
    for ty in range(h):
        row = []
        for tx in range(w):
            x0, y0 = ox + tx * pitch, oy + ty * pitch
            c, pill, n = Counter(), 0, 0
            for yy in range(int(y0 + pitch * 0.15), int(y0 + pitch * 0.85), 2):
                for xx in range(int(x0 + pitch * 0.15), int(x0 + pitch * 0.85), 2):
                    n += 1
                    if table is not TERRAIN and near(px[xx, yy], LABEL, tol=8):
                        pill += 1
                    k = near(px[xx, yy], table)
                    if k:
                        c[table[k]] += 1
            row.append(c.most_common(1)[0][0] if c and pill < 0.25 * n else "?")
        grid.append(row)
    # labels are horizontal pills over a road or shore: a run of unknown cells takes what continues on
    # both sides of it in its row (or the one side, at the map edge)
    for y in range(h):
        x = 0
        while x < w:
            if grid[y][x] != "?":
                x += 1
                continue
            x1 = x
            while x1 < w and grid[y][x1] == "?":
                x1 += 1
            a = grid[y][x - 1] if x > 0 else None
            b = grid[y][x1] if x1 < w else None
            if (a or b) and (a == b or a is None or b is None):
                for i in range(x, x1):
                    grid[y][i] = a or b
            x = x1
    # the rest (covered by markers) from their neighbours
    for _ in range(4):
        for y in range(h):
            for x in range(w):
                if grid[y][x] == "?":
                    n = Counter(grid[j][i] for i, j in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                                if 0 <= i < w and 0 <= j < h and grid[j][i] != "?")
                    if n:
                        grid[y][x] = n.most_common(1)[0][0]
    return grid


def components(grid, chars):
    h, w = len(grid), len(grid[0])
    seen, out = set(), []
    for y in range(h):
        for x in range(w):
            if grid[y][x] in chars and (x, y) not in seen:
                q, cells = deque([(x, y)]), []
                seen.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    cells.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and grid[ny][nx] in chars:
                            seen.add((nx, ny))
                            q.append((nx, ny))
                out.append(cells)
    return out


def find_markers(im, frame, pitch):
    px = im.load()
    left, top, right, bottom = frame
    hits = {}
    for y in range(top, bottom, 2):
        for x in range(left, right, 2):
            k = near(px[x, y], MARKERS, tol=6)
            if k:
                hits.setdefault(MARKERS[k], []).append((x, y))
    out = []
    for kind, pts in hits.items():
        # cluster points that are close together into single markers
        clusters = []
        for p in pts:
            for cl in clusters:
                if abs(cl[0][0] - p[0]) < pitch * 0.9 and abs(cl[0][1] - p[1]) < pitch * 0.9:
                    cl.append(p)
                    break
            else:
                clusters.append([p])
        for cl in clusters:
            if len(cl) < 60:  # marker circles give 95+ samples; crop-row and fairy-ring dots 20-35
                continue
            cx = sum(p[0] for p in cl) / len(cl)
            cy = sum(p[1] for p in cl) / len(cl)
            out.append({"kind": kind, "x": int((cx - left) // pitch), "y": int((cy - top) // pitch)})
    return sorted(out, key=lambda m: (m["y"], m["x"]))


def find_exits(im, frame, pitch):
    """The mockup's exit arrows: small dark triangles sitting on the frame's edges. Returns
    [{"side": "N|S|W|E", "pos": tile index along that edge}] (the arrow's centre)."""
    px = im.load()
    left, top, right, bottom = frame
    W, H = im.size
    band = int(pitch * 0.75)
    out = []
    for side in "NSWE":
        hits = []
        if side in "NS":
            y0 = top if side == "N" else bottom
            for y in range(max(0, y0 - band), min(H, y0 + band), 2):
                for x in range(left, right, 2):
                    if near(px[x, y], LABEL, tol=10):
                        hits.append((x, y))
        else:
            x0 = left if side == "W" else right
            for x in range(max(0, x0 - band), min(W, x0 + band), 2):
                for y in range(top, bottom, 2):
                    if near(px[x, y], LABEL, tol=10):
                        hits.append((x, y))
        # cluster along the edge
        key = (lambda p: p[0]) if side in "NS" else (lambda p: p[1])
        hits.sort(key=key)
        clusters = []
        for p in hits:
            if clusters and key(p) - key(clusters[-1][-1]) <= 6:
                clusters[-1].append(p)
            else:
                clusters.append([p])
        for cl in clusters:
            span = key(cl[-1]) - key(cl[0])
            if len(cl) < 12 or span > pitch * 1.6:  # an arrow is about a tile across; a label pill is longer
                continue
            c = sum(key(p) for p in cl) / len(cl)
            pos = int((c - (left if side in "NS" else top)) // pitch)
            out.append({"side": side, "pos": pos})
    return out


def main(path, prefix, outdoor=False):
    im = Image.open(path).convert("RGB")
    frame = find_frame(im)
    pitch, lines = grid_pitch(im, frame)
    if not pitch or (frame[2] - frame[0]) / pitch > 120:  # too few grid lines to measure (small rooms), or
        pitch = 36.0                                       # crop hatching read as grid lines: every mockup uses 36 px
    grid = classify(im, frame, pitch, TERRAIN_OUTDOOR if outdoor else TERRAIN)
    buildings = []
    for cells in components(grid, BUILDING):
        xs, ys = [c[0] for c in cells], [c[1] for c in cells]
        kinds = Counter(grid[y][x] for x, y in cells)
        buildings.append({"kind": kinds.most_common(1)[0][0], "x": min(xs), "y": min(ys),
                          "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1})
    open(prefix + ".grid.txt", "w").write("\n".join("".join(r) for r in grid) + "\n")
    json.dump({"source": path, "frame": frame, "pitch": pitch, "width": len(grid[0]), "height": len(grid),
               "buildings": buildings, "markers": find_markers(im, frame, pitch),
               "exits": find_exits(im, frame, pitch) if outdoor else []},
              open(prefix + ".detected.json", "w"), indent=1)
    print(f"frame={frame} pitch={pitch} size={len(grid[0])}x{len(grid)}")


if __name__ == "__main__":
    main(*sys.argv[1:3], outdoor="--outdoor" in sys.argv)

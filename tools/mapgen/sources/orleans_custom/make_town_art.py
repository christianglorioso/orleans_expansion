"""Own art for Grand Oak: the glass-conservatory gym and a complete round oak.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_town_art.py
writes greenhouse.png (10x7 cells), oak.png and magnolia.png (2x3), planter.png (3x3) next to this script; magenta = transparent.

The oak starts from vanilla Emerald's round tree (general tileset 0x1D4/0x1D5/0x1DC/0x1DD), which
is only the lower half of a canopy; its missing cap is drawn here from the canopy's own leaves.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = (255, 0, 255)
CLEAR = (0, 0, 0, 0)


# ---------------------------------------------------------------- oak
def oak():
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from render import Tilesets
    ts = Tilesets("data/tilesets/primary/general", "data/tilesets/secondary/petalburg")
    src = Image.new("RGB", (32, 32))
    for i, k in enumerate((0x1D4, 0x1D5, 0x1DC, 0x1DD)):
        src.paste(ts.metatile(k), ((i % 2) * 16, (i // 2) * 16))
    ground = {(115, 197, 164), (65, 180, 131), (164, 213, 197), (24, 164, 106)}  # grass + its shadow
    leaf = src.convert("RGBA")
    px = leaf.load()
    for y in range(32):
        for x in range(32):
            if px[x, y][:3] in ground:
                px[x, y] = CLEAR
    out = Image.new("RGBA", (32, 48), CLEAR)
    # extend the canopy upward: copies of its leafy upper rows stacked above it, then rounded off
    top = leaf.crop((0, 0, 32, 14))
    out.alpha_composite(top, (0, 0))
    out.alpha_composite(top, (0, 6))
    out.alpha_composite(top, (0, 11))
    out.alpha_composite(leaf, (0, 16))
    op = out.load()
    cx, cy, rx, ry = 15.5, 25.0, 15.6, 24.0
    for y in range(0, 24):
        for x in range(32):
            if ((x + 0.5 - cx - 0.5) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 > 1:
                op[x, y] = CLEAR
    # outline the new dome with the canopy's darkest green
    dark = (57, 82, 0, 255)
    edge = []
    for y in range(20):
        for x in range(32):
            if op[x, y][3] and any(not (0 <= x + dx < 32 and 0 <= y + dy < 48) or op[x + dx, y + dy][3] == 0
                                   for dx, dy in ((1, 0), (-1, 0), (0, -1))):
                edge.append((x, y))
    for x, y in edge:
        op[x, y] = dark
    # a soft swamp-green shadow under the trunk instead of vanilla's teal one
    sh = (88, 120, 72, 255)
    for x in range(6, 26):
        for y in (45, 46):
            if op[x, y][3] == 0:
                op[x, y] = sh
    return out


# ---------------------------------------------------------------- greenhouse
FRAME, FRAME_D = (244, 244, 236), (176, 184, 180)
GLASS, GLASS_L, GLASS_D = (176, 216, 222), (214, 238, 240), (132, 180, 190)
LEAF, LEAF_D, LEAF_L = (96, 150, 96), (64, 112, 72), (132, 182, 112)
STONE, STONE_D = (168, 160, 148), (124, 116, 108)
OUTL = (64, 72, 76)
RED = (200, 56, 48)
BLOOM = (232, 120, 150)


def greenhouse(W=8, H=6):
    w, h = W * 16, H * 16
    im = Image.new("RGBA", (w, h), CLEAR)
    d = ImageDraw.Draw(im)
    roof_top, eave, base = 6, 46, h - 9
    # --- roof: a long glass gable seen from above, curved ends
    d.rounded_rectangle([2, roof_top, w - 3, eave], radius=10, fill=GLASS, outline=OUTL)
    # plants under the roof glass
    for cx, cy, r in ((18, 32, 9), (40, 36, 8), (64, 30, 10), (88, 36, 8), (110, 32, 9), (30, 22, 6), (98, 22, 6), (76, 40, 6)):
        d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=LEAF)
        d.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.3, cy], fill=LEAF_L)
    # glazing bars: roof panes
    for x in range(10, w - 8, 12):
        d.line([(x, roof_top + 2), (x, eave - 1)], fill=FRAME)
    for y in (roof_top + 14, roof_top + 28):
        d.line([(4, y), (w - 5, y)], fill=FRAME)
    d.line([(4, roof_top + 6), (w - 5, roof_top + 6)], fill=FRAME_D)  # ridge
    d.rectangle([4, roof_top + 4, w - 5, roof_top + 5], fill=FRAME)
    for x in range(14, w - 10, 24):  # finials on the ridge
        d.rectangle([x, roof_top - 3, x + 1, roof_top + 4], fill=FRAME)
        d.point((x, roof_top - 4), fill=OUTL)
    # glints on the glass
    for x in range(6, w - 12, 24):
        d.line([(x + 2, eave - 6), (x + 7, roof_top + 18)], fill=GLASS_L)
    d.rounded_rectangle([2, roof_top, w - 3, eave], radius=10, outline=OUTL)
    # eave/gutter
    d.rectangle([1, eave, w - 2, eave + 2], fill=FRAME)
    d.line([(1, eave + 3), (w - 2, eave + 3)], fill=FRAME_D)
    # --- front wall: glass panes with plants inside
    d.rectangle([3, eave + 4, w - 4, base], fill=GLASS_D, outline=OUTL)
    for cx in range(10, w - 6, 14):
        d.ellipse([cx - 7, base - 18, cx + 7, base + 2], fill=LEAF_D)
        d.ellipse([cx - 5, base - 22, cx + 3, base - 10], fill=LEAF)
        d.point((cx - 1, base - 18), fill=BLOOM)
        d.point((cx + 2, base - 14), fill=BLOOM)
    d.rectangle([4, eave + 5, w - 5, eave + 9], fill=GLASS)  # upper clerestory panes
    for x in range(3, w - 2, 16):
        d.rectangle([x, eave + 4, x + 1, base], fill=FRAME)
    d.line([(3, eave + 10), (w - 4, eave + 10)], fill=FRAME)
    for x in range(10, w - 6, 16):
        d.line([(x, eave + 13), (x + 3, eave + 24)], fill=GLASS_L)
    # door: double glass doors with a white portico
    dx0 = w // 2 - 9
    d.rectangle([dx0 - 2, eave + 6, dx0 + 19, base], fill=FRAME, outline=OUTL)
    d.rectangle([dx0 + 1, eave + 16, dx0 + 16, base], fill=GLASS_D, outline=OUTL)
    d.line([(dx0 + 8, eave + 16), (dx0 + 8, base)], fill=FRAME)
    d.line([(dx0 + 3, eave + 18), (dx0 + 6, base - 4)], fill=GLASS_L)
    # GYM plaque above the doors
    d.rectangle([dx0 + 1, eave + 8, dx0 + 16, eave + 14], fill=(236, 236, 236), outline=OUTL)
    font = {"G": ["111", "100", "101", "101", "111"], "Y": ["101", "101", "010", "010", "010"], "M": ["101", "111", "111", "101", "101"]}
    for i, ch in enumerate("GYM"):
        for r, row in enumerate(font[ch][:5]):
            for c, bit in enumerate(row):
                if bit == "1" and eave + 9 + r <= eave + 13:
                    d.point((dx0 + 3 + i * 4 + c, eave + 9 + r), fill=RED)
    # stone plinth
    d.rectangle([2, base + 1, w - 3, h - 2], fill=STONE, outline=OUTL)
    for x in range(8, w - 4, 12):
        d.line([(x, base + 2), (x, h - 3)], fill=STONE_D)
    d.line([(3, base + 4), (w - 4, base + 4)], fill=STONE_D)
    d.rectangle([dx0 - 2, base + 1, dx0 + 19, h - 2], fill=STONE_D)  # step at the door
    return im


# ---------------------------------------------------------------- planter (each flower its own colour)
FLOWER_RAMPS = [  # dark, mid, light
    ((168, 40, 48), (216, 72, 72), (248, 136, 128)),     # red
    ((200, 160, 40), (240, 212, 72), (255, 244, 160)),   # yellow
    ((96, 60, 150), (150, 104, 204), (204, 168, 240)),   # purple
    ((176, 176, 188), (226, 226, 234), (255, 255, 255)), # white
    ((190, 92, 32), (240, 144, 56), (255, 196, 128)),    # orange
    ((60, 92, 176), (104, 144, 224), (176, 208, 255)),   # blue
    ((176, 72, 128), (230, 124, 176), (255, 188, 220)),  # pink
]
FLOWER_SRC = {(172, 65, 82), (222, 98, 123), (255, 131, 148), (216, 200, 64), (248, 240, 96)}
PAVING = {(222, 230, 230), (197, 205, 213), (172, 189, 205), (208, 216, 232)}
PLANTER_RECOLOR = {(96, 200, 136): (104, 138, 92), (72, 152, 88): (72, 112, 66), (148, 238, 74): (150, 190, 96),
                   (80, 112, 80): (60, 92, 58)}


def planter(width=3):
    """HnS National Park planter (a tiling bed), closed with a mirrored right end, tips included."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from render import Tilesets
    ts = Tilesets("../tilesets/primary/johto_general_hns", "../tilesets/secondary/national_park_hns", "frlg")
    cols = {"L": (0x288, 0x290, 0x298), "M": (0x289, 0x291, 0x299)}
    col = lambda ids: [ts.metatile(k).convert("RGBA") for k in ids]
    left, mid = col(cols["L"]), col(cols["M"])
    right = [t.transpose(Image.FLIP_LEFT_RIGHT) for t in left]
    pieces = [left] + [mid] * (width - 2) + [right]
    im = Image.new("RGBA", (16 * width, 48), CLEAR)
    for i, c in enumerate(pieces):
        for j, t in enumerate(c):
            im.paste(t, (i * 16, j * 16))
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            c = px[x, y][:3]
            if c in PAVING:
                px[x, y] = CLEAR
            elif c in PLANTER_RECOLOR:
                px[x, y] = PLANTER_RECOLOR[c] + (255,)
    # each flower (connected blob of petal colours) gets its own colour ramp
    seen, k = set(), 0
    lum = lambda c: c[0] * 3 + c[1] * 6 + c[2]
    for y in range(H):
        for x in range(W):
            if (x, y) in seen or px[x, y][:3] not in FLOWER_SRC:
                continue
            stack, blob = [(x, y)], []
            seen.add((x, y))
            while stack:
                a, b = stack.pop()
                blob.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # 4-connected: touching flowers stay apart
                    if True:
                        n = (a + da, b + db)
                        if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and px[n][:3] in FLOWER_SRC:
                            seen.add(n)
                            stack.append(n)
            shades = sorted({px[p][:3] for p in blob}, key=lum)
            ramp = FLOWER_RAMPS[k % len(FLOWER_RAMPS)]
            k += 1
            for p in blob:
                r = shades.index(px[p][:3])
                idx = 0 if r == 0 and len(shades) > 1 else (2 if r == len(shades) - 1 else 1)
                px[p] = ramp[idx] + (255,)
    return im


# ---------------------------------------------------------------- magnolia
MAG_RECOLOR = {(57, 139, 49): (44, 100, 58), (57, 82, 0): (22, 54, 34), (131, 197, 98): (70, 132, 78),
               (180, 255, 131): (126, 180, 116)}


def magnolia():
    """Southern magnolia: the oak's form, glossy dark leaves, a pointed crown and big white blossoms."""
    im = oak()
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            if c[3] and c[:3] in MAG_RECOLOR:
                px[x, y] = MAG_RECOLOR[c[:3]] + (255,)
    # taper the crown to a rounded point
    for y in range(0, 22):
        hw = 15.6 * ((y + 2) / 24) ** 0.75
        for x in range(W):
            if abs(x + 0.5 - 16) > hw:
                px[x, y] = CLEAR
    edge = [(x, y) for y in range(22) for x in range(W)
            if px[x, y][3] and any(not (0 <= x + dx < W) or px[x + dx, y + dy][3] == 0
                                   for dx, dy in ((1, 0), (-1, 0), (0, -1)) if 0 <= y + dy)]
    for x, y in edge:
        px[x, y] = (22, 54, 34, 255)
    # blossoms: big white cups with a cream centre and a shaded base
    W_, C_, S_ = (252, 252, 246), (232, 204, 120), (206, 202, 188)
    shape = [(".", "W", "."), ("W", "C", "W"), ("S", "W", "S")]
    for bx, by in ((15, 6), (8, 12), (22, 14), (14, 20), (6, 25), (25, 25), (16, 31)):
        if not px[bx, by][3]:
            continue
        for j, row in enumerate(shape):
            for i, ch in enumerate(row):
                x, y = bx + i - 1, by + j - 1
                if ch != "." and 0 <= x < W and px[x, y][3]:
                    px[x, y] = {"W": W_, "C": C_, "S": S_}[ch] + (255,)
    return im


def save(img, name):
    out = Image.new("RGB", img.size, KEY)
    out.paste(img, (0, 0), img)
    path = os.path.join(HERE, name)
    out.save(path)
    print(path)


if __name__ == "__main__":
    save(greenhouse(10, 7), "greenhouse.png")
    save(oak(), "oak.png")
    save(magnolia(), "magnolia.png")
    save(planter(3), "planter.png")

"""Re-letter the Derby bet slips' banner: MAUVILLE DERBY -> CRESCENT DERBY (graphics/derby/betslip_bg.png, _2.png).

usage (from the decomp root): python tools/game_corner_art/make_betslip.py

The banner words are pixels in tiles that only the banner uses (tilemap rows 2-3, columns 5-12; the same tile
numbers and pixels in both slips), so the new word is painted into those tiles in place: the .bin tilemaps and the
.pal palettes are untouched. CRESCENT has as many letters as MAUVILLE. R and E are the banner font's own (copied
from DERBY); C, S, N and T are drawn to the same rules (2 px strokes, 6 px wide, 1 px gaps, the purple drop
shadow under every horizontal stroke and below the baseline).
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, ROOT, font, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

LETTER, SHADOW, BG = 1, 5, 8          # palette indices (bet_bg.pal / bet_bg_2.pal share the roles)
FONT = {
    "C": [".#####", "######", "##ssss", "##....", "##....", "##....", "######", "s#####", ".sssss"],
    "R": ["#####.", "######", "##ss##", "######", "#####s", "##s###", "##.s##", "##..##", "ss..ss"],
    "E": [".#####", "######", "##ssss", "####..", "####..", "##ss..", "######", "s#####", ".sssss"],
    "S": [".#####", "######", "##ssss", "#####.", "s#####", ".ss###", "######", "#####s", "sssss."],
    "N": ["##..##", "###.##", "######", "##s###", "##.s##", "##..##", "##..##", "##..##", "ss..ss"],
    "T": ["######", "######", "ss##ss", "..##..", "..##..", "..##..", "..##..", "..##..", "..ss.."],
}
WORD, X0, Y0, X1 = "CRESCENT", 41, 20, 96     # MAUVILLE filled x 41..96, rows 20..28 (8 rows + shadow)


def tilemap(name):
    return struct.unpack("<640H", open(os.path.join(ROOT, f"graphics/derby/{name}.bin"), "rb").read())


def reletter(name):
    path = os.path.join(ROOT, f"graphics/derby/{name}.png")
    im = Image.open(path)
    px = im.load()
    W = im.width // 8
    tm = tilemap(name)
    uses = {}
    for e in tm[:20 * 32]:
        uses[e & 0x3FF] = uses.get(e & 0x3FF, 0) + 1
    # screen pixel -> (tile, x, y) for the banner area (no flips there)
    def at(sx, sy):
        e = tm[(sy // 8) * 32 + sx // 8]
        t = e & 0x3FF
        assert not (e >> 10) & 3, "flipped banner tile"
        assert uses[t] == 1, f"tile {t:#x} is used elsewhere"
        return (t % W) * 8 + sx % 8, (t // W) * 8 + sy % 8
    for sy in range(Y0, Y0 + 9):
        for sx in range(X0, X1 + 1):
            x, y = at(sx, sy)
            px[x, y] = BG
    x = X0
    for ch in WORD:
        g = FONT[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v != ".":
                    tx, ty = at(x + i, Y0 + j)
                    px[tx, ty] = LETTER if v == "#" else SHADOW
        x += len(g[0]) + 1
    assert x - 1 <= X1 + 1
    im.save(path, bits=4)
    return im


def render(name, pal_name):
    im = Image.open(os.path.join(ROOT, f"graphics/derby/{name}.png"))
    px = im.load()
    lines = open(os.path.join(ROOT, f"graphics/derby/{pal_name}")).read().split("\n")
    pal = [tuple(int(v) for v in lines[3 + i].split()) for i in range(16)]
    W = im.width // 8
    out = Image.new("RGB", (240, 160))
    o = out.load()
    for i, e in enumerate(tilemap(name)):
        mx, my = (i % 32) * 8, (i // 32) * 8
        if mx >= 240 or my >= 160:
            continue
        t, hf, vf = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1
        tx, ty = (t % W) * 8, (t // W) * 8
        for y in range(8):
            for x in range(8):
                o[mx + x, my + y] = pal[px[tx + (7 - x if hf else x), ty + (7 - y if vf else y)] & 15]
    return out


def main():
    os.makedirs(REVIEW, exist_ok=True)
    for n in ("betslip_bg", "betslip_bg_2"):
        reletter(n)
    a, b = render("betslip_bg", "bet_bg.pal"), render("betslip_bg_2", "bet_bg_2.pal")
    out = Image.new("RGB", (240 * 3 * 2 + 60, 160 * 3 + 50), (40, 40, 48))
    d = ImageDraw.Draw(out)
    d.text((20, 12), "bet slips, re-lettered (3x): species page / stake page", fill=(230, 230, 230), font=font(16))
    out.paste(scale(a, 3), (20, 40))
    out.paste(scale(b, 3), (40 + 720, 40))
    out.save(os.path.join(REVIEW, "betslip_banner.png"))


if __name__ == "__main__":
    main()

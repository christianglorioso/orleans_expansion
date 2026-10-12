"""Draw the capsized pirogue (our own art) as a transparent 4x2-cell overlay sheet.

usage (from the decomp root): python tools/mapgen/sources/orleans_custom/make_pirogue.py
writes tools/mapgen/sources/orleans_custom/pirogue.png (64x32; transparent = magenta)
"""
import os

from PIL import Image, ImageDraw

OUT = (48, 36, 28)      # outline
RIM = (176, 144, 96)    # sunlit upper hull
HULL = (128, 96, 64)    # hull
HULLD = (96, 72, 48)    # keel line, shaded side
PAINT = (96, 128, 88)   # faded green stripe at the gunwale
PAD = (200, 168, 112)   # paddle
SHADOW = (92, 60, 52)   # cast shadow on the mud
KEY = (255, 0, 255)


def lens(W, H):
    """Half-height of a pointed pirogue outline at each column."""
    return [H / 2 * (1 - abs(2 * (x + 0.5) / W - 1) ** 2.2) ** 0.55 for x in range(W)]


def hull(W=50, H=9, side=3):
    im = Image.new('RGBA', (W, H + side + 2), (0, 0, 0, 0))
    px = im.load()
    hh = lens(W, H)
    cy = H / 2
    for x in range(W):
        top, bot = round(cy - hh[x]), round(cy + hh[x])
        if bot - top < 1:
            continue
        for y in range(top, bot):
            px[x, y] = (RIM if y < cy - 1 else HULL) + (255,)
        px[x, round(cy) - 1] = HULLD + (255,)
        for y in range(bot, bot + side):
            px[x, y] = (PAINT if y == bot else HULLD) + (255,)
    return outline(im)


def paddle(L=18):
    im = Image.new('RGBA', (L + 2, 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(1, 3), (L - 6, 3)], fill=PAD + (255,))
    d.rectangle([L - 6, 1, L, 5], fill=PAD + (255,), outline=OUT + (255,))
    return outline(im)


def outline(im):
    px = im.load()
    W, H = im.size
    big = Image.new('RGBA', (W + 2, H + 2), (0, 0, 0, 0))
    bp = big.load()
    for y in range(H):
        for x in range(W):
            if px[x, y][3]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    bp[x + 1 + dx, y + 1 + dy] = OUT + (255,)
    big.alpha_composite(im, (1, 1))
    return big


def main():
    sheet = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    h = hull()
    hx, hy = 6, 5
    # cast shadow: the hull's footprint shifted down-right, under the hull itself
    a = h.split()[3]
    sh = Image.new('RGBA', h.size, SHADOW + (255,))
    sheet.paste(sh, (hx + 2, hy + 2), a)
    sheet.alpha_composite(h, (hx, hy))
    p = paddle()
    sheet.alpha_composite(p, (hx + 13, hy + 16))
    out = Image.new('RGB', sheet.size, KEY)
    out.paste(sheet, (0, 0), sheet)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pirogue.png')
    out.save(path)
    print(path)


if __name__ == '__main__':
    main()

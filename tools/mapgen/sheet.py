"""Review sheet: mockup-vs-build comparison images stacked into one PNG.

usage (from tools/mapgen): python sheet.py <out.png> <title> <key> [key ...]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))


def main(out, title, keys, width=2400):
    ims = []
    for k in keys:
        im = Image.open(os.path.join(HERE, "maps", f"{k}_compare.png")).convert("RGB")
        ims.append((k, im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)))
    try:
        font = ImageFont.truetype("arial.ttf", 34)
        big = ImageFont.truetype("arialbd.ttf", 48)
    except OSError:
        font = big = ImageFont.load_default()
    H = 90 + sum(im.height + 60 for _, im in ims)
    sheet = Image.new("RGB", (width, H), (250, 247, 240))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, width, 80], fill=(47, 72, 60))
    d.text((24, 14), title, fill="white", font=big)
    y = 90
    for k, im in ims:
        d.text((16, y + 8), k.replace("_", " ").title(), fill=(47, 72, 60), font=font)
        sheet.paste(im, (0, y + 56))
        y += im.height + 60
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

"""Derby species-name bitmaps DODUO and DODRIO (graphics/derby/species_name/name-doduo.png, name-dodrio.png).

usage (from the decomp root): python tools/game_corner_art/make_names.py

64 x 32, indexed, the palette and index order of the fork's name bitmaps (0 = clear, 1 = dark purple outline and
shadow, 2 = cream letter). The lettering is the fork's own: D, O, R and I are copied pixel for pixel from the old
RAPIDASH / PONYTA bitmaps (kept below as strings so this script does not depend on the placeholders it replaces);
U, which the fork never drew, is built from its H stems and O bowl. Same placement as name-rattata / name-feebas:
left-aligned, letters on rows 12-19, 8 px advance (I is 7 wide, as in RAPIDASH).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, Ix, font, rgb, save_indexed, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

PAL = [(150, 255, 231), (80, 8, 120), (255, 255, 231)] + [(0, 0, 0)] * 13
GLYPHS = {
    "D": ['222221..', '2211221.', '221.1221', '221..221', '221..221', '221.2211', '2222211.', '111111..'],
    "O": ['.222221.', '22111221', '221..221', '221..221', '221..221', '221..221', '12222211', '.111111.'],
    "R": ['2222221.', '22111221', '221..221', '221.2221', '22222111', '2212221.', '22112221', '111.1111'],
    "I": ['2222221', '1122111', '..221..', '..221..', '..221..', '..221..', '2222221', '1111111'],
    "U": ['221..221'] * 6 + ['12222211', '.111111.'],
}


def word(text, top=12):
    cv = Ix(64, 32)
    x = 0
    for ch in text:
        g = GLYPHS[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v != ".":
                    cv.put(x + i, top + j, int(v))
        x += len(g[0])
    assert x <= 64, text
    return cv


def main():
    os.makedirs(REVIEW, exist_ok=True)
    out = []
    for name in ("DODUO", "DODRIO"):
        im = word(name).image(PAL)
        save_indexed(im, f"graphics/derby/species_name/name-{name.lower()}.png")
        out.append((name, im))
    for other in ("rattata", "feebas"):
        out.append((other.upper() + " (fork)", Image.open(os.path.join(
            os.path.dirname(HERE), "..", "graphics", "derby", "species_name", f"name-{other}.png"))))
    k = 6
    sheet = Image.new("RGB", (64 * k + 40, len(out) * (32 * k + 30) + 10), (40, 40, 48))
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(out):
        y = 10 + i * (32 * k + 30)
        d.text((20, y), n, fill=(230, 230, 230), font=font(16))
        sheet.paste(scale(rgb(im), k), (20, y + 22))
    sheet.save(os.path.join(REVIEW, "names_preview.png"))


if __name__ == "__main__":
    main()

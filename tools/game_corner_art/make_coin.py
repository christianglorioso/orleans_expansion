"""A coin glyph in place of the money sign on the coin stakes: the Derby bet slip's "P10" stake sprite
(graphics/derby/10p.png, both blink frames) and the Blackjack "+P10" / "-P10" buttons (graphics/blackjack/option_1.png,
option_2.png). The stakes are Game Corner coins, not money.

usage (from the decomp root): python tools/game_corner_art/make_coin.py

Each sprite keeps its palette and every pixel outside the glyph's box; the coin uses the colours the runtime palette
already has (10p.png draws with PAL_DIGITS = graphics/derby/digits.pal; the buttons with cursor.pal):
    bet slip : a cream token with a grey rim and stamped ring, the digits' salmon shading on its lower right
    Blackjack: a gold coin (the cursor palette's two golds) with a white glint and the buttons' rust drop shadow
option_3.png (BET / DOUBLE / INSURE) has no money sign and is left alone.
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, ROOT, font, rgb, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# 10p.png (digits.pal: 1 grey, 2 light grey, 3 cream, 4 salmon)
TOKEN = ["..1111..",
         ".133331.",
         "13322331",
         "13233231",
         "13233231",
         "13322331",
         "41333314",
         ".441144.",
         "..4444.."]
# option_1/2 (cursor.pal: 5 deep gold, D light gold, E white, 2 rust shadow)
COIN = [".DD..",
        "DEDD.",
        "DD552",
        "D5D52",
        "D5D52",
        "D5552",
        ".5522",
        "..22."]


def original(path):
    """The sprite as committed before this script touched it (so re-running is idempotent)."""
    rel = path.replace(os.sep, "/")
    log = subprocess.run(["git", "log", "--format=%H", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for h in log:  # newest first: take the newest version that still has the money sign (no coin yet)
        blob = subprocess.run(["git", "show", f"{h}:{rel}"], cwd=ROOT, capture_output=True).stdout
        im = Image.open(io.BytesIO(blob))
        im.load()
        if not getattr(im, "text", {}).get("orleans_coin"):
            return im
    return Image.open(os.path.join(ROOT, path))


def stamp(im, glyph, x0, y0, clear_box):
    px = im.load()
    bx0, by0, bx1, by1 = clear_box
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            px[x, y] = 0
    for j, row in enumerate(glyph):
        for i, v in enumerate(row):
            if v != ".":
                px[x0 + i, y0 + j] = int(v, 16)


def save(im, rel):
    from PIL import PngImagePlugin
    meta = PngImagePlugin.PngInfo()
    meta.add_text("orleans_coin", "1")
    im.save(os.path.join(ROOT, rel), bits=4, pnginfo=meta)


def main():
    os.makedirs(REVIEW, exist_ok=True)
    shots = []
    # Derby: the sign sat at x 11..16, rows 2..12 (frame 1) and 18..28 (frame 2); digits start at x 20
    rel = "graphics/derby/10p.png"
    im = original(rel).copy()
    before = im.copy()
    for oy in (0, 16):
        stamp(im, TOKEN, 11, 3 + oy, (11, 2 + oy, 17, 13 + oy))
    save(im, rel)
    shots.append(("10p.png (bet slip stake, 2 frames)", before, im, (167, 255, 255)))
    # Blackjack: the sign sat at x 8..12, rows 3..10, between the +/- (x 2..7) and the 10 (x 14..)
    for n in (1, 2):
        rel = f"graphics/blackjack/option_{n}.png"
        im = original(rel).copy()
        before = im.copy()
        stamp(im, COIN, 8, 3, (8, 3, 13, 10))  # 5 wide: a clear column before the 10
        save(im, rel)
        shots.append((f"option_{n}.png (Blackjack)", before, im, (24, 24, 32)))
    k = 8
    out = Image.new("RGB", (2 * 32 * k + 80, len(shots) * (48 * k + 40) + 20), (40, 40, 48))
    d = ImageDraw.Draw(out)
    y = 10
    for lab, a, b, bg in shots:
        d.text((20, y), lab + "   before | after", fill=(230, 230, 230), font=font(16))
        out.paste(scale(rgb(a, bg), k), (20, y + 24))
        out.paste(scale(rgb(b, bg), k), (40 + 32 * k, y + 24))
        y += a.height * k + 40
    out.crop((0, 0, out.width, y)).save(os.path.join(REVIEW, "coin_glyph.png"))


if __name__ == "__main__":
    main()

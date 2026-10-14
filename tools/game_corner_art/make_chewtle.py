"""Derby race sprite and name plate for Chewtle, the slow turtle racer (graphics/derby/chewtle_ow.png,
graphics/derby/species_name/name-chewtle.png), plus the review sheet tile_review/game_corner/chewtle_mock.png.

usage (from the decomp root): python tools/game_corner_art/make_chewtle.py

Race sprite: 32 x 32 indexed PNG, two 32x16 frames of a plodding walk stacked top to bottom, the sheet layout of
rattata_ow.png / feebas_ow.png (CompressedSpriteSheet size 0x200 = 2 frames x 8 tiles x 32 bytes, OAM 32x16, anim
frames at tile 0 and 8). It faces LEFT like every racer (src/derby.c moves racers towards smaller x). The pixels are
indices into Chewtle's own graphics/pokemon/chewtle/normal.pal, which is also the PNG's palette, so shiny.pal works
through the same indices (it keeps the colour roles):
    1 horn edge  2 horn  4 horn shade / cheek    3 skin dark  6 skin mid  5 skin light   7 black  8 white
    9 shell edge  a shell blue  d shell shade  b shell rim  c shell pattern   e plastron  f plastron shade
Drawn by hand from the front sprite (anim_front.png) and the side frames of overworld.png: tall round head with
the yellow horn, orange cheek disc, wide snapping jaw with a white tooth, a low blue shell with the orange-brown rim
and dark-brown scutes, a cream plastron, stubby clawed legs and a short tail. Frame 1 is the stride (legs spread,
body a pixel lower; it is also the standing pose), frame 2 the gather (legs under the body, body up), so the
two-frame loop reads as a heavy plod. Feet are on the bottom row in both frames.

Name plate: 64 x 32, the palette, index order and lettering of make_names.py (0 clear, 1 dark purple outline and
shadow, 2 cream letter; rows 12-19, 8 px advance). C, H, W and L are new glyphs built from the fork's stems,
bowls and bars in the same 3-px-stroke style; E and T are the fork's own (from FEEBAS / RATTATA). W is 9 wide and
T 7, so CHEWTLE is 56 px wide.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, ROOT, Ix, font, read_pal, rgb, save_indexed, scale  # noqa: E402
from make_names import GLYPHS as FORK_GLYPHS, PAL as NAME_PAL  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# ------------------------------------------------------------------------------------------------ race sprite
# body without legs, 32 wide; '.' = clear, hex digit = normal.pal index
BODY = [
    # head (x 1-15), shell (x 16-28), tail (x 29-31)
    #         1111111111222222222233
    # 34567890123456789012345678901
    "........1",                                      # 0  horn tip
    ".......121",                                     # 1
    "......12241",                                    # 2
    "....3312244133",                                 # 3  horn base on the crown
    "...355555555553",                                # 4
    "..35555555555663" "..99999999",                  # 5  shell top
    ".353355555556663" "99aaaaaadd99",                # 6  brow
    ".35785555511666" "3" "aaaacbbcaddd9",            # 7  eye, cheek disc, central scute
    ".75555555124166" "3" "aaacbbbbcddd9",            # 8
    ".77777773144166" "3" "dadacbbcadcd9",            # 9  mouth line
    "..7855555511666" "3" "ddcddccddcdd9",            # 10 tooth
    "..73355556666666" "cbbbbbbbbbbbc" "37",          # 11 lower jaw, shell rim, tail
    "...7777777333333" "eeffeeeffeeef" "667",         # 12 chin, plastron, tail
]
BODY = [r.ljust(32, ".") for r in BODY]
assert all(len(r) == 32 for r in BODY), [len(r) for r in BODY]
BODY_H = len(BODY)

# legs under the body: (x, rows), far legs (dark) first, then the near ones (light skin, white claws); the last
# row is the foot, always on the sprite's bottom row. Frame 1 is the stride (legs spread, body a pixel lower),
# frame 2 the gather (legs under the body, body up), so the plod bobs.
STEP = {
    0: (1, [(15, ["337", "777"]), (20, ["337", "777"]),
            (9, [".3667", "7887"]), (24, ["3667", ".7887"])]),
    1: (0, [(9, ["337", "337", "777"]), (25, ["337", "337", "777"]),
            (12, ["3667", "3667", "7887"]), (21, ["3667", "3667", "7887"])]),
}


def frame(f):
    cv = Ix(32, 16)
    bob, legs = STEP[f]
    for y, row in enumerate(BODY):
        for x, ch in enumerate(row):
            if ch != ".":
                cv.put(x, y + bob, int(ch, 16))
    for lx, stamp in legs:
        for j, row in enumerate(stamp):
            for i, ch in enumerate(row):
                if ch != ".":
                    cv.put(lx + i, BODY_H + bob + j, int(ch, 16))
    return cv


def sheet():
    out = Ix(32, 32)
    for f in range(2):
        out.paste(frame(f), 0, f * 16)
    return out


# ------------------------------------------------------------------------------------------------ name plate
GLYPHS = dict(FORK_GLYPHS)
GLYPHS.update({
    # E and T copied from the fork's FEEBAS / RATTATA bitmaps; C from the O bowl; H and L from the E / D stems;
    # W is three stems joined at the foot, 9 wide.
    "C": ['.222221.', '22111221', '221..111', '221.....', '221.....', '221..221', '12222211', '.111111.'],
    "H": ['221..221', '221..221', '221..221', '22222221', '22111221', '221..221', '221..221', '111..111'],
    "E": ['22222221', '22111111', '221.....', '2222221.', '2211111.', '221.....', '22222221', '11111111'],
    "W": ['221...221', '221...221', '221.21221', '221221221', '221221221', '221221221', '122222211', '.1111111.'],
    "T": ['2222221', '1122111', '..221..', '..221..', '..221..', '..221..', '..221..', '..111..'],
    "L": ['221.....', '221.....', '221.....', '221.....', '221.....', '221.....', '22222221', '11111111'],
})


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


# ------------------------------------------------------------------------------------------------ review mock
TRACK = (200, 192, 152)
INK = (230, 230, 230)
NEW = (255, 220, 120)
RACERS = [("chewtle", 16), ("doduo", 32), ("rattata", 16), ("feebas", 16)]


def frames_of(path, pal, fh):
    """The frames of a racer sheet as RGB images, drawn by index with `pal` (as the race screen does)."""
    im = Image.open(os.path.join(ROOT, path))
    px = im.load()
    out = []
    for f in range(im.height // fh):
        fr = Image.new("RGB", (im.width, fh), TRACK)
        o = fr.load()
        for y in range(fh):
            for x in range(im.width):
                v = px[x, f * fh + y] & 15
                if v:
                    o[x, y] = pal[v]
        out.append(fr)
    return out


def race_strip():
    """The race screen (3x) with Chewtle in the field, built with make_mocks' helpers."""
    import make_mocks as mm
    sc = mm.bg("graphics/derby/race_bg.png", "graphics/derby/race_bg.bin", "graphics/derby/racetrack_bg.pal")
    field = [("doduo", 150, 0, False, 32), ("chewtle", 196, 0, False, 16), ("rattata", 170, 0, False, 16),
             ("doduo", 132, 2, True, 32), ("chewtle", 204, 1, True, 16), ("dodrio", 96, 2, False, 32)]
    for k, (sp, x, fr, shiny, h) in enumerate(field):
        pal = f"graphics/pokemon/{sp}/{'shiny' if shiny else 'normal'}.pal"
        mm.sprite(sc, f"graphics/derby/{sp}_ow.png", pal, x, (48 if h == 32 else 56) + 16 * k, 32, h, fr)
    return sc


def mock():
    k = 4
    col = 32 * k + 24
    sec_h = 24 + 3 * (32 * k + 8)                  # tallest column: Doduo's three 32x32 frames
    names = ["chewtle", "doduo", "dodrio", "rattata", "feebas"]
    race = race_strip()
    W = 30 + 90 + 4 * col + 20 + 240 * 3 + 30
    H = 70 + 2 * sec_h + 30 + 40 + 32 * k + 30
    out = Image.new("RGB", (W, H), (40, 40, 48))
    d = ImageDraw.Draw(out)
    d.text((30, 12), "Chewtle Derby racer: chewtle_ow.png (2 frames, 32x16) and name-chewtle.png, beside the other racers",
           fill=INK, font=font(20))
    d.text((30, 40), "4x. Racers drawn by index with graphics/pokemon/<species>/normal.pal / shiny.pal on the track "
           "colour; they face left (run towards smaller x). Frame numbers top-left.", fill=(190, 190, 200), font=font(13))
    y0 = 70
    for pi, palname in enumerate(("normal", "shiny")):
        y = y0 + pi * sec_h
        d.text((30, y + 24), palname, fill=INK, font=font(18))
        x = 120
        for sp, fh in RACERS:
            pal = read_pal(f"graphics/pokemon/{sp}/{palname}.pal")
            d.text((x, y), sp + ("  (new)" if sp == "chewtle" else ""), fill=NEW if sp == "chewtle" else INK, font=font(15))
            yy = y + 24
            for i, fr in enumerate(frames_of(f"graphics/derby/{sp}_ow.png", pal, fh)):
                out.paste(scale(fr, k), (x, yy))
                d.text((x + 3, yy + 1), str(i + 1), fill=(90, 80, 60), font=font(11))
                yy += fh * k + 8
            x += col
    # name plates, with the bet slip's text palette
    tp = read_pal("graphics/derby/bet_text.pal")
    y = y0 + 2 * sec_h + 10
    d.text((30, y), "name plates (64x32, bet_text.pal), 4x", fill=INK, font=font(16))
    x = 30
    for n in names:
        im = Image.open(os.path.join(ROOT, f"graphics/derby/species_name/name-{n}.png"))
        im = im.copy()
        flat = [v for c in tp for v in c]
        im.putpalette(flat + [0] * (768 - len(flat)))
        d.text((x, y + 24), n + ("  (new)" if n == "chewtle" else ""), fill=NEW if n == "chewtle" else INK, font=font(13))
        out.paste(scale(rgb(im), k), (x, y + 44))
        x += 64 * k + 12
    # race screen in context
    rx = 120 + 4 * col + 20
    d.text((rx, y0), "race screen, 3x (Chewtle normal, frame 1, and shiny, frame 2)", fill=INK, font=font(15))
    out.paste(scale(race, 3), (rx, y0 + 24))
    return out


def main():
    os.makedirs(REVIEW, exist_ok=True)
    pal = read_pal("graphics/pokemon/chewtle/normal.pal")
    save_indexed(sheet().image(pal), "graphics/derby/chewtle_ow.png")
    save_indexed(word("CHEWTLE").image(NAME_PAL), "graphics/derby/species_name/name-chewtle.png")
    mock().save(os.path.join(REVIEW, "chewtle_mock.png"))


if __name__ == "__main__":
    main()

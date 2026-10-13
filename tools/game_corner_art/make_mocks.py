"""Screen mocks for the Game Corner art review: the Derby bet slip (species page for Doduo and Dodrio, stake page
with the coin), and the race screen with the new racers. Built from the real files in graphics/ and the sprite
positions in src/derby.c (sprite x, y are centres), at 3x. Writes tile_review/game_corner/mock_betslip.png and
mock_race.png.

usage (from the decomp root): python tools/game_corner_art/make_mocks.py
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, ROOT, font, read_pal, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

G = lambda p: os.path.join(ROOT, p)  # noqa: E731


def bg(png, binf, pal):
    im = Image.open(G(png))
    px = im.load()
    P = read_pal(pal)
    W = im.width // 8
    tm = struct.unpack("<640H", open(G(binf), "rb").read())
    out = Image.new("RGB", (240, 160))
    o = out.load()
    for i, e in enumerate(tm):
        mx, my = (i % 32) * 8, (i // 32) * 8
        if mx >= 240 or my >= 160:
            continue
        t, hf, vf = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1
        tx, ty = (t % W) * 8, (t // W) * 8
        if ty >= im.height:
            continue
        for y in range(8):
            for x in range(8):
                o[mx + x, my + y] = P[px[tx + (7 - x if hf else x), ty + (7 - y if vf else y)] & 15]
    return out


def sprite(screen, png, pal, cx, cy, w, h, frame=0):
    """Draw a w x h frame (frames stacked vertically) centred at cx, cy with the runtime palette."""
    im = Image.open(G(png))
    px = im.load()
    P = read_pal(pal)
    x0, y0 = cx - w // 2, cy - h // 2
    s = screen.load()
    for y in range(h):
        for x in range(w):
            v = px[x, frame * h + y] & 15
            if v and 0 <= x0 + x < 240 and 0 <= y0 + y < 160:
                s[x0 + x, y0 + y] = P[v]


def betslip(species):
    sc = bg("graphics/derby/betslip_bg.png", "graphics/derby/betslip_bg.bin", "graphics/derby/bet_bg.pal")
    sprite(sc, "graphics/derby/pokemon_ui/ui-1.png", "graphics/derby/betmenu_interface.pal", 64, 64, 64, 32)
    y = 88 if species == "dodrio" else 96
    sprite(sc, f"graphics/pokemon/{species}/anim_front.png", f"graphics/pokemon/{species}/normal.pal", 64, y, 64, 64)
    sprite(sc, f"graphics/derby/species_name/name-{species}.png", "graphics/derby/bet_text.pal", 164, 60, 64, 32)
    sprite(sc, "graphics/derby/condition/condition-1.png", "graphics/derby/condition.pal", 164, 93, 64, 32)
    return sc


def stake():
    sc = bg("graphics/derby/betslip_bg_2.png", "graphics/derby/betslip_bg_2.bin", "graphics/derby/bet_bg_2.pal")
    sprite(sc, "graphics/pokemon/dodrio/anim_front.png", "graphics/pokemon/dodrio/normal.pal", 64, 88, 64, 64)
    sprite(sc, "graphics/derby/10p.png", "graphics/derby/digits.pal", 172, 80, 32, 16)
    return sc


def race():
    sc = bg("graphics/derby/race_bg.png", "graphics/derby/race_bg.bin", "graphics/derby/racetrack_bg.pal")
    field = [("doduo", 150, 0, False), ("dodrio", 118, 1, False), ("rattata", 170, 0, False),
             ("doduo", 132, 2, True), ("feebas", 210, 0, False), ("dodrio", 96, 2, True)]
    for k, (sp, x, fr, shiny) in enumerate(field):
        pal = f"graphics/pokemon/{sp}/{'shiny' if shiny else 'normal'}.pal"
        if sp in ("doduo", "dodrio"):
            sprite(sc, f"graphics/derby/{sp}_ow.png", pal, x, 48 + 16 * k, 32, 32, fr)
        else:
            sprite(sc, f"graphics/derby/{sp}_ow.png", pal, x, 56 + 16 * k, 32, 16, 0)
    return sc


def sheet(title, shots, name):
    k = 3
    W = max(len(shots) * (240 * k + 20) + 20, 1500)
    out = Image.new("RGB", (W, 160 * k + 70), (40, 40, 48))
    d = ImageDraw.Draw(out)
    d.text((20, 10), title, fill=(230, 230, 230), font=font(18))
    for i, (lab, sc) in enumerate(shots):
        x = 20 + i * (240 * k + 20)
        d.text((x, 38), lab, fill=(200, 200, 210), font=font(14))
        out.paste(scale(sc, k), (x, 60))
    out.save(os.path.join(REVIEW, name))


def main():
    os.makedirs(REVIEW, exist_ok=True)
    sheet("Derby bet slip mock (3x): CRESCENT DERBY banner, DODUO / DODRIO names, coin on the stake",
          [("species page: Doduo", betslip("doduo")), ("species page: Dodrio", betslip("dodrio")),
           ("stake page: the coin stake", stake())], "mock_betslip.png")
    sheet("Derby race mock (3x): racers run right to left (x decreases in derby.c); Doduo and Dodrio on their own "
          "palettes, a shiny of each", [("mid-race (Rattata and Feebas as the game draws them now: their PNGs are indexed to "
                                       "their own palettes, not the species palettes derby.c loads - not part of this commission)",
                                       race())], "mock_race.png")


if __name__ == "__main__":
    main()

"""Derby race sprites for Doduo and Dodrio (graphics/derby/doduo_ow.png, dodrio_ow.png).

usage (from the decomp root): python tools/game_corner_art/make_racers.py [--preview]

32 x 96 indexed PNGs: three 32x32 frames of a run cycle, top to bottom, drawn in the style of the fork's race
sprites (Ponyta / Rapidash: GBA overworld size, dark outline, feet on the bottom row). They face LEFT: the race code
moves every racer towards smaller x (src/derby.c, DERBY_STATE_RACE_*: x -= speed / 2, finishing at x <= 16), and the
fork's horses and Rattata face left too. Indices are the species' own palette (graphics/pokemon/<species>/normal.pal;
shiny.pal keeps the colour roles), which the race screen loads once the placeholder palette table is removed.
Frame 1 doubles as the standing pose.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gc_kit import REVIEW, Ix, font, read_pal, rgb, save_indexed, scale  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# ---------------------------------------------------------------- Doduo (normal.pal indices; 1-4 are unused there)
D_B1, D_B2, D_B3, D_B4 = 5, 6, 7, 8          # body: light, mid, shade, dark brown
D_C1, D_C2, D_C3, D_C4 = 9, 10, 11, 12       # beak / legs: cream light, mid, dark, olive-dark
D_GR, D_BK, D_WH = 13, 14, 15                # grey, black, white


def body_shade(b1, b2, b3, b4, tex=True):
    def f(x, y, nx, ny):
        d = nx * 0.55 + ny * 0.8           # light from the upper left
        c = b1 if d < -0.45 else b2 if d < 0.35 else b3
        if tex and c == b2 and (x * 3 + y * 5) % 7 == 0:
            c = b3                          # a few feather flecks
        if tex and c == b1 and (x + y * 2) % 5 == 0:
            c = b2
        return c
    return f


def leg(cv, hip, knee, foot, c, cd, toe_dir=-1, lifted=False):
    """A thin bird leg: thigh-knee-shank in c with a darker back edge, three toes at the foot."""
    cv.line(hip[0], hip[1], knee[0], knee[1], c, 2)
    cv.line(knee[0], knee[1], foot[0], foot[1], c)
    cv.line(knee[0] + 1, knee[1], foot[0] + 1, foot[1], cd)
    fx, fy = foot
    if lifted:      # toes curled under
        cv.put(fx - 1, fy + 1, c)
        cv.put(fx + 1, fy + 1, c)
        cv.put(fx, fy + 1, cd)
    else:           # toes spread on the ground: two forward, one back
        for i in range(1, 4):
            cv.put(fx + toe_dir * i, fy, c)
        cv.put(fx - toe_dir, fy, c)
        cv.put(fx + toe_dir * 3, fy, cd)


def head(cv, cx, cy, r, shade, beak, eye_dx=-1):
    """A round head (r ~ 3) with a long beak to the left: beak = (light, mid, dark, line)."""
    cv.ellipse(cx, cy, r, r, None, shade)
    bl, bm, bd, bline = beak
    x0 = int(cx - r) + 1
    L = int(r) + 3
    for i in range(L):
        x = x0 - i
        cv.put(x, cy - 1 + (1 if i > L - 2 else 0), bl if i < L - 1 else bm)
        if i < L - 2:
            cv.put(x, cy, bm)
        if i < L - 3:
            cv.put(x, cy + 1, bd)
    cv.put(x0 - L + 1, cy, bline)


def eye(cv, x, y, black, white):
    cv.put(x, y, black)
    cv.put(x, y - 1, white)


def neck(cv, root, hx, hy, dark, light):
    cv.line(root[0], root[1], hx + 1, hy + 2, dark, 2)
    cv.line(root[0] - 1, root[1], hx, hy + 2, light, 1)


def doduo(f):
    cv = Ix(32, 32)
    bob = [0, -1, 0][f]
    near_b, far_b = [(1, 0), (0, 0), (0, 1)][f]   # the two heads bob out of step
    # legs behind the body first
    if f == 0:
        leg(cv, (21, 25), (24, 28), (26, 29), D_C2, D_C3, lifted=True)        # back leg kicking up behind
    elif f == 1:
        leg(cv, (21, 25 + bob), (22, 28), (21, 29), D_C2, D_C3, lifted=True)  # back leg tucked, passing
    else:
        leg(cv, (21, 25), (23, 28), (25, 31), D_C2, D_C3)                     # back leg pushing off
    # tail tuft and body
    cv.poly([(26, 16 + bob), (30, 14 + bob), (29, 18 + bob), (27, 20 + bob)], D_B3)
    cv.put(29, 15 + bob, D_B2)
    hx, hy = 18, 5 + bob + far_b
    ax, ay = 9, 10 + bob + near_b
    neck(cv, (21, 18 + bob), hx, hy, D_BK, D_GR)     # the necks rise from inside the body
    neck(cv, (18, 20 + bob), ax, ay, D_BK, D_GR)
    cv.ellipse(20, 20 + bob, 7.5, 6.5, None, body_shade(D_B1, D_B2, D_B3, D_B4))
    # front leg over the body's lower edge
    if f == 0:
        leg(cv, (18, 25), (16, 28), (14, 31), D_C1, D_C3)
    elif f == 1:
        leg(cv, (18, 25 + bob), (18, 28), (18, 31), D_C1, D_C3)
    else:
        leg(cv, (18, 25), (15, 28), (12, 29), D_C1, D_C3, lifted=True)
    # black necks, the far head first
    head(cv, hx, hy, 3.2, body_shade(D_B2, D_B2, D_B3, D_B4, tex=False), (D_C2, D_C3, D_C3, D_C4))
    eye(cv, hx - 1, hy - 1, D_BK, D_WH)
    head(cv, ax, ay, 3.4, body_shade(D_B1, D_B2, D_B3, D_B4, tex=False), (D_C1, D_C2, D_C3, D_C4))
    eye(cv, ax - 1, ay - 1, D_BK, D_WH)
    cv.outline(D_B4, only={D_B1, D_B2, D_B3})
    cv.outline(D_BK)
    return cv


# ---------------------------------------------------------------- Dodrio (normal.pal indices)
R_B1, R_B2, R_B3, R_B4 = 1, 2, 3, 4          # body browns
R_C1, R_C2, R_C3 = 5, 6, 7                   # cream beak / legs
R_P1, R_P2, R_P3 = 8, 9, 10                  # pink tail / mouth
R_G1, R_G2, R_G3 = 11, 12, 13                # greys: neck, crests, lower body
R_BK, R_WH = 14, 15


def crest(cv, x, y, c1, c2):
    """Dodrio's two black head plumes, swept back."""
    cv.line(x, y, x + 3, y - 3, c1)
    cv.line(x + 2, y, x + 5, y - 2, c2)


def dodrio(f):
    cv = Ix(32, 32)
    bob = [0, -1, 0][f]
    nb, mb, fb = [(1, 0, 0), (0, 0, 1), (0, 1, 0)][f]
    if f == 0:
        leg(cv, (22, 24), (25, 27), (28, 28), R_C2, R_C3, lifted=True)
    elif f == 1:
        leg(cv, (22, 24 + bob), (23, 27), (22, 29), R_C2, R_C3, lifted=True)
    else:
        leg(cv, (22, 24), (25, 28), (27, 31), R_C2, R_C3)
    # pink tail feathers
    cv.poly([(27, 15 + bob), (31, 10 + bob), (31, 15 + bob), (29, 19 + bob)], R_P2)
    cv.line(28, 15 + bob, 31, 11 + bob, R_P1)
    cv.line(29, 18 + bob, 31, 15 + bob, R_P3)

    # body: brown above, dark grey below
    def shade(x, y, nx, ny):
        if ny > 0.3:
            return R_G2 if (ny < 0.55 and (x * 2 + y) % 4 == 0) else R_G3
        return body_shade(R_B1, R_B2, R_B3, R_B4)(x, y, nx, ny)
    heads = [(25, 5 + bob + fb, (24, 15 + bob), (R_B2, R_B2, R_B3, R_B4)),
             (15, 5 + bob + mb, (21, 15 + bob), (R_B1, R_B2, R_B3, R_B4)),
             (7, 12 + bob + nb, (17, 18 + bob), (R_B1, R_B2, R_B3, R_B4))]
    for hx, hy, root, _ in heads:      # the necks rise from inside the body
        neck(cv, root, hx, hy, R_G3, R_G2)
    cv.ellipse(21, 18 + bob, 8.5, 7.0, None, shade)
    if f == 0:
        leg(cv, (18, 24), (15, 28), (12, 31), R_C1, R_C3)
    elif f == 1:
        leg(cv, (18, 24 + bob), (18, 28), (18, 31), R_C1, R_C3)
    else:
        leg(cv, (18, 24), (14, 27), (11, 28), R_C1, R_C3, lifted=True)
    # three necks (dark grey) and heads, far to near
    for k, (hx, hy, root, light) in enumerate(heads):
        crest(cv, hx + 1, hy - 2, R_BK, R_G3)
        head(cv, hx, hy, 3.0, body_shade(*light, tex=False), (R_C1, R_C2, R_C3, R_C3))
        eye(cv, hx - 1, hy - 1, R_BK, R_WH)
        if k == 2 and f != 1:   # the near head calls out: open beak, pink mouth
            x0 = int(hx - 3) + 1
            cv.put(x0 - 1, hy, R_P2)
            cv.put(x0 - 2, hy, R_P3)
    cv.outline(R_B4, only={R_B1, R_B2, R_B3})
    cv.outline(R_BK)
    return cv


def sheet(fn):
    out = Ix(32, 96)
    for f in range(3):
        out.paste(fn(f), 0, f * 32)
    return out


def main():
    os.makedirs(REVIEW, exist_ok=True)
    made = {}
    for name, fn in (("doduo", doduo), ("dodrio", dodrio)):
        pal = read_pal(f"graphics/pokemon/{name}/normal.pal")
        shiny = read_pal(f"graphics/pokemon/{name}/shiny.pal")
        cv = sheet(fn)
        im = cv.image(pal)
        save_indexed(im, f"graphics/derby/{name}_ow.png")
        made[name] = (im, cv.image(shiny))
    # preview: both palettes, 6x, on the racetrack colour
    k = 6
    W = 4 * (32 * k + 20) + 20
    out = Image.new("RGB", (W, 96 * k + 60), (40, 40, 48))
    d = ImageDraw.Draw(out)
    x = 20
    for name, (n, s) in made.items():
        for lab, im in (("normal", n), ("shiny", s)):
            d.text((x, 10), f"{name}_ow.png  {lab}", fill=(230, 230, 230), font=font(16))
            out.paste(scale(rgb(im, (200, 192, 152)), k), (x, 40))
            x += 32 * k + 20
    out.save(os.path.join(REVIEW, "racers_preview.png"))


if __name__ == "__main__":
    main()

"""Small shared kit for the Game Corner art scripts: an indexed pixel canvas, .pal / .png I/O and preview helpers.

Every script here writes the final indexed PNG straight into graphics/ (the files the Game Corner port loads), keeps
the target palette exactly, and draws previews/mocks under tile_review/game_corner/.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
REVIEW = os.path.join(os.path.dirname(ROOT), "tile_review", "game_corner")


def read_pal(path):
    """JASC .pal -> list of 16 RGB tuples."""
    lines = open(os.path.join(ROOT, path)).read().split("\n")
    n = int(lines[2])
    return [tuple(int(v) for v in lines[3 + i].split()) for i in range(n)][:16]


class Ix:
    """An indexed canvas; None = transparent (index 0)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[None] * w for _ in range(h)]

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if c is not None and 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.p[y][x]
        return None

    def rect(self, x, y, w, h, c):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.put(i, j, c)

    def ellipse(self, cx, cy, rx, ry, c, shade=None):
        """Filled ellipse; shade(x, y, nx, ny) -> index overrides c (nx, ny = position in -1..1)."""
        for j in range(int(cy - ry - 1), int(cy + ry + 2)):
            for i in range(int(cx - rx - 1), int(cx + rx + 2)):
                nx, ny = (i + 0.5 - cx) / rx, (j + 0.5 - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    self.put(i, j, shade(i, j, nx, ny) if shade else c)

    def line(self, x0, y0, x1, y1, c, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for k in range(n + 1):
            t = k / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dy in range(w):
                for dx in range(w):
                    self.put(math.floor(x + dx - (w - 1) / 2 + 0.5), math.floor(y + dy - (w - 1) / 2 + 0.5), c)

    def poly(self, pts, c):
        m = Image.new("1", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=1)
        mp = m.load()
        for j in range(self.h):
            for i in range(self.w):
                if mp[i, j]:
                    self.put(i, j, c)

    def outline(self, c, only=None, diag=False):
        """Ink the clear pixels touching drawn ones (optionally only around pixels whose index is in `only`)."""
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] is not None:
                    continue
                nb = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
                for dx, dy in nb:
                    v = self.get(x + dx, y + dy)
                    if v is not None and (only is None or v in only):
                        add.append((x, y))
                        break
        for x, y in add:
            self.p[y][x] = c

    def paste(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                if other.p[y][x] is not None:
                    self.put(ox + x, oy + y, other.p[y][x])

    def flip_x(self):
        out = Ix(self.w, self.h)
        for y in range(self.h):
            out.p[y] = list(reversed(self.p[y]))
        return out

    def image(self, pal):
        """Indexed PIL image with the given 16-colour palette (index 0 for clear)."""
        im = Image.new("P", (self.w, self.h), 0)
        flat = []
        for c in pal:
            flat += list(c)
        im.putpalette(flat + [0] * (768 - len(flat)))
        px = im.load()
        for y in range(self.h):
            for x in range(self.w):
                v = self.p[y][x]
                px[x, y] = 0 if v is None else v
        return im


def rgb(im_p, bg=None):
    """An indexed image as RGB (index 0 shown as bg, or its palette colour)."""
    out = im_p.convert("RGB")
    if bg is not None:
        px, src = out.load(), im_p.load()
        for y in range(out.height):
            for x in range(out.width):
                if src[x, y] == 0:
                    px[x, y] = bg
    return out


def scale(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def font(sz):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def save_indexed(im, path):
    """Save an indexed PNG with exactly 16 palette entries."""
    pal = im.getpalette()[:48]
    out = im.copy()
    out.putpalette(pal)
    out.save(os.path.join(ROOT, path), bits=4)

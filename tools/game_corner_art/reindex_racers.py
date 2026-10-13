"""Re-index the Rattata and Feebas race sprites (graphics/derby/{rattata,feebas}_ow.png) to the species palettes src/derby.c
loads for them (graphics/pokemon/<species>/normal.pal; the shiny racer uses shiny.pal by index). Index 0 stays transparent;
every other pixel takes the nearest colour of the normal palette (weighted RGB), so the art keeps its look but the colours
in the race are the species' own.

usage (from the decomp root): python tools/game_corner_art/reindex_racers.py [--check]
"""
import sys

from PIL import Image


def read_pal(path):
    return [tuple(int(c) for c in l.split()) for l in open(path).read().split("\n")[3:19]]


def dist(a, b):
    r = (a[0] + b[0]) / 2
    return (2 + r / 256) * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + (2 + (255 - r) / 256) * (a[2] - b[2]) ** 2


def reindex(species):
    p = f"graphics/derby/{species}_ow.png"
    im = Image.open(p)
    src = im.getpalette()[:48]
    src = [tuple(src[i:i + 3]) for i in range(0, 48, 3)]
    pal = read_pal(f"graphics/pokemon/{species}/normal.pal")
    remap = {0: 0}
    for i, c in enumerate(src):
        if i:
            remap[i] = min(range(1, 16), key=lambda j: dist(c, pal[j]))
    out = Image.new("P", im.size)
    flat = [v for c in pal for v in c]
    out.putpalette(flat + [0] * (768 - len(flat)))
    px, o = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            o[x, y] = remap[px[x, y]]
    return im, out, remap


def main():
    check = "--check" in sys.argv
    for s in ("rattata", "feebas"):
        im, out, remap = reindex(s)
        pal = read_pal(f"graphics/pokemon/{s}/normal.pal")
        if check:
            used = set(out.get_flattened_data() if hasattr(out, "get_flattened_data") else out.getdata())
            cur = im.getpalette()[:48]
            ok = [tuple(cur[i:i + 3]) for i in range(0, 48, 3)] == pal
            print(f"{s}: palette {'matches' if ok else 'DIFFERS'} the species normal.pal")
            continue
        out.save(f"graphics/derby/{s}_ow.png")
        print(s, {k: v for k, v in remap.items() if k})


if __name__ == "__main__":
    main()

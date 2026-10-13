"""Clean GBA-accurate render of a map plus its camera margin (no annotations), for before/after review.

usage (from the decomp root):  python tools/mapgen/edge_render.py <out.png | out_{}.png> [--scale 2] <map_stem> [more stems]   ({} = the stem)
Draws gba_view.World.backup (the engine's backup layout: border blocks, neighbour strips drawn with THIS map's tilesets) cropped to the
map + the camera margin (7 W/E, 5 N/S), at --scale (default 2).  Several stems are written as <out>_<stem>.png when out has no {}.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gba_view as gv  # noqa: E402


def render(wd, stem, scale=2):
    grid, src, W, H = wd.backup(stem)
    w, h = wd.size(stem)
    ts = wd.ts(stem)
    im = gv.Image.new("RGB", (W * 16, H * 16))
    for i, v in enumerate(grid):
        im.paste(gv.cell_img(ts, v), ((i % W) * 16, (i // W) * 16))
    o = gv.MAP_OFFSET
    box = ((o - 7) * 16, (o - 5) * 16, (o + w + 7) * 16, (o + h + 5) * 16)
    im = im.crop(box)
    return im.resize((im.width * scale, im.height * scale), gv.Image.NEAREST)


def main(argv):
    scale = 2
    out = argv[0]
    rest = argv[1:]
    if rest and rest[0] == "--scale":
        scale = int(rest[1])
        rest = rest[2:]
    wd = gv.World()
    for stem in rest:
        p = out.format(stem) if "{}" in out else out if len(rest) == 1 else out.replace(".png", f"_{stem}.png")
        render(wd, stem, scale).save(p)
        print("wrote", p)


if __name__ == "__main__":
    main(sys.argv[1:])

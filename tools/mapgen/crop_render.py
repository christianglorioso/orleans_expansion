"""GBA-accurate crop of a map region in map cells: python tools/mapgen/crop_render.py <out.png> <map_stem> x0 y0 x1 y1 [scale]  (inclusive cells)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gba_view as gv  # noqa: E402


def main(a):
    out, stem = a[0], a[1]
    x0, y0, x1, y1 = (int(v) for v in a[2:6])
    scale = int(a[6]) if len(a) > 6 else 3
    wd = gv.World()
    grid, src, W, H = wd.backup(stem)
    ts = wd.ts(stem)
    o = gv.MAP_OFFSET
    im = gv.Image.new("RGB", ((x1 - x0 + 1) * 16, (y1 - y0 + 1) * 16))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            im.paste(gv.cell_img(ts, grid[(y + o) * W + (x + o)]), ((x - x0) * 16, (y - y0) * 16))
    im = im.resize((im.width * scale, im.height * scale), gv.Image.NEAREST)
    im.save(out)


if __name__ == "__main__":
    main(sys.argv[1:])

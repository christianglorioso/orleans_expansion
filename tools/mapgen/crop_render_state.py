"""Like crop_render.py but applies a map's generated `<Map>_EventScript_State<name>` setmetatile lines first (the flood and the like).
usage: python tools/mapgen/crop_render_state.py <out.png> <map_stem> <MapDir> <StateName> x0 y0 x1 y1 [scale]"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gba_view as gv  # noqa: E402


def main(a):
    out, stem, mapdir, state = a[:4]
    x0, y0, x1, y1 = (int(v) for v in a[4:8])
    scale = int(a[8]) if len(a) > 8 else 3
    wd = gv.World()
    grid, src, W, H = wd.backup(stem)
    ts = wd.ts(stem)
    o = gv.MAP_OFFSET
    txt = open(os.path.join("data/maps", mapdir, "scripts.inc"), encoding="utf-8").read()
    body = txt[txt.index(f"{mapdir}_EventScript_State{state}::"):]
    body = body[:body.index("\treturn")]
    grid = list(grid)
    for m in re.finditer(r"setmetatile (\d+), (\d+), 0x([0-9A-Fa-f]+), (\w+)", body):
        x, y, mid = int(m.group(1)), int(m.group(2)), int(m.group(3), 16)
        i = (y + o) * W + (x + o)
        grid[i] = (grid[i] & ~0x3FF) | mid
    im = gv.Image.new("RGB", ((x1 - x0 + 1) * 16, (y1 - y0 + 1) * 16))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            im.paste(gv.cell_img(ts, grid[(y + o) * W + (x + o)]), ((x - x0) * 16, (y - y0) * 16))
    im.resize((im.width * scale, im.height * scale), gv.Image.NEAREST).save(out)


if __name__ == "__main__":
    main(sys.argv[1:])

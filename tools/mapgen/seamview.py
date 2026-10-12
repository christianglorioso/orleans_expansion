"""Render one join of world.WORLD from the built map.bin files, edge to edge (a restart aid for the phase-2 seam work).

usage (from the decomp root): python -W ignore tools/mapgen/seamview.py <map_a> <map_b> <out.png> [depth=14] [scale=3]
Prints nothing else.  Magenta line = the border; ticks every 5 cells along the border; rows/cols numbered in map A's coordinates.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
import world_stitch as ws  # noqa: E402


def main(a, b, out, depth=14, scale=3):
    entry = next(e for e in world.WORLD if {e[0], e[2]} == {a, b})
    ea, d, eb, k, _ = entry
    maps = world.Maps()
    cache = {}
    A, B = ws.Built(ea, maps, cache), ws.Built(eb, maps, cache)
    sa, sb = ws.SIDE[d]
    horiz = sa in "EW"
    la, lb = A.length(sa), B.length(sb)
    lo, hi = min(0, k), max(la, k + lb)
    cs = 16 * scale
    n = hi - lo
    if horiz:
        P = Image.new("RGB", (2 * depth * cs, n * cs), (40, 40, 40))
    else:
        P = Image.new("RGB", (n * cs, 2 * depth * cs), (40, 40, 40))

    def cut(bm, side, i0, i1):
        if side == "E":
            box = ((bm.w - depth) * 16, 0, bm.w * 16, bm.h * 16)
        elif side == "W":
            box = (0, 0, depth * 16, bm.h * 16)
        elif side == "S":
            box = (0, (bm.h - depth) * 16, bm.w * 16, bm.h * 16)
        else:
            box = (0, 0, bm.w * 16, depth * 16)
        return bm.im.crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.NEAREST)

    ia, ib = cut(A, sa, 0, la), cut(B, sb, 0, lb)
    if horiz:
        ax, bx = (0, depth * cs) if sa == "E" else (depth * cs, 0)
        P.paste(ia, (ax, (0 - lo) * cs)); P.paste(ib, (bx, (k - lo) * cs))
    else:
        ay, by = (0, depth * cs) if sa == "S" else (depth * cs, 0)
        P.paste(ia, ((0 - lo) * cs, ay)); P.paste(ib, ((k - lo) * cs, by))
    dr = ImageDraw.Draw(P)
    seam = depth * cs
    if horiz:
        dr.line([(seam, 0), (seam, P.height)], fill=(255, 0, 255), width=2)
    else:
        dr.line([(0, seam), (P.width, seam)], fill=(255, 0, 255), width=2)
    for t in range(lo, hi):
        if t % 5 == 0:
            u = (t - lo) * cs
            if horiz:
                dr.line([(seam - 10, u), (seam + 10, u)], fill=(255, 255, 0), width=1); dr.text((seam + 12, u), str(t), fill=(255, 255, 0))
            else:
                dr.line([(u, seam - 10), (u, seam + 10)], fill=(255, 255, 0), width=1); dr.text((u + 2, seam + 12), str(t), fill=(255, 255, 0))
    P.save(out)
    r = ws.analyse(entry, {ea: A, eb: B})
    print("   ", r["sev"], "; ".join(r["reasons"]) or "clean")
    print(out, P.size, f"A={ea}({sa}) B={eb}({sb}) offset {k}; numbers are {ea} coordinates")


if __name__ == "__main__":
    a, b, out = sys.argv[1:4]
    main(a, b, out, *(int(x) for x in sys.argv[4:]))

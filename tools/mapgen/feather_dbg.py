"""debug: python tools/mapgen/feather_dbg.py <map_stem> [--brief]   (in-memory build; nothing is written)
prints the feather log, the report lines (what could not be done), edge cells not drawn with an overhang piece, outer-corner cells"""
import os, sys, warnings, time
os.environ.setdefault("EDGE_FEATHER_ALL", "1")
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, borders
key = sys.argv[1]
brief = "--brief" in sys.argv
t0 = time.time()
b = build.Builder(os.path.join(HERE, "maps", key + ".json"))
b.draw()
inv = {}
for n, v in build.MAPPING.items():
    inv.setdefault(v, n)
bad = []
for (x, y), face in sorted(b.edge.items()):
    nm = inv.get(b.blocks[y][x] & 0x3FF, "?")
    if not nm.startswith(("bd:", "bdg", "patch:bd", "patch:bk")):
        bad.append((x, y, face, nm, b.grid[y][x]))
mc = getattr(b, "feather_missing", [])
rep = getattr(b, "feather_report", [])
if brief:
    log = [l for l in b.border_log if "feather" in l]
    left = sum(1 for r in rep if r.startswith("edge cell"))
    exp = getattr(b, "feather_exposed", {})
    other = [r for r in rep if not r.startswith("edge cell") and "surf exposure" not in r]
    print(f"{key:15s} {b.border_style:5s} wall {len(b.wall):4d} edge {len(b.edge):4d} plain-edge {len(bad):3d} left-plain {left:3d} exposed {sum(len(v) for v in exp.values()):3d} {dict((k, len(v)) for k, v in exp.items())} {time.time()-t0:.0f}s")
    for r in other:
        print("      -", r[:230])
else:
    print("log:", *b.border_log, sep="\n  ")
    print("report:", *rep, sep="\n  ")
    print(f"{len(b.edge)} edge cells, {len(bad)} not drawn with an overhang piece")
    for t in bad[:60]:
        print("  ", t)
    print(f"{len(mc)} outer-corner cells (no art)")

if "--ascii" in sys.argv:
    import feather
    blocked, struct = feather.blocking_cells(b)
    for y in range(b.h):
        row = ""
        for x in range(b.w):
            c = (x, y)
            ch = b.grid[y][x]
            if c in b.wall:
                row += "W"
            elif c in b.edge:
                row += "e"
            elif c in blocked:
                row += "#"
            elif c in struct:
                row += "="
            elif ch in "~Iw":
                row += "~"
            else:
                row += ch
        print(f"{y:2d} {row}")

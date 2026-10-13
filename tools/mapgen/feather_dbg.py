"""debug: python tools/mapgen/feather_dbg.py <map_stem>  (in-memory build; prints the feather log, uncovered edge cells, missing corners)"""
import os, sys, warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build, borders
key = sys.argv[1]
b = build.Builder(os.path.join(HERE, "maps", key + ".json"))
b.draw()
inv = {}
for n, v in build.MAPPING.items():
    inv.setdefault(v, n)
print("log:", *b.border_log, sep="\n  ")
print("report:", *getattr(b, "feather_report", []), sep="\n  ")
bad = []
for (x, y), face in sorted(b.edge.items()):
    terr, under = borders.edge_base(b, x, y, inv)
    # after apply the cell holds the overhang piece; compare with the grid terrain instead
    pass
names = {}
for (x, y), face in sorted(b.edge.items()):
    nm = inv.get(b.blocks[y][x] & 0x3FF, "?")
    if not nm.startswith(("bd:", "bdg")):
        bad.append((x, y, face, nm, b.grid[y][x]))
print(f"{len(b.edge)} edge cells, {len(bad)} not drawn with an overhang piece")
for t in bad[:60]:
    print("  ", t)
mc = getattr(b, "feather_missing", [])
print(f"{len(mc)} outer-corner cells (no art)")

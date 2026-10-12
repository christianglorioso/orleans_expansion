import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as s, species_map as m, ppdata as p
t, e = p.load()
cons = m.species_consts()
by = collections.defaultdict(list)
for r in s.load_dex():
    if r["kind"] != "species":
        continue
    if r["name"] in m.ORLEANIAN:
        k = m.canonical("SPECIES_" + r["name"].upper())
    else:
        k = m.base_const(r["name"], cons)
    by[p.fields(e[k])["natdex"]].append((r["num"], r["name"], k))
for nd, v in by.items():
    if len(v) > 1:
        print(nd, v)
print(len(by), sum(len(v) for v in by.values()))

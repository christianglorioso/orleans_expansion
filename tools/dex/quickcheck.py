import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as s, species_map as m, ppdata as p, cdata as c
t, e = p.load()
cons = m.species_consts()
bad = 0
for r in s.load_dex():
    if r["name"] in m.CUSTOM_MEGAS and m.CUSTOM_MEGAS[r["name"]] not in e:
        continue
    k = m.orleanian_const(r["name"]) if r["name"] in m.ORLEANIAN and r["kind"] == "species" else m.base_const(r["name"], cons)
    f = p.fields(e[k])
    wa = (([m.ability_const(a) for a in r["abilities"]]) + ["ABILITY_NONE"] * 3)[:3]
    if f["stats"] != r["stats"] or f["types"] != [c.TYPE_NAMES[x] for x in r["types"]] or f["abilities"] != wa:
        bad += 1
        print(r["name"], f["stats"], f["types"], f["abilities"])
print("bad", bad)

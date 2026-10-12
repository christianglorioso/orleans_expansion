import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as s, species_map as m, ppdata as p
t, e = p.load()
cons = m.species_consts()
for r in s.load_dex():
    if r["kind"] != "species":
        continue
    n = r["notes"]
    if re.search(r"volve|Linking|trade|Evolution", n, re.I) or r["name"] in ("Gimmighoul",):
        k = m.orleanian_const(r["name"]) if r["name"] in m.ORLEANIAN else m.base_const(r["name"], cons)
        body = e[k]
        i = body.find(".evolutions =")
        ev = ""
        if i >= 0:
            j = body.index("\n", i)
            ev = body[i:j].strip()[:200]
        print(f"{r['name']}: NOTE: {n[:230]}\n    ENGINE: {ev}")

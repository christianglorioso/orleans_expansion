import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as s, species_map as m, ppdata as p
t, e = p.load()
cons = m.species_consts()
def evos(k):
    body = e[k]
    i = body.find(".evolutions =")
    if i < 0:
        return None
    # take to matching end
    j = body.index("{ 0xFFFF }", i)
    txt = body[i + 13:j]
    txt = re.sub(r"\(const struct EvolutionParam\[\]\) ", "", txt)
    txt = re.sub(r"\(const struct Evolution\[\]\) ", "", txt)
    return re.sub(r"\s+", " ", txt)
if __name__ == "__main__":
    for r in s.load_dex():
        if r["kind"] != "species":
            continue
        k = m.orleanian_const(r["name"]) if r["name"] in m.ORLEANIAN else m.base_const(r["name"], cons)
        ev = evos(k)
        if ev:
            print(f"{r['name']} [{k}]: {ev}")

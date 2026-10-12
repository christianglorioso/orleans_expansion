import json, sys, re, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as s, species_map as m
cons = m.species_consts()
dex = set()
for r in s.load_dex():
    if r["kind"] == "species":
        dex.add(m.orleanian_const(r["name"]) if r["name"] in m.ORLEANIAN else m.base_const(r["name"], cons))
ORL_BASE = {m.base_of_orleanian(n): m.orleanian_const(n) for n in m.ORLEANIAN}
ROOT = m.ROOT
d = json.load(open(ROOT / "src/data/wild_encounters.json", encoding="utf-8"))
bad = collections.defaultdict(list)
fix = collections.Counter()
for g in d["wild_encounter_groups"][:1]:
    for e in g["encounters"]:
        if "_Orleans" not in e["base_label"]:
            continue
        for k, v in e.items():
            if isinstance(v, dict) and "mons" in v:
                for mon in v["mons"]:
                    sp = m.canonical(mon["species"])
                    if sp in ORL_BASE:
                        fix[sp] += 1
                    elif sp not in dex:
                        bad[sp].append(e["base_label"])
print("orleanian-base uses:", dict(fix))
for k, v in bad.items():
    print("NOT IN DEX", k, len(v), sorted(set(v))[:4])

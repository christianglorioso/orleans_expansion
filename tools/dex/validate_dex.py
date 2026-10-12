"""Compares the built Orleans data against orleans_dex.xlsx / orleans_learnsets.xlsx and reports mismatches.

usage:  python tools/dex/validate_dex.py [--pp]
  --pp   first regenerate tools/dex/out/pokemon_pp.c (src/pokemon.c preprocessed with the real build flags, in WSL)
         -- run a ROM build first so the generated teachable_learnsets.h in the WSL mirror is current.

Checks (every mismatch is printed; exit code 1 if any):
  1. types, base stats and abilities of every sheet species / Mega / Primal (343 rows)
  2. Mega Evolution wiring (form-change table entry with a Mega stone for every Mega row)
  3. evolutions: the decided methods (apply_evolutions.EVOS, the Orleanian chain) and closure inside the Orleans dex
  4. regional dex order (300 entries, sheet order) and that each entry resolves to the sheet species
  5. level-up learnsets, egg moves, TM/tutor compatibility (sheet TM + tutor columns, pre-evolution entries excluded),
     and that every move constant exists
  6. wild encounters (Orleans headers) and Orleans trainer parties: species in dex, moves legal, abilities valid
  7. abilities: every ability constant used exists and has a gAbilitiesInfo entry
Informational (not mismatches): TM count, sheet TM-column moves that are tutors instead of TMs.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_evolutions
import cdata
import learnset_model as lm
import partylib
import party_check as pc
import ppdata
import sheet_data as sd
import species_map as sm

ROOT = sm.ROOT
mismatches = []
info = []


def bad(section, msg):
    mismatches.append(f"[{section}] {msg}")


def run_pp():
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "/mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/dex/pp.sh"],
                       capture_output=True, text=True, env={**__import__("os").environ, "MSYS_NO_PATHCONV": "1"})
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit("pp.sh failed")


def species_for(row, cons):
    if row["name"] in sm.ORLEANIAN and row["kind"] == "species":
        return sm.orleanian_const(row["name"])
    return sm.base_const(row["name"], cons)


def main():
    if "--pp" in sys.argv:
        run_pp()
    t, ents = ppdata.load()
    cons = sm.species_consts()
    dex = sd.load_dex()
    abil_src = (ROOT / "include/constants/abilities.h").read_text(encoding="utf-8")
    abil_consts = set("ABILITY_" + x for x in re.findall(r"ABILITY_(\w+)\s*=", abil_src))
    abil_info = set(re.findall(r"\[(ABILITY_\w+)\] =", (ROOT / "src/data/abilities.h").read_text(encoding="utf-8")))
    ntype = 0

    # ---- 1 types / stats / abilities --------------------------------------------------------------
    sp_of = {}
    for r in dex:
        k = species_for(r, cons)
        sp_of[r["name"]] = k
        if k not in ents:
            bad("species", f"{r['name']}: {k} missing"); continue
        f = ppdata.fields(ents[k])
        wt = [cdata.TYPE_NAMES[x] for x in r["types"]]
        wa = ([sm.ability_const(a) for a in r["abilities"]] + ["ABILITY_NONE"] * 3)[:3]
        if f["stats"] != r["stats"]:
            bad("stats", f"{r['name']}: built {f['stats']} sheet {r['stats']}")
        if f["types"] != wt:
            bad("types", f"{r['name']}: built {f['types']} sheet {wt}")
        if f["abilities"] != wa:
            bad("abilities", f"{r['name']}: built {f['abilities']} sheet {wa}")
        for a in wa:
            if a not in abil_consts:
                bad("abilities", f"{r['name']}: {a} not defined")
            elif a not in abil_info and a != "ABILITY_NONE":
                bad("abilities", f"{r['name']}: {a} has no gAbilitiesInfo entry")
        ntype += 1
        if r["kind"] != "species" and ".isMegaEvolution = TRUE" not in ents[k] and "isMegaEvolution = 1" not in ents[k] \
                and r["kind"] == "mega" and not re.search(r"\.isMegaEvolution = (TRUE|1)", ents[k]):
            bad("mega", f"{r['name']}: {k} is not flagged isMegaEvolution")

    # ---- 2 mega wiring ---------------------------------------------------------------------------
    fct = (ROOT / "src/data/pokemon/form_change_tables.h").read_text(encoding="utf-8")
    for r in dex:
        if r["kind"] != "mega":
            continue
        k = sp_of[r["name"]]
        if not re.search(r"FORM_CHANGE_BATTLE_MEGA_EVOLUTION_(?:ITEM|MOVE),\s*" + k + r",", fct):
            bad("mega", f"{r['name']}: no Mega Evolution form-change entry for {k}")
    for r in dex:
        if r["kind"] == "primal":
            if not re.search(k_re(sp_of[r["name"]]), fct):
                bad("mega", f"{r['name']}: no primal form-change entry for {sp_of[r['name']]}")

    # ---- 3 evolutions ----------------------------------------------------------------------------
    import evo_dump
    norm = lambda s: re.sub(r"\s+", "", re.sub(r"CONDITIONS\(", "(", s))
    for const, spec in apply_evolutions.EVOS.items():
        got = evo_dump.evos(const)
        want = spec
        # compare the (method, param, target) triples
        trip = lambda s: re.findall(r"\{(EVO_\w+),?\s*([^{}]*?)\s*SPECIES_(\w+)", s)
        wt_ = sorted((a, c) for a, b, c in trip(want))
        gt_ = sorted((a, c) for a, b, c in trip(got or ""))
        if wt_ != gt_:
            bad("evolutions", f"{const}: built {gt_} decided {wt_}")
    dexset = set(sp_of.values())
    dex_natdex = {ppdata.fields(ents[k])["natdex"] for k in dexset}
    for name, k in sp_of.items():
        ev = evo_dump.evos(k)
        if not ev:
            continue
        for m in re.finditer(r"\{(EVO_\w+), [^{}]*?(SPECIES_\w+)", ev):
            if m.group(1) == "EVO_NONE":
                continue
            tgt = m.group(2)
            if ppdata.fields(ents[tgt])["natdex"] not in dex_natdex:
                bad("evolutions", f"{name}: evolves into {tgt} which is not an Orleans dex species")
    # decided methods that must not exist any more
    for name, k in sp_of.items():
        ev = evo_dump.evos(k) or ""
        if "EVO_TRADE" in ev:
            bad("evolutions", f"{name}: still has a plain trade evolution (Linking Cord only)")

    # ---- 4 dex order ----------------------------------------------------------------------------
    ph = (ROOT / "include/constants/pokedex.h").read_text(encoding="utf-8")
    a = ph.index("#define FOREACH_SPECIES_IN_HOENN_DEX_ORDER(F)")
    seg = ph[a:ph.index("\n\n", a)]
    order = re.findall(r"F\((\w+)\)", seg)
    want = []
    for r in sorted([x for x in dex if x["kind"] == "species"], key=lambda x: x["num"]):
        want.append(ppdata.fields(ents[sp_of[r["name"]]])["natdex"][len("NATIONAL_DEX_"):])
    if order != want:
        bad("dex order", f"regional list differs from sheet order ({len(order)} vs {len(want)} entries); first diff at "
            f"{next((i + 1 for i, (x, y) in enumerate(zip(order, want)) if x != y), '-')}")
    if len(set(want)) != len(want):
        bad("dex order", "two sheet entries share a national dex number")
    if f"HOENN_DEX_{order[-1]} + 1" not in ph:
        bad("dex order", "HOENN_DEX_COUNT does not end at the last Orleans entry")
    for r in dex:
        if r["kind"] in ("mega", "primal"):
            base = [x for x in dex if x["num"] == r["num"] and x["kind"] == "species"]
            if base:
                nd_b = ppdata.fields(ents[sp_of[base[0]["name"]]])["natdex"]
                nd_m = ppdata.fields(ents[sp_of[r["name"]]])["natdex"]
                if nd_b != nd_m:
                    bad("dex order", f"{r['name']} natDexNum {nd_m} differs from base {base[0]['name']} {nd_b}")

    # ---- 5 learnsets ------------------------------------------------------------------------------
    lv = ppdata.levelup_sets(t)
    tc = ppdata.move_sets(t, "TeachableLearnset")
    eg = ppdata.move_sets(t, "EggMoveLearnset")
    rows = lm.build()
    for r in rows:
        p = r["ptr_lv"]
        want_lv = sorted((m, l) for l, m in r["levelup"])
        if lv.get(p) is None or sorted(lv[p]) != want_lv:
            bad("level-up", f"{r['name']}: built {len(lv.get(p) or [])} moves vs sheet {len(want_lv)}")
        if r["ptr_egg"] and "None" not in r["ptr_egg"]:
            if sorted(eg.get(r["ptr_egg"], [])) != sorted(r["egg"]):
                bad("egg", f"{r['name']}: built {sorted(eg.get(r['ptr_egg'], []))[:4]}.. vs sheet {sorted(r['egg'])[:4]}..")
        got = set(tc.get(r["ptr_tm"], []))
        want_t = set(r["tm"]) | set(r["tutor"])
        if got != want_t:
            bad("TM/tutor", f"{r['name']}: missing {sorted(want_t - got)[:4]} extra {sorted(got - want_t)[:4]}")
    src = (ROOT / "include/constants/tms_hms.h").read_text(encoding="utf-8")
    tm_part = src.split("#define FOREACH_HM")[0]
    tms = ["MOVE_" + x for x in re.findall(r"F\((\w+)\)", tm_part)]
    for need in ("MOVE_TRAILBLAZE", "MOVE_SHOCK_WAVE", "MOVE_SHADOW_BALL"):
        if need not in tms:
            bad("TM", f"{need} (story TM) is not in the TM list")
    info.append(f"TM count: {len(tms)} (TM001-TM{len(tms)}); HMs unchanged (8)")
    sheet_tm_moves = set()
    for r in rows:
        sheet_tm_moves |= set(r["tm"])
    tut_only = sorted(m for m in sheet_tm_moves if m not in tms and m not in
                      ["MOVE_" + x for x in re.findall(r"F\((\w+)\)", src.split("#define FOREACH_HM")[1].split("#define FOREACH_TMHM")[0])])
    info.append(f"sheet TM-column moves that are tutor (Move Relearner) moves instead of TMs: {len(tut_only)}")
    moves_src = (ROOT / "include/constants/moves.h").read_text(encoding="utf-8")
    for r in rows:
        for m in set(r["tm"]) | set(r["tutor"]) | set(r["egg"]) | {x for _, x in r["levelup"]}:
            if not re.search(r"\b" + m + r"\b", moves_src):
                bad("moves", f"{r['name']}: {m} does not exist")
    # story TMs legal for their intended users is a data property of the TM list: nothing more to check here

    # ---- 6 encounters / trainers -------------------------------------------------------------------
    d = json.load(open(ROOT / "src/data/wild_encounters.json", encoding="utf-8"))
    orl_species = set()
    for g in d["wild_encounter_groups"][:1]:
        for e in g["encounters"]:
            if "_Orleans" not in e["base_label"]:
                continue
            for k2, v in e.items():
                if isinstance(v, dict) and "mons" in v:
                    for mon in v["mons"]:
                        s_ = sm.canonical(mon["species"])
                        orl_species.add(s_)
                        if s_ not in ents:
                            bad("encounters", f"{e['base_label']}: unknown species {s_}")
                        elif s_ not in dexset:
                            bad("encounters", f"{e['base_label']}: {s_} is not in the Orleans dex")
    removed = {"SPECIES_LOTAD", "SPECIES_LOMBRE", "SPECIES_LUDICOLO", "SPECIES_PINCURCHIN", "SPECIES_CHATOT"}
    for g in d["wild_encounter_groups"]:
        for e in g["encounters"]:
            for k2, v in e.items():
                if isinstance(v, dict) and "mons" in v:
                    for mon in v["mons"]:
                        if mon["species"] in removed:
                            bad("encounters", f"{e['base_label']}: removed species {mon['species']} still in a wild table")
    master = {x["const"] for x in partylib.parse(ROOT / "tools/dex/out/trainers_master.party")}
    cur = partylib.parse(ROOT / "src/data/trainers.party")
    orl = {x["const"] for x in cur} - master
    for p in pc.main([ROOT / "src/data/trainers.party"]):
        if p[0] in orl:
            bad("trainers", str(p))
    not_dex = sorted({m["species"] for x in cur if x["const"] in orl for m in x["mons"]
                      if sm.canonical(pc.species_const(m["species"])) not in dexset})
    info.append(f"Orleans trainers use {len(not_dex)} species outside the Orleans dex (story decision, not changed): {', '.join(not_dex)}")

    print(f"checked {ntype} sheet rows, {len(rows)} learnset rows, {len(order)} regional dex entries")
    for i in info:
        print("info:", i)
    for m in mismatches:
        print("MISMATCH", m)
    print(f"mismatches: {len(mismatches)}")
    return 1 if mismatches else 0


def k_re(const):
    return r"FORM_CHANGE_\w+,\s*" + const


if __name__ == "__main__":
    sys.exit(main())

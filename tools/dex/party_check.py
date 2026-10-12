"""Validates Orleans trainer parties against the built species data (run after pp.sh)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import partylib
import ppdata
import sheet_data as sd
import species_map as sm

ROOT = sm.ROOT


def species_const(name):
    n = re.sub(r"[^A-Za-z0-9]+", "_", name.replace("é", "e")).strip("_").upper()
    return "SPECIES_" + n


def build_tables():
    t, ents = ppdata.load()
    lv = ppdata.levelup_sets(t)
    tc = ppdata.move_sets(t, "TeachableLearnset")
    eg = ppdata.move_sets(t, "EggMoveLearnset")
    info = {k: ppdata.fields(v) for k, v in ents.items()}
    # evolution graph: prev[species] = set(pre-evolutions)
    prev = {}
    for k, v in ents.items():
        i = v.find(".evolutions =")
        if i < 0:
            continue
        seg = v[i:]
        j = seg.find("{ 0xFFFF }")
        for m in re.finditer(r"\{EVO_\w+, [^{}]*?(SPECIES_\w+)(?:,|\})", seg[:j] if j > 0 else seg):
            prev.setdefault(m.group(1), set()).add(k)
    return info, lv, tc, eg, prev


def legal_moves(sp, level, info, lv, tc, eg, prev):
    """all moves a trainer's `sp` could have at `level`: own and pre-evolution level-up moves, teachable, egg moves"""
    out = set()
    seen, stack = set(), [sp]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        f = info.get(s)
        if not f:
            continue
        out |= {m for m, l in lv.get(f["levelUp"], []) if l <= level}
        out |= set(eg.get(f["egg"], []))
        stack += list(prev.get(s, []))
    f = info[sp]
    out |= set(tc.get(f["teach"], []))
    return out


def main(path_list):
    info, lv, tc, eg, prev = build_tables()
    mv = sd.load_move_names()
    cons = sm.species_consts()
    problems = []
    for path in path_list:
        for tr in partylib.parse(path):
            for mon in tr["mons"]:
                sc = sm.canonical(species_const(mon["species"]))
                if sc not in info:
                    problems.append((tr["const"], mon["species"], "unknown species", sc))
                    continue
                level = int(mon["fields"].get("Level", 1))
                legal = legal_moves(sc, level, info, lv, tc, eg, prev)
                for mvn in mon["moves"]:
                    mc = mv.get(sd.norm(mvn))
                    if mc is None:
                        problems.append((tr["const"], mon["species"], "unknown move", mvn))
                    elif mc not in legal:
                        problems.append((tr["const"], mon["species"], "illegal move", mvn, level))
                ab = mon["fields"].get("Ability")
                if ab:
                    ac = sm.ability_const(ab)
                    if ac not in info[sc]["abilities"]:
                        problems.append((tr["const"], mon["species"], "ability not on species", ab))
    return problems


if __name__ == "__main__":
    paths = [ROOT / "src/data/trainers.party"]
    pr = main(paths)
    new = {t["const"] for t in partylib.parse(ROOT / "tools/dex/out/trainers_master.party")}
    orl = {t["const"] for t in partylib.parse(ROOT / "src/data/trainers.party")} - new
    pr = [p for p in pr if p[0] in orl]
    for p in pr:
        print(p)
    print("problems:", len(pr))

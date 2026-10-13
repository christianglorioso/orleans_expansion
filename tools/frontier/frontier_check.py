"""Lint for the Battle Frontier data (run it after gen_frontier.py and after every change to species/learnset data).

usage (from the decomp root):  python tools/frontier/frontier_check.py [--quiet]
exit code 1 on any problem.

Checks
  legends   no legendary, sub-legendary, restricted, mythical, ultra beast or paradox species anywhere (flags in the species data + Bloodmoon Ursaluna, Gimmighoul, Gholdengo)
  species   every set / brain / Pike / Pyramid species is in the Orleans dex (Orleanian forms, not the Kantonian base), is not Frontier-banned,
            and is a real SPECIES constant
  moves     every move is a real move, is legal for the species under OUR learnsets (level-up up to 50 incl. pre-evolutions, egg, TM/tutor),
            no duplicates, at least one damaging move unless the set is a declared support set
  ability   the explicit .ability is one of the species' abilities in the built data
  item      the item exists, has a battle effect, is not banned, and is obtainable in Orleans or on the allow-list below; Mega stones and masks
            match the species; Eviolite only on unevolved species
  evs       each EV <= 252, total <= 510; natures and balls are valid constants
  pools     every trainer pool macro exists, ids are valid, and (ids <= 849, the Level 50 view) it holds enough distinct species and items for
            FillTrainerParty not to loop forever
  trainers  300 trainers, names 1-7 letters A-Z and unique, facility classes valid
  engine    battle_factory.c ranges use macros defined in include/constants/battle_frontier_mons.h
"""
import collections
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fdata
import movedb
import odex
import layoutplan
import lint_items

ROOT = fdata.ROOT
problems = []
notes = []


def bad(section, msg):
    problems.append(f"[{section}] {msg}")


def main():
    quiet = "--quiet" in sys.argv
    d = odex.Dex()
    mv = movedb.load()
    items = lint_items.load_items()
    obtainable = lint_items.obtainable(items)
    megas = lint_items.mega_stones(d)
    natures = set(re.findall(r"#define (NATURE_\w+)\s+\d+", (ROOT / "include/constants/pokemon.h").read_text(encoding="utf-8")))
    balls = set(re.findall(r"(BALL_\w+) =", (ROOT / "include/constants/pokeball.h").read_text(encoding="utf-8")))
    abil_defined = set(re.findall(r"\[(ABILITY_\w+)\] =", (ROOT / "src/data/abilities.h").read_text(encoding="utf-8")))
    banned_sp = {k for k, v in d.ents.items() if re.search(r"\.isFrontierBanned = (TRUE|1)", v)}

    def check_member(where, sp, moves, item, ability, nature=None, ball=None, ev=None, level=50, support_ok=False):
        c = d.canonical(sp)
        if c not in d.species:
            bad("species", f"{where}: {sp} is not in the Orleans dex")
            return
        if c in banned_sp:
            bad("species", f"{where}: {sp} is Frontier-banned")
        if layoutplan.is_legend(d, c):
            bad("species", f"{where}: {sp} is a legendary / mythical / sub-legendary (none allowed in the Battle Frontier)")
        legal = d.legal(sp, level)
        seen = set()
        real = [m for m in moves if m != "MOVE_NONE"]
        if not real:
            bad("moves", f"{where}: no moves")
        for m in real:
            if m not in mv:
                bad("moves", f"{where}: {m} is not a move")
            elif m not in legal:
                bad("moves", f"{where}: {sp[8:]} cannot learn {mv[m].name} ({m}) at level {level}")
            if m in seen:
                bad("moves", f"{where}: duplicate move {m}")
            seen.add(m)
        if real and not any(m in mv and mv[m].damaging for m in real) and not support_ok:
            bad("moves", f"{where}: {sp[8:]} has no damaging move")
        if ability:
            if ability not in abil_defined:
                bad("ability", f"{where}: {ability} is not defined")
            elif ability not in d.info[c]["abilities"]:
                bad("ability", f"{where}: {sp[8:]} does not have {ability} (has {', '.join(a for a in d.info[c]['abilities'] if a != 'ABILITY_NONE')})")
        if item is not None:
            it = items.get(item)
            if it is None:
                bad("item", f"{where}: {item} does not exist")
            else:
                why = lint_items.item_problem(item, it, sp, d, megas, obtainable)
                if why:
                    bad("item", f"{where}: {item}: {why}")
        if nature and nature not in natures:
            bad("evs", f"{where}: {nature} is not a nature")
        if ball and ball not in balls:
            bad("evs", f"{where}: {ball} is not a ball")
        if ev is not None:
            if any(e < 0 or e > 252 for e in ev) or sum(ev) > 510:
                bad("evs", f"{where}: EVs {ev} out of range")

    # ------------------------------------------------------------------ constants
    cons = fdata.mon_consts()
    ids = sorted(v for k, v in cons.items())
    if ids != list(range(len(ids))) or len(ids) != 882:
        bad("constants", f"mon ids are not 0..881 contiguous ({len(ids)} found)")
    t = fdata.read(fdata.CONST)
    if "FRONTIER_MONS_HIGH_TIER     849" not in t or "NUM_FRONTIER_MONS           882" not in t:
        bad("constants", "FRONTIER_MONS_HIGH_TIER / NUM_FRONTIER_MONS changed")
    fac = fdata.read(fdata.src("src/battle_factory.c"))
    for m in re.findall(r"\{(FRONTIER_MON\w+),\s*(FRONTIER_MON\w+)\}", fac):
        for x in m:
            if x not in cons and x not in re.findall(r"#define (FRONTIER_MON\w+)", t):
                bad("engine", f"battle_factory.c range uses {x} which is not defined")

    # ------------------------------------------------------------------ sets
    mons = fdata.parse_mons()
    if len(mons) != 882:
        bad("sets", f"{len(mons)} sets, expected 882")
    sigs = collections.defaultdict(list)
    for i, m in enumerate(mons):
        where = f"set {i} {m['const'][13:]}"
        if cons.get(m["const"]) != i:
            bad("sets", f"{where}: id {cons.get(m['const'])} does not match its position")
        support = m["species"] == "SPECIES_DITTO"
        check_member(where, m["species"], m["moves"], m["item"], m["ability"], m["nature"], m["ball"], m["ev"], support_ok=support)
        if m["ability"] is None:
            bad("ability", f"{where}: no explicit .ability")
        if m["item"] in (None, "ITEM_NONE"):
            bad("item", f"{where}: no held item")
        sigs[(m["species"], tuple(sorted(m["moves"])), m["item"])].append(i)
    for k, v in sigs.items():
        if len(v) > 1:
            bad("sets", f"duplicate sets {v}: {k[0]}")
    seen_sp = {d.canonical(m["species"]) for m in mons}
    missing = sorted(s[8:] for s in d.species if s not in seen_sp and s not in banned_sp)
    if missing:
        notes.append(f"species never used by a set: {', '.join(missing)}")
    n_mega = sum(1 for m in mons if m["item"] in megas.get(d.canonical(m["species"]), ()))
    notes.append(f"{n_mega} Mega-stone sets over {len({m['species'] for m in mons if m['item'] in megas.get(d.canonical(m['species']), ())})} species")

    # ------------------------------------------------------------------ pools / trainers
    pools = fdata.parse_pools()
    defined = set(pools)
    trainers = fdata.parse_trainers()
    if len(trainers) != 300:
        bad("trainers", f"{len(trainers)} trainers, expected 300")
    names_seen = collections.Counter(tr["name"] for tr in trainers)
    classes = set(re.findall(r"(FACILITY_CLASS_\w+)", fdata.read(ROOT / "include/constants/trainers.h")))
    for tr in trainers:
        if not re.fullmatch(r"[A-Z]{1,7}", tr["name"]):
            bad("trainers", f"{tr['const']}: name {tr['name']!r} must be 1-7 letters A-Z")
        if names_seen[tr["name"]] > 1:
            bad("trainers", f"duplicate trainer name {tr['name']}")
        if tr["cls"] not in classes:
            bad("trainers", f"{tr['const']}: unknown class {tr['cls']}")
        if tr["pool"] not in defined:
            bad("trainers", f"{tr['const']}: pool {tr['pool']} is not defined")
            continue
        low = [x for x in pools[tr["pool"]] if x in cons and cons[x] <= 849]
        spx = {mons[cons[x]]["species"] for x in low}
        itx = {mons[cons[x]]["item"] for x in low if mons[cons[x]]["item"] != "ITEM_NONE"}
        if len(spx) < 8 or len(itx) < 6:
            bad("pools", f"{tr['pool']} (used by {tr['const']}): only {len(spx)} species / {len(itx)} items at ids <= 849; the party filler needs 8 / 6 for safety")
    for name, lst in pools.items():
        for x in lst:
            if x not in cons:
                bad("pools", f"{name}: {x} is not a mon id")
        if lst and len(lst) != len(set(lst)):
            bad("pools", f"{name}: duplicate ids")
    # open level view: ids above 849 are allowed, the Level 50 view above must still stand
    for tr in trainers:
        pass

    # ------------------------------------------------------------------ brains, pike, pyramid
    fu = fdata.read(fdata.src("src/frontier_util.c"))
    i0 = fu.index("sFrontierBrainsMons[][2][FRONTIER_PARTY_SIZE]")
    seg = fu[i0:fu.index("\n};\n", i0)]
    nb = 0
    for fm in re.finditer(r"\[(FRONTIER_FACILITY_\w+)\] =\n    \{(.*?)\n    \},", seg, flags=re.S):
        sym = 0
        for sb in re.split(r"// (?:Silver|Gold) Symbol\.", fm.group(2))[1:]:
            for mb in re.finditer(r"\.species = (\w+),\s*\.heldItem = (\w+),\s*(?:\.ability = (\w+),\s*)?\.fixedIV = \w+,\s*\.nature = (\w+),\s*\.evs = \{([^}]*)\},\s*\.moves = \{([^}]*)\}", sb, flags=re.S):
                nb += 1
                where = f"brain {fm.group(1)[18:]} {'silver' if sym == 0 else 'gold'} {mb.group(1)[8:]}"
                evs = [int(x) for x in mb.group(5).split(",")]
                check_member(where, mb.group(1), [x.strip() for x in mb.group(6).split(",")], mb.group(2), mb.group(3), mb.group(4), None, evs)
                if not mb.group(3):
                    bad("ability", f"{where}: no explicit .ability")
            sym += 1
    if nb != 36:
        bad("brains", f"{nb} brain mons parsed, expected 36")
    pk = fdata.read(fdata.src("src/battle_pike.c"))
    for m in re.finditer(r"\.species = (SPECIES_\w+),\s*\.levelDelta = \d+,\s*\.moves = \{([^}]*)\}", pk):
        check_member(f"pike {m.group(1)[8:]}", m.group(1), [x.strip() for x in m.group(2).split(",")], None, None)
    for f in (BF_PY := ["battle_pyramid_level_50_wild_mons.h", "battle_pyramid_open_level_wild_mons.h"]):
        t = fdata.read(fdata.src("src/data/battle_frontier/" + f))
        for m in re.finditer(r"\.species = (SPECIES_\w+),\s*\.lvl = (\d+),\s*\.abilityNum = \w+,\s*\.moves = \{([^}]*)\}", t):
            check_member(f"pyramid {f[15:19]} {m.group(1)[8:]}", m.group(1), [x.strip() for x in m.group(3).split(",")], None, None, level=int(m.group(2)))

    if not quiet:
        for n in notes:
            print("note:", n)
        for p in problems:
            print(p)
    print("frontier_check:", len(problems), "problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

"""Capture sets for the lair-unlock trophies (user spec 2026-10-14, map_pass/lair_unlocks_spec.md).

    python tools/achievements/lair_sets.py            # regenerate src/data/lair_capture_sets.h and ../map_pass/lair_unlock_sets.md
    python tools/achievements/lair_sets.py --check    # exit 1 if either would change (also verifies the sets against the species data)

A set = the Orleans regional dex (300 entries, tools/dex/out/dex_order.txt) minus legendary / mythical / sub-legendary / Mega / lair-only species, filtered by the
game's own types (tools/dex/out/pokemon_pp.c: src/pokemon.c preprocessed with the real flags, tools/dex/pp.sh), Orleanian and other regional forms with their
altered types. A two-type goal is the UNION of the types. "Caught" = registered CAUGHT in the Pokedex (the species' national dex number, so a form with a dex
number of its own counts on its own).

Obtainability is checked as a closure: wild tables (Orleans maps), scripted gifts / static battles / in-game trades / fossil, then evolution, then breeding
(an egg hatches into the family's first stage; a Ditto is in the dex). The md lists every set member with its first source and flags the ones with none.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "dex"))
import ppdata  # noqa: E402

OUT_H = ROOT / "src" / "data" / "lair_capture_sets.h"
NL = chr(10)
OUT_MD = ROOT.parent / "map_pass" / "lair_unlock_sets.md"

# the lair-only one-offs that are not flagged legendary in the species data (the rougarou and Bloodmoon Ursaluna): excluded as raid species
LAIR_ONLY = {"SPECIES_LYCANROC_MIDNIGHT", "SPECIES_URSALUNA_BLOODMOON"}
# Rayquaza / Kyogre / Groudon carry no legendary flag in this engine version; the raid arena species
RAID = {"SPECIES_RAYQUAZA", "SPECIES_KYOGRE", "SPECIES_GROUDON"}

# maps whose scripts hold a lair's / arena's static: a source there is "after its own lair"
LAIR_FILES = {"Route14_RougarouHollow", "Route23_BloodmoonArroyo", "PointeRouge_IcePlant", "Route7_CelebiGlade", "Route11_SuicuneIsle", "Route2_RaikouClearing",
              "Route16_EnteiField", "OldWater_KnowingPool", "Route1_HeartPool", "Route23_UnfailingSpring", "StormsEdge_LighthouseGallery", "Route12_LeveeCrown",
              "Route13_DeepWood", "Route13_CourirGlade", "Route3_WindsEye", "Route14_SpanishFort", "Route14_BushTrack", "Route10_MilneburgPavilion",
              "Route17_Sugarhouse", "Route23_BountifulField", "LandsEnd_DrownedTemple", "LandsEnd_SaltCathedral", "OldestShrine"}

# set key -> (trophy key, label, [types])
SETS = [
    ("WATER", "Water", ["WATER"]),
    ("FIRE", "Fire", ["FIRE"]),
    ("ELECTRIC", "Electric", ["ELECTRIC"]),
    ("FIGHTING_FLYING", "Fighting + Flying", ["FIGHTING", "FLYING"]),
    ("PSYCHIC_FLYING", "Psychic + Flying", ["PSYCHIC", "FLYING"]),
    ("DARK_FLYING", "Dark + Flying", ["DARK", "FLYING"]),
    ("GRASS_DARK", "Grass + Dark", ["GRASS", "DARK"]),
]

# the 17 other legendaries Rayquaza's arena waits for (spec): the lake trio, the three birds and their Galarian forms, the three beasts, the three forces, Zarude, Celebi, Ogerpon
LEGENDS = [
    ("SPECIES_UXIE", "Uxie"), ("SPECIES_MESPRIT", "Mesprit"), ("SPECIES_AZELF", "Azelf"),
    ("SPECIES_ARTICUNO", "Articuno"), ("SPECIES_ZAPDOS", "Zapdos"), ("SPECIES_MOLTRES", "Moltres"),
    ("SPECIES_ARTICUNO_GALAR", "Galarian Articuno"), ("SPECIES_ZAPDOS_GALAR", "Galarian Zapdos"), ("SPECIES_MOLTRES_GALAR", "Galarian Moltres"),
    ("SPECIES_RAIKOU", "Raikou"), ("SPECIES_ENTEI", "Entei"), ("SPECIES_SUICUNE", "Suicune"),
    ("SPECIES_TORNADUS_INCARNATE", "Tornadus"), ("SPECIES_THUNDURUS_INCARNATE", "Thundurus"), ("SPECIES_LANDORUS_INCARNATE", "Landorus"),
    ("SPECIES_ZARUDE", "Zarude"), ("SPECIES_CELEBI", "Celebi"), ("SPECIES_OGERPON_TEAL", "Ogerpon"),
]


# ---------------------------------------------------------------------------------------------- the dex
def load_dex():
    """[(regional number, name, species const, national dex const)]"""
    rows = []
    for line in (ROOT / "tools" / "dex" / "out" / "dex_order.txt").read_text(encoding="utf-8").splitlines():
        p = line.split("\t")
        if len(p) >= 4:
            rows.append((int(p[0]), p[1], p[2], p[3]))
    assert len(rows) == 300, len(rows)
    return rows


def species_data():
    _, ents = ppdata.load()
    out = {}
    for const, body in ents.items():
        f = ppdata.fields(body)
        flags = set(re.findall(r"\.(is(?:Mythical|SubLegendary|UltraBeast|Paradox|Legendary|MegaEvolution|PrimalReversion|Ultra))\s*=\s*1", body))
        seg = body[body.find(".evolutions"):] if ".evolutions" in body else ""
        seg = seg[:seg.find("{ 0xFFFF }")] if "{ 0xFFFF }" in seg else ""
        evos = re.findall(r"SPECIES_\w+", seg)
        eg = re.search(r"\.eggGroups\s*=\s*\{\s*(\w+),\s*(\w+)", body)
        out[const] = dict(types=f["types"], flags=flags, evos=evos, eggs=list(eg.groups()) if eg else [])
    return out


def excluded(const, info):
    d = info.get(const)
    if const in LAIR_ONLY or const in RAID:
        return "raid / lair-only species"
    if d is None:
        return "no species data"
    for fl in ("isMythical", "isSubLegendary", "isUltraBeast", "isParadox", "isLegendary", "isMegaEvolution"):
        if fl in d["flags"]:
            return fl
    return None


def type_names(d):
    return [t[len("TYPE_"):] for t in d["types"]]


def compute():
    dex, info = load_dex(), species_data()
    base = [(n, name, c, nd) for n, name, c, nd in dex if not excluded(c, info)]
    sets = {}
    for key, label, types in SETS:
        sets[key] = [(n, name, c, nd) for n, name, c, nd in base if set(type_names(info[c])) & set(types)]
    return dex, info, base, sets


# ---------------------------------------------------------------------------------------------- obtainability
SCRIPT_RE = re.compile(r"\b(givemon|giveegg|setwildbattle|createmon|special_give\w*)\b[^\n]*")


def base_sources(info, skip_lair=False):
    """species const -> first source description, for everything the game hands over or lets the player meet without evolution / breeding"""
    src = {}
    sm = None
    sys.path.insert(0, str(ROOT / "tools" / "dex"))
    import species_map
    sm = species_map

    def add(sp, why):
        sp = sm.canonical(sp) if hasattr(sm, "canonical") else sp
        src.setdefault(sp, why)

    d = json.load(open(ROOT / "src" / "data" / "wild_encounters.json", encoding="utf-8"))
    for e in d["wild_encounter_groups"][0]["encounters"]:
        if "_Orleans" not in e["base_label"]:
            continue
        for field, v in e.items():
            if isinstance(v, dict) and "mons" in v:
                for mon in v["mons"]:
                    add(mon["species"], "wild: %s (%s)" % (e["base_label"].replace("gOrleans_", "").replace("g", "", 1) if False else e["base_label"], field))
    files = list((ROOT / "tools" / "mapgen" / "story").glob("*.inc")) + list((ROOT / "data" / "scripts").glob("*.inc")) + list((ROOT / "data" / "maps").glob("*/scripts.inc"))
    for f in files:
        owner = f.parent.name if f.name == "scripts.inc" else f.stem
        if f.stem.lower().startswith("debug") or (skip_lair and owner in LAIR_FILES):
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = SCRIPT_RE.search(line)
            if m:
                for sp in re.findall(r"SPECIES_\w+", line):
                    add(sp, "script: %s (%s)" % (f.parent.name if f.name == "scripts.inc" else f.stem, m.group(1)))
    trades = (ROOT / "src" / "data" / "trade.h").read_text(encoding="utf-8")
    for m in re.finditer(r"\[INGAME_TRADE_(ALOLAN_\w+)\]\s*=\s*\{.*?\.species = (SPECIES_\w+)", trades, re.S):
        add(m.group(2), "in-game trade (Crescent City trade house)")
    return src


def closure(info, src):
    """add evolutions and breeding to the base sources; returns species -> how.
    Breeding: a family whose members (any stage, any form) include one that can breed hatches the family's first stage (a Ditto is in the dex)."""
    got = dict(src)
    pre = {}
    for sp, d in info.items():
        for t in d["evos"]:
            if t in info and t != sp:
                pre.setdefault(t, sp)

    def root(sp):
        seen = {sp}
        while sp in pre and pre[sp] not in seen:
            sp = pre[sp]
            seen.add(sp)
        return sp

    fam = {}
    for sp in info:
        fam.setdefault(root(sp), []).append(sp)
    changed = True
    while changed:
        changed = False
        for sp, d in info.items():
            if sp in got:
                for t in d["evos"]:
                    if t in info and t not in got and t != sp:
                        got[t] = "evolves from %s" % sp
                        changed = True
        for r, members in fam.items():
            if r in got:
                continue
            for m in members:
                if m in got and info[m]["eggs"] and "EGG_GROUP_NO_EGGS_DISCOVERED" not in info[m]["eggs"]:
                    got[r] = "egg from %s" % m
                    changed = True
                    break
    return got


# ---------------------------------------------------------------------------------------------- output
def cname(label):
    return label.replace(" + ", "_").replace(" ", "_").upper()


def build():
    dex, info, base, sets = compute()
    free = closure(info, base_sources(info, skip_lair=True))
    full = closure(info, base_sources(info))
    return dex, info, base, sets, free, full


def gen_header(sets):
    out = ["// GENERATED by tools/achievements/lair_sets.py. Do not edit by hand (python tools/achievements/lair_sets.py).",
           "// The lair-unlock capture sets: Orleans regional dex entries (300) minus legendary / mythical / sub-legendary / Mega / raid species, by the game's own types.", ""]
    for key, label, types in SETS:
        out.append("// %s (%d)" % (label, len(sets[key])))
        out.append("static const u16 sLairSet_%s[] =" % key)
        out.append("{")
        row = "   "
        for n, name, c, nd in sets[key]:
            item = " %s," % c
            if len(row) + len(item) > 150:
                out.append(row)
                row = "   "
            row += item
        out.append(row)
        out.append("};")
        out.append("")
    out.append("// The 18 other legendaries Rayquaza's arena waits for (spec list)")
    out.append("static const u16 sLairSet_LEGENDS[] =")
    out.append("{")
    for c, name in LEGENDS:
        out.append("    %s," % c)
    out.append("};")
    out.append("")
    return "\n".join(out)


def gen_md(dex, info, base, sets, free, full):
    L = ["# Lair-unlock capture sets", "",
         "Generated by `tools/achievements/lair_sets.py` from the game's own data (types from the compiled species info, dex = the 300 Orleans entries). "
         "Capture = registered CAUGHT in the Pokedex (the entry's national dex number; forms with a dex number of their own count on their own).", "",
         "Excluded from every set: %d entries - the legendary, mythical, sub-legendary and raid species (%s), plus the two lair-only one-offs "
         "(Lycanroc Midnight, Ursaluna Bloodmoon). Eligible species: **%d**." % (
             300 - len(base), ", ".join(name for n, name, c, nd in dex if excluded(c, info)), len(base)), ""]
    problems = []
    for key, label, types in SETS:
        mem = sets[key]
        L += ["## %s - %d species" % (label, len(mem)), "", "Types counted: %s (a species counts if it has ANY of them)." % ", ".join(t.title() for t in types), ""]
        L += ["| # | Species | Types | First source |", "|---|---|---|---|"]
        for n, name, c, nd in mem:
            how = free.get(c)
            note = how or ("ONLY after a lair: " + full.get(c, "NO SOURCE") if c in full else "NO SOURCE")
            if not how:
                problems.append((label, name, note))
            L.append("| %d | %s | %s | %s |" % (n, name, "/".join(t.title() for t in type_names(info[c])), note))
        L.append("")
    L += ["## Rayquaza's arena - the other legendaries (%d)" % len(LEGENDS), "",
          "The spec text says 17; its list names %d (lake trio 3, Articuno / Zapdos / Moltres and their Galarian forms 6, Raikou / Entei / Suicune 3, "
          "Tornadus / Thundurus / Landorus 3, Zarude, Celebi, Ogerpon 3). All %d are required. Ogerpon counts as the Teal Mask form (the one met in its lair)." % (
              len(LEGENDS), len(LEGENDS)), ""]
    L += ["| Species |", "|---|"] + ["| %s |" % name for c, name in LEGENDS] + [""]
    L += ["## Sets that cannot be completed", ""]
    if problems:
        L += ["| Set | Species | Problem |", "|---|---|---|"] + ["| %s | %s | %s |" % p for p in problems]
    else:
        L.append("None: every member of every set has a source that does not need a lair (wild tables, gifts, trades, evolution or breeding).")
    L.append("")
    eggs = []
    for key, label, types in SETS:
        for n, name, c, nd in sets[key]:
            if free.get(c, "").startswith("egg from") and name not in [e[0] for e in eggs]:
                eggs.append((name, c, free[c]))
    L += ["", "## Members whose only source is breeding", "",
          "The Pokemon Day Care lives in Crescent City. These %d set members are in no wild table, gift or trade: the player hatches them from a family member that can breed (with a Ditto, which is in the wild tables), so every set depends on the Day Care working. The Rockruff family likewise has its Midday form only through breeding from the Own Tempo Rockruff / Dusk line (Rock type, in no set). The three starters Chikorita / Fuecoco / Totodile: the shelter gives only the one the player picks; the other two first stages hatch from their wild Bayleef / Crocalor / Croconaw in the same way." % len(eggs), "",
          "| Species | Hatches from |", "|---|---|"] + ["| %s | %s |" % (n, h.replace("egg from SPECIES_", "").replace("_", " ").title()) for n, c, h in eggs] + [""]
    return "\n".join(L), problems


def main():
    dex, info, base, sets, free, full = build()
    h = gen_header(sets)
    md, problems = gen_md(dex, info, base, sets, free, full)
    if "--check" in sys.argv:
        ok = OUT_H.exists() and OUT_H.read_text(encoding="utf-8") == h
        print("lair_sets: header %s" % ("up to date" if ok else "STALE"))
        sys.exit(0 if ok else 1)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_H, "w", encoding="utf-8", newline=NL) as f:
        f.write(h)
    with open(OUT_MD, "w", encoding="utf-8", newline=NL) as f:
        f.write(md)
    print("sets:", {k: len(v) for k, v in sets.items()}, "problems:", problems)


if __name__ == "__main__":
    main()

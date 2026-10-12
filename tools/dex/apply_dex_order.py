"""Stage 6: the Orleans regional Pokedex.

The expansion's regional dex is a list of National Dex numbers (FOREACH_SPECIES_IN_HOENN_DEX_ORDER), one entry per
National Dex number. The sheet numbers alternate forms separately (Alolan Vulpix is #97, Vulpix #95), so each of the 22
sheet entries that shares a National Dex number with an earlier entry gets its own NATIONAL_DEX_* number (appended after
NATIONAL_DEX_PECHARUNT) and the species is pointed at it. The Hoenn list is then replaced by the sheet's 300 entries,
in sheet order (Megas and Primals stay under their base). Idempotent.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdata
import orleans_gen as g
import ppdata
import sheet_data
import species_map as sm

ROOT = g.ROOT
POKEDEX_H = ROOT / "include/constants/pokedex.h"
ORDERS_H = ROOT / "src/data/pokemon/pokedex_orders.h"
POKEDEX_C = ROOT / "src/pokedex.c"
GEN9 = cdata.SI_DIR / "gen_9_families.h"
OUT = Path(__file__).resolve().parent / "out"

# species that get their own national dex number -> the base national dex entry they sit beside in the static sort orders
DEX_FORMS = {
    "SPECIES_RAICHU_ALOLA": "RAICHU", "SPECIES_VULPIX_ALOLA": "VULPIX", "SPECIES_NINETALES_ALOLA": "NINETALES",
    "SPECIES_LILLIGANT_HISUI": "LILLIGANT", "SPECIES_ROTOM_HEAT": "ROTOM", "SPECIES_ROTOM_WASH": "ROTOM",
    "SPECIES_ROTOM_FROST": "ROTOM", "SPECIES_ROTOM_FAN": "ROTOM", "SPECIES_ROTOM_MOW": "ROTOM",
    "SPECIES_ROCKRUFF_OWN_TEMPO": "ROCKRUFF", "SPECIES_LYCANROC_DUSK": "LYCANROC", "SPECIES_LYCANROC_MIDNIGHT": "LYCANROC",
    "SPECIES_SANDSHREW_ALOLA": "SANDSHREW", "SPECIES_SANDSLASH_ALOLA": "SANDSLASH", "SPECIES_FLOETTE_ETERNAL": "FLOETTE",
    "SPECIES_URSALUNA_BLOODMOON": "URSALUNA", "SPECIES_ARTICUNO_GALAR": "ARTICUNO", "SPECIES_ZAPDOS_GALAR": "ZAPDOS",
    "SPECIES_MOLTRES_GALAR": "MOLTRES", "SPECIES_OGERPON_WELLSPRING": "OGERPON", "SPECIES_OGERPON_HEARTHFLAME": "OGERPON",
    "SPECIES_OGERPON_CORNERSTONE": "OGERPON",
}
# Megas / Tera forms that follow a form's own number
FOLLOWERS = {"SPECIES_FLOETTE_MEGA": "SPECIES_FLOETTE_ETERNAL", "SPECIES_RAICHU_MEGA_Y": "SPECIES_RAICHU_ALOLA",
             "SPECIES_LYCANROC_MIDNIGHT_MEGA": "SPECIES_LYCANROC_MIDNIGHT"}


def nd_name(const):
    return "NATIONAL_DEX_" + const[len("SPECIES_"):]


def main():
    t_pp, ents = ppdata.load()
    cons = sm.species_consts()
    rows = sorted([r for r in sheet_data.load_dex() if r["kind"] == "species"], key=lambda r: r["num"])
    order = []
    for r in rows:
        const = sm.orleanian_const(r["name"]) if r["name"] in sm.ORLEANIAN else sm.base_const(r["name"], cons)
        nd = nd_name(const) if const in DEX_FORMS else ppdata.fields(ents[const])["natdex"]
        order.append((r["num"], r["name"], const, nd))
    all_nd = [o[3] for o in order]
    assert len(set(all_nd)) == 300 and len(order) == 300, (len(set(all_nd)), len(order))
    custom = [nd_name(c) for c in DEX_FORMS]

    # --- national dex enum + count ---
    ph = POKEDEX_H.read_text(encoding="utf-8")
    if custom[0] + "," not in ph:
        add = ("    // Orleans: alternate forms that have their own regional dex number (tools/dex/apply_dex_order.py)\n"
               + "".join(f"    {c},\n" for c in custom))
        assert "    NATIONAL_DEX_PECHARUNT,\n};" in ph
        ph = ph.replace("    NATIONAL_DEX_PECHARUNT,\n};", "    NATIONAL_DEX_PECHARUNT,\n" + add + "};", 1)
        ph = ph.replace("#if P_GEN_9_POKEMON == TRUE\n    #define NATIONAL_DEX_COUNT  NATIONAL_DEX_PECHARUNT",
                        f"#if P_GEN_9_POKEMON == TRUE\n    #define NATIONAL_DEX_COUNT  {custom[-1]}", 1)
    # --- the Orleans regional list ---
    BS = chr(92)
    names = [nd[len("NATIONAL_DEX_"):] for nd in all_nd]
    body = "#define FOREACH_SPECIES_IN_HOENN_DEX_ORDER(F) " + BS + "\n" + "\n".join(f"    F({n}) " + BS for n in names)
    body = body.rstrip(BS).rstrip()
    a = ph.index("#define FOREACH_SPECIES_IN_HOENN_DEX_ORDER(F)")
    pos = a
    while True:
        e = ph.index("\n", pos)
        if not ph[pos:e].rstrip().endswith(BS):
            break
        pos = e + 1
    ph = ph[:a] + body + ph[e:]
    ph = re.sub(r"#define HOENN_DEX_COUNT \(HOENN_DEX_\w+ \+ 1\)", f"#define HOENN_DEX_COUNT (HOENN_DEX_{names[-1]} + 1)", ph)
    POKEDEX_H.write_text(ph, encoding="utf-8", newline="\n")

    # --- species natDexNum ---
    sf = cdata.SpeciesFiles()
    for const in DEX_FORMS:
        blk = sf.get(const)
        if blk is None:
            continue  # macro-built (Ogerpon masks), below
        sf.put(const, re.sub(r"\.natDexNum = \w+", ".natDexNum = " + nd_name(const), blk))
    for mega, base in FOLLOWERS.items():
        blk = sf.get(mega)
        sf.put(mega, re.sub(r"\.natDexNum = \w+", ".natDexNum = " + nd_name(base), blk))
    sf.save()
    t9 = GEN9.read_text(encoding="utf-8")
    if "isTeraform, dexNum)" not in t9:
        t9 = t9.replace("iconpalette, isTeraform)", "iconpalette, isTeraform, dexNum)", 1)
        t9 = re.sub(r"\.natDexNum = NATIONAL_DEX_OGERPON,", ".natDexNum = dexNum,", t9, count=1)
        mp = {"TEAL": "NATIONAL_DEX_OGERPON", "WELLSPRING": "NATIONAL_DEX_OGERPON_WELLSPRING",
              "HEARTHFLAME": "NATIONAL_DEX_OGERPON_HEARTHFLAME", "CORNERSTONE": "NATIONAL_DEX_OGERPON_CORNERSTONE"}

        def fix(m):
            return m.group(0)[:-2] + ", " + mp[m.group(1)] + "),"
        t9 = re.sub(r"\[SPECIES_OGERPON_(TEAL|WELLSPRING|HEARTHFLAME|CORNERSTONE)(?:_TERA)?\]\s*= OGERPON_SPECIES_INFO\([^\n]*\),", fix, t9)
        GEN9.write_text(t9, encoding="utf-8", newline="\n")

    # --- static sort orders (alphabetical, weight, height): list each new number right after its base entry ---
    po = ORDERS_H.read_text(encoding="utf-8")
    for const, base in DEX_FORMS.items():
        new = nd_name(const)
        if f"    {new},\n" in po:
            continue
        pat = re.compile(r"(?m)^    NATIONAL_DEX_" + base + r",[^\n]*\n")
        po = pat.sub(lambda m: m.group(0) + f"    {new},\n", po)
    ORDERS_H.write_text(po, encoding="utf-8", newline="\n")

    # --- visible text ---
    pc = POKEDEX_C.read_text(encoding="utf-8")
    pc = pc.replace('COMPOUND_STRING("HOENN region\'s POKéDEX"),   COMPOUND_STRING("HOENN DEX")',
                    'COMPOUND_STRING("ORLEANS region\'s POKéDEX"), COMPOUND_STRING("ORLEANS DEX")')
    POKEDEX_C.write_text(pc, encoding="utf-8", newline="\n")
    OUT.mkdir(exist_ok=True)
    (OUT / "dex_order.txt").write_text("\n".join(f"{n}\t{nm}\t{c}\t{nd}" for n, nm, c, nd in order), encoding="utf-8")
    print("regional dex entries:", len(order), "custom national numbers:", len(custom))


if __name__ == "__main__":
    main()

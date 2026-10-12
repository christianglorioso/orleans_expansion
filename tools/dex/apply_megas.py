"""Stage 3: Mega Evolutions.

* 16 custom Megas (new species cloned from the base species block, placeholder graphics), each with a new Mega stone item.
* Wiring for the sheet's choices among the existing official Megas: Mega Charizard is Y only, Mega Raichu = X on Raichu,
  Mega Alolan Raichu = Y on Alolan Raichu, Mega Chandelure belongs to the Orleanian Chandelure.
Stats/types/abilities of official Megas were set in stage 1. Idempotent.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_stats
import cdata
import orleans_gen as g
import sheet_data
import species_map as sm

OUT = Path(__file__).resolve().parent / "out"
ITEMS_C = g.ROOT / "include/constants/items.h"
ITEMS_D = g.ROOT / "src/data/items.h"
PLACEHOLDER_ICON = "Lucarionite"  # shared placeholder icon until commissioned item art exists


def insert_in_table(text, tname, line, first=False):
    m = re.search(r"static const (?:u16|struct FormChange) " + tname + r"\[\] =\s*\{\n", text)
    assert m, tname
    if line.strip() in text[m.end():m.end() + 1500].split("};")[0]:
        return text
    if first:
        return text[:m.end()] + line + text[m.end():]
    e = text.index("FORM_SPECIES_END", m.end())
    # step back to start of the line
    e = text.rindex("\n", 0, e) + 1
    return text[:e] + line + text[e:]


def add_items():
    ct = ITEMS_C.read_text(encoding="utf-8")
    dt = ITEMS_D.read_text(encoding="utf-8")
    ids = [int(x) for x in re.findall(r"^\s+ITEM_\w+ = (\d+),", ct, re.M)]
    nxt = max(ids) + 1
    add_c, add_d = "", ""
    for name, (base, item, disp) in sm.CUSTOM_MEGA_BASE.items():
        if f"    {item} = " in ct:
            continue
        spname = sheet_names[name]
        add_c += f"    {item} = {nxt},  // Orleans custom Mega stone (tools/dex/apply_megas.py)\n"
        nxt += 1
        add_d += (f'\n    [{item}] =\n    {{\n        .name = ITEM_NAME("{disp}"),\n        .price = 0,\n'
                  f'        .holdEffect = HOLD_EFFECT_MEGA_STONE,\n        .description = COMPOUND_STRING(\n'
                  f'            "This stone enables\\n"\n            "{spname} to Mega\\n"\n            "Evolve in battle."),\n'
                  f'        .pocket = POCKET_ITEMS,\n        .sortType = ITEM_TYPE_MEGA_STONE,\n'
                  f'        .type = ITEM_USE_BAG_MENU,\n        .fieldUseFunc = ItemUseOutOfBattle_CannotUse,\n'
                  f'        .flingPower = 80,\n        .iconPic = gItemIcon_{PLACEHOLDER_ICON},\n'
                  f'        .iconPalette = gItemIconPalette_{PLACEHOLDER_ICON},\n    }},\n')
    if add_c:
        ct = ct.replace("\n    ITEMS_COUNT,\n", "\n" + add_c + "\n    ITEMS_COUNT,\n", 1) if False else re.sub(
            r"\n(\n    ITEMS_COUNT,)", lambda m: "\n" + add_c + m.group(1), ct, count=1)
        ITEMS_C.write_text(ct, encoding="utf-8", newline="\n")
        idx = dt.rindex("};")
        dt = dt[:idx].rstrip("\n") + "\n" + add_d + "\n" + dt[idx:]
        ITEMS_D.write_text(dt, encoding="utf-8", newline="\n")
    return add_c.count("\n")


def main():
    global sheet_names
    g.ensure_species_consts()
    rows = {r["name"]: r for r in sheet_data.load_dex()}
    sheet_names = {n: n[5:] for n in sm.CUSTOM_MEGA_BASE}
    n_items = add_items()
    sf = cdata.SpeciesFiles()
    ftxt = g.FORM_SPECIES_H.read_text(encoding="utf-8")
    ctxt = g.FORM_CHANGE_H.read_text(encoding="utf-8")
    blocks = []
    for name, (base, item, disp) in sm.CUSTOM_MEGA_BASE.items():
        new = sm.CUSTOM_MEGAS[name]
        row = rows[name]
        p, m = sf.find(base)
        assert m, base
        raw = m.group(0)
        # ensure the base has a form species table and a form-change table
        mt = re.search(r"\.formSpeciesIdTable = (\w+)", raw)
        if mt:
            fst = mt.group(1)
        else:
            fst = g.table_name(base)
            ftxt = ftxt.rstrip("\n") + "\n" + g.form_table_text(fst, [base])
            raw = g.set_or_insert_field(raw, "formSpeciesIdTable", fst)
        mc = re.search(r"\.formChangeTable = (\w+)", raw)
        if mc:
            fct = mc.group(1)
        else:
            fct = f"s{g.pascal(base)}FormChangeTable"
            ctxt = ctxt.rstrip("\n") + (
                f"\nstatic const struct FormChange {fct}[] = {{\n"
                f"    {{FORM_CHANGE_FAINT,                         {base}}},\n"
                f"    {{FORM_CHANGE_END_BATTLE,                    {base}}},\n"
                f"    {{FORM_CHANGE_TERMINATOR}},\n}};\n")
            raw = g.set_or_insert_field(raw, "formChangeTable", fct, before=("formSpeciesIdTable",))
        sf.put(base, raw)
        ftxt = insert_in_table(ftxt, fst, f"    {new},\n")
        ctxt = insert_in_table(ctxt, fct, f"    {{FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,    {new}, {item}}},\n", first=True)
        # the Mega block
        b = raw.replace(f"    [{base}] =", f"    [{new}] =", 1)
        wa = [sm.ability_const(a) for a in row["abilities"]]
        b, done = apply_stats.edit_region(b, row, wa, set(apply_stats.STATS) | {"types", "abilities"})
        assert len(done) == 8, (name, done)
        b = g.remove_field(b, "evolutions")
        b = g.remove_field(b, "eggMoveLearnset")
        b = g.set_or_insert_field(b, "isMegaEvolution", "TRUE")
        blocks.append(b)

    # --- wiring of official Megas -------------------------------------------------------------
    # Charizard: Mega Y only
    ctxt = re.sub(r"    \{FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,    SPECIES_CHARIZARD_MEGA_X, ITEM_CHARIZARDITE_X\},\n", "", ctxt)
    # Raichu: X on Raichu, Y on Alolan Raichu
    if "sRaichuAlolaFormChangeTable" not in ctxt:
        ctxt = ctxt.replace("    {FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,    SPECIES_RAICHU_MEGA_Y, ITEM_RAICHUNITE_Y},\n", "", 1)
        i = ctxt.index("static const struct FormChange sRaichuFormChangeTable[]")
        j = ctxt.index("};\n", i) + 3
        ctxt = ctxt[:j] + (
            "\nstatic const struct FormChange sRaichuAlolaFormChangeTable[] = {\n"
            "#if P_GEN_9_MEGA_EVOLUTIONS\n"
            "    {FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,    SPECIES_RAICHU_MEGA_Y, ITEM_RAICHUNITE_Y},\n"
            "#endif\n"
            "    {FORM_CHANGE_FAINT,                         SPECIES_RAICHU_ALOLA},\n"
            "    {FORM_CHANGE_END_BATTLE,                    SPECIES_RAICHU_ALOLA},\n"
            "    {FORM_CHANGE_TERMINATOR},\n};\n") + ctxt[j:]
    p, m = sf.find("SPECIES_RAICHU_ALOLA")
    blk = m.group(0)
    blk = blk.replace(".formChangeTable = sRaichuFormChangeTable", ".formChangeTable = sRaichuAlolaFormChangeTable")
    if ".formChangeTable" not in blk:
        blk = g.set_or_insert_field(blk, "formChangeTable", "sRaichuAlolaFormChangeTable", before=("formSpeciesIdTable",))
    sf.put("SPECIES_RAICHU_ALOLA", blk)
    p, m = sf.find("SPECIES_RAICHU_MEGA_Y")
    blk = m.group(0)
    blk = blk.replace(".formChangeTable = sRaichuFormChangeTable", ".formChangeTable = sRaichuAlolaFormChangeTable")
    blk = blk.replace("sRaichuLevelUpLearnset", "sRaichuAlolaLevelUpLearnset").replace("sRaichuTeachableLearnset", "sRaichuAlolaTeachableLearnset")
    sf.put("SPECIES_RAICHU_MEGA_Y", blk)
    # Chandelure: the Orleanian Chandelure carries the official Mega
    i = ctxt.index("static const struct FormChange sChandelureFormChangeTable[]")
    j = ctxt.index("};\n", i)
    seg = ctxt[i:j].replace("SPECIES_CHANDELURE}", "SPECIES_CHANDELURE_ORLEANIAN}")
    ctxt = ctxt[:i] + seg + ctxt[j:]
    p, m = sf.find("SPECIES_CHANDELURE_ORLEANIAN")
    blk = m.group(0)
    if ".formChangeTable" not in blk:
        blk = g.set_or_insert_field(blk, "formChangeTable", "sChandelureFormChangeTable", before=("formSpeciesIdTable",))
        sf.put("SPECIES_CHANDELURE_ORLEANIAN", blk)

    g.FORM_SPECIES_H.write_text(ftxt, encoding="utf-8", newline="\n")
    g.FORM_CHANGE_H.write_text(ctxt, encoding="utf-8", newline="\n")
    sf.save()
    hdr = ("// Custom Mega Evolutions: generated by tools/dex/apply_megas.py from orleans_dex.xlsx.\n"
           "// Graphics, cry, footprint and overworld sprites are PLACEHOLDERS (the base species' assets) until the\n"
           "// commissioned art arrives; see tools/dex/commissioned_art_pending.md.\n\n")
    g.ORL_MEGAS_H.write_text(hdr + "\n".join(blocks), encoding="utf-8", newline="\n")
    g.include_in_species_info("orleans_megas.h")
    print("custom megas:", len(blocks), "new items:", n_items)


if __name__ == "__main__":
    main()

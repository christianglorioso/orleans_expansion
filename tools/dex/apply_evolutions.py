"""Stage 4: evolution changes from the sheet notes / design doc (Linking Cord for trades, regional/location conditions
replaced by items or time, etc). Also adds the Fais Do-Do Ribbon evolution item. Idempotent."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdata
import orleans_gen as g

F = "FRIENDSHIP_EVO_THRESHOLD"
EVOS = {
    "SPECIES_PIKACHU": "EVOLUTION({EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_RAICHU})",
    "SPECIES_EEVEE": ("EVOLUTION({EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_JOLTEON},\n"
                      "                            {EVO_ITEM, ITEM_WATER_STONE, SPECIES_VAPOREON},\n"
                      "                            {EVO_ITEM, ITEM_FIRE_STONE, SPECIES_FLAREON},\n"
                      "                            {EVO_ITEM, ITEM_LEAF_STONE, SPECIES_LEAFEON},\n"
                      "                            {EVO_ITEM, ITEM_ICE_STONE, SPECIES_GLACEON},\n"
                      f"                            {{EVO_LEVEL, 0, SPECIES_SYLVEON, CONDITIONS({{IF_MIN_FRIENDSHIP, {F}}}, {{IF_KNOWS_MOVE_TYPE, TYPE_FAIRY}})}},\n"
                      f"                            {{EVO_LEVEL, 0, SPECIES_ESPEON, CONDITIONS({{IF_MIN_FRIENDSHIP, {F}}}, {{IF_NOT_TIME, TIME_NIGHT}})}},\n"
                      f"                            {{EVO_LEVEL, 0, SPECIES_UMBREON, CONDITIONS({{IF_MIN_FRIENDSHIP, {F}}}, {{IF_TIME, TIME_NIGHT}})}})"),
    "SPECIES_SCYTHER": ("EVOLUTION({EVO_ITEM, ITEM_LINKING_CORD, SPECIES_SCIZOR, CONDITIONS({IF_HOLD_ITEM, ITEM_METAL_COAT})},\n"
                        "                            {EVO_ITEM, ITEM_BLACK_AUGURITE, SPECIES_KLEAVOR})"),
    "SPECIES_CRABRAWLER": "EVOLUTION({EVO_ITEM, ITEM_ICE_STONE, SPECIES_CRABOMINABLE})",
    "SPECIES_FEEBAS": "EVOLUTION({EVO_ITEM, ITEM_PRISM_SCALE, SPECIES_MILOTIC})",
    "SPECIES_PETILIL": ("EVOLUTION({EVO_ITEM, ITEM_SUN_STONE, SPECIES_LILLIGANT},\n"
                        "                            {EVO_ITEM, ITEM_FAIS_DO_DO_RIBBON, SPECIES_LILLIGANT_HISUI})"),
    "SPECIES_STANTLER": "EVOLUTION({EVO_LEVEL, 0, SPECIES_WYRDEER, CONDITIONS({IF_KNOWS_MOVE, MOVE_PSYSHIELD_BASH})})",
    "SPECIES_HAUNTER": "EVOLUTION({EVO_ITEM, ITEM_LINKING_CORD, SPECIES_GENGAR})",
    "SPECIES_POLIWHIRL": ("EVOLUTION({EVO_ITEM, ITEM_WATER_STONE, SPECIES_POLIWRATH},\n"
                          "                            {EVO_ITEM, ITEM_LINKING_CORD, SPECIES_POLITOED})"),
    "SPECIES_URSARING": ("EVOLUTION({EVO_ITEM, ITEM_PEAT_BLOCK, SPECIES_URSALUNA, CONDITIONS({IF_TIME, TIME_NIGHT})},\n"
                         "                            {EVO_NONE, 0, SPECIES_URSALUNA_BLOODMOON})"),
    "SPECIES_MAGNETON": "EVOLUTION({EVO_ITEM, ITEM_THUNDER_STONE, SPECIES_MAGNEZONE})",
    "SPECIES_BOLDORE": "EVOLUTION({EVO_ITEM, ITEM_LINKING_CORD, SPECIES_GIGALITH})",
    "SPECIES_GOOMY": "EVOLUTION({EVO_LEVEL, 40, SPECIES_SLIGGOO})",
    "SPECIES_SLIGGOO": "EVOLUTION({EVO_LEVEL, 50, SPECIES_GOODRA, CONDITIONS({IF_WEATHER, WEATHER_RAIN})})",
    "SPECIES_INKAY": "EVOLUTION({EVO_LEVEL, 30, SPECIES_MALAMAR, CONDITIONS({IF_TIME, TIME_NIGHT})})",
    "SPECIES_GIMMIGHOUL_CHEST": "EVOLUTION({EVO_LEVEL, 60, SPECIES_GHOLDENGO})",
    "SPECIES_ROCKRUFF_OWN_TEMPO": "EVOLUTION({EVO_LEVEL, 25, SPECIES_LYCANROC_DUSK})",
}

ITEMS_C = g.ROOT / "include/constants/items.h"
ITEMS_D = g.ROOT / "src/data/items.h"


def add_ribbon_item():
    ct = ITEMS_C.read_text(encoding="utf-8")
    if "ITEM_FAIS_DO_DO_RIBBON" in ct:
        return
    dt = ITEMS_D.read_text(encoding="utf-8")
    nxt = max(int(x) for x in re.findall(r"^\s+ITEM_\w+ = (\d+),", ct, re.M)) + 1
    ct = re.sub(r"\n(\n    ITEMS_COUNT,)",
                lambda m: f"\n    ITEM_FAIS_DO_DO_RIBBON = {nxt},  // Orleans: evolves Petilil into Hisuian Lilligant (tools/dex/apply_evolutions.py)\n" + m.group(1),
                ct, count=1)
    block = ('\n    [ITEM_FAIS_DO_DO_RIBBON] =\n    {\n        .name = ITEM_NAME("Fais Do-Do Ribbon"),\n        .price = 0,\n'
             '        .description = COMPOUND_STRING(\n            "A dance hall ribbon.\\n"\n            "Makes certain Pokémon\\n"\n            "evolve."),\n'
             '        .pocket = POCKET_ITEMS,\n        .sortType = ITEM_TYPE_EVOLUTION_STONE,\n        .type = ITEM_USE_PARTY_MENU,\n'
             '        .fieldUseFunc = ItemUseOutOfBattle_EvolutionStone,\n        .effect = gItemEffect_EvoItem,\n'
             '        .flingPower = 30,\n        .iconPic = gItemIcon_SunStone,\n        .iconPalette = gItemIconPalette_SunStone,\n    },\n')
    idx = dt.rindex("};")
    dt = dt[:idx].rstrip("\n") + "\n" + block + "\n" + dt[idx:]
    ITEMS_C.write_text(ct, encoding="utf-8", newline="\n")
    ITEMS_D.write_text(dt, encoding="utf-8", newline="\n")


def main():
    add_ribbon_item()
    sf = cdata.SpeciesFiles()
    n = 0
    for const, spec in EVOS.items():
        blk = sf.get(const)
        assert blk, const
        new = g.replace_field(blk, "evolutions", spec)
        if new != blk:
            sf.put(const, new)
            n += 1
    # Gimmighoul roaming form shares the evolution
    blk = sf.get("SPECIES_GIMMIGHOUL_ROAMING")
    if blk and ".evolutions" in blk:
        new = g.replace_field(blk, "evolutions", EVOS["SPECIES_GIMMIGHOUL_CHEST"])
        if new != blk:
            sf.put("SPECIES_GIMMIGHOUL_ROAMING", new)
            n += 1
    sf.save()
    print("evolution blocks changed:", n)


if __name__ == "__main__":
    main()

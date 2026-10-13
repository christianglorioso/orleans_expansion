"""Item rules for frontier_check.py.

An opponent item is accepted when it exists, has a battle effect, is not banned, fits the species, and is either
  - obtainable by the player in Orleans (the id appears in a reachable map/script source, or in the Arena lobby's BP stock), or
  - on ALLOWED_OPPONENT, the documented list of standard competitive items the facility lends or equips even though the player cannot
    obtain them (the Factory rental screen already hands out non-obtainable items; see frontier/01_plan.md "Items").
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BP_STOCK = {"ITEM_LEFTOVERS", "ITEM_WHITE_HERB", "ITEM_QUICK_CLAW", "ITEM_MENTAL_HERB", "ITEM_BRIGHT_POWDER", "ITEM_CHOICE_BAND", "ITEM_KINGS_ROCK", "ITEM_FOCUS_BAND", "ITEM_SCOPE_LENS"}

ALLOWED_OPPONENT = {
    # damage / role items
    "ITEM_LIFE_ORB", "ITEM_CHOICE_SPECS", "ITEM_CHOICE_SCARF", "ITEM_EXPERT_BELT", "ITEM_MUSCLE_BAND", "ITEM_WISE_GLASSES", "ITEM_ASSAULT_VEST", "ITEM_ROCKY_HELMET",
    "ITEM_FOCUS_SASH", "ITEM_WEAKNESS_POLICY", "ITEM_EVIOLITE", "ITEM_SHELL_BELL", "ITEM_BLACK_SLUDGE", "ITEM_LIGHT_CLAY", "ITEM_FLAME_ORB", "ITEM_TOXIC_ORB",
    "ITEM_LIGHT_BALL", "ITEM_THICK_CLUB", "ITEM_LEEK", "ITEM_DEEP_SEA_SCALE", "ITEM_DEEP_SEA_TOOTH", "ITEM_METAL_POWDER", "ITEM_AIR_BALLOON", "ITEM_HEAVY_DUTY_BOOTS",
    # berries
    "ITEM_SITRUS_BERRY", "ITEM_SALAC_BERRY", "ITEM_LIECHI_BERRY", "ITEM_PETAYA_BERRY", "ITEM_LEPPA_BERRY",
    # resist berries
    "ITEM_OCCA_BERRY", "ITEM_PASSHO_BERRY", "ITEM_WACAN_BERRY", "ITEM_RINDO_BERRY", "ITEM_YACHE_BERRY", "ITEM_CHOPLE_BERRY", "ITEM_KEBIA_BERRY", "ITEM_SHUCA_BERRY",
    "ITEM_COBA_BERRY", "ITEM_PAYAPA_BERRY", "ITEM_TANGA_BERRY", "ITEM_CHARTI_BERRY", "ITEM_KASIB_BERRY", "ITEM_HABAN_BERRY", "ITEM_COLBUR_BERRY", "ITEM_BABIRI_BERRY",
    "ITEM_ROSELI_BERRY",
    # type boosters
    "ITEM_CHARCOAL", "ITEM_MYSTIC_WATER", "ITEM_MAGNET", "ITEM_TWISTED_SPOON", "ITEM_SILVER_POWDER", "ITEM_SPELL_TAG", "ITEM_DRAGON_FANG", "ITEM_SHARP_BEAK",
    "ITEM_POISON_BARB", "ITEM_SOFT_SAND", "ITEM_BLACK_BELT", "ITEM_FAIRY_FEATHER",
}

# never on a trainer set (no effect in this build, one-use key/gimmick items, forms the opponent cannot use)
BANNED = {"ITEM_NONE", "ITEM_MASTER_BALL", "ITEM_RED_ORB", "ITEM_BLUE_ORB", "ITEM_SOUL_DEW", "ITEM_ADAMANT_ORB", "ITEM_LUSTROUS_ORB", "ITEM_GRISEOUS_ORB",
          "ITEM_RUSTED_SWORD", "ITEM_RUSTED_SHIELD", "ITEM_BOOSTER_ENERGY", "ITEM_TERA_ORB", "ITEM_DYNAMAX_BAND", "ITEM_MEGA_RING"}
BANNED_PREFIX = ("ITEM_ZMOVE", "ITEM_Z_")


def load_items():
    t = (ROOT / "src/data/items.h").read_text(encoding="utf-8", errors="replace")
    out = {}
    for m in re.finditer(r"\n    \[(ITEM_\w+)\] =\n    \{(.*?)\n    \},", t, flags=re.S):
        he = re.search(r"\.holdEffect = (\w+)", m.group(2))
        out[m.group(1)] = dict(hold=he.group(1) if he else "HOLD_EFFECT_NONE")
    return out


def obtainable(items):
    toks = set()
    for f in glob.glob(str(ROOT / "data/maps/*/scripts.inc")) + glob.glob(str(ROOT / "data/maps/*/map.json")) + glob.glob(str(ROOT / "data/scripts/*.inc")):
        try:
            toks |= set(re.findall(r"ITEM_[A-Z0-9_]+", open(f, encoding="utf-8", errors="replace").read()))
        except OSError:
            pass
    return (toks | BP_STOCK) & set(items)


def mega_stones(d):
    """species const -> set of Mega stones that species may hold (read from the form change tables)"""
    t = (ROOT / "src/data/pokemon/form_change_tables.h").read_text(encoding="utf-8")
    res = {}
    for mc in d.megas:
        m = re.search(r"FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,\s*" + mc + r",\s*(ITEM_\w+)", t)
        if not m:
            continue
        b = re.search(r"FORM_CHANGE_END_BATTLE,\s*(SPECIES_\w+)", t[m.end():]).group(1)
        res.setdefault(b, set()).add(m.group(1))
    return res


MASKS = {"SPECIES_OGERPON_WELLSPRING": "ITEM_WELLSPRING_MASK",
         "SPECIES_OGERPON_HEARTHFLAME": "ITEM_HEARTHFLAME_MASK", "SPECIES_OGERPON_CORNERSTONE": "ITEM_CORNERSTONE_MASK"}


def item_problem(item, info, sp, d, megas, obtainable_set):
    c = d.canonical(sp)
    if item in BANNED or item.startswith(BANNED_PREFIX):
        return "banned on trainer sets"
    hold = info["hold"]
    if item in megas.get(c, ()):
        return None
    if hold == "HOLD_EFFECT_MEGA_STONE" or item.endswith("ITE") or re.search(r"ITE_[XYZ]$", item):
        if hold == "HOLD_EFFECT_MEGA_STONE" or hold == "HOLD_EFFECT_NONE":
            return f"Mega stone that {sp[8:]} cannot use"
    if item in MASKS.values():
        return None if MASKS.get(c) == item else f"mask that {sp[8:]} cannot wear"
    if c in MASKS and item != MASKS[c]:
        return "Ogerpon must hold its own mask"
    if hold == "HOLD_EFFECT_NONE":
        return "has no battle hold effect"
    if item == "ITEM_EVIOLITE" and d.fully_evolved(c):
        return "Eviolite on a fully evolved species"
    if item == "ITEM_LIGHT_BALL" and c not in ("SPECIES_PIKACHU", "SPECIES_RAICHU", "SPECIES_RAICHU_ALOLA"):
        return "Light Ball on a non-Pikachu line"
    if item in obtainable_set or item in ALLOWED_OPPONENT:
        return None
    return "not obtainable in Orleans and not on the opponent allow-list"

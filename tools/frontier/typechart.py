"""The type chart as built (src/data/types_info.h, Gen 6+ matchups) and the item <-> type table."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TYPES = ["NORMAL", "FIGHTING", "FLYING", "POISON", "GROUND", "ROCK", "BUG", "GHOST", "STEEL", "FIRE", "WATER", "GRASS",
         "ELECTRIC", "PSYCHIC", "ICE", "DRAGON", "DARK", "FAIRY"]
COLS = ["NONE", "NORMAL", "FIGHTING", "FLYING", "POISON", "GROUND", "ROCK", "BUG", "GHOST", "STEEL", "MYSTERY", "FIRE", "WATER",
        "GRASS", "ELECTRIC", "PSYCHIC", "ICE", "DRAGON", "DARK", "FAIRY", "STELLAR"]
MACRO = {"______": 1.0, "BUG_RS": 1.0, "PSN_RS": 0.5, "PSY_RS": 2.0, "STL_RS": 1.0, "FIR_RS": 0.5}


def load():
    t = (ROOT / "src/data/types_info.h").read_text(encoding="utf-8")
    i = t.index("gTypeEffectivenessTable")
    j = t.index("};", i)
    chart = {}
    for m in re.finditer(r"\[TYPE_(\w+)\]\s*=\s*\{([^}]*)\}", t[i:j]):
        row = {}
        for col, tok in zip(COLS, [x.strip() for x in m.group(2).split(",")]):
            mm = re.fullmatch(r"X\(([\d.]+)\)", tok)
            row[col] = float(mm.group(1)) if mm else MACRO.get(tok, 1.0)
        chart[m.group(1)] = row
    return chart


CHART = load()


def eff(atk_type, def_types):
    """damage multiplier of an attacking type against a defender with the given types ('TYPE_X' constants)"""
    a = atk_type[5:]
    m = 1.0
    for t in def_types:
        m *= CHART[a][t[5:]]
    return m


# type-boosting held items (the 1.2x/1.1x item per type)
TYPE_ITEM = {"NORMAL": "ITEM_SILK_SCARF", "FIGHTING": "ITEM_BLACK_BELT", "FLYING": "ITEM_SHARP_BEAK", "POISON": "ITEM_POISON_BARB",
             "GROUND": "ITEM_SOFT_SAND", "ROCK": "ITEM_HARD_STONE", "BUG": "ITEM_SILVER_POWDER", "GHOST": "ITEM_SPELL_TAG",
             "STEEL": "ITEM_METAL_COAT", "FIRE": "ITEM_CHARCOAL", "WATER": "ITEM_MYSTIC_WATER", "GRASS": "ITEM_MIRACLE_SEED",
             "ELECTRIC": "ITEM_MAGNET", "PSYCHIC": "ITEM_TWISTED_SPOON", "ICE": "ITEM_NEVER_MELT_ICE", "DRAGON": "ITEM_DRAGON_FANG",
             "DARK": "ITEM_BLACK_GLASSES", "FAIRY": "ITEM_FAIRY_FEATHER"}

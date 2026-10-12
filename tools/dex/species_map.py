"""Sheet entry name -> SPECIES_ constant (engine species used for the base data)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Orleanian regional forms (new species added by apply_forms.py). Sheet names equal the base species name.
ORLEANIAN = ["Tangela", "Tangrowth", "Bonsly", "Sudowoodo", "Corphish", "Crawdaunt", "Koffing", "Weezing",
             "Krabby", "Kingler", "Voltorb", "Electrode", "Exeggcute", "Exeggutor", "Litwick", "Lampent",
             "Chandelure", "Budew", "Roselia", "Roserade", "Spearow", "Fearow"]

# the 16 custom Megas (sheet name -> new species constant)
CUSTOM_MEGAS = {
    "Mega Skeledirge": "SPECIES_SKELEDIRGE_MEGA", "Mega Roserade": "SPECIES_ROSERADE_ORLEANIAN_MEGA",
    "Mega Electrode": "SPECIES_ELECTRODE_ORLEANIAN_MEGA", "Mega Scyther": "SPECIES_SCYTHER_MEGA",
    "Mega Crawdaunt": "SPECIES_CRAWDAUNT_ORLEANIAN_MEGA", "Mega Kingler": "SPECIES_KINGLER_ORLEANIAN_MEGA",
    "Mega Weezing": "SPECIES_WEEZING_ORLEANIAN_MEGA", "Mega Tangrowth": "SPECIES_TANGROWTH_ORLEANIAN_MEGA",
    "Mega Sudowoodo": "SPECIES_SUDOWOODO_ORLEANIAN_MEGA", "Mega Exeggutor": "SPECIES_EXEGGUTOR_ORLEANIAN_MEGA",
    "Mega Fearow": "SPECIES_FEAROW_ORLEANIAN_MEGA", "Mega Quaquaval": "SPECIES_QUAQUAVAL_MEGA",
    "Mega Exploud": "SPECIES_EXPLOUD_MEGA", "Mega Kleavor": "SPECIES_KLEAVOR_MEGA",
    "Mega Serperior": "SPECIES_SERPERIOR_MEGA", "Mega Lycanroc": "SPECIES_LYCANROC_MIDNIGHT_MEGA",
}

EXPLICIT = {
    "Alolan Raichu": "SPECIES_RAICHU_ALOLA", "Mega Raichu": "SPECIES_RAICHU_MEGA_X",
    "Mega Alolan Raichu": "SPECIES_RAICHU_MEGA_Y", "Alolan Vulpix": "SPECIES_VULPIX_ALOLA",
    "Alolan Ninetales": "SPECIES_NINETALES_ALOLA", "Alolan Sandshrew": "SPECIES_SANDSHREW_ALOLA",
    "Alolan Sandslash": "SPECIES_SANDSLASH_ALOLA", "Hisuian Lilligant": "SPECIES_LILLIGANT_HISUI",
    "Galarian Corsola": "SPECIES_CORSOLA_GALAR", "Galarian Articuno": "SPECIES_ARTICUNO_GALAR",
    "Galarian Zapdos": "SPECIES_ZAPDOS_GALAR", "Galarian Moltres": "SPECIES_MOLTRES_GALAR",
    "Rockruff (Own Tempo)": "SPECIES_ROCKRUFF_OWN_TEMPO", "Lycanroc (Midday)": "SPECIES_LYCANROC_MIDDAY",
    "Lycanroc (Dusk)": "SPECIES_LYCANROC_DUSK", "Lycanroc (Midnight)": "SPECIES_LYCANROC_MIDNIGHT",
    "Floette": "SPECIES_FLOETTE", "Floette (Eternal Flower)": "SPECIES_FLOETTE_ETERNAL",
    "Mega Floette": "SPECIES_FLOETTE_MEGA", ("Gimmighoul"): "SPECIES_GIMMIGHOUL_CHEST",
    "Ogerpon (Teal Mask)": "SPECIES_OGERPON_TEAL", "Ogerpon (Wellspring Mask)": "SPECIES_OGERPON_WELLSPRING",
    "Ogerpon (Hearthflame Mask)": "SPECIES_OGERPON_HEARTHFLAME", "Ogerpon (Cornerstone Mask)": "SPECIES_OGERPON_CORNERSTONE",
    "Primal Groudon": "SPECIES_GROUDON_PRIMAL", "Primal Kyogre": "SPECIES_KYOGRE_PRIMAL",
    "Mega Rayquaza": "SPECIES_RAYQUAZA_MEGA", "Mega Charizard": "SPECIES_CHARIZARD_MEGA_Y",
    "Rotom-Heat": "SPECIES_ROTOM_HEAT", "Rotom-Wash": "SPECIES_ROTOM_WASH", "Rotom-Frost": "SPECIES_ROTOM_FROST",
    "Rotom-Fan": "SPECIES_ROTOM_FAN", "Rotom-Mow": "SPECIES_ROTOM_MOW", "Ursaluna Bloodmoon": "SPECIES_URSALUNA_BLOODMOON",
}


def species_consts():
    src = (ROOT / "include/constants/species.h").read_text(encoding="utf-8")
    raw = dict(re.findall(r"SPECIES_(\w+) = (\w+),", src))
    out = {}
    for k, v in raw.items():
        while not v.isdigit() and v.startswith("SPECIES_") and v[8:] in raw:
            v = raw[v[8:]]
        out[k] = v
    return out


def canonical(const, consts=None):
    """resolve alias constants (SPECIES_MIMIKYU -> SPECIES_MIMIKYU_DISGUISED)"""
    src = (ROOT / "include/constants/species.h").read_text(encoding="utf-8")
    raw = dict(re.findall(r"SPECIES_(\w+) = (\w+),", src))
    v = const
    while v.startswith("SPECIES_") and v[8:] in raw and not raw[v[8:]].isdigit():
        v = raw[v[8:]]
    return v


def base_const(name, consts=None):
    """species constant of the sheet entry; Orleanian forms are resolved by apply_forms (see orleanian_const)."""
    consts = consts or species_consts()
    if name in EXPLICIT:
        return canonical(EXPLICIT[name])
    if name in CUSTOM_MEGAS:
        return CUSTOM_MEGAS[name]
    n = name
    if n.startswith("Mega "):
        n = n[5:] + "_MEGA"
    c = re.sub(r"[^A-Z0-9]+", "_", n.upper().replace("É", "E")).strip("_")
    if c in consts:
        return canonical("SPECIES_" + c)
    return None


def orleanian_const(name):
    return "SPECIES_" + name.upper().replace(" ", "_") + "_ORLEANIAN"


def ability_const(name):
    """sheet ability name -> ABILITY_ constant (custom abilities included, added by apply_stats)"""
    if not name:
        return "ABILITY_NONE"
    n = re.sub(r"\s*\(custom.*\)$", "", str(name).strip())
    n = n.replace("'", "")
    return "ABILITY_" + re.sub(r"[^A-Z0-9]+", "_", n.upper()).strip("_")


def ability_consts():
    src = (ROOT / "include/constants/abilities.h").read_text(encoding="utf-8")
    return set(re.findall(r"ABILITY_(\w+)\s*=", src))

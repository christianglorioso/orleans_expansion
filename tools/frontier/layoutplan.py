"""Which species sit in which part of the 882-slot mon table (the tier plan of 01_plan.md).

Index layout (kept from vanilla, the engine and the trainer windows depend on it):
  T0   0-109   110 slots   first-stage / baby species
  T1   110-161  52         the rest of the unevolved species + the weakest finished ones
  A1   162-266 105         105 finished species, first sets            (same species list as A2)
  A2   267-371 105         the same 105 species, second sets
  B1   372-467  96         96 strongest non-legend species, first sets (same list in B1-B4)
  B2   468-563, B3 564-659, B4 660-755
  L    756-849  94         legends and pseudo-legends, three or four sets each (Level 50 and Open Level)
  H    850-881  32         HIGH TIER (Open Level only): 8 species x 4 sets
"""
import typechart as tc

TIERS = [("T0", 0, 109), ("T1", 110, 161), ("A1", 162, 266), ("A2", 267, 371), ("B1", 372, 467), ("B2", 468, 563),
         ("B3", 564, 659), ("B4", 660, 755), ("L", 756, 849), ("H", 850, 881)]
NUM_MONS = 882

# banned for the player in the Frontier (isFrontierBanned): never used by opponents either
# Smeargle: the Orleans sheet gives it Sketch and nothing else, so a trainer Smeargle could never attack (note in audit/11_fix_coordination.md)
EXCLUDED = {"SPECIES_SMEARGLE"}
# NO legendaries or mythicals anywhere in the Frontier (user decision 2026-10-13): everything the species data flags as legendary / sub-legendary /
# restricted / mythical / ultra beast / paradox, plus the ones the flags miss (Bloodmoon Ursaluna, Gimmighoul and Gholdengo are treated as legends).
LEGEND_FLAGS = ("isLegendary", "isMythical", "isSubLegendary", "isRestrictedLegendary", "isUltraBeast", "isParadox")
LEGEND_EXTRA = {"SPECIES_URSALUNA_BLOODMOON", "SPECIES_GIMMIGHOUL_CHEST", "SPECIES_GHOLDENGO"}
BANNED = {"SPECIES_ZARUDE", "SPECIES_CELEBI", "SPECIES_GROUDON", "SPECIES_KYOGRE", "SPECIES_RAYQUAZA"}
LEGENDS = []   # kept for older imports
HIGH_TIER = ["SPECIES_DRAGONITE", "SPECIES_METAGROSS", "SPECIES_DRAGAPULT", "SPECIES_GOODRA", "SPECIES_ARCHALUDON", "SPECIES_URSALUNA", "SPECIES_EXCADRILL", "SPECIES_GENGAR"]
OGERPON_MASK = {}


def is_legend(dex, sp):
    import re
    c = dex.canonical(sp)
    return c in LEGEND_EXTRA or any(re.search(r"\." + f + r" = (TRUE|1)", dex.ents[c]) for f in LEGEND_FLAGS)


def plan(dex):
    """returns dict tier -> list of species (the species list of that group, in table order)"""
    allsp = [s for s in dex.species if s not in BANNED and s not in EXCLUDED and not is_legend(dex, s)]
    bst = lambda s: sum(dex.stats(s).values())
    key = lambda s: (bst(s), s)
    fe = sorted([s for s in allsp if dex.fully_evolved(s)], key=key)
    nfe = sorted([s for s in allsp if not dex.fully_evolved(s)], key=key)
    out = {}
    out["T0"] = nfe[:110]
    t1 = nfe[110:] + [s for s in fe if s not in nfe][:52 - len(nfe[110:])]
    out["T1"] = sorted(t1, key=key)
    out["A"] = sorted(fe[:105], key=key)
    out["B"] = sorted(fe[-96:], key=key)
    out["L_species"] = sorted(fe[-31:], key=key)   # the 31 strongest finished non-legend species (pseudo-legends first in BST order)
    out["H_species"] = HIGH_TIER
    return out

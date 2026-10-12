"""Rebuild every Orleans wild table (labels g<Map>_Orleans and g<Map>_Orleans_Night) from the mockup notes.

Time-of-day layout (OW_TIME_OF_DAY_ENCOUNTERS TRUE, fallback TIME_MORNING, fallback enabled):
  * g<Map>_Orleans        (no suffix -> TIME_MORNING slot)  = DAY pool + every unsplit table (fishing, unsplit water).
                            Day and Evening have no tables of their own, so they fall back to this one.
  * g<Map>_Orleans_Night  (TIME_NIGHT slot)                  = NIGHT land pool, plus a night water pool where the
                            mockup's day/night lists cover the water. Anything absent (fishing, unsplit water)
                            falls back per-area to the morning/day table.

Usage: python wild_review.py            (dry run, prints tables + warnings)
       python wild_review.py --write    (atomic write of src/data/wild_encounters.json)
"""
import json, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evo import load as load_evo

ROOT = r"C:\Users\chris\orleans_expansion\orleans_expansion"
PATH = os.path.join(ROOT, "src", "data", "wild_encounters.json")
WRITE = "--write" in sys.argv
WARN = []
_minlvl, _ = load_evo()
species_h = open(os.path.join(ROOT, "include/constants/species.h"), encoding="utf-8").read()
KNOWN = set(re.findall(r"\b(SPECIES_\w+)\s*=", species_h))
ALIAS = dict(re.findall(r"\b(SPECIES_\w+)\s*=\s*(SPECIES_\w+)\s*,", species_h))


def evo_min(s):
    full = "SPECIES_" + s
    return _minlvl(ALIAS.get(full, full))


# ---------------------------------------------------------------- level helpers
def land(lo, hi, sp):
    """12 slots (20/20/10/10/10/10/5/5/4/4/1/1): commons lo..hi-1, uncommon lo+1..hi, rare lo+2..hi."""
    assert len(sp) == 12, sp
    out = []
    for i, s in enumerate(sp):
        a, b = (lo, hi - 1) if i < 6 else (lo + 1, hi) if i < 8 else (lo + 2, hi)
        out.append((s, a, b))
    return out


def water(lo, hi, sp):
    """5 slots (60/30/5/4/1)."""
    assert len(sp) == 5, sp
    return [(s, lo, hi) for s in sp[:3]] + [(sp[3], lo + 1, hi), (sp[4], lo + 2, hi)]


RW = (15, 20)  # boat-revisit band for water on maps reached before gym 4 (the player's boat opens after gym 4)


def early(old_sp, good_sp, sup_sp):
    """Pre-gym-4 maps. Old Rod (start): 5-10. Good Rod (Route 5, before gym 4): 10-18.
    Super Rod (Kingfisher, after gym 4) is revisit content: kept at/below Route 6's Super Rod (20-26)."""
    assert len(old_sp) == 2 and len(good_sp) == 3 and len(sup_sp) == 5
    return ([(s, 5, 10) for s in old_sp] + [(s, 10, 18) for s in good_sp]
            + [(s, 15, 20) for s in sup_sp[:2]] + [(s, 17, 22) for s in sup_sp[2:4]] + [(sup_sp[4], 20, 24)])


def banded(lo, hi, old_sp, good_sp, sup_sp):
    """Post-gym-4 maps: old rod just under the band, good rod = band, super rod above it."""
    assert len(old_sp) == 2 and len(good_sp) == 3 and len(sup_sp) == 5
    return ([(s, lo - 5, lo) for s in old_sp] + [(s, lo, hi) for s in good_sp]
            + [(s, lo + 3, hi + 5) for s in sup_sp[:4]] + [(sup_sp[4], hi + 2, hi + 5)])


# ---------------------------------------------------------------- tables
T = []  # (map, label, rate_land, day:{land,water,fish}, night:{land,water})


def add(mapc, label, day, night=None, land_rate=20):
    T.append((mapc, label, land_rate, day, night or {}))


R = lambda n: f"MAP_ORLEANS_ROUTE{n}"

# ===== Route 1 (before gym 1) - wild 3-6
add(R(1), "gRoute1_Orleans", land_rate=21, day=dict(
    land=land(3, 6, ["ZIGZAGOON", "RATTATA", "STARLY", "SPEAROW", "BIDOOF", "WINGULL",
                     "CORPHISH", "STARLY", "SPEAROW", "WINGULL", "BULBASAUR", "MUDKIP"]),
    fish=early(["MAGIKARP", "MAGIKARP"], ["MAGIKARP", "CORPHISH", "CORPHISH"],
               ["CORPHISH", "CORPHISH", "CORPHISH", "CORPHISH", "CORPHISH"])),
    night=dict(
    land=land(3, 6, ["ZUBAT", "RATTATA", "ZUBAT", "BIDOOF", "KOFFING", "RATTATA",
                     "CORPHISH", "KOFFING", "BIDOOF", "CORPHISH", "LITWICK", "MUDKIP"])))

# ===== Isle Marais (home town; no grass, dock fishing; water = boat revisit after gym 4)
add("MAP_ISLE_MARAIS", "gIsleMarais_Orleans", day=dict(
    water=water(*RW, ["CORPHISH", "WINGULL", "BIDOOF", "PSYDUCK", "CORPHISH"]),
    fish=early(["MAGIKARP", "MAGIKARP"], ["MAGIKARP", "CORPHISH", "CORPHISH"],
               ["CORPHISH", "CORPHISH", "CORPHISH", "MAGIKARP", "CORPHISH"])))

# ===== Old Water (opens before gym 1; no grass, dock fishing)
add("MAP_OLD_WATER", "gOldWater_Orleans", day=dict(
    water=water(*RW, ["WOOPER", "PSYDUCK", "CORPHISH", "BIDOOF", "WOOPER"]),
    fish=early(["MAGIKARP", "BARBOACH"], ["BARBOACH", "WOOPER", "CORPHISH"],
               ["BARBOACH", "WOOPER", "CORPHISH", "BARBOACH", "CORPHISH"])))

# ===== Route 2 (after gym 1) - wild 5-9
add(R(2), "gRoute2_Orleans", day=dict(
    land=land(5, 9, ["ZIGZAGOON", "PIKIPEK", "RATTATA", "EKANS", "PIKIPEK", "ZIGZAGOON",
                     "PICHU", "PIKACHU", "PICHU", "PIKACHU", "JOLTIK", "JOLTIK"]),
    water=water(*RW, ["TENTACOOL", "WINGULL", "TENTACOOL", "WINGULL", "TENTACOOL"]),
    fish=early(["MAGIKARP", "BARBOACH"], ["BARBOACH", "BARBOACH", "BARBOACH"],
               ["BARBOACH", "BARBOACH", "BARBOACH", "TENTACOOL", "TENTACOOL"])),
    night=dict(
    land=land(5, 9, ["ZUBAT", "HOOTHOOT", "ZUBAT", "RATTATA", "EKANS", "HOOTHOOT",
                     "RATTATA", "EKANS", "PIKACHU", "PIKACHU", "VOLTORB", "VOLTORB"])))

# ===== Storm's Edge (gym 2 town; no grass; pier fishing)
add("MAP_STORMS_EDGE", "gStormsEdge_Orleans", day=dict(
    water=water(*RW, ["TENTACOOL", "WINGULL", "TENTACOOL", "WINGULL", "VOLTORB"]),
    fish=early(["MAGIKARP", "BARBOACH"], ["BARBOACH", "BARBOACH", "BARBOACH"],
               ["BARBOACH", "BARBOACH", "BARBOACH", "TENTACOOL", "TENTACOOL"])))

# ===== Route 3 (after gym 2) - wild 8-12
add(R(3), "gRoute3_Orleans", day=dict(
    land=land(8, 12, ["ODDISH", "BELLSPROUT", "PARAS", "PSYDUCK", "DUCKLETT", "WOOPER",
                      "SURSKIT", "DEWPIDER", "PARAS", "SURSKIT", "DITTO", "DITTO"]),
    water=water(*RW, ["PSYDUCK", "SURSKIT", "WOOPER", "DUCKLETT", "DEWPIDER"]),
    fish=early(["MAGIKARP", "WOOPER"], ["BARBOACH", "WOOPER", "PSYDUCK"],
               ["PSYDUCK", "BARBOACH", "BARBOACH", "PSYDUCK", "BARBOACH"])),
    night=dict(
    land=land(8, 12, ["ZUBAT", "ODDISH", "ZUBAT", "BELLSPROUT", "PARAS", "WOOPER",
                      "SWINUB", "HOOTHOOT", "SWINUB", "HOOTHOOT", "SWINUB", "HOOTHOOT"]),
    water=water(*RW, ["WOOPER", "BARBOACH", "WOOPER", "BARBOACH", "WOOPER"])))

# ===== Crescent City (hub, gym 3; reached after gym 2, before Route 4) - mockup gives one list, no day/night split
add("MAP_CRESCENT_CITY", "gCrescentCity_Orleans", day=dict(
    land=[("WHISMUR", 10, 13), ("GASTLY", 10, 13), ("BUDEW", 10, 13), ("DROWZEE", 10, 13),
          ("PETILIL", 10, 13), ("TANGELA", 11, 14), ("WATTREL", 11, 14), ("EEVEE", 11, 14),
          ("SCYTHER", 12, 14), ("FENNEKIN", 12, 14), ("SMEARGLE", 12, 14), ("EEVEE", 14, 14)],
    water=water(*RW, ["PSYDUCK", "WINGULL", "DUCKLETT", "SURSKIT", "BARBOACH"]),
    fish=early(["MAGIKARP", "WOOPER"], ["BARBOACH", "WOOPER", "PSYDUCK"],
               ["PSYDUCK", "BARBOACH", "BARBOACH", "PSYDUCK", "BARBOACH"])))

# ===== Route 4 (after gym 3) - wild 13-17
add(R(4), "gRoute4_Orleans", day=dict(
    land=land(13, 17, ["ROOKIDEE", "DODUO", "SANDSHREW", "EKANS", "VOLTORB", "ROOKIDEE",
                       "DODUO", "SANDSHREW", "VOLTORB", "EKANS", "FERROSEED", "FERROSEED"]),
    water=water(*RW, ["PSYDUCK", "WINGULL", "VOLTORB", "DUCKLETT", "BUIZEL"]),
    fish=early(["MAGIKARP", "BARBOACH"], ["BARBOACH", "BARBOACH", "POLIWAG"],
               ["BARBOACH", "POLIWAG", "BARBOACH", "PSYDUCK", "BUIZEL"])),
    night=dict(
    land=land(13, 17, ["ZUBAT", "KOFFING", "ZUBAT", "EKANS", "SANDSHREW", "HOOTHOOT",
                       "VOLTORB", "KOFFING", "HOOTHOOT", "SANDSHREW", "MAGNEMITE", "MAGNEMITE"])))

# ===== Route 5 (after gym 3; Good Rod here) - wild 14-18
add(R(5), "gRoute5_Orleans", day=dict(
    land=land(14, 18, ["PSYDUCK", "DUCKLETT", "POLIWAG", "BUIZEL", "DODUO", "ROOKIDEE",
                       "PSYDUCK", "DUCKLETT", "BUIZEL", "POLIWAG", "DODUO", "ROOKIDEE"]),
    water=water(*RW, ["PSYDUCK", "BUIZEL", "DUCKLETT", "POLIWAG", "BUIZEL"]),
    fish=early(["MAGIKARP", "POLIWAG"], ["BARBOACH", "WOOPER", "BUIZEL"],
               ["BUIZEL", "WOOPER", "BUIZEL", "WOOPER", "BUIZEL"])),
    night=dict(
    land=land(14, 18, ["ZUBAT", "HOOTHOOT", "ZUBAT", "PSYDUCK", "POLIWAG", "WOOPER",
                       "HOOTHOOT", "PSYDUCK", "WOOPER", "POLIWAG", "CRAMORANT", "CRAMORANT"]),
    water=water(*RW, ["PSYDUCK", "POLIWAG", "WOOPER", "BARBOACH", "CRAMORANT"])))

# ===== Pointe Rouge (gym 4 town; tall grass on the east bank south of the lower bridge, a Gulf riverbank) - wild 15-19,
# a notch above Route 5's 14-18 (and Route 4's 13-17), under Route 6's 17-21. Species are the neighbours' (Routes 4 and 5).
add("MAP_POINTE_ROUGE", "gPointeRouge_Orleans", day=dict(
    land=land(15, 19, ["PSYDUCK", "DUCKLETT", "POLIWAG", "BUIZEL", "DODUO", "ROOKIDEE",
                       "WOOPER", "VOLTORB", "PSYDUCK", "DODUO", "CRAMORANT", "CRAMORANT"]),
    water=water(*RW, ["PSYDUCK", "DUCKLETT", "BUIZEL", "VOLTORB", "CRAMORANT"]),
    fish=early(["MAGIKARP", "POLIWAG"], ["BARBOACH", "WOOPER", "BUIZEL"],
               ["BUIZEL", "WOOPER", "BUIZEL", "WOOPER", "BUIZEL"])),
    night=dict(
    land=land(15, 19, ["ZUBAT", "HOOTHOOT", "ZUBAT", "WOOPER", "POLIWAG", "KOFFING",
                       "PSYDUCK", "MAGNEMITE", "HOOTHOOT", "WOOPER", "CRAMORANT", "CRAMORANT"])))

# ===== Route 6 (boat, after gym 4) - wild 17-21
add(R(6), "gRoute6_Orleans", day=dict(
    land=land(17, 21, ["ODDISH", "BELLSPROUT", "KRABBY", "DUCKLETT", "WINGULL", "PSYDUCK",
                       "ODDISH", "BELLSPROUT", "KRABBY", "SURSKIT", "DEWPIDER", "DEWPIDER"]),
    water=water(17, 21, ["PSYDUCK", "SURSKIT", "WINGULL", "DUCKLETT", "DEWPIDER"]),
    fish=banded(17, 21, ["MAGIKARP", "BARBOACH"], ["BARBOACH", "BARBOACH", "KRABBY"],
                ["KRABBY", "BARBOACH", "KRABBY", "BARBOACH", "WHISCASH"])),
    night=dict(
    land=land(17, 21, ["ZUBAT", "ODDISH", "ZUBAT", "BELLSPROUT", "KRABBY", "SWINUB",
                       "PSYDUCK", "SWINUB", "ODDISH", "BELLSPROUT", "TRUBBISH", "TRUBBISH"]),
    water=water(17, 21, ["PSYDUCK", "KRABBY", "PSYDUCK", "KRABBY", "PSYDUCK"])))

# ===== Route 7 - wild 19-23
add(R(7), "gRoute7_Orleans", day=dict(
    land=land(19, 23, ["WOOPER", "ODDISH", "BELLSPROUT", "CROAGUNK", "PARAS", "FOONGUS",
                       "NINCADA", "CROAGUNK", "FOONGUS", "NINCADA", "BONSLY", "BONSLY"]),
    water=water(19, 23, ["WOOPER", "BARBOACH", "WOOPER", "QUAGSIRE", "QUAGSIRE"]),
    fish=banded(19, 23, ["BARBOACH", "WOOPER"], ["WOOPER", "BARBOACH", "BARBOACH"],
                ["QUAGSIRE", "BARBOACH", "QUAGSIRE", "BARBOACH", "WHISCASH"])),
    night=dict(
    land=land(19, 23, ["ZUBAT", "HOOTHOOT", "ZUBAT", "ODDISH", "BELLSPROUT", "CROAGUNK",
                       "SWINUB", "FOONGUS", "PARAS", "NOIBAT", "SEVIPER", "SEVIPER"])))

# ===== Route 8 - wild 21-25
add(R(8), "gRoute8_Orleans", day=dict(
    land=land(21, 25, ["GLOOM", "WEEPINBELL", "GLOOM", "WEEPINBELL", "GLOOM", "WEEPINBELL",
                       "GLOOM", "WEEPINBELL", "GLOOM", "WEEPINBELL", "CRABRAWLER", "CRABRAWLER"]),
    water=water(21, 25, ["TENTACOOL", "FRILLISH", "QUAGSIRE", "SURSKIT", "CRABRAWLER"]),
    fish=banded(21, 25, ["BARBOACH", "BARBOACH"], ["BARBOACH", "BARBOACH", "BARBOACH"],
                ["BARBOACH", "BARBOACH", "BARBOACH", "CRABRAWLER", "INKAY"])),
    night=dict(
    land=land(21, 25, ["ZUBAT", "GLOOM", "ZUBAT", "WEEPINBELL", "SWINUB", "GLOOM",
                       "WEEPINBELL", "SWINUB", "GLOOM", "WEEPINBELL", "INKAY", "INKAY"]),
    water=water(21, 25, ["FRILLISH", "QUAGSIRE", "FRILLISH", "QUAGSIRE", "INKAY"])))

# ===== Route 9 - wild 23-27
add(R(9), "gRoute9_Orleans", day=dict(
    land=land(23, 27, ["SANDILE", "FOONGUS", "CROAGUNK", "GLOOM", "WEEPINBELL", "SANDILE",
                       "FOONGUS", "CROAGUNK", "GLOOM", "WEEPINBELL", "CROCONAW", "CROCONAW"]),
    water=water(23, 27, ["BARBOACH", "QUAGSIRE", "BARBOACH", "QUAGSIRE", "QUAGSIRE"]),
    fish=banded(23, 27, ["BARBOACH", "BARBOACH"], ["BARBOACH", "BARBOACH", "BARBOACH"],
                ["BARBOACH", "BARBOACH", "BARBOACH", "BARBOACH", "BARBOACH"])),
    night=dict(
    land=land(23, 27, ["GOLBAT", "SANDILE", "GOLBAT", "FOONGUS", "CROAGUNK", "SWINUB",
                       "SANDILE", "FOONGUS", "CROAGUNK", "SWINUB", "BRELOOM", "BRELOOM"])))

# ===== Camp Cocodrie (gym 5; after Route 9 23-27, before Route 10 25-29): no wild grass, dock fishing
add("MAP_CAMP_COCODRIE", "gCampCocodrie_Orleans", day=dict(
    water=water(24, 28, ["BARBOACH", "QUAGSIRE", "WOOPER", "PSYDUCK", "QUAGSIRE"]),
    fish=banded(24, 28, ["BARBOACH", "WOOPER"], ["WOOPER", "BARBOACH", "BARBOACH"],
                ["QUAGSIRE", "WHISCASH", "QUAGSIRE", "WHISCASH", "WHISCASH"])))

# ===== Route 10 (after gym 5) - wild 25-29
add(R(10), "gRoute10_Orleans", day=dict(
    land=land(25, 29, ["DUCKLETT", "PSYDUCK", "PELIPPER", "MASQUERAIN", "POLIWHIRL", "DUCKLETT",
                       "PSYDUCK", "PELIPPER", "MASQUERAIN", "POLIWHIRL", "BUDEW", "BUDEW"]),
    water=water(25, 29, ["PSYDUCK", "POLIWHIRL", "DUCKLETT", "MASQUERAIN", "PELIPPER"]),
    fish=banded(25, 29, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["POLIWHIRL", "BARBOACH", "POLIWHIRL", "BARBOACH", "POLIWHIRL"])),
    night=dict(
    land=land(25, 29, ["GOLBAT", "NOCTOWL", "GOLBAT", "PSYDUCK", "MASQUERAIN", "POLIWHIRL",
                       "NOCTOWL", "PSYDUCK", "MASQUERAIN", "POLIWHIRL", "BUIZEL", "BUIZEL"]),
    water=water(25, 29, ["PSYDUCK", "POLIWHIRL", "MASQUERAIN", "PSYDUCK", "BUIZEL"])))

# ===== Route 11 - wild 28-32 (water only)
add(R(11), "gRoute11_Orleans", day=dict(
    water=water(28, 32, ["TENTACOOL", "FRILLISH", "QUAGSIRE", "MASQUERAIN", "DREDNAW"]),
    fish=banded(28, 32, ["MAGIKARP", "BARBOACH"], ["BARBOACH", "BARBOACH", "CRABRAWLER"],
                ["CRABRAWLER", "INKAY", "BARBOACH", "CRABRAWLER", "INKAY"])),
    night=dict(
    water=water(28, 32, ["FRILLISH", "QUAGSIRE", "INKAY", "NOCTOWL", "GYARADOS"])))

# ===== Route 12 - wild 31-35
add(R(12), "gRoute12_Orleans", day=dict(
    land=land(31, 35, ["NUZLEAF", "TOUCANNON", "SHIINOTIC", "RIBOMBEE", "PARASECT", "LEDIAN",
                       "NINCADA", "NUZLEAF", "TOUCANNON", "RIBOMBEE", "BAYLEEF", "BAYLEEF"]),
    water=water(31, 35, ["POLIWHIRL", "MASQUERAIN", "GOLDUCK", "QUAGSIRE", "GYARADOS"]),
    fish=banded(31, 35, ["MAGIKARP", "MAGIKARP"], ["MAGIKARP", "MAGIKARP", "MAGIKARP"],
                ["MAGIKARP", "MAGIKARP", "MAGIKARP", "GYARADOS", "GYARADOS"])),
    night=dict(
    land=land(31, 35, ["GOLBAT", "NOCTOWL", "GOLBAT", "SHIINOTIC", "NUZLEAF", "VOLBEAT",
                       "NINCADA", "NOCTOWL", "SHIINOTIC", "VOLBEAT", "ILLUMISE", "ILLUMISE"])))

# ===== Route 13 - wild 33-37
add(R(13), "gRoute13_Orleans", day=dict(
    land=land(33, 37, ["FLABEBE", "SHIINOTIC", "RIBOMBEE", "MORGREM", "NUZLEAF", "LEDIAN",
                       "FLABEBE", "SHIINOTIC", "MORGREM", "RIBOMBEE", "SERVINE", "SERVINE"])),
    night=dict(
    land=land(33, 37, ["GOLBAT", "SHIINOTIC", "GOLBAT", "MORGREM", "NUZLEAF", "NINCADA",
                       "SHIINOTIC", "MORGREM", "NUZLEAF", "NINCADA", "MISDREAVUS", "MISDREAVUS"])))

# ===== Lutin's Hollow (gym 6; no grass)
add("MAP_LUTINS_HOLLOW", "gLutinsHollow_Orleans", day=dict(
    water=water(33, 37, ["POLIWHIRL", "MASQUERAIN", "GOLDUCK", "QUAGSIRE", "GYARADOS"]),
    fish=banded(33, 37, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["POLIWHIRL", "BARBOACH", "POLIWHIRL", "BARBOACH", "GYARADOS"])))

# ===== Route 14 (after gym 6) - wild 37-41
add(R(14), "gRoute14_Orleans", day=dict(
    land=land(37, 41, ["DODRIO", "RATICATE", "STARAPTOR", "ARBOK", "DODRIO", "RATICATE",
                       "STARAPTOR", "ARBOK", "DODRIO", "STARAPTOR", "STANTLER", "STANTLER"]),
    water=water(37, 41, ["POLIWHIRL", "GOLDUCK", "WHISCASH", "QUAGSIRE", "QUAGSIRE"]),
    fish=banded(37, 41, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "BARBOACH"],
                ["WHISCASH", "POLIWHIRL", "WHISCASH", "POLIWHIRL", "GYARADOS"])),
    night=dict(
    land=land(37, 41, ["GOLBAT", "ARBOK", "GOLBAT", "WEEZING", "NOCTOWL", "ARBOK",
                       "WEEZING", "NOCTOWL", "CROBAT", "CROBAT", "SANDSLASH", "SANDSLASH"])))

# ===== Route 15 - wild 39-43
add(R(15), "gRoute15_Orleans", day=dict(
    land=land(39, 43, ["CAPSAKID", "SUNKERN", "LEDIAN", "DODRIO", "OINKOLOGNE", "CAPSAKID",
                       "SUNKERN", "LEDIAN", "DODRIO", "OINKOLOGNE", "EXEGGCUTE", "EXEGGCUTE"])),
    night=dict(
    land=land(39, 43, ["GOLBAT", "CAPSAKID", "GOLBAT", "ILLUMISE", "NOCTOWL", "CAPSAKID",
                       "ILLUMISE", "NOCTOWL", "CROBAT", "CROBAT", "VOLBEAT", "VOLBEAT"])))

# ===== Route 16 - wild 41-45
add(R(16), "gRoute16_Orleans", day=dict(
    land=land(41, 45, ["CAPSAKID", "VULPIX", "SUNKERN", "EXEGGCUTE", "DODRIO", "OINKOLOGNE",
                       "CAPSAKID", "VULPIX", "EXEGGCUTE", "OINKOLOGNE", "CHARMELEON", "CHARMELEON"])),
    night=dict(
    land=land(41, 45, ["GOLBAT", "VULPIX", "GOLBAT", "CAPSAKID", "ARBOK", "NOCTOWL",
                       "VULPIX", "CAPSAKID", "CROBAT", "CROBAT", "CROCALOR", "CROCALOR"])))

# ===== Route 17 - wild 43-47
add(R(17), "gRoute17_Orleans", day=dict(
    land=land(43, 47, ["MAGNETON", "SANDSLASH", "ARBOK", "RATICATE", "FERROTHORN", "MAGNETON",
                       "SANDSLASH", "RATICATE", "FERROTHORN", "ARBOK", "COALOSSAL", "COALOSSAL"])),
    night=dict(
    land=land(43, 47, ["GOLBAT", "MAGNETON", "GOLBAT", "ARBOK", "SANDSLASH", "NOCTOWL",
                       "MAGNETON", "NOCTOWL", "CROBAT", "CROBAT", "WEEZING", "WEEZING"])))

# ===== Redfield (gym 7; reached after Route 17 43-47, before Route 18 45-49). Mockup lists no pools;
#        split by the neighbouring Routes 15/16 day/night lists (sugarcane country).
add("MAP_REDFIELD", "gRedfield_Orleans", day=dict(
    land=land(44, 48, ["CAPSAKID", "SUNKERN", "DODRIO", "OINKOLOGNE", "CAPSAKID", "SUNKERN",
                       "DODRIO", "OINKOLOGNE", "EXEGGCUTE", "EXEGGCUTE", "VULPIX", "VULPIX"]),
    water=water(44, 48, ["POLIWHIRL", "GOLDUCK", "WHISCASH", "FLOATZEL", "SEISMITOAD"]),
    fish=banded(44, 48, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["WHISCASH", "POLIWHIRL", "WHISCASH", "POLIWHIRL", "GYARADOS"])),
    night=dict(
    land=land(44, 48, ["GOLBAT", "CAPSAKID", "GOLBAT", "NOCTOWL", "ARBOK", "VULPIX",
                       "CAPSAKID", "NOCTOWL", "CROBAT", "CROBAT", "VOLBEAT", "VOLBEAT"])))

# ===== Route 18 (after gym 7) - wild 45-49 (water)
add(R(18), "gRoute18_Orleans", day=dict(
    water=water(45, 49, ["TENTACRUEL", "PELIPPER", "FLOATZEL", "POLIWHIRL", "SEISMITOAD"]),
    fish=banded(45, 49, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["WHISCASH", "FLOATZEL", "WHISCASH", "FLOATZEL", "WHISCASH"])),
    night=dict(
    water=water(45, 49, ["TENTACRUEL", "FLOATZEL", "POLIWHIRL", "WHISCASH", "SHARPEDO"])))

# ===== Route 19 - wild 47-51
add(R(19), "gRoute19_Orleans", day=dict(
    land=land(47, 51, ["CRAWDAUNT", "SWANNA", "GOLDUCK", "ARAQUANID", "MASQUERAIN", "SKRELP",
                       "CRAWDAUNT", "SWANNA", "ARAQUANID", "SKRELP", "SHELLDER", "SHELLDER"]),
    water=water(47, 51, ["GOLDUCK", "CRAWDAUNT", "SWANNA", "SKRELP", "SHELLDER"]),
    fish=banded(47, 51, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["WHISCASH", "WHISCASH", "WHISCASH", "WHISCASH", "WHISCASH"])),
    night=dict(
    land=land(47, 51, ["CRAWDAUNT", "GOLDUCK", "ARAQUANID", "MASQUERAIN", "SKRELP", "CRAWDAUNT",
                       "GOLDUCK", "MASQUERAIN", "ARAQUANID", "SKRELP", "HAUNTER", "HAUNTER"]),
    water=water(47, 51, ["GOLDUCK", "CRAWDAUNT", "ARAQUANID", "SKRELP", "SKRELP"])))

# ===== Route 20 - wild 49-53 (water only)
add(R(20), "gRoute20_Orleans", day=dict(
    water=water(49, 53, ["PELIPPER", "BARBARACLE", "POLIWHIRL", "SEISMITOAD", "FLAMIGO"]),
    fish=banded(49, 53, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["WHISCASH", "SEISMITOAD", "WHISCASH", "SEISMITOAD", "SEISMITOAD"])),
    night=dict(
    water=water(49, 53, ["POLIWHIRL", "BARBARACLE", "SEISMITOAD", "SEISMITOAD", "JELLICENT"])))

# ===== Land's End (gym 8; boardwalk fishing)
add("MAP_LANDS_END", "gLandsEnd_Orleans", day=dict(
    water=water(49, 53, ["TENTACRUEL", "PELIPPER", "POLIWHIRL", "BARBARACLE", "SEISMITOAD"]),
    fish=banded(49, 53, ["MAGIKARP", "POLIWAG"], ["POLIWHIRL", "BARBOACH", "POLIWHIRL"],
                ["WHISCASH", "SEISMITOAD", "WHISCASH", "SEISMITOAD", "SEISMITOAD"])))

# ===== Route 21 (after gym 8) - wild 51-55 (water). 6 day species for 5 water slots: Gyarados is
#        carried by the Super Rod (uncommon) per the fishing note.
add(R(21), "gRoute21_Orleans", day=dict(
    water=water(51, 55, ["TENTACRUEL", "PELIPPER", "JELLICENT", "DRAGALGE", "WAILORD"]),
    fish=banded(51, 55, ["MAGIKARP", "MAGIKARP"], ["CRABRAWLER", "CRABRAWLER", "CRABRAWLER"],
                ["MALAMAR", "MALAMAR", "GYARADOS", "MALAMAR", "GYARADOS"])),
    night=dict(
    water=water(51, 55, ["TENTACRUEL", "JELLICENT", "DRAGALGE", "TENTACRUEL", "KILOWATTREL"])))

# ===== Route 22 - wild 53-57
add(R(22), "gRoute22_Orleans", day=dict(
    land=land(53, 57, ["BARBARACLE", "DREDNAW", "BARBARACLE", "DREDNAW", "BARBARACLE", "DREDNAW",
                       "BARBARACLE", "GIMMIGHOUL", "GIMMIGHOUL", "GIMMIGHOUL", "CURSOLA", "CURSOLA"]),
    water=water(53, 57, ["TENTACRUEL", "JELLICENT", "BARBARACLE", "GIMMIGHOUL", "CURSOLA"]),
    fish=banded(53, 57, ["MAGIKARP", "MAGIKARP"], ["CRABRAWLER", "CRABRAWLER", "CRABRAWLER"],
                ["MALAMAR", "CRABRAWLER", "MALAMAR", "CRABRAWLER", "CRABRAWLER"])),
    night=dict(
    land=land(53, 57, ["MISDREAVUS", "MISDREAVUS", "MISDREAVUS", "MISDREAVUS", "MISDREAVUS", "MISDREAVUS",
                       "MISDREAVUS", "GIMMIGHOUL", "GIMMIGHOUL", "GIMMIGHOUL", "DHELMISE", "DHELMISE"]),
    water=water(53, 57, ["TENTACRUEL", "JELLICENT", "MISDREAVUS", "GIMMIGHOUL", "DHELMISE"])))

# ===== Route 23 - wild 55-59
add(R(23), "gRoute23_Orleans", day=dict(
    land=land(55, 59, ["KROOKODILE", "URSARING", "STANTLER", "BOLDORE", "NUZLEAF", "STARAPTOR",
                       "KROOKODILE", "URSARING", "STANTLER", "STARAPTOR", "FLYGON", "FLYGON"])),
    night=dict(
    land=land(55, 59, ["GOLBAT", "CROBAT", "KROOKODILE", "URSARING", "BOLDORE", "NOCTOWL",
                       "KROOKODILE", "URSARING", "BOLDORE", "NOCTOWL", "NOCTOWL", "NOCTOWL"])))

# ===== Route 24 - wild 57-61
add(R(24), "gRoute24_Orleans", day=dict(
    land=land(57, 61, ["BOLDORE", "SANDSLASH", "COALOSSAL", "MAGNETON", "FLYGON", "BOLDORE",
                       "SANDSLASH", "COALOSSAL", "MAGNETON", "FLYGON", "EXCADRILL", "EXCADRILL"])),
    night=dict(
    land=land(57, 61, ["GOLBAT", "CROBAT", "BOLDORE", "COALOSSAL", "SANDSLASH", "MAGNETON",
                       "NOIVERN", "BOLDORE", "SANDSLASH", "NOIVERN", "GIGALITH", "GIGALITH"])))

# ===== Route 25 (after both raids) - wild 59-63
add(R(25), "gRoute25_Orleans", day=dict(
    land=land(59, 63, ["AMOONGUSS", "QUAGSIRE", "AMOONGUSS", "SEISMITOAD", "WHISCASH", "QUAGSIRE",
                       "AMOONGUSS", "SEISMITOAD", "QUAGSIRE", "WHISCASH", "AMOONGUSS", "SEISMITOAD"]),
    water=water(59, 63, ["QUAGSIRE", "WHISCASH", "JELLICENT", "SEISMITOAD", "DRAGONAIR"]),
    fish=banded(59, 63, ["MAGIKARP", "MAGIKARP"], ["WHISCASH", "QUAGSIRE", "WHISCASH"],
                ["WHISCASH", "WHISCASH", "WHISCASH", "DRAGONAIR", "DRAGONAIR"])),
    night=dict(
    land=land(59, 63, ["MISDREAVUS", "QUAGSIRE", "SLIGGOO", "MISDREAVUS", "QUAGSIRE", "SLIGGOO",
                       "MISDREAVUS", "QUAGSIRE", "SLIGGOO", "MISDREAVUS", "DRAKLOAK", "DRAKLOAK"]),
    water=water(59, 63, ["QUAGSIRE", "JELLICENT", "SLIGGOO", "MISDREAVUS", "DRAKLOAK"])))

# ===== Oldest Shrine (reached by Route 25; mockup lists no pools -> mirrors Route 25's water/fishing)
add("MAP_OLDEST_SHRINE", "gOldestShrine_Orleans", day=dict(
    water=water(59, 63, ["QUAGSIRE", "WHISCASH", "JELLICENT", "SEISMITOAD", "DRAGONAIR"]),
    fish=banded(59, 63, ["MAGIKARP", "MAGIKARP"], ["WHISCASH", "QUAGSIRE", "WHISCASH"],
                ["WHISCASH", "WHISCASH", "WHISCASH", "DRAGONAIR", "DRAGONAIR"])),
    night=dict(
    water=water(59, 63, ["QUAGSIRE", "JELLICENT", "SLIGGOO", "MISDREAVUS", "DRAKLOAK"])))


# ---------------------------------------------------------------- build
def mk(mapc, key, mons):
    out = []
    for s, lo, hi in mons:
        full = "SPECIES_" + s
        assert full in KNOWN, full
        em = evo_min(s)
        if lo < em:
            nlo, nhi = em, max(hi, em)
            WARN.append(f"{mapc} {key}: {s} {lo}-{hi} raised to {nlo}-{nhi} (evolves in at {em})")
            lo, hi = nlo, nhi
        assert 1 <= lo <= hi <= 100, (mapc, s, lo, hi)
        out.append({"min_level": lo, "max_level": hi, "species": full})
    return out


def entry(mapc, label, land_rate, tabs):
    e = {"map": mapc, "base_label": label}
    for key, src, n, rate in (("land_mons", "land", 12, land_rate), ("water_mons", "water", 5, 4),
                              ("fishing_mons", "fish", 10, 30)):
        if src in tabs:
            assert len(tabs[src]) == n, (mapc, key)
            e[key] = {"encounter_rate": rate, "mons": mk(mapc, key + ("" if not label.endswith("_Night") else "/night"), tabs[src])}
    return e


new = []
for mapc, label, lr, day, night in T:
    assert set(day) <= {"land", "water", "fish"} and set(night) <= {"land", "water"}
    new.append(entry(mapc, label, lr, day))
    if night:
        new.append(entry(mapc, label + "_Night", lr, night))

raw = open(PATH, "rb").read()
data = json.loads(raw.decode("utf-8"))
assert (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8") == raw, "format round-trip mismatch"
grp = data["wild_encounter_groups"][0]
enc = grp["encounters"]
pat = re.compile(r"^g\w+_Orleans(_Night)?$")
idx = [i for i, e in enumerate(enc) if pat.match(e["base_label"])]
assert idx == list(range(idx[0], idx[-1] + 1)), "Orleans block not contiguous"
old_maps = {enc[i]["map"] for i in idx}
new_maps = {e["map"] for e in new}
print("maps dropped:", sorted(old_maps - new_maps), " maps added:", sorted(new_maps - old_maps))
map_ids = set()
for d in os.listdir(os.path.join(ROOT, "data/maps")):
    p = os.path.join(ROOT, "data/maps", d, "map.json")
    if os.path.exists(p):
        map_ids.add(json.load(open(p, encoding="utf-8"))["id"])
for e in new:
    assert e["map"] in map_ids, e["map"]
labels = [e["base_label"] for e in new]
assert len(set(labels)) == len(labels)
others = {e["base_label"] for g in data["wild_encounter_groups"] for j, e in enumerate(g["encounters"])
          if not (g is grp and j in idx)}
assert not (set(labels) & others)
# no other (non-Orleans) table on these maps
assert not ({e["map"] for j, e in enumerate(enc) if j not in idx} & new_maps)
grp["encounters"] = enc[:idx[0]] + new + enc[idx[-1] + 1:]
out = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
json.loads(out.decode("utf-8"))
print(f"{len(idx)} old Orleans entries -> {len(new)} new; {len(raw)} -> {len(out)} bytes")
for w in WARN:
    print("WARN", w)
if "--out" in sys.argv:
    open(sys.argv[sys.argv.index("--out") + 1], "wb").write(out)
if WRITE:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PATH), prefix=".wild_encounters.", suffix=".tmp")
    with os.fdopen(fd, "wb") as fh:
        fh.write(out)
    os.replace(tmp, PATH)
    print("written")
if "--show" in sys.argv:
    for e in new:
        parts = []
        for k in ("land_mons", "water_mons", "fishing_mons"):
            if k in e:
                ms = e[k]["mons"]
                parts.append(k.split("_")[0] + ": " + ", ".join(f"{x['species'][8:].title()} {x['min_level']}-{x['max_level']}" for x in ms))
        print(e["base_label"], "|", " || ".join(parts))

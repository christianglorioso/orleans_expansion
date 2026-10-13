"""Wild held items: every competitively useful held item must be farmable (5% itemRare slot, or an existing wild source) from a species that is
really encountered in the wild in Orleans. Writes ../frontier/wild_held_items.md (item -> species -> where) and exits 1 if an item has no source.

usage (from the decomp root): python tools/dex/wild_held_items.py [--no-report]
SetWildMonHeldItem (src/pokemon.c): 45% nothing, 50% itemCommon, 5% itemRare (if both are equal the mon always holds it). Orleans keeps the common slot
for its vanilla loot and uses itemRare for the competitive item. Leftover Hoenn maps (Safari Zone, Artisan Cave, Route 111) do not count as sources.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
EXCLUDE = ("SafariZone", "ArtisanCave", "Route111")
ITEMS = [
    "ABILITY_SHIELD", "FAIRY_FEATHER", "LEPPA_BERRY", "LIECHI_BERRY", "PETAYA_BERRY", "SALAC_BERRY", "ABSORB_BULB", "ADRENALINE_ORB", "AIR_BALLOON", "ASSAULT_VEST", "BABIRI_BERRY", "BIG_ROOT", "BINDING_BAND", "BLACK_BELT",
    "BLACK_GLASSES", "BLACK_SLUDGE", "BRIGHT_POWDER", "CELL_BATTERY", "CHARCOAL", "CHARTI_BERRY", "CHILAN_BERRY", "CHOICE_BAND", "CHOICE_SCARF",
    "CHOICE_SPECS", "CHOPLE_BERRY", "CLEAR_AMULET", "COBA_BERRY", "COLBUR_BERRY", "COVERT_CLOAK", "DAMP_ROCK", "DEEP_SEA_TOOTH", "DRACO_PLATE",
    "DRAGON_FANG", "DREAD_PLATE", "EARTH_PLATE", "EJECT_BUTTON", "EJECT_PACK", "EVIOLITE", "EXPERT_BELT", "FIST_PLATE", "FLAME_ORB", "FLAME_PLATE",
    "FLOAT_STONE", "FOCUS_BAND", "FOCUS_SASH", "GRIP_CLAW", "HABAN_BERRY", "HARD_STONE", "HEAT_ROCK", "HEAVY_DUTY_BOOTS", "ICICLE_PLATE", "ICY_ROCK",
    "INSECT_PLATE", "IRON_PLATE", "KASIB_BERRY", "KEBIA_BERRY", "KINGS_ROCK", "LEFTOVERS", "LIFE_ORB", "LIGHT_BALL", "LIGHT_CLAY", "LOADED_DICE",
    "LUMINOUS_MOSS", "LUM_BERRY", "MAGNET", "MEADOW_PLATE", "MENTAL_HERB", "METAL_COAT", "METAL_POWDER", "MIND_PLATE", "MIRACLE_SEED", "MIRROR_HERB",
    "MUSCLE_BAND", "MYSTIC_WATER", "NEVER_MELT_ICE", "OCCA_BERRY", "PASSHO_BERRY", "PAYAPA_BERRY", "PIXIE_PLATE", "POISON_BARB", "POWER_HERB",
    "PROTECTIVE_PADS", "QUICK_CLAW", "QUICK_POWDER", "RAZOR_CLAW", "RAZOR_FANG", "RED_CARD", "RINDO_BERRY", "ROCKY_HELMET", "ROOM_SERVICE",
    "ROSELI_BERRY", "SAFETY_GOGGLES", "SCOPE_LENS", "SHARP_BEAK", "SHED_SHELL", "SHELL_BELL", "SHUCA_BERRY", "SILK_SCARF", "SILVER_POWDER",
    "SITRUS_BERRY", "SKY_PLATE", "SMOOTH_ROCK", "SNOWBALL", "SOFT_SAND", "SPELL_TAG", "SPLASH_PLATE", "SPOOKY_PLATE", "STARF_BERRY", "STICKY_BARB",
    "STONE_PLATE", "TANGA_BERRY", "TERRAIN_EXTENDER", "THROAT_SPRAY", "TOXIC_ORB", "TOXIC_PLATE", "TWISTED_SPOON", "UTILITY_UMBRELLA", "WACAN_BERRY",
    "WEAKNESS_POLICY", "WHITE_HERB", "WIDE_LENS", "WISE_GLASSES", "YACHE_BERRY", "ZAP_PLATE"
]


def wild_species():
    d = json.load(open("src/data/wild_encounters.json"))["wild_encounter_groups"][0]
    lay = {l["id"]: l for l in json.load(open("data/layouts/layouts.json"))["layouts"]}
    idmap = {}
    for dn in os.listdir("data/maps"):
        p = f"data/maps/{dn}/map.json"
        if os.path.exists(p):
            m = json.load(open(p))
            idmap[m["id"]] = (dn, lay.get(m["layout"]))
    out = defaultdict(set)
    for e in d["encounters"]:
        dn, l = idmap.get(e["map"], (None, None))
        if not l or l["width"] * l["height"] <= 4 or dn.startswith(EXCLUDE):
            continue
        for k, v in e.items():
            if isinstance(v, dict) and "mons" in v:
                for m in v["mons"]:
                    out[m["species"]].add(dn)
    return out


def species_items():
    sp = {}
    for f in sorted(glob.glob("src/data/pokemon/species_info/*.h")):
        cur = None
        for l in open(f, encoding="utf8"):
            m = re.match(r"\s*\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{?\s*$", l)
            if m:
                cur = m.group(1)
                sp[cur] = {"ic": None, "ir": None}
                continue
            if cur:
                for key, pat in (("ic", r"\.itemCommon\s*=\s*(\w+)"), ("ir", r"\.itemRare\s*=\s*(\w+)")):
                    mm = re.search(pat, l)
                    if mm:
                        sp[cur][key] = mm.group(1)
    return sp


def sources():
    wild, sp = wild_species(), species_items()
    src = defaultdict(list)   # item -> [(species, slot, maps)]
    for s, maps in wild.items():
        d = sp.get(s)
        if not d:
            continue
        for slot, key in (("5%", "ir"), ("50%", "ic")):
            it = d[key]
            if it and it[5:] in ITEMS:
                src[it[5:]].append((s[8:], "100%" if d["ic"] == d["ir"] else slot, sorted(maps)))
    return src


def main():
    src = sources()
    missing = [i for i in ITEMS if i not in src]
    for i in missing:
        print("MISSING wild source:", i)
    print(f"{len(ITEMS) - len(missing)}/{len(ITEMS)} items have a wild source")
    if "--no-report" not in sys.argv:
        out = os.path.join(os.path.dirname(ROOT), "frontier", "wild_held_items.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf8") as f:
            f.write("# Wild held items (generated by tools/dex/wild_held_items.py; do not edit)\n\n")
            f.write("Held items with a competitive use, farmable from wild Pokemon: 5% chance (the species' itemRare slot; 45% hold nothing, 50% their common item).\n")
            f.write("Species are the ones that appear in the wild in Orleans (wild_encounters.json, leftover Hoenn maps excluded).\n\n")
            f.write("| Item | Species (slot) | Found in |\n|---|---|---|\n")
            for i in ITEMS:
                for s, slot, maps in src.get(i, [("MISSING", "", [])]):
                    more = " +%d more" % (len(maps) - 6) if len(maps) > 6 else ""
                    f.write(f"| {i} | {s} ({slot}) | {', '.join(maps[:6])}{more} |\n")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

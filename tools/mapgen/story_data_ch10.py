"""Chapter 10 (the post-game) data for story_overlay.py: balls and static legendary encounters that stay hidden until the game is cleared
(story 45), plus the gifts, trades and shop changes that make every dex-required item obtainable (tools/dex/obtain_audit.py).

How the hiding works (the scripts are hand-written in story/<Map>.inc, "post-game" blocks): each object has its own FLAG_PG_*. Every map load below story 45 sets it (hidden); the
epilogue clears them all (OldestShrine.inc); picking an item up / ending an encounter sets it again for good (nothing sets it at story >= 45, except
the two conditional kinds: an arena's legendary shows only if Jayden took it, and the night-only Ursaluna only at night).
"""
from story_data_ch3 import T, FACE


def spec(x):
    return f"OBJ_EVENT_GFX_SPECIES({x})"


# key, map, species const, species gfx name, level, (x, y), note
STATICS = [
    dict(key="RAIKOU", map="Route2_RaikouClearing", sp="RAIKOU", level=60, at=(10, 10)),
    dict(key="ZAPDOS", map="StormsEdge_LighthouseGallery", sp="ZAPDOS", level=60, at=(10, 9)),
    dict(key="ENTEI", map="Route16_EnteiField", sp="ENTEI", level=60, at=(9, 10)),
    dict(key="MOLTRES", map="Route17_Sugarhouse", sp="MOLTRES", level=60, at=(3, 6)),
    dict(key="SUICUNE", map="Route11_SuicuneIsle", sp="SUICUNE", level=60, at=(10, 7)),
    dict(key="ARTICUNO", map="PointeRouge_IcePlant", sp="ARTICUNO", level=60, at=(9, 5)),
    dict(key="GALAR_ARTICUNO", map="Route10_MilneburgPavilion", sp="ARTICUNO_GALAR", gfx="ARTICUNO_GALAR", level=60, at=(10, 7)),
    dict(key="GALAR_ZAPDOS", map="Route14_BushTrack", sp="ZAPDOS_GALAR", gfx="ZAPDOS_GALAR", level=60, at=(12, 8)),
    dict(key="GALAR_MOLTRES", map="Route14_SpanishFort", sp="MOLTRES_GALAR", gfx="MOLTRES_GALAR", level=60, at=(10, 6)),
    dict(key="TORNADUS", map="Route3_WindsEye", sp="TORNADUS", level=62, at=(10, 7)),
    dict(key="THUNDURUS", map="Route12_LeveeCrown", sp="THUNDURUS", level=62, at=(10, 6)),
    dict(key="LANDORUS", map="Route23_BountifulField", sp="LANDORUS", level=62, at=(10, 6)),
    dict(key="AZELF", map="Route23_UnfailingSpring", sp="AZELF", level=55, at=(10, 9)),
    dict(key="MESPRIT", map="Route1_HeartPool", sp="MESPRIT", level=55, at=(10, 7)),
    dict(key="UXIE", map="OldWater_KnowingPool", sp="UXIE", level=55, at=(10, 5)),
    dict(key="ZARUDE", map="Route13_DeepWood", sp="ZARUDE", level=55, at=(10, 7)),
    dict(key="OGERPON", map="Route13_CourirGlade", sp="OGERPON_TEAL", gfx="OGERPON", level=50, at=(10, 9)),
    dict(key="CELEBI", map="Route7_CelebiGlade", sp="CELEBI", level=50, at=(10, 10)),
    dict(key="URSALUNA_BM", map="Route23_BloodmoonArroyo", sp="URSALUNA_BLOODMOON", gfx="URSALUNA_BLOODMOON", level=60, at=(10, 8), night=True, done="FLAG_PG_URSALUNA_DONE"),
    # the raid arenas: the legendary Jayden took is back (only that one): Kyogre if the player took Groudon (pick 2), Groudon if the player took Kyogre
    dict(key="KYOGRE_RE", map="LandsEnd_DrownedTemple", sp="KYOGRE", gfx="KYOGRE_FRONT", level=70, at=(9, 5), pick=2, raw_gfx=True),
    dict(key="GROUDON_RE", map="LandsEnd_SaltCathedral", sp="GROUDON", gfx="GROUDON_FRONT", level=70, at=(11, 4), pick=1, raw_gfx=True),
    # Rayquaza returns to the stone, catchable (Mega Rayquaza needs only Dragon Ascent)
    dict(key="RAYQUAZA", map="OldestShrine", sp="RAYQUAZA", level=70, at=(16, 9)),
]

# the items that had no source (tools/dex/obtain_audit.py): balls hidden until the game is cleared
ITEMS = [
    dict(key="CHANDELURITE", map="Redfield", item="ITEM_CHANDELURITE", at=(26, 12)),
    dict(key="SCOVILLAINITE", map="Redfield", item="ITEM_SCOVILLAINITE", at=(34, 32)),
    dict(key="HEARTHFLAME_MASK", map="Redfield", item="ITEM_HEARTHFLAME_MASK", at=(42, 7)),
    dict(key="DRAGONINITE", map="OldestShrine", item="ITEM_DRAGONINITE", at=(17, 24)),
    dict(key="CRABOMINITE", map="PointeRouge", item="ITEM_CRABOMINITE", at=(31, 29)),
    dict(key="WEEZINGITE", map="CrescentCity_BlacksnakeBase", item="ITEM_WEEZINGITE", at=(20, 5)),
    dict(key="WELLSPRING_MASK", map="Route19", item="ITEM_WELLSPRING_MASK", at=(36, 3)),
    dict(key="CORNERSTONE_MASK", map="Route24", item="ITEM_CORNERSTONE_MASK", at=(31, 8)),
]

# the legendary lairs (lairs.py builds these maps; story_data_lairs.py): their statics are placed there, not by a route spec's overlay. Articuno's lair is the
# existing ice plant room (INTERIOR_KEYS)
LAIR_MAPS = {"Route2_RaikouClearing", "Route16_EnteiField", "Route11_SuicuneIsle", "Route7_CelebiGlade", "Route23_BloodmoonArroyo",
             # batch 2 (story_data_lairs.LAIRS2); the gallery and the sugarhouse are lair-built rooms too
             "OldWater_KnowingPool", "Route1_HeartPool", "Route23_UnfailingSpring", "StormsEdge_LighthouseGallery", "Route12_LeveeCrown", "Route13_DeepWood",
             "Route13_CourirGlade", "Route3_WindsEye", "Route14_SpanishFort", "Route14_BushTrack", "Route10_MilneburgPavilion", "Route17_Sugarhouse",
             "Route23_BountifulField"}

# interior rooms: (mockup key, kind) so the generated people get a script label (read back from the built map.json by position)
INTERIOR_KEYS = {"PointeRouge_IcePlant": "pointe_rouge_ice_plant", "CrescentCity_BlacksnakeBase": "crescent_city_blacksnake_base",
                 "LandsEnd_DrownedTemple": "lands_end_drowned_temple", "LandsEnd_SaltCathedral": "lands_end_salt_cathedral"}


def all_objects():
    """(map, key, kind, flag, gfx, (x, y), extra) for every post-game object"""
    out = []
    for s in STATICS:
        gfx = s.get("gfx") or s["sp"]
        out.append((s["map"], s["key"], "static", "FLAG_PG_" + s["key"], gfx, s["at"], s))
    for i in ITEMS:
        out.append((i["map"], i["key"], "item", "FLAG_PG_" + i["key"], "OBJ_EVENT_GFX_ITEM_BALL", i["at"], i))
    return out


def gfx_const(kind, gfx):
    if kind == "item":
        return gfx
    return f"OBJ_EVENT_GFX_{gfx}" if gfx in ("KYOGRE_FRONT", "GROUDON_FRONT") else spec(gfx)


def map_snake(name):
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name.replace("_", "")).upper() if "_" not in name else "_".join(map_snake(p) for p in name.split("_"))


def overlay_for(map_name):
    """add_objects for an outdoor map"""
    objs = []
    for (m, key, kind, flag, gfx, (x, y), s) in all_objects():
        if m != map_name:
            continue
        objs.append({"id": f"LOCALID_{map_snake(m)}_PG_{key}", "gfx": gfx_const(kind, gfx), "x": x, "y": y, "move": FACE + "DOWN", "text": "",
                     "custom": True, "flag": flag})
    return objs


def interior_extras(map_name):
    """extra people for an interior room: (kind, text, opts, (x, y))"""
    out = []
    for (m, key, kind, flag, gfx, (x, y), s) in all_objects():
        if m == map_name:
            out.append(("pg" + key.lower(), "", {"custom": True, "gfx": gfx_const(kind, gfx), "face": "DOWN", "flag": flag}, (x, y)))
    return out


# ---------------------------------------------------------------------------------------------- rooms with scripted people (merged into INTERIOR)
ROOMS = {
    # the trade house (Alolan forms): Trader0 Sandshrine, Trader1 Vulpix, the collector Raichu
    "crescent_city_trades": {"opts": {0: {"custom": True}, 1: {"custom": True}, 2: {"custom": True}}},
    # the herbalist's apprentice: the Floette (Eternal Flower) seed after the game is cleared
    "lutins_hollow_herbalist": {"opts": {1: {"custom": True}}},
}

# the Battle Frontier: the plaza opens when the guard steps aside (story 45). The seven halls' doors are real warps into the vanilla lobbies (crescent.py
# FAC_LOBBY) and every lobby exit is a warp retargeted to the door in front of it (frontier_wire.py), so nothing here is a script
FRONTIER = {}

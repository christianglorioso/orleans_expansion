"""Chapter 7 data for story_overlay.py: Routes 14-17, Redfield (outdoors, the mill yard trial, the rooms), the Old Water raid actors.
Trainers are a table (TRAINERS + EXTRA_PARTIES) for gen_route_trainers.py (python tools/mapgen/gen_route_trainers.py ch7).

Story: 31 reached Redfield (arrival frame script, from 29 or 30), 32 Rita's Mega Chandelure beaten at the yard gate, 33 Cayenne beaten
(badge 7), 34 Isaac's raid at the Old Water defended (partner battle with Wren).
"""
from story_data_ch3 import T, FACE

# a mon is (species, level[, moves[, extras]]); extras: {"item": "...", "ability": "..."}
TRAINERS = [
    # ---- Route 14 (the levee road south of Crescent, 41-43)
    dict(m="Route14", n=0, const="TRAINER_ORLEANS_ROUTE14_FISHERMAN", name="ONESIME", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="LEFT", sight=4, team=[("Whiscash", 41), ("Quagsire", 41), ("Gyarados", 42)],
         intro=T("The levee road is dry again. My", "lines are not. Battle me!"), defeat=T("Snapped line."),
         after=T("The water went down all at once.", "I almost lost my boat.")),
    dict(m="Route14", n=3, const="TRAINER_ORLEANS_ROUTE14_BIRD_KEEPER", name="DENIS", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="DOWN", sight=4, team=[("Corviknight", 42), ("Staraptor", 42), ("Noctowl", 42)],
         intro=T("My birds watched the flood go", "down. They want a rematch!"), defeat=T("Grounded."),
         after=T("Noctowl sees the rougarou at", "night. Won't tell me where.")),
    dict(m="Route14", n=5, const="TRAINER_ORLEANS_ROUTE14_CAMPER", name="VALERE", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="RIGHT", sight=4, team=[("Ursaring", 42), ("Toxicroak", 42), ("Excadrill", 43)],
         intro=T("I camp on the crest. Something", "howls there after dark."), defeat=T("Howled out."),
         after=T("Don't camp up there. Take it", "from me.")),
    dict(m="Route14", n=7, const="TRAINER_ORLEANS_ROUTE14_PICNICKER", name="COLETTE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="LEFT", sight=4, team=[("Floette", 42), ("Lilligant", 42), ("Sunflora", 43)],
         intro=T("Sunflowers grow wild by the", "levee. I guard them!"), defeat=T("Wilted."),
         after=T("They all face the mill. Don't", "ask me why.")),
    dict(m="Route14", n=8, const="TRAINER_ORLEANS_ROUTE14_BUG_MANIAC", name="ALBAN", cls="Bug Maniac", pic="Bug Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BUG_CATCHER", face="UP", sight=4, team=[("Galvantula", 42), ("Ninjask", 42), ("Parasect", 43)],
         intro=T("Cane beetles, cane moths. This", "road is a bug paradise."), defeat=T("Squashed."),
         after=T("Cane smoke drives the bugs", "onto the road. Happy me!")),
    dict(m="Route14", n=10, const="TRAINER_ORLEANS_ROUTE14_BLACK_BELT", name="LEANDRE", cls="Black Belt", pic="Black Belt", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BLACK_BELT", face="RIGHT", sight=4, team=[("Poliwrath", 42), ("Crabominable", 43), ("Toxicroak", 43)],
         intro=T("I trained against the flood.", "Now I train against you!"), defeat=T("Knocked flat."),
         after=T("The sugar country starts south", "of here. Eat well.")),
    # ---- Route 15 (the cane fields, 42-44)
    dict(m="Route15", n=1, const="TRAINER_ORLEANS_ROUTE15_HIKER", name="BASILE", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="DOWN", sight=4, team=[("Coalossal", 43), ("Gigalith", 43), ("Excadrill", 44)],
         intro=T("Red earth, hot rock. I came", "south to hike it."), defeat=T("Cooled off."),
         after=T("The mill's chimney smokes day", "and night. You can see it far off.")),
    dict(m="Route15", n=2, const="TRAINER_ORLEANS_ROUTE15_LASS", name="MARGUERITE", cls="Lass", pic="Lass", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_LASS", face="LEFT", sight=4, team=[("Ribombee", 43), ("Florges", 43), ("Mimikyu", 44)],
         intro=T("Fairies like sugar. So do I.", "Care to battle?"), defeat=T("Too sweet."),
         after=T("The cane workers leave a little", "sugar out for the Ribombee.")),
    dict(m="Route15", n=3, const="TRAINER_ORLEANS_ROUTE15_GENTLEMAN", name="AURELE", cls="Gentleman", pic="Gentleman", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_GENTLEMAN", face="RIGHT", sight=4, team=[("Hypno", 43), ("Wyrdeer", 43), ("Mismagius", 44)],
         intro=T("A planter's life is quiet. A", "battle is a pleasant change."), defeat=T("Well fought."),
         after=T("I own the east field. Mind the", "rows. I count them.")),
    dict(m="Route15", n=4, const="TRAINER_ORLEANS_ROUTE15_CAMPER", name="JOCELYN", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="DOWN", sight=4, team=[("Sandslash", 43), ("Breloom", 43), ("Flygon", 44)],
         intro=T("The dry ground's a good place", "to pitch a tent. Or fight."), defeat=T("Tent's flat."),
         after=T("Dust everywhere. The north is", "worse, they say.")),
    dict(m="Route15", n=5, const="TRAINER_ORLEANS_ROUTE15_FISHERMAN", name="REMI", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="LEFT", sight=4, team=[("Seismitoad", 43), ("Politoed", 43), ("Jellicent", 44)],
         intro=T("Irrigation ditches hold fish.", "Don't tell the planters."), defeat=T("Ditched."),
         after=T("The ditches are cooler than", "the river. The fish know.")),
    # ---- Route 16 (the pepper road, 43-45)
    dict(m="Route16", n=1, const="TRAINER_ORLEANS_ROUTE16_PICNICKER", name="SIDONIE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="DOWN", sight=4, team=[("Vileplume", 44), ("Sunflora", 44), ("Florges", 44)],
         intro=T("Peppers for lunch. Battle for", "dessert!"), defeat=T("Burned my tongue."),
         after=T("Eat the red ones. The green", "ones just look innocent.")),
    dict(m="Route16", n=2, const="TRAINER_ORLEANS_ROUTE16_BLACK_BELT", name="OCTAVE", cls="Black Belt", pic="Black Belt", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BLACK_BELT", face="DOWN", sight=4, team=[("Crabominable", 44), ("Poliwrath", 44), ("Hypno", 45)],
         intro=T("I train in the heat. It hardens", "the spirit. And the skin."), defeat=T("Spirit intact."),
         after=T("Heat's no enemy. Only a", "teacher. A mean one.")),
    dict(m="Route16", n=3, const="TRAINER_ORLEANS_ROUTE16_RUIN_MANIAC", name="ULYSSE", cls="Ruin Maniac", pic="Ruin Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_MANIAC", face="DOWN", sight=4, team=[("Gigalith", 44), ("Coalossal", 44), ("Excadrill", 45)],
         intro=T("Old mill foundations under the", "peppers! Fight me for them!"), defeat=T("Dug up."),
         after=T("The first mill burned. The", "land greened over. Remember that.")),
    dict(m="Route16", n=4, const="TRAINER_ORLEANS_ROUTE16_EXPERT", name="PROSPER", cls="Expert", pic="Expert M", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_EXPERT_M", face="DOWN", sight=4, team=[("Flareon", 44), ("Vaporeon", 44), ("Jolteon", 45)],
         intro=T("Three siblings, three styles.", "I only fight with all three."), defeat=T("A family loss."),
         after=T("Eevee is the friendliest of all", "POKéMON. Ask anyone.")),
    dict(m="Route16", n=5, const="TRAINER_ORLEANS_ROUTE16_PICNICKER_2", name="CELINE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="DOWN", sight=4, team=[("Mismagius", 44), ("Roserade-Orleanian", 44), ("Lilligant-Hisui", 45)],
         intro=T("I walk the pepper rows at", "dusk. The lights are lovely."), defeat=T("Lights out."),
         after=T("Dusk is when the mill sleeps.", "Only the cane keeps growing.")),
    # ---- Route 17 (the mill road, 44-46)
    dict(m="Route17", n=3, const="TRAINER_ORLEANS_ROUTE17_KINDLER", name="ARMAND", cls="Kindler", pic="Kindler", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_MAN_3", face="LEFT", sight=4, team=[("Ninetales", 45), ("Coalossal", 45), ("Scovillain", 46)],
         intro=T("The mill's gym burns bright.", "Warm up on me first!"), defeat=T("Doused."),
         after=T("CAYENNE does not lose to the", "cold. Or to anyone, really.")),
    dict(m="Route17", n=4, const="TRAINER_ORLEANS_ROUTE17_BIRD_KEEPER", name="HIPPOLYTE", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="DOWN", sight=4, team=[("Corviknight", 45), ("Noivern", 45), ("Toucannon", 46)],
         intro=T("Thermals over the cane field!", "My birds love them."), defeat=T("Fell out of the sky."),
         after=T("Smoke rises, birds follow. It's", "an old trick.")),
    dict(m="Route17", n=5, const="TRAINER_ORLEANS_ROUTE17_COOLTRAINER", name="VIVIANE", cls="Cooltrainer", pic="Cooltrainer F", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_BEAUTY", face="DOWN", sight=4, team=[("Delphox", 45), ("Raichu", 45), ("Sylveon", 46)],
         intro=T("Six badges, and the next town", "wants a seventh. Let's see yours!"), defeat=T("You've earned them."),
         after=T("A sunny day, a sunny gym. It's", "a hard combination.")),
    dict(m="Route17", n=6, const="TRAINER_ORLEANS_ROUTE17_HIKER", name="ROMAIN", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="LEFT", sight=4, team=[("Gigalith", 45), ("Coalossal", 45), ("Mamoswine", 46)],
         intro=T("The last stretch before the", "mill. I'll make it harder!"), defeat=T("Stumbled."),
         after=T("Past the gate, the sun's the", "judge. Come at noon.")),
]

EXTRA_PARTIES = [
    # the gym's two trainers
    dict(const="TRAINER_ORLEANS_REDFIELD_GYM_KINDLER", name="ALCEE", cls="Kindler", pic="Kindler", sex="Male", music="Male",
         team=[("Flareon", 45), ("Coalossal", 45), ("Ninetales", 46)]),
    dict(const="TRAINER_ORLEANS_REDFIELD_GYM_CANE_CUTTER", name="BENOIT", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         team=[("Sunflora", 45), ("Lilligant", 45), ("Ferrothorn", 46)]),
    # Rita, at the yard gate (battle 7.3): the first Mega the player meets
    dict(const="TRAINER_ORLEANS_RITA_REDFIELD", name="RITA", cls="Aqua Admin", pic="Aqua Admin F", sex="Female", music="Aqua",
         team=[("Garbodor", 44), ("Malamar", 45), ("Gengar", 45),
               ("Chandelure-Orleanian", 46, [], {"item": "Chandelurite"})],
         ai="Check Bad Move / Try To Faint", iv=24),
    # the Old Water raid's two grunts (a partner battle with Wren)
    dict(const="TRAINER_ORLEANS_RAID_GRUNT_A", name="MARCEL", cls="Team Aqua", pic="Aqua Grunt M", sex="Male", music="Aqua",
         team=[("Crobat", 44), ("Garbodor", 44)]),
    dict(const="TRAINER_ORLEANS_RAID_GRUNT_B", name="ODETTE", cls="Team Aqua", pic="Aqua Grunt F", sex="Female", music="Aqua",
         team=[("Sharpedo", 44), ("Weezing-Orleanian", 44)]),
    # Cayenne (gym 7, Sun): Ninetales' Drought is its hidden ability; Charizard holds Charizardite Y (Mega: Drought again)
    dict(const="TRAINER_CAYENNE", name="CAYENNE", cls="Leader", pic="Leader Flannery", sex="Female", music="Female",
         team=[("Scovillain", 46, ["Flamethrower", "Seed Bomb", "Sunny Day", "Protect"]),
               ("Weezing-Orleanian", 46, ["Sludge Bomb", "Flamethrower", "Will-O-Wisp", "Protect"]),
               ("Ninetales", 47, ["Flamethrower", "Solar Beam", "Extrasensory", "Will-O-Wisp"], {"ability": "Drought"}),
               ("Lilligant-Hisui", 47, ["Leaf Blade", "Close Combat", "Solar Blade", "Protect"]),
               ("Rotom-Heat", 47, ["Overheat", "Thunderbolt", "Volt Switch", "Will-O-Wisp"]),
               ("Charizard", 48, ["Heat Wave", "Solar Beam", "Air Slash", "Roost"], {"item": "Charizardite Y"})],
         ai="Check Bad Move / Try To Faint", iv=28),
]

# Wren's partner parties (battle_partners.party, one per starter line; partners.py): the Old Water raid (PARTNER_WREN_<starter>, IV 24)
# and the Blacksnake base (PARTNER_WREN_BASE_<starter>, low level, IV 12; audit fix A2)
PARTNERS = []
for _starter, _final, _base in (("CHIKORITA", "Meganium", "Bayleef"), ("FUECOCO", "Skeledirge", "Fuecoco"), ("TOTODILE", "Feraligatr", "Croconaw")):
    PARTNERS.append((f"PARTNER_WREN_{_starter}", [("Pelipper", 44, None), ("Roselia-Orleanian", 44, None), (_final, 46, None)], 24))
    PARTNERS.append((f"PARTNER_WREN_BASE_{_starter}", [("Wingull", 21, None), ("Roselia-Orleanian", 21, None), (_base, 22, None)], 12))


# ---------------------------------------------------------------------------------------------- Routes 14-17 overlay
def _patch(m):
    out = {}
    for t in TRAINERS:
        if t["m"] == m:
            out[f"LOCALID_ORLEANS_{m.upper()}_TRAINER_{t['n']}"] = {"gfx": t["gfx"], "move": FACE + t["face"], "sight": t["sight"], "custom": True}
    return out


ROUTE14 = {
    "patch_objects": _patch("Route14"),
    "add_items": [{"x": 24, "y": 9, "item": "ITEM_TM_SEED_BOMB", "flag": "FLAG_ROUTE14_ITEM_SEED_BOMB", "_comment": "TM075 (Routes 7-12 band, left over)"}],
    # (the rougarou, a one-off night Lycanroc Midnight, lives in its lair since the legendary lairs: Route14_RougarouHollow, story_data_lairs.py)
}
ROUTE15 = {
    "patch_objects": _patch("Route15"),
    "add_items": [{"x": 14, "y": 10, "item": "ITEM_TM_HYPER_VOICE", "flag": "FLAG_ROUTE15_ITEM_HYPER_VOICE", "_comment": "TM092"}],
}
ROUTE16 = {
    "patch_objects": _patch("Route16"),
    "add_items": [{"x": 33, "y": 10, "item": "ITEM_TM_THROAT_CHOP", "flag": "FLAG_ROUTE16_ITEM_THROAT_CHOP", "_comment": "TM116"}],
}
ROUTE17 = {
    "patch_objects": _patch("Route17"),
    "add_items": [{"x": 24, "y": 20, "item": "ITEM_TM_FOUL_PLAY", "flag": "FLAG_ROUTE17_ITEM_FOUL_PLAY", "_comment": "TM119"}],
}

# ---------------------------------------------------------------------------------------------- Redfield (outdoors)
# the mill yard trial: six mirrors (A-F) in three pairs serve three sundials, lit in order (see Redfield.inc)
MIRRORS = {  # letter -> (x, y) of the top cell (the mirror is 1 x 2)
    "A": (30, 4), "B": (32, 4), "C": (32, 8), "D": (30, 10), "E": (29, 10), "F": (26, 10),
}
DIALS = {"Middle": (32, 6), "South": (32, 10)}  # the two sundials the corridor reaches (2x2); the third (north-west), at (28, 4), is only seen


def _mirror_signs():
    signs = []
    for k, (x, y) in MIRRORS.items():
        for part, dy in (("1", 0), ("2", 1)):
            signs.append({"id": f"Mirror{k}{part}", "x": x, "y": y + dy, "text": "", "custom": True})
    for k, (x, y) in DIALS.items():
        for part, (dx, dy) in (("1", (0, 0)), ("2", (0, 1))):
            signs.append({"id": f"Dial{k}{part}", "x": x + dx, "y": y + dy, "text": "", "custom": True})
    return signs


REDFIELD = {
    "patch_objects": {
        "LOCALID_REDFIELD_CAYENNE": {"custom": True, "gfx": "OBJ_EVENT_GFX_FLANNERY", "move": FACE + "DOWN"},
        "LOCALID_REDFIELD_RITA": {"custom": True, "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F", "x": 30, "y": 13, "move": FACE + "DOWN", "flag": "FLAG_HIDE_REDFIELD_RITA"},
        "LOCALID_REDFIELD_FARMHAND": {"text": T("Cane's ready to cut. Don't wander", "into the rows. You'll get lost.")},
        "LOCALID_REDFIELD_PICKER": {"text": T("Peppers by the bushel. Dry, dry", "weather: the best kind for heat.")},
        "LOCALID_REDFIELD_KEEPER": {"text": T("The great sundial's older than the", "mill. It has never been wrong.")},
        "LOCALID_REDFIELD_BOATMAN": {"custom": True},   # two states (story/Redfield.inc): before and after the span is gone
    },
    "add_objects": [
        # Wren stands outside the mill door once the badge is won (story 33), until the raid is defended
        {"id": "LOCALID_REDFIELD_WREN", "gfx": "OBJ_EVENT_GFX_GIRL_3", "x": 38, "y": 14, "move": FACE + "LEFT", "text": "", "custom": True,
         "flag": "FLAG_HIDE_REDFIELD_WREN"},
        # the mill's shutter: the gym door's only approach cell is shut until the three sundials are lit
        {"id": "LOCALID_REDFIELD_SHUTTER_1", "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "x": 37, "y": 13, "move": "MOVEMENT_TYPE_NONE",
         "text": T("The mill's shutter is down. The", "sundials light it, they say."), "flag": "FLAG_REDFIELD_MILL_OPEN"},
    ],
    # Rita holds the yard gate (the two cells inside the fence) until her battle is won (story 31 -> 32)
    "triggers": [
        {"x": 29, "y": 14, "elevation": 0, "var": "VAR_ORLEANS_STORY", "value": 31, "script": "Redfield_EventScript_RitaGate"},
        {"x": 30, "y": 14, "elevation": 0, "var": "VAR_ORLEANS_STORY", "value": 31, "script": "Redfield_EventScript_RitaGate"},
    ],
    "patch_signs": {
        "SignMill": {"text": "REDFIELD SUGAR MILL\nCayenne's mill yard.\\pMirrors work by daylight only."},
    },
    "signs": _mirror_signs(),
}

# ---------------------------------------------------------------------------------------------- the rooms
ROOMS = {
    "redfield_gym": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_FLANNERY", "face": "DOWN"},
                 1: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": "OBJ_EVENT_GFX_MAN_3"},
                 2: {"custom": True, "sight": 3, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_HIKER"},
                 3: {"custom": True}},
    },
    "redfield_ritas_office": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M"}},
    },
    "redfield_pokecenter": {"texts": {1: T("The mill's been running day and", "night. The cane waits for no one.")}},
    "redfield_bottling_works": {"texts": {0: T("Hottest batch in years. The sun", "was on our side this season.")}},
    "redfield_shotgun_house_2": {
        "texts": {0: T("Light the dials from the south-east", "to the north-west. Two mirrors each.")},
    },
}

# ---------------------------------------------------------------------------------------------- the Old Water (raid actors)
OLD_WATER = {
    "add_objects": [
        {"id": "LOCALID_OLD_WATER_RAID_ISAAC", "gfx": "OBJ_EVENT_GFX_BOY_1", "x": 24, "y": 29, "move": FACE + "DOWN", "text": "", "custom": True,
         "flag": "FLAG_HIDE_RAID_ISAAC"},
        {"id": "LOCALID_OLD_WATER_RAID_GRUNT1", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M", "x": 22, "y": 29, "move": FACE + "DOWN", "text": "",
         "custom": True, "flag": "FLAG_HIDE_RAID_GRUNT1"},
        {"id": "LOCALID_OLD_WATER_RAID_GRUNT2", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F", "x": 26, "y": 29, "move": FACE + "DOWN", "text": "",
         "custom": True, "flag": "FLAG_HIDE_RAID_GRUNT2"},
        {"id": "LOCALID_OLD_WATER_RAID_WREN", "gfx": "OBJ_EVENT_GFX_GIRL_3", "x": 21, "y": 32, "move": FACE + "UP", "text": "", "custom": True,
         "flag": "FLAG_HIDE_RAID_WREN"},
    ],
}

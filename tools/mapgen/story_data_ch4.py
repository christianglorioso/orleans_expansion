"""Chapter 4 data for story_overlay.py: Route 4, Route 5, Pointe Rouge (outdoors and rooms), merged there.

Same conventions as story_data_ch3.py (T() joins Gen-3 text lines: two to a page; story_lint.py checks the generated scripts).
"""
from story_data_ch3 import T, FACE


def trainer(gfx, move, sight=3):
    return {"gfx": gfx, "move": FACE + move, "sight": sight, "custom": True}


# ---------------------------------------------------------------------------------------------- Route 4 (the levee road)
# Landing at its south end (Chapter 3), six trainers climbing north (levels 24-27), three item balls, a hidden Dusk Stone.
ROUTE4 = {
    "patch_objects": {
        "LOCALID_ORLEANS_ROUTE4_TRAINER_8": trainer("OBJ_EVENT_GFX_HIKER", "UP", 4),           # (16, 37) Basile
        "LOCALID_ORLEANS_ROUTE4_TRAINER_6": trainer("OBJ_EVENT_GFX_PICNICKER", "DOWN", 4),     # (18, 29) Mireille
        "LOCALID_ORLEANS_ROUTE4_TRAINER_4": trainer("OBJ_EVENT_GFX_CAMPER", "LEFT", 4),        # (16, 23) Ollie
        "LOCALID_ORLEANS_ROUTE4_TRAINER_2": trainer("OBJ_EVENT_GFX_SAILOR", "DOWN", 4),        # (12, 19) Titus
        "LOCALID_ORLEANS_ROUTE4_TRAINER_1": trainer("OBJ_EVENT_GFX_FISHERMAN", "LEFT", 4),     # (18, 15) Clovis
        "LOCALID_ORLEANS_ROUTE4_TRAINER_0": trainer("OBJ_EVENT_GFX_BOY_2", "DOWN", 4),   # (16, 5)  Pepin
    },
    "patch_items": {
        "FLAG_UNUSED_0x270": {"item": "ITEM_TM_TAILWIND", "_comment": "TM108, an item ball on Routes 3-9 (tm_list.md)"},
        "FLAG_UNUSED_0x271": {"item": "ITEM_X_SPEED"},
        "FLAG_UNUSED_0x272": {"item": "ITEM_X_DEFENSE"},
    },
    "add_hidden": [
        {"x": 4, "y": 13, "item": "ITEM_DUSK_STONE", "flag": "FLAG_ROUTE4_HIDDEN_DUSK_STONE", "_note": "evolution stone (obtainability.md)"},
    ],
}

# ---------------------------------------------------------------------------------------------- Route 5 (the fishing lake)
ROUTE5 = {
    "patch_objects": {
        "LOCALID_ORLEANS_ROUTE5_TRAINER_0": trainer("OBJ_EVENT_GFX_FISHERMAN", "DOWN", 4),      # (17, 3)  Odilon
        "LOCALID_ORLEANS_ROUTE5_TRAINER_1": trainer("OBJ_EVENT_GFX_LASS", "RIGHT", 4),          # (9, 4)   Delphine
        "LOCALID_ORLEANS_ROUTE5_NPC_2": {"custom": True, "gfx": "OBJ_EVENT_GFX_FISHERMAN"},     # (36, 9)  the tournament angler
        "LOCALID_ORLEANS_ROUTE5_TRAINER_5": trainer("OBJ_EVENT_GFX_BOY_2", "RIGHT", 4),   # (5, 15)  Gaston
        "LOCALID_ORLEANS_ROUTE5_TRAINER_8": trainer("OBJ_EVENT_GFX_CAMPER", "LEFT", 4),         # (39, 21) Raoul
        "LOCALID_ORLEANS_ROUTE5_TRAINER_9": trainer("OBJ_EVENT_GFX_PICNICKER", "UP", 4),        # (25, 24) Solange
    },
    "patch_items": {
        "FLAG_UNUSED_0x27A": {"item": "ITEM_TM_AGILITY", "flag": "FLAG_ROUTE5_ITEM_AGILITY", "_comment": "TM069 on the pier"},
    },
    "add_hidden": [
        {"x": 30, "y": 23, "item": "ITEM_SUN_STONE", "flag": "FLAG_ROUTE5_HIDDEN_SUN_STONE", "_note": "evolution stone (obtainability.md)"},
    ],
}

# ---------------------------------------------------------------------------------------------- Pointe Rouge (outdoors)
POINTE_ROUGE = {
    "patch_objects": {
        # people with lines that change with the story are written by hand (story/PointeRouge.inc)
        "LOCALID_POINTE_ROUGE_KINGFISHER": {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_1"},
        "LOCALID_POINTE_ROUGE_WORKER": {"custom": True},
        "LOCALID_POINTE_ROUGE_CHEMIST": {"custom": True},
        "LOCALID_POINTE_ROUGE_SAILOR": {"custom": True},
        "LOCALID_POINTE_ROUGE_ANGLER": {"text": T("The big ones hide under the bridges.", "KINGFISHER says the river is a gift.")},
        "LOCALID_POINTE_ROUGE_CLERK": {"text": T("The legislature is in session.", "Thirty-four floors of arguing!")},
        "LOCALID_POINTE_ROUGE_KID": {"text": T("The magnolias smell like lemons!", "I counted forty-one of them.")},
        "LOCALID_POINTE_ROUGE_RETIREE": {"text": T("Fifty years I've watched barges pass", "this bench. Never the same twice.")},
        "LOCALID_POINTE_ROUGE_YARDMAN": {"text": T("Tank cars in, tank cars out.", "The yard never sleeps.")},
        "LOCALID_POINTE_ROUGE_LASS": {"text": T("Our street has the best gardens in", "the whole capital.")},
        "LOCALID_POINTE_ROUGE_TWIN": {"text": T("KINGFISHER's POKéMON fly so fast", "they ripple the river!")},
        "LOCALID_POINTE_ROUGE_POKEFAN": {"text": T("On windy days something huge circles", "the south bridge. Never lands.")},
        "LOCALID_POINTE_ROUGE_SHOPPER": {"text": T("The Mart's stocked for the session.", "Every lawmaker wants Potions.")},
    },
    "add_objects": [
        # the old ice plant is locked until the post-game; the worker stands on its door's only approach cell (39, 26)
        {"id": "LOCALID_POINTE_ROUGE_ICE_PLANT_GUARD", "gfx": "OBJ_EVENT_GFX_WORKER_M", "x": 39, "y": 26, "move": FACE + "DOWN",
         "text": T("The old ice plant is padlocked.", "Cold room's off limits. For now.")},
    ],
    "add_hidden": [
        {"x": 10, "y": 44, "item": "ITEM_BLACK_AUGURITE", "flag": "FLAG_POINTE_HIDDEN_AUGURITE", "_note": "rail yard (obtainability.md)"},
    ],
    # the refinery gate (rows 33, 34 of the fence): the first time the player walks in, a worker explains the leak
    "triggers": [
        {"x": 19, "y": y, "var": "VAR_ORLEANS_STORY", "value": 18, "script": "PointeRouge_EventScript_RefineryGate"}
        for y in (33, 34)
    ],
}

# ---------------------------------------------------------------------------------------------- the rooms
ROOMS = {
    "pointe_rouge_gym": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_1"},
                 1: {"custom": True, "sight": 3, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_BOY_2"},
                 2: {"custom": True, "sight": 3, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_FISHERMAN"},
                 3: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_4"}},
        # two nets hang across the gaps (6, 7) and (14, 7) in the net-rack wall: the only ways to Kingfisher's rafters. They are
        # hidden once the tailwind is up (FLAG_POINTE_GYM_TAILWIND). The Fearowite ball lies in the rafters.
        "extra": [
            ("net", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "flag": "FLAG_POINTE_GYM_TAILWIND"}, (6, 7)),
            ("net", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "flag": "FLAG_POINTE_GYM_TAILWIND"}, (14, 7)),
            ("fearowite", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_POINTE_ITEM_FEAROWITE"}, (12, 3)),
        ],
        # the three fans (west, centre on the rack, east); standing next to one and pressing A runs its script
        "bg_events": [
            {"type": "sign", "x": 6, "y": 11, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Gym_EventScript_FanWest"},
            {"type": "sign", "x": 10, "y": 7, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Gym_EventScript_FanCentre"},
            {"type": "sign", "x": 14, "y": 11, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Gym_EventScript_FanEast"},
        ],
    },
    "pointe_rouge_refinery": {
        "opts": {0: {"custom": True, "sight": 3, "face": "DOWN", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M"},
                 1: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M"}},
        "extra": [
            ("camille", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F", "face": "DOWN", "flag": "FLAG_HIDE_POINTE_CAMILLE"}, (11, 13)),
            ("jayden", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_BOY_1", "face": "DOWN", "flag": "FLAG_HIDE_POINTE_JAYDEN"}, (12, 13)),
            ("smoke ball", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_POINTE_ITEM_SMOKE_BALL"}, (20, 14)),
            ("metal coat", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_POINTE_ITEM_METAL_COAT"}, (1, 3)),
        ],
        # the four leaking valves sit on the pipes (rows 4 and 9)
        "bg_events": [
            {"type": "sign", "x": 7, "y": 4, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Refinery_EventScript_Valve1"},
            {"type": "sign", "x": 15, "y": 4, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Refinery_EventScript_Valve2"},
            {"type": "sign", "x": 7, "y": 9, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Refinery_EventScript_Valve3"},
            {"type": "sign", "x": 15, "y": 9, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_Refinery_EventScript_Valve4"},
        ],
    },
    "pointe_rouge_tackle_shop": {
        "opts": {0: {"custom": True}, 1: {"custom": True}},
    },
    "pointe_rouge_pokecenter": {
        "texts": {1: T("Something's wrong at the plant. They", "sent every one of us home."),
                  2: T("The fishing tournament on Route 5 decides", "who may face KINGFISHER.")},
    },
    "pointe_rouge_house_nw": {
        "texts": {0: T("Forty years at the refinery. I never", "saw a leak like this one."),
                  1: T("I want to be a Bird Keeper like", "KINGFISHER when I grow up!")},
    },
    "pointe_rouge_house_ne": {
        "texts": {0: T("These trophies are all from the", "river tournament. None are mine.")},
    },
    "pointe_rouge_house_s": {
        "texts": {0: T("There's a strange stone in the", "smokestack yard. Heavy. Hums.")},
    },
    "pointe_rouge_capitol_lobby": {
        "texts": {0: T("The observation deck is open to the", "public. Elevator's on the right."),
                  1: T("The tower went up after the great", "flood of '27. Nothing's moved it.")},
    },
    "pointe_rouge_capitol_deck": {
        "texts": {0: T("Down there, my house stood before the", "river moved. Funny, what a river does.")},
        "bg_events": [
            {"type": "sign", "x": 3, "y": 5, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_CapitolDeck_EventScript_TelescopeEast"},
            {"type": "sign", "x": 8, "y": 5, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_CapitolDeck_EventScript_TelescopeRiver"},
            {"type": "sign", "x": 13, "y": 5, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "PointeRouge_CapitolDeck_EventScript_TelescopeBasin"},
        ],
    },
}

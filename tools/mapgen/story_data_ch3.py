"""Chapter 3 data for story_overlay.py: Crescent City's people, items and rooms (merged into OVERLAY / INTERIOR there).

T(...) builds a Gen-3 text: lines of up to 36 characters, two lines to a page (the Python side only joins them:
story_lint.py checks the generated scripts).
"""
B = chr(92)


def T(*lines):
    out = ""
    for i, ln in enumerate(lines):
        if i:
            out += (B + "p") if i % 2 == 0 else (B + "n")
        out += ln
    return out


FACE = "MOVEMENT_TYPE_FACE_"

# ---------------------------------------------------------------------------------------------- the city (outdoors)
CRESCENT = {
    # the seven halls' doors are warps (crescent.py), the sign lists them
    "patch_signs": {"FrontierSign": {"text": "BATTLE FRONTIER\nOpen to champions only.\\pTOWER  DOME  PALACE  ARENA\nFACTORY  PIKE  PYRAMID"}},
    "patch_objects": {
        # Lafayette waits at the conservation center's door while the story is 13 (Crescent's OnTransition hides him otherwise)
        "LOCALID_CRESCENT_CITY_LAFAYETTE": {"custom": True, "gfx": "OBJ_EVENT_GFX_SCIENTIST_1", "flag": "FLAG_HIDE_CRESCENT_LAFAYETTE"},
        "LOCALID_CRESCENT_CITY_PARADE_LEADER": {"custom": True, "gfx": "OBJ_EVENT_GFX_BARD"},
        "LOCALID_CRESCENT_CITY_FRONTIER_GUARD": {"text": T("The seven halls of the FRONTIER", "open after the Rayquaza finale.")},
        "LOCALID_CRESCENT_CITY_PARK_STROLLER": {"text": T("The magnolias here came from GRAND", "OAK, years ago. They took.")},
        "LOCALID_CRESCENT_CITY_MOURNER": {"text": T("The old tombs flooded to the lids.", "We rebuilt every one by hand.")},
        "LOCALID_CRESCENT_CITY_SHOPPER": {"text": T("The department store has three", "floors. Mind the second, it's TMs.")},
        "LOCALID_CRESCENT_CITY_QUARTER_GENT": {"text": T("The second line parade comes through", "here at noon. Mind the brass.")},
        "LOCALID_CRESCENT_CITY_QUARTER_LASS": {"text": T("I came for the music. Stayed for", "the beignets.")},
        "LOCALID_CRESCENT_CITY_SAILOR": {"text": T("The riverboat for POINTE ROUGE", "leaves from the terminal, west.")},
        "LOCALID_CRESCENT_CITY_FISHERMAN": {"text": T("Catfish the size of a door in the", "Emerald River. Truly.")},
        "LOCALID_CRESCENT_CITY_STROLLER": {"text": T("The conservation center is the best", "zoo I ever saw. And I've seen two.")},
        "LOCALID_CRESCENT_CITY_OLD_MAN": {"text": T("These levees held through two", "storms. Three, if you count mine.")},
        "LOCALID_CRESCENT_CITY_VERGE_BOY": {"text": T("Wild POKéMON gather at the edge of", "the park after dark.")},
        "LOCALID_CRESCENT_CITY_BUSKER": {"text": T("A tune for the shoppers! Tips go", "in the hat. The hat is a boot.")},
        "LOCALID_CRESCENT_CITY_SHOP_MOM": {"text": T("Everything cost triple while the", "bridge was up. Now it's merely dear.")},
        "LOCALID_CRESCENT_CITY_PAINTER": {"text": T("The light on the pond is perfect", "today. Don't move. Don't breathe.")},
        "LOCALID_CRESCENT_CITY_PARK_KID": {"text": T("I saw something red in the long", "grass! Maybe it was a flower.")},
        "LOCALID_CRESCENT_CITY_CONSERVATION_KID": {"text": T("There's a real alligator inside!", "It looked at me. I looked back.")},
        "LOCALID_CRESCENT_CITY_FRONTIER_JOGGER": {"text": T("I'm training for the Frontier.", "Four laps of the plaza, daily.")},
        "LOCALID_CRESCENT_CITY_FRONTIER_PAIR": {"custom": True},   # two states (story/CrescentCity.inc): before and after the ending
        "LOCALID_CRESCENT_CITY_FRONTIER_FAN": {"text": T("One day I'll battle at the Dome.", "One day. Soon.")},
        "LOCALID_CRESCENT_CITY_PICNICKER": {"text": T("The levee breeze is lovely. The", "ants are less lovely.")},
    },
    "add_objects": [
        # Wren at the Drowned Ward gate once Fifolet is beaten (story 16; hidden otherwise by Crescent's OnTransition)
        {"id": "LOCALID_CRESCENT_CITY_WREN", "gfx": "OBJ_EVENT_GFX_GIRL_3", "x": 60, "y": 27, "move": FACE + "RIGHT",
         "text": "", "custom": True, "flag": "FLAG_HIDE_CRESCENT_WREN"},
        # the Drowned Ward's door has one approach cell (62,27): a ward worker stands on it until the third badge (hidden by
        # FLAG_BADGE03_GET), so the base cannot be entered, or its carving found, before Fifolet
        {"id": "LOCALID_CRESCENT_CITY_WARD_GUARD", "gfx": "OBJ_EVENT_GFX_WORKER_M", "x": 62, "y": 27, "move": FACE + "DOWN",
         "text": "", "custom": True, "flag": "FLAG_BADGE03_GET"},
        # the gym's usher on its only approach cell (22,19) until the briefing and the market speech are done (story 15)
        {"id": "LOCALID_CRESCENT_CITY_GYM_USHER", "gfx": "OBJ_EVENT_GFX_WORKER_F", "x": 22, "y": 19, "move": FACE + "DOWN",
         "text": "", "custom": True, "flag": "FLAG_HIDE_CRESCENT_GYM_USHER"},
        # the waterfront generator Rotom (the last of the five)
        {"id": "LOCALID_CRESCENT_CITY_ROTOM_GENERATOR", "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "x": 69, "y": 35,
         "move": FACE + "DOWN", "text": "", "custom": True, "flag": "FLAG_CRESCENT_ROTOM_GENERATOR"},
        # City Park's lawn mower (the fifth appliance; with the TV, blender, washer, freezer and generator that is every form)
        {"id": "LOCALID_CRESCENT_CITY_ROTOM_MOW", "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "x": 10, "y": 42,
         "move": FACE + "DOWN", "text": "", "custom": True, "flag": "FLAG_CRESCENT_ROTOM_MOW"},
    ],
    # Bottle Caps for the IV judge (decision 6): two hidden in the city, one each on Routes 3 and 4, one from Lafayette at 15 species
    "add_hidden": [
        {"x": 16, "y": 24, "item": "ITEM_BOTTLE_CAP", "flag": "FLAG_UNUSED_0x26F", "_note": "between the old tombs"},
        {"x": 9, "y": 38, "item": "ITEM_BOTTLE_CAP", "flag": "FLAG_UNUSED_0x2AD", "_note": "City Park, behind the mower"},
    ],
    "add_items": [
        {"x": 7, "y": 24, "item": "ITEM_GENGARITE", "flag": "FLAG_UNUSED_0x269", "_comment": "Mega Stone (night path, old cemetery)"},
        {"x": 13, "y": 38, "item": "ITEM_SCIZORITE", "flag": "FLAG_UNUSED_0x26A", "_comment": "Mega Stone (the park tree)"},
    ],
}

ROUTE3 = {"add_hidden": [{"x": 40, "y": 20, "item": "ITEM_BOTTLE_CAP", "flag": "FLAG_UNUSED_0x2AE", "_note": "south verge"}]}

# Pointe Rouge's east exit to Route 23 is closed by a dust storm until Rayquaza wakes (story 38, the plan; FLAG_DUST_STORMS_LIFTED is set by that beat).
# Every cell of the last column (x=65) runs the same script, which turns the player back; both bridges and every
# other approach end in that column. "var" is a FLAG id tested as a flag (fires while FLAG_DUST_STORMS_LIFTED is clear).
_PR_EAST_ROWS = tuple(range(0, 48))  # every row: a trigger on a blocked cell never fires, and the terrain may change under it
POINTE_ROUGE = {
    "triggers": [{"x": 65, "y": y, "elevation": e, "var": "FLAG_DUST_STORMS_LIFTED", "value": 0, "script": "PointeRouge_EventScript_DustStorm"}
                 for y in _PR_EAST_ROWS for e in (3, 1)],  # elevation 1 = a surfer on water
}

# Route 4's landing: the deckhand who takes the player back to Crescent City
ROUTE4 = {
    "add_hidden": [{"x": 3, "y": 33, "item": "ITEM_BOTTLE_CAP", "flag": "FLAG_UNUSED_0x2AF", "_note": "west bank, off the road"}],
    "add_objects": [
        {"id": "LOCALID_ORLEANS_ROUTE4_DECKHAND", "gfx": "OBJ_EVENT_GFX_SAILOR", "x": 22, "y": 42, "move": FACE + "LEFT",
         "text": "", "custom": True},
    ],
}

# ---------------------------------------------------------------------------------------------- the rooms
ROOMS = {
    "crescent_city_gym": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_HEX_MANIAC"},
                 1: {"custom": True, "sight": 3, "face": "DOWN", "gfx": "OBJ_EVENT_GFX_HEX_MANIAC"},
                 2: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": "OBJ_EVENT_GFX_HEX_MANIAC"},   # Lucille (Psychic, Pic F)
                 3: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_4"}},
        # the five lights (mockup switches; two blue on the true way, three orange on the loops that tempt): stepping on one runs its script while the badge is not earned
        "coord_events": [
            {"type": "trigger", "x": 14, "y": 11, "elevation": 3, "var": "FLAG_BADGE03_GET", "var_value": "0",
             "script": "CrescentCity_Gym_EventScript_BlueLight"},
            {"type": "trigger", "x": 12, "y": 8, "elevation": 3, "var": "FLAG_BADGE03_GET", "var_value": "0",
             "script": "CrescentCity_Gym_EventScript_BlueLight"},
            {"type": "trigger", "x": 6, "y": 12, "elevation": 3, "var": "FLAG_BADGE03_GET", "var_value": "0",
             "script": "CrescentCity_Gym_EventScript_OrangeLight"},
            {"type": "trigger", "x": 16, "y": 10, "elevation": 3, "var": "FLAG_BADGE03_GET", "var_value": "0",
             "script": "CrescentCity_Gym_EventScript_OrangeLight"},
            {"type": "trigger", "x": 18, "y": 8, "elevation": 3, "var": "FLAG_BADGE03_GET", "var_value": "0",
             "script": "CrescentCity_Gym_EventScript_OrangeLight"},
        ],
    },
    "crescent_city_blacksnake_base": {
        "opts": {0: {"custom": True, "sight": 3, "face": "DOWN", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M"},
                 1: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_M"},
                 2: {"custom": True, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F"},   # Louise: the lieutenant's guard, the partner battle (talk to start)
                 3: {"custom": True, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F", "flag": "FLAG_HIDE_CRESCENT_LIEUTENANT"},
                 4: {"custom": True, "gfx": "OBJ_EVENT_GFX_GIRL_3", "face": "UP", "flag": "FLAG_HIDE_CRESCENT_BASE_WREN"}},
        "bg_events": [
            {"type": "sign", "x": 3, "y": 13, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "CrescentCity_BlacksnakeBase_EventScript_Carving"},
            {"type": "hidden_item", "x": 20, "y": 3, "elevation": 3, "item": "ITEM_DUSK_BALL", "flag": "FLAG_UNUSED_0x26B"},
        ],
    },
    "crescent_city_conservation": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_SCIENTIST_1"}, 1: {"custom": True}},
        "extra": [("scientist", T("The fossil lab revives a fossil once", "you bring one. Mind the dust."), {"custom": True, "gfx": "OBJ_EVENT_GFX_SCIENTIST_1"}, (11, 9))],
    },
    "crescent_city_apartment": {"opts": {0: {"custom": True}}},
    "crescent_city_cafe": {
        "opts": {0: {"custom": True}},
        "texts": {1: T("Pokéblocks make my POKéMON happy.", "And a little glossy.")},
        "extra": [("rotom blender", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "flag": "FLAG_CRESCENT_ROTOM_BLENDER"}, (6, 3))],
    },
    "crescent_city_ice_cream": {
        "opts": {0: {"custom": True}},
        "texts": {1: T("The freezer growled at me!", "Cold in there. Colder than usual.")},
        "extra": [("rotom freezer", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "flag": "FLAG_CRESCENT_ROTOM_FREEZER"}, (7, 2))],
    },
    "crescent_city_laundry": {
        "texts": {0: T("One machine keeps running with", "nothing in it. I've stopped asking.")},
        "extra": [("rotom washer", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "flag": "FLAG_CRESCENT_ROTOM_WASHER"}, (5, 3))],
    },
    "crescent_city_dept_1f": {
        "texts": {0: T("Welcome! First floor: balls and", "medicine. Second: TMs and stones.")},
        "opts": {1: {"custom": True}},
        "extra": [("rotom tv", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(ROTOM)", "flag": "FLAG_CRESCENT_ROTOM_TV"}, (14, 8))],
    },
    "crescent_city_dept_2f": {
        "opts": {0: {"custom": True}, 1: {"custom": True}},
        "texts": {2: T("Trade evolutions only need a", "Linking Cord here. No trade!")},
    },
    "crescent_city_dept_3f": {
        "opts": {0: {"custom": True}, 1: {"custom": True}},
        "texts": {2: T("Mega Stones mean nothing without", "the cypress charm.")},
    },
    "crescent_city_game_corner": {
        "texts": {0: T("The Game Corner is closed while the", "machines dry out. Back soon!"),
                  1: T("The coin exchange is closed too.", "Sorry!"),
                  2: T("The third slot always paid out", "after a storm. I'll wait.")},
    },
    "crescent_city_salon": {
        "opts": {0: {"custom": True}},
        "texts": {1: T("My Furfrou has never looked", "better. Never.")},
    },
    "crescent_city_name_rater": {
        "extra": [("name rater", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_3"}, (5, 3))],
    },
    "crescent_city_tutor": {
        "extra": [("move tutor", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_2"}, (2, 4)),
                  ("ev coach", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_BLACK_BELT"}, (7, 4)),
                  ("iv judge", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_EXPERT_F"}, (2, 6))],
    },
    "crescent_city_day_care": {"opts": {0: {"custom": True}, 1: {"custom": True}}},
    "crescent_city_riverboat_terminal": {"opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_1"}}},
    "crescent_city_pelipper_post": {
        "texts": {0: T("Mail goes out on the hour. Birds", "go out whenever they feel like it.")},
        "opts": {1: {"custom": True}},
    },
    "crescent_city_cathedral": {
        "texts": {0: T("The city kept its bells through the", "storm. Every one rang."),
                  1: T("A tune like the Rootkin's songs, you", "say? ...Where did you hear it?")},
    },
    "crescent_city_trades": {
        "texts": {0: T("I'd swap a Kantonian Sandshrew for", "an Alolan one, if you have it."),
                  1: T("Alolan Vulpix for a Kantonian one.", "If both make the dex, of course."),
                  2: T("I like regional forms side by side.", "Don't you?")},
    },
    "crescent_city_pokecenter_quarter": {
        "texts": {1: T("I came for the music. Stayed for", "the storm cleanup."),
                  2: T("The second line passes right by", "here. You can hear it start.")},
    },
    "crescent_city_pokecenter_waterfront": {
        "texts": {1: T("The riverboat to POINTE ROUGE leaves", "from the terminal, west of here.")},
    },
}

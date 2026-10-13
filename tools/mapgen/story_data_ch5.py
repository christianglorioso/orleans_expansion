"""Chapter 5 data for story_overlay.py: Routes 6-9, Camp Cocodrie (outdoors and rooms), merged there. Trainers are a table (TRAINERS) that
gen_route_trainers.py turns into trainers/orleans_ch5.party and the trainer scripts in story/Route<N>.inc.
"""
from story_data_ch3 import T, FACE

# ---------------------------------------------------------------------------------------------- the route trainers
# m = map, n = the mockup marker id (the script is <Map>_EventScript_Trainer<n>), levels climb 31 -> 36 west to east / by route
SW = "OBJ_EVENT_GFX_SWIMMER_M"
SWF = "OBJ_EVENT_GFX_SWIMMER_F"
TRAINERS = [
    # ---- Route 6 (the big lake west of Crescent)
    dict(m="Route6", n=0, const="TRAINER_ORLEANS_ROUTE6_SWIMMER", name="TRISTAN", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="LEFT", sight=4, team=[("Tentacruel", 31), ("Wailmer", 31), ("Floatzel", 32)],
         intro=T("The lake's mine! I swim it every", "morning. Race you, with POKéMON!"),
         defeat=T("Outswum."), after=T("The current bends west. It wants to", "carry you to the camp.")),
    dict(m="Route6", n=2, const="TRAINER_ORLEANS_ROUTE6_FISHERMAN", name="DESIRE", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="DOWN", sight=4, team=[("Whiscash", 31), ("Quagsire", 32), ("Gyarados", 32)],
         intro=T("Fishing the old drowned road. The", "big ones sleep on the pavement."),
         defeat=T("The big one got away. It was you."), after=T("Cast near the old lampposts. They", "like the shade.")),
    dict(m="Route6", n=4, const="TRAINER_ORLEANS_ROUTE6_SWIMMER_F", name="ANASTASIE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="LEFT", sight=4, team=[("Frillish", 31), ("Masquerain", 32), ("Golduck", 32)],
         intro=T("You came by water! Brave. Or", "silly. Let's find out!"),
         defeat=T("Silly, then. Brave too."), after=T("The storm moved everything. Even", "the fish are lost.")),
    dict(m="Route6", n=6, const="TRAINER_ORLEANS_ROUTE6_SAILOR", name="MAXIME", cls="Sailor", pic="Sailor", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_SAILOR", face="UP", sight=4, team=[("Pelipper", 32), ("Cloyster", 32), ("Tentacruel", 33)],
         intro=T("A landlubber on my shore! Show", "me you can keep your footing!"),
         defeat=T("Knocked off my feet."), after=T("Past the jam it's open water.", "Mind the currents.")),
    # ---- Route 7
    dict(m="Route7", n=2, const="TRAINER_ORLEANS_ROUTE7_CAMPER", name="LEON", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="DOWN", sight=4, team=[("Breloom", 32), ("Toxicroak", 32), ("Sandslash", 33)],
         intro=T("The bayou's the best campground", "in the region. Mind the gators!"),
         defeat=T("Smashed my tent."), after=T("A stump near here holds a cache.", "Needs a Pry Bar, though.")),
    dict(m="Route7", n=3, const="TRAINER_ORLEANS_ROUTE7_PICNICKER", name="CLEMENCE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="LEFT", sight=4, team=[("Amoonguss", 33), ("Lilligant", 33), ("Masquerain", 33)],
         intro=T("I picked a spot for lunch and", "it's already taken. By you!"),
         defeat=T("Lunch is ruined."), after=T("The camp's gumbo is worth the", "trip. Ask for the real roux.")),
    dict(m="Route7", n=4, const="TRAINER_ORLEANS_ROUTE7_BUG_MANIAC", name="REMY", cls="Bug Maniac", pic="Bug Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BUG_CATCHER", face="RIGHT", sight=4, team=[("Ledian", 32), ("Ninjask", 33), ("Parasect", 33)],
         intro=T("Fireflies and ninjask! The bayou", "at night is my lab."),
         defeat=T("My lab is in ruins."), after=T("Ninjask molts at the cypress knees.", "Collect the shells!")),
    dict(m="Route7", n=5, const="TRAINER_ORLEANS_ROUTE7_BIRD_KEEPER", name="NICOLAS", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="LEFT", sight=4, team=[("Swanna", 33), ("Noctowl", 33), ("Staraptor", 34)],
         intro=T("My flock hunts these islands.", "Prove you can fly with them."),
         defeat=T("Grounded."), after=T("A swanna never sinks. Neither", "does a good plan.")),
    # ---- Route 8
    dict(m="Route8", n=0, const="TRAINER_ORLEANS_ROUTE8_HIKER", name="GILBERT", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="DOWN", sight=4, team=[("Boldore", 33), ("Carkol", 34), ("Coalossal", 35)],
         intro=T("No mountains here, so I hike", "the dikes. Stone's stone!"),
         defeat=T("Cracked."), after=T("The channel north of here is shut.", "Storm wall. Nobody sails it.")),
    dict(m="Route8", n=2, const="TRAINER_ORLEANS_ROUTE8_SWIMMER", name="PHILIPPE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Sharpedo", 34), ("Jellicent", 34), ("Drednaw", 34)],
         intro=T("Deep water, deep trouble. In", "you go!"),
         defeat=T("Blub."), after=T("Sharpedo hunt the reed edge.", "Stay out of the shallows.")),
    dict(m="Route8", n=3, const="TRAINER_ORLEANS_ROUTE8_SWIMMER_F", name="ELOISE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="LEFT", sight=4, team=[("Araquanid", 34), ("Cloyster", 34), ("Wailord", 35)],
         intro=T("A fellow swimmer! No, a trainer.", "Even better!"),
         defeat=T("Soaked, in every way."), after=T("The camp is west. The brothers", "cook on a boat of a stove.")),
    dict(m="Route8", n=6, const="TRAINER_ORLEANS_ROUTE8_FISHERMAN", name="AUGUSTIN", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="UP", sight=4, team=[("Whiscash", 34), ("Barbaracle", 34), ("Floatzel", 35)],
         intro=T("The tide's out on my fishing", "hole. The mood's out too."),
         defeat=T("Hooked."), after=T("Barbaracle grip the rocks. They", "never let go.")),
    dict(m="Route8", n=7, const="TRAINER_ORLEANS_ROUTE8_CAMPER", name="JULES", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="LEFT", sight=4, team=[("Excadrill", 34), ("Ursaring", 34), ("Sandslash", 34)],
         intro=T("I dig where I camp. Nobody", "tells me otherwise!"),
         defeat=T("Dug my own hole."), after=T("Something hums in the north", "channel. Don't go yet.")),
    # ---- Route 9
    dict(m="Route9", n=1, const="TRAINER_ORLEANS_ROUTE9_PICNICKER", name="AGATHE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="DOWN", sight=4, team=[("Vileplume", 35), ("Ribombee", 35), ("Lilligant", 35)],
         intro=T("My garden came through the storm.", "Barely. Like me!"),
         defeat=T("Wilted."), after=T("The camp's okra is the best in", "the region. Ask the gardener.")),
    dict(m="Route9", n=2, const="TRAINER_ORLEANS_ROUTE9_HIKER", name="FABIEN", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="DOWN", sight=4, team=[("Gigalith", 35), ("Sudowoodo-Orleanian", 35), ("Ursaring", 36)],
         intro=T("A hiker, a bayou, a boulder.", "That's my whole life!"),
         defeat=T("Rock bottom."), after=T("Stone and cypress. That's the", "old way.")),
    dict(m="Route9", n=3, const="TRAINER_ORLEANS_ROUTE9_SAILOR", name="TIBERE", cls="Sailor", pic="Sailor", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_SAILOR", face="DOWN", sight=4, team=[("Kingler-Orleanian", 35), ("Cloyster", 35), ("Pelipper", 36)],
         intro=T("Camp's just ahead, sailor. But", "first, a toll!"),
         defeat=T("Paid in full."), after=T("The brothers like their gumbo", "thick. Don't call it soup.")),
    dict(m="Route9", n=5, const="TRAINER_ORLEANS_ROUTE9_BIRD_KEEPER", name="HONORE", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="RIGHT", sight=4, team=[("Toucannon", 36), ("Corvisquire", 36), ("Swanna", 36)],
         intro=T("My birds smell the gumbo from", "here. Let's earn a bowl."),
         defeat=T("No bowl for me."), after=T("Fly low over the camp. The", "smoke carries news.")),
]

# the camp's own trainers: Isaac (before the gym), the fisherman (shrimp for the cook-off) and the brothers (the double battle)
CAMP_PARTIES = [
    dict(const="TRAINER_ORLEANS_ISAAC_CAMP", name="ISAAC", cls="Aqua Admin", pic="Aqua Admin M", sex="Male", music="Aqua",
         team=[("Sharpedo", 33), ("Tentacruel", 34), ("Floatzel", 34)], ai="Basic Trainer"),
    dict(const="TRAINER_ORLEANS_CAMP_FISHERMAN", name="GASTON", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         team=[("Barboach", 33), ("Whiscash", 34), ("Crawdaunt-Orleanian", 34)], ai="Basic Trainer"),
    dict(const="TRAINER_BOUDREAUX", name="BOUDREAUX", cls="Leader", pic="Hiker", sex="Male", music="Male",
         team=[("Whiscash", 36, ["Waterfall", "Earthquake", "Amnesia", "Rest"]), ("Toxicroak", 37, ["Sludge Bomb", "Drain Punch", "Poison Jab", "Earthquake"]),
               ("Krookodile", 39, ["Earthquake", "Crunch", "Rock Slide", "Dig"])],
         ai="Check Bad Move / Try To Faint", iv=24),
    dict(const="TRAINER_THIBODEAUX", name="THIBODEAUX", cls="Leader", pic="Fisherman", sex="Male", music="Male",
         team=[("Amoonguss", 36, ["Giga Drain", "Sludge Bomb", "Stun Spore", "Protect"]), ("Breloom", 37, ["Mach Punch", "Seed Bomb", "Spore", "Bullet Seed"]),
               ("Crawdaunt-Orleanian", 39, ["Crabhammer", "Crunch", "Swords Dance", "Flamethrower"])],
         ai="Check Bad Move / Try To Faint", iv=24),
]

# ---------------------------------------------------------------------------------------------- Routes 6-9 overlay
def _patch(m):
    out = {}
    for t in TRAINERS:
        if t["m"] != m:
            continue
        out[f"LOCALID_ORLEANS_{m.upper()}_TRAINER_{t['n']}"] = {"gfx": t["gfx"], "move": FACE + t["face"], "sight": t["sight"], "custom": True}
    return out


ROUTE6 = {
    "patch_objects": _patch("Route6"),
    "add_items": [{"x": 34, "y": 23, "item": "ITEM_TM_STEALTH_ROCK", "flag": "FLAG_ROUTE6_ITEM_STEALTH_ROCK", "_comment": "TM089, an item ball on Routes 3-9"}],
}
ROUTE7 = {
    "patch_objects": _patch("Route7"),
    "patch_items": {"FLAG_UNUSED_0x27B": {"item": "ITEM_TM_TRICK", "_comment": "TM111"}},
    "add_objects": [
        # the cut stump: a Pry Bar cache (decision 2: optional, never a gate). Kleavorite inside (obtainability.md)
        {"id": "LOCALID_ORLEANS_ROUTE7_STUMP", "gfx": "OBJ_EVENT_GFX_BREAKABLE_ROCK", "x": 14, "y": 15, "move": "MOVEMENT_TYPE_NONE",
         "text": "", "custom": True, "flag": "FLAG_ROUTE7_STUMP_OPENED"},
    ],
}
ROUTE8 = {
    "patch_objects": _patch("Route8"),
    "patch_items": {"FLAG_UNUSED_0x27C": {"item": "ITEM_TM_WILL_O_WISP", "_comment": "TM112"}},
    "add_items": [{"x": 38, "y": 20, "item": "ITEM_TM_NASTY_PLOT", "flag": "FLAG_ROUTE8_ITEM_NASTY_PLOT", "_comment": "TM095"}],
}
ROUTE9 = {
    "patch_objects": _patch("Route9"),
    "patch_items": {"FLAG_UNUSED_0x27D": {"item": "ITEM_TM_ENCORE", "_comment": "TM094"}},
}

# ---------------------------------------------------------------------------------------------- Camp Cocodrie (outdoors)
CAMP = {
    "patch_objects": {
        "LOCALID_CAMP_COCODRIE_BOUDREAUX": {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_3"},
        "LOCALID_CAMP_COCODRIE_THIBODEAUX": {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_1"},
        "LOCALID_CAMP_COCODRIE_FISHERMAN": {"custom": True},
        # Isaac stands on the nurse cabin's only approach cell (7, 22) until his battle is won
        "LOCALID_CAMP_COCODRIE_ISAAC": {"custom": True, "gfx": "OBJ_EVENT_GFX_BOY_1", "x": 7, "y": 22, "move": FACE + "DOWN", "sight": 3,
                                        "flag": "FLAG_HIDE_CAMP_ISAAC"},
        "LOCALID_CAMP_COCODRIE_OLD_NEIGHBOUR": {"text": T("My grandson plays the porch.", "Cabin's open if you want filé.")},
        "LOCALID_CAMP_COCODRIE_ZYDECO_ACCORDION": {"text": T("Zydeco isn't played. It's survived.", "Come back at night.")},
        "LOCALID_CAMP_COCODRIE_ZYDECO_RUBBOARD": {"text": T("The rub-board's older than the camp.", "Don't touch. It bites.")},
        "LOCALID_CAMP_COCODRIE_WRANGLER": {"text": T("Gator pens are behind the cabins.", "They're friendlier than they look.")},
        "LOCALID_CAMP_COCODRIE_KID": {"text": T("The brothers make their gumbo by", "arguing. It tastes the same!")},
        "LOCALID_CAMP_COCODRIE_SMOKER": {"text": T("The smokehouse door's always open.", "The sausage doesn't mind.")},
    },
    "patch_signs": {
        "SignLanding": {"text": "CAMP COCODRIE\nGator pens: look, don't touch."},
        "SignCookhouse": {"text": "COOKHOUSE\nBring your own fixings!"},
    },
    "patch_items": {
        "FLAG_UNUSED_0x276": {"item": "ITEM_TM_BATON_PASS", "_comment": "TM113"},
        "FLAG_UNUSED_0x28E": {"item": "ITEM_TM_IRON_DEFENSE", "_comment": "TM114"},
        "FLAG_UNUSED_0x275": {"item": "ITEM_SHINY_STONE", "_comment": "evolution stone (obtainability.md)"},
        "FLAG_UNUSED_0x274": {"item": "ITEM_HYPER_POTION"},
    },
    "add_hidden": [
        {"x": 1, "y": 21, "item": "ITEM_PEAT_BLOCK", "flag": "FLAG_CAMP_HIDDEN_PEAT_BLOCK", "_note": "evolution item (obtainability.md): Ursaring -> Ursaluna at night"},
    ],
    # the okra garden behind cabin 4 (north-east): picked after the gardener has been asked
    "signs": [
        {"id": "OkraPatch1", "x": 45, "y": 6, "text": "", "custom": True},
        {"id": "OkraPatch2", "x": 46, "y": 6, "text": "", "custom": True},
    ],
}

# ---------------------------------------------------------------------------------------------- the camp's rooms
ROOMS = {
    "camp_cocodrie_gym": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_3", "face": "DOWN"}, 1: {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_1", "face": "DOWN"},
                 2: {"custom": True}},
        "bg_events": [  # the judging table: stand below it (9, 4) and press A facing up
            {"type": "sign", "x": 9, "y": 3, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "CampCocodrie_Gym_EventScript_JudgingTable"},
        ],
    },
    "camp_cocodrie_nurse_cabin": {"texts": {}},
    "camp_cocodrie_bait_shack": {"opts": {0: {"custom": True}}, "texts": {1: T("The shrimp comes off the dock.", "GASTON runs it. He fights for it.")}},
    "camp_cocodrie_smokehouse": {
        "opts": {0: {"custom": True}},
        "bg_events": [  # the smoker's fire door (the smoker block is x 4-6, y 4-5): stand below (5, 6)
            {"type": "sign", "x": 5, "y": 5, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": "CampCocodrie_Smokehouse_EventScript_FireDoor"},
        ],
    },
    "camp_cocodrie_cabin_1": {"opts": {0: {"custom": True}}},
    "camp_cocodrie_cabin_2": {"texts": {0: T("The Krokorok pen's out back. The", "brothers raised every one by hand.")}},
    "camp_cocodrie_cabin_3": {"texts": {0: T("I run the airboat. It hauls shrimp,", "not people. Your POKéMON can swim.")}},
    "camp_cocodrie_cabin_4": {"opts": {0: {"custom": True}}},
    "camp_cocodrie_dance_porch": {
        "opts": {0: {"custom": True}},
        "texts": {1: T("The accordion player came from ISLE", "MARAIS. Same tune, other bayou."),
                  2: T("Grandma has filé, if you ask nicely.", "Very nicely.")},
    },
}

"""Chapter 6 data for story_overlay.py: Routes 10-13, Lutin's Hollow (outdoors and rooms), the Old Water carver. Trainers are a table
(TRAINERS + EXTRA_PARTIES) for gen_route_trainers.py (python tools/mapgen/gen_route_trainers.py ch6).
"""
from story_data_ch3 import T, FACE

SW = "OBJ_EVENT_GFX_SWIMMER_M"
SWF = "OBJ_EVENT_GFX_SWIMMER_F"

TRAINERS = [
    # ---- Route 10 (Crescent's lakefront canal, 36-37)
    dict(m="Route10", n=0, const="TRAINER_ORLEANS_ROUTE10_SWIMMER", name="BAPTISTE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Tentacruel", 36), ("Floatzel", 36), ("Wailord", 37)],
         intro=T("The lake road's open again! I", "swim it just to say I can."), defeat=T("Dunked."),
         after=T("The brothers' gumbo smell carries", "all the way to the canal.")),
    dict(m="Route10", n=2, const="TRAINER_ORLEANS_ROUTE10_SWIMMER_F", name="CELESTE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="RIGHT", sight=4, team=[("Jellicent", 36), ("Masquerain", 36), ("Golduck", 37)],
         intro=T("Big Lake is bigger than it looks.", "Don't drown. Battle!"), defeat=T("Bubbles."),
         after=T("Past the jam, the lake is clear.", "Mostly.")),
    dict(m="Route10", n=3, const="TRAINER_ORLEANS_ROUTE10_SWIMMER_2", name="RENAUD", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="LEFT", sight=4, team=[("Sharpedo", 36), ("Drednaw", 37), ("Cloyster", 37)],
         intro=T("Nobody swims here uninvited.", "Except you. Fine!"), defeat=T("Swept away."),
         after=T("The current's strongest at the", "narrows. Hold on.")),
    dict(m="Route10", n=6, const="TRAINER_ORLEANS_ROUTE10_CAMPER", name="THEO", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="LEFT", sight=4, team=[("Sandslash", 36), ("Breloom", 37), ("Ursaring", 37)],
         intro=T("The shore road is mine. I", "pitched a tent on it!"), defeat=T("Tent's down."),
         after=T("A shrine hides in the meadow", "north of here, they say.")),
    # ---- Route 11
    dict(m="Route11", n=0, const="TRAINER_ORLEANS_ROUTE11_SWIMMER_F", name="HELOISE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Jellicent", 37), ("Araquanid", 37), ("Wailord", 38)],
         intro=T("The water's perfect today. Is", "your team, though?"), defeat=T("Lost the current."),
         after=T("The lake's colder past the", "second bend.")),
    dict(m="Route11", n=1, const="TRAINER_ORLEANS_ROUTE11_SWIMMER", name="ACHILLE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="LEFT", sight=4, team=[("Sharpedo", 37), ("Barbaracle", 38), ("Kingler-Orleanian", 38)],
         intro=T("I race the ferries. Today", "I race you!"), defeat=T("Second place again."),
         after=T("Routes 12 and 13 climb into", "the hills. It's green up there.")),
    dict(m="Route11", n=4, const="TRAINER_ORLEANS_ROUTE11_SWIMMER_2", name="OSCAR", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="UP", sight=4, team=[("Gyarados", 38), ("Quagsire", 37), ("Poliwrath", 38)],
         intro=T("Slow down! This is a toll lake.", "The toll is a battle."), defeat=T("Toll paid."),
         after=T("I saw something glow under the", "lilies at dusk. Twice.")),
    # ---- Route 12 (the hill road north, 38-39)
    dict(m="Route12", n=1, const="TRAINER_ORLEANS_ROUTE12_BIRD_KEEPER", name="ARTHUR", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="DOWN", sight=4, team=[("Staraptor", 38), ("Noctowl", 38), ("Swanna", 39)],
         intro=T("My birds like the hills. Up", "here the wind is honest."), defeat=T("Plucked."),
         after=T("Honest wind, honest trainer.", "Mostly honest.")),
    dict(m="Route12", n=2, const="TRAINER_ORLEANS_ROUTE12_HIKER", name="URBAIN", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="RIGHT", sight=4, team=[("Gigalith", 38), ("Coalossal", 39), ("Excadrill", 39)],
         intro=T("Hills, finally! I was going", "stir-crazy on the lake."), defeat=T("Avalanche."),
         after=T("Mind the roots. They trip", "everyone.")),
    dict(m="Route12", n=4, const="TRAINER_ORLEANS_ROUTE12_PICNICKER", name="LEONIE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="LEFT", sight=4, team=[("Lilligant", 38), ("Amoonguss", 38), ("Ribombee", 39)],
         intro=T("Wildflowers everywhere. I'm", "defending them!"), defeat=T("Trampled."),
         after=T("The hollow ahead is full of", "fairy rings. Don't step in one.")),
    dict(m="Route12", n=6, const="TRAINER_ORLEANS_ROUTE12_FISHERMAN", name="SERGE", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="UP", sight=4, team=[("Whiscash", 38), ("Gyarados", 38), ("Floatzel", 39)],
         intro=T("Even hills have ponds. This", "one's mine."), defeat=T("Off the line."),
         after=T("The pond is bottomless, they", "say. I've dropped a lot in it.")),
    # ---- Route 13 (the road to the hollow, 39-40)
    dict(m="Route13", n=0, const="TRAINER_ORLEANS_ROUTE13_BUG_MANIAC", name="ALCIDE", cls="Bug Maniac", pic="Bug Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BUG_CATCHER", face="DOWN", sight=4, team=[("Ninjask", 39), ("Ledian", 39), ("Parasect", 40)],
         intro=T("Fireflies lead to the hollow.", "I follow them. And fight."), defeat=T("Lights out."),
         after=T("They only glow for the polite.", "Be polite.")),
    dict(m="Route13", n=2, const="TRAINER_ORLEANS_ROUTE13_CAMPER", name="ROCH", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="RIGHT", sight=4, team=[("Toxicroak", 39), ("Breloom", 39), ("Ursaring", 40)],
         intro=T("Camped here two nights. The", "moss whispers. Battle me!"), defeat=T("Quiet now."),
         after=T("Don't answer the whispers.", "That's how they get you.")),
    dict(m="Route13", n=5, const="TRAINER_ORLEANS_ROUTE13_PICNICKER", name="AMELIE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="LEFT", sight=4, team=[("Floette", 39), ("Ribombee", 40), ("Lilligant", 39)],
         intro=T("I'm picking flowers for the", "hollow's fairies. Help?"), defeat=T("Petals everywhere."),
         after=T("A rose for the real one. The", "false ones don't take gifts.")),
    dict(m="Route13", n=7, const="TRAINER_ORLEANS_ROUTE13_BIRD_KEEPER", name="MATHIAS", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="UP", sight=4, team=[("Corviknight", 40), ("Swanna", 39), ("Noctowl", 40)],
         intro=T("Last stop before the hollow.", "Pay the road toll!"), defeat=T("Toll's paid."),
         after=T("The hollow's gate is a lane of", "moss. You'll feel watched.")),
]

# the hollow's own parties (not route trainers): the gym's two trainers, Jayden (battle 4, a variant per starter) and Lutin
EXTRA_PARTIES = [
    dict(const="TRAINER_ORLEANS_HOLLOW_GYM_LASS", name="MIRABELLE", cls="Lass", pic="Lass", sex="Female", music="Female",
         team=[("Floette", 38), ("Ribombee", 39), ("Mimikyu", 38)]),
    dict(const="TRAINER_ORLEANS_HOLLOW_GYM_PSYCHIC", name="AURELIEN", cls="Psychic", pic="Psychic M", sex="Male", music="Male",
         team=[("Hypno", 39), ("Wyrdeer", 39), ("Mimikyu", 38)]),
    dict(const="TRAINER_ORLEANS_JAYDEN_HOLLOW_CHIKORITA", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 38), ("Arbok", 39), ("Meganium", 40)], iv=22),
    dict(const="TRAINER_ORLEANS_JAYDEN_HOLLOW_FUECOCO", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 38), ("Arbok", 39), ("Skeledirge", 40)], iv=22),
    dict(const="TRAINER_ORLEANS_JAYDEN_HOLLOW_TOTODILE", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 38), ("Arbok", 39), ("Feraligatr", 40)], iv=22),
    dict(const="TRAINER_LUTIN", name="LUTIN", cls="Leader", pic="Hex Maniac", sex="Female", music="Female",
         team=[("Ribombee", 41, ["Moonblast", "Bug Buzz", "Stun Spore", "Protect"]), ("Mismagius", 41, ["Dazzling Gleam", "Shadow Ball", "Mystical Fire", "Thunder Wave"]),
               ("Grimmsnarl", 42, ["Play Rough", "Spirit Break", "Thunder Wave", "Taunt"]), ("Florges", 42, ["Moonblast", "Aromatherapy", "Psychic", "Protect"]),
               ("Milotic", 42, ["Scald", "Recover", "Ice Beam", "Dragon Tail"]), ("Delphox", 43, ["Fire Blast", "Dazzling Gleam", "Psychic", "Calm Mind"])],
         ai="Check Bad Move / Try To Faint", iv=26),
]

# ---------------------------------------------------------------------------------------------- Routes 10-13 overlay
def _patch(m):
    out = {}
    for t in TRAINERS:
        if t["m"] == m:
            out[f"LOCALID_ORLEANS_{m.upper()}_TRAINER_{t['n']}"] = {"gfx": t["gfx"], "move": FACE + t["face"], "sight": t["sight"], "custom": True}
    return out


ROUTE10 = {
    "patch_objects": _patch("Route10"),
    "add_items": [{"x": 9, "y": 16, "item": "ITEM_TM_CRUNCH", "flag": "FLAG_ROUTE10_ITEM_CRUNCH", "_comment": "TM093 (Routes 7-12)"}],
}
ROUTE11 = {
    "patch_objects": _patch("Route11"),
    "add_items": [{"x": 30, "y": 20, "item": "ITEM_TM_LIQUIDATION", "flag": "FLAG_ROUTE11_ITEM_LIQUIDATION", "_comment": "TM087 (Routes 7-12)"}],
    "add_hidden": [{"x": 31, "y": 22, "item": "ITEM_ICE_STONE", "flag": "FLAG_ROUTE11_HIDDEN_ICE_STONE", "_note": "evolution stone (obtainability.md)"}],
}
ROUTE12 = {
    "patch_objects": _patch("Route12"),
    "patch_items": {"FLAG_UNUSED_0x27E": {"item": "ITEM_TM_ENERGY_BALL", "flag": "FLAG_ROUTE12_ITEM_ENERGY_BALL", "_comment": "TM070"},
                    "FLAG_UNUSED_0x27F": {"item": "ITEM_TM_EARTH_POWER", "flag": "FLAG_ROUTE12_ITEM_EARTH_POWER", "_comment": "TM086"}},
}
ROUTE13 = {
    "patch_objects": _patch("Route13"),
    "patch_items": {"FLAG_UNUSED_0x280": {"item": "ITEM_TM_ZEN_HEADBUTT", "flag": "FLAG_ROUTE13_ITEM_ZEN_HEADBUTT", "_comment": "TM085"},
                    "FLAG_UNUSED_0x281": {"item": "ITEM_TM_DARK_PULSE", "flag": "FLAG_ROUTE13_ITEM_DARK_PULSE", "_comment": "TM097"}},
}

# ---------------------------------------------------------------------------------------------- Lutin's Hollow (outdoors)
HOLLOW = {
    "patch_objects": {
        # the glade's painters (the six "Lutins" outdoors) only tell the rule of the trial: illusions have no reflection
        "LOCALID_LUTINS_HOLLOW_LUTIN": {"text": T("I'm a pupil. The real LUTIN is in", "the gym, behind moss. Trust water.")},
        "LOCALID_LUTINS_HOLLOW_FLOETTE_SEED": {"text": T("A Floette seed sleeps in my garden.", "It wakes after the great storm.")},
        "LOCALID_LUTINS_HOLLOW_JAYDEN": {"custom": True, "flag": "FLAG_HIDE_HOLLOW_JAYDEN", "move": FACE + "RIGHT"},
        "LOCALID_LUTINS_HOLLOW_WREN": {"custom": True, "flag": "FLAG_HIDE_HOLLOW_WREN", "move": FACE + "LEFT"},
        "LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_1": {"text": T("Look in the pool beside me. See", "that? Nothing. That's the rule.")},
        "LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_2": {"text": T("A real Lutin can't hide from still", "water. We can. That's our trick.")},
        "LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_3": {"text": T("I painted all of these ferns. Don't", "look for my face in the pond.")},
        "LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_4": {"text": T("What the water shows is not the", "water. Remember that.")},
        "LOCALID_LUTINS_HOLLOW_FALSE_LUTIN_5": {"text": T("The real one never lies. The water", "doesn't either.")},
    },
    "patch_signs": {"SignHollow": {"text": "LUTIN'S HOLLOW\nMind the false Lutins."}},
    "patch_items": {"FLAG_UNUSED_0x290": {"item": "ITEM_REVIVE", "_comment": "was the Delphoxite: now the riddler's reward (moss house N)"}},
    "add_objects": [
        # the gym door's only approach cell (25, 7): Lutin's pupil keeps it until the singers by the south pools have been dealt with
        {"id": "LOCALID_LUTINS_HOLLOW_GYM_USHER", "gfx": "OBJ_EVENT_GFX_ARTIST", "x": 25, "y": 7, "move": FACE + "DOWN",
         "text": "", "custom": True, "flag": "FLAG_HIDE_HOLLOW_GYM_USHER"},
    ],
}

# ---------------------------------------------------------------------------------------------- the rooms
ROOMS = {
    "lutins_hollow_gym": {
        "opts": {0: {"custom": True}, 1: {"custom": True}, 2: {"custom": True}, 3: {"custom": True},
                 4: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": "OBJ_EVENT_GFX_LASS"},
                 5: {"custom": True, "sight": 3, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_PSYCHIC_M"},
                 6: {"custom": True}},
        # the three pools below the alcoves (x 4-6, 9-11, 14-16): stand above one (row 8) and press A facing down
        "bg_events": [
            {"type": "sign", "x": 5, "y": 9, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": "LutinsHollow_Gym_EventScript_Pool1"},
            {"type": "sign", "x": 10, "y": 9, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": "LutinsHollow_Gym_EventScript_Pool2"},
            {"type": "sign", "x": 15, "y": 9, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": "LutinsHollow_Gym_EventScript_Pool3"},
        ],
    },
    "lutins_hollow_pokecenter": {"texts": {1: T("The moss moves when nobody is", "looking. I counted. Twice.")}},
    "lutins_hollow_herbalist": {"opts": {0: {"custom": True}}, "texts": {1: T("The Floette seed is for later. It", "wakes after the great storm.")}},
    "lutins_hollow_moss_house_n": {"opts": {0: {"custom": True}}},
    "lutins_hollow_moss_house_s": {"texts": {0: T("Heard singing by the south pools", "last night. A girl, and a boy.")}},
}

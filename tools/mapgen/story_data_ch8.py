"""Chapter 8 data for story_overlay.py: Routes 18-22, Land's End (outdoors and rooms), the Old Water song house. Trainers are a table
(TRAINERS + EXTRA_PARTIES) for gen_route_trainers.py (python tools/mapgen/gen_route_trainers.py ch8).

Story: 35 reached Land's End (arrival frame script, from 34), 36 Heron beaten (badge 8, the final verse, TM Scald, Gyaradosite, Diving Gear),
37 Andrew named and Jayden battle 5 (his first Mega), 38 Rayquaza wakes (the dust storms lift), 39 the full telling at the Old Water.
"""
from story_data_ch3 import T, FACE

SW = "OBJ_EVENT_GFX_SWIMMER_M"
SWF = "OBJ_EVENT_GFX_SWIMMER_F"
SAILOR = "OBJ_EVENT_GFX_SAILOR"

TRAINERS = [
    # ---- Route 18 (the delta below the fallen span, 47-48). The gate triggers (x 38) are never in a trainer's line of sight.
    dict(m="Route18", n=1, const="TRAINER_ORLEANS_ROUTE18_SWIMMER", name="LAZARE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Tentacruel", 47), ("Floatzel", 47), ("Wailord", 48)],
         intro=T("The span fell and the delta opened.", "I swim where it used to be!"), defeat=T("Swept under."),
         after=T("The black arches are warm in the", "afternoon. Old fire, still there.")),
    dict(m="Route18", n=2, const="TRAINER_ORLEANS_ROUTE18_SWIMMER_F", name="PHILOMENE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Jellicent", 47), ("Masquerain", 47), ("Dragalge", 48)],
         intro=T("Cayenne's verse took the span", "down. Now the water's mine!"), defeat=T("Washed out."),
         after=T("East of here the delta fans out.", "Take your time. It's wide.")),
    dict(m="Route18", n=3, const="TRAINER_ORLEANS_ROUTE18_SWIMMER_2", name="ISIDORE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="RIGHT", sight=4, team=[("Sharpedo", 47), ("Drednaw", 48), ("Cloyster", 48)],
         intro=T("Fresh water meets salt out here.", "It makes everyone nervous."), defeat=T("Nerves."),
         after=T("The current flips at noon.", "Don't fight it.")),
    dict(m="Route18", n=7, const="TRAINER_ORLEANS_ROUTE18_SWIMMER_3", name="CLEMENCE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="UP", sight=4, team=[("Araquanid", 47), ("Golduck", 48), ("Gyarados", 48)],
         intro=T("I race the ferries to Land's", "End. Win or lose, I'm early."), defeat=T("Beaten to the dock."),
         after=T("Land's End sits on pilings. The", "whole town floats a little.")),
    # ---- Route 19 (the tidal flats, 48-49)
    dict(m="Route19", n=1, const="TRAINER_ORLEANS_ROUTE19_SAILOR", name="THEODULE", cls="Sailor", pic="Sailor", sex="Male", music="Male",
         gfx=SAILOR, face="DOWN", sight=4, team=[("Pelipper", 48), ("Crawdaunt-Orleanian", 48), ("Quagsire", 49)],
         intro=T("Low tide! The flats are mine", "until it turns back."), defeat=T("Tide's turned."),
         after=T("A fossil hunter dug up the east", "flat last spring. Might be more.")),
    dict(m="Route19", n=2, const="TRAINER_ORLEANS_ROUTE19_FISHERMAN", name="OSMOND", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_FISHERMAN", face="RIGHT", sight=4, team=[("Whiscash", 48), ("Barbaracle", 48), ("Gyarados", 49)],
         intro=T("The flats drain, the fish gather.", "I gather the fish. And fights!"), defeat=T("Off the hook."),
         after=T("Mud holds secrets. Mostly mud.", "But sometimes a fossil.")),
    dict(m="Route19", n=3, const="TRAINER_ORLEANS_ROUTE19_BIRD_KEEPER", name="FABRICE", cls="Bird Keeper", pic="Bird Keeper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BOY_2", face="DOWN", sight=4, team=[("Kilowattrel", 48), ("Corviknight", 49), ("Pelipper", 49)],
         intro=T("Shorebirds follow the tide. So", "do I. Battle?"), defeat=T("Blown away."),
         after=T("The herons on Route 20 nest in", "the old pilings. Don't startle them.")),
    dict(m="Route19", n=4, const="TRAINER_ORLEANS_ROUTE19_RANGER", name="DELPHINE", cls="Pkmn Ranger", pic="Pokemon Ranger F", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_BEAUTY", face="LEFT", sight=4, team=[("Kabutops", 49), ("Dhelmise", 49), ("Floatzel", 49)],
         intro=T("I ranger the delta. Nobody", "crosses without a fight!"), defeat=T("Crossed."),
         after=T("Kabutops are older than the", "town. They keep to the flats.")),
    # ---- Route 20 (the heron islets, 49-50)
    dict(m="Route20", n=2, const="TRAINER_ORLEANS_ROUTE20_SWIMMER", name="HONORE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Sharpedo", 49), ("Jellicent", 49), ("Tentacruel", 50)],
         intro=T("The herons watch from the pilings.", "They judge swimmers."), defeat=T("Judged."),
         after=T("Land's End is two islets east.", "Follow the herons.")),
    dict(m="Route20", n=3, const="TRAINER_ORLEANS_ROUTE20_SWIMMER_F", name="ROSALIE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Milotic", 49), ("Masquerain", 50), ("Cramorant", 50)],
         intro=T("Rain's coming. I can smell it.", "Heron's rain, they call it."), defeat=T("Drenched."),
         after=T("HERON keeps the rain. She lets", "it fall when it's ready.")),
    dict(m="Route20", n=4, const="TRAINER_ORLEANS_ROUTE20_SAILOR", name="GERMAIN", cls="Sailor", pic="Sailor", sex="Male", music="Male",
         gfx=SAILOR, face="LEFT", sight=4, team=[("Wailord", 49), ("Pelipper", 50), ("Barbaracle", 50)],
         intro=T("Last islet before Land's End.", "Toll's a battle!"), defeat=T("Toll paid."),
         after=T("The pilings go on for miles.", "Nobody remembers who built them.")),
    dict(m="Route20", n=5, const="TRAINER_ORLEANS_ROUTE20_SWIMMER_2", name="ANATOLE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="LEFT", sight=4, team=[("Gyarados", 49), ("Quagsire", 50), ("Politoed", 50)],
         intro=T("Almost there! Don't dawdle,", "the tide's turning."), defeat=T("Out of breath."),
         after=T("Land's End's gym is a pavilion", "on pilings. Wear a raincoat.")),
    # ---- Route 21 (into the Gulf, 50-51): its barge opens with badge 8
    dict(m="Route21", n=0, const="TRAINER_ORLEANS_ROUTE21_SWIMMER", name="ALEXIS", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="LEFT", sight=4, team=[("Wailord", 50), ("Sharpedo", 50), ("Dragalge", 51)],
         intro=T("The barge is gone, the Gulf is", "open. Out here it's deep."), defeat=T("Too deep."),
         after=T("The rain stopped the day the", "last verse was sung.")),
    dict(m="Route21", n=4, const="TRAINER_ORLEANS_ROUTE21_SWIMMER_F", name="CAMILLA", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Jellicent", 50), ("Milotic", 50), ("Tentacruel", 51)],
         intro=T("Out past the delta the swells", "get long. Fight on them!"), defeat=T("Swamped."),
         after=T("The Gulf glows at night, down", "south. Don't look too long.")),
    dict(m="Route21", n=5, const="TRAINER_ORLEANS_ROUTE21_SWIMMER_2", name="BAPTISTINE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Araquanid", 50), ("Cloyster", 51), ("Gyarados", 51)],
         intro=T("Everyone wants the temple.", "Few can reach it."), defeat=T("Not today."),
         after=T("The temple door is on ROUTE 22.", "Face it from the water.")),
    dict(m="Route21", n=6, const="TRAINER_ORLEANS_ROUTE21_SWIMMER_3", name="MAXENCE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="UP", sight=4, team=[("Kingler-Orleanian", 50), ("Barbaracle", 51), ("Seismitoad", 51)],
         intro=T("Another traveler. The Gulf is", "busy this year."), defeat=T("Crabbed."),
         after=T("Route 22 is the last water", "before the temple.")),
    # ---- Route 22 (the open Gulf, 51-52)
    dict(m="Route22", n=0, const="TRAINER_ORLEANS_ROUTE22_SWIMMER", name="AUGUSTIN", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Gyarados", 51), ("Wailord", 51), ("Jellicent", 52)],
         intro=T("Open water, nothing but the", "horizon. And me!"), defeat=T("Horizon wins."),
         after=T("The temple door has a hollow", "shaped like a song. I heard it.")),
    dict(m="Route22", n=1, const="TRAINER_ORLEANS_ROUTE22_SWIMMER_F", name="LEONTINE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Milotic", 51), ("Tentacruel", 52), ("Dragalge", 52)],
         intro=T("The lights down there are the", "temple's. Beautiful. Wrong."), defeat=T("Lights out."),
         after=T("Kyogre sleeps below. Everybody", "knows. Nobody says it.")),
    dict(m="Route22", n=2, const="TRAINER_ORLEANS_ROUTE22_SWIMMER_2", name="CASIMIR", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Sharpedo", 52), ("Seismitoad", 52), ("Archaludon", 52)],
         intro=T("This is as far as the sea lets", "you go. For now."), defeat=T("Beached."),
         after=T("The water lets the singers through.", "It's letting you.")),
]

EXTRA_PARTIES = [
    # the gym's two trainers
    dict(const="TRAINER_ORLEANS_LANDS_END_GYM_SWIMMER", name="ISOLDE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         team=[("Jellicent", 51), ("Dragalge", 51), ("Cloyster", 52)]),
    dict(const="TRAINER_ORLEANS_LANDS_END_GYM_FISHERMAN", name="GASPARD", cls="Fisherman", pic="Fisherman", sex="Male", music="Hiker",
         team=[("Whiscash", 51), ("Barbaracle", 51), ("Kingler-Orleanian", 52)]),
    # Heron (gym 8, Rain): Drizzle on Pelipper and Politoed, the Gyarados holds Gyaradosite
    dict(const="TRAINER_HERON", name="HERON", cls="Leader", pic="Leader Juan", sex="Female", music="Female",
         team=[("Pelipper", 50, ["Hurricane", "Scald", "Roost", "Protect"], {"ability": "Drizzle"}),
               ("Politoed", 50, ["Hydro Pump", "Ice Beam", "Earth Power", "Perish Song"], {"ability": "Drizzle"}),
               ("Archaludon", 51, ["Flash Cannon", "Draco Meteor", "Electro Shot", "Body Press"]),
               ("Floatzel", 51, ["Wave Crash", "Ice Fang", "Aqua Jet", "Crunch"]),
               ("Seismitoad", 52, ["Hydro Pump", "Earth Power", "Sludge Wave", "Toxic"]),
               ("Gyarados", 53, ["Waterfall", "Dragon Dance", "Crunch", "Ice Fang"], {"item": "Gyaradosite"})],
         ai="Check Bad Move / Try To Faint", iv=30),
    # Jayden battle 5 (Land's End): his first Mega Evolution (the starter's final stage, one variant per starter like battles 2-4)
    dict(const="TRAINER_ORLEANS_JAYDEN_LANDS_END_CHIKORITA", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 50), ("Arbok", 51), ("Meganium", 53, [], {"item": "Meganiumite"})], iv=28, ai="Check Bad Move / Try To Faint"),
    dict(const="TRAINER_ORLEANS_JAYDEN_LANDS_END_FUECOCO", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 50), ("Arbok", 51), ("Skeledirge", 53, [], {"item": "Skeledirgite"})], iv=28, ai="Check Bad Move / Try To Faint"),
    dict(const="TRAINER_ORLEANS_JAYDEN_LANDS_END_TOTODILE", name="JAYDEN", cls="Rival", pic="Brendan", sex="Male", music="Male",
         team=[("Crobat", 50), ("Arbok", 51), ("Feraligatr", 53, [], {"item": "Feraligite"})], iv=28, ai="Check Bad Move / Try To Faint"),
]


# ---------------------------------------------------------------------------------------------- Routes 18-22 overlay
def _patch(m):
    out = {}
    for t in TRAINERS:
        if t["m"] == m:
            out[f"LOCALID_ORLEANS_{m.upper()}_TRAINER_{t['n']}"] = {"gfx": t["gfx"], "move": FACE + t["face"], "sight": t["sight"], "custom": True}
    return out


ROUTE18 = {
    "patch_objects": _patch("Route18"),
    "add_items": [{"x": 28, "y": 15, "item": "ITEM_TM_UPROAR", "flag": "FLAG_ROUTE18_ITEM_UPROAR", "_comment": "TM062 (Routes 7-12 band, left over): the islet"}],
}
ROUTE19 = {
    "patch_objects": _patch("Route19"),
    # the tidal flats' dig spot (8.1): a fossil for Lafayette's revival (the Kabuto line)
    "add_hidden": [{"x": 36, "y": 19, "item": "ITEM_DOME_FOSSIL", "flag": "FLAG_ROUTE19_HIDDEN_DOME_FOSSIL", "_note": "fossil dig spot (obtainability.md): Kabuto"}],
}
ROUTE20 = {"patch_objects": _patch("Route20")}
ROUTE21 = {"patch_objects": _patch("Route21")}
ROUTE22 = {"patch_objects": _patch("Route22")}

# ---------------------------------------------------------------------------------------------- Land's End (outdoors)
LANDS_END = {
    "patch_objects": {
        # Andrew and Jayden arrive after the gym (story 36): they stand in front of the pavilion door, hidden until then
        "LOCALID_LANDS_END_ANDREW": {"custom": True, "x": 26, "y": 36, "move": FACE + "RIGHT", "flag": "FLAG_HIDE_LANDS_END_ANDREW"},
        "LOCALID_LANDS_END_JAYDEN": {"custom": True, "x": 28, "y": 36, "move": FACE + "LEFT", "flag": "FLAG_HIDE_LANDS_END_JAYDEN"},
        "LOCALID_LANDS_END_HERON": {"text": T("HERON keeps the rain pavilion. She", "says the rain only listens to order.")},
        "LOCALID_LANDS_END_FISHERMAN": {"text": T("The flats on Route 19 drain at dawn.", "Fossils turn up in the mud.")},
        "LOCALID_LANDS_END_BOATMAN_W": {"text": T("West of here, the delta road to the", "mill. The span fell. Good riddance.")},
        "LOCALID_LANDS_END_BOATMAN_S": {"text": T("South, past Route 21, the Gulf. The", "barge sat there for years.")},
        "LOCALID_LANDS_END_KID": {"text": T("My dad says the pavilion's rain is a", "puzzle. I just get wet.")},
        "LOCALID_LANDS_END_SHRIMPER": {"text": T("Shrimp run in the rain. I love", "Heron's pavilion. Business!")},
    },
}

# ---------------------------------------------------------------------------------------------- the rooms
PANELS = {  # panel -> (sign cells, verse number it carries): the true order is verse 1 .. 7 (shuffled across the pavilion)
    "A": ([(2, 7), (3, 7)], 4), "B": ([(5, 7), (6, 7)], 1), "C": ([(8, 7), (9, 7)], 6), "D": ([(11, 7), (12, 7)], 2),
    "E": ([(14, 7), (15, 7)], 7), "F": ([(17, 7), (18, 7)], 3), "G": ([(9, 10), (10, 10), (11, 10)], 5),
}


def _panel_events():
    ev = []
    for k, (cells, _v) in PANELS.items():
        for n, (x, y) in enumerate(cells, 1):
            ev.append({"type": "sign", "x": x, "y": y, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
                       "script": f"LandsEnd_Gym_EventScript_Panel{k}{n}"})
    return ev


ROOMS = {
    "lands_end_gym": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_OLD_WOMAN", "face": "DOWN"},
                 1: {"custom": True, "sight": 3, "face": "RIGHT", "gfx": SWF},
                 2: {"custom": True, "sight": 3, "face": "LEFT", "gfx": "OBJ_EVENT_GFX_FISHERMAN"},
                 3: {"custom": True}},
        "bg_events": _panel_events(),
    },
    "lands_end_pokecenter": {"texts": {1: T("The Gulf's been strange since the", "temple lights came on.")}},
    "lands_end_house_3": {"texts": {0: T("A man in a black coat asked about", "the Rain Pavilion. Then he left.")}},
}

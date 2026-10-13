"""Chapter 9 (the finale) data for story_overlay.py: Routes 23-25, the two raid arenas (the Drowned Temple's Tide Hall and the Salt Cathedral), the Old
Water ceremony actors, the Oldest Shrine's last stand and the Rayquaza raid. Trainers are a table (TRAINERS + EXTRA_PARTIES + PARTNERS) for
gen_route_trainers.py (python tools/mapgen/gen_route_trainers.py ch9).

Story: 39 the telling (Chapter 8). 40 both raids done (FLAG_KYOGRE_CALMED, FLAG_GROUDON_CALMED, either order; FLAG_ROUTE25_OPEN with the second),
41 the dusk orb ceremony at the Old Water (the player takes Kyogre or Groudon, Jayden the other: VAR_ORLEANS_LEGENDARY_PICK 1 or 2),
42 Camille and Andrew beaten on the Oldest Shrine's landing steps, 43 the Rayquaza raid won (2 v 1 with Jayden), 44 the epilogue (the credits),
45 the post-game (the Battle Frontier is open).
"""
from story_data_ch3 import T, FACE

SW = "OBJ_EVENT_GFX_SWIMMER_M"
SWF = "OBJ_EVENT_GFX_SWIMMER_F"

TRAINERS = [
    # ---- Route 23 (the dust plains, 54-55)
    dict(m="Route23", n=3, const="TRAINER_ORLEANS_ROUTE23_HIKER", name="ELZEAR", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="DOWN", sight=4, team=[("Gigalith", 54), ("Coalossal", 54), ("Excadrill", 55)],
         intro=T("The dust's gone, finally. The", "plains are mine again."), defeat=T("Dust to dust."),
         after=T("The salt mine's north-east. Don't", "go in without a light.")),
    dict(m="Route23", n=5, const="TRAINER_ORLEANS_ROUTE23_RUIN_MANIAC", name="NARCISSE", cls="Ruin Maniac", pic="Ruin Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_MANIAC", face="LEFT", sight=4, team=[("Gholdengo", 54), ("Magnezone", 55), ("Gigalith", 54)],
         intro=T("The storm uncovered an old wall.", "I'm guarding it. Fight me!"), defeat=T("Buried."),
         after=T("The wall sings when the wind", "hits it. Like a flute.")),
    dict(m="Route23", n=6, const="TRAINER_ORLEANS_ROUTE23_PICNICKER", name="ODILE", cls="Picnicker", pic="Picnicker", sex="Female", music="Female",
         gfx="OBJ_EVENT_GFX_PICNICKER", face="RIGHT", sight=4, team=[("Sylveon", 54), ("Ribombee", 54), ("Mimikyu", 55)],
         intro=T("Grass grows back through dust.", "I came to watch it."), defeat=T("Pressed flat."),
         after=T("A shadow crossed the whole sky.", "I felt it in my teeth.")),
    dict(m="Route23", n=7, const="TRAINER_ORLEANS_ROUTE23_BLACK_BELT", name="RIGOBERT", cls="Black Belt", pic="Black Belt", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_BLACK_BELT", face="DOWN", sight=4, team=[("Crabominable", 54), ("Poliwrath", 55), ("Toxicroak", 55)],
         intro=T("The storm's lifted. My training", "can resume. Spar with me!"), defeat=T("Sparred out."),
         after=T("Cleaner air makes better", "training.")),
    # ---- Route 24 (the salt flats, 56-57)
    dict(m="Route24", n=1, const="TRAINER_ORLEANS_ROUTE24_HIKER", name="PLACIDE", cls="Hiker", pic="Hiker", sex="Male", music="Hiker",
         gfx="OBJ_EVENT_GFX_HIKER", face="DOWN", sight=4, team=[("Coalossal", 56), ("Gigalith", 56), ("Mamoswine", 57)],
         intro=T("Salt gets into everything. Even", "my boots. Even my battles."), defeat=T("Salted."),
         after=T("The old mine goes deep. The", "ground cracked last month.")),
    dict(m="Route24", n=2, const="TRAINER_ORLEANS_ROUTE24_CAMPER", name="ARSENE", cls="Camper", pic="Camper", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_CAMPER", face="RIGHT", sight=4, team=[("Excadrill", 56), ("Krookodile", 56), ("Flygon", 57)],
         intro=T("I camp on the flats. Nothing", "grows here but my nerve."), defeat=T("Nerve lost."),
         after=T("A shaft opened in the rock. It", "breathes heat. Don't stand near.")),
    dict(m="Route24", n=3, const="TRAINER_ORLEANS_ROUTE24_EXPERT", name="CYRILLE", cls="Expert", pic="Expert M", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_EXPERT_M", face="DOWN", sight=4, team=[("Gengar", 56), ("Magnezone", 56), ("Delphox", 57)],
         intro=T("I study the heat under the", "flats. And trainers."), defeat=T("Data gathered."),
         after=T("Something enormous sleeps down", "there. The readings say so.")),
    dict(m="Route24", n=4, const="TRAINER_ORLEANS_ROUTE24_RUIN_MANIAC", name="THADEE", cls="Ruin Maniac", pic="Ruin Maniac", sex="Male", music="Male",
         gfx="OBJ_EVENT_GFX_MANIAC", face="DOWN", sight=4, team=[("Metagross", 56), ("Gholdengo", 56), ("Dragapult", 57)],
         intro=T("These tunnels are older than", "the town. Don't touch the walls."), defeat=T("Walled in."),
         after=T("The oldest wall has carvings.", "Rootkin hands. A verse, maybe.")),
    # ---- Route 25 (the channel to the Oldest Shrine, 57-59); open only once both raids are done
    dict(m="Route25", n=1, const="TRAINER_ORLEANS_ROUTE25_SWIMMER", name="EUSTACHE", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Gyarados", 57), ("Kingler-Orleanian", 57), ("Wailord", 58)],
         intro=T("The storm wall's gone. The", "channel is mine to cross first!"), defeat=T("Second again."),
         after=T("The shrine sits on an island of", "singing stone. You'll hear it.")),
    dict(m="Route25", n=2, const="TRAINER_ORLEANS_ROUTE25_SWIMMER_F", name="GENEVIEVE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Milotic", 57), ("Jellicent", 57), ("Dragalge", 58)],
         intro=T("The water's calm now. Both", "sleepers are at rest."), defeat=T("Calm as ever."),
         after=T("Black boats passed here at", "night. They didn't light a lamp.")),
    dict(m="Route25", n=4, const="TRAINER_ORLEANS_ROUTE25_SWIMMER_2", name="SYLVAIN", cls="Swimmer M", pic="Swimmer M", sex="Male", music="Swimmer",
         gfx=SW, face="DOWN", sight=4, team=[("Sharpedo", 58), ("Tentacruel", 58), ("Archaludon", 59)],
         intro=T("Nobody swims past me to the", "shrine. Not today."), defeat=T("Let through."),
         after=T("Mind the third current. It", "turns toward the stone.")),
    dict(m="Route25", n=6, const="TRAINER_ORLEANS_ROUTE25_SWIMMER_F2", name="HORTENSE", cls="Swimmer F", pic="Swimmer F", sex="Female", music="Swimmer",
         gfx=SWF, face="DOWN", sight=4, team=[("Politoed", 58), ("Seismitoad", 58), ("Gyarados", 59)],
         intro=T("Last stretch before the stone.", "I won't make it easy."), defeat=T("Easy after all."),
         after=T("Sing when you land. The stone", "listens.")),
]

EXTRA_PARTIES = [
    # the raids: one legendary each, the primal weather comes from its orb at switch-in (Primordial Sea / Desolate Land)
    dict(const="TRAINER_ORLEANS_KYOGRE_RAID", name="KYOGRE", cls="Pkmn Trainer 1", pic="Brendan", sex="Male", music="Male",
         team=[("Kyogre", 60, ["Origin Pulse", "Ice Beam", "Thunder", "Calm Mind"], {"item": "Blue Orb"})],
         ai="Check Bad Move / Try To Faint", iv=31),
    dict(const="TRAINER_ORLEANS_GROUDON_RAID", name="GROUDON", cls="Pkmn Trainer 1", pic="Brendan", sex="Male", music="Male",
         team=[("Groudon", 60, ["Precipice Blades", "Fire Punch", "Rock Slide", "Swords Dance"], {"item": "Red Orb"})],
         ai="Check Bad Move / Try To Faint", iv=31),
    # the Oldest Shrine's landing steps: Camille (Mega Weezing), then Andrew (Mega Metagross)
    dict(const="TRAINER_ORLEANS_CAMILLE_SHRINE", name="CAMILLE", cls="Aqua Admin", pic="Aqua Admin F", sex="Female", music="Aqua",
         team=[("Crobat", 56), ("Malamar", 56), ("Sharpedo", 57), ("Gengar", 57), ("Weezing-Orleanian", 58, [], {"item": "Weezingite"})],
         ai="Check Bad Move / Try To Faint", iv=28),
    dict(const="TRAINER_ORLEANS_ANDREW", name="ANDREW", cls="Aqua Leader", pic="Aqua Leader Archie", sex="Male", music="Aqua",
         team=[("Corviknight", 57), ("Gholdengo", 57), ("Excadrill", 58), ("Dragalge", 58), ("Magnezone", 58),
               ("Metagross", 60, [], {"item": "Metagrossite"})],
         ai="Check Bad Move / Try To Faint", iv=30),
    # the Rayquaza raid: one Mega Rayquaza (Dragon Ascent) against the player and Jayden (2 v 1); Delta Stream overrides both primal weathers
    dict(const="TRAINER_ORLEANS_RAYQUAZA_RAID", name="RAYQUAZA", cls="Pkmn Trainer 1", pic="Brendan", sex="Male", music="Male",
         team=[("Rayquaza", 66, ["Dragon Ascent", "Extreme Speed", "Earthquake", "Dragon Dance"])],
         ai="Check Bad Move / Try To Faint", iv=31),
]

# Jayden's partner parties for the Rayquaza raid (battle_partners.party): the starter in Mega form, the legendary the player did NOT take, Arbok
PARTNERS = []
for _starter, _final, _stone in (("CHIKORITA", "Meganium", "Meganiumite"), ("FUECOCO", "Skeledirge", "Skeledirgite"), ("TOTODILE", "Feraligatr", "Feraligite")):
    for _leg, _orb in (("KYOGRE", "Blue Orb"), ("GROUDON", "Red Orb")):
        PARTNERS.append((f"PARTNER_JAYDEN_{_starter}_{_leg}",
                         [(_final, 56, _stone), (_leg.capitalize(), 58, _orb), ("Arbok", 56, None)]))


# ---------------------------------------------------------------------------------------------- Routes 23-25 overlay
def _patch(m):
    out = {}
    for t in TRAINERS:
        if t["m"] == m:
            out[f"LOCALID_ORLEANS_{m.upper()}_TRAINER_{t['n']}"] = {"gfx": t["gfx"], "move": FACE + t["face"], "sight": t["sight"], "custom": True}
    return out


ROUTE23 = {"patch_objects": _patch("Route23")}
ROUTE24 = {
    "patch_objects": _patch("Route24"),
    # the cracked shaft in the rock wall (the way down to the Salt Cathedral): press A facing it from (39, 7); the Lantern lights the way
    # (fix B: the trigger sits on the visible dome door, the sign beside it)
    "signs": [{"id": "SaltShaft", "x": 39, "y": 6, "text": "", "custom": True}],
}
ROUTE25 = {"patch_objects": _patch("Route25")}
ROUTE22 = {
    # the dive spot: Surf up to the ruin door and face it from the water cell (5, 24); the trigger is the door's water cell (5, 23), elevation 1
    # (a surfer's elevation). The Route 22 sign (2, 23) is elevation 0 (any) so it reads from the water too (fix B, ch8_2 S3)
    "signs": [{"id": "DiveSpot", "x": 5, "y": 23, "elevation": 1, "text": "", "custom": True}],
}

# ---------------------------------------------------------------------------------------------- the Oldest Shrine (outdoors)
OLDEST_SHRINE = {
    "patch_objects": {
        # the shrine keeper: the Swampertite waits with her when the bag was full (story >= 43)
        "LOCALID_OLDEST_SHRINE_NPC_0": {"custom": True},
        "LOCALID_OLDEST_SHRINE_NPC_1": {"text": T("They say the shrine is older than", "the telling. Older than the water.")},
    },
    "add_objects": [
        # Camille and Andrew hold the landing steps while the story is 41; Rayquaza and Jayden stand at the stone from story 42
        {"id": "LOCALID_OLDEST_SHRINE_CAMILLE", "gfx": "OBJ_EVENT_GFX_AQUA_MEMBER_F", "x": 17, "y": 18, "move": FACE + "DOWN", "text": "",
         "custom": True, "flag": "FLAG_HIDE_SHRINE_CAMILLE"},
        {"id": "LOCALID_OLDEST_SHRINE_ANDREW", "gfx": "OBJ_EVENT_GFX_MAN_2", "x": 18, "y": 16, "move": FACE + "DOWN", "text": "",
         "custom": True, "flag": "FLAG_HIDE_SHRINE_ANDREW"},
        {"id": "LOCALID_OLDEST_SHRINE_RAYQUAZA", "gfx": "OBJ_EVENT_GFX_SPECIES(RAYQUAZA)", "x": 18, "y": 8, "move": FACE + "DOWN", "text": "",
         "custom": True, "flag": "FLAG_HIDE_SHRINE_RAYQUAZA"},
        {"id": "LOCALID_OLDEST_SHRINE_JAYDEN", "gfx": "OBJ_EVENT_GFX_BOY_2", "x": 16, "y": 14, "move": FACE + "RIGHT", "text": "",
         "custom": True, "flag": "FLAG_HIDE_SHRINE_JAYDEN"},
    ],
}

# ---------------------------------------------------------------------------------------------- the Old Water (ceremony actors)
OLD_WATER = {
    "add_objects": [
        {"id": "LOCALID_OLD_WATER_CER_KYOGRE", "gfx": "OBJ_EVENT_GFX_KYOGRE_FRONT", "x": 22, "y": 29, "move": FACE + "DOWN", "text": "", "custom": True,
         "flag": "FLAG_HIDE_CER_KYOGRE"},
        {"id": "LOCALID_OLD_WATER_CER_GROUDON", "gfx": "OBJ_EVENT_GFX_GROUDON_FRONT", "x": 26, "y": 29, "move": FACE + "DOWN", "text": "", "custom": True,
         "flag": "FLAG_HIDE_CER_GROUDON"},
        {"id": "LOCALID_OLD_WATER_CER_TUPELO", "gfx": "OBJ_EVENT_GFX_OLD_MAN", "x": 24, "y": 29, "move": FACE + "DOWN", "text": "", "custom": True,
         "flag": "FLAG_HIDE_CER_TUPELO"},
        {"id": "LOCALID_OLD_WATER_CER_JAYDEN", "gfx": "OBJ_EVENT_GFX_BOY_2", "x": 22, "y": 31, "move": FACE + "DOWN", "text": "", "custom": True,
         "flag": "FLAG_HIDE_CER_JAYDEN"},
        {"id": "LOCALID_OLD_WATER_CER_WREN", "gfx": "OBJ_EVENT_GFX_GIRL_3", "x": 21, "y": 32, "move": FACE + "UP", "text": "", "custom": True,
         "flag": "FLAG_HIDE_CER_WREN"},
    ],
}

# ---------------------------------------------------------------------------------------------- the rooms (scripted warps in and out)
ROOMS = {
    "lands_end_drowned_temple": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "face": "DOWN", "flag": "FLAG_TEMPLE_DOOR_OPEN"},
                 1: {"custom": True, "gfx": "OBJ_EVENT_GFX_KYOGRE_FRONT", "face": "DOWN", "flag": "FLAG_HIDE_KYOGRE_RAID"}},
        # the exit mat (8, 14) leaves by script (to the end of Route 22), the coord event runs before the warp
        "coord_events": [{"type": "trigger", "x": 8, "y": 14, "elevation": 0, "var": "FLAG_FINALE_NEVER_SET", "var_value": "0", "script": "LandsEnd_DrownedTemple_EventScript_Exit"}],
    },
    "lands_end_salt_cathedral": {
        "opts": {0: {"custom": True, "gfx": "OBJ_EVENT_GFX_GROUDON_FRONT", "face": "DOWN", "flag": "FLAG_HIDE_GROUDON_RAID"}},
        "coord_events": [{"type": "trigger", "x": 10, "y": 16, "elevation": 0, "var": "FLAG_FINALE_NEVER_SET", "var_value": "0", "script": "LandsEnd_SaltCathedral_EventScript_Exit"}],
    },
}

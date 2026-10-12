"""The 36 custom abilities from the dex sheet's Notes tab: constant name -> (display name, description <= 29 chars, aiRating).

Behaviour is implemented in src/battle_util.c etc. (see dex_progress.log.md for which ones); every ability here is
defined (name + description) so species data can reference it.
"""
NEW_ABILITIES = [
    # (CONST, display name, description, aiRating)
    ("BLUR", "Blur", "Technician; immune to Rock.", 7),
    ("BOILING_POINT", "Boiling Point", "Water moves are also Fire.", 7),
    ("BOTTOM_FEEDER", "Bottom Feeder", "Ups Attack if hit by Grass.", 5),
    ("BUOYANCY", "Buoyancy", "Levitates; holds its ground.", 7),
    ("BURNING_SEASON", "Burning Season", "Casts sun; Grass moves surge.", 9),
    ("CLINGING_MOSS", "Clinging Moss", "Leech Seeds foes on contact.", 5),
    ("COTTONMOUTH", "Cottonmouth", "Intimidate; contact poisons.", 8),
    ("CROC_AND_ROLL", "Croc and Roll", "Punk Rock plus Unaware.", 8),
    ("CYPRESS_KNEES", "Cypress Knees", "Water heals; holds position.", 7),
    ("DEAD_ZONE", "Dead Zone", "Foes can't restore HP.", 7),
    ("DEATH_ROLL", "Death Roll", "Bites trap; Strong Jaw.", 8),
    ("FIELD_BURNER", "Field Burner", "Grass moves surge in sun.", 6),
    ("FIREDAMP", "Firedamp", "Levitate; burns the poisoned.", 7),
    ("FISH_HAWK", "Fish Hawk", "Ups damage to Water-types.", 5),
    ("FLEUR_DE_LIS", "Fleur-de-Lis", "Ups Grass/Fairy; stats safe.", 8),
    ("GRAVEYARD_MOSS", "Graveyard Moss", "Seeds foes; heals when out.", 8),
    ("HEARTWOOD", "Heartwood", "Stamina plus Cypress Knees.", 8),
    ("IRIS_BLOOM", "Iris Bloom", "Sp.Atk up in rain or Grassy.", 6),
    ("LIVE_WIRE", "Live Wire", "Adds Electric; Levitates.", 8),
    ("LOST_LIGHT", "Lost Light", "Burns on hit; hurts burned.", 8),
    ("LURE_LIGHT", "Lure Light", "Burned foes can't escape.", 6),
    ("NIGHT_GLOW", "Night Glow", "Stronger and faster at night.", 6),
    ("PENDULUM", "Pendulum", "Sleep moves: sure hit, +1.", 7),
    ("PEELER", "Peeler", "Molts when hit: Atk, Spe up.", 6),
    ("PLUNGE_DIVE", "Plunge Dive", "Turn 1: +1 priority, crits.", 7),
    ("REGAL_COIL", "Regal Coil", "Contrary and Queenly Majesty.", 8),
    ("ROLLING_BOIL", "Rolling Boil", "Water moves may burn foes.", 6),
    ("ROUGAROU", "Rougarou", "No Guard and Infiltrator.", 9),
    ("SECOND_LINE", "Second Line", "Boosts dances; copies dances.", 8),
    ("SKY_SCORCHER", "Sky Scorcher", "Levitate plus Drought.", 9),
    ("SOFT_SHELL", "Soft Shell", "Molts once below half HP.", 5),
    ("STORM_BEACON", "Storm Beacon", "Sets rain & Electric Terrain.", 9),
    ("SWAMP_GAS", "Swamp Gas", "Levitate; may poison or burn.", 7),
    ("TIMBER", "Timber", "Sharpness; ignores Sturdy.", 8),
    ("WEB_WEAVER", "Web Weaver", "Sets Sticky Web on entry.", 7),
    ("ZYDECO", "Zydeco", "Sound boost; hits Ghosts.", 7),
]

"""Hand-written overrides: HAND[(species, tier, variant)] / HAND[(species, tier)] / HAND[species] = dict(role=, moves=[], item=, nature=, ability=, ev=(hp, atk, def, spe, spa, spd)).

Only what the generator cannot reason about is here: Ditto (Transform), and Shedinja (1 HP: no recoil, no Focus Sash, every move must be Wonder-Guard-safe attacks).
"""

HAND = {
    "SPECIES_DITTO": dict(moves=["MOVE_TRANSFORM", "MOVE_NONE", "MOVE_NONE", "MOVE_NONE"], ability="ABILITY_IMPOSTER", nature="NATURE_JOLLY", ev=(252, 0, 4, 252, 0, 0)),
    ("SPECIES_SHEDINJA", "T1", 1): dict(moves=["MOVE_SHADOW_SNEAK", "MOVE_X_SCISSOR", "MOVE_SHADOW_CLAW", "MOVE_SLASH"], item="ITEM_LUM_BERRY", ability="ABILITY_WONDER_GUARD", nature="NATURE_ADAMANT", ev=(0, 112, 0, 112, 0, 0)),
    ("SPECIES_SHEDINJA", "A1", 1): dict(moves=["MOVE_SWORDS_DANCE", "MOVE_SHADOW_SNEAK", "MOVE_X_SCISSOR", "MOVE_SHADOW_CLAW"], item="ITEM_PERSIM_BERRY", ability="ABILITY_WONDER_GUARD", nature="NATURE_ADAMANT", ev=(0, 176, 0, 176, 0, 0)),
    ("SPECIES_SHEDINJA", "A2", 2): dict(moves=["MOVE_SWORDS_DANCE", "MOVE_PHANTOM_FORCE", "MOVE_X_SCISSOR", "MOVE_SUCKER_PUNCH"], item="ITEM_LEFTOVERS", ability="ABILITY_WONDER_GUARD", nature="NATURE_JOLLY", ev=(0, 176, 0, 176, 0, 0)),
}

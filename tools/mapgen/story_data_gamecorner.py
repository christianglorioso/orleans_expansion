"""The Crescent City Game Corner (a riverboat-casino hall): its people and machines, merged into INTERIOR by story_overlay.py.

People are all in the overlay (positions match the room shapes in interiors_world.py). The scripts of the clerks, the dealer, the
Derby attendant and the capsule machines are hand-written in story/CrescentCity_GameCorner.inc (the generated NPC block between
the mapgen markers would wipe them), so every one of them is "custom". The machines and the table are bg_events (sign type):
stand below and press A facing up.
"""
from story_data_ch3 import T

SIGN = "BG_EVENT_PLAYER_FACING_NORTH"


def _sign(x, y, script):
    return {"type": "sign", "x": x, "y": y, "elevation": 3, "player_facing_dir": SIGN, "script": script}


GAME_CORNER = {
    "crescent_city_game_corner": {
        "people": [
            ("coin clerk", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_MART_EMPLOYEE"}),
            ("prize clerk", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_MART_EMPLOYEE"}),
            ("dealer", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_GENTLEMAN"}),
            ("derby attendant", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_BARD"}),
            ("gambler", T("The slots are gone, but the capsule", "machines still pay out. Mostly in", "disappointment."), {"gfx": "OBJ_EVENT_GFX_MAN_2"}),
            ("regular", T("The capsule machines hold the first", "partners from the old river towns.", "Grass, fire, water, one per swing.", "The pricier the machine, the rarer."),
             {"gfx": "OBJ_EVENT_GFX_WOMAN_2"}),
        ],
        "positions": [(3, 7), (18, 2), (9, 6), (13, 2), (15, 9), (5, 6)],
        "bg_events": [
            _sign(2, 3, "CrescentCity_GameCorner_EventScript_GachaBasic"),
            _sign(4, 3, "CrescentCity_GameCorner_EventScript_GachaGreat"),
            _sign(6, 3, "CrescentCity_GameCorner_EventScript_GachaUltra"),
            _sign(8, 3, "CrescentCity_GameCorner_EventScript_GachaMaster"),
            _sign(9, 8, "CrescentCity_GameCorner_EventScript_Blackjack"),
            _sign(10, 8, "CrescentCity_GameCorner_EventScript_Blackjack"),
            _sign(13, 3, "CrescentCity_GameCorner_EventScript_Derby"),
            _sign(14, 3, "CrescentCity_GameCorner_EventScript_Derby"),
        ],
    },
}

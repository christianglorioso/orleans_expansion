"""Story overlay: the story pass's changes to the generated maps, kept apart from the generators so a rebuild never wipes them.

The generators (firstpass.py for routes, storms_edge.py / crescent.py / ... for towns, interior_rooms_world.py for the
rooms) write placeholder NPCs from the mockup markers. build.py applies `apply(spec)` right after it loads a spec, so
whichever generator wrote the spec, the story pass is layered on top:

  patch_objects  {local_id: {field: value}}   change a placeholder NPC: "custom": True (its script is written by hand in
                                              story/<Map>.inc), "gfx", "move" (facing), "sight": n (a trainer who spots the
                                              player n tiles away), "flag" (hidden while set), "text"
  add_objects    [{object}]                   NPCs the markers don't have (same fields as the spec's objects)
  patch_items    {flag: {field: value}}       change an item ball by its flag (e.g. the item it holds)
  add_items      [{item, x, y, flag}]
  triggers       [{x, y, var, value, script}] coord events that run a script while a story variable has a value
  signs          [{id, x, y, text}]           extra signs (custom scripts: add "custom": True)
  patch_signs    {id: {field: value}}         change a generated sign (its text, "custom")

Trainers named in a script need a slot: see orleans_trainers.py and trainers/*.party.
Rooms (interiors): `INTERIOR[<mockup key>]` = {"people": [(kind, text, opts)], "positions": [(x, y)], "bg_events": [...],
"coord_events": [...]} or, to change only some of the generated people, "texts": {index: text} and "opts": {index: {...}}: interior_rooms_world.world_rooms swaps the people, build_interior.build adds the events (it keeps events
already in a room's map.json, so these are merged by position + script).

`python tools/mapgen/story_overlay.py` lists what is defined and checks every patched id exists in its spec.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FACE = "MOVEMENT_TYPE_FACE_"


def trainer(gfx, move, sight=3):
    return {"gfx": gfx, "move": FACE + move, "sight": sight, "custom": True}


OVERLAY = {
    # ------------------------------------------------------------------ Chapter 2
    "Route2": {
        "patch_objects": {
            "LOCALID_ORLEANS_ROUTE2_TRAINER_2": trainer("OBJ_EVENT_GFX_YOUNGSTER", "DOWN"),       # (9, 8)   Thibault
            "LOCALID_ORLEANS_ROUTE2_TRAINER_5": trainer("OBJ_EVENT_GFX_CAMPER", "UP"),            # (17, 11) Noe
            "LOCALID_ORLEANS_ROUTE2_TRAINER_6": trainer("OBJ_EVENT_GFX_PICNICKER", "UP"),         # (27, 13) Josette
            "LOCALID_ORLEANS_ROUTE2_TRAINER_4": trainer("OBJ_EVENT_GFX_BOY_2", "DOWN"),           # (34, 10) Alcee
            "LOCALID_ORLEANS_ROUTE2_TRAINER_3": trainer("OBJ_EVENT_GFX_BARD", "DOWN"),            # (44, 9)  Remi
        },
        "patch_items": {
            "FLAG_UNUSED_0x278": {"item": "ITEM_GREAT_BALL", "_comment": "mockup: Potions, Antidotes, a Great Ball or two"},
        },
        "add_items": [
            {"x": 32, "y": 7, "item": "ITEM_RAICHUNITE_Y", "flag": "FLAG_UNUSED_0x268",
             "_comment": "Mega Stone (mockup marker 2): foot of the towers"},
        ],
    },
    "StormsEdge": {
        # the gym is on the west bank (user decision 9): the town's people are ordinary townsfolk with lines that change
        # with the grid; the arrival scene is a frame script (StormsEdge_OnFrameTable), not a trigger line
        "patch_objects": {
            "LOCALID_STORMS_EDGE_ECLAIR": {"custom": True, "flag": "FLAG_HIDE_STORMS_EDGE_ECLAIR"},
            "LOCALID_STORMS_EDGE_BRIDGE_TENDER": {"custom": True},
            "LOCALID_STORMS_EDGE_DECKHAND": {"custom": True},
            "LOCALID_STORMS_EDGE_LINEMAN": {"custom": True},
            "LOCALID_STORMS_EDGE_KEEPER": {"custom": True},
            # ordinary townsfolk read the same before and after the grid is back (audit ch2 S2)
            "LOCALID_STORMS_EDGE_KID": {"text": "The poles hum when the wind blows.\nZzzzt! Zzzzt!"},
            "LOCALID_STORMS_EDGE_FISHMONGER": {"text": "Shrimp's cheap today. The boats\ncome and go with the tide."},
            "LOCALID_STORMS_EDGE_BOY": {"text": "ECLAIR's crew keeps the substation\nhumming. Listen to it!"},
        },
    },
    "Route3": {
        "patch_objects": {
            # trainers 19-22 (Eclair's team is 18-21), west to east
            "LOCALID_ORLEANS_ROUTE3_TRAINER_1": trainer("OBJ_EVENT_GFX_FISHERMAN", "DOWN"),       # (5, 10)  Lazare
            "LOCALID_ORLEANS_ROUTE3_TRAINER_6": trainer("OBJ_EVENT_GFX_SAILOR", "UP"),            # (12, 12) Armand
            "LOCALID_ORLEANS_ROUTE3_TRAINER_2": trainer("OBJ_EVENT_GFX_BUG_CATCHER", "DOWN"),     # (19, 10) Dupre
            "LOCALID_ORLEANS_ROUTE3_TRAINER_7": trainer("OBJ_EVENT_GFX_WOMAN_3", "UP"),           # (28, 12) Rosalie
            "LOCALID_ORLEANS_ROUTE3_TRAINER_4": trainer("OBJ_EVENT_GFX_WOMAN_1", "DOWN"),         # (34, 10) Celestine
            "LOCALID_ORLEANS_ROUTE3_TRAINER_8": trainer("OBJ_EVENT_GFX_COOLTRAINER_M", "UP"),     # (38, 12) Auguste
        },
        "patch_items": {
            "FLAG_UNUSED_0x279": {"item": "ITEM_SUPER_POTION", "_comment": "mockup: Super Potions, Repels"},
        },
        "patch_signs": {
            # the generated line "Storm's Edge west, Crescent City east." is 38 characters (the box holds 36)
            "RouteSign2": {"text": "CAUSEWAY ROAD\nWest: Storm's Edge. East: Crescent."},
        },
        "add_objects": [
            # Jayden is hidden (Route3_OnTransition) until his scene: BridgeStandoffRow<r> puts him at (43, r), in front of
            # the player. Default spot: the bridge's middle lane.
            # elevation 4: on the bridge rows the deck cells are 15 and a walker keeps the bridgehead's elevation 4, so he must be
            # at 4 to stand on (not under) the deck; on the ground rows an object spawns at the cell's elevation anyway
            {"id": "LOCALID_ROUTE3_JAYDEN", "gfx": "OBJ_EVENT_GFX_BOY_1", "x": 43, "y": 11, "move": FACE + "LEFT",
             "text": "JAYDEN: Tch.", "custom": True, "flag": "FLAG_HIDE_ROUTE3_JAYDEN", "elevation": 4},
        ],
        # Jayden's trigger is a column across the whole causeway. Column x 42 has only five walkable cells (rows 0, 1, 8 and the
        # bridge's 11, 12: the pond and river fill the rest), so nobody crosses it without stepping on one of them; x 43 has the
        # same rows free for Jayden to stand on (story_gates_check.py proves it with a flood fill).
        # The bridge rows (11, 12) are deck cells (elevation 15) and the player crosses them at elevation 4, so those two triggers
        # use elevation 0 (= any); an event only fires at the player's own elevation. Rows 0, 1, 8 are ground (3).
        "triggers": [
            {"x": 42, "y": y, "var": "VAR_ORLEANS_STORY", "value": 11, "script": f"Route3_EventScript_BridgeStandoffRow{y}",
             **({"elevation": 0} if y in (11, 12) else {})}
            for y in (0, 1, 8, 11, 12)
        ],
    },
    "GrandOak": {
        # the road to Route 2 is three cells wide (rows 13-15): the hedge covers all three (the east edge is a magnolia wall)
        "add_objects": [
            {"id": "LOCALID_GRAND_OAK_STORM_HEDGE_3", "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "x": 43, "y": 13,
             "move": "MOVEMENT_TYPE_NONE", "text": "A storm-tangled hedge blocks the road.\nGarden Shears could cut it.",
             "custom": True, "flag": "FLAG_CUT_STORM_HEDGE"},
        ],
    },
    "CrescentCity": {
        # Route 14 (the levee road south of the city) is under floodwater until gym 6. Every walkable cell of the bottom row
        # inside the Route 14 connection (x 39-66) runs the same script, which turns the player back. The trigger's "var" is a
        # FLAG id, which the engine tests as a flag: it fires while FLAG_BADGE06_GET is clear (value 0) and turns itself off at
        # gym 6. (NEVER "var": "0": that is TRIGGER_RUN_IMMEDIATELY and freezes on a msgbox.) A later chapter replaces this
        # with the real water state (fix B: crescent_flood.py).
        "triggers": [
            {"x": x, "y": 63, "elevation": 3, "var": "FLAG_BADGE06_GET", "value": 0, "script": "CrescentCity_EventScript_FloodedRoad"}
            for x in range(39, 67)  # the whole connection (Route 14 is 28 wide), on the water's bank row (the water itself is rows 64-65)
        ],
    },
}

# Routes 6-8 are reachable on foot from Crescent's west edge along Route 6's south shore, but they open with the fourth verse
# (decision 3: the verse clears a water obstacle, here a jam of storm debris). The shore path narrows to two cells at x 29
# (rows 22, 23); both are debris objects, hidden by FLAG_ROUTE6_DEBRIS_CLEARED. (Flood fill: story_gates_check.py.)
OVERLAY["Route6"] = {
    "add_objects": [
        {"id": f"LOCALID_ORLEANS_ROUTE6_DEBRIS_{n}", "gfx": "OBJ_EVENT_GFX_CUTTABLE_TREE", "x": 29, "y": y,
         "move": "MOVEMENT_TYPE_NONE", "text": "", "custom": True, "flag": "FLAG_ROUTE6_DEBRIS_CLEARED"}
        for n, y in ((1, 22), (2, 23))
    ],
}

# rooms: key = the interior mockup key (interiors_world.py / map_name())
INTERIOR = {
    "storms_edge_gym": {
        "people": [
            ("gym guide", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_MAN_4"}),
            ("lineworker", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_WORKER_M", "sight": 2, "face": "RIGHT"}),
            ("electrician", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_EXPERT_F", "sight": 2, "face": "LEFT"}),
            ("eclair", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_WORKER_F"}),
            ("voltorb", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(VOLTORB)", "flag": "FLAG_HIDE_STORMS_EDGE_VOLTORB_1"}),
            ("voltorb", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_SPECIES(VOLTORB)", "flag": "FLAG_HIDE_STORMS_EDGE_VOLTORB_2"}),
        ],
        "positions": [(12, 15), (4, 8), (16, 11), (10, 2), (8, 13), (12, 8)],
        # the six junction panels: sign-type bg events, drawn lit/dark by the map's ON_LOAD script
        "bg_events": [
            {"type": "sign", "x": x, "y": y, "elevation": 3, "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": f"StormsEdge_Gym_EventScript_Junction{n}"}
            for n, (x, y) in enumerate([(6, 7), (10, 7), (14, 7), (6, 10), (10, 10), (14, 10)], 1)
        ],
    },
    # Storm's Edge's other rooms: the mockup notes became the generated lines ("gives the Good Rod once the grid is restored"),
    # so the people the grid changes are custom (story/StormsEdge_<Room>.inc) and the rest get proper lines.
    "storms_edge_pokecenter": {"opts": {1: {"custom": True}}},                      # Lineworker1
    "storms_edge_house_c": {"opts": {0: {"custom": True}}},                         # OldFisherman0
    "storms_edge_seafood_market": {"opts": {1: {"custom": True}}},                  # Shrimper1
    "storms_edge_lighthouse": {"opts": {0: {"custom": True}}},                      # Keeper0
    "storms_edge_mart": {"texts": {1: "Everything electric sold out in a\\nday. Batteries, bulbs, the lot!"}},
    "storms_edge_house_w": {"texts": {0: "My husband climbs the poles all\\nday. He sleeps like a log.",
                                      1: "I love the lighthouse. It looks so\\ntall from our window!"}},
    "storms_edge_house_e": {"texts": {0: "I'd swap my WINGULL for a MAGIKARP.\\nIt's homesick for the sea."}},
}


# ---------------------------------------------------------------------------------------------- Chapter 3 (story_data_ch3.py)
import story_data_ch3 as _c3  # noqa: E402


def _merge_ch3():
    cc = OVERLAY["CrescentCity"]
    cc.setdefault("add_hidden", []).extend(_c3.CRESCENT.get("add_hidden", []))
    OVERLAY.setdefault("Route3", {}).setdefault("add_hidden", []).extend(_c3.ROUTE3["add_hidden"])
    OVERLAY["PointeRouge"] = _c3.POINTE_ROUGE
    for key in ("patch_objects", "add_objects", "add_items"):
        if isinstance(_c3.CRESCENT.get(key), dict):
            cc.setdefault(key, {}).update(_c3.CRESCENT[key])
        else:
            cc.setdefault(key, []).extend(_c3.CRESCENT.get(key, []))
    cc.setdefault("patch_signs", {}).update(_c3.CRESCENT.get("patch_signs", {}))
    OVERLAY["Route4"] = _c3.ROUTE4
    for k, v in _c3.ROOMS.items():
        INTERIOR[k] = v


_merge_ch3()

# ---------------------------------------------------------------------------------------------- Chapter 4 (story_data_ch4.py)
import story_data_ch4 as _c4  # noqa: E402


def _merge_into(dst, src):
    for key, val in src.items():
        if isinstance(val, dict):
            dst.setdefault(key, {}).update(val)
        elif isinstance(val, list):
            dst.setdefault(key, []).extend(val)
        else:
            dst[key] = val


def _merge_ch4():
    for name, data in (("Route4", _c4.ROUTE4), ("Route5", _c4.ROUTE5), ("PointeRouge", _c4.POINTE_ROUGE)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c4.ROOMS.items():
        INTERIOR[k] = v


_merge_ch4()

# ---------------------------------------------------------------------------------------------- Chapter 5 (story_data_ch5.py)
import story_data_ch5 as _c5  # noqa: E402


def _merge_ch5():
    for name, data in (("Route6", _c5.ROUTE6), ("Route7", _c5.ROUTE7), ("Route8", _c5.ROUTE8), ("Route9", _c5.ROUTE9), ("CampCocodrie", _c5.CAMP)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c5.ROOMS.items():
        INTERIOR[k] = v


_merge_ch5()

# ---------------------------------------------------------------------------------------------- Chapter 6 (story_data_ch6.py)
import story_data_ch6 as _c6  # noqa: E402


def _merge_ch6():
    for name, data in (("Route10", _c6.ROUTE10), ("Route11", _c6.ROUTE11), ("Route12", _c6.ROUTE12), ("Route13", _c6.ROUTE13), ("LutinsHollow", _c6.HOLLOW)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c6.ROOMS.items():
        INTERIOR[k] = v


_merge_ch6()

# ---------------------------------------------------------------------------------------------- Chapter 7 (story_data_ch7.py)
import story_data_ch7 as _c7  # noqa: E402


def _merge_ch7():
    for name, data in (("Route14", _c7.ROUTE14), ("Route15", _c7.ROUTE15), ("Route16", _c7.ROUTE16), ("Route17", _c7.ROUTE17),
                       ("Redfield", _c7.REDFIELD), ("OldWater", _c7.OLD_WATER)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c7.ROOMS.items():
        INTERIOR[k] = v


_merge_ch7()

# ---------------------------------------------------------------------------------------------- Chapter 8 (story_data_ch8.py)
import story_data_ch8 as _c8  # noqa: E402


def _merge_ch8():
    for name, data in (("Route18", _c8.ROUTE18), ("Route19", _c8.ROUTE19), ("Route20", _c8.ROUTE20), ("Route21", _c8.ROUTE21),
                       ("Route22", _c8.ROUTE22), ("LandsEnd", _c8.LANDS_END)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c8.ROOMS.items():
        INTERIOR[k] = v


_merge_ch8()

# ---------------------------------------------------------------------------------------------- Chapter 9, the finale (story_data_ch9.py)
import story_data_ch9 as _c9  # noqa: E402


def _merge_ch9():
    for name, data in (("Route22", _c9.ROUTE22), ("Route23", _c9.ROUTE23), ("Route24", _c9.ROUTE24), ("Route25", _c9.ROUTE25),
                       ("OldestShrine", _c9.OLDEST_SHRINE), ("OldWater", _c9.OLD_WATER)):
        _merge_into(OVERLAY.setdefault(name, {}), data)
    for k, v in _c9.ROOMS.items():
        INTERIOR[k] = v


_merge_ch9()

# ---------------------------------------------------------------------------------------------- Chapter 10, the post-game (story_data_ch10.py)
import story_data_ch10 as _c10  # noqa: E402


def _merge_ch10():
    outdoor = sorted({m for (m, *_rest) in _c10.all_objects() if m not in _c10.INTERIOR_KEYS})
    for name in outdoor:
        _merge_into(OVERLAY.setdefault(name, {}), {"add_objects": _c10.overlay_for(name)})
    for name, key in _c10.INTERIOR_KEYS.items():
        ov = INTERIOR.setdefault(key, {})
        ov.setdefault("extra", []).extend(_c10.interior_extras(name))
    _merge_into(OVERLAY.setdefault("CrescentCity", {}), _c10.FRONTIER)
    for k, v in _c10.ROOMS.items():
        ov = INTERIOR.setdefault(k, {})
        for sub, val in v.items():
            ov.setdefault(sub, {}).update(val)


_merge_ch10()

# ---------------------------------------------------------------------------------------------- the water gates (story_data_gates.py)
import story_data_gates as _gates  # noqa: E402


def _merge_gates():
    import world_reach  # map sizes come from the built layouts
    for g in _gates.GATES:
        d = world_reach.load(g["map"])
        trig, objs = _gates.overlay_for(g, d["w"], d["h"])
        ov = OVERLAY.setdefault(g["map"], {})
        ov.setdefault("triggers", []).extend(trig)
        ov.setdefault("add_objects", []).extend(objs)


_merge_gates()

# ---------------------------------------------------------------------------------------------- trainer sight fixes (fix B, audit ch8_2 N2 + sight_lint.py)
# A rock or wall in the first cell blinds a trainer: those are moved or turned so their line is open. (A land trainer looking over water is
# fixed in build.py's sight_cells(): the cell under it gets elevation 0, the engine ignores a spawned NPC's template elevation.)
# sight_lint.py proves every sight trainer can spot a player somewhere.
SIGHT_FIXES = {
    "Route11": {"LOCALID_ORLEANS_ROUTE11_TRAINER_0": {"move": FACE + "LEFT"}},                      # a rock stood right below him (43, 6): look along the water
    "Route18": {"LOCALID_ORLEANS_ROUTE18_TRAINER_7": {"move": FACE + "RIGHT"}},                      # the rock formation stood right above her
    "Route22": {"LOCALID_ORLEANS_ROUTE22_TRAINER_1": {"x": 28, "y": 14}},                            # Leontine: the rock at (27, 14) blinded her
    "Route25": {"LOCALID_ORLEANS_ROUTE25_TRAINER_2": {"x": 14}},                                     # Genevieve: the rock at (13, 16)
}
for _m, _f in SIGHT_FIXES.items():
    OVERLAY.setdefault(_m, {}).setdefault("patch_objects", {})
    for _lid, _fields in _f.items():
        OVERLAY[_m]["patch_objects"].setdefault(_lid, {}).update(_fields)

# the Route 22 ruin sign stands on the island's shore and is read by swimmers from the water (elevation 1) as well as from land: 0 matches both (ch8_2 S3)
OVERLAY.setdefault("Route22", {}).setdefault("patch_signs", {})["RouteSign1"] = {"elevation": 0}

# ---------------------------------------------------------------------------------------------- Heart Scales (fix B, ch3_2 R1)
# The move tutor (CrescentCity_Tutor) charges one HEART SCALE a lesson and says they "wash up on the flats", but no scale existed anywhere.
# Six hidden ones on shores and flats (the shop sells more: fix C). Flags are hidden-item flags from flag_pool.py (>= 0x1F4).
HEART_SCALES = [
    ("Route2", 14, 18, "FLAG_HIDDEN_HEART_SCALE_ROUTE2", "the lake bank below the road"),
    ("Route3", 23, 13, "FLAG_HIDDEN_HEART_SCALE_ROUTE3", "the mud flats south of the bridge"),
    ("Route5", 37, 14, "FLAG_HIDDEN_HEART_SCALE_ROUTE5", "the lakeshore"),
    ("Route9", 29, 7, "FLAG_HIDDEN_HEART_SCALE_ROUTE9", "the marsh shore"),
    ("Route12", 11, 38, "FLAG_HIDDEN_HEART_SCALE_ROUTE12", "the shallows"),
    ("StormsEdge", 29, 14, "FLAG_HIDDEN_HEART_SCALE_STORMS_EDGE", "the harbour shingle"),
]
for _m, _x, _y, _flag, _note in HEART_SCALES:
    OVERLAY.setdefault(_m, {}).setdefault("add_hidden", []).append({"x": _x, "y": _y, "item": "ITEM_HEART_SCALE", "flag": _flag, "_note": _note})

# ---------------------------------------------------------------------------------------------- NPC lines that were leaked spec notes
import story_data_npc_text as _npct  # noqa: E402

_npct.merge(INTERIOR)

# ---------------------------------------------------------------------------------------------- application
def apply(spec):
    """Layer the story pass onto a spec (in place; returns it). A map with no overlay is returned unchanged."""
    ov = OVERLAY.get(spec.get("map"))
    if not ov:
        return spec
    objs = spec.setdefault("objects", [])
    byid = {o["id"]: o for o in objs}
    for lid, fields in ov.get("patch_objects", {}).items():
        if lid in byid:
            byid[lid].update(fields)
    for o in ov.get("add_objects", []):
        if o["id"] in byid:
            byid[o["id"]].update(o)
        else:
            objs.append(dict(o))
    items = spec.setdefault("items", [])
    byflag = {i["flag"]: i for i in items}
    for flag, fields in ov.get("patch_items", {}).items():
        if flag in byflag:
            byflag[flag].update(fields)
    for it in ov.get("add_items", []):
        if it["flag"] in byflag:
            byflag[it["flag"]].update(it)
        else:
            items.append(dict(it))
    if ov.get("add_hidden"):
        hid = spec.setdefault("hidden_items", [])
        have_h = {h["flag"] for h in hid}
        for h in ov["add_hidden"]:
            if h["flag"] not in have_h:
                hid.append(dict(h))
    trig = spec.setdefault("triggers", []) if ov.get("triggers") else spec.get("triggers")
    for t in ov.get("triggers", []):
        if t not in trig:
            trig.append(dict(t))
    if ov.get("patch_signs"):
        for sg in spec.get("signs", []):
            sg.update(ov["patch_signs"].get(sg["id"], {}))
    if ov.get("signs"):
        signs = spec.setdefault("signs", [])
        have = {s["id"] for s in signs}
        for s in ov["signs"]:
            if s["id"] not in have:
                signs.append(dict(s))
    return spec


def interior_people(key, people, positions):
    """The room's people and their positions: the overlay's if it has one, else what the generator made."""
    ov = INTERIOR.get(key)
    if ov and ov.get("people"):
        out, pos = list(ov["people"]), list(ov.get("positions", positions))
        for kind, text, opts, at in ov.get("extra", []):  # the post-game objects (story_data_ch10) come after the room's own people
            out.append((kind, text, opts) if opts else (kind, text))
            pos.append(at)
        return out, pos
    if ov and (ov.get("texts") or ov.get("opts") or ov.get("extra")):  # change some of the generated people in place
        out = []
        for i, p in enumerate(people):
            kind, text = p[0], p[1]
            opts = dict(p[2]) if len(p) > 2 else {}
            text = ov.get("texts", {}).get(i, text)
            opts.update(ov.get("opts", {}).get(i, {}))
            out.append((kind, text, opts) if opts else (kind, text))
        pos = list(positions)
        for kind, text, opts, at in ov.get("extra", []):  # people the markers didn't make (appended: their index is after the generated ones)
            out.append((kind, text, opts) if opts else (kind, text))
            pos.append(at)
        return out, pos
    return people, positions


def interior_events(key, which, existing):
    """existing + the overlay's bg_events / coord_events for the room. An overlay event REPLACES the existing events that run
    the same script (so moving a light in the overlay moves it in the map instead of leaving the old one behind)."""
    ov = INTERIOR.get(key, {}).get(which, [])
    scripts = {e.get("script") for e in ov}
    kept = [e for e in existing if e.get("script") not in scripts]
    return kept + [dict(e) for e in ov]


# ---------------------------------------------------------------------------------------------- self check
def main():
    spec_dir = os.path.join(HERE, "maps")
    by_map = {}
    for fn in os.listdir(spec_dir):
        if fn.endswith(".json") and not fn.endswith((".detected.json", ".base.json")) and not fn.startswith("_"):
            try:
                s = json.load(open(os.path.join(spec_dir, fn), encoding="utf-8"))
            except ValueError:
                continue
            if isinstance(s, dict) and "map" in s and "objects" in s:
                by_map.setdefault(s["map"], (fn, s))
    bad = 0
    for name, ov in OVERLAY.items():
        if name not in by_map:
            print(f"{name}: no spec found")
            bad += 1
            continue
        fn, spec = by_map[name]
        ids = {o["id"] for o in spec.get("objects", [])}
        flags = {i["flag"] for i in spec.get("items", [])}
        for lid in ov.get("patch_objects", {}):
            if lid not in ids:
                print(f"{name}: patched object {lid} is not in {fn}")
                bad += 1
        for fl in ov.get("patch_items", {}):
            if fl not in flags:
                print(f"{name}: patched item flag {fl} is not in {fn}")
                bad += 1
        after = apply(json.loads(json.dumps(spec)))
        print(f"{name}: +{len(after['objects']) - len(spec['objects'])} objects, "
              f"+{len(after.get('items', [])) - len(spec.get('items', []))} items, "
              f"+{len(after.get('triggers') or []) - len(spec.get('triggers') or [])} triggers ({fn})")
    for key, ov in INTERIOR.items():
        print(f"room {key}: {len(ov.get('people', []))} people, {len(ov.get('bg_events', []))} bg events")
    print("problems:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

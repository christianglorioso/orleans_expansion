"""The region's water gates (decision 3 follow-up): each Singer's verse clears an OBSTACLE ON THE WATER, so Surf (given after gym 4)
cannot sail past a verse that has not been earned. Merged into story_overlay.OVERLAY by story_overlay._merge_gates().

Every gate is a CUT across one route: a full column (axis "x") or row (axis "y") of coord-event triggers, one per cell (elevation 0 = a
walker and a surfer both fire it; a trigger on a wall cell never fires, so the whole line is written and the terrain may change
under it), keyed on the verse flag (var = FLAG, value 0: it fires while the flag is clear and is dead once it is set). The script turns
the player back one step toward the near side. A few obstacle OBJECTS (existing sprite, hidden by the same flag) stand on the cut's
water cells so the jam is visible; they are kept out of the seam bands (7 columns / 5 rows from connected edges).
story_gates_check.py proves every gate with a world-wide flood fill (walk + Surf) over all maps joined by their connections.

  map     Orleans map directory name            at      the column (axis x) or row (axis y) of the cut
  flag    the key flag (the verse)               back    the movement that turns the player back (towards the near side)
  objects [(x, y)] cells that get an obstacle object (ids `LOCALID_<MAP>_<WORD>_<n>`)
"""
from story_data_ch3 import T

GATES = [
    # verse 4 (Kingfisher), sung at the Old Water: Routes 6-9 and Camp Cocodrie. Route 6's channel at x 29: water rows 4-21, the
    # shore path (rows 22, 23) is already blocked by the two storm-debris objects of story_overlay.py.
    {"map": "Route6", "axis": "x", "at": 29, "flag": "FLAG_ROUTE6_DEBRIS_CLEARED", "script": "Route6_EventScript_WaterGate",
     "back": "walk_right", "word": "DEBRIS", "first": 3, "objects": [(29, y) for y in range(16, 22)],
     "text": T("Storm debris jams the whole channel.", "Nothing floats through.")},
    # verse 5 (the brothers): Routes 10-11 across Big Lake. Route 10 at x 11 (water rows 0-11, the lake road below).
    {"map": "Route10", "axis": "x", "at": 11, "flag": "FLAG_BADGE05_GET", "script": "Route10_EventScript_WaterGate",
     "back": "walk_left", "word": "JAM", "first": 1, "objects": [(11, y) for y in range(8, 12)],
     "text": T("A jam of logs and rafts fills", "the canal. Nothing floats through.")},
    # verse 7 (Cayenne): Routes 18-20. Route 18 at x 38.
    {"map": "Route18", "axis": "x", "at": 38, "flag": "FLAG_BADGE07_GET", "script": "Route18_EventScript_WaterGate",
     "back": "walk_left", "word": "SPAN", "first": 1, "objects": [(38, y) for y in range(8, 12)],
     "text": T("A fallen span lies across the", "channel, black with old fire.")},
    # verse 8 (Heron): Routes 21-22 into the Gulf. Route 21 at row 8 (all water), objects in the middle.
    {"map": "Route21", "axis": "y", "at": 8, "flag": "FLAG_BADGE08_GET", "script": "Route21_EventScript_WaterGate",
     "back": "walk_up", "word": "DEBRIS", "first": 1, "objects": [(x, 8) for x in range(22, 28)],
     "text": T("A wrecked barge and a wall of rain", "block the way into the Gulf.")},
    # both raids (Kyogre and Groudon calmed, either order): ALL of Route 25 (wild Lv 59-63) and the Oldest Shrine stay shut. The cut is
    # Route 8's row 1, just inside its north exit (the 8/25 seam): the 'up' connection is the only one that reaches row 0 (Route 9's
    # and Route 7's connections start at rows 2 and 3), so row 1 across the whole width seals it. No objects (rows 0-4 are the seam band).
    {"map": "Route8", "axis": "y", "at": 1, "flag": "FLAG_ROUTE25_OPEN", "script": "Route8_EventScript_WaterGate",
     "back": "walk_down", "word": "JAM", "first": 1, "objects": [],
     "text": T("The channel boils under a wall of", "storm. Nothing can cross it.")},
]

GFX = "OBJ_EVENT_GFX_CUTTABLE_TREE"


def overlay_for(gate, width, height):
    """(triggers, add_objects) for one gate; width/height are the map's size in cells"""
    cells = [(gate["at"], i) for i in range(height)] if gate["axis"] == "x" else [(i, gate["at"]) for i in range(width)]
    trig = [{"x": x, "y": y, "elevation": 0, "var": gate["flag"], "value": 0, "script": gate["script"], "gate": True} for x, y in cells]
    mapu = gate["map"].upper()
    objs = []
    for n, (x, y) in enumerate(gate["objects"], gate["first"]):
        objs.append({"id": f"LOCALID_ORLEANS_{mapu}_{gate['word']}_{n}", "gfx": GFX, "x": x, "y": y, "move": "MOVEMENT_TYPE_NONE",
                     "text": gate["text"], "flag": gate["flag"]})
    return trig, objs

"""First-pass rooms for every interior after the vertical slice (the mockups in interiors_world.py).

Each room is painted straight from its mockup with the "generic" style below (gTileset_OrleansInterior plus
the building primary), and people come from the mockup markers. Each room's door is the town building
that town_plans.PLANS gives it (matched by label); rooms without one are built but not linked yet (their
exit leads back to the town's first door).
"""
import re

import interiors as mock
import story_overlay
from town_plans import TOWN_CFG, door_label, room_keys

TOWNS = {  # mockup key prefix -> town map, spec, group, map section, music
    "storms_edge": ("MAP_STORMS_EDGE", "StormsEdge", "MAPSEC_STORMS_EDGE", "MUS_RG_VERMILLION"),
    "crescent_city": ("MAP_CRESCENT_CITY", "CrescentCity", "MAPSEC_CRESCENT_CITY", "MUS_RG_CELADON"),
    "pointe_rouge": ("MAP_POINTE_ROUGE", "PointeRouge", "MAPSEC_POINTE_ROUGE", "MUS_RG_SILPH"),
    "camp_cocodrie": ("MAP_CAMP_COCODRIE", "CampCocodrie", "MAPSEC_CAMP_COCODRIE", "MUS_RG_FUCHSIA"),
    "lutins_hollow": ("MAP_LUTINS_HOLLOW", "LutinsHollow", "MAPSEC_LUTINS_HOLLOW", "MUS_RG_LAVENDER"),
    "redfield": ("MAP_REDFIELD", "Redfield", "MAPSEC_REDFIELD", "MUS_RG_PEWTER"),
    "lands_end": ("MAP_LANDS_END", "LandsEnd", "MAPSEC_LANDS_END", "MUS_RG_CINNABAR"),
}

PLANNED = room_keys()  # rooms with a building in their town
# rooms reached from another room rather than the street: room -> (the room it leads back to, stairs to it)
UPSTAIRS = {"crescent_city_dept_2f": "crescent_city_dept_1f", "crescent_city_dept_3f": "crescent_city_dept_2f",
            "pointe_rouge_capitol_deck": "pointe_rouge_capitol_lobby",
            "storms_edge_lighthouse_gallery": "storms_edge_lighthouse"}
# the way up from a floor, and the way down from the floor above (each on that floor's stairs or lift art)
STAIRS = {"crescent_city_dept_1f": (14, 2), "crescent_city_dept_2f": (1, 8), "pointe_rouge_capitol_lobby": (14, 2),
          "storms_edge_lighthouse": (4, 2)}
DOWN = {"crescent_city_dept_2f": (14, 2), "crescent_city_dept_3f": (14, 2), "pointe_rouge_capitol_deck": (14, 8),
        "storms_edge_lighthouse_gallery": (1, 2)}
MART = ["ITEM_POKE_BALL", "ITEM_GREAT_BALL", "ITEM_POTION", "ITEM_SUPER_POTION", "ITEM_ANTIDOTE",
        "ITEM_PARALYZE_HEAL", "ITEM_AWAKENING", "ITEM_REPEL"]
# Redfield and Land's End are visited at levels 44-57: a late-game shelf (audit ch7 N6 / ch8 N3)
MART_LATE = MART + ["ITEM_ULTRA_BALL", "ITEM_HYPER_POTION", "ITEM_REVIVE", "ITEM_FULL_HEAL", "ITEM_MAX_REPEL"]
LATE_MARTS = ("redfield_mart", "lands_end_marine_supply")
GENERIC = dict(style="generic", tileset="orleans_interior", secondary="gTileset_OrleansInterior")


def map_name(key):
    town = next(t for t in TOWNS if key.startswith(t))
    return TOWNS[town][1] + "_" + "".join(p.capitalize() for p in key[len(town) + 1:].split("_")), town


def say(text):
    """Mockup marker text -> a short placeholder line: ASCII (plus é), wrapped into 2-line boxes."""
    text = text.replace("“", "'").replace("”", "'").replace("’", "'").replace("…", "...").replace('"', "'")
    text = "".join(c if (c.isascii() or c in "éÉ") else " " for c in text)
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > 30 and line:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    out = ""
    for i, l in enumerate(lines[:6]):
        out += ("" if i == 0 else ("\\n" if i % 2 else "\\p")) + l
    return out


BLOCKING = {"wall", "thatch", "counter", "shelf", "bed", "plant", "metal", "screen", "tank", "water", "glass",
            "moss", "hedge", "tomb", "stool"}


def open_cells(spec):
    """Floor cells of a mockup room nobody's standing on yet (exits excluded)."""
    w, h = spec["size"]
    kinds = [[None] * w for _ in range(h)]
    for kind, x, y, rw, rh, *_ in mock.room(w, h, spec.get("floor", "wood"), spec.get("door"), spec.get("door_w", 1)) + spec["shapes"]:
        for yy in range(y, min(h, y + rh)):
            for xx in range(x, min(w, x + rw)):
                kinds[yy][xx] = kind
    return {(x, y) for y in range(h) for x in range(w) if kinds[y][x] not in BLOCKING and kinds[y][x] != "exit"
            and y < h - 2}


def nudge(x, y, free, taken):
    """The nearest free floor cell to (x, y) (people drawn on a table stand beside it)."""
    best = min(((abs(fx - x) + abs(fy - y), fy, fx) for fx, fy in free if (fx, fy) not in taken), default=None)
    return (best[2], best[1]) if best else (x, y)


def people(spec):
    """Mockup markers -> (kind, text) people and their positions, in marker order."""
    free, taken = open_cells(spec), set()
    out, pos = [], []
    for kind, x, y, text in spec["markers"]:
        if kind == "heal":
            out.append(("nurse", ""))
        elif kind == "shop":
            out.append(("clerk", ""))
        elif kind == "trainer":
            out.append(("trainer", say("(Trainer battle to be scripted.)")))
        elif kind == "npc":
            who, _, line = text.partition(":")
            who = re.sub(r"[^a-z ]", "", who.lower()).strip() or "npc"
            who = " ".join(who.split()[:2]) if len(who) < 24 else "npc"
            out.append((who, say(line.strip() or text)))
        else:
            continue
        if kind not in ("heal", "shop") and ((x, y) not in free or (x, y) in taken):
            x, y = nudge(x, y, free, taken)
        taken.add((x, y))
        pos.append((x, y))
    return out, pos


def world_rooms(room):
    rooms = []
    for key, spec in mock.INTERIORS.items():
        if not any(key.startswith(t) for t in TOWNS):
            continue
        name, town = map_name(key)
        tmap, tname, mapsec, music = TOWNS[town]
        base = dict(exterior=tmap, exterior_spec=f"{town}.json", exterior_cfg=TOWN_CFG[town],
                    group=f"gMapGroup_Indoor{tname}", mapsec=mapsec,
                    music="MUS_GYM" if key.endswith("_gym") else "MUS_RG_POKE_CENTER" if "pokecenter" in key else music)
        ppl, pos = people(spec)
        ppl, pos = story_overlay.interior_people(key, ppl, pos)  # the story pass swaps a room's people
        r = room(base, GENERIC, map=name, const="MAP_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper().replace("__", "_"),
                 mockup=key, people=ppl, positions=pos, title=spec["title"])
        if any(p[0] == "clerk" for p in ppl):
            r["mart"] = MART_LATE if key in LATE_MARTS else MART
        if key in UPSTAIRS:
            r["door_label"] = None
            r["no_door"] = True  # an upper floor: no street door, only its stairs
        elif key not in PLANNED:
            r["door_label"] = None
            r["exit_to"] = (tmap, 0)
        else:
            r["door_label"] = door_label(key, spec["title"])
        # the two legendary arenas are entered from Routes 24 / 22: their own region map sections (Fly map, popup)
        r["mapsec"] = {"lands_end_salt_cathedral": "MAPSEC_SALT_DOME", "lands_end_drowned_temple": "MAPSEC_DROWNED_TEMPLE"}.get(key, r["mapsec"])
        rooms.append(r)
    # stairs between floors. An upper floor's warp 0 is its way down, landing on the up-warp of the floor
    # below; that up-warp comes after the floor's own exits (the door mat, or the way down)
    consts = {r["mockup"]: r["const"] for r in rooms}
    up_index = lambda k: 1 if k in UPSTAIRS else mock.INTERIORS[k].get("door_w", 1)
    for r in rooms:
        k = r["mockup"]
        r["warps_extra"] = []
        if k in UPSTAIRS:
            x, y = DOWN[k]
            r["warps_extra"].append((x, y, consts[UPSTAIRS[k]], up_index(UPSTAIRS[k])))
        if k in STAIRS:
            up = next(u for u, v in UPSTAIRS.items() if v == k)
            x, y = STAIRS[k]
            r["warps_extra"].append((x, y, consts[up], 0))
    return rooms


# ------------------------------------------------------------------ the generic style
def paint_generic(kind, label, dx, dy, rw, rh, x, y, w=0, h=0):
    """Paint any mockup shape with HnS house/Center/Mart pieces (gTileset_OrleansInterior) on the building
    primary: back wall, wood or tile floors, counters, shelves, beds, rugs, plants, plus hedges, glass,
    water and statues for the gyms."""
    if kind in (None, "wall", "thatch"):
        if y == 0:
            return "jb:0A8", 1
        if y == 1:
            return "jb:0B0", 1
        if y == h - 1:
            return "jb:008", 1
        return "jb:000", 1
    if kind == "exit":  # the HnS door mat: a south-arrow warp, so walking down onto it leaves the room
        return "jb:0E7", 0
    if "stairs" in label or "elevator" in label:  # the warp tile (a west-arrow warp: approach from the east)
        return ("jb:0DC", 0) if dx == 0 and dy == 0 else ("jb:0A9", 0)
    if kind == "wood":
        return ("jb:0B1" if y == 2 else "jb:0A9"), 0
    if kind == "tile":
        return "pc:401", 0
    if kind in ("stone",):
        return "pc:401", 0
    if kind == "carpet":
        return "jb:0CC", 0
    if kind == "mud":
        return "jb:0A9", 0
    if kind == "grass":
        return "cg:46E", 0
    if kind == "sand":
        return "cg:425", 0
    if kind == "counter":
        if "bench" in label:
            return "pc:475", 1
        if any(k in label for k in ("table", "desk")):  # the HnS wooden table (2 wide, legs on the lower row)
            return "jb:" + (("0C8" if dx % 2 == 0 else "0C9") if dy % 2 == 0 else ("0D0" if dx % 2 == 0 else "0D1")), 1
        return ("pc:43C" if rw == 1 else "pc:439" if dx == 0 else "pc:43D" if dx == rw - 1 else "pc:43C"), 1
    if kind == "shelf":
        if y < 2:  # on the back wall: a bookcase
            return ("jb:0E5" if dx % 2 == 0 else "jb:0E6"), 1
        if dy == 0:
            return ("mt:457" if dx % 2 == 0 else "mt:458"), 1
        return ("mt:453" if dx % 2 == 0 else "mt:454"), 1
    if kind == "bed":
        return ("ph:404" if dy == 0 else "ph:414"), 1
    if kind == "rug":
        if rw == 1 or rh == 1:
            return "jb:0CC", 0
        col = "L" if dx == 0 else "R" if dx == rw - 1 else "M"
        row = "T" if dy == 0 else "B" if dy == rh - 1 else "M"
        return "jb:" + {"TL": "0C3", "TM": "0C4", "TR": "0C5", "ML": "0CB", "MM": "0CC", "MR": "0CD",
                        "BL": "0D3", "BM": "0D4", "BR": "0D5"}[row + col], 0
    if kind == "plant":
        return ("jb:0F6" if rh >= 2 and dy == 0 else "jb:0FE"), 1
    if kind == "stage":
        return ("cv:dais_L" if dx == 0 and rw > 1 else "cv:dais_R" if dx == rw - 1 and rw > 1 else "cv:dais_M"), 0
    if kind == "metal":
        return (("mt:456" if dx % 2 == 0 else "mt:455") if dy == 0 else ("mt:453" if dx % 2 == 0 else "mt:454")), 1
    if kind == "screen":
        return "ph:40E", 1
    if kind in ("tank", "water"):
        return "ekat:water_C", 1
    if kind == "glass":
        return ("cv:glass_0" if y == 0 else "cv:glass_1" if y == 1 else "cv:glass_side"), 1
    if kind in ("moss", "hedge"):
        return "cg:415", 1
    if kind == "flowers":
        return ("cg:436" if (x + y) % 2 else "cg:437"), 0
    if kind == "statue":
        return ("cg:438", 0) if dy == 0 else ("cg:439", 1)
    if kind == "tomb":
        return "cg:439", 1
    if kind == "stool":
        return "pc:475", 1
    return "jb:0A9", 0


STYLE = {"prefix": "jb", "side": "jb:000", "paint": paint_generic}

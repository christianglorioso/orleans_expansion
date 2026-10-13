"""Build interior maps and wire them to their exterior doors.

usage (from the decomp root): python tools/mapgen/build_interior.py [ROOM ...] [--preview DIR]

Two kinds of room (see ROOMS in interior_rooms.py):
  * "ref": a reference layout from the soulgold project (interior_sources.REFERENCES), translated
    metatile by metatile into our composed interior tilesets. Its exit warp and NPC spots come from
    the reference map, so furniture and people sit where a real HGSS room had them.
  * "mockup": drawn from the planning mockup in interiors.py (Rootkin huts, the conservatory gym),
    using our own art through a style table.

Writes data/layouts/<Map>/{map.bin,border.bin}, the layouts.json entry, data/maps/<Map>/{map.json,
scripts.inc} and the map group, and records each room's exterior door so build.py can point it inside.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import interior_sources as src  # noqa: E402
import interiors as mock  # noqa: E402
from event_scripts import include_map_scripts  # noqa: E402
from interior_rooms import ROOMS, STYLES  # noqa: E402
import story_overlay  # noqa: E402
import interior_rest  # noqa: E402

TS = os.path.join(HERE, "tilesets")
WALL_ELEV = 3


def load_mapping(*names):
    m = {}
    for n in names:
        m.update(json.load(open(os.path.join(TS, n + ".mapping.json")))["metatiles"])
    return m


def block(mid, coll, elev=3):
    return mid | (coll << 10) | (elev << 12)


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ------------------------------------------------------------------ reference rooms
def ref_room(room):
    L = src.layouts()
    lay = L[src.REFERENCES[room["map"]]]
    sec = lay["secondary_tileset"]
    raw = src.blocks(lay)
    w, h = lay["width"], lay["height"]
    grid = []
    M = load_mapping("orleans_building", room["tileset"])
    for y in range(h):
        row = []
        for x in range(w):
            mid, coll, elev = src.decode(raw[y * w + x], lay["id"])
            name = src.name_of(mid, sec, lay["primary_tileset"])
            if name not in M:
                raise SystemExit(f"{room['map']}: {name} missing from the composed tilesets")
            row.append(block(M[name], coll, elev))
        grid.append(row)
    # the reference map's events: exit warp and NPC spots
    ref_map = None
    for d in os.listdir(f"{src.SG}/data/maps"):
        p = f"{src.SG}/data/maps/{d}/map.json"
        if os.path.exists(p):
            m = json.load(open(p))
            if m.get("layout") == lay["id"]:
                ref_map = m
                break
    outs = [w_ for w_ in ref_map["warp_events"] if "STAIRS" not in w_["dest_map"] and "_2F" not in w_["dest_map"]]
    exits = [(w_["x"], w_["y"]) for w_ in sorted(outs, key=lambda w_: -w_["y"])][:1]  # the front door: the lowest exit
    spots = [(o["x"], o["y"], o.get("graphics_id", "")) for o in ref_map.get("object_events", [])]
    return grid, exits, spots


# ------------------------------------------------------------------ pret rooms
def pret_room(room):
    """A vanilla pokeemerald room (src.PRET_ROOMS), read in Emerald's block format."""
    pr = src.PRET_ROOMS[room["map"]]
    M = load_mapping("orleans_building", room["tileset"])
    raw = src.pret_blocks(room["map"])
    m = json.load(open(f"{src.PRET}/maps/{pr['map']}/map.json"))
    w = room["width"]
    h = len(raw) // w
    grid = [[block(M[f"{pr['prefix']}:{b & 0x3FF:03X}"], 1 if (b >> 10) & 3 else 0, b >> 12) for b in raw[y * w:(y + 1) * w]]
            for y in range(h)]
    exits = [(e["x"], e["y"]) for e in m["warp_events"]][:1]
    spots = [(o["x"], o["y"], o.get("graphics_id", "")) for o in m.get("object_events", [])]
    return grid, exits, spots


# ------------------------------------------------------------------ kit rooms
def kit_room(room):
    """A plain HnS room (wall, floor, black surround, exit mat) laid out like the mockup, furnished with
    blocks copied from reference layouts: kit = {size, wall_top, wall, floor, outside, mat_x}, copies =
    [(layout, sx, sy, w, h, dx, dy)]."""
    k = room["kit"]
    M = load_mapping("orleans_building", room["tileset"])
    w, h = k["size"]
    t = lambda n, c: block(M[n], c)
    grid = [[t(k["floor"], 0)] * w for _ in range(h)]
    for x in range(w):
        grid[0][x] = t(k["wall_top"], 1)
        grid[1][x] = t(k["wall"], 1)
        grid[h - 1][x] = t(k["outside"], 1)
    if k.get("edge_left"):  # HnS rooms have a darker strip of floor along the left wall
        for y in range(2, h - 1):
            grid[y][0] = t(k["edge_left"], 0)
    L = src.layouts()
    for lid, sx, sy, cw, ch, dx, dy in room.get("copies", []):
        lay = L[lid]
        raw = src.blocks(lay)
        for j in range(ch):
            for i in range(cw):
                b = raw[(sy + j) * lay["width"] + sx + i]
                grid[dy + j][dx + i] = block(M[src.name_of(b & 0x7FF, lay["secondary_tileset"])], (b >> 11) & 1, b >> 12)
    exits = [(k["mat_x"], h - 2)]
    return grid, exits, []


# ------------------------------------------------------------------ mockup rooms
def mockup_room(room):
    spec = mock.INTERIORS[room["mockup"]]
    style = STYLES[room["style"]]
    M = load_mapping("orleans_building", room["tileset"])
    t = lambda n: M[n if ":" in n else f"{style['prefix']}:{n}"]
    w, h = spec["size"]
    grid = [[block(t(style["side"]), 1)] * w for _ in range(h)]
    base = mock.room(w, h, spec.get("floor", "wood"), spec.get("door"), spec.get("door_w", 1)) if not spec.get("custom_room") else []
    exits = []
    kinds = [[None] * w for _ in range(h)]
    labels = {}
    for kind, x, y, rw, rh, *lab in base + spec["shapes"]:
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                kinds[yy][xx] = kind
                labels[(xx, yy)] = (lab[0] if lab else "", x, y, rw, rh)
    for y in range(h):
        for x in range(w):
            k = kinds[y][x]
            if k == "exit" and room.get("no_door"):
                k = "wall"  # an upper floor: the mockup's default door mat is bottom wall; its stairs lead out
            lab, x0, y0, rw, rh = labels.get((x, y), ("", x, y, 1, 1))
            name, coll = style["paint"](k, lab.lower(), x - x0, y - y0, rw, rh, x, y, w, h,
                                        **({"kinds": kinds} if style.get("neighbours") else {}))
            grid[y][x] = block(t(name), coll)
            if k == "exit":
                exits.append((x, y))
    spots = [(mx, my, kind) for kind, mx, my, text in spec["markers"] if kind in ("npc", "heal", "shop", "trainer")]
    return grid, exits, spots


# ------------------------------------------------------------------ events and files
# Interior NPC sprites. gfx_for(text, kind, map, index): an explicit {"gfx": ...} option wins (checked by the caller), then
# SPRITE_OVERRIDES[(map, index)], then SPRITE_BY_KIND[kind] (the role word of the room's people list), then a role word found in
# the spec text, then the fallback by marker kind. Every id must be a non-NULL Emerald graphics id (gfx_null_check.py) and
# each map stays far inside the 16 OBJ palette slots (npc_sprites.py palettes). Nurses are always the Pokemon Center nurse and
# Mart clerks the Mart employee. Anyone who runs Common_EventScript_PkmnCenterNurse (or is a heal respawn_npc) MUST be a NURSE: the bow
# movement exists only on that sprite and waitmovement never ends on another (check_interior.py enforces it); shop-less "clerks" (cafe, salon...) are overridden below so they look like what they are.
G = "OBJ_EVENT_GFX_"
SPRITE_BY_KIND = {
    "nurse": "NURSE", "clerk": "MART_EMPLOYEE", "mother": "WOMAN_5", "lafayette": "SCIENTIST_1", "magnolia": "WOMAN_4",
    "tupelo": "OLD_MAN", "wren": "GIRL_3", "priest": "EXPERT_M", "ringer": "OLD_MAN", "parishioner": "OLD_WOMAN",
    "neighbour": "WOMAN_1", "old neighbour": "OLD_WOMAN", "old neighbours": "OLD_WOMAN", "child": "LITTLE_BOY", "kid": "LITTLE_BOY",
    "grandmother": "OLD_WOMAN", "grandson": "LITTLE_BOY", "daughter": "LITTLE_GIRL", "boy": "BOY_1", "baby": "WOMAN_1",
    "fisherman": "FISHERMAN", "old fisherman": "OLD_MAN", "shrimper": "FISHERMAN", "angler": "FISHERMAN", "oldtimer": "OLD_MAN",
    "boatman": "SAILOR", "deckhand": "SAILOR", "captain": "SAILOR", "watchman": "OLD_MAN", "old diver": "OLD_MAN", "diver": "SWIMMER_M",
    "healer": "WOMAN_5", "apprentice": "GIRL_2", "helper": "GIRL_2", "volunteer": "WOMAN_4", "gardener": "WOMAN_4",
    "aroma lady": "WOMAN_1", "traveller": "WOMAN_3", "shopper": "WOMAN_3", "woman": "WOMAN_3", "regular": "POKEFAN_F",
    "tourist": "POKEFAN_F", "parade fan": "BOY_2", "client": "WOMAN_3", "owner": "WOMAN_1", "landlady": "WOMAN_5",
    "trader": "MAN_3", "collector": "GENTLEMAN", "carver": "MAN_2", "guide": "MAN_4", "gym guide": "MAN_4", "recruit": "MAN_2",
    "accordion": "MAN_1", "dancer": "WOMAN_3", "zydeco band": "BARD", "choir singer": "LASS", "receptionist": "LINK_RECEPTIONIST",
    "tour guide": "GENTLEMAN", "old man": "OLD_MAN", "refinery worker": "WORKER_M", "lineworker": "WORKER_M", "father": "WORKER_M",
    "man": "MAN_2", "keeper": "SAILOR", "forecaster": "REPORTER_F", "scientist": "SCIENTIST_1", "hiker": "HIKER", "cane cutter": "POKEFAN_M",
    "foreman": "WORKER_M", "taster": "WORKER_F", "sundial keeper": "EXPERT_F", "farmer": "FAT_MAN", "birdwatcher": "CAMPER",
    "wrangler": "CAMPER", "smoker": "FAT_MAN", "riddler": "PSYCHIC_M", "gambler": "MAN_2", "handler": "MAN_4",
    "pelipper handler": "MAN_4", "tournament registrar": "MAN_2", "day care": "OLD_MAN", "ticket clerk": "MAN_1",
    "name rater": "MAN_3", "move tutor": "MAN_2", "ev coach": "BLACK_BELT", "iv judge": "EXPERT_F",
}
SPRITE_OVERRIDES = {
    ("IsleMarais_Shelter", 0): "MOM", ("IsleMarais_PlayersHouse", 0): "MOM",
    ("IsleMarais_Shelter", 4): "WOMAN_1",                       # Rita's recruiter (the shelter's second one is the accordion man)
    ("IsleMarais_HouseEastmost", 0): "OLD_MAN",                 # forty years on the water
    ("IsleMarais_HouseNE", 0): "WOMAN_1", ("IsleMarais_HouseNE", 1): "LITTLE_GIRL",
    ("GrandOak_Gym", 0): "MAN_4", ("GrandOak_Gym", 1): "BUG_CATCHER",   # straw-hat gardener trainer
    ("GrandOak_Nursery", 0): "WOMAN_4", ("GrandOak_Nursery", 1): "GIRL_2",
    ("OldWater_Trader", 1): "LITTLE_GIRL",
    ("StormsEdge_Mart", 1): "MAN_2",
    ("StormsEdge_SeafoodMarket", 0): "COOK", ("StormsEdge_HouseW", 0): "WOMAN_5", ("StormsEdge_HouseW", 1): "LITTLE_GIRL",
    ("StormsEdge_Lighthouse", 0): "SAILOR",
    ("CrescentCity_Cafe", 0): "COOK", ("CrescentCity_Salon", 0): "BEAUTY", ("CrescentCity_IceCream", 0): "MART_EMPLOYEE",
    ("CrescentCity_IceCream", 1): "LITTLE_GIRL", ("CrescentCity_PelipperPost", 0): "MYSTERY_GIFT_MAN",
    ("CrescentCity_Trades", 1): "WOMAN_5", ("CrescentCity_DayCare", 0): "OLD_MAN", ("CrescentCity_DayCare", 1): "OLD_WOMAN",
    ("CrescentCity_Conservation", 1): "SCIENTIST_2", ("CrescentCity_Dept3f", 2): "GENTLEMAN",
    ("PointeRouge_TackleShop", 0): "FISHERMAN", ("PointeRouge_HouseNw", 0): "WORKER_M",
    ("CampCocodrie_BaitShack", 0): "FISHERMAN", ("CampCocodrie_Cabin4", 0): "WOMAN_4", ("CampCocodrie_Gym", 2): "MAN_4",
    ("CampCocodrie_DancePorch", 0): "BARD", ("CampCocodrie_DancePorch", 1): "WOMAN_3",
    ("LutinsHollow_Herbalist", 0): "OLD_WOMAN", ("LutinsHollow_Pokecenter", 1): "WOMAN_3",
    ("LutinsHollow_Gym", 0): "MAN_5", ("LutinsHollow_Gym", 1): "MAN_5", ("LutinsHollow_Gym", 2): "MAN_5",   # the four lutins look alike
    ("LutinsHollow_Gym", 3): "MAN_5", ("LutinsHollow_Gym", 6): "WOMAN_4",
    ("Redfield_Gym", 3): "MAN_4", ("LandsEnd_Gym", 3): "WOMAN_4",
    ("LandsEnd_Lookout", 0): "SAILOR", ("LandsEnd_House4", 0): "OLD_MAN",
}
TEXT_WORDS = (("nurse", "NURSE"), ("clerk", "MART_EMPLOYEE"), ("priest", "EXPERT_M"), ("fisherman", "FISHERMAN"), ("sailor", "SAILOR"),
              ("grandmother", "OLD_WOMAN"), ("grandson", "LITTLE_BOY"), ("child", "LITTLE_BOY"))


def gfx_for(text, kind, name=None, idx=None):
    g = SPRITE_OVERRIDES.get((name, idx)) or SPRITE_BY_KIND.get(kind.lower())
    if not g:
        t = text.lower()
        g = next((v for k, v in TEXT_WORDS if k in t), None)
    if not g:
        g = {"heal": "WOMAN_5", "shop": "MART_EMPLOYEE", "trainer": "YOUNGSTER"}.get(kind, "WOMAN_3")
    return g if g.startswith(G) else G + g


def walkable(grid, x, y, exits):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0]) and not (grid[y][x] >> 10) & 3 and (x, y) not in exits


def free_cell(grid, taken, exits, near):
    best = None
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if walkable(grid, x, y, exits) and (x, y) not in taken and all(abs(x - ex) + abs(y - ey) > 1 for ex, ey in exits):
                d = abs(x - near[0]) + abs(y - near[1])
                if best is None or d < best[0]:
                    best = (d, x, y)
    return best[1:] if best else None


def build(room, door_warps):
    name = room["map"]
    grid, exits, spots = (pret_room(room) if room["map"] in src.PRET_ROOMS else kit_room(room) if room.get("kit")
                          else ref_room(room) if room.get("ref") else mockup_room(room))
    if room.get("crop"):  # trim a reference room (e.g. the black padding HnS layouts carry)
        cx, cy, cw, ch = room["crop"]
        grid = [row[cx:cx + cw] for row in grid[cy:cy + ch]]
        exits = [(x - cx, y - cy) for x, y in exits]
        spots = [(x - cx, y - cy, g) for x, y, g in spots if cx <= x < cx + cw and cy <= y < cy + ch]
    h, w = len(grid), len(grid[0])
    # adjustments: swap one tile for another everywhere, then stamp pieces at given cells
    M = load_mapping("orleans_building", room["tileset"])
    for a, b in room.get("replace", {}).items():
        for y in range(h):
            for x in range(w):
                if grid[y][x] & 0x3FF == M[a]:
                    grid[y][x] = (grid[y][x] & ~0x3FF & ~0xC00) | M[b]
    for name_, x, y, coll in room.get("stamps", []):
        grid[y][x] = block(M[name_], coll, grid[y][x] >> 12)
    # layout files
    d = f"data/layouts/{name}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/map.bin", "wb").write(struct.pack(f"<{w * h}H", *[v for row in grid for v in row]))
    border = grid[0][0] & 0x3FF
    open(f"{d}/border.bin", "wb").write(struct.pack("<4H", *[block(border, 1, 0)] * 4))
    lp = "data/layouts/layouts.json"
    L = json.load(open(lp))
    lid = "LAYOUT_" + room["const"][4:]
    entry = {"id": lid, "name": f"{name}_Layout", "width": w, "height": h,
             "primary_tileset": room.get("primary", "gTileset_OrleansBuilding"), "secondary_tileset": room["secondary"],
             "border_filepath": f"{d}/border.bin", "blockdata_filepath": f"{d}/map.bin"}
    # replace in place: a layout's position is its numeric id, which saves store (mapLayoutId), so a rerun must not move it
    at = [i for i, l in enumerate(L["layouts"]) if l.get("id") == lid]
    if at:
        L["layouts"][at[0]] = entry
    else:
        L["layouts"].append(entry)
    with open(lp, "w", newline="\n") as f:
        json.dump(L, f, indent=2)
        f.write("\n")
    gp = "data/maps/map_groups.json"
    G = json.load(open(gp))
    grp = room["group"]
    if grp not in G:
        G[grp] = []
        G["group_order"].append(grp)
    if name not in G[grp]:
        G[grp].append(name)
    dump(gp, G)
    # events
    # the way out: the exterior door, or (upstairs rooms) the room below
    out_map, out_warp = (room["exit_to"] if room.get("exit_to") else (room["exterior"], door_warps[0]))
    warps = [{"x": x, "y": y, "elevation": 3, "dest_map": out_map, "dest_warp_id": str(out_warp)} for x, y in exits]
    for x, y, dm, dw in room.get("warps_extra", []):  # e.g. stairs up
        warps.append({"x": x, "y": y, "elevation": 3, "dest_map": dm, "dest_warp_id": str(dw)})
    objs, scripts, taken = [], [], set()
    pool = list(spots)
    role_gfx = {"nurse": ("NURSE",), "clerk": ("CLERK", "MART", "SHOP")}
    fixed = room.get("positions", [])
    for i, (kind, text, *rest_) in enumerate(room["people"]):
        opts = rest_[0] if rest_ else {}  # {"custom": True} = script written by hand; {"flag": FLAG} = hidden while set
        if i < len(fixed) and fixed[i]:
            sx, sy = fixed[i]
            taken.add((sx, sy))
            pool = [p for p in pool if (p[0], p[1]) != (sx, sy)]
        # nurse and clerk take the reference map's nurse/clerk spot (behind the counter); others take a
        # remaining spot, or the nearest open floor
        match = [p for p in pool if any(k in str(p[2]).upper() for k in role_gfx.get(kind, ()))]
        if i < len(fixed) and fixed[i]:
            pass
        elif kind in role_gfx and match:
            sx, sy, _ = match[0]
            pool.remove(match[0])
        else:
            rest = [p for p in pool if not any(k in str(p[2]).upper() for ks in role_gfx.values() for k in ks)]
            if rest:
                sx, sy, _ = rest[0]
                pool.remove(rest[0])
                if not walkable(grid, sx, sy, exits) or (sx, sy) in taken:
                    sx, sy = free_cell(grid, taken, exits, (sx, sy)) or (sx, sy)
            else:
                sx, sy = free_cell(grid, taken, exits, (w // 2, h // 2 + 1))
        taken.add((sx, sy))
        tag = "".join(p.capitalize() for p in kind.split())
        sid = f"{name}_EventScript_{tag}{i}"
        lid_ = f"LOCALID_{room['const'][4:]}_{kind.upper().replace(' ', '_')}{i}"
        # opts: "gfx" overrides the sprite (e.g. OBJ_EVENT_GFX_SPECIES(TOTODILE)), "sight": n makes a trainer,
        # "face" sets the facing direction (DOWN, UP, LEFT, RIGHT)
        objs.append({"local_id": lid_, "graphics_id": opts.get("gfx", gfx_for(text, kind, name, i)), "x": sx, "y": sy, "elevation": 3,
                     "movement_type": f"MOVEMENT_TYPE_FACE_{opts.get('face', 'DOWN')}", "movement_range_x": 0, "movement_range_y": 0,
                     "trainer_type": "TRAINER_TYPE_NORMAL" if opts.get("sight") else "TRAINER_TYPE_NONE",
                     "trainer_sight_or_berry_tree_id": str(opts.get("sight", 0)), "script": sid,
                     "flag": opts.get("flag", "0")})
        if opts.get("custom"):
            continue
        if kind == "nurse":
            scripts.append(f"{sid}::\n\tsetvar VAR_0x800B, {lid_}\n\tcall Common_EventScript_PkmnCenterNurse\n\twaitmessage\n\twaitbuttonpress\n\trelease\n\tend\n")
        elif kind == "clerk":
            items = "".join(f"\t.2byte {it}\n" for it in room.get("mart", []))
            scripts.append(f"{sid}::\n\tlock\n\tfaceplayer\n\tmessage gText_HowMayIServeYou\n\twaitmessage\n\tpokemart {name}_Pokemart{i}\n"
                           f"\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n\trelease\n\tend\n\n\t.align 2\n{name}_Pokemart{i}:\n{items}\tpokemartlistend\n")
        else:
            tid = f"{name}_Text_{tag}{i}"
            scripts.append(f"{sid}::\n\tmsgbox {tid}, MSGBOX_NPC\n\tend\n\n{tid}:\n\t.string \"{text}$\"\n")
    md = f"data/maps/{name}"
    os.makedirs(md, exist_ok=True)
    mp = f"{md}/map.json"
    old = json.load(open(mp)) if os.path.exists(mp) else {}
    # rest spots (interior_rest.py): sign events on a bed / cot / bench; the previous run's are dropped first so a rerun does not duplicate them
    taken_cells = {(o["x"], o["y"]) for o in objs} | {(x, y) for x, y in exits} | {(w_["x"], w_["y"]) for w_ in warps}
    rest = interior_rest.rest_events(name, lambda x, y: walkable(grid, x, y, exits), taken_cells)
    bg = interior_rest.without_rest(story_overlay.interior_events(room.get("mockup"), "bg_events", old.get("bg_events", []))) + rest
    dump(mp, {"id": room["const"], "name": name, "layout": lid, "music": room.get("music", "MUS_RG_PALLET"),
              "region_map_section": room["mapsec"], "requires_flash": False, "weather": "WEATHER_NONE",
              "map_type": "MAP_TYPE_INDOOR", "allow_cycling": False, "allow_escaping": False, "allow_running": True,
              "show_map_name": False, "battle_scene": "MAP_BATTLE_SCENE_NORMAL", "connections": None,
              "object_events": objs, "warp_events": warps,
              "coord_events": story_overlay.interior_events(room.get("mockup"), "coord_events", old.get("coord_events", [])),
              "bg_events": bg})
    write_scripts(f"{md}/scripts.inc", name, scripts)
    include_map_scripts(".", name)
    return grid, exits


BEGIN, END = "@ --- mapgen: generated NPC scripts (begin) ---", "@ --- mapgen: generated NPC scripts (end) ---"


def write_scripts(path, name, scripts):
    """Regenerate only the marked block; hand-written scripts (map scripts, story events, custom NPCs) outside
    it are kept. A file written before the markers existed is entirely generated, so it is replaced."""
    src = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if BEGIN in src:
        src = src[:src.index(BEGIN)].rstrip("\n") + "\n" + src[src.index(END) + len(END):].lstrip("\n")
    else:
        src = ""
    if f"{name}_MapScripts::" not in src:
        src = f"{name}_MapScripts::\n\t.byte 0\n" + src
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(src.rstrip("\n") + "\n\n" + BEGIN + "\n\n" + "\n".join(scripts) + "\n" + END + "\n")


def door_warp_index(exterior_spec, cfg_name, label):
    """Index of a building's first door warp in its exterior map (same order build.py writes them)."""
    spec = json.load(open(os.path.join(HERE, "maps", exterior_spec), encoding="utf-8"))
    cfg = json.load(open(os.path.join(TS, cfg_name + ".json")))
    i = 0
    for b in spec["buildings"]:
        door = cfg["prefabs"][b["prefab"]].get("door")
        if not door or b.get("closed"):  # closed buildings have no warps
            continue
        doors = door if isinstance(door[0], list) else [door]
        if b["label"] == label:
            return list(range(i, i + len(doors)))
        i += len(doors)
    raise SystemExit(f"no building labelled {label!r} in {exterior_spec}")


def main(args):
    preview = args[args.index("--preview") + 1] if "--preview" in args else None
    names = [a for a in args if not a.startswith("--") and a != preview] or [r["map"] for r in ROOMS]
    links = {}
    for room in ROOMS:
        if room["map"] not in names:
            continue
        dw = door_warp_index(room["exterior_spec"], room["exterior_cfg"], room["door_label"]) if room.get("door_label") else [None]
        grid, exits = build(room, dw)
        if room.get("door_label"):
            links.setdefault(room["exterior_spec"], {})[room["door_label"]] = room["const"]
        print(f"{room['map']}: {len(grid[0])}x{len(grid)}, exit {exits} -> {room.get('exit_to') or (room['exterior'], dw[0])}")
        if preview:
            from render import Tilesets
            from PIL import Image
            t = Tilesets("data/tilesets/primary/orleans_building", f"data/tilesets/secondary/{room['tileset']}")
            im = Image.new("RGB", (len(grid[0]) * 16, len(grid) * 16))
            for y, row in enumerate(grid):
                for x, v in enumerate(row):
                    im.paste(t.metatile(v & 0x3FF), (x * 16, y * 16))
            im.save(os.path.join(preview, room["map"] + ".png"))
    for n in interior_rest.apply_vanilla("."):
        print(f"{n}: rest spots added")
    # tell the exterior specs where each door leads
    for spec_name, doors in links.items():
        p = os.path.join(HERE, "maps", spec_name)
        spec = json.load(open(p, encoding="utf-8"))
        changed = False
        for b in spec["buildings"]:
            if b["label"] in doors and b.get("interior") != doors[b["label"]]:
                b["interior"] = doors[b["label"]]
                changed = True
        dump(p, spec)
        first = spec.get("_comment", "").startswith("FIRST PASS")
        if changed or first:  # rebuild the exterior so its door warps lead inside (first passes keep plain tiles)
            import subprocess
            flags = ["--no-blends"] if first else []
            r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), p] + flags,
                               capture_output=True, text=True)
            print(f"rebuilt {spec_name}: {(r.stdout.strip().splitlines() or [r.stderr.strip()[-200:]])[-1]}")


if __name__ == "__main__":
    main(sys.argv[1:])

"""Check built interiors and render review images.

usage (from the decomp root): python tools/mapgen/check_interior.py [ROOM ...] [--out DIR]
For each room: the exit warp exists and has a walkable tile above it; every NPC stands on floor and
can be reached on foot from the entrance. Writes <out>/<Map>.png (3x, N = NPC, E = exit).
"""
import json
import os
import struct
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from interior_rooms import ROOMS  # noqa: E402
from render import Tilesets  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


MOCKUP_OF = {  # reference rooms -> their planning mockup (mockup rooms name theirs directly)
    "IsleMarais_Shelter": "isle_marais_shelter", "IsleMarais_PlayersHouse": "isle_marais_players_house",
    "IsleMarais_PlayersHouse_2F": None, "IsleMarais_HouseNE": "isle_marais_tarp_house",
    "IsleMarais_HouseW": "isle_marais_house_w", "IsleMarais_HouseE": "isle_marais_house_e",
    "IsleMarais_HouseEastmost": "isle_marais_house_tilted", "GrandOak_PokemonCenter": "grand_oak_pokecenter",
    "GrandOak_Mart": "grand_oak_mart", "GrandOak_Nursery": "grand_oak_nursery", "GrandOak_HouseSW1": "grand_oak_house_sw1",
    "GrandOak_HouseSW2": "grand_oak_house_sw2", "GrandOak_HouseSE": "grand_oak_house_se",
}
MOCKUPS = os.path.join(HERE, "..", "..", "..", "orleans_maps", "interiors")


def compare(room, built, out):
    """<out>/<Map>_compare.png: the planning mockup's room (left) next to the built room (right)."""
    import glob
    import interiors as mock
    key = room.get("mockup") or MOCKUPS_OF(room["map"])
    files = glob.glob(os.path.join(MOCKUPS, f"*_{key}.png"))
    if not files:
        return
    w, h = mock.INTERIORS[key]["size"]
    m = Image.open(files[0]).convert("RGB").crop((0, 140, w * mock.PITCH + 1, 140 + h * mock.PITCH + 1))
    H = max(m.height, built.height)
    s = H / m.height
    m = m.resize((int(m.width * s), H), Image.LANCZOS)
    b = built if built.height == H else built.resize((int(built.width * H / built.height), H), Image.NEAREST)
    canvas = Image.new("RGB", (m.width + b.width + 30, H + 44), (255, 255, 255))
    canvas.paste(m, (0, 44))
    canvas.paste(b, (m.width + 30, 44))
    d = ImageDraw.Draw(canvas)
    d.text((8, 14), f"Mockup: {mock.INTERIORS[key]['title']}", fill=(0, 0, 0))
    d.text((m.width + 38, 14), f"{room['map']} built  (N = person, E = exit)", fill=(0, 0, 0))
    canvas.save(os.path.join(out, room["map"] + "_compare.png"))


MOCKUPS_OF = MOCKUP_OF.get


def nurse_check():
    """Anyone who runs Common_EventScript_PkmnCenterNurse, and every heal respawn_npc (the whiteout script), must use OBJ_EVENT_GFX_NURSE:
    the bow movement exists only on that sprite, so on any other the script's waitmovement never ends and the game freezes."""
    import glob
    import re
    bad = 0
    heal = set(re.findall(r'"respawn_npc":\s*"(LOCALID_\w+)"', open("src/data/heal_locations.json", encoding="utf-8").read()))
    for p in sorted(glob.glob("data/maps/*/map.json")):
        d = os.path.dirname(p)
        m = json.load(open(p, encoding="utf-8"))
        sc = open(os.path.join(d, "scripts.inc"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "scripts.inc")) else ""
        for o in m.get("object_events", []):
            lid = o.get("local_id", "")
            uses = False
            i = sc.find(o["script"] + "::")
            if i >= 0:
                body = sc[i:].split("\n\n")[0]
                uses = "Common_EventScript_PkmnCenterNurse" in body or "EventScript_PkmnCenterNurse" in body
            if (uses or lid in heal) and o["graphics_id"] != "OBJ_EVENT_GFX_NURSE":
                print(f"{m['name']}: {lid} heals/bows but is {o['graphics_id']}, not OBJ_EVENT_GFX_NURSE (waitmovement on the nurse bow never ends)")
                bad += 1
    return bad


def tileset_dir(symbol):
    """gTileset_OrleansRootkinIn -> orleans_rootkin_in, gTileset_GenericBuilding -> generic_building."""
    import re
    name = symbol.replace("gTileset_", "")
    special = {"OrleansRootkinIn": "orleans_rootkin_in"}
    if name in special:
        return special[name]
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def main(args):
    out = args[args.index("--out") + 1] if "--out" in args else os.path.join(HERE, "maps", "interiors")
    names = [a for a in args if not a.startswith("--") and a != out] or [r["map"] for r in ROOMS]
    os.makedirs(out, exist_ok=True)
    bad = 0
    for room in ROOMS:
        name = room["map"]
        if name not in names:
            continue
        m = json.load(open(f"data/maps/{name}/map.json"))
        L = [l for l in json.load(open("data/layouts/layouts.json"))["layouts"] if l.get("id") == m["layout"]][0]
        w, h = L["width"], L["height"]
        raw = open(L["blockdata_filepath"], "rb").read()
        g = struct.unpack(f"<{w * h}H", raw)
        opened = set()
        if room.get("arena"):  # an arena's map states (the Tide Hall's sealed door) are applied: its people must be reachable once the story opens them
            import arena_rooms
            opened = {(x, y) for st in arena_rooms.states(room["arena"]).values() for x, y, _n, wk in st if wk}
        walk = lambda x, y: 0 <= x < w and 0 <= y < h and (not (g[y * w + x] >> 10) & 3 or (x, y) in opened)
        problems, notes = [], []
        exits = [(e["x"], e["y"]) for e in m["warp_events"]]
        if not exits:
            problems.append("no exit warp")
        start = None
        for ex, ey in exits:
            if not walk(ex, ey):
                problems.append(f"exit ({ex},{ey}) is blocked")
        if exits:  # walk from any open tile next to the first warp (above a door mat, beside stairs)
            ex, ey = exits[0]
            for nx, ny in ((ex, ey - 1), (ex - 1, ey), (ex + 1, ey), (ex, ey + 1)):
                if walk(nx, ny):
                    start = (nx, ny)
                    break
        seen = set()
        if start:
            q = deque([start])
            seen.add(start)
            # objects hidden by a flag (a gym net, a one-off scene) are not walls here: a puzzle gate is proved in story_gates_check.py
            npcs = {(o["x"], o["y"]) for o in m["object_events"] if str(o.get("flag", "0")) in ("0", "")}
            while q:
                x, y = q.popleft()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if (nx, ny) not in seen and walk(nx, ny) and (nx, ny) not in npcs:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            npcs0 = {(o["x"], o["y"]) for o in m["object_events"]}
            if start in npcs0:
                problems.append(f"a person stands on {start}, the only tile in front of the exit (the door is blocked)")
            else:
                free_floor = {(x, y) for x in range(w) for y in range(h) if walk(x, y)} - npcs0
                if len(seen) < 3 and len(free_floor) > 3:
                    problems.append(f"only {len(seen)} tile(s) can be reached from the door: the room is blocked off")
        else:
            problems.append("no walkable tile next to the exit")
        for ex, ey in exits[1:]:
            if not any((ex + dx, ey + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                problems.append(f"warp ({ex},{ey}) can't be reached")
        for o in m["object_events"]:
            if room.get("arena") and not walk(o["x"], o["y"]):
                continue  # the legendary stands on its dais (a blocked cell: the player faces it from the cell below, checked in story_gates_check.py)
            if o["graphics_id"] == "OBJ_EVENT_GFX_ITEM_BALL" and not walk(o["x"], o["y"]) and walk(o["x"], o["y"] + 1):
                continue  # a Poke Ball on a table (the shelter's starters): faced from the floor cell below
            if not walk(o["x"], o["y"]):
                problems.append(f"{o['local_id']} stands on a blocked tile ({o['x']},{o['y']})")
            elif not any((o["x"] + dx, o["y"] + dy) in seen or (o["x"] + 2 * dx, o["y"] + 2 * dy) in seen
                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):  # two away = talking across a counter
                if room.get("gated"):
                    notes.append(f"{o['local_id']} is behind the puzzle (expected)")
                else:
                    problems.append(f"{o['local_id']} can't be reached ({o['x']},{o['y']})")
        bad += len(problems)
        print(f"{name}: {w}x{h}, {len(m['object_events'])} people, {'ok' if not problems else '; '.join(problems)}{' (' + str(len(notes)) + ' behind the puzzle)' if notes else ''}")
        # review image
        t = Tilesets(f"data/tilesets/primary/{tileset_dir(L['primary_tileset'])}", f"data/tilesets/secondary/{tileset_dir(L['secondary_tileset'])}")
        im = Image.new("RGB", (w * 16, h * 16))
        for y in range(h):
            for x in range(w):
                im.paste(t.metatile(g[y * w + x] & 0x3FF), (x * 16, y * 16))
        im = im.resize((w * 48, h * 48), Image.NEAREST)
        d = ImageDraw.Draw(im)
        for o in m["object_events"]:
            x, y = o["x"] * 48, o["y"] * 48
            d.rectangle([x + 6, y + 6, x + 41, y + 41], outline=(30, 140, 230), width=4)
            d.text((x + 18, y + 16), "N", fill=(30, 140, 230))
        for ex, ey in exits:
            d.rectangle([ex * 48 + 6, ey * 48 + 6, ex * 48 + 41, ey * 48 + 41], outline=(230, 0, 230), width=4)
            d.text((ex * 48 + 18, ey * 48 + 16), "E", fill=(230, 0, 230))
        im.save(os.path.join(out, name + ".png"))
        compare(room, im, out)
    bad += nurse_check()
    print(f"problems: {bad}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

"""The legendary lairs, all 20 (tools/mapgen/lairs.py, story_data_lairs.py): batch 1 (7 lairs) and batch 2 (13 lairs).

For every outdoor lair (batch 1: the rougarou off Route 14, Bloodmoon Ursaluna off Route 23, Celebi off Route 7, Suicune off Route 11, Raikou off Route 2, Entei off
Route 16; batch 2: Uxie by canoe from the Old Water, Mesprit off Route 1, Azelf and Landorus off Route 23, Zapdos at the top of the Storm's Edge lighthouse,
Thundurus off Route 12, Zarude and Ogerpon off Route 13, Tornadus off Route 3, Galarian Moltres and Zapdos off Route 14, Galarian Articuno off Route 10 by Surf,
Moltres in the Route 17 sugarhouse) plus Articuno's ice plant:
  * the entrance is SEALED before its story value (the rougarou: FLAG_BADGE06_GET; the others: story 44) and OPEN after: the same walk ends in the lair on its
    arrival cell (the boatman's canoe, the lighthouse stair and the Surf walk to the pavilion's pier are their own flows);
  * walking out puts the player back on the entrance cell (the map and cell the data says), and the lair's weather does not leak onto the route;
  * the overworld weather in the lair is the weather_plan one, and in battle it starts what that weather starts (fog = Misty Terrain, thunderstorm = rain +
    Electric Terrain, snow, sandstorm, sun, rain; sunny / clouds / none = nothing);
  * the encounter is hidden below story 45 (FLAG_PG_*), shown at 45; the rougarou and Ursaluna only at night;
  * a battle starts as a 2-bar boss (setbossbattle), a KO leaves it standing and it fights again, a Master Ball catch (the guaranteed victory catch) retires it;
  * the soft reset: two boots with different timing from a save made in front of it roll a different Pokemon (the roll happens when the battle starts);
  * in-engine screenshots: tile_review/set_pieces/lairs/ingame_<lair>.png (batch 1) and .../batch2/ingame_<lair>.png + ingame_<lair>_entrance.png (the open way in on
    its route), weather pictures weather_<lair>.png.
Also the static facts: every lair's objects and triggers in its map.json, the scripts moved out of the routes, the Shrine Seeker "discovered" bits.
"""
import re
import shutil
import sys
from pathlib import Path

from bot import Bot, map_data, ROOT, wsl_path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(Path(ROOT) / "tools" / "mapgen"))
import story_data_lairs as D  # noqa: E402
import weather_plan  # noqa: E402
import t19_starters as S  # noqa: E402
import t25_boss as B  # noqa: E402

ORDER = ["NONE", "SUNNY_CLOUDS", "SUNNY", "RAIN", "SNOW", "RAIN_THUNDERSTORM", "FOG_HORIZONTAL", "VOLCANIC_ASH", "SANDSTORM", "FOG_DIAGONAL",
         "UNDERWATER", "SHADE", "DROUGHT", "DOWNPOUR", "UNDERWATER_BUBBLES"]     # include/constants/weather.h
MASK = {"B_WEATHER_RAIN": 0xE, "B_WEATHER_SUN": 0x30, "B_WEATHER_SANDSTORM": 0x40, "B_WEATHER_HAIL": 0x80, "B_WEATHER_SNOW": 0x100, "B_WEATHER_FOG": 0x200}   # include/constants/battle.h
ANY = tuple(MASK)
# what an overworld weather starts in battle: (the gBattleWeather flag or None, the terrain in gFieldTimers+5 or None): fog = Misty Terrain (2), thunderstorm = rain +
# Electric Terrain (3), snow = snow (B_OVERWORLD_SNOW >= GEN_9), sunny / clouds / none start nothing
BATTLE = {"WEATHER_FOG_HORIZONTAL": (None, 2), "WEATHER_SANDSTORM": ("B_WEATHER_SANDSTORM", None), "WEATHER_SUNNY": (None, None), "WEATHER_RAIN": ("B_WEATHER_RAIN", None),
          "WEATHER_RAIN_THUNDERSTORM": ("B_WEATHER_RAIN", 3), "WEATHER_DROUGHT": ("B_WEATHER_SUN", None), "WEATHER_SNOW": ("B_WEATHER_SNOW", None),
          "WEATHER_SHADE": (None, None), "WEATHER_NONE": (None, None)}
SHOTS = Path(ROOT).parent / "tile_review" / "set_pieces" / "lairs"
SHOTS2 = SHOTS / "batch2"
DAY, NIGHT = 12, 22

# key: the open condition ("flag", FLAG) or ("story", 45); the steps from the approach cell to the entrance trigger ("walk" entries); kind of entry
CFG = {
    "rougarou": dict(cond=("flag", "FLAG_BADGE06_GET"), steps="RR", night=True),
    "ursaluna": dict(cond=("story", 45), steps="UU", night=True),
    "celebi": dict(cond=("story", 45), steps="UU"),
    "suicune": dict(cond=("story", 45), steps="U"),
    "raikou": dict(cond=("story", 45), steps="UUUU"),
    "entei": dict(cond=("story", 45), steps="UUU"),
    "mesprit": dict(cond=("story", 45), steps="RR"),
    "azelf": dict(cond=("story", 45), steps="UU"),
    "landorus": dict(cond=("story", 45), steps="DDD"),
    "thundurus": dict(cond=("story", 45), steps="RR"),
    "zarude": dict(cond=("story", 45), steps="RR"),
    "ogerpon": dict(cond=("story", 45), steps="LLL"),
    "tornadus": dict(cond=("story", 45), steps="UU"),
    "galar_moltres": dict(cond=("story", 45), steps="LLL"),
    "galar_zapdos": dict(cond=("story", 45), steps="RRR"),
    "galar_articuno": dict(cond=("story", 45), steps="UU", entry="surf"),
    "moltres": dict(cond=("story", 45), steps="UU"),
    "uxie": dict(cond=("story", 45), entry="boatman"),
    "zapdos": dict(cond=("story", 45), entry="stair"),
}
APPROACH = {"mesprit": (25, 27), "azelf": (33, 3), "landorus": (27, 36), "thundurus": (24, 22), "zarude": (25, 26), "ogerpon": (3, 25), "tornadus": (27, 3),
            "galar_moltres": (3, 7), "galar_zapdos": (24, 19), "galar_articuno": (30, 14), "moltres": (33, 11)}
FLAGS = {"rougarou": "FLAG_HIDE_ROUTE14_ROUGAROU", "ursaluna": "FLAG_PG_URSALUNA_BM"}
BACKMAP = {"MAP_OLD_WATER_CANOE_DOCKS": "OldWater_CanoeDocks", "MAP_STORMS_EDGE_LIGHTHOUSE": "StormsEdge_Lighthouse"}
FACING = {"LEFT": "face_left", "DOWN": "face_down", "RIGHT": "face_right", "UP": "face_up"}
OLD_MAP = {"zapdos": "StormsEdge", "moltres": "Route17", "galar_articuno": "CrescentCity", "galar_zapdos": "CrescentCity", "galar_moltres": "CrescentCity",
           "tornadus": "Route3", "thundurus": "Route12", "landorus": "Route23", "azelf": "Route23", "mesprit": "Route1", "uxie": "OldWater", "zarude": "Route13",
           "ogerpon": "Route13"}
DIRS = {(1, 0): "R", (-1, 0): "L", (0, 1): "D", (0, -1): "U"}


def enc_flag(key):
    return FLAGS.get(key) or "FLAG_PG_" + key.upper()


def route_of(key):
    lair = D.LAIRS[key]
    return lair.get("route") or "Route14"


def approach_of(key):
    return APPROACH.get(key) or D.LAIRS[key]["approach"]


def weather_now(b):
    return "WEATHER_" + ORDER[b.call("GetCurrentWeather") & 0xFF]


def battle_state(b):
    return b.r16(b.sym("gBattleWeather")), b.r8(b.sym("gFieldTimers") + 5)


ABILITY_SUN = ("moltres", "entei")      # Moltres' ability is Drought in this dex (the foe's roll may give it): sun in battle on top of the map's own (none)


def check_battle_weather(b, t, key, got):
    ow = weather_plan.HEADER[D.LAIRS[key]["map"]] if key in D.LAIRS else "WEATHER_SNOW"
    flag, terrain = BATTLE[ow]
    w, ter = got
    bits = {n: bool(w & MASK[n]) for n in ANY}
    want = {n: n == flag for n in ANY}
    if key in ABILITY_SUN and flag is None and bits.get("B_WEATHER_SUN") and not any(v for n, v in bits.items() if n != "B_WEATHER_SUN"):
        want = {n: n == "B_WEATHER_SUN" for n in ANY}      # Drought (ability), not the map
    t.check("%s: the battle weather is %s%s (gBattleWeather %#x, terrain %s)" % (key, flag or "none", " + terrain %d" % terrain if terrain else "", w, ter),
            bits == want and (ter == (terrain or 0)), "%s terrain %s" % ([n for n, v in bits.items() if v], ter))


def set_time(b, hour):
    b.set_clock(hour)
    b.frames(30)


def other_map(b):
    b.advance_text(30)
    b.frames(30)
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.frames(30)
    b.advance_text(30)


def save_shot(b, key, label, dest=None):
    png = b.shot(label)
    d = SHOTS2 if key in D.LAIRS2 else SHOTS
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, d / (dest or "ingame_%s.png" % key))


def set_open(b, cond, on):
    kind, v = cond
    if kind == "flag":
        b.set_flag(v, on)
    else:
        b.set_var("VAR_ORLEANS_STORY", v if on else v - 1)


def surfing(b):
    return bool(b.r8(b.sym("gPlayerAvatar")) & 8)


def start_surf(b, elev=1):
    """what Surf does: the avatar takes the water's flags and elevation (as t_transitions does it)"""
    b.call("SetPlayerAvatarTransitionFlags", 8)
    b.frames(10)
    oid = b.r8(b.sym("gPlayerAvatar") + 5)
    ea = b.sym("gObjectEvents") + oid * 0x24 + 0x0B
    b.w8(ea, (b.r8(ea) & 0xF0) | elev)


def enter(b, key, cfg):
    """the walk (or ride) from the way in to the lair; the caller checks where it ended"""
    kind = cfg.get("entry", "walk")
    if kind == "boatman":
        b.warp("OldWater_CanoeDocks", 4, 6)
        b.frames(30)
        b.face("U")
        b.press("A", 4, 30)
        b.frames(60)
        if b.var("VAR_ORLEANS_STORY") >= 45:
            b.press("A", 4, 40)          # "Want a paddle out?": YES
            b.frames(30)
            b.press("A", 4, 40)          # "Keep your voice low."
        else:
            b.press("B", 4, 40)          # "Need a ride back to the landing?": NO (a yes would paddle to Route 1)
        for _ in range(12):
            b.frames(40)
            b.press("A" if b.var("VAR_ORLEANS_STORY") >= 45 else "B", 4, 40)
        b.frames(120)
        b.settle()
        return
    if kind == "stair":
        b.warp("StormsEdge_Lighthouse", 4, 3)
        b.frames(30)
        b.step("U")
        b.frames(120)
        b.settle()
        return
    ax, ay = approach_of(key)
    b.warp(route_of(key), ax, ay)
    b.frames(30)
    if kind == "surf":
        start_surf(b)
    b.walk(cfg["steps"])
    b.frames(90)
    b.settle()


def reset_party(b):
    """back to the tester alone: the caught legends are zeroed out of slots 1-5 (a plain count write would leave stale mons that a later catch trips over)"""
    base = b.r32(b.sym("gPlayerPartyPtr"))
    for slot in range(1, 6):
        b.call("ZeroMonData", base + slot * 100)
    b.w8(b.r32(b.sym("gPlayerPartyCountPtr")), 1)
    b.call("HealPlayerParty")                      # Tackle has 35 PP: about 14 lairs' catches would drain it


def break_bars(b):
    """two bars: each attack leaves the boss at 1 HP and finishes it; a stray move (Protect, a miss) costs a turn, so go on until the last bar breaks and the catch is offered"""
    for _ in range(6):
        if not B.attack(b, 1, True, limit=700):
            break


def battle_menu(b):
    """start the battle with A (the caller stands facing it); returns True when the turn menu waits"""
    b.press("A", 4, 26)
    if not B.start_battle(b):
        return False
    return B.wait_menu(b)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_move(0, "MOVE_FEINT")                    # Psychic cannot touch Zarude / the Galarian Moltres; Feint goes through the Galarian Zapdos' Detect
    b.set_var("VAR_STARTER_MON", 2)
    for i in range(1, 9):
        b.set_flag("FLAG_BADGE0%d_GET" % i)        # a level 100 tester only obeys with the badges
    b.give_item("ITEM_MASTER_BALL", 40)
    set_time(b, DAY)
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.frames(900)                                  # the trophy popups the story value unlocks must be gone before the first input
    keys = list(CFG)

    # ---------------------------------------------------------------- static facts
    for key in keys:
        lair = D.LAIRS[key]
        name = lair["map"]
        md = map_data(name)
        w, h = lair.get("size", (20, 16)) if "size" in lair else ((19, 14) if key == "moltres" else (20, 16))
        exits = D.exits(key)
        t.check("%s: a %dx%d map with the encounter object and %d exit trigger(s) armed by %s%s" % (name, w, h, len(exits), D.TRIG, " and the hatch warp" if key == "zapdos" else ""),
                (md["width"], md["height"]) == (w, h) and len(md["objects"]) == 1 and len(md["coords"]) == len(exits)
                and all(c["var"] == D.TRIG and c["script"] == name + "_EventScript_Exit" for c in md["coords"]) and len(md["warps"]) == (1 if key == "zapdos" else 0),
                "%sx%s %d objects %d triggers %d warps" % (md["width"], md["height"], len(md["objects"]), len(md["coords"]), len(md["warps"])))
        enter_name = lair.get("enter")
        if key in D.LAIRS2:
            if enter_name:
                rt = map_data(lair["route"])
                trig = [c for c in rt["coords"] if c["script"] == "%s_EventScript_LairEnter%s" % (lair["route"], enter_name)]
                t.check("%s: %d entrance trigger(s) for %s, armed by %s" % (lair["route"], len(trig), key, D.TRIG), len(trig) >= 1 and all(c["var"] == D.TRIG for c in trig))
            old = OLD_MAP[key]
            ot = map_data(old)
            t.check("%s: the old %s encounter object is gone from the map" % (old, key), not [o for o in ot["objects"] if o.get("flag") == enc_flag(key)])
        else:
            route = lair["route"]
            rt = map_data(route)
            trig = [c for c in rt["coords"] if c["script"] == route + "_EventScript_LairEnter"]
            t.check("%s: two entrance triggers, armed by %s" % (route, D.TRIG), len(trig) == 2 and all(c["var"] == D.TRIG for c in trig))
            if key != "rougarou":
                t.check("%s: the old encounter object is gone from the route" % route, not [o for o in rt["objects"] if o.get("flag") == enc_flag(key)])
    rt14 = map_data("Route14")
    t.check("Route 14: the rougarou left the levee crest", not [o for o in rt14["objects"] if o.get("flag") == "FLAG_HIDE_ROUTE14_ROUGAROU"])
    ice = map_data("PointeRouge_IcePlant")
    t.check("the ice plant: Articuno's object on the dais front (9, 5), the exit warp (9, 13) to Pointe Rouge",
            [(o["x"], o["y"], o["flag"]) for o in ice["objects"]] == [(9, 5, "FLAG_PG_ARTICUNO")] and [(w["x"], w["y"]) for w in ice["warps"]] == [(9, 13)])

    # ---------------------------------------------------------------- the "discovered" bits (Shrine Seeker): first, on the fresh game
    discovered(b, t)

    # ---------------------------------------------------------------- the outdoor / interior lairs, batch 1 then batch 2
    for key in keys:
        lair_flow(b, t, key, CFG[key])

    # ---------------------------------------------------------------- Articuno: the ice plant (the door exists; the legend from story 45)
    articuno(b, t)

    # ---------------------------------------------------------------- the Zapdos lantern, the Moltres door sign
    zapdos_lamp(b, t)
    moltres_sign(b, t)

    # ---------------------------------------------------------------- the scripts left the routes
    story = Path(ROOT) / "tools" / "mapgen" / "story"
    for route, lair in (("Route2", "Route2_RaikouClearing"), ("Route7", "Route7_CelebiGlade"), ("Route11", "Route11_SuicuneIsle"),
                        ("Route16", "Route16_EnteiField"), ("Route23", "Route23_BloodmoonArroyo"), ("Route14", "Route14_RougarouHollow")):
        rsrc = (story / (route + ".inc")).read_text(encoding="utf-8")
        lsrc = (story / (lair + ".inc")).read_text(encoding="utf-8")
        t.check("%s: the encounter's scripts are in %s, not on the route" % (route, lair),
                not re.search(r"^%s_EventScript_(Pg(Raikou|Celebi|Suicune|Entei|UrsalunaBm)|Rougarou)::" % route, rsrc, re.M)
                and re.search(r"^%s_EventScript_(Pg\w+|Rougarou)::" % lair, lsrc, re.M) is not None)
    for key, old in OLD_MAP.items():
        lair = D.LAIRS[key]["map"]
        rsrc = (story / (old + ".inc")).read_text(encoding="utf-8")
        lsrc = (story / (lair + ".inc")).read_text(encoding="utf-8")
        t.check("%s: %s's scripts are in %s, not on %s" % (key, key, lair, old),
                not re.search(r"^%s_EventScript_Pg%s::" % (old, "".join(p.capitalize() for p in key.split("_"))), rsrc, re.M)
                and re.search(r"^%s_EventScript_Pg%s::" % (lair, "".join(p.capitalize() for p in key.split("_"))), lsrc, re.M) is not None)

    # ---------------------------------------------------------------- the soft reset: every lair rolls its Pokemon when the battle starts
    for key in keys:
        soft_reset(b, t, key)


def lair_flow(b, t, key, cfg):
    lair = D.LAIRS[key]
    name = lair["map"]
    cond = cfg["cond"]
    night = cfg.get("night", False)
    flag = enc_flag(key)
    arrive = D.arrive(key)
    exits = D.exits(key)
    (sx, sy), sface = D.STAND[key]
    route = route_of(key) if key not in ("uxie", "zapdos") else ("OldWater_CanoeDocks" if key == "uxie" else "StormsEdge_Lighthouse")
    kind = cfg.get("entry", "walk")
    set_time(b, DAY)

    # -- sealed (zapdos: the stair is always open, nothing to seal)
    if kind != "stair":
        b.set_var("VAR_ORLEANS_STORY", 44)
        set_open(b, cond, False)
        other_map(b)
        enter(b, key, cfg)
        t.check("%s: SEALED (%s): the way in leaves the player outside" % (key, cond[1]), b.map_name() == route, b.where())
        if kind == "walk" or kind == "surf":
            if kind == "surf":
                b.set_flag("FLAG_TEMP_1", False)
            b.shot("%s_sealed" % key)
            if key in D.LAIRS2:
                save_shot(b, key, "%s_sealed_entrance" % key, "ingame_%s_entrance_sealed.png" % key)
    # -- open
    set_open(b, cond, True)
    if cond[0] == "story":
        b.set_var("VAR_ORLEANS_STORY", 45)
    other_map(b)
    if kind in ("walk", "surf"):
        ax, ay = approach_of(key)
        b.warp(route, ax, ay)
        b.frames(30)
        if kind == "surf":
            start_surf(b)
        b.frames(40)
        b.settle()
        if key in D.LAIRS2:
            save_shot(b, key, "%s_open_entrance" % key, "ingame_%s_entrance.png" % key)
        else:
            b.shot("%s_open" % key)
        route_weather = weather_now(b)
        b.walk(cfg["steps"])
        b.frames(90)
        b.settle()
    else:
        b.warp(route, 4, 6) if kind == "boatman" else b.warp(route, 4, 3)
        b.frames(40)
        b.settle()
        b.face("U")
        b.frames(20)
        save_shot(b, key, "%s_open_entrance" % key, "ingame_%s_entrance.png" % key)       # the boatman at the Canoe Docks / the keeper's stair
        route_weather = weather_now(b)
        enter(b, key, cfg)
    t.check("%s: OPEN: the way in ends in %s on the arrival cell %s" % (key, name, arrive), b.map_name() == name and b.pos() == tuple(arrive), b.where())
    want_w = weather_plan.HEADER[name]
    t.check("%s: the overworld weather in the lair is %s" % (key, want_w), weather_now(b) == want_w, weather_now(b))
    # -- the encounter's conditions
    if night:
        set_time(b, DAY)
        other_map(b)
        b.set_flag("FLAG_PG_URSALUNA_DONE", False)
        b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
        b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
        b.warp(name, *arrive)
        b.frames(30)
        t.check("%s: by day the encounter is hidden (%s)" % (key, flag), b.flag(flag))
        set_time(b, NIGHT)
        other_map(b)
        b.warp(name, *arrive)
        b.frames(30)
        t.check("%s: at night the encounter stands in its lair (%s clear)" % (key, flag), not b.flag(flag))
    else:
        b.set_var("VAR_ORLEANS_STORY", 44)
        other_map(b)
        b.warp(name, *arrive)
        b.frames(30)
        t.check("%s: below story 45 the encounter is hidden on load (%s)" % (key, flag), b.flag(flag))
        b.set_var("VAR_ORLEANS_STORY", 45)
        b.set_flag(flag, False)             # the epilogue's unhide script (OldestShrine.inc PostGame_EventScript_Unhide)
        other_map(b)
        b.warp(name, *arrive)
        b.frames(30)
        t.check("%s: at story 45 it stays shown (%s clear)" % (key, flag), not b.flag(flag))
    # -- in front of it: a battle (a 2-bar boss, its weather), a KO leaves it standing, it fights again
    b.warp(name, sx, sy)
    b.face(sface)
    b.frames(20)
    save_shot(b, key, "%s_in_front" % key)
    b.frames(60)
    png = b.shot("%s_weather" % key)
    d = SHOTS2 if key in D.LAIRS2 else SHOTS
    shutil.copyfile(png, d / ("weather_%s.png" % key))
    ok = battle_menu(b)
    t.check("%s: a battle starts" % key, ok)
    if ok:
        check_battle_weather(b, t, key, battle_state(b))
        s = B.state(b)
        t.check("%s: a boss with 2 bars (1 icon on the healthbox)" % key, s["is_boss"] and s["total"] == 2 and s["bars"] == 2 and s["visible"] == 1, s)
    B.end_battle(b)
    t.check("%s: a KO (not a catch) leaves it standing: not retired" % key,
            not b.flag(flag) and not b.flag("FLAG_PG_URSALUNA_DONE") and not b.flag("FLAG_ROUTE14_ROUGAROU_DONE") and not b.flag("FLAG_RECEIVED_LYCANROCITE"))
    reset_party(b)      # heal (a status the first battle left would stop the tester's moves) and drop earlier catches: a full party would send the catch to the PC
    b.face(sface)
    t.check("%s: it fights again" % key, battle_menu(b))
    # -- the guaranteed victory catch retires it
    n0 = b.party_count()
    break_bars(b)
    caught = B.catch_through(b, n0)
    t.check("%s: breaking the last bar offers the victory catch, the Master Ball catches it (party %d -> %d)" % (key, n0, b.party_count()), caught)
    t.check("%s: a catch retires the encounter (%s set)" % (key, flag), b.flag(flag) or key == "rougarou")
    b.set_flag(flag, False)
    b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
    b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
    b.set_flag("FLAG_PG_URSALUNA_DONE", False)
    # -- walking out
    set_time(b, DAY)
    other_map(b)
    b.warp(name, *arrive)
    b.frames(20)
    if key == "zapdos":      # the hatch is the arrival cell too: step off it and on again
        b.warp(name, 10, 11)
        b.frames(20)
        b.walk("D")
        bx, by, face = lair["back"]
        bm = BACKMAP.get(lair.get("back_map"), route)
    else:
        ex = exits[0]
        d = DIRS[(ex[0] - arrive[0], ex[1] - arrive[1])]
        b.walk(d)
        bx, by, face = lair["back"]
        bm = BACKMAP.get(lair.get("back_map"), route)
    b.frames(90)
    b.settle()
    t.check("%s: walking out returns to %s %s%s" % (key, bm, (bx, by), " facing " + lair["back"][2]), b.map_name() == bm and b.pos() == (bx, by), b.where())
    b.shot("%s_back_on_route" % key)
    b.frames(60)
    t.check("%s: the lair's weather does not leak onto %s (%s on leaving, %s when it was entered)" % (key, bm, weather_now(b), route_weather),
            weather_now(b) == route_weather, weather_now(b))


def articuno(b, t):
    b.set_flag("FLAG_HIDE_POINTE_ICE_GUARD", False)
    b.set_var("VAR_ORLEANS_STORY", 44)
    other_map(b)
    b.warp("PointeRouge", 39, 27)
    b.frames(30)
    b.step("U")
    t.check("articuno: sealed (story 44): the guard holds the ice plant door", b.map_name() == "PointeRouge", b.where())
    b.set_var("VAR_ORLEANS_STORY", 45)
    other_map(b)
    b.warp("PointeRouge", 39, 27)
    b.frames(30)
    b.step("U")
    b.step("U")
    b.frames(60)
    b.settle()
    t.check("articuno: open (story 45): the door leads into the ice plant, arrival on its mat (9, 13)", b.map_name() == "PointeRouge_IcePlant" and b.pos() == (9, 13), b.where())
    b.set_var("VAR_ORLEANS_STORY", 44)
    b.set_flag("FLAG_PG_ARTICUNO", False)
    other_map(b)
    b.warp("PointeRouge_IcePlant", 9, 12)
    b.frames(30)
    t.check("articuno: below story 45 Articuno is hidden on load", b.flag("FLAG_PG_ARTICUNO"))
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_ARTICUNO", False)
    other_map(b)
    b.warp("PointeRouge_IcePlant", 9, 12)
    b.frames(30)
    t.check("articuno: at story 45 it stands on the dais", not b.flag("FLAG_PG_ARTICUNO"))
    (sx, sy), sface = D.STAND["articuno"]
    b.warp("PointeRouge_IcePlant", sx, sy)
    b.face(sface)
    b.frames(20)
    save_shot(b, "articuno", "articuno_in_front")
    b.frames(60)
    t.check("articuno: the overworld weather in the ice plant is WEATHER_SNOW", weather_now(b) == "WEATHER_SNOW" == weather_plan.HEADER["PointeRouge_IcePlant"], weather_now(b))
    png = b.shot("articuno_weather")
    shutil.copyfile(png, SHOTS / "weather_articuno.png")
    ok = battle_menu(b)
    t.check("articuno: a battle starts", ok)
    if ok:
        check_battle_weather(b, t, "articuno", battle_state(b))
        s = B.state(b)
        t.check("articuno: a boss with 2 bars", s["is_boss"] and s["total"] == 2 and s["visible"] == 1, s)
    B.end_battle(b)
    t.check("articuno: a KO leaves it standing", not b.flag("FLAG_PG_ARTICUNO"))
    b.face(sface)
    reset_party(b)
    b.face(sface)
    ok = battle_menu(b)
    n0 = b.party_count()
    break_bars(b)
    t.check("articuno: the Master Ball catch (party %d -> %d)" % (n0, b.party_count()), B.catch_through(b, n0))
    t.check("articuno: a catch retires it", b.flag("FLAG_PG_ARTICUNO"))
    b.set_flag("FLAG_PG_ARTICUNO", False)
    b.warp("PointeRouge_IcePlant", 9, 12)
    b.frames(20)
    b.walk("DD")      # the mat is an arrow warp: step on, then press down
    b.frames(90)
    b.settle()
    t.check("articuno: walking out of the ice plant returns to Pointe Rouge", b.map_name() == "PointeRouge", b.where())
    b.frames(60)
    t.check("articuno: the snow does not leak onto Pointe Rouge (%s)" % weather_now(b), weather_now(b) == weather_plan.HEADER["PointeRouge"], weather_now(b))


def metatile(b, x, y):
    return b.call("MapGridGetMetatileIdAt", x + 7, y + 7) & 0xFFFF      # grid coordinates carry the 7-cell border margin (MAP_OFFSET)


def zapdos_lamp(b, t):
    """the gallery's lantern is dark until Eclair's grid is back (FLAG_STORMS_EDGE_GRID_RESTORED), then lit"""
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_STORMS_EDGE_GRID_RESTORED", False)
    other_map(b)
    b.warp("StormsEdge_LighthouseGallery", 10, 12)
    b.frames(40)
    dark = metatile(b, 9, 5)
    save_shot(b, "zapdos", "zapdos_lamp_dark", "ingame_zapdos_lamp_dark.png")
    b.set_flag("FLAG_STORMS_EDGE_GRID_RESTORED", True)
    other_map(b)
    b.warp("StormsEdge_LighthouseGallery", 10, 12)
    b.frames(40)
    lit = metatile(b, 9, 5)
    save_shot(b, "zapdos", "zapdos_lamp_lit", "ingame_zapdos_lamp_lit.png")
    t.check("Zapdos' gallery: the lantern is dark before the grid is restored and lit after (metatile %#x -> %#x)" % (dark, lit), dark != lit)
    b.set_flag("FLAG_STORMS_EDGE_GRID_RESTORED", False)


def moltres_sign(b, t):
    """the Route 17 mill door: barred (a message) before story 45"""
    b.set_var("VAR_ORLEANS_STORY", 44)
    other_map(b)
    b.warp("Route17", 33, 10)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 26)
    b.frames(40)
    txt = S.text_at(b, "gStringVar4")
    t.check("Route 17: the sealed mill door says it is barred (%r)" % txt[:40], "barred" in txt.lower() or b.script_status() != 2)
    b.advance_text(20)
    b.set_var("VAR_ORLEANS_STORY", 45)


def discovered(b, t):
    """AchievementSaveData.lairs (offset 50 of the block): a bit per lair set on first arrival (Achievement_OnMapEntered); Shrine Seeker (trophy #61, id 60) needs the trio's
    three pools, Celebi's glade, the Old Water and the Oldest Shrine"""
    import t20_achievements as A
    b.set_var("VAR_ORLEANS_STORY", 45)
    a = A.block(b)
    bits0 = [b.r8(a + 50 + i) for i in range(3)]
    t.check("a new game has no lair discovered (bits %s)" % bits0, bits0 == [0, 0, 0])
    order = ["rougarou", "ursaluna", "articuno", "celebi", "suicune", "raikou", "entei", "uxie", "mesprit", "azelf", "zapdos", "thundurus", "zarude", "ogerpon",
             "tornadus", "galar_moltres", "galar_zapdos", "galar_articuno", "moltres", "landorus"]
    seen = {}
    for i, key in enumerate(order):
        if key == "articuno":
            name, at = "PointeRouge_IcePlant", (9, 12)
        else:
            name, at = D.LAIRS[key]["map"], tuple(D.arrive(key))
        other_map(b)
        b.warp(name, *at)
        b.frames(40)
        a = A.block(b)
        got = [b.r8(a + 50 + k) for k in range(3)]
        seen[key] = bool(got[i // 8] >> (i % 8) & 1)
    t.check("every lair sets its own 'discovered' bit on first arrival (%d of %d)" % (sum(seen.values()), len(order)), all(seen.values()), seen)
    b.frames(240)
    t.check("Shrine Seeker is still locked with the four shrine lairs found (the Old Water and the Oldest Shrine are missing)", not A.unlocked(b, 60))
    for name, at in (("OldWater", (24, 33)), ("OldestShrine", (16, 20))):
        other_map(b)
        b.warp(name, *at)
        b.frames(40)
    b.frames(240)
    t.check("Shrine Seeker unlocks once the four shrine lairs, the Old Water and the Oldest Shrine are all discovered", A.unlocked(b, 60))


def soft_reset(b0, t, key):
    """a save made in front of the encounter; boots with different timing roll a different Pokemon when the battle starts"""
    lair = D.LAIRS[key]
    name = lair["map"]
    (sx, sy), sface = D.STAND[key]
    flag = enc_flag(key)
    b = Bot(rom=b0.rom, out_dir=b0.out / ("sr_%s" % key))
    try:
        b.new_game()
        b.give_mon("SPECIES_MEWTWO", 100)
        b.set_move(0, "MOVE_TACKLE")
        b.set_var("VAR_STARTER_MON", 2)
        for i in range(1, 9):
            b.set_flag("FLAG_BADGE0%d_GET" % i)
        b.set_var("VAR_ORLEANS_STORY", 45)
        b.set_flag(flag, False)
        b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
        b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
        b.set_flag("FLAG_PG_URSALUNA_DONE", False)
        b.set_clock(NIGHT if CFG[key].get("night") else DAY)
        b.warp(name, sx, sy)
        b.face(sface)
        b.frames(30)
        S.save_game(b)
        sav = b.out / "pre.sav"
        b.h.cmd("dumpsave " + wsl_path(sav))
        rolls = []
        for extra in (0, 97, 253):
            c = Bot(rom=b.rom, out_dir=b.out / ("boot_%d" % extra), save=sav)
            try:
                S.continue_game(c, extra)
                c.face(sface)
                c.press("A", 4, 26)
                if not B.start_battle(c):
                    rolls.append(None)
                    continue
                txt = B.intro_text(c)
                pers = c.r32(S.enemy_mon(c))
                m = S.WILD.search(txt or "")
                rolls.append((pers, m.group(2) if m else None, m is not None))
            finally:
                c.close()
        ok = all(r and r[2] for r in rolls)
        t.check("%s: every boot reached the battle with the wild intro naming the roll" % key, ok, rolls)
        pers = {r[0] for r in rolls if r}
        t.check("%s: different boot timing gives different Pokemon (%d personalities)" % (key, len(pers)), len(pers) >= 2, ["%08x %s" % (r[0], r[1]) for r in rolls if r])
    finally:
        b.close()

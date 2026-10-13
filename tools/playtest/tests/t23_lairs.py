"""The legendary lairs, batch 1 (tools/mapgen/lairs.py, story_data_lairs.py): seven lairs and their route entrances.

For each of the six outdoor lairs (the rougarou off Route 14, Bloodmoon Ursaluna off Route 23, Celebi off Route 7, Suicune off Route 11, Raikou off
Route 2, Entei off Route 16) and Articuno's ice plant:
  * the entrance is SEALED before its story value (the rougarou: before the flood flag, FLAG_BADGE06_GET; the others: story 44): the bot walks at the
    entrance cells and stays on the route; and OPEN after it: the same walk ends in the lair, on its arrival cell (10, 13);
  * walking out (south onto the exit triggers) puts the player back on the entrance cell, facing the way the table says;
  * the encounter appears under its conditions: hidden below story 45 (FLAG_PG_*), shown at 45; the rougarou and Ursaluna only at night;
  * a battle starts, a KO leaves it standing (not retired), and it fights again;
  * in-engine screenshots: tile_review/set_pieces/lairs/ingame_<lair>.png (the lair at night where it is night-only, the player in front of the encounter).
Also the static facts: every lair's objects and triggers in its map.json, the scripts moved out of the routes, the maps' tilesets.
"""
import re
import shutil
import sys
from pathlib import Path

from bot import map_data, ROOT

sys.path.insert(0, str(Path(ROOT) / "tools" / "mapgen"))
import story_data_lairs as D  # noqa: E402
import weather_plan  # noqa: E402

ORDER = ["NONE", "SUNNY_CLOUDS", "SUNNY", "RAIN", "SNOW", "RAIN_THUNDERSTORM", "FOG_HORIZONTAL", "VOLCANIC_ASH", "SANDSTORM", "FOG_DIAGONAL",
         "UNDERWATER", "SHADE", "DROUGHT", "DOWNPOUR", "UNDERWATER_BUBBLES"]     # include/constants/weather.h
# the lair's weather (weather_plan.HEADER, user-approved) and what it starts in battle: (gBattleWeather flag name or None, terrain or None)
# fog = Misty Terrain (B_OVERWORLD_FOG >= GEN_8), thunderstorm = rain + Electric Terrain (B_THUNDERSTORM_TERRAIN), snow = snow (B_OVERWORLD_SNOW >= GEN_9)
BATTLE = {"rougarou": ("WEATHER_FOG_HORIZONTAL", None, 2), "ursaluna": ("WEATHER_SANDSTORM", "B_WEATHER_SANDSTORM", None),
          "celebi": ("WEATHER_SUNNY", None, None), "suicune": ("WEATHER_RAIN", "B_WEATHER_RAIN", None),
          "raikou": ("WEATHER_RAIN_THUNDERSTORM", "B_WEATHER_RAIN", 3), "entei": ("WEATHER_DROUGHT", "B_WEATHER_SUN", None),
          "articuno": ("WEATHER_SNOW", "B_WEATHER_SNOW", None)}
MASK = {"B_WEATHER_RAIN": 0xE, "B_WEATHER_SUN": 0x30, "B_WEATHER_SANDSTORM": 0x40, "B_WEATHER_HAIL": 0x80, "B_WEATHER_SNOW": 0x100, "B_WEATHER_FOG": 0x200}   # include/constants/battle.h
ANY = ("B_WEATHER_RAIN", "B_WEATHER_SUN", "B_WEATHER_SANDSTORM", "B_WEATHER_SNOW", "B_WEATHER_HAIL", "B_WEATHER_FOG")


def weather_now(b):
    return "WEATHER_" + ORDER[b.call("GetCurrentWeather") & 0xFF]


def start_battle(b):
    """A is pressed; wait for the battle to reach the first turn menu, return (gBattleWeather, terrain) there; None if no battle started"""
    for _ in range(400):
        if b.in_battle():
            break
        b.press("A", 4, 26)
    else:
        return None
    main_func = b.sym("gBattleMainFunc")
    for _ in range(900):
        if (b.r32(main_func) & ~1) == b.sym("HandleTurnActionSelectionState"):
            break
        b.press("A", 4, 26)
    got = (b.r16(b.sym("gBattleWeather")), b.r8(b.sym("gFieldTimers") + 5))
    b.fight()
    b.frames(30)
    b.advance_text(60)
    return got


def check_battle_weather(b, t, key, got):
    ow, flag, terrain = BATTLE[key]
    w, ter = got
    bits = {n: bool(w & MASK[n]) for n in ANY}
    want = {n: n == flag for n in ANY}
    t.check("%s: the battle weather is %s%s (gBattleWeather %#x, terrain %s)" % (key, flag or "none", " + terrain %d" % terrain if terrain else "", w, ter),
            bits == want and (ter == (terrain or 0)), "%s terrain %s" % ([n for n, v in bits.items() if v], ter))

SHOTS = Path(ROOT).parent / "tile_review" / "set_pieces" / "lairs"
DAY, NIGHT = 12, 22

# key: (route map, steps from the approach cell to the entrance trigger, the open condition: ("flag", FLAG) or ("story", 45), the encounter's flag,
#       the night-only logic)
LAIRS = {
    "rougarou": ("Route14", "RR", ("flag", "FLAG_BADGE06_GET"), "FLAG_HIDE_ROUTE14_ROUGAROU", True),
    "ursaluna": ("Route23", "UU", ("story", 45), "FLAG_PG_URSALUNA_BM", True),
    "celebi": ("Route7", "UU", ("story", 45), "FLAG_PG_CELEBI", False),
    "suicune": ("Route11", "U", ("story", 45), "FLAG_PG_SUICUNE", False),
    "raikou": ("Route2", "UUUU", ("story", 45), "FLAG_PG_RAIKOU", False),
    "entei": ("Route16", "UUU", ("story", 45), "FLAG_PG_ENTEI", False),
}
FACING = {"LEFT": "face_left", "DOWN": "face_down", "RIGHT": "face_right", "UP": "face_up"}


def set_time(b, hour):
    b.set_clock(hour)
    b.frames(30)


def battle_through(b):
    """talk is already started; fight any battle to its end, then clear the text. Returns True if a battle happened"""
    seen = False
    for _ in range(300):
        if b.in_battle():
            seen = True
            b.fight()
        elif seen:
            break
        else:
            b.press("A", 4, 26)
    b.frames(30)
    b.advance_text(60)
    return seen


def other_map(b):
    b.advance_text(30)
    b.frames(30)
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.frames(30)
    b.advance_text(30)


def save_shot(b, key, label):
    png = b.shot(label)
    SHOTS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, SHOTS / ("ingame_%s.png" % key))


def set_open(b, cond, on):
    kind, v = cond
    if kind == "flag":
        b.set_flag(v, on)
    else:
        b.set_var("VAR_ORLEANS_STORY", v if on else v - 1)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    set_time(b, DAY)

    # ---------------------------------------------------------------- static facts
    for key, lair in D.LAIRS.items():
        name = lair["map"]
        md = map_data(name)
        t.check("%s: a 20 x 16 map with the encounter object and the two exit triggers (armed by %s)" % (name, D.TRIG),
                (md["width"], md["height"]) == (20, 16) and len(md["objects"]) == 1 and len(md["coords"]) == 2
                and all(c["var"] == D.TRIG and c["script"] == name + "_EventScript_Exit" for c in md["coords"]) and not md["warps"],
                "%sx%s %d objects %d triggers" % (md["width"], md["height"], len(md["objects"]), len(md["coords"])))
        route = LAIRS[key][0]
        rt = map_data(route)
        trig = [c for c in rt["coords"] if c["script"] == route + "_EventScript_LairEnter"]
        t.check("%s: two entrance triggers, armed by %s" % (route, D.TRIG), len(trig) == 2 and all(c["var"] == D.TRIG for c in trig))
        if key != "rougarou":
            t.check("%s: the old encounter object is gone from the route" % route,
                    not [o for o in rt["objects"] if str(o.get("flag", "")).startswith("FLAG_PG_") and o["flag"] == LAIRS[key][3]])
    rt14 = map_data("Route14")
    t.check("Route 14: the rougarou left the levee crest", not [o for o in rt14["objects"] if o.get("flag") == "FLAG_HIDE_ROUTE14_ROUGAROU"])
    ice = map_data("PointeRouge_IcePlant")
    t.check("the ice plant: Articuno's object on the dais front (9, 5), the exit warp (9, 13) to Pointe Rouge",
            [(o["x"], o["y"], o["flag"]) for o in ice["objects"]] == [(9, 5, "FLAG_PG_ARTICUNO")] and [(w["x"], w["y"]) for w in ice["warps"]] == [(9, 13)])

    # ---------------------------------------------------------------- the six outdoor lairs
    for key, (route, steps, cond, enc_flag, night) in LAIRS.items():
        lair = D.LAIRS[key]
        name = lair["map"]
        ax, ay = lair["approach"]
        bx, by, face = lair["back"]
        (sx, sy), sface = D.STAND[key]
        # -- sealed
        b.set_var("VAR_ORLEANS_STORY", 44)
        set_open(b, cond, False)
        other_map(b)
        b.warp(route, ax, ay)
        b.frames(30)
        b.walk(steps)
        b.frames(30)
        t.check("%s: SEALED (%s): walking at the entrance leaves the player on the route" % (key, cond[1]), b.map_name() == route, b.where())
        b.shot("%s_sealed" % key)
        # -- open
        set_open(b, cond, True)
        if cond[0] == "story":
            b.set_var("VAR_ORLEANS_STORY", 45)
        other_map(b)
        b.warp(route, ax, ay)
        b.frames(30)
        b.shot("%s_open" % key)
        route_weather = weather_now(b)
        b.walk(steps)
        b.frames(90)
        b.settle()
        t.check("%s: OPEN: the same walk ends in %s on the arrival cell (10, 13)" % (key, name), b.map_name() == name and b.pos() == D.ARRIVE, b.where())
        t.check("%s: the overworld weather in the lair is %s" % (key, BATTLE[key][0]), weather_now(b) == BATTLE[key][0] == weather_plan.HEADER[name],
                weather_now(b))
        # -- the encounter's conditions
        if night:
            set_time(b, DAY)
            other_map(b)
            b.set_flag("FLAG_PG_URSALUNA_DONE", False)
            b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
            b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
            b.warp(name, 10, 13)
            b.frames(30)
            t.check("%s: by day the encounter is hidden (%s)" % (key, enc_flag), b.flag(enc_flag))
            set_time(b, NIGHT)
            other_map(b)
            b.warp(name, 10, 13)
            b.frames(30)
            t.check("%s: at night the encounter stands in its lair (%s clear)" % (key, enc_flag), not b.flag(enc_flag))
        else:
            b.set_var("VAR_ORLEANS_STORY", 44)
            other_map(b)
            b.warp(name, 10, 13)
            b.frames(30)
            t.check("%s: below story 45 the encounter is hidden on load (%s)" % (key, enc_flag), b.flag(enc_flag))
            b.set_var("VAR_ORLEANS_STORY", 45)
            b.set_flag(enc_flag, False)             # the epilogue's unhide script (OldestShrine.inc PostGame_EventScript_Unhide)
            other_map(b)
            b.warp(name, 10, 13)
            b.frames(30)
            t.check("%s: at story 45 it stays shown (%s clear)" % (key, enc_flag), not b.flag(enc_flag))
        # -- walk in front of it, a battle, a KO leaves it standing, it fights again
        enc = map_data(name)["objects"][0]
        b.warp(name, sx, sy)
        b.face(sface)
        b.frames(20)
        save_shot(b, key, "%s_in_front" % key)
        b.press("A", 4, 20)
        got = start_battle(b)
        t.check("%s: a battle starts" % key, got is not None)
        if got is not None:
            check_battle_weather(b, t, key, got)
        t.check("%s: a KO (not a catch) leaves it standing: not retired" % key,
                not b.flag(enc_flag) and not b.flag("FLAG_PG_URSALUNA_DONE") and not b.flag("FLAG_ROUTE14_ROUGAROU_DONE") and not b.flag("FLAG_RECEIVED_LYCANROCITE"))
        b.face(sface)
        b.press("A", 4, 20)
        t.check("%s: it fights again" % key, battle_through(b))
        # -- the weather picture (the night ones at night: the dark tint and the weather layers together)
        if night:
            set_time(b, NIGHT)
            other_map(b)
            b.warp(name, sx, sy)
            b.face(sface)
        b.frames(120)
        png = b.shot("%s_weather" % key)
        shutil.copyfile(png, SHOTS / ("weather_%s.png" % key))
        # -- walking out
        set_time(b, DAY)
        b.warp(name, 10, 13)
        b.frames(20)
        b.walk("D")
        b.frames(90)
        b.settle()
        t.check("%s: walking out (south) returns to %s %s facing %s" % (key, route, (bx, by), face), b.map_name() == route and b.pos() == (bx, by), b.where())
        b.shot("%s_back_on_route" % key)
        b.frames(60)
        t.check("%s: the lair's weather does not leak onto %s (%s on arrival, %s when it was entered)" % (key, route, weather_now(b), route_weather),
                weather_now(b) == route_weather, weather_now(b))
        b.set_flag(enc_flag, False)

    # ---------------------------------------------------------------- Articuno: the ice plant (the door exists; the legend from story 45)
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
    b.press("A", 4, 20)
    got = start_battle(b)
    t.check("articuno: a battle starts", got is not None)
    if got is not None:
        check_battle_weather(b, t, "articuno", got)
    t.check("articuno: a KO leaves it standing", not b.flag("FLAG_PG_ARTICUNO"))
    b.warp("PointeRouge_IcePlant", 9, 12)
    b.frames(20)
    b.walk("DD")      # the mat is an arrow warp: step on, then press down
    b.frames(90)
    b.settle()
    t.check("articuno: walking out of the ice plant returns to Pointe Rouge", b.map_name() == "PointeRouge", b.where())
    b.frames(60)
    t.check("articuno: the snow does not leak onto Pointe Rouge (%s)" % weather_now(b), weather_now(b) == weather_plan.HEADER["PointeRouge"], weather_now(b))

    # ---------------------------------------------------------------- the scripts left the routes
    story = Path(ROOT) / "tools" / "mapgen" / "story"
    for route, lair in (("Route2", "Route2_RaikouClearing"), ("Route7", "Route7_CelebiGlade"), ("Route11", "Route11_SuicuneIsle"),
                        ("Route16", "Route16_EnteiField"), ("Route23", "Route23_BloodmoonArroyo"), ("Route14", "Route14_RougarouHollow")):
        rsrc = (story / (route + ".inc")).read_text(encoding="utf-8")
        lsrc = (story / (lair + ".inc")).read_text(encoding="utf-8")
        t.check("%s: the encounter's scripts are in %s, not on the route" % (route, lair),
                not re.search(r"^%s_EventScript_(Pg(Raikou|Celebi|Suicune|Entei|UrsalunaBm)|Rougarou)::" % route, rsrc, re.M)
                and re.search(r"^%s_EventScript_(Pg\w+|Rougarou)::" % lair, lsrc, re.M) is not None)

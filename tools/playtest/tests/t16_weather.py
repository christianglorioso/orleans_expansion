"""Overworld weather (user-approved table, tools/mapgen/weather_plan.py): the weather on each map at the key story values, read from the engine
(GetCurrentWeather after the warp), the weather that changes with the story, and the battle weather it starts (rain / sandstorm / sun / Misty Terrain
come from the overworld weather in battle; clear, sunny, sunny with clouds and clouds start nothing). Interiors have none, except the Drowned Temple."""
import os
import sys

from bot import map_data

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mapgen"))
import weather_plan  # noqa: E402

W = weather_plan.HEADER


def weather_now(b):
    return b.call("GetCurrentWeather") & 0xFF


ORDER = ["NONE", "SUNNY_CLOUDS", "SUNNY", "RAIN", "SNOW", "RAIN_THUNDERSTORM", "FOG_HORIZONTAL", "VOLCANIC_ASH", "SANDSTORM", "FOG_DIAGONAL",
         "UNDERWATER", "SHADE", "DROUGHT", "DOWNPOUR", "UNDERWATER_BUBBLES"]     # include/constants/weather.h


def name_of(n):
    return "WEATHER_" + ORDER[n] if n < len(ORDER) else str(n)


def spot(mapname):
    """a walkable cell: where the first object stands"""
    o = map_data(mapname)["objects"][0]
    return o["x"], o["y"]


def at(b, t, mapname, want, why, pre=None):
    for f in (pre or {}).get("flags", []):
        b.set_flag(f[0], f[1])
    for v, n in (pre or {}).get("vars", []):
        b.set_var(v, n)
    x, y = spot(mapname)
    b.warp(mapname, x, y)
    b.frames(90)
    got = name_of(weather_now(b))
    t.check("%s: %s" % (mapname, why), got == want, "%s (want %s)" % (got, want))


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    # ---- the switches: before and after
    clear = {"vars": [("VAR_ORLEANS_STORY", 5)], "flags": [("FLAG_STORMS_EDGE_GRID_RESTORED", False), ("FLAG_BADGE06_GET", False), ("FLAG_DUST_STORMS_LIFTED", False)]}
    at(b, t, "IsleMarais", "WEATHER_RAIN", "rain before the player leaves for Grand Oak (story 5)", clear)
    at(b, t, "Route1", "WEATHER_RAIN", "rain before story 6")
    at(b, t, "StormsEdge", "WEATHER_RAIN_THUNDERSTORM", "thunderstorm until the grid is back")
    at(b, t, "Route14", "WEATHER_RAIN", "rain until badge 6")
    at(b, t, "Route23", "WEATHER_SANDSTORM", "sandstorm until the dust storms lift")
    at(b, t, "Route24", "WEATHER_SANDSTORM", "sandstorm until the dust storms lift")
    at(b, t, "Route25", "WEATHER_RAIN_THUNDERSTORM", "thunderstorm through the finale (story 41)", {"vars": [("VAR_ORLEANS_STORY", 41)]})
    at(b, t, "OldestShrine", "WEATHER_RAIN_THUNDERSTORM", "thunderstorm through the finale (story 41)")
    after = {"vars": [("VAR_ORLEANS_STORY", 45)], "flags": [("FLAG_STORMS_EDGE_GRID_RESTORED", True), ("FLAG_BADGE06_GET", True), ("FLAG_DUST_STORMS_LIFTED", True)]}
    at(b, t, "IsleMarais", "WEATHER_SUNNY_CLOUDS", "sunny with clouds from story 6 on (45)", after)
    at(b, t, "Route1", "WEATHER_SUNNY_CLOUDS", "sunny with clouds from story 6 on")
    at(b, t, "StormsEdge", "WEATHER_NONE", "clear once the grid is back")
    at(b, t, "Route14", "WEATHER_NONE", "clear after badge 6")
    at(b, t, "Route23", "WEATHER_NONE", "clear once the dust storms are lifted")
    at(b, t, "Route24", "WEATHER_NONE", "clear once the dust storms are lifted")
    at(b, t, "Route25", "WEATHER_NONE", "clear after the Rayquaza raid (story 45)")
    at(b, t, "OldestShrine", "WEATHER_NONE", "clear after the Rayquaza raid (story 45)")
    at(b, t, "IsleMarais", "WEATHER_SUNNY_CLOUDS", "story 6 exactly", {"vars": [("VAR_ORLEANS_STORY", 6)]})
    at(b, t, "Route25", "WEATHER_RAIN_THUNDERSTORM", "story 42 (Rayquaza not yet calmed)", {"vars": [("VAR_ORLEANS_STORY", 42)]})
    # ---- the static ones
    for m, w in W.items():
        if m in weather_plan.SWITCH:
            continue
        at(b, t, m, w, "static weather")
    # ---- interiors have none
    for m in ("IsleMarais_Shelter", "GrandOak_Gym", "CrescentCity_Gym", "LandsEnd_Gym", "Redfield_Pokecenter"):
        at(b, t, m, "WEATHER_NONE", "an interior has no weather")
    # ---- sanity: the map.json header agrees with the plan
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[3] / "data" / "maps"
    for m, w in W.items():
        t.check("%s map.json header" % m, json.loads((root / m / "map.json").read_text())["weather"] == w, w)

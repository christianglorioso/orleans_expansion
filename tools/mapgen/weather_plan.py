"""Overworld weather of every Orleans map (user-approved table, 2026-10-13).

HEADER is the weather written into data/maps/<Map>/map.json ("weather"); build.py (write_events) re-applies it whenever a map is rebuilt, so a
regenerated map keeps it. SWITCH lists the maps whose weather changes with the story: the map's OnTransition script (tools/mapgen/story/<Map>.inc,
label <Map>_EventScript_StoryWeather) does `setweather` before the weather is started, so the new weather is in place when the map is shown.
"clear" = WEATHER_NONE, "clouds" = WEATHER_SHADE (overcast), "sunny with clouds" = WEATHER_SUNNY_CLOUDS, "sunny" = WEATHER_SUNNY.

Battles: the overworld weather starts in every battle on that map (field effect OVERWORLD_WEATHER, permanent, and in Gen 9 mode it cannot be
overridden): rain / thunderstorm / downpour = rain (thunderstorm adds Electric Terrain), sandstorm = sandstorm, drought = harsh sun,
fog (either kind) = Misty Terrain. Clear, sunny, sunny with clouds and clouds start nothing.

usage: python tools/mapgen/weather_plan.py [--apply]     check (or with --apply, rewrite) the "weather" field of every map.json
"""
import json
import os
import sys

HEADER = {
    "IsleMarais": "WEATHER_RAIN",              # until story 6 (SWITCH), then sunny with clouds
    "Route1": "WEATHER_RAIN",                  # likewise
    "GrandOak": "WEATHER_NONE",
    "Route2": "WEATHER_SUNNY_CLOUDS",
    "Route3": "WEATHER_SHADE",
    "StormsEdge": "WEATHER_RAIN_THUNDERSTORM",  # until FLAG_STORMS_EDGE_GRID_RESTORED, then clear
    "CrescentCity": "WEATHER_NONE",
    "PointeRouge": "WEATHER_NONE",
    "Route4": "WEATHER_SHADE",
    "Route5": "WEATHER_FOG_HORIZONTAL",
    "Route6": "WEATHER_NONE",
    "Route7": "WEATHER_FOG_HORIZONTAL",
    "Route8": "WEATHER_FOG_HORIZONTAL",
    "Route9": "WEATHER_NONE",
    "CampCocodrie": "WEATHER_NONE",
    "Route10": "WEATHER_NONE",
    "Route11": "WEATHER_FOG_HORIZONTAL",
    "Route12": "WEATHER_NONE",
    "Route13": "WEATHER_NONE",
    "LutinsHollow": "WEATHER_FOG_DIAGONAL",
    "OldWater": "WEATHER_FOG_HORIZONTAL",
    "Route14": "WEATHER_RAIN",                # until FLAG_BADGE06_GET, then clear
    "Route15": "WEATHER_SUNNY_CLOUDS",
    "Route16": "WEATHER_SUNNY",
    "Route17": "WEATHER_SUNNY",
    "Redfield": "WEATHER_DROUGHT",
    "Route18": "WEATHER_SHADE",
    "Route19": "WEATHER_RAIN",
    "Route20": "WEATHER_RAIN",
    "LandsEnd": "WEATHER_RAIN",
    "Route21": "WEATHER_RAIN",
    "Route22": "WEATHER_DOWNPOUR",
    "Route23": "WEATHER_SANDSTORM",           # until FLAG_DUST_STORMS_LIFTED, then clear
    "Route24": "WEATHER_SANDSTORM",
    "Route25": "WEATHER_RAIN_THUNDERSTORM",   # until Rayquaza is calmed (story 43), then clear
    "OldestShrine": "WEATHER_RAIN_THUNDERSTORM",
    "LandsEnd_DrownedTemple": "WEATHER_UNDERWATER_BUBBLES",
    # the legendary lairs (user-approved 2026-10-13, story_data_lairs.py): the weather starts in their battles like any overworld weather
    "Route14_RougarouHollow": "WEATHER_FOG_HORIZONTAL",    # battle: Misty Terrain (B_OVERWORLD_FOG >= GEN_8)
    "Route23_BloodmoonArroyo": "WEATHER_SANDSTORM",        # battle: sandstorm (Bloodmoon Ursaluna is Normal/Ground: immune)
    "Route7_CelebiGlade": "WEATHER_SUNNY",                 # a bright day, no battle weather
    "Route11_SuicuneIsle": "WEATHER_RAIN",                 # battle: rain
    "Route2_RaikouClearing": "WEATHER_RAIN_THUNDERSTORM",  # battle: rain + Electric Terrain (B_THUNDERSTORM_TERRAIN)
    "Route16_EnteiField": "WEATHER_DROUGHT",               # battle: harsh sun
    "PointeRouge_IcePlant": "WEATHER_SNOW",                # battle: snow (B_OVERWORLD_SNOW >= GEN_9)
}

# map -> (condition script text, weather it switches to); documentation and the bot test read this
SWITCH = {
    "IsleMarais": ("VAR_ORLEANS_STORY >= 6", "WEATHER_SUNNY_CLOUDS"),
    "Route1": ("VAR_ORLEANS_STORY >= 6", "WEATHER_SUNNY_CLOUDS"),
    "StormsEdge": ("FLAG_STORMS_EDGE_GRID_RESTORED", "WEATHER_NONE"),
    "Route14": ("FLAG_BADGE06_GET", "WEATHER_NONE"),
    "Route23": ("FLAG_DUST_STORMS_LIFTED", "WEATHER_NONE"),
    "Route24": ("FLAG_DUST_STORMS_LIFTED", "WEATHER_NONE"),
    "Route25": ("VAR_ORLEANS_STORY >= 43", "WEATHER_NONE"),
    "OldestShrine": ("VAR_ORLEANS_STORY >= 43", "WEATHER_NONE"),
}


def header(map_name):
    """the map.json weather for an Orleans map; interiors and everything not listed stay WEATHER_NONE"""
    return HEADER.get(map_name)


def main(argv):
    apply = "--apply" in argv
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "maps")
    bad = 0
    for name, want in HEADER.items():
        path = os.path.join(root, name, "map.json")
        raw = open(path, encoding="utf-8", newline="").read()
        d = json.loads(raw)
        if d.get("weather") != want:
            bad += 1
            print(f"{name}: {d.get('weather')} -> {want}")
            if apply:
                old = f'"weather": "{d.get("weather")}"'
                assert raw.count(old) == 1, name
                open(path, "w", encoding="utf-8", newline="").write(raw.replace(old, f'"weather": "{want}"'))
    print(f"{len(HEADER)} maps, {bad} {'rewritten' if apply else 'differ'}")
    return 0 if apply or not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

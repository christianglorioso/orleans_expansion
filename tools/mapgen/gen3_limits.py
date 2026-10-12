"""Gen-3 engine limit checks for every Orleans map (outdoor and interior).  Read-only on game data.

usage (from the decomp root):  python tools/mapgen/gen3_limits.py

Writes tools/mapgen/maps/00_gen3_limits.md with, per map:
  1. map buffer: (w + 15) * (h + 14) against MAX_MAP_DATA_SIZE 10240          (fieldmap.h: MAP_OFFSET 7, W = 2*7+1, H = 2*7)
  2. object slots: OBJECT_EVENTS_COUNT 16 incl. the player; the most object events inside one spawn window
     (event_object_movement.c TrySpawnObjectEvents: template x in [px-9, px+10], y in [py-7, py+9], a 20 x 17 cell window
     around the player), plus the overworld-wild-encounter reserve (OWE_SPAWNS_MAX = 4 generated OWEs, which are object
     events in the same 16 slots)
  3. sprite palettes: 16 OBJ palette slots, ALL dynamic in the overworld (ResumeMap -> FreeAllSpritePalettes; the 12-slot
     reserve of InitObjectEventPalettes is never used), shared by weather, the player, field effects, every object palette
     tag in the window (graphics_id -> src/data/object_events graphics info paletteTag) and every OWE species palette.
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

ROOT = world.ROOT
OUT = os.path.join(world.MAPS, "00_gen3_limits.md")

MAP_OFFSET = 7
MAX_MAP_DATA_SIZE = 10240
OBJECT_EVENTS_COUNT = 16
OWE_SPAWNS_MAX = 4
WIN_X = (-9, 10)      # template.x + 7 within [pos.x - 2, pos.x + 17] (backup coords)  ->  map x in [px - 9, px + 10]
WIN_Y = (-7, 9)       # template.y + 7 within [pos.y, pos.y + 16]                        ->  map y in [py - 7, py + 9]
FIXED_PALETTES = ["weather fog (StartWeather, always)", "player (Brendan/May tag)",
                  "field effects GENERAL_0 (shadow, grass, ripple...)", "field effects GENERAL_1"]


def load_gfx_palettes():
    base = os.path.join(ROOT, "src/data/object_events")
    ptr = open(os.path.join(base, "object_event_graphics_info_pointers.h"), encoding="utf-8").read()
    info = open(os.path.join(base, "object_event_graphics_info.h"), encoding="utf-8").read()
    try:
        info += open(os.path.join(base, "object_event_graphics_info_followers.h"), encoding="utf-8").read()
    except OSError:
        pass
    tags = {}
    for m in re.finditer(r"const struct ObjectEventGraphicsInfo (\w+)\s*=\s*\{(.*?)\n\};", info, re.S):
        t = re.search(r"\.paletteTag\s*=\s*(\w+)", m.group(2))
        if t:
            tags[m.group(1)] = t.group(1)
    gfx = {}
    for m in re.finditer(r"\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&(\w+)", ptr):
        gfx[m.group(1)] = tags.get(m.group(2), "?")
    return gfx


def palette_tag(gfx, gid):
    m = re.match(r"OBJ_EVENT_GFX_SPECIES\((\w+)\)", gid)
    if m:
        return "MON_" + m.group(1)
    if re.match(r"OBJ_EVENT_GFX_VAR_\d+", gid):
        return "VAR(" + gid[len("OBJ_EVENT_GFX_"):] + ")"
    t = gfx.get(gid, "?")
    return t.replace("OBJ_EVENT_PAL_TAG_", "") if t != "OBJ_EVENT_PAL_TAG_DYNAMIC" else "DYNAMIC(" + gid + ")"


def load_encounters():
    d = json.load(open(os.path.join(ROOT, "src/data/wild_encounters.json"), encoding="utf-8"))
    out = {}
    for e in d["wild_encounter_groups"][0]["encounters"]:
        s = out.setdefault(e["map"], {"land": set(), "water": set()})
        for k, n in (("land_mons", "land"), ("water_mons", "water")):
            for mon in (e.get(k) or {}).get("mons", []):
                s[n].add(mon["species"].replace("SPECIES_", ""))
    return out


def orleans_maps():
    layouts = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json"), encoding="utf-8"))["layouts"]}
    res = []
    for d in sorted(os.listdir(os.path.join(ROOT, "data/maps"))):
        p = os.path.join(ROOT, "data/maps", d, "map.json")
        if not os.path.exists(p):
            continue
        m = json.load(open(p, encoding="utf-8"))
        lay = layouts.get(m.get("layout"))
        if not lay or m.get("layout") == "LAYOUT_STRIP_STUB" or not lay["primary_tileset"].startswith("gTileset_Orleans"):
            continue
        res.append((d, m, lay))
    return res


def worst_window(objs, w, h):
    """(count, (px, py), [objects]) for the player position whose spawn window holds the most object events"""
    best = (-1, None, [])
    for py in range(h):
        for px in range(w):
            ins = [o for o in objs if px + WIN_X[0] <= o["x"] <= px + WIN_X[1] and py + WIN_Y[0] <= o["y"] <= py + WIN_Y[1]]
            if len(ins) > best[0]:
                best = (len(ins), (px, py), ins)
    return best


def main():
    gfx = load_gfx_palettes()
    enc = load_encounters()
    rows = []
    for name, m, lay in orleans_maps():
        w, h = lay["width"], lay["height"]
        area = (w + 2 * MAP_OFFSET + 1) * (h + 2 * MAP_OFFSET)
        objs = [o for o in m.get("object_events", []) if "x" in o]
        cnt, pos, ins = worst_window(objs, w, h) if objs else (0, None, [])
        e = enc.get(m["id"])
        species = sorted((e["land"] | e["water"])) if e else []
        owe = OWE_SPAWNS_MAX if species else 0
        tags = Counter(palette_tag(gfx, o["graphics_id"]) for o in ins)
        owe_pals = min(OWE_SPAWNS_MAX, len(species)) if species else 0
        rows.append(dict(name=name, id=m["id"], w=w, h=h, area=area, pct=100.0 * area / MAX_MAP_DATA_SIZE, n_obj=len(objs), cnt=cnt, pos=pos,
                         ins=ins, owe=owe, species=species, tags=tags, owe_pals=owe_pals, mtype=m.get("map_type", ""),
                         total_slots=1 + cnt + owe, pal_total=len(FIXED_PALETTES) + len(tags) + owe_pals, weather=m.get("weather", "")))
    L = []
    L.append("# Gen-3 limit checks (buffer, object slots, sprite palettes)\n")
    L.append("Generated by `tools/mapgen/gen3_limits.py`; read-only. %d Orleans maps (layouts with an Orleans primary tileset, stub layouts excluded).\n" % len(rows))
    L.append("## Engine facts used\n")
    L.append(f"- Map buffer: `MAP_OFFSET` 7, `MAP_OFFSET_W` 15, `MAP_OFFSET_H` 14 (include/fieldmap.h); `InitMapLayoutData` leaves the map unloaded if (w+15)*(h+14) > MAX_MAP_DATA_SIZE = {MAX_MAP_DATA_SIZE}.")
    L.append(f"- Object slots: OBJECT_EVENTS_COUNT = {OBJECT_EVENTS_COUNT} (include/constants/global.h), the player takes one. The camera is a sprite, not an object event. Followers are off (OW_FOLLOWERS_ENABLED FALSE).")
    L.append("- Spawn window (`TrySpawnObjectEvents`/`RemoveObjectEventIfOutsideView`): an object event exists while its cell is within x [px-9, px+10], y [py-7, py+9] of the player: 20 x 17 cells (screen is 15 x 10). Objects whose flag is set are not spawned; counted here as present (worst case).")
    L.append(f"- OWEs (WE_OW_ENCOUNTERS TRUE): up to OWE_SPAWNS_MAX = {OWE_SPAWNS_MAX} generated OWEs at once, local ids 249-252, each a normal object event in the same 16 slots (`TrySpawnObjectEventTemplate`). They spawn in a 15 x 9 area around the player on land/water encounter tiles of maps that have a wild header. Only routes, Storm's Edge, Isle Marais and a few towns have headers here; interiors have none. (WE_OWE_DESPAWN_ON_ENTER_TOWN despawns OWEs on entering MAP_TYPE_TOWN/CITY, so the reserve on a town map is conservative.) If slots run out the spawn simply fails (GetNextOWESpawnSlot / InitObjectEventStateFromTemplate returns OBJECT_EVENTS_COUNT); a story NPC that cannot get a slot at load fails to appear.")
    L.append("- Sprite palettes: 16 OBJ slots, ALL dynamic in the overworld (`ResumeMap` calls FreeAllSpritePalettes, gReservedSpritePaletteCount = 0; `InitObjectEventPalettes`'s 12 reserved slots are not used). Every distinct paletteTag among object events in view takes one slot (`LoadObjectEventPalette` -> `LoadSpritePalette`), NPC_1..4, NPC_BLUE/PINK/GREEN/WHITE, each Pokemon species (and shiny/female variant) etc. each are separate tags. Always taken: " + "; ".join(FIXED_PALETTES) + ". Also taken on demand: a reflection palette per reflected object palette on reflective tiles, ash/dust/light sprites. `LoadSpritePalette` with no free slot first despawns generated OWEs, then returns 0xFF (the sprite draws with the wrong palette). `CheckCanLoadOWE_Palette` needs 2 free slots (or the mon palette or its spawn-effect palette already loaded) else the OWE does not spawn.")
    L.append(f"- Palette budget: 16 - {len(FIXED_PALETTES)} fixed = {16 - len(FIXED_PALETTES)} for object palettes + OWE species palettes (up to {OWE_SPAWNS_MAX} distinct species at once) + reflections.\n")

    L.append("## 1. Map buffer\n")
    L.append("| map | size | (w+15)*(h+14) | % of 10240 | flag |")
    L.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: -r["pct"]):
        flag = "OVER" if r["area"] > MAX_MAP_DATA_SIZE else "HIGH (>85%)" if r["pct"] > 85 else ""
        if r["pct"] > 40 or flag:
            L.append(f"| {r['name']} | {r['w']}x{r['h']} | {r['area']} | {r['pct']:.1f}% | {flag} |")
    L.append(f"\nEvery other map is under 40% (largest of the rest: {max([r['pct'] for r in rows if r['pct'] <= 40] or [0]):.1f}%)..\n")

    L.append("## 2. Object slots (worst spawn window per map)\n")
    L.append(f"Slots needed in the worst window = 1 player + objects in the 20x17 window + {OWE_SPAWNS_MAX} OWE reserve on maps with a wild header. Limit {OBJECT_EVENTS_COUNT}.\n")
    L.append("| map | objects (all) | worst window objects | at player x,y | OWE reserve | slots needed | flag |")
    L.append("|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (-r["total_slots"], -r["cnt"]))[:45]:
        flag = "OVER" if r["total_slots"] > OBJECT_EVENTS_COUNT else "TIGHT (>=14)" if r["total_slots"] >= 14 else ""
        L.append(f"| {r['name']} ({r['id'][4:]}) | {r['n_obj']} | {r['cnt']} | {r['pos']} | {r['owe']} | {r['total_slots']} | {flag} |")
    L.append("")
    over = [r for r in rows if r["total_slots"] >= 14]
    L.append("### Spots at or near the limit (story-critical objects marked)\n")
    if not over:
        L.append("None: no map reaches 14 slots.\n")
    for r in sorted(over, key=lambda r: -r["total_slots"]):
        L.append(f"**{r['name']}** worst at player {r['pos']}: {r['cnt']} objects + player + {r['owe']} OWE = {r['total_slots']}")
        for o in r["ins"]:
            crit = []
            if o.get("trainer_type", "TRAINER_TYPE_NONE") != "TRAINER_TYPE_NONE":
                crit.append("TRAINER")
            if re.search(r"JAYDEN|LEADER|GYM|RIVAL", (o.get("script", "") + o.get("local_id", "")).upper()):
                crit.append("STORY")
            L.append(f"- ({o['x']},{o['y']}) {o['graphics_id'].replace('OBJ_EVENT_GFX_', '')} `{o.get('script', '')}` flag {o.get('flag', '0')} {' '.join(crit)}")
        L.append("")

    L.append("## 3. Sprite palettes (worst spawn window per map)\n")
    L.append(f"Palettes needed = {len(FIXED_PALETTES)} fixed + distinct object palette tags in the worst-objects window + OWE species palettes (min({OWE_SPAWNS_MAX}, species in the land/water tables)). Limit 16. Window chosen for the most objects, so a window with fewer objects but more distinct palettes can be slightly worse; the tag list shows the window used.\n")
    L.append("| map | distinct object palettes in window | OWE species palettes | total | flag | object tags |")
    L.append("|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: -r["pal_total"])[:45]:
        flag = "OVER" if r["pal_total"] > 16 else "TIGHT (>=14)" if r["pal_total"] >= 14 else ""
        tg = ", ".join(f"{k}x{v}" for k, v in r["tags"].most_common())
        L.append(f"| {r['name']} ({r['id'][4:]}) | {len(r['tags'])} | {r['owe_pals']} | {r['pal_total']} | {flag} | {tg} |")
    L.append("")
    L.append("### Maps with OWE-capable encounter tables (species that can appear)\n")
    for r in rows:
        if r["species"]:
            L.append(f"- {r['name']}: {len(r['species'])} species: {', '.join(r['species'])}")
    L.append("")
    pal_over = [r for r in rows if r["pal_total"] >= 14]
    L.append("### Palette-risk windows\n")
    if not pal_over:
        L.append("None reach 14 of 16.\n")
    for r in sorted(pal_over, key=lambda r: -r["pal_total"]):
        L.append(f"- **{r['name']}**: {r['pal_total']} of 16 ({len(FIXED_PALETTES)} fixed + {len(r['tags'])} object tags + {r['owe_pals']} OWE) at player {r['pos']}")
    L.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # console summary
    print(len(rows), "maps")
    print("buffer worst:", [(r["name"], round(r["pct"], 1)) for r in sorted(rows, key=lambda r: -r["pct"])[:4]])
    print("slots worst:", [(r["name"], r["total_slots"], r["cnt"]) for r in sorted(rows, key=lambda r: -r["total_slots"])[:8]])
    print("pal worst:", [(r["name"], r["pal_total"], len(r["tags"])) for r in sorted(rows, key=lambda r: -r["pal_total"])[:8]])


if __name__ == "__main__":
    main()

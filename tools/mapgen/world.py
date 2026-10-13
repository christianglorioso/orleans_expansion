"""The Orleans world's map connections: the single source of truth.

WORLD lists every map connection once, as (map_a, direction, map_b, offset, note); this script writes both
sides into data/maps/<Map>/map.json ("connections"), reciprocal:  A down B at k  means  B up A at -k.

Geometry (the GBA/pokeemerald rule, the same one the slice maps already use):
    right/left:  B's row 0 sits at A's row `offset`      (B.y0 = A.y0 + offset),  B is east/west of A
    down/up:     B's column 0 sits at A's column `offset` (B.x0 = A.x0 + offset),  B is south/north of A
So Route 1 down Isle Marais at -5 puts Isle Marais' column 18 (its exit) under Route 1's column 13 (its exit).

Only the "connections" key of each map.json is touched: build.py rewrites the events (warps, objects, coord/bg
events) of a map.json and nothing else, and firstpass.py creates a map.json only when it is missing, so connections
written here survive a rebuild.  Every other key, and the file's formatting, is left exactly as it was (the file is
read and written the way build.py does it; the script refuses to write a file it could not round-trip).

usage (from the decomp root):
  python tools/mapgen/world.py --dry-run     show a diff of what would change, write nothing
  python tools/mapgen/world.py               write the connections (takes the build lock "world")
  python tools/mapgen/world.py --list        the table, with each join's two sides
  python tools/mapgen/world.py --questions   the open questions and the warps that are NOT connections
tools/mapgen/world_stitch.py lays the world out from this table and writes the seam report.
"""
import difflib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAPS = os.path.join(HERE, "maps")

# the Orleans outdoor maps: spec stem -> pretty name (the spec gives the map's folder name and constant)
OUTDOOR = {
    "isle_marais": "Isle Marais", "grand_oak": "Grand Oak", "old_water": "The Old Water",
    "storms_edge": "Storm's Edge", "crescent_city": "Crescent City", "pointe_rouge": "Pointe Rouge",
    "camp_cocodrie": "Camp Cocodrie", "lutins_hollow": "Lutin's Hollow", "redfield": "Redfield",
    "lands_end": "Land's End", "oldest_shrine": "Oldest Shrine",
    **{f"route_{n}": f"Route {n}" for n in range(1, 26)},
}

# (map_a, direction, map_b, offset, note).  direction is where map_b lies from map_a.
# Boat routes join through water ("w"), road routes through road cells ("r"); the note says what lines up.
WORLD = [
    # ---- the vertical slice: exactly as it was written before this table existed
    ("route_1", "down", "isle_marais", -5, "road to road: Route 1 S (13-14) / Isle Marais N (18-19)"),
    ("route_1", "up", "grand_oak", -5, "road to road: Route 1 N (14-15) / Grand Oak S (19-20)"),
    ("route_1", "left", "old_water", -15, "hidden channel (opens after the trust event), water to water"),
    # ---- west coast: Grand Oak - Route 2 - Storm's Edge - Route 3 - Crescent City
    ("grand_oak", "right", "route_2", 5, "road to road: Grand Oak E rows 13-15 / Route 2 W rows 8-10"),
    ("route_2", "right", "storms_edge", -5, "road: Route 2 E rows 10-12 / Storm's Edge W rows 16-17 (2 of 3 cells; the map has 4 lake rows above since the edge-feather rollout)"),
    ("storms_edge", "right", "route_3", 5, "causeway: Storm's Edge E rows 16-17 / Route 3 W rows 11-12"),
    ("route_3", "right", "crescent_city", -32, "causeway: Route 3 E rows 11-12 / Crescent City W rows 43-44"),
    # ---- the Basin boat chain, east to west: Crescent City - 6 - 7 - 8 - 9 - Camp Cocodrie (Route 25 north off Route 8)
    ("route_6", "right", "crescent_city", 12, "basin canal: Route 6 E row 12 / Crescent W water rows 0-1 (upper)"),
    ("route_7", "right", "route_6", 0, "Route 7 E channels (rows 11-12, 18-19) open into Route 6's basin"),
    ("route_8", "right", "route_7", 3, "Route 7 W channels (rows 11-12, 2-3) open into Route 8 rows 14-15, 5-6"),
    ("route_9", "right", "route_8", -2, "wide water to wide water: Route 9 rows 0-24 / Route 8 rows 2-26"),
    ("camp_cocodrie", "right", "route_9", 4, "boardwalk landing: Camp E rows 15-16 / Route 9 W rows 11-12"),
    ("route_8", "up", "route_25", 9, "after both raids: Route 8 N col 23 / Route 25 S col 14 (water to water; Route 8 N edge has no channel built)"),
    ("route_25", "up", "oldest_shrine", -3, "Route 25 N water cols 6-22 / Oldest Shrine S (all water)"),
    # ---- the Big Lake: Crescent City - 10 - 11 - 12 - 13 - Lutin's Hollow
    ("crescent_city", "right", "route_10", -2, "lake: Crescent E water rows 0-11 / Route 10 W water rows 2-13 (no Crescent E exit built)"),
    ("route_10", "right", "route_11", -22, "boat: Route 10 E row 3 / Route 11 W row 25"),
    ("route_11", "up", "route_12", 22, "Route 12 S edge (all water, 28 cells) over Route 11's N edge cols 22-49 (see QUESTIONS)"),
    ("route_12", "up", "route_13", -1, "road: Route 12 N (13-14) / Route 13 S (14-15)"),
    ("route_13", "right", "lutins_hollow", -28, "lane: Route 13 E rows 2-3 / Lutin's Hollow W rows 30-31 (of 29-33)"),
    # ---- sugar country and the delta: Crescent City - 14 - 15 - 16 - 17 - Redfield - 18 - 19 - 20 - Land's End - 21 - 22
    ("crescent_city", "down", "route_14", 39, "levee road: Crescent S (52-53) / Route 14 N (13-14)"),
    ("route_14", "down", "route_15", 4, "Route 14 S road (13-14) / Route 15 N road (9-10: the mockup junction's north arm; was +8 against an unbuilt stub at 5-6)"),
    ("route_15", "right", "route_16", -4, "road: Route 15 E rows 9-10 / Route 16 W rows 13-14"),
    ("route_16", "right", "route_17", 5, "road: Route 16 E rows 17-18 / Route 17 W rows 12-13"),
    ("route_17", "right", "redfield", -5, "mill road: Route 17 E rows 12-13 / Redfield W rows 17-18"),
    ("redfield", "right", "route_18", 9, "river dock, boat: Redfield E row 20 / Route 18 W row 11"),
    ("route_18", "right", "route_19", 1, "boat: Route 18 E row 12 / Route 19 W channel rows 10-12"),
    ("route_19", "right", "route_20", 1, "boat: Route 19 E channel rows 11-13 / Route 20 W row 11"),
    ("route_20", "right", "lands_end", -3, "heron rookery boardwalk: Route 20 E row 12 / Land's End W rows 15-16"),
    ("lands_end", "down", "route_21", -2, "landing pier, boat: Land's End S (41-42) / Route 21 N col 44"),
    ("route_21", "left", "route_22", 21, "open Gulf: Route 21 W row 24 / Route 22 E row 3"),
    # ---- the north: Pointe Rouge and its three roads.  (No connection to Crescent City: the riverboat is a warp.)
    ("route_5", "right", "pointe_rouge", -15, "road: Route 5 E rows 2-4 / Pointe Rouge W rows 17-19 (3 of 3 cells)"),
    ("pointe_rouge", "down", "route_4", 5, "levee road: Pointe S (22-25) / Route 4 N approach paving (17-20); was +6 against a 2-wide road"),
    ("pointe_rouge", "right", "route_23", -7, "both bridges: Pointe E rows 5-6 and 26-27 / Route 23 W rows 12-13 and 33-34"),
    ("route_23", "right", "route_24", -3, "road: Route 23 E rows 10-11 / Route 24 W rows 13-14 (was -2: Route 23's road is 2 wide there)"),
]

# Exit cells (rows for E/W edges, columns for N/S edges, in the map's own coordinates) on sides where the map's spec
# lists no exit: the boat routes' water channels and the exits the mockups draw that the spec does not have.
# Used by the seam report (world_stitch.py) to say whether exits line up.  A side may list several spans.
EXTRA_EXITS = {
    ("route_1", "W"): [list(range(6, 13))],         # the hidden channel to the Old Water (water run rows 6-12)
    ("old_water", "E"): [list(range(21, 28))],      # ... and where it leaves the Old Water
    ("route_6", "W"): [[11]], ("route_6", "E"): [[12]],
    ("route_7", "W"): [[11, 12]], ("route_7", "E"): [[11, 12]],
    ("route_8", "W"): [[14]], ("route_8", "E"): [[14]], ("route_8", "N"): [[23]],
    ("route_9", "E"): [[12]],
    ("route_10", "E"): [[3]],
    ("route_11", "W"): [[25]], ("route_11", "N"): [[35, 36]],  # N: Route 12's arrow (cols 13-14 of Route 12 = 35-36), the water run to it
    ("route_12", "S"): [[13, 14]],
    ("route_18", "W"): [[11]], ("route_18", "E"): [[12]],
    ("route_19", "W"): [[10, 11, 12]], ("route_19", "E"): [[11, 12, 13]],
    ("route_20", "W"): [[11]], ("route_20", "E"): [[12]],
    ("route_21", "N"): [[44]], ("route_21", "W"): [[24]],
    ("route_22", "E"): [[3]],
    ("route_25", "N"): [[14]], ("route_25", "S"): [[14]],
    ("oldest_shrine", "S"): [[17]],
    ("redfield", "E"): [[20]],
    ("crescent_city", "W"): [[0, 1]],               # the basin canal (Route 6 basin mouth, boat)
    ("crescent_city", "E"): [list(range(0, 12))],   # the lake shore (Route 10 lakefront): the whole water run
    ("route_10", "W"): [list(range(2, 14))],        # its lake water; the spec's W exit is the lakefront promenade (rows 19-22)
}

# Open questions: choices where the mockup is ambiguous or contradicts the region map.  Nothing is hidden: each
# entry says what was wired and what the alternative is.
QUESTIONS = [
    "Q1 Route 14 -> Route 15 (corner join). Route 14 is a north-south map whose arrow is on its south edge ('Route 15 (south)'), "
    "Route 15 is east-west and its arrow is on its WEST edge ('Route 14 (north-west)'). Wired: Route 14 down Route 15 (offset now +4, see the table; was +8) "
    "(Route 14 S road cols 13-14 over Route 15's N edge road stub cols 5-6). Alternative: Route 15 left Route 14 (Route 15 W "
    "exit rows 3-4 against a new exit on Route 14's east edge near its south end). tools/mapgen/town_plans.py DRY_FADE assumes "
    "'Route 15's west edge is Route 14's', so the alternative keeps Route 15's built west fade and costs a ~13-tile road spur "
    "on Route 14; the wired reading keeps both built exits' roads and needs Route 15's N edge opened and faded.",
    "Q2 Route 11 -> Route 12 (corner join). Route 11 is east-west, its arrow is on its EAST edge row 2 ('Route 12 landing "
    "(north-east)'); Route 12 is north-south, its arrow on its SOUTH edge ('Route 11 landing (south)'). Wired: Route 11 up "
    "Route 12 at +22 (Route 12's all-water south edge over Route 11's north edge, cols 22-49: water to water along the full "
    "28 cells, no edits). Alternative: Route 11 right Route 12, Route 12's west edge rows 41-45 (water) against Route 11's "
    "east rows 0-4; Route 11's drawn east arrow would be used but Route 12's drawn south arrow would not.",
    "Q3 Crescent City -> Route 10 (corner join). Crescent's mockup puts 'Route 10 lakefront (boat)' on its NORTH edge "
    "(x~83 of 104, the lake), Route 10's arrow is on its WEST edge ('Crescent City lakefront', the promenade). Wired: "
    "Crescent right Route 10 at -2, so the lake continues across Crescent's east edge rows 0-11 into Route 10's west water "
    "rows 2-13 (Crescent has no east exit built; its lakefront ground rows 13-43 meets Route 10's promenade rows 16-22). "
    "Alternative: Crescent up Route 10 through the north edge (Route 10 would sit above Crescent's NE corner, its south "
    "edge would need a channel).",
    "Q4 Pointe Rouge's group (Routes 4, 5, 23, 24 + Pointe Rouge) is not connected to the rest. The region map joins "
    "Route 4's south end to Crescent City only by the riverboat ferry (Crescent mockup: 'Riverboat to Pointe Rouge', Route "
    "4: 'Riverboat landing (south)'), so Route 4 S and Crescent N are WARPS, as the brief says. Consequence: walking "
    "from Isle Marais never reaches Pointe Rouge (you take the ferry). If you want the river to be sailable/walkable as "
    "well, Route 4 down Crescent City (Route 4's S edge cols 22-27 is water, Crescent's N edge cols 0-82 is water) "
    "would be one more connection; not wired.",
    "Q5 Route 6 east -> Crescent City west (upper). The region map and the Route 6 mockup agree that Route 6 ends at "
    "Crescent City, but the Crescent mockup puts 'Route 6 basin mouth (boat)' on its WEST edge at row ~1 while "
    "Route 3's causeway uses the same west edge at rows 43-44. Wired: both Route 3 and Route 6 connect to Crescent's "
    "west edge (two left connections at different rows: Route 6 at rows 0-1, Route 3 at rows 43-44). The canal is only 2 "
    "cells wide (Crescent W rows 0-1) against Route 6's 19-row wide basin water: the rest is a hard cut.",
    "Q6 Route 8 north -> Route 25 -> Oldest Shrine. The Route 8 mockup draws the Route 25 arrow on its north edge at col 23 "
    "('Route 25 (north; after both raids)') but the built Route 8 north edge is open marsh with no channel. Wired at +9 "
    "(Route 25's arrow col 14 under Route 8 col 23). The gate (both raids) is an event.",
    "Q7 Route 4 north and Pointe Rouge south: Pointe's S exit is 4 cells wide (cols 22-25), Route 4's 2 (cols 17-18): wired "
    "centred (Route 4 under Pointe cols 23-24), two Pointe exit cells meet Route 4's levee verge.",
    "Q8 Isle Marais' west arrow ('Local channel (opening rescue...)') is NOT wired: it is the opening rescue, "
    "a scripted water event, not a map join. Isle Marais keeps only its north connection.",
]

# Exits that lead to places that are not outdoor maps (or are scenery): warps, not connections.
WARPS = [
    ("route_4", "S", "Riverboat landing (ferry to Crescent City): the riverboat, a warp/ferry event"),
    ("crescent_city", "N", "Riverboat to Pointe Rouge: the riverboat (Crescent mockup's north arrow at x~65 of 104)"),
    ("route_24", "S", "Salt-dome cavern (Groudon): cave mouth/door -> 12_salt_dome_cavern (its 'Up to Route 24 mine tunnels')"),
    ("route_22", "W (arrow)", "Dive: drowned temple (Kyogre) -> 11_drowned_temple (Dive spot, an underwater warp)"),
    ("isle_marais", "W", "Local channel (opening rescue): scripted water scene, not a join (Q8)"),
]


def load_json(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def dump(d):
    """map.json exactly as build.py's write_events writes it."""
    return json.dumps(d, indent=2) + "\n"


class Maps:
    """stem -> (spec, map.json path, MAP_ constant, size)."""

    def __init__(self):
        layouts = {l["id"]: l for l in json.loads(load_json(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"]}
        self.info = {}
        for stem in OUTDOOR:
            spec = json.loads(load_json(os.path.join(MAPS, stem + ".json")))
            mj = os.path.join(ROOT, "data", "maps", spec["map"], "map.json")
            const = json.loads(load_json(mj))["id"]
            lay = layouts[spec["layout"]]
            self.info[stem] = {"spec": spec, "path": mj, "const": const, "w": lay["width"], "h": lay["height"],
                               "layout": lay}


OPPOSITE = {"right": "left", "left": "right", "down": "up", "up": "down"}


def planned(maps):
    """stem -> [{'map': const, 'offset': k, 'direction': d}] in WORLD order, both sides of every entry."""
    out = {s: [] for s in OUTDOOR}
    for a, d, b, k, _note in WORLD:
        assert a in OUTDOOR and b in OUTDOOR, (a, b)
        out[a].append({"map": maps.info[b]["const"], "offset": k, "direction": d})
        out[b].append({"map": maps.info[a]["const"], "offset": -k, "direction": OPPOSITE[d]})
    return out


def validate(maps):
    """Sanity checks on the table: no duplicate side pair, and the two maps overlap along the seam."""
    problems = []
    seen = set()
    for a, d, b, k, _ in WORLD:
        if (a, b) in seen or (b, a) in seen:
            problems.append(f"{a}/{b} listed twice")
        seen.add((a, b))
        A, B = maps.info[a], maps.info[b]
        if d in ("right", "left"):
            lo, hi = max(0, k), min(A["h"], k + B["h"])
        else:
            lo, hi = max(0, k), min(A["w"], k + B["w"])
        if hi - lo < 1:
            problems.append(f"{a} {d} {b} at {k}: the maps do not touch")
    return problems


def current_text(maps, stem):
    return load_json(maps.info[stem]["path"])


def main(argv):
    dry = "--dry-run" in argv
    maps = Maps()
    if "--questions" in argv:
        print("QUESTIONS")
        for q in QUESTIONS:
            print(" -", q)
        print("\nWARPS (not connections)")
        for m, side, what in WARPS:
            print(f" - {m} {side}: {what}")
        return 0
    probs = validate(maps)
    if probs:
        print("\n".join(probs))
        return 1
    plan = planned(maps)
    if "--list" in argv:
        for a, d, b, k, note in WORLD:
            print(f"{a:14s} {d:5s} {b:14s} {k:+4d}   {note}")
        return 0

    edits = {}
    for stem, conns in plan.items():
        text = current_text(maps, stem)
        data = json.loads(text)
        if dump(data) != text:
            print(f"REFUSING: {maps.info[stem]['path']} does not round-trip through json.dumps(indent=2); not touching it")
            return 1
        old = data.get("connections")
        keep = [c for c in (old or []) if c["map"] not in {x["map"] for x in conns}]  # connections to maps not in WORLD stay
        # a connection the file already has to the same map keeps its place in the list (order is not significant to the game)
        new = []
        for c in old or []:
            hit = next((x for x in conns if x["map"] == c["map"]), None)
            if hit:
                new.append(hit)
                conns = [x for x in conns if x is not hit]
        new += conns
        data["connections"] = new if new else None
        out = dump(data)
        if out != text:
            edits[stem] = (text, out)
        for c in keep:
            print(f"note: {stem} keeps a connection not in WORLD: {c}")

    if not edits:
        print("connections already match the WORLD table; nothing to write")
        return 0
    if dry:
        for stem, (old, new) in edits.items():
            sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                                       f"a/data/maps/{maps.info[stem]['spec']['map']}/map.json",
                                                       f"b/data/maps/{maps.info[stem]['spec']['map']}/map.json", n=1))
        print(f"\n{len(edits)} map.json files would change (dry run, nothing written)")
        return 0

    lock = os.path.join(HERE, "buildlock.py")
    subprocess.run([sys.executable, lock, "acquire", "world"], check=True)
    try:
        for stem, (old, new) in edits.items():
            # re-read under the lock: another agent's build may have rewritten the events since
            cur = current_text(maps, stem)
            if cur != old:
                data = json.loads(cur)
                data["connections"] = json.loads(new)["connections"]
                new = dump(data)
            with open(maps.info[stem]["path"], "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
        print(f"wrote connections to {len(edits)} map.json files")
    finally:
        subprocess.run([sys.executable, lock, "release", "world"], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

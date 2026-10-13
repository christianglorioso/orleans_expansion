"""Trainer sight lint: every sight trainer must be able to spot a player somewhere (static port of src/trainer_see.c).

usage (decomp root): python tools/mapgen/sight_lint.py [Map ...] [-v]      exit 1 if a trainer can never spot anyone

Engine rule (CheckPathBetweenTrainerAndPlayer): the trainer looks along its facing direction up to `range` cells. Every cell before the
player's must be free (map collision 0, no object, and no elevation mismatch against the TRAINER's elevation: IsElevationMismatchAt is false
for trainer elevation 0 and for cells of elevation 0/15, else the cell's elevation must equal the trainer's); the player's own cell must
not be a wall, must match the trainer's elevation the same way, and holds the player object. So a land trainer (elevation 3) looking over
a water strip (elevation 1) sees nothing, and a rock in the first cell blinds a trainer (ch8_2 NIT-1/N2: Germain, Leontine, Route 18 T7,
Route 19 T3). Fix by facing another way, moving the trainer, or giving its CELL elevation 0 (build.py sight_cells() does that for a
land trainer over water; the map.json elevation of an NPC is overwritten by the cell's when it spawns).
A "spot cell" is a walkable or surfable cell (collision 0) where a player standing is spotted. ERROR: no spot cell. WARN (-v): fewer
than 2 spot cells while the range is 3 or more.
"""
import glob
import json
import os
import re
import struct
import sys

ROOT = os.getcwd()
ORLEANS = re.compile(r"^(IsleMarais|GrandOak|OldWater|StormsEdge|CrescentCity|PointeRouge|CampCocodrie|LutinsHollow|Redfield|LandsEnd|"
                     r"Route([1-9]|1\d|2[0-5])$|OldestShrine)")
DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def mismatch(telev, melev):
    if telev == 0 or melev in (0, 15):
        return False
    return telev != melev


def lint(names=None, verbose=False):
    lay = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"]}
    errors, warns = [], []
    for mp in sorted(glob.glob(os.path.join(ROOT, "data/maps/*/map.json"))):
        m = json.load(open(mp, encoding="utf-8"))
        if not ORLEANS.match(m["name"]) or (names and m["name"] not in names):
            continue
        l = lay[m["layout"]]
        raw = open(os.path.join(ROOT, l["blockdata_filepath"]), "rb").read()
        w, h = l["width"], l["height"]
        words = struct.unpack(f"<{len(raw) // 2}H", raw)
        cell = lambda x, y: ((words[y * w + x] >> 10) & 3, words[y * w + x] >> 12)
        occupied = {(o["x"], o["y"]) for o in m["object_events"]}
        for o in m["object_events"]:
            if o.get("trainer_type") not in ("TRAINER_TYPE_NORMAL", "TRAINER_TYPE_SEE_ALL_DIRECTIONS"):
                continue
            rng = int(o["trainer_sight_or_berry_tree_id"])
            mt = o["movement_type"]
            if o["trainer_type"] == "TRAINER_TYPE_NORMAL":
                dirs = [d for d in DIRS if mt.endswith("FACE_" + d)]
                if not dirs:
                    continue
            else:
                dirs = list(DIRS)
            telev = cell(o["x"], o["y"])[1]   # a stationary NPC takes the elevation of its cell (the template value is overwritten at spawn)
            spots = []
            for d in dirs:
                dx, dy = DIRS[d]
                x, y = o["x"], o["y"]
                for dist in range(1, rng + 1):
                    x, y = x + dx, y + dy
                    if not (0 <= x < w and 0 <= y < h):
                        break
                    col, el = cell(x, y)
                    if col:
                        break
                    if not mismatch(telev, el):
                        spots.append((x, y))   # the player may stand here (an NPC beyond it does not matter for this cell)
                    else:
                        break                    # an elevation mismatch blocks the line from here on
                    if (x, y) in occupied:
                        break
            tag = f"{m['name']}: {o.get('local_id') or o['script']} ({o['x']},{o['y']}) elev {telev} {mt[14:]} range {rng}"
            if not spots:
                errors.append(f"{tag} can never spot anyone (rock, wall or elevation mismatch in the first cell)")
            elif len(spots) < 2 and rng >= 3:
                warns.append(f"{tag} sees only {spots}")
    return errors, warns


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("-")]
    e, wns = lint(a, "-v" in sys.argv)
    for s in e:
        print("PROBLEM", s)
    if "-v" in sys.argv:
        for s in wns:
            print("warn", s)
    print(f"sight_lint: {len(e)} problems, {len(wns)} warnings")
    sys.exit(1 if e else 0)

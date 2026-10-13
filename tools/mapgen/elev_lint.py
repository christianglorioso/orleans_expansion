"""Elevation lint: an event you interact with by pressing A must be reachable at its own elevation.

usage (decomp root): python tools/mapgen/elev_lint.py [Map ...]     exit 1 if anything is wrong

The engine matches a bg_event (hidden item, sign) against the PLAYER's elevation, not the event cell's. A surfing player stands at
elevation 1 on water, a walker at 3 on land (4 on a bridge deck), so a hidden item on a water cell with elevation 3 can never be picked
up from the water (ch8_2 N1: Route 21 Max Revive, Route 22 Big Pearl, Route 10 Pearl, Route 11 Ether, Route 25 sign). For every
hidden_item and sign this checks that some walkable orthogonal neighbour has a matching elevation, or that the event uses 0
(ELEVATION_TRANSITION, matches any player elevation; 15 is the bridge level and is NOT a wildcard). build.py derives the elevation from the
layout (Builder.event_elevation) so a regeneration never brings the defect back; this lint proves the committed map.json files.
It also fails a map with more than 15 object events inside one camera window (the engine has 16 slots and the player takes one).
Object events are not checked here: a stationary NPC keeps its map.json elevation, and trainer sight is covered by sight_lint.py.
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
WILD = (0,)  # ELEVATION_TRANSITION: a bg_event with elevation 0 matches any player elevation (15 is the bridge level, NOT a wildcard)


def layouts():
    d = json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))
    return {l["id"]: l for l in d["layouts"]}


def load_bin(l):
    raw = open(os.path.join(ROOT, l["blockdata_filepath"]), "rb").read()
    w, h = l["width"], l["height"]
    words = struct.unpack(f"<{len(raw) // 2}H", raw)
    return w, h, words


def cell(words, w, x, y):
    v = words[y * w + x]
    return (v >> 10) & 3, v >> 12  # collision, elevation


def lint(names=None):
    lay = layouts()
    problems = []
    for mp in sorted(glob.glob(os.path.join(ROOT, "data/maps/*/map.json"))):
        m = json.load(open(mp, encoding="utf-8"))
        if not ORLEANS.match(m["name"]):
            continue
        if names and m["name"] not in names:
            continue
        w, h, words = load_bin(lay[m["layout"]])
        objs = [(o["x"], o["y"]) for o in m.get("object_events", [])]
        for x0 in range(-1, w):    # the engine spawns the objects near the camera (about 22x16 cells): at most 15 at once (16 slots, the player takes one)
            for y0 in range(-1, h):
                n = sum(1 for ox, oy in objs if x0 <= ox < x0 + 22 and y0 <= oy < y0 + 16)
                if n > 15:
                    problems.append(f"{m['name']}: {n} object events inside one camera window at ({x0},{y0}) (max 15: 16 slots, the player takes one)")
                    break
            else:
                continue
            break
        evs = [("hidden_item", e) for e in m.get("bg_events", []) if e["type"] == "hidden_item"]
        evs += [("sign", e) for e in m.get("bg_events", []) if e["type"] == "sign"]
        # object events are not checked: the engine re-reads their elevation from the cell they stand on (ObjectEventUpdateElevation)
        for kind, e in evs:
            x, y, el = e["x"], e["y"], int(e["elevation"])
            if el in WILD:
                continue
            if not (0 <= x < w and 0 <= y < h):
                problems.append(f"{m['name']}: {kind} ({x},{y}) outside the map")
                continue
            ok = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                col, nel = cell(words, w, nx, ny)
                if col == 0 and (nel == el or nel in (0, 15)):
                    ok = True
                    break
            if not ok:
                what = e.get("item") or e.get("script") or e.get("graphics_id")
                problems.append(f"{m['name']}: {kind} ({x},{y}) {what} has elevation {el}, no walkable neighbour matches")
    return problems


if __name__ == "__main__":
    p = lint(sys.argv[1:])
    for s in p:
        print("PROBLEM", s)
    print(f"elev_lint: {len(p)} problems")
    sys.exit(1 if p else 0)

"""Mock layouts of the legendary lairs, BATCH 2, and their entrances, rendered at 3x, plus the batch-2 review sheet.

usage (from the decomp root): python tools/mapgen/tilesets/lairs/lair_mocks_b2.py [--no-art] [--no-compose] [KEY ...]
    1. runs the batch-2 art scripts (TILESETS below, make_entrances_b2.py)
    2. composes every batch-2 secondary in a STAGING tree (lair_kit_b2.STAGE, the system temp dir): the budget, the palette report
       and the check that every metatile draws its sheet cell exactly. Nothing in data/ is written, nothing is registered.
    3. builds each lair from its function below and writes ../tile_review/set_pieces/lairs/batch2/<lair>_mock.png (3x, caption)
       + <lair>_mock.json (terrain, metatile names, walkable mask, encounter and stand cells, entry / exit, objects, notes, weather)
    4. renders every entrance (sealed and open) over the built route / town / room: <lair>_entrance.png
    5. writes the review sheet batch2/art_lairs_b2.png and the overview batch2/00_batch2_sheet.png
The mocks are proposals for the layout agent (LAYOUT_HANDOFF_batch2.md); data/, the maps and the story are not touched.
"""
import json
import math
import os
import subprocess
import sys
from collections import deque

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lair_kit_b2 import (REVIEW, LairMap, MAPGEN, ROOT, dump, gba, scale, stage_compose, stage_verify,  # noqa: E402
                         staged_tileset)
import lair_kit_b2 as K  # noqa: E402
from lair_kit import SPRITES  # noqa: E402
import lair_mocks as B1  # noqa: E402  (batch 1: caption, fonts, frames, resolvers, route rendering)

BG, FG, HEAD, DIM = B1.BG, B1.FG, B1.HEAD, B1.DIM
font, caption = B1.font, B1.caption
frame_std, water_res, marsh_res = B1.frame_std, B1.water_res, B1.marsh_res

for _k, _p in {"uxie": "uxie", "mesprit": "mesprit", "azelf": "azelf", "zapdos": "zapdos", "moltres": "moltres",
               "articuno_g": "articuno/galar", "zapdos_g": "zapdos/galar", "moltres_g": "moltres/galar", "tornadus": "tornadus",
               "thundurus": "thundurus", "landorus": "landorus", "zarude": "zarude", "ogerpon": "ogerpon", "npc": None}.items():
    if _p:
        SPRITES[_k] = (f"graphics/pokemon/{_p}/overworld.png", 32, 32)
SPRITES["boatman"] = ("graphics/object_events/pics/people/sailor.png", 16, 32)


# ---------------------------------------------------------------- shared map helpers
def cypress(m, x, y, base="marsh", small=False):
    """A primary cypress patch (3x3 big / 3x2? small) with its top-left cell at (x, y), on marsh or water."""
    k = "cypress_small" if small else "cypress"
    for dy in range(3 if not small else 3):
        for dx in range(3):
            n = f"patch:{k}_{dx}{dy}_{base}"
            if n in PRIM:
                m.props.append(("P", n, x + dx, y + dy))


PRIM = json.load(open(os.path.join(MAPGEN, "tilesets", "orleans_general.mapping.json")))["metatiles"]


def pp(m, name, x, y):
    """A single primary metatile as a prop (blocking)."""
    m.props.append(("P", name, x, y))


def occupied(m):
    occ = set()
    for (pre, n, px, py) in m.props:
        if pre == "P":
            occ.add((px, py))
            continue
        cv = m.pieces[pre].items[n]["cv"]
        occ |= {(px + i, py + j) for i in range(cv.cw) for j in range(cv.ch)}
    return occ


def free(m, x, y, ch=".", ring=False):
    """A plain cell of terrain `ch`, not by the wall, not under a prop (ring: its 8 neighbours are `ch` too)."""
    if not (0 <= x < m.W and 0 <= y < m.H) or m.g[y][x] != ch or (x, y) in m.wall or m.edge_cell(x, y):
        return False
    if (x, y) in occupied(m):
        return False
    cs = [m.ch(x, y), m.ch(x + 1, y), m.ch(x, y + 1), m.ch(x + 1, y + 1)]
    if any(c != ch for c in cs):
        return False
    if ring:
        return all(m.ch(x + dx, y + dy) == ch for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    return True


def scatter(m, prefix, names, cells, ch=".", ring=False):
    k = 0
    for (x, y) in cells:
        if free(m, x, y, ch, ring):
            m.prop(prefix, names[k % len(names)], x, y)
            k += 1


def set_res(prefix, name, allowed=(".",)):
    return lambda key, others: f"{prefix}:{name}_{key}" if others <= set(allowed) else None


# ---------------------------------------------------------------- the lake trio (lt)

def walk_line(m, x, y0, y1):
    """The rope-and-plank walk down column x: over the pool's own cells (C / N / S kerb) or over the grass."""
    m.resolve()
    for y in range(y0, y1 + 1):
        n = m.names[y][x]
        if n.startswith("lt:spring_"):
            k = n.split("_", 1)[1]
            m.prop("lt", f"walk_spring_{k if k in ('C', 'N', 'S') else 'C'}", x, y)
        elif n.startswith("P:ekat:water"):
            m.prop("lt", "walk_water", x, y)
        else:
            m.prop("lt", "walk_grass", x, y)





# ---------------------------------------------------------------- the storm lairs (ls, batch-1 Raikou's set extended)
def zapdos(P):
    base = {"k": ("ls:sky_00", False), "d": ("ls:deck_C", True)}   # (sky_00 is a placeholder: every sky cell gets a design below)
    sets = [("d", set_res("ls", "deck", ("k",)), True)]
    m = LairMap(20, 16, base, sets, {"ls": P}, wall_style="none", fill="k")
    m.disc("d", 9.9, 8.0, 7.7, 5.7)                       # the gallery deck round the lantern
    m.resolve()
    m.fixed = {}
    for y in range(m.H):
        for x in range(m.W):
            if m.names[y][x] == "ls:sky_00":
                design = "abc"[int(K.hashn(x // 2, y // 2, 977) * 3)]
                m.fixed[(x, y)] = f"ls:sky_{design}_{x & 1}{y & 1}"
            elif m.names[y][x] == "ls:deck_N" and x % 3 == 1:
                m.fixed[(x, y)] = "ls:deck_N_spark"
    m.prop("ls", "lantern", 8, 4)
    m.prop("ls", "hatch", 10, 12)
    m.prop("ls", "flag_mast", 4, 6)
    m.prop("ls", "anemometer", 15, 6)
    m.prop("ls", "storm_lamp", 13, 11)
    m.prop("ls", "rope", 6, 11)
    for (x, y, n) in [(7, 10, "deck_C3"), (13, 9, "deck_C3"), (5, 9, "deck_C2"), (15, 10, "deck_C2"), (12, 11, "deck_C2"),
                      (8, 12, "deck_C3"), (6, 4, "deck_C2"), (13, 4, "deck_C3")]:
        if m.names[y][x] == "ls:deck_C" and (x, y) not in occupied(m):
            m.prop("ls", n, x, y)
    m.obj("zapdos", 10, 9, "Zapdos (post-game) on the gallery deck before the lamp")
    m.obj("player", 10, 10, "the player, facing north")
    m.weather = "WEATHER_RAIN_THUNDERSTORM (Storm's Edge's own weather)"
    m.border = "ls:sky_a_XY (the storm, cloud design a) - the map is the gallery deck floating in the storm, as Emerald's Sky Pillar top floats in cloud"
    m.notes = [
        "20x16, the StormsEdge_LighthouseGallery map redone (it is an 11x9 Pokemon Center stand-in today); no wall: the deck floats in the",
        "storm (three cloud-heap designs laid by a hash, border block = design a). The way in and out is the stair hatch at (10,12) (the warp to StormsEdge_Lighthouse warp 1, as now).",
        "The iron gallery deck with its railing round the rim, St Elmo's fire on the north rail; the lantern room in the middle (red dome,",
        "lightning rod, the great lens burning; dark until Eclair's grid is restored); hurricane-warning flags, an anemometer, the keeper's",
        "storm lantern, rope, rain puddles and rust on the plates. Zapdos at (10,9) before the lamp, the player at (10,10).",
    ]
    return m


def thundurus(P):
    base = {".": ("P:ekat:grass", True), "~": ("P:ekat:water_C", False), "r": ("ls:riprap0", False), "n": ("ls:slope_n0", False),
            "c": ("ls:crown0", True), "s": ("ls:slope_s0", True), "t": ("ls:toe0", True), "x": ("ls:scorch_C", True)}
    sets = [("x", set_res("ls", "scorch", (".",)), True)]
    m = LairMapB2(20, 16, base, sets, {"ls": P}, wall_style="swamp")
    frame_b2(m, "w", 5, n=[2] + [1] * 8 + [2], s=[2, 1, 2, 1, 1, 1, 1, 1, 1, 2], w=[2, 1, 1, 1, 1, 1, 1, 2], e=[2, 1, 1, 1, 1, 2, 1, 2])
    for (row, ch) in [(2, "~"), (3, "~"), (4, "r"), (5, "n"), (6, "c"), (7, "s"), (8, "t")]:
        m.rect(ch, 0, row, 20, 1)
    m.disc("x", 7.4, 12.0, 1.6, 0.9)                      # where the last bolt came down
    m.reserved |= set([(10, 6), (10, 7), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (10, 9), (10, 8)])
    m.resolve()
    m.fixed = {}
    for y in range(m.H):
        for x in range(m.W):
            n = m.names[y][x]
            for b in ("riprap", "slope_n", "crown", "slope_s", "toe"):
                if n == f"ls:{b}0" and x & 1:
                    m.fixed[(x, y)] = f"ls:{b}1"
    place(m, P, "ls", [(12, 9, "shack"), (15, 9, "bell_post"), (4, 9, "struck_pole"), (8, 12, "glass")], "thundurus")
    for (x, y, n) in [(4, 6, "sandbags"), (14, 6, "sandbags"), (7, 6, "mile_post")]:
        m.prop("ls", n, x, y)                             # on the crown road (a band, not plain ground: placed by hand)
    m.obj("thundurus", 10, 6, "Thundurus (post-game) on the levee crown")
    m.obj("player", 10, 7, "the player on the landward slope, facing north")
    m.weather = "WEATHER_RAIN_THUNDERSTORM"
    m.notes = [
        "20x16, unconnected, swamp canopy over the river and the woods (irregular to the south), the way in from the WEST (rows 10-11),",
        "as the Route 12 steps head east. The levee crown above the river in a thunderstorm, in the in-game levee's colours: riprap at",
        "the waterline, the shaded river face, the shell-and-gravel crown road, the lit landward slope. The watchman's shack with its",
        "storm lantern lit, the crevasse bell, sandbags, a mile marker, a line pole split by lightning and the scorch where it struck.",
        "Thundurus at (10,6) on the crown, the player at (10,7).",
    ]
    return m


# ---------------------------------------------------------------- the woods lairs (lj)

OFFSETS = sorted({(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)}, key=lambda o: (abs(o[0]) + abs(o[1]), o[1], o[0]))


def place(m, P, prefix, items, label, ground="."):
    """Place props at (or, if that spot is taken, by a wall edge or across a terrain seam, as near as possible to) the given cells.
    Cells in m.reserved (the encounter, the stand cell, the arrival and the exits) are never covered. Every cell must hold the
    terrain the prop is drawn on (`ground`, or a 4th item element), so no prop shows a square of the wrong ground round it."""
    reserved = set(getattr(m, "reserved", set()))
    for it in items:
        x, y, n = it[:3]
        need = it[3] if len(it) > 3 else ground
        cv = P.items[n]["cv"]
        for (dx, dy) in OFFSETS:
            cells = [(x + dx + i, y + dy + j) for i in range(cv.cw) for j in range(cv.ch)]
            if all(0 <= cx < m.W and 0 <= cy < m.H and m.g[cy][cx] == need and free(m, cx, cy, need)
                   and (cx, cy) not in reserved for (cx, cy) in cells):
                m.prop(prefix, n, x + dx, y + dy)
                break
        else:
            print(f"{label}: no room for {n} near {(x, y)}")

def galar(P):
    base = {".": ("P:ekat:grass", True), "f": ("lf:floor_C", True)}
    sets = [("f", set_res("lf", "floor", (".",)), True)]
    m = LairMapB2(20, 16, base, sets, {"lf": P}, wall_style="swamp")
    frame_b2(m, "e", 4, n=[2] + [1] * 8 + [2], s=[2, 2, 1, 1, 1, 1, 2, 1, 1, 2], w=[2, 1, 1, 2, 1, 1, 1, 2], e=[2, 1, 1, 1, 1, 1, 2, 2])
    m.disc("f", 10.0, 9.0, 6.2, 3.3)                      # the old dance floor round the bandstand
    m.reserved |= set([(6, 5), (6, 6), (10, 9), (10, 10), (15, 9), (15, 10), (16, 8), (17, 8)])
    m.resolve()
    m.prop("lf", "casemate_glow", 5, 3)
    m.prop("lf", "rampart", 7, 3)
    m.prop("lf", "rampart_ivy", 8, 3)
    m.prop("lf", "casemate", 9, 3)
    m.prop("lf", "rampart_ivy", 11, 3)
    m.prop("lf", "rampart", 12, 3)
    m.prop("lf", "casemate", 13, 3)
    m.prop("lf", "bandstand", 8, 6)
    place(m, P, "lf", [(16, 3, "pier"), (16, 5, "pier"), (3, 9, "lamp"), (16, 10, "lamp"), (7, 12, "cannon"), (5, 12, "carousel_horse"),
                       (9, 12, "shot"), (4, 5, "rubble"), (3, 4, "rubble")], "galar")
    for (x, y) in [(4, 9), (16, 11), (15, 5), (4, 8)]:
        if free(m, x, y):
            m.prop("lf", "festoon", x, y)
    m.obj("moltres_g", 6, 5, "Galarian Moltres (post-game) before its casemate")
    m.obj("articuno_g", 10, 9, "Galarian Articuno (post-game) on the bandstand steps")
    m.obj("zapdos_g", 15, 9, "Galarian Zapdos (post-game) strutting on the dance floor")
    m.obj("player", 10, 10, "the player before the bandstand, facing north (Moltres: stand (6,6); Zapdos: stand (15,10))")
    m.weather = "WEATHER_SHADE (the woods have closed over the fort; the day/night tint makes it at dusk)"
    m.notes = [
        "20x16, unconnected, an irregular swamp canopy wall; the way in from the EAST (rows 8-9), as the Route 14 sally port faces west.",
        "Spanish Fort: an old brick fort in the marsh south of the city, turned jazz-age pleasure garden, then abandoned. The north",
        "rampart with its arched casemates (brick of the Drowned Ward); on the parade ground the bandstand under its verdigris dome,",
        "the cracked terrazzo dance floor, lamp posts with broken globes, strings of dead bulbs, a fallen carousel horse, a cannon.",
        "The three Galarian birds keep it like a band that never left: Moltres in the dark casemate (violet embers) at (6,5),",
        "Articuno on the bandstand steps at (10,9), Zapdos on the dance floor at (15,9). Stand cells (6,6), (10,10), (15,10).",
    ]
    return m


# ---------------------------------------------------------------- Moltres: the sugarhouse (lm, on the interiors' primary)
def moltres(P):
    base = {"f": ("lm:floor", True)}
    m = LairMap(19, 14, base, [], {"lm": P}, wall_style="none", fill="f")
    for x in range(1, 18):
        m.prop("lm", "cap", x, 0)
        m.prop("lm", {3: "wall_window", 7: "wall_window", 11: "wall_window", 15: "wall_window", 5: "wall_tools",
                      13: "wall_tools"}.get(x, "wall"), x, 1)
        m.prop("lm", "wall_s" if x != 9 else "mat", x, 13)
    for y in range(0, 13):
        m.prop("lm", "side_l", 0, y)
        m.prop("lm", "side_r", 18, y)
    m.prop("lm", "wall_sw", 0, 13)
    m.prop("lm", "wall_se", 18, 13)
    for (x, n) in [(2, "batterie"), (5, "sirop"), (8, "flambeau"), (11, "grande")]:
        m.prop("lm", n, x, 3)
    m.prop("lm", "flue", 14, 2)
    m.prop("lm", "cooler", 5, 9)
    m.prop("lm", "cooler", 11, 9)
    m.prop("lm", "cane", 16, 9)
    for (x, y) in [(1, 7), (1, 8), (17, 6), (17, 7), (16, 3)]:
        m.prop("lm", "hogshead", x, y)
    m.prop("lm", "floor_glow_l", 2, 6)
    m.prop("lm", "floor_glow", 3, 6)
    m.prop("lm", "floor_glow_r", 4, 6)
    m.prop("lm", "ash", 6, 7)
    for (x, y) in [(13, 7), (15, 7), (14, 11), (16, 11), (12, 6), (9, 7), (7, 11), (10, 11)]:
        m.prop("lm", "floor_bagasse", x, y)
    m.obj("moltres", 3, 6, "Moltres (post-game) roosting at the batterie, the fire it keeps behind it")
    m.obj("player", 3, 7, "the player, facing north")
    m.weather = "WEATHER_NONE (an interior); the furnace's glow is in the art"
    m.border = "lm:cap (a dark wall top) or the interiors' usual black"
    m.notes = [
        "19x14, an interior (gTileset_OrleansBuilding + its own secondary, like the ice plant), behind the plank door of the",
        "Route 17 sugar mill with the chimney. The door mat at (9,13) (south-arrow warp) leads back out to Route 17 (33,10).",
        "The boiling house: the Jamaica train (four iron kettles in a brick furnace bench, smallest to largest, syrup boiling in",
        "each), the batterie over the open furnace mouth, the flue rising to the chimney stack; the mill shut long ago, but its",
        "fire never went out. Sugar coolers, molasses hogsheads, stacked cane, bagasse on the floor, skimmers and ladles on the",
        "wall, daylight through barred windows. Moltres at (3,6) before the batterie, the player at (3,7).",
    ]
    return m


# ---------------------------------------------------------------- Landorus: the field (lh)
def landorus(P):
    base = {"d": ("P:dry:0_0", True), "c": ("lh:clay_C", True), "t": ("lh:thresh_C", True)}
    sets = [("c", set_res("lh", "clay", ("d",)), True), ("t", set_res("lh", "thresh", ("d",)), True)]
    m = LairMapB2(20, 16, base, sets, {"lh": P}, wall_style="lh", fill="d")
    frame_b2(m, "n", 5, n=[2, 1, 2, 1, 1, 1, 1, 1, 2, 2], s=[2] + [1] * 8 + [2], w=[2, 1, 1, 1, 1, 1, 1, 2], e=[2, 2, 1, 1, 1, 1, 1, 2])
    m.disc("t", 10.5, 5.6, 2.7, 1.5)                      # the threshing floor, just inside the way in
    m.rect("c", 3, 9, 14, 4)                              # the field below the terrace: tilled red clay
    m.reserved |= set([(10, 6), (10, 5), (10, 4), (10, 3)])
    m.resolve()
    for y in (9, 10, 11):
        for x in range(3, 16):
            if m.names[y][x] != "lh:clay_C" or 9 <= x <= 10:
                continue
            n = "cane" if x in (3, 15) else ("pumpkins" if y == 10 else ("corn_a" if (x + y) % 2 else "corn_b"))
            m.prop("lh", n, x, y)
    for x in range(3, 17):
        if x not in (9, 10, 11):
            m.prop("lh", "terrace_a" if x % 2 else "terrace_b", x, 8)
    place(m, P, "lh", [(13, 5, "basket"), (4, 4, "field_tree"), (15, 4, "jar"), (6, 6, "plough"), (12, 11, "scarecrow", "c")], "landorus", ground="d")
    m.obj("landorus", 10, 6, "Landorus (post-game) on the threshing floor")
    m.obj("player", 10, 5, "the player, facing south (the way in is north of the floor)")
    m.weather = "WEATHER_NONE (Route 23's sandstorm drops away in the hollow: the field is still and gold)"
    m.notes = [
        "20x16, unconnected, an irregular wall of the dry scrub (Route 23's border art); the way in from the NORTH (x 10-11), as the",
        "Route 23 field gate opens south. The Field That Always Bears: just inside, the round stone threshing floor where the dry",
        "country's farmers leave the first fruits; below it a dry-stone terrace wall with a way down, and the terraced field of red clay",
        "where the corn stands ripe, the pumpkins swell and the cane is thick whatever the season; a scarecrow, an old plough, a pecan.",
        "Landorus at (10,6) on the threshing floor, the player at (10,5) facing south.",
    ]
    return m


# ---------------------------------------------------------------- the entrances, sealed and open
ENTRANCES = {
    # lair: (placement key in entrances_b2.json, route map, crop (x, y, w, h), sealed actions, open actions)
    "mesprit": ("Route1", "Route1", (14, 20, 14, 12), [("ovl", "spirit_gate_e_moss", 26, 27)], [("ovl", "spirit_gate_e", 26, 27)]),
    "azelf": ("Route23_N", "Route23", (24, 0, 18, 9), [("fill", "dry", 32, 0, 4, 2)], [("ovl", "grove_gap", 33, 1)]),
    "landorus": ("Route23_S", "Route23", (20, 31, 16, 9), [("ovl", "field_gate_shut", 27, 38)], [("ovl", "field_gate", 27, 38)]),
    "thundurus": ("Route12", "Route12", (14, 16, 14, 12), [("ovl", "levee_steps_e_log", 25, 22)], [("ovl", "levee_steps_e", 25, 22)]),
    "zarude": ("Route13_E", "Route13", (14, 19, 14, 12), [("ovl", "liana_curtain_e", 26, 25)], [("ovl", "liana_gap_e", 26, 25)]),
    "ogerpon": ("Route13_W", "Route13", (0, 19, 14, 12), [("ovl", "liana_curtain_w", 0, 25)], [("ovl", "courir_gap_w", 0, 25)]),
    "tornadus": ("Route3", "Route3", (18, 0, 18, 12), [("fill", "swamp_marsh", 27, 0, 2, 2)], []),
    "galar": ("Route14", "Route14", (0, 2, 14, 12), [("ovl", "sally_port_w_bricked", 0, 7)], [("ovl", "sally_port_w", 0, 7)]),
    "moltres": ("Route17", "Route17", (26, 2, 16, 11), [], []),
}

ENTRANCE_NOTES = {
    "mesprit": ["Route 1, the bay in the east canopy beside the north-east pond (cells 26-27, rows 27-28), just east of Mesprit's old cell.",
                "Sealed: a curtain of Spanish moss over the trail between two carved cedar posts. Open from story 45: the pink charms, the trail.",
                "Walking east into (27,27) or (27,28) warps to the Heart Pool; it returns to (26,27) facing west."],
    "azelf": ["Route 23, the feather notch in the north scrub at x 33-34 (11 cells east of the Ursaluna cleft, same make).",
              "Sealed: the notch closed with the scrub block over x 32-35 (its corner cells too, so no square patch), the south edge cells on",
              "row 2 running on. Open from story 45: a cleft with the grove's green beyond, a cedar post with blue charms.",
              "Walking north into (33,1) or (34,1) warps to the Unfailing Spring; it returns to (33,2) facing south."],
    "landorus": ["Route 23, the bay in the south scrub at x 27-28 (rows 37-39), straight south of the road's bend.",
                 "Sealed: a split-rail field gate shut and chained. Open from story 45: the gate swung back, a cart track through.",
                 "Walking south into (27,39) or (28,39) warps to the field; it returns to (27,37) facing north."],
    "thundurus": ["Route 12, the notch in the east canopy at rows 22-23 (x 25-26), east of the road's middle bend and Thundurus' old cell.",
                  "Sealed: a fallen trunk across the trail. Open from story 45: plank steps up the bank into the trees, a storm lantern.",
                  "Walking east into (26,22) or (26,23) warps to the levee; it returns to (24,22) facing west."],
    "zarude": ["Route 13, the bay in the east canopy at rows 25-26, past the dense cypress grove (the deep wood begins there).",
               "Sealed: a curtain of lianas. Open from story 45: the lianas pulled aside, a trail into the trees.",
               "Walking east into (27,25) or (27,26) warps to the Deep Wood; it returns to (26,26) facing west."],
    "ogerpon": ["Route 13, the bay in the west canopy at rows 25-26, across the road from Ogerpon's old cell.",
                "Sealed: a curtain of lianas. Open from story 45: a trail into the trees, a ribbon-stake in the Courir's colours.",
                "Walking west into (0,25) or (0,26) warps to the Courir glade; it returns to (2,25) facing east."],
    "tornadus": ["Route 3, the marsh notch in the north canopy at x 27-28 (rows 1-2), just east of the rest area's dirt spur.",
                 "Route 3 is on the Crescent tileset, which is full (510/512 tiles): no new art, as Raikou's Route 2. Sealed: the notch filled",
                 "with the canopy block (primary pieces). Open from story 45: the notch as built; walking north onto (27,1) or (28,1) warps to",
                 "the Wind's Eye (it returns to (27,2) facing south). wind_gap_n (a windsock, the leaves combed east) is drawn if 16 tiles free up."],
    "galar": ["Route 14, the bay in the west canopy at rows 7-8, the first on the way south out of Crescent City (outside the seam band).",
              "Sealed: the old fort's gate bricked up and grown over. Open from story 45: the brick piers, the trail between them.",
              "Walking west into (0,7) or (0,8) warps to Spanish Fort; it returns to (2,7) facing east."],
    "moltres": ["Route 17, the plank door of the sugar mill with the chimney (cell 33,9), the path already runs to it.",
                "Sealed: the door as built, no warp ('It's barred. Heat comes through the planks.'). Open from story 45: the warp is live.",
                "The Capital tileset is full (508/512): no new art; mill_door_ajar (the door ajar, firelight, 5 tiles) only if tiles are freed.",
                "So sealed and open look the same; the difference is the warp (and the sign-like message while sealed). The lair's mat returns to (33,10)."],
}


def overlay_sheet():
    from PIL import Image as _I
    sheet = _I.open(os.path.join(HERE, "entrances_b2.png")).convert("RGBA")
    art = json.load(open(os.path.join(HERE, "entrances_b2.json")))["pieces"]
    return sheet, art


def overlay_img(sheet, art, name):
    p = art[name]
    crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
    px = crop.load()
    for j in range(crop.height):
        for i in range(crop.width):
            if px[i, j][:3] == (255, 0, 255):
                px[i, j] = (0, 0, 0, 0)
    return crop


def route_grid(route, acts):
    ts, names, blocks, W, H, sec = B1.route_render(route)
    grid = [[blocks[y * W + x] & 0x3FF for x in range(W)] for y in range(H)]
    for a in acts:
        if a[0] == "fill":
            _, style, x0, y0, w, h = a
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    grid[y][x] = names[f"bd:swamp_canopy_{x & 1}{y & 1}" if style.startswith("swamp") else f"bd:dry_scrub_{x & 1}{y & 1}"]
            for x in range(x0, x0 + w):
                n = {"swamp": f"patch:bdg_swamp_S{x & 1}_542aa1ca", "swamp_marsh": f"bd:swamp_S_marsh_{x & 1}"}.get(style, f"bd:dry_S_dry_{x & 1}")
                if n in names:
                    grid[y0 + h][x] = names[n]
    return ts, names, grid, W, H, sec


def entrance_panel(lair, which):
    key, route, (cx, cy, cw, ch), sealed, opened = ENTRANCES[lair]
    acts = sealed if which == "sealed" else opened
    ts, names, grid, W, H, sec = route_grid(route, acts)
    img = Image.new("RGBA", (cw * 16, ch * 16))
    for y in range(cy, cy + ch):
        for x in range(cx, cx + cw):
            img.paste(ts.metatile(grid[y][x]), ((x - cx) * 16, (y - cy) * 16))
    sheet, art = overlay_sheet()
    for a in acts:
        if a[0] == "ovl":
            img.alpha_composite(overlay_img(sheet, art, a[1]), ((a[2] - cx) * 16, (a[3] - cy) * 16))
    return img, route, sec


def route_budget(lair):
    """What the open and sealed overlays cost the route tileset: distinct composited 8x8 tiles (flips free), and how many of them
    fit no palette the route already has (those would need a palette slot or a squeeze)."""
    from arena_art import tiles_of, tile_key
    key, route, crop, sealed, opened = ENTRANCES[lair]
    ts, names, grid, W, H, sec = route_grid(route, [])
    pals = []
    for d, rng in ((f"data/tilesets/primary/orleans_general", range(0, 6)), (f"data/tilesets/secondary/{sec}", range(6, 13))):
        for i in rng:
            try:
                lines = open(os.path.join(ROOT, d, "palettes", f"{i:02d}.pal")).read().split("\n")[4:19]
                pals.append({tuple(int(v) for v in l.split()) for l in lines if l.strip()})
            except FileNotFoundError:
                pass
    sheet, art = overlay_sheet()
    tiles, nofit = set(), set()
    for a in sealed + opened:
        if a[0] != "ovl":
            continue
        o = overlay_img(sheet, art, a[1])
        base = Image.new("RGBA", o.size)
        for j in range(o.height // 16):
            for i in range(o.width // 16):
                base.paste(ts.metatile(grid[a[3] + j][a[2] + i]).convert("RGBA"), (i * 16, j * 16))
        base.alpha_composite(o)
        for t in tiles_of(base.convert("RGB")):
            k = tile_key(t)
            tiles.add(k)
            cols = {tuple((v >> 3) << 3 for v in c) for c in t if c is not None}
            if not any(cols <= p for p in pals):
                nofit.add(k)
    import glob
    from PIL import Image as _I
    tpng = os.path.join(ROOT, "data", "tilesets", "secondary", sec, "tiles.png")
    have = None
    if os.path.exists(tpng):                                     # the last tile in use (tiles.png is padded to whole rows)
        im = _I.open(tpng)
        w, h = im.size
        px = im.load()
        have = 0
        for t in range((w // 8) * (h // 8)):
            tx, ty = (t % (w // 8)) * 8, (t // (w // 8)) * 8
            if any(px[tx + i, ty + j] for i in range(8) for j in range(8)):
                have = t + 1
    return {"route": route, "tileset": sec, "tileset_tiles_now": have, "overlay_tiles_at_most": len(tiles),
            "tiles_fitting_no_existing_palette": len(nofit)}


def entrance_mock(lair, notes):
    a, route, sec = entrance_panel(lair, "sealed")
    b, _, _ = entrance_panel(lair, "open")
    A, B = scale(a.convert("RGB"), 3), scale(b.convert("RGB"), 3)
    f, fb = font(15), font(20)
    bud = route_budget(lair)
    notes = notes + [f"Budget on {bud['tileset']} ({bud['tileset_tiles_now']} tiles now, 512 max): the open + sealed overlays add at most "
                     f"{bud['overlay_tiles_at_most']} tiles; {bud['tiles_fitting_no_existing_palette']} of them fit no existing palette."]
    out = Image.new("RGB", (A.width + B.width + 24, A.height + 40 + 52 + 21 * len(notes)), BG)
    d = ImageDraw.Draw(out)
    d.text((8, 8), "sealed (during the story)", fill=HEAD, font=fb)
    d.text((A.width + 24, 8), "open (story 45)", fill=HEAD, font=fb)
    out.paste(A, (0, 40))
    out.paste(B, (A.width + 24, 40))
    y = A.height + 48
    d.text((8, y), f"{route} entrance to the {lair} lair (route tileset {sec}), 3x", fill=HEAD, font=fb)
    for i, l in enumerate(notes):
        d.text((8, y + 30 + 21 * i), l, fill=FG, font=f)
    return out, bud


def town_door_mock(lair):
    """Uxie and Zapdos: the way in is an existing door in the town (no town change); the panel shows the town at the door and the room
    the way goes through."""
    import struct
    import re
    import render
    L = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"] if "id" in l}

    def room(name):
        dmap = json.load(open(os.path.join(ROOT, f"data/maps/{name}/map.json")))
        lay = L[dmap["layout"]]

        def snake(sym):
            return re.sub(r"(?<!^)(?=[A-Z])", "_", sym.replace("gTileset_", "")).lower()
        t = render.Tilesets(os.path.join(ROOT, f"data/tilesets/primary/{snake(lay['primary_tileset'])}"),
                            os.path.join(ROOT, f"data/tilesets/secondary/{snake(lay['secondary_tileset'])}"))
        raw = open(os.path.join(ROOT, lay["blockdata_filepath"]), "rb").read()
        W, H = lay["width"], lay["height"]
        b = struct.unpack(f"<{W * H}H", raw)
        im = Image.new("RGB", (W * 16, H * 16))
        for y in range(H):
            for x in range(W):
                im.paste(t.metatile(b[y * W + x] & 0x3FF).convert("RGB"), (x * 16, y * 16))
        return im, dmap

    if lair == "uxie":
        town, (cx, cy, cw, ch), door = "OldWater", (17, 26, 15, 12), (24, 34)
        rm, mark = "OldWater_CanoeDocks", [(4, 5, "the boatman: from story 45 he offers to paddle you to the Knowing Pool")]
        notes = ["Uxie: the Old Water is a town and stays as it is. The way is the Canoe Docks' existing door (24,34): inside, the boatman",
                 "(4,5) offers the trip from story 45 (a script warp to the lair's arrival cell, the Rootkin pirogue; no map edit). The lair's",
                 "south gap brings you back into the Canoe Docks at (4,6). Sealed / open: the boatman's line; nothing on the map changes.",
                 "Uxie's old cell (24,29) on the islet north of the docks is freed (keep_open, as batch 1 did)."]
    else:
        town, (cx, cy, cw, ch), door = "StormsEdge", (32, 28, 16, 12), (40, 37)
        rm, mark = "StormsEdge_Lighthouse", [(4, 2, "the stair up to the gallery (warp 1, existing)")]
        notes = ["Zapdos: Storm's Edge stays as it is (and its tileset, Port, is full). The way is the lighthouse's existing door (40,37)",
                 "and the keeper's existing stair (4,2) up to StormsEdge_LighthouseGallery, the lair (that map is redone; it is an 11x9",
                 "Pokemon Center stand-in today). Nothing in the town changes. Sealed / open: the gallery is reachable in the story; its lamp",
                 "is dark until FLAG_STORMS_EDGE_GRID_RESTORED; Zapdos appears from story 45. Zapdos' old cell (22,20) by the bridge is freed."]
    ts, names, grid, W, H, sec = route_grid(town, [])
    a = Image.new("RGB", (cw * 16, ch * 16))
    for y in range(cy, cy + ch):
        for x in range(cx, cx + cw):
            a.paste(ts.metatile(grid[y][x]).convert("RGB"), ((x - cx) * 16, (y - cy) * 16))
    d0 = ImageDraw.Draw(a)
    d0.rectangle([(door[0] - cx) * 16, (door[1] - cy) * 16, (door[0] - cx + 1) * 16 - 1, (door[1] - cy + 1) * 16 - 1], outline=(0, 255, 255), width=2)
    b, dmap = room(rm)
    d1 = ImageDraw.Draw(b)
    for (x, y, label) in mark:
        d1.rectangle([x * 16, y * 16, x * 16 + 15, y * 16 + 15], outline=(255, 255, 0), width=2)
    A, B = scale(a.convert("RGB"), 3), scale(b.convert("RGB"), 3)
    f, fb = font(15), font(20)
    notes = notes + [f"{label} (yellow)" for (_, _, label) in mark]
    out = Image.new("RGB", (A.width + B.width + 24, max(A.height, B.height) + 40 + 52 + 21 * len(notes)), BG)
    d = ImageDraw.Draw(out)
    d.text((8, 8), f"{town}: the existing door (cyan), unchanged", fill=HEAD, font=fb)
    d.text((A.width + 24, 8), f"{rm} (existing room)", fill=HEAD, font=fb)
    out.paste(A, (0, 40))
    out.paste(B, (A.width + 24, 40))
    y = max(A.height, B.height) + 48
    d.text((8, y), f"The way to the {lair} lair: an existing town door (no town change), 3x", fill=HEAD, font=fb)
    for i, l in enumerate(notes):
        d.text((8, y + 30 + 21 * i), l, fill=FG, font=f)
    return out


# ---------------------------------------------------------------- revision 2: irregular walls, an entry on any side
class LairMapB2(LairMap):
    """LairMap plus: walk_fix (cells whose walkability the mock sets by hand after resolving, e.g. a walk laid over water at the gap),
    and edge clearing: every cell the wall's edge pieces stand on is reset to the fill terrain first, so irregular walls never
    meet a terrain set's transition (the edge cells need a plain cell under them)."""

    def __init__(self, W, H, base, sets, pieces, wall_style="swamp", fill="."):
        super().__init__(W, H, base, sets, pieces, wall_style=wall_style, fill=fill)
        self.fill_ch = fill

    def clear_edges(self):
        """Reset the cells under the wall's edge pieces that hold a dual-set terrain (pool, path, clay, shell ...) to the fill, when
        the 2x2 an edge piece stands on is mixed. Water and marsh are kept (the swamp wall has edge pieces for them); the cleared
        area is bounded by the edge cells, so repeated resolves change nothing more."""
        if self.wall_style == "none":
            return
        setch = getattr(self, "clear_chars", None) or ({c for (c, _, _) in self.sets} - {"~", '"', self.fill_ch})
        for y in range(self.H):
            for x in range(self.W):
                if (x, y) in self.wall or not any((x + dx, y + dy) in self.wall for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    continue
                quad = [(i, j) for (i, j) in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)) if 0 <= i < self.W and 0 <= j < self.H]
                if len({self.g[j][i] for (i, j) in quad}) > 1:
                    for (i, j) in quad:
                        if self.g[j][i] in setch:
                            self.g[j][i] = self.fill_ch
        for (i, j) in self.wall:
            if self.g[j][i] in setch:
                self.g[j][i] = self.fill_ch

    def resolve(self):
        self.clear_edges()
        names = super().resolve()
        for (x, y), w in getattr(self, "walk_fix", {}).items():
            self.walk[y][x] = w
        return names


def frame_b2(m, side, gap, n=None, s=None, w=None, e=None):
    """Walls of 2x2 blocks with a depth (in blocks) per block along each side (n / s: 10 entries, w / e: 8), and the way in cut
    through `side` ('n', 's', 'w', 'e') at block `gap` along it. Sets m.entry {arrive, exit} and returns it."""
    BW, BH = (m.W + 1) // 2, (m.H + 1) // 2
    std = lambda L: [2] + [1] * (L - 2) + [2]  # noqa: E731
    n, s, w, e = n or std(BW), s or std(BW), w or std(BH), e or std(BH)
    b = set()
    for k in range(BW):
        b |= {(k, d) for d in range(n[k])}
        b |= {(k, BH - 1 - d) for d in range(s[k])}
    for k in range(BH):
        b |= {(d, k) for d in range(w[k])}
        b |= {(BW - 1 - d, k) for d in range(e[k])}
    deep = 4
    if side == "s":
        b -= {(gap, BH - 1 - d) for d in range(deep)}
    elif side == "n":
        b -= {(gap, d) for d in range(deep)}
    elif side == "w":
        b -= {(d, gap) for d in range(deep)}
    else:
        b -= {(BW - 1 - d, gap) for d in range(deep)}
    m.wall = set()
    for (bx, by) in b:
        for dy in (0, 1):
            for dx in (0, 1):
                m.wall.add((bx * 2 + dx, by * 2 + dy))
    x, y = 2 * gap, 2 * gap
    m.entry = {"s": {"arrive": [x, m.H - 3], "exit": [[x, m.H - 2], [x + 1, m.H - 2]]},
               "n": {"arrive": [x, 2], "exit": [[x, 1], [x + 1, 1]]},
               "w": {"arrive": [2, y], "exit": [[1, y], [1, y + 1]]},
               "e": {"arrive": [m.W - 3, y], "exit": [[m.W - 2, y], [m.W - 2, y + 1]]}}[side]
    m.entry_side = side
    m.reserved = {tuple(m.entry["arrive"])} | {tuple(c) for c in m.entry["exit"]}
    return m.entry


def clump(m, *blocks):
    """Extra wall blocks inside the map (block coordinates): the canopy pushing in."""
    for (bx, by) in blocks:
        for dy in (0, 1):
            for dx in (0, 1):
                m.wall.add((bx * 2 + dx, by * 2 + dy))


def trio_map(P, fill="."):
    base = {".": ("P:ekat:grass", True), "~": ("P:ekat:water_C", False), '"': ("P:ekat:marsh_C", True),
            "p": ("lt:spring_C", False)}
    sets = [("p", set_res("lt", "spring"), False), ("~", water_res, False), ('"', marsh_res, True)]
    return LairMapB2(20, 16, base, sets, {"lt": P}, wall_style="swamp", fill=fill)


def woods_map(P, extra_base=None, extra_sets=()):
    base = {".": ("P:ekat:grass", True), "~": ("P:ekat:water_C", False), '"': ("P:ekat:marsh_C", True),
            "t": ("P:ekat:tallgrass", True)}
    base.update(extra_base or {})
    sets = list(extra_sets) + [("~", water_res, False), ('"', marsh_res, True)]
    return LairMapB2(20, 16, base, sets, {"lj": P}, wall_style="swamp")


def grove(m, x, y, w=4, h=4, base="marsh"):
    """A cypress in its marsh (primary art): the marsh rect (w x h) and the 3x3 tree in it."""
    m.rect('"', x, y, w, h)
    m.resolve()
    cypress(m, x + (w - 3) // 2, y + (h - 3) // 2, base)


def uxie(P):
    m = trio_map(P, fill="~")
    m.clear_chars = {".", "p"}                            # the island keeps off the trees: water all round, under the wall
    frame_b2(m, "s", 5, n=[2, 1, 1, 1, 1, 1, 1, 1, 2, 2], s=[2, 2, 1, 1, 1, 1, 1, 1, 1, 2], w=[2, 1, 1, 2, 1, 1, 1, 2], e=[2, 1, 1, 1, 2, 1, 1, 2])
    m.entry["exit"] = [[10, 14]]                           # (11, 14) is water: the walk is the way out
    m.disc(".", 10.0, 7.5, 7.4, 4.8)                      # the island in the Old Water
    m.disc("p", 10.0, 7.8, 3.4, 1.8)                      # the Knowing Pool on it
    m.reserved |= set([(10, 5), (10, 6)])
    m.resolve()
    walk_line(m, 10, 6, 13)
    m.fixed = {(10, 14): "lt:walk_end", (10, 15): "lt:walk_water"}
    m.walk_fix = {(10, 14): True, (10, 15): True}
    for (x, y) in [(10, 13), (10, 12)]:
        if m.names[y][x].startswith("P:ekat:water") or m.names[y][x].startswith("P:bd:"):
            m.fixed[(x, y)] = "lt:walk_water"
            m.walk_fix[(x, y)] = True
    m.prop("lt", "telling_stone", 9, 3)
    place(m, P, "lt", [(7, 3, "story_post"), (12, 3, "story_post"), (8, 3, "cords"), (11, 3, "cords"), (5, 4, "story_post"),
                       (14, 4, "story_post"), (6, 4, "cords"), (13, 4, "cords"), (4, 8, "reading_stone"), (14, 9, "reading_stone"),
                       (6, 10, "spirit_uxie"), (3, 7, "fern")], "uxie")
    m.resolve()
    for (x, y, n) in [(6, 8, "fog_pool0"), (7, 8, "fog_pool1"), (12, 7, "fog_pool1"), (13, 7, "fog_pool0"),
                      (8, 8, "lotus_y"), (12, 8, "lotus_pads"), (7, 7, "lotus_pads")]:
        if m.names[y][x] == "lt:spring_C" and (x, y) not in occupied(m):
            m.prop("lt", n, x, y)
    # the boatman's pirogue moored beside the walk's end (over the water's edge cells), cypress standing in the open water
    m.fixed[(11, 13)] = "lt:pirogue_0_0"
    m.fixed[(12, 13)] = "lt:pirogue_1_0"
    for (x, y) in [(2, 2), (15, 2), (2, 11), (15, 11)]:
        if all(m.g[y + j][x + i] == "~" and (x + i, y + j) not in m.wall for i in range(3) for j in range(3)):
            cypress(m, x, y, "water")
    scatter(m, "lt", ["fern", "pebbles", "fern"], [(5, 6), (15, 6), (6, 11), (13, 11), (4, 9), (16, 8), (11, 10), (8, 10)])
    m.obj("uxie", 10, 5, "Uxie (post-game) before the telling stone, its eyes shut")
    m.obj("boatman", 12, 14, "the boatman in his pirogue (the way back is the walk south)")
    m.obj("player", 10, 6, "the player at the walk's north end, facing north")
    m.weather = "WEATHER_FOG_HORIZONTAL (the Old Water's own fog)"
    m.notes = [
        "20x16, unconnected, an irregular swamp canopy wall standing in water all round (the Old Water's look: water at every edge,",
        "cypress standing in it). Reached by the Canoe Docks' boatman (post-game); his pirogue is moored at the walk's end.",
        "An island in the Old Water holds the Knowing Pool: a still spring in a kerb of Rootkin cut stone, mist and yellow lotus on it.",
        "A rope-and-plank walk runs from the mooring over the water and across the pool to the telling stone (Uxie's spiral) in a",
        "line of memory posts strung with knotted cords. Uxie at (10,5), the player at (10,6); the way back: the walk south (10,14).",
    ]
    return m


def mesprit(P):
    m = trio_map(P)
    frame_b2(m, "w", 4, n=[2, 2, 1, 1, 1, 1, 1, 1, 2, 2], s=[2, 1, 1, 2, 1, 1, 1, 2, 1, 2], w=[2, 1, 1, 1, 1, 2, 1, 2], e=[2, 1, 2, 1, 1, 1, 1, 2])
    for j in range(m.H):                                  # the Heart Pool: two lobes and a point
        for i in range(m.W):
            x, y = i + 0.5, j + 0.5
            lobe = min(math.hypot(x - 8.1, y - 6.6), math.hypot(x - 12.9, y - 6.6)) <= 2.65
            tri = 7.0 <= y <= 11.6 and abs(x - 10.5) <= max(1.6, (12.3 - y) * 1.0)
            if lobe or tri:
                m.g[j][i] = "p"
    m.reserved |= set([(10, 7), (10, 8)])
    m.resolve()
    for y in range(8, 14):
        if m.names[y][10] == "lt:spring_C":
            m.prop("lt", "step_pool", 10, y)
        elif m.names[y][10] == "lt:spring_S":
            m.prop("lt", "step_spring_S", 10, y)
    m.prop("lt", "spirit_mesprit", 10, 3)                 # in the cleft between the lobes, over the kerb
    place(m, P, "lt", [(6, 3, "garland_post"), (14, 3, "garland_post"),
                                         (4, 6, "garland_post"), (16, 8, "garland_post")], "mesprit")
    m.resolve()
    for (x, y, n) in [(7, 6, "lotus_p"), (13, 6, "lotus_y"), (8, 8, "lotus_pads"), (12, 8, "lotus_p"), (8, 5, "lotus_pads"),
                      (13, 5, "lotus_pads"), (9, 10, "lotus_pads"), (12, 9, "lotus_y"), (9, 7, "lotus_y")]:
        if m.names[y][x] == "lt:spring_C" and (x, y) not in occupied(m):
            m.prop("lt", n, x, y)
    ring = []
    for k in range(64):
        a = 2 * math.pi * k / 64
        x, y = int(round(10.5 + 7.0 * math.cos(a))), int(round(7.6 + 4.6 * math.sin(a)))
        if (x, y) not in ring:
            ring.append((x, y))
    scatter(m, "lt", ["iris_violet", "iris_red", "iris_yellow", "iris_violet", "iris_yellow", "iris_red"],
            [c for c in ring if not (c[0] <= 3 and 7 <= c[1] <= 9)])
    scatter(m, "lt", ["fern", "iris_red", "fern", "iris_violet"], [(4, 11), (15, 11), (6, 12), (13, 12), (3, 10), (16, 5), (5, 4)])
    m.obj("mesprit", 10, 7, "Mesprit (post-game) hovering at the heart of the pool")
    m.obj("player", 10, 8, "the player on the top stepping stone, facing north")
    m.weather = "WEATHER_NONE (Route 1's rain stops at the trees: the pool is the one bright, still place)"
    m.notes = [
        "20x16, unconnected, an irregular swamp canopy wall; the way in from the WEST (rows 8-9), as the Route 1 trail heads east.",
        "The Heart Pool: a heart-shaped spring in a kerb of Rootkin cut stone, pink and yellow American lotus on it, stepping stones up",
        "from its point to its heart, where Mesprit hovers; its standing stone glows pink in the cleft beyond. A ring of Louisiana",
        "irises (violet, copper-red, yellow), cedar posts wound with garlands and ribbons: people come to wish here.",
        "Mesprit at (10,7) over the water (its cell blocks), the player at (10,8) on the top stepping stone.",
    ]
    return m


def azelf(P):
    base = {"d": ("P:dry:0_0", True), ".": ("P:ekat:grass", True), "p": ("lh:spring_C", False), "k": ("lh:crack_C", True),
            "w": ("lh:straw_C", True)}
    sets = [("p", set_res("lh", "spring", (".",)), False), (".", lambda k, o: f"lh:green_{k}" if o <= {"d"} else None, True),
            ("k", set_res("lh", "crack", ("d",)), True), ("w", set_res("lh", "straw", ("d",)), True)]
    m = LairMapB2(20, 16, base, sets, {"lh": P}, wall_style="lh", fill="d")
    frame_b2(m, "s", 5, n=[2, 1, 1, 1, 1, 1, 1, 1, 2, 2], s=[2, 2, 1, 1, 1, 1, 2, 1, 1, 2], w=[2, 1, 2, 1, 1, 1, 1, 2], e=[2, 1, 1, 1, 2, 1, 1, 2])
    m.disc(".", 10.0, 7.4, 5.0, 3.4)                      # the green, only round the spring
    m.disc("p", 10.0, 7.4, 2.8, 1.4)                      # the Unfailing Spring
    for (cx, cy, rx, ry) in [(4.6, 11.6, 1.4, 0.9), (15.6, 11.6, 1.4, 1.0), (16.0, 4.2, 1.0, 0.8)]:
        m.disc("k", cx, cy, rx, ry)                       # cracked earth
    for (cx, cy, rx, ry) in [(4.2, 5.0, 1.3, 1.1), (13.4, 12.3, 1.4, 0.8), (6.6, 12.6, 1.0, 0.7)]:
        m.disc("w", cx, cy, rx, ry)                       # straw-dry grass
    m.reserved |= set([(10, 9), (10, 10), (10, 11), (10, 12)])
    m.resolve()
    m.prop("lh", "boil", 10, 7)
    m.prop("lh", "spirit_azelf", 10, 4)                   # at the spring's head, over the kerb
    place(m, P, "lh", [(6, 8, "split_rock"), (13, 6, "cairn"), (7, 5, "cairn")], "azelf", ground=".")
    place(m, P, "lh", [(3, 7, "scrub_bush"), (16, 7, "scrub_bush"), (3, 3, "scrub_bush"), (16, 2, "scrub_bush"), (12, 13, "scrub_bush"),
                       (5, 9, "roots"), (15, 9, "roots"), (8, 11, "roots"), (4, 12, "cairn_dry"), (16, 12, "cairn_dry"), (14, 3, "cairn_dry"),
                       (6, 3, "cairn_dry"), (3, 9, "cairn_dry"), (17, 9, "scrub_bush"), (12, 11, "roots")], "azelf", ground="d")
    m.obj("azelf", 10, 9, "Azelf (post-game) on the spring's south lip")
    m.obj("player", 10, 10, "the player, facing north")
    m.weather = "WEATHER_SANDSTORM (Route 23's own, faint: it is dust over dry country; or WEATHER_NONE if the user prefers the calm)"
    m.notes = [
        "20x16, unconnected, an irregular wall of the dry scrub (Route 23's border art), the way in from the south (x 10-11).",
        "The Unfailing Spring: dry country, sand and cracked earth, straw-dry grass, thorn scrub, roots crawling toward the water;",
        "only round the spring is the ground green. The spring wells up through white sand in a kerb of Rootkin cut stone, Azelf's blue",
        "standing stone at its head; cairns stacked by those who came for the will to go on; a boulder split by a sapling.",
        "Azelf at (10,9), the player at (10,10).",
    ]
    return m


def zarude(P):
    m = woods_map(P)
    m.fill_ch = "t"
    frame_b2(m, "w", 4, n=[2, 2, 2, 1, 1, 1, 1, 2, 2, 2], s=[2, 2, 1, 1, 1, 1, 1, 1, 2, 2], w=[2, 2, 1, 1, 1, 1, 2, 2], e=[2, 2, 1, 2, 1, 1, 2, 2])
    clump(m, (2, 5), (7, 4))                              # the canopy pushing in
    for y in range(m.H):                                  # undergrowth everywhere in the shade ...
        for x in range(m.W):
            m.g[y][x] = "t"
    for x in range(0, 11):                                # ... but the trail in from the west to the tree
        for y in (8, 9):
            m.g[y][x] = "."
    m.rect(".", 8, 7, 5, 3)                               # and the trodden ground before the bower
    m.rect("~", 8, 10, 5, 2)                              # a black-water slough
    m.reserved |= set([(10, 7), (10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (5, 8), (4, 8), (3, 8)])
    m.resolve()
    m.prop("lj", "great_cypress", 8, 3)
    m.resolve()
    for y in range(9, 13):
        k = {"P:ekat:water_N": "N", "P:ekat:water_C": "C", "P:ekat:water_S": "S"}.get(m.names[y][10])
        if k:
            m.prop("lj", f"log_bridge_{k}", 10, y)
    place(m, P, "lj", [(12, 8, "larder")], "zarude", ground=".")
    place(m, P, "lj", [(6, 6, "palmetto_t"), (13, 8, "palmetto_t"), (7, 6, "fern_t"), (4, 7, "roots_a"),
                       (5, 6, "roots_b"), (12, 5, "roots_a"), (14, 6, "undergrowth"), (5, 4, "undergrowth"), (4, 5, "palmetto_t"),
                       (15, 10, "undergrowth"), (6, 12, "fern_t"), (16, 8, "palmetto_t"), (5, 11, "palmetto_t"), (13, 12, "fern_t"),
                       (3, 6, "fern_t"), (15, 4, "lianas_t"), (6, 10, "lianas_t"), (14, 11, "palmetto_t"), (16, 12, "fern_t"),
                       (13, 4, "undergrowth"), (7, 4, "roots_b"), (3, 11, "undergrowth"), (12, 9, "roots_b")], "zarude", ground="t")
    m.obj("zarude", 10, 7, "Zarude (post-game) before its bower in the great cypress")
    m.obj("player", 10, 8, "the player, facing north")
    m.weather = "WEATHER_SHADE (the deep wood's gloom)"
    m.notes = [
        "20x16, unconnected; the swamp canopy pushes in deep and irregular from every side, with clumps of it standing inside; the way",
        "in from the WEST (rows 8-9), as the Route 13 trail heads east. The Deep Wood: tall grass and undergrowth in the shade, roots",
        "crawling, palmettos and ferns, curtains of lianas; a black-water slough with a fallen trunk across it. At its head the giant",
        "buttressed cypress, Zarude's bower of woven vines in its hollow, the troop's larder beside it.",
        "Zarude at (10,7) before the bower, the player at (10,8).",
    ]
    return m


def ogerpon(P):
    m = woods_map(P, {"r": ("lj:dance_C", True)}, [("r", set_res("lj", "dance", (".",)), True)])
    frame_b2(m, "e", 4, n=[2, 1, 1, 1, 2, 1, 1, 1, 2, 2], s=[2, 2, 1, 1, 1, 1, 2, 1, 1, 2], w=[2, 1, 2, 1, 1, 1, 1, 2], e=[2, 1, 1, 2, 1, 1, 1, 2])
    m.disc("r", 9.4, 8.6, 3.0, 2.2)                       # the dance ring
    m.rect("r", 12, 8, 6, 2)                              # the path in from the east
    m.rect("r", 5, 4, 2, 4)                               # to the mask-maker's bench
    m.rect("r", 9, 4, 2, 3)                               # to the mask at the ring's head
    m.rect("r", 6, 10, 2, 3)                              # to the coop
    m.reserved |= set([(10, 9), (10, 10)])
    m.resolve()
    for (gx, gy) in [(13, 11), (3, 3)]:
        if all(m.g[gy + j][gx + i] == "." and (gx + i, gy + j) not in m.wall and not m.edge_cell(gx + i, gy + j)
               for i in range(-1, 5) for j in range(-1, 4)):
            grove(m, gx, gy, 4, 3)
    place(m, P, "lj", [(10, 3, "mask_teal"), (6, 7, "stake_blue"), (13, 7, "stake_red"), (6, 10, "stake_grey"), (12, 11, "stake_red"),
                       (3, 3, "workbench"), (7, 3, "courir_flag"), (12, 3, "courir_flag"), (3, 6, "capuchons"), (13, 5, "capuchons"),
                       (3, 12, "coop"), (9, 12, "gumbo_pot"), (14, 11, "costumes"), (16, 4, "costumes"), (16, 12, "palmetto"),
                       (14, 3, "palmetto"), (4, 9, "fern_w"), (11, 12, "fern_w"), (15, 6, "fern_w"), (3, 10, "palmetto")], "ogerpon")
    m.obj("ogerpon", 10, 9, "Ogerpon (Teal Mask, post-game) dancing in the ring")
    m.obj("player", 10, 10, "the player, facing north")
    m.weather = "WEATHER_NONE (a sunny clearing in the moss forest)"
    m.notes = [
        "20x16, unconnected, an irregular swamp canopy wall; the way in from the EAST (rows 8-9), as the Route 13 trail heads west.",
        "The Courir glade: paths trampled to bare earth run in from the trail, to the mask-maker's bench and to the coop, round a dance",
        "ring where the Courir de Mardi Gras riders dance. The teal mask on its stake at the ring's head; empty stakes tied with ribbons",
        "in the Wellspring, Hearthflame and Cornerstone colours round it; the Courir's flags, capuchons set out on benches, costumes",
        "drying, the coop (the Courir chases chickens for its gumbo) and the gumbo pot. Ogerpon at (10,9), the player at (10,10).",
    ]
    return m


def tornadus(P):
    m = woods_map(P, {"s": ("lj:shell_C", True)}, [("s", set_res("lj", "shell", (".",)), True)])
    frame_b2(m, "s", 5, n=[2, 1, 1, 1, 1, 1, 1, 2, 1, 2], s=[2, 1, 2, 1, 1, 1, 1, 1, 1, 2], w=[2, 1, 1, 1, 2, 1, 1, 2], e=[2, 1, 1, 1, 1, 1, 2, 2])
    for x in range(m.W):                                  # the chenier: a long ridge of shell and sand running west-east
        y0 = 7.4 + 0.9 * math.sin(x * 0.45)
        for y in range(m.H):
            if abs(y + 0.5 - y0) <= 1.1 and 3 <= x <= 16:
                m.g[y][x] = "s"
    m.disc("s", 10.0, 7.4, 2.7, 1.9)                      # the eye: a bare round of shell on the ridge
    grove(m, 12, 10, 3, 3)                                # cypress in the marsh below the ridge
    m.reserved |= set([(10, 7), (10, 8), (10, 9), (10, 10), (10, 11), (10, 12)])
    m.resolve()
    place(m, P, "lj", [(3, 3, "wind_oak"), (13, 2, "wind_oak"), (3, 10, "wind_oak"), (8, 10, "wind_oak")], "tornadus")
    place(m, P, "lj", [(7, 3, "weathervane"), (12, 3, "chimes"), (3, 7, "chimes"), (16, 6, "sea_oats"), (8, 9, "sea_oats"),
                       (12, 9, "sea_oats"), (4, 6, "sea_oats"), (15, 8, "sea_oats")], "tornadus")
    for k in range(80):                                   # grass combed flat round the eye, the way the wind goes round
        a = 2 * math.pi * k / 80
        for r in (3.8, 4.8):
            x, y = int(round(10.0 + r * 1.4 * math.cos(a))), int(round(7.4 + r * math.sin(a)))
            tx, ty = -math.sin(a), math.cos(a)
            kind = "h" if abs(tx) > 2 * abs(ty) else ("v" if abs(ty) > 2 * abs(tx) else ("a" if tx * ty < 0 else "b"))
            if free(m, x, y) and not (9 <= x <= 11 and y >= 12):
                m.prop("lj", f"comb_{kind}", x, y)
    m.obj("tornadus", 10, 7, "Tornadus (post-game) in the eye")
    m.obj("player", 10, 8, "the player, facing north")
    m.weather = "WEATHER_RAIN (the storm's edge; in the eye itself the air is still)"
    m.notes = [
        "20x16, unconnected, an irregular swamp canopy wall, the way in from the south (x 10-11).",
        "The Wind's Eye: a chenier, a ridge of sand and crushed shell running west-east across the marsh, rippled by the wind, live",
        "oaks on it shorn low and swept east; cypress in the marsh below. On the ridge a bare round of shell where nothing moves,",
        "and round it the grass combed flat in streaks the way the wind goes round; a weathervane swung hard round, shell chimes",
        "streaming, sea oats bent double. Tornadus at (10,7) in the eye, the player at (10,8).",
    ]
    return m


# ---------------------------------------------------------------- the pipeline
TILESETS = [  # (art script, module, recipe dir, sheet, prefix, primary dir, lairs, extends batch 1?)
    ("make_lair_trio.py", "make_lair_trio", "orleans_lair_trio", "lair_trio.png", "lt", "orleans_general",
     "Uxie, Mesprit", None),
    ("make_lair_storm_b2.py", "make_lair_storm_b2", "orleans_lair_storm", "lair_storm_b2.png", "ls", "orleans_general",
     "Raikou (batch 1); Zapdos, Thundurus", "orleans_lair_storm"),
    ("make_lair_woods.py", "make_lair_woods", "orleans_lair_woods", "lair_woods.png", "lj", "orleans_general",
     "Zarude, Ogerpon, Tornadus", None),
    ("make_lair_fort.py", "make_lair_fort", "orleans_lair_fort", "lair_fort.png", "lf", "orleans_general", "the Galarian birds", None),
    ("make_lair_sugarhouse.py", "make_lair_sugarhouse", "orleans_lair_sugarhouse", "lair_sugarhouse.png", "lm", "orleans_building", "Moltres", None),
    ("make_lair_field.py", "make_lair_field", "orleans_lair_field", "lair_field.png", "lh", "orleans_general", "Landorus, Azelf (the Route 23 lairs)", None),
]

LAIRS = [  # (key, title, builder, prefix of its pieces)
    ("uxie", "Uxie's Knowing Pool, by canoe from the Old Water", "uxie", "lt"),
    ("mesprit", "Mesprit's Heart Pool, off Route 1", "mesprit", "lt"),
    ("azelf", "Azelf's Unfailing Spring, off Route 23", "azelf", "lh"),
    ("zapdos", "Zapdos: the lamp gallery of the Storm's Edge lighthouse", "zapdos", "ls"),
    ("thundurus", "Thundurus on the levee crown, off Route 12", "thundurus", "ls"),
    ("zarude", "Zarude's Deep Wood, off Route 13", "zarude", "lj"),
    ("ogerpon", "Ogerpon's Courir glade, off Route 13", "ogerpon", "lj"),
    ("tornadus", "Tornadus in the Wind's Eye, off Route 3", "tornadus", "lj"),
    ("galar", "The Galarian birds at Spanish Fort, off Route 14", "galar", "lf"),
    ("moltres", "Moltres in the sugarhouse of the Route 17 mill", "moltres", "lm"),
    ("landorus", "Landorus: the Field That Always Bears, off Route 23", "landorus", "lh"),
]

ENTRY = {
    "uxie": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "OldWater_CanoeDocks (4,6), facing north (the boatman paddles you back)"},
    "mesprit": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route1 (26,27), facing west"},
    "azelf": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route23 (33,2), facing south"},
    "zapdos": {"arrive": [10, 12], "exit": [[10, 12]], "to": "StormsEdge_Lighthouse warp 1 (the stair, as the gallery's warp is now)"},
    "thundurus": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route12 (24,22), facing west"},
    "zarude": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route13 (26,26), facing west"},
    "ogerpon": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route13 (2,25), facing east"},
    "tornadus": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route3 (27,2), facing south"},
    "galar": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route14 (2,7), facing east"},
    "moltres": {"arrive": [9, 12], "exit": [[9, 13]], "to": "Route17 (33,10), facing south (the mill door)"},
    "landorus": {"arrive": [10, 13], "exit": [[10, 14], [11, 14]], "to": "Route23 (27,37), facing north"},
}

BEFORE = {
    "uxie": "Before story 45 the Canoe Docks' boatman only talks; from story 45 he offers the trip (no map change in the Old Water).",
    "mesprit": "Before story 45 the Route 1 gap is a curtain of Spanish moss on the spirit gate; afterwards the moss is parted.",
    "azelf": "Before story 45 the Route 23 gate is hung with a curtain of moss; afterwards it is open, the grove's green showing.",
    "zapdos": "The gallery is reachable during the story (the keeper's stair): the same deck, the lamp dark (lantern_dark) until "
              "FLAG_STORMS_EDGE_GRID_RESTORED, lit after; Zapdos only from story 45 (FLAG_PG_ZAPDOS).",
    "thundurus": "Before story 45 the Route 12 levee ramp is closed by a fallen trunk across the trail; afterwards it is cleared.",
    "zarude": "Before story 45 the Route 13 trail east is a curtain of lianas; afterwards the lianas are parted.",
    "ogerpon": "Before story 45 the Route 13 trail west is a curtain of lianas; afterwards a Courir flag marks it, open.",
    "tornadus": "Before story 45 the Route 3 gap in the canopy is overgrown (the canopy as built); afterwards a wind-bent trail opens.",
    "galar": "Before story 45 the Route 14 sally port is bricked up and overgrown; afterwards the brick has fallen in and it is open.",
    "moltres": "Before story 45 the mill door is barred (a locked-door message: heat comes through the planks); afterwards the bar is off.",
    "landorus": "Before story 45 the Route 23 field gate is shut and chained; afterwards it stands open.",
}


def bfs(m, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < m.W and 0 <= ny < m.H and (nx, ny) not in seen and m.walk[ny][nx]:
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


def build_lairs(mods, stats, only=None):
    imgs, maps = {}, {}
    os.makedirs(REVIEW, exist_ok=True)
    for (key, title, fn, prefix) in LAIRS:
        if only and key not in only:
            continue
        m = globals()[fn](mods[prefix])
        img = m.render()
        imgs[key], maps[key] = img, m
        rec = [r for r in TILESETS if r[4] == prefix][0]
        st = stats.get(rec[2])
        enc = [o for o in m.objs if o[0] not in ("player", "boatman", "npc")]
        player = [o for o in m.objs if o[0] == "player"]
        entry = dict(ENTRY[key], **getattr(m, "entry", {}))
        arrive = tuple(entry["arrive"])
        reach = bfs(m, arrive) if m.walk[arrive[1]][arrive[0]] else set()
        checks = []
        if arrive not in reach:
            checks.append(f"arrival {arrive} does not walk")
        if player and (player[0][1], player[0][2]) not in reach:
            checks.append(f"player cell {(player[0][1], player[0][2])} unreachable")
        for e in entry["exit"]:
            if tuple(e) not in reach:
                checks.append(f"exit {e} unreachable")
        lines = m.notes + ["Weather: " + getattr(m, "weather", "WEATHER_NONE"), "Before it opens: " + BEFORE[key]]
        if st:
            lines.append(f"Tileset {rec[2]} ({rec[6]}): {st[0]}")
        if m.problems:
            lines.append(f"autotile conflicts left in the mock: {len(m.problems)}: {m.problems[:3]}")
        if checks:
            lines.append("WALK CHECK: " + "; ".join(checks))
        print(key, "conflicts:", m.problems, "checks:", checks)
        caption(img, title + " - mock, 3x", lines).save(os.path.join(REVIEW, f"{key}_mock.png"))
        m.export(os.path.join(REVIEW, f"{key}_mock.json"), {
            "tileset": rec[2], "primary": rec[5],
            "encounter_cells": [{"species": o[0], "cell": [o[1], o[2]], "label": o[3]} for o in enc],
            "encounter_cell": [enc[0][1], enc[0][2]] if enc else None,
            "player_cell": [player[0][1], player[0][2]] if player else None,
            "entry": entry, "before": BEFORE[key], "weather": getattr(m, "weather", "WEATHER_NONE"),
            "walk_check": checks or "ok"})
    return imgs, maps


def run_art(only_scripts=None):
    for r in TILESETS:
        if only_scripts and r[1] not in only_scripts:
            continue
        p = subprocess.run([sys.executable, os.path.join(HERE, r[0])], cwd=ROOT, capture_output=True, text=True)
        if p.returncode:
            raise SystemExit(p.stdout + p.stderr)
        print(p.stdout.strip().splitlines()[-1])


def load_mods():
    import importlib
    mods = {}
    for r in TILESETS:
        M = importlib.import_module(r[1])
        P = M.build()
        P.pack()
        mods[r[4]] = P
    return mods


def compose_all():
    stats = {}
    for (script, mod, rdir, png, prefix, prim, lairs, ext) in TILESETS:
        line, pal, out = stage_compose(rdir, png)
        off, worst = stage_verify(rdir, png, prefix, prim)
        squeeze = [p for p in pal if "in 15" in p or "reduced" in p]
        stats[rdir] = (line, squeeze, off, worst, lairs, pal)
        print(line, squeeze or "no squeeze", f"off {off} worst {worst:.1f}")
    return stats


def entrances(only=None):
    buds = {}
    for lair in ENTRANCES:
        if only and lair not in only:
            continue
        img, bud = entrance_mock(lair, ENTRANCE_NOTES[lair])
        img.save(os.path.join(REVIEW, f"{lair}_entrance.png"))
        buds[lair] = bud
    for lair in ("uxie", "zapdos"):
        if only and lair not in only:
            continue
        town_door_mock(lair).save(os.path.join(REVIEW, f"{lair}_entrance.png"))
    return buds


def review_sheet(mods, stats):
    from lair_kit import tiles_of_count
    keys = ("N", "S", "W", "E", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW", "landNE", "landNW", "sTLBR", "sTRBL")
    secs = []
    for (script, mod, rdir, png, prefix, prim, lairs, ext) in TILESETS:
        P = mods[prefix]
        b1 = set()
        if ext:                                                   # a batch-1 superset: show only the batch-2 pieces
            import importlib
            b1 = set(importlib.import_module({"orleans_lair_storm": "make_lair_storm"}[ext]).build().order)
        items = []
        for n in P.order:
            if n in b1 or ("_" in n and n.rsplit("_", 1)[1] in keys and not n.startswith("walk_") and not n.startswith("step_")):
                continue
            cv = P.items[n]["cv"]
            items.append((cv.im, f"{n} {cv.cw}x{cv.ch}: {tiles_of_count(cv.im)} t"))
        st = stats.get(rdir)
        sub = (f"{st[0]}  |  budget 512 tiles / 512 metatiles / 7 palettes  |  squeeze: {st[1] or 'none'}  |  metatiles off their art: "
               f"{st[2]} (worst shift {st[3]:.0f})" if st else "")
        title = f"{rdir} (prefix {prefix}, on {prim}): {lairs}" + (" - batch-2 pieces only (the batch-1 ones are unchanged, first)" if ext else "")
        secs.append(B1.section(items, title, sub + "  |  corner sets: C only; 4x, t = distinct 8x8 tiles", k=4))
    ent = json.load(open(os.path.join(HERE, "entrances_b2.json")))
    sheet = Image.open(os.path.join(HERE, "entrances_b2.png")).convert("RGBA")
    items = []
    for n, p in ent["pieces"].items():
        crop = sheet.crop((p["x"] * 16, p["y"] * 16, (p["x"] + p["w"]) * 16, (p["y"] + p["h"]) * 16))
        items.append((crop, f"{n} {p['w']}x{p['h']} overlay"))
    secs.append(B1.section(items, "Route entrances, batch 2 (overlays, source le2; magenta = clear; each snapped into its route's palettes)",
                           "Route 1 spirit gate, Route 23 grove gap + field gate, Route 12 levee steps, Route 13 liana gaps, Route 14 sally "
                           "port; Route 3 and Route 17: no art by default (Crescent and Capital are full)", k=4))
    W = max(x.width for x in secs)
    out = Image.new("RGB", (W, sum(x.height for x in secs)), BG)
    y = 0
    for x in secs:
        out.paste(x, (0, y))
        y += x.height
    out.save(os.path.join(REVIEW, "art_lairs_b2.png"))
    print("wrote art_lairs_b2.png", out.size)


def overview(imgs):
    """00_batch2_sheet.png: every batch-2 mock at 2x, titled, in a grid."""
    f = font(18)
    cells = []
    for (key, title, fn, prefix) in LAIRS:
        if key in imgs:
            cells.append((key, title, scale(imgs[key].convert("RGB"), 2)))
    cw = max(c[2].width for c in cells) + 20
    chh = max(c[2].height for c in cells) + 40
    cols = 4
    rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * cw + 20, rows * chh + 70), BG)
    d = ImageDraw.Draw(out)
    d.text((14, 14), "Legendary lairs, batch 2: every mock at 2x (details and captions in <lair>_mock.png)", fill=HEAD, font=font(24))
    for k, (key, title, im) in enumerate(cells):
        x, y = 14 + (k % cols) * cw, 60 + (k // cols) * chh
        d.text((x, y), title, fill=FG, font=f)
        out.paste(im, (x, y + 28))
    out.save(os.path.join(REVIEW, "00_batch2_sheet.png"))
    print("wrote 00_batch2_sheet.png", out.size)


def main():
    args = sys.argv[1:]
    only = [a for a in args if not a.startswith("--")]
    if "--no-art" not in args:
        run_art()
        subprocess.run([sys.executable, os.path.join(HERE, "make_entrances_b2.py")], cwd=ROOT, check=True, capture_output=True)
    mods = load_mods()
    stats = compose_all() if "--no-compose" not in args else {}
    imgs, maps = build_lairs(mods, stats, only or None)
    buds = entrances(only or None)
    if not only:
        dump(os.path.join(REVIEW, "entrance_budgets_b2.json"), buds)
        if stats:
            review_sheet(mods, stats)
        overview(imgs)
    dump(os.path.join(REVIEW, "budgets_b2.json"), {k: {"line": v[0], "squeeze": v[1], "cells_off": v[2], "worst_shift": v[3],
                                                       "lairs": v[4], "palette": v[5]} for k, v in stats.items()})


if __name__ == "__main__":
    main()

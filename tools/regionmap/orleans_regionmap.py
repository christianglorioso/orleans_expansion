"""The Orleans region map (Town Map / Fly map / Pokenav map / Pokedex area map): art, cell layout and review sheets.

usage (from the decomp root):  python tools/regionmap/orleans_regionmap.py

Everything is drawn from the data at the top of this file (grid coordinates, see below), so a change to a town,
a route or the coast is one edit here and a rerun.  Nothing under data/, src/ or graphics/ is touched: the outputs
go to tools/regionmap/out/ and the review images to C:/Users/chris/orleans_expansion/region_map/.  A code agent
copies the out/ files into graphics/ and src/data/region_map/ (see region_map/01_wiring_plan.md).

Grid coordinates.  The cursor grid is 28 x 15 cells (MAP_WIDTH x MAP_HEIGHT in src/region_map.c); cell (cx, cy)
is drawn at tilemap tile (cx + 1, cy + 2) (MAPCURSOR_X_MIN / MAPCURSOR_Y_MIN).  A point (gx, gy) in grid units is
pixel ((gx + 1) * 8, (gy + 2) * 8) of the 64x64-tile affine BG; the visible screen is the first 30 x 20 tiles,
i.e. gx in [-1, 29), gy in [-2, 18).  Cell centres are (cx + 0.5, cy + 0.5).

Engine format (vanilla): 8bpp tiles, affine BG with a 64x64 one-byte tilemap (no flips, <= 256 tiles; vanilla
ships 233 and builds with -num_tiles 233), the palette is loaded at BG palette 7 (colours 112..159, 48 entries).
The Pokedex area screen uses the same picture as a text BG (32x32 u16 entries, 8bpp, built with -num_tiles 232).
This script keeps the unique tile count at or under 232 so both builds take it unchanged.

Outputs (tools/regionmap/out/):
  map.png / map.bin / map.pal            -> graphics/pokenav/region_map/  (Fly map, Town Map, Pokenav)
  dex_region_map.png / .bin / .pal       -> graphics/pokedex/region_map.* (Pokedex area screen)
  region_map_art_1x.png                  the 240x160 source picture (indexed, palette at 112+)
  region_map_layout.h                    sRegionMap_MapSectionLayout for Orleans (MAP_HEIGHT x MAP_WIDTH)
  sections.json                          every Orleans section: name, cells, entry rect, marker kind, icon path
  region_map_orleans_paths.h             sOrleansRoutePaths: the player icon cells along each route
Review images (region_map/):
  region_map_mock.png      the Fly screen as the GBA shows it (frame, icons, cursor, name box), 3x
  region_map_full_3x.png   the whole 30x20-tile picture, 3x
  02_cells_sheet.png       every cell labelled with its section, cursor grid, 4x, plus the legend
"""
import json
import math
import os
import struct
import sys
from collections import Counter, defaultdict

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "out")
DOCS = os.path.normpath(os.path.join(ROOT, "..", "region_map"))
VANILLA = os.path.join(ROOT, "graphics", "pokenav", "region_map")

MAP_W, MAP_H = 28, 15          # cursor grid
OFF_X, OFF_Y = 1, 2            # MAPCURSOR_X_MIN, MAPCURSOR_Y_MIN
SCREEN_TW, SCREEN_TH = 30, 20  # visible tiles
W, H = SCREEN_TW * 8, SCREEN_TH * 8
TILE_BUDGET = 232

# ------------------------------------------------------------------ palette (BG palette 7..9 = colours 112..159)
# The first 29 entries are the vanilla Hoenn map colours at the same indices (113..140), so the markers, water and
# route shading are the original ones; the Orleans terrain colours follow.
PALETTE = [
    ("K", (0, 0, 0)),          # 112 unused (black)
    ("w", (156, 213, 255)),    # 113 shallow water
    ("W", (164, 180, 255)),    # 114 shallow water stripe
    ("s", (123, 180, 213)),    # 115 small-town marker light
    ("b", (74, 156, 230)),     # 116 river / boat route
    ("B", (41, 131, 230)),     # 117 river / boat route stripe
    ("c", (65, 106, 205)),     # 118 deep water
    ("C", (0, 115, 172)),      # 119 small-town marker
    ("d", (32, 74, 197)),      # 120 deep water stripe
    ("D", (0, 57, 139)),       # 121 small-town marker dark
    ("1", (213, 255, 123)),    # 122 land highlight
    ("2", (172, 238, 49)),     # 123 land light
    ("3", (98, 213, 0)),       # 124 land
    ("4", (57, 172, 8)),       # 125 land shade
    ("5", (0, 115, 0)),        # 126 coast / dark green
    ("k", (205, 205, 148)),    # 127 (vanilla khaki; unused)
    ("n", (33, 115, 82)),      # 128 marsh dark (tufts, marsh shore)   [vanilla: unused black]
    ("#", (255, 255, 255)),    # 129 white
    ("a", (238, 230, 172)),    # 130 pale sand
    ("A", (238, 230, 115)),    # 131 sand yellow
    ("o", (238, 189, 57)),     # 132 road
    ("O", (246, 213, 82)),     # 133 road light
    ("r", (230, 164, 0)),      # 134 road edge
    ("R", (255, 172, 16)),     # 135 city marker
    ("x", (255, 57, 16)),      # 136 city marker red
    ("X", (246, 0, 0)),        # 137 red
    ("z", (148, 0, 0)),        # 138 city marker dark
    ("g", (205, 205, 205)),    # 139 marker rim light
    ("G", (98, 98, 98)),       # 140 marker rim dark
    ("m", (90, 180, 106)),     # 141 marsh
    ("M", (65, 148, 90)),      # 142 marsh shade
    ("t", (222, 197, 123)),    # 143 dry country
    ("u", (180, 139, 82)),     # 144 dry country shade / dry shore
    ("v", (139, 98, 57)),      # 145 dry country dark (salt-dome rim, gullies)
    ("f", (24, 98, 41)),       # 146 moss forest dark
    ("F", (49, 139, 41)),      # 147 moss forest
    ("p", (205, 49, 49)),      # 148 pepper rows
]
PAL_BASE = 112
CI = {ch: PAL_BASE + i for i, (ch, _) in enumerate(PALETTE)}
RGB = {PAL_BASE + i: rgb for i, (_, rgb) in enumerate(PALETTE)}
assert len(PALETTE) <= 48

# ------------------------------------------------------------------ geography (grid units)
# Converted from the region design map (orleans_maps/00_orleans_region.png: gx = x * 28 / 1595, gy = (y - 75) / 75)
# and tuned so every town and route lands on its own cell.

# The Fly screen's name box covers cursor row 14 from column 15 on (vanilla keeps that corner empty too), so the
# south-east (the delta, Land's End, Routes 21-22) sits one row higher than the design map and row 14 is open Gulf.
COAST = [(-1.5, 12.25), (1.5, 12.2), (3.0, 12.3), (5.0, 12.4), (6.5, 12.55), (8.0, 12.7), (9.5, 12.9),
         (10.5, 13.05), (11.5, 13.1), (13.0, 13.2), (14.0, 13.15), (16.0, 13.1), (18.0, 13.0), (20.0, 12.95),
         (22.0, 12.95), (24.0, 13.0), (25.5, 13.05), (26.0, 13.25), (26.6, 13.3), (27.05, 13.0), (27.6, 12.8),
         (29.5, 12.7)]
DEEP = [(-1.5, 14.75), (3.0, 14.6), (7.0, 14.75), (10.0, 14.75), (12.5, 14.35), (15.0, 14.0), (19.0, 13.85),
        (23.0, 13.95), (27.0, 13.9), (29.5, 13.8)]

LAKES = {
    "pointe_lake": [(8.4, 1.3), (9.0, 0.9), (10.0, 0.95), (10.55, 1.3), (10.35, 1.9), (9.5, 2.0), (8.7, 1.85)],
    "basin_lake": [(7.0, 6.35), (7.8, 5.95), (9.0, 6.0), (9.85, 6.45), (9.95, 7.2), (9.2, 7.6), (8.0, 7.5),
                   (7.2, 7.1)],
    "big_lake": [(17.55, 8.55), (17.85, 7.6), (18.8, 6.75), (20.0, 6.35), (21.4, 6.45), (22.5, 6.25), (23.35, 6.6),
                 (23.5, 7.25), (23.0, 8.0), (21.8, 8.4), (20.5, 8.55), (19.4, 8.75), (18.3, 8.95)],
    "old_water_pool": [(1.45, 10.25), (2.2, 9.95), (2.95, 10.3), (2.75, 11.0), (1.8, 11.1)],
}
# land inside water (drawn after the lakes and the Gulf)
ISLANDS = {
    "isle_marais": ("ellipse", (4.45, 13.6), (1.2, 0.62), "marsh"),
    "suicune_islet": ("ellipse", (20.6, 6.78), (0.3, 0.17), "plain"),
    # marsh islets off the coast and in the delta mouth
    "islet_w": ("ellipse", (1.0, 12.85), (0.45, 0.2), "marsh"),
    "islet_c1": ("ellipse", (7.4, 13.45), (0.4, 0.18), "marsh"),
    "islet_c2": ("ellipse", (13.2, 13.75), (0.32, 0.16), "marsh"),
    "islet_d1": ("ellipse", (19.6, 13.35), (0.42, 0.15), "marsh"),
    "islet_d2": ("ellipse", (28.0, 13.2), (0.35, 0.14), "marsh"),
}
RIVERS = {  # name: (points, width in px)
    "emerald": ([(11.6, -2.5), (11.7, 0.0), (11.85, 1.6), (11.95, 2.6), (12.15, 3.6), (12.45, 4.6), (13.4, 5.3),
                 (14.6, 6.2), (15.4, 7.1), (15.9, 8.1), (16.4, 9.0), (17.2, 9.75), (18.4, 10.35), (19.5, 10.75),
                 (20.5, 11.5), (24.5, 11.5), (24.5, 12.5), (26.5, 12.5), (26.8, 13.0), (27.1, 13.3)], 3),
    "west_river": ([(7.0, -2.5), (7.1, 0.0), (7.4, 1.6), (7.9, 3.2), (8.35, 4.3), (8.5, 5.3), (8.45, 6.1)], 2),
    "west_river_south": ([(9.5, 7.4), (9.85, 8.4), (10.1, 9.6), (10.3, 10.8), (10.45, 12.0), (10.55, 13.3)], 2),
    "tributary": ([(-1.5, 4.45), (0.5, 4.3), (2.5, 4.55), (4.5, 4.4), (6.5, 4.55), (8.3, 4.45)], 2),
    "old_water_channel": ([(2.7, 10.5), (3.4, 10.45), (4.3, 10.45)], 2),
    # bayou channels (1 px)
    "bayou_coast_w": ([(5.6, 12.6), (6.2, 11.7), (5.9, 11.0), (6.6, 10.4)], 1),
    "bayou_coast_e": ([(12.6, 13.0), (13.0, 12.2), (12.5, 11.4)], 1),
    "bayou_basin": ([(3.6, 6.9), (4.6, 7.2), (5.6, 6.8), (6.2, 6.6)], 1),
    "delta_1": ([(22.0, 11.9), (22.3, 12.5), (22.0, 13.1)], 1),
    "delta_2": ([(23.4, 12.0), (23.7, 12.6), (23.5, 13.15)], 1),
}
# land types other than plain (order: later wins)
REGIONS = [
    ("marsh", [(2.7, 7.4), (2.5, 6.6), (2.8, 5.8), (3.4, 4.7), (4.1, 4.1), (5.0, 4.0), (5.8, 3.7), (6.8, 3.85),
               (7.6, 3.6), (8.8, 3.85), (9.8, 3.7), (10.6, 4.1), (11.3, 4.4), (12.5, 5.6), (14.1, 6.8), (14.75, 7.8),
               (14.55, 8.6), (13.4, 8.75), (12.6, 8.45), (12.0, 8.6), (11.2, 8.1), (10.4, 8.25), (9.6, 7.95),
               (8.7, 8.2), (7.6, 7.9), (6.6, 8.15), (5.6, 7.8), (4.6, 8.05), (3.6, 7.75)]),     # the Basin
    ("marsh", [(-1.5, 9.1), (0.4, 8.8), (1.5, 9.05), (2.5, 8.75), (3.5, 8.95), (4.6, 8.7), (5.8, 9.0), (6.7, 8.75),
               (7.6, 8.85), (8.5, 8.5), (9.3, 8.65), (10.1, 8.45), (10.8, 8.6), (12.0, 8.95), (13.6, 9.2),
               (14.4, 9.9), (14.2, 11.0), (13.6, 12.2), (12.4, 12.8), (11.0, 13.4), (9.0, 13.4), (6.0, 13.2),
               (3.0, 13.0), (-1.5, 13.0)]),                                                   # the coastal marsh
    ("forest", [(21.6, -2.5), (29.5, -2.5), (29.5, 6.0), (27.6, 6.25), (26.5, 5.95), (25.4, 6.15), (24.5, 5.8),
                (23.7, 5.6), (23.0, 4.9), (22.7, 4.2), (22.1, 3.6), (22.0, 2.8), (21.5, 2.2), (21.6, 1.4),
                (21.2, 0.7), (21.5, -0.4)]),                                                 # the moss forest
    ("dry", [(12.9, -2.5), (21.2, -2.5), (21.1, -0.6), (20.7, 0.4), (21.0, 1.1), (20.5, 1.7), (19.6, 2.0),
             (18.8, 2.4), (17.5, 2.35), (16.6, 2.75), (15.6, 2.7), (14.6, 3.05), (13.9, 2.8), (13.5, 2.2),
             (13.6, 1.5), (13.1, 0.9), (13.35, 0.1), (12.95, -0.8)]),                       # the high dry country
    ("sugar", [(14.3, 10.25), (15.8, 9.95), (16.9, 10.25), (17.7, 11.0), (18.4, 11.45), (19.3, 11.75),
               (18.6, 12.4), (17.7, 12.75), (15.3, 12.75), (14.4, 12.1)]),                    # sugar country
    ("pepper", [(17.2, 10.45), (18.4, 10.3), (18.95, 10.7), (18.85, 11.8), (17.6, 11.85), (17.1, 11.2)]),  # peppers
    ("marsh", [(21.0, 11.15), (22.4, 11.05), (23.6, 11.2), (24.9, 11.15), (25.2, 12.0), (26.9, 12.2),
               (27.4, 13.6), (21.2, 13.6), (20.75, 12.7), (21.05, 12.2), (20.8, 11.7)]),     # the delta
]

# ------------------------------------------------------------------ sections
# kind: town_small (blue round), town (red round), city (red pill), site (gold diamond), frontier (red diamond)
TOWNS = [
    # mapsec,                  name,             cell,     w, h, kind
    ("MAPSEC_ISLE_MARAIS", "ISLE MARAIS", (4, 13), 1, 1, "town_small"),
    ("MAPSEC_OLD_WATER", "THE OLD WATER", (2, 10), 1, 1, "town_small"),
    ("MAPSEC_GRAND_OAK", "GRAND OAK", (4, 9), 1, 1, "town"),
    ("MAPSEC_STORMS_EDGE", "STORM'S EDGE", (10, 12), 1, 1, "town"),
    ("MAPSEC_CRESCENT_CITY", "CRESCENT CITY", (16, 9), 2, 1, "city"),
    ("MAPSEC_POINTE_ROUGE", "POINTE ROUGE", (12, 2), 2, 1, "city"),
    ("MAPSEC_CAMP_COCODRIE", "CAMP COCODRIE", (6, 6), 1, 1, "town"),
    ("MAPSEC_LUTINS_HOLLOW", "LUTIN'S HOLLOW", (25, 3), 1, 1, "town"),
    ("MAPSEC_REDFIELD", "REDFIELD", (20, 11), 1, 1, "town"),
    ("MAPSEC_LANDS_END", "LAND'S END", (26, 12), 1, 1, "town"),
    ("MAPSEC_OLDEST_SHRINE", "OLDEST SHRINE", (8, 4), 1, 1, "site"),
    ("MAPSEC_SALT_DOME", "SALT DOME", (18, 1), 1, 1, "site"),             # new section (proposed)
    ("MAPSEC_DROWNED_TEMPLE", "DROWNED TEMPLE", (21, 13), 1, 1, "site"),  # new section (proposed)
    ("MAPSEC_BATTLE_FRONTIER", "BATTLE FRONTIER", (15, 10), 1, 1, "frontier"),
]

# routes: (number, foot|boat, polyline).  Cells are the ones the line runs through (see route_cells), minus
# town/site cells, plus CELL_FIX.
# Routes are straight bands with right-angle corners only, like vanilla Emerald (user, 2026-10-13).  Each line runs
# through cell centres (x.5) in world.WORLD order; where two places are diagonal the corner is the one closest to the
# design map.  The band fills its cells (square ends and corners: see band_dist).
ROUTES = [
    (1, "foot", [(4.5, 9.5), (4.5, 13.5)]),                                  # Grand Oak S -> Isle Marais
    (2, "foot", [(4.5, 9.5), (7.5, 9.5), (7.5, 12.5), (10.5, 12.5)]),        # Grand Oak E, down the coast, Storm's Edge W
    (3, "foot", [(10.5, 12.5), (13.5, 12.5), (13.5, 9.5), (16.5, 9.5)]),     # Storm's Edge E, north, Crescent W
    (4, "foot", [(13.5, 2.5), (13.5, 4.95)]),                                # Pointe Rouge S, the river's east bank
    (5, "foot", [(12.5, 2.5), (9.05, 2.5)]),                                 # Pointe Rouge W, under the Pointe lake
    (6, "boat", [(12.95, 7.5), (16.5, 7.5), (16.5, 9.5)]),                   # the canal into Crescent from the north-west
    (7, "boat", [(9.95, 6.5), (10.5, 6.5), (10.5, 7.5), (12.95, 7.5)]),
    (8, "boat", [(7.95, 6.5), (9.95, 6.5)]),                                 # across the Basin lake
    (9, "boat", [(6.5, 6.5), (7.95, 6.5)]),                                  # Camp Cocodrie E
    (10, "boat", [(17.5, 9.5), (18.5, 9.5), (18.5, 7.95)]),                  # Crescent E, north onto the Big Lake
    (11, "boat", [(18.5, 7.95), (18.5, 7.5), (22.95, 7.5)]),                 # across the Big Lake
    (12, "foot", [(22.95, 7.5), (23.5, 7.5), (23.5, 3.95)]),                 # north along the forest edge
    (13, "foot", [(23.5, 3.95), (23.5, 3.5), (25.5, 3.5)]),                  # east into Lutin's Hollow
    (14, "foot", [(16.5, 9.5), (16.5, 10.95)]),                              # Crescent S (levee road)
    (15, "foot", [(16.5, 10.95), (16.5, 12.5), (16.95, 12.5)]),
    (16, "foot", [(16.95, 12.5), (18.95, 12.5)]),
    (17, "foot", [(18.95, 12.5), (19.5, 12.5), (19.5, 11.5), (20.5, 11.5)]),  # up to Redfield's mill road
    (18, "boat", [(20.5, 11.5), (23.95, 11.5)]),                             # down the river
    (19, "boat", [(23.95, 11.5), (24.5, 11.5), (24.5, 12.5), (24.95, 12.5)]),
    (20, "boat", [(24.95, 12.5), (26.5, 12.5)]),                             # into Land's End
    (21, "boat", [(26.5, 12.5), (26.5, 13.5), (25.05, 13.5)]),               # Land's End S, then west
    (22, "boat", [(25.05, 13.5), (21.5, 13.5)]),                             # out to the Drowned Temple
    (23, "foot", [(13.5, 2.5), (15.5, 2.5), (15.5, 1.5), (15.95, 1.5)]),     # Pointe Rouge E, up into the dry country
    (24, "foot", [(15.95, 1.5), (18.5, 1.5)]),                               # to the Salt Dome
    (25, "boat", [(8.5, 6.5), (8.5, 4.5)]),                                  # Route 8 N -> the Oldest Shrine
]
# Player icon: the map's long axis and whether the polyline starts at the map's low end (west / north).  The
# region map places the player icon on icon_path[progress along that axis] (see 01_wiring_plan.md).
ROUTE_AXIS = {1: ("y", True), 2: ("x", True), 3: ("x", True), 4: ("y", True), 5: ("x", False), 6: ("x", True),
              7: ("x", True), 8: ("x", True), 9: ("x", True), 10: ("x", True), 11: ("x", True), 12: ("y", False),
              13: ("y", False), 14: ("y", True), 15: ("x", True), 16: ("x", True), 17: ("x", True), 18: ("x", True),
              19: ("x", True), 20: ("x", True), 21: ("x", False), 22: ("x", False), 23: ("x", True), 24: ("x", True),
              25: ("y", False)}
# cell overrides: route -> (add, remove)
CELL_FIX = {
    1: ([(3, 10)], []),          # the hidden channel to the Old Water is Route 1's map
}
# the riverboat, Pointe Rouge -> Crescent City along the Emerald River: white dots drawn over the river AND the route
# bands it crosses (Route 4's landing, Route 6), so the line reads unbroken from one city marker to the other
FERRY = [(12.0, 3.0), (12.15, 3.6), (12.45, 4.6), (13.4, 5.3), (14.6, 6.2), (15.4, 7.1), (15.9, 8.1), (16.3, 8.95)]  # riverboat, drawn dotted


# ------------------------------------------------------------------ helpers
def to_px(p):
    return ((p[0] + 1) * 8.0, (p[1] + 2) * 8.0)


def interp(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            t = 0 if x1 == x0 else (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


def _hash(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def noise(x, y, scale, seed):
    """smooth value noise in [-1, 1]"""
    fx, fy = x / scale, y / scale
    ix, iy = math.floor(fx), math.floor(fy)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = _hash(ix, iy, seed), _hash(ix + 1, iy, seed)
    c, d = _hash(ix, iy + 1, seed), _hash(ix + 1, iy + 1, seed)
    return 2 * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty) - 1


def jitter(x, y, amp=1.2, seed=1):
    return x + amp * noise(x, y, 5.0, seed), y + amp * noise(x, y, 5.0, seed + 7)


def in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy)


def band_dist(px, py, pts):
    """Chebyshev distance to a polyline of horizontal/vertical segments: square band ends and corners"""
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        qx = min(max(px, min(ax, bx)), max(ax, bx))
        qy = min(max(py, min(ay, by)), max(ay, by))
        best = min(best, max(abs(px - qx), abs(py - qy)))
    return best


def poly_dist(px, py, pts):
    return min(seg_dist(px, py, a, b) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ section cells
def route_cells():
    taken = {}
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        for dx in range(w):
            for dy in range(h):
                taken[(cx + dx, cy + dy)] = mapsec
    cells = {}
    for num, mode, pts in ROUTES:
        length, first = Counter(), {}
        k = 0
        for a, b in zip(pts, pts[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(1, int(seg / 0.02))
            for i in range(n):
                t = (i + 0.5) / n
                x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
                c = (int(math.floor(x)), int(math.floor(y)))
                length[c] += seg / n
                first.setdefault(c, k)
                k += 1
        ok = lambda c: c not in taken and 0 <= c[0] < MAP_W and 0 <= c[1] < MAP_H
        mine = sorted((c for c, L in length.items() if L >= 0.3 and ok(c)), key=lambda c: first[c])
        # a route steps diagonally between two of its cells: add the corner cell the line passes nearer, so the
        # cursor walks the route without a gap
        joined = []
        for c in mine:
            if joined:
                p = joined[-1]
                if abs(c[0] - p[0]) == 1 and abs(c[1] - p[1]) == 1:
                    corners = [q for q in ((c[0], p[1]), (p[0], c[1])) if ok(q) and q not in joined]
                    if corners:
                        joined.append(max(corners, key=lambda q: length.get(q, 0)))
            joined.append(c)
        mine = joined
        add, rem = CELL_FIX.get(num, ([], []))
        mine = [c for c in mine if c not in rem] + [c for c in add if c not in mine]
        for c in mine:
            if c in taken:
                raise SystemExit(f"Route {num} cell {c} already belongs to {taken[c]}")
            taken[c] = f"MAPSEC_ROUTE_{num}"
        cells[num] = mine          # in the order the line runs (start of the polyline first)
    return taken, cells


def sections():
    taken, rcells = route_cells()
    out = []
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        out.append({"id": mapsec, "name": name, "cells": [[cx + dx, cy + dy] for dy in range(h) for dx in range(w)],
                    "x": cx, "y": cy, "width": w, "height": h, "kind": kind})
    for num, mode, pts in ROUTES:
        path = [c for c in rcells[num] if c not in CELL_FIX.get(num, ([], []))[0]]   # added cells: not on the path
        axis, start_low = ROUTE_AXIS[num]
        if not start_low:
            path.reverse()
        cs = sorted(rcells[num], key=lambda c: (c[1], c[0]))
        xs, ys = [c[0] for c in path], [c[1] for c in path]      # the rectangle covers the route's own line
        out.append({"id": f"MAPSEC_ROUTE_{num}", "name": f"ROUTE {num}", "cells": [list(c) for c in cs],
                    "x": min(xs), "y": min(ys), "width": max(xs) - min(xs) + 1, "height": max(ys) - min(ys) + 1,
                    "kind": "route_" + mode, "icon_axis": axis, "icon_path": [list(c) for c in path]})
    return taken, out


# ------------------------------------------------------------------ the picture
WATER, DEEPW, LAKE, RIVER, PLAIN, MARSH, FOREST, DRY, SUGAR, PEPPER = range(10)
LANDS = {PLAIN, MARSH, FOREST, DRY, SUGAR, PEPPER}
REGION_CODE = {"marsh": MARSH, "forest": FOREST, "dry": DRY, "sugar": SUGAR, "pepper": PEPPER, "plain": PLAIN}

# Interior texture: every land tile is one of a few 8x8 variants of its terrain, picked by a hash of the tile's
# position (weights below).  Details never cross a tile edge, so each terrain costs only its variant count in tiles
# and the land still reads as scattered hummocks, tufts, pools and trees instead of wallpaper.
def _v(*rows):
    assert len(rows) == 8 and all(len(r) == 8 for r in rows), rows
    return list(rows)


VARIANTS = {
    PLAIN: [
        (10, _v("33333333", "33333333", "33333333", "33333333", "33333333", "33333333", "33333333", "33333333")),
        (3, _v("33333333", "33322333", "33222233", "33212233", "33322433", "33334333", "33333333", "33333333")),
        (3, _v("33333333", "33333333", "33333333", "32233333", "22123333", "32243333", "33433333", "33333333")),
        (2, _v("33333333", "33333223", "33333124", "33333343", "33333333", "33223333", "33244333", "33333333")),
        (2, _v("33333333", "33322233", "32222223", "32222224", "33222243", "33344333", "33333333", "33333333")),
        (2, _v("33333333", "33333333", "33333333", "33333333", "33333333", "33333223", "33332212", "33333244")),
    ],
    MARSH: [
        (9, _v("mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm")),
        (4, _v("mmmmmmmm", "mmmmmmmm", "mMmnmMmm", "mmMnMmmm", "mmmnmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm")),
        (3, _v("mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmmmmm", "mmmmMmnm", "mmmmmMnM", "mmmmmmnm", "mmmmmmmm")),
        (3, _v("mmmmmmmm", "mmmmmmmm", "mmmMMMmm", "mmMbbbMm", "mmMbBbMm", "mmmMMMmm", "mmmmmmmm", "mmmmmmmm")),
        (2, _v("mmmmmmmm", "MmnmMmmm", "mMnMmmmm", "mmnmmmmm", "mmmmmmmm", "mmmmmMnM", "mmmmmmnm", "mmmmmmmm")),
        (2, _v("mmmmmmmm", "mmmmmmmm", "mMMmmmmm", "Mbbbmmmm", "mMMmmmmm", "mmmmmMMm", "mmmmMbbM", "mmmmmMMm")),
    ],
    FOREST: [
        (4, _v("FF44FFFF", "F4444FFF", "F4434fFF", "FF4ffFFF", "FFffFF4F", "FFFFF444", "FFFFF43f", "FFFFFFff")),
        (4, _v("FFFFF44F", "FFFF4444", "FFFF434f", "F44FF4ff", "4444FFfF", "4434fFFF", "F4ffFFFF", "FFfFFFFF")),
        (3, _v("FFFFFFFF", "F44FFFFF", "4444F44F", "434f4444", "F4ff434f", "FFfFF4ff", "FFFFFFfF", "FFFFFFFF")),
        (3, _v("FF44FFFF", "F4444F44", "F434f444", "FF4ff43f", "FFfFFFff", "FFF44FFF", "FF4434FF", "FFF4ffFF")),
    ],
    DRY: [
        (10, _v("tttttttt", "tttttttt", "tttttttt", "tttttttt", "tttttttt", "tttttttt", "tttttttt", "tttttttt")),
        (3, _v("tttttttt", "ttaattut", "taaaautt", "ttuuuttt", "tttttttt", "tttttttt", "tttttttt", "tttttttt")),
        (3, _v("tttttttt", "tttttttt", "tttttttt", "tttttutt", "ttttuvut", "tttttutt", "tttttttt", "tttttttt")),
        (2, _v("tttttttt", "tttttttt", "tuttttat", "uttttaau", "tttttuut", "tttttttt", "ttuttttt", "tttttttt")),
        (2, _v("tttttttt", "tttttttt", "ttttaaat", "tttaaaau", "ttuuuuut", "tttttttt", "tttttttt", "tttttttt")),
    ],
    SUGAR: [
        (1, _v("21212121", "21212121", "21212121", "21212121", "21212121", "21212121", "21212121", "33333333")),
    ],
    PEPPER: [
        (1, _v("aaaaaaaa", "pApApApA", "aaaaaaaa", "ApApApAp", "aaaaaaaa", "pApApApA", "aaaaaaaa", "ApApApAp")),
    ],
}


def variant(t, tx, ty):
    opts = VARIANTS[t]
    total = sum(w for w, _ in opts)
    r = _hash(tx, ty, 97 + t) * total
    for w, rows in opts:
        r -= w
        if r <= 0:
            return rows
    return opts[-1][1]


SHORE1 = {PLAIN: "5", MARSH: "n", FOREST: "f", DRY: "u", SUGAR: "4", PEPPER: "u"}
SHORE2 = {PLAIN: "4", MARSH: "M", FOREST: "f", DRY: "t", SUGAR: "3", PEPPER: "A"}
EDGE = {MARSH: "M", FOREST: "f", DRY: "u", SUGAR: "4", PEPPER: "u"}   # rim against another land type

MARKERS = {
    "town_small": ["oG####Go", "G#ssCCgG", "#s##sCDg", "#s##sCDg", "#CssCCDg", "#CCCCDDg", "G#DDDDgG", "oGggggGo"],
    "town": ["oG####Go", "G#RRxxgG", "#R##Rxzg", "#R##Rxzg", "#xRRxxzg", "#xxxxzzg", "G#zzzzgG", "oGggggGo"],
    "city": ["oG############Go", "G#RRRRxxxxxzzz#G", "#R###RRxxxxxzzzg", "#R###RRxxxxxzzzg", "#xRRRRxxxxxzzzzg",
             "#xxxxxxxxzzzzzzg", "GgzzzzzzzzzzzzgG", "oGggggggggggggGo"],
    "site": ["...GG...", "..G#OG..", ".G#OORG.", "GOORRRrG", "GRRRRrrG", ".GRRrrG.",
             "..GrrG..", "...GG..."],
    "frontier": ["...GG...", "..G#xG..", ".G#xxXG.", "GxxXXXzG", "GXXXXzzG", ".GXXzzG.", "..GzzG..", "...GG..."],
}


def load_vanilla_red_round():
    """the vanilla 8x8 red marker (Petalburg), so the gym towns use the original art"""
    im = Image.open(os.path.join(VANILLA, "map.png"))
    tm = open(os.path.join(VANILLA, "map.bin"), "rb").read()
    t = tm[11 * 64 + 2]
    inv = {v: k for k, v in CI.items()}
    rows = []
    for y in range(8):
        row = ""
        for x in range(8):
            v = im.getpixel(((t % 16) * 8 + x, (t // 16) * 8 + y))
            row += inv.get(v, "?")
        rows.append(row)
    # corners show the background in the vanilla tile: make them transparent
    rows[0] = "o" + rows[0][1:7] + "o"
    rows[7] = "o" + rows[7][1:7] + "o"
    if all(ch != "?" for r in rows for ch in r) and rows[1][1] == "#":
        return rows
    return MARKERS["town"]


DEEP_WAVE = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1, 0, 0]


def deep_level(x):
    """pixel row where the deep Gulf starts: two levels (west, east of Storm's Edge) and a 2-tile slope between"""
    west, east = to_px((0, 14.6))[1], to_px((0, 13.9))[1]
    x0, x1 = to_px((11.0, 0))[0], to_px((13.0, 0))[0]
    if x <= x0:
        return round(west)
    if x >= x1:
        return round(east)
    return round(west + (east - west) * (x - x0) / (x1 - x0))
FLAT = {PLAIN: "3", MARSH: "m", FOREST: "F", DRY: "t"}


def feature_tiles(T, dist):
    """tiles that carry a feature (water, shore, terrain edge, route band, marker): their land is drawn flat so the
    feature does not multiply with the texture variants (tile budget); interior tiles keep their variant"""
    busy = set()
    for y in range(H):
        for x in range(W):
            t = T[y][x]
            if t not in LANDS or dist[y][x] <= 2:
                busy.add((x // 8, y // 8))
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and T[yy][xx] in LANDS and T[yy][xx] != t:
                    busy.add((x // 8, y // 8))
    for num, mode, pts in ROUTES:
        pp = [to_px(p) for p in pts]
        reach = 3.6
        for ty in range(SCREEN_TH):
            for tx in range(SCREEN_TW):
                if (tx, ty) not in busy and band_dist(tx * 8 + 4, ty * 8 + 4, pp) <= reach + 4:
                    if any(band_dist(tx * 8 + x + 0.5, ty * 8 + y + 0.5, pp) <= reach
                           for y in range(8) for x in range(8)):
                        busy.add((tx, ty))
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        for dx in range(w):
            busy.add((cx + OFF_X + dx, cy + OFF_Y))
    return busy


def paint():
    """returns the 240x160 picture as palette indices and the terrain classes"""
    T = [[PLAIN] * W for _ in range(H)]
    coast_px = [(to_px((gx, gy))) for gx, gy in COAST]
    deep_px = [(to_px((gx, gy))) for gx, gy in DEEP]
    lakes = {k: [to_px(p) for p in v] for k, v in LAKES.items()}
    regions = [(REGION_CODE[k], [to_px(p) for p in v]) for k, v in REGIONS]
    for y in range(H):
        for x in range(W):
            cx, cy = x + 0.5, y + 0.5
            jx, jy = jitter(cx, cy, 1.8, 3)
            t = PLAIN
            for code, poly in regions:
                if in_poly(jx, jy, poly):
                    t = code
            if cy + 1.6 * noise(cx, 0, 5.0, 11) + 0.7 * noise(cx, 0, 2.2, 17) > interp(coast_px, cx):
                # the deep-water edge: a level quantised to 3 px plus a 16 px wave, so it repeats tile by tile
                level = deep_level(x)
                t = DEEPW if y >= level + DEEP_WAVE[x % 16] else WATER
            for poly in lakes.values():
                if in_poly(jx, jy, poly):
                    t = LAKE
            T[y][x] = t
    for name, (shape, c, r, kind) in ISLANDS.items():
        (ccx, ccy), (rx, ry) = to_px(c), (r[0] * 8, r[1] * 8)
        for y in range(H):
            for x in range(W):
                jx, jy = jitter(x + 0.5, y + 0.5, 0.6, 5)
                if ((jx - ccx) / rx) ** 2 + ((jy - ccy) / ry) ** 2 <= 1.0:
                    T[y][x] = REGION_CODE[kind]
    for name, (pts, width) in RIVERS.items():
        pp = [to_px(p) for p in pts]
        r = width / 2.0
        for y in range(H):
            for x in range(W):
                if T[y][x] in (WATER, DEEPW):
                    continue
                if poly_dist(x + 0.5, y + 0.5, pp) <= r:
                    T[y][x] = RIVER
    # land shading: distance (chebyshev) to water
    dist = [[99] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if T[y][x] not in LANDS:
                dist[y][x] = 0
    for _ in range(3):
        for y in range(H):
            for x in range(W):
                if dist[y][x] == 99:
                    best = 99
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < H and 0 <= xx < W:
                                best = min(best, dist[yy][xx] + 1)
                    if best < 99:
                        dist[y][x] = best
    busy = feature_tiles(T, dist)
    P = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            t = T[y][x]
            if t == WATER or t == LAKE:
                ch = "w" if y % 2 == 0 else "W"
            elif t == DEEPW:
                ch = "c" if y % 2 == 0 else "d"
            elif t == RIVER:
                ch = "b" if y % 2 == 0 else "B"
            else:
                if (x // 8, y // 8) in busy and t == MARSH:
                    ch = VARIANTS[MARSH][1][1][y % 8][x % 8]   # one fixed tuft: marsh still reads as marsh
                elif (x // 8, y // 8) in busy and t in FLAT:
                    ch = FLAT[t]
                else:
                    ch = variant(t, x // 8, y // 8)[y % 8][x % 8]
                d = dist[y][x]
                if d == 1:
                    ch = SHORE1[t]
                elif d == 2 and t != PLAIN:
                    ch = SHORE2[t] if t in (MARSH,) else ch
                elif d == 2:
                    ch = SHORE2[t]
                if d > 1 and t in EDGE:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < W and 0 <= yy < H and T[yy][xx] in LANDS and T[yy][xx] != t:
                            ch = EDGE[t]
            P[y][x] = CI[ch]
    return P, T


def draw_routes(P, T):
    for num, mode, pts in ROUTES:
        pp = [to_px(p) for p in pts]
        xs = [p[0] for p in pp]
        ys = [p[1] for p in pp]
        for y in range(max(0, int(min(ys)) - 5), min(H, int(max(ys)) + 6)):
            for x in range(max(0, int(min(xs)) - 5), min(W, int(max(xs)) + 6)):
                d = band_dist(x + 0.5, y + 0.5, pp)
                if mode == "foot":
                    if d <= 1.0:
                        P[y][x] = CI["O"]
                    elif d <= 2.6:
                        P[y][x] = CI["o"]
                    elif d <= 3.6:
                        P[y][x] = CI["r"]
                else:
                    if d <= 3.6:
                        P[y][x] = CI["b"] if y % 2 == 0 else CI["B"]
    # the riverboat (Pointe Rouge <-> Crescent City): white dots, drawn after the bands so they sit on top
    for x, y in ferry_pixels():
        P[y][x] = CI["#"]


def ferry_pixels():
    pp = [to_px(p) for p in FERRY]
    out, step, acc = [], 3.0, 0.0
    for a, b in zip(pp, pp[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        t = acc
        while t < seg:
            out.append((int(a[0] + (b[0] - a[0]) * t / seg), int(a[1] + (b[1] - a[1]) * t / seg)))
            t += step
        acc = t - seg
    return out


def draw_markers(P):
    red = load_vanilla_red_round()
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        pat = red if kind == "town" else MARKERS[kind]
        ox, oy = (cx + OFF_X) * 8, (cy + OFF_Y) * 8
        for y, row in enumerate(pat):
            for x, ch in enumerate(row):
                if ch in ".o ":
                    continue
                P[oy + y][ox + x] = CI[ch]


# ------------------------------------------------------------------ tiles
def tiles_of(P):
    grid = {}
    for ty in range(SCREEN_TH):
        for tx in range(SCREEN_TW):
            grid[(tx, ty)] = tuple(P[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
    return grid


def reduce_tiles(grid, protected):
    """merge similar tiles until the unique count fits TILE_BUDGET.  protected: tile coords never changed (markers).
    Greedy: repeatedly fold the tile whose replacement costs least (colour distance x number of uses) into its
    nearest neighbour."""
    import numpy as np
    uses = defaultdict(list)
    for pos, t in grid.items():
        uses[t].append(pos)
    uniq = list(uses)
    n = len(uniq)
    if n <= TILE_BUDGET:
        return 0
    lut = np.zeros((256, 3), dtype=np.int32)
    for i, rgb in RGB.items():
        lut[i] = rgb
    arr = lut[np.array(uniq, dtype=np.int32)]                     # n x 64 x 3
    flat = arr.reshape(n, -1)
    dist = np.abs(flat[:, None, :] - flat[None, :, :]).sum(axis=2).astype(np.float64)
    np.fill_diagonal(dist, np.inf)
    locked = np.array([t in {grid[p] for p in protected} for t in uniq])
    alive = np.ones(n, dtype=bool)
    count = np.array([len(uses[t]) for t in uniq], dtype=np.float64)
    merges = 0
    while alive.sum() > TILE_BUDGET:
        cost = dist * count[:, None]
        cost[~alive, :] = np.inf
        cost[:, ~alive] = np.inf
        cost[locked, :] = np.inf
        a, b = np.unravel_index(np.argmin(cost), cost.shape)
        ta, tb = uniq[a], uniq[b]
        for pos in uses[ta]:
            grid[pos] = tb
        uses[tb].extend(uses.pop(ta))
        count[b] += count[a]
        alive[a] = False
        merges += 1
    return merges


def build_outputs(P, taken, secs):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    grid = tiles_of(P)
    raw_unique = len(set(grid.values()))
    protected = set()
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        for dx in range(w):
            for dy in range(h):
                protected.add((cx + OFF_X + dx, cy + OFF_Y + dy))
    for x, y in ferry_pixels():                       # the tile merge must not eat riverboat dots
        protected.add((x // 8, y // 8))
    merges = reduce_tiles(grid, protected)
    # the final picture (after merging)
    Q = [[0] * W for _ in range(H)]
    for (tx, ty), t in grid.items():
        for i, v in enumerate(t):
            Q[ty * 8 + i // 8][tx * 8 + i % 8] = v
    # tile order: the Gulf water tile first (tile 0 fills the unused part of the 64x64 map)
    order = []
    water = grid[(SCREEN_TW // 2, SCREEN_TH - 1)]
    order.append(water)
    for ty in range(SCREEN_TH):
        for tx in range(SCREEN_TW):
            if grid[(tx, ty)] not in order:
                order.append(grid[(tx, ty)])
    index = {t: i for i, t in enumerate(order)}
    ntiles = len(order)
    assert ntiles <= TILE_BUDGET, ntiles

    def screen_tile(tx, ty):
        """64x64 (or 32x32) tilemap cell -> picture tile; past the picture the edge row/column repeats"""
        if tx >= SCREEN_TW:
            tx = SCREEN_TW - 1 if tx < 48 else 0
        if ty >= SCREEN_TH:
            ty = SCREEN_TH - 1 if ty < 42 else 0
        return index[grid[(tx, ty)]]

    # tileset png (128 px wide like vanilla), 8bpp indexed
    rows = (ntiles + 15) // 16
    sheet = Image.new("P", (128, rows * 8), 0)
    pal = [0] * 768
    for i, rgb in RGB.items():
        pal[i * 3:i * 3 + 3] = list(rgb)
    sheet.putpalette(pal)
    px = sheet.load()
    for i, t in enumerate(order):
        for k, v in enumerate(t):
            px[(i % 16) * 8 + k % 8, (i // 16) * 8 + k // 8] = v
    sheet.save(os.path.join(OUT, "map.png"))
    sheet.save(os.path.join(OUT, "dex_region_map.png"))
    # affine tilemap 64x64 bytes
    with open(os.path.join(OUT, "map.bin"), "wb") as f:
        f.write(bytes(screen_tile(tx, ty) for ty in range(64) for tx in range(64)))
    # Pokedex area map: text BG 32x32, u16 entries (tile index, no flip, palette 0)
    with open(os.path.join(OUT, "dex_region_map.bin"), "wb") as f:
        for ty in range(32):
            for tx in range(32):
                f.write(struct.pack("<H", screen_tile(tx, ty)))
    # palettes: 48 colours from index 112 (the engine loads 3 BG palettes at slot 7)
    cols = [RGB.get(PAL_BASE + i, (0, 0, 0)) for i in range(48)]
    for name in ("map.pal", "dex_region_map.pal"):
        with open(os.path.join(OUT, name), "w", newline="\r\n") as f:
            f.write("JASC-PAL\n0100\n48\n")
            for r, g, b in cols:
                f.write(f"{r} {g} {b}\n")
    # 1x source picture
    src = Image.new("P", (W, H))
    src.putpalette(pal)
    src.putdata([Q[y][x] for y in range(H) for x in range(W)])
    src.save(os.path.join(OUT, "region_map_art_1x.png"))
    # layout header
    with open(os.path.join(OUT, "region_map_layout.h"), "w", newline="\n") as f:
        f.write("// Orleans region map: generated by tools/regionmap/orleans_regionmap.py (do not edit by hand)\n")
        f.write("static const mapsec_u8_t sRegionMap_MapSectionLayout[MAP_HEIGHT][MAP_WIDTH] = {\n")
        for cy in range(MAP_H):
            f.write("    {" + ", ".join(taken.get((cx, cy), "MAPSEC_NONE") for cx in range(MAP_W)) + "},\n")
        f.write("};\n")
    # player-icon paths for the routes (see 01_wiring_plan.md, "Player icon")
    with open(os.path.join(OUT, "region_map_orleans_paths.h"), "w", newline="\n") as f:
        f.write("// Orleans region map: generated by tools/regionmap/orleans_regionmap.py (do not edit by hand)\n")
        f.write("// Per route: the cells of its line from the map's west (alongY FALSE) or north (alongY TRUE) end.\n")
        f.write("// The player icon sits on cells[pos * count / mapSize] instead of the rectangle's scaled cell.\n")
        f.write("struct OrleansRoutePath { mapsec_u8_t mapsec; bool8 alongY; u8 count; u8 cells[8][2]; };\n\n")
        f.write("static const struct OrleansRoutePath sOrleansRoutePaths[] =\n{\n")
        for sec in secs:
            if "icon_path" not in sec:
                continue
            path = sec["icon_path"]
            assert len(path) <= 8, sec["id"]
            cells = ", ".join("{%d, %d}" % (c[0], c[1]) for c in path)
            f.write("    {%s, %s, %d, {%s}},\n" % (sec["id"], "TRUE" if sec["icon_axis"] == "y" else "FALSE",
                                                  len(path), cells))
        f.write("};\n")
    with open(os.path.join(OUT, "sections.json"), "w", newline="\n") as f:
        json.dump({"sections": secs, "tiles": ntiles, "raw_unique_tiles": raw_unique, "tile_merges": merges,
                   "colours": len(PALETTE)}, f, indent=1)
    return Q, ntiles, raw_unique, merges


# ------------------------------------------------------------------ review images
def to_rgb(Q, scale):
    im = Image.new("RGB", (W, H))
    im.putdata([RGB[Q[y][x]] for y in range(H) for x in range(W)])
    return im.resize((W * scale, H * scale), Image.NEAREST)


def font(size, bold=False):
    for name in (("arialbd.ttf" if bold else "arial.ttf"), "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def load_4bpp_sheet(name):
    im = Image.open(os.path.join(VANILLA, name))
    return im, im.getpalette()


def mock(Q, cursor_sec="MAPSEC_CRESCENT_CITY"):
    """the Fly screen: BG2 map, BG1 frame, fly-destination sprites, cursor, name and prompt windows"""
    scr = Image.new("RGB", (W, H))
    scr.putdata([RGB[Q[y][x]] for y in range(H) for x in range(W)])
    # frame (BG1, 4bpp, palette from frame.png)
    fim, fpal = load_4bpp_sheet("frame.png")
    fbin = open(os.path.join(VANILLA, "frame.bin"), "rb").read()
    ftw = fim.width // 8
    fpx = fim.load()
    for i in range(len(fbin) // 2):
        e = struct.unpack_from("<H", fbin, i * 2)[0]
        tx, ty = i % 32, i // 32
        if tx >= SCREEN_TW or ty >= SCREEN_TH:
            continue
        t, hf, vf = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1
        if t == 0:
            continue
        for y in range(8):
            for x in range(8):
                sx, sy = (7 - x if hf else x), (7 - y if vf else y)
                v = fpx[(t % ftw) * 8 + sx, (t // ftw) * 8 + sy]
                if v:
                    scr.putpixel((tx * 8 + x, ty * 8 + y), tuple(fpal[v * 3:v * 3 + 3]))
    # fly destination icons (sprites): towns pink (can fly), Frontier red outline
    iim = Image.open(os.path.join(VANILLA, "fly_target_icons.png"))
    ipal = iim.getpalette()
    ipx = iim.load()

    def blit_tile(n, X, Y):
        sx, sy = (n % 2) * 8, (n // 2) * 8
        for y in range(8):
            for x in range(8):
                v = ipx[sx + x, sy + y]
                if v and 0 <= X + x < W and 0 <= Y + y < H:
                    scr.putpixel((X + x, Y + y), tuple(ipal[v * 3:v * 3 + 3]))

    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        X, Y = (cx + OFF_X) * 8, (cy + OFF_Y) * 8
        if kind in ("town", "town_small", "city"):
            if w == 2:
                blit_tile(1, X, Y)
                blit_tile(2, X + 8, Y)
            else:
                blit_tile(0, X, Y)
        elif kind == "frontier":
            for k, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
                blit_tile(10 + k, X - 4 + dx, Y - 4 + dy)
    # cursor (the small 16x16 cursor the Fly map uses, frame 0, colour 0 transparent) on the section's first cell
    cim = Image.open(os.path.join(VANILLA, "cursor_small.png"))
    cpal, cpx = cim.getpalette(), cim.load()
    cname = ""
    for mapsec, name, (cx, cy), w, h, kind in TOWNS:
        if mapsec == cursor_sec:
            X, Y = (cx + OFF_X) * 8 - 4, (cy + OFF_Y) * 8 - 4
            for y in range(16):
                for x in range(16):
                    v = cpx[x, y]
                    if v and 0 <= X + x < W and 0 <= Y + y < H:
                        scr.putpixel((X + x, Y + y), tuple(cpal[v * 3:v * 3 + 3]))
            cname = name
    # windows (approximate GBA text boxes)
    d = ImageDraw.Draw(scr)
    d.rectangle((0, 136, 120, 159), fill=(255, 255, 255))
    d.rectangle((128, 128, 239, 151), fill=(74, 82, 106))
    d.rectangle((131, 131, 236, 148), fill=(255, 255, 255))
    big = scr.resize((W * 3, H * 3), Image.NEAREST)
    d = ImageDraw.Draw(big)
    f = font(28)
    d.text((18, 418), "FLY to where?", font=f, fill=(74, 74, 74))
    d.text((405, 405), cname, font=f, fill=(74, 74, 74))
    return big


def cells_sheet(Q, taken, secs):
    S = 4
    im = to_rgb(Q, S)
    d = ImageDraw.Draw(im, "RGBA")
    # cursor grid
    for cx in range(MAP_W + 1):
        X = (cx + OFF_X) * 8 * S
        d.line((X, OFF_Y * 8 * S, X, (OFF_Y + MAP_H) * 8 * S), fill=(0, 0, 0, 90))
    for cy in range(MAP_H + 1):
        Y = (cy + OFF_Y) * 8 * S
        d.line((OFF_X * 8 * S, Y, (OFF_X + MAP_W) * 8 * S, Y), fill=(0, 0, 0, 90))
    fs = font(10, True)
    for cx in range(MAP_W):
        d.text(((cx + OFF_X) * 8 * S + 10, OFF_Y * 8 * S - 14), str(cx), font=fs, fill=(0, 0, 0))
    for cy in range(MAP_H):
        d.text((OFF_X * 8 * S - 18, (cy + OFF_Y) * 8 * S + 10), str(cy), font=fs, fill=(0, 0, 0))
    short = {s["id"]: "R" + s["id"].split("_")[-1] for s in secs if s["id"].startswith("MAPSEC_ROUTE_")}
    short.update({"MAPSEC_ISLE_MARAIS": "IM", "MAPSEC_OLD_WATER": "OW", "MAPSEC_GRAND_OAK": "GO",
                  "MAPSEC_STORMS_EDGE": "SE", "MAPSEC_CRESCENT_CITY": "CC", "MAPSEC_POINTE_ROUGE": "PR",
                  "MAPSEC_CAMP_COCODRIE": "CA", "MAPSEC_LUTINS_HOLLOW": "LH", "MAPSEC_REDFIELD": "RF",
                  "MAPSEC_LANDS_END": "LE", "MAPSEC_OLDEST_SHRINE": "OS", "MAPSEC_SALT_DOME": "SD",
                  "MAPSEC_DROWNED_TEMPLE": "DT", "MAPSEC_BATTLE_FRONTIER": "BF"})
    for (cx, cy), sec in taken.items():
        X, Y = (cx + OFF_X) * 8 * S, (cy + OFF_Y) * 8 * S
        boat = any(s["id"] == sec and s["kind"] == "route_boat" for s in secs)
        town = not sec.startswith("MAPSEC_ROUTE_")
        col = (200, 40, 40, 255) if town else ((20, 60, 200, 255) if boat else (120, 70, 0, 255))
        d.rectangle((X + 2, Y + 2, X + 8 * S - 3, Y + 8 * S - 3), outline=col, width=2)
        d.rectangle((X + 3, Y + 10, X + 8 * S - 4, Y + 22), fill=(255, 255, 255, 200))
        d.text((X + 4, Y + 10), short[sec], font=fs, fill=col[:3])
    # legend
    lw = 560
    sheet = Image.new("RGB", (im.width + lw, max(im.height, 40 + 15 * len(secs) + 40)), (250, 248, 240))
    sheet.paste(im, (0, 0))
    d = ImageDraw.Draw(sheet)
    fl, fb = font(12), font(13, True)
    x0 = im.width + 12
    d.text((x0, 8), "Section  (code)  cells  /  entry rect x,y,w,h", font=fb, fill=(0, 0, 0))
    y = 30
    for s in secs:
        cells = " ".join(f"{c[0]},{c[1]}" for c in s["cells"])
        line = f"{s['name']} ({short[s['id']]})  {cells}  /  {s['x']},{s['y']},{s['width']},{s['height']}"
        d.text((x0, y), line, font=fl, fill=(0, 0, 0))
        y += 15
    d.text((x0, y + 10), "red = town/site, brown = route on foot, blue = Surf/boat route", font=fl, fill=(60, 60, 60))
    d.text((x0, y + 26), "grid = cursor cells (MAP_WIDTH 28 x MAP_HEIGHT 15); numbers = cell x / y", font=fl,
           fill=(60, 60, 60))
    return sheet


def main():
    taken, secs = sections()
    P, T = paint()
    draw_routes(P, T)
    draw_markers(P)
    Q, ntiles, raw, merges = build_outputs(P, taken, secs)
    to_rgb(Q, 3).save(os.path.join(DOCS, "region_map_full_3x.png"))
    mock(Q).save(os.path.join(DOCS, "region_map_mock.png"))
    cells_sheet(Q, taken, secs).save(os.path.join(DOCS, "02_cells_sheet.png"))
    # what changed by the tile merge (review aid)
    pre = Image.new("RGB", (W, H))
    pre.putdata([RGB[P[y][x]] for y in range(H) for x in range(W)])
    pre.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(DOCS, "03_before_tile_merge_3x.png"))
    print(f"tiles: {ntiles} (raw unique {raw}, merged {merges}); colours {len(PALETTE)}; sections {len(secs)}")
    for s in secs:
        print(f"  {s['id']:28s} {s['name']:16s} rect {s['x']},{s['y']},{s['width']},{s['height']}  cells {s['cells']}")


if __name__ == "__main__":
    main()

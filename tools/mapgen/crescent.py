"""Crescent City, the hub city: a hand-designed generator (not a first pass).

Fantasy New Orleans on the Emerald River, laid out after ../orleans_maps/04_crescent_city.png at 1.5x, then widened
14 columns on the west so City Park has room (104x66; the code works in design coordinates, x from -14):

    Old Cemetery     NW: an iron-fenced city of the dead: oven vaults and the oldest crypt at the head of the centre
                     aisle, whitewashed family tombs, overgrown cemetery grass (tall grass), and the Fifolet gym (a
                     marble temple-mausoleum with blue wisp lanterns) at the foot, gates east and south
    City Park        W, the centrepiece: a walk loops round a big pond with a white bandstand on an island (plank
                     bridge), cypresses in the water, benches facing the water, lamps, magnolias at the corners,
                     formal flower beds; north-west a wild garden of soft long grass (encounters), a cypress grove,
                     magnolias and the Day Care
    French Quarter   N: the Cathedral, the Cafe and the Apartment on the canal; two-storey townhouses with iron
                     balconies and hanging ferns along Royal Lane; a fenced square with a fountain and flower beds
    Drowned Ward     NE: two flooded basins of black water with roofless brick shells and cypresses standing in
                     them, a reed marsh, and the Blacksnake cellar door in the ruin at the south basin's foot
    Downtown Market  centre: the Department Store and its plaza with market stalls, the Game Corner, the Name Rater
                     and the Tutor in two narrow houses
    Waterfront       E: magnolia lawn, Conservation Center, second Pokemon Center, ice cream, a riverside promenade
                     with benches and lamps, the Riverboat Terminal and Pelipper Post on the quay, Rotom's pier with
                     its old generator, the riverboat (a sternwheeler) moored by its gangway, a levee lawn
    Battle Frontier  S: seven facilities behind an iron fence, stepped back in a shallow bay towards the Arena, a
                     paved plaza of city flagstones with a fountain lawn and four flower parterres, a gate guard
                     (post-game; doors shut)
    Far bank         E of the river: a cypress swamp, a grove on the point by the lake (Surf only)

Exits (map coordinates): Route 6 basin mouth (boat, west edge, canal rows 0-2), the Riverboat to Pointe Rouge (north
edge, river x 74-83), Route 10 lakefront (boat, north edge, lake x 92-103), Route 3 causeway (west edge, y 43-44),
Route 14 levee road (south edge, x 52-53).

usage (from the decomp root): python -W ignore tools/mapgen/crescent.py [--no-check]
writes maps/crescent_city.grid.txt + crescent_city.json, builds (two passes when new overlay/blend tiles are
needed: build, compose, build), runs check.py and draws the review sheet maps/00_crescent_review.png. Then run
build_interior.py (or pass --relink) so the rooms' exits point at the right door warps. Note: build.py rewrites
data/layouts/layouts.json; never run it while another tool writes that file.
"""
import crescent_flood
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from town_plans import PLANS, door_label  # noqa: E402

ROOT = os.getcwd()
MAPS = os.path.join(HERE, "maps")
W, H = 104, 66
OX = 14  # the map was widened 14 columns to the west for City Park; layout code works in design
         # coordinates (x from -14), stored at x + OX
CFG = "orleans_crescent"
KEY = "crescent_city"


def cfg():
    return json.load(open(os.path.join(HERE, "tilesets", CFG + ".json"), encoding="utf-8"))


def paginate(text, width=36):
    """Message text for a Gen-3 text box (two lines of about 36 characters): long lines wrap at word breaks, lines come
    in pairs joined by a line feed, pairs by a page break (a literal backslash-p, which build.py writes through)."""
    import textwrap
    lines = []
    for ln in text.split(chr(10)):
        lines += textwrap.wrap(ln, width) or [""]
    out = ""
    for i, ln in enumerate(lines):
        out += ln if i == 0 else (chr(92) + ("n" if i % 2 else "p")) + ln
    return out


class City:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]
        self.buildings = []
        self.objects = []
        self.signs = []
        self.pf = cfg()["prefabs"]
        self.taken = set()  # cells covered by prefabs
        self.meadow = set()  # tall-grass cells (drawn last as pgrass overlays, soft-edged)

    # ---- terrain
    def rect(self, ch, x, y, w, h):
        for j in range(max(0, y), min(H, y + h)):
            for i in range(max(-OX, x), min(W - OX, x + w)):
                self.g[j][i + OX] = ch

    def at(self, x, y):
        return self.g[y][x + OX] if -OX <= x < W - OX and 0 <= y < H else None

    # ---- prefabs
    def size(self, prefab, rows=None):
        rows = rows or self.pf[prefab]["rows"]
        return len(rows[0]), len(rows)

    def put(self, prefab, x, y, label=None, **kw):
        w, h = self.size(prefab, kw.get("rows"))
        cells = {(x + i, y + j) for i in range(w) for j in range(h)
                 if (kw.get("rows") or self.pf[prefab]["rows"])[j][i] is not None}
        over = kw.pop("over", False)  # drawn over another prefab on purpose (balconies on a wall)
        clash = set() if over else cells & self.taken
        if clash:
            print(f"  warning: {prefab} at ({x},{y}) overlaps {sorted(clash)[:4]}")
        self.taken |= cells
        b = {"prefab": prefab, "x": x + OX, "y": y, "label": label or prefab}
        b.update(kw)
        self.buildings.append(b)
        return b

    def room(self, key, x, y, prefab=None):
        """A building from the town plan (town_plans.PLANS) that leads to an interior room."""
        import interiors as mock
        plan = {k: p for k, _, p, _ in PLANS[KEY] if k}
        return self.put(prefab or plan[key], x, y, door_label(key, mock.INTERIORS[key]["title"]))

    def closed(self, label, x, y, prefab):
        return self.put(prefab, x, y, label, closed=True)

    def grove(self, x, y, trees, pad=1):
        """A marsh grove holding trees (prefab, dx, dy) with a full marsh tile on every side of each tree."""
        xs = [x + dx for t, dx, dy in trees] + [x + dx + self.size(t)[0] for t, dx, dy in trees]
        ys = [y + dy for t, dx, dy in trees] + [y + dy + self.size(t)[1] for t, dx, dy in trees]
        self.rect('"', min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad + 1, max(ys) - min(ys) + 2 * pad + 1)
        for t, dx, dy in trees:
            self.put(t, x + dx, y + dy, "Tree")

    def grove_fits(self, x, y, prefab="cypress_marsh", pad=1):
        """Whether a one-tree grove at (x, y) lands on open grass with a grass cell between it and anything else."""
        w, h = self.size(prefab)
        for j in range(y - pad - 1, y + h + pad + 2):
            for i in range(x - pad - 1, x + w + pad + 2):
                if self.at(i, j) != "." or (i, j) in self.taken:
                    return False
        return True

    def walkway(self, x, y, n, vertical=True, label="Boardwalk", wide=3):
        """A boardwalk n long and `wide` (2 or 3) across north-south, or 2 deep east-west; walkable over water."""
        cols = (("vl", "vm", "vr") if wide == 3 else ("vl", "vr")) if vertical else ("ht", "hb")
        for k in range(n):
            for i, piece in enumerate(cols):
                self.put("walk_" + piece, x + (i if vertical else k), y + (k if vertical else i), label)

    def grass(self, rows):
        """Mark wild-encounter long grass: rows = {y: (x0, x1)} inclusive."""
        for y, (x0, x1) in rows.items():
            self.meadow |= {(x, y) for x in range(x0, x1 + 1)}

    def lay_grass(self):
        """Long grass on every meadow cell: dense inside, sparse on the patch's edge so it fades out."""
        cells = self.meadow - self.taken
        for x, y in sorted(cells, key=lambda c: (c[1], c[0])):
            edge = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            self.put("pgrass_rim" if edge else "pgrass", x, y, "Tall grass")

    def free(self, prefab, x, y):
        """Whether prefab fits at (x, y) on plain ground that nothing else covers."""
        w, h = self.size(prefab)
        return all(self.at(x + i, y + j) == "." and (x + i, y + j) not in self.taken
                   for i in range(w) for j in range(h))

    def dress(self, prefab, x, y, label):
        """put() where it fits, silently skipped otherwise (street furniture on lawns)."""
        if self.free(prefab, x, y):
            self.put(prefab, x, y, label)

    def hedge(self, x, y, n):
        """A clipped box hedge n long, rounded at both ends."""
        for i in range(n):
            self.put("hedge_" + ("l" if i == 0 else "r" if i == n - 1 else "m"), x + i, y, "Hedge")

    def fence(self, cells, gaps=()):
        """Wrought-iron fence along a set of cells; each piece joins its fenced neighbours."""
        cells = set(cells) - set(gaps)
        for (x, y) in sorted(cells, key=lambda c: (c[1], c[0])):
            flags = "".join(k for k, (dx, dy) in zip("NSEW", ((0, -1), (0, 1), (1, 0), (-1, 0))) if (x + dx, y + dy) in cells)
            self.put("fence_" + (flags or "N"), x, y, "Fence")

    def npc(self, ident, gfx, x, y, text, move="MOVEMENT_TYPE_FACE_DOWN", flag=None):
        """A placeholder person (flag: hidden once that flag is set)."""
        o = {"id": f"LOCALID_CRESCENT_CITY_{ident}", "gfx": gfx, "x": x + OX, "y": y, "move": move, "text": paginate(text)}
        if flag:
            o["flag"] = flag
        self.objects.append(o)

    def sign(self, ident, x, y, text, art=True):
        if art:
            self.put("sign", x, y, "Sign")
        self.signs.append({"id": ident, "x": x + OX, "y": y, "text": paginate(text)})


def ring(x, y, w, h):
    return [(i, y) for i in range(x, x + w)] + [(i, y + h - 1) for i in range(x, x + w)] + \
           [(x, j) for j in range(y + 1, y + h - 1)] + [(x + w - 1, j) for j in range(y + 1, y + h - 1)]


def lerp(pts, y):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
    return pts[-1][0]


# ---------------------------------------------------------------- water and streets
CANAL_WIDE = 6  # the canal is 4 rows wide for this many cells at the west edge (the Route 6 seam), 3 elsewhere
WEST_BANK = [(60, 0), (60, 66)]  # one straight levee down the city side: its cells repeat (tile budget)
EAST_BANK = [(70, 0), (70, 21), (78, 39), (90, 44)]
LAKE = [(78, 0), (82, 10), (90, 13)]


def water(c):
    c.rect("~", -OX, 0, 60 + OX, 3)  # the basin canal (Route 6 boat exit at its west end)
    c.rect("~", -OX, 3, CANAL_WIDE, 1)  # ... a fourth row wide for its first cells, so Route 6's mouth has 3 open cells across the seam
    for y in range(H):
        xw = round(lerp(WEST_BANK, y))
        xe = round(lerp(EAST_BANK, y)) if y <= 44 else W - OX
        c.rect("~", xw, y, xe - xw, 1)
        if y <= 13:
            xl = round(lerp(LAKE, y))
            c.rect("~", xl, y, W - OX - xl, 1)


def streets(c):
    c.rect("=", 16, 4, 4, 41)    # Rampart Avenue (A): canal to street 3
    # Canal Avenue (B): canal to the south edge, 4 wide, then it narrows by a tile a side (two rows each) to the 2-wide
    # levee road into Route 14, instead of a 2-wide stub hanging off the avenue
    c.rect("=", 37, 4, 4, 56)
    c.rect("=", 38, 60, 3, 2)
    c.rect("=", 38, 62, 2, 4)
    c.rect("=", 20, 11, 39, 3)   # street 1: Cathedral row to the river
    c.rect("=", 20, 20, 17, 2)   # Royal Lane (French Quarter)
    c.rect("=", 20, 27, 39, 3)   # street 2
    c.rect("=", 30, 35, 7, 2)    # Market lane
    c.rect("=", -OX + 2, 42, 71, 3)  # street 3: the causeway road from the west, 3 wide to within 2 cells of the edge ...
    c.rect("=", -OX, 43, 2, 2)   # ... then the Route 3 causeway's 2 (rows 43-44, the exit cells) in the last two
    c.rect("=", 57, 11, 2, 55)   # riverside promenade, along the levee to the south edge
    c.rect("=", 41, 51, 16, 2)   # the quay in front of the terminal and the post


# ---------------------------------------------------------------- districts
def cemetery(c):
    """Old Cemetery: iron fence x 1-15, y 4-23. The oldest crypt heads the centre aisle between oven vaults and
    family tombs; overgrown cemetery grass either side; the Fifolet gym at the foot, its forecourt opening east
    onto Rampart Avenue."""
    c.rect("=", 2, 20, 14, 2)      # forecourt in front of the gym, out through the east gate
    c.rect("=", 2, 12, 13, 2)      # cross aisle above the gym
    c.rect("=", 2, 14, 2, 6)       # west aisle (the night path)
    c.rect("=", 13, 14, 2, 6)      # east aisle
    c.rect("=", 7, 8, 3, 4)        # centre aisle up to the crypt
    c.grass({10: (2, 6), 11: (2, 6)})      # cemetery grass, overgrown plots by the centre aisle
    c.grass({10: (10, 14), 11: (10, 14)})
    # the fence's south run (y 22) sits flush on the park's north walk (y 23-24); the gym and its forecourt moved up a row
    c.fence(ring(1, 4, 15, 19), gaps=[(15, 20), (15, 21)])
    c.room("crescent_city_gym", 5, 14)
    c.put("crypt", 7, 5, "Oldest crypt")  # Galarian Moltres (night); 3x3, centred on the aisle (x 7-9)
    c.put("tomb", 2, 5, "Tomb")
    c.put("tomb", 13, 5, "Tomb")
    c.put("tomb", 5, 5, "Tomb")
    c.put("tomb", 10, 5, "Tomb")
    for x in (2, 5, 10, 13):
        c.put("tomb", x, 8, "Tomb")
    for x in (3, 11):
        c.put("tomb", x, 10, "Tomb")
    c.sign("CemeterySign", 12, 19, "OLD CEMETERY\nFifolet Gym ahead.\nFollow the steady blue lights;\nthe flickering ones lead astray.")


def blob(c, ch, rows):
    """Paint an organic patch: rows = {y: (x0, x1)} inclusive."""
    for y, (x0, x1) in rows.items():
        c.rect(ch, x0, y, x1 - x0 + 1, 1)


def park(c):
    """City Park, the city's centrepiece (x -14..15, y 3..41 in design coordinates), symmetric about x 3.
    A walk runs round three sides and opens onto Rampart Avenue at both ends; inside it a lawn with benches
    facing a big pond, magnolias and two soft patches of the park's long grass (encounters). In the middle of the
    pond a white bandstand stands centred on its island, reached by a white railed footbridge (a surfer passes
    under it), between two cypresses: the western one is the Old Cypress (the Scizorite tree). Painters' easels on
    the south shore (Smeargle), formal flower beds at the south entrance, lamps and magnolias outside the walk.
    North-west, round the Day Care, a wild garden: soft meadows of long grass, a cypress grove and magnolias."""
    # the walk: north and south runs out to Rampart Avenue, the west side up to the Day Care door
    c.rect("=", -11, 23, 27, 2)
    c.rect("=", -11, 38, 27, 2)
    c.rect("=", -11, 23, 2, 17)
    c.rect("=", 2, 40, 4, 2)       # south entrance from street 3
    # the pond and the island in its middle, the bandstand centred on the island: everything here is symmetric about
    # the line x = 4 (cells 0-7 are the island, 2-5 the bandstand, -5..12 the pond) and y = 32 (pond rows 27-36,
    # island rows 29-34, bandstand rows 30-33)
    # (the bank is drawn through the middle of the edge tiles, half a tile up and to the left of the cells, so the
    # visible pond, island and bandstand all centre on x 4 and y 31.75: pond cells -5..13, island cells 1..7 x 30..34
    # (a margin of 1.5 tiles either side and 1 above and below the bandstand's roof and base), bandstand cells 2-5)
    blob(c, "~", {27: (-3, 11), 28: (-5, 13), 29: (-5, 13), 30: (-5, 13), 31: (-5, 13), 32: (-5, 13), 33: (-5, 13),
                  34: (-5, 13), 35: (-5, 13), 36: (-3, 11)})
    c.rect(".", 1, 30, 7, 5)
    c.put("gazebo", 2, 30, "Bandstand", passable=[[1, 3], [2, 3]])  # its front steps are walkable (the footbridge lands there)
    # the footbridge: a bridge a surfer can pass under (build.py's "Bridge": deck art on the top layer, elevation
    # 15 over the water, 4 on the banks, an elevation-0 step down to the walk)
    c.put("fbridge_l", 3, 34, "Bridge", rows=[["ccsr:fbridge_l_00", "ccsr:fbridge_r_00"]] * 4,
          passable=[[i, j] for j in range(4) for i in range(2)])  # island shore, water, water, south shore
    c.put("cypress_water", -4, 30, "Tree")  # the Old Cypress: Scizorite
    c.put("cypress_water", 9, 30, "Tree")
    c.sign("OldCypressSign", -9, 30, "THE OLD CYPRESS\nThe oldest tree in the park.")
    # the lawn inside the walk: benches facing the water, magnolias, long grass, easels by the south shore
    for x in (-5, -1, 8, 12):
        c.put("bench", x, 25, "Bench")
    c.put("magnolia", -8, 26, "Magnolia")
    c.put("magnolia", 14, 26, "Magnolia")
    c.grass({31: (-9, -8), 32: (-9, -7), 33: (-9, -7), 34: (-9, -7), 35: (-9, -8)})
    c.grass({31: (15, 15), 32: (15, 15), 33: (15, 15), 34: (15, 15), 35: (15, 15)})
    c.put("easel", -2, 37, "Easel")
    c.put("easel", 9, 37, "Easel")
    # outside the walk: lamps and magnolias on the west side, flower beds and lamps at the south entrance
    c.put("magnolia", -14, 26, "Magnolia")
    c.put("magnolia", -14, 35, "Magnolia")
    c.put("lamp", -12, 29, "Lamp")
    c.put("lamp", -12, 33, "Lamp")
    for x0 in (-3, 7):
        for x in range(x0, x0 + 4):
            for y in (40, 41):
                c.put("flowerbed", x, y, "Flowers")
    for x in (1, 6):
        c.put("lamp", x, 40, "Lamp")
    # the wild garden north-west, round the Day Care
    c.room("crescent_city_day_care", -11, 18)   # walls on the walk's west line (x -11), door on the walk
    c.grass({7: (-12, -8), 8: (-13, -7), 9: (-13, -6), 10: (-13, -6), 11: (-12, -6), 12: (-11, -7)})
    c.grass({14: (-6, -2), 15: (-7, -1), 16: (-7, -1), 17: (-6, -2)})
    c.put("magnolia", -4, 7, "Magnolia")
    c.put("magnolia", -1, 9, "Magnolia")
    for x, y in ((-14, 13), (-10, 14), (-5, 19), (-3, 19)):
        c.put("magnolia", x, y, "Magnolia")
    c.put("bench", -6, 22, "Bench")
    c.put("lamp", -12, 23, "Lamp")
    c.sign("CitySign", -13, 41, "CRESCENT CITY\nThe Crescent on the Emerald River.")
    c.sign("ParkSign", -8, 41, "CITY PARK\nPlease keep off the flower beds.")


def french_quarter(c):
    """French Quarter: the Cathedral, then Creole townhouses in four stucco colours with iron galleries and their
    trade signs (Cafe, Apartment, Salon, Laundry, Trade House), the Pokemon Center, a fenced square."""
    c.room("crescent_city_cathedral", 21, 4)
    c.room("crescent_city_cafe", 27, 5)
    c.room("crescent_city_apartment", 33, 5)
    c.room("crescent_city_salon", 20, 14)
    c.room("crescent_city_laundry", 26, 14)
    c.room("crescent_city_pokecenter_quarter", 33, 16)
    c.room("crescent_city_trades", 20, 22)
    c.put("lamp", 20, 8, "Lamp")
    c.put("lamp", 25, 18, "Lamp")
    c.put("lamp", 32, 18, "Lamp")
    for x in range(33, 37):
        c.put("flowerbed", x, 15, "Flowers")
    c.put("magnolia", 26, 22, "Magnolia")
    # the square: a fenced garden of flower beds round a lamp
    c.fence(ring(28, 22, 9, 5))
    c.put("lamp", 32, 23, "Lamp")
    for x in range(29, 36):
        for y in (23, 24, 25):
            if (x, y) not in ((32, 23), (32, 24)):
                c.put("flowerbed", x, y, "Flowers")


def market(c):
    """Downtown Market: the Department Store's plaza with market stalls at its corners, the Game Corner, and the
    Name Rater and Tutor in two narrow houses."""
    # the Department Store block (7x5, door (3,4)) on its 10x9 plot (20-29 x 30-38); x 21 keeps its door on (24, 37)
    c.room("crescent_city_dept_1f", 21, 33, prefab="block_dept")
    c.rect("=", 23, 38, 4, 4)      # the store's plaza, between the flower-bed lawns (it starts at the shop's door)
    c.room("crescent_city_game_corner", 31, 30)
    c.room("crescent_city_name_rater", 31, 37)
    c.room("crescent_city_tutor", 34, 37)
    # a market stall (awning over counter, 3x2) either side of the plaza
    c.put("stall", 20, 38, "Market stall")
    c.put("stall", 27, 38, "Market stall")
    c.put("lamp", 30, 33, "Lamp")
    c.put("lamp", 30, 39, "Lamp")


def waterfront(c):
    c.put("magnolia", 42, 30, "Magnolia")
    c.put("bench", 45, 32, "Bench")
    c.put("magnolia", 48, 30, "Magnolia")
    c.room("crescent_city_conservation", 41, 36, prefab="block_hall")  # 9x5 on its 10x9 plot; door (45, 40)
    c.rect("=", 44, 41, 3, 1)      # the doorstep, out to street 3
    c.room("crescent_city_pokecenter_waterfront", 52, 30)
    c.rect("=", 51, 34, 6, 2)      # from the Pokemon Center to the promenade
    c.room("crescent_city_ice_cream", 51, 37)
    c.put("lamp", 51, 31, "Lamp")
    c.room("crescent_city_riverboat_terminal", 41, 46)   # flush on the quay (y 51)
    c.room("crescent_city_pelipper_post", 51, 46, prefab="warehouse6b")  # the metal warehouse, for variety
    # the one pier: out from the promenade into the river, Rotom's old generator at its end; the riverboat
    # moored north-south along the shore beside it, its bow at the pier
    c.walkway(59, 47, 9, vertical=False, label="Rotom's pier")
    c.put("generator", 67, 47, "Generator", over=True)
    c.put("steamboat_ns", 68, 45, "Riverboat")   # the crossbar of a T: the pier (x 59-67, y 47-48) meets the middle of its west side
    # the levee runs along the promenade's river side (levee_ground)


def drowned_ward(c):
    """The Drowned Ward: two flooded basins either side of street 1, roofless brick shells and cypresses standing
    in black water; the Blacksnake cellar door is the ruin at the south basin's foot, on street 2 (no walkway)."""
    # (the north basin starts at y 6: water within a cell of the canal levee would read as the end of its run)
    blob(c, "~", {6: (43, 54), 7: (42, 55), 8: (42, 55), 9: (42, 54), 10: (43, 52)})
    blob(c, "~", {15: (47, 54), 16: (46, 55), 17: (46, 55), 18: (46, 55), 19: (46, 55), 20: (46, 55),
                  21: (46, 55), 22: (46, 55), 23: (46, 55), 24: (46, 55), 25: (46, 55), 26: (47, 54)})
    c.rect(".", 40, 4, 1, 7)       # a grass verge on Canal Avenue's east kerb, magnolias along it
    c.rect(".", 40, 14, 1, 13)
    c.put("magnolia", 40, 15, "Magnolia")
    c.put("lamp", 40, 18, "Lamp")
    c.put("magnolia", 40, 21, "Magnolia")
    c.put("ruin_a", 43, 6, "Ruin")
    c.put("cypress_water", 47, 7, "Tree")
    c.put("ruin_a", 51, 6, "Ruin")
    # the Blacksnake cellar door: the ruin stands at the basin's south end, its door on street 2 (no walkway)
    c.room("crescent_city_blacksnake_base", 47, 24)
    c.put("ruin_a", 47, 16, "Ruin")
    c.put("cypress_water", 52, 16, "Tree")
    c.put("ruin_a", 51, 21, "Ruin")


FAC = (("Battle Tower (post-game)", "fac_tower", -12), ("Battle Dome (post-game)", "fac_dome", -5),
       ("Battle Palace (post-game)", "fac_palace", 2), ("Battle Arena (post-game)", "fac_arena", 9),
       ("Battle Factory (post-game)", "fac_factory", 16), ("Battle Pike (post-game)", "fac_pike", 23),
       ("Battle Pyramid (post-game)", "fac_pyramid", 30))
FAC_LOBBY = {"fac_tower": "MAP_BATTLE_FRONTIER_BATTLE_TOWER_LOBBY", "fac_dome": "MAP_BATTLE_FRONTIER_BATTLE_DOME_LOBBY",
             "fac_palace": "MAP_BATTLE_FRONTIER_BATTLE_PALACE_LOBBY", "fac_arena": "MAP_BATTLE_FRONTIER_BATTLE_ARENA_LOBBY",
             "fac_factory": "MAP_BATTLE_FRONTIER_BATTLE_FACTORY_LOBBY", "fac_pike": "MAP_BATTLE_FRONTIER_BATTLE_PIKE_LOBBY",
             "fac_pyramid": "MAP_BATTLE_FRONTIER_BATTLE_PYRAMID_LOBBY"}
FAC_DOOR = (52, 51, 50, 49, 50, 51, 52)  # each facility's door row: a shallow bay, the Arena at its head


def frontier(c):
    """Battle Frontier (post-game): seven facilities in a symmetric row about x 11, the Arena in the middle,
    behind an iron fence, on a gentle bay (each stands one row further back than the one outside it, so no two
    stand shoulder to shoulder) round a paved plaza: city flagstones with their stone border, bevelled corners, a
    border of flower beds, the tiered fountain in front of the Arena, benches and lamps; a one-tile gate onto
    Canal Avenue with its guard."""
    gate = [(36, 57)]  # one tile wide: the guard stands in it until the post-game
    c.fence([(x, 45) for x in range(-14, 37)] + [(36, y) for y in range(46, 66)] + [(-14, y) for y in range(46, 66)],
            gaps=gate)
    for (label, prefab, x), door in zip(FAC, FAC_DOOR):
        # every facility's door on its row, facing the plaza; the door is a real warp into the vanilla lobby (the Hoenn facility halls are kept)
        c.put(prefab, x, door + 1 - c.size(prefab)[1], label, interior=FAC_LOBBY[prefab])
    # the plaza: from each facility's front (and the alley beside it, down from the shallower neighbour's front)
    top = {}
    for i, ((_, _, x), door) in enumerate(zip(FAC, FAC_DOOR)):
        for dx in range(5):
            top[x + dx] = door + 1
        if i + 1 < len(FAC):
            for dx in (5, 6):
                top[x + dx] = min(door, FAC_DOOR[i + 1]) + 1
    top[-13] = top[35] = 54                    # bevelled top corners
    for x in range(-13, 36):
        y0 = top.get(x, 53)
        y1 = 60 if x in (-13, -12, 34, 35) else 61 if x in (-11, -10, 32, 33) else 62  # bevelled bottom corners
        c.rect("=", x, y0, 1, y1 - y0 + 1)
    # lawns inside the paving (the stone border runs round each): the fountain's, and four parterres, mirrored about
    # x 11, each with a bed of flowers, a bench and a lamp; props stand on the lawns, not the paving (tile budget)
    c.rect(".", 9, 52, 5, 5)
    c.put("fountain", 10, 53, "Fountain")       # the plaza's centrepiece, in front of the Arena (x 9-13, centre 11)
    for x0 in (-9, -1, 19, 27):
        c.rect(".", x0, 56, 5, 4)
        for dx in (1, 2, 3):
            for y in (56, 57):
                c.put("flowerbed", x0 + dx, y, "Flowers")
        c.put("bench", x0 + 1, 59, "Bench")
        c.put("lamp", x0 + 4 if x0 < 11 else x0, 56, "Lamp")
    for (_, _, x0), door in zip(FAC, FAC_DOOR):  # a planter at each facility's front corners
        for x in (x0, x0 + 4):
            c.put("flowerbed", x, door + 1, "Flowers")
    for i in range(len(FAC) - 1):              # a planter block in each alley, at the shallower facility's foot
        x = FAC[i][2] + 5
        back = min(FAC_DOOR[i], FAC_DOOR[i + 1])
        for dx in (0, 1):
            for y in (back - 1, back):
                c.put("flowerbed", x + dx, y, "Flowers")
    for x in range(-8, 31):                          # the plaza's flower-bed border along its south edge
        c.put("flowerbed", x, 62, "Flowers")
    for x, y in ((-12, 58), (33, 58)):               # a flower seller's cart at each end of the plaza, barrels by them
        c.put("flower_cart", x, y, "Flower cart")
    for x, y in ((-12, 60), (34, 60)):
        c.put("barrel", x, y, "Barrel")
    for x in (-12, -7, -2, 3, 18, 23):  # a row of magnolias along the south edge (the two at design x 28 and 33 stood on the last row against Route 14's marsh: hard colour cut)
        c.put("magnolia", x, 63, "Magnolia")
    c.sign("FrontierSign", 36, 56, "BATTLE FRONTIER\nOpen to champions only.", art=False)
    c.npc("FRONTIER_GUARD", "OBJ_EVENT_GFX_MAN_1", 36, 57, "(The Battle Frontier opens after the Rayquaza finale.)",
          move="MOVEMENT_TYPE_FACE_LEFT", flag="FLAG_UNUSED_0x2D9")  # set after the finale: the guard steps aside


def east_bank(c):
    """The far bank keeps its natural shore and is all long grass (encounters), with bald cypresses standing in the
    water off its shore and in the lake (no marsh: the city's tile budget)."""
    for x, y in ((83, 0), (86, 7)):  # the lake's two (the river itself is clear of trees)
        if all(c.at(x + i, y + j) == "~" and (x + i, y + j) not in c.taken for i in range(-1, 4) for j in range(-1, 4)):
            c.put("cypress_water", x, y, "Tree")
    # the Route 10 lakefront landing (map decision 4, 2026-10-12): a short dirt shore walk on the far bank ('r': the same Johto dirt as
    # Route 10's promenade, which runs down Route 10's west edge, x 0-1, rows 17-24 = this map's rows 15-22): 2 wide, from just back
    # of the shore (row 14) to the seam, with a lamp at its head; the exit cells are Route 10's rows 19-22 = rows 17-20
    c.rect("r", W - OX - 2, 14, 2, 9)
    c.put("lamp", W - OX - 4, 14, "Lamp")
    for y in range(0, 46):
        for x in range(70, W - OX):
            near = lambda r: any((c.at(x + i, y + j) or "") == "~" for i in range(-r, r + 1) for j in range(-r, r + 1))
            if c.at(x, y) == "." and (x, y) not in c.taken and not near(2):
                c.meadow.add((x, y))


def riverside(c):
    """The levee lawn south of the quay: a grove of magnolias in rows, benches between them, flower beds along
    the promenade, a lamp at each end."""
    for x in (42, 46, 50, 54):
        for y in (54, 59):
            c.put("magnolia", x, y, "Magnolia")
    for x in (44, 52):
        c.put("bench", x, 57, "Bench")
    c.put("lamp", 48, 56, "Lamp")
    for x in range(42, 56, 2):
        c.put("flowerbed", x, 63, "Flowers")
        c.put("flowerbed", x + 1, 63, "Flowers")
    c.sign("LeveeSign", 41, 63, "SOUTH: Route 14\nThe levee road.")


def street_life(c):
    """The lawns the big plots left: trees, flower beds and benches in the downtown block and in front of the
    Conservation Center, magnolias between the Frontier facilities and beds along the Frontier's fence."""
    # downtown: the department store's lawn (the plot is 20-29 x 30-38, the block stands at 21-27 x 33-37)
    c.dress("magnolia", 28, 30, "Magnolia")
    c.dress("magnolia", 28, 33, "Magnolia")
    for x in range(22, 28):
        c.dress("flowerbed", x, 32, "Flowers")
    c.dress("bench", 22, 30, "Bench")
    c.dress("bench", 26, 30, "Bench")
    for y in (33, 35, 37):     # a strip of potted shrubs down the lawn's west edge, a barrel by the stall
        c.dress("shrub_pot", 20, y, "Potted shrub")
    c.dress("barrel", 29, 37, "Barrel")
    for dx in (0, 1):
        for y in (36, 37):
            c.dress("flowerbed", 28 + dx, y, "Flowers")
    # the lawn east of the French Quarter (Canal Avenue's east kerb): a flower seller's corner with a barrel, shrubs
    c.dress("flower_cart", 42, 24, "Flower cart")
    c.dress("barrel", 45, 24, "Barrel")
    for x, y in ((42, 16), (44, 20), (42, 27)):
        c.dress("shrub_pot", x, y, "Potted shrub")
    # the Conservation Center's lawn (plot 41-50 x 33-41, the hall stands at 41-49 x 36-40)
    for x in range(43, 48):
        for y in (33, 34):
            c.dress("flowerbed", x, y, "Flowers")
    c.dress("magnolia", 41, 33, "Magnolia")
    c.dress("magnolia", 48, 33, "Magnolia")
    c.dress("bench", 41, 41, "Bench")
    c.dress("bench", 49, 41, "Bench")
    for x in (43, 47):
        c.dress("shrub_pot", x, 41, "Potted shrub")
    # the Frontier: flower beds along the north fence (the facilities' alleys are planted in frontier())
    for (_, _, x0), door in zip(FAC, FAC_DOOR):
        for x in range(x0 + 1, x0 + 4):
            c.dress("flowerbed", x, 46, "Flowers")


def street_lamps(c):
    """Gas lamps along the avenues' outer kerbs every eight paces, never across a side opening."""
    for x, side in ((40, 1),):  # Canal Avenue's grass verge (Rampart Avenue is lit by the park's lamps)
        for y in range(6, 42, 8):
            cells = [(x, y), (x, y + 1)]
            if any(cell in c.taken for cell in cells) or any(c.at(x + side, j) == "=" for j in (y - 1, y, y + 1, y + 2)):
                continue
            c.put("lamp", x, y, "Lamp")


def townsfolk(c):
    """Placeholder townsfolk on lawns and plazas, off the paths."""
    for ident, gfx, x, y, move, text in (
            ("PAINTER", "ARTIST", -1, 37, "FACE_UP", "(Painter: the light on the pond is perfect today.)"),
            ("PARK_STROLLER", "WOMAN_1", 12, 26, "WANDER_AROUND", "(Townsperson: placeholder.)"),
            ("PARK_KID", "LITTLE_BOY", -5, 12, "WANDER_AROUND", "(Kid: I saw something red in the long grass!)"),
            ("MOURNER", "OLD_WOMAN", 4, 17, "FACE_LEFT", "(Townsperson: placeholder.)"),
            ("SHOPPER", "WOMAN_2", 26, 41, "FACE_UP", "(Shopper: placeholder.)"),
            ("QUARTER_GENT", "GENTLEMAN", 26, 26, "FACE_DOWN", "(Townsperson: placeholder.)"),
            ("QUARTER_LASS", "LASS", 20, 6, "FACE_DOWN", "(Townsperson: placeholder.)"),
            ("SAILOR", "SAILOR", 55, 52, "FACE_RIGHT", "(Sailor: the riverboat sails for Pointe Rouge.)"),
            ("FISHERMAN", "FISHERMAN", 58, 36, "FACE_RIGHT", "(Fisherman: placeholder.)"),
            ("STROLLER", "BEAUTY", 46, 31, "FACE_DOWN", "(Townsperson: placeholder.)"),
            ("OLD_MAN", "OLD_MAN", 48, 58, "FACE_DOWN", "(Townsperson: placeholder.)"),
            ("VERGE_BOY", "BOY_1", 40, 9, "FACE_LEFT", "(Townsperson: placeholder.)"),
            ("BUSKER", "MAN_2", 24, 31, "FACE_DOWN", "(Busker: a tune for the shoppers.)"),
            ("SHOP_MOM", "WOMAN_3", 23, 40, "FACE_RIGHT", "(Townsperson: placeholder.)"),
            ("CONSERVATION_KID", "LITTLE_GIRL", 46, 41, "FACE_UP", "(Kid: there is a real alligator inside!)"),
            ("FRONTIER_JOGGER", "MAN_5", -3, 55, "WANDER_AROUND", "(Jogger: I'm training for the Frontier.)"),
            ("FRONTIER_PAIR", "GIRL_2", 19, 60, "FACE_LEFT", "(Townsperson: placeholder.)"),
            ("FRONTIER_FAN", "BOY_2", 25, 58, "FACE_UP", "(Fan: one day I'll battle at the Dome.)"),
            ("PICNICKER", "PICNICKER", 49, 58, "FACE_DOWN", "(Picnicker: the levee breeze is lovely.)")):
        c.npc(ident, "OBJ_EVENT_GFX_" + gfx, x, y, text, move="MOVEMENT_TYPE_" + move)


LEVEE_FROM = 4


def levee_ground(c):
    """The city side of the river is a levee (levee.py, drawn by build.py on 'B' cells): one straight run of levee
    ground down the bank (x 59, beside the promenade), so its cells repeat; Rotom's pier is laid over it. The canal,
    the far bank and the lake keep their natural shores."""
    for y in range(LEVEE_FROM, H):
        if c.at(59, y) == "." and ((59, y) not in c.taken or y in (47, 48)):
            c.rect("B", 59, y, 1, 1)
    # ... and it turns the corner and runs west along the basin canal (the bank row, y 3), the whole way to the edge
    for x in range(-OX + CANAL_WIDE + 2, 60):  # (the levee stops 2 cells short of the wide mouth: the shore there is plain bank, as on Route 6)
        if c.at(x, 3) == "." and (x, 3) not in c.taken:
            c.rect("B", x, 3, 1, 1)


def bevel_junctions(c):
    """Round the corners at the bigger junctions: a street wider than two meeting an avenue or plaza at least three
    wide gets one paving cell in each concave corner, so the corner is a quarter-round instead of a square notch.
    The French Quarter's streets stay a grid; narrow lanes, the promenade and the walks are left alone."""
    def run(x, y, dx, dy):
        n = 1
        for sgn in (1, -1):
            i = 1
            while c.at(x + sgn * i * dx, y + sgn * i * dy) == "=":
                n += 1
                i += 1
        return n
    out = []
    for y in range(H):
        for x in range(-OX, W - OX):
            if c.at(x, y) != "." or (x, y) in c.taken or y > 45:  # (not the Frontier's plaza or the avenue's taper)
                continue
            for hx in (-1, 1):
                for vy in (-1, 1):
                    if c.at(x + hx, y) == "=" and c.at(x, y + vy) == "=" and c.at(x + hx, y + vy) == "=":
                        wide_v = run(x + hx, y, 1, 0)    # the vertical avenue's thickness beside the corner
                        wide_h = run(x, y + vy, 0, 1)    # the horizontal street's thickness above or below it
                        if min(wide_h, wide_v) >= 3:
                            out.append((x, y))
    for x, y in out:
        c.rect("=", x, y, 1, 1)
    print("  bevelled junction corners:", sorted(set(out)))


def build_all():
    c = City()
    water(c)
    streets(c)
    cemetery(c)
    park(c)
    french_quarter(c)
    market(c)
    waterfront(c)
    drowned_ward(c)
    frontier(c)
    east_bank(c)
    riverside(c)
    street_life(c)
    street_lamps(c)
    c.lay_grass()
    bevel_junctions(c)
    levee_ground(c)
    c.npc("PARADE_LEADER", "OBJ_EVENT_GFX_MAN_1", 24, 12, "(Second-line parade leader: placeholder.)")
    c.npc("LAFAYETTE", "OBJ_EVENT_GFX_MAN_1", 43, 42, "(Lafayette: placeholder.)")
    townsfolk(c)
    # the Frontier doors come last in the building list: build_interior.py numbers the Crescent door warps in this order, so no town room's exit
    # warp moves when the seven facility doors open
    fac = {label for label, _, _ in FAC}
    c.buildings.sort(key=lambda b: b["label"] in fac)
    validate(c)
    return c


def validate(c):
    """Placement rules the autotiles need: marsh never 8-adjacent to water; paving never directly left of or above
    a patch (its border would be covered)."""
    bad = []
    for y in range(H):
        for x in range(-OX, W - OX):
            ch = c.at(x, y)
            near = {c.at(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
            if ch == '"' and "~" in near:
                bad.append(f"marsh beside water at ({x},{y})")
            if ch == "=" and (c.at(x + 1, y) in ('"', "~") or c.at(x, y + 1) in ('"', "~")):
                bad.append(f"paving left of/above a patch at ({x},{y})")
    for b in bad[:20]:
        print("  rule:", b)
    if len(bad) > 20:
        print(f"  ... {len(bad)} rule problems")


# ---------------------------------------------------------------- output
def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def write(c):
    grid = "\n".join("".join(r) for r in c.g) + "\n"
    tmp = os.path.join(MAPS, KEY + ".grid.txt.tmp")
    open(tmp, "w").write(grid)
    os.replace(tmp, os.path.join(MAPS, KEY + ".grid.txt"))
    spec = {"_comment": "Generated by crescent.py (hand-designed Crescent City); edit crescent.py, not this file.",
            "map": "CrescentCity", "map_const": "MAP_CRESCENT_CITY", "layout": "LAYOUT_CRESCENT_CITY",
            "layout_dir": "data/layouts/CrescentCity", "tileset": CFG, "mockup": "../orleans_maps/04_crescent_city.png",
            "grid": KEY + ".grid.txt", "edits": [], "buildings": c.buildings, "objects": c.objects, "surf_only": [],
            "items": [], "hidden_items": [], "signs": c.signs,
            "states": crescent_flood.STATES,   # the floodwater on the Route 14 road until badge 6 (CrescentCity_OnLoad)
            "levee_phase": [8, 12],  # shifts the riprap so the north run's corner onto the east bank has no stone-edge seam
            "exits": [{"name": "Route 3 causeway (west)", "cells": [[0, 43], [0, 44]]},
                      {"name": "Route 14 levee road (south)", "cells": [[38 + OX, 65], [39 + OX, 65]]},
                      {"name": "Route 10 lakefront promenade (east)", "cells": [[W - 1, y] for y in (17, 18, 19, 20)],
                       "by_boat": True}]}
    old = os.path.join(MAPS, KEY + ".json")
    if os.path.exists(old):  # keep the interior links build_interior.py wrote
        prev = {b["label"]: b.get("interior") for b in json.load(open(old, encoding="utf-8"))["buildings"]}
        for b in spec["buildings"]:
            if prev.get(b["label"]):
                b["interior"] = prev[b["label"]]
    dump(old, spec)
    return old


def run(cmd):
    r = subprocess.run([sys.executable, "-W", "ignore"] + cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode:
        raise SystemExit(out[-2000:])
    return out


def compose():
    return run([os.path.join(HERE, "compose.py"), os.path.join(HERE, "tilesets", "recipes", CFG + ".json")])


DISTRICTS = [  # design coordinates (x from -OX; no longer used by review())
    ("City Park (whole)", (-14, 2, 30, 41)), ("Old Cemetery", (0, 3, 17, 22)), ("French Quarter", (19, 3, 19, 24)),
    ("Drowned Ward", (40, 2, 20, 26)), ("Downtown Market", (19, 28, 19, 17)),
    ("Waterfront, Riverboat Terminal, steamboat, Rotom's pier", (40, 28, 30, 27)),
    ("Battle Frontier (post-game)", (-14, 44, 52, 22)), ("Emerald River and the far bank", (55, 0, 35, 45))]


def review(spec_path):
    """maps/00_crescent_review.png: the whole map before | after the review-2 round, then 3x crops of every change
    (crescent_review.py; maps/crescent_city_before.png is the build before the round)."""
    import crescent_review
    crescent_review.make()


SAVED = ["tilesets/recipes/orleans_crescent.json", "tilesets/orleans_crescent.json", "tilesets/orleans_crescent.mapping.json",
         "tilesets/orleans_crescent.blends.json", "maps/crescent_city.json", "maps/crescent_city.grid.txt"]


def snapshot():
    """Copies of everything this run rewrites (the tileset, its blends, the spec), so a failed run can be undone."""
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="crescent_")
    for rel in SAVED:
        src = os.path.join(HERE, rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            shutil.copy2(src, os.path.join(tmp, rel))
    tdir = os.path.join(ROOT, "data", "tilesets", "secondary", CFG)
    shutil.copytree(tdir, os.path.join(tmp, "tileset"))
    return tmp


def restore(tmp):
    import shutil
    for rel in SAVED:
        src = os.path.join(tmp, rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(HERE, rel))
    tdir = os.path.join(ROOT, "data", "tilesets", "secondary", CFG)
    for f in os.listdir(os.path.join(tmp, "tileset")):
        src = os.path.join(tmp, "tileset", f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(tdir, f))
        else:
            shutil.copytree(src, os.path.join(tdir, f), dirs_exist_ok=True)


def main(args):
    backup = snapshot()
    try:
        generate(args)
    except BaseException:
        restore(backup)  # leave the last good tileset and spec in place (another tool may build from them)
        print("crescent.py failed: the previous tileset, blends and spec were restored")
        raise


def generate(args):
    run([os.path.join(HERE, "make_town_tilesets.py"), CFG])
    bf = os.path.join(HERE, "tilesets", CFG + ".blends.json")
    if os.path.exists(bf):  # start clean: only the overlays and blends this layout uses get composed
        os.remove(bf)
    c = build_all()
    spec = write(c)
    prev = args[args.index("--preview") + 1] if "--preview" in args else None
    flags = (["--dry-run"] if "--dry-run" in args else []) + (["--preview", prev] if prev else [])
    for attempt in range(3):
        print(compose().splitlines()[0])
        out = run([os.path.join(HERE, "build.py"), spec] + flags)
        print(out.splitlines()[-1])
        if "transition tiles needed" not in out:
            break
    if "--dry-run" in args:
        return
    if "--relink" in args:  # only when no other tool is writing data/layouts/layouts.json at the same time
        print(run([os.path.join(HERE, "build_interior.py")]).splitlines()[-1])
    else:
        print("interiors not relinked: run tools/mapgen/build_interior.py next (it updates the rooms' exit warps)")
    if "--no-check" not in args:
        print(run([os.path.join(HERE, "check.py"), spec]))
        review(spec)


if __name__ == "__main__":
    main(sys.argv[1:])

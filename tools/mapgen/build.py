"""Build a Porymap-ready map from an extracted terrain grid + a map spec.

usage (from the decomp root):
    python tools/mapgen/build.py tools/mapgen/maps/<map>.json [--preview out.png] [--dry-run]

Writes <layout_dir>/map.bin and border.bin, updates the layout size in data/layouts/layouts.json,
and rewrites the events in data/maps/<map>/map.json (warps, objects, items, hidden items).
Scripts for generated NPCs are written to data/maps/<map>/scripts.inc between marker comments.
"""
import json
import os
import struct
import sys
from event_scripts import include_map_scripts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import Tilesets, render  # noqa: E402

COLLISION_SHIFT, ELEVATION_SHIFT = 10, 12


MAPPING = {}  # "source:name" -> metatile id, from composed tilesets' mapping files
USED = set()  # the named pieces this map places (written to tilesets/uses/: a "demand" tileset composes only those)
WANTED = set()  # pieces it needs that its demand-driven tileset left out last time (composed on the next run)
DEMAND = False


PRIMARY_ART = ("brg", "mag", "props")  # overlay art that lives in the primary (make_primary_recipe.py): the railed road bridge
# the rail track and boxcar (route landmark art) over paving / grass: Pointe Rouge's rail yard runs through its seam bands, so just
# these pieces over just these grounds live in the primary (make_primary_recipe.py LMK_IDS, tilesets/orleans_general.blends.json)
PRIMARY_LMK = {f"lmk:{i}" for i in ("15_9", "8_11", "9_11", "10_11", "8_12", "9_12", "10_12")}
PRIMARY_LMK_BASES = ("johto:1C9", "johto:1C8", "johto:1B9", "ekat:grass")


CURRENT_TILESET = ""


def primary_overlay(o):
    """is this overlay (a dict with art, base) of primary art over a primary ground (so it belongs to the primary's blends)?"""
    if o["art"] in PRIMARY_LMK:     # only Pointe Rouge's yard: other maps' landmark rails stay in their own secondary
        return o["base"] in PRIMARY_LMK_BASES and CURRENT_TILESET == "orleans_pointe"
    return o["art"].split(":")[0] in PRIMARY_ART and 0 <= MAPPING.get(o["base"], 9999) < 512
PRIMARY_IDS = None  # metatile ids the (pruned) primary really holds: tilesets/orleans_general.mapping.json
CHECK_PRIMARY = False  # set by Builder for maps on gTileset_OrleansGeneral


def primary_ids():
    global PRIMARY_IDS
    if PRIMARY_IDS is None:
        p = os.path.join(HERE, "tilesets", "orleans_general.mapping.json")
        PRIMARY_IDS = {0} | set(json.load(open(p))["metatiles"].values()) if os.path.exists(p) else set()
    return PRIMARY_IDS


def hx(s):
    """A metatile id: hex ("12B") or a named piece from a composed tileset ("ekat:water_C"). A hex id below 512 is a piece of
    the primary: the primary is pruned to what the maps use (primary_keep.py), so an id outside it would draw an empty cell."""
    if CHECK_PRIMARY and ":" not in s and int(s, 16) < 512 and int(s, 16) not in primary_ids():
        raise SystemExit(f"primary metatile {s} was pruned from gTileset_OrleansGeneral: add it to primary_keep.py "
                         f"(EXTRA), write the keep file and recompose the primary")
    if ":" in s:
        USED.add(s)
        if s not in MAPPING:
            if DEMAND:  # left out of the tileset because no map used it before: ask for it, draw a stand-in
                WANTED.add(s)
                return 0
            raise SystemExit(f"unknown metatile name {s}")
        return MAPPING[s]
    return int(s, 16)


def script_suffix(local_id, map_const):
    """LOCALID_ISLE_MARAIS_RECRUITER_1 -> Recruiter1 (MAP_ORLEANS_ROUTE1's ids are LOCALID_ROUTE1_...)"""
    rest = local_id
    for prefix in (map_const[len("MAP_"):], map_const[len("MAP_"):].replace("ORLEANS_", "", 1)):
        rest = rest.replace("LOCALID_" + prefix + "_", "")
    return "".join(p.title() for p in rest.split("_"))


def block(mid, collision=0, elev=3):
    return mid | (collision << COLLISION_SHIFT) | (elev << ELEVATION_SHIFT)


class Builder:
    def __init__(self, spec_path):
        self.spec = json.load(open(spec_path, encoding="utf-8"))
        try:  # the story pass (story_overlay.py): NPCs, items and triggers layered on whatever generator wrote the spec
            import story_overlay
            story_overlay.apply(self.spec)
        except ImportError:
            pass
        self.key = os.path.splitext(os.path.basename(spec_path))[0]
        self.band, self.band_log, self.band_unresolved = set(), [], []
        self.band_blends = set()
        self.border_names, self.border_style, self.wall, self.edge = None, None, set(), {}
        self.ts = json.load(open(os.path.join(HERE, "tilesets", self.spec["tileset"] + ".json")))
        global DEMAND, CHECK_PRIMARY
        CHECK_PRIMARY = self.ts.get("primary") == "gTileset_OrleansGeneral"
        recipe = os.path.join(HERE, "tilesets", "recipes", self.spec["tileset"] + ".json")
        DEMAND = os.path.exists(recipe) and bool(json.load(open(recipe, encoding="utf-8")).get("demand"))
        for m in self.ts.get("mappings", []):
            MAPPING.update(json.load(open(os.path.join(HERE, "tilesets", m)))["metatiles"])
        grid_path = os.path.join(os.path.dirname(spec_path), self.spec["grid"])
        self.grid = [list(l.rstrip("\n")) for l in open(grid_path) if l.strip()]
        self.h, self.w = len(self.grid), len(self.grid[0])
        for ch, x, y, w, h in self.spec.get("edits", []):
            for j in range(y, y + h):
                for i in range(x, x + w):
                    self.grid[j][i] = ch
        # building footprints from the mockup are just ground: real buildings are prefabs drawn on top,
        # and leaving these marks would stop patch borders being drawn next to them
        for row in self.grid:
            for i, c in enumerate(row):
                if c in "HKPM":
                    row[i] = "."
        self.blocks = [[0] * self.w for _ in range(self.h)]
        self.warps = []
        self.pending_blends = {}

    def at(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return None  # off-map: treated as "same as neighbour" by callers

    # --- terrain ---------------------------------------------------------
    def terrain(self):
        T, A = self.ts["terrain"], self.ts["autotile"]
        for a in A.values():
            if a.get("smooth"):
                self.smooth(a["smooth"], ".")
        for y in range(self.h):
            for x in range(self.w):
                t = T[self.grid[y][x]]
                mid, coll = hx(t["tile"]), t.get("collision", 0)  # collision: 1 = blocking terrain (dry-country pepper rows)
                kind = t.get("autotile")
                if kind in ("path", "levee", "paved", "path_g"):  # path_g: the Johto dirt path kept on grass beside the dry-country road set
                    mid = self.path_tile(x, y, A[kind])
                elif kind == "octagon":
                    mid = self.octagon_tile(x, y, A[t["autotile_set"]])
                elif kind == "bank":
                    mid = self.bank_tile(x, y, A["bank"])
                elif kind == "shore":
                    mid = self.shore_tile(x, y, A["shore"])
                elif kind == "boardwalk":
                    mid = self.boardwalk_tile(x, y, A["boardwalk"])
                elif kind == "churchyard":
                    a = A["churchyard"]
                    if (x, y) in self.grave_cells(a):
                        mid, coll = hx(a["grave"]), 1
                elif kind == "tombs":
                    a = A["tombs"]
                    if (x + y) % 2 == 0:
                        mid, coll = hx(a["stone"]), a["stone_collision"]
                    else:
                        mid = hx(a["floor"])
                self.blocks[y][x] = block(mid, coll, t["elev"])
        if "bank" in A:
            self.bank_lips(A["bank"])
        for name, a in A.items():
            if a.get("kind") == "octagon":
                self.octagon_land(a)
            elif a.get("kind") == "corners":
                self.corners(a)
        # patch-interior terrain (tall grass): only on cells whose four dual-grid corners are all inside
        # the patch; edge cells keep the patch's own border pieces so the edge stays soft
        for ch, t in T.items():
            if "interior_of" in t:
                for y in range(self.h):
                    for x in range(self.w):
                        if self.grid[y][x] == ch and all(self.at(min(x + dx, self.w - 1), min(y + dy, self.h - 1))
                                                         in t["interior_of"] for dx in (0, 1) for dy in (0, 1)):
                            self.blocks[y][x] = block(hx(t["tile"]), 0, t["elev"])
        self.water_decor()

    CORNER_KEYS = {
        "1111": "C", "0011": "N", "1100": "S", "0101": "W", "1010": "E",
        "0111": "inNW", "1011": "inNE", "1101": "inSW", "1110": "inSE",
        "0001": "landSE", "0010": "landSW", "0100": "landNE", "1000": "landNW",
        "0110": "sTLBR", "1001": "sTRBL",
    }

    def corners(self, a):
        """Dual-grid autotiling for corner-based sets (Ekat99's swamp octagons).

        Each drawn tile is picked from what its four corners sit on: the corners of tile (x, y) are
        cells (x, y), (x+1, y), (x, y+1), (x+1, y+1), so the patch boundary runs through tile middles
        and every diagonal, bend and mouth gets a matching piece. A tile with two or more corners in
        the patch takes the patch's elevation (e.g. surfable water); otherwise it stays land."""
        con, on = a["connects"], a["apply_on"]
        if self.key in ("route_16", "route_17") and "p" in self.ts["terrain"] and "d" in con:
            con += "p"   # the Johto road through the dry join (Route 17 / Redfield) is dry underfoot: no dry edge pieces beside it
        neutral = a.get("neutral", "")
        patch_elev = a["elev"]
        cl = lambda v, hi: max(0, min(v, hi - 1))

        def resolved(x, y):
            """Piers/boats count as water only where they stand over water: look across them."""
            c = self.grid[y][x]
            if c not in neutral:
                return c in con
            for ring in (((1, 0), (-1, 0), (0, 1), (0, -1)), ((1, 1), (-1, 1), (1, -1), (-1, -1))):
                vals = [self.grid[y + dy][x + dx] in con for dx, dy in ring
                        if 0 <= x + dx < self.w and 0 <= y + dy < self.h and self.grid[y + dy][x + dx] not in neutral]
                if vals:
                    return sum(vals) * 2 >= len(vals)
            return True

        inside = lambda x, y: resolved(cl(x, self.w), cl(y, self.h))
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] not in on:
                    continue
                if a.get("graves") and (x, y) in self.grave_cells(self.ts["autotile"][a["graves"]]):
                    continue
                bits = "".join("1" if inside(x + dx, y + dy) else "0" for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)))
                if bits == "0000":
                    continue
                key = self.CORNER_KEYS[bits]
                tile = a[key]
                alts = a.get("alt_land") or []
                alts = alts if isinstance(alts, list) else [alts]
                corners = [(x + dx, y + dy) for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1))]
                outside = [c for c, bit in zip(corners, bits) if bit == "0"]
                ch = lambda c: self.grid[cl(c[1], self.h)][cl(c[0], self.w)]
                hit = [alt for alt in alts if any(ch(c) in alt["chars"] for c in outside)]
                if hit:
                    alt = hit[0]
                    tile = alt["tiles"].get(key, tile)
                    if any(ch(c) not in alt["chars"] for c in outside) and alt.get("blend"):
                        # three terrains meet (e.g. water, mud, grass): blend the grass-bank and the
                        # mud-bank pieces along the land patch's own soft edge
                        bl = alt["blend"]
                        mbits = "".join("1" if (bit == "1" or ch(c) in alt["chars"]) else "0" for c, bit in zip(corners, bits))
                        mkey = self.CORNER_KEYS.get(mbits)
                        if (x, y) in self.band:   # no secondary blend tile in a seam band: band_rules.repair() removes the junction
                            self.band_blends.add((x, y))
                        elif mkey:
                            m_tile = bl["patch"][mkey] if not isinstance(bl["patch"][mkey], list) else bl["patch"][mkey][0]
                            a_tile = a[key] if not isinstance(a[key], list) else a[key][0]
                            bid = f"blend_{bl['name']}_{key}_{mkey}"
                            if f"patch:{bid}" in MAPPING:
                                tile = f"patch:{bid}"
                            else:
                                self.pending_blends[bid] = {"id": bid, "blend": {"A": a_tile, "B": alt["tiles"][key],
                                                            "M": m_tile, "land": bl["land"]}}
                if isinstance(tile, list):  # variations for the open patch (none inside a seam band: they might be secondary)
                    tile = tile[0] if ((x * 31 + y * 17) % 9 or (x, y) in self.band) else tile[(x * 7 + y * 13) % len(tile)]
                n = bits.count("1")
                elev = patch_elev if n >= 2 else self.ts["terrain"].get(self.grid[y][x], {"elev": 3})["elev"]
                # "collision": a blocking patch (the dry country's cane wall): its tiles with two or more corners in it
                self.blocks[y][x] = block(hx(tile), a.get("collision", 0) if n >= 2 else 0, elev)
        if a.get("face"):
            # "face": the cliff's face extension (dry-country rock_wall, make_dry_country.face_cells): under every south edge
            # and outer corner the plain cell below the wall gets a face piece (blocking); _il / _ir when the wall steps
            # beside it on the west / east
            wall = lambda x, y: self.grid[cl(y, self.h)][cl(x, self.w)] in con   # off the map edge the wall carries on
            for y in range(self.h):
                for x in range(self.w):
                    if self.grid[y][x] not in on or self.grid[y][x] in con:
                        continue
                    if wall(x + 1, y) or wall(x, y + 1) or wall(x + 1, y + 1):
                        continue
                    n, ne = y > 0 and wall(x, y - 1), y > 0 and wall(x + 1, y - 1)
                    il = wall(x - 1, y) or wall(x - 1, y + 1)
                    ir = wall(x + 2, y) or wall(x + 2, y + 1)
                    if n and ne:
                        key = "face" + ("_ilr" if il and ir else "_il" if il else "_ir" if ir else "")
                    elif n:
                        key = "face_r" + ("_il" if il else "")
                    elif ne:
                        key = "face_l" + ("_ir" if ir else "")
                    else:
                        continue
                    self.blocks[y][x] = block(hx(a["face"][key]), 1, patch_elev)
        self._corner_sets = getattr(self, "_corner_sets", []) + [a]

    def grave_cells(self, a):
        """Headstones on every other column of every other row of the churchyard, from its top-left."""
        if not hasattr(self, "_graves"):
            cells = [(x, y) for y in range(self.h) for x in range(self.w) if self.grid[y][x] in a["chars"]]
            if not cells:
                self._graves = set()
                return self._graves
            x0, y0 = min(c[0] for c in cells), min(c[1] for c in cells)
            full = lambda x, y: all(self.at(x + dx, y + dy) in a["chars"] for dx in (0, 1) for dy in (0, 1))
            self._graves = {(x, y) for x, y in cells if full(x, y) and (x - x0) % a["every_x"] == 0 and (y - y0) % a["every_y"] == 0}
        return self._graves

    def smooth(self, chars, land):
        """Remove one-tile spurs and notches from a patch so its octagon edge pieces join up."""
        g = self.grid
        inside = lambda x, y: 0 <= x < self.w and 0 <= y < self.h and g[y][x] in chars
        for _ in range(6):
            changed = False
            for y in range(self.h):
                for x in range(self.w):
                    n = sum(inside(i, j) for i, j in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
                    edge = x in (0, self.w - 1) or y in (0, self.h - 1)
                    if g[y][x] == chars[0] and n <= 1 and not edge:
                        g[y][x] = land
                        changed = True
                    elif g[y][x] in land and n >= 3:
                        g[y][x] = chars[0]
                        changed = True
            if not changed:
                break

    def octagon_tile(self, x, y, a):
        """Cell inside an RPG-Maker-style octagon patch (water, marsh, mud): edge or diagonal piece."""
        con = a["connects"]
        out = lambda i, j: not self.same(i, j, con)
        n, s, w, e = out(x, y - 1), out(x, y + 1), out(x - 1, y), out(x + 1, y)
        for cond, key in ((n and w, "inNW"), (n and e, "inNE"), (s and w, "inSW"), (s and e, "inSE"),
                          (n, "N"), (s, "S"), (w, "W"), (e, "E")):
            if cond:
                return hx(a[key])
        centers = a["C"] if isinstance(a["C"], list) else [a["C"]]
        return hx(centers[(x * 7 + y * 13) % len(centers)] if (x * 31 + y * 17) % 9 == 0 and (x, y) not in self.band else centers[0])

    def octagon_land(self, a):
        """Land cells hugging a patch's diagonal get the matching sliver of the patch."""
        con, on = a["connects"], a["land_on"]
        inside = lambda i, j: self.at(i, j) is not None and self.at(i, j) in con
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] not in on:
                    continue
                n, s, w, e = inside(x, y - 1), inside(x, y + 1), inside(x - 1, y), inside(x + 1, y)
                key = ("landSE" if s and e else "landSW" if s and w else
                       "landNE" if n and e else "landNW" if n and w else None)
                if key:
                    self.blocks[y][x] = block(hx(a[key]), 0, self.ts["terrain"][self.grid[y][x]]["elev"])

    def bank_tile(self, x, y, a):
        """Water cell of a muddy-bank pond: bank piece on the N/W/E sides that touch land."""
        con = a["connects"]
        land = lambda i, j: not self.same(i, j, con)
        n, w, e = land(x, y - 1), land(x - 1, y), land(x + 1, y)
        if n:
            key = "land_NW" if w else "land_NE" if e else "land_N"
        elif w and not e:
            key = "land_W"
        elif e and not w:
            key = "land_E"
        else:
            return hx(self.ts["terrain"][self.grid[y][x]]["tile"])
        return hx(a[key])

    def bank_lips(self, a):
        """Land cells directly south of water show the bank's lower lip."""
        con = a["connects"]
        for y in range(1, self.h):
            for x in range(self.w):
                if self.grid[y][x] not in a["lip_on"] or self.grid[y - 1][x] not in con:
                    continue
                wet = lambda i: self.at(i, y - 1) is None or self.at(i, y - 1) in con
                key = "lip_W" if not wet(x - 1) else "lip_E" if not wet(x + 1) else "lip"
                self.blocks[y][x] = block(hx(a[key]), 0, self.ts["terrain"][self.grid[y][x]]["elev"])

    def water_decor(self):
        """Scatter decoration (lily pads, logs) on open water, away from shores, deterministically."""
        for ch, t in self.ts["terrain"].items():
            d = t.get("decor")
            if not d:
                continue
            r = d.get("min_open", 1)
            for y in range(self.h):
                for x in range(self.w):
                    if self.grid[y][x] != ch:
                        continue
                    if x in (0, self.w - 1) or y in (0, self.h - 1):  # none on the outer ring: a plant on the seam reads as a cut across a join
                        continue
                    if any(self.at(i, j) not in (ch, None) for i in range(x - r, x + r + 2) for j in range(y - r, y + r + 2)):
                        continue
                    hsh = (x * 73856093 ^ y * 19349663) % 1000
                    if hsh < d["rate"] * 1000:
                        mid = hx(d["tiles"][hsh % len(d["tiles"])])
                        self.blocks[y][x] = block(mid, d["collision"], t["elev"])

    def same(self, x, y, connects):
        c = self.at(x, y)
        return c is None or c in connects

    def path_tile(self, x, y, a):
        con = a["connects"]
        if (x, y) in self.band and self.key in ("route_16", "route_17") and "C" in a and a is self.ts["autotile"].get("path_g"):
            return hx(a["C"])  # the Johto path through a dry-country seam band: plain dirt, no green kerb pieces against the sand
        if not hasattr(self, "_decks"):  # a bridge's deck carries the road on: no kerb or rounded end against it
            self._decks = {(b["x"] + i, b["y"] + j) for b in self.spec.get("buildings", [])
                           if b.get("label") == "Bridge" for i, j in b.get("passable", [])}
        same = lambda i, j: self.same(i, j, con) or (i, j) in self._decks
        n, s = same(x, y - 1), same(x, y + 1)
        w, e = same(x - 1, y), same(x + 1, y)
        # an edge piece only makes sense if the path is at least 2 wide across that edge
        if not n and not s:
            n = s = True
        if not w and not e:
            w = e = True
        key = ("N" if not n else "S" if not s else "") + ("W" if not w else "E" if not e else "")
        if not key and "iNW" in a:
            # inner corners where two paths meet and only the diagonal is grass
            for dx, dy, k in ((-1, -1, "iNW"), (1, -1, "iNE"), (-1, 1, "iSW"), (1, 1, "iSE")):
                if not same(x + dx, y + dy):
                    return hx(a[k])
        return hx(a[key or "C"])

    def shore_tile(self, x, y, a):
        con = a["connects"]
        land = lambda i, j: not self.same(i, j, con)
        n, w, e = land(x, y - 1), land(x - 1, y), land(x + 1, y)
        if n and w and "land_NW" in a:
            return hx(a["land_NW"])
        if n and e and "land_NE" in a:
            return hx(a["land_NE"])
        if n:
            return hx(a["land_N"])
        if w and not e:
            return hx(a["land_W"])
        if e and not w:
            return hx(a["land_E"])
        if land(x - 1, y - 1) and not (w or n):
            return hx(a["diag_NW"])
        if land(x + 1, y - 1) and not (e or n):
            return hx(a["diag_NE"])
        return hx(self.ts["terrain"]["~"]["tile"])

    def boardwalk_tile(self, x, y, a):
        con = a["connects"]
        vert = self.at(x, y - 1) in con or self.at(x, y + 1) in con
        horiz = self.at(x - 1, y) in con or self.at(x + 1, y) in con
        # a 2-wide vertical pier also has horizontal neighbours; prefer vertical unless it's clearly a horizontal run
        run_h = sum(1 for i in range(x - 2, x + 3) if self.at(i, y) in con)
        run_v = sum(1 for j in range(y - 2, y + 3) if self.at(x, j) in con)
        rows = a["vertical"] if run_v >= run_h else a["horizontal"]
        if rows is a["vertical"]:
            # pick left/right column from the position within the pier
            col = 0 if self.at(x - 1, y) not in con else 1
            return hx(rows[y % 2][col])
        row = 0 if self.at(x, y - 1) not in con else 1
        return hx(rows[row][x % 2])

    def draw(self):
        """Everything, in order: terrain, river levees, city approaches, then the buildings and objects on top.
        Every tool that draws a map (build, check, previews) goes through here so they all see the same map.
        The seam-band rule (band_rules.py) is applied around it: props out of the bands first, then draw / repair / draw
        until no band cell holds a secondary piece (or nothing more can be repaired)."""
        import band_rules
        import borders
        band_rules.prepare(self, self.key)
        borders.prepare(self, self.key)
        if not self.band:
            return self.draw_once()
        used0, wanted0, pend0 = set(USED), set(WANTED), dict(self.pending_blends)
        for rnd in range(band_rules.MAX_ROUNDS):
            self.draw_once()
            if not band_rules.repair(self):
                break
            USED.clear(); USED.update(used0); WANTED.clear(); WANTED.update(wanted0)
            self.pending_blends = dict(pend0)
            self.warps = []
            self.band_blends = set()
            for a in ("_corner_sets", "_decks", "_graves"):
                if hasattr(self, a):
                    delattr(self, a)
            self.blocks = [[0] * self.w for _ in range(self.h)]
        left = band_rules.violations(self)
        if left:
            self.band_log.append(f"{len(left)} band cells are still secondary pieces after repair: "
                                 + ", ".join(sorted({n for *_, n in left}))[:300])

    def draw_once(self):
        self.terrain()
        self.levee()
        import approach
        approach.draw(self)  # city paving breaking up into a route's dirt road ('&' cells)
        self.states()
        self.buildings()
        for x, y in self.spec.get("block", []):  # cells made impassable on top of whatever is drawn there (spec "block")
            self.blocks[y][x] = (self.blocks[y][x] & ~0x0C00) | (1 << 10)
        import borders
        borders.apply(self)  # the inward walls and their edge cells (borders.py)
        self.sight_cells()

    def sight_cells(self):
        """A stationary NPC's elevation is the elevation of the cell it stands on (the engine overwrites the template value when the object
        spawns), and a trainer's sight check treats an elevation mismatch as a wall. So a trainer on land (elevation 3) looking over water
        (elevation 1) is blind to a surfing player (ch8_2 NIT-1: Germain; Route 6's fisherman, Route 19's sailor and boy). The cell under
        such a trainer gets elevation 0 (ELEVATION_TRANSITION: matches every elevation); nobody can stand there anyway. sight_lint.py proves it."""
        face = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        for o in self.spec.get("objects", []):
            d = face.get(str(o.get("move", "")).rsplit("_", 1)[-1])
            if not o.get("sight") or d is None:
                continue
            x, y = o["x"], o["y"]
            if not (0 <= x < self.w and 0 <= y < self.h):
                continue
            own = self.blocks[y][x] >> ELEVATION_SHIFT
            if own in (0, 15):
                continue
            for dist in range(1, int(o["sight"]) + 1):   # along the line until a wall: any walkable cell of another elevation blinds the trainer
                nx, ny = x + d[0] * dist, y + d[1] * dist
                if not (0 <= nx < self.w and 0 <= ny < self.h) or (self.blocks[ny][nx] >> COLLISION_SHIFT) & 3:
                    break
                ne = self.blocks[ny][nx] >> ELEVATION_SHIFT
                if ne not in (0, 15) and ne != own:
                    self.blocks[y][x] &= 0x0FFF
                    break

    def states(self):
        """Alternative looks a map script swaps in with setmetatile (spec "states": {name: [cells]}, e.g. Storm's
        Edge's drawbridge raised). Each cell is {"x", "y", "overlay": art (drawn over the terrain beneath, like a
        prefab overlay; optional "layer", "behavior") or "tile": a named piece ("terrain": the terrain tile itself),
        "collision": 0/1}. Resolved here, before the buildings, so overlays sit on the terrain; the pieces count as
        used (a demand tileset keeps them) and write_scripts() emits <Map>_EventScript_State<name> with the ids.
        setmetatile keeps the cell's elevation from map.bin."""
        self.state_cells = {}
        for name, cells in self.spec.get("states", {}).items():
            out = []
            for c in cells:
                x, y = c["x"], c["y"]
                if "overlay" in c:
                    mid = hx(self.overlay(c["overlay"], x, y, behavior=c.get("behavior"), layer=c.get("layer")))
                elif c.get("tile") == "terrain":
                    mid = self.blocks[y][x] & 0x3FF
                else:
                    mid = hx(c["tile"])
                out.append((x, y, mid, c.get("collision", 0)))
            self.state_cells[name] = out

    # --- levees ----------------------------------------------------------
    def levee(self):
        """River-channel levees (levee.py): the levee ground ('B') and the water beside it redrawn pixel by pixel
        over the terrain just laid. Every distinct cell is a metatile of its own, requested from compose through
        the blends file like the transitions (its image saved under tilesets/levee/)."""
        bank = {(x, y) for y in range(self.h) for x in range(self.w) if self.grid[y][x] == "B"}
        if not bank:
            return
        import hashlib
        import levee
        root = os.getcwd()
        ts = Tilesets(os.path.join(root, self.ts["primary_dir"]), os.path.join(root, self.ts["secondary_dir"]))
        inv = {mid: n for n, mid in MAPPING.items()}
        blocked = set()  # bridges and docks: a levee run ends before them
        for b in self.spec.get("buildings", []):
            if b.get("label") in ("Bridge", "Dock", "Boardwalk", "Pier") and b.get("rows"):
                if "levee_blocks" in b:  # the cells where a levee run ends (a dock's planks: its posts hang in the water)
                    blocked |= {(b["x"] + i, b["y"] + j) for i, j in b["levee_blocks"]}
                    continue
                blocked |= {(b["x"] + i, b["y"] + j) for j, row in enumerate(b["rows"]) for i, c in enumerate(row)
                            if c is not None}  # a gap in a dock's rows (no piece) is open ground
        grid = ["".join(r) for r in self.grid]
        # open water's variations (lilies, weeds) give way to plain water under the riprap: fewer distinct cells
        plain = {}
        for a in self.ts["autotile"].values():
            for v in a.values():
                if isinstance(v, list) and v and isinstance(v[0], str) and v[0] in MAPPING:
                    plain.update({MAPPING[n]: MAPPING[v[0]] for n in v[1:] if n in MAPPING})

        def base(x, y):
            mid = self.blocks[y][x] & 0x3FF
            if grid[y][x] in levee.WATER and mid in plain:
                mid = plain[mid]
                self.blocks[y][x] = (self.blocks[y][x] & ~0x3FF) | mid
            return ts.metatile(mid)
        levee.PHASE = tuple(self.spec.get("levee_phase", (0, 0)))  # (riprap shift, px; default none)
        cells = levee.render(grid, bank, base, blocked)
        out_dir = os.path.join(HERE, "tilesets", "levee")
        os.makedirs(out_dir, exist_ok=True)
        for (x, y), im in cells.items():
            if (x, y) in self.band:
                continue  # no secondary levee piece in a seam band (the bank is plain ground and water there)
            # the levee is an overlay on the named ground piece under it, combined by compose from the source
            # art (so the name doesn't change when a recompose nudges the ground's palette)
            under = inv.get(self.blocks[y][x] & 0x3FF)
            if not under:
                continue  # an unnamed tile underneath: leave the cell as it is
            lid = "lv_" + hashlib.sha1(im.tobytes() + under.encode()).hexdigest()[:12]
            if f"patch:{lid}" in MAPPING:
                self.blocks[y][x] = (self.blocks[y][x] & ~0x3FF) | MAPPING[f"patch:{lid}"]
                USED.add(f"patch:{lid}")
                continue
            path = os.path.join(out_dir, lid + ".png")
            if not os.path.exists(path):
                im.save(path)
            self.pending_blends[lid] = {"id": lid, "pixels": os.path.relpath(path, root).replace(os.sep, "/"),
                                        "base": under, "attr_of": under, "group": "levee"}

    # --- buildings -------------------------------------------------------
    def buildings(self):
        for b in self.spec.get("buildings", []):
            # a spec building may carry its own rows/passable (e.g. a pier cut to length from the pier prefab)
            p = dict(self.ts["prefabs"][b["prefab"]], **{k: b[k] for k in ("rows", "passable") if k in b})
            passable = {tuple(c) for c in p.get("passable", [])}
            door = p.get("door")
            # "closed": a building with no interior (a route's shed, the post-game Frontier): its door stays shut
            doors = [] if not door or b.get("closed") else door if isinstance(door[0], list) else [door]
            bridge = b.get("label") == "Bridge"
            for j, row in enumerate(p["rows"]):
                for i, mid in enumerate(row):
                    x, y = b["x"] + i, b["y"] + j
                    if mid is None or not (0 <= x < self.w and 0 <= y < self.h):
                        continue
                    if bridge:
                        self.bridge_cell(mid, x, y, (i, j) in passable)
                        continue
                    if isinstance(mid, dict) and mid.get("only_water") and (self.blocks[y][x] >> 12) != 1:
                        continue  # e.g. pilings: only where the cell is water
                    if isinstance(mid, dict) and "overlay" in mid:
                        mid = self.overlay(mid["overlay"], x, y, upper=mid.get("upper", False), walk=mid.get("walk", False),
                                           behavior=mid.get("behavior"), vflip=mid.get("vflip", False))
                    elif isinstance(mid, dict):
                        mid = self.variant(mid["var"], x, y)
                    coll = 0 if (i, j) in passable or [i, j] in doors else 1
                    self.blocks[y][x] = block(hx(mid), coll, p.get("elev", 3))
            for dx, dy in doors:
                self.warps.append({"x": b["x"] + dx, "y": b["y"] + dy, "label": b["label"], "interior": b.get("interior")})
            if bridge:
                self.bridge_heads(b, p["rows"], passable)

    # bridges a surfer can pass under: the deck and rails on the top layer over the water. Walkers cross at
    # elevation 4 (drawn above the top layer), surfers stay at 1 (drawn below it); the deck over the water is
    # elevation 15 (any level), the rails over the water elevation 1 (surfers pass, walkers can't step on them)
    def bridge_cell(self, mid, x, y, deck):
        wet = self.grid[y][x] in "~I"
        art = mid["overlay"] if isinstance(mid, dict) else mid
        if deck:
            m = self.overlay(art, x, y, behavior="MB_BRIDGE_OVER_POND_LOW" if wet else None, layer="normal")
            self.blocks[y][x] = block(hx(m), 0, 15 if wet else 4)
        elif wet:
            self.blocks[y][x] = block(hx(self.overlay(art, x, y, layer="normal")), 0, 1)
        else:  # an end post on the bank
            self.blocks[y][x] = block(hx(self.overlay(art, x, y)), 1, 3)

    def bridge_heads(self, b, rows, passable):
        """Each end of the deck steps down to the street (elevation 3) through a transition cell (elevation 0),
        which must not touch the water (a surfer could ride onto it): until it can, the bridgehead (4) runs on."""
        n_rows, n_cols = len(rows), len(rows[0])
        ew = all(j in (1, 2) for _, j in passable) and n_rows == 4
        ends = []
        for i, j in passable:
            if ew and i in (0, n_cols - 1):
                ends.append((b["x"] + i, b["y"] + j, -1 if i == 0 else 1, 0))
            elif not ew and j in (0, n_rows - 1):
                ends.append((b["x"] + i, b["y"] + j, 0, -1 if j == 0 else 1))
        wet = lambda x, y: 0 <= x < self.w and 0 <= y < self.h and self.grid[y][x] in "~I"
        for x, y, dx, dy in ends:
            for _ in range(3):
                x, y = x + dx, y + dy
                if not (0 <= x < self.w and 0 <= y < self.h) or wet(x, y) or (self.blocks[y][x] >> COLLISION_SHIFT) & 3:
                    break
                touches = any(wet(x + a, y + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                self.blocks[y][x] = (self.blocks[y][x] & ~(0xF << ELEVATION_SHIFT)) | ((4 if touches else 0) << ELEVATION_SHIFT)
                if not touches:
                    break

    def overlay(self, art, x, y, upper=False, walk=False, behavior=None, layer=None, vflip=False):
        """An object cell (e.g. the pirogue) composited over whatever terrain tile is underneath.
        Missing combinations are requested from compose through the blends file, like blends.
        layer="normal": the art on the top layer, over characters at low elevation (bridges you surf under)."""
        inv = {mid: n for n, mid in MAPPING.items()}
        under = inv.get(self.blocks[y][x] & 0x3FF)
        # a patch's random variations (plants on mud, reeds on marsh) become the plain tile under objects
        for a in self.ts["autotile"].values():
            for v in a.values():
                if isinstance(v, list) and v and isinstance(v[0], str) and under in v[1:]:
                    under = v[0]
        if not under or ":" not in under:
            raise SystemExit(f"overlay {art} at ({x},{y}): no named tile underneath ({under})")
        oid = ("ovl_" + art.replace(":", "_") + "__" + under.replace("patch:", "").replace(":", "_")
               + ("__door" if behavior and not layer else "") + (f"__{layer}" if layer else "") + ("__vflip" if vflip else ""))
        if f"patch:{oid}" in MAPPING:
            return f"patch:{oid}"
        spec = {"base": under, "art": art}
        if layer:
            spec["layer"] = layer
        if upper:
            spec["upper"] = True
        if vflip:
            spec["vflip"] = True
        if walk:
            spec["walk"] = True
        if behavior:
            spec["behavior"] = behavior
        self.pending_blends[oid] = {"id": oid, "overlay": spec}
        return under

    def variant(self, name, x, y):
        """A prefab piece drawn over whatever is underneath (e.g. pier planks over grass, bank or water)."""
        v = self.ts["variants"][name]
        under = self.blocks[y][x]
        inv = {mid: n for n, mid in MAPPING.items()}
        under_name = inv.get(under & 0x3FF)
        if under_name in v:
            return v[under_name]
        return v["water" if (under >> 12) == 1 else "land"]

    # --- output ----------------------------------------------------------
    def flat(self):
        return [v for row in self.blocks for v in row]

    def write_layout(self, root):
        d = os.path.join(root, self.spec["layout_dir"])
        open(os.path.join(d, "map.bin"), "wb").write(struct.pack(f"<{self.w * self.h}H", *self.flat()))
        border = [block(hx(m), 0, 0) for m in (getattr(self, "border_names", None) or self.ts["border"])]
        open(os.path.join(d, "border.bin"), "wb").write(struct.pack("<4H", *border))
        lp = os.path.join(root, "data/layouts/layouts.json")
        layouts = json.load(open(lp))
        for l in layouts["layouts"]:
            if l.get("id") == self.spec["layout"]:
                l["width"], l["height"] = self.w, self.h
                l["primary_tileset"], l["secondary_tileset"] = self.ts["primary"], self.ts["secondary"]
        with open(lp, "w", newline="\n") as f:
            json.dump(layouts, f, indent=2)
            f.write("\n")

    def event_elevation(self, x, y, explicit=None):
        """Elevation for a bg_event (hidden item, sign) at (x, y). The engine compares it with the PLAYER's elevation, so it must match the
        walkable neighbour the player faces it from: 3 on land, 1 on surfable water, 4 on a bridge deck. An explicit spec value wins; else
        the neighbours decide (a land neighbour -> 3; else the one value they share; else 0 = ELEVATION_TRANSITION, matches any player elevation). elev_lint.py proves the result."""
        if explicit is not None:
            return explicit
        els = set()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                v = self.blocks[ny][nx]
                if (v >> COLLISION_SHIFT) & 3 == 0 and (v >> ELEVATION_SHIFT) not in (0, 15):
                    els.add(v >> ELEVATION_SHIFT)
        if not els or 3 in els:
            return 3     # reachable on foot: the usual land value (also keeps every existing event as it was)
        return next(iter(els)) if len(els) == 1 else 0

    def write_events(self, root):
        name = self.spec["map"]
        mp = os.path.join(root, "data/maps", name, "map.json")
        m = json.load(open(mp))
        m["warp_events"] = [
            # Each door leads to its interior (the building's "interior"), or back to itself until one exists.
            {"x": w["x"], "y": w["y"], "elevation": 3, "dest_map": w["interior"] or self.spec["map_const"],
             "dest_warp_id": "0" if w["interior"] else str(i)}
            for i, w in enumerate(self.warps)
        ]
        objs = []
        for o in self.spec.get("objects", []):
            # optional: "sight": n makes the NPC a trainer who spots the player n tiles away; "flag": hidden while set
            objs.append({"local_id": o["id"], "graphics_id": o["gfx"], "x": o["x"], "y": o["y"],
                         "elevation": o.get("elevation", 3),  # 1 for swimmers on surfable water
                         "movement_type": o["move"], "movement_range_x": 1, "movement_range_y": 1,
                         "trainer_type": "TRAINER_TYPE_NORMAL" if o.get("sight") else "TRAINER_TYPE_NONE",
                         "trainer_sight_or_berry_tree_id": str(o.get("sight", 0)),
                         "script": f"{name}_EventScript_{script_suffix(o['id'], self.spec['map_const'])}",
                         "flag": o.get("flag", "0")})
        for it in self.spec.get("items", []):
            objs.append({"graphics_id": "OBJ_EVENT_GFX_ITEM_BALL", "x": it["x"], "y": it["y"], "elevation": 3,
                         "movement_type": "MOVEMENT_TYPE_LOOK_AROUND", "movement_range_x": 1, "movement_range_y": 1,
                         "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": it["item"],
                         "script": "Common_EventScript_FindItem", "flag": it["flag"]})
        m["object_events"] = objs
        try:   # the approved overworld weather (weather_plan.py) survives a rebuild
            import weather_plan
            if weather_plan.header(name):
                m["weather"] = weather_plan.header(name)
        except ImportError:
            pass
        # trigger tiles: run a (hand-written) script when the player steps on them while var == value (a flag id in "var" is
        # tested as a flag: it fires while the flag equals "value"; NEVER "var": "0", that is TRIGGER_RUN_IMMEDIATELY and
        # freezes on any msgbox). "elevation" (default 3) must match the player's elevation on the cell: 4 on bridges (deck
        # cells are 15, a walker keeps 4), or 0 = any elevation. story_gates_check.py verifies both.
        m["coord_events"] = [
            {"type": "trigger", "x": t["x"], "y": t["y"], "elevation": t.get("elevation", 3), "var": t["var"], "var_value": str(t["value"]),
             "script": t["script"]}
            for t in self.spec.get("triggers", [])
        ]
        m["bg_events"] = [
            {"type": "hidden_item", "x": h["x"], "y": h["y"], "elevation": self.event_elevation(h["x"], h["y"], h.get("elevation")), "item": h["item"], "flag": h["flag"]}
            for h in self.spec.get("hidden_items", [])
        ] + [
            {"type": "sign", "x": g["x"], "y": g["y"], "elevation": self.event_elevation(g["x"], g["y"], g.get("elevation")), "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": f"{name}_EventScript_{g['id']}"}
            for g in self.spec.get("signs", [])
        ]
        with open(mp, "w", newline="\n") as f:
            json.dump(m, f, indent=2)
            f.write("\n")
        self.write_scripts(os.path.join(root, "data/maps", name, "scripts.inc"))
        include_map_scripts(root, name)
        import story  # a rebuild must never drop the hand-written story scripts: splice them back in (story.py)
        story.splice(name)

    def write_scripts(self, path):
        begin, end = "@ --- mapgen: generated NPC scripts (begin) ---", "@ --- mapgen: generated NPC scripts (end) ---"
        src = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if begin in src:
            src = src[:src.index(begin)] + src[src.index(end) + len(end):].lstrip("\n")
        name, out = self.spec["map"], [begin, ""]
        for o in self.spec.get("objects", []):
            if o.get("custom"):  # its script is written by hand, outside the generated block
                continue
            suffix = script_suffix(o["id"], self.spec["map_const"])
            label, text = f"{name}_EventScript_{suffix}", f"{name}_Text_{suffix}"
            out += [f"{label}::", f"\tmsgbox {text}, MSGBOX_NPC", "\tend", "",
                    f"{text}:", f"\t.string \"{o['text'].replace(chr(10), chr(92) + 'n')}$\"", ""]
        for g in self.spec.get("signs", []):  # the bg_events written above point at these labels
            if g.get("custom"):
                continue
            label, text = f"{name}_EventScript_{g['id']}", f"{name}_Text_{g['id']}"
            out += [f"{label}::", f"\tmsgbox {text}, MSGBOX_SIGN", "\tend", "",
                    f"{text}:", f"\t.string \"{g['text'].replace(chr(10), chr(92) + 'n')}$\"", ""]
        for sname, cells in getattr(self, "state_cells", {}).items():  # see states(): called from a map script
            out += [f"{name}_EventScript_State{sname}::"]
            out += [f"\tsetmetatile {x}, {y}, 0x{m:03X}, {'TRUE' if coll else 'FALSE'}" for x, y, m, coll in cells]
            out += ["\treturn", ""]
        out.append(end)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(src.rstrip("\n") + "\n\n" + "\n".join(out) + "\n")

    def preview(self, root, out, events=True):
        from PIL import ImageDraw
        ts = Tilesets(os.path.join(root, self.ts["primary_dir"]), os.path.join(root, self.ts["secondary_dir"]))
        im = render(ts, self.flat(), self.w)
        if events:
            d = ImageDraw.Draw(im)
            def mark(x, y, color, label):
                d.rectangle([x * 16 + 1, y * 16 + 1, x * 16 + 14, y * 16 + 14], outline=color, width=2)
                d.text((x * 16 + 4, y * 16 + 2), label, fill=color)
            for w in self.warps:
                mark(w["x"], w["y"], (255, 0, 255), "W")
            for o in self.spec.get("objects", []):
                mark(o["x"], o["y"], (0, 160, 255), "N")
            for it in self.spec.get("items", []):
                mark(it["x"], it["y"], (255, 200, 0), "i")
            for h in self.spec.get("hidden_items", []):
                mark(h["x"], h["y"], (180, 120, 40), "?")
        im.save(out)


def main(argv):
    spec, root = argv[0], os.getcwd()
    b = Builder(spec)
    b.draw()
    # what this map places, for demand-driven tilesets (compose keeps only the pieces some map uses)
    ud = os.path.join(HERE, "tilesets", "uses", b.spec["tileset"])
    os.makedirs(ud, exist_ok=True)
    with open(os.path.join(ud, b.spec["layout"] + ".json"), "w") as f:
        json.dump(sorted(USED | {f"patch:{k}" for k in b.pending_blends}), f, indent=0)
    if WANTED:
        print(f"{len(WANTED)} transition tiles needed: pieces the tileset left out ({', '.join(sorted(WANTED)[:6])}"
              f"{', ...' if len(WANTED) > 6 else ''}). Re-run compose, then build again.")
    if b.pending_blends and "--no-blends" in argv:  # first passes: keep the plain tiles, don't grow the tileset
        print(f"{len(b.pending_blends)} transition tiles left as plain tiles (--no-blends)")
    elif b.pending_blends:
        # an overlay of primary art on a primary piece (the shared bridge, tilesets/orleans_general.blends.json) belongs to the
        # primary: every secondary reaches it there, and it may stand in a seam band
        global CURRENT_TILESET
        CURRENT_TILESET = b.spec["tileset"]

        def pool(e):
            o = e.get("overlay")
            if o and primary_overlay(o) and not (o["art"].startswith("mag:") and b.spec["tileset"] == "orleans_pointe"):   # Pointe's magnolia is its own art
                return "orleans_general.blends.json"
            if e["id"].startswith("bdg_"):   # swamp border cells baked over grass: the primary's
                return "orleans_general.blends.json"
            return b.ts.get("blends_file", "blends.json")
        by_file = {}
        for k, e in sorted(b.pending_blends.items()):
            by_file.setdefault(pool(e), []).append((k, e))
        for name, items in by_file.items():
            bf = os.path.join(HERE, "tilesets", name)
            have = json.load(open(bf)) if os.path.exists(bf) else []
            known = {e["id"] for e in have}
            have += [e for k, e in items if k not in known]
            json.dump(have, open(bf, "w"), indent=1)
        print(f"{len(b.pending_blends)} transition tiles needed: added to {', '.join(by_file)}. Re-run compose, then build again.")
    if "--preview" in argv:
        b.preview(root, argv[argv.index("--preview") + 1])
    if WANTED and "--allow-missing" not in argv:
        # a piece the tileset does not have would be drawn as metatile 0 (plain grass): never write that. Compose, build again.
        lp = os.path.join(root, "data/layouts/layouts.json")   # the layout's tileset is recorded all the same (compose reads it)
        layouts = json.load(open(lp))
        for l in layouts["layouts"]:
            if l.get("id") == b.spec["layout"] and (l["primary_tileset"], l["secondary_tileset"]) != (b.ts["primary"], b.ts["secondary"]):
                l["primary_tileset"], l["secondary_tileset"] = b.ts["primary"], b.ts["secondary"]
                with open(lp, "w", newline="\n") as f:
                    json.dump(layouts, f, indent=2)
                    f.write("\n")
        print(f"MISSING PIECES: {len(WANTED)} named pieces are not in the tileset's mapping, nothing was written: "
              f"{', '.join(sorted(WANTED)[:8])}")
        sys.exit(3)
    if "--dry-run" not in argv:
        b.write_layout(root)
        b.write_events(root)
    print(f"{b.spec['map']}: {b.w}x{b.h}, {len(b.warps)} warps")


if __name__ == "__main__":
    main(sys.argv[1:])

"""River-channel levees: a grassy embankment with riprap at the waterline, only along river channels.

A river channel is narrow, elongated water (a river or canal), not a lake, pond or the sea. Land along it is
marked 'B' (levee ground) by firstpass, so nothing is planted or built there; build.py then draws the levee
pixel by pixel (render_cells) and asks compose for the pieces it needs, one metatile per distinct 16x16 cell.

The levee is drawn from distance fields, so it bends round corners on its own:
    d   distance (px) from the waterline, positive on land
    W   the levee's width there: wide where its face is seen (water to the south), narrow where it faces away
        (water to the north), clipped short of anything that isn't levee ground (a road, a building)
    s   strength: 1 along a channel, fading to 0 where the channel ends, where the levee gives way to the map's
        ordinary shore through a scatter of stones rather than a hard line
"""
import math
import os

WATER = "~I"
NARROW, LONG = 7, 14          # a channel cell: water run across it at most NARROW, along it at least LONG
RATIO = 2.5                   # ... and that much longer than it is wide
SMALLEST = 24                 # cells in a channel component
MIN_RUN = 12                  # levee ground cells in a run (shorter stubs keep their natural shore)
REACH = 2                     # levee ground: land within this many cells of channel water
# the maps whose mockups draw a river or canal through land (the coast, lakes and the boat routes' open water
# keep their natural shores; the two handmade cities have their own banks)
# (Route 7's forest stream keeps its wild banks; Route 3's canal is too short between its pond and tall grass)
MAPS = {"route_4", "storms_edge", "redfield"}
# where on a map (cells x0, y0, x1, y1); maps not listed: anywhere. Storm's Edge: the river above the town
# bridge (below it the river opens into the harbour, whose shores, like the lighthouse inlet's, stay natural)
AREAS = {"storms_edge": (21, 0, 32, 16)}  # x0 <= x < x1: storms_edge.py's river is 5 wide (x 24-28)

# one palette: the swamp grass and water the levee meets, plus its own slope, earth, stone and foam
GRASS = [(104, 144, 96), (120, 160, 104), (136, 176, 128)]
WATER_C, WATER_D = (96, 136, 136), (72, 112, 112)
SLOPE = [(96, 128, 88), (80, 112, 72), (64, 96, 64)]
EARTH, EARTH_D = (120, 96, 72), (88, 72, 56)
STONE_L, STONE, STONE_D, OUTLINE = (184, 176, 160), (144, 136, 128), (104, 100, 96), (80, 80, 80)
FOAM = (200, 224, 224)


def channel_cells(grid):
    """Water that is narrow everywhere and runs off the map: lake and sea are the water any disc wider than a
    river fits inside (so a river keeps its own width up to where it opens into them), and a pond, however
    narrow, never reaches the map's edge."""
    h, w = len(grid), len(grid[0])
    wet = lambda x, y: grid[y][x] in WATER
    # distance (Chebyshev, in cells) from each water cell to the nearest land; the map's edge counts as land,
    # so a river cut lengthwise by the edge is still a river
    INF = 10 ** 6
    dist = [[0 if not wet(x, y) else INF for x in range(w)] for y in range(h)]
    frontier = []
    for y in range(h):
        for x in range(w):
            if wet(x, y) and (x in (0, w - 1) or y in (0, h - 1)
                              or any(not wet(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1))):
                dist[y][x] = 1
                frontier.append((x, y))
    while frontier:
        nxt = []
        for x, y in frontier:
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    a, b = x + i, y + j
                    if 0 <= a < w and 0 <= b < h and dist[b][a] > dist[y][x] + 1:
                        dist[b][a] = dist[y][x] + 1
                        nxt.append((a, b))
        frontier = nxt
    half = (NARROW + 1) // 2
    wide = set()
    for y in range(h):
        for x in range(w):
            r = dist[y][x]
            if r > half and r < INF:
                for j in range(y - r + 1, y + r):
                    for i in range(x - r + 1, x + r):
                        if 0 <= i < w and 0 <= j < h:
                            wide.add((i, j))
    cand = {(x, y) for y in range(h) for x in range(w) if wet(x, y) and (x, y) not in wide}
    out, seen = set(), set()
    for c in cand:
        if c in seen:
            continue
        comp, stack = [], [c]
        seen.add(c)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in cand and n not in seen:
                    seen.add(n)
                    stack.append(n)
        edge = any(x in (0, w - 1) or y in (0, h - 1) for x, y in comp)
        if len(comp) >= SMALLEST and edge:
            out |= set(comp)
    return out


def bank_cells(grid, blocked=frozenset(), ground="."):
    """Land along channels that becomes levee ground: plain ground within REACH of channel water whose nearest
    water is the channel (not a lake it opens into), in runs long enough to read as an embankment."""
    h, w = len(grid), len(grid[0])
    chan = channel_cells(grid)
    cand = set()
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in ground or (x, y) in blocked:
                continue
            best = None
            for r in range(1, REACH + 1):
                ring = [(x + i, y + j) for i in range(-r, r + 1) for j in range(-r, r + 1)
                        if max(abs(i), abs(j)) == r and 0 <= x + i < w and 0 <= y + j < h
                        and grid[y + j][x + i] in WATER]
                if ring:
                    best = ring
                    break
            if best and sum(c in chan for c in best) * 2 > len(best):
                cand.add((x, y))
    out, seen = set(), set()
    for c in cand:
        if c in seen:
            continue
        comp, stack = [], [c]
        seen.add(c)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in cand and n not in seen:
                    seen.add(n)
                    stack.append(n)
        if len(comp) >= MIN_RUN:
            out |= set(comp)
    return out


# ---------------------------------------------------------------- drawing
def _edt(mask, reach=48):
    """Euclidean distance (px) from every pixel to the nearest True pixel of mask, capped at reach."""
    import numpy as np
    h, w = mask.shape
    big = reach + 1
    v = np.full((h, w), big, dtype=np.float32)  # vertical distance to the nearest mask pixel in the column
    run = np.full(w, big, dtype=np.float32)
    for y in range(h):
        run = np.where(mask[y], 0, np.minimum(run + 1, big))
        v[y] = run
    run = np.full(w, big, dtype=np.float32)
    for y in range(h - 1, -1, -1):
        run = np.where(mask[y], 0, np.minimum(run + 1, big))
        v[y] = np.minimum(v[y], run)
    v2 = v * v
    d2 = v2.copy()
    for dx in range(1, reach + 1):
        d2[:, dx:] = np.minimum(d2[:, dx:], v2[:, :-dx] + dx * dx)
        d2[:, :-dx] = np.minimum(d2[:, :-dx], v2[:, dx:] + dx * dx)
    return np.sqrt(d2)


def _blur(a, r):
    """Box blur of radius r, twice (close to a gaussian), edges clamped."""
    import numpy as np
    for _ in range(2):
        for axis in (0, 1):
            p = np.pad(a, [(r + 1, r) if ax == axis else (0, 0) for ax in (0, 1)], mode="edge")
            c = np.cumsum(p, axis=axis, dtype=np.float64)
            n = a.shape[axis]
            hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
            lo = np.take(c, np.arange(0, n), axis=axis)
            a = ((hi - lo) / (2 * r + 1)).astype(np.float32)
    return a


def _hash(x, y, k=0):
    """Repeatable noise in [0, 1) that repeats every 16 px, so straight runs of levee repeat cell for cell."""
    n = ((x % 16) * 374761393 + (y % 16) * 668265263 + k * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


# riprap: rounded stones laid out on a 16 px torus (x, y, radius)
STONES = [(2.5, 3.0, 3.2), (9.0, 2.0, 3.6), (14.5, 6.5, 3.0), (5.5, 9.0, 3.4), (11.5, 11.0, 3.3), (1.0, 14.0, 2.8),
          (8.0, 15.5, 2.6)]


PHASE = (0, 0)  # px the riprap stones are shifted on the map (a spec may set "levee_phase"; default none)


def _stone(x, y, keep=None):
    """(inside, shade) for the riprap at pixel x, y: shade -1 lit edge, 0 face, 1 shadow, 2 outline.
    keep(cx, cy, r) decides whether the stone centred at map pixel (cx, cy) is laid at all (whole stones only:
    none cut off where the levee's cells stop, fewer toward the end of a run)."""
    best = None
    for sx, sy, r in STONES:
        dx = (x - sx - PHASE[0] + 8) % 16 - 8
        dy = (y - sy - PHASE[1] + 8) % 16 - 8
        dd = math.hypot(dx, dy * 1.2) - r
        if best is None or dd < best[0]:
            best = (dd, dx, dy, r)
    dd, dx, dy, r = best
    if dd > 0.6:
        return False, None
    if keep is not None and not keep(round(x - dx), round(y - dy), r):
        return False, None
    if dd > -0.4:
        return True, 2
    u = dx + dy
    return True, (-1 if u < -1.5 else 1 if u > 1.8 else 0)


CAPS = False   # set per map by borders.prepare (LEVEE_CAP_MAPS): where a levee run ends in open water its head gets the rounded jetty nose (make_levee_caps.render_caps)


def render(grid, bank, base, blocked=frozenset()):
    """{(x, y): 16x16 RGBA overlay} for every cell the levee changes (clear where the ground shows through).
    base(x, y) gives the cell as drawn without it. bank is the levee ground (the 'B' cells); the water cells
    beside it get the riprap. blocked: bridge and dock footprints, where a run ends."""
    if CAPS:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources", "orleans_custom"))
        import make_levee_caps
        return make_levee_caps.render_caps(grid, bank, base, blocked)
    import numpy as np
    from PIL import Image
    h, w = len(grid), len(grid[0])
    wet_cell = lambda x, y: grid[y][x] in WATER
    region = set(bank)
    for x, y in bank:
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if 0 <= x + i < w and 0 <= y + j < h and wet_cell(x + i, y + j):
                    region.add((x + i, y + j))
    if not region:
        return {}
    # work in a window round the region (with a margin for the distance fields)
    x0 = max(0, min(x for x, _ in region) - 4)
    y0 = max(0, min(y for _, y in region) - 4)
    x1 = min(w, max(x for x, _ in region) + 5)
    y1 = min(h, max(y for _, y in region) + 5)
    W, H = (x1 - x0) * 16, (y1 - y0) * 16
    cell_mask = lambda pred: np.kron(np.array([[1.0 if pred(x, y) else 0.0 for x in range(x0, x1)]
                                               for y in range(y0, y1)], dtype=np.float32),
                                     np.ones((16, 16), dtype=np.float32))
    water = _blur(cell_mask(wet_cell), 3) > 0.5          # the cells' water, its corners rounded
    d_land = _edt(water)                                    # land pixels: distance to the water
    d_water = _edt(~water)                                  # water pixels: distance to the land
    d = np.where(water, -d_water, d_land)
    # which way the bank faces: the gradient of d points from the water up onto the land
    ds = _blur(d, 4)
    gy, gx = np.gradient(ds)
    norm = np.hypot(gx, gy) + 1e-6
    ny = gy / norm
    vis = np.clip((-ny + 1) / 2, 0, 1)                      # 1: water to the south, its face toward us
    # the levee's width on the map: its whole face where it faces us, the face seen side-on to the east and
    # west, only the crest and the stones where it faces away (water to the north)
    # one width all round (the face seen at any angle): a width that changed with the facing made the corners
    # that jut into the river and the ones that step back from it come out in different styles
    width = np.full(d.shape, float(WIDTH), dtype=np.float32)
    # the meadow (or road) behind the levee is level with its crest: its face only has to fit the levee ground
    # in front of it. Where a run ends - the ordinary shore beyond it, a bridge or dock - it comes down in a
    # short ramp with its crest rounded off.
    def near(x, y, pred):
        return any(0 <= x + i < w and 0 <= y + j < h and pred(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1))

    def shore(x, y):  # ordinary shore just past the end of a run (square cells, so every end of a kind matches)
        return (not wet_cell(x, y) and (x, y) not in bank and near(x, y, wet_cell)
                and near(x, y, lambda i, j: (i, j) in bank))
    ends = cell_mask(lambda x, y: shore(x, y) or (x, y) in blocked) > 0.5
    # behind the levee: land that isn't levee ground, except just past a run's end (the taper sees to that;
    # counting it would pull the crest round the end in a hard line)
    ends_at = {(x, y) for x in range(x0, x1) for y in range(y0, y1) if shore(x, y) or (x, y) in blocked}
    back = _blur(cell_mask(lambda x, y: not wet_cell(x, y) and (x, y) not in bank and not near(
        x, y, lambda i, j: (i, j) in ends_at)), 3) > 0.5
    avail = _blur(d + _edt(back), 6)  # water to the meadow behind, measured across the levee
    width = np.minimum(width, np.maximum(8, avail - 2))
    width = np.round(width / 4) * 4  # in steps, so a straight run draws the same cell over and over
    e = _edt(ends)
    # toward the end of a run the face narrows until the crest meets the water
    taper = np.clip((e - 2) / (END - 2), 0, 1)
    width = TOE + (width - TOE) * taper ** 0.8
    # the crest band is a fixed 4 px across the slope however fast the width changes along it
    fy, fx = np.gradient(width - d)
    steep = np.maximum(np.hypot(fx, fy), 0.25)
    inner = _edt(cell_mask(lambda x, y: (x, y) not in region) > 0.5)  # room left inside the drawn cells

    def keep(sx, sy, r):
        X, Y = sx - x0 * 16, sy - y0 * 16
        if not (0 <= X < W and 0 <= Y < H) or inner[Y, X] <= r + 1.5:
            return False
        if float(e[Y, X]) <= END and not -TOE + r * 0.6 <= float(d[Y, X]) <= TOE:
            return False  # where a run tapers away, whole stones only: none sliced by the band's edge
        ev = float(e[Y, X])
        if ev > END:
            return True
        taper = max(0.0, (ev - 2) / (END - 2))
        return _hash(sx, sy, 13) < taper * 1.3 - 0.15

    out = {}
    for cx, cy in sorted(region):
        bp = base(cx, cy).convert("RGB").load()
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))  # the levee alone: clear where the ground shows
        px = im.load()
        changed = False
        for yy in range(16):
            for xx in range(16):
                X, Y = (cx - x0) * 16 + xx, (cy - y0) * 16 + yy
                gxp, gyp = cx * 16 + xx, cy * 16 + yy   # map pixel: textures repeat on the map's 16 px grid
                dv, ev = float(d[Y, X]), float(e[Y, X])
                if dv < -9 or ev < 0.5:
                    continue
                c = _levee_px(gxp, gyp, dv, float(width[Y, X]), float(vis[Y, X]), ev, keep, float(steep[Y, X]))
                if c is None:
                    continue
                px[xx, yy] = c + (255,)
                changed |= c != bp[xx, yy]
        if changed:
            out[(cx, cy)] = im
    return out


END = 20.0  # px over which the levee tapers away at the end of a run
WIDTH = 28  # px from the waterline to the crest (inside two cells of levee ground)
TOE = 6.0   # px the riprap reaches either side of the waterline


def _levee_px(x, y, d, width, vis, e, keep=None, steep=1.0):
    """The colour of one pixel of levee at distance d (px, + on land) from the waterline and e from the end of
    its run, or None to keep what's there; width is already narrowed toward the run's ends, where the stones
    thin out too, so the levee sinks into the map's ordinary shore, which shows through."""
    full = e > END
    toe_r = TOE
    inside, shade = _stone(x, y, keep)
    if d < 0:  # in the water: stones tumbled in at the toe, foam round them, a shadow under the bank
        if d > -toe_r + 0.5 and inside:
            return OUTLINE if shade == 2 else STONE_D if shade == 1 else STONE
        if not full:
            return None
        if d > -toe_r - 1.5:
            near = not inside and (_stone(x + 1, y, keep)[0] or _stone(x - 1, y, keep)[0]
                                   or _stone(x, y - 1, keep)[0])
            if near and _hash((x % 16) // 2, (y % 16) // 2, 3) < 0.22:
                return FOAM
        if d > -2:
            return WATER_D
        return WATER_C if d > -6 else None
    if d < toe_r:  # riprap above the waterline, wet earth between the stones
        if inside:
            return OUTLINE if shade == 2 else {-1: STONE_L, 0: STONE, 1: STONE_D}[shade]
        return EARTH_D if width > toe_r + 4 and e > 0.45 * END else None
    if d >= width:
        return None                              # the crest's top: plain meadow
    # the earth, crest and slope textures repeat every 8 px, so along a straight run the top and bottom halves
    # of a cell are the same tile (half the tiles)
    x8, y8 = x % 8, y % 8
    toe = toe_r + max(2.0, 0.1 * width)
    if d < toe:  # the earth band at the toe of the slope
        return EARTH_D if _hash(x8, y8, 5) < 0.3 else EARTH
    rim = width - (3 if width > 16 else 2) * steep
    if d >= rim:  # the crest: the meadow's own grass, lit along the brow in a broken line
        if d >= width - steep and _hash(x8, y8, 9) < 0.7:
            return GRASS[2]
        return GRASS[max(1, _grass_index(x, y))] if _hash(x8, y8, 19) < 0.6 else SLOPE[0]
    # the slope face: darker as it falls, with blades of grass down the fall line
    k = (d - toe) / max(1.0, rim - toe)
    band = 2 if k < 0.3 else 1 if k < 0.65 else 0
    # blades: short strokes down the fall line, staggered so they don't line up in rows
    if vis > 0.7:
        blade = (x8 == 2 and y8 in (1, 2, 3)) or (x8 == 6 and y8 in (5, 6, 7)) or (x8 == 4 and y8 == 0)
    elif vis > 0.25:  # seen side-on: the fall line runs across the map
        blade = (y8 == 2 and x8 in (1, 2, 3)) or (y8 == 6 and x8 in (5, 6, 7)) or (y8 == 4 and x8 == 0)
    else:
        blade = False
    if blade:
        band = max(0, band - 1)
    elif _hash(x8, y8, 11) < 0.1:
        band = min(2, band + 1)
    return SLOPE[band]


_GRASS_TILE = None


def _grass_index(x, y):
    """The swamp grass tile's own pixel at this spot (so the crest runs seamlessly into the meadow)."""
    global _GRASS_TILE
    if _GRASS_TILE is None:
        import os
        from PIL import Image
        here = os.path.dirname(os.path.abspath(__file__))
        im = Image.open(os.path.join(here, "sources", "ekat_swamp", "swamp_tiles.png")).convert("RGB")
        cell = im.crop((0, 0, 16, 16)).load()  # ekat:grass is the sheet's cell (0, 0)
        _GRASS_TILE = [[min(range(3), key=lambda i: sum((a - b) ** 2 for a, b in zip(cell[i_x, i_y], GRASS[i])))
                        for i_x in range(16)] for i_y in range(16)]
    return _GRASS_TILE[y % 16][x % 16]


REACH_FOR = {}   # per map: levee ground this many cells from the channel water (default REACH); Storm's Edge: tile budget (the lake-end heads are all distinct cells)


def mark(grid, blocked=frozenset(), key=None):
    global REACH
    keep_reach = REACH
    REACH = REACH_FOR.get(key, REACH)
    try:
        cells = bank_cells(grid, blocked)
    finally:
        REACH = keep_reach
    if key in AREAS:
        x0, y0, x1, y1 = AREAS[key]
        cells = {(x, y) for x, y in cells if x0 <= x < x1 and y0 <= y < y1}
    g = [list(r) for r in grid]
    for x, y in cells:
        g[y][x] = "B"
    return ["".join(r) for r in g]


if __name__ == "__main__":  # survey: which maps have channels, and how much levee ground they'd get
    import glob
    import json
    import os
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(glob.glob(os.path.join(here, "maps", "*.json"))):
        if f.endswith(".detected.json") or os.path.basename(f).startswith(("00_", "_")):
            continue
        spec = json.load(open(f, encoding="utf-8"))
        if "grid" not in spec:
            continue
        grid = [l.rstrip("\n") for l in open(os.path.join(here, "maps", spec["grid"]), encoding="utf-8") if l.strip()]
        print(f"{os.path.basename(f)[:-5]:16} channel {len(channel_cells(grid)):4}  levee ground {len(bank_cells(grid)):4}")

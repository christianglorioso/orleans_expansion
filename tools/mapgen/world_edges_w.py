"""Agent W's edge edits (world phase 2): the boat joins.  `python tools/mapgen/world_edges_w.py [key ...]` rewrites each
map's entry in world_edges.json (from the generated grid, so it is re-runnable) and patches its spec; then build + check.
Order matters where a map's edge is another's reference (a reference edge is read from the effective grid)."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0].rsplit("\\", 1)[0])
import wedge


def route_7():
    g = wedge.Grid("route_7")
    # both channels are 4 grid rows wide at the edge (3 open cells): E: row 10 joins the channel, W: row 10 too
    g.rect(47, 10, 3, 1, "~")
    g.rect(0, 10, 4, 1, "~")
    wedge.rim(g)
    return g


def route_6():
    g = wedge.Grid("route_6")
    # W edge meets Route 7's E edge (offset 0): Route 7's marsh banks run on into the basin, its channel opens out
    p = wedge.prof_of("route_7", "E")
    wedge.pour(g, "W", p, 0, 26, base=6, spread=2, seed=6)
    # E edge meets Crescent's W edge (Route 6 row = Crescent row + 12): the canal (Crescent rows 0-2 = rows 12-14) runs on
    # straight into the basin, its south bank (Crescent's levee row 3 = row 15) carried on as a straight shore for a while,
    # then falling away south-west into the basin's own south shore
    for y, d in zip(range(16, 26), (16, 14, 12, 10, 9, 8, 8, 8, 8, 8)):
        g.rect(g.w - d, y, d, 1, ".")
    g.rect(g.w - 8, 12, 8, 4, "~")  # 4 rows (Crescent's canal is 4 rows wide for its first 6 cells: 3 open cells across the seam)
    g.rect(20, 22, 30, 4, ".")  # the south shore from the pond east is ground (no marsh/ground/water triple under the new shore)
    g.grove(23, 23, 9, 3, [("cypress_small_marsh", 25, 23), ("cypress_small_marsh", 29, 23)])
    wedge.rim(g)
    return g


def route_8():
    g = wedge.Grid("route_8")
    # E edge meets Route 7's W edge (Route 8 row = Route 7 row + 3)
    p = wedge.prof_of("route_7", "W")
    wedge.pour(g, "E", p, 3, 29, base=6, spread=2, seed=8, offset=3)
    route_8_north(g)
    wedge.rim(g)
    return g


def route_9():
    g = wedge.Grid("route_9")
    # W edge meets Camp Cocodrie's E edge (Camp row = Route 9 row + 4): marsh, the ground under the landing, the lagoon
    p = wedge.prof_of("camp_cocodrie", "E")
    wedge.pour(g, "W", p, 0, 26, base=6, spread=2, seed=9, offset=-4, wet=True, only='."~')
    # first-pass leftovers inside Route 9 that check.py flags (the dead-end spur south of the boardwalk, two loose path cells
    # beside the landing shack)
    g.rect(24, 14, 3, 6, ".")
    g.set(30, 13, ".")
    g.set(34, 13, ".")
    g.rect(34, 14, 1, 2, ".")
    # the shore beside the shack is ground the whole way up to the map's top (a 2-wide ground bank between marsh and water):
    # marsh, ground and water then never meet in a blend tile there
    for y in range(0, 9):
        xw = next(x for x in range(20, g.w) if g.at(x, y) == "~")
        g.rect(xw - 2, y, 2, 1, ".")
    wedge.rim(g)
    return g


def route_25():
    g = wedge.Grid("route_25")
    # S end: the lake narrows into an 8-wide channel (cols 10-17, the mockup's arrow at col 14) between marsh banks, so Route 8's
    # north shore has a real channel to meet (decision 5)
    for y in range(36, 46):
        w = max(8, 20 - 2 * (y - 36))
        x0 = 14 - w // 2
        g.rect(4, y, x0 - 4, 1, '"')
        g.rect(x0 + w, y, 26 - (x0 + w), 1, '"')
    g.rect(x0, 45, 8, 1, "~")
    g.add.append({"prefab": "cypress_small_marsh", "x": 3, "y": 40, "label": "Tree"})
    g.add.append({"prefab": "cypress_small_marsh", "x": 22, "y": 40, "label": "Tree"})
    # N end: the lone ground cells at the corners become marsh (the Shrine's south pour matches marsh)
    for x in (0, 29):
        g.rect(x, 0, 1, 2, '"')
    wedge.rim(g)
    return g


def route_8_north(g):
    # N edge meets Route 25's S edge (Route 8 col = Route 25 col + 9): Route 25's channel (cols 10-17) = cols 19-26 runs through
    # Route 8's north shore; the shore (rows 0-1) is marsh the whole way, so the banks continue Route 25's marsh
    g.rect(0, 0, g.w, 2, '"')
    g.rect(19, 0, 8, 2, "~")


def oldest_shrine():
    g = wedge.Grid("oldest_shrine")
    # S edge meets Route 25's N edge (Shrine col = Route 25 col + 3): Route 25's marsh banks run on south of the island
    p = wedge.prof_of("route_25", "N")
    wedge.pour(g, "S", p, 3, 33, base=5, spread=1, seed=14, offset=3, only="~")
    # check.py's seams in the courtyard (first-pass leftovers: a marsh patch's border cells must not touch paving or the path):
    # the stone's marsh gets a 2-cell grass moat inside a paving ring (a third paving row on the north side keeps it 2 deep)
    g.rect(13, 8, 10, 1, "=")
    g.rect(15, 10, 6, 5, ".")
    g.rect(17, 12, 3, 2, '"')
    # the south-east marsh keeps off the stem path
    g.rect(19, 17, 4, 1, ".")
    g.rect(19, 18, 2, 4, ".")
    g.rect(17, 21, 2, 1, ".")      # the landing path stops a cell short of the water (a path cell can't sit on the shore row)
    wedge.rim(g)
    return g


def route_18():
    g = wedge.Grid("route_18")
    # W edge meets Redfield's E edge (Redfield row = Route 18 row + 9): the river, all water, runs on west
    g.rect(0, 4, 10, 5, "~")  # the mud bar's west half goes (its tip is cut by the edge pour otherwise)
    wedge.pour(g, "W", {i: "~" for i in range(26)}, 0, 26, base=6, spread=2, seed=18, wet=True)
    # E edge meets Route 19's W edge (Route 19 row = Route 18 row - 1): the oyster flats run on west, the channel (Route 19
    # rows 10-13 = rows 11-14) cuts through them
    p = wedge.prof_of("route_19", "W")
    wedge.pour(g, "E", p, 1, 26, base=6, spread=2, seed=19, offset=1)
    wedge.moat(g, "L", '"')
    return g


def route_20():
    g = wedge.Grid("route_20")
    # W edge meets Route 19's E edge (Route 19 row = Route 20 row + 1): the oyster flats run on east, the channel cuts through
    p = wedge.prof_of("route_19", "E")
    wedge.pour(g, "W", p, 0, 25, base=6, spread=2, seed=20, offset=-1)
    # E edge meets Land's End's W edge (Land's End row = Route 20 row + 3): the north marsh, open water, then Land's End's
    # western mud flat that carries the main walk out to the edge (the walk itself is Land's End's own planks)
    p = wedge.prof_of("lands_end", "W")
    wedge.pour(g, "E", p, 0, 26, base=6, spread=2, seed=21, offset=-3)
    wedge.moat(g, "L", '"')
    wedge.keep_off(g, ".", "L", 2)   # the two islands keep clear of the new flats (no mud/ground/water blend tiles)
    g.exits.append({"name": "Land's End boardwalk (east): the flat runs on to its walk", "cells": [[49, 12], [49, 13]]})
    wedge.rim(g)
    return g


def route_19():
    g = wedge.Grid("route_19")
    # first-pass leftovers in the oyster-shed road that check.py flags: the west shed stands a row higher (the road
    # under it was 1 deep) and the stub above the road's west end goes
    g.move(16, 5, 16, 4)           # the west shed up a row, so the road under it is 2 deep (rows 8-9)
    g.rect(16, 8, 3, 1, ":")
    g.rect(11, 7, 2, 1, ".")
    return g


def route_10():
    g = wedge.Grid("route_10")
    # the lakefront promenade (W edge): first-pass leftovers (stray path bits, a path on the shore row) re-laid as one clean
    # system: grass shore row 16 under the docks' feet, an upper walk (rows 17-18, x 0-11), the promenade (x 0-1, rows 17-24,
    # meeting Crescent's lakefront landing across the seam: Route 10 rows 19-22 = Crescent rows 17-20) and a lower walk
    # (rows 23-24) under both boathouses' doors
    g.rect(0, 14, 13, 1, "~")
    g.rect(0, 15, 13, 2, ".")        # the shore row matches Crescent's (its water ends at row 12 = Route 10 row 14)
    g.rect(0, 17, 12, 2, ":")
    g.rect(2, 19, 11, 6, ".")
    g.rect(0, 19, 2, 6, ":")
    g.rect(0, 23, 10, 2, ":")
    g.move(2, 17, 2, 19)
    g.move(6, 18, 6, 19)
    return g


JOBS = {"route_10": route_10, "route_19": route_19, "route_20": route_20, "route_18": route_18, "route_25": route_25, "oldest_shrine": oldest_shrine, "route_9": route_9, "route_7": route_7, "route_6": route_6, "route_8": route_8}

if __name__ == "__main__":
    for k in (sys.argv[1:] or JOBS):
        g = JOBS[k]()
        print(k, "dropped", g.auto_drop())
        g.save()

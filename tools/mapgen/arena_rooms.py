"""The two legendary arenas that are interiors: the Drowned Temple (Kyogre) and the Salt Cathedral (Groudon).

Their layouts are the approved mocks (tilesets/arenas/arena_mocks.py: temple_mock / cathedral_mock), cell for cell: the metatile names of
each cell and the walkable mask. build_interior.py turns them into map.bin (blocking cells get collision 1), writes the exit warp on the
art's exit cell, and appends the map-state scripts below to the room's generated script block.

States (the same idea as build.py's spec "states" for outdoor maps, here for an interior): the Drowned Temple's sealed door is drawn closed in
map.bin; LandsEnd_DrownedTemple_EventScript_StateDoorOpen (generated) setmetatile's the open door over it, and the story script calls it
when the verse is sung and from the room's ON_LOAD once FLAG_TEMPLE_DOOR_OPEN is set. The lintel over the open cell is a top layer.

Nothing here imports build.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARENAS = os.path.join(HERE, "tilesets", "arenas")
for p in (HERE, ARENAS):
    if p not in sys.path:
        sys.path.insert(0, p)

ARENAS_BY_NAME = {
    "temple": dict(tileset="orleans_temple", secondary="gTileset_OrleansTemple", prefix="dt", border="dt:void"),
    "cathedral": dict(tileset="orleans_saltdome", secondary="gTileset_OrleansSaltdome", prefix="sc", border="sc:void"),
    # Articuno's frozen hall: the Pointe Rouge ice plant redone from the lair art (tilesets/lairs/lair_mocks.py articuno()); the room's black border as every interior's
    "iceplant": dict(tileset="orleans_iceplant", secondary="gTileset_OrleansIcePlant", prefix="ip", border="jb:008"),
}
# the cell the art marks as the exit (walking south onto it leaves: MB_SOUTH_ARROW_WARP in the piece)
EXITS = {"temple": [(9, 19)], "cathedral": [(11, 21)], "iceplant": [(9, 13)]}
# where the arrival lands (one step in from the exit) and where the legendary stands / the player faces it from
ARRIVAL = {"temple": (9, 18), "cathedral": (11, 20), "iceplant": (9, 12)}
LEGENDARY = {"temple": (9, 5), "cathedral": (11, 4), "iceplant": (9, 5)}
SING_CELL = (9, 11)       # the temple: the player sings here, facing the door cell (9, 10)
DOOR_CELL = (9, 10)


def mock(arena, state=None):
    if arena == "iceplant":      # the lair art's mock (lairs.py shares its loader), not an arena mock
        import lairs
        return lairs.iceplant_mock()
    import arena_mocks
    if arena == "temple":
        return arena_mocks.temple_mock(state or "closed")
    return arena_mocks.cathedral_mock()


def layout(arena):
    """(names, walk): names[y][x] = metatile name (dt:... / sc:...), walk[y][x] = bool"""
    m = mock(arena)
    return m.grid, m.walk


def states(arena):
    """{state name: [(x, y, metatile name, walkable)]}: the cells that differ from the default drawing"""
    if arena != "temple":
        return {}
    a, b = mock("temple"), mock("temple", "open")
    cells = [(x, y, b.grid[y][x], b.walk[y][x]) for y in range(a.h) for x in range(a.w)
             if (a.grid[y][x], a.walk[y][x]) != (b.grid[y][x], b.walk[y][x])]
    return {"DoorOpen": cells}


def state_scripts(name, arena, mapping):
    """the generated script lines for the room's states (mapping: piece name -> metatile id)"""
    out = []
    for sname, cells in states(arena).items():
        out.append(f"{name}_EventScript_State{sname}::\n"
                   + "".join(f"\tsetmetatile {x}, {y}, 0x{mapping[n]:03X}, {'FALSE' if walk else 'TRUE'}\n" for x, y, n, walk in cells)
                   + "\treturn\n")
    return out

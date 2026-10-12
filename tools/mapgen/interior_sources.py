"""Which reference layouts (from the soulgold project) each interior is built from, and the interior
tileset recipes generated from the metatiles those layouts actually use.

usage (from the decomp root): python tools/mapgen/interior_sources.py
writes tools/mapgen/tilesets/recipes/orleans_{building,home,hall,services}.json
"""
import json
import os
import struct

SG = "C:/Users/chris/soulgold"
PRIMARY_METATILES = 1024  # soulgold: 11-bit metatile ids, 1024 in the primary

# primaries other than the Johto building: their metatiles go into one of our secondaries
# (soulgold symbol -> (prefix, data dir, our secondary))
OTHER_PRIMARIES = {
    "gTileset_Building": ("eb", "building", "briney"),
}
# secondary tileset (soulgold symbol) -> (prefix used in our mapping names, data dir, our secondary[, primary dir])
SECONDARIES = {
    "gTileset_GenericBuilding": ("gb", "generic_building", "briney", "building"),
    "gTileset_House_Lab": ("hl", "house_lab", "home"),
    "gTileset_PlayersHouse": ("ph", "players_house", "home"),
    "gTileset_PokemonDayCare": ("dc", "pokemon_day_care", "home"),
    "gTileset_EcruteakTheater": ("th", "ecruteak_theater", "hall"),
    "gTileset_SoulHouse": ("sh", "soul_house", "hall"),
    "gTileset_Kanto_PokemonCenter": ("pc", "kanto_pokemon_center", "services"),
    "gTileset_JohtoMart": ("mt", "johto_mart", "services"),
}
OURS = {
    "home": ("gTileset_OrleansHome", "orleans_home", "House interiors (HnS house, player's house, flower shop), from the soulgold project."),
    "hall": ("gTileset_OrleansHall", "orleans_hall", "Dance hall and church (HnS Ecruteak theater, Soul House), from the soulgold project."),
    "services": ("gTileset_OrleansServices", "orleans_services", "Pokemon Center and Mart (HnS), from the soulgold project."),
}

# pieces borrowed from other rooms, drawn over this tileset's own floor (patch: lower = our floor,
# upper = the borrowed piece)
sys_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources", "orleans_custom")
import sys as _sys  # noqa: E402
_sys.path.insert(0, sys_path)
import make_interior_art as _art  # noqa: E402

_SP = _art.cell_index(_art.SHELTER)
_ON_WALL = {"accordion": "th:44E"}
_COUNTERS = {n for n in _SP if n.startswith("ct_")}
EXTRAS = {
    "hall": {
        # own art drawn over the hall's floor: camp cots, folding-table counters, the field kit, the accordion
        "images": [{"name": "sp", "type": "image", "image": "tools/mapgen/sources/orleans_custom/shelter.png",
                    "transparent": [[255, 0, 255]], "metatiles": [{"id": n, "bottom": c} for n, c in _SP.items()]},
                   {"name": "cw", "type": "image", "image": "tools/mapgen/sources/orleans_custom/church.png",
                    "transparent": [[255, 0, 255]],
                    "metatiles": [dict({"id": n, "bottom": c}, **({"behavior": "MB_SOUTH_ARROW_WARP"} if n.startswith("mat_") else {}))
                                  for n, c in _art.cell_index(_art.CHURCH).items()]}],
        "patches": [dict({"id": n, "overlay": dict({"base": _ON_WALL.get(n, "th:459"), "art": f"sp:{n}"},
                                                    **({"behavior": "MB_COUNTER"} if n in _COUNTERS else {}))})
                    for n in _SP],
    },
}

# rooms taken from vanilla pokeemerald files (tools/mapgen/sources/pret_emerald): Emerald block format,
# every metatile in the room's secondary
PRET = "tools/mapgen/sources/pret_emerald/data"
PRET_ROOMS = {
    "IsleMarais_HouseEastmost": {"layout": "Route104_MrBrineysHouse", "map": "Route104_MrBrineysHouse",
                                 "secondary": "generic_building", "ours": "briney", "prefix": "gb"},
}
OURS["briney"] = ("gTileset_OrleansBriney", "orleans_briney",
                  "Mr. Briney's house (vanilla Emerald generic building, from pret/pokeemerald).")


def pret_blocks(room):
    raw = open(f"{PRET}/layouts/{PRET_ROOMS[room]['layout']}/map.bin", "rb").read()
    return struct.unpack(f"<{len(raw) // 2}H", raw)


# building-primary pieces only the generic interior style uses (interior_rooms_world.py): the plain rug centre
EXTRA_PRIMARY = {0x0CC}

# room -> reference layout
REFERENCES = {
    "_theater_tiles": "LAYOUT_ECRUTEAK_CITY_THEATER",  # walls, floors and dance floor for the shelter
    "_players_house_1f": "LAYOUT_NEW_BARK_TOWN_PLAYERS_HOUSE_1F",  # kit pieces for the player's house
    "IsleMarais_PlayersHouse_2F": "LAYOUT_NEW_BARK_TOWN_PLAYERS_HOUSE_2F",
    "IsleMarais_HouseW": "LAYOUT_GOLDENROD_CITY_BILLS_HOUSE",
    "IsleMarais_HouseE": "LAYOUT_LAVENDER_TOWN_HOUSE1",
    "GrandOak_PokemonCenter": "LAYOUT_CHERRYGROVE_CITY_POKEMON_CENTER",
    "GrandOak_Mart": "LAYOUT_CHERRYGROVE_CITY_MART",
    "GrandOak_Nursery": "LAYOUT_GOLDENROD_CITY_FLOWER_SHOP",
    "GrandOak_HouseSW1": "LAYOUT_CHERRYGROVE_CITY_HOUSE1",
    "GrandOak_HouseSW2": "LAYOUT_VIOLET_CITY_HOUSE2",
    "GrandOak_HouseSE": "LAYOUT_ECRUTEAK_CITY_HOUSE1",
}


def layouts():
    return {l["id"]: l for l in json.load(open(f"{SG}/data/layouts/layouts.json"))["layouts"] if "id" in l}


def blocks(layout):
    raw = open(f"{SG}/{layout['blockdata_filepath']}", "rb").read()
    return struct.unpack(f"<{len(raw) // 2}H", raw)


# rooms soulgold never converted: their map.bin is still in Emerald's block format (10-bit metatile id,
# secondary from 512, collision in bits 10-11)
EMERALD_FORMAT = {"LAYOUT_ROUTE104_MR_BRINEYS_HOUSE"}


def decode(b, lid):
    """A map block -> (metatile id in soulgold numbering, collision 0/1, elevation)."""
    if lid in EMERALD_FORMAT:
        mid = b & 0x3FF
        return (mid if mid < 0x200 else mid - 0x200 + PRIMARY_METATILES), 1 if (b >> 10) & 3 else 0, b >> 12
    return b & 0x7FF, (b >> 11) & 1, b >> 12


def name_of(mid, secondary, primary="gTileset_Johto_Building"):
    """Our mapping name for a soulgold metatile id in a layout using `primary` + `secondary`."""
    if mid < PRIMARY_METATILES:
        return f"{OTHER_PRIMARIES[primary][0] if primary in OTHER_PRIMARIES else 'jb'}:{mid:03X}"
    return f"{SECONDARIES[secondary][0]}:{mid:03X}"  # compose names picks by their absolute id


def main():
    L = layouts()
    prim, sec, others = set(), {}, {}
    for room, lid in REFERENCES.items():
        lay = L[lid]
        p_ = lay["primary_tileset"]
        assert p_ == "gTileset_Johto_Building" or p_ in OTHER_PRIMARIES, lid
        s = lay["secondary_tileset"]
        for b in blocks(lay):
            mid, _, _ = decode(b, lid)
            if mid < PRIMARY_METATILES:
                if p_ in OTHER_PRIMARIES:
                    others.setdefault(p_, (s, set()))[1].add(mid)
                else:
                    prim.add(mid)
            else:
                sec.setdefault(s, set()).add(mid - PRIMARY_METATILES)
    prim |= EXTRA_PRIMARY
    R = "tools/mapgen/tilesets/recipes/"
    json.dump({
        "_comment": "Orleans interior primary: the HnS Johto building metatiles our interiors use, from the soulgold project.",
        "kind": "primary", "dir": "orleans_building", "symbol": "gTileset_OrleansBuilding",
        "sources": [{"name": "jb", "primary": f"{SG}/data/tilesets/primary/johto_building",
                     "secondary": f"{SG}/data/tilesets/secondary/house_lab", "layout": "sg", "layers": 3, "primary_layers": 3,
                     "ids": [f"{m:03X}" for m in sorted(prim)]}],
    }, open(R + "orleans_building.json", "w"), indent=2)
    for key, (sym, d, comment) in OURS.items():
        sources = []
        for p_, (s, ids) in sorted(others.items()):
            prefix, pdir, ours = OTHER_PRIMARIES[p_]
            if ours == key:
                sources.append({"name": prefix, "primary": f"{SG}/data/tilesets/primary/{pdir}",
                                "secondary": f"{SG}/data/tilesets/secondary/{SECONDARIES[s][1]}", "layout": "sg",
                                "layers": 3, "primary_layers": 3, "ids": [f"{m:03X}" for m in sorted(ids)]})
        for s, ids in sorted(sec.items()):
            prefix, sdir, ours = SECONDARIES[s][:3]
            pdir = SECONDARIES[s][3] if len(SECONDARIES[s]) > 3 else "johto_building"
            if ours != key:
                continue
            sources.append({"name": prefix, "primary": f"{SG}/data/tilesets/primary/{pdir}",
                            "secondary": f"{SG}/data/tilesets/secondary/{sdir}", "layout": "sg", "layers": 3, "primary_layers": 3,
                            "ids": [f"{PRIMARY_METATILES + m:03X}" for m in sorted(ids)]})
        for room, pr in PRET_ROOMS.items():
            if pr["ours"] == key:
                ids = sorted({b & 0x3FF for b in pret_blocks(room)})
                sources.append({"name": pr["prefix"], "primary": f"{PRET}/tilesets/primary/building",
                                "secondary": f"{PRET}/tilesets/secondary/{pr['secondary']}", "ids": [f"{m:03X}" for m in ids]})
        extra = EXTRAS.get(key, {})
        sources += extra.get("images", [])
        json.dump({"_comment": comment, "kind": "secondary", "dir": d, "symbol": sym,
                   "primary_mapping": "orleans_building.mapping.json", "sources": sources,
                   "patches": extra.get("patches", [])},
                  open(R + d + ".json", "w"), indent=2)
    print("primary metatiles used:", len(prim), {s: len(v) for s, v in sec.items()})


if __name__ == "__main__":
    main()

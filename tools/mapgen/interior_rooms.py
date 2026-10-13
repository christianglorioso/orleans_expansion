"""Every interior room: where it is, what it's built from, and who is inside. Used by build_interior.py.

people: (kind, text). kind "nurse" heals, "clerk" runs the shop in "mart"; anything else just talks.
Reference rooms put people where the reference map had NPCs; mockup rooms use the mockup markers.
"""

IM = dict(exterior="MAP_ISLE_MARAIS", exterior_spec="isle_marais.json", exterior_cfg="orleans_bayou",
          group="gMapGroup_IndoorIsleMarais", mapsec="MAPSEC_ISLE_MARAIS", music="MUS_RG_PALLET")
GO = dict(exterior="MAP_GRAND_OAK", exterior_spec="grand_oak.json", exterior_cfg="orleans_town",
          group="gMapGroup_IndoorGrandOak", mapsec="MAPSEC_GRAND_OAK", music="MUS_RG_CELADON")
OW = dict(exterior="MAP_OLD_WATER", exterior_spec="old_water.json", exterior_cfg="orleans_village",
          group="gMapGroup_IndoorOldWater", mapsec="MAPSEC_OLD_WATER", music="MUS_RG_FUCHSIA")
HOME = dict(ref=True, tileset="orleans_home", secondary="gTileset_OrleansHome")
HALL = dict(ref=True, tileset="orleans_hall", secondary="gTileset_OrleansHall")
HALLM = dict(style="hall", tileset="orleans_hall", secondary="gTileset_OrleansHall")
CHURCHM = dict(style="church", tileset="orleans_hall", secondary="gTileset_OrleansHall")
SERV = dict(ref=True, tileset="orleans_services", secondary="gTileset_OrleansServices")
ROOT = dict(style="rootkin", tileset="orleans_rootkin_in", secondary="gTileset_OrleansRootkinIn")
CONS = dict(style="conservatory", tileset="orleans_conservatory", secondary="gTileset_OrleansConservatory")


PH1, PH2 = "LAYOUT_NEW_BARK_TOWN_PLAYERS_HOUSE_1F", "LAYOUT_NEW_BARK_TOWN_PLAYERS_HOUSE_2F"


def room(base, kind, **kw):
    r = dict(base)
    r.update(kind)
    r.update(kw)
    return r


ROOMS = [
    # ---------------- Isle Marais
    room(IM, HALLM, map="IsleMarais_Shelter", const="MAP_ISLE_MARAIS_SHELTER", door_label="Fais do-do dance hall (shelter)",
         mockup="isle_marais_shelter",
         people=[("mother", "", {"custom": True, "flag": "FLAG_HIDE_SHELTER_MOM"}),
                 ("lafayette", "", {"custom": True, "flag": "FLAG_HIDE_SHELTER_LAFAYETTE"}),
                 ("nurse", ""),
                 ("clerk", ""),
                 ("recruit", "We've got hot food and good news.\\nTake a pamphlet, friend."),
                 ("fisherman", "", {"custom": True}),
                 ("accordion", "Someone still plays that old\\naccordion every evening.", {"custom": True}),
                 # the starter pick (story steps 2-3): three Poké Balls on the field-station table (top right), Jayden and Wren
                 ("totodile", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_HIDE_SHELTER_TOTODILE"}),
                 ("chikorita", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_HIDE_SHELTER_CHIKORITA"}),
                 ("fuecoco", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_ITEM_BALL", "flag": "FLAG_HIDE_SHELTER_FUECOCO"}),
                 ("jayden", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_BOY_1", "flag": "FLAG_HIDE_SHELTER_JAYDEN", "face": "RIGHT"}),
                 ("wren", "", {"custom": True, "gfx": "OBJ_EVENT_GFX_GIRL_3", "flag": "FLAG_HIDE_SHELTER_WREN", "face": "LEFT"})],
         mart=["ITEM_POTION", "ITEM_POKE_BALL", "ITEM_ANTIDOTE", "ITEM_PARALYZE_HEAL"],
         positions=[(6, 9), (18, 5), (2, 4), (10, 3), (3, 13), (13, 12), (5, 2), (16, 2), (17, 2), (18, 2), (13, 6), (20, 5)],
         stamps=[("patch:accordion", 5, 1, 1)]),
    room(IM, HOME, map="IsleMarais_PlayersHouse", const="MAP_ISLE_MARAIS_PLAYERS_HOUSE", door_label="Player's house (damaged)",
         # ground floor: kitchen, TV and window on the back wall, stairs up in the corner, the table on its
         # rug in the middle (the bed is upstairs). Pieces from the HnS player's house.
         kit=dict(size=(11, 10), wall_top="jb:0A8", wall="jb:0B0", floor="jb:0A9", outside="jb:008", mat_x=5,
                  edge_left="jb:0B1"),
         copies=[(PH1, 1, 0, 3, 3, 1, 0),      # sink, counter and fridge
                 (PH1, 5, 0, 2, 3, 4, 0),      # TV and drawers
                 (PH1, 8, 0, 2, 2, 6, 0),      # window
                 (PH1, 10, 0, 3, 4, 8, 0),     # stairs up
                 (PH1, 5, 3, 5, 1, 4, 4),      # rug, top edge
                 (PH1, 4, 4, 6, 3, 3, 5),      # table and chairs on the rug
                 (PH1, 1, 4, 1, 2, 0, 6),      # potted plant (left)
                 (PH1, 12, 7, 1, 2, 10, 7),    # potted plant (right)
                 (PH1, 8, 8, 3, 2, 4, 8)],     # exit mat and door frame
         stamps=[("jb:0C3", 3, 4, 0)],         # rug, top-left corner
         warps_extra=[(8, 2, "MAP_ISLE_MARAIS_PLAYERS_HOUSE_2F", 0)],
         people=[("mother", "MOM: It's good to be home.\\nRest up whenever you need to.", {"flag": "FLAG_HIDE_PLAYERS_HOUSE_MOM"})], positions=[(3, 3)]),
    room(IM, HOME, map="IsleMarais_PlayersHouse_2F", const="MAP_ISLE_MARAIS_PLAYERS_HOUSE_2F", door_label=None,
         # the player's bedroom: PC, game console and TV, bookshelf, bed, clock (HnS player's room as-is)
         exit_to=("MAP_ISLE_MARAIS_PLAYERS_HOUSE", 1), people=[]),
    room(IM, CHURCHM, map="IsleMarais_Church", const="MAP_ISLE_MARAIS_CHURCH", door_label="Church", mockup="isle_marais_church",
         positions=[(7, 4), (12, 4), (3, 12)],
         people=[("priest", "The town is coming back together,\\none family at a time."),
                 ("ringer", "I ring the bell every hour.\\nIt helps people find their way home."),
                 ("parishioner", "I light a candle for the folks\\nwho haven't come back yet.")]),
    room(IM, HOME, map="IsleMarais_HouseNE", const="MAP_ISLE_MARAIS_HOUSE_NE", door_label="House (tarped roof)",
         # a family home: window, TV, bookshelf and clock on the back wall, the child's bed, a small table on
         # a rug (HnS player's house pieces, arranged differently from the player's own house)
         kit=dict(size=(11, 10), wall_top="jb:0A8", wall="jb:0B0", floor="jb:0A9", outside="jb:008", mat_x=5,
                  edge_left="jb:0B1"),
         copies=[(PH1, 8, 0, 2, 2, 1, 0),      # window
                 (PH1, 5, 0, 2, 3, 4, 0),      # TV and drawers
                 (PH2, 5, 0, 2, 3, 7, 0),      # bookshelf
                 (PH2, 10, 0, 1, 2, 10, 0),    # clock
                 (PH2, 0, 5, 3, 3, 0, 3),      # the child's bed
                 (PH2, 6, 5, 4, 4, 5, 3),      # small table on a rug
                 (PH1, 12, 7, 1, 2, 10, 7),    # potted plant
                 (PH1, 8, 8, 3, 2, 4, 8)],     # exit mat and door frame
         people=[("neighbour", "Could you check on the levee crew?\\nThey've been out there since dawn."),
                 ("child", "I saw a weird POKéMON on ROUTE 1!\\nI wish I could see it again.")],
         positions=[(3, 7), (1, 6)]),
    room(IM, HOME, map="IsleMarais_HouseW", const="MAP_ISLE_MARAIS_HOUSE_W", door_label="House (west)",
         crop=(0, 0, 11, 10),
         people=[("fisherman", "The shrimp boats used to fill\\nthat whole channel.")]),
    room(IM, HOME, map="IsleMarais_HouseE", const="MAP_ISLE_MARAIS_HOUSE_E", door_label="House (east)",
         people=[("baby", "The baby only sleeps when someone\\nplays the accordion.")]),
    room(IM, HOME, map="IsleMarais_HouseEastmost", const="MAP_ISLE_MARAIS_HOUSE_EASTMOST", door_label="House (tilted)",
         # the retired shrimper's house: Mr. Briney's house from Emerald (Route 104), on Emerald's own tilesets
         # Mr. Briney's house from Emerald (Route 104), vanilla pokeemerald files
         tileset="orleans_briney", secondary="gTileset_OrleansBriney", width=12,
         people=[("shrimper", "Forty years on the water. The storm\\ntook my boat, but not my stories.")]),
    # ---------------- Grand Oak (Magnolia's town)
    room(GO, SERV, map="GrandOak_PokemonCenter", const="MAP_GRAND_OAK_POKEMON_CENTER", door_label="Pokemon Center", music="MUS_POKE_CENTER",
         people=[("nurse", ""), ("traveller", "MAGNOLIA's gym uses Grassy Terrain.\\nFire or Flying types help."),
                 ("volunteer", "The ISLE MARAIS shelter still needs\\nsupplies, if you're heading back.")],
         positions=[None, (3, 6), (10, 7)]),
    room(GO, SERV, map="GrandOak_Mart", const="MAP_GRAND_OAK_MART", door_label="Poke Mart", music="MUS_POKE_MART",
         people=[("clerk", ""), ("shopper", "RITA's people bought out every\\nSUPER POTION in town.")],
         mart=["ITEM_POKE_BALL", "ITEM_POTION", "ITEM_ANTIDOTE", "ITEM_PARALYZE_HEAL", "ITEM_REPEL", "ITEM_ESCAPE_ROPE"]),
    room(GO, HOME, map="GrandOak_Nursery", const="MAP_GRAND_OAK_NURSERY", door_label="Garden nursery (Berries)",
         people=[("gardener", "The magnolias are my pride. The\\nrest of the garden is a sideline."),
                 ("helper", "I water the beds out back. Slowly,\\nbut it's worth it.")]),
    room(GO, HOME, map="GrandOak_HouseSW1", const="MAP_GRAND_OAK_HOUSE_SW1", door_label="House (south-west)",
         crop=(0, 0, 11, 10),  # a basic HnS house
         people=[("grandmother", "I remember when those magnolias\\nwere planted."), ("grandson", "I want a BONSLY!")]),
    room(GO, HOME, map="GrandOak_HouseSW2", const="MAP_GRAND_OAK_HOUSE_SW2", door_label="House (south-centre)",
         crop=(0, 0, 11, 10),
         people=[("woman", "I sell sugarcane in CRESCENT CITY,\\nbut that hedge ruined my route.")]),
    room(GO, HOME, map="GrandOak_HouseSE", const="MAP_GRAND_OAK_HOUSE_SE", door_label="House (south-east)",
         crop=(0, 0, 11, 10),
         people=[("recruit", "RITA says the serpent was murdered.\\nI don't know what to believe.")]),
    room(GO, CONS, map="GrandOak_Gym", const="MAP_GRAND_OAK_GYM", door_label="Gym: glass conservatory", mockup="grand_oak_gym",
         music="MUS_GYM",
         people=[("guide", "MAGNOLIA's waiting at the heart\\nof the maze. Don't get lost!"),
                 ("gardener", "", {"custom": True, "sight": 2, "face": "LEFT"}),   # faces along the corridor (down was a hedge: sight_lint)
                 ("aroma lady", "", {"custom": True, "sight": 2}),
                 ("magnolia", "", {"custom": True})]),
    # ---------------- The Old Water
    room(OW, ROOT, map="OldWater_Healer", const="MAP_OLD_WATER_HEALER", door_label="Healer", mockup="old_water_healer",
         people=[("nurse", ""), ("apprentice", "That one's sweetgrass. That one's\\nfor fevers. That one... I forget.")]),
    room(OW, ROOT, map="OldWater_SongHouse", const="MAP_OLD_WATER_SONG_HOUSE", door_label="Song house", mockup="old_water_song_house",
         people=[("tupelo", "", {"custom": True}),
                 ("wren", "", {"custom": True})]),
    room(OW, ROOT, map="OldWater_Trader", const="MAP_OLD_WATER_TRADER", door_label="Trader", mockup="old_water_trader",
         people=[("clerk", ""), ("child", "I collect shiny shells!\\nThis one's my favourite.")],
         mart=["ITEM_NET_BALL", "ITEM_POKE_BALL", "ITEM_POTION", "ITEM_ORAN_BERRY"]),
    room(OW, ROOT, map="OldWater_Carver", const="MAP_OLD_WATER_CARVER", door_label="Carver's workshop", mockup="old_water_carver",
         people=[("carver", "", {"custom": True})]),
    room(OW, ROOT, map="OldWater_TupelosHouse", const="MAP_OLD_WATER_TUPELOS_HOUSE", door_label="Tupelo's house", mockup="old_water_tupelo",
         people=[("tupelo", "TUPELO: The water was here first.\\nWe only borrow the banks.")]),
    room(OW, ROOT, map="OldWater_RestHouse", const="MAP_OLD_WATER_REST_HOUSE", door_label="Rest house (bed)", mockup="old_water_rest_house",
         people=[("nurse", "")]),
    room(OW, ROOT, map="OldWater_WrensHouse", const="MAP_OLD_WATER_WRENS_HOUSE", door_label="Wren's house", mockup="old_water_wren",
         people=[("wren", "WREN: Come back when you've got\\nanother verse. Then we'll battle!", {"flag": "FLAG_HIDE_WRENS_HOUSE_WREN"})]),
    room(OW, ROOT, map="OldWater_CanoeDocks", const="MAP_OLD_WATER_CANOE_DOCKS", door_label="Canoe docks", mockup="old_water_canoe_docks",
         people=[("boatman", "", {"custom": True})]),
]


# ---------------------------------------------------------------- mockup styles: mockup shapes -> our art
def paint_rootkin(kind, label, dx, dy, rw, rh, x, y, w=0, h=0):
    if kind in (None, "wall"):
        return "side", 1
    if kind == "thatch":
        return ("thatch_top" if y == 0 else "thatch_bot"), 1
    if kind == "exit":
        return "doormat", 0
    if kind == "rug":
        if "kettle" in label:
            return f"kettle_{dx % 2 + 2 * (dy % 2)}", 1
        if "fire" in label and rw == 3 and rh == 3:
            return f"firepit_{dx + 3 * dy}", 1
        if "fire" in label:
            cx, cy = rw // 2 - 1, rh // 2 - 1
            if 0 <= dx - cx < 2 and 0 <= dy - cy < 2:
                return f"hearth_{(dx - cx) + 2 * (dy - cy)}", 1
            return "mat", 0
        if rw == 1:
            return "mat", 0
        return ("mat_L" if dx == 0 else "mat_R" if dx == rw - 1 else "mat_M"), 0
    if kind == "bed":  # on the right of the room, mirrored so the pillow is against the wall
        m = "m" if w and x >= w / 2 else ""
        return (f"bedroll{m}_L" if dx % 2 == 0 else f"bedroll{m}_R"), 1
    if kind == "stool":
        return "stool", 1
    if kind == "counter":
        if "trade" in label:  # the trader's counter, wares along it
            part = "L" if dx == 0 else "R" if dx == rw - 1 else "M"
            return f"counter_{part}_{'bare' if part != 'M' else 'potions' if dx == rw // 2 else 'balls'}", 1
        if "workbench" in label:  # tools at the ends, the charm in the middle
            if dx == 0:
                return "wb_L_knife", 1
            if dx == rw - 1:
                return "wb_R_knife", 1
            return ("wb_M_charm" if dx == rw // 2 else "wb_M_mallet"), 1
        if "canoe" in label:
            return f"canoe_{0 if dy == 0 else 2 if dy == rh - 1 else 1}", 1
        return ("bench_L" if dx % 2 == 0 else "bench_R"), 1
    if kind == "shelf":
        if y < 2:
            if "verse" in label:  # each verse panel has its own painting
                return f"verse{label.split()[-1]}_{'L' if dx == 0 else 'R'}{dy}", 1
            if "net" in label:
                return f"net_{'L' if dx == 0 else 'R' if dx == rw - 1 else 'M'}", 1
            if "baskets" in label:
                return f"wbasket_{'L' if dx % 2 == 0 else 'R'}", 1
            for key in ("herbs", "paddles"):
                if key in label:
                    return f"{key}_{'L' if dx % 2 == 0 else 'R'}", 1
            return "thatch_bot", 1
        return ("basket" if (x + y) % 2 else "jar"), 1
    if kind == "stage":
        for orb in ("blue", "red"):
            if orb in label:
                return f"orb_{orb}_{0 if dy == 0 else 1}{'w' if y < 2 else ''}", 1  # w: standing against the back wall
        if "logs" in label:
            return f"logs_{dx % 2 + 2 * (dy % 2)}", 1
        if "seat" in label:  # Tupelo's chair: he sits on the seat; the high back stands behind him
            return (f"chair_0{'w' if y < 2 else ''}", 1) if dy == 0 else ("chair_1", 0)  # w: against the back wall
        return "mat", 0
    return ("floor" if (x * 3 + y) % 5 else "floor_b"), 0


def paint_conservatory(kind, label, dx, dy, rw, rh, x, y, w=0, h=0, kinds=None):
    """Our glass walls and dais round a hedge maze of HnS Celadon gym tiles (cg:*): each hedge tree's crown
    overlaps the tile above it, so the tile above a hedge is the 'tree top' version."""
    at = lambda xx, yy: kinds[yy][xx] if 0 <= yy < len(kinds) and 0 <= xx < len(kinds[0]) else None
    if kind in (None, "wall"):
        return "glass_side", 1
    if kind == "glass":
        return ("glass_0" if y == 0 else "glass_1" if y == 1 else "glass_side"), 1
    if kind == "exit":
        return "exitmat", 0
    if kind == "stage":
        return ("dais_L" if dx == 0 else "dais_R" if dx == rw - 1 else "dais_M"), 0
    if kind == "hedge":
        return ("cg:40D" if at(x, y + 1) == "hedge" else "cg:415"), 1
    if kind == "flowers":
        return ("cg:436" if (x + y) % 2 else "cg:437"), 0
    if kind == "statue":
        return ("cg:438", 0) if dy == 0 else ("cg:439", 1)
    if kind == "sand":
        if dy == rh - 1 and dx in (8, 9, 10):  # the mat in front of the door
            return f"cg:{0x430 + dx - 8:03X}", 0
        return ("cg:41D" if dy == 0 else "cg:425"), 0
    if kind == "grass":
        if at(x, y + 1) == "hedge":
            return "cg:405", 0
        return "cg:46E", 0
    return "pavers", 0


def paint_hall(kind, label, dx, dy, rw, rh, x, y, w, h):
    """The Fais Do-Do dance hall: Ecruteak theater walls and floors, our own cots, counters and kit."""
    if kind in (None, "wall"):
        if y == h - 1:
            return "jb:000", 1
        if x in (0, w - 1):
            return "th:44D", 1
        if y == 0:
            return ("th:445" if x in (0, w - 1) else "th:446" if x % 2 else "th:441"), 1
        return ("th:44E" if x % 2 else "th:449"), 1
    if kind == "exit":
        return "th:461", 0
    if kind == "bed":
        return f"patch:cot_{0 if dy == 0 else 1}", 1
    if kind == "rug":  # the dance floor, with the theater's border
        top, bot, left, right = dy == 0, dy == rh - 1, dx == 0, dx == rw - 1
        if top:
            return ("th:442" if left else "th:444" if right else "th:443"), 0
        if bot:
            return ("th:452" if left else "th:454" if right else "th:453"), 0
        return ("th:44A" if left else "th:44C" if right else "th:44B"), 0
    if kind == "counter":
        part = "L" if dx == 0 else "R" if dx == rw - 1 else "M"
        if "supply" in label:
            return f"patch:{['ct_L_water', 'ct_M_cans', 'ct_M_bread', 'ct_M_water'][min(dx, 3)] if part != 'R' else 'ct_R_aid'}", 1
        if "nurse" in label:
            return f"patch:{ {'L': 'ct_L_aid', 'M': 'ct_M_aid', 'R': 'ct_R_aid'}[part]}", 1
        if "field" in label:
            return f"patch:{ {'L': 'ct_L_papers', 'M': 'ct_M_papers', 'R': 'ct_R_papers'}[part]}", 1
        if "hot" in label:
            return f"patch:{'ct_L_pot' if dx == 0 else 'ct_R_bowls'}", 1
        return "patch:ct_M_cans", 1
    if kind == "stage":
        side = "_L" if dx == 0 else "_R" if dx == rw - 1 else ""
        return ("patch:stage_lip" if dy == rh - 1 else "patch:stage") + side, 0
    if kind == "shelf":  # Lafayette's PC / lab kit
        return f"patch:labkit_{(dx % 2) + 2 * (dy % 2)}", 1
    return "th:459", 0


def paint_church(kind, label, dx, dy, rw, rh, x, y, w, h):
    """The Isle Marais church (own art): stone floor, wood and plaster walls with stained glass, pews,
    the altar on its step, a red aisle runner, candles and the bell rope."""
    if kind in (None, "wall"):
        if y == h - 1:
            return "jb:000", 1
        if x in (0, w - 1):
            return "cw:side", 1
        window = x in (3, 7, 11)
        return (f"cw:{'win' if window else 'wall'}_{0 if y == 0 else 1}"), 1
    if kind == "exit":
        return f"cw:mat_{'L' if dx == 0 else 'R' if dx == rw - 1 else 'C'}", 0
    if kind == "counter":  # pews
        return f"cw:pew_{'L' if dx == 0 else 'R' if dx == rw - 1 else 'M'}", 1
    if kind == "stage":  # the altar
        return f"cw:altar_{'L' if dx == 0 else 'R' if dx == rw - 1 else 'M'}{0 if dy == 0 else 1}", 1 if dy == 0 else 0
    if kind == "rug":
        return f"cw:run_{'T' if dy == 0 else 'M'}{'L' if dx == 0 else 'R' if dx == rw - 1 else 'C'}", 0
    if kind == "shelf":
        if "rope" in label:
            return (f"cw:rope_{0 if dy == 0 else 1}" if dx == 0 else "cw:floor"), 1 if dx == 0 else 0
        return "cw:candles", 1
    return "cw:floor", 0


STYLES = {
    "church": {"prefix": "cw", "side": "cw:side", "paint": paint_church},
    "hall": {"prefix": "th", "side": "th:44D", "paint": paint_hall},
    "rootkin": {"prefix": "rk", "side": "side", "paint": paint_rootkin},
    "conservatory": {"prefix": "cv", "side": "glass_side", "paint": paint_conservatory, "neighbours": True},
}

# the rest of the game: first-pass rooms painted straight from their mockups (interior_rooms_world.py)
import interior_rooms_world as _world  # noqa: E402
STYLES["generic"] = _world.STYLE
ROOMS += _world.world_rooms(room)

# the finale's two arenas are drawn from the approved arena art (arena_rooms.py), not from their planning mockups: the Drowned Temple and
# the Salt Cathedral on their own secondaries, the layout cell for cell
import arena_rooms as _arena  # noqa: E402
for _r in ROOMS:
    _a = {"lands_end_drowned_temple": "temple", "lands_end_salt_cathedral": "cathedral"}.get(_r.get("mockup"))
    if _a:
        _r.update(arena=_a, tileset=_arena.ARENAS_BY_NAME[_a]["tileset"], secondary=_arena.ARENAS_BY_NAME[_a]["secondary"],
                  border=_arena.ARENAS_BY_NAME[_a]["border"])

"""Planning mockups for every interior after the vertical slice: Storm's Edge through Land's End.

Drawn by interiors.py (same style, same key), which merges these with the vertical-slice rooms. Each town's
buildings, gym trials and story beats come from its town mockup (../orleans_maps/NN_<town>.png) and the
region design doc. Coordinates are tiles inside the room (0,0 = top-left of the back wall); the door is in
the middle of the bottom wall unless "door" says otherwise.
"""

GROUPS = [("Storm's Edge", "storms_edge_"), ("Crescent City", "crescent_city_"), ("Pointe Rouge", "pointe_rouge_"),
          ("Camp Cocodrie", "camp_cocodrie_"), ("Lutin's Hollow", "lutins_hollow_"), ("Redfield", "redfield_"),
          ("Land's End", "lands_end_")]


def world(house, maze):
    """The rest of the game's interiors, keyed like interiors.INTERIORS (the key's prefix is its town)."""

    def center(title, sub, markers=(), notes=(), extra=()):
        """A Pokémon Center: nurse counter, PC, benches, plants (15 x 10)."""
        return {"title": title, "subtitle": sub, "size": (15, 10), "floor": "tile",
                "shapes": [("counter", 5, 3, 5, 1, "nurse counter"), ("shelf", 12, 2, 2, 2, "PC"),
                           ("counter", 1, 6, 3, 1, "bench"), ("counter", 11, 6, 3, 1, "bench"),
                           ("plant", 1, 2, 1, 1), ("plant", 13, 7, 1, 1), ("rug", 6, 7, 3, 1)] + list(extra),
                "markers": [("heal", 7, 2, "Nurse: heals the party")] + list(markers),
                "notes": list(notes), "exits": [(7, 9, "Exit")]}

    def shop(title, sub, stock, markers=(), notes=(), extra=(), size=(11, 9)):
        """A shop: counter on the left, shelves on the right."""
        w, h = size
        return {"title": title, "subtitle": sub, "size": size, "floor": "tile",
                "shapes": [("counter", 1, 4, 3, 1, "counter"), ("shelf", w - 4, 3, 3, 1, "shelves"),
                           ("shelf", w - 4, 5, 3, 1, "shelves")] + list(extra),
                "markers": [("shop", 2, 3, f"Clerk: {stock}")] + list(markers),
                "notes": list(notes), "exits": [(w // 2, h - 1, "Exit")]}

    R = {}

    # ================================================================ Storm's Edge (gym 2, Éclair)
    R["storms_edge_pokecenter"] = center(
        "Pokémon Center (generator)", "Storm's Edge · the lights flicker until the grid is back",
        [("npc", 2, 5, "Lineworker: the grid's down past the drawbridge; ÉCLAIR's crew is on it"),
         ("event", 12, 5, "Backup generator: hums and sputters; the lights steady after the trial")],
        ["A backup generator in the corner keeps the healing machine running.",
         "The overhead lights flicker until ÉCLAIR's trial restores the grid (palette swap)."],
        [("metal", 12, 4, 2, 1, "generator")])
    R["storms_edge_mart"] = shop(
        "Poké Mart", "Storm's Edge · half-empty shelves after the storm",
        "Potion, Paralyze Heal, Repel, Poké Ball; Super Potion after the trial",
        [("npc", 8, 6, "Shopper: everything electric sold out in a day")],
        ["Shelves restock after the trial (the delivery trucks can cross the drawbridge again)."])
    R["storms_edge_gym"] = {
        "title": "Storm's Edge Gym: Substation", "subtitle": "Gym 2 · Éclair (Electric Terrain) · restore the power grid",
        "size": (21, 18), "floor": "stone",
        "shapes": [("metal", 1, 3, 3, 3, "transformer"), ("metal", 17, 3, 3, 3, "transformer"),
                   ("metal", 1, 10, 3, 3, "transformer"), ("metal", 17, 10, 3, 3, "transformer"),
                   ("stage", 8, 2, 5, 2, "Éclair's\ncontrol desk"), ("screen", 6, 2, 2, 1), ("screen", 13, 2, 2, 1),
                   ("counter", 5, 6, 11, 1, "conduit"), ("counter", 5, 9, 11, 1, "conduit"),
                   ("counter", 5, 12, 11, 1, "conduit"), ("rug", 9, 15, 3, 2)],
        "markers": [("npc", 12, 15, "Gym guide: the junctions only turn one way. Watch the buoy VOLTORB!"),
                    ("switch", 6, 7, "Junction 1: rotate to carry the current up"),
                    ("switch", 10, 7, "Junction 2"), ("switch", 14, 7, "Junction 3"),
                    ("switch", 6, 10, "Junction 4"), ("switch", 10, 10, "Junction 5"), ("switch", 14, 10, "Junction 6"),
                    ("event", 8, 13, "Buoy VOLTORB roll along the conduits; touching one starts a battle"),
                    ("trainer", 4, 8, "Trainer: Lineworker (Magnemite, Voltorb)"),
                    ("trainer", 16, 11, "Trainer: Electrician (Joltik, Elekid)"),
                    ("npc", 10, 2, "ÉCLAIR (Electric Terrain): buoy Voltorb, Joltik, Wattrel")],
        "notes": ["Trial: rotate the junction tiles so a single line runs from the generator to the control desk.",
                  "Each completed row lights one district outside (the lights come back street by street).",
                  "Reward: the second verse, an Electric TM and the Pry Bar from Éclair's lineworkers.",
                  "After the trial the drawbridge outside is lowered: Route 3 opens."],
        "exits": [(10, 17, "Exit to Storm's Edge")]}
    R["storms_edge_seafood_market"] = shop(
        "Seafood Market", "Storm's Edge · the fishmonger buys treasure from the Gulf",
        "buys Pearls, Big Pearls and Stardust at a good price; sells Net Balls and Repels",
        [("npc", 5, 6, "Shrimper: the trawlers will go out again once the grid's back"),
         ("item", 9, 6, "Item: a Big Pearl in a crate of oysters (one time)")],
        ["Ice chests and crab traps along the walls; the place to sell treasure early."],
        [("counter", 1, 6, 2, 1, "ice chest"), ("counter", 8, 2, 2, 1, "ice chest")])
    R["storms_edge_house_w"] = house(
        "Stilt House (west)", "Storm's Edge · a lineworker's family",
        [("npc", 3, 4, "Mother: her husband's been up the poles for three days"),
         ("npc", 7, 5, "Child: wants to see the lighthouse lit again")],
        ["Ordinary house; a hard hat and coiled cable by the door."])
    R["storms_edge_house_c"] = house(
        "Stilt House (centre)", "Storm's Edge · the old fisherman",
        [("npc", 4, 4, "Old fisherman: gives the Good Rod once the grid is restored"),
         ("item", 8, 3, "Item: Net Ball on the shelf")],
        ["Nets and rods on the wall; a photo of the harbour before the storm."])
    R["storms_edge_house_e"] = house(
        "Stilt House (east)", "Storm's Edge · in-game trade",
        [("npc", 5, 4, "Trader: swaps a Wingull for a Magikarp (it's homesick for the sea)")],
        ["A trade house; the Wingull has a nickname and a Pretty Wing."])
    R["storms_edge_lighthouse"] = {
        "title": "Lighthouse", "subtitle": "Storm's Edge · the keeper's room, stairs up to the lamp gallery",
        "size": (11, 11), "floor": "stone",
        "shapes": [("shelf", 1, 2, 2, 2, "log\nbook"), ("bed", 8, 2, 2, 1), ("stage", 4, 2, 3, 3, "spiral\nstairs"),
                   ("counter", 1, 6, 2, 2, "table"), ("rug", 4, 8, 3, 1)],
        "markers": [("npc", 7, 6, "Keeper: the lamp's been dark since the storm; ÉCLAIR's grid will light it"),
                    ("event", 5, 5, "Stairs up to the lamp gallery (an outdoor balcony map)"),
                    ("item", 9, 7, "Item: Thunder Stone in the keeper's toolbox (after the trial)")],
        "notes": ["Post-game: the weekly storm brings ZAPDOS to the lamp gallery at the top.",
                  "The lamp is lit after ÉCLAIR's trial: a sweeping beam over the harbour at night."],
        "exits": [(5, 10, "Exit")]}

    R["storms_edge_lighthouse_gallery"] = {
        "title": "Lighthouse Lamp Room", "subtitle": "Storm's Edge · the great lens, up the spiral stairs",
        "size": (11, 9), "floor": "stone",
        "shapes": [("stage", 1, 2, 2, 2, "spiral\nstairs"), ("glass", 3, 2, 5, 1, "storm windows"),
                   ("metal", 4, 4, 3, 2, "great lens"), ("glass", 8, 2, 2, 1, "storm windows")],
        "markers": [("event", 5, 6, "The great lens: dark until ÉCLAIR's grid is restored; post-game, ZAPDOS "
                                    "rides the weekly storm here")],
        "notes": ["Reached by the keeper's spiral stairs; no door of its own."],
        "exits": []}

    # ================================================================ Crescent City (hub, gym 3, Fifolet)
    R["crescent_city_cathedral"] = {
        "title": "Cathedral", "subtitle": "Crescent City · French Quarter · bell tower above",
        "size": (19, 17), "floor": "stone",
        "shapes": [("stage", 6, 2, 7, 2, "altar"), ("rug", 8, 4, 3, 12, "aisle"),
                   ("counter", 2, 6, 5, 1, "pew"), ("counter", 12, 6, 5, 1, "pew"),
                   ("counter", 2, 8, 5, 1, "pew"), ("counter", 12, 8, 5, 1, "pew"),
                   ("counter", 2, 10, 5, 1, "pew"), ("counter", 12, 10, 5, 1, "pew"),
                   ("counter", 2, 12, 5, 1, "pew"), ("counter", 12, 12, 5, 1, "pew"),
                   ("shelf", 1, 2, 2, 1, "candles"), ("shelf", 16, 2, 2, 1, "candles"),
                   ("stage", 16, 14, 2, 2, "tower\nstairs")],
        "markers": [("npc", 9, 3, "Priest: the city kept its bells through the storm"),
                    ("npc", 4, 9, "Choir singer: hums a tune like the Rootkin's songs"),
                    ("event", 16, 13, "Bell-tower stairs (post-game: Galarian ARTICUNO in the tower)")],
        "notes": ["Modelled on St. Louis Cathedral: tall windows, a long aisle, side candles.",
                  "The second-line parade leader outside (Quaxly after gym 3, Quaquaval after gym 6) starts here."],
        "exits": [(9, 16, "Exit")]}
    R["crescent_city_cafe"] = {
        "title": "Café", "subtitle": "Crescent City · French Quarter · Pokéblocks and beignets",
        "size": (13, 10), "floor": "wood",
        "shapes": [("counter", 1, 3, 5, 1, "counter"), ("metal", 1, 2, 2, 1, "blender"),
                   ("counter", 7, 4, 2, 1, "table"), ("counter", 10, 4, 2, 1, "table"),
                   ("counter", 7, 7, 2, 1, "table"), ("counter", 10, 7, 2, 1, "table"), ("rug", 5, 8, 3, 1)],
        "markers": [("shop", 3, 2, "Barista: sells Pokéblocks (the Pokéblock case comes free)"),
                    ("service", 1, 2, "ROTOM quest: the blender (after gym 3)"),
                    ("npc", 9, 5, "Regular: Pokéblocks make contest-style condition... and happy Pokémon")],
        "notes": ["The café that sells Pokéblocks (design doc).", "Powdered-sugar floor by the counter."],
        "exits": [(6, 9, "Exit")]}
    R["crescent_city_apartment"] = {
        "title": "The Player's Apartment", "subtitle": "Crescent City · French Quarter · decorated like a secret base",
        "size": (13, 10), "floor": "wood",
        "shapes": [("shelf", 1, 2, 2, 1, "PC"), ("bed", 10, 2, 2, 2), ("rug", 4, 4, 5, 3, "decoration\nspace"),
                   ("shelf", 10, 6, 2, 1, "mailbox")],
        "markers": [("event", 6, 5, "Decorations: place desks, chairs, plants and dolls like a secret base"),
                    ("npc", 6, 8, "Landlady: hands over the keys")],
        "notes": ["Unlocks after 25 species are contributed to Lafayette's conservation project.",
                  "The PC and bed work like home: rest here to heal."],
        "exits": [(6, 9, "Exit")]}
    R["crescent_city_salon"] = shop(
        "Salon", "Crescent City · French Quarter · grooming raises friendship",
        "grooms one Pokémon a day (friendship up)",
        [("npc", 7, 6, "Client: my Furfrou's never looked better")],
        ["Two styling chairs with mirrors; one grooming a day per party."],
        [("stage", 6, 2, 2, 1, "mirror"), ("stage", 8, 2, 2, 1, "mirror")])
    R["crescent_city_laundry"] = {
        "title": "Laundry", "subtitle": "Crescent City · French Quarter · a ROTOM in the washer",
        "size": (11, 9), "floor": "tile",
        "shapes": [("metal", 1, 2, 9, 1, "washers"), ("metal", 1, 5, 3, 1, "dryers"), ("counter", 7, 5, 3, 1, "folding")],
        "markers": [("service", 5, 3, "ROTOM quest: the washer that spins on its own (after gym 3)"),
                    ("npc", 2, 6, "Owner: one machine keeps running with nothing in it")],
        "notes": ["Part of the Rotom quest: TV, blender, washer, freezer, then the waterfront generator."],
        "exits": [(5, 8, "Exit")]}
    R["crescent_city_pokecenter_quarter"] = center(
        "Pokémon Center (French Quarter)", "Crescent City · one of two Centers",
        [("npc", 2, 5, "Tourist: came for the music, stayed for the storm cleanup"),
         ("npc", 12, 5, "Parade fan: the second line passes right by here")])
    R["crescent_city_pokecenter_waterfront"] = center(
        "Pokémon Center (Waterfront)", "Crescent City · one of two Centers, by the river",
        [("npc", 2, 5, "Deckhand: the riverboat leaves for Pointe Rouge from next door"),
         ("event", 12, 5, "Board: riverboat timetable and boat-route notices")])
    R["crescent_city_trades"] = house(
        "Trade House", "Crescent City · NPC trades (Alolan forms)",
        [("npc", 3, 4, "Trader: offers Alolan Sandshrew for a Kantonian one"),
         ("npc", 7, 4, "Trader: offers an Alolan Vulpix for a Kantonian one (if both make the dex)"),
         ("npc", 5, 6, "Collector: wants to see regional forms side by side")],
        ["Two or three in-game trades for regional forms (from the dex spreadsheet)."])
    R["crescent_city_dept_1f"] = {
        "title": "Department Store 1F", "subtitle": "Crescent City · downtown market · everything in the game is sold here",
        "size": (17, 12), "floor": "tile",
        "shapes": [("counter", 1, 3, 4, 1, "info desk"), ("shelf", 7, 3, 3, 1, "goods"), ("shelf", 11, 3, 3, 1, "goods"),
                   ("shelf", 7, 6, 3, 1, "goods"), ("shelf", 11, 6, 3, 1, "goods"), ("stage", 14, 2, 2, 2, "stairs"),
                   ("metal", 1, 8, 2, 2, "elevator"), ("screen", 15, 7, 1, 2, "TVs")],
        "markers": [("npc", 2, 2, "Receptionist: floor guide"),
                    ("shop", 9, 4, "Clerk: Poké Balls and medicine"),
                    ("service", 15, 8, "ROTOM quest: the TV display that changes channels by itself"),
                    ("event", 8, 10, "Andrew's speech in the plaza outside (story event 11)")],
        "notes": ["Three floors: 1F general goods, 2F TMs and evolution items, 3F the Mega Stone vendor.",
                  "When each item unlocks is still open in the design doc."],
        "exits": [(8, 11, "Exit")]}
    R["crescent_city_dept_2f"] = {
        "title": "Department Store 2F", "subtitle": "Crescent City · TMs, evolution items, the Linking Cord",
        "size": (17, 12), "floor": "tile",
        "shapes": [("shelf", 2, 3, 3, 1, "TMs"), ("shelf", 2, 6, 3, 1, "TMs"), ("shelf", 7, 3, 3, 1, "stones"),
                   ("shelf", 7, 6, 3, 1, "held\nitems"), ("counter", 11, 4, 3, 1, "counter"), ("stage", 14, 2, 2, 2, "stairs"),
                   ("metal", 1, 8, 2, 2, "elevator")],
        "markers": [("shop", 12, 3, "Clerk: evolution stones, the Linking Cord, held items"),
                    ("shop", 3, 5, "Clerk: TMs (stock grows with badges)"),
                    ("npc", 8, 9, "Shopper: trade evolutions just need a Linking Cord here")],
        "notes": ["Trade evolutions use the Linking Cord (decided)."],
        "exits": []}
    R["crescent_city_dept_3f"] = {
        "title": "Department Store 3F", "subtitle": "Crescent City · the Mega Stone vendor",
        "size": (17, 12), "floor": "carpet",
        "shapes": [("counter", 5, 3, 7, 1, "vendor's\ncases"), ("shelf", 1, 3, 2, 2, "vitamins"),
                   ("stage", 14, 2, 2, 2, "stairs"), ("metal", 1, 8, 2, 2, "elevator")],
        "markers": [("shop", 8, 2, "Mega Stone vendor: stones unlock as the charm's power grows"),
                    ("shop", 2, 5, "Clerk: vitamins, Rare Candy (late game)"),
                    ("npc", 12, 7, "Collector: Mega Stones mean nothing without the cypress charm")],
        "notes": ["The vendor sells stones after gym 6 (the charm from Tupelo)."],
        "exits": []}
    R["crescent_city_game_corner"] = {
        "title": "Game Corner", "subtitle": "Crescent City · downtown market",
        "size": (17, 12), "floor": "carpet",
        "shapes": [("metal", 2, 3, 1, 3, "slots"), ("metal", 5, 3, 1, 3, "slots"), ("metal", 8, 3, 1, 3, "slots"),
                   ("metal", 2, 7, 1, 3, "slots"), ("metal", 5, 7, 1, 3, "slots"), ("metal", 8, 7, 1, 3, "slots"),
                   ("counter", 12, 3, 4, 1, "prize\ncounter"), ("counter", 12, 7, 4, 1, "coin\ncounter")],
        "markers": [("shop", 14, 2, "Prize counter: TMs, a rare Pokémon, decorations"),
                    ("shop", 14, 8, "Coin exchange"), ("npc", 10, 5, "Gambler: the third slot pays out after a storm")],
        "notes": ["Slots and the roulette tables; prizes include apartment decorations."],
        "exits": [(8, 11, "Exit")]}
    R["crescent_city_name_rater"] = house(
        "Name Rater", "Crescent City · downtown market · free",
        [("service", 5, 4, "Name Rater: renames Pokémon for free")],
        ["Small office; a wall of framed nicknames."], size=(9, 8))
    R["crescent_city_tutor"] = house(
        "Tutor and Trainers' Gym", "Crescent City · downtown market · move tutor, EV and IV changers",
        [("service", 2, 4, "Move tutor: teaches moves for Heart Scales"),
         ("service", 6, 4, "EV coach: resets or trains EVs (costs money)"),
         ("service", 4, 6, "IV judge: raises IVs with Bottle Caps")],
        ["Service costs (design doc): tutor takes Heart Scales, EV changers money, IV changers Bottle Caps."],
        size=(9, 8))
    R["crescent_city_day_care"] = house(
        "Day Care", "Crescent City · city park",
        [("npc", 3, 4, "Day Care lady: raises two Pokémon"), ("npc", 7, 4, "Day Care man: watches the yard")],
        ["Standard Day Care; the yard is the city park outside."])
    R["crescent_city_conservation"] = {
        "title": "Conservation Center", "subtitle": "Crescent City · waterfront · zoo, aquarium, fossils",
        "size": (23, 16), "floor": "tile",
        "shapes": [("tank", 1, 2, 6, 3, "aquarium"), ("tank", 16, 2, 6, 3, "aquarium"),
                   ("grass", 1, 7, 5, 4, "marsh\nhabitat"), ("sand", 17, 7, 5, 4, "dry\nhabitat"),
                   ("counter", 8, 3, 7, 1, "contributions"), ("shelf", 9, 7, 5, 2, "fossil lab"),
                   ("rug", 10, 13, 3, 2)],
        "markers": [("npc", 11, 2, "LAFAYETTE: logs each species you contribute"),
                    ("service", 11, 9, "Fossil lab: revives the Kabuto fossil"),
                    ("event", 4, 9, "Habitats fill in as you contribute species (like a museum)"),
                    ("npc", 19, 12, "Keeper: the apartment key comes at 25 species")],
        "notes": ["Modelled on the Pokémon Lazarus conservation center: habitats fill with what the player catches.",
                  "Contributing 25 species earns the apartment (decided). Fossil revival is placed here (proposed)."],
        "exits": [(11, 15, "Exit")]}
    R["crescent_city_ice_cream"] = shop(
        "Ice Cream Parlour", "Crescent City · waterfront",
        "sells Casteliacone-style treats (cure status)",
        [("service", 9, 2, "ROTOM quest: the freezer that frosts over in summer"),
         ("npc", 5, 6, "Kid: the freezer growled at me!")],
        ["Small parlour; the freezer is the Rotom quest stop."], [("metal", 8, 2, 2, 1, "freezer")], size=(11, 8))
    R["crescent_city_riverboat_terminal"] = {
        "title": "Riverboat Terminal", "subtitle": "Crescent City · waterfront · ferry to Pointe Rouge",
        "size": (15, 10), "floor": "tile",
        "shapes": [("counter", 2, 3, 4, 1, "tickets"), ("counter", 9, 5, 4, 1, "benches"),
                   ("counter", 9, 7, 4, 1, "benches"), ("stage", 12, 2, 2, 2, "gangway")],
        "markers": [("npc", 4, 2, "Ticket clerk: the pass is valid after gym 3"),
                    ("event", 13, 4, "Gangway: board the riverboat to Pointe Rouge")],
        "notes": ["The riverboat is a cutscene ride (or a small boat map) to the Pointe Rouge landing on Route 4."],
        "exits": [(7, 9, "Exit")]}
    R["crescent_city_pelipper_post"] = {
        "title": "Pelipper Post", "subtitle": "Crescent City · waterfront · mail by Pelipper",
        "size": (13, 9), "floor": "wood",
        "shapes": [("counter", 2, 3, 5, 1, "mail counter"), ("shelf", 9, 2, 3, 2, "sorting\nshelves"),
                   ("stage", 9, 5, 3, 1, "perches")],
        "markers": [("npc", 4, 2, "Clerk: sends Mail; delivers daily gifts later"),
                    ("npc", 10, 6, "Pelipper handler: the birds know every roof in the city")],
        "notes": ["A mail and gift-delivery service (Mystery Gift style hook)."],
        "exits": [(6, 8, "Exit")]}
    TOMBS = [
        "#########.#########",
        "#.....#.....#.....#",
        "#.###.#.###.#.###.#",
        "#.#.......#.....#.#",
        "#.#.#####.#.###.#.#",
        "#...#.....#...#...#",
        "###.#.#######.#.###",
        "#...#.........#...#",
        "#.###.###.###.###.#",
        "#.................#",
        "#########.#########",
    ]
    R["crescent_city_gym"] = {
        "title": "Crescent City Gym: Old Cemetery", "subtitle": "Gym 3 · Fifolet (Ghost/Psychic) · the cemetery maze at night",
        "size": (21, 18), "floor": "stone",
        "shapes": [("stage", 8, 2, 5, 2, "Fifolet's\ncrypt")] + maze(1, 5, TOMBS, "tomb") + [("rug", 9, 16, 3, 1)],
        "markers": [("npc", 10, 2, "FIFOLET: Litwick (Fifolet form), Gastly, Drowzee, Mimikyu"),
                    ("switch", 2, 6, "Steady blue light: a true guide"),
                    ("switch", 18, 8, "Flickering orange light: leads back to the start"),
                    ("switch", 10, 10, "Steady blue light"), ("switch", 6, 12, "Flickering orange light"),
                    ("trainer", 14, 6, "Trainer: Hex Maniac"), ("trainer", 4, 14, "Trainer: Medium"),
                    ("npc", 12, 16, "Gym guide: follow the lights that don't blink")],
        "notes": ["Gym 3: a maze of tombs at night. Steady blue lights are true guides; flickering orange lights warp the "
                  "player back to the start.",
                  "Reward: the third verse, a Ghost TM, a Mimikyu and the Lantern (lights dark tunnels).",
                  "A mockup of the gym building; the old cemetery outside has the same feel."],
        "exits": [(10, 17, "Exit to the Old Cemetery")]}
    R["crescent_city_blacksnake_base"] = {
        "title": "Team Blacksnake Base", "subtitle": "Crescent City · Drowned Ward · act 1, cleared with Wren after gym 3",
        "size": (23, 16), "floor": "mud",
        "shapes": [("water", 1, 2, 6, 5, "flooded\nhall"), ("counter", 9, 3, 3, 2, "crates"), ("counter", 15, 3, 2, 3, "crates"),
                   ("wall", 8, 7, 1, 6), ("wall", 14, 7, 1, 6), ("stage", 17, 9, 5, 3, "command\nroom"),
                   ("screen", 18, 8, 3, 1), ("shelf", 2, 11, 3, 2, "Rootkin\ncarving"), ("rug", 10, 14, 3, 1)],
        "markers": [("trainer", 11, 6, "Grunt (Poison)"), ("trainer", 4, 9, "Grunt (Dark)"), ("trainer", 16, 12, "Grunt (Water)"),
                    ("npc", 19, 10, "Admin RITA's lieutenant: retreats after the battle"),
                    ("event", 3, 12, "The damaged Rootkin carving (story: the mistranslated verse)"),
                    ("npc", 12, 13, "WREN: fights alongside the player here (multi battle)"),
                    ("item", 21, 3, "Item: Dusk Ball")],
        "notes": ["A flooded warehouse in the Drowned Ward, occupied by Team Blacksnake.",
                  "Cleared with Wren after gym 3; the damaged carving shows the 'laid low' mistranslation."],
        "exits": [(11, 15, "Exit to the Drowned Ward")]}

    # ================================================================ Pointe Rouge (gym 4, Kingfisher)
    R["pointe_rouge_capitol_lobby"] = {
        "title": "Capitol Tower: Lobby", "subtitle": "Pointe Rouge · the tallest building in the region",
        "size": (17, 12), "floor": "stone",
        "shapes": [("counter", 6, 3, 5, 1, "reception"), ("metal", 14, 2, 2, 2, "elevator"),
                   ("carpet", 7, 6, 3, 5, ""), ("screen", 1, 2, 3, 1, "murals"), ("plant", 1, 9, 1, 1), ("plant", 15, 9, 1, 1)],
        "markers": [("npc", 8, 2, "Receptionist: the observation deck is open to the public"),
                    ("npc", 3, 6, "Tour guide: the tower was built after the great flood of the '27")],
        "notes": ["Art deco lobby; the elevator goes straight up to the observation deck."],
        "exits": [(8, 11, "Exit")]}
    R["pointe_rouge_capitol_deck"] = {
        "title": "Capitol Tower: Observation Deck", "subtitle": "Pointe Rouge · a view of the whole region",
        "size": (17, 11), "floor": "stone", "door": None,
        "shapes": [("glass", 1, 2, 15, 1, "windows"), ("metal", 3, 4, 1, 1), ("metal", 8, 4, 1, 1), ("metal", 13, 4, 1, 1),
                   ("metal", 14, 8, 2, 2, "elevator")],
        "markers": [("event", 3, 5, "Telescope: the high dry country (Routes 23 and 24) shimmers with heat"),
                    ("event", 8, 5, "Telescope: the Emerald River back to Crescent City"),
                    ("event", 13, 5, "Telescope: a storm over the Basin, where the rivers meet"),
                    ("npc", 6, 8, "Old man: points out where his house stood before the river moved")],
        "notes": ["Each telescope hints at a later area; the view of the Basin foreshadows the oldest shrine."],
        "exits": []}
    R["pointe_rouge_pokecenter"] = center(
        "Pokémon Center", "Pointe Rouge",
        [("npc", 2, 5, "Refinery worker: something's wrong at the plant, they sent us all home"),
         ("npc", 12, 5, "Angler: the fishing tournament on Route 5 decides who faces KINGFISHER")])
    R["pointe_rouge_mart"] = shop(
        "Poké Mart", "Pointe Rouge", "Great Ball, Super Potion, Full Heal, Repel, Escape Rope")
    R["pointe_rouge_tackle_shop"] = shop(
        "Tackle Shop", "Pointe Rouge · gear for the fishing tournament",
        "Lures (fishing encounter rate up), Net and Dive Balls",
        [("npc", 7, 6, "Tournament registrar: sign up here for KINGFISHER's trial")],
        ["Rods and nets on the walls; the tournament board by the door."], [("shelf", 1, 2, 3, 1, "rods")])
    R["pointe_rouge_ice_plant"] = {
        "title": "Old Ice Plant", "subtitle": "Pointe Rouge · abandoned · the cold room (post-game)",
        "size": (19, 14), "floor": "stone",
        "shapes": [("metal", 1, 2, 4, 3, "compressor"), ("metal", 14, 2, 4, 3, "compressor"),
                   ("tank", 7, 2, 5, 2, "brine tanks"), ("counter", 1, 7, 5, 1, "ice blocks"),
                   ("wall", 10, 6, 1, 6), ("tank", 12, 7, 6, 4, "cold room"), ("rug", 8, 12, 3, 1)],
        "markers": [("switch", 3, 5, "Compressor valve (post-game: restart the plant)"),
                    ("switch", 15, 5, "Compressor valve"),
                    ("event", 14, 9, "Post-game: ARTICUNO in the cold room once the plant runs"),
                    ("mega", 16, 8, "Crabominite (cold room, post-game)")],
        "notes": ["Locked until the post-game; restarting both compressors freezes the cold room."],
        "exits": [(9, 13, "Exit")]}
    R["pointe_rouge_refinery"] = {
        "title": "Refinery", "subtitle": "Pointe Rouge · Camille's sabotage (Jayden battle 3) · before the gym",
        "size": (23, 17), "floor": "stone",
        "shapes": [("metal", 2, 2, 3, 5, "tank"), ("metal", 18, 2, 3, 5, "tank"), ("counter", 6, 4, 11, 1, "pipes"),
                   ("counter", 6, 9, 11, 1, "pipes"), ("metal", 8, 11, 7, 2, "control\nroom"), ("rug", 10, 15, 3, 1)],
        "markers": [("switch", 7, 5, "Valve: shut to stop the leak"), ("switch", 15, 5, "Valve"),
                    ("switch", 7, 10, "Valve"), ("switch", 15, 10, "Valve"),
                    ("trainer", 11, 7, "Grunt (Poison)"), ("trainer", 4, 12, "Grunt (Ground)"),
                    ("event", 11, 13, "CAMILLE at the controls, JAYDEN beside her: Jayden battle 3, then Camille"),
                    ("item", 20, 14, "Item: Smoke Ball")],
        "notes": ["Team Blacksnake opens the valves to flood the marsh with runoff; shut them all to reach the control room.",
                  "Jayden's doubts show for the first time here (Isaac's seed)."],
        "exits": [(11, 16, "Exit")]}
    R["pointe_rouge_house_nw"] = house(
        "House (north-west)", "Pointe Rouge · a refinery family",
        [("npc", 3, 4, "Father: forty years at the refinery, never seen a leak like that"),
         ("npc", 7, 5, "Daughter: wants to be a Bird Keeper like KINGFISHER")],
        ["Ordinary house; a hard hat on the hook."])
    R["pointe_rouge_house_ne"] = house(
        "House (north-east)", "Pointe Rouge · the move reminder",
        [("service", 5, 4, "Move reminder: re-teaches forgotten moves for a Heart Scale")],
        ["Quiet house; old trophies on the shelves."])
    R["pointe_rouge_house_s"] = house(
        "House (south)", "Pointe Rouge · Weezing fan",
        [("npc", 4, 4, "Man: the smokestack yard has a strange stone (Weezingite, post-game)")],
        ["Ordinary house by the rail yards."])
    R["pointe_rouge_gym"] = {
        "title": "Pointe Rouge Gym: Riverfront Boathouse", "subtitle": "Gym 4 · Kingfisher (Tailwind Flying)",
        "size": (21, 16), "floor": "wood",
        "shapes": [("water", 1, 2, 5, 9, "boat slip"), ("water", 15, 2, 5, 9, "boat slip"),
                   ("stage", 8, 2, 5, 2, "Kingfisher's\nrafters"), ("counter", 7, 7, 7, 1, "net racks"),
                   ("metal", 6, 11, 1, 1, "fan"), ("metal", 14, 11, 1, 1, "fan"), ("rug", 9, 14, 3, 1)],
        "markers": [("npc", 10, 2, "KINGFISHER: Fearow (osprey form), Doduo, Golbat, Scyther, Corvisquire"),
                    ("trainer", 7, 5, "Trainer: Bird Keeper"), ("trainer", 13, 9, "Trainer: Fisherman"),
                    ("event", 10, 12, "Fans set up a tailwind across the boathouse (flavour)"),
                    ("npc", 12, 14, "Gym guide: no battle until you've won the fishing tournament")],
        "notes": ["Trial: the fishing tournament on Route 5; Kingfisher won't battle until the player wins it.",
                  "Reward: the fourth verse, a Flying TM and the Super Rod."],
        "exits": [(10, 15, "Exit")]}

    # ================================================================ Camp Cocodrie (gym 5, the brothers)
    R["camp_cocodrie_gym"] = {
        "title": "Camp Cocodrie Gym: the Brothers' Cookhouse", "subtitle": "Gym 5 · Boudreaux and Thibodeaux · double battle",
        "size": (19, 14), "floor": "wood",
        "shapes": [("metal", 2, 2, 3, 2, "Boudreaux's\npot"), ("metal", 14, 2, 3, 2, "Thibodeaux's\npot"),
                   ("counter", 7, 3, 5, 1, "judging table"), ("counter", 1, 7, 4, 1, "spice shelf"),
                   ("counter", 14, 7, 4, 1, "prep table"), ("stage", 6, 8, 7, 3, "battle floor"), ("rug", 8, 12, 3, 1)],
        "markers": [("npc", 3, 4, "BOUDREAUX: Krokorok, Whiscash, Croagunk"),
                    ("npc", 15, 4, "THIBODEAUX: Foongus, Breloom, Crawdaunt (crawfish form)"),
                    ("event", 9, 2, "Judge the two pots: the right answer is a tie"),
                    ("npc", 10, 12, "Gym guide: bring andouille, shrimp, okra and filé")],
        "notes": ["Trial: the gumbo cook-off. Gather andouille, shrimp, okra and filé around the camp, then judge the "
                  "brothers' pots; calling it a tie starts the double battle.",
                  "Reward: the fifth verse and a Ground TM. The brothers' verse opens boat routes 10 and 11."],
        "exits": [(9, 13, "Exit")]}
    R["camp_cocodrie_nurse_cabin"] = {
        "title": "Nurse Cabin", "subtitle": "Camp Cocodrie · the camp's Pokémon Center",
        "size": (11, 9), "floor": "wood",
        "shapes": [("counter", 3, 3, 5, 1, "counter"), ("bed", 1, 5, 2, 1), ("bed", 8, 5, 2, 1), ("shelf", 8, 2, 2, 1, "PC")],
        "markers": [("heal", 5, 2, "Camp nurse: heals the party"),
                    ("event", 5, 6, "ISAAC lingers outside: a half-hearted battle before the gym")],
        "notes": ["A cabin in place of a full Center; same services."],
        "exits": [(5, 8, "Exit")]}
    R["camp_cocodrie_bait_shack"] = shop(
        "Bait Shack", "Camp Cocodrie", "bait, Dive and Net Balls, Super Potion, Antidote",
        [("npc", 7, 6, "Old-timer: the airboat dock's where the shrimp is")],
        ["Crawfish traps and coolers; no grass in camp, so fishing is the way."])
    R["camp_cocodrie_smokehouse"] = house(
        "Smokehouse", "Camp Cocodrie · sausage hanging from the rafters",
        [("npc", 4, 4, "Smoker: gives the andouille for the cook-off if you help stoke the fire"),
         ("item", 8, 6, "Andouille (trial ingredient)")],
        ["Racks of sausage and a smoker in the corner."], extra=[("metal", 8, 2, 2, 2, "smoker")])
    R["camp_cocodrie_dance_porch"] = {
        "title": "Dance Porch", "subtitle": "Camp Cocodrie · zydeco on Saturday night",
        "size": (15, 10), "floor": "wood",
        "shapes": [("stage", 4, 2, 7, 2, "bandstand"), ("rug", 4, 5, 7, 3, "dance floor"), ("counter", 1, 4, 2, 3, "benches"),
                   ("counter", 12, 4, 2, 3, "benches")],
        "markers": [("npc", 7, 2, "Zydeco band (night): gives the Exploudite after gym 6"),
                    ("npc", 5, 6, "Dancer: the accordion player came from ISLE MARAIS"),
                    ("npc", 13, 5, "Old neighbour's son: grandma has filé, if you ask nicely")],
        "notes": ["Open-sided porch; the band only plays at night.", "Echoes the Isle Marais dance hall and its accordion."],
        "exits": [(7, 9, "Exit")]}
    R["camp_cocodrie_cabin_1"] = house(
        "Stilt Cabin (west)", "Camp Cocodrie · the old neighbour",
        [("npc", 4, 4, "Old neighbour: gives the filé powder for the cook-off"), ("item", 8, 3, "Filé (trial ingredient)")],
        ["Herbs drying over the stove."])
    R["camp_cocodrie_cabin_2"] = house(
        "Stilt Cabin", "Camp Cocodrie · a gator wrangler",
        [("npc", 5, 4, "Wrangler: the gator pens hold Krokorok the brothers raised")],
        ["Ordinary cabin; leather gloves on the table."])
    R["camp_cocodrie_cabin_3"] = house(
        "Stilt Cabin (pond)", "Camp Cocodrie · the airboat captain",
        [("npc", 4, 4, "Captain: will take you round the bayou once the boat routes open")],
        ["Ordinary cabin overlooking the pond."])
    R["camp_cocodrie_cabin_4"] = house(
        "Stilt Cabin (east)", "Camp Cocodrie · okra growers",
        [("npc", 5, 4, "Gardener: pick okra from the garden out back (trial ingredient)")],
        ["Ordinary cabin; baskets of okra."])

    # ================================================================ Lutin's Hollow (gym 6, Lutin)
    R["lutins_hollow_gym"] = {
        "title": "Lutin's Hollow Gym: the Moss Curtains", "subtitle": "Gym 6 · Lutin (Fairy) · find the real Lutin",
        "size": (21, 16), "floor": "grass",
        "shapes": [("moss", 3, 2, 1, 6), ("moss", 7, 2, 1, 6), ("moss", 13, 2, 1, 6), ("moss", 17, 2, 1, 6),
                   ("water", 4, 9, 3, 2, "pool"), ("water", 9, 9, 3, 2, "pool"), ("water", 14, 9, 3, 2, "pool"),
                   ("flowers", 1, 13, 3, 1), ("flowers", 17, 13, 3, 1), ("rug", 9, 14, 3, 1)],
        "markers": [("npc", 5, 4, "A Lutin: no reflection in the pool"), ("npc", 10, 4, "A Lutin: no reflection"),
                    ("npc", 15, 4, "The real LUTIN: casts a reflection (Morgrem, Ribombee, Florges, Mismagius, Milotic, Delphox)"),
                    ("npc", 19, 6, "A Lutin: no reflection"),
                    ("trainer", 2, 11, "Trainer: Fairy Tale Girl"), ("trainer", 18, 11, "Trainer: Psychic"),
                    ("npc", 12, 14, "Gym guide: the water never lies")],
        "notes": ["Trial: find the real Lutin among illusions in the moss; only the real Lutin casts a reflection in "
                  "the still pools. Talking to a false one sends the player back through the curtains.",
                  "Reward: the sixth verse and a Fairy TM; then back to the Old Water for the cypress-wood charm."],
        "exits": [(10, 15, "Exit")]}
    R["lutins_hollow_pokecenter"] = {
        "title": "Pokémon Center (Hollow Tree)", "subtitle": "Lutin's Hollow · inside a great hollow cypress",
        "size": (13, 11), "floor": "wood",
        "shapes": [("wall", 1, 2, 2, 2), ("wall", 10, 2, 2, 2), ("wall", 1, 8, 1, 2), ("wall", 11, 8, 1, 2),
                   ("counter", 4, 3, 5, 1, "nurse counter"), ("shelf", 9, 5, 2, 1, "PC"), ("moss", 3, 6, 1, 1), ("rug", 5, 8, 3, 1)],
        "markers": [("heal", 6, 2, "Nurse: heals the party"), ("npc", 3, 7, "Traveller: the moss moves when nobody's looking")],
        "notes": ["Round, root-lined walls (the corners are roots); otherwise a normal Center."],
        "exits": [(6, 10, "Exit")]}
    R["lutins_hollow_herbalist"] = shop(
        "Herbalist", "Lutin's Hollow · bitter medicine that works",
        "Heal Powder, Energy Powder, Energy Root, Revival Herb",
        [("npc", 8, 6, "Apprentice: the Floette seed is for later (post-game quest)")],
        ["Herbs hang from every beam; jars on the shelves."], [("plant", 1, 2, 3, 1)])
    R["lutins_hollow_moss_house_n"] = house(
        "Moss House (north)", "Lutin's Hollow · a riddler",
        [("npc", 5, 4, "Riddler: answer three riddles for the Delphoxite (after the gym)")],
        ["Moss-hung walls; a reading chair."])
    R["lutins_hollow_moss_house_s"] = house(
        "Moss House (south)", "Lutin's Hollow · by the path in",
        [("npc", 4, 4, "Woman: heard singing by the pools last night (Jayden battle 4 and Wren's song happen outside)")],
        ["Ordinary moss house near the entrance."])

    # ================================================================ Redfield (gym 7, Cayenne)
    R["redfield_gym"] = {
        "title": "Redfield Gym: the Sugar Mill", "subtitle": "Gym 7 · Cayenne (Sun) · the trial is the mill yard outside",
        "size": (21, 16), "floor": "stone",
        "shapes": [("metal", 1, 2, 4, 4, "rollers"), ("metal", 16, 2, 4, 4, "rollers"), ("metal", 7, 2, 7, 1, "boiling pans"),
                   ("stage", 8, 4, 5, 2, "Cayenne's\nfurnace floor"), ("counter", 3, 9, 5, 1, "cane"), ("counter", 13, 9, 5, 1, "cane"),
                   ("rug", 9, 14, 3, 1)],
        "markers": [("npc", 10, 4, "CAYENNE: Scovillain, Weezing, Ninetales, Hisuian Lilligant, Charizard (Mega), Rotom-Heat"),
                    ("trainer", 5, 11, "Trainer: Kindler"), ("trainer", 15, 11, "Trainer: Cane cutter"),
                    ("event", 10, 8, "Harsh sunlight all battle (Ninetales' Drought / Mega Charizard Y)"),
                    ("npc", 12, 14, "Gym guide: the mill only opens once the sundials are lit")],
        "notes": ["Trial (outside, by day): turn mirrors to bounce sunlight onto the sundials in order; each lit sundial "
                  "opens a gate to the mill.",
                  "Reward: the seventh verse, a Fire TM and the Charizardite.",
                  "Rita's battle at the mill comes first: her Mega Chandelure is the player's first Mega opponent."],
        "exits": [(10, 15, "Exit")]}
    R["redfield_ritas_office"] = {
        "title": "Rita's Office", "subtitle": "Redfield · Team Blacksnake recruitment, in the mill yard",
        "size": (11, 9), "floor": "carpet",
        "shapes": [("counter", 3, 3, 4, 1, "desk"), ("shelf", 1, 2, 2, 2, "files"), ("screen", 8, 2, 2, 1, "map")],
        "markers": [("npc", 5, 2, "RITA (before the gym): battles outside the mill with Mega Chandelure"),
                    ("event", 9, 3, "Wall map: recruitment drives in every flooded town"),
                    ("mega", 2, 6, "Chandelurite (post-game, after Rita abandons the team)")],
        "notes": ["Pamphlets about the 'murdered serpent' stacked by the door."],
        "exits": [(5, 8, "Exit")]}
    R["redfield_pokecenter"] = center(
        "Pokémon Center", "Redfield",
        [("npc", 2, 5, "Cane cutter: the mill's been running day and night"),
         ("npc", 12, 5, "Hiker: the dry country north of here is going to dust")])
    R["redfield_mart"] = shop(
        "Poké Mart", "Redfield", "Hyper Potion, Full Heal, Ultra Ball, Burn Heal, Max Repel")
    R["redfield_bottling_works"] = {
        "title": "Pepper-Sauce Bottling Works", "subtitle": "Redfield · conveyor belts and bottles",
        "size": (19, 12), "floor": "stone",
        "shapes": [("metal", 2, 3, 15, 1, "conveyor"), ("metal", 2, 7, 15, 1, "conveyor"),
                   ("tank", 1, 9, 3, 2, "pepper vats"), ("counter", 14, 9, 4, 1, "crates"), ("rug", 8, 10, 3, 1)],
        "markers": [("npc", 5, 5, "Foreman: the hottest batch in years since the drought"),
                    ("npc", 13, 5, "Taster: gives a Spicy Berry blend (Tamato Berries)"),
                    ("item", 16, 10, "Item: Charcoal")],
        "notes": ["The Scovillainite is outside by the loading door (town mockup)."],
        "exits": [(9, 11, "Exit")]}
    R["redfield_shotgun_house_1"] = {
        "title": "Shotgun House", "subtitle": "Redfield · one room behind the next",
        "size": (6, 15), "floor": "wood", "door": 2,
        "shapes": [("shelf", 1, 2, 2, 1, "stove"), ("bed", 3, 2, 2, 2), ("counter", 1, 6, 2, 1, "table"),
                   ("wall", 1, 9, 2, 1), ("wall", 4, 9, 1, 1), ("counter", 3, 11, 2, 1, "chairs")],
        "markers": [("npc", 2, 7, "Grandmother: the cane fields were greener before the storm"),
                    ("npc", 3, 12, "Grandson: wants a Charmander more than anything")],
        "notes": ["A narrow shotgun house: rooms in a line, doors aligned front to back."],
        "exits": [(2, 14, "Exit")]}
    R["redfield_shotgun_house_2"] = {
        "title": "Shotgun House", "subtitle": "Redfield · the sundial keeper",
        "size": (6, 15), "floor": "wood", "door": 2,
        "shapes": [("shelf", 1, 2, 4, 1, "almanacs"), ("counter", 1, 6, 2, 1, "desk"), ("wall", 1, 9, 2, 1),
                   ("wall", 4, 9, 1, 1), ("bed", 3, 11, 2, 2)],
        "markers": [("npc", 2, 7, "Sundial keeper: explains the mirror trial (hint: east to west)")],
        "notes": ["Almanacs and sun charts; the great sundial is across the street."],
        "exits": [(2, 14, "Exit")]}
    R["redfield_house_1"] = house(
        "House", "Redfield · a pepper farmer",
        [("npc", 4, 4, "Farmer: the pepper rows love this heat"), ("item", 8, 6, "Item: Tamato Berry")],
        ["Ordinary house; strings of dried peppers."])
    R["redfield_house_2"] = house(
        "House", "Redfield · the Hearthflame rumour",
        [("npc", 5, 4, "Boy: there's a mask in the mill yard that glows (Hearthflame Mask, post-game)")],
        ["Ordinary house."])

    # ================================================================ Land's End (gym 8, Heron)
    R["lands_end_gym"] = {
        "title": "Land's End Gym: the Rain Pavilion", "subtitle": "Gym 8 · Heron (Rain) · arrange the seven verses",
        "size": (21, 16), "floor": "wood",
        "shapes": [("water", 1, 2, 19, 1), ("stage", 8, 3, 5, 2, "Heron's\nplatform"),
                   ("shelf", 2, 7, 2, 1, "panel"), ("shelf", 5, 7, 2, 1, "panel"), ("shelf", 8, 7, 2, 1, "panel"),
                   ("shelf", 11, 7, 2, 1, "panel"), ("shelf", 14, 7, 2, 1, "panel"), ("shelf", 17, 7, 2, 1, "panel"),
                   ("shelf", 9, 10, 3, 1, "panel"), ("water", 1, 12, 3, 2), ("water", 17, 12, 3, 2), ("rug", 9, 14, 3, 1)],
        "markers": [("npc", 10, 3, "HERON: Pelipper, Politoed, Archaludon, Floatzel, Gyarados (Mega), Seismitoad"),
                    ("switch", 3, 8, "Carved verse panel: slide into the order of the true telling"),
                    ("switch", 10, 11, "The seventh panel"),
                    ("event", 10, 6, "When the order is right the rain pauses and the heron carvings reveal the final verse"),
                    ("trainer", 4, 12, "Trainer: Swimmer"), ("trainer", 16, 12, "Trainer: Fisherman"),
                    ("npc", 12, 14, "Gym guide: you've heard every verse; now put them in order")],
        "notes": ["Trial: arrange the seven carved verse panels in the order of the true telling (the player has heard them all).",
                  "Reward: the final verse, a Water TM, the Gyaradosite and the Diving Gear. Winning opens Route 21.",
                  "After the gym: Andrew hears the whole telling and rejects it; Jayden battle 5; then Rayquaza wakes."],
        "exits": [(10, 15, "Exit")]}
    R["lands_end_pokecenter"] = center(
        "Pokémon Center", "Land's End · on pilings over the water",
        [("npc", 2, 5, "Shrimper: the Gulf's been strange since the temple lights came on"),
         ("npc", 12, 5, "Hiker: the last stop before the open Gulf")])
    R["lands_end_marine_supply"] = shop(
        "Marine Supply", "Land's End", "Dive Balls, Max Repel, Max Potion, Full Restore",
        [("npc", 7, 6, "Diver: the Drowned Temple's door won't open for just anyone")],
        ["Anchors, rope and wetsuits; the Diving Gear itself comes from Heron."])
    R["lands_end_lookout"] = {
        "title": "Lookout", "subtitle": "Land's End · a watchtower over the delta and the Gulf",
        "size": (9, 9), "floor": "wood",
        "shapes": [("glass", 1, 2, 7, 1, "windows"), ("metal", 4, 3, 1, 1), ("stage", 1, 5, 2, 2, "stairs")],
        "markers": [("event", 4, 4, "Telescope: a ring of calm water out in the Gulf (the Drowned Temple)"),
                    ("npc", 6, 5, "Watchman: logs every storm since he was a boy")],
        "notes": ["Hints at the Drowned Temple off Route 22 before the player has the Diving Gear."],
        "exits": [(4, 8, "Exit")]}
    R["lands_end_weather_station"] = {
        "title": "Tide Gauge and Weather Station", "subtitle": "Land's End · forecasts and tide charts",
        "size": (13, 9), "floor": "tile",
        "shapes": [("metal", 1, 2, 3, 2, "instruments"), ("screen", 5, 2, 4, 1, "radar"), ("counter", 9, 4, 3, 1, "desk"),
                   ("tank", 1, 6, 2, 1, "tide\ngauge")],
        "markers": [("npc", 10, 3, "Forecaster: tells the day's weather in each region (useful for Rain and Sun teams)"),
                    ("npc", 4, 5, "Scientist: the pressure drops every time the Gulf glows")],
        "notes": ["A weather service: checks which routes have rain or sun today."],
        "exits": [(6, 8, "Exit")]}
    for name, sub, npc in (
            ("lands_end_house_1", "a shrimping family", "Shrimper: the boats go out at dawn, storm or not"),
            ("lands_end_house_2", "the heron watcher", "Birdwatcher: the herons on Route 20 nest in the old pilings"),
            ("lands_end_house_3", "Andrew's arrival", "Woman: a man in a black coat asked about the Rain Pavilion (story event 2 outside)"),
            ("lands_end_house_4", "an old diver", "Old diver: the temple was on dry land when my grandfather was young"),
            ("lands_end_house_5", "in-game trade", "Trader: swaps a Relicanth for a Clamperl")):
        R[name] = house("House on Pilings", f"Land's End · {sub}", [("npc", 5, 4, npc)],
                        ["Ordinary house on stilts; the floor creaks with the tide."])
    # ================================================================ the finale's two raid arenas (Chapter 9: scripted warps, no street door)
    R["lands_end_drowned_temple"] = {
        "title": "Drowned Temple: the Tide Hall", "subtitle": "Off Route 22 · reached by diving · Kyogre's raid arena",
        "size": (17, 15), "floor": "stone",
        "shapes": [("wall", 1, 7, 7, 4, "temple wall"), ("wall", 9, 7, 7, 4, "temple wall"),
                   ("water", 2, 2, 13, 1, "the Tide Hall's water"), ("metal", 3, 4, 1, 2, "sea pillar"), ("metal", 13, 4, 1, 2, "land pillar"),
                   ("rug", 7, 12, 3, 1)],
        "markers": [("npc", 8, 8, "The sealed door: opens when the player sings Heron's verse"),
                    ("npc", 8, 3, "Kyogre (raid)")],
        "notes": ["Primordial Sea is active for the whole fight. Reached with the Diving Gear from the end of Route 22."],
        "exits": [(8, 14, "Exit")]}
    R["lands_end_salt_cathedral"] = {
        "title": "Salt Cathedral", "subtitle": "Below Route 24 · the old salt mine · Groudon's raid arena",
        "size": (21, 17), "floor": "stone",
        "shapes": [("metal", 3, 3, 2, 2, "salt pillar"), ("metal", 8, 3, 2, 2, "salt pillar"), ("metal", 14, 3, 2, 2, "salt pillar"),
                   ("metal", 3, 8, 2, 2, "salt pillar"), ("metal", 8, 8, 2, 2, "salt pillar"), ("metal", 14, 8, 2, 2, "salt pillar"),
                   ("rug", 9, 15, 3, 1)],
        "markers": [("npc", 10, 3, "Groudon (raid)")],
        "notes": ["Desolate Land is active for the whole fight. The cracked shaft from Route 24; the Lantern lights the way."],
        "exits": [(10, 16, "Exit")]}
    return R

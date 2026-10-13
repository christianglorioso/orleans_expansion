"""The Orleans achievement table (100 trophies from orleans_achievements.xlsx). Source of truth for src/data/achievements.h and
include/constants/achievements.h (run tools/achievements/gen_achievements.py). Rewards live in src/data/achievement_rewards.h (hand-edited).

Row: (num, category, KEY, name, how_to_earn, trigger, tier, status)
  num      the sheet's row number. enum id = num - 1 and NEVER changes (it is the bit position in the save).
  trigger  ("story", n)              VAR_ORLEANS_STORY >= n
           ("flag", "FLAG_X")        a story flag / badge flag
           ("varge", "VAR_X", n)     a var >= n
           ("dex", "SPECIES_X")      species caught in the Pokedex
           ("dexcount", n)           n species caught (national count, Lafayette's tally)
           ("stat", "GAME_STAT_X", n)
           ("pred", "Fn")            a C predicate Achievement_PredicateFn in achievements.c
           ("manual",)               unlocked by a hook / script special (Achievement_Unlock)
           ("soon",)                 the feature does not exist yet: shown as "coming soon", never unlocks
  tier     0 Poke Ball icon .. 3 Master Ball icon (a visual rank only)
  status   live | hook (needs a hook, wired) | soon | revise (wording changed from the sheet, for the user's review)
Text: name <= 24 characters, how-to <= 2 lines of 38 (the generator wraps it)."""

POKE, GREAT, ULTRA, MASTER = 0, 1, 2, 3

ROWS = [
    (1, "Story", "WELCOME_TO_CRESCENT_CITY", "Welcome to Crescent City", "Reach Crescent City for the first time, after Éclair.", ("story", 13), POKE, "live"),
    (2, "Story", "TRUST_EARNED", "Trust Earned", "Earn the Rootkin's trust and open the way to the Old Water.", ("story", 6), POKE, "live"),
    (3, "Story", "MAGNOLIAS_GARDEN", "Magnolia's Garden", "Finish the garden puzzle in Grand Oak.", ("manual",), POKE, "hook"),
    (4, "Story", "ECLAIRS_GRID", "Éclair's Grid", "Restore the power grid in Storm's Edge.", ("flag", "FLAG_STORMS_EDGE_GRID_RESTORED"), POKE, "live"),
    (5, "Story", "FIFOLETS_MAZE", "Fifolet's Maze", "Find your way through the cemetery maze of feu follet lights.", ("manual",), POKE, "hook"),
    (6, "Story", "KINGFISHERS_TOURNAMENT", "Kingfisher's Tournament", "Win the fishing tournament near Pointe Rouge.", ("flag", "FLAG_POINTE_TOURNEY_WON"), POKE, "live"),
    (7, "Story", "THE_BROTHERS_GUMBO", "The Brothers' Gumbo", "Settle the gumbo cook-off Boudreaux and Thibodeaux bicker over.", ("story", 25), POKE, "revise"),
    (8, "Story", "LUTINS_MIRAGE", "Lutin's Mirage", "Find the real Lutin among the illusions in the moss.", ("manual",), POKE, "hook"),
    (9, "Story", "CAYENNES_LIGHT", "Cayenne's Light", "Solve the mirrors and sundials in Redfield's sugar mill yard.", ("flag", "FLAG_REDFIELD_MILL_OPEN"), POKE, "live"),
    (10, "Story", "HERONS_TELLING", "Heron's Telling", "Arrange the seven verses in order to reveal the last one.", ("flag", "FLAG_HERON_TRIAL_DONE"), POKE, "live"),
    (11, "Story", "DEFEAT_MAGNOLIA", "Defeat Magnolia", "Defeat Magnolia in battle.", ("flag", "FLAG_BADGE01_GET"), GREAT, "live"),
    (12, "Story", "DEFEAT_ECLAIR", "Defeat Éclair", "Defeat Éclair in battle.", ("flag", "FLAG_BADGE02_GET"), GREAT, "live"),
    (13, "Story", "DEFEAT_FIFOLET", "Defeat Fifolet", "Defeat Fifolet in battle.", ("flag", "FLAG_BADGE03_GET"), GREAT, "live"),
    (14, "Story", "DEFEAT_KINGFISHER", "Defeat Kingfisher", "Defeat Kingfisher in battle.", ("flag", "FLAG_BADGE04_GET"), GREAT, "live"),
    (15, "Story", "DEFEAT_THE_BROTHERS", "Defeat the Brothers", "Defeat Boudreaux and Thibodeaux in the double battle.", ("flag", "FLAG_BADGE05_GET"), GREAT, "live"),
    (16, "Story", "DEFEAT_LUTIN", "Defeat Lutin", "Defeat Lutin in battle.", ("flag", "FLAG_BADGE06_GET"), GREAT, "live"),
    (17, "Story", "DEFEAT_CAYENNE", "Defeat Cayenne", "Defeat Cayenne in battle.", ("flag", "FLAG_BADGE07_GET"), GREAT, "live"),
    (18, "Story", "DEFEAT_HERON", "Defeat Heron", "Defeat Heron in battle.", ("flag", "FLAG_BADGE08_GET"), GREAT, "live"),
    (19, "Story", "THE_CHARM", "The Charm", "Receive the cypress-wood charm from Tupelo after the sixth gym.", ("flag", "FLAG_RECEIVED_CYPRESS_CHARM"), ULTRA, "live"),
    (20, "Story", "CALM_THE_SERPENT", "Calm the Serpent", "Complete the game: calm Rayquaza and see the credits.", ("story", 44), MASTER, "live"),
    (21, "Battle", "TIDE_TURNER", "Tide Turner", "Defeat primal Kyogre in a raid.", ("flag", "FLAG_KYOGRE_CALMED"), GREAT, "live"),
    (22, "Battle", "EARTH_SHAKER", "Earth Shaker", "Defeat primal Groudon in a raid.", ("flag", "FLAG_GROUDON_CALMED"), GREAT, "live"),
    (23, "Battle", "UNBROKEN", "Unbroken", "Win the Rayquaza raid without any of your Pokémon fainting.", ("manual",), ULTRA, "hook"),
    (24, "Battle", "BOND_BEYOND_LIMITS", "Bond Beyond Limits", "Mega Evolve a Pokémon for the first time.", ("manual",), GREAT, "hook"),
    (25, "Battle", "CAMILLE_FALLS", "Camille Falls", "Defeat Camille, the Zealot.", ("pred", "CamilleDefeated"), GREAT, "live"),
    (26, "Battle", "RITA_FALLS", "Rita Falls", "Defeat Rita, the Opportunist.", ("flag", "FLAG_REDFIELD_RITA_BEATEN"), GREAT, "live"),
    (27, "Battle", "ANDREWS_END", "Andrew's End", "Defeat Andrew, Team Blacksnake's leader.", ("pred", "AndrewDefeated"), GREAT, "live"),
    (28, "Battle", "SAILORS_CHALLENGE", "Defeat a Sailor", "Defeat any sailor who challenges you.", ("pred", "SailorDefeated"), POKE, "revise"),
    (29, "Battle Frontier", "BATTLE_TOWER_STREAK", "Battle Tower Streak", "Win 21 battles in a row at the Battle Tower.", ("pred", "TowerStreak"), ULTRA, "live"),
    (30, "Battle Frontier", "BATTLE_DOME_STREAK", "Battle Dome Streak", "Win 21 battles in a row at the Battle Dome.", ("pred", "DomeStreak"), ULTRA, "live"),
    (31, "Battle Frontier", "BATTLE_PALACE_STREAK", "Battle Palace Streak", "Win 21 battles in a row at the Battle Palace.", ("pred", "PalaceStreak"), ULTRA, "live"),
    (32, "Battle Frontier", "BATTLE_ARENA_STREAK", "Battle Arena Streak", "Win 21 battles in a row at the Battle Arena.", ("pred", "ArenaStreak"), ULTRA, "live"),
    (33, "Battle Frontier", "BATTLE_FACTORY_STREAK", "Battle Factory Streak", "Win 21 battles in a row at the Battle Factory.", ("pred", "FactoryStreak"), ULTRA, "live"),
    (34, "Battle Frontier", "BATTLE_PIKE_STREAK", "Battle Pike Streak", "Win 21 battles in a row at the Battle Pike.", ("pred", "PikeStreak"), ULTRA, "live"),
    (35, "Battle Frontier", "BATTLE_PYRAMID_STREAK", "Battle Pyramid Streak", "Win 21 battles in a row at the Battle Pyramid.", ("pred", "PyramidStreak"), ULTRA, "live"),
    (36, "Battle Frontier", "FRONTIER_LEGEND", "Frontier Legend", "Earn a win streak at every battle center.", ("pred", "AllFrontierStreaks"), MASTER, "live"),
    (37, "Conservation", "COMPLETE_THE_POKEDEX", "Complete the Pokédex", "Register every species of the Orleans Pokédex.", ("pred", "BaseDexComplete"), MASTER, "live"),
    (38, "Conservation", "A_PLACE_OF_YOUR_OWN", "A Place of Your Own", "Earn your apartment through Professor Lafayette's project.", ("flag", "FLAG_APARTMENT_UNLOCKED"), GREAT, "live"),
    (39, "Conservation", "ZOO_BAYOU_AND_SWAMP", "Zoo: Bayou and Swamp", "Fill the zoo's bayou and swamp habitat.", ("soon",), GREAT, "soon"),
    (40, "Conservation", "ZOO_MOSS_FOREST", "Zoo: Moss Forest", "Fill the zoo's moss forest habitat.", ("soon",), GREAT, "soon"),
    (41, "Conservation", "ZOO_CITY_AND_CEMETERY", "Zoo: City and Cemetery", "Fill the zoo's city and cemetery habitat.", ("soon",), GREAT, "soon"),
    (42, "Conservation", "ZOO_SALT_HILLS_AND_CAVES", "Zoo: Salt Hills, Caves", "Fill the zoo's salt hills and caves habitat.", ("soon",), GREAT, "soon"),
    (43, "Conservation", "ZOO_COAST_AND_GULF", "Zoo: Coast and Gulf", "Fill the zoo's coast and Gulf habitat.", ("soon",), GREAT, "soon"),
    (44, "Conservation", "ZOO_CANE_AND_PEPPER_FIELDS", "Zoo: Cane and Pepper", "Fill the zoo's cane and pepper fields habitat.", ("soon",), GREAT, "soon"),
    (45, "Conservation", "A_FULL_ZOO", "A Full Zoo", "Fill every habitat in the zoo.", ("soon",), ULTRA, "soon"),
    (46, "Conservation", "A_FULL_AQUARIUM", "A Full Aquarium", "Fill the aquarium.", ("soon",), ULTRA, "soon"),
    (47, "Conservation", "CAUSE_I", "40 for the Cause", "Have 40 species registered as caught.", ("dexcount", 40), GREAT, "revise"),
    (48, "Conservation", "CAUSE_II", "75 for the Cause", "Have 75 species registered as caught.", ("dexcount", 75), GREAT, "revise"),
    (49, "Conservation", "CAUSE_III", "120 for the Cause", "Have 120 species registered as caught.", ("dexcount", 120), ULTRA, "revise"),
    (50, "Conservation", "BACK_FROM_THE_PAST", "Back from the Past", "Revive the fossil from the Route 19 tidal flats.", ("flag", "FLAG_KABUTO_REVIVED"), GREAT, "live"),
    (51, "Conservation", "SOMETHING_HATCHED", "Something Hatched", "Hatch your first Egg.", ("stat", "GAME_STAT_HATCHED_EGGS", 1), POKE, "revise"),
    (52, "Exploration", "FIRST_WAVE", "First Wave", "Learn to Surf and take to the water.", ("flag", "FLAG_RECEIVED_HM_SURF"), POKE, "revise"),
    (53, "Exploration", "ALL_ABOARD", "All Aboard", "Ride the riverboat from Crescent City to Pointe Rouge.", ("story", 18), POKE, "live"),
    (54, "Exploration", "INTO_THE_BASIN", "Into the Basin", "Reach Camp Cocodrie.", ("story", 23), POKE, "revise"),
    (55, "Exploration", "ACROSS_THE_LAKE", "Across the Lake", "Reach Lutin's Hollow.", ("story", 27), POKE, "revise"),
    (56, "Exploration", "DELTA_BOUND", "Delta Bound", "Reach Land's End.", ("story", 35), POKE, "revise"),
    (57, "Exploration", "THE_OPEN_GULF", "The Open Gulf", "Enter Kyogre's drowned temple across the Gulf.", ("pred", "TempleVisited"), GREAT, "revise"),
    (58, "Exploration", "LAND_HO", "Land Ho", "Find your first optional island.", ("soon",), POKE, "soon"),
    (59, "Exploration", "ISLAND_HOPPER", "Island Hopper", "Find every optional island.", ("soon",), GREAT, "soon"),
    (60, "Exploration", "THE_OLD_WATER", "The Old Water", "Discover the Old Water.", ("story", 5), POKE, "live"),
    (61, "Exploration", "SHRINE_SEEKER", "Shrine Seeker", "Discover all six Rootkin shrines.", ("pred", "ShrinesVisited"), GREAT, "hook"),
    (62, "Exploration", "EVERY_ROUTE", "Every Route", "Visit all 25 routes.", ("pred", "RoutesVisited"), GREAT, "hook"),
    (63, "Exploration", "EVERY_CORNER", "Every Corner", "Step inside every building in Crescent City.", ("pred", "CrescentVisited"), GREAT, "hook"),
    (64, "Craft and culture", "ORDER_UP", "Order Up", "Blend your first Pokéblock at the café.", ("soon",), POKE, "soon"),
    (65, "Craft and culture", "BEST_FRIENDS", "Best Friends", "Max a Pokémon's friendship at the salon.", ("manual",), GREAT, "hook"),
    (66, "Craft and culture", "A_NAME_OF_ITS_OWN", "A Name of Its Own", "Nickname a Pokémon with the Name Rater.", ("manual",), POKE, "hook"),
    (67, "Craft and culture", "LESSONS_LEARNED", "Lessons Learned", "Learn a move from the move tutor.", ("manual",), POKE, "hook"),
    (68, "Craft and culture", "TRAINING_DAY", "Training Day", "Use an EV changer.", ("manual",), POKE, "hook"),
    (69, "Craft and culture", "BORN_READY", "Born Ready", "Use an IV changer.", ("manual",), POKE, "hook"),
    (70, "Craft and culture", "FIRST_TOUCH", "First Touch", "Place your first decoration in your apartment.", ("soon",), POKE, "soon"),
    (71, "Craft and culture", "MAKE_IT_HOME", "Make It Home", "Place 20 decorations in your apartment.", ("soon",), GREAT, "soon"),
    (72, "Craft and culture", "SPARK_IN_THE_HOUSE", "Spark in the House", "Catch every appliance Rotom in Crescent City.", ("pred", "AllApplianceRotoms"), GREAT, "revise"),
    (73, "Craft and culture", "THE_WHOLE_TELLING", "The Whole Telling", "Learn all eight verses.", ("varge", "VAR_OLD_WATER_TELLING", 2), ULTRA, "live"),
    (74, "Craft and culture", "WRENS_FRIEND", "Wren's Friend", "Complete a quest for Wren.", ("flag", "FLAG_RECEIVED_ROCKRUFF"), POKE, "live"),
    (75, "Craft and culture", "A_RARE_CATCH", "A Rare Catch", "Catch a Feebas.", ("dex", "SPECIES_FEEBAS"), GREAT, "revise"),
    (76, "Collection", "LEGEND_RAYQUAZA", "Legend: Rayquaza", "Obtain Rayquaza.", ("dex", "SPECIES_RAYQUAZA"), MASTER, "live"),
    (77, "Collection", "LEGEND_KYOGRE", "Legend: Kyogre", "Obtain Kyogre.", ("dex", "SPECIES_KYOGRE"), ULTRA, "live"),
    (78, "Collection", "LEGEND_GROUDON", "Legend: Groudon", "Obtain Groudon.", ("dex", "SPECIES_GROUDON"), ULTRA, "live"),
    (79, "Collection", "LEGEND_UXIE", "Legend: Uxie", "Obtain Uxie at its Rootkin shrine.", ("dex", "SPECIES_UXIE"), ULTRA, "live"),
    (80, "Collection", "LEGEND_MESPRIT", "Legend: Mesprit", "Obtain Mesprit at its Rootkin shrine.", ("dex", "SPECIES_MESPRIT"), ULTRA, "live"),
    (81, "Collection", "LEGEND_AZELF", "Legend: Azelf", "Obtain Azelf at its Rootkin shrine.", ("dex", "SPECIES_AZELF"), ULTRA, "live"),
    (82, "Collection", "LEGEND_CELEBI", "Legend: Celebi", "Obtain Celebi at its Rootkin shrine.", ("dex", "SPECIES_CELEBI"), ULTRA, "live"),
    (83, "Collection", "LEGEND_ARTICUNO", "Legend: Articuno", "Obtain Articuno in Pointe Rouge's ice plant.", ("dex", "SPECIES_ARTICUNO"), ULTRA, "live"),
    (84, "Collection", "LEGEND_ARTICUNO_GALAR", "Legend: Galarian Articuno", "Obtain Galarian Articuno in the cathedral bell tower.", ("dex", "SPECIES_ARTICUNO_GALAR"), ULTRA, "live"),
    (85, "Collection", "LEGEND_ZAPDOS", "Legend: Zapdos", "Obtain Zapdos atop the Storm's Edge lighthouse.", ("dex", "SPECIES_ZAPDOS"), ULTRA, "live"),
    (86, "Collection", "LEGEND_ZAPDOS_GALAR", "Legend: Galarian Zapdos", "Obtain Galarian Zapdos in the Battle Frontier arena.", ("dex", "SPECIES_ZAPDOS_GALAR"), ULTRA, "live"),
    (87, "Collection", "LEGEND_MOLTRES", "Legend: Moltres", "Obtain Moltres at the Route 17 sugar mill chimney.", ("dex", "SPECIES_MOLTRES"), ULTRA, "live"),
    (88, "Collection", "LEGEND_MOLTRES_GALAR", "Legend: Galarian Moltres", "Obtain Galarian Moltres in the oldest crypt at night.", ("dex", "SPECIES_MOLTRES_GALAR"), ULTRA, "live"),
    (89, "Collection", "LEGEND_RAIKOU", "Legend: Raikou", "Obtain Raikou on the Route 2 transmission towers.", ("dex", "SPECIES_RAIKOU"), ULTRA, "live"),
    (90, "Collection", "LEGEND_ENTEI", "Legend: Entei", "Obtain Entei in the Route 16 pepper fields.", ("dex", "SPECIES_ENTEI"), ULTRA, "live"),
    (91, "Collection", "LEGEND_SUICUNE", "Legend: Suicune", "Obtain Suicune on the hidden island in the big lake.", ("dex", "SPECIES_SUICUNE"), ULTRA, "live"),
    (92, "Collection", "LEGEND_TORNADUS", "Legend: Tornadus", "Obtain Tornadus on Pointe Rouge's highest bridge span.", ("dex", "SPECIES_TORNADUS"), ULTRA, "live"),
    (93, "Collection", "LEGEND_THUNDURUS", "Legend: Thundurus", "Obtain Thundurus on the lightning-struck cypress island.", ("dex", "SPECIES_THUNDURUS"), ULTRA, "live"),
    (94, "Collection", "LEGEND_LANDORUS", "Legend: Landorus", "Obtain Landorus in the hidden hollow in the dry hills.", ("dex", "SPECIES_LANDORUS"), ULTRA, "live"),
    (95, "Collection", "LEGEND_ZARUDE", "Legend: Zarude", "Obtain Zarude in the overgrown moss forest grove.", ("dex", "SPECIES_ZARUDE"), ULTRA, "live"),
    (96, "Collection", "LEGEND_OGERPON", "Legend: Ogerpon", "Obtain Ogerpon and find the three other masks.", ("soon",), ULTRA, "soon"),
    (97, "Collection", "THE_BLOODMOON", "The Bloodmoon", "Find Ursaluna Bloodmoon, a one-off encounter.", ("dex", "SPECIES_URSALUNA_BLOODMOON"), ULTRA, "live"),
    (98, "Collection", "MIDNIGHT_WOLF", "Midnight Wolf", "Find Lycanroc Midnight, a one-off encounter.", ("dex", "SPECIES_LYCANROC_MIDNIGHT"), ULTRA, "live"),
    (99, "Collection", "SPARK_OF_LIFE", "Spark of Life", "Complete the quest for the base Rotom.", ("dex", "SPECIES_ROTOM"), GREAT, "live"),
    (100, "Collection", "FOREVER_FLOWER", "Forever Flower", "Complete the quest for Floette (Eternal Flower).", ("flag", "FLAG_RECEIVED_FLOETTE_EF"), GREAT, "live"),
]

CATEGORIES = ["Story", "Battle", "Battle Frontier", "Conservation", "Exploration", "Craft and culture", "Collection"]

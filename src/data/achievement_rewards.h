// ACHIEVEMENT REWARDS (placeholders). HAND-EDITED: this file is the one place to review and change what each trophy gives.
// Generated once by tools/achievements/gen_achievements.py --rewards; the generator never overwrites it unless asked.
//
// A reward is up to two item stacks plus money and Battle Points. It is given automatically when the unlock popup shows; if the bag is
// full, it waits and Lafayette (Conservation Center) hands it over. An empty line {} means no reward.
// Each row's comment shows what the sheet (orleans_achievements.xlsx) asked for. NOTE flags rewards that are placeholders because
// the sheet's reward (title, decoration, boat look, a choice menu, an undefined item) has no system behind it yet.

static const struct AchievementReward sAchievementRewards[ACHIEVEMENTS_MAX] =
{
    // #1 Welcome to Crescent City. Sheet: 3 Great Balls
    [ACH_WELCOME_TO_CRESCENT_CITY] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #2 Trust Earned. Sheet: 5 Revives
    [ACH_TRUST_EARNED] = { .item = ITEM_REVIVE, .qty = 5 },
    // #3 Magnolia's Garden. Sheet: 3 Heart Scales + PP Up
    [ACH_MAGNOLIAS_GARDEN] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #4 Éclair's Grid. Sheet: 3 Heart Scales + PP Up
    [ACH_ECLAIRS_GRID] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #5 Fifolet's Maze. Sheet: 3 Heart Scales + PP Up
    [ACH_FIFOLETS_MAZE] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #6 Kingfisher's Tournament. Sheet: 3 Heart Scales + PP Up
    [ACH_KINGFISHERS_TOURNAMENT] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #7 The Brothers' Gumbo. Sheet: 3 Heart Scales + PP Up
    [ACH_THE_BROTHERS_GUMBO] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #8 Lutin's Mirage. Sheet: 3 Heart Scales + PP Up
    [ACH_LUTINS_MIRAGE] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #9 Cayenne's Light. Sheet: 3 Heart Scales + PP Up
    [ACH_CAYENNES_LIGHT] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #10 Heron's Telling. Sheet: 3 Heart Scales + PP Up
    [ACH_HERONS_TELLING] = { .item = ITEM_HEART_SCALE, .qty = 3, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #11 Defeat Magnolia. Sheet: 5,000 money
    [ACH_DEFEAT_MAGNOLIA] = { .money = 5000 },
    // #12 Defeat Éclair. Sheet: 5,000 money
    [ACH_DEFEAT_ECLAIR] = { .money = 5000 },
    // #13 Defeat Fifolet. Sheet: 5,000 money
    [ACH_DEFEAT_FIFOLET] = { .money = 5000 },
    // #14 Defeat Kingfisher. Sheet: 5,000 money
    [ACH_DEFEAT_KINGFISHER] = { .money = 5000 },
    // #15 Defeat the Brothers. Sheet: 5,000 money
    [ACH_DEFEAT_THE_BROTHERS] = { .money = 5000 },
    // #16 Defeat Lutin. Sheet: 5,000 money
    [ACH_DEFEAT_LUTIN] = { .money = 5000 },
    // #17 Defeat Cayenne. Sheet: 5,000 money
    [ACH_DEFEAT_CAYENNE] = { .money = 5000 },
    // #18 Defeat Heron. Sheet: 5,000 money
    [ACH_DEFEAT_HERON] = { .money = 5000 },
    // #19 The Charm. Sheet: Title: Charmed  NOTE: COSMETIC, no system yet: placeholder item (titles do not exist yet)
    [ACH_THE_CHARM] = { .item = ITEM_RARE_CANDY, .qty = 1 },
    // #20 Calm the Serpent. Sheet: Title: Guardian of the Bayou + 100 Battle Points  NOTE: COSMETIC, no system yet: placeholder item for the title; the 100 BP are real
    [ACH_CALM_THE_SERPENT] = { .item = ITEM_RARE_CANDY, .qty = 1, .bp = 100 },
    // #21 Tide Turner. Sheet: 50 Battle Points
    [ACH_TIDE_TURNER] = { .bp = 50 },
    // #22 Earth Shaker. Sheet: 50 Battle Points
    [ACH_EARTH_SHAKER] = { .bp = 50 },
    // #23 Unbroken. Sheet: 100 Battle Points
    [ACH_UNBROKEN] = { .bp = 100 },
    // #24 Bond Beyond Limits. Sheet: Mega Stone of your choice  NOTE: needs a choice menu: placeholder item, replace with a fixed stone or an NPC claim
    [ACH_BOND_BEYOND_LIMITS] = { .item = ITEM_RARE_CANDY, .qty = 3 },
    // #25 Camille Falls. Sheet: 5,000 money
    [ACH_CAMILLE_FALLS] = { .money = 5000 },
    // #26 Rita Falls. Sheet: 5,000 money
    [ACH_RITA_FALLS] = { .money = 5000 },
    // #27 Andrew's End. Sheet: 10,000 money
    [ACH_ANDREWS_END] = { .money = 10000 },
    // #28 Defeat a Sailor. Sheet: 3 Super Potions
    [ACH_SAILORS_CHALLENGE] = { .item = ITEM_SUPER_POTION, .qty = 3 },
    // #29 Battle Tower Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_TOWER_STREAK] = { .bp = 25 },
    // #30 Battle Dome Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_DOME_STREAK] = { .bp = 25 },
    // #31 Battle Palace Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_PALACE_STREAK] = { .bp = 25 },
    // #32 Battle Arena Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_ARENA_STREAK] = { .bp = 25 },
    // #33 Battle Factory Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_FACTORY_STREAK] = { .bp = 25 },
    // #34 Battle Pike Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_PIKE_STREAK] = { .bp = 25 },
    // #35 Battle Pyramid Streak. Sheet: 25 Battle Points
    [ACH_BATTLE_PYRAMID_STREAK] = { .bp = 25 },
    // #36 Frontier Legend. Sheet: Title: Frontier Legend + 100 Battle Points  NOTE: COSMETIC, no system yet: placeholder item for the title; the 100 BP are real
    [ACH_FRONTIER_LEGEND] = { .item = ITEM_RARE_CANDY, .qty = 1, .bp = 100 },
    // #37 Complete the Pokédex. Sheet: Title: Master Naturalist + decoration set  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_COMPLETE_THE_POKEDEX] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #38 A Place of Your Own. Sheet: Apartment decoration pack  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_A_PLACE_OF_YOUR_OWN] = { .item = ITEM_NUGGET, .qty = 1 },
    // #39 Zoo: Bayou and Swamp. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_BAYOU_AND_SWAMP] = { .item = ITEM_NUGGET, .qty = 1 },
    // #40 Zoo: Moss Forest. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_MOSS_FOREST] = { .item = ITEM_NUGGET, .qty = 1 },
    // #41 Zoo: City and Cemetery. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_CITY_AND_CEMETERY] = { .item = ITEM_NUGGET, .qty = 1 },
    // #42 Zoo: Salt Hills, Caves. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_SALT_HILLS_AND_CAVES] = { .item = ITEM_NUGGET, .qty = 1 },
    // #43 Zoo: Coast and Gulf. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_COAST_AND_GULF] = { .item = ITEM_NUGGET, .qty = 1 },
    // #44 Zoo: Cane and Pepper. Sheet: Zoo plaque decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_ZOO_CANE_AND_PEPPER_FIELDS] = { .item = ITEM_NUGGET, .qty = 1 },
    // #45 A Full Zoo. Sheet: Ability Capsule + 5 Heart Scales
    [ACH_A_FULL_ZOO] = { .item = ITEM_ABILITY_CAPSULE, .qty = 1, .item2 = ITEM_HEART_SCALE, .qty2 = 5 },
    // #46 A Full Aquarium. Sheet: Aquarium tank decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_A_FULL_AQUARIUM] = { .item = ITEM_NUGGET, .qty = 1 },
    // #47 40 for the Cause. Sheet: 5 Ultra Balls
    [ACH_CAUSE_I] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #48 75 for the Cause. Sheet: 10 Ultra Balls
    [ACH_CAUSE_II] = { .item = ITEM_ULTRA_BALL, .qty = 10 },
    // #49 120 for the Cause. Sheet: PP Max x3
    [ACH_CAUSE_III] = { .item = ITEM_PP_MAX, .qty = 3 },
    // #50 Back from the Past. Sheet: Fossil decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_BACK_FROM_THE_PAST] = { .item = ITEM_NUGGET, .qty = 1 },
    // #51 Something Hatched. Sheet: 5 Lucky Eggs  NOTE: sheet says 5 Lucky Eggs; the Oval Charm proposal competes (study 3.5)
    [ACH_SOMETHING_HATCHED] = { .item = ITEM_LUCKY_EGG, .qty = 1 },
    // #52 First Wave. Sheet: Boat look: Salvaged Skiff  NOTE: boat looks are dead (no player boat): placeholder
    [ACH_FIRST_WAVE] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #53 All Aboard. Sheet: 1,000 money
    [ACH_ALL_ABOARD] = { .money = 1000 },
    // #54 Into the Basin. Sheet: Boat look: Cypress Paint  NOTE: boat look is dead: placeholder
    [ACH_INTO_THE_BASIN] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #55 Across the Lake. Sheet: Boat look: Moss Garland  NOTE: boat look is dead: placeholder
    [ACH_ACROSS_THE_LAKE] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #56 Delta Bound. Sheet: Boat look: Heron Flag  NOTE: boat look is dead: placeholder
    [ACH_DELTA_BOUND] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #57 The Open Gulf. Sheet: Boat look: Storm Sail  NOTE: boat look is dead: placeholder
    [ACH_THE_OPEN_GULF] = { .item = ITEM_GREAT_BALL, .qty = 3 },
    // #58 Land Ho. Sheet: Rare item from the island  NOTE: islands do not exist yet
    [ACH_LAND_HO] = { .item = ITEM_RARE_CANDY, .qty = 1 },
    // #59 Island Hopper. Sheet: Boat look: Island Pennant  NOTE: boat look is dead: placeholder
    [ACH_ISLAND_HOPPER] = { .item = ITEM_ULTRA_BALL, .qty = 3 },
    // #60 The Old Water. Sheet: Berry set  NOTE: placeholder berries
    [ACH_THE_OLD_WATER] = { .item = ITEM_SITRUS_BERRY, .qty = 3, .item2 = ITEM_LUM_BERRY, .qty2 = 3 },
    // #61 Shrine Seeker. Sheet: Title: Shrine Seeker  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_SHRINE_SEEKER] = { .item = ITEM_RARE_CANDY, .qty = 1 },
    // #62 Every Route. Sheet: 10,000 money
    [ACH_EVERY_ROUTE] = { .money = 10000 },
    // #63 Every Corner. Sheet: Postcard decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_EVERY_CORNER] = { .item = ITEM_NUGGET, .qty = 1 },
    // #64 Order Up. Sheet: A Pokeblock case  NOTE: the barista already gives the case: placeholder
    [ACH_ORDER_UP] = { .item = ITEM_ULTRA_BALL, .qty = 3 },
    // #65 Best Friends. Sheet: Salon ribbon decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_BEST_FRIENDS] = { .item = ITEM_NUGGET, .qty = 1 },
    // #66 A Name of Its Own. Sheet: Name tag decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_A_NAME_OF_ITS_OWN] = { .item = ITEM_NUGGET, .qty = 1 },
    // #67 Lessons Learned. Sheet: 3 TMs of your choice  NOTE: needs a choice menu: placeholder item
    [ACH_LESSONS_LEARNED] = { .item = ITEM_ELIXIR, .qty = 3 },
    // #68 Training Day. Sheet: 6 vitamins  NOTE: placeholder vitamins
    [ACH_TRAINING_DAY] = { .item = ITEM_HP_UP, .qty = 3, .item2 = ITEM_PROTEIN, .qty2 = 3 },
    // #69 Born Ready. Sheet: 3 Bottle Caps
    [ACH_BORN_READY] = { .item = ITEM_BOTTLE_CAP, .qty = 3 },
    // #70 First Touch. Sheet: Welcome mat decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_FIRST_TOUCH] = { .item = ITEM_NUGGET, .qty = 1 },
    // #71 Make It Home. Sheet: Decorator title  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_MAKE_IT_HOME] = { .item = ITEM_RARE_CANDY, .qty = 1 },
    // #72 Spark in the House. Sheet: Appliance-themed decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_SPARK_IN_THE_HOUSE] = { .item = ITEM_NUGGET, .qty = 1 },
    // #73 The Whole Telling. Sheet: Title: Keeper of the Songs  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_THE_WHOLE_TELLING] = { .item = ITEM_RARE_CANDY, .qty = 1 },
    // #74 Wren's Friend. Sheet: Rootkin charm item  NOTE: the item is undefined: placeholder
    [ACH_WRENS_FRIEND] = { .item = ITEM_HEART_SCALE, .qty = 3 },
    // #75 A Rare Catch. Sheet: Prism Scale  NOTE: Prism Scale is sold in Dept2f: pick another reward
    [ACH_A_RARE_CATCH] = { .item = ITEM_HEART_SCALE, .qty = 5 },
    // #76 Legend: Rayquaza. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_RAYQUAZA] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #77 Legend: Kyogre. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_KYOGRE] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #78 Legend: Groudon. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_GROUDON] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #79 Legend: Uxie. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_UXIE] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #80 Legend: Mesprit. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_MESPRIT] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #81 Legend: Azelf. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_AZELF] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #82 Legend: Celebi. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_CELEBI] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #83 Legend: Articuno. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ARTICUNO] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #84 Legend: Galarian Articuno. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ARTICUNO_GALAR] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #85 Legend: Zapdos. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ZAPDOS] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #86 Legend: Galarian Zapdos. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ZAPDOS_GALAR] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #87 Legend: Moltres. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_MOLTRES] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #88 Legend: Galarian Moltres. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_MOLTRES_GALAR] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #89 Legend: Raikou. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_RAIKOU] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #90 Legend: Entei. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ENTEI] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #91 Legend: Suicune. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_SUICUNE] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #92 Legend: Tornadus. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_TORNADUS] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #93 Legend: Thundurus. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_THUNDURUS] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #94 Legend: Landorus. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_LANDORUS] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #95 Legend: Zarude. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_ZARUDE] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #96 Legend: Ogerpon. Sheet: Title and trophy decoration  NOTE: COSMETIC, no system yet: placeholder item
    [ACH_LEGEND_OGERPON] = { .item = ITEM_RARE_CANDY, .qty = 2 },
    // #97 The Bloodmoon. Sheet: 5 Heart Scales + PP Up
    [ACH_THE_BLOODMOON] = { .item = ITEM_HEART_SCALE, .qty = 5, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #98 Midnight Wolf. Sheet: 5 Heart Scales + PP Up
    [ACH_MIDNIGHT_WOLF] = { .item = ITEM_HEART_SCALE, .qty = 5, .item2 = ITEM_PP_UP, .qty2 = 1 },
    // #99 Spark of Life. Sheet: Rotom-themed item  NOTE: the item is undefined: placeholder
    [ACH_SPARK_OF_LIFE] = { .item = ITEM_NUGGET, .qty = 1 },
    // #100 Forever Flower. Sheet: Floette-themed item  NOTE: the item is undefined: placeholder
    [ACH_FOREVER_FLOWER] = { .item = ITEM_NUGGET, .qty = 1 },
    // #117 Hunter's Jaws. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_HUNTERS_JAWS] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #118 Psychic Fury. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_PSYCHIC_FURY] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #104 Paralysis Pro. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_PARALYSIS_PRO] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #105 Snow Setter. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_SNOW_SETTER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #106 Sun Setter. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_SUN_SETTER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #110 Tailwind Rider. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_TAILWIND_RIDER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #111 Rain Dancer. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_RAIN_DANCER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #112 Sandstorm Caller. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_SANDSTORM_CALLER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #115 Mist Weaver. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_MIST_WEAVER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #116 Room Warper. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_ROOM_WARPER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #101 Water Collector. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_WATER_COLLECTOR] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #102 Fire Collector. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_FIRE_COLLECTOR] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #103 Electric Collector. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_ELECTRIC_COLLECTOR] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #107 Fighters and Fliers. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_FIGHTERS_AND_FLIERS] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #108 Mind and Wing. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_MIND_AND_WING] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #109 Night Wings. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_NIGHT_WINGS] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #113 Moss and Shadow. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_MOSS_AND_SHADOW] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #114 Mask Collector. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_MASK_COLLECTOR] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
    // #119 Legend Hunter. Sheet: (new 2026-10-14) lair-key trophy  NOTE: placeholder, the real reward is the lair it opens
    [ACH_LEGEND_HUNTER] = { .item = ITEM_ULTRA_BALL, .qty = 5 },
};

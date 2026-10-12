#ifndef GUARD_CONSTANTS_FLAGS_H
#define GUARD_CONSTANTS_FLAGS_H

#include "constants/trainers.h"
#include "constants/opponents.h"
#include "constants/rematches.h"


// Temporary Flags
// These temporary flags are are cleared every time a map is loaded. They are used
// for things like shortening an NPCs introduction text if the player already spoke
// to them once.
#define TEMP_FLAGS_START 0x0
#define FLAG_TEMP_1      (TEMP_FLAGS_START + 0x1)
#define FLAG_TEMP_2      (TEMP_FLAGS_START + 0x2)
#define FLAG_TEMP_3      (TEMP_FLAGS_START + 0x3)
#define FLAG_TEMP_4      (TEMP_FLAGS_START + 0x4)
#define FLAG_TEMP_5      (TEMP_FLAGS_START + 0x5)  // Unused Flag
#define FLAG_TEMP_6      (TEMP_FLAGS_START + 0x6)  // Unused Flag
#define FLAG_TEMP_7      (TEMP_FLAGS_START + 0x7)  // Unused Flag
#define FLAG_TEMP_8      (TEMP_FLAGS_START + 0x8)  // Unused Flag
#define FLAG_TEMP_9      (TEMP_FLAGS_START + 0x9)  // Unused Flag
#define FLAG_TEMP_A      (TEMP_FLAGS_START + 0xA)  // Unused Flag
#define FLAG_TEMP_B      (TEMP_FLAGS_START + 0xB)  // Unused Flag
#define FLAG_TEMP_C      (TEMP_FLAGS_START + 0xC)  // Unused Flag
#define FLAG_TEMP_D      (TEMP_FLAGS_START + 0xD)  // Unused Flag
#define FLAG_TEMP_E      (TEMP_FLAGS_START + 0xE)  // When set, follower Pokémon won't be spawned
#define FLAG_TEMP_F      (TEMP_FLAGS_START + 0xF)  // Unused Flag
#define FLAG_TEMP_10     (TEMP_FLAGS_START + 0x10) // Unused Flag
#define FLAG_TEMP_11     (TEMP_FLAGS_START + 0x11)
#define FLAG_TEMP_12     (TEMP_FLAGS_START + 0x12)
#define FLAG_TEMP_13     (TEMP_FLAGS_START + 0x13)
#define FLAG_TEMP_14     (TEMP_FLAGS_START + 0x14)
#define FLAG_TEMP_15     (TEMP_FLAGS_START + 0x15)
#define FLAG_TEMP_16     (TEMP_FLAGS_START + 0x16)
#define FLAG_TEMP_17     (TEMP_FLAGS_START + 0x17)
#define FLAG_TEMP_18     (TEMP_FLAGS_START + 0x18)
#define FLAG_TEMP_19     (TEMP_FLAGS_START + 0x19)
#define FLAG_TEMP_1A     (TEMP_FLAGS_START + 0x1A)
#define FLAG_TEMP_1B     (TEMP_FLAGS_START + 0x1B)
#define FLAG_TEMP_1C     (TEMP_FLAGS_START + 0x1C)
#define FLAG_TEMP_1D     (TEMP_FLAGS_START + 0x1D)
#define FLAG_TEMP_1E     (TEMP_FLAGS_START + 0x1E)
#define FLAG_TEMP_1F     (TEMP_FLAGS_START + 0x1F)
#define TEMP_FLAGS_END   FLAG_TEMP_1F
#define NUM_TEMP_FLAGS   (TEMP_FLAGS_END - TEMP_FLAGS_START + 1)

#if IS_FRLG

#include "constants/flags_frlg.h"

#else

// ---------------------------------------------------------------------------------------------
// Orleans flag pool. Flags the Hoenn strip left unreferenced are named FLAG_ORLEANS_POOL_nnn
// (anywhere in this file). To use one, RENAME it in place (same id, never renumber), for example
//     python tools/mapgen/flag_pool.py claim FLAG_MY_NEW_THING "what it means"
// then use the new name. Ids >= FLAG_HIDDEN_ITEMS_START (0x1F4) can also be hidden-item flags
// (claim --hidden). Item-ball flags come from the FLAG_UNUSED_0x270+ names (tools/mapgen/item_flags.json),
// not from the pool. Same idea for vars: VAR_ORLEANS_POOL_nnn in vars.h. See tools/flag_pool.md.
// ---------------------------------------------------------------------------------------------
#define FLAG_ITEM_ISLE_MARAIS_POTION       0x20
#define FLAG_ITEM_ISLE_MARAIS_POKE_BALL    0x21
#define FLAG_ITEM_ISLE_MARAIS_SWAMPERTITE  0x22
#define FLAG_ITEM_ROUTE1_POTION          0x23
#define FLAG_ITEM_ROUTE1_POKE_BALL       0x24
#define FLAG_ITEM_ROUTE1_ORAN_BERRY      0x25
#define FLAG_ITEM_OLD_WATER_NET_BALL     0x26
#define FLAG_ORLEANS_GAME_STARTED    0x27 // set once the new game is initialised in the shelter
#define FLAG_HIDE_SHELTER_TOTODILE       0x28 // Orleans vertical slice
#define FLAG_HIDE_SHELTER_CHIKORITA      0x29 // Orleans vertical slice
#define FLAG_HIDE_SHELTER_FUECOCO        0x2A // Orleans vertical slice
#define FLAG_HIDE_SHELTER_JAYDEN         0x2B // Orleans vertical slice
#define FLAG_HIDE_SHELTER_WREN           0x2C // Orleans vertical slice
#define FLAG_HIDE_SHELTER_LAFAYETTE      0x2D // Orleans vertical slice
#define FLAG_HIDE_SHELTER_MOM            0x2E // Orleans vertical slice
#define FLAG_HIDE_PLAYERS_HOUSE_MOM      0x2F // Orleans vertical slice
#define FLAG_HIDE_ROUTE1_LAFAYETTE       0x30 // Orleans vertical slice
#define FLAG_HIDE_ROUTE1_JAYDEN          0x31 // Orleans vertical slice
#define FLAG_HIDE_ROUTE1_WREN            0x32 // Orleans vertical slice
#define FLAG_HIDE_OLD_WATER_TUPELO       0x33 // Orleans vertical slice
#define FLAG_HIDE_OLD_WATER_WREN         0x34 // Orleans vertical slice
#define FLAG_HIDE_WRENS_HOUSE_WREN       0x35 // Orleans vertical slice
#define FLAG_HIDE_GRAND_OAK_WREN         0x36 // Orleans vertical slice
#define FLAG_CUT_STORM_HEDGE             0x37 // Orleans vertical slice
#define FLAG_RECEIVED_GARDEN_SHEARS      0x38 // Orleans vertical slice
#define FLAG_STORMS_EDGE_GRID_RESTORED   0x39 // Orleans: Storm's Edge power grid restored (gym 2): the drawbridge is lowered
#define FLAG_HIDE_STORMS_EDGE_ECLAIR     0x3A // Orleans Ch2: Eclair outside the substation, hidden once the grid is back (she's in the gym)
#define FLAG_HIDE_ROUTE3_JAYDEN          0x3B // Orleans Ch2: Jayden on the Route 3 bridge, hidden after battle 2
#define FLAG_RECEIVED_PRY_BAR            0x3C // Orleans Ch2: the gym 2 rewards (TM Shock Wave, Pry Bar) were handed over
#define FLAG_STORMS_EDGE_DESK_POWERED    0x3D // Orleans Ch2: the substation puzzle is solved, Eclair's desk is live
#define FLAG_STORMS_EDGE_JUNCTION_1      0x3E // Orleans Ch2: gym 2 junction 1 is lit
#define FLAG_STORMS_EDGE_JUNCTION_2      0x3F // Orleans Ch2: gym 2 junction 2 is lit
#define FLAG_STORMS_EDGE_JUNCTION_3      0x40 // Orleans Ch2: gym 2 junction 3 is lit
#define FLAG_STORMS_EDGE_JUNCTION_4      0x41 // Orleans Ch2: gym 2 junction 4 is lit
#define FLAG_STORMS_EDGE_JUNCTION_5      0x42 // Orleans Ch2: gym 2 junction 5 is lit
#define FLAG_STORMS_EDGE_JUNCTION_6      0x43 // Orleans Ch2: gym 2 junction 6 is lit
#define FLAG_STORMS_EDGE_PUZZLE_STARTED  0x44 // Orleans Ch2: the junctions have been set to their starting pattern
#define FLAG_HIDE_STORMS_EDGE_VOLTORB_1  0x45 // Orleans Ch2: buoy Voltorb 1 in the gym, hidden once beaten
#define FLAG_HIDE_STORMS_EDGE_VOLTORB_2  0x46 // Orleans Ch2: buoy Voltorb 2 in the gym, hidden once beaten
#define FLAG_RECEIVED_TM_TRAILBLAZE      0x47 // Orleans: Magnolia's TM Trailblaze was handed over (separate from the Shears so a full bag never duplicates it)
#define FLAG_RECEIVED_TM_ECLAIR_SHOCK_WAVE      0x48 // Orleans Ch2: Eclair's TM Shock Wave was handed over
#define FLAG_RESPAWN_GRAND_OAK_SET       0x49 // Orleans: the Grand Oak respawn point was set on the first arrival (later visits must not override a Center healed at elsewhere)
#define FLAG_RESPAWN_STORMS_EDGE_SET     0x4A // Orleans: the Storm's Edge respawn point was set on the first arrival
#define FLAG_ORLEANS_TUTOR_RELEARNER                     0x4B // Orleans: the Crescent City tutor has opened the Move Relearner tutor list (P_FLAG_TUTOR_MOVES)
#define FLAG_ORLEANS_EGG_RELEARNER                       0x4C // Orleans: the Crescent City tutor has opened the Move Relearner egg-move list (P_FLAG_EGG_MOVES)
#define FLAG_POINTE_VALVE_1                              0x4D // Orleans Ch4: refinery valve n shut
#define FLAG_POINTE_VALVE_2                              0x4E // Orleans Ch4: refinery valve n shut
#define FLAG_POINTE_VALVE_3                              0x4F // Orleans Ch4: refinery valve n shut

// Scripts
#define FLAG_POINTE_VALVE_4                              0x50 // Orleans Ch4: refinery valve n shut
#define FLAG_SET_WALL_CLOCK                      0x51
#define FLAG_RESCUED_BIRCH                       0x52
#define FLAG_LEGENDARIES_IN_SOOTOPOLIS           0x53

#define FLAG_POINTE_GYM_TAILWIND                         0x54 // Orleans Ch4: the gym's tailwind is up, the rafter nets are blown aside
#define FLAG_POINTE_TOURNEY_WON                          0x55 // Orleans Ch4: the Route 5 fishing tournament was won (weigh-in passed)

#define FLAG_HIDE_CONTEST_POKE_BALL          0x56  // Always set after new game, object it hides is added directly
#define FLAG_RECEIVED_GOOD_ROD                           0x57 // Orleans Ch4: Good Rod received from the tournament angler
#define FLAG_RECEIVED_SUPER_ROD                          0x58 // Orleans Ch4: Kingfisher's Super Rod received
#define FLAG_RECEIVED_TM_AERIAL_ACE                      0x59 // Orleans Ch4: Kingfisher's TM Aerial Ace received
#define FLAG_RECEIVED_BIKE                   0x5A
#define FLAG_WATTSON_REMATCH_AVAILABLE       0x5B
#define FLAG_COLLECTED_ALL_SILVER_SYMBOLS    0x5C
#define FLAG_GOOD_LUCK_SAFARI_ZONE           0x5D // Set after talking to NPC blocking Safari Zone entrance/exit once.
#define FLAG_RECEIVED_HM_SURF                            0x5E // Orleans Ch4: HM Surf received at the Old Water midpoint visit
#define FLAG_RECEIVED_POKEBLOCK_CASE         0x5F
#define FLAG_RECEIVED_SECRET_POWER           0x60
#define FLAG_MET_TEAM_AQUA_HARBOR            0x61
#define FLAG_RECEIVED_ROCKRUFF                           0x62 // Orleans Ch4: Wren's Own Tempo Rockruff received
#define FLAG_ROUTE6_DEBRIS_CLEARED                       0x63 // Orleans Ch4: verse 4 cleared the Route 6 storm debris (set at the Old Water midpoint visit)
#define FLAG_HIDE_POINTE_CAMILLE                         0x64 // Orleans Ch4: Camille / Jayden in the refinery, hidden once the sabotage is stopped
#define FLAG_HIDE_POINTE_JAYDEN                          0x65 // Orleans Ch4: Camille / Jayden in the refinery, hidden once the sabotage is stopped
#define FLAG_POINTE_ITEM_METAL_COAT                      0x66 // Orleans Ch4: item balls placed by the story pass
#define FLAG_POINTE_ITEM_SMOKE_BALL                      0x67 // Orleans Ch4: item balls placed by the story pass

#define FLAG_POINTE_ITEM_FEAROWITE                       0x68 // Orleans Ch4: item balls placed by the story pass

#define FLAG_OCEANIC_MUSEUM_MET_REPORTER     0x69
#define FLAG_RECEIVED_HM_STRENGTH            0x6A
#define FLAG_ROUTE5_ITEM_AGILITY                         0x6B // Orleans Ch4: item balls placed by the story pass
#define FLAG_WHITEOUT_TO_LAVARIDGE           0x6C // Set after defeating Flannery, so the player can't white out from poison before receiving Go Goggles
#define FLAG_KYOGRE_CALMED                               0x6D // Orleans finale: the Kyogre raid is done (plan story 40; either order)
#define FLAG_POINTE_GATE_SCENE_SEEN                      0x6E // Orleans Ch4: the refinery gate scene was played
#define FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT  0x6F
#define FLAG_TEAM_AQUA_ESCAPED_IN_SUBMARINE  0x70
#define FLAG_GROUDON_CALMED                              0x71 // Orleans finale: the Groudon raid is done (plan story 40; either order)
#define FLAG_SCOTT_CALL_BATTLE_FRONTIER      0x72 // Used in order to activate a phone call from Scott, inviting the player to the SS Tidal.
#define FLAG_ROUTE25_OPEN                                0x73 // Orleans: the channel to the Oldest Shrine is open (set once BOTH raids are done; the Route 25 water gate keys on it)
#define FLAG_ADVENTURE_STARTED               0x74 // RECEIVED Pokédex.
#define FLAG_DEFEATED_MAGMA_SPACE_CENTER     0x75 // Set when Team Magma is defeated at Mossdeep's Space Center.
#define FLAG_CAMP_FIRE_STOKED                            0x76 // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)

#define FLAG_CANCEL_BATTLE_ROOM_CHALLENGE    0x77

#define FLAG_LANDMARK_MIRAGE_TOWER           0x78
#define FLAG_CAMP_ANDOUILLE                              0x79 // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)
#define FLAG_CAMP_SHRIMP                                 0x7A // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)
#define FLAG_CAMP_OKRA_ASKED                             0x7B // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)
#define FLAG_CAMP_OKRA                                   0x7C // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)
#define FLAG_CAMP_FILE                                   0x7D // Orleans Ch5: the gumbo cook-off ingredients (smokehouse fire stoked / andouille / shrimp / okra asked / okra picked / file)
#define FLAG_DEFEATED_WALLY_VICTORY_ROAD     0x7E
#define FLAG_RECEIVED_TM_SLUDGE_BOMB                     0x7F // Orleans Ch5: the brothers' TM Sludge Bomb was handed over
#define FLAG_ENABLE_ROXANNE_FIRST_CALL       0x80 // Set after defeating Brawly. This will activate a call with Roxanne in order to register her.
#define FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN  0x81
#define FLAG_HIDE_CAMP_ISAAC                             0x82 // Orleans Ch5: Isaac left the nurse cabin door (set once his battle is won)
#define FLAG_ROUTE7_STUMP_OPENED                         0x83 // Orleans Ch5: Route 7's cut stump (Pry Bar) was opened
#define FLAG_ROUTE6_ITEM_STEALTH_ROCK                    0x84 // Orleans Ch5: item balls placed by the story pass
#define FLAG_RECEIVED_AMULET_COIN            0x85
#define FLAG_PENDING_DAYCARE_EGG             0x86
#define FLAG_ROUTE8_ITEM_NASTY_PLOT                      0x87 // Orleans Ch5: item balls placed by the story pass
#define FLAG_ENABLE_FIRST_WALLY_POKENAV_CALL 0x88 // Set after defeating Wally outside Mauville Gym. Will activate a call later to register Wally.
#define FLAG_VERSE4_HEARD                                0x89 // Orleans Ch4: Tupelo has sung verse 4 and given the true piece (the HM offer follows; retried until HM Surf is in the bag)
#define FLAG_SCOTT_CALL_FORTREE_GYM          0x8A // Triggers call from Scott after defeating Winona
#define FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY   0x8B
#define FLAG_HIDE_HOLLOW_JAYDEN                          0x8C // Orleans Ch6: Jayden / Wren by the hollow's south pools (hidden after the scene), the gym usher (hidden from story 28)
#define FLAG_HIDE_HOLLOW_WREN                            0x8D // Orleans Ch6: Jayden / Wren by the hollow's south pools (hidden after the scene), the gym usher (hidden from story 28)
#define FLAG_HIDE_HOLLOW_GYM_USHER                       0x8E // Orleans Ch6: Jayden / Wren by the hollow's south pools (hidden after the scene), the gym usher (hidden from story 28)
#define FLAG_RECEIVED_TM_DAZZLING_GLEAM                  0x8F // Orleans Ch6: Lutin's TM Dazzling Gleam was handed over
#define FLAG_RECEIVED_DELPHOXITE                         0x90 // Orleans Ch6: Delphoxite (riddler) / Exploudite (zydeco band) received
#define FLAG_CAUGHT_LUGIA                    0x91
#define FLAG_CAUGHT_HO_OH                    0x92
#define FLAG_RECEIVED_EXPLOUDITE                         0x93 // Orleans Ch6: Delphoxite (riddler) / Exploudite (zydeco band) received
#define FLAG_VERSE6_HEARD                                0x94 // Orleans Ch6: Tupelo sang verse 6 / the carver gave the cypress-wood charm (the Mega Evolution key item)
#define FLAG_DELIVERED_DEVON_GOODS           0x95
#define FLAG_RECEIVED_CYPRESS_CHARM                      0x96 // Orleans Ch6: Tupelo sang verse 6 / the carver gave the cypress-wood charm (the Mega Evolution key item)
#define FLAG_RECEIVED_CASTFORM               0x97
#define FLAG_ROUTE12_ITEM_ENERGY_BALL                    0x98 // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_ROUTE12_ITEM_EARTH_POWER                    0x99 // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_ROUTE13_ITEM_ZEN_HEADBUTT                   0x9A // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_ROUTE13_ITEM_DARK_PULSE                     0x9B // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_BATTLE_FRONTIER_TRADE_DONE      0x9C
#define FLAG_FORCE_MIRAGE_TOWER_VISIBLE      0x9D
#define FLAG_ROUTE10_ITEM_CRUNCH                         0x9E // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_ROUTE11_ITEM_LIQUIDATION                    0x9F // Orleans Ch6: item balls (TMs) placed by the story pass
#define FLAG_RECEIVED_QUAQUAVALITE                       0xA0 // Orleans Ch6/7: the parade leader's Quaquavalite (after badge 6)
#define FLAG_HIDE_REDFIELD_RITA                          0xA1 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_ORLEANS_POOL_052                            0xA2
#define FLAG_HIDE_REDFIELD_WREN                          0xA3 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_HIDE_RAID_ISAAC                             0xA4 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_HIDE_RAID_GRUNT1                            0xA5 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_HIDE_RAID_GRUNT2                            0xA6 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_HIDE_RAID_WREN                              0xA7 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_HIDE_ROUTE14_ROUGAROU                       0xA8 // Chapter 7 visibility flags: Rita at the mill, her office double, Wren at the mill, the Old Water raid actors, the rougarou
#define FLAG_REDFIELD_SUN1                               0xA9 // Chapter 7 mill yard trial: sundials lit, the mill shutter open
#define FLAG_REDFIELD_SUN2                               0xAA // Chapter 7 mill yard trial: sundials lit, the mill shutter open
#define FLAG_REDFIELD_SUN3                               0xAB // Chapter 7 mill yard trial: sundials lit, the mill shutter open
#define FLAG_REDFIELD_MILL_OPEN                          0xAC // Chapter 7 mill yard trial: sundials lit, the mill shutter open
#define FLAG_HIDE_SECRET_BASE_TRAINER        0xAD
#define FLAG_DECORATION_1                    0xAE
#define FLAG_DECORATION_2                    0xAF
#define FLAG_DECORATION_3                    0xB0
#define FLAG_DECORATION_4                    0xB1
#define FLAG_DECORATION_5                    0xB2
#define FLAG_DECORATION_6                    0xB3
#define FLAG_DECORATION_7                    0xB4
#define FLAG_DECORATION_8                    0xB5
#define FLAG_DECORATION_9                    0xB6
#define FLAG_DECORATION_10                   0xB7
#define FLAG_DECORATION_11                   0xB8
#define FLAG_DECORATION_12                   0xB9
#define FLAG_DECORATION_13                   0xBA
#define FLAG_DECORATION_14                   0xBB
#define FLAG_RECEIVED_POKENAV                0xBC
#define FLAG_DELIVERED_STEVEN_LETTER         0xBD
#define FLAG_RECEIVED_TM050_OVERHEAT                     0xBE // Chapter 7: Cayenne's TM Overheat received
#define FLAG_RECEIVED_CHARIZARDITE_Y                     0xBF // Chapter 7 one-offs: Cayenne rewards, the rougarou and its stone, Rita beaten
#define FLAG_ROUTE14_ROUGAROU_DONE                       0xC0 // Chapter 7 one-offs: Cayenne rewards, the rougarou and its stone, Rita beaten
#define FLAG_RECEIVED_LYCANROCITE                        0xC1 // Chapter 7 one-offs: Cayenne rewards, the rougarou and its stone, Rita beaten
#define FLAG_REDFIELD_RITA_BEATEN                        0xC2 // Chapter 7 one-offs: Cayenne rewards, the rougarou and its stone, Rita beaten
#define FLAG_ROUTE14_ITEM_SEED_BOMB                      0xC3 // Orleans Ch7: item balls (TMs) placed by the story pass
#define FLAG_ROUTE15_ITEM_HYPER_VOICE                    0xC4 // Orleans Ch7: item balls (TMs) placed by the story pass
#define FLAG_ROUTE16_ITEM_THROAT_CHOP                    0xC5 // Orleans Ch7: item balls (TMs) placed by the story pass
#define FLAG_ROUTE17_ITEM_FOUL_PLAY                      0xC6 // Orleans Ch7: item balls (TMs) placed by the story pass
#define FLAG_RUSTURF_TUNNEL_OPENED           0xC7
#define FLAG_ORLEANS_POOL_072                           0xC8
#define FLAG_ORLEANS_POOL_073                           0xC9
#define FLAG_ORLEANS_POOL_074                           0xCA
#define FLAG_ORLEANS_POOL_075                           0xCB
#define FLAG_ORLEANS_POOL_076                           0xCC
#define FLAG_ORLEANS_POOL_077                           0xCD
#define FLAG_ORLEANS_POOL_078                           0xCE
#define FLAG_MET_ARCHIE_METEOR_FALLS         0xCF
#define FLAG_ORLEANS_POOL_079                           0xD0
#define FLAG_ORLEANS_POOL_080                           0xD1
#define FLAG_ORLEANS_POOL_081                           0xD2
#define FLAG_ORLEANS_POOL_082                           0xD3
#define FLAG_RECEIVED_RED_OR_BLUE_ORB        0xD4
#define FLAG_ORLEANS_POOL_083                           0xD5
#define FLAG_ENABLE_WALLY_MATCH_CALL         0xD6
#define FLAG_ENABLE_SCOTT_MATCH_CALL         0xD7
#define FLAG_ENABLE_MOM_MATCH_CALL           0xD8
#define FLAG_ORLEANS_POOL_084                           0xD9
#define FLAG_ORLEANS_POOL_085                           0xDA
#define FLAG_ORLEANS_POOL_086                           0xDB

#define FLAG_NEVER_SET_0x0DC                 0xDC // This flag is read, but never written to

#define FLAG_ORLEANS_POOL_087                           0xDD
#define FLAG_ORLEANS_POOL_088                           0xDE
#define FLAG_ORLEANS_POOL_089                           0xDF
#define FLAG_ORLEANS_POOL_090                           0xE0
#define FLAG_ORLEANS_POOL_091                           0xE1
#define FLAG_ORLEANS_POOL_092                           0xE2
#define FLAG_ORLEANS_POOL_093                           0xE3
#define FLAG_REGI_DOORS_OPENED               0xE4
#define FLAG_ORLEANS_POOL_094                           0xE5
#define FLAG_ORLEANS_POOL_095                           0xE6
#define FLAG_ORLEANS_POOL_096                           0xE7
#define FLAG_ORLEANS_POOL_097                           0xE8

#define FLAG_ORLEANS_POOL_098                           0xE9

#define FLAG_ORLEANS_POOL_099                           0xEA
#define FLAG_RECEIVED_TM_ATTRACT             0xEB
#define FLAG_ORLEANS_POOL_100                           0xEC
#define FLAG_RECEIVED_SILVER_SHIELD          0xED
#define FLAG_RECEIVED_GOLD_SHIELD            0xEE
#define FLAG_ORLEANS_POOL_101                           0xEF
#define FLAG_ORLEANS_POOL_102                           0xF0
#define FLAG_ORLEANS_POOL_103                           0xF1
#define FLAG_ORLEANS_POOL_104                           0xF2
#define FLAG_ORLEANS_POOL_105                           0xF3
#define FLAG_ORLEANS_POOL_106                           0xF4
#define FLAG_ORLEANS_POOL_107                           0xF5
#define FLAG_ORLEANS_POOL_108                           0xF6
#define FLAG_ORLEANS_POOL_109                           0xF7
#define FLAG_ORLEANS_POOL_110                           0xF8
#define FLAG_ORLEANS_POOL_111                           0xF9
#define FLAG_ORLEANS_POOL_112                           0xFA
#define FLAG_ORLEANS_POOL_113                           0xFB
#define FLAG_ORLEANS_POOL_114                           0xFC
#define FLAG_ENABLE_RIVAL_MATCH_CALL         0xFD
#define FLAG_ORLEANS_POOL_115                           0xFE
#define FLAG_LATIOS_OR_LATIAS_ROAMING        0xFF
#define FLAG_ORLEANS_POOL_116                           0x100
#define FLAG_RECEIVED_OLD_ROD                0x101
#define FLAG_ORLEANS_POOL_117                           0x102
#define FLAG_ORLEANS_POOL_118                           0x103
#define FLAG_ORLEANS_POOL_119                           0x104
#define FLAG_ORLEANS_POOL_120                           0x105
#define FLAG_ORLEANS_POOL_121                           0x106
#define FLAG_ORLEANS_POOL_122                           0x107
#define FLAG_ORLEANS_POOL_123                           0x108
#define FLAG_RECEIVED_TM_TORMENT             0x109
#define FLAG_ORLEANS_POOL_124                           0x10A
#define FLAG_ORLEANS_POOL_125                           0x10B
#define FLAG_SECRET_BASE_REGISTRY_ENABLED    0x10C
#define FLAG_ORLEANS_POOL_126                           0x10D
#define FLAG_CONTEST_SKETCH_CREATED          0x10E  // Set but never read
#define FLAG_ORLEANS_POOL_127                           0x10F
#define FLAG_RECEIVED_EXP_SHARE              0x110
#define FLAG_POKERUS_EXPLAINED               0x111
#define FLAG_RECEIVED_RUNNING_SHOES          0x112
#define FLAG_ORLEANS_POOL_128                           0x113
#define FLAG_ORLEANS_POOL_129                           0x114
#define FLAG_ORLEANS_POOL_130                           0x115
#define FLAG_ORLEANS_POOL_131                           0x116
#define FLAG_ORLEANS_POOL_132                           0x117
#define FLAG_ORLEANS_POOL_133                           0x118
#define FLAG_ENABLE_PROF_BIRCH_MATCH_CALL    0x119
#define FLAG_ORLEANS_POOL_134                           0x11A
#define FLAG_ORLEANS_POOL_135                           0x11B
#define FLAG_ORLEANS_POOL_136                           0x11C
#define FLAG_ORLEANS_POOL_137                           0x11D
#define FLAG_ORLEANS_POOL_138                           0x11E
#define FLAG_ORLEANS_POOL_139                           0x11F
#define FLAG_ORLEANS_POOL_140                           0x120
#define FLAG_ORLEANS_POOL_141                           0x121
#define FLAG_ORLEANS_POOL_142                           0x122
#define FLAG_RECEIVED_SS_TICKET              0x123
#define FLAG_ORLEANS_POOL_143                           0x124
#define FLAG_ORLEANS_POOL_144                           0x125
#define FLAG_ORLEANS_POOL_145                           0x126
#define FLAG_ORLEANS_POOL_146                           0x127
#define FLAG_PETALBURG_MART_EXPANDED_ITEMS   0x128
#define FLAG_ORLEANS_POOL_147                           0x129
#define FLAG_RECEIVED_BELDUM                 0x12A
#define FLAG_ORLEANS_POOL_148                           0x12B
#define FLAG_ORLEANS_POOL_149                           0x12C
#define FLAG_ORLEANS_POOL_150                           0x12D
#define FLAG_ORLEANS_POOL_151                           0x12E
#define FLAG_HAS_MATCH_CALL                  0x12F
#define FLAG_ADDED_MATCH_CALL_TO_POKENAV     0x130
#define FLAG_REGISTERED_STEVEN_POKENAV       0x131
#define FLAG_ENABLE_NORMAN_MATCH_CALL        0x132
#define FLAG_ORLEANS_POOL_152                           0x133
#define FLAG_ORLEANS_POOL_153                           0x134
#define FLAG_ORLEANS_POOL_154                           0x135
#define FLAG_ORLEANS_POOL_155                           0x136
#define FLAG_ORLEANS_POOL_156                           0x137
#define FLAG_ORLEANS_POOL_157                           0x138
#define FLAG_ORLEANS_POOL_158                           0x139
#define FLAG_RECEIVED_AURORA_TICKET          0x13A
#define FLAG_RECEIVED_MYSTIC_TICKET          0x13B
#define FLAG_RECEIVED_OLD_SEA_MAP            0x13C
#define FLAG_WONDER_CARD_UNUSED_1            0x13D // These Wonder Card flags are referenced but never set
#define FLAG_WONDER_CARD_UNUSED_2            0x13E
#define FLAG_WONDER_CARD_UNUSED_3            0x13F
#define FLAG_WONDER_CARD_UNUSED_4            0x140
#define FLAG_WONDER_CARD_UNUSED_5            0x141
#define FLAG_WONDER_CARD_UNUSED_6            0x142
#define FLAG_WONDER_CARD_UNUSED_7            0x143
#define FLAG_WONDER_CARD_UNUSED_8            0x144
#define FLAG_WONDER_CARD_UNUSED_9            0x145
#define FLAG_WONDER_CARD_UNUSED_10           0x146
#define FLAG_WONDER_CARD_UNUSED_11           0x147
#define FLAG_WONDER_CARD_UNUSED_12           0x148
#define FLAG_WONDER_CARD_UNUSED_13           0x149
#define FLAG_WONDER_CARD_UNUSED_14           0x14A
#define FLAG_WONDER_CARD_UNUSED_15           0x14B
#define FLAG_WONDER_CARD_UNUSED_16           0x14C
#define FLAG_WONDER_CARD_UNUSED_17           0x14D
#define NUM_WONDER_CARD_FLAGS                (1 + FLAG_WONDER_CARD_UNUSED_17 - FLAG_RECEIVED_AURORA_TICKET)

#define FLAG_MIRAGE_TOWER_VISIBLE            0x14E
#define FLAG_ORLEANS_POOL_159                           0x14F
#define FLAG_CHOSE_CLAW_FOSSIL               0x150
#define FLAG_ORLEANS_POOL_160                           0x151

#define FLAG_CHOSEN_MULTI_BATTLE_NPC_PARTNER 0x152

#define FLAG_MET_BATTLE_FRONTIER_BREEDER     0x153
#define FLAG_MET_BATTLE_FRONTIER_MANIAC      0x154
#define FLAG_ENTERED_CONTEST                 0x155
#define FLAG_ORLEANS_POOL_161                           0x156
#define FLAG_MET_BATTLE_FRONTIER_GAMBLER     0x157
#define FLAG_ENABLE_MR_STONE_POKENAV         0x158
#define FLAG_NURSE_MENTIONS_GOLD_CARD        0x159
#define FLAG_MET_FRONTIER_BEAUTY_MOVE_TUTOR  0x15A
#define FLAG_MET_FRONTIER_SWIMMER_MOVE_TUTOR 0x15B

// Flags for whether a rematchable trainer has been registered in the player's Match Call.
// Most are used implicitly by adding their REMATCH_* id to TRAINER_REGISTERED_FLAGS_START.
// Some Match Call entries (like those for gym leaders, Wally, and all non-trainer NPCs like Prof. Birch)
// have their own separate flag that needs to be set to be enabled; see src/pokenav_match_call_data.c
#define TRAINER_REGISTERED_FLAGS_START       0x15C
#define FLAG_REGISTERED_ROSE                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_ROSE)
#define FLAG_REGISTERED_ANDRES               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ANDRES)
#define FLAG_REGISTERED_DUSTY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_DUSTY)
#define FLAG_REGISTERED_LOLA                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_LOLA)
#define FLAG_REGISTERED_RICKY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_RICKY)
#define FLAG_REGISTERED_LILA_AND_ROY         (TRAINER_REGISTERED_FLAGS_START + REMATCH_LILA_AND_ROY)
#define FLAG_REGISTERED_CRISTIN              (TRAINER_REGISTERED_FLAGS_START + REMATCH_CRISTIN)
#define FLAG_REGISTERED_BROOKE               (TRAINER_REGISTERED_FLAGS_START + REMATCH_BROOKE)
#define FLAG_REGISTERED_WILTON               (TRAINER_REGISTERED_FLAGS_START + REMATCH_WILTON)
#define FLAG_REGISTERED_VALERIE              (TRAINER_REGISTERED_FLAGS_START + REMATCH_VALERIE)
#define FLAG_REGISTERED_CINDY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_CINDY)
#define FLAG_REGISTERED_THALIA               (TRAINER_REGISTERED_FLAGS_START + REMATCH_THALIA)
#define FLAG_REGISTERED_JESSICA              (TRAINER_REGISTERED_FLAGS_START + REMATCH_JESSICA)
#define FLAG_REGISTERED_WINSTON              (TRAINER_REGISTERED_FLAGS_START + REMATCH_WINSTON)
#define FLAG_REGISTERED_STEVE                (TRAINER_REGISTERED_FLAGS_START + REMATCH_STEVE)
#define FLAG_REGISTERED_TONY                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_TONY)
#define FLAG_REGISTERED_NOB                  (TRAINER_REGISTERED_FLAGS_START + REMATCH_NOB)
#define FLAG_REGISTERED_KOJI                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_KOJI)
#define FLAG_REGISTERED_FERNANDO             (TRAINER_REGISTERED_FLAGS_START + REMATCH_FERNANDO)
#define FLAG_REGISTERED_DALTON               (TRAINER_REGISTERED_FLAGS_START + REMATCH_DALTON)
#define FLAG_REGISTERED_BERNIE               (TRAINER_REGISTERED_FLAGS_START + REMATCH_BERNIE)
#define FLAG_REGISTERED_ETHAN                (TRAINER_REGISTERED_FLAGS_START + REMATCH_ETHAN)
#define FLAG_REGISTERED_JOHN_AND_JAY         (TRAINER_REGISTERED_FLAGS_START + REMATCH_JOHN_AND_JAY)
#define FLAG_REGISTERED_JEFFREY              (TRAINER_REGISTERED_FLAGS_START + REMATCH_JEFFREY)
#define FLAG_REGISTERED_CAMERON              (TRAINER_REGISTERED_FLAGS_START + REMATCH_CAMERON)
#define FLAG_REGISTERED_JACKI                (TRAINER_REGISTERED_FLAGS_START + REMATCH_JACKI)
#define FLAG_REGISTERED_WALTER               (TRAINER_REGISTERED_FLAGS_START + REMATCH_WALTER)
#define FLAG_REGISTERED_KAREN                (TRAINER_REGISTERED_FLAGS_START + REMATCH_KAREN)
#define FLAG_REGISTERED_JERRY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_JERRY)
#define FLAG_REGISTERED_ANNA_AND_MEG         (TRAINER_REGISTERED_FLAGS_START + REMATCH_ANNA_AND_MEG)
#define FLAG_REGISTERED_ISABEL               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ISABEL)
#define FLAG_REGISTERED_MIGUEL               (TRAINER_REGISTERED_FLAGS_START + REMATCH_MIGUEL)
#define FLAG_REGISTERED_TIMOTHY              (TRAINER_REGISTERED_FLAGS_START + REMATCH_TIMOTHY)
#define FLAG_REGISTERED_SHELBY               (TRAINER_REGISTERED_FLAGS_START + REMATCH_SHELBY)
#define FLAG_REGISTERED_CALVIN               (TRAINER_REGISTERED_FLAGS_START + REMATCH_CALVIN)
#define FLAG_REGISTERED_ELLIOT               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ELLIOT)
#define FLAG_REGISTERED_ISAIAH               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ISAIAH)
#define FLAG_REGISTERED_MARIA                (TRAINER_REGISTERED_FLAGS_START + REMATCH_MARIA)
#define FLAG_REGISTERED_ABIGAIL              (TRAINER_REGISTERED_FLAGS_START + REMATCH_ABIGAIL)
#define FLAG_REGISTERED_DYLAN                (TRAINER_REGISTERED_FLAGS_START + REMATCH_DYLAN)
#define FLAG_REGISTERED_KATELYN              (TRAINER_REGISTERED_FLAGS_START + REMATCH_KATELYN)
#define FLAG_REGISTERED_BENJAMIN             (TRAINER_REGISTERED_FLAGS_START + REMATCH_BENJAMIN)
#define FLAG_REGISTERED_PABLO                (TRAINER_REGISTERED_FLAGS_START + REMATCH_PABLO)
#define FLAG_REGISTERED_NICOLAS              (TRAINER_REGISTERED_FLAGS_START + REMATCH_NICOLAS)
#define FLAG_REGISTERED_ROBERT               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ROBERT)
#define FLAG_REGISTERED_LAO                  (TRAINER_REGISTERED_FLAGS_START + REMATCH_LAO)
#define FLAG_REGISTERED_CYNDY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_CYNDY)
#define FLAG_REGISTERED_MADELINE             (TRAINER_REGISTERED_FLAGS_START + REMATCH_MADELINE)
#define FLAG_REGISTERED_JENNY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_JENNY)
#define FLAG_REGISTERED_DIANA                (TRAINER_REGISTERED_FLAGS_START + REMATCH_DIANA)
#define FLAG_REGISTERED_AMY_AND_LIV          (TRAINER_REGISTERED_FLAGS_START + REMATCH_AMY_AND_LIV)
#define FLAG_REGISTERED_ERNEST               (TRAINER_REGISTERED_FLAGS_START + REMATCH_ERNEST)
#define FLAG_REGISTERED_CORY                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_CORY)
#define FLAG_REGISTERED_EDWIN                (TRAINER_REGISTERED_FLAGS_START + REMATCH_EDWIN)
#define FLAG_REGISTERED_LYDIA                (TRAINER_REGISTERED_FLAGS_START + REMATCH_LYDIA)
#define FLAG_REGISTERED_ISAAC                (TRAINER_REGISTERED_FLAGS_START + REMATCH_ISAAC)
#define FLAG_REGISTERED_GABRIELLE            (TRAINER_REGISTERED_FLAGS_START + REMATCH_GABRIELLE)
#define FLAG_REGISTERED_CATHERINE            (TRAINER_REGISTERED_FLAGS_START + REMATCH_CATHERINE)
#define FLAG_REGISTERED_JACKSON              (TRAINER_REGISTERED_FLAGS_START + REMATCH_JACKSON)
#define FLAG_REGISTERED_HALEY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_HALEY)
#define FLAG_REGISTERED_JAMES                (TRAINER_REGISTERED_FLAGS_START + REMATCH_JAMES)
#define FLAG_REGISTERED_TRENT                (TRAINER_REGISTERED_FLAGS_START + REMATCH_TRENT)
#define FLAG_REGISTERED_SAWYER               (TRAINER_REGISTERED_FLAGS_START + REMATCH_SAWYER)
#define FLAG_REGISTERED_KIRA_AND_DAN         (TRAINER_REGISTERED_FLAGS_START + REMATCH_KIRA_AND_DAN)
#define FLAG_REGISTERED_WALLY                (TRAINER_REGISTERED_FLAGS_START + REMATCH_WALLY_VR)
#define FLAG_REGISTERED_ROXANNE              (TRAINER_REGISTERED_FLAGS_START + REMATCH_ROXANNE)
#define FLAG_REGISTERED_BRAWLY               (TRAINER_REGISTERED_FLAGS_START + REMATCH_BRAWLY)
#define FLAG_REGISTERED_WATTSON              (TRAINER_REGISTERED_FLAGS_START + REMATCH_WATTSON)
#define FLAG_REGISTERED_FLANNERY             (TRAINER_REGISTERED_FLAGS_START + REMATCH_FLANNERY)
#define FLAG_REGISTERED_NORMAN               (TRAINER_REGISTERED_FLAGS_START + REMATCH_NORMAN)
#define FLAG_REGISTERED_WINONA               (TRAINER_REGISTERED_FLAGS_START + REMATCH_WINONA)
#define FLAG_REGISTERED_TATE_AND_LIZA        (TRAINER_REGISTERED_FLAGS_START + REMATCH_TATE_AND_LIZA)
#define FLAG_REGISTERED_JUAN                 (TRAINER_REGISTERED_FLAGS_START + REMATCH_JUAN)
#define FLAG_REGISTERED_SIDNEY               (TRAINER_REGISTERED_FLAGS_START + REMATCH_SIDNEY)
#define FLAG_REGISTERED_PHOEBE               (TRAINER_REGISTERED_FLAGS_START + REMATCH_PHOEBE)
#define FLAG_REGISTERED_GLACIA               (TRAINER_REGISTERED_FLAGS_START + REMATCH_GLACIA)
#define FLAG_REGISTERED_DRAKE                (TRAINER_REGISTERED_FLAGS_START + REMATCH_DRAKE)
#define FLAG_REGISTERED_WALLACE              (TRAINER_REGISTERED_FLAGS_START + REMATCH_WALLACE)

#define FLAG_ORLEANS_POOL_162                           0x1AA
#define FLAG_ORLEANS_POOL_163                           0x1AB

#define FLAG_DEFEATED_DEOXYS                 0x1AC
#define FLAG_BATTLED_DEOXYS                  0x1AD
#define FLAG_SHOWN_EON_TICKET                0x1AE
#define FLAG_SHOWN_AURORA_TICKET             0x1AF
#define FLAG_SHOWN_OLD_SEA_MAP               0x1B0
#define FLAG_MOVE_TUTOR_TAUGHT_SWAGGER       0x1B1
#define FLAG_MOVE_TUTOR_TAUGHT_ROLLOUT       0x1B2
#define FLAG_MOVE_TUTOR_TAUGHT_FURY_CUTTER   0x1B3
#define FLAG_MOVE_TUTOR_TAUGHT_MIMIC         0x1B4
#define FLAG_MOVE_TUTOR_TAUGHT_METRONOME     0x1B5
#define FLAG_MOVE_TUTOR_TAUGHT_SLEEP_TALK    0x1B6
#define FLAG_MOVE_TUTOR_TAUGHT_SUBSTITUTE    0x1B7
#define FLAG_MOVE_TUTOR_TAUGHT_DYNAMICPUNCH  0x1B8
#define FLAG_MOVE_TUTOR_TAUGHT_DOUBLE_EDGE   0x1B9
#define FLAG_MOVE_TUTOR_TAUGHT_EXPLOSION     0x1BA
#define FLAG_ORLEANS_POOL_164                           0x1BB
#define FLAG_ORLEANS_POOL_165                           0x1BC
#define FLAG_ORLEANS_POOL_166                           0x1BD
#define FLAG_DEFEATED_KYOGRE                 0x1BE
#define FLAG_DEFEATED_GROUDON                0x1BF
#define FLAG_ORLEANS_POOL_167                           0x1C0
#define FLAG_ORLEANS_POOL_168                           0x1C1
#define FLAG_ORLEANS_POOL_169                           0x1C2
#define FLAG_ORLEANS_POOL_170                           0x1C3
#define FLAG_ORLEANS_POOL_171                           0x1C4
#define FLAG_ORLEANS_POOL_172                           0x1C5
#define FLAG_DEFEATED_SUDOWOODO              0x1C6
#define FLAG_DEFEATED_MEW                    0x1C7
#define FLAG_DEFEATED_LATIAS_OR_LATIOS       0x1C8
#define FLAG_ORLEANS_POOL_173                           0x1C9
#define FLAG_CAUGHT_MEW                      0x1CA
#define FLAG_ORLEANS_POOL_174                           0x1CB
#define FLAG_MET_SCOTT_IN_VERDANTURF         0x1CC
#define FLAG_MET_SCOTT_IN_FALLARBOR          0x1CD
#define FLAG_ORLEANS_POOL_175                           0x1CE
#define FLAG_ORLEANS_POOL_176                           0x1CF
#define FLAG_MET_SCOTT_ON_SS_TIDAL           0x1D0
#define FLAG_SCOTT_GIVES_BATTLE_POINTS       0x1D1
#define FLAG_COLLECTED_ALL_GOLD_SYMBOLS      0x1D2
#define FLAG_ENABLE_ROXANNE_MATCH_CALL       0x1D3
#define FLAG_ENABLE_BRAWLY_MATCH_CALL        0x1D4
#define FLAG_ENABLE_WATTSON_MATCH_CALL       0x1D5
#define FLAG_ENABLE_FLANNERY_MATCH_CALL      0x1D6
#define FLAG_ENABLE_WINONA_MATCH_CALL        0x1D7
#define FLAG_ENABLE_TATE_AND_LIZA_MATCH_CALL 0x1D8
#define FLAG_ENABLE_JUAN_MATCH_CALL          0x1D9

#define FLAG_ORLEANS_POOL_177                           0x1DA

#define FLAG_SHOWN_MYSTIC_TICKET             0x1DB
#define FLAG_DEFEATED_HO_OH                  0x1DC
#define FLAG_DEFEATED_LUGIA                  0x1DD

#define FLAG_HIDE_CRESCENT_LIEUTENANT      0x1DE // Orleans Ch3: the Drowned Ward lieutenant retreated and is gone for good
#define FLAG_CARVING_FOUND                   0x1DF // Orleans Ch3: the Drowned Ward carving was found (story 17)
#define FLAG_LAFAYETTE_REWARD_15             0x1E0 // Orleans Ch3: Lafayette's Bottle Cap (15 species) was given
#define FLAG_CRESCENT_ROTOM_MOW              0x1E1 // Orleans Ch3: the lawn-mower Rotom (Mow) was beaten or caught
#define FLAG_HIDE_CRESCENT_GYM_USHER         0x1E2 // Orleans Ch3: the usher in front of the gym, there until the market speech (story 15)
#define FLAG_DUST_STORMS_LIFTED              0x1E3 // Orleans: Rayquaza has woken (story 38); the Route 23 dust storms lift (set by that beat; Ch8)

// Mystery Gift Flags (Unknown)
#define FLAG_MYSTERY_GIFT_DONE               0x1E4
#define FLAG_MYSTERY_GIFT_1                  0x1E5
#define FLAG_MYSTERY_GIFT_2                  0x1E6
#define FLAG_MYSTERY_GIFT_3                  0x1E7
#define FLAG_MYSTERY_GIFT_4                  0x1E8
#define FLAG_MYSTERY_GIFT_5                  0x1E9
#define FLAG_MYSTERY_GIFT_6                  0x1EA
#define FLAG_MYSTERY_GIFT_7                  0x1EB
#define FLAG_MYSTERY_GIFT_8                  0x1EC
#define FLAG_MYSTERY_GIFT_9                  0x1ED
#define FLAG_MYSTERY_GIFT_10                 0x1EE
#define FLAG_MYSTERY_GIFT_11                 0x1EF
#define FLAG_MYSTERY_GIFT_12                 0x1F0
#define FLAG_MYSTERY_GIFT_13                 0x1F1
#define FLAG_MYSTERY_GIFT_14                 0x1F2
#define FLAG_MYSTERY_GIFT_15                 0x1F3

// Hidden Items
#define FLAG_HIDDEN_ITEMS_START                                                         0x1F4
#define FLAG_HIDDEN_ITEM_LAVARIDGE_TOWN_ICE_HEAL             (FLAG_HIDDEN_ITEMS_START + 0x00)
#define FLAG_HIDDEN_ITEM_TRICK_HOUSE_NUGGET                  (FLAG_HIDDEN_ITEMS_START + 0x01)
#define FLAG_HIDDEN_ITEM_ROUTE_111_STARDUST                  (FLAG_HIDDEN_ITEMS_START + 0x02)
#define FLAG_POINTE_HIDDEN_AUGURITE                      (FLAG_HIDDEN_ITEMS_START + 0x03) // Orleans Ch4: hidden items
#define FLAG_ROUTE4_HIDDEN_DUSK_STONE                    (FLAG_HIDDEN_ITEMS_START + 0x04) // Orleans Ch4: hidden items
#define FLAG_ROUTE5_HIDDEN_SUN_STONE                     (FLAG_HIDDEN_ITEMS_START + 0x05) // Orleans Ch4: hidden items
#define FLAG_CAMP_HIDDEN_PEAT_BLOCK                      (FLAG_HIDDEN_ITEMS_START + 0x06) // Orleans Ch5: hidden Peat Block at the camp
#define FLAG_ROUTE11_HIDDEN_ICE_STONE                    (FLAG_HIDDEN_ITEMS_START + 0x07) // Orleans Ch6: hidden Ice Stone on Route 11
#define FLAG_ORLEANS_POOL_183                           (FLAG_HIDDEN_ITEMS_START + 0x08)
#define FLAG_ORLEANS_POOL_184                           (FLAG_HIDDEN_ITEMS_START + 0x09)
#define FLAG_ORLEANS_POOL_185                           (FLAG_HIDDEN_ITEMS_START + 0x0A)
#define FLAG_ORLEANS_POOL_186                           (FLAG_HIDDEN_ITEMS_START + 0x0B)
#define FLAG_ORLEANS_POOL_187                           (FLAG_HIDDEN_ITEMS_START + 0x0C)
#define FLAG_ORLEANS_POOL_188                           (FLAG_HIDDEN_ITEMS_START + 0x0D)
#define FLAG_ORLEANS_POOL_189                           (FLAG_HIDDEN_ITEMS_START + 0x0E)
#define FLAG_ORLEANS_POOL_190                           (FLAG_HIDDEN_ITEMS_START + 0x0F)
#define FLAG_ORLEANS_POOL_191                           (FLAG_HIDDEN_ITEMS_START + 0x10)
#define FLAG_ORLEANS_POOL_192                           (FLAG_HIDDEN_ITEMS_START + 0x11)
#define FLAG_ORLEANS_POOL_193                           (FLAG_HIDDEN_ITEMS_START + 0x12)
#define FLAG_ORLEANS_POOL_194                           (FLAG_HIDDEN_ITEMS_START + 0x13)
#define FLAG_ORLEANS_POOL_195                           (FLAG_HIDDEN_ITEMS_START + 0x14)
#define FLAG_ORLEANS_POOL_196                           (FLAG_HIDDEN_ITEMS_START + 0x15)
#define FLAG_ORLEANS_POOL_197                           (FLAG_HIDDEN_ITEMS_START + 0x16)
#define FLAG_ORLEANS_POOL_198                           (FLAG_HIDDEN_ITEMS_START + 0x17)
#define FLAG_ORLEANS_POOL_199                           (FLAG_HIDDEN_ITEMS_START + 0x18)
#define FLAG_ORLEANS_POOL_200                           (FLAG_HIDDEN_ITEMS_START + 0x19)
#define FLAG_ORLEANS_POOL_201                           (FLAG_HIDDEN_ITEMS_START + 0x1A)
#define FLAG_ORLEANS_POOL_202                           (FLAG_HIDDEN_ITEMS_START + 0x1B)
#define FLAG_ORLEANS_POOL_203                           (FLAG_HIDDEN_ITEMS_START + 0x1C)
#define FLAG_ORLEANS_POOL_204                           (FLAG_HIDDEN_ITEMS_START + 0x1D)
#define FLAG_ORLEANS_POOL_205                           (FLAG_HIDDEN_ITEMS_START + 0x1E)
#define FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_1_KEY             (FLAG_HIDDEN_ITEMS_START + 0x1F)
#define FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_2_KEY             (FLAG_HIDDEN_ITEMS_START + 0x20)
#define FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_4_KEY             (FLAG_HIDDEN_ITEMS_START + 0x21)
#define FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_6_KEY             (FLAG_HIDDEN_ITEMS_START + 0x22)
#define FLAG_ORLEANS_POOL_206                           (FLAG_HIDDEN_ITEMS_START + 0x23)
#define FLAG_ORLEANS_POOL_207                           (FLAG_HIDDEN_ITEMS_START + 0x24)
#define FLAG_ORLEANS_POOL_208                           (FLAG_HIDDEN_ITEMS_START + 0x25)
#define FLAG_ORLEANS_POOL_209                           (FLAG_HIDDEN_ITEMS_START + 0x26)
#define FLAG_ORLEANS_POOL_210                           (FLAG_HIDDEN_ITEMS_START + 0x27)
#define FLAG_ORLEANS_POOL_211                           (FLAG_HIDDEN_ITEMS_START + 0x28)
#define FLAG_ORLEANS_POOL_212                           (FLAG_HIDDEN_ITEMS_START + 0x29)
#define FLAG_ORLEANS_POOL_213                           (FLAG_HIDDEN_ITEMS_START + 0x2A)
#define FLAG_ORLEANS_POOL_214                           (FLAG_HIDDEN_ITEMS_START + 0x2B)
#define FLAG_ORLEANS_POOL_215                           (FLAG_HIDDEN_ITEMS_START + 0x2C)
#define FLAG_ORLEANS_POOL_216                           (FLAG_HIDDEN_ITEMS_START + 0x2D)
#define FLAG_ORLEANS_POOL_217                           (FLAG_HIDDEN_ITEMS_START + 0x2E)
#define FLAG_ORLEANS_POOL_218                           (FLAG_HIDDEN_ITEMS_START + 0x2F)
#define FLAG_ORLEANS_POOL_219                           (FLAG_HIDDEN_ITEMS_START + 0x30)
#define FLAG_ORLEANS_POOL_220                           (FLAG_HIDDEN_ITEMS_START + 0x31)
#define FLAG_ORLEANS_POOL_221                           (FLAG_HIDDEN_ITEMS_START + 0x32)
#define FLAG_ORLEANS_POOL_222                           (FLAG_HIDDEN_ITEMS_START + 0x33)
#define FLAG_ORLEANS_POOL_223                           (FLAG_HIDDEN_ITEMS_START + 0x34)
#define FLAG_ORLEANS_POOL_224                           (FLAG_HIDDEN_ITEMS_START + 0x35)
#define FLAG_ORLEANS_POOL_225                           (FLAG_HIDDEN_ITEMS_START + 0x36)
#define FLAG_ORLEANS_POOL_226                           (FLAG_HIDDEN_ITEMS_START + 0x37)
#define FLAG_HIDDEN_ITEM_ROUTE_111_PROTEIN                   (FLAG_HIDDEN_ITEMS_START + 0x38)
#define FLAG_HIDDEN_ITEM_ROUTE_111_RARE_CANDY                (FLAG_HIDDEN_ITEMS_START + 0x39)
#define FLAG_ORLEANS_POOL_227                           (FLAG_HIDDEN_ITEMS_START + 0x3A)
#define FLAG_ORLEANS_POOL_228                           (FLAG_HIDDEN_ITEMS_START + 0x3B)
#define FLAG_ORLEANS_POOL_229                           (FLAG_HIDDEN_ITEMS_START + 0x3C)
#define FLAG_ORLEANS_POOL_230                           (FLAG_HIDDEN_ITEMS_START + 0x3D)
#define FLAG_ORLEANS_POOL_231                           (FLAG_HIDDEN_ITEMS_START + 0x3E)
#define FLAG_ORLEANS_POOL_232                           (FLAG_HIDDEN_ITEMS_START + 0x3F)
#define FLAG_ORLEANS_POOL_233                           (FLAG_HIDDEN_ITEMS_START + 0x40)
#define FLAG_ORLEANS_POOL_234                           (FLAG_HIDDEN_ITEMS_START + 0x41)
#define FLAG_ORLEANS_POOL_235                           (FLAG_HIDDEN_ITEMS_START + 0x42)
#define FLAG_ORLEANS_POOL_236                           (FLAG_HIDDEN_ITEMS_START + 0x43)
#define FLAG_ORLEANS_POOL_237                           (FLAG_HIDDEN_ITEMS_START + 0x44)
#define FLAG_ORLEANS_POOL_238                           (FLAG_HIDDEN_ITEMS_START + 0x45)
#define FLAG_ORLEANS_POOL_239                           (FLAG_HIDDEN_ITEMS_START + 0x46)
#define FLAG_ORLEANS_POOL_240                           (FLAG_HIDDEN_ITEMS_START + 0x47)
#define FLAG_ORLEANS_POOL_241                           (FLAG_HIDDEN_ITEMS_START + 0x48)
#define FLAG_ORLEANS_POOL_242                           (FLAG_HIDDEN_ITEMS_START + 0x49)
#define FLAG_ORLEANS_POOL_243                           (FLAG_HIDDEN_ITEMS_START + 0x4A)
#define FLAG_ORLEANS_POOL_244                           (FLAG_HIDDEN_ITEMS_START + 0x4B)
#define FLAG_ORLEANS_POOL_245                           (FLAG_HIDDEN_ITEMS_START + 0x4C)
#define FLAG_ORLEANS_POOL_246                           (FLAG_HIDDEN_ITEMS_START + 0x4D)
#define FLAG_ORLEANS_POOL_247                           (FLAG_HIDDEN_ITEMS_START + 0x4E)
#define FLAG_ORLEANS_POOL_248                           (FLAG_HIDDEN_ITEMS_START + 0x4F)
#define FLAG_ORLEANS_POOL_249                           (FLAG_HIDDEN_ITEMS_START + 0x50)
#define FLAG_ORLEANS_POOL_250                           (FLAG_HIDDEN_ITEMS_START + 0x51)
#define FLAG_ORLEANS_POOL_251                           (FLAG_HIDDEN_ITEMS_START + 0x52)
#define FLAG_ORLEANS_POOL_252                           (FLAG_HIDDEN_ITEMS_START + 0x53)
#define FLAG_ORLEANS_POOL_253                           (FLAG_HIDDEN_ITEMS_START + 0x54)
#define FLAG_ORLEANS_POOL_254                           (FLAG_HIDDEN_ITEMS_START + 0x55)
#define FLAG_ORLEANS_POOL_255                           (FLAG_HIDDEN_ITEMS_START + 0x56)
#define FLAG_ORLEANS_POOL_256                           (FLAG_HIDDEN_ITEMS_START + 0x57)
#define FLAG_ORLEANS_POOL_257                           (FLAG_HIDDEN_ITEMS_START + 0x58)
#define FLAG_ORLEANS_POOL_258                           (FLAG_HIDDEN_ITEMS_START + 0x59)
#define FLAG_ORLEANS_POOL_259                           (FLAG_HIDDEN_ITEMS_START + 0x5A)
#define FLAG_ORLEANS_POOL_260                           (FLAG_HIDDEN_ITEMS_START + 0x5B)
#define FLAG_ORLEANS_POOL_261                           (FLAG_HIDDEN_ITEMS_START + 0x5C)
#define FLAG_ORLEANS_POOL_262                           (FLAG_HIDDEN_ITEMS_START + 0x5D)
#define FLAG_ORLEANS_POOL_263                           (FLAG_HIDDEN_ITEMS_START + 0x5E)
#define FLAG_ORLEANS_POOL_264                           (FLAG_HIDDEN_ITEMS_START + 0x5F)
#define FLAG_HIDDEN_ITEM_ROUTE_116_BLACK_GLASSES             (FLAG_HIDDEN_ITEMS_START + 0x60)
#define FLAG_ORLEANS_POOL_265                           (FLAG_HIDDEN_ITEMS_START + 0x61)
#define FLAG_ORLEANS_POOL_266                           (FLAG_HIDDEN_ITEMS_START + 0x62)
#define FLAG_ORLEANS_POOL_267                           (FLAG_HIDDEN_ITEMS_START + 0x63)
#define FLAG_ORLEANS_POOL_268                           (FLAG_HIDDEN_ITEMS_START + 0x64)
#define FLAG_HIDDEN_ITEM_ARTISAN_CAVE_B1F_CALCIUM            (FLAG_HIDDEN_ITEMS_START + 0x65)
#define FLAG_HIDDEN_ITEM_ARTISAN_CAVE_B1F_ZINC               (FLAG_HIDDEN_ITEMS_START + 0x66)
#define FLAG_HIDDEN_ITEM_ARTISAN_CAVE_B1F_PROTEIN            (FLAG_HIDDEN_ITEMS_START + 0x67)
#define FLAG_HIDDEN_ITEM_ARTISAN_CAVE_B1F_IRON               (FLAG_HIDDEN_ITEMS_START + 0x68)
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_SOUTH_EAST_FULL_RESTORE (FLAG_HIDDEN_ITEMS_START + 0x69)
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_NORTH_EAST_RARE_CANDY   (FLAG_HIDDEN_ITEMS_START + 0x6A)
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_NORTH_EAST_ZINC         (FLAG_HIDDEN_ITEMS_START + 0x6B)
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_SOUTH_EAST_PP_UP        (FLAG_HIDDEN_ITEMS_START + 0x6C)
#define FLAG_ORLEANS_POOL_269                           (FLAG_HIDDEN_ITEMS_START + 0x6D)
#define FLAG_ORLEANS_POOL_270                           (FLAG_HIDDEN_ITEMS_START + 0x6E)
#define FLAG_ORLEANS_POOL_271                           (FLAG_HIDDEN_ITEMS_START + 0x6F)

#define FLAG_HIDDEN_ITEM_ISLE_MARAIS_CHURCHYARD  (FLAG_HIDDEN_ITEMS_START + 0x70)
#define FLAG_HIDDEN_ITEM_GRAND_OAK_GARDEN     (FLAG_HIDDEN_ITEMS_START + 0x71)
#define FLAG_HIDDEN_ITEM_GRAND_OAK_HOUSES     (FLAG_HIDDEN_ITEMS_START + 0x72)
#define FLAG_HIDDEN_ITEM_STORMS_EDGE_PIER     (FLAG_HIDDEN_ITEMS_START + 0x73)
#define FLAG_UNUSED_0x268  0x268 // Unused Flag
#define FLAG_UNUSED_0x269  0x269 // Unused Flag
#define FLAG_UNUSED_0x26A  0x26A // Unused Flag
#define FLAG_UNUSED_0x26B  0x26B // Unused Flag
#define FLAG_APARTMENT_UNLOCKED            0x26C // Orleans Ch3: 25 species contributed, the apartment is open
#define FLAG_HIDE_CRESCENT_LAFAYETTE       0x26D // Orleans Ch3: Lafayette outside the conservation center, there only while story 13 (set by Crescent's OnTransition)
#define FLAG_HIDE_CRESCENT_BASE_WREN       0x26E // Orleans Ch3: Wren inside the Drowned Ward base, there only while story 16 (set by the base's OnTransition)
#define FLAG_UNUSED_0x26F  0x26F // Unused Flag
#define FLAG_UNUSED_0x270  0x270 // Unused Flag
#define FLAG_UNUSED_0x271  0x271 // Unused Flag
#define FLAG_UNUSED_0x272  0x272 // Unused Flag
#define FLAG_UNUSED_0x273  0x273 // Unused Flag
#define FLAG_UNUSED_0x274  0x274 // Unused Flag
#define FLAG_UNUSED_0x275  0x275 // Unused Flag
#define FLAG_UNUSED_0x276  0x276 // Unused Flag
#define FLAG_UNUSED_0x277  0x277 // Unused Flag
#define FLAG_UNUSED_0x278  0x278 // Unused Flag
#define FLAG_UNUSED_0x279  0x279 // Unused Flag
#define FLAG_UNUSED_0x27A  0x27A // Unused Flag
#define FLAG_UNUSED_0x27B  0x27B // Unused Flag
#define FLAG_UNUSED_0x27C  0x27C // Unused Flag
#define FLAG_UNUSED_0x27D  0x27D // Unused Flag
#define FLAG_UNUSED_0x27E  0x27E // Unused Flag
#define FLAG_UNUSED_0x27F  0x27F // Unused Flag
#define FLAG_UNUSED_0x280  0x280 // Unused Flag
#define FLAG_UNUSED_0x281  0x281 // Unused Flag
#define FLAG_UNUSED_0x282  0x282 // Unused Flag
#define FLAG_UNUSED_0x283  0x283 // Unused Flag
#define FLAG_UNUSED_0x284  0x284 // Unused Flag
#define FLAG_UNUSED_0x285  0x285 // Unused Flag
#define FLAG_UNUSED_0x286  0x286 // Unused Flag
#define FLAG_UNUSED_0x287  0x287 // Unused Flag
#define FLAG_UNUSED_0x288  0x288 // Unused Flag
#define FLAG_UNUSED_0x289  0x289 // Unused Flag
#define FLAG_UNUSED_0x28A  0x28A // Unused Flag
#define FLAG_UNUSED_0x28B  0x28B // Unused Flag
#define FLAG_UNUSED_0x28C  0x28C // Unused Flag
#define FLAG_UNUSED_0x28D  0x28D // Unused Flag
#define FLAG_UNUSED_0x28E  0x28E // Unused Flag
#define FLAG_UNUSED_0x28F  0x28F // Unused Flag
#define FLAG_UNUSED_0x290  0x290 // Unused Flag
#define FLAG_UNUSED_0x291  0x291 // Unused Flag
#define FLAG_UNUSED_0x292  0x292 // Unused Flag
#define FLAG_UNUSED_0x293  0x293 // Unused Flag
#define FLAG_UNUSED_0x294  0x294 // Unused Flag
#define FLAG_UNUSED_0x295  0x295 // Unused Flag
#define FLAG_UNUSED_0x296  0x296 // Unused Flag
#define FLAG_UNUSED_0x297  0x297 // Unused Flag
#define FLAG_UNUSED_0x298  0x298 // Unused Flag
#define FLAG_UNUSED_0x299  0x299 // Unused Flag
#define FLAG_UNUSED_0x29A  0x29A // Unused Flag
#define FLAG_UNUSED_0x29B  0x29B // Unused Flag
#define FLAG_UNUSED_0x29C  0x29C // Unused Flag
#define FLAG_UNUSED_0x29D  0x29D // Unused Flag
#define FLAG_UNUSED_0x29E  0x29E // Unused Flag
#define FLAG_UNUSED_0x29F  0x29F // Unused Flag
#define FLAG_UNUSED_0x2A0  0x2A0 // Unused Flag
#define FLAG_UNUSED_0x2A1  0x2A1 // Unused Flag
#define FLAG_UNUSED_0x2A2  0x2A2 // Unused Flag
#define FLAG_UNUSED_0x2A3  0x2A3 // Unused Flag
#define FLAG_UNUSED_0x2A4  0x2A4 // Unused Flag
#define FLAG_UNUSED_0x2A5  0x2A5 // Unused Flag
#define FLAG_UNUSED_0x2A6  0x2A6 // Unused Flag
#define FLAG_UNUSED_0x2A7  0x2A7 // Unused Flag
#define FLAG_UNUSED_0x2A8  0x2A8 // Unused Flag
#define FLAG_UNUSED_0x2A9  0x2A9 // Unused Flag
#define FLAG_UNUSED_0x2AA  0x2AA // Unused Flag
#define FLAG_UNUSED_0x2AB  0x2AB // Unused Flag
#define FLAG_UNUSED_0x2AC  0x2AC // Unused Flag
#define FLAG_UNUSED_0x2AD  0x2AD // Unused Flag
#define FLAG_UNUSED_0x2AE  0x2AE // Unused Flag
#define FLAG_UNUSED_0x2AF  0x2AF // Unused Flag
#define FLAG_HIDE_CRESCENT_WREN            0x2B0 // Orleans Ch3: Wren at the Drowned Ward gate (hidden unless story 16; set by Crescent's OnTransition)
#define FLAG_RECEIVED_TM_SHADOW_BALL       0x2B1 // Orleans Ch3: Fifolet's TM Shadow Ball was handed over
#define FLAG_RECEIVED_LANTERN              0x2B2 // Orleans Ch3: the Lantern was handed over
#define FLAG_RECEIVED_MIMIKYU              0x2B3 // Orleans Ch3: Fifolet's Mimikyu was handed over
#define FLAG_RECEIVED_QUAXLY               0x2B4 // Orleans Ch3: the parade leader's Quaxly was handed over
#define FLAG_CRESCENT_ROTOM_TV             0x2B5 // Orleans Ch3: the market TV Rotom is gone (caught, beaten or fled)
#define FLAG_CRESCENT_ROTOM_BLENDER        0x2B6 // Orleans Ch3: the cafe blender Rotom is gone
#define FLAG_CRESCENT_ROTOM_WASHER         0x2B7 // Orleans Ch3: the laundry washer Rotom is gone
#define FLAG_CRESCENT_ROTOM_FREEZER        0x2B8 // Orleans Ch3: the ice-cream freezer Rotom is gone
#define FLAG_CRESCENT_ROTOM_GENERATOR      0x2B9 // Orleans Ch3: the waterfront generator Rotom is gone
#define FLAG_CARVING_SHOWN_TUPELO          0x2BA // Orleans Ch3: Tupelo has seen the damaged carving from the Drowned Ward
#define FLAG_LAFAYETTE_REWARD_10           0x2BB // Orleans Ch3: Lafayette's first conservation reward (10 species) was given

// Event Flags
#define FLAG_HIDE_ROUTE_101_BIRCH_STARTERS_BAG                      0x2BC
#define FLAG_HIDE_APPRENTICE                                        0x2BD
#define FLAG_HIDE_POKEMON_CENTER_2F_MYSTERY_GIFT_MAN                0x2BE
#define FLAG_ORLEANS_POOL_272                           0x2BF
#define FLAG_ORLEANS_POOL_273                           0x2C0
#define FLAG_ORLEANS_POOL_274                           0x2C1
#define FLAG_ORLEANS_POOL_275                           0x2C2
#define FLAG_ORLEANS_POOL_276                           0x2C3
#define FLAG_ORLEANS_POOL_277                           0x2C4
#define FLAG_ORLEANS_POOL_278                           0x2C5
#define FLAG_ORLEANS_POOL_279                           0x2C6
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_1               0x2C7
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_2               0x2C8
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_3               0x2C9
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_4               0x2CA
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_5               0x2CB
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_6               0x2CC
#define FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS            0x2CD
#define FLAG_HIDE_MEW                                               0x2CE
#define FLAG_ORLEANS_POOL_280                           0x2CF
#define FLAG_HIDE_ROUTE_101_BIRCH_ZIGZAGOON_BATTLE                  0x2D0
#define FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_BIRCH                  0x2D1
#define FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM          0x2D2
#define FLAG_ORLEANS_POOL_281                           0x2D3
#define FLAG_ORLEANS_POOL_282                           0x2D4
#define FLAG_ORLEANS_POOL_283                           0x2D5
#define FLAG_ORLEANS_POOL_284                           0x2D6
#define FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_INVISIBLE_NINJA_BOY   0x2D7
#define FLAG_ORLEANS_POOL_285                           0x2D8

#define FLAG_UNUSED_0x2D9                                           0x2D9 // Unused Flag

#define FLAG_HIDE_LILYCOVE_FAN_CLUB_INTERVIEWER                     0x2DA
#define FLAG_ORLEANS_POOL_286                           0x2DB
#define FLAG_ORLEANS_POOL_287                           0x2DC
#define FLAG_ORLEANS_POOL_288                           0x2DD
#define FLAG_HIDE_PLAYERS_HOUSE_DAD                                 0x2DE
#define FLAG_ORLEANS_POOL_289                           0x2DF
#define FLAG_ORLEANS_POOL_290                           0x2E0
#define FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_MAGMA_NOTE             0x2E1
#define FLAG_HIDE_ROUTE_104_MR_BRINEY                               0x2E2
#define FLAG_HIDE_BRINEYS_HOUSE_MR_BRINEY                           0x2E3
#define FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN                            0x2E4
#define FLAG_HIDE_ROUTE_109_MR_BRINEY                               0x2E5
#define FLAG_HIDE_ROUTE_104_MR_BRINEY_BOAT                          0x2E6
#define FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD_TOWN                       0x2E7
#define FLAG_HIDE_ROUTE_109_MR_BRINEY_BOAT                          0x2E8
#define FLAG_ORLEANS_POOL_291                           0x2E9
#define FLAG_ORLEANS_POOL_292                           0x2EA
#define FLAG_HIDE_SAFARI_ZONE_SOUTH_EAST_EXPANSION                  0x2EB
#define FLAG_ORLEANS_POOL_293                           0x2EC
#define FLAG_ORLEANS_POOL_294                           0x2ED
#define FLAG_ORLEANS_POOL_295                           0x2EE
#define FLAG_HIDE_VICTORY_ROAD_EXIT_WALLY                           0x2EF
#define FLAG_ORLEANS_POOL_296                           0x2F0
#define FLAG_ORLEANS_POOL_297                           0x2F1
#define FLAG_HIDE_LITTLEROOT_TOWN_PLAYERS_HOUSE_VIGOROTH_1          0x2F2
#define FLAG_HIDE_LITTLEROOT_TOWN_PLAYERS_HOUSE_VIGOROTH_2          0x2F3
#define FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_TEAM_MAGMA          0x2F4
#define FLAG_ORLEANS_POOL_298                           0x2F5
#define FLAG_ORLEANS_POOL_299                           0x2F6
#define FLAG_ORLEANS_POOL_300                           0x2F7
#define FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM      0x2F8
#define FLAG_ORLEANS_POOL_301                           0x2F9
#define FLAG_ORLEANS_POOL_302                           0x2FA
#define FLAG_ORLEANS_POOL_303                           0x2FB
#define FLAG_ORLEANS_POOL_304                           0x2FC
#define FLAG_ORLEANS_POOL_305                           0x2FD
#define FLAG_HIDE_VERDANTURF_TOWN_SCOTT                             0x2FE
#define FLAG_HIDE_FALLARBOR_TOWN_BATTLE_TENT_SCOTT                  0x2FF
#define FLAG_HIDE_ROUTE_111_VICTOR_WINSTRATE                        0x300
#define FLAG_HIDE_ROUTE_111_VICTORIA_WINSTRATE                      0x301
#define FLAG_HIDE_ROUTE_111_VIVI_WINSTRATE                          0x302
#define FLAG_HIDE_ROUTE_111_VICKY_WINSTRATE                         0x303
#define FLAG_ORLEANS_POOL_306                           0x304
#define FLAG_ORLEANS_POOL_307                           0x305
#define FLAG_ORLEANS_POOL_308                           0x306
#define FLAG_HIDE_LILYCOVE_MUSEUM_CURATOR                           0x307
#define FLAG_ORLEANS_POOL_309                           0x308
#define FLAG_ORLEANS_POOL_310                           0x309
#define FLAG_ORLEANS_POOL_311                           0x30A
#define FLAG_ORLEANS_POOL_312                           0x30B
#define FLAG_ORLEANS_POOL_313                           0x30C
#define FLAG_HIDE_PETALBURG_GYM_GREETER                             0x30D
#define FLAG_ORLEANS_POOL_314                           0x30E
#define FLAG_ORLEANS_POOL_315                           0x30F
#define FLAG_ORLEANS_POOL_316                           0x310
#define FLAG_ORLEANS_POOL_317                           0x311
#define FLAG_ORLEANS_POOL_318                           0x312
#define FLAG_ORLEANS_POOL_319                           0x313
#define FLAG_HIDE_MOSSDEEP_CITY_SCOTT                               0x314
#define FLAG_HIDE_FANCLUB_OLD_LADY                                  0x315
#define FLAG_HIDE_FANCLUB_BOY                                       0x316
#define FLAG_HIDE_FANCLUB_LITTLE_BOY                                0x317
#define FLAG_HIDE_FANCLUB_LADY                                      0x318
#define FLAG_ORLEANS_POOL_320                           0x319
#define FLAG_ORLEANS_POOL_321                           0x31A
#define FLAG_ORLEANS_POOL_322                           0x31B
#define FLAG_HIDE_ROUTE_111_GABBY_AND_TY_1                          0x31C
#define FLAG_HIDE_ROUTE_118_GABBY_AND_TY_1                          0x31D
#define FLAG_HIDE_ROUTE_120_GABBY_AND_TY_1                          0x31E
#define FLAG_HIDE_ROUTE_111_GABBY_AND_TY_2                          0x31F
#define FLAG_ORLEANS_POOL_323                           0x320
#define FLAG_ORLEANS_POOL_324                           0x321
#define FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER                    0x322
#define FLAG_ORLEANS_POOL_325                           0x323
#define FLAG_HIDE_MAUVILLE_CITY_WALLY                               0x324
#define FLAG_ORLEANS_POOL_326                           0x325
#define FLAG_ORLEANS_POOL_327                           0x326
#define FLAG_ORLEANS_POOL_328                           0x327
#define FLAG_HIDE_VERDANTURF_TOWN_WANDAS_HOUSE_WANDAS_BOYFRIEND     0x328
#define FLAG_ORLEANS_POOL_329                           0x329
#define FLAG_ORLEANS_POOL_330                           0x32A
#define FLAG_ORLEANS_POOL_331                           0x32B
#define FLAG_ORLEANS_POOL_332                           0x32C
#define FLAG_ORLEANS_POOL_333                           0x32D
#define FLAG_ORLEANS_POOL_334                           0x32E
#define FLAG_ORLEANS_POOL_335                           0x32F
#define FLAG_ORLEANS_POOL_336                           0x330
#define FLAG_ORLEANS_POOL_337                           0x331
#define FLAG_ORLEANS_POOL_338                           0x332
#define FLAG_ORLEANS_POOL_339                           0x333
#define FLAG_ORLEANS_POOL_340                           0x334
#define FLAG_ORLEANS_POOL_341                           0x335
#define FLAG_ORLEANS_POOL_342                           0x336
#define FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA                          0x337
#define FLAG_ORLEANS_POOL_343                           0x338
#define FLAG_ORLEANS_POOL_344                           0x339
#define FLAG_ORLEANS_POOL_345                           0x33A
#define FLAG_ORLEANS_POOL_346                           0x33B
#define FLAG_ORLEANS_POOL_347                           0x33C
#define FLAG_ORLEANS_POOL_348                           0x33D
#define FLAG_ORLEANS_POOL_349                           0x33E
#define FLAG_ORLEANS_POOL_350                           0x33F
#define FLAG_HIDE_LILYCOVE_CONTEST_HALL_BLEND_MASTER                0x340
#define FLAG_ORLEANS_POOL_351                           0x341
#define FLAG_ORLEANS_POOL_352                           0x342
#define FLAG_ORLEANS_POOL_353                           0x343
#define FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT              0x344
#define FLAG_ORLEANS_POOL_354                           0x345
#define FLAG_ORLEANS_POOL_355                           0x346
#define FLAG_ORLEANS_POOL_356                           0x347
#define FLAG_ORLEANS_POOL_357                           0x348
#define FLAG_ORLEANS_POOL_358                           0x349
#define FLAG_HIDE_BATTLE_FRONTIER_SUDOWOODO                         0x34A
#define FLAG_HIDE_ROUTE_111_ROCK_SMASH_TIP_GUY                      0x34B
#define FLAG_ORLEANS_POOL_359                           0x34C
#define FLAG_ORLEANS_POOL_360                           0x34D
#define FLAG_ORLEANS_POOL_361                           0x34E
#define FLAG_ORLEANS_POOL_362                           0x34F
#define FLAG_ORLEANS_POOL_363                           0x350
#define FLAG_ORLEANS_POOL_364                           0x351
#define FLAG_ORLEANS_POOL_365                           0x352
#define FLAG_ORLEANS_POOL_366                           0x353
#define FLAG_ORLEANS_POOL_367                           0x354
#define FLAG_ORLEANS_POOL_368                           0x355
#define FLAG_ORLEANS_POOL_369                           0x356
#define FLAG_ORLEANS_POOL_370                           0x357
#define FLAG_ORLEANS_POOL_371                           0x358
#define FLAG_ORLEANS_POOL_372                           0x359
#define FLAG_HIDE_VICTORY_ROAD_ENTRANCE_WALLY                       0x35A
#define FLAG_ORLEANS_POOL_373                           0x35B
#define FLAG_HIDE_SLATEPORT_CITY_HARBOR_SS_TIDAL                    0x35C
#define FLAG_HIDE_LILYCOVE_HARBOR_SSTIDAL                           0x35D
#define FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA          0x35E
#define FLAG_ORLEANS_POOL_374                           0x35F
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_ALT_1           0x360
#define FLAG_HIDE_BATTLE_TOWER_MULTI_BATTLE_PARTNER_ALT_2           0x361
#define FLAG_ORLEANS_POOL_375                           0x362
#define FLAG_ORLEANS_POOL_376                           0x363
#define FLAG_ORLEANS_POOL_377                           0x364
#define FLAG_HIDE_SLATEPORT_CITY_STERNS_SHIPYARD_MR_BRINEY          0x365
#define FLAG_ORLEANS_POOL_378                           0x366
#define FLAG_ORLEANS_POOL_379                           0x367
#define FLAG_ORLEANS_POOL_380                           0x368
#define FLAG_ORLEANS_POOL_381                           0x369
#define FLAG_HIDE_DESERT_UNDERPASS_FOSSIL                           0x36A
#define FLAG_HIDE_ROUTE_111_PLAYER_DESCENT                          0x36B
#define FLAG_HIDE_ROUTE_111_DESERT_FOSSIL                           0x36C
#define FLAG_ORLEANS_POOL_382                           0x36D
#define FLAG_ORLEANS_POOL_383                           0x36E
#define FLAG_ORLEANS_POOL_384                           0x36F
#define FLAG_ORLEANS_POOL_385                           0x370
#define FLAG_HIDE_BRINEYS_HOUSE_PEEKO                               0x371
#define FLAG_ORLEANS_POOL_386                           0x372
#define FLAG_ORLEANS_POOL_387                           0x373
#define FLAG_ORLEANS_POOL_388                           0x374
#define FLAG_ORLEANS_POOL_389                           0x375
#define FLAG_ORLEANS_POOL_390                           0x376
#define FLAG_ORLEANS_POOL_391                           0x377
#define FLAG_HIDE_BATTLE_TOWER_OPPONENT                             0x378
#define FLAG_ORLEANS_POOL_392                           0x379
#define FLAG_ORLEANS_POOL_393                           0x37A
#define FLAG_HIDE_ROUTE_116_MR_BRINEY                               0x37B
#define FLAG_ORLEANS_POOL_394                           0x37C
#define FLAG_ORLEANS_POOL_395                           0x37D
#define FLAG_ORLEANS_POOL_396                           0x37E
#define FLAG_ORLEANS_POOL_397                           0x37F
#define FLAG_HIDE_LITTLEROOT_TOWN_BIRCHS_LAB_UNKNOWN_0x380          0x380
#define FLAG_HIDE_ROUTE_101_BIRCH                                   0x381
#define FLAG_HIDE_ROUTE_103_BIRCH                                   0x382
#define FLAG_ORLEANS_POOL_398                           0x383
#define FLAG_ORLEANS_POOL_399                           0x384
#define FLAG_HIDE_ROUTE_118_GABBY_AND_TY_2                          0x385
#define FLAG_HIDE_ROUTE_120_GABBY_AND_TY_2                          0x386
#define FLAG_HIDE_ROUTE_111_GABBY_AND_TY_3                          0x387
#define FLAG_HIDE_ROUTE_118_GABBY_AND_TY_3                          0x388
#define FLAG_ORLEANS_POOL_400                           0x389
#define FLAG_ORLEANS_POOL_401                           0x38A
#define FLAG_ORLEANS_POOL_402                           0x38B
#define FLAG_ORLEANS_POOL_403                           0x38C
#define FLAG_ORLEANS_POOL_404                           0x38D
#define FLAG_ORLEANS_POOL_405                           0x38E
#define FLAG_ORLEANS_POOL_406                           0x38F
#define FLAG_ORLEANS_POOL_407                           0x390
#define FLAG_ORLEANS_POOL_408                           0x391
#define FLAG_ORLEANS_POOL_409                           0x392
#define FLAG_ORLEANS_POOL_410                           0x393
#define FLAG_ORLEANS_POOL_411                           0x394
#define FLAG_ORLEANS_POOL_412                           0x395
#define FLAG_HIDE_BATTLE_TOWER_REPORTER                             0x396
#define FLAG_ORLEANS_POOL_413                           0x397
#define FLAG_ORLEANS_POOL_414                           0x398
#define FLAG_ORLEANS_POOL_415                           0x399
#define FLAG_ORLEANS_POOL_416                           0x39A
#define FLAG_ORLEANS_POOL_417                           0x39B
#define FLAG_ORLEANS_POOL_418                           0x39C
#define FLAG_HIDE_LILYCOVE_MOTEL_GAME_DESIGNERS                     0x39D
#define FLAG_ORLEANS_POOL_419                           0x39E
#define FLAG_ORLEANS_POOL_420                           0x39F
#define FLAG_ORLEANS_POOL_421                           0x3A0
#define FLAG_ORLEANS_POOL_422                           0x3A1
#define FLAG_ORLEANS_POOL_423                           0x3A2
#define FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1                             0x3A3
#define FLAG_HIDE_RUSTURF_TUNNEL_ROCK_2                             0x3A4
#define FLAG_ORLEANS_POOL_424                           0x3A5
#define FLAG_ORLEANS_POOL_425                           0x3A6
#define FLAG_ORLEANS_POOL_426                           0x3A7
#define FLAG_ORLEANS_POOL_427                           0x3A8
#define FLAG_ORLEANS_POOL_428                           0x3A9
#define FLAG_ORLEANS_POOL_429                           0x3AA
#define FLAG_ORLEANS_POOL_430                           0x3AB
#define FLAG_ORLEANS_POOL_431                           0x3AC
#define FLAG_ORLEANS_POOL_432                           0x3AD
#define FLAG_ORLEANS_POOL_433                           0x3AE
#define FLAG_ORLEANS_POOL_434                           0x3AF
#define FLAG_ORLEANS_POOL_435                           0x3B0
#define FLAG_ORLEANS_POOL_436                           0x3B1
#define FLAG_ORLEANS_POOL_437                           0x3B2
#define FLAG_ORLEANS_POOL_438                           0x3B3
#define FLAG_HIDE_SLATEPORT_CITY_TM_SALESMAN                        0x3B4
#define FLAG_ORLEANS_POOL_439                           0x3B5
#define FLAG_HIDE_SS_TIDAL_CORRIDOR_MR_BRINEY                       0x3B6
#define FLAG_ORLEANS_POOL_440                           0x3B7
#define FLAG_ORLEANS_POOL_441                           0x3B8
#define FLAG_ORLEANS_POOL_442                           0x3B9
#define FLAG_ORLEANS_POOL_443                           0x3BA
#define FLAG_ORLEANS_POOL_444                           0x3BB
#define FLAG_ORLEANS_POOL_445                           0x3BC
#define FLAG_ORLEANS_POOL_446                           0x3BD
#define FLAG_ORLEANS_POOL_447                           0x3BE
#define FLAG_ORLEANS_POOL_448                           0x3BF
#define FLAG_HIDE_ROUTE_111_SECRET_POWER_MAN                        0x3C0
#define FLAG_ORLEANS_POOL_449                           0x3C1
#define FLAG_ORLEANS_POOL_450                           0x3C2
#define FLAG_ORLEANS_POOL_451                           0x3C3
#define FLAG_ORLEANS_POOL_452                           0x3C4
#define FLAG_ORLEANS_POOL_453                           0x3C5
#define FLAG_ORLEANS_POOL_454                           0x3C6
#define FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_STEVEN                0x3C7
#define FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_BELDUM_POKEBALL       0x3C8
#define FLAG_ORLEANS_POOL_455                           0x3C9
#define FLAG_ORLEANS_POOL_456                           0x3CA
#define FLAG_HIDE_LILYCOVE_CITY_RIVAL                               0x3CB
#define FLAG_ORLEANS_POOL_457                           0x3CC
#define FLAG_ORLEANS_POOL_458                           0x3CD
#define FLAG_ORLEANS_POOL_459                           0x3CE
#define FLAG_ORLEANS_POOL_460                           0x3CF
#define FLAG_ORLEANS_POOL_461                           0x3D0
#define FLAG_ORLEANS_POOL_462                           0x3D1
#define FLAG_ORLEANS_POOL_463                           0x3D2
#define FLAG_ORLEANS_POOL_464                           0x3D3
#define FLAG_ORLEANS_POOL_465                           0x3D4
#define FLAG_ORLEANS_POOL_466                           0x3D5
#define FLAG_ORLEANS_POOL_467                           0x3D6
#define FLAG_ORLEANS_POOL_468                           0x3D7
#define FLAG_HIDE_VERDANTURF_TOWN_WANDAS_HOUSE_WANDA                0x3D8
#define FLAG_ORLEANS_POOL_469                           0x3D9
#define FLAG_ORLEANS_POOL_470                           0x3DA
#define FLAG_ORLEANS_POOL_471                           0x3DB
#define FLAG_ORLEANS_POOL_472                           0x3DC
#define FLAG_ORLEANS_POOL_473                           0x3DD
#define FLAG_ORLEANS_POOL_474                           0x3DE
#define FLAG_ORLEANS_POOL_475                           0x3DF
#define FLAG_ORLEANS_POOL_476                           0x3E0
#define FLAG_ORLEANS_POOL_477                           0x3E1
#define FLAG_ORLEANS_POOL_478                           0x3E2
#define FLAG_ORLEANS_POOL_479                           0x3E3
#define FLAG_HIDE_SOOTOPOLIS_CITY_RAYQUAZA                          0x3E4
#define FLAG_ORLEANS_POOL_480                           0x3E5
#define FLAG_ORLEANS_POOL_481                           0x3E6
#define FLAG_ORLEANS_POOL_482                           0x3E7

// Item Ball Flags
#define FLAG_ITEM_ROUTE_102_POTION                                  0x3E8
#define FLAG_UNUSED_0x3E9                               0x3E9
#define FLAG_UNUSED_0x3EA                               0x3EA
#define FLAG_UNUSED_0x3EB                               0x3EB
#define FLAG_UNUSED_0x3EC                               0x3EC
#define FLAG_UNUSED_0x3ED                               0x3ED
#define FLAG_UNUSED_0x3EE                               0x3EE
#define FLAG_UNUSED_0x3EF                               0x3EF
#define FLAG_ITEM_ROUTE_111_TM_SANDSTORM                            0x3F0
#define FLAG_ITEM_ROUTE_111_STARDUST                                0x3F1
#define FLAG_ITEM_ROUTE_111_HP_UP                                   0x3F2
#define FLAG_UNUSED_0x3F3                               0x3F3
#define FLAG_UNUSED_0x3F4                               0x3F4
#define FLAG_UNUSED_0x3F5                               0x3F5
#define FLAG_UNUSED_0x3F6                               0x3F6
#define FLAG_UNUSED_0x3F7                               0x3F7
#define FLAG_UNUSED_0x3F8                               0x3F8
#define FLAG_UNUSED_0x3F9                               0x3F9
#define FLAG_UNUSED_0x3FA                               0x3FA
#define FLAG_UNUSED_0x3FB                               0x3FB
#define FLAG_UNUSED_0x3FC                               0x3FC
#define FLAG_UNUSED_0x3FD                               0x3FD
#define FLAG_UNUSED_0x3FE                               0x3FE
#define FLAG_UNUSED_0x3FF                               0x3FF
#define FLAG_UNUSED_0x400                               0x400
#define FLAG_UNUSED_0x401                               0x401
#define FLAG_UNUSED_0x402                               0x402
#define FLAG_UNUSED_0x403                               0x403
#define FLAG_UNUSED_0x404                               0x404
#define FLAG_UNUSED_0x405                               0x405
#define FLAG_UNUSED_0x406                               0x406
#define FLAG_UNUSED_0x407                               0x407
#define FLAG_UNUSED_0x408                               0x408
#define FLAG_UNUSED_0x409                               0x409
#define FLAG_UNUSED_0x40A                               0x40A
#define FLAG_UNUSED_0x40B                               0x40B
#define FLAG_UNUSED_0x40C                               0x40C
#define FLAG_UNUSED_0x40D                               0x40D
#define FLAG_UNUSED_0x40E                               0x40E
#define FLAG_UNUSED_0x40F                               0x40F
#define FLAG_UNUSED_0x410                               0x410
#define FLAG_UNUSED_0x411                               0x411
#define FLAG_UNUSED_0x412                               0x412
#define FLAG_UNUSED_0x413                               0x413
#define FLAG_UNUSED_0x414                               0x414
#define FLAG_UNUSED_0x415                               0x415
#define FLAG_UNUSED_0x416                               0x416
#define FLAG_UNUSED_0x417                               0x417
#define FLAG_UNUSED_0x418                               0x418
#define FLAG_UNUSED_0x419                               0x419
#define FLAG_UNUSED_0x41A                               0x41A
#define FLAG_UNUSED_0x41B                               0x41B
#define FLAG_UNUSED_0x41C                               0x41C
#define FLAG_UNUSED_0x41D                               0x41D
#define FLAG_UNUSED_0x41E                               0x41E
#define FLAG_UNUSED_0x41F                               0x41F
#define FLAG_UNUSED_0x420                               0x420
#define FLAG_UNUSED_0x421                               0x421
#define FLAG_UNUSED_0x422                               0x422
#define FLAG_UNUSED_0x423                               0x423
#define FLAG_UNUSED_0x424                               0x424
#define FLAG_UNUSED_0x425                               0x425
#define FLAG_UNUSED_0x426                               0x426
#define FLAG_UNUSED_0x427                               0x427
#define FLAG_UNUSED_0x428                               0x428
#define FLAG_UNUSED_0x429                               0x429
#define FLAG_UNUSED_0x42A                               0x42A
#define FLAG_UNUSED_0x42B                               0x42B
#define FLAG_UNUSED_0x42C                               0x42C
#define FLAG_UNUSED_0x42D                               0x42D
#define FLAG_UNUSED_0x42E                               0x42E
#define FLAG_UNUSED_0x42F                               0x42F
#define FLAG_UNUSED_0x430                               0x430
#define FLAG_UNUSED_0x431                               0x431
#define FLAG_UNUSED_0x432                               0x432
#define FLAG_UNUSED_0x433                               0x433
#define FLAG_UNUSED_0x434                               0x434
#define FLAG_UNUSED_0x435                               0x435
#define FLAG_UNUSED_0x436                               0x436
#define FLAG_UNUSED_0x437                               0x437
#define FLAG_UNUSED_0x438                               0x438
#define FLAG_UNUSED_0x439                               0x439
#define FLAG_UNUSED_0x43A                               0x43A
#define FLAG_UNUSED_0x43B                               0x43B
#define FLAG_UNUSED_0x43C                               0x43C
#define FLAG_UNUSED_0x43D                               0x43D
#define FLAG_UNUSED_0x43E                               0x43E
#define FLAG_UNUSED_0x43F                               0x43F
#define FLAG_UNUSED_0x440                               0x440
#define FLAG_UNUSED_0x441                               0x441
#define FLAG_UNUSED_0x442                               0x442
#define FLAG_UNUSED_0x443                               0x443
#define FLAG_UNUSED_0x444                               0x444
#define FLAG_UNUSED_0x445                               0x445
#define FLAG_ITEM_SAFARI_ZONE_NORTH_WEST_TM_SOLAR_BEAM              0x446
#define FLAG_UNUSED_0x447                               0x447
#define FLAG_UNUSED_0x448                               0x448
#define FLAG_UNUSED_0x449                               0x449
#define FLAG_UNUSED_0x44A                               0x44A
#define FLAG_UNUSED_0x44B                               0x44B
#define FLAG_ITEM_ABANDONED_SHIP_CAPTAINS_OFFICE_STORAGE_KEY        0x44C
#define FLAG_UNUSED_0x44D                               0x44D
#define FLAG_UNUSED_0x44E                               0x44E
#define FLAG_UNUSED_0x44F                               0x44F
#define FLAG_UNUSED_0x450                               0x450
#define FLAG_UNUSED_0x451                               0x451
#define FLAG_UNUSED_0x452                               0x452
#define FLAG_UNUSED_0x453                               0x453
#define FLAG_UNUSED_0x454                               0x454
#define FLAG_UNUSED_0x455                               0x455
#define FLAG_UNUSED_0x456                               0x456
#define FLAG_UNUSED_0x457                               0x457
#define FLAG_UNUSED_0x458                               0x458
#define FLAG_UNUSED_0x459                               0x459
#define FLAG_UNUSED_0x45A                               0x45A
#define FLAG_UNUSED_0x45B                               0x45B
#define FLAG_UNUSED_0x45C                               0x45C
#define FLAG_UNUSED_0x45D                               0x45D
#define FLAG_UNUSED_0x45E                               0x45E
#define FLAG_ITEM_SAFARI_ZONE_NORTH_CALCIUM                         0x45F
#define FLAG_UNUSED_0x460                               0x460
#define FLAG_UNUSED_0x461                               0x461
#define FLAG_UNUSED_0x462                               0x462
#define FLAG_UNUSED_0x463                               0x463
#define FLAG_UNUSED_0x464                               0x464
#define FLAG_UNUSED_0x465                               0x465
#define FLAG_UNUSED_0x466                               0x466
#define FLAG_UNUSED_0x467                               0x467
#define FLAG_UNUSED_0x468                                           0x468 // Unused Flag
#define FLAG_UNUSED_0x469                               0x469
#define FLAG_UNUSED_0x46A                               0x46A
#define FLAG_ITEM_SAFARI_ZONE_SOUTH_WEST_MAX_REVIVE                 0x46B
#define FLAG_ITEM_AQUA_HIDEOUT_B1F_NUGGET                           0x46C
#define FLAG_UNUSED_0x46D                               0x46D
#define FLAG_UNUSED_0x46E                               0x46E
#define FLAG_UNUSED_0x46F                               0x46F
#define FLAG_UNUSED_0x470                                           0x470 // Unused Flag
#define FLAG_UNUSED_0x471                               0x471
#define FLAG_UNUSED_0x472                                           0x472 // Unused Flag
#define FLAG_UNUSED_0x473                               0x473
#define FLAG_UNUSED_0x474                               0x474
#define FLAG_UNUSED_0x475                               0x475
#define FLAG_ITEM_ROUTE_111_ELIXIR                                  0x476
#define FLAG_UNUSED_0x477                               0x477
#define FLAG_UNUSED_0x478                               0x478
#define FLAG_UNUSED_0x479                                           0x479 // Unused Flag
#define FLAG_UNUSED_0x47A                               0x47A
#define FLAG_UNUSED_0x47B                               0x47B
#define FLAG_UNUSED_0x47C                               0x47C
#define FLAG_UNUSED_0x47D                               0x47D
#define FLAG_UNUSED_0x47E                               0x47E
#define FLAG_UNUSED_0x47F                               0x47F
#define FLAG_UNUSED_0x480                               0x480
#define FLAG_UNUSED_0x481                               0x481
#define FLAG_UNUSED_0x482                               0x482
#define FLAG_UNUSED_0x483                               0x483
#define FLAG_UNUSED_0x484                               0x484
#define FLAG_UNUSED_0x485                               0x485
#define FLAG_UNUSED_0x486                               0x486
#define FLAG_UNUSED_0x487                               0x487
#define FLAG_UNUSED_0x488                               0x488
#define FLAG_UNUSED_0x489                               0x489
#define FLAG_ITEM_ARTISAN_CAVE_B1F_HP_UP                            0x48A
#define FLAG_ITEM_ARTISAN_CAVE_1F_CARBOS                            0x48B
#define FLAG_UNUSED_0x48C                               0x48C
#define FLAG_UNUSED_0x48D                               0x48D
#define FLAG_UNUSED_0x48E                               0x48E
#define FLAG_UNUSED_0x48F                               0x48F
#define FLAG_UNUSED_0x490                               0x490
#define FLAG_ITEM_SAFARI_ZONE_NORTH_EAST_NUGGET                     0x491
#define FLAG_ITEM_SAFARI_ZONE_SOUTH_EAST_BIG_PEARL                  0x492

#define FLAG_UNUSED_0x493                                           0x493 // Unused Flag
#define FLAG_UNUSED_0x494                                           0x494 // Unused Flag
#define FLAG_UNUSED_0x495                                           0x495 // Unused Flag
#define FLAG_UNUSED_0x496                                           0x496 // Unused Flag
#define FLAG_UNUSED_0x497                                           0x497 // Unused Flag
#define FLAG_UNUSED_0x498                                           0x498 // Unused Flag
#define FLAG_UNUSED_0x499                                           0x499 // Unused Flag
#define FLAG_UNUSED_0x49A                                           0x49A // Unused Flag
#define FLAG_UNUSED_0x49B                                           0x49B // Unused Flag
#define FLAG_UNUSED_0x49C                                           0x49C // Unused Flag
#define FLAG_UNUSED_0x49D                                           0x49D // Unused Flag
#define FLAG_UNUSED_0x49E                                           0x49E // Unused Flag
#define FLAG_UNUSED_0x49F                                           0x49F // Unused Flag
#define FLAG_UNUSED_0x4A0                                           0x4A0 // Unused Flag
#define FLAG_UNUSED_0x4A1                                           0x4A1 // Unused Flag
#define FLAG_UNUSED_0x4A2                                           0x4A2 // Unused Flag
#define FLAG_UNUSED_0x4A3                                           0x4A3 // Unused Flag
#define FLAG_UNUSED_0x4A4                                           0x4A4 // Unused Flag
#define FLAG_UNUSED_0x4A5                                           0x4A5 // Unused Flag
#define FLAG_UNUSED_0x4A6                                           0x4A6 // Unused Flag
#define FLAG_UNUSED_0x4A7                                           0x4A7 // Unused Flag
#define FLAG_UNUSED_0x4A8                                           0x4A8 // Unused Flag
#define FLAG_UNUSED_0x4A9                                           0x4A9 // Unused Flag
#define FLAG_UNUSED_0x4AA                                           0x4AA // Unused Flag
#define FLAG_UNUSED_0x4AB                                           0x4AB // Unused Flag
#define FLAG_UNUSED_0x4AC                                           0x4AC // Unused Flag
#define FLAG_UNUSED_0x4AD                                           0x4AD // Unused Flag
#define FLAG_UNUSED_0x4AE                                           0x4AE // Unused Flag
#define FLAG_UNUSED_0x4AF                                           0x4AF // Unused Flag
#define FLAG_UNUSED_0x4B0                                           0x4B0 // Unused Flag
#define FLAG_UNUSED_0x4B1                                           0x4B1 // Unused Flag
#define FLAG_UNUSED_0x4B2                                           0x4B2 // Unused Flag
#define FLAG_UNUSED_0x4B3                                           0x4B3 // Unused Flag
#define FLAG_UNUSED_0x4B4                                           0x4B4 // Unused Flag
#define FLAG_UNUSED_0x4B5                                           0x4B5 // Unused Flag
#define FLAG_UNUSED_0x4B6                                           0x4B6 // Unused Flag
#define FLAG_UNUSED_0x4B7                                           0x4B7 // Unused Flag
#define FLAG_UNUSED_0x4B8                                           0x4B8 // Unused Flag
#define FLAG_UNUSED_0x4B9                                           0x4B9 // Unused Flag
#define FLAG_UNUSED_0x4BA                                           0x4BA // Unused Flag
#define FLAG_UNUSED_0x4BB                                           0x4BB // Unused Flag
#define FLAG_UNUSED_0x4BC                                           0x4BC // Unused Flag
#define FLAG_UNUSED_0x4BD                                           0x4BD // Unused Flag
#define FLAG_UNUSED_0x4BE                                           0x4BE // Unused Flag
#define FLAG_UNUSED_0x4BF                                           0x4BF // Unused Flag
#define FLAG_UNUSED_0x4C0                                           0x4C0 // Unused Flag
#define FLAG_UNUSED_0x4C1                                           0x4C1 // Unused Flag
#define FLAG_UNUSED_0x4C2                                           0x4C2 // Unused Flag
#define FLAG_UNUSED_0x4C3                                           0x4C3 // Unused Flag
#define FLAG_UNUSED_0x4C4                                           0x4C4 // Unused Flag
#define FLAG_UNUSED_0x4C5                                           0x4C5 // Unused Flag
#define FLAG_UNUSED_0x4C6                                           0x4C6 // Unused Flag
#define FLAG_UNUSED_0x4C7                                           0x4C7 // Unused Flag
#define FLAG_UNUSED_0x4C8                                           0x4C8 // Unused Flag
#define FLAG_UNUSED_0x4C9                                           0x4C9 // Unused Flag
#define FLAG_UNUSED_0x4CA                                           0x4CA // Unused Flag
#define FLAG_UNUSED_0x4CB                                           0x4CB // Unused Flag
#define FLAG_UNUSED_0x4CC                                           0x4CC // Unused Flag
#define FLAG_UNUSED_0x4CD                                           0x4CD // Unused Flag
#define FLAG_UNUSED_0x4CE                                           0x4CE // Unused Flag
#define FLAG_UNUSED_0x4CF                                           0x4CF // Unused Flag
#define FLAG_UNUSED_0x4D0                                           0x4D0 // Unused Flag
#define FLAG_UNUSED_0x4D1                                           0x4D1 // Unused Flag
#define FLAG_UNUSED_0x4D2                                           0x4D2 // Unused Flag
#define FLAG_UNUSED_0x4D3                                           0x4D3 // Unused Flag
#define FLAG_UNUSED_0x4D4                                           0x4D4 // Unused Flag
#define FLAG_UNUSED_0x4D5                                           0x4D5 // Unused Flag
#define FLAG_UNUSED_0x4D6                                           0x4D6 // Unused Flag
#define FLAG_UNUSED_0x4D7                                           0x4D7 // Unused Flag
#define FLAG_UNUSED_0x4D8                                           0x4D8 // Unused Flag
#define FLAG_UNUSED_0x4D9                                           0x4D9 // Unused Flag
#define FLAG_UNUSED_0x4DA                                           0x4DA // Unused Flag
#define FLAG_UNUSED_0x4DB                                           0x4DB // Unused Flag
#define FLAG_UNUSED_0x4DC                                           0x4DC // Unused Flag
#define FLAG_UNUSED_0x4DD                                           0x4DD // Unused Flag
#define FLAG_UNUSED_0x4DE                                           0x4DE // Unused Flag
#define FLAG_UNUSED_0x4DF                                           0x4DF // Unused Flag
#define FLAG_UNUSED_0x4E0                                           0x4E0 // Unused Flag
#define FLAG_UNUSED_0x4E1                                           0x4E1 // Unused Flag
#define FLAG_UNUSED_0x4E2                                           0x4E2 // Unused Flag
#define FLAG_UNUSED_0x4E3                                           0x4E3 // Unused Flag
#define FLAG_UNUSED_0x4E4                                           0x4E4 // Unused Flag
#define FLAG_UNUSED_0x4E5                                           0x4E5 // Unused Flag
#define FLAG_UNUSED_0x4E6                                           0x4E6 // Unused Flag
#define FLAG_UNUSED_0x4E7                                           0x4E7 // Unused Flag
#define FLAG_UNUSED_0x4E8                                           0x4E8 // Unused Flag
#define FLAG_UNUSED_0x4E9                                           0x4E9 // Unused Flag
#define FLAG_UNUSED_0x4EA                                           0x4EA // Unused Flag
#define FLAG_UNUSED_0x4EB                                           0x4EB // Unused Flag
#define FLAG_UNUSED_0x4EC                                           0x4EC // Unused Flag
#define FLAG_UNUSED_0x4ED                                           0x4ED // Unused Flag
#define FLAG_UNUSED_0x4EE                                           0x4EE // Unused Flag
#define FLAG_UNUSED_0x4EF                                           0x4EF // Unused Flag

#define FLAG_DEFEATED_RUSTBORO_GYM                                  0x4F0
#define FLAG_DEFEATED_DEWFORD_GYM                                   0x4F1
#define FLAG_ORLEANS_POOL_483                           0x4F2
#define FLAG_DEFEATED_LAVARIDGE_GYM                                 0x4F3
#define FLAG_DEFEATED_PETALBURG_GYM                                 0x4F4
#define FLAG_ORLEANS_POOL_484                           0x4F5
#define FLAG_DEFEATED_MOSSDEEP_GYM                                  0x4F6
#define FLAG_DEFEATED_SOOTOPOLIS_GYM                                0x4F7
#define FLAG_DEFEATED_METEOR_FALLS_STEVEN                           0x4F8

#define FLAG_UNUSED_0x4F9                                           0x4F9 // Unused Flag
#define FLAG_UNUSED_0x4FA                                           0x4FA // Unused Flag

#define FLAG_DEFEATED_ELITE_4_SIDNEY                                0x4FB
#define FLAG_DEFEATED_ELITE_4_PHOEBE                                0x4FC
#define FLAG_DEFEATED_ELITE_4_GLACIA                                0x4FD
#define FLAG_DEFEATED_ELITE_4_DRAKE                                 0x4FE

#define FLAG_UNUSED_0x4FF                                           0x4FF // Unused Flag

// Trainer Flags
// Trainer flags occupy 0x500 - 0x85F, the last 9 of which are unused
// See constants/opponents.h. The values there + FLAG_TRAINER_FLAG_START are the flag IDs

#define TRAINER_FLAGS_START                                         0x500
#define TRAINER_FLAGS_END                                           (TRAINER_FLAGS_START + MAX_TRAINERS_COUNT - 1) // 0x85F

// System Flags

#define SYSTEM_FLAGS                                   (TRAINER_FLAGS_END + 1) // 0x860

#define FLAG_SYS_POKEMON_GET                         (SYSTEM_FLAGS + 0x0) // FLAG_0x860
#define FLAG_SYS_POKEDEX_GET                         (SYSTEM_FLAGS + 0x1)
#define FLAG_SYS_POKENAV_GET                         (SYSTEM_FLAGS + 0x2)
#define FLAG_ORLEANS_POOL_485                           (SYSTEM_FLAGS + 0x3)
#define FLAG_SYS_GAME_CLEAR                          (SYSTEM_FLAGS + 0x4)
#define FLAG_SYS_CHAT_USED                           (SYSTEM_FLAGS + 0x5)
#define FLAG_UNLOCKED_TRENDY_SAYINGS                 (SYSTEM_FLAGS + 0x6)

// Badges
#define FLAG_BADGE01_GET                      (SYSTEM_FLAGS + 0x7)
#define FLAG_BADGE02_GET                      (SYSTEM_FLAGS + 0x8)
#define FLAG_BADGE03_GET                      (SYSTEM_FLAGS + 0x9)
#define FLAG_BADGE04_GET                      (SYSTEM_FLAGS + 0xA)
#define FLAG_BADGE05_GET                      (SYSTEM_FLAGS + 0xB)
#define FLAG_BADGE06_GET                      (SYSTEM_FLAGS + 0xC)
#define FLAG_BADGE07_GET                      (SYSTEM_FLAGS + 0xD)
#define FLAG_BADGE08_GET                      (SYSTEM_FLAGS + 0xE)
#define NUM_BADGES                            (1 + FLAG_BADGE08_GET - FLAG_BADGE01_GET)

// Towns and Cities
#define FLAG_VISITED_LITTLEROOT_TOWN                (SYSTEM_FLAGS + 0xF)
#define FLAG_VISITED_OLDALE_TOWN                    (SYSTEM_FLAGS + 0x10)
#define FLAG_VISITED_DEWFORD_TOWN                   (SYSTEM_FLAGS + 0x11)
#define FLAG_VISITED_LAVARIDGE_TOWN                 (SYSTEM_FLAGS + 0x12)
#define FLAG_VISITED_FALLARBOR_TOWN                 (SYSTEM_FLAGS + 0x13)
#define FLAG_VISITED_VERDANTURF_TOWN                (SYSTEM_FLAGS + 0x14)
#define FLAG_VISITED_PACIFIDLOG_TOWN                (SYSTEM_FLAGS + 0x15)
#define FLAG_VISITED_PETALBURG_CITY                 (SYSTEM_FLAGS + 0x16)
#define FLAG_VISITED_SLATEPORT_CITY                 (SYSTEM_FLAGS + 0x17)
#define FLAG_VISITED_MAUVILLE_CITY                  (SYSTEM_FLAGS + 0x18)
#define FLAG_VISITED_RUSTBORO_CITY                  (SYSTEM_FLAGS + 0x19)
#define FLAG_VISITED_FORTREE_CITY                   (SYSTEM_FLAGS + 0x1A)
#define FLAG_VISITED_LILYCOVE_CITY                  (SYSTEM_FLAGS + 0x1B)
#define FLAG_VISITED_MOSSDEEP_CITY                  (SYSTEM_FLAGS + 0x1C)
#define FLAG_VISITED_SOOTOPOLIS_CITY                (SYSTEM_FLAGS + 0x1D)
#define FLAG_VISITED_EVER_GRANDE_CITY               (SYSTEM_FLAGS + 0x1E)

#define FLAG_IS_CHAMPION                            (SYSTEM_FLAGS + 0x1F) // Seems to be related to linking.
#define FLAG_NURSE_UNION_ROOM_REMINDER              (SYSTEM_FLAGS + 0x20)

#define FLAG_ORLEANS_POOL_486                           (SYSTEM_FLAGS + 0x21)
#define FLAG_ORLEANS_POOL_487                           (SYSTEM_FLAGS + 0x22)
#define FLAG_ORLEANS_POOL_488                           (SYSTEM_FLAGS + 0x23)
#define FLAG_ORLEANS_POOL_489                           (SYSTEM_FLAGS + 0x24)
#define FLAG_ORLEANS_POOL_490                           (SYSTEM_FLAGS + 0x25)
#define FLAG_ORLEANS_POOL_491                           (SYSTEM_FLAGS + 0x26)
#define FLAG_ORLEANS_POOL_492                           (SYSTEM_FLAGS + 0x27)

#define FLAG_SYS_USE_FLASH                          (SYSTEM_FLAGS + 0x28)
#define FLAG_SYS_USE_STRENGTH                       (SYSTEM_FLAGS + 0x29)
// Sets abnormal weather on maps that check for it
#define FLAG_SYS_WEATHER_CTRL                       (SYSTEM_FLAGS + 0x2A)
#define FLAG_SYS_CYCLING_ROAD                       (SYSTEM_FLAGS + 0x2B)
#define FLAG_SYS_SAFARI_MODE                        (SYSTEM_FLAGS + 0x2C)
#define FLAG_SYS_CRUISE_MODE                        (SYSTEM_FLAGS + 0x2D)

#define FLAG_ORLEANS_POOL_493                           (SYSTEM_FLAGS + 0x2E)
#define FLAG_ORLEANS_POOL_494                           (SYSTEM_FLAGS + 0x2F)

#define FLAG_SYS_TV_HOME                            (SYSTEM_FLAGS + 0x30)
#define FLAG_SYS_TV_WATCH                           (SYSTEM_FLAGS + 0x31)
#define FLAG_SYS_TV_START                           (SYSTEM_FLAGS + 0x32)
#define FLAG_SYS_CHANGED_DEWFORD_TREND              (SYSTEM_FLAGS + 0x33)
#define FLAG_SYS_MIX_RECORD                         (SYSTEM_FLAGS + 0x34)
#define FLAG_SYS_CLOCK_SET                          (SYSTEM_FLAGS + 0x35)
#define FLAG_SYS_NATIONAL_DEX                       (SYSTEM_FLAGS + 0x36)
#define FLAG_SYS_CAVE_SHIP                          (SYSTEM_FLAGS + 0x37) // Unused Flag, leftover from R/S debug, presumably used by Emerald's debug too
#define FLAG_SYS_CAVE_WONDER                        (SYSTEM_FLAGS + 0x38) // Unused Flag, same as above
#define FLAG_SYS_CAVE_BATTLE                        (SYSTEM_FLAGS + 0x39) // Unused Flag, same as above
#define FLAG_SYS_SHOAL_TIDE                         (SYSTEM_FLAGS + 0x3A)
#define FLAG_SYS_RIBBON_GET                         (SYSTEM_FLAGS + 0x3B)

#define FLAG_LANDMARK_FLOWER_SHOP                   (SYSTEM_FLAGS + 0x3C)
#define FLAG_LANDMARK_MR_BRINEY_HOUSE               (SYSTEM_FLAGS + 0x3D)
#define FLAG_LANDMARK_ABANDONED_SHIP                (SYSTEM_FLAGS + 0x3E)
#define FLAG_LANDMARK_SEASHORE_HOUSE                (SYSTEM_FLAGS + 0x3F)
#define FLAG_LANDMARK_NEW_MAUVILLE                  (SYSTEM_FLAGS + 0x40)
#define FLAG_LANDMARK_OLD_LADY_REST_SHOP            (SYSTEM_FLAGS + 0x41)
#define FLAG_LANDMARK_TRICK_HOUSE                   (SYSTEM_FLAGS + 0x42)
#define FLAG_LANDMARK_WINSTRATE_FAMILY              (SYSTEM_FLAGS + 0x43)
#define FLAG_LANDMARK_GLASS_WORKSHOP                (SYSTEM_FLAGS + 0x44)
#define FLAG_LANDMARK_LANETTES_HOUSE                (SYSTEM_FLAGS + 0x45)
#define FLAG_LANDMARK_POKEMON_DAYCARE               (SYSTEM_FLAGS + 0x46)
#define FLAG_LANDMARK_SEAFLOOR_CAVERN               (SYSTEM_FLAGS + 0x47)
#define FLAG_LANDMARK_BATTLE_FRONTIER               (SYSTEM_FLAGS + 0x48)
#define FLAG_LANDMARK_SOUTHERN_ISLAND               (SYSTEM_FLAGS + 0x49)
#define FLAG_LANDMARK_FIERY_PATH                    (SYSTEM_FLAGS + 0x4A)

#define FLAG_SYS_PC_LANETTE                         (SYSTEM_FLAGS + 0x4B)
#define FLAG_SYS_MYSTERY_EVENT_ENABLE               (SYSTEM_FLAGS + 0x4C)
#define FLAG_SYS_ENC_UP_ITEM                        (SYSTEM_FLAGS + 0x4D)
#define FLAG_SYS_ENC_DOWN_ITEM                      (SYSTEM_FLAGS + 0x4E)
#define FLAG_SYS_BRAILLE_DIG                        (SYSTEM_FLAGS + 0x4F)
#define FLAG_SYS_REGIROCK_PUZZLE_COMPLETED          (SYSTEM_FLAGS + 0x50)
#define FLAG_SYS_BRAILLE_REGICE_COMPLETED           (SYSTEM_FLAGS + 0x51)
#define FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED         (SYSTEM_FLAGS + 0x52)
#define FLAG_ENABLE_SHIP_SOUTHERN_ISLAND            (SYSTEM_FLAGS + 0x53)

#define FLAG_LANDMARK_POKEMON_LEAGUE                (SYSTEM_FLAGS + 0x54)
#define FLAG_LANDMARK_ISLAND_CAVE                   (SYSTEM_FLAGS + 0x55)
#define FLAG_LANDMARK_DESERT_RUINS                  (SYSTEM_FLAGS + 0x56)
#define FLAG_LANDMARK_FOSSIL_MANIACS_HOUSE          (SYSTEM_FLAGS + 0x57)
#define FLAG_LANDMARK_SCORCHED_SLAB                 (SYSTEM_FLAGS + 0x58)
#define FLAG_LANDMARK_ANCIENT_TOMB                  (SYSTEM_FLAGS + 0x59)
#define FLAG_LANDMARK_TUNNELERS_REST_HOUSE          (SYSTEM_FLAGS + 0x5A)
#define FLAG_LANDMARK_HUNTERS_HOUSE                 (SYSTEM_FLAGS + 0x5B)
#define FLAG_LANDMARK_SEALED_CHAMBER                (SYSTEM_FLAGS + 0x5C)

#define FLAG_SYS_TV_LATIAS_LATIOS                   (SYSTEM_FLAGS + 0x5D)

#define FLAG_LANDMARK_SKY_PILLAR                    (SYSTEM_FLAGS + 0x5E)

#define FLAG_SYS_SHOAL_ITEM                         (SYSTEM_FLAGS + 0x5F)
#define FLAG_SYS_B_DASH                             (SYSTEM_FLAGS + 0x60) // RECEIVED Running Shoes
#define FLAG_SYS_CTRL_OBJ_DELETE                    (SYSTEM_FLAGS + 0x61)
#define FLAG_SYS_RESET_RTC_ENABLE                   (SYSTEM_FLAGS + 0x62)

#define FLAG_LANDMARK_BERRY_MASTERS_HOUSE           (SYSTEM_FLAGS + 0x63)

#define FLAG_SYS_TOWER_SILVER                       (SYSTEM_FLAGS + 0x64)
#define FLAG_SYS_TOWER_GOLD                         (SYSTEM_FLAGS + 0x65)
#define FLAG_SYS_DOME_SILVER                        (SYSTEM_FLAGS + 0x66)
#define FLAG_SYS_DOME_GOLD                          (SYSTEM_FLAGS + 0x67)
#define FLAG_SYS_PALACE_SILVER                      (SYSTEM_FLAGS + 0x68)
#define FLAG_SYS_PALACE_GOLD                        (SYSTEM_FLAGS + 0x69)
#define FLAG_SYS_ARENA_SILVER                       (SYSTEM_FLAGS + 0x6A)
#define FLAG_SYS_ARENA_GOLD                         (SYSTEM_FLAGS + 0x6B)
#define FLAG_SYS_FACTORY_SILVER                     (SYSTEM_FLAGS + 0x6C)
#define FLAG_SYS_FACTORY_GOLD                       (SYSTEM_FLAGS + 0x6D)
#define FLAG_SYS_PIKE_SILVER                        (SYSTEM_FLAGS + 0x6E)
#define FLAG_SYS_PIKE_GOLD                          (SYSTEM_FLAGS + 0x6F)
#define FLAG_SYS_PYRAMID_SILVER                     (SYSTEM_FLAGS + 0x70)
#define FLAG_SYS_PYRAMID_GOLD                       (SYSTEM_FLAGS + 0x71)
#define FLAG_SYS_FRONTIER_PASS                      (SYSTEM_FLAGS + 0x72)

#define FLAG_MAP_SCRIPT_CHECKED_DEOXYS              (SYSTEM_FLAGS + 0x73)
#define FLAG_DEOXYS_ROCK_COMPLETE                   (SYSTEM_FLAGS + 0x74)
#define FLAG_ENABLE_SHIP_BIRTH_ISLAND               (SYSTEM_FLAGS + 0x75)
#define FLAG_ENABLE_SHIP_FARAWAY_ISLAND             (SYSTEM_FLAGS + 0x76)

#define FLAG_SHOWN_BOX_WAS_FULL_MESSAGE             (SYSTEM_FLAGS + 0x77)

#define FLAG_ARRIVED_ON_FARAWAY_ISLAND              (SYSTEM_FLAGS + 0x78)
#define FLAG_ARRIVED_AT_MARINE_CAVE_EMERGE_SPOT     (SYSTEM_FLAGS + 0x79)
#define FLAG_ARRIVED_AT_TERRA_CAVE_ENTRANCE         (SYSTEM_FLAGS + 0x7A)

#define FLAG_SYS_MYSTERY_GIFT_ENABLE                (SYSTEM_FLAGS + 0x7B)

#define FLAG_ENTERED_MIRAGE_TOWER                   (SYSTEM_FLAGS + 0x7C)
#define FLAG_LANDMARK_ALTERING_CAVE                 (SYSTEM_FLAGS + 0x7D)
#define FLAG_LANDMARK_DESERT_UNDERPASS              (SYSTEM_FLAGS + 0x7E)
#define FLAG_LANDMARK_ARTISAN_CAVE                  (SYSTEM_FLAGS + 0x7F)
#define FLAG_ENABLE_SHIP_NAVEL_ROCK                 (SYSTEM_FLAGS + 0x80)
#define FLAG_ARRIVED_AT_NAVEL_ROCK                  (SYSTEM_FLAGS + 0x81)
#define FLAG_LANDMARK_TRAINER_HILL                  (SYSTEM_FLAGS + 0x82)

#define FLAG_ORLEANS_POOL_495                           (SYSTEM_FLAGS + 0x83)

#define FLAG_RECEIVED_POKEDEX_FROM_BIRCH            (SYSTEM_FLAGS + 0x84)

#define FLAG_ORLEANS_POOL_496                           (SYSTEM_FLAGS + 0x85)
#define FLAG_ORLEANS_POOL_497                           (SYSTEM_FLAGS + 0x86)
#define FLAG_ORLEANS_POOL_498                           (SYSTEM_FLAGS + 0x87)
#define FLAG_ORLEANS_POOL_499                           (SYSTEM_FLAGS + 0x88)
#define FLAG_ORLEANS_POOL_500                           (SYSTEM_FLAGS + 0x89)
#define FLAG_ORLEANS_POOL_501                           (SYSTEM_FLAGS + 0x8A)
#define FLAG_ORLEANS_POOL_502                           (SYSTEM_FLAGS + 0x8B)
#define FLAG_ORLEANS_POOL_503                           (SYSTEM_FLAGS + 0x8C)
#define FLAG_ORLEANS_POOL_504                           (SYSTEM_FLAGS + 0x8D)
#define FLAG_ORLEANS_POOL_505                           (SYSTEM_FLAGS + 0x8E)
#define FLAG_ORLEANS_POOL_506                           (SYSTEM_FLAGS + 0x8F)
#define FLAG_ORLEANS_POOL_507                           (SYSTEM_FLAGS + 0x90)
#define FLAG_ORLEANS_POOL_508                           (SYSTEM_FLAGS + 0x91)
#define FLAG_ORLEANS_POOL_509                           (SYSTEM_FLAGS + 0x92)
#define FLAG_ORLEANS_POOL_510                           (SYSTEM_FLAGS + 0x93)
#define FLAG_ORLEANS_POOL_511                           (SYSTEM_FLAGS + 0x94)
#define FLAG_ORLEANS_POOL_512                           (SYSTEM_FLAGS + 0x95)
#define FLAG_ORLEANS_POOL_513                           (SYSTEM_FLAGS + 0x96)
#define FLAG_ORLEANS_POOL_514                           (SYSTEM_FLAGS + 0x97)
#define FLAG_ORLEANS_POOL_515                           (SYSTEM_FLAGS + 0x98)
#define FLAG_ORLEANS_POOL_516                           (SYSTEM_FLAGS + 0x99)
#define FLAG_ORLEANS_POOL_517                           (SYSTEM_FLAGS + 0x9A)
#define FLAG_ORLEANS_POOL_518                           (SYSTEM_FLAGS + 0x9B)
#define FLAG_ORLEANS_POOL_519                           (SYSTEM_FLAGS + 0x9C)
#define FLAG_ORLEANS_POOL_520                           (SYSTEM_FLAGS + 0x9D)
#define FLAG_ORLEANS_POOL_521                           (SYSTEM_FLAGS + 0x9E)
#define FLAG_ORLEANS_POOL_522                           (SYSTEM_FLAGS + 0x9F)
#define FLAG_ORLEANS_POOL_523                           (SYSTEM_FLAGS + 0xA0)
#define FLAG_ORLEANS_POOL_524                           (SYSTEM_FLAGS + 0xA1)
#define FLAG_ORLEANS_POOL_525                           (SYSTEM_FLAGS + 0xA2)
#define FLAG_ORLEANS_POOL_526                           (SYSTEM_FLAGS + 0xA3)
#define FLAG_ORLEANS_POOL_527                           (SYSTEM_FLAGS + 0xA4)
#define FLAG_ORLEANS_POOL_528                           (SYSTEM_FLAGS + 0xA5)
#define FLAG_ORLEANS_POOL_529                           (SYSTEM_FLAGS + 0xA6)
#define FLAG_ORLEANS_POOL_530                           (SYSTEM_FLAGS + 0xA7)
#define FLAG_ORLEANS_POOL_531                           (SYSTEM_FLAGS + 0xA8)
#define FLAG_ORLEANS_POOL_532                           (SYSTEM_FLAGS + 0xA9)
#define FLAG_ORLEANS_POOL_533                           (SYSTEM_FLAGS + 0xAA)
#define FLAG_ORLEANS_POOL_534                           (SYSTEM_FLAGS + 0xAB)
#define FLAG_ORLEANS_POOL_535                           (SYSTEM_FLAGS + 0xAC)
#define FLAG_ORLEANS_POOL_536                           (SYSTEM_FLAGS + 0xAD)
#define FLAG_ORLEANS_POOL_537                           (SYSTEM_FLAGS + 0xAE)
#define FLAG_ORLEANS_POOL_538                           (SYSTEM_FLAGS + 0xAF)
#define FLAG_ORLEANS_POOL_539                           (SYSTEM_FLAGS + 0xB0)
#define FLAG_ORLEANS_POOL_540                           (SYSTEM_FLAGS + 0xB1)
#define FLAG_ORLEANS_POOL_541                           (SYSTEM_FLAGS + 0xB2)
#define FLAG_ORLEANS_POOL_542                           (SYSTEM_FLAGS + 0xB3)
#define FLAG_ORLEANS_POOL_543                           (SYSTEM_FLAGS + 0xB4)
#define FLAG_ORLEANS_POOL_544                           (SYSTEM_FLAGS + 0xB5)
#define FLAG_ORLEANS_POOL_545                           (SYSTEM_FLAGS + 0xB6)
#define FLAG_ORLEANS_POOL_546                           (SYSTEM_FLAGS + 0xB7)
#define FLAG_ORLEANS_POOL_547                           (SYSTEM_FLAGS + 0xB8)
#define FLAG_ORLEANS_POOL_548                           (SYSTEM_FLAGS + 0xB9)
#define FLAG_ORLEANS_POOL_549                           (SYSTEM_FLAGS + 0xBA)
#define FLAG_ORLEANS_POOL_550                           (SYSTEM_FLAGS + 0xBB)
#define FLAG_ORLEANS_POOL_551                           (SYSTEM_FLAGS + 0xBC)
#define FLAG_ORLEANS_POOL_552                           (SYSTEM_FLAGS + 0xBD)
#define FLAG_ORLEANS_POOL_553                           (SYSTEM_FLAGS + 0xBE)
#define FLAG_UNUSED_0x91F                           (SYSTEM_FLAGS + 0xBF) // Unused Flag

// Daily Flags
// These flags are cleared once per day
// The start and end are byte-aligned because the flags are cleared in byte increments
#define DAILY_FLAGS_START                           (FLAG_UNUSED_0x91F + (8 - FLAG_UNUSED_0x91F % 8))
#define FLAG_UNUSED_0x920                           (DAILY_FLAGS_START + 0x0)  // Unused Flag
#define FLAG_DAILY_CONTEST_LOBBY_RECEIVED_BERRY     (DAILY_FLAGS_START + 0x1)
#define FLAG_DAILY_SECRET_BASE                      (DAILY_FLAGS_START + 0x2)
#define FLAG_UNUSED_0x923                           (DAILY_FLAGS_START + 0x3)  // Unused Flag
#define FLAG_UNUSED_0x924                           (DAILY_FLAGS_START + 0x4)  // Unused Flag
#define FLAG_UNUSED_0x925                           (DAILY_FLAGS_START + 0x5)  // Unused Flag
#define FLAG_UNUSED_0x926                           (DAILY_FLAGS_START + 0x6)  // Unused Flag
#define FLAG_UNUSED_0x927                           (DAILY_FLAGS_START + 0x7)  // Unused Flag
#define FLAG_UNUSED_0x928                           (DAILY_FLAGS_START + 0x8)  // Unused Flag
#define FLAG_UNUSED_0x929                           (DAILY_FLAGS_START + 0x9)  // Unused Flag
#define FLAG_DAILY_PICKED_LOTO_TICKET               (DAILY_FLAGS_START + 0xA)
#define FLAG_DAILY_ROUTE_114_RECEIVED_BERRY         (DAILY_FLAGS_START + 0xB)
#define FLAG_DAILY_ROUTE_111_RECEIVED_BERRY         (DAILY_FLAGS_START + 0xC)
#define FLAG_DAILY_BERRY_MASTER_RECEIVED_BERRY      (DAILY_FLAGS_START + 0xD)
#define FLAG_DAILY_ROUTE_120_RECEIVED_BERRY         (DAILY_FLAGS_START + 0xE)
#define FLAG_DAILY_LILYCOVE_RECEIVED_BERRY          (DAILY_FLAGS_START + 0xF)
#define FLAG_DAILY_FLOWER_SHOP_RECEIVED_BERRY       (DAILY_FLAGS_START + 0x10)
#define FLAG_DAILY_BERRY_MASTERS_WIFE               (DAILY_FLAGS_START + 0x11)
#define FLAG_DAILY_SOOTOPOLIS_RECEIVED_BERRY        (DAILY_FLAGS_START + 0x12)
#define FLAG_UNUSED_0x933                           (DAILY_FLAGS_START + 0x13) // Unused Flag
#define FLAG_DAILY_APPRENTICE_LEAVES                (DAILY_FLAGS_START + 0x14)

#define FLAG_UNUSED_0x935                           (DAILY_FLAGS_START + 0x15) // Unused Flag
#define FLAG_UNUSED_0x936                           (DAILY_FLAGS_START + 0x16) // Unused Flag
#define FLAG_UNUSED_0x937                           (DAILY_FLAGS_START + 0x17) // Unused Flag
#define FLAG_UNUSED_0x938                           (DAILY_FLAGS_START + 0x18) // Unused Flag
#define FLAG_UNUSED_0x939                           (DAILY_FLAGS_START + 0x19) // Unused Flag
#define FLAG_UNUSED_0x93A                           (DAILY_FLAGS_START + 0x1A) // Unused Flag
#define FLAG_UNUSED_0x93B                           (DAILY_FLAGS_START + 0x1B) // Unused Flag
#define FLAG_UNUSED_0x93C                           (DAILY_FLAGS_START + 0x1C) // Unused Flag
#define FLAG_UNUSED_0x93D                           (DAILY_FLAGS_START + 0x1D) // Unused Flag
#define FLAG_UNUSED_0x93E                           (DAILY_FLAGS_START + 0x1E) // Unused Flag
#define FLAG_UNUSED_0x93F                           (DAILY_FLAGS_START + 0x1F) // Unused Flag
#define FLAG_UNUSED_0x940                           (DAILY_FLAGS_START + 0x20) // Unused Flag
#define FLAG_UNUSED_0x941                           (DAILY_FLAGS_START + 0x21) // Unused Flag
#define FLAG_UNUSED_0x942                           (DAILY_FLAGS_START + 0x22) // Unused Flag
#define FLAG_UNUSED_0x943                           (DAILY_FLAGS_START + 0x23) // Unused Flag
#define FLAG_UNUSED_0x944                           (DAILY_FLAGS_START + 0x24) // Unused Flag
#define FLAG_UNUSED_0x945                           (DAILY_FLAGS_START + 0x25) // Unused Flag
#define FLAG_UNUSED_0x946                           (DAILY_FLAGS_START + 0x26) // Unused Flag
#define FLAG_UNUSED_0x947                           (DAILY_FLAGS_START + 0x27) // Unused Flag
#define FLAG_UNUSED_0x948                           (DAILY_FLAGS_START + 0x28) // Unused Flag
#define FLAG_UNUSED_0x949                           (DAILY_FLAGS_START + 0x29) // Unused Flag
#define FLAG_UNUSED_0x94A                           (DAILY_FLAGS_START + 0x2A) // Unused Flag
#define FLAG_UNUSED_0x94B                           (DAILY_FLAGS_START + 0x2B) // Unused Flag
#define FLAG_UNUSED_0x94C                           (DAILY_FLAGS_START + 0x2C) // Unused Flag
#define FLAG_UNUSED_0x94D                           (DAILY_FLAGS_START + 0x2D) // Unused Flag
#define FLAG_UNUSED_0x94E                           (DAILY_FLAGS_START + 0x2E) // Unused Flag
#define FLAG_UNUSED_0x94F                           (DAILY_FLAGS_START + 0x2F) // Unused Flag
#define FLAG_UNUSED_0x950                           (DAILY_FLAGS_START + 0x30) // Unused Flag
#define FLAG_UNUSED_0x951                           (DAILY_FLAGS_START + 0x31) // Unused Flag
#define FLAG_UNUSED_0x952                           (DAILY_FLAGS_START + 0x32) // Unused Flag
#define FLAG_UNUSED_0x953                           (DAILY_FLAGS_START + 0x33) // Unused Flag
#define FLAG_UNUSED_0x954                           (DAILY_FLAGS_START + 0x34) // Unused Flag
#define FLAG_UNUSED_0x955                           (DAILY_FLAGS_START + 0x35) // Unused Flag
#define FLAG_UNUSED_0x956                           (DAILY_FLAGS_START + 0x36) // Unused Flag
#define FLAG_UNUSED_0x957                           (DAILY_FLAGS_START + 0x37) // Unused Flag
#define FLAG_UNUSED_0x958                           (DAILY_FLAGS_START + 0x38) // Unused Flag
#define FLAG_UNUSED_0x959                           (DAILY_FLAGS_START + 0x39) // Unused Flag
#define FLAG_UNUSED_0x95A                           (DAILY_FLAGS_START + 0x3A) // Unused Flag
#define FLAG_UNUSED_0x95B                           (DAILY_FLAGS_START + 0x3B) // Unused Flag
#define FLAG_UNUSED_0x95C                           (DAILY_FLAGS_START + 0x3C) // Unused Flag
#define FLAG_UNUSED_0x95D                           (DAILY_FLAGS_START + 0x3D) // Unused Flag
#define FLAG_UNUSED_0x95E                           (DAILY_FLAGS_START + 0x3E) // Unused Flag
#define FLAG_UNUSED_0x95F                           (DAILY_FLAGS_START + 0x3F) // Unused Flag
#define DAILY_FLAGS_END                             (FLAG_UNUSED_0x95F + (7 - FLAG_UNUSED_0x95F % 8))
#define NUM_DAILY_FLAGS                             (DAILY_FLAGS_END - DAILY_FLAGS_START + 1)

#define FLAGS_COUNT (DAILY_FLAGS_END + 1)

// Special Flags (Stored in EWRAM (sSpecialFlags), not in the SaveBlock)
#define SPECIAL_FLAGS_START                     0x4000
#define FLAG_HIDE_MAP_NAME_POPUP                (SPECIAL_FLAGS_START + 0x0)
#define FLAG_DONT_TRANSITION_MUSIC              (SPECIAL_FLAGS_START + 0x1)
#define FLAG_ENABLE_MULTI_CORRIDOR_DOOR         (SPECIAL_FLAGS_START + 0x2)
#define FLAG_SPECIAL_FLAG_UNUSED_0x4003         (SPECIAL_FLAGS_START + 0x3) // Unused Flag
#define FLAG_STORING_ITEMS_IN_PYRAMID_BAG       (SPECIAL_FLAGS_START + 0x4)
#define FLAG_SAFE_FOLLOWER_MOVEMENT             (SPECIAL_FLAGS_START + 0x5) // When set, applymovement does not put the follower inside a pokeball
                                                                            // Also, scripted movements on the player will move follower(s), too
// FLAG_SPECIAL_FLAG_0x4005 - 0x407F also exist and are unused
#define SPECIAL_FLAGS_END                       (SPECIAL_FLAGS_START + 0x7F)
#define NUM_SPECIAL_FLAGS                       (SPECIAL_FLAGS_END - SPECIAL_FLAGS_START + 1)

// Temp flag aliases
#define FLAG_TEMP_SKIP_GABBY_INTERVIEW          FLAG_TEMP_1
#define FLAG_TEMP_REGICE_PUZZLE_STARTED         FLAG_TEMP_2
#define FLAG_TEMP_REGICE_PUZZLE_FAILED          FLAG_TEMP_3
#define FLAG_TEMP_HIDE_FOLLOWER                 FLAG_TEMP_E
#define FLAG_TEMP_HIDE_MIRAGE_ISLAND_BERRY_TREE FLAG_TEMP_11

// FRLG flags

#define FLAG_HIDE_BULBASAUR_BALL                           0
#define FLAG_HIDE_SQUIRTLE_BALL                            0
#define FLAG_HIDE_CHARMANDER_BALL                          0
#define FLAG_HIDE_OAK_IN_HIS_LAB                           0
#define FLAG_HIDE_OAK_IN_PALLET_TOWN                       0
#define FLAG_HIDE_RIVAL_IN_LAB                             0
#define FLAG_HIDE_PEWTER_CITY_GYM_GUIDE                    0
#define FLAG_HIDE_DOME_FOSSIL                              0
#define FLAG_HIDE_HELIX_FOSSIL                             0
#define FLAG_HIDE_NUGGET_BRIDGE_ROCKET                     0
#define FLAG_HIDE_BILL_CLEFAIRY                            0
#define FLAG_HIDE_BILL_HUMAN_SEA_COTTAGE                   0
#define FLAG_HIDE_TOWER_FUJI                               0
#define FLAG_HIDE_POKEHOUSE_FUJI                           0
#define FLAG_HIDE_LIFT_KEY                                 0
#define FLAG_HIDE_SILPH_SCOPE                              0
#define FLAG_HIDE_HIDEOUT_GIOVANNI                         0
#define FLAG_HIDE_TOWN_MAP                                 0
#define FLAG_HIDE_POKEDEX                                  0
#define FLAG_HIDE_CERULEAN_ROCKET                          0
#define FLAG_HIDE_CERULEAN_RIVAL                           0
#define FLAG_HIDE_SS_ANNE_RIVAL                            0
#define FLAG_HIDE_SAFFRON_ROCKETS                          0
#define FLAG_HIDE_SAFFRON_CIVILIANS                        0
#define FLAG_HIDE_SEAFOAM_1F_BOULDER_1                     0
#define FLAG_HIDE_SEAFOAM_1F_BOULDER_2                     0
#define FLAG_HIDE_SEAFOAM_B1F_BOULDER_1                    0
#define FLAG_HIDE_SEAFOAM_B1F_BOULDER_2                    0
#define FLAG_HIDE_SEAFOAM_B2F_BOULDER_1                    0
#define FLAG_HIDE_SEAFOAM_B2F_BOULDER_2                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_1                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_2                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_3                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_4                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_5                    0
#define FLAG_HIDE_SEAFOAM_B3F_BOULDER_6                    0
#define FLAG_HIDE_SEAFOAM_B4F_BOULDER_1                    0
#define FLAG_HIDE_SEAFOAM_B4F_BOULDER_2                    0
#define FLAG_HIDE_SILPH_RIVAL                              0
#define FLAG_HIDE_ROUTE_22_RIVAL                           0
#define FLAG_HIDE_PEWTER_MUSEUM_GUIDE                      0
#define FLAG_HIDE_TOWER_RIVAL                              0
#define FLAG_HIDE_MOLTRES                                  0
#define FLAG_HIDE_SILPH_ROCKETS                            0
#define FLAG_HIDE_ROUTE_12_SNORLAX                         0
#define FLAG_HIDE_VIRIDIAN_GIOVANNI                        0
#define FLAG_HIDE_OLD_AMBER                                0
#define FLAG_HIDE_EEVEE_BALL                               0
#define FLAG_HIDE_VICTORY_ROAD_2F_BOULDER                  0
#define FLAG_HIDE_VICTORY_ROAD_3F_BOULDER                  0
#define FLAG_HIDE_OAK_IN_CHAMP_ROOM                        0
#define FLAG_HIDE_GAME_CORNER_ROCKET                       0
#define FLAG_HIDE_CERULEAN_CAVE_GUARD                      0
#define FLAG_HIDE_ZAPDOS                                   0
#define FLAG_HIDE_TOWER_ROCKET_1                           0
#define FLAG_HIDE_CELADON_ROCKETS                          0
#define FLAG_HIDE_DOJO_HITMONLEE_BALL                      0
#define FLAG_HIDE_DOJO_HITMONCHAN_BALL                     0
#define FLAG_HIDE_CINNABAR_BILL                            0
#define FLAG_HIDE_UNION_ROOM_PLAYER_1                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_2                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_3                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_4                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_5                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_6                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_7                      0
#define FLAG_HIDE_UNION_ROOM_PLAYER_8                      0
#define FLAG_HIDE_CINNABAR_SEAGALLOP                       0
#define FLAG_HIDE_SAFFRON_FAN_CLUB_BLACKBELT               0
#define FLAG_HIDE_SAFFRON_FAN_CLUB_ROCKER                  0
#define FLAG_HIDE_SAFFRON_FAN_CLUB_WOMAN                   0
#define FLAG_HIDE_SAFFRON_FAN_CLUB_BEAUTY                  0
#define FLAG_HIDE_MG_DELIVERYMEN                           0
#define FLAG_HIDE_ONE_ISLAND_BILL                          0
#define FLAG_HIDE_ONE_ISLAND_POKECENTER_BILL               0
#define FLAG_HIDE_ONE_ISLAND_POKECENTER_CELIO              0
#define FLAG_HIDE_TWO_ISLAND_GAME_CORNER_BIKER             0
#define FLAG_HIDE_TWO_ISLAND_GAME_CORNER_LOSTELLE          0
#define FLAG_HIDE_LOSTELLE_IN_HER_HOME                     0
#define FLAG_0x077                                         0
#define FLAG_0x078                                         0
#define FLAG_HIDE_THREE_ISLAND_BIKERS                      0
#define FLAG_HIDE_LOSTELLE_IN_BERRY_FOREST                 0
#define FLAG_HIDE_TWO_ISLAND_WOMAN                         0
#define FLAG_HIDE_TWO_ISLAND_BEAUTY                        0
#define FLAG_HIDE_TWO_ISLAND_SUPER_NERD                    0
#define FLAG_HIDE_THREE_ISLAND_ANTIBIKERS                  0
#define FLAG_0x07F                                         0
#define FLAG_HIDE_ROUTE_16_SNORLAX                         0
#define FLAG_HIDE_MEWTWO                                   0
#define FLAG_HIDE_ARTICUNO                                 0
#define FLAG_HIDE_TOWER_ROCKET_2                           0
#define FLAG_HIDE_TOWER_ROCKET_3                           0
#define FLAG_HIDE_POWER_PLANT_ELECTRODE_1                  0
#define FLAG_HIDE_POWER_PLANT_ELECTRODE_2                  0
#define FLAG_HIDE_SS_ANNE                                  0
#define FLAG_HIDE_FIVE_ISLAND_ROCKETS                      0
#define FLAG_HIDE_MT_EMBER_EXTERIOR_ROCKETS                0
#define FLAG_HIDE_RUBY                                     0
#define FLAG_HIDE_ICEFALL_CAVE_LORELEI                     0
#define FLAG_HIDE_LORELEI_IN_HER_HOUSE                     0
#define FLAG_HIDE_ICEFALL_CAVE_ROCKETS                     0
#define FLAG_HIDE_RUIN_VALLEY_SCIENTIST                    0
#define FLAG_HIDE_SAPPHIRE                                 0
#define FLAG_HIDE_DOTTED_HOLE_SCIENTIST                    0
#define FLAG_HIDE_THREE_ISLAND_LONE_BIKER                  0
#define FLAG_HIDE_PEWTER_CITY_RUNNING_SHOES_GUY            0
#define FLAG_HIDE_LOST_CAVE_SELPHY                         0
#define FLAG_HIDE_RESORT_GORGEOUS_SELPHY                   0
#define FLAG_HIDE_RESORT_GORGEOUS_INSIDE_SELPHY            0
#define FLAG_HIDE_SELPHYS_BUTLER                           0
#define FLAG_HIDE_FOUR_ISLAND_RIVAL                        0
#define FLAG_HIDE_SIX_ISLAND_POKECENTER_RIVAL              0
#define FLAG_HIDE_BIRTH_ISLAND_METEORITE                   0
#define FLAG_HIDE_POSTGAME_GOSSIPERS                       0
#define FLAG_HIDE_FAME_CHECKER_ERIKA_JOURNALS              0
#define FLAG_HIDE_FAME_CHECKER_KOGA_JOURNAL                0
#define FLAG_HIDE_FAME_CHECKER_LT_SURGE_JOURNAL            0
#define FLAG_HIDE_VERMILION_CITY_OAKS_AIDE                 0
#define FLAG_HIDE_CINNABAR_POKECENTER_BILL                 0
#define FLAG_HIDE_CREDITS_RIVAL                            0
#define FLAG_HIDE_CREDITS_OAK                              0
#define FLAG_HIDE_LORELEI_HOUSE_MEOWTH_DOLL                0
#define FLAG_HIDE_LORELEI_HOUSE_CHANSEY_DOLL               0
#define FLAG_HIDE_LORELEIS_HOUSE_NIDORAN_F_DOLL            0
#define FLAG_HIDE_LORELEI_HOUSE_JIGGLYPUFF_DOLL            0
#define FLAG_HIDE_LORELEIS_HOUSE_NIDORAN_M_DOLL            0
#define FLAG_HIDE_LORELEIS_HOUSE_FEAROW_DOLL               0
#define FLAG_HIDE_LORELEIS_HOUSE_PIDGEOT_DOLL              0
#define FLAG_HIDE_LORELEIS_HOUSE_LAPRAS_DOLL               0
#define FLAG_HIDE_MISC_KANTO_ROCKETS                       0
#define FLAG_HIDE_SAFFRON_CITY_POKECENTER_SABRINA_JOURNALS 0

#define FLAG_HIDE_ROUTE2_ETHER                                  0
#define FLAG_HIDE_ROUTE2_PARALYZE_HEAL                          0
#define FLAG_HIDE_VIRIDIAN_FOREST_POKE_BALL                     0
#define FLAG_HIDE_VIRIDIAN_FOREST_ANTIDOTE                      0
#define FLAG_HIDE_VIRIDIAN_FOREST_POTION                        0
#define FLAG_HIDE_MT_MOON_1F_PARALYZE_HEAL                      0
#define FLAG_HIDE_MT_MOON_1F_TM09                               0
#define FLAG_HIDE_MT_MOON_1F_POTION                             0
#define FLAG_HIDE_MT_MOON_1F_RARE_CANDY                         0
#define FLAG_HIDE_MT_MOON_1F_ESCAPE_ROPE                        0
#define FLAG_HIDE_MT_MOON_1F_MOON_STONE                         0
#define FLAG_HIDE_MT_MOON_B2F_STAR_PIECE                        0
#define FLAG_HIDE_MT_MOON_B2F_TM46                              0
#define FLAG_HIDE_ROUTE4_TM05                                   0
#define FLAG_HIDE_ROUTE24_TM45                                  0
#define FLAG_HIDE_ROUTE25_TM43                                  0
#define FLAG_HIDE_SSANNE_1F_ROOM2_TM31                          0
#define FLAG_HIDE_SSANNE_2F_ROOM2_STARDUST                      0
#define FLAG_HIDE_SSANNE_2F_ROOM4_X_ATTACK                      0
#define FLAG_HIDE_SSANNE_B1F_ROOM2_TM44                         0
#define FLAG_HIDE_SSANNE_B1F_ROOM3_ETHER                        0
#define FLAG_HIDE_SSANNE_B1F_ROOM5_SUPER_POTION                 0
#define FLAG_HIDE_SSANNE_KITCHEN_GREAT_BALL                     0
#define FLAG_HIDE_ROUTE9_TM40                                   0
#define FLAG_HIDE_ROCKET_HIDEOUT_B1F_ESCAPE_ROPE                0
#define FLAG_HIDE_ROCKET_HIDEOUT_B1F_HYPER_POTION               0
#define FLAG_HIDE_ROCKET_HIDEOUT_B2F_X_SPEED                    0
#define FLAG_HIDE_ROCKET_HIDEOUT_B2F_MOON_STONE                 0
#define FLAG_HIDE_ROCKET_HIDEOUT_B2F_TM12                       0
#define FLAG_HIDE_ROCKET_HIDEOUT_B2F_SUPER_POTION               0
#define FLAG_HIDE_ROCKET_HIDEOUT_B3F_RARE_CANDY                 0
#define FLAG_HIDE_ROCKET_HIDEOUT_B3F_TM21                       0
#define FLAG_HIDE_ROCKET_HIDEOUT_B4F_TM49                       0
#define FLAG_HIDE_ROCKET_HIDEOUT_B4F_MAX_ETHER                  0
#define FLAG_HIDE_ROCKET_HIDEOUT_B4F_CALCIUM                    0
#define FLAG_HIDE_POKEMON_TOWER_3F_ESCAPE_ROPE                  0
#define FLAG_HIDE_POKEMON_TOWER_4F_ELIXIR                       0
#define FLAG_HIDE_POKEMON_TOWER_4F_AWAKENING                    0
#define FLAG_HIDE_POKEMON_TOWER_4F_GREAT_BALL                   0
#define FLAG_HIDE_POKEMON_TOWER_5F_NUGGET                       0
#define FLAG_HIDE_POKEMON_TOWER_6F_RARE_CANDY                   0
#define FLAG_HIDE_POKEMON_TOWER_6F_X_ACCURACY                   0
#define FLAG_HIDE_ROUTE12_TM48                                  0
#define FLAG_HIDE_ROUTE12_IRON                                  0
#define FLAG_HIDE_ROUTE15_TM18                                  0
#define FLAG_HIDE_SAFARI_ZONE_CENTER_NUGGET                     0
#define FLAG_HIDE_SAFARI_ZONE_EAST_MAX_POTION                   0
#define FLAG_HIDE_SAFARI_ZONE_EAST_FULL_RESTORE                 0
#define FLAG_HIDE_SAFARI_ZONE_EAST_TM11                         0
#define FLAG_HIDE_SAFARI_ZONE_EAST_LEAF_STONE                   0
#define FLAG_HIDE_SAFARI_ZONE_NORTH_PROTEIN                     0
#define FLAG_HIDE_SAFARI_ZONE_NORTH_TM47                        0
#define FLAG_HIDE_SAFARI_ZONE_WEST_TM32                         0
#define FLAG_HIDE_SAFARI_ZONE_WEST_GOLD_TEETH                   0
#define FLAG_HIDE_SAFARI_ZONE_WEST_MAX_POTION                   0
#define FLAG_HIDE_SAFARI_ZONE_WEST_MAX_REVIVE                   0
#define FLAG_HIDE_SILPH_CO_3F_HYPER_POTION                      0
#define FLAG_HIDE_SILPH_CO_4F_MAX_REVIVE                        0
#define FLAG_HIDE_SILPH_CO_4F_ESCAPE_ROPE                       0
#define FLAG_HIDE_SILPH_CO_4F_FULL_HEAL                         0
#define FLAG_HIDE_SILPH_CO_5F_PROTEIN                           0
#define FLAG_HIDE_SILPH_CO_5F_TM01                              0
#define FLAG_HIDE_SILPH_CO_5F_CARD_KEY                          0
#define FLAG_HIDE_SILPH_CO_6F_HP_UP                             0
#define FLAG_HIDE_SILPH_CO_6F_X_SPECIAL                         0
#define FLAG_HIDE_SILPH_CO_7F_CALCIUM                           0
#define FLAG_HIDE_SILPH_CO_7F_TM08                              0
#define FLAG_HIDE_SILPH_CO_10F_CARBOS                           0
#define FLAG_HIDE_SILPH_CO_10F_ULTRA_BALL                       0
#define FLAG_HIDE_SILPH_CO_10F_RARE_CANDY                       0
#define FLAG_HIDE_POWER_PLANT_MAX_POTION                        0
#define FLAG_HIDE_POWER_PLANT_TM17                              0
#define FLAG_HIDE_POWER_PLANT_TM25                              0
#define FLAG_HIDE_POWER_PLANT_THUNDER_STONE                     0
#define FLAG_HIDE_POWER_PLANT_ELIXIR                            0
#define FLAG_HIDE_POKEMON_MANSION_1F_CARBOS                     0
#define FLAG_HIDE_POKEMON_MANSION_1F_ESCAPE_ROPE                0
#define FLAG_HIDE_POKEMON_MANSION_2F_CALCIUM                    0
#define FLAG_HIDE_POKEMON_MANSION_3F_MAX_POTION                 0
#define FLAG_HIDE_POKEMON_MANSION_3F_IRON                       0
#define FLAG_HIDE_POKEMON_MANSION_B1F_TM14                      0
#define FLAG_HIDE_POKEMON_MANSION_B1F_FULL_RESTORE              0
#define FLAG_0x1A6                                              0
#define FLAG_HIDE_POKEMON_MANSION_B1F_TM22                      0
#define FLAG_HIDE_POKEMON_MANSION_B1F_SECRET_KEY                0
#define FLAG_HIDE_VICTORY_ROAD_1F_RARE_CANDY                    0
#define FLAG_HIDE_VICTORY_ROAD_1F_TM02                          0
#define FLAG_HIDE_VICTORY_ROAD_2F_GUARD_SPEC                    0
#define FLAG_HIDE_VICTORY_ROAD_2F_TM07                          0
#define FLAG_HIDE_VICTORY_ROAD_2F_FULL_HEAL                     0
#define FLAG_HIDE_VICTORY_ROAD_2F_TM37                          0
#define FLAG_HIDE_VICTORY_ROAD_3F_MAX_REVIVE                    0
#define FLAG_HIDE_VICTORY_ROAD_3F_TM50                          0
#define FLAG_HIDE_CERULEAN_CAVE_1F_MAX_ELIXIR                   0
#define FLAG_HIDE_CERULEAN_CAVE_1F_NUGGET                       0
#define FLAG_HIDE_CERULEAN_CAVE_1F_FULL_RESTORE                 0
#define FLAG_HIDE_CERULEAN_CAVE_2F_FULL_RESTORE                 0
#define FLAG_HIDE_CERULEAN_CAVE_2F_PP_UP                        0
#define FLAG_HIDE_CERULEAN_CAVE_2F_ULTRA_BALL                   0
#define FLAG_HIDE_CERULEAN_CAVE_B1F_MAX_REVIVE                  0
#define FLAG_HIDE_CERULEAN_CAVE_B1F_ULTRA_BALL                  0
#define FLAG_HIDE_FUCHSIA_CITY_WARDENS_HOUSE_RARE_CANDY         0
#define FLAG_HIDE_TWO_ISLAND_REVIVE                             0
#define FLAG_HIDE_THREE_ISLAND_ZINC                             0
#define FLAG_0x1BC                                              0
#define FLAG_0x1BD                                              0
#define FLAG_HIDE_VIRIDIAN_FOREST_POTION_2                      0
#define FLAG_HIDE_MT_MOON_B2F_REVIVE                            0
#define FLAG_HIDE_MT_MOON_B2F_ANTIDOTE                          0
#define FLAG_HIDE_ROUTE11_X_DEFEND                              0
#define FLAG_HIDE_ROUTE9_BURN_HEAL                              0
#define FLAG_HIDE_ROCK_TUNNEL_1F_REPEL                          0
#define FLAG_HIDE_ROCK_TUNNEL_1F_PEARL                          0
#define FLAG_HIDE_ROCK_TUNNEL_1F_ESCAPE_ROPE                    0
#define FLAG_HIDE_ROCK_TUNNEL_B1F_REVIVE                        0
#define FLAG_HIDE_ROCK_TUNNEL_B1F_MAX_ETHER                     0
#define FLAG_HIDE_SILPH_CO_8F_IRON                              0
#define FLAG_HIDE_SILPH_CO_11F_ZINC                             0
#define FLAG_HIDE_POKEMON_MANSION_1F_PROTEIN                    0
#define FLAG_HIDE_POKEMON_MANSION_2F_ZINC                       0
#define FLAG_HIDE_POKEMON_MANSION_2F_HP_UP                      0
#define FLAG_HIDE_VIRIDIAN_CITY_POTION                          0
#define FLAG_HIDE_ROUTE11_GREAT_BALL                            0
#define FLAG_HIDE_ROUTE11_AWAKENING                             0
#define FLAG_HIDE_POKEMON_TOWER_5F_CLEANSE_TAG                  0
#define FLAG_HIDE_CELADON_CITY_ETHER                            0
#define FLAG_HIDE_ROCKET_HIDEOUT_B3F_BLACK_GLASSES              0
#define FLAG_HIDE_SAFARI_ZONE_NORTH_QUICK_CLAW                  0
#define FLAG_HIDE_SEAFOAM_ISLANDS_1F_ICE_HEAL                   0
#define FLAG_HIDE_SEAFOAM_ISLANDS_B1F_WATER_STONE               0
#define FLAG_HIDE_SEAFOAM_ISLANDS_B1F_REVIVE                    0
#define FLAG_HIDE_SEAFOAM_ISLANDS_B2F_BIG_PEARL                 0
#define FLAG_HIDE_SEAFOAM_ISLANDS_B4F_ULTRA_BALL                0
#define FLAG_HIDE_FOUR_ISLAND_STAR_PIECE                        0
#define FLAG_HIDE_FOUR_ISLAND_STARDUST                          0
#define FLAG_HIDE_ONE_ISLAND_KINDLE_ROAD_ETHER                  0
#define FLAG_HIDE_ONE_ISLAND_KINDLE_ROAD_MAX_REPEL              0
#define FLAG_HIDE_ONE_ISLAND_KINDLE_ROAD_CARBOS                 0
#define FLAG_HIDE_FIVE_ISLAND_MEADOW_MAX_POTION                 0
#define FLAG_HIDE_FIVE_ISLAND_MEADOW_PP_UP                      0
#define FLAG_HIDE_FIVE_ISLAND_MEMORIAL_PILLAR_METAL_COAT        0
#define FLAG_HIDE_SIX_ISLAND_OUTCAST_ISLAND_PP_UP               0
#define FLAG_HIDE_SIX_ISLAND_WATER_PATH_ELIXIR                  0
#define FLAG_HIDE_SIX_ISLAND_WATER_PATH_DRAGON_SCALE            0
#define FLAG_HIDE_SIX_ISLAND_RUIN_VALLEY_FULL_RESTORE           0
#define FLAG_HIDE_SIX_ISLAND_RUIN_VALLEY_HP_UP                  0
#define FLAG_HIDE_SIX_ISLAND_RUIN_VALLEY_SUN_STONE              0
#define FLAG_HIDE_SEVEN_ISLAND_SEVAULT_CANYON_KINGS_ROCK        0
#define FLAG_HIDE_SEVEN_ISLAND_SEVAULT_CANYON_MAX_ELIXIR        0
#define FLAG_HIDE_SEVEN_ISLAND_SEVAULT_CANYON_NUGGET            0
#define FLAG_HIDE_THREE_ISLAND_BERRY_FOREST_MAX_ETHER           0
#define FLAG_HIDE_THREE_ISLAND_BERRY_FOREST_FULL_HEAL           0
#define FLAG_HIDE_THREE_ISLAND_BERRY_FOREST_MAX_ELIXIR          0
#define FLAG_HIDE_MT_EMBER_EXTERIOR_ULTRA_BALL                  0
#define FLAG_HIDE_MT_EMBER_EXTERIOR_FIRE_STONE                  0
#define FLAG_HIDE_MT_EMBER_EXTERIOR_DIRE_HIT                    0
#define FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_ULTRA_BALL        0
#define FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07              0
#define FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_B1F_FULL_RESTORE     0
#define FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_B1F_NEVER_MELT_ICE   0
#define FLAG_HIDE_FIVE_ISLAND_ROCKET_WAREHOUSE_BIG_PEARL        0
#define FLAG_HIDE_FIVE_ISLAND_ROCKET_WAREHOUSE_TM36             0
#define FLAG_HIDE_FIVE_ISLAND_ROCKET_WAREHOUSE_PEARL            0
#define FLAG_HIDE_FIVE_ISLAND_ROCKET_WAREHOUSE_UP_GRADE         0
#define FLAG_HIDE_FIVE_ISLAND_LOST_CAVE_ROOM10_SILK_SCARF       0
#define FLAG_HIDE_FIVE_ISLAND_LOST_CAVE_ROOM11_LAX_INCENSE      0
#define FLAG_HIDE_FIVE_ISLAND_LOST_CAVE_ROOM12_SEA_INCENSE      0
#define FLAG_HIDE_FIVE_ISLAND_LOST_CAVE_ROOM13_MAX_REVIVE       0
#define FLAG_HIDE_FIVE_ISLAND_LOST_CAVE_ROOM14_RARE_CANDY       0
#define FLAG_HIDE_SEVEN_ISLAND_SEVAULT_CANYON_HOUSE_LUCKY_PUNCH 0
#define FLAG_HIDE_SILPH_CO_4F_TM41                              0

#define STORY_FLAGS_START                                0
#define FLAG_GOT_POTION_ON_ROUTE_1                       0
#define FLAG_GOT_TM34_FROM_SURGE                         0
#define FLAG_GOT_FOSSIL_FROM_MT_MOON                     0
#define FLAG_HELPED_BILL_IN_SEA_COTTAGE                  0
#define FLAG_GOT_SS_TICKET                               0
#define FLAG_GOT_SS_TICKET_DUP                           0
#define FLAG_GOT_TM42_AT_MEMORIAL_PILLAR                 0
#define FLAG_GOT_HM01                                    0
#define FLAG_GOT_HM02                                    0
#define FLAG_GOT_HM03                                    0
#define FLAG_GOT_HM04                                    0
#define FLAG_GOT_HM05                                    0
#define FLAG_RESCUED_MR_FUJI                             0
#define FLAG_GOT_POKE_FLUTE                              0
#define FLAG_0x23E                                       0
#define FLAG_GOT_TM28_FROM_ROCKET                        0
#define FLAG_GOT_OLD_ROD                                 0
#define FLAG_GOT_BIKE_VOUCHER                            0
#define FLAG_0x242                                       0
#define FLAG_GOT_COIN_CASE                               0
#define FLAG_GOT_GOOD_ROD                                0
#define FLAG_GOT_TM29_FROM_MR_PSYCHIC                    0
#define FLAG_GOT_LAPRAS_FROM_SILPH                       0
#define FLAG_GOT_POKEBALLS_FROM_OAK_AFTER_22_RIVAL       0
#define FLAG_DID_MIMIEN_TRADE                            0
#define FLAG_BOUGHT_MAGIKARP                             0
#define FLAG_DID_ZYNX_TRADE                              0
#define FLAG_DID_MS_NIDO_TRADE                           0
#define FLAG_0x24C                                       0
#define FLAG_DID_CH_DING_TRADE                           0
#define FLAG_GOT_TM38_FROM_BLAINE                        0
#define FLAG_OAK_SKIP_22_RIVAL_CHECK                     0
#define FLAG_GOT_MASTER_BALL_FROM_SILPH                  0
#define FLAG_DID_NINA_TRADE                              0
#define FLAG_GOT_ITEMFINDER                              0
#define FLAG_WOKE_UP_ROUTE_12_SNORLAX                    0
#define FLAG_GOT_TM39_FROM_BROCK                         0
#define FLAG_GOT_SUPER_ROD                               0
#define FLAG_GOT_EXP_SHARE_FROM_OAKS_AIDE                0
#define FLAG_DID_MARC_TRADE                              0
#define FLAG_BEAT_RIVAL_IN_OAKS_LAB                      0
#define FLAG_GOT_TM06_FROM_KOGA                          0
#define FLAG_0x25A                                       0
#define FLAG_GOT_TM27                                    0
#define FLAG_0x25C                                       0
#define FLAG_0x25D                                       0
#define FLAG_GOT_OLD_AMBER                               0
#define FLAG_0x25F                                       0
#define FLAG_0x260                                       0
#define FLAG_0x261                                       0
#define FLAG_0x262                                       0
#define FLAG_GOT_EEVEE                                   0
#define FLAG_FOUND_BOTH_VERMILION_GYM_SWITCHES           0
#define FLAG_CINNABAR_GYM_QUIZ_1                         0
#define FLAG_CINNABAR_GYM_QUIZ_2                         0
#define FLAG_CINNABAR_GYM_QUIZ_3                         0
#define FLAG_CINNABAR_GYM_QUIZ_4                         0
#define FLAG_CINNABAR_GYM_QUIZ_5                         0
#define FLAG_CINNABAR_GYM_QUIZ_6                         0
#define FLAG_POKEMON_MANSION_SWITCH_STATE                0
#define FLAG_OPENED_ROCKET_HIDEOUT                       0
#define FLAG_GOT_10_COINS_FROM_GAMBLER                   0
#define FLAG_GOT_20_COINS_FROM_GAMBLER                   0
#define FLAG_GOT_20_COINS_FROM_GAMBLER_2                 0
#define FLAG_GOT_BICYCLE                                 0
#define FLAG_GOT_DOME_FOSSIL                             0
#define FLAG_GOT_HELIX_FOSSIL                            0
#define FLAG_DID_ESPHERE_TRADE                           0
#define FLAG_DID_TANGENY_TRADE                           0
#define FLAG_DID_SEELOR_TRADE                            0
#define FLAG_0x277                                       0
#define FLAG_GOT_HITMON_FROM_DOJO                        0
#define FLAG_0x279                                       0
#define FLAG_SILPH_2F_DOOR_1                             0
#define FLAG_SILPH_2F_DOOR_2                             0
#define FLAG_SILPH_3F_DOOR_1                             0
#define FLAG_SILPH_3F_DOOR_2                             0
#define FLAG_SILPH_4F_DOOR_1                             0
#define FLAG_SILPH_4F_DOOR_2                             0
#define FLAG_SILPH_5F_DOOR_1                             0
#define FLAG_SILPH_5F_DOOR_2                             0
#define FLAG_SILPH_5F_DOOR_3                             0
#define FLAG_SILPH_6F_DOOR                               0
#define FLAG_SILPH_7F_DOOR_1                             0
#define FLAG_SILPH_7F_DOOR_2                             0
#define FLAG_SILPH_7F_DOOR_3                             0
#define FLAG_SILPH_8F_DOOR                               0
#define FLAG_SILPH_9F_DOOR_1                             0
#define FLAG_SILPH_9F_DOOR_2                             0
#define FLAG_SILPH_9F_DOOR_3                             0
#define FLAG_SILPH_9F_DOOR_4                             0
#define FLAG_SILPH_10F_DOOR                              0
#define FLAG_SILPH_11F_DOOR                              0
#define FLAG_0x28E                                       0
#define FLAG_0x28F                                       0
#define FLAG_MET_STICKER_MAN                             0
#define FLAG_PALLET_LADY_NOT_BLOCKING_SIGN               0
#define FLAG_GOT_VS_SEEKER                               0
#define FLAG_GOT_TM19_FROM_ERIKA                         0
#define FLAG_GOT_TM33_FROM_THIRSTY_GIRL                  0
#define FLAG_GOT_TM20_FROM_THIRSTY_GIRL                  0
#define FLAG_GOT_TM16_FROM_THIRSTY_GIRL                  0
#define FLAG_GOT_TM03_FROM_MISTY                         0
#define FLAG_GOT_TM26_FROM_GIOVANNI                      0
#define FLAG_0x299                                       0
#define FLAG_GOT_TM04_FROM_SABRINA                       0
#define FLAG_GOT_FAME_CHECKER                            0
#define FLAG_GOT_RECORD_SETTING_MAGIKARP                 0
#define FLAG_TWO_ISLAND_SHOP_INTRODUCED                  0
#define FLAG_TWO_ISLAND_SHOP_EXPANDED_1                  0
#define FLAG_TWO_ISLAND_SHOP_EXPANDED_2                  0
#define FLAG_TWO_ISLAND_SHOP_EXPANDED_3                  0
#define FLAG_SEVII_DETOUR_FINISHED                       0
#define FLAG_VISITED_TWO_ISLAND                          0
#define FLAG_RESCUED_LOSTELLE                            0
#define FLAG_0x2A4                                       0
#define FLAG_CAN_USE_ROCKET_HIDEOUT_LIFT                 0
#define FLAG_GOT_TEA                                     0
#define FLAG_GOT_POWDER_JAR                              0
#define FLAG_FOUGHT_MEWTWO                               0
#define FLAG_FOUGHT_MOLTRES                              0
#define FLAG_FOUGHT_ARTICUNO                             0
#define FLAG_FOUGHT_ZAPDOS                               0
#define FLAG_TUTOR_DOUBLE_EDGE                           0
#define FLAG_TUTOR_THUNDER_WAVE                          0
#define FLAG_TUTOR_ROCK_SLIDE                            0
#define FLAG_TUTOR_EXPLOSION                             0
#define FLAG_TUTOR_MEGA_PUNCH                            0
#define FLAG_TUTOR_MEGA_KICK                             0
#define FLAG_TUTOR_DREAM_EATER                           0
#define FLAG_TUTOR_SOFT_BOILED                           0
#define FLAG_TUTOR_SUBSTITUTE                            0
#define FLAG_TUTOR_SWORDS_DANCE                          0
#define FLAG_TUTOR_SEISMIC_TOSS                          0
#define FLAG_TUTOR_COUNTER                               0
#define FLAG_TUTOR_METRONOME                             0
#define FLAG_TUTOR_MIMIC                                 0
#define FLAG_TUTOR_BODY_SLAM                             0
#define FLAG_VISITED_OAKS_LAB                            0
#define FLAG_FOUGHT_POWER_PLANT_ELECTRODE_1              0
#define FLAG_FOUGHT_POWER_PLANT_ELECTRODE_2              0
#define FLAG_STOPPED_SEAFOAM_B3F_CURRENT                 0
#define FLAG_STOPPED_SEAFOAM_B4F_CURRENT                 0
#define FLAG_TALKED_TO_LORELEI_AFTER_WAREHOUSE           0
#define FLAG_DEFEATED_ROCKETS_IN_WAREHOUSE               0
#define FLAG_UNLOCKED_ROCKET_WAREHOUSE                   0
#define FLAG_NO_ROOM_FOR_TM42_AT_MEMORIAL_PILLAR         0
#define FLAG_LEARNED_YES_NAH_CHANSEY                     0
#define FLAG_GOT_NEST_BALL_FROM_WATER_PATH_HOUSE_1       0
#define FLAG_GOT_TOGEPI_EGG                              0
#define FLAG_NO_ROOM_FOR_TOGEPI_EGG                      0
#define FLAG_RECOVERED_SAPPHIRE                          0
#define FLAG_GOT_RUBY                                    0
#define FLAG_TUTOR_FRENZY_PLANT                          0
#define FLAG_TUTOR_BLAST_BURN                            0
#define FLAG_TUTOR_HYDRO_CANNON                          0
#define FLAG_LEARNED_ALL_MOVES_AT_CAPE_BRINK             0
#define FLAG_GOT_NUGGET_FROM_DUNSPARCE_TUNNEL            0
#define FLAG_USED_CUT_ON_RUIN_VALLEY_BRAILLE             0
#define FLAG_FOUGHT_DEOXYS                               0
#define FLAG_0x2E5                                       0
#define FLAG_0x2E6                                       0
#define FLAG_0x2E7                                       0
#define FLAG_0x2E8                                       0
#define FLAG_0x2E9                                       0
#define FLAG_0x2EA                                       0
#define FLAG_0x2EB                                       0
#define FLAG_REVIVED_DOME                                0
#define FLAG_REVIVED_HELIX                               0
#define FLAG_REVIVED_AMBER                               0
#define FLAG_GOT_HM06                                    0
#define FLAG_FOUGHT_LUGIA                                0
#define FLAG_FOUGHT_HO_OH                                0
#define FLAG_OAK_SAW_DEX_COMPLETION                      0
#define FLAG_LUGIA_FLEW_AWAY                             0
#define FLAG_HO_OH_FLEW_AWAY                             0
#define FLAG_DEOXYS_FLEW_AWAY                            0
#define FLAG_TALKED_TO_TEA_LADY_AFTER_HOF                0
#define FLAG_TALKED_TO_OAKS_AIDE_IN_VERMILION            0
#define FLAG_GOT_EVERSTONE_FROM_OAKS_AIDE                0
#define FLAG_GOT_MOON_STONE_FROM_JOYFUL_GAME_CORNER      0
#define FLAG_GOT_FULL_RESTORE_FROM_THREE_ISLAND_DEFENDER 0
#define FLAG_GOT_AMULET_COIN_FROM_OAKS_AIDE              0
#define FLAG_NO_ROOM_FOR_JOYFUL_GAME_CORNER_MOON_STONE   0
#define FLAG_OAKS_RATING_IS_VIA_PC                       0

#define FLAG_HIDDEN_ITEM_VIRIDIAN_FOREST_POTION                            0
#define FLAG_HIDDEN_ITEM_VIRIDIAN_FOREST_ANTIDOTE                          0
#define FLAG_HIDDEN_ITEM_MT_MOON_B2F_MOON_STONE                            0
#define FLAG_HIDDEN_ITEM_MT_MOON_B2F_ETHER                                 0
#define FLAG_HIDDEN_ITEM_ROUTE25_ELIXIR                                    0
#define FLAG_HIDDEN_ITEM_ROUTE25_ETHER                                     0
#define FLAG_HIDDEN_ITEM_ROUTE9_ETHER                                      0
#define FLAG_HIDDEN_ITEM_UNUSED_0x07                                       0
#define FLAG_HIDDEN_ITEM_SSANNE_B1F_CORRIDOR_HYPER_POTION                  0
#define FLAG_HIDDEN_ITEM_ROUTE10_SUPER_POTION                              0
#define FLAG_HIDDEN_ITEM_ROUTE10_MAX_ETHER                                 0
#define FLAG_HIDDEN_ITEM_ROCKET_HIDEOUT_B1F_PP_UP                          0
#define FLAG_HIDDEN_ITEM_ROCKET_HIDEOUT_B3F_NUGGET                         0
#define FLAG_HIDDEN_ITEM_ROCKET_HIDEOUT_B4F_NEST_BALL                      0
#define FLAG_HIDDEN_ITEM_POKEMON_TOWER_5F_BIG_MUSHROOM                     0
#define FLAG_HIDDEN_ITEM_ROUTE13_PP_UP                                     0
#define FLAG_HIDDEN_ITEM_UNUSED_0x10                                       0
#define FLAG_HIDDEN_ITEM_ROUTE17_RARE_CANDY                                0
#define FLAG_HIDDEN_ITEM_ROUTE17_FULL_RESTORE                              0
#define FLAG_HIDDEN_ITEM_ROUTE17_PP_UP                                     0
#define FLAG_HIDDEN_ITEM_ROUTE17_MAX_REVIVE                                0
#define FLAG_HIDDEN_ITEM_ROUTE17_MAX_ELIXIR                                0
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_CENTER_LEAF_STONE                     0
#define FLAG_HIDDEN_ITEM_SAFARI_ZONE_WEST_REVIVE                           0
#define FLAG_HIDDEN_ITEM_SILPH_CO_5F_ELIXIR                                0
#define FLAG_HIDDEN_ITEM_SILPH_CO_9F_MAX_POTION                            0
#define FLAG_HIDDEN_ITEM_SAFFRON_CITY_COPYCATS_HOUSE_2F_NUGGET             0
#define FLAG_HIDDEN_ITEM_POWER_PLANT_MAX_ELIXIR                            0
#define FLAG_HIDDEN_ITEM_POWER_PLANT_THUNDER_STONE                         0
#define FLAG_HIDDEN_ITEM_SEAFOAM_ISLANDS_B3F_NUGGET                        0
#define FLAG_HIDDEN_ITEM_SEAFOAM_ISLANDS_B4F_WATER_STONE                   0
#define FLAG_HIDDEN_ITEM_POKEMON_MANSION_1F_MOON_STONE                     0
#define FLAG_HIDDEN_ITEM_POKEMON_MANSION_3F_RARE_CANDY                     0
#define FLAG_HIDDEN_ITEM_POKEMON_MANSION_B1F_ELIXIR                        0
#define FLAG_HIDDEN_ITEM_ROUTE23_FULL_RESTORE                              0
#define FLAG_HIDDEN_ITEM_ROUTE23_ULTRA_BALL                                0
#define FLAG_HIDDEN_ITEM_ROUTE23_MAX_ETHER                                 0
#define FLAG_HIDDEN_ITEM_VICTORY_ROAD_1F_FULL_RESTORE                      0
#define FLAG_HIDDEN_ITEM_CERULEAN_CAVE_1F_ULTRA_BALL                       0
#define FLAG_HIDDEN_ITEM_UNUSED_0x28                                       0
#define FLAG_HIDDEN_ITEM_ROUTE11_ESCAPE_ROPE                               0
#define FLAG_HIDDEN_ITEM_ROUTE12_HYPER_POTION                              0
#define FLAG_HIDDEN_ITEM_UNUSED_0x2B                                       0
#define FLAG_HIDDEN_ITEM_UNUSED_0x2C                                       0
#define FLAG_HIDDEN_ITEM_UNUSED_0x2D                                       0
#define FLAG_HIDDEN_ITEM_UNUSED_0x2E                                       0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_PP_UP                                0
#define FLAG_HIDDEN_ITEM_VERMILION_CITY_MAX_ETHER                          0
#define FLAG_HIDDEN_ITEM_CERULEAN_CITY_RARE_CANDY                          0
#define FLAG_HIDDEN_ITEM_ROUTE4_GREAT_BALL                                 0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS                    0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_2                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_3                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_4                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_5                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_6                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_7                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_8                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_9                  0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_10                 0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_11                 0
#define FLAG_HIDDEN_ITEM_CELADON_CITY_GAME_CORNER_COINS_12                 0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_SEVAULT_CANYON_CHERI_BERRY           0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TANOBY_RUINS_HEART_SCALE_4           0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TANOBY_RUINS_HEART_SCALE             0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TANOBY_RUINS_HEART_SCALE_2           0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TANOBY_RUINS_HEART_SCALE_3           0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_ROCKET_WAREHOUSE_NEST_BALL            0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_ROCKET_WAREHOUSE_NET_BALL             0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_POTION        0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_ANTIDOTE      0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_PARALYZE_HEAL 0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_AWAKENING     0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_BURN_HEAL     0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_ICE_HEAL      0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL_ETHER         0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_POTION          0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_ANTIDOTE        0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_PARALYZE_HEAL   0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_AWAKENING       0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_BURN_HEAL       0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_ICE_HEAL        0
#define FLAG_HIDDEN_ITEM_UNDERGROUND_PATH_EAST_WEST_TUNNEL_ETHER           0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_TINY_MUSHROOM                         0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_TINY_MUSHROOM_2                       0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_TINY_MUSHROOM_3                       0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_BIG_MUSHROOM                          0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_BIG_MUSHROOM_2                        0
#define FLAG_HIDDEN_ITEM_MT_MOON_B1F_BIG_MUSHROOM_3                        0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_RAZZ_BERRY              0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_BLUK_BERRY              0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_NANAB_BERRY             0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_WEPEAR_BERRY            0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_ORAN_BERRY              0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_CHERI_BERRY             0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_CHESTO_BERRY            0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_PECHA_BERRY             0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_RAWST_BERRY             0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_ASPEAR_BERRY            0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_PERSIM_BERRY            0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_PINAP_BERRY             0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BERRY_FOREST_LUM_BERRY               0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_STARDUST                0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_STARDUST_2              0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_PEARL                   0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_PEARL_2                 0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_ULTRA_BALL              0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_ULTRA_BALL_2            0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_STAR_PIECE              0
#define FLAG_HIDDEN_ITEM_ONE_ISLAND_TREASURE_BEACH_BIG_PEARL               0
#define FLAG_HIDDEN_ITEM_TWO_ISLAND_CAPE_BRINK_RARE_CANDY                  0
#define FLAG_HIDDEN_ITEM_PEWTER_CITY_POKE_BALL                             0
#define FLAG_HIDDEN_ITEM_ROUTE3_ORAN_BERRY                                 0
#define FLAG_HIDDEN_ITEM_ROUTE4_PERSIM_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE24_PECHA_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE25_ORAN_BERRY                                0
#define FLAG_HIDDEN_ITEM_ROUTE25_BLUK_BERRY                                0
#define FLAG_HIDDEN_ITEM_ROUTE6_SITRUS_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE6_RARE_CANDY                                 0
#define FLAG_HIDDEN_ITEM_SSANNE_KITCHEN_PECHA_BERRY                        0
#define FLAG_HIDDEN_ITEM_SSANNE_KITCHEN_CHERI_BERRY                        0
#define FLAG_HIDDEN_ITEM_SSANNE_KITCHEN_CHESTO_BERRY                       0
#define FLAG_HIDDEN_ITEM_ROUTE9_RARE_CANDY                                 0
#define FLAG_HIDDEN_ITEM_UNUSED_0x7C                                       0
#define FLAG_HIDDEN_ITEM_ROUTE10_PERSIM_BERRY                              0
#define FLAG_HIDDEN_ITEM_ROUTE10_CHERI_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE8_RAWST_BERRY                                0
#define FLAG_HIDDEN_ITEM_ROUTE8_LUM_BERRY                                  0
#define FLAG_HIDDEN_ITEM_ROUTE8_LEPPA_BERRY                                0
#define FLAG_HIDDEN_ITEM_ROUTE12_RARE_CANDY                                0
#define FLAG_HIDDEN_ITEM_ROUTE12_LEFTOVERS                                 0
#define FLAG_HIDDEN_ITEM_ROUTE16_LEFTOVERS                                 0
#define FLAG_HIDDEN_ITEM_FUCHSIA_CITY_MAX_REVIVE                           0
#define FLAG_HIDDEN_ITEM_ROCKET_HIDEOUT_B4F_NET_BALL                       0
#define FLAG_HIDDEN_ITEM_SILPH_CO_2F_ULTRA_BALL                            0
#define FLAG_HIDDEN_ITEM_SILPH_CO_3F_PROTEIN                               0
#define FLAG_HIDDEN_ITEM_SILPH_CO_4F_IRON                                  0
#define FLAG_HIDDEN_ITEM_SILPH_CO_5F_PP_UP                                 0
#define FLAG_HIDDEN_ITEM_SILPH_CO_6F_CARBOS                                0
#define FLAG_HIDDEN_ITEM_SILPH_CO_7F_ZINC                                  0
#define FLAG_HIDDEN_ITEM_SILPH_CO_8F_NUGGET                                0
#define FLAG_HIDDEN_ITEM_SILPH_CO_9F_CALCIUM                               0
#define FLAG_HIDDEN_ITEM_SILPH_CO_10F_HP_UP                                0
#define FLAG_HIDDEN_ITEM_SILPH_CO_11F_REVIVE                               0
#define FLAG_HIDDEN_ITEM_ROUTE23_LUM_BERRY                                 0
#define FLAG_HIDDEN_ITEM_ROUTE23_SITRUS_BERRY                              0
#define FLAG_HIDDEN_ITEM_ROUTE23_ASPEAR_BERRY                              0
#define FLAG_HIDDEN_ITEM_ROUTE23_LEPPA_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE14_ZINC                                      0
#define FLAG_HIDDEN_ITEM_ROUTE9_CHESTO_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE10_NANAB_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE7_WEPEAR_BERRY                               0
#define FLAG_HIDDEN_ITEM_ROUTE20_STARDUST                                  0
#define FLAG_HIDDEN_ITEM_ROUTE21_NORTH_PEARL                               0
#define FLAG_HIDDEN_ITEM_ROUTE23_MAX_ELIXIR                                0
#define FLAG_HIDDEN_ITEM_ROUTE4_RAZZ_BERRY                                 0
#define FLAG_HIDDEN_ITEM_ROUTE14_PINAP_BERRY                               0
#define FLAG_HIDDEN_ITEM_MT_EMBER_EXTERIOR_FIRE_STONE                      0
#define FLAG_HIDDEN_ITEM_POKEMON_TOWER_7F_SOOTHE_BELL                      0
#define FLAG_HIDDEN_ITEM_NAVEL_ROCK_SUMMIT_SACRED_ASH                      0
#define FLAG_HIDDEN_ITEM_TWO_ISLAND_CAPE_BRINK_PP_MAX                      0
#define FLAG_HIDDEN_ITEM_MT_EMBER_EXTERIOR_ULTRA_BALL                      0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_DUNSPARCE_TUNNEL_NUGGET              0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_PP_UP                                0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BOND_BRIDGE_MAX_REPEL                0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BOND_BRIDGE_PEARL                    0
#define FLAG_HIDDEN_ITEM_THREE_ISLAND_BOND_BRIDGE_STARDUST                 0
#define FLAG_HIDDEN_ITEM_FOUR_ISLAND_PEARL                                 0
#define FLAG_HIDDEN_ITEM_FOUR_ISLAND_ULTRA_BALL                            0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_MEMORIAL_PILLAR_BIG_PEARL             0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_MEMORIAL_PILLAR_RAZZ_BERRY            0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_MEMORIAL_PILLAR_SITRUS_BERRY          0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_MEMORIAL_PILLAR_BLUK_BERRY            0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_RESORT_GORGEOUS_NEST_BALL             0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_RESORT_GORGEOUS_STARDUST              0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_RESORT_GORGEOUS_STAR_PIECE            0
#define FLAG_HIDDEN_ITEM_FIVE_ISLAND_RESORT_GORGEOUS_STARDUST_2            0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_OUTCAST_ISLAND_STAR_PIECE              0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_OUTCAST_ISLAND_NET_BALL                0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_GREEN_PATH_ULTRA_BALL                  0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_WATER_PATH_ASPEAR_BERRY                0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_WATER_PATH_ORAN_BERRY                  0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_WATER_PATH_PINAP_BERRY                 0
#define FLAG_HIDDEN_ITEM_SIX_ISLAND_LEPPA_BERRY                            0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TRAINER_TOWER_BIG_PEARL              0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TRAINER_TOWER_PEARL                  0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_TRAINER_TOWER_NANAB_BERRY            0
#define FLAG_HIDDEN_ITEM_SEVEN_ISLAND_SEVAULT_CANYON_ENTRANCE_RAWST_BERRY  0
#define FLAG_HIDDEN_ITEM_VIRIDIAN_CITY_GYM_MACHO_BRACE                     0
#define FLAG_HIDDEN_ITEM_SSANNE_EXTERIOR_LAVA_COOKIE                       0

#define FLAG_DEFEATED_BROCK           0
#define FLAG_DEFEATED_MISTY           0
#define FLAG_DEFEATED_LT_SURGE        0
#define FLAG_DEFEATED_ERIKA           0
#define FLAG_DEFEATED_KOGA            0
#define FLAG_DEFEATED_SABRINA         0
#define FLAG_DEFEATED_BLAINE          0
#define FLAG_DEFEATED_LEADER_GIOVANNI 0
#define FLAG_DEFEATED_LORELEI         0
#define FLAG_DEFEATED_BRUNO           0
#define FLAG_DEFEATED_AGATHA          0
#define FLAG_DEFEATED_LANCE           0
#define FLAG_DEFEATED_CHAMP           0

#define FLAG_0x82A                                                  0
#define FLAG_0x82B                                                  0
#define FLAG_SYS_SET_TRAINER_CARD_PROFILE                           0
#define FLAG_0x82E                                                  0
#define FLAG_SYS_ON_CYCLING_ROAD                                    0
#define FLAG_0x831                                                  0
#define FLAG_0x832                                                  0
#define FLAG_0x833                                                  0
#define FLAG_0x835                                                  0
#define FLAG_0x836                                                  0
#define FLAG_0x838                                                  0 // Set, never read
#define FLAG_0x83A                                                  0
#define FLAG_SYS_SAW_HELP_SYSTEM_INTRO                              0
#define FLAG_0x83D                                                  0
#define FLAG_OPENED_START_MENU                                      0
#define FLAG_SYS_PC_STORAGE_DISABLED                                0
#define FLAG_SYS_SEVII_MAP_123                                      0
#define FLAG_SYS_SEVII_MAP_4567                                     0
#define FLAG_SYS_GOT_BERRY_POUCH                                    0
#define FLAG_SYS_UNLOCKED_TANOBY_RUINS                              0

// World Map Flags
#define FLAG_WORLD_MAP_PALLET_TOWN                                  0
#define FLAG_WORLD_MAP_VIRIDIAN_CITY                                0
#define FLAG_WORLD_MAP_PEWTER_CITY                                  0
#define FLAG_WORLD_MAP_CERULEAN_CITY                                0
#define FLAG_WORLD_MAP_LAVENDER_TOWN                                0
#define FLAG_WORLD_MAP_VERMILION_CITY                               0
#define FLAG_WORLD_MAP_CELADON_CITY                                 0
#define FLAG_WORLD_MAP_FUCHSIA_CITY                                 0
#define FLAG_WORLD_MAP_CINNABAR_ISLAND                              0
#define FLAG_WORLD_MAP_INDIGO_PLATEAU_EXTERIOR                      0
#define FLAG_WORLD_MAP_SAFFRON_CITY                                 0
#define FLAG_WORLD_MAP_ONE_ISLAND                                   0
#define FLAG_WORLD_MAP_TWO_ISLAND                                   0
#define FLAG_WORLD_MAP_THREE_ISLAND                                 0
#define FLAG_WORLD_MAP_FOUR_ISLAND                                  0
#define FLAG_WORLD_MAP_FIVE_ISLAND                                  0
#define FLAG_WORLD_MAP_SEVEN_ISLAND                                 0
#define FLAG_WORLD_MAP_SIX_ISLAND                                   0
#define FLAG_WORLD_MAP_ROUTE4_POKEMON_CENTER_1F                     0
#define FLAG_WORLD_MAP_ROUTE10_POKEMON_CENTER_1F                    0
#define FLAG_WORLD_MAP_VIRIDIAN_FOREST                              0
#define FLAG_WORLD_MAP_MT_MOON_1F                                   0
#define FLAG_WORLD_MAP_SSANNE_EXTERIOR                              0
#define FLAG_WORLD_MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL          0
#define FLAG_WORLD_MAP_UNDERGROUND_PATH_EAST_WEST_TUNNEL            0
#define FLAG_WORLD_MAP_DIGLETTS_CAVE_B1F                            0
#define FLAG_WORLD_MAP_VICTORY_ROAD_1F                              0
#define FLAG_WORLD_MAP_ROCKET_HIDEOUT_B1F                           0
#define FLAG_WORLD_MAP_SILPH_CO_1F                                  0
#define FLAG_WORLD_MAP_POKEMON_MANSION_1F                           0
#define FLAG_WORLD_MAP_SAFARI_ZONE_CENTER                           0
#define FLAG_WORLD_MAP_POKEMON_LEAGUE_LORELEIS_ROOM                 0
#define FLAG_WORLD_MAP_ROCK_TUNNEL_1F                               0
#define FLAG_WORLD_MAP_SEAFOAM_ISLANDS_1F                           0
#define FLAG_WORLD_MAP_POKEMON_TOWER_1F                             0
#define FLAG_WORLD_MAP_CERULEAN_CAVE_1F                             0
#define FLAG_WORLD_MAP_POWER_PLANT                                  0
#define FLAG_WORLD_MAP_NAVEL_ROCK_EXTERIOR                          0
#define FLAG_WORLD_MAP_MT_EMBER_EXTERIOR                            0
#define FLAG_WORLD_MAP_THREE_ISLAND_BERRY_FOREST                    0
#define FLAG_WORLD_MAP_FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE            0
#define FLAG_WORLD_MAP_FIVE_ISLAND_ROCKET_WAREHOUSE                 0
#define FLAG_WORLD_MAP_TRAINER_TOWER_LOBBY                          0
#define FLAG_WORLD_MAP_SIX_ISLAND_DOTTED_HOLE_1F                    0
#define FLAG_WORLD_MAP_FIVE_ISLAND_LOST_CAVE_ENTRANCE               0
#define FLAG_WORLD_MAP_SIX_ISLAND_PATTERN_BUSH                      0
#define FLAG_WORLD_MAP_SIX_ISLAND_ALTERING_CAVE                     0
#define FLAG_WORLD_MAP_SEVEN_ISLAND_TANOBY_RUINS_MONEAN_CHAMBER     0
#define FLAG_WORLD_MAP_THREE_ISLAND_DUNSPARCE_TUNNEL                0
#define FLAG_WORLD_MAP_SEVEN_ISLAND_SEVAULT_CANYON_TANOBY_KEY       0
#define FLAG_WORLD_MAP_BIRTH_ISLAND_EXTERIOR                        0

#endif

#if TESTING
#define TESTING_FLAGS_START                     0x5000
#define TESTING_FLAG_SLEEP_CLAUSE               (TESTING_FLAGS_START + 0x0)
#define TESTING_FLAG_INVERSE_BATTLE             (TESTING_FLAGS_START + 0x1)
#define TESTING_FLAG_TRAINER_SLIDES             (TESTING_FLAGS_START + 0x2)
#define TESTING_FLAG_UNUSED_3                   (TESTING_FLAGS_START + 0x3)
#define TESTING_FLAG_UNUSED_4                   (TESTING_FLAGS_START + 0x4)
#define TESTING_FLAG_UNUSED_5                   (TESTING_FLAGS_START + 0x5)
#define TESTING_FLAG_UNUSED_6                   (TESTING_FLAGS_START + 0x6)
#define TESTING_FLAG_UNUSED_7                   (TESTING_FLAGS_START + 0x7)
#endif // TESTING


#endif // GUARD_CONSTANTS_FLAGS_H

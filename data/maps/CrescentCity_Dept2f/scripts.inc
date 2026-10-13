CrescentCity_Dept2f_MapScripts::
	.byte 0

@ Second floor: evolution stones and held items (clerk 0), TMs whose stock grows with the badges (clerk 1).

CrescentCity_Dept2f_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	@ the Linking Cord (every trade evolution) and the Prism Scale (Feebas -> Milotic) join the stock at the third badge
	goto_if_ge VAR_ORLEANS_STORY, 45, CrescentCity_Dept2f_EventScript_Clerk03
	goto_if_set FLAG_BADGE06_GET, CrescentCity_Dept2f_EventScript_Clerk02
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Dept2f_EventScript_Clerk01
	pokemart CrescentCity_Dept2f_Pokemart_Clerk00
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

@ the Metal Alloy (Duraludon -> Archaludon) joins the stock at the sixth badge; after the game is cleared the Sun, Ice, Dusk and Shiny Stones and the six EX vitamins (SoulGold, 40000 each) too
CrescentCity_Dept2f_EventScript_Clerk02:
	pokemart CrescentCity_Dept2f_Pokemart_Clerk02
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept2f_EventScript_Clerk03:
	pokemart CrescentCity_Dept2f_Pokemart_Clerk03
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept2f_EventScript_Clerk01:
	pokemart CrescentCity_Dept2f_Pokemart_Clerk01
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk00:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_EVERSTONE
	.2byte ITEM_HEART_SCALE
	pokemartlistend

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk01:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_LINKING_CORD
	.2byte ITEM_EVERSTONE
	.2byte ITEM_PRISM_SCALE
	.2byte ITEM_HEART_SCALE
	pokemartlistend

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk02:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_LINKING_CORD
	.2byte ITEM_EVERSTONE
	.2byte ITEM_PRISM_SCALE
	.2byte ITEM_METAL_ALLOY
	.2byte ITEM_HEART_SCALE
	pokemartlistend

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk03:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_SUN_STONE
	.2byte ITEM_ICE_STONE
	.2byte ITEM_DUSK_STONE
	.2byte ITEM_SHINY_STONE
	.2byte ITEM_LINKING_CORD
	.2byte ITEM_EVERSTONE
	.2byte ITEM_PRISM_SCALE
	.2byte ITEM_METAL_ALLOY
	.2byte ITEM_HP_UP_EX
	.2byte ITEM_PROTEIN_EX
	.2byte ITEM_IRON_EX
	.2byte ITEM_CALCIUM_EX
	.2byte ITEM_ZINC_EX
	.2byte ITEM_CARBOS_EX
	.2byte ITEM_LIFE_ORB
	.2byte ITEM_CHOICE_SPECS
	.2byte ITEM_CHOICE_SCARF
	.2byte ITEM_ASSAULT_VEST
	.2byte ITEM_FOCUS_SASH
	.2byte ITEM_EXPERT_BELT
	.2byte ITEM_ROCKY_HELMET
	.2byte ITEM_WEAKNESS_POLICY
	.2byte ITEM_EVIOLITE
	.2byte ITEM_SHELL_BELL
	.2byte ITEM_BLACK_SLUDGE
	.2byte ITEM_LIGHT_CLAY
	.2byte ITEM_FLAME_ORB
	.2byte ITEM_TOXIC_ORB
	.2byte ITEM_MUSCLE_BAND
	.2byte ITEM_WISE_GLASSES
	.2byte ITEM_AIR_BALLOON
	.2byte ITEM_HEAVY_DUTY_BOOTS
	.2byte ITEM_SITRUS_BERRY
	.2byte ITEM_SALAC_BERRY
	.2byte ITEM_LIECHI_BERRY
	.2byte ITEM_PETAYA_BERRY
	.2byte ITEM_LEPPA_BERRY
	.2byte ITEM_SILK_SCARF
	.2byte ITEM_BLACK_BELT
	.2byte ITEM_SHARP_BEAK
	.2byte ITEM_POISON_BARB
	.2byte ITEM_SOFT_SAND
	.2byte ITEM_HARD_STONE
	.2byte ITEM_SILVER_POWDER
	.2byte ITEM_SPELL_TAG
	.2byte ITEM_METAL_COAT
	.2byte ITEM_CHARCOAL
	.2byte ITEM_MYSTIC_WATER
	.2byte ITEM_MIRACLE_SEED
	.2byte ITEM_MAGNET
	.2byte ITEM_TWISTED_SPOON
	.2byte ITEM_NEVER_MELT_ICE
	.2byte ITEM_DRAGON_FANG
	.2byte ITEM_BLACK_GLASSES
	.2byte ITEM_FAIRY_FEATHER
	.2byte ITEM_OCCA_BERRY
	.2byte ITEM_PASSHO_BERRY
	.2byte ITEM_WACAN_BERRY
	.2byte ITEM_RINDO_BERRY
	.2byte ITEM_YACHE_BERRY
	.2byte ITEM_CHOPLE_BERRY
	.2byte ITEM_KEBIA_BERRY
	.2byte ITEM_SHUCA_BERRY
	.2byte ITEM_COBA_BERRY
	.2byte ITEM_PAYAPA_BERRY
	.2byte ITEM_TANGA_BERRY
	.2byte ITEM_CHARTI_BERRY
	.2byte ITEM_KASIB_BERRY
	.2byte ITEM_HABAN_BERRY
	.2byte ITEM_COLBUR_BERRY
	.2byte ITEM_BABIRI_BERRY
	.2byte ITEM_ROSELI_BERRY
	.2byte ITEM_LIGHT_BALL
	.2byte ITEM_HEART_SCALE
	pokemartlistend

CrescentCity_Dept2f_EventScript_Clerk1::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	goto_if_set FLAG_BADGE05_GET, CrescentCity_Dept2f_EventScript_Clerk12
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Dept2f_EventScript_Clerk11
	pokemart CrescentCity_Dept2f_Pokemart_Clerk10
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept2f_EventScript_Clerk11:
	pokemart CrescentCity_Dept2f_Pokemart_Clerk11
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept2f_EventScript_Clerk12:
	pokemart CrescentCity_Dept2f_Pokemart_Clerk12
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk10:
	.2byte ITEM_TM_DOUBLE_TEAM
	.2byte ITEM_TM_REST
	.2byte ITEM_TM_SANDSTORM
	.2byte ITEM_TM_RAIN_DANCE
	.2byte ITEM_TM_SUNNY_DAY
	.2byte ITEM_TM_ROCK_TOMB
	pokemartlistend

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk11:
	.2byte ITEM_TM_DOUBLE_TEAM
	.2byte ITEM_TM_REST
	.2byte ITEM_TM_SANDSTORM
	.2byte ITEM_TM_RAIN_DANCE
	.2byte ITEM_TM_SUNNY_DAY
	.2byte ITEM_TM_ROCK_TOMB
	.2byte ITEM_TM_SLUDGE_BOMB
	.2byte ITEM_TM_FACADE
	.2byte ITEM_TM_AERIAL_ACE
	.2byte ITEM_TM_BRICK_BREAK
	.2byte ITEM_TM_REFLECT
	.2byte ITEM_TM_LIGHT_SCREEN
	pokemartlistend

	.align 2
CrescentCity_Dept2f_Pokemart_Clerk12:
	.2byte ITEM_TM_DOUBLE_TEAM
	.2byte ITEM_TM_REST
	.2byte ITEM_TM_SANDSTORM
	.2byte ITEM_TM_RAIN_DANCE
	.2byte ITEM_TM_SUNNY_DAY
	.2byte ITEM_TM_ROCK_TOMB
	.2byte ITEM_TM_SLUDGE_BOMB
	.2byte ITEM_TM_FACADE
	.2byte ITEM_TM_AERIAL_ACE
	.2byte ITEM_TM_BRICK_BREAK
	.2byte ITEM_TM_REFLECT
	.2byte ITEM_TM_LIGHT_SCREEN
	.2byte ITEM_TM_THUNDERBOLT
	.2byte ITEM_TM_ICE_BEAM
	.2byte ITEM_TM_FLAMETHROWER
	.2byte ITEM_TM_PSYCHIC
	.2byte ITEM_TM_SOLAR_BEAM
	pokemartlistend

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Dept2f_EventScript_Shopper2::
	msgbox CrescentCity_Dept2f_Text_Shopper2, MSGBOX_NPC
	end

CrescentCity_Dept2f_Text_Shopper2:
	.string "Trade evolutions only need a\nLinking Cord here. No trade!$"

@ --- mapgen: generated NPC scripts (end) ---

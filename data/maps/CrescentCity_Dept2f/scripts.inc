CrescentCity_Dept2f_MapScripts::
	.byte 0

@ Second floor: evolution stones and held items (clerk 0), TMs whose stock grows with the badges (clerk 1).

CrescentCity_Dept2f_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	@ the Linking Cord (every trade evolution) and the Prism Scale (Feebas -> Milotic) join the stock at the third badge
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Dept2f_EventScript_Clerk01
	pokemart CrescentCity_Dept2f_Pokemart_Clerk00
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

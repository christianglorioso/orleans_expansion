CrescentCity_Cafe_MapScripts::
	.byte 0

@ The ROTOM quest (after gym 3): the blender. Before the badge it only pranks; after, the ROTOM inside battles (wild, level 22).
CrescentCity_Cafe_EventScript_RotomBlender2::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_Cafe_EventScript_RotomQuiet
	playmoncry SPECIES_ROTOM_FAN, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_Cafe_Text_RotomGo, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM_FAN, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_Cafe_EventScript_RotomDone
	release
	end

CrescentCity_Cafe_EventScript_RotomDone:
	setflag FLAG_CRESCENT_ROTOM_BLENDER
	removeobject LOCALID_CRESCENT_CITY_CAFE_ROTOM_BLENDER2
	release
	end

CrescentCity_Cafe_EventScript_RotomQuiet:
	msgbox CrescentCity_Cafe_Text_RotomQuiet, MSGBOX_DEFAULT
	release
	end

@ The barista hands over the Pokeblock case once (free), then sells berries.
CrescentCity_Cafe_EventScript_Clerk0::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_POKEBLOCK_CASE, CrescentCity_Cafe_EventScript_Sell
	msgbox CrescentCity_Cafe_Text_CaseOffer, MSGBOX_DEFAULT
	giveitem ITEM_POKEBLOCK_CASE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_POKEBLOCK_CASE
	msgbox CrescentCity_Cafe_Text_CaseInfo, MSGBOX_DEFAULT
CrescentCity_Cafe_EventScript_Sell:
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Cafe_Pokemart_Berries
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Cafe_Pokemart_Berries:
	.2byte ITEM_ORAN_BERRY
	.2byte ITEM_CHERI_BERRY
	.2byte ITEM_CHESTO_BERRY
	.2byte ITEM_PECHA_BERRY
	.2byte ITEM_RAWST_BERRY
	.2byte ITEM_ASPEAR_BERRY
	.2byte ITEM_PERSIM_BERRY
	.2byte ITEM_LUM_BERRY
	pokemartlistend

CrescentCity_Cafe_Text_RotomQuiet:
	.string "The blender whirs up on its own,\n"
	.string "then stops. Then whirs again.$"

CrescentCity_Cafe_Text_RotomGo:
	.string "The blender turns itself on and\n"
	.string "off. It sounds like a chuckle.\p"
	.string "The lid blasts off! A ROTOM whirls\n"
	.string "out on a gust of air!$"

CrescentCity_Cafe_Text_CaseOffer:
	.string "BARISTA: Welcome! Here, a POKéBLOCK\n"
	.string "case, on the house. Free for all.\p"
	.string "Blend berries, bake a block, and\n"
	.string "your POKéMON will love you for it.$"

CrescentCity_Cafe_Text_CaseInfo:
	.string "BARISTA: The blender's temperamental\n"
	.string "lately. Mind it. What'll it be?$"

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Cafe_EventScript_Regular1::
	msgbox CrescentCity_Cafe_Text_Regular1, MSGBOX_NPC
	end

CrescentCity_Cafe_Text_Regular1:
	.string "Pokéblocks make my POKéMON happy.\nAnd a little glossy.$"

@ --- mapgen: generated NPC scripts (end) ---

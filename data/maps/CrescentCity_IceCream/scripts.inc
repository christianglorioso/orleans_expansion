CrescentCity_IceCream_MapScripts::
	.byte 0

@ The ROTOM quest (after gym 3): the freezer. Before the badge it only pranks; after, the ROTOM inside battles (wild, level 22).
CrescentCity_IceCream_EventScript_RotomFreezer2::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_IceCream_EventScript_RotomQuiet
	playmoncry SPECIES_ROTOM_FROST, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_IceCream_Text_RotomGo, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM_FROST, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CrescentCity_IceCream_EventScript_RotomDone
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_IceCream_EventScript_RotomDone
	release
	end

CrescentCity_IceCream_EventScript_RotomDone:
	setflag FLAG_CRESCENT_ROTOM_FREEZER
	removeobject LOCALID_CRESCENT_CITY_ICE_CREAM_ROTOM_FREEZER2
	release
	end

CrescentCity_IceCream_EventScript_RotomQuiet:
	msgbox CrescentCity_IceCream_Text_RotomQuiet, MSGBOX_DEFAULT
	release
	end

@ The ice-cream counter sells status cures
CrescentCity_IceCream_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_IceCream_Pokemart_Clerk0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_IceCream_Pokemart_Clerk0:
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	pokemartlistend

CrescentCity_IceCream_Text_RotomQuiet:
	.string "The freezer door frosts over by\n"
	.string "itself. A cold light blinks inside.$"

CrescentCity_IceCream_Text_RotomGo:
	.string "The freezer rattles. Frost creeps\n"
	.string "over the handle.\p"
	.string "Cold air pours out. A ROTOM spins\n"
	.string "out of the freezer, grinning!$"

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_IceCream_EventScript_Kid1::
	msgbox CrescentCity_IceCream_Text_Kid1, MSGBOX_NPC
	end

CrescentCity_IceCream_Text_Kid1:
	.string "The freezer growled at me!\nCold in there. Colder than usual.$"

@ --- mapgen: generated NPC scripts (end) ---

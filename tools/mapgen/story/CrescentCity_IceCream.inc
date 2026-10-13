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
	goto_if_set FLAG_RECEIVED_VANILLITE, CrescentCity_IceCream_EventScript_ClerkShop
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_IceCream_EventScript_ClerkShop
	msgbox CrescentCity_IceCream_Text_VanilliteOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_IceCream_EventScript_ClerkShop
	checkmoney 2500
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_IceCream_EventScript_VanilliteNoMoney
	givemon SPECIES_VANILLITE, 20
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, CrescentCity_IceCream_EventScript_VanilliteNoRoom
	removemoney 2500
	setflag FLAG_RECEIVED_VANILLITE
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, CrescentCity_IceCream_EventScript_VanilliteToPC
	msgbox CrescentCity_IceCream_Text_VanilliteGiven, MSGBOX_DEFAULT
	goto CrescentCity_IceCream_EventScript_ClerkShop

CrescentCity_IceCream_EventScript_VanilliteToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_VANILLITE
	call Common_EventScript_TransferredToPC
	msgbox CrescentCity_IceCream_Text_VanilliteGiven, MSGBOX_DEFAULT
	goto CrescentCity_IceCream_EventScript_ClerkShop

CrescentCity_IceCream_EventScript_VanilliteNoMoney:
	msgbox CrescentCity_IceCream_Text_VanilliteNoMoney, MSGBOX_DEFAULT
	goto CrescentCity_IceCream_EventScript_ClerkShop

CrescentCity_IceCream_EventScript_VanilliteNoRoom:
	call Common_EventScript_NoMoreRoomForPokemon
	release
	end

CrescentCity_IceCream_EventScript_ClerkShop:
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

CrescentCity_IceCream_Text_VanilliteOffer:
	.string "A VANILLITE is cooling in the back\n"
	.string "freezer. 2500 and it's yours.\p"
	.string "It's an ice cream cone with a soul.\n"
	.string "Would you like to take it home?$"

CrescentCity_IceCream_Text_VanilliteGiven:
	.string "You received a VANILLITE!\p"
	.string "Keep it cold and it'll keep you\n"
	.string "company.$"

CrescentCity_IceCream_Text_VanilliteNoMoney:
	.string "Oh, you're a bit short. Come back\n"
	.string "when you've got 2500.$"

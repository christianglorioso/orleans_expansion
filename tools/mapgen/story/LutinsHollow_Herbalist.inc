LutinsHollow_Herbalist_MapScripts::
	.byte 0

@ The herbalist: bitter medicine that works
LutinsHollow_Herbalist_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart LutinsHollow_Herbalist_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
LutinsHollow_Herbalist_Pokemart:
	.2byte ITEM_HEAL_POWDER
	.2byte ITEM_ENERGY_POWDER
	.2byte ITEM_ENERGY_ROOT
	.2byte ITEM_REVIVAL_HERB
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_REPEL
	pokemartlistend

@ the Floette (Eternal Flower) and its Floettite: after the game is cleared (story 45), one each (own flags; the Floettite also if the party was full)
LutinsHollow_Herbalist_EventScript_Apprentice1::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 45, LutinsHollow_Herbalist_EventScript_ApprenticeSeed
	goto_if_set FLAG_RECEIVED_FLOETTE_EF, LutinsHollow_Herbalist_EventScript_ApprenticeStone
	msgbox LutinsHollow_Herbalist_Text_Woke, MSGBOX_DEFAULT
	givemon SPECIES_FLOETTE_ETERNAL, 50
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, LutinsHollow_Herbalist_EventScript_ApprenticeNoRoom
	setflag FLAG_RECEIVED_FLOETTE_EF
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, LutinsHollow_Herbalist_EventScript_ApprenticeToPC
	playfanfare MUS_OBTAIN_ITEM
	msgbox LutinsHollow_Herbalist_Text_FloetteGiven, MSGBOX_DEFAULT
	waitfanfare
	goto LutinsHollow_Herbalist_EventScript_ApprenticeStone

LutinsHollow_Herbalist_EventScript_ApprenticeToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_FLOETTE_ETERNAL
	call Common_EventScript_TransferredToPC
	goto LutinsHollow_Herbalist_EventScript_ApprenticeStone

LutinsHollow_Herbalist_EventScript_ApprenticeStone:
	goto_if_set FLAG_RECEIVED_FLOETTITE, LutinsHollow_Herbalist_EventScript_ApprenticeAfter
	msgbox LutinsHollow_Herbalist_Text_WokeStone, MSGBOX_DEFAULT
	giveitem ITEM_FLOETTITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_FLOETTITE
	release
	end

LutinsHollow_Herbalist_EventScript_ApprenticeAfter:
	msgbox LutinsHollow_Herbalist_Text_After, MSGBOX_DEFAULT
	release
	end

LutinsHollow_Herbalist_EventScript_ApprenticeNoRoom:
	msgbox LutinsHollow_Herbalist_Text_NoRoom, MSGBOX_DEFAULT
	release
	end

LutinsHollow_Herbalist_EventScript_ApprenticeSeed:
	msgbox LutinsHollow_Herbalist_Text_Seed, MSGBOX_DEFAULT
	release
	end

LutinsHollow_Herbalist_Text_Seed:
	.string "The Floette seed is for later. It\n"
	.string "wakes after the great storm.$"

LutinsHollow_Herbalist_Text_FloetteGiven:
	.string "{PLAYER} received FLOETTE from the\n"
	.string "apprentice!$"

LutinsHollow_Herbalist_Text_Woke:
	.string "The seed woke! After the great storm\n"
	.string "it bloomed into a FLOETTE with an\p"
	.string "eternal flower. It chose you.$"

LutinsHollow_Herbalist_Text_WokeStone:
	.string "And this came up with it:\n"
	.string "a FLOETTITE.$"

LutinsHollow_Herbalist_Text_NoRoom:
	.string "Your party and boxes are full. Make\n"
	.string "room and come back to me.$"

LutinsHollow_Herbalist_Text_After:
	.string "The garden's lovelier since the\n"
	.string "storm passed.$"

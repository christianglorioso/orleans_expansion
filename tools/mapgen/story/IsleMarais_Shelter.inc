IsleMarais_Shelter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IsleMarais_Shelter_OnTransition
	.byte 0

@ The shelter is home for now: the player respawns here, and a new game is initialised on the first arrival.
IsleMarais_Shelter_OnTransition:
	setrespawn HEAL_LOCATION_ISLE_MARAIS
	goto_if_set FLAG_ORLEANS_GAME_STARTED, IsleMarais_Shelter_OnTransitionEnd
	setflag FLAG_ORLEANS_GAME_STARTED
	@ everyone who turns up later in the story starts hidden
	setflag FLAG_HIDE_SHELTER_TOTODILE
	setflag FLAG_HIDE_SHELTER_CHIKORITA
	setflag FLAG_HIDE_SHELTER_FUECOCO
	setflag FLAG_HIDE_SHELTER_JAYDEN
	setflag FLAG_HIDE_SHELTER_WREN
	setflag FLAG_HIDE_PLAYERS_HOUSE_MOM
	setflag FLAG_HIDE_ROUTE1_LAFAYETTE
	setflag FLAG_HIDE_OLD_WATER_TUPELO
	setflag FLAG_HIDE_OLD_WATER_WREN
	setflag FLAG_HIDE_WRENS_HOUSE_WREN
	setflag FLAG_HIDE_GRAND_OAK_WREN
IsleMarais_Shelter_OnTransitionEnd:
	end

@ ---------------------------------------------------------------- step 1: Mom's gifts, step 2: the rescuers
IsleMarais_Shelter_EventScript_Mother0::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 2, IsleMarais_Shelter_EventScript_MotherCareful
	goto_if_eq VAR_ORLEANS_STORY, 1, IsleMarais_Shelter_EventScript_MotherGoOn
	msgbox IsleMarais_Shelter_Text_MotherMorning, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message IsleMarais_Shelter_Text_ReceivedShoes
	waitfanfare
	setflag FLAG_SYS_B_DASH
	msgbox IsleMarais_Shelter_Text_ShoesInfo, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message IsleMarais_Shelter_Text_ReceivedPokenav
	waitfanfare
	setflag FLAG_SYS_POKENAV_GET
	msgbox IsleMarais_Shelter_Text_MotherPokenav, MSGBOX_DEFAULT
	closemessage
	@ the rescue crew comes in with three Pokémon
	fadescreen FADE_TO_BLACK
	clearflag FLAG_HIDE_SHELTER_TOTODILE
	clearflag FLAG_HIDE_SHELTER_CHIKORITA
	clearflag FLAG_HIDE_SHELTER_FUECOCO
	addobject LOCALID_ISLE_MARAIS_SHELTER_TOTODILE7
	addobject LOCALID_ISLE_MARAIS_SHELTER_CHIKORITA8
	addobject LOCALID_ISLE_MARAIS_SHELTER_FUECOCO9
	msgbox IsleMarais_Shelter_Text_DoorBangs, MSGBOX_DEFAULT
	fadescreen FADE_FROM_BLACK
	msgbox IsleMarais_Shelter_Text_RescuersArrive, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 1
	release
	end

IsleMarais_Shelter_EventScript_MotherGoOn:
	msgbox IsleMarais_Shelter_Text_MotherGoOn, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_MotherCareful:
	msgbox IsleMarais_Shelter_Text_MotherCareful, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_Lafayette1::
	lock
	faceplayer
	goto_if_eq VAR_ORLEANS_STORY, 1, IsleMarais_Shelter_EventScript_LafayettePick
	msgbox IsleMarais_Shelter_Text_LafayetteWaiting, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_LafayettePick:
	msgbox IsleMarais_Shelter_Text_LafayettePick, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_Fisherman5::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_OLD_ROD, IsleMarais_Shelter_EventScript_FishermanAfterRod
	goto_if_lt VAR_ORLEANS_STORY, 2, IsleMarais_Shelter_EventScript_FishermanRescue
	msgbox IsleMarais_Shelter_Text_FishermanOfferRod, MSGBOX_DEFAULT
	giveitem ITEM_OLD_ROD
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_OLD_ROD
	msgbox IsleMarais_Shelter_Text_FishermanRodInfo, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_FishermanRescue:
	msgbox IsleMarais_Shelter_Text_FishermanRescue, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_FishermanAfterRod:
	msgbox IsleMarais_Shelter_Text_FishermanAfterRod, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- step 3: the starter pick
@ VAR_STARTER_MON: 0 = Totodile, 1 = Chikorita, 2 = Fuecoco (the player's pick).
@ Jayden takes the one with the advantage, Wren's people raise the third.
IsleMarais_Shelter_EventScript_Totodile7::
	lock
	faceplayer
	bufferspeciesname STR_VAR_1, SPECIES_TOTODILE
	msgbox IsleMarais_Shelter_Text_TotodileLooks, MSGBOX_DEFAULT
	msgbox IsleMarais_Shelter_Text_LookAfterIt, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IsleMarais_Shelter_EventScript_NotYet
	setvar VAR_STARTER_MON, 0
	removeobject LOCALID_ISLE_MARAIS_SHELTER_TOTODILE7
	setflag FLAG_HIDE_SHELTER_TOTODILE
	givemon SPECIES_TOTODILE, 5
	goto IsleMarais_Shelter_EventScript_ReceivedStarter

IsleMarais_Shelter_EventScript_Chikorita8::
	lock
	faceplayer
	bufferspeciesname STR_VAR_1, SPECIES_CHIKORITA
	msgbox IsleMarais_Shelter_Text_ChikoritaLooks, MSGBOX_DEFAULT
	msgbox IsleMarais_Shelter_Text_LookAfterIt, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IsleMarais_Shelter_EventScript_NotYet
	setvar VAR_STARTER_MON, 1
	removeobject LOCALID_ISLE_MARAIS_SHELTER_CHIKORITA8
	setflag FLAG_HIDE_SHELTER_CHIKORITA
	givemon SPECIES_CHIKORITA, 5
	goto IsleMarais_Shelter_EventScript_ReceivedStarter

IsleMarais_Shelter_EventScript_Fuecoco9::
	lock
	faceplayer
	bufferspeciesname STR_VAR_1, SPECIES_FUECOCO
	msgbox IsleMarais_Shelter_Text_FuecocoLooks, MSGBOX_DEFAULT
	msgbox IsleMarais_Shelter_Text_LookAfterIt, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IsleMarais_Shelter_EventScript_NotYet
	setvar VAR_STARTER_MON, 2
	removeobject LOCALID_ISLE_MARAIS_SHELTER_FUECOCO9
	setflag FLAG_HIDE_SHELTER_FUECOCO
	givemon SPECIES_FUECOCO, 5
	goto IsleMarais_Shelter_EventScript_ReceivedStarter

IsleMarais_Shelter_EventScript_NotYet:
	release
	end

IsleMarais_Shelter_EventScript_ReceivedStarter:
	setflag FLAG_SYS_POKEMON_GET
	playfanfare MUS_OBTAIN_ITEM
	message IsleMarais_Shelter_Text_ReceivedStarter
	waitmessage
	waitfanfare
	msgbox IsleMarais_Shelter_Text_LafayetteGoodMatch, MSGBOX_DEFAULT
	closemessage
	@ Jayden comes in with Rita's recruiters and takes the one with the advantage
	clearflag FLAG_HIDE_SHELTER_JAYDEN
	addobject LOCALID_ISLE_MARAIS_SHELTER_JAYDEN10
	msgbox IsleMarais_Shelter_Text_JaydenArrives, MSGBOX_DEFAULT
	call_if_eq VAR_STARTER_MON, 0, IsleMarais_Shelter_EventScript_JaydenTakesChikorita
	call_if_eq VAR_STARTER_MON, 1, IsleMarais_Shelter_EventScript_JaydenTakesFuecoco
	call_if_eq VAR_STARTER_MON, 2, IsleMarais_Shelter_EventScript_JaydenTakesTotodile
	msgbox IsleMarais_Shelter_Text_JaydenLeaves, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ISLE_MARAIS_SHELTER_JAYDEN10
	setflag FLAG_HIDE_SHELTER_JAYDEN
	fadescreen FADE_FROM_BLACK
	@ Wren, watching quietly, asks for the third
	clearflag FLAG_HIDE_SHELTER_WREN
	addobject LOCALID_ISLE_MARAIS_SHELTER_WREN11
	msgbox IsleMarais_Shelter_Text_WrenAsks, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	call_if_eq VAR_STARTER_MON, 0, IsleMarais_Shelter_EventScript_WrenTakesFuecoco
	call_if_eq VAR_STARTER_MON, 1, IsleMarais_Shelter_EventScript_WrenTakesTotodile
	call_if_eq VAR_STARTER_MON, 2, IsleMarais_Shelter_EventScript_WrenTakesChikorita
	removeobject LOCALID_ISLE_MARAIS_SHELTER_WREN11
	setflag FLAG_HIDE_SHELTER_WREN
	fadescreen FADE_FROM_BLACK
	msgbox IsleMarais_Shelter_Text_LafayetteHeadsOut, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ISLE_MARAIS_SHELTER_LAFAYETTE1
	setflag FLAG_HIDE_SHELTER_LAFAYETTE
	clearflag FLAG_HIDE_ROUTE1_LAFAYETTE
	fadescreen FADE_FROM_BLACK
	setvar VAR_ORLEANS_STORY, 2
	release
	end

IsleMarais_Shelter_EventScript_JaydenTakesChikorita:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_CHIKORITA8
	setflag FLAG_HIDE_SHELTER_CHIKORITA
	bufferspeciesname STR_VAR_2, SPECIES_CHIKORITA
	msgbox IsleMarais_Shelter_Text_JaydenTakes, MSGBOX_DEFAULT
	return

IsleMarais_Shelter_EventScript_JaydenTakesFuecoco:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_FUECOCO9
	setflag FLAG_HIDE_SHELTER_FUECOCO
	bufferspeciesname STR_VAR_2, SPECIES_FUECOCO
	msgbox IsleMarais_Shelter_Text_JaydenTakes, MSGBOX_DEFAULT
	return

IsleMarais_Shelter_EventScript_JaydenTakesTotodile:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_TOTODILE7
	setflag FLAG_HIDE_SHELTER_TOTODILE
	bufferspeciesname STR_VAR_2, SPECIES_TOTODILE
	msgbox IsleMarais_Shelter_Text_JaydenTakes, MSGBOX_DEFAULT
	return

IsleMarais_Shelter_EventScript_WrenTakesFuecoco:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_FUECOCO9
	setflag FLAG_HIDE_SHELTER_FUECOCO
	return

IsleMarais_Shelter_EventScript_WrenTakesTotodile:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_TOTODILE7
	setflag FLAG_HIDE_SHELTER_TOTODILE
	return

IsleMarais_Shelter_EventScript_WrenTakesChikorita:
	removeobject LOCALID_ISLE_MARAIS_SHELTER_CHIKORITA8
	setflag FLAG_HIDE_SHELTER_CHIKORITA
	return

IsleMarais_Shelter_EventScript_Jayden10::
	msgbox IsleMarais_Shelter_Text_JaydenArrives, MSGBOX_NPC
	end

IsleMarais_Shelter_EventScript_Wren11::
	msgbox IsleMarais_Shelter_Text_WrenAsks, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- text
IsleMarais_Shelter_Text_MotherMorning:
	.string "MOM: Morning, sweetheart.\n"
	.string "Did you sleep at all? Me neither.\p"
	.string "The streets are a mess out there.\n"
	.string "Take these, so you can get around.$"

IsleMarais_Shelter_Text_ReceivedShoes:
	.string "{PLAYER} received the\n"
	.string "RUNNING SHOES!$"

IsleMarais_Shelter_Text_ShoesInfo:
	.string "Hold the B Button to run.$"

IsleMarais_Shelter_Text_ReceivedPokenav:
	.string "{PLAYER} received a POKéNAV!$"

IsleMarais_Shelter_Text_MotherPokenav:
	.string "MOM: And keep this on you.\n"
	.string "If the lines go down again,\p"
	.string "I want to know where you are.$"

IsleMarais_Shelter_Text_DoorBangs:
	.string "The door bangs open.\n"
	.string "The rescue crew is back!$"

IsleMarais_Shelter_Text_RescuersArrive:
	.string "FISHERMAN: PROFESSOR! We found\n"
	.string "these three on a porch roof in\p"
	.string "the flooded district!\p"
	.string "LAFAYETTE: Bring them here.\n"
	.string "{PLAYER}, could you give me a hand\p"
	.string "settling them?$"

IsleMarais_Shelter_Text_MotherGoOn:
	.string "MOM: Go on, the PROFESSOR\n"
	.string "needs a hand.$"

IsleMarais_Shelter_Text_MotherCareful:
	.string "MOM: Be careful out there,\n"
	.string "both of you.$"

IsleMarais_Shelter_Text_LafayetteWaiting:
	.string "LAFAYETTE: The rescue crew went\n"
	.string "out to the flooded district at dawn.\p"
	.string "I've set up here until they're back.$"

IsleMarais_Shelter_Text_LafayettePick:
	.string "LAFAYETTE: They're cold and scared.\n"
	.string "See if one of them takes to you.$"

IsleMarais_Shelter_Text_FishermanRescue:
	.string "FISHERMAN: The water came right up\n"
	.string "the streets. We pulled what we could\p"
	.string "off the roofs.$"

IsleMarais_Shelter_Text_FishermanOfferRod:
	.string "FISHERMAN: You've got a partner now!\n"
	.string "Here, the fish are still biting.$"

IsleMarais_Shelter_Text_FishermanRodInfo:
	.string "FISHERMAN: Cast it anywhere there's\n"
	.string "water. Plenty of that around here.$"

IsleMarais_Shelter_Text_FishermanAfterRod:
	.string "FISHERMAN: Caught anything yet?$"

IsleMarais_Shelter_Text_TotodileLooks:
	.string "TOTODILE is shivering, but it\n"
	.string "snaps its jaws at you, curious.$"

IsleMarais_Shelter_Text_ChikoritaLooks:
	.string "CHIKORITA's leaf is drooping, but\n"
	.string "it nudges your hand.$"

IsleMarais_Shelter_Text_FuecocoLooks:
	.string "FUECOCO is soaked through. It\n"
	.string "puffs a tiny flame at you.$"

IsleMarais_Shelter_Text_LookAfterIt:
	.string "Will you look after {STR_VAR_1}?$"

IsleMarais_Shelter_Text_ReceivedStarter:
	.string "{PLAYER} received {STR_VAR_1}!$"

IsleMarais_Shelter_Text_LafayetteGoodMatch:
	.string "LAFAYETTE: A good match.\n"
	.string "Keep it close; it needs a friend.$"

IsleMarais_Shelter_Text_JaydenArrives:
	.string "JAYDEN: So this is where they\n"
	.string "brought them.$"

IsleMarais_Shelter_Text_JaydenTakes:
	.string "JAYDEN: I'll take {STR_VAR_2}.\n"
	.string "My crew needs strong POKéMON.\p"
	.string "LAFAYETTE: Jayden, wait-$"

IsleMarais_Shelter_Text_JaydenLeaves:
	.string "JAYDEN: ...Don't look at me like\n"
	.string "that. Someone has to fix things.$"

IsleMarais_Shelter_Text_WrenAsks:
	.string "WREN: ...Excuse me.\n"
	.string "My people can raise the last one.\p"
	.string "We know the water. It'll be safe\n"
	.string "with us.$"

IsleMarais_Shelter_Text_LafayetteHeadsOut:
	.string "LAFAYETTE: Well. That went\n"
	.string "faster than I planned.\p"
	.string "I'm heading up to ROUTE 1 to count\n"
	.string "what the storm moved. Meet me there!$"

@ the Fais Do-Do Ribbon (Chapter 10 audit: Petilil -> Hisuian Lilligant): the accordion player gives it once the sixth badge is held
IsleMarais_Shelter_EventScript_Accordion6::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_FAIS_DO_DO, IsleMarais_Shelter_EventScript_AccordionAfter
	goto_if_unset FLAG_BADGE06_GET, IsleMarais_Shelter_EventScript_AccordionTune
	msgbox IsleMarais_Shelter_Text_Ribbon1, MSGBOX_DEFAULT
	giveitem ITEM_FAIS_DO_DO_RIBBON
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_FAIS_DO_DO
	msgbox IsleMarais_Shelter_Text_RibbonGiven, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_AccordionAfter:
	msgbox IsleMarais_Shelter_Text_RibbonAfter, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_EventScript_AccordionTune:
	msgbox IsleMarais_Shelter_Text_Accordion, MSGBOX_DEFAULT
	release
	end

IsleMarais_Shelter_Text_Accordion:
	.string "Someone still plays that old\n"
	.string "accordion every evening.$"

IsleMarais_Shelter_Text_Ribbon1:
	.string "The accordion player grins. You've\n"
	.string "danced a long road, haven't you?\p"
	.string "Take this fais do-do ribbon. It's\n"
	.string "for whoever the dance picks. A shy\p"
	.string "PETILIL would love it.$"

IsleMarais_Shelter_Text_RibbonGiven:
	.string "Hold it to a PETILIL and it will\n"
	.string "dance into a HISUIAN LILLIGANT.$"

IsleMarais_Shelter_Text_RibbonAfter:
	.string "Fais do-do! Dance till the lamps\n"
	.string "go out.$"

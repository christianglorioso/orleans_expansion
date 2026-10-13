Route24_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route24_OnTransitionPG
	.byte 0

@ The cracked shaft (Chapter 9, F.2): stand below the dome's door at (39, 7) facing up. Needs the Lantern (Fifolet) and the telling (story >= 39); it leads
@ down to the Salt Cathedral (Groudon's raid arena).
Route24_EventScript_SaltShaft::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 39, Route24_EventScript_ShaftNotYet
	checkitem ITEM_LANTERN
	goto_if_eq VAR_RESULT, FALSE, Route24_EventScript_ShaftNoLight
	msgbox Route24_Text_ShaftGo, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warpsilent MAP_LANDS_END_SALT_CATHEDRAL, 10, 15
	waitstate
	releaseall
	end

Route24_EventScript_ShaftNoLight:
	msgbox Route24_Text_ShaftNoLight, MSGBOX_DEFAULT
	releaseall
	end

Route24_EventScript_ShaftNotYet:
	msgbox Route24_Text_ShaftNotYet, MSGBOX_DEFAULT
	releaseall
	end

Route24_Text_ShaftNoLight:
	.string "A crack in the rock breathes heat.\n"
	.string "The dark below is total. A light\p"
	.string "would help.$"

Route24_Text_ShaftNotYet:
	.string "The crack breathes heat. Not yet.\n"
	.string "The telling comes first.$"

Route24_Text_ShaftGo:
	.string "The LANTERN's steady flame leads you\n"
	.string "down the cracked shaft.$"

@ --- route trainers (gen_route_trainers.py) ---
Route24_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE24_HIKER, Route24_Text_Route24HikerIntro, Route24_Text_Route24HikerDefeat
	msgbox Route24_Text_Route24HikerAfter, MSGBOX_AUTOCLOSE
	end

Route24_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE24_CAMPER, Route24_Text_Route24CamperIntro, Route24_Text_Route24CamperDefeat
	msgbox Route24_Text_Route24CamperAfter, MSGBOX_AUTOCLOSE
	end

Route24_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE24_EXPERT, Route24_Text_Route24ExpertIntro, Route24_Text_Route24ExpertDefeat
	msgbox Route24_Text_Route24ExpertAfter, MSGBOX_AUTOCLOSE
	end

Route24_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE24_RUIN_MANIAC, Route24_Text_Route24RuinManiacIntro, Route24_Text_Route24RuinManiacDefeat
	msgbox Route24_Text_Route24RuinManiacAfter, MSGBOX_AUTOCLOSE
	end

Route24_Text_Route24HikerIntro:
	.string "Salt gets into everything. Even\nmy boots. Even my battles.$"

Route24_Text_Route24HikerDefeat:
	.string "Salted.$"

Route24_Text_Route24HikerAfter:
	.string "The old mine goes deep. The\nground cracked last month.$"

Route24_Text_Route24CamperIntro:
	.string "I camp on the flats. Nothing\ngrows here but my nerve.$"

Route24_Text_Route24CamperDefeat:
	.string "Nerve lost.$"

Route24_Text_Route24CamperAfter:
	.string "A shaft opened in the rock. It\nbreathes heat. Don't stand near.$"

Route24_Text_Route24ExpertIntro:
	.string "I study the heat under the\nflats. And trainers.$"

Route24_Text_Route24ExpertDefeat:
	.string "Data gathered.$"

Route24_Text_Route24ExpertAfter:
	.string "Something enormous sleeps down\nthere. The readings say so.$"

Route24_Text_Route24RuinManiacIntro:
	.string "These tunnels are older than\nthe town. Don't touch the walls.$"

Route24_Text_Route24RuinManiacDefeat:
	.string "Walled in.$"

Route24_Text_Route24RuinManiacAfter:
	.string "The oldest wall has carvings.\nRootkin hands. A verse, maybe.$"

@ --- end route trainers ---

Route24_OnTransitionPG:
	call Route24_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route24_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route24_EventScript_PGHide
Route24_EventScript_PGSetupDone:
	return

Route24_EventScript_PGHide:
	setflag FLAG_PG_CORNERSTONE_MASK
	return

Route24_EventScript_PgCornerstoneMask::
	lock
	giveitem ITEM_CORNERSTONE_MASK
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_PG_CORNERSTONE_MASK
	removeobject LOCALID_ROUTE24_PG_CORNERSTONE_MASK
	release
	end

@ --- end post-game ---

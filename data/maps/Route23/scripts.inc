Route23_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route23_OnTransitionPG
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route23_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_HIKER, Route23_Text_Route23HikerIntro, Route23_Text_Route23HikerDefeat
	msgbox Route23_Text_Route23HikerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_RUIN_MANIAC, Route23_Text_Route23RuinManiacIntro, Route23_Text_Route23RuinManiacDefeat
	msgbox Route23_Text_Route23RuinManiacAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_PICNICKER, Route23_Text_Route23PicnickerIntro, Route23_Text_Route23PicnickerDefeat
	msgbox Route23_Text_Route23PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_BLACK_BELT, Route23_Text_Route23BlackBeltIntro, Route23_Text_Route23BlackBeltDefeat
	msgbox Route23_Text_Route23BlackBeltAfter, MSGBOX_AUTOCLOSE
	end

Route23_Text_Route23HikerIntro:
	.string "The dust's gone, finally. The\nplains are mine again.$"

Route23_Text_Route23HikerDefeat:
	.string "Dust to dust.$"

Route23_Text_Route23HikerAfter:
	.string "The salt mine's north-east. Don't\ngo in without a light.$"

Route23_Text_Route23RuinManiacIntro:
	.string "The storm uncovered an old wall.\nI'm guarding it. Fight me!$"

Route23_Text_Route23RuinManiacDefeat:
	.string "Buried.$"

Route23_Text_Route23RuinManiacAfter:
	.string "The wall sings when the wind\nhits it. Like a flute.$"

Route23_Text_Route23PicnickerIntro:
	.string "Grass grows back through dust.\nI came to watch it.$"

Route23_Text_Route23PicnickerDefeat:
	.string "Pressed flat.$"

Route23_Text_Route23PicnickerAfter:
	.string "A shadow crossed the whole sky.\nI felt it in my teeth.$"

Route23_Text_Route23BlackBeltIntro:
	.string "The storm's lifted. My training\ncan resume. Spar with me!$"

Route23_Text_Route23BlackBeltDefeat:
	.string "Sparred out.$"

Route23_Text_Route23BlackBeltAfter:
	.string "Cleaner air makes better\ntraining.$"

@ --- end route trainers ---

Route23_OnTransitionPG:
	call Route23_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route23_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route23_EventScript_PGHide
	goto_if_lt VAR_ORLEANS_STORY, 45, Route23_EventScript_PGSetupDone
	call Route23_EventScript_PGNightUrsalunaBm
Route23_EventScript_PGSetupDone:
	return

Route23_EventScript_PGHide:
	setflag FLAG_PG_LANDORUS
	setflag FLAG_PG_AZELF
	setflag FLAG_PG_URSALUNA_BM
	return

Route23_EventScript_PgLandorus::
	lock
	faceplayer
	playmoncry SPECIES_LANDORUS, CRY_MODE_ENCOUNTER
	msgbox Route23_Text_PGLandorus, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_LANDORUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_EventScript_PgLandorusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_EventScript_PgLandorusStill
	release
	end

Route23_EventScript_PgLandorusStill:
	msgbox Route23_Text_PGStillLandorus, MSGBOX_DEFAULT
	release
	end

Route23_EventScript_PgLandorusDone:
	setflag FLAG_PG_LANDORUS
	removeobject LOCALID_ROUTE23_PG_LANDORUS
	release
	end

Route23_EventScript_PgAzelf::
	lock
	faceplayer
	playmoncry SPECIES_AZELF, CRY_MODE_ENCOUNTER
	msgbox Route23_Text_PGAzelf, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_AZELF, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_EventScript_PgAzelfDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_EventScript_PgAzelfStill
	release
	end

Route23_EventScript_PgAzelfStill:
	msgbox Route23_Text_PGStillAzelf, MSGBOX_DEFAULT
	release
	end

Route23_EventScript_PgAzelfDone:
	setflag FLAG_PG_AZELF
	removeobject LOCALID_ROUTE23_PG_AZELF
	release
	end

Route23_EventScript_PgUrsalunaBm::
	lock
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Route23_EventScript_PgUrsalunaBmNight
	msgbox Route23_Text_PGDayUrsalunaBm, MSGBOX_DEFAULT
	setflag FLAG_PG_URSALUNA_BM
	removeobject LOCALID_ROUTE23_PG_URSALUNA_BM
	release
	end

Route23_EventScript_PgUrsalunaBmNight:
	faceplayer
	playmoncry SPECIES_URSALUNA_BLOODMOON, CRY_MODE_ENCOUNTER
	msgbox Route23_Text_PGUrsalunaBm, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_URSALUNA_BLOODMOON, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_EventScript_PgUrsalunaBmDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_EventScript_PgUrsalunaBmStill
	release
	end

Route23_EventScript_PgUrsalunaBmStill:
	msgbox Route23_Text_PGStillUrsalunaBm, MSGBOX_DEFAULT
	release
	end

Route23_EventScript_PgUrsalunaBmDone:
	setflag FLAG_PG_URSALUNA_BM
	setflag FLAG_PG_URSALUNA_DONE
	removeobject LOCALID_ROUTE23_PG_URSALUNA_BM
	release
	end

Route23_EventScript_PGNightUrsalunaBm:
	goto_if_set FLAG_PG_URSALUNA_DONE, Route23_EventScript_PGNightHideUrsalunaBm
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, FALSE, Route23_EventScript_PGNightHideUrsalunaBm
	clearflag FLAG_PG_URSALUNA_BM
	return

Route23_EventScript_PGNightHideUrsalunaBm:
	setflag FLAG_PG_URSALUNA_BM
	return

Route23_Text_PGLandorus:
	.string "LANDORUS stands before you,\n"
	.string "the ground trembling under it.$"

Route23_Text_PGStillLandorus:
	.string "LANDORUS shakes itself off,\n"
	.string "still standing its ground.$"

Route23_Text_PGAzelf:
	.string "AZELF stands before you,\n"
	.string "its will gleaming like a blade.$"

Route23_Text_PGStillAzelf:
	.string "AZELF shakes itself off,\n"
	.string "still standing its ground.$"

Route23_Text_PGUrsalunaBm:
	.string "URSALUNA stands before you,\n"
	.string "a red moon in its eyes.$"

Route23_Text_PGStillUrsalunaBm:
	.string "URSALUNA shakes itself off,\n"
	.string "still standing its ground.$"

Route23_Text_PGDayUrsalunaBm:
	.string "URSALUNA dislikes the daylight and\n"
	.string "slips back into the brush.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

Route23_EventScript_SignCity::
	msgbox Route23_Text_SignCity, MSGBOX_SIGN
	end

Route23_Text_SignCity:
	.string "POINTE ROUGE\nCity limits: welcome!$"

Route23_EventScript_RouteSign1::
	msgbox Route23_Text_RouteSign1, MSGBOX_SIGN
	end

Route23_Text_RouteSign1:
	.string "AZELF'S RIDGE\nA shrine stands on the heights.$"

Route23_EventScript_RouteSign2::
	msgbox Route23_Text_RouteSign2, MSGBOX_SIGN
	end

Route23_Text_RouteSign2:
	.string "DUST STORM WARNING\nThe road closes when the wind rises.$"

Route23_EventScript_RouteSign3::
	msgbox Route23_Text_RouteSign3, MSGBOX_SIGN
	end

Route23_Text_RouteSign3:
	.string "FERTILE HOLLOW\nThe ground is green here, oddly.$"

@ --- mapgen: generated NPC scripts (end) ---

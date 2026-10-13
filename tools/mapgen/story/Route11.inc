Route11_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route11_OnTransitionPG
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route11_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER_F, Route11_Text_Route11SwimmerFIntro, Route11_Text_Route11SwimmerFDefeat
	msgbox Route11_Text_Route11SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route11_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER, Route11_Text_Route11SwimmerIntro, Route11_Text_Route11SwimmerDefeat
	msgbox Route11_Text_Route11SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route11_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER_2, Route11_Text_Route11Swimmer2Intro, Route11_Text_Route11Swimmer2Defeat
	msgbox Route11_Text_Route11Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route11_Text_Route11SwimmerFIntro:
	.string "The water's perfect today. Is\nyour team, though?$"

Route11_Text_Route11SwimmerFDefeat:
	.string "Lost the current.$"

Route11_Text_Route11SwimmerFAfter:
	.string "The lake's colder past the\nsecond bend.$"

Route11_Text_Route11SwimmerIntro:
	.string "I race the ferries. Today\nI race you!$"

Route11_Text_Route11SwimmerDefeat:
	.string "Second place again.$"

Route11_Text_Route11SwimmerAfter:
	.string "Routes 12 and 13 climb into\nthe hills. It's green up there.$"

Route11_Text_Route11Swimmer2Intro:
	.string "Slow down! This is a toll lake.\nThe toll is a battle.$"

Route11_Text_Route11Swimmer2Defeat:
	.string "Toll paid.$"

Route11_Text_Route11Swimmer2After:
	.string "I saw something glow under the\nlilies at dusk. Twice.$"

@ --- end route trainers ---

Route11_OnTransitionPG:
	call Route11_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route11_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route11_EventScript_PGHide
Route11_EventScript_PGSetupDone:
	return

Route11_EventScript_PGHide:
	setflag FLAG_PG_SUICUNE
	return

Route11_EventScript_PgSuicune::
	lock
	faceplayer
	playmoncry SPECIES_SUICUNE, CRY_MODE_ENCOUNTER
	msgbox Route11_Text_PGSuicune, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_SUICUNE, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route11_EventScript_PgSuicuneDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route11_EventScript_PgSuicuneStill
	release
	end

Route11_EventScript_PgSuicuneStill:
	msgbox Route11_Text_PGStillSuicune, MSGBOX_DEFAULT
	release
	end

Route11_EventScript_PgSuicuneDone:
	setflag FLAG_PG_SUICUNE
	removeobject LOCALID_ROUTE11_PG_SUICUNE
	release
	end

Route11_Text_PGSuicune:
	.string "SUICUNE stands before you,\n"
	.string "the water around it perfectly still.$"

Route11_Text_PGStillSuicune:
	.string "SUICUNE shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

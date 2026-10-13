Route17_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route17_OnTransitionPG
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route17_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_KINDLER, Route17_Text_Route17KindlerIntro, Route17_Text_Route17KindlerDefeat
	msgbox Route17_Text_Route17KindlerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_BIRD_KEEPER, Route17_Text_Route17BirdKeeperIntro, Route17_Text_Route17BirdKeeperDefeat
	msgbox Route17_Text_Route17BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_COOLTRAINER, Route17_Text_Route17CooltrainerIntro, Route17_Text_Route17CooltrainerDefeat
	msgbox Route17_Text_Route17CooltrainerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_HIKER, Route17_Text_Route17HikerIntro, Route17_Text_Route17HikerDefeat
	msgbox Route17_Text_Route17HikerAfter, MSGBOX_AUTOCLOSE
	end

Route17_Text_Route17KindlerIntro:
	.string "The mill's gym burns bright.\nWarm up on me first!$"

Route17_Text_Route17KindlerDefeat:
	.string "Doused.$"

Route17_Text_Route17KindlerAfter:
	.string "CAYENNE does not lose to the\ncold. Or to anyone, really.$"

Route17_Text_Route17BirdKeeperIntro:
	.string "Thermals over the cane field!\nMy birds love them.$"

Route17_Text_Route17BirdKeeperDefeat:
	.string "Fell out of the sky.$"

Route17_Text_Route17BirdKeeperAfter:
	.string "Smoke rises, birds follow. It's\nan old trick.$"

Route17_Text_Route17CooltrainerIntro:
	.string "Two badges short of the next\ntown. Let's see yours!$"

Route17_Text_Route17CooltrainerDefeat:
	.string "You've earned them.$"

Route17_Text_Route17CooltrainerAfter:
	.string "A sunny day, a sunny gym. It's\na hard combination.$"

Route17_Text_Route17HikerIntro:
	.string "The last stretch before the\nmill. I'll make it harder!$"

Route17_Text_Route17HikerDefeat:
	.string "Stumbled.$"

Route17_Text_Route17HikerAfter:
	.string "Past the gate, the sun's the\njudge. Come at noon.$"

@ --- end route trainers ---

Route17_OnTransitionPG:
	call Route17_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route17_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route17_EventScript_PGHide
Route17_EventScript_PGSetupDone:
	return

Route17_EventScript_PGHide:
	setflag FLAG_PG_MOLTRES
	return

Route17_EventScript_PgMoltres::
	lock
	faceplayer
	playmoncry SPECIES_MOLTRES, CRY_MODE_ENCOUNTER
	msgbox Route17_Text_PGMoltres, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_MOLTRES, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route17_EventScript_PgMoltresDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route17_EventScript_PgMoltresStill
	release
	end

Route17_EventScript_PgMoltresStill:
	msgbox Route17_Text_PGStillMoltres, MSGBOX_DEFAULT
	release
	end

Route17_EventScript_PgMoltresDone:
	setflag FLAG_PG_MOLTRES
	removeobject LOCALID_ROUTE17_PG_MOLTRES
	release
	end

Route17_Text_PGMoltres:
	.string "MOLTRES stands before you,\n"
	.string "wings burning like a forge.$"

Route17_Text_PGStillMoltres:
	.string "MOLTRES shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

Route12_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route12_OnTransitionPG
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route12_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_BIRD_KEEPER, Route12_Text_Route12BirdKeeperIntro, Route12_Text_Route12BirdKeeperDefeat
	msgbox Route12_Text_Route12BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_HIKER, Route12_Text_Route12HikerIntro, Route12_Text_Route12HikerDefeat
	msgbox Route12_Text_Route12HikerAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_PICNICKER, Route12_Text_Route12PicnickerIntro, Route12_Text_Route12PicnickerDefeat
	msgbox Route12_Text_Route12PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_FISHERMAN, Route12_Text_Route12FishermanIntro, Route12_Text_Route12FishermanDefeat
	msgbox Route12_Text_Route12FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route12_Text_Route12BirdKeeperIntro:
	.string "My birds like the hills. Up\nhere the wind is honest.$"

Route12_Text_Route12BirdKeeperDefeat:
	.string "Plucked.$"

Route12_Text_Route12BirdKeeperAfter:
	.string "Honest wind, honest trainer.\nMostly honest.$"

Route12_Text_Route12HikerIntro:
	.string "Hills, finally! I was going\nstir-crazy on the lake.$"

Route12_Text_Route12HikerDefeat:
	.string "Avalanche.$"

Route12_Text_Route12HikerAfter:
	.string "Mind the roots. They trip\neveryone.$"

Route12_Text_Route12PicnickerIntro:
	.string "Wildflowers everywhere. I'm\ndefending them!$"

Route12_Text_Route12PicnickerDefeat:
	.string "Trampled.$"

Route12_Text_Route12PicnickerAfter:
	.string "The hollow ahead is full of\nfairy rings. Don't step in one.$"

Route12_Text_Route12FishermanIntro:
	.string "Even hills have ponds. This\none's mine.$"

Route12_Text_Route12FishermanDefeat:
	.string "Off the line.$"

Route12_Text_Route12FishermanAfter:
	.string "The pond is bottomless, they\nsay. I've dropped a lot in it.$"

@ --- end route trainers ---

Route12_OnTransitionPG:
	call Route12_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route12_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route12_EventScript_PGHide
Route12_EventScript_PGSetupDone:
	return

Route12_EventScript_PGHide:
	setflag FLAG_PG_THUNDURUS
	return

Route12_EventScript_PgThundurus::
	lock
	faceplayer
	playmoncry SPECIES_THUNDURUS, CRY_MODE_ENCOUNTER
	msgbox Route12_Text_PGThundurus, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_THUNDURUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route12_EventScript_PgThundurusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route12_EventScript_PgThundurusStill
	release
	end

Route12_EventScript_PgThundurusStill:
	msgbox Route12_Text_PGStillThundurus, MSGBOX_DEFAULT
	release
	end

Route12_EventScript_PgThundurusDone:
	setflag FLAG_PG_THUNDURUS
	removeobject LOCALID_ROUTE12_PG_THUNDURUS
	release
	end

Route12_Text_PGThundurus:
	.string "THUNDURUS stands before you,\n"
	.string "thunder rolling around it.$"

Route12_Text_PGStillThundurus:
	.string "THUNDURUS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

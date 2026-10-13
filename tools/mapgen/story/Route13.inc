Route13_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route13_OnTransitionPG
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route13_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_BUG_MANIAC, Route13_Text_Route13BugManiacIntro, Route13_Text_Route13BugManiacDefeat
	msgbox Route13_Text_Route13BugManiacAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_CAMPER, Route13_Text_Route13CamperIntro, Route13_Text_Route13CamperDefeat
	msgbox Route13_Text_Route13CamperAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_PICNICKER, Route13_Text_Route13PicnickerIntro, Route13_Text_Route13PicnickerDefeat
	msgbox Route13_Text_Route13PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_BIRD_KEEPER, Route13_Text_Route13BirdKeeperIntro, Route13_Text_Route13BirdKeeperDefeat
	msgbox Route13_Text_Route13BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route13_Text_Route13BugManiacIntro:
	.string "Fireflies lead to the hollow.\nI follow them. And fight.$"

Route13_Text_Route13BugManiacDefeat:
	.string "Lights out.$"

Route13_Text_Route13BugManiacAfter:
	.string "They only glow for the polite.\nBe polite.$"

Route13_Text_Route13CamperIntro:
	.string "Camped here two nights. The\nmoss whispers. Battle me!$"

Route13_Text_Route13CamperDefeat:
	.string "Quiet now.$"

Route13_Text_Route13CamperAfter:
	.string "Don't answer the whispers.\nThat's how they get you.$"

Route13_Text_Route13PicnickerIntro:
	.string "I'm picking flowers for the\nhollow's fairies. Help?$"

Route13_Text_Route13PicnickerDefeat:
	.string "Petals everywhere.$"

Route13_Text_Route13PicnickerAfter:
	.string "A rose for the real one. The\nfalse ones don't take gifts.$"

Route13_Text_Route13BirdKeeperIntro:
	.string "Last stop before the hollow.\nPay the road toll!$"

Route13_Text_Route13BirdKeeperDefeat:
	.string "Toll's paid.$"

Route13_Text_Route13BirdKeeperAfter:
	.string "The hollow's gate is a lane of\nmoss. You'll feel watched.$"

@ --- end route trainers ---

Route13_OnTransitionPG:
	call Route13_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route13_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route13_EventScript_PGHide
Route13_EventScript_PGSetupDone:
	return

Route13_EventScript_PGHide:
	setflag FLAG_PG_ZARUDE
	setflag FLAG_PG_OGERPON
	return

Route13_EventScript_PgZarude::
	lock
	faceplayer
	playmoncry SPECIES_ZARUDE, CRY_MODE_ENCOUNTER
	msgbox Route13_Text_PGZarude, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ZARUDE, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route13_EventScript_PgZarudeDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route13_EventScript_PgZarudeStill
	release
	end

Route13_EventScript_PgZarudeStill:
	msgbox Route13_Text_PGStillZarude, MSGBOX_DEFAULT
	release
	end

Route13_EventScript_PgZarudeDone:
	setflag FLAG_PG_ZARUDE
	removeobject LOCALID_ROUTE13_PG_ZARUDE
	release
	end

Route13_EventScript_PgOgerpon::
	lock
	faceplayer
	playmoncry SPECIES_OGERPON_TEAL, CRY_MODE_ENCOUNTER
	msgbox Route13_Text_PGOgerpon, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_OGERPON_TEAL, 50
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route13_EventScript_PgOgerponDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route13_EventScript_PgOgerponStill
	release
	end

Route13_EventScript_PgOgerponStill:
	msgbox Route13_Text_PGStillOgerpon, MSGBOX_DEFAULT
	release
	end

Route13_EventScript_PgOgerponDone:
	setflag FLAG_PG_OGERPON
	removeobject LOCALID_ROUTE13_PG_OGERPON
	release
	end

Route13_Text_PGZarude:
	.string "ZARUDE stands before you,\n"
	.string "vines swaying like a crowd.$"

Route13_Text_PGStillZarude:
	.string "ZARUDE shakes itself off,\n"
	.string "still standing its ground.$"

Route13_Text_PGOgerpon:
	.string "OGERPON stands before you,\n"
	.string "a mask on its face, dancing.$"

Route13_Text_PGStillOgerpon:
	.string "OGERPON shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

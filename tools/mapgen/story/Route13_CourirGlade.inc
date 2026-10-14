Route13_CourirGlade_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route13_CourirGlade_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/ogerpon_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route13_CourirGlade_OnTransition:
	setflag FLAG_TEMP_1
	call Route13_CourirGlade_EventScript_PGSetup
	end

Route13_CourirGlade_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route13_CourirGlade_Movement_FaceRight
	waitmovement 0
	warp MAP_ORLEANS_ROUTE13, 2, 25
	waitstate
	end

Route13_CourirGlade_Movement_FaceRight:
	face_right
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route13_CourirGlade_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route13_CourirGlade_EventScript_PGHide
Route13_CourirGlade_EventScript_PGSetupDone:
	return

Route13_CourirGlade_EventScript_PGHide:
	setflag FLAG_PG_OGERPON
	return

Route13_CourirGlade_EventScript_PgOgerpon::
	lock
	faceplayer
	playmoncry SPECIES_OGERPON_TEAL, CRY_MODE_ENCOUNTER
	msgbox Route13_CourirGlade_Text_PGOgerpon, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_OGERPON_TEAL, 50
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route13_CourirGlade_EventScript_PgOgerponDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route13_CourirGlade_EventScript_PgOgerponStill
	release
	end

Route13_CourirGlade_EventScript_PgOgerponStill:
	msgbox Route13_CourirGlade_Text_PGStillOgerpon, MSGBOX_DEFAULT
	release
	end

Route13_CourirGlade_EventScript_PgOgerponDone:
	setflag FLAG_PG_OGERPON
	removeobject LOCALID_ROUTE13_COURIR_GLADE_PG_OGERPON
	release
	end

Route13_CourirGlade_Text_PGOgerpon:
	.string "OGERPON stands before you,\n"
	.string "a mask on its face, dancing.$"

Route13_CourirGlade_Text_PGStillOgerpon:
	.string "OGERPON shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

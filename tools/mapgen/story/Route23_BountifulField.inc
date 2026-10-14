Route23_BountifulField_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route23_BountifulField_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/landorus_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route23_BountifulField_OnTransition:
	setflag FLAG_TEMP_1
	call Route23_BountifulField_EventScript_PGSetup
	end

Route23_BountifulField_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_BountifulField_Movement_FaceUp
	waitmovement 0
	warp MAP_ORLEANS_ROUTE23, 27, 37
	waitstate
	end

Route23_BountifulField_Movement_FaceUp:
	face_up
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route23_BountifulField_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route23_BountifulField_EventScript_PGHide
Route23_BountifulField_EventScript_PGSetupDone:
	return

Route23_BountifulField_EventScript_PGHide:
	setflag FLAG_PG_LANDORUS
	return

Route23_BountifulField_EventScript_PgLandorus::
	lock
	faceplayer
	playmoncry SPECIES_LANDORUS, CRY_MODE_ENCOUNTER
	msgbox Route23_BountifulField_Text_PGLandorus, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_LANDORUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_BountifulField_EventScript_PgLandorusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_BountifulField_EventScript_PgLandorusStill
	release
	end

Route23_BountifulField_EventScript_PgLandorusStill:
	msgbox Route23_BountifulField_Text_PGStillLandorus, MSGBOX_DEFAULT
	release
	end

Route23_BountifulField_EventScript_PgLandorusDone:
	setflag FLAG_PG_LANDORUS
	removeobject LOCALID_ROUTE23_BOUNTIFUL_FIELD_PG_LANDORUS
	release
	end

Route23_BountifulField_Text_PGLandorus:
	.string "LANDORUS stands before you,\n"
	.string "the ground trembling under it.$"

Route23_BountifulField_Text_PGStillLandorus:
	.string "LANDORUS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

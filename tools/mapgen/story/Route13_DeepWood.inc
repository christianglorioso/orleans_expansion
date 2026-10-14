Route13_DeepWood_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route13_DeepWood_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/zarude_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route13_DeepWood_OnTransition:
	setflag FLAG_TEMP_1
	call Route13_DeepWood_EventScript_PGSetup
	end

Route13_DeepWood_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route13_DeepWood_Movement_FaceLeft
	waitmovement 0
	warp MAP_ORLEANS_ROUTE13, 26, 26
	waitstate
	end

Route13_DeepWood_Movement_FaceLeft:
	face_left
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route13_DeepWood_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route13_DeepWood_EventScript_PGHide
Route13_DeepWood_EventScript_PGSetupDone:
	return

Route13_DeepWood_EventScript_PGHide:
	setflag FLAG_PG_ZARUDE
	return

Route13_DeepWood_EventScript_PgZarude::
	lock
	faceplayer
	playmoncry SPECIES_ZARUDE, CRY_MODE_ENCOUNTER
	msgbox Route13_DeepWood_Text_PGZarude, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_ZARUDE, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route13_DeepWood_EventScript_PgZarudeDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route13_DeepWood_EventScript_PgZarudeStill
	release
	end

Route13_DeepWood_EventScript_PgZarudeStill:
	msgbox Route13_DeepWood_Text_PGStillZarude, MSGBOX_DEFAULT
	release
	end

Route13_DeepWood_EventScript_PgZarudeDone:
	setflag FLAG_PG_ZARUDE
	removeobject LOCALID_ROUTE13_DEEP_WOOD_PG_ZARUDE
	release
	end

Route13_DeepWood_Text_PGZarude:
	.string "ZARUDE stands before you,\n"
	.string "vines swaying like a crowd.$"

Route13_DeepWood_Text_PGStillZarude:
	.string "ZARUDE shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

Route10_MilneburgPavilion_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route10_MilneburgPavilion_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45 (by Surf)); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/galar_articuno_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route10_MilneburgPavilion_OnTransition:
	setflag FLAG_TEMP_1
	call Route10_MilneburgPavilion_EventScript_PGSetup
	end

Route10_MilneburgPavilion_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route10_MilneburgPavilion_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE10, 30, 13
	waitstate
	end

Route10_MilneburgPavilion_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route10_MilneburgPavilion_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route10_MilneburgPavilion_EventScript_PGHide
Route10_MilneburgPavilion_EventScript_PGSetupDone:
	return

Route10_MilneburgPavilion_EventScript_PGHide:
	setflag FLAG_PG_GALAR_ARTICUNO
	return

Route10_MilneburgPavilion_EventScript_PgGalarArticuno::
	lock
	faceplayer
	playmoncry SPECIES_ARTICUNO_GALAR, CRY_MODE_ENCOUNTER
	msgbox Route10_MilneburgPavilion_Text_PGGalarArticuno, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_ARTICUNO_GALAR, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route10_MilneburgPavilion_EventScript_PgGalarArticunoDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route10_MilneburgPavilion_EventScript_PgGalarArticunoStill
	release
	end

Route10_MilneburgPavilion_EventScript_PgGalarArticunoStill:
	msgbox Route10_MilneburgPavilion_Text_PGStillGalarArticuno, MSGBOX_DEFAULT
	release
	end

Route10_MilneburgPavilion_EventScript_PgGalarArticunoDone:
	setflag FLAG_PG_GALAR_ARTICUNO
	removeobject LOCALID_ROUTE10_MILNEBURG_PAVILION_PG_GALAR_ARTICUNO
	release
	end

Route10_MilneburgPavilion_Text_PGGalarArticuno:
	.string "GALARIAN ARTICUNO stands before you,\n"
	.string "its gaze cold and proud.$"

Route10_MilneburgPavilion_Text_PGStillGalarArticuno:
	.string "GALARIAN ARTICUNO shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

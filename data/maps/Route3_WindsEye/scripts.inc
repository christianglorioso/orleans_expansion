Route3_WindsEye_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route3_WindsEye_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/tornadus_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route3_WindsEye_OnTransition:
	setflag FLAG_TEMP_1
	call Route3_WindsEye_EventScript_PGSetup
	end

Route3_WindsEye_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route3_WindsEye_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE3, 27, 2
	waitstate
	end

Route3_WindsEye_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route3_WindsEye_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route3_WindsEye_EventScript_PGHide
Route3_WindsEye_EventScript_PGSetupDone:
	return

Route3_WindsEye_EventScript_PGHide:
	setflag FLAG_PG_TORNADUS
	return

Route3_WindsEye_EventScript_PgTornadus::
	lock
	faceplayer
	playmoncry SPECIES_TORNADUS, CRY_MODE_ENCOUNTER
	msgbox Route3_WindsEye_Text_PGTornadus, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_TORNADUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route3_WindsEye_EventScript_PgTornadusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route3_WindsEye_EventScript_PgTornadusStill
	release
	end

Route3_WindsEye_EventScript_PgTornadusStill:
	msgbox Route3_WindsEye_Text_PGStillTornadus, MSGBOX_DEFAULT
	release
	end

Route3_WindsEye_EventScript_PgTornadusDone:
	setflag FLAG_PG_TORNADUS
	removeobject LOCALID_ROUTE3_WINDS_EYE_PG_TORNADUS
	release
	end

Route3_WindsEye_Text_PGTornadus:
	.string "TORNADUS stands before you,\n"
	.string "wrapped in a roaring gale.$"

Route3_WindsEye_Text_PGStillTornadus:
	.string "TORNADUS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

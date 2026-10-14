Route12_LeveeCrown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route12_LeveeCrown_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/thundurus_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route12_LeveeCrown_OnTransition:
	setflag FLAG_TEMP_1
	call Route12_LeveeCrown_EventScript_PGSetup
	end

Route12_LeveeCrown_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route12_LeveeCrown_Movement_FaceLeft
	waitmovement 0
	warp MAP_ORLEANS_ROUTE12, 24, 22
	waitstate
	end

Route12_LeveeCrown_Movement_FaceLeft:
	face_left
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route12_LeveeCrown_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route12_LeveeCrown_EventScript_PGHide
Route12_LeveeCrown_EventScript_PGSetupDone:
	return

Route12_LeveeCrown_EventScript_PGHide:
	setflag FLAG_PG_THUNDURUS
	return

Route12_LeveeCrown_EventScript_PgThundurus::
	lock
	faceplayer
	playmoncry SPECIES_THUNDURUS, CRY_MODE_ENCOUNTER
	msgbox Route12_LeveeCrown_Text_PGThundurus, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_THUNDURUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route12_LeveeCrown_EventScript_PgThundurusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route12_LeveeCrown_EventScript_PgThundurusStill
	release
	end

Route12_LeveeCrown_EventScript_PgThundurusStill:
	msgbox Route12_LeveeCrown_Text_PGStillThundurus, MSGBOX_DEFAULT
	release
	end

Route12_LeveeCrown_EventScript_PgThundurusDone:
	setflag FLAG_PG_THUNDURUS
	removeobject LOCALID_ROUTE12_LEVEE_CROWN_PG_THUNDURUS
	release
	end

Route12_LeveeCrown_Text_PGThundurus:
	.string "THUNDURUS stands before you,\n"
	.string "thunder rolling around it.$"

Route12_LeveeCrown_Text_PGStillThundurus:
	.string "THUNDURUS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

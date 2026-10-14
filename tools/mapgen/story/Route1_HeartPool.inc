Route1_HeartPool_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route1_HeartPool_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/mesprit_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route1_HeartPool_OnTransition:
	setflag FLAG_TEMP_1
	call Route1_HeartPool_EventScript_PGSetup
	end

Route1_HeartPool_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route1_HeartPool_Movement_FaceLeft
	waitmovement 0
	warp MAP_ORLEANS_ROUTE1, 26, 27
	waitstate
	end

Route1_HeartPool_Movement_FaceLeft:
	face_left
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route1_HeartPool_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route1_HeartPool_EventScript_PGHide
Route1_HeartPool_EventScript_PGSetupDone:
	return

Route1_HeartPool_EventScript_PGHide:
	setflag FLAG_PG_MESPRIT
	return

Route1_HeartPool_EventScript_PgMesprit::
	lock
	faceplayer
	playmoncry SPECIES_MESPRIT, CRY_MODE_ENCOUNTER
	msgbox Route1_HeartPool_Text_PGMesprit, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_MESPRIT, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route1_HeartPool_EventScript_PgMespritDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route1_HeartPool_EventScript_PgMespritStill
	release
	end

Route1_HeartPool_EventScript_PgMespritStill:
	msgbox Route1_HeartPool_Text_PGStillMesprit, MSGBOX_DEFAULT
	release
	end

Route1_HeartPool_EventScript_PgMespritDone:
	setflag FLAG_PG_MESPRIT
	removeobject LOCALID_ROUTE1_HEART_POOL_PG_MESPRIT
	release
	end

Route1_HeartPool_Text_PGMesprit:
	.string "MESPRIT stands before you,\n"
	.string "its heart glowing soft and warm.$"

Route1_HeartPool_Text_PGStillMesprit:
	.string "MESPRIT shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

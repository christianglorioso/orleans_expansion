Route17_Sugarhouse_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route17_Sugarhouse_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/moltres_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route17_Sugarhouse_OnTransition:
	setflag FLAG_TEMP_1
	call Route17_Sugarhouse_EventScript_PGSetup
	end

Route17_Sugarhouse_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route17_Sugarhouse_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE17, 33, 10
	waitstate
	end

Route17_Sugarhouse_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route17_Sugarhouse_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route17_Sugarhouse_EventScript_PGHide
Route17_Sugarhouse_EventScript_PGSetupDone:
	return

Route17_Sugarhouse_EventScript_PGHide:
	setflag FLAG_PG_MOLTRES
	return

Route17_Sugarhouse_EventScript_PgMoltres::
	lock
	faceplayer
	playmoncry SPECIES_MOLTRES, CRY_MODE_ENCOUNTER
	msgbox Route17_Sugarhouse_Text_PGMoltres, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_MOLTRES, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route17_Sugarhouse_EventScript_PgMoltresDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route17_Sugarhouse_EventScript_PgMoltresStill
	release
	end

Route17_Sugarhouse_EventScript_PgMoltresStill:
	msgbox Route17_Sugarhouse_Text_PGStillMoltres, MSGBOX_DEFAULT
	release
	end

Route17_Sugarhouse_EventScript_PgMoltresDone:
	setflag FLAG_PG_MOLTRES
	removeobject LOCALID_ROUTE17_SUGARHOUSE_PG_MOLTRES
	release
	end

Route17_Sugarhouse_Text_PGMoltres:
	.string "MOLTRES stands before you,\n"
	.string "wings burning like a forge.$"

Route17_Sugarhouse_Text_PGStillMoltres:
	.string "MOLTRES shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

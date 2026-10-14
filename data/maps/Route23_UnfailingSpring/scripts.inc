Route23_UnfailingSpring_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route23_UnfailingSpring_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/azelf_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route23_UnfailingSpring_OnTransition:
	setflag FLAG_TEMP_1
	call Route23_UnfailingSpring_EventScript_PGSetup
	end

Route23_UnfailingSpring_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_UnfailingSpring_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE23, 33, 2
	waitstate
	end

Route23_UnfailingSpring_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route23_UnfailingSpring_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route23_UnfailingSpring_EventScript_PGHide
Route23_UnfailingSpring_EventScript_PGSetupDone:
	return

Route23_UnfailingSpring_EventScript_PGHide:
	setflag FLAG_PG_AZELF
	return

Route23_UnfailingSpring_EventScript_PgAzelf::
	lock
	faceplayer
	playmoncry SPECIES_AZELF, CRY_MODE_ENCOUNTER
	msgbox Route23_UnfailingSpring_Text_PGAzelf, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_AZELF, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_UnfailingSpring_EventScript_PgAzelfDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_UnfailingSpring_EventScript_PgAzelfStill
	release
	end

Route23_UnfailingSpring_EventScript_PgAzelfStill:
	msgbox Route23_UnfailingSpring_Text_PGStillAzelf, MSGBOX_DEFAULT
	release
	end

Route23_UnfailingSpring_EventScript_PgAzelfDone:
	setflag FLAG_PG_AZELF
	removeobject LOCALID_ROUTE23_UNFAILING_SPRING_PG_AZELF
	release
	end

Route23_UnfailingSpring_Text_PGAzelf:
	.string "AZELF stands before you,\n"
	.string "its will gleaming like a blade.$"

Route23_UnfailingSpring_Text_PGStillAzelf:
	.string "AZELF shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

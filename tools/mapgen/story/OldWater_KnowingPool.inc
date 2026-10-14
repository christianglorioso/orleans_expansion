OldWater_KnowingPool_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldWater_KnowingPool_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45 (the Canoe Docks boatman)); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/uxie_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.
@ Uxie's pool is reached by canoe: the Old Water Canoe Docks boatman paddles the player here from story 45; the walk's end at the pirogue is the way out.

OldWater_KnowingPool_OnTransition:
	setflag FLAG_TEMP_1
	call OldWater_KnowingPool_EventScript_PGSetup
	end

OldWater_KnowingPool_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, OldWater_KnowingPool_Movement_FaceUp
	waitmovement 0
	warp MAP_OLD_WATER_CANOE_DOCKS, 4, 6
	waitstate
	end

OldWater_KnowingPool_Movement_FaceUp:
	face_up
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
OldWater_KnowingPool_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, OldWater_KnowingPool_EventScript_PGHide
OldWater_KnowingPool_EventScript_PGSetupDone:
	return

OldWater_KnowingPool_EventScript_PGHide:
	setflag FLAG_PG_UXIE
	return

OldWater_KnowingPool_EventScript_PgUxie::
	lock
	faceplayer
	playmoncry SPECIES_UXIE, CRY_MODE_ENCOUNTER
	msgbox OldWater_KnowingPool_Text_PGUxie, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_UXIE, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, OldWater_KnowingPool_EventScript_PgUxieDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, OldWater_KnowingPool_EventScript_PgUxieStill
	release
	end

OldWater_KnowingPool_EventScript_PgUxieStill:
	msgbox OldWater_KnowingPool_Text_PGStillUxie, MSGBOX_DEFAULT
	release
	end

OldWater_KnowingPool_EventScript_PgUxieDone:
	setflag FLAG_PG_UXIE
	removeobject LOCALID_OLD_WATER_KNOWING_POOL_PG_UXIE
	release
	end

OldWater_KnowingPool_Text_PGUxie:
	.string "UXIE stands before you,\n"
	.string "its eyes shut, knowing everything.$"

OldWater_KnowingPool_Text_PGStillUxie:
	.string "UXIE shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

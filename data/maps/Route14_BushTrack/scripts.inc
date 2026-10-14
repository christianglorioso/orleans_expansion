Route14_BushTrack_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route14_BushTrack_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/galar_zapdos_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route14_BushTrack_OnTransition:
	setflag FLAG_TEMP_1
	call Route14_BushTrack_EventScript_PGSetup
	end

Route14_BushTrack_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route14_BushTrack_Movement_FaceLeft
	waitmovement 0
	warp MAP_ORLEANS_ROUTE14, 25, 19
	waitstate
	end

Route14_BushTrack_Movement_FaceLeft:
	face_left
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route14_BushTrack_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route14_BushTrack_EventScript_PGHide
Route14_BushTrack_EventScript_PGSetupDone:
	return

Route14_BushTrack_EventScript_PGHide:
	setflag FLAG_PG_GALAR_ZAPDOS
	return

Route14_BushTrack_EventScript_PgGalarZapdos::
	lock
	faceplayer
	playmoncry SPECIES_ZAPDOS_GALAR, CRY_MODE_ENCOUNTER
	msgbox Route14_BushTrack_Text_PGGalarZapdos, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_ZAPDOS_GALAR, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route14_BushTrack_EventScript_PgGalarZapdosDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route14_BushTrack_EventScript_PgGalarZapdosStill
	release
	end

Route14_BushTrack_EventScript_PgGalarZapdosStill:
	msgbox Route14_BushTrack_Text_PGStillGalarZapdos, MSGBOX_DEFAULT
	release
	end

Route14_BushTrack_EventScript_PgGalarZapdosDone:
	setflag FLAG_PG_GALAR_ZAPDOS
	removeobject LOCALID_ROUTE14_BUSH_TRACK_PG_GALAR_ZAPDOS
	release
	end

Route14_BushTrack_Text_PGGalarZapdos:
	.string "GALARIAN ZAPDOS stands before you,\n"
	.string "kicking up sparks.$"

Route14_BushTrack_Text_PGStillGalarZapdos:
	.string "GALARIAN ZAPDOS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

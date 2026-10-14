Route14_SpanishFort_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route14_SpanishFort_OnTransition
	.byte 0

@ Legendary lair, batch 2 (story 45); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/galar_moltres_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

Route14_SpanishFort_OnTransition:
	setflag FLAG_TEMP_1
	call Route14_SpanishFort_EventScript_PGSetup
	end

Route14_SpanishFort_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route14_SpanishFort_Movement_FaceRight
	waitmovement 0
	warp MAP_ORLEANS_ROUTE14, 2, 7
	waitstate
	end

Route14_SpanishFort_Movement_FaceRight:
	face_right
	step_end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
Route14_SpanishFort_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route14_SpanishFort_EventScript_PGHide
Route14_SpanishFort_EventScript_PGSetupDone:
	return

Route14_SpanishFort_EventScript_PGHide:
	setflag FLAG_PG_GALAR_MOLTRES
	return

Route14_SpanishFort_EventScript_PgGalarMoltres::
	lock
	faceplayer
	playmoncry SPECIES_MOLTRES_GALAR, CRY_MODE_ENCOUNTER
	msgbox Route14_SpanishFort_Text_PGGalarMoltres, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_MOLTRES_GALAR, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route14_SpanishFort_EventScript_PgGalarMoltresDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route14_SpanishFort_EventScript_PgGalarMoltresStill
	release
	end

Route14_SpanishFort_EventScript_PgGalarMoltresStill:
	msgbox Route14_SpanishFort_Text_PGStillGalarMoltres, MSGBOX_DEFAULT
	release
	end

Route14_SpanishFort_EventScript_PgGalarMoltresDone:
	setflag FLAG_PG_GALAR_MOLTRES
	removeobject LOCALID_ROUTE14_SPANISH_FORT_PG_GALAR_MOLTRES
	release
	end

Route14_SpanishFort_Text_PGGalarMoltres:
	.string "GALARIAN MOLTRES stands before you,\n"
	.string "flames dark as a bruise.$"

Route14_SpanishFort_Text_PGStillGalarMoltres:
	.string "GALARIAN MOLTRES shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

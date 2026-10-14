Route11_SuicuneIsle_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route11_SuicuneIsle_OnTransition
	.byte 0

@ Suicune's hidden island (Route 11, through the stone arch on the island in the big lake; Surf to reach it).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way in is the route's coord trigger (Route11_EventScript_LairEnter), the way
@ out is the gap in the south wall: the exit triggers (10..11, 14) put the player back on the route's entrance cell. The legendary is the old route
@ static (FLAG_PG_*, hidden below story 45, retired only on a catch, rolled when it is talked to).
Route11_SuicuneIsle_OnTransition:
	setflag FLAG_TEMP_1
	call Route11_SuicuneIsle_EventScript_PGSetup
	end

Route11_SuicuneIsle_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route11_SuicuneIsle_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE11, 28, 22
	waitstate
	end

Route11_SuicuneIsle_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the legendary lairs were built) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route11_SuicuneIsle_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route11_SuicuneIsle_EventScript_PGHide
Route11_SuicuneIsle_EventScript_PGSetupDone:
	return

Route11_SuicuneIsle_EventScript_PGHide:
	setflag FLAG_PG_SUICUNE
	return

Route11_SuicuneIsle_EventScript_PgSuicune::
	lock
	faceplayer
	playmoncry SPECIES_SUICUNE, CRY_MODE_ENCOUNTER
	msgbox Route11_SuicuneIsle_Text_PGSuicune, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_SUICUNE, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route11_SuicuneIsle_EventScript_PgSuicuneDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route11_SuicuneIsle_EventScript_PgSuicuneStill
	release
	end

Route11_SuicuneIsle_EventScript_PgSuicuneStill:
	msgbox Route11_SuicuneIsle_Text_PGStillSuicune, MSGBOX_DEFAULT
	release
	end

Route11_SuicuneIsle_EventScript_PgSuicuneDone:
	setflag FLAG_PG_SUICUNE
	removeobject LOCALID_ROUTE11_SUICUNE_ISLE_PG_SUICUNE
	release
	end

Route11_SuicuneIsle_Text_PGSuicune:
	.string "SUICUNE stands before you,\n"
	.string "the water around it perfectly still.$"

Route11_SuicuneIsle_Text_PGStillSuicune:
	.string "SUICUNE shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

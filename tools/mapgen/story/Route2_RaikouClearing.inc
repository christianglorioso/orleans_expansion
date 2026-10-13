Route2_RaikouClearing_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route2_RaikouClearing_OnTransition
	.byte 0

@ Raikou's struck clearing (Route 2, off the notch in the north canopy above the transmission towers).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way in is the route's coord trigger (Route2_EventScript_LairEnter), the way
@ out is the gap in the south wall: the exit triggers (10..11, 14) put the player back on the route's entrance cell. The legendary is the old route
@ static (FLAG_PG_*, hidden below story 45, retired only on a catch, rolled when it is talked to).
Route2_RaikouClearing_OnTransition:
	setflag FLAG_TEMP_1
	call Route2_RaikouClearing_EventScript_PGSetup
	end

Route2_RaikouClearing_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route2_RaikouClearing_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE2, 24, 1
	waitstate
	end

Route2_RaikouClearing_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the legendary lairs were built) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route2_RaikouClearing_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route2_RaikouClearing_EventScript_PGHide
Route2_RaikouClearing_EventScript_PGSetupDone:
	return

Route2_RaikouClearing_EventScript_PGHide:
	setflag FLAG_PG_RAIKOU
	return

Route2_RaikouClearing_EventScript_PgRaikou::
	lock
	faceplayer
	playmoncry SPECIES_RAIKOU, CRY_MODE_ENCOUNTER
	msgbox Route2_RaikouClearing_Text_PGRaikou, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_RAIKOU, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route2_RaikouClearing_EventScript_PgRaikouDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route2_RaikouClearing_EventScript_PgRaikouStill
	release
	end

Route2_RaikouClearing_EventScript_PgRaikouStill:
	msgbox Route2_RaikouClearing_Text_PGStillRaikou, MSGBOX_DEFAULT
	release
	end

Route2_RaikouClearing_EventScript_PgRaikouDone:
	setflag FLAG_PG_RAIKOU
	removeobject LOCALID_ROUTE2_RAIKOU_CLEARING_PG_RAIKOU
	release
	end

Route2_RaikouClearing_Text_PGRaikou:
	.string "RAIKOU stands before you,\n"
	.string "its hide crackling with static.$"

Route2_RaikouClearing_Text_PGStillRaikou:
	.string "RAIKOU shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

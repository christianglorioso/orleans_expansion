Route16_EnteiField_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route16_EnteiField_OnTransition
	.byte 0

@ Entei's burned pepper field (Route 16, through the cleft in the north scrub above the pepper fields).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way in is the route's coord trigger (Route16_EventScript_LairEnter), the way
@ out is the gap in the south wall: the exit triggers (10..11, 14) put the player back on the route's entrance cell. The legendary is the old route
@ static (FLAG_PG_*, hidden below story 45, retired only on a catch, rolled when it is talked to).
Route16_EnteiField_OnTransition:
	setflag FLAG_TEMP_1
	call Route16_EnteiField_EventScript_PGSetup
	end

Route16_EnteiField_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route16_EnteiField_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE16, 15, 2
	waitstate
	end

Route16_EnteiField_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the legendary lairs were built) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route16_EnteiField_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route16_EnteiField_EventScript_PGHide
Route16_EnteiField_EventScript_PGSetupDone:
	return

Route16_EnteiField_EventScript_PGHide:
	setflag FLAG_PG_ENTEI
	return

Route16_EnteiField_EventScript_PgEntei::
	lock
	faceplayer
	playmoncry SPECIES_ENTEI, CRY_MODE_ENCOUNTER
	msgbox Route16_EnteiField_Text_PGEntei, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ENTEI, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route16_EnteiField_EventScript_PgEnteiDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route16_EnteiField_EventScript_PgEnteiStill
	release
	end

Route16_EnteiField_EventScript_PgEnteiStill:
	msgbox Route16_EnteiField_Text_PGStillEntei, MSGBOX_DEFAULT
	release
	end

Route16_EnteiField_EventScript_PgEnteiDone:
	setflag FLAG_PG_ENTEI
	removeobject LOCALID_ROUTE16_ENTEI_FIELD_PG_ENTEI
	release
	end

Route16_EnteiField_Text_PGEntei:
	.string "ENTEI stands before you,\n"
	.string "heat rolling off its mane.$"

Route16_EnteiField_Text_PGStillEntei:
	.string "ENTEI shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

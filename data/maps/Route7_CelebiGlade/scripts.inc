Route7_CelebiGlade_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route7_CelebiGlade_OnTransition
	.byte 0

@ Celebi's Rootkin shrine glade (Route 7, through the stone arch in the north canopy).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way in is the route's coord trigger (Route7_EventScript_LairEnter), the way
@ out is the gap in the south wall: the exit triggers (10..11, 14) put the player back on the route's entrance cell. The legendary is the old route
@ static (FLAG_PG_*, hidden below story 45, retired only on a catch, rolled when it is talked to).
Route7_CelebiGlade_OnTransition:
	setflag FLAG_TEMP_1
	call Route7_CelebiGlade_EventScript_PGSetup
	end

Route7_CelebiGlade_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route7_CelebiGlade_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE7, 34, 3
	waitstate
	end

Route7_CelebiGlade_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the legendary lairs were built) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route7_CelebiGlade_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route7_CelebiGlade_EventScript_PGHide
Route7_CelebiGlade_EventScript_PGSetupDone:
	return

Route7_CelebiGlade_EventScript_PGHide:
	setflag FLAG_PG_CELEBI
	return

Route7_CelebiGlade_EventScript_PgCelebi::
	lock
	faceplayer
	playmoncry SPECIES_CELEBI, CRY_MODE_ENCOUNTER
	msgbox Route7_CelebiGlade_Text_PGCelebi, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_CELEBI, 50
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route7_CelebiGlade_EventScript_PgCelebiDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route7_CelebiGlade_EventScript_PgCelebiStill
	release
	end

Route7_CelebiGlade_EventScript_PgCelebiStill:
	msgbox Route7_CelebiGlade_Text_PGStillCelebi, MSGBOX_DEFAULT
	release
	end

Route7_CelebiGlade_EventScript_PgCelebiDone:
	setflag FLAG_PG_CELEBI
	removeobject LOCALID_ROUTE7_CELEBI_GLADE_PG_CELEBI
	release
	end

Route7_CelebiGlade_Text_PGCelebi:
	.string "CELEBI stands before you,\n"
	.string "the air shimmering with time.$"

Route7_CelebiGlade_Text_PGStillCelebi:
	.string "CELEBI shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

@ --- mapgen: generated NPC scripts (end) ---

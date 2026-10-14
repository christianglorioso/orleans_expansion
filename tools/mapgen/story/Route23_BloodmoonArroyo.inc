Route23_BloodmoonArroyo_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route23_BloodmoonArroyo_OnTransition
	.byte 0

@ Bloodmoon Ursaluna's arroyo den (Route 23, through the cleft in the north scrub; open from story 45).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way out is the gap in the south wall: the exit triggers (10..11, 14) put the
@ player back in the cleft. Ursaluna is the old route static (FLAG_PG_URSALUNA_BM, hidden below story 45) and NIGHT ONLY: it is shown on load at night
@ until it is caught (FLAG_PG_URSALUNA_DONE; a win leaves it); talking to it by day only sends it back into the brush.
Route23_BloodmoonArroyo_OnTransition:
	setflag FLAG_TEMP_1
	setflag FLAG_PG_URSALUNA_BM
	goto_if_lt VAR_ORLEANS_STORY, 45, Route23_BloodmoonArroyo_EventScript_PGSetupDone
	call Route23_BloodmoonArroyo_EventScript_PGNightUrsalunaBm
Route23_BloodmoonArroyo_EventScript_PGSetupDone:
	end

Route23_BloodmoonArroyo_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_BloodmoonArroyo_Movement_FaceDown
	waitmovement 0
	warp MAP_ORLEANS_ROUTE23, 22, 2
	waitstate
	end

Route23_BloodmoonArroyo_Movement_FaceDown:
	face_down
	step_end

@ --- post-game (moved here from the route when the legendary lairs were built) ---

Route23_BloodmoonArroyo_EventScript_PgUrsalunaBm::
	lock
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmNight
	msgbox Route23_BloodmoonArroyo_Text_PGDayUrsalunaBm, MSGBOX_DEFAULT
	setflag FLAG_PG_URSALUNA_BM
	removeobject LOCALID_ROUTE23_BLOODMOON_ARROYO_PG_URSALUNA_BM
	release
	end

Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmNight:
	faceplayer
	playmoncry SPECIES_URSALUNA_BLOODMOON, CRY_MODE_ENCOUNTER
	msgbox Route23_BloodmoonArroyo_Text_PGUrsalunaBm, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_URSALUNA_BLOODMOON, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmStill
	release
	end

Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmStill:
	msgbox Route23_BloodmoonArroyo_Text_PGStillUrsalunaBm, MSGBOX_DEFAULT
	release
	end

Route23_BloodmoonArroyo_EventScript_PgUrsalunaBmDone:
	setflag FLAG_PG_URSALUNA_BM
	setflag FLAG_PG_URSALUNA_DONE
	removeobject LOCALID_ROUTE23_BLOODMOON_ARROYO_PG_URSALUNA_BM
	release
	end

Route23_BloodmoonArroyo_EventScript_PGNightUrsalunaBm:
	goto_if_set FLAG_PG_URSALUNA_DONE, Route23_BloodmoonArroyo_EventScript_PGNightHideUrsalunaBm
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, FALSE, Route23_BloodmoonArroyo_EventScript_PGNightHideUrsalunaBm
	clearflag FLAG_PG_URSALUNA_BM
	return

Route23_BloodmoonArroyo_EventScript_PGNightHideUrsalunaBm:
	setflag FLAG_PG_URSALUNA_BM
	return

Route23_BloodmoonArroyo_Text_PGUrsalunaBm:
	.string "URSALUNA stands before you,\n"
	.string "a red moon in its eyes.$"

Route23_BloodmoonArroyo_Text_PGStillUrsalunaBm:
	.string "URSALUNA shakes itself off,\n"
	.string "still standing its ground.$"

Route23_BloodmoonArroyo_Text_PGDayUrsalunaBm:
	.string "URSALUNA dislikes the daylight and\n"
	.string "slips back into the brush.$"

@ --- end post-game ---

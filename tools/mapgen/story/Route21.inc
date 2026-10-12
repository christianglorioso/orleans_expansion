Route21_MapScripts::
	.byte 0

@ Chapter 8 gate: Heron's verse (gym 8, FLAG_BADGE08_GET) clears the wreck and the wall of rain (Route 21, row 8).
Route21_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_BADGE08_GET, Route21_EventScript_WaterGateOpen
	msgbox Route21_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route21_Movement_TurnBack
	waitmovement 0
Route21_EventScript_WaterGateOpen:
	releaseall
	end

Route21_Movement_TurnBack:
	walk_up
	step_end

Route21_Text_WaterGate:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.\p"
	.string "The old songs say the last verse\nbrings the rain its own end.$"


Route18_MapScripts::
	.byte 0

@ Chapter 8 gate: Cayenne's verse (gym 7, FLAG_BADGE07_GET) clears the fallen span across Route 18 (x 38).
Route18_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_BADGE07_GET, Route18_EventScript_WaterGateOpen
	msgbox Route18_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route18_Movement_TurnBack
	waitmovement 0
Route18_EventScript_WaterGateOpen:
	releaseall
	end

Route18_Movement_TurnBack:
	walk_left
	step_end

Route18_Text_WaterGate:
	.string "A fallen span lies across the\nchannel, its arches black with fire.\p"
	.string "Nothing passes. The old songs say\nthe burned field greens again.$"


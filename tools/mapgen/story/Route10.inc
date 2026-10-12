Route10_MapScripts::
	.byte 0

@ Chapter 5+ gate: the brothers' verse (gym 5, FLAG_BADGE05_GET) clears the log jam across Route 10's canal (x 11). A cut of
@ flag triggers (story_data_gates.py) turns walkers and surfers back; story_gates_check.py proves it world-wide.
Route10_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_BADGE05_GET, Route10_EventScript_WaterGateOpen
	msgbox Route10_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route10_Movement_TurnBack
	waitmovement 0
Route10_EventScript_WaterGateOpen:
	releaseall
	end

Route10_Movement_TurnBack:
	walk_left
	step_end

Route10_Text_WaterGate:
	.string "A jam of logs and rafts chokes\nthe canal. Nothing floats through.\p"
	.string "The lake beyond has to wait. The\nold songs say the table is shared.$"


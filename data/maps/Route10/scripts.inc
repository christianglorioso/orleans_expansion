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

@ --- mapgen: generated NPC scripts (begin) ---

Route10_EventScript_Trainer0::
	msgbox Route10_Text_Trainer0, MSGBOX_NPC
	end

Route10_Text_Trainer0:
	.string "(Trainer: first-pass placeholder.)$"

Route10_EventScript_Trainer2::
	msgbox Route10_Text_Trainer2, MSGBOX_NPC
	end

Route10_Text_Trainer2:
	.string "(Trainer: first-pass placeholder.)$"

Route10_EventScript_Trainer3::
	msgbox Route10_Text_Trainer3, MSGBOX_NPC
	end

Route10_Text_Trainer3:
	.string "(Trainer: first-pass placeholder.)$"

Route10_EventScript_Trainer6::
	msgbox Route10_Text_Trainer6, MSGBOX_NPC
	end

Route10_Text_Trainer6:
	.string "(Trainer: first-pass placeholder.)$"

Route10_EventScript_Jam1::
	msgbox Route10_Text_Jam1, MSGBOX_NPC
	end

Route10_Text_Jam1:
	.string "A jam of logs and rafts fills\nthe canal. Nothing floats through.$"

Route10_EventScript_Jam2::
	msgbox Route10_Text_Jam2, MSGBOX_NPC
	end

Route10_Text_Jam2:
	.string "A jam of logs and rafts fills\nthe canal. Nothing floats through.$"

Route10_EventScript_Jam3::
	msgbox Route10_Text_Jam3, MSGBOX_NPC
	end

Route10_Text_Jam3:
	.string "A jam of logs and rafts fills\nthe canal. Nothing floats through.$"

Route10_EventScript_Jam4::
	msgbox Route10_Text_Jam4, MSGBOX_NPC
	end

Route10_Text_Jam4:
	.string "A jam of logs and rafts fills\nthe canal. Nothing floats through.$"

Route10_EventScript_RouteSign1::
	msgbox Route10_Text_RouteSign1, MSGBOX_SIGN
	end

Route10_Text_RouteSign1:
	.string "CRESCENT CITY LAKEFRONT\nBoats for the big lake leave here.$"

@ --- mapgen: generated NPC scripts (end) ---

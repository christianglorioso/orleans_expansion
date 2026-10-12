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

@ --- mapgen: generated NPC scripts (begin) ---

Route18_EventScript_Trainer1::
	msgbox Route18_Text_Trainer1, MSGBOX_NPC
	end

Route18_Text_Trainer1:
	.string "(Trainer: first-pass placeholder.)$"

Route18_EventScript_Trainer2::
	msgbox Route18_Text_Trainer2, MSGBOX_NPC
	end

Route18_Text_Trainer2:
	.string "(Trainer: first-pass placeholder.)$"

Route18_EventScript_Trainer3::
	msgbox Route18_Text_Trainer3, MSGBOX_NPC
	end

Route18_Text_Trainer3:
	.string "(Trainer: first-pass placeholder.)$"

Route18_EventScript_Trainer7::
	msgbox Route18_Text_Trainer7, MSGBOX_NPC
	end

Route18_Text_Trainer7:
	.string "(Trainer: first-pass placeholder.)$"

Route18_EventScript_Span1::
	msgbox Route18_Text_Span1, MSGBOX_NPC
	end

Route18_Text_Span1:
	.string "A fallen span lies across the\nchannel, black with old fire.$"

Route18_EventScript_Span2::
	msgbox Route18_Text_Span2, MSGBOX_NPC
	end

Route18_Text_Span2:
	.string "A fallen span lies across the\nchannel, black with old fire.$"

Route18_EventScript_Span3::
	msgbox Route18_Text_Span3, MSGBOX_NPC
	end

Route18_Text_Span3:
	.string "A fallen span lies across the\nchannel, black with old fire.$"

Route18_EventScript_Span4::
	msgbox Route18_Text_Span4, MSGBOX_NPC
	end

Route18_Text_Span4:
	.string "A fallen span lies across the\nchannel, black with old fire.$"

@ --- mapgen: generated NPC scripts (end) ---

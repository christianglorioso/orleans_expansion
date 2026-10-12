Route25_MapScripts::
	.byte 0

@ Finale gate: the channel to the Oldest Shrine (Route 25, row 20) stays shut until BOTH raids are done; the finale script
@ sets FLAG_ROUTE25_OPEN when FLAG_KYOGRE_CALMED and FLAG_GROUDON_CALMED are both set.
Route25_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_ROUTE25_OPEN, Route25_EventScript_WaterGateOpen
	msgbox Route25_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route25_Movement_TurnBack
	waitmovement 0
Route25_EventScript_WaterGateOpen:
	releaseall
	end

Route25_Movement_TurnBack:
	walk_down
	step_end

Route25_Text_WaterGate:
	.string "The channel ahead boils under a wall\nof storm. Nothing can cross it.\p"
	.string "Not until the two great ones are\ncalmed.$"

@ --- mapgen: generated NPC scripts (begin) ---

Route25_EventScript_Trainer1::
	msgbox Route25_Text_Trainer1, MSGBOX_NPC
	end

Route25_Text_Trainer1:
	.string "(Trainer: first-pass placeholder.)$"

Route25_EventScript_Trainer2::
	msgbox Route25_Text_Trainer2, MSGBOX_NPC
	end

Route25_Text_Trainer2:
	.string "(Trainer: first-pass placeholder.)$"

Route25_EventScript_Trainer4::
	msgbox Route25_Text_Trainer4, MSGBOX_NPC
	end

Route25_Text_Trainer4:
	.string "(Trainer: first-pass placeholder.)$"

Route25_EventScript_Trainer6::
	msgbox Route25_Text_Trainer6, MSGBOX_NPC
	end

Route25_Text_Trainer6:
	.string "(Trainer: first-pass placeholder.)$"

Route25_EventScript_Jam1::
	msgbox Route25_Text_Jam1, MSGBOX_NPC
	end

Route25_Text_Jam1:
	.string "The channel boils under a wall of\nstorm. Nothing can cross it.$"

Route25_EventScript_Jam2::
	msgbox Route25_Text_Jam2, MSGBOX_NPC
	end

Route25_Text_Jam2:
	.string "The channel boils under a wall of\nstorm. Nothing can cross it.$"

Route25_EventScript_Jam3::
	msgbox Route25_Text_Jam3, MSGBOX_NPC
	end

Route25_Text_Jam3:
	.string "The channel boils under a wall of\nstorm. Nothing can cross it.$"

Route25_EventScript_Jam4::
	msgbox Route25_Text_Jam4, MSGBOX_NPC
	end

Route25_Text_Jam4:
	.string "The channel boils under a wall of\nstorm. Nothing can cross it.$"

Route25_EventScript_RouteSign1::
	msgbox Route25_Text_RouteSign1, MSGBOX_SIGN
	end

Route25_Text_RouteSign1:
	.string "THE OLDEST SHRINE\nThe heart of the basin lies north.$"

@ --- mapgen: generated NPC scripts (end) ---

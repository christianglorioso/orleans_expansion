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

@ --- mapgen: generated NPC scripts (begin) ---

Route21_EventScript_Trainer0::
	msgbox Route21_Text_Trainer0, MSGBOX_NPC
	end

Route21_Text_Trainer0:
	.string "(Trainer: first-pass placeholder.)$"

Route21_EventScript_Trainer4::
	msgbox Route21_Text_Trainer4, MSGBOX_NPC
	end

Route21_Text_Trainer4:
	.string "(Trainer: first-pass placeholder.)$"

Route21_EventScript_Trainer5::
	msgbox Route21_Text_Trainer5, MSGBOX_NPC
	end

Route21_Text_Trainer5:
	.string "(Trainer: first-pass placeholder.)$"

Route21_EventScript_Trainer6::
	msgbox Route21_Text_Trainer6, MSGBOX_NPC
	end

Route21_Text_Trainer6:
	.string "(Trainer: first-pass placeholder.)$"

Route21_EventScript_Debris1::
	msgbox Route21_Text_Debris1, MSGBOX_NPC
	end

Route21_Text_Debris1:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

Route21_EventScript_Debris2::
	msgbox Route21_Text_Debris2, MSGBOX_NPC
	end

Route21_Text_Debris2:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

Route21_EventScript_Debris3::
	msgbox Route21_Text_Debris3, MSGBOX_NPC
	end

Route21_Text_Debris3:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

Route21_EventScript_Debris4::
	msgbox Route21_Text_Debris4, MSGBOX_NPC
	end

Route21_Text_Debris4:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

Route21_EventScript_Debris5::
	msgbox Route21_Text_Debris5, MSGBOX_NPC
	end

Route21_Text_Debris5:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

Route21_EventScript_Debris6::
	msgbox Route21_Text_Debris6, MSGBOX_NPC
	end

Route21_Text_Debris6:
	.string "A wrecked barge and a wall of rain\nblock the way into the Gulf.$"

@ --- mapgen: generated NPC scripts (end) ---

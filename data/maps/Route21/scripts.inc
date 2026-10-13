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

@ --- route trainers (gen_route_trainers.py) ---
Route21_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE21_SWIMMER, Route21_Text_Route21SwimmerIntro, Route21_Text_Route21SwimmerDefeat
	msgbox Route21_Text_Route21SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route21_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE21_SWIMMER_F, Route21_Text_Route21SwimmerFIntro, Route21_Text_Route21SwimmerFDefeat
	msgbox Route21_Text_Route21SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route21_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE21_SWIMMER_2, Route21_Text_Route21Swimmer2Intro, Route21_Text_Route21Swimmer2Defeat
	msgbox Route21_Text_Route21Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route21_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE21_SWIMMER_3, Route21_Text_Route21Swimmer3Intro, Route21_Text_Route21Swimmer3Defeat
	msgbox Route21_Text_Route21Swimmer3After, MSGBOX_AUTOCLOSE
	end

Route21_Text_Route21SwimmerIntro:
	.string "The barge is gone, the Gulf is\nopen. Out here it's deep.$"

Route21_Text_Route21SwimmerDefeat:
	.string "Too deep.$"

Route21_Text_Route21SwimmerAfter:
	.string "The rain stopped the day the\nlast verse was sung.$"

Route21_Text_Route21SwimmerFIntro:
	.string "Out past the delta the swells\nget long. Fight on them!$"

Route21_Text_Route21SwimmerFDefeat:
	.string "Swamped.$"

Route21_Text_Route21SwimmerFAfter:
	.string "The Gulf glows at night, down\nsouth. Don't look too long.$"

Route21_Text_Route21Swimmer2Intro:
	.string "Everyone wants the temple.\nFew can reach it.$"

Route21_Text_Route21Swimmer2Defeat:
	.string "Not today.$"

Route21_Text_Route21Swimmer2After:
	.string "The temple door is on ROUTE 22.\nFace it from the water.$"

Route21_Text_Route21Swimmer3Intro:
	.string "Another traveler. The Gulf is\nbusy this year.$"

Route21_Text_Route21Swimmer3Defeat:
	.string "Crabbed.$"

Route21_Text_Route21Swimmer3After:
	.string "Route 22 is the last water\nbefore the temple.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

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

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

@ --- route trainers (gen_route_trainers.py) ---
Route10_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE10_SWIMMER, Route10_Text_Route10SwimmerIntro, Route10_Text_Route10SwimmerDefeat
	msgbox Route10_Text_Route10SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE10_SWIMMER_F, Route10_Text_Route10SwimmerFIntro, Route10_Text_Route10SwimmerFDefeat
	msgbox Route10_Text_Route10SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE10_SWIMMER_2, Route10_Text_Route10Swimmer2Intro, Route10_Text_Route10Swimmer2Defeat
	msgbox Route10_Text_Route10Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route10_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE10_CAMPER, Route10_Text_Route10CamperIntro, Route10_Text_Route10CamperDefeat
	msgbox Route10_Text_Route10CamperAfter, MSGBOX_AUTOCLOSE
	end

Route10_Text_Route10SwimmerIntro:
	.string "The lake road's open again! I\nswim it just to say I can.$"

Route10_Text_Route10SwimmerDefeat:
	.string "Dunked.$"

Route10_Text_Route10SwimmerAfter:
	.string "The brothers' gumbo smell carries\nall the way to the canal.$"

Route10_Text_Route10SwimmerFIntro:
	.string "Big Lake is bigger than it looks.\nDon't drown. Battle!$"

Route10_Text_Route10SwimmerFDefeat:
	.string "Bubbles.$"

Route10_Text_Route10SwimmerFAfter:
	.string "Past the jam, the lake is clear.\nMostly.$"

Route10_Text_Route10Swimmer2Intro:
	.string "Nobody swims here uninvited.\nExcept you. Fine!$"

Route10_Text_Route10Swimmer2Defeat:
	.string "Swept away.$"

Route10_Text_Route10Swimmer2After:
	.string "The current's strongest at the\nnarrows. Hold on.$"

Route10_Text_Route10CamperIntro:
	.string "The shore road is mine. I\npitched a tent on it!$"

Route10_Text_Route10CamperDefeat:
	.string "Tent's down.$"

Route10_Text_Route10CamperAfter:
	.string "A shrine hides in the meadow\nnorth of here, they say.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

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

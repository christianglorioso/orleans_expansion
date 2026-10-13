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

@ --- route trainers (gen_route_trainers.py) ---
Route18_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE18_SWIMMER, Route18_Text_Route18SwimmerIntro, Route18_Text_Route18SwimmerDefeat
	msgbox Route18_Text_Route18SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE18_SWIMMER_F, Route18_Text_Route18SwimmerFIntro, Route18_Text_Route18SwimmerFDefeat
	msgbox Route18_Text_Route18SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE18_SWIMMER_2, Route18_Text_Route18Swimmer2Intro, Route18_Text_Route18Swimmer2Defeat
	msgbox Route18_Text_Route18Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route18_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE18_SWIMMER_3, Route18_Text_Route18Swimmer3Intro, Route18_Text_Route18Swimmer3Defeat
	msgbox Route18_Text_Route18Swimmer3After, MSGBOX_AUTOCLOSE
	end

Route18_Text_Route18SwimmerIntro:
	.string "The span fell and the delta opened.\nI swim where it used to be!$"

Route18_Text_Route18SwimmerDefeat:
	.string "Swept under.$"

Route18_Text_Route18SwimmerAfter:
	.string "The black arches are warm in the\nafternoon. Old fire, still there.$"

Route18_Text_Route18SwimmerFIntro:
	.string "Cayenne's verse took the span\ndown. Now the water's mine!$"

Route18_Text_Route18SwimmerFDefeat:
	.string "Washed out.$"

Route18_Text_Route18SwimmerFAfter:
	.string "East of here the delta fans out.\nTake your time. It's wide.$"

Route18_Text_Route18Swimmer2Intro:
	.string "Fresh water meets salt out here.\nIt makes everyone nervous.$"

Route18_Text_Route18Swimmer2Defeat:
	.string "Nerves.$"

Route18_Text_Route18Swimmer2After:
	.string "The current flips at noon.\nDon't fight it.$"

Route18_Text_Route18Swimmer3Intro:
	.string "I race the ferries to Land's\nEnd. Win or lose, I'm early.$"

Route18_Text_Route18Swimmer3Defeat:
	.string "Beaten to the dock.$"

Route18_Text_Route18Swimmer3After:
	.string "Land's End sits on pilings. The\nwhole town floats a little.$"

@ --- end route trainers ---

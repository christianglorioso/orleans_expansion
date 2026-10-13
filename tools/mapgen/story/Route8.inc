Route8_MapScripts::
	.byte 0

@ The finale gate (story_data_gates.py): Route 8's row 1, the seam to Route 25. Flag triggers turn walkers and surfers back until BOTH
@ raids are done (the finale script sets FLAG_ROUTE25_OPEN once FLAG_KYOGRE_CALMED and FLAG_GROUDON_CALMED are set).
Route8_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_ROUTE25_OPEN, Route8_EventScript_WaterGateOpen
	msgbox Route8_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route8_Movement_TurnBack
	waitmovement 0
Route8_EventScript_WaterGateOpen:
	releaseall
	end

Route8_Movement_TurnBack:
	walk_down
	step_end

Route8_Text_WaterGate:
	.string "The channel north boils under a wall\n"
	.string "of storm. Nothing can cross it.\p"
	.string "Not yet.$"

@ --- route trainers (gen_route_trainers.py) ---
Route8_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE8_HIKER, Route8_Text_Route8HikerIntro, Route8_Text_Route8HikerDefeat
	msgbox Route8_Text_Route8HikerAfter, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE8_SWIMMER, Route8_Text_Route8SwimmerIntro, Route8_Text_Route8SwimmerDefeat
	msgbox Route8_Text_Route8SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE8_SWIMMER_F, Route8_Text_Route8SwimmerFIntro, Route8_Text_Route8SwimmerFDefeat
	msgbox Route8_Text_Route8SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE8_FISHERMAN, Route8_Text_Route8FishermanIntro, Route8_Text_Route8FishermanDefeat
	msgbox Route8_Text_Route8FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route8_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE8_CAMPER, Route8_Text_Route8CamperIntro, Route8_Text_Route8CamperDefeat
	msgbox Route8_Text_Route8CamperAfter, MSGBOX_AUTOCLOSE
	end

Route8_Text_Route8HikerIntro:
	.string "No mountains here, so I hike\nthe dikes. Stone's stone!$"

Route8_Text_Route8HikerDefeat:
	.string "Cracked.$"

Route8_Text_Route8HikerAfter:
	.string "The channel north of here is shut.\nStorm wall. Nobody sails it.$"

Route8_Text_Route8SwimmerIntro:
	.string "Deep water, deep trouble. In\nyou go!$"

Route8_Text_Route8SwimmerDefeat:
	.string "Blub.$"

Route8_Text_Route8SwimmerAfter:
	.string "Sharpedo hunt the reed edge.\nStay out of the shallows.$"

Route8_Text_Route8SwimmerFIntro:
	.string "A fellow swimmer! No, a trainer.\nEven better!$"

Route8_Text_Route8SwimmerFDefeat:
	.string "Soaked, in every way.$"

Route8_Text_Route8SwimmerFAfter:
	.string "The camp is west. The brothers\ncook on a boat of a stove.$"

Route8_Text_Route8FishermanIntro:
	.string "The tide's out on my fishing\nhole. The mood's out too.$"

Route8_Text_Route8FishermanDefeat:
	.string "Hooked.$"

Route8_Text_Route8FishermanAfter:
	.string "Barbaracle grip the rocks. They\nnever let go.$"

Route8_Text_Route8CamperIntro:
	.string "I dig where I camp. Nobody\ntells me otherwise!$"

Route8_Text_Route8CamperDefeat:
	.string "Dug my own hole.$"

Route8_Text_Route8CamperAfter:
	.string "Something hums in the north\nchannel. Don't go yet.$"

@ --- end route trainers ---

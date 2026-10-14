Route6_MapScripts::
	.byte 0

@ Route 6's south shore path (the only land way from Crescent City to Routes 6-9) narrows to two cells at x 29; both hold a jam of
@ storm debris (objects hidden by FLAG_ROUTE6_DEBRIS_CLEARED, story_overlay.py). Decision 3: each Singer's verse clears a water obstacle, so
@ the fourth verse (Kingfisher's), sung back at the Old Water (the midpoint visit, OldWater_SongHouse.inc), clears it: that sets
@ FLAG_ROUTE6_DEBRIS_CLEARED. Debris1 and Debris2 are the same obstacle.
Route6_EventScript_Debris1::
Route6_EventScript_Debris2::
	lock
	goto_if_ge VAR_ORLEANS_STORY, 21, Route6_EventScript_DebrisVerse
	msgbox Route6_Text_Debris, MSGBOX_DEFAULT
	release
	end

Route6_EventScript_DebrisVerse:
	msgbox Route6_Text_DebrisVerse, MSGBOX_DEFAULT
	release
	end

Route6_Text_Debris:
	.string "Storm debris is jammed across the\n"
	.string "shore path. Nothing gets through.\p"
	.string "The old songs say the river clears\n"
	.string "its own way for those who know it.$"

Route6_Text_DebrisVerse:
	.string "The jam holds. You carry the fourth\n"
	.string "verse, but it hasn't been sung yet.\p"
	.string "TUPELO, at the Old Water, can sing\n"
	.string "it where the river will hear.$"

@ The cut across the channel (x 29, every row; story_data_gates.py): flag triggers turn walkers and surfers back until the
@ fourth verse has been sung at the Old Water.
Route6_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_ROUTE6_DEBRIS_CLEARED, Route6_EventScript_WaterGateOpen
	goto_if_ge VAR_ORLEANS_STORY, 21, Route6_EventScript_WaterGateVerse
	msgbox Route6_Text_WaterGate, MSGBOX_DEFAULT
	goto Route6_EventScript_WaterGateBack

Route6_EventScript_WaterGateVerse:
	msgbox Route6_Text_DebrisVerse, MSGBOX_DEFAULT
Route6_EventScript_WaterGateBack:
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route6_Movement_TurnBack
	waitmovement 0
Route6_EventScript_WaterGateOpen:
	releaseall
	end

Route6_Movement_TurnBack:
	walk_right
	step_end

Route6_Text_WaterGate:
	.string "Storm debris is jammed across the\nchannel, shore to shore.\p"
	.string "Nothing floats or walks through. The\nold songs say the river clears its\p"
	.string "own way for those who know it.$"

@ --- route trainers (gen_route_trainers.py) ---
Route6_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE6_SWIMMER, Route6_Text_Route6SwimmerIntro, Route6_Text_Route6SwimmerDefeat
	msgbox Route6_Text_Route6SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE6_FISHERMAN, Route6_Text_Route6FishermanIntro, Route6_Text_Route6FishermanDefeat
	msgbox Route6_Text_Route6FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE6_SWIMMER_F, Route6_Text_Route6SwimmerFIntro, Route6_Text_Route6SwimmerFDefeat
	msgbox Route6_Text_Route6SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route6_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE6_SAILOR, Route6_Text_Route6SailorIntro, Route6_Text_Route6SailorDefeat
	msgbox Route6_Text_Route6SailorAfter, MSGBOX_AUTOCLOSE
	end

Route6_Text_Route6SwimmerIntro:
	.string "The lake's mine! I swim it every\nmorning. Race you, with POKéMON!$"

Route6_Text_Route6SwimmerDefeat:
	.string "Outswum.$"

Route6_Text_Route6SwimmerAfter:
	.string "The current bends west. It wants to\ncarry you to the camp.$"

Route6_Text_Route6FishermanIntro:
	.string "Fishing the old drowned road. The\nbig ones sleep on the pavement.$"

Route6_Text_Route6FishermanDefeat:
	.string "The big one got away. It was you.$"

Route6_Text_Route6FishermanAfter:
	.string "Cast near the old lampposts. They\nlike the shade.$"

Route6_Text_Route6SwimmerFIntro:
	.string "You came by water! Brave. Or\nsilly. Let's find out!$"

Route6_Text_Route6SwimmerFDefeat:
	.string "Silly, then. Brave too.$"

Route6_Text_Route6SwimmerFAfter:
	.string "The storm moved everything. Even\nthe fish are lost.$"

Route6_Text_Route6SailorIntro:
	.string "A landlubber on my shore! Show\nme you can keep your footing!$"

Route6_Text_Route6SailorDefeat:
	.string "Knocked off my feet.$"

Route6_Text_Route6SailorAfter:
	.string "Past the jam it's open water.\nMind the currents.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

Route6_EventScript_Debris3::
	msgbox Route6_Text_Debris3, MSGBOX_NPC
	end

Route6_Text_Debris3:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

Route6_EventScript_Debris4::
	msgbox Route6_Text_Debris4, MSGBOX_NPC
	end

Route6_Text_Debris4:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

Route6_EventScript_Debris5::
	msgbox Route6_Text_Debris5, MSGBOX_NPC
	end

Route6_Text_Debris5:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

Route6_EventScript_Debris6::
	msgbox Route6_Text_Debris6, MSGBOX_NPC
	end

Route6_Text_Debris6:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

Route6_EventScript_Debris7::
	msgbox Route6_Text_Debris7, MSGBOX_NPC
	end

Route6_Text_Debris7:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

Route6_EventScript_Debris8::
	msgbox Route6_Text_Debris8, MSGBOX_NPC
	end

Route6_Text_Debris8:
	.string "Storm debris jams the whole channel.\nNothing floats through.$"

@ --- mapgen: generated NPC scripts (end) ---

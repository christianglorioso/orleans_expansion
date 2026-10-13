Route2_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, Route2_OnLoad
	.byte 0

@ Route 2: Grand Oak to Storm's Edge, under the high-voltage line. Five trainers (levels 13-16, west to east),
@ a Great Ball, Raichunite Y at the foot of the towers and a hidden Thunder Stone at the lookout.
@ Trainer scripts are named after the mockup marker ids (Trainer2 = marker 2, ...).
Route2_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE2_YOUNGSTER, Route2_Text_YoungsterIntro, Route2_Text_YoungsterDefeat
	msgbox Route2_Text_YoungsterAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE2_CAMPER, Route2_Text_CamperIntro, Route2_Text_CamperDefeat
	msgbox Route2_Text_CamperAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE2_PICNICKER, Route2_Text_PicnickerIntro, Route2_Text_PicnickerDefeat
	msgbox Route2_Text_PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE2_BIRD_KEEPER, Route2_Text_BirdKeeperIntro, Route2_Text_BirdKeeperDefeat
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, Route2_EventScript_BirdKeeperRestored
	msgbox Route2_Text_BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_BirdKeeperRestored:
	msgbox Route2_Text_BirdKeeperRestored, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE2_GUITARIST, Route2_Text_GuitaristIntro, Route2_Text_GuitaristDefeat
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, Route2_EventScript_GuitaristRestored
	msgbox Route2_Text_GuitaristAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_GuitaristRestored:
	msgbox Route2_Text_GuitaristRestored, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- text
Route2_Text_YoungsterIntro:
	.string "You're the one who beat MAGNOLIA!\n"
	.string "Word gets around the poles fast.\p"
	.string "Let's see if you can beat me!$"

Route2_Text_YoungsterDefeat:
	.string "Ow! Cut me down like a hedge!$"

Route2_Text_YoungsterAfter:
	.string "Don't touch the fallen lines in\n"
	.string "the middle. They still bite.$"

Route2_Text_CamperIntro:
	.string "I camped under the towers all\n"
	.string "night. They hum like a hive.\p"
	.string "Good thing I brought backup!$"

Route2_Text_CamperDefeat:
	.string "Your team's wired differently.$"

Route2_Text_CamperAfter:
	.string "ZUBAT love it out here. The hum\n"
	.string "does something to their ears.$"

Route2_Text_PicnickerIntro:
	.string "A PIKACHU followed me home from\n"
	.string "the lookout! Now it's my partner!$"

Route2_Text_PicnickerDefeat:
	.string "We got a little too excited.$"

Route2_Text_PicnickerAfter:
	.string "There's a stone at the lookout\n"
	.string "that crackles. Somebody hid it.$"

Route2_Text_BirdKeeperIntro:
	.string "Birds roost on the wires. The\n"
	.string "lineworkers hate it. I love it.\p"
	.string "Let's see what you've got!$"

Route2_Text_BirdKeeperDefeat:
	.string "Clipped my wings!$"

Route2_Text_BirdKeeperAfter:
	.string "STORM'S EDGE is just ahead. Its\n"
	.string "bridge is up, so I hear.$"

Route2_Text_BirdKeeperRestored:
	.string "The birds are back on the wires\n"
	.string "since the grid hummed to life.$"

Route2_Text_GuitaristIntro:
	.string "I tune up under the towers. The\n"
	.string "line adds a bass note.\p"
	.string "Care for a duet? Battle me!$"

Route2_Text_GuitaristDefeat:
	.string "Off key. Off tempo. Off the stage!$"

Route2_Text_GuitaristAfter:
	.string "ÉCLAIR's crew is repairing the\n"
	.string "grid in STORM'S EDGE. Help them!$"

Route2_Text_GuitaristRestored:
	.string "The line's singing in tune again.\n"
	.string "Whatever you did, thank you!$"

@ The legendary lair's way in (story_data_lairs.py, build.py gates()): sealed in map.bin; from story 45 the generated Route2_EventScript_StateRaikouOpen swaps the
@ open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load, so a sealed way never has a live trigger).
Route2_OnLoad:
	call_if_ge VAR_ORLEANS_STORY, 45, Route2_EventScript_LairOpen
	end

Route2_EventScript_LairOpen:
	call Route2_EventScript_StateRaikouOpen
	setflag FLAG_TEMP_1
	return

Route2_EventScript_LairEnter::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route2_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE2_RAIKOU_CLEARING, 10, 13
	waitstate
	end

Route2_Movement_LairFaceUp:
	face_up
	step_end

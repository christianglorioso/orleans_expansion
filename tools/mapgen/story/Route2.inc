Route2_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route2_OnTransitionPG
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

Route2_OnTransitionPG:
	call Route2_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route2_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route2_EventScript_PGHide
Route2_EventScript_PGSetupDone:
	return

Route2_EventScript_PGHide:
	setflag FLAG_PG_RAIKOU
	return

Route2_EventScript_PgRaikou::
	lock
	faceplayer
	playmoncry SPECIES_RAIKOU, CRY_MODE_ENCOUNTER
	msgbox Route2_Text_PGRaikou, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_RAIKOU, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route2_EventScript_PgRaikouDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route2_EventScript_PgRaikouStill
	release
	end

Route2_EventScript_PgRaikouStill:
	msgbox Route2_Text_PGStillRaikou, MSGBOX_DEFAULT
	release
	end

Route2_EventScript_PgRaikouDone:
	setflag FLAG_PG_RAIKOU
	removeobject LOCALID_ROUTE2_PG_RAIKOU
	release
	end

Route2_Text_PGRaikou:
	.string "RAIKOU stands before you,\n"
	.string "its hide crackling with static.$"

Route2_Text_PGStillRaikou:
	.string "RAIKOU shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

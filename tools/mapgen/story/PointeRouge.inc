PointeRouge_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_OnTransitionPG
	.byte 0

@ Pointe Rouge (Chapter 4). The beats, in order:
@   story 18  (arrived by the riverboat on Route 4) the refinery gate scene: a worker tells the player the control house was
@             taken and the valves opened; four valves to shut (inside the refinery, PointeRouge_Refinery.inc)
@   story 19  the sabotage is stopped (Jayden battle 3, then Camille): the Route 5 tournament can start (Route5.inc)
@   story 21  Kingfisher beaten (PointeRouge_Gym.inc): badge 4, verse 4; go to the Old Water (OldWater_SongHouse.inc)
@ Pointe Rouge's east edge (x=65) is closed by a dust storm until Rayquaza wakes (story 38): see PointeRouge_EventScript_DustStorm.

@ ---------------------------------------------------------------- the refinery gate (story 18)
PointeRouge_EventScript_RefineryGate::
	lockall
	goto_if_set FLAG_POINTE_GATE_SCENE_SEEN, PointeRouge_EventScript_RefineryGateDone
	setflag FLAG_POINTE_GATE_SCENE_SEEN
	applymovement LOCALID_POINTE_ROUGE_WORKER, Common_Movement_FaceLeft
	waitmovement 0
	msgbox PointeRouge_Text_GateScene1, MSGBOX_DEFAULT
	msgbox PointeRouge_Text_GateScene2, MSGBOX_DEFAULT
	msgbox PointeRouge_Text_GateScene3, MSGBOX_DEFAULT
PointeRouge_EventScript_RefineryGateDone:
	releaseall
	end

PointeRouge_EventScript_Worker::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 19, PointeRouge_EventScript_WorkerAfter
	msgbox PointeRouge_Text_WorkerLeak, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_WorkerAfter:
	msgbox PointeRouge_Text_WorkerAfter, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_Chemist::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 19, PointeRouge_EventScript_ChemistAfter
	msgbox PointeRouge_Text_ChemistLeak, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_ChemistAfter:
	msgbox PointeRouge_Text_ChemistAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- Kingfisher on the quay (his line follows the story)
PointeRouge_EventScript_Kingfisher::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 21, PointeRouge_EventScript_KingfisherBeaten
	goto_if_set FLAG_POINTE_TOURNEY_WON, PointeRouge_EventScript_KingfisherWon
	goto_if_ge VAR_ORLEANS_STORY, 20, PointeRouge_EventScript_KingfisherEntered
	goto_if_ge VAR_ORLEANS_STORY, 19, PointeRouge_EventScript_KingfisherOpen
	msgbox PointeRouge_Text_KingfisherFouled, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_KingfisherOpen:
	msgbox PointeRouge_Text_KingfisherOpen, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_KingfisherEntered:
	msgbox PointeRouge_Text_KingfisherEntered, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_KingfisherWon:
	msgbox PointeRouge_Text_KingfisherWon, MSGBOX_DEFAULT
	release
	end

PointeRouge_EventScript_KingfisherBeaten:
	msgbox PointeRouge_Text_KingfisherBeaten, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- the ferry pier: the sailor takes the player back to Crescent City
PointeRouge_EventScript_Sailor::
	lock
	faceplayer
	msgbox PointeRouge_Text_SailorOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PointeRouge_EventScript_SailorNo
	msgbox PointeRouge_Text_SailorGo, MSGBOX_DEFAULT
	closemessage
	setrespawn HEAL_LOCATION_CRESCENT_CITY_WATERFRONT
	fadescreen FADE_TO_BLACK
	warp MAP_CRESCENT_CITY, 56, 51
	waitstate
	release
	end

PointeRouge_EventScript_SailorNo:
	msgbox PointeRouge_Text_SailorNo, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- Route 23: the dust storm
@ Pointe Rouge's east edge (x=65) is closed by a dust storm until Rayquaza wakes (story 38) (Route 23 and 24 are late-game). Flag-based
@ trigger on every cell of the last column: stepping onto one turns the player back west. See story_data_ch3.POINTE_ROUGE.
PointeRouge_EventScript_DustStorm::
	lockall
	msgbox PointeRouge_Text_DustStorm, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, PointeRouge_Movement_StepBackWest
	waitmovement 0
	releaseall
	end

PointeRouge_Movement_StepBackWest:
	walk_left
	step_end

@ ---------------------------------------------------------------- text
PointeRouge_Text_GateScene1:
	.string "WORKER: Back! Stay back from the\n"
	.string "unit! You'll cough up a lung!$"

PointeRouge_Text_GateScene2:
	.string "WORKER: Some people in black took\n"
	.string "the control house at dawn. They\p"
	.string "opened every valve by hand. The\n"
	.string "runoff is going straight to the\p"
	.string "river. Our boss took the shift\n"
	.string "home before it got worse.$"

PointeRouge_Text_GateScene3:
	.string "WORKER: Four valves hold it back,\n"
	.string "two on the north pipe and two on\p"
	.string "the south. Somebody has to shut\n"
	.string "all four. Wear a mask, kid. Or\p"
	.string "just hold your breath.$"

PointeRouge_Text_WorkerLeak:
	.string "WORKER: Four valves, north pipe\n"
	.string "and south pipe. Shut them all.\p"
	.string "The people in black are inside.\n"
	.string "Mind the control house.$"

PointeRouge_Text_WorkerAfter:
	.string "WORKER: The runoff's stopped. The\n"
	.string "air's back to normal. For us,\p"
	.string "that's merely terrible. Thanks,\n"
	.string "kid.$"

PointeRouge_Text_ChemistLeak:
	.string "CHEMIST: Pressure's all over the\n"
	.string "place. Nobody touch the red\p"
	.string "valves! ...Except you, apparently.\n"
	.string "Go on. I'm too old to run.$"

PointeRouge_Text_ChemistAfter:
	.string "CHEMIST: Column two is steady\n"
	.string "again. Thank you, truly.\p"
	.string "Now if I could just feel my\n"
	.string "hands.$"

PointeRouge_Text_KingfisherFouled:
	.string "KINGFISHER: The river's fouled and\n"
	.string "the birds won't fly over it.\p"
	.string "I won't battle with the water this\n"
	.string "dirty. Deal with the refinery.$"

PointeRouge_Text_KingfisherOpen:
	.string "KINGFISHER: The air's clear. That\n"
	.string "was you? Then you earned it.\p"
	.string "The tournament on Route 5 decides\n"
	.string "who battles me. The angler runs it.$"

PointeRouge_Text_KingfisherEntered:
	.string "KINGFISHER: You entered? Good.\n"
	.string "Fish. Wait. Fish some more.\p"
	.string "The river rewards patience. And I\n"
	.string "reward a winner.$"

PointeRouge_Text_KingfisherWon:
	.string "KINGFISHER: You won the tournament.\n"
	.string "The boathouse is open to you.\p"
	.string "The fans are in the rafters. Find\n"
	.string "the right gust and fly up to me.$"

PointeRouge_Text_KingfisherBeaten:
	.string "KINGFISHER: The boathouse has a\n"
	.string "back stair. Faster than a flight.\p"
	.string "The river's road is open to you.\n"
	.string "Take the verse to TUPELO.$"

PointeRouge_Text_SailorOffer:
	.string "SAILOR: The riverboat sails for\n"
	.string "CRESCENT CITY from this pier.\p"
	.string "Going back?$"

PointeRouge_Text_SailorGo:
	.string "SAILOR: All aboard. Hold the rail.$"

PointeRouge_Text_SailorNo:
	.string "SAILOR: She's not going anywhere.\n"
	.string "Neither am I.$"

PointeRouge_Text_DustStorm:
	.string "A wall of red dust rolls in from\n"
	.string "the plains. No one can see to cross.\p"
	.string "Nobody crosses in this. It will\n"
	.string "have to blow itself out first.$"

PointeRouge_OnTransitionPG:
	setflag FLAG_VISITED_POINTE_ROUGE
	call PointeRouge_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
PointeRouge_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, PointeRouge_EventScript_PGHide
	call_if_ge VAR_ORLEANS_STORY, 45, PointeRouge_EventScript_IceGuardGone
	call_if_lt VAR_ORLEANS_STORY, 45, PointeRouge_EventScript_IceGuardHere
PointeRouge_EventScript_PGSetupDone:
	return

@ the ice plant guard steps aside from story 45, state-based so a save that already cleared the game is fixed too
PointeRouge_EventScript_IceGuardGone:
	setflag FLAG_HIDE_POINTE_ICE_GUARD
	return

PointeRouge_EventScript_IceGuardHere:
	clearflag FLAG_HIDE_POINTE_ICE_GUARD
	return

PointeRouge_EventScript_PGHide:
	setflag FLAG_PG_CRABOMINITE
	return

PointeRouge_EventScript_PgCrabominite::
	lock
	giveitem ITEM_CRABOMINITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_PG_CRABOMINITE
	removeobject LOCALID_POINTE_ROUGE_PG_CRABOMINITE
	release
	end

@ --- end post-game ---

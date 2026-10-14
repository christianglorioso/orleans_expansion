Route17_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route17_OnTransitionPG
	map_script MAP_SCRIPT_ON_LOAD, Route17_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route17_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_KINDLER, Route17_Text_Route17KindlerIntro, Route17_Text_Route17KindlerDefeat
	msgbox Route17_Text_Route17KindlerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_BIRD_KEEPER, Route17_Text_Route17BirdKeeperIntro, Route17_Text_Route17BirdKeeperDefeat
	msgbox Route17_Text_Route17BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_COOLTRAINER, Route17_Text_Route17CooltrainerIntro, Route17_Text_Route17CooltrainerDefeat
	msgbox Route17_Text_Route17CooltrainerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_HIKER, Route17_Text_Route17HikerIntro, Route17_Text_Route17HikerDefeat
	msgbox Route17_Text_Route17HikerAfter, MSGBOX_AUTOCLOSE
	end

Route17_Text_Route17KindlerIntro:
	.string "The mill's gym burns bright.\nWarm up on me first!$"

Route17_Text_Route17KindlerDefeat:
	.string "Doused.$"

Route17_Text_Route17KindlerAfter:
	.string "CAYENNE does not lose to the\ncold. Or to anyone, really.$"

Route17_Text_Route17BirdKeeperIntro:
	.string "Thermals over the cane field!\nMy birds love them.$"

Route17_Text_Route17BirdKeeperDefeat:
	.string "Fell out of the sky.$"

Route17_Text_Route17BirdKeeperAfter:
	.string "Smoke rises, birds follow. It's\nan old trick.$"

Route17_Text_Route17CooltrainerIntro:
	.string "Six badges, and the next town\nwants a seventh. Let's see yours!$"

Route17_Text_Route17CooltrainerDefeat:
	.string "You've earned them.$"

Route17_Text_Route17CooltrainerAfter:
	.string "A sunny day, a sunny gym. It's\na hard combination.$"

Route17_Text_Route17HikerIntro:
	.string "The last stretch before the\nmill. I'll make it harder!$"

Route17_Text_Route17HikerDefeat:
	.string "Stumbled.$"

Route17_Text_Route17HikerAfter:
	.string "Past the gate, the sun's the\njudge. Come at noon.$"

@ --- end route trainers ---

Route17_OnTransitionPG:
	end

@ Batch-2 legendary lairs' ways in (story_data_lairs.py, build.py gates()): each is sealed in map.bin; from story 45 the generated
@ Route17_EventScript_State<Name>Open swaps the open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load,
@ so a sealed way never has a live trigger). Entering = LairEnter<Name>; leaving = the lair's Exit script.


Route17_EventScript_LairEnterSugarhouse::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route17_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE17_SUGARHOUSE, 9, 12
	waitstate
	end

Route17_Movement_LairFaceUp:
	face_up
	step_end


@ The mill door (33, 9): barred until the lair is open (story 45 and the Sun Setter trophy; a sign on the door cell, read from the south); once open (FLAG_TEMP_1, armed
@ by Route17_OnLoad) the cell walks and the trigger enters.
Route17_EventScript_MillDoor::
	goto_if_set FLAG_TEMP_1, Route17_EventScript_LairEnterSugarhouse
	goto_if_lt VAR_ORLEANS_STORY, 45, Route17_EventScript_MillDoorBarred
	msgbox Route17_Text_MillDoorSealed, MSGBOX_SIGN
	end

Route17_EventScript_MillDoorBarred:
	msgbox Route17_Text_MillDoorBarred, MSGBOX_SIGN
	end

Route17_Text_MillDoorBarred:
	.string "It's barred. Heat comes through\n"
	.string "the planks.$"

Route17_Text_MillDoorSealed:
	.string "Barred. It opens after the game,\n"
	.string "for the Sun Setter trophy:\p"
	.string "Set Sun 25 times in the\n"
	.string "Battle Frontier.$"

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route17_OnLoad:
	setvar VAR_0x8004, ACH_SUN_SETTER
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route17_EventScript_LairOpenMoltres
	end

Route17_EventScript_LairOpenMoltres:
	call Route17_EventScript_StateSugarhouseOpen
	setflag FLAG_TEMP_1
	return

Route17_EventScript_LairSealEnd:
	end

@ --- lair gates end ---

@ --- mapgen: generated NPC scripts (begin) ---

Route17_EventScript_RouteSign1::
	msgbox Route17_Text_RouteSign1, MSGBOX_SIGN
	end

Route17_Text_RouteSign1:
	.string "SUGAR MILL ROAD\nMind the rail cars.$"

Route17_EventScript_StateSugarhouseOpen::
	setmetatile 33, 9, 0x3A5, FALSE
	return

@ --- mapgen: generated NPC scripts (end) ---

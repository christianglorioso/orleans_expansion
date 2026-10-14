Route12_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route12_OnTransitionPG
	map_script MAP_SCRIPT_ON_LOAD, Route12_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route12_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_BIRD_KEEPER, Route12_Text_Route12BirdKeeperIntro, Route12_Text_Route12BirdKeeperDefeat
	msgbox Route12_Text_Route12BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_HIKER, Route12_Text_Route12HikerIntro, Route12_Text_Route12HikerDefeat
	msgbox Route12_Text_Route12HikerAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_PICNICKER, Route12_Text_Route12PicnickerIntro, Route12_Text_Route12PicnickerDefeat
	msgbox Route12_Text_Route12PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route12_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE12_FISHERMAN, Route12_Text_Route12FishermanIntro, Route12_Text_Route12FishermanDefeat
	msgbox Route12_Text_Route12FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route12_Text_Route12BirdKeeperIntro:
	.string "My birds like the hills. Up\nhere the wind is honest.$"

Route12_Text_Route12BirdKeeperDefeat:
	.string "Plucked.$"

Route12_Text_Route12BirdKeeperAfter:
	.string "Honest wind, honest trainer.\nMostly honest.$"

Route12_Text_Route12HikerIntro:
	.string "Hills, finally! I was going\nstir-crazy on the lake.$"

Route12_Text_Route12HikerDefeat:
	.string "Avalanche.$"

Route12_Text_Route12HikerAfter:
	.string "Mind the roots. They trip\neveryone.$"

Route12_Text_Route12PicnickerIntro:
	.string "Wildflowers everywhere. I'm\ndefending them!$"

Route12_Text_Route12PicnickerDefeat:
	.string "Trampled.$"

Route12_Text_Route12PicnickerAfter:
	.string "The hollow ahead is full of\nfairy rings. Don't step in one.$"

Route12_Text_Route12FishermanIntro:
	.string "Even hills have ponds. This\none's mine.$"

Route12_Text_Route12FishermanDefeat:
	.string "Off the line.$"

Route12_Text_Route12FishermanAfter:
	.string "The pond is bottomless, they\nsay. I've dropped a lot in it.$"

@ --- end route trainers ---

Route12_OnTransitionPG:
	end

@ Batch-2 legendary lairs' ways in (story_data_lairs.py, build.py gates()): each is sealed in map.bin; from story 45 the generated
@ Route12_EventScript_State<Name>Open swaps the open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load,
@ so a sealed way never has a live trigger). Entering = LairEnter<Name>; leaving = the lair's Exit script.


Route12_EventScript_LairEnterThundurus::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route12_Movement_LairFaceRight
	waitmovement 0
	warp MAP_ROUTE12_LEVEE_CROWN, 2, 10
	waitstate
	end

Route12_Movement_LairFaceRight:
	face_right
	step_end

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route12_OnLoad:
	setvar VAR_0x8004, ACH_RAIN_DANCER
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route12_EventScript_LairOpenThundurus
	end

Route12_EventScript_LairOpenThundurus:
	call Route12_EventScript_StateThundurusOpen
	setflag FLAG_TEMP_1
	return

Route12_EventScript_LairSealThundurus::
	goto_if_set FLAG_TEMP_1, Route12_EventScript_LairSealEnd
	msgbox Route12_Text_LairSealThundurus, MSGBOX_SIGN
	end

Route12_Text_LairSealThundurus:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Set Rain 25 times in the\n"
	.string "Battle Frontier.$"

Route12_EventScript_LairSealEnd:
	end

@ --- lair gates end ---

@ --- mapgen: generated NPC scripts (begin) ---

Route12_EventScript_RouteSign1::
	msgbox Route12_Text_RouteSign1, MSGBOX_SIGN
	end

Route12_Text_RouteSign1:
	.string "OVERGROWN GROVE\nSomething stirs among the trees.$"

Route12_EventScript_RouteSign2::
	msgbox Route12_Text_RouteSign2, MSGBOX_SIGN
	end

Route12_Text_RouteSign2:
	.string "GREAT LIVE OAK\nIts roots coil like a serpent.$"

Route12_EventScript_StateThundurusOpen::
	setmetatile 25, 22, 0x27F, FALSE
	setmetatile 26, 22, 0x281, FALSE
	setmetatile 25, 23, 0x280, FALSE
	setmetatile 26, 23, 0x282, FALSE
	return

@ --- mapgen: generated NPC scripts (end) ---

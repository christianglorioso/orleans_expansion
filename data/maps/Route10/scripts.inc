Route10_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, Route10_OnLoad
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

@ Batch-2 legendary lairs' ways in (story_data_lairs.py, build.py gates()): each is sealed in map.bin; from story 45 the generated
@ Route10_EventScript_State<Name>Open swaps the open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load,
@ so a sealed way never has a live trigger). Entering = LairEnter<Name>; leaving = the lair's Exit script.


Route10_EventScript_LairEnterPavilion::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route10_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE10_MILNEBURG_PAVILION, 10, 13
	waitstate
	end

Route10_Movement_LairFaceUp:
	face_up
	step_end

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route10_OnLoad:
	setvar VAR_0x8004, ACH_MIND_AND_WING
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route10_EventScript_LairOpenGalarArticuno
	end

Route10_EventScript_LairOpenGalarArticuno:
	call Route10_EventScript_StatePavilionOpen
	setflag FLAG_TEMP_1
	return

Route10_EventScript_LairSealGalarArticuno::
	goto_if_set FLAG_TEMP_1, Route10_EventScript_LairSealEnd
	msgbox Route10_Text_LairSealGalarArticuno, MSGBOX_SIGN
	end

Route10_Text_LairSealGalarArticuno:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Capture every Psychic and\n"
	.string "Flying Pokémon.$"

Route10_EventScript_LairSealEnd:
	end

@ --- lair gates end ---

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

Route10_EventScript_StatePavilionOpen::
	setmetatile 30, 12, 0x287, FALSE
	setmetatile 31, 12, 0x289, FALSE
	setmetatile 30, 13, 0x288, FALSE
	setmetatile 31, 13, 0x28A, FALSE
	return

@ --- mapgen: generated NPC scripts (end) ---

Route13_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route13_OnTransitionPG
	map_script MAP_SCRIPT_ON_LOAD, Route13_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route13_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_BUG_MANIAC, Route13_Text_Route13BugManiacIntro, Route13_Text_Route13BugManiacDefeat
	msgbox Route13_Text_Route13BugManiacAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_CAMPER, Route13_Text_Route13CamperIntro, Route13_Text_Route13CamperDefeat
	msgbox Route13_Text_Route13CamperAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_PICNICKER, Route13_Text_Route13PicnickerIntro, Route13_Text_Route13PicnickerDefeat
	msgbox Route13_Text_Route13PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route13_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE13_BIRD_KEEPER, Route13_Text_Route13BirdKeeperIntro, Route13_Text_Route13BirdKeeperDefeat
	msgbox Route13_Text_Route13BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route13_Text_Route13BugManiacIntro:
	.string "Fireflies lead to the hollow.\nI follow them. And fight.$"

Route13_Text_Route13BugManiacDefeat:
	.string "Lights out.$"

Route13_Text_Route13BugManiacAfter:
	.string "They only glow for the polite.\nBe polite.$"

Route13_Text_Route13CamperIntro:
	.string "Camped here two nights. The\nmoss whispers. Battle me!$"

Route13_Text_Route13CamperDefeat:
	.string "Quiet now.$"

Route13_Text_Route13CamperAfter:
	.string "Don't answer the whispers.\nThat's how they get you.$"

Route13_Text_Route13PicnickerIntro:
	.string "I'm picking flowers for the\nhollow's fairies. Help?$"

Route13_Text_Route13PicnickerDefeat:
	.string "Petals everywhere.$"

Route13_Text_Route13PicnickerAfter:
	.string "A rose for the real one. The\nfalse ones don't take gifts.$"

Route13_Text_Route13BirdKeeperIntro:
	.string "Last stop before the hollow.\nPay the road toll!$"

Route13_Text_Route13BirdKeeperDefeat:
	.string "Toll's paid.$"

Route13_Text_Route13BirdKeeperAfter:
	.string "The hollow's gate is a lane of\nmoss. You'll feel watched.$"

@ --- end route trainers ---

Route13_OnTransitionPG:
	end

@ Batch-2 legendary lairs' ways in (story_data_lairs.py, build.py gates()): each is sealed in map.bin; from story 45 the generated
@ Route13_EventScript_State<Name>Open swaps the open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load,
@ so a sealed way never has a live trigger). Entering = LairEnter<Name>; leaving = the lair's Exit script.


Route13_EventScript_LairEnterZarude::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route13_Movement_LairFaceRight
	waitmovement 0
	warp MAP_ROUTE13_DEEP_WOOD, 2, 8
	waitstate
	end

Route13_EventScript_LairEnterOgerpon::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route13_Movement_LairFaceLeft
	waitmovement 0
	warp MAP_ROUTE13_COURIR_GLADE, 17, 8
	waitstate
	end

Route13_Movement_LairFaceLeft:
	face_left
	step_end

Route13_Movement_LairFaceRight:
	face_right
	step_end

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route13_OnLoad:
	setvar VAR_0x8004, ACH_MOSS_AND_SHADOW
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route13_EventScript_LairOpenZarude
	setvar VAR_0x8004, ACH_MASK_COLLECTOR
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route13_EventScript_LairOpenOgerpon
	end

Route13_EventScript_LairOpenZarude:
	call Route13_EventScript_StateZarudeOpen
	setflag FLAG_TEMP_1
	return

Route13_EventScript_LairOpenOgerpon:
	call Route13_EventScript_StateOgerponOpen
	setflag FLAG_TEMP_2
	return

Route13_EventScript_LairSealZarude::
	goto_if_set FLAG_TEMP_1, Route13_EventScript_LairSealEnd
	msgbox Route13_Text_LairSealZarude, MSGBOX_SIGN
	end

Route13_Text_LairSealZarude:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Capture every Grass and Dark\n"
	.string "Pokémon.$"

Route13_EventScript_LairSealOgerpon::
	goto_if_set FLAG_TEMP_2, Route13_EventScript_LairSealEnd
	msgbox Route13_Text_LairSealOgerpon, MSGBOX_SIGN
	end

Route13_Text_LairSealOgerpon:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Collect all of Ogerpon's\n"
	.string "masks.$"

Route13_EventScript_LairSealEnd:
	end

@ --- lair gates end ---

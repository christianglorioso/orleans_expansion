Route16_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, Route16_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route16_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE16_PICNICKER, Route16_Text_Route16PicnickerIntro, Route16_Text_Route16PicnickerDefeat
	msgbox Route16_Text_Route16PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE16_BLACK_BELT, Route16_Text_Route16BlackBeltIntro, Route16_Text_Route16BlackBeltDefeat
	msgbox Route16_Text_Route16BlackBeltAfter, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE16_RUIN_MANIAC, Route16_Text_Route16RuinManiacIntro, Route16_Text_Route16RuinManiacDefeat
	msgbox Route16_Text_Route16RuinManiacAfter, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE16_EXPERT, Route16_Text_Route16ExpertIntro, Route16_Text_Route16ExpertDefeat
	msgbox Route16_Text_Route16ExpertAfter, MSGBOX_AUTOCLOSE
	end

Route16_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE16_PICNICKER_2, Route16_Text_Route16Picnicker2Intro, Route16_Text_Route16Picnicker2Defeat
	msgbox Route16_Text_Route16Picnicker2After, MSGBOX_AUTOCLOSE
	end

Route16_Text_Route16PicnickerIntro:
	.string "Peppers for lunch. Battle for\ndessert!$"

Route16_Text_Route16PicnickerDefeat:
	.string "Burned my tongue.$"

Route16_Text_Route16PicnickerAfter:
	.string "Eat the red ones. The green\nones just look innocent.$"

Route16_Text_Route16BlackBeltIntro:
	.string "I train in the heat. It hardens\nthe spirit. And the skin.$"

Route16_Text_Route16BlackBeltDefeat:
	.string "Spirit intact.$"

Route16_Text_Route16BlackBeltAfter:
	.string "Heat's no enemy. Only a\nteacher. A mean one.$"

Route16_Text_Route16RuinManiacIntro:
	.string "Old mill foundations under the\npeppers! Fight me for them!$"

Route16_Text_Route16RuinManiacDefeat:
	.string "Dug up.$"

Route16_Text_Route16RuinManiacAfter:
	.string "The first mill burned. The\nland greened over. Remember that.$"

Route16_Text_Route16ExpertIntro:
	.string "Three siblings, three styles.\nI only fight with all three.$"

Route16_Text_Route16ExpertDefeat:
	.string "A family loss.$"

Route16_Text_Route16ExpertAfter:
	.string "Eevee is the friendliest of all\nPOKéMON. Ask anyone.$"

Route16_Text_Route16Picnicker2Intro:
	.string "I walk the pepper rows at\ndusk. The lights are lovely.$"

Route16_Text_Route16Picnicker2Defeat:
	.string "Lights out.$"

Route16_Text_Route16Picnicker2After:
	.string "Dusk is when the mill sleeps.\nOnly the cane keeps growing.$"

@ --- end route trainers ---

@ The legendary lair's way in (story_data_lairs.py, build.py gates()): sealed in map.bin; from story 45 the generated Route16_EventScript_StateEnteiOpen swaps the
@ open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load, so a sealed way never has a live trigger).


Route16_EventScript_LairEnter::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route16_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE16_ENTEI_FIELD, 10, 13
	waitstate
	end

Route16_Movement_LairFaceUp:
	face_up
	step_end

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route16_OnLoad:
	setvar VAR_0x8004, ACH_FIRE_COLLECTOR
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route16_EventScript_LairOpenEntei
	end

Route16_EventScript_LairOpenEntei:
	call Route16_EventScript_StateEnteiOpen
	setflag FLAG_TEMP_1
	return

Route16_EventScript_LairSealEntei::
	goto_if_set FLAG_TEMP_1, Route16_EventScript_LairSealEnd
	msgbox Route16_Text_LairSealEntei, MSGBOX_SIGN
	end

Route16_Text_LairSealEntei:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Capture every Fire Pokémon.$"

Route16_EventScript_LairSealEnd:
	end

@ --- lair gates end ---

@ --- mapgen: generated NPC scripts (begin) ---

Route16_EventScript_RouteSign1::
	msgbox Route16_Text_RouteSign1, MSGBOX_SIGN
	end

Route16_Text_RouteSign1:
	.string "PEPPER FIELDS\nPickers wanted. Mind the heat.$"

Route16_EventScript_StateEnteiOpen::
	setmetatile 15, 1, 0x273, FALSE
	setmetatile 16, 1, 0x275, FALSE
	setmetatile 15, 2, 0x274, FALSE
	setmetatile 16, 2, 0x276, FALSE
	setmetatile 17, 2, 0x271, TRUE
	setmetatile 17, 3, 0x272, TRUE
	return

@ --- mapgen: generated NPC scripts (end) ---

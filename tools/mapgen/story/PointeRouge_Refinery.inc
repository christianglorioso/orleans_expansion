PointeRouge_Refinery_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_Refinery_OnTransition
	.byte 0

@ Chapter 4 beat 4.2: Camille's sabotage (Team Blacksnake in Pointe Rouge, decision 7), Jayden battle 3, then Camille.
@ Team Blacksnake opened the refinery's valves to flood the marsh with runoff. Four valves sit on the pipes (bg events from
@ story_overlay.py): north row (7, 4) and (15, 4), south row (7, 9) and (15, 9). Each is shut once (FLAG_POINTE_VALVE_1..4).
@ Two grunts patrol the floor (Poison, Ground). When all four valves are shut, Camille and Jayden at the control room
@ (11, 13) / (12, 13) can be fought: Jayden first (a variant per starter, like Route 3), then Camille. Winning sets story 19
@ (never lowered) and hides both. If the player blacks out between the two battles, each trainer's defeated flag skips what is done.
@ Camille taunts until the valves are shut (no battle). The refinery stays open afterwards; the chemist outside thanks the player.

PointeRouge_Refinery_OnTransition:
	call_if_ge VAR_ORLEANS_STORY, 19, PointeRouge_Refinery_EventScript_HideBoss
	end

PointeRouge_Refinery_EventScript_HideBoss:
	setflag FLAG_HIDE_POINTE_CAMILLE
	setflag FLAG_HIDE_POINTE_JAYDEN
	return

PointeRouge_Refinery_EventScript_Valve1::
	lockall
	goto_if_set FLAG_POINTE_VALVE_1, PointeRouge_Refinery_EventScript_ValveShut
	setflag FLAG_POINTE_VALVE_1
	goto PointeRouge_Refinery_EventScript_ValveTurned

PointeRouge_Refinery_EventScript_Valve2::
	lockall
	goto_if_set FLAG_POINTE_VALVE_2, PointeRouge_Refinery_EventScript_ValveShut
	setflag FLAG_POINTE_VALVE_2
	goto PointeRouge_Refinery_EventScript_ValveTurned

PointeRouge_Refinery_EventScript_Valve3::
	lockall
	goto_if_set FLAG_POINTE_VALVE_3, PointeRouge_Refinery_EventScript_ValveShut
	setflag FLAG_POINTE_VALVE_3
	goto PointeRouge_Refinery_EventScript_ValveTurned

PointeRouge_Refinery_EventScript_Valve4::
	lockall
	goto_if_set FLAG_POINTE_VALVE_4, PointeRouge_Refinery_EventScript_ValveShut
	setflag FLAG_POINTE_VALVE_4
	goto PointeRouge_Refinery_EventScript_ValveTurned

PointeRouge_Refinery_EventScript_ValveTurned:
	playse SE_PIN
	msgbox PointeRouge_Refinery_Text_ValveTurned, MSGBOX_DEFAULT
	goto_if_unset FLAG_POINTE_VALVE_1, PointeRouge_Refinery_EventScript_ValveMore
	goto_if_unset FLAG_POINTE_VALVE_2, PointeRouge_Refinery_EventScript_ValveMore
	goto_if_unset FLAG_POINTE_VALVE_3, PointeRouge_Refinery_EventScript_ValveMore
	goto_if_unset FLAG_POINTE_VALVE_4, PointeRouge_Refinery_EventScript_ValveMore
	msgbox PointeRouge_Refinery_Text_AllShut, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Refinery_EventScript_ValveMore:
	msgbox PointeRouge_Refinery_Text_ValveMore, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Refinery_EventScript_ValveShut:
	msgbox PointeRouge_Refinery_Text_ValveShut, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Refinery_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_POINTE_REFINERY_GRUNT_POISON, PointeRouge_Refinery_Text_PoisonIntro, PointeRouge_Refinery_Text_PoisonDefeat
	msgbox PointeRouge_Refinery_Text_PoisonAfter, MSGBOX_AUTOCLOSE
	end

PointeRouge_Refinery_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_POINTE_REFINERY_GRUNT_GROUND, PointeRouge_Refinery_Text_GroundIntro, PointeRouge_Refinery_Text_GroundDefeat
	msgbox PointeRouge_Refinery_Text_GroundAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Camille and Jayden at the control room
PointeRouge_Refinery_EventScript_Camille2::
	lock
	faceplayer
	goto_if_unset FLAG_POINTE_VALVE_1, PointeRouge_Refinery_EventScript_CamilleTaunt
	goto_if_unset FLAG_POINTE_VALVE_2, PointeRouge_Refinery_EventScript_CamilleTaunt
	goto_if_unset FLAG_POINTE_VALVE_3, PointeRouge_Refinery_EventScript_CamilleTaunt
	goto_if_unset FLAG_POINTE_VALVE_4, PointeRouge_Refinery_EventScript_CamilleTaunt
	goto PointeRouge_Refinery_EventScript_Showdown

PointeRouge_Refinery_EventScript_CamilleTaunt:
	msgbox PointeRouge_Refinery_Text_CamilleTaunt, MSGBOX_DEFAULT
	release
	end

PointeRouge_Refinery_EventScript_Jayden3::
	lock
	faceplayer
	goto_if_unset FLAG_POINTE_VALVE_1, PointeRouge_Refinery_EventScript_JaydenTaunt
	goto_if_unset FLAG_POINTE_VALVE_2, PointeRouge_Refinery_EventScript_JaydenTaunt
	goto_if_unset FLAG_POINTE_VALVE_3, PointeRouge_Refinery_EventScript_JaydenTaunt
	goto_if_unset FLAG_POINTE_VALVE_4, PointeRouge_Refinery_EventScript_JaydenTaunt
	goto PointeRouge_Refinery_EventScript_Showdown

PointeRouge_Refinery_EventScript_JaydenTaunt:
	msgbox PointeRouge_Refinery_Text_JaydenTaunt, MSGBOX_DEFAULT
	release
	end

PointeRouge_Refinery_EventScript_Showdown:
	msgbox PointeRouge_Refinery_Text_Showdown1, MSGBOX_DEFAULT
	msgbox PointeRouge_Refinery_Text_Showdown2, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_STARTER_MON, 0, PointeRouge_Refinery_EventScript_BattleJaydenChikorita
	call_if_eq VAR_STARTER_MON, 1, PointeRouge_Refinery_EventScript_BattleJaydenFuecoco
	call_if_eq VAR_STARTER_MON, 2, PointeRouge_Refinery_EventScript_BattleJaydenTotodile
	msgbox PointeRouge_Refinery_Text_JaydenAfter, MSGBOX_DEFAULT
	goto_if_defeated TRAINER_ORLEANS_CAMILLE, PointeRouge_Refinery_EventScript_AfterCamille
	msgbox PointeRouge_Refinery_Text_CamilleIntro, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_ORLEANS_CAMILLE, PointeRouge_Refinery_Text_CamilleDefeat
PointeRouge_Refinery_EventScript_AfterCamille:
	msgbox PointeRouge_Refinery_Text_CamilleRetreat, MSGBOX_DEFAULT
	closemessage
	call_if_lt VAR_ORLEANS_STORY, 19, PointeRouge_Refinery_EventScript_SetStory19
	setflag FLAG_HIDE_POINTE_CAMILLE
	setflag FLAG_HIDE_POINTE_JAYDEN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_POINTE_ROUGE_REFINERY_CAMILLE2
	removeobject LOCALID_POINTE_ROUGE_REFINERY_JAYDEN3
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	msgbox PointeRouge_Refinery_Text_Afterwards, MSGBOX_DEFAULT
	release
	end

PointeRouge_Refinery_EventScript_SetStory19:
	setvar VAR_ORLEANS_STORY, 19
	return

PointeRouge_Refinery_EventScript_BattleJaydenChikorita:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_REFINERY_CHIKORITA, PointeRouge_Refinery_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_REFINERY_CHIKORITA, PointeRouge_Refinery_Text_JaydenDefeat
	return

PointeRouge_Refinery_EventScript_BattleJaydenFuecoco:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_REFINERY_FUECOCO, PointeRouge_Refinery_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_REFINERY_FUECOCO, PointeRouge_Refinery_Text_JaydenDefeat
	return

PointeRouge_Refinery_EventScript_BattleJaydenTotodile:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_REFINERY_TOTODILE, PointeRouge_Refinery_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_REFINERY_TOTODILE, PointeRouge_Refinery_Text_JaydenDefeat
	return

PointeRouge_Refinery_EventScript_JaydenDone:
	return

@ the items on the floor: bag-full safe (the flag is set only once the item is in the bag)
PointeRouge_Refinery_EventScript_SmokeBall4::
	lock
	giveitem ITEM_SMOKE_BALL
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_POINTE_ITEM_SMOKE_BALL
	removeobject LOCALID_POINTE_ROUGE_REFINERY_SMOKE_BALL4
	release
	end

PointeRouge_Refinery_EventScript_MetalCoat5::
	lock
	giveitem ITEM_METAL_COAT
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_POINTE_ITEM_METAL_COAT
	removeobject LOCALID_POINTE_ROUGE_REFINERY_METAL_COAT5
	release
	end

@ ---------------------------------------------------------------- text
PointeRouge_Refinery_Text_ValveTurned:
	.string "You haul on the wheel. It squeals,\n"
	.string "stiffens... and the valve shuts.\p"
	.string "The hiss from the pipe dies down.$"

PointeRouge_Refinery_Text_ValveMore:
	.string "The pipes still hiss from the\n"
	.string "other valves. More to shut.$"

PointeRouge_Refinery_Text_AllShut:
	.string "The last hiss fades. The pipes\n"
	.string "tick as they cool.\p"
	.string "At the far end of the floor, a\n"
	.string "voice you know starts to clap.$"

PointeRouge_Refinery_Text_ValveShut:
	.string "This valve is already shut. The\n"
	.string "pipe above it is quiet.$"

PointeRouge_Refinery_Text_PoisonIntro:
	.string "The valves are open and nobody's\n"
	.string "shutting them. Not on my watch!$"

PointeRouge_Refinery_Text_PoisonDefeat:
	.string "Choked.$"

PointeRouge_Refinery_Text_PoisonAfter:
	.string "RITA says the marsh deserves what\n"
	.string "it gets. I only opened valves.$"

PointeRouge_Refinery_Text_GroundIntro:
	.string "Nobody walks the floor unless\n"
	.string "CAMILLE says so!$"

PointeRouge_Refinery_Text_GroundDefeat:
	.string "Buried.$"

PointeRouge_Refinery_Text_GroundAfter:
	.string "The pipes feed the river. The\n"
	.string "river feeds the city. That's the\p"
	.string "plan. I just don't like the smell.$"

PointeRouge_Refinery_Text_CamilleTaunt:
	.string "CAMILLE: Little mouse. The valves\n"
	.string "are open. They'll stay open.\p"
	.string "Shut every last one, if you dare.\n"
	.string "Then we'll talk.$"

PointeRouge_Refinery_Text_JaydenTaunt:
	.string "JAYDEN: ...Why are you here? Go\n"
	.string "shut the valves. Do it, then.$"

PointeRouge_Refinery_Text_Showdown1:
	.string "CAMILLE: Hm. You shut them all.\n"
	.string "Persistent. I admire that.\p"
	.string "The old storm took my sister in\n"
	.string "one night. A river doesn't\p"
	.string "forgive. It only stops for a\n"
	.string "while. We will make it pay.$"

PointeRouge_Refinery_Text_Showdown2:
	.string "JAYDEN: CAMILLE. ...Wait. You said\n"
	.string "the marsh, not the town. You\p"
	.string "said it was just the marsh!\p"
	.string "CAMILLE: Quiet, boy. Prove\n"
	.string "you're worth the team's name.\p"
	.string "Show them how a Blacksnake bites.$"

PointeRouge_Refinery_Text_JaydenDefeat:
	.string "JAYDEN: ...Tch. Tch. Don't look\n"
	.string "at me like that.$"

PointeRouge_Refinery_Text_JaydenAfter:
	.string "JAYDEN: She never said the river\n"
	.string "would reach the houses. She\p"
	.string "never said. I... I didn't know.$"

PointeRouge_Refinery_Text_CamilleIntro:
	.string "CAMILLE: Hmph. Don't go soft on\n"
	.string "me now, boy. Fine.\p"
	.string "I'll show you what the storm\n"
	.string "left in me. Come, little mouse.$"

PointeRouge_Refinery_Text_CamilleDefeat:
	.string "CAMILLE: ...Strong. Too strong.\n"
	.string "The river is on your side.$"

PointeRouge_Refinery_Text_CamilleRetreat:
	.string "CAMILLE: You've stopped nothing.\n"
	.string "Every pipe is a road for the\p"
	.string "water. RITA's flood is coming.\n"
	.string "Remember my face. Boy. We go.\p"
	.string "JAYDEN: ...Right. Yes. Coming.\p"
	.string "He looks back at you, once.$"

PointeRouge_Refinery_Text_Afterwards:
	.string "The runoff is stopped. The control\n"
	.string "room is empty, and very quiet.\p"
	.string "Outside, the smoke thins in the\n"
	.string "wind. POINTE ROUGE can breathe.$"

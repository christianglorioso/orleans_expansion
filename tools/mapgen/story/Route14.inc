Route14_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route14_OnTransition
	.byte 0

@ Route 14 (Chapter 7). The rougarou: a one-off night Lycanroc Midnight (Lv. 42) on the levee crest; the object shows at night only, until it
@ is beaten or caught. Then the crest holds a LYCANROCITE (given once, bag-full safe: the flag is set after the stone is in the bag).
Route14_OnTransition:
	setflag FLAG_HIDE_ROUTE14_ROUGAROU
	goto_if_set FLAG_RECEIVED_LYCANROCITE, Route14_EventScript_NoRougarou
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Route14_EventScript_ShowRougarou
Route14_EventScript_NoRougarou:
	end

Route14_EventScript_ShowRougarou:
	clearflag FLAG_HIDE_ROUTE14_ROUGAROU
	end

Route14_EventScript_Rougarou::
	lock
	faceplayer
	goto_if_set FLAG_ROUTE14_ROUGAROU_DONE, Route14_EventScript_RougarouStone
	playmoncry SPECIES_LYCANROC_MIDNIGHT, CRY_MODE_ENCOUNTER
	msgbox Route14_Text_Rougarou1, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_LYCANROC_MIDNIGHT, 42
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route14_EventScript_RougarouBeaten
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route14_EventScript_RougarouBeaten
	msgbox Route14_Text_RougarouRan, MSGBOX_DEFAULT
	release
	end

Route14_EventScript_RougarouBeaten:
	setflag FLAG_ROUTE14_ROUGAROU_DONE
	goto Route14_EventScript_RougarouStone

Route14_EventScript_RougarouStone:
	goto_if_set FLAG_RECEIVED_LYCANROCITE, Route14_EventScript_RougarouGone
	msgbox Route14_Text_RougarouStone, MSGBOX_DEFAULT
	giveitem ITEM_LYCANROCITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_LYCANROCITE
	setflag FLAG_HIDE_ROUTE14_ROUGAROU
	removeobject LOCALID_ROUTE14_ROUGAROU
	release
	end

Route14_EventScript_RougarouGone:
	msgbox Route14_Text_RougarouGone, MSGBOX_DEFAULT
	release
	end

@ --- route trainers (gen_route_trainers.py) ---
Route14_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_FISHERMAN, Route14_Text_Route14FishermanIntro, Route14_Text_Route14FishermanDefeat
	msgbox Route14_Text_Route14FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route14_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_BIRD_KEEPER, Route14_Text_Route14BirdKeeperIntro, Route14_Text_Route14BirdKeeperDefeat
	msgbox Route14_Text_Route14BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route14_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_CAMPER, Route14_Text_Route14CamperIntro, Route14_Text_Route14CamperDefeat
	msgbox Route14_Text_Route14CamperAfter, MSGBOX_AUTOCLOSE
	end

Route14_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_PICNICKER, Route14_Text_Route14PicnickerIntro, Route14_Text_Route14PicnickerDefeat
	msgbox Route14_Text_Route14PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route14_EventScript_Trainer8::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_BUG_MANIAC, Route14_Text_Route14BugManiacIntro, Route14_Text_Route14BugManiacDefeat
	msgbox Route14_Text_Route14BugManiacAfter, MSGBOX_AUTOCLOSE
	end

Route14_EventScript_Trainer10::
	trainerbattle_single TRAINER_ORLEANS_ROUTE14_BLACK_BELT, Route14_Text_Route14BlackBeltIntro, Route14_Text_Route14BlackBeltDefeat
	msgbox Route14_Text_Route14BlackBeltAfter, MSGBOX_AUTOCLOSE
	end

Route14_Text_Route14FishermanIntro:
	.string "The levee road is dry again. My\nlines are not. Battle me!$"

Route14_Text_Route14FishermanDefeat:
	.string "Snapped line.$"

Route14_Text_Route14FishermanAfter:
	.string "The water went down all at once.\nI almost lost my boat.$"

Route14_Text_Route14BirdKeeperIntro:
	.string "My birds watched the flood go\ndown. They want a rematch!$"

Route14_Text_Route14BirdKeeperDefeat:
	.string "Grounded.$"

Route14_Text_Route14BirdKeeperAfter:
	.string "Noctowl sees the rougarou at\nnight. Won't tell me where.$"

Route14_Text_Route14CamperIntro:
	.string "I camp on the crest. Something\nhowls there after dark.$"

Route14_Text_Route14CamperDefeat:
	.string "Howled out.$"

Route14_Text_Route14CamperAfter:
	.string "Don't camp up there. Take it\nfrom me.$"

Route14_Text_Route14PicnickerIntro:
	.string "Sunflowers grow wild by the\nlevee. I guard them!$"

Route14_Text_Route14PicnickerDefeat:
	.string "Wilted.$"

Route14_Text_Route14PicnickerAfter:
	.string "They all face the mill. Don't\nask me why.$"

Route14_Text_Route14BugManiacIntro:
	.string "Cane beetles, cane moths. This\nroad is a bug paradise.$"

Route14_Text_Route14BugManiacDefeat:
	.string "Squashed.$"

Route14_Text_Route14BugManiacAfter:
	.string "Cane smoke drives the bugs\nonto the road. Happy me!$"

Route14_Text_Route14BlackBeltIntro:
	.string "I trained against the flood.\nNow I train against you!$"

Route14_Text_Route14BlackBeltDefeat:
	.string "Knocked flat.$"

Route14_Text_Route14BlackBeltAfter:
	.string "The sugar country starts south\nof here. Eat well.$"

@ --- end route trainers ---

Route14_Text_Rougarou1:
	.string "Something big stands on the levee\n"
	.string "crest, silver in the dark. It lifts\p"
	.string "its head and howls, once.$"

Route14_Text_RougarouRan:
	.string "The rougarou melts into the cane.\n"
	.string "The crest is quiet again.$"

Route14_Text_RougarouStone:
	.string "Where it stood, a stone glows dimly:\n"
	.string "a LYCANROCITE, left in the grass.$"

Route14_Text_RougarouGone:
	.string "The crest is empty now. Only the\n"
	.string "wind, and a flattened ring of grass.$"

Route14_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route14_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, Route14_OnLoad
	.byte 0

@ Route 14 (Chapter 7). The rougarou, a one-off night Lycanroc Midnight (Lv. 42), no longer stands on the levee crest: it lives in its own hollow in the
@ east canopy (Route14_RougarouHollow, story/Route14_RougarouHollow.inc). The trail into the trees opens with the flood: the generated
@ Route14_EventScript_StateRougarouOpen (the canopy gap, story_data_lairs.py) is swapped in on load once FLAG_BADGE06_GET is set (the water is down, the
@ road is open) and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load).
Route14_OnTransition:
	call Route14_EventScript_StoryWeather
	end

Route14_OnLoad:
	call_if_set FLAG_BADGE06_GET, Route14_EventScript_LairOpen
	end

Route14_EventScript_LairOpen:
	call Route14_EventScript_StateRougarouOpen
	setflag FLAG_TEMP_1
	return

Route14_EventScript_LairEnter::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route14_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE14_ROUGAROU_HOLLOW, 10, 13
	waitstate
	end

Route14_Movement_LairFaceUp:
	face_up
	step_end

@ weather (weather_plan.py): rain until the floodwater has gone (gym 6), then clear. Runs from OnTransition, before the weather starts.
Route14_EventScript_StoryWeather:
	goto_if_unset FLAG_BADGE06_GET, Route14_EventScript_StoryWeatherDone
	setweather WEATHER_NONE
Route14_EventScript_StoryWeatherDone:
	return

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

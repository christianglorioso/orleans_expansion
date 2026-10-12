Route4_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route4_OnFrameTable
	.byte 0

@ Route 4, the levee road between the riverboat landing (south, Chapter 3's ferry) and Pointe Rouge (north).
@ Chapter 4 beat 4.1: the arrival scene. Six trainers (levels 24-27, south to north), three item balls (TM Tailwind, X Speed,
@ X Defense), a hidden Dusk Stone and the hidden Bottle Cap. Trainer scripts are named after the mockup marker ids.

Route4_OnFrameTable:
	map_script_2 VAR_ROUTE4_ARRIVAL, 0, Route4_EventScript_Arrival
	.2byte 0

@ (A frame table compares VARS only, never flags: hence a var, not a flag.)
@ The first time the player steps off the riverboat: the respawn point moves to Pointe Rouge's center (set once, here; the
@ center sets it again when the player walks in, which is the same place) and the player sees the smoke over the city.
Route4_EventScript_Arrival::
	@ only the riverboat's first landing (story 18) plays the scene; any other way onto the map (a debug warp) skips it
	goto_if_ne VAR_ORLEANS_STORY, 18, Route4_EventScript_ArrivalSkip
	lockall
	setvar VAR_ROUTE4_ARRIVAL, 1
	setrespawn HEAL_LOCATION_POINTE_ROUGE
	msgbox Route4_Text_Arrival1, MSGBOX_DEFAULT
	msgbox Route4_Text_Arrival2, MSGBOX_DEFAULT
	releaseall
	end

Route4_EventScript_ArrivalSkip:
	end

@ The riverboat landing's deckhand takes the player back to Crescent City's terminal.
Route4_EventScript_Deckhand::
	lock
	faceplayer
	msgbox Route4_Text_DeckhandOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route4_EventScript_DeckhandNo
	msgbox Route4_Text_DeckhandGo, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warp MAP_CRESCENT_CITY, 56, 51
	waitstate
	release
	end

Route4_EventScript_DeckhandNo:
	msgbox Route4_Text_DeckhandNo, MSGBOX_DEFAULT
	release
	end

Route4_EventScript_Trainer8::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_HIKER, Route4_Text_HikerIntro, Route4_Text_HikerDefeat
	msgbox Route4_Text_HikerAfter, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_PICNICKER, Route4_Text_PicnickerIntro, Route4_Text_PicnickerDefeat
	msgbox Route4_Text_PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_CAMPER, Route4_Text_CamperIntro, Route4_Text_CamperDefeat
	msgbox Route4_Text_CamperAfter, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_SAILOR, Route4_Text_SailorIntro, Route4_Text_SailorDefeat
	msgbox Route4_Text_SailorAfter, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_FISHERMAN, Route4_Text_FishermanIntro, Route4_Text_FishermanDefeat
	msgbox Route4_Text_FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route4_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE4_BIRD_KEEPER, Route4_Text_BirdKeeperIntro, Route4_Text_BirdKeeperDefeat
	msgbox Route4_Text_BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- text
Route4_Text_Arrival1:
	.string "The riverboat's wake rolls out and\n"
	.string "slaps the levee. Then it's quiet.\p"
	.string "The Emerald River runs wide and\n"
	.string "brown beside the road.$"

Route4_Text_Arrival2:
	.string "Upriver, a column of black smoke\n"
	.string "stands over POINTE ROUGE.\p"
	.string "The chimneys are always smoking\n"
	.string "there. Not like that.$"

Route4_Text_DeckhandOffer:
	.string "DECKHAND: The riverboat goes back\n"
	.string "to CRESCENT CITY. Heading back?$"

Route4_Text_DeckhandGo:
	.string "DECKHAND: Mind the gangway.$"

Route4_Text_DeckhandNo:
	.string "DECKHAND: She sails when you're\n"
	.string "ready. The river's not going\p"
	.string "anywhere.$"

Route4_Text_HikerIntro:
	.string "I climbed the levee for the view.\n"
	.string "Found a rock fight instead!$"

Route4_Text_HikerDefeat:
	.string "Crumbled like old mortar.$"

Route4_Text_HikerAfter:
	.string "The levee's older than the town.\n"
	.string "Treat her kindly.$"

Route4_Text_PicnickerIntro:
	.string "I packed a lunch for two. You\n"
	.string "look hungry. Battle first!$"

Route4_Text_PicnickerDefeat:
	.string "Fine. You can have the sandwich.$"

Route4_Text_PicnickerAfter:
	.string "Don't eat the ones in the red\n"
	.string "napkin. Those are for my GLOOM.$"

Route4_Text_CamperIntro:
	.string "Camping by a river is the best.\n"
	.string "Until a trainer shows up.$"

Route4_Text_CamperDefeat:
	.string "My tent was more fun than this.$"

Route4_Text_CamperAfter:
	.string "Keep walking north. You'll smell\n"
	.string "the refinery before you see it.$"

Route4_Text_SailorIntro:
	.string "Off the boat and onto my road!\n"
	.string "Let me test your sea legs!$"

Route4_Text_SailorDefeat:
	.string "Overboard, and I'm the one who\n"
	.string "got wet.$"

Route4_Text_SailorAfter:
	.string "The river's low in the shallows\n"
	.string "and wild in the bends.$"

Route4_Text_FishermanIntro:
	.string "Nothing's biting. I'm in a mood.\n"
	.string "Battle me, or I'll sulk louder.$"

Route4_Text_FishermanDefeat:
	.string "That's the first thing to bite\n"
	.string "all day.$"

Route4_Text_FishermanAfter:
	.string "Even the catfish are staying\n"
	.string "south. Something's in the water.$"

Route4_Text_BirdKeeperIntro:
	.string "The river road belongs to the\n"
	.string "birds. Cross it and cross me!$"

Route4_Text_BirdKeeperDefeat:
	.string "Clipped.$"

Route4_Text_BirdKeeperAfter:
	.string "My birds won't fly near that\n"
	.string "smoke. They know bad air.$"

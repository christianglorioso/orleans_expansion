Route7_MapScripts::
	.byte 0

@ Route 7 (the bayou islands): four trainers (32-34), a cut stump that holds a Pry Bar cache (Kleavorite; decision 2: optional,
@ never a gate), TM Trick, a hidden Star Piece. Trainer scripts are generated (gen_route_trainers.py).
Route7_EventScript_Stump::
	lock
	checkitem ITEM_PRY_BAR
	goto_if_eq VAR_RESULT, FALSE, Route7_EventScript_StumpLocked
	msgbox Route7_Text_StumpPry, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route7_EventScript_StumpLeave
	giveitem ITEM_KLEAVORITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_ROUTE7_STUMP_OPENED
	removeobject LOCALID_ORLEANS_ROUTE7_STUMP
	release
	end

Route7_EventScript_StumpLocked:
	msgbox Route7_Text_StumpLocked, MSGBOX_DEFAULT
	release
	end

Route7_EventScript_StumpLeave:
	release
	end

Route7_Text_StumpLocked:
	.string "A hollow cypress stump. A seam runs\n"
	.string "around it, painted over. Something\p"
	.string "is wedged inside. A tool with a\n"
	.string "flat edge could pry it open.$"

Route7_Text_StumpPry:
	.string "The stump has a hidden seam. Pry it\n"
	.string "open with the PRY BAR?$"

@ --- route trainers (gen_route_trainers.py) ---
Route7_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE7_CAMPER, Route7_Text_Route7CamperIntro, Route7_Text_Route7CamperDefeat
	msgbox Route7_Text_Route7CamperAfter, MSGBOX_AUTOCLOSE
	end

Route7_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE7_PICNICKER, Route7_Text_Route7PicnickerIntro, Route7_Text_Route7PicnickerDefeat
	msgbox Route7_Text_Route7PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route7_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE7_BUG_MANIAC, Route7_Text_Route7BugManiacIntro, Route7_Text_Route7BugManiacDefeat
	msgbox Route7_Text_Route7BugManiacAfter, MSGBOX_AUTOCLOSE
	end

Route7_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE7_BIRD_KEEPER, Route7_Text_Route7BirdKeeperIntro, Route7_Text_Route7BirdKeeperDefeat
	msgbox Route7_Text_Route7BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route7_Text_Route7CamperIntro:
	.string "The bayou's the best campground\nin the region. Mind the gators!$"

Route7_Text_Route7CamperDefeat:
	.string "Smashed my tent.$"

Route7_Text_Route7CamperAfter:
	.string "A stump near here holds a cache.\nNeeds a Pry Bar, though.$"

Route7_Text_Route7PicnickerIntro:
	.string "I picked a spot for lunch and\nit's already taken. By you!$"

Route7_Text_Route7PicnickerDefeat:
	.string "Lunch is ruined.$"

Route7_Text_Route7PicnickerAfter:
	.string "The camp's gumbo is worth the\ntrip. Ask for the real roux.$"

Route7_Text_Route7BugManiacIntro:
	.string "Fireflies and ninjask! The bayou\nat night is my lab.$"

Route7_Text_Route7BugManiacDefeat:
	.string "My lab is in ruins.$"

Route7_Text_Route7BugManiacAfter:
	.string "Ninjask molts at the cypress knees.\nCollect the shells!$"

Route7_Text_Route7BirdKeeperIntro:
	.string "My flock hunts these islands.\nProve you can fly with them.$"

Route7_Text_Route7BirdKeeperDefeat:
	.string "Grounded.$"

Route7_Text_Route7BirdKeeperAfter:
	.string "A swanna never sinks. Neither\ndoes a good plan.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

Route7_EventScript_RouteSign1::
	msgbox Route7_Text_RouteSign1, MSGBOX_SIGN
	end

Route7_Text_RouteSign1:
	.string "THE OLDEST CYPRESS\nA shrine to the forest's keeper.$"

Route7_EventScript_RouteSign2::
	msgbox Route7_Text_RouteSign2, MSGBOX_SIGN
	end

Route7_Text_RouteSign2:
	.string "OLD LOGGING RUN\nThe trunks floated down from here.$"

@ --- mapgen: generated NPC scripts (end) ---

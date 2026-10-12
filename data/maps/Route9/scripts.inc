Route9_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route9_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE9_PICNICKER, Route9_Text_Route9PicnickerIntro, Route9_Text_Route9PicnickerDefeat
	msgbox Route9_Text_Route9PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route9_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE9_HIKER, Route9_Text_Route9HikerIntro, Route9_Text_Route9HikerDefeat
	msgbox Route9_Text_Route9HikerAfter, MSGBOX_AUTOCLOSE
	end

Route9_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE9_SAILOR, Route9_Text_Route9SailorIntro, Route9_Text_Route9SailorDefeat
	msgbox Route9_Text_Route9SailorAfter, MSGBOX_AUTOCLOSE
	end

Route9_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE9_BIRD_KEEPER, Route9_Text_Route9BirdKeeperIntro, Route9_Text_Route9BirdKeeperDefeat
	msgbox Route9_Text_Route9BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route9_Text_Route9PicnickerIntro:
	.string "My garden came through the storm.\nBarely. Like me!$"

Route9_Text_Route9PicnickerDefeat:
	.string "Wilted.$"

Route9_Text_Route9PicnickerAfter:
	.string "The camp's okra is the best in\nthe region. Ask the gardener.$"

Route9_Text_Route9HikerIntro:
	.string "A hiker, a bayou, a boulder.\nThat's my whole life!$"

Route9_Text_Route9HikerDefeat:
	.string "Rock bottom.$"

Route9_Text_Route9HikerAfter:
	.string "Stone and cypress. That's the\nold way.$"

Route9_Text_Route9SailorIntro:
	.string "Camp's just ahead, sailor. But\nfirst, a toll!$"

Route9_Text_Route9SailorDefeat:
	.string "Paid in full.$"

Route9_Text_Route9SailorAfter:
	.string "The brothers like their gumbo\nthick. Don't call it soup.$"

Route9_Text_Route9BirdKeeperIntro:
	.string "My birds smell the gumbo from\nhere. Let's earn a bowl.$"

Route9_Text_Route9BirdKeeperDefeat:
	.string "No bowl for me.$"

Route9_Text_Route9BirdKeeperAfter:
	.string "Fly low over the camp. The\nsmoke carries news.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

Route9_EventScript_RouteSign1::
	msgbox Route9_Text_RouteSign1, MSGBOX_SIGN
	end

Route9_Text_RouteSign1:
	.string "CAMP COCODRIE\nGator wranglers' trail leads north.$"

Route9_EventScript_RouteSign2::
	msgbox Route9_Text_RouteSign2, MSGBOX_SIGN
	end

Route9_Text_RouteSign2:
	.string "BOAT LANDING\nBoats leave for the open bayou lake.$"

@ --- mapgen: generated NPC scripts (end) ---

Route17_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route17_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_KINDLER, Route17_Text_Route17KindlerIntro, Route17_Text_Route17KindlerDefeat
	msgbox Route17_Text_Route17KindlerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_BIRD_KEEPER, Route17_Text_Route17BirdKeeperIntro, Route17_Text_Route17BirdKeeperDefeat
	msgbox Route17_Text_Route17BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_COOLTRAINER, Route17_Text_Route17CooltrainerIntro, Route17_Text_Route17CooltrainerDefeat
	msgbox Route17_Text_Route17CooltrainerAfter, MSGBOX_AUTOCLOSE
	end

Route17_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE17_HIKER, Route17_Text_Route17HikerIntro, Route17_Text_Route17HikerDefeat
	msgbox Route17_Text_Route17HikerAfter, MSGBOX_AUTOCLOSE
	end

Route17_Text_Route17KindlerIntro:
	.string "The mill's gym burns bright.\nWarm up on me first!$"

Route17_Text_Route17KindlerDefeat:
	.string "Doused.$"

Route17_Text_Route17KindlerAfter:
	.string "CAYENNE does not lose to the\ncold. Or to anyone, really.$"

Route17_Text_Route17BirdKeeperIntro:
	.string "Thermals over the cane field!\nMy birds love them.$"

Route17_Text_Route17BirdKeeperDefeat:
	.string "Fell out of the sky.$"

Route17_Text_Route17BirdKeeperAfter:
	.string "Smoke rises, birds follow. It's\nan old trick.$"

Route17_Text_Route17CooltrainerIntro:
	.string "Two badges short of the next\ntown. Let's see yours!$"

Route17_Text_Route17CooltrainerDefeat:
	.string "You've earned them.$"

Route17_Text_Route17CooltrainerAfter:
	.string "A sunny day, a sunny gym. It's\na hard combination.$"

Route17_Text_Route17HikerIntro:
	.string "The last stretch before the\nmill. I'll make it harder!$"

Route17_Text_Route17HikerDefeat:
	.string "Stumbled.$"

Route17_Text_Route17HikerAfter:
	.string "Past the gate, the sun's the\njudge. Come at noon.$"

@ --- end route trainers ---

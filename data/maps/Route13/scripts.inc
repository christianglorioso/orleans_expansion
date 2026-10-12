Route13_MapScripts::
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

@ --- mapgen: generated NPC scripts (begin) ---

Route13_EventScript_RouteSign1::
	msgbox Route13_Text_RouteSign1, MSGBOX_SIGN
	end

Route13_Text_RouteSign1:
	.string "MEADOW SHRINE\nFlowers are left here for Flabébé.$"

Route13_EventScript_RouteSign2::
	msgbox Route13_Text_RouteSign2, MSGBOX_SIGN
	end

Route13_Text_RouteSign2:
	.string "THE MIST THICKENS\nStay on the path.$"

@ --- mapgen: generated NPC scripts (end) ---

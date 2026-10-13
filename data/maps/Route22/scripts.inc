Route22_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route22_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE22_SWIMMER, Route22_Text_Route22SwimmerIntro, Route22_Text_Route22SwimmerDefeat
	msgbox Route22_Text_Route22SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route22_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE22_SWIMMER_F, Route22_Text_Route22SwimmerFIntro, Route22_Text_Route22SwimmerFDefeat
	msgbox Route22_Text_Route22SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route22_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE22_SWIMMER_2, Route22_Text_Route22Swimmer2Intro, Route22_Text_Route22Swimmer2Defeat
	msgbox Route22_Text_Route22Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route22_Text_Route22SwimmerIntro:
	.string "Open water, nothing but the\nhorizon. And me!$"

Route22_Text_Route22SwimmerDefeat:
	.string "Horizon wins.$"

Route22_Text_Route22SwimmerAfter:
	.string "The temple door has a hollow\nshaped like a song. I heard it.$"

Route22_Text_Route22SwimmerFIntro:
	.string "The lights down there are the\ntemple's. Beautiful. Wrong.$"

Route22_Text_Route22SwimmerFDefeat:
	.string "Lights out.$"

Route22_Text_Route22SwimmerFAfter:
	.string "Kyogre sleeps below. Everybody\nknows. Nobody says it.$"

Route22_Text_Route22Swimmer2Intro:
	.string "This is as far as the sea lets\nyou go. For now.$"

Route22_Text_Route22Swimmer2Defeat:
	.string "Beached.$"

Route22_Text_Route22Swimmer2After:
	.string "When the telling's complete, the\nwater will let you through.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

Route22_EventScript_RouteSign1::
	msgbox Route22_Text_RouteSign1, MSGBOX_SIGN
	end

Route22_Text_RouteSign1:
	.string "DROWNED TEMPLE\nDive here. Diving Gear required.$"

@ --- mapgen: generated NPC scripts (end) ---

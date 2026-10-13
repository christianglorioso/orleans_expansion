Route22_MapScripts::
	.byte 0

@ The dive spot (Chapter 9, F.1): stand on the islet's east tip (13, 20) facing the water (14, 20). Needs the Diving Gear (Heron, gym 8) and
@ the telling (story >= 39); it leads down to the Drowned Temple's Tide Hall (Kyogre's raid arena).
Route22_EventScript_DiveSpot::
	lockall
	goto_if_unset FLAG_RECEIVED_DIVING_GEAR, Route22_EventScript_DiveNoGear
	goto_if_lt VAR_ORLEANS_STORY, 39, Route22_EventScript_DiveNotYet
	msgbox Route22_Text_DiveGo, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warpsilent MAP_LANDS_END_DROWNED_TEMPLE, 8, 13
	waitstate
	releaseall
	end

Route22_EventScript_DiveNoGear:
	msgbox Route22_Text_DiveNoGear, MSGBOX_DEFAULT
	releaseall
	end

Route22_EventScript_DiveNotYet:
	msgbox Route22_Text_DiveNotYet, MSGBOX_DEFAULT
	releaseall
	end

Route22_Text_DiveNoGear:
	.string "The water past the islet is dark and\n"
	.string "deep. Without gear, you'd never\p"
	.string "come back up.$"

Route22_Text_DiveNotYet:
	.string "The water glows faintly below. Not\n"
	.string "yet. The telling comes first.$"

Route22_Text_DiveGo:
	.string "You pull on the DIVING GEAR and sink\n"
	.string "into the dark, toward the glow.$"

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
	.string "The water lets the singers through.\nIt's letting you.$"

@ --- end route trainers ---

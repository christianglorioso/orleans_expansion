Route25_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route25_OnTransition
	.byte 0

Route25_OnTransition:
	call Route25_EventScript_StoryWeather
	end

@ weather (weather_plan.py): thunderstorm through the finale, clear once the Rayquaza raid is won (story 43)
Route25_EventScript_StoryWeather:
	goto_if_lt VAR_ORLEANS_STORY, 43, Route25_EventScript_StoryWeatherDone
	setweather WEATHER_NONE
Route25_EventScript_StoryWeatherDone:
	return

@ --- route trainers (gen_route_trainers.py) ---
Route25_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE25_SWIMMER, Route25_Text_Route25SwimmerIntro, Route25_Text_Route25SwimmerDefeat
	msgbox Route25_Text_Route25SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE25_SWIMMER_F, Route25_Text_Route25SwimmerFIntro, Route25_Text_Route25SwimmerFDefeat
	msgbox Route25_Text_Route25SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE25_SWIMMER_2, Route25_Text_Route25Swimmer2Intro, Route25_Text_Route25Swimmer2Defeat
	msgbox Route25_Text_Route25Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE25_SWIMMER_F2, Route25_Text_Route25SwimmerF2Intro, Route25_Text_Route25SwimmerF2Defeat
	msgbox Route25_Text_Route25SwimmerF2After, MSGBOX_AUTOCLOSE
	end

Route25_Text_Route25SwimmerIntro:
	.string "The storm wall's gone. The\nchannel is mine to cross first!$"

Route25_Text_Route25SwimmerDefeat:
	.string "Second again.$"

Route25_Text_Route25SwimmerAfter:
	.string "The shrine sits on an island of\nsinging stone. You'll hear it.$"

Route25_Text_Route25SwimmerFIntro:
	.string "The water's calm now. Both\nsleepers are at rest.$"

Route25_Text_Route25SwimmerFDefeat:
	.string "Calm as ever.$"

Route25_Text_Route25SwimmerFAfter:
	.string "Black boats passed here at\nnight. They didn't light a lamp.$"

Route25_Text_Route25Swimmer2Intro:
	.string "Nobody swims past me to the\nshrine. Not today.$"

Route25_Text_Route25Swimmer2Defeat:
	.string "Let through.$"

Route25_Text_Route25Swimmer2After:
	.string "Mind the third current. It\nturns toward the stone.$"

Route25_Text_Route25SwimmerF2Intro:
	.string "Last stretch before the stone.\nI won't make it easy.$"

Route25_Text_Route25SwimmerF2Defeat:
	.string "Easy after all.$"

Route25_Text_Route25SwimmerF2After:
	.string "Sing when you land. The stone\nlistens.$"

@ --- end route trainers ---

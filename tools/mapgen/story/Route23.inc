Route23_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route23_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_HIKER, Route23_Text_Route23HikerIntro, Route23_Text_Route23HikerDefeat
	msgbox Route23_Text_Route23HikerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_RUIN_MANIAC, Route23_Text_Route23RuinManiacIntro, Route23_Text_Route23RuinManiacDefeat
	msgbox Route23_Text_Route23RuinManiacAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_PICNICKER, Route23_Text_Route23PicnickerIntro, Route23_Text_Route23PicnickerDefeat
	msgbox Route23_Text_Route23PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_BLACK_BELT, Route23_Text_Route23BlackBeltIntro, Route23_Text_Route23BlackBeltDefeat
	msgbox Route23_Text_Route23BlackBeltAfter, MSGBOX_AUTOCLOSE
	end

Route23_Text_Route23HikerIntro:
	.string "The dust's gone, finally. The\nplains are mine again.$"

Route23_Text_Route23HikerDefeat:
	.string "Dust to dust.$"

Route23_Text_Route23HikerAfter:
	.string "The salt mine's north-east. Don't\ngo in without a light.$"

Route23_Text_Route23RuinManiacIntro:
	.string "The storm uncovered an old wall.\nI'm guarding it. Fight me!$"

Route23_Text_Route23RuinManiacDefeat:
	.string "Buried.$"

Route23_Text_Route23RuinManiacAfter:
	.string "The wall sings when the wind\nhits it. Like a flute.$"

Route23_Text_Route23PicnickerIntro:
	.string "Grass grows back through dust.\nI came to watch it.$"

Route23_Text_Route23PicnickerDefeat:
	.string "Pressed flat.$"

Route23_Text_Route23PicnickerAfter:
	.string "A shadow crossed the whole sky.\nI felt it in my teeth.$"

Route23_Text_Route23BlackBeltIntro:
	.string "The storm's lifted. My training\ncan resume. Spar with me!$"

Route23_Text_Route23BlackBeltDefeat:
	.string "Sparred out.$"

Route23_Text_Route23BlackBeltAfter:
	.string "Cleaner air makes better\ntraining.$"

@ --- end route trainers ---

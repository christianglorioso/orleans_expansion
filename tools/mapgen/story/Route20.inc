Route20_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route20_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE20_SWIMMER, Route20_Text_Route20SwimmerIntro, Route20_Text_Route20SwimmerDefeat
	msgbox Route20_Text_Route20SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route20_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE20_SWIMMER_F, Route20_Text_Route20SwimmerFIntro, Route20_Text_Route20SwimmerFDefeat
	msgbox Route20_Text_Route20SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route20_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE20_SAILOR, Route20_Text_Route20SailorIntro, Route20_Text_Route20SailorDefeat
	msgbox Route20_Text_Route20SailorAfter, MSGBOX_AUTOCLOSE
	end

Route20_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE20_SWIMMER_2, Route20_Text_Route20Swimmer2Intro, Route20_Text_Route20Swimmer2Defeat
	msgbox Route20_Text_Route20Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route20_Text_Route20SwimmerIntro:
	.string "The herons watch from the pilings.\nThey judge swimmers.$"

Route20_Text_Route20SwimmerDefeat:
	.string "Judged.$"

Route20_Text_Route20SwimmerAfter:
	.string "Land's End is two islets east.\nFollow the herons.$"

Route20_Text_Route20SwimmerFIntro:
	.string "Rain's coming. I can smell it.\nHeron's rain, they call it.$"

Route20_Text_Route20SwimmerFDefeat:
	.string "Drenched.$"

Route20_Text_Route20SwimmerFAfter:
	.string "HERON keeps the rain. She lets\nit fall when it's ready.$"

Route20_Text_Route20SailorIntro:
	.string "Last islet before Land's End.\nToll's a battle!$"

Route20_Text_Route20SailorDefeat:
	.string "Toll paid.$"

Route20_Text_Route20SailorAfter:
	.string "The pilings go on for miles.\nNobody remembers who built them.$"

Route20_Text_Route20Swimmer2Intro:
	.string "Almost there! Don't dawdle,\nthe tide's turning.$"

Route20_Text_Route20Swimmer2Defeat:
	.string "Out of breath.$"

Route20_Text_Route20Swimmer2After:
	.string "Land's End's gym is a pavilion\non pilings. Wear a raincoat.$"

@ --- end route trainers ---

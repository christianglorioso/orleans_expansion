Route15_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route15_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE15_HIKER, Route15_Text_Route15HikerIntro, Route15_Text_Route15HikerDefeat
	msgbox Route15_Text_Route15HikerAfter, MSGBOX_AUTOCLOSE
	end

Route15_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE15_LASS, Route15_Text_Route15LassIntro, Route15_Text_Route15LassDefeat
	msgbox Route15_Text_Route15LassAfter, MSGBOX_AUTOCLOSE
	end

Route15_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE15_GENTLEMAN, Route15_Text_Route15GentlemanIntro, Route15_Text_Route15GentlemanDefeat
	msgbox Route15_Text_Route15GentlemanAfter, MSGBOX_AUTOCLOSE
	end

Route15_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE15_CAMPER, Route15_Text_Route15CamperIntro, Route15_Text_Route15CamperDefeat
	msgbox Route15_Text_Route15CamperAfter, MSGBOX_AUTOCLOSE
	end

Route15_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE15_FISHERMAN, Route15_Text_Route15FishermanIntro, Route15_Text_Route15FishermanDefeat
	msgbox Route15_Text_Route15FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route15_Text_Route15HikerIntro:
	.string "Red earth, hot rock. I came\nsouth to hike it.$"

Route15_Text_Route15HikerDefeat:
	.string "Cooled off.$"

Route15_Text_Route15HikerAfter:
	.string "The mill's chimney smokes day\nand night. You can see it far off.$"

Route15_Text_Route15LassIntro:
	.string "Fairies like sugar. So do I.\nCare to battle?$"

Route15_Text_Route15LassDefeat:
	.string "Too sweet.$"

Route15_Text_Route15LassAfter:
	.string "The cane workers leave a little\nsugar out for the Ribombee.$"

Route15_Text_Route15GentlemanIntro:
	.string "A planter's life is quiet. A\nbattle is a pleasant change.$"

Route15_Text_Route15GentlemanDefeat:
	.string "Well fought.$"

Route15_Text_Route15GentlemanAfter:
	.string "I own the east field. Mind the\nrows. I count them.$"

Route15_Text_Route15CamperIntro:
	.string "The dry ground's a good place\nto pitch a tent. Or fight.$"

Route15_Text_Route15CamperDefeat:
	.string "Tent's flat.$"

Route15_Text_Route15CamperAfter:
	.string "Dust everywhere. The north is\nworse, they say.$"

Route15_Text_Route15FishermanIntro:
	.string "Irrigation ditches hold fish.\nDon't tell the planters.$"

Route15_Text_Route15FishermanDefeat:
	.string "Ditched.$"

Route15_Text_Route15FishermanAfter:
	.string "The ditches are cooler than\nthe river. The fish know.$"

@ --- end route trainers ---

@ --- mapgen: generated NPC scripts (begin) ---

Route15_EventScript_RouteSign1::
	msgbox Route15_Text_RouteSign1, MSGBOX_SIGN
	end

Route15_Text_RouteSign1:
	.string "SUNKEN CANE CO.\nHarvest burn at dusk. Mind smoke.$"

@ --- mapgen: generated NPC scripts (end) ---

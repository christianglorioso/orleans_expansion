Route19_MapScripts::
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route19_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE19_SAILOR, Route19_Text_Route19SailorIntro, Route19_Text_Route19SailorDefeat
	msgbox Route19_Text_Route19SailorAfter, MSGBOX_AUTOCLOSE
	end

Route19_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE19_FISHERMAN, Route19_Text_Route19FishermanIntro, Route19_Text_Route19FishermanDefeat
	msgbox Route19_Text_Route19FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route19_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE19_BIRD_KEEPER, Route19_Text_Route19BirdKeeperIntro, Route19_Text_Route19BirdKeeperDefeat
	msgbox Route19_Text_Route19BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route19_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE19_RANGER, Route19_Text_Route19RangerIntro, Route19_Text_Route19RangerDefeat
	msgbox Route19_Text_Route19RangerAfter, MSGBOX_AUTOCLOSE
	end

Route19_Text_Route19SailorIntro:
	.string "Low tide! The flats are mine\nuntil it turns back.$"

Route19_Text_Route19SailorDefeat:
	.string "Tide's turned.$"

Route19_Text_Route19SailorAfter:
	.string "A fossil hunter dug up the east\nflat last spring. Might be more.$"

Route19_Text_Route19FishermanIntro:
	.string "The flats drain, the fish gather.\nI gather the fish. And fights!$"

Route19_Text_Route19FishermanDefeat:
	.string "Off the hook.$"

Route19_Text_Route19FishermanAfter:
	.string "Mud holds secrets. Mostly mud.\nBut sometimes a fossil.$"

Route19_Text_Route19BirdKeeperIntro:
	.string "Shorebirds follow the tide. So\ndo I. Battle?$"

Route19_Text_Route19BirdKeeperDefeat:
	.string "Blown away.$"

Route19_Text_Route19BirdKeeperAfter:
	.string "The herons on Route 20 nest in\nthe old pilings. Don't startle them.$"

Route19_Text_Route19RangerIntro:
	.string "I ranger the delta. Nobody\ncrosses without a fight!$"

Route19_Text_Route19RangerDefeat:
	.string "Crossed.$"

Route19_Text_Route19RangerAfter:
	.string "Kabutops are older than the\ntown. They keep to the flats.$"

@ --- end route trainers ---

Route5_MapScripts::
	.byte 0

@ Route 5, the fishing lake west of Pointe Rouge. Chapter 4 beat 4.3: the fishing tournament. The angler at the shack runs it:
@   story < 19   the refinery runoff has spooked the fish; no tournament yet
@   story >= 19  enter: the Good Rod (free, once), the bite counter starts (VAR_TOURNEY_BASELINE), story 20
@   story 20     weigh-in: five bites since entering wins (the score is GAME_STAT_FISHING_ENCOUNTERS, see src/orleans_services.c),
@                FLAG_POINTE_TOURNEY_WON, and KINGFISHER will battle
@ Five trainers (levels 26-28) and two items (TM Agility, a hidden Sun Stone) are on the lake road.

Route5_EventScript_Npc2::
	lock
	faceplayer
	goto_if_set FLAG_POINTE_TOURNEY_WON, Route5_EventScript_AnglerWon
	goto_if_ge VAR_ORLEANS_STORY, 20, Route5_EventScript_Weighin
	goto_if_ge VAR_ORLEANS_STORY, 19, Route5_EventScript_AnglerOffer
	msgbox Route5_Text_AnglerSpooked, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_AnglerOffer:
	msgbox Route5_Text_AnglerOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route5_EventScript_AnglerNo
	goto_if_set FLAG_RECEIVED_GOOD_ROD, Route5_EventScript_AnglerStart
	msgbox Route5_Text_GoodRodGift, MSGBOX_DEFAULT
	giveitem ITEM_GOOD_ROD
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_GOOD_ROD
Route5_EventScript_AnglerStart:
	special OrleansSvc_SetFishingBaseline
	call_if_lt VAR_ORLEANS_STORY, 20, Route5_EventScript_SetStory20
	msgbox Route5_Text_AnglerRules, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_SetStory20:
	setvar VAR_ORLEANS_STORY, 20
	return

Route5_EventScript_AnglerNo:
	msgbox Route5_Text_AnglerNo, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_Weighin:
	special OrleansSvc_FishingBites
	copyvar VAR_0x8008, VAR_RESULT
	buffernumberstring STR_VAR_1, VAR_0x8008
	goto_if_ge VAR_0x8008, 5, Route5_EventScript_Winner
	msgbox Route5_Text_WeighinShort, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_Winner:
	msgbox Route5_Text_WeighinWin, MSGBOX_DEFAULT
	setflag FLAG_POINTE_TOURNEY_WON
	msgbox Route5_Text_WeighinKingfisher, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_AnglerWon:
	msgbox Route5_Text_AnglerAfter, MSGBOX_DEFAULT
	release
	end

Route5_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE5_FISHERMAN, Route5_Text_FishermanIntro, Route5_Text_FishermanDefeat
	msgbox Route5_Text_FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route5_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE5_LASS, Route5_Text_LassIntro, Route5_Text_LassDefeat
	msgbox Route5_Text_LassAfter, MSGBOX_AUTOCLOSE
	end

Route5_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE5_BIRD_KEEPER, Route5_Text_BirdKeeperIntro, Route5_Text_BirdKeeperDefeat
	msgbox Route5_Text_BirdKeeperAfter, MSGBOX_AUTOCLOSE
	end

Route5_EventScript_Trainer8::
	trainerbattle_single TRAINER_ORLEANS_ROUTE5_CAMPER, Route5_Text_CamperIntro, Route5_Text_CamperDefeat
	msgbox Route5_Text_CamperAfter, MSGBOX_AUTOCLOSE
	end

Route5_EventScript_Trainer9::
	trainerbattle_single TRAINER_ORLEANS_ROUTE5_PICNICKER, Route5_Text_PicnickerIntro, Route5_Text_PicnickerDefeat
	msgbox Route5_Text_PicnickerAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- text
Route5_Text_AnglerSpooked:
	.string "ANGLER: No tournament this year.\n"
	.string "The runoff from the refinery has\p"
	.string "the whole lake spooked. Not a\n"
	.string "bite since the smoke started.$"

Route5_Text_AnglerOffer:
	.string "ANGLER: The refinery's quiet and\n"
	.string "the fish are back. The annual\p"
	.string "fishing tournament is on!\n"
	.string "KINGFISHER only battles the winner.\p"
	.string "Want to enter?$"

Route5_Text_GoodRodGift:
	.string "ANGLER: Every entrant gets a\n"
	.string "proper rod. Take the GOOD ROD.$"

Route5_Text_AnglerRules:
	.string "ANGLER: The rules are simple.\n"
	.string "Fish the lake. The fish don't\p"
	.string "have to be big, they have to\n"
	.string "bite. Five bites wins.\p"
	.string "Then come back to me to weigh in.$"

Route5_Text_AnglerNo:
	.string "ANGLER: Think it over. The fish\n"
	.string "aren't going anywhere.$"

Route5_Text_WeighinShort:
	.string "{STR_VAR_1} so far. Not five yet.\n"
	.string "ANGLER: Back to the water!$"

Route5_Text_WeighinWin:
	.string "ANGLER: That's the tournament, and\n"
	.string "it's yours! {STR_VAR_1} bites!\p"
	.string "The fish gave you their vote.$"

Route5_Text_WeighinKingfisher:
	.string "ANGLER: KINGFISHER will see you at\n"
	.string "the boathouse in POINTE ROUGE.\p"
	.string "Fair warning. He fights the way\n"
	.string "he fishes. From above.$"

Route5_Text_AnglerAfter:
	.string "ANGLER: A winner's lake. Fish all\n"
	.string "you like.$"

Route5_Text_FishermanIntro:
	.string "I'm in the tournament. Not the\n"
	.string "battle one. But sure, why not!$"

Route5_Text_FishermanDefeat:
	.string "I should've stuck to fishing.$"

Route5_Text_FishermanAfter:
	.string "Whiscash like it by the reeds.\n"
	.string "Don't tell the others.$"

Route5_Text_LassIntro:
	.string "I came for the wildflowers, not\n"
	.string "the trainers! Fine, battle!$"

Route5_Text_LassDefeat:
	.string "My flowers will never forgive me.$"

Route5_Text_LassAfter:
	.string "Pretty, isn't it? Just don't\n"
	.string "stand in the reeds.$"

Route5_Text_BirdKeeperIntro:
	.string "My birds hunt over this lake.\n"
	.string "Tell them you're a fish!$"

Route5_Text_BirdKeeperDefeat:
	.string "My birds are embarrassed.$"

Route5_Text_BirdKeeperAfter:
	.string "KINGFISHER trained me, a little.\n"
	.string "I mostly learned to lose.$"

Route5_Text_CamperIntro:
	.string "A fisher on the pier, a trainer\n"
	.string "on the path. That's the rule!$"

Route5_Text_CamperDefeat:
	.string "No bites, no battles. Wow.$"

Route5_Text_CamperAfter:
	.string "I'm hoping for a Gyarados. Or a\n"
	.string "Magikarp. I'm not picky.$"

Route5_Text_PicnickerIntro:
	.string "The south path is mine! My\n"
	.string "POKéMON love the shallows!$"

Route5_Text_PicnickerDefeat:
	.string "Splash! Lost.$"

Route5_Text_PicnickerAfter:
	.string "If you go north, the pier stops\n"
	.string "at a very deep bit.$"

@ --- mapgen: generated NPC scripts (begin) ---

Route5_EventScript_SignCity::
	msgbox Route5_Text_SignCity, MSGBOX_SIGN
	end

Route5_Text_SignCity:
	.string "POINTE ROUGE\nCity limits: welcome!$"

Route5_EventScript_RouteSign1::
	msgbox Route5_Text_RouteSign1, MSGBOX_SIGN
	end

Route5_Text_RouteSign1:
	.string "ANGLER'S SHACK\nGood Rod for those who earn it.$"

Route5_EventScript_RouteSign2::
	msgbox Route5_Text_RouteSign2, MSGBOX_SIGN
	end

Route5_Text_RouteSign2:
	.string "REED BED\nSomething rare hides in the reeds.$"

@ --- mapgen: generated NPC scripts (end) ---

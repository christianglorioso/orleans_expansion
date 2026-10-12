PointeRouge_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_Gym_OnTransition
	.byte 0

@ Gym 4, the riverfront boathouse: Kingfisher (Tailwind, Flying). Reached after the Route 5 tournament (FLAG_POINTE_TOURNEY_WON).
@ The trial is the tailwind puzzle: two nets hang across the only gaps ((6, 7) and (14, 7)) in the net-rack wall in front of
@ Kingfisher's rafters. Three fans (bg events from story_overlay.py): west (6, 11), centre (10, 7, on the rack) and east
@ (14, 11). A tailwind needs them started IN ORDER, west, centre, east (VAR_POINTE_FAN_STEP counts 0-3); a wrong fan drops
@ the wind and the count restarts. The Fisherman's and the guide's lines give the order (west first, east last). When the
@ third fan catches, FLAG_POINTE_GYM_TAILWIND is set and both nets blow away (their objects are hidden by that flag). The
@ puzzle can never dead-end: the count restarts at 0 on every wrong press and every visit. A Fearowite lies in the rafters.

PointeRouge_Gym_OnTransition:
	call_if_unset FLAG_POINTE_GYM_TAILWIND, PointeRouge_Gym_EventScript_ResetFans
	end

PointeRouge_Gym_EventScript_ResetFans:
	setvar VAR_POINTE_FAN_STEP, 0
	return

PointeRouge_Gym_EventScript_FanWest::
	lockall
	goto_if_set FLAG_POINTE_GYM_TAILWIND, PointeRouge_Gym_EventScript_FanSteady
	goto_if_eq VAR_POINTE_FAN_STEP, 0, PointeRouge_Gym_EventScript_FanWestOn
	goto PointeRouge_Gym_EventScript_FanWrong

PointeRouge_Gym_EventScript_FanWestOn:
	setvar VAR_POINTE_FAN_STEP, 1
	msgbox PointeRouge_Gym_Text_FanWestOn, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Gym_EventScript_FanCentre::
	lockall
	goto_if_set FLAG_POINTE_GYM_TAILWIND, PointeRouge_Gym_EventScript_FanSteady
	goto_if_eq VAR_POINTE_FAN_STEP, 1, PointeRouge_Gym_EventScript_FanCentreOn
	goto PointeRouge_Gym_EventScript_FanWrong

PointeRouge_Gym_EventScript_FanCentreOn:
	setvar VAR_POINTE_FAN_STEP, 2
	msgbox PointeRouge_Gym_Text_FanCentreOn, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Gym_EventScript_FanEast::
	lockall
	goto_if_set FLAG_POINTE_GYM_TAILWIND, PointeRouge_Gym_EventScript_FanSteady
	goto_if_eq VAR_POINTE_FAN_STEP, 2, PointeRouge_Gym_EventScript_FanEastOn
	goto PointeRouge_Gym_EventScript_FanWrong

@ the third fan catches: the tailwind is up, both nets lift away
PointeRouge_Gym_EventScript_FanEastOn:
	setvar VAR_POINTE_FAN_STEP, 3
	setflag FLAG_POINTE_GYM_TAILWIND
	msgbox PointeRouge_Gym_Text_FanEastOn, MSGBOX_DEFAULT
	closemessage
	playse SE_M_GUST
	removeobject LOCALID_POINTE_ROUGE_GYM_NET4
	removeobject LOCALID_POINTE_ROUGE_GYM_NET5
	msgbox PointeRouge_Gym_Text_NetsAway, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Gym_EventScript_FanWrong:
	setvar VAR_POINTE_FAN_STEP, 0
	msgbox PointeRouge_Gym_Text_FanWrong, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Gym_EventScript_FanSteady:
	msgbox PointeRouge_Gym_Text_FanSteady, MSGBOX_DEFAULT
	releaseall
	end

PointeRouge_Gym_EventScript_Net4::
	msgbox PointeRouge_Gym_Text_Net, MSGBOX_NPC
	end

PointeRouge_Gym_EventScript_Net5::
	msgbox PointeRouge_Gym_Text_Net, MSGBOX_NPC
	end

@ the Fearowite: bag-full safe (the flag is only set once the stone is in the bag)
PointeRouge_Gym_EventScript_Fearowite6::
	lock
	giveitem ITEM_FEAROWITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_POINTE_ITEM_FEAROWITE
	removeobject LOCALID_POINTE_ROUGE_GYM_FEAROWITE6
	release
	end

PointeRouge_Gym_EventScript_GymGuide3::
	lock
	faceplayer
	goto_if_set FLAG_BADGE04_GET, PointeRouge_Gym_EventScript_GuideAfter
	goto_if_unset FLAG_POINTE_TOURNEY_WON, PointeRouge_Gym_EventScript_GuideTourney
	msgbox PointeRouge_Gym_Text_GuideHint, MSGBOX_DEFAULT
	release
	end

PointeRouge_Gym_EventScript_GuideTourney:
	msgbox PointeRouge_Gym_Text_GuideTourney, MSGBOX_DEFAULT
	release
	end

PointeRouge_Gym_EventScript_GuideAfter:
	msgbox PointeRouge_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

PointeRouge_Gym_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_POINTE_GYM_BIRD_KEEPER, PointeRouge_Gym_Text_BirdIntro, PointeRouge_Gym_Text_BirdDefeat
	msgbox PointeRouge_Gym_Text_BirdAfter, MSGBOX_AUTOCLOSE
	end

PointeRouge_Gym_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_POINTE_GYM_FISHERMAN, PointeRouge_Gym_Text_FishIntro, PointeRouge_Gym_Text_FishDefeat
	msgbox PointeRouge_Gym_Text_FishAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Kingfisher
@ Badge, story (never lowered) and the rewards: each reward has its own flag set only once the item is in the bag, so a full
@ bag can't lose it; talking to Kingfisher again retries.
PointeRouge_Gym_EventScript_Kingfisher0::
	lock
	faceplayer
	goto_if_set FLAG_BADGE04_GET, PointeRouge_Gym_EventScript_KingfisherAfter
	goto_if_unset FLAG_POINTE_TOURNEY_WON, PointeRouge_Gym_EventScript_KingfisherNoTourney
	trainerbattle_single TRAINER_KINGFISHER, PointeRouge_Gym_Text_KingfisherIntro, PointeRouge_Gym_Text_KingfisherDefeat, PointeRouge_Gym_EventScript_KingfisherDefeated, NO_MUSIC
	goto PointeRouge_Gym_EventScript_KingfisherAfter
	end

PointeRouge_Gym_EventScript_KingfisherNoTourney:
	msgbox PointeRouge_Gym_Text_KingfisherNoTourney, MSGBOX_DEFAULT
	release
	end

PointeRouge_Gym_EventScript_KingfisherDefeated::
	message PointeRouge_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE04_GET
	call_if_lt VAR_ORLEANS_STORY, 21, PointeRouge_Gym_EventScript_SetStory21
	msgbox PointeRouge_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call PointeRouge_Gym_EventScript_GiveRewards
	release
	end

PointeRouge_Gym_EventScript_SetStory21:
	setvar VAR_ORLEANS_STORY, 21
	return

PointeRouge_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_SUPER_ROD, PointeRouge_Gym_EventScript_RewardsDone
	goto_if_set FLAG_RECEIVED_TM_AERIAL_ACE, PointeRouge_Gym_EventScript_GiveSuperRod
	msgbox PointeRouge_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_AERIAL_ACE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_AERIAL_ACE
	msgbox PointeRouge_Gym_Text_AerialAceInfo, MSGBOX_DEFAULT
PointeRouge_Gym_EventScript_GiveSuperRod:
	giveitem ITEM_SUPER_ROD
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SUPER_ROD
	msgbox PointeRouge_Gym_Text_SuperRodInfo, MSGBOX_DEFAULT
	msgbox PointeRouge_Gym_Text_FourthVerse, MSGBOX_DEFAULT
PointeRouge_Gym_EventScript_RewardsDone:
	return

PointeRouge_Gym_EventScript_KingfisherAfter:
	call PointeRouge_Gym_EventScript_GiveRewards
	msgbox PointeRouge_Gym_Text_KingfisherPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
PointeRouge_Gym_Text_FanWestOn:
	.string "You thumb the west fan on. The\n"
	.string "sailcloth shivers. A thin breeze\p"
	.string "crosses the boathouse and quits.$"

PointeRouge_Gym_Text_FanCentreOn:
	.string "The centre fan, bolted to the net\n"
	.string "rack, spins up. The breeze grows\p"
	.string "teeth. It almost lifts the nets.$"

PointeRouge_Gym_Text_FanEastOn:
	.string "The east fan roars. Three gusts\n"
	.string "meet over the boat slips and\p"
	.string "become one steady TAILWIND!$"

PointeRouge_Gym_Text_NetsAway:
	.string "The wind lifts both nets clean out\n"
	.string "of the gaps. The rafters are open!$"

PointeRouge_Gym_Text_FanWrong:
	.string "The gust stumbles. The sailcloth\n"
	.string "goes slack. The wind is gone.\p"
	.string "All three fans wind down. Start\n"
	.string "again, in the right order.$"

PointeRouge_Gym_Text_FanSteady:
	.string "The fans hold a steady tailwind\n"
	.string "across the boathouse.$"

PointeRouge_Gym_Text_Net:
	.string "A heavy net hangs across the gap.\n"
	.string "A strong tailwind could lift it.$"

PointeRouge_Gym_Text_GuideTourney:
	.string "GUIDE: KINGFISHER doesn't battle\n"
	.string "just anyone. Win the fishing\p"
	.string "tournament on Route 5 first. The\n"
	.string "angler runs it. Once the refinery\p"
	.string "leak is stopped, that is.$"

PointeRouge_Gym_Text_GuideHint:
	.string "GUIDE: The boss waits in the\n"
	.string "rafters. Two nets bar the way.\p"
	.string "A tailwind lifts them. The east\n"
	.string "fan goes last, or the gust dies.$"

PointeRouge_Gym_Text_GuideAfter:
	.string "GUIDE: The boss has a way with\n"
	.string "the wind. And the river.$"

PointeRouge_Gym_Text_BirdIntro:
	.string "The boss said no one flies up\n"
	.string "here without a tailwind. So how\p"
	.string "did you get past the nets?$"

PointeRouge_Gym_Text_BirdDefeat:
	.string "You rode the wind better than\n"
	.string "my birds ever did.$"

PointeRouge_Gym_Text_BirdAfter:
	.string "The centre fan is the quiet one.\n"
	.string "It only wakes in the middle.$"

PointeRouge_Gym_Text_FishIntro:
	.string "Here for the boss? You fish a\n"
	.string "lot? I fish more. Battle!$"

PointeRouge_Gym_Text_FishDefeat:
	.string "Caught and released.$"

PointeRouge_Gym_Text_FishAfter:
	.string "The west fan starts any tailwind.\n"
	.string "Always. Everything begins in the\p"
	.string "west. That's the river's way.$"

PointeRouge_Gym_Text_KingfisherNoTourney:
	.string "KINGFISHER: Not yet. Win the\n"
	.string "tournament on Route 5, and then\p"
	.string "come up to my rafters. The river\n"
	.string "chooses who flies.$"

PointeRouge_Gym_Text_KingfisherIntro:
	.string "KINGFISHER: You flew up. Good. The\n"
	.string "first net, the first boat. The\p"
	.string "river is a road, and the wind is\n"
	.string "the hand on its back.\p"
	.string "I fight with both. TAILWIND first.\n"
	.string "Then everything else, faster.$"

PointeRouge_Gym_Text_KingfisherDefeat:
	.string "KINGFISHER: Faster than my wind.\n"
	.string "The river has chosen well.$"

PointeRouge_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the KINGFISHER\n"
	.string "BADGE from KINGFISHER.$"

PointeRouge_Gym_Text_BadgeInfo:
	.string "KINGFISHER: With that BADGE you can\n"
	.string "stand on the water, if you know\p"
	.string "how. The Rootkin do. Ask them.$"

PointeRouge_Gym_Text_TakeThis:
	.string "KINGFISHER: Take this. A gift from\n"
	.string "the rafters.$"

PointeRouge_Gym_Text_AerialAceInfo:
	.string "KINGFISHER: AERIAL ACE. It never\n"
	.string "misses. Neither does the river.$"

PointeRouge_Gym_Text_SuperRodInfo:
	.string "KINGFISHER: And a SUPER ROD. For\n"
	.string "the big ones under the bridges.$"

PointeRouge_Gym_Text_FourthVerse:
	.string "KINGFISHER: The fourth verse. The\n"
	.string "first net, the first boat.\p"
	.string "The river was never a wall. It\n"
	.string "was a road, and it carried the\p"
	.string "people home. Take that to TUPELO.\n"
	.string "He'll know the Old Water's tune.$"

PointeRouge_Gym_Text_KingfisherPost:
	.string "KINGFISHER: The tailwind's yours,\n"
	.string "and the road with it. Visit the\p"
	.string "Old Water. The Rootkin keep what\n"
	.string "this river forgot.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

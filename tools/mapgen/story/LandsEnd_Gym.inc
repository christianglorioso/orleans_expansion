LandsEnd_Gym_MapScripts::
	.byte 0

@ Gym 8, the Rain Pavilion (Chapter 8): Heron (Rain: Drizzle on Pelipper and Politoed, a Mega Gyarados). The trial: seven carved panels
@ hold the seven verses the player has heard, shuffled; touching them in the order of the telling (1 to 7) ends the rain
@ (FLAG_HERON_TRIAL_DONE); a wrong one resets the count (VAR_HERON_PANELS). Heron won't battle until then. Story 36 + badge 8 + TM Scald +
@ Gyaradosite + Diving Gear (each with its own flag, bag-full safe) + the eighth verse come after the battle. Route 21's barge goes with the badge.

LandsEnd_Gym_EventScript_GymGuide3::
	lock
	faceplayer
	goto_if_set FLAG_BADGE08_GET, LandsEnd_Gym_EventScript_GuideBeaten
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_GuideAfter
	msgbox LandsEnd_Gym_Text_GuideBefore, MSGBOX_DEFAULT
	release
	end

LandsEnd_Gym_EventScript_GuideAfter:
	msgbox LandsEnd_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

LandsEnd_Gym_EventScript_GuideBeaten:
	msgbox LandsEnd_Gym_Text_GuideBeaten, MSGBOX_DEFAULT
	release
	end

LandsEnd_Gym_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_LANDS_END_GYM_SWIMMER, LandsEnd_Gym_Text_SwimmerIntro, LandsEnd_Gym_Text_SwimmerDefeat
	msgbox LandsEnd_Gym_Text_SwimmerAfter, MSGBOX_AUTOCLOSE
	end

LandsEnd_Gym_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_LANDS_END_GYM_FISHERMAN, LandsEnd_Gym_Text_FishermanIntro, LandsEnd_Gym_Text_FishermanDefeat
	msgbox LandsEnd_Gym_Text_FishermanAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- the verse panels
LandsEnd_Gym_EventScript_PanelA1::
LandsEnd_Gym_EventScript_PanelA2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse4, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 3, LandsEnd_Gym_EventScript_Right4
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelB1::
LandsEnd_Gym_EventScript_PanelB2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse1, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 0, LandsEnd_Gym_EventScript_Right1
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelC1::
LandsEnd_Gym_EventScript_PanelC2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse6, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 5, LandsEnd_Gym_EventScript_Right6
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelD1::
LandsEnd_Gym_EventScript_PanelD2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse2, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 1, LandsEnd_Gym_EventScript_Right2
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelE1::
LandsEnd_Gym_EventScript_PanelE2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse7, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 6, LandsEnd_Gym_EventScript_Right7
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelF1::
LandsEnd_Gym_EventScript_PanelF2::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse3, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 2, LandsEnd_Gym_EventScript_Right3
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_PanelG1::
LandsEnd_Gym_EventScript_PanelG2::
LandsEnd_Gym_EventScript_PanelG3::
	lockall
	goto_if_set FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_PanelDone
	msgbox LandsEnd_Gym_Text_Verse5, MSGBOX_DEFAULT
	goto_if_eq VAR_HERON_PANELS, 4, LandsEnd_Gym_EventScript_Right5
	goto LandsEnd_Gym_EventScript_PanelWrong

LandsEnd_Gym_EventScript_Right1:
	setvar VAR_HERON_PANELS, 1
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right2:
	setvar VAR_HERON_PANELS, 2
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right3:
	setvar VAR_HERON_PANELS, 3
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right4:
	setvar VAR_HERON_PANELS, 4
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right5:
	setvar VAR_HERON_PANELS, 5
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right6:
	setvar VAR_HERON_PANELS, 6
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_Click, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_Right7:
	setvar VAR_HERON_PANELS, 7
	setflag FLAG_HERON_TRIAL_DONE
	playse SE_PIN
	msgbox LandsEnd_Gym_Text_RainPauses, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_PanelWrong:
	setvar VAR_HERON_PANELS, 0
	playse SE_FAILURE
	msgbox LandsEnd_Gym_Text_Wrong, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_Gym_EventScript_PanelDone:
	msgbox LandsEnd_Gym_Text_PanelDone, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- Heron
LandsEnd_Gym_EventScript_Heron0::
	lock
	faceplayer
	goto_if_set FLAG_BADGE08_GET, LandsEnd_Gym_EventScript_HeronAfter
	goto_if_unset FLAG_HERON_TRIAL_DONE, LandsEnd_Gym_EventScript_HeronNotYet
	trainerbattle_single TRAINER_HERON, LandsEnd_Gym_Text_HeronIntro, LandsEnd_Gym_Text_HeronDefeat, LandsEnd_Gym_EventScript_HeronDefeated, NO_MUSIC
	goto LandsEnd_Gym_EventScript_HeronAfter
	end

LandsEnd_Gym_EventScript_HeronNotYet:
	msgbox LandsEnd_Gym_Text_NotYet, MSGBOX_DEFAULT
	release
	end

LandsEnd_Gym_EventScript_HeronDefeated::
	message LandsEnd_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE08_GET
	call_if_eq VAR_ORLEANS_STORY, 35, LandsEnd_Gym_EventScript_SetStory36
	msgbox LandsEnd_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call LandsEnd_Gym_EventScript_GiveRewards
	release
	end

LandsEnd_Gym_EventScript_SetStory36:
	setvar VAR_ORLEANS_STORY, 36
	return

@ The TM, the stone and the gear each have their own flag (set once really in the bag), so a full bag can't lose them; Heron retries on a talk.
LandsEnd_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_TM082_SCALD, LandsEnd_Gym_EventScript_StoneReward
	msgbox LandsEnd_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_SCALD
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM082_SCALD
	msgbox LandsEnd_Gym_Text_ScaldInfo, MSGBOX_DEFAULT
	msgbox LandsEnd_Gym_Text_EighthVerse, MSGBOX_DEFAULT
LandsEnd_Gym_EventScript_StoneReward:
	goto_if_set FLAG_RECEIVED_GYARADOSITE, LandsEnd_Gym_EventScript_GearReward
	msgbox LandsEnd_Gym_Text_TakeThisToo, MSGBOX_DEFAULT
	giveitem ITEM_GYARADOSITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_GYARADOSITE
	msgbox LandsEnd_Gym_Text_StoneInfo, MSGBOX_DEFAULT
LandsEnd_Gym_EventScript_GearReward:
	goto_if_set FLAG_RECEIVED_DIVING_GEAR, LandsEnd_Gym_EventScript_RewardsDone
	msgbox LandsEnd_Gym_Text_TakeThisThree, MSGBOX_DEFAULT
	giveitem ITEM_DIVING_GEAR
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_DIVING_GEAR
	msgbox LandsEnd_Gym_Text_GearInfo, MSGBOX_DEFAULT
LandsEnd_Gym_EventScript_RewardsDone:
	return

LandsEnd_Gym_EventScript_HeronAfter:
	call LandsEnd_Gym_EventScript_GiveRewards
	msgbox LandsEnd_Gym_Text_HeronPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
LandsEnd_Gym_Text_Verse1:
	.string "Carved on the panel:\n"
	.string "The water rose, and the land was\p"
	.string "afraid. The people built walls\n"
	.string "against what they did not know.$"

LandsEnd_Gym_Text_Verse2:
	.string "Carved on the panel:\n"
	.string "The sky split open, and light ran\p"
	.string "down the wires of the world. The\n"
	.string "Long One lay down in the river bed,\p"
	.string "and the people heard it sing.$"

LandsEnd_Gym_Text_Verse3:
	.string "Carved on the panel:\n"
	.string "Lamps burned over the water to lead\p"
	.string "the drowned home. The Long One\n"
	.string "kept every one of them lit.$"

LandsEnd_Gym_Text_Verse4:
	.string "Carved on the panel:\n"
	.string "The first net, the first boat. The\p"
	.string "river was a road, and a gift. The\n"
	.string "wind carried the songs along it.$"

LandsEnd_Gym_Text_Verse5:
	.string "Carved on the panel:\n"
	.string "The people ate together, and the\p"
	.string "land was fed. A tie, they said:\n"
	.string "no pot is greater than the table.$"

LandsEnd_Gym_Text_Verse6:
	.string "Carved on the panel:\n"
	.string "What the water shows is not the\p"
	.string "water. The Long One only looked\n"
	.string "drowned. It was keeping watch.$"

LandsEnd_Gym_Text_Verse7:
	.string "Carved on the panel:\n"
	.string "The field burned and the people\p"
	.string "wept. Then the green came back\n"
	.string "through the ash, taller than before.$"

LandsEnd_Gym_Text_Click:
	.string "The panel hums, and slides a finger\n"
	.string "into the wall. The rain eases a bit.$"

LandsEnd_Gym_Text_Wrong:
	.string "The panel goes dark. The rain comes\n"
	.string "back hard, and every panel resets.$"

LandsEnd_Gym_Text_RainPauses:
	.string "The seventh panel clicks. All seven\n"
	.string "glow, and the rain over the pavilion\p"
	.string "stops, mid-drop. HERON waits on her\n"
	.string "platform.$"

LandsEnd_Gym_Text_PanelDone:
	.string "The panels glow softly. The rain\n"
	.string "has paused.$"

LandsEnd_Gym_Text_GuideBefore:
	.string "GUIDE: Seven panels, seven verses.\n"
	.string "Touch them in the telling's order.\p"
	.string "GUIDE: Get one wrong and the rain\n"
	.string "starts over. You know the verses.$"

LandsEnd_Gym_Text_GuideAfter:
	.string "GUIDE: The rain stopped for you.\n"
	.string "It does that for very few.$"

LandsEnd_Gym_Text_GuideBeaten:
	.string "GUIDE: Eight verses. The telling is\n"
	.string "whole. Mind what ANDREW says.$"

LandsEnd_Gym_Text_SwimmerIntro:
	.string "I swim the pavilion's moat. It's\n"
	.string "small. I'm very good at it.$"

LandsEnd_Gym_Text_SwimmerDefeat:
	.string "Out of my depth.$"

LandsEnd_Gym_Text_SwimmerAfter:
	.string "The panels teach order. The moat\n"
	.string "teaches patience.$"

LandsEnd_Gym_Text_FishermanIntro:
	.string "I fish the moat. Nothing bites.\n"
	.string "I'll fish for a battle instead.$"

LandsEnd_Gym_Text_FishermanDefeat:
	.string "Snapped.$"

LandsEnd_Gym_Text_FishermanAfter:
	.string "HERON's rain feeds the moat. I\n"
	.string "feed the herons. Fair trade.$"

LandsEnd_Gym_Text_NotYet:
	.string "HERON: The rain won't pause for the\n"
	.string "unready. Touch the verses in order.\p"
	.string "HERON: Seven panels. You know them.\n"
	.string "Come back when the rain has stopped.$"

LandsEnd_Gym_Text_HeronIntro:
	.string "HERON: You put the verses in order.\n"
	.string "Most people argue with the rain.\p"
	.string "HERON: Rain is my team's best\n"
	.string "friend. Let's see yours.$"

LandsEnd_Gym_Text_HeronDefeat:
	.string "HERON: Dry at last. Take your badge.$"

LandsEnd_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the TIDE BADGE\n"
	.string "from HERON.$"

LandsEnd_Gym_Text_BadgeInfo:
	.string "HERON: With that BADGE, every\n"
	.string "POKéMON obeys you, and the rain\p"
	.string "stops minding you. The last of the\n"
	.string "eight.$"

LandsEnd_Gym_Text_TakeThis:
	.string "HERON: Take this. A little rain\n"
	.string "of my own.$"

LandsEnd_Gym_Text_ScaldInfo:
	.string "HERON: SCALD. Water that burns.\n"
	.string "Careful where you aim it.$"

LandsEnd_Gym_Text_EighthVerse:
	.string "HERON: And the eighth verse, the\n"
	.string "last. The Long One lay down to\p"
	.string "guard, not to die. It sleeps so the\n"
	.string "water will not run wild. When the\p"
	.string "storm comes again, the song wakes\n"
	.string "it. And the song calms it.$"

LandsEnd_Gym_Text_TakeThisToo:
	.string "HERON: And this. My GYARADOSITE.\n"
	.string "It was my mother's. Use it kindly.$"

LandsEnd_Gym_Text_StoneInfo:
	.string "HERON: Hold it on a GYARADOS and the\n"
	.string "Cypress Charm does the rest.$"

LandsEnd_Gym_Text_TakeThisThree:
	.string "HERON: And the DIVING GEAR, for the\n"
	.string "Gulf. The temple's door is a hollow\p"
	.string "shaped like a song. You know the\n"
	.string "song.$"

LandsEnd_Gym_Text_GearInfo:
	.string "The wrecked barge and the wall of\n"
	.string "rain on Route 21 are gone. The last\p"
	.string "verse did that. Nobody warns you\n"
	.string "songs do things.$"

LandsEnd_Gym_Text_HeronPost:
	.string "HERON: Go out when the rain is\n"
	.string "ready. It listens to you now.$"


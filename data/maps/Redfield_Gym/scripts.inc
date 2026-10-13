Redfield_Gym_MapScripts::
	.byte 0

@ Gym 7, the sugar mill (Chapter 7): Cayenne (Sun: Ninetales' Drought, Mega Charizard Y). The trial is the mill yard outside (by day:
@ Redfield.inc); the shutter on the door's approach cell keeps the gym shut until the three sundials burn. Story 33 + badge 7 + TM Overheat
@ (flag-guarded, bag-full safe) + Charizardite Y (own flag) + verse 7. Story 32 (Rita beaten) is needed.

Redfield_Gym_EventScript_GymGuide3::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, Redfield_Gym_EventScript_GuideAfter
	msgbox Redfield_Gym_Text_GuideBefore, MSGBOX_DEFAULT
	release
	end

Redfield_Gym_EventScript_GuideAfter:
	msgbox Redfield_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

Redfield_Gym_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_REDFIELD_GYM_KINDLER, Redfield_Gym_Text_KindlerIntro, Redfield_Gym_Text_KindlerDefeat
	msgbox Redfield_Gym_Text_KindlerAfter, MSGBOX_AUTOCLOSE
	end

Redfield_Gym_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_REDFIELD_GYM_CANE_CUTTER, Redfield_Gym_Text_CutterIntro, Redfield_Gym_Text_CutterDefeat
	msgbox Redfield_Gym_Text_CutterAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Cayenne
Redfield_Gym_EventScript_Cayenne0::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, Redfield_Gym_EventScript_CayenneAfter
	goto_if_lt VAR_ORLEANS_STORY, 32, Redfield_Gym_EventScript_CayenneNotYet
	trainerbattle_single TRAINER_CAYENNE, Redfield_Gym_Text_CayenneIntro, Redfield_Gym_Text_CayenneDefeat, Redfield_Gym_EventScript_CayenneDefeated, NO_MUSIC
	goto Redfield_Gym_EventScript_CayenneAfter
	end

Redfield_Gym_EventScript_CayenneNotYet:
	msgbox Redfield_Gym_Text_NotYet, MSGBOX_DEFAULT
	release
	end

Redfield_Gym_EventScript_CayenneDefeated::
	message Redfield_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE07_GET
	call_if_eq VAR_ORLEANS_STORY, 32, Redfield_Gym_EventScript_SetStory33
	msgbox Redfield_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call Redfield_Gym_EventScript_GiveRewards
	release
	end

Redfield_Gym_EventScript_SetStory33:
	setvar VAR_ORLEANS_STORY, 33
	return

@ The TM and the stone have their own flags (each set once it is really in the bag), so a full bag can't lose them; talking to
@ Cayenne again retries.
Redfield_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_TM050_OVERHEAT, Redfield_Gym_EventScript_StoneReward
	msgbox Redfield_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_OVERHEAT
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM050_OVERHEAT
	msgbox Redfield_Gym_Text_OverheatInfo, MSGBOX_DEFAULT
	msgbox Redfield_Gym_Text_SeventhVerse, MSGBOX_DEFAULT
Redfield_Gym_EventScript_StoneReward:
	goto_if_set FLAG_RECEIVED_CHARIZARDITE_Y, Redfield_Gym_EventScript_RewardsDone
	msgbox Redfield_Gym_Text_TakeThisToo, MSGBOX_DEFAULT
	giveitem ITEM_CHARIZARDITE_Y
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_CHARIZARDITE_Y
	goto_if_set FLAG_RECEIVED_CYPRESS_CHARM, Redfield_Gym_EventScript_StoneInfoOwned
	msgbox Redfield_Gym_Text_StoneInfoNoCharm, MSGBOX_DEFAULT
	goto Redfield_Gym_EventScript_StoneInfoDone
Redfield_Gym_EventScript_StoneInfoOwned:
	msgbox Redfield_Gym_Text_StoneInfo, MSGBOX_DEFAULT
Redfield_Gym_EventScript_StoneInfoDone:
	msgbox Redfield_Gym_Text_Span, MSGBOX_DEFAULT
Redfield_Gym_EventScript_RewardsDone:
	return

Redfield_Gym_EventScript_CayenneAfter:
	call Redfield_Gym_EventScript_GiveRewards
	msgbox Redfield_Gym_Text_CayennePost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
Redfield_Gym_Text_GuideBefore:
	.string "GUIDE: The sundials answered you.\n"
	.string "The mill runs on that, and CAYENNE.$"

Redfield_Gym_Text_GuideAfter:
	.string "GUIDE: Seventh verse. The cane came\n"
	.string "back. It always does.$"

Redfield_Gym_Text_KindlerIntro:
	.string "The furnace floor is hot. So am I!\n"
	.string "Battle?$"

Redfield_Gym_Text_KindlerDefeat:
	.string "Burned out.$"

Redfield_Gym_Text_KindlerAfter:
	.string "CAYENNE's Ninetales brings the sun\n"
	.string "on its own. Bring a cold answer.$"

Redfield_Gym_Text_CutterIntro:
	.string "I cut cane ten hours a day. I'm\n"
	.string "not afraid of a fight.$"

Redfield_Gym_Text_CutterDefeat:
	.string "Cut down.$"

Redfield_Gym_Text_CutterAfter:
	.string "Sun's the boss in here. Mind your\n"
	.string "Water types.$"

Redfield_Gym_Text_CayenneIntro:
	.string "CAYENNE: You read the sun. Good.\n"
	.string "Now let's see if you stand heat.\p"
	.string "CAYENNE: My POKéMON learned from\n"
	.string "fire, and from the green after.$"

Redfield_Gym_Text_CayenneDefeat:
	.string "CAYENNE: Ha! Bright. Brighter than\n"
	.string "my mill. Take your badge.$"

Redfield_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the EMBER BADGE\n"
	.string "from CAYENNE.$"

Redfield_Gym_Text_BadgeInfo:
	.string "CAYENNE: With that BADGE, you stand\n"
	.string "heat that wilts others.\p"
	.string "Nor will you mind a long, bright\n"
	.string "day.$"

Redfield_Gym_Text_TakeThis:
	.string "CAYENNE: Take this. It's hot, so\n"
	.string "handle it with care.$"

Redfield_Gym_Text_OverheatInfo:
	.string "CAYENNE: OVERHEAT. Hits hard, then\n"
	.string "costs you for it. Like cane work.$"

Redfield_Gym_Text_SeventhVerse:
	.string "CAYENNE: And the seventh verse. The\n"
	.string "field burned, and the people wept.\p"
	.string "Then the green came back through\n"
	.string "the ash, taller than before.\p"
	.string "Take it to TUPELO. Songs are for\n"
	.string "sharing.$"

Redfield_Gym_Text_TakeThisToo:
	.string "CAYENNE: And this. My grandfather's\n"
	.string "CHARIZARDITE Y. It sat in a mill\p"
	.string "drawer with the sun on it every\n"
	.string "day. It's still warm.$"

Redfield_Gym_Text_StoneInfo:
	.string "CAYENNE: Hold it on a CHARIZARD and\n"
	.string "the Cypress Charm will do the rest.$"

Redfield_Gym_Text_StoneInfoNoCharm:
	.string "CAYENNE: Without the charm from the\n"
	.string "OLD WATER's carver it's a stone.$"

Redfield_Gym_Text_Span:
	.string "CAYENNE: The fallen span on Route 18\n"
	.string "stood on the old mill's stone. The\p"
	.string "verse shook it loose. It'll clear.\n"
	.string "And someone's looking for you: a\p"
	.string "girl outside, in a hurry. Go.$"

Redfield_Gym_Text_CayennePost:
	.string "CAYENNE: Go. The sun's on your side\n"
	.string "today. Don't waste it.$"

Redfield_Gym_Text_NotYet:
	.string "CAYENNE: RITA keeps the books at\n"
	.string "the gate. Settle that first.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

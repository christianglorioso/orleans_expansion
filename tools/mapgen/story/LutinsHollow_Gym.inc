LutinsHollow_Gym_MapScripts::
	.byte 0

@ Gym 6, the moss curtains: Lutin (Fairy). The trial is to find the real Lutin among four in the alcoves (x 5, 10, 15, 19). Three still
@ pools lie below the first three alcoves (bg events at (5, 9), (10, 9), (15, 9): stand above one and press A facing down): the pools of
@ the illusions show no reflection, the third (below the real Lutin at (15, 4)) shows one. The fourth alcove has no pool (a false one by
@ elimination). Talking to a false Lutin sends the player back to the door (warpsilent); the real one battles. Two trainers (a Lass and
@ a Psychic) stand in the hall. Rewards: badge 6, story 29 (never lowered: set only from 28, the usher keeps the gym shut until then),
@ verse 6, TM Dazzling Gleam (flag-guarded, bag-full safe); the Route 14 floodwater recedes (the Crescent gate keys on FLAG_BADGE06_GET).

LutinsHollow_Gym_EventScript_Pool1::
	msgbox LutinsHollow_Gym_Text_PoolEmpty, MSGBOX_SIGN
	end

LutinsHollow_Gym_EventScript_Pool2::
	msgbox LutinsHollow_Gym_Text_PoolEmpty, MSGBOX_SIGN
	end

LutinsHollow_Gym_EventScript_Pool3::
	msgbox LutinsHollow_Gym_Text_PoolReflection, MSGBOX_SIGN
	end

LutinsHollow_Gym_EventScript_ALutin0::
	goto LutinsHollow_Gym_EventScript_FalseLutin

LutinsHollow_Gym_EventScript_ALutin1::
	goto LutinsHollow_Gym_EventScript_FalseLutin

LutinsHollow_Gym_EventScript_ALutin3::
	goto LutinsHollow_Gym_EventScript_FalseLutin

@ an illusion: it unravels into moss and the player is carried back to the door
LutinsHollow_Gym_EventScript_FalseLutin:
	lockall
	goto_if_set FLAG_BADGE06_GET, LutinsHollow_Gym_EventScript_FalseLutinSpent
	msgbox LutinsHollow_Gym_Text_FalseLutin, MSGBOX_DEFAULT
	closemessage
	playse SE_PIN
	fadescreen FADE_TO_BLACK
	warpsilent MAP_LUTINS_HOLLOW_GYM, 10, 14
	waitstate
	releaseall
	end

LutinsHollow_Gym_EventScript_FalseLutinSpent:
	msgbox LutinsHollow_Gym_Text_FalseLutinSpent, MSGBOX_DEFAULT
	releaseall
	end

LutinsHollow_Gym_EventScript_GymGuide6::
	lock
	faceplayer
	goto_if_set FLAG_BADGE06_GET, LutinsHollow_Gym_EventScript_GuideAfter
	msgbox LutinsHollow_Gym_Text_GuideHint, MSGBOX_DEFAULT
	release
	end

LutinsHollow_Gym_EventScript_GuideAfter:
	msgbox LutinsHollow_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

LutinsHollow_Gym_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_HOLLOW_GYM_LASS, LutinsHollow_Gym_Text_LassIntro, LutinsHollow_Gym_Text_LassDefeat
	msgbox LutinsHollow_Gym_Text_LassAfter, MSGBOX_AUTOCLOSE
	end

LutinsHollow_Gym_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_HOLLOW_GYM_PSYCHIC, LutinsHollow_Gym_Text_PsychicIntro, LutinsHollow_Gym_Text_PsychicDefeat
	msgbox LutinsHollow_Gym_Text_PsychicAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Lutin
LutinsHollow_Gym_EventScript_TheReal2::
	lock
	faceplayer
	goto_if_set FLAG_BADGE06_GET, LutinsHollow_Gym_EventScript_LutinAfter
	trainerbattle_single TRAINER_LUTIN, LutinsHollow_Gym_Text_LutinIntro, LutinsHollow_Gym_Text_LutinDefeat, LutinsHollow_Gym_EventScript_LutinDefeated, NO_MUSIC
	goto LutinsHollow_Gym_EventScript_LutinAfter
	end

LutinsHollow_Gym_EventScript_LutinDefeated::
	message LutinsHollow_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE06_GET
	call_if_eq VAR_ORLEANS_STORY, 28, LutinsHollow_Gym_EventScript_SetStory29
	msgbox LutinsHollow_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call LutinsHollow_Gym_EventScript_GiveRewards
	release
	end

LutinsHollow_Gym_EventScript_SetStory29:
	setvar VAR_ORLEANS_STORY, 29
	return

LutinsHollow_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_TM_DAZZLING_GLEAM, LutinsHollow_Gym_EventScript_RewardsDone
	msgbox LutinsHollow_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_DAZZLING_GLEAM
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_DAZZLING_GLEAM
	msgbox LutinsHollow_Gym_Text_GleamInfo, MSGBOX_DEFAULT
	msgbox LutinsHollow_Gym_Text_SixthVerse, MSGBOX_DEFAULT
	msgbox LutinsHollow_Gym_Text_Flood, MSGBOX_DEFAULT
LutinsHollow_Gym_EventScript_RewardsDone:
	return

LutinsHollow_Gym_EventScript_LutinAfter:
	call LutinsHollow_Gym_EventScript_GiveRewards
	msgbox LutinsHollow_Gym_Text_LutinPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
LutinsHollow_Gym_Text_PoolEmpty:
	.string "A still pool, black and clear. The\n"
	.string "moss above it is bright, and the\p"
	.string "water shows no one. Not the\n"
	.string "alcove, not the figure in it. Not\p"
	.string "you.$"

LutinsHollow_Gym_Text_PoolReflection:
	.string "A still pool. In it, upside down,\n"
	.string "the alcove above. A woman with\p"
	.string "moss-green hair stands in it,\n"
	.string "casting a perfect reflection.$"

LutinsHollow_Gym_Text_FalseLutin:
	.string "The LUTIN smiles, bows, and comes\n"
	.string "apart like wet moss. A hundred\p"
	.string "green threads fall away, and the\n"
	.string "curtains carry you back to the door.$"

LutinsHollow_Gym_Text_FalseLutinSpent:
	.string "The false LUTIN only smiles, a green\n"
	.string "thread of moss. It lets you pass.$"

LutinsHollow_Gym_Text_GuideHint:
	.string "GUIDE: Four LUTINS stand behind the\n"
	.string "moss, and only one is real. The\p"
	.string "illusions forget themselves. Look\n"
	.string "in the pools. The water never lies.$"

LutinsHollow_Gym_Text_GuideAfter:
	.string "GUIDE: You found her. Most people\n"
	.string "argue with the moss.$"

LutinsHollow_Gym_Text_LassIntro:
	.string "I tend the curtains. Pretty, but\n"
	.string "they hide things. Battle?$"

LutinsHollow_Gym_Text_LassDefeat:
	.string "You parted the curtains.$"

LutinsHollow_Gym_Text_LassAfter:
	.string "Don't trust the ones without a\n"
	.string "reflection. I trusted one once.$"

LutinsHollow_Gym_Text_PsychicIntro:
	.string "Your mind is an open door. Let me\n"
	.string "walk through it. With POKéMON.$"

LutinsHollow_Gym_Text_PsychicDefeat:
	.string "A closed door after all.$"

LutinsHollow_Gym_Text_PsychicAfter:
	.string "The pools think. They think\n"
	.string "slowly. They remember.$"

LutinsHollow_Gym_Text_LutinIntro:
	.string "LUTIN: You didn't argue with the\n"
	.string "moss. Good. Most do.\p"
	.string "What the water shows is not the\n"
	.string "water. Remember that. Now show me\p"
	.string "what's real about you.$"

LutinsHollow_Gym_Text_LutinDefeat:
	.string "LUTIN: Real. Every bit of it.\n"
	.string "The water agrees.$"

LutinsHollow_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the REFLECTION\n"
	.string "BADGE from LUTIN.$"

LutinsHollow_Gym_Text_BadgeInfo:
	.string "LUTIN: With that BADGE, the hollow's\n"
	.string "illusions won't fool you again.\p"
	.string "Nor the ones people tell about\n"
	.string "themselves.$"

LutinsHollow_Gym_Text_TakeThis:
	.string "LUTIN: Take this. A gift from the\n"
	.string "moss.$"

LutinsHollow_Gym_Text_GleamInfo:
	.string "LUTIN: DAZZLING GLEAM. Light that\n"
	.string "tells the truth, scattered wide.$"

LutinsHollow_Gym_Text_SixthVerse:
	.string "LUTIN: And the sixth verse. What\n"
	.string "the water shows is not the water.\p"
	.string "The Long One only looked drowned.\n"
	.string "Take it to TUPELO. He has a gift\p"
	.string "that waits for it.$"

LutinsHollow_Gym_Text_Flood:
	.string "LUTIN: And the water on the levee\n"
	.string "road, south of CRESCENT CITY, has\p"
	.string "gone down. The sixth verse did that.\n"
	.string "Nobody warns you songs do things.$"

LutinsHollow_Gym_Text_LutinPost:
	.string "LUTIN: Go back to the OLD WATER.\n"
	.string "TUPELO will give you what you've\p"
	.string "earned. Mind the reflection.\n"
	.string "It's usually right.$"

@ Orleans trophies: rewards that could not be handed over when the trophy was earned (the bag was full) wait for Lafayette.
@ Called from his Conservation Center script right after he turns to the player. Achievement_ClaimNextReward (src/achievements.c) gives the
@ next waiting reward: VAR_RESULT 0 = nothing waiting, 1 = given (STR_VAR_4 holds the line to show), 2 = the bag is still full.
Common_EventScript_AchievementRewards::
	special Achievement_CheckAllSpecial
	special Achievement_ClaimNextReward
	goto_if_eq VAR_RESULT, 0, Common_EventScript_AchievementRewards_None
	goto_if_eq VAR_RESULT, 2, Common_EventScript_AchievementRewards_BagFull
	msgbox Common_Text_AchievementRewardsIntro, MSGBOX_DEFAULT
Common_EventScript_AchievementRewards_Give:
	playfanfare MUS_OBTAIN_ITEM
	msgbox gStringVar4, MSGBOX_DEFAULT
	waitfanfare
	special Achievement_ClaimNextReward
	goto_if_eq VAR_RESULT, 1, Common_EventScript_AchievementRewards_Give
	goto_if_eq VAR_RESULT, 2, Common_EventScript_AchievementRewards_BagFull
Common_EventScript_AchievementRewards_None:
	return

Common_EventScript_AchievementRewards_BagFull:
	msgbox Common_Text_AchievementRewardsBagFull, MSGBOX_DEFAULT
	return

Common_Text_AchievementRewardsIntro:
	.string "LAFAYETTE: Ah, there you are! Your\n"
	.string "trophies have been piling up.\p"
	.string "I kept a few of the prizes safe\n"
	.string "for you.$"

Common_Text_AchievementRewardsBagFull:
	.string "LAFAYETTE: Your BAG is full! Make\n"
	.string "some room and come see me again.\p"
	.string "I'm holding the rest of your\n"
	.string "trophy prizes.$"

@ Lair gates (tools/mapgen/lair_gates.py, story_data_lairs.GATES): a legendary lair opens only when its trophy is complete AND the game is beaten (story 45).
@ In: VAR_0x8004 = the trophy id (ACH_*). Out: VAR_RESULT = TRUE when the lair is open. Re-polls the trophies, so one earned elsewhere counts at once.
LairGate_EventScript_Check::
	setvar VAR_RESULT, FALSE
	goto_if_lt VAR_ORLEANS_STORY, 45, LairGate_EventScript_CheckDone
	special Achievement_CheckUnlockedVar8004
LairGate_EventScript_CheckDone:
	return

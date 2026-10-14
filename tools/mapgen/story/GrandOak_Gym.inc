GrandOak_Gym_MapScripts::
	.byte 0

@ step 9: the hedge maze trainers and Magnolia
GrandOak_Gym_EventScript_Gardener1::
	trainerbattle_single TRAINER_ORLEANS_GRAND_OAK_GYM_RANGER, GrandOak_Gym_Text_RangerIntro, GrandOak_Gym_Text_RangerDefeat
	msgbox GrandOak_Gym_Text_RangerAfter, MSGBOX_AUTOCLOSE
	end

GrandOak_Gym_EventScript_AromaLady2::
	trainerbattle_single TRAINER_ORLEANS_GRAND_OAK_GYM_AROMA_LADY, GrandOak_Gym_Text_AromaLadyIntro, GrandOak_Gym_Text_AromaLadyDefeat
	msgbox GrandOak_Gym_Text_AromaLadyAfter, MSGBOX_AUTOCLOSE
	end

GrandOak_Gym_EventScript_Magnolia3::
	setvar VAR_0x8004, ACH_MAGNOLIAS_GARDEN
	special Achievement_UnlockVar8004
	trainerbattle_single TRAINER_MAGNOLIA, GrandOak_Gym_Text_MagnoliaIntro, GrandOak_Gym_Text_MagnoliaDefeat, GrandOak_Gym_EventScript_MagnoliaDefeated, NO_MUSIC
	call_if_unset FLAG_RECEIVED_GARDEN_SHEARS, GrandOak_Gym_EventScript_GiveRewards
	msgbox GrandOak_Gym_Text_MagnoliaPostBattle, MSGBOX_DEFAULT
	release
	end

GrandOak_Gym_EventScript_MagnoliaDefeated::
	message GrandOak_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE01_GET
	call_if_lt VAR_ORLEANS_STORY, 7, GrandOak_Gym_EventScript_SetStory7
	@ recovery: Mom moves back into the house
	setflag FLAG_HIDE_SHELTER_MOM
	clearflag FLAG_HIDE_PLAYERS_HOUSE_MOM
	msgbox GrandOak_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call GrandOak_Gym_EventScript_GiveRewards
	release
	end

@ Each reward has its own flag and is only marked as given when it went into the bag (a full pocket leaves the flag unset, so
@ talking to Magnolia again retries; the TM is never given twice).
GrandOak_Gym_EventScript_GiveRewards::
	goto_if_set FLAG_RECEIVED_TM_TRAILBLAZE, GrandOak_Gym_EventScript_GiveShears
	msgbox GrandOak_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_TRAILBLAZE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_TRAILBLAZE
	msgbox GrandOak_Gym_Text_TrailblazeInfo, MSGBOX_DEFAULT
GrandOak_Gym_EventScript_GiveShears:
	giveitem ITEM_GARDEN_SHEARS
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_GARDEN_SHEARS
	msgbox GrandOak_Gym_Text_ShearsInfo, MSGBOX_DEFAULT
	msgbox GrandOak_Gym_Text_FirstVerse, MSGBOX_DEFAULT
	return

GrandOak_Gym_Text_RangerIntro:
	.string "Lost already? The hedges turn\n"
	.string "you around. So do I!$"

GrandOak_Gym_Text_RangerDefeat:
	.string "Pruned!$"

GrandOak_Gym_Text_RangerAfter:
	.string "Keep left at the fork. Or was it\n"
	.string "right? I only trim these.$"

GrandOak_Gym_Text_AromaLadyIntro:
	.string "Smell that? Magnolia blossoms.\n"
	.string "You're almost there.$"

GrandOak_Gym_Text_AromaLadyDefeat:
	.string "How lovely. You've earned the\n"
	.string "last turn.$"

GrandOak_Gym_Text_AromaLadyAfter:
	.string "MAGNOLIA is waiting on her dais.\n"
	.string "She'll make it grow under you.$"

GrandOak_Gym_Text_MagnoliaIntro:
	.string "MAGNOLIA: Welcome to my garden.\p"
	.string "This glass held through the whole\n"
	.string "storm. Not one pane broke.\p"
	.string "Things that are rooted deep\n"
	.string "don't wash away. Let me show you!$"

GrandOak_Gym_Text_MagnoliaDefeat:
	.string "MAGNOLIA: Oh, you grew so fast.\n"
	.string "The garden accepts you.$"

GrandOak_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the MAGNOLIA BADGE\n"
	.string "from MAGNOLIA.$"

GrandOak_Gym_Text_BadgeInfo:
	.string "MAGNOLIA: With that BADGE, your\n"
	.string "POKéMON will trust you a bit more.\p"
	.string "Trust grows, like anything.$"

GrandOak_Gym_Text_TakeThis:
	.string "MAGNOLIA: Take these as well.$"

GrandOak_Gym_Text_TrailblazeInfo:
	.string "MAGNOLIA: TRAILBLAZE cuts a path\n"
	.string "and quickens your step after.$"

GrandOak_Gym_Text_ShearsInfo:
	.string "MAGNOLIA: And my GARDEN SHEARS.\n"
	.string "The storm tangled hedges all over\p"
	.string "the region. Those will clear them.$"

GrandOak_Gym_Text_FirstVerse:
	.string "MAGNOLIA: One more thing.\n"
	.string "TUPELO sent you, didn't he?\p"
	.string "Then hear it. The first verse.\p"
	.string "“The water rose, and the land\n"
	.string "was afraid...”\p"
	.string "Carry it back to the song house.$"

GrandOak_Gym_Text_MagnoliaPostBattle:
	.string "MAGNOLIA: ÉCLAIR keeps the next\n"
	.string "verse, out past the storm hedge.$"

GrandOak_Gym_EventScript_SetStory7:
	setvar VAR_ORLEANS_STORY, 7
	return

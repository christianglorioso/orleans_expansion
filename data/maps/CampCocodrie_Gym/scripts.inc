CampCocodrie_Gym_MapScripts::
	.byte 0

@ Gym 5, the brothers' cookhouse (Chapter 5): Boudreaux and Thibodeaux, a DOUBLE battle (both trainers on one side: the engine's
@ trainerbattle_two_trainers, each with his own three Pokemon).
@ The trial is the gumbo cook-off. Four ingredients are gathered around the camp (flags FLAG_CAMP_ANDOUILLE: the smokehouse,
@ FLAG_CAMP_SHRIMP: the dock fisherman's battle, FLAG_CAMP_OKRA: the gardener's patch, FLAG_CAMP_FILE: the old neighbour's cabin).
@ Then the judging table: Boudreaux's pot, Thibodeaux's pot, or a tie. The right answer is the tie (story 25); only then do the
@ brothers battle. Story 26 + badge 5 + verse 5 + TM Sludge Bomb come after the battle (flag-guarded, bag-full safe). The player needs
@ two usable POKéMON for the double battle (HasEnoughMonsForDoubleBattle).

CampCocodrie_Gym_EventScript_GymGuide2::
	lock
	faceplayer
	goto_if_set FLAG_BADGE05_GET, CampCocodrie_Gym_EventScript_GuideAfter
	goto_if_ge VAR_ORLEANS_STORY, 25, CampCocodrie_Gym_EventScript_GuideTie
	goto_if_ge VAR_ORLEANS_STORY, 24, CampCocodrie_Gym_EventScript_GuideCook
	msgbox CampCocodrie_Gym_Text_GuideIsaac, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Gym_EventScript_GuideCook:
	msgbox CampCocodrie_Gym_Text_GuideCook, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Gym_EventScript_GuideTie:
	msgbox CampCocodrie_Gym_Text_GuideTie, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Gym_EventScript_GuideAfter:
	msgbox CampCocodrie_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- the judging table
CampCocodrie_Gym_EventScript_JudgingTable::
	lockall
	goto_if_ge VAR_ORLEANS_STORY, 25, CampCocodrie_Gym_EventScript_TableDone
	goto_if_lt VAR_ORLEANS_STORY, 24, CampCocodrie_Gym_EventScript_TableLater
	goto_if_unset FLAG_CAMP_ANDOUILLE, CampCocodrie_Gym_EventScript_TableMissing
	goto_if_unset FLAG_CAMP_SHRIMP, CampCocodrie_Gym_EventScript_TableMissing
	goto_if_unset FLAG_CAMP_OKRA, CampCocodrie_Gym_EventScript_TableMissing
	goto_if_unset FLAG_CAMP_FILE, CampCocodrie_Gym_EventScript_TableMissing
	msgbox CampCocodrie_Gym_Text_TableReady, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, CampCocodrie_Gym_Text_ChoiceBoudreaux, CampCocodrie_Gym_Text_ChoiceThibodeaux, CampCocodrie_Gym_Text_ChoiceTie
	switch VAR_RESULT
	case 2, CampCocodrie_Gym_EventScript_TableTie
	case 0, CampCocodrie_Gym_EventScript_TableWrong
	case 1, CampCocodrie_Gym_EventScript_TableWrong
	releaseall
	end

CampCocodrie_Gym_EventScript_TableTie:
	call_if_eq VAR_ORLEANS_STORY, 24, CampCocodrie_Gym_EventScript_SetStory25
	msgbox CampCocodrie_Gym_Text_TableTie, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Gym_EventScript_SetStory25:
	setvar VAR_ORLEANS_STORY, 25
	return

CampCocodrie_Gym_EventScript_TableWrong:
	msgbox CampCocodrie_Gym_Text_TableWrong, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Gym_EventScript_TableMissing:
	msgbox CampCocodrie_Gym_Text_TableMissing, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Gym_EventScript_TableLater:
	msgbox CampCocodrie_Gym_Text_TableLater, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Gym_EventScript_TableDone:
	msgbox CampCocodrie_Gym_Text_TableDone, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- the double battle
CampCocodrie_Gym_EventScript_Boudreaux0::
	lock
	faceplayer
	goto CampCocodrie_Gym_EventScript_Brothers

CampCocodrie_Gym_EventScript_Thibodeaux1::
	lock
	faceplayer
	goto CampCocodrie_Gym_EventScript_Brothers

CampCocodrie_Gym_EventScript_Brothers:
	goto_if_set FLAG_BADGE05_GET, CampCocodrie_Gym_EventScript_BrothersAfter
	goto_if_lt VAR_ORLEANS_STORY, 25, CampCocodrie_Gym_EventScript_BrothersNotYet
	special HasEnoughMonsForDoubleBattle
	goto_if_ne VAR_RESULT, PLAYER_HAS_TWO_USABLE_MONS, CampCocodrie_Gym_EventScript_BrothersNeedTwo
	msgbox CampCocodrie_Gym_Text_BrothersIntro1, MSGBOX_DEFAULT
	msgbox CampCocodrie_Gym_Text_BrothersIntro2, MSGBOX_DEFAULT
	closemessage
	@ the raw trainerbattle command (trainerbattle_two_trainers has no post-battle script, so the script would end after the battle):
	@ trainer A's "event script" is what runs after the win
	trainerbattle OBJ_ID_NONE, TRAINER_BOUDREAUX, NULL, CampCocodrie_Gym_Text_BoudreauxDefeat, CampCocodrie_Gym_EventScript_BrothersDefeated, OBJ_ID_NONE, TRAINER_THIBODEAUX, NULL, CampCocodrie_Gym_Text_ThibodeauxDefeat, NULL, NULL, NULL, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE
	end

CampCocodrie_Gym_EventScript_BrothersNotYet:
	msgbox CampCocodrie_Gym_Text_BrothersNotYet, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Gym_EventScript_BrothersNeedTwo:
	msgbox CampCocodrie_Gym_Text_BrothersNeedTwo, MSGBOX_DEFAULT
	release
	end

@ Badge, story (never lowered) and the verse come first; the TM has its own flag (set once it is really in the bag), so a full bag
@ can't lose it; talking to a brother again retries.
CampCocodrie_Gym_EventScript_BrothersDefeated::
	message CampCocodrie_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE05_GET
	call_if_eq VAR_ORLEANS_STORY, 25, CampCocodrie_Gym_EventScript_SetStory26
	msgbox CampCocodrie_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call CampCocodrie_Gym_EventScript_GiveRewards
	release
	end

CampCocodrie_Gym_EventScript_SetStory26:
	setvar VAR_ORLEANS_STORY, 26
	return

CampCocodrie_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_TM_SLUDGE_BOMB, CampCocodrie_Gym_EventScript_RewardsDone
	msgbox CampCocodrie_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_SLUDGE_BOMB
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_SLUDGE_BOMB
	msgbox CampCocodrie_Gym_Text_SludgeBombInfo, MSGBOX_DEFAULT
	msgbox CampCocodrie_Gym_Text_FifthVerse, MSGBOX_DEFAULT
CampCocodrie_Gym_EventScript_RewardsDone:
	return

CampCocodrie_Gym_EventScript_BrothersAfter:
	call CampCocodrie_Gym_EventScript_GiveRewards
	msgbox CampCocodrie_Gym_Text_BrothersPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
CampCocodrie_Gym_Text_GuideIsaac:
	.string "GUIDE: The brothers won't cook for\n"
	.string "a camp that's looking over its\p"
	.string "shoulder. A boy in a dark jacket\n"
	.string "is lurking by the nurse cabin.\p"
	.string "Deal with him first.$"

CampCocodrie_Gym_Text_GuideCook:
	.string "GUIDE: Four things make a gumbo:\n"
	.string "andouille from the smokehouse,\p"
	.string "shrimp from the dock, okra from the\n"
	.string "garden and filé from the old\p"
	.string "neighbour. Then judge the pots at\n"
	.string "the table.$"

CampCocodrie_Gym_Text_GuideTie:
	.string "GUIDE: The pots are judged. The\n"
	.string "brothers are waiting. Talk to\p"
	.string "either one. Bring two POKéMON.$"

CampCocodrie_Gym_Text_GuideAfter:
	.string "GUIDE: Two cooks, one table. I\n"
	.string "told you the table was the trial.$"

CampCocodrie_Gym_Text_TableLater:
	.string "Two pots simmer on the stoves, one\n"
	.string "on each side. Nobody's cooking\p"
	.string "yet. The camp isn't ready.$"

CampCocodrie_Gym_Text_TableMissing:
	.string "The judging table is bare. The\n"
	.string "brothers need all four of the\p"
	.string "ingredients, brought from around\n"
	.string "the camp.$"

CampCocodrie_Gym_Text_TableReady:
	.string "Two pots, a ladle in each. The four\n"
	.string "ingredients are in. Time to taste.\p"
	.string "Which pot is better?$"

CampCocodrie_Gym_Text_ChoiceBoudreaux:
	.string "Boudreaux's pot$"

CampCocodrie_Gym_Text_ChoiceThibodeaux:
	.string "Thibodeaux's pot$"

CampCocodrie_Gym_Text_ChoiceTie:
	.string "It's a tie$"

CampCocodrie_Gym_Text_TableWrong:
	.string "The brothers glare at each other.\n"
	.string "Neither wins. Neither smiles.\p"
	.string "Taste again. Honestly this time.$"

CampCocodrie_Gym_Text_TableTie:
	.string "A tie! Both pots, side by side, are\n"
	.string "as good as each other's.\p"
	.string "The brothers stare. Then laugh.\n"
	.string "BOUDREAUX: That's what we've been\p"
	.string "telling each other for forty years!\n"
	.string "THIBODEAUX: Now. About that battle.$"

CampCocodrie_Gym_Text_TableDone:
	.string "Two pots on the stoves, both empty.\n"
	.string "The tie is still painted on the\p"
	.string "wall behind them.$"

CampCocodrie_Gym_Text_BrothersNotYet:
	.string "BOUDREAUX: We cook first. We fight\n"
	.string "later. Taste the pots, kid.$"

CampCocodrie_Gym_Text_BrothersNeedTwo:
	.string "THIBODEAUX: We fight as two. You\n"
	.string "need two POKéMON on your feet.$"

CampCocodrie_Gym_Text_BrothersIntro1:
	.string "BOUDREAUX: Forty years in one\n"
	.string "kitchen. Never agreed on a thing.\p"
	.string "THIBODEAUX: Until you called the\n"
	.string "tie. Nobody's ever done that.$"

CampCocodrie_Gym_Text_BrothersIntro2:
	.string "BOUDREAUX: So we fight together.\n"
	.string "THIBODEAUX: Two cooks, one pot.\p"
	.string "BOTH: Come and get it!$"

CampCocodrie_Gym_Text_BoudreauxDefeat:
	.string "BOUDREAUX: Ha! The pot boiled over.$"

CampCocodrie_Gym_Text_ThibodeauxDefeat:
	.string "THIBODEAUX: Burnt on the bottom!$"

CampCocodrie_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the GUMBO BADGE\n"
	.string "from BOUDREAUX and THIBODEAUX.$"

CampCocodrie_Gym_Text_BadgeInfo:
	.string "BOUDREAUX: That BADGE says you can\n"
	.string "feed a table of two.\p"
	.string "THIBODEAUX: And that the lake road\n"
	.string "will carry you now.$"

CampCocodrie_Gym_Text_TakeThis:
	.string "THIBODEAUX: Take this. A gift from\n"
	.string "both our kitchens.$"

CampCocodrie_Gym_Text_SludgeBombInfo:
	.string "BOUDREAUX: SLUDGE BOMB. Thick,\n"
	.string "dark, and surprisingly sweet.$"

CampCocodrie_Gym_Text_FifthVerse:
	.string "BOUDREAUX: And the fifth verse.\n"
	.string "THIBODEAUX: The people ate together.\p"
	.string "BOTH: And the land was fed. Take\n"
	.string "that back to TUPELO.$"

CampCocodrie_Gym_Text_BrothersPost:
	.string "BOUDREAUX: The lake road is open\n"
	.string "to you now.\p"
	.string "THIBODEAUX: Eat before you go. We\n"
	.string "insist. Both of us.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

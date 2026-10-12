CrescentCity_Tutor_MapScripts::
	.byte 0

@ The services house: the move tutor (Heart Scales), the EV coach (money) and the IV judge (Bottle Caps).
@ The EV/IV edits are the specials in src/orleans_services.c (VAR_0x8004 = party slot, VAR_0x8005 = stat 0-5, VAR_0x8006 = mode).

@ ---------------------------------------------------------------- move tutor: one Heart Scale per move, four moves
CrescentCity_Tutor_EventScript_MoveTutor0::
	lock
	faceplayer
	msgbox CrescentCity_Tutor_Text_TutorIntro, MSGBOX_DEFAULT
	@ opens the Move Relearner's tutor and egg-move lists (summary screen too): every move the dex sheet gives a species that is not a TM; see tools/dex/tm_list.md
	setflag FLAG_ORLEANS_TUTOR_RELEARNER
	setflag FLAG_ORLEANS_EGG_RELEARNER
	dynmultichoice 1, 1, FALSE, 6, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_Tutor_Text_MoveSubstitute, CrescentCity_Tutor_Text_MoveFirePunch, CrescentCity_Tutor_Text_MoveSwift, CrescentCity_Tutor_Text_MoveIcePunch, CrescentCity_Tutor_Text_MoveMore, CrescentCity_Tutor_Text_Cancel
	switch VAR_RESULT
	case 0, CrescentCity_Tutor_EventScript_TeachSubstitute
	case 1, CrescentCity_Tutor_EventScript_TeachFirePunch
	case 2, CrescentCity_Tutor_EventScript_TeachSwift
	case 3, CrescentCity_Tutor_EventScript_TeachIcePunch
	case 4, CrescentCity_Tutor_EventScript_MoreMoves
	goto CrescentCity_Tutor_EventScript_TutorDeclined

@ free: the relearner's own picker lists, for the chosen POKéMON, every tutor move it can learn
CrescentCity_Tutor_EventScript_MoreMoves:
	msgbox CrescentCity_Tutor_Text_MoreIntro, MSGBOX_DEFAULT
	setmoverelearnerstate MOVE_RELEARNER_TUTOR_MOVES
	bufferstring STR_VAR_3, MoveRelearner_Text_TutorMoveLWR
	goto MoveRelearner_EventScript_TeachMove
	end

CrescentCity_Tutor_EventScript_TeachSubstitute:
	setvar VAR_0x8009, MOVE_SUBSTITUTE
	goto CrescentCity_Tutor_EventScript_TeachMove

CrescentCity_Tutor_EventScript_TeachFirePunch:
	setvar VAR_0x8009, MOVE_FIRE_PUNCH
	goto CrescentCity_Tutor_EventScript_TeachMove

CrescentCity_Tutor_EventScript_TeachSwift:
	setvar VAR_0x8009, MOVE_SWIFT
	goto CrescentCity_Tutor_EventScript_TeachMove

CrescentCity_Tutor_EventScript_TeachIcePunch:
	setvar VAR_0x8009, MOVE_ICE_PUNCH
	goto CrescentCity_Tutor_EventScript_TeachMove

CrescentCity_Tutor_EventScript_TeachMove:
	checkitem ITEM_HEART_SCALE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_NoScale
	msgbox CrescentCity_Tutor_Text_WhichMon, MSGBOX_DEFAULT
	copyvar VAR_0x8005, VAR_0x8009
	@ a cancel from the picker leaves VAR_RESULT as it was (checkitem's TRUE): clear it so a cancel can never take the scale
	setvar VAR_RESULT, FALSE
	call MoveTutor_EventScript_OpenBox
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_TutorDeclined
	removeitem ITEM_HEART_SCALE
	msgbox CrescentCity_Tutor_Text_Taught, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_NoScale:
	msgbox CrescentCity_Tutor_Text_NoScale, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_TutorDeclined:
	msgbox CrescentCity_Tutor_Text_Declined, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- EV coach: +10 EVs in a stat for 1000, or clear a stat for 500
CrescentCity_Tutor_EventScript_EvCoach1::
	lock
	faceplayer
	msgbox CrescentCity_Tutor_Text_EvIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_Tutor_EventScript_Declined
	getpartysize
	goto_if_eq VAR_RESULT, 0, CrescentCity_Tutor_EventScript_Declined
	msgbox CrescentCity_Tutor_Text_WhichMon, MSGBOX_DEFAULT
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, CrescentCity_Tutor_EventScript_Declined
	copyvar VAR_0x8007, VAR_0x8004
	callnative Script_GetChosenMonOffensiveEVs
	msgbox CrescentCity_Tutor_Text_EvOffense, MSGBOX_DEFAULT
	callnative Script_GetChosenMonDefensiveEVs
	msgbox CrescentCity_Tutor_Text_EvDefense, MSGBOX_DEFAULT
	msgbox CrescentCity_Tutor_Text_WhichStat, MSGBOX_DEFAULT
	call CrescentCity_Tutor_EventScript_PickStat
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, CrescentCity_Tutor_EventScript_Declined
	copyvar VAR_0x8008, VAR_RESULT
	dynmultichoice 1, 1, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_Tutor_Text_EvAdd, CrescentCity_Tutor_Text_EvClear, CrescentCity_Tutor_Text_Cancel
	goto_if_eq VAR_RESULT, 0, CrescentCity_Tutor_EventScript_EvAdd
	goto_if_eq VAR_RESULT, 1, CrescentCity_Tutor_EventScript_EvClear
	goto CrescentCity_Tutor_EventScript_Declined

CrescentCity_Tutor_EventScript_EvAdd:
	checkmoney 1000
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_NoMoney
	copyvar VAR_0x8004, VAR_0x8007
	copyvar VAR_0x8005, VAR_0x8008
	setvar VAR_0x8006, 1
	special OrleansSvc_ChangeEv
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_EvNoChange
	removemoney 1000
	msgbox CrescentCity_Tutor_Text_EvDone, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_EvClear:
	checkmoney 500
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_NoMoney
	copyvar VAR_0x8004, VAR_0x8007
	copyvar VAR_0x8005, VAR_0x8008
	setvar VAR_0x8006, 0
	special OrleansSvc_ChangeEv
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_EvNoChange
	removemoney 500
	msgbox CrescentCity_Tutor_Text_EvDone, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_EvNoChange:
	msgbox CrescentCity_Tutor_Text_EvNoChange, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- IV judge: one stat's IV to 31 for one Bottle Cap
CrescentCity_Tutor_EventScript_IvJudge2::
	lock
	faceplayer
	msgbox CrescentCity_Tutor_Text_IvIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_Tutor_EventScript_Declined
	checkitem ITEM_BOTTLE_CAP
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_NoCap
	getpartysize
	goto_if_eq VAR_RESULT, 0, CrescentCity_Tutor_EventScript_Declined
	msgbox CrescentCity_Tutor_Text_WhichMon, MSGBOX_DEFAULT
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, CrescentCity_Tutor_EventScript_Declined
	copyvar VAR_0x8007, VAR_0x8004
	callnative Script_GetChosenMonOffensiveIVs
	msgbox CrescentCity_Tutor_Text_IvOffense, MSGBOX_DEFAULT
	callnative Script_GetChosenMonDefensiveIVs
	msgbox CrescentCity_Tutor_Text_IvDefense, MSGBOX_DEFAULT
	msgbox CrescentCity_Tutor_Text_WhichStat, MSGBOX_DEFAULT
	call CrescentCity_Tutor_EventScript_PickStat
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, CrescentCity_Tutor_EventScript_Declined
	copyvar VAR_0x8005, VAR_RESULT
	copyvar VAR_0x8004, VAR_0x8007
	special OrleansSvc_MaxIv
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Tutor_EventScript_IvNoChange
	removeitem ITEM_BOTTLE_CAP
	msgbox CrescentCity_Tutor_Text_IvDone, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_IvNoChange:
	msgbox CrescentCity_Tutor_Text_IvNoChange, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_NoCap:
	msgbox CrescentCity_Tutor_Text_NoCap, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- shared
CrescentCity_Tutor_EventScript_PickStat:
	dynmultichoice 1, 1, FALSE, 7, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_Tutor_Text_StatHp, CrescentCity_Tutor_Text_StatAtk, CrescentCity_Tutor_Text_StatDef, CrescentCity_Tutor_Text_StatSpAtk, CrescentCity_Tutor_Text_StatSpDef, CrescentCity_Tutor_Text_StatSpeed, CrescentCity_Tutor_Text_Cancel
	goto_if_eq VAR_RESULT, 6, CrescentCity_Tutor_EventScript_PickCancel
	return

CrescentCity_Tutor_EventScript_PickCancel:
	setvar VAR_RESULT, MULTI_B_PRESSED
	return

CrescentCity_Tutor_EventScript_NoMoney:
	msgbox CrescentCity_Tutor_Text_NoMoney, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_EventScript_Declined:
	msgbox CrescentCity_Tutor_Text_Declined, MSGBOX_DEFAULT
	release
	end

CrescentCity_Tutor_Text_StatHp:
	.string "HP$"

CrescentCity_Tutor_Text_StatAtk:
	.string "ATTACK$"

CrescentCity_Tutor_Text_StatDef:
	.string "DEFENSE$"

CrescentCity_Tutor_Text_StatSpAtk:
	.string "SP. ATK$"

CrescentCity_Tutor_Text_StatSpDef:
	.string "SP. DEF$"

CrescentCity_Tutor_Text_StatSpeed:
	.string "SPEED$"

CrescentCity_Tutor_Text_Cancel:
	.string "CANCEL$"

CrescentCity_Tutor_Text_MoveSubstitute:
	.string "SUBSTITUTE$"

CrescentCity_Tutor_Text_MoveFirePunch:
	.string "FIRE PUNCH$"

CrescentCity_Tutor_Text_MoveSwift:
	.string "SWIFT$"

CrescentCity_Tutor_Text_MoveIcePunch:
	.string "ICE PUNCH$"

CrescentCity_Tutor_Text_MoveMore:
	.string "OTHER MOVES$"

CrescentCity_Tutor_Text_MoreIntro:
	.string "TUTOR: Anything else a POKéMON\n"
	.string "could learn from me? Pick one.$"

CrescentCity_Tutor_Text_EvAdd:
	.string "ADD 10 (¥1000)$"

CrescentCity_Tutor_Text_EvClear:
	.string "CLEAR (¥500)$"

CrescentCity_Tutor_Text_TutorIntro:
	.string "TUTOR: One HEART SCALE a lesson.\n"
	.string "Pick a move, then the POKéMON.$"

CrescentCity_Tutor_Text_WhichMon:
	.string "Which POKéMON?$"

CrescentCity_Tutor_Text_NoScale:
	.string "TUTOR: No HEART SCALE, no lesson.\n"
	.string "They wash up on the flats.$"

CrescentCity_Tutor_Text_Taught:
	.string "TUTOR: There! Learned. Practice it.$"

CrescentCity_Tutor_Text_Declined:
	.string "Maybe another time, then.$"

CrescentCity_Tutor_Text_EvIntro:
	.string "COACH: I reshape what a POKéMON\n"
	.string "has trained. Ten points for ¥1000,\p"
	.string "or I wipe a stat clean for ¥500.\n"
	.string "Interested?$"

CrescentCity_Tutor_Text_WhichStat:
	.string "Which stat?$"

CrescentCity_Tutor_Text_EvOffense:
	.string "ATK {STR_VAR_1}, SPA {STR_VAR_2}\nSPE {STR_VAR_3}$"

CrescentCity_Tutor_Text_EvDefense:
	.string "HP {STR_VAR_1}, DEF {STR_VAR_2}\nSPD {STR_VAR_3}$"

CrescentCity_Tutor_Text_EvDone:
	.string "COACH: Done. Feel the difference?$"

CrescentCity_Tutor_Text_EvNoChange:
	.string "COACH: That stat can't take any\n"
	.string "more, or has nothing to clear.$"

CrescentCity_Tutor_Text_NoMoney:
	.string "You can't afford that.$"

CrescentCity_Tutor_Text_IvIntro:
	.string "JUDGE: I judge a POKéMON's gifts.\n"
	.string "For one BOTTLE CAP I'll raise a\p"
	.string "stat to its very best. Care to\n"
	.string "try?$"

CrescentCity_Tutor_Text_NoCap:
	.string "JUDGE: No BOTTLE CAP. They're\n"
	.string "rare. Come back with one.$"

CrescentCity_Tutor_Text_IvOffense:
	.string "ATK {STR_VAR_1}, SPA {STR_VAR_2}\nSPE {STR_VAR_3}$"

CrescentCity_Tutor_Text_IvDefense:
	.string "HP {STR_VAR_1}, DEF {STR_VAR_2}\nSPD {STR_VAR_3}$"

CrescentCity_Tutor_Text_IvDone:
	.string "JUDGE: Splendid. A perfect stat.$"

CrescentCity_Tutor_Text_IvNoChange:
	.string "JUDGE: That stat is already as\n"
	.string "good as it gets.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

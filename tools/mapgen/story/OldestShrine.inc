OldestShrine_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldestShrine_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, OldestShrine_OnFrameTable
	.byte 0

@ The Oldest Shrine (Chapter 9, F.5-F.7). Story: 41 arrival by Route 25 (VAR_SHRINE_ARRIVAL): Camille (Mega Weezing), then Andrew (Mega Metagross), then they
@ run for their boat; 42 Rayquaza descends and Jayden arrives (talk to either to start the raid); 43 the Rayquaza raid (2 v 1 with Jayden) won,
@ the Swampertite, the dawn and the credits (story 44, then 45 = the post-game). A blackout replays what is not done (trainer flags skip won fights).

OldestShrine_OnTransition:
	setflag FLAG_HIDE_SHRINE_CAMILLE
	setflag FLAG_HIDE_SHRINE_ANDREW
	setflag FLAG_HIDE_SHRINE_RAYQUAZA
	setflag FLAG_HIDE_SHRINE_JAYDEN
	call_if_eq VAR_ORLEANS_STORY, 42, OldestShrine_EventScript_ShowRaid
	call_if_eq VAR_ORLEANS_STORY, 43, OldestShrine_EventScript_ShowRaid
	end

OldestShrine_EventScript_ShowRaid:
	clearflag FLAG_HIDE_SHRINE_RAYQUAZA
	clearflag FLAG_HIDE_SHRINE_JAYDEN
	return

OldestShrine_OnFrameTable:
	map_script_2 VAR_SHRINE_ARRIVAL, 0, OldestShrine_EventScript_Arrival
	.2byte 0

@ ---------------------------------------------------------------- F.5 the landing steps (story 41 -> 42)
OldestShrine_EventScript_Arrival::
	goto_if_ne VAR_ORLEANS_STORY, 41, OldestShrine_EventScript_ArrivalOther
	lockall
	clearflag FLAG_HIDE_SHRINE_CAMILLE
	clearflag FLAG_HIDE_SHRINE_ANDREW
	addobject LOCALID_OLDEST_SHRINE_CAMILLE
	addobject LOCALID_OLDEST_SHRINE_ANDREW
	msgbox OldestShrine_Text_Arrival1, MSGBOX_DEFAULT
	msgbox OldestShrine_Text_Camille1, MSGBOX_DEFAULT
	closemessage
	goto_if_defeated TRAINER_ORLEANS_CAMILLE_SHRINE, OldestShrine_EventScript_CamilleDone
	trainerbattle_no_intro TRAINER_ORLEANS_CAMILLE_SHRINE, OldestShrine_Text_CamilleDefeat
OldestShrine_EventScript_CamilleDone:
	msgbox OldestShrine_Text_CamilleAfter, MSGBOX_DEFAULT
	clearflag FLAG_HIDE_SHRINE_JAYDEN
	addobject LOCALID_OLDEST_SHRINE_JAYDEN
	msgbox OldestShrine_Text_JaydenHeal, MSGBOX_DEFAULT
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox OldestShrine_Text_Andrew1, MSGBOX_DEFAULT
	closemessage
	goto_if_defeated TRAINER_ORLEANS_ANDREW, OldestShrine_EventScript_AndrewDone
	trainerbattle_no_intro TRAINER_ORLEANS_ANDREW, OldestShrine_Text_AndrewDefeat
OldestShrine_EventScript_AndrewDone:
	msgbox OldestShrine_Text_AndrewAfter, MSGBOX_DEFAULT
	msgbox OldestShrine_Text_Rayquaza1, MSGBOX_DEFAULT
	closemessage
	setvar VAR_SHRINE_ARRIVAL, 1
	setvar VAR_ORLEANS_STORY, 42
	setflag FLAG_HIDE_SHRINE_CAMILLE
	setflag FLAG_HIDE_SHRINE_ANDREW
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLDEST_SHRINE_CAMILLE
	removeobject LOCALID_OLDEST_SHRINE_ANDREW
	clearflag FLAG_HIDE_SHRINE_RAYQUAZA
	addobject LOCALID_OLDEST_SHRINE_RAYQUAZA
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	goto_if_eq VAR_ORLEANS_LEGENDARY_PICK, 2, OldestShrine_EventScript_JaydenArrivesK
	msgbox OldestShrine_Text_JaydenK, MSGBOX_DEFAULT
	releaseall
	end

OldestShrine_EventScript_JaydenArrivesK:
	msgbox OldestShrine_Text_JaydenG, MSGBOX_DEFAULT
	releaseall
	end

@ any other story: nothing to play, and the entry must not loop
OldestShrine_EventScript_ArrivalOther:
	goto_if_lt VAR_ORLEANS_STORY, 41, OldestShrine_EventScript_ArrivalWait
	setvar VAR_SHRINE_ARRIVAL, 1
OldestShrine_EventScript_ArrivalWait:
	end

OldestShrine_EventScript_Camille::
OldestShrine_EventScript_Andrew::
	end

@ ---------------------------------------------------------------- F.6 the Rayquaza raid (story 42 -> 43)
OldestShrine_EventScript_Rayquaza::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 43, OldestShrine_EventScript_RayCalm
	goto OldestShrine_EventScript_RayStart

OldestShrine_EventScript_Jayden::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 43, OldestShrine_EventScript_JaydenIdle
	goto OldestShrine_EventScript_RayStart

OldestShrine_EventScript_JaydenIdle:
	msgbox OldestShrine_Text_JaydenIdle, MSGBOX_DEFAULT
	release
	end

OldestShrine_EventScript_RayCalm:
	call OldestShrine_EventScript_Rewards
	goto_if_lt VAR_ORLEANS_STORY, 44, OldestShrine_EventScript_Epilogue
	msgbox OldestShrine_Text_RayIdle, MSGBOX_DEFAULT
	release
	end

OldestShrine_EventScript_RayStart:
	special SavePlayerParty
	msgbox OldestShrine_Text_RayIntro, MSGBOX_DEFAULT
	closemessage
	goto OldestShrine_EventScript_RayBattle

@ Jayden's partner party depends on his starter (VAR_STARTER_MON 0 Chikorita, 1 Fuecoco, 2 Totodile) and on the legendary the player did NOT take
@ (VAR_ORLEANS_LEGENDARY_PICK 1: the player has Kyogre, Jayden Groudon)
OldestShrine_EventScript_RayBattle:
	call_if_eq VAR_STARTER_MON, 0, OldestShrine_EventScript_BattleChikorita
	call_if_eq VAR_STARTER_MON, 1, OldestShrine_EventScript_BattleFuecoco
	call_if_eq VAR_STARTER_MON, 2, OldestShrine_EventScript_BattleTotodile
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_LOST, OldestShrine_EventScript_RayLost
	goto OldestShrine_EventScript_RayWon

OldestShrine_EventScript_BattleChikorita:
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 1, OldestShrine_EventScript_BattleChikoritaG
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 2, OldestShrine_EventScript_BattleChikoritaK
	return

OldestShrine_EventScript_BattleFuecoco:
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 1, OldestShrine_EventScript_BattleFuecocoG
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 2, OldestShrine_EventScript_BattleFuecocoK
	return

OldestShrine_EventScript_BattleTotodile:
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 1, OldestShrine_EventScript_BattleTotodileG
	call_if_eq VAR_ORLEANS_LEGENDARY_PICK, 2, OldestShrine_EventScript_BattleTotodileK
	return

OldestShrine_EventScript_BattleChikoritaG:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_CHIKORITA_GROUDON
	return

OldestShrine_EventScript_BattleChikoritaK:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_CHIKORITA_KYOGRE
	return

OldestShrine_EventScript_BattleFuecocoG:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_FUECOCO_GROUDON
	return

OldestShrine_EventScript_BattleFuecocoK:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_FUECOCO_KYOGRE
	return

OldestShrine_EventScript_BattleTotodileG:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_TOTODILE_GROUDON
	return

OldestShrine_EventScript_BattleTotodileK:
	multi_fixed_2_vs_1 TRAINER_ORLEANS_RAYQUAZA_RAID, OldestShrine_Text_RayDefeat, PARTNER_JAYDEN_TOTODILE_KYOGRE
	return

@ a loss: heal, then TRY AGAIN or REST FIRST (B = rest first; nothing is lost)
OldestShrine_EventScript_RayLost:
	special HealPlayerParty
	msgbox OldestShrine_Text_Retry, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 2, 0, DYN_MULTICHOICE_CB_NONE, OldestShrine_Text_ChoiceAgain, OldestShrine_Text_ChoiceRest
	goto_if_eq VAR_RESULT, 0, OldestShrine_EventScript_RayAgain
	release
	end

OldestShrine_EventScript_RayAgain:
	closemessage
	goto OldestShrine_EventScript_RayBattle

OldestShrine_EventScript_RayWon:
	special HealPlayerParty
	msgbox OldestShrine_Text_RayCalm, MSGBOX_DEFAULT
	call_if_eq VAR_ORLEANS_STORY, 42, OldestShrine_EventScript_SetStory43
	call OldestShrine_EventScript_Rewards
	goto OldestShrine_EventScript_Epilogue

OldestShrine_EventScript_SetStory43:
	setvar VAR_ORLEANS_STORY, 43
	return

@ the Swampertite (own flag, bag-full safe: talking to Rayquaza retries)
OldestShrine_EventScript_Rewards:
	goto_if_set FLAG_RECEIVED_SWAMPERTITE, OldestShrine_EventScript_RewardsDone
	msgbox OldestShrine_Text_Swampertite, MSGBOX_DEFAULT
	giveitem ITEM_SWAMPERTITE
	goto_if_eq VAR_RESULT, FALSE, OldestShrine_EventScript_StoneOwed
	setflag FLAG_RECEIVED_SWAMPERTITE
OldestShrine_EventScript_RewardsDone:
	return

@ a full Items pocket never gates the ending: the stone waits on the singing stone (any time from story 43: the shrine keeper hands it over)
OldestShrine_EventScript_StoneOwed:
	msgbox OldestShrine_Text_StoneOwed, MSGBOX_DEFAULT
	return

@ ---------------------------------------------------------------- F.7 the epilogue (story 43 -> 44 -> 45): dawn, the party in Crescent City, the credits
@ The Swampertite never gates the ending: a bag-full stone is retried at the shrine keeper (OldestShrine_EventScript_Npc0).
OldestShrine_EventScript_Epilogue:
	fadescreen FADE_TO_WHITE
	fadescreen FADE_FROM_WHITE
	msgbox OldestShrine_Text_Dawn, MSGBOX_DEFAULT
	msgbox OldestShrine_Text_JaydenEnd, MSGBOX_DEFAULT
	msgbox OldestShrine_Text_Crescent, MSGBOX_DEFAULT
	msgbox OldestShrine_Text_TheEnd, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_ORLEANS_STORY, 43, OldestShrine_EventScript_SetStory44
	setflag FLAG_HIDE_SHRINE_RAYQUAZA
	setflag FLAG_HIDE_SHRINE_JAYDEN
	setrespawn HEAL_LOCATION_CRESCENT_CITY
	call_if_eq VAR_ORLEANS_STORY, 44, OldestShrine_EventScript_SetStory45
	special GameClear
	waitstate
	releaseall
	end

OldestShrine_EventScript_EpilogueLater:
	release
	end

OldestShrine_EventScript_SetStory44:
	setvar VAR_ORLEANS_STORY, 44
	return

@ 44 -> 45 just before the save: the Hall of Fame and the credits follow (GameClear), and the game resumes in Crescent City at story 45
OldestShrine_EventScript_SetStory45:
	setvar VAR_ORLEANS_STORY, 45
	return

OldestShrine_EventScript_Npc0::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 43, OldestShrine_EventScript_StoneQuiet
	goto_if_set FLAG_RECEIVED_SWAMPERTITE, OldestShrine_EventScript_StoneQuiet
	call OldestShrine_EventScript_Rewards
	releaseall
	end

OldestShrine_EventScript_StoneQuiet:
	msgbox OldestShrine_Text_StoneIdle, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- text
OldestShrine_Text_Arrival1:
	.string "The OLDEST SHRINE: a ring of singing\n"
	.string "stone on a bare island. The air\p"
	.string "hums, and the water answers.$"

OldestShrine_Text_Camille1:
	.string "CAMILLE: So you made it. Of course.\n"
	.string "RITA took a boat at dawn. She's done\p"
	.string "with us. I'm not.\n"
	.string "CAMILLE: ANDREW wants the stone to\p"
	.string "sing his way. I want you out of it.$"

OldestShrine_Text_CamilleDefeat:
	.string "CAMILLE: ...Fine. Fine!$"

OldestShrine_Text_CamilleAfter:
	.string "CAMILLE steps aside, her MEGA\n"
	.string "WEEZING venting gas into the wind.$"

OldestShrine_Text_Andrew1:
	.string "ANDREW: You sang the whole telling.\n"
	.string "Then you know what it costs.\p"
	.string "ANDREW: The Long One lay down to\n"
	.string "guard. Guard against what? Us.\p"
	.string "ANDREW: I'll wake it myself and\n"
	.string "make it listen. Not sing. Not beg.$"

OldestShrine_Text_AndrewDefeat:
	.string "ANDREW: Not like this. Not now.$"

OldestShrine_Text_AndrewAfter:
	.string "ANDREW: ...The stone is calling\n"
	.string "anyway. Look.$"

OldestShrine_Text_Rayquaza1:
	.string "The singing stone flares green. A\n"
	.string "long shape uncoils from the clouds\p"
	.string "and descends, vast and slow:\n"
	.string "RAYQUAZA. The admins flee by boat.$"

OldestShrine_Text_JaydenK:
	.string "JAYDEN: I'm here, and I brought\n"
	.string "GROUDON. Together?$"

OldestShrine_Text_JaydenG:
	.string "JAYDEN: I'm here, and I brought\n"
	.string "KYOGRE. Together?$"

OldestShrine_Text_RayIntro:
	.string "RAYQUAZA fills the sky above the\n"
	.string "stone, its green coils crackling. It\p"
	.string "doesn't attack. It waits to be\n"
	.string "heard. Sing, and hold on.$"

OldestShrine_Text_RayDefeat:
	.string "RAYQUAZA's roar rolls out across the\n"
	.string "sea, and gentles.$"

OldestShrine_Text_RayCalm:
	.string "The Long One settles over the stone,\n"
	.string "the way a hand settles on a head.\p"
	.string "It knows the song. It always did.$"

OldestShrine_Text_Retry:
	.string "JAYDEN: Again? We can do this.\n"
	.string "Or rest first?$"

OldestShrine_Text_ChoiceAgain:
	.string "TRY AGAIN$"

OldestShrine_Text_ChoiceRest:
	.string "REST FIRST$"

OldestShrine_Text_Swampertite:
	.string "Where RAYQUAZA coiled, the stone\n"
	.string "gave up a gift: a SWAMPERTITE, warm\p"
	.string "and dripping.$"

OldestShrine_Text_Dawn:
	.string "Dawn breaks over the OLDEST SHRINE.\n"
	.string "RAYQUAZA coils up into the light and\p"
	.string "the storm clouds unravel behind it.$"

OldestShrine_Text_JaydenEnd:
	.string "JAYDEN: ...Thanks. For listening.\n"
	.string "I'll sing it too, someday. Badly.$"

OldestShrine_Text_Crescent:
	.string "By evening, CRESCENT CITY is dancing\n"
	.string "in the streets. Lamps burn over the\p"
	.string "water, every one of them lit.$"

OldestShrine_Text_TheEnd:
	.string "The telling is sung.\n"
	.string "And the Long One keeps watch.$"

OldestShrine_Text_JaydenHeal:
	.string "JAYDEN runs up the steps. You look\n"
	.string "rough. Hold still. He patches up\p"
	.string "your whole party. Every POKéMON\n"
	.string "perks up.$"

OldestShrine_Text_StoneOwed:
	.string "The stone gave up a gift, but your\n"
	.string "bag is full. The shrine keeper keeps\p"
	.string "it for you. Come back.$"

OldestShrine_Text_StoneIdle:
	.string "The shrine keeper smiles. The stone\n"
	.string "hums, for anyone who listens.$"

OldestShrine_Text_RayIdle:
	.string "RAYQUAZA is calm. It watches the\n"
	.string "dawn.$"

OldestShrine_Text_JaydenIdle:
	.string "JAYDEN: Whenever you're ready.$"

OldestShrine_Text_CamilleIdle:
	.string "CAMILLE: ...$"

OldestShrine_Text_AndrewIdle:
	.string "ANDREW: ...$"


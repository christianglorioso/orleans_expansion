OldWater_SongHouse_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, OldWater_SongHouse_OnLoad
	.byte 0

@ Each verse panel stays bare reed wall until its Singer's badge is earned.
OldWater_SongHouse_OnLoad:
	call_if_unset FLAG_BADGE01_GET, OldWater_SongHouse_EventScript_HideVerse1
	call_if_unset FLAG_BADGE02_GET, OldWater_SongHouse_EventScript_HideVerse2
	call_if_unset FLAG_BADGE03_GET, OldWater_SongHouse_EventScript_HideVerse3
	call_if_unset FLAG_BADGE04_GET, OldWater_SongHouse_EventScript_HideVerse4
	end

OldWater_SongHouse_EventScript_HideVerse1:
	setmetatile 5, 0, 0x202, TRUE
	setmetatile 6, 0, 0x202, TRUE
	setmetatile 5, 1, 0x203, TRUE
	setmetatile 6, 1, 0x203, TRUE
	return

OldWater_SongHouse_EventScript_HideVerse2:
	setmetatile 7, 0, 0x202, TRUE
	setmetatile 8, 0, 0x202, TRUE
	setmetatile 7, 1, 0x203, TRUE
	setmetatile 8, 1, 0x203, TRUE
	return

OldWater_SongHouse_EventScript_HideVerse3:
	setmetatile 10, 0, 0x202, TRUE
	setmetatile 11, 0, 0x202, TRUE
	setmetatile 10, 1, 0x203, TRUE
	setmetatile 11, 1, 0x203, TRUE
	return

OldWater_SongHouse_EventScript_HideVerse4:
	setmetatile 12, 0, 0x202, TRUE
	setmetatile 13, 0, 0x202, TRUE
	setmetatile 12, 1, 0x203, TRUE
	setmetatile 13, 1, 0x203, TRUE
	return

@ step 8: the trust event; step 10: the first verse
OldWater_SongHouse_EventScript_Tupelo0::
	lock
	faceplayer
	goto_if_eq VAR_ORLEANS_STORY, 5, OldWater_SongHouse_EventScript_TupeloTrust
	goto_if_eq VAR_ORLEANS_STORY, 21, OldWater_SongHouse_EventScript_TupeloVerse4Entry
	goto_if_set FLAG_CARVING_FOUND, OldWater_SongHouse_EventScript_TupeloCarvingCheck
	goto_if_ge VAR_ORLEANS_STORY, 22, OldWater_SongHouse_EventScript_TupeloLater
	goto_if_eq VAR_ORLEANS_STORY, 7, OldWater_SongHouse_EventScript_TupeloFirstVerse
	goto_if_ge VAR_ORLEANS_STORY, 8, OldWater_SongHouse_EventScript_TupeloAfterVerse
	msgbox OldWater_SongHouse_Text_TupeloBringVerse, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_TupeloTrust:
	msgbox OldWater_SongHouse_Text_TupeloTrust, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 6
	release
	end

OldWater_SongHouse_EventScript_TupeloFirstVerse:
	msgbox OldWater_SongHouse_Text_TupeloFirstVerse, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 8
	release
	end

OldWater_SongHouse_EventScript_TupeloAfterVerse:
	goto_if_set FLAG_BADGE02_GET, OldWater_SongHouse_EventScript_TupeloSecondVerse
	msgbox OldWater_SongHouse_Text_TupeloAfterVerse, MSGBOX_DEFAULT
	release
	end

@ Ch2: the second verse is on the wall (the panel lights with the badge). No forced visit: Tupelo only remarks on it.
OldWater_SongHouse_EventScript_TupeloSecondVerse:
	msgbox OldWater_SongHouse_Text_TupeloSecondVerse, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_Text_TupeloSecondVerse:
	.string "TUPELO: The second verse is up.\n"
	.string "Light, running down the wires.\p"
	.string "Interesting, what the outsiders\n"
	.string "do with a phrase like 'lay down'.\p"
	.string "Six verses left. Go on.$"

OldWater_SongHouse_Text_TupeloTrust:
	.string "TUPELO: So you're the one who\n"
	.string "stood between WREN and that boy.\p"
	.string "Outsiders have taken our songs\n"
	.string "before. They took them wrong.\p"
	.string "The telling has eight verses.\n"
	.string "Eight SINGERS keep them, spread\l"
	.string "across the land.\p"
	.string "The first is MAGNOLIA, in\n"
	.string "GRAND OAK.\p"
	.string "Bring me her verse, and I'll know\n"
	.string "the water trusts you.$"

OldWater_SongHouse_Text_TupeloBringVerse:
	.string "TUPELO: MAGNOLIA keeps the first\n"
	.string "verse. GRAND OAK is north of the\l"
	.string "boat landing.$"

OldWater_SongHouse_Text_TupeloFirstVerse:
	.string "TUPELO: You have it. I can hear\n"
	.string "it on you, like rain on a roof.\p"
	.string "Look. The first verse is back\n"
	.string "on the wall.\p"
	.string "“The water rose, and the land\n"
	.string "was afraid...”\p"
	.string "That's how it begins. Not with\n"
	.string "a hunt. Remember that.$"

OldWater_SongHouse_Text_TupeloAfterVerse:
	.string "TUPELO: Seven verses left.\n"
	.string "The water is patient.$"

@ Ch3: the Drowned Ward carving (story 17). Shown once; the old carvers' word for the lay-down verse is a mistranslation.
OldWater_SongHouse_EventScript_TupeloCarvingCheck:
	goto_if_unset FLAG_CARVING_SHOWN_TUPELO, OldWater_SongHouse_EventScript_TupeloCarving
	goto_if_ge VAR_ORLEANS_STORY, 22, OldWater_SongHouse_EventScript_TupeloLater
	goto_if_eq VAR_ORLEANS_STORY, 7, OldWater_SongHouse_EventScript_TupeloFirstVerse
	goto_if_set FLAG_BADGE02_GET, OldWater_SongHouse_EventScript_TupeloSecondVerse
	msgbox OldWater_SongHouse_Text_TupeloAfterVerse, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_TupeloCarving:
	setflag FLAG_CARVING_SHOWN_TUPELO
	msgbox OldWater_SongHouse_Text_TupeloCarving, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_Text_TupeloCarving:
	.string "TUPELO: You found a carving under\nthe city? Show me. Tell me.\p"
	.string "The old word we sing as 'lay\ndown'... the carvers meant 'laid\p"
	.string "low'. Sunk, not rested. We have\nbeen singing a drowning.\p"
	.string "Keep walking. The next Singer\nwill know what to do with it.$"

@ ---------------------------------------------------------------- Ch4 beat 4.6: the midpoint visit (story 21 -> 22)
@ Kingfisher's verse is sung back where the river hears it: the fourth verse clears the Route 6 storm debris
@ (FLAG_ROUTE6_DEBRIS_CLEARED, decision 3: verses clear water obstacles), Tupelo gives the first true piece of the telling (the
@ "laid down to guard" reading: the carving's "laid low" was chipped), and the Rootkin give the player HM Surf (decision 3
@ follow-up: Surf, not a boat). Bag-full safe: the debris flag marks the first half done; the story value moves to 22 only once
@ HM Surf is in the bag, so talking to Tupelo again retries. Wren's friendly battle and the Rockruff are Wren1's, open from story 22.
@ the carving scene (Ch3) comes first if the player has found the carving and Tupelo has not seen it yet
OldWater_SongHouse_EventScript_TupeloVerse4Entry:
	goto_if_unset FLAG_CARVING_FOUND, OldWater_SongHouse_EventScript_TupeloVerse4
	goto_if_set FLAG_CARVING_SHOWN_TUPELO, OldWater_SongHouse_EventScript_TupeloVerse4
	setflag FLAG_CARVING_SHOWN_TUPELO
	msgbox OldWater_SongHouse_Text_TupeloCarving, MSGBOX_DEFAULT
OldWater_SongHouse_EventScript_TupeloVerse4:
	goto_if_set FLAG_ROUTE6_DEBRIS_CLEARED, OldWater_SongHouse_EventScript_TupeloGiveSurf
	msgbox OldWater_SongHouse_Text_Verse4A, MSGBOX_DEFAULT
	msgbox OldWater_SongHouse_Text_Verse4B, MSGBOX_DEFAULT
	msgbox OldWater_SongHouse_Text_Verse4C, MSGBOX_DEFAULT
	setflag FLAG_ROUTE6_DEBRIS_CLEARED
OldWater_SongHouse_EventScript_TupeloGiveSurf:
	goto_if_set FLAG_RECEIVED_HM_SURF, OldWater_SongHouse_EventScript_TupeloSurfDone
	msgbox OldWater_SongHouse_Text_Verse4D, MSGBOX_DEFAULT
	giveitem ITEM_HM_SURF
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_HM_SURF
OldWater_SongHouse_EventScript_TupeloSurfDone:
	call_if_lt VAR_ORLEANS_STORY, 22, OldWater_SongHouse_EventScript_SetStory22
	msgbox OldWater_SongHouse_Text_Verse4E, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_SetStory22:
	setvar VAR_ORLEANS_STORY, 22
	return

OldWater_SongHouse_EventScript_TupeloLater:
	goto_if_set FLAG_BADGE05_GET, OldWater_SongHouse_EventScript_TupeloLater5
	msgbox OldWater_SongHouse_Text_TupeloLater, MSGBOX_DEFAULT
	release
	end

@ Ch5: the brothers' verse (the song house's wall has panels for verses 1-4 only: no art for 5-8 yet, see the plan's open questions)
OldWater_SongHouse_EventScript_TupeloLater5:
	msgbox OldWater_SongHouse_Text_TupeloLater5, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_Wren1::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 22, OldWater_SongHouse_EventScript_WrenWait
	goto_if_set FLAG_RECEIVED_ROCKRUFF, OldWater_SongHouse_EventScript_WrenRematch
	msgbox OldWater_SongHouse_Text_WrenShow, MSGBOX_DEFAULT
	closemessage
	call OldWater_SongHouse_EventScript_WrenBattle
	msgbox OldWater_SongHouse_Text_WrenGift, MSGBOX_DEFAULT
	givemon SPECIES_ROCKRUFF_OWN_TEMPO, 22
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, OldWater_SongHouse_EventScript_WrenNoRoom
	setflag FLAG_RECEIVED_ROCKRUFF
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, OldWater_SongHouse_EventScript_WrenToPC
	msgbox OldWater_SongHouse_Text_WrenGiven, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_WrenToPC:
	call Common_EventScript_TransferredToPC
	msgbox OldWater_SongHouse_Text_WrenGiven, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_WrenNoRoom:
	call Common_EventScript_NoMoreRoomForPokemon
	release
	end

OldWater_SongHouse_EventScript_WrenWait:
	msgbox OldWater_SongHouse_Text_WrenWait, MSGBOX_DEFAULT
	release
	end

@ a friendly rematch whenever the player likes (no bag or party is touched)
OldWater_SongHouse_EventScript_WrenRematch:
	msgbox OldWater_SongHouse_Text_WrenRematch, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OldWater_SongHouse_EventScript_WrenNoRematch
	closemessage
	call OldWater_SongHouse_EventScript_WrenBattle
	msgbox OldWater_SongHouse_Text_WrenBattleAfter, MSGBOX_DEFAULT
	release
	end

OldWater_SongHouse_EventScript_WrenNoRematch:
	msgbox OldWater_SongHouse_Text_WrenNoRematch, MSGBOX_DEFAULT
	release
	end

@ Wren raised the starter that neither the player nor Jayden took (VAR_STARTER_MON: 0 = Totodile -> she has Fuecoco, ...)
OldWater_SongHouse_EventScript_WrenBattle:
	call_if_eq VAR_STARTER_MON, 0, OldWater_SongHouse_EventScript_WrenBattleFuecoco
	call_if_eq VAR_STARTER_MON, 1, OldWater_SongHouse_EventScript_WrenBattleTotodile
	call_if_eq VAR_STARTER_MON, 2, OldWater_SongHouse_EventScript_WrenBattleChikorita
	special HealPlayerParty
	return

OldWater_SongHouse_EventScript_WrenBattleFuecoco:
	trainerbattle_no_intro TRAINER_ORLEANS_WREN_OLD_WATER_FUECOCO, OldWater_SongHouse_Text_WrenDefeat
	return

OldWater_SongHouse_EventScript_WrenBattleTotodile:
	trainerbattle_no_intro TRAINER_ORLEANS_WREN_OLD_WATER_TOTODILE, OldWater_SongHouse_Text_WrenDefeat
	return

OldWater_SongHouse_EventScript_WrenBattleChikorita:
	trainerbattle_no_intro TRAINER_ORLEANS_WREN_OLD_WATER_CHIKORITA, OldWater_SongHouse_Text_WrenDefeat
	return

OldWater_SongHouse_Text_Verse4A:
	.string "TUPELO: KINGFISHER's verse. You hold\nthe fourth. The first net, the first\p"
	.string "boat. The river as a road, not a\nwall. I have always known it.$"

OldWater_SongHouse_Text_Verse4B:
	.string "TUPELO: Hear a piece I never gave\nanyone. The carving you found said\p"
	.string "“laid low”, and the chip took the\nrest. My grandmother sang it whole:\p"
	.string "“...the Long One laid down to guard\nthe river's bed.” Laid DOWN, child.\p"
	.string "Not low. I thought it a lullaby.\nIt may be the truth.$"

OldWater_SongHouse_Text_Verse4C:
	.string "TUPELO: Sung where the river hears,\na verse clears the river's way.\p"
	.string "Listen. ...Somewhere west, a jam of\nstorm wood has just let go.$"

OldWater_SongHouse_Text_Verse4D:
	.string "TUPELO: But a road you can't walk is\nonly a picture. The Rootkin stand\p"
	.string "on the water. Take this, and teach\nit to a POKéMON that can carry you.\p"
	.string "It is SURF. Mind the currents.$"

OldWater_SongHouse_Text_Verse4E:
	.string "TUPELO: The way west is open now.\nThe old songs say it opens, one\p"
	.string "verse at a time. WREN waits in the\nsong house. She has something to\p"
	.string "show you.$"

OldWater_SongHouse_Text_TupeloLater:
	.string "TUPELO: Four verses, and the river\nlistens. Four more to bring home.\p"
	.string "Go on. The water remembers you.$"

OldWater_SongHouse_Text_WrenWait:
	.string "WREN: Tupelo's in a mood. Something\nabout verses and rivers. Go on.$"

OldWater_SongHouse_Text_WrenShow:
	.string "WREN: There you are! The river road\nis yours, and the wind. See the one\p"
	.string "I raised? She's been waiting to be\nshown off. Friendly battle!$"

OldWater_SongHouse_Text_WrenDefeat:
	.string "WREN: Oh! You're good. Really good.$"

OldWater_SongHouse_Text_WrenGift:
	.string "WREN: Here. A ROCKRUFF. The Rootkin\nraise them with an Own Tempo, calm\p"
	.string "and unbothered. Nothing rattles it.\nTake care of it, and it of you.$"

OldWater_SongHouse_Text_WrenGiven:
	.string "{PLAYER} received ROCKRUFF from WREN!$"

OldWater_SongHouse_Text_WrenRematch:
	.string "WREN: Another friendly battle?$"

OldWater_SongHouse_Text_WrenBattleAfter:
	.string "WREN: Good battle! Tell me when you\nhave another verse to show me.$"

OldWater_SongHouse_Text_WrenNoRematch:
	.string "WREN: Anytime. The song house is\nalways open.$"

OldWater_SongHouse_Text_TupeloLater5:
	.string "TUPELO: Five verses. The people ate\n"
	.string "together and the land was fed. I can\p"
	.string "hear the table in it. The wall has\n"
	.string "no room for it yet. We'll carve one.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

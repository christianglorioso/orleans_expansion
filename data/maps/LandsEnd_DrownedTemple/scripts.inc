LandsEnd_DrownedTemple_MapScripts::
	.byte 0

@ The Drowned Temple's Tide Hall (Chapter 9, F.1): the sealed door opens when the player sings Heron's verse (story >= 39), Kyogre waits in the
@ hall. A trainer battle with Primal Kyogre (its Blue Orb makes Primordial Sea: Fire attacks fail all fight); a win calms it (FLAG_KYOGRE_CALMED).
@ The exit mat leaves by script to the end of Route 22.
LandsEnd_DrownedTemple_EventScript_TheSealed0::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 39, LandsEnd_DrownedTemple_EventScript_DoorSealed
	msgbox LandsEnd_DrownedTemple_Text_DoorSing, MSGBOX_DEFAULT
	setflag FLAG_TEMPLE_DOOR_OPEN
	removeobject LOCALID_LANDS_END_DROWNED_TEMPLE_THE_SEALED0
	releaseall
	end

LandsEnd_DrownedTemple_EventScript_DoorSealed:
	msgbox LandsEnd_DrownedTemple_Text_DoorSealed, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_DrownedTemple_EventScript_KyogreRaid1::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 39, LandsEnd_DrownedTemple_EventScript_NotYet
	msgbox LandsEnd_DrownedTemple_Text_KyogreIntro, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_ORLEANS_KYOGRE_RAID, LandsEnd_DrownedTemple_Text_KyogreDefeat
	msgbox LandsEnd_DrownedTemple_Text_KyogreCalm, MSGBOX_DEFAULT
	setflag FLAG_KYOGRE_CALMED
	setflag FLAG_HIDE_KYOGRE_RAID
	removeobject LOCALID_LANDS_END_DROWNED_TEMPLE_KYOGRE_RAID1
	goto LandsEnd_DrownedTemple_EventScript_RaidDone

LandsEnd_DrownedTemple_EventScript_NotYet:
	msgbox LandsEnd_DrownedTemple_Text_NotYet, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_DrownedTemple_EventScript_Exit::
	lockall
	fadescreen FADE_TO_BLACK
	warpsilent MAP_ORLEANS_ROUTE22, 13, 20
	waitstate
	releaseall
	end

@ The second raid done: story 40, the channel to the Oldest Shrine opens (FLAG_ROUTE25_OPEN), and the dusk ceremony at the Old Water follows.
LandsEnd_DrownedTemple_EventScript_RaidDone:
	goto_if_unset FLAG_GROUDON_CALMED, LandsEnd_DrownedTemple_EventScript_OneLeft
	setflag FLAG_ROUTE25_OPEN
	call_if_eq VAR_ORLEANS_STORY, 39, LandsEnd_DrownedTemple_EventScript_SetStory40
	msgbox LandsEnd_DrownedTemple_Text_BothDone, MSGBOX_DEFAULT
	closemessage
	setvar VAR_OLD_WATER_CEREMONY, 1
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER, 22, 32
	waitstate
	releaseall
	end

LandsEnd_DrownedTemple_EventScript_SetStory40:
	setvar VAR_ORLEANS_STORY, 40
	return

LandsEnd_DrownedTemple_EventScript_OneLeft:
	msgbox LandsEnd_DrownedTemple_Text_OneLeft, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_DrownedTemple_Text_DoorSealed:
	.string "A sealed door carved with waves. It\n"
	.string "hums, waiting for a song.$"

LandsEnd_DrownedTemple_Text_DoorSing:
	.string "You sing HERON's verse: the Long One\n"
	.string "lay down to guard, not to die.\p"
	.string "The carved waves ripple, and the\n"
	.string "door slides into the floor.$"

LandsEnd_DrownedTemple_Text_KyogreIntro:
	.string "The Tide Hall is a dome of held air.\n"
	.string "KYOGRE rises from the water, its\p"
	.string "markings glowing red and blue. The\n"
	.string "sea around you thickens.$"

LandsEnd_DrownedTemple_Text_KyogreDefeat:
	.string "KYOGRE sinks back, its glow dimming.$"

LandsEnd_DrownedTemple_Text_KyogreCalm:
	.string "The song reaches it. KYOGRE settles\n"
	.string "like a tide going out, and the dome\p"
	.string "goes still. The sea remembers.$"

LandsEnd_DrownedTemple_Text_OneLeft:
	.string "One sleeper is calm. The other waits\n"
	.string "in the salt, below ROUTE 24.$"

LandsEnd_DrownedTemple_Text_BothDone:
	.string "Far away, a storm wall breaks. The\n"
	.string "channel to the SHRINE is open. A\p"
	.string "pale light calls from the OLD\n"
	.string "WATER.$"

LandsEnd_DrownedTemple_Text_NotYet:
	.string "The water pulls at you. Not yet.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

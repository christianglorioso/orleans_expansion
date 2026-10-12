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

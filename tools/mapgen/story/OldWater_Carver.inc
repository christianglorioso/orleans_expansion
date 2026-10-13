OldWater_Carver_MapScripts::
	.byte 0

@ The carver finishes the cypress-wood charm (Chapter 6, 6.6): the Mega Evolution key item (ITEM_MEGA_RING, renamed "Cypress Charm"; the
@ engine's Mega Evolution needs it in the bag). Needs verse 6 sung to Tupelo (FLAG_VERSE6_HEARD), story >= 29. Bag-full safe (the flag is
@ set after the charm is in the bag); story 30 only from 29.
OldWater_Carver_EventScript_Carver0::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_CYPRESS_CHARM, OldWater_Carver_EventScript_Done
	goto_if_set FLAG_VERSE6_HEARD, OldWater_Carver_EventScript_GiveCharm
	goto_if_unset FLAG_BADGE06_GET, OldWater_Carver_EventScript_Plain
	goto_if_lt VAR_ORLEANS_STORY, 38, OldWater_Carver_EventScript_Plain
OldWater_Carver_EventScript_GiveCharm:
	msgbox OldWater_Carver_Text_Gives, MSGBOX_DEFAULT
	giveitem ITEM_MEGA_RING
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_CYPRESS_CHARM
	call_if_eq VAR_ORLEANS_STORY, 29, OldWater_Carver_EventScript_SetStory30
	msgbox OldWater_Carver_Text_Explain, MSGBOX_DEFAULT
	release
	end

OldWater_Carver_EventScript_SetStory30:
	setvar VAR_ORLEANS_STORY, 30
	return

OldWater_Carver_EventScript_Plain:
	msgbox OldWater_Carver_Text_Plain, MSGBOX_DEFAULT
	release
	end

OldWater_Carver_EventScript_Done:
	msgbox OldWater_Carver_Text_Done, MSGBOX_DEFAULT
	release
	end

OldWater_Carver_Text_Plain:
	.string "CARVER: Cypress keeps its shape\nlonger than any of us.$"

OldWater_Carver_Text_Gives:
	.string "CARVER: TUPELO's word: six verses.\nI carved this the night the storm\p"
	.string "came, and kept it unfinished.\nHold out your hands.\p"
	.string "{PLAYER} received the CYPRESS CHARM!$"

OldWater_Carver_Text_Explain:
	.string "CARVER: The charm listens to the\nstones. A POKéMON holding a MEGA\p"
	.string "STONE will answer it in battle.\nThe vendor in CRESCENT CITY sells\p"
	.string "stones now. Spend wisely.$"

OldWater_Carver_Text_Done:
	.string "CARVER: The charm is yours. Wood\nremembers who carved it. And who\p"
	.string "carried it.$"


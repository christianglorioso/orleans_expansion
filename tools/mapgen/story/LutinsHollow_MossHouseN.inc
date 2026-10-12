LutinsHollow_MossHouseN_MapScripts::
	.byte 0

@ The riddler: three riddles (VAR_HOLLOW_RIDDLES counts the answered ones, 0-3; a wrong answer costs nothing), and then the Delphoxite
@ (obtainability.md: Delphox's Mega Stone). Open once Lutin has been beaten (story >= 29). Bag-full safe: the flag is set after the stone
@ is in the bag, and the riddles stay solved.
LutinsHollow_MossHouseN_EventScript_Riddler0::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_DELPHOXITE, LutinsHollow_MossHouseN_EventScript_Done
	goto_if_lt VAR_ORLEANS_STORY, 29, LutinsHollow_MossHouseN_EventScript_Later
	goto_if_eq VAR_HOLLOW_RIDDLES, 3, LutinsHollow_MossHouseN_EventScript_Gives
	goto_if_eq VAR_HOLLOW_RIDDLES, 2, LutinsHollow_MossHouseN_EventScript_Riddle3
	goto_if_eq VAR_HOLLOW_RIDDLES, 1, LutinsHollow_MossHouseN_EventScript_Riddle2
	msgbox LutinsHollow_MossHouseN_Text_Intro, MSGBOX_DEFAULT
	msgbox LutinsHollow_MossHouseN_Text_Riddle1, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, LutinsHollow_MossHouseN_Text_A1a, LutinsHollow_MossHouseN_Text_A1b, LutinsHollow_MossHouseN_Text_A1c
	switch VAR_RESULT
	case 0, LutinsHollow_MossHouseN_EventScript_Right
	goto LutinsHollow_MossHouseN_EventScript_Wrong

LutinsHollow_MossHouseN_EventScript_Riddle2:
	msgbox LutinsHollow_MossHouseN_Text_Riddle2, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, LutinsHollow_MossHouseN_Text_A2a, LutinsHollow_MossHouseN_Text_A2b, LutinsHollow_MossHouseN_Text_A2c
	switch VAR_RESULT
	case 1, LutinsHollow_MossHouseN_EventScript_Right
	goto LutinsHollow_MossHouseN_EventScript_Wrong

LutinsHollow_MossHouseN_EventScript_Riddle3:
	msgbox LutinsHollow_MossHouseN_Text_Riddle3, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, LutinsHollow_MossHouseN_Text_A3a, LutinsHollow_MossHouseN_Text_A3b, LutinsHollow_MossHouseN_Text_A3c
	switch VAR_RESULT
	case 2, LutinsHollow_MossHouseN_EventScript_Right
	goto LutinsHollow_MossHouseN_EventScript_Wrong

LutinsHollow_MossHouseN_EventScript_Right:
	addvar VAR_HOLLOW_RIDDLES, 1
	goto_if_eq VAR_HOLLOW_RIDDLES, 3, LutinsHollow_MossHouseN_EventScript_Gives
	msgbox LutinsHollow_MossHouseN_Text_Right, MSGBOX_DEFAULT
	release
	end

LutinsHollow_MossHouseN_EventScript_Wrong:
	msgbox LutinsHollow_MossHouseN_Text_Wrong, MSGBOX_DEFAULT
	release
	end

LutinsHollow_MossHouseN_EventScript_Gives:
	msgbox LutinsHollow_MossHouseN_Text_Gives, MSGBOX_DEFAULT
	giveitem ITEM_DELPHOXITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_DELPHOXITE
	release
	end

LutinsHollow_MossHouseN_EventScript_Later:
	msgbox LutinsHollow_MossHouseN_Text_Later, MSGBOX_DEFAULT
	release
	end

LutinsHollow_MossHouseN_EventScript_Done:
	msgbox LutinsHollow_MossHouseN_Text_Done, MSGBOX_DEFAULT
	release
	end

LutinsHollow_MossHouseN_Text_Later:
	.string "RIDDLER: Riddles are for people who\n"
	.string "have already been fooled once.\p"
	.string "Meet LUTIN. Then come back.$"

LutinsHollow_MossHouseN_Text_Intro:
	.string "RIDDLER: Fooled by the moss? Good.\n"
	.string "Now try me. Three riddles. Get\p"
	.string "them right and a stone is yours.\n"
	.string "Get one wrong and I'll just\p"
	.string "chuckle and ask again.$"

LutinsHollow_MossHouseN_Text_Riddle1:
	.string "RIDDLER: I follow you in the light,\n"
	.string "I vanish in the dark, and I have\p"
	.string "never said a word. What am I?$"

LutinsHollow_MossHouseN_Text_Riddle2:
	.string "RIDDLER: The more you take from me,\n"
	.string "the larger I get. What am I?$"

LutinsHollow_MossHouseN_Text_Riddle3:
	.string "RIDDLER: What does the water show\n"
	.string "that isn't the water?$"

LutinsHollow_MossHouseN_Text_A1a:
	.string "A shadow$"

LutinsHollow_MossHouseN_Text_A1b:
	.string "An echo$"

LutinsHollow_MossHouseN_Text_A1c:
	.string "A fog$"

LutinsHollow_MossHouseN_Text_A2a:
	.string "A debt$"

LutinsHollow_MossHouseN_Text_A2b:
	.string "A hole$"

LutinsHollow_MossHouseN_Text_A2c:
	.string "A secret$"

LutinsHollow_MossHouseN_Text_A3a:
	.string "A storm$"

LutinsHollow_MossHouseN_Text_A3b:
	.string "A fish$"

LutinsHollow_MossHouseN_Text_A3c:
	.string "A reflection$"

LutinsHollow_MossHouseN_Text_Right:
	.string "RIDDLER: Hm! Right. You may think\n"
	.string "after all. Another?$"

LutinsHollow_MossHouseN_Text_Wrong:
	.string "RIDDLER: Ha! No. Think about it,\n"
	.string "then come back. I'll wait.$"

LutinsHollow_MossHouseN_Text_Gives:
	.string "RIDDLER: Three for three! Take the\n"
	.string "stone. DELPHOXITE. It remembers\p"
	.string "a fox who set the whole hollow\n"
	.string "glowing.$"

LutinsHollow_MossHouseN_Text_Done:
	.string "RIDDLER: I've run out of riddles.\n"
	.string "Come back when you've made some.$"

PointeRouge_Pokecenter_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

PointeRouge_Pokecenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_POINTE_ROUGE_POKECENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PointeRouge_Pokecenter_EventScript_RefineryWorker1::
	msgbox PointeRouge_Pokecenter_Text_RefineryWorker1, MSGBOX_NPC
	end

PointeRouge_Pokecenter_Text_RefineryWorker1:
	.string "something's wrong at the\nplant, they sent us all home$"

PointeRouge_Pokecenter_EventScript_Angler2::
	msgbox PointeRouge_Pokecenter_Text_Angler2, MSGBOX_NPC
	end

PointeRouge_Pokecenter_Text_Angler2:
	.string "the fishing tournament on\nRoute 5 decides who faces\pKINGFISHER$"

@ --- mapgen: generated NPC scripts (end) ---

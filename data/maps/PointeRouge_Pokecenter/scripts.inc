PointeRouge_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
PointeRouge_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_POINTE_ROUGE
	end

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
	.string "Something's wrong at the plant. They\nsent every one of us home.$"

PointeRouge_Pokecenter_EventScript_Angler2::
	msgbox PointeRouge_Pokecenter_Text_Angler2, MSGBOX_NPC
	end

PointeRouge_Pokecenter_Text_Angler2:
	.string "The Route 5 tournament decides who\nmay face KINGFISHER.$"

@ --- mapgen: generated NPC scripts (end) ---

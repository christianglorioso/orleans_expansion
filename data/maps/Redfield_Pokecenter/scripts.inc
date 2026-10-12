Redfield_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Redfield_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
Redfield_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_REDFIELD
	end

@ --- mapgen: generated NPC scripts (begin) ---

Redfield_Pokecenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_REDFIELD_POKECENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

Redfield_Pokecenter_EventScript_CaneCutter1::
	msgbox Redfield_Pokecenter_Text_CaneCutter1, MSGBOX_NPC
	end

Redfield_Pokecenter_Text_CaneCutter1:
	.string "The mill's been running day and\nnight. The cane waits for no one.$"

Redfield_Pokecenter_EventScript_Hiker2::
	msgbox Redfield_Pokecenter_Text_Hiker2, MSGBOX_NPC
	end

Redfield_Pokecenter_Text_Hiker2:
	.string "the dry country north of here\nis going to dust$"

@ --- mapgen: generated NPC scripts (end) ---

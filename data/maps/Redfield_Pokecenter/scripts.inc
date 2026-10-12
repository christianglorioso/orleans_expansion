Redfield_Pokecenter_MapScripts::
	.byte 0

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
	.string "the mill's been running day\nand night$"

Redfield_Pokecenter_EventScript_Hiker2::
	msgbox Redfield_Pokecenter_Text_Hiker2, MSGBOX_NPC
	end

Redfield_Pokecenter_Text_Hiker2:
	.string "the dry country north of here\nis going to dust$"

@ --- mapgen: generated NPC scripts (end) ---

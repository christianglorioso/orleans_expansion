LandsEnd_Pokecenter_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

LandsEnd_Pokecenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_LANDS_END_POKECENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

LandsEnd_Pokecenter_EventScript_Shrimper1::
	msgbox LandsEnd_Pokecenter_Text_Shrimper1, MSGBOX_NPC
	end

LandsEnd_Pokecenter_Text_Shrimper1:
	.string "the Gulf's been strange since\nthe temple lights came on$"

LandsEnd_Pokecenter_EventScript_Hiker2::
	msgbox LandsEnd_Pokecenter_Text_Hiker2, MSGBOX_NPC
	end

LandsEnd_Pokecenter_Text_Hiker2:
	.string "the last stop before the open\nGulf$"

@ --- mapgen: generated NPC scripts (end) ---

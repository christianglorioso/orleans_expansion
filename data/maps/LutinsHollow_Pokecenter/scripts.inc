LutinsHollow_Pokecenter_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

LutinsHollow_Pokecenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_LUTINS_HOLLOW_POKECENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

LutinsHollow_Pokecenter_EventScript_Traveller1::
	msgbox LutinsHollow_Pokecenter_Text_Traveller1, MSGBOX_NPC
	end

LutinsHollow_Pokecenter_Text_Traveller1:
	.string "the moss moves when nobody's\nlooking$"

@ --- mapgen: generated NPC scripts (end) ---

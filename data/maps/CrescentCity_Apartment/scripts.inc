CrescentCity_Apartment_MapScripts::
	.byte 0

@ The landlady hands over the keys once 25 species are contributed (FLAG_APARTMENT_UNLOCKED). The secret-base-style decoration
@ system is not built yet (plan: open question 3.x): the apartment is the room itself for now.
CrescentCity_Apartment_EventScript_Landlady0::
	lock
	faceplayer
	goto_if_set FLAG_APARTMENT_UNLOCKED, CrescentCity_Apartment_EventScript_Open
	msgbox CrescentCity_Apartment_Text_Locked, MSGBOX_DEFAULT
	release
	end

CrescentCity_Apartment_EventScript_Open:
	msgbox CrescentCity_Apartment_Text_Open, MSGBOX_DEFAULT
	release
	end

CrescentCity_Apartment_Text_Locked:
	.string "LANDLADY: This one's reserved for\n"
	.string "a friend of the conservation\p"
	.string "center. Twenty-five species, the\n"
	.string "city says. Ask LAFAYETTE.$"

CrescentCity_Apartment_Text_Open:
	.string "LANDLADY: The keys are yours. Put\n"
	.string "your desks and your dolls where\p"
	.string "you like. Make it a little\n"
	.string "secret base.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

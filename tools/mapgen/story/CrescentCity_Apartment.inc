CrescentCity_Apartment_MapScripts::
	.byte 0

@ The landlady hands over the keys once 25 species are contributed (FLAG_APARTMENT_UNLOCKED). The apartment is the room itself: no
@ secret-base decoration system (the text promises none; audit ch3 S3).
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
	.string "LANDLADY: The keys are yours. It's\n"
	.string "a quiet room with a good view.\p"
	.string "Take your time. Nobody will\n"
	.string "hurry you here.$"

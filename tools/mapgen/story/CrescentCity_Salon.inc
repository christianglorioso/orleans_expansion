CrescentCity_Salon_MapScripts::
	.byte 0

@ The salon: grooms one POKéMON for ¥500 (friendship to maximum; the special is in src/orleans_services.c)
CrescentCity_Salon_EventScript_Clerk0::
	lock
	faceplayer
	msgbox CrescentCity_Salon_Text_Welcome, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_Salon_EventScript_Declined
	checkmoney 500
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Salon_EventScript_NoMoney
	getpartysize
	goto_if_eq VAR_RESULT, 0, CrescentCity_Salon_EventScript_Declined
	msgbox CrescentCity_Salon_Text_Which, MSGBOX_DEFAULT
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, CrescentCity_Salon_EventScript_Declined
	special OrleansSvc_MaxFriendship
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_Salon_EventScript_AlreadyHappy
	removemoney 500
	msgbox CrescentCity_Salon_Text_Done, MSGBOX_DEFAULT
	release
	end

CrescentCity_Salon_EventScript_AlreadyHappy:
	msgbox CrescentCity_Salon_Text_AlreadyHappy, MSGBOX_DEFAULT
	release
	end

CrescentCity_Salon_EventScript_NoMoney:
	msgbox CrescentCity_Salon_Text_NoMoney, MSGBOX_DEFAULT
	release
	end

CrescentCity_Salon_EventScript_Declined:
	msgbox CrescentCity_Salon_Text_Declined, MSGBOX_DEFAULT
	release
	end

CrescentCity_Salon_Text_Welcome:
	.string "STYLIST: Welcome to the salon! A\n"
	.string "wash, a brush, a little pampering:\p"
	.string "¥500, and your POKéMON will adore\n"
	.string "you. Shall we?$"

CrescentCity_Salon_Text_Which:
	.string "Which POKéMON deserves a treat?$"

CrescentCity_Salon_Text_Done:
	.string "STYLIST: Gorgeous! Look how it\n"
	.string "beams at you. That's a friend.$"

CrescentCity_Salon_Text_AlreadyHappy:
	.string "STYLIST: Oh, it already adores\n"
	.string "you! Nothing more I could add.$"

CrescentCity_Salon_Text_NoMoney:
	.string "STYLIST: Oh dear, that's ¥500. Come\n"
	.string "back when you've got it.$"

CrescentCity_Salon_Text_Declined:
	.string "STYLIST: Another time, then!$"

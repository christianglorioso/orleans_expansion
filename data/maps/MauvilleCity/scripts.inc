MauvilleCity_MapScripts::
	.byte 0

MauvilleCity_EventScript_RegisterWallyCall::
	lockall
	pokenavcall MauvilleCity_Text_WallyPokenavCall
	waitmessage
	delay 30
	playfanfare MUS_REGISTER_MATCH_CALL
	msgbox MauvilleCity_Text_RegisteredWally, MSGBOX_DEFAULT
	waitfanfare
	closemessage
	delay 30
	setflag FLAG_ENABLE_WALLY_MATCH_CALL
	clearflag FLAG_ENABLE_FIRST_WALLY_POKENAV_CALL
	releaseall
	end

MauvilleCity_Text_RegisteredWally::
	.string "Registered WALLY\n"
	.string "in the POKéNAV.$"

MauvilleCity_Text_WallyPokenavCall::
	.string "… … … … … …\n"
	.string "… … … … … Beep!\p"
	.string "WALLY: Oh, hello, {PLAYER}!\p"
	.string "I just wanted to tell you that\n"
	.string "my uncle bought me a POKéNAV!\p"
	.string "Now I can get in touch with you\n"
	.string "anytime, {PLAYER}!\p"
	.string "… … … … … …\n"
	.string "… … … … … Click!$"

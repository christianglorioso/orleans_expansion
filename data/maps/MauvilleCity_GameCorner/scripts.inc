MauvilleCity_GameCorner_MapScripts::
	.byte 0

MauvilleCity_GameCorner_EventScript_NoCoinCase::
	msgbox MauvilleCity_GameCorner_Text_CantPlayWithNoCoinCase, MSGBOX_DEFAULT
	releaseall
	end

MauvilleCity_GameCorner_Text_CantPlayWithNoCoinCase::
	.string "You can't play if you don't have\n"
	.string "a COIN CASE.$"

CrescentCity_Trades_MapScripts::
	.byte 0

@ The trade house (Chapter 10): three in-game trades for Alolan forms (INGAME_TRADE_ALOLAN_*; one each, flags FLAG_TRADED_ALOLAN_*)
CrescentCity_Trades_EventScript_Trader0::
	lock
	faceplayer
	goto_if_set FLAG_TRADED_ALOLAN_SANDSHREW, CrescentCity_Trades_EventScript_Done0
	ingame_trade INGAME_TRADE_ALOLAN_SANDSHREW, CrescentCity_Trades_Text_Ask0, CrescentCity_Trades_EventScript_Decline, CrescentCity_Trades_EventScript_Wrong, CrescentCity_Trades_Text_Done0
	setflag FLAG_TRADED_ALOLAN_SANDSHREW
	release
	end

CrescentCity_Trades_EventScript_Done0:
	msgbox CrescentCity_Trades_Text_After0, MSGBOX_DEFAULT
	release
	end

CrescentCity_Trades_EventScript_Trader1::
	lock
	faceplayer
	goto_if_set FLAG_TRADED_ALOLAN_VULPIX, CrescentCity_Trades_EventScript_Done1
	ingame_trade INGAME_TRADE_ALOLAN_VULPIX, CrescentCity_Trades_Text_Ask1, CrescentCity_Trades_EventScript_Decline, CrescentCity_Trades_EventScript_Wrong, CrescentCity_Trades_Text_Done1
	setflag FLAG_TRADED_ALOLAN_VULPIX
	release
	end

CrescentCity_Trades_EventScript_Done1:
	msgbox CrescentCity_Trades_Text_After1, MSGBOX_DEFAULT
	release
	end

CrescentCity_Trades_EventScript_Collector2::
	lock
	faceplayer
	goto_if_set FLAG_TRADED_ALOLAN_RAICHU, CrescentCity_Trades_EventScript_Done2
	ingame_trade INGAME_TRADE_ALOLAN_RAICHU, CrescentCity_Trades_Text_Ask2, CrescentCity_Trades_EventScript_Decline, CrescentCity_Trades_EventScript_Wrong, CrescentCity_Trades_Text_Done2
	setflag FLAG_TRADED_ALOLAN_RAICHU
	release
	end

CrescentCity_Trades_EventScript_Done2:
	msgbox CrescentCity_Trades_Text_After2, MSGBOX_DEFAULT
	release
	end

CrescentCity_Trades_EventScript_Decline::
	msgbox CrescentCity_Trades_Text_Decline, MSGBOX_DEFAULT
	release
	end

CrescentCity_Trades_EventScript_Wrong::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox CrescentCity_Trades_Text_Wrong, MSGBOX_DEFAULT
	release
	end

CrescentCity_Trades_Text_Ask0:
	.string "My Alolan {STR_VAR_2} for your\n"
	.string "{STR_VAR_1}? A fair swap.$"

CrescentCity_Trades_Text_Ask1:
	.string "My Alolan {STR_VAR_2} for your\n"
	.string "{STR_VAR_1}. Interested?$"

CrescentCity_Trades_Text_Ask2:
	.string "Forms side by side! My Alolan\n"
	.string "{STR_VAR_2} for your {STR_VAR_1}?$"

CrescentCity_Trades_Text_Decline:
	.string "Maybe another time, then.$"

CrescentCity_Trades_Text_Wrong:
	.string "That's not a {STR_VAR_1}. Nothing\n"
	.string "doing, I'm afraid.$"

CrescentCity_Trades_Text_Done0:
	.string "The Alolan form's cold as ice. Take\n"
	.string "good care of it.$"

CrescentCity_Trades_Text_Done1:
	.string "Thank you! It looks happy already.$"

CrescentCity_Trades_Text_Done2:
	.string "Side by side at last. Thank you!$"

CrescentCity_Trades_Text_After0:
	.string "The Alolan SANDSHREW likes the cold.\n"
	.string "Ice Stone, remember.$"

CrescentCity_Trades_Text_After1:
	.string "The Alolan VULPIX is the shyest of\n"
	.string "the lot. Be kind.$"

CrescentCity_Trades_Text_After2:
	.string "Two RAICHU, two worlds. Lovely.$"

OldWater_Trader_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

OldWater_Trader_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart OldWater_Trader_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
OldWater_Trader_Pokemart0:
	.2byte ITEM_NET_BALL
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ORAN_BERRY
	pokemartlistend

OldWater_Trader_EventScript_Child1::
	msgbox OldWater_Trader_Text_Child1, MSGBOX_NPC
	end

OldWater_Trader_Text_Child1:
	.string "I collect shiny shells!\nThis one's my favourite.$"

@ --- mapgen: generated NPC scripts (end) ---

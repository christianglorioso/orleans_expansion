StormsEdge_Mart_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

StormsEdge_Mart_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart StormsEdge_Mart_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
StormsEdge_Mart_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

StormsEdge_Mart_EventScript_Shopper1::
	msgbox StormsEdge_Mart_Text_Shopper1, MSGBOX_NPC
	end

StormsEdge_Mart_Text_Shopper1:
	.string "Everything electric sold out in a\nday. Batteries, bulbs, the lot!$"

@ --- mapgen: generated NPC scripts (end) ---

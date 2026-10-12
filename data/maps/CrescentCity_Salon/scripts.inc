CrescentCity_Salon_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Salon_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Salon_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Salon_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_Salon_EventScript_Client1::
	msgbox CrescentCity_Salon_Text_Client1, MSGBOX_NPC
	end

CrescentCity_Salon_Text_Client1:
	.string "my Furfrou's never looked\nbetter$"

@ --- mapgen: generated NPC scripts (end) ---

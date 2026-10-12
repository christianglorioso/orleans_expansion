CrescentCity_PelipperPost_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_PelipperPost_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_PelipperPost_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_PelipperPost_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_PelipperPost_EventScript_PelipperHandler1::
	msgbox CrescentCity_PelipperPost_Text_PelipperHandler1, MSGBOX_NPC
	end

CrescentCity_PelipperPost_Text_PelipperHandler1:
	.string "the birds know every roof in\nthe city$"

@ --- mapgen: generated NPC scripts (end) ---

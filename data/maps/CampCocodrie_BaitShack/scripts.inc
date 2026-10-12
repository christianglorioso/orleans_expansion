CampCocodrie_BaitShack_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CampCocodrie_BaitShack_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CampCocodrie_BaitShack_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CampCocodrie_BaitShack_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CampCocodrie_BaitShack_EventScript_Oldtimer1::
	msgbox CampCocodrie_BaitShack_Text_Oldtimer1, MSGBOX_NPC
	end

CampCocodrie_BaitShack_Text_Oldtimer1:
	.string "the airboat dock's where the\nshrimp is$"

@ --- mapgen: generated NPC scripts (end) ---

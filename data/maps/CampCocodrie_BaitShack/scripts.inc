CampCocodrie_BaitShack_MapScripts::
	.byte 0

@ The bait shack: Net and Dive Balls, potions and Super Repels for the bayou (the camp has no grass, so the water is the way)
CampCocodrie_BaitShack_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CampCocodrie_BaitShack_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CampCocodrie_BaitShack_Pokemart:
	.2byte ITEM_NET_BALL
	.2byte ITEM_DIVE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_SUPER_REPEL
	pokemartlistend

@ --- mapgen: generated NPC scripts (begin) ---

CampCocodrie_BaitShack_EventScript_Oldtimer1::
	msgbox CampCocodrie_BaitShack_Text_Oldtimer1, MSGBOX_NPC
	end

CampCocodrie_BaitShack_Text_Oldtimer1:
	.string "The shrimp comes off the dock.\nGASTON runs it. He fights for it.$"

@ --- mapgen: generated NPC scripts (end) ---

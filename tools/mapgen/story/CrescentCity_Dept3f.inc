CrescentCity_Dept3f_MapScripts::
	.byte 0

@ Third floor: the Mega Stone vendor (his stock opens with the cypress charm, story 30: nothing to sell before it) and the vitamin
@ clerk (Rare Candy only after the eighth badge).
CrescentCity_Dept3f_EventScript_Clerk0::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 30, CrescentCity_Dept3f_EventScript_VendorOpen
	msgbox CrescentCity_Dept3f_Text_VendorClosed, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept3f_EventScript_VendorOpen:
	msgbox CrescentCity_Dept3f_Text_VendorLater, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept3f_EventScript_Clerk1::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	goto_if_set FLAG_BADGE08_GET, CrescentCity_Dept3f_EventScript_Clerk11
	pokemart CrescentCity_Dept3f_Pokemart_Clerk10
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept3f_EventScript_Clerk11:
	pokemart CrescentCity_Dept3f_Pokemart_Clerk11
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept3f_Pokemart_Clerk10:
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CALCIUM
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_HP_UP
	pokemartlistend

	.align 2
CrescentCity_Dept3f_Pokemart_Clerk11:
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CALCIUM
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_HP_UP
	.2byte ITEM_RARE_CANDY
	pokemartlistend

CrescentCity_Dept3f_Text_VendorClosed:
	.string "MEGA STONE VENDOR: The stones are\n"
	.string "in the back, under glass.\p"
	.string "I can't sell one without the\n"
	.string "cypress charm. They'd just sit\p"
	.string "in your bag. Come back with it.$"

CrescentCity_Dept3f_Text_VendorLater:
	.string "MEGA STONE VENDOR: The charm's with\n"
	.string "you? Then the stones are, too.\p"
	.string "The cases are still being\n"
	.string "unpacked. Come back soon.$"

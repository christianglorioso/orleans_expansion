StormsEdge_SeafoodMarket_MapScripts::
	.byte 0

StormsEdge_SeafoodMarket_EventScript_Shrimper1::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_SeafoodMarket_EventScript_ShrimperRestored
	msgbox StormsEdge_SeafoodMarket_Text_ShrimperDown, MSGBOX_DEFAULT
	release
	end

StormsEdge_SeafoodMarket_EventScript_ShrimperRestored:
	msgbox StormsEdge_SeafoodMarket_Text_ShrimperRestored, MSGBOX_DEFAULT
	release
	end

StormsEdge_SeafoodMarket_Text_ShrimperDown:
	.string "The trawlers will go out again\n"
	.string "once the grid's back.$"

StormsEdge_SeafoodMarket_Text_ShrimperRestored:
	.string "Grid's back! The trawlers go out\n"
	.string "at dawn. Bring your appetite.$"

@ --- mapgen: generated NPC scripts (begin) ---

StormsEdge_SeafoodMarket_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart StormsEdge_SeafoodMarket_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
StormsEdge_SeafoodMarket_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

@ --- mapgen: generated NPC scripts (end) ---

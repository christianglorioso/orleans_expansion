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

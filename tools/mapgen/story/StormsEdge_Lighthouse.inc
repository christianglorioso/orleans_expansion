StormsEdge_Lighthouse_MapScripts::
	.byte 0

StormsEdge_Lighthouse_EventScript_Keeper0::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_Lighthouse_EventScript_KeeperRestored
	msgbox StormsEdge_Lighthouse_Text_KeeperDown, MSGBOX_DEFAULT
	release
	end

StormsEdge_Lighthouse_EventScript_KeeperRestored:
	msgbox StormsEdge_Lighthouse_Text_KeeperRestored, MSGBOX_DEFAULT
	release
	end

StormsEdge_Lighthouse_Text_KeeperDown:
	.string "The lamp's been dark since the\n"
	.string "storm. ÉCLAIR's grid will light it.$"

StormsEdge_Lighthouse_Text_KeeperRestored:
	.string "Look at that beam sweep the bay!\n"
	.string "ÉCLAIR's grid reached my lamp.$"

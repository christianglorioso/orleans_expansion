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

@ The keeper's stair up to the lamp gallery (Zapdos' lair, StormsEdge_LighthouseGallery): the stair cell (4, 2) is a trigger that always fires (see story_overlay._merge_lairs)
StormsEdge_Lighthouse_EventScript_Stair::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, StormsEdge_Lighthouse_Movement_FaceUp
	waitmovement 0
	warp MAP_STORMS_EDGE_LIGHTHOUSE_GALLERY, 10, 12
	waitstate
	end

StormsEdge_Lighthouse_Movement_FaceUp:
	face_up
	step_end

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

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
	setvar VAR_0x8004, ACH_PARALYSIS_PRO
	call LairGate_EventScript_Check
	goto_if_eq VAR_RESULT, FALSE, StormsEdge_Lighthouse_EventScript_StairSealed
	applymovement OBJ_EVENT_ID_PLAYER, StormsEdge_Lighthouse_Movement_FaceUp
	waitmovement 0
	warp MAP_STORMS_EDGE_LIGHTHOUSE_GALLERY, 10, 12
	waitstate
	end

@ Zapdos' gallery opens only for story 45 AND the Paralysis Pro trophy (Paralyze 25 Pokemon in the Battle Frontier); until then the keeper bars the stair and says what opens it
StormsEdge_Lighthouse_EventScript_StairSealed:
	msgbox StormsEdge_Lighthouse_Text_StairSealed, MSGBOX_DEFAULT
	applymovement OBJ_EVENT_ID_PLAYER, StormsEdge_Lighthouse_Movement_WalkDown
	waitmovement 0
	releaseall
	end

StormsEdge_Lighthouse_Text_StairSealed:
	.string "The stair to the lamp gallery is\n"
	.string "sealed until the game is beaten,\p"
	.string "and it needs a trophy: Paralyze 25\n"
	.string "Pokémon in the Battle Frontier.$"

StormsEdge_Lighthouse_Movement_WalkDown:
	walk_down
	step_end

StormsEdge_Lighthouse_Movement_FaceUp:
	face_up
	step_end

StormsEdge_HouseC_MapScripts::
	.byte 0

@ The old fisherman. (The mockup note said he gives a Good Rod once the grid is back; the Good Rod is the Route 5 angler's in
@ Chapter 4, so he only talks about the fish.)
StormsEdge_HouseC_EventScript_OldFisherman0::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_HouseC_EventScript_FishermanRestored
	msgbox StormsEdge_HouseC_Text_FishermanDown, MSGBOX_DEFAULT
	release
	end

StormsEdge_HouseC_EventScript_FishermanRestored:
	msgbox StormsEdge_HouseC_Text_FishermanRestored, MSGBOX_DEFAULT
	release
	end

StormsEdge_HouseC_Text_FishermanDown:
	.string "After a blow the fish crowd the\n"
	.string "river mouth. Not that I can see\p"
	.string "to fish in the dark. Come back\n"
	.string "when the lights are on.$"

StormsEdge_HouseC_Text_FishermanRestored:
	.string "Lights are on and the fish are\n"
	.string "biting. Try the river mouth with\p"
	.string "a rod, young one. They love the\n"
	.string "noise of the generators.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

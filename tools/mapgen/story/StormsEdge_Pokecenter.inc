StormsEdge_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, StormsEdge_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point (the slice's other centers get the same line in their own story files)
StormsEdge_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_STORMS_EDGE
	end

@ The lineworker on his break: the line past the drawbridge is the last one down, until Eclair's trial is done
StormsEdge_Pokecenter_EventScript_Lineworker1::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_Pokecenter_EventScript_LineworkerRestored
	msgbox StormsEdge_Pokecenter_Text_LineworkerDown, MSGBOX_DEFAULT
	release
	end

StormsEdge_Pokecenter_EventScript_LineworkerRestored:
	msgbox StormsEdge_Pokecenter_Text_LineworkerRestored, MSGBOX_DEFAULT
	release
	end

StormsEdge_Pokecenter_Text_LineworkerDown:
	.string "The line past the drawbridge is the\n"
	.string "last one down. ÉCLAIR's crew is\p"
	.string "on it. The generator here just\n"
	.string "has to hold out a little longer.$"

StormsEdge_Pokecenter_Text_LineworkerRestored:
	.string "Every line's live, all the way to\n"
	.string "the causeway. The generator can\p"
	.string "finally rest. So can I!$"

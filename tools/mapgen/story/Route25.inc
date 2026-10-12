Route25_MapScripts::
	.byte 0

@ Finale gate: the channel to the Oldest Shrine (Route 25, row 20) stays shut until BOTH raids are done; the finale script
@ sets FLAG_ROUTE25_OPEN when FLAG_KYOGRE_CALMED and FLAG_GROUDON_CALMED are both set.
Route25_EventScript_WaterGate::
	lockall
	goto_if_set FLAG_ROUTE25_OPEN, Route25_EventScript_WaterGateOpen
	msgbox Route25_Text_WaterGate, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route25_Movement_TurnBack
	waitmovement 0
Route25_EventScript_WaterGateOpen:
	releaseall
	end

Route25_Movement_TurnBack:
	walk_down
	step_end

Route25_Text_WaterGate:
	.string "The channel ahead boils under a wall\nof storm. Nothing can cross it.\p"
	.string "Not until the two great ones are\ncalmed.$"


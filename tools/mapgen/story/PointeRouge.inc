PointeRouge_MapScripts::
	.byte 0

@ Pointe Rouge's east edge (x=65) is closed by a dust storm until Rayquaza wakes (story 38) (Route 23 and 24 are late-game). Flag-based
@ trigger on every walkable cell of the last column: stepping onto one turns the player back west. See story_data_ch3.POINTE_ROUGE.
PointeRouge_EventScript_DustStorm::
	lockall
	msgbox PointeRouge_Text_DustStorm, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, PointeRouge_Movement_StepBackWest
	waitmovement 0
	releaseall
	end

PointeRouge_Movement_StepBackWest:
	walk_left
	step_end

PointeRouge_Text_DustStorm:
	.string "A wall of red dust rolls in from\nthe plains. No one can see to cross.\p"
	.string "Nobody crosses in this. It will\nhave to blow itself out first.$"

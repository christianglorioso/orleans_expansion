SouthernIsland_Exterior_MapScripts::
	.byte 0

Ferry_EventScript_DepartIslandSouth::
	applymovement LOCALID_PLAYER, Ferry_Movement_DepartIslandBoardSouth
	waitmovement 0
	return

Ferry_EventScript_DepartIslandWest::
	applymovement LOCALID_PLAYER, Ferry_Movement_DepartIslandBoardWest
	waitmovement 0
	return

Ferry_Movement_DepartIslandBoardSouth::
	walk_down
	step_end

Ferry_Movement_DepartIslandBoardWest::
	walk_left
	walk_in_place_faster_down
	step_end

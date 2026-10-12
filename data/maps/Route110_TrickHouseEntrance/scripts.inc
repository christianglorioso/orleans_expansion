Route110_TrickHouseEntrance_MapScripts::
	.byte 0

Route110_TrickHouseEntrance_Text_DoorLockedWriteSecretCodeHere::
	.string "The door is locked.\p"
	.string "…On closer inspection, this is written\n"
	.string "on it: “Write the secret code here.”$"

Route110_TrickHousePuzzle1_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_1_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle1_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_1_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle2_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_2_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle2_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_2_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle3_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_3_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle3_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_3_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle4_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_4_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle4_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_4_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle5_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_5_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle5_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_5_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle6_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_6_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle6_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_6_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle7_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_7_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle7_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_7_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle8_EventScript_Door::
	goto_if_eq VAR_TRICK_HOUSE_PUZZLE_8_STATE, 0, Route110_TrickHousePuzzle_EventScript_DoorLocked
	msgbox Route110_TrickHousePuzzle8_Text_WroteSecretCodeLockOpened, MSGBOX_DEFAULT
	playse SE_PIN
	setvar VAR_TRICK_HOUSE_PUZZLE_8_STATE, 2
	setmetatile 13, 1, METATILE_TrickHousePuzzle_Stairs_Down, FALSE
	special DrawWholeMapView
	releaseall
	end

Route110_TrickHousePuzzle_EventScript_Door::
	lockall
	switch VAR_TRICK_HOUSE_LEVEL
	case 0, Route110_TrickHousePuzzle1_EventScript_Door
	case 1, Route110_TrickHousePuzzle2_EventScript_Door
	case 2, Route110_TrickHousePuzzle3_EventScript_Door
	case 3, Route110_TrickHousePuzzle4_EventScript_Door
	case 4, Route110_TrickHousePuzzle5_EventScript_Door
	case 5, Route110_TrickHousePuzzle6_EventScript_Door
	case 6, Route110_TrickHousePuzzle7_EventScript_Door
	case 7, Route110_TrickHousePuzzle8_EventScript_Door
	end

Route110_TrickHousePuzzle_EventScript_DoorLocked::
	msgbox Route110_TrickHouseEntrance_Text_DoorLockedWriteSecretCodeHere, MSGBOX_DEFAULT
	releaseall
	end

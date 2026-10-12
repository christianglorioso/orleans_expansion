OldWater_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

OldWater_EventScript_Tupelo::
	msgbox OldWater_Text_Tupelo, MSGBOX_NPC
	end

OldWater_Text_Tupelo:
	.string "TUPELO: The water told us you\nwere coming. Sit. Listen.$"

OldWater_EventScript_Wren::
	msgbox OldWater_Text_Wren, MSGBOX_NPC
	end

OldWater_Text_Wren:
	.string "WREN: You made it! Welcome to\nthe Old Water.$"

OldWater_EventScript_Carver::
	msgbox OldWater_Text_Carver, MSGBOX_NPC
	end

OldWater_Text_Carver:
	.string "CARVER: Cypress keeps its shape\nlonger than any of us.$"

OldWater_EventScript_UxieShrine::
	msgbox OldWater_Text_UxieShrine, MSGBOX_SIGN
	end

OldWater_Text_UxieShrine:
	.string "A small stone, worn smooth.\nIt feels like being remembered.$"

@ --- mapgen: generated NPC scripts (end) ---

CrescentCity_DayCare_MapScripts::
	.byte 0

@ The Day Care uses the shared day care scripts (data/scripts/day_care.inc): the lady keeps the deposit counter, the man
@ is her husband (the Hoenn data's scripts and texts, kept as they are).
CrescentCity_DayCare_EventScript_DayCare0::
	goto Route117_PokemonDayCare_EventScript_DaycareWoman

CrescentCity_DayCare_EventScript_DayCare1::
	goto Route117_EventScript_DaycareMan

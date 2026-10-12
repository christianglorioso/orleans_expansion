Route6_MapScripts::
	.byte 0

@ Route 6's south shore path (the only land way from Crescent City to Routes 6-9) narrows to two cells at x 29; both hold a jam of
@ storm debris (objects hidden by FLAG_ROUTE6_DEBRIS_CLEARED, story_overlay.py). Decision 3: each Singer's verse clears a water obstacle, so
@ the fourth verse (Kingfisher's), sung back at the Old Water (the midpoint visit, OldWater_SongHouse.inc), clears it: that sets
@ FLAG_ROUTE6_DEBRIS_CLEARED. Debris1 and Debris2 are the same obstacle.
Route6_EventScript_Debris1::
Route6_EventScript_Debris2::
	lock
	goto_if_ge VAR_ORLEANS_STORY, 21, Route6_EventScript_DebrisVerse
	msgbox Route6_Text_Debris, MSGBOX_DEFAULT
	release
	end

Route6_EventScript_DebrisVerse:
	msgbox Route6_Text_DebrisVerse, MSGBOX_DEFAULT
	release
	end

Route6_Text_Debris:
	.string "Storm debris is jammed across the\n"
	.string "shore path. Nothing gets through.\p"
	.string "The old songs say the river clears\n"
	.string "its own way for those who know it.$"

Route6_Text_DebrisVerse:
	.string "The jam holds. You carry the fourth\n"
	.string "verse, but it hasn't been sung yet.\p"
	.string "TUPELO, at the Old Water, can sing\n"
	.string "it where the river will hear.$"

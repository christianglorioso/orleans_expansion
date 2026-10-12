Route6_MapScripts::
	.byte 0

@ Route 6's south shore path (the only land way from Crescent City to Routes 6-9) narrows to two cells at x 29; both hold a jam of
@ storm debris (objects hidden by FLAG_BADGE04_GET, story_overlay.py). Decision 3: each Singer's verse clears a water obstacle, so
@ the fourth verse (Kingfisher's) opens the way to the boat routes. Debris1 and Debris2 are the same obstacle.
Route6_EventScript_Debris1::
Route6_EventScript_Debris2::
	msgbox Route6_Text_Debris, MSGBOX_NPC
	end

Route6_Text_Debris:
	.string "Storm debris is jammed across the\n"
	.string "shore path. Nothing gets through.\p"
	.string "The old songs say the river clears\n"
	.string "its own way for those who know it.$"

Redfield_RitasOffice_MapScripts::
	.byte 0

@ Rita's office (Chapter 7): a recruiter keeps the desk. Rita herself battles at the yard gate (Redfield.inc); after the battle she is gone.
Redfield_RitasOffice_EventScript_RitaBefore0::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 32, Redfield_RitasOffice_EventScript_After
	msgbox Redfield_RitasOffice_Text_Before, MSGBOX_DEFAULT
	release
	end

Redfield_RitasOffice_EventScript_After:
	msgbox Redfield_RitasOffice_Text_After, MSGBOX_DEFAULT
	release
	end

Redfield_RitasOffice_Text_Before:
	.string "RECRUITER: Ms. RITA is out in the\n"
	.string "yard. Don't mind her CHANDELURE.$"

Redfield_RitasOffice_Text_After:
	.string "RECRUITER: She left. Out the back,\n"
	.string "the pamphlets still on her desk.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---

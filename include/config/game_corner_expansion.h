#ifndef GUARD_GAME_CORNER_EXPANSION_H
#define GUARD_GAME_CORNER_EXPANSION_H

// Orleans: the Game Corner minigames' flags and vars, claimed from the flag pool (tools/mapgen/flag_pool.py).
// Ported from the Game Corner Expansion (heyopc, agsmgmaster64); see CREDITS.md.

// Set by the Derby when it finishes a race the player won; the script that started the Derby pays it out (VAR_TEMP_4 is cleared on every map change)
#define GAME_CORNER_VAR_WINNINGS        VAR_TEMP_4

// FLAG_DERBY_RESET: the race has been generated; clear to roll a new one. FLAG_DERBY_NICKNAME: its nicknames have been generated.
#define DERBY_FLAG_NICKNAME             FLAG_DERBY_NICKNAME
#define DERBY_FLAG_RESET                FLAG_DERBY_RESET

// One var per racer: nickname id * 1000 + species * 100 + shiny * 10 + condition
#define DERBY_VAR_RACER_1               VAR_DERBY_RACER_1
#define DERBY_VAR_RACER_2               VAR_DERBY_RACER_2
#define DERBY_VAR_RACER_3               VAR_DERBY_RACER_3
#define DERBY_VAR_RACER_4               VAR_DERBY_RACER_4
#define DERBY_VAR_RACER_5               VAR_DERBY_RACER_5
#define DERBY_VAR_RACER_6               VAR_DERBY_RACER_6

#endif // GUARD_GAME_CORNER_EXPANSION_H

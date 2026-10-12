#include "global.h"
#include "test/battle.h"

// Orleans custom abilities (tools/dex/new_abilities.py). Names/rules: orleans_dex.xlsx, Notes tab.

SINGLE_BATTLE_TEST("Orleans: Bottom Feeder absorbs Grass moves and raises Attack")
{
    GIVEN {
        PLAYER(SPECIES_BARBOACH) { Ability(ABILITY_BOTTOM_FEEDER); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_VINE_WHIP); }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_BOTTOM_FEEDER);
        NONE_OF { HP_BAR(player); }
    } THEN {
        EXPECT_EQ(player->statStages[STAT_ATK], DEFAULT_STAT_STAGE + 1);
    }
}

SINGLE_BATTLE_TEST("Orleans: Cypress Knees absorbs Water moves")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_CYPRESS_KNEES); MaxHP(200); HP(100); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_WATER_GUN); }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_CYPRESS_KNEES);
    } THEN {
        EXPECT_GT(player->hp, 100);
    }
}

SINGLE_BATTLE_TEST("Orleans: Blur makes the user immune to Rock moves")
{
    GIVEN {
        PLAYER(SPECIES_SCYTHER) { Ability(ABILITY_BLUR); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_ROCK_THROW); }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_BLUR);
        NONE_OF { HP_BAR(player); }
    }
}

SINGLE_BATTLE_TEST("Orleans: Buoyancy grants Ground immunity (Levitate) and blocks forced switches (Suction Cups)")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_BUOYANCY); }
        PLAYER(SPECIES_WYNAUT);
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_EARTHQUAKE); }
        TURN { MOVE(opponent, MOVE_ROAR); }
    } SCENE {
        NONE_OF { HP_BAR(player); }
        ABILITY_POPUP(player, ABILITY_BUOYANCY);
    }
}

SINGLE_BATTLE_TEST("Orleans: Sky Scorcher sets harsh sunlight on entry")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_SKY_SCORCHER); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { ; }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_SKY_SCORCHER);
    } THEN {
        EXPECT(gBattleWeather & B_WEATHER_SUN);
    }
}

SINGLE_BATTLE_TEST("Orleans: Storm Beacon sets rain and Electric Terrain on entry")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_STORM_BEACON); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { ; }
    } THEN {
        EXPECT(gBattleWeather & B_WEATHER_RAIN);
        EXPECT_EQ(gFieldTimers.terrain, B_TERRAIN_ELECTRIC);
    }
}

SINGLE_BATTLE_TEST("Orleans: Fish Hawk boosts moves against Water-type targets", s16 damage)
{
    enum Ability ability;
    PARAMETRIZE { ability = ABILITY_KLUTZ; }
    PARAMETRIZE { ability = ABILITY_FISH_HAWK; }
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ability); }
        OPPONENT(SPECIES_MAGIKARP);
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, UQ_4_12(1.5), results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Orleans: Zydeco boosts sound moves by 1.5x", s16 damage)
{
    enum Ability ability;
    PARAMETRIZE { ability = ABILITY_KLUTZ; }
    PARAMETRIZE { ability = ABILITY_ZYDECO; }
    GIVEN {
        ASSUME(IsSoundMove(MOVE_HYPER_VOICE));
        PLAYER(SPECIES_WOBBUFFET) { Ability(ability); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_HYPER_VOICE); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, UQ_4_12(1.5), results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Orleans: Fleur-de-Lis boosts Grass and Fairy moves by 1.3x", s16 damage)
{
    enum Ability ability;
    PARAMETRIZE { ability = ABILITY_KLUTZ; }
    PARAMETRIZE { ability = ABILITY_FLEUR_DE_LIS; }
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ability); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_VINE_WHIP); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, UQ_4_12(1.3), results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Orleans: Field Burner boosts Grass moves by 1.5x in harsh sunlight", s16 damage)
{
    enum Ability ability;
    PARAMETRIZE { ability = ABILITY_KLUTZ; }
    PARAMETRIZE { ability = ABILITY_FIELD_BURNER; }
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ability); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_SUNNY_DAY); MOVE(player, MOVE_VINE_WHIP); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].damage);
    } FINALLY {
        EXPECT_MUL_EQ(results[0].damage, UQ_4_12(1.5), results[1].damage);
    }
}

SINGLE_BATTLE_TEST("Orleans: Pendulum gives sleep-inducing moves +1 priority")
{
    GIVEN {
        ASSUME(GetMoveNonVolatileStatus(MOVE_HYPNOSIS) == MOVE_EFFECT_SLEEP);
        PLAYER(SPECIES_DROWZEE) { Ability(ABILITY_PENDULUM); Speed(1); }
        OPPONENT(SPECIES_WOBBUFFET) { Speed(100); }
    } WHEN {
        TURN { MOVE(player, MOVE_HYPNOSIS); MOVE(opponent, MOVE_TACKLE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_HYPNOSIS, player);
    }
}

SINGLE_BATTLE_TEST("Orleans: Plunge Dive: first turn after entering the user gets +1 priority and crits")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_PLUNGE_DIVE); Speed(1); }
        OPPONENT(SPECIES_WOBBUFFET) { Speed(100); }
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); MOVE(opponent, MOVE_TACKLE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_TACKLE, player);
        MESSAGE("A critical hit!");
        ANIMATION(ANIM_TYPE_MOVE, MOVE_TACKLE, opponent);
    }
}

SINGLE_BATTLE_TEST("Orleans: Clinging Moss plants Leech Seed on a contact attacker")
{
    GIVEN {
        ASSUME(MoveMakesContact(MOVE_TACKLE));
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_CLINGING_MOSS); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_TACKLE); }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_CLINGING_MOSS);
    } THEN {
        EXPECT(opponent->volatiles.leechSeed);
    }
}

SINGLE_BATTLE_TEST("Orleans: Web Weaver lays Sticky Web on entry, once per battle")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_WEB_WEAVER); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { ; }
    } SCENE {
        ABILITY_POPUP(player, ABILITY_WEB_WEAVER);
    } THEN {
        EXPECT(IsHazardOnSide(B_SIDE_OPPONENT, HAZARDS_STICKY_WEB));
    }
}

SINGLE_BATTLE_TEST("Orleans: Soft Shell molts once when HP falls to half or below (Speed +2, Defense -1)")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_SOFT_SHELL); MaxHP(100); HP(60); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(opponent, MOVE_TACKLE); }
    } THEN {
        EXPECT_EQ(player->statStages[STAT_SPEED], DEFAULT_STAT_STAGE + 2);
        EXPECT_EQ(player->statStages[STAT_DEF], DEFAULT_STAT_STAGE - 1);
    }
}

SINGLE_BATTLE_TEST("Orleans: Regal Coil reverses stat changes (Contrary)")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_REGAL_COIL); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_SWORDS_DANCE); }
    } THEN {
        EXPECT_EQ(player->statStages[STAT_ATK], DEFAULT_STAT_STAGE - 2);
    }
}

SINGLE_BATTLE_TEST("Orleans: Dead Zone stops the opposing side from restoring HP")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_DEAD_ZONE); }
        OPPONENT(SPECIES_WOBBUFFET) { MaxHP(160); HP(50); Item(ITEM_LEFTOVERS); }
    } WHEN {
        TURN { MOVE(opponent, MOVE_CELEBRATE); }
    } THEN {
        EXPECT_EQ(opponent->hp, 50);
    }
}

SINGLE_BATTLE_TEST("Orleans: Live Wire adds the Electric type")
{
    GIVEN {
        PLAYER(SPECIES_ROTOM_WASH) { Ability(ABILITY_LIVE_WIRE); }
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { ; }
    } THEN {
        EXPECT(IS_BATTLER_OF_TYPE(0, TYPE_ELECTRIC));
    }
}

SINGLE_BATTLE_TEST("Orleans: Mold Breaker ignores Buoyancy's Ground immunity (the custom Levitate twins are breakable)")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_BUOYANCY); }
        OPPONENT(SPECIES_WOBBUFFET) { Ability(ABILITY_MOLD_BREAKER); }
    } WHEN {
        TURN { MOVE(opponent, MOVE_EARTHQUAKE); }
    } SCENE {
        HP_BAR(player);
    }
}

SINGLE_BATTLE_TEST("Orleans: Mold Breaker ignores Cypress Knees' Water absorption")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_CYPRESS_KNEES); }
        OPPONENT(SPECIES_WOBBUFFET) { Ability(ABILITY_MOLD_BREAKER); }
    } WHEN {
        TURN { MOVE(opponent, MOVE_WATER_GUN); }
    } SCENE {
        HP_BAR(player);
    }
}

SINGLE_BATTLE_TEST("Orleans: Lure Light traps a foe it burned")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_LURE_LIGHT); }
        OPPONENT(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WYNAUT);
    } WHEN {
        TURN { MOVE(player, MOVE_WILL_O_WISP); }
    } THEN {
        EXPECT(opponent->status1 & STATUS1_BURN);
        EXPECT(IsAbilityPreventingEscape(1));
    }
}

SINGLE_BATTLE_TEST("Orleans: Lure Light does not trap a foe burned by something else")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET) { Ability(ABILITY_LURE_LIGHT); }
        OPPONENT(SPECIES_WOBBUFFET) { Item(ITEM_FLAME_ORB); }
        OPPONENT(SPECIES_WYNAUT);
    } WHEN {
        TURN { MOVE(player, MOVE_CELEBRATE); }
    } THEN {
        EXPECT(opponent->status1 & STATUS1_BURN);
        EXPECT(!IsAbilityPreventingEscape(1));
    }
}

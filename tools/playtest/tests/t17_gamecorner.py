"""Crescent City Game Corner: Blackjack, the Gacha capsule machines, the Derby, the coin clerk and the prize counter.

Every game is entered through its own machine (a sign on the table, the capsule machine or the Derby window; the dealer and attendant are
the same entry), played for one round, and left again back into the room. The coin clerk gives the Coin Case and sells coins; the prize
counter sells a Heart Scale for coins; a save/continue keeps the coins, the scale and the Derby line-up. Gacha: a pull gives one of the nine
first-stage starters, and with all nine already caught the fallback still gives a starter (no hang)."""
from bot import Bot, enum_value
from pathlib import Path

MAP = "CrescentCity_GameCorner"
STARTERS = ["SPECIES_BULBASAUR", "SPECIES_CHARMANDER", "SPECIES_CHIKORITA", "SPECIES_TOTODILE", "SPECIES_MUDKIP",
            "SPECIES_SNIVY", "SPECIES_FENNEKIN", "SPECIES_FUECOCO", "SPECIES_QUAXLY"]
MON_DATA_SPECIES = 18          # index in enum MonData (include/pokemon.h)


def coins(b):
    return b.call("GetCoins") & 0xFFFF


def money_ptr(b):
    return b.save1() + 0x490   # gSaveBlock1Ptr->money


def money(b):
    return b.call("GetMoney", money_ptr(b))


def bag(b, item):
    it = enum_value("items.h", item)
    n = 0
    while n < 999 and b.call("CheckBagHasItem", it, n + 1) & 0xFF:
        n += 1
    return n


def last_species(b):
    return b.call("GetMonData2", b.r32(b.sym("gPlayerPartyPtr")) + (b.party_count() - 1) * 100, MON_DATA_SPECIES)


def enter(b, x, y, max_a=16):
    """stand at (x, y) of the Game Corner, face up, press A and mash A through the question (YES is the default) until a minigame is up"""
    b.warp(MAP, x, y)
    b.frames(30)
    b.press("UP", 2, 14)
    b.press("A", 4, 20)
    for _ in range(max_a):
        b.frames(30)
        if not b.in_overworld() and not b.fading():
            b.frames(60)
            return True
        b.press("A", 4, 20)
    return not b.in_overworld()


def leave(b, key="B", tries=10):
    for _ in range(tries):
        if b.in_overworld() and b.script_status() == 2:
            return True
        b.press(key, 4, 30)
        b.frames(60)
    return b.in_overworld() and b.script_status() == 2


def pull(b, wager_tens):
    """in a capsule machine: the cursor starts on the ones; LEFT to the tens, UP wager_tens times, A, then watch the pull through and the nickname prompt"""
    b.press("LEFT", 3, 8)
    for _ in range(wager_tens):
        b.press("UP", 3, 8)
    b.press("A", 4, 20)
    for _ in range(60):
        b.frames(90)
        if b.in_overworld():
            break
        b.press("A", 4, 10)
    b.settle(10)
    return b.advance_text(60)


def derby_race(b, bet_steps=1):
    """in the Derby: pick the first racer, bet 10 coins per step, run the race; returns when the screen is gone"""
    b.press("A", 4, 20)
    b.frames(30)
    for _ in range(bet_steps):
        b.press("UP", 3, 8)
    b.press("A", 4, 20)
    for _ in range(60):
        b.frames(120)
        if b.in_overworld():
            break
        b.press("A", 4, 10)
    return b.advance_text(60)


def continue_game(b):
    b.frames(1500)
    for _ in range(4):
        b.press("START", 6, 50)
    b.press("A", 6, 90)
    b.press("A", 6, 90)
    for _ in range(40):
        if b.in_overworld() and b.player_idle():
            break
        b.press("A", 4, 30)
    b.settle()


def save_game(b):
    b.press("START", 6, 30)
    for _ in range(3 if b.party_count() else 2):     # with a party the menu starts with POKEMON: SAVE is one lower
        b.press("DOWN", 6, 10)
    b.press("A", 6, 40)
    b.frames(150)
    b.press("A", 6, 40)
    b.frames(200)
    b.press("A", 6, 40)
    b.frames(900)
    for _ in range(4):
        b.press("A", 4, 60)
    b.frames(120)


def run(b, t):
    b.new_game()
    b.warp(MAP, 10, 12)
    b.frames(30)
    t.check("the Game Corner loads", b.map_name() == MAP, b.where())
    b.shot("room")

    # --- the coin clerk: the Coin Case on the first visit, then 50 coins for 1,000
    b.call("AddMoney", money_ptr(b), 5000)
    m0 = money(b)
    b.warp(MAP, 3, 9)                         # the clerk (3,7) is behind the counter cell (3,8), which is blocked: stand below it
    b.press("UP", 2, 14)                      # only turns: (3,8) is a blocked counter cell
    t.check("standing at (3,9) below the counter, the counter cell blocks the step", b.pos() == (3, 9), b.where())
    t.check("no Coin Case before the clerk", bag(b, "ITEM_COIN_CASE") == 0, "")
    b.press("A", 4, 20)
    for _ in range(14):
        b.frames(30)
        if bag(b, "ITEM_COIN_CASE") and b.script_status() == 1:
            break
        b.press("A", 4, 20)
    t.check("the clerk answers across the counter and gave the Coin Case", bag(b, "ITEM_COIN_CASE") == 1, b.where())
    for _ in range(12):                       # the sale menu: the first entry (50 coins) is the default
        b.press("A", 4, 30)
        b.frames(20)
        if coins(b) == 50:
            break
    b.advance_text(40)
    t.check("50 coins cost 1,000", coins(b) == 50 and money(b) == m0 - 1000, "coins %d money %d -> %d" % (coins(b), m0, money(b)))
    b.shot("clerk")

    # --- Blackjack: one hand through the table
    b.call("SetCoins", 500)
    t.check("the Blackjack table opens a game", enter(b, 9, 9), "%s %s" % (b.callback2_name(), b.where()))
    b.shot("bj_open")
    c0 = coins(b)
    b.press("A", 4, 20)                       # +10
    b.frames(20)
    t.check("a bet takes 10 coins", coins(b) == c0 - 10, "%d -> %d" % (c0, coins(b)))
    b.press("DOWN", 4, 10)
    b.press("DOWN", 4, 10)
    b.press("A", 4, 20)                       # BET: deal
    b.frames(120)
    b.shot("bj_dealt")
    for _ in range(12):                       # STAND until the hand is settled
        b.press("DOWN", 4, 10)
        b.press("A", 4, 30)
        b.frames(90)
    c1 = coins(b)
    t.check("one hand settled (lose: -10, push: 0, win: +10, natural: +15)", c1 - c0 in (-10, 0, 10, 15), "%d -> %d" % (c0, c1))
    b.shot("bj_settled")
    t.check("Blackjack leaves back into the room", leave(b) and b.map_name() == MAP, b.where() + " " + b.callback2_name())

    # --- Gacha, the Basic machine: one pull, a starter from the list
    b.call("SetCoins", 1000)
    t.check("the capsule machine opens", enter(b, 2, 4), b.callback2_name())
    pc0, c0 = b.party_count(), coins(b)
    pull(b, 5)                                # 50 coins
    wanted = {enum_value("species.h", s) for s in STARTERS}
    got = last_species(b) if b.party_count() > pc0 else None
    t.check("the pull gave a starter from the list for 50 coins", got in wanted and coins(b) == c0 - 50, "species %s coins %d -> %d party %d -> %d" % (got, c0, coins(b), pc0, b.party_count()))
    t.check("the Gacha left the player in the room", b.map_name() == MAP and b.script_status() == 2, b.where())
    b.shot("gacha_result")

    # --- Gacha fallback: every starter already caught (and the Great machine, whose Ultra Rare bucket holds one species): still a starter, no hang
    for s in STARTERS:
        nat = b.call("SpeciesToNationalPokedexNum", enum_value("species.h", s))
        b.call("GetSetPokedexFlag", nat, 2)    # FLAG_SET_SEEN
        b.call("GetSetPokedexFlag", nat, 3)    # FLAG_SET_CAUGHT
    b.call("SetCoins", 1000)
    t.check("the Great machine opens", enter(b, 4, 4), b.callback2_name())
    pc1 = b.party_count()
    b.press("LEFT", 3, 8)
    for _ in range(2):
        b.press("LEFT", 3, 8)                  # hundreds
    for _ in range(3):
        b.press("UP", 3, 8)                    # 300 coins (the machine's minimum is 250)
    b.press("A", 4, 20)
    for _ in range(60):
        b.frames(90)
        if b.in_overworld():
            break
        b.press("A", 4, 10)
    b.settle(10)
    b.advance_text(60)
    got2 = last_species(b) if b.party_count() > pc1 else None
    t.check("all nine starters owned: the fallback still gives a starter", got2 in wanted, "species %s party %d -> %d coins %d" % (got2, pc1, b.party_count(), coins(b)))
    t.check("the fallback pull ended in the room", b.map_name() == MAP and b.script_status() == 2, b.where())
    b.shot("gacha_fallback")

    # --- the Derby: one race (the bet leaves the case at the start), then races until a win pays out
    b.call("SetCoins", 500)
    t.check("the Derby window opens", enter(b, 13, 4), b.callback2_name())
    b.shot("derby_bet")
    t.check("the Derby line-up is made (FLAG_DERBY_RESET and the racer vars)", b.flag("FLAG_DERBY_RESET") and all(b.var("VAR_DERBY_RACER_%d" % i) > 0 for i in range(1, 7)),
            str([b.var("VAR_DERBY_RACER_%d" % i) for i in range(1, 7)]))
    racers = [b.var("VAR_DERBY_RACER_%d" % i) for i in range(1, 7)]
    c0 = coins(b)
    derby_race(b)
    c1 = coins(b)
    t.check("one race ran and the 10-coin bet was taken (or paid back)", c1 <= c0 + 100 and b.map_name() == MAP and b.script_status() == 2, "%d -> %d" % (c0, c1))
    t.check("the next race gets a new line-up (FLAG_DERBY_RESET cleared by the race)", not b.flag("FLAG_DERBY_RESET"), "")
    won = c1 > c0 - 10
    tries = 1
    while not won and tries < 30:
        b.call("SetCoins", 500)
        if not enter(b, 13, 4):
            break
        derby_race(b)
        tries += 1
        won = coins(b) > 490
    t.check("a winning bet is paid out (coins above stake-less) after %d race(s)" % tries, won, "coins %d" % coins(b))
    b.shot("derby_won")

    # --- Derby speeds (fix D3): Dodrio and Feebas read their own table rows, and Feebas really runs
    import struct

    def derby_speeds():
        p = b.r32(b.sym("sDerby"))
        fl = lambda o: [struct.unpack("<f", struct.pack("<I", b.r32(p + o + 4 * i)))[0] for i in range(6)]
        return fl(32), fl(56)

    b.call("GetNewDerby")
    for i, v in enumerate([604, 713, 614, 3, 102, 202], 1):      # Dodrio cond 4, Feebas (shiny) cond 3, Dodrio (shiny) cond 4, Doduo 1 cond 3, Doduo 2 cond 2, Doduo 3 cond 2
        b.set_var("VAR_DERBY_RACER_%d" % i, v)
    b.call("SetCoins", 500)
    t.check("the Derby window opens for the speed check", enter(b, 13, 4), b.callback2_name())
    b.frames(30)
    start, race = derby_speeds()
    t.check("Dodrio races at its own speeds 4/7 x (1+cond/10), not Doduo's 4/5 (racers 1 and 3: %s)" % ([round(race[0], 2), round(race[2], 2)]),
            abs(race[0] - 7 * (1 + 4 / 10.0)) < 0.01 and abs(start[0] - 4 * (1 + 4 / 10.0)) < 0.01 and abs(race[2] - 7 * (1 + 4 / 10.0)) < 0.01, (start, race))
    t.check("Feebas (racer 2) has real speeds, not garbage/zero: start %.2f race %.2f" % (start[1], race[1]),
            abs(start[1] - 3 * (1 + 3 / 10.0)) < 0.01 and abs(race[1] - 4 * (1 + 3 / 10.0)) < 0.01, (start, race))
    t.check("Doduo (racers 4-6) keep their table speeds", abs(race[3] - 5 * 1.3) < 0.01 and abs(race[4] - 5 * 1.2) < 0.01 and abs(race[5] - 4 * 1.2) < 0.01, race)
    c0 = coins(b)
    derby_race(b, bet_steps=1)
    t.check("a race with Feebas runs to the end (no hang) and settles the bet", b.map_name() == MAP and b.script_status() == 2 and coins(b) <= c0 + 100, "%d -> %d" % (c0, coins(b)))
    b.shot("derby_feebas_race")

    # --- the prize counter: a Heart Scale for 100 coins
    b.call("SetCoins", 500)
    hs0 = bag(b, "ITEM_HEART_SCALE")
    b.warp(MAP, 18, 4)
    b.press("UP", 2, 14)
    b.press("A", 4, 20)
    for _ in range(14):                        # intro, STONES list, HEART SCALE line, yes, the item text
        b.frames(30)
        if bag(b, "ITEM_HEART_SCALE") > hs0:
            break
        b.press("A", 4, 20)
    b.advance_text(20)
    n = bag(b, "ITEM_HEART_SCALE") - hs0
    t.check("the prize counter sold Heart Scales for 100 coins each", n >= 1 and coins(b) == 500 - 100 * n, "scales +%d coins %d" % (n, coins(b)))
    hs0 += n - 1
    for _ in range(6):
        b.press("B", 4, 30)
        b.frames(30)
    b.shot("prize")
    b.settle(6)

    # --- save and reload
    racers = [b.var("VAR_DERBY_RACER_%d" % i) for i in range(1, 7)]
    b.warp(MAP, 10, 12)
    b.frames(30)
    b.settle(6)
    save_game(b)
    out = b.out / "gc_roundtrip.sav"
    b.h.cmd("dumpsave " + _wsl(out))
    again = Bot(rom=b.rom, out_dir=b.out / "reload", save=out)
    try:
        continue_game(again)
        again.shot("reloaded")
        t.check("the save reloads in the Game Corner", again.map_name() == MAP, again.where())
        t.check("coins and the Heart Scale survived", coins(again) == coins(b) and bag(again, "ITEM_HEART_SCALE") == hs0 + 1, "coins %d scales %d" % (coins(again), bag(again, "ITEM_HEART_SCALE")))
        t.check("the Derby line-up survived", [again.var("VAR_DERBY_RACER_%d" % i) for i in range(1, 7)] == racers, "")
    finally:
        again.close()


def _wsl(p):
    from bot import wsl_path
    return wsl_path(Path(p))

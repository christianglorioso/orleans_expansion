"""Role-based set builder for the Battle Frontier redesign.

Given an Orleans species (types, stats, abilities and legal moves from the built data) it picks a role, an ability, four
legal moves, a nature, an EV spread and a held item.  Everything is deterministic: the random choices are seeded from
(species, tier, variant) so a rebuild reproduces the same ROM data.
"""
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import typechart as tc  # noqa: E402
from setitems import ItemMixin  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/dex'))
from new_abilities import NEW_ABILITIES  # noqa: E402
CUSTOM_ABILITIES = {'ABILITY_' + a[0] for a in NEW_ABILITIES}


def M(*names):
    return ["MOVE_" + n for n in names]


# ---------------------------------------------------------------------------------------------------------------------
# curated move groups (constants without the MOVE_ prefix; anything not legal for the species is skipped)
SETUP_PHYS = M("DRAGON_DANCE", "SWORDS_DANCE", "BULK_UP", "COIL", "SHELL_SMASH", "HONE_CLAWS", "WORK_UP", "CURSE", "AGILITY", "ROCK_POLISH", "VICTORY_DANCE", "FILLET_AWAY", "NO_RETREAT")
SETUP_SPEC = M("QUIVER_DANCE", "NASTY_PLOT", "CALM_MIND", "TAIL_GLOW", "SHELL_SMASH", "AGILITY", "ROCK_POLISH", "GROWTH")
BULK_SETUP_PHYS = M("BULK_UP", "COIL", "IRON_DEFENSE", "CURSE", "DEFEND_ORDER", "COTTON_GUARD", "ACID_ARMOR")
BULK_SETUP_SPEC = M("CALM_MIND", "AMNESIA", "ACID_ARMOR", "STOCKPILE")
RECOVERY = M("RECOVER", "ROOST", "SOFT_BOILED", "SLACK_OFF", "MILK_DRINK", "MOONLIGHT", "MORNING_SUN", "SYNTHESIS", "SHORE_UP", "HEAL_ORDER", "STRENGTH_SAP", "WISH", "REST", "LUNAR_BLESSING")
STATUS_MOVES = M("WILL_O_WISP", "THUNDER_WAVE", "TOXIC", "SPORE", "SLEEP_POWDER", "STUN_SPORE", "GLARE", "HYPNOSIS", "YAWN", "LEECH_SEED", "CONFUSE_RAY", "SING", "POISON_POWDER", "LOVELY_KISS", "SWEET_KISS", "DARK_VOID", "SCALD")
HAZARDS = M("STEALTH_ROCK", "SPIKES", "TOXIC_SPIKES", "STICKY_WEB")
SCREENS = M("REFLECT", "LIGHT_SCREEN")
UTILITY = M("TAUNT", "ENCORE", "HAZE", "TRICK", "WHIRLWIND", "ROAR", "PERISH_SONG", "DESTINY_BOND", "PAIN_SPLIT", "HEAL_BELL", "AROMATHERAPY", "HELPING_HAND", "FOLLOW_ME", "RAGE_POWDER", "WIDE_GUARD", "TAILWIND", "TRICK_ROOM", "SUBSTITUTE", "PROTECT", "DETECT", "SPIKES", "STEALTH_ROCK", "REFLECT", "LIGHT_SCREEN", "WILL_O_WISP", "TOXIC")
PRIORITY = M("EXTREME_SPEED", "MACH_PUNCH", "BULLET_PUNCH", "AQUA_JET", "ICE_SHARD", "SHADOW_SNEAK", "SUCKER_PUNCH", "ACCELEROCK", "QUICK_ATTACK", "VACUUM_WAVE", "WATER_SHURIKEN", "JET_PUNCH")
PIVOT = M("U_TURN", "VOLT_SWITCH", "FLIP_TURN", "PARTING_SHOT")
WEATHER = {"RAIN": "MOVE_RAIN_DANCE", "SUN": "MOVE_SUNNY_DAY", "SAND": "MOVE_SANDSTORM", "SNOW": "MOVE_SNOWSCAPE", "HAIL": "MOVE_SNOWSCAPE"}

# attacking moves a trainer set must never use (self-KO, no-op without setup, random, fixed damage, lockout)
NEVER_ATTACK = set(M("FUTURE_SIGHT", "DOOM_DESIRE", "STEEL_ROLLER", "SYNCHRONOISE", "BELCH", "FIRST_IMPRESSION", "POLTERGEIST", "UPROAR", "ELECTRO_SHOT", "SPIT_UP", "EXPLOSION", "SELF_DESTRUCT", "MISTY_EXPLOSION", "MEMENTO", "DREAM_EATER", "FOCUS_PUNCH", "SNORE", "LAST_RESORT", "SPIT_UP", "FLING", "NATURAL_GIFT",
                     "PRESENT", "MAGNITUDE", "BEAT_UP", "HIDDEN_POWER", "RAGE", "BIDE", "PSYWAVE", "ENDEAVOR", "COUNTER", "MIRROR_COAT", "METAL_BURST", "SKY_ATTACK", "FALSE_SWIPE",
                     "GUILLOTINE", "HORN_DRILL", "FISSURE", "SHEER_COLD", "FURY_CUTTER", "SECRET_POWER", "NIGHT_SHADE", "SEISMIC_TOSS", "DRAGON_RAGE", "SONIC_BOOM", "SUPER_FANG",
                     "NATURES_MADNESS", "RUINATION", "LOW_KICK", "GRASS_KNOT", "WEATHER_BALL", "TERRAIN_PULSE", "JUDGMENT", "TECHNO_BLAST", "MULTI_ATTACK", "ROUND", "ECHOED_VOICE",
                     "FLAIL", "REVERSAL", "WRING_OUT", "CRUSH_GRIP", "TRUMP_CARD", "PUNISHMENT", "STORED_POWER", "POWER_TRIP", "FRUSTRATION", "SPIT_UP", "STRUGGLE", "COVET",
                     "TACKLE", "POUND", "WATER_GUN", "BUBBLE", "VINE_WHIP", "GUST", "WING_ATTACK", "PECK", "LICK", "SMOG", "ROCK_THROW", "MUD_SLAP", "MUD_SHOT", "POISON_STING",
                     "ABSORB", "ASTONISH", "FURY_SWIPES", "FURY_ATTACK", "DOUBLE_SLAP", "COMET_PUNCH", "CONSTRICT", "BIND", "WRAP", "ROCK_SMASH", "BRUTAL_SWING",
                     "GIGA_IMPACT", "THUNDER_SHOCK", "EMBER",
                     "RAZOR_WIND", "SKULL_BASH", "MAGMA_STORM",
                     "FLAME_WHEEL", "ROLLOUT", "ICE_BALL", "ECHOED_VOICE", "TRIPLE_KICK", "DRAGON_TAIL",
                     "COSMIC_POWER"))
# low-quality status picks
ALL_PROTECT_LIKE = set(M("PROTECT", "DETECT"))

# multi-turn / drawback attack penalties
TWO_TURN = set(M("SOLAR_BEAM", "SOLAR_BLADE", "FLY", "DIG", "DIVE", "BOUNCE", "SKY_DROP", "SHADOW_FORCE", "PHANTOM_FORCE", "RAZOR_WIND", "SKULL_BASH", "FREEZE_SHOCK", "ICE_BURN", "METEOR_BEAM", "GEOMANCY"))
RECHARGE = set(M("HYPER_BEAM", "GIGA_IMPACT", "BLAST_BURN", "FRENZY_PLANT", "HYDRO_CANNON", "ROCK_WRECKER", "ROAR_OF_TIME", "PRISMATIC_LASER", "ETERNABEAM"))
DRAWBACK = set(M("OVERHEAT", "DRACO_METEOR", "LEAF_STORM", "FLEUR_CANNON", "PSYCHO_BOOST", "CLOSE_COMBAT", "SUPERPOWER", "HAMMER_ARM", "ICE_HAMMER", "V_CREATE", "OUTRAGE", "THRASH", "PETAL_DANCE", "FIRE_LASH", "SCALE_SHOT"))
RECOIL = set(M("DOUBLE_EDGE", "BRAVE_BIRD", "FLARE_BLITZ", "WOOD_HAMMER", "HEAD_SMASH", "VOLT_TACKLE", "WILD_CHARGE", "TAKE_DOWN", "HEAD_CHARGE", "WAVE_CRASH", "SUBMISSION", "LIGHT_OF_RUIN"))
GOOD_CONTACT = set()

NEG_ABILITIES = {"ABILITY_TRUANT": -9, "ABILITY_SLOW_START": -9, "ABILITY_DEFEATIST": -4, "ABILITY_KLUTZ": -5, "ABILITY_STALL": -5, "ABILITY_NORMALIZE": -1,
                 "ABILITY_RUN_AWAY": -3, "ABILITY_PICKUP": -3, "ABILITY_HONEY_GATHER": -3, "ABILITY_ILLUMINATE": -2, "ABILITY_GLUTTONY": -2, "ABILITY_STENCH": -2,
                 "ABILITY_ANGER_POINT": -1, "ABILITY_OBLIVIOUS": -1, "ABILITY_RIVALRY": -1, "ABILITY_MOODY": 0, "ABILITY_TANGLED_FEET": -1, "ABILITY_STEADFAST": -1,
                 "ABILITY_FRISK": -1, "ABILITY_HEALER": -1, "ABILITY_MINUS": -2, "ABILITY_PLUS": -2, "ABILITY_SYMBIOSIS": -2, "ABILITY_KEEN_EYE": -2, "ABILITY_BIG_PECKS": -1}
# abilities that only pay off with a weather/terrain; picked only when the set can start it
WEATHER_ABILITY = {"ABILITY_SWIFT_SWIM": "RAIN", "ABILITY_RAIN_DISH": "RAIN", "ABILITY_HYDRATION": "RAIN", "ABILITY_CHLOROPHYLL": "SUN", "ABILITY_SOLAR_POWER": "SUN",
                   "ABILITY_LEAF_GUARD": "SUN", "ABILITY_FLOWER_GIFT": "SUN", "ABILITY_SAND_RUSH": "SAND", "ABILITY_SAND_FORCE": "SAND", "ABILITY_SAND_VEIL": "SAND",
                   "ABILITY_SLUSH_RUSH": "SNOW", "ABILITY_SNOW_CLOAK": "SNOW", "ABILITY_ICE_BODY": "SNOW", "ABILITY_FIELD_BURNER": "SUN"}
SELF_WEATHER = {"ABILITY_DRIZZLE": "RAIN", "ABILITY_DROUGHT": "SUN", "ABILITY_SAND_STREAM": "SAND", "ABILITY_SNOW_WARNING": "SNOW", "ABILITY_SKY_SCORCHER": "SUN",
                "ABILITY_BURNING_SEASON": "SUN", "ABILITY_STORM_BEACON": "RAIN"}
SUN_MOVES = set(M("SOLAR_BEAM", "SOLAR_BLADE"))


class Sets:
    """one finished set; ev is in TRAINER_PARTY_EVS argument order: (hp, atk, def, speed, spatk, spdef)"""

    def __init__(self, **kw):
        self.__dict__.update(kw)


class Builder(ItemMixin):
    def __init__(self, dex, moves, ability_rating, mega_map):
        self.d = dex
        self.mv = moves
        self.rate = ability_rating
        self.mega = mega_map            # base species -> (mega species, stone item)
        self.cache = {}

    # ------------------------------------------------------------------ profile
    def profile(self, sp, as_species=None):
        k = as_species or sp
        st = self.d.stats(k)
        types = self.d.types(k)
        atk, spa = st["atk"], st["spa"]
        side = "phys" if atk >= spa * 1.12 else "spec" if spa >= atk * 1.12 else "mixed"
        if side == "mixed":
            side = "phys" if atk >= spa else "spec"
        bulk = st["hp"] + st["def_"] + st["spd"]
        return dict(types=types, stats=st, side=side, spe=st["spe"], bulk=bulk, off=max(atk, spa), bst=sum(st.values()))

    # ------------------------------------------------------------------ attack scoring
    def eff_power(self, mv, prof, ability, level_sun=False):
        m = self.mv[mv]
        if not m.damaging or mv in NEVER_ATTACK:
            return 0.0
        pw = m.power
        if m.effect in ("EFFECT_RETURN", "EFFECT_FRUSTRATION"):
            pw = 102
        if pw <= 1:
            return 0.0
        if m.has_effect("strikeCount") or m.effect == "EFFECT_MULTI_HIT":
            pw *= 3.0 if m.effect == "EFFECT_MULTI_HIT" else 2.0
        acc = m.acc if m.acc else 100
        v = pw * min(acc, 100) / 100.0
        if mv in TWO_TURN and not (mv in SUN_MOVES and (ability in SELF_WEATHER and SELF_WEATHER[ability] == "SUN")):
            v *= 0.5
        if mv in RECHARGE:
            v *= 0.5
        if mv in DRAWBACK:
            v *= 0.82
        if mv in RECOIL:
            v *= 0.9
        if m.priority > 0:
            v *= 1.0  # handled separately
        stab = m.type[5:] in [t[5:] for t in prof["types"]]
        if stab:
            v *= 2.0 if ability == "ABILITY_ADAPTABILITY" else 1.5
        if m.spread:
            v *= 0.9
        return v

    def attack_pool(self, sp, prof, ability, side, legal):
        """[(score, move)] legal damaging moves of the wanted side, best first"""
        out = []
        for mv in legal:
            if mv not in self.mv:
                continue
            m = self.mv[mv]
            if not m.damaging or m.cat != side:
                continue
            s = self.eff_power(mv, prof, ability)
            if s > 0:
                out.append((s, mv))
        out.sort(key=lambda x: (-x[0], x[1]))
        return out

    def pick_attacks(self, sp, prof, ability, side, legal, n, rng, avoid=(), strict=False):
        """STAB first (one per own type), then coverage by type-chart gain.  returns list of moves"""
        pool = [x for x in self.attack_pool(sp, prof, ability, side, legal) if x[1] not in avoid]
        if side == "phys" and prof["stats"]["spa"] >= prof["stats"]["atk"] * 0.9:
            pool += [x for x in self.attack_pool(sp, prof, ability, "spec", legal) if x[1] not in avoid]
            pool.sort(key=lambda x: (-x[0], x[1]))
        if side == "spec" and prof["stats"]["atk"] >= prof["stats"]["spa"] * 0.9:
            pool += [x for x in self.attack_pool(sp, prof, ability, "phys", legal) if x[1] not in avoid]
            pool.sort(key=lambda x: (-x[0], x[1]))
        chosen, covered = [], {t: 0.0 for t in tc.TYPES}
        own = [t[5:] for t in prof["types"]]
        used_types = set()

        def take(s, mv):
            chosen.append(mv)
            ty = self.mv[mv].type[5:]
            used_types.add(ty)
            for t in tc.TYPES:
                covered[t] = max(covered[t], tc.CHART[ty][t])

        # best move of each own type (power >= 60 or the best available)
        for ty in own:
            cand = [x for x in pool if self.mv[x[1]].type[5:] == ty and x[1] not in chosen]
            if cand and len(chosen) < n:
                top = cand[0]
                # small deterministic variety: among the top two within 12 percent pick by rng
                alt = [c for c in cand[:3] if c[0] >= top[0] * 0.88]
                pick = alt[rng.randrange(len(alt))] if len(alt) > 1 and rng.random() < 0.35 else top
                take(*pick)
        # coverage
        relax = False
        while len(chosen) < n:
            best = None
            for s, mv in pool:
                if mv in chosen:
                    continue
                ty = self.mv[mv].type[5:]
                if ty in used_types and not relax:
                    continue
                gain = sum(1 for t in tc.TYPES if tc.CHART[ty][t] >= 2 and covered[t] < 2) + 0.4 * sum(1 for t in tc.TYPES if tc.CHART[ty][t] >= 1 and covered[t] < 1)
                val = s * (1 + 0.12 * gain)
                if ty in used_types:
                    val *= 0.6
                if best is None or val > best[0]:
                    best = (val, mv)
            if not best:
                if relax or strict:
                    break
                relax = True
                continue
            take(0, best[1])
        return chosen

    # ------------------------------------------------------------------ ability
    def pick_ability(self, sp, role_hint, can_weather, rng, prof):
        abs_ = self.d.abilities(sp)
        best, bs = None, -99
        for i, a in enumerate(abs_):
            s = self.rate.get(a, 5) + NEG_ABILITIES.get(a, 0) - 0.15 * i
            if a in CUSTOM_ABILITIES:
                s += 2.5   # Orleans showcase: the custom abilities get met in the Frontier
            if a in WEATHER_ABILITY and WEATHER_ABILITY[a] not in can_weather:
                s -= 6
            if a in SELF_WEATHER and SELF_WEATHER[a] in ("SUN", "RAIN"):
                s += 1.0
            if a == "ABILITY_HUGE_POWER" or a == "ABILITY_PURE_POWER":
                s += 4
            if a in ("ABILITY_GUTS",) and prof["side"] != "phys":
                s -= 4
            if a in ("ABILITY_TECHNICIAN",) and prof["side"] == "phys" and prof["off"] < 80:
                s -= 2
            if a in ("ABILITY_SHEER_FORCE",) and role_hint in ("bulky", "support"):
                s -= 2
            if a in ("ABILITY_SHED_SKIN", "ABILITY_NATURAL_CURE", "ABILITY_REGENERATOR") and role_hint in ("bulky", "support"):
                s += 2
            if a in ("ABILITY_MOODY",):
                s -= 2
            if s > bs:
                best, bs = a, s
        return best

    def can_set_weather(self, legal, ability):
        out = set()
        for k, mv in WEATHER.items():
            if mv in legal:
                out.add(k)
        if ability in SELF_WEATHER:
            out.add(SELF_WEATHER[ability])
        return out

    # ------------------------------------------------------------------ helper picks
    def first_legal(self, names, legal, k=1, skip=()):
        out = []
        for n in names:
            if n in legal and n not in skip and n not in out:
                out.append(n)
                if len(out) == k:
                    break
        return out

    def best_status(self, legal, prof, ability, rng, k=1, skip=()):
        """status moves that fit the species: Toxic/Will-O-Wisp/Thunder Wave/Spore etc."""
        cand = [n for n in STATUS_MOVES if n in legal and n not in skip]
        order = []
        for n in cand:
            w = 1.0
            if n in M("SPORE", "SLEEP_POWDER", "WILL_O_WISP", "THUNDER_WAVE", "TOXIC"):
                w = 3.0
            if n == "MOVE_WILL_O_WISP" and prof["side"] != "phys" and prof["bulk"] < 230:
                w = 1.5
            if n == "MOVE_SCALD":
                continue
            if n in M("SING", "HYPNOSIS", "LOVELY_KISS", "DARK_VOID", "CONFUSE_RAY", "POISON_POWDER", "STUN_SPORE", "GLARE"):
                w = 1.4
            order.append((w + rng.random() * 0.8, n))
        order.sort(reverse=True)
        return [n for _, n in order[:k]]

    # ------------------------------------------------------------------ roles
    def role_options(self, sp, prof, legal):
        opts = {"attacker": max(0.8, min(4.0, 1.5 + (prof["off"] - 70) / 12.0))}
        has = lambda grp: any(n in legal for n in grp)
        setup = SETUP_PHYS if prof["side"] == "phys" else SETUP_SPEC
        if has(setup) and prof["off"] >= 80:
            opts["setup"] = 2.4
        if prof["off"] >= 95:
            opts["choice"] = 2.0
        rec = [n for n in RECOVERY if n in legal and n != "MOVE_REST"]
        if (rec or "MOVE_REST" in legal) and prof["bulk"] >= 230:
            opts["bulky"] = (2.6 if prof["bulk"] >= 270 else 1.8) * (1.0 if rec else 0.4)
        if prof["bulk"] >= 210 and (has(HAZARDS) or has(SCREENS) or has(M("WISH", "HEAL_BELL", "AROMATHERAPY", "WISH_X"))):
            opts["support"] = 1.8
        if has(M("TAUNT", "ENCORE", "TRICK", "HAZE", "KNOCK_OFF", "PARTING_SHOT", "FAKE_OUT")) and prof["spe"] >= 60:
            opts["disrupt"] = 1.2
        return opts

    def build_moves(self, sp, prof, ability, role, legal, rng, tier_q, atk_species=None):
        """returns the move list for a role (never more than 4, no duplicates)"""
        side = prof["side"]
        att = lambda n, avoid=(): self.pick_attacks(sp, prof, ability, side, legal, n, rng, avoid=avoid, strict=True)
        setup = SETUP_PHYS if side == "phys" else SETUP_SPEC
        mv = []

        def add(xs):
            for x in xs:
                if x not in mv and len(mv) < 4:
                    mv.append(x)

        weather = self.can_set_weather(legal, ability)
        if role == "setup":
            su = self.first_legal(setup, legal, 1)
            if su and su[0] in M("AGILITY", "ROCK_POLISH") and len(self.first_legal(setup, legal, 3)) > 1:
                su = self.first_legal(setup, legal, 3)[1:2]
            add(su)
            add(att(3))
        elif role == "choice":
            add(att(3))
            pr = [n for n in PRIORITY + PIVOT if n in legal and n not in mv and self.mv[n].type[5:] in [t[5:] for t in prof["types"]] + tc.TYPES]
            pri = self.first_legal(PRIORITY, legal, 1, skip=mv)
            piv = self.first_legal(PIVOT, legal, 1, skip=mv)
            if len(mv) == 3 and (pri or piv):
                add((pri or piv)[:1] if rng.random() < 0.6 else (piv or pri)[:1])
            add(att(4, avoid=mv))
        elif role == "bulky":
            rec = [n for n in RECOVERY if n in legal and n not in ("MOVE_REST", "MOVE_WISH")] or self.first_legal(M("WISH", "REST"), legal, 1)
            add(rec[:1])
            if rec and rec[0] == "MOVE_REST" and "MOVE_SLEEP_TALK" in legal:
                add(["MOVE_SLEEP_TALK"])
            add(self.best_status(legal, prof, ability, rng, 1))
            add(att(2))
            if len(mv) < 4:
                add(self.first_legal(M("PROTECT", "SUBSTITUTE", "REST") + BULK_SETUP_PHYS[:0], legal, 1, skip=mv))
        elif role == "support":
            sup = self.first_legal(HAZARDS + SCREENS + M("WISH", "HEAL_BELL", "AROMATHERAPY"), legal, 2)
            add(sup[:1])
            if len(sup) > 1 and rng.random() < 0.5:
                add(sup[1:2])
            add(att(2))
            add(self.best_status(legal, prof, ability, rng, 1))
            add(self.first_legal(M("PROTECT", "TAUNT", "SUBSTITUTE"), legal, 1, skip=mv))
        elif role == "disrupt":
            add(self.first_legal(M("FAKE_OUT", "TAUNT", "ENCORE", "TRICK", "PARTING_SHOT", "HAZE"), legal, 1))
            add(att(2))
            add(self.best_status(legal, prof, ability, rng, 1))
            add(att(4, avoid=mv))
        elif role == "weather" and weather:
            wmv = WEATHER[sorted(weather)[0]] if sorted(weather)[0] in WEATHER else None
            if wmv and wmv in legal and ability not in SELF_WEATHER:
                add([wmv])
            add(att(3))
        else:  # attacker, basic
            add(att(3))
            pri = self.first_legal(PRIORITY, legal, 1, skip=mv)
            if pri and (prof["spe"] < 90 or rng.random() < 0.4):
                add(pri)
            add(att(4, avoid=mv))
        # fill: more attacks, then status/utility, then anything damaging, then whatever is legal
        add(att(4, avoid=mv))
        if len(mv) < 4:
            add(self.first_legal(M("PROTECT", "SUBSTITUTE") + UTILITY, legal, 4, skip=mv))
        if len(mv) < 4:
            add(self.pick_attacks(sp, prof, ability, side, legal, 4, rng, avoid=mv, strict=False))
        if len(mv) < 4:
            rest = sorted(x for x in legal if x in self.mv and x not in mv and x not in NEVER_ATTACK or (x in self.mv and not self.mv[x].damaging and x not in mv))
            add(rest[:4])
        return mv[:4]

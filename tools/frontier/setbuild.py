"""FullBuilder: assembles one finished set (see setbuilder.Builder for the pieces)."""
import random

import typechart as tc
from setbuilder import Builder, Sets, SELF_WEATHER, WEATHER, WEATHER_ABILITY, M

TIER_Q = {"T0": 0, "T1": 0, "A1": 1, "A2": 1, "B1": 2, "B2": 2, "B3": 3, "B4": 3, "L": 3, "H": 4}


class FullBuilder(Builder):
    def build(self, sp, tier, variant, mega=None, avoid_roles=(), force_role=None, tag=""):
        rng = random.Random(f"{sp}:{tier}:{variant}:{tag}")
        legal = self.d.legal(sp, 50)
        prof = self.profile(sp, as_species=mega[0] if mega else None)
        q = TIER_Q[tier]
        nfe = not self.d.fully_evolved(sp)
        opts = self.role_options(sp, prof, legal)
        if q == 0:
            opts = {"attacker": 4.0, **{k: v * 0.3 for k, v in opts.items() if k in ("bulky", "setup")}}
        elif q == 1:
            opts = {k: v for k, v in opts.items() if k in ("attacker", "bulky", "choice", "setup", "support")}
        if mega or tier in ("L", "H"):
            opts = {k: v for k, v in opts.items() if k in ("attacker", "setup", "choice", "bulky") and not (mega and k == "bulky")}
        ranked = sorted(opts.items(), key=lambda kv: -(kv[1] + rng.random() * 1.4 - (3.0 if kv[0] in avoid_roles else 0)))
        role = force_role or ranked[0][0]
        if role == 'choice' and q < 2 and prof['side'] == 'spec':
            role = 'attacker'
        weather = self.can_set_weather(legal, None)
        ability = self.pick_ability(sp, role, weather, rng, prof)
        moves = self.build_moves(sp, prof, ability, role, legal, rng, q)
        # ability <-> move glue
        if ability in ("ABILITY_GUTS", "ABILITY_POISON_HEAL", "ABILITY_QUICK_FEET") and "MOVE_FACADE" in legal and "MOVE_FACADE" not in moves and prof["side"] == "phys":
            att = [m for m in moves if self.mv[m].damaging]
            if att:
                moves[moves.index(att[-1])] = "MOVE_FACADE"
        need = WEATHER_ABILITY.get(ability)
        if need and ability not in SELF_WEATHER and WEATHER.get(need) in legal and WEATHER[need] not in moves:
            att = [m for m in moves if self.mv[m].damaging]
            if len(att) >= 3 or len(moves) < 4:
                if len(moves) < 4:
                    moves.append(WEATHER[need])
                else:
                    moves[moves.index(att[-1])] = WEATHER[need]
        if ability == "ABILITY_SKY_SCORCHER" or ability in ("ABILITY_DROUGHT", "ABILITY_DRIZZLE"):
            pass
        nat = self.nature_for(prof, role, rng, q, moves)
        ev = self.evs_for(prof, role, nat, q, moves, rng)
        if mega:
            item = mega[1]
        else:
            item = self.pick_item(sp, prof, ability, role, moves, q, rng, nfe)
        return Sets(species=sp, moves=moves, item=item, ev=ev, nature=nat, ability=ability, role=role, tier=tier, variant=variant, mega=bool(mega))

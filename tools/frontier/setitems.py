"""Nature, EV and item choice for the set builder (mixin for setbuilder.Builder)."""
import typechart as tc

EARLY_OK = {"ITEM_ORAN_BERRY", "ITEM_QUICK_CLAW", "ITEM_KINGS_ROCK", "ITEM_FOCUS_BAND", "ITEM_SCOPE_LENS", "ITEM_LUM_BERRY", "ITEM_LEFTOVERS", "ITEM_MENTAL_HERB"}
HIGH_ONLY = {"ITEM_LIFE_ORB", "ITEM_CHOICE_SCARF", "ITEM_CHOICE_SPECS", "ITEM_WEAKNESS_POLICY", "ITEM_ASSAULT_VEST", "ITEM_ROCKY_HELMET", "ITEM_EXPERT_BELT", "ITEM_FOCUS_SASH"}
BERRIES = {"FIRE": "ITEM_OCCA_BERRY", "WATER": "ITEM_PASSHO_BERRY", "ELECTRIC": "ITEM_WACAN_BERRY", "GRASS": "ITEM_RINDO_BERRY", "ICE": "ITEM_YACHE_BERRY",
           "FIGHTING": "ITEM_CHOPLE_BERRY", "POISON": "ITEM_KEBIA_BERRY", "GROUND": "ITEM_SHUCA_BERRY", "FLYING": "ITEM_COBA_BERRY", "PSYCHIC": "ITEM_PAYAPA_BERRY",
           "BUG": "ITEM_TANGA_BERRY", "ROCK": "ITEM_CHARTI_BERRY", "GHOST": "ITEM_KASIB_BERRY", "DRAGON": "ITEM_HABAN_BERRY", "DARK": "ITEM_COLBUR_BERRY",
           "STEEL": "ITEM_BABIRI_BERRY", "FAIRY": "ITEM_ROSELI_BERRY"}
DRAWBACK_NAMES = {"MOVE_OVERHEAT", "MOVE_DRACO_METEOR", "MOVE_LEAF_STORM", "MOVE_CLOSE_COMBAT", "MOVE_SUPERPOWER", "MOVE_HAMMER_ARM", "MOVE_V_CREATE", "MOVE_FLEUR_CANNON", "MOVE_PSYCHO_BOOST"}


class ItemMixin:
    # ------------------------------------------------------------------ nature / EVs
    def nature_for(self, prof, role, rng, tier_q, moves):
        side = prof["side"]
        phys = sum(1 for m in moves if self.mv[m].cat == "phys")
        spec = sum(1 for m in moves if self.mv[m].cat == "spec")
        fast = prof["spe"] >= 85
        st = prof["stats"]
        if tier_q <= 0 and rng.random() < 0.45:
            return rng.choice(["NATURE_HARDY", "NATURE_DOCILE", "NATURE_BASHFUL", "NATURE_QUIRKY", "NATURE_SERIOUS"])
        if role in ("bulky", "support"):
            if phys > spec:
                return "NATURE_IMPISH" if st["def_"] >= st["spd"] else "NATURE_CAREFUL"
            if phys == 0 and spec == 0:
                return "NATURE_BOLD" if st["def_"] <= st["spd"] else "NATURE_CALM"
            return "NATURE_BOLD" if st["def_"] <= st["spd"] else "NATURE_CALM"
        if phys == 0 and spec == 0:
            return "NATURE_CALM" if st["spd"] >= st["def_"] else "NATURE_BOLD"
        if phys > 0 and spec > 0 and abs(phys - spec) <= 1 and st["atk"] >= 0.88 * st["spa"] and st["spa"] >= 0.88 * st["atk"]:
            return "NATURE_NAIVE" if fast else "NATURE_HARDY"
        quick = fast or (role == "setup" and prof["spe"] >= 70)
        if phys >= spec:
            return "NATURE_JOLLY" if quick else "NATURE_ADAMANT"
        return "NATURE_TIMID" if quick else "NATURE_MODEST"

    def evs_for(self, prof, role, nature, tier_q, moves, rng):
        phys = sum(1 for m in moves if self.mv[m].cat == "phys")
        spec = sum(1 for m in moves if self.mv[m].cat == "spec")
        off = "atk" if phys >= spec else "spa"
        fast = nature in ("NATURE_JOLLY", "NATURE_TIMID", "NATURE_NAIVE", "NATURE_HASTY") or (prof["spe"] >= 95 and role in ("attacker", "setup", "choice"))
        st = prof["stats"]
        e = dict(hp=0, atk=0, def_=0, spa=0, spd=0, spe=0)
        if role in ("bulky", "support"):
            e["hp"] = 252
            if st["def_"] >= st["spd"]:
                e["def_"], e["spd"] = 252, 4
            else:
                e["spd"], e["def_"] = 252, 4
        elif phys == 0 and spec == 0:
            e["hp"], e["def_"], e["spd"] = 252, 128, 128
        elif fast:
            e[off], e["spe"], e["hp"] = 252, 252, 4
        else:
            e["hp"], e[off] = 252, 252
            e["def_" if st["def_"] <= st["spd"] else "spd"] = 4
        scale = {0: 0.45, 1: 0.7, 2: 0.9, 3: 1.0, 4: 1.0}[tier_q]
        out = e if scale >= 1.0 else {k: (int(v * scale) // 4) * 4 for k, v in e.items()}
        return (out["hp"], out["atk"], out["def_"], out["spe"], out["spa"], out["spd"])  # TRAINER_PARTY_EVS order

    # ------------------------------------------------------------------ items
    def best_resist_berry(self, types):
        worst, wt = None, 1.9
        for t in tc.TYPES:
            m = tc.eff("TYPE_" + t, types)
            if m > wt and t != "NORMAL":
                worst, wt = t, m
        return BERRIES.get(worst) if worst else None

    def pick_item(self, sp, prof, ability, role, moves, tier_q, rng, nfe):
        types = prof["types"]
        phys = sum(1 for m in moves if self.mv[m].cat == "phys")
        spec = sum(1 for m in moves if self.mv[m].cat == "spec")
        att_moves = [m for m in moves if self.mv[m].damaging]
        stab_types = [self.mv[m].type[5:] for m in att_moves if self.mv[m].type in types]
        cands = []

        def c(w, it):
            cands.append((w, it))

        if ability in ("ABILITY_GUTS", "ABILITY_QUICK_FEET") and "MOVE_FACADE" in moves:
            c(6, "ITEM_FLAME_ORB" if tier_q >= 2 else "ITEM_CHESTO_BERRY")
        if ability == "ABILITY_POISON_HEAL":
            c(6, "ITEM_TOXIC_ORB" if tier_q >= 2 else "ITEM_LUM_BERRY")
        if ability in ("ABILITY_MAGIC_GUARD", "ABILITY_SHEER_FORCE") and phys + spec >= 3 and tier_q >= 2:
            c(5, "ITEM_LIFE_ORB")
        if nfe and tier_q >= 1:
            c(5, "ITEM_EVIOLITE")
        stab_item = tc.TYPE_ITEM.get(stab_types[0]) if stab_types else None
        if role == "choice":
            if phys >= spec:
                c(4, "ITEM_CHOICE_BAND")
            else:
                c(4, "ITEM_CHOICE_SPECS" if tier_q >= 2 else "ITEM_CHOICE_BAND")
            if prof["spe"] >= 70 and tier_q >= 2:
                c(2.5, "ITEM_CHOICE_SCARF")
        elif role == "setup":
            c(2, "ITEM_LUM_BERRY")
            c(2, "ITEM_SITRUS_BERRY")
            c(1.5, "ITEM_LEFTOVERS")
            if tier_q >= 2:
                c(2.5, "ITEM_LIFE_ORB")
                c(1.5, "ITEM_WEAKNESS_POLICY")
                c(1.2, "ITEM_SALAC_BERRY" if prof["spe"] < 100 else "ITEM_FOCUS_SASH")
        elif role in ("bulky", "support"):
            c(4, "ITEM_LEFTOVERS")
            c(2, "ITEM_SITRUS_BERRY")
            c(1.5, "ITEM_LUM_BERRY")
            if tier_q >= 2:
                c(1.3, "ITEM_ROCKY_HELMET")
                c(1.0, "ITEM_SHELL_BELL" if phys + spec else "ITEM_MENTAL_HERB")
            if "MOVE_REFLECT" in moves or "MOVE_LIGHT_SCREEN" in moves:
                c(3, "ITEM_LIGHT_CLAY" if tier_q >= 2 else "ITEM_MENTAL_HERB")
            if "POISON" in [t[5:] for t in types]:
                c(1.5, "ITEM_BLACK_SLUDGE")
        elif role == "disrupt":
            c(2, "ITEM_MENTAL_HERB")
            c(2, "ITEM_FOCUS_SASH" if tier_q >= 2 else "ITEM_FOCUS_BAND")
            c(1.5, "ITEM_LEFTOVERS")
            c(1.5, "ITEM_LUM_BERRY")
        else:
            if stab_item:
                c(3, stab_item)
            if any("criticalHitStage" in self.mv[m].body for m in moves):
                c(3, "ITEM_SCOPE_LENS")
            c(1.6, "ITEM_QUICK_CLAW")
            c(1.6, "ITEM_KINGS_ROCK")
            c(1.6, "ITEM_LEFTOVERS")
            c(1.4, "ITEM_FOCUS_BAND")
            c(1.5, "ITEM_LUM_BERRY")
            c(1.2, "ITEM_SITRUS_BERRY")
            if tier_q >= 2:
                c(3, "ITEM_LIFE_ORB")
                c(2.2, "ITEM_EXPERT_BELT")
                c(2.0, "ITEM_MUSCLE_BAND" if phys >= spec else "ITEM_WISE_GLASSES")
                c(1.6, "ITEM_FOCUS_SASH")
                if all(self.mv[m].damaging for m in moves):
                    c(1.2, "ITEM_ASSAULT_VEST")
            if prof["spe"] < 70 and tier_q >= 1 and any(m in DRAWBACK_NAMES for m in moves):
                c(1.5, "ITEM_WHITE_HERB")
        if role == 'choice':
            cands = [(w, i) for w, i in cands if i in ('ITEM_CHOICE_BAND', 'ITEM_CHOICE_SPECS', 'ITEM_CHOICE_SCARF')]
            return self._wchoice(cands, rng)
        if tier_q >= 1:
            rb = self.best_resist_berry(types)
            if rb:
                c(2.2 if tier_q >= 3 else 1.6, rb)
            for st in sorted(set(stab_types)):
                if tc.TYPE_ITEM.get(st):
                    c(1.2, tc.TYPE_ITEM[st])
            c(0.8, 'ITEM_MENTAL_HERB')
            c(0.8, 'ITEM_PERSIM_BERRY')
        if tier_q <= 0:
            cands = [(w * 0.6, i) for w, i in cands if i in EARLY_OK]
            cands += [(1.5, "ITEM_ORAN_BERRY"), (1.0, "ITEM_CHERI_BERRY"), (1.0, "ITEM_PECHA_BERRY"), (1.0, "ITEM_RAWST_BERRY"),
                      (1.0, "ITEM_ASPEAR_BERRY"), (1.0, "ITEM_PERSIM_BERRY"), (1.0, "ITEM_CHESTO_BERRY")]
            if stab_item:
                cands.append((2.0, stab_item))
        elif tier_q == 1:
            cands = [(w, i) for w, i in cands if i not in HIGH_ONLY]
        if not cands:
            cands = [(1, "ITEM_LEFTOVERS")]
        return self._wchoice(cands, rng)

    def _wchoice(self, cands, rng):
        tot = sum(w for w, _ in cands)
        r = rng.random() * tot
        for w, it in cands:
            r -= w
            if r <= 0:
                return it
        return cands[-1][1]

"""Helpers for the lair-unlock tests (t23_lairs, t29_lair_unlocks): trophy bits and the battle counters in SaveBlock3, found by their magics."""
import sys
from pathlib import Path

from bot import ROOT, enum_value

sys.path.insert(0, str(Path(ROOT) / "tools" / "achievements"))
import achievements_data as AD  # noqa: E402

ACH_MAGIC = 0xAC1E0001
OFF_UNLOCKED, OFF_PENDING = 4, 20
# counter ids (include/constants/achievements.h LAIR_COUNTER_*)
COUNTERS = ["PARALYZE", "SNOW", "SUN", "RAIN", "SANDSTORM", "TAILWIND", "MISTY", "TRICK_ROOM", "BITE_DAMAGE", "PSYCHIC_DAMAGE"]
SB3_SIZE = 1624


def ach_id(const):
    """ACH_WATER_COLLECTOR -> its id (sheet number - 1)"""
    key = const[4:] if const.startswith("ACH_") else const
    for r in AD.ROWS:
        if r[2] == key:
            return r[0] - 1
    raise KeyError(const)


def _scan(b, magic):
    base = b.sym("gSaveblock3")
    for off in range(0, SB3_SIZE - 4, 4):
        if b.r32(base + off) == magic:
            return base + off
    return None


def ach_block(b):
    return _scan(b, ACH_MAGIC)


def counter_block(b):
    """the counters sit right after the 56-byte AchievementSaveData"""
    return ach_block(b) + 56


def trophy(b, ach):
    a = ach_block(b)
    return bool(b.r8(a + OFF_UNLOCKED + ach // 8) >> (ach % 8) & 1)


def set_trophy(b, ach, on=True):
    """test setup: set / clear the unlocked bit (no popup, no reward)"""
    a = ach_block(b)
    addr = a + OFF_UNLOCKED + ach // 8
    v = b.r8(addr)
    b.w8(addr, (v | (1 << ach % 8)) if on else (v & ~(1 << ach % 8)) & 0xFF)


def counter(b, name):
    a = counter_block(b)
    i = COUNTERS.index(name)
    return b.r8(a + i) if i < 8 else b.r32(a + 8 + (i - 8) * 4)


def set_counter(b, name, v):
    a = counter_block(b)
    i = COUNTERS.index(name)
    if i < 8:
        b.w8(a + i, v)
    else:
        b.w32(a + 8 + (i - 8) * 4, v)


def lair_trophies():
    """{lair key: ach id} from story_data_lairs.GATES"""
    sys.path.insert(0, str(Path(ROOT) / "tools" / "mapgen"))
    import story_data_lairs as D
    return {k: ach_id(v[0]) for k, v in D.GATES.items()}

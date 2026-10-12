"""Move data touched by the dex sheets: Mystical Power is Fairy-type (lake guardians' signature move, decided);
Psychic Fangs / Victory Dance PP follow the learnsets sheet's Move Index (Pokemon Champions values). Idempotent."""
import re
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "src/data/moves_info.h"
t = p.read_text(encoding="utf-8")


def edit(move, field, old, new):
    global t
    m = re.search(r"\n    \[" + move + r"\] =", t)
    i = m.start()
    j = t.index("\n    },", i)
    seg = t[i:j]
    seg2 = re.sub(r"(\." + field + r" = )" + re.escape(old) + ",", lambda mm: mm.group(1) + new + ",", seg, count=1)
    t = t[:i] + seg2 + t[j:]
    return seg != seg2


print(edit("MOVE_MYSTICAL_POWER", "type", "TYPE_PSYCHIC", "TYPE_FAIRY"),
      edit("MOVE_PSYCHIC_FANGS", "pp", "15", "10"), edit("MOVE_VICTORY_DANCE", "pp", "20", "10"))
p.write_text(t, encoding="utf-8", newline=chr(10))

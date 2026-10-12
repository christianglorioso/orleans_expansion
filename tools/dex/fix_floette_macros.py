"""One-off: split the shared FLOETTE_MISC_INFO abilities so Floette keeps Symbiosis (hidden) and Floette (Eternal Flower)
has no hidden ability, as the dex sheet says."""
import re
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "src/data/pokemon/species_info/gen_6_families.h"
t = p.read_text(encoding="utf-8")
BS = chr(92)
# 1. drop the abilities line from the shared misc macro (Floette section only)
i = t.index("#define FLOETTE_MISC_INFO")
j = t.index("#define FLOETTE_NORMAL_INFO")
seg = t[i:j]
seg2 = re.sub(r"        \.abilities = [^\n]*\n", "", seg, count=1)
assert seg != seg2
t = t[:i] + seg2 + t[j:]
# 2. add it to the normal-info macro
k = t.index("#define FLOETTE_NORMAL_INFO")
m = re.search(r"        \.eggGroups = [^\n]*\n", t[k:])
line = "        .abilities = { ABILITY_FLOWER_VEIL, ABILITY_NONE, ABILITY_SYMBIOSIS },"
line = line.ljust(88) + BS + "\n"
t = t[:k + m.end()] + line + t[k + m.end():]
# 3. eternal block: literal abilities (Flower Veil only)
e = t.index("    [SPECIES_FLOETTE_ETERNAL] =")
m = re.search(r"        \.eggGroups = [^\n]*\n", t[e:])
t = t[:e + m.end()] + "        .abilities = { ABILITY_FLOWER_VEIL, ABILITY_NONE, ABILITY_NONE },\n" + t[e + m.end():]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")

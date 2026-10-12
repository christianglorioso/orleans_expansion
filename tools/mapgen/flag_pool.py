"""Orleans flag / var pool: hand out the next free FLAG_ORLEANS_POOL_nnn / VAR_ORLEANS_POOL_nnn.

The Hoenn strip left hundreds of story flags (and ~100 vars) that nothing references. They are named
FLAG_ORLEANS_POOL_nnn in include/constants/flags.h and VAR_ORLEANS_POOL_nnn in include/constants/vars.h, each at its
original id. Claiming one RENAMES it in place: the id never moves, the save layout never changes.

usage (from the decomp root):
  python tools/mapgen/flag_pool.py status
  python tools/mapgen/flag_pool.py claim FLAG_NEW_NAME "what it means" [--hidden]   -> prints the id it took
  python tools/mapgen/flag_pool.py claimvar VAR_NEW_NAME "what it means"
  python tools/mapgen/flag_pool.py claim FLAG_A,FLAG_B,FLAG_C "..."                   several names in one call

  --hidden   take an id >= FLAG_HIDDEN_ITEMS_START (0x1F4): the only ids a hidden-item bg event may use
             (without --hidden the lowest free id is taken, which keeps those for hidden items later)
Item-ball (object) flags do NOT come from here: tools/mapgen/firstpass.py item_flag() hands out the
FLAG_UNUSED_0x270+ names through item_flags.json.
The edit is a single read-modify-write of the header; run it while no other agent is mid-edit of that header.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLAGS = os.path.join(ROOT, "include", "constants", "flags.h")
VARS = os.path.join(ROOT, "include", "constants", "vars.h")
HIDDEN_START = 0x1F4
SYSTEM_FLAGS = 0x860


def pool_entries(text, prefix):
    out = []
    for m in re.finditer(r"^#define (%s_ORLEANS_POOL_(\d+))[ \t]+(.+?)[ \t]*(?://.*)?$" % prefix, text, re.M):
        expr = m.group(3)
        try:
            ident = eval(expr, {"SYSTEM_FLAGS": SYSTEM_FLAGS, "FLAG_HIDDEN_ITEMS_START": HIDDEN_START, "TEMP_FLAGS_START": 0, "TRAINER_FLAGS_START": 0x500})
        except Exception:
            continue
        out.append((int(m.group(2)), m.group(1), ident))
    return out


def read(path):
    with open(path, encoding="utf8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf8", newline="") as f:
        f.write(text)


def claim(path, prefix, names, comment, hidden):
    text = read(path)
    entries = pool_entries(text, prefix)
    for name in names:
        if not re.fullmatch(r"%s_[A-Z0-9_]+" % prefix, name):
            sys.exit(f"{name}: must be {prefix}_UPPER_CASE")
        if re.search(r"\b%s\b" % re.escape(name), text):
            sys.exit(f"{name} already exists")
    free = [e for e in entries if (not hidden or e[2] >= HIDDEN_START)]
    if len(free) < len(names):
        sys.exit("the pool has no free entries left" + (" at ids >= 0x1F4" if hidden else ""))
    # lowest id first
    free.sort(key=lambda e: e[2])
    taken = []
    for name in names:
        num, old, ident = free.pop(0)
        pat = re.compile(r"^(#define )%s([ \t]+)(.+?)[ \t]*(//.*)?$" % re.escape(old), re.M)
        m = pat.search(text)
        val = m.group(3)
        line = "#define %s %s" % (name.ljust(48), val)
        if comment:
            line = line + " // " + comment
        text = text[:m.start()] + line + text[m.end():]
        taken.append((name, ident, old))
    write(path, text)
    for name, ident, old in taken:
        print(f"{name} = 0x{ident:X} (was {old})")


def status():
    ft, vt = read(FLAGS), read(VARS)
    fe, ve = pool_entries(ft, "FLAG"), pool_entries(vt, "VAR")
    hid = [e for e in fe if e[2] >= HIDDEN_START]
    print(f"flags free: {len(fe)} (of which {len(hid)} usable as hidden-item flags, id >= 0x1F4)")
    print(f"vars free:  {len(ve)}")
    for label, es in (("flags", fe), ("vars", ve)):
        runs, s, p = [], None, None
        for _, _, i in sorted(es, key=lambda e: e[2]):
            if s is None:
                s = p = i
            elif i == p + 1:
                p = i
            else:
                runs.append((s, p)); s = p = i
        if s is not None:
            runs.append((s, p))
        big = [f"0x{a:X}-0x{b:X} ({b - a + 1})" for a, b in runs if b - a >= 7]
        print(f"  {label}: contiguous runs of 8+: " + ", ".join(big))


def main(argv):
    if len(argv) < 2 or argv[1] == "status":
        return status()
    hidden = "--hidden" in argv
    args = [a for a in argv[2:] if a != "--hidden"]
    if argv[1] in ("claim", "claimvar") and args:
        names = args[0].split(",")
        comment = args[1] if len(args) > 1 else ""
        if argv[1] == "claim":
            return claim(FLAGS, "FLAG", names, comment, hidden)
        return claim(VARS, "VAR", names, comment, False)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)

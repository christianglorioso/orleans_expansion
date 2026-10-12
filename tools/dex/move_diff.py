import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheet_data as sd
ROOT = sd.ROOT
txt = (ROOT / "src/data/moves_info.h").read_text(encoding="utf-8")
parts = re.split(r"\n    \[(MOVE_\w+)\] =", txt)
eng = {}
for i in range(1, len(parts), 2):
    b = parts[i + 1]
    nm = re.search(r'\.name = COMPOUND_STRING\("([^"]*)"\)', b)
    if not nm:
        continue
    g = lambda f: (re.search(r"\." + f + r" = ([^,\n]+),", b) or [None, None])[1]
    eng[sd.norm(nm.group(1))] = dict(const=parts[i], type=g("type"), power=g("power"), acc=g("accuracy"), pp=g("pp"), cat=g("category"))
h, rows = sd.load_move_index()
diffs = []
for r in rows:
    if not r[0]:
        continue
    e = eng.get(sd.norm(r[0]))
    if not e:
        diffs.append((r[0], "missing in engine"))
        continue
    t = "TYPE_" + str(r[1]).upper()
    d = []
    if e["type"] != t:
        d.append(f"type {e['type']}->{t}")
    p = r[3] if isinstance(r[3], (int, float)) else 0
    ep = int(re.sub(r"\D", "", e["power"] or "0") or 0) if (e["power"] or "").strip().isdigit() else None
    if ep is not None and ep != p:
        d.append(f"power {ep}->{p}")
    pp = r[5]
    if (e["pp"] or "").strip().isdigit() and int(e["pp"]) != pp:
        d.append(f"pp {e['pp']}->{pp}")
    acc = r[4]
    if isinstance(acc, (int, float)) and (e["acc"] or "").strip().isdigit() and int(e["acc"]) != acc:
        d.append(f"acc {e['acc']}->{acc}")
    if d:
        diffs.append((r[0], "; ".join(d)))
print(len(diffs))
for x in diffs:
    print(x)

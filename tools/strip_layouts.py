"""Stage 2 of the Hoenn strip: drop map layouts nothing uses.
usage (decomp root): PYTHONUTF8=1 python tools/strip_layouts.py [--apply]
Works from the pre-strip layouts.json (git show HEAD~..., via STRIP_BASE commit) + current map.json files.

Rules:
 - layout used by a kept (non-hollow) map: untouched
 - else referenced by a LAYOUT_ literal in src/include/data/test: entry kept, repointed to the 1x1 stub data (constant survives)
 - else: entry removed
data/layouts/<dir>/ files are left on disk (nothing compiles them once the entry is gone).
"""
import json
import os
import re
import subprocess
import sys

BASE = 'd7b88d21da'
txt = subprocess.run(['git', 'show', f'{BASE}:data/layouts/layouts.json'], capture_output=True).stdout.decode('utf-8')
base = json.loads(txt)
cur = json.load(open('data/layouts/layouts.json', encoding='utf-8'))
stub = next(l for l in cur['layouts'] if l and l['id'] == 'LAYOUT_STRIP_STUB')

used = set()
for d in os.listdir('data/maps'):
    p = f'data/maps/{d}/map.json'
    if os.path.exists(p):
        j = json.load(open(p, encoding='utf-8'))
        used.add(j['layout'])

pat = re.compile(r'\bLAYOUT_[A-Z0-9_]+\b')
lit = {}
for root in ['src', 'include', 'data', 'test', 'asm']:
    for dp, dn, fn in os.walk(root):
        d = dp.replace(os.sep, '/')
        if d.startswith(('data/maps', 'data/layouts', 'data/tilesets', 'include/constants/layouts')):
            continue
        for f in fn:
            if not f.endswith(('.c', '.h', '.s', '.inc', '.json', '.party', '.mk')):
                continue
            if f == 'layouts.h':
                continue
            p = d + '/' + f
            for t in set(pat.findall(open(p, encoding='utf-8', errors='replace').read())):
                lit.setdefault(t, set()).add(p)

out = []
removed, repointed, kept_n = [], [], 0
sizes = 0
for l in base['layouts']:
    if l is None:
        out.append(l)
        continue
    i = l['id']
    if i == 'LAYOUT_STRIP_STUB':
        continue
    if i in used:
        out.append(l)
        kept_n += 1
    elif i in lit:
        out.append(dict(l, width=1, height=1, primary_tileset=stub['primary_tileset'],
                        secondary_tileset=stub['secondary_tileset'],
                        border_filepath=stub['border_filepath'], blockdata_filepath=stub['blockdata_filepath']))
        repointed.append((i, sorted(lit[i])[:2]))
    else:
        removed.append(i)
out.append(stub)
print('layouts: base', len(base['layouts']), 'kept', kept_n, 'repointed to stub', len(repointed), 'removed', len(removed))
for i, f in repointed:
    print('  repoint', i, f)
if '--apply' in sys.argv:
    cur['layouts'] = out
    with open('data/layouts/layouts.json', 'w', encoding='utf-8', newline=chr(10)) as f:
        json.dump(cur, f, indent=2)
        f.write(chr(10))
    json.dump({'removed': removed, 'repointed': [r[0] for r in repointed]}, open('tools/strip_layouts_plan.json', 'w'), indent=1)

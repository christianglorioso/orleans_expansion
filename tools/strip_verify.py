"""Strip verification: every Orleans warp/connection resolves to a real, non-hollow map with a real layout.
usage (decomp root): PYTHONUTF8=1 python tools/strip_verify.py
Reads the working tree (not git)."""
import json
import os

G = json.load(open('data/maps/map_groups.json', encoding='utf-8'))
groups = G['group_order']
orl = {m for g in groups[groups.index('gMapGroup_Towns'):] for m in G[g]}
maps = {}
byid = {}
for d in os.listdir('data/maps'):
    p = f'data/maps/{d}/map.json'
    if os.path.exists(p):
        j = json.load(open(p, encoding='utf-8'))
        maps[d] = j
        byid[j['id']] = d
L = {l['id']: l for l in json.load(open('data/layouts/layouts.json', encoding='utf-8'))['layouts']}
bad = 0
nwarps = 0
for m in sorted(orl):
    j = maps[m]
    if j['layout'] == 'LAYOUT_STRIP_STUB' or j['layout'] not in L:
        print('BAD layout', m, j['layout'])
        bad += 1
    for w in j.get('warp_events') or []:
        nwarps += 1
        d = byid.get(w['dest_map'])
        if d is None:
            print('BAD warp dest', m, w['dest_map'])
            bad += 1
            continue
        if d not in orl and maps[d]['layout'] == 'LAYOUT_STRIP_STUB':
            print('BAD warp to hollow map', m, d)
            bad += 1
            continue
        n = len(maps[d].get('warp_events') or [])
        wid = w['dest_warp_id']
        if str(wid).isdigit() and int(wid) >= n:
            print('BAD warp id', m, '->', d, wid, 'of', n)
            bad += 1
    for c in j.get('connections') or []:
        d = byid.get(c['map'])
        if d is None or (d not in orl and maps[d]['layout'] == 'LAYOUT_STRIP_STUB'):
            print('BAD connection', m, c['map'])
            bad += 1
for m, j in maps.items():
    if j['layout'] not in L:
        print('layout missing for', m, j['layout'])
        bad += 1
    else:
        for k in ('primary_tileset', 'secondary_tileset'):
            pass
print(f'orleans maps {len(orl)}, warps checked {nwarps}, problems {bad}')

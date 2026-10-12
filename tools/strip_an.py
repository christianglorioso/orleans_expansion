"""Analysis helper for the Hoenn strip (maps reachability). Run from decomp root."""
import json,os,glob,collections
G=json.load(open('data/maps/map_groups.json'))
groups=[g for g in G['group_order']]
grp_of={}
for gi,g in enumerate(groups):
    for m in G[g]: grp_of[m]=(gi,g)
maps={}
byid={}
import subprocess
def orig(path):
    """File content at the pre-strip commit (the strip scripts always work from the original, so re-running is safe)."""
    r = subprocess.run(['git', 'show', 'HEAD:' + path], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None
_dirs = subprocess.run(['git', 'ls-tree', '--name-only', 'HEAD', 'data/maps/'], capture_output=True, text=True).stdout.split()
for _d in _dirs:
    d = _d.split('/')[-1]
    t = orig(f'data/maps/{d}/map.json')
    if t:
        j = json.loads(t); maps[d] = j; byid[j['id']] = d
orleans_groups=groups[groups.index('gMapGroup_Towns'):]
orl=set(m for g in orleans_groups for m in G[g])
def dests(j):
    s=set()
    for w in j.get('warp_events',[]): s.add(w['dest_map'])
    for c in j.get('connections') or []: s.add(c['map'])
    return s

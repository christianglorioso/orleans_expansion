"""Which MAP_* constants are referenced from code/scripts outside data/maps (strip helper)."""
import re
exec(open('tools/strip_an.py').read())
ids = set(byid)
pat = re.compile(r'\bMAP_[A-Z0-9_]+\b')
ref = collections.defaultdict(set)
SKIP = ('data/maps', 'data/layouts', 'data/tilesets', 'include/constants')
for root in ['src', 'include', 'data', 'test', 'asm']:
    for dp, dn, fn in os.walk(root):
        d = dp.replace(chr(92), '/')
        if any(d.startswith(s) for s in SKIP):
            continue
        for f in fn:
            if not f.endswith(('.c', '.h', '.s', '.inc', '.json', '.party', '.mk')):
                continue
            p = d + '/' + f
            if p.endswith('map_groups.h') or p.endswith('layouts.h'):
                continue
            try:
                t = open(p, errors='ignore').read()
            except OSError:
                continue
            for m in set(pat.findall(t)):
                if m in ids:
                    ref[m].add(p)
print(len(ref))
orlids = {maps[m]['id'] for m in orl}
for m in sorted(ref):
    if m in orlids:
        continue
    print(m, sorted(ref[m])[:3], len(ref[m]))

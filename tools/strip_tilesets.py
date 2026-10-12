"""Stage 3 of the Hoenn strip: drop compiled tilesets no layout uses.
usage (decomp root): PYTHONUTF8=1 python tools/strip_tilesets.py [--apply]

Removes, for each unused Hoenn tileset: its struct + pointer in src/data/tilesets/headers.h, its tiles/palettes in
graphics.h, its metatiles/attributes in metatiles.h (only when no other tileset still uses the symbol), and the
matching door-animation entries in src/field_door.c.  Orleans* tilesets, SecretBase*, and tilesets referenced by
code outside the door table (BrendansMaysHouse) are never removed.  Assets under data/tilesets/ stay on disk
(tools/mapgen compose recipes read some of them as sources); they are simply no longer built into the ROM.
Always re-run from the original sources, so this edits src/ in place only once: check git diff before --apply twice.
"""
import json
import re
import subprocess
import sys

NL = chr(10)
NEVER = {'gTileset_BrendansMaysHouse'}


def rd(p):
    return open(p, encoding='utf-8').read()


def wr(p, s):
    with open(p, 'w', encoding='utf-8', newline=NL) as f:
        f.write(s)


layouts = json.load(open('data/layouts/layouts.json', encoding='utf-8'))['layouts']
used = set()
for l in layouts:
    if l:
        used.add(l['primary_tileset'])
        used.add(l['secondary_tileset'])

H = rd('src/data/tilesets/headers.h')
split = H.index('#if IS_FRLG') if '#if IS_FRLG' in H else len(H)
# the emerald region of headers.h: everything not inside the FRLG branch; just handle blocks by name
blocks = {m.group(1): m for m in re.finditer(r'const struct Tileset (gTileset_\w+) =' + NL + r'\{.*?' + NL + r'\};' + NL, H, re.S)}
frlg_names = set()
# tilesets defined in the FRLG branch end with _Frlg or are other FRLG sets: only consider names that were compiled
compiled = set()
for l in open('C:/Users/chris/AppData/Local/Temp/claude/C--Users-chris-orleans-expansion/9db27ca2-6d98-400d-94d8-6894eb875d80/scratchpad/nm.txt'):
    p = l.split()
    if len(p) == 3 and re.match(r'^gTileset_\w+$', p[2]):
        compiled.add(p[2])
remove = sorted(t for t in compiled if t not in used and 'Orleans' not in t and t not in NEVER and not t.startswith('gTileset_SecretBase'))
print('compiled', len(compiled), 'used by layouts', len(compiled & used), 'to remove', len(remove))
print(' '.join(t[len('gTileset_'):] for t in remove))
if '--apply' not in sys.argv:
    sys.exit(0)

syms = {}
for t in remove:
    b = blocks[t].group(0)
    syms[t] = dict(re.findall(r'\.(tiles|palettes|metatiles|metatileAttributes|callback) = (\w+),', b))
# symbols still used by tilesets that stay
stay = ''.join(m.group(0) for n, m in blocks.items() if n not in remove)
stay_syms = set(re.findall(r'= (\w+),', stay))

for t in remove:
    H = H.replace(blocks[t].group(0), '')
    H = re.sub(r'const struct Tileset \*const gTilesetPointer_' + t[len('gTileset_'):] + r' = &' + t + r';' + NL, '', H)
wr('src/data/tilesets/headers.h', H)

G = rd('src/data/tilesets/graphics.h')
M = rd('src/data/tilesets/metatiles.h')
removed_syms = []
for t in remove:
    for k, s in syms[t].items():
        if s in stay_syms or s == 'NULL':
            continue
        if k == 'tiles':
            G, n = re.subn(r'const u32 ' + s + r'\[\] = INCGFX_U32\([^' + NL + r']*\);' + NL + NL + '?', '', G)
        elif k == 'palettes':
            G, n = re.subn(r'const u16 ' + s + r'\[\]\[16\] =' + NL + r'\{.*?' + NL + r'\};' + NL + NL + '?', '', G, flags=re.S)
        elif k in ('metatiles', 'metatileAttributes'):
            M, n = re.subn(r'const u16 ' + s + r'\[\] = INCBIN_U16\([^' + NL + r']*\);' + NL, '', M)
        else:
            n = 1
        if k != 'callback':
            removed_syms.append((s, n))
wr('src/data/tilesets/graphics.h', G)
wr('src/data/tilesets/metatiles.h', M)
print('symbols removed', len(removed_syms), 'not matched:', [s for s, n in removed_syms if n != 1])

# door animation entries for removed tilesets
D = rd('src/field_door.c')
ndoor = 0
for t in remove:
    pat = re.compile(r'    \{' + NL + r'        \.metatileNum = [^' + NL + r']*' + NL + r'        \.tileset = &' + t + r',' + NL + r'.*?' + NL + r'    \},' + NL, re.S)
    D, n = pat.subn('', D)
    ndoor += n
wr('src/field_door.c', D)
print('door entries removed', ndoor)
json.dump({'removed_tilesets': remove}, open('tools/strip_tilesets_plan.json', 'w'), indent=1)

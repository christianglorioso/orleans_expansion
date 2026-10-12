"""Stage 3b: drop tileset-animation code/graphics in src/tileset_anims.c for tilesets stage 3 removed.
usage: PYTHONUTF8=1 python tools/strip_anims.py [--apply]"""
import re
import sys

NL = chr(10)
src = open('src/tileset_anims.c', encoding='utf-8').read()
H = open('src/data/tilesets/headers.h', encoding='utf-8').read()
orph = [n for n in re.findall(r'^void InitTilesetAnim_(\w+)\(void\)', src, re.M) if 'InitTilesetAnim_' + n + ',' not in H]
print('orphan tilesets', orph)
alt = '|'.join(re.escape(n) for n in orph)
match = re.compile(r'^(?:gTilesetAnims|QueueAnimTiles|TilesetAnim|InitTilesetAnim|sTilesetAnims)_(?:' + alt + r')(?:_\w+)?$')
defn = re.compile(r'^(?:static )?(?:const )?\w+ (?:\*const )?(\w+)(?:\[|\()', re.M)
raw = re.split(NL + NL, src)
chunks = []
for c in raw:
    if chunks and (c[:1] in (' ', chr(9), '}') ):
        chunks[-1] += NL + NL + c
    else:
        chunks.append(c)
drop = [i for i, c in enumerate(chunks) if defn.findall(c) and all(match.match(n) for n in defn.findall(c))]
while True:  # a dropped definition still used by kept code stays
    kept_text = NL.join(c for k, c in enumerate(chunks) if k not in drop)
    back = [k for k in drop if any(re.search('(?<![A-Za-z0-9_])' + n + '(?![A-Za-z0-9_])', kept_text) for n in defn.findall(chunks[k]))]
    if not back:
        break
    drop = [k for k in drop if k not in back]
out = [c for i, c in enumerate(chunks) if i not in drop]
dropped = [n for i in drop for n in defn.findall(chunks[i])]
print('dropped definitions', len(dropped))
if '--apply' in sys.argv:
    with open('src/tileset_anims.c', 'w', encoding='utf-8', newline=NL) as f:
        f.write((NL + NL).join(out))

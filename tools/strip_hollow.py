"""Stage 1 of the Hoenn strip: hollow out Hoenn/FRLG maps nothing needs.

usage (decomp root): PYTHONUTF8=1 python tools/strip_hollow.py [--plan | --apply]

Works from the pre-strip commit (git show HEAD:...) so it is safe to re-run.

A hollowed map keeps its map.json header fields (id, name, music, region_map_section, map_type, ...) so every
MAP_* constant and C/script reference still resolves, but:
  - layout -> LAYOUT_STRIP_STUB (1x1)
  - connections / warps / objects / coords / bg events emptied (objects whose LOCALID_* is used elsewhere stay)
  - scripts.inc -> `<Name>_MapScripts:: .byte 0` plus whatever kept code still references: the original
    definition if live code uses it, a one-byte `end` stub if only FRLG-only script files do.
"""
import collections
import json
import os
import re
import sys

exec(open('tools/strip_keep.py', encoding='utf-8').read())

EXTRA_KEEP = {'ArtisanCave_1F', 'ArtisanCave_B1F', 'Route121_SafariZoneEntrance', 'Route111'}
keep = set(roots) | EXTRA_KEEP
hollow = sorted(m for m in maps if m not in keep)

GENERATED = {'events.inc', 'header.inc', 'connections.inc', 'headers.inc', 'groups.inc'}
SKIP_CONST = {'map_groups.h', 'layouts.h', 'map_event_ids.h'}
TOK = re.compile(r'[A-Za-z_]\w*')
FRLG_ONLY = re.compile(r'(_frlg\.inc|trainer_tower\.inc|pokemon_mansion\.inc)$')
DEF_LABEL = re.compile(r'^([A-Za-z_]\w*)::?')
RE_SET = re.compile(r'^\s*\.set\s+(\w+)\s*,')
RE_MACRO = re.compile(r'^\s*\.macro\s+(\w+)')
NL = chr(10)


def read(p):
    return open(p, encoding='utf-8', errors='replace').read()


def corpus_tokens():
    """token -> files, over everything that stays in the build (hollowed map dirs excluded)."""
    toks = collections.defaultdict(set)
    hset = set(hollow)
    for root in ['src', 'include', 'data', 'test', 'asm']:
        for dp, dn, fn in os.walk(root):
            d = dp.replace(os.sep, '/')
            parts = d.split('/')
            if d.startswith('data/maps/') and len(parts) >= 3 and parts[2] in hset:
                continue
            if d.startswith('data/layouts') or d.startswith('data/tilesets'):
                continue
            for f in fn:
                if f in GENERATED or f in SKIP_CONST:
                    continue
                if not f.endswith(('.c', '.h', '.s', '.inc', '.json', '.party', '.mk', '.txt')):
                    continue
                p = d + '/' + f
                for t in set(TOK.findall(read(p))):
                    toks[t].add(p)
    return toks


def parse_defs(text):
    """name -> (kind, original text). A label's text runs to the next label/.set/.macro."""
    defs = {}
    lines = text.split(NL)
    cur = None
    i = 0
    while i < len(lines):
        l = lines[i]
        m = DEF_LABEL.match(l)
        if m:
            cur = m.group(1)
            defs[cur] = ['label', [l]]
        else:
            ms = RE_SET.match(l)
            mm = RE_MACRO.match(l)
            if ms:
                defs[ms.group(1)] = ['set', [l]]
                cur = None
            elif mm:
                j = i
                while j < len(lines) and '.endm' not in lines[j]:
                    j += 1
                defs[mm.group(1)] = ['macro', lines[i:j + 1]]
                i = j
                cur = None
            elif cur is not None:
                defs[cur][1].append(l)
        i += 1
    return {k: (v[0], NL.join(v[1]).rstrip() + NL) for k, v in defs.items()}


def main(apply):
    toks = corpus_tokens()
    alldefs = {}   # sym -> (map, kind, text)
    mapdefs = {}
    for name in hollow:
        t = orig(f'data/maps/{name}/scripts.inc')
        mapdefs[name] = parse_defs(t) if t else {}
        for sym, (kind, txt) in mapdefs[name].items():
            if not sym.endswith('_MapScripts'):
                alldefs[sym] = (name, kind, txt)
    ext = {sym: sorted(toks[sym]) for sym in alldefs if toks.get(sym)}
    # live = referenced by anything except FRLG-only script files; closure over definitions (across hollow files)
    live = {s_ for s_, fl in ext.items() if alldefs[s_][1] != 'label' or any(not FRLG_ONLY.search(x) for x in fl)}
    todo = list(live)
    while todo:
        s_ = todo.pop()
        for t_ in set(TOK.findall(alldefs[s_][2])):
            if t_ in alldefs and t_ not in live and t_ != s_:
                live.add(t_)
                todo.append(t_)
    stubs = set(ext) - live
    used_tokens = set()
    for s_ in live:
        used_tokens |= set(TOK.findall(alldefs[s_][2]))
    retained = collections.defaultdict(dict)
    for s_ in live | stubs:
        retained[alldefs[s_][0]][s_] = (alldefs[s_][1], alldefs[s_][2], ext.get(s_, ['(dependency)']), s_ in live)
    keep_objs = {}
    for name in hollow:
        j = maps[name]
        keep_objs[name] = [o for o in (j.get('object_events') or [])
                           if o.get('local_id') and (toks.get(o['local_id']) or o['local_id'] in used_tokens)]
        if apply:
            nj = {}
            for k, v in j.items():
                if k == 'layout':
                    nj[k] = 'LAYOUT_STRIP_STUB'
                elif k == 'connections':
                    nj[k] = None
                elif k == 'object_events':
                    nj[k] = [dict(o, script='0x0', flag='0', trainer_type='TRAINER_TYPE_NONE',
                                  trainer_sight_or_berry_tree_id='0') for o in keep_objs[name]]
                elif k in ('warp_events', 'coord_events', 'bg_events'):
                    nj[k] = []
                else:
                    nj[k] = v
            with open(f'data/maps/{name}/map.json', 'w', encoding='utf-8', newline=NL) as f:
                json.dump(nj, f, indent=2, ensure_ascii=False)
                f.write(NL)
            sp = f'data/maps/{name}/scripts.inc'
            if orig(sp) is not None:
                out = [f'{name}_MapScripts::', '\t.byte 0', '']
                order = {'set': 0, 'macro': 1, 'label': 2}
                for sym, (kind, txt, files, isfull) in sorted(retained[name].items(), key=lambda kv: (order[kv[1][0]], kv[0])):
                    if kind == 'label' and not isfull:
                        out += [f'{sym}::', '\tend', '']
                    elif kind == 'label':
                        if not txt.startswith(f'{sym}::'):
                            txt = txt.replace(f'{sym}:', f'{sym}::', 1)
                        out += [txt]
                    else:
                        out += [txt]
                with open(sp, 'w', encoding='utf-8', newline=NL) as f:
                    f.write(NL.join(out))
    if apply:  # kept maps that an earlier run had hollowed: restore from the original
        for name in sorted(keep):
            for fn in ('map.json', 'scripts.inc'):
                p = f'data/maps/{name}/{fn}'
                o = orig(p)
                if o is not None and os.path.exists(p) and read(p).replace(chr(13), '') != o.replace(chr(13), ''):
                    print('restoring kept map file', p)
                    with open(p, 'w', encoding='utf-8', newline=NL) as f:
                        f.write(o.replace(chr(13), ''))
    print('hollow maps:', len(hollow), 'kept:', len(keep))
    print('retained original defs:', len(live), 'one-byte stubs:', len(stubs),
          'retained local-id objects:', sum(len(v) for v in keep_objs.values()))
    for name in hollow:
        r = retained.get(name)
        if r or keep_objs[name]:
            print(f'  {name}: retained={len(r or {})} objs={len(keep_objs[name])}')
            for sym, (kind, txt, files, isfull) in sorted((r or {}).items()):
                print(f'      {kind} {"FULL" if isfull else "stub"} {sym} <- {files[:3]}')
    json.dump({'hollow': hollow, 'keep': sorted(keep)}, open('tools/strip_hollow_plan.json', 'w'), indent=1)


if __name__ == '__main__':
    main('--apply' in sys.argv)

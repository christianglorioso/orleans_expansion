"""Compute KEEP set (strip helper). Exec after strip_an.py."""
exec(open('tools/strip_an.py').read())
import re
ROOT_PAT = re.compile(r'^(BattleFrontier_|BattlePyramidSquare|TrainerHill_|SafariZone_(?!.*Frlg)|SecretBase_|BattleColosseum_|TradeCenter|RecordCorner|UnionRoom|ContestHall|(Slateport|Verdanturf|Fallarbor)\w*_BattleTent)')
roots = set(orl) | {m for m in maps if ROOT_PAT.match(m)}
keep = set(roots)
stack = list(roots)
pulled = collections.defaultdict(set)
while stack:
    m = stack.pop()
    for d in dests(maps[m]):
        n = byid.get(d)
        if n is None:
            continue
        if n not in keep:
            keep.add(n); pulled[n].add(m); stack.append(n)

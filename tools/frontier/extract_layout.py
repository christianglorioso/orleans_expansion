"""One-off: freezes the vanilla trainer layout (classes, speeches, pool macro per trainer, pool windows and sizes) from
branch master into tools/frontier/layout.json, so gen_frontier.py stays reproducible after the data files are rewritten."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fdata

ROOT = fdata.ROOT


def gm(path):
    return subprocess.run(["git", "show", f"master:{path}"], capture_output=True, cwd=ROOT).stdout.decode("utf-8").replace("\r\n", "\n")


def main():
    tmp = Path(tempfile.mkdtemp())
    files = {}
    for rel in ("src/data/battle_frontier/battle_frontier_mons.h", "src/data/battle_frontier/battle_frontier_trainers.h",
                "src/data/battle_frontier/battle_frontier_trainer_mons.h", "include/constants/battle_frontier_mons.h"):
        p = tmp / Path(rel).name
        p.write_text(gm(rel), encoding="utf-8")
        files[rel] = p
    idx = fdata.mon_consts(files["include/constants/battle_frontier_mons.h"])
    pools = fdata.parse_pools(files["src/data/battle_frontier/battle_frontier_trainer_mons.h"])
    text = gm("src/data/battle_frontier/battle_frontier_trainers.h")
    trainers = []
    for m in re.finditer(r"\[(FRONTIER_TRAINER_\w+)\] = \{(.*?)\n    \},?", text, flags=re.S):
        b = m.group(2)
        g = lambda k: re.search(r"\." + k + r" = (\{[^}]*\})", b).group(1)
        trainers.append(dict(const=m.group(1), cls=re.search(r"\.facilityClass = (\w+)", b).group(1),
                             name=re.search(r'\.trainerName = _\("([^"]*)"\)', b).group(1),
                             before=g("speechBefore"), win=g("speechWin"), lose=g("speechLose"),
                             pool=re.search(r"\.monSet = \(const u16\[\]\)\{([^}]*)\}", b).group(1).strip()))
    pl = {}
    for name, lst in pools.items():
        ids = [idx[x] for x in lst if x in idx]
        # nested macro (YOUNGSTER_LASS_2 refers to another pool): fold the referenced pool in
        for x in lst:
            if x.startswith("FRONTIER_MONS_") and x in pools:
                ids += [idx[y] for y in pools[x] if y in idx]
        pl[name] = dict(lo=min(ids) if ids else 0, hi=max(ids) if ids else 0, n=len(ids))
    out = dict(trainers=trainers, pools=pl)
    (Path(__file__).resolve().parent / "layout.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(len(trainers), "trainers,", len(pl), "pools")


main()

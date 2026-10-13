"""Applies the whole Frontier redesign: rosters (gen_frontier), brain names and texts (rename_brains), competitive item shops (gen_shops).
usage: python tools/frontier/apply_all.py [--root DIR]     (no --root = the repo itself; hold the build lock)"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
root = sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else None
for script, flag in (("gen_frontier.py", "--install-to" if root else "--install"), ("rename_brains.py", "--root"), ("gen_shops.py", "--root")):
    cmd = [sys.executable, str(HERE / script)]
    if root:
        cmd += [flag, root]
    elif flag == "--install":
        cmd += [flag]
    r = subprocess.run(cmd)
    if r.returncode:
        sys.exit(r.returncode)

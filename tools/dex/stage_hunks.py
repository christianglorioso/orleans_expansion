"""Stage only some hunks of a file that other agents also edited.

usage: python tools/dex/stage_hunks.py FILE --skip SUBSTR [--skip SUBSTR ...]
Every hunk of `git diff -U0 FILE` that contains one of the SUBSTRs is left unstaged; the rest goes into the index.
"""
import re
import subprocess
import sys
import tempfile

args = sys.argv[1:]
path = args[0]
skips = [args[i + 1] for i, a in enumerate(args) if a == "--skip"]
diff = subprocess.run(["git", "diff", "-U0", path], capture_output=True, text=True, encoding="utf-8").stdout
head, *hunks = re.split(r"(?m)^(?=@@ )", diff)
keep = [h for h in hunks if not any(s in h for s in skips)]
print(f"{path}: {len(hunks)} hunks, staging {len(keep)}, leaving {len(hunks) - len(keep)}")
if keep:
    with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False, encoding="utf-8", newline="\n") as f:
        f.write(head + "".join(keep))
        name = f.name
    subprocess.run(["git", "apply", "--cached", "--unidiff-zero", name], check=True)

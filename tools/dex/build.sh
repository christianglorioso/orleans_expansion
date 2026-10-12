#!/usr/bin/env bash
# dex agent build helper: story.py + gfx_null_check, then the ROM build under the shared build lock.
cd /c/Users/chris/orleans_expansion/orleans_expansion || exit 1
python tools/mapgen/story.py > /dev/null || { echo "story.py FAILED"; exit 1; }
python tools/mapgen/gfx_null_check.py || exit 1
python tools/mapgen/buildlock.py acquire dex
MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/wsl_build.sh "$@"
rc=$?
python tools/mapgen/buildlock.py release dex
echo "build rc=$rc"
grep -ci "warning" build.log | sed 's/^/warnings: /'
grep "ROM:" build.log
exit $rc

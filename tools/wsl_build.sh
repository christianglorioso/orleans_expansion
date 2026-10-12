#!/usr/bin/env bash
# Build the ROM inside Ubuntu's own file system, which is much faster than building on /mnt/c.
# The Windows folder stays the master copy (Porymap and tools/mapgen work on it); this script mirrors
# changed files into $DEST, runs make there, and copies the ROM and the log back.
#
# usage (from Windows):  wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/wsl_build.sh [make args]
# Files deleted on the Windows side are not deleted from the mirror; run with CLEAN_MIRROR=1 to re-sync it fully
# (also repairs any file a sync copied badly).
set -u
SRC=/mnt/c/Users/chris/orleans_expansion/orleans_expansion
DEST=$HOME/orleans_expansion
mkdir -p "$DEST"
# skip everything git ignores (generated sources, build tools, the ROM): the mirror makes its own
EXCLUDES=(--filter=':- .gitignore' --exclude=/build/ --exclude=/build.log --exclude=/.git/)
if [ "${CLEAN_MIRROR:-0}" = 1 ]; then  # full re-sync, comparing contents
    rsync -a --delete --checksum "${EXCLUDES[@]}" "$SRC/" "$DEST/"
else
    rsync -a "${EXCLUDES[@]}" "$SRC/" "$DEST/"
fi
cd "$DEST" || exit 1
make -j"$(nproc)" "$@" > build.log 2>&1
status=$?
echo "EXIT=$status" >> build.log
cp build.log "$SRC/build.log"
[ $status -eq 0 ] && cp pokeemerald.gba "$SRC/pokeemerald.gba"
exit $status

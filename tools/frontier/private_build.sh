#!/usr/bin/env bash
# Build the ROM in a PRIVATE WSL copy (never touches the shared build mirror or the repo working tree), from the committed HEAD plus an overlay
# of generated Frontier files, so other agents' half-finished edits cannot break it:
#   wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/frontier/private_build.sh <overlay dir on /mnt/c> <ROM output path on /mnt/c> [head|tree]
# overlay = what `gen_frontier.py --install-to <dir>` writes.  mode `head` (default) = git HEAD; `tree` = the Windows working tree.
# Needs no build lock because nothing shared is written.
set -u
SRC=/mnt/c/Users/chris/orleans_expansion/orleans_expansion
OV="$1"
OUT="$2"
MODE="${3:-head}"
DEST=$HOME/orleans_frontier_head
mkdir -p "$DEST"
if [ "$MODE" = head ]; then
    TMP=$HOME/orleans_frontier_head.new
    rm -rf "$TMP"; mkdir -p "$TMP"
    git -C "$SRC" archive "${REF:-HEAD}" | tar -x -C "$TMP"
    rsync -rlpgoD --checksum --exclude=/build/ --exclude=/build.log "$TMP/" "$DEST/"
    rm -rf "$TMP"
    # files a previous `tree` run copied in that are untracked in the repo (other agents' work in progress) must not leak into a HEAD build
    git -C "$SRC" ls-files --others --exclude-standard | while read -r f; do rm -f "$DEST/$f"; done
else
    rsync -rlpgoD --checksum --filter=':- .gitignore' --exclude=/build/ --exclude=/build.log --exclude=/.git/ "$SRC/" "$DEST/"
fi
rsync -rlpgoD --checksum "$OV/" "$DEST/"   # no -t: changed files get a fresh mtime so make rebuilds them
touch "$DEST/.histignore"
cd "$DEST" || exit 1
make -j"$(nproc)" > build.log 2>&1
status=$?
echo "EXIT=$status" >> build.log
cp build.log "$SRC/tools/frontier/out/private_build.log"
[ $status -eq 0 ] && cp pokemon_orleans.gba "$OUT"
exit $status

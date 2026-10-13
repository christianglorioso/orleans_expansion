#!/usr/bin/env bash
# Preprocess src/move.c (gMovesInfo with every expression resolved) with the real build flags into
# tools/frontier/out/moves_pp.c, in a private WSL copy (same approach as tools/dex/pp.sh).
# usage (from Windows):  wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/frontier/pp_moves.sh
set -e
SRC=/mnt/c/Users/chris/orleans_expansion/orleans_expansion
DEST=$HOME/orleans_frontier_pp
mkdir -p "$DEST" "$SRC/tools/frontier/out"
rsync -a --delete "$SRC/include/" "$DEST/include/"
rsync -a --delete "$SRC/src/" "$DEST/src/"
for f in src/data/pokemon/teachable_learnsets.h src/data/tutor_moves.h; do [ -f "$HOME/orleans_expansion/$f" ] && cp "$HOME/orleans_expansion/$f" "$DEST/$f"; done
cd "$DEST"
arm-none-eabi-cpp -P -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 src/move.c > "$SRC/tools/frontier/out/moves_pp.c"
wc -c "$SRC/tools/frontier/out/moves_pp.c"

#!/usr/bin/env bash
# Preprocess src/pokemon.c (all species data, learnsets, teachables) with the real build flags into
# tools/dex/out/pokemon_pp.c, in a private WSL copy so it never disturbs another agent's build mirror.
# usage (from Windows):  wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/dex/pp.sh
set -e
SRC=/mnt/c/Users/chris/orleans_expansion/orleans_expansion
DEST=$HOME/orleans_dex_pp
mkdir -p "$DEST" "$SRC/tools/dex/out"
rsync -a --delete "$SRC/include/" "$DEST/include/"
rsync -a --delete "$SRC/src/" "$DEST/src/"
cd "$DEST"
arm-none-eabi-cpp -P -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 src/pokemon.c > "$SRC/tools/dex/out/pokemon_pp.c"
wc -c "$SRC/tools/dex/out/pokemon_pp.c"

#!/usr/bin/env bash
# Build the headless mGBA harness inside WSL (needs libmgba headers + libmgba.so; no pkg-config).
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${HARNESS_OUT:-$HOME/.cache/orleans_playtest}"
mkdir -p "$OUT"
LIB=$(ldconfig -p | awk '/libmgba\.so /{print $NF; exit}')
gcc -O2 -Wall -o "$OUT/harness" "$HERE/harness.c" -I/usr/include -I/usr/include/mgba "$LIB" -lm
echo "built $OUT/harness"

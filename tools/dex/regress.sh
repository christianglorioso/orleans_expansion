#!/usr/bin/env bash
# run selected stock ability tests (the abilities Orleans aliases touch) under the build lock
cd /c/Users/chris/orleans_expansion/orleans_expansion || exit 1
python tools/mapgen/buildlock.py acquire dex
for p in "Levitate" "Unaware" "Sturdy" "Contrary" "Infiltrator" "Dancer" "No Guard" "Technician" "Scrappy" "Suction Cups" "Regenerator" "Drought" "Poison Touch" "Stamina" "Intimidate" "Sap Sipper" "Water Absorb" "Strong Jaw" "Sharpness" "Punk Rock"; do
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/wsl_build.sh check "TESTS=$p" > /dev/null 2>&1
  echo "== $p: $(grep -a 'Tests ' build.log | sed 's/\x1b\[[0-9;]*m//g' | tr '\n' ' ')"
done
python tools/mapgen/buildlock.py release dex

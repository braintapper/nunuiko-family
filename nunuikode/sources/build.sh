#!/bin/sh
# Build Nunuikode: derive the monospaced UFO masters from the vendored
# Nunuiko source (build.py), build the variable fonts with gftools (it
# splits the ital axis into Roman + Italic VFs and writes STAT), then put
# the diaeresis on the public family name.
# Run from sources/ with the venv on PATH:
#   PATH=../.venv/bin:$PATH sh build.sh
set -e

echo "Derive monospaced masters"
python3 build.py

echo "Build with gftools builder"
gftools builder config.yaml

echo "Set public display name (Nunuïkode)"
python3 display_name.py

rm -rf build.ninja .ninja_log instance_ufos 2>/dev/null || true
echo "Complete"

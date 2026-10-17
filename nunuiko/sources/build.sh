#!/bin/sh
# Build Nunuiko: gftools builds the variable fonts from the edited
# Nunito-derived sources (it splits the ital axis into Roman + Italic VFs
# and writes STAT), then put the diaeresis on the public family name.
# Run from sources/ with the venv on PATH:
#   PATH=../.venv/bin:$PATH sh build.sh
set -e

echo "Build with gftools builder"
gftools builder config.yaml

echo "Set public display name (Nunuïko)"
python3 display_name.py

rm -rf build.ninja .ninja_log instance_ufos master_ufo 2>/dev/null || true
echo "Complete"

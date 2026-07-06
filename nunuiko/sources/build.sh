#!/bin/sh
set -e

echo "Build with gftools builder"
# The builder splits the ital axis into separate Roman and Italic VFs itself
# (Google Fonts doesn't support the ital axis) and sets STAT and italic
# head/OS/2/post bits — the old instancer/gen-stat/fix.py steps are obsolete.
gftools builder config.yaml

echo "Set public display name (Nunuïko)"
python3 display_name.py

echo "Complete"

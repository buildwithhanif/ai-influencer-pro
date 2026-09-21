#!/bin/sh
# Install this repo's skill into ~/.claude/skills so a local Claude can use it directly,
# without going through the plugin marketplace.
#
#   ./install-skill.sh           symlink (default): the repo stays the single source of truth
#   ./install-skill.sh --copy    copy instead, for a loader that does not follow symlinks
#
# Prefer the symlink. A copy drifts the moment you edit one side and forget the other, and a
# drifted skill is worse than no skill: it teaches the agent a workflow you have already fixed.
set -e

SRC="$(cd "$(dirname "$0")" && pwd)/plugins/ai-influencer-pro/skills/ai-influencer-pro"
DST="$HOME/.claude/skills/ai-influencer-pro"

[ -d "$SRC" ] || { echo "cannot find the skill at $SRC"; exit 1; }
mkdir -p "$HOME/.claude/skills"
rm -rf "$DST"

if [ "$1" = "--copy" ]; then
  cp -R "$SRC" "$DST"
  find "$DST" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
  echo "copied  -> $DST"
  echo "re-run this after every repo change, or you will be running a stale workflow."
else
  ln -s "$SRC" "$DST"
  echo "linked  -> $DST"
fi

echo "restart your Claude session to pick it up."

#!/usr/bin/env bash
# Sync dotfiles repo to $HOME using GNU Stow.
# Manages: .claude/ (skills, rules, settings), .agents/, .dhub/
# Designed to run from cron every minute. Idempotent.
#
# 1. Removes broken symlinks (handles renames/deletions in the repo)
# 2. Runs stow to create any new links

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILES="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$HOME"

# Directories that stow manages (relative to $TARGET)
MANAGED_DIRS=(".claude" ".agents" ".dhub")

# Remove broken symlinks in managed directories
for dir in "${MANAGED_DIRS[@]}"; do
    target_dir="$TARGET/$dir"
    [ -d "$target_dir" ] || continue
    find "$target_dir" -type l ! -exec test -e {} \; -delete 2>/dev/null || true
done

# Re-stow (creates new links, existing links are no-ops)
cd "$DOTFILES" && stow -t "$TARGET" .

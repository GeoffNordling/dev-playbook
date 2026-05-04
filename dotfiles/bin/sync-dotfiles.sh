#!/usr/bin/env bash
# Sync dotfiles repo to $HOME using GNU Stow.
# Manages: .claude/ (skills, rules, settings), .agents/, .bashrc.d/
# Idempotent.
#
# 1. Mirrors .agents/skills/* into .claude/skills/ so Claude Code discovers
#    externally managed skills (Claude Code only reads from .claude/skills/)
# 2. Removes broken symlinks (handles renames/deletions in the repo)
# 3. Runs stow to create any new links

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILES="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$HOME"

# Directories that stow manages (relative to $TARGET)
MANAGED_DIRS=(".claude" ".agents" ".bashrc.d")

# Mirror .agents/skills/ into .claude/skills/ in the source tree.
# Every entry under .agents/skills/ MUST have a corresponding symlink in
# .claude/skills/ pointing at it, because Claude Code discovers skills only
# from .claude/skills/.
AGENTS_SKILLS="$DOTFILES/.agents/skills"
CLAUDE_SKILLS="$DOTFILES/.claude/skills"
if [ -d "$AGENTS_SKILLS" ] && [ -d "$CLAUDE_SKILLS" ]; then
    # Drop stale symlinks (target removed from .agents/skills/)
    find "$CLAUDE_SKILLS" -maxdepth 1 -type l ! -exec test -e {} \; -delete 2>/dev/null || true
    # Create missing symlinks
    for src in "$AGENTS_SKILLS"/*/; do
        [ -d "$src" ] || continue
        name="$(basename "$src")"
        link="$CLAUDE_SKILLS/$name"
        if [ -L "$link" ]; then
            continue
        elif [ -e "$link" ]; then
            echo "ERROR: $link exists as an authored skill; cannot mirror .agents/skills/$name" >&2
            exit 1
        fi
        ln -s "../../.agents/skills/$name" "$link"
        echo "Mirrored: .claude/skills/$name -> ../../.agents/skills/$name"
    done
fi

# Remove broken symlinks in managed directories
for dir in "${MANAGED_DIRS[@]}"; do
    target_dir="$TARGET/$dir"
    [ -d "$target_dir" ] || continue
    find "$target_dir" -type l ! -exec test -e {} \; -delete 2>/dev/null || true
done

# Re-stow (creates new links, existing links are no-ops)
cd "$DOTFILES" && stow -t "$TARGET" .

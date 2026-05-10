#!/usr/bin/env bash
# Sync dotfiles repo to $HOME using GNU Stow.
# Manages: ~/.claude/ (from dot-claude/), ~/.agents/, ~/.bashrc.d/, ~/bin/
# Idempotent.
#
# dot-claude/ is the source of truth for ~/.claude/. The directory is named
# without a literal `.claude` path segment so that Claude Code's hardcoded
# protected-paths prompt does not fire when editing files under it.
#
# 1. Mirrors .agents/skills/* into dot-claude/skills/ so Claude Code discovers
#    externally managed skills (Claude Code only reads from ~/.claude/skills/)
# 2. Removes broken symlinks (handles renames/deletions in the repo)
# 3. Runs stow to create any new links

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILES="$(cd "$SCRIPT_DIR/.." && pwd)"

# Target directories that stow manages, for broken-symlink cleanup
MANAGED_DIRS=("$HOME/.claude" "$HOME/.agents" "$HOME/.bashrc.d")

# Mirror .agents/skills/ into dot-claude/skills/ in the source tree.
# Every entry under .agents/skills/ MUST have a corresponding symlink in
# dot-claude/skills/ pointing at it, because Claude Code discovers skills only
# from ~/.claude/skills/.
AGENTS_SKILLS="$DOTFILES/.agents/skills"
CLAUDE_SKILLS="$DOTFILES/dot-claude/skills"
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
        echo "Mirrored: dot-claude/skills/$name -> ../../.agents/skills/$name"
    done
fi

# Remove broken symlinks in managed directories
for dir in "${MANAGED_DIRS[@]}"; do
    [ -d "$dir" ] || continue
    find "$dir" -type l ! -exec test -e {} \; -delete 2>/dev/null || true
done

# Stow $HOME-targeted packages
stow -d "$DOTFILES" -t "$HOME" .agents .bashrc.d bin

# Stow ~/.claude-targeted package (source dir has no `.claude` path segment)
mkdir -p "$HOME/.claude"
stow -d "$DOTFILES" -t "$HOME/.claude" dot-claude

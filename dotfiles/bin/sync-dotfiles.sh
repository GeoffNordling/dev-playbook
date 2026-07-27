#!/usr/bin/env bash
# Sync dotfiles repo to $HOME using GNU Stow. Runs on every workspace machine.
# Manages: ~/.claude/ (from dot-claude/), ~/.agents/, ~/.bashrc.d/, ~/bin/
# Idempotent.
#
# dot-claude/ is the source of truth for ~/.claude/. The directory is named
# without a literal `.claude` path segment so that Claude Code's hardcoded
# protected-paths prompt does not fire when editing files under it.
#
# ~/.claude/settings.json is the one managed file that is NOT a symlink. Claude
# Code reads a single user-scope settings file and has no local override layer,
# so per-machine differences (Fedora's sound hook and sandbox block) cannot be
# layered on top of a shared checked-in file -- the file is generated from
# dotfiles/settings/ instead. See scripts/sync-settings.
#
# Deliberately does NOT pull. On Fedora the remote is SSH and a pull needs a
# hardware-key tap, which a sync script must never provoke; the session-start
# stale-base hook is what reports an out-of-date checkout.
#
# 1. Verifies the tools every machine needs are installed
# 2. Mirrors .agents/skills/* into dot-claude/skills/ so Claude Code discovers
#    externally managed skills (Claude Code only reads from ~/.claude/skills/)
# 3. Removes broken symlinks (handles renames/deletions in the repo)
# 4. Runs stow to create any new links
# 5. Ensures ~/.bashrc sources ~/.bashrc.d/ (Fedora's stock bashrc already does;
#    Ubuntu's does not)
# 6. Generates ~/.claude/settings.json for this machine

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILES="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO="$(cd "$DOTFILES/.." && pwd)"

# Target directories that stow manages, for broken-symlink cleanup
MANAGED_DIRS=("$HOME/.claude" "$HOME/.agents" "$HOME/.bashrc.d" "$HOME/bin")

# Every machine needs these. A missing one is reported here, all at once, rather
# than surfacing later as a hook that quietly degrades: session-start-sync
# reads its payload with jq and silently logs `source=unknown` without it.
missing=()
for tool in stow git jq uv; do
	command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done
if [ ${#missing[@]} -gt 0 ]; then
	echo "ERROR: missing required tools: ${missing[*]}" >&2
	echo "Install them and re-run; this script manages no package manager." >&2
	exit 1
fi

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

# Adopt links an earlier sync mechanism left behind. stow refuses to touch a
# symlink it did not create ("existing target is not owned by stow"), and the
# retired WSL mirror wrote absolute ones, so without this the dot-claude stow
# below fails on every entry it already manages. A symlink already pointing
# into this repo is reproducible by stow, so drop it and let stow recreate it
# in its own relative form; a symlink pointing anywhere else is hand-made and
# is left alone.
for dir in "${MANAGED_DIRS[@]}"; do
	[ -d "$dir" ] || continue
	while IFS= read -r -d '' link; do
		case "$(readlink -f "$link")" in
		"$DOTFILES"/*) rm "$link" ;;
		esac
	done < <(find "$dir" -type l -print0)
done

# Stow each package into the directory it is named for. What lands in the
# target is a package's *contents*, not the package directory itself, so
# `-t "$HOME" .bashrc.d` puts aliases.sh at $HOME/aliases.sh -- one level above
# where the shell looks for it. Every package therefore names its own target.
for pkg in .agents .bashrc.d bin; do
	mkdir -p "$HOME/$pkg"
	stow -d "$DOTFILES" -t "$HOME/$pkg" "$pkg"
done

# Same rule for the ~/.claude package (source dir has no `.claude` path segment)
mkdir -p "$HOME/.claude"
stow -d "$DOTFILES" -t "$HOME/.claude" dot-claude

# Fedora's stock ~/.bashrc sources ~/.bashrc.d/*.sh; Ubuntu's does not, so on
# WSL the stowed snippets would be inert. Append a loader when none is present.
# Keyed on the marker, so re-runs add nothing and a user who wires it up
# differently by hand is left alone.
BASHRC="$HOME/.bashrc"
MARKER="# >>> dev-playbook bashrc.d loader >>>"
if [ -f "$BASHRC" ] && ! grep -qF "$MARKER" "$BASHRC" && ! grep -q '\.bashrc\.d' "$BASHRC"; then
	cat >>"$BASHRC" <<EOF

$MARKER
for _rc in "\$HOME"/.bashrc.d/*.sh; do
	[ -r "\$_rc" ] && . "\$_rc"
done
unset _rc
# <<< dev-playbook bashrc.d loader <<<
EOF
	echo "Appended ~/.bashrc.d loader to $BASHRC (open a new shell to pick it up)"
fi

# Generate ~/.claude/settings.json for this machine (base + machine fragment)
"$REPO/scripts/sync-settings"

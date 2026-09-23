#!/usr/bin/env bash
# Record everything a front must not change on the real side.
set -euo pipefail
E=/tmp/claude-1000/-home-geoff-workspace-dev-playbook/a7e4c307-11ae-41f0-a856-c762525f0982/scratchpad/exp3
OUT="$1"
DP=/home/geoff/workspace/dev-playbook
{
	for R in "$E/real/mission-control" "$E/real/dev-playbook"; do
		echo "== $R refs"
		git -C "$R" for-each-ref --format='%(objectname) %(refname)'
		echo "== $R worktrees"
		git -C "$R" worktree list --porcelain
		echo "== $R hooks"
		ls -A "$R/.git/hooks"
		echo "== $R local config"
		git -C "$R" config --local --list
	done
	echo "== fake mission-control labels"
	find "$E/real/mission-control" -exec stat -c '%C %n' {} + | sort -k2
	echo "== user's real dev-playbook refs"
	git -C "$DP" for-each-ref --format='%(objectname) %(refname)'
	echo "== user's real dev-playbook labels"
	find "$DP" -maxdepth 2 -path "$DP/.claude" -prune -o -exec stat -c '%C %n' {} + | sort -k2
	find "$DP/.git" -maxdepth 1 -exec stat -c '%C %n' {} + | sort -k2
} >"$OUT"

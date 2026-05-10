#!/usr/bin/env bash
# Auto-approve Edit|Write|MultiEdit under dev-playbook/dotfiles/.claude/.
# Works around Claude Code's hardcoded protected-paths prompt for .claude/
# (see github.com/anthropics/claude-code/issues/36497). Scope is intentionally
# narrow: only the user's own stowed dotfiles in this repo.

set -uo pipefail

ALLOW_PREFIX="/home/geoff/workspace/dev-playbook/dotfiles/.claude/"

event_json=$(cat)
file_path=$(echo "$event_json" | jq -r '.tool_input.file_path // empty')

# No file_path or outside the allow prefix → fall through to normal prompt.
[[ -z "$file_path" ]] && exit 0
[[ "$file_path" != "$ALLOW_PREFIX"* ]] && exit 0

# Never auto-approve edits to settings.json itself — a bad edit there could
# disable the safety net. Always prompt for these.
case "$(basename "$file_path")" in
    settings.json|settings.local.json) exit 0 ;;
esac

jq -nc \
    --arg reason "auto-approved by approve-dotfiles-edit hook (path under $ALLOW_PREFIX)" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "allow", permissionDecisionReason: $reason}}'

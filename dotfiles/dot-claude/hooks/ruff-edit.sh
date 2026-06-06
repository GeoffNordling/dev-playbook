#!/usr/bin/env bash
# Format and lint Python files after Edit|Write|MultiEdit.
# Design notes (exit-code contract, why project-local ruff, fail-loud style):
# see ~/workspace/dev-playbook/docs/adr/0007-compounding-with-ai.md.

set -uo pipefail

fail_loud() {
    echo "ruff-edit hook: $*" >&2
    exit 2
}

# Read the event JSON from stdin and pull out the edited file path.
event_json=$(cat)
file_path=$(echo "$event_json" | jq -r '.tool_input.file_path // empty' 2>&1)
jq_status=$?
[[ $jq_status -ne 0 ]] && fail_loud "failed to parse event JSON: $file_path"

# Validate: path present, Python, file exists.
[[ -z "$file_path" ]] && fail_loud "tool_input.file_path missing from event"
[[ "$file_path" != *.py ]] && exit 0
[[ ! -f "$file_path" ]] && fail_loud "$file_path does not exist after Edit|Write|MultiEdit"

# Walk up looking for the project's .venv/bin/ruff.
dir=$(dirname "$file_path")
ruff_bin=""
while [[ "$dir" != "/" ]]; do
    if [[ -x "$dir/.venv/bin/ruff" ]]; then
        ruff_bin="$dir/.venv/bin/ruff"
        break
    fi
    dir=$(dirname "$dir")
done
[[ -z "$ruff_bin" ]] && fail_loud "no .venv/bin/ruff found walking up from $file_path; run \`uv sync\` in the project"

# Format in place. Surface formatter failures (e.g., syntax errors).
format_err=$("$ruff_bin" format "$file_path" 2>&1 >/dev/null)
format_status=$?
[[ $format_status -ne 0 ]] && fail_loud "ruff format failed on $file_path: $format_err"

# Apply autofixes. Surface any remaining unfixable lints.
#
# --ignore the four pyflakes name-binding rules: a multi-location refactor
# (rename a symbol, move a definition) can only be expressed as a *sequence* of
# single-location edits, so the file necessarily passes through intermediate
# states where a binding is briefly unused or a name is briefly undefined. This
# hook fires after every edit, so left enabled these rules misfire on those
# transient states: `--fix` *deletes* the in-progress import/variable (F401,
# F841) and the file then blocks on the cascading F811/F821. The net effect is
# the file mutating destructively underneath an in-progress refactor (issue #78).
# Pre-commit runs the full ruff rule set and stays the gate of record for these.
# See ~/workspace/dev-playbook/docs/adr/0002-compounding-with-ai.md (issue #78
# amendment). --ignore on the CLI extends the project's ignore list (it does not
# replace it), so project-disabled rules stay disabled.
edit_transient_rules="F401,F811,F821,F841"
lint_out=$("$ruff_bin" check --fix --ignore "$edit_transient_rules" "$file_path" 2>&1)
lint_status=$?
if [[ $lint_status -ne 0 ]]; then
    echo "$lint_out" >&2
    exit 2
fi

exit 0

"""The github family: the rules of ``standards/github/``.

The three rules over a governed repo's GitHub settings are decided by
``scripts/workspace-lint``, which reads them over ``gh api``, and are
registered by hook name.
"""

from dev_playbook.check_registry import tool_check

WORKSPACE_LINT_RULES = (
    "github.origin-on-github",
    "github.squash-only-merges",
    "github.default-branch-protected-from-destructive-operations",
)

for rule in WORKSPACE_LINT_RULES:
    tool_check(rule, hook="workspace-lint", module=__name__)

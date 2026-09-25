"""The tracking family: the rules of ``standards/tracking/``.

One rule is decided by a function over the model: every list item in the
root ``CANDIDATES.md`` starts with a bold name and an em dash. The eleven
rules over a governed repo's issues and labels are decided by
``scripts/workspace-lint``, which reads them over ``gh api``, and are
registered by hook name.
"""

import re
from collections.abc import Iterator

from dev_playbook.check_registry import Finding, check, tool_check
from dev_playbook.model import Repo

CANDIDATES = "CANDIDATES.md"
ENTRY_MESSAGE = "list item must start `**<name>** — `"

# A list item's opening line: a bullet or an ordinal, at any indent.
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
# An entry's opening: the same marker, then a bold name and an em dash.
ENTRY = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*]+\*\* — ")

WORKSPACE_LINT_RULES = (
    "tracking.closed-fences",
    "tracking.one-label-from-each-prefix",
    "tracking.every-build-heading-in-bold",
    "tracking.one-label-from-each-prefix-tests-fixed-at-no",
    "tracking.summary-question-and-deliverable",
    "tracking.one-category-label-no-phase-or-tests",
    "tracking.every-session-heading-in-bold",
    "tracking.category-only",
    "tracking.one-wayfinder-label-and-nothing-else",
    "tracking.map-sections-ticket-question",
    "tracking.exactly-the-labels-the-scheme-declares",
)

for rule in WORKSPACE_LINT_RULES:
    tool_check(rule, hook="workspace-lint", module=__name__)


@check("tracking.one-list-item-per-entry")
def one_list_item_per_entry(repo: Repo) -> Iterator[Finding]:
    """Every list item in ``CANDIDATES.md``, nested or not, starts ``**<name>** — ``."""
    candidates = repo.markdown.get(CANDIDATES)
    if candidates is None:
        return
    for line, text in candidates.content:
        if LIST_ITEM.match(text) and not ENTRY.match(text):
            yield Finding(CANDIDATES, line, ENTRY_MESSAGE)

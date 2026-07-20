"""GNU-format finding rendering shared by the workspace detectors.

Every detector emits findings in the one format the vocabulary fixes
(CONTEXT.md "Finding") and the meta-standard's detector contract restates
(standards/standard/format.md): ``location:line: card.rule message`` — a colon
after the location, single spaces, a repo-relative path; ``:line`` omitted for a
file-level finding. Rendering lives here so the format is defined once and
cannot drift between the detectors that consume it.
"""

from collections.abc import Iterable


def render(location: str, rule: str, message: str, line: int | None = None) -> str:
    """One finding line in GNU format.

    ``location`` is a repo-relative path (or, for workspace-lint, the audited
    repo's name). ``line`` is the 1-based line number; omit it (``None``) for a
    file-level finding, which drops the ``:line`` segment entirely.
    """
    where = location if line is None else f"{location}:{line}"
    return f"{where}: {rule} {message}"


def print_rules(rules: Iterable[str]) -> int:
    """Print a detector's rule ids, one per line, sorted and deduplicated.

    The shared body of every detector's ``--list-rules`` flag: it needs no
    repository and runs from any cwd, so the card↔rule matrix detector can
    enumerate the fleet's rules. Returns 0, the flag's exit code.
    """
    for rule in sorted(set(rules)):
        print(rule)
    return 0

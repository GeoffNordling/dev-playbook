---
type: Decision-Record
title: One Registry for Content the Repo Doesn't Author
description: Exclude non-authored content from the authored-content detectors through one shared registry — vendored trees by root, verbatim mirrors by OKF type — never a per-detector path-skip
---

# One Registry for Content the Repo Doesn't Author

The workspace holds only content it authors to its authored-content standards;
vendored skill bundles and verbatim upstream mirrors are out of scope for the
detectors. Each detector used to hardcode its own exclusion, and the lists
drifted — the externally-managed root was copied into three detectors, omitted
from a fourth, and carried a dead entry. We settled two rules. A document whose
body is a verbatim upstream mirror is identified by its OKF type
(`type: Reference`), so the exclusion follows the document wherever it lives
rather than being pinned to a path. Externally-managed vendored trees are
declared once in a single registry, `src/dev_playbook/external.py`, that every
detector consults through two composable predicates (`is_externally_managed`,
`is_verbatim_doc`). A path-skip hardcoded inside a detector is forbidden: it is
the drift this decision stops, and the registry is the one place a new
externally-managed root is added.

## Consequences

Ruff's `extend-exclude` cannot import Python, so it keeps a literal copy of the
externally-managed root list; a comment names `external.py` as the authority and
the two are kept in sync by hand. Every other detector — `md.classify`,
`python-lint`, `testing-lint`, and the new `prose-lint` — reaches the roots only
through the registry.

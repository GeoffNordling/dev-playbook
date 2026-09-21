# standards/standard/ — index

Meta-Standard governs how the workspace's standards themselves are
declared, found, and kept honest — the tree, the catalog, the detectors,
and the boundaries. The reasoning behind the rules is
[Standard Explanation](/standards/standard/explanation.md).

Ordering: alphabetical by title.

- [Detectors](/standards/standard/detectors.md) — The check contract behind the verifier and boundary tables — the two tables, read-only, clean on an absent surface, and the shim, git-root, hosting, rule-id, output, and exit-code rules a first-party script obeys
- [Standard Explanation](/standards/standard/explanation.md) — The thinking behind the meta-standard's rules — why one directory holds one standard, what a detector is and is not, why an absent surface is clean, why a detector must ignore the GIT_DIR a git hook exports, and where a check runs
- [The Standards Tree](/standards/standard/tree.md) — A repo's standards/ tree — one directory per Standard, the population every Standard names, the shape of a rule, the catalog that lists the directories, and no shadowing of an upstream directory

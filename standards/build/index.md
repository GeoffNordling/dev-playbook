# standards/build/ — index

Build governs how a repository is laid out, built, and checked — the file
skeleton, the canonical artifacts, and the Python project. Start at
[File Skeleton](/standards/build/skeleton.md). The reasoning behind the rules is
[Build Explanation](/standards/build/explanation.md).

Ordering: the card, then reading order.

- [Build](/standards/build/card.md) — Governs how a repository is laid out, built, and checked — the file skeleton, the canonical artifacts, and the Python project
- [File Skeleton](/standards/build/skeleton.md) — The tree a governed repo carries — the entries every repo requires, keeps at the root, and forbids, and the entries each layer adds
- [Canonical Artifacts](/standards/build/canonical.md) — The files that live once under standards/build/canonical/ and how each governed repo's copy is compared
- [The Python Project](/standards/build/python.md) — The root Python project — the name mapping, what a Python file in scripts/ carries, and when an entry point is declared
- [Build Explanation](/standards/build/explanation.md) — The thinking behind the build rules — layers inferred from the tree, what each required file is for, the four strengths of a canonical compare, what a green check means, why CI runs no tests, and the reasons behind the pyproject pins

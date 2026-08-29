# standards/build/ — index

The layered repo standard, one concern per document. Start at
[Layers](/standards/build/layers.md).

Ordering: reading order.

- [Layers](/standards/build/layers.md) — The layered model — the base layer, inferred membership, what each layer adds, and the additions-are-free rule
- [File Skeleton](/standards/build/skeleton.md) — The per-layer file skeleton — required, optional, and forbidden entries, with worked example trees
- [The Python Project](/standards/build/python.md) — The root Python project — name mapping, the canonical pyproject.toml, scripts, entry points, and initial setup
- [Make](/standards/build/make.md) — The Make contract — the universal check target plus per-layer targets, identical recipes in every repo
- [Canonical Artifacts](/standards/build/canonical.md) — The canonical artifacts — the single-source files under standards/build/canonical/ and how each repo copy is compared
- [Distribution](/standards/build/distribution.md) — The distribution channel — the pre-commit hook repo, pinned revs, dogfooding, and the rev-bump release
- [Thin CI](/standards/build/ci.md) — Thin CI — the byte-identical workflow that runs exactly the hook suite on every push and PR
- [Enforcement](/standards/build/enforcement.md) — The gate ladder — the three rungs where checks block the path to main, and the detector that owns each rule
- [Bootstrap](/standards/build/bootstrap.md) — How a repository joins the workspace — repo-init scaffolds a fresh tree, adoption brings an existing one to green; the GitHub tail and roster enrollment complete both

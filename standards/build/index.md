# standards/build/ — index

The layered repo standard, one concern per document, listed in reading
order. Start at [Layers](/standards/build/layers.md).

- [Layers](/standards/build/layers.md) — The layered model — the base layer, inferred membership, what each layer adds, and the additions-are-free rule
- [File Skeleton](/standards/build/skeleton.md) — The per-layer file skeleton — required, optional, and forbidden entries, with worked example trees
- [The Python Project](/standards/build/python.md) — The root Python project — name mapping, the canonical pyproject.toml, scripts, entry points, and initial setup
- [The AWS Layer](/standards/build/aws.md) — The AWS layer — one CDK codebase under src/, per-Lambda dependency groups exported at synth time
- [Make](/standards/build/make.md) — The Make contract — the universal check target plus per-layer targets, identical recipes in every repo
- [Canonical Artifacts](/standards/build/canonical.md) — The canonical artifacts — the single-source files under standards/build/canonical/ and how each repo copy is compared
- [Distribution](/standards/build/distribution.md) — The distribution channel — the pre-commit hook repo, pinned revs, dogfooding, and the rev-bump release
- [Thin CI](/standards/build/ci.md) — Thin CI — the byte-identical workflow that runs exactly the hook suite on every push and PR
- [Enforcement](/standards/build/enforcement.md) — The enforcement map — the venues where checks fire and the tool that owns each rule

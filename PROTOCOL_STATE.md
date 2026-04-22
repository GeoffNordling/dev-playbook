# Protocol State — sdd-tools audit

Protocol: Align, Map, Execute
Started: 2026-04-22

## Objective — **approved**

Audit the tooling code and tests in `sdd-tools/` to build the user's
understanding of the current state, proceeding in three stages:
(a) understand, (b) judge, (c) fix. The agent describes current state;
the user judges. Fixes happen either inline when the user directs, or
accumulate in a backlog for post-workflow resolution.

## Scope — **approved**

**In scope:**
- `sdd-tools/src/sdd_tools/` (all modules, including `pytest_plugin`)
- `sdd-tools/tests/` (all tests)
- `sdd-tools/README.md`, `sdd-tools/pyproject.toml`, any `conftest.py` — as context

**Out of scope:**
- `tools/` (entirely — `tools/bin/` is simple scripts the user doesn't care about; `tools/src/devtools_lib/workspace.py` is 60 lines of glue with no tests and not worth auditing)
- `sdd-tools/lib/` (vendored JAR)
- `.venv`, `__pycache__`, build artifacts

**Src depth:** module- and function-level understanding. Implementation details only when a facet surfaces something.
**Test depth:** detailed — fixtures, conventions, what's covered, whether tests verify real behavior.

## Facets — **approved**

1. **Organization** — module boundaries, layering, file structure
2. **Functionality** — what each module/function is for and whether code delivers that
3. **Duplication** — same logic or functionality implemented more than once
4. **Dependencies** — external (JAR, libraries) and internal (module-to-module)
5. **Test structure** — fixtures, conventions, what's tested, mock data vs. real specs
6. **Test value** — do tests verify real behavior or fake green?

Facets 1–4 live in the "code" bucket (module/function-level understanding).
Facets 5–6 live in the "test" bucket (detailed).
User noted facets may not fit neatly — expected to adjust as we go.

## References — **approved**

Read in full:
- `~/workspace/dev-playbook/CLAUDE.md`
- `~/workspace/dev-playbook/README.md`
- `~/workspace/dev-playbook/standards/repo-documentation.md`
- `~/workspace/dev-playbook/standards/development-workflow.md`
- `~/workspace/dev-playbook/sdd-standards/README.md`
- `~/workspace/dev-playbook/sdd-standards/overview.md`
- `~/workspace/dev-playbook/sdd-standards/writing.md`
- `~/workspace/dev-playbook/sdd-standards/design-layer.md`
- `~/workspace/dev-playbook/sdd-standards/tooling.md`
- `~/workspace/dev-playbook/sdd-tools/README.md` (and any other top-level markdown in `sdd-tools/`)
- `~/workspace/dev-playbook/docs/adr/004-observable-to-tests-design-scope.md`
- `~/workspace/dev-playbook/docs/adr/005-design-dimensions-and-verification-fields.md`

## Shared Alignment — **approved**

### Description

Enumerable report for every facet: items sorted by classification, then by
source location. Each item names a specific thing, cites where, states what
I observe. Try this shape across all six facets; may revise per-facet if it
fits poorly.

1. **Organization** — module/package tree compactly rendered, short layering
   statement, grouping rationale I infer. Flag files with no clear home,
   oversized modules, shallow wrappers.
2. **Functionality** — for each module/public function in scope: one-line
   purpose and an observation of whether the code delivers it. Flag mismatches
   (purpose-unclear, code-does-more, code-does-less, "can't tell").
3. **Duplication** — enumerated instances of the same logic/functionality in
   more than one place. Per item: locations (≥2), what's duplicated, and
   whether it looks true-duplicate or parallel-but-intentionally-different.
4. **Dependencies** — (a) external deps with purpose; (b) internal
   module-to-module edges. Flag circular deps, heavy chains, deps that look
   undermotivated.
5. **Test structure** — inventory: test files, fixtures (location, scope,
   what they produce), naming conventions, coverage granularity,
   mock/synthetic vs. real spec data.
6. **Test value** — per test, one line: does it verify real behavior, or is
   it fake-green? Flag fake-green and "can't tell without running" as their
   own items.

Counts where they help. Anchors use `path:line` or `module.symbol`.

### Quality

- **Complete within scope.** No silent skipping. When a facet has no finding
  for a region, say so.
- **Anchored.** Every assertion cites `path:line` or a fully-qualified symbol.
- **Compressed.** A few lines per item.
- **Neutral.** Describe; don't pre-grade. The user judges.
- **Uncertainty-honest.** "Can't tell" is a first-class finding.
- **Redundancy-aware.** Cross-reference when the same finding spans facets;
  don't re-state.

## Map — pending
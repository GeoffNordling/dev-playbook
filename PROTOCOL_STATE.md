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

Each Phase 3 pass produces an enumerable report over the selected work:
items sorted by classification, then by source location. Each item names a
specific thing, cites where, states what I observe. This shape applies
across all six facets; may revise per-facet if it fits poorly.

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

## Map — **approved**

Rows are topic-based regions: each unites a module (or module group) with its
tests so all six facets apply. Facets 1–4 look at production code; facets 5–6
look at the region's tests. `—` marks a facet that does not apply (e.g. a
region with no tests).

Cells are t-shirt sizings of the work to investigate each region along each
facet: `S`, `M`, `L`, `XL`. Descriptive analysis happens in Phase 3.

### Regions

| # | Region | Files |
|---|---|---|
| 1 | Package glue | `src/sdd_tools/__init__.py`, `pyproject.toml`, `Makefile`, `conftest.py`, `README.md` |
| 2 | Config | `config.py`, `tests/test_config.py` |
| 3 | Data models | `models.py`, `tests/test_models.py` |
| 4 | Markdown parser | `parse/markdown.py`, `parse/__init__.py`, `tests/test_parse_markdown.py` |
| 5 | OFT JAR wrapper | `oft.py`, `tests/test_oft.py` |
| 6 | Lint suite | `lint.py`, `lint_id.py`, `lint_obligations.py`, `lint_syntax.py`, `lint_dimensions.py`, `lint_verification.py`, `tests/test_lint.py`, `tests/test_lint_dimensions.py`, `tests/test_lint_verification.py` |
| 7 | Interface validator | `interface.py`, `tests/test_interface.py`, `tests/iface_fixture.py` |
| 8 | Pytest markers | `markers.py`, `tests/test_markers.py` |
| 9 | Shared helpers | `chains.py`, `filtering.py`, `formatter.py`, `tests/test_chains.py`, `tests/test_filtering.py`, `tests/test_formatter.py` |
| 10 | Pytest plugin | `pytest_plugin.py`, `tests/test_pytest_plugin.py` |
| 11 | CLI suite | `cli/chain.py`, `cli/index.py`, `cli/atlas.py`, `cli/review.py`, `tests/test_cli_chain.py`, `tests/test_cli_index.py`, `tests/test_cli_atlas.py`, `tests/test_cli_review.py` |

### Matrix

| # | Region              | Organization | Functionality | Duplication | Dependencies | Test structure | Test value |
|---|---------------------|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Package glue        | S   | S   | —   | S   | —   | —   |
| 2 | Config              | S   | S   | S   | S   | S   | S   |
| 3 | Data models         | S   | M   | S   | S   | S   | S   |
| 4 | Markdown parser     | S   | L   | M   | S   | L   | L   |
| 5 | OFT JAR wrapper     | S   | M   | S   | S   | M   | M   |
| 6 | Lint suite          | M   | L   | L   | M   | L   | L   |
| 7 | Interface validator | S   | L   | S   | S   | M   | M   |
| 8 | Pytest markers      | S   | S   | S   | S   | M   | M   |
| 9 | Shared helpers      | M   | M   | M   | S   | M   | M   |
| 10| Pytest plugin       | S   | M   | M   | M   | M   | M   |
| 11| CLI suite           | M   | L   | L   | M   | L   | L   |

### Sizing rationale

- **Small single-file modules** (Config, Data models, Markers) size `S` on most
  facets. Their surface is narrow enough to read and judge in one pass.
- **Pure-Python parser** (`parse/markdown.py`, 363 lines) is the single largest
  module; functionality and tests each rate `L`.
- **Interface validator** (238 lines of introspection logic against real
  fixture symbols) rates `L` on functionality, `M` on tests.
- **Lint suite** spans six source modules and three test modules (~470 + ~460
  lines) with many rules; functionality, duplication (overlap between
  rule modules and the parser's section model), and tests all rate `L`.
- **CLI suite** has four CLIs sharing config-load / root-detection /
  dimension-grouping patterns; functionality, duplication, and tests rate `L`.
- **Pytest plugin** (196 lines) is the integration seam — synthesizes
  pytest items, composes lint + coverage + interface; `M` across the board.
- Facets 5–6 are `—` for Package glue (no tests).

### Traversal

Row-by-row (region-by-region): one region at a time, all six facets together
in a single pass.

## Region Progress

| # | Region | Status |
|---|---|---|
| 1 | Package glue | complete |
| 2 | Config | not started |
| 3 | Data models | not started |
| 4 | Markdown parser | not started |
| 5 | OFT JAR wrapper | not started |
| 6 | Lint suite | not started |
| 7 | Interface validator | not started |
| 8 | Pytest markers | not started |
| 9 | Shared helpers | not started |
| 10 | Pytest plugin | not started |
| 11 | CLI suite | not started |

## Displaced Content

_(Findings surfaced in one region's pass that belong to a later region. None yet.)_

## Intent Calibration Log

### General

- **Matrix shape is not up for re-litigation.** The rows unify code + tests
  because facets 5–6 are the test columns; proposing a code/test row split
  was a misread. Future passes should treat the shape as settled.
- **Traversal: row-by-row.** One region, all six facets together, in a
  single report the user can review before moving on.
- **Surface new findings distinctly — don't bury them in fix-writeups.**
  When a fix creates a new observation (e.g., a redundancy left behind),
  treat it as a fresh numbered item and get explicit direction, rather
  than folding it as a "minor follow-up" line. The user needs to see each
  finding clearly enumerated, not smuggled in via prose.
- **Consistency principle for tooling entry points.** User rejects
  asymmetry like "three of four dev-loop checks scripted in Makefile,
  one not." Apply symmetry: if `format` / `lint` / `typecheck` are
  targets, so is `test`. Generalize: flag and default-fix cases where
  a tooling surface covers N-1 of N equivalent operations.

### Organization

- **`__init__.py` files SHALL be blank.** User rejected docstrings in all three
  `__init__.py` files (`src/sdd_tools/__init__.py`, `cli/__init__.py`,
  `parse/__init__.py`) and directed blanking. Reason: docstrings in package
  `__init__.py` are useless commentary. **How to apply:** in every subsequent
  region, flag any non-blank `__init__.py` as an anomaly and default to
  blanking unless it carries actual exports / `__all__`.

### Functionality
_(empty)_

### Duplication
_(empty)_

### Dependencies
_(empty)_

### Test structure
_(empty)_

### Test value
_(empty)_

## Scratchpad

_(user's notes — agent writes only on user request)_

# Tools Refactor Plan

**Temporary planning document.** Captures the state of `sdd-tools/` and the two open GitHub issues so that a fresh session can pick up the refactor conversation without re-deriving context. Delete or archive after the refactor lands.

The authority for this work is the principles at the top of `sdd-tools/README.md` (frontier-invariance; deterministic validation; deterministic compression). GitHub issues #10 and #11 are input, not law — they pre-date the current framing and may not survive it intact.

## 1. Current state of `sdd-tools/`

### Layout

```
sdd-tools/
├── src/
│   ├── pytest_sdd/       pytest plugin
│   └── sdd_chain_text/   CLI
├── tests/
│   ├── pytest_sdd/
│   └── sdd_chain_text/
├── lib/openfasttrace-4.2.2.jar   (gitignored)
├── pyproject.toml
├── Makefile
└── conftest.py           (enables pytester for tests)
```

### `src/pytest_sdd/` modules

| Module | Role |
|---|---|
| `plugin.py` | pytest entry point; `pytest_collection_modifyitems` hook that walks spec dirs and synthesizes collectors |
| `collector.py` | virtual pytest collectors: `SpecFile` (one per `.md`), `SpecLintItem` (structural lint per file), `SpecTraceItem` (single item; runs OFT JAR across the whole tree) |
| `config.py` | reads `[tool.pytest-sdd]` from the project's `pyproject.toml`: `spec_dirs`, `oft_jar` |
| `parser.py` | regex-based markdown parser that returns `SpecItem` dataclasses. Used today only by lint, not by the coverage path |
| `models.py` | `SpecItem` dataclass plus regex constants (`SPEC_ID_RE`, `STATUS_RE`, `NEEDS_RE`, `COVERS_RE`, `H3_RE`, `HRULE_RE`) |
| `lint.py` | structural checks: ID format, Status field, Covers syntax, Needs values, bare/mixed obligation keywords, fenced code blocks |
| `markers.py` | scans pytest test items for `@pytest.mark.req("...")` / `dsn` / `utest` markers; synthesizes an in-memory OFT markdown file of `utest~` items that `Covers:` each marked spec ID |
| `trace.py` | subprocess wrapper around `java -jar <oft.jar> trace <spec-dirs>`; also hosts `resolve_oft_jar()` and `require_java()` |

### `src/sdd_chain_text/` modules

| Module | Role |
|---|---|
| `cli.py` | argparse entry; filters `--id`, `--type`, `--file`, `--feature`, `--root`. No `--view` concept today |
| `oft_xml.py` | shells out to `java -jar <oft.jar> convert -s <spec-dirs>`; parses the resulting XML into `SpecItem` list. Imports `pytest_sdd.trace` for JAR resolution (cross-package import within `sdd-tools/src`) |
| `chains.py` | builds coverage chains from OFT's `providescoverage` XML |
| `filtering.py` | applies CLI filters to chains |
| `formatter.py` | renders a chain as text with full body at each layer |

### External dependencies and seams

- Both tools depend on the OFT JAR at `sdd-tools/lib/openfasttrace-4.2.2.jar`.
- All OFT parsing is delegated to the JAR; the in-Python regex parser is used only for lint.
- `sdd_chain_text.oft_xml` → `pytest_sdd.trace` is the only cross-package import.
- pytest plugin hosts validation at pytest collection time.
- Ruff `SLF001` is enabled in `sdd-tools/pyproject.toml` and catches private access in *this repo's* source. It does not apply to downstream projects' test files.

## 2. What the two issues suggest

Treated as input, not as specification. Both reference ADR-004 (observable-to-tests design scope; machine-validated interfaces).

### Issue #10 — pytest-sdd: modular refactor for Interface: validation

Proposes breaking pytest-sdd into six components:

1. OFT parser extracted into a first-class module
2. Coverage graph as a component
3. `Interface:` parser — regex-extract `Interface:` lines from `dsn` items
4. Introspection validator — import each declared symbol, render live signature via `inspect.signature()` + `typing.get_type_hints()`, compare as strings for strict equality
5. Test-privacy AST check — flag non-dunder leading-underscore access in test files (complement to ruff `SLF001`)
6. Consolidated reporting across coverage, interface, privacy tracks

Acceptance notes: modular structure; all three validators run under `pytest -m spec`; toggleable; human sign-off before merge.

### Issue #11 — sdd-chain-text: add --view=structure

Proposes a new CLI mode:

- `sdd-chain-text --view=structure` walks `dsn` items, extracts `Interface:` entries, prints a module → class → method tree
- Derived on demand; no cache, no maintained artifact
- Works with split design specs
- Referenced as a sibling to pre-existing `--view=coverage` and `--view=trace` modes — those do not exist today, so `--view` itself is new

### Cross-cutting

- Both issues need an `Interface:` parser. Neither tool parses `Interface:` today.
- No `Interface:` line exists in any spec file yet; the keyword is documented in `sdd-standards/writing.md` but unused.
- ADR-004 is the driving decision.

## 3. How we'll approach the refactor

**The principles decide the structure, not the issues.** A clean sdd-tools serves two purposes: deterministic validation of SDD artifacts, and deterministic compression of conformant SDD artifacts. Every module should map cleanly to one of those, plus any primitives shared across them (spec parsing, Interface: parsing, code introspection).

The next conversation answers:

- Is the current layout (pytest plugin + separate CLI, both tied to OFT JAR) the right substrate, or is there a reorganization that maps more cleanly onto the two principles?
- Where do shared primitives live? The `Interface:` parser, in particular, is needed by both a validator (issue #10) and a compressor (issue #11).
- Do all validators belong behind the pytest plugin, or is that an accident of history? Would some validators work as standalone CLIs consumed by pre-commit hooks, equally well?
- What gets promoted from "happens to be a module" to "first-class seam we name and document"? Today, OFT parsing, coverage tracing, and marker bridging all exist but aren't named as components.
- Which of issue #10's six components are genuine separations and which are just the existing code reshuffled?

Open questions to resolve during that conversation:

1. Should there be a third shared-primitives package alongside `pytest_sdd` and `sdd_chain_text`, or are the primitives better hosted inside one of the existing packages and imported across?
2. "Coverage graph" — does this need an in-process Python representation, or does the OFT JAR call remain authoritative with a named Python seam wrapping it?
3. Missing-symbol behavior for the introspection validator (red phase may declare an `Interface:` whose stub doesn't exist yet).
4. Test-privacy scope — intra-file leading-underscore helpers vs cross-module `_private` access. ADR-004 line 45 gives the rule; confirm the AST check respects it.
5. `--view` as a dispatch mechanism — is `structure` the only view we'll add, or should we design the dispatcher for future views (coverage, trace, something else) from the start?
6. Human sign-off (issue #10 requirement) — formal gate, or "review carefully before merging" reminder?

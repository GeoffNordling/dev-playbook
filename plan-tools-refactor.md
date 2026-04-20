# Tools Refactor Plan

**Temporary planning document.** Captures the current state of `sdd-tools/` and the refactor decisions from the alignment conversation, so that a fresh session can pick up the work without re-deriving context. Delete or archive after the refactor lands.

The authority for this work is the principles at the top of `sdd-tools/README.md` (frontier-invariance; deterministic validation; deterministic compression). GitHub issues #10 and #11 have been consolidated into this plan and closed.

## Why this refactor

Two forces motivate it.

**The current layout doesn't match the purpose.** `sdd-tools/README.md` names the two enduring roles the package serves: deterministic validation of SDD artifacts, and deterministic compression of conformant artifacts. The code today is organized by invocation surface (pytest plugin vs. standalone CLI) rather than by these purposes. That mismatch has produced two `SpecItem` classes with the same name and different fields, a cross-package import for JAR resolution, and a regex parser used only for lint while a second parser handles the coverage path.

**ADR-004 introduced new validators that have no clean home.** Interface signature validation requires a new `Interface:` parser that neither current package provides; test-privacy is a new AST check with no existing analog in the codebase. Bolting them onto the existing structure would deepen the organizational accident.

The refactor reorganizes around the two principles so that each capability has one home, each data type has one definition, and a single output contract makes agent invocation uniform across every tool. Delivery surfaces (pytest plugin, per-view CLIs) become thin adapters over shared logic.

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
| `oft_xml.py` | shells out to `java -jar <oft.jar> convert -s <spec-dirs>`; parses the resulting XML into `SpecItem` list. Defines its own `SpecItem` class, distinct from `pytest_sdd.models.SpecItem` (different fields). Imports `pytest_sdd.trace` for JAR resolution (cross-package import within `sdd-tools/src`) |
| `chains.py` | builds coverage chains from OFT's `providescoverage` XML |
| `filtering.py` | applies CLI filters to chains |
| `formatter.py` | renders a chain as text with full body at each layer |

### External dependencies and seams

- Both tools depend on the OFT JAR at `sdd-tools/lib/openfasttrace-4.2.2.jar`.
- All OFT parsing is delegated to the JAR; the in-Python regex parser is used only for lint.
- `sdd_chain_text.oft_xml` → `pytest_sdd.trace` is the only cross-package import.
- Two `SpecItem` classes exist with different field names (`item_type`/`revision`/`body` vs. `doctype`/`version`/`description`/`rationale`). Accidental duplication.
- pytest plugin hosts validation at pytest collection time.
- Ruff `SLF001` is enabled in `sdd-tools/pyproject.toml` and catches private access in *this repo's* source. It does not apply to downstream projects' test files.

## 2. Decisions

### Package topology

Collapse `pytest_sdd` and `sdd_chain_text` into a single `sdd_tools` package. Delivery surfaces (pytest plugin, per-view CLIs) are declared as entry points in `pyproject.toml` and import from shared modules. No cross-package imports, no parallel packages.

```
[project.scripts]
sdd-chain = "sdd_tools.cli.chain:main"

[project.entry-points."pytest11"]
pytest-sdd = "sdd_tools.pytest_plugin"
```

### Backward compatibility

Downstream repos (currently 19) depend on `pytest-sdd` via dev-dep install, run `pytest -m spec` in pre-commit, and configure via `[tool.pytest-sdd]` in their `pyproject.toml`. Three surfaces stay stable through the refactor:

- **Dist name** `pytest-sdd` in `[project.name]`. Internal Python package is `sdd_tools`; a thin `pytest_sdd` namespace re-exports from `sdd_tools` for any downstream direct imports.
- **Pytest marker** `spec` — the pre-commit entry point (`pytest -m spec`) is the stable contract. New validators register themselves as pytest items tagged `spec` and are picked up automatically when a downstream repo bumps its `pytest-sdd` pin.
- **Config section** `[tool.pytest-sdd]` with keys `spec_dirs`, `oft_jar`. No rename.

New validators introduced by this refactor (Interface, test-privacy) may produce failures on pre-existing code in downstream repos. That is expected — each downstream fixes its own issues when it bumps the pin. The refactor does not attempt to make them pass silently.

### SpecItem

One typed dataclass, designed fresh. Fields chosen to serve the new consumers (Interface validator, chain renderer, filters). Produced by a single JAR-backed ingestion call that parses the `convert` XML output. Both existing `SpecItem` classes retire.

Minimum shape:

```
SpecItem:
  id             str    "dsn~parser.session~1"
  doctype        str    "req", "dsn", "feat", "utest", "itest"
  name           str
  revision       int
  covers         list[str]
  needs          list[str]
  description    str
  rationale      str
  source_file    Path
  source_line    int
  interfaces     list[str]   parsed from description; empty for non-dsn
```

Additional fields (title, status, comment, tags) added only if a consumer needs them.

### Lint

Operates over raw markdown files directly. No `SpecItem` dependency, no JAR. Checks: fenced code blocks, bare/mixed obligation keywords, ID format, required fields, `Covers:` syntax, `Needs:` values.

### JAR strategy

Depend on the JAR freely; it is already available in every repo that uses these tools. Do not rewrite functionality the JAR provides: tolerant markdown parsing, coverage graph, recursive directory scan, XML export. Simplicity wins.

### Output contract — `Finding`

Introduce a new shared dataclass produced by every validator. Replaces the current `list[str]` pattern in `lint.py` and unifies output across all validators:

```
Finding:
  rule       str     "interface.mismatch", "interface.missing-symbol", "lint.fenced-code", "privacy.cross-module", ...
  file       Path    relative to project root
  line       int     best-available anchor line
  line_kind  str | None    labels what `line` points to when it is not the exact problem line (e.g., "dsn header" for Interface findings that anchor to the dsn's ID line because the validator does not re-parse the item body to locate the exact `Interface:` line)
  spec_id    str | None
  message    str     one line
  detail     str | None    multi-line block (e.g., committed vs. actual signature)
  fix        str | None    one-line guidance for the agent
```

Text rendering — when `line_kind` is set, the renderer annotates the anchor so the line number isn't presented with false precision:

```
specs/feature.md:42 (dsn header)  interface.mismatch  Signature differs for parser.parse_session
  committed: parser.parse_session(path: pathlib.Path) -> parser.Session
  actual:    parser.parse_session(path: str) -> parser.Session
  fix:       update Interface: or update the code to match
```

Zero noise on success — a single `OK <validator>` line at most.

### Exit codes (standalone CLIs)

| Code | Meaning |
|---|---|
| 0 | Success — checks passed or view rendered (empty output counts as success) |
| 1 | Validator reported findings (validators only; views do not use this code) |
| 2 | Tool-level error — JAR missing, Java missing, unreadable config, subprocess crash |

pytest-hosted validators inherit pytest's native exit scheme (0 pass, 1 failures, 2 interrupted, 3 internal, 4 usage, 5 no tests collected). Not ours to redesign; pre-commit only cares about nonzero-means-fail.

### Hosting

- **pytest plugin** hosts all validators: lint, coverage, Interface, test-privacy, marker harvest. Ingestion runs once at collection time; items flow to each validator; one pytest item per validator whose failure message renders the `Finding` list.
- **Per-view binaries** host compressors: `sdd-chain` today. Each is a thin `main()` in its own module; all logic lives in shared `sdd_tools` modules. Additional views (e.g., a deferred structure view) ship as additional binaries in the same package when needed.
- **`sdd-check` (non-pytest validator CLI) is deferred.** Only built if a use case surfaces — agents can already invoke pytest with filter flags for ad-hoc checks.

### Validator semantics

- **Lint** — structural markdown checks. No JAR. Findings emitted per file per rule.
- **Coverage** — single pytest item runs JAR `trace`; pass/fail is the JAR's exit code; JAR's own report is the assertion message on failure. Coverage does not emit `Finding` objects; translating the JAR report would add work with no structured consumer (one implementation, no fan-out). Marker harvest feeds synthetic utest markdown into the trace pass.
- **Interface** — parse `Interface:` lines from dsn items, import the named symbol, introspect via `inspect.signature()` + `typing.get_type_hints()`, render annotations in modern form, compare as strings. **Hard-fail on missing symbol *or* signature mismatch.** Per ADR-004, the design agent writes dsn items and interface stubs together, so stubs exist when a dsn lands; a missing symbol indicates either a workflow violation or subsequent code removal without dsn update.
- **Test-privacy** — AST walk per ADR-004 line 45. Intra-file `_helper` names pass; imports or attribute accesses reaching into `_private` names of non-test modules fail.
- **Marker harvest** — scan pytest items for `@pytest.mark.<type>("...")` markers; synthesize in-memory OFT markdown of `utest~` items; hand to the JAR trace alongside real specs. Unchanged in principle from the current implementation.

## 3. Next steps

Create `src/sdd_tools/` with the modules described in section 2; retire `src/pytest_sdd/` and `src/sdd_chain_text/` as the new modules replace them; port tests as each module lands. Write the code directly — no SDD bootstrap layer for this package.

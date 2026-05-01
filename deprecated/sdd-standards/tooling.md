# Spec Tooling

Tools ship from the `pytest-sdd` package in dev-playbook: a pytest plugin (`pytest-sdd`) and four standalone CLIs (`sdd-chain`, `sdd-review`, `sdd-index`, `sdd-atlas`). All read the same `[tool.pytest-sdd]` configuration.

## Installation

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=sdd-tools"
```

## Configuration

In `pyproject.toml`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements", "specs/design"]
oft_jar = "../dev-playbook/sdd-tools/lib/openfasttrace-4.2.2.jar"
```

Both fields are required. `spec_dirs` lists the directories containing OFT markdown files; `oft_jar` is the path to the OpenFastTrace JAR (v4.2.2), relative to the project root.

The JAR is vendored once in dev-playbook at `sdd-tools/lib/openfasttrace-4.2.2.jar` (gitignored). All workspace projects reference it via the relative path `../dev-playbook/sdd-tools/lib/openfasttrace-4.2.2.jar`. This assumes the standard workspace layout where all repos live under `~/workspace/`. If the JAR is not present, download it from https://github.com/itsallcode/openfasttrace/releases/tag/4.2.2 and place it at that path.

Projects that only have functional requirements and no design layer omit `specs/design` from `spec_dirs`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements"]
oft_jar = "../dev-playbook/sdd-tools/lib/openfasttrace-4.2.2.jar"
```

**OFT JAR requirement.** Java must be on `PATH`. The JAR file must exist at the configured path. Neither is optional — a missing JAR or missing Java is a hard failure for `spec-coverage`, `spec-interface`, and `sdd-chain`.

## pytest-sdd

`pytest-sdd` is a pytest plugin that hosts every SDD validator as part of the normal test suite. Each validator runs as a single pytest item tagged with the `spec` marker:

- **`spec-lint`** — structural validation of every `.md` spec file: ID format, Status field, obligation keyword backticking, mixed obligation levels, `Covers:` syntax, `Needs:` values, fenced code blocks, `AgentReview:` well-formedness, `Dimension:` presence and well-formedness on every `dsn`, and verification-field presence on every `dsn`.
- **`spec-coverage`** — full OFT traceability check, delegating to the OpenFastTrace JAR to verify that every `Needs:` declaration is satisfied and every `Covers:` reference resolves. Test coverage is derived from `@pytest.mark.req` / `@pytest.mark.dsn` markers on the tests pytest collected for this run, so scoped runs (`pytest path/to/file.py`, `-k` filters) produce a partial picture — requirements covered only by uncollected tests surface as `-utest`. Run `pytest` with no scope arguments to evaluate full coverage.
- **`spec-interface`** — for every `dsn` item that declares an `Interface:`, imports the named symbol and verifies the actual signature matches the committed one. Hard-fails on missing symbol or signature mismatch.

Each validator emits structured `Finding` blocks; the failure message renders them in a uniform format.

**Invocation:**

```bash
pytest -m spec                       # all SDD validators
pytest -m spec -k lint               # lint only
pytest -m spec -k coverage           # coverage only
pytest -m spec -k interface          # interface signatures only
pytest -m "not spec"                 # skip every SDD validator
```

Validators run automatically when `pytest` is invoked without `-m` flags, alongside the project's normal test suite. The `spec` marker allows selective execution.

## sdd-chain

`sdd-chain` is a standalone CLI that displays full spec traceability chains with verbatim body text. It runs the OFT JAR's `convert` command to extract all spec items as structured XML, enumerates coverage chains (feat → req → dsn), and prints each chain with the full text of every item at every layer.

The tool answers the question "is the content at each layer appropriate?" — features describe capabilities, functional requirements describe behavior, design items name interfaces and make structural decisions. Each chain is self-contained: shared upstream items repeat so that every chain can be read independently.

Test layers (utest, itest) are excluded from output. Coverage validation is out of scope — that is what `pytest -m spec -k coverage` does.

**Invocation:**

```bash
sdd-chain                       # dump all chains
sdd-chain --id '*auth*'         # chains containing an item matching this glob
sdd-chain --type dsn            # chains containing an item of this type
sdd-chain --file registry       # chains with items from files matching this substring
sdd-chain --feature '*user*'    # chains rooted at a feat item matching this glob
sdd-chain --root /path/to/proj  # explicit project root (default: auto-detect from cwd)
```

## sdd-review

`sdd-review` is a standalone CLI that scans every `dsn` spec item for `AgentReview:` fields and emits structured records — spec ID, source location, prose body — for consumption by the `sdd-review` skill. The skill reads those records and dispatches a review agent per item, reporting items that are stale or out-of-sync with the code.

`sdd-review` is reporting, not validation: it emits facts, does not gate a pytest run, and has no pass/fail. Well-formedness of `AgentReview:` fields is checked at pytest collection time by `spec-lint`.

## sdd-index

`sdd-index` is a standalone CLI that emits a one-line catalog of every `dsn` item in the project — id, title, and source location — keyed by the four design dimensions. The output is the full inventory of design commitments at a glance, without any body text.

Output is markdown, grouped under the four dimension headers (`## Data`, `## API Shape`, `## Algorithms`, `## Composition`). Each group lists items whose `Dimension:` field names that dimension, in file order. An item with multiple dimensions appears under each group it names. Dimensions named by no item render as an empty header — the tool's signal, not a requirement of the source files.

`sdd-index` is the cheapest compression view — useful as a first pass for humans scanning the project's design surface, and as input to agent prompts that need to reason about the dsn inventory without reading every body.

**Invocation:**

```bash
sdd-index                       # dump the whole project
sdd-index --root /path/to/proj  # explicit project root (default: auto-detect from cwd)
```

## sdd-atlas

`sdd-atlas` is a standalone CLI that emits the full body of every `dsn` item in the project, keyed by dimension. It applies the same dimension-scoped filter as `sdd-index` but retains each item's body, including all keyword fields (`Status:`, `Dimension:`, `Covers:`, `Needs:`, `Interface:`, `AgentReview:`, `Rationale:`, `Comment:`).

Output is markdown, grouped under the four dimension headers. Items within each group render in file order; an item whose `Dimension:` field names multiple dimensions appears under each group it names.

`sdd-atlas` is for cases where the catalog-level view from `sdd-index` is insufficient and the reader needs the full text. Both humans and agents use it as input to ad-hoc prompted summarization until richer projections (schema extraction, cross-dimension linking, gap analysis) prove their worth through dogfooding.

**Invocation:**

```bash
sdd-atlas                       # dump the whole project
sdd-atlas --root /path/to/proj  # explicit project root (default: auto-detect from cwd)
```

## Rule-to-tool crosswalk

Mapping from standard rule to the tool that enforces it.

| Standard | Rule | Enforced by |
|---|---|---|
| [rfc2119.md — Backticking](rfc2119.md#backticking--constraint) | Backticked obligation keywords | `spec-lint` |
| [rfc2119.md — One obligation level](rfc2119.md#one-obligation-level-per-item--constraint) | One obligation level per item | `spec-lint` |
| [oft.md — Fenced code blocks](oft.md#fenced-code-blocks--constraint-forbidden) | Fenced code blocks forbidden | `spec-lint` |
| [ears.md](ears.md) | EARS sentence form | — |
| [spec-format.md — Illustrative examples](spec-format.md#illustrative-examples-in-prose) | Illustrative examples (`SHOULD`) | — |
| [oft.md — Specification item ID](oft.md#specification-item-id) | Well-formed `type~name~revision` IDs | `spec-lint` |
| [oft.md — Keyword fields](oft.md#keyword-fields) | `Status:` field present + valid | `spec-lint` |
| [oft.md — Keyword fields](oft.md#keyword-fields) | `Covers:` syntactic form | `spec-lint` |
| [oft.md — Artifact types subset](oft.md#artifact-types--subset) | `Needs:` known artifact types | `spec-lint` |
| [oft.md — `Interface:`](oft.md#extension-keyword-interface) | `Interface:` parseable, resolves, matches code | `spec-interface` |
| [oft.md — `AgentReview:`](oft.md#extension-keyword-agentreview) | `AgentReview:` well-formed prose | `spec-lint` |
| [oft.md — Coverage checks](oft.md#coverage-checks) | `Needs:` coverage satisfied | `spec-coverage` |
| [oft.md — Coverage checks](oft.md#coverage-checks) | `Covers:` IDs resolve at revision | `spec-coverage` |
| [oft.md — Coverage checks](oft.md#coverage-checks) | No orphans | `spec-coverage` |
| [oft.md — Forwarding forbidden](oft.md#forwarding--constraint-forbidden) | Forwarding syntax forbidden | — |
| [oft.md — `Dimension:`](oft.md#extension-keyword-dimension) | Every `dsn` carries a `Dimension:` field naming one or more valid dimensions | `spec-lint` |
| [oft.md — Verification coverage](oft.md#verification-coverage--extension) | Every `dsn` carries at least one of `Needs:` / `Interface:` / `AgentReview:` | `spec-lint` |

Rules marked `—` are either agent-judgment territory (EARS form, illustrative examples) or gaps awaiting tool support.

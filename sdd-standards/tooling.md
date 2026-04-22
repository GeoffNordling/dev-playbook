# Spec Tooling

Tools ship from the `pytest-sdd` package in dev-playbook: a pytest plugin (`pytest-sdd`) and two standalone CLIs (`sdd-chain`, `sdd-review`). All three read the same `[tool.pytest-sdd]` configuration.

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

- **`spec-lint`** — structural validation of every `.md` spec file: ID format, Status field, obligation keyword backticking, mixed obligation levels, `Covers:` syntax, `Needs:` values, fenced code blocks, `AgentReview:` well-formedness, dimension section organization in `dsn` files, and verification-field presence on every `dsn`.
- **`spec-coverage`** — full OFT traceability check, delegating to the OpenFastTrace JAR to verify that every `Needs:` declaration is satisfied and every `Covers:` reference resolves.
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

## Rule-to-tool crosswalk

Mapping from standard rule to the tool that enforces it.

| Standard | Rule | Enforced by |
|---|---|---|
| [writing.md — Prose](writing.md#prose-rfc-2119-and-ears) | Backticked obligation keywords | `spec-lint` |
| [writing.md — Prose](writing.md#prose-rfc-2119-and-ears) | One obligation level per item | `spec-lint` |
| [writing.md — Prose](writing.md#prose-conventions) | Fenced code blocks forbidden | `spec-lint` |
| [writing.md — Prose](writing.md#sentence-templates) | EARS sentence form | — |
| [writing.md — Prose](writing.md#prose-conventions) | Illustrative examples (`SHOULD`) | — |
| [writing.md — Structure](writing.md#id-format) | Well-formed `type~name~revision` IDs | `spec-lint` |
| [writing.md — Structure](writing.md#item-structure) | Status field present + valid | `spec-lint` |
| [writing.md — Structure](writing.md#item-structure) | `Covers:` syntactic form | `spec-lint` |
| [writing.md — Structure](writing.md#item-structure) | `Needs:` known artifact types | `spec-lint` |
| [writing.md — Interface Declarations](writing.md#interface-declarations) | `Interface:` parseable, resolves, matches code | `spec-interface` |
| [writing.md — AgentReview Declarations](writing.md#agentreview-declarations) | `AgentReview:` well-formed prose | `spec-lint` |
| [overview.md — Coverage Chain](overview.md#coverage-chain) | `Needs:` coverage satisfied | `spec-coverage` |
| [overview.md — Coverage Chain](overview.md#coverage-chain) | `Covers:` IDs resolve at revision | `spec-coverage` |
| [overview.md — Coverage Chain](overview.md#coverage-chain) | No orphans | `spec-coverage` |
| [overview.md — Forwarding](overview.md#forwarding) | Forwarding syntax forbidden | — |
| [design-layer.md — Dimensions](design-layer.md#dimension-section-organization) | All four dimension headers present per `dsn` file | `spec-lint` |
| [design-layer.md — Dimensions](design-layer.md#dimension-section-organization) | Every `dsn` placed under a dimension header | `spec-lint` |
| [design-layer.md — Verification Fields](design-layer.md#verification-fields) | Every `dsn` carries at least one of `Needs:` / `Interface:` / `AgentReview:` | `spec-lint` |

Rules marked `—` are either agent-judgment territory (EARS form, illustrative examples) or gaps awaiting tool support.

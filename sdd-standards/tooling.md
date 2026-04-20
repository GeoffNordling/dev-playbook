# Spec Tooling

Two tools ship from the `pytest-sdd` package in dev-playbook: a pytest plugin (`pytest-sdd`) and a standalone CLI (`sdd-chain`). Both read the same `[tool.pytest-sdd]` configuration.

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

- **`spec-lint`** — structural validation of every `.md` spec file: ID format, Status field, bare obligation keywords, mixed obligation levels, Covers syntax, Needs values, fenced code blocks.
- **`spec-coverage`** — full OFT traceability check, delegating to the OpenFastTrace JAR to verify that every `Needs:` declaration is satisfied.
- **`spec-interface`** — for every dsn item that declares an `Interface:`, imports the named symbol and verifies the actual signature matches the committed one. Hard-fails on missing symbol or signature mismatch.
- **`spec-privacy`** — AST scan of every test file flagging non-dunder leading-underscore imports and attribute accesses that reach into non-test modules. Local underscore helpers in test files pass.

Each validator emits structured `Finding` blocks; the failure message renders them in a uniform format.

**Invocation:**

```bash
pytest -m spec                       # all SDD validators
pytest -m spec -k lint               # lint only
pytest -m spec -k coverage           # coverage only
pytest -m spec -k interface          # interface signatures only
pytest -m spec -k privacy            # test-privacy only
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

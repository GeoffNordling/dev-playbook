# Spec Tooling

## pytest-sdd

`pytest-sdd` is a pytest plugin that validates OFT spec files as part of the normal test suite. It provides two checks:

- **Lint** (`-m spec -k lint`): structural validation of every `.md` spec file — ID format, Status field, bare obligation keywords, mixed obligation levels, Covers syntax, Needs values.
- **Trace** (`-m spec -k trace`): full OFT traceability check, delegating to the OpenFastTrace JAR to verify that every `Needs:` declaration is satisfied.

**Installation:**

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=tools"
```

**Configuration** in `pyproject.toml`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements", "specs/design"]
oft_jar = "../dev-playbook/tools/lib/openfasttrace-4.2.2.jar"
```

Both fields are required. `spec_dirs` lists the directories containing OFT markdown files; `oft_jar` is the path to the OpenFastTrace JAR (v4.2.2), relative to the project root.

The JAR is vendored once in dev-playbook at `tools/lib/openfasttrace-4.2.2.jar` (gitignored). All workspace projects reference it via the relative path `../dev-playbook/tools/lib/openfasttrace-4.2.2.jar`. This assumes the standard workspace layout where all repos live under `~/workspace/`. If the JAR is not present, download it from https://github.com/itsallcode/openfasttrace/releases/tag/4.2.2 and place it at that path.

Projects that only have functional requirements and no design layer omit `specs/design` from `spec_dirs`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements"]
oft_jar = "../dev-playbook/tools/lib/openfasttrace-4.2.2.jar"
```

**Invocation:**

```bash
pytest -m spec              # run all spec checks (lint + trace)
pytest -m spec -k lint      # lint only
pytest -m spec -k trace     # traceability only
pytest -m "not spec"        # skip spec checks
```

Spec checks run automatically when `pytest` is invoked without `-m` flags, interleaved with the normal test suite. The `spec` marker allows selective execution.

**OFT JAR requirement:** Java must be on `PATH`. The JAR file must exist at the configured path. Neither is optional — a missing JAR or missing Java is a hard test failure.

## sdd-chain-text

`sdd-chain-text` is a standalone CLI tool that displays full spec traceability chains with verbatim body text. It reads the same `[tool.pytest-sdd]` configuration as `pytest-sdd`, runs the OFT JAR's `convert` command to extract all spec items as structured XML, enumerates coverage chains (feat → req → dsn), and prints each chain with the full text of every item at every layer.

The tool answers the question "is the content at each layer appropriate?" — features describe capabilities, functional requirements describe behavior, design items name interfaces and make structural decisions. Each chain is self-contained: shared upstream items repeat so that every chain can be read independently.

Test layers (utest, itest) are excluded from output. Coverage validation is out of scope — that is what `pytest -m spec -k trace` does.

**Installation:**

`sdd-chain-text` is installed as a console script from the same `dev-playbook-tools` package as `pytest-sdd`:

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=tools"
```

**Invocation:**

```bash
sdd-chain-text                       # dump all chains
sdd-chain-text --id '*auth*'         # chains containing an item matching this glob
sdd-chain-text --type dsn            # chains containing an item of this type
sdd-chain-text --file registry       # chains with items from files matching this substring
sdd-chain-text --feature '*user*'    # chains rooted at a feat item matching this glob
sdd-chain-text --root /path/to/proj  # explicit project root (default: auto-detect from cwd)
```

**OFT JAR requirement:** Same as `pytest-sdd` — Java must be on `PATH` and the OFT JAR must exist at the configured path.

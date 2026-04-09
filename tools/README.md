# Tools

CLI utilities and shared libraries for workspace automation; lightweight, pragmatic glue across a multi-repo workspace.

> *"The perfect race car crosses the finish line in first place and then falls to pieces."*  
> — Ferdinand Porsche
>
> *"The purpose of a system is what it does."*  
> — Stafford Beer
>
> *"There is no prize to perfection, only an end to pursuit."*  
> — Viktor, *Arcane*

## What belongs here

- CLI tools that operate across multiple repos or automate workspace tasks
- Shared libraries consumed by those tools
- Spec-driven packages with their own test suites

## What does NOT belong here

- Project-specific scripts — put them in that project's repo
- Standards, agent configuration, or templates — those go in the repo root
- One-off shell aliases — put them in dotfiles

## Setup

```bash
cd tools && uv pip install -e .   # installs packages (sdd-trace, pytest-sdd)
```

Requires Python >= 3.11 and [uv](https://docs.astral.sh/uv/). Standalone scripts in `bin/` use PEP 723 inline metadata; `uv run` handles their dependencies automatically. Skills reference tools by absolute path; no PATH configuration needed.

## What's here

### Standalone scripts (`bin/`)

Each script is self-contained with a PEP 723 `# /// script` block. Skills reference them by absolute path.

| Tool | Location | Purpose |
|------|----------|---------|
| `py-outline` | `bin/py-outline` | Print class/function structure of a Python package (signatures + docstrings) |
| `repo-conformance` | `bin/repo-conformance` | Check workspace repos against the repo-documentation standard |
| `repo-sync` | `bin/repo-sync` | Sync all workspace repos with their remotes (auto-pull/push when safe) |

### Packages (`src/`)

Installed via `pyproject.toml` console entry points.

| Package | Location | Purpose |
|---------|----------|---------|
| `sdd-trace` | `src/sdd_trace/` | Legacy traceability CLI (pre-OFT); superseded by pytest-sdd for new projects |
| `pytest-sdd` | `src/pytest_sdd/` | pytest plugin for OFT spec validation: lint checks + traceability via OFT JAR |

### Shared library

| Library | Location | Purpose |
|---------|----------|---------|
| `devtools_lib` | `src/devtools_lib/` | Workspace discovery, git helpers; consumed by `repo-conformance`, `repo-sync` |

## Tool reference

Each tool supports `--help` for full usage, options, and exit codes.

### py-outline

Print the structure of a Python package; classes, functions, type-hinted signatures, and first-line docstrings via static analysis.

```bash
py-outline src/mypackage
py-outline src/mypackage > structure.txt
```

### repo-conformance

Check repos against the [repo-documentation standard](https://github.com/GeoffNordling/dev-playbook/blob/main/standards/repo-documentation.md). Scans for required files, misplaced files, and unknown root-level markdown.

```bash
repo-conformance /path/to/repo
repo-conformance --all
```

### repo-sync

Sync all Git repos in the workspace with their remotes. Auto-pulls when behind (clean, not ahead), auto-pushes when ahead (clean, not behind), errors on conflicts. Designed to keep two machines in sync.

```bash
repo-sync
repo-sync /path/to/workspace
```

**Exit codes:** 0 = all synced, 1 = some repos not fully synced.

### pytest-sdd

pytest plugin for validating OFT spec files as part of the normal test suite. Installed as a dev dependency in each project; configured in `pyproject.toml`. See [spec-format.md](../standards/spec-format.md#tooling-integration) for configuration and invocation.

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=tools"
```

```bash
pytest -m spec          # run all spec checks (lint + trace)
pytest -m spec -k lint  # lint only
pytest -m spec -k trace # traceability only
```

Requires Java on `PATH` and the OFT JAR at `../dev-playbook/tools/lib/openfasttrace-4.2.2.jar`.

### sdd-trace

Legacy traceability CLI for pre-OFT specs. Superseded by `pytest-sdd` for all new projects. Verify traceability across a linear pipeline: functional requirements → design → tests.

```bash
sdd-trace
sdd-trace --specs path/to/specs --tests path/to/tests
sdd-trace --detail ERR AQD
```

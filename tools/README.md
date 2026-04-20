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

- Simple CLI tools that automate workspace tasks across multiple repos
- Shared libraries consumed by those tools

## What does NOT belong here

- Spec-driven development tools — those go in [`sdd-tools/`](../sdd-tools/)
- Project-specific scripts — put them in that project's repo
- Anything with a dedicated home elsewhere in this repo (standards, agent config, templates, shell aliases)

## Setup

```bash
cd tools && uv sync
```

Requires Python >= 3.11 and [uv](https://docs.astral.sh/uv/). Standalone scripts in `bin/` use PEP 723 inline metadata; `uv run` handles their dependencies automatically. Skills reference tools by absolute path; no PATH configuration needed.

## What's here

### Standalone scripts (`bin/`)

Each script is self-contained with a PEP 723 `# /// script` block. Skills reference them by absolute path. Scripts fall into two categories.

#### Validation scripts

Run automatically on every commit via pre-commit hooks. Each validation script:

- Declares a `# /// pre-commit` metadata block (see below) with its hook config and the standard it enforces
- Asserts its governing standard exists at startup — fails immediately if the standard has moved or been renamed
- Exits 0 on success, 1 on failure, 2 on tool error
- Writes machine-readable findings to stdout (one line per finding)
- Writes a human-readable summary to stderr (one line)

| Tool | Standard | Purpose |
|------|----------|---------|
| `ref-check` | [repo-documentation.md](../standards/repo-documentation.md) | Broken cross-references in markdown |
| `skill-audit` | [skill-authoring.md](../standards/skill-authoring.md) | Skill front matter conformance |

##### `# /// pre-commit` metadata

Validation scripts embed pre-commit hook configuration as inline metadata, similar to PEP 723. The `generate-pre-commit` script reads these blocks to produce the generated section of `.pre-commit-config.yaml`.

```python
# /// pre-commit
# id = "skill-audit"
# entry = "python3 tools/bin/skill-audit"
# pass_filenames = false
# files = "dotfiles/\\.claude/skills/"
# standard = "standards/skill-authoring.md"
# ///
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Hook identifier (used in `.pre-commit-config.yaml`) |
| `entry` | Yes | Command to run |
| `pass_filenames` | Yes | Whether pre-commit passes changed filenames as arguments |
| `types` | No | File types that trigger the hook (e.g., `["markdown"]`) |
| `always_run` | No | If `true`, run on every commit regardless of which files changed |
| `files` | No | Regex pattern limiting which file paths trigger the hook |
| `standard` | Yes | Path (relative to repo root) to the standards document this script enforces |

After adding or modifying a `# /// pre-commit` block, run `python3 tools/bin/generate-pre-commit` to regenerate the hooks.

#### Utility scripts

Run ad hoc on user demand. Not part of the pre-commit pipeline.

| Tool | Purpose |
|------|---------|
| `py-outline` | Print class/function structure of a Python package (signatures + docstrings) |
| `repo-sync` | Sync all workspace repos with their remotes (auto-pull/push when safe) |
| `workspace-backup` | Archive every workspace repo (with `.git/`) into a single dated .zip |

### Shared library (`src/`)

| Library | Location | Purpose |
|---------|----------|---------|
| `devtools_lib` | `src/devtools_lib/` | Workspace discovery, git helpers; consumed by `repo-sync` |

## Tool reference

Each tool supports `--help` for full usage, options, and exit codes.

### py-outline

Print the structure of a Python package; classes, functions, type-hinted signatures, and first-line docstrings via static analysis.

```bash
py-outline src/mypackage
py-outline src/mypackage > structure.txt
```

### ref-check

Scan all markdown files for `~/workspace/` cross-references and report their status as JSON Lines to stdout. Designed for agent consumption. Enforces the cross-reference conventions in [repo-documentation.md](../standards/repo-documentation.md).

```bash
ref-check [directory]
```

Each line is a JSON object with `source`, `line`, `target`, and `status` (`ok`, `broken`, or `external`). Exit code 1 if any broken references.

### skill-audit

Audit all skill SKILL.md files for front matter conformance against [skill-authoring.md](../standards/skill-authoring.md).

```bash
skill-audit [directory]
```

One line per finding to stdout in `file:check: message` format. Exit code 1 if any issues found.

### generate-pre-commit

Scan `tools/bin/` for `# /// pre-commit` metadata blocks and regenerate the validation hooks section of `.pre-commit-config.yaml`. Run this after adding or changing a validation script.

```bash
generate-pre-commit [directory]
```

### repo-sync

Sync all Git repos in the workspace with their remotes. Auto-pulls when behind (clean, not ahead), auto-pushes when ahead (clean, not behind), errors on conflicts. Designed to keep two machines in sync.

```bash
repo-sync
repo-sync /path/to/workspace
```

**Exit codes:** 0 = all synced, 1 = some repos not fully synced.

### workspace-backup

Archive every Git repo in a workspace into a single dated `.zip`, preserving each repo's `.git/` directory so the archive can fully replace the workspace if GitHub is lost. Each repo becomes a top-level folder inside the archive.

```bash
workspace-backup                      # auto-detect workspace, write workspace-backup-YYYY-MM-DD.zip
workspace-backup /path/to/workspace   # explicit workspace
workspace-backup -o /tmp/snap.zip     # custom output path
workspace-backup --force              # overwrite existing output
```

Skips hidden directories, non-repo subfolders, and the entries in `devtools_lib.workspace.SKIP_DIRS`. Symlinks are not followed.

## Development

```bash
cd tools && uv sync          # setup
uv run pytest                # tests
make lint                    # ruff check
make format                  # ruff format
make typecheck               # mypy
```

Python >= 3.11; ruff for lint + format, mypy for type checking. Line length 88 (ruff default). Ruff rules: E, W, F, I, UP, B, SIM, SLF (E501 ignored). Standalone scripts in `bin/` use PEP 723 inline metadata — their dependencies do not go in `pyproject.toml`. Packages in `src/` ship via `pyproject.toml` console entry points. When adding a new tool, add it to the tables above.

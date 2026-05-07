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

- Spec-driven development tools — those go in [`~/workspace/spec-tools/`](~/workspace/spec-tools/)
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

- Exits 0 on success, 1 on failure, 2 on tool error
- Writes machine-readable findings to stdout (one line per finding)
- Writes a human-readable summary to stderr (one line)

| Tool | Standard | Purpose |
|------|----------|---------|
| `ref-check` | [repo-documentation.md](../standards/repo-documentation.md) | Broken cross-references in markdown |
| `internal-skill-audit` | [skill-conventions.md](../standards/skill-conventions.md) | Skill conformance (internal skills only; externally-managed skills are skipped) |
| `test-privacy` | [testing-conventions.md](../standards/testing-conventions.md) | Private-name access in test files |

Hook configuration lives in `.pre-commit-config.yaml` at the repo root and is the source of truth. To add a new validation script:

1. Write the script under `bin/`.
2. Add a `local` hook entry to `.pre-commit-config.yaml` with its `id`, `name`, `entry`, `language: system`, and the appropriate `pass_filenames` / `types` / `always_run` flags. Use the existing entries as a model.
3. If the hook scans specific paths, pass them in the `entry`. Update the YAML when those paths change.

#### Utility scripts

Run ad hoc on user demand. Not part of the pre-commit pipeline.

| Tool | Purpose |
|------|---------|
| `py-outline` | Print class/function structure of a Python package (signatures + docstrings) |
| `workspace-backup` | Archive every workspace repo (with `.git/`) into a single dated .zip |
| `worktree-sweep` | Prune `.claude/worktrees/` entries whose PR is merged with no local divergence; report ambiguous cases |

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

### internal-skill-audit

Audit internal skill bundles (real directories under `dotfiles/.claude/skills/`) for conformance against [skill-conventions.md](../standards/skill-conventions.md). Externally-managed skills — bundle directories that are symlinks, typically into `dotfiles/.agents/skills/` — are skipped, since their conformance is the upstream's concern.

```bash
internal-skill-audit [directory]
```

One line per finding to stdout in `file:check: message` format. Exit code 1 if any issues found.

### test-privacy

Flag private-name access in test files. Enforces the "Access only public names" rule from [testing-conventions.md](../standards/testing-conventions.md): tests `SHALL` exercise public identifiers only, reaching private helpers through the public interfaces that call them.

```bash
test-privacy                       # scans ./tests
test-privacy path/to/tests [...]   # scans one or more explicit directories
```

One line per finding to stdout in `file:line  rule  message` form. Exit code 0 if clean, 1 if any findings, 2 on tool error.

### workspace-backup

Archive every Git repo in a workspace into a single dated `.zip`, preserving each repo's `.git/` directory so the archive can fully replace the workspace if GitHub is lost. Each repo becomes a top-level folder inside the archive.

```bash
workspace-backup                      # auto-detect workspace, write workspace-backup-YYYY-MM-DD.zip
workspace-backup /path/to/workspace   # explicit workspace
workspace-backup -o /tmp/snap.zip     # custom output path
workspace-backup --force              # overwrite existing output
```

Skips hidden directories and non-repo subfolders. Symlinks are not followed.

### worktree-sweep

Walk `.claude/worktrees/` in the current repo and prune worktrees whose most-recent PR is merged with no local divergence. Anything else is reported for human triage. Implements the cleanup step of [issue-implementation.md](../standards/issue-implementation.md).

```bash
worktree-sweep            # apply prunes, report the rest
worktree-sweep --dry-run  # report only
```

Auto-prune requires all three: PR state `MERGED`, local tip SHA matches the PR's `headRefOid`, and `git status --porcelain` is empty. Ambiguous categories: PR open (in-progress, skipped), PR closed without merge (rejected), no PR for branch, local tip diverges from PR head (unpushed commits or force-push). Exit code 1 if any errors during processing, 0 otherwise.

## Development

```bash
cd tools && uv sync             # setup
uv run ruff check .             # lint
uv run ruff format .            # format
```

Python >= 3.11; ruff for lint + format. Line length 88 (ruff default). Ruff rules: E, W, F, I, UP, B, SIM, SLF (E501 ignored). Standalone scripts in `bin/` use PEP 723 inline metadata — their dependencies do not go in `pyproject.toml`. When adding a new tool, add it to the tables above.

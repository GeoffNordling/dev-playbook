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
| `no-future-annotations` | (rule documented in script docstring) | Bans `from __future__ import annotations` (dead weight on Python >= 3.11) |

Hook configuration lives in `.pre-commit-config.yaml` at this repo's root and is the **canonical workspace config**. Other workspace repos symlink it (`ln -s ~/workspace/dev-playbook/.pre-commit-config.yaml .pre-commit-config.yaml`) so any hook added here flows to every repo on the next commit. Each validator is responsible for finding its own targets from cwd and exiting 0 silently when there are none, so the same invocation is safe in a repo that has nothing to audit.

#### Three-environment contract

Every `local` hook entry runs in three environments and MUST work in all of them:

1. **dev-playbook locally** — `.pre-commit-config.yaml` is the real file.
2. **Consumer repos locally** — `.pre-commit-config.yaml` is a *symlink* back to dev-playbook.
3. **GitHub Actions runner** — repo checked out at an arbitrary path; no `$HOME` paths exist.

Hardcoded absolute paths under `$HOME` break (3). Cwd-relative paths break (2). The working pattern is to resolve dev-playbook's root via `realpath .pre-commit-config.yaml` and build the tool path from there, e.g.:

```yaml
entry: bash -c 'exec python3 "$(dirname "$(realpath .pre-commit-config.yaml)")/tools/bin/your-tool" "$@"' --
```

When changing a hook entry, walk all three environments before pushing. Past failures (CI 403/404 on `tools/bin/...`) trace back to skipping environment (3) in review.

To add a new validation script:

1. Write the script under `bin/`. Discover targets relative to cwd; exit 0 silently when none exist.
2. Add a `local` hook entry to `.pre-commit-config.yaml`. Resolve the tool's path via `realpath .pre-commit-config.yaml` (consumer repos symlink the config back to dev-playbook; in dev-playbook itself `realpath` returns the local file). Use the existing entries as a model for `language: system`, `pass_filenames`, `types`, `always_run`.
3. Run `pre-commit run --all-files` in dev-playbook and at least one consumer repo to confirm both pass.

#### Utility scripts

Run ad hoc on user demand. Not part of the pre-commit pipeline.

| Tool | Purpose |
|------|---------|
| `py-outline` | Print class/function structure of a Python package (signatures + docstrings) |
| `workspace-backup` | Archive every workspace repo (with `.git/`) into a single dated .zip |
| `worktree-sweep` | Prune `.claude/worktrees/` entries whose PR is merged with no local divergence; report ambiguous cases |
| `bootstrap-labels` | Enforce the workspace's GitHub label scheme in the current repo (closed-world, idempotent); auto-invoked by `/intake` |
| `gh-show` (in `dotfiles/bin/`) | Print a GitHub issue or PR with body + comments in a compact, agent-friendly form |

## Tool reference

Each tool supports `--help` for full usage, options, and exit codes.

### py-outline

Print the structure of a Python package; classes, functions, type-hinted signatures, and first-line docstrings via static analysis.

```bash
py-outline src/mypackage
py-outline src/mypackage > structure.txt
```

### ref-check

Scan every markdown file in the invoking repo for `~/workspace/` cross-references and report their status as JSON Lines to stdout. Resolves in-repo references against the working copy (worktree-safe via `git rev-parse --git-common-dir`); resolves cross-repo references against the absolute path on disk. Enforces the cross-reference conventions in [repo-documentation.md](../standards/repo-documentation.md).

```bash
ref-check [--all] [directory]
```

Each line is a JSON object with `source`, `line`, `target`, and `status` (`ok` or `broken`). Default emits broken refs only; `--all` emits every reference. Exit code: 0 clean, 1 broken refs found, 2 cannot run (no .md files, or not a git repo).

Fragment anchors (`#heading-slug`) are stripped before resolution and are intentionally **not** validated — only the file's existence is checked. A link to a real file with a stale `#section` anchor reports `ok`. Validating heading slugs is out of scope.

### internal-skill-audit

Audit internal skill bundles for conformance against [skill-conventions.md](../standards/skill-conventions.md). Walks two skill roots when present in the target directory: `.claude/skills/` (project-level skills, any repo) and `dotfiles/dot-claude/skills/` (workspace-global skills, dev-playbook only). Externally-managed skills — bundle directories that are symlinks, typically into `dotfiles/.agents/skills/` — are skipped, since their conformance is the upstream's concern.

```bash
internal-skill-audit [directory]
```

One line per finding to stdout in `file:check: message` format. Exit code 0 if clean (or no skill roots present, so the same invocation is safe in any repo); 1 if any errors.

### test-privacy

Flag private-name access in test files. Enforces the "Access only public names" rule from [testing-conventions.md](../standards/testing-conventions.md): tests `SHALL` exercise public identifiers only, reaching private helpers through the public interfaces that call them.

```bash
test-privacy                       # walks current directory for test_*.py
test-privacy path [...]            # scans one or more explicit files or directories
```

One line per finding to stdout in `file:line  rule  message` form. Exit code 0 if clean (or no test files found, so the same invocation is safe in any repo); 1 if any findings; 2 on tool error.

### no-future-annotations

Flag `from __future__ import annotations` in Python files. This workspace targets Python >= 3.11, where every motivation for the import (PEP 604 unions, builtin generics, forward references) is already met by the language. Scans `*.py` files plus extensionless files with a Python shebang; uses AST parsing so string literals don't trigger false positives.

```bash
no-future-annotations                 # scans current directory
no-future-annotations path [...]      # scans explicit files or directories
```

One line per finding to stdout in `file:line  rule  message` form. Exit code 0 if clean, 1 if any findings, 2 on tool error.

### workspace-backup

Archive every Git repo in `~/workspace` into a single dated `.zip`, preserving each repo's `.git/` directory so the archive can fully replace the workspace if GitHub is lost. Each repo becomes a top-level folder inside the archive.

```bash
workspace-backup                      # archive ~/workspace → workspace-backup-YYYY-MM-DD.zip
workspace-backup -o /tmp/snap.zip     # custom output path
workspace-backup --force              # overwrite existing output
```

Pinned to `~/workspace` — no auto-detection and no alternate-path argument. Fails loudly if `~/workspace` is missing rather than backing up the wrong directory. Skips hidden directories and non-repo subfolders. Symlinks are not followed.

### worktree-sweep

Walk `.claude/worktrees/` in the current repo and prune worktrees whose most-recent PR is merged with no local divergence. Anything else is reported for human triage. Implements the cleanup step of [workflow.md](../workflow/workflow.md).

```bash
worktree-sweep            # apply prunes, report the rest
worktree-sweep --dry-run  # report only
```

Auto-prune requires all three: PR state `MERGED`, local tip SHA matches the PR's `headRefOid`, and `git status --porcelain` is empty. Ambiguous categories: PR open (in-progress, skipped), PR closed without merge (rejected), no PR for branch, local tip diverges from PR head (unpushed commits or force-push). Exit code 1 if any errors during processing, 0 otherwise.

### bootstrap-labels

Enforce the workspace's GitHub label scheme in the current repo. Closed-world and idempotent: canonical labels are created or have their descriptions corrected; any label not in the canonical table is deleted. Color drift is ignored. The label scheme is defined in [workflow.md](../workflow/workflow.md). `/intake` auto-invokes this on every run, so the labels are reconciled automatically the first time the workflow is used in a new repo.

```bash
bootstrap-labels
```

Emits one line per label: `created`, `updated`, `deleted`, or `unchanged`. Reads the current repo from `gh`'s context (`git remote -v`). Stdlib-only (no PEP 723 deps). Exits 0 on success.

### gh-show

Print a GitHub issue or PR in a compact form: title, state, labels, body, then comments in chronological order. Lives in `dotfiles/bin/` (not `tools/bin/`) because it is a personal shell helper, but is documented here so workflow consumers can find it.

```bash
gh-show <issue-or-pr-number>
```

Used by `/intake`, `/sdd`, and the SDD phase skills to load issue context at the start of every session.

## Development

```bash
cd tools && uv sync             # setup
uv run ruff check .             # lint
uv run ruff format .            # format
```

Python >= 3.11; ruff for lint + format. Line length 88 (ruff default). Ruff rules: E, W, F, I, UP, B, SIM, SLF (E501 ignored). Standalone scripts in `bin/` use PEP 723 inline metadata — their dependencies do not go in `pyproject.toml`. When adding a new tool, add it to the tables above.

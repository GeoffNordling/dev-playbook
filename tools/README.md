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

- Project-specific scripts — put them in that project's repo
- Anything with a dedicated home elsewhere in this repo (standards, agent config, templates, shell aliases)

## Setup

```bash
cd tools && uv sync
```

## Validation scripts (`bin/`)

Run automatically on every commit via pre-commit hooks. Each script exits 0 on success / 1 on failure / 2 on tool error, writes machine-readable findings to stdout (one per line) and a one-line summary to stderr. Each validator discovers its targets from cwd and exits 0 silently when none exist, so the same invocation is safe in any repo.

| Script | Standard | Purpose |
|--------|----------|---------|
| `ref-check` | [repo-documentation.md](../standards/repo-documentation.md) | Broken cross-references in markdown |
| `internal-skill-audit` | [skill-conventions.md](../standards/skill-conventions.md) | Skill conformance |
| `test-privacy` | [testing-conventions.md](../standards/testing-conventions.md) | Private-name access in test files |
| `no-future-annotations` | [python-conventions.md — Future Imports](../standards/python-conventions.md#future-imports) | Bans `from __future__ import annotations` |

Run any script with `--help`; each script's docstring documents its behavior in full.

### Three-environment contract

Every `local` hook entry runs in three environments and MUST work in all of them:

1. **dev-playbook locally** — `.pre-commit-config.yaml` is the real file.
2. **Consumer repos locally** — `.pre-commit-config.yaml` is a relative symlink back to dev-playbook.
3. **GitHub Actions runner** — repo checked out at an arbitrary path. Consumer repos check out dev-playbook as a sibling so the relative symlink resolves.

Hardcoded `$HOME` paths break (3); cwd-relative paths break (2). Resolve dev-playbook's root via `realpath .pre-commit-config.yaml`:

```yaml
entry: bash -c 'exec python3 "$(dirname "$(realpath .pre-commit-config.yaml)")/tools/bin/your-tool" "$@"' --
```

When adding a validator, test it in both dev-playbook and a consumer repo before pushing.

## Utility scripts

Run ad hoc on user demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `py-outline` | Print class/function structure of a Python package |
| `workspace-backup` | Archive every workspace repo (with `.git/`) into a dated `.zip` |
| `worktree-sweep` | Prune merged-PR worktrees in `.claude/worktrees/` |
| `bootstrap-labels` | Enforce GitHub label scheme in the current repo (auto-invoked by `/intake`) |
| `gh-show` (in `dotfiles/bin/`) | Print a GitHub issue or PR with body + comments |

Run any script with `--help`; each script's docstring documents its behavior in full.

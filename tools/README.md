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

### Two run environments

Each hook entry runs in two environments and MUST work in both:

1. **dev-playbook itself** — the `repo: local` block in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) runs the script from the working tree, cwd at the repo root.
2. **Consumer repos and CI** — pre-commit clones dev-playbook at the pinned `rev` into its own cache and runs the script from that clone, cwd at the consumer repo. See [build-conventions.md — Pre-commit](../standards/build-conventions.md#pre-commit).

In both, pre-commit resolves the script by the relative `entry: tools/bin/<tool>` declared in [`.pre-commit-hooks.yaml`](../.pre-commit-hooks.yaml) (mirrored in the local block) against the dev-playbook checkout that holds it — no `$HOME` paths, no `realpath` indirection.

When adding a validator, mirror it into both the manifest and the local block, and test it in dev-playbook and a consumer repo before pushing.

## Utility scripts

Run ad hoc on human demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `griffe-outline` | Print class/function structure of a Python package |
| `worktree-sweep` | Prune merged-PR worktrees in `.claude/worktrees/` |
| `bootstrap-labels` | Enforce GitHub label scheme in the current repo (auto-invoked by `/intake`) |
| `workflow-state-data` | Emit workflow metrics and live issue states as JSON, reconstructed from GitHub label timelines |

Run any script with `--help`; each script's docstring documents its behavior in full.

> [!WARNING]
> **`workflow-state-data` is unreviewed and untrusted.** It was produced end-to-end by an autonomous agent workflow; no human read its code or exercised any engineering judgment over its implementation. Treat it as completely untrustworthy — do not rely on its output, and read and vet the code yourself before using it for anything that matters.

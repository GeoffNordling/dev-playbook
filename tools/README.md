---
type: README
title: Tools
description: CLI utilities and shared libraries that automate cross-repo workspace tasks
---

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

Run automatically on every commit via pre-commit hooks. Each script exits 0 on success / 1 on findings / 2 on tool error, writes machine-readable findings to stdout (one per line) and a one-line summary to stderr. Each takes the repository root as its argument (default: cwd) and discovers its targets through `git ls-files`, so discovery is gitignore-aware and worktree-scoped.

| Script | Standard | Purpose |
|--------|----------|---------|
| `python-lint` | [python-conventions.md](/standards/python-conventions.md), [testing-conventions.md](/standards/testing-conventions.md) | Python-source rules in one walk: no `from __future__ import annotations`, empty `__init__.py`, no private-name access from tests |
| `ref-check` | [cross-references.md](/standards/docs/cross-references.md) | Cross-reference integrity — root-absolute Links and `~/workspace` Citations |
| `okf-lint` | [document-types.md](/standards/document-types.md), [indexes.md](/standards/docs/indexes.md) | OKF-bundle integrity — concept-doc frontmatter types and `index.md` freshness |
| `internal-skill-audit` | [skill-conventions.md](/standards/skill-conventions.md) | Skill conformance |
| `judgments-lint` | [declarations.md](/standards/judgments/declarations.md) | Judgment declaration validity |

`python-lint`, `ref-check`, and `okf-lint` assert unconditionally and fail loud; they do not skip themselves when a target kind is absent. Run any script with `--help`; each script's docstring documents its behavior in full.

## Shared libraries (`lib/`)

The validators share their markdown and Python primitives rather than redefining them per script:

- `lib/md` — fenced-code skipping, GitHub heading slugs, YAML frontmatter, link extraction, and the OKF concept-doc/harness-owned path classification. Consumed by `ref-check` and `okf-lint`.
- `lib/pyast` — gitignore-aware Python-file discovery and AST parsing. Consumed by `python-lint`.

A `tools/bin/` script imports them by adding its parent (`tools/`) to `sys.path`, so `from lib import md` resolves from the pre-commit clone that holds the script, not the consumer's working directory.

### Two run environments

Each hook entry runs in two environments and MUST work in both:

1. **dev-playbook itself** — the `repo: local` block in [`.pre-commit-config.yaml`](/.pre-commit-config.yaml) runs the script from the working tree, cwd at the repo root.
2. **Consumer repos and CI** — pre-commit clones dev-playbook at the pinned `rev` into its own cache and runs the script from that clone, cwd at the consumer repo. See [distribution.md](/standards/build/distribution.md).

In both, pre-commit resolves the script by the relative `entry: tools/bin/<tool>` declared in [`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml) (mirrored in the local block) against the dev-playbook checkout that holds it — no `$HOME` paths, no `realpath` indirection.

When adding a validator, mirror it into both the manifest and the local block, and test it in dev-playbook and a consumer repo before pushing.

## Utility scripts

Run ad hoc on human demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `griffe-outline` | Print class/function structure of a Python package |
| `bootstrap-labels` | Enforce GitHub label scheme in the current repo (auto-invoked by `/intake`) |
| `transcript-export` | Render Claude Code sessions to readable per-session XML transcripts: `transcript-export <out_dir> <session_id… \| --recent N \| --all>` |

Run any script with `--help`; each script's docstring documents its behavior in full.

---
type: README
title: Scripts
description: The executable surface of published hook entry points and local dev scripts, with shared library code in src/dev_playbook/
---

# Scripts

The repo's executable surface: the published pre-commit hook entry points and
the local dev CLIs. Each file here is a thin shim — a program you run, not a
module you import — over the library code in `src/dev_playbook/`.

> *"The perfect race car crosses the finish line in first place and then falls to pieces."*  
> — Ferdinand Porsche
>
> *"The purpose of a system is what it does."*  
> — Stafford Beer
>
> *"There is no prize to perfection, only an end to pursuit."*  
> — Viktor, *Arcane*

## What belongs here

- Published hook entry points — the scripts consumer repos run via pre-commit.
- Local dev CLIs that automate workspace tasks across repos, run ad hoc.

Every file is an executable shim: it puts `src/` on `sys.path` and calls into
`src/dev_playbook/`, so the logic stays importable and testable while the file
here stays a runnable program.

## What does NOT belong here

- Library code — the logic the shims call lives in `src/dev_playbook/`, not here.
- Project-specific scripts — put them in that project's repo.
- Anything with a dedicated home elsewhere in this repo (standards, agent config, templates, shell aliases).

## Setup

```bash
uv sync
```

Run from the repo root. `uv sync` builds the editable install of
`dev_playbook`; each script is directly executable and also self-bootstraps
its dependencies via its `uv run --script` shebang.

## Validation scripts

The published hooks. They run automatically on every commit via pre-commit,
and consumer repos run them from a pinned clone (see
[distribution.md](/standards/build/distribution.md)). Each script exits 0 on
success / 1 on findings / 2 on tool error, writes machine-readable findings to
stdout (one per line) and a one-line summary to stderr. Each takes the
repository root as its argument (default: cwd) and discovers its targets
through `git ls-files`, so discovery is gitignore-aware and worktree-scoped.

| Script | Standard | Purpose |
|--------|----------|---------|
| `repo-audit` | [the build standard](/standards/build/index.md) | Repo structure — inferred layers, required/forbidden files, canonical-artifact compares, name mapping, doc shape |
| `python-lint` | [python-style.md](/standards/python-style.md), [testing-conventions.md](/standards/testing-conventions.md) | Python-source rules in one walk: no `from __future__ import annotations`, empty `__init__.py`, no private-name access from tests |
| `ref-check` | [cross-references.md](/standards/docs/cross-references.md) | Cross-reference integrity — root-absolute Links and `~/workspace` Citations |
| `okf-lint` | [document-types.md](/standards/docs/document-types.md), [indexes.md](/standards/docs/indexes.md) | OKF-bundle integrity — concept-doc frontmatter types and `index.md` freshness |
| `internal-skill-audit` | [skill-conventions.md](/standards/skill-conventions.md) | Skill conformance |
| `judgments-lint` | [declarations.md](/instruments/judgments/declarations.md) | Judgment declaration validity |

`repo-audit`, `python-lint`, `ref-check`, and `okf-lint` assert unconditionally
and fail loud; they do not skip themselves when a target kind is absent. Run
any script with `--help`; each script's docstring documents its behavior in
full.

## Shared libraries (`src/dev_playbook/`)

The scripts share their markdown and Python primitives rather than redefining
them per script. The library is the installed `dev_playbook` package:

- `dev_playbook.md` — fenced-code skipping, GitHub heading slugs, YAML frontmatter, link extraction, and the OKF concept-doc/harness-owned path classification. Consumed by `ref-check` and `okf-lint`.
- `dev_playbook.pyast` — gitignore-aware Python-file discovery and AST parsing. Consumed by `python-lint` and `repo-audit`.
- `dev_playbook.gitrepo` — canonical repo-name resolution (main checkout and worktrees answer alike) and gitignore-aware file listing. Consumed by `ref-check` and `repo-audit`.

The larger surfaces are subpackages: `dev_playbook.judgments` (declaration
loading/validation and the plan/render/record runner, behind `judgments-lint`
and `judgments-run`), `dev_playbook.transcript_export` (the Claude Code session
model, classifier, and renderer behind `transcript-export`), and
`dev_playbook.skipcache` (the seen-set the judgments runner uses to skip
already-recorded work).

A `scripts/` shim reaches the package by inserting the repo's `src/` directory
(`Path(__file__).resolve().parents[1] / "src"`) at the front of `sys.path`, so
`from dev_playbook import md` resolves from the checkout that holds the
script — the pre-commit clone at the pinned `rev`, not the consumer's working
directory.

### Two run environments

Each hook entry runs in two environments and MUST work in both:

1. **dev-playbook itself** — the `repo: local` block in [`.pre-commit-config.yaml`](/.pre-commit-config.yaml) runs the script from the working tree, cwd at the repo root.
2. **Consumer repos and CI** — pre-commit clones dev-playbook at the pinned `rev` into its own cache and runs the script from that clone, cwd at the consumer repo. See [distribution.md](/standards/build/distribution.md).

In both, pre-commit resolves the script by the relative `entry:` path declared
in [`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml) (mirrored in the local
block) against the dev-playbook checkout that holds it — no `$HOME` paths, no
`realpath` indirection.

When adding a validator, mirror it into both the manifest and the local block,
and test it in dev-playbook and a consumer repo before pushing.

## Utility scripts

Run ad hoc on human or skill demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `judgments-run` | Plan / render / record over a repo's judgment declarations (driven by the `/run-judgments` skill) |
| `griffe-outline` | Print class/function structure of a Python package |
| `sweep` | On-demand workspace sweep: GitHub settings drift via `gh api` ([repo-settings.md](/standards/repo-settings.md)) and stale dev-playbook pins |
| `bootstrap-labels` | Enforce GitHub label scheme in the current repo (auto-invoked by `/intake`) |
| `transcript-export` | Render Claude Code sessions to readable per-session XML transcripts: `transcript-export <out_dir> <session_id… \| --recent N \| --all>` |

Run any script with `--help`; each script's docstring documents its behavior in
full.

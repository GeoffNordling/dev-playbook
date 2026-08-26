---
type: README
title: Scripts
description: The executable surface of published hook entry points and local dev scripts, with shared library code in src/dev_playbook/
---

# Scripts

The repo's executable surface: the published pre-commit hook entry points and
the local dev CLIs. Each file here is a thin shim over the library code in
`src/dev_playbook/`.

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

The commit-gate detectors. They run automatically on every commit through
`playbook-lint` — the one published hook, whose roster
(`src/dev_playbook/playbook_lint.py`) dispatches every detector below
concurrently and aggregates their exits — and consumer repos run that hook
from a pinned clone (see
[distribution.md](/standards/build/distribution.md)). Each script exits 0
on success / 1 on findings / 2 on tool error, writes machine-readable findings
to stdout (one per line) and a one-line summary to stderr. Each takes the
repository root as its argument (default: cwd) and discovers its targets
through `git ls-files`, so discovery is gitignore-aware and worktree-scoped.

| Script | Standard | Purpose |
|--------|----------|---------|
| `repo-lint` | [the build standard](/standards/build/index.md) | Repo structure — inferred layers, required/forbidden files, canonical-artifact compares, name mapping, doc shape |
| `python-lint` | [python/style.md](/standards/python/style.md) | Python-source rules in one walk: no `from __future__ import annotations`, empty `__init__.py` |
| `testing-lint` | [testing/conventions.md](/standards/testing/conventions.md) | Python test rules: no private-name access from tests, test-file mirror placement, no `if`/`try` logic in a test body |
| `ref-lint` | [cross-references.md](/standards/knowledge-organization/cross-references.md) | Cross-reference integrity — root-absolute Links and `~/workspace` Citations |
| `okf-lint` | [document-types.md](/standards/knowledge-organization/document-types.md), [indexes.md](/standards/knowledge-organization/indexes.md) | OKF-bundle integrity — concept-doc frontmatter types and `index.md` freshness |
| `decisions-lint` | [decisions/records.md](/standards/decisions/records.md) | Decision Record integrity — sequential numbering and status vocabulary over `docs/decisions/` |
| `harness-files-lint` | [runbook-conventions.md](/standards/harness/runbook-conventions.md) | Skill conformance |
| `judgments-lint` | [declarations.md](/standards/semantic-validation/declarations.md) | Judgment declaration validity |
| `prose-lint` | [prose/conventions.md](/standards/prose/conventions.md) | Prose spelling — the American `judgment` — over authored Markdown, and the banned actor noun over every tracked file of any type, less the vendored `.agents/` trees and verbatim `type: Reference` mirrors |
| `standards-lint` | [standard/format.md](/standards/standard/format.md) | The meta-standard's rules over `standards/` — card layout, catalog order, the card↔rule matrix, hook-surface agreement, and no shadowing of an upstream card (consumer mode); clean by construction where no `standards/` tree is present |

`repo-lint`, `python-lint`, `testing-lint`, `ref-lint`, `okf-lint`,
`decisions-lint`, and `prose-lint` assert unconditionally and fail loud; they do
not skip themselves when a target kind is absent. `harness-files-lint` and
`standards-lint` are optional-surface: each exits 0 silently when its audited
surface is absent — no skills, no `standards/` tree — and asserts only over a
surface that is present. Run
any script with `--help`; each script's docstring documents its behavior in
full.

## Shared libraries (`src/dev_playbook/`)

The scripts share their markdown and Python primitives through the library —
the installed `dev_playbook` package:

- `dev_playbook.md` — fenced-code skipping, GitHub heading slugs, YAML frontmatter, link extraction, and the OKF concept-doc/harness-owned path classification. Consumed by `ref-lint` and `okf-lint`.
- `dev_playbook.pyast` — gitignore-aware Python-file discovery and AST parsing. Consumed by `python-lint`, `testing-lint`, and `repo-lint`.
- `dev_playbook.testing_lint` — the Python-testing detector logic: the three test-file rules (privacy, mirror layout, no-logic) over one walk. Consumed by `testing-lint`.
- `dev_playbook.gitrepo` — canonical repo-name resolution (main checkout and worktrees answer alike) and gitignore-aware file listing. Consumed by `ref-lint` and `repo-lint`.
- `dev_playbook.filegraph` — the file-graph builder: node bucketing, edge extraction, and the graph queries (`graph`), plus the self-contained HTML viz assembler (`viz`). Consumed by `file-graph`.
- `dev_playbook.dotfiles` — the dotfiles install: which machine this is (`machine`), the per-machine settings merge (`settings`), and the stow/mirror/loader steps (`sync`). Consumed by `sync-dotfiles`.
- `dev_playbook.voice` — the agent-facing voice vocabulary: the first-person words instruction text may not speak in, each with the wording of the fault it trips. Consumed by `repo-lint`, which enforces it over prose, and `repo-init`, which refuses a repo name that carries one (or the banned actor noun, via `dev_playbook.prose_lint`).
- `dev_playbook.repo_init` — the fresh-repo scaffold: canonical-artifact rendering and the local init steps (`git init`, `uv lock`, hook install, `repo-lint` self-check). Consumed by `repo-init`.

The larger surfaces are subpackages: `dev_playbook.judgments` (declaration
loading/validation and the plan/render/record runner, behind `judgments-lint`
and `judgments-run`), `dev_playbook.transcript_export` (the Claude Code session
model, classifier, and renderer behind `transcript-export`),
`dev_playbook.skipcache` (the seen-set the judgments runner uses to skip
already-recorded work), and `dev_playbook.factory`, whose pieces are the
software factory's append-only run ledger — the `ledger` table beside the
hook-capture `events` table, its per-kind writers and its two read queries; the
job launcher that sweeps a launch's credentials, spawns a factory node, watches
its stream live, and writes its two job rows; and the build-region traverse that
carries one issue from its phase label to an open pull request, behind
`traverse-issue`. The launcher and the traverse are **Linux only**, and say so
at import: every node the launcher spawns is set to die with it through
`PR_SET_PDEATHSIG`, a `prctl` operation with no portable equivalent, and a
child that could outlive its launcher is an hour of claude billed with nobody
watching it.

A `scripts/` shim reaches the package by inserting the repo's `src/` directory
(`Path(__file__).resolve().parents[1] / "src"`) at the front of `sys.path`, so
`from dev_playbook import md` resolves from the checkout that holds the
script — the pre-commit clone at the pinned `rev`, not the consumer's working
directory.

### Two run environments

Each *published* hook entry runs in two environments and MUST work in both:

1. **dev-playbook itself** — the `repo: local` block in [`.pre-commit-config.yaml`](/.pre-commit-config.yaml) runs the script from the working tree, cwd at the repo root.
2. **Consumer repos and CI** — pre-commit clones dev-playbook at the pinned `rev` into its own cache and runs the script from that clone, cwd at the consumer repo. See [distribution.md](/standards/build/distribution.md).

In both, pre-commit resolves the script by the relative `entry:` path declared
in [`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml) (mirrored in the local
block) against the dev-playbook checkout that holds it — no `$HOME` paths, no
`realpath` indirection.

When adding a validator, enroll it in the `playbook-lint` roster
(`DETECTORS` in `src/dev_playbook/playbook_lint.py`) — the manifest and the
local block carry only the aggregate hook and never change — and test it in
dev-playbook and a consumer repo before pushing.

## Utility scripts

Run ad hoc on user or skill demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `file-graph` | Build the file graph of a repo per [file-graph.md](/instruments/file-graph.md) — every file bucketed, every reference a typed edge, reachability/components/orphans/defects queries; JSON to stdout, `--html` assembles the viz |
| `judgments-run` | Plan / render / record over a repo's judgment declarations (driven by the `/judgments-sweep` skill) |
| `griffe-outline` | Print class/function structure of a Python package |
| `workspace-lint` | On-demand workspace audit via `gh api`: GitHub settings drift and default-branch protection ([repo-settings.md](/standards/tracking/repo-settings.md)), label-scheme parity and blocked-label bans, open-leaf four-tuple validity and brief shape, epic shape, wayfinder map and ticket shape, and stale dev-playbook pins |
| `bootstrap-labels` | Enforce the GitHub label scheme in the current repo — run by hand, after a scheme change or when adopting a repo |
| `bump-pins` | Move the dev-playbook `rev` pin across the governed consumer repos and re-run each one's commit gate — the release step of [distribution.md](/standards/build/distribution.md); commits nothing |
| `repo-init` | Scaffold a fresh workspace repo conforming to the build standard — canonical artifacts, `git init`, `uv lock`, hook install, `repo-lint` self-check; the GitHub tail is [bootstrap.md](/standards/build/bootstrap.md) |
| `transcript-export` | Render Claude Code sessions to readable per-session XML transcripts: `transcript-export <out_dir> <session_id… \| --find PATTERN \| --recent N \| --all>` |
| `sync-dotfiles` | Install [`dotfiles/`](/dotfiles/README.md) into `$HOME` — stow the packages, mirror the externally managed skills, generate `~/.claude/settings.json` for this machine; `--check` reports settings drift and is what the session-start hook runs |
| `traverse-issue` | Carry one factory issue from its phase label to an open PR: `traverse-issue <owner/name> <issue> <auto\|user-rework>` — per-issue lock, worktree create-or-reuse, the `build` and `open-pr` nodes launched headless, one JSON line on stdout naming the terminal status |

Run any script with `--help`; each script's docstring documents its behavior in
full.

### Regenerating this repo's file graph

dev-playbook commits its own file graph under `readings/file-graph/` — a
reading like any other, regenerated manually on demand by running the executor
with this repo's scope, never hand-edited and free to lag until you rerun it.
Run this only when the user asks for a fresh graph — never as part of a
refactor or rename sweep:

```bash
scripts/file-graph --seed CLAUDE.md --exclude readings/file-graph/ --exclude src/dev_playbook/filegraph/assets/ --output readings/file-graph/dev-playbook.json --html readings/file-graph/dev-playbook.html
```

The `--seed` answers "what can an agent reading only the injected `CLAUDE.md`
reach?"; the two `--exclude`s drop the graph's own output and the vendored d3
(which alone spawns hundreds of spurious `code-ref` edges). Both choices are
stamped into the JSON (`seeds`, `excluded`), so the artifact records how it was
built.

### Exporting a session transcript

Naming the session is the only hard step, so `transcript-export` takes it
several ways and never asks the caller to reach past it to the `agentsview`
CLI:

```bash
scripts/transcript-export out/ "$CLAUDE_CODE_SESSION_ID"   # the running session
scripts/transcript-export out/ --find 'the auth bug'       # by content
scripts/transcript-export out/ --recent 3                  # the 3 newest
```

`CLAUDE_CODE_SESSION_ID` is set in every Claude Code session and holds exactly
the id the exporter wants. `--find` searches message and tool content; a pattern
matching more than one session is ambiguous and fails loud rather than guess, so
narrow it or pass `--limit N`.

When a filter `--find` does not expose is needed (`--project`, `--date-from`,
`--regex`), query the daemon directly and pass the ids through. `agentsview`
requires `--server`: without it the CLI auto-starts a rival daemon, which dies on
the write lock the running one holds.

```bash
agentsview --server http://127.0.0.1:8080 session search 'x' --json --project p
```

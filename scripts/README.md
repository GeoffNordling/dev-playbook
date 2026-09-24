---
type: README
title: Scripts
description: The local dev scripts, thin shims over the library code in src/dev_playbook/, and how the published playbook hook relates to them
---

# Scripts

The repo's local dev CLIs. The one published hook is the `playbook`
console script, not a file here. Each file here is a thin shim over the
library code in `src/dev_playbook/`.

> *"The perfect race car crosses the finish line in first place and then falls to pieces."*  
> — Ferdinand Porsche
>
> *"The purpose of a system is what it does."*  
> — Stafford Beer
>
> *"There is no prize to perfection, only an end to pursuit."*  
> — Viktor, *Arcane*

## What belongs here

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

## The commit gate

The commit gate is `playbook check` — the one published hook, the console
script `pyproject.toml` declares. It builds one model of the repository
from `git ls-files`, runs every check the package registers
(`src/dev_playbook/checks/`, one module per `standards/` directory), then
two steps that are not functions over the model: the
[Loop Conventions](/standards/doc-type/loop-conventions.md) checks in
`dev_playbook.loop_lint`, until the loop workstream moves them into the
package, and `pre-commit validate-manifest` where the repo publishes a
manifest. It exits 0 on success / 1 on findings / 2 when the model cannot
be built or a step cannot run, writes findings to stdout one per line, and
a summary to stderr. `playbook checks` lists the registry. Consumer repos
run the hook from a venv pre-commit installs at the pinned rev (see
[Distribution Channel](/standards/distribution/channel.md)).

## Shared libraries (`src/dev_playbook/`)

The scripts share their markdown and Python primitives through the library —
the installed `dev_playbook` package:

- `dev_playbook.md` — fenced-code skipping, GitHub heading slugs, YAML frontmatter, link extraction, the OKF concept-doc/harness-owned path classification, and the agent-instruction test behind the voice rule. Consumed by the repo model and the checks.
- `dev_playbook.gitrepo` — canonical repo-name resolution (main checkout and worktrees answer alike) and gitignore-aware file listing. Consumed by the repo model.
- `dev_playbook.dotfiles` — the dotfiles install: which machine this is (`machine`), the per-machine settings merge (`settings`), and the stow/mirror/loader steps (`sync`). Consumed by `sync-dotfiles`.
- `dev_playbook.voice` — the agent-facing voice vocabulary: the first-person words instruction text may not speak in, each with the wording of the fault it trips. Consumed by the prose checks, which check prose against it, and `repo-init`, which refuses a repo name that carries one (or the banned actor noun, via `dev_playbook.checks.prose`).
- `dev_playbook.repo_init` — the fresh-repo scaffold: canonical-artifact rendering and the local init steps (`git init`, `uv lock`, hook install, `playbook check` self-check). Consumed by `repo-init`.

The one larger surface is a subpackage: `dev_playbook.transcript_export`,
the Claude Code session model, classifier, and renderer behind
`transcript-export`.

A `scripts/` shim reaches the package by inserting the repo's `src/` directory
(`Path(__file__).resolve().parents[1] / "src"`) at the front of `sys.path`, so
`from dev_playbook import md` resolves from the checkout that holds the
script — the pre-commit clone at the pinned `rev`, not the consumer's working
directory.

### Two run environments

The published hook runs in two environments and MUST work in both:

1. **dev-playbook itself** — the `repo: local` block in [`.pre-commit-config.yaml`](/.pre-commit-config.yaml) runs `uv run playbook check` from the working tree, cwd at the repo root.
2. **Consumer repos and CI** — pre-commit installs dev-playbook at the pinned `rev` into a venv it caches and runs the console script from there, cwd at the consumer repo. See [Distribution Channel](/standards/distribution/channel.md).

When adding a check, write it as one function under `src/dev_playbook/checks/`
with the `@check` decorator — the manifest and the local block carry only the
one hook and never change — and test it in dev-playbook and a consumer repo
before pushing.

## Utility scripts

Run ad hoc on user or skill demand; not part of the pre-commit pipeline.

| Script | Purpose |
|--------|---------|
| `griffe-outline` | Print class/function structure of a Python package |
| `workspace-lint` | On-demand workspace check via `gh api`: GitHub settings drift and default-branch protection ([repo-settings.md](/guides/repo-settings.md)), label-scheme parity and blocked-label bans, open-leaf four-tuple validity and brief shape, session-leaf shape, epic shape, wayfinder map and ticket shape, and whether each consumer's published config pins dev-playbook's published head with the hook ids its manifest publishes there ([Distribution Channel](/standards/distribution/channel.md)); a roster name with no repo on this machine is announced and passed over |
| `bootstrap-labels` | Apply the GitHub label scheme to the current repo — run by hand, after a scheme change or when adopting a repo |
| `labelgen` | Render the label scheme as the table in [label-scheme.md](/standards/tracking/label-scheme.md); `--check` fails on drift |
| `bump-pin` | Check whether one consumer repo's dev-playbook pin — its `rev` and the hook ids the manifest publishes at that rev, and in a host the dev-playbook source's `rev` in `pyproject.toml` with `uv.lock` re-locked — can move to the release head (`--check`, a probe run in a throwaway worktree of `origin/main`) or move it (`--write`) — the release step of [Distribution Channel](/standards/distribution/channel.md); commits nothing |
| `update-pins` | Move every governed repo's dev-playbook pin to the release head — for each repo on this machine with no ledger row at that head, probe the bump in a throwaway worktree of `origin/main`; green lands one commit on `main`, red cuts a `bump-pin-<sha12>` worktree and hands it to a headless agent that runs `/finish-pin-bump` and opens a PR — and append one row per repo to the [Pin Updates Ledger](/docs/pin-updates.md); run by a systemd user timer every fifteen minutes, exits at once when every repo is recorded; first removes every `bump-pin-*` worktree and branch whose PR is merged or closed; merges nothing; `--dry-run` probes and lands nothing |
| `repo-init` | Scaffold a fresh workspace repo conforming to the build standard — canonical artifacts, `git init`, `uv lock`, hook install, `playbook check` self-check; the GitHub tail is [bootstrap.md](/guides/bootstrap.md) |
| `transcript-export` | Render Claude Code sessions to readable per-session XML transcripts: `transcript-export <out_dir> <session_id… \| --find PATTERN \| --recent N \| --all>` |
| `sync-dotfiles` | Install [`dotfiles/`](/dotfiles/README.md) into `$HOME` — stow the packages and wire up the `~/.bashrc.d` loader |

Run any script with `--help`; each script's docstring documents its behavior in
full.

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

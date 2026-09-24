---
type: General-Sheet
title: Pin Cascade
description: The working root for the pin cascade — the goal, the decisions the user has ruled on, the design of the cascade command and its ledger, the timer, the headless per-repo run, and the worklist; speculative until the cascade has run once over the governed repos
---

# Pin Cascade

The working documentation set for the pin cascade: the system that
moves every governed consumer repo's dev-playbook pin to the published
head whenever dev-playbook `main` moves, works each repo back to green,
and records what it did. This set is speculative: it is the plan and
the decisions of one session, written before the cascade has run once.
The branch is `worktree-pin-cascade`, cut from `main` at `a94aebd`
(PR #495) in the worktree `.claude/worktrees/pin-cascade`.

## Goal

A change merged or committed to dev-playbook `main` reaches every
governed repo within one poll interval, with no user action unless a
repo goes red, and the history of every such release is readable in
git and the IDE.

## Constraints

- **The user merges every PR.** No agent approves or merges a PR, ever.
- **Local only.** No GitHub Actions, no cloud routines. The trigger and
  the fan-out run on this Fedora machine.
- **Non-governed repos are out of scope.** Only the `GOVERNED` roster
  in `src/dev_playbook/workspace_lint.py` is the population; the
  non-governed repos sitting on `adopt-*` branches are not thought
  about.
- **The headless fan-out is unsandboxed for now.** The `sandcastle`
  branch, unmerged, is the future fence; a follow-up sandboxes the
  cascade once it merges.
- **A `ci.yml` change costs the user a PAT widening.** A fine-grained
  PAT needs Workflows read/write, granted by hand at
  github.com/settings/personal-access-tokens, before any push that
  changes `.github/workflows/ci.yml`. The cascade must say when a repo's
  adaptation touches that file.
- **Off-machine repos exist.** `lunch` and `date-tree` are governed and
  live only on the WSL machine (GPU, personal data). They are handled
  after the seven on this machine: clone locally, update, push, and
  the other machine pulls when ready.

## Decisions

Rulings the user made in the session, in the order made.

- **The trigger is activity on dev-playbook `main`**, not a merge and
  not a pin change. The user sometimes commits straight to `main`.
- **Landing rule.** Green at the new pin → one commit on the consumer's
  `main`. Red → a branch, the agent works the findings to green, opens a
  PR, and the user merges or vetoes.
- **Unmerged branches take the pin when they merge.** The cascade bumps
  `main` regardless of in-flight branches and worktrees. A branch is
  untouched; it meets the new pin when it rebases or merges, and its
  findings surface then, on its own PR. The cascade *reports* every
  remote branch not merged to `main` with its last-commit date, so the
  user can spot a live one and veto. Merged-but-undeleted remote
  branches are noise and are not reported.
- **Poll interval: 15 minutes.** A systemd user timer on this machine.
- **One ledger file in dev-playbook**, one row per repo per run,
  committed by the cascade itself, so the history reads in `git log`
  and the IDE.
- **The ledger commit is not a release.** Pending the user's veto: the
  release head is the newest commit on dev-playbook `main` that touches
  anything other than the ledger file. Without this, each ledger commit
  moves `main` and triggers the next cascade, forever.
- **Headless `claude -p`, Opus**, one run per red repo, the user's
  first use of headless. Billing and flags are in
  [Headless Operation](/docs/headless.md).

## Findings

What the survey established, kept because the design rests on it.

- Every consumer pins hook id `playbook-lint`; PR #495 renamed it
  `playbook-check`. A bare `rev` bump fails in pre-commit before any
  check runs. Step 1 fixed this: `bump-pin` rewrites the hook ids from
  the manifest at the target sha.
- `workspace-lint` audited nothing about pins before this branch. Step 2
  added `distribution.a-consumer-pins-the-published-head`; its first
  live run found all seven on-machine consumers behind `a94aebd`
  (story-forge at `cc561fe`, dwarf-flow at `949d3d0`, sounds at
  `aaaf9c5` on GitHub, the other four at `c29060e`) and every one on
  the stale id.
- `workspace-lint` refused to run on this machine because `lunch` and
  `date-tree` are absent. Step 2 made absence an announcement, not a
  refusal.
- Direct pushes to a consumer's `main` are allowed: the `protect-main`
  ruleset carries only `deletion` and `non_fast_forward`.
- Remotes are HTTPS; `gh` is logged in via keyring; the systemd service
  needs no SSH agent.
- pre-commit hooks installed in a consumer's main checkout fire in its
  linked worktrees, because hooks live in the shared `.git`.
- The systemd units for this laptop live in sysadmin-playbook
  (`systemd/`, documented under `docs/periodic-jobs/`, symlinked into
  `~/.config/systemd/user/`, `%h` for home). The timer lands there as a
  separate PR.
- `claude -p` takes `--model`, `--effort`, `--permission-mode
  bypassPermissions`, `--output-format json`, `--session-id`,
  `--json-schema`.
- **The published manifest could not install at all.** The first dry run
  (step 3, over story-forge) died before any check: pre-commit builds a
  `language: python` hook with the interpreter running pre-commit, the
  consumers' gate is `uvx pre-commit`, and that tool environment runs on
  uv's managed Python 3.13 while dev-playbook requires 3.14. The manifest
  had no `language_version`. Fixed on this branch:
  `language_version: python3.14` in `.pre-commit-hooks.yaml`, verified
  with `pre-commit try-repo` against story-forge. The fix reaches
  consumers only through a release head that carries it, so this PR must
  merge before any consumer can be moved.
- **story-forge is red at `a94aebd`**: 404 findings, most of them
  `tracking.one-list-item-per-entry` in `CANDIDATES.md`. The first real
  measure of what the red-path agent will be handed.

## Design

The shape of the cascade command, `src/dev_playbook/cascade.py` with
the shim `scripts/cascade`, as planned before it was written.

- **Entry.** `cascade [--workspace DIR] [--repos a,b] [--dry-run]`. It
  reads the release head from GitHub and the ledger from dev-playbook
  `main`; a repo with a row at that head, whatever the verdict, is done
  for this release. No repo to move → exit 0 with one line, nothing else
  runs. So the timer runs `cascade` and nothing more; there is no
  separate poller, a `failed` repo is not retried until the next release
  or a hand `bump-pin`, and a `--repos` subset leaves the rest to the
  next tick. Without a published ledger a live run refuses; a dry run
  treats it as empty.
- **Per repo, in roster order, sequentially** (pre-commit's cache lock
  is global). Skip the hook repo by identity (`is_hook_repo`); announce
  off-machine repos. `git fetch origin --prune`. Read the pin on
  `origin/main`; already current → row `current`. A PR already open on
  `bump-pin-<sha12>` → row `pending`, nothing runs.
- **Branch report.** Every `refs/remotes/origin/*` with commits not in
  `origin/main`: name, last-commit date, commits ahead. Under 14 days
  reads as live, older as stale. Goes to stdout, the ledger row's
  notes, and the PR body.
- **Probe.** `bump_pins.probe_worktree` at `origin/main`; rewrite the
  pin with `bump_pins.rewritten`; run the gate once. No baseline run:
  the cascade's question is "green at the new pin", and every finding
  is the agent's to work whatever release caused it.
- **Green.** Commit the one-file change in the worktree, push
  `HEAD:main`. The commit hook runs the gate at the new pin; the
  pre-push `make check` is the second verification. A rejected push is
  a `failed` row with the reason, not a retry.
- **Red.** A persistent worktree at
  `<repo>/.claude/worktrees/bump-pin-<sha12>` on branch
  `bump-pin-<sha12>`, the pin committed `--no-verify`, then
  `claude -p --model opus --permission-mode bypassPermissions` with a
  prompt that names the state, orders the findings worked per
  `/update-standards-pin` §6, a push, `gh pr create` with the sha move
  and each adaptation in the body, no merge, and says no user is
  present. The row is `red → PR <url>`, read back from
  `gh pr list --head`, never from the agent's text. No PR → `failed`,
  worktree kept and named; a worktree already at that path → `failed`
  too, it belongs to a run that did not finish. The agent is not
  launched while any credential variable from
  [Headless Operation](/docs/headless.md) § Billing is set: that is a
  `failed` row, not a scrub. Agent output goes to
  `~/.local/state/dev-playbook/cascade/<run>/<repo>.log`, the gate's
  findings beside it.
- **Ledger.** `docs/pin-cascade.md`, `type: Log`, a table: time (UTC),
  release head (12 chars), repo, verdict (`current` / `green` / `red` /
  `pending` / `failed`), landing (`main <sha12>` / `PR <url>` / reason),
  notes (unmerged branches). Appended and committed in a detached
  worktree of dev-playbook `origin/main`, pushed to `main`. Rows landed
  but not recorded are printed to stderr and the run exits 1.
- **Release head.** Both `cascade` and `workspace-lint`'s pin check use
  it: walk back from `main`'s head over commits whose only changed
  file is the ledger. `gh api repos/{slug}/commits/{sha}` gives `files`
  and `parents`.

## Terms

- **Release head** — the newest commit on dev-playbook `main` that
  touches any file other than the ledger; the sha consumers pin.
- **Ledger** — `docs/pin-cascade.md`, the append-only record of every
  cascade run, one row per repo.
- **Cascade** — one run of `scripts/cascade` over the governed repos at
  one release head.

## Planned

- **Step 4 — the headless per-repo runbook.** Rewrite
  `dotfiles/dot-claude/skills/update-standards-pin/SKILL.md`: §2 and
  §3 still say the checkout must be on a clean `main` and that the
  probe "restores the config", both false since step 1; add the mode
  the cascade launches, a worktree that already holds the bump, work
  the findings, open the PR.
- **Step 5 — the timer.** In sysadmin-playbook: `systemd/pin-cascade.
  service` and `.timer` (15 min, `Persistent=true`, the DNS wait
  `agentsview-update.service` uses), a `docs/periodic-jobs/pin-cascade.
  md` per that repo's conventions, a separate PR.
- **Step 6 — first run.** After this PR merges — the ledger and the
  manifest's `language_version` must be on `main` for any consumer to
  move — over the seven on-machine repos with the user watching, `--dry-run`
  first; then `lunch` and `date-tree` by local clone.
- **Follow-ups.** Sandbox the fan-out once `sandcastle` merges; the
  consumers' `ci.yml` carries `SKIP: ref-lint,web-typecheck` against a
  canonical `SKIP: workspace`, so the first bump reddens every repo on
  `ci.yml` and costs one PAT widening each.

## Completed

- **Step 1 — `bump-pin` moves the hook ids and probes in a worktree.**
  Commit `4a26af0`. `rewritten(text, url, sha, ids)` replaces the
  pinned block's hook entries with the manifest's ids; `check` runs in
  a detached worktree of `origin/main` and never touches the caller's
  checkout; `require_fresh_main` is gone. 33 tests.
- **Step 2 — `workspace-lint` reports pin drift.** Commit `1de29cd`.
  Rule `distribution.a-consumer-pins-the-published-head` in
  `standards/distribution/channel.md`, registered in
  `checks/distribution.py`, decided in `workspace_lint.check_pin` over
  the consumer's published config; `published_head`,
  `published_hook_ids`, `manifest_ids`, `published_file`,
  `pinned_hook_ids`, `is_hook_repo` live in `workspace_lint`;
  `gitrepo.common_dir` is the identity; absent roster names are
  announced on stderr. Docs fixed: `guides/bootstrap.md`,
  `enable-repo-governance/SKILL.md` (ghost rule
  `distribution.a-pinned-rev`), `scripts/README.md`. The two shims
  declare `pyyaml`. 130 tests in the two suites; the full suite's five
  errors are `run make web first`, a build artifact the fresh worktree
  lacks.
- **Step 3 — the cascade command.** 2026-09-23. `src/dev_playbook/
  cascade.py` and `scripts/cascade` as the Design section states;
  `workspace_lint.release_head` walks `gh api repos/{slug}/commits/{sha}`
  back over ledger-only commits and is the target of `bump-pin`,
  `workspace-lint`'s pin rule, and the cascade alike; the ledger
  `docs/pin-cascade.md` (type Log) with its `docs/index.md` row; the
  `scripts/README.md` row; `.pre-commit-hooks.yaml` gains
  `language_version: python3.14`. 26 cascade tests over throwaway repos
  with a real bare origin and scripted gate, `claude`, and `gh`; 6
  release-head tests; 164 in the three suites. First dry run over
  story-forge found the interpreter fault above.

## Unfiled

- The consumers' `ci.yml` `SKIP` names (`ref-lint`) no longer exist as
  hook ids; pre-commit ignores unknown `SKIP` names, so this is only
  drift against the canonical block.
- Whether the red-path agent should also fix a repo that is red before
  the bump (a red baseline) — the design says yes, every finding is
  worked; `bump_pins.check` still refuses a red baseline for its own
  callers.
- A `failed` row is never retried by the cascade; the user re-runs by
  hand or waits for the next release. A `--again REPO` flag that ignores
  the ledger for one repo may earn its place after the first runs.
- The cascade does not run `pre-commit gc` after a green landing, so
  superseded dev-playbook clones accumulate in `~/.cache/pre-commit`
  until someone does.
- The consumers' existing pre-commit environments were built under four
  different interpreters (`py_env-python3`, `3.12`, `3.13`, `3.14` in the
  cache); with `language_version` pinned, every consumer rebuilds once
  under 3.14 at its bump.

## Acronyms

- **PAT** — personal access token, the GitHub credential `gh` and `git`
  push with.
- **PR** — pull request.
- **CI** — continuous integration, the GitHub Actions workflow in
  `.github/workflows/ci.yml`.
- **WSL** — Windows Subsystem for Linux, the other machine.
- **DNS** — domain name system.

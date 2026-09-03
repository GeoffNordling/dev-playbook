---
type: Standard
title: Detectors and Drift
description: The detector contract behind every Audit cell and the drift machinery that keeps standards honest
---

# Detectors and Drift

The Meta-Standard card's machinery: the contract every detector obeys
and the drift checks that keep standards meaning what they meant. The
card shape is declared in the Standard-Card doc-type
([doc-types/standard-card/](/doc-types/standard-card/index.md)); what a
standard *is* belongs to the Standard doc-type
([doc-types/standard/](/doc-types/standard/index.md)).

## Detectors

A **detector** is the read-only check behind an Audit cell — it inspects the
repository against one or more standards and emits findings, never mutating the
repository and never blocking by itself (its runs at a gate are the audit
stationed there — that is Enforcement). This document defines the detector
contract.

- **Read-only means mutating nothing git tracks.** Reaching outside the
  working tree does not disqualify it: workspace-lint queries GitHub over
  `gh api`, writing findings to stdout and a summary to stderr — reading
  remote state and mutating nothing git tracks — so it is read-only and
  belongs in an Audit cell.
- **A formatter is a detector by its check mode.** `shfmt -d` and
  `ruff format --check` report and mutate nothing, so the tool is a
  detector and an Audit cell cites it. The commit gate stations the write
  mode, `shfmt -w`, and that run is Enforcement, never an audit
  ([Vocabulary](/CONTEXT.md#governance)).
- **Wired throughout its scope; applicability lives inside the detector.** A
  workspace-scoped detector runs in every repo, a repo-scoped one throughout
  its host repo; the population it governs runs the full menu, never a
  subset. A detector whose surface is optional (skills, or a `standards/`
  tree) exits 0 silently when the surface is absent; every other detector
  asserts unconditionally and fails loud. A gap is never resolved by making
  a detector opt-in.
- **A card may have more than one detector.** Cards are organized by the
  question they govern; detectors by the mechanism they run. Question and
  mechanism cross-cut, so the relation is one-to-many: one question can need
  several mechanisms (a card cited by more than one detector), and one
  mechanism can serve several questions (a detector cited by more than one
  card). The one-to-one invariant lives a level down, at the rule — every
  `card.rule` id belongs to exactly one card. A card may still audit `none`
  when no automatic check exists.
- **Thin shims.** A detector script stays a thin shim over the host repo's
  reusable modules (in dev-playbook, `src/dev_playbook`); the logic lives in the
  module, the script wires argument parsing and output to it.
- **Explicit roots outrank the hook environment.** Detectors run at git gates,
  and a hook inherits an absolute `GIT_DIR` whenever discovery from its own
  working directory would land on the wrong repository — always from a linked
  worktree, where agent work happens, and in submodule flows. It silently
  outranks `git -C <root>` and the working directory in every child process,
  redirecting git to the hook's repository instead of the audited one. A plain
  clone's hook exports no absolute `GIT_DIR`, so finding it absent there is not
  evidence the clause is stale. A detector that shells out to git therefore
  scrubs the redirecting variables from its subprocess environment; git names
  them itself through `git rev-parse --local-env-vars`, which stays correct
  across git versions. It leaves transport and auth settings such as
  `GIT_SSH_COMMAND` untouched but strips the `GIT_CONFIG_*` channel, through
  which ad-hoc config relocates a repository as readily as `GIT_DIR` does. dev-playbook detectors call `gitrepo.no_git_env`; a self-contained
  consumer detector cannot import it and either carries its own copy or runs
  `unset $(git rev-parse --local-env-vars)`, the remedy `githooks(5)` documents.
  The same variable makes a bare `git init` a silent no-op, so a detector's test
  suite clears the same set before every test (an autouse fixture in
  `tests/conftest.py`).
- **The hosting pattern.** A repo's detectors live at `scripts/<name>`, are
  published in that repo's own `.pre-commit-hooks.yaml`, and are mirrored in its
  `repo: local` block — dev-playbook is the topmost instance of this pattern. A
  repo that ships a manifest must run what it ships from its own local block;
  that dogfooding invariant is stated once in
  [Distribution Channel](/standards/distribution/channel.md#the-local-block-covers-the-manifest)
  and not restated here.
- **Card-namespaced rule ids.** Every finding carries a rule id of the form
  `card.rule`, namespaced by the card whose question it answers and named
  after that question — never after the tool that happens to detect it.
- **`--list-rules`.** Every detector answers `--list-rules`, printing the
  `card.rule` ids it can emit.
- **Two citation kinds in an Audit cell.** A cell cites a **lint** via a
  `/scripts/` link — a deterministic detector, held to the rule-matrix
  `--list-rules` contract — or an **audit** (an LLM judge) via a judgment link
  (`/standards/semantic-validation/…` or `/judgments/*.yaml`), which carries no script
  contract. The rule-matrix check scopes its citation collection to `/scripts/`
  links, so audit-kind citations are exempt by construction, not by exception.
  The [Semantic Validation](/standards/semantic-validation.md) card shows both:
  judgments-lint is the lint, the LLM judgments the audit.
- **Finding format.** A finding is one line, GNU format:
  `file:line: card.rule message` — a colon after the location, single spaces, a
  repo-relative path; `:line` is omitted for a file-level finding
  (e.g. `README.md: knowledge-organization.doc-shape missing an H1 title`).

### Verbatim content

A document whose body is a verbatim copy of an upstream external one
(`type: Reference`) is not the repo's to hold to the authored-content
standards. A detector excludes such a document by consulting the shared
registry `src/dev_playbook/external.py` (`is_verbatim_doc`) — never a
path-skip hardcoded in the detector — so every detector excludes the same
documents; the drift this norm forbids is an unsynced, undocumented
per-detector skip list.

## Drift

Standards drift, each grain with its own detector:

1. **Fine grain** — a specific document or passage must keep meaning what
   it meant when validated.
   [Judgments](/standards/semantic-validation/index.md) cover this: the
   content-addressed cache expires a verdict the moment the underlying
   bytes change.
2. **Contract grain** — a change to a define cell obligates rework across the
   standard's adopting population. For a workspace-scoped standard that
   population is every repo in the workspace: a version bump propagated and
   verified by workspace-lint. For a repo-scoped standard the adopting
   population is the host repo itself, so no workspace-lint obligation
   attaches — the rework lands in the same repo as the define-cell change.

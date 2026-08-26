---
type: Standard
title: Standards and Standard Cards
description: What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
---

# Standards and Standard Cards

Returning to a topic months later should not require re-deriving shared
understanding over several turns of conversation. Each standard therefore
gets a **standard card**: a small fixed-format record that tells a user or
agent where to look. The files it points at define the standard; the card
aggregates pointers so a thought that originates at the abstract level
("how do we do X here?") resolves to concrete files in one hop.

## What a standard is

A standard is named by the question it governs, not by the current answer.
"How knowledge is organized in markdown" is a standard; the OKF spec is
today's answer, pointed at by its define cell. The litmus: if the
implementation could be swapped while the name stays true, it is a
standard.

- **Membership is non-exclusive.** A file may belong to more than one
  standard at once. Standards are overlapping views over the repository,
  not a partition of it — pointers, not directory placement, say what
  belongs to what.
- **A standard may have sub-standards,** one level deep.

## What a standard is not

Not everything normative is a standard. A device built to serve a purpose
— an artifact format, a tool, a template — is an answer, so it belongs
inside a cell rather than in the catalog. Such devices are **instruments**;
each carries a prescriptive contract of its own, typed `Instrument-Spec`.
The instrument concept is defined in
[Instruments and Instrument Specs](/standards/instrument/format.md).

## Where a standard lives

A document typed `Standard` lives under `standards/`; nothing outside that tree
claims the label. okf-lint's `knowledge-organization.type-location` checks it.

This binds the type label, not membership — a card's define cell still points
wherever the contract is, and prose that governs without being a conformance
target takes another type.

## Scope

Every standard has a **scope** — the population it governs:

- **Workspace-scoped** — declared in dev-playbook, governing every repo in
  `~/workspace`. The bulk of the catalog is workspace-scoped: the
  cross-project standards every repo inherits through dev-playbook's published
  hooks.
- **Repo-scoped** — declared in one consumer repo, governing that repo alone.
  A repo stands one up when it has a convention no other repo shares; the
  recipe is
  [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md).

Exactly two levels — a standard governs the whole workspace or a single repo,
never an intermediate group. Deeper nesting is deliberately unsupported
(YAGNI): no third scope is introduced until a real population sits between
"one repo" and "every repo."

**No shadowing.** A repo-scoped card may not reuse a workspace-scoped card's
name. A consumer's `standards/<name>.md` may not collide with a card stem
dev-playbook publishes, because that would silently override the upstream
standard of that name; the rule `standard.card-shadows-upstream` catches the
collision at the consumer's commit gate.

## Naming

A standard's filename is kebab-case and names its topic as a noun: a plain
noun (`conventions.md`, `records.md`, `distribution.md`), a noun compound
(`cache-gate.md`, `context-content.md`), or a gerund compound
(`issue-authoring.md`) — never a bare verb
(`skill-write.md`). When a directory has an established family prefix, a
new sibling on the same subject keeps it.

## The card

A card is a markdown file at `standards/<name>.md` with
`type: Standard-Card` frontmatter: a heading, one sentence naming the
governed question, then exactly four cells as sections. That sentence
opens `Governs how`, names the territory its define cell covers, and runs
about a breath; the frontmatter `description` repeats it verbatim less the
period, so the catalog row and the card state the same remit.
standards-lint's `standard.card-question` checks the pairing. Each cell holds
annotated pointers; an empty cell states an explicit "none" so gaps stay
visible. Cards are thin — often just a handful of pointers — and never
restate the content of their targets.

- **Define** — the contract: prose documents and canonical reference
  files.
- **Audit** — read-only deviation detection: the detectors that report
  nonconformance without blocking anything.
- **Enforce** — blocking gates: the rungs where nonconformance stops the
  path to main, cited by fixed name (**commit gate**, **push gate**,
  **CI gate**), defined in [enforcement.md](/standards/build/enforcement.md).
  A cell cites the single rung where the detector is stationed — where its
  wiring lives (pre-commit hooks → the commit gate; tools that run only inside
  `make check` / `make check-judgments-cache` → the push gate); the hook pattern in enforcement.md's Map
  implies the echoes at the other rungs. Enforcement is automatic and
  continuously in effect; a code review is a one-time checkpoint, never an
  Enforce pointer.
- **Adopt** — anything that helps bring a repository into conformance,
  such as templates or migration procedures. Often "none": the generic
  path is an agent reading the define cell and fixing the repository.

The cards themselves are the examples: [Build](/standards/build.md) and
[Meta-Standard](/standards/standard.md) — the latter is this standard's own
card, since the meta-standard is an instance of the format it defines.

## The catalog

Each repo that carries cards has its own catalog at `standards/index.md`; in
dev-playbook that is [standards/index.md](/standards/index.md). okf-lint's
index rule forces a catalog to list every card with a matching description.

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
  [distribution.md](/standards/build/distribution.md) and not restated here.
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

### Externally-managed and verbatim content

Some content in a repo is not the repo's to hold to the authored-content
standards: an externally-managed vendored tree — a bundle mirrored in but not
maintained file-by-file — or a document whose body is a verbatim copy of an
upstream external one (`type: Reference`). A detector that can import the
registry excludes such content by consulting the shared registry
`src/dev_playbook/external.py` —
`is_externally_managed` for vendored roots, `is_verbatim_doc` for verbatim
mirrors — never a path-skip hardcoded in the detector. (The exception is a
detector whose configuration cannot import Python — ruff, shellcheck, and shfmt
today, whose exclude lists are static config — which keeps a hand-synced literal
mirror of the roots, carrying a comment that names `external.py` as the
authority.) The registry is the one
place an externally-managed root is declared, so every detector that can reach
it excludes the same trees; the drift this norm forbids is an unsynced,
undocumented per-detector skip list, not the acknowledged mirror.

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

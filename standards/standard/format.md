---
type: Standard
title: Standards and Standard Cards
description: What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
---

# Standards and Standard Cards

Returning to a topic months later should not require re-deriving shared
understanding over several turns of conversation. Each standard therefore
gets a **standard card**: a small fixed-format record that tells a human or
agent where to look. The card does not define the standard — the files it
points at do that. It aggregates pointers so a thought that originates at
the abstract level ("how do we do X here?") resolves to concrete files in
one hop.

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
— an artifact format, a tool, a template — is an answer, not a governed
question, and so belongs inside a cell rather than in the catalog. Such
devices are **instruments**; each carries a prescriptive contract of its
own, typed `Instrument-Spec`. The instrument concept is defined in
[Instruments and Instrument Specs](/standards/instrument/format.md).

## The card

A card is a markdown file at `standards/<name>.md` with
`type: Standard-Card` frontmatter: a heading, one sentence naming the
governed question, then exactly four cells as sections. Each cell holds
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
  `make check` / `make check-judgments` → the push gate); the hook pattern in enforcement.md's Map
  implies the echoes at the other rungs. Enforcement is automatic and
  continuously in effect; a code review is a one-time checkpoint, not
  enforcement, and never an Enforce pointer.
- **Adopt** — anything that helps bring a repository into conformance,
  such as templates or migration procedures. Often "none": the generic
  path is an agent reading the define cell and fixing the repository.

The living exemplars are the cards themselves: [Build](/standards/build.md)
and [Meta-Standard](/standards/standard.md) — the latter is this standard's own
card, since the meta-standard is an instance of the format it defines.

## The catalog

The catalog of all standards is [standards/index.md](/standards/index.md).
okf-lint's index rule already forces that index to list every card with a
matching description, so catalog completeness is enforced by the existing
hook suite rather than by new tooling.

## Detectors

A **detector** is the read-only check behind an Audit cell — it inspects the
repository against one or more standards and emits findings, never mutating the
repository and never blocking by itself (its runs at a gate are the audit
stationed there — that is Enforcement). This is the normative home of the
detector contract.

- **Read-only means mutating nothing git tracks.** A detector reports without
  changing the repository. Reaching outside the working tree does not disqualify
  it: workspace-lint queries GitHub over `gh api`, writing findings to stdout
  and a summary to stderr — reading remote state and mutating nothing git
  tracks — so it is read-only and belongs in an Audit cell.
- **Universal wiring; applicability lives inside the detector.** Every detector
  is wired in every repo — consumers run the full menu, never a subset. A
  detector whose surface is optional (skills) exits 0 silently when the surface
  is absent; every other detector asserts unconditionally and fails loud. A gap
  is never resolved by making a detector opt-in. (The one exception is a
  detector whose audited surface exists only in one repo — standards-lint
  audits the `standards/` tree, which only dev-playbook carries — so it is wired
  in that repo's local block alone.)
- **A card may have more than one detector.** Cards are organized by the
  question they govern; detectors by the mechanism they run. Question and
  mechanism cross-cut, so the relation is one-to-many, not one-to-one: one
  question can need several mechanisms (a card cited by more than one
  detector), and one mechanism can serve several questions (a detector cited by
  more than one card). The one-to-one invariant lives a level down, at the rule
  — every `card.rule` id belongs to exactly one card. A card may still honestly
  audit `none` when no automatic check exists.
- **Thin shims.** A detector script stays a thin shim over the reusable
  modules in `src/dev_playbook`; the logic lives in the module, the script
  wires argument parsing and output to it.
- **Card-namespaced rule ids.** Every finding carries a rule id of the form
  `card.rule`, namespaced by the card whose question it answers and named
  after that question — never after the tool that happens to detect it.
- **`--list-rules`.** Every detector answers `--list-rules`, printing the
  `card.rule` ids it can emit.
- **Two citation kinds in an Audit cell.** A cell cites a **lint** via a
  `/scripts/` link — a deterministic detector, held to the rule-matrix
  `--list-rules` contract — or an **audit** (an LLM judge) via a judgment link
  (`/standards/judgments/…` or `/judgments/*.yaml`), which carries no script
  contract. The rule-matrix check scopes its citation collection to `/scripts/`
  links, so audit-kind citations are exempt by construction, not by exception.
  The [Semantic Validation](/standards/semantic-validation.md) card shows both:
  judgments-lint is the lint, the LLM judgments the audit.
- **Finding format.** A finding is one line, GNU format:
  `file:line: card.rule message` — a colon after the location, single spaces, a
  repo-relative path; `:line` is omitted for a file-level finding
  (e.g. `README.md: docs.readme-missing …`).

### Externally-managed and verbatim content

Some content in a repo is not the repo's to hold to the authored-content
standards: an externally-managed vendored tree — a bundle mirrored in but not
maintained file-by-file — or a document whose body is a verbatim copy of an
upstream external one (`type: Reference`). A detector excludes such content by
consulting the shared registry `src/dev_playbook/external.py` —
`is_externally_managed` for vendored roots, `is_verbatim_doc` for verbatim
mirrors — never a path-skip hardcoded in the detector. The registry is the one
place an externally-managed root is declared, so every detector excludes the
same trees; a per-detector skip list is the drift this norm forbids.

## Drift

Standards drift at two grains, each with its own detector:

1. **Fine grain** — a specific document or passage must keep meaning what
   it meant when validated.
   [Judgments](/standards/judgments/index.md) cover this: the
   content-addressed cache expires a verdict the moment the underlying
   bytes change.
2. **Contract grain** — a change to a define cell obligates rework across
   adopting repositories. This is a version bump of the standard,
   propagated and verified by workspace-lint.

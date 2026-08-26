---
type: General-Sheet
title: Factory Survey
description: One session's full read of the software factory — a classification of its files, the intent they carry, and sketches for a possible native rewrite
---

# Factory Survey

Notes from a single session that read every software-factory file once,
written down before a deliberate pause. The factory phase of the
`no-more-slop` branch is parked. Same working-file conventions as
[the branch plan](/no-more-slop-branch-working-files/NO-MORE-SLOP.md): every
disposition and candidate here is a guess, and nothing binds until a ruling
elsewhere says it does.

Why parked: an outside source on software-factory patterns is expected
imminently, and the user intends to rewrite the factory anyway — so mapping
the CLOA primitives onto its *current* files looked like wasted effort. The
sketch that felt most promising when we stopped: distill the factory's
intent, design any new primitives against that intent, then re-author the
factory natively in them. That sequencing is a suggestion.

## The census

Clusters and dispositions are one reader's take, meant to speed navigation.

**Guides — `software-factory/`** (plus `README.md` and `index.md`,
directory furniture):

| File | Cluster | Role | Disposition sketch |
|---|---|---|---|
| `software-factory.md` | spine | the two-region state graph — definition (user-led) and factory (autonomous) — with a mermaid map | graph-content; the irreducible "Guide" core |
| `factory-operations.md` | spine | the operating contract: dispatch, permissions, worktrees, the node-skill contract, the review loop | mixed — graph-content, rules, and mechanics interleaved; the hub every other file cites |
| `user-checkpoints.md` | spine | every point the factory stops for the user; the merge prohibition | intent-carrier; short and largely clean |
| `review-contract.md` | protocol contract | what all three reviews obey: severities, citeability, findings-as-threads, cycle headers, dispositions, the report envelope | mixed — protocol rules + ~150 lines of `gh`/`jq` mechanics that read like a Script written as prose |
| `deviation-contract.md` | protocol contract | the three limiters, halt-commit-escalate, the PR-callout lane, the deviation ledger | intent-carrier; the ledger entry shape is artifact-schema-ish |
| `pr-feedback.md` | protocol contract | the comment surfaces a PR carries and the one thread query | mostly mechanics; the GraphQL read could plausibly be a bundled script |
| `tdd.md` | node craft | the test-first discipline `build` reads on `tests:yes` | intent-carrier; conditional required reading |
| `refactor-catalogue.md` | node craft | structural cues and moves; the step-size rule | intent-carrier; reads like reference material |
| `node-agent-and-skill-authoring.md` | node craft | authoring conventions for factory node agents and skills | Standard-in-disguise? `doc-pr-review` audits against it |

**Agents — `dotfiles/dot-claude/agents/`** (headless nodes, launched by
the traverse script):

| File | Cluster | Role | Disposition sketch |
|---|---|---|---|
| `build.md` | headless node | carries out a direct-mode issue against its brief; opus/xhigh | intent-carrier |
| `open-pr.md` | headless node | idempotently opens the issue's PR with an authored merge message; sonnet/low | small and clean |
| `bug-pr-review.md` | headless node | bug-hunting review, eight finder angles; sonnet/xhigh | template-instance — see the parameterized-contract note below |
| `code-pr-review.md` | headless node | brief-fidelity and convention review; sonnet/xhigh | template-instance |
| `doc-pr-review.md` | headless node | doc review with a one-hop coherence frontier; sonnet/xhigh | template-instance |
| `adjudicator.md` | headless node | settles Suggestion threads by an ordered routing; regenerates the merge message at convergence; opus/xhigh | intent-carrier; leans hardest on the contracts |

**Skills — `dotfiles/dot-claude/skills/`** (all single-file bundles, no
references/ or scripts/):

| File | Cluster | Role | Disposition sketch |
|---|---|---|---|
| `issue-overwatch/SKILL.md` | session skill | executes one issue's traverse inline, node by node, stopping at checkpoints | duplicates the Script's job in prose — a tension a rewrite might resolve |
| `agent-view-overwatch/SKILL.md` | session skill | fleet board: reads issue state, recommends launches, renders a glyph table | intent-carrier; the board format is artifact-schema-ish |
| `issue-review-claims/SKILL.md` | definition lens | adversarial audit of a brief's empirical claims, findings only | small and clean |
| `issue-review-simulation/SKILL.md` | definition lens | mentally builds the brief, reports where it would fail its implementer | small and clean |
| `wayfinder-to-build/SKILL.md` | bridge | turns a finished wayfinder map into a build epic and child stubs | intent-carrier; invokes /grilling and /codebase-design |

**Script:**

| File | Cluster | Role | Disposition sketch |
|---|---|---|---|
| `scripts/traverse-issue` (→ `src/dev_playbook/factory/traverse.py`) | orchestrator | the factory region's spine: per-issue lock, worktree, headless launches, verdict arithmetic over PR thread state | already the Script primitive; judgment lives only in the agents it launches |

## The durable intent

What the factory seems to be *for*, independent of its current file layout.
A rewrite would presumably preserve most of this:

- **Two regions.** User-led definition (idea → interview → ready issue with
  a brief) and an autonomous factory (build → review loop → merge-ready),
  joined at a user-approved release.
- **A deterministic spine.** Orchestration is code; every branch in the
  traverse is conditional logic, and judgment happens only inside launched
  agents. The review verdict is arithmetic over PR thread state — no agent
  takes it.
- **Durable state is the only memory.** Prompts are fully determined by
  what the issue and PR hold at launch; one writer moves the labels. The
  written artifacts — PR body sections, cycle headers, review threads, the
  deviation ledger — function as the state machine's registers.
- **Fixed protocols.** A review contract (two severities, a citeability
  rule, findings-as-threads), a deviation contract (three yes/no limiters,
  halt-commit-escalate), suggestion dispositions (ordered routing, a fixed
  reason vocabulary), and user checkpoints (the merge prohibition above
  all).
- **Typed reports.** Every headless node ends on a report envelope —
  `outcome: done|escalated`, a `gist`, counts. The
  [reports edge](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#reference-chain)
  carries this as-is.

## Primitive candidates the intent hints at

Ideas only. None has been proposed for a ruling, and the ontology's rule
still applies to every one — a type earns a noun only when it demonstrates a
verb interface, the way Standard did
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#reference-chain)):

- **A declared graph.** The fleet's state machine — regions, nodes, edges,
  dispatch table — today lives in prose+mermaid and is executed twice: once
  by the traverse script, once by `issue-overwatch` reading the prose. If
  the graph were declared data both consume, "Guide" might reduce to it.
  A verb like *traverse* could be its interface.
- **An artifact schema.** The PR body's mandatory sections, the
  cycle-header line, the envelope fields — schemas described in prose,
  checkable today only "by absence." Declared and lintable, they might
  dissolve the largest class in the accepted-residuals ledger
  (Written-artifact semantics). Verbs might be write/read/validate.
- **Generated runbooks.** The three reviewers share most of their text;
  `review-contract.md` even names its "two parameters" (review name, what
  counts as Blocking) that each supplies. A template plus parameter blocks,
  deterministically expanded, would resemble
  [Edge Encoding](/no-more-slop-branch-working-files/EDGE-ENCODING.md)'s
  plan of generating traces from in-file structure.
- **Scripts for mechanics.** The `jq`/GraphQL recipes agents currently
  re-type each run (posting a review, reading threads, resolving one)
  could become bundled scripts with `does → Script` edges. No new
  primitive — just relocation.

Also noticed: some "Guide" content states rules another runbook audits
against, which is what a Standard does; retyping those would shrink the
Guide census before any new noun is weighed.

## A possible sequence, when unparked

One sketch of how to avoid extending primitives and rewriting the factory
as two entangled efforts — sequence them instead:

1. **Requirements sheet.** Distill the durable intent into a short prose
   document the user vets, with no reference to the current file layout.
   Incorporate whatever the outside source (below) changes.
2. **Primitive design.** Weigh the candidates above against those
   requirements, one at a time, each ruled by the user — so the rewrite,
   if it happens, contains no ontology decisions of its own.
3. **Native re-authoring.** Express the factory in whatever primitives
   survive. Chains would then be born with the runbooks rather than extracted
   after the fact.
4. **Close-out.** Residuals to the ledger,
   [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
   and [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md)
   updated, then the lint plan — which by then would have real declared
   structure to lint.

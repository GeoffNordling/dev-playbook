---
name: frozen-doc-pr-review
description: Audits the documentation in an issue's PR against its brief and the doc standards — the copy frozen for the factory rebuild. Use when the frozen issue overwatch dispatches the doc track at a review stop.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# Doc & PR Review (frozen)

**Post-freeze additions are out of scope.** This contract was frozen while the
factory it describes is rebuilt, so the repo's standards and conventions move
ahead of it. Sections, labels, and lint rules this contract does not name — in a
brief, in a PR body, or in a standard — are outside your scope: never flag their
presence, their absence, or their contents.

Review the documentation in an issue's PR diff against its issue brief, the doc standards, and the documents around it, and attach your findings to the PR.

**Jurisdiction: docs, plus the PR body.** Findings post on the diff's non-spec markdown and prose artifacts, and on the PR body, for the presence check alone. Specs — `feat`/`req`/`dsn` items — belong to the spec instrument, and code files to the code track, which reviews in parallel with you; both are reference material: read them where the docs describe them, and post no findings on them. Judgment declarations under `judgments/` are ordinary docs here — a review may flag one as stale against the artifacts it names ([Maintenance](~/workspace/dev-playbook/standards/judgments/declarations.md#maintenance)); cache state is never a finding.

## Read first

Before doing anything else, read end-to-end:

- [review contract](~/.claude/skills/frozen-issue-overwatch/references/review-contract.md) — the stance, the green gate, the cycle count, the findings comment, the escalation boundary.
- [PR feedback](~/.claude/skills/frozen-issue-overwatch/references/pr-feedback.md) — every comment surface a PR carries, and the command that reaches each.
- [doc conventions](~/workspace/dev-playbook/standards/prose/conventions.md) — the contract every doc answers to, whatever the diff holds.

Then report: `READ: review-contract.md, pr-feedback.md, doc-conventions.md`. Proceed only after.

Your values for the contract's three parameters:

| Parameter | Value |
|---|---|
| Review name | `Doc review` |
| Staging filename | `/tmp/doc-review-<issue>.md` |
| Blocking | a missing PR-description section, a fidelity gap, a missed knock-on update, a contradiction between docs, a convention breach that matters |

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --json title,body,comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- The PR's existing feedback, across every surface — any prior doc-review cycle's findings, so you don't re-flag them.

## 2. Read what the diff calls for

The diff's content picks the standards that bind this review on top of the doc conventions. Read the ones it calls for, end-to-end, then report `READ: <what you read>`:

| The diff carries | Read |
|---|---|
| skills | [skill conventions](~/workspace/dev-playbook/standards/claude-code/skill-conventions.md) — the binding format, plus /writing-for-agents for the craft every skill answers to; and for a `phase:*` skill, [node-skill authoring](~/.claude/skills/frozen-issue-overwatch/references/node-skill-authoring.md) on top |
| standard cards | [the standard-card format](~/workspace/dev-playbook/standards/standard/format.md) |
| structure in question — frontmatter, indexes, cross-references | [the OKF docs](~/workspace/dev-playbook/standards/docs/index.md) |

## 3. Audit the change

Read the changed docs whole, not as hunks — the brief and the docs together — against the standards they answer to. Pin each finding to its file and line and the rule or criterion it breaches. All six dimensions are audited — the presence check against the PR body, the rest against the docs — and they are also the dimensions the comment enumerates when they come back clean.

- **The presence check**, first and mechanical. The PR body carries the
  three mandatory sections of the
  [merge-message recipe](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#the-merge-message-recipe)
  — `## Summary`, `## Deviation ledger`, `## Deferred` — with the explicit
  empty-markers (`No deviations.`, `Nothing deferred.`) accepted. A missing
  section is an automatic Blocking finding; absence is checkable, so this
  dimension involves no judgment call.
- **Brief fidelity.** Every acceptance criterion the docs answer to is satisfied, the desired behavior is captured with no silent gap, and nothing reaches past the brief's stated scope.
- **Doc conventions.** The prose conforms to doc-conventions.md — voice, structure, one rule per section, current-state only.
- **The doc-type contract.** Each changed doc does what its type declares — a standard states rules a reviewer could cite, a card stays thin pointers, an index lists and delegates, a README orients.
- **Semantic accuracy.** The doc reads true against the thing it documents — the code, artifact, or process it describes. Verify claims against that thing itself, not against plausibility.
- **Cross-document coherence.** After the change, the repo's docs must still read as one consistent body — editing one document knocks on to its semantic neighbors, and a missed knock-on update is as Blocking as a contradiction inside the diff. The deterministic linters already prove references resolve and indexes match frontmatter; your subject is meaning — whether what the neighbors say is still true.

**The coherence frontier.** The diff picks what you read beyond itself, one hop, three derivations — then you stop:

1. **Inbound** — docs that reference the changed docs (grep the changed paths repo-wide): each may now misdescribe what it points at.
2. **Outbound** — docs the changed docs reference: each claim the changed docs make about them must hold.
3. **Concept** — for each term, name, or rule the diff renames, redefines, or retires, grep repo-wide: every hit outside the diff is a candidate stale claim.

Read the frontier docs and check agreement with the diff. The frontier is one hop: a neighbor's own neighbors are out of bounds — a problem you suspect beyond it goes in the findings as a question or risk naming the doc, not another expansion. Generated and derived artifacts are off the frontier: anything under `readings/`, `*.html` datasheets, and the like are regenerated from source rather than hand-maintained — never flag them, not even as an out-of-scope follow-up.

## 4. Attach findings

Write and post the comment per the review contract, using your parameter values above. Then emit the terminal line and stop:

```
DONE: <repo>#<issue> · phase: <node> · doc findings on PR #<n>
```

## 5. Escalations

Your line:

```
ESCALATE: <repo>#<issue> · phase: <node> · <where you're stuck and the call you need>
```

Your blocks:

- **Green gate red.** The check gate fails — the PR sits over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.
- **No docs in the diff.** The diff carries no documentation — the doc track was dispatched on work outside its jurisdiction.

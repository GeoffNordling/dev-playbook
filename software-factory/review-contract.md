---
type: Guide
title: Review Contract
description: The contract the code and doc reviews run under — its parameters, green gate, findings comment, and escalation boundary
---

# Review Contract

What the code and doc reviews do once dispatched: the gate they run before
reading anything, the comment they leave behind, and the line between a finding
and an escalation. Which reviews run at a stop is
[factory-operations.md](/software-factory/factory-operations.md#the-review-stop);
how a pull request's existing feedback is read is
[pr-feedback.md](/software-factory/pr-feedback.md).

The bug review is a **partial citer**, bound only by the clauses it names at
their point of use — judgments, anchoring, and the escalation boundary. It runs
no gate, counts no cycle, and sets no Blocking severity, so the rest of this
document passes it by.

## The three parameters

A citing review supplies three values and inherits everything below them:

- **Review name** — the review's own name, `Code review` for instance. It heads
  the comment and it is what the cycle count counts.
- **Staging filename** — the `/tmp` path the comment body is written to before
  posting.
- **What counts as Blocking** — one line, and it differs by review: a code
  review's Blocking is not a doc review's.

## The stance

A review is an **audit only**. It never modifies the work under review, and the
verdict on its findings is not its to take — it posts them and stops. Defects
route back to the authoring node through the human's rework verdict, never
through the reviewer's hand.

The audit runs hands-off: finding problems is its output, not a reason to stop.

## The green gate

The review opens by running the gate — `make -C <subproject> check`, or
`make check` when the `Makefile` is at the repo root. Green: the audit proceeds.
Red: `build` opened a PR over a red tree, which is an escalation rather than a
review of broken work.

The gate is the whole of what the review runs; individual lint tools are never
run on their own. Where there is no `make check` to run, the audit proceeds.

## Judgments sit outside the review

The semantic judgment gate is settled once, at
[the judgments node](/software-factory/factory-operations.md#the-judgments-node),
after review approves. No review arms it and no review runs a judge: never
`make check-judgments`, never a bare `uv run pytest`. Where a review runs
`make check`, the gate is left skipped, and skipped-judgment lines in the output
are noise.

Until the judgments node runs, a stale or red cache is the expected condition,
not a defect. A review acts as though judgments do not exist: it skips any
`judgments/*.yaml` the diff touches, cites no judgment's claim, and mentions no
judgment, verdict, or cache state in any finding.

## The cycle

The cycle number is the count of prior comments headed with this review's own
name, plus one; another review's comments are not counted.

Cycles 1 and 2 are full reviews across the review's own dimensions. From cycle 3
on the review is a **lockdown**: its sole job is verifying the prior cycle's
Blocking findings are fixed, so it hunts no new findings — though anything
noticed incidentally is still reported.

## The findings comment

The body is staged in the review's staging file — writes inside the worktree are
denied, `/tmp` is allowed — and posted as one comment on the issue's PR with
`gh pr comment --body-file <path>`.

**The header carries the revision and the cycle.**
`## <Review name> — <sha> · cycle <n>`, using the short HEAD sha
(`git rev-parse --short HEAD`). Where the PR already carries a prior comment
under this review's name, the header reads
`## <Review name> — <sha> · cycle <n> (supersedes review of <prior-sha>)` and the
comment opens with a one-line disposition of each prior finding — resolved or
still open — so neither the human nor a later read treats stale findings as live.

**Every finding is a problem plus its fix**, grouped by severity: **Blocking**,
as the review defines it, or **Suggestion**, a non-disqualifying improvement.
Nothing unactionable is written — no "acceptable as written", "no action
needed", "just noting", and no explaining why a clean thing is clean; detail
belongs to Blocking and Suggestion findings alone. Genuine uncertainty is still
surfaced, as a question or risk naming the decision the human faces.

**A real problem outside the work's scope** is highlighted with a recommended
follow-up issue; the review never opens one itself.

**The clean dimensions are enumerated bare** — names only, no per-dimension
justification. Where the whole diff is clean, the comment says so plainly: a
clean review is a real outcome.

### Anchoring

Each finding is anchored to its location with a blob link —
`https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using
the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and
names the rule or criterion it breaches. A finding on a file the diff leaves
untouched anchors the same way.

A finding whose subject is not a repo file has no path to link. It anchors by
naming that subject and the rule that governs it, in place of the blob link.

### Worked examples

A well-formed finding: one problem, the action it calls for, the rule it
breaches, and a link that renders the code being talked about.

```markdown
**Blocking — silent fallback in `read_scheme()`**

[`label_scheme.py#L41-L47`](https://github.com/<owner>/<repo>/blob/<full-sha>/src/dev_playbook/label_scheme.py#L41-L47)
returns `{}` when the scheme file is missing, so a mistyped path reads as an
empty scheme and every caller sees zero labels instead of an error. Raise on
the missing file — python style's fail-loud rule forbids the defensive guard.
```

The same observation, malformed. It hedges instead of asserting, names no
action, cites no rule, anchors nowhere, and spends its second sentence
explaining that a clean thing is clean — so a reader can do nothing with it but
read it again.

```markdown
- `label_scheme.py` — the missing-file handling looks a bit defensive here,
  might be worth a look at some point. Otherwise this file is clean and
  well-organized.
```

## Escalation

Where the review cannot be produced at all, it surfaces the block and stops,
emitting a terminal `ESCALATE:` line per
[the terminal report contract](/software-factory/factory-operations.md#engagement).
Two blocks recur — a red green gate, and a missing PR or diff — and each review
states its own full list.

### Findings are not escalations

A problem the review can describe belongs in the findings comment. Escalation is
reserved for something stopping the review from being produced at all.

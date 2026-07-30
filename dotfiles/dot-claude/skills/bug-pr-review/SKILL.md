---
name: bug-pr-review
description: Runs a bug review over an issue's PR diff — eight finder angles, deduped without verification, at most eight findings posted as one PR comment; an audit that never edits code. Use when the issue overwatch dispatches the code track at a review stop.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# Bug PR Review

<!-- Intentionally mirrors Anthropic's retired native /code-review (medium tier); keep the sections lifted from it verbatim. -->

Hunt bugs in the PR diff through eight finder angles, dedup, and post the
findings as one PR comment. The review is an audit only: you never modify the
code under review, and the verdict on the findings is not yours to take — post
them and stop.

Review for **correctness bugs**: surface every plausible bug. Catching real
bugs matters more than avoiding false positives — err on the side of
surfacing.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree** (cwd `.claude/worktrees/issue-<issue>`); if
not, enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If
the worktree is gone, escalate (§5) — don't start a fresh tree.

`gh pr diff` — the diff under review (resolves the current branch's PR).
Treat this diff as the whole review scope; no PR or an empty diff is an
escalation (§5).

**Judgments are not yours.** Never run the repo's semantic judgment gate —
no `make check-judgments`, no bare `uv run pytest`, no judge. The user
settles those judgments at the end of the traverse, so a stale or red
judgment cache is the expected state here. Act as though judgments do not
exist: skip any `judgments/*.yaml` the diff touches, and let no finding
mention a judgment, its verdict, or its cache state.

## 2. Find candidates

Run the **eight finder angles** defined in
[finder-angles.md](references/finder-angles.md) — read it now — in sequence,
yourself, in THIS context; do NOT spawn subagents for them. Each angle
surfaces **up to 6 candidate findings** with `file`, `line`, a one-line
`summary`, and a concrete `failure_scenario`. Do NOT let one angle's
conclusions suppress another's — if two angles flag the same line for
different reasons, record both.

Pass every candidate with a nameable failure scenario through — finders that
silently drop half-believed candidates are the dominant cause of misses.

## 3. Dedup — no verify

Pool all candidates. Dedup near-duplicates only (same defect, same location,
same reason → keep one). Do NOT run verifiers; do NOT re-judge; do not drop
on uncertainty. Sort by severity — correctness bugs always outrank cleanup,
altitude, and conventions findings when the output cap forces a cut.

## 4. Post findings to the PR

Target **at least 4 findings**; cap at **8**, keeping the 8 most severe. If
fewer genuine findings exist, post what you have — do not invent to hit the
floor. A clean pass is a real outcome: say so plainly in the comment.

Stage the comment body in `/tmp/bug-review-<issue>.md` (worktree writes are
denied, `/tmp` is allowed), then post one PR comment with
`gh pr comment --body-file <path>`.

- **Head it `## Bug review — <sha>`**, using the short HEAD sha
  (`git rev-parse --short HEAD`) — that exact header, no other.
- **Rank findings most-severe first.** Each finding: `file:line`, its
  one-sentence summary, and its failure scenario. Anchor it with a blob
  link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`,
  using the full SHA from `git rev-parse HEAD` — so GitHub renders a code
  preview.

Emit the terminal line, then stop:

```
DONE: <repo>#<issue> · phase: pr-review · bug review on PR #<n> (<k> findings)
```

## 5. Escalations

Whenever you can't produce the review — no PR, an empty diff, the worktree
gone — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · phase: pr-review · <where you're stuck and the call you need>
```

Findings are not escalations. A bug you can describe goes in the §4 comment;
you escalate only when something stops you from producing the review at all.

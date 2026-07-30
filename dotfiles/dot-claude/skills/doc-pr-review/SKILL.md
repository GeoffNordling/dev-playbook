---
name: doc-pr-review
description: Audits the documentation in an issue's PR against its brief, the doc standards, and the adjacent docs it must agree with, and attaches findings to the PR. Use when the issue overwatch dispatches the doc track at a review stop.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# Doc & PR Review

Review the documentation in an issue's PR diff against its issue brief, the doc standards, and the documents around it, and attach your findings to the PR. The review is an audit only: you never modify the work under review, and the verdict on the findings is not yours to take — post them and stop.

**Jurisdiction: docs.** Findings post only on the diff's non-spec markdown and prose artifacts. Specs — `feat`/`req`/`dsn` items — belong to the spec instrument, and code files to the code track, which reviews in parallel with you; both are reference material: read them where the docs describe them, and post no findings on them. The audit runs hands-off; finding problems is its output, not a reason to stop.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- The PR's existing feedback — any prior doc-review cycle's findings; to avoid re-flagging, read every comment surface on the PR: its body, top-level conversation comments, review summary bodies, and inline diff comments. (`gh pr view --comments` shows the body and conversation but omits the inline diff comments, which live at `gh api repos/{owner}/{repo}/pulls/<pr>/comments`; review summaries are at `.../pulls/<pr>/reviews`.)
- [Doc conventions](~/workspace/dev-playbook/standards/prose/conventions.md) — the contract every doc answers to; read it always. By the diff's content, also read: [skill authoring](~/workspace/dev-playbook/software-factory/skill-authoring.md) when the diff touches skills; [the standard-card format](~/workspace/dev-playbook/standards/standard/format.md) when it touches standard cards; the [OKF docs](~/workspace/dev-playbook/standards/docs/index.md) when structure — frontmatter, indexes, cross-references — is in question.

## 2. Green gate

Run the gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root). Green: proceed to the audit. Red: the PR sits over a red tree — escalate (§5) rather than review broken work. Don't run individual lint tools yourself; where there's no `make check` to run, proceed to the audit.

**Judgments are not yours.** `make check` leaves the repo's semantic judgment gate skipped, and that is the whole gate you run — never `make check-judgments`, never a bare `uv run pytest`, never a judge. The user settles those judgments at the end of the traverse; until then the cache is expected to be stale or red, and any skipped-judgment lines in the gate output are noise. Act as though judgments do not exist: skip any `judgments/*.yaml` the diff touches, cite no judgment's claim, and let no finding mention a judgment, its verdict, or its cache state.

## 3. Audit the change

Read the changed docs whole, not as hunks — the brief and the docs together — against the standards they answer to. Pin each finding to its file and line and the rule or criterion it breaches.

**Know your cycle first.** The cycle number is the count of prior `## Doc review — …` comments on the PR, plus one; the code track's `## Code review — …` comments are not yours and don't count. Cycles 1 and 2 are full reviews across the dimensions below. From cycle 3 on, the review is a lockdown: its sole job is verifying the prior review's Blocking findings are fixed — don't hunt for new findings, though anything you notice incidentally still gets reported.

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

Stage the comment body in a `/tmp` file (e.g. `/tmp/doc-review-<issue>.md`) — writes inside the worktree are denied, `/tmp` is allowed — then post one PR comment with `gh pr comment --body-file <path>`.

- **Head it with the reviewed revision and the cycle.** `## Doc review — <sha> · cycle <n>`, using the short HEAD sha (`git rev-parse --short HEAD`) and the cycle number from §3. On a re-review — the PR already carries a prior `## Doc review — …` comment — head it `## Doc review — <sha> · cycle <n> (supersedes review of <prior-sha>)` and open with a one-line disposition of each prior finding (resolved / still open), so neither the user nor a later read treats the stale findings as live.
- **Every finding is a problem plus its fix.** State the believed problem and the action it calls for, grouped by severity — **Blocking** (a fidelity gap, a missed knock-on update, a contradiction between docs, a convention breach that matters) or **Suggestion** (a non-disqualifying improvement). Write nothing that isn't actionable: no "acceptable as written", "no action needed", "just noting", and no explaining why a clean thing is clean. Where you are genuinely unsure, raise it as a question or risk, naming the decision the user faces.
- **A real problem outside this PR's scope** — highlight it and recommend a follow-up issue; never open one yourself.
- Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or criterion it breaches; a coherence finding on an unchanged file anchors there the same way. Enumerate the clean dimensions bare — names only; if the whole diff is clean, say so plainly — a clean review is a real outcome.

Emit the terminal line, then stop:

```
DONE: <repo>#<issue> · phase: <node> · doc findings on PR #<n>
```

## 5. Escalations

Whenever you can't produce the review, surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · phase: <node> · <where you're stuck and the call you need>
```

In particular:

- **Green gate red.** The check gate fails — the PR sits over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.
- **No docs in the diff.** The diff carries no documentation — the doc track was dispatched on work outside its jurisdiction.

Findings are not escalations. A problem you can describe goes in the §4 comment; you escalate only when something stops you from producing the review at all.

---
type: General-Sheet
title: Residual Ledger
description: Per runbook, what its full rewrite could not express in the edge-encoding map — recorded at the moment of porting
---

# Residual Ledger

Per runbook ported to the
[Edge Encoding](/no-more-slop-branch-working-files/EDGE-ENCODING.md) map:
what the full rewrite could not express in it, recognized and written
down at the moment of porting. That is all an entry is — a record, not
a question awaiting a verdict.

An entry is a couple of sentences, hard limit: name each specific
action the file could not express and why the map cannot say it —
nothing else. No inventories of what fit, no family taxonomies, no
cross-references to other entries, no history, no restating the map's
rules.

## log-friction

Could not express the fire-and-forget behavior mode, the early exit
("and stop"), or the why-text calibrating judgment — no primitive for
any of the three.

## document-deslop

Partially ported; the Review section still waits. Could not express
"this skill never commits" (no primitive for a forbidden action) or a
report that one branch deliberately withholds.

## grill-with-docs

Could not express what is *not* overridden ("Everything else applies
as written") — no primitive asserts an edge's absence.

## usage-report

Could not express the script's own read of `usage.json` — a script has
no frontmatter or spans, so the does edge ends at the file.

## deslopper

Could not express being a Standard's enforce arm (flattened to a plain
read) or an agent's inputs — agents have no `arguments` frontmatter.

## handoff

Could not express the OS temp-directory write (the writes—scratch
hole) or telling the two reports apart — both render `outcome: str`.

## ralph-setup

Could not express the report's name (`launch_command` rides only in
annotation) or the mid-run `READ:` acknowledgment, which targets the
conversation, not the invoker.

## commit

Could not express committing the ambient repo — `git_detail()` demands
a `-C <repo>` no honest same-repo command carries — or the
skip-the-amend decision itself; only its report has a primitive.

## datasheet

Could not express the `.datasheet/` scratch write (writes—scratch
hole) or `griffe-outline` as a Script — `classify()` types scripts by
`.sh`/`.py`/`.bash` extension and it has none.

## clean-up-branch-worktree

Could not express the ambient-repo `git fetch`/`git merge`, the
`ExitWorktree` tool call (does covers only file-linked runbooks), or the
state-reading `git`/`gh` commands.

## idea

Could not express the delegation target's own behavior — the Run edge
resolves to mission-control's skill, outside the scanned corpus, so no
chain exists to stitch into — or the Overrides section, which binds
fixed values, not one linked runbook for another.

## rewind-compact

Could not express telling the two reports apart (both `outcome: str`).

## commit-off

Could not express forbidding an action ("run no `git commit`") or the
two exact-text mid-session acknowledgments — no primitive for either.
The chain is the bare node header.

## candidate-promote

Could not express reading the invoking repo's `CANDIDATES.md` —
`{Read}` needs one fixed on-disk link and the target changes per
invocation — or the typed report (`issue_number: int`) — reports
render only `outcome: str`.

## orchestrate

Could not express launching runtime-chosen subagents — `{Launch}`
needs a link to one agent file and none exists — or the persistent
session posture, which no primitive covers.

## intake

Could not express the GitHub issue writes (`gh issue create`/`edit`,
comments) — the writes—GitHub hole — the `gh issue view` read (no
on-disk link), or the mode→phase routing table (a table has no
sentence for the grammar to span). `software-factory.md` renders as
bare link text: `classify()` has no type for docs outside
`standards/`.

## runbook-creator

Could not express the interview loop of steps 2 and 6 (no primitive
for a question-and-answer round), the `scripts/harness-files-lint` run (bare
command, no link for a does edge), or the step-completion gates (no
control-flow primitive).

## working-doc-set-deslop

Could not express the pre-flight `git status` check (no on-disk link, so
no `{Read}`), forbidding commits (no primitive for a forbidden action),
or the closing user verdict — accept-and-commit versus
reject-and-restore-to-`HEAD` — which no primitive covers.

## doc-pr-review

Could not express the anchored reads (review-contract.md's gh-mechanics,
delta-re-review, findings-are-threads, resolution-ownership, and
findings-are-not-escalations sections; declarations.md's maintenance
section; factory-operations.md's merge-message recipe) — `{Read}` fails
on `#fragment` links. Could not express the review's central act —
auditing the docs in the diff and posting the findings as threads on
the PR, and resolving verified prior-cycle threads (`gh` writes, the
writes—GitHub hole). Could not express the diff-conditional standards
table in § Read what the diff calls for — a table has no sentence for
the grammar to span — or the `gh` state reads (PR threads, the diff
itself, the issue brief) — no on-disk link. The escalation bullets in
§ 6 restate the guard's condition rather than firing their own edges,
since the map has no primitive for enumerating alternative trigger
conditions under one guard.

## adjudicator

Could not express the `gh` state reads (issue, PR, threads, comments) or the
`gh api`/`gh issue create`/`gh pr edit`/`gh pr comment` writes — no on-disk
link for either hole. Could not express the routing test and its dispositions
(§3–§4), the ordered-first-hit routing, or the callout distinction — no
control-flow or enumeration primitive for any of them. Could not express the
prompt's issue-number and verdict-word input — agents have no `arguments`
frontmatter — or the `READ:` acknowledgment, which targets the conversation,
not the invoker.

## build

Could not express the `gh issue view` read (no on-disk link), the `gh api`
reply and the deviation-ledger's `gh issue create`/`gh pr edit` writes (the
writes—GitHub hole), the issue-number input (agents have no `arguments`
frontmatter), the open-ended "read the standard that governs the artifact"
instruction (an example-led rule, not an enumerable branch), telling the
escalation and completion reports apart (both render `outcome: str`), or
the gate runs (`make check`, §4 and §6) — a bare command in the ambient
repo, with no on-disk link for a does edge.

## design

Could not express the phase-label move (§8's `gh issue edit`,
`phase:design` → `phase:build`) or the other `gh issue`
reads/writes (no on-disk link, writes—GitHub hole), the
`EnterWorktree`/`ExitWorktree` tool calls and worktree/branch git
commands (does covers only file-linked runbooks, and none carries a fenced
`-C` block for `{Commit}`), the approval gate spanning §6 into §7
(guard containment can't cross sections), the area-discovery and
probe-picking interviews (no primitive for a question-and-answer round
with the user), or the `READ:` acknowledgment (targets the
conversation, not the invoker).

## judgments-sweep

Could not express dispatching the judge fan-out — `Workflow({ name: "judgments", … })`
is neither an Agent nor a Skill/Script link, so does has no primitive for a
Workflow call. `judgments-run` renders as bare link text, not a `Script` node:
`classify()` types scripts by `.sh`/`.py`/`.bash` extension and this one has
none.

## code-pr-review

Could not express the review itself — auditing the diff and posting the
findings as threads on the PR, and resolving verified prior-cycle
threads (`gh api` writes, the writes—GitHub hole; no primitive for the
audit act). Could not express the `gh` state reads (repo, PR list, brief,
threads, diff) — no on-disk link — the diff-conditional standards table
in § Read what the diff calls for, or the presence-check and
audit-dimension tables — a table has no sentence for the grammar to
span. The green-gate and PR/diff-missing
escalation bullets restate the guard's condition rather than firing their
own edges, since the map has no primitive for enumerating alternative
trigger conditions under one guard.

## compact-prep

Could not express step 2's "only if something stands out" condition —
the guard primitive gates a whole span, not a report's own contents.

## set-auditor

Could not express the set-member reads — the root and its linked working
files are runtime-bound (named in the launching prompt), so `{Read}`'s one
fixed on-disk link cannot cover them; they stay plain prose. No primitive
covers forbidding an action ("edit nothing, commit nothing, ask no
questions").

## agent-view-overwatch

Could not express the `gh issue view`/`gh pr list` state reads (no
on-disk link), the launch command handed to the user (no primitive for
an instruction the agent itself never runs), the teardown's
`git worktree remove`/`git branch -D` (writes—git bucket is scoped to
commits, not arbitrary git subcommands), or the board table (no
primitive for a rendered report's shape).

## bug-pr-review

Could not express the anchored reads inside review-contract.md (gh-mechanics,
delta-re-review, findings-are-threads, resolution-ownership,
findings-are-not-escalations) — `{Read}` fails on `#fragment` links — or the
`gh` state reads (PR threads, the diff itself) — no on-disk link. Could
not express the review's central act — posting the findings as threads
on the PR and resolving prior-cycle threads (`gh` writes, the
writes—GitHub hole). The eight finder angles and their dedup/tag steps
are procedure, not edges, so the map has nothing to encode there.

## set-deslopper

Could not express reading every set member — `{Read}` needs one fixed
on-disk link, and set membership is runtime-determined — or forbidding
the commit action itself (no primitive for a forbidden action).

## enable-repo-governance

Could not type `repo-lint`, `bootstrap-labels`, and `workspace-lint` as
Script nodes — `classify()` types scripts by extension and these have none,
so they render as bare `does` targets. Could not express the size-conditional
landing choice in § 5 (a decision, not a fixed condition to guard) or the
GitHub-token permission preflight, which has no primitive.

## user-intent-mini-interview

Could not express the anchored read of issue-authoring.md's build-leaf-brief
section — `{Read}` fails on `#fragment` links — or the `gh issue view` read
of the draft when `issue` is given (no on-disk link). Could not express the
ask/scrutinize/marry interview loop of steps 1–3 (no primitive for a
question-and-answer round) or the closing "writes nothing to GitHub"
assertion (no primitive for an edge's absence).

## issue-review-claims

Could not express the `gh issue view` reads of the issue body and its parent
epic (no on-disk link) or the forbidden actions — never edit files or the
issue, post nothing to GitHub (no primitive for a forbidden action). The
`disallowed-tools` frontmatter key sits outside the node-data set the header
renders (`tools`, `model`, `effort`, `allowed-tools`), so its edit/write ban
is silently absent from the chain.

## issue-overwatch

Could not express the anchored reads throughout (the briefing rule, the dispatch
table, readiness, the terminal report contract, the escalation rule, comment
surfaces, the two owners, turn boundaries — all `#fragment` links), the `gh`
state and write calls (issue view, blocked-by check, label moves, PR/issue
comments, stub creation — no on-disk link, the writes—GitHub hole), or the
`EnterWorktree` calls and worktree-only git commands (does covers only
file-linked runbooks). The AFK/Inline/Review-stop engagement switch, including
the fixed `/open-pr` launch inside the Review-stop branch, has no primitive
for a multi-way enumeration — encoding just that one branch would misstate it
as unconditional. The runtime-chosen `Run /<skill> <N>` delegation has no
fixed link for `{Launch}`.

## pocock-sweep

Could not express the `gh api` state reads (release tag, commit SHAs) or the
`gh pr create` write that opens the PR — no on-disk link for either, the
writes—GitHub hole. Could not express the scratch writes — the tag clone, the
optional cross-window plan file, and the hand-install route's bundle,
symlink, and lock-entry copies — all writes—scratch hole, nor the
`npx skills@latest`/`scripts/sync-dotfiles` calls, bare commands with no link
for a does edge. Could not express the commit-SHA branch that decides step
6's install route, or the branch-tip-versus-hand-install alternation itself —
both would guard a later section, and guard containment can't cross sections.
Could not express opening the worktree branch (no primitive for the
EnterWorktree tool call), the docket-ruling round with the user (no
primitive for a question-and-answer round), or the main-checkout commit that
lands the installs (no fenced git block to satisfy `{Commit}`'s block
requirement, since the staged files vary per sweep).

## open-pr

Could not express the anchored read — `{Read}` fails on `#fragment`
links, so the recipe link dropped its anchor — the `gh issue view` and
branch-diff reads (no on-disk link), the PR-body scratch write and
`gh pr create` (writes—GitHub/scratch hole), or the issue-number input
(agents have no `arguments` frontmatter). Three alternate reports all
collapse to `outcome: str`.

## update-standards-pin

Could not express the `git rev-parse`/`gh api` state read confirming the
release is pushed, or the report-format table in § Read the report (a table
has no sentence for the grammar to span, so its `/enable-repo-governance`
mention stays unencoded too). Could not express the ambient dev-playbook
commit for a release-defect fix or the per-consumer commit/push — the
writes—git bucket needs a fenced command with a fixed `-C`, and neither the
ambient nor the runtime-chosen consumer repo carries an honest one — or the
`pre-commit gc` cleanup, a bare command with no on-disk link for a does
edge.

## issue-review-simulation

Could not express the `gh issue view` state reads (title/body/comments,
the parent-epic lookup) or the read of whatever files the brief names —
`{Read}` needs one fixed on-disk link and all three are runtime-bound.
Could not express forbidding edits or GitHub writes (no primitive for a
forbidden action), or the `disallowed-tools` permission as node data —
only `tools`/`model`/`effort`/`allowed-tools` render in the header.

## wayfinder-to-build

Could not express the anchored reads (tracker-operations.md's wayfinding
section, issue-authoring.md's vertical-slice-rules and epic-body sections,
user-checkpoints.md's issue-review-verdict section) — `{Read}` fails on
`#fragment` links. Could not express reading the map issue and its child
tickets via `gh issue view` (no on-disk link), minting the build epic and
child stubs, or wiring sub-issue/blocked-by relationships (`gh` writes, the
writes—GitHub hole). Could not express the mid-run `READ:` acknowledgment
(targets the conversation, not the invoker) or the per-step "Done when"
completion gates (no control-flow primitive).

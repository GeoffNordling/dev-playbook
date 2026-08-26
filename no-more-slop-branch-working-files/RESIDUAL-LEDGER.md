---
type: General-Sheet
title: Residual Ledger
description: Per unit, what its full rewrite could not express in the edge-encoding map — recorded at the moment of porting
---

# Residual Ledger

Per unit ported to the
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
`ExitWorktree` tool call (does covers only file-linked units), or the
state-reading `git`/`gh` commands.

## idea

Could not express the delegation target's own behavior — the Run edge
resolves to mission-control's skill, outside the scanned corpus, so no
chain exists to stitch into — or the Overrides section, which binds
fixed values, not one linked unit for another.

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

## skill-creator

Could not express the interview loop of steps 2 and 6 (no primitive
for a question-and-answer round), the `scripts/skill-lint` run (bare
command, no link for a does edge), or the step-completion gates (no
control-flow primitive).

## working-doc-set-deslop

Could not express the pre-flight `git status` check (no on-disk link, so
no `{Read}`), forbidding commits (no primitive for a forbidden action),
or the closing human verdict — accept-and-commit versus
reject-and-restore-to-`HEAD` — which no primitive covers.

## doc-pr-review

Could not express the anchored reads (review-contract.md's gh-mechanics,
delta-re-review, findings-are-threads, resolution-ownership, and
findings-are-not-escalations sections; declarations.md's maintenance
section; factory-operations.md's merge-message recipe) — `{Read}` fails
on `#fragment` links. Could not express the diff-conditional standards
table in § Read what the diff calls for — a table has no sentence for
the grammar to span — or the `gh` state reads (PR threads, the diff
itself, the issue brief) — no on-disk link. The escalation bullets in
§ 6 restate the guard's condition rather than firing their own edges,
since the map has no primitive for enumerating alternative trigger
conditions under one guard.

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
commands (does covers only file-linked units, and none carries a fenced
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

## open-pr

Could not express the anchored read — `{Read}` fails on `#fragment`
links, so the recipe link dropped its anchor — the `gh issue view` and
branch-diff reads (no on-disk link), the PR-body scratch write and
`gh pr create` (writes—GitHub/scratch hole), or the issue-number input
(agents have no `arguments` frontmatter). Three alternate reports all
collapse to `outcome: str`.

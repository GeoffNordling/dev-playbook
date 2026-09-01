---
type: General-Sheet
title: Runbook Residual Ledger
description: Runbook's residual record — what the Reference chain cannot express, one entry per ported runbook
---

# Runbook Residual Ledger

Runbook's residual record: what the
[Reference chain](/doc-types/runbook/contract-shape.md)
cannot express. That is all an entry is — a record.

## Runbooks

Per runbook ported to the chain: what the full rewrite could not
express, recognized and written down at the moment of porting.
Entries name spans and keywords in the vocabulary
[encoding.md](/doc-types/runbook/encoding.md)
declares.

An entry is a couple of sentences, hard limit: name each specific
action the file could not express and why the map cannot say it —
nothing else. No inventories of what fit, no family taxonomies, no
cross-references to other entries, no history, no restating the map's
rules.

### Accepted classes

Residual classes ruled on and accepted as-is, one line each, so no run
raises the same question twice. A construct listed here is real but
deliberately outside the ontology until a ruling is reversed.

- **Reality probes** — direct shell contact with repo state ("run the
  gate", "confirm the git tree is clean"). A real operation; ruled not
  accounted.
- **Attestation checkpoints** — "report `READ: x`, proceed only after."
  A prompt device that raises the probability the read happens; ruled
  not accounted.
- **Agent-held ephemeral state** — counts and set-aside lists a runbook
  tracks only in its own working memory, persisted nowhere
  (judgments-sweep's fix-attempt cap and skip list); ruled not
  accounted.
- **User interview loops** — a mid-run, multi-round dialogue with the
  user (runbook-creator's "iterate until the user is satisfied";
  grilling's whole body). Conversing is what running in the calling
  context means; ruled not accounted.
- **Behavior-mode setting** — a runbook whose body installs standing
  behavior in the session's ephemeral context and fires no edge at
  invocation (orchestrate: "everything below you is a subagent").
  Ruled residual; admitting it later requires a lintable,
  deterministic form.
- **Presentation gestures** — opening an already-written artifact for
  the user (improve-codebase-architecture's `xdg-open` on its report);
  part of reporting the value, never an edge; ruled not accounted.
- **Phase gates** — a step-scoped prohibition inside a runbook's own
  program, lifted by a later step (improve-codebase-architecture's "Do
  NOT propose interfaces yet"); internal sequencing below the CLOA,
  already covered by the steps-are-the-program rule; ruled not
  accounted.
- **Written-artifact semantics** — the schema and state rules of a
  document a runbook writes and later re-reads: wayfinder's map-body
  sections, fog lifecycle, HITL/AFK axis, claim-by-assignment, ticket
  sizing. The artifact's contract lives in the artifact; the chain
  records only the writes and reads that touch it.

### log-friction

Could not express the fire-and-forget behavior mode, the early exit
("and stop"), or the why-text calibrating judgment — no primitive for
any of the three.

### document-deslop

Partially ported; the Review section still waits. Could not express a
report that one branch deliberately withholds.

### usage-report

Could not express the script's own read of `usage.json` — a script has
no frontmatter or spans, so the does edge ends at the file.

### deslopper

Could not express being a Standard's enforce arm (flattened to a plain
read) or an agent's inputs — agents have no `arguments` frontmatter.

### handoff

Could not express telling the two reports apart — both render
`outcome: str`.

### ralph-setup

Could not express the report's name (`launch_command` rides only in
annotation) or the mid-run `READ:` acknowledgment, which targets the
conversation, not the invoker.

### commit

Could not express committing the ambient repo — `git_detail()` demands
a `-C <repo>` no honest same-repo command carries — or the
skip-the-amend decision itself; only its report has a primitive.

### clean-up-branch-worktree

Could not express the ambient-repo `git fetch`/`git merge`, the
`ExitWorktree` tool call (does covers only file-linked runbooks), or the
state-reading local `git` commands.

### idea

Could not express the delegation target's own behavior — the Run edge
resolves to mission-control's skill, outside the scanned corpus, so no
chain exists to stitch into — or the Overrides section, which binds
fixed values, not one linked runbook for another.

### rewind-compact

Could not express telling the two reports apart (both `outcome: str`).

### commit-off

Could not express the two exact-text mid-session acknowledgments —
they target the conversation, not the invoker, and no primitive covers
them.

### candidate-promote

Could not express reading the invoking repo's `CANDIDATES.md` —
`{Read}` needs one fixed on-disk link and the target changes per
invocation — or the typed report (`issue_number: int`) — reports
render only `outcome: str`.

### grilling

Could not express dispatching the fact-finding sub-agent — `{Launch}` needs
a link to one agent definition file, and this is an unnamed, ad hoc
dispatch with none. Could not express the round-by-round design-tree loop
itself (no primitive for an iterative Q&A frontier) or the closing
"do not act on it until the user confirms" prohibition — it is
conditional on the user's confirmation, and the Never vocabulary has no
verb for acting.

### orchestrate

Could not express launching runtime-chosen subagents — `{Launch}`
needs a link to one agent file and none exists — or the persistent
session posture, which no primitive covers.

### intake

Could not express the mode→phase routing table (a table has no
sentence for the grammar to span). `software-factory.md` renders as
bare link text: `classify()` has no type for docs outside
`standards/`.

### runbook-creator

Could not express the interview loop of steps 2 and 6 (no primitive
for a question-and-answer round), the `scripts/harness-files-lint` run (bare
command, no link for a does edge), or the step-completion gates (no
control-flow primitive).

### working-doc-set-deslop

Could not express the pre-flight `git status` check (no on-disk link, so
no `{Read}`) or the closing user verdict — accept-and-commit versus
reject-and-restore-to-`HEAD` — which no primitive covers.

### doc-pr-review

Could not express the audit act itself — no primitive for it — or the
diff-conditional standards table in § Read what the diff calls for — a
table has no sentence for the grammar to span. The escalation bullets in
§ 6 restate the condition rather than firing their own edges,
since the map has no primitive for enumerating alternative triggers
under one condition.

### adjudicator

Could not express the routing test and its dispositions
(§3–§4), the ordered-first-hit routing, or the callout distinction — no
control-flow or enumeration primitive for any of them. Could not express the
prompt's issue-number and verdict-word input — agents have no `arguments`
frontmatter — or the `READ:` acknowledgment, which targets the conversation,
not the invoker.

### build

Could not express the issue-number input (agents have no `arguments`
frontmatter), the open-ended "read the standard that governs the artifact"
instruction (an example-led rule, not an enumerable branch), telling the
escalation and completion reports apart (both render `outcome: str`), or
the gate runs (`make check`, §4 and §6) — a bare command in the ambient
repo, with no on-disk link for a does edge.

### design

Could not express the
`EnterWorktree`/`ExitWorktree` tool calls and worktree/branch git
commands (does covers only file-linked runbooks, and none carries a fenced
`-C` block for `{Commit}`), the approval gate spanning §6 into §7
(condition containment can't cross sections), the area-discovery and
probe-picking interviews (no primitive for a question-and-answer round
with the user), or the `READ:` acknowledgment (targets the
conversation, not the invoker).

### judgments-sweep

Could not express dispatching the judge fan-out — `Workflow({ name: "judgments", … })`
is neither an Agent nor a Skill/Script link, so does has no primitive for a
Workflow call.

### code-pr-review

Could not express the audit act itself — no primitive for it — or the
diff-conditional standards table
in § Read what the diff calls for, or the presence-check and
audit-dimension tables — a table has no sentence for the grammar to
span. The green-gate and PR/diff-missing
escalation bullets restate the condition rather than firing their
own edges, since the map has no primitive for enumerating alternative
triggers under one condition.

### compact-prep

Could not express step 2's "only if something stands out" condition —
the condition primitive gates a whole span, not a report's own contents.

### set-auditor

Could not express the set-member reads — the root and its linked working
files are runtime-bound (named in the launching prompt), so `{Read}`'s one
fixed on-disk link cannot cover them; they stay plain prose. Could not
express "ask no questions" — the Never vocabulary has no verb for it.

### agent-view-overwatch

Could not express the launch command handed to the user (no primitive for
an instruction the agent itself never runs), the teardown's
`git worktree remove`/`git branch -D` (writes—git bucket is scoped to
commits, not arbitrary git subcommands), or the board table (no
primitive for a rendered report's shape).

### bug-pr-review

The eight finder angles and their dedup/tag steps
are procedure, not edges, so the map has nothing to encode there.

### set-deslopper

Could not express reading every set member — `{Read}` needs one fixed
on-disk link, and set membership is runtime-determined.

### enable-repo-governance

Could not express the size-conditional
landing choice in § 5 (a decision, not a fixed condition) or the
GitHub-token permission preflight, which has no primitive.

### user-intent-mini-interview

Could not express the
ask/scrutinize/marry interview loop of steps 1–3 (no primitive for a
question-and-answer round).

### issue-overwatch

Could not express the
`EnterWorktree` calls and worktree-only git commands (does covers only
file-linked runbooks). The AFK/Inline/Review-stop engagement switch, including
the fixed `/open-pr` launch inside the Review-stop branch, has no primitive
for a multi-way enumeration — encoding just that one branch would misstate it
as unconditional. The runtime-chosen `Run /<skill> <N>` delegation has no
fixed link for `{Launch}` — tabled: the factory's node-delegation process is
in flux and likely to be overhauled, so no encoding is attempted for it now.

### open-pr

Could not express the local branch-diff read
(`git diff origin/main...issue-<issue>` — no on-disk link) or the
issue-number input (agents have no `arguments` frontmatter). The
alternate reports all collapse to `outcome: str`.

### update-standards-pin

Could not express the report-format table in § Read the report (a table
has no sentence for the grammar to span, so its `/enable-repo-governance`
mention stays unencoded too). Could not express the ambient dev-playbook
commit for a release-defect fix or the per-consumer commit/push — the
writes—git bucket needs a fenced command with a fixed `-C`, and neither the
ambient nor the runtime-chosen consumer repo carries an honest one — or the
`pre-commit gc` cleanup, a bare command with no on-disk link for a does
edge.

### issue-review-simulation

Could not express the read of whatever files the brief names —
`{Read}` needs one fixed on-disk link and they are runtime-bound.

### improve-codebase-architecture

Could not express spawning the
anonymous exploration sub-agent — `{Launch}` needs a link to one agent
definition file, and this is an ad hoc Task-tool call with none.

### diagnosing-bugs

Could not express the redact-every-secret discipline, a behavior-mode
setting with no primitive. Could not express Phase 3's ranked-list check-in
(targets the conversation mid-run, not a terminal report) or the
throwaway-harness and captured-trace writes — menu options among Phase 1's
ten ways, so an unconditional scratch edge would misstate them. Could
not express the commit that carries the confirmed hypothesis — writes—git
bucket needs a fixed `-C <repo>` a same-repo commit can't honestly carry.

### wayfinder-to-build

Could not express the mid-run `READ:` acknowledgment
(targets the conversation, not the invoker) or the per-step "Done when"
completion gates (no control-flow primitive).

### research

Could not express spawning the background research agent — `{Launch}` needs
a link to one agent definition file, and this is an ad hoc, unnamed dispatch
with none. Could not express reading primary sources — `{Read}` needs one
fixed on-disk link, and the sources vary with the question asked.

### domain-modeling

Could not express cross-referencing the code — the files consulted vary
with the claim under test, so there is no single target to name.

### wayfinder

Could not express the dead `/setup-matt-pocock-skills`
reference, since no such skill exists in this corpus — kept verbatim as
adopted. Could not express invoking whatever skill the map's Notes section
names, or an effort overriding the plan-don't-do default from that same
section — both are resolved from map content at runtime, not a link to one
fixed runbook. Could not express the research-branch write
(`research/<name>`) — writes—git bucket needs a fixed `-C` command block,
and the branch name is chosen per ticket.

### prototype

Could not express committing the prototype to a throwaway branch —
`git_detail()` requires a fixed `-C` fenced command, and here the repo
and branch are chosen at runtime, not fixed.

## Acronyms

- **AFK** — Away From Keyboard: a run that proceeds without the user present.
- **HITL** — the user in the loop: a run that stops for the user.

---
type: General-Sheet
title: Runbook Residual Ledger
description: Runbook's residual record — what the chain cannot express, one entry per ported runbook
---

# Runbook Residual Ledger

Runbook's residual record: what the
[chain](/doc-types/runbook/contract-shape.md)
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
  tracks only in its own working memory, persisted nowhere; ruled not
  accounted.
- **User interview loops** — a mid-run, multi-round dialogue with the
  user (runbook-creator's "iterate until the user is satisfied";
  grilling's whole body). Conversing is what running in the calling
  context means; ruled not accounted.
- **Behavior-mode setting** — a runbook whose body installs standing
  behavior in the session's ephemeral context and fires no edge at
  invocation. Ruled residual; admitting it later requires a checkable,
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

Could not express being the runbook that fixes a Standard's findings
(flattened to a plain read) or an agent's inputs — agents have no `arguments` frontmatter.

### ralph-setup

Could not express the report's name (`launch_command` rides only in
annotation) or the mid-run `READ:` acknowledgment, which targets the
conversation, not the invoker. Could not express the reads of §5's chain —
the files vary with the plan, so no link names them — or its tripwire, a
threshold with no primitive. Could not express the gate runs of §6 and §7 —
a bare command in the target repo, with no on-disk link for a does edge — the
read-back of the checkpoint markers it just wrote, which inspects the file's
own text rather than firing an edge — or the `/ralph-checkpoint` mention in
§8, which names a skill the user invokes and this one never runs.

### commit

Could not express committing the ambient repo — `git_detail()` demands
a `-C <repo>` no honest same-repo command carries — or the
skip-the-amend decision itself; only its report has a primitive.

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

### grilling

Could not express dispatching the fact-finding sub-agent — `{Launch}` needs
a link to one agent definition file, and this is an unnamed, ad hoc
dispatch with none. Could not express the round-by-round design-tree loop
itself (no primitive for an iterative Q&A frontier) or the closing
"do not act on it until the user confirms" prohibition — it is
conditional on the user's confirmation, and the Never vocabulary has no
verb for acting.

### runbook-creator

Could not express the interview loop of steps 2 and 6 (no primitive
for a question-and-answer round), the `uv run playbook check` run (bare
command, no link for a does edge), or the step-completion gates (no
control-flow primitive).

### doc-deslop

Could not express the pre-flight `git status` check (no on-disk link, so
no `{Read}`), the stop on a hint that names no set or two, the
one-set-versus-child-sets decision it passes down (a condition on
the tree, with no link for `{If}` to read), or the closing user
verdict — accept-and-commit versus reject-and-restore-to-`HEAD` —
which no primitive covers.

### compact-prep

Could not express step 2's "only if something stands out" condition —
the condition primitive gates a whole span, not a report's own contents.

### doc-judge

Could not express the set-member reads — the head file and its linked
files are runtime-bound (named in the launching prompt), so `{Read}`'s one
fixed on-disk link cannot cover them; they stay plain prose. Could not
express "ask no questions" — the Never vocabulary has no verb for it.

### doc-repairer

Could not express reading every set member — `{Read}` needs one fixed
on-disk link, and set membership is runtime-determined.

### update-standards-pin

Could not express the exit-code routing table in § Probe the bump (a table
has no sentence for the grammar to span). Could not express the
`EnterWorktree` call that cuts the branch after a red probe, or the
`--no-verify` commits, the landing commit, and the push — the writes—git
bucket needs a fenced command with a fixed `-C`, and the runtime-chosen
consumer repo carries no honest one. Could not express `pre-commit gc` or
the PR the run ends on: a bare command and a `gh` call, neither with an
on-disk link for a does edge.

### improve-codebase-architecture

Could not express spawning the
anonymous exploration sub-agent — `{Launch}` needs a link to one agent
definition file, and this is an ad hoc Task-tool call with none.

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

### ralph-checkpoint

Could not express the blocker-versus-checkpoint branch on the workflow's
return value, or the zero-findings branch on the reviewer's, both runtime
data with no link for `{If}` to read. Could not express the `git log` runs
that name the segment — bare commands with no on-disk link — or the wait for
the user's ruling, which targets the conversation, not the invoker.

### ralph-checkpointer

Could not express applying the user's ruling to each finding, which is a
decision with no primitive.

### ralph-reviewer

Could not express running each task's Verify clause or reading each task's
sources — both are chosen per task, so there is no fixed target — or the
ranking itself, which is a decision with no primitive.


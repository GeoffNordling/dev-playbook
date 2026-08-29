---
name: working-doc-set-deslopper
description: Audits one working documentation set through three auditor slices, merges their reports, and fixes the set, committing nothing. Use when the working-doc-set-deslop skill dispatches its fork agent.
model: inherit
effort: xhigh
---

# Set Deslopper

Bring one working documentation set into conformance with the standards,
editing in place and committing nothing. The launching prompt names the
working directory and the set's root file.

## Audit

{Launch three [working-doc-set-auditor](~/.claude/agents/working-doc-set-auditor.md) subagents in
one message, `model: sonnet`, `effort: high`}. Each prompt names the working directory,
the set's root file, and that auditor's assigned sections:

- **Fact placement** —
  [one home per fact](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#one-home-per-fact),
  [one rule, one place](~/workspace/dev-playbook/standards/prose/conventions.md#one-rule-one-place),
  [point at canonical artifacts](~/workspace/dev-playbook/standards/prose/conventions.md#point-at-canonical-artifacts).
- **Set shape** —
  [shape](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#shape),
  [worklist](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#worklist),
  [buckets](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#buckets),
  [terms](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#terms),
  [acronyms](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#acronyms),
  [one concern per document](~/workspace/dev-playbook/standards/prose/conventions.md#one-concern-per-document).
- **Document prose** —
  [speculative voice](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md#speculative-voice),
  [one concern per document](~/workspace/dev-playbook/standards/prose/conventions.md#one-concern-per-document),
  [declare before use](~/workspace/dev-playbook/standards/prose/conventions.md#declare-before-use),
  [current state and next steps only](~/workspace/dev-playbook/standards/prose/conventions.md#current-state-and-next-steps-only),
  [open with purpose](~/workspace/dev-playbook/standards/prose/conventions.md#open-with-purpose),
  [lead with the edge case](~/workspace/dev-playbook/standards/prose/conventions.md#lead-with-the-edge-case-when-reach-is-surprising),
  [section formats](~/workspace/dev-playbook/standards/prose/conventions.md#how-to-decide-between-section-formats),
  [positive statement](~/workspace/dev-playbook/standards/prose/conventions.md#positive-statement),
  [person of address](~/workspace/dev-playbook/standards/prose/conventions.md#person-of-address),
  [name concepts once](~/workspace/dev-playbook/standards/prose/conventions.md#name-concepts-once-use-consistently),
  [heading casing](~/workspace/dev-playbook/standards/prose/conventions.md#heading-casing),
  [grammatical parallelism](~/workspace/dev-playbook/standards/prose/conventions.md#grammatical-parallelism).

Set shape and document prose both carry one concern per document — shape
judges it from the tree, prose from inside each file — and you adjudicate
where they disagree.

Each prompt carries two briefings the auditors would otherwise lack: the
set declares speculative voice, so a guess written as a guess is
conforming; and the worklist's Completed section is the standard's own
mechanism, never past-state residue.

## Repair

Merge the three reports, then work them finding by finding, placing each
fix by judgment.

1. **Edit only the set's members.** Nothing outside the set changes.
2. {Never {Commit}} — the uncommitted diff is the user's review.
3. Where a finding needs a ruling only the user can give, leave it
   unfixed and name it in the report.

## Report back

{Report: when the audits are clean, one line saying so; otherwise one
line per member changed and one line per finding left unfixed with the
reason}.

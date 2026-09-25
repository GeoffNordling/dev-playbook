---
type: General-Sheet
title: Stint Model
description: How a stint's target, its checks, and its agents fit together — one or more draft Standards in the workstream as a temporary target, wired to --check and not to the gate, two reviewers, and done as zero findings — decided with the user on 2026-09-25, with its diagram
---

# Stint Model

The model of one unattended stint, from its target to its yield, as
decided with the user on 2026-09-25 in the session "Think the system
through". It is a guess, per
[Drive Workstream](/workstreams/system/drive/WORKSTREAM.md), and the
`stint` command does not do all of it yet; the changes are in that
head file's Planned list.

## Diagram

```
you + attended principal ── write ──▶ workstream (a leaf)
                                      ├─ WORKSTREAM.md
                                      │   ├─ ## Done when ──▶ the workstream's draft Standard(s)
                                      │   └─ ## Stints    planned entry: loop + the rule ids it targets
                                      ├─ draft Standard(s) typed Standard, ids <workstream>.<slug>, no gate
                                      └─ check             check <rule-id>…; what --check runs

stint branch                          PLAN.md · PROGRESS.md

principal-0      reads the head file, the stint entry, PLAN.md ─▶ launch
┌ segment ────────────────────────────────────────────────────────────────────────┐
│ iter-k         does one task from PLAN.md                                       │
│                runs check ─▶ the workstream's draft Standard(s), deterministic  │
│                  ─▶ findings; any time, as often as it likes; no stop           │
│                commits ─▶ pre-commit gate: the permanent Standards              │
│                PROGRESS.md: done, or best effort + deviation + reason           │
└─────────────────────────────────────────────────────────────────────────────────┘
checkpoint   ┌─ driver runs check  the workstream's draft Standard(s), deterministic ─▶ findings ─┐
             ├─ verifier           the workstream's draft Standard(s), stochastic    ─▶ findings ─┤
             └─ plan reviewer      the segment against PLAN.md                       ─▶ report   ─┤
                                                                                                  ▼
principal-n      revises PLAN.md ─▶ continue · stop                   (done: zero findings from both)
                                                                                                  ▼
yield            ─▶ you: done · stuck · budget spent ─▶ verdict: advance · accept · delete

only the rules the stint targets are run · authority goes down only: you ▶ principal ▶ iterations
```

## Settled

- **A workstream's target is one or more draft Standards.** A
  [draft Standard](/workstreams/system/drive/WORKSTREAM.md#terms) is a
  file typed `Standard` in the workstream, held to the Standards about
  Standards. `## Done when` points at them. It differs from any other
  Standard only in its place and its wiring, and wiring is never the
  Standard's; whether it becomes a doc-type of its own is not decided.
- **Wiring is what makes a Standard permanent.** A Standard under
  `standards/` is wired to the pre-commit gate, and its deterministic
  rules must hold on every commit. A draft Standard is wired to
  `--check` only: its rules may fail at any time, and a failure is a
  signal toward the target, never a block.
- **On accept, each draft Standard is deleted or promoted.** A
  promoted one moves under `standards/` and is wired to the gate.
- **A rule id is `<workstream>.<slug>`**, such as
  `view-rename.no-kind-word`, the name of the workstream that holds it,
  and no two rules of one workstream's draft Standards share a slug.
- **A loop advances a leaf workstream only.** A workstream with
  children is never a stint's target, so every rule id names a leaf.
- **`check` sits beside the head file.** It runs the deterministic
  rules of the workstream's draft Standards, `check <rule-id>…`, prints one finding per failed
  member, and is what the stint's `--check` runs. It lives as long as
  the workstream does.
- **You and the attended principal write the target before launch**:
  the draft Standards, `check`, and the stint's entry.
- **A stint advances part of a workstream.** Its planned entry under
  `## Stints` names its loop and the rule ids it targets. Rules outside
  that list are not checked.
- **`PLAN.md` and `PROGRESS.md` are one stint's breakdown**, on its
  branch: the tasks, in segments, that one iteration each does. They
  are a level below the head file's worklist.
- **The pre-commit gate holds the permanent Standards** on every
  iteration's commit. An iteration has to pass the gate and nothing
  more.
- **An iteration may run `check` at any time.** Its output is a signal
  of direction, and no call stops on it. The driver's run at the
  checkpoint is the one that counts.
- **Findings usually go down over a stint, but not always.** They are optional and helpful
backpressure.
- **Two reviewers, each with one job.** The verifier judges each
  stochastic rule the stint targets as a classifier, one bool per rule per
  member, and returns findings. The plan reviewer reads the segment
  against `PLAN.md` for the big picture and returns a sorted report.
  Neither sees the other's output: both report to the principal, as
  peers, so that the verifier's verdicts reach the principal unfiltered.
- **Done is zero findings from both `check` and the verifier**, over
  the rules the stint targets. The driver decides it in code; the principal does
  not claim it. The loop will have a pressure release valve to allow the
  principal to pause and escalate to higher level if it feels the goal is unachieveable.
- **Authority goes down only.** You set the principal's target; the
  principal sets the iterations' tasks. The principal may revise
  `PLAN.md`, and never the draft Standards, `check`, or the stint's entry. A
  rule the principal judges wrong ends the stint as stuck, and you rule
  on it.
- **An agent that fails its task reports it.** A blocked iteration
  commits what it did, logs a deviation and its reason in
  `PROGRESS.md`, and exits. The stint continues, and the principal
  handles the deviation at the checkpoint. Only the principal stops a
  stint.

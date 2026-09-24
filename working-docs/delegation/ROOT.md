---
type: General-Sheet
title: Delegation Working Root
description: The root of the delegation set — how the user hands work to agents and takes it back, attended or unattended, the shape and words of that workflow, what is settled, what is open, and the worklist
---

# Delegation Working Root

This set is speculative: every member writes a guess as a guess, and every
member inherits that voice. The work is a standard workflow for delegation:
the user and an agent brief a piece of work, agents advance it, with the
user present or not, and the work comes back to the user for a verdict.
This root holds the ideas, the tracking, and the words of that workflow.
The machinery that runs an unattended stint, the Sandcastle pipeline, is
described in the nested
[sandcastle set](/working-docs/delegation/sandcastle/ROOT.md). The set
grew out of the parallel-fronts set, renamed on 2026-09-24 when its
question widened.

## Goal

The user delegates more and does less. Today the user drives one idea at a
time from inside a Claude Code session, holds what is in flight in their
head or in loose notes, and leaves compute budget unused. The guess: every
line of work is a workstream, advanced by a loop in stints, and most stints
run unattended while the user reads a board and checks in where a stint
has stopped. Every step has one standard procedure and one standard
Markdown format, so nothing is invented anew each time.

## Principles

- Bias for simplicity: take the simpler way until a more complex one
  proves its need. No queue, no push notification: a board the user reads
  and a procedure for checking in.
- One set of objects for both modes. An attended stint and an unattended
  stint advance the same workstream with the same loop and the same
  records; only whether the user is present differs.
- Markdown in designated places, never GitHub issues, for tracking work.
- Past decisions do not bind this set. A decision record that stands in the
  way is revised rather than worked around.

## Constraints

- New names do not carry "Ralph". The names that carry it now stay.
- Every repo in `~/workspace` is in scope. The procedure, formats, and
  tooling are workspace-scoped standards in dev-playbook; a workstream
  lives in the repo it changes.
- Nothing reaches `main` unattended. Every unattended stint ends with the
  user's verdict, and only the user brings its work in, pushes it, and
  merges it.
- An unattended stint has local version control only, and no GitHub. An
  agent in an attended stint keeps its GitHub access.
- Context is managed on purpose: no agent runs until its context window
  fills. An unattended stint is a run of iterations, each a fresh agent.

## Working with the user

The user holds the requirements and the approvals; the agent holds the
technical detail. Decisions are made at the level of the structure: a
Unicode diagram or a tree the user can see, never a wall of prose. The
agent reports in plain language and leaves out commands, flags, and
mechanism unless the user asks. It puts each question with a recommended
answer, at most four at once. It describes a test plan and gets the user's
approval before running it, and discusses results before acting on them.

## Terms

The words of the workflow, one meaning each, and the name of the
machinery an unattended stint runs on.

- **Workstream** — one line of work: an intent and its history. It holds
  the goal, the reasons, the boundaries, what was decided and tried, and
  what comes next, and it ends when the user accepts or deletes it. A
  workstream will be a doc-type, its one typed file the head of a
  directory that may hold documentation sets; this set is one.
- **Loop** — machinery: a shape of act, verify, and yield steps, defined
  once in a file typed [Loop](/doc-types/loop/definition.md) under
  `loops/`. It holds no goal and no history. A workstream is driven by a
  loop chosen for it, and one loop drives many workstreams.
- **Stint** — a bounded spend of effort advancing one workstream with its
  loop. An **attended** stint has the user in it, as in a session like the
  one that wrote this set: the most effective and the most costly. An
  **unattended** stint runs in a sealed container with no user, on the
  Sandcastle pipeline, and ends by yielding to the user.
- **Checkpoint** — a review point inside an unattended stint, after a
  block of iterations: the work is reviewed against the plan, and the plan
  is revised. It is the review the
  [Ralph checkpoint skill](/dotfiles/dot-claude/skills/ralph-checkpoint/SKILL.md)
  runs today.
- **Iteration** — one fresh-context agent that does one task of the plan,
  commits, and exits.
- **Sandcastle pipeline** — the machinery that runs an agent in a sealed
  container, described in
  [The Sandcastle Pipeline](/working-docs/delegation/sandcastle/pipeline.md).

The parallel-fronts words these replace are listed in
[the sandcastle set](/working-docs/delegation/sandcastle/ROOT.md#superseded-terms),
whose members still use them.

## Shape

The guess as it stands:

```
Loop                        loops/<name>.md — the shape: act · verify · yield
Workstream                  one line of work, its head file typed Workstream
├─ head file                Goal · Done when · Boundaries · Planned · Completed
│                           · the loop that drives it · the log of its stints
├─ documentation sets       whatever the work accumulates
├─ child workstreams        a subdirectory with its own head file
└─ stints                   bounded spends of effort, one after another
   ├─ attended              the user and Claude in a session
   └─ unattended            a sealed container, its own branch, no user
      ├─ plan               checkpoints × iterations, plus slack; a hard limit
      ├─ checkpoint 1       iterations 1..n → review → revise the plan
      ├─ checkpoint 2       …
      └─ yield → the user   verdict: advance again · accept · delete
```

## Settled

Decided with the user on 2026-09-24.

- **A workstream is a doc-type.** "Working documentation set" retires as a
  term. A documentation set stays a pattern of files, defined in its
  standard, and is not a doc-type. A workstream's typed file is its head
  file, and the documentation sets in its directory are its material, so
  no doc-type spans more than one file.
- **`working-docs/` becomes `workstreams/`**, named for its doc-type as
  `loops/` is.
- **A strand is a child workstream.** A subdirectory with its own head
  file has its own loop, stints, and verdicts; the word "strand" retires.
  The [sandcastle set](/working-docs/delegation/sandcastle/ROOT.md) is
  this set's first.
- **A loop is distinct from a workstream.** The loop is how, general and
  without memory; the workstream is what and why, particular and with
  history. The user chooses the loop that drives a workstream.
- **The brief is the workstream's head file.** The buckets a working
  documentation set has today (Goal, Planned, Completed, …) grow the
  fields an unattended stint needs, and every workstream carries them, so
  one object serves attended and unattended work alike.
- **An unattended stint is planned before launch** as checkpoints ×
  iterations, plus slack. At the hard limit the agent wraps up and yields.
  Wall-clock time and commit counts are not budgets; tokens would be
  welcome if an agent can measure them.
- **A stint ends by yielding to the user** when the done-when holds, the
  budget runs out, or the agent is stuck. The user's verdict is one of
  three: advance again, accept, or delete. Deleting a workstream and
  starting fresh is possible and unusual.
- **Advance again continues from the tip.** The next stint starts a new
  branch from where the last one stopped. A branch may start from another
  unmerged branch.
- **No queue and no push.** A script reads the workstreams and the live
  stints and prints a board, ✈️ for running and 💤 for waiting on the
  user, and any agent can run it from the command line. What the board
  tracks is open.
- **The tracking standard splits in two.** GitHub issues become one way
  to track work among several, in their own section; this workflow is
  another, and the two do not tangle.
- **The Ralph checkpoint skill serves both modes.** It is refactored, by
  progressive disclosure, to run in an attended stint as it does today and
  inside an unattended one.
- **A coordinator agent advises only.** The user runs it; it reads the
  board, says which workstreams need the user, and drafts head files and
  verdicts. It launches nothing.
- **The Loop working set folds in when the first Loop is written.**
  [`doc-type-system/loop/`](/working-docs/doc-type-system/loop/ROOT.md)
  is where the unattended stint's Loop gets written, not beside it.

## Open

Each question with the agent's recommendation, to be decided from the
[Shape](#shape) diagram.

- **Who rules at an unattended checkpoint.** The reviewer ranks findings
  and no user is there to confirm them. The checkpointer rules against the
  head file, a separate judge rules, or every finding is accepted; in each,
  a finding the head file cannot settle stops the stint as stuck.
  Recommended: the checkpointer rules and records every ruling in the
  progress file.
- **The head file's name.** `ROOT.md` or `WORKSTREAM.md`. Recommended:
  `WORKSTREAM.md`, named for its type as `SKILL.md` is, so the board finds
  workstreams by name alone.
- **The head file's fields.** What Goal, Planned, and Completed gain:
  done when, boundaries, the loop, the plan shape, the base branch, what
  to read first, the stint log.
- **What the board tracks.** For each stint: its workstream, branch,
  state, checkpoints and iterations done against planned, why it stopped,
  where it runs, its log. Recommended: one row per stint running or
  waiting, grouped by workstream.
- **How a workstream names its loop.**
- **Where the driver and the integrator go.** Whether the program that
  runs an unattended stint and the role that brings its work in need
  names of their own, or are the Sandcastle pipeline and the user.
- **A workstream's target as a Standard.** A loop's target lives in the
  Standards its verify steps point at, and a workstream could hold its
  done-when as a draft Standard. Parked by the user.

## Planned

Sessions with the user come first, each at a high level, the agent
guiding. Running an unattended stint is the
[sandcastle set's worklist](/working-docs/delegation/sandcastle/ROOT.md#planned).

- **Decide the Open questions from the diagram.** A diagram of the system
  in this set, and each item of [Open](#open) settled at that level.
- **Write the Workstream doc-type.** Its definition and encoding under
  `doc-types/workstream/`, its entry in
  [Document Types](/standards/knowledge-organization/document-types.md),
  and a conventions Standard with checks.
- **Retire "working documentation set".** `working-docs/` renamed to
  `workstreams/`, each head file renamed,
  [Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
  rewritten as the Workstream's rules, the exemptions the other rules
  grant a working set reworded, and every link fixed.
- **Split the tracking standard.** GitHub tracking and workstream
  tracking, each in its own section of
  [`standards/tracking/`](/standards/tracking/index.md).
- **Write the unattended stint's Loop.** The first file in `loops/`,
  written by folding in
  [`doc-type-system/loop/`](/working-docs/doc-type-system/loop/ROOT.md).
- **Refactor the Ralph checkpoint skill** for attended and unattended
  stints, by progressive disclosure.
- **Build the board script.** It reads the head files and the live stints
  and prints the ✈️/💤 board.
- **Build the coordinator agent.** Advisory only.

## Completed

- **Design the delegation workflow.** Done 2026-09-24: a grilling session
  with the user set the five terms, the [Shape](#shape), and everything
  under [Settled](#settled), and renamed this set from `parallel-fronts`.
- **Separate the machinery.** Done 2026-09-24: the Sandcastle members
  moved into the nested
  [sandcastle set](/working-docs/delegation/sandcastle/ROOT.md), so this
  root holds the workflow and that one holds how an unattended stint runs.
- **Check overlap with active branches.** Done 2026-09-24: `main`'s
  refactor is merged into this branch, and no active branch conflicts
  with it.

## Acronyms

None.

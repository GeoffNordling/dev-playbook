---
type: Workstream
title: Drive Workstream
description: The head file of the Drive child workstream — work advances without the user always in the loop, in stints the user briefs and rules on, attended or unattended, with the built stint command as its tool; the shape of that workflow, what is settled, and the worklist
---

# Drive Workstream

The child workstream that drives work without the user always in the
loop. This workstream is speculative. The work is a
standard workflow: the user and an agent brief a piece of work, agents
advance it, with the user present or not, and the work comes back to
the user for a verdict. This head file holds the ideas, the tracking,
and the shape of that workflow.

The `stint` command runs one unattended stint in sealed Sandcastle
containers, from launch to its end, as described in
[Running a Stint](/guides/running-a-stint.md). It is a tool this
workstream's unattended stints run on.

## Goal

The user delegates more and does less: stints run unattended, and the
user gives verdicts from a board. Today the user drives one idea at a
time from inside a Claude Code session, holds what is in flight in their
head or in loose notes, and leaves compute budget unused. The guess: every
line of work is a workstream, advanced by a loop in stints, and most stints
run unattended while the user reads a board and checks in where a stint
has stopped. Every step has one standard procedure and one standard
Markdown format, so nothing is invented anew each time.

## Done when

The first unattended stint on a real workstream yields to the user and
gets a verdict.

## Principles

- Bias for simplicity: take the simpler way until a more complex one
  proves its need. No queue, no push notification: a board the user reads
  and a procedure for checking in.
- One set of objects for both modes. An attended stint and an unattended
  stint advance the same workstream with the same loop and the same
  records; only whether the user is present differs.
- Markdown in designated places, never GitHub issues, for tracking work.
- Past decisions do not bind this workstream. A decision record that stands in the
  way is revised rather than worked around.
- Predicates, not fixes. An idea for how the system should be is
  written as a goal, a predicate, or an objective, never carried out as
  an instruction; the fix follows when an accepted predicate fails its
  verifier.
- A Loop document for every loop, one a script runs included.

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

### Working with the user

The user holds the requirements and the approvals; the agent holds the
technical detail. Decisions are made at the level of the structure: a
Unicode diagram or a tree the user can see, never a wall of prose. The
agent reports in plain language and leaves out commands, flags, and
mechanism unless the user asks. It puts each question with a recommended
answer, at most four at once. It describes a test plan and gets the user's
approval before running it, and discusses results before acting on them.

## Terms

The words of the workflow, workstream, loop, yield, stint, driver,
principal, iteration, segment, and checkpoint, are the repo's
([CONTEXT.md](/CONTEXT.md#workstreams-and-loops)), since the doc-types
and [Running a Stint](/guides/running-a-stint.md) use them too, and
so is [draft Standard](/CONTEXT.md#governance), since the Standards
about Standards use it. This head file coins none.

### Shape

The guess as it stands:

```
Loop                        loops/<name>.md — the shape: act · verify · yield
Driver                      a program from the driver menu that runs a loop
Workstream                  one line of work, its head file typed Workstream
├─ head file                the headings picked from the menu
├─ documentation sets       whatever the work accumulates
├─ child workstreams        a subdirectory with its own head file
└─ stints                   bounded spends of effort, one after another,
   │                        each with its own loop and driver
   ├─ attended              the user and Claude in a session
   └─ unattended            a sealed container, its own branch, no user
      ├─ plan               checkpoints × iterations, plus slack; a hard limit
      ├─ checkpoint 1       iterations 1..n → review → revise the plan
      ├─ checkpoint 2       …
      └─ yield → the user   verdict: advance again · accept · delete
```

## Settled

Decided with the user on 2026-09-24.

- **A workstream is a doc-type.** A documentation set stays a pattern of files, defined in its
  standard, and is not a doc-type. A workstream's typed file is its head
  file, and the documentation sets in its directory are its material, so
  no doc-type spans more than one file.
- **Workstreams live under `workstreams/`**, named for their doc-type
  as `loops/` is.
- **A child workstream is a subdirectory with its own head file.** It
  has its own loop, stints, and verdicts.
- **A loop is distinct from a workstream.** The loop is how, general and
  without memory; the workstream is what and why, particular and with
  history. The loop and the driver belong to a stint, not to the
  workstream: the user chooses them for each stint, and the workstream's
  Stints heading records which ran.
- **The brief is the workstream's head file.** One object serves attended
  and unattended work alike.
- **A workstream picks its headings from one menu.** The user and the
  agent pick the ones the work needs. The menu is
  [Headings from the registry](/standards/doc-type/workstream-conventions.md#headings-from-the-registry).
- **Open holds questions only.** An answer, recommended or not, is a
  separate thing and does not sit with the question.
- **The Ralph pattern has four parts**, and every driver keeps them:
  1. The plan is written in the standard format. An attended principal
     makes it; an unattended principal is given it.
  2. Independent fresh-context iterations each do one chunk.
  3. A fresh-context reviewer compares what was done with the plan, sorts
     its findings, and returns them to the principal, which supplies taste
     and judgment. The sorting is how the pattern scales: the user rules
     on the top findings only, since no user can read everything agents
     report, and ruling on a sorted list calibrates the user's taste.
     In an unattended stint this reviewer is the plan reviewer, and a
     second one, the verifier, judges the target's stochastic rules
     ([Stint Model](/workstreams/system/drive/stint-model.md)).
  4. The principal changes the plan on the iterations' and the reviewer's
     reports, so the entity that manages the plan is the one that changes
     it.
- **An unattended principal keeps the whole stint in its own context,
  and never forks.** It knows the history of what it is doing because it
  lived it. The attended Ralph, which changes the plan through a fork of
  the top session, stays as it is, and the unattended driver is built
  separately.
- **The drivers form a menu.** Today: the Ralph workflow, which runs in a
  Claude Code session through the `Workflow` runtime
  ([`ralph-loop.js`](/dotfiles/dot-claude/workflows/ralph-loop.js)), and
  the `stint` command, which runs an unattended stint to its yield
  ([Running a Stint](/guides/running-a-stint.md)).
- **A headless agent never runs a Claude Code workflow.** An unattended
  stint's driver is headless code the user writes and maintains, as a
  professional practice, even where a headless agent could run a
  workflow. The Ralph pattern (fresh agent, status, stop rule,
  checkpoints) is written in Python as the `stint` command, and every
  call it makes runs in a sealed container, never on the host. Decided
  2026-09-24.
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
  user, and any agent can run it from the command line.
- **The tracking standard splits in two.** GitHub issues become one way
  to track work among several, in their own section; this workflow is
  another, and the two do not tangle.
- **A coordinator agent advises only.** The user runs it; it reads the
  board, says which workstreams need the user, and drafts head files and
  verdicts. It launches nothing.
- **Workstream and Loop are built doc-types.** Both live under
  [`doc-types/`](/doc-types/index.md), in the closed doc-type system;
  this workstream holds only the workflow that uses them.
- **The `stint` command is the driver of an unattended stint.** It
  supports this workstream as a tool.
- **The unattended principal rules on the findings itself.** It judges
  the reviewer's sorted findings against the head file's Goal, Done when,
  and Constraints, and writes each ruling in the progress file, so the
  user sees every ruling at the yield. A finding the head file cannot
  settle ends the stint as stuck.
- **The unattended principal is one headless Claude session.** The
  driver resumes the same session at each checkpoint, so its context
  holds the whole stint, and it runs sealed like every other call.
- **The context-window risk is accepted.** The principal takes in every
  report of the stint, which may break the constraint that no agent runs
  until its context fills. The stint's hard limit bounds it; a better
  answer waits for a real stint to show the need.
- **The head file is `WORKSTREAM.md`**, named for its type as `SKILL.md`
  is.
- **The board shows one row per stint running (✈️) or waiting (💤)**:
  its workstream, its branch, the checkpoint reached, such as "2 of 3",
  and why it stopped. Nothing more for now.
- **The user brings a stint's work in.** No term names the role.
- **A stint's plan is `PLAN.md` and `PROGRESS.md`** beside the head file
  on the stint's branch, as a Ralph run keeps them today. At the verdict,
  the stint's entry under Stints records the outcome.
- **A workstream's target is one or more draft Standards.**
  `## Done when` points at them, they are wired to `--check` and not to the
  gate, and a stint targets some of their rules. The whole model of a
  stint, decided 2026-09-25, is
  [Stint Model](/workstreams/system/drive/stint-model.md).

## Open

None.

## Planned

In order of dependency: each item needs the ones above it, except
where it says otherwise. The design is
[Stint Model](/workstreams/system/drive/stint-model.md), and a session
is with the user, at a high level, the agent guiding. An unattended
stint runs with the `stint` command
([Running a Stint](/guides/running-a-stint.md)).

- **Run the pre-commit gate in the stint's work copy.** Everything
  below needs it: without the gate, no call holds the permanent
  Standards, and `--check` cannot become the target check. Today no
  hook runs on an iteration's commit: the work copy is a plain
  `git clone` (`src/dev_playbook/stint/workcopy.py:267`), which copies
  no hooks, and the image has no `pre-commit`
  (`src/dev_playbook/stint/Containerfile`). The iteration prompt runs
  `--check` as the only gate instead
  (`src/dev_playbook/stint/prompts/iteration.md.in:18`). The fix: the
  image gets `pre-commit`, the hooks are installed in the work copy
  after it opens, inside the container, and the hook environments are
  cached across calls, since every call is a fresh container and the
  hook set comes from each target repo's `.pre-commit-config.yaml`,
  so the image cannot build them in advance.
- **Put the draft Standard in the doc-type system.** It does not wait
  on the gate. In order:
  - **Teach the Workstream doc-type the target.** `## Done when` links
    the workstream's draft Standards, a stint names the rule ids it
    targets, a new `targets` field of the `Stint` part, and only a leaf
    workstream has a stint, in the Workstream doc-type and
    [Workstream Conventions](/standards/doc-type/workstream-conventions.md).
  - **Fix the goal wherever it is stale.**
    [Writing Predicates](/guides/writing-predicates.md) says a goal
    lives in an issue, and the terms in [CONTEXT.md](/CONTEXT.md)
    still say so; both follow the model.
- **Bring the `stint` command to the model.** `--check` becomes the
  target check, which iterations may run at any time and the driver
  runs at each checkpoint; the checkpoint runs the verifier and the
  plan reviewer; the driver decides done as zero findings; and a
  blocked iteration logs a deviation and exits, so the stop rules
  `iter-k blocked` and `iter-k committed nothing` go, and
  [Running a Stint](/guides/running-a-stint.md) follows.
- **Write the stint's Loop.** The first file in `loops/`. In order:
  - **Design what a stint returns.** A session. Inside the container,
    iterations and checkpoints write files on the stint's branch:
    `PLAN.md`, `PROGRESS.md`, commits, and the head file's worklist
    moves. The design settles which of these come back when the
    container stops, which stay on the branch, and which reach `main`
    only on an accept. It also settles who writes the stint's entry
    under `## Stints`, and when: the container at the yield, or the
    driver after the user's verdict, since a verdict exists only after
    the yield.
  - **Write the Loop.** The checkpointed loop of
    [Stint Model](/workstreams/system/drive/stint-model.md), from the
    segment to the yield, as a graph that names no workstream.
- **Build the board script.** It reads the head files and the live
  stints and prints the ✈️/💤 board.
- **Build the coordinator agent.** Advisory only; it reads the board.
- **Decide what an objective is to a workstream.** A session, and it
  waits on nothing above. An idea written down takes one of three
  forms: a goal, spent when it is met, now a workstream's draft
  Standards; a predicate, standing, a rule in a Standard; or an
  objective, standing, a scalar descended under the predicates. Where
  an objective sits in a workstream or a loop is not decided.

## Completed

- **Let a draft Standard live in a workstream.** Done 2026-09-25: the
  user ruled it a plain `Standard`, not a doc-type of its own.
  [Standard Conventions](/standards/doc-type/standard-conventions.md)
  now binds it, with the leaf workstream's directory name as its rule
  ids' family;
  [Workstream Files](/standards/knowledge-organization/documentation-sets/workstream-files.md)
  keeps it in a leaf and each leaf's name unique; and the term moved to
  [CONTEXT.md](/CONTEXT.md#governance). The gate reads rules under
  `standards/` only, so nothing under `workstreams/` is wired to it.
- **Design the delegation workflow.** Done 2026-09-24: a grilling session
  with the user set the five terms, the [Shape](#shape), and everything
  under [Settled](#settled), and renamed this workstream from `parallel-fronts`.
- **Decide the Open questions from the diagram.** Done 2026-09-24: the
  diagrams of a driven Sandcastle stint and of today's attended Ralph
  settled every question, recorded under [Settled](#settled).
- **Separate the machinery.** Done 2026-09-24: how an unattended
  stint runs became the `stint` command and its guide,
  [Running a Stint](/guides/running-a-stint.md), and this workstream
  holds the workflow.
- **Check overlap with active branches.** Done 2026-09-24: `main`'s
  refactor is merged into this branch, and no active branch conflicts
  with it.
- **Write the Workstream doc-type.** Done 2026-09-24, with Loop:
  its class in the reference model, the bundle in
  [`doc-types/workstream/`](/doc-types/workstream/index.md),
  [Workstream Conventions](/standards/doc-type/workstream-conventions.md)
  and its checks, and every head file typed `Workstream`.
- **Move the work to `workstreams/`.** Done 2026-09-24: each head
  file renamed `WORKSTREAM.md` and typed Workstream,
  [Workstream Files](/standards/knowledge-organization/documentation-sets/workstream-files.md)
  rewritten as the rules of a workstream's files, the exemptions the
  other rules grant a workstream reworded, the old terms replaced in
  every file, and every link fixed.
- **Think the system through.** Done 2026-09-25: a session with the
  user settled how a stint's target, its checks, and its agents fit
  together, recorded in
  [Stint Model](/workstreams/system/drive/stint-model.md); what it left
  is under [Planned](#planned).
- **Split the tracking standard.** Done 2026-09-25:
  [`standards/tracking/`](/standards/tracking/index.md) holds two
  sections, [GitHub Tracking](/standards/tracking/github/index.md),
  the Candidate register, the issue shapes, and the label scheme, and
  [Workstream Tracking](/standards/tracking/workstreams/index.md),
  whose rule keeps a worklist item off GitHub issues. The GitHub
  settings moved to their own Standard,
  [`standards/github/`](/standards/github/index.md).

## Acronyms

None.

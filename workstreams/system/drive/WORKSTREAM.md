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

The words of the workflow, workstream, loop, yield, stint,
principal, iteration, segment, and checkpoint, are the repo's
([CONTEXT.md](/CONTEXT.md#workstreams-and-loops)), since the doc-types
and [Running a Stint](/guides/running-a-stint.md) use them too, and
so is [draft Standard](/CONTEXT.md#governance), since the Standards
about Standards use it. This head file coins none.

### Shape

The guess as it stands:

```
Loop                        loops/<name>.md — the shape: act · verify · yield
Workstream                  one line of work, its head file typed Workstream
├─ head file                the headings picked from the menu
├─ documentation sets       whatever the work accumulates
├─ child workstreams        a subdirectory with its own head file
└─ stints                   bounded spends of effort, one after another,
   │                        each run by a loop
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
  history.
- **The brief is the workstream's head file.** One object serves attended
  and unattended work alike.
- **A workstream picks its headings from one menu.** The user and the
  agent pick the ones the work needs. The menu is
  [Headings from the registry](/standards/doc-type/workstream-conventions.md#headings-from-the-registry).
- **Open holds questions only.** An answer, recommended or not, is a
  separate thing and does not sit with the question.
- **The Ralph pattern has four parts**, and every loop keeps them:
  1. The plan is written in the standard format. An attended principal
     makes it; an unattended principal is given it.
  2. Independent fresh-context iterations each do one chunk.
  3. A fresh-context reviewer compares what was done with the plan, sorts
     its findings, and returns them to the principal, which supplies taste
     and judgment. The sorting is how the pattern scales: the user rules
     on the top findings only, since no user can read everything agents
     report, and ruling on a sorted list calibrates the user's taste.
     Beside the reviewer, the verifiers of the stint's target report
     to the principal
     ([Stint Model](/workstreams/system/drive/stint-model.md)).
  4. The principal changes the plan on the iterations' and the reviewer's
     reports, so the entity that manages the plan is the one that changes
     it.
- **An unattended principal keeps the whole stint in its own context,
  and never forks.** It knows the history of what it is doing because it
  lived it. The attended Ralph keeps its own mechanism, changing the
  plan through a fork of the top session, and the unattended `stint`
  command is built separately; both follow the
  [Stint Model](/workstreams/system/drive/stint-model.md).
- **Today's loops.** The Ralph workflow, which runs in a
  Claude Code session through the `Workflow` runtime
  ([`ralph-loop.js`](/dotfiles/dot-claude/workflows/ralph-loop.js)), and
  the `stint` command, which runs an unattended stint to its yield
  ([Running a Stint](/guides/running-a-stint.md)).
- **A headless agent never runs a Claude Code workflow.** An unattended
  stint runs headless code the user writes and maintains, as a
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
- **The `stint` command runs an unattended stint.** It supports this
  workstream as a tool.
- **The unattended principal rules on the findings itself.** It judges
  the reviewer's sorted findings against the head file's Goal, Done when,
  and Constraints, and writes each ruling in the progress file, so the
  user sees every ruling at the yield. A finding the head file cannot
  settle ends the stint as stuck.
- **The unattended principal is one headless Claude session.** The
  stint resumes the same session at each checkpoint, so its context
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
  `## Done when` points at them, they are wired to the workstream's `check` and not to the
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

- **Build the judge.** It runs a stint's stochastic rules, as `check`
  runs the deterministic ones: the stint already reads the `Targets:`
  ids and splits them by kind, and today refuses a stochastic one. The
  judge takes those ids and returns findings in `check`'s shape, and
  the checkpoint runs it beside `check` and the reviewer.
- **Bring the attended Ralph to the model.** The Ralph workflow
  (`ralph-loop.js`), its skills (`ralph-setup`, `ralph-checkpoint`),
  and its agents (`ralph-reviewer`, `ralph-checkpointer`) take the
  [Stint Model](/workstreams/system/drive/stint-model.md)'s target,
  verifiers, done rule, and deviations, and its names. The fork that
  changes the plan stays.
- **Write the stint's Loop.** The first file in `loops/`. In order:
  - **Design what a stint returns.** A session. Inside the container,
    iterations and checkpoints write files on the stint's branch:
    `PLAN.md`, `PROGRESS.md`, commits, and the head file's worklist
    moves. The design settles which of these come back when the
    container stops, which stay on the branch, and which reach `main`
    only on an accept. It also settles who writes the stint's entry
    under `## Stints`, and when: the container at the yield, or the
    loop after the user's verdict, since a verdict exists only after
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

- **Read the target from the workstream.** Done 2026-09-25: the stint
  reads the rule ids from the `Targets:` of the head file's planned
  stint entry and runs the workstream's `check` on the deterministic
  ones, as `<workstream>/check <rule-id>…`; `--check` is gone. A call
  that changes the head file, a draft Standard, or `check` stops the
  stint, and a worker that cannot do its task is now `stuck`, not a
  deviation. The stop rules are listed once, in
  [Running a Stint](/guides/running-a-stint.md#what-stops-a-stint).
- **Bring the `stint` command to the model.** Done 2026-09-25:
  `--check` is now the target check, which iterations may run at any
  time and the stint runs at each checkpoint; the checkpoint runs the
  target's verifiers and the reviewer; the principal decides done, and
  the stint refuses a done while the check reports findings; and a
  blocked iteration logs a deviation and ends its segment, so the stop
  rules `iter-k blocked` and `iter-k committed nothing` are gone, and
  [Running a Stint](/guides/running-a-stint.md) follows. Where a leaf's
  `check` script sits stays undecided: `--check` takes any command, so
  nothing in the stint depends on it. The judge that would decide a
  stint's stochastic rules is not built; it would read the `Targets:`
  ids of the head file's Planned stint entry, the model's one source
  for them, rather than repeat the ids in a new argument.
- **Put the draft Standard in the doc-type system.** Done 2026-09-25:
  the user ruled it a plain `Standard`, not a doc-type of its own.
  [Standard Conventions](/standards/doc-type/standard-conventions.md)
  now binds it, with the leaf workstream's directory name as its rule
  ids' family;
  [Workstream Files](/standards/knowledge-organization/documentation-sets/workstream-files.md)
  keeps it in a leaf and each leaf's name unique; and the term moved to
  [CONTEXT.md](/CONTEXT.md#governance). The gate reads rules under
  `standards/` only, so nothing under `workstreams/` is wired to it.
  The `Stint` part gained an optional `targets` field, `Targets:` in
  the entry, checked against the leaf's draft Standards; only a leaf
  has `## Stints`
  ([Workstream Conventions](/standards/doc-type/workstream-conventions.md));
  and [Writing Predicates](/guides/writing-predicates.md) puts a goal
  in a draft Standard, not an issue. `## Done when` stays free text: a
  stint may run with no draft Standard.
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
- **Run the pre-commit gate in the stint's work copy.** Done
  2026-09-25: before each agent, the call installs the work copy's
  pre-commit hooks in the container, so every commit runs the gate it
  runs on the host; the hook downloads live in a cache the stint's
  calls share. The image gained pre-commit, make, Node, and Chromium,
  so `make check` runs in the container. The work copy is named for its
  repository, carries the repository's `origin` URL, and has read-only
  copies of the repositories the base links to, for the gate's link
  checks. Real Sonnet stints on dev-playbook, mission-control, and
  story-forge committed through the gate;
  [Running a Stint](/guides/running-a-stint.md) has the details.
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

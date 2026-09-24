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
[sandcastle set](/working-docs/delegation/sandcastle/ROOT.md).

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
  `loops/`. It holds no goal and no history. Each stint is driven by a
  loop chosen for it, and one loop drives many workstreams.
- **Driver** — the program that runs a stint's loop: it starts each
  iteration, reads what the iteration reports, and stops the stint. The
  drivers form a menu, and each stint names the one it used.
- **Stint** — a bounded spend of effort advancing one workstream, with a
  loop and a driver chosen for it. An **attended** stint has the user in
  it, as in a session like the one that wrote this set: the most effective
  and the most costly. An **unattended** stint runs in a sealed container
  with no user, on the Sandcastle pipeline, and ends by yielding to the
  user.
- **Checkpoint** — a review point inside an unattended stint, after a
  block of iterations: the work is reviewed against the plan, and the plan
  is revised. It is the review the
  [Ralph checkpoint skill](/dotfiles/dot-claude/skills/ralph-checkpoint/SKILL.md)
  runs today.
- **Iteration** — one fresh-context agent that does one task of the plan,
  commits, and exits.
- **Principal** — the top-level entity of a stint, which owns the plan
  and rules on the reports of the iterations and the reviewer. In an
  attended stint it is the user and the top-level agent together; in an
  unattended stint it is the top-level agent alone.
- **Sandcastle pipeline** — the machinery that runs an agent in a sealed
  container, described in
  [The Sandcastle Pipeline](/working-docs/delegation/sandcastle/pipeline.md).

## Shape

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
  history. The loop and the driver belong to a stint, not to the
  workstream: the user chooses them for each stint, and the workstream's
  Stints heading records which ran.
- **The brief is the workstream's head file.** One object serves attended
  and unattended work alike.
- **A workstream picks its headings from one menu.** The user and the
  agent pick the ones the work needs:

  | Heading | Holds |
  |---|---|
  | Goal | what the work is for |
  | Done when | the state at which a stint yields as finished |
  | Principles | the judgment calls that guide choices |
  | Constraints | the hard bounds, the boundaries of a stint included |
  | Terms | the terms the work coins |
  | Settled | the decisions made, with their dates |
  | Open | the questions not yet decided |
  | Planned, Completed | the worklist |
  | Stints | the log of stints: date, loop, driver, branch, verdict |
  | Unfiled | material awaiting triage |
  | Acronyms | the appendix |

  Goal, Principles, Constraints, Terms, Planned, Completed, Unfiled, and
  Acronyms are a working documentation set's buckets today; Done when,
  Settled, Open, and Stints are new.
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
  the headless loop script, which runs an unattended stint to its yield
  on the Sandcastle pipeline.
- **A headless agent never runs a Claude Code workflow.** An unattended
  stint's driver is headless code the user writes and maintains, as a
  professional practice, even where a headless agent could run a
  workflow. The Ralph pattern (fresh agent, status, stop rule,
  checkpoints) is written as a Python script, and every call it makes
  runs in the Sandcastle pipeline, never on the host. Decided 2026-09-24.
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
- **The doc-types have one home.** Workstream and Loop are designed
  together in
  [the Loop and Workstream strand](/working-docs/doc-type-system/loop-and-workstream/ROOT.md)
  of the doc-type system set; this set holds only the workflow. Decided
  2026-09-24.
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
- **A workstream's target is not a Standard, for now.** Done when stays a
  heading; the idea returns after the first real stint.

## Open

None.

## Planned

Sessions with the user come first, each at a high level, the agent
guiding. Running an unattended stint is the
[sandcastle set's worklist](/working-docs/delegation/sandcastle/ROOT.md#planned).

- **Write the Workstream doc-type.** Designed and built with Loop in
  [the Loop and Workstream strand](/working-docs/doc-type-system/loop-and-workstream/ROOT.md),
  which holds its worklist; this item closes when that strand's does.
- **Retire "working documentation set".** `working-docs/` renamed to
  `workstreams/`, each head file renamed,
  [Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
  rewritten as the Workstream's rules, the exemptions the other rules
  grant a working set reworded, and every link fixed.
- **Split the tracking standard.** GitHub tracking and workstream
  tracking, each in its own section of
  [`standards/tracking/`](/standards/tracking/index.md).
- **Write the unattended stint's Loop.** The first file in `loops/`,
  once [the Loop and Workstream strand](/working-docs/doc-type-system/loop-and-workstream/ROOT.md)
  has settled both doc-types.
- **Build the board script.** It reads the head files and the live stints
  and prints the ✈️/💤 board.
- **Build the coordinator agent.** Advisory only.

## Completed

- **Design the delegation workflow.** Done 2026-09-24: a grilling session
  with the user set the five terms, the [Shape](#shape), and everything
  under [Settled](#settled), and renamed this set from `parallel-fronts`.
- **Decide the Open questions from the diagram.** Done 2026-09-24: the
  diagrams of a driven Sandcastle stint and of today's attended Ralph
  settled every question, recorded under [Settled](#settled).
- **Separate the machinery.** Done 2026-09-24: the Sandcastle members
  moved into the nested
  [sandcastle set](/working-docs/delegation/sandcastle/ROOT.md), so this
  root holds the workflow and that one holds how an unattended stint runs.
- **Check overlap with active branches.** Done 2026-09-24: `main`'s
  refactor is merged into this branch, and no active branch conflicts
  with it.

## Acronyms

None.

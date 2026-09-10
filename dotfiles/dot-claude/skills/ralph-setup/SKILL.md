---
name: ralph-setup
description: Scaffolds a Ralph loop — the plan and progress files a memoryless agent grinds through one task at a time. Use when the user asks to set up or scaffold a ralph loop.
disable-model-invocation: false
model: inherit
effort: xhigh
arguments: [goal]
---

# Ralph Setup

## Read first

{Read [ralph-loop.md](~/workspace/dev-playbook/harness-recipes/recipes/ralph-loop.md)
end-to-end, before anything else; the recipe states what the loop requires of
the files this skill writes}. Then say `READ: ralph-loop.md` and proceed.

## 1. Establish the target

- Confirm the cwd is the repo or worktree where the loop will run — agents
  inherit it, so the plan and progress files must live here and be named with
  relative paths. Ask if it isn't obvious.
- Keep the default filenames, `PLAN.md` and `PROGRESS.md`; these become
  the loop's `planFile` and `progressFile`. okf-lint excludes a file with
  exactly either name from the bundle, in any directory, so the pair
  needs no frontmatter and no index row. Any other name makes them
  concept documents, and the gate then demands both.
- If either file already exists, stop and ask before writing anything — the
  file on disk stands until the user says otherwise.

Then agree two numbers with the user, before the interview so the chunking has
a target:

- **How many tasks**, roughly. One task is one fresh iteration.
- **How many checkpoints**, at the recipe's floor of one or above. Suggest one
  every three to six tasks, and fewer only where the tasks are mechanical and a
  wrong turn is cheap to spot in the final diff.

## 2. Interview for intent

{Run [/grilling](~/.claude/skills/grilling/SKILL.md)}, with
{Run [/domain-modeling](~/.claude/skills/domain-modeling/SKILL.md) active
throughout}, to reach shared understanding of the goal: what the finished
product is, what is in and out of scope, what "good" means. `goal`, if
present, is the starting idea.

## 3. Define done

Synthesize the finished product as explicit, checkable success criteria —
concrete enough that a memoryless agent can judge whether the plan is
complete. Present them for explicit approval.

## 4. Chunk the plan

Break the work into an ordered task list where each task:

- is small enough to finish cleanly in one fresh-context iteration,
- is independently committable,
- leaves the check gate green (or committable, if the repo has no gate) when
  done,
- depends only on tasks above it — sequential, no forward references,
- is self-contained: executable from the plan and progress log alone, without
  re-deriving the higher-level plan,
- carries a **Verify** clause: what proves it landed, stated as something to
  check against the artifact rather than against the agent's word for it.
  Name a command wherever a command settles it.

The Verify clause is what a checkpoint reviewer runs, so a vague one ("the code
works") verifies nothing. It earns its place with the iteration agent too, where
it tells it when the task is done.

Order so prerequisites come first.

Then place the agreed number of `<!-- [ ] checkpoint -->` lines, the last of them
after the final task and counting toward that number. A segment is a stretch the
user is willing to have go wrong before anyone looks; make the first one shorter
than the rest, since that is where a plan is most likely to be wrong. Cut where
the work has a reviewable result, never mid-way through a thing that only makes
sense finished.

Present the chunked plan, its Verify clauses, and its segment boundaries for
explicit approval — a hard gate: nothing is written until the user approves.

## 5. Determine the check gate and verify loop-ready

The loop runs a **check gate** at the start and end of every iteration, and
raises on a red entry. The gate is loop config passed as the `checkCmd` arg —
decided once here, with the user, because the memoryless iteration agents
execute it.

Settle it now, before writing anything:

- Decide the single shell command that means "green" for this repo: a root
  `make check`, a sub-project `make -C tools check`, an `&&`-chain across
  several, or none. Per the workspace build standard, a repo may have no
  check (e.g. docs-only) — the gate is then the empty string `""`.
- Run the chosen gate and confirm it passes green (or confirm there is no
  gate to run).
- Confirm the git tree is clean and committed.

If the chosen gate is red, surface it and stop — scaffolding waits on a
green tree.

## 6. Write the files

{If the user approved the criteria and the plan, and the gate is green,
{Write the plan file; instantiate
[plan-skeleton.md](references/plan-skeleton.md) — the approved criteria under
`## Done when`, the approved tasks as `- [ ]` checkboxes with their Verify
clauses under `## Tasks`, the approved `<!-- [ ] checkpoint -->` markers
between segments and after the last task, and any durable facts the interview
surfaced under `## Working notes` (else leave it empty for the loop to fill);
fill the placeholders, keep the structure, drop the authoring comments}, and
{Write the progress file; instantiate
[progress-skeleton.md](references/progress-skeleton.md) unchanged — it is fixed,
and the loop appends to it}}. Run the gate once more; the two new files must
leave it green, or the names are wrong.

Then read back what was written and confirm three things before handing off.
All three are invisible once the run starts, and each one turns a reviewed run
into an unreviewed one:

- every marker reads exactly `<!-- [ ] checkpoint -->`, character for
  character — a near miss is a comment no parser sees,
- at least one marker is present,
- no unchecked task sits below the last marker.

## 7. Hand off the launch command

{Report the full launch command for the user to run; never run it yourself}.
`planFile`, `progressFile`, and `checkCmd` are fixed by this setup; the user
picks `model` and `maxIters` at launch:

```
Workflow({ name: "ralph-loop", args: { model: "<model>", maxIters: <n>, planFile: "<planFile>", progressFile: "<progressFile>", checkCmd: "<gate, or \"\" for no checks>" } })
```

`maxIters` is a rail on one segment, not on the run: size it to the longest
segment plus a little, not to the whole task list.

Then say what happens at the first stop: the workflow returns at the checkpoint,
and [/ralph-checkpoint](~/.claude/skills/ralph-checkpoint/SKILL.md) reviews the
segment and hands back the command for the next one. The user runs that pair
once per segment, the last time to review the finished plan. Naming it is all
this skill does — the user invokes it, not you.

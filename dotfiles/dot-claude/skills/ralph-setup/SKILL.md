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
- Choose the plan and progress filenames (default `PLAN.md` and
  `PROGRESS.md`); these become the loop's `planFile` and `progressFile`.
- If either file already exists, stop and ask before writing anything — the
  file on disk stands until the user says otherwise.

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
  re-deriving the higher-level plan.

Order so prerequisites come first. Present the chunked plan for explicit
approval — a hard gate: nothing is written until the user approves.

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
`## Done when`, the approved tasks as `- [ ]` checkboxes under `## Tasks`,
and any durable facts the interview surfaced under `## Working notes` (else
leave it empty for the loop to fill); fill the placeholders, keep the
structure, drop the authoring comments}, and {Write the progress file; copy
[progress-skeleton.md](references/progress-skeleton.md) unchanged — it is
fixed, the loop appends to it}}.

## 7. Hand off the launch command

{Report the full launch command for the user to run; never run it yourself}.
`planFile`, `progressFile`, and the `checkCmd` gate are fixed by this setup;
the user picks `model` and `maxIters` at launch:

```
Workflow({ name: "ralph-loop", args: { model: "<model>", maxIters: <n>, planFile: "<planFile>", progressFile: "<progressFile>", checkCmd: "<gate, or \"\" for no checks>" } })
```

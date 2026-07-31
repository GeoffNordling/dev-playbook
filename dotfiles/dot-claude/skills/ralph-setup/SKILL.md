---
name: ralph-setup
description: Scaffolds a Ralph loop — interviews the user to pin what the finished product is, breaks it into a sequential plan a memoryless agent can grind through one task at a time, and writes the plan and progress files the loop requires. Use when the user wants to set up or scaffold a ralph loop or says "set up a ralph loop".
disable-model-invocation: false
model: inherit
effort: xhigh
argument-hint: "[goal description]"
---

# Ralph Setup

The Ralph loop boots a fresh, memoryless agent each iteration; its only inputs are a plan file, a progress file, and a green check gate (or none). This skill produces those — above all a plan **chunked** so each fresh agent can do the next task without re-deriving the whole.

The interview and the chunking are the value here. A vague plan makes a loop that thrashes; a well-ordered one makes a loop that grinds to done.

## Read first

Read what the loop requires of the files you'll write:

- [ralph-loop.md](~/workspace/dev-playbook/harness-recipes/recipes/ralph-loop.md) — the recipe.

Then report `READ: ralph-loop.md` and proceed.

## 1. Establish the target

- Confirm the cwd is the repo or worktree where the loop will run — agents inherit it, so the plan and progress files must live here and be named with relative paths. Ask if it isn't obvious.
- Choose the plan and progress filenames (default `PLAN.md` and `PROGRESS.md`); these become the loop's `planFile` and `progressFile`.
- If either file already exists, stop and ask — never overwrite an existing plan or progress file.

## 2. Interview for intent

Invoke /grill-with-docs to reach shared understanding of the goal: what the finished product is, what is in and out of scope, what "good" means. `$ARGUMENTS`, if present, is the starting idea.

## 3. Define done

Synthesize the finished product as explicit, checkable success criteria — concrete enough that a memoryless agent can judge whether the plan is complete. Present them for explicit approval.

## 4. Chunk the plan

The heart. Break the work into an ordered task list where each task:

- is small enough to finish cleanly in one fresh-context iteration,
- is independently committable,
- leaves the check gate green (or committable, if the repo has no gate) when done,
- depends only on tasks above it — sequential, no forward references,
- is self-contained: executable from the plan and progress log alone, without re-deriving the higher-level plan.

Order so prerequisites come first. Present the chunked plan for explicit approval — a hard gate. Nothing is written until the user approves.

## 5. Determine the check gate and verify loop-ready

The loop runs a **check gate** at the start and end of every iteration, and raises on a red entry. The gate is loop config passed as the `checkCmd` arg — decided once here, with the user, because the memoryless iteration agents execute it, they do not re-decide it.

Settle it now, before writing anything:

- Decide the single shell command that means "green" for this repo: a root `make check`, a sub-project `make -C tools check`, an `&&`-chain across several, or none. Per the workspace build standard, a repo may legitimately have no check (e.g. docs-only); that is allowed — the gate is then the empty string `""`.
- Run the chosen gate and confirm it passes green (or confirm there is genuinely no gate to run).
- Confirm the git tree is clean and committed.

If the chosen gate is red, surface it and stop — do not scaffold a repo whose gate already fails. A repo with no gate is fine; that is not a reason to stop.

## 6. Write the files

- Instantiate [plan-skeleton.md](references/plan-skeleton.md) into the plan file: the approved criteria under `## Done when`, the approved tasks as `- [ ]` checkboxes under `## Tasks`, and any durable facts the interview surfaced under `## Working notes` (else leave it empty for the loop to fill). Fill the placeholders, keep the structure, drop the authoring comments.
- Write [progress-skeleton.md](references/progress-skeleton.md) into the progress file unchanged — it is fixed; the loop appends to it.

## 7. Hand off the launch command

Surface the full launch command for the user to run, with the decided values filled in — `planFile`, `progressFile`, and the `checkCmd` gate are fixed by this setup; the user picks `model` and `maxIters` at launch:

    Workflow({ name: "ralph-loop", args: { model: "<model>", maxIters: <n>, planFile: "<planFile>", progressFile: "<progressFile>", checkCmd: "<gate, or \"\" for no checks>" } })
---
name: ralph-setup
description: Scaffolds a Ralph loop — interviews the user to pin what the finished product is, breaks it into a sequential plan a memoryless agent can grind through one task at a time, and writes the plan and progress files the loop requires. Use when the user wants to set up or scaffold a ralph loop or says "set up a ralph loop".
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "[goal description]"
---

# Ralph Setup

The Ralph loop boots a fresh, memoryless agent each iteration; its only inputs are a plan file, a progress file, and a green `make check`. This skill produces those — above all a plan **chunked** so each fresh agent can do the next task without re-deriving the whole.

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
- leaves `make check` green when done,
- depends only on tasks above it — sequential, no forward references,
- is self-contained: executable from the plan and progress log alone, without re-deriving the higher-level plan.

Order so prerequisites come first. Present the chunked plan for explicit approval — a hard gate. Nothing is written until the user approves.

## 5. Verify loop-ready

The loop raises on a red entry, so before writing anything, confirm the repo can run iteration 1:

- `make check` exists and passes green,
- the git tree is clean and committed.

If either fails, surface it and stop — do not scaffold a repo that cannot run the loop. `make check` is the loop's fixed gate; a repo without one cannot host a Ralph loop until it has one.

## 6. Write the files

- Instantiate [plan-skeleton.md](references/plan-skeleton.md) into the plan file: the approved criteria under `## Done when`, the approved tasks as `- [ ]` checkboxes under `## Tasks`, and any durable facts the interview surfaced under `## Working notes` (else leave it empty for the loop to fill). Fill the placeholders, keep the structure, drop the authoring comments.
- Write [progress-skeleton.md](references/progress-skeleton.md) into the progress file unchanged — it is fixed; the loop appends to it.
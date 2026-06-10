---
name: improve-python-code
description: Review a Python file or codebase for organization, modularity, and maintainability improvements against workspace Python conventions, then apply changes for the user to review before committing.
disable-model-invocation: true
effort: xhigh
argument-hint: "<path-or-name>"
---

# Improve Python Code

Target: `$ARGUMENTS`

Review the target for opportunities to improve **organization, modularity, and maintainability**, apply changes, and stop for the user to view diffs before committing.

## 1. Resolve the target

`$ARGUMENTS` may be an absolute path, a relative path, a bare filename, or the name of a codebase under `~/workspace/`. Interpret loosely:

- Looks like a path that exists → use it.
- Bare filename → search the current repo (and `~/workspace/<name>/` if no hit).
- Codebase name → resolve to `~/workspace/<name>/`.

If ambiguous, ask the user which target they meant before continuing. Don't guess silently.

## 2. Read the standard

Read [python-conventions.md](~/workspace/dev-playbook/standards/python-conventions.md). It is the primary reference for this skill. Beyond the standard, apply general software-engineering judgment: naming, cohesion, dead code, duplicated logic, unclear control flow, modules that have grown two unrelated concerns.

The standard wins on the topics it covers. Don't re-litigate decisions it has already made.

## 3. Survey

Read the target exhaustively. Every file, end to end. Don't sample, don't skim, don't skip large modules because they look mechanical — the issues this skill catches often hide in the parts that look boring.

Note candidates as you go. Each candidate is one specific change with a clear motivation.

**Do not modify tests.** Tests are out of scope for this skill — read them only to understand the code under review. If a test seems wrong, surface it separately and ask.

## 4. Present candidates

Show the user a numbered list before editing. For each:

- **File(s)** with line numbers
- **What** — the change in one or two sentences
- **Why** — which convention or principle it serves

Ask which to apply. The user may pick all, some, or none, and may push back on individual items. Don't argue past one round — if they reject a candidate with a reason, drop it.

## 5. Apply changes

Apply only the approved changes. Keep edits surgical:

- One concern per edit. Don't bundle a docstring fix with a module-layout reshuffle.
- Don't reformat untouched lines.
- Don't rename things across the codebase as a side effect — flag rename candidates separately and ask first.
- If a change turns out to be larger than presented, stop and re-confirm.

## 6. Hand back for review

When edits are done, summarize what changed (file + one-line description per change) and stop. Do **not** commit. The user reviews diffs and decides when to commit.

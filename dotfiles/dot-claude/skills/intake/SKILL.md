---
name: intake
description: Capture an idea (one issue or many) and triage at creation. Decides category, mode, tests, first phase label; writes the brief into the issue body. Use when starting any new piece of work, splitting a plan into tracer-bullet issues, or breaking down a feature into deliverable units.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh label *) Skill(grill-with-docs)
---

# Intake

Single entry point for an idea. Produces one or many GitHub issues, each born ready: labeled with category, mode, tests, and first phase; brief written into the body.

For the full workflow, label scheme, issue body template, and vertical-slice rules, see the [workflow standard](~/workspace/dev-playbook/workflow/workflow.md).

## Process

### 1. Understand the idea

The user passes a free-form description. If terminology is fuzzy, scope is unclear, or the idea spans concepts that should live in `CONTEXT.md`, invoke /grill-with-docs first to sharpen. Then return here.

### 2. Decide one issue or many

If the idea is a single coherent piece of work → one issue.

If the idea is a plan that crosses concerns or layers → break into vertical slices per the [vertical-slice rules](~/workspace/dev-playbook/workflow/workflow.md#vertical-slice-rules-when-one-idea-becomes-many-issues). Quiz the user on granularity and dependencies before publishing.

### 3. For each issue, decide

Every issue carries the triple `(mode:*, tests:*, phase/*)` plus a category label. Pick each:

- **Category** — `bug`, `enhancement`, or `chore`.
  - `chore` covers housekeeping (config tweaks, dep bumps, doc relocations, label-scheme audits) and watch-and-wait reminders (revisit-when-data-arrives tickets) — anything that doesn't change product behavior.
- **Mode** — `mode:sdd` if the repo uses SDD (check for a top-level `specs/` directory; ask the user if unclear) and this issue warrants the spec → design → TDD ceremony; otherwise `mode:direct`. Chores are almost always `mode:direct`. A trivial issue in an SDD repo may not need full ceremony — your call.
- **Tests** — `mode:sdd` always carries `tests:yes` automatically. For `mode:direct`, **ask the human**: does this work involve writing or modifying tests?
  - `tests:yes` — testable behavior changes (most bugs, most enhancements).
  - `tests:no` — docs, config, dep bumps, label-scheme audits, pure renames, anything without a runtime behavior to assert.
- **First phase** — derived from mode + tests:
  - `mode:sdd` → `phase/sdd-requirements`
  - `mode:direct, tests:yes` → `phase/tdd`
  - `mode:direct, tests:no` → `phase/build`

### 4. Write the issue

The issue body IS the agent brief. Use the [issue body format](~/workspace/dev-playbook/workflow/workflow.md#issue-body-format-the-brief-is-the-body).

### 5. Publish

```bash
gh issue create \
  --title "..." \
  --label "<category>" \
  --label "<mode>" \
  --label "<tests>" \
  --label "<phase>" \
  --body "$(cat <<'EOF'
...body...
EOF
)"
```

Concrete examples:

- SDD enhancement → `enhancement`, `mode:sdd`, `tests:yes`, `phase/sdd-requirements`
- Direct bug with tests → `bug`, `mode:direct`, `tests:yes`, `phase/tdd`
- Doc-only chore → `chore`, `mode:direct`, `tests:no`, `phase/build`

For multi-issue plans, publish in dependency order so `Blocked by` references can use real issue numbers.

## Output

Print issue numbers, a one-line summary of each, and the next-phase skill the dispatcher would invoke (`/sdd-requirements`, `/tdd`, or `/build`). Do NOT auto-launch — the dispatcher decides when to start work.

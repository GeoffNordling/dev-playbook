---
name: intake
description: Capture an idea (one issue or many) and triage at creation. Decides category, SDD-mode, first phase label, writes the brief into the issue body. Use when starting any new piece of work, capturing a bug report, splitting a plan into tracer-bullet issues, or breaking down a feature into deliverable units.
disable-model-invocation: false
model: opus
effort: xhigh
---

# Intake

Single entry point for an idea. Produces one or many GitHub issues, each born ready: labeled with category, mode, and first phase; brief written into the body.

For the full workflow, label scheme, issue body template, and vertical-slice rules, see the [workflow standard](~/workspace/dev-playbook/standards/workflow.md).

## First step

Run [bootstrap-labels](~/workspace/dev-playbook/tools/bin/bootstrap-labels) to reconcile the repo's labels with the workflow's scheme. Closed-world and idempotent — extras are deleted, drifted descriptions are corrected, and one line per label reports the action.

```bash
python3 ~/workspace/dev-playbook/tools/bin/bootstrap-labels
```

## Process

### 1. Understand the idea

The user passes a free-form description. If terminology is fuzzy, scope is unclear, or the idea spans concepts that should live in `CONTEXT.md`, invoke /grill-with-docs first to sharpen. Then return here.

### 2. Decide one issue or many

If the idea is a single coherent piece of work → one issue.

If the idea is a plan that crosses concerns or layers → break into vertical slices per the [vertical-slice rules](~/workspace/dev-playbook/standards/workflow.md#vertical-slice-rules-when-one-idea-becomes-many-issues). Quiz the user on granularity, dependencies, and HITL/AFK type before publishing.

### 3. For each issue, decide

- **Category** — `bug`, `enhancement`, or `chore`.
  - `chore` covers housekeeping (config tweaks, dep bumps, doc relocations, label-scheme audits) and watch-and-wait reminders (revisit-when-data-arrives tickets) — anything that doesn't change product behavior.
- **SDD?** — apply `sdd` if the repo uses SDD and this issue's implementation will follow the spec → design → TDD path. A trivial issue in an SDD repo may not need full ceremony — your call. Chores skip `sdd` by default.
- **First phase** — `phase/requirements` if SDD, `phase/build` if not. Chores typically carry no `phase/*` label; add `phase/build` only if the chore is substantial enough to want a real PR cycle visible in the phase view.

### 4. Write the issue

The issue body IS the agent brief. Use the [issue body format](~/workspace/dev-playbook/standards/workflow.md#issue-body-format-the-brief-is-the-body).

### 5. Publish

```bash
gh issue create --title "..." --body "$(cat <<'EOF'
...body...
EOF
)"
gh issue edit <num> --add-label "bug" --add-label "sdd" --add-label "phase/requirements"
```

For multi-issue plans, publish in dependency order so `Blocked by` references can use real issue numbers.

## Output

Print the issue numbers and a one-line summary of each. Do NOT invoke `/sdd` automatically — let the user decide when to start work.

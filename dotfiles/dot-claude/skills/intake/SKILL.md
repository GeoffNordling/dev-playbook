---
name: intake
description: Capture an idea (one issue or many) and triage at creation. Decides category, mode, tests, first phase label; writes the brief into the issue body. Use when starting any new piece of work, splitting a plan into tracer-bullet issues, or breaking down a feature into deliverable units.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh label *) Skill(grill-with-docs)
---

# Intake

Single entry point for an idea. Produces one or many GitHub issues, each born ready with the four-tuple labels and a body brief.

## Read first

Before doing anything else, read end-to-end:

- [workflow standard](~/workspace/dev-playbook/workflow/workflow.md) — label scheme, state-machine graph.
- [issue conventions](~/workspace/dev-playbook/standards/issue-conventions.md) — body format, brief principles, vertical-slice rules.

Then report: `READ: workflow.md, issue-conventions.md`. Proceed only after.

## Process

### 1. Understand the idea

User passes a free-form description. If terminology is fuzzy, scope is unclear, or the idea spans concepts that should live in `CONTEXT.md`, invoke /grill-with-docs first to sharpen, then return.

### 2. Decide one issue or many

Single coherent piece → one issue. Plan crossing concerns or layers → break into vertical slices, quizzing the user on granularity and dependencies. Size each slice to the context budget (issue conventions → vertical-slice rules): split anything whose build would push an agent past ~30% context. The build agent won't resize the work, so the split has to happen here.

### 3. For each issue, pick the four-tuple

- `category:*` — pick one.
- `mode:*` — pick one. Check for a top-level `specs/` directory; ask the user if SDD applicability is unclear.
- `tests:*` — `mode:sdd` is always `tests:yes`. For `mode:direct`, ask the human.
- `phase:*` — implied by `(mode, tests)` per the state-machine graph.

### 4. Draft the brief

Per the issue conventions.

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

Multi-issue plans: publish in dependency order so `Blocked by` references can use real issue numbers.

## Output

Print issue numbers, a one-line summary of each, and the next-phase skill (`/sdd-requirements`, `/tdd`, or `/build`). Do NOT auto-launch — the dispatcher decides when to start work.

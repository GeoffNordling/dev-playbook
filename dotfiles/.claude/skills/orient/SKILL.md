---
name: orient
description: Orient to the current repository by reading its standard documentation files
disable-model-invocation: true
---

# Orient

Quickly orient yourself to this repository using its documentation hierarchy.
Do NOT launch explore agents or do deep code searches.

## Step 1 — See the shape of the repo

Run `ls` at the repo root to see the top-level file and directory structure.

## Step 2 — Discover what documentation exists

From the repo root, check for these files and directories:

- `README.md`
- `CLAUDE.md`
- `ROADMAP.md`
- `BUSINESS_CONTEXT.md`
- `specs/functional_requirements.md`
- `specs/design.md`
- `docs/adr/README.md`

Use Glob to check which of these exist. Do not search for anything else.

## Step 3 — Read what exists

Read each file that exists, in the order listed above. For specs and ADR index
files, read just enough to understand scope — do not read every ADR entry or
chase cross-references.

## Step 4 — Check open issues

Run `gh issue list` to see what tactical work is tracked.

## Step 5 — Summarize

Give the user a brief summary of what you learned and, based on everything you
found (docs, roadmap, issues, repo shape), what you think the logical next step
for this project is.

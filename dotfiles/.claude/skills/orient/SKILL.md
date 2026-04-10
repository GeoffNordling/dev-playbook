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

Read the Files table in the repo documentation standard:
`~/workspace/dev-playbook/standards/repo-documentation.md`

Check which of those files and directories exist in the current repo.

## Step 3 — Read what exists

Read each file that exists. For specs and docs, read just enough to understand
scope — do not chase cross-references or read every sub-file.

## Step 4 — Check open issues

Run `gh issue list` to see what tactical work is tracked.

## Step 5 — Summarize

Give the user a brief summary of what you learned. Include whether you noticed any obvious duplicate, redundant, or inaccurate documentation.
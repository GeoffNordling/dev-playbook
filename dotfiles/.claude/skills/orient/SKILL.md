---
name: orient
description: Orient to the current repository
disable-model-invocation: true
model: sonnet
effort: medium
allowed-tools: Bash(ls *) Bash(gh issue list *)
---

# Orient

Quickly orient yourself to this repository using its documentation hierarchy.
Do NOT launch explore agents or do deep code searches.

## Step 1 — See the shape of the repo

Run `ls` at the repo root to see the top-level file and directory structure.

## Step 2 — Discover what documentation exists

Read the Files table in the [repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md).

Check which of those files and directories exist in the current repo. Use
separate tool calls or fault-tolerant commands (e.g., `ls dir1; ls dir2`)
— never chain existence checks with `&&`, because one missing path will fail
the entire command and cancel any parallel tool calls.

## Step 3 — Read what exists

Read each file that exists. For specs and docs, read just enough to understand
scope — do not chase cross-references or read every sub-file.

## Step 4 — Check open issues

Run `gh issue list` to see what tactical work is tracked.

## Step 5 — Summarize

Give the user a brief summary of what you learned. Include whether you noticed any obvious duplicate, redundant, or inaccurate documentation.
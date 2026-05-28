---
name: orient
description: Orient to the current repository. Use when invoked by the user.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(ls *) Bash(gh issue list *)
---

# Orient

Quickly orient yourself to this repository using its documentation hierarchy.
Do NOT launch explore agents or do deep code searches.

## Step 1 — see the shape of the repo

Run `ls` at the repo root to see the top-level file and directory structure.

## Step 2 — discover what documentation exists

Read the Files table in the [repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md).

Check existence with one `ls` call that always exits 0:

```
ls -d FILE1 FILE2 DIR1 ... 2>/dev/null; true
```

The trailing `; true` keeps the call green when paths are missing, so sibling parallel tool calls in the batch survive.

## Step 3 — read what exists

Read each file that exists. For specs and docs, read just enough to understand
scope — do not chase cross-references or read every sub-file.

## Step 4 — check open issues

Run `gh issue list` to see what tactical work is tracked.

## Step 5 — summarize

Give the user a brief summary of what you learned. Include whether you noticed any obvious duplicate, redundant, or inaccurate documentation.
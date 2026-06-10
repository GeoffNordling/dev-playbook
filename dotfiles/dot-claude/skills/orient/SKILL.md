---
name: orient
description: Orient to the current repository. Use when invoked by the user.
disable-model-invocation: false
effort: xhigh
allowed-tools: Bash(ls *) Bash(gh issue list *)
argument-hint: "[focus]"
---

# Orient

Quickly orient yourself to this repository using its documentation hierarchy.
Do NOT launch explore agents or do deep code searches.

## Optional focus

$ARGUMENTS

If the line above is empty, run the default top-level orientation. If it holds a
hint, still complete every step below at the top level, but spend extra time on
the docs, directories, and code the hint points to — read those files more
closely and weight your summary toward them. Keep the no-explore-agents,
no-deep-search constraint either way.

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

Read each file that exists. Do not chase cross-references or read every nested reference — unless a focus was given, in which case you may follow references that bear on it.

Then report: `READ: {list of files you read}`. Proceed only after.

## Step 4 — summarize

Give the user a concise summary of what you learned. Include whether you noticed any obvious duplicate, redundant, or inaccurate documentation. If a focus was given, lead with what you found on it.
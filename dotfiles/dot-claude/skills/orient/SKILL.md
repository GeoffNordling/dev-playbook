---
name: orient
description: Orient to the current repository.
disable-model-invocation: true
model: sonnet
effort: xhigh
allowed-tools: Bash(ls *) Bash(gh issue list *)
argument-hint: "[focus]"
---

# Orient

Orient to this repository from its **documentation hierarchy** — what the docs
say, read quickly at the top level. That hierarchy is the whole search: no
explore agents, no deep code searches.

## Optional focus

$ARGUMENTS

If the line above is empty, run the default top-level orientation. If it holds a
hint, still complete every step below at the top level, but read the docs,
directories, and code it points to more closely and weight your summary toward
them. The documentation hierarchy bounds the reading either way.

## Step 1 — see the shape of the repo

Run `ls` at the repo root to see the top-level file and directory structure.

## Step 2 — discover what documentation exists

Read the Files table in the [documentation bundle standard](~/workspace/dev-playbook/standards/knowledge-organization/bundle.md).

Check existence with one `ls` call that always exits 0:

```
ls -d FILE1 FILE2 DIR1 ... 2>/dev/null; true
```

The trailing `; true` keeps the call green when paths are missing, so sibling parallel tool calls in the batch survive.

## Step 3 — read what exists

Read each file that exists, stopping at its cross-references — unless a focus was given, in which case follow the references that bear on it.

Then report: `READ: {list of files you read}`. Proceed only after.

## Step 4 — summarize

Summarize what you learned for the user. Include whether you noticed any obvious duplicate, redundant, or inaccurate documentation. If a focus was given, lead with what you found on it.

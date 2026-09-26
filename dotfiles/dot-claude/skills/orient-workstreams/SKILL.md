---
name: orient-workstreams
description: Orient the session on the work in flight under dev-playbook's `workstreams/` — the doctrine, the reference model, and the head file of each workstream the hint selects, never the material under them.
disable-model-invocation: true
model: inherit
effort: medium
arguments: [workstream-hint]
---

# Orient Workstreams

This orientation is high level: two fixed documents and the head file,
`WORKSTREAM.md`, of each workstream. The head files name the ideas, how
they connect, and what is open. The detail under each head file waits
until a task needs it.

`workstream-hint` is a loose hint, not a path. Match it to the
top-level directories of `~/workspace/dev-playbook/workstreams/`: the
hint `system` selects `workstreams/system/` with every child workstream
under it, and skips the other top-level directories. With no hint,
select every top-level directory. When the hint matches no directory,
or matches several where it reads as one, report the directory names
and stop.

## 1. Read the doctrine

Read each file end-to-end:

- {Read [System Legibility](~/workspace/dev-playbook/docs/system-legibility.md)}.
- {Read [the reference model](~/workspace/dev-playbook/doc-types/reference-model.md)}.

## 2. Read the head files

List the head files of each selected directory, from the root of the
dev-playbook checkout:

```bash
find workstreams/<directory> -name WORKSTREAM.md | sort
```

The sort puts each parent before its children. Read each listed file
end-to-end, in that order.

Read only the head files. Do not read the other files under
`workstreams/`: the material beside each `WORKSTREAM.md`, its data, and
its code. The head files link to them, and a link is followed later,
only when the user's task names it.

This step is done when every listed head file is read.

## 3. Scan the docs index

{Read [the docs index](~/workspace/dev-playbook/docs/index.md)}, the
index only. Note each file whose description bears on the workstreams
you read, beyond System Legibility. Do not read the noted files.

## 4. Report and wait

{Report `READ:` and each file you read, then two or three sentences on
how the workstreams connect}. {If step 3 noted a file, {Report each
noted path with one line on why it may bear on the work, and ask the
user for approval to read them}}. Then wait for the user's task.

## A file the head files miss

The head files are the map, and no map proves it is complete. When a file on
this subject turns up that no head file or index leads to — a stray note, a
doc in another directory — {Report the file's path to the user and ask
whether it belongs on the map} before acting on its content.

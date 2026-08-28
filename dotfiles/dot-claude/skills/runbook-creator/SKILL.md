---
name: runbook-creator
description: Author a new runbook — a skill bundle or an agent definition — against the workspace's runbook conventions. Use when the user says to create a skill or an agent.
disable-model-invocation: false
model: opus
effort: xhigh
arguments: [idea]
---

# Runbook Creator

Create one runbook: a skill bundle or an agent definition. `idea` carries
whatever the user has already said about it, and step 1 starts there.

The steps run in order. Step 1 ends by putting its questions to the user and
waiting, so the first line of the new file gets written at step 2.

## Read first

The rules live in these two, and this skill is only the workflow over them.
Before doing anything else:

- {Read [runbook-conventions.md](~/workspace/dev-playbook/standards/harness/runbook-conventions.md) end-to-end; the binding format a skill or agent takes}.
- {Run [/writing-for-agents](~/.claude/skills/writing-for-agents/SKILL.md) in context; the craft of writing what an agent consumes}.

{Override [/writing-for-agents](~/.claude/skills/writing-for-agents/SKILL.md)
where it states runbook format with [runbook-conventions.md](~/workspace/dev-playbook/standards/harness/runbook-conventions.md);
its `references/skill-mechanics.md` carries front matter and invocation rules of its own,
and this workspace's win}.

Then report: `READ: runbook-conventions.md, writing-for-agents`. Proceed only
after.

## 1. Interview the user

The user decides which kind — skill or agent — what it is for, the scenarios it
handles, and every front matter field, which `runbook-conventions.md` names and
marks optional or not. Where the conversation already implies an answer — the
idea is decided, or the new runbook mimics one that exists — recommend it
rather than asking, and state each recommendation with the open questions, so
the user approves or corrects it in the same reply.

This step is done when every decision above carries an answer the user gave or
approved.

## 2. Draft

{Write the new runbook} from those answers.

## 3. Check, then hand off

{Run [playbook-lint](~/workspace/dev-playbook/scripts/playbook-lint)} over the
dev-playbook **repo root**, and fix what it reports. Its `harness-files-lint`
line must show a nonzero count; aimed narrower it finds no runbooks and passes
vacuously.

Leave the clean result uncommitted — the user reviews the working-tree diff in
their IDE.

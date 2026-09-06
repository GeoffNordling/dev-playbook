---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent. Extensible: terms are added here as they're pinned down.

## Language

### Legibility

The words the user and the AI meet on
([System Legibility](/docs/system-legibility.md)).

**Slop**
Output that diverges from the user's intent, or that the user cannot read.

**CLOA**
Correct Level of Abstraction: the best-effort shared level where the user and the AI communicate in exactly the same terminology — the highest level the user can trust the AI at, and the lowest the AI needs the user at.

**Doc-type**
Operations plus a composition rule, handing one documentation family a contract shape ([Doc-Type](/doc-types/doc-type.md)).

**Contract**
Everything a caller of an instance may rely on; its machine-checkable core is the signature — args in, results out ([Doc-Type](/doc-types/doc-type.md#contract)).

### Governance

Five words once swirled around one idea — the thing that inspects the
repository and may block it. They are separated here into five roles.

**Audit**
The umbrella term for the Standard's read-only checking process: a run of one or more detectors; read-only — it never mutates the repository and never blocks by itself. A Detector is a **lint** if it is deterministic code, an **audit** in the narrow sense if it is an LLM judge.
_Avoid_: check (too broad — a check may block; an audit never does).

**Lint**
A Detector implemented as deterministic code — the `*-lint` scripts under `scripts/`. Every lint is part of the audit process (lint ⊂ audit), never the reverse — an audit in the narrow sense (an LLM judge) is not a lint.
_Avoid_: audit, for a deterministic detector — that detector is a lint.

**Detector**
The read-only check that inspects the repository against one or more standards and emits findings; it never mutates the repository. A Detector is a **lint** if it is deterministic code and an **audit** in the narrow sense if it is an LLM judge.
_Avoid_: audit, for the check itself — an audit is a *run* of one or more detectors.

**Gate**
An automatic, unmanned blocking point on the path to main, continuously in effect. An audit never blocks; a gate is what blocks.
_Avoid_: venue (retired — say **gate**, or a rung name).

**Enforcement**
What compels conformance, in one of two modes: an audit stationed at a gate, whose findings block the path to main there, or a tool invoked on demand, which rewrites the object into conformance.
_Avoid_: audit, where the blocking or the rewriting is the point — an audit only reports, however it is run.

### File roles

The two axes a repository file sits on, its role and its content
([File Roles](/standards/knowledge-organization/file-roles.md)).

**Concept document**
Prose a reader loads to understand something. It carries OKF frontmatter, and okf-lint reads its type.

**Harness-owned file**
A file a tool consumes as configuration or runs as code or instructions: every non-`.md` file, plus the Claude Code file set the harness-files registry enumerates. It carries no OKF frontmatter.

**Rule**
A rule of the system: a contract, a state and the moves out of it, a format, what one part owes another. It binds every actor who touches the thing, whatever job that actor is doing.

**Procedure**
The steps of one job: its trigger, its target, the order of the steps, the conditions it branches on, the commands it issues, when it stops, what it reports. It binds one actor for the length of one run.

**Runbook**
An invocable command written as documentation: a skill or an agent definition. It is invoked by name, args in, a report out, effects on state in between, and its body is natural imperative English commanding the executing agent ([Runbook](/doc-types/runbook/definition.md)).

**Context file**
Prose the harness injects into agent context, read and never invoked: a `CLAUDE.md` at any scope and every `rules/*.md` ([Claude Code Files](/standards/harness/files.md)).

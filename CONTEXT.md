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

### Governance

How a Standard's rules are decided, in the terms of the Standard's
shape ([Population and Rules](/doc-types/standard/contract-shape.md)).

**Rule**
One heading of a Standard, its predicate, and its trailer: an id, `<family>.<slug>`, and a kind, deterministic or stochastic.

**Verifier**
What decides one rule over a member and returns findings: a check or a judge. It reads and never writes.

**Check**
A verifier for a deterministic rule: a function registered under the rule's id, which `playbook check` runs, or a tool such as ruff registered by its hook.
_Avoid_: detector, lint.

**Judge**
A verifier for a stochastic rule: a model prompted with the rule's predicate.

**Finding**
What a verifier returns for a member that fails a rule: the member, the rule's id, and a message.

**Gate**
A point where findings block work: pre-commit, pre-push, or CI.
_Avoid_: audit, enforcement, venue.

### Documentation sets

How concept documents group
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)).

**Documentation set**
The concept documents one `index.md` owns, related as a set by the index's listing; a directory with its own `index.md` is a set nested in its parent's.

**Concern**
The boundary a document or a set declares: a document's frontmatter `description`, a set's index introduction. A body is judged against it.

### File roles

The two axes a repository file sits on, its role and its content
([Document Types](/standards/knowledge-organization/document-types.md)).

**Concept document**
Prose a reader loads to understand something. It carries OKF frontmatter, and a check reads its type.

**Harness-owned file**
A file a tool consumes as configuration or runs as code or instructions: every non-`.md` file, plus the Claude Code file set the harness-files registry enumerates. It carries no OKF frontmatter.

**Procedure**
The steps of one job: its trigger, its target, the order of the steps, the conditions it branches on, the commands it issues, when it stops, what it reports. It binds one actor for the length of one run.

**Runbook**
An invocable command written as documentation: a skill or an agent definition. It is invoked by name, args in, a report out, effects on state in between, and its body is natural imperative English commanding the executing agent ([Runbook](/doc-types/runbook/definition.md)).

**Context file**
Prose the harness injects into agent context, read and never invoked: a `CLAUDE.md` at any scope and every `rules/*.md` ([Claude Code Files](/standards/harness/files.md)).

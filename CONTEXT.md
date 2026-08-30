---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent. Extensible: terms are added here as they're pinned down.

## Language

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
An automatic, unmanned blocking point on the path to main. An audit never blocks; a gate is what blocks.
_Avoid_: venue (retired — say **gate**, or a rung name).

**Enforcement**
An audit stationed at a gate — the audit's findings block the path to main there. Enforcement is automatic and continuously in effect.
_Avoid_: audit, where the blocking is the point — an audit run by hand is not Enforcement.

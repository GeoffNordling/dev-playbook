---
type: Guide
title: File Roles
description: The two axes a repository file sits on — role, who consumes it, and content, rule or procedure — and which combinations serve a reader
---

# File Roles

Every file in a workspace repository sits on two axes. **Role** is who
consumes the file: a concept document is prose a reader loads to
understand something, and a harness-owned file is one a tool consumes as
configuration or runs as code. **Content** is what the file holds: a
rule of the system, or the procedure of one job. The four terms are
defined in the vocabulary ([CONTEXT.md](/CONTEXT.md#file-roles)). The
boundary between the two roles is the population of
[Document Types](/standards/knowledge-organization/document-types.md);
which files exist is [File Skeleton](/standards/build/skeleton.md)'s.

## What each role may hold

The axes are independent:

| | Concept document | Harness-owned file |
|---|---|---|
| **Rule** | Its home — a Standard, a Decision Record, the vocabulary. | Cites the document that owns it; may state what its own run needs but avoid duplication. |
| **Procedure** | A recipe a reader follows — an adoption walkthrough, a migration. | A program the harness runs — a skill body, an agent definition. |

The division is a general aim, not a strict gate: rules live in documents,
procedures live in runbooks, and follow that split where it serves the
reader. A runbook that needs a rule of the system cites the document that
defines it rather than duplicating; the terms, formats, and states of a
runbook's own run are part of the procedure and need no document.

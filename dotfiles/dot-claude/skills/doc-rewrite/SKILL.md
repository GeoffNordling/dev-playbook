---
name: doc-rewrite
description: Rewrite a Markdown document from scratch, rebuilding its structure while preserving content by default.
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "[doc-hint]"
---

# Doc Rewrite

Rewrite the target Markdown document from scratch, preserving content by
default — information is dropped only with the user's explicit approval,
asked for during the workflow.

Markdown documents only.

## Target

`$ARGUMENTS` is a hint identifying which document to operate on. It need not
be a literal path — it can be a path, a partial path, a filename fragment, or
a description like "the auth setup doc."

- **Empty.** Operate on the Markdown document most clearly in focus in the
  current conversation. If no document is clearly in focus, ask which file.
- **Non-empty.** Resolve the hint to a single `.md` file. If the hint matches
  exactly one file, proceed. If it matches zero or multiple files, ask.

## Workflow

1. **Read the doc conventions** at
   [prose/conventions.md](~/workspace/dev-playbook/standards/prose/conventions.md).
   These are the patterns the rewrite applies.
2. **Read the entire target document**, top to bottom, before any edits.
3. **Articulate the document's purpose** — what it's for, who it's for, and
   what a reader should be able to do after reading it — before rewriting.
   It guides every structural choice.
4. **Interview the user only when a genuine ambiguity would change the
   rewrite** — for example, the document's purpose is unclear and two
   readings produce different structures, two sections appear to
   contradict and you cannot tell which is current, or a section's
   relevance hinges on a decision not visible in the document. Batch those
   questions into one round; every other call is yours to make from the
   source.
5. **Inventory the substantive content.** List every fact, rule, example,
   constraint, and reference the document contains. As you go, flag two
   categories of candidates for removal:
   - **Stale.** Items recording a past decision no longer relevant given
     current state and next steps.
   - **Ancillary.** Minor details, tangential examples, or asides that a
     tighter rewrite may not need.
6. **Ask the user about cuts before rewriting.** Present the flagged items
   in one batch, grouped by category, and ask which to drop and which to
   keep.
7. **Rewrite the document from scratch**, applying the doc conventions.
   Preserve every item except those the user approved cutting in step 6.
8. **Verify against the inventory.** Confirm every preserved item is
   present in the rewrite. If any preserved item no longer fits, surface
   it explicitly.
9. **Report** the one-sentence purpose, the structural changes made, items
   dropped (with user approval), and any preserved items flagged as
   no-longer-fitting.

## Rules

- **Default to preservation.** Wording and structure are free to change,
  but information is preserved unless the user has explicitly approved
  cutting it in workflow step 6.
- Limit the rewrite to what the source contains. Reorganization,
  rephrasing, and surfacing implicit structure are in scope; inventing new
  rules or examples is not.
- Ground the rewrite in the current document and any interview answers
  alone — git history, related files, and the surrounding project context
  stay out of it. The rewrite restructures one document.
- If a section genuinely cannot be restructured without losing meaning,
  leave it and say so in the report.

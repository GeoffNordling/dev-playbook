---
name: doc-rewrite
description: Rewrite a Markdown document from scratch, preserving content by default
disable-model-invocation: true
effort: xhigh
argument-hint: "[doc-hint]"
---

# Doc Rewrite

Rewrite the target Markdown document from scratch. Throw away the existing
structure and rebuild it from the ground up, preserving content by default —
information is dropped only with the user's explicit approval, asked for
during the workflow.

Markdown documents only. Do not apply this skill to code.

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
   [doc-conventions.md](~/workspace/dev-playbook/standards/doc-conventions.md).
   These are the patterns the rewrite applies.
2. **Read the entire target document**, top to bottom, before any edits.
3. **Articulate the document's purpose.** This is the north star for the
   rewrite — what the document is for, who it is for, and what a reader
   should be able to do after reading it. Surface it explicitly before
   rewriting so it can guide every structural choice.
4. **Interview the user only when a genuine ambiguity would change the
   rewrite.** Default is no interview. Ask when, and only when, the source
   leaves a question whose answer would materially redirect the rewrite —
   for example, the document's purpose is unclear and two readings produce
   different structures, two sections appear to contradict and you cannot
   tell which is current, or a section's relevance hinges on a decision
   not visible in the document. Batch targeted questions into one round.
   Do not use the interview to confirm choices you can already make from
   the source, or to gather content the document does not contain.
5. **Inventory the substantive content.** List every fact, rule, example,
   constraint, and reference the document contains. As you go, flag two
   categories of candidates for removal:
   - **Stale.** Items recording a past decision no longer relevant given
     current state and next steps.
   - **Ancillary.** Minor details, tangential examples, or asides that may
     not earn their place in a tighter rewrite.
6. **Ask the user about cuts before rewriting.** Present the flagged items
   in one batch, grouped by category, and ask which to drop and which to
   keep. Default-keep anything the user does not explicitly approve
   cutting. Do not ask about items you intend to preserve.
7. **Rewrite the document from scratch**, applying the doc conventions.
   Preserve every item except those the user approved cutting in step 6.
8. **Verify against the inventory.** Confirm every preserved item is
   present in the rewrite. If any preserved item no longer fits, surface
   it explicitly rather than silently dropping it.
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
  only. Do not consult git history, related files, or other surrounding
  context to research the document's evolution, reconstruct intent, or
  track recent work. The rewrite is not a synthesis of project state.
- If a section genuinely cannot be restructured without losing meaning,
  leave it and say so in the report.

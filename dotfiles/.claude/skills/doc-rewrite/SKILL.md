---
name: doc-rewrite
description: Rewrite a Markdown document from scratch, preserving all content
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "[doc-hint]"
---

# Doc Rewrite

Rewrite the target Markdown document from scratch. Throw away the existing
structure and rebuild it from the ground up, preserving every fact, rule,
and example the source contains.

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

1. **Read the entire document first**, top to bottom, before any edits.
2. **Articulate the document's purpose.** This is the north
   star for the rewrite — what the document is for, who it is for, and what
   a reader should be able to do after reading it. Surface it explicitly
   before rewriting so it can guide every structural choice.
3. **Inventory the substantive content.** List every fact, rule, example,
   constraint, and reference the document contains. Flag any item that
   records a past decision no longer relevant given current state and next
   steps — these are candidates for removal, not preservation.
4. **Rewrite the document from scratch**, applying the patterns below.
   Preserve every non-flagged item; exclude flagged stale items.
5. **Verify against the inventory.** Confirm every non-flagged item is
   present in the rewrite. If any item no longer fits, surface it
   explicitly rather than silently dropping it.
6. **Report** the one-sentence purpose, the structural changes made, items
   removed as stale, and any items flagged as no-longer-fitting.

## Patterns to Apply

Apply each of these while rewriting.

- **Open with a clear, concise statement of purpose.** State what the
  document is for, who it is for, and what the reader should be able to do
  after reading.
- **Write for a cold-start reader.** Assume zero prior conversation context. The document must stand alone for a fresh agent in this repository.
- **Lead each section with its most important point.** Setup,
  qualifications, and background follow; the lede comes first.
- **Name each concept on first use, and use that name consistently.** One
  name per concept across the document.
- **Group rules with their rationale and examples.** A rule, why it
  exists, and what it looks like belong together in one place.
- **Consolidate duplicates.** Each point lives in one authoritative
  location.
- **Emphasize current state and future next steps, not historical records.**
  Past decisions that no longer constrain present or future work belong in
  the report, not in the rewrite.
- **Format consistently throughout.** Pick one convention per dimension —
  heading levels, bullet style and nesting, casing and terminal
  punctuation, emphasis, code spans, spacing — and apply it uniformly.

## Rules

- Preserve every currently-meaningful fact, rule, and example. Wording and
  structure are free to change; information disappears only when surfaced
  in the report.
- Limit the rewrite to what the source contains. Reorganization,
  rephrasing, and surfacing implicit structure are in scope; inventing new
  rules or examples is not.
- If a section genuinely cannot be restructured without losing meaning,
  leave it and say so in the report.

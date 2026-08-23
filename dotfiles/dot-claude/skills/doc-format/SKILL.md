---
name: doc-format
description: Standardize formatting and style across a Markdown document without changing its content.
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "[doc-hint]"
---

# Doc Format

Make the formatting and style of a Markdown document consistent throughout
without changing its content — a **formatting-only pass**, bounded by the
rules at the bottom.

## Target

`$ARGUMENTS` is a hint identifying which document to operate on. It need not
be a literal path — it can be a path, a partial path, a filename fragment, or
a description like "the auth setup doc."

- **Empty.** Operate on the Markdown document most clearly in focus in the
  current conversation (the one being iteratively edited or discussed). If no
  document is clearly in focus, ask which file.
- **Non-empty.** Resolve the hint to a single `.md` file. If the hint matches
  exactly one file, proceed. If it matches zero or multiple files, ask.

## Convention selection

For each formatting dimension below, adopt the **majority (mode) style
already present in the document**. Where there is no clear majority, prefer
the flatter, simpler option.

## Formatting dimensions

Review the entire document and standardize each of these. Pick one convention
per dimension and apply it everywhere.

- **Heading hierarchy.** Consistent nesting depth, using only the levels the
  document already has.
- **Bullets vs. prose.** Comparable sections settle on one style.
- **Nested bullets.** Either used consistently or flattened to a single level.
- **Bullet lead-in style.** Bullets throughout either begin with **bold
  lead-ins** followed by a period and explanation, or read as plain sentences —
  one shape for the whole document.
- **Sentence casing and terminal punctuation** in bullets and headings.
- **Emphasis conventions.** Consistent use of bold vs. italics for the same
  kind of thing (e.g., terms, UI labels, filenames).
- **Code spans and fences.** Consistent backtick usage for identifiers, paths,
  and commands.
- **List punctuation.** Trailing periods on bullets: either all or none.
- **Spacing.** Blank lines between sections, around lists, and around code
  blocks applied consistently.

## Workflow

1. Resolve the target document from `$ARGUMENTS` per the **Target** rules.
2. Read the entire target document.
3. For each dimension, pick the convention per the **Convention selection**
   rule.
4. Edit the file in place to bring every section into line.
5. Report a short summary of the conventions chosen and what was changed.

## Rules

- **The words survive the pass.** Wording, content, section order, and heading
  text all come through unchanged; only a heading's level or casing may move,
  for consistency.
- If a section's content genuinely requires a different structure (e.g., a
  table vs. a list), leave it; consistency applies within comparable sections.

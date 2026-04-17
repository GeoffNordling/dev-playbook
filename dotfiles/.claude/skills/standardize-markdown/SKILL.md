---
name: standardize-markdown
description: Standardize formatting and style across a Markdown document
disable-model-invocation: true
model: sonnet
effort: low
argument-hint: "[path-or-preferences]"
---

# Standardize Markdown

Make the formatting and style of a Markdown document consistent throughout.
This is a formatting-only pass — do not change the content, meaning, wording,
or structure of any section.

## Target

Operate on the Markdown document most clearly in focus in the current
conversation (the one being iteratively edited or discussed). If `$ARGUMENTS`
is a path, operate on that file instead. If no document is clearly in focus,
ask which file.

## Arguments

`$ARGUMENTS` is optional and may be one of:

- **A file path.** Use that file as the target.
- **A sentence of preferences.** Natural-language guidance for which
  conventions to adopt (e.g., "flatten all nested bullets", "use bold
  lead-ins on bullets", "no trailing periods").
- **Empty.** Pick conventions automatically using the rule below.

When no preferences are given, adopt the **majority (mode) style already
present in the document** for each dimension. Where there is no clear
majority, prefer the flatter, simpler option.

## Formatting Dimensions

Review the entire document and standardize each of these. Pick one convention
per dimension and apply it everywhere.

- **Heading hierarchy.** Consistent nesting depth. Do not introduce new levels
  unless already present.
- **Bullets vs. prose.** Matching similar sections to one style; do not mix.
- **Nested bullets.** Either used consistently or flattened to a single level.
- **Bullet lead-in style.** Either bullets begin with **bold lead-ins**
  followed by a period and explanation, or they are plain sentences. Do not
  mix.
- **Sentence casing and terminal punctuation** in bullets and headings.
- **Emphasis conventions.** Consistent use of bold vs. italics for the same
  kind of thing (e.g., terms, UI labels, filenames).
- **Code spans and fences.** Consistent backtick usage for identifiers, paths,
  and commands.
- **List punctuation.** Trailing periods on bullets: either all or none.
- **Spacing.** Blank lines between sections, around lists, and around code
  blocks applied consistently.

## Workflow

1. Read the entire target document.
2. For each dimension above, determine the convention to apply:
   - If `$ARGUMENTS` specifies a preference for that dimension, use it.
   - Otherwise, adopt the majority (mode) style already present in the
     document.
   - If there is no clear majority, pick the flatter, simpler option.
3. Edit the file in place to bring every section into line with the chosen
   conventions.
4. Report a short summary of the conventions chosen and what was changed.

## Rules

- Do NOT change wording, add content, remove content, or reorganize sections.
- Do NOT rename headings or alter their meaning — only adjust their level or
  casing for consistency.
- If a section's content genuinely requires a different structure (e.g., a
  table vs. a list), leave it; consistency applies within comparable sections.

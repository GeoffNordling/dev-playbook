---
name: working-doc-set-audit
description: Audit a working documentation set — the in-process Markdown files of one work stream — against the working-documentation-sets standard, reporting findings without editing. Use when working docs have drifted, or when asked to audit a set of planning files for duplication, staleness, conflicts, or term drift.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
argument-hint: "[set-hint]"
---

# Working Doc Set Audit

Audit one working documentation set against
[Working Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md)
and report findings. Edit nothing and commit nothing — the report is the
whole product.

## Target

`$ARGUMENTS` is a hint identifying the set: its root file, its directory, or
a description such as "the no-more-slop working files."

- **Empty.** Operate on the set most clearly in focus in the current
  conversation. Where none is, ask which.
- **Non-empty.** Resolve the hint to a root file. Where it matches nothing,
  ask.

The set is the root plus every working file it links, plus any sibling
working file the root fails to link — an unlinked sibling is itself a
finding, never a reason to skip the file.

## Audit

Read the standard, then every member in full, before judging anything.
Check the set against each rule of the standard, using the bucket names and
conventions the set itself declares. The finding categories:

- **Stale next steps** — plan prose, in the root or a child's own to-dos,
  contradicted by the set's own ledgers or by later members.
- **Duplicated fact** — one fact in two or more homes; name the single home
  it should keep.
- **Conflict** — two members (or a definition and its usage) that disagree;
  quote both sides.
- **Broken shape** — an orphan member, a dead link, a child restating a
  parent, a root summary that no longer matches its child.
- **Term drift** — a coined term used across members but missing from the
  terms bucket, used inconsistently, or resolvable nowhere in the set.
- **Misfiled or unfiled** — material sitting outside the bucket that owns
  its type, with no Unfiled entry declaring it.
- **Cut candidates** — content flagged stale or ancillary under the
  standard's conservation rule, listed for the user's ruling, never cut.

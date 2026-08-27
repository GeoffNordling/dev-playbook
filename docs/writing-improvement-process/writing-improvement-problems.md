---
type: General-Sheet
title: Writing Improvement Problems
description: The catalog of recurring problems in Claude's document writing — each one a pattern a review can reject, with its countermeasure where one exists
---

# Writing Improvement Problems

The catalog of recurring problems in Claude's document writing. Each
entry names a pattern a review can cite. A problem enters the catalog
when it recurs; a countermeasure, once built, is linked from its entry.

## Slop tics

**Definition.** Sentence-level style patterns: changelog residue,
contrast pairs, closing cadence, and the rest. The named tics live in
[slop-tics.md](/standards/prose/slop-tics.md).

**Action.** `/document-remove-tics` dispatches the tics-remover agent to
remove them from a document.

**Examples.** Each tic in slop-tics.md carries its own before/after
examples.

## Official-doc pointing

**Definition.** Pointing readers at official documentation unnecessarily.

**Action.** Delete the pointer. Cover the feature or say nothing. The reader
always retains the option to search official documentation and does not need
to be reminded.

**Examples.**

- **Before** "For the full feature reference (subagent execution, shell
  injection, hooks, etc.), see the official skill and subagent
  documentation." → **After** deleted.

## Enforcement meta-commentary

**Definition.** Declaring the document binding, or naming the lint that
enforces it.

**Action.** Delete the sentence. The purpose of a document does not include
documenting its own external validators.

**Examples.**

- **Before** "This standard is binding, and harness-files-lint enforces
  it at the commit gate." → **After** deleted.

## Relationship meta-commentary

**Definition.** Describing the document's relationship to other
machinery — craft skills, sibling processes — instead of stating its
rules.

**Action.** Delete the description. State the rules.

**Examples.**

- **Before** "The craft beside it is the installed `/writing-for-agents`
  skill, which covers any document an agent consumes… Invoke it when
  authoring or editing a runbook. Where the two collide this standard
  wins…" → **After** deleted.

## Duplication instead of integration

**Definition.** Restating a fact another document owns instead of
citing that document or moving the fact to its owner.

**Action.** Cite the owning document, or move the fact to its owner.
Never duplicate facts across multiple documents.

**Examples.**

- **Before** "A runbook is harness-owned — Claude Code loads it as
  configuration, not as prose to learn from — so it is not an OKF
  concept document." (the file-roles standard owns this) → **After**
  deleted.

## Section-scale duplication

**Definition.** A whole section that near-verbatim duplicates another
standard, instead of landing in that standard.

**Action.** Land the section in the standard that owns the subject and
keep a pointer.

**Examples.**

- **Before** a Cross-references section restating the no-fixed-root
  rule and the full target-style table the cross-references standard
  owns → **After** the section moved there as its Runbooks section; one
  pointer sentence remains.

## Stale-prone examples

**Definition.** Citing specific corpus files as examples; the examples
go stale as the corpus moves.

**Action.** Name the rules and the classes they govern.

**Examples.**

- **Before** "Related runbooks share a namespace prefix:
  `issue-review-claims`, `issue-review-simulation`." → **After**
  "Related runbooks share a namespace prefix."

## Nonexistent-thing mentions

**Definition.** Mentioning things decided not to exist.

**Action.** Delete the mention.

**Examples.**

- **Before** "Where skills live, and how third-party skills are
  installed, is skill-management.md's concern." (the workspace decided
  against third-party skills) → **After** "Where skills live is
  skill-management.md's concern."

## Unapproved negative examples

**Definition.** Teaching what not to do without a specific reason or
user approval.

**Action.** Delete the instruction, or get the reason approved.

**Examples.**

- **Before** "**`user-invocable`** — do not include this field.
  Upstream defines it…" → **After** deleted; the closed field
  vocabulary already excludes it.

## Coined transitions

**Definition.** Transitional phrases invented on the spot that the
reader must decode.

**Action.** Write a plain transition that names what follows.

**Examples.**

## Platform explainers

**Definition.** Explaining how an underlying platform or tool operates
instead of stating the document's own content. A rule may rest on a
platform fact; the document states the rule, not the mechanics behind
it.

**Action.** State the rule; drop the mechanics.

**Examples.**

- **Before** "`false` is the standard — per the dispatch model, the
  dispatcher's slash commands arrive as agent text input and count as
  model invocation. Use `true` only for skills meant for direct user
  invocation outside the dispatcher." → **After** "`false` is the
  standard; use `true` only for skills meant for direct user
  invocation."
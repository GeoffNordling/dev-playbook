---
type: Standard
title: The OKF Bundle
description: The documentation bundle — its purpose, principles, and the concept/harness boundary
---

# The OKF Bundle

Every documentation file in a workspace repository has a defined content
scope, so any human or agent can open a repo cold and immediately orient —
what it is, how to operate it, and where to find the rest. Which files must
exist is declared once, in the build standard's
[file skeleton](/standards/build/skeleton.md); what goes inside each is
governed by that file's content standard, linked from the skeleton.

A repo's agent-navigated documentation is one
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog)
bundle, per the [OKF SPEC](/standards/references/okf-spec.md). The bundle is
the whole repository: an agent triages a document by its frontmatter and
navigates between documents by the per-directory `index.md` listings
([indexes.md](/standards/docs/indexes.md)), loading full bodies only when a
document is relevant.

## Concept documents and harness-owned files

Not every file in the repo is a concept document. The bundle divides in two:

- **Concept documents** — prose knowledge a reader loads to *understand*
  something: standards, guides, surveys, Decision Records, READMEs, the
  vocabulary. Each carries OKF frontmatter (`type` + `title` +
  `description`, per [document-types.md](/standards/docs/document-types.md)) and
  is subject to the type-lint.
- **Harness-owned files** — files a tool *consumes as configuration or runs
  as code*, not prose a reader loads to learn: every non-`.md` file, every
  `.md` under a top-level `tests/` tree, plus the Claude Code file set
  enumerated in [the harness-files registry](/standards/claude-code/files.md).
  These carry no OKF frontmatter and are not type-linted. They keep whatever
  format their consumer requires — a `SKILL.md` keeps its Claude Code
  frontmatter (`name`, `model`, …), not OKF frontmatter; a `tests/` markdown
  file is parser fixture data, often deliberately malformed, so it is never
  measured against OKF format at all.

The test is *how the file is used*, not where it sits: everything is in the
repo, hence in the bundle; harness-owned files are simply in-bundle
non-concept-documents. `CLAUDE.md` is the worked example — it is prose a
human could read, but Claude Code loads it as operating configuration, so
it is harness-owned and carries no OKF frontmatter.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope
(what goes in it), but depth varies by project. A CLI tool's README may be
10 lines. A simulation's may be 100. Both are conformant if the content
stays within scope.

**Presence is the status signal.** There are no explicit status fields. The
presence or absence of optional files signals the project's stage. A missing
`CONTEXT.md` means no vocabulary has needed pinning yet; a populated
`specs/` directory means the project is complex enough to warrant formal
requirements.

**No duplication across files.** Each piece of information has exactly one
home. Files reference each other rather than repeating content.

**Voice and structure are standardized.** Every doc in this hierarchy
follows [prose/conventions.md](/standards/prose/conventions.md) — declarative
present tense, one rule per section, current-state only.

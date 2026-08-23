---
type: Standard
title: CONTEXT.md Content
description: The CONTEXT.md vocabulary center — the installed format, plus the two workspace differences
---

# CONTEXT.md Content

CONTEXT.md is the repo's vocabulary disambiguation center: when several
words compete for one concept, pick one and retire the rest.

## Format

[CONTEXT-FORMAT.md](/dotfiles/.agents/skills/domain-modeling/CONTEXT-FORMAT.md)
gives the format, installed verbatim from mattpocock/skills alongside the
`/domain-modeling` skill: the `## Language` section, the `**Term**:`
definition shape, the `_Avoid_` alias line, and the rules that keep
definitions tight and specific to the project.

These differences hold in this workspace:

- **OKF frontmatter.** `type: Vocabulary`, `title`, and `description`, as
  every concept document carries
  ([document-types.md](/standards/knowledge-organization/document-types.md)).
- **One file, at the root.** The installed format's multi-context
  `CONTEXT-MAP.md` variant does not apply. `repo-lint` reports a `CONTEXT.md`
  outside the root as `build.forbidden`.

`## Language` is the one required section. `repo-lint` reports its absence as
`knowledge-organization.doc-shape`.

---
type: General-Sheet
title: Headings and Stints Encoding
description: The layer below the shape — how a Workstream's head file writes its frontmatter, its headings, and its stints so a check can read them, and where the file sits
---

# Headings and Stints Encoding

The layer below [the shape](/doc-types/workstream/contract-shape.md):
the form a Workstream's head file takes so deterministic code reads
every heading and every stint, and where the file sits. The Standard
that binds a head file to this encoding is
[Workstream Conventions](/standards/doc-type/workstream-conventions.md).

## The frontmatter

`type: Workstream`, `title`, and `description`. The description names
the line of work.

## The lead

The prose between the H1 and the first H2: what the work is and how it
relates to its parent and children. No part lives here and the parser
skips it.

## Headings

A heading is an H2 whose text is one name from the menu in
[Headings from the menu](/standards/doc-type/workstream-conventions.md#headings-from-the-menu).
Each name is used at most once. An H3 or deeper under a heading is part of its body, and
the body is opaque, except under Stints.

## Stints

The Stints section is one bulleted list, one entry per stint. An entry
opens with a bold run, `**Planned.**` for the planned stint or the date
it started, `**2026-09-24.**`, for a recorded one. Then the fields, each
a label, a colon, and a value, ending in a period:

```markdown
## Stints

- **Planned.** Loop: [Design Review](/loops/design-review.md). Budget: one session, to the user's approval.
- **2026-09-24.** Loop: [Design Review](/loops/design-review.md). Budget: two sessions. Spent: two sessions. Branch: `worktree-sandcastle-fronts`. Verdict: advance.
```

`Loop` links a file typed `Loop`, and `Budget` is free text. A
recorded entry adds `Spent` and `Branch`, and `Verdict`, one of
`advance`, `accept`, or `delete`, once the user has ruled. The planned
entry, if there is one, is first; the recorded entries follow, newest
first.

## Parent and children

Nothing in the head file writes them: the parser derives them from the
directory. A child's head file is reached from its parent's by a chain
of links between files of the parent's directory.

## Where a Workstream lives

A Workstream is `workstreams/<name>/WORKSTREAM.md`, typed `Workstream`,
and a child is `workstreams/<name>/<child>/WORKSTREAM.md`
([definition.md](/doc-types/workstream/definition.md#where-a-workstream-lives)).

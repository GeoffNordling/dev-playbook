---
type: Decision-Record
title: Per-Repo Prose Exemption — the .prose-lint-exempt File
description: Let each repo declare the paths its prose rules do not govern in a tracked root-level file, replacing the detector's hardcoded exemption roster
date: 2026-08-11
---

# Per-Repo Prose Exemption — the .prose-lint-exempt File

## Context

[0019](/docs/decisions/0019-one-word-for-the-person.md) banned the second noun
for the workspace's one actor, and enforcement rides the pin: a bump delivers
`prose.banned-word` to a consumer's entire tracked tree. The first bumps
beyond dev-playbook and spec-tools reached trees the rule was never measured
against — story-forge holds verbatim captures of employers' job postings and
career artifacts written for recruiters in that audience's own terms of art;
mission-control holds essays about humanity as a species, not the actor. The standard's Terminology section already exempted
"text this workspace does not own", but the implementation could not reach
these files: `type: Reference` frontmatter works only on Markdown, the
vendored-roots registry is a tuple hardcoded in dev-playbook, and the
detector's own two-file exemption roster (`BANNED_EXEMPT`) was equally
hardcoded. A consumer had no surface at all.

## Decision

Each repo declares its own exemptions in a tracked root-level
`.prose-lint-exempt`: one repo-relative path per line, files or directories, a
directory covering its whole subtree, `#` opening a comment line. Listed paths
are skipped by both prose rules. Any file is listable, indexes included; the
declaration file itself is structurally exempt, since an entry may
legitimately name a path carrying the banned word. The rule itself stays
absolute — the file narrows where it applies, in review-visible form, not what
it says. There is no inline pragma: a suppression is a declared path, not a
scattered annotation.

`BANNED_EXEMPT` is deleted; dev-playbook's own `.prose-lint-exempt` lists the
detector module and its test file, the two that must name the word to ban it.
`type: Reference` frontmatter stands for Markdown verbatim mirrors, as does
the vendored-roots registry. Exempting a file wholesale rather than rewording
it — mission-control's `principles.md`, whose subject is the species — is a
per-file call the repo makes in its own declaration.

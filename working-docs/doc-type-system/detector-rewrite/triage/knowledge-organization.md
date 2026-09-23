---
type: General-Sheet
title: Knowledge Organization
description: The triage of the knowledge-organization family's thirty-nine deterministic rules — fifteen kept, twenty-one restated or gaining a check, three deleted to a test, eleven escalated
---

# Knowledge Organization

Thirty-nine deterministic rules over eight Standards under
`standards/knowledge-organization/`, triaged per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md) by one
Opus agent. The stochastic rules in the same files are skipped. Every
measured number is from the worktree at `05a79d0`, read with a Python
script over `git ls-files` and `src/dev_playbook/md.py`; no gate was run.

Three detectors emit the family's ids today: `scripts/okf-lint` (18 ids),
`scripts/ref-lint` (3), and `scripts/repo-lint` (2). The other 16 rules
are `null` in `standards/verifiers.yaml`.

## context-content.md

Kept as written, the check matching the sentence:
`language-section-present` (`scripts/repo-lint:544`, `check_doc_shapes`,
looks for the line `## Language` outside fences in the root `CONTEXT.md`).

- **`frontmatter-declares-type-vocabulary`**,
  `standards/knowledge-organization/context-content.md:22`. Keep, add the
  check: read the root `CONTEXT.md` frontmatter and compare `type` to
  `Vocabulary`. Today `okf-lint` checks only that the type is registered
  (`scripts/okf-lint:436`). Holds today.
- **`term-definition-avoid-line`**,
  `standards/knowledge-organization/context-content.md:34`. Rewrite, gains
  its check.

  > Under `## Language` in `CONTEXT.md`, a paragraph whose first line
  > starts `**` is an entry. Its first line is only the term in bold. One
  > or more definition lines follow. A line that starts `_Avoid_:` is at
  > most one, is the last line of the entry, and is never outside an
  > entry.

  `wording only`. Check: split the `## Language` section into paragraphs
  at blank lines and headings, and test each one that starts `**`. A
  group introduction under an H3 is a paragraph that does not start `**`,
  so it passes. 14 entries today, 0 fail.

## cross-references.md

For the rows below, a reference is what `scripts/ref-lint` reads today
(`scan_file`, `scripts/ref-lint:154`): an inline link's target, and a bare
`~/workspace/` path outside a link, both outside code. Inline code is the
form the stochastic `inline-code-for-a-varying-location` governs, and no
check reads it as a reference: in this repo it holds commands such as
`git -C ~/workspace/mission-control push` and placeholders such as
`~/workspace/<repo>/`. "Fixed repo root" is the parent heading's test at
`standards/knowledge-organization/cross-references.md:101`: no directory
in the file's path is `skills`, `rules`, or `agents`
(`has_fixed_repo_root`, `src/dev_playbook/md.py:216`).

The per-line scan misses a link split across two lines (2 today) and does
not see an indented code block (one at
`dotfiles/dot-claude/skills/log-friction/SKILL.md:45`). Both go with the
markdown parser decision that is open in
[Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md).

Measured over 244 tracked `.md` files, numbered Decision Records aside:
770 `/` link targets, 159 `~/workspace/dev-playbook/`, 3
`~/workspace/<other repo>/`, 27 `~/.claude/`, 14 relative, 27 same-file
`#anchor`, 9 URIs.

- **`reference-resolves`**,
  `standards/knowledge-organization/cross-references.md:26`. Rewrite,
  meaning changed: escalation 1.

  > The target of a reference exists. A `/` target and a
  > `~/workspace/<this repo>/` target are read from the checkout root; a
  > relative target is read from the linking file's directory. A
  > `~/workspace/<other repo>/` target is read from that repo's main
  > checkout on this machine.

  Check: today's `status_of` (`scripts/ref-lint:138`), with relative
  targets added. The last sentence is today's enforcement, not today's
  sentence.
- **`fragment-anchor-matches-the-slug`**,
  `standards/knowledge-organization/cross-references.md:38`. Rewrite.

  > In a reference to a `.md` file that ends `#anchor`, the anchor is the
  > GitHub slug of a heading in that file.

  `wording only`. Check: `status_of` (`scripts/ref-lint:147`), extended to
  the targets `ref-lint` skips today: a same-file `#anchor` and a relative
  target. The 27 same-file anchors and the relative anchors all match
  today, so 0 new findings.
- **`headings-slugify-distinctly`**,
  `standards/knowledge-organization/cross-references.md:45`. Rewrite,
  meaning changed: escalation 2.

  > No two headings in a `.md` file, a numbered Decision Record aside,
  > have the same GitHub slug.

  Check: `github_slug` (`src/dev_playbook/md.py:98`) over each file's
  headings outside fences, and count repeats. `null` today.
- **`stable-named-anchor`**,
  `standards/knowledge-organization/cross-references.md:56`. Rewrite,
  meaning changed: escalation 3.

  > The `#anchor` of a reference does not name a heading whose text
  > starts with a section number, such as `3. Bundle Structure` or
  > `2.2.3 Revision`.

  Check: find the heading the anchor names, and match its text against
  `^\d+(\.\d+)*\.?\s`. `null` today.
- **`workspace-path-for-another-repo`**,
  `standards/knowledge-organization/cross-references.md:81`. Rewrite, part
  of escalation 4.

  > A reference to a file or a directory in another repo is a link whose
  > target starts `~/workspace/<repo>/`. A bare `~/workspace/<other repo>/`
  > path outside a link, and a relative target that goes above the repo
  > root, are findings.

  `wording only`, except for `~/.claude/` targets (escalation 4). Check:
  the two findings named. `null` today. 0 relative targets leave the repo
  root. The 4 bare cross-repo paths are 3 in the indented code block at
  `dotfiles/dot-claude/skills/log-friction/SKILL.md:45` and 1 link split
  across `dotfiles/dot-claude/skills/idea/SKILL.md:13-14`; with a
  CommonMark parse, 0 findings.
- **`slash-invocation-for-a-skill`**,
  `standards/knowledge-organization/cross-references.md:94`. Rewrite,
  meaning changed: escalation 5.

  > A link whose target is a skill's `SKILL.md` has the link text
  > `/<skill-name>`, where `<skill-name>` is the name of the skill's
  > directory.

  Check: compare the link text to the directory above `SKILL.md`. `null`
  today. 26 of 28 such links pass.
- **`root-absolute-path-in-the-same-repo`**,
  `standards/knowledge-organization/cross-references.md:106`. Rewrite.

  > In a file with a fixed repo root, a reference to a file or a directory
  > of the same repo is a link whose target starts `/` and is the path
  > from the repo root. A relative target, and a
  > `~/workspace/<this repo>/` target in a link or bare, are findings.

  `wording only`. Check: today's `wrong-form` (`scripts/ref-lint:178`)
  flags only the `~/workspace/<this repo>/` form; add relative targets.
  0 relative targets and 0 bare same-repo paths in fixed-root files today,
  so 0 new findings. `dotfiles/dot-claude/CLAUDE.md` counts as fixed-root
  under the segment test, although every repo loads it; its one same-repo
  path at line 7 is inline code and is not read.
- **`workspace-path-for-a-stable-location`**,
  `standards/knowledge-organization/cross-references.md:125`. Rewrite, part
  of escalation 4.

  > In a file with no fixed repo root, a reference to a file of the same
  > repo, outside the file's own skill bundle, is a link whose target
  > starts `~/workspace/<repo>/`. A `/` target, and a relative target that
  > goes out of the file's own `skills/<name>/` directory, are findings.

  `wording only` for these two findings; `~/.claude/` targets are
  escalation 4. Check: `null` today. 56 files have no fixed repo root;
  0 `/` targets and 0 relative targets that leave a bundle.
- **`relative-path-inside-the-bundle`**,
  `standards/knowledge-organization/cross-references.md:138`. Rewrite,
  gains its check.

  > In a skill bundle, a reference to another file of the same bundle is
  > a link with a relative target. A `/`, `~/workspace/`, or `~/.claude/`
  > target that resolves inside the linking file's own `skills/<name>/`
  > directory is a finding.

  `wording only`. Check: resolve each absolute target and test whether it
  falls under the bundle directory. `null` today; 0 findings.

## documentation-sets.md

- **`an-index-in-every-directory`**,
  `standards/knowledge-organization/documentation-sets/documentation-sets.md:36`.
  Rewrite.

  > Every directory that has a concept document in it, a numbered Decision
  > Record or a `type: Mirror` file included, has an `index.md`.

  `wording only`. Check: `check_indexes` (`scripts/okf-lint:536`) flags
  each directory of a concept document with no `index.md`. A missing root
  `index.md` today comes out as `okf-version-declared`
  (`scripts/okf-lint:526`); it moves to this id.

## working-documentation-sets.md

- **`every-member-reached-from-rootmd`**,
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:43`.
  Rewrite, gains its check; escalation 6 for the 26 files it fails.

  > Every `.md` file of a working documentation set other than an
  > `index.md` is reached from its `ROOT.md` by a chain of links between
  > files of the set. A link in an `index.md` is not part of a chain. The
  > `ROOT.md` of a file is the one in its own directory or the nearest
  > directory above; the `ROOT.md` of a strand is reached from the next
  > `ROOT.md` above it.

  `wording only`. Check: build the link graph of the set, `index.md`
  files left out, and walk it from each `ROOT.md`. `null` today.
- **`one-directory-under-working-docs`**,
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:53`.
  Rewrite, gains its check.

  > Every directory directly under `working-docs/` has an `index.md` and a
  > `ROOT.md`. Every file under it has a lowercase kebab-case name, such
  > as `detector-fixes.md`, except `index.md`, `ROOT.md`, `README.md`,
  > `PROMPT.md`, `SKILL.md`, `CLAUDE.md`, and a Python module.

  `wording only`. Check: a name test on each file's stem,
  `^[a-z0-9]+(-[a-z0-9]+)*$`, and a presence test per set. `null` today;
  2 sets, 0 findings.
- **`working-docs-holds-only-sets`**,
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:65`.
  Rewrite, gains its check.

  > `working-docs/` directly has `index.md`, directories, and no other
  > file.

  `wording only`. Check: list the entries directly under `working-docs/`.
  `null` today; 0 findings.
- **`one-list-of-items-state-by-section`**,
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:74`.
  Rewrite, gains its check.

  > In a working documentation set, every `ROOT.md` with no `ROOT.md` in
  > a directory below it has exactly one `## Planned` and one
  > `## Completed` section, and no other file of the set has either. Each
  > bullet directly under them starts with a bold name.

  `wording only`. A strand held in one file, which the introduction at
  line 21 allows, has no worklist of its own under this sentence, as
  under today's. Check: headings and first bullet lines per file. `null`
  today; 7 `ROOT.md` files, 0 findings. A lead-in sentence under
  `Planned` is not a bullet and passes (3 files have one).

## document-types.md

Kept as written, the check matching the sentence:
`frontmatter-a-yaml-mapping`, `type-names-a-registered-type`,
`non-empty-title`, `non-empty-description-no-closing-period`,
`recipe-description-carries-a-resource`, `standard-lives-under-standards`,
`loop-lives-under-loops`, `guide-lives-under-guides`. All eight are
`check_types`, `scripts/okf-lint:424`.

- **`resource-a-repo-root-path-or-a-uri`**,
  `standards/knowledge-organization/document-types.md:79`. Keep, add the
  check: a `resource` value starts `/` or matches
  `^[a-zA-Z][a-zA-Z0-9+.-]*:`. `null` today; 3 values, 0 findings.
- **`no-tags-or-timestamp`**,
  `standards/knowledge-organization/document-types.md:93`. Keep, add the
  check: the frontmatter mapping has neither key. `null` today;
  0 findings.

## indexes.md

Kept as written, the check matching the sentence: `okf-version-declared`
(`scripts/okf-lint:628`).

- **`no-okf-type`**, `standards/knowledge-organization/indexes.md:24`.
  Rewrite, gains its check.

  > The frontmatter of an `index.md` has no `type` key.

  `wording only`. Check: read the frontmatter of each `index.md`. `null`
  today; 41 files, 0 findings.
- **`introduction-between-h1-and-listing`**,
  `standards/knowledge-organization/indexes.md:30`. Rewrite.

  > An `index.md` has at least one line of prose between its H1 and its
  > first listed entry. A heading and an `Ordering:` line are not prose.

  `wording only`: the second sentence says what `check_index_intro`
  (`scripts/okf-lint:639`) already skips.
- **`one-entry-per-concept-document-and-child-directory`**,
  `standards/knowledge-organization/indexes.md:48`. Rewrite.

  > An `index.md` has exactly one bullet for each concept document in its
  > directory and one for each child directory's `index.md`, and no other
  > bullet in its listing. Each bullet is a link whose target starts `/`.
  > A concept document's bullet ends with ` — ` and that document's
  > frontmatter `description`, character for character.

  `wording only`. Check: `check_indexes` (`scripts/okf-lint:557`), with
  the two gaps from
  [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
  closed: a child index listed twice (today a set) and a bullet with no
  `/` link (today invisible to `INDEX_BULLET`). 0 new findings. Today the
  check expects the nearest index below, not the child's; no directory in
  this repo lacks an `index.md` while a directory below it has one, so
  the two agree.
- **`alphabetical-unless-declared-otherwise`**,
  `standards/knowledge-organization/indexes.md:58`. Rewrite, meaning
  changed: escalation 7.

  > In an `index.md`, the `README.md` bullet, where there is one, is the
  > first bullet. The concept-document bullets come next, then the
  > child-directory bullets, and each group is sorted by link text,
  > ignoring case. A line that starts `Ordering:` above the first bullet
  > turns off the sorting and the group order, and never moves the
  > `README.md` bullet.

  Check: `check_index_ordering` (`scripts/okf-lint:680`), with the group
  order added and the `README.md` test run over the whole listing, not
  the concept group only.

## readme-content.md

- **`readme-holds-an-h1`**,
  `standards/knowledge-organization/readme-content.md:15`. Rewrite.

  > Every `README.md` has an H1.

  `wording only`. Check: `check_doc_shapes` (`scripts/repo-lint:547`)
  opens the root `README.md` only; run it over every `README.md`. 7 files,
  0 findings.

## type-registry.md

Kept as written, the check matching the sentence:
`type-name-to-description`, `keys-in-alphabetical-order`. Both are
`check_local_types`, `scripts/okf-lint:306`, run in a repo without
`standards/build/canonical/`.

- **`type-name-in-first-cell`**,
  `standards/knowledge-organization/type-registry.md:30`. Delete, escalation
  8: its member is the table dev-playbook's checker reads, which a test
  over `sources.py` covers.
- **`description-in-second-cell`**,
  `standards/knowledge-organization/type-registry.md:38`. Delete, escalation
  8, the same reason. `null` today.
- **`rows-in-alphabetical-order`**,
  `standards/knowledge-organization/type-registry.md:47`. Delete, escalation
  8, the same reason.
- **`add-never-shadow`**, `standards/knowledge-organization/type-registry.md:84`.
  Rewrite.

  > No key of the `okf_types` mapping is equal, ignoring case, to a type
  > name in the table under `` `type` names a registered type `` in
  > `standards/knowledge-organization/document-types.md`, or to an earlier
  > key of the same mapping.

  `wording only`: the old body names a `## Types` table, a heading no
  file has. Check: `check_local_types` (`scripts/okf-lint:374`).

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
The number is the one the rows above cite.

1. `reference-resolves`,
   `standards/knowledge-organization/cross-references.md:26`: built in
   full, relative targets included; the two placeholder links became
   code spans, a fix the user approved by name.
2. `headings-slugify-distinctly`,
   `standards/knowledge-organization/cross-references.md:45`: built,
   with the Decision Record exception.
3. `stable-named-anchor`,
   `standards/knowledge-organization/cross-references.md:56`: built,
   narrowed to the row's blockquote.
4. `workspace-path-for-a-stable-location` and
   `workspace-path-for-another-repo`,
   `standards/knowledge-organization/cross-references.md:125` and
   `:81`: built, `~/.claude/` named as a target form in both.
5. `slash-invocation-for-a-skill`,
   `standards/knowledge-organization/cross-references.md:94`:
   stochastic, a prose mention is not a function's to decide.
6. `every-member-reached-from-rootmd`,
   `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:43`:
   built in full; `working-docs/software-factory/ROOT.md` gained a
   Members section linking all 26 files, a fix the user approved by
   name.
7. `alphabetical-unless-declared-otherwise`,
   `standards/knowledge-organization/indexes.md:58`: built, the row's
   reading: the concept-document group before the child-directory
   group, and an `Ordering:` line turns that group order off too.
8. `type-name-in-first-cell`, `description-in-second-cell`, and
   `rows-in-alphabetical-order`,
   `standards/knowledge-organization/type-registry.md:30`, `:38`, and
   `:47`: the three rules deleted; the test on the `sources.py`
   constant asserts the three shapes.

New rules below: `README` accepted; `Vocabulary` rejected, the user
keeps other Vocabulary files open.

## New rules

- **`README.md` is typed `README`**, under `document-types.md`: a concept
  document named `README.md` has `type: README`, and no document of
  another name has it. Today this is only a phrase in the `README` row of
  the type table, "filename `README.md` ⟺ `type: README`". 7 `README.md`
  files, 0 findings.
- **Only `CONTEXT.md` is typed `Vocabulary`**, under `document-types.md`:
  no concept document other than the root `CONTEXT.md` has
  `type: Vocabulary`. Today this is only "(lives in `CONTEXT.md`)" in the
  `Vocabulary` row. 1 file, 0 findings.

## Acronyms

- **CI** — continuous integration.
- **OKF** — Open Knowledge Format.
- **URI** — Uniform Resource Identifier.
- **YAML** — YAML Ain't Markup Language.

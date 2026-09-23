---
type: General-Sheet
title: Knowledge Organization
description: The rewrite of the knowledge-organization family's thirty-nine deterministic rules and one new rule — thirty-five checks over the model, two tagged workspace, three deleted per their escalation, one made stochastic, one set aside, eight Standards edited to the triage, and okf-lint, ref-lint, and repo-lint retired
---

# Knowledge Organization

The step built `src/dev_playbook/checks/knowledge_organization.py` and
`tests/dev_playbook/checks/test_knowledge_organization.py` from
[the knowledge-organization triage](/working-docs/doc-type-system/detector-rewrite/triage/knowledge-organization.md).
The module holds thirty-five functions and no hook registration. The
`DETECTORS` roster in `src/dev_playbook/playbook_lint.py` now holds only
`loop-lint`.

A reference is an inline link's target or a bare `~/workspace/` path
outside a link, read from the model's lines outside fences, with inline
code stripped, and with an indented code block left out. A link whose
text wraps a line is one link. A numbered Decision Record is not read
as a source.

## Built

### context-content.md

- `knowledge-organization.frontmatter-declares-type-vocabulary`:
  function `frontmatter_declares_type_vocabulary`, new; body kept.
- `knowledge-organization.language-section-present`: function
  `language_section_present`, ported from `check_doc_shapes`; body
  kept.
- `knowledge-organization.term-definition-avoid-line`: function
  `term_definition_avoid_line`, new. The body is the triage blockquote;
  the example block stays. 14 entries pass.

### cross-references.md

- `knowledge-organization.reference-resolves`: function
  `reference_resolves`, ported from `status_of` with relative targets
  added, tagged `workspace`. The body is the triage blockquote.
- `knowledge-organization.fragment-anchor-matches-the-slug`: function
  `fragment_anchor_matches_the_slug`, ported with same-file and
  relative targets added, tagged `workspace` since it reads another
  repo's file for its anchor. The body is the triage blockquote.
- `knowledge-organization.headings-slugify-distinctly`: function
  `headings_slugify_distinctly`, new. The body is the triage
  blockquote.
- `knowledge-organization.stable-named-anchor`: function
  `stable_named_anchor`, new, over targets in this repo. The body is
  the triage blockquote.
- `knowledge-organization.workspace-path-for-another-repo`: function
  `workspace_path_for_another_repo`, new. The body is the triage
  blockquote.
- `knowledge-organization.root-absolute-path-in-the-same-repo`:
  function `root_absolute_path_in_the_same_repo`, ported from the
  `wrong-form` status with relative targets added. The body is the
  triage blockquote.
- `knowledge-organization.workspace-path-for-a-stable-location`:
  function `workspace_path_for_a_stable_location`, new. The body is
  the triage blockquote.
- `knowledge-organization.relative-path-inside-the-bundle`: function
  `relative_path_inside_the_bundle`, new. The body is the triage
  blockquote.
- `knowledge-organization.slash-invocation-for-a-skill`: stochastic
  per escalation 5; the trailer's kind changed and the body is kept.

### document-types.md

- `frontmatter-a-yaml-mapping`, `type-names-a-registered-type`,
  `non-empty-title`, `non-empty-description-no-closing-period`,
  `recipe-description-carries-a-resource`,
  `standard-lives-under-standards`, `loop-lives-under-loops`,
  `guide-lives-under-guides`: one function each, named for the slug,
  ported from `check_types`; bodies kept. The registry is the new
  `sources.REGISTERED_TYPES`, unioned with a consumer's `okf_types`
  keys.
- `knowledge-organization.resource-a-repo-root-path-or-a-uri`,
  `knowledge-organization.no-tags-or-timestamp`: one function each,
  new; bodies kept.
- `knowledge-organization.readmemd-is-typed-readme`: function
  `readmemd_is_typed_readme`, the accepted new rule `README.md` is
  typed `README`, added last in the file. 7 files pass. The file's
  `description` and its index row name it.

### documentation-sets.md

- `knowledge-organization.an-index-in-every-directory`: function
  `an_index_in_every_directory`, ported from `check_indexes`, the
  missing root `index.md` included. The body is the triage blockquote.

### working-documentation-sets.md

- `knowledge-organization.one-directory-under-working-docs`,
  `knowledge-organization.working-docs-holds-only-sets`,
  `knowledge-organization.one-list-of-items-state-by-section`: one
  function each, new. Each body is its triage blockquote; the link each
  old body held to the general rule it qualifies moved into a Why.

### indexes.md

- `knowledge-organization.no-okf-type`: function `no_okf_type`, new.
  The body is the triage blockquote.
- `knowledge-organization.introduction-between-h1-and-listing`:
  function `introduction_between_h1_and_listing`, ported from
  `check_index_intro`. The body is the triage blockquote.
- `knowledge-organization.one-entry-per-concept-document-and-child-directory`:
  function `one_entry_per_concept_document_and_child_directory`, ported
  from `check_indexes` with the two gaps from
  [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
  closed. The body is the triage blockquote.
- `knowledge-organization.alphabetical-unless-declared-otherwise`:
  function `alphabetical_unless_declared_otherwise`, ported from
  `check_index_ordering` with the group order added. The body is the
  triage blockquote.
- `knowledge-organization.okf-version-declared`: function
  `okf_version_declared`, ported; body kept.

### readme-content.md

- `knowledge-organization.readme-holds-an-h1`: function
  `readme_holds_an_h1`, ported from `check_doc_shapes` over every
  `README.md`. The body is the triage blockquote.

### type-registry.md

- `knowledge-organization.type-name-to-description`,
  `knowledge-organization.keys-in-alphabetical-order`: one function
  each, ported from `check_local_types`; bodies kept.
- `knowledge-organization.add-never-shadow`: function
  `add_never_shadow`, ported. The body is the triage blockquote.

The file's `description` and its index row now say what it holds, the
consumer's `okf_types` mapping; its opening no longer names the
retired detector.

## Deleted

- `knowledge-organization.type-name-in-first-cell`,
  `knowledge-organization.description-in-second-cell`, and
  `knowledge-organization.rows-in-alphabetical-order`, escalation 8,
  with the `Global table` condition they emptied. Four tests in
  `tests/dev_playbook/test_sources.py` pin `sources.REGISTERED_TYPES`
  to the table and assert the three shapes. No link pointed at them.

## Retired

- `scripts/okf-lint` and `tests/test_okf_lint.py`.
- `scripts/ref-lint` and `tests/test_ref_lint.py`.
- `scripts/repo-lint`, `tests/test_repo_lint.py`, and
  `src/dev_playbook/pyast.py` with `tests/dev_playbook/test_pyast.py`,
  which only `repo-lint` imported.
- Three roster lines in `DETECTORS`, both tuples each for `okf-lint`
  and `repo-lint` in `tests/test_rule_registry.py`, and three rows of
  the table in `scripts/README.md`.
- Mentions repointed in `CANDIDATES.md`, `CONTEXT.md`, `Makefile`,
  `pyproject.toml`, `guides/bootstrap.md`, `guides/consuming.md`,
  `doc-types/standard/definition.md`, `doc-types/standard/encoding.md`,
  eight numbered Decision Records, `standards/harness/files.md`,
  `standards/harness/claude-content.md`, `standards/standard/detectors.md`,
  four files under `dotfiles/dot-claude/`, the permission entries in
  `dotfiles/dot-claude/settings.json`, and comments in `md.py`,
  `repo_init.py`, `playbook_lint.py`, the viewer, and three tests.
- Left for the cut-over: `SKIP: ref-lint` in the canonical `ci.yml`,
  its shipped copy, and this repo's workflow, and the Why at
  `standards/build/canonical.md:30` that explains it. Left for a
  ruling: `SKIP=ref-lint` in `dotfiles/.bashrc.d/machine-env.sh` and
  its bullet in `docs/machines.md`. The skip now stands nothing down,
  and the `playbook-check` hook runs the two `workspace` checks on a
  secondary machine with no way to leave them out.

## Set aside

- `knowledge-organization.every-member-reached-from-rootmd`, built in
  full per escalation 6. It fails 10 files: the rewrite reports under
  `working-docs/doc-type-system/detector-rewrite/rewrite/`, which only
  that directory's `index.md` links, and `index.md` links are no part
  of a chain. The rule left `working-documentation-sets.md`, and the
  file's `description` and index row no longer name a link tree:

  > Every `.md` file of a working documentation set other than an
  > `index.md` is reached from its `ROOT.md` by a chain of links between
  > files of the set. A link in an `index.md` is not part of a chain. The
  > `ROOT.md` of a file is the one in its own directory or the nearest
  > directory above; the `ROOT.md` of a strand is reached from the next
  > `ROOT.md` above it.

  The check built the link graph of the set, `index.md` files left out,
  and walked it from each member's `ROOT.md`. The link to the rule in
  `dotfiles/dot-claude/skills/doc-set-diagram/SKILL.md` now names the
  file.

## Measured

- `uv run playbook check .`: 0.53 s, 102 checks over 460 files, zero
  findings.
- `scripts/playbook-lint .`: 0.15 s, clean.

## Acronyms

- **OKF** — Open Knowledge Format.
- **URI** — Uniform Resource Identifier.
- **YAML** — YAML Ain't Markup Language.

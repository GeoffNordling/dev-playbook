---
type: General-Sheet
title: Knowledge Organization Rulings
description: The knowledge-organization family agent's work order — every rule under standards/knowledge-organization/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Knowledge Organization Rulings

The work order of the `knowledge-organization` family agent: every rule under `standards/knowledge-organization/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `knowledge-organization.glossary-only` | knowledge-organization/context-content.md | keep | stochastic |  |
| `knowledge-organization.vocabulary-type` | knowledge-organization/context-content.md | keep | deterministic |  |
| `knowledge-organization.the-language-section` | knowledge-organization/context-content.md | keep | deterministic |  |
| `knowledge-organization.entry-shape` | knowledge-organization/context-content.md | rewrite | deterministic | Block: the example block is rewritten to match `CONTEXT.md`: no colon after the bold term, one H3 group shown. |
| `knowledge-organization.tight-definitions` | knowledge-organization/context-content.md | rewrite | stochastic | Sentence: An entry's definition in a repo's `CONTEXT.md` is at most two sentences: one that says what the term is, and at most one more that sharpens it; where a concept document defines the term the definition links that document. |
| `knowledge-organization.project-terms-only` | knowledge-organization/context-content.md | keep | stochastic |  |
| `knowledge-organization.reference-resolves` | knowledge-organization/cross-references.md | rewrite | deterministic | Sentence: A reference names a file or a directory that exists in the referencing file's own repository<br>Why: A `~/workspace/<repo>/` target naming another repository resolves against that repo's main checkout. A repo cannot check the other side from its own files, so the predicate binds same-repo targets. |
| `knowledge-organization.fragment-anchor-matches-the-slug` | knowledge-organization/cross-references.md | keep | deterministic |  |
| `knowledge-organization.stable-named-anchor` | knowledge-organization/cross-references.md | rewrite | deterministic | Sentence: A reference's `#anchor` carries no number that is the heading's position in the file; where the target numbers every heading by position and carries no other anchor, the reference carries no anchor.<br>Why: *stands.* An anchor names the concept the heading carries and so survives a renumbering; a positional number breaks on the next insert. |
| `knowledge-organization.citation-another-repo` | knowledge-organization/cross-references.md | rewrite | deterministic | Block: the file's `population` phrase and preamble gain `except inside a code block, fenced or indented`; the rule sentence stands. |
| `knowledge-organization.skill-invocation` | knowledge-organization/cross-references.md | rewrite | deterministic | Sentence: A reference to a skill names it by its slash invocation, `/<skill-name>`. |
| `knowledge-organization.fixed-repo-root` | knowledge-organization/cross-references.md | condition |  |  |
| `knowledge-organization.link-same-bundle` | knowledge-organization/cross-references.md | keep | deterministic |  |
| `knowledge-organization.no-fixed-repo-root` | knowledge-organization/cross-references.md | condition |  |  |
| `knowledge-organization.workspace-path-for-a-stable-location` | knowledge-organization/cross-references.md | rewrite | deterministic | Sentence: A reference to a file in the referencing file's own repository is an inline link whose target is the full `~/workspace/<repo>/<path>` path, unless the target is inside the referencing file's own skill bundle.<br>Why: The condition above says what stable means: a location fixed relative to the repo root. |
| `knowledge-organization.relative-path-inside-the-bundle` | knowledge-organization/cross-references.md | keep | deterministic |  |
| `knowledge-organization.inline-code-for-a-varying-location` | knowledge-organization/cross-references.md | keep | stochastic |  |
| `knowledge-organization.frontmatter-block` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.types` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.title` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.description` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.description-voice` | knowledge-organization/document-types.md | rewrite | stochastic | Sentence: A concept document's `description` is a sentence fragment in the present tense that names what the document is, what it governs, or, for a `Decision-Record`, the decision it records. |
| `knowledge-organization.resource` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.resource-names-the-asset` | knowledge-organization/document-types.md | keep | stochastic |  |
| `knowledge-organization.no-tags-or-timestamp` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.recipe-description` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.typed-standard` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.typed-loop` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.typed-guide` | knowledge-organization/document-types.md | keep | deterministic |  |
| `knowledge-organization.an-index-in-every-directory` | knowledge-organization/documentation-sets/documentation-sets.md | keep | deterministic |  |
| `knowledge-organization.body-inside-its-concern` | knowledge-organization/documentation-sets/documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.rows-inside-the-set` | knowledge-organization/documentation-sets/documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.one-home` | knowledge-organization/documentation-sets/documentation-sets.md | rewrite | stochastic | Sentence: A fact, rule, or decision has one home, the member whose concern is the thing the fact binds and the most general such member where the fact still holds; every other document in this repo links there and states the fact without its reason.<br>Why: *stands.* The same holds across repos: another repo links here rather than restating. A repo cannot check the other side. |
| `knowledge-organization.distinct-concerns` | knowledge-organization/documentation-sets/documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.distinct-from-the-parent` | knowledge-organization/documentation-sets/documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.terms-defined-once` | knowledge-organization/documentation-sets/documentation-sets.md | delete |  |  |
| `knowledge-organization.terms-that-cross-sets` | knowledge-organization/documentation-sets/documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.speculative-voice` | knowledge-organization/documentation-sets/working-documentation-sets.md | rewrite | stochastic | Sentence: Every member of a working documentation set writes a guess as a guess, and the set's `ROOT.md` declares the set speculative. |
| `knowledge-organization.the-link-tree` | knowledge-organization/documentation-sets/working-documentation-sets.md | keep | deterministic |  |
| `knowledge-organization.where-a-set-lives` | knowledge-organization/documentation-sets/working-documentation-sets.md | rewrite | deterministic | Sentence: A working documentation set is one directory under `working-docs/` at the repo root, `working-docs/<work>/`, holding the set's `index.md`, its `ROOT.md`, and its members under lowercase kebab-case names, flat or in subdirectories, except a member whose kind fixes its name (`README.md`, `PROMPT.md`, `SKILL.md`, `CLAUDE.md`, a Python module). |
| `knowledge-organization.a-set-stands-on-main` | knowledge-organization/documentation-sets/working-documentation-sets.md | guide |  | Guide: `guides/governed-repo.md` |
| `knowledge-organization.working-docs-holds-only-sets` | knowledge-organization/documentation-sets/working-documentation-sets.md | keep | deterministic |  |
| `knowledge-organization.worklist` | knowledge-organization/documentation-sets/working-documentation-sets.md | keep | deterministic |  |
| `knowledge-organization.buckets` | knowledge-organization/documentation-sets/working-documentation-sets.md | rewrite | stochastic | Sentence: Every fact in a member of a working documentation set sits under a named section, its bucket, and a bucket holds facts of its own type only; the section under the member's H1, which says what the member is and what it is for, is exempt. |
| `knowledge-organization.terms` | knowledge-organization/documentation-sets/working-documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.acronyms` | knowledge-organization/documentation-sets/working-documentation-sets.md | keep | stochastic |  |
| `knowledge-organization.typeless` | knowledge-organization/indexes.md | keep | deterministic |  |
| `knowledge-organization.the-introduction` | knowledge-organization/indexes.md | keep | deterministic |  |
| `knowledge-organization.the-opening-sentence` | knowledge-organization/indexes.md | keep | stochastic |  |
| `knowledge-organization.the-listing` | knowledge-organization/indexes.md | keep | deterministic |  |
| `knowledge-organization.ordering` | knowledge-organization/indexes.md | keep | deterministic |  |
| `knowledge-organization.the-root-index` | knowledge-organization/indexes.md | condition |  |  |
| `knowledge-organization.okf-version-declared` | knowledge-organization/indexes.md | keep | deterministic |  |
| `knowledge-organization.h1` | knowledge-organization/readme-content.md | keep | deterministic |  |
| `knowledge-organization.the-purpose-sentence` | knowledge-organization/readme-content.md | keep | stochastic |  |
| `knowledge-organization.no-agent-instructions-or-decisions` | knowledge-organization/readme-content.md | keep | stochastic |  |
| `knowledge-organization.no-roster-of-harness-injected-files` | knowledge-organization/readme-content.md | keep | stochastic |  |
| `knowledge-organization.global-table` | knowledge-organization/type-registry.md | condition |  |  |
| `knowledge-organization.row-shape` | knowledge-organization/type-registry.md | keep | deterministic |  |
| `knowledge-organization.row-description` | knowledge-organization/type-registry.md | rewrite | deterministic | Sentence: Every row of the `## Types` table below its header holds, in its second cell, non-empty text on one line.<br>Why: The second cell is a description a reader picks the type by. |
| `knowledge-organization.alphabetical-order` | knowledge-organization/type-registry.md | keep | deterministic |  |
| `knowledge-organization.local-declaration` | knowledge-organization/type-registry.md | condition |  |  |
| `knowledge-organization.mapping-entry-shape` | knowledge-organization/type-registry.md | rewrite | deterministic | Sentence: Each entry's key is a type name in Title Case, hyphen-joined for a multi-word name, and its value is non-empty text on one line.<br>Why: The value is a description a reader picks the type by. |
| `knowledge-organization.alphabetical-keys` | knowledge-organization/type-registry.md | keep | deterministic |  |
| `knowledge-organization.add-never-shadow` | knowledge-organization/type-registry.md | keep | deterministic |  |

## Acronyms

- **H1** — markdown heading level one.
- **H3** — markdown heading level three.

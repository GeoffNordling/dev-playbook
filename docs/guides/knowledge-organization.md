---
type: Guide
title: Knowledge Organization Guide
description: The thinking behind the knowledge-organization rules — what CONTEXT.md is for, why a reference takes the form it does, what a description is for, how a documentation set stays navigable, what a working set is, how an index reads, how a Loop is checked, and why a type registry is frontmatter
---

# Knowledge Organization Guide

The guide behind the nine knowledge-organization rulesets under
[standards/knowledge-organization/](/standards/knowledge-organization/index.md).
Each states its rules as predicates okf-lint, ref-lint, loop-lint,
repo-lint, or a reviewer can decide; this guide carries the templates,
the examples, and the reasoning. Nothing here is enforced.

## CONTEXT.md is a glossary

A repo's `CONTEXT.md` is a glossary and nothing else
([Glossary only](/standards/knowledge-organization/context-content.md#glossary-only)):
implementation decisions live in Decision Records, specifications in
their own documents. Its shape:

````md
---
type: Vocabulary
title: {Context Name}
description: {One-line description of the vocabulary}
---

# {Context Name}

{One or two sentences on what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request
````

When several words exist for one concept, the entry picks the best one
and lists the others under `_Avoid_`. The test before adding a term: is
this a concept unique to this context, and used beyond the
documentation set that defines it? Only then does it belong
([Project terms only](/standards/knowledge-organization/context-content.md#project-terms-only)).
A general programming concept has no entry however heavily the project
uses it, and a term one set defines and uses within itself stays in
that set.

## Why a reference takes the form it does

A root-absolute link, `/standards/prose/conventions.md`, resolves
against the reader's own checkout root, so it points at the copy that
matches the checkout the reader is in, main checkout or per-issue
worktree
([Link, same bundle](/standards/knowledge-organization/cross-references.md#link-same-bundle)).
A same-repo reference written `~/workspace/<this-repo>/…` fails
ref-lint as `wrong-form` whether or not the target exists: from inside
a worktree that path jumps to the main checkout, a different and
possibly stale copy.

A cross-repo citation, `~/workspace/mission-control/friction/log.md`,
resolves to that repo's main checkout, its published state
([Citation, another repo](/standards/knowledge-organization/cross-references.md#citation-another-repo)).
The form is self-describing: the repo name is in the path, so no
external convention is needed to interpret it.

A runbook, a skill bundle, an agent definition, or a global rule under
`~/.claude/` is loaded across arbitrary repos, with no root for `/` to
resolve against, which is why those files cite by workspace path even
inside their own repo and by relative path inside their own bundle
([No fixed repo root](/standards/knowledge-organization/cross-references.md#no-fixed-repo-root)).

The wrapper records intent: an inline link means "go open this";
inline code means "this file exists conceptually", the right form for
a file whose location varies between repos; a bare `/<skill-name>` is
how a skill is invoked. ref-lint treats inline code and a bare
invocation as prose.

An anchor names a heading by its GitHub slug, which ref-lint computes,
so a stale or misspelled anchor fails the commit. A positional anchor,
`#223-revision` or an in-prose `§2.10`, breaks silently the moment its
target is renumbered or reordered
([Stable named anchor](/standards/knowledge-organization/cross-references.md#stable-named-anchor)).

## What a description is for

A concept document's `description` powers triage and the authored
`index.md` listings, which carry it verbatim. It is a sentence fragment
in the present tense, leading with what distinguishes the document,
roughly one breath, twenty words as a soft limit, with no trailing
period ([Description](/standards/knowledge-organization/document-types.md#description)).
`resource`, where present, names the asset the document describes,
`/dotfiles/dot-claude/workflows/ralph-loop.js` for a
`Recipe-Description`; a companion skill is linked in the body, not in
`resource`. `tags` and `timestamp`, the OKF spec's optional keys, stay
absent.

## How a documentation set stays navigable

A set is the concept documents one `index.md` owns, and a subdirectory
holding concept documents carries an `index.md` of its own and is a
child set, never absorbed into the parent's listing
([An index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)).
A set is then exactly one directory, so the tree a reader walks is the
tree of sets, and every directory declares its concern in an
introduction sentence of its own. A set is judged with no neighbour's
body open.

A member serves the one purpose its description states. A section the
reader would not have predicted is a second purpose: it splits into a
member of its own, or into a directory of members with an `index.md`
where the purposes nest, or the description was wrong and is
rewritten. A reader crawling for one answer then loads one small file.
A row the reader would not expect sits in the wrong set, or the
introduction is too narrow and is rewritten.

A fact has one home because the reason is what drifts, so it is written
once, at the home
([One home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home)).
A second place that argues the fact is a duplicate; a place that names
it and links the home is not. Two neighbouring concerns draw their
boundary where there is room, in each lead paragraph, each linking the
other. Two whose descriptions cannot be told apart are one concern
written twice, and merge; a child set whose introduction cannot be
told apart from its parent's is the parent's concern written twice,
and its members merge upwards.

A term used beyond the set that coins it earns a one-sentence gloss in
the repo's `CONTEXT.md` that links the definition, the way an index
row links a member
([Terms that cross sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-that-cross-sets)).
A definition is a fact like any other, so its home follows one home.

## What a working documentation set is

A working documentation set is the Markdown one stream of in-process
work accumulates, one directory under `working-docs/` named for the
work and not for a branch, and it lives as long as the work does, on
every branch the work touches and on `main` between them
([Where a set lives](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#where-a-set-lives)).
`working-docs/` itself is a plain parent: its `index.md` lists the
sets, and it holds no `ROOT.md` and no members of its own. A
subdirectory of a set that holds a `ROOT.md` is a strand; one that
holds none is governed by the nearest `ROOT.md` above it.

A set stands on `main` because the speculative voice lets it: a reader
meets a guess marked as a guess, and the worklist shows where the work
is. The work ends when its Planned bucket is empty; then the set is
drained or deleted, and an empty `working-docs/` stays. A set under
`docs/` is the defect, since `docs/` holds permanent documents.

The link tree is the set's second structure, over the tree of sets: a
member links what it depends on, its parent, its children, the sibling
whose fact it defers to. `ROOT.md` need not link every member, but a
member no path from `ROOT.md` reaches is an orphan, listed or not
([The link tree](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#the-link-tree)).

The buckets are a menu, one home made navigable: a set uses the buckets
its work needs, skips the rest, and coins its own where none fits, and
a bucket the set does not use is never a finding
([Buckets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#buckets)).
`Unfiled` is the escape valve, so material fitting no bucket lands
somewhere explicit instead of being force-fitted or scattered. A term
of the work is defined in a `ROOT.md`'s Terms bucket rather than in
`CONTEXT.md` because it crosses no set until the set drains: it earns
its `CONTEXT.md` entry when the member that carries it lands in a
permanent home and a second set uses it. The Acronyms appendix is where
a member declares its acronyms, in place of a definition above first
use.

## How an index reads

Restating the path is not an introduction: "the files in `standards/`"
tells a reader nothing the H1 did not. The live indexes name the thing:
*the catalog*; *the documentation type system*; *Build governs how a
repository is laid out, built, and checked*
([The opening sentence](/standards/knowledge-organization/indexes.md#the-opening-sentence)).
After that sentence comes only what a reader needs before the listing
makes sense: a start-here pointer, where the governing concept is
defined, or a structural fact the listing hides, such as half the
directory's material living elsewhere. okf-lint checks only that the
introduction is present; what it says is a reviewer's judgment.

`Ordering: in Decision Record number order` and
`Ordering: by level of abstraction` are declarations of a meaningful
order. The marker is structured: the detector checks only that an
introduction line, one before the first listed entry, begins
`Ordering:`. An undeclared deviation from alphabetical is a defect,
because a reader cannot tell unstated meaning from randomness
([Ordering](/standards/knowledge-organization/indexes.md#ordering)).

An `index.md` is authored, never generated: the writer chooses the
introduction and the order, and the description is copied by hand so
okf-lint can report the moment it goes stale. The root index declares
the bundle's OKF version, `okf_version: "0.1"`, per the OKF spec's
Versioning section; that key is dev-playbook's whole root frontmatter,
and a consumer repo carries one key more, the `okf_types` mapping.

## How a Loop is checked

A document typed `Loop` is checked by `scripts/loop-lint`, which reads
it the way the encoding cuts it: one paragraph, one fenced `mermaid`
flowchart, then three H2s. The graph is the source of truth; the
paragraph says what state the loop drives and toward what. The detector
stops at a file's first disagreement, since each rule reads the cut the
one before it made, and goes on to the next file. A repo with no
`loops/` tree is clean by construction. The edge rule,
[Edges follow the shape](/standards/knowledge-organization/loop-conventions.md#edges-follow-the-shape),
is the shape the Loop doc-type draws: steps in iteration order, a
programmed exit where its author put it, and control coming back.

## Why a README lists no harness files

Claude Code puts each injected file's name and description into every
session, so a hand-maintained roster of skills duplicates what its
reader already has and rots the moment a skill is added
([No roster of harness-injected files](/standards/knowledge-organization/readme-content.md#no-roster-of-harness-injected-files)).
An inventory of files the harness does not inject, the executables
under `scripts/`, is legitimate content: nothing else hands the reader
that list. Agent instructions and architecture decisions are absent
from a README because they live in `CLAUDE.md` and `docs/decisions/`.

## Why a type registry is frontmatter

dev-playbook's `## Types` table is the global registry, the vocabulary
every repo inherits. A consumer declares its own types in the
`okf_types` mapping of its root `index.md` frontmatter
([Local declaration](/standards/knowledge-organization/type-registry.md#local-declaration)):

```yaml
okf_version: "0.1"
okf_types:
  Resume: A resume markdown source, master or batch variant
  Story: One work-experience story in SPAR form
```

Frontmatter, not a document under the repo's own `standards/` tree:
that tree is the meta-standard's population, so a registry document
there could not pass, and a path that mirrors dev-playbook's own folder
name breaks the moment that folder is renamed upstream.

Membership stays exact-case, and the shadowing test is case-insensitive
so a consumer cannot alias upstream `Guide` as a distinct `GUIDE`
([Add, never shadow](/standards/knowledge-organization/type-registry.md#add-never-shadow)).
A consumer never edits the global table, so it can neither loosen nor
drop an upstream type; a local type is legal only in the repo that
declares it and any repo downstream of it, invisible uphill to
dev-playbook and sideways to sibling consumers. An entry carries the
type's name and its description and nothing else: the per-type
constraints upstream types impose, `resource` on `Recipe-Description`
for one, stay hardcoded upstream, and a local type declares none.

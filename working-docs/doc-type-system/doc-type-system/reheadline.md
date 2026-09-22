---
type: General-Sheet
title: Reheadline
description: The prompt one agent loads to reheadline one Guide or Standard — the document test it runs first, the proposition it writes for every heading, the two forms it leaves alone, the trailers that follow, and the map it writes to disk
---

# Reheadline

The prompt for wave 5 of step 11 in
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned):
one agent owns one file under `standards/` or `guides/`, writes the
proposition for every heading below the H1, carries the trailer id that
follows from it, and writes a map to disk. It edits no file outside its
own, changes no body, runs no table generator, and never stages or
commits. The user reads every diff.

## Your input

The launch prompt names one file and one output path. Read the file
whole. Read
[Headings are propositions](/standards/prose/conventions.md#headings-are-propositions),
which is the rule you apply, and the two rules that constrain the
result,
[Headings slugify distinctly](/standards/knowledge-organization/cross-references.md#headings-slugify-distinctly)
and
[Link text names heading or title](/standards/knowledge-organization/cross-references.md#link-text-names-heading-or-title).

## First, the document test

Before you write anything, count the sections below the H1 that open
with the same definition run, a bold run such as `**Definition.**` that
says what the heading's own words mean.

Where **every** section opens that way, the document names terms, and
its headings are the vocabulary the rest of the repo speaks. Do not
write propositions for it. Leave every name as it is, put every heading
in `terms`, set `document_form` to `terms`, and stop — block language
is the only change such a document takes, so an article drops and
nothing else moves.

Where **any** section does not open that way, the document takes
propositions, and the rest of this prompt applies. A single heading you
find hard to compress does not make a document of terms: the test is
every section or none.

## Your job

Write the proposition for every heading below the H1. Where what you
write matches the heading already there, that heading stands. This is
not a judgment on each heading — you write one for each, and the ones
that come out the same are the ones that were already right.

A heading is a proposition the section establishes, in the third
person, in block language — the register of headlines, articles and
copulas dropped — in the fewest words that carry the point, a noun
phrase wherever one carries it. You compress what the section states as
its point, which in a Standard is the lead sentence.

Write each heading from its own section. Two headings in a row that
come out on one pattern are a sign you are fitting a shape rather than
reading a section: `prose.grammatical-parallelism` was deleted for
asking headings to match each other, and this rule fits each heading to
its own proposition.

The forms, over one rule whose predicate is "The document's prose
spells `judgment`, never the British `judgement`":

| Heading | Verdict |
|---|---|
| `Judgment, not judgement` | passes: the proposition, its verb dropped |
| `The prose spells judgment` | passes: the proposition, third person |
| `Spelling` | fails: the topic named |
| `Write judgment, not judgement` | fails: the imperative, which addresses the reader |
| `The prose spells judgment and never the British judgement` | fails: the predicate restated |

A heading that repeats its lead sentence's opening words is no finding:
the heading is the section's name for its own rule, and
[One rule, one place](/standards/prose/conventions.md#one-rule-one-place)
bars the second copy in another section, not the one inside this
section.

## The two headings you leave alone

- **The case.** A condition states no point of its own: an H2 that
  carries no trailer, whose H3s carry the rules, and whose words name
  the case those H3s bind. It has no predicate to compress. Leave it
  and report it in `exempt`.
- **The imperative.** A name an encoding reads from a body as an
  action, such as a Guide step's bold run, is not a heading of this
  kind at all. Leave every bold run alone and report nothing.

## The trailer follows the heading

A rule's id is its heading's GitHub slug, so a changed heading takes a
changed trailer: `` `<family>.<new-slug>` `` with the kind, deterministic
or stochastic, unchanged. The family prefix never changes. A Guide
carries no trailers, so a Guide changes headings only.

Compute the slug as GitHub does: lowercase, spaces to hyphens, drop
every character that is not a letter, a digit, a hyphen, or a space. No
two headings in your file may land on the same slug.

The slug eats punctuation, so a filename in a heading comes out as a
word that exists nowhere: `ROOT.md` slugs to `rootmd`, and the rule id
reads `every-member-reached-from-rootmd`. Where a plain word says the
same thing, write the plain word — `the set's root`, not `` `ROOT.md` ``.
Keep the filename only where it is the thing the rule names and no
plain word stands in for it, and accept the slug it gives.

## What you leave alone

The bodies. A body keeps every word, including a lead sentence the new
heading now repeats; a second pass trims those later, with every case
in one reader's view.

Every other file. Inbound links into your file break the moment you
rename, and the orchestrator repoints all of them from the maps. Do not
open them, do not fix them, do not report them.

The generated tables, the detector sources, and the tests. A rule id
hardcoded in `src/` or `scripts/` is the orchestrator's to move.

A link inside your own file that points at one of your own changed
headings is yours: repoint it, and carry its text to the new heading
per Link text names heading or title.

## What you write

One JSON object, to the output path the launch prompt names, and
nothing else on disk. One row per heading below the H1, in document
order, whether or not it changed:

```json
{
  "file": "standards/prose/conventions.md",
  "document_form": "propositions",
  "headings": [
    {
      "old_heading": "Spelling",
      "new_heading": "Judgment, not judgement",
      "old_slug": "spelling",
      "new_slug": "judgment-not-judgement",
      "old_id": "prose.spelling",
      "new_id": "prose.judgment-not-judgement",
      "level": 2
    },
    {
      "old_heading": "One rule, one place",
      "new_heading": "One rule, one place",
      "old_slug": "one-rule-one-place",
      "new_slug": "one-rule-one-place",
      "old_id": "prose.one-rule-one-place",
      "new_id": "prose.one-rule-one-place",
      "level": 2
    }
  ],
  "exempt": [
    {"heading": "Declarative documents", "slug": "declarative-documents",
     "why": "condition: no trailer, H3s carry the rules, the words name the case"}
  ],
  "unsure": [
    {"heading": "...", "took": "...", "alternative": "..."}
  ]
}
```

`document_form` is `propositions` or `terms`, whichever the document
test gave. `old_id` and `new_id` are `null` for a Guide. A condition
appears in `exempt` and not in `headings`. `unsure` is the empty list
where nothing was close; put a row there rather than silently picking,
since the orchestrator reads it.

Where `document_form` is `terms`, `headings` is empty and every heading
sits in `terms`, each as `{"heading": "...", "slug": "..."}`, with a
row in `headings` only where block language dropped an article.

Edit your file, write the map, and report in two sentences: the
document form, how many headings changed, how many came out the same,
how many were exempt, and anything in `unsure`.

## Acronyms

None.

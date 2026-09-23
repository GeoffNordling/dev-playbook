---
type: General-Sheet
title: Stories Fact Base
description: The simulated fact base over story-forge's stories — the questions it answers, the data file and its extractors, the nine predicates health decomposes into, the views selected from it, and the facts no extractor reaches
---

# Stories Fact Base

The first hand simulation of the story-forge strand
([Story-Forge Simulation](/working-docs/doc-type-system/story-forge-simulation/ROOT.md)),
on the model of
[Ralph Fact Base](/working-docs/doc-type-system/fact-base/fact-base-ralph.md).
The subject is every Story in story-forge at commit `3af571a` and every
node that cites one. The user's question was "what are all my stories
and how healthy are they in terms of details, gaps, and being ready to
study one by one." Health is not a term; it is decomposed below into
nine predicates over facts a story file carries today, and the views
are selections that answer the question predicate by predicate.

The order of work was backwards from the question: the question chose
the views, the views named the facts, and the facts named the
extractors. No field was added to any story. One Sonnet agent surveyed
the Story shape; a second acted as the extractors, writing every row
with a receipt through a throwaway script; the views were computed by
a second throwaway script over the JSON, never by reading rows.
Neither script is kept: the stamp says `no module exists`, and the
extractors table below is their specification.

## The questions

Seven, agreed with the user before any row was written. F means
answerable from extractable facts; D means it needs a declared fact.

1. What stories exist, and what does each carry: title, tags, status. F
2. Which required sections does each story have or lack. F, and
   uninformative: the lint `stories.body` refuses any story without the
   seven H2s in order, so all 32 have them.
3. How long is each story and each section. F
4. Which stories carry an empty section or an open to-do. F, once the
   marker is named: the literal `None.` body and bullets under
   `## To-dos`.
5. Which tags does each story use, and are they registered. F
6. Which stories does a projection, resume, or prep-unit cite, and
   which does nothing cite. F, with four extractors, one per citation
   form.
7. Which stories are ready to memorize. D. The file has `status`
   (draft, needs-detail, complete), and the user rules it "a good sign
   that it's mostly done" but loosely applied. So `status` is a
   declared fact shown beside the finer predicates, never in place of
   them.

## The data file

[stories-fact-base.json](/working-docs/doc-type-system/story-forge-simulation/stories-fact-base.json),
in the viewer's envelope, `kind: fact-base`, `kind_version: 0`. 299
nodes and 537 edges, every row with a receipt. No derived row: every
row came from an extractor.

| Node type | Count | Id | Extractor |
|---|---|---|---|
| Story | 32 | `stories/<stem>.md` | frontmatter, line 1; `description` redacted to its word count |
| Section | 224 | `<story>#<heading-slug>` | headings, the H2's line |
| Tag | 31 | `tag:<name>` | yaml over `stories/tags.yaml` |
| Resume | 5 | path | frontmatter |
| Projection | 1 | path | frontmatter |
| Prep-Unit | 2 | path | frontmatter |
| General-Sheet | 2 | path | frontmatter |
| File | 2 | path | fs; the two index files, no frontmatter |

| Relation | Count | Source → target | Extractor |
|---|---|---|---|
| contains | 224 | Story → Section, with order | headings |
| tagged | 86 | Story → Tag | frontmatter, the `tags:` line |
| related | 58 | Story → Story, symmetric | frontmatter |
| supplements | 24 | Story → the `supplemental_context` file | frontmatter |
| sources | 7 | Projection → Story | frontmatter, the item's line |
| links | 73 | any file → Story, `[..](/stories/<id>.md)` | mdlink |
| cites | 65 | Resume → Story, `<!-- stories: a, b -->` | html-comment |

Section attrs are the finer facts health needs: `body_lines`,
`bullets` (lines matching `^- `), `is_none` (the body is exactly
`None.`), and `h3_count`. Every target resolves: no unregistered tag,
no dangling related, source, cite, or supplement, and all 29 related
pairs are reciprocal.

## The extractors

Five, all bedrock or a parser over a format story-forge fixed.
`frontmatter`, `headings`, and `mdlink` are the same three the Ralph
simulation used. `yaml` reads the two-list tag registry.
`html-comment` is the one story-forge owns: a resume bullet cites its
stories in a trailing `<!-- stories: a, b -->`, and a company section
lists `<!-- unassigned stories (resume-eligible): a, b -->`. The
survey's guess that the first fact base needs no span parser held.

## The predicates

Nine, each a test over one Story's rows. The first six are the repo's
own facts restated as predicates; the two thresholds marked with an
asterisk are the session's guess at "thin" and are the user's to
correct. Kind is deterministic for all nine.

1. `quantitative-not-none`: the Quantitative Results section is not
   `None.`
2. `todos-empty`: the To-dos section is `None.` or has no bullet.
3. `notes-empty`: the Notes section is `None.` or has no body line.
4. `status-complete`: frontmatter `status` is `complete`.
5. `situation-two-bullets`: Situation and Problem has two or more
   bullets. \*
6. `actions-three-bullets`: Actions has three or more bullets. \*
7. `resume-cites`: at least one `cites` edge reaches the story.
8. `projection-or-prep-reaches`: a `sources` or `links` edge from a
   Projection or Prep-Unit reaches the story.
9. `has-related`: at least one `related` edge reaches the story.

Predicates 1 to 3 are what the lint `stories.body` already enforces
for `complete` stories only; here they run over every story, which is
what makes the contradictions view possible.

## Views selected from it

Every view is a selection over the JSON, with nothing read from a
file. The catalog answers questions 1, 3, and 4; the matrix answers 4,
5, and 6 per predicate; the contradictions view is question 7 as far
as facts reach; the last two are question 6.

### Catalog

Bullets per section: S Situation and Problem, A Actions, Qn Quantitative Results, Ql Qualitative Results, T To-dos; N is the literal `None.`. Cites: resume bullets citing it / projection and prep-unit links reaching it.

| story | status | tags | lines | S/A/Qn/Ql/T | cites |
|---|---|---|---|---|---|
| abstraction-ladder | needs-detail | 4 | 81 | 3/6/3/4/1 | 4/0 |
| agentic-practice-since-amazon | complete | 7 | 59 | 6/5/N/2/N | 0/0 |
| agentic-software-factory | needs-detail | 4 | 79 | 4/8/4/4/2 | 4/0 |
| asap-ship-option | complete | 2 | 71 | 5/2/2/6/N | 4/0 |
| batman-grocery-delivery-zones | complete | 4 | 82 | 7/7/4/3/N | 2/1 |
| bayes-in-the-lab | complete | 4 | 63 | 4/3/5/3/N | 4/0 |
| block-length-optimization | needs-detail | 4 | 179 | 3/17/3/2/N | 5/1 |
| computer-vision-labor-tracking | complete | 4 | 60 | 3/13/3/4/N | 1/1 |
| difficult-colleague-collaboration | needs-detail | 2 | 78 | 3/10/N/4/1 | 0/0 |
| distributional-simulation-outputs | complete | 5 | 62 | 4/10/3/3/N | 1/0 |
| edu-customer-complaint | draft | 1 | 45 | 1/1/N/1/5 | 0/0 |
| gam-tree-methodology-adoption | complete | 5 | 73 | 6/10/4/6/N | 3/0 |
| gp-school-project | needs-detail | 2 | 59 | 3/7/4/3/1 | 1/0 |
| hiring-and-mentorship | complete | 3 | 54 | 2/8/2/2/N | 3/0 |
| intent-extraction-pipeline | needs-detail | 3 | 66 | 3/4/N/4/1 | 4/0 |
| jarvis-grocery-delivery-coverage | complete | 2 | 86 | 6/7/3/2/N | 5/1 |
| large-scale-data-fluency | complete | 1 | 61 | 5/6/N/2/N | 0/1 |
| llm-as-tool-not-brain | draft | 3 | 65 | 8/6/N/7/2 | 0/0 |
| production-python-collaboration | complete | 3 | 80 | 4/8/5/4/N | 5/1 |
| profiling-performance-optimization | complete | 1 | 57 | 4/3/1/4/N | 2/0 |
| project-plan-simulator | complete | 2 | 84 | 3/7/1/2/N | 2/0 |
| project-roar-mall-delivery | complete | 1 | 173 | 5/5/3/3/N | 2/0 |
| rdm-strategic-vision | complete | 2 | 56 | 3/3/2/2/N | 0/0 |
| resource-constrained-scheduling-cp | complete | 1 | 94 | 4/7/2/1/N | 2/0 |
| resource-constrained-scheduling-dp-tree-search | complete | 1 | 129 | 3/12/1/3/N | 2/0 |
| retrofit-games | complete | 3 | 67 | 9/8/N/6/N | 1/0 |
| simpy-pod-production | complete | 1 | 58 | 5/8/N/4/N | 1/0 |
| spec-tools | draft | 2 | 77 | 5/7/2/2/2 | 0/0 |
| tech-club-knowledge-sharing | complete | 3 | 50 | 2/5/3/3/N | 2/0 |
| warehouse-operations-manager | complete | 3 | 77 | 2/7/5/3/N | 1/0 |
| web-portal-tool-deployment | complete | 2 | 65 | 3/20/2/3/N | 1/2 |
| wfm-time-series-forecasting | complete | 1 | 50 | 3/7/1/2/N | 1/1 |

### Cross-reference matrix, predicates by stories

Columns are the nine predicates in the order listed under The predicates; `.` holds, `x` fails.

| story | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| abstraction-ladder | . | x | . | x | . | . | . | x | . |
| agentic-practice-since-amazon | x | . | . | . | . | . | x | x | . |
| agentic-software-factory | . | x | . | x | . | . | . | x | . |
| asap-ship-option | . | . | . | . | . | x | . | x | x |
| batman-grocery-delivery-zones | . | . | . | . | . | . | . | . | . |
| bayes-in-the-lab | . | . | . | . | . | . | . | x | x |
| block-length-optimization | . | . | . | x | . | . | . | . | . |
| computer-vision-labor-tracking | . | . | . | . | . | . | . | . | x |
| difficult-colleague-collaboration | x | x | . | x | . | . | x | x | . |
| distributional-simulation-outputs | . | . | . | . | . | . | . | x | . |
| edu-customer-complaint | x | x | x | x | x | x | x | x | x |
| gam-tree-methodology-adoption | . | . | . | . | . | . | . | x | x |
| gp-school-project | . | x | . | x | . | . | . | x | x |
| hiring-and-mentorship | . | . | . | . | . | . | . | x | x |
| intent-extraction-pipeline | x | x | . | x | . | . | . | x | . |
| jarvis-grocery-delivery-coverage | . | . | . | . | . | . | . | . | . |
| large-scale-data-fluency | x | . | . | . | . | . | x | . | . |
| llm-as-tool-not-brain | x | x | . | x | . | . | x | x | . |
| production-python-collaboration | . | . | . | . | . | . | . | . | . |
| profiling-performance-optimization | . | . | . | . | . | . | . | x | . |
| project-plan-simulator | . | . | . | . | . | . | . | x | . |
| project-roar-mall-delivery | . | . | . | . | . | . | . | x | x |
| rdm-strategic-vision | . | . | . | . | . | . | x | x | x |
| resource-constrained-scheduling-cp | . | . | . | . | . | . | . | x | . |
| resource-constrained-scheduling-dp-tree-search | . | . | . | . | . | . | . | x | . |
| retrofit-games | x | . | . | . | . | . | . | x | x |
| simpy-pod-production | x | . | . | . | . | . | . | x | x |
| spec-tools | . | x | x | x | . | . | x | x | . |
| tech-club-knowledge-sharing | . | . | . | . | . | . | . | x | x |
| warehouse-operations-manager | . | . | . | . | . | . | . | x | x |
| web-portal-tool-deployment | . | . | . | . | . | . | . | . | . |
| wfm-time-series-forecasting | . | . | . | . | . | . | . | . | . |

Failures per predicate:

1. `quantitative-not-none`: 8
2. `todos-empty`: 8
3. `notes-empty`: 2
4. `status-complete`: 9
5. `situation-two-bullets`: 1
6. `actions-three-bullets`: 2
7. `resume-cites`: 7
8. `projection-or-prep-reaches`: 24
9. `has-related`: 13

### Contradictions, status complete against the finer predicates

- agentic-practice-since-amazon: fails `quantitative-not-none`
- asap-ship-option: fails `actions-three-bullets`
- large-scale-data-fluency: fails `quantitative-not-none`
- retrofit-games: fails `quantitative-not-none`
- simpy-pod-production: fails `quantitative-not-none`

### Stories no resume, projection, or prep-unit reaches

- agentic-practice-since-amazon, complete, resume_eligible true
- difficult-colleague-collaboration, needs-detail, resume_eligible false
- edu-customer-complaint, draft, resume_eligible false
- llm-as-tool-not-brain, draft, resume_eligible false
- rdm-strategic-vision, complete, resume_eligible false
- spec-tools, draft, resume_eligible false

### Citers, distinct stories each reaches

| type | file | stories |
|---|---|---|
| File | `career/background/agentic-journey-notes/index.md` | 1 |
| File | `stories/index.md` | 32 |
| General-Sheet | `career/background/amazon-robotics-context.md` | 1 |
| General-Sheet | `career/candidate-profile.md` | 1 |
| Prep-Unit | `interview-prep/prep-units/distributed-systems/principles.md` | 1 |
| Prep-Unit | `interview-prep/prep-units/solid-principles/principles.md` | 1 |
| Projection | `stories/projections/distributed-scalable-systems.md` | 7 |
| Resume | `resume/geoff-nordling-elevator-resume.md` | 8 |
| Resume | `resume/geoff-nordling-jpmc-ai-lead-resume.md` | 10 |
| Resume | `resume/geoff-nordling-jpmc-resume.md` | 10 |
| Resume | `resume/geoff-nordling-master-resume.md` | 25 |
| Resume | `resume/geoff-nordling-resume.md` | 10 |


The `links` relation alone says nothing about use: `stories/index.md`
links all 32 stories, so "reached" is restricted to a Projection or a
Prep-Unit source. The containment tree, control flow, data flow, and
interface card are not drawn: a Story has no control or data flow, and
the catalog row is its interface card.

## What no extractor reaches

Four facts the extractor agent saw in the files and the row shape
could not hold, plus one the views raised.

- **A placeholder to-do.** `stories/edu-customer-complaint.md:31-37`
  holds five bullets under To-dos that read "Fill in the situation",
  "Fill in the actions". The row says `bullets: 5`, the same as five
  real work items. Whether a to-do is real is a judgment, or a
  convention not yet declared.
- **Appendix H3 titles.** `stories/abstraction-ladder.md:57-69` has
  three H3s; the row holds `h3_count: 3` and loses the titles.
- **Wrapped tag comments.** Eight entries in `stories/tags.yaml`
  continue their trailing comment on a second line, such as line 16
  after `statistics` at line 15; the Tag row's `comment` holds one line.
- **Resume derivation.** `resume/geoff-nordling-jpmc-resume.md:7-8`
  carries `<!-- tailored from: … -->` and `<!-- tailored to: … -->`,
  a derivation chain no relation here holds.
- **What `status: complete` means.** The user's words: "I've been loose
  with it in the past. It hints a story is complete but I wouldn't be
  100% sure." The contradictions view shows five stories where the
  hint and the facts disagree. The gap between the hint and "ready to
  memorize" is the first residual the domain layer must own.

## Acronyms

None.

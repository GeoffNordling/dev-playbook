---
type: Guide
title: Slop Tics
description: The named tics in Claude's slop writing — the patterns to remove from any workspace document
---

# Slop Tics

The catalog behind Doc Conventions'
[No slop tics](/standards/prose/conventions.md#no-slop-tics): each named
tic in Claude's slop writing, its definition, the action that removes it,
and before-and-after examples.

## Changelog residue

**Definition.** Traces of an earlier draft, of the path to the knowledge, or of
the conversation that produced the document, left in a document whose job is to
say what is true now. Git holds the history. The words are "already",
"previously", "it turns out", "no longer", "used to", "I had assumed", any
sentence whose subject is a change of mind, and any closure claim that records
what was said privately about the work's future: "no more are expected", "no
further development is planned".

It accumulates. A document edited across many sessions collects a layer each
time: told to move a tool from Adopt to Reject, Claude writes "we previously
adopted this, then decided against it" instead of moving the line. The
most-rewritten documents carry the most residue.

**Action.** Make the edit and say only what is true now.

**Examples.**

- **Before** "Docstring enforcement is already deterministic, and I had
  forgotten." → **After** deleted; the section states the enforcement as it
  stands.
- **Before** "Docstrings — already settled" (a section heading) → **After**
  "Docstrings"
- **Before** "It is complete, and no further development of it is planned." →
  **After** deleted; the map already shows the part as built.
- **Before** "The generated text files were the proof of concept; all three
  are deleted and kept in git history." (in a Principles entry) → **After**
  deleted.

## Misplaced status

**Definition.** Status written into a section whose job is to say what holds,
such as Principles, Terms, or a theory page. What is built, not yet built,
dated, or deleted has its own place: Planned, Completed, or git history. In the
wrong section it goes stale the moment the work moves, and nobody editing the
worklist sees it.

**Action.** Delete the status. Where the worklist lacks it, move it there.

**Examples.**

- **Before** "A drift check binds the document to the code it describes; a
  loop has none yet." (in a Principles entry) → **After** deleted; the drift
  check is a Planned item.
- **Before** "...per Fact Base Workstream, whose Planned list holds the
  solver's build." → **After** "...per Fact Base Workstream."
- **Before** "Rulings, 2026-09-23: a story's..." → **After** "A story's..."

## Unnecessary enumeration

**Definition.** A count of the items in a list that follows, written into the
prose above it. The list already says how many. The count only has to be
maintained, and it goes wrong the moment a fourth item is added — worse across
files, where nobody sees the count when they edit the list. The words are "three
places", "the following two", "both of which", "all four", etc.

**Action.** Delete the count.

**Examples.**

- **Before** "The two disagree in three places:" → **After** "The two disagree
  like so:"

## Bloated phrasing

**Definition.** The same point in far more words than it needs. The short form
was available and the sentence took a longer route to the same place.
Restatement makes the point twice; this makes it once, slowly.

**Action.** Write the short form.

**Examples.**

- **Before** "The defense against that imagined misreading is what bloats the
  prose." → **After** "This is unnecessary bloat."

## Unnecessary examples

**Definition.** Instances piled onto a claim the reader already understood. Each
one has to be read before the point can be picked up again.

**Action.** Delete the instances. Keep the claim.

**Examples.**

- **Before** "Report-shaped tools rot: a call-graph HTML nobody opens or a
  metrics dashboard is one more artifact I will not read." → **After**
  "Report-shaped tools take effort to read."

## Contrast pair

**Definition.** An assertion paired with a denial of something the reader never
proposed, in either order: assertion then denial, or denial then assertion.

**Action.** Delete the denial. The assertion stands on its own.

**Examples.**

- **Before** "A record of decisions, not a specification." → **After** "A record
  of decisions."
- **Before** "The failure was not reading tests. It was having one
  undifferentiated tier." → **After** "The failure was having one
  undifferentiated tier."
- **Before** "Collapse a call graph up to module level and you get roughly the
  import graph. Roughly, not exactly, and the leaks are where the architecture
  hides:" → **After** "Collapse a call graph up to module level and you get
  roughly the import graph. The two disagree here:"
- **Before** "...so that the documentation is a pleasure to read and not a
  terror." → **After** "...a pleasure to read."
- **Before** "What good writing looks like here, and the named tics that keep it
  from happening." → **After** "The named tics in Claude's writing."
- **Before** "X is hand-maintained — there is no generator." → **After** "X is
  the source of truth."
- **Before** "The fact base holds declarations and state, never findings." →
  **After** "The fact base records what is declared."

## Closing cadence

**Definition.** A short punchy sentence or pair of sentences at the end of a
paragraph, there for rhythm. The paragraph already made the point; the cadence
adds sound.

**Action.** Delete the closing sentence. End on the point.

**Examples.**

- **Before** "Gates compound. Reports rot." → **After** deleted.
- **Before** "...and I cannot read a thousand tests. Nobody can." → **After**
  "...and I cannot read a thousand tests."
- **Before** "The document says what is true now. Git holds the history." →
  **After** folded into the definition above it.

## Flourish

**Definition.** A dramatic word or image where an ordinary one carries the same
meaning.

**Action.** Write the ordinary word. Where the drama was the whole sentence,
delete the sentence.

**Examples.**

- **Before** "Report-shaped tools rot." → **After** deleted; the paragraph
  already said reports depend on being read.
- **Before** "...and the leaks are where the architecture hides:" → **After**
  "The two disagree here:"
- **Before** "No interactive zoomable viewer — that is the heavy-HTML mistake
  in a new costume." → **After** deleted; the user never said that.

## Restatement

**Definition.** A point made in plain words, then made again — with terminology
attached so it reads as a conclusion, or in a second clause that repeats the
first.

**Action.** Say each thing once. Attach the term to the plain statement instead
of repeating the statement to carry it.

**Examples.**

- **Before** "The format may be wrong — a heavy HTML file is possibly the wrong
  way to go." → **After** "A heavy HTML file may be the wrong format."
- **Before** "The challenge is imposing quality standards that keep it from
  being sloppified. I am fundamentally incapable of reading Claude's
  slop-filled documentation style. Something must be imposed so that the
  documentation is a pleasure to read and not a terror." → **After** "I am
  incapable of reading Claude's slop-filled style, so something has to keep the
  documentation a pleasure to read."

## Unasked disclaimer

**Definition.** A whole sentence defending against a misreading nobody was going
to make.

**Action.** Delete the sentence.

**Examples.**

- **Before** "Nothing here describes software to build yet." → **After**
  deleted.

## Reassurance

**Definition.** Comfort offered to a reader who might feel bad about a choice
they made. The tell is emotional rather than logical: the sentence manages
feelings.

**Action.** Delete the comfort. Leave the fact it was wrapped around.

**Examples.**

- **Before** "Sometimes stochastic functions are required — that is the power
  of AI, and it is not a failure to use them." → **After** "Sometimes
  stochastic functions are required — that is the power of AI."
- **Before** "This is the orthodox test pyramid, and acceptance tests as
  executable specification are an established paradigm." → **After** "This is
  the orthodox test pyramid."

## Minted term

**Definition.** A term invented on the spot and then used as though it were
established — bold type and a definite article lend it an authority it has not
earned. It also appears as an abstract insider word where a plain description
fits.

**Action.** State the reason and what follows from it.

**Examples.**

- **Before** "**The adoption test.** A tool earns its place if it fails a build
  with a one-line message." → **After** "These tools hide complexity behind
  deterministic code, so the ones worth adopting fail the build with a one-line
  message."
- **Before** "Two kinds of force" (a section heading; neither thing in the
  section is a force) → **After** "Stochastic functions and deterministic
  backpressure"
- **Before** "`import-linter` is the gate." → **After** "Only `import-linter`
  fails the build, and it checks the import graph against rules I write."

## Needless definition

**Definition.** A term defined because the document has a Terms section, not
because a reader needs it. A plain word used in its plain sense gets no
definition. Define a term only when a reader would misread it without one.

**Action.** Delete the definition. Where the term has a real home elsewhere,
link the first use to it.

**Examples.**

- **Before** "**Checkout** — one working copy of a repo, a main checkout or a
  worktree." → **After** deleted.
- **Before** "**Schema** — the fact base's set of node types and relation
  types." → **After** deleted.

## Inflated analogy

**Definition.** A comparison said once in passing, grown into doctrine: defined
terms, a principle built on it, and framing repeated through a lead document.
The analogy was an aid to thought and now carries weight it cannot bear.

**Action.** State the comparison once, where it helps, or delete it. Delete
the terms and principles built on it.

**Examples.**

- **Before** The user says once that tests are "like a safety net". The
  document then defines **Net** and **Hole**, adds the principle "Every gap in
  the net is a hole a regression falls through", and calls each new check "a
  strand". → **After** the terms and the principle are deleted, and the prose
  says "The tests catch regressions."

## Obvious qualifier

**Definition.** A qualifier — sometimes a whole sentence — that carries nothing,
because no alternative exists or because it restates the document's own premise.

**Action.** Delete it.

**Examples.**

- **Before** "Both tool outputs are generated on demand." → **After** deleted;
  tools run when they are run.
- **Before** "Raw material, carried forward without analysis. We have not
  earned conclusions here." (under a heading that already said "not yet
  examined") → **After** "Raw material only."
- **Before** "New terms introduced here" (a section heading) → **After** "New
  terms"
- **Before** "Not yet examined: documentation" (a section heading) → **After**
  "The documentation toolbox"
- **Before** "Candidates for `CONTEXT.md`, not yet added there:" → **After**
  "Candidates for `CONTEXT.md`:"

## Overclaim

**Definition.** A qualified position restated as an absolute. Absolutes read as
stronger writing and are usually false. The words are "everything", "never",
"always", "nothing", and any flat refusal attributed to the user.

**Action.** Write what is actually true, qualifier included.

**Examples.**

- **Before** "...depends on me reading it, and I will not read it." → **After**
  "I will read one when I need to, but it is much more work than a one-line
  message and much less useful to the AI."
- **Before** "Everything I have done for the last six months has been slop." →
  **After** "Six months of building this way has produced a lot of slop."
- **Before** "I never look at the code." → **After** "I rarely look at the
  code."
- **Before** "I am fundamentally incapable of reading Claude's slop-filled
  style..." → **After** "I am incapable of reading Claude's slop-filled
  style..."

## Synthesized voice

**Definition.** The user's ideas paraphrased into generated prose: abstract,
even, and in terms the user never used. It reads as the model's summary of the
user, and the user does not recognize it as their own.

**Action.** Write it the way the user said it, from their words in the
conversation or in git history. Where their words are not at hand, report
that; do not paraphrase again.

**Examples.**

- **Before** "**Logic and statistics meet at one seam.** Predicates define a
  set, with no probabilities attached. An act is a draw from a distribution
  over states..." → **After** "**Markdown is code.** Just a fuzzy, random form
  of it, with the LLM as the stochastic compiler." (the user's own words)

## Hypothetical misreader

**Definition.** Writing aimed at a reader who is about to misunderstand, rather
than the one actually reading. This is unnecessary bloat.

**Action.** Write for the reader actually there — someone careful enough to
follow a single sentence.

**Examples.**

- **Before** "Run `make check`, the check target in the Makefile, before
  pushing." → **After** "Run `make check` before pushing."

## Prepositional padding

**Definition.** A phrase that spends a preposition to say what a compound says
in fewer words. Common in headings, where the subject ends up buried behind the
preposition instead of leading.

**Action.** Write the compound.

**Examples.**

- **Before** "Tests in two tiers" → **After** "Two testing tiers"

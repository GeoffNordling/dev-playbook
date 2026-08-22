---
type: Guide
title: Writing
description: The named tics in Claude's writing
---

# Writing

The named tics in Claude's writing.

Every example below is a real edit. "Before" is what Claude wrote; "after" is
what survived review.

## Tics

### The hypothetical misreader

Writing aimed at a reader who is about to misunderstand, rather than the one
actually reading. This is unnecessary bloat.

### Contrast pair

An assertion paired with a denial of something the reader never proposed. Either
order: assertion then denial, or denial then assertion. Keep the assertion,
delete the denial.

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

### Unasked disclaimer

A whole sentence defending against a misreading nobody was going to make. Delete
the sentence.

- **Before** "Nothing here describes software to build yet." → **After**
  deleted.

### Reassurance

Comfort offered to a reader who might feel bad about a choice they made. The
tell is emotional rather than logical: the sentence manages feelings.

- **Before** "Sometimes stochastic functions are required — that is the power
  of AI, and it is not a failure to use them." → **After** "Sometimes
  stochastic functions are required — that is the power of AI."
- **Before** "This is the orthodox test pyramid, and acceptance tests as
  executable specification are an established paradigm." → **After** "This is
  the orthodox test pyramid."

### Minted term

A term invented on the spot and then used as though it were established — bold
type and a definite article lend it an authority it has not earned. It also
appears as an abstract insider word where a plain description fits. State the
reason, then state what follows from it.

- **Before** "**The adoption test.** A tool earns its place if it fails a build
  with a one-line message." → **After** "These tools exist to hide complexity
  behind deterministic code and give me a simple interface onto it. So the ones
  worth adopting fail the build with a one-line message, the way ruff names a
  file, a line, and a rule id."
- **Before** "Two kinds of force" (a section heading; neither thing in the
  section is a force) → **After** "Stochastic functions and deterministic
  backpressure"
- **Before** "`import-linter` is the gate." → **After** "Only `import-linter`
  fails the build, and it checks the import graph against rules I write."

### Flourish

A dramatic word or image where an ordinary one carries the same meaning.

- **Before** "Report-shaped tools rot." → **After** deleted; the paragraph
  already said reports depend on being read.
- **Before** "...and the leaks are where the architecture hides:" → **After**
  "The two disagree here:"
- **Before** "No interactive zoomable viewer — that is the heavy-HTML mistake
  in a new costume." → **After** deleted.

### Lopsided examples

Examples supplied on one side of a contrast only. Give one of each, or none.

- **Before** "Report-shaped tools rot: a call-graph HTML nobody opens or a
  metrics dashboard is one more artifact I will not read." (two examples of the
  bad kind, none of the good) → **After** "...the ones worth adopting fail the
  build with a one-line message, the way ruff names a file, a line, and a rule
  id. A tool that produces something to look at instead, such as a call-graph
  HTML page, needs me to read it."

### Closing cadence

A short punchy sentence or pair of sentences at the end of a paragraph, there
for rhythm. The paragraph already made the point; the cadence adds sound.

- **Before** "Gates compound. Reports rot." → **After** deleted.
- **Before** "...and I cannot read a thousand tests. Nobody can." → **After**
  "...and I cannot read a thousand tests."
- **Before** "The document says what is true now. Git holds the history." →
  **After** folded into the definition above it.

### Overclaim

A qualified position restated as an absolute. Absolutes read as stronger writing
and are usually false.

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

Watch for "everything", "never", "always", "nothing", and for any flat refusal
attributed to the user.

### Changelog residue

Traces of an earlier draft or of the path to the knowledge, left in a document
whose job is to say what is true now. Git holds the history. It happens most
when we rewrite in place: told to move a tool from Adopt to Reject, Claude
writes "we previously adopted this, then decided against it" instead of moving
the line.

- **Before** "Docstring enforcement is already deterministic, and I had
  forgotten." → **After** deleted; the section states the enforcement as it
  stands.
- **Before** "Docstrings — already settled" (a section heading) → **After**
  "Docstrings"

Watch for "already", "previously", "it turns out", "no longer", "used to", "I
had assumed", and for any sentence whose subject is a change of mind.

### Restatement

A point made in plain words, then made again — with terminology attached so it
reads as a conclusion, or in a second clause that repeats the first. Say each
thing once; attach a term to the plain statement instead of repeating the
statement to carry it.

- **Before** "Four to a few dozen nodes. I can hold it in my head, and rules
  can be written against it. This is at the CLOA, and it is what
  `import-linter` enforces." → **After** "Four to a few dozen nodes. This is at
  the CLOA: I can hold it in my head, and `import-linter` can enforce rules
  against it."
- **Before** "The format may be wrong — a heavy HTML file is possibly the wrong
  way to go." → **After** "A heavy HTML file may be the wrong format."
- **Before** "The challenge is imposing quality standards that keep it from
  being sloppified. I am fundamentally incapable of reading Claude's
  slop-filled documentation style. Something must be imposed so that the
  documentation is a pleasure to read and not a terror." → **After** "I am
  incapable of reading Claude's slop-filled style, so something has to keep the
  documentation a pleasure to read."

### Bloated phrasing

The same point in far more words than it needs. The short form was available and
the sentence took a longer route to the same place. Restatement makes the point
twice; this makes it once, slowly.

- **Before** "The defense against that imagined misreading is what bloats the
  prose." → **After** "This is unnecessary bloat."

### Obvious qualifier

A qualifier — sometimes a whole sentence — that carries nothing, because no
alternative exists or because it restates the document's own premise. Delete it;
keep a qualifier only where the alternative is real and someone might have
expected it.

- **Before** "Both graphs are understanding tools, generated on demand." (tools
  run when they are run) → **After** the qualifier deleted, and then the whole
  sentence — the document is about understanding.
- **Before** "Raw material, carried forward without analysis. We have not
  earned conclusions here." (under a heading that already said "not yet
  examined") → **After** "Not yet examined. Raw material only."
- **Before** "New terms introduced here" (a section heading) → **After** "New
  terms"
- **Before** "Not yet examined: documentation" (a section heading) → **After**
  "The documentation toolbox"
- **Before** "Candidates for `CONTEXT.md`, not yet added there:" → **After**
  "Candidates for `CONTEXT.md`:"

### Unnecessary enumeration

A count of the items in a list that follows, written into the prose above it.
The list already says how many. The count only has to be maintained, and it goes
wrong the moment a fourth item is added — worse across files, where nobody sees
the count when they edit the list.

- **Before** "The two disagree in three places:" → **After** "The two disagree
  here:"

Watch for "three places", "the following two", "both of which", "all four".

### Prepositional padding

A phrase that spends a preposition to say what a compound says in fewer words.
Common in headings, where the subject ends up buried behind the preposition
instead of leading.

- **Before** "Tests in two tiers" → **After** "Two testing tiers"

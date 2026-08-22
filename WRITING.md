---
type: Guide
title: Writing
description: What good writing looks like here, and the named tics that keep it from happening
---

# Writing

What good writing looks like here, and the named tics that keep it from
happening.

Detection is approximate. There are many ways to write a contrast pair, and most
of them do not contain the word "not" next to a comma. A deterministic linter can
catch a first-pass subset and nothing more. The rest stays with the reader and
with review agents.

## What good looks like

**Grammatical parallelism in section headings.** Headings within a document take
the same grammatical shape. In `SCRATCH.md` they are noun phrases: "The problem",
"The code toolbox", "Two testing tiers", "Gray modules".

## The hypothetical misreader

The root of several artifacts below. Claude writes for a reader who is about to
misunderstand, rather than for the reader who is actually there. The defense
against that imagined misreading is what bloats the prose.

## Tics

### Contrast pair

An assertion paired with a denial of something the reader never proposed. Either
order.

> A record of decisions, not a specification.

> The failure was not reading tests. It was having one undifferentiated tier.

In the first, the sentence finishes at "decisions". In the second, only the
second sentence is needed. Keep the assertion and delete the denial.

*First-pass detection:* a clause-final "not X" appended to a complete assertion,
or a sentence of the form "It was not X" followed by "It was Y". Catches the
obvious cases only.

### Unasked disclaimer

A whole sentence defending against a misreading nobody was going to make.

> Nothing here describes software to build yet.

Delete the sentence.

*First-pass detection:* weak. The giveaway is that the sentence carries no
information the reader lacked, which no regex sees.

### Reassurance

Comfort offered to a reader who might feel bad about a choice they made.

> Sometimes stochastic functions are required — that is the power of AI, and it
> is not a failure to use them.

Cut from the comma. Same root as the others, but the tell is emotional rather
than logical: the sentence is managing feelings instead of carrying information.
Lower priority than the contrast pair and the unasked disclaimer.

*First-pass detection:* none.

### Minted term

A term invented on the spot and then used as though it were established.

> **The adoption test.** A tool earns its place if...

Nobody has heard of the adoption test. It was invented one sentence earlier and
given bold type and a definite article, which lends it an authority it has not
earned. The plain alternative is to state the reason and then state what follows
from it.

### Flourish

A dramatic word where an ordinary one carries the same meaning.

> Report-shaped tools **rot**.

Reports do not rot. They go unread.

### Lopsided examples

Examples supplied on one side of a contrast only.

> ...a call-graph HTML nobody opens or a metrics dashboard...

Two examples of the bad kind, none of the good kind. Either give one of each or
give neither.

### Closing cadence

A pair of short parallel sentences at the end of a paragraph, there for rhythm.

> Gates compound. Reports rot.

The paragraph already made both points. The cadence adds sound, not meaning.

### Overclaim

A position you stated with qualifications, restated as an absolute.

> ...depends on me reading it, and I will not read it.

You said reports are more work and less useful to the AI. The rewrite turned
that into a refusal you never made. The same tic produced "everything I have done
for the last six months has been slop" from a milder original.

Absolutes read as stronger writing and are usually false. Watch for "everything",
"never", "always", "nothing", and for any flat refusal attributed to you.

### Changelog residue

Traces of an earlier draft, left in a document whose job is to say what is true
now.

> Docstring enforcement is already deterministic, and I had forgotten.

It happens most when we rewrite in place. Told to move a tool from Adopt to
Reject, Claude writes "we previously adopted this, then decided against it"
instead of simply moving the line.

The document says what is true now. Git holds the history.

Watch for "already", "previously", "it turns out", "no longer", "used to", "I had
assumed", and for any sentence whose subject is the act of changing our minds.

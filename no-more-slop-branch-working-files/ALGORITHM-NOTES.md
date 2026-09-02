---
type: General-Sheet
title: Algorithm Notes
description: Scratch notes on what worked while constructing new CLOA objects — tentative, gathered as we go, a possible complement to the EM loop documentation later
---

# Algorithm Notes

Little notes on things learned to be effective while constructing new
CLOA objects. Member of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).
These are tentative ideas and scratch notes, written as they occur.
They may one day complement the EM loop documentation; they do not
live there yet because nothing here is settled.

## Pseudocode is a muscle, not a target

Writing a document kind as pseudocode is helpful. It forces a precise
statement of things natural language is squirrely and fuzzy about:
what the fields are, what they may hold, what rules the object's own
state obeys. The point is to think of documentation as code, as a
structured object. The point is not to reimplement the documentation
in literal Python. The moment the pseudocode starts holding the
content of the markdown, the rows of a table or the enumeration of
every rule, it has gone too deep. Stop one screen above that.

## Find the primitive at the heart of the kind

The registry refactor moved once a primitive named Rule existed. A
Standard is something that enforces rules; naming Rule as a primitive
got to the heart of what a Standard is, and after that the CLOA
object was easy to construct on screen and easy to agree on. When a
kind resists expression, look for the one primitive it is made of and
name it first.

## Greenfield mindset

The agent's tendency is to constrain itself to what it finds in the
system: today's headings, today's tables, today's file boundaries. The
work is to refactor, redesign, and reimplement the repository in
whatever way makes sense for the long term. What is preserved is what
the rules mean and what the existing lints check. Everything else is
open. This needs saying repeatedly, because the tendency returns.

## Borrow the CS abstraction that fits, case by case

The first draft of the Standard's object copied the runbook's chain,
because the chain had worked. A runbook is by definition a sequence
of commands, so a trace drawing fits it. A Standard is a collection,
not a sequence, and the copy made no sense. What fit was a relational
table, with joins across the collections of rules, audits, and
enforcements. Usually some abstraction from computer science relates
to whatever group of documentation is in hand: a sequence, a relation,
a tree, a graph. Which one is decided case by case, not by what
worked last time.

## Read the corpus for cut points before inventing marks

The card generator needed no new mark. Every card already wrote its
bullets one way: a lead, a spaced em dash, an annotation, and in
Enforce a gate name in bold. The encoding named those cut points and
the generator sliced on them; only four bullets in four cards had to
move, and each move was a remark that had been sitting in a bullet.
Before designing marks for a kind, read how its files already write
the thing the view needs. The marks may already be there, and an
encoding that names what exists costs the port almost nothing.

## A heading level is a mark

The Standard encoding spends heading levels on meaning: an H2 is a
rule or a condition, an H3 is a rule under a condition. Doc Conventions had
spent its H2s on navigation, `Contents`, `Voice`, `Mechanics`, and
those went in the port, because a parser that reads levels cannot
also let a level mean nothing. A markdown file has few marks a parser
can slice on, and the levels are the strongest; once one carries
meaning, navigation moves to the description and the generated view.

## Test the predicate, not the heading

"How to decide between section formats" read as a writer's process,
and the first pass evicted it. Its bullets were each a predicate over
a block as it stands: a list of items that are not parallel is wrong
on sight. The heading was about process; the content was a rule. When
sorting a section, ask whether a reviewer could reject a document by
comparing its state to the sentences, and let the heading be rewritten
to match the answer.

## Acronyms

None. CLOA and EM are defined in the root,
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#acronyms).

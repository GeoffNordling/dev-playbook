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

## Acronyms

None. CLOA and EM are defined in the root,
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#acronyms).

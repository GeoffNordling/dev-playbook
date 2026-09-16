---
type: General-Sheet
title: Vision Email
description: The informal email to a friend that carries the whole pitch — stochastic code, deterministic structure, programming one level up, the knowledge graph and its views — dictated by the user and cleaned up, in progress on the vision-doc branch
---

# Vision Email

Draft. The user's dictation, cleaned for typos and grammar, assembled in
order and grouped into paragraphs. Not for the repo and not for a reader
other than the friend it is addressed to. Draft in progress on the
`vision-doc` branch, nothing links into it.

---

My ideas are fragmented across a bunch of files in various components,
so there's no single doc I can send you. I've been thinking about a few different things all year.

First, natural
language is now a stochastic form of code. And it makes slop. The way
to stop slop is to understand your system. But we can't read all this
new markdown; the LLMs write like trash. If you try to read it all, your brain melts.

The solution to agent slop, everyone agrees, is to add deterministic structure
to the system. People are adding it in the form of verifiers, tests,
gates, etc. But that is structure added to the control the behavior of the system.
What if we added structure to help *understand* and *define* the system instead?
What if we could generate call graphs, import graphs, class hierarchies,
coverage maps, etc. for markdown instructions? If we could do that, then
we'd be back to understanding the new 

And it feels like this stochastic markdown code is taking our love of
programming away from us. We mourn our craft. One good thing AI
lets us do is move up a level of abstraction, where we can be more
productive and think about bigger things. So what's to stop us from
programming one level up?

Because what is programming, really? A language fixes the primitives:
its types, its operators, its control structures, its rules for
composition. On top of those you declare the things your system is made
of, the relations between them, the operations each one answers to, and
the invariants that must hold. Then a type checker, a compiler, and a
test suite hold every one of those declarations to account. The language
was fixed. The objects were always ours to invent.

Nothing says we can't keep programming higher up the stack. We can
invent new compositions, new rules, new primitives using natural
language, and as long as we connect them to the bedrock of determinism
with some form of actual code, then the entire space of ideas is ours to
program in. It's turtles all the way up! And what do our new turtles
say? They say simple things in precise ways. They are code of our own
invention, simple nouns with verbs attached, objects at this new level
of abstraction that own specific operations on one another. This is an
ontology we get to "program" ourselves, and it's held to account by
determinism embedded within it: linting, parsing, and constraint
solving.

Take two words everybody already uses. A **runbook** is a noun, its
verbs are read, write, and do, and you invoke it. A **loop** is a noun,
its verbs are act, check, and yield, and it drives. The difference is
that for me these aren't just words for a kind of document anymore.
They're types. A runbook has declared verbs, declared parts, a rule for
where its instances live, and an encoding that says which marks in the
markdown carry which verb. Break the encoding and the lint rejects the
file; follow it and a parser reads the file into rows. And they can be
anything, because runbook and loop are only two examples that happen to
be in common usage across the industry. You declare whatever your domain
is made of. That's the whole point, it's as general as programming. It's
programming in our own words.

https://github.com/GeoffNordling/dev-playbook/blob/main/working-docs/doc-type-system/doc-type-system/reference-model.md

So we declare our domain precisely. The stochastic code doesn't go away,
we still write it in natural language, but now it has deterministic
structure embedded in it and a lint, a parser, and a constraint solver
holding it to that structure. What we've got at that point is an actual
programming language whose surface syntax is English. But what good is
that if it's still a pile of markdown nobody can read?

That's where the **knowledge graph** comes in. One object per checkout,
nodes and edges and nothing else, built entirely by deterministic code,
and every single row in it carries a receipt naming the extractor that
produced it and the line of the file it came from. Nothing in there is
unsourced and nothing in there was guessed. Once you have the graph, a
view is just a selection from it: it drops rows, it never adds one. The
seven I want:

- **containment tree** — how is it organized
- **catalog** — what exists
- **dependency graph** — how do the parts relate
- **control flow** — what happens in what order
- **data flow** — what's produced and what's consumed
- **cross-reference matrix** — which X take part in which Y
- **interface card** — how one thing is used

Call graph, import graph, class hierarchy. Same idea, for a system
that's half prose. And they're cheap: deterministic code builds them in
milliseconds, they're identical until the checkout changes, and no model
token is spent to put anything on screen. So slop was never really about
volume. It was about not understanding our own system, and now there's a
view of a stochastic system built entirely by deterministic code, where
everything on the screen traces back to a line in a file.

So that's the whole thing. A programming language of our own design,
written in markdown, where the primitives are nouns and verbs we
invented for the domain in front of us. We're programming in the space
of ideas. And once it's a language, the rest is old news: Google built
Kythe and Meta built Glean to do exactly this for real code, extracting
every fact out of the source, putting it in one graph, anchoring every
fact to the line it came from, and letting every view be a query over
it. That architecture is proven and it's been running at scale for
years. The only reason it never reached our markdown is that markdown
had no types in it to extract. Now it does.

Guido invented Python. Great language. Fixed language: his primitives,
his semantics, and everybody downstream programs inside them. What's new
is that we don't have to stop there anymore. We get to invent the
language for the domain in hand, and it can be as large or as small as
we like, a lemonade stand or a whole software factory. And what comes
out the other side is a mixture, deterministic code and stochastic code
all mixed together, one graph over both halves of it. That's the future.
It's turtles all the way up.

---

## Not in the email yet

- **The admission that it isn't built.** The email describes seven views
  and the graph in the present tense. One line before the close fixes
  it: the pieces exist, we think they fit together, we haven't proven
  it.
- **"Turtles all the way up" lands twice**, at the ladder and at the
  close. Kept as a bookend. Cut the first if the ending should hit
  harder.
- **The domain-declaration point is made twice**, once at "you declare
  whatever your domain is made of" and again at "so we declare our
  domain precisely." Fine in an email, but one could go.

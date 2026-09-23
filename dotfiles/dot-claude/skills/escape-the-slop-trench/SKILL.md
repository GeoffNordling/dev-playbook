---
name: escape-the-slop-trench
description: Finds the stretch of this session's work that ran as a list of steps, states the target state those steps reached for as falsifiable rules, and writes the rules into a Standard once the user agrees.
disable-model-invocation: true
model: inherit
effort: high
---

# Escape the Slop Trench

The slop trench is work driven by a list of actions: the user or the agent
names the steps, the agent does them in order, and the user watches. Replace
the list with a target state, written as rules a verifier can decide. Then
the instruction becomes "reach the state that satisfies the rules", and the
verifier supervises in place of the user.

Run inline. Launch no subagent: the conversation is the input.
{Never {Commit}}.

## Find the stretch

Read this conversation as work done: the edits, the commands, the lists
followed, whoever wrote them. Find the stretches that ran as a list of
steps done one after another.

Pick the one stretch where a target state would help most: the most steps
replaced, and the most likely to come back in another session, on other
content.

The example: to land one change, the agent renumbered the sections of a
skill, updated the ledger entry that names those sections, changed an index
row, and renamed a role in two skeleton files. Each step happened only
because someone remembered it.

## State the target

Do not read the standards index yet. A list of the existing standards shows
only the rules that fit them.

Ask what state the steps reached for, and write it as rules: each one
sentence, true or false of one file. In the example, each step becomes a
rule that makes the step unnecessary:

| Step done by hand | Rule that replaces it |
|---|---|
| Update the ledger entry to the new section numbers | Every residual-ledger entry names only sections its skill has. |
| Change the index row | Every index row's description equals its file's `description`. |
| Rename the role in the skeleton files | Every agent a skeleton names exists, with the job its definition gives it. |

The rules are enough when a state that satisfies them needs none of the
stretch's steps done by hand.

Give each rule its kind: deterministic, where a function can decide it and
a check runs it free at every gate; or stochastic, where a judge must
decide it.

## Announce the target

{Report the stretch and its target, and nothing else}:

    Stretch: <the steps, in a few words each>
    Target:
    - <rule> · <deterministic or stochastic>
    - <…>

With no stretch that ran as a list of steps, say so in one sentence and
stop.

Then {Read [place.md](references/place.md)} and carry it out. It ends the
turn at the user's ruling.

When the user has ruled, {Read [write.md](references/write.md)} and carry
it out.

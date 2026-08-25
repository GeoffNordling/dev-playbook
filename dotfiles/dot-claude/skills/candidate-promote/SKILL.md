---
name: candidate-promote
description: Promote a Candidate from the current repo's CANDIDATES.md into a committed GitHub issue. Use when the user asks to promote a candidate, or names an entry in CANDIDATES.md they now want built.
disable-model-invocation: false
model: inherit
effort: xhigh
arguments: [candidate]
---

# Promote a Candidate

Turn a Candidate into committed work. A Candidate is uncommitted future work
recorded in the repo's root `CANDIDATES.md`; promotion authors a GitHub issue
from it and **deletes the entry in the same change**, so the work never sits in
both homes. {Read [candidate conventions](~/workspace/dev-playbook/standards/tracking/candidates.md)
as the contract}.

This skill owns the lookup and the delete. Authoring the brief and the
four-tuple is /intake's job — it accepts a free-form idea as text, so nothing
is passed but the entry.

## Steps

1. **Read `CANDIDATES.md`** at the repo root. If the file is absent, say so and
   stop — there is nothing to promote.

2. **Locate the entry.** Match `candidate` against the bolded entry names. If
   none was given, or the match is ambiguous, list the candidate names
   and ask which one. Never guess between two plausible entries.

3. **Decide the scope with the user.** An entry with nested children is a
   scoping question: ask whether they want the whole subtree promoted, or one
   child alone. An entry with no children promotes as itself. Either way this
   skill lands **one** issue — intake does not slice and never mints an epic, so
   a subtree promotes whole and its decomposition waits for the `design` node.

4. {Run [/intake](~/.claude/skills/intake/SKILL.md) with the entry's name and
   prose as the free-form idea — the children's text too, when promoting a
   subtree}. A one-line entry is the expected input: intake grills the idea,
   authors the brief and four-tuple, and lands the issue on its own
   confirmation gate, routing a subtree to `phase:design`.

5. {If intake reports the issue number, {Write the promoted entries out of
   `CANDIDATES.md`; remove the whole subtree when the subtree was promoted —
   the work is committed to that one issue now, wherever design later splits
   it; when only one child was promoted, remove that child and leave the
   parent. If removing the last child of a parent leaves it childless, keep
   the parent — an outcome with no remaining decomposition is still a
   Candidate}}.

6. {Report the issue number and which entries were removed}. Leave the
   change uncommitted for the user's review unless they ask otherwise.

## Boundaries

- **Never delete an entry before intake lands the issue.** A failed or
  abandoned intake leaves `CANDIDATES.md` untouched.
- **Promotion moves a record between homes.** The work itself is then
  dispatched through the software factory like any other issue.
- **Repo-scoped Candidates only.** This skill moves entries recorded as
  serious, repo-scoped Candidates; random, unfiltered, or cross-repo ideas go
  to mission-control via /idea.

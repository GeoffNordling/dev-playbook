---
name: candidate-promote
description: Promote a Candidate from the current repo's CANDIDATES.md into a committed GitHub issue, deleting the entry as the issue lands. Use when the user invokes /candidate-promote, says "promote this candidate", "turn that candidate into an issue", or names an entry in CANDIDATES.md they now want built.
disable-model-invocation: false
model: inherit
effort: high
argument-hint: "[candidate name]"
---

# Promote a Candidate

Turn a Candidate into committed work. A Candidate is uncommitted future work
recorded in the repo's root `CANDIDATES.md`; promotion authors a GitHub issue
from it and **deletes the entry in the same change**, so the work never sits in
both homes. The contract is
[candidate conventions](~/workspace/dev-playbook/standards/tracking/candidates.md).

This skill owns the lookup and the delete. Authoring the brief and the
four-tuple is /intake's job — it already accepts a free-form idea as text, so
nothing is passed but the entry.

## Candidate: $ARGUMENTS

## Steps

1. **Read `CANDIDATES.md`** at the repo root. If the file is absent, say so and
   stop — there is nothing to promote.

2. **Locate the entry.** Match `$ARGUMENTS` against the bolded entry names. If
   no argument was given, or the match is ambiguous, list the candidate names
   and ask which one. Never guess between two plausible entries.

3. **Decide the scope with the user.** An entry with nested children is a
   decomposition question, not a mechanical transform: ask whether they want
   the whole subtree promoted as an epic with children, one child alone, or the
   parent collapsed into a single issue. An entry with no children promotes as
   itself.

4. **Invoke /intake**, passing the entry's name and prose — plus the children's
   text when promoting a subtree — as the free-form idea. A one-line entry is
   the expected input, not a problem to solve first: intake grills the idea,
   authors the brief and four-tuple, and lands the issue(s) on its own
   confirmation gate. Never pre-author the brief here, and never turn an entry
   away for being thin.

5. **Delete the promoted entries** from `CANDIDATES.md` once intake reports the
   issue number(s). Remove the whole subtree when the subtree was promoted; when
   only one child was promoted, remove that child and leave the parent. If
   removing the last child of a parent leaves it childless, keep the parent —
   an outcome with no remaining decomposition is still a Candidate.

6. **Report** the issue number(s) and which entries were removed. Leave the
   change uncommitted for the user's review unless they ask otherwise.

## Boundaries

- **Never delete an entry before intake lands the issue.** A failed or abandoned
  intake leaves `CANDIDATES.md` untouched — losing the entry loses the work.
- **Do not implement anything.** Promotion moves a record between homes; the
  issue is then dispatched through the software factory like any other.
- **Not the capture path.** Random, unfiltered, or cross-repo ideas belong in
  mission-control via /capture. This skill only moves entries that are already
  recorded as serious, repo-scoped Candidates.

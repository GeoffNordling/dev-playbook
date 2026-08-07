---
type: Decision-Record
title: "One Word for the Person: User"
description: Collapse the two-name convention for the workspace's one dispatching actor into a single word — `user` in every authored file — banning the second noun outright rather than assigning it a voice
date: 2026-08-06
---

# One Word for the Person: User

## Context

One actor dispatches the work, reviews it, and approves it. Until this record
the workspace gave that actor two names and chose between them by voice.
Agent-facing instruction text — every `CLAUDE.md`, every skill body, every rule
body — said `user`, on the argument that those files have exactly one audience
and should name the person the way Claude Code names them
(`AskUserQuestion`). Declarative documentation — `software-factory/`,
`standards/`, `docs/`, `README.md` — used a second, biological noun, on the
argument that third-person description of the system reads better with it. The
retired rule stated both halves in full and is recoverable verbatim from
`git show 207a1bf:standards/prose/conventions.md`.

The split cost more than it bought, in both directions:

- **Every file needed a voice decision before it needed a sentence.** The rule
  keyed on the document's audience, but real files straddle it — a standard
  quoted in a skill, a skill's frontmatter read by both, a judgment claim
  describing an agent-facing rule from the outside. Deciding the voice was a
  per-file judgment call with no deterministic answer.
- **Review friction ran both ways.** A doc using the agent-facing word and a
  skill using the declarative one were each a finding, so the convention
  generated corrections in two directions instead of one.
- **The rule could only be enforced on half the repo.** `repo-lint` banned the
  second noun inside agent-facing files, because that is the only side where
  the correct word was unambiguous. Everywhere else the convention was prose
  the reviewer upheld by eye.

One word plus one ban removes all three at once: no audience judgment, one
direction of correction, and a rule a detector can run over every authored
file.

## Decision

The actor is `user` in every authored file — one word, no synonyms, in any
case, plural, or hyphenated compound. The other noun is banned outright rather
than reassigned to a voice.

Where the banned compound was the natural phrase, the replacement drops it
rather than translating it: "readable", not "readable by a person"; the user's
own act named directly ("a step the user runs") rather than adjectivally. Text
this workspace does not own is exempt and unchanged — skills vendored under an
`.agents/` path, and verbatim mirrors of external specifications
(`standards/references/okf-spec.md`).

Dropping is the default, not a rule against ever naming the actor. Where the
qualifier is doing real work — distinguishing which of several things is meant,
rather than decorating a noun that already implies the actor — the replacement
translates instead. The factory's checkpoints document is the case: the system
pauses at many points and only some are the user's, so
`software-factory/user-checkpoints.md` states which kind the document covers.
The test is whether removing the word loses a distinction a reader needs.

The swap ran across roughly 300 occurrences in about 70 files, in four
commits — `software-factory/` and the root docs, `standards/` and `docs/`, the
harness and code and judgments, and the rename of the factory's checkpoints
document, whose own filename carried the banned noun, to
`software-factory/user-checkpoints.md`. The revised rule now lives in `standards/prose/conventions.md` under
"Terminology: the person is the user"; it states the ban positively, naming
only the allowed word, because a rule that spelled the forbidden one would be
its own violation.

### Decision Records were swapped under an explicit waiver

Seven historical records (`0001`, `0002`, `0003`, `0005`, `0006`, `0007`,
`0016`) contained the banned noun. Record immutability would normally freeze
them. The owner waived it for this change specifically and only this far: the
word is swapped, nothing else in those files changes, ever. The waiver covers
the word wherever it appears in them, including inside code spans and inside a
quotation of an external source.

### The enforcing lint landed with the swap

The half-repo check was replaced rather than left standing. `prose-lint` gained
`prose.banned-word`, a deterministic ban over **every tracked file** of any
type — no code-span and no fence escape, since a banned word inside backticks
is still the word — with the vendored and verbatim-mirror exemptions above.
`repo-lint`'s `agent-facing-voice` check narrowed to the first person it still
owns, and `dev_playbook.voice` narrowed with it; `repo-init` consults the ban
before scaffolding, so a repo name carrying the noun is refused up front.

The rule id names no noun (`prose.banned-word`, not the word itself): the scan
reads whole files, so a card or README quoting the id would otherwise trip the
rule it documents.

Two different things let a file still carry the word, and they are not the same
kind of thing:

- **Out of scope.** The scan never reads text this workspace does not author —
  the vendored `.agents/` trees (reached through their symlinks too, since a
  symlink's content belongs to its target) and verbatim `type: Reference`
  mirrors such as `standards/references/okf-spec.md`. Three such files carry
  the word today; the ban has no opinion about them, because the swap never
  claimed them either.
- **Exempted inside scope.** Exactly two authored files are excused by name:
  the detector `src/dev_playbook/prose_lint.py` and its test, which must spell
  the word to ban it. That roster is a constant in the detector rather than a
  convention, so a third exemption is a code change and a visible one.

## Recovery

The two-name convention was last alive on `main` at commit
`207a1bf64f4ce3a0df191e479c65609e87d91ec4`, the branch point of
`worktree-simplify`. The retired rule in full:

```
git show 207a1bf:standards/prose/conventions.md
```

The retired section is the `## Terminology…` heading immediately after "Name
concepts once, use consistently"; its own title names both words. It carries
what this record summarizes plus the platform-token
carve-out it relied on (the `~/.claude/` settings tier, a "user message",
`user-invocable` — Claude Code's own names, never translated), which the
collapse makes moot.

The swap commits on `worktree-simplify`, in order, are `b1aad6d` (the
checkpoints-document rename), `f7c5d9f` (`software-factory/` and the root
docs), `75dec08` (`standards/` and `docs/`), `955964a` (the harness, the
code, and the judgments), `43af60c` (two files no sweep's scope had reached),
and `f251469` (the lint, which swapped the replaced machinery as it landed).
Any individual file's pre-swap text is `git show 207a1bf:<path>`.

## Consequences

- **Two historical records now cite a label literal that never existed.**
  `0001` and `0005` describe the retired 5-state issue-label vocabulary, and
  the swap rewrote one of its label names. The label itself is long gone, so
  the records document a vocabulary no repo carries; treat their label names as
  prose, not as strings to match.
- **One quotation in `0003` is no longer verbatim.** The record quotes an
  external framework's own text, and the swap changed a word inside the
  quotation. The owner ruled that it stands as swapped — the ban admits no
  exception for quotations. Cite the upstream source, not this record, when the
  exact wording matters.
- **Every consumer repo inherits the ban at its next pin bump.** The published
  `playbook-lint` hook dispatches `prose-lint`, so a consumer that bumps its
  dev-playbook `rev` starts failing its own commit gate on every occurrence it
  carries. Each repo needs its own swap before it bumps
  ([distribution.md](/standards/build/distribution.md)).
- **Reinstating a second noun means re-deciding this.** The collapse is a
  vocabulary decision, not a formatting one; a future document that wants a
  different word for the actor argues against this record rather than adding an
  exception to the lint.

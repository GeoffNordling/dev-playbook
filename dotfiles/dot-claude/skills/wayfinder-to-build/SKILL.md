---
name: wayfinder-to-build
description: Hands a completed wayfinder map off to the software factory — slices the destination with the user, then mints a build epic and thin child stubs tied to the map's resolutions as provenance.
disable-model-invocation: true
model: inherit
effort: xhigh
argument-hint: "<map-number>"
---

# Wayfinder to Build

The hand-off. A completed wayfinder map holds every decision on the way to its
destination — resolved on its tickets, indexed in Decisions so far — and has
executed nothing. This skill turns the map into the factory's input: a build
epic whose children carry the work, every piece tied back to the resolutions
that decided it. `$ARGUMENTS` names the map.

## Read first

Before doing anything else:

- Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md)
  end-to-end — the epic body format, the readiness bar, the One-goal test, the
  vertical-slice rules, and native relationships.
- Read [software factory](~/workspace/dev-playbook/software-factory/software-factory.md)
  end-to-end — the two regions, the label scheme, and where the minted children
  go next.
- Invoke /codebase-design — deep modules, interfaces, the deletion test: the
  qualities a good slice boundary preserves.

Then report: `READ: issue-authoring.md, software-factory.md,
codebase-design`. Proceed only after.

## Standalone, with provenance

The style everything minted here follows — the tie between the build work and
the map:

- **Every artifact stands alone.** The epic's outcome and rationale — and,
  later, every child brief — carry everything their reader needs in their own
  text. Nothing minted here says "see the map for what this means."
- **Resolutions are linked as provenance.** "Per the
  [Deviation regime resolution](…)" lets an auditor walk backwards to the why;
  the link is bookkeeping, never required reading.
- **Divergence is declared inline where it happens** — "*(adapted from the
  resolution's push-the-branch step: build agents cannot push)*" — never
  carried silently.
- **Refer by name**, per the wayfinder skill's own rule: a name wraps its
  link; a bare issue number stands for nothing.

## 1. Verify the map is complete

`$ARGUMENTS` names an issue labelled `wayfinder:map`. The hand-off takes only
a **finished** map: every child ticket closed (the open-children query in
[tracker operations](~/workspace/dev-playbook/standards/tracking/tracker-operations.md#wayfinding-operations)
returns nothing) and no fog left in **Not yet specified**. Anything still
open — a ticket, a fog patch — stops the hand-off: report exactly what is
open and end the session there.

Done when: the map is verified complete, or the session ended on that report.

## 2. Read the map

The map body first — destination, notes, every line of Decisions so far.
Then every child ticket in full — question body and all comments
(`gh issue view <n> --json title,body,comments`): harvest corpora, amendments, and linked
assets ride in the trail. Resolutions are
the canonical decisions this hand-off executes; the epic re-litigates none
of them.

Done when: every child ticket of the map has been read in full.

## 3. Slice, with the user

The map planned; it did not slice. **The slicing is this skill's decision to
take, here, with the user** — never assume the map made it. Invoke /grilling and
work these three branches as its design tree — each round asks the whole
frontier in the skill's numbered question-and-recommendation format, and the
user rules every question before the next round:

1. **The delivery surface** — for each load-bearing resolution, the files and
   systems it lands on.
2. **The slices** — cut per the
   [vertical-slice rules](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#vertical-slice-rules),
   boundaries falling on module seams per the module-design standard, each
   slice tested against the One-goal bullet's two-question orthogonality test
   at epic and slice altitude. What fails the test is deferred exactly as the
   bullet says: a real tracker stub at `phase:intake`, named in the epic's
   Out of scope.
3. **The ordering** — dependency order, with the reason for each edge. A
   dependency is any **consumed artifact**, not just textual overlap: a slice
   that dispatches or cites what an earlier slice installs is blocked by it.

The children cut here are ultimately designed and released under the design
node's own decomposition guidance —
[the decompose exit](~/workspace/dev-playbook/dotfiles/dot-claude/skills/design/references/decompose.md)
— so weigh that guidance while cutting, not after.

Done when: the user has approved a named, dependency-ordered slice list,
every slice passing the two-question test.

## 4. Mint the build epic

A fresh issue — the map stays what it is; the two are tied by links, not
labels. Title it to pair with the map's: "Factory reliability mechanisms —
wayfinder map" begets "Factory reliability mechanisms — build epic", the
shared prefix tying the two at a glance. Label it `category:*` **only**, and
give it the epic body from
[issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#the-epic-body):

- **Outcome** — opens by naming the map once ("per the resolutions of the
  [<map name>](url)"), then states the end state in prose that stands alone.
- **Decomposition rationale** — the slicing decision and its ordering
  reasons, standalone, with the resolutions that informed it linked as
  provenance.
- **Standing rulings** — seeded with exactly these two, which bind every
  child session (they read the epic; they do not read this skill):

  ```markdown
  **Standing rulings:**
  1. Child briefs stand alone: a builder needs nothing beyond the brief. Map
     resolutions are linked as provenance, never as required reading, and any
     divergence from a resolution is declared inline where it happens.
  2. When the build contradicts a map resolution, the resolution comment is
     amended in place on its ticket — edit history preserves the original —
     and the map's Decisions-so-far line gains "*(amended during the build
     epic — see the resolution)*".
  ```

  Later rulings append after these; numbers are never reused.

When slicing yielded a single slice, there is no epic: mint one leaf in the
same style — standalone body, resolutions linked as provenance — and carry
the two rulings in its brief's Out of scope-adjacent prose rather than a
rulings section.

Done when: the epic is live and its body carries all three sections.

## 5. Mint and wire the children

One issue per slice, in dependency order, each a **thin stub**: a title
naming the slice, a short body stating the slice's goal and naming the
resolutions it executes (linked, per the style above), and the full
four-tuple at `phase:design`. Assigning that four-tuple is the children's
intake, done here in place — no child round-trips through the intake node,
same as a design decomposition's children. Each child is carried to brief-complete — and
released at its own
[issue-review verdict](~/workspace/dev-playbook/software-factory/user-checkpoints.md#the-issue-review-verdict)
— later, in its own design session with full attention; nothing here authors
a brief.

Then wire the native relationships, commands per
[tracker operations](~/workspace/dev-playbook/standards/tracking/tracker-operations.md):
every child a sub-issue of the epic, and every ordered slice blocked-by its
predecessor.

Done when: every approved slice has a live, labelled stub, and both
relationship graphs match the approved ordering.

## 6. Report the shape

Show the user the whole hand-off on screen: the epic, the ordered children
with their four-tuples, both relationship graphs (they need not align), any
deferral stubs step 3 minted, and the next move — each child through
`/design`, one at a time.

Done when: the user can see the full shape without opening GitHub.

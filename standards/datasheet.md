---
type: Standard
title: Datasheet Standard
description: The datasheet — a fixed-section, budgeted HTML report giving a system's owner trust and direction without reading its code
---

# Datasheet Standard

A datasheet is a fixed-section, budgeted, accuracy-gated HTML document that
gives a system's owner — who will never read its code — enough understanding
to trust the system and direct its future work. This standard is the contract
for generating one: an agent handed this document, a subject name, and a scope
manifest produces a conformant datasheet with no other instruction. The
datasheet is total over any file set: pointed at a tree with no code, its
sections render blank, never as errors.

## The owner

Every visible sentence must be meaningful and useful to a reader who will
*never* open the code — not "hasn't yet," never. This reader is the **owner**:
an experienced engineer who delegates all coding to agents and collaborates on
design. The owner reads a datasheet to answer two questions:

- **Trust** — what does this system do, what does it touch, what is verified,
  and what should I worry about?
- **Direction** — what vocabulary and structure does it have, so I can specify
  future work precisely?

## Scope and identity

The caller chooses the scope: an explicit manifest of paths and globs. The datasheet never decides
its own scope. The **subject** names the datasheet and its file; the caller supplies it, or the
generator proposes one and the caller confirms. 

- Home: `docs/datasheets/<subject>.html` in the covered repository.
- One datasheet per subject. Regenerating an existing subject overwrites the
  file in place.
- Before creating a new subject, check every existing sheet's identity by its
  stamp comment alone — never by reading a full sheet. If the new manifest
  overlaps an existing one, stop and surface the overlap to the caller instead
  of writing a near-duplicate.
- Datasheets are regenerated, never hand-edited.

## Document form

One self-contained HTML file: inline CSS, no scripts required to read, no
external requests. It renders complete from `file://` in any browser.

The document has two layers:

- **Visible layer** — everything rendered by default. It stands alone: reading
  only the visible layer yields the complete mid-level understanding. Hard
  budget: **1,000 words**, counted as every visible word except the stamp
  block. Diagram and exhibit text counts.
- **Collapsed layer** — `<details>` elements holding optional depth. Hard
  budget: **1,000 additional words**. Collapsed content deepens the story; it
  never completes it — nothing in the visible layer may depend on it.

The visual form is fixed, and the [example](#example) is its normative
embodiment: a sheet copies the example's stylesheet and card markup verbatim
and varies only the content. The layout is a fact rail beside a main grid:
the rail (narrow, sticky) holds identity, Concepts, Touch surface, and Tests
for constant-position lookup; the main grid pairs Purpose and Behavior side
by side, then gives Shape and Assessment each a full-width band; on narrow
windows the main grid collapses to one column. Color is semantics, never
decoration — green marks the verified, amber marks opinion and coverage
gaps, indigo chips mark concepts, slate is neutral.

The ceiling is independent of scope: a whole-repository datasheet and a
single-tool datasheet share the same maximum, and a larger scope raises the
altitude of description rather than the word count. The ceiling is not a
target — a small subject yields a short sheet. Depth comes from narrowing
scope, never from lengthening the document.

## Language

The subject of every visible sentence is a behavior or a concept — what the
system does, decides, produces, touches, or refuses. Code identifiers
(variables, functions, env vars, filenames) appear only as parenthetical
anchors or in the collapsed layer, never as what a sentence is about. State
the consequence first; the mechanism supports it.

Banned:

> `ENV_VAR` is set to 1 when the pre-commit hook takes the fallback path.

Blessed:

> When the primary lookup fails, the hook silently falls back to a degraded
> mode (opt-out via an env flag).

Same fact — but the blessed sentence is about a behavior, means something to
the owner, and demotes the identifier to a parenthetical.

Structure over prose: anything enumerable — concepts, touched paths, test
coverage — renders as chips, labeled cells, or rows, never as a paragraph.
Prose is reserved for what only a sentence can say: purpose, what an exhibit
demonstrates, a judgment's consequence.

## Content classes

Every section is one of two classes, and the accuracy standard differs:

- **Extractive [E]** — statements derivable from the files. A false extractive
  sentence is a defect, as a failing test is a defect in code. Every
  extractive claim carries a source anchor — file path, and line where
  sensible — in a `title` attribute or the collapsed layer; anchors spend no
  budget.
- **Judgment [J]** — the generator's opinion, confined to the Assessment
  section and visually marked as opinion. Judgments must be grounded; owner
  disagreement with one is not a defect.

## Sections

Every section always appears, in a fixed place. The fact rail holds the
lookup sections under the identity header; the main grid holds the narrative
sections. The markup follows the same order — rail, then main. A section
whose subject is absent states that plainly ("None.") — presence with an
affirmative blank is the signal, silence is a violation.

| Section | Place | Class | Contents |
|---|---|---|---|
| Stamp | file head + rail header | E | Subject name, scope manifest, git commit covered, generation date, generator model. Budget-exempt. |
| Concepts | rail | E | The vocabulary the owner needs (typically 3–7) — a chip and one defining phrase each. |
| Touch surface | rail | E | Six fixed cells — Reads, Writes, Spawns, Net, Env, Deps — each concrete or an explicit "none". |
| Tests | rail | E | Rows: what is verified (green), what is gated or missing (amber). "None." when no tests exist. |
| Purpose | main | E | What the system is for and why it exists. Three sentences or fewer. |
| Behavior | main | E | One worked example: an invocation, its input, its output. |
| Shape | main, full band | E | The flow between major parts — the diagram carries it. |
| Assessment | main, full band | J | What the owner should worry about. |

### Stamp

The stamp exists in two forms carrying the same fields: a YAML block inside an
HTML comment that opens the file — the first thing in it, before the doctype —
so a datasheet's identity is readable from its opening lines alone; and the
identity card that opens the fact rail. The [example](#example) shows both.

### Concepts

Concepts are the owner's vocabulary, not the code's. Each chip names
something the owner needs in order to direct future work or to read the rest
of this sheet; the defining phrase is one clause. A concept earns its place
only when another part of the sheet leans on it — the exhibit, a diagram
node, an Assessment item. A concept nothing else references is a souvenir of
reading the code; cut it.

### Touch surface

Six fixed cells — Reads, Writes, Spawns, Net, Env, Deps — each holding the
concrete surface: paths, commands, variables, packages, with qualifiers kept
to a word or two ("overwrites", "test-only"). An empty cell states "none"
explicitly.

### Tests

Rows, not paragraphs. Each row is a count or mark plus what that
verification covers — the suite's shape, never its file list. Verified
coverage is green; gated, skipped, or absent coverage is amber.

### Behavior

The exhibit is the smallest input/output pair that demonstrates the system's
primary transformation — any element that could be deleted without weakening
the demonstration is cut. Two labels, both mandatory:

- **verified:** `run` — the invocation was executed during generation — or
  `not-run`, with one sentence saying why (e.g. unsafe, private information, not runnable, needs
  credentials).
- **exhibit:** `captured` — real output, elisions marked honestly ("showing 14
  of 3,400 lines") — or `constructed` — a synthetic illustration, which may be
  informed by a real run.

Exhibit content is committed forever; nothing unvetted for sensitivity goes
in. When real output is too large or too private, run live for verification
and construct a small exhibit (`verified: run`, `exhibit: constructed`).

### Shape

The diagram carries the section; prose is one caption sentence naming the
entry point. Every node names a concept or artifact the sheet already
discusses — the diagram draws relationships among the sheet's vocabulary and
never introduces entities of its own. Edges are labeled with the data that
flows across them; the input and output endpoints are tinted (blue in, green
out). Node and edge labels count against the visible budget. The medium is
Graphviz: DOT rendered to SVG, inlined, with the DOT source embedded as an
HTML comment beside it. A diagram that fails to render is a generation
failure, not a degraded datasheet. Optional depth — a module roster, a
schema — goes in a collapsed block at the card's foot.

### Assessment

The one section allowed opinion, fenced five ways:

1. Every judgment rests on facts already stated in the extractive sections and
   points to them. Assessment interprets the sheet; it introduces no new facts.
2. Flag, don't prescribe. "Nothing verifies the output shape — consumers are
   trusting string templates" flags; "add schema validation" prescribes and is
   banned.
3. Consequence first, mechanism as support — the language rule applies to
   opinions too.
4. At most five items, each a bolded consequence headline over at most one
   supporting line. Ranking is the point.
5. "Nothing concerning." is a legal answer and must be stated affirmatively.

## Example

[datasheet-example.html](/standards/datasheet-example.html) is a complete,
minimal datasheet for a fictional tool — read it in full before generating.
It is normative for form: copy its stylesheet and card markup verbatim — the
stamp comment first, the rail and main regions, the chips, cells, rows,
badges, and the Shape diagram in the prescribed form (inline SVG, DOT source
in a comment beside it) — and vary only the content. It does not set the
size: a real system may spend the full budget.

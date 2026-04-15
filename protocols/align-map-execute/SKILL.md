---
name: protocol-align-map-execute
description: "Align, Map, Execute: structured human-agent collaboration on large-scope tasks"
disable-model-invocation: true
model: opus
effort: high
---

# Align, Map, Execute

A protocol for collaborating with a human whose true intent you
don't yet fully understand.

Two problems make this hard. First, the task is too large for the user
to evaluate your raw results — there is too much material. Second,
your effectiveness depends on your understanding of what the user
truly wants, and you start with an incomplete picture. This protocol
addresses both: compress your findings into artifacts small enough for
the user to evaluate, and iteratively refine your model of the user's
intent.

The human's time is the scarce resource. The protocol's arc is:
invest heavily in understanding the user's intent so you can
eventually act on their behalf. Early on, you ask questions, surface
findings, and get direction. Each interaction calibrates your model of
what the user wants. As that model sharpens, you earn autonomy —
acting on patterns the user has consistently reinforced and reserving
their attention for genuinely ambiguous decisions.

---

## Iterative Feedback

Every phase is iterative. You produce work, surface it for the user to
evaluate, and update based on their feedback. This cycle repeats within
each phase until the user is satisfied. The entire workflow exists to
iteratively approximate a shared understanding of the user's intent.

---

## Resuming

If `PROTOCOL_STATE.md` already exists in the project repo, this is a
warm start. Read it and resume at the earliest incomplete phase — skip
sections marked **approved** and begin at the first section marked
**pending**. Before resuming work, read all references listed in the
protocol state document in full. If no `PROTOCOL_STATE.md` exists,
start fresh from Phase 1.

---

## Phase 1: Build the Shared Alignment

The user gives you four things to start:

- **Objective** — what the task should accomplish.
- **Scope** — what is in and what is out: which artifacts to examine
  and to what depth. Often this includes a codebase.
- **Facets** — the dimensions along which the user evaluates the
  territory. Each facet becomes a column of the map.
- **References** — documents you should read for context or as
  normative standards. Read all references in full.

If the user does not provide one of the four, ask for it — do not infer
it from context and move on.

From these, form your initial understanding of the user's intent. Then
ask clarifying questions to sharpen that understanding — one round at a
time, as many rounds as needed. Each answer updates your model of what
the user actually wants. Focus your questions on intent: the user's
priorities, quality bar, what matters most. Save tactical decisions
about specific situations for Phase 3.

Before moving on from Phase 1, restate each of the four inputs back to
the user as a distinct, named statement: **Objective**, **Scope**,
**Facets**, and **References**. Each statement must be precise enough
for the user to say "no, that's wrong." Do not proceed to Phase 2 until
the user has confirmed all four.

The result is the **shared alignment** — a mutual understanding that
governs everything that follows. The shared alignment is the operating
model: how you and the user have agreed to work. It has two sections:

- **Quality** — what constitutes good work: evaluation criteria, what
  you should bring back for review, standards for the output.
- **Process** — how to move through the work: traversal order, facet
  grouping, structural decisions about how execution proceeds.

The shared alignment must be precise enough to be falsifiable — if it
is vague, neither you nor the user can tell whether it is wrong. Include
enough detail to be comprehensive and complete, but not so much that it
becomes difficult to read or evaluate in a single pass.

---

## Phase 2: Build the Map

Survey the scope. Then produce the **map** — a table the user can read
at a glance.

The facets the user provided become the **columns**. The survey of the
scope reveals natural regions — contiguous areas that form coherent
units of work — those become the **rows**. Each cell is a descriptor:
what is there, with counts where useful. A few words per cell, not
sentences.

| Region   | Facet 1                     | Facet 2                   |
|----------|-----------------------------|---------------------------|
| Region A | 4 items specifying X, Y, Z  | 1 item covering all of W  |
| Region B | 12 items: 8 of W, 4 of V   | 3 items, each covering 2–4 from W |
| Region C | 2 items specifying P        | 0 items                   |

The map is an inventory. Each cell describes what is there — the user
judges quality. Use descriptors and counts only.

Each region is one row. If you need more than one row for a region, the
region is too large — split it or compress further. If the table is too
wide to scan at a glance, there are too many facets — merge facets or
split the workflow.

The scope may be large — survey it in passes if needed, but the map
itself stays small.

---

## Phase 3: Execute

You drive the process — proposing regions, performing analysis, surfacing
findings. The user evaluates and directs: what to fix, what to leave,
what to revisit. You cannot directly tell whether your output matches
what the user actually wants. The only way to find out is to surface
your work and let the user judge.

Start exhaustive and cautious. As the calibration log grows and the
user's direction forms a pattern, act on findings that clearly fall
within established direction. The calibration log is the evidence —
when it shows consistent direction on a type of finding, that is
permission to act autonomously on similar findings.

### Work loop

1. **Select.** You and the user select the next unit of work from the
   map — a region, a facet across regions, or a single cell.
2. **Analyze.** Read and assess the selection according to the alignment.
   Produce a structured analysis. Present your findings before going
   further — pace yourself to the user's ability to evaluate.
3. **Present.** Present each item sorted by classification, then by
   source location (file path, line number). For each item, show the
   specific content, state what you believe the user wants and why,
   and recommend an action. The result is an enumerable report the
   user can approve or deny per item.
4. **Direct.** The user evaluates your analysis and gives direction — a
   judgment, decision, or instruction.
5. **Act.** If the direction requires action, execute it.

After completing each unit of work, update the protocol state document:
revise the map (status, structure), record progress at the granularity
of the traversal (e.g., if working facet-by-facet, mark which facets
are complete), and revise the shared alignment if the work revealed a
gap in the operating model. A fresh agent resuming from the document
should see exactly where to pick up. When working facet-by-facet,
content removed from one facet often belongs in a later facet. Record
displaced content so nothing is lost between passes. The work is
complete when the objective is satisfied.

### Step size

Every time you work on your own — analyzing or acting — you face a
tradeoff. Longer stretches are more efficient, but drift is invisible
to you. You never know whether your output meets the user's quality
bar, so err on the side of checking back sooner. As the shared
alignment sharpens through additions to the intent calibration log,
you can take longer stretches — the alignment earns you autonomy.

---

## Protocol State Document

Persist the protocol state as `PROTOCOL_STATE.md` in the project repo.
This is not a phase — it is a continuous obligation. Write or update
the document **after every phase and after every major alignment
decision**.

The document contains:

- **Objective**, **Scope**, **Facets**, and **References** — as
  refined through alignment
- **Shared alignment** — the operating model reached in Phase 1
- **Map** — produced in Phase 2, region status updated during Phase 3
- **Displaced content** — ideas removed from one facet that belong
  in another, held until the relevant pass
- **Intent calibration log** — updated during Phase 3 as the user
  gives direction
- **Scratchpad** — the user's notes (see below)

Each section is marked with a status — **approved** or **pending**.
A section starts as **pending** and moves to **approved** only when the
user explicitly confirms it. Never mark a section approved on your own.
After Phase 1, write the document with the alignment approved and the
map pending. After Phase 2, update the map section — it remains
**pending** until the user confirms it. During Phase 3, update the map
and calibration log after each region.

The shared alignment section is the alignment as agreed — transfer it
in full, not summarized. A fresh agent resuming from this document will
have no other source for the operating model. The document is
self-contained: anyone reading it cold can reconstruct the full protocol
state without access to the conversation that produced it.

Update the document in place. It always reflects
current state. Every aspect is mutable: the user may pause execution at
any point to revise the objective, scope, facets, alignment, or map.

### Intent calibration log

The log is organized by the facets — each facet has its own section,
and entries accumulate under the relevant facet. Workflow-level
preferences (region sequencing, presentation format) go in a General
section.

Always log when the user disagrees with or modifies your
recommendation. Agreements may also be logged when they establish a
pattern useful for future autonomy.

For each entry, describe the specific finding you raised and the user's
response. Err on the side of detail: a fresh agent reading the log
should be able to see exactly what was asked, what the user decided, and
why that decision is evidence for future autonomy on that facet.

The log refines the shared alignment. A fresh agent reading the log
reconstructs the alignment without access to the conversation that
produced it.

### Scratchpad

The last section of the protocol state document is the user's
scratchpad — a place for observations, ideas, and open questions that
arise during the work. Write entries when the user asks you to. Do not
interpret scratchpad content as direction, do not act on it, and do not
incorporate it into the alignment or the map. It is the user's private
notepad; you are the scribe.

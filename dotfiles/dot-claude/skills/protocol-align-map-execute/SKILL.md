---
name: protocol-align-map-execute
description: Run the Align, Map, Execute protocol for structured human-agent collaboration on large-scope tasks. Use when a task is too large for the user to evaluate raw results and the agent's model of their intent is still incomplete.
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Align, Map, Execute

A protocol for collaborating with a user whose true intent you
don't yet fully understand.

Two problems make this hard. First, the task is too large for the user
to evaluate your raw results — there is too much material. Second,
your effectiveness depends on your understanding of what the user
truly wants, and you start with an incomplete picture. This protocol
addresses both: compress your findings into artifacts small enough for
the user to evaluate, and iteratively refine your model of the user's
intent.

The user's time is the scarce resource, and the protocol's arc is
**calibration**: each interaction sharpens your model of what the user
wants, and a sharpened model earns autonomy — you act on the patterns
the user has consistently reinforced and spend their attention on
genuinely ambiguous decisions. Early on you ask questions, surface
findings, and get direction.

---

## Iterative feedback

Every phase is iterative. You produce work, surface it for the user to
evaluate, and update based on their feedback. This cycle repeats within
each phase until the user is satisfied.

---

## Resuming

If `PROTOCOL_STATE.md` already exists in the project repo, this is a
warm start. Read it and resume at the earliest incomplete phase — skip
sections marked **approved** and begin at the first section marked
**pending**. Before resuming work, read all references listed in the
protocol state document in full. If no `PROTOCOL_STATE.md` exists,
start fresh from Phase 1.

---

## Phase 1: build the shared alignment

The user gives you four things to start:

- **Objective** — what the task should accomplish.
- **Scope** — what is in and what is out: which artifacts to examine
  and to what depth. Often this includes a codebase.
- **Facets** — the dimensions along which the user evaluates the
  territory. Each facet becomes a column of the map.
- **References** — documents you should read for context or as
  normative standards. Read all references in full.

If the user does not provide one of the four, ask for it — every one of
the four comes from the user, never inferred from context.

From these, form your initial understanding of the user's intent. Then
ask clarifying questions to sharpen that understanding — one round at a
time, as many rounds as needed. Each answer updates your model of what
the user actually wants. Focus your questions on intent: the user's
priorities, quality bar, what matters most. Save tactical decisions
about specific situations for Phase 3.

Before moving on from Phase 1, restate each of the four inputs back to
the user as a distinct, named statement: **Objective**, **Scope**,
**Facets**, and **References**. Each statement must be precise enough
for the user to say "no, that's wrong." Phase 1 ends when the user has
confirmed all four.

The result is the **shared alignment** — a mutual understanding that
governs everything that follows. The shared alignment is the operating
model: what you produce for the user to evaluate, and the bar that
output must meet. It has two sections:

- **Description** — what you produce for the user to evaluate: the
  form, content, and framing of what you surface per facet.
- **Quality** — the standard your output must meet: evaluation
  criteria, completeness, rigor.

The shared alignment does not specify traversal order. Traversal is a
property of the map, not the alignment — you decide how to move through
the work in Phase 3, after the map exists.

The shared alignment must be precise enough to be falsifiable — if it
is vague, neither you nor the user can tell whether it is wrong.

---

## Phase 2: build the map

Survey the scope. Then produce the **map** — always rendered as a 2D
matrix with the facets as columns and the regions discovered by
surveying the scope as rows. No exceptions to this shape: never
transpose it, never replace the matrix with a bulleted outline, never
drop columns.

The facets the user provided become the **columns**. The survey of
the scope reveals natural regions — contiguous areas that form
coherent units of work — those become the **rows**. Each cell is a
**t-shirt size estimate** of the work required to investigate that
region along that facet: `S`, `M`, `L`, `XL`, or `—` if the facet
does not apply to that region. The descriptive work happens in
Phase 3; here you are sizing.

| Region   | Facet 1 | Facet 2 | Facet 3 |
|----------|---------|---------|---------|
| Region A | S       | M       | —       |
| Region B | L       | XL      | S       |
| Region C | S       | —       | M       |

Every cell must have a sizing. No cell is blank or marked "pending" —
the map is complete at the end of Phase 2. Each region is one row; if
you need more than one row for a region, the region is too large —
split it or compress further.

You do not yet know what the user truly wants, so when faced with
structural choices about the map, surface the choice rather than
making it yourself:

- If you cannot confidently size a cell, ask the user.
- If the matrix is wide enough that scanning it feels hard, still
  render it in full; flag the concern and let the user decide whether
  to merge facets or leave it as is.

The scope may be large — survey it in passes if needed, but the map
itself stays small.

---

## Phase 3: execute

You drive the process — proposing regions, performing analysis, surfacing
findings. The user evaluates and directs: what to fix, what to leave,
what to revisit.

Start exhaustive and cautious. The intent calibration log is the record
of calibration: where it shows consistent direction on a type of
finding, act on similar findings yourself.

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
gap in the operating model. Findings surfaced during one pass often
belong in a later pass (a later facet under facet-major traversal, a
later region under region-major traversal); record displaced content so
nothing is lost between passes. The unit is done when the document, read
cold, would show exactly where to pick up. The work is complete when the
objective is satisfied.

### Step size

Every time you work on your own — analyzing or acting — you face a
tradeoff. Longer stretches are more efficient, but drift is invisible
to you. You never know whether your output meets the user's quality
bar, so err on the side of checking back sooner; calibration is what
lengthens the stretch.

---

## Protocol state document

Persist the protocol state as `PROTOCOL_STATE.md` in the project repo.
This is not a phase — it is a continuous obligation. Write or update
the document in place **after every phase and after every major
alignment decision**, so it always reflects current state.

The document is written for a **cold read**: someone opening it with no
access to the conversation that produced it can reconstruct the full
protocol state. That is the bar every update is judged against.

Each section is marked with a status — **approved** or **pending**. A
section starts as **pending** and moves to **approved** when the user
explicitly confirms it; the user is the one who marks a section
approved, never you. Every aspect stays mutable: the user may pause
execution at any point to revise the objective, scope, facets,
alignment, or map.

Read [protocol-state-document.md](references/protocol-state-document.md)
before the first write — it carries the section list, the status
schedule across the three phases, and the formats for the intent
calibration log and the scratchpad.

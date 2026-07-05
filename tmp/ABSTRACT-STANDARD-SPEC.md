# Abstract Standard Spec

Design output of the 2026-07-05 ideation session. Nothing here is
implemented yet; this document is the complete input to that future build.

## Motivation

Without this, returning to a topic months later means describing "build
standards" loosely and re-deriving shared understanding over several turns.
Instead: each standard gets a small fixed-format OKF object that tells a
human or agent where to look. The object does **not** define the standard —
the files it points at do that. It aggregates pointers so a thought that
originates at the abstract level ("how do we do X here?") resolves to
concrete files in one hop.

## What a standard is — and is not

- **Named by the question it governs, not the current answer.** "How to
  organize knowledge in markdown" is the standard; the OKF spec is today's
  answer, pointed at by its define cell. Litmus: if the implementation could
  be swapped while the name stays true, it is a standard.
- **Mechanisms are not standards.** Judgments and datasheet are purpose-built
  abstractions with tooling and rules — akin to a pandas DataFrame. They are
  what standard cells point *at*, never standards themselves.
- **Thinness principle.** Objects may be extremely lightweight pass-throughs.
  Skill authoring can be literally two pointers (conventions doc + audit
  tool). These are not complex objects.
- **Membership is non-exclusive.** A file or pointer may belong to more than
  one standard at once. Standards are overlapping views, not a partition.
- **Nesting: one level.** Standard → sub-standard (coding → python). The
  parent holds what is shared; the child holds specifics. A repo may adopt a
  child without its siblings. Resist deeper nesting until a real case forces
  it.

## Object form

- One flat OKF markdown file per standard; the files live in a directory
  carrying an `index.md` catalog that lists every standard with its
  one-liner. (Exact placement relative to the existing `standards/` contents
  is decided at build time.)
- Four fixed, mandatory cells — simple one-word verbs. An empty cell says an
  explicit "none" so gaps stay visible and nameable:
  - **define** — the contract: prose docs plus canonical reference bytes.
  - **audit** — read-only deviation detection (linters, repo-audit).
  - **enforce** — blocking gates (pre-commit hooks, `make check`, CI).
  - **adopt** — standard-specific helpers that bring a repo into
    conformance (templates, migration procedures). The generic path — an
    agent reads define and fixes the repo — needs no pointer, so "none" is
    the common value. The cell exists because real adopt artifacts already
    do: the greenfield-CLI template, and the enforcement-last sequencing
    lesson (audit stays advisory until findings hit zero, then the gate is
    wired).

Thin-object sketch:

```markdown
# Standard: skill authoring

How we author agent skills.

## Define
- <skill conventions doc> — the contract

## Audit
- scripts/internal-skill-audit — deterministic linter

## Enforce
- pre-commit hook `internal-skill-audit`

## Adopt
- none
```

## Initial catalog — nine standards, list closed

1. **Build** — this branch's PR. define: `standards/build/*.md` +
   `standards/canonical/`; audit: `scripts/repo-audit`; enforce: pre-commit
   + `make check` + CI; adopt: greenfield-CLI template.
2. **Knowledge organization in markdown** — define points at the OKF spec.
3. **Semantic validation & drift detection** — how we check things grounded
   in language rather than deterministically code-checkable, and how we
   detect when previously validated meaning drifts. Points at the judgments
   mechanism (its content-addressed cache *is* the drift detector: bytes
   change → verdict expires → re-judge), one of possibly many instruments.
4. **Skill authoring** — SKILL.md conventions + internal-skill-audit.
5. **Distillation** (name TBD) — ways we distill and approximate complex
   systems into parsimonious, low-dimensional, human-legible objects.
   Rationale: the agent–human bandwidth asymmetry — Claude absorbs thousands
   of files instantly; the human interface needs accurate,
   pseudo-comprehensive, at-a-glance artifacts. Datasheet is the first
   instrument of this standard; more will exist.
6. **English writing style.**
7. **Coding style** — sub-standards: python (style docs already exist in
   this repo), shell, SQL, …
8. **Git/PR conventions.**
9. **Agentic coding workflow** — how agentic work runs, intake to merge.
   Raw material already exists: the `workflow/` state machine,
   harness-recipes (e.g. ralph-loop), the agentic-box standard.

Explicitly not ruled a standard: agent-context docs (CLAUDE.md /
CONTEXT.md).

## Drift — two tiers

1. **Fine grain:** a specific sentence, paragraph, or document must keep
   meaning a certain thing → a judgment. Already in motion; expect many.
2. **Contract grain:** a define-cell change triggers repo-wide rework
   (e.g. a python convention change touching every `.py` file) → version
   bump + sweep.

## Applicability

Auto-detect, in the style of repo-audit's layer detection (`.py` files
present → python standard applies). No repo-side adoption manifest. Agents
do not wander into repos deciding what applies — they are sent, and
applicability is resolved at dispatch time.

## Coverage lint

Every doc in the OKF graph must be connected to at least one standard
object (directly or transitively through its pointers). An orphan doc is,
by definition, a non-standard standardization document — a contradiction
the lint surfaces. This is the meta-level analogue of index-staleness in
okf-lint.

## Self-hosting

The meta-standard dogfoods: it is itself an instance of the object it
defines. Pointer integrity is guarded by ref-check; semantic honesty is
guarded by one judgment per object ("these pointers really do define,
audit, and enforce this standard").

## Deferred

- Directory placement of the object files vs. existing `standards/`
  contents.
- In-file representation of sub-standards.
- A proper name for the distillation standard.
- Rename `standards/python-conventions.md` → `python-style.md` (minor,
  pre-dates this session).

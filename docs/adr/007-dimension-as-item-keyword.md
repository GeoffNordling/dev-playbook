# ADR-007: Dimension as item-level keyword, not section header

**Date:** 2026-04-23
**Status:** Accepted

## Context

[ADR-005](005-design-dimensions-and-verification-fields.md) introduced the four design dimensions (Data, API Shape, Algorithms, Composition) and organized `dsn` spec files around four mandatory `##` section headers in canonical order. Each `dsn` item was placed under exactly one header. Files with no items in a given dimension still carried the empty header as an explicit "considered, nothing to commit here" signal.

Preparing for the greenfield `spec-tools` rewrite (issue #16) surfaced friction with that choice.

**Inconsistency with peer workspace extensions.** The workspace adds three pieces of metadata to `dsn` items beyond OFT's native keywords: `Interface:`, `AgentReview:`, and dimension classification. Two of the three live with the item as keyword fields. Dimension is the odd one out — it's expressed through surrounding Markdown structure rather than an item-level attribute. The asymmetry is unmotivated; dimension is metadata about the commitment, same as the others.

**Multi-dimensional commitments can't be expressed.** Some decisions genuinely commit across two dimensions — a schema choice that also pins a return signature commits both Data and API Shape; an algorithm that also fixes an ordering contract commits both Algorithms and Composition. The section-header rule forces each `dsn` into exactly one header. ADR-005 resolved this by saying items that genuinely span dimensions are "candidates for being split." That's a workaround for a representation that can't hold the idea — split items lose the unity of a single commitment.

**Section headers conflict with other file-organization axes.** A `dsn` file may want to organize by feature, subsystem, or capability area rather than by dimension. Under the current rule, either (a) the file repeats the four headers under each feature subsection, or (b) feature-organized content fights the dimension-organized structure. Splitting `design.md` into `design/` by feature inherits the conflict — each feature file needs its own four dimension headers, most of them empty. The boilerplate grows with the split, not shrinks.

**Empty headers are boilerplate the tools don't need.** The "empty header is a deliberate signal" framing reads well in isolation, but most projects never commit in all four dimensions, and every file ends up with two or three empty headers. The signal is diluted by its frequency. Per-dimension projection tools can render an empty group on their own when no items name a dimension — that signal doesn't need to live in the source files.

## Decision

### `Dimension:` is a workspace extension keyword

`Dimension:` joins `Interface:` and `AgentReview:` as a workspace extension keyword, valid only on `dsn` items. Every `dsn` `SHALL` carry a `Dimension:` field.

The field value is a comma-separated list of dimension names from the fixed set `{Data, API Shape, Algorithms, Composition}`:

    Dimension: Data
    Dimension: API Shape, Algorithms

Dimension names are spelled exactly as in [design-layer.md](../../sdd-standards/design-layer.md) — two-word names (`API Shape`) use a single space; case is preserved. A name outside the fixed set is invalid. Empty lists and repeated names within one field are invalid.

### Many allowed, one typical

Most items name a single dimension. A comma-separated list expresses decisions that genuinely commit across dimensions — the representation admits what's real rather than forcing a split the commitment does not support. Items that span three or more dimensions remain candidates for splitting; one commitment typically has one primary axis.

### Section headers are no longer required

The rule "every `dsn` file carries `## Data`, `## API Shape`, `## Algorithms`, `## Composition` in canonical order" from ADR-005 is removed. `dsn` files may organize items however is readable — by feature, by subsystem, by capability area, or by dimension if the author prefers. Section headers are free-form Markdown, same as in `feat` and `req` files.

### Projection moves from structure to content

Per-dimension projection scans `Dimension:` fields instead of tracking Markdown section context. An item with `Dimension: Data, API Shape` appears under both the Data and API Shape projections — the tool no longer loses information to the one-header-per-item constraint. A dimension that no item names renders as an empty group in tool output; the signal lives in the tool's output rather than as boilerplate in every file.

### Forced-classification property is preserved

ADR-005 justified section headers in part as a device for forcing classification at write time. That property is preserved in full: a `dsn` without a `Dimension:` field is a lint failure, the same way a `dsn` without a verification field is. The field is required; section headers were one way to express it, and not the only way.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep dimension section headers as in ADR-005 | Inconsistent with peer extensions, forces splits on multi-dimensional commitments, conflicts with feature-organized file layouts, creates empty-header boilerplate. |
| `Dimension:` field allows only one dimension per item | Reintroduces ADR-005's "candidate for splitting" workaround for genuinely multi-dimensional commitments. Many-allowed admits what's real; convention keeps most items single-dimensional. |
| Section headers optional; `Dimension:` field also optional | Removes the forced-classification property ADR-005 valued. A required `Dimension:` field keeps the property without the headers. |
| Section headers required plus `Dimension:` field | Double bookkeeping; the two representations drift. Pick one. |

## Consequences

- `sdd-standards/design-layer.md` replaces its "Dimension section organization" section with a "Dimension commitment" section describing the `Dimension:` field and the many-allowed rule. The keyword definition itself lives in `oft-format.md`.
- `sdd-standards/oft-format.md` Extensions section gains an "Extension keyword: `Dimension:`" subsection alongside `Interface:` and `AgentReview:`.
- `sdd-standards/spec-format.md` updates the `dsn` anatomy example to show a `Dimension:` field instead of a `## API Shape` header; the "What a valid file looks like" checklist drops the four-header bullet.
- `sdd-standards/tooling.md` updates `spec-lint`'s rule list (dimension-section rule is gone; `Dimension:` well-formedness and presence replace it), updates `sdd-index` / `sdd-atlas` descriptions to describe grouping from the `Dimension:` field, and updates the rule-to-tool crosswalk.
- `sdd-standards/README.md` updates the `design-layer.md` and `oft-format.md` blurbs to reflect the keyword addition.
- `sdd-tools/README.md` notes that per-dimension projection reads the `Dimension:` field.
- `dotfiles/.claude/skills/sdd-review/SKILL.md` updates its per-record context description: the review agent receives the item's dimension(s) as prose, not a section location.
- ADR-005 is partially superseded: its "Dimension section organization" subsection is no longer in effect; its four dimensions, verification fields, compression tooling, and forced-classification principle remain.
- Existing `sdd-tools/src/` code and its tests no longer match the standard. Per issue #16, that code is reference-only pending the greenfield `spec-tools` rewrite; no changes to it are required here.

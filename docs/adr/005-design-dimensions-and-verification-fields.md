# ADR-005: Design Dimensions and Verification Fields

**Date:** 2026-04-21
**Status:** Draft — decisions below are settled; compression tooling is pending a follow-on discussion (see [Open](#open)).

## Context

[ADR-004](004-observable-to-tests-design-scope.md) established the observable-to-tests scope and the `Interface:` validator. Three gaps surfaced in practice.

**The design phase feels scattered.** ADR-004 listed five decision categories (API shape, algorithm, data schema, error semantics, data-structure choice) as examples inside Principle 1 of [design-layer.md](../../sdd-standards/design-layer.md). The list was never formalized into a section, never ordered, and two of the five categories overlap with others. During a design session, the author juggles multiple axes of thinking — what are the entities? what's the public surface? what are the operations? how do they combine? — with no explicit guidance on how to sequence them. The result is decision paralysis.

**Non-testable commitments have no place in the chain.** Some functional requirements cannot be deterministically tested. The clearest case is LLM behavior — e.g., "agent `SHALL NOT` attempt polite conversation for no reason." Prompt-inclusion tests are test-theater (they check the text of the prompt, not the behavior). Human review doesn't scale — the review never actually happens. OFT coverage chains fail on these requirements because no `utest` or `itest` covers them, and dropping them from the spec would lose the intent.

**The "Four Principles" framing doesn't carry its weight.** Each principle in `design-layer.md` is better served by a more specific home — a new section, an existing standard, or a skill. The grouping obscures more than it organizes.

## Decision

### Four decision dimensions

Design items commit decisions across exactly four dimensions. Previously implicit and informal, they are now defined as a top-level section of `design-layer.md`.

1. **Data** — the fundamental abstractions the system is built around. Entities, fields, relationships, containment, ownership. These abstractions exist in both the design spec and the implementation code; they are the nouns the system manipulates.
2. **API shape** — signatures of public callables, classes, and methods. What callers name, invoke, and receive.
3. **Algorithms** — the exact operations that produce outputs from inputs. Sum, fold, filter, derive. A system typically commits several.
4. **Composition** — how operations combine. Sequencing, dependency, data flow, fan-out, fan-in.

At the project level, any dimension `MAY` be null. A pure-data library may have no Algorithms or Composition; a single-function tool may have no Composition; a CLI wrapper may have thin Algorithms. Every individual `dsn`, however, `SHALL` commit to at least one dimension; a `dsn` with no dimensional commitment is not a design decision, it is narrative.

Consolidations from ADR-004's five-item list:

- **Error semantics** folds into API shape (raises are part of the contract) and Algorithms (failure paths).
- **Data-structure choice** folds into API shape when the signature pins it (e.g., `-> list[Event]`), or into the green agent's territory when the signature abstracts it (e.g., `-> Iterable[Event]`).
- **Module layout** (extend-vs-new) folds into API shape; the fully-qualified symbol path declared in `Interface:` encodes the placement.

Elevation: **Composition** is promoted from an implicit organizing axis (the existing skill already says to "order sections to follow the pipeline") to a first-class dimension. Two designs with identical Data, API shape, and Algorithms can still commit to different Compositions and produce different integration-test outcomes.

### Dimension section organization

Every `dsn` spec file `SHALL` organize its items under four markdown section headers, one per dimension, in this order:

    ## Data
    ## API Shape
    ## Algorithms
    ## Composition

Every `dsn` item `SHALL` appear under exactly one header. Items that float above or between sections are errors. When a file has no commitments for a given dimension, the header still appears with an empty body — the explicit signal "considered, nothing to commit here." A missing header is not equivalent to an empty one; the header makes the absence deliberate.

This markdown-header organization serves two purposes. First, it forces the author to classify each `dsn` into a dimension at the moment of writing, rather than inferring classification post-hoc from prose. Second, it enables per-dimension projection by downstream compression tools without requiring a separate `Dimension:` field on every item. A `Dimension:` field remains a fallback option if section-based projection proves insufficient in practice.

### Scope of a design item

A design item records a **commitment**. Within a dimension, a commitment is any decision whose chosen option some other part of the system — callers, tests, downstream code — will rely on. Decisions entirely inside a module's private boundary (internal helpers, file layout, local control flow) are not commitments; they belong to the green agent.

This reframes ADR-004's Principle 2 ("observable-to-tests scope") from a counterfactual ("would a test fail if flipped?") to a direct statement. The scope is the same; the phrasing is more natural to apply at design time.

### Three verification fields

A dsn `MAY` use any combination of the following fields to name how its commitment is verified:

| Field | Origin | Purpose | Verified by |
|---|---|---|---|
| `Needs: utest, itest` | OFT standard | Behavioral commitment | pytest run |
| `Interface:` | Workspace extension ([ADR-004](004-observable-to-tests-design-scope.md)) | Structural contract | Interface validator at pytest collection time |
| `AgentReview:` | Workspace extension (this ADR) | Non-test commitment | `sdd-review` skill on invocation |

`AgentReview:` is a new dsn-only field whose value is prose describing what must be checked. Example:

    AgentReview: The agent's system prompt at src/prompts/agent.md should contain a directive discouraging filler or polite conversation.

The prose is the instruction the review agent reads when `sdd-review` is invoked. File references inside the prose let the agent find what to compare against.

**Why a standalone field, not a `Needs:` value.** OFT's `Needs:` takes artifact types — persistent items that cover the chain. Agent reviews are ephemeral actions, so an `agent-review` artifact type doesn't fit. `Interface:` already set the precedent for workspace-specific dsn-only fields that carry verification info outside the OFT type system; `AgentReview:` follows the same pattern. OFT ignores unknown keywords as prose, so both extensions coexist cleanly with the standard.

### Single dsn, multiple fields

A single dsn records one design decision. That decision `MAY` commit multiple aspects simultaneously, verified through any combination of the three fields. Example:

    Needs: utest
    Interface: myapp.parser.Parser.parse(path: pathlib.Path) -> myapp.session.Session
    AgentReview: Log output from Parser.parse follows the human-readable format specified in docs/log-format.md.

Forcing separate dsn items per verification field would inflate the dsn count and artificially split closely related commitments.

### Verification coverage

Every `dsn` `SHALL` carry at least one verification field — one of `Needs:`, `Interface:`, or `AgentReview:`. A `dsn` with none of these names a commitment that nothing ever checks.

The rule is uniform across all `dsn` items. Items with `Needs:` are verified downstream by tests; items with `Interface:` are verified by the interface validator; items with `AgentReview:` are verified by the review skill. The rule does not distinguish chain leaves from interior nodes: a `dsn` that terminates its branch (no `Needs:`) is subject to the same rule as any other and must still carry `Interface:` or `AgentReview:`. "Leaf" remains descriptive vocabulary for an item with no `Needs:`, but it is not a special validation category.

Non-testable behavioral commitments terminate the chain with `AgentReview:` alone. Example:

    feat~agent~1
        ↑ Covers:
    req~agent.no-polite-conversation~1
        Agent SHALL NOT attempt polite conversation for no reason.
        Needs: dsn
        ↑ Covers:
    dsn~agent.no-polite-conversation~1
        Enforcement via system prompt directive.
        AgentReview: The agent's system prompt at src/prompts/agent.md should contain
                     a directive discouraging filler or polite conversation.

### Drop the "Four Principles" section

The four principles in `design-layer.md` are dissolved:

| Principle | Resolution |
|---|---|
| P1 — Single role | Redundant with the new Decision Dimensions section. Removed. |
| P2 — Observable-to-tests scope | Reframed as commitment-based scope and folded into Purpose in `design-layer.md`. |
| P3 — Commitment by naming | Specific to API shape; content relocated into the API shape dimension definition and the existing `Interface:` section of [writing.md](../../sdd-standards/writing.md). |
| P4 — Design-agent ownership of structure | Workflow guidance, not a standard. Relocated to [sdd-design/SKILL.md](../../dotfiles/.claude/skills/sdd-design/SKILL.md). |

### Revised structure of `design-layer.md`

`design-layer.md` is refactored to contain `dsn`-layer specifics only. Sections that apply across all layers are moved to `overview.md`, where they frame the workflow as a whole rather than the design layer specifically.

New `design-layer.md`:

1. Purpose (rewritten around commitment framing)
2. Decision Dimensions (new)
3. Dimension Section Organization (new)
4. Verification Fields (new — `Needs:`, `Interface:`, `AgentReview:`; combining; uniform rule)

Moved to `overview.md`:

- Coverage Chain (chain-wide rules, not `dsn`-specific)
- Revision Policy (applies to every layer)
- Forwarding (chain-adjacent)

The "Scope of a Design Item" framing from an earlier draft of this ADR is folded into Purpose, since the commitment-based definition is what makes a `dsn` a `dsn`.

### Tool and skill

A new tool and skill execute agent reviews on demand:

- **Tool** — `sdd-tools/src/sdd_tools/cli/review.py`, CLI entry `sdd-review`. Scans spec files for `AgentReview:` fields; emits structured records (dsn id, file:line, prose, referenced paths) for agent consumption.
- **Skill** — `dotfiles/.claude/skills/sdd-review/SKILL.md`. Iterates tool output and invokes the review agent per item, reporting stale or out-of-sync items.

This matches the sdd-tools mandate: deterministic extraction in the tool, judgment in the agent.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep five dimensions including error semantics and data-structure choice | Both fold into API shape + Algorithms. Keeping them separate adds axes without adding decision-making value. |
| Keep the "Four Principles" framing | Each principle is better served by a concrete section or relocated to skills. "Principles" suggests axioms; the content is rules and workflow. |
| Retain the counterfactual phrasing of the scope rule | The counterfactual ("would a test fail if flipped?") is awkward to apply at design time. Direct phrasing in terms of commitment is more natural. |
| Make `AgentReview` a `Needs:` value via a custom OFT artifact type | Artifact types describe persistent items with coverage records. Agent reviews are ephemeral actions. A custom artifact type here bends OFT semantics. |
| Tag vocabulary inside `AgentReview:` (construction, periodic-review, eval-harness) | For personal-scale work, only agent-review is a pragmatic non-test mechanism. Human reviews don't happen reliably, eval harnesses are infrastructure overhead we won't build, construction-check degenerates into prompt-inclusion test-theater. One mechanism; no tag taxonomy. |
| Alternate field names (`Verification:`, `Upheld:`, `Reviewed:`) | `Verification:` is formal and muddled with the test channel. `Upheld:` is abstract — doesn't name the mechanism. `Reviewed:` conflates with PR review. `AgentReview:` is explicit and unambiguous. |
| Require one dsn per verification field | Inflates dsn count without gaining clarity. One design decision may span multiple aspects; one dsn captures them. |
| Keep "Pipeline" as the dimension name | "Pipeline" implies linear data flow. "Composition" generalizes to any form of combining operations, including branching, fan-out, event-driven. |

## Consequences

- `sdd-standards/overview.md` gains Coverage Chain, Revision Policy, and Forwarding — sections that apply across all layers, previously housed in `design-layer.md`.
- `sdd-standards/design-layer.md` is rewritten around the new structure: Purpose, Decision Dimensions, Dimension Section Organization, Verification Fields. The "Four Principles" section is removed; Coverage Chain, Revision Policy, and Forwarding relocate to `overview.md`.
- `sdd-standards/writing.md` gains an `AgentReview:` entry in the keyword table and an AgentReview Declarations subsection parallel to Interface Declarations. The LaTeX math convention is dropped as a rendering preference, not a correctness rule.
- `sdd-standards/tooling.md` documents the new `sdd-review` CLI, expands `spec-lint`'s rule list (AgentReview well-formedness, dimension section organization, per-dsn verification-field presence), adds a rule-to-tool crosswalk, and removes `spec-privacy` (test privacy is a testing-conventions concern, out of SDD scope; the module will migrate out of `sdd-tools/` in a follow-on refactor).
- `sdd-standards/README.md` blurbs are updated to reflect the new content boundaries.
- `dotfiles/.claude/skills/sdd-design/SKILL.md` is updated to reference the four dimensions, the commitment-based scope rule, the dimension section organization, and the three verification fields. (Deferred until the compression tooling is in place — see [Open](#open).)
- New tool: `sdd-tools/src/sdd_tools/cli/review.py` (`sdd-review`) scans `AgentReview:` fields.
- New skill: `dotfiles/.claude/skills/sdd-review/SKILL.md` invokes the review agent per `AgentReview:` item.
- `spec-lint` gains rules for dimension section organization, `AgentReview:` well-formedness, and verification-field presence on every `dsn`. No separate leaf validator is needed — the uniform verification-field rule subsumes the former "leaf dsn" case.
- ADR-004 is partially superseded: its scope rule (Principle 2) is reframed; its five-dimension list is consolidated to four. The `Interface:` machinery and observable-to-tests premise remain.

## Open

**Compression tooling for the dsn wall-of-markdown problem.** A dsn collection of 30+ items exceeds the human context window. The design agent produces them; the human needs tools that project the collection onto one dimension at a time — e.g., a Data-only view, an API-shape-only view. `sdd-chain` today is tuned for feat→req→dsn narrative walks, not for design-phase consumption.

This ADR will be completed by a follow-on decision on the compression views — what views exist, what each answers, what the CLI surface looks like. The dimension framing above sets up the vocabulary the views will use; without the views, the dimensions remain useful for thinking but do not scale past a dozen dsn items.

Next step: separate focused discussion on compression tooling; update this ADR's Decision and Consequences sections with the outcome; move Status from Draft to Accepted; integrate the complete ADR into the standards.

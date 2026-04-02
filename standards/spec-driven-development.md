# Meta Spec: A Spec For Spec-Driven Development with Agentic Coding Tools

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, and `OPTIONAL` in this document are to be interpreted as described in RFC 2119.

### Vocabulary Conventions

This document and all specs produced under it adopt the following conventions for consistency:

- `SHALL` is used for all absolute requirements. MUST and REQUIRED are equivalent per RFC 2119 but are not used here.
- `SHALL NOT` is used for all absolute prohibitions. MUST NOT is equivalent but not used here.
- `SHOULD` is used for strong preferences. RECOMMENDED is equivalent but not used here.
- `SHOULD NOT` is used for strong preferences against. NOT RECOMMENDED is equivalent but not used here.
- `MAY` is used for optional behavior. OPTIONAL is equivalent but not used here.

---

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)
- Various articles, blog posts, and community discussions on spec-driven development with Claude Code (2025–2026)

---

## Core Principles

**Write the spec before writing code.** Every decision you skip in a spec gets made anyway — just later, under worse conditions, mid-build or post-ship. Front-loading decisions is always cheaper.

**Only write a spec when there are hard decisions to document.** If a spec would just be an implementation manual with no genuine choices in it, there was nothing worth writing. The spec earns its existence by capturing difficult decisions — options considered, trade-offs weighed, and the choice made. If there were no hard decisions, skip the doc.

**The spec `SHALL` explicitly state what NOT to build.** Scope exclusions are as important as requirements. Without them, the agent makes reasonable assumptions that turn out wrong. An explicit out-of-scope section prevents the agent from building things you didn't ask for.

**The spec is a living document.** It `SHALL` stay in sync with what the system actually does as development proceeds. Stale specs are a maintenance failure, not an inherent property of specs. Changes to behavior `SHOULD` include a corresponding spec update in the same commit or pull request.

**Functional before design.** Decide what the system does before deciding how it's structured. A functional spec is always written first. A design spec is written after behavior is settled, defining the components, interfaces, and data structures that the red/green agents will implement against.

**Humans `SHALL NOT` write tasks.** Deriving and managing implementation tasks is the agent's job. The human only ever edits the spec. The agent creates, tracks, and completes its own tasks from the spec. Writing tasks manually reduces the human to a project manager for the LLM and defeats the purpose of agentic development.

**Plans are ephemeral; specs are durable.** Claude Code's plan mode is a thinking tool — plans are intentionally not version controlled and are disposable once used. The spec in Git is the durable source of truth. These are distinct artifacts and `SHALL NOT` be conflated.

**Deviations from the spec `SHALL` be documented before merging.** When implementation diverges from the spec, the deviation is captured and the spec is updated to reflect what was actually built. The spec always describes reality, not intent.

### The Three Levels of Spec-Driven Development

These levels represent a progression of maturity. Each builds on the previous.

| Level | Definition |
|---|---|
| **Spec-First** | The spec is written before any code. Implementation follows the spec. |
| **Spec-Anchored** | The spec remains alive and current throughout the project lifecycle. It is updated as the system evolves. |
| **Spec-as-Source** | The spec is the only artifact the human authors. The human never edits code directly — all code is generated from the spec. This is the most aspirational level and the target practice. |

---

## When Spec-Driven Development is Overkill

SDD is not always warranted. Apply the same hard-decisions test: if there is nothing difficult to decide and document, the overhead is not justified.

SDD is appropriate for: large refactors touching many files, migrations, features with unclear or evolving requirements.

SDD is overkill for: single-file changes, simple well-defined bug fixes, trivially small features with no real decisions to make.

---

## Spec Files and Structure

All spec files `SHALL` live in a `/specs` folder inside the Git repository, versioned alongside the code.

Each spec file below starts as a single file. When a spec file grows large enough to impair the agent's ability to work with it in a single context load, it `SHOULD` be split into a folder of files organized by topic — typically one per feature or major system concern. The decision to split `SHALL` be made by the human, not the agent. When split, the folder `SHALL` contain an `index.md` that serves as a context map for the agent, listing every file with a one-line scope description so the agent can decide which files to load without reading all of them.

### Required Files

#### `/specs/functional_requirements.md`
Defines what the system does, written in EARS notation (see below) with RFC 2119 modal verbs. This is the functional spec. It is always written and always kept current.

Requirements `SHALL` be organized hierarchically using markdown sections and subsections, grouping related requirements together. For example:

```markdown
## Authentication

### Login
- When the user submits credentials, the system `SHALL` validate them against the store.

### Session Management
- While a session is active, the system `SHALL` refresh the token every 30 minutes.
```

When split, functional requirements live in `/specs/functional_requirements/`.

### Optional Files

#### `/docs/adr/`
Architecture Decision Records — the established professional convention for documenting significant architectural decisions. Each ADR is a short markdown file capturing one decision: its context, the options considered, the choice made, and the rationale. ADRs are immutable once written; superseded decisions get a new ADR rather than an edit. Useful as context for future work — an agent can be pointed to specific ADRs to understand prior decisions without searching the entire codebase. The directory `SHOULD` contain a `README.md` that indexes all ADRs with a one-line summary of each decision.

#### `/specs/design.md`
The system design spec. It defines the system's components, their responsibilities, their interfaces, and how data flows between them. It is the bridge between what the system does (functional spec) and how the code is organized (implementation). It is written proactively as a design phase before implementation begins, not retroactively as documentation of accumulated decisions.

Like the functional spec, the design spec is a **living document**. It stays in sync with the system as implementation proceeds. When the green agent discovers that an interface needs to change, the design spec is updated to reflect what was actually built.

This document uses the same RFC 2119 modal verbs as the functional requirements, but its subject matter is different. Functional requirements describe behavior ("the system `SHALL` produce segments sorted by timestamp"). The design spec names the parts and wires them together ("SessionParser `SHALL` accept a Path and return a list of TranscriptEntry objects; each TranscriptEntry `SHALL` carry these fields: ...").

A design spec earns its existence when the functional requirements describe behavior complex enough that a red/green agent pair cannot derive the module structure, class names, data structures, and interfaces without making design decisions. If the functional spec directly implies the implementation (one module, obvious data structures, no interface choices), the design spec may be skipped. For new features with multiple components, it `SHOULD` be written.

The design spec sets the overall approach and names the parts. It is not an implementation manual. It `SHOULD` include:

- **Design philosophy**: the broad structural approach (e.g., "the system `SHALL` follow object-oriented design with SOLID principles"; "the system `SHALL` use a pipeline architecture")
- **Components and responsibilities**: what modules or classes exist and what each one does (e.g., "SessionFinder `SHALL` locate all JSONL session files under a given root path")
- **Key data structures**: the important types and their fields, at the level of detail needed for a red agent to write tests against them
- **Data flow**: the pipeline from input to output, showing which component hands off to which

It `SHOULD` reference relevant ADRs for the reasoning behind individual decisions rather than re-explaining them.

### Requirement Traceability

Every requirement ID from the functional spec `SHALL` appear at least once in the design spec, attached to the component or data structure responsible for satisfying it. This ensures that every functional requirement has been translated into a concrete piece of the design. A single component may reference many requirement IDs; the constraint is only that no ID is left unaccounted for.

Use inline references (e.g., "SessionFinder `SHALL` scan `~/.claude/projects/` for session files (REQ-DISC-001)") to bind requirement IDs to the design elements that own them. The `sdd-trace` tool verifies this coverage.

When split, design specs live in `/specs/design/`.

---

## Writing Requirements — EARS + RFC 2119

Requirements `SHALL` be written using EARS (Easy Approach to Requirements Syntax) sentence templates combined with RFC 2119 modal verbs. EARS provides the sentence structure; RFC 2119 provides the strength of obligation.

### EARS Sentence Templates

| Type | Pattern |
|---|---|
| **Ubiquitous** | The [system] `SHALL` [action] |
| **Event-driven** | When [trigger], the [system] `SHALL` [action] |
| **State-driven** | While [state], the [system] `SHALL` [action] |
| **Optional feature** | Where [feature included], the [system] `SHALL` [action] |
| **Unwanted behavior** | If [condition], then the [system] `SHALL` [action] |

### RFC 2119 Obligation Levels

Substitute the modal verb in any EARS sentence to grade the requirement:

| Verb | Meaning | Agent treatment | Mandatory |
|---|---|---|---|
| `SHALL` | Absolute requirement | Blocking acceptance criterion | Yes |
| `SHALL NOT` | Absolute prohibition | Blocking acceptance criterion | Yes |
| `SHOULD` | Strong preference; deviation requires justification | Quality target | No |
| `SHOULD NOT` | Strong preference against; deviation requires justification | Quality target | No |
| `MAY` | Truly optional | Nice to have | No |

### Requirement IDs

Every requirement `SHALL` have a unique, stable identifier using the format `REQ-{AREA}-{NNN}`, where `{AREA}` is 3–6 uppercase letters identifying the requirement's domain (e.g., `AUTH`, `ERR`, `PARSE`) and `{NNN}` is a zero-padded three-digit sequence number. IDs `SHALL NOT` be reused, even if a requirement is removed.

### Deterministic Formatting

Functional specs serve two audiences: humans who read them and tools that parse them. The formatting rules in this section ensure that every spec is deterministically machine-parseable with zero ambiguity. Every requirement `SHALL` be locatable by its definition site, and its obligation level `SHALL` be extractable by pattern matching alone — no heuristics, no natural language interpretation. The `sdd-trace` tool relies on these conventions to verify traceability across specs and tests.

#### Definition Sites

A **definition site** introduces a requirement. It uses bold formatting on the ID, followed by a colon, then the requirement text:

```markdown
- **REQ-AUTH-001**: When the user submits a form, the system `SHALL` validate all fields.
```

The definition site marks the start of a requirement's text block. The text block extends until the next definition site, markdown heading (any level), or horizontal rule (`---`).

#### Reference Sites

A **reference site** mentions an existing requirement without defining it. References use the bare ID, never bold+colon:

```markdown
...error handling requirements (REQ-ERR-004) apply only to...
```

Reference sites are not parsed for obligation level.

#### Obligation Keywords

Each requirement `SHALL` contain exactly one obligation keyword from the RFC 2119 table above, wrapped in backticks (e.g., `` `SHALL` ``, `` `MAY` ``). The backtick-wrapped keyword is the obligation declaration for the entire requirement.

All uppercase obligation verbs `SHALL` be wrapped in backticks wherever they appear — in requirements, prose, and section introductions. This is a universal formatting rule with no exceptions.

#### One Obligation Level Per Requirement

A requirement `SHALL NOT` mix obligation levels. If a multi-sentence requirement contains behavior at a different obligation level, that behavior `SHALL` be split into its own requirement with its own ID. Repeating the same keyword within a requirement is permitted.

### Other Conventions

Specs `SHALL` use LaTeX math notation (e.g., `$k$`, `$N-1$`) when referring to variables, quantities, or mathematical relationships. This distinguishes formal variables from prose and renders correctly in markdown environments.

### Examples
- **REQ-AUTH-001**: When the user submits a form, the system `SHALL` validate all fields before submission. — mandatory
- **REQ-AUTH-002**: When validation fails, the system `SHOULD` highlight the offending field in red. — non-mandatory (quality target)
- **REQ-UX-001**: When the user is idle, the system `MAY` display a contextual tooltip. — non-mandatory (optional)

### Illustrative Examples

A spec section that introduces non-trivial domain vocabulary `SHOULD` include a short illustrative example before the formal requirements. The example grounds the vocabulary so that requirements can reference terms without re-explaining them.

An illustrative example is a disambiguation tool, not a test case. It shows one concrete scenario that exercises the key concepts of the section — what the nouns look like in practice, how they relate to each other, and where the boundaries are. It `SHOULD` be followed by a sentence calling out what the example demonstrates, so the reader knows which details are load-bearing and which are incidental.

Guidelines:

- Keep it to one scenario per section. If a second example is needed, the section's vocabulary may be too overloaded and `SHOULD` be split.
- Place the example after the section's prose introduction and before the formal requirements. The example bridges the two: prose sets up the concepts, the example makes them concrete, and the requirements formalize them.
- Use a fenced code block or structured format that mirrors what the system actually produces or consumes. Invented notation that doesn't match real artifacts creates more ambiguity than it resolves.

---

## Machine-Readable Contracts

Where appropriate, natural language requirements `SHOULD` be paired with machine-readable contracts (OpenAPI specs, JSON Schema) to formally constrain agent behavior. These are especially useful for API boundaries and data structures where ambiguity could cause silent regressions.

---

## The Spec as a Recovery Point

When a session derails, context gets polluted, or an agent goes off track, the recovery procedure is:

1. Open a new session
2. Load the spec explicitly into context (e.g. `@specs/functional_requirements.md`)
3. Paste the error or describe the problem
4. Continue from the spec

This is only possible if the spec is in Git and current. A stale spec cannot serve as a recovery point. This is a concrete operational reason why the living document principle is non-negotiable.



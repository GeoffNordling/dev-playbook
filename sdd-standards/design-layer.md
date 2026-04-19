# Design Layer

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in [writing.md](writing.md).

## Purpose

Functional requirements describe behavior. Design items record the decisions that shape the code fulfilling that behavior. A functional spec is written first; design items follow once the behavior is settled.

A design item can commit to any of the decisions a design makes: the public API surface, the algorithm, the data schema, the error semantics, the data structure. API shape is one kind of decision, and is often the only decision a given dsn records.

## Four Principles

### 1. Single role

Every design item records a design decision. API shape, algorithm, data schema, error semantics, and data-structure choice are equal kinds of decision. A dsn whose only decision is the shape of a public callable is as complete as one that commits to several choices together.

### 2. Observable-to-tests scope

A design item commits to a decision when a test could fail on it if the decision were changed. Structural choices below the public surface — private helpers, internal delegation, non-public module layout — belong to the code and are written by the green agent.

The question to ask at every fork is: *Can I write a test that fails if this decision flips?* When the answer is yes, the decision belongs in a dsn. When the answer is no, the decision belongs to the green agent.

### 3. Commitment by naming

When a dsn names a public surface, the shape of what it names is the commitment. Naming `parse_session(path: Path) -> Session` commits the public surface to a module-level callable with that signature. Naming `Parser.parse(path: Path) -> Session` commits the public surface to a class with that method. The `Interface:` keyword (see [Interface Declarations](writing.md#interface-declarations)) carries the committed signature in a form the validator checks against code.

### 4. Design-agent ownership of structure

The design agent performs brownfield reconnaissance — reading the existing code, choosing whether new functionality extends an existing class or introduces a new one, selecting the public surface — before writing any dsn. The output is dsn items plus interface stubs (`raise NotImplementedError` bodies) that the red agent tests against and the green agent fills in. The reasoning behind structural choices lives in each dsn's `Rationale:` field. Red-first workflow stays.

## When to write a design item

Every design item commits to at least one decision the functional requirement leaves open — the shape of a public surface, an algorithm, a schema, an error contract, or another choice a test could observe. Most functional requirements have a corresponding design item; cases where a `req` skips the design layer entirely are rare.

## Coverage Chain

OFT enforces a directed graph of coverage. Each item declares what must cover it downstream (`Needs:`), and each downstream item declares what it covers upstream (`Covers:`). OFT walks this graph and fails if any required link is absent.

The standard layers, from upstream to downstream:

```
feat  →  req  →  dsn  →  utest / itest
```

Each arrow represents a coverage relationship: the downstream layer covers the upstream layer. Every item declares which downstream types must cover it (`Needs:`) and which upstream items it satisfies (`Covers:`).

**Which layers are required depends on the project and the item:**

- `feat` is required. Every project `SHALL` begin the chain at `feat`.
- `dsn` is expected for most `req` items. In rare cases where a `req` item needs neither a design decision nor an ownership assignment, it `MAY` declare `Needs: utest` or `Needs: itest` directly, skipping `dsn`.
- Each item's `Needs:` declaration `SHALL` list whichever test types are appropriate to verify it. A `req` item may need `utest`, `itest`, or both. A `dsn` item may need `utest`, `itest`, or both.

A **terminating item** has no `Needs:` declaration. OFT treats it as a leaf — nothing downstream is required.

OFT fails the trace when:
- Any item's `Needs:` types are not all covered by at least one item of each required type
- A `Covers:` link references an ID that does not exist at that revision
- Any item is orphaned (has `Covers:` pointing to a nonexistent item)

## Revision Policy

The revision number is a semantic version for the item's meaning.

**Increment** the revision when the semantic content changes — when the requirement means something different than it did before. This immediately breaks all downstream `Covers:` links that referenced the previous revision, forcing downstream documents to explicitly acknowledge and respond to the change.

**Do not increment** for typo fixes, rephrasing that does not change meaning, or formatting changes.

When you increment a revision, update all `Covers:` references in downstream documents to the new revision. If a downstream item's response to the change is "no change needed," update the `Covers:` link and note this in the `Comment:` field.

## Forwarding

OFT supports a forwarding syntax that lets a document layer acknowledge a requirement and pass coverage responsibility downstream without creating a full spec item:

```markdown
arch --> dsn : req~auth.login-validation~1
```

**Do not use forwarding in this workspace.** When a layer has nothing to say for a particular item, the item `SHALL` skip that layer entirely (by omitting the type from its `Needs:`) rather than creating a hollow passthrough. Forwarding is documented here so you recognize it if you encounter it in the OFT documentation.

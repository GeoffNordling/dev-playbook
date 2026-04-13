# Design Layer

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in [writing.md](writing.md).

## Why the Design Layer Exists

**Functional before design.** Decide what the system does before deciding how it's structured. A functional spec is always written first. A design spec is written after behavior is settled.

**The design layer's primary role is to name the interfaces that tests target.** Each design item connects a functional requirement to the specific code (module, class, function) that fulfills it. The red agent writes tests against that interface; the green agent implements it. Without this layer, the red agent has no target — the functional requirement says what the system does, but not where the code lives or what the public API looks like.

**The design layer's secondary role is to document design decisions** — algorithm choice, data structure, component boundary, error handling strategy — when those decisions exist. Most design items do both; some only do one.

## What Qualifies a Design Item

**Every design item `SHALL` earn its place.** A design item earns its place by doing one or both of:

- **Naming an interface** — connecting a functional requirement to the specific code that fulfills it. This is the essential bridge between behavioral requirements and testable code.
- **Making a concrete design decision** — something the functional requirement deliberately left open, where options were weighed and a choice was made.

A design item `SHALL NOT` merely restate the functional requirement's behavior without naming an interface or making a decision. Every design item must do at least one of the above. Most functional requirements will have a corresponding design item, because the red agent needs a target even when there is no hard design decision. Cases where a functional requirement skips the design layer entirely are rare.

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

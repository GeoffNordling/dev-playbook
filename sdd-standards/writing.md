# Spec Writing Reference

Our specs use two complementary systems:

- **RFC 2119 modal verbs + EARS sentence templates** — govern the *prose* inside each spec item: what the requirement says and how strong the obligation is.
- **OpenFastTrace (OFT) Requirement-Enhanced Markdown** — governs the *structure* of each spec item: how it is identified, how items link to each other, and how a tracing tool can verify that every requirement has been designed, implemented, and tested.

RFC 2119 and EARS handle how individual requirements read. OFT handles structure and linking. The two systems are independent and complementary. See [overview.md](overview.md#references) for the canonical references.

## Prose: RFC 2119 and EARS

### Obligation Levels

Requirements use RFC 2119 modal verbs to indicate the strength of each obligation. This workspace uses a subset of the RFC 2119 vocabulary for consistency:

| Verb | Meaning | Agent treatment | Mandatory | RFC 2119 synonyms (not used here) |
|---|---|---|---|---|
| `SHALL` | Absolute requirement | Blocking acceptance criterion | Yes | MUST, REQUIRED |
| `SHALL NOT` | Absolute prohibition | Blocking acceptance criterion | Yes | MUST NOT |
| `SHOULD` | Strong preference; deviation requires justification | Quality target | No | RECOMMENDED |
| `SHOULD NOT` | Strong preference against; deviation requires justification | Quality target | No | NOT RECOMMENDED |
| `MAY` | Truly optional | Nice to have | No | OPTIONAL |

All uppercase obligation verbs `SHALL` be wrapped in backticks wherever they appear — in requirements, prose, and section introductions. This is a universal formatting rule with no exceptions.

A requirement `SHALL NOT` mix obligation levels (absolute, preference, optional). For example, a requirement that contains both `SHALL` and `SHOULD` is mixing an absolute obligation with a preference — the `SHOULD` behavior `SHALL` be split into its own spec item with its own ID. Using both `SHALL` and `SHALL NOT` within a requirement is permitted because they are the same level (absolute).

### Sentence Templates

Requirements `SHALL` be written using EARS (Easy Approach to Requirements Syntax) sentence templates. EARS provides the sentence structure; the obligation level table above provides the strength of obligation.

| Type | Pattern |
|---|---|
| **Ubiquitous** | The [system] `SHALL` [action] |
| **Event-driven** | When [trigger], the [system] `SHALL` [action] |
| **State-driven** | While [state], the [system] `SHALL` [action] |
| **Optional feature** | Where [feature included], the [system] `SHALL` [action] |
| **Unwanted behavior** | If [condition], then the [system] `SHALL` [action] |

Substitute the modal verb in any EARS sentence to grade the requirement's obligation level.

### Prose Conventions

**Fenced code blocks.** Spec files `SHALL NOT` contain fenced code blocks (triple backticks). OFT's markdown parser silently ignores all spec items that appear after a fenced code block. Use indented code blocks (4-space indent) instead.

**Illustrative examples.** A spec section that introduces non-trivial domain vocabulary `SHOULD` include a short illustrative example before the formal requirements. The example grounds the vocabulary in concrete terms so that requirements can reference it without re-explaining. Guidelines:

- One scenario per section. If a second example is needed, the section's vocabulary may be too overloaded and `SHOULD` be split.
- Place the example after the section's prose introduction and before the formal spec items.
- Examples `SHALL` use indented code blocks (4-space indent) or structured format that mirrors what the system actually produces or consumes.

## Structure: OpenFastTrace

### ID Format

Every requirement, design item, or test marker is identified by a tilde-separated ID:

```
type~name~revision
```

In source files, IDs are wrapped in backticks: `` `req~auth.login-validation~1` ``

**type** — a short ASCII-letter string identifying what kind of document this item lives in. See [Artifact Types](#artifact-types) below.

**name** — a unique identifier for this specific item within its type. Rules:
- Must start with a Unicode letter
- Subsequent characters: Unicode letters, numbers, hyphens (`-`), underscores (`_`), or dots (`.`)
- No whitespace
- No consecutive dots
- Dots create readable hierarchies: `auth.login-validation`, `parser.segment.timestamp`

**revision** — a positive integer (conventionally starting at 1). See [overview.md](overview.md#revision-policy) for the revision policy.

Examples:
```
feat~user-authentication~1
req~auth.login-validation~2
dsn~auth.login-validation~1
utest~auth.login-validation~3
```

### Artifact Types

This workspace uses five of OFT's artifact types:

| Type | Purpose |
|------|---------|
| `feat` | High-level feature |
| `req` | User/functional requirement |
| `dsn` | Design item |
| `utest` | Unit test |
| `itest` | Integration test |

OFT supports additional types (`arch`, `impl`, `stest`, `uman`, `oman`) but this workspace does not use them. Projects `MAY` adopt additional types if needed; additional types `SHALL` be documented in the project's `specs/` directory.

### Item Structure

A complete specification item in a Markdown file:

```markdown
### Login Credential Validation
`req~auth.login-validation~1`
Status: approved

When the user submits credentials, the system `SHALL` verify the provided
username and password against the credential store before granting session
access.

Rationale:
Unauthenticated access to any session-bearing endpoint is a critical
security vulnerability.

Comment:
The credential store interface is defined in dsn~credential-store~1.

Covers:
- feat~user-authentication~1

Needs: dsn, utest
```

The heading (`### Login Credential Validation`) is a standard Markdown heading and gives the item a human-readable title. The ID line immediately follows. The item ends when the next heading, ID line, or horizontal rule (`---`) is encountered.

Every keyword is followed by a colon. Content may start on the same line or the next, depending on the keyword.

| Keyword | Description | Notes |
|---|---|---|
| `Status:` | Lifecycle state: `draft`, `proposed`, or `approved`. Appears before the description. | OFT does **not** exclude `draft` items from coverage — status is informational only. |
| `Covers:` | Upstream IDs this item satisfies. Bullet format (`-`, `*`, or `+`), one ID per line. | Machine-readable claim, not free-form prose. |
| `Needs:` | Downstream artifact types that `SHALL` cover this item. | Comma-separated (`Needs: dsn, utest`). |
| `Rationale:` | Why the requirement exists. | Named field so tooling can extract it separately from the description. |
| `Comment:` | Caveats, implementation notes, or anything that fits neither description nor rationale. | |
| `Tags:` | Comma-separated labels for filtering traces by team or component. | Optional. |
| `Depends:` | Ordering dependencies between items. | Does not affect coverage; currently affects XML output only. |
| `Description:` | Explicit marker for the start of the description body. | Optional — any non-keyword text automatically starts the description. |
| `Interface:` | Public surface (signature) committed by a `dsn` item. One signature per line; repeatable. | `dsn` items only. Machine-validated; see [Interface Declarations](#interface-declarations). |
| `AgentReview:` | Prose describing what the review agent must check. Repeatable. | `dsn` items only. Verified by the `sdd-review` skill; see [AgentReview Declarations](#agentreview-declarations). |

### Interface Declarations

Design items that commit to a public surface `SHALL` declare the committed signatures in an `Interface:` field. The field is machine-validated: `pytest-sdd` imports the named symbol, introspects its signature, and fails at pytest collection time when the committed signature and the actual signature diverge.

#### Format

Each `Interface:` entry is a single line declaring one signature. A design item may declare multiple `Interface:` entries to commit to multiple related signatures (e.g., a class and its public methods).

    Interface: parser.parse_session(path: pathlib.Path) -> parser.Session
    Interface: parser.SessionParser.__init__(self, config: parser.ParserConfig) -> None
    Interface: parser.SessionParser.parse(self, path: pathlib.Path) -> parser.Session

Each signature includes the fully-qualified symbol path (`module.ClassName.method`), the parameter list with annotations, and the return annotation. Parameter kinds are expressed using standard Python syntax (`/` for positional-only, `*` for keyword-only, `*args`, `**kwargs`).

Instance methods include `self`. Classmethods include `cls`. Staticmethods omit both.

#### Annotation convention

Interface annotations follow a single modern idiom, matching what ruff's `UP` rules produce in the code.

| Annotation form | Modern (use) | Legacy |
|---|---|---|
| Non-stdlib classes | `pathlib.Path`, `myapp.session.Session` | bare `Path`, bare `Session` |
| Built-in generics | `list[int]`, `dict[str, Event]` | `typing.List[int]`, `typing.Dict[str, Event]` |
| Unions with None | `Event \| None` | `Optional[Event]`, `Union[Event, None]` |
| Primitives | `int`, `str`, `float`, `bool`, `bytes` | — |

Complex types are named through a single import and referenced by name rather than inlined as sprawling generic expressions.

#### Validator behavior

`pytest-sdd` parses each `Interface:` at pytest collection time and:

1. Imports the fully-qualified module containing the named symbol.
2. Resolves the symbol via attribute access (with MRO for inherited methods).
3. Reads its signature via `inspect.signature()` and evaluates annotations via `typing.get_type_hints()`.
4. Qualifies each annotation's class with its `__module__` and renders in modern form.
5. Compares parameter names, kinds, annotations, return annotation, and presence of defaults against the committed form.

Any mismatch fails collection. Because ruff's `UP` rules keep the code in the same modern idiom as the dsn, the comparison runs without a normalization layer.

#### Coexistence with prose

A design item may contain both prose and `Interface:` entries. Prose captures non-API decisions — schema, algorithm, error semantics — and flows through the OFT tooling into traceability reports and chain-text output. `Interface:` entries are the machine-checked part: the validator compares them against the code.

### AgentReview Declarations

Design items that commit to a non-testable behavior or a review-only property `SHALL` declare what must be checked in an `AgentReview:` field. The field carries prose; the `sdd-review` skill reads it on invocation and dispatches a review agent per item.

#### Format

Each `AgentReview:` entry is a single declaration describing one thing to check. A design item `MAY` declare multiple entries for multiple separate checks.

    AgentReview: The agent's system prompt at src/prompts/agent.md should contain
                 a directive discouraging filler or polite conversation.

File paths named inside the prose let the review agent locate what to compare against. Path staleness is detected when the review runs — `spec-lint` does not parse free-form prose for paths.

#### When to use

`AgentReview:` is the mechanism for commitments that cannot be deterministically tested. Typical cases:

- Behavioral requirements for LLM agents (e.g., "`SHALL NOT` attempt polite conversation for no reason")
- Output-format requirements where a prompt-inclusion test would degenerate into test-theater
- Cross-cutting conventions too contextual for a unit assertion

If a commitment can be tested deterministically, prefer `Needs: utest` or `Needs: itest` — tests are faster and more reliable than a review skill.

#### Coexistence with other verification fields

A `dsn` `MAY` combine `AgentReview:` with `Needs:` and `Interface:`. One design decision often commits several aspects; one `dsn` captures them all. See [Verification Fields](design-layer.md#verification-fields) for the rules on combining.

### Excluding Sections

When a document contains text that looks like OFT IDs but is not intended to be parsed (examples, reference sections, this document itself), exclude the section:

```markdown
<!-- oft:off -->
This section will not be parsed for spec items.
`req~example-only~1`
<!-- oft:on -->
```

## File Organization

### Spec Files

All spec files `SHALL` live in a `/specs/` directory at the repository root, versioned alongside the code. The [repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md) defines which files exist and their purpose.

### Splitting Large Specs

Each spec file starts as a single file. When it grows large enough to impair the agent's ability to work with it in a single context load, it `SHOULD` be split into a folder of files organized by feature or capability area.

**The decision to split `SHALL` be made by the human, not the agent.**

When split:
- `functional_requirements.md` → `functional_requirements/` folder
- `design.md` → `design/` folder
- Each folder `SHALL` contain an `index.md` — a structured Markdown table listing every file with a one-line scope description, so an agent can decide which files to load without reading all of them

OFT natively supports hierarchical organization. It scans all Markdown files it encounters recursively, assembling the full coverage graph from whatever IDs and links it finds. File names and folder structure do not affect tracing.

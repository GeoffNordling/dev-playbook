# Spec Format Reference

Our specs use two complementary systems:

- **RFC 2119 modal verbs + EARS sentence templates** — govern the *prose* inside each spec item: what the requirement says and how strong the obligation is.
- **OpenFastTrace (OFT) Requirement-Enhanced Markdown** — governs the *structure* of each spec item: how it is identified, how items link to each other, and how a tracing tool can verify that every requirement has been designed, implemented, and tested.

RFC 2119 and EARS handle how individual requirements read. OFT handles structure and linking. The two systems are independent and complementary.

---

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- EARS — Easy Approach to Requirements Syntax (Mavin et al.)
- OFT user guide (canonical format reference): https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- OFT repository: https://github.com/itsallcode/openfasttrace

---

## Writing Specs with RFC 2119 and EARS

### RFC 2119 Obligation Levels

Requirements use RFC 2119 modal verbs to indicate the strength of each obligation. This workspace uses a subset of the RFC 2119 vocabulary for consistency:

| Verb | Meaning | Agent treatment | Mandatory | RFC 2119 synonyms (not used here) |
|---|---|---|---|---|
| `SHALL` | Absolute requirement | Blocking acceptance criterion | Yes | MUST, REQUIRED |
| `SHALL NOT` | Absolute prohibition | Blocking acceptance criterion | Yes | MUST NOT |
| `SHOULD` | Strong preference; deviation requires justification | Quality target | No | RECOMMENDED |
| `SHOULD NOT` | Strong preference against; deviation requires justification | Quality target | No | NOT RECOMMENDED |
| `MAY` | Truly optional | Nice to have | No | OPTIONAL |

All uppercase obligation verbs `SHALL` be wrapped in backticks wherever they appear — in requirements, prose, and section introductions. This is a universal formatting rule with no exceptions.

### One Obligation Level Per Requirement

A requirement `SHALL NOT` mix obligation levels. If a multi-sentence requirement contains behavior at a different obligation level, that behavior `SHALL` be split into its own spec item with its own ID. Repeating the same keyword within a requirement is permitted.

### EARS Sentence Templates

Requirements `SHALL` be written using EARS (Easy Approach to Requirements Syntax) sentence templates. EARS provides the sentence structure; the obligation level table above provides the strength of obligation.

| Type | Pattern |
|---|---|
| **Ubiquitous** | The [system] `SHALL` [action] |
| **Event-driven** | When [trigger], the [system] `SHALL` [action] |
| **State-driven** | While [state], the [system] `SHALL` [action] |
| **Optional feature** | Where [feature included], the [system] `SHALL` [action] |
| **Unwanted behavior** | If [condition], then the [system] `SHALL` [action] |

Substitute the modal verb in any EARS sentence to grade the requirement's obligation level.

### Other Prose Conventions

**LaTeX math notation.** Specs `SHALL` use LaTeX math notation (e.g., `$k$`, `$N-1$`) when referring to variables, quantities, or mathematical relationships. This distinguishes formal variables from prose and renders correctly in markdown environments.

**Artifact type vocabulary conflict.** Spec item names that happen to match an artifact type pattern (3–6 letters, hyphen, 3 digits — e.g., `SHA-256`, `AES-128`) `SHALL` be written in unhyphenated form (`SHA256`, `AES128`). OFT may parse these as malformed IDs.

**Illustrative examples.** A spec section that introduces non-trivial domain vocabulary `SHOULD` include a short illustrative example before the formal requirements. The example grounds the vocabulary in concrete terms so that requirements can reference it without re-explaining.

Guidelines:
- One scenario per section. If a second example is needed, the section's vocabulary may be too overloaded and `SHOULD` be split.
- Place the example after the section's prose introduction and before the formal spec items.
- Examples `SHALL` use indented code blocks (4-space indent) or structured format that mirrors what the system actually produces or consumes. Spec files `SHALL NOT` contain fenced code blocks (triple backticks) — OFT's markdown parser silently ignores all spec items that appear after a fenced code block.

---

## Structuring Specs with OpenFastTrace

### Specification Item ID Format

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

**revision** — a positive integer (conventionally starting at 1). See [Revision Policy](#revision-policy).

Examples:
```
feat~user-authentication~1
req~auth.login-validation~2
dsn~auth.login-validation~1
utest~auth.login-validation~3
```

### Artifact Types

OFT defines a conventional vocabulary of artifact types. Projects `MAY` define additional custom types; custom types `SHALL` be documented in the project's `specs/` directory.

| Type | Purpose |
|------|---------|
| `feat` | High-level feature |
| `req` | User/functional requirement |
| `arch` | Architectural requirement |
| `dsn` | Design item |
| `impl` | Implementation marker (in source code) |
| `utest` | Unit test |
| `itest` | Integration test |
| `stest` | System test |
| `uman` | User manual |
| `oman` | Operations manual |

### Specification Item Structure

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

#### Keywords

Every keyword is followed by a colon. Content may start on the same line or the next, depending on the keyword.

**`Status:`** — lifecycle state of the item. One of `draft`, `proposed`, `approved`. Appears before the description. Important: OFT does **not** automatically exclude `draft` items from coverage enforcement — draft items participate in tracing like any other item. Status is informational only.

**`Covers:`** — explicit upstream links. Lists the IDs this item satisfies. Machine-readable claim; not free-form prose. Bullet format using `-`, `*`, or `+`. One ID per line.

```
Covers:
- feat~user-authentication~1
- feat~session-management~2
```

**`Needs:`** — declares which downstream artifact types `SHALL` cover this item. OFT fails the trace if any required type is absent. Two syntax variants (do not mix within one item):

```
Needs: dsn, utest
```
```
Needs:
- dsn
- utest
```

**`Rationale:`** — the reason the requirement exists. Named field so tooling can extract it separately from the description.

**`Comment:`** — caveats, implementation notes, or anything that fits neither description nor rationale.

**`Tags:`** — comma-separated labels for filtering traces by team or component. Optional.

**`Depends:`** — ordering dependencies between items. Does not affect coverage; currently affects XML output only.

**`Description:`** — explicit keyword to mark the start of the description body. Optional: any non-keyword text automatically starts the description. Only needed in unusual layouts.

### The Coverage Chain

OFT enforces a directed graph of coverage. Each item declares what must cover it downstream (`Needs:`), and each downstream item declares what it covers upstream (`Covers:`). OFT walks this graph and fails if any required link is absent.

Our standard chain for a project:

```
feat~user-authentication~1
  Needs: req
      |
      ▼
req~auth.login-validation~1         (Covers: feat~user-authentication~1)
  Needs: dsn, utest
      |                   |
      ▼                   ▼
dsn~auth.login-validation~1     utest~auth.login-validation~1
  Covers: req~...                 Covers: req~...
  Needs: itest                    (no Needs — terminates chain)
      |
      ▼
itest~auth.login-validation~1
  Covers: dsn~...
  (no Needs — terminates chain)
```

A **terminating item** has no `Needs:` declaration. OFT treats it as a leaf — nothing downstream is required.

OFT fails the trace when:
- Any item's `Needs:` types are not all covered by at least one item of each required type
- A `Covers:` link references an ID that does not exist at that revision
- Any item is orphaned (has `Covers:` pointing to a nonexistent item)

The `feat` level is optional for smaller projects. A project with no feature decomposition `MAY` begin the chain at `req`.

### Revision Policy

The revision number is a semantic version for the item's meaning.

**Increment** the revision when the semantic content changes — when the requirement means something different than it did before. This immediately breaks all downstream `Covers:` links that referenced the previous revision, forcing downstream documents to explicitly acknowledge and respond to the change.

**Do not increment** for typo fixes, rephrasing that does not change meaning, or formatting changes.

When you increment a revision, update all `Covers:` references in downstream documents to the new revision. If a downstream item's response to the change is "no change needed," update the `Covers:` link and note this in the `Comment:` field.

### Forwarding

OFT supports a forwarding syntax that lets a document layer acknowledge a requirement and pass coverage responsibility downstream without creating a full spec item:

```markdown
arch --> dsn : req~auth.login-validation~1
```

**Do not use forwarding in this workspace.** Every layer in our standard chain (`feat → req → dsn → utest/itest`) is expected to have real content. Forwarding is an escape hatch for situations where a chain layer exists structurally but has nothing to say — a situation our chain is designed to avoid. It is documented here so you recognize it if you encounter it in the OFT documentation.

### Excluding Sections from OFT Parsing

When a document contains text that looks like OFT IDs but is not intended to be parsed (examples, reference sections, this document itself), exclude the section:

```markdown
<!-- oft:off -->
This section will not be parsed for spec items.
`req~example-only~1`
<!-- oft:on -->
```

---

## File Structure and Organization

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

### Requirement Traceability

Every `req` item defined in the functional spec `SHALL` appear in the design spec via at least one `Covers:` link from a `dsn` item. This ensures every functional requirement has been translated into a concrete piece of the design.

OFT (invoked via `pytest-sdd`) verifies this coverage. See [Tooling Integration](#tooling-integration) below.

### Machine-Readable Contracts

Where appropriate, natural language requirements `SHOULD` be paired with machine-readable contracts (OpenAPI specs, JSON Schema) to formally constrain agent behavior. These are especially useful for API boundaries and data structures where ambiguity could cause silent regressions.

---

## Tooling Integration

### pytest-sdd

`pytest-sdd` is a pytest plugin that validates OFT spec files as part of the normal test suite. It provides two checks:

- **Lint** (`-m spec -k lint`): structural validation of every `.md` spec file — ID format, Status field, bare obligation keywords, mixed obligation levels, Covers syntax, Needs values.
- **Trace** (`-m spec -k trace`): full OFT traceability check, delegating to the OpenFastTrace JAR to verify that every `Needs:` declaration is satisfied.

**Installation:**

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=tools"
```

**Configuration** in `pyproject.toml`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements", "specs/design"]
oft_jar = "../dev-playbook/tools/lib/openfasttrace-4.2.2.jar"
```

Both fields are required. `spec_dirs` lists the directories containing OFT markdown files; `oft_jar` is the path to the OpenFastTrace JAR (v4.2.2), relative to the project root.

The JAR is vendored once in dev-playbook at `tools/lib/openfasttrace-4.2.2.jar` (gitignored). All workspace projects reference it via the relative path `../dev-playbook/tools/lib/openfasttrace-4.2.2.jar`. This assumes the standard workspace layout where all repos live under `~/workspace/`. If the JAR is not present, download it from https://github.com/itsallcode/openfasttrace/releases/tag/4.2.2 and place it at that path.

Projects that only have functional requirements and no design layer omit `specs/design` from `spec_dirs`:

```toml
[tool.pytest-sdd]
spec_dirs = ["specs/functional_requirements"]
oft_jar = "../dev-playbook/tools/lib/openfasttrace-4.2.2.jar"
```

**Invocation:**

```bash
pytest -m spec              # run all spec checks (lint + trace)
pytest -m spec -k lint      # lint only
pytest -m spec -k trace     # traceability only
pytest -m "not spec"        # skip spec checks
```

Spec checks run automatically when `pytest` is invoked without `-m` flags, interleaved with the normal test suite. The `spec` marker allows selective execution.

**OFT JAR requirement:** Java must be on `PATH`. The JAR file must exist at the configured path. Neither is optional — a missing JAR or missing Java is a hard test failure.
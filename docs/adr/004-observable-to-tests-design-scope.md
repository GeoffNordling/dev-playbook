# ADR-004: Observable-to-Tests Design Scope and Machine-Validated Interfaces

**Date:** 2026-04-19
**Status:** Accepted

## Context

The custom SDD workflow established in [ADR-001](001-adopt-openfasttrace.md), [ADR-002](002-evaluate-spec-kit-retain-custom-sdd.md), and [ADR-003](003-evaluate-sdd-community-landscape.md) leaves three gaps that became apparent during use.

**The design-layer framing was imprecise.** The current [design-layer.md](../../sdd-standards/design-layer.md) presents design items as serving a *primary* role of "naming the interfaces that tests target" and a *secondary* role of recording design decisions. The split blurs what belongs in a dsn versus what belongs in code, particularly for greenfield work where committing to a specific class or function felt premature before the code existed. The same imprecision pushed authors toward verbose disclaimers about what a dsn was not constraining, which scaled poorly.

**Public-surface claims in dsn items were not machine-validated.** A dsn could claim a function exists with a given signature while the actual code drifted to a different signature. Unlike `req → utest` coverage (enforced by `@pytest.mark.req` markers and `pytest-sdd`), public-surface claims were prose that could silently rot. Any artifact in the coverage chain should be machine-checkable.

**The public-only testing rule was implicit.** Line 26 of `testing-conventions.md` forbids asserting on private state and line 71 forbids mocking internal implementation, yet no line makes the positive rule explicit, and no tooling catches violations.

## Decision

### Four principles for design items

1. **Single role.** Every design item records a design decision. API shape, algorithm, data schema, error semantics, and data-structure choice are equal kinds of decision. A dsn whose only decision is API shape is a complete dsn.

2. **Observable-to-tests scope.** A design item commits to a decision when a test could fail on it if the decision were changed. Invisible choices — private helpers, internal delegation, non-public file layout — stay in the code and do not appear in design items.

3. **Commitment by naming.** When a dsn names a public surface, the shape of what it names is the commitment. A class, a method, a module-level callable — each is committed by being named in that form.

4. **Design-agent ownership of structure.** The design agent performs brownfield reconnaissance (extend-vs-new, public-surface choice, module layout) before writing any dsn, producing dsn items and interface stubs. The red agent tests against the committed stubs; the green agent fills in bodies and makes only invisible choices below the committed surface. Red-first order stays.

### Machine-validated interface claims

Each design item that names a public surface `SHALL` declare the interface in a structured `Interface:` field. The validator parses this field, introspects the code, and fails when the committed signature and the actual signature diverge.

- **Keyword format.** `Interface:` accepts a single signature line, or a bulleted block of signatures for cohesive classes. Multiple `Interface:` declarations per dsn are permitted for interfaces that belong together under one design decision.
- **Annotation convention.** Fully-qualified non-stdlib names (`pathlib.Path`, `myapp.session.Session`), PEP 585 built-in generics (`list[int]`, `dict[str, Event]`), PEP 604 unions (`Event | None`). Ruff `UP` rules keep the code in the same modern form, so the validator compares modern-form against modern-form without a normalization layer.
- **Validator algorithm.** Resolve the fully-qualified symbol via import, call `inspect.signature()`, evaluate annotations via `typing.get_type_hints()`, qualify each class with its `__module__`, render in modern form, compare as strings.
- **Strict equality on parameters.** Name, kind (positional-only, positional-or-keyword, keyword-only, `*args`, `**kwargs`), annotation, and presence of defaults all match exactly.
- **Host.** `pytest-sdd` extends to parse `Interface:` and run the validator at pytest collection time, alongside the existing coverage check.

### Public-only testing, enforced

Tests access only public names (identifiers not prefixed with `_`, excluding Python dunder protocol methods). Private helpers are exercised through the public interfaces that call them. `standards/testing-conventions.md` gains one line stating this rule positively.

Two enforcement mechanisms combine:

- **Ruff `SLF001`** (private-member-access) is enabled in both `tools/pyproject.toml` and `sdd-tools/pyproject.toml`. It catches `obj._private` attribute access.
- **`pytest-sdd` adds a test-privacy AST check** that flags non-dunder leading-underscore imports and attribute accesses reaching into non-test modules. Leading-underscore helpers defined locally in test files remain scoped to the test file and pass.

### Reasoning goes in `Rationale:`

Brownfield reconnaissance output — why the design extends `FooParser` rather than creating a new class, why a free function rather than a class — lives in each dsn's existing `Rationale:` field.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Separate code-organization document (per-feature or per-project) | Stale-on-merge unless machine-validated; once machine-validated, it duplicates what `Interface:` on dsn items already provides. A derived view over the dsn collection meets the human-review need without introducing a maintained artifact. |
| `arch~` artifact type for structural items | No relational claims (module-A-imports-module-B, module-boundary assertions) are pressing at current scale. Deferred until a case surfaces where signature-level dsn items cannot express the constraint. |
| Protocol/ABC structural-typing validation | Low value at current scale. A dsn naming concrete classes and methods directly is sufficient. Deferred. |
| Stdlib annotation shorthand with a known-name table | Ambiguity and maintenance cost of the table outweigh the ergonomic gain. Fully-qualified explicit form is unambiguous, and ruff `UP` already keeps code in modern form. |
| Loose signature matching (structural compatibility) | Defeats the validation purpose. Strict equality forces dsn updates when the public surface changes, which is the behavior we want. |
| Green agent selects API shape | Incompatible with red-first workflow: red needs stable interface stubs before writing tests. Design agent commits structure up front. |
| Implicit public-only testing (no validator) | Already implicit today and produces no signal when violated. Explicit rule plus enforcement closes the loop. |

## Consequences

- `sdd-standards/design-layer.md` is rewritten around the four principles.
- `sdd-standards/writing.md` gains the `Interface:` keyword spec and the annotation convention.
- `standards/testing-conventions.md` gains one line making the public-only rule explicit.
- `dotfiles/.claude/skills/sdd-design/SKILL.md` is rewritten to reflect the four principles, brownfield reconnaissance, `Interface:` authoring, interface-stub generation, and `Rationale:` as the reasoning home.
- `dotfiles/.claude/skills/sdd-red/SKILL.md` is updated to read `Interface:` as the test target rather than parsing dsn prose.
- `dotfiles/.claude/skills/sdd-green/SKILL.md` is updated to state that invisible choices below the committed surface belong to the green agent.
- `sdd-func-reqs` and `sdd-issue-coordinate` are audited; substantive changes expected to be zero.
- A follow-up issue is opened: `pytest-sdd` refactor for modular hosting of OFT parsing, coverage graph, `Interface:` parsing, introspection validator, test-privacy check, and reporting. Refactor plan is required before code.
- Ruff `SLF001` is enabled in both `tools/pyproject.toml` and `sdd-tools/pyproject.toml`.
- The deferred directions from [ADR-003](003-evaluate-sdd-community-landscape.md) (adversarial review, replanning phase, `dec` artifact type) remain open; none are addressed here.

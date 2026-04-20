# SDD Tools

Spec-driven development is a [frontier-invariant](../protocols/README.md) response to rapidly advancing AI capabilities. It lets humans specify requirements at the highest appropriate level of abstraction — in terms natural for humans to express and think about, yet precise enough for the current generation of AI to understand and implement reliably.

> *"It appears to be a quite general principle that, whenever there is a randomized way of doing something, then there is a non-randomized way that delivers better performance but requires more thought."*  
> — E.T. Jaynes
>
> *"A designer knows he has achieved perfection not when there is nothing left to add, but when there is nothing left to take away."*  
> — Antoine de Saint-Exupéry
>
> *"I didn't have time to write a short letter, so I wrote a long one instead."*  
> — Mark Twain (attributed)

The tools here serve two narrow, enduring purposes:

- **Deterministic validation** — lint specs, check traces, verify interface signatures, enforce test-privacy. Structure reduces variance; these checks will always be cheaper, faster, and more reliable than AI for the specific narrow things they do, even as AI continues to advance.
- **Deterministic compression** — render conformant specs into views that fit within the human context window. Compressed yet precise, sufficient for their purpose, deterministic and reliable.

## What belongs here

- Validators that enforce conformance to SDD standards (lint, trace, interface signatures, test-privacy)
- Compressors that render conformant specs into human-graspable views (chains, structure summaries) with 100% accuracy
- Supporting libraries consumed by the above

## What does NOT belong here

- Generators, scaffolders, or anything that a frontier model does well
- General workspace automation — that lives in [`tools/`](../tools/)
- Standards themselves — those live in [`sdd-standards/`](../sdd-standards/)

## Setup

```bash
cd sdd-tools && uv sync
```

Requires Python >= 3.11, [uv](https://docs.astral.sh/uv/), and Java on `PATH` for the OFT JAR.

## Layout

```
sdd-tools/
├── src/sdd_tools/
│   ├── models.py           SpecItem + Finding (canonical types)
│   ├── config.py           [tool.pytest-sdd] reader
│   ├── oft.py              JAR adapter: trace, convert, parse XML → SpecItem
│   ├── lint.py             markdown lint → Finding list
│   ├── interface.py        Interface: parser + signature introspection
│   ├── privacy.py          AST test-privacy walk
│   ├── markers.py          pytest markers → synthetic utest md
│   ├── pytest_plugin.py    plugin entry; one pytest item per validator
│   ├── chains.py           coverage chain builder
│   ├── filtering.py        chain filters
│   ├── formatter.py        chain text renderer
│   └── cli/chain.py        sdd-chain entry point
├── tests/
├── lib/openfasttrace-4.2.2.jar   (gitignored)
├── pyproject.toml
└── Makefile
```

## Vendored binaries (`lib/`)

| File | Purpose |
|------|---------|
| `openfasttrace-4.2.2.jar` | OpenFastTrace JAR used by every JAR-backed validator (gitignored) |

## Tools

| Surface | Entry point | Purpose |
|---------|-------------|---------|
| pytest plugin | `sdd_tools.pytest_plugin` | hosts `spec-lint`, `spec-coverage`, `spec-interface`, `spec-privacy` items |
| CLI | `sdd-chain` (`sdd_tools.cli.chain:main`) | render full spec traceability chains with body text |

Each tool supports `--help` for usage. See [sdd-standards/tooling.md](../sdd-standards/tooling.md) for installation, configuration, invocation, and CI integration.

## Output contract

Every Finding-emitting validator produces `Finding` objects. The standard rendering anchors each finding to a file/line and tags rule, optional spec ID, optional `line_kind` (when the line is the best available anchor rather than the exact site, e.g. the dsn header for an Interface mismatch), an optional multi-line `detail` block, and an optional one-line `fix` hint.

```
specs/feature.md:42 (dsn header)  interface.mismatch  signature differs for parser.parse_session
  committed: parser.parse_session(path: pathlib.Path) -> parser.Session
  actual:    parser.parse_session(path: str) -> parser.Session
  fix:       update Interface: or update the code to match
```

The pytest plugin renders the failing item's failure message as the rendered Finding list (or, for `spec-coverage`, the OFT JAR's report).

## Exit codes (standalone CLIs)

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | Tool-level error — JAR missing, Java missing, unreadable config |

pytest-hosted validators inherit pytest's native exit scheme.

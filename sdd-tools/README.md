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

- **Deterministic validation** — lint specs, check traces, verify interface signatures. Structure reduces variance; these checks will always be cheaper, faster, and more reliable than AI for the specific narrow things they do, even as AI continues to advance.
- **Deterministic compression** — render conformant specs into views that fit within the human context window. Compressed yet precise, sufficient for their purpose, deterministic and reliable.

## What belongs here

- Validators that enforce conformance to SDD standards (lint, trace, interface signatures)
- Compressors that render conformant specs into human-graspable views (chains, dimension projections) with 100% accuracy
- Reporters that inventory spec-declared commitments for follow-up by skills (AgentReview records)
- Supporting libraries consumed by the above

## What does NOT belong here

- Generators, scaffolders, or anything that a frontier model does well
- General workspace automation — that lives in [`tools/`](../tools/)
- Standards themselves — those live in [`sdd-standards/`](../sdd-standards/)

## Setup

```bash
cd sdd-tools && uv sync
```

Requires Python >= 3.11, [uv](https://docs.astral.sh/uv/), Java on `PATH`, and the OpenFastTrace JAR at `lib/openfasttrace-4.2.2.jar` (gitignored; download from https://github.com/itsallcode/openfasttrace/releases/tag/4.2.2).

## What's here

| Surface | Entry point | Role | Parse tier |
|---|---|---|---|
| pytest plugin | `sdd_tools.pytest_plugin` | `spec-lint` (structure + dimensions + verification), `spec-coverage`, `spec-interface` | markdown (lint) + OFT JAR (coverage, interface) |
| CLI | `sdd-chain` (`sdd_tools.cli.chain:main`) | Focused-narrative projection (feat→req→dsn walks) | OFT JAR |
| CLI | `sdd-index` (`sdd_tools.cli.index:main`) | Per-dimension one-line catalog of every `dsn` | markdown |
| CLI | `sdd-atlas` (`sdd_tools.cli.atlas:main`) | Per-dimension full-body dump of every `dsn` | markdown |
| CLI | `sdd-review` (`sdd_tools.cli.review:main`) | `AgentReview:` inventory (reporting, not validation) | markdown |

The markdown tier is a pure-Python parser in `sdd_tools.parse.markdown`; the OFT tier wraps the `openfasttrace` JAR via `sdd_tools.oft`. Lint modules, `sdd-index`, `sdd-atlas`, and `sdd-review` share the markdown tier; `sdd-chain`, coverage, and the interface validator share the OFT tier.

Test-privacy enforcement has moved out of SDD scope to [`tools/bin/test-privacy`](../tools/bin/test-privacy) — it enforces a testing convention, not an SDD rule.

## Tool reference

Each tool supports `--help` for full usage.

### pytest-sdd

Pytest plugin that synthesizes one `spec`-marked pytest item per SDD validator (`spec-lint`, `spec-coverage`, `spec-interface`). Items fail with rendered `Finding` blocks.

```bash
pytest -m spec                       # all SDD validators
pytest -m spec -k lint               # lint only
pytest -m "not spec"                 # skip every SDD validator
```

### sdd-chain

Render full spec traceability chains (feat → req → dsn) with verbatim body text at every layer. Test layers are excluded from output.

```bash
sdd-chain                       # dump all chains
sdd-chain --id '*auth*'         # chains containing a matching item
sdd-chain --feature '*user*'    # chains rooted at a matching feat item
```

### sdd-index

Emit a per-dimension one-line catalog of every `dsn` in the project — id, title, source location — grouped under the four dimension headers (`## Data`, `## API Shape`, `## Algorithms`, `## Composition`). Grouping is driven by each item's `Dimension:` field; items with multiple dimensions appear under each group they name. Useful as a first pass for humans scanning the project's design surface, and as input to agent prompts that reason about the dsn inventory without reading every body.

```bash
sdd-index                       # whole project
sdd-index --root /path/to/proj  # explicit project root
```

### sdd-atlas

Emit the full body of every `dsn` in the project, grouped by dimension. Same discovery and filtering as `sdd-index`, but retains each item's prose and keyword fields. Use when the catalog view is not enough.

```bash
sdd-atlas                       # whole project
sdd-atlas --root /path/to/proj  # explicit project root
```

### sdd-review

Inventory every `dsn` carrying an `AgentReview:` field. Emits one structured record per reviewed item, consumed by the `sdd-review` skill which dispatches a review agent per record. Reporting only — well-formedness of `AgentReview:` fields is enforced at pytest collection time by `spec-lint`.

```bash
sdd-review                      # whole project
sdd-review --root /path/to/proj # explicit project root
```

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

## Development

```bash
cd sdd-tools && uv sync      # setup
uv run pytest                # tests
make lint                    # ruff check
make format                  # ruff format
make typecheck               # mypy
```

Python >= 3.11; ruff for lint + format, mypy for type checking. Line length 88 (ruff default). Ruff rules: E, W, F, I, UP, B, SIM, SLF (E501 ignored).

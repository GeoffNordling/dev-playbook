# SDD Tools

Spec-driven development is a [frontier-invariant](../protocols/README.md) response to rapidly advancing AI capabilities. It lets humans specify requirements at the highest appropriate level of abstraction — in terms natural for humans to express and think about, yet precise enough for the current generation of AI to understand and implement reliably.

The tools here serve two narrow, enduring purposes:

- **Deterministic validation** — lint specs, check traces, verify interface signatures. Structure reduces variance; these checks will always be cheaper, faster, and more reliable than AI for the specific narrow things they do, even as AI continues to advance.
- **Deterministic compression** — render conformant specs into views that fit within the human context window. Compressed yet precise, sufficient for their purpose, deterministic and reliable.

<!-- QUOTES: placeholder — fill in later -->
> *"…"*
> — TBD

## What belongs here

- Validators that enforce conformance to SDD standards (lint, trace, signature checks)
- Compressors that render conformant specs into human-graspable views (trees, diagrams, summaries) with 100% accuracy
- Supporting libraries consumed by the above

## What does NOT belong here

- Generators, scaffolders, or anything that a frontier model does well
- General workspace automation — that lives in [`tools/`](../tools/)
- Standards themselves — those live in [`sdd-standards/`](../sdd-standards/)

## Setup

```bash
cd sdd-tools && uv pip install -e .
```

Requires Python >= 3.11, [uv](https://docs.astral.sh/uv/), and Java on `PATH` for the OFT JAR.

## What's here

### Packages (`src/`)

| Package | Location | Purpose |
|---------|----------|---------|
| `pytest-sdd` | `src/pytest_sdd/` | pytest plugin for OFT spec validation: lint checks + traceability via OFT JAR |
| `sdd-chain-text` | `src/sdd_chain_text/` | Standalone CLI: display full spec traceability chains with body text |

### Vendored binaries (`lib/`)

| File | Purpose |
|------|---------|
| `openfasttrace-4.2.2.jar` | OpenFastTrace JAR used by `pytest-sdd` and `sdd-chain-text` (gitignored) |

## Tool reference

Each tool supports `--help` for full usage, options, and exit codes.

### pytest-sdd

pytest plugin for validating OFT spec files as part of the normal test suite. Installed as a dev dependency in each project; configured in `pyproject.toml`. See [tooling.md](../sdd-standards/tooling.md) for configuration and invocation.

```bash
uv add --dev "pytest-sdd @ git+https://github.com/GeoffNordling/dev-playbook#subdirectory=sdd-tools"
```

```bash
pytest -m spec          # run all spec checks (lint + trace)
pytest -m spec -k lint  # lint only
pytest -m spec -k trace # traceability only
```

Requires Java on `PATH` and the OFT JAR at `../dev-playbook/sdd-tools/lib/openfasttrace-4.2.2.jar`.

### sdd-chain-text

Display full spec traceability chains with verbatim body text. Reads `[tool.pytest-sdd]` config from the project's `pyproject.toml`, runs the OFT JAR to extract all spec items as XML, builds coverage chains, and prints them with full text at each layer.

```bash
sdd-chain-text                       # dump all chains
sdd-chain-text --id '*auth*'         # chains containing items matching glob
sdd-chain-text --type dsn            # chains containing dsn items
sdd-chain-text --file registry       # chains with items from matching files
sdd-chain-text --feature '*user*'    # chains rooted at a matching feat item
sdd-chain-text --root /path/to/proj  # explicit project root
```

Test layers (utest, itest) are excluded from chain output. Requires Java on `PATH` and the OFT JAR configured in `pyproject.toml`.

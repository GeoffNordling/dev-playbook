---
type: General-Sheet
title: Parking Lot
description: Content evicted from Standards during the ports — important, belonging elsewhere, held here with its provenance until sorted
---

# Parking Lot

The one location for what a port evicts from a Standard: rationale,
heuristics, procedure, anything that does a second thing in a document
that does one
([System Legibility](/docs/system-legibility.md#standing-principles)).
Member of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).
Each entry is the evicted text verbatim under a heading, with one line
of provenance: the file it left, the port that moved it, and who still
cites it. Sorting the lot into permanent homes is its own step in
[Registry Refactor](/no-more-slop-branch-working-files/REGISTRY-REFACTOR.md#next-steps).

## The src/ conjunction

From `standards/build/layers.md`, the Build port; File Skeleton's
Python package condition states the conjunction as its test, and
nothing carries the reason.

`src/` is the default source root of most JavaScript build tools as well, so
the `python · src` trigger is a conjunction: a repo without `pyproject.toml`
is not in the python layer, and therefore not in `python · src`, whatever it
keeps in `src/`.

## A deviation is an amendment

From `standards/build/layers.md`, the Build port; cited by nothing.

A deviation from a requirement is an amendment to this standard in
dev-playbook.

## Deferred licensing

From `standards/build/layers.md`, the Build port; cited by nothing.

Licensing: the standard takes no position on `LICENSE` files.

## Why CI skips ref-lint

From `standards/build/ci.md`, the Build port; Gates' Skips rule carries
the one-sentence form.

`SKIP: ref-lint` because `ref-lint` validates cross-repo Citations
(`~/workspace/<repo>/…`), and a CI runner checks out only the one repo, so
those citations can never resolve there. Local pre-commit remains the strict
reference gate. `okf-lint` runs in CI — everything it checks is in-repo.

## Tests run locally

From `standards/build/ci.md`, the Build port; Canonical Artifacts'
ci.yml rule says tests run at the push gate, and nothing carries the
reason.

CI runs the hook suite and nothing else. Tests stay local: this workspace is
local-first (no cloud agents, ever), and test suites depend on dev-playbook
as a local path dependency that does not exist on a cloud runner. The
pre-push-stage hook does not fire under `pre-commit run`, so CI stays
test-free automatically.

## The Make target table

From `standards/build/make.md`, the Build port; Canonical Artifacts'
Makefile rule names the fragments, and the fragments hold the recipes.

| Target | Layer | Recipe |
|---|---|---|
| `check` | base | `uvx pre-commit run --all-files`, after the layer prerequisites below |
| `check-judgments-cache` | base / python | base: `check-judgments-cache: check` (no pytest, nothing to arm); python: `$(MAKE) check SKIP_JUDGMENTS=$(if $(NO_JUDGMENT_CACHE),1,0)` — `check` with the judgment cache gate armed |
| `format` (mutating) | python | `uv run ruff format .` |
| `format-check` | python | `uv run ruff format --check .` |
| `lint` | python | `uv run ruff check .` |
| `typecheck` | python | `uv run mypy <code-roots>` — whichever of `src tests scripts` hold `.py` files |
| `test` | python | `uv run pytest` |

## Judgment cache tripwires under make

From `standards/build/make.md`, the Build port; a candidate home is the
[cache gate](/standards/semantic-validation/cache-gate.md).

The `test` target carries whatever judgment cache tripwires the repo has
wired via pytest — deterministic checks, no LLM
([cache-gate.md](/standards/semantic-validation/cache-gate.md)) — but `make test`
and `make check` **skip** them by default (they export `SKIP_JUDGMENTS=1`), so
a subagent never hits a miss it cannot fill. `make check-judgments-cache` arms
them and is the pre-push hook's entry — a repo with none wired passes it
vacuously; a bare `uv run pytest` arms them too (fail-safe).

## The cache lives on one machine

From `standards/build/make.md`, the Build port; a candidate home is
[Machines](/docs/machines.md), which Canonical Artifacts' Makefile rule
already links for `NO_JUDGMENT_CACHE`.

The judgment cache exists only on the Fedora primary. Every other machine sets
`NO_JUDGMENT_CACHE=1`, and `check-judgments-cache` skips that one check there.
The rest of the push gate — mypy, pytest, the hook suite — runs everywhere
([machines.md](/docs/machines.md)).

## The pyproject pins, the reasons

From `standards/build/python.md`, the Build port; worth keeping
([Registry Refactor](/no-more-slop-branch-working-files/REGISTRY-REFACTOR.md#findings-from-two-readings));
Canonical Artifacts' pyproject.toml rule lists the pins, and nothing
carries the reasons.

The reasons behind the canonical file's pins:

- **`uv_build`** over other backends: it is bundled inside the uv binary,
  so building the package — including editable installs by consumers —
  needs no network and no PyPI, and its default layout is exactly this
  standard's (`src/<package>`, named from the project name).
- **`disallow_untyped_defs` + `disallow_incomplete_defs`** instead of
  `strict = true`: the pair guarantees every function signature is fully
  annotated, while full strict also turns on `disallow_untyped_calls`
  (chokes on every untyped third-party lib) and `disallow_any_generics`
  (noisy about every bare `list`/`dict`).
- **`disable_error_code = ["import-untyped"]`**: importing a library that
  ships no type stubs works without `# type: ignore` at each import site;
  `types-*` stub packages join `dev` when a specific library warrants them.
- **The ruff families** beyond the `E`/`W`/`F` core: each catches a
  distinct defect class — `I` import order, `UP` outdated syntax, `B`
  bug-prone patterns, `SIM` needless complexity, `SLF` private-member
  access from outside the defining class, and `D` docstring presence and
  format (pydocstyle), enforcing the docstring conventions in
  [python/style.md](/standards/python/style.md).
- **`[tool.ruff.lint.pydocstyle] convention = "pep257"`**: `D` on its own
  turns on mutually-exclusive members (`D203` vs `D211`, `D212` vs `D213`),
  so `ruff check` is unsatisfiable until a `convention` selects between
  them — pinning it is what keeps the family usable. Per-file ignores then
  drop all of `D` for `tests/**` (test functions carry no docstrings by
  convention) and `D104` for `__init__.py` (an empty init has none — see
  `python.empty-init`).
- **`ignore = ["E501", "D401"]`**: `ruff format` owns line length, so the
  `E501` lint rule would report the same overruns a second time; `D401`
  (imperative-mood summaries) is dropped to keep the workspace's
  noun-phrase docstring voice.

## A uv workspace for multiple projects

From `standards/build/python.md`, the Build port; File Skeleton's
Root-only files rule holds the one-project rule, and nothing carries
the escape hatch.

A repo that genuinely needs multiple projects uses a
[uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) — one root
`uv.lock`, members declared in the root `pyproject.toml` — and amends this
standard first.

## Workspace-wide utility

From `standards/build/python.md`, the Build port; cited by nothing.

**Workspace-wide utility**: `uv tool install -e .` puts the project's
entry points on `PATH` machine-wide, editable — the tool tracks the
checkout.

## Initial setup

From `standards/build/python.md`, the Build port; a candidate home is
[Bootstrap](/standards/build/bootstrap.md).

`uv init --package <repo>` generates the uv_build src layout; overwrite the
generated `pyproject.toml` with the canonical shape.

## One config serves every repo

From `standards/build/canonical.md`, the Build port; Canonical
Artifacts' .pre-commit-config.yaml rule carries what the config holds,
and nothing carries why one config fits every repo.

It serves every repo unchanged: a hook with no matching files skips itself, and
detectors like `judgments-lint` and `harness-files-lint` pass trivially where a repo
has no `[tool.judgments]` table and no authored skills.

## Non-gate checks

From `standards/build/enforcement.md`, the Build port; Gates' Three
rungs body carries the same two non-gates in prose.

| Non-gate | When | What runs | Blocks |
|---|---|---|---|
| agent ritual | before finishing every committing phase | `make check` | no — a node-skill discipline; the normative rule lives in [the node-skill contract](/software-factory/factory-operations.md#the-node-skill-contract) |
| workspace-lint | on demand and via the periodic review | GitHub settings drift and default-branch protection ([repo-settings.md](/standards/tracking/repo-settings.md)), label/issue/epic tracking conformance, four-tuple validity, and stale dev-playbook pins, via [`workspace-lint`](/scripts/workspace-lint) | no — reports |

## The detector map

From `standards/build/enforcement.md`, the Build port; retired as the
hand-written form of the join rulegen's third table computes, and cited
by nothing.

| Detector | Owns | Gates |
|---|---|---|
| repo-lint | structure: presence, forbidden files, layer shape, canonical compares, doc shape, script shebangs, name mapping | hook pattern |
| ruff-check / ruff-format | Python lint + formatting + docstrings (`D`) | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| testing-lint | test privacy, mirror layout, no-logic | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| decisions-lint | Decision Record sequential numbering, status vocabulary | hook pattern |
| ref-lint | Links and Citations | hook pattern, except the CI gate and the secondary machines (skipped — neither carries the cited repos) |
| prose-lint | prose spelling (the American `judgment`); the banned actor noun; the first person in harness-loaded agent instructions | hook pattern |
| judgments-lint | judgment declarations | hook pattern |
| standards-lint | the meta-standard's card layout, catalog order, card↔rule matrix, hook surfaces | hook pattern (dev-playbook only) |
| shellcheck | shell scripts | hook pattern |
| shfmt | shell formatting | hook pattern |
| harness-files-lint | runbooks — skill bundles and agent definitions (runbook-authoring repos); the global CLAUDE.md source's shape (dev-playbook only) | hook pattern |
| mypy | types | push gate only — never the CI gate |
| pytest | tests + judgments cache gate | push gate only — never the CI gate; the judgments cache gate is skipped on the secondary machines |
| workspace-lint | GitHub settings and default-branch protection ([repo-settings.md](/standards/tracking/repo-settings.md)), label-scheme and issue/epic tracking conformance, four-tuple validity, stale pins | workspace-lint (outside the gates) |

## Enrollment rides the pin, the argument

From `standards/build/distribution.md`, the Build port; Distribution
Channel's One published id rule carries the one-sentence form.

An enumerated consumer block cannot do this, which is why the manifest
publishes one id and `MUST` keep publishing one. `pre-commit autoupdate`
moves `rev` and nothing else, and pre-commit accepts no wildcard in place of
a literal hook id, so any list a consumer writes is frozen at the revision
that wrote it — and the canonical-block compare that would flag the gap
ships inside the pinned clone, so it reads that same frozen list and passes.
Enrollment must therefore ride something the pin carries.

## Why the roster is declared

From `standards/build/distribution.md`, the Build port; Distribution
Channel's roster rule states "never inferred from the directory
listing", and nothing carries the reason.

A repo sitting under the workspace root is not thereby a consumer: repos land
there by cloning, vendoring, and experiment, and inferring governance from a
directory listing would make `git clone` an act of enrollment.

## Dogfooding, testable in place

From `standards/build/distribution.md`, the Build port; Distribution
Channel's Dogfood rule states the local block, and nothing carries the
reason.

dev-playbook consumes its own hook from the working tree via a
`repo: local` block in its `.pre-commit-config.yaml`, so detector edits are
testable in place before release.

## Acronyms

None.

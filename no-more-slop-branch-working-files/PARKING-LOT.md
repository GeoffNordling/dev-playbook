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

From `standards/build/python.md`, the Build port; worth keeping.
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

## Broken extension degrades, never aborts

From `standards/knowledge-organization/document-types.md`, the Knowledge
Organization port; okf-lint's `check_extension` docstring states the
same behavior, and no Standard names it.

- **Broken extension degrades, never aborts.** A malformed or empty extension
  table yields findings on that file (`knowledge-organization.registry-row`,
  `knowledge-organization.index-ordering`) while the rest of the repo is still
  fully checked.

## How okf-lint tells the registry from an extension

From `standards/knowledge-organization/document-types.md`, the Knowledge
Organization port; cited by nothing.

(okf-lint tells the two apart by the canonical consumer template, not by the
registry file's presence: only dev-playbook hosts that template, so a consumer's
extension never flips the audit into replacing the global registry.)

## Group terms under subheadings

From `standards/knowledge-organization/context-content.md`, the
Knowledge Organization port; cited by nothing.

- **Group terms under subheadings** when natural clusters emerge. If all
  terms belong to a single cohesive area, a flat list is fine.

## Create CONTEXT.md lazily

From `standards/knowledge-organization/context-content.md`, the
Knowledge Organization port; cited by nothing.

Create it lazily — when the first term is
resolved.

## VS Code and the two link forms

From `standards/knowledge-organization/cross-references.md`, the
Knowledge Organization port; cited by nothing.

VS Code does not expand `~/` in markdown links, and it resolves a leading
`/` against the filesystem root rather than the bundle root, so neither
form is clickable from the editor
([vscode#103542](https://github.com/microsoft/vscode/issues/103542)).
Accepted — agents are the primary audience, and both forms are what the
`ref-lint` linter (`/scripts/ref-lint`) validates.

## Why same-repo resolution is a written rule

From `standards/knowledge-organization/cross-references.md`, the
Knowledge Organization port; the wording's home is
`dotfiles/dot-claude/CLAUDE.md`, and Decision Record 0009 records the
same reasoning.

The written form is kept because no static path can encode this: the same
`~/workspace/<repo>/…` citation must resolve to a different checkout
depending on where the reader stands — a globally-loaded skill resolves a
dev-playbook citation to dev-playbook's main checkout from another repo's
worktree, but to the worktree when run inside a dev-playbook worktree — so
the meaning has to be a reader-side rule. `ref-lint` already resolves
same-repo citations this way, against the invoking checkout, so this rule
states at read time what the linter has enforced at commit time all along;
the [same-repo-resolution Decision Record](/docs/decisions/0009-same-repo-resolution.md)
records why the alternatives were rejected.

## The refinement step

From `standards/tracking/issue-authoring.md`, the Tracking port; the
Readiness rule keeps the bar and the one-crossing exemption, and the
intake and design skills carry the interview itself. Cited by nothing.

The refinement interview — intake, or the `design` node — is the **refinement
step** that carries a leaf to ready by authoring its brief; the issue-review
verdict at the beat's end is what releases it.

## Agents serve the work nodes

From `standards/tracking/factory-labels.md`, the Tracking port, which
renamed the file `label-scheme.md`; a fact about the factory, with no
rule in it. Cited by nothing.

The factory region's work nodes are served by typed agent definitions that the
traverse script launches — several of them at a review diamond. A
definition-region node is usually served by a slash-command of the same name
(`design` → `/design`), but that mapping is not guaranteed.

## Individual projects may supercede

From `standards/testing/conventions.md` and `standards/python/style.md`,
the Testing and Python ports; the same sentence with the same misspelling
opened both, and evicting it makes each Standard binding rather than a
default. Cited by nothing.

These are default testing conventions. Individual projects may supercede.

Default Python conventions for projects in this workspace. Individual
projects may supercede.

## Extract logic away from the non-deterministic boundary

From `standards/testing/conventions.md`, the Testing port; a candidate
home is [Module Design](/standards/modules/design.md), whose
`Designing for testability` list already states it. Testing keeps the
test half as No test of a non-deterministic decision.

When testing systems with non-deterministic components (LLM calls, network
requests, randomness), apply the Humble Object pattern: extract all testable
logic away from the non-deterministic boundary, leaving the non-deterministic
part as thin as possible.

## Ports (services you own, reached over the network)

From `standards/testing/conventions.md`, the Testing port; a candidate
home is [Module Design](/standards/modules/design.md), where
`3. Remote but owned (Ports & Adapters)` already states it. The one
sentence Testing keeps is "the double then sits at that seam", in The
lightest double.

A service you own but call over the network — an internal API, a queue
consumer — has no local stand-in to swap in and is too slow to call for real.
Give it a **port**: the interface at the seam, owned by the calling module. The
logic stays in that module; the transport is an injected **adapter** — an HTTP,
gRPC, or queue client in production, an in-memory adapter in tests.

## Integration tests trade speed for confidence

From `standards/testing/conventions.md`, the Testing port; rationale. The
rule half folded into The lightest double. Cited by nothing.

Integration tests that exercise the real dependency give the highest
confidence but are slower and harder to isolate.

## A deep mock is a design problem

From `standards/testing/conventions.md`, the Testing port; rationale about
the module. Mocks at boundaries only keeps the action, "deeper in the call
chain a fake takes its place". Cited by nothing.

Needing a mock deep inside the code under test signals a design problem —
extract an interface and use a fake instead.

## Why an initializer stays blank

From `standards/python/style.md`, the Python port; Python Style's Empty
rule states the emptiness, and nothing carries the reason.

Rationale: a blank `__init__.py` has no import-time side effects, surfaces the
true source of every name to readers and tooling, and avoids the
circular-import traps that grow with populated package initializers.

## Why a docstring earns its place

From `standards/python/style.md`, the Python port; cited by nothing.

Rationale: a name says what something is called; a docstring says what it
does. Readers (user and agent) should not have to read the body to learn
the contract.

## Why a hidden fallback costs more

From `standards/python/style.md`, the Python port; cited by nothing.

Rationale: a fallback that hides a bug delays the failure to a place far
from the cause, where it's much harder to diagnose. Failing at the point of
the missing value points straight at the defect.

## Why constants sit at the top

From `standards/python/style.md`, the Python port; cited by nothing.

Rationale: a reader scanning a new module wants to find its dependencies and
its tunable values without searching. Mixing constants into the body of the
file hides them — a reader who doesn't already know the constant exists
won't think to look for it past the first `def`. The cost of putting every
constant at the top is one scroll; the cost of hiding one is a bug that
slips past review because nobody saw it.

## Why 3.11 needs no future import

From `standards/python/style.md`, the Python port; Python Style's No
future annotations rule states the ban, and nothing carries the reason.

Python 3.11+ already provides every motivation: PEP 604 unions (`X | Y`),
builtin generics (`list[int]`), and string-quoted forward references.

## Asking for a future import

From `standards/python/style.md`, the Python port; cited by nothing.
`python.no-future-annotations` rejects the import unconditionally, so no
escape hatch exists to document.

If a future import is truly necessary, ask the user for permission.

## Why the helper bar is written down

From `standards/python/style.md`, the Python port; cited by nothing.

Rationale: every helper costs the reader a jump. Helpers that genuinely
encapsulate a concept pay that cost back; helpers that just relocate a few
lines don't. Pinning these criteria explicitly keeps review consistent —
without them, "should this be extracted?" becomes a matter of taste, and
codebases drift toward over-factored or under-factored extremes depending
on who reviewed last.

## Use the module vocabulary exactly

From `standards/modules/design.md`, the Modules port; cited by nothing.
Its population is an authored document or a review comment, not a
module. Its shape is Doc Conventions' Terminology rule; whether it
becomes a rule there is the Prose card's call.

Use these terms exactly — don't substitute "component," "service," "API," or
"boundary." Consistent language is the whole point.

## Rejected framings of depth

From `standards/modules/design.md`, the Modules port; cited by nothing.
Rationale for a vocabulary choice, and Doc Conventions' Current state and
next steps only bans rejected alternatives. The operative half of each
survives in a term definition: depth as leverage in Deep, not shallow,
and seam over boundary in Internal seams stay inside.

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.

## Interface design questions

From `standards/modules/design.md`, the Modules port; cited by nothing.
A writer's prompt in the second person; no state fails it.

When designing an interface, ask:

- Can you reduce the number of methods?
- Can you simplify the parameters?
- Can you hide more complexity inside?

## Small surface area

From `standards/modules/design.md`, the Modules port; cited by nothing.
Restates Deep, not shallow with no separate threshold.

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test setup.

## The date backfill

From `standards/decisions/records.md`, the Decisions port; cited by
nothing.

Records predating this key (introduced 2026-08-01) were backfilled from the
dates their own text or git history could prove, null otherwise.

## No deterministic check for immutability

From `standards/decisions/records.md`, the Decisions port; the rule to
lint join computes the same fact, and nothing else carries the warning.

There is deliberately no deterministic check for immutability; it is a rule
the reviewer upholds.

## The template is not a form

From `standards/decisions/records.md`, the Decisions port; Template's
body keeps "A Decision Record can be a single paragraph", and nothing
carries the reason.

The value is in recording *that* a decision was made and *why* — not in
filling out sections.

## Why an external evaluation is recorded

From `standards/decisions/records.md`, the Decisions port; What was
examined states the pin, and nothing carries the reason.

the record is what stops the same source being re-evaluated from scratch in
six months

## A judgment's case, and the content-addressed key

From `standards/semantic-validation/declarations.md`, the Semantic
Validation port; mechanism of the tooling, not a predicate over a
declaration. The key is built in `src/dev_playbook/judgments/core.py`;
a candidate home is
[the cache gate](/standards/semantic-validation/cache-gate.md), whose
`assert_judgment_cached` walkthrough now says "keys the named judgment"
with nothing behind it.

A declaration sets a judgment's **case** — its claim, files, and bench. It
does not set the **procedure**: every judgment is ruled through one fixed
judge prompt and output schema (constants in
[`src/dev_playbook/judgments/core.py`](/src/dev_playbook/judgments/core.py)),
uniform across all judgments, so there is nothing to declare for it.

The claim, the contents of every evidence and reference file, the bench, and
that fixed procedure together form a content-addressed **key**. The key is
what the cache is keyed on, so a judgment is re-judged exactly when one of
those inputs changes. The `id` (below) is a label only; it never enters the
key. Renaming an `id` with unchanged content stays a cache hit; changing
content under the same `id` is a miss.

## The key is root-invariant

From `standards/semantic-validation/declarations.md`, the Semantic
Validation port; mechanism, and the sentence depends on the key entry
above. The Standard's lead prose keeps the `root` definition, which is
the population's boundary; nothing carries this consequence.

Because the key is **root-invariant** (the root only *locates* files; it
never enters the key), the same judgment caches identically across worktrees
and checkouts.

## Why a judgment is spent sparingly

From `standards/semantic-validation/declarations.md`, the Semantic
Validation port; rationale and a writer's heuristic behind The bar,
which keeps the predicate. Cited through `#the-bar` by
`dotfiles/dot-claude/agents/build.md` and
`dotfiles/dot-claude/agents/doc-pr-review.md`.

A judgment is expensive — every sweep re-judges it whenever the bytes of any
input change, and each re-run is a fresh chance for a stochastic false
refutation someone must weigh — so it is spent only where it buys the most.
When in doubt, do not add one.

## Who maintains a declaration

From `standards/semantic-validation/declarations.md`, its Maintenance
section, the Semantic Validation port; process, not a predicate over a
declaration. `dotfiles/dot-claude/agents/build.md` carries the
same-change duty and `software-factory/factory-operations.md` the
no-judge-in-a-node rule.

Declarations are peer documentation: whoever edits an artifact updates,
removes, or adds the declarations that describe it in the same change — and
never runs judges or touches the cache; judging belongs to the periodic
`judgments-sweep`. Kept this way, the sweep opens on declarations that mean
what they say.

## The governed artifact rides review

From `standards/harness/claude-content.md`, the Harness port; Global
file names the source path, and nothing carries the reason. Cited by
nothing.

In this workspace it is not authored in place — its source is
`dotfiles/dot-claude/CLAUDE.md`, Stow-symlinked into `~/.claude/`, so the
governed artifact lives in dev-playbook and rides the normal review path.

## Behaviors are required

From `standards/harness/claude-content.md`, the Harness port; Required
rules names the headings, and nothing carries the reason. Cited by
nothing.

Behaviors are `REQUIRED`, because no repo file restates them and this is
the only place they can be placed

## The global file's citation form

From `standards/harness/claude-content.md`, the Harness port; a
Knowledge Organization matter: ref-lint treats the global file as
fixed-root, Cross-References does not. Cited by nothing.

Their workspace paths are backticked prose rather than live citations, since
a citation would be `wrong-form` inside dev-playbook itself
([cross-references.md](/standards/knowledge-organization/cross-references.md)).

## A new front matter field is an amendment

From `standards/harness/runbook-conventions.md`, the Harness port; Front
matter's predicate holds the closed set. Cited by nothing.

These eight fields are the whole skill vocabulary; a new one requires an
edit here before its first use.

These five fields are the whole agent vocabulary; a new one requires an
edit here before its first use.

## Related skills share a prefix

From `standards/harness/runbook-conventions.md`, the Harness port; a
heuristic with no test for "related". Cited by nothing.

Related skills share a namespace prefix.

## A card may have more than one detector

From `standards/standard/detectors.md`, the Meta-Standard port;
Card-namespaced rule ids carries the one-to-one invariant, Card
Catalog's Audit rule the `none` cell. Cited by nothing.

- **A card may have more than one detector.** Cards are organized by the question they govern; detectors by the mechanism they run. Question and mechanism cross-cut, so the relation is one-to-many: one question can need several mechanisms (a card cited by more than one detector), and one mechanism can serve several questions (a detector cited by more than one card). The one-to-one invariant lives a level down, at the rule — every `card.rule` id belongs to exactly one card. A card may still audit `none` when no automatic check exists.

## Drift at the fine grain

From `standards/standard/detectors.md`, the Meta-Standard port; the
cache is The Cache Gate's. Cited by nothing.

Standards drift, each grain with its own detector:

1. **Fine grain** — a specific document or passage must keep meaning what it meant when validated. [Judgments](/standards/semantic-validation/index.md) cover this: the content-addressed cache expires a verdict the moment the underlying bytes change.

## Drift at the contract grain

From `standards/standard/detectors.md`, the Meta-Standard port; the
state half is Distribution Channel's A pinned rev, and nothing carries
the rework obligation. Cited by nothing.

2. **Contract grain** — a change to a define cell obligates rework across the standard's adopting population. For a workspace-scoped standard that population is every repo in the workspace: a version bump propagated and verified by workspace-lint. For a repo-scoped standard the adopting population is the host repo itself, so no workspace-lint obligation attaches — the rework lands in the same repo as the define-cell change.

## Declare a type only when a population carries it

From `standards/standard/consuming.md`, the Meta-Standard port; a
heuristic Type Registry lacks. Cited by nothing.

- Declare a type only when a population of documents actually carries it — a vocabulary word earns its place by the documents that use it, and it stays as local as that population.

## The two vocabularies are closed

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; the Front matter predicate already says `exactly`.
Cited by nothing.

The two vocabularies are closed: the fields above are all of them.

## The description is the invocation match surface

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; rationale and three writer's heuristics. Writing for
Agents' [Context pointers](/standards/harness/writing-for-agents.md#context-pointers)
already carries the three verbatim.

The two-sentence form is the invocation match surface, the context pointer the agent reads to reach the runbook, so it is specific, and every word of it costs on every turn:

- **Front-load the leading word.** The pointer is where it does its triggering work.
- **One trigger per branch.** Synonyms that rename a single branch are one branch written twice; collapse them and keep only genuinely distinct branches.
- **Cut identity the body already carries.**

## The two levers of a completion criterion

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; a summary of what Writing for Agents'
[Steps and completion criteria](/standards/harness/writing-for-agents.md#steps-and-completion-criteria)
explains at length. Cited by nothing.

The criterion's clarity, whether the agent can tell done from not-done, and its demand, how much it requires, are the two levers Writing for Agents explains.

## Why material spills into references/

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; the context-cost reason behind Bundle layout. Cited
by nothing.

... so the agent loads each file on demand instead of paying the context cost up front.

## When to reach for allowed-tools and disallowed-tools

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; a writer's heuristic for choosing between the two
fields. Cited by nothing.

`allowed-tools` pre-approves the listed calls to run without prompting, the form for a focused, mechanical skill; `disallowed-tools` denies outright, the form for a stance that must be enforced rather than asked for.

## Why an argument's name carries its meaning

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; the reason behind the bare-name form. Cited by
nothing.

Every argument is a string, so the name alone carries the meaning, for the user and for the [Reference chain](/doc-types/runbook/contract-shape.md).

## The lazy-load pattern assumes a flat tree

From `standards/harness/runbook-conventions.md`, the Harness port,
scrubbed at review; the reason behind References one level deep. Cited
by nothing.

The lazy-load pattern assumes a flat tree: the agent loads each file on demand from `SKILL.md`.

## Leverage and locality

From `standards/modules/design.md`, the Modules port, scrubbed at
review; the payoff argument for depth, and the Glossary entries for two
terms no rule in the Standard uses. Cited by nothing.

Depth pays out twice. **Leverage** is what callers get: more capability per unit of interface they learn, so one implementation pays back across N call sites and M tests. **Locality** is what maintainers get: change, bugs, knowledge, and verification concentrate in one place instead of spreading across callers, so a fix lands once and holds everywhere.

## Acronyms

None.

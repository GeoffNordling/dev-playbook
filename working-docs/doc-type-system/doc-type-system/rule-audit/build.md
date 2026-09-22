---
type: General-Sheet
title: Build Family Rule Audit
description: The rule audit over the build/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Build Family Rule Audit

The `standards/build/` family declares 26 rules across three Standards,
[File Skeleton](/standards/build/skeleton.md) (13),
[Canonical Artifacts](/standards/build/canonical.md) (9), and
[The Python Project](/standards/build/python.md) (4). One rule moves from
deterministic to stochastic, `build.one-version-set`, whose predicate asks
whether each pin is the latest upstream release — a fact no file in the repo
carries; none moves the other way. Two rules break in this repo:
`build.entry-points`, which demands `<package>.cli:main` while
`pyproject.toml` declares `dev_playbook.cloa_viewer.cli:main`, and
`build.name-mapping`, which names "the repo directory's name" while the
detector and the repo both use the canonical repo name that a worktree
shares with its main checkout. Three rules are weakly checked,
`build.name-mapping`, `build.pre-commit-configyaml`, and
`build.the-source-directory`. Three rules are low value,
`build.javascript`, `build.lockfile-committed`, and `build.artifactsmk`.
Eight rules have no check at all: the four condition rules
(`build.python`, `build.python-package`, `build.python-source`,
`build.scripts`, whose conditions `scripts/repo-lint` computes but never
emits, which is correct for a condition), plus `build.artifactsmk`,
`build.entry-points`, `build.javascript`, and `build.one-version-set`.
One script decides the family, `scripts/repo-lint`. The population is
"a governed repo's tree", and only one member, dev-playbook itself, is
visible from this repo; every `holds` below is read off that one member.

## Rules

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `build.required-files` | "`README.md`, `CLAUDE.md`, `index.md`, `.gitignore`, `.pre-commit-config.yaml`, and `Makefile` exist at the root, and `.github/workflows/ci.yml` exists." | deterministic | deterministic | full | holds | none | high | Test: seven paths are files. `repo-lint` `BASE_REQUIRED` in `check_presence`. All seven present at the root. |
| `build.root-only-files` | "`pyproject.toml`, `CONTEXT.md`, and `CANDIDATES.md` appear at the root or not at all, one of each." | deterministic | deterministic | full | holds | none | high | Test: no git-listed file of those three names sits below the root. Only `standards/build/canonical/pyproject.toml` does, and the population excludes that directory. |
| `build.no-other-future-work-file` | "No file named `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or `IDEAS.md` exists at any depth in the tree." | deterministic | deterministic | full | holds | none | high | Test: no basename in the set appears in `git ls-files`. `git ls-files` finds none. |
| `build.runnables-live-in-scripts` | "No `bin/` directory and no `tools/` directory exists at the root." | deterministic | deterministic | full | holds | none | high | Test: `<root>/bin` and `<root>/tools` are not directories. Neither exists. |
| `build.dependencies-live-in-pyprojecttoml` | "No file named `requirements.txt` exists anywhere in the tree." | deterministic | deterministic | full | holds | none | high | Test: no `requirements.txt` basename in `git ls-files`. None found. |
| `build.python` | "A repo in which `pyproject.toml` exists at the root." | deterministic | deterministic | none | holds | none | high | Condition, not an obligation. `infer_layers` computes the same test and emits no id, which is right for a condition. |
| `build.uvlock-and-python-version` | "`uv.lock` is tracked and `.python-version` exists, both at the root." | deterministic | deterministic | full | holds | none | high | Test: `uv.lock` in `git ls-files --cached`, `.python-version` is a file. Both true. |
| `build.python-package` | "A Python repo in which `src/` exists." | deterministic | deterministic | none | holds | `build.python-source` | high | Condition. Subsumed by `build.python-source`'s first disjunct, which is the same conjunction. |
| `build.one-package-under-src` | "`src/` holds exactly one entry: a directory whose name is the import package the name mapping names." | deterministic | deterministic | full | holds | none | high | Test: children of `src/` equal `{package_name(repo)}`. `src/` holds `dev_playbook` alone. |
| `build.python-source` | "A repo in which `src/` exists beside a root `pyproject.toml`, or `scripts/` holds a Python file." | deterministic | deterministic | none | holds | `build.python-package` | high | Condition. Strict superset of `build.python-package`; this one subsumes it. |
| `build.tests-present` | "`tests/` exists and is not empty." | deterministic | deterministic | full | holds | none | high | Test: some git-listed path starts with `tests/`. `tests/` holds 22 entries. |
| `build.javascript` | "A repo in which `package.json` exists at the root." | deterministic | deterministic | none | holds | none | low | Condition, vacuously true here: the only `package.json` is at `src/dev_playbook/cloa_viewer/web/`, so no governed repo enters the layer. |
| `build.lockfile-committed` | "A lockfile, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, or `bun.lockb`, is tracked beside `package.json`." | deterministic | deterministic | full | holds | none | low | Vacuous: no member is in the JavaScript layer. The repo's real JS project sits inside the Python package, where the rule never reaches. |
| `build.ciyml` | "`.github/workflows/ci.yml` is byte-identical to the canonical ci.yml." | deterministic | deterministic | full | holds | none | high | Test: `read_bytes()` equality. `cmp` of the two files reports no difference. |
| `build.python-version` | "`.python-version` is byte-identical to the canonical .python-version." | deterministic | deterministic | full | holds | none | high | Test: `read_bytes()` equality. `cmp` reports no difference; both hold `3.14`. |
| `build.pre-commit-configyaml` | "`.pre-commit-config.yaml` holds every block of the canonical .pre-commit-config.yaml verbatim and in order; hooks may follow inside a block, further `repo:` blocks may sit between blocks, and the line pinning the dev-playbook `rev` carries the consumer's own value." | deterministic | deterministic | weak | holds | `distribution.a-pinned-rev` | high | The hook-repo exemption drops the whole first segment, so `default_install_hook_types:` and `repos:` go unchecked here. See Escalations. |
| `build.makefile` | "`Makefile` holds the targets of its layer's fragment verbatim and unbroken, Makefile.base in a repo with no root `pyproject.toml` or Makefile.python in a repo with one, with `<code-roots>` replaced by whichever of `src`, `tests`, and `scripts` hold a `.py` file, in that order; further targets may follow." | deterministic | deterministic | full | holds | none | high | Test: the substituted fragment appears as one contiguous run. `scripts/` holds no `.py`, so `<code-roots>` is `src tests`, which the Makefile has. |
| `build.artifactsmk` | "`artifacts.mk`, where it exists at the root, sets `ARTIFACTS` to a list of files and gives each one a rule whose target is that file's path." | deterministic | deterministic | none | holds | none | low | Verifier row is null. `artifacts.mk` sets `ARTIFACTS := $(WEB)/dist/index.html` and gives that path a rule. `make` already fails loud on a missing rule. |
| `build.pyprojecttoml` | "`pyproject.toml` parses as TOML and matches every value the canonical pyproject.toml pins: `project.requires-python`, `tool.pytest.ini_options.testpaths`, `tool.ruff.target-version`, `tool.ruff.line-length`, `tool.ruff.lint.select`, `tool.ruff.lint.ignore`, `tool.ruff.lint.pydocstyle.convention`, and every `[tool.mypy]` key." | deterministic | deterministic | full | holds | `build.name-mapping` | high | Every pinned value matches. The `project.name` clause is tested but emitted under `build.name-mapping`, so the two rules state one fact twice. |
| `build.gitignore` | "`.gitignore` holds every pattern of the canonical .gitignore; comments and order are free, and further patterns may follow." | deterministic | deterministic | full | holds | none | high | Test: canonical non-comment patterns are a subset of the copy's. All eight baseline patterns present. |
| `build.one-version-set` | "Every version the canonical artifacts pin, the Python interpreter, ruff, mypy, pytest, and each hook `rev`, is the latest stable release." | deterministic | stochastic | none | unknown | none | high | "Latest stable release" is upstream state; no repo file holds it. Cannot be decided here. See Escalations. |
| `build.the-source-directory` | "Every file directly under `standards/build/canonical/` is one a rule of this Standard names, and every file a rule of this Standard names is directly under `standards/build/canonical/`." | deterministic | deterministic | weak | holds | none | high | The compare is against `CANONICAL_MANIFEST`, a literal in `scripts/repo-lint`, not against this Standard's rules. See Escalations. |
| `build.name-mapping` | "The root `pyproject.toml` sets `project.name` to the repo directory's name lowercased, `My-Repo` → `my-repo`, and the import package is that name with each hyphen an underscore, `my_repo`." | deterministic | deterministic | weak | breaks | `build.pyprojecttoml` | high | "The repo directory's name" is `doc-type-system-refactor` in this worktree; `project.name` is `dev-playbook`. See Escalations. |
| `build.entry-points` | "`[project.scripts]` in the root `pyproject.toml` is absent, or every entry under it has the value `<package>.cli:main`, where `<package>` is the import package and `src/<package>/cli.py` defines `main`." | deterministic | deterministic | none | breaks | none | high | `pyproject.toml:10` declares `dev_playbook.cloa_viewer.cli:main`, and `src/dev_playbook/cli.py` does not exist. See Escalations. |
| `build.scripts` | "A Python file under `scripts/`: a file whose name ends in `.py`, or a file with no extension whose first line is a Python shebang." | deterministic | deterministic | none | holds | none | high | Condition. `pyast.looks_python` implements exactly this test. The condition swaps the member from the Python project to one file, which the Standard's population phrase does not cover. |
| `build.shebang-and-inline-metadata` | "An executable Python file under `scripts/` has `#!/usr/bin/env -S uv run --script` as its first line and carries a PEP 723 inline metadata block opened by a line reading `# /// script`; where the repo has a root `.python-version`, that block's `requires-python` value is `>=` followed by the contents of `.python-version`, `>=3.13` for a `.python-version` of `3.13`." | deterministic | deterministic | full | holds | none | high | Test: first line, `# /// script` present, declared floor equals `>=` plus `.python-version`. All 21 executable files in `scripts/` pass. |

## Escalations

### `build.name-mapping` — "The root `pyproject.toml` sets `project.name` to the repo directory's name lowercased, `My-Repo` → `my-repo`, and the import package is that name with each hyphen an underscore, `my_repo`."

**Breaks.** The predicate names "the repo directory's name". This audit runs
in a linked worktree whose directory is
`.claude/worktrees/doc-type-system-refactor`, so the repo directory's name is
`doc-type-system-refactor`. `pyproject.toml:2` sets
`name = "dev-playbook"`. Read literally, the member fails.

The detector does not use the directory name. `scripts/repo-lint` calls
`gitrepo.canonical_repo_name(root)`, which runs
`git rev-parse --git-common-dir` and takes that directory's parent, so it
answers `dev-playbook` from the main checkout and from every worktree alike.
The module docstring of `src/dev_playbook/gitrepo.py` states the intent in its
first paragraph: "which repo is the invoking checkout a working copy of
(identical answer from the main checkout and any worktree of it)". The code is
the detector, and the code disagrees with the predicate's words.

**Weak.** The predicate carries two clauses. Only the first,
`project.name`, is emitted under this id, by the
`pin("project.name", project_name(repo_name), NAME_MAPPING)` call in
`check_pyproject`. The second clause, that the import package is the project
name with each hyphen an underscore, is never emitted under
`build.name-mapping`. It is tested elsewhere, under
`build.one-package-under-src` (the `src/` child name) and under
`build.pyprojecttoml` (`tool.ruff.lint.isort.known-first-party`), so the fact
is checked but the rule id does not cover what its own sentence says.

**Proposal.** Rewrite the predicate. The repo's behavior is deliberate — the
whole `gitrepo` module exists to make a worktree answer the same name as its
main checkout — so changing the repo would break the worktree workflow the
workspace runs on. New sentence: "The root `pyproject.toml` sets
`project.name` to the repository's own name lowercased, the directory holding
the shared `.git` and therefore the same from the main checkout and from every
worktree, `My-Repo` → `my-repo`, and the import package is that name with each
hyphen an underscore, `my_repo`."

### `build.entry-points` — "`[project.scripts]` in the root `pyproject.toml` is absent, or every entry under it has the value `<package>.cli:main`, where `<package>` is the import package and `src/<package>/cli.py` defines `main`."

**Breaks.** `pyproject.toml:9-10` reads:

```
[project.scripts]
cloa-viewer = "dev_playbook.cloa_viewer.cli:main"
```

The import package is `dev_playbook`, so the predicate demands the value
`dev_playbook.cli:main` and a file `src/dev_playbook/cli.py` defining `main`.
Neither holds: the value names a submodule, and `src/dev_playbook/cli.py` does
not exist. The function the entry does name is real —
`src/dev_playbook/cloa_viewer/cli.py:120` defines
`def main(argv: list[str] | None = None) -> int`.

Nothing caught this. `standards/verifiers.yaml:8` maps
`build.entry-points` to `null`, and `build.entry-points` is not among the 21
ids in `scripts/repo-lint`'s `RULES` tuple.

**Proposal.** Rewrite the predicate. The repo plainly wants one CLI per
subpackage, not one CLI per repo: `cloa_viewer` is a self-contained tool with
its own `cli.py`, `server.py`, and `web/` tree, and forcing its entry through
a repo-level `src/dev_playbook/cli.py` shim would add a file that does
nothing. New sentence: "`[project.scripts]` in the root `pyproject.toml` is
absent, or every entry under it has the value `<module>:main`, where
`<module>` is a module inside the import package and that module defines
`main`." The rewritten predicate stays deterministic — resolve the dotted
module to a path under `src/` and read the file's AST for a top-level `main`.

### `build.pre-commit-configyaml` — "`.pre-commit-config.yaml` holds every block of the canonical .pre-commit-config.yaml verbatim and in order; hooks may follow inside a block, further `repo:` blocks may sit between blocks, and the line pinning the dev-playbook `rev` carries the consumer's own value."

**Weak.** The predicate exempts one thing from the repo that carries
`standards/build/canonical/`: "the block holding that `rev`". The code exempts
more. `config_segments` in `scripts/repo-lint` splits the canonical text at
each line starting `  - repo:` and attaches everything before the first such
line to the first segment. The canonical file's first segment is therefore:

```
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: <pinned-sha>
    hooks:
      - id: playbook-lint
```

`check_precommit_config` then runs `if hook_repo and any(REV_PLACEHOLDER in
line for line in segment): continue`, which skips all six lines. In
dev-playbook, `default_install_hook_types: [pre-commit, pre-push]` and
`repos:` are never compared against the canonical file. Both happen to be
correct today, at `.pre-commit-config.yaml:8-9`, so the state holds; the check
would not notice if either changed. In a consumer repo the segment is
compared, so the weakness is dev-playbook's alone — which is the repo that
authors the canonical file.

### `build.the-source-directory` — "Every file directly under `standards/build/canonical/` is one a rule of this Standard names, and every file a rule of this Standard names is directly under `standards/build/canonical/`."

**Weak.** The predicate compares the directory against the rules of
[Canonical Artifacts](/standards/build/canonical.md). The code compares it
against `CANONICAL_MANIFEST`, a `frozenset` literal in `scripts/repo-lint`
holding seven names: `ci.yml`, `.python-version`, `.pre-commit-config.yaml`,
`pyproject.toml`, `Makefile.base`, `Makefile.python`, `.gitignore`.
`check_canonical_artifacts` diffs the directory listing against that set in
both directions and emits `build.the-source-directory` for each difference.

What the code cannot see is the half of the predicate that reads the Standard.
Add a rule to `canonical.md` naming an eighth artifact and the manifest does
not learn about it; delete a rule and the manifest still demands its file. The
Standard and the script agree today — the seven names on disk are exactly the
seven the rules name — but nothing checks that agreement.

One sign of the drift already: the docstring of `check_canonical_artifacts` in
`scripts/repo-lint` says "only it owns the ten canonical artifacts", while the
manifest holds seven.

### `build.one-version-set` — "Every version the canonical artifacts pin, the Python interpreter, ruff, mypy, pytest, and each hook `rev`, is the latest stable release."

**Reclassify, deterministic to stochastic.** The trailer says
`deterministic`. A deterministic rule is one a script that reads only files in
the repo can decide with no judgment call
([Detectors](/standards/standard/detectors.md)). This predicate compares each
pin to the latest stable release upstream. No file in the repo states what
that release is. The pins themselves are
`.python-version` `3.14`; `standards/build/canonical/pyproject.toml`
`mypy>=2.0`, `pytest>=9.0`, `ruff>=0.15.20`; and
`standards/build/canonical/.pre-commit-config.yaml` `rev: v0.15.20`,
`rev: v0.11.0.1`, `rev: v4.0.0`. Deciding the rule means asking PyPI, GitHub,
and python.org, which a read-only repo script cannot do.

The verifier row is `null`, which is consistent, and no tool in the repo fills
the gap: `src/dev_playbook/bump_pins.py` moves a consumer's dev-playbook
`rev`, a different question entirely — its own docstring calls the network
step "the only step that touches the network", and that step runs the gate,
not a release lookup.

State is `unknown` for the same reason: this audit cannot reach upstream to
compare.

## Detectors

**`scripts/repo-lint`.** The one detector of the family. It infers the repo's
layers from facts on disk (`infer_layers`: `python` from a root
`pyproject.toml`, `src` from `pyproject.toml` and `src/` together,
`scripts` from any Python file under `scripts/`, `js` from a root
`package.json`), then runs ten checks and two conditional self-audits. It
decides 18 of the family's 26 rules and three ids belonging to other families
(`distribution.a-publisher-dogfoods-its-manifest`,
`knowledge-organization.h1`, `knowledge-organization.the-language-section`).
Canonical compares come at four strengths: byte-identical (`ci.yml`,
`.python-version`), verbatim line runs (`.pre-commit-config.yaml`, the
`Makefile`), baseline pattern subset (`.gitignore`), and parsed TOML values
(`pyproject.toml`). Two details worth the design pass's attention: the script
holds all of its rule logic itself, unlike the thin-shim pattern its sibling
scripts follow; and `line_matches` right-strips both sides, so trailing
whitespace drift passes a compare the rule calls "verbatim".

**`src/dev_playbook/gitrepo.py`.** Supplies `repo-lint` with the two facts it
starts from. `canonical_repo_name` reads `git rev-parse --git-common-dir` and
returns that directory's parent name, so a worktree and its main checkout
answer alike — this is what `build.name-mapping` and
`build.one-package-under-src` compare against. `git_files` lists the checkout
through `git ls-files`, honoring `.gitignore`, with `tracked_only` for the
"must be committed" rules, `build.uvlock-and-python-version` and
`build.lockfile-committed`. Every call runs under `no_git_env()`, which strips
the variables git itself reports as naming a repository.

**`src/dev_playbook/pyast.py`.** Supplies the Python-file discovery behind the
`scripts` layer. `looks_python` returns true for a `.py` file or an
extensionless file whose first line starts with a Python or
`uv run --script` shebang, which is the `build.scripts` condition stated in
code. `find_python_files` runs the same gitignore-aware `git ls-files` walk
and filters it through `looks_python`; its results drive both
`build.shebang-and-inline-metadata` and the `<code-roots>` substitution in the
`build.makefile` compare.

**`src/dev_playbook/findings.py`.** Renders each finding as
`location:line: <rule id> message` and prints the `--list-rules` output.
It decides no rule of this family; it fixes the shape
`standard.finding-format` and `standard.list-rules` require.

## Acronyms

- **AST** — Abstract Syntax Tree.
- **CLI** — Command-Line Interface.
- **JS** — JavaScript.
- **PEP** — Python Enhancement Proposal.
- **TOML** — Tom's Obvious Minimal Language.

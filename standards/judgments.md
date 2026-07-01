---
type: Standard
title: Judgments
description: LLM-judged assertions on files, declared in YAML, cached by content hash, proven through a pytest gate
---

# Judgments

A **judgment** is a single yes/no question about one or more files, ruled on by
an LLM judge — for example, *"docs/errors.md lists every exception type that
src/exceptions.py raises."* A judgment is declared as data on disk; a fast,
deterministic pytest gate then passes a judgment **iff its exact content has
already been judged-and-passed**, and a separate `run-judgments` skill fills the
cache by actually running the judge on the misses. This standard is for a repo author
adding judgments to their own repo.

## What a judgment is

A judgment has four parts:

- **claim** — the proposition to rule on, in prose.
- **evidence** — the files under judgment; what the judge is ruling on.
- **reference** — optional files the judge may consult for context but are not judged.
- **instrument** — the `model` and `effort` the judge runs under.

A declaration sets a judgment's **case** — its claim, files, and instrument. It
does not set the **judge**: every judgment is ruled through one fixed judge prompt
and output schema (constants in [`tools/src/judgments/core.py`](/tools/src/judgments/core.py)),
uniform across all judgments, so there is nothing to declare for them.

The claim, the contents of every evidence and reference file, the instrument, and
that fixed prompt and schema together form a content-addressed **key**. The key is
what the cache is keyed on, so a judgment is re-judged exactly when one of those
inputs changes — and not otherwise. The `id` (below) is a label only; it never
enters the key. Renaming an `id` with unchanged content stays a cache hit;
changing content under the same `id` is a miss.

## The YAML declaration format

A repo declares its judgments in one or more YAML files. Each file has a single
top-level key `judgments:` whose value is a list of judgment objects:

```yaml
judgments:
  - id: errors-exhaustive
    claim: |
      docs/errors.md lists every exception type that src/exceptions.py raises.
    evidence:  [docs/errors.md]          # files under judgment
    reference: [src/exceptions.py]        # consulted, not judged (optional)
    model: claude-sonnet-4-6
    effort: high
```

Every field rule is a hard, fail-loud error naming the offending `id` (or file):

| field | required | rule |
|---|---|---|
| `id` | yes | non-empty string, charset `[A-Za-z0-9._-]`, **globally unique across all of the repo's declaration files** (it is a CLI argument and a cache/report handle). |
| `claim` | yes | non-empty string. |
| `evidence` | yes | list of **≥1** repo-root-relative path strings. |
| `reference` | no | list of repo-root-relative path strings; omit or `[]` for none. |
| `model` | yes | string in `VALID_MODELS` (see [Instruments](#instruments)). |
| `effort` | yes | string in `VALID_EFFORTS` (see [Instruments](#instruments)). |

Paths are **relative to the repo root** (see [Config and root resolution](#config-and-root-resolution)),
never to the YAML file's own location. Each must be a relative path — no absolute
path, no `..` segment — that points to an existing file.

## Config and root resolution

A repo opts in via a `[tool.judgments]` table in its `pyproject.toml`:

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]   # globs (relative to root) locating the declaration files
```

- **`paths`** — required list of globs, expanded relative to the root to find the
  declaration files. A `[tool.judgments]` table that is present but declares no
  `paths` (or an empty `paths`) is a hard configuration error: the repo opted in
  but pointed nowhere.
- **`root`** — the nearest ancestor directory of the current working directory
  that contains a `pyproject.toml` with a `[tool.judgments]` table. All `paths`
  globs and all evidence/reference paths resolve against this root.

Because the key is **root-invariant** (the root only *locates* files; it never
enters the key), the same judgment caches identically across worktrees and
checkouts.

If no `[tool.judgments]` table is found anywhere up the tree, there are **no
judgments**.

## Instruments

A judgment's instrument is its `model` and `effort`. The valid values are the
single source of truth in
[`tools/src/judgments/instruments.py`](/tools/src/judgments/instruments.py)
(`VALID_MODELS`, `VALID_EFFORTS`); a `model` or `effort` outside it is a
fail-loud error.

## The pytest cache-gate

Every judgment is a **pytest** whose body does only a deterministic, offline
cache check — no LLM, no network, no API key:

```python
from judgments.pytest_support import assert_judgment_cached


def test_errors_exhaustive():
    assert_judgment_cached("errors-exhaustive")
```

`assert_judgment_cached(id)` resolves the root, keys the named judgment, and asks
the seen-set whether that exact content has been judged-and-passed:

- **cache hit → the test passes.** The judgment's content has already been ruled
  true by the judge.
- **cache miss → the test fails** with `judgment '<id>': cache miss`. The content
  is new or changed and needs the `run-judgments` skill to run it.
- an unknown `id`, or an unreadable evidence file, surfaces as a loud test error,
  never a silent pass.

A repo can instead cover **all** its judgments with one parametrized test,
enumerating ids through the loader:

```python
import pytest
from judgments.loader import load, resolve_root
from judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

So `pytest` is a fast gate: green means every judgment's current content is
already cached as passing. Filling the cache — running the judge on the misses
and recording the passes — is the job of the `run-judgments` skill, the only
place an LLM ever runs. It has to be a skill — thin harness instructions —
because subscription billing requires running the judges through the harness
interactively. A judgment whose judge returns *false* is never recorded, so it stays a
permanent miss (a permanent failing test) until the underlying content is fixed.

## Consuming judgments from another repo

The judgments tooling lives in dev-playbook's `tools/` directory as an
installable package, **`dev-playbook-tools`**, that exposes the `judgments` and
`skipcache` import packages and the `judgments-run` / `judgments-lint` console
scripts. Any repo on the same machine consumes it as a **local path
dependency** — no network, no PyPI, no published index. The recipe below is
end-to-end; the field rules, config, and gate it points at are the same ones a
repo author uses above.

### 1. Add the package as an editable path dependency

In the consuming repo's `pyproject.toml`, depend on `dev-playbook-tools` and
point a `[tool.uv.sources]` entry at dev-playbook's `tools/` directory on disk:

```toml
[dependency-groups]
dev = ["dev-playbook-tools"]

[tool.uv.sources]
dev-playbook-tools = { path = "../dev-playbook/tools", editable = true }
```

Adjust `path` to wherever `dev-playbook` sits relative to the consumer. The
dependency is `editable`, so the consumer always resolves against the current
`tools/` source — nothing to re-publish or re-pin when the libraries change.
`uv sync` builds the package with uv's own bundled build backend, so building
it needs no network or PyPI access. Its one runtime dependency, `pyyaml`,
resolves from uv's local cache whenever it is present (it almost always is);
only a completely cold cache reaches PyPI for it. Afterwards `from
judgments.pytest_support import assert_judgment_cached` resolves in the
consumer's environment and `judgments-run` is on its venv PATH.

### 2. Declare the repo's judgments

Opt in exactly as a repo author does (see [Config and root
resolution](#config-and-root-resolution) and [The YAML declaration
format](#the-yaml-declaration-format)): a `[tool.judgments]` table in the
consumer's own `pyproject.toml` and one or more declaration YAML files.

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]
```

The root is the consumer's own repo — the nearest ancestor with a
`[tool.judgments]` table — and every evidence/reference path resolves against
it.

### 3. Gate the judgments in pytest

Add the cache-gate as an ordinary test in the consumer's suite (see [The pytest
cache-gate](#the-pytest-cache-gate)):

```python
import pytest
from judgments.loader import load, resolve_root
from judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

The check is deterministic and offline; it reads the same machine-local seen-set
the `run-judgments` skill fills, so it needs no LLM and no API key on CI.

### 4. Lint the declarations on commit

Add the `judgments-lint` pre-commit hook so malformed or stale declarations fail
fast. It ships from dev-playbook's published hook manifest; reference it by URL
and pinned `rev`, exactly as for the other dev-playbook hooks:

```yaml
- repo: https://github.com/GeoffNordling/dev-playbook
  rev: <commit-sha>
  hooks:
    - id: judgments-lint
```

The hook runs from pre-commit's own clone of dev-playbook at the pinned `rev`
and self-bootstraps its imports, so it needs neither the installed package nor a
checkout path — it is independent of the editable dependency in step 1.

### 5. Fill the cache with the run-judgments skill

A cache miss — a failing gate — is filled by the global `run-judgments` skill:
it runs the LLM judge on each miss and records the passing verdicts into the
machine-local seen-set. The skill is available in any repo on the machine; run
it whenever the cache-gate is red.

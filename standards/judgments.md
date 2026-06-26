# Judgments

A **judgment** is a single yes/no question about one or more files, ruled on by
an LLM judge — for example, *"docs/errors.md lists every exception type that
src/exceptions.py raises."* You declare judgments as data on disk; a fast,
deterministic pytest gate then passes a judgment **iff its exact content has
already been judged-and-passed**, and a separate judge skill fills the cache by
actually running the judge on the misses.

This document is for a repo author adding judgments to their own repo. It covers
the YAML declaration format, the `[tool.judgments]` config and root resolution,
the valid instrument values, and how the pytest cache-gate works.

## What a judgment is

A judgment has four parts:

- **claim** — the proposition to rule on, in prose.
- **evidence** — the files under judgment; what the judge is ruling on.
- **reference** — optional files the judge may consult for context but does not
  itself judge.
- **instrument** — the `model` and `effort` the judge runs under.

The claim, the contents of every evidence and reference file, and the instrument
together form a content-addressed **key**. The key is what the cache is keyed on,
so a judgment is re-judged exactly when one of those inputs changes — and not
otherwise. The `id` (below) is a label only; it never enters the key. Renaming an
`id` with unchanged content stays a cache hit; changing content under the same
`id` is a miss.

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
| `model` | yes | string in `VALID_MODELS` (see [Instruments](#instruments)). **No default — required on every judgment.** |
| `effort` | yes | string in `VALID_EFFORTS` (see [Instruments](#instruments)). **No default — required on every judgment.** |

Paths are **relative to the repo root** (see [Config and root resolution](#config-and-root-resolution)),
never to the YAML file's own location.

Path checking is layered by design:

- the **loader** validates only YAML structure and field values, and does *no*
  file I/O on the declared paths;
- the **lint** (`judgments-lint`) statically pre-checks that each path is
  relative (not absolute, no `..`) and exists;
- `judgments.prepare` is the authoritative runtime enforcer (absolute / `..` /
  symlink-escape / missing / non-UTF-8).

The overlap between the lint and `prepare` is intentional — the lint catches
mistakes before a run, `prepare` is the source of truth during one.

## Config and root resolution

A repo opts in via a `[tool.judgments]` table in its `pyproject.toml`:

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]   # globs (relative to root) locating the declaration files
```

- **`paths`** — required list of globs, expanded relative to the root to find the
  declaration files. A `[tool.judgments]` table that is present but declares no
  `paths` (or an empty `paths`) is a hard configuration error: you opted in but
  pointed nowhere.
- **`root`** — the nearest ancestor directory of the current working directory
  that contains a `pyproject.toml` with a `[tool.judgments]` table. Both the CLI
  and the pytest helper resolve it this way (walking up from the cwd). All
  `paths` globs and all evidence/reference paths resolve against this root.

Because the key is **root-invariant** (the root only *locates* files; it never
enters the key), the same judgment caches identically across worktrees and
checkouts.

If no `[tool.judgments]` table is found anywhere up the tree, there are **no
judgments**: the bulk commands no-op cleanly (they exit 0), while a by-id command
(`render`/`record` for a specific `id`) still fails loud as an unknown id.

## Instruments

The valid instrument values are the single source of truth in
[`tools/judgments/instruments.py`](~/workspace/dev-playbook/tools/judgments/instruments.py):

```python
VALID_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})
VALID_MODELS  = frozenset({
    "claude-opus-4-8",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
})
```

These are **full model IDs, not aliases** — the full ID is what gets hashed into
the key, so the cached judge identity is exact. The list is **maintained by hand
and must be bumped when a new model ships**: a too-stale `VALID_MODELS` will
reject an otherwise-valid config. Both the loader and `judgments-lint` validate
`model`/`effort` against these sets.

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
  is new or changed and needs the judge skill to run it.
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
and recording the passes — is the judge skill's job, the only place an LLM ever
runs. A judgment whose judge returns *false* is never recorded, so it stays a
permanent miss (a permanent failing test) until the underlying content is fixed.

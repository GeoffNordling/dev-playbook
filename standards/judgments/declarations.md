---
type: Standard
title: Judgment Declarations
description: The judgment model and YAML declaration format — claim, evidence, instrument, and the content-addressed key
---

# Judgment Declarations

A **judgment** is a single yes/no question about one or more files, ruled
on by an LLM judge — for example, *"docs/errors.md lists every exception
type that src/exceptions.py raises."* A judgment is declared as data on
disk; the deterministic [cache gate](/standards/judgments/cache-gate.md)
passes it **iff its exact content has already been judged-and-passed**, and
the `run-judgments` skill fills the cache by actually running the judge on
the misses.

## What a judgment is

A judgment has four parts:

- **claim** — the proposition to rule on, in prose.
- **evidence** — the files under judgment; what the judge is ruling on.
- **reference** — optional files the judge may consult for context but are
  not judged.
- **instrument** — the `model` and `effort` the judge runs under.

A declaration sets a judgment's **case** — its claim, files, and
instrument. It does not set the **judge**: every judgment is ruled through
one fixed judge prompt and output schema (constants in
[`tools/src/judgments/core.py`](/tools/src/judgments/core.py)), uniform
across all judgments, so there is nothing to declare for them.

The claim, the contents of every evidence and reference file, the
instrument, and that fixed prompt and schema together form a
content-addressed **key**. The key is what the cache is keyed on, so a
judgment is re-judged exactly when one of those inputs changes — and not
otherwise. The `id` (below) is a label only; it never enters the key.
Renaming an `id` with unchanged content stays a cache hit; changing content
under the same `id` is a miss.

## The YAML declaration format

A repo declares its judgments in one or more YAML files. Each file has a
single top-level key `judgments:` whose value is a list of judgment
objects:

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

Every field rule is a hard, fail-loud error naming the offending `id` (or
file):

| field | required | rule |
|---|---|---|
| `id` | yes | non-empty string, charset `[A-Za-z0-9._-]`, **globally unique across all of the repo's declaration files** (it is a CLI argument and a cache/report handle). |
| `claim` | yes | non-empty string. |
| `evidence` | yes | list of **≥1** repo-root-relative path strings. |
| `reference` | no | list of repo-root-relative path strings; omit or `[]` for none. |
| `model` | yes | string in `VALID_MODELS` (see [Instruments](#instruments)). |
| `effort` | yes | string in `VALID_EFFORTS` (see [Instruments](#instruments)). |

Paths are **relative to the repo root** (see
[Config and root resolution](#config-and-root-resolution)), never to the
YAML file's own location. Each must be a relative path — no absolute path,
no `..` segment — that points to an existing file.

## Config and root resolution

A repo opts in via a `[tool.judgments]` table in its `pyproject.toml`:

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]   # globs (relative to root) locating the declaration files
```

- **`paths`** — required list of globs, expanded relative to the root to
  find the declaration files. A `[tool.judgments]` table that is present
  but declares no `paths` (or an empty `paths`) is a hard configuration
  error: the repo opted in but pointed nowhere.
- **`root`** — the nearest ancestor directory of the current working
  directory that contains a `pyproject.toml` with a `[tool.judgments]`
  table. All `paths` globs and all evidence/reference paths resolve against
  this root.

Because the key is **root-invariant** (the root only *locates* files; it
never enters the key), the same judgment caches identically across
worktrees and checkouts.

If no `[tool.judgments]` table is found anywhere up the tree, there are
**no judgments**.

## Instruments

A judgment's instrument is its `model` and `effort`. The valid values are
the single source of truth in
[`tools/src/judgments/instruments.py`](/tools/src/judgments/instruments.py)
(`VALID_MODELS`, `VALID_EFFORTS`); a `model` or `effort` outside it is a
fail-loud error.

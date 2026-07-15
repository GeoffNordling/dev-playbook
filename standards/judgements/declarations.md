---
type: Standard
title: Judgement Declarations
description: The judgement model and YAML declaration format — claim, evidence, bench, and the content-addressed key
---

# Judgement Declarations

A **judgement** is a single yes/no question about one or more files, ruled
on by an LLM judge — for example, *"docs/errors.md lists every exception
type that src/exceptions.py raises."* A judgement is declared as data on
disk; the deterministic [cache gate](/standards/judgements/cache-gate.md)
passes it **iff its exact content has already been judged-and-passed**, and
the `run-judgements` skill fills the cache by actually running the judge on
the misses.

## What a judgement is

A judgement has four parts:

- **claim** — the proposition to rule on, in prose.
- **evidence** — the files under judgement; what the judge is ruling on.
- **reference** — optional files the judge may consult for context but are
  not judged.
- **bench** — the `model` and `effort` the judge runs under.

A declaration sets a judgement's **case** — its claim, files, and bench. It
does not set the **procedure**: every judgement is ruled through one fixed
judge prompt and output schema (constants in
[`src/dev_playbook/judgements/core.py`](/src/dev_playbook/judgements/core.py)), uniform
across all judgements, so there is nothing to declare for it.

The claim, the contents of every evidence and reference file, the bench,
and that fixed procedure together form a
content-addressed **key**. The key is what the cache is keyed on, so a
judgement is re-judged exactly when one of those inputs changes — and not
otherwise. The `id` (below) is a label only; it never enters the key.
Renaming an `id` with unchanged content stays a cache hit; changing content
under the same `id` is a miss.

## The bar

Not every true statement about a repo deserves a judgement. A judgement is
expensive — an LLM re-runs whenever the bytes of any input change — so it
is spent only where it buys the most: **targeted semantic glue at a
high-risk point**, a specific claim about specific files whose silent drift
would be costly and that no deterministic detector can catch. A judgement is
never a catch-all, and never a blanket family stretched over a whole
population of documents — a population is a detector's job, or no one's.
When in doubt, do not add one.

## The YAML declaration format

A repo declares its judgements in one or more YAML files, **one file per
claim family**. A claim family is a set of judgements that share a claim
shape — what is on trial, what it is tried against, and what makes the
verdict true or false. Each file opens with a header comment defining its
family's shape, so a reader learns the pattern once and reads the entries
against it. The families themselves are each repo's own and live in the
file headers, not in this contract; the uniform rule is only that
declarations are grouped into families, one file each. Discovery globs all
declaration files (see [Config and root resolution](#config-and-root-resolution)),
so adding or splitting a family file needs no registration beyond matching
the glob.

Each file has a single top-level key `judgements:` whose value is a list of
judgement objects:

```yaml
judgements:
  - id: errors-exhaustive
    claim: |
      docs/errors.md lists every exception type that src/exceptions.py raises.
    evidence:  [docs/errors.md]          # files under judgement
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
| `model` | yes | string in `VALID_MODELS` (see [The bench](#the-bench)). |
| `effort` | yes | string in `VALID_EFFORTS` (see [The bench](#the-bench)). |

Paths are **relative to the repo root** (see
[Config and root resolution](#config-and-root-resolution)), never to the
YAML file's own location. Each must be a relative path — no absolute path,
no `..` segment — that points to an existing file.

## Config and root resolution

A repo opts in via a `[tool.judgements]` table in its `pyproject.toml`:

```toml
[tool.judgements]
paths = ["judgements/*.yaml"]   # globs (relative to root) locating the declaration files
```

- **`paths`** — required list of globs, expanded relative to the root to
  find the declaration files. A `[tool.judgements]` table that is present
  but declares no `paths` (or an empty `paths`) is a hard configuration
  error: the repo opted in but pointed nowhere.
- **`root`** — the nearest ancestor directory of the current working
  directory that contains a `pyproject.toml` with a `[tool.judgements]`
  table. All `paths` globs and all evidence/reference paths resolve against
  this root.

Because the key is **root-invariant** (the root only *locates* files; it
never enters the key), the same judgement caches identically across
worktrees and checkouts.

If no `[tool.judgements]` table is found anywhere up the tree, there are
**no judgements**.

## The bench

A judgement's bench is its `model` and `effort` — the judge that hears the
case. The valid values are the single source of truth in
[`src/dev_playbook/judgements/bench.py`](/src/dev_playbook/judgements/bench.py)
(`VALID_MODELS`, `VALID_EFFORTS`); a `model` or `effort` outside it is a
fail-loud error.

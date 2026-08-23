---
type: Standard
title: Judgment Declarations
description: The judgment model and YAML declaration format — claim, evidence, bench, and the content-addressed key
---

# Judgment Declarations

A **judgment** is a single yes/no question about one or more files, ruled
on by an LLM judge — for example, *"docs/errors.md lists every exception
type that src/exceptions.py raises."* A judgment is declared as data on
disk; a machine-local cache remembers **which exact content has been
judged-and-passed**; the periodic
[`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
skill fills that
cache by running the judge on whatever drifted out; and the
deterministic [cache gate](/standards/semantic-validation/cache-gate.md) — where a
repo wires one — turns a miss into a failing pytest.

## What a judgment is

A judgment consists of:

- **claim** — the proposition to rule on, in prose.
- **evidence** — the files under judgment; what the judge is ruling on.
- **reference** — optional files the judge may consult for context but are
  not judged.
- **bench** — the `model` and `effort` the judge runs under.

A declaration sets a judgment's **case** — its claim, files, and bench. It
does not set the **procedure**: every judgment is ruled through one fixed
judge prompt and output schema (constants in
[`src/dev_playbook/judgments/core.py`](/src/dev_playbook/judgments/core.py)),
uniform across all judgments, so there is nothing to declare for it.

The claim, the contents of every evidence and reference file, the bench,
and that fixed procedure together form a
content-addressed **key**. The key is what the cache is keyed on, so a
judgment is re-judged exactly when one of those inputs changes. The `id`
(below) is a label only; it never enters the key. Renaming an `id` with
unchanged content stays a cache hit; changing content under the same `id`
is a miss.

## The bar

Not every true statement about a repo deserves a judgment. A judgment is
expensive — every sweep re-judges it whenever the bytes of any input
change, and each re-run is a fresh chance for a stochastic false refutation
someone must weigh — so it is spent only where it buys the most: a
specific claim about specific files whose silent drift would be costly and
that no deterministic detector can catch. A judgment is never a catch-all,
and never covers a whole population of documents — that is a detector's
job, or no one's. When in doubt, do not add one.

## Maintenance

Declarations are peer documentation: whoever edits an artifact updates,
removes, or adds the declarations that describe it in the same change —
and never runs judges or touches the cache; judging belongs to the
periodic `judgments-sweep`. Kept this way, the sweep opens on declarations
that mean what they say.

Additions stay rare ([The bar](#the-bar)). Success in daily work is
keeping existing declarations accurate.

## The YAML declaration format

A repo declares its judgments in one or more YAML files, **one file per
claim family**. A claim family is a set of judgments that share a claim
shape — what is on trial, what it is tried against, and what makes the
verdict true or false. Each file opens with a header comment defining its
family's shape, so a reader learns the pattern once and reads the entries
against it. The families themselves are each repo's own and live in the
file headers, not in this contract; the uniform rule is only that
declarations are grouped into families, one file each. Discovery globs all
declaration files (see [Config and root resolution](#config-and-root-resolution)),
so adding or splitting a family file needs no registration beyond matching
the glob.

Each file has a single top-level key `judgments:` whose value is a list of
judgment objects:

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
| `model` | yes | string in `VALID_MODELS` (see [The bench](#the-bench)). |
| `effort` | yes | string in `VALID_EFFORTS` (see [The bench](#the-bench)). |

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

## The bench

A judgment's bench is its `model` and `effort` — the judge that hears the
case. The valid values are the single source of truth in
[`src/dev_playbook/judgments/bench.py`](/src/dev_playbook/judgments/bench.py)
(`VALID_MODELS`, `VALID_EFFORTS`); a `model` or `effort` outside it is a
fail-loud error.

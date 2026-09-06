---
type: Standard
title: Judgment Declarations
description: A repo's judgment declarations — the opt-in table, one file per claim family, an entry's fields, and the bar a claim clears
population: "a repo's judgment declarations: the [tool.judgments] table in its pyproject.toml, the declaration files the table's globs match, and every entry in them"
---

# Judgment Declarations

A **judgment** is a single yes/no question about one or more files, ruled on
by an LLM judge, such as *"docs/errors.md lists every exception type that
src/exceptions.py raises."* A judgment is declared as data on disk, and one
entry states four things. The **claim** is the proposition to rule on, in
prose. The **evidence** is the files under judgment, what the judge rules on.
The **reference** is optional further files the judge may consult for context
but does not rule on. The **bench** is the `model` and `effort` the judge runs
under.

A repo's declarations are the `[tool.judgments]` table in its
`pyproject.toml`, the files that table's globs match, and every entry in those
files. The **root** is the nearest ancestor directory of the current working
directory holding a `pyproject.toml` with a `[tool.judgments]` table, and
every glob and every declared path resolves against it. Where no such table
exists anywhere up the tree, the repo has no judgments and nothing here binds.
What runs the judge and remembers its verdict is
[The Cache Gate](/standards/semantic-validation/cache-gate.md); how a repo
picks the tooling up is
[Consuming Judgments](/standards/semantic-validation/consuming.md).

## Opt-in table

The `[tool.judgments]` table declares `paths`, a non-empty list of globs that
locate the declaration files, each expanded relative to the root. A table
present with `paths` absent or empty is a hard configuration error reported at
`pyproject.toml` (`semantic-validation.declaration`): the repo opted in and
pointed nowhere.

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]   # globs (relative to root) locating the declaration files
```

## File shape

A declaration file is a YAML mapping whose single top-level key `judgments:`
holds a list of judgment entries. A file parsing to anything else is a hard
error reported at that file (`semantic-validation.declaration`).

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

## One file per claim family

A declaration file holds one claim family, the judgments that share a claim
shape: what is on trial, what it is tried against, and what makes the verdict
true or false. The file opens with a header comment stating that shape, so a
reader learns the pattern once and reads the entries against it.

The families themselves are each repo's own and live in the file headers, not
in this Standard; the uniform rule is only that declarations are grouped into
families, one file each. Discovery globs every declaration file, so adding or
splitting a family file needs no registration beyond matching the glob.

## Fields

An entry carries `id`, `claim`, `evidence`, `model`, and `effort`, and
optionally `reference`, each valid by the table below. A missing or invalid
field is a hard, fail-loud error naming the offending `id`, or the file where
the `id` itself is the problem (`semantic-validation.declaration`).

| field | required | rule |
|---|---|---|
| `id` | yes | non-empty string, charset `[A-Za-z0-9._-]`. |
| `claim` | yes | non-empty string. |
| `evidence` | yes | list of **≥1** root-relative path strings. |
| `reference` | no | list of root-relative path strings; omit or `[]` for none. |
| `model` | yes | string in `VALID_MODELS`. |
| `effort` | yes | string in `VALID_EFFORTS`. |

The bench is a judgment's `model` and `effort`, the judge that hears the case.
Its valid values are the single source of truth in
[`src/dev_playbook/judgments/bench.py`](/src/dev_playbook/judgments/bench.py)
(`VALID_MODELS`, `VALID_EFFORTS`). The loader reads the named fields only, so
a further key in an entry is read by nothing.

## Unique id

An `id` occurs once across all of a repo's declaration files. It is a CLI
argument and a cache and report handle, so a repeat is a hard error at the
repeating file, naming the file that declared it first
(`semantic-validation.declaration`).

## Evidence and reference paths

Every `evidence` and `reference` path is relative to the root, never to the
YAML file's own location; carries no `..` segment; and names an existing file
(`semantic-validation.evidence-path`).

## The bar

A claim is specific: it names specific files and a proposition whose silent
drift would be costly and that no deterministic detector catches. A claim is
never a catch-all, and never covers a whole population of documents; that is a
detector's job, or no one's.

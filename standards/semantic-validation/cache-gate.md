---
type: Guide
title: The Cache Gate
description: How a judgment is gated — the offline cache check a pytest makes, the spectrum of positions a repo picks from, and the environment variable that arms the gate
---

# The Cache Gate

A **gated** judgment is one some pytest names — a test whose body does only
a deterministic, offline cache check, no LLM, no network, no API key:

```python
from dev_playbook.judgments.pytest_support import assert_judgment_cached


def test_errors_exhaustive():
    assert_judgment_cached("errors-exhaustive")
```

`assert_judgment_cached(id)` resolves the root
([declarations.md — Opt-in table](/standards/semantic-validation/declarations.md#opt-in-table)),
keys the named judgment, and asks the seen-set whether that exact content has
been judged-and-passed:

- **cache hit → the test passes.** The judge has ruled the content true.
- **cache miss → the test fails** with `judgment '<id>': cache miss`. The
  content is new or changed, and no judge has ruled on it yet.
- an unknown `id`, or an unreadable evidence file, surfaces as a loud test
  error, never a silent pass — a test naming a deleted or renamed judgment
  fails instead of lingering unnoticed.

So the gate is fast and deterministic: green means every judgment it names
is cached as passing. Filling the cache — running the judge on the misses
and recording the passes — is the job of the
[`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
skill, the only place an LLM ever runs. A judgment whose judge returns
*false* is never recorded, so it stays a permanent miss (a permanent
failing test, where gated) until the underlying content is fixed.

## The gate spectrum

Gate enforcement is per-judgment, by design: **a judgment is gate-enforced
iff some pytest calls `assert_judgment_cached` with its id.** A repo
therefore chooses where to sit on a spectrum — all of its judgments gated,
some, or none — and every position runs on identical machinery: the same
declarations, CLI, cache, and build files. An ungated judgment is checked
by no test and no hook; the periodic `judgments-sweep` is its only checker,
and the sweep always considers every declaration regardless of gating.

Test shapes cover the whole spectrum:

- **Explicit, per judgment** — one test naming one id, as above. Opt-in: a
  new declaration is not gated until someone writes its test.
- **Parametrized, over many** — one test enumerating ids through the
  loader. Unfiltered, it gates every declaration automatically, including
  ones added later; filtering the expression gates a chosen subset.

```python
import pytest
from dev_playbook.judgments.loader import load, resolve_root
from dev_playbook.judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

Gate a judgment where it is load-bearing verification — where a push over
unjudged content must not land. Leave the rest ungated: the sweep still
judges them, and a stochastic judge's false positive never blocks a push
mid-work.

The sweep pre-fills the shared cache for gated judgments too, so gates are
usually green; when a push still blocks, the remedy is running
`judgments-sweep` ad hoc.

## Two tiers: when the gate is armed

A cache miss is only remediable by a judgments sweep, but subagents are
told to run `make check` regularly. So the gate is two-tier, keyed off one
environment variable, `SKIP_JUDGMENTS`, read inside `assert_judgment_cached`
itself:

| Invocation | `SKIP_JUDGMENTS` | The gate |
|---|---|---|
| `make check`, `make test` | `1` (the Makefile default, exported) | **skipped** |
| `make check-judgments-cache` | `0` — or `1` on machines without the cache (`NO_JUDGMENT_CACHE`, [Machines](/docs/machines.md)) | **armed** |
| bare `uv run pytest` | unset | **armed** (fail-safe) |

When `SKIP_JUDGMENTS` is exactly `1`, the helper **skips** each case with a
visible pytest skip naming the id — never a silent pass; any other value, or
unset, arms the check. The lever lives in the helper — the one choke point
every gate test calls — so it covers both test shapes with **no per-test
markers**. `make check-judgments-cache` is the
[pre-push hook](/standards/build/canonical/.pre-commit-config.yaml)'s entry:
it asserts the cache for whatever judgments the repo has tripwired via
pytest, so in a gated repo a miss blocks the push until a sweep fills it,
and a repo with nothing tripwired passes it vacuously — a valid position on
the spectrum.

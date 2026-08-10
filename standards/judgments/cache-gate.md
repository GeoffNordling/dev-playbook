---
type: Standard
title: The Cache Gate
description: The deterministic pytest gate — green iff every judgment's exact content is already judged-and-passed
---

# The Cache Gate

Every judgment is a **pytest** whose body does only a deterministic,
offline cache check — no LLM, no network, no API key:

```python
from dev_playbook.judgments.pytest_support import assert_judgment_cached


def test_errors_exhaustive():
    assert_judgment_cached("errors-exhaustive")
```

`assert_judgment_cached(id)` resolves the root
([declarations.md — Config and root resolution](/standards/judgments/declarations.md#config-and-root-resolution)),
keys the named judgment
([declarations.md — What a judgment is](/standards/judgments/declarations.md#what-a-judgment-is)),
and asks the seen-set whether that exact content has been
judged-and-passed:

- **cache hit → the test passes.** The judgment's content has already been
  ruled true by the judge.
- **cache miss → the test fails** with `judgment '<id>': cache miss`. The
  content is new or changed and needs the `run-judgments` skill to run it.
- an unknown `id`, or an unreadable evidence file, surfaces as a loud test
  error, never a silent pass.

A repo can instead cover **all** its judgments with one parametrized test,
enumerating ids through the loader:

```python
import pytest
from dev_playbook.judgments.loader import load, resolve_root
from dev_playbook.judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

So `pytest` is a fast gate: green means every judgment's current content is
already cached as passing. Filling the cache — running the judge on the
misses and recording the passes — is the job of the `run-judgments` skill,
the only place an LLM ever runs, and it runs at the **main loop only**: it
needs orchestration tooling a subagent lacks. It has to be a skill — thin
harness instructions — because subscription billing requires running the
judges through the harness interactively. A judgment whose judge returns
*false* is never recorded, so it stays a permanent miss (a permanent failing
test) until the underlying content is fixed.

## Two tiers: when the gate is armed

The cache miss is only remediable by `run-judgments` at the main loop, but
subagents are told to run `make check` regularly. So the gate is two-tier,
keyed off one environment variable, `SKIP_JUDGMENTS`, read inside
`assert_judgment_cached` itself:

| Invocation | `SKIP_JUDGMENTS` | The gate |
|---|---|---|
| `make check`, `make test` | `1` (the Makefile default, exported) | **skipped** |
| `make check-judgments-cache` | `0` (`$(MAKE) check SKIP_JUDGMENTS=0`) | **armed** |
| bare `uv run pytest` | unset | **armed** (fail-safe) |

When `SKIP_JUDGMENTS` is exactly `1`, the helper **skips** each case with a
visible pytest skip naming the id — never a silent pass; any other value, or
unset, arms the check. The lever lives in the helper — the one choke point
every consumer's gate test calls — so it covers any test shape (the single or
parametrized recipes above) with **no per-test markers** and no change to
those recipes. `make check-judgments-cache` is the
[pre-push hook](/standards/build/canonical/.pre-commit-config.yaml)'s entry, so
a miss blocks the push; the user or main-loop agent then runs `run-judgments`
and retries. A subagent running plain `make check` never meets an
unresolvable red.

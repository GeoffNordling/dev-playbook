---
type: Instrument Spec
title: The Cache Gate
description: The deterministic pytest gate — green iff every judgment's exact content is already judged-and-passed
---

# The Cache Gate

Every judgment is a **pytest** whose body does only a deterministic,
offline cache check — no LLM, no network, no API key:

```python
from judgments.pytest_support import assert_judgment_cached


def test_errors_exhaustive():
    assert_judgment_cached("errors-exhaustive")
```

`assert_judgment_cached(id)` resolves the root
([declarations.md — Config and root resolution](/instruments/judgments/declarations.md#config-and-root-resolution)),
keys the named judgment
([declarations.md — What a judgment is](/instruments/judgments/declarations.md#what-a-judgment-is)),
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
from judgments.loader import load, resolve_root
from judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

So `pytest` is a fast gate: green means every judgment's current content is
already cached as passing. Filling the cache — running the judge on the
misses and recording the passes — is the job of the `run-judgments` skill,
the only place an LLM ever runs. It has to be a skill — thin harness
instructions — because subscription billing requires running the judges
through the harness interactively. A judgment whose judge returns *false*
is never recorded, so it stays a permanent miss (a permanent failing test)
until the underlying content is fixed.

"""The pytest cache-gate: assert a judgement's content has already been judged.

A consumer repo's per-judgement test is just ``assert_judgement_cached("<id>")``.
The check is deterministic and offline -- it resolves the repo's judgements,
keys the named one, and asks the seen-set whether that exact content has been
judged-and-passed. A hit passes; a miss fails the test (the judge skill must run
it). Filling the cache is the skill's job; this only reads it.

The gate is two-tier via one environment variable, ``SKIP_JUDGEMENTS``. When it
is exactly ``"1"`` the check is skipped (a visible pytest skip), so a subagent
running ``make check``/``make test`` -- which default it to ``1`` -- never hits
an unresolvable red it lacks the tooling to fill. Any other value, or unset,
runs the gate: a bare ``pytest`` and the ``make check-judgements`` push tripwire
(which sets it to ``0``) are fail-safe. The lever lives here, the one choke
point every consumer's gate test calls, so it covers any test shape with no
per-test markers.
"""

import os

import pytest

from dev_playbook.judgements.core import prepare
from dev_playbook.judgements.loader import by_id, load, resolve_root
from dev_playbook.skipcache import seen


def assert_judgement_cached(id: str) -> None:
    """Pass iff judgement ``id``'s content key is in the seen-set; else fail the test.

    When ``SKIP_JUDGEMENTS`` is exactly ``"1"`` in the environment, skips the
    check with a visible pytest skip naming the id -- never a silent pass. Any
    other value, or unset, arms the gate below.

    Otherwise resolves the repo root, loads the judgement by ``id``, and keys it
    via ``judgements.prepare``. A cache hit returns silently. A miss raises
    ``AssertionError`` with a factual message naming the id -- it reports the
    miss only, with no remediation advice. An unknown ``id`` or an unreadable
    evidence file propagates as a loud error, never a silent pass.
    """
    if os.environ.get("SKIP_JUDGEMENTS") == "1":
        pytest.skip(f"judgement {id!r}: SKIP_JUDGEMENTS=1")
    root = resolve_root()
    declaration = by_id(load(root), id)
    assert root is not None  # a declaration was found, so a root resolved
    prepared = prepare(
        declaration.claim,
        declaration.evidence,
        declaration.reference,
        declaration.model,
        declaration.effort,
        root,
    )
    if not seen.filter([prepared.key]).seen:
        raise AssertionError(f"judgement {id!r}: cache miss")

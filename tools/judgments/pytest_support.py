"""The pytest cache-gate: assert a judgment's content has already been judged.

A consumer repo's per-judgment test is just ``assert_judgment_cached("<id>")``.
The check is deterministic and offline -- it resolves the repo's judgments,
keys the named one, and asks the seen-set whether that exact content has been
judged-and-passed. A hit passes; a miss fails the test (the judge skill must run
it). Filling the cache is the skill's job; this only reads it.
"""

from judgments.core import prepare
from judgments.loader import by_id, load, resolve_root
from skipcache import seen


def assert_judgment_cached(id: str) -> None:
    """Pass iff judgment ``id``'s content key is in the seen-set; else fail the test.

    Resolves the repo root, loads the judgment by ``id``, and keys it via
    ``judgments.prepare``. A cache hit returns silently. A miss raises
    ``AssertionError`` with a factual message naming the id -- it reports the
    miss only, with no remediation advice. An unknown ``id`` or an unreadable
    evidence file propagates as a loud error, never a silent pass.
    """
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
        raise AssertionError(f"judgment {id!r}: cache miss")

"""The judgements cache-gate for dev-playbook's own declared judgements.

dev-playbook is a consumer of its judgements tooling: the parametrized test
below is its gate. Green means every declared judgement's current content has
already been judged-and-passed (its key is cached); a miss fails until the
run-judgements skill judges it and records the pass. See standards/judgements/.

The gate does an offline cache check only, but the cache it reads is
machine-local and only the interactive, subscription-billed run-judgements skill
can fill it. So the two-tier gate governs when it is armed: default ``make
check``/``make test`` export ``SKIP_JUDGEMENTS=1``, which ``assert_judgement_cached``
honours by skipping each case visibly -- a subagent can run them and never hit an
unresolvable red. ``make check-judgements`` arms the gate (``SKIP_JUDGEMENTS=0``)
and is the pre-push hook's entry, so a miss blocks the push. A bare ``pytest``
runs the gate too (fail-safe). The config-resolves guard above it is never
skipped: it must hold everywhere.
"""

import pytest

from dev_playbook.judgements.loader import load, resolve_root
from dev_playbook.judgements.pytest_support import assert_judgement_cached


# Guards the gate below: resolve_root() must find the repo's [tool.judgements]
# config in every environment (it needs no LLM and no cache, so it never skips).
# If it returned None, load() would yield no ids, the parametrized gate would
# collect zero cases, and pytest would silently skip it -- a misconfiguration
# reading as success. Fail loud instead.
def test_judgements_config_resolves() -> None:
    assert resolve_root() is not None


# The cache-gate itself, one case per declared judgement. Armed or skipped by the
# SKIP_JUDGEMENTS env var, which assert_judgement_cached reads: default make
# check/make test set it to 1 (each case skips, visibly); make check-judgements
# sets it to 0 (the gate runs, at the pre-push hook). No skipif marker -- the
# helper owns the skip so it covers every consumer's gate shape alike.
@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgement_cached(jid: str) -> None:
    assert_judgement_cached(jid)

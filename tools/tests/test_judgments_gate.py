"""The judgments cache-gate for dev-playbook's own declared judgments.

dev-playbook is a consumer of its judgments tooling: the parametrized test
below is its gate. Green means every declared judgment's current content has
already been judged-and-passed (its key is cached); a miss fails until the
run-judgments skill judges it and records the pass. See standards/judgments.md.

The gate does an offline cache check only -- but the cache it reads is
machine-local and only the interactive, subscription-billed run-judgments skill
can fill it, so the gate passes only where a human has run the judge. It is a
local pre-merge tripwire, skipped on GH CI via SKIP_JUDGMENTS (see
.github/workflows/ci.yml). The config-resolves guard above it is never skipped:
it must hold everywhere, CI included.
"""

import os

import pytest

from judgments.loader import load, resolve_root
from judgments.pytest_support import assert_judgment_cached


# Guards the gate below: resolve_root() must find the repo's [tool.judgments]
# config in every environment (it needs no LLM and no cache, so it runs on CI
# too). If it returned None, load() would yield no ids, the parametrized gate
# would collect zero cases, and pytest would silently skip it -- a
# misconfiguration reading as success. Fail loud instead.
def test_judgments_config_resolves() -> None:
    assert resolve_root() is not None


# The cache-gate itself, one case per declared judgment. Skipped on GH CI
# (SKIP_JUDGMENTS=1 in .github/workflows/ci.yml): the seen-set is machine-local
# and only the interactive run-judgments skill can fill it, neither of which
# exists on the CI runner. Locally it is the strict pre-merge gate.
@pytest.mark.skipif(
    os.environ.get("SKIP_JUDGMENTS") == "1",
    reason="judgments run locally only; the LLM judge can't run on GH CI",
)
@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid: str) -> None:
    assert_judgment_cached(jid)

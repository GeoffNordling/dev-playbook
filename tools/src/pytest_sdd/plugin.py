"""pytest-sdd plugin entry point.

Registers the 'spec' marker and injects spec validation test items into the
pytest session via pytest_collection_modifyitems. Items are injected with
tryfirst=True so the built-in -m marker filter runs after injection.

Usage:
    pytest -m spec           # run only spec checks
    pytest -m "not spec"     # exclude spec checks
    pytest                   # run everything (normal tests + spec checks)
"""

import pytest

from pytest_sdd.collector import SpecFile, SpecTraceItem
from pytest_sdd.config import SddConfig, load_config

_SDD_KEY: pytest.StashKey[SddConfig] = pytest.StashKey()


def pytest_configure(config: pytest.Config) -> None:
    """Register the 'spec' marker and load plugin configuration."""
    config.addinivalue_line(
        "markers",
        "spec: marks OFT spec validation tests (lint + traceability)",
    )
    sdd_config = load_config(config)
    if sdd_config is not None:
        config.stash[_SDD_KEY] = sdd_config


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Inject spec lint and trace items into the collected test suite."""
    sdd_config = config.stash.get(_SDD_KEY, None)
    if sdd_config is None:
        return

    spec_items: list[pytest.Item] = []

    # One SpecFile collector per .md file → one SpecLintItem each
    for spec_dir in sdd_config.spec_dirs:
        if not spec_dir.is_dir():
            continue
        for md_file in sorted(spec_dir.rglob("*.md")):
            collector = SpecFile.from_parent(
                session,
                path=md_file,
                sdd_config=sdd_config,
            )
            spec_items.extend(collector.collect())

    # One SpecTraceItem for the entire spec tree — pass collected test items
    # so it can extract @pytest.mark.req/dsn markers for OFT coverage bridging
    trace_item = SpecTraceItem.from_parent(
        session,
        name="spec-trace",
        path=session.fspath,
        sdd_config=sdd_config,
        test_items=list(items),
    )
    spec_items.append(trace_item)

    items.extend(spec_items)

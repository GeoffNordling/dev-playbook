"""pytest-sdd plugin entry point.

Hosts every SDD validator (lint, coverage, interface, test-privacy) as a
pytest item tagged with the ``spec`` marker. Synthesizes one item per
validator at collection time. Each item's failure message renders the
validator's Finding list (or, for coverage, the OFT JAR's report).

Usage:
    pytest -m spec           # run only spec checks
    pytest -m "not spec"     # exclude spec checks
    pytest                   # run everything
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from sdd_tools.config import SddConfig, load_config_from_root
from sdd_tools.interface import validate_interfaces
from sdd_tools.lint import lint_file
from sdd_tools.markers import create_coverage_dir
from sdd_tools.models import Finding, render_findings
from sdd_tools.oft import load_spec_items, require_java, resolve_oft_jar, run_oft_trace
from sdd_tools.privacy import validate_files

_SDD_KEY: pytest.StashKey[SddConfig] = pytest.StashKey()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "spec: marks SDD validation tests (lint, coverage, interface, privacy)",
    )
    sdd_config = load_config_from_root(Path(config.rootpath))
    if sdd_config is not None:
        config.stash[_SDD_KEY] = sdd_config


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    sdd_config = config.stash.get(_SDD_KEY, None)
    if sdd_config is None:
        return

    # Snapshot test items before injection so validators that depend on the
    # real test suite (privacy, coverage marker harvest) don't see our items.
    test_items = list(items)

    spec_items: list[pytest.Item] = [
        SddValidatorItem.from_parent(
            session,
            name="spec-lint",
            path=Path(config.rootpath),
            sdd_config=sdd_config,
            validator=_run_lint,
            test_items=None,
        ),
        SddTraceItem.from_parent(
            session,
            name="spec-coverage",
            path=Path(config.rootpath),
            sdd_config=sdd_config,
            test_items=test_items,
        ),
        SddValidatorItem.from_parent(
            session,
            name="spec-interface",
            path=Path(config.rootpath),
            sdd_config=sdd_config,
            validator=_run_interface,
            test_items=None,
        ),
        SddValidatorItem.from_parent(
            session,
            name="spec-privacy",
            path=Path(config.rootpath),
            sdd_config=sdd_config,
            validator=_run_privacy,
            test_items=test_items,
        ),
    ]
    items.extend(spec_items)


# ---------------------------------------------------------------------------
# Pytest items
# ---------------------------------------------------------------------------


class SddValidatorError(Exception):
    """Raised by a Finding-emitting validator when findings exist."""


class SddTraceError(Exception):
    """Raised when the OFT trace pass fails."""


class SddValidatorItem(pytest.Item):
    """Pytest item for a Finding-emitting validator (lint, interface, privacy)."""

    def __init__(
        self,
        *,
        sdd_config: SddConfig,
        validator: Any,
        test_items: list[pytest.Item] | None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sdd_config = sdd_config
        self.validator = validator
        self.test_items = test_items
        self.add_marker(pytest.mark.spec)

    def runtest(self) -> None:
        findings = self.validator(self.sdd_config, self.test_items)
        if findings:
            raise SddValidatorError(render_findings(findings))

    def repr_failure(self, excinfo: pytest.ExceptionInfo[BaseException], style: Any = None):  # type: ignore[override]
        if isinstance(excinfo.value, SddValidatorError):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style)

    def reportinfo(self) -> tuple[Path, int | None, str]:
        return self.path, None, self.name


class SddTraceItem(pytest.Item):
    """Pytest item for the OFT trace pass (coverage check)."""

    def __init__(
        self,
        *,
        sdd_config: SddConfig,
        test_items: list[pytest.Item],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sdd_config = sdd_config
        self.test_items = test_items
        self.add_marker(pytest.mark.spec)

    def runtest(self) -> None:
        jar_path = resolve_oft_jar(self.sdd_config.oft_jar)
        require_java()

        for spec_dir in self.sdd_config.spec_dirs:
            if not spec_dir.is_dir():
                raise FileNotFoundError(f"Spec directory not found: {spec_dir}")

        coverage_tmp = create_coverage_dir(self.test_items)
        input_paths = list(self.sdd_config.spec_dirs)
        if coverage_tmp:
            input_paths.append(Path(coverage_tmp.name))

        try:
            run_oft_trace(jar_path, input_paths)
        except subprocess.CalledProcessError as exc:
            raise SddTraceError(f"OFT trace failed:\n{exc.output}") from exc
        finally:
            if coverage_tmp:
                coverage_tmp.cleanup()

    def repr_failure(self, excinfo: pytest.ExceptionInfo[BaseException], style: Any = None):  # type: ignore[override]
        if isinstance(
            excinfo.value, (SddTraceError, FileNotFoundError, RuntimeError)
        ):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style)

    def reportinfo(self) -> tuple[Path, int | None, str]:
        return self.path, None, self.name


# ---------------------------------------------------------------------------
# Validator entry points (wrap module-level functions for SddValidatorItem)
# ---------------------------------------------------------------------------


def _run_lint(
    sdd_config: SddConfig, _test_items: list[pytest.Item] | None
) -> list[Finding]:
    findings: list[Finding] = []
    for spec_dir in sdd_config.spec_dirs:
        if not spec_dir.is_dir():
            continue
        for md_file in sorted(spec_dir.rglob("*.md")):
            findings.extend(lint_file(md_file, md_file.read_text(encoding="utf-8")))
    return findings


def _run_interface(
    sdd_config: SddConfig, _test_items: list[pytest.Item] | None
) -> list[Finding]:
    items = load_spec_items(sdd_config.oft_jar, sdd_config.spec_dirs)
    return validate_interfaces(items)


def _run_privacy(
    _sdd_config: SddConfig, test_items: list[pytest.Item] | None
) -> list[Finding]:
    if not test_items:
        return []
    paths: list[Path] = []
    seen: set[Path] = set()
    for item in test_items:
        path = item.path
        if path in seen:
            continue
        seen.add(path)
        paths.append(path)
    return validate_files(paths)

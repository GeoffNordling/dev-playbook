"""Pytest collectors and test items for OFT spec validation.

SpecFile      -- File collector for one .md spec file; yields SpecLintItem
SpecLintItem  -- Runs all structural lint checks for one spec file
SpecTraceItem -- Runs OFT JAR traceability check across all spec directories
"""

import subprocess
from pathlib import Path

import pytest

from pytest_sdd.config import SddConfig
from pytest_sdd.lint import run_all as run_lint
from pytest_sdd.markers import create_coverage_dir
from pytest_sdd.parser import parse_spec_file
from pytest_sdd.trace import require_java, resolve_oft_jar, run_oft_trace


class SpecLintError(Exception):
    """Raised when one or more lint checks fail for a spec file."""


class SpecTraceError(Exception):
    """Raised when OFT trace finds coverage gaps."""


class SpecFile(pytest.File):
    """Virtual file collector for one OFT markdown spec file.

    Created programmatically in pytest_collection_modifyitems; not triggered
    by pytest's own file walker.
    """

    def __init__(self, *, sdd_config: SddConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sdd_config = sdd_config

    def collect(self):
        text = self.path.read_text(encoding="utf-8")
        items = parse_spec_file(self.path)
        yield SpecLintItem.from_parent(
            self,
            name="lint",
            spec_items=items,
            file_text=text,
        )


class SpecLintItem(pytest.Item):
    """Structural lint check for one OFT spec file."""

    def __init__(self, *, spec_items, file_text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.spec_items = spec_items
        self.file_text = file_text
        self.add_marker(pytest.mark.spec)

    def runtest(self) -> None:
        errors = run_lint(self.path, self.file_text, self.spec_items)
        if errors:
            raise SpecLintError("\n".join(errors))

    def repr_failure(self, excinfo, style=None):
        if isinstance(excinfo.value, SpecLintError):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style)

    def reportinfo(self):
        return self.path, None, f"spec-lint: {self.path.name}"


class SpecTraceItem(pytest.Item):
    """OFT traceability check across all configured spec directories."""

    def __init__(
        self,
        *,
        sdd_config: SddConfig,
        test_items: list[pytest.Item],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.sdd_config = sdd_config
        self.test_items = test_items
        self.add_marker(pytest.mark.spec)

    def runtest(self) -> None:
        jar_path = resolve_oft_jar(self.sdd_config.oft_jar)
        require_java()

        # Validate all spec dirs exist
        for spec_dir in self.sdd_config.spec_dirs:
            if not spec_dir.is_dir():
                raise FileNotFoundError(f"Spec directory not found: {spec_dir}")

        # Generate coverage file from pytest markers (if any)
        coverage_tmp = create_coverage_dir(self.test_items)

        # Single OFT invocation across all spec dirs + coverage
        input_paths = list(self.sdd_config.spec_dirs)
        if coverage_tmp:
            input_paths.append(Path(coverage_tmp.name))

        try:
            run_oft_trace(jar_path, input_paths)
        except subprocess.CalledProcessError as exc:
            raise SpecTraceError(f"OFT trace failed:\n{exc.output}") from exc
        finally:
            if coverage_tmp:
                coverage_tmp.cleanup()

    def repr_failure(self, excinfo, style=None):
        if isinstance(excinfo.value, (SpecTraceError, FileNotFoundError, RuntimeError)):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style)

    def reportinfo(self):
        return Path("."), None, "spec-trace: OFT traceability"

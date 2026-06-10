"""Tests for workflow_state_data.phases — phase ordering and canonical labels."""

import importlib.machinery
import importlib.util
from pathlib import Path

from workflow_state_data import phases

BOOTSTRAP_LABELS = Path(__file__).resolve().parents[1] / "bin" / "bootstrap-labels"


def test_code_review_back_to_tdd_is_backward() -> None:
    assert phases.is_backward("code-pr-review", "tdd") is True


def test_tdd_to_code_review_is_forward() -> None:
    assert phases.is_backward("tdd", "code-pr-review") is False


def test_sdd_spec_review_back_to_sdd_specs_is_backward() -> None:
    assert phases.is_backward("sdd-spec-review", "sdd-specs") is True


def test_canonical_labels_include_phase_and_metadata() -> None:
    assert "phase:tdd" in phases.CANONICAL_LABELS
    assert "category:bug" in phases.CANONICAL_LABELS
    assert "mode:direct" in phases.CANONICAL_LABELS
    assert "tests:yes" in phases.CANONICAL_LABELS


def test_canonical_labels_match_bootstrap_labels_script() -> None:
    # The script has no .py extension, so the loader must be given explicitly.
    loader = importlib.machinery.SourceFileLoader(
        "bootstrap_labels", str(BOOTSTRAP_LABELS)
    )
    spec = importlib.util.spec_from_file_location(
        "bootstrap_labels", BOOTSTRAP_LABELS, loader=loader
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    minted = {name for name, _, _ in module.canonical_labels()}

    assert minted == phases.CANONICAL_LABELS

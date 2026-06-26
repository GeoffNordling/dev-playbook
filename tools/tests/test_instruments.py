"""The instrument source of truth: the valid model and effort value sets."""

from judgments.instruments import VALID_EFFORTS, VALID_MODELS


def test_valid_efforts_are_the_documented_levels() -> None:
    assert frozenset({"low", "medium", "high", "xhigh", "max"}) == VALID_EFFORTS


def test_valid_models_are_the_current_full_ids() -> None:
    assert (
        frozenset(
            {
                "claude-opus-4-8",
                "claude-sonnet-4-6",
                "claude-haiku-4-5-20251001",
            }
        )
        == VALID_MODELS
    )

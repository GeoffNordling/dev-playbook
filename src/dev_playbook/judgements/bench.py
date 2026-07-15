"""The bench source of truth: the model and effort values a judge may run under.

These mirror the values the agent runtime accepts -- full model IDs, not aliases,
because the full ID is what gets hashed into a judgement's content key, so the
cached judge identity is exact. The lists are maintained by hand: when a new model
ships, add its full ID here, or an otherwise-valid config will be rejected. Both
the loader and the lint validate ``model``/``effort`` against these sets.
"""

VALID_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})

VALID_MODELS = frozenset(
    {
        "claude-opus-4-8",
        "claude-sonnet-5",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    }
)

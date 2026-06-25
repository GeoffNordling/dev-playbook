"""Judgments: the deterministic core of an LLM-judge cache.

Defines what a judgment is and, for one judgment, computes the content fingerprint
(``key``) and the exact text to hand the judge (``prompt``). Makes no LLM calls and
does no caching: pure, local, fully unit-testable standard-library Python. A separate
layer calls the LLM, stores the fingerprints, and decides what to skip.
"""

from judgments.config import PROMPT, SCHEMA
from judgments.model import Judgment

__all__ = ["PROMPT", "SCHEMA", "Judgment"]

"""Judgments: the deterministic core of the LLM-judge cache.

This library owns the definition of a judgment -- a single yes/no question about
one or more files -- and, for a given judgment, computes the two things the rest
of the system needs: a content fingerprint (``key``) that re-keys only when an
answer-relevant input changes, and the exact ``prompt`` text to hand the judge.
It makes no LLM calls and does no caching itself.
"""

from judgments.core import PROMPT, SCHEMA, Judgment, Prepared, prepare

__all__ = ["PROMPT", "SCHEMA", "Judgment", "Prepared", "prepare"]

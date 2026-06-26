"""The judgment model and the fixed judge configuration.

A judgment is a single yes/no question about one or more files, ruled on by an
LLM judge. This module owns the judgment vocabulary -- claim, evidence,
reference -- the ``Judgment`` verdict type, and the two fixed pieces of judge
configuration (``PROMPT`` and ``SCHEMA``) that the downstream layer must run the
judge under verbatim, because they are folded into the content key.
"""

from typing import Any, NamedTuple


class Judgment(NamedTuple):
    """A judge's ruling on a claim: a verdict plus one paragraph of reasoning."""

    verdict: bool
    opinion: str


# The general judge prompt. It is part of the content key, so editing it re-keys
# (and therefore re-runs) every judgment everywhere -- by design.
PROMPT = """\
You are a careful and fair judge. You are given a single CLAIM — a proposition
stated in prose — and you must decide whether it holds.

You are given the material to judge it against:
- EVIDENCE — the material the claim is about. This is what you are ruling on.
- REFERENCE — optional additional material you may consult for context. It is not
  itself under judgment; use it only to interpret or corroborate the evidence.

Each piece of material is delivered in its own XML tag: the claim in <claim>, each
evidence file in an <evidence> tag, and each reference file in a <reference> tag. Every
<evidence> and <reference> tag carries the file's path in a path attribute, so you can
match file names mentioned in the claim to the right material.

Decide by these rules:
1. Base your verdict only on the CLAIM, the EVIDENCE, and the REFERENCE provided. Do
   not assume facts about this material that it does not show, and do not rely on
   remembered knowledge of these specific files or systems. You may use general
   knowledge to read and interpret the material, but not to supply evidence that is
   absent.
2. Judge the substance of the claim. It holds (verdict true) when the material
   supports it on the points that matter; it does not hold (false) when the material
   contradicts it or leaves a load-bearing part of it unsupported. Do not fail a claim
   that is true in substance over trivial or immaterial gaps.
3. Judge what the material says or commits to, not how it is written. Ignore cosmetic
   or stylistic matters unless the claim is specifically about them.
4. If the claim is too ambiguous to decide, or the material provided is not enough to
   decide it, return false and explain why — prefer a clear false over a confident
   guess.

Return:
- verdict — true if the material supports the claim in substance; false if it
  contradicts the claim or leaves a material part unsupported.
- opinion — one paragraph. On a false verdict, name the specific defect and where it
  occurs (quote or cite it). On a true verdict, briefly state why the evidence
  supports the claim.

The CLAIM, EVIDENCE, and any REFERENCE follow, each in its own XML tag."""


# The structured-output contract the judge must fill: the JSON schema of Judgment.
SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": {"type": "boolean"},
        "opinion": {"type": "string"},
    },
    "required": ["verdict", "opinion"],
    "additionalProperties": False,
}

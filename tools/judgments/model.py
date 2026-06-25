"""The judgment model: a single yes/no question about files, answered by a judge."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Judgment:
    """A judge's ruling on a claim: a verdict and one paragraph of reasoning."""

    verdict: bool
    opinion: str

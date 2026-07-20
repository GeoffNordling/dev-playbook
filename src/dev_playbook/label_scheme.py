"""The canonical GitHub label scheme, as policy-as-data.

One JSON file (``label_scheme.json``, beside this module) is the single source
of the workspace's label scheme. It is structured by dimension — each dimension
carries its label color, a description recipe, and its values — so the two
consumers read one authority and cannot disagree: ``bootstrap-labels`` mints the
scheme into a repo, and ``workspace-lint`` checks live repos against it.

The semantic authority for what the labels *mean* stays software-factory.md's label
table and state-machine graph; this file is the operational data. The
scheme-vs-graph consistency between the two is left to a judgement, never parsed
here.
"""

import json
from dataclasses import dataclass
from pathlib import Path

SCHEME_PATH = Path(__file__).parent / "label_scheme.json"


@dataclass(frozen=True)
class Dimension:
    """One label dimension: its name prefix, color, description recipe, values."""

    name: str
    color: str
    description: str  # a recipe with a ``{value}`` placeholder
    values: tuple[str, ...]


def _dimensions() -> list[Dimension]:
    """The scheme's dimensions, parsed from the JSON data file."""
    raw = json.loads(SCHEME_PATH.read_text(encoding="utf-8"))
    return [
        Dimension(
            name=dim["name"],
            color=dim["color"],
            description=dim["description"],
            values=tuple(dim["values"]),
        )
        for dim in raw["dimensions"]
    ]


def canonical_labels() -> list[tuple[str, str, str]]:
    """Every canonical label as ``(name, color, description)``, in scheme order.

    The closed-world label set: ``<dimension>:<value>`` for every value of every
    dimension, its dimension's color, and its description with ``{value}`` filled
    in. This is what bootstrap-labels mints and what the label-scheme audit
    checks a repo against at full parity.
    """
    return [
        (f"{dim.name}:{value}", dim.color, dim.description.format(value=value))
        for dim in _dimensions()
        for value in dim.values
    ]


def values_by_dimension() -> dict[str, set[str]]:
    """Map each dimension name to the set of values the scheme allows.

    The membership authority for the four-tuple validity check: a label
    ``<dimension>:<value>`` is valid when ``value`` is in this dimension's set.
    """
    return {dim.name: set(dim.values) for dim in _dimensions()}

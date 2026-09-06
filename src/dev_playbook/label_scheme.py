"""The canonical GitHub label scheme, as policy-as-data.

One JSON file (``label_scheme.json``, beside this module) is the single source
of the workspace's label scheme. It is structured by dimension — each dimension
carries its label color and its values, and each value carries the one sentence
that is both its GitHub label description and its meaning in the Label Scheme
standard — so the three consumers read one authority and cannot disagree:
``bootstrap-labels`` mints the scheme into a repo, ``workspace-lint`` checks
live repos against it, and ``labelgen`` renders it as the table in
standards/tracking/label-scheme.md.
"""

import json
from dataclasses import dataclass
from pathlib import Path

SCHEME_PATH = Path(__file__).parent / "label_scheme.json"

# GitHub truncates a label description past this many characters, and a
# truncated description would silently disagree with the standard's table.
DESCRIPTION_LIMIT = 100


@dataclass(frozen=True)
class Dimension:
    """One label dimension: its name prefix, color, and values with descriptions."""

    name: str
    color: str
    values: dict[str, str]  # value -> description, in scheme order


def _dimensions() -> list[Dimension]:
    """The scheme's dimensions, parsed from the JSON data file."""
    raw = json.loads(SCHEME_PATH.read_text(encoding="utf-8"))
    dimensions = [
        Dimension(name=dim["name"], color=dim["color"], values=dict(dim["values"]))
        for dim in raw["dimensions"]
    ]
    for dim in dimensions:
        for value, description in dim.values.items():
            if len(description) > DESCRIPTION_LIMIT:
                raise ValueError(
                    f"{dim.name}:{value} description is {len(description)} "
                    f"characters; GitHub allows {DESCRIPTION_LIMIT}"
                )
    return dimensions


def canonical_labels() -> list[tuple[str, str, str]]:
    """Every canonical label as ``(name, color, description)``, in scheme order.

    The closed-world label set: ``<dimension>:<value>`` for every value of every
    dimension, its dimension's color, and the value's description. This is what
    bootstrap-labels mints and what the label-scheme audit checks a repo against
    at full parity.
    """
    return [
        (f"{dim.name}:{value}", dim.color, description)
        for dim in _dimensions()
        for value, description in dim.values.items()
    ]


def values_by_dimension() -> dict[str, set[str]]:
    """Map each dimension name to the set of values the scheme allows.

    The membership authority for the label validity checks: a label
    ``<dimension>:<value>`` is valid when ``value`` is in this dimension's set.
    """
    return {dim.name: set(dim.values) for dim in _dimensions()}


def render_table() -> str:
    """The scheme as the markdown table the Label Scheme standard carries.

    One row per label, in scheme order; the description column is the same
    sentence GitHub shows on the label.
    """
    lines = ["| Label | Description |", "|---|---|"]
    lines.extend(
        f"| `{name}` | {description} |" for name, _, description in canonical_labels()
    )
    return "\n".join(lines) + "\n"

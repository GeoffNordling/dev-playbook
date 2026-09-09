"""The two records a registry entry is made of: a kind, and one view it writes.

They live below the registry rather than inside it so that a kind module can
name them without importing the registry that lists it. The registry imports
every kind module to build ``KINDS``; were a kind module to import the registry
back, importing that kind first would re-enter a half-built registry and fail.
``registry`` re-exports both names, so a reader still finds them where the
design puts them.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class View:
    """One view file a generator built, before anything writes it to disk.

    ``relpath`` is the path under the checkout directory: ``index-tree.json``
    for a per-checkout kind, ``markdown-file/<identity>.json`` for a per-subject
    one. ``envelope`` is the whole file, the seven fields ``state.envelope``
    builds.
    """

    relpath: str
    envelope: dict[str, Any]


@dataclass(frozen=True)
class Kind:
    """One registered kind: what it is called, and what writes its view files.

    ``version`` is the version of the kind's payload schema, which is the
    ``kind_version`` its envelopes carry. ``per_subject`` says whether the kind
    writes one view file per checkout or one per thing it describes, which is
    what decides how a refresh replaces its files.
    """

    name: str
    version: int
    per_subject: bool
    generate: Callable[[Path], list[View]]

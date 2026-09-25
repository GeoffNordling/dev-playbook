"""A stint's target, read from the workstream: the rules, and the files that set them.

The head file's planned stint entry names the rule ids the stint targets:

    ## Stints

    - **Planned.** Budget: five iterations. Targets: `wordcount.counts-words`.

Each id is a rule of a draft Standard, a Markdown file typed ``Standard`` in
the workstream folder, whose trailer says whether it is deterministic or
stochastic. The deterministic ids go to the workstream's ``check``, an
executable file beside the head file, run from the repository's root as
``<workstream>/check <id>…``; its exit 0 is zero findings. The stochastic ids
would go to a judge, which is not built, so a stochastic target is refused.

The head file, the draft Standards, and ``check`` set the target, and no
call of the stint may change them. They are read from the work copy as
plain files at launch, before any call.
"""

import os
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from dev_playbook.checks.doc_type import BULLET, STINT_OPENING, TARGETS
from dev_playbook.model import MarkdownFile, ModelError, parse_markdown
from dev_playbook.stint import workcopy

CHECK = "check"
"""The name of the workstream's check, in its folder."""


class TargetFault(Exception):
    """The workstream does not name a target the stint can run toward."""


@dataclass(frozen=True)
class Target:
    """The rules a stint targets, and the files that set them."""

    rules: tuple[str, ...]
    """The deterministic rule ids the planned stint entry targets."""
    command: str
    """The target check: ``<workstream>/check`` with the rule ids."""
    files: dict[str, str]
    """The head file, the draft Standards, and ``check``, by path, as read at launch."""


def read_target(copy: Path, workstream: str) -> Target:
    """Read the target from the work copy; raise TargetFault when there is none."""
    head = f"{workstream}/WORKSTREAM.md"
    check = f"{workstream}/{CHECK}"
    files = {head: workcopy.read_plain(copy, head)}
    kinds: dict[str, str] = {}
    for rel in markdown_files(copy, workstream):
        text = workcopy.read_plain(copy, rel)
        doc = parse(rel, text)
        if doc.frontmatter and doc.frontmatter.get("type") == "Standard":
            files[rel] = text
            kinds |= {trailer.id: trailer.kind for trailer in doc.trailers}
    ids = planned_targets(parse(head, files[head]))
    unknown = [i for i in ids if i not in kinds]
    if unknown:
        raise TargetFault(f"no draft Standard holds {', '.join(unknown)}")
    stochastic = [i for i in ids if kinds[i] == "stochastic"]
    if stochastic:
        raise TargetFault(
            f"{', '.join(stochastic)} is stochastic, and the judge is not built"
        )
    if not (copy / check).is_file() or not os.access(copy / check, os.X_OK):
        raise TargetFault(f"{check} is not an executable file")
    files[check] = workcopy.read_plain(copy, check)
    return Target(
        rules=tuple(ids),
        command=shlex.join([check, *ids]),
        files=files,
    )


def markdown_files(copy: Path, workstream: str) -> list[str]:
    """Every Markdown file in the workstream folder, as repository paths."""
    found = []
    for folder, dirs, files in os.walk(copy / workstream):
        dirs.sort()
        found += [
            (Path(folder) / file).relative_to(copy).as_posix()
            for file in sorted(files)
            if file.endswith(".md")
        ]
    return found


def parse(rel: str, text: str) -> MarkdownFile:
    """The Markdown file parsed; a file the model cannot parse is a TargetFault."""
    try:
        return parse_markdown(rel, text)
    except ModelError as err:
        raise TargetFault(str(err)) from err


def planned_targets(head: MarkdownFile) -> list[str]:
    """The rule ids of the head file's planned stint entry, the first in ``## Stints``."""
    try:
        section = head.section("stints")
    except KeyError:
        raise TargetFault(f"{head.path} has no ## Stints") from None
    starts = [i for i, (_, text) in enumerate(section) if BULLET.match(text)]
    if not starts:
        raise TargetFault(f"{head.path} has no planned stint entry")
    end = starts[1] if len(starts) > 1 else len(section)
    entry = " ".join(text for _, text in section[starts[0] : end])
    opening = STINT_OPENING.match(entry)
    if opening is None or opening.group(1) != "Planned":
        raise TargetFault(f"{head.path} has no planned stint entry")
    targets = TARGETS.search(entry)
    if targets is None:
        raise TargetFault(f"the planned stint entry in {head.path} names no Targets")
    return re.findall(r"`([^`]+)`", targets.group(1))

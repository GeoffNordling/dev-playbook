"""Behavioral tests for dev_playbook.label_scheme, labelgen, and bootstrap-labels.

The scheme module is the single source every consumer reads; these tests pin
the canonical label set (name, color, description) byte-for-byte, hold the
Label Scheme standard's table to the same data, and drive the bootstrap shim
end-to-end against a fake ``gh`` that records the label operations.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

from dev_playbook import label_scheme

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts" / "bootstrap-labels"
LABELGEN = ROOT / "scripts" / "labelgen"
DOC = ROOT / "standards" / "tracking" / "label-scheme.md"

# The canonical scheme, in mint order: the metadata labels (category, mode,
# tests) grey, then every phase label yellow, then the wayfinder labels blue —
# a planning dimension, coloured to read differently at a glance — and last the
# origin label, grey provenance minted onto what the factory itself opens.
EXPECTED_LABELS = [
    (
        "category:maintenance",
        "cccccc",
        "Maintains shipped state: a fix, hygiene, or polish that adds no capability.",
    ),
    (
        "category:extension",
        "cccccc",
        "Extends a system past its shipped line: a capability it lacks today.",
    ),
    (
        "mode:direct",
        "cccccc",
        "Built by the software factory against its brief; ends in merged code.",
    ),
    (
        "mode:spike",
        "cccccc",
        "A question; the answer closes the issue in a comment, and no PR opens.",
    ),
    (
        "mode:session",
        "cccccc",
        "Led by the user in a session: worked in a worktree, PR opened by hand, "
        "never dispatched.",
    ),
    (
        "tests:yes",
        "cccccc",
        "The work writes or changes tests, so the build runs test-first.",
    ),
    (
        "tests:no",
        "cccccc",
        "The work touches no tests, so the build implements directly.",
    ),
    (
        "phase:intake",
        "fbca04",
        "Untriaged; intake authors the brief and routes the issue.",
    ),
    (
        "phase:design",
        "fbca04",
        "The approach is explored and the brief re-authored or decomposed.",
    ),
    ("phase:spike", "fbca04", "The question is being answered."),
    (
        "phase:build",
        "fbca04",
        "Released to the factory; the build node runs next.",
    ),
    (
        "phase:pr-review",
        "fbca04",
        "A pull request is open and in the review loop.",
    ),
    (
        "wayfinder:map",
        "1d76db",
        "A wayfinder map: the planning epic the /wayfinder skill drives.",
    ),
    (
        "wayfinder:research",
        "1d76db",
        "A decision ticket resolved by research: sources outside the working "
        "directory.",
    ),
    (
        "wayfinder:prototype",
        "1d76db",
        "A decision ticket resolved by a cheap, concrete artifact to react to.",
    ),
    (
        "wayfinder:grilling",
        "1d76db",
        "A decision ticket resolved in conversation with the user.",
    ),
    (
        "wayfinder:task",
        "1d76db",
        "A decision ticket resolved by manual work that unblocks a decision.",
    ),
    (
        "origin:deferral",
        "cccccc",
        "Opened by the factory to hold work a review suggested and the run deferred.",
    ),
]


def test_canonical_labels_match_the_scheme_in_mint_order() -> None:
    assert label_scheme.canonical_labels() == EXPECTED_LABELS


def test_every_description_fits_a_github_label() -> None:
    for name, _, description in label_scheme.canonical_labels():
        assert len(description) <= label_scheme.DESCRIPTION_LIMIT, name


def test_an_overlong_description_fails_loud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scheme = tmp_path / "scheme.json"
    scheme.write_text(
        '{"dimensions": [{"name": "d", "color": "cccccc", '
        '"values": {"v": "' + "x" * 101 + '"}}]}'
    )
    monkeypatch.setattr(label_scheme, "SCHEME_PATH", scheme)

    with pytest.raises(ValueError, match="d:v description is 101 characters"):
        label_scheme.canonical_labels()


def test_values_by_dimension_exposes_every_dimension() -> None:
    values = label_scheme.values_by_dimension()

    assert values["category"] == {"maintenance", "extension"}
    assert values["mode"] == {"direct", "spike", "session"}
    assert values["tests"] == {"yes", "no"}
    assert values["phase"] == {"intake", "design", "spike", "build", "pr-review"}
    assert values["wayfinder"] == {"map", "research", "prototype", "grilling", "task"}
    assert values["origin"] == {"deferral"}


# --- the standard's table is the scheme, rendered ---


def test_render_table_is_one_row_per_label_in_scheme_order() -> None:
    lines = label_scheme.render_table().splitlines()

    assert lines[:2] == ["| Label | Description |", "|---|---|"]
    assert [line.split("`")[1] for line in lines[2:]] == [
        name for name, _, _ in EXPECTED_LABELS
    ]


def test_label_scheme_standard_carries_the_rendered_table() -> None:
    """The doc's table is generated, never hand-edited: drift fails here."""
    text = DOC.read_text(encoding="utf-8")
    block = re.search(
        r"<!-- labelgen:start -->\n(.*?)<!-- labelgen:end -->", text, re.DOTALL
    )
    assert block is not None, "label-scheme.md has no labelgen block"
    assert block.group(1) == label_scheme.render_table()


def test_labelgen_check_passes_on_the_committed_doc() -> None:
    result = subprocess.run(
        ["python3", str(LABELGEN), "--check"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


# --- the bootstrap-labels shim mints from the scheme ---

FAKE_GH = """\
#!/usr/bin/env python3
import os, sys

args = sys.argv[1:]
log = os.environ["FAKE_GH_LOG"]


def record(action, name):
    with open(log, "a") as handle:
        handle.write(f"{action} {name}\\n")


if args[:2] == ["label", "list"]:
    print("[]")
elif args[:2] == ["label", "create"]:
    record("create", args[2])
elif args[:2] == ["label", "edit"]:
    record("edit", args[2])
elif args[:2] == ["label", "delete"]:
    record("delete", args[2])
else:
    sys.exit(1)
"""


def test_bootstrap_labels_mints_the_whole_scheme(tmp_path: Path) -> None:
    gh_dir = tmp_path / "fakebin"
    gh_dir.mkdir()
    gh = gh_dir / "gh"
    gh.write_text(FAKE_GH)
    os.chmod(gh, 0o755)
    log = tmp_path / "gh.log"
    env = dict(os.environ, PATH=f"{gh_dir}:{os.environ['PATH']}", FAKE_GH_LOG=str(log))

    result = subprocess.run(
        ["python3", str(BOOTSTRAP)], capture_output=True, text=True, env=env
    )

    assert result.returncode == 0, result.stdout + result.stderr
    created = {
        line.removeprefix("create ")
        for line in log.read_text().splitlines()
        if line.startswith("create ")
    }
    assert created == {name for name, _, _ in EXPECTED_LABELS}

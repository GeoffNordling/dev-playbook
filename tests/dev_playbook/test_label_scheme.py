"""Behavioral tests for dev_playbook.label_scheme and the bootstrap-labels shim.

The scheme module is the single source both consumers read; these tests pin the
canonical label set (name, color, description) byte-for-byte so the policy-as-data
lift preserves exactly what bootstrap-labels minted before, and drive the shim
end-to-end against a fake ``gh`` that records the label operations.
"""

import os
import subprocess
from pathlib import Path

from dev_playbook import label_scheme

BOOTSTRAP = Path(__file__).resolve().parents[2] / "scripts" / "bootstrap-labels"

# The canonical scheme, in mint order: the six fixed-value metadata labels
# (category, mode, tests) grey, then every phase label yellow, then the wayfinder
# labels blue — a planning dimension, coloured to read differently at a glance —
# and last the origin label, grey provenance minted onto what the factory itself
# opens.
EXPECTED_LABELS = [
    ("category:maintenance", "cccccc", "Category: maintenance."),
    ("category:extension", "cccccc", "Category: extension."),
    ("mode:direct", "cccccc", "Mode: direct."),
    ("mode:spike", "cccccc", "Mode: spike."),
    ("tests:yes", "cccccc", "Tests: yes."),
    ("tests:no", "cccccc", "Tests: no."),
    ("phase:intake", "fbca04", "Phase: intake."),
    ("phase:design", "fbca04", "Phase: design."),
    ("phase:spike", "fbca04", "Phase: spike."),
    ("phase:build", "fbca04", "Phase: build."),
    ("phase:pr-review", "fbca04", "Phase: pr-review."),
    ("wayfinder:map", "1d76db", "Wayfinder: map."),
    ("wayfinder:research", "1d76db", "Wayfinder: research."),
    ("wayfinder:prototype", "1d76db", "Wayfinder: prototype."),
    ("wayfinder:grilling", "1d76db", "Wayfinder: grilling."),
    ("wayfinder:task", "1d76db", "Wayfinder: task."),
    ("origin:deferral", "cccccc", "Origin: deferral."),
]


def test_canonical_labels_match_the_scheme_in_mint_order() -> None:
    assert label_scheme.canonical_labels() == EXPECTED_LABELS


def test_scheme_preserves_the_spike_labels() -> None:
    names = {name for name, _, _ in label_scheme.canonical_labels()}

    assert "mode:spike" in names
    assert "phase:spike" in names


def test_values_by_dimension_exposes_the_tuple_dimensions() -> None:
    values = label_scheme.values_by_dimension()

    assert values["category"] == {"maintenance", "extension"}
    assert values["mode"] == {"direct", "spike"}
    assert values["tests"] == {"yes", "no"}
    assert "spike" in values["phase"]
    assert "pr-review" in values["phase"]


def test_values_by_dimension_exposes_the_wayfinder_dimension() -> None:
    values = label_scheme.values_by_dimension()

    assert values["wayfinder"] == {"map", "research", "prototype", "grilling", "task"}


def test_values_by_dimension_exposes_the_origin_dimension() -> None:
    """Provenance on what the factory opens for itself, and one value only.

    A deferral stub is the whole of it today: no speculative value is minted
    ahead of something that opens issues under it.
    """
    values = label_scheme.values_by_dimension()

    assert values["origin"] == {"deferral"}


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
    assert "mode:spike" in created
    assert "phase:spike" in created

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

# The canonical scheme, in mint order: the eight fixed-value metadata labels
# (category, mode, tests, status) grey, then every phase label yellow. This is
# exactly the set the pre-lift bootstrap-labels hard-coded.
EXPECTED_LABELS = [
    ("category:bug", "cccccc", "Category: bug. See workflow.md."),
    ("category:enhancement", "cccccc", "Category: enhancement. See workflow.md."),
    ("mode:sdd", "cccccc", "Mode: sdd. See workflow.md."),
    ("mode:direct", "cccccc", "Mode: direct. See workflow.md."),
    ("mode:spike", "cccccc", "Mode: spike. See workflow.md."),
    ("tests:yes", "cccccc", "Tests: yes. See workflow.md."),
    ("tests:no", "cccccc", "Tests: no. See workflow.md."),
    ("status:parked", "cccccc", "Status: parked. See workflow.md."),
    ("phase:intake", "fbca04", "Phase: intake. See workflow.md."),
    ("phase:sdd-specs", "fbca04", "Phase: sdd-specs. See workflow.md."),
    ("phase:sdd-spec-review", "fbca04", "Phase: sdd-spec-review. See workflow.md."),
    ("phase:sdd-tdd", "fbca04", "Phase: sdd-tdd. See workflow.md."),
    ("phase:sdd-pr-review", "fbca04", "Phase: sdd-pr-review. See workflow.md."),
    ("phase:design", "fbca04", "Phase: design. See workflow.md."),
    ("phase:tdd", "fbca04", "Phase: tdd. See workflow.md."),
    ("phase:build", "fbca04", "Phase: build. See workflow.md."),
    ("phase:pr-review", "fbca04", "Phase: pr-review. See workflow.md."),
    ("phase:spike", "fbca04", "Phase: spike. See workflow.md."),
]


def test_canonical_labels_match_the_scheme_in_mint_order() -> None:
    assert label_scheme.canonical_labels() == EXPECTED_LABELS


def test_scheme_preserves_the_spike_labels() -> None:
    names = {name for name, _, _ in label_scheme.canonical_labels()}

    assert "mode:spike" in names
    assert "phase:spike" in names


def test_values_by_dimension_exposes_the_tuple_dimensions() -> None:
    values = label_scheme.values_by_dimension()

    assert values["category"] == {"bug", "enhancement"}
    assert values["mode"] == {"sdd", "direct", "spike"}
    assert values["tests"] == {"yes", "no"}
    assert "spike" in values["phase"]
    assert "pr-review" in values["phase"]


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

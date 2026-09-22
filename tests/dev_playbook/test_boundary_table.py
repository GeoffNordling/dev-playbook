"""Behavioral tests for boundary-table, the generator that writes and lints it.

Each fixture is a dev-playbook-mode repo with a pre-commit config, a Makefile,
and a workflow, so the derivation reads real wiring: ``make -n`` runs against
the fixture's Makefile, and nothing subprocesses a detector.
"""

from pathlib import Path

import pytest

from dev_playbook import boundary_table as bt

CANONICAL = "standards/build/canonical/.pre-commit-config.yaml"
ROSTER = ("repo-lint", "ref-lint")

CONFIG = """\
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v1
    hooks:
      - id: ruff-check
      - id: ruff-format
  - repo: local
    hooks:
      - id: make-check
        entry: make check
        language: system
        stages: [pre-push]
      - id: playbook-lint
        entry: scripts/playbook-lint
        language: script
"""

MAKEFILE = """\
.PHONY: lint typecheck check
lint:
\tuv run ruff check .
typecheck:
\tuv run mypy src
check: lint typecheck
\tuvx pre-commit run --all-files
"""

WORKFLOW = """\
name: ci
on: [push]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - run: uvx pre-commit run --all-files
        env:
          SKIP: ref-lint
"""

DEPENDENCIES = {
    "mypy": ("python.a",),
    "ruff-check": ("python.b",),
    "ruff-format": ("python.c",),
}


@pytest.fixture(autouse=True)
def small_roster(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bt, "DETECTORS", ROSTER)
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset({"workspace-lint"}))
    monkeypatch.setattr(bt, "DEPENDENCY_RULES", DEPENDENCIES)


def dev_playbook(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    """A dev-playbook-mode repo wired like the real one, in miniature."""
    files = {
        CANONICAL: "",
        ".pre-commit-config.yaml": CONFIG,
        "Makefile": MAKEFILE,
        ".github/workflows/ci.yml": WORKFLOW,
        ".pre-commit-hooks.yaml": "- id: playbook-lint\n",
        **(extra or {}),
    }
    repo = tmp_path / "repo"
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return repo


# --- the derivation ---------------------------------------------------------


def test_rows_are_the_verifier_tables_addresses_with_their_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset())
    repo = dev_playbook(tmp_path)

    table = bt.derive(repo)

    assert table.rows == {
        "mypy": ("push",),
        "ruff-check": ("commit", "push", "ci"),
        "ruff-format": ("commit", "push", "ci"),
        "scripts/ref-lint": ("commit", "push"),
        "scripts/repo-lint": ("commit", "push", "ci"),
    }
    assert table.findings == []


def test_the_aggregate_hook_runs_the_manifest_check_where_a_manifest_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        bt, "DEPENDENCY_RULES", {"pre-commit validate-manifest": ("d.a",)}
    )
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset())
    repo = dev_playbook(tmp_path)

    assert bt.derive(repo).rows["pre-commit validate-manifest"] == (
        "commit",
        "push",
        "ci",
    )

    (repo / ".pre-commit-hooks.yaml").unlink()
    table = bt.derive(repo)

    assert table.rows["pre-commit validate-manifest"] == ()
    assert [f.rule for f in table.findings] == [bt.EVERY_ADDRESS_RUNS_SOMEWHERE]


def test_a_registered_ungated_audit_is_on_demand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset({"ref-lint"}))
    repo = dev_playbook(
        tmp_path,
        {
            ".pre-commit-config.yaml": CONFIG.replace(
                "      - id: playbook-lint\n        entry: scripts/playbook-lint\n"
                "        language: script\n",
                "      - id: repo-lint\n        entry: scripts/repo-lint\n"
                "        language: script\n",
            )
        },
    )
    (repo / ".github/workflows/ci.yml").unlink()

    table = bt.derive(repo)

    assert table.rows["scripts/ref-lint"] == ("on-demand",)
    assert table.findings == []


def test_an_address_at_no_gate_and_unregistered_is_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset())
    repo = dev_playbook(
        tmp_path, {".pre-commit-config.yaml": "repos: []\n", "Makefile": ""}
    )

    table = bt.derive(repo)

    assert table.rows["scripts/repo-lint"] == ()
    assert ("scripts/repo-lint", bt.EVERY_ADDRESS_RUNS_SOMEWHERE) in [
        (f.file, f.rule) for f in table.findings
    ]


def test_a_registered_audit_a_gate_runs_is_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bt, "UNGATED_AUDITS", frozenset({"repo-lint"}))
    repo = dev_playbook(tmp_path)

    table = bt.derive(repo)

    assert table.rows["scripts/repo-lint"] == ("commit", "push", "ci")
    assert [(f.file, f.rule) for f in table.findings] == [
        ("scripts/repo-lint", bt.EVERY_ADDRESS_RUNS_SOMEWHERE)
    ]
    assert "registered" in table.findings[0].message


def test_a_workflow_skip_removes_that_detector_from_ci_only(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    assert bt.ci_addresses(repo) == {
        "pre-commit validate-manifest",
        "ruff-check",
        "ruff-format",
        "scripts/repo-lint",
    }


def test_a_workflow_that_runs_make_check_expands_the_makefile(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {
            ".github/workflows/ci.yml": WORKFLOW.replace(
                "uvx pre-commit run --all-files", "make check"
            )
        },
    )

    assert "mypy" in bt.ci_addresses(repo)
    assert "scripts/ref-lint" not in bt.ci_addresses(repo)


def test_a_make_target_that_does_not_exist_cannot_run(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path, {"Makefile": ""})

    with pytest.raises(bt.CannotRun, match="make -n check"):
        bt.derive(repo)


def test_a_hook_without_stages_fires_at_every_gate() -> None:
    assert bt.hook_gates({"id": "x"}, {}) == {"commit", "push"}
    assert bt.hook_gates({"id": "x", "stages": ["pre-push"]}, {}) == {"push"}
    assert bt.hook_gates({"id": "x"}, {"default_stages": ["commit"]}) == {"commit"}


def test_render_is_a_header_then_sorted_rows() -> None:
    text = bt.render_table({"scripts/b": ("on-demand",), "mypy": ("push",)})

    assert text.startswith("# The boundary table")
    assert text.endswith("mypy: [push]\nscripts/b: [on-demand]\n")


# --- consumer mode ----------------------------------------------------------


def test_a_consumer_rows_only_its_own_detectors(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {
            ".pre-commit-config.yaml": (
                "repos:\n  - repo: local\n    hooks:\n"
                "      - id: widget-lint\n        entry: scripts/widget-lint\n"
            )
        },
    )
    (repo / CANONICAL).unlink()

    table = bt.derive(repo)

    assert table.rows == {"scripts/widget-lint": ("commit", "push", "ci")}
    assert table.findings == []


# --- the walk ---------------------------------------------------------------


def test_missing_stale_and_current_tables(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    assert [(f.file, f.rule) for f in bt.audit(repo)] == [
        (bt.TABLE, bt.THE_BOUNDARY_TABLE)
    ]
    assert not (repo / bt.TABLE).exists()

    assert bt.audit(repo, write=True) == []
    assert bt.audit(repo) == []

    (repo / bt.TABLE).write_text("mypy: [commit]\n")

    assert [f.rule for f in bt.audit(repo)] == [bt.THE_BOUNDARY_TABLE]


def test_repo_with_no_address_and_no_table_is_clean(tmp_path: Path) -> None:
    repo = tmp_path / "bare"
    repo.mkdir()

    assert bt.audit(repo) == []


def test_main_exit_codes(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    assert bt.main([str(repo)]) == 1
    assert bt.main(["--write", str(repo)]) == 0
    assert bt.main([str(repo)]) == 0
    assert bt.main([str(dev_playbook(tmp_path / "broken", {"Makefile": ""}))]) == 2


def test_list_rules_prints_every_rule(capsys: pytest.CaptureFixture[str]) -> None:
    assert bt.main(["--list-rules"]) == 0

    assert set(capsys.readouterr().out.split()) == set(bt.RULES)

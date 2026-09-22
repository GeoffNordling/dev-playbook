"""Behavioral tests for verifier-table, the generator that writes and lints it.

Each fixture is a git repo carrying a ``standards/<name>/<topic>.md`` with rule
trailers. The ``--list-rules`` boundary is injected as a plain callable, the
dependency map as a mapping, and a consumer fixture passes a synthetic upstream
root, so nothing subprocesses a real detector.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from dev_playbook import verifier_table as vt

CANONICAL = "standards/build/canonical/.pre-commit-config.yaml"


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


def standard(name: str, rules: list[tuple[str, str]]) -> str:
    """A Standard whose headings are the given (title, kind) rules."""
    body = f"---\ntype: Standard\ntitle: {name}\n---\n\n# {name}\n"
    for title, kind in rules:
        slug = title.lower().replace(" ", "-")
        body += f"\n## {title}\n\nA predicate.\n\n`{name}.{slug}` · {kind}\n"
    return body


def config(hook_ids: list[str], detectors: tuple[str, ...] = ()) -> str:
    """A pre-commit config: dependency hooks by id, local scripts/ detectors."""
    text = "repos:\n  - repo: https://example.invalid/hooks\n    rev: v1\n    hooks:\n"
    for hook_id in hook_ids:
        text += f"      - id: {hook_id}\n"
    if detectors:
        text += "  - repo: local\n    hooks:\n"
    for name in detectors:
        text += f"      - id: {name}\n        entry: scripts/{name}\n"
    return text


def fake_list_rules(mapping: dict[str, list[str]]) -> Callable[[str, Path], list[str]]:
    """A --list-rules stand-in; an absent name models a script that won't answer."""

    def _list(name: str, root: Path) -> list[str]:
        if name not in mapping:
            raise vt.CannotRun(f"scripts/{name} does not answer --list-rules")
        return mapping[name]

    return _list


def dev_playbook(
    tmp_path: Path, extra: dict[str, str] | None = None, *, table: str | None = None
) -> Path:
    """A dev-playbook-mode repo: one Standard with a deterministic and a stochastic rule."""
    files = {
        CANONICAL: "",
        ".pre-commit-config.yaml": config(["ruff-format"]),
        "pyproject.toml": '[dependency-groups]\ndev = ["mypy>=2.0"]\n',
        "standards/build/rules.md": standard(
            "build", [("Alpha", "deterministic"), ("Beta", "stochastic")]
        ),
        **(extra or {}),
    }
    if table is not None:
        files[vt.TABLE] = table
    return make_repo(tmp_path, files)


ROSTER = ("repo-lint",)


@pytest.fixture(autouse=True)
def small_roster(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vt, "DETECTORS", ROSTER)
    monkeypatch.setattr(vt, "UNGATED_AUDITS", frozenset())


# --- the derivation ---------------------------------------------------------


def test_every_declared_rule_gets_a_row(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo, fake_list_rules({"repo-lint": ["build.alpha"]}), dependencies={}
    )

    assert table.rows == {"build.alpha": "scripts/repo-lint", "build.beta": None}
    assert table.findings == []


def test_render_is_a_header_then_sorted_rows() -> None:
    text = vt.render_table({"b.y": None, "a.x": "scripts/z"})

    assert text.startswith("# The verifier table")
    assert text.endswith("a.x: scripts/z\nb.y: null\n")


def test_dependency_rows_take_their_address(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo,
        fake_list_rules({"repo-lint": []}),
        dependencies={"ruff-format": ("build.alpha",)},
    )

    assert table.rows["build.alpha"] == "ruff-format"
    assert table.findings == []


def test_emitted_id_with_no_heading_is_flagged(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo, fake_list_rules({"repo-lint": ["build.gamma"]}), dependencies={}
    )

    assert [(f.file, f.rule) for f in table.findings] == [
        ("scripts/repo-lint", vt.AN_EMITTED_ID_IS_A_RULE_HEADING)
    ]
    assert "build.gamma" in table.findings[0].message


def test_emitted_stochastic_id_is_flagged(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo, fake_list_rules({"repo-lint": ["build.beta"]}), dependencies={}
    )

    assert [f.rule for f in table.findings] == [vt.AN_EMITTED_ID_IS_A_RULE_HEADING]
    assert "stochastic" in table.findings[0].message
    assert table.rows["build.beta"] is None


def test_id_two_checks_emit_is_flagged_on_the_second(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo,
        fake_list_rules({"repo-lint": ["build.alpha"]}),
        dependencies={"ruff-format": ("build.alpha",)},
    )

    assert [(f.file, f.rule) for f in table.findings] == [
        ("scripts/repo-lint", vt.AN_EMITTED_ID_IS_A_RULE_HEADING)
    ]
    assert "ruff-format also emits" in table.findings[0].message
    assert table.rows["build.alpha"] == "ruff-format"


def test_dependency_address_the_repo_lacks_is_flagged(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    table = vt.derive(
        repo,
        fake_list_rules({"repo-lint": []}),
        dependencies={"shfmt": ("build.alpha",)},
    )

    assert [(f.file, f.rule) for f in table.findings] == [
        (vt.TABLE, vt.AN_ADDRESS_EXISTS)
    ]


def test_dependency_named_in_pyproject_or_as_pre_commit_is_an_address(
    tmp_path: Path,
) -> None:
    repo = dev_playbook(
        tmp_path,
        {
            "standards/build/rules.md": standard(
                "build", [("Alpha", "deterministic"), ("Gamma", "deterministic")]
            )
        },
    )

    table = vt.derive(
        repo,
        fake_list_rules({"repo-lint": []}),
        dependencies={
            "mypy": ("build.alpha",),
            "pre-commit validate-manifest": ("build.gamma",),
        },
    )

    assert table.findings == []


def test_roster_member_that_will_not_answer_cannot_run(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    with pytest.raises(vt.CannotRun):
        vt.derive(repo, fake_list_rules({}), dependencies={})


# --- the declared rules -----------------------------------------------------


def test_trailer_disagreeing_with_its_heading_cannot_run(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {
            "standards/build/rules.md": (
                "# Build\n\n## Alpha\n\nText.\n\n`build.alpah` · deterministic\n"
            )
        },
    )

    with pytest.raises(vt.CannotRun, match="should read `build.alpha`"):
        vt.declared_rules(repo)


def test_trailer_with_no_heading_cannot_run(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {"standards/build/rules.md": "# Build\n\n`build.alpha` · deterministic\n"},
    )

    with pytest.raises(vt.CannotRun, match="no heading"):
        vt.declared_rules(repo)


def test_id_declared_twice_cannot_run(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {"standards/build/other.md": standard("build", [("Alpha", "deterministic")])},
    )

    with pytest.raises(vt.CannotRun, match="already declared"):
        vt.declared_rules(repo)


def test_trailer_inside_a_fence_is_not_a_rule(tmp_path: Path) -> None:
    repo = dev_playbook(
        tmp_path,
        {
            "standards/build/rules.md": (
                "# Build\n\n## Alpha\n\n```\n`build.wrong` · deterministic\n```\n\n"
                "`build.alpha` · deterministic\n"
            )
        },
    )

    assert set(vt.declared_rules(repo)) == {"build.alpha"}


# --- the walk ---------------------------------------------------------------


def test_missing_table_is_flagged(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    findings = vt.audit(repo, fake_list_rules({"repo-lint": []}), dependencies={})

    assert [(f.file, f.rule) for f in findings] == [(vt.TABLE, vt.THE_VERIFIER_TABLE)]


def test_stale_table_is_flagged_and_current_table_passes(tmp_path: Path) -> None:
    rows = {"build.alpha": "scripts/repo-lint", "build.beta": None}
    repo = dev_playbook(tmp_path, table=vt.render_table(rows))
    list_rules = fake_list_rules({"repo-lint": ["build.alpha"]})

    assert vt.audit(repo, list_rules, dependencies={}) == []

    (repo / vt.TABLE).write_text(vt.render_table({**rows, "build.alpha": None}))
    findings = vt.audit(repo, list_rules, dependencies={})

    assert [f.rule for f in findings] == [vt.THE_VERIFIER_TABLE]


def test_write_puts_the_derived_table_on_disk(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)
    list_rules = fake_list_rules({"repo-lint": ["build.alpha"]})

    assert vt.audit(repo, list_rules, write=True, dependencies={}) == []
    assert (repo / vt.TABLE).read_text() == vt.render_table(
        {"build.alpha": "scripts/repo-lint", "build.beta": None}
    )
    assert vt.audit(repo, list_rules, dependencies={}) == []


def test_lint_mode_never_writes(tmp_path: Path) -> None:
    repo = dev_playbook(tmp_path)

    vt.audit(repo, fake_list_rules({"repo-lint": []}), dependencies={})

    assert not (repo / vt.TABLE).exists()


def test_repo_with_no_rules_and_no_table_is_clean(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"README.md": "# r\n"})

    assert vt.audit(repo, fake_list_rules({}), upstream_root=repo) == []


def test_main_exit_codes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = dev_playbook(tmp_path)
    monkeypatch.setattr(
        vt, "list_rules_via_subprocess", fake_list_rules({"repo-lint": []})
    )
    monkeypatch.setattr(vt, "DEPENDENCY_RULES", {})

    assert vt.main([str(repo)]) == 1
    assert vt.main(["--write", str(repo)]) == 0
    assert vt.main([str(repo)]) == 0


def test_list_rules_prints_every_rule(capsys: pytest.CaptureFixture[str]) -> None:
    assert vt.main(["--list-rules"]) == 0

    assert set(capsys.readouterr().out.split()) == set(vt.RULES)


# --- consumer mode ----------------------------------------------------------


def consumer(tmp_path: Path, upstream_rows: dict[str, str | None]) -> tuple[Path, Path]:
    """A consumer repo with one local detector hook, and an upstream carrying a table."""
    upstream = make_repo(tmp_path / "up", {vt.TABLE: vt.render_table(upstream_rows)})
    repo = make_repo(
        tmp_path,
        {
            ".pre-commit-config.yaml": config([], ("widget-lint",)),
            "standards/widget/rules.md": standard(
                "widget", [("Alpha", "deterministic"), ("Beta", "deterministic")]
            ),
        },
    )
    return repo, upstream


def test_consumer_asks_its_own_hooks_and_tables_only_its_rules(tmp_path: Path) -> None:
    repo, upstream = consumer(
        tmp_path, {"build.ciyml-byte-identical-to-canonical": "scripts/repo-lint"}
    )

    table = vt.derive(
        repo,
        fake_list_rules({"widget-lint": ["widget.alpha"]}),
        dependencies={"ruff-format": ("build.ciyml-byte-identical-to-canonical",)},
        upstream_root=upstream,
    )

    assert table.rows == {"widget.alpha": "scripts/widget-lint", "widget.beta": None}
    assert table.findings == []


def test_consumer_row_naming_an_upstream_rule_is_flagged(tmp_path: Path) -> None:
    repo, upstream = consumer(tmp_path, {"widget.beta": None})

    table = vt.derive(
        repo, fake_list_rules({"widget-lint": []}), upstream_root=upstream
    )

    assert [(f.file, f.rule) for f in table.findings] == [
        ("standards/widget/rules.md", vt.A_CONSUMER_ADDS_ONLY_ITS_OWN_RULES)
    ]


def test_consumer_without_an_upstream_table_cannot_run(tmp_path: Path) -> None:
    repo, _ = consumer(tmp_path, {})

    with pytest.raises(vt.CannotRun):
        vt.derive(
            repo, fake_list_rules({"widget-lint": []}), upstream_root=tmp_path / "none"
        )


# --- the subprocess boundary ------------------------------------------------


def detector_repo(tmp_path: Path, script: str) -> Path:
    """A dev-playbook-mode repo whose one roster detector is ``scripts/foo``."""
    repo = dev_playbook(tmp_path, {"scripts/foo": script})
    (repo / "scripts" / "foo").chmod(0o755)
    return repo


def test_a_spawned_detector_does_not_inherit_the_hook_ambient_git_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_git_dir: Callable[[str], Path],
) -> None:
    # The generator runs at a git gate and can inherit an absolute GIT_DIR the
    # hook exports; a detector it spawns must not receive it, or the detector's
    # own git calls answer for the hook's repo instead of the audited one. The
    # detector records the git dir it resolves to; with the redirecting
    # variables scrubbed it names the audited root, not the decoy.
    monkeypatch.setattr(vt, "DETECTORS", ("foo",))
    monkeypatch.setattr(vt, "DEPENDENCY_RULES", {})
    repo = detector_repo(
        tmp_path,
        "#!/usr/bin/env bash\ngit rev-parse --absolute-git-dir > git-dir-seen\n",
    )
    decoy = ambient_git_dir("leaked.txt")

    vt.main([str(repo)])

    seen = Path((repo / "git-dir-seen").read_text().strip()).resolve()
    assert seen == (repo / ".git").resolve()
    assert seen != (decoy / ".git").resolve()


def test_a_hung_detector_fails_the_gate_loudly_without_hanging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A detector that hangs on --list-rules must fail the commit gate loudly,
    # not block it forever: the timeout converts to a CannotRun, exit 2.
    monkeypatch.setattr(vt, "DETECTORS", ("foo",))
    repo = detector_repo(tmp_path, "#!/usr/bin/env bash\n")
    real_run = subprocess.run

    def hang(cmd: Any, *args: Any, **kwargs: Any) -> Any:
        # Only the detector's --list-rules call hangs; git ls-files runs for real.
        if "--list-rules" in cmd:
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=10)
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(vt.subprocess, "run", hang)

    assert vt.main([str(repo)]) == 2
    assert "--list-rules" in capsys.readouterr().err

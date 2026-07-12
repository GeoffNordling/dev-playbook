"""Behavioral tests for scripts/workspace-audit.

Fixtures build a throwaway workspace of git repos and point --workspace at
it. Settings tests put a fake ``gh`` executable on PATH that serves canned
JSON from a file, so no test touches the network. The pinned-repo URL and
the hook repo's ``main`` sha come from the real checkout the script lives
in, exactly as in production.
"""

import json
import os
import re
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workspace-audit"
HOOK_REPO = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = (
    HOOK_REPO / "standards" / "build" / "canonical" / ".pre-commit-config.yaml"
)

FAKE_GH = """\
#!/usr/bin/env python3
import json, os, sys

# Only `gh api <path>` is faked. Find the path arg (skip flags), drop any query
# string, and split into segments: repos/<owner>/<name>[/<resource>].
path = next(a for a in sys.argv[2:] if not a.startswith("-")).split("?", 1)[0]
segs = path.split("/")
slug = "/".join(segs[1:3])
resource = segs[3] if len(segs) > 3 else "settings"

data = json.load(open(os.environ["FAKE_GH_DATA"]))
if slug not in data:
    sys.exit(1)
entry = data[slug]

# An entry is either a bare settings dict (legacy) or a wrapper carrying any of
# settings / labels / issues. A bare entry answers the base repo path with its
# settings and every sub-resource with an empty list.
wrapper = isinstance(entry, dict) and any(
    k in entry for k in ("settings", "labels", "issues")
)
if wrapper:
    payload = entry.get(resource, [] if resource in ("labels", "issues") else {})
else:
    payload = entry if resource == "settings" else []
print(json.dumps(payload))
"""


def canonical_label_objects() -> list[dict]:
    """The scheme's labels as the GitHub labels endpoint returns them."""
    import sys as _sys

    _sys.path.insert(0, str(HOOK_REPO / "src"))
    from dev_playbook.label_scheme import canonical_labels

    return [
        {"name": name, "color": color, "description": desc}
        for name, color, desc in canonical_labels()
    ]


GOOD_SETTINGS = {
    "allow_squash_merge": True,
    "allow_merge_commit": False,
    "allow_rebase_merge": False,
    "delete_branch_on_merge": True,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY",
}


def hook_repo_url() -> str:
    text = CANONICAL_CONFIG.read_text()
    match = re.search(r"-\s*repo:\s*(\S+)\n\s*rev:\s*<pinned-sha>", text)
    assert match, "canonical config lost its pinned block"
    return match.group(1)


def main_sha() -> str:
    return subprocess.run(
        ["git", "-C", str(HOOK_REPO), "rev-parse", "main"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def make_workspace_repo(
    workspace: Path, name: str, files: dict[str, str], origin: str | None = None
) -> Path:
    repo = workspace / name
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    if origin:
        subprocess.run(
            ["git", "-C", str(repo), "remote", "add", "origin", origin],
            check=True,
            capture_output=True,
        )
    return repo


def pin_config(rev: str) -> str:
    return f"repos:\n  - repo: {hook_repo_url()}\n    rev: {rev}\n    hooks:\n      - id: repo-audit\n"


def run(
    workspace: Path, *args: str, gh_data: Path | None = None, gh_dir: Path | None = None
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if gh_dir is not None:
        env["PATH"] = f"{gh_dir}:{env['PATH']}"
    if gh_data is not None:
        env["FAKE_GH_DATA"] = str(gh_data)
    return subprocess.run(
        ["python3", str(SCRIPT), "--workspace", str(workspace), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def make_fake_gh(tmp_path: Path, data: dict[str, dict]) -> tuple[Path, Path]:
    gh_dir = tmp_path / "fakebin"
    gh_dir.mkdir()
    gh = gh_dir / "gh"
    gh.write_text(FAKE_GH)
    os.chmod(gh, 0o755)
    gh_data = tmp_path / "gh.json"
    gh_data.write_text(json.dumps(data))
    return gh_dir, gh_data


# --- rule ids ---


def test_list_rules_prints_card_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = set(result.stdout.split())
    assert "tracking.settings" in ids
    assert "tracking.remote" in ids
    assert "build.pin" in ids
    # the tracking and workflow rules this slice adds
    assert "tracking.label-scheme" in ids
    assert "tracking.no-blocked-label" in ids
    assert "tracking.issue-brief-shape" in ids
    assert "tracking.epic-shape" in ids
    assert "workflow.tuple-valid" in ids
    assert all(
        rule.split(".")[0] in {"tracking", "build", "workflow"} for rule in ids
    ), ids


# --- pins ---


def test_missing_workspace_exits_two(tmp_path: Path) -> None:
    result = run(tmp_path / "nowhere", "--pins-only")
    assert result.returncode == 2
    assert "workspace root not found" in result.stderr


def test_pin_current_stale_and_absent(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {".pre-commit-config.yaml": pin_config(main_sha())}
    )
    make_workspace_repo(
        ws, "beta", {".pre-commit-config.yaml": pin_config("0000000000000000")}
    )
    make_workspace_repo(ws, "gamma", {"README.md": "# G\n"})
    result = run(ws, "--pins-only")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "alpha: pin current" in result.stderr
    assert re.search(
        r"beta: build.pin 0{16} \(hook repo main is \w{12}\)", result.stdout
    )
    assert "gamma: no .pre-commit-config.yaml" in result.stderr
    assert "1 stale pin(s)" in result.stderr


def test_stale_pin_is_not_a_failure(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "beta", {".pre-commit-config.yaml": pin_config("0000000000000000")}
    )
    assert run(ws, "--pins-only").returncode == 0


def test_short_sha_pin_matches_main(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {".pre-commit-config.yaml": pin_config(main_sha()[:10])}
    )
    result = run(ws, "--pins-only")
    assert "alpha: pin current" in result.stderr


def test_config_without_hook_repo_pin(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws,
        "delta",
        {
            ".pre-commit-config.yaml": (
                "repos:\n  - repo: https://github.com/example/other\n"
                "    rev: v1.0.0\n    hooks:\n      - id: x\n"
            )
        },
    )
    result = run(ws, "--pins-only")
    assert "delta: no dev-playbook pin" in result.stderr


def test_hook_repo_itself_has_no_pin_line(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "hooks-repo", {".pre-commit-hooks.yaml": "- id: x\n"})
    result = run(ws, "--pins-only")
    assert "hooks-repo" not in result.stdout


# --- settings ---


def test_conforming_settings_pass(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_drifted_setting_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="https://github.com/me/alpha.git"
    )
    drifted = dict(GOOD_SETTINGS, allow_merge_commit=True)
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": drifted})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.settings allow_merge_commit is True (want False)"
        in result.stdout
    )


def test_unreachable_repo_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/unknown.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.settings unreachable via gh api (me/unknown)" in result.stdout
    )


def test_repo_without_origin_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.remote no GitHub origin; settings unchecked" in result.stdout
    )


# --- label scheme (full mode; settings clean so only label findings surface) ---


def full_mode_repo(
    tmp_path: Path,
    *,
    labels: list[dict],
    issues: list[dict] | None = None,
) -> tuple[Path, Path, Path]:
    """A one-repo workspace with a GitHub origin and a fake gh serving good
    settings plus the given labels/issues, so a full-mode run surfaces only the
    label/issue findings under test."""
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "labels": labels,
                "issues": issues or [],
            }
        },
    )
    return ws, gh_dir, gh_data


def test_conformant_labels_raise_no_label_finding(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=canonical_label_objects())
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "tracking.label-scheme" not in result.stdout
    assert "tracking.no-blocked-label" not in result.stdout


def test_missing_canonical_label_is_a_finding(tmp_path: Path) -> None:
    labels = [obj for obj in canonical_label_objects() if obj["name"] != "mode:spike"]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.label-scheme missing label mode:spike" in result.stdout
    assert result.returncode == 1


def test_drifted_label_color_is_a_finding(tmp_path: Path) -> None:
    labels = canonical_label_objects()
    labels[0] = dict(labels[0], color="ff0000")
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.label-scheme" in result.stdout
    assert labels[0]["name"] in result.stdout


def test_drifted_label_description_is_a_finding(tmp_path: Path) -> None:
    labels = canonical_label_objects()
    labels[0] = dict(labels[0], description="wrong")
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.label-scheme" in result.stdout
    assert labels[0]["name"] in result.stdout


def test_unexpected_label_is_a_finding(tmp_path: Path) -> None:
    labels = [
        *canonical_label_objects(),
        {"name": "wip", "color": "cccccc", "description": ""},
    ]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.label-scheme unexpected label wip" in result.stdout


# --- blocked labels (own rule, overlapping the closed world by design) ---


def test_blocked_label_is_its_own_finding(tmp_path: Path) -> None:
    labels = [
        *canonical_label_objects(),
        {"name": "status:Blocked", "color": "cccccc", "description": ""},
    ]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.no-blocked-label" in result.stdout
    assert "status:Blocked" in result.stdout
    # deliberately also flagged by the closed-world scheme rule
    assert (
        "alpha: tracking.label-scheme unexpected label status:Blocked" in result.stdout
    )


# --- issue rules: tuple validity, brief shape, epic shape (full mode) ---

BUILD_BODY = (
    "**Summary:** s\n\n**Current behavior:** c\n\n**Desired behavior:** d\n\n"
    "**Key interfaces:** none\n\n**Acceptance criteria:** a\n\n**Out of scope:** o\n"
)
SPIKE_BODY = (
    "**Summary:** s\n\n**Question:** q\n\n**Timebox:** t\n\n**Deliverable:** d\n"
)
VALID_DIRECT = ["category:enhancement", "mode:direct", "tests:no", "phase:build"]


def issue(
    number: int,
    labels: list[str],
    *,
    body: str = "",
    sub_issues_total: int = 0,
    pull_request: bool = False,
) -> dict:
    obj = {
        "number": number,
        "title": f"issue {number}",
        "body": body,
        "state": "open",
        "labels": [{"name": name} for name in labels],
        "sub_issues_summary": {"total": sub_issues_total},
    }
    if pull_request:
        obj["pull_request"] = {"url": "https://example/pr"}
    return obj


def run_with_issue(tmp_path: Path, one: dict) -> subprocess.CompletedProcess:
    ws, gh_dir, gh_data = full_mode_repo(
        tmp_path, labels=canonical_label_objects(), issues=[one]
    )
    return run(ws, gh_dir=gh_dir, gh_data=gh_data)


def test_valid_leaf_tuple_and_brief_pass(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(1, VALID_DIRECT, body=BUILD_BODY))
    assert "workflow.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout
    assert "tracking.epic-shape" not in result.stdout


def test_untriaged_issue_is_out_of_scope(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(2, ["phase:intake"], body=""))
    assert "workflow.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout


def test_leaf_missing_mode_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:enhancement", "tests:no", "phase:build"]
    result = run_with_issue(tmp_path, issue(7, labels, body=BUILD_BODY))
    assert "alpha: workflow.tuple-valid" in result.stdout
    assert "#7" in result.stdout
    assert "mode" in result.stdout


def test_leaf_invalid_phase_value_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:enhancement", "mode:direct", "tests:no", "phase:frobnicate"]
    result = run_with_issue(tmp_path, issue(8, labels, body=BUILD_BODY))
    assert "alpha: workflow.tuple-valid" in result.stdout
    assert "phase" in result.stdout


def test_sdd_leaf_requires_tests_yes(tmp_path: Path) -> None:
    labels = ["category:enhancement", "mode:sdd", "tests:no", "phase:sdd-tdd"]
    result = run_with_issue(tmp_path, issue(9, labels, body=BUILD_BODY))
    assert "alpha: workflow.tuple-valid" in result.stdout
    assert "tests:yes" in result.stdout


def test_spike_leaf_requires_tests_no(tmp_path: Path) -> None:
    labels = ["category:enhancement", "mode:spike", "tests:yes", "phase:spike"]
    result = run_with_issue(tmp_path, issue(10, labels, body=SPIKE_BODY))
    assert "alpha: workflow.tuple-valid" in result.stdout
    assert "tests:no" in result.stdout


def test_epic_with_phase_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:enhancement", "phase:tdd"]
    result = run_with_issue(tmp_path, issue(3, labels, sub_issues_total=4))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#3" in result.stdout
    assert "workflow.tuple-valid" not in result.stdout


def test_wellformed_epic_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(4, ["category:enhancement"], sub_issues_total=4)
    )
    assert "tracking.epic-shape" not in result.stdout


def test_build_leaf_missing_heading_is_a_finding(tmp_path: Path) -> None:
    body = BUILD_BODY.replace("**Out of scope:** o\n", "")
    result = run_with_issue(tmp_path, issue(5, VALID_DIRECT, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Out of scope" in result.stdout


def test_spike_leaf_missing_heading_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:enhancement", "mode:spike", "tests:no", "phase:spike"]
    body = SPIKE_BODY.replace("**Timebox:** t\n\n", "")
    result = run_with_issue(tmp_path, issue(6, labels, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Timebox" in result.stdout


def test_pull_requests_are_ignored(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(11, ["phase:tdd"], body="", pull_request=True)
    )
    assert "workflow.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout

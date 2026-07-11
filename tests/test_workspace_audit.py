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
slug = sys.argv[2].removeprefix("repos/")
data = json.load(open(os.environ["FAKE_GH_DATA"]))
if slug not in data:
    sys.exit(1)
print(json.dumps(data[slug]))
"""

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
    assert "alpha  pin  current" in result.stdout
    assert re.search(r"beta  pin  0{16} \(hook repo main is \w{12}\)", result.stdout)
    assert "gamma  pin  no .pre-commit-config.yaml" in result.stdout
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
    assert "alpha  pin  current" in result.stdout


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
    assert "delta  pin  no dev-playbook pin" in result.stdout


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
    assert "alpha  settings  allow_merge_commit is True (want False)" in result.stdout


def test_unreachable_repo_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/unknown.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "alpha  settings  unreachable via gh api (me/unknown)" in result.stdout


def test_repo_without_origin_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "alpha  remote  no GitHub origin; settings unchecked" in result.stdout

"""Behavioral tests for scripts/workspace-lint.

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
from collections.abc import Callable
from pathlib import Path

from conftest import init_repo

from dev_playbook import gitrepo, workspace_lint

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "workspace-lint"
HOOK_REPO = Path(__file__).resolve().parents[2]
CANONICAL_CONFIG = (
    HOOK_REPO / "standards" / "build" / "canonical" / ".pre-commit-config.yaml"
)

FAKE_GH = """\
#!/usr/bin/env python3
import json, os, sys

# The audit's auth preflight. FAKE_GH_AUTH set to "0" (the default) stands for a
# usable credential; any other value is the exit code an unauthenticated `gh`
# returns, which the audit must treat as a precondition failure.
if sys.argv[1:3] == ["auth", "status"]:
    code = int(os.environ.get("FAKE_GH_AUTH", "0"))
    if code:
        sys.stderr.write("The token in default is invalid.\\n")
    sys.exit(code)

# Two `gh api` forms are faked, matching the two the audit issues. Settings come
# over `gh api graphql -f query=... -f owner=... -f name=...`, so the slug is
# rebuilt from the variables; every other resource comes over REST, whose path
# splits into repos/<owner>/<name>[/<resource>]. Flags are skipped either way.
args = [a for a in sys.argv[2:] if not a.startswith("-")]
graphql = args[0] == "graphql"
if graphql:
    variables = dict(a.split("=", 1) for a in args[1:] if "=" in a)
    slug = variables["owner"] + "/" + variables["name"]
    # Two GraphQL queries now share the -f owner/-f name shape, so the query
    # body is what tells them apart.
    protection = "defaultBranchRef" in variables["query"]
    resource = "protection" if protection else "settings"
else:
    segs = args[0].split("?", 1)[0].split("/")
    slug = "/".join(segs[1:3])
    resource = segs[3] if len(segs) > 3 else "settings"

# What a resource answers when a test says nothing about it. Protection defaults
# to fully protected so that a test about merge settings or labels does not have
# to restate the branch rules to stay clean.
DEFAULTS = {
    "labels": [],
    "issues": [],
    "protection": {
        "defaultBranchRef": {
            "name": "main",
            "rules": {"nodes": [{"type": "NON_FAST_FORWARD"}, {"type": "DELETION"}]},
        }
    },
}

data = json.load(open(os.environ["FAKE_GH_DATA"]))
if slug not in data:
    sys.exit(1)
entry = data[slug]

# An entry is either a bare settings dict (legacy) or a wrapper carrying any of
# settings / protection / labels / issues. A bare entry answers the base repo
# path with its settings and every other resource with that resource's default.
wrapper = isinstance(entry, dict) and any(
    k in entry for k in ("settings", "protection", "labels", "issues")
)
if wrapper:
    payload = entry.get(resource, DEFAULTS.get(resource, {}))
else:
    payload = entry if resource == "settings" else DEFAULTS.get(resource, {})
# A resource set to the sentinel "__unreachable__" simulates a non-zero `gh api`
# exit (rate limit, permissions, transient 5xx) for that one resource.
if payload == "__unreachable__":
    sys.exit(1)
# "__badjson__" simulates a zero-exit response whose body is not JSON (204 No
# Content, a degraded/HTML error body) — the parse, not the exit, is what fails.
if payload == "__badjson__":
    sys.stdout.write("{not valid json")
    sys.exit(0)
# GraphQL wraps its answer. A settings payload of null models the null
# repository GitHub returns when the token cannot see the repo at all; one
# missing the merge fields models a response that answers 200 without them.
if graphql:
    payload = {"data": {"repository": payload}}
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


# Settings as GraphQL serves them — the camelCase names the audit queries, not
# the REST names its findings print.
GOOD_SETTINGS = {
    "squashMergeAllowed": True,
    "mergeCommitAllowed": False,
    "rebaseMergeAllowed": False,
    "deleteBranchOnMerge": True,
    "squashMergeCommitTitle": "PR_TITLE",
    "squashMergeCommitMessage": "PR_BODY",
}


def protection(*types: str, branch: str = "main") -> dict:
    """A default-branch rules payload as GraphQL serves it.

    No arguments is the unprotected repo — a default branch with an empty rule
    list, which is what a repo carrying no ruleset answers.
    """
    return {
        "defaultBranchRef": {
            "name": branch,
            "rules": {"nodes": [{"type": t} for t in types]},
        }
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
    return f"repos:\n  - repo: {hook_repo_url()}\n    rev: {rev}\n    hooks:\n      - id: repo-lint\n"


def run(
    workspace: Path,
    *args: str,
    gh_data: Path | None = None,
    gh_dir: Path | None = None,
    repos: str | None = None,
    gh_auth: str | None = None,
) -> subprocess.CompletedProcess:
    """Run the audit over ``workspace``, governing every repo the test built.

    The production roster names real repos, so tests pass their own via
    ``--repos``. Defaulting it to the synthetic workspace's contents keeps each
    test's subject exactly the repos it created; pass ``repos`` explicitly to
    govern something else — including a name that is deliberately absent.
    """
    env = dict(os.environ)
    if gh_dir is not None:
        env["PATH"] = f"{gh_dir}:{env['PATH']}"
    if gh_data is not None:
        env["FAKE_GH_DATA"] = str(gh_data)
    if gh_auth is not None:
        env["FAKE_GH_AUTH"] = gh_auth
    if repos is None:
        found = (
            sorted(e.name for e in workspace.iterdir() if (e / ".git").exists())
            if workspace.is_dir()
            else []
        )
        repos = ",".join(found)
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--workspace",
            str(workspace),
            "--repos",
            repos,
            *args,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def make_fake_gh(tmp_path: Path, data: dict[str, object]) -> tuple[Path, Path]:
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
    # the tracking and software-factory rules this slice adds
    assert "tracking.label-scheme" in ids
    assert "tracking.no-blocked-label" in ids
    assert "tracking.issue-brief-shape" in ids
    assert "tracking.epic-shape" in ids
    assert "software-factory.tuple-valid" in ids
    assert all(
        rule.split(".")[0] in {"tracking", "build", "software-factory"} for rule in ids
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
    assert result.returncode == 1, result.stdout + result.stderr
    assert "alpha: pin current" in result.stderr
    assert re.search(
        r"beta: build.pin 0{16} \(hook repo main is \w{12}\)", result.stdout
    )
    assert "gamma: build.pin no .pre-commit-config.yaml" in result.stdout
    # The stale pin is advisory and the absent one is a finding; the summary
    # counts them apart even though both carry build.pin.
    assert "1 finding(s), 1 stale pin(s)" in result.stderr


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
    assert result.returncode == 1
    assert "delta: build.pin no dev-playbook pin" in result.stdout


def test_hook_repo_itself_has_no_pin_line() -> None:
    # The real checkout, since the exemption is identity: dev-playbook dogfoods
    # from its working tree and has nothing to pin.
    result = run(HOOK_REPO.parent, "--pins-only", repos=HOOK_REPO.name)
    assert result.returncode == 0, result.stdout + result.stderr
    assert HOOK_REPO.name not in result.stdout


def test_consumer_publishing_its_own_hooks_is_still_pin_checked(
    tmp_path: Path,
) -> None:
    # A consumer may publish hooks of its own; that does not make it the hook
    # repo, and its dev-playbook pin must still be audited. Reading the
    # exemption off the manifest instead of off identity dropped exactly this
    # repo's pin from the sweep.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws,
        "publisher",
        {
            ".pre-commit-hooks.yaml": "- id: x\n",
            ".pre-commit-config.yaml": pin_config("0000000000000000"),
        },
    )
    result = run(ws, "--pins-only")
    assert "publisher: build.pin 0000000000000000" in result.stdout


# --- the governed roster ---


def test_ungoverned_repo_draws_no_output(tmp_path: Path) -> None:
    # Inclusion is the decision: a repo nobody listed is not a finding, not an
    # advisory, not a line. It is simply not this audit's business.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {".pre-commit-config.yaml": pin_config(main_sha())}
    )
    make_workspace_repo(ws, "stranger", {"README.md": "# not ours\n"})
    result = run(ws, "--pins-only", repos="alpha")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "stranger" not in result.stdout + result.stderr
    assert "1 repos" in result.stderr


def test_governed_repo_that_is_absent_stops_the_run(tmp_path: Path) -> None:
    # The other direction does close: the roster claiming a repo that is not
    # there is a false claim, and a shorter audit must not pass for a clean one.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {".pre-commit-config.yaml": pin_config(main_sha())}
    )
    result = run(ws, "--pins-only", repos="alpha,ghost")
    assert result.returncode == 2
    assert "governed repo(s) not found" in result.stderr
    assert "ghost" in result.stderr


def test_governed_directory_without_git_is_not_a_repo(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    (ws / "plain").mkdir(parents=True)
    result = run(ws, "--pins-only", repos="plain")
    assert result.returncode == 2
    assert "governed repo(s) not found" in result.stderr


def test_roster_order_is_the_audit_order(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    for name in ("alpha", "beta"):
        make_workspace_repo(
            ws, name, {".pre-commit-config.yaml": pin_config(main_sha())}
        )
    result = run(ws, "--pins-only", repos="beta,alpha")
    assert result.stderr.index("beta: pin current") < result.stderr.index(
        "alpha: pin current"
    )


def test_default_roster_is_the_governed_constant() -> None:
    # The roster is the --repos default, so the constant is what a bare run
    # audits; nothing else in the module may narrow it.
    assert workspace_lint.GOVERNED
    assert "dev-playbook" in workspace_lint.GOVERNED


# --- auth preflight ---


def test_unauthenticated_gh_stops_the_run(tmp_path: Path) -> None:
    # The whole point: unauthenticated, the settings read fails on every repo
    # while a public repo's other reads still answer, so a per-repo degradation
    # would mix fiction into real findings. Exit 2 says "could not run" instead.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data, gh_auth="1")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "no usable credential" in result.stderr
    # No finding may be printed: a half-answered audit is what this prevents.
    assert result.stdout == ""


def test_unauthenticated_gh_reports_ghs_own_reason(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data, gh_auth="1")
    assert "The token in default is invalid." in result.stderr


def test_pins_only_needs_no_auth(tmp_path: Path) -> None:
    # --pins-only reads nothing over the network, so requiring a credential
    # would refuse a run that could answer correctly.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {".pre-commit-config.yaml": pin_config(main_sha())}
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--pins-only", gh_dir=gh_dir, gh_data=gh_data, gh_auth="1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "alpha: pin current" in result.stderr


def test_authenticated_gh_runs_normally(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data, gh_auth="0")
    assert result.returncode == 0, result.stdout + result.stderr


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
    drifted = dict(GOOD_SETTINGS, mergeCommitAllowed=True)
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": drifted})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    # Queried as mergeCommitAllowed, reported under the REST name.
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


def test_response_without_merge_fields_is_unreachable_not_six_drifts(
    tmp_path: Path,
) -> None:
    # The failure this audit hit in production: a 200 whose repository object
    # carries none of the merge fields (REST answers this way for a fine-grained
    # token, whatever its permissions). Absent is not "set wrong" — the repo is
    # unreadable, and reporting six confident drifts per repo is a wrong answer.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": {"settings": {}}})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        "alpha: tracking.settings unreachable via gh api (me/alpha)"
    ]


def test_partial_response_is_unreachable_not_partial_drift(tmp_path: Path) -> None:
    # A repository object carrying only some merge fields is a degraded read, not
    # a repo whose remaining settings are all None.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    partial = {"settings": {"squashMergeAllowed": True, "mergeCommitAllowed": False}}
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": partial})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        "alpha: tracking.settings unreachable via gh api (me/alpha)"
    ]


def test_null_repository_is_unreachable(tmp_path: Path) -> None:
    # GraphQL answers 200 with a null repository when the token cannot see it.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": {"settings": None}})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "alpha: tracking.settings unreachable via gh api (me/alpha)" in result.stdout


def test_repo_without_origin_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.remote no GitHub origin; settings unchecked" in result.stdout
    )


# --- branch protection ---


def test_protected_default_branch_passes(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("NON_FAST_FORWARD", "DELETION"),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_unprotected_default_branch_is_two_findings(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path, {"me/alpha": {"settings": GOOD_SETTINGS, "protection": protection()}}
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.branch-protection main is not protected against force-push"
        in result.stdout
    )
    assert (
        "alpha: tracking.branch-protection main is not protected against deletion"
        in result.stdout
    )


def test_each_missing_rule_is_reported_alone(tmp_path: Path) -> None:
    # Half-protected is its own state: the rule that is present must not be
    # reported, or a repo cannot tell which half it still owes.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("DELETION"),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "not protected against force-push" in result.stdout
    assert "not protected against deletion" not in result.stdout


def test_unrelated_rules_do_not_satisfy_the_requirement(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("PULL_REQUEST", "REQUIRED_SIGNATURES"),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "not protected against force-push" in result.stdout
    assert "not protected against deletion" in result.stdout


def test_extra_rules_alongside_the_required_two_are_fine(tmp_path: Path) -> None:
    # The requirement is a floor, not an exact set — a repo may protect more.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection(
                    "DELETION", "NON_FAST_FORWARD", "PULL_REQUEST"
                ),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr


def test_finding_names_the_actual_default_branch(tmp_path: Path) -> None:
    # The branch name comes from the API, so a repo whose default is not main
    # is told about the branch it actually has.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection(branch="trunk"),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "trunk is not protected against force-push" in result.stdout


def test_unreadable_rules_are_surfaced_not_read_as_unprotected(tmp_path: Path) -> None:
    # A failed read must never masquerade as a clean answer or as drift: the
    # audit cannot tell whether the branch is protected, and says so.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {"me/alpha": {"settings": GOOD_SETTINGS, "protection": "__unreachable__"}},
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.branch-protection rules unreachable via gh api (me/alpha)"
        in result.stdout
    )
    assert "not protected against" not in result.stdout


def test_repo_without_origin_draws_one_finding_not_two(tmp_path: Path) -> None:
    # tracking.remote already says the origin is missing; protection stays quiet
    # rather than reporting the same absent repo a second time.
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "tracking.branch-protection" not in result.stdout
    assert len(result.stdout.strip().splitlines()) == 1


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
    # A current pin included deliberately: a governed repo carrying none is
    # itself a finding, which would leak into every label/issue assertion here.
    make_workspace_repo(
        ws,
        "alpha",
        {"README.md": "# A\n", ".pre-commit-config.yaml": pin_config(main_sha())},
        origin="git@github.com:me/alpha.git",
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


def test_label_containing_blocked_substring_is_not_a_blocked_finding(
    tmp_path: Path,
) -> None:
    # The rule names a blocked *state* — the value token equal to "blocked".
    # Names that merely contain the substring (a negation, a compound) are not
    # blocked states and must not draw the no-blocked-label rule.
    labels = [
        *canonical_label_objects(),
        {"name": "status:unblocked", "color": "cccccc", "description": ""},
        {"name": "type:blocked-by-vendor", "color": "cccccc", "description": ""},
    ]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "tracking.no-blocked-label" not in result.stdout


# --- fetch reachability (a failed labels/issues read must surface loudly) ---


def test_labels_fetch_failure_is_surfaced(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {"me/alpha": {"settings": GOOD_SETTINGS, "labels": "__unreachable__"}},
    )
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "alpha" in result.stdout
    assert "unreachable" in result.stdout


def test_issues_fetch_failure_is_surfaced(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "labels": canonical_label_objects(),
                "issues": "__unreachable__",
            }
        },
    )
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "alpha" in result.stdout
    assert "unreachable" in result.stdout


def test_bad_json_response_reports_repo_unreachable_and_run_survives(
    tmp_path: Path,
) -> None:
    # A zero-exit response with a non-JSON body for one repo must not abort the
    # whole run: that repo is reported unreachable and every later repo is still
    # audited (alpha sorts first, so beta's finding proves the loop continued).
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    make_workspace_repo(
        ws, "beta", {"README.md": "# B\n"}, origin="git@github.com:me/beta.git"
    )
    drifted = dict(GOOD_SETTINGS, mergeCommitAllowed=True)
    gh_dir, gh_data = make_fake_gh(
        tmp_path, {"me/alpha": "__badjson__", "me/beta": drifted}
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "Traceback" not in result.stderr
    assert "alpha: tracking.settings unreachable via gh api (me/alpha)" in result.stdout
    assert "beta: tracking.settings allow_merge_commit is True (want False)" in (
        result.stdout
    )
    assert result.returncode == 1


def test_wrong_shape_response_is_surfaced_not_crash(tmp_path: Path) -> None:
    # A valid-JSON but wrong-typed response (a dict where the labels list is
    # expected) must degrade to an unreachable finding, not an AssertionError
    # traceback that blinds the audit to the rest of the repo.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {"me/alpha": {"settings": GOOD_SETTINGS, "labels": {"wrong": "shape"}}},
    )
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "Traceback" not in result.stderr
    assert result.returncode == 1
    assert "alpha" in result.stdout
    assert "unreachable" in result.stdout


# --- issue rules: tuple validity, brief shape, epic shape (full mode) ---

BUILD_BODY = (
    "**Summary:** s\n\n**User intent:** i\n\n"
    "**Current behavior:** c\n\n**Desired behavior:** d\n\n"
    "**Key interfaces:** none\n\n**Acceptance criteria:** a\n\n**Out of scope:** o\n"
)
SPIKE_BODY = "**Summary:** s\n\n**Question:** q\n\n**Deliverable:** d\n"
VALID_DIRECT = ["category:extension", "mode:direct", "tests:no", "phase:build"]


def issue(
    number: int,
    labels: list[str],
    *,
    body: str = "",
    sub_issues_total: int = 0,
    pull_request: bool = False,
) -> dict:
    """One issue object shaped as the GitHub issues endpoint returns it."""
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
    """Run a full-mode audit over a one-repo workspace carrying the one issue."""
    ws, gh_dir, gh_data = full_mode_repo(
        tmp_path, labels=canonical_label_objects(), issues=[one]
    )
    return run(ws, gh_dir=gh_dir, gh_data=gh_data)


def test_valid_leaf_tuple_and_brief_pass(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(1, VALID_DIRECT, body=BUILD_BODY))
    assert "software-factory.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout
    assert "tracking.epic-shape" not in result.stdout


def test_untriaged_issue_is_out_of_scope(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(2, ["phase:intake"], body=""))
    assert "software-factory.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout


def test_leaf_missing_mode_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "tests:no", "phase:build"]
    result = run_with_issue(tmp_path, issue(7, labels, body=BUILD_BODY))
    assert "alpha: software-factory.tuple-valid" in result.stdout
    assert "#7" in result.stdout
    assert "mode" in result.stdout


def test_leaf_invalid_phase_value_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:direct", "tests:no", "phase:frobnicate"]
    result = run_with_issue(tmp_path, issue(8, labels, body=BUILD_BODY))
    assert "alpha: software-factory.tuple-valid" in result.stdout
    assert "phase" in result.stdout


def test_leaf_invalid_mode_value_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:frobnicate", "tests:yes", "phase:build"]
    result = run_with_issue(tmp_path, issue(9, labels, body=BUILD_BODY))
    assert "alpha: software-factory.tuple-valid" in result.stdout
    assert "mode:frobnicate is not a scheme value" in result.stdout


def test_spike_leaf_requires_tests_no(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:spike", "tests:yes", "phase:spike"]
    result = run_with_issue(tmp_path, issue(10, labels, body=SPIKE_BODY))
    assert "alpha: software-factory.tuple-valid" in result.stdout
    assert "tests:no" in result.stdout


def test_epic_with_phase_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "phase:build"]
    result = run_with_issue(tmp_path, issue(3, labels, sub_issues_total=4))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#3" in result.stdout
    assert "software-factory.tuple-valid" not in result.stdout


def test_wellformed_epic_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(4, ["category:extension"], sub_issues_total=4)
    )
    assert "tracking.epic-shape" not in result.stdout


def test_epic_with_mode_label_but_no_phase_is_a_finding(tmp_path: Path) -> None:
    # An epic carrying a mode/tests label but no phase label is still malformed:
    # the category-only invariant holds regardless of triage state.
    labels = ["category:extension", "mode:direct"]
    result = run_with_issue(tmp_path, issue(12, labels, sub_issues_total=3))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#12" in result.stdout
    assert "software-factory.tuple-valid" not in result.stdout


def test_epic_without_category_label_is_a_finding(tmp_path: Path) -> None:
    # "An epic carries a category label only" is a positive invariant too: an
    # epic with no category label at all is malformed.
    result = run_with_issue(tmp_path, issue(13, [], sub_issues_total=2))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#13" in result.stdout


def test_epic_with_two_category_labels_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "category:maintenance"]
    result = run_with_issue(tmp_path, issue(14, labels, sub_issues_total=2))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#14" in result.stdout


def test_epic_with_invalid_category_value_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(15, ["category:frobnicate"], sub_issues_total=2)
    )
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#15" in result.stdout


# --- wayfinder species: the map and the decision ticket ---

MAP_BODY = (
    "## Destination\n\nd\n\n## Notes\n\nn\n\n## Decisions so far\n\n- x\n\n"
    "## Not yet specified\n\nf\n\n## Out of scope\n\no\n"
)
TICKET_BODY = "## Question\n\nq\n"


def test_wellformed_map_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(16, ["wayfinder:map"], body=MAP_BODY, sub_issues_total=3)
    )
    assert "tracking.wayfinder-shape" not in result.stdout
    assert "tracking.epic-shape" not in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_map_is_told_by_its_label_not_by_having_children(tmp_path: Path) -> None:
    # A freshly charted map with no tickets yet is still a map, not a leaf.
    result = run_with_issue(
        tmp_path, issue(17, ["wayfinder:map"], body=MAP_BODY, sub_issues_total=0)
    )
    assert "tracking.wayfinder-shape" not in result.stdout
    assert "software-factory.tuple-valid" not in result.stdout


def test_map_carrying_a_factory_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:map", "category:extension", "phase:build"]
    result = run_with_issue(
        tmp_path, issue(18, labels, body=MAP_BODY, sub_issues_total=2)
    )
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "#18" in result.stdout
    assert "category:extension" in result.stdout
    assert "phase:build" in result.stdout


def test_map_missing_a_body_section_is_a_finding(tmp_path: Path) -> None:
    body = MAP_BODY.replace("## Not yet specified\n\nf\n\n", "")
    result = run_with_issue(
        tmp_path, issue(19, ["wayfinder:map"], body=body, sub_issues_total=2)
    )
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "Not yet specified" in result.stdout


def test_map_also_carrying_a_ticket_type_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:map", "wayfinder:research"]
    result = run_with_issue(
        tmp_path, issue(21, labels, body=MAP_BODY, sub_issues_total=2)
    )
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "a map is not a ticket" in result.stdout


def test_wellformed_ticket_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(22, ["wayfinder:research"], body=TICKET_BODY)
    )
    assert "tracking.wayfinder-shape" not in result.stdout
    assert "software-factory.tuple-valid" not in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_ticket_carrying_a_factory_label_is_a_finding(tmp_path: Path) -> None:
    # A ticket carries no phase label, so it used to fall past the post-intake
    # gate entirely; it is now checked against its own contract.
    labels = ["wayfinder:grilling", "mode:direct", "tests:no"]
    result = run_with_issue(tmp_path, issue(23, labels, body=TICKET_BODY))
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "#23" in result.stdout
    assert "a decision ticket carries no factory label" in result.stdout


def test_ticket_missing_its_question_section_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(24, ["wayfinder:task"], body=""))
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "Question" in result.stdout


def test_ticket_with_two_wayfinder_labels_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:research", "wayfinder:grilling"]
    result = run_with_issue(tmp_path, issue(25, labels, body=TICKET_BODY))
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "multiple wayfinder labels" in result.stdout


def test_ticket_with_an_out_of_scheme_type_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(26, ["wayfinder:frobnicate"], body=TICKET_BODY)
    )
    assert "alpha: tracking.wayfinder-shape" in result.stdout
    assert "is not a scheme value" in result.stdout


def test_childed_issue_without_a_wayfinder_label_still_checks_as_an_epic(
    tmp_path: Path,
) -> None:
    # The species dispatch keys on the wayfinder labels; an ordinary issue with
    # children is still a build epic and still carries the epic's shape.
    result = run_with_issue(tmp_path, issue(27, [], sub_issues_total=2))
    assert "alpha: tracking.epic-shape" in result.stdout
    assert "#27" in result.stdout


def test_null_sub_issues_summary_does_not_crash(tmp_path: Path) -> None:
    # GitHub can return sub_issues_summary as JSON null (key present, value null);
    # a valid leaf so shaped must be classified as a leaf, not crash the audit.
    one = {
        "number": 20,
        "title": "issue 20",
        "body": BUILD_BODY,
        "state": "open",
        "labels": [{"name": name} for name in VALID_DIRECT],
        "sub_issues_summary": None,
    }
    result = run_with_issue(tmp_path, one)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Traceback" not in result.stderr


def test_issue_missing_labels_key_is_surfaced_not_silently_skipped(
    tmp_path: Path,
) -> None:
    # GitHub's issues endpoint always returns a labels array; an issue with no
    # labels key at all is a malformed response. It must surface loudly, not be
    # papered over with an empty-list default that silently skips the issue.
    one = {
        "number": 30,
        "title": "issue 30",
        "body": "",
        "state": "open",
        "sub_issues_summary": {"total": 0},
    }
    result = run_with_issue(tmp_path, one)
    assert "Traceback" in result.stderr
    assert "KeyError" in result.stderr


def test_build_leaf_missing_heading_is_a_finding(tmp_path: Path) -> None:
    body = BUILD_BODY.replace("**Out of scope:** o\n", "")
    result = run_with_issue(tmp_path, issue(5, VALID_DIRECT, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Out of scope" in result.stdout


def test_build_leaf_missing_user_intent_is_a_finding(tmp_path: Path) -> None:
    # User intent is a required build-leaf heading, not an optional one: a brief
    # that never says why the work exists leaves the builder with no way to
    # choose among permitted fixes.
    body = BUILD_BODY.replace("**User intent:** i\n\n", "")
    result = run_with_issue(tmp_path, issue(32, VALID_DIRECT, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "User intent" in result.stdout


def test_spike_leaf_missing_heading_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:spike", "tests:no", "phase:spike"]
    body = SPIKE_BODY.replace("**Deliverable:** d\n", "")
    result = run_with_issue(tmp_path, issue(6, labels, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Deliverable" in result.stdout


def test_heading_with_colon_outside_bold_is_accepted(tmp_path: Path) -> None:
    # `**Summary**:` (colon after the close markers) reads as a present heading
    # to a reader; it must not draw a false brief-shape finding.
    body = (
        "**Summary**: s\n\n**User intent**: i\n\n"
        "**Current behavior**: c\n\n**Desired behavior**: d\n\n"
        "**Key interfaces**: none\n\n**Acceptance criteria**: a\n\n**Out of scope**: o\n"
    )
    result = run_with_issue(tmp_path, issue(31, VALID_DIRECT, body=body))
    assert "tracking.issue-brief-shape" not in result.stdout


def test_heading_only_inside_a_code_fence_is_a_finding(tmp_path: Path) -> None:
    # A brief quoting a template in a code fence is showing the heading, not
    # carrying it. A fenced occurrence must not forge a heading the brief lacks.
    body = BUILD_BODY.replace(
        "**Out of scope:** o\n",
        "```markdown\n**Out of scope:** the template's line\n```\n",
    )
    result = run_with_issue(tmp_path, issue(33, VALID_DIRECT, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Out of scope" in result.stdout


def test_headings_beside_a_quoted_template_pass(tmp_path: Path) -> None:
    # The other direction: a brief carrying every heading for real, plus an
    # Artifacts fence quoting a brief template, is well-shaped — fence awareness
    # must not swallow the real headings around the fence.
    body = (
        BUILD_BODY
        + "\n## Artifacts\n\n````markdown\n**Summary:** one-line description\n\n"
        "**User intent:**\nWhy this issue exists.\n```\nnested fence\n```\n````\n"
    )
    result = run_with_issue(tmp_path, issue(34, VALID_DIRECT, body=body))
    assert "tracking.issue-brief-shape" not in result.stdout


def test_heading_inside_a_nested_fence_does_not_forge(tmp_path: Path) -> None:
    # A four-backtick artifact fence wraps three-backtick content without
    # closing early, so a heading between the inner fences is still quoted. The
    # real heading is dropped from the brief, so the assertion fails the moment
    # the outer fence is allowed to close on the inner one.
    body = BUILD_BODY.replace("**Out of scope:** o\n", "") + (
        "\n## Artifacts\n\n````markdown\n**Summary:** t\n"
        "```\n**Out of scope:** forged\n```\n````\n"
    )
    result = run_with_issue(tmp_path, issue(35, VALID_DIRECT, body=body))
    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "Out of scope" in result.stdout


def test_body_with_an_unclosed_fence_is_a_finding(tmp_path: Path) -> None:
    # A closer carrying an info string does not close, so the block runs to the
    # end of the body and the headings after it drop out of the scanned view.
    # The audit names the fence rather than reporting the headings it can no
    # longer see — and the run survives, so one malformed body does not blind
    # the audit for every other issue.
    body = "**Summary:** s\n\n```markdown\nquoted\n```markdown\n" + BUILD_BODY

    result = run_with_issue(tmp_path, issue(36, VALID_DIRECT, body=body))

    assert "alpha: tracking.issue-brief-shape" in result.stdout
    assert "unclosed" in result.stdout
    assert "missing" not in result.stdout


def test_pull_requests_are_ignored(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(11, ["phase:build"], body="", pull_request=True)
    )
    assert "software-factory.tuple-valid" not in result.stdout
    assert "tracking.issue-brief-shape" not in result.stdout


def _add_origin(repo: Path, url: str) -> None:
    """Give ``repo`` an ``origin`` remote, scrubbing any ambient ``GIT_DIR``.

    The scrub keeps ``-C repo`` authoritative even after ``ambient_git_dir``
    has exported a ``GIT_DIR`` naming the decoy, so this lands on ``repo`` by
    argument rather than by coincidence of the two paths agreeing.
    """
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", url],
        check=True,
        capture_output=True,
        env=gitrepo.no_git_env(),
    )


def test_ambient_git_dir_does_not_redirect_origin_slug(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    target = tmp_path / "target"
    init_repo(target)
    _add_origin(target, "git@github.com:target/target.git")
    decoy = ambient_git_dir("leaked.txt")
    _add_origin(decoy, "git@github.com:decoy/decoy.git")

    assert workspace_lint.origin_slug(target) == "target/target"

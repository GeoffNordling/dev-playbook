"""Behavioral tests for scripts/workspace-lint.

Fixtures build a throwaway workspace of git repos and point --workspace at
it. Every run puts a fake ``gh`` executable on PATH that serves canned JSON
from a file, so no test touches the network.
"""

import json
import os
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
    # A file read keeps its path, so a test can serve one file and not another.
    if resource == "contents":
        resource = "contents/" + "/".join(segs[4:])

# What a resource answers when a test says nothing about it. Protection defaults
# to fully protected under the canonical ruleset, so that a test about merge
# settings or labels does not have to restate the branch rules to stay clean.
CANONICAL = {
    "name": "protect-main",
    "enforcement": "ACTIVE",
    "bypassActors": {"nodes": []},
}
# The pin defaults: the hook repo's head is HEAD and its manifest publishes one
# id, and a consumer pins exactly that. So a test about anything else stays
# clean on the pin rule, and a test about the pin serves its own config.
HEAD = "HEAD_SHA"
MANIFEST = "- id: playbook-check\\n  entry: playbook check\\n  language: python\\n"
CONFIG = (
    "repos:\\n"
    "  - repo: HOOK_URL\\n"
    "    rev: HEAD_SHA\\n"
    "    hooks:\\n"
    "      - id: playbook-check\\n"
)
DEFAULTS = {
    "labels": [],
    "issues": [],
    "branches": {"commit": {"sha": HEAD}},
    "contents/.pre-commit-hooks.yaml": MANIFEST,
    "contents/.pre-commit-config.yaml": CONFIG,
    "protection": {
        "defaultBranchRef": {
            "name": "main",
            "rules": {
                "nodes": [
                    {"type": "NON_FAST_FORWARD", "repositoryRuleset": CANONICAL},
                    {"type": "DELETION", "repositoryRuleset": CANONICAL},
                ]
            },
        }
    },
}
WRAPPER_KEYS = ("settings", "protection", "labels", "issues", "branches")

data = json.load(open(os.environ["FAKE_GH_DATA"]))
# The hook repo is read for its head and manifest in every run, and a test that
# says nothing about it gets the defaults; any other unlisted slug is unreachable.
hook_repo_read = resource == "branches" or resource.startswith("contents/")
if slug not in data and not hook_repo_read:
    sys.exit(1)
entry = data.get(slug, {})

# An entry is either a bare settings dict (legacy) or a wrapper carrying any of
# settings / protection / labels / issues / branches / contents/<path>. A bare
# entry answers the base repo path with its settings and every other resource
# with that resource's default.
wrapper = isinstance(entry, dict) and any(
    k in WRAPPER_KEYS or k.startswith("contents/") for k in entry
)
if wrapper or slug not in data:
    payload = entry.get(resource, DEFAULTS.get(resource, {}))
else:
    payload = entry if resource == "settings" else DEFAULTS.get(resource, {})
# A file's text is served the way the contents endpoint serves it.
if resource.startswith("contents/") and isinstance(payload, str) and payload not in (
    "__unreachable__",
    "__badjson__",
):
    import base64
    payload = {
        "encoding": "base64",
        "content": base64.b64encode(payload.encode()).decode(),
    }
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


def protection(
    *types: str,
    branch: str = "main",
    ruleset: str | None = "protect-main",
    enforcement: str = "ACTIVE",
    bypass: int = 0,
) -> dict:
    """A default-branch rules payload as GraphQL serves it.

    No arguments is the unprotected repo — a default branch with an empty rule
    list, which is what a repo carrying no ruleset answers. The ruleset keywords
    describe the one ruleset behind every rule, defaulting to the canonical
    arrangement so that a test about rule types alone need not restate it;
    ``ruleset=None`` is the rule whose ruleset the read could not see.
    """
    behind = (
        None
        if ruleset is None
        else {
            "name": ruleset,
            "enforcement": enforcement,
            "bypassActors": {"nodes": [{"bypassMode": "ALWAYS"}] * bypass},
        }
    )
    return {
        "defaultBranchRef": {
            "name": branch,
            "rules": {
                "nodes": [{"type": t, "repositoryRuleset": behind} for t in types]
            },
        }
    }


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
    # The default consumer config pins the real hook URL, so the pin rule reads
    # it as the block it audits.
    gh.write_text(FAKE_GH.replace("HOOK_URL", workspace_lint.hook_repo_url()))
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
    assert "tracking.squash-only-merges" in ids
    assert "tracking.origin-on-github" in ids
    # the tracking and software-factory rules this slice adds
    assert "tracking.exactly-the-labels-the-scheme-declares" in ids
    assert "tracking.every-build-heading-in-bold" in ids
    assert "tracking.category-only" in ids
    assert "tracking.one-label-from-each-prefix" in ids
    assert "tracking.one-category-label-no-phase-or-tests" in ids
    assert all(
        rule.split(".")[0] in {"tracking", "distribution", "software-factory"}
        for rule in ids
    ), ids


# --- the workspace root ---


def test_missing_workspace_exits_two(tmp_path: Path) -> None:
    result = run(tmp_path / "nowhere")
    assert result.returncode == 2
    assert "workspace root not found" in result.stderr


# --- the governed roster ---


def test_ungoverned_repo_draws_no_output(tmp_path: Path) -> None:
    # Inclusion is the decision: a repo nobody listed is not a finding, not an
    # advisory, not a line. It is simply not this audit's business.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    make_workspace_repo(ws, "stranger", {"README.md": "# not ours\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(ws, "--settings-only", repos="alpha", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "stranger" not in result.stdout + result.stderr
    assert "1 repos" in result.stderr


def test_governed_repo_absent_from_this_machine_is_announced_and_passed_over(
    tmp_path: Path,
) -> None:
    # The workspace spans machines: a roster name with no repo behind it here
    # may live on another one, so the rest is audited and the absence is said.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(tmp_path, {"me/alpha": GOOD_SETTINGS})
    result = run(
        ws, "--settings-only", repos="alpha,ghost", gh_dir=gh_dir, gh_data=gh_data
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "not on this machine, not audited: ghost" in result.stderr
    assert "1 repos" in result.stderr


def test_governed_directory_without_git_is_not_a_repo(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    (ws / "plain").mkdir(parents=True)
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, repos="plain", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0
    assert "not on this machine, not audited: plain" in result.stderr
    assert "0 repos" in result.stderr


def test_roster_order_is_the_audit_order(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    drifted = dict(GOOD_SETTINGS, mergeCommitAllowed=True)
    data: dict[str, object] = {}
    for name in ("alpha", "beta"):
        make_workspace_repo(
            ws, name, {"README.md": "# R\n"}, origin=f"git@github.com:me/{name}.git"
        )
        data[f"me/{name}"] = drifted
    gh_dir, gh_data = make_fake_gh(tmp_path, data)
    result = run(
        ws, "--settings-only", repos="beta,alpha", gh_dir=gh_dir, gh_data=gh_data
    )
    assert result.stdout.index(
        "beta: tracking.squash-only-merges"
    ) < result.stdout.index("alpha: tracking.squash-only-merges")


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
        "alpha: tracking.squash-only-merges allow_merge_commit is True (want False)"
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
        "alpha: tracking.squash-only-merges unreachable via gh api (me/unknown)"
        in result.stdout
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
        "alpha: tracking.squash-only-merges unreachable via gh api (me/alpha)"
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
        "alpha: tracking.squash-only-merges unreachable via gh api (me/alpha)"
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
    assert (
        "alpha: tracking.squash-only-merges unreachable via gh api (me/alpha)"
        in result.stdout
    )


def test_repo_without_origin_is_a_finding(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.origin-on-github no GitHub origin; settings unchecked"
        in result.stdout
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
        "alpha: tracking.default-branch-protected-from-destructive-operations main is not protected against force-push"
        in result.stdout
    )
    assert (
        "alpha: tracking.default-branch-protected-from-destructive-operations main is not protected against deletion"
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
        "alpha: tracking.default-branch-protected-from-destructive-operations rules unreachable via gh api (me/alpha)"
        in result.stdout
    )
    assert "not protected against" not in result.stdout


def test_bypass_actor_on_the_guarding_ruleset_is_a_finding(tmp_path: Path) -> None:
    # The blind spot this closes: a bypass actor leaves both rules in force, so
    # the branch reads protected while whoever holds the bypass can still erase
    # it. Nothing about the rule types themselves shows the exemption.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("NON_FAST_FORWARD", "DELETION", bypass=2),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.default-branch-protected-from-destructive-operations ruleset 'protect-main' grants bypass "
        "to 2 actors (want none)" in result.stdout
    )
    assert "not protected against" not in result.stdout


def test_one_bypass_actor_is_reported_in_the_singular(tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("NON_FAST_FORWARD", "DELETION", bypass=1),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "grants bypass to 1 actor (want none)" in result.stdout


def test_protection_under_another_name_is_a_finding(tmp_path: Path) -> None:
    # The branch is genuinely protected; what it is not is filed where the
    # standard says to file it, so the finding names both.
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
                    "NON_FAST_FORWARD", "DELETION", ruleset="no-touchy"
                ),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.default-branch-protected-from-destructive-operations main is protected by 'no-touchy', "
        "not by the canonical 'protect-main'" in result.stdout
    )
    assert "not protected against" not in result.stdout


def test_unprotected_branch_is_not_also_told_it_lacks_the_canonical_ruleset(
    tmp_path: Path,
) -> None:
    # A repo carrying no ruleset at all owes the two rules, and hears that. The
    # name finding would be a third line saying the same absence again.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path, {"me/alpha": {"settings": GOOD_SETTINGS, "protection": protection()}}
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert "canonical" not in result.stdout
    assert len(result.stdout.strip().splitlines()) == 2


def test_inactive_ruleset_enforcement_is_a_finding(tmp_path: Path) -> None:
    # GitHub is documented to serve only active rulesets' rules here, so this
    # asserts that documented behavior rather than trusting it.
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
                    "NON_FAST_FORWARD", "DELETION", enforcement="EVALUATE"
                ),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "ruleset 'protect-main' enforcement is 'EVALUATE' (want 'ACTIVE')"
        in result.stdout
    )


def test_unreadable_ruleset_is_surfaced_not_read_as_bypassless(
    tmp_path: Path,
) -> None:
    # A rule whose ruleset the read could not see is still in force, so the two
    # rule findings stay quiet — but nothing is known about its bypass list, and
    # silence there would be indistinguishable from an empty one.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    gh_dir, gh_data = make_fake_gh(
        tmp_path,
        {
            "me/alpha": {
                "settings": GOOD_SETTINGS,
                "protection": protection("NON_FAST_FORWARD", "DELETION", ruleset=None),
            }
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        "alpha: tracking.default-branch-protected-from-destructive-operations a ruleset protecting main could not "
        "be read" in result.stdout
    )
    assert "not protected against" not in result.stdout


def test_a_bypassed_ruleset_carrying_nothing_required_is_not_judged(
    tmp_path: Path,
) -> None:
    # Only rulesets supplying a required rule can hand one back. A repo's other
    # rulesets — a PR-review ruleset with an admin bypass, say — are its own
    # business, so neither their name nor their bypass list is measured.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    canonical = protection("NON_FAST_FORWARD", "DELETION")
    other = protection("PULL_REQUEST", ruleset="reviews", bypass=3)
    canonical["defaultBranchRef"]["rules"]["nodes"] += other["defaultBranchRef"][
        "rules"
    ]["nodes"]
    gh_dir, gh_data = make_fake_gh(
        tmp_path, {"me/alpha": {"settings": GOOD_SETTINGS, "protection": canonical}}
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_the_required_rules_may_be_split_across_rulesets(tmp_path: Path) -> None:
    # The floor is measured on the branch, not on one ruleset: a repo that files
    # the second rule elsewhere is still protected, and both rulesets are judged
    # for bypass because either one could hand its rule back.
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    split = protection("NON_FAST_FORWARD")
    extra = protection("DELETION", ruleset="no-delete", bypass=1)
    split["defaultBranchRef"]["rules"]["nodes"] += extra["defaultBranchRef"]["rules"][
        "nodes"
    ]
    gh_dir, gh_data = make_fake_gh(
        tmp_path, {"me/alpha": {"settings": GOOD_SETTINGS, "protection": split}}
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "not protected against" not in result.stdout
    assert "canonical" not in result.stdout
    assert "ruleset 'no-delete' grants bypass to 1 actor (want none)" in result.stdout


def test_repo_without_origin_draws_one_finding_not_two(tmp_path: Path) -> None:
    # tracking.origin-on-github already says the origin is missing; protection stays quiet
    # rather than reporting the same absent repo a second time.
    ws = tmp_path / "ws"
    make_workspace_repo(ws, "alpha", {"README.md": "# A\n"})
    gh_dir, gh_data = make_fake_gh(tmp_path, {})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert (
        "tracking.default-branch-protected-from-destructive-operations"
        not in result.stdout
    )
    assert len(result.stdout.strip().splitlines()) == 1


# --- the pin ---

PIN_RULE = "distribution.a-consumer-pins-the-published-head"


def pin_repo(
    tmp_path: Path,
    hook_repo: dict[str, object] | None = None,
    config: str | None = None,
) -> tuple[Path, Path, Path]:
    """A one-repo workspace with good settings, whose fake gh serves ``config``
    as alpha's published pre-commit config and, when given, the hook repo's
    head and manifest; either left None takes the fake's clean default."""
    ws = tmp_path / "ws"
    make_workspace_repo(
        ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"
    )
    alpha: dict[str, object] = {"settings": GOOD_SETTINGS}
    if config is not None:
        alpha["contents/.pre-commit-config.yaml"] = config
    data: dict[str, object] = {"me/alpha": alpha}
    if hook_repo is not None:
        data[workspace_lint.hook_repo_slug()] = hook_repo
    gh_dir, gh_data = make_fake_gh(tmp_path, data)
    return ws, gh_dir, gh_data


def pin_config(rev: str, *ids: str) -> str:
    """A consumer config pinning the hook repo at ``rev`` with ``ids`` under it."""
    hooks = "".join(f"      - id: {i}\n" for i in ids)
    url = workspace_lint.hook_repo_url()
    return f"repos:\n  - repo: {url}\n    rev: {rev}\n    hooks:\n{hooks}"


def test_a_consumer_at_the_published_head_draws_no_pin_finding(
    tmp_path: Path,
) -> None:
    ws, gh_dir, gh_data = pin_repo(tmp_path)
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_pin_behind_the_head_is_a_finding(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = pin_repo(
        tmp_path,
        config=pin_config("OLD_SHA", "playbook-check"),
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        f"alpha: {PIN_RULE} pinned OLD_SHA, published head is HEAD_SHA" in result.stdout
    )


def test_a_stale_hook_id_is_a_finding_even_at_the_head(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = pin_repo(
        tmp_path,
        config=pin_config("HEAD_SHA", "playbook-lint"),
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert (
        f"alpha: {PIN_RULE} hook ids playbook-lint; the manifest publishes playbook-check"
        in result.stdout
    )
    assert "published head is" not in result.stdout


def test_a_consumer_with_no_pin_is_a_finding(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = pin_repo(
        tmp_path,
        config="repos: []\n",
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert f"alpha: {PIN_RULE} no {workspace_lint.hook_repo_url()} pin" in result.stdout


def test_a_consumer_with_no_config_on_main_is_a_finding(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = pin_repo(tmp_path, config="__unreachable__")
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert f"alpha: {PIN_RULE} no .pre-commit-config.yaml on main" in result.stdout


def test_the_head_and_manifest_follow_the_hook_repo_as_github_has_it(
    tmp_path: Path,
) -> None:
    # The fake's default head is HEAD_SHA; the hook repo entry moves it, and
    # the consumer left at HEAD_SHA is now behind.
    ws, gh_dir, gh_data = pin_repo(
        tmp_path,
        hook_repo={
            "branches": {"commit": {"sha": "NEWER_SHA"}},
            "contents/.pre-commit-hooks.yaml": "- id: playbook-check\n  entry: x\n",
        },
    )
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 1
    assert "pinned HEAD_SHA, published head is NEWER_SHA" in result.stdout


def test_an_unreadable_hook_repo_head_stops_the_run(tmp_path: Path) -> None:
    ws, gh_dir, gh_data = pin_repo(tmp_path, hook_repo={"branches": "__unreachable__"})
    result = run(ws, "--settings-only", gh_dir=gh_dir, gh_data=gh_data)
    assert result.returncode == 2
    assert "cannot read main's head sha" in result.stderr


def test_the_hook_repo_itself_is_passed_over(tmp_path: Path) -> None:
    # dev-playbook is governed and pins nothing; the audit knows it by identity.
    lines = workspace_lint.check_pin(
        HOOK_REPO, "GeoffNordling/dev-playbook", "url", "HEAD", ("playbook-check",)
    )
    assert lines == []


def test_a_worktree_of_the_hook_repo_is_the_hook_repo(tmp_path: Path) -> None:
    # Identity is the shared .git directory, so the main checkout and a
    # worktree of it — wherever either sits on disk — are one repo.
    worktree = tmp_path / "wt"
    subprocess.run(
        [
            "git",
            "-C",
            str(HOOK_REPO),
            "worktree",
            "add",
            "-q",
            "--detach",
            str(worktree),
        ],
        check=True,
        capture_output=True,
        env=gitrepo.no_git_env(),
    )
    try:
        assert workspace_lint.is_hook_repo(worktree)
        assert workspace_lint.is_hook_repo(HOOK_REPO)
    finally:
        subprocess.run(
            [
                "git",
                "-C",
                str(HOOK_REPO),
                "worktree",
                "remove",
                "--force",
                str(worktree),
            ],
            check=True,
            capture_output=True,
            env=gitrepo.no_git_env(),
        )


def test_another_repo_is_not_the_hook_repo(tmp_path: Path) -> None:
    other = tmp_path / "other"
    init_repo(other)
    assert not workspace_lint.is_hook_repo(other)
    assert not workspace_lint.is_hook_repo(tmp_path / "nowhere")


def test_pinned_hook_ids_reads_the_block_for_the_url() -> None:
    url = workspace_lint.hook_repo_url()
    assert workspace_lint.pinned_hook_ids(pin_config("X", "a", "b"), url) == ("a", "b")
    assert workspace_lint.pinned_hook_ids(pin_config("X"), url) == ()
    assert workspace_lint.pinned_hook_ids("repos: []\n", url) is None
    assert workspace_lint.pinned_hook_ids("- not a mapping\n", url) is None


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
    assert "tracking.exactly-the-labels-the-scheme-declares" not in result.stdout


def test_missing_canonical_label_is_a_finding(tmp_path: Path) -> None:
    labels = [obj for obj in canonical_label_objects() if obj["name"] != "mode:spike"]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert (
        "alpha: tracking.exactly-the-labels-the-scheme-declares missing label mode:spike"
        in result.stdout
    )
    assert result.returncode == 1


def test_drifted_label_color_is_a_finding(tmp_path: Path) -> None:
    labels = canonical_label_objects()
    labels[0] = dict(labels[0], color="ff0000")
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.exactly-the-labels-the-scheme-declares" in result.stdout
    assert labels[0]["name"] in result.stdout


def test_drifted_label_description_is_a_finding(tmp_path: Path) -> None:
    labels = canonical_label_objects()
    labels[0] = dict(labels[0], description="wrong")
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert "alpha: tracking.exactly-the-labels-the-scheme-declares" in result.stdout
    assert labels[0]["name"] in result.stdout


def test_unexpected_label_is_a_finding(tmp_path: Path) -> None:
    labels = [
        *canonical_label_objects(),
        {"name": "wip", "color": "cccccc", "description": ""},
    ]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert (
        "alpha: tracking.exactly-the-labels-the-scheme-declares unexpected label wip"
        in result.stdout
    )


# --- blocked labels (own rule, overlapping the closed world by design) ---


def test_blocked_label_is_an_unexpected_label(tmp_path: Path) -> None:
    # The scheme has no blocked state, so a label naming one is outside the
    # closed world; valid-labels is the one rule that flags it.
    labels = [
        *canonical_label_objects(),
        {"name": "status:Blocked", "color": "cccccc", "description": ""},
    ]
    ws, gh_dir, gh_data = full_mode_repo(tmp_path, labels=labels)
    result = run(ws, gh_dir=gh_dir, gh_data=gh_data)
    assert (
        "alpha: tracking.exactly-the-labels-the-scheme-declares unexpected label status:Blocked"
        in result.stdout
    )


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
    assert (
        "alpha: tracking.squash-only-merges unreachable via gh api (me/alpha)"
        in result.stdout
    )
    assert (
        "beta: tracking.squash-only-merges allow_merge_commit is True (want False)"
        in (result.stdout)
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
    "**Key interfaces:** none\n\n**Acceptance criteria:** a\n\n"
    "**Prohibited surfaces:** none\n\n**Out of scope:** o\n"
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
    assert "tracking.one-label-from-each-prefix" not in result.stdout
    assert "tracking.every-build-heading-in-bold" not in result.stdout
    assert "tracking.category-only" not in result.stdout


def test_untriaged_issue_is_out_of_scope(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(2, ["phase:intake"], body=""))
    assert "tracking.one-label-from-each-prefix" not in result.stdout
    assert "tracking.every-build-heading-in-bold" not in result.stdout


def test_leaf_missing_mode_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "tests:no", "phase:build"]
    result = run_with_issue(tmp_path, issue(7, labels, body=BUILD_BODY))
    assert "alpha: tracking.one-label-from-each-prefix" in result.stdout
    assert "#7" in result.stdout
    assert "mode" in result.stdout


def test_leaf_invalid_phase_value_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:direct", "tests:no", "phase:frobnicate"]
    result = run_with_issue(tmp_path, issue(8, labels, body=BUILD_BODY))
    assert "alpha: tracking.one-label-from-each-prefix" in result.stdout
    assert "phase" in result.stdout


def test_leaf_invalid_mode_value_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:frobnicate", "tests:yes", "phase:build"]
    result = run_with_issue(tmp_path, issue(9, labels, body=BUILD_BODY))
    assert "alpha: tracking.one-label-from-each-prefix" in result.stdout
    assert "mode:frobnicate is not a scheme value" in result.stdout


def test_spike_leaf_requires_tests_no(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:spike", "tests:yes", "phase:spike"]
    result = run_with_issue(tmp_path, issue(10, labels, body=SPIKE_BODY))
    assert (
        "alpha: tracking.one-label-from-each-prefix-tests-fixed-at-no" in result.stdout
    )
    assert "tests:no" in result.stdout


def test_epic_with_phase_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "phase:build"]
    result = run_with_issue(tmp_path, issue(3, labels, sub_issues_total=4))
    assert "alpha: tracking.category-only" in result.stdout
    assert "#3" in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout


def test_wellformed_epic_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(4, ["category:extension"], sub_issues_total=4)
    )
    assert "tracking.category-only" not in result.stdout


def test_epic_with_mode_label_but_no_phase_is_a_finding(tmp_path: Path) -> None:
    # An epic carrying a mode/tests label but no phase label is still malformed:
    # the category-only invariant holds regardless of triage state.
    labels = ["category:extension", "mode:direct"]
    result = run_with_issue(tmp_path, issue(12, labels, sub_issues_total=3))
    assert "alpha: tracking.category-only" in result.stdout
    assert "#12" in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout


def test_epic_without_category_label_is_a_finding(tmp_path: Path) -> None:
    # "An epic carries a category label only" is a positive invariant too: an
    # epic with no category label at all is malformed.
    result = run_with_issue(tmp_path, issue(13, [], sub_issues_total=2))
    assert "alpha: tracking.category-only" in result.stdout
    assert "#13" in result.stdout


def test_epic_with_two_category_labels_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "category:maintenance"]
    result = run_with_issue(tmp_path, issue(14, labels, sub_issues_total=2))
    assert "alpha: tracking.category-only" in result.stdout
    assert "#14" in result.stdout


def test_epic_with_invalid_category_value_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(15, ["category:frobnicate"], sub_issues_total=2)
    )
    assert "alpha: tracking.category-only" in result.stdout
    assert "#15" in result.stdout


# --- the session leaf: user-led, never dispatched ---

SESSION_BODY = (
    "**Summary:** s\n\n**User intent:** i\n\n"
    "**Current behavior:** c\n\n**Desired behavior:** d\n\n"
    "**Acceptance criteria:** a\n\n**Out of scope:** Unknown; dealt with when found.\n"
)
VALID_SESSION = ["category:extension", "mode:session"]


def test_wellformed_session_leaf_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(40, VALID_SESSION, body=SESSION_BODY))
    assert "tracking.one-category-label-no-phase-or-tests" not in result.stdout
    assert "tracking.every-session-heading-in-bold" not in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_session_leaf_is_checked_without_a_phase_label(tmp_path: Path) -> None:
    # No phase label means the post-intake gate never opens; the session
    # branch is what makes the brief visible to the audit at all.
    body = SESSION_BODY.replace("**Acceptance criteria:** a\n\n", "")
    result = run_with_issue(tmp_path, issue(41, VALID_SESSION, body=body))
    assert "alpha: tracking.every-session-heading-in-bold" in result.stdout
    assert "Acceptance criteria" in result.stdout


def test_session_leaf_never_needs_the_factory_only_headings(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(42, VALID_SESSION, body=SESSION_BODY))
    assert "Key interfaces" not in result.stdout
    assert "Prohibited surfaces" not in result.stdout


def test_session_leaf_with_phase_label_is_a_finding(tmp_path: Path) -> None:
    labels = [*VALID_SESSION, "phase:build"]
    result = run_with_issue(tmp_path, issue(43, labels, body=SESSION_BODY))
    assert "alpha: tracking.one-category-label-no-phase-or-tests" in result.stdout
    assert "phase:build" in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout


def test_session_leaf_with_tests_label_is_a_finding(tmp_path: Path) -> None:
    labels = [*VALID_SESSION, "tests:no"]
    result = run_with_issue(tmp_path, issue(44, labels, body=SESSION_BODY))
    assert "alpha: tracking.one-category-label-no-phase-or-tests" in result.stdout
    assert "tests:no" in result.stdout


def test_session_leaf_with_second_mode_is_a_finding(tmp_path: Path) -> None:
    labels = [*VALID_SESSION, "mode:direct"]
    result = run_with_issue(tmp_path, issue(45, labels, body=SESSION_BODY))
    assert "alpha: tracking.one-category-label-no-phase-or-tests" in result.stdout
    assert "mode:direct" in result.stdout


def test_session_leaf_without_category_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(46, ["mode:session"], body=SESSION_BODY))
    assert "alpha: tracking.one-category-label-no-phase-or-tests" in result.stdout
    assert "missing category" in result.stdout


def test_session_leaf_with_invalid_category_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:frobnicate", "mode:session"]
    result = run_with_issue(tmp_path, issue(47, labels, body=SESSION_BODY))
    assert "alpha: tracking.one-category-label-no-phase-or-tests" in result.stdout
    assert "category:frobnicate" in result.stdout


def test_epic_carrying_mode_session_is_an_epic_finding(tmp_path: Path) -> None:
    # Children make an epic before a mode label makes a session leaf.
    result = run_with_issue(
        tmp_path, issue(48, VALID_SESSION, body="", sub_issues_total=2)
    )
    assert "alpha: tracking.category-only" in result.stdout
    assert "tracking.one-category-label-no-phase-or-tests" not in result.stdout


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
    assert "tracking.one-wayfinder-label-and-nothing-else" not in result.stdout
    assert "tracking.category-only" not in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_map_is_told_by_its_label_not_by_having_children(tmp_path: Path) -> None:
    # A freshly charted map with no tickets yet is still a map, not a leaf.
    result = run_with_issue(
        tmp_path, issue(17, ["wayfinder:map"], body=MAP_BODY, sub_issues_total=0)
    )
    assert "tracking.one-wayfinder-label-and-nothing-else" not in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout


def test_map_carrying_a_factory_label_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:map", "category:extension", "phase:build"]
    result = run_with_issue(
        tmp_path, issue(18, labels, body=MAP_BODY, sub_issues_total=2)
    )
    assert "alpha: tracking.one-wayfinder-label-and-nothing-else" in result.stdout
    assert "#18" in result.stdout
    assert "category:extension" in result.stdout
    assert "phase:build" in result.stdout


def test_map_missing_a_body_section_is_a_finding(tmp_path: Path) -> None:
    body = MAP_BODY.replace("## Not yet specified\n\nf\n\n", "")
    result = run_with_issue(
        tmp_path, issue(19, ["wayfinder:map"], body=body, sub_issues_total=2)
    )
    assert "alpha: tracking.map-sections-ticket-question" in result.stdout
    assert "Not yet specified" in result.stdout


def test_map_also_carrying_a_ticket_type_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:map", "wayfinder:research"]
    result = run_with_issue(
        tmp_path, issue(21, labels, body=MAP_BODY, sub_issues_total=2)
    )
    assert "alpha: tracking.one-wayfinder-label-and-nothing-else" in result.stdout
    assert "a map is not a ticket" in result.stdout


def test_wellformed_ticket_raises_no_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(22, ["wayfinder:research"], body=TICKET_BODY)
    )
    assert "tracking.one-wayfinder-label-and-nothing-else" not in result.stdout
    assert "tracking.one-label-from-each-prefix" not in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr


def test_ticket_carrying_a_factory_label_is_a_finding(tmp_path: Path) -> None:
    # A ticket carries no phase label, so it used to fall past the post-intake
    # gate entirely; it is now checked against its own contract.
    labels = ["wayfinder:grilling", "mode:direct", "tests:no"]
    result = run_with_issue(tmp_path, issue(23, labels, body=TICKET_BODY))
    assert "alpha: tracking.one-wayfinder-label-and-nothing-else" in result.stdout
    assert "#23" in result.stdout
    assert "a decision ticket carries no factory label" in result.stdout


def test_ticket_missing_its_question_section_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(tmp_path, issue(24, ["wayfinder:task"], body=""))
    assert "alpha: tracking.map-sections-ticket-question" in result.stdout
    assert "Question" in result.stdout


def test_ticket_with_two_wayfinder_labels_is_a_finding(tmp_path: Path) -> None:
    labels = ["wayfinder:research", "wayfinder:grilling"]
    result = run_with_issue(tmp_path, issue(25, labels, body=TICKET_BODY))
    assert "alpha: tracking.one-wayfinder-label-and-nothing-else" in result.stdout
    assert "multiple wayfinder labels" in result.stdout


def test_ticket_with_an_out_of_scheme_type_is_a_finding(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(26, ["wayfinder:frobnicate"], body=TICKET_BODY)
    )
    assert "alpha: tracking.one-wayfinder-label-and-nothing-else" in result.stdout
    assert "is not a scheme value" in result.stdout


def test_childed_issue_without_a_wayfinder_label_still_checks_as_an_epic(
    tmp_path: Path,
) -> None:
    # The species dispatch keys on the wayfinder labels; an ordinary issue with
    # children is still a build epic and still carries the epic's shape.
    result = run_with_issue(tmp_path, issue(27, [], sub_issues_total=2))
    assert "alpha: tracking.category-only" in result.stdout
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
    assert "alpha: tracking.every-build-heading-in-bold" in result.stdout
    assert "Out of scope" in result.stdout


def test_build_leaf_missing_user_intent_is_a_finding(tmp_path: Path) -> None:
    # User intent is a required build-leaf heading, not an optional one: a brief
    # that never says why the work exists leaves the builder with no way to
    # choose among permitted fixes.
    body = BUILD_BODY.replace("**User intent:** i\n\n", "")
    result = run_with_issue(tmp_path, issue(32, VALID_DIRECT, body=body))
    assert "alpha: tracking.every-build-heading-in-bold" in result.stdout
    assert "User intent" in result.stdout


def test_build_leaf_missing_prohibited_surfaces_is_a_finding(tmp_path: Path) -> None:
    # Prohibited surfaces is a required build-leaf heading: it names the
    # codebase territory the issue must not touch, which is what makes the
    # second deviation limiter mechanical rather than a judgment call.
    body = BUILD_BODY.replace("**Prohibited surfaces:** none\n\n", "")
    result = run_with_issue(tmp_path, issue(37, VALID_DIRECT, body=body))
    assert "alpha: tracking.every-build-heading-in-bold" in result.stdout
    assert "Prohibited surfaces" in result.stdout


def test_spike_leaf_missing_heading_is_a_finding(tmp_path: Path) -> None:
    labels = ["category:extension", "mode:spike", "tests:no", "phase:spike"]
    body = SPIKE_BODY.replace("**Deliverable:** d\n", "")
    result = run_with_issue(tmp_path, issue(6, labels, body=body))
    assert "alpha: tracking.summary-question-and-deliverable" in result.stdout
    assert "Deliverable" in result.stdout


def test_heading_with_colon_outside_bold_is_accepted(tmp_path: Path) -> None:
    # `**Summary**:` (colon after the close markers) reads as a present heading
    # to a reader; it must not draw a false brief-shape finding.
    body = (
        "**Summary**: s\n\n**User intent**: i\n\n"
        "**Current behavior**: c\n\n**Desired behavior**: d\n\n"
        "**Key interfaces**: none\n\n**Acceptance criteria**: a\n\n"
        "**Prohibited surfaces**: none\n\n**Out of scope**: o\n"
    )
    result = run_with_issue(tmp_path, issue(31, VALID_DIRECT, body=body))
    assert "tracking.every-build-heading-in-bold" not in result.stdout


def test_heading_only_inside_a_code_fence_is_a_finding(tmp_path: Path) -> None:
    # A brief quoting a template in a code fence is showing the heading, not
    # carrying it. A fenced occurrence must not forge a heading the brief lacks.
    body = BUILD_BODY.replace(
        "**Out of scope:** o\n",
        "```markdown\n**Out of scope:** the template's line\n```\n",
    )
    result = run_with_issue(tmp_path, issue(33, VALID_DIRECT, body=body))
    assert "alpha: tracking.every-build-heading-in-bold" in result.stdout
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
    assert "tracking.every-build-heading-in-bold" not in result.stdout


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
    assert "alpha: tracking.every-build-heading-in-bold" in result.stdout
    assert "Out of scope" in result.stdout


def test_body_with_an_unclosed_fence_is_a_finding(tmp_path: Path) -> None:
    # A closer carrying an info string does not close, so the block runs to the
    # end of the body and the headings after it drop out of the scanned view.
    # The audit names the fence rather than reporting the headings it can no
    # longer see — and the run survives, so one malformed body does not blind
    # the audit for every other issue.
    body = "**Summary:** s\n\n```markdown\nquoted\n```markdown\n" + BUILD_BODY

    result = run_with_issue(tmp_path, issue(36, VALID_DIRECT, body=body))

    assert "alpha: tracking.closed-fences" in result.stdout
    assert "unclosed" in result.stdout
    assert "missing" not in result.stdout


def test_pull_requests_are_ignored(tmp_path: Path) -> None:
    result = run_with_issue(
        tmp_path, issue(11, ["phase:build"], body="", pull_request=True)
    )
    assert "tracking.one-label-from-each-prefix" not in result.stdout
    assert "tracking.every-build-heading-in-bold" not in result.stdout


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

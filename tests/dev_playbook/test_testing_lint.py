"""Behavioral tests for scripts/testing-lint.

testing-lint walks a repo's Python files once and applies three rules to the
test files it finds: no-private-access (privacy of non-test modules),
mirror-layout (test placement), and no-logic (no if/try in a test body).
Discovery goes through `git ls-files`, so every fixture is a git repo; a
directory (repo root) is the only positional argument.
"""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "testing-lint"


def run(repo: Path) -> subprocess.CompletedProcess:
    """Run testing-lint against repo and capture its output."""
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write files into a fresh git repo and return its root."""
    repo = tmp_path / "repo"
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    return repo


# --- no-private-access rule ---


def test_import_of_private_name_from_non_test_module_is_flagged(
    tmp_path: Path,
) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_thing.py": "from mypkg.thing import _secret\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-private-access" in result.stdout
    assert "tests/test_thing.py" in result.stdout


def test_attribute_access_into_private_name_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_thing.py": "import mypkg.thing\n\n\ndef test_it():\n    mypkg.thing._secret()\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-private-access" in result.stdout


def test_import_and_attribute_reach_share_one_rule_id(tmp_path: Path) -> None:
    """Both reaches collapse onto testing.no-private-access; the message differs."""
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_import.py": "from mypkg.thing import _secret\n",
            "tests/test_attr.py": "import mypkg.thing\n\n\ndef test_it():\n    mypkg.thing._secret()\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "privacy" not in result.stdout
    assert "imports private name" in result.stdout
    assert "reaches into private name" in result.stdout


def test_dunder_access_is_public(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "class T:\n    pass\n",
            "tests/test_thing.py": "import mypkg.thing\n\n\ndef test_it():\n    mypkg.thing.__name__\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_public_access_in_test_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "from mypkg.thing import public\n\n\ndef test_it():\n    assert public() == 1\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_privacy_scans_deprecated_tree(tmp_path: Path) -> None:
    """The privacy rule's only exclusions are caches, so deprecated/ is scanned."""
    repo = make_repo(
        tmp_path,
        {
            "deprecated/thing.py": "def _secret():\n    return 1\n",
            "deprecated/tests/test_thing.py": "from deprecated.thing import _secret\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-private-access" in result.stdout
    assert "deprecated/tests/test_thing.py" in result.stdout


# --- mirror-layout rule ---


def test_test_file_off_its_module_mirror_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.mirror-layout" in result.stdout
    assert "tests/test_thing.py" in result.stdout
    assert "tests/pkg/test_thing.py" in result.stdout


def test_test_file_at_its_module_mirror_is_clean(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_at_scope_nested_mirror_under_unit_is_clean(tmp_path: Path) -> None:
    """A mirror nested beneath the SDD unit scope root is an accepted location."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/unit/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_at_scope_nested_mirror_under_integration_is_clean(
    tmp_path: Path,
) -> None:
    """A mirror nested beneath the SDD integration scope root is accepted."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/integration/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_at_scope_nested_mirror_under_agent_review_is_clean(
    tmp_path: Path,
) -> None:
    """A mirror nested beneath the SDD agent_review scope root is accepted."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/agent_review/pkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_flat_inside_a_scope_root_is_flagged(tmp_path: Path) -> None:
    """A scope root is a mirror root, not an exemption: the package path is still required."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/unit/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.mirror-layout" in result.stdout
    assert "tests/unit/test_thing.py" in result.stdout


def test_test_file_at_wrong_location_inside_a_scope_root_is_flagged(
    tmp_path: Path,
) -> None:
    """Neither the plain mirror nor the scope-nested mirror: still a finding."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/unit/otherpkg/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.mirror-layout" in result.stdout
    assert "tests/unit/otherpkg/test_thing.py" in result.stdout


def test_plain_mirror_of_a_scope_root_named_src_package_is_clean(
    tmp_path: Path,
) -> None:
    """When a src package is itself named after a scope root, its plain mirror still passes."""
    repo = make_repo(
        tmp_path,
        {
            "src/integration/thing.py": "def public():\n    return 1\n",
            "tests/integration/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_matching_no_module_in_a_scope_root_is_outside_the_rule(
    tmp_path: Path,
) -> None:
    """A flattened name whose stem names no src module stays exempt inside a scope root."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/render.py": "def public():\n    return 1\n",
            "tests/unit/test_pkg_render_edgecases.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_matching_no_module_is_outside_the_rule(tmp_path: Path) -> None:
    """A flattened name whose stem names no src module is not policed."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/render.py": "def public():\n    return 1\n",
            "tests/test_pkg_render_edgecases.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_conftest_is_outside_the_rule(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/conftest.py": "x = 1\n",
            "tests/conftest.py": "import pytest\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_test_file_outside_the_top_level_tests_tree_is_outside_the_rule(
    tmp_path: Path,
) -> None:
    """A nested scaffold's test tree is not matched against the repo's src/."""
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/cli.py": "def public():\n    return 1\n",
            "templates/scaffold/tests/test_cli.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_mirror_finding_is_file_level_without_a_line(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "src/pkg/thing.py": "def public():\n    return 1\n",
            "tests/test_thing.py": "def test_it():\n    pass\n",
        },
    )
    result = run(repo)
    assert "tests/test_thing.py: testing.mirror-layout " in result.stdout


# --- no-logic rule ---


def test_if_statement_in_a_test_body_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {"tests/test_x.py": "def test_it():\n    if True:\n        assert 1\n"},
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-logic" in result.stdout
    assert "tests/test_x.py" in result.stdout


def test_try_statement_in_a_test_body_is_flagged(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def test_it():\n"
                "    try:\n"
                "        assert 1\n"
                "    except AssertionError:\n"
                "        pass\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-logic" in result.stdout


def test_if_nested_in_a_loop_in_a_test_body_is_flagged(tmp_path: Path) -> None:
    """A loop is legal, but an if nested inside it is still logic in the body."""
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def test_it():\n"
                "    for i in range(3):\n"
                "        if i:\n"
                "            assert i\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "testing.no-logic" in result.stdout


def test_if_inside_a_nested_helper_is_exempt(tmp_path: Path) -> None:
    """A helper defined inside a test may branch; only the test body is policed."""
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def test_it():\n"
                "    def walk(n):\n"
                "        if n:\n"
                "            return walk(n - 1)\n"
                "        return 0\n"
                "    assert walk(3) == 0\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_loops_are_legal(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def test_it():\n"
                "    total = 0\n"
                "    for i in range(3):\n"
                "        total += i\n"
                "    assert total == 3\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_ternary_and_comprehension_filter_are_legal(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def test_it():\n"
                "    x = 1 if True else 0\n"
                "    ys = [n for n in range(5) if n % 2]\n"
                "    assert x == 1 and ys == [1, 3]\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_if_in_a_non_test_helper_is_exempt(tmp_path: Path) -> None:
    """Module-level fixtures and helpers are outside the rule; only test_* funcs."""
    repo = make_repo(
        tmp_path,
        {
            "tests/test_x.py": (
                "def build(n):\n"
                "    if n:\n"
                "        return n\n"
                "    return 0\n"
                "\n\n"
                "def test_it():\n"
                "    assert build(1) == 1\n"
            )
        },
    )
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr


# --- rule ids and finding format ---


def test_list_rules_prints_card_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    """--list-rules names every rule, card-prefixed, needing no repository."""
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = result.stdout.split()
    assert "testing.no-private-access" in ids
    assert "testing.mirror-layout" in ids
    assert "testing.no-logic" in ids


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_repo(
        tmp_path,
        {
            "mypkg/thing.py": "def _secret():\n    return 1\n",
            "tests/test_thing.py": "from mypkg.thing import _secret\n",
        },
    )
    result = run(repo)
    assert result.returncode == 1
    assert "tests/test_thing.py:1: testing.no-private-access " in result.stdout

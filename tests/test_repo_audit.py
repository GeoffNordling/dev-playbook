"""Behavioral tests for scripts/repo-audit.

Every fixture is a git repo (discovery and the repo-name mapping both go
through git) with all files staged, since "committed" requirements read the
index. Fixtures copy the real canonical artifacts from standards/build/canonical/,
so these tests also pin that the canonical files themselves stay auditable.
"""

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "repo-audit"
CANONICAL = Path(__file__).resolve().parents[1] / "standards" / "build" / "canonical"

UV_SCRIPT = (
    "#!/usr/bin/env -S uv run --script\n"
    "# /// script\n"
    '# requires-python = ">=3.14"\n'
    "# ///\n"
    'print("hi")\n'
)


def canonical(name: str) -> str:
    return (CANONICAL / name).read_text()


def run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )


def make_repo(
    tmp_path: Path,
    files: dict[str, str],
    name: str = "sample-repo",
    executable: tuple[str, ...] = (),
) -> Path:
    repo = tmp_path / name
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for rel in executable:
        os.chmod(repo / rel, 0o755)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True
    )
    return repo


def base_files() -> dict[str, str]:
    return {
        "README.md": "# Sample Repo\n\nOne line of purpose.\n",
        "CLAUDE.md": canonical("CLAUDE.md.standards"),
        "index.md": "# Index\n",
        ".gitignore": canonical(".gitignore"),
        ".pre-commit-config.yaml": canonical(".pre-commit-config.yaml").replace(
            "<pinned-sha>", "0123abcd"
        ),
        "Makefile": canonical("Makefile.base"),
        ".github/workflows/ci.yml": canonical("ci.yml"),
    }


def python_files(code_roots: str = "src tests") -> dict[str, str]:
    files = base_files()
    files.update(
        {
            "pyproject.toml": canonical("pyproject.toml")
            .replace("<repo>", "sample-repo")
            .replace("<package>", "sample_repo"),
            "uv.lock": "# lock\n",
            ".python-version": canonical(".python-version"),
            "src/sample_repo/__init__.py": "",
            "tests/test_sample.py": "def test_ok() -> None:\n    assert True\n",
            "Makefile": canonical("Makefile.python").replace(
                "<code-roots>", code_roots
            ),
        }
    )
    return files


def scripts_only_files() -> dict[str, str]:
    files = python_files(code_roots="tests scripts")
    del files["src/sample_repo/__init__.py"]
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        '[build-system]\nrequires = ["uv_build>=0.11,<0.12"]\n'
        'build-backend = "uv_build"\n',
        "[tool.uv]\npackage = false\n",
    )
    files["scripts/tool.py"] = UV_SCRIPT
    return files


def aws_files() -> dict[str, str]:
    files = python_files()
    files.update(
        {
            "cdk.json": '{"app": "uv run python -m sample_repo.app"}\n',
            "src/sample_repo/app.py": "app = None\n",
            "Makefile": canonical("Makefile.python").replace(
                "<code-roots>", "src tests"
            )
            + canonical("Makefile.aws"),
        }
    )
    return files


# --- exit codes and base layer ---


def test_not_a_git_repo_exits_two(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    result = run(plain)
    assert result.returncode == 2
    assert "not a git repository" in result.stderr


def test_conforming_base_repo_is_clean(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, base_files())
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert "clean (layers: base)" in result.stderr


def test_missing_base_files_all_reported(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"README.md": "# X\n"})
    result = run(repo)
    assert result.returncode == 1
    for rel in (
        "CLAUDE.md",
        "index.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        "Makefile",
        ".github/workflows/ci.yml",
    ):
        assert f"{rel}  required-file" in result.stdout


def test_ci_yml_must_be_byte_identical(tmp_path: Path) -> None:
    files = base_files()
    files[".github/workflows/ci.yml"] = canonical("ci.yml").replace(
        "SKIP: ref-audit", "SKIP: nothing"
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert ".github/workflows/ci.yml  canonical-bytes" in result.stdout


def test_root_bin_and_tools_forbidden(tmp_path: Path) -> None:
    files = base_files()
    files["bin/run.sh"] = "echo hi\n"
    files["tools/helper.sh"] = "echo hi\n"
    result = run(make_repo(tmp_path, files))
    assert "bin/  forbidden" in result.stdout
    assert "tools/  forbidden" in result.stdout


# --- .gitignore: patterns only ---


def test_gitignore_reordered_with_own_comments_passes(tmp_path: Path) -> None:
    files = base_files()
    patterns = [
        line
        for line in canonical(".gitignore").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    files[".gitignore"] = "# my own comment\nextra-dir/\n" + "\n".join(
        reversed(patterns)
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 0, result.stdout + result.stderr


def test_gitignore_missing_baseline_pattern_fails(tmp_path: Path) -> None:
    files = base_files()
    files[".gitignore"] = canonical(".gitignore").replace(".venv/\n", "")
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "missing baseline pattern '.venv/'" in result.stdout


# --- .pre-commit-config.yaml: canonical blocks ---


def test_any_rev_accepted_on_the_pinned_block(tmp_path: Path) -> None:
    files = base_files()
    files[".pre-commit-config.yaml"] = canonical(".pre-commit-config.yaml").replace(
        "<pinned-sha>", "deadbeefcafe"
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_drifted_ruff_rev_fails(tmp_path: Path) -> None:
    files = base_files()
    files[".pre-commit-config.yaml"] = files[".pre-commit-config.yaml"].replace(
        "rev: v0.15.20", "rev: v0.1.0"
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "canonical-block" in result.stdout
    assert "ruff-pre-commit" in result.stdout


def test_missing_shellcheck_block_fails(tmp_path: Path) -> None:
    files = base_files()
    config = files[".pre-commit-config.yaml"]
    start = config.index("  - repo: https://github.com/shellcheck-py")
    end = config.index("  - repo: local")
    files[".pre-commit-config.yaml"] = config[:start] + config[end:]
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "shellcheck-py" in result.stdout


def test_appended_hook_inside_pinned_block_passes(tmp_path: Path) -> None:
    files = base_files()
    files[".pre-commit-config.yaml"] = files[".pre-commit-config.yaml"].replace(
        "      - id: judgments-lint\n",
        "      - id: judgments-lint\n      - id: internal-skill-audit\n",
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_extra_repo_block_appended_passes(tmp_path: Path) -> None:
    files = base_files()
    files[".pre-commit-config.yaml"] += (
        "  - repo: https://github.com/example/extra\n"
        "    rev: v1.0.0\n"
        "    hooks:\n"
        "      - id: extra-hook\n"
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


# --- doc shape ---


def test_readme_without_h1_fails(tmp_path: Path) -> None:
    files = base_files()
    files["README.md"] = "Just prose, no heading.\n"
    result = run(make_repo(tmp_path, files))
    assert "README.md  doc-shape" in result.stdout


def test_claude_md_missing_standards_block_fails(tmp_path: Path) -> None:
    files = base_files()
    files["CLAUDE.md"] = "## Rules\n\n- be good\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "CLAUDE.md  canonical-block" in result.stdout
    assert "## Standards" in result.stdout


def test_claude_md_drifted_standards_block_fails(tmp_path: Path) -> None:
    files = base_files()
    files["CLAUDE.md"] = files["CLAUDE.md"].replace(
        "navigated by index", "navigated by vibes"
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "CLAUDE.md  canonical-block" in result.stdout


def test_claude_md_prose_around_standards_block_passes(tmp_path: Path) -> None:
    files = base_files()
    files["CLAUDE.md"] += "\n## Rules\n\n- be good\n"
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_context_md_with_all_sections_passes(tmp_path: Path) -> None:
    files = base_files()
    files["CONTEXT.md"] = (
        "# Domain\n\n## Language\n\n## Relationships\n\n"
        "## Example dialogue\n\n## Flagged ambiguities\n"
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_context_md_missing_section_fails(tmp_path: Path) -> None:
    files = base_files()
    files["CONTEXT.md"] = "# Domain\n\n## Language\n\n## Relationships\n"
    result = run(make_repo(tmp_path, files))
    assert "missing section '## Example dialogue'" in result.stdout
    assert "missing section '## Flagged ambiguities'" in result.stdout


def test_nested_context_md_forbidden(tmp_path: Path) -> None:
    files = base_files()
    files["docs/CONTEXT.md"] = "# Nested\n"
    result = run(make_repo(tmp_path, files))
    assert "docs/CONTEXT.md  forbidden" in result.stdout


# --- skills ---


def test_skills_dir_without_audit_hook_fails(tmp_path: Path) -> None:
    files = base_files()
    files[".claude/skills/greet/SKILL.md"] = "---\nname: greet\n---\nhi\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "skills-hook" in result.stdout


def test_skills_dir_with_audit_hook_appended_passes(tmp_path: Path) -> None:
    files = base_files()
    files[".claude/skills/greet/SKILL.md"] = "---\nname: greet\n---\nhi\n"
    files[".pre-commit-config.yaml"] = files[".pre-commit-config.yaml"].replace(
        "      - id: judgments-lint\n",
        "      - id: judgments-lint\n      - id: internal-skill-audit\n",
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


# --- python layer ---


def test_conforming_python_repo_is_clean(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, python_files())
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "layers: base, python, src" in result.stderr


def test_python_repo_missing_lock_version_tests(tmp_path: Path) -> None:
    files = python_files()
    del files["uv.lock"]
    del files[".python-version"]
    del files["tests/test_sample.py"]
    result = run(make_repo(tmp_path, files))
    assert "uv.lock  required-file" in result.stdout
    assert ".python-version  required-file" in result.stdout
    assert "tests/  required-file" in result.stdout


def test_python_version_must_match_canonical_pin(tmp_path: Path) -> None:
    files = python_files()
    files[".python-version"] = "3.12\n"
    result = run(make_repo(tmp_path, files))
    assert ".python-version  canonical-bytes" in result.stdout


def test_requirements_txt_forbidden_anywhere(tmp_path: Path) -> None:
    files = python_files()
    files["docs/requirements.txt"] = "flask\n"
    result = run(make_repo(tmp_path, files))
    assert "docs/requirements.txt  forbidden" in result.stdout


def test_nested_pyproject_forbidden(tmp_path: Path) -> None:
    files = python_files()
    files["sub/pyproject.toml"] = "[project]\nname = 'sub'\n"
    result = run(make_repo(tmp_path, files))
    assert "sub/pyproject.toml  forbidden" in result.stdout


def test_project_name_must_follow_mapping(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        'name = "sample-repo"', 'name = "other-name"'
    )
    result = run(make_repo(tmp_path, files))
    assert "project.name must be 'sample-repo'" in result.stdout


def test_src_package_must_match_mapping(tmp_path: Path) -> None:
    files = python_files()
    del files["src/sample_repo/__init__.py"]
    files["src/wrongpkg/__init__.py"] = ""
    result = run(make_repo(tmp_path, files))
    assert "src/wrongpkg  name-mapping" in result.stdout
    assert "src/sample_repo/  name-mapping" in result.stdout


def test_second_src_package_flagged(tmp_path: Path) -> None:
    files = python_files()
    files["src/extra_pkg/__init__.py"] = ""
    result = run(make_repo(tmp_path, files))
    assert "src/extra_pkg  name-mapping" in result.stdout


def test_extra_dev_dependency_allowed_missing_floor_fails(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        '    "ruff>=0.15.20",\n', '    "types-pyyaml>=6.0",\n'
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "dependency-groups.dev must contain 'ruff>=0.15.20'" in result.stdout
    assert "types-pyyaml" not in result.stdout


def test_pinned_ruff_selection_enforced(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        'select = ["E", "W", "F", "I", "UP", "B", "SIM", "SLF"]',
        'select = ["E", "F"]',
    )
    result = run(make_repo(tmp_path, files))
    assert "tool.ruff.lint.select" in result.stdout


def test_missing_mypy_strictness_key_fails(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        "disallow_untyped_defs = true\n", ""
    )
    result = run(make_repo(tmp_path, files))
    assert "tool.mypy.disallow_untyped_defs must be True, got None" in result.stdout


def test_additions_to_pyproject_are_free(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] += (
        '\n[project.scripts]\nsample = "sample_repo.cli:main"\n'
        '\n[tool.ruff.lint.per-file-ignores]\n"tests/*" = ["SLF"]\n'
    )
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_scripts_only_repo_shape(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, scripts_only_files(), executable=("scripts/tool.py",))
    result = run(repo)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "layers: base, python, scripts" in result.stderr


def test_scripts_only_repo_with_build_system_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        "[tool.uv]\npackage = false\n",
        '[build-system]\nrequires = ["uv_build>=0.11,<0.12"]\n'
        'build-backend = "uv_build"\n',
    )
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "omits [build-system]" in result.stdout
    assert "tool.uv.package must be False" in result.stdout


def test_src_repo_missing_build_system_fails(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        '[build-system]\nrequires = ["uv_build>=0.11,<0.12"]\n'
        'build-backend = "uv_build"\n',
        "",
    )
    result = run(make_repo(tmp_path, files))
    assert "build-system.requires" in result.stdout


# --- Makefile ---


def test_makefile_wrong_mypy_roots_fails(tmp_path: Path) -> None:
    files = python_files(code_roots="src")
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "Makefile  canonical-block" in result.stdout
    assert "Makefile.python" in result.stdout


def test_makefile_extra_targets_allowed(tmp_path: Path) -> None:
    files = python_files()
    files["Makefile"] += "\n.PHONY: docs\ndocs:\n\techo docs\n"
    assert run(make_repo(tmp_path, files)).returncode == 0


# --- scripts layer ---


def test_executable_script_with_plain_shebang_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/tool.py"] = "#!/usr/bin/env python3\nprint('hi')\n"
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "scripts/tool.py  script-shebang" in result.stdout


def test_executable_script_without_pep723_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/tool.py"] = "#!/usr/bin/env -S uv run --script\nprint('hi')\n"
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "PEP 723" in result.stdout


def test_script_python_floor_mismatch_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/tool.py"] = UV_SCRIPT.replace('">=3.14"', '">=3.11"')
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "scripts/tool.py  script-python" in result.stdout
    assert '">=3.14"' in result.stdout


def test_script_python_floor_missing_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/tool.py"] = UV_SCRIPT.replace('# requires-python = ">=3.14"\n', "")
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "scripts/tool.py  script-python" in result.stdout


def test_makefile_roots_require_real_py_files(tmp_path: Path) -> None:
    # scripts/ holding only extensionless executables earns no <code-roots>
    # slot — mypy exits 2 on a directory without .py files.
    files = scripts_only_files()
    del files["scripts/tool.py"]
    files["scripts/tool"] = UV_SCRIPT
    files["Makefile"] = canonical("Makefile.python").replace("<code-roots>", "tests")
    result = run(make_repo(tmp_path, files, executable=("scripts/tool",)))
    assert result.returncode == 0, result.stdout + result.stderr


def test_non_executable_helper_module_not_checked(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/helper.py"] = "X = 1\n"
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 0, result.stdout + result.stderr


# --- aws layer ---


def test_conforming_aws_repo_is_clean(tmp_path: Path) -> None:
    result = run(make_repo(tmp_path, aws_files()))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "layers: base, python, src, aws" in result.stderr


def test_cdk_app_command_enforced(tmp_path: Path) -> None:
    files = aws_files()
    files["cdk.json"] = '{"app": "python3 app.py"}\n'
    result = run(make_repo(tmp_path, files))
    assert "cdk.json  canonical-value" in result.stdout
    assert "uv run python -m sample_repo.app" in result.stdout


def test_root_app_py_forbidden_and_entry_required(tmp_path: Path) -> None:
    files = aws_files()
    del files["src/sample_repo/app.py"]
    files["app.py"] = "app = None\n"
    result = run(make_repo(tmp_path, files))
    assert "app.py  forbidden" in result.stdout
    assert "src/sample_repo/app.py  required-file" in result.stdout


def test_aws_without_src_flagged(tmp_path: Path) -> None:
    files = base_files()
    files["cdk.json"] = '{"app": "uv run python -m sample_repo.app"}\n'
    result = run(make_repo(tmp_path, files))
    assert "cdk.json  layer-shape" in result.stdout


def test_tracked_cdk_out_forbidden(tmp_path: Path) -> None:
    files = aws_files()
    files["cdk.out/manifest.json"] = "{}\n"
    result = run(make_repo(tmp_path, files))
    assert "cdk.out/  forbidden" in result.stdout


def test_makefile_missing_aws_targets_fails(tmp_path: Path) -> None:
    files = aws_files()
    files["Makefile"] = canonical("Makefile.python").replace(
        "<code-roots>", "src tests"
    )
    result = run(make_repo(tmp_path, files))
    assert "Makefile.aws" in result.stdout


# --- js layer ---


def test_package_json_requires_committed_lockfile(tmp_path: Path) -> None:
    files = base_files()
    files["package.json"] = '{"name": "sample"}\n'
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "package.json  required-file" in result.stdout

    files["package-lock.json"] = "{}\n"
    result = run(make_repo(tmp_path, files, name="locked-repo"))
    assert result.returncode == 0, result.stdout + result.stderr


# --- hook-repo self-audit ---


def hook_repo_files() -> dict[str, str]:
    files = base_files()
    config = files[".pre-commit-config.yaml"]
    start = config.index("  - repo: https://github.com/GeoffNordling/dev-playbook")
    end = config.index("  - repo: https://github.com/astral-sh/ruff-pre-commit")
    files[".pre-commit-config.yaml"] = (
        config[:start]
        + config[end:]
        + "  - repo: local\n    hooks:\n"
        + "".join(f"      - id: {h}\n" for h in ("repo-audit", "okf-audit"))
    )
    files[".pre-commit-hooks.yaml"] = "- id: repo-audit\n- id: okf-audit\n"
    # is_file(): tools that treat the canonical pyproject.toml template as a
    # real project drop cache dirs (e.g. .ruff_cache/) into standards/build/canonical/.
    for name in CANONICAL.iterdir():
        if name.is_file():
            files[f"standards/build/canonical/{name.name}"] = name.read_text()
    return files


def test_hook_repo_dogfood_mirror_passes(tmp_path: Path) -> None:
    result = run(make_repo(tmp_path, hook_repo_files()))
    assert result.returncode == 0, result.stdout + result.stderr


def test_hook_repo_dogfood_drift_fails(tmp_path: Path) -> None:
    files = hook_repo_files()
    files[".pre-commit-hooks.yaml"] += "- id: brand-new-hook\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "self-audit" in result.stdout
    assert "missing: brand-new-hook" in result.stdout


def test_hook_repo_unknown_canonical_artifact_fails(tmp_path: Path) -> None:
    files = hook_repo_files()
    files["standards/build/canonical/mystery.cfg"] = "x\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "standards/build/canonical/mystery.cfg  self-audit" in result.stdout


def test_canonical_dir_exempt_from_tree_rules(tmp_path: Path) -> None:
    # hook_repo_files copies the canonical pyproject.toml template into
    # standards/build/canonical/ — it must not trip the one-pyproject rule.
    result = run(make_repo(tmp_path, hook_repo_files()))
    assert "standards/build/canonical/pyproject.toml" not in result.stdout

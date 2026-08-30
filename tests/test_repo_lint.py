"""Behavioral tests for scripts/repo-lint.

Every fixture is a git repo (discovery and the repo-name mapping both go
through git) with all files staged, since "committed" requirements read the
index. Fixtures copy the real canonical artifacts from standards/build/canonical/,
so these tests also pin that the canonical files themselves stay auditable.
"""

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "repo-lint"
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
    symlinks: tuple[tuple[str, str], ...] = (),
) -> Path:
    repo = tmp_path / name
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for rel in executable:
        os.chmod(repo / rel, 0o755)
    for rel, target in symlinks:
        link = repo / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True
    )
    return repo


def base_files() -> dict[str, str]:
    return {
        "README.md": "# Sample Repo\n\nOne line of purpose.\n",
        "CLAUDE.md": "# Sample Repo\n",
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
        assert f"{rel}: build.required-file" in result.stdout


def test_ci_yml_must_be_byte_identical(tmp_path: Path) -> None:
    files = base_files()
    files[".github/workflows/ci.yml"] = canonical("ci.yml").replace(
        "SKIP: ref-lint", "SKIP: nothing"
    )
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert ".github/workflows/ci.yml: build.canonical-bytes" in result.stdout


def test_root_bin_and_tools_forbidden(tmp_path: Path) -> None:
    files = base_files()
    files["bin/run.sh"] = "echo hi\n"
    files["tools/helper.sh"] = "echo hi\n"
    result = run(make_repo(tmp_path, files))
    assert "bin/: build.forbidden" in result.stdout
    assert "tools/: build.forbidden" in result.stdout


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
        "      - id: validate-manifest\n",
        "      - id: validate-manifest\n      - id: extra-lint\n",
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
    assert "README.md: knowledge-organization.doc-shape" in result.stdout


def test_repo_claude_md_content_is_free(tmp_path: Path) -> None:
    # A repo's own CLAUDE.md carries whatever that repo needs and nothing is
    # mandated: the workspace-wide rules live in the global file.
    files = base_files()
    files["CLAUDE.md"] = "# Sample Repo\n\n## Rules\n\n- be good\n"
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_repo_claude_md_bare_heading_passes(tmp_path: Path) -> None:
    # A repo with nothing repo-specific to say has nothing to write.
    files = base_files()
    files["CLAUDE.md"] = "# Sample Repo\n"
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_context_md_with_language_passes(tmp_path: Path) -> None:
    files = base_files()
    files["CONTEXT.md"] = "# Domain\n\n## Language\n\n**Order**:\nA request.\n"
    assert run(make_repo(tmp_path, files)).returncode == 0


def test_context_md_missing_language_fails(tmp_path: Path) -> None:
    files = base_files()
    files["CONTEXT.md"] = "# Domain\n\nTerms for the domain.\n"
    result = run(make_repo(tmp_path, files))
    assert "missing section '## Language'" in result.stdout


def test_nested_context_md_forbidden(tmp_path: Path) -> None:
    files = base_files()
    files["docs/CONTEXT.md"] = "# Nested\n"
    result = run(make_repo(tmp_path, files))
    assert "docs/CONTEXT.md: build.forbidden" in result.stdout


def test_rogue_future_work_files_forbidden_anywhere(tmp_path: Path) -> None:
    files = base_files()
    for name in ("ROADMAP.md", "TODO.md", "BACKLOG.md", "IDEAS.md"):
        files[f"docs/{name}"] = "# Later\n\n- ship the thing\n"
    files["TODO.md"] = "# Later\n\n- ship the thing\n"
    result = run(make_repo(tmp_path, files))
    for name in ("ROADMAP.md", "TODO.md", "BACKLOG.md", "IDEAS.md"):
        assert f"docs/{name}: tracking.rogue-future-work-file" in result.stdout
    assert "TODO.md: tracking.rogue-future-work-file" in result.stdout


def test_root_candidates_md_is_allowed(tmp_path: Path) -> None:
    files = base_files()
    files["CANDIDATES.md"] = (
        "---\ntype: Candidate-List\ntitle: Candidates\n"
        "description: Uncommitted future work\n---\n\n# Candidates\n\n"
        "- **Fuzzy matching** — matching is exact-prefix only today.\n"
    )
    result = run(make_repo(tmp_path, files))
    assert "CANDIDATES.md" not in result.stdout


def test_nested_candidates_md_forbidden(tmp_path: Path) -> None:
    files = base_files()
    files["docs/CANDIDATES.md"] = "# Nested\n"
    result = run(make_repo(tmp_path, files))
    assert "docs/CANDIDATES.md: build.forbidden" in result.stdout


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
    assert "uv.lock: build.required-file" in result.stdout
    assert ".python-version: build.required-file" in result.stdout
    assert "tests/: build.required-file" in result.stdout


def test_python_version_must_match_canonical_pin(tmp_path: Path) -> None:
    files = python_files()
    files[".python-version"] = "3.12\n"
    result = run(make_repo(tmp_path, files))
    assert ".python-version: build.canonical-bytes" in result.stdout


def test_requirements_txt_forbidden_anywhere(tmp_path: Path) -> None:
    files = python_files()
    files["docs/requirements.txt"] = "flask\n"
    result = run(make_repo(tmp_path, files))
    assert "docs/requirements.txt: build.forbidden" in result.stdout


def test_nested_pyproject_forbidden(tmp_path: Path) -> None:
    files = python_files()
    files["sub/pyproject.toml"] = "[project]\nname = 'sub'\n"
    result = run(make_repo(tmp_path, files))
    assert "sub/pyproject.toml: build.forbidden" in result.stdout


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
    assert "src/wrongpkg: build.name-mapping" in result.stdout
    assert "src/sample_repo/: build.name-mapping" in result.stdout


def test_second_src_package_flagged(tmp_path: Path) -> None:
    files = python_files()
    files["src/extra_pkg/__init__.py"] = ""
    result = run(make_repo(tmp_path, files))
    assert "src/extra_pkg: build.name-mapping" in result.stdout


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
        'select = ["E", "W", "F", "I", "UP", "B", "SIM", "SLF", "D"]',
        'select = ["E", "F"]',
    )
    result = run(make_repo(tmp_path, files))
    assert "tool.ruff.lint.select" in result.stdout


def test_pinned_pydocstyle_convention_enforced(tmp_path: Path) -> None:
    files = python_files()
    files["pyproject.toml"] = files["pyproject.toml"].replace(
        'convention = "pep257"',
        'convention = "google"',
    )
    result = run(make_repo(tmp_path, files))
    assert "tool.ruff.lint.pydocstyle.convention" in result.stdout


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
        "\n[tool.ruff.lint.mccabe]\nmax-complexity = 10\n"
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
    assert "Makefile: build.canonical-block" in result.stdout
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
    assert "scripts/tool.py: build.script-shebang" in result.stdout


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
    assert "scripts/tool.py: build.script-python" in result.stdout
    assert '">=3.14"' in result.stdout


def test_script_python_floor_missing_fails(tmp_path: Path) -> None:
    files = scripts_only_files()
    files["scripts/tool.py"] = UV_SCRIPT.replace('# requires-python = ">=3.14"\n', "")
    result = run(make_repo(tmp_path, files, executable=("scripts/tool.py",)))
    assert result.returncode == 1
    assert "scripts/tool.py: build.script-python" in result.stdout


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


# --- js layer ---


def test_package_json_requires_committed_lockfile(tmp_path: Path) -> None:
    files = base_files()
    files["package.json"] = '{"name": "sample"}\n'
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert "package.json: build.required-file" in result.stdout

    files["package-lock.json"] = "{}\n"
    result = run(make_repo(tmp_path, files, name="locked-repo"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_js_src_is_not_the_python_src_layer(tmp_path: Path) -> None:
    files = base_files()
    files["package.json"] = '{"name": "sample"}\n'
    files["package-lock.json"] = "{}\n"
    files["src/pages/index.astro"] = "<h1>hello</h1>\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "layers: base, js" in result.stderr


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
        + "".join(f"      - id: {h}\n" for h in ("repo-lint", "okf-lint"))
    )
    files[".pre-commit-hooks.yaml"] = "- id: repo-lint\n- id: okf-lint\n"
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
    assert "standards/build/canonical/mystery.cfg: build.self-audit" in result.stdout


def manifest_only_files() -> dict[str, str]:
    # A consumer that also hosts a hook manifest: it carries the pinned
    # dev-playbook block AND dogfoods what it publishes, but has no
    # standards/build/canonical/ directory (that is dev-playbook's alone).
    files = base_files()
    files[".pre-commit-hooks.yaml"] = "- id: acme-lint\n"
    files[".pre-commit-config.yaml"] += "      - id: acme-lint\n"
    return files


def test_manifest_without_canonical_dir_is_clean(tmp_path: Path) -> None:
    result = run(make_repo(tmp_path, manifest_only_files()))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "canonical artifact missing" not in result.stdout


def test_manifest_without_canonical_dir_still_requires_pinned_block(
    tmp_path: Path,
) -> None:
    files = manifest_only_files()
    config = files[".pre-commit-config.yaml"]
    start = config.index("  - repo: https://github.com/GeoffNordling/dev-playbook")
    end = config.index("  - repo: https://github.com/astral-sh/ruff-pre-commit")
    files[".pre-commit-config.yaml"] = config[:start] + config[end:]
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert ".pre-commit-config.yaml: build.canonical-block" in result.stdout


def test_manifest_without_canonical_dir_enforces_dogfood_mirror(
    tmp_path: Path,
) -> None:
    files = manifest_only_files()
    files[".pre-commit-hooks.yaml"] += "- id: unmirrored-lint\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 1
    assert ".pre-commit-config.yaml: build.self-audit" in result.stdout
    assert "missing: unmirrored-lint" in result.stdout


def test_list_rules_prints_card_prefixed_ids_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--list-rules"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ids = set(result.stdout.split())
    assert "build.required-file" in ids
    assert "build.canonical-block" in ids
    assert "knowledge-organization.doc-shape" in ids
    assert "tracking.rogue-future-work-file" in ids
    # No harness.* here: the voice rule is prose-lint's and the global CLAUDE.md
    # shape is harness-files-lint's. repo-lint checks that CLAUDE.md exists,
    # which is build.required-file, and nothing about what it says.
    assert all(
        rule.split(".")[0] in {"build", "knowledge-organization", "tracking"}
        for rule in ids
    ), ids


def test_finding_line_is_gnu_format(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"README.md": "# X\n"})
    result = run(repo)
    assert result.returncode == 1
    assert "CLAUDE.md: build.required-file " in result.stdout


def test_global_claude_source_is_not_this_detectors_business(tmp_path: Path) -> None:
    # The global file's shape moved to harness-files-lint; a misshapen one draws
    # nothing here, and the file's mere presence trips no build rule either.
    files = base_files()
    files["dotfiles/dot-claude/CLAUDE.md"] = "# Global\n\n## Extras\n\nNope.\n"
    result = run(make_repo(tmp_path, files))
    assert result.returncode == 0, result.stdout + result.stderr


def test_canonical_dir_exempt_from_tree_rules(tmp_path: Path) -> None:
    # hook_repo_files copies the canonical pyproject.toml template into
    # standards/build/canonical/ — it must not trip the one-pyproject rule.
    result = run(make_repo(tmp_path, hook_repo_files()))
    assert "standards/build/canonical/pyproject.toml" not in result.stdout

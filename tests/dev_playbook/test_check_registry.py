"""Unit tests for the check registry, and the meta-test over every registered check."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from dev_playbook import check_registry
from dev_playbook.check_registry import WORKSPACE, Check, Finding
from dev_playbook.model import Repo


def a_function(repo: Repo) -> Iterator[Finding]:
    yield from ()


a_function.__module__ = "dev_playbook.checks.fam"


class TestRegistration:
    def test_check_writes_one_entry(self) -> None:
        reg: dict[str, Check] = {}
        assert check_registry.check("fam.one", registry=reg)(a_function) is a_function
        assert reg["fam.one"].function is a_function
        assert reg["fam.one"].hook is None
        assert reg["fam.one"].needs == frozenset()

    def test_needs_tags_the_entry(self) -> None:
        reg: dict[str, Check] = {}
        check_registry.check("fam.one", needs=[WORKSPACE], registry=reg)(a_function)
        assert reg["fam.one"].needs == frozenset({WORKSPACE})

    def test_tool_check_holds_the_hook_name(self) -> None:
        reg: dict[str, Check] = {}
        check_registry.tool_check(
            "fam.two", hook="shellcheck", module="dev_playbook.checks.fam", registry=reg
        )
        assert reg["fam.two"].function is None
        assert reg["fam.two"].hook == "shellcheck"

    def test_duplicate_id_raises(self) -> None:
        reg: dict[str, Check] = {}
        check_registry.check("fam.one", registry=reg)(a_function)
        with pytest.raises(check_registry.RegistryError, match="registered twice"):
            check_registry.check("fam.one", registry=reg)(a_function)

    def test_module_must_be_named_for_the_family(self) -> None:
        reg: dict[str, Check] = {}
        with pytest.raises(check_registry.RegistryError, match="not other"):
            check_registry.check("other.one", registry=reg)(a_function)

    def test_hyphenated_family_registers_from_underscored_module(self) -> None:
        reg: dict[str, Check] = {}
        check_registry.tool_check(
            "doc-type.one",
            hook="h",
            module="dev_playbook.checks.doc_type",
            registry=reg,
        )
        assert reg["doc-type.one"].family == "doc-type"
        assert check_registry.module_name("knowledge-organization") == (
            "knowledge_organization"
        )

    @pytest.mark.parametrize("bad", ["noslug", "Fam.x", "fam.x_y", "fam."])
    def test_bad_id_raises(self, bad: str) -> None:
        reg: dict[str, Check] = {}
        with pytest.raises(check_registry.RegistryError, match="not <family>.<slug>"):
            check_registry.add(
                Check(bad, None, "h", frozenset(), "dev_playbook.checks.fam"), reg
            )

    def test_family_and_slug(self) -> None:
        entry = Check("fam.a-b", None, "h", frozenset(), "m.fam")
        assert (entry.family, entry.slug) == ("fam", "a-b")


@pytest.fixture(scope="module")
def registered() -> dict[str, Check]:
    return check_registry.load()


class TestEveryRegisteredCheck:
    def test_load_is_idempotent(self, registered: dict[str, Check]) -> None:
        assert check_registry.load() is registered

    def test_has_a_function_or_a_hook_never_both(
        self, registered: dict[str, Check]
    ) -> None:
        for entry in registered.values():
            assert (entry.function is None) != (entry.hook is None), entry.id

    def test_matches_the_standards_and_the_tests(
        self, registered: dict[str, Check], dev_playbook_repo: Repo
    ) -> None:
        # Each check is a deterministic rule of its family with its test, and
        # each deterministic rule under standards/ has a check.
        assert check_registry.layer_problems(registered, dev_playbook_repo) == []


RULES = """\
# Fam

## One

A predicate.

`fam.one` · deterministic

## Two

A predicate.

`fam.two` · stochastic
"""

FAM = """\
from dev_playbook.check_registry import check


@check("fam.one")
def one(repo):
    yield from ()
"""


def a_consumer(files: dict[str, str]) -> Repo:
    """A consumer repo whose import package is ``a_consumer``."""
    files = {"pyproject.toml": '[project]\nname = "a-consumer"\n'} | files
    return Repo.from_files(
        Path("/r"), {path: text.encode() for path, text in files.items()}
    )


class TestRepoLayer:
    def test_runs_the_repo_checks_into_their_own_layer(self) -> None:
        repo = a_consumer(
            {"src/a_consumer/checks/fam.py": FAM, "src/a_consumer/fam.py": FAM}
        )
        registry = check_registry.load(repo)
        assert registry["fam.one"].module == "a_consumer.checks.fam"
        assert "fam.one" not in check_registry.CHECKS
        assert registry.keys() - check_registry.CHECKS.keys() == {"fam.one"}

    def test_a_second_load_runs_the_modules_again(self) -> None:
        repo = a_consumer({"src/a_consumer/checks/fam.py": FAM})
        assert "fam.one" in check_registry.load(repo)
        assert "fam.one" in check_registry.load(repo)

    def test_dev_playbook_hosts_no_second_layer(self, dev_playbook_repo: Repo) -> None:
        assert check_registry.load(dev_playbook_repo) == check_registry.CHECKS

    def test_an_id_both_layers_register_raises(self) -> None:
        shadow = FAM.replace("fam.one", "standard.no-shadowing")
        repo = a_consumer({"src/a_consumer/checks/standard.py": shadow})
        with pytest.raises(check_registry.RegistryError, match="by dev-playbook"):
            check_registry.load(repo)


class TestLayerProblems:
    def problems(self, files: dict[str, str]) -> list[str]:
        repo = a_consumer(files)
        return check_registry.layer_problems(check_registry.load(repo), repo)

    def test_a_matching_layer_has_none(self) -> None:
        files = {
            "standards/fam/rules.md": RULES,
            "src/a_consumer/checks/fam.py": FAM,
            "tests/a_consumer/checks/test_fam.py": "def test_one():\n    pass\n",
        }
        assert self.problems(files) == []

    def test_each_mismatch_is_named(self) -> None:
        other = RULES.replace("## One", "## Uno").replace("fam.two", "fam.three")
        files = {
            "standards/fam/rules.md": other,
            "standards/other/rules.md": "## Four\n\nP.\n\n`fam.four` · deterministic\n",
            "src/a_consumer/checks/fam.py": FAM
            + '\n\n@check("fam.three")\ndef three(repo):\n    yield from ()\n'
            + '\n\n@check("fam.five")\ndef five(repo):\n    yield from ()\n',
        }
        tests = "tests/a_consumer/checks/test_fam.py"
        assert self.problems(files) == [
            "fam.five: no rule under standards/ has this id",
            "fam.one: the rule's heading in standards/fam/rules.md is not one",
            f"fam.one: no test_one in {tests}",
            "fam.three: the rule in standards/fam/rules.md is stochastic",
            "fam.three: the rule's heading in standards/fam/rules.md is not three",
            f"fam.three: no test_three in {tests}",
            "fam.four: the rule in standards/other/rules.md has no check",
        ]

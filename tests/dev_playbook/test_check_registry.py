"""Unit tests for the check registry, and the meta-test over every registered check."""

import ast
from collections.abc import Iterator
from pathlib import Path

import pytest

from dev_playbook import check_registry
from dev_playbook.check_registry import WORKSPACE, Check, Finding
from dev_playbook.model import Repo, Trailer

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_TESTS = REPO_ROOT / "tests" / "dev_playbook" / "checks"


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


def standards_trailers(repo: Repo) -> dict[str, tuple[str, Trailer]]:
    """Every rule trailer under standards/, by id, with the file it is in."""
    return {
        t.id: (path, t)
        for path, doc in repo.markdown.items()
        if path.startswith("standards/")
        for t in doc.trailers
    }


def collected_test_names(path: Path) -> set[str]:
    """Every test function name in a test file, at module level or in a class."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            names.add(node.name)
    return names


class TestEveryRegisteredCheck:
    def test_load_is_idempotent(self, registered: dict[str, Check]) -> None:
        assert check_registry.load() is registered

    def test_is_a_deterministic_rule_heading_of_its_family(
        self, registered: dict[str, Check], dev_playbook_repo: Repo
    ) -> None:
        trailers = standards_trailers(dev_playbook_repo)
        for entry in registered.values():
            assert entry.id in trailers, f"{entry.id}: no trailer under standards/"
            path, trailer = trailers[entry.id]
            assert trailer.kind == "deterministic", entry.id
            assert trailer.heading is not None, entry.id
            assert trailer.heading.slug == entry.slug, entry.id
            assert path.split("/")[1] == entry.family, f"{entry.id} in {path}"

    def test_has_a_function_or_a_hook_never_both(
        self, registered: dict[str, Check]
    ) -> None:
        for entry in registered.values():
            assert (entry.function is None) != (entry.hook is None), entry.id

    def test_every_function_has_a_test(self, registered: dict[str, Check]) -> None:
        missing = []
        for entry in registered.values():
            if entry.function is None:
                continue
            test_file = CHECK_TESTS / f"test_{entry.family}.py"
            name = "test_" + entry.slug.replace("-", "_")
            if not test_file.is_file() or name not in collected_test_names(test_file):
                missing.append(f"{entry.id}: {test_file.name}::{name}")
        assert missing == []

    @pytest.mark.xfail(
        strict=True,
        reason="until cut over: the old scripts still decide the unported rules",
    )
    def test_every_deterministic_rule_is_registered(
        self, registered: dict[str, Check], dev_playbook_repo: Repo
    ) -> None:
        unregistered = sorted(
            t.id
            for _, t in standards_trailers(dev_playbook_repo).values()
            if t.kind == "deterministic" and t.id not in registered
        )
        assert unregistered == []

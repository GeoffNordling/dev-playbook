"""Behavioral tests for the judgments loader: root resolution, discovery, validation."""

from collections.abc import Callable
from pathlib import Path

import pytest

from dev_playbook.judgments.loader import Declaration, by_id, load, resolve_root

CONFIG = '[tool.judgments]\npaths = ["judgments/*.yaml"]\n'

_OMIT = object()

_DEFAULTS = {
    "id": "j1",
    "claim": "docs/errors.md lists every exception type.",
    "evidence": "[docs/errors.md]",
    "reference": "[src/exceptions.py]",
    "model": "claude-sonnet-4-6",
    "effort": "high",
}


def declaration_yaml(**overrides: object) -> str:
    """Render a one-judgment declaration YAML.

    Each field is rendered verbatim as ``key: value`` (so a test controls the
    exact YAML scalar); pass ``_OMIT`` to leave a field out entirely.
    """
    fields = {**_DEFAULTS, **overrides}
    rendered = [(k, v) for k, v in fields.items() if v is not _OMIT]
    lines = ["judgments:"]
    for index, (key, value) in enumerate(rendered):
        prefix = "  - " if index == 0 else "    "
        lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines) + "\n"


def test_resolve_root_finds_nearest_ancestor_with_tool_judgments(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo({"pyproject.toml": CONFIG, "sub/deep/.keep": ""})

    found = resolve_root(start=repo / "sub" / "deep")

    assert found == repo


def test_resolve_root_returns_none_when_no_config_in_any_ancestor(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo({"pyproject.toml": "[project]\nname = 'x'\n", "sub/.keep": ""})

    found = resolve_root(start=repo / "sub")

    assert found is None


def test_load_returns_empty_when_root_is_none() -> None:
    assert load(None) == []


def test_load_parses_a_valid_declaration(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo({"pyproject.toml": CONFIG, "judgments/a.yaml": declaration_yaml()})

    declarations = load(repo)

    assert declarations == [
        Declaration(
            id="j1",
            claim="docs/errors.md lists every exception type.",
            evidence=["docs/errors.md"],
            reference=["src/exceptions.py"],
            model="claude-sonnet-4-6",
            effort="high",
        )
    ]


def test_load_normalizes_omitted_reference_to_empty_list(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(reference=_OMIT),
        }
    )

    declarations = load(repo)

    assert declarations[0].reference == []


@pytest.mark.parametrize("field", ["id", "claim", "evidence", "model", "effort"])
def test_load_rejects_a_missing_required_field(
    make_repo: Callable[[dict[str, str]], Path], field: str
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(**{field: _OMIT}),
        }
    )

    with pytest.raises(ValueError, match=field):
        load(repo)


def test_load_rejects_an_id_with_illegal_characters(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(id='"bad id!"'),
        }
    )

    with pytest.raises(ValueError, match="bad id!"):
        load(repo)


def test_load_rejects_an_empty_claim(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": declaration_yaml(claim='""')}
    )

    with pytest.raises(ValueError, match="claim"):
        load(repo)


def test_load_rejects_empty_evidence(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": declaration_yaml(evidence="[]")}
    )

    with pytest.raises(ValueError, match="evidence"):
        load(repo)


def test_load_rejects_a_model_outside_valid_models(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {"pyproject.toml": CONFIG, "judgments/a.yaml": declaration_yaml(model="gpt-4")}
    )

    with pytest.raises(ValueError, match="model"):
        load(repo)


def test_load_rejects_an_effort_outside_valid_efforts(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(effort="turbo"),
        }
    )

    with pytest.raises(ValueError, match="effort"):
        load(repo)


def test_load_rejects_a_duplicate_id_across_files(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(id="dup"),
            "judgments/b.yaml": declaration_yaml(id="dup"),
        }
    )

    with pytest.raises(ValueError, match="dup"):
        load(repo)


def test_load_does_no_io_on_declared_evidence_paths(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    # evidence names a file that does not exist; load must still succeed because
    # existence is the lint's and prepare's job, not the loader's.
    repo = make_repo(
        {
            "pyproject.toml": CONFIG,
            "judgments/a.yaml": declaration_yaml(evidence="[does/not/exist.md]"),
        }
    )

    declarations = load(repo)

    assert declarations[0].evidence == ["does/not/exist.md"]


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("judgments:\n", "must be a list"),  # key present, null value
        ("judgments: 5\n", "must be a list"),  # scalar, not a list
        ("- a\n", "mapping"),  # top-level list, not a mapping
    ],
)
def test_load_rejects_a_malformed_judgments_shape(
    make_repo: Callable[[dict[str, str]], Path], content: str, expected: str
) -> None:
    # A structurally-malformed declaration file must raise the loader's clear,
    # file-named ValueError -- not a raw TypeError/AttributeError that escapes the
    # lint's and CLI's error handling and dumps a traceback.
    repo = make_repo({"pyproject.toml": CONFIG, "judgments/a.yaml": content})

    with pytest.raises(ValueError, match=expected):
        load(repo)


def test_load_rejects_tool_judgments_table_with_no_paths(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo({"pyproject.toml": "[tool.judgments]\n"})

    with pytest.raises(ValueError, match="paths"):
        load(repo)


def test_load_rejects_tool_judgments_table_with_empty_paths(
    make_repo: Callable[[dict[str, str]], Path],
) -> None:
    repo = make_repo({"pyproject.toml": "[tool.judgments]\npaths = []\n"})

    with pytest.raises(ValueError, match="paths"):
        load(repo)


def test_by_id_returns_the_matching_declaration() -> None:
    declarations = [
        Declaration("a", "c", ["e"], [], "claude-opus-4-8", "low"),
        Declaration("b", "c", ["e"], [], "claude-opus-4-8", "low"),
    ]

    assert by_id(declarations, "b").id == "b"


def test_by_id_raises_on_unknown_id() -> None:
    declarations = [Declaration("a", "c", ["e"], [], "claude-opus-4-8", "low")]

    with pytest.raises(ValueError, match="nope"):
        by_id(declarations, "nope")

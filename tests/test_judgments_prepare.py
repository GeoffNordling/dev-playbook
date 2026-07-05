"""prepare(): single-read derivation of the content key and the judge prompt."""

from pathlib import Path

import pytest

from dev_playbook.judgments.core import PROMPT, Prepared, prepare


def write(root: Path, rel: str, text: str) -> None:
    """Create a file at root/rel with the given text, making parents as needed."""
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def _forbidden_read(self: Path) -> bytes:
    """Stand in for Path.read_bytes to assert no file is read; fails if called."""
    raise AssertionError(f"must not read {self}")


# --- shape of the result ---------------------------------------------------


def test_prepare_returns_a_hex_key_and_a_prompt(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")

    out = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert isinstance(out, Prepared)
    assert len(out.key) == 64
    assert all(ch in "0123456789abcdef" for ch in out.key)
    assert isinstance(out.prompt, str)


# --- prompt rendering ------------------------------------------------------


def test_prompt_wraps_instructions_claim_and_evidence(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")

    out = prepare(
        claim="the claim",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert out.prompt == (
        f"<instructions>\n{PROMPT}\n</instructions>\n\n"
        "<claim>\nthe claim\n</claim>\n\n"
        '<evidence path="docs/a.md">\nALPHA\n</evidence>'
    )


def test_prompt_appends_reference_after_evidence(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")
    write(tmp_path, "src/x.py", "CODE")

    out = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=["src/x.py"],
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert out.prompt == (
        f"<instructions>\n{PROMPT}\n</instructions>\n\n"
        "<claim>\nc\n</claim>\n\n"
        '<evidence path="docs/a.md">\nALPHA\n</evidence>\n\n'
        '<reference path="src/x.py">\nCODE\n</reference>'
    )


def test_prompt_omits_reference_tag_when_reference_is_none(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")

    out = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    # PROMPT itself mentions "<reference>" in prose, so check for a rendered tag.
    assert "<reference path=" not in out.prompt


def test_prompt_treats_empty_reference_like_none(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")

    out = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=[],
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert "<reference path=" not in out.prompt


def test_prompt_sorts_evidence_by_path(tmp_path: Path) -> None:
    write(tmp_path, "docs/b.md", "B")
    write(tmp_path, "docs/a.md", "A")

    out = prepare(
        claim="c",
        evidence=["docs/b.md", "docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert out.prompt.index('path="docs/a.md"') < out.prompt.index('path="docs/b.md"')


def test_prompt_is_identical_across_roots_and_leaks_no_absolute_path(
    tmp_path: Path,
) -> None:
    root_a = tmp_path / "wt_a"
    root_b = tmp_path / "wt_b"
    write(root_a, "docs/a.md", "ALPHA")
    write(root_b, "docs/a.md", "ALPHA")

    out_a = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=root_a,
    )
    out_b = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=root_b,
    )

    assert out_a.prompt == out_b.prompt
    assert str(root_a) not in out_a.prompt


# --- key: stability and root-invariance ------------------------------------


def test_key_is_stable_for_identical_inputs(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "ALPHA")

    first = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )
    second = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert first.key == second.key


def test_key_is_invariant_to_root(tmp_path: Path) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    write(root_a, "docs/a.md", "ALPHA")
    write(root_b, "docs/a.md", "ALPHA")

    key_a = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=root_a,
    ).key
    key_b = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=root_b,
    ).key

    assert key_a == key_b


# --- key: sensitivity to each input ----------------------------------------


def test_key_changes_when_claim_changes(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")

    key_one = prepare(
        claim="one",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    key_two = prepare(
        claim="two",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert key_one != key_two


def test_key_changes_when_file_bytes_change(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")
    key_before = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    write(tmp_path, "a.md", "B")
    key_after = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert key_before != key_after


def test_key_changes_when_declared_relpath_changes(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "SAME")
    write(tmp_path, "b.md", "SAME")

    key_a = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    key_b = prepare(
        claim="c",
        evidence=["b.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert key_a != key_b


def test_key_changes_when_model_changes(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")

    key_one = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m1",
        effort="high",
        root=tmp_path,
    ).key
    key_two = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m2",
        effort="high",
        root=tmp_path,
    ).key

    assert key_one != key_two


def test_key_changes_when_effort_changes(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")

    key_low = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="low",
        root=tmp_path,
    ).key
    key_high = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert key_low != key_high


def test_same_file_keys_differently_as_evidence_versus_reference(
    tmp_path: Path,
) -> None:
    write(tmp_path, "a.md", "A")

    as_evidence = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    as_reference = prepare(
        claim="c",
        evidence=[],
        reference=["a.md"],
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert as_evidence != as_reference


# --- key: canonicalization and order independence --------------------------


def test_canonical_path_variants_key_identically(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "A")

    plain = prepare(
        claim="c",
        evidence=["docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    dotted = prepare(
        claim="c",
        evidence=["./docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    double_slash = prepare(
        claim="c",
        evidence=["docs//a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert plain == dotted == double_slash


def test_canonical_relpath_is_used_in_prompt(tmp_path: Path) -> None:
    write(tmp_path, "docs/a.md", "A")

    out = prepare(
        claim="c",
        evidence=["./docs/a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert 'path="docs/a.md"' in out.prompt
    assert "./docs" not in out.prompt


def test_key_is_independent_of_evidence_order(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")
    write(tmp_path, "b.md", "B")

    forward = prepare(
        claim="c",
        evidence=["a.md", "b.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    reverse = prepare(
        claim="c",
        evidence=["b.md", "a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert forward == reverse


def test_duplicate_canonical_paths_key_like_single_occurrence(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")

    once = prepare(
        claim="c",
        evidence=["a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key
    twice = prepare(
        claim="c",
        evidence=["a.md", "./a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    ).key

    assert once == twice


def test_duplicate_paths_render_a_single_tag(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "A")

    out = prepare(
        claim="c",
        evidence=["a.md", "./a.md"],
        reference=None,
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert out.prompt.count('<evidence path="a.md">') == 1


# --- fail-loud path handling -----------------------------------------------


def test_missing_evidence_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        prepare(
            claim="c",
            evidence=["nope.md"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_absolute_path_is_rejected_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "read_bytes", _forbidden_read)

    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["/etc/passwd"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_dotdot_path_is_rejected_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "read_bytes", _forbidden_read)

    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["../secret.md"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_absolute_path_after_a_valid_path_is_rejected_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A valid path precedes the bad one: validation must reject the whole list
    # before reading *any* file, not just the offending entry.
    write(tmp_path, "a.md", "A")
    monkeypatch.setattr(Path, "read_bytes", _forbidden_read)

    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["a.md", "/etc/passwd"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_dotdot_path_after_a_valid_path_is_rejected_before_any_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path, "a.md", "A")
    monkeypatch.setattr(Path, "read_bytes", _forbidden_read)

    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["a.md", "../secret.md"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_empty_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=[""],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_dot_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["."],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )


def test_symlink_escaping_root_is_rejected(tmp_path: Path) -> None:
    # A symlink *under* root whose target is outside root must not be followed:
    # its contents would otherwise leak into the key and the prompt.
    root = tmp_path / "root"
    root.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET-OUTSIDE-ROOT")
    (root / "innocent.md").symlink_to(secret)

    with pytest.raises(ValueError):
        prepare(
            claim="c",
            evidence=["innocent.md"],
            reference=None,
            model="m",
            effort="high",
            root=root,
        )


def test_non_utf8_file_raises_naming_the_path(tmp_path: Path) -> None:
    # The key hashes raw bytes but the prompt needs UTF-8 text; reject a
    # non-decodable file at read time, with the offending path in the message.
    (tmp_path / "bad.md").write_bytes(b"\xff\xfe\x00")

    with pytest.raises(ValueError) as exc:
        prepare(
            claim="c",
            evidence=["bad.md"],
            reference=None,
            model="m",
            effort="high",
            root=tmp_path,
        )

    assert "bad.md" in str(exc.value)


# --- single read for both outputs ------------------------------------------


def test_each_file_is_read_exactly_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path, "a.md", "A")
    write(tmp_path, "b.md", "B")
    reads: list[str] = []
    real_read = Path.read_bytes

    def counting_read(self: Path) -> bytes:
        reads.append(str(self))
        return real_read(self)

    monkeypatch.setattr(Path, "read_bytes", counting_read)

    prepare(
        claim="c",
        evidence=["a.md"],
        reference=["b.md"],
        model="m",
        effort="high",
        root=tmp_path,
    )

    assert sorted(reads) == [str(tmp_path / "a.md"), str(tmp_path / "b.md")]

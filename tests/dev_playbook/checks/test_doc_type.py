"""Unit tests for the doc-type family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from dev_playbook.check_registry import Finding
from dev_playbook.checks.doc_type import (
    a_rule_heading_predicate_trailer,
    a_sequence_is_one_list,
    a_step_opens_with_its_name,
    an_act_links_a_runbook,
    arguments_bare_kebab_case_names,
    body_opens_with_an_h1,
    boolean_disable_model_invocation,
    description_two_sentences_or_one,
    every_bundle_file_reached_from_skillmd,
    front_matter_holds_its_kinds_vocabulary,
    kebab_case_name,
    model_and_effort_from_closed_sets,
    name_matches_its_home,
    no_argument_placeholder,
    no_trailer,
    references_one_level_deep,
    registered,
    skillmd_at_most_500_lines,
    the_files_why_ends_the_opening_prose,
    the_frontmatter_names_the_population,
    tools_comma_separated_tool_names,
)
from dev_playbook.model import Repo

SKILLS = "dotfiles/dot-claude/skills"
AGENTS = ".claude/agents"
SKILL_FRONT = (
    "name: {name}\n"
    "description: Does a thing. Use when a thing is wanted.\n"
    "disable-model-invocation: false\n"
    "model: opus\n"
    "effort: high\n"
)
AGENT_FRONT = (
    "name: {name}\n"
    "description: Does a thing. Use when a thing is wanted.\n"
    "model: sonnet\n"
    "effort: low\n"
)


def found(
    check: Callable[[Repo], Iterator[Finding]], contents: dict[str, bytes]
) -> list[tuple[str, int | None]]:
    repo = Repo.from_files(Path("/r"), contents)
    return [(f.path, f.line) for f in check(repo)]


def skill(name: str, extra: str = "", body: str = "# Skill\n") -> tuple[str, bytes]:
    text = "---\n" + SKILL_FRONT.format(name=name) + extra + "---\n\n" + body
    return f"{SKILLS}/{name}/SKILL.md", text.encode()


def agent(name: str, extra: str = "", body: str = "# Agent\n") -> tuple[str, bytes]:
    text = "---\n" + AGENT_FRONT.format(name=name) + extra + "---\n\n" + body
    return f"{AGENTS}/{name}.md", text.encode()


def typed(doctype: str, body: str, extra: str = "") -> bytes:
    return f"---\ntype: {doctype}\ntitle: T\n{extra}---\n\n{body}".encode()


def test_registered() -> None:
    table = b"""\
# System

## Registry rulings

| Kind | Family | Ruling |
|---|---|---|
| Guide | guides | The [Guide](/doc-types/guide/definition.md) doc-type |
| Loop | [Loop](/doc-types/loop/definition.md) | Pending |
"""
    assert found(
        registered,
        {
            "doc-types/doc-type-system.md": table,
            "doc-types/guide/definition.md": b"# Guide\n",
            "doc-types/loop/definition.md": b"# Loop\n",
            "doc-types/index.md": b"# Index\n",
        },
    ) == [("doc-types/loop", None)]


GOOD_GUIDE = """\
# Guide

## Setup runs in order

One sentence says what follows.

1. **Wire the pin.** Set it.

   ```yaml
   rev: v1
   ```

2. **Run the gate.** Run it.

## Next
"""

BAD_GUIDE = """\
# Guide

## Setup

One sentence. Two sentences.

2. **Wire the pin.** Set it.
   1. **Nested.** No.

A paragraph after the list.

## Loose

1. **Alone.** Fine.
3. Plain text item.
"""


def test_a_sequence_is_one_list() -> None:
    assert (
        found(
            a_sequence_is_one_list,
            {"guides/good.md": typed("Guide", GOOD_GUIDE)},
        )
        == []
    )
    assert found(
        a_sequence_is_one_list,
        {
            "guides/bad.md": typed("Guide", BAD_GUIDE),
            "notes/bad.md": typed("General-Sheet", BAD_GUIDE),
            "working-docs/w/draft.md": typed("Guide", BAD_GUIDE),
        },
    ) == [
        ("guides/bad.md", 12),
        ("guides/bad.md", 13),
        ("guides/bad.md", 12),
        ("guides/bad.md", 15),
    ]


def test_a_step_opens_with_its_name() -> None:
    assert (
        found(
            a_step_opens_with_its_name, {"guides/good.md": typed("Guide", GOOD_GUIDE)}
        )
        == []
    )
    assert found(
        a_step_opens_with_its_name, {"guides/bad.md": typed("Guide", BAD_GUIDE)}
    ) == [("guides/bad.md", 20)]


def test_no_trailer() -> None:
    body = "# Guide\n\n```\n`x.y` · deterministic\n```\n"
    assert found(no_trailer, {"guides/a.md": typed("Guide", body)}) == [
        ("guides/a.md", 9)
    ]
    assert found(no_trailer, {"notes/a.md": typed("General-Sheet", body)}) == []


def test_an_act_links_a_runbook() -> None:
    body = """\
# Loop

Drives a state.

```mermaid
flowchart
  a --> b
```

## Acts

- `a` — fires when x; runs [commit](/dotfiles/dot-claude/skills/commit/SKILL.md).
- `b` — fires when y; reads [notes](/notes/a.md)
  and [more](../notes/b.md).
- `c` — fires every iteration.

## Checks
"""
    assert found(an_act_links_a_runbook, {"loops/a.md": typed("Loop", body)}) == [
        ("loops/a.md", 18)
    ]


def test_front_matter_holds_its_kinds_vocabulary() -> None:
    good_skill = skill("one", extra="allowed-tools: Read\n")
    good_agent = agent("two", extra="tools: Read\n")
    bare = f"{SKILLS}/three/SKILL.md", b"# Three\n"
    stray = agent("four", extra="arguments: [x]\n")
    short = f"{SKILLS}/five/SKILL.md", b"---\nname: five\n---\n# Five\n"
    assert found(
        front_matter_holds_its_kinds_vocabulary,
        dict([good_skill, good_agent, bare, stray, short]),
    ) == [
        (f"{AGENTS}/four.md", None),
        (f"{SKILLS}/five/SKILL.md", None),
        (f"{SKILLS}/five/SKILL.md", None),
        (f"{SKILLS}/five/SKILL.md", None),
        (f"{SKILLS}/five/SKILL.md", None),
        (f"{SKILLS}/three/SKILL.md", 1),
    ]


def test_name_matches_its_home() -> None:
    path, text = skill("one")
    assert found(name_matches_its_home, dict([skill("one"), agent("two")])) == []
    assert found(name_matches_its_home, {f"{SKILLS}/other/SKILL.md": text}) == [
        (f"{SKILLS}/other/SKILL.md", None)
    ]
    assert path == f"{SKILLS}/one/SKILL.md"


def test_kebab_case_name() -> None:
    assert found(kebab_case_name, dict([skill("one-two")])) == []
    assert found(kebab_case_name, dict([agent("One_Two")])) == [
        (f"{AGENTS}/One_Two.md", None)
    ]


def test_description_two_sentences_or_one() -> None:
    one = (
        f"{SKILLS}/one/SKILL.md",
        b"---\nname: one\ndescription: Only one sentence.\n"
        b"disable-model-invocation: true\n---\n# One\n",
    )
    two = (
        f"{SKILLS}/two/SKILL.md",
        b"---\nname: two\ndescription: Only one sentence.\n---\n# Two\n",
    )
    three = (
        f"{AGENTS}/three.md",
        b"---\nname: three\ndescription: Does it. Called when wanted.\n---\n# Three\n",
    )
    assert found(description_two_sentences_or_one, dict([one, skill("ok")])) == []
    assert found(description_two_sentences_or_one, dict([two, three])) == [
        (f"{AGENTS}/three.md", None),
        (f"{SKILLS}/two/SKILL.md", None),
    ]


def test_model_and_effort_from_closed_sets() -> None:
    bad = (
        f"{AGENTS}/bad.md",
        b"---\nname: bad\nmodel: gpt\neffort: max\n---\n# Bad\n",
    )
    assert found(model_and_effort_from_closed_sets, dict([agent("good")])) == []
    assert found(model_and_effort_from_closed_sets, dict([bad])) == [
        (f"{AGENTS}/bad.md", None),
        (f"{AGENTS}/bad.md", None),
    ]


def test_body_opens_with_an_h1() -> None:
    assert found(body_opens_with_an_h1, dict([skill("one")])) == []
    assert found(
        body_opens_with_an_h1,
        dict([skill("two", body="Intro.\n\n# Two\n"), agent("three", body="\n")]),
    ) == [(f"{AGENTS}/three.md", None), (f"{SKILLS}/two/SKILL.md", 9)]


def test_every_bundle_file_reached_from_skillmd() -> None:
    body = (
        "# One\n\nRead [a](references/a.md) and run "
        "[s](/dotfiles/dot-claude/skills/one/scripts/s.sh).\n"
    )
    contents = dict([skill("one", body=body)])
    contents[f"{SKILLS}/one/references/a.md"] = b"# A\n"
    contents[f"{SKILLS}/one/scripts/s.sh"] = b"echo\n"
    contents[f"{SKILLS}/one/agents/openai.yaml"] = b"x: 1\n"
    assert found(every_bundle_file_reached_from_skillmd, contents) == []
    contents[f"{SKILLS}/one/references/deep/b.md"] = b"# B\n"
    assert found(every_bundle_file_reached_from_skillmd, contents) == [
        (f"{SKILLS}/one/references/deep/b.md", None)
    ]


def test_boolean_disable_model_invocation() -> None:
    assert found(boolean_disable_model_invocation, dict([skill("one")])) == []
    bad = (
        f"{SKILLS}/two/SKILL.md",
        b"---\nname: two\ndisable-model-invocation: 'yes'\n---\n# Two\n",
    )
    assert found(boolean_disable_model_invocation, dict([bad])) == [
        (f"{SKILLS}/two/SKILL.md", None)
    ]


def test_arguments_bare_kebab_case_names() -> None:
    assert (
        found(
            arguments_bare_kebab_case_names,
            dict([skill("one", extra="arguments: [subject, the-target]\n")]),
        )
        == []
    )
    assert found(
        arguments_bare_kebab_case_names,
        dict(
            [
                skill("two", extra="arguments: []\n"),
                skill("three", extra="arguments: [ok, Not_Kebab]\n"),
            ]
        ),
    ) == [(f"{SKILLS}/three/SKILL.md", None), (f"{SKILLS}/two/SKILL.md", None)]


def test_no_argument_placeholder() -> None:
    assert found(no_argument_placeholder, dict([skill("one")])) == []
    body = "# Two\n\n```\necho $ARGUMENTS\n```\n"
    assert found(no_argument_placeholder, dict([skill("two", body=body)])) == [
        (f"{SKILLS}/two/SKILL.md", 12)
    ]


def test_references_one_level_deep() -> None:
    refs = f"{SKILLS}/one/references"
    contents = dict([skill("one")])
    contents[f"{refs}/a.md"] = b"# A\n\nSee [the skill](../SKILL.md).\n"
    contents[f"{refs}/b.md"] = b"# B\n\nSee [a](a.md).\n"
    contents[f"{refs}/deep/c.md"] = b"# C\n\nSee [b][ref].\n\n[ref]: ../b.md\n"
    contents[f"{refs}/d.md"] = (
        b"# D\n\nSee [a](/dotfiles/dot-claude/skills/one/references/a.md)"
        b" and [c](~/.claude/skills/one/references/deep/c.md).\n"
    )
    assert found(references_one_level_deep, contents) == [
        (f"{refs}/b.md", None),
        (f"{refs}/d.md", None),
        (f"{refs}/d.md", None),
        (f"{refs}/deep/c.md", None),
    ]


def test_skillmd_at_most_500_lines() -> None:
    assert found(skillmd_at_most_500_lines, dict([skill("one")])) == []
    long_body = "# Two\n" + "line\n" * 500
    assert found(skillmd_at_most_500_lines, dict([skill("two", body=long_body)])) == [
        (f"{SKILLS}/two/SKILL.md", None)
    ]


def test_tools_comma_separated_tool_names() -> None:
    assert (
        found(
            tools_comma_separated_tool_names,
            dict([agent("one", extra="tools: Read, Grep, mcp__x-y__z\n")]),
        )
        == []
    )
    assert found(
        tools_comma_separated_tool_names,
        dict(
            [
                agent("two", extra="tools: Read Grep\n"),
                agent("three", extra="tools: Read,\n"),
            ]
        ),
    ) == [(f"{AGENTS}/three.md", None), (f"{AGENTS}/two.md", None)]


def test_the_frontmatter_names_the_population() -> None:
    body = "# S\n"
    assert found(
        the_frontmatter_names_the_population,
        {
            "standards/a/good.md": typed("Standard", body, 'population: "a file"\n'),
            "standards/a/bad.md": typed("Standard", body, 'population: " "\n'),
            "standards/a/none.md": typed("Standard", body),
            "notes/a.md": typed("General-Sheet", body),
        },
    ) == [("standards/a/bad.md", None), ("standards/a/none.md", None)]


GOOD_STANDARD = """\
# S

Opening.

> **Why.** The file's argument.

## A rule

The predicate.

- a list
- of items

| a | b |
|---|---|

`fam.a-rule` · deterministic

> **Why.** The rule's argument.

## A condition

### Under it

The predicate.

`fam.under-it` · stochastic
"""

BAD_STANDARD = """\
# S

Opening.

## A rule

- a list first

`other.a-rule` · deterministic

A stray paragraph.

### Under a rule

The predicate.

`fam.wrong-slug` · deterministic
"""


def test_a_rule_heading_predicate_trailer() -> None:
    assert (
        found(
            a_rule_heading_predicate_trailer,
            {"standards/fam/good.md": typed("Standard", GOOD_STANDARD)},
        )
        == []
    )
    assert found(
        a_rule_heading_predicate_trailer,
        {"standards/fam/bad.md": typed("Standard", BAD_STANDARD)},
    ) == [
        ("standards/fam/bad.md", 14),
        ("standards/fam/bad.md", 10),
        ("standards/fam/bad.md", 14),
        ("standards/fam/bad.md", 22),
        ("standards/fam/bad.md", 18),
    ]


def test_the_files_why_ends_the_opening_prose() -> None:
    assert (
        found(
            the_files_why_ends_the_opening_prose,
            {"standards/fam/good.md": typed("Standard", GOOD_STANDARD)},
        )
        == []
    )
    late = "# S\n\n> **Why.** One.\n\nOpening after it.\n\n## Rule\n"
    twice = "# S\n\n> **Why.** One.\n\n> **Why.** Two.\n"
    assert found(
        the_files_why_ends_the_opening_prose,
        {
            "standards/fam/late.md": typed("Standard", late),
            "standards/fam/twice.md": typed("Standard", twice),
        },
    ) == [("standards/fam/late.md", 8), ("standards/fam/twice.md", 10)]

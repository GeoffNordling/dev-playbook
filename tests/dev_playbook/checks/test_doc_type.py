"""Unit tests for the doc-type family's checks."""

from collections.abc import Callable, Iterator
from pathlib import Path

from dev_playbook.check_registry import Finding
from dev_playbook.checks.doc_type import (
    DOC_TYPE_FILES,
    a_rule_heading_predicate_trailer,
    a_sequence_is_one_list,
    a_step_opens_with_its_name,
    a_stint_entry_in_form,
    a_worklist_item_opens_with_its_bold_name,
    acts_verifications_and_yields_in_that_order,
    an_act_links_a_runbook,
    arguments_bare_kebab_case_names,
    body_opens_with_an_h1,
    boolean_disable_model_invocation,
    description_two_sentences_or_one,
    edges_lead_to_steps,
    every_bundle_file_reached_from_skillmd,
    every_child_reached_from_its_parent,
    every_entry_states_its_condition,
    five_files,
    front_matter_holds_its_kinds_vocabulary,
    headings_from_the_registry,
    its_instances_are_its_own,
    its_instances_are_registered,
    kebab_case_name,
    model_and_effort_from_closed_sets,
    name_matches_its_home,
    no_argument_placeholder,
    no_trailer,
    nodes_and_entries_agree,
    one_paragraph_then_one_graph,
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
# Doc-Type Registry

## Doc-types

| Doc-type | OKF type | Harness members | Conventions |
|---|---|---|---|
| [Guide](/doc-types/guide/definition.md) | `Guide` | - | [Loop](/doc-types/loop/definition.md) |
"""
    assert found(
        registered,
        {
            "registries/doc-types.md": table,
            "doc-types/guide/definition.md": b"# Guide\n",
            "doc-types/loop/definition.md": b"# Loop\n",
            "doc-types/index.md": b"# Index\n",
        },
    ) == [("doc-types/loop", None)]


REGISTRIES = {
    "registries/okf-types.md": b"""\
# OKF Type Registry

## OKF types

| OKF type | What it is |
|---|---|
| `Guide` | A guide. |
| `Loop` | A loop. |
""",
    "registries/harness-files.md": b"""\
# Harness File Registry

## Members

| Member | Class | Role | Content standard |
|---|---|---|---|
| skill bundles | runbook | loaded | none |
| `agents/*.md` | runbook | loaded | none |
""",
}
NONE = "\u2014"


def doc_type_registry(*rows: tuple[str, str, str]) -> dict[str, bytes]:
    lines = [
        "# Doc-Type Registry",
        "",
        "## Doc-types",
        "",
        "| Doc-type | OKF type | Harness members | Conventions |",
        "|---|---|---|---|",
    ]
    for name, okf, members in rows:
        link = f"[{name}](/doc-types/{name}/definition.md)"
        lines.append(f"| {link} | {okf} | {members} | C |")
    registry = "\n".join(lines) + "\n"
    return REGISTRIES | {"registries/doc-types.md": registry.encode()}


def test_its_instances_are_registered() -> None:
    good = doc_type_registry(
        ("guide", "`Guide`", NONE),
        ("runbook", NONE, "skill bundles; `agents/*.md`"),
    )
    assert found(its_instances_are_registered, good) == []
    bad = doc_type_registry(
        ("guide", "`Log`", NONE),
        ("runbook", NONE, "hooks"),
        ("loop", NONE, NONE),
    )
    assert found(its_instances_are_registered, bad) == [
        ("doc-types/guide", None),
        ("doc-types/runbook", None),
        ("doc-types/loop", None),
    ]


def test_its_instances_are_its_own() -> None:
    good = doc_type_registry(("guide", "`Guide`", NONE), ("loop", "`Loop`", NONE))
    assert found(its_instances_are_its_own, good) == []
    bad = doc_type_registry(("guide", "`Guide`", NONE), ("loop", "`Guide`", NONE))
    assert found(its_instances_are_its_own, bad) == [("doc-types/loop", None)]


def test_five_files() -> None:
    whole = {f"doc-types/guide/{name}": b"# G\n" for name in DOC_TYPE_FILES}
    assert (
        found(
            five_files,
            {
                **whole,
                "doc-types/loop/definition.md": b"# Loop\n",
                "doc-types/loop/encoding.md": b"# Loop\n",
                "doc-types/index.md": b"# Index\n",
            },
        )
        == [("doc-types/loop", None)] * 3
    )


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
            "workstreams/w/draft.md": typed("Guide", BAD_GUIDE),
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


def test_headings_from_the_registry() -> None:
    body = """\
# Work

## Goal

## Stints

## Ideas

## Goal
"""
    assert found(
        headings_from_the_registry,
        {"workstreams/w/WORKSTREAM.md": typed("Workstream", body)},
    ) == [("workstreams/w/WORKSTREAM.md", 12), ("workstreams/w/WORKSTREAM.md", 14)]


def test_a_worklist_item_opens_with_its_bold_name() -> None:
    body = """\
# Work

## Planned

- **Write the board script.** It reads the head files.
- plain item

### Detail

- plain detail

## Completed

- **Done.** Body.
* plain again

## Goal

- plain goal
"""
    assert found(
        a_worklist_item_opens_with_its_bold_name,
        {"workstreams/w/WORKSTREAM.md": typed("Workstream", body)},
    ) == [("workstreams/w/WORKSTREAM.md", 11), ("workstreams/w/WORKSTREAM.md", 20)]


STINTS = """\
# Work

## Stints

- **Planned.** Loop: [Design](/loops/design.md). Budget: one session.
- **2026-09-24.** Loop: [Design](/loops/design.md). Budget: two sessions.
  Spent: two sessions. Verdict: advance.
- **2026-09-20.** Loop: [Design](/loops/design.md). Verdict: accept.
"""


def test_a_stint_entry_in_form() -> None:
    loop = typed("Loop", "# Design\n")
    head = "workstreams/w/WORKSTREAM.md"
    assert (
        found(
            a_stint_entry_in_form,
            {head: typed("Workstream", STINTS), "loops/design.md": loop},
        )
        == []
    )
    bad = (
        STINTS.replace("2026-09-20", "2026-09-30")
        .replace("Verdict: accept", "Verdict: merged")
        .replace(
            "Budget: one session.", "Budget: one session. Also [x](/loops/design.md)."
        )
        + "- **Planned.** Loop: [Notes](/notes.md).\n- Next, maybe.\n"
    )
    assert found(
        a_stint_entry_in_form,
        {head: typed("Workstream", bad), "loops/design.md": loop, "notes.md": b"# N\n"},
    ) == [(head, 10), (head, 13), (head, 13), (head, 14), (head, 14), (head, 15)]


def test_every_child_reached_from_its_parent() -> None:
    parent = typed("Workstream", "# Top\n\nSee [notes](notes.md).\n")
    notes = b"# Notes\n\nThe [child](/w/a/WORKSTREAM.md).\n"
    assert found(
        every_child_reached_from_its_parent,
        {
            "w/WORKSTREAM.md": parent,
            "w/notes.md": notes,
            "w/a/WORKSTREAM.md": typed("Workstream", "# A\n"),
            "w/a/deep/WORKSTREAM.md": typed("Workstream", "# Deep\n"),
            "w/b/WORKSTREAM.md": typed("Workstream", "# B\n"),
        },
    ) == [("w/a/deep/WORKSTREAM.md", None), ("w/b/WORKSTREAM.md", None)]


# --- the five Loop rules that read its cut in order -------------------------

LOOP_RUNBOOK = "---\nname: tidy\ndescription: Tidies\n---\n\nTidy the tree.\n"
LOOP_STANDARD = (
    "---\ntype: Standard\ntitle: Tidy Tree\ndescription: A tidy tree\n"
    'population: "a tree"\n---\n\n# Tidy Tree\n\n## Flat\n\nNo nesting.\n'
)
TIDY_LOOP = """---
type: Loop
title: Tidy
description: Drives the tree tidy
---

# Tidy

Drives the repo's tree toward Tidy Tree.

```mermaid
flowchart LR
    tidy[tidy] -->|every iteration| flat[flat?]
    flat -->|findings| ask{ask?}
    ask -->|none met| tidy
    ask -->|3 rounds| user([the user])
    user -->|resumes| tidy
```

## Acts

- `tidy` — [tidy](/skills/tidy.md), fires every iteration.

## Verifications

- `flat` — [Tidy Tree](/standards/tidy/tree.md), fires every
  iteration.

## Yields

- `ask` — to the user, yields when three rounds have run.
"""


def loop_found(
    check: Callable[[Repo], Iterator[Finding]], loop: str = TIDY_LOOP
) -> list[tuple[str, str]]:
    """The findings of one Loop check over a repo of a runbook, a Standard, a Loop."""
    repo = Repo.from_files(
        Path("/r"),
        {
            "skills/tidy.md": LOOP_RUNBOOK.encode(),
            "standards/tidy/tree.md": LOOP_STANDARD.encode(),
            "loops/tidy.md": loop.encode(),
        },
    )
    return [(f.path, f.message) for f in check(repo)]


LOOP_CHECKS = (
    one_paragraph_then_one_graph,
    acts_verifications_and_yields_in_that_order,
    nodes_and_entries_agree,
    edges_lead_to_steps,
    every_entry_states_its_condition,
)


def only(loop: str) -> tuple[str, str]:
    """The one finding the five Loop checks give together over ``loop``, by check name."""
    hits = [(c.__name__, m) for c in LOOP_CHECKS for _, m in loop_found(c, loop)]
    assert len(hits) == 1, hits
    return hits[0]


def test_graph_and_prose_that_agree_pass() -> None:
    assert [loop_found(c) for c in LOOP_CHECKS] == [[]] * 5


def test_nodes_and_entries_agree() -> None:
    loop = TIDY_LOOP.replace(
        "    ask -->|none met| tidy\n",
        "    ask -->|none met| tidy\n    extra[extra] --> tidy\n",
    )
    assert only(loop) == (
        "nodes_and_entries_agree",
        "`extra` has no entry and no yield leads to it",
    )


def test_an_entry_with_no_node_fails() -> None:
    loop = TIDY_LOOP.replace(
        "## Verifications\n",
        "## Verifications\n\n- `ghost` — [Tidy Tree](/standards/tidy/tree.md), "
        "fires every iteration.\n",
    )
    assert only(loop) == (
        "nodes_and_entries_agree",
        "`ghost` has an entry but is not a node of the graph",
    )


def test_edges_lead_to_steps() -> None:
    loop = TIDY_LOOP.replace(
        "    flat -->|findings| ask{ask?}\n",
        "    flat -->|findings| ask{ask?}\n    flat --> user\n",
    )
    name, message = only(loop)
    assert name == "edges_lead_to_steps"
    assert message.startswith("edge `flat` → `user` is verification → receiver")


def test_a_verification_that_links_a_file_not_typed_standard_fails() -> None:
    loop = TIDY_LOOP.replace(
        "[Tidy Tree](/standards/tidy/tree.md)", "[tidy](/skills/tidy.md)"
    )
    name, message = only(loop)
    assert name == "every_entry_states_its_condition"
    assert "a verification links a file typed Standard" in message


def test_a_link_that_does_not_resolve_fails() -> None:
    loop = TIDY_LOOP.replace("/skills/tidy.md", "/skills/gone.md")
    assert only(loop) == (
        "every_entry_states_its_condition",
        "link '/skills/gone.md' does not resolve",
    )


def test_a_second_link_that_does_not_resolve_fails() -> None:
    loop = TIDY_LOOP.replace(
        "[tidy](/skills/tidy.md),", "[tidy](/skills/tidy.md) [gone](gone.md),"
    )
    assert only(loop) == (
        "every_entry_states_its_condition",
        "link 'gone.md' does not resolve",
    )


def test_a_yield_to_the_principal_passes() -> None:
    loop = TIDY_LOOP.replace("to the user, yields", "to the principal, yields")
    assert [loop_found(c, loop) for c in LOOP_CHECKS] == [[]] * 5


def test_a_yield_with_no_receiver_fails() -> None:
    loop = TIDY_LOOP.replace("to the user, yields", "yields")
    name, message = only(loop)
    assert name == "every_entry_states_its_condition"
    assert message.startswith("`ask` names no receiver")


def test_every_entry_states_its_condition() -> None:
    loop = TIDY_LOOP.replace("yields when three rounds have run", "after three rounds")
    name, message = only(loop)
    assert name == "every_entry_states_its_condition"
    assert message.startswith("`ask` states no condition")


def test_acts_verifications_and_yields_in_that_order() -> None:
    loop = TIDY_LOOP.replace("## Verifications", "## Measures")
    name, message = only(loop)
    assert name == "acts_verifications_and_yields_in_that_order"
    assert message.startswith("verb sections are")


def test_one_paragraph_then_one_graph() -> None:
    loop = TIDY_LOOP.replace(
        "Drives the repo's tree toward Tidy Tree.\n",
        "Drives the tree.\n\nToward Tidy Tree.\n",
    )
    assert only(loop) == (
        "one_paragraph_then_one_graph",
        "2 paragraphs before the graph; the encoding is one",
    )


def test_a_loop_in_a_workstream_is_not_read() -> None:
    bad = TIDY_LOOP.replace("## Verifications", "## Measures")
    repo = Repo.from_files(Path("/r"), {"workstreams/w/tidy.md": bad.encode()})
    assert [list(c(repo)) for c in LOOP_CHECKS] == [[]] * 5

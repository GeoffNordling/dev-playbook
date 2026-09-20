# docs/guides/ — index

The guides behind the Standards — one per Standard directory, carrying
the vocabulary, the reasoning, the diagrams, and the examples that make
that directory's rules intelligible. Nothing here is enforced; every rule
is in its Standard.

Ordering: alphabetical by title.

- [Build Guide](/docs/guides/build.md) — The thinking behind the build rules — layers inferred from the tree, what each required file is for, the four strengths of a canonical compare, what a green check means, why CI runs no tests, and the reasons behind the pyproject pins
- [Decisions Guide](/docs/guides/decisions.md) — The thinking behind the Decision Record rules — the bar with worked examples, where a record lives, how a new record is numbered, why a record is frozen after merge, and what the optional sections are for
- [Distribution Guide](/docs/guides/distribution.md) — The thinking behind the distribution rules — one published hook id, why enrollment rides the pin, the roster, why dev-playbook dogfoods its manifest instead of pinning, and why a stale pin is advisory
- [Harness Guide](/docs/guides/harness.md) — The thinking behind the harness rules — where a runbook lives and what its front matter holds, what each skill and agent field does, how arguments reach a skill, what an agent's body is, and why a CLAUDE.md has no frontmatter and one scope
- [Knowledge Organization Guide](/docs/guides/knowledge-organization.md) — The thinking behind the knowledge-organization rules — what CONTEXT.md is for, why a reference takes the form it does, what a description is for, how a documentation set stays navigable, what a working set is, how an index reads, how a Loop is checked, and why a type registry is frontmatter
- [Module Design Guide](/docs/guides/modules.md) — The thinking behind the module-design rules — depth and the deletion test, seams and adapters, ports at a process boundary, and the diagrams and examples that teach them
- [Prose Guide](/docs/guides/prose.md) — The thinking behind the prose rules — where a rule sits in a section, why history is cut, how a block's form is chosen, why the two voices differ, what the slop-tics catalog is, and the examples that show the casing and parallelism rules
- [Python Guide](/docs/guides/python.md) — The thinking behind the Python style rules — why an init is empty, which docstrings matter, what a fallback hides, where a constant sits, why future annotations are gone, what justifies a helper, and which tool decides each rule
- [Shell Guide](/docs/guides/shell.md) — The thinking behind the shell rules — bash and not POSIX sh, shellcheck and the cost of a disable, shfmt's defaults as the bar, when a script has outgrown shell, what strict mode fixes, and why a sourced fragment is different
- [Standard Guide](/docs/guides/standard.md) — The thinking behind the meta-standard's rules — what a detector is and is not, why an absent surface is clean, and why a detector must ignore the GIT_DIR a git hook exports
- [Test Design Guide](/docs/guides/testing.md) — The thinking behind the testing rules — what a test verifies, the tautological test, the non-deterministic boundary, the ladder of doubles, what a fake is, where a mock stands, and why layered coverage is waste
- [Tracking Guide](/docs/guides/tracking.md) — The thinking behind the tracking rules — what a Candidate is and how it becomes an issue, the roles and relationships an issue has, the five species, what the labels mean, and why the repository settings are what they are, with the hand-set ruleset spelled out

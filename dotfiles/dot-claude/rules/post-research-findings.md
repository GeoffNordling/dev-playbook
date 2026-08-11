# Post Research Findings on the Ticket

A research delegation that resolves a tracker ticket — a `/research` run, a
wayfinder research ticket — ends with the complete findings text posted as a
comment on the ticket. The ticket is the reading room; a branch or file copy
is only the durable original. A pointer comment alone does not resolve the
ticket, even where a skill prescribes one.

## Same bytes, generated once

Write the findings file once, then post that file — never re-emit the
content through model output:

    gh issue comment <N> --body-file <findings>.md

A provenance header is fine: stage it with `cat header.md findings.md >
staged.md`, then `--body-file` the staged file. Spell the path literally on
the `gh` line (see Running Bash Commands: `$TMPDIR` is empty there).

## Oversized findings

GitHub comments cap near 65k characters. Past that, open a draft PR from the
research branch — its Files-changed view renders the document — and comment
on the ticket that the findings live there.

# Place the Rules

{Read [the standards index](~/workspace/dev-playbook/standards/index.md)}.
{If this session is homed in another repo and it holds a
`standards/index.md`, {Read that index too}}. Follow the indexes they lead
to only as far as the rules' subject needs. Give each rule one home, in
dev-playbook where the rule holds for every repo, in this repo's standards
where it holds only here:

- **An existing section.** The rule joins a section whose concern it
  shares.
- **A new section in an existing standard.** The standard's population
  holds the files the rule reads, and no section shares the concern.
- **A new standard.** No standard's population holds the files. A new
  standard costs a lot of design, so this home must be the only one that
  fits.
- **No standard.** The rule belongs in a skill step, a rule in
  `~/.claude/rules/`, or a `CLAUDE.md` line, because it is about how an
  agent works and not a property of a file.

## Report

{Report each rule with its home, and nothing else}:

    - <rule> · <home>
    - <…>

Under a rule whose home is a new standard, name the nearest existing
standards and, for each, the reason it does not fit: its population does
not hold the files the rule reads, or no section's concern is the rule's.

End the turn. The user accepts the rules, changes them, or drops them.

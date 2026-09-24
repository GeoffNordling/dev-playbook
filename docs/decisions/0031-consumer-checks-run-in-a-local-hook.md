---
type: Decision-Record
title: Consumer Checks Run in a Second, Local Hook
description: A consumer that writes its own checks runs them in a second hook, playbook-check-local, in its own uv environment, and sources dev-playbook as a git dev dependency at the pinned rev, because the pinned hook's environment cannot import the consumer's package
date: 2026-09-24
status: accepted
---

# Consumer Checks Run in a Second, Local Hook

The check rewrite let a consumer keep its own checks in
`src/<package>/checks/`, and the pinned `playbook-check` hook ran them beside
dev-playbook's. pre-commit runs that hook in a venv it builds from
dev-playbook's clone, which holds dev-playbook and pyyaml and nothing of the
consumer's. story-forge, the first consumer to write checks, has rules about
what its own code produces, so its checks must import `story_forge`, numpy,
and pydantic, and in that venv they cannot.

The decision: a consumer's checks run in a second hook. The pinned
`playbook-check` runs dev-playbook's checks only. A host lists
`playbook-check-local` in a `repo: local` block, with
`entry: uv run --locked playbook check --local` and `language: system`, so its
checks run in its own environment and the layer test runs with them. The host
sources dev-playbook as a git dev dependency at the same rev its pre-commit
config pins. Two rules in the
[Distribution Channel](/standards/distribution/channel.md) hold this: a repo
with its own rules or checks lists the hook, and its dev-playbook source rides
the pin. `bump-pin` and `update-pins` move both revs and re-lock `uv.lock` as
one act.

[One Published Hook](/docs/decisions/0012-one-published-hook.md) still holds:
dev-playbook publishes one hook, and enrollment in dev-playbook's checks rides
the pin. The second hook is the host's own, and it runs only the host's own
checks.

## Considered Options

- **The pinned hook reruns itself in the consumer's environment**, with
  `uv run --project <consumer> --with <dev-playbook clone>`. Rejected: a hook
  that relaunches itself needs a guard against a loop and depends on where
  pre-commit installed dev-playbook from, and that complexity is hidden in
  every consumer's gate.
- **The consumer's environment runs the whole check, with no pinned hook.**
  Rejected: the pre-commit pin is the release, and removing it for hosts
  gives them a different release channel from every other consumer.
- **A path source for the dev dependency**, as spec-tools had. Rejected: it
  follows the live checkout instead of the pin, and a CI runner does not
  have it.
- **No change: a host tests such rules in pytest.** Rejected: a rule about
  what the repo's code produces is a Standard's rule like any other, and it
  belongs at the same gate as other rules.

---
type: Box Artifact
title: "Charter: sessionxml"
description: Non-goals, conformance targets, resolution rules, and escalation triggers for the sessionxml box
---

# Charter

GOAL

    Personal-tooling grade, one-shot exporter. Not a library, not a product.

NON-GOALS

    - no HTML, no rendering, no TUI
    - no streaming / watch mode
    - no recovery of corrupt sessions beyond a clean exit-1
    - no config files; flags are the entire interface

CONFORMANCE

    The work product conforms to these workspace standards. Read each one
    before writing code. A reviewer or judge may cite them to reject work.

    - ~/workspace/dev-playbook/standards/python-style.md
    - ~/workspace/dev-playbook/standards/testing-conventions.md

RESOLUTION RULES (when contract and fixtures are silent)

    1. fixtures beat contract prose; contract prose beats your judgment
    2. unpinned edge case -> pick the behavior that fails loudest,
       record it in DEVIATIONS.md, keep moving
    3. dependencies: stdlib first; else one small pinned dep;
       anything heavier -> escalate
    4. do not optimize. correctness and clarity only.

INTERNAL TESTS

    Write your own suite under tools/sessionxml/tests/. It is yours:
    no human reviews it, but it must pass in gate.sh, and a separate
    audit agent will read it as evidence of where you saw risk.

ESCALATE — write tools/sessionxml/BLOCKED.md and stop, when:

    - the contract contradicts a fixture
    - an acceptance test appears wrong (never edit it)
    - you need a dependency outside rule 3
